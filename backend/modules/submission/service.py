"""Submission orchestrator — coordinates execution, judging, diagnosis, and persistence.

Flow: submit code → run tests via Judge0 → compare results → detect mistakes → 
      generate explanation → update mastery → store everything in database
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    Submission,
    SubmissionResult,
    MistakeRecord,
    Challenge,
)
from modules.challenges.service import get_challenge_tests_for_judging
from modules.judge.engine import judge_submission, JudgeResult, TestOutcome, ExecutionServiceUnavailableError
from modules.diagnosis.detector import detect_mistakes
from modules.learner.service import update_mastery, get_or_create_learner
from modules.hints.groq_client import generate_hint_with_groq

logger = logging.getLogger(__name__)


async def process_submission(
    db: AsyncSession,
    learner_supabase_id: str,
    challenge_id: str,
    code: str,
) -> dict:
    """Process a code submission end-to-end.
    
    1. Validate the challenge exists
    2. Get/create learner profile
    3. Create submission record
    4. Get all tests (visible + hidden) for server-side judging
    5. Run tests via Judge0
    6. Compare results on backend
    7. Detect mistake patterns
    8. Generate explanation
    9. Update mastery
    10. Store results and return response
    """
    # 1. Validate challenge
    challenge_result = await db.execute(
        select(Challenge).where(
            (Challenge.id == challenge_id) | (Challenge.slug == challenge_id)
        )
    )
    challenge = challenge_result.scalar_one_or_none()
    if not challenge:
        return {"error": "Challenge not found", "status_code": 404}
    
    # 2. Get or create learner
    learner = await get_or_create_learner(db, learner_supabase_id)
    
    # 3. Create submission
    submission = Submission(
        learner_id=learner.id,
        challenge_id=challenge.id,
        code=code,
        overall_status="pending",
    )
    db.add(submission)
    await db.flush()
    
    # 4. Get all tests for judging (visible + hidden)
    tests = await get_challenge_tests_for_judging(db, challenge.id)
    
    if not tests:
        submission.overall_status = "failed"
        submission.explanation = "No tests found for this challenge."
        return {"error": "No tests configured", "status_code": 500}
    
    # 5-6. Run tests via Judge0 and compare results server-side
    try:
        judge_result = await judge_submission(
            learner_code=code,
            tests=tests,
            timeout_per_test=10.0,
        )
    except ExecutionServiceUnavailableError as exc:
        logger.error("Submission failed due to unavailable execution service: %s", str(exc))
        submission.overall_status = "service_unavailable"
        submission.explanation = str(exc)
        await db.flush()
        return {
            "error": "Code execution service is currently unavailable. Please try again.",
            "status_code": 503,
            "retryable": True,
        }
    
    # 7. Store results
    all_outcomes = judge_result.visible_results + judge_result.hidden_results
    for outcome in all_outcomes:
        # Find the test to link the result
        matching_test = next(
            (t for t in tests if t["test_number"] == outcome.test_number),
            None,
        )
        
        sub_result = SubmissionResult(
            submission_id=submission.id,
            test_id=matching_test["id"] if matching_test else "",
            test_number=outcome.test_number,
            is_hidden=outcome.is_hidden,
            outcome=outcome.outcome,
            actual_output=outcome.actual_display or "" if not outcome.is_hidden else "",
            stderr_output=outcome.error_message or "",
        )
        db.add(sub_result)
    
    # Update submission status
    submission.overall_status = judge_result.overall_status
    
    # 8. Detect mistakes
    mistake_tags = detect_mistakes(code, all_outcomes)
    for mistake in mistake_tags:
        record = MistakeRecord(
            learner_id=learner.id,
            submission_id=submission.id,
            challenge_id=challenge.id,
            category=mistake.category,
            evidence=mistake.evidence,
        )
        db.add(record)
    
    # 9. Generate explanation
    explanation = _build_explanation(judge_result, mistake_tags)
    submission.explanation = explanation
    
    # 10. Count hints used for this challenge by this learner
    from database.models import HintUsage
    hint_count_result = await db.execute(
        select(func.count(HintUsage.id))
        .where(
            and_(
                HintUsage.learner_id == learner.id,
                HintUsage.challenge_id == challenge.id,
            )
        )
    )
    hints_used = hint_count_result.scalar() or 0
    
    # Update mastery
    await update_mastery(
        db,
        learner_id=learner.id,
        challenge_id=challenge.id,
        passed=(judge_result.overall_status == "passed"),
        hints_used=hints_used,
    )
    
    await db.flush()
    
    # Build response (hidden tests show only number + outcome)
    visible_results = [
        {
            "test_number": r.test_number,
            "outcome": r.outcome,
            "call_expression": r.call_expression,
            "expected": r.expected_display,
            "actual": r.actual_display,
            "error_message": r.error_message,
        }
        for r in judge_result.visible_results
    ]
    
    hidden_results = [
        {
            "test_number": r.test_number,
            "outcome": r.outcome,
            # No input, expected, or actual for hidden tests
        }
        for r in judge_result.hidden_results
    ]
    
    return {
        "submission_id": submission.id,
        "challenge_id": challenge.id,
        "learner_id": learner.id,
        "overall_status": judge_result.overall_status,
        "total_passed": judge_result.total_passed,
        "total_tests": judge_result.total_tests,
        "visible_results": visible_results,
        "hidden_results": hidden_results,
        "mistake_tags": [
            {"category": m.category, "evidence": m.evidence}
            for m in mistake_tags
        ],
        "explanation": explanation,
    }


def _build_explanation(
    judge_result: JudgeResult,
    mistakes: list,
) -> str:
    """Build a plain-language explanation of the submission results."""
    if judge_result.overall_status == "passed":
        return "All tests passed! Great work! 🎉"
    
    parts = []
    
    # Summarize failures
    failed_visible = [r for r in judge_result.visible_results if r.outcome != "passed"]
    failed_hidden = [r for r in judge_result.hidden_results if r.outcome != "passed"]
    
    if failed_visible:
        parts.append(
            f"{len(failed_visible)} visible test(s) failed."
        )
        # Show the first failure details
        first_fail = failed_visible[0]
        if first_fail.outcome == "wrong_output":
            parts.append(
                f"For example, test {first_fail.test_number}: "
                f"expected {first_fail.expected_display} but got {first_fail.actual_display}."
            )
        elif first_fail.outcome == "runtime_error":
            parts.append(
                f"Test {first_fail.test_number} caused a runtime error: "
                f"{first_fail.error_message or 'unknown error'}."
            )
        elif first_fail.outcome == "timeout":
            parts.append(f"Test {first_fail.test_number} timed out.")
    
    if failed_hidden:
        parts.append(f"{len(failed_hidden)} hidden test(s) also failed.")
    
    # Add mistake insights
    if mistakes:
        parts.append("\n💡 Detected patterns:")
        for m in mistakes:
            parts.append(f"  • {m.evidence}")
    
    return " ".join(parts) if parts else "Some tests did not pass. Review the test results for details."
