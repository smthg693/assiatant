"""Tests for mistake detection across all 5 required categories and recurring mistake aggregation."""

import pytest
from modules.judge.engine import TestOutcome
from modules.diagnosis.detector import (
    detect_mistakes,
    detect_print_not_return,
    detect_off_by_one,
    detect_unhandled_short_input,
    detect_boundary_comparison,
    detect_mutates_input,
)
from database.connection import init_db, async_session
from database.models import MistakeRecord, LearnerProfile, Challenge, Submission
from modules.learner.service import get_learner_dashboard


def test_detect_print_not_return():
    """Detect when learner prints instead of returning."""
    code = "def f(x):\n    print(x * 2)"
    outcomes = [
        TestOutcome(test_number=1, is_hidden=False, outcome="wrong_output", actual_display="None"),
        TestOutcome(test_number=2, is_hidden=False, outcome="wrong_output", actual_display="None"),
    ]
    det = detect_print_not_return(code, outcomes)
    assert det is not None
    assert det.category == "print_not_return"
    assert det.confidence >= 0.8


def test_detect_off_by_one():
    """Detect off-by-one errors in ranges or slices."""
    code = "def first_n_squares(n):\n    return [i*i for i in range(n)]"
    outcomes = [
        TestOutcome(
            test_number=1,
            is_hidden=False,
            outcome="wrong_output",
            actual_display="[0, 1, 4, 9]",
            expected_display="[1, 4, 9, 16]",
        )
    ]
    det = detect_off_by_one(code, outcomes)
    assert det is not None
    assert det.category == "off_by_one"


def test_detect_unhandled_short_input():
    """Detect missing edge case handling for short or empty inputs."""
    code = "def last_k_total(marks, k):\n    return sum(marks[-k:])"
    outcomes = [
        TestOutcome(
            test_number=1,
            is_hidden=False,
            outcome="wrong_output",
            call_expression="last_k_total([], 3)",
            actual_display="0",
            expected_display="0",
        ),
        TestOutcome(
            test_number=2,
            is_hidden=False,
            outcome="runtime_error",
            call_expression="last_k_total([10], 0)",
            error_message="IndexError",
        )
    ]
    det = detect_unhandled_short_input(code, outcomes)
    assert det is not None
    assert det.category == "unhandled_short_input"


def test_detect_boundary_comparison():
    """Detect using < instead of <= or > instead of >= at boundary tests."""
    code = "def count_passes(marks):\n    return sum(1 for m in marks if m > 40)"
    outcomes = [
        TestOutcome(
            test_number=1,
            is_hidden=False,
            outcome="wrong_output",
            actual_display="2",
            expected_display="3",
        )
    ]
    det = detect_boundary_comparison(code, outcomes)
    assert det is not None
    assert det.category == "boundary_comparison"


def test_detect_mutates_input():
    """Detect unexpected in-place mutations like .sort() or .pop()."""
    code = "def process(items):\n    items.sort()\n    return items[0]"
    outcomes = [
        TestOutcome(test_number=1, is_hidden=False, outcome="wrong_output")
    ]
    det = detect_mutates_input(code, outcomes)
    assert det is not None
    assert det.category == "mutates_input"


@pytest.mark.asyncio
async def test_recurring_mistakes_in_dashboard():
    """Verify recurring mistakes only surface when present in 2+ distinct challenges."""
    import uuid
    uid = f"recurring-test-{uuid.uuid4()}"
    await init_db()
    async with async_session() as session:
        learner = LearnerProfile(supabase_user_id=uid)
        session.add(learner)
        await session.flush()
        
        # Add mistake in Challenge A
        m1 = MistakeRecord(
            learner_id=learner.id,
            submission_id="sub-1",
            challenge_id="challenge-A",
            category="off_by_one",
            evidence="Off by one in slice",
        )
        session.add(m1)
        await session.commit()
        
        # When in only 1 challenge: NOT yet recurring
        dash1 = await get_learner_dashboard(session, learner.id)
        assert len(dash1["recurring_mistakes"]) == 0
        
        # Add same category mistake in Challenge B
        m2 = MistakeRecord(
            learner_id=learner.id,
            submission_id="sub-2",
            challenge_id="challenge-B",
            category="off_by_one",
            evidence="Off by one in loop range",
        )
        session.add(m2)
        await session.commit()
        
        # Now it must be in recurring_mistakes!
        dash2 = await get_learner_dashboard(session, learner.id)
        assert len(dash2["recurring_mistakes"]) == 1
        rec = dash2["recurring_mistakes"][0]
        assert rec["category"] == "off_by_one"
        assert rec["challenge_count"] == 2
