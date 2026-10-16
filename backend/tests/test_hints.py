"""Tests for Hint Ladders, AI coaching fallback, progression, and anti-solution security."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from modules.hints.curated import CURATED_HINTS, get_curated_hint
from modules.hints.groq_client import _contains_solution, generate_hint_with_groq
from modules.hints.service import get_next_hint, get_hint_history, GENERIC_FALLBACKS
from database.connection import init_db, async_session
from database.seed import seed_challenges
from database.models import Submission, LearnerProfile, Challenge
import uuid


def test_all_challenges_have_curated_hints():
    """Verify all challenges have at least 3 curated progressive hints."""
    from challenges.bank import CHALLENGES
    for c in CHALLENGES:
        slug = c["slug"]
        assert slug in CURATED_HINTS, f"Missing curated hints for {slug}"
        hints = CURATED_HINTS[slug]
        assert len(hints) >= 3, f"{slug} has only {len(hints)} curated hints (expected 3+)"
        
        # Test 1-indexed helper
        assert get_curated_hint(slug, 1) == hints[0]
        assert get_curated_hint(slug, 2) == hints[1]
        assert get_curated_hint(slug, 3) == hints[2]


def test_anti_solution_detector():
    """Verify _contains_solution detects complete code solutions."""
    # Complete function definition
    assert _contains_solution("Here is def last_k_total(marks, k): return sum(marks)", "last_k_total") is True
    # Code block with return
    assert _contains_solution("Try this:\n```python\nresult = sum(marks)\nreturn result\n```", "last_k_total") is True
    # Conceptual guidance without solution code
    assert _contains_solution("Think about list slicing with negative indices.", "last_k_total") is False


@pytest.mark.asyncio
async def test_hint_ladder_progression_and_persistence():
    """Verify progressive hint requests increment level and persist history."""
    await init_db()
    async with async_session() as session:
        uid = f"hint-learner-{uuid.uuid4()}"
        learner = LearnerProfile(supabase_user_id=uid)
        session.add(learner)
        await session.flush()
        
        # Create submission
        sub = Submission(
            learner_id=learner.id,
            challenge_id="last-k-total",
            code="def last_k_total(marks, k): pass",
            overall_status="failed",
        )
        session.add(sub)
        await session.commit()
        
        # Level 1
        h1, lvl1, src1 = await get_next_hint(
            db=session,
            submission_id=sub.id,
            learner_id=learner.id,
            challenge_slug="last-k-total",
            challenge_id="last-k-total",
            challenge_description="Sum the last k marks",
            function_name="last_k_total",
            learner_code=sub.code,
            visible_test_results=[],
        )
        assert lvl1 == 1
        assert src1 == "curated"
        assert h1 == CURATED_HINTS["last-k-total"][0]
        
        # Level 2
        h2, lvl2, src2 = await get_next_hint(
            db=session,
            submission_id=sub.id,
            learner_id=learner.id,
            challenge_slug="last-k-total",
            challenge_id="last-k-total",
            challenge_description="Sum the last k marks",
            function_name="last_k_total",
            learner_code=sub.code,
            visible_test_results=[],
        )
        assert lvl2 == 2
        assert src2 == "curated"
        assert h2 == CURATED_HINTS["last-k-total"][1]
        
        # History
        history = await get_hint_history(session, sub.id)
        assert len(history) == 2
        assert history[0]["level"] == 1
        assert history[1]["level"] == 2


@pytest.mark.asyncio
async def test_deterministic_fallback_when_beyond_curated_and_ai_unavailable():
    """Verify deterministic fallback hints are used when curated is exhausted and Groq fails."""
    await init_db()
    async with async_session() as session:
        uid = f"fallback-learner-{uuid.uuid4()}"
        learner = LearnerProfile(supabase_user_id=uid)
        session.add(learner)
        await session.flush()
        
        sub = Submission(
            learner_id=learner.id,
            challenge_id="test-challenge",
            code="def f(): pass",
            overall_status="failed",
        )
        session.add(sub)
        await session.commit()
        
        with patch("modules.hints.service.generate_hint_with_groq", return_value=None):
            hint_text, level, source = await get_next_hint(
                db=session,
                submission_id=sub.id,
                learner_id=learner.id,
                challenge_slug="non-existent-challenge",
                challenge_id="test-challenge",
                challenge_description="Desc",
                function_name="f",
                learner_code=sub.code,
                visible_test_results=[],
            )
            assert level == 1
            assert source == "fallback"
            assert hint_text in GENERIC_FALLBACKS
