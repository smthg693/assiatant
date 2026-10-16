"""Hint service — orchestrates curated and AI-generated hints with progression tracking.

Progressive hint ladder:
1. Always try curated hints first (they're vetted for quality)
2. Fall back to Groq AI for additional context
3. Use deterministic fallbacks when AI is unavailable
4. Never reveal complete solutions
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import HintUsage, Submission, Challenge
from modules.hints.curated import get_curated_hint, get_max_curated_level
from modules.hints.groq_client import generate_hint_with_groq

logger = logging.getLogger(__name__)

# Deterministic fallback hints when neither curated nor AI is available
GENERIC_FALLBACKS = [
    "Look carefully at the test cases that failed. What do the inputs have in common?",
    "Try tracing through your code by hand with the failing input. Write down what each variable holds at each step.",
    "Compare the expected output with your actual output. What's the pattern in the difference?",
    "Check your boundary conditions — are you handling the smallest and largest possible inputs correctly?",
    "Review your loop bounds and return statement. Are you processing all the elements you need to, and returning the right value?",
]


async def get_next_hint(
    db: AsyncSession,
    submission_id: str,
    learner_id: str,
    challenge_slug: str,
    challenge_id: str,
    challenge_description: str,
    function_name: str,
    learner_code: str,
    visible_test_results: list[dict],
) -> tuple[str, int, str]:
    """Get the next hint for a submission.
    
    Returns:
        (hint_text, hint_level, source)
        source is one of: 'curated', 'groq', 'fallback'
    """
    # Find the current hint level for this submission
    result = await db.execute(
        select(func.max(HintUsage.level))
        .where(HintUsage.submission_id == submission_id)
    )
    current_max_level = result.scalar() or 0
    next_level = current_max_level + 1
    
    # Get previous hints for context
    prev_result = await db.execute(
        select(HintUsage.hint_text)
        .where(HintUsage.submission_id == submission_id)
        .order_by(HintUsage.level)
    )
    previous_hints = [row[0] for row in prev_result.all()]
    
    # 1. Try curated hint
    curated = get_curated_hint(challenge_slug, next_level)
    if curated:
        hint_text = curated
        source = "curated"
    else:
        # 2. Try Groq AI
        ai_hint = await generate_hint_with_groq(
            challenge_description=challenge_description,
            function_name=function_name,
            learner_code=learner_code,
            visible_test_results=visible_test_results,
            hint_level=min(next_level, 3),  # Groq still uses 3 levels
            previous_hints=previous_hints,
        )
        
        if ai_hint:
            hint_text = ai_hint
            source = "groq"
        else:
            # 3. Deterministic fallback
            fallback_idx = min(next_level - 1, len(GENERIC_FALLBACKS) - 1)
            hint_text = GENERIC_FALLBACKS[fallback_idx]
            source = "fallback"
    
    # Record the hint usage
    hint_usage = HintUsage(
        learner_id=learner_id,
        submission_id=submission_id,
        challenge_id=challenge_id,
        level=next_level,
        hint_text=hint_text,
        source=source,
    )
    db.add(hint_usage)
    await db.flush()
    
    return hint_text, next_level, source


async def get_hint_history(
    db: AsyncSession,
    submission_id: str,
) -> list[dict]:
    """Get all hints given for a submission."""
    result = await db.execute(
        select(HintUsage)
        .where(HintUsage.submission_id == submission_id)
        .order_by(HintUsage.level)
    )
    hints = result.scalars().all()
    return [
        {
            "level": h.level,
            "text": h.hint_text,
            "source": h.source,
        }
        for h in hints
    ]
