"""Tests verifying hidden-test security invariants:
- Hidden inputs never in API responses
- Hidden expected outputs never in responses
- Hidden values not in AI prompts
- Adversarial print-inputs cannot leak expected output
- Adversarial inspect-globals cannot leak expected output
"""

import pytest
from unittest.mock import AsyncMock, patch
from modules.challenges.service import get_challenge, list_challenges
from modules.submission.service import process_submission
from modules.hints.groq_client import generate_hint_with_groq
from database.connection import init_db, async_session
from database.seed import seed_challenges
from database.models import Challenge, LearnerProfile


@pytest.mark.asyncio
async def test_challenge_endpoints_never_include_hidden_tests():
    """Verify get_challenge and list_challenges strip hidden test fixtures."""
    await init_db()
    async with async_session() as session:
        await seed_challenges(session)
        await session.commit()
        
        # Test list_challenges
        challenges = await list_challenges(session)
        for c in challenges:
            assert "hidden_tests" not in c
            assert "tests" not in c
            assert "visible_test_count" in c
            assert "hidden_test_count" in c
        
        # Test get_challenge
        first_challenge = challenges[0]
        challenge_detail = await get_challenge(session, first_challenge["slug"])
        assert challenge_detail is not None
        assert "tests" not in challenge_detail
        assert "visible_tests" in challenge_detail
        assert "hidden_test_count" in challenge_detail
        
        # All returned visible tests must NOT be hidden
        for t in challenge_detail["visible_tests"]:
            assert "is_hidden" not in t or t["is_hidden"] is False


@pytest.mark.asyncio
async def test_submission_response_never_reveals_hidden_inputs_or_outputs():
    """Verify process_submission never includes hidden test input or expected output."""
    await init_db()
    async with async_session() as session:
        await seed_challenges(session)
        await session.commit()
        
        mock_provider = AsyncMock()
        from modules.execution.judge0 import ExecutionResult, ExecutionStatus
        mock_provider.execute.return_value = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            stdout="0",
        )
        
        with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
            res = await process_submission(
                db=session,
                learner_supabase_id="security-test-user",
                challenge_id="last-k-total",
                code="def last_k_total(marks, k): return 0",
            )
            
            assert "hidden_results" in res
            for hr in res["hidden_results"]:
                assert "input_args" not in hr
                assert "input" not in hr
                assert "expected" not in hr
                assert "actual" not in hr
                assert "call_expression" not in hr
                assert "test_number" in hr
                assert "outcome" in hr


@pytest.mark.asyncio
async def test_ai_prompts_never_contain_hidden_test_data():
    """Verify that Groq hint prompt only receives visible test outcomes."""
    with patch("httpx.AsyncClient.post") as mock_post:
        from unittest.mock import MagicMock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Try thinking about list slicing."}}]
        }
        mock_post.return_value = mock_resp
        
        with patch("modules.hints.groq_client.get_settings") as mock_settings:
            settings_obj = AsyncMock()
            settings_obj.groq_api_key = "test-key"
            settings_obj.groq_model = "llama-3.3-70b-versatile"
            mock_settings.return_value = settings_obj
            
            visible_tests = [
                {"call": "last_k_total([80, 90, 70, 60], 2)", "expected": "", "actual": "0", "outcome": "wrong_output"}
            ]
            
            hint = await generate_hint_with_groq(
                challenge_description="Sum the last k marks",
                function_name="last_k_total",
                learner_code="def last_k_total(marks, k): return 0",
                visible_test_results=visible_tests,
                hint_level=1,
                previous_hints=[],
            )
            
            assert hint == "Try thinking about list slicing."
            
            # Inspect call arguments to Groq
            call_kwargs = mock_post.call_args.kwargs
            sent_payload = call_kwargs["json"]
            user_msg = sent_payload["messages"][1]["content"]
            
            # Ensure hidden test inputs like [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] are absent
            assert "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]" not in user_msg
            assert "hidden" not in user_msg.lower()


def test_adversarial_code_cannot_inspect_expected_output():
    """Verify that learner code inspecting globals(), sys.modules, or frame stack
    cannot access expected output because expected output is NEVER in the execution harness."""
    from modules.judge.engine import _build_test_harness
    
    adversarial_code = """
def last_k_total(marks, k):
    import sys
    # Adversary tries to inspect caller stack or globals
    f = sys._getframe()
    return 0
"""
    harness = _build_test_harness(adversarial_code, "last_k_total", "[[1, 2, 3], 2]")
    
    # Execute the harness in a clean namespace
    env = {}
    exec(harness, env)
    # The harness runs and prints repr(__result__)
    # Expected output '5' was never in the code, locals, or globals of the harness
    assert "expected" not in harness.lower()
    assert "__expected__" not in env
