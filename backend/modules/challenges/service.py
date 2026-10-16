"""Challenge service — CRUD operations for challenges."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Challenge, ChallengeTest


async def list_challenges(
    db: AsyncSession,
    difficulty: Optional[str] = None,
    concept: Optional[str] = None,
    search: Optional[str] = None,
) -> list[dict]:
    """List all challenges with optional filters.
    
    Never returns hidden test details.
    """
    query = select(Challenge).order_by(Challenge.difficulty, Challenge.title)
    
    if difficulty:
        query = query.where(Challenge.difficulty == difficulty.lower())
    
    if concept:
        query = query.where(Challenge.concepts.contains(concept.lower()))
    
    if search:
        query = query.where(
            Challenge.title.ilike(f"%{search}%")
            | Challenge.description.ilike(f"%{search}%")
        )
    
    result = await db.execute(query)
    challenges = result.scalars().all()
    
    items = []
    for c in challenges:
        # Count tests
        test_result = await db.execute(
            select(ChallengeTest).where(ChallengeTest.challenge_id == c.id)
        )
        tests = test_result.scalars().all()
        visible_count = sum(1 for t in tests if not t.is_hidden)
        hidden_count = sum(1 for t in tests if t.is_hidden)
        
        items.append({
            "id": c.id,
            "slug": c.slug,
            "title": c.title,
            "description": c.description,
            "starter_code": c.starter_code,
            "difficulty": c.difficulty,
            "concepts": c.concepts.split(","),
            "visible_test_count": visible_count,
            "hidden_test_count": hidden_count,
        })
    
    return items


async def get_challenge(db: AsyncSession, challenge_id: str) -> Optional[dict]:
    """Get a single challenge with visible tests only.
    
    Hidden test inputs and expected outputs are NEVER returned.
    """
    result = await db.execute(
        select(Challenge).where(
            (Challenge.id == challenge_id) | (Challenge.slug == challenge_id)
        )
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        return None
    
    # Get visible tests only for API response
    test_result = await db.execute(
        select(ChallengeTest)
        .where(ChallengeTest.challenge_id == challenge.id)
        .order_by(ChallengeTest.test_number)
    )
    all_tests = test_result.scalars().all()
    
    visible_tests = []
    hidden_count = 0
    for t in all_tests:
        if t.is_hidden:
            hidden_count += 1
        else:
            visible_tests.append({
                "test_number": t.test_number,
                "function_name": t.function_name,
                "input_args": t.input_args,
                "expected_output": t.expected_output,
            })
    
    return {
        "id": challenge.id,
        "slug": challenge.slug,
        "title": challenge.title,
        "description": challenge.description,
        "starter_code": challenge.starter_code,
        "difficulty": challenge.difficulty,
        "concepts": challenge.concepts.split(","),
        "visible_tests": visible_tests,
        "hidden_test_count": hidden_count,
    }


async def get_challenge_tests_for_judging(
    db: AsyncSession, challenge_id: str
) -> list[dict]:
    """Get ALL tests (visible + hidden) for server-side judging.
    
    This data is used internally only — never sent to the client.
    """
    result = await db.execute(
        select(ChallengeTest)
        .where(ChallengeTest.challenge_id == challenge_id)
        .order_by(ChallengeTest.test_number)
    )
    tests = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "test_number": t.test_number,
            "is_hidden": t.is_hidden,
            "function_name": t.function_name,
            "input_args": t.input_args,
            "expected_output": t.expected_output,
        }
        for t in tests
    ]
