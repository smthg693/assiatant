"""Learner service — analytics, mastery, recommendations."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    LearnerProfile,
    Submission,
    SubmissionResult,
    MistakeRecord,
    HintUsage,
    ConceptMastery,
    Challenge,
    Recommendation,
)

logger = logging.getLogger(__name__)

# Mastery scoring weights
MASTERY_NO_HINTS = 1.0     # Full credit for solving without hints
MASTERY_WITH_HINTS = 0.6   # Reduced credit when hints were used
MASTERY_DECAY = 0.9        # Decay factor for older submissions


async def get_or_create_learner(db: AsyncSession, supabase_user_id: str) -> LearnerProfile:
    """Get or create a learner profile for a Supabase user."""
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.supabase_user_id == supabase_user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = LearnerProfile(supabase_user_id=supabase_user_id)
        db.add(profile)
        await db.flush()
    
    return profile


async def get_learner_dashboard(db: AsyncSession, learner_id: str) -> dict:
    """Build the complete learner dashboard data.
    
    Includes: recurring mistakes, mastery by concept, progress, recommendation.
    """
    # Get the learner profile
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.id == learner_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return {"error": "Learner not found"}
    
    # 1. Recurring mistakes (appear in 2+ distinct challenges)
    mistake_result = await db.execute(
        select(
            MistakeRecord.category,
            func.count(func.distinct(MistakeRecord.challenge_id)).label("challenge_count"),
        )
        .where(MistakeRecord.learner_id == learner_id)
        .group_by(MistakeRecord.category)
    )
    
    all_mistakes = {}
    recurring_mistakes = []
    for row in mistake_result.all():
        category, count = row
        all_mistakes[category] = count
        if count >= 2:
            recurring_mistakes.append({
                "category": category,
                "challenge_count": count,
                "description": MISTAKE_DESCRIPTIONS.get(category, category),
            })
    
    # 2. Concept mastery
    mastery_result = await db.execute(
        select(ConceptMastery)
        .where(ConceptMastery.learner_id == learner_id)
        .order_by(ConceptMastery.score)
    )
    masteries = mastery_result.scalars().all()
    mastery_data = [
        {
            "concept": m.concept,
            "score": round(m.score, 2),
            "total_challenges": m.total_challenges,
            "completed_challenges": m.completed_challenges,
        }
        for m in masteries
    ]
    
    # 3. Progress
    submission_count_result = await db.execute(
        select(func.count(Submission.id))
        .where(Submission.learner_id == learner_id)
    )
    total_submissions = submission_count_result.scalar() or 0
    
    passed_challenges_result = await db.execute(
        select(func.count(func.distinct(Submission.challenge_id)))
        .where(
            and_(
                Submission.learner_id == learner_id,
                Submission.overall_status == "passed",
            )
        )
    )
    passed_challenges = passed_challenges_result.scalar() or 0
    
    total_challenges_result = await db.execute(select(func.count(Challenge.id)))
    total_challenges = total_challenges_result.scalar() or 0
    
    # 4. Recommendation
    recommendation = await generate_recommendation(db, learner_id, recurring_mistakes, mastery_data)
    
    return {
        "learner_id": learner_id,
        "recurring_mistakes": recurring_mistakes,
        "all_mistakes": all_mistakes,
        "mastery": mastery_data,
        "progress": {
            "total_submissions": total_submissions,
            "challenges_completed": passed_challenges,
            "total_challenges": total_challenges,
        },
        "recommendation": recommendation,
    }


async def generate_recommendation(
    db: AsyncSession,
    learner_id: str,
    recurring_mistakes: list[dict],
    mastery_data: list[dict],
) -> Optional[dict]:
    """Generate a personalized challenge recommendation.
    
    Strategy:
    1. If there are recurring mistakes, find a challenge targeting that concept
    2. If no recurring mistakes, find the weakest mastery area
    3. Recommend an uncompleted challenge in that area
    """
    # Get completed challenge IDs
    completed_result = await db.execute(
        select(func.distinct(Submission.challenge_id))
        .where(
            and_(
                Submission.learner_id == learner_id,
                Submission.overall_status == "passed",
            )
        )
    )
    completed_ids = {row[0] for row in completed_result.all()}
    
    # Get all challenges
    all_challenges_result = await db.execute(select(Challenge))
    all_challenges = all_challenges_result.scalars().all()
    uncompleted = [c for c in all_challenges if c.id not in completed_ids]
    
    if not uncompleted:
        return {
            "challenge_id": None,
            "challenge_title": None,
            "reason": "Congratulations! You've completed all available challenges.",
        }
    
    # Strategy 1: Target recurring mistakes
    if recurring_mistakes:
        worst_mistake = max(recurring_mistakes, key=lambda m: m["challenge_count"])
        # Find a challenge that targets concepts related to this mistake type
        target_concepts = MISTAKE_TO_CONCEPTS.get(worst_mistake["category"], [])
        for challenge in uncompleted:
            challenge_concepts = challenge.concepts.split(",")
            if any(c in challenge_concepts for c in target_concepts):
                # Save recommendation
                rec = Recommendation(
                    learner_id=learner_id,
                    challenge_id=challenge.id,
                    reason=f"This challenge targets {', '.join(target_concepts)} — "
                           f"you've made '{worst_mistake['category']}' mistakes in "
                           f"{worst_mistake['challenge_count']} different challenges.",
                )
                db.add(rec)
                await db.flush()
                
                return {
                    "challenge_id": challenge.id,
                    "challenge_slug": challenge.slug,
                    "challenge_title": challenge.title,
                    "reason": rec.reason,
                }
    
    # Strategy 2: Target weakest mastery area
    if mastery_data:
        weakest = min(mastery_data, key=lambda m: m["score"])
        for challenge in uncompleted:
            if weakest["concept"] in challenge.concepts.split(","):
                rec = Recommendation(
                    learner_id=learner_id,
                    challenge_id=challenge.id,
                    reason=f"Your mastery of '{weakest['concept']}' is at "
                           f"{int(weakest['score'] * 100)}%. This challenge will "
                           f"help you improve.",
                )
                db.add(rec)
                await db.flush()
                
                return {
                    "challenge_id": challenge.id,
                    "challenge_slug": challenge.slug,
                    "challenge_title": challenge.title,
                    "reason": rec.reason,
                }
    
    # Strategy 3: Just pick the next uncompleted by difficulty
    difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
    uncompleted.sort(key=lambda c: difficulty_order.get(c.difficulty, 0))
    next_challenge = uncompleted[0]
    
    return {
        "challenge_id": next_challenge.id,
        "challenge_slug": next_challenge.slug,
        "challenge_title": next_challenge.title,
        "reason": "This is the next challenge in your learning path.",
    }


async def update_mastery(
    db: AsyncSession,
    learner_id: str,
    challenge_id: str,
    passed: bool,
    hints_used: int,
) -> None:
    """Update concept mastery after a submission.
    
    Scoring:
    - Passed with no hints: MASTERY_NO_HINTS (1.0) weight
    - Passed with hints: MASTERY_WITH_HINTS (0.6) weight
    - Failed: 0.0 weight
    
    Score = weighted average of all attempts on challenges with this concept.
    """
    # Get the challenge's concepts
    challenge_result = await db.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = challenge_result.scalar_one_or_none()
    if not challenge:
        return
    
    concepts = [c.strip() for c in challenge.concepts.split(",")]
    
    for concept in concepts:
        # Get or create mastery record
        mastery_result = await db.execute(
            select(ConceptMastery).where(
                and_(
                    ConceptMastery.learner_id == learner_id,
                    ConceptMastery.concept == concept,
                )
            )
        )
        mastery = mastery_result.scalar_one_or_none()
        
        if not mastery:
            mastery = ConceptMastery(
                learner_id=learner_id,
                concept=concept,
                score=0.0,
                total_challenges=0,
                completed_challenges=0,
            )
            db.add(mastery)
        
        # Count total challenges with this concept  
        total_result = await db.execute(
            select(func.count(Challenge.id))
            .where(Challenge.concepts.contains(concept))
        )
        mastery.total_challenges = total_result.scalar() or 0
        
        if passed:
            # Count unique completed challenges with this concept
            completed_result = await db.execute(
                select(func.count(func.distinct(Submission.challenge_id)))
                .join(Challenge, Submission.challenge_id == Challenge.id)
                .where(
                    and_(
                        Submission.learner_id == learner_id,
                        Submission.overall_status == "passed",
                        Challenge.concepts.contains(concept),
                    )
                )
            )
            mastery.completed_challenges = completed_result.scalar() or 0
            
            # Calculate score
            weight = MASTERY_NO_HINTS if hints_used == 0 else MASTERY_WITH_HINTS
            if mastery.total_challenges > 0:
                mastery.score = min(1.0, (mastery.completed_challenges / mastery.total_challenges) * weight)
            else:
                mastery.score = weight
        
        await db.flush()


# Mapping from mistake categories to relevant concepts
MISTAKE_TO_CONCEPTS = {
    "off_by_one": ["slicing", "iteration", "lists"],
    "unhandled_short_input": ["edge-cases", "lists"],
    "print_not_return": ["functions", "iteration"],
    "boundary_comparison": ["comparison", "iteration"],
    "mutates_input": ["lists", "mutation"],
}

MISTAKE_DESCRIPTIONS = {
    "off_by_one": "Off-by-one errors in indexing or ranges",
    "unhandled_short_input": "Missing edge case handling for empty or short inputs",
    "print_not_return": "Using print() instead of returning the value",
    "boundary_comparison": "Wrong comparison operator at boundaries (< vs <=)",
    "mutates_input": "Unintended mutation of input data",
}
