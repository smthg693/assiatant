"""Tests for Learner mastery scoring, recommendation logic, and progress tracking."""

import pytest
import uuid
from database.connection import init_db, async_session
from database.seed import seed_challenges
from database.models import LearnerProfile, Submission, Challenge, ConceptMastery
from modules.learner.service import update_mastery, get_learner_dashboard, generate_recommendation
from sqlalchemy import select


@pytest.mark.asyncio
async def test_mastery_scoring_with_and_without_hints():
    """Verify mastery weight: 1.0 without hints vs 0.6 with hints."""
    await init_db()
    async with async_session() as session:
        await seed_challenges(session)
        await session.commit()
        
        # Get last-k-total challenge
        c_res = await session.execute(select(Challenge).where(Challenge.slug == "last-k-total"))
        challenge = c_res.scalar_one()
        
        uid1 = f"learner-nohints-{uuid.uuid4()}"
        l1 = LearnerProfile(supabase_user_id=uid1)
        session.add(l1)
        await session.flush()
        
        # Learner 1 solves with 0 hints
        sub1 = Submission(
            learner_id=l1.id,
            challenge_id=challenge.id,
            code="def last_k_total(marks, k): return sum(marks[-k:])",
            overall_status="passed",
        )
        session.add(sub1)
        await session.commit()
        
        await update_mastery(session, l1.id, challenge.id, passed=True, hints_used=0)
        await session.commit()
        
        # Check concept mastery for 'slicing'
        m1_res = await session.execute(
            select(ConceptMastery).where(ConceptMastery.learner_id == l1.id, ConceptMastery.concept == "slicing")
        )
        m1 = m1_res.scalar_one_or_none()
        assert m1 is not None
        assert m1.score > 0
        score_nohints = m1.score
        
        # Learner 2 solves with 2 hints
        uid2 = f"learner-withhints-{uuid.uuid4()}"
        l2 = LearnerProfile(supabase_user_id=uid2)
        session.add(l2)
        await session.flush()
        
        sub2 = Submission(
            learner_id=l2.id,
            challenge_id=challenge.id,
            code="def last_k_total(marks, k): return sum(marks[-k:])",
            overall_status="passed",
        )
        session.add(sub2)
        await session.commit()
        
        await update_mastery(session, l2.id, challenge.id, passed=True, hints_used=2)
        await session.commit()
        
        m2_res = await session.execute(
            select(ConceptMastery).where(ConceptMastery.learner_id == l2.id, ConceptMastery.concept == "slicing")
        )
        m2 = m2_res.scalar_one_or_none()
        assert m2 is not None
        score_withhints = m2.score
        
        # Solving with hints gives lower score than without hints
        assert score_nohints > score_withhints


@pytest.mark.asyncio
async def test_recommendations_target_recurring_mistakes():
    """Verify recommendation system prioritizes concepts associated with recurring mistakes."""
    await init_db()
    async with async_session() as session:
        await seed_challenges(session)
        await session.commit()
        
        uid = f"rec-learner-{uuid.uuid4()}"
        l = LearnerProfile(supabase_user_id=uid)
        session.add(l)
        await session.flush()
        
        recurring = [
            {"category": "off_by_one", "challenge_count": 2, "description": "Off-by-one errors"}
        ]
        mastery = [
            {"concept": "strings", "score": 0.5, "total_challenges": 2, "completed_challenges": 1}
        ]
        
        rec = await generate_recommendation(session, l.id, recurring, mastery)
        assert rec is not None
        assert rec["challenge_id"] is not None
        # Rationale must explain that it targets the recurring mistake category
        assert "off_by_one" in rec["reason"]
