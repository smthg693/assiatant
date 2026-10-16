"""Database seeding — load challenge bank into the database."""

from __future__ import annotations

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Challenge, ChallengeTest
from challenges.bank import CHALLENGES

logger = logging.getLogger(__name__)


async def seed_challenges(db: AsyncSession) -> int:
    """Seed all challenges from the challenge bank into the database.
    
    Skips challenges that already exist (by slug).
    Returns the number of new challenges added.
    """
    added = 0
    
    for challenge_data in CHALLENGES:
        # Check if already exists
        result = await db.execute(
            select(Challenge).where(Challenge.slug == challenge_data["slug"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info("Challenge '%s' already exists, skipping", challenge_data["slug"])
            continue
        
        # Create challenge
        challenge = Challenge(
            slug=challenge_data["slug"],
            title=challenge_data["title"],
            description=challenge_data["description"],
            starter_code=challenge_data["starter_code"],
            difficulty=challenge_data["difficulty"],
            concepts=challenge_data["concepts"],
        )
        db.add(challenge)
        await db.flush()  # Get the ID
        
        # Create tests
        for test_data in challenge_data["tests"]:
            test = ChallengeTest(
                challenge_id=challenge.id,
                test_number=test_data["test_number"],
                is_hidden=test_data["is_hidden"],
                function_name=test_data["function_name"],
                input_args=test_data["input_args"],
                expected_output=test_data["expected_output"],
            )
            db.add(test)
        
        added += 1
        logger.info("Seeded challenge: %s (%d tests)", challenge_data["slug"], len(challenge_data["tests"]))
    
    await db.flush()
    logger.info("Seeding complete: %d new challenges added", added)
    return added
