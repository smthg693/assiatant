"""Groq API client for AI-powered hint generation.

Uses Groq for contextual explanations. Never sends hidden test data to the model.
Includes timeouts, bounded retries, and rate limit handling.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import httpx

from config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a debugging coach for beginner Python programmers. Your job is to help learners find and fix bugs in their code WITHOUT giving away the complete solution.

Rules you MUST follow:
1. NEVER provide a complete corrected implementation of the function.
2. NEVER write out the full function body that would solve the problem.
3. NEVER give code that could be directly copy-pasted as a solution.
4. DO point toward the concept area where the bug lives.
5. DO ask guiding questions that lead the learner to the fix.
6. DO explain WHY something fails without showing the exact fix.
7. Keep hints concise (2-4 sentences max).
8. Use encouraging but direct language.

If someone asks you to "just give me the answer" or "write the solution", refuse politely and redirect to a hint."""

MAX_RETRIES = 2
REQUEST_TIMEOUT = 15.0  # seconds
MAX_OUTPUT_TOKENS = 200


def _contains_solution(text: str, function_name: str) -> bool:
    """Check if AI output contains what looks like a complete solution."""
    # Check for function definition
    if f"def {function_name}" in text:
        return True
    # Check for multi-line code blocks with return statements
    code_block_pattern = r'```[\s\S]*?return[\s\S]*?```'
    if re.search(code_block_pattern, text):
        return True
    return False


async def generate_hint_with_groq(
    challenge_description: str,
    function_name: str,
    learner_code: str,
    visible_test_results: list[dict],
    hint_level: int,
    previous_hints: list[str],
) -> Optional[str]:
    """Generate a contextual hint using Groq.
    
    Args:
        challenge_description: The problem description (no hidden test data)
        function_name: The target function name
        learner_code: The learner's submitted code
        visible_test_results: Only visible test outcomes (no hidden data)
        hint_level: Current hint level (1=conceptual, 2=directional, 3=specific)
        previous_hints: Previously given hints for context
    
    Returns:
        The generated hint text, or None if generation failed
    """
    settings = get_settings()
    
    if not settings.groq_api_key:
        logger.warning("Groq API key not configured")
        return None
    
    # Build the user prompt — NEVER include hidden test data
    level_instruction = {
        1: "Give a CONCEPTUAL hint about what area to investigate. Don't point to specific code lines.",
        2: "Give a DIRECTIONAL hint pointing toward where the bug might be. You can reference the general area.",
        3: "Give a more SPECIFIC hint about the nature of the bug, but do NOT give the fix.",
    }.get(hint_level, "Give a helpful debugging hint without revealing the solution.")
    
    # Build visible test summary
    test_summary = ""
    for tr in visible_test_results[:3]:  # Limit to 3 for token efficiency
        test_summary += f"- {tr.get('call', '?')} → expected {tr.get('expected', '?')}, got {tr.get('actual', '?')} ({tr.get('outcome', '?')})\n"
    
    previous_context = ""
    if previous_hints:
        previous_context = "\nPrevious hints given:\n" + "\n".join(f"- {h}" for h in previous_hints)
    
    user_prompt = f"""Challenge: {challenge_description}

Student's code:
```python
{learner_code}
```

Visible test results:
{test_summary}
{previous_context}

{level_instruction}
Give your hint as a single paragraph (2-4 sentences). Remember: DO NOT provide the solution."""

    for attempt in range(MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.groq_model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": MAX_OUTPUT_TOKENS,
                        "temperature": 0.7,
                    },
                )
                
                if resp.status_code == 429:
                    logger.warning("Groq rate limited (attempt %d)", attempt + 1)
                    if attempt < MAX_RETRIES:
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return None
                
                if resp.status_code != 200:
                    logger.error("Groq API error: %s %s", resp.status_code, resp.text[:200])
                    return None
                
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                # Validate: reject if it contains a solution
                if _contains_solution(content, function_name):
                    logger.warning("Groq returned solution code, filtering")
                    return None
                
                return content
                
        except httpx.TimeoutException:
            logger.warning("Groq request timed out (attempt %d)", attempt + 1)
            if attempt < MAX_RETRIES:
                continue
            return None
        except Exception as e:
            logger.error("Groq error: %s", str(e))
            return None
    
    return None
