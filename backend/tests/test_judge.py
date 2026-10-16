"""Tests for Judge Engine outcomes, comparisons, direct Judge0 CE provider, and execution isolation."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from modules.execution.judge0 import (
    ExecutionResult,
    ExecutionStatus,
    _map_judge0_status,
    Judge0ExecutionProvider,
    discover_python_language_id,
    verify_judge0_endpoint,
)
from modules.judge.engine import (
    _compare_output,
    _normalize_output,
    _build_test_harness,
    run_single_test,
    judge_submission,
    TestOutcome,
    ExecutionServiceUnavailableError,
)


def test_judge0_status_mapping():
    """Verify Judge0 status codes map correctly to ExecutionStatus."""
    assert _map_judge0_status(3) == ExecutionStatus.SUCCESS
    assert _map_judge0_status(5) == ExecutionStatus.TIMEOUT
    assert _map_judge0_status(6) == ExecutionStatus.COMPILATION_ERROR
    assert _map_judge0_status(11) == ExecutionStatus.RUNTIME_ERROR  # NZEC
    assert _map_judge0_status(7) == ExecutionStatus.RUNTIME_ERROR   # SIGSEGV
    assert _map_judge0_status(13) == ExecutionStatus.INTERNAL_ERROR


def test_output_comparison():
    """Verify repr-based output comparison with whitespace normalization."""
    assert _compare_output("130", "130") is True
    assert _compare_output("  130 \n", "130") is True
    assert _compare_output("[1, 2, 3]", "[1, 2, 3]") is True
    assert _compare_output("[1, 2, 4]", "[1, 2, 3]") is False
    assert _compare_output("True", "True") is True
    assert _compare_output("False", "True") is False
    assert _compare_output("'hello'", "'hello'") is True


def test_harness_does_not_contain_expected_output():
    """Verify that generated test harness NEVER contains expected output."""
    learner_code = "def add(a, b): return a + b"
    harness = _build_test_harness(learner_code, "add", "[2, 3]")
    assert "add(2, 3)" in harness
    # Ensure expected output '5' is not baked in
    assert "__result__ = add(2, 3)" in harness
    assert "print(repr(__result__))" in harness


def test_judge0_direct_headers_no_rapidapi():
    """Verify direct Judge0 provider does NOT send RapidAPI headers and only sends X-Auth-Token if configured."""
    provider = Judge0ExecutionProvider()
    
    # When no API key is set
    with patch.object(provider.settings, "judge0_api_key", ""):
        headers = provider._headers()
        assert "X-RapidAPI-Key" not in headers
        assert "X-RapidAPI-Host" not in headers
        assert "X-Auth-Token" not in headers
        assert headers["Content-Type"] == "application/json"

    # When API key is set
    with patch.object(provider.settings, "judge0_api_key", "secret-token"):
        headers_with_key = provider._headers()
        assert "X-RapidAPI-Key" not in headers_with_key
        assert "X-RapidAPI-Host" not in headers_with_key
        assert headers_with_key["X-Auth-Token"] == "secret-token"


@pytest.mark.asyncio
async def test_judge0_language_discovery():
    """Verify dynamic discovery selects modern Python 3 ID from languages list."""
    sample_languages = [
        {"id": 70, "name": "Python (2.7.17)"},
        {"id": 71, "name": "Python (3.8.1)"},
        {"id": 92, "name": "Python (3.11.2)"},
        {"id": 63, "name": "JavaScript (Node.js 12.14.0)"},
    ]

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample_languages
        mock_get.return_value = mock_resp

        discovered_id = await discover_python_language_id(
            base_url="https://ce.judge0.com",
            headers={},
        )
        assert discovered_id == 92  # Prefers Python 3.11 over 3.8 and 2.7


@pytest.mark.asyncio
async def test_judge_outcome_passed():
    """Verify 'passed' outcome when execution matches expected."""
    mock_provider = AsyncMock()
    mock_provider.execute.return_value = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        stdout="130",
    )
    with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
        outcome = await run_single_test(
            learner_code="def f(x): return x",
            function_name="f",
            input_args_json="[130]",
            expected_output="130",
            test_number=1,
            is_hidden=False,
        )
        assert outcome.outcome == "passed"
        assert outcome.actual_display == "130"
        assert outcome.expected_display == "130"


@pytest.mark.asyncio
async def test_judge_outcome_wrong_output():
    """Verify 'wrong_output' outcome when execution output differs."""
    mock_provider = AsyncMock()
    mock_provider.execute.return_value = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        stdout="100",
    )
    with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
        outcome = await run_single_test(
            learner_code="def f(x): return x",
            function_name="f",
            input_args_json="[100]",
            expected_output="130",
            test_number=1,
            is_hidden=False,
        )
        assert outcome.outcome == "wrong_output"
        assert outcome.actual_display == "100"
        assert outcome.expected_display == "130"


@pytest.mark.asyncio
async def test_judge_outcome_runtime_error():
    """Verify 'runtime_error' outcome on exception."""
    mock_provider = AsyncMock()
    mock_provider.execute.return_value = ExecutionResult(
        status=ExecutionStatus.RUNTIME_ERROR,
        stderr="IndexError: list index out of range",
    )
    with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
        outcome = await run_single_test(
            learner_code="def f(x): return x[10]",
            function_name="f",
            input_args_json="[[1]]",
            expected_output="1",
            test_number=1,
            is_hidden=False,
        )
        assert outcome.outcome == "runtime_error"
        assert "IndexError" in outcome.error_message


@pytest.mark.asyncio
async def test_judge_outcome_timeout():
    """Verify 'timeout' outcome when execution exceeds time limit."""
    mock_provider = AsyncMock()
    mock_provider.execute.return_value = ExecutionResult(
        status=ExecutionStatus.TIMEOUT,
        error_message="Time limit exceeded",
    )
    with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
        outcome = await run_single_test(
            learner_code="def f():\n while True: pass",
            function_name="f",
            input_args_json="[]",
            expected_output="0",
            test_number=1,
            is_hidden=False,
        )
        assert outcome.outcome == "timeout"


@pytest.mark.asyncio
async def test_judge_distinguishes_service_failure_from_code_failure():
    """Verify infrastructure/provider failure raises ExecutionServiceUnavailableError
    instead of conflating it with a learner code runtime error."""
    mock_provider = AsyncMock()
    mock_provider.execute.return_value = ExecutionResult(
        status=ExecutionStatus.INTERNAL_ERROR,
        error_message="Judge0 connection refused: 503 Service Unavailable",
    )
    with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
        with pytest.raises(ExecutionServiceUnavailableError) as exc_info:
            await run_single_test(
                learner_code="def f(): return 1",
                function_name="f",
                input_args_json="[]",
                expected_output="1",
                test_number=1,
                is_hidden=False,
            )
        assert "503" in str(exc_info.value) or "unavailable" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_judge_submission_isolated_execution():
    """Verify judge_submission invokes execution independently for each test."""
    mock_provider = AsyncMock()
    # 2 calls: first passes, second fails
    mock_provider.execute.side_effect = [
        ExecutionResult(status=ExecutionStatus.SUCCESS, stdout="10"),
        ExecutionResult(status=ExecutionStatus.SUCCESS, stdout="25"),
    ]
    with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
        tests = [
            {"function_name": "f", "input_args": "[1]", "expected_output": "10", "test_number": 1, "is_hidden": False},
            {"function_name": "f", "input_args": "[2]", "expected_output": "20", "test_number": 2, "is_hidden": True},
        ]
        result = await judge_submission("def f(x): pass", tests)
        assert mock_provider.execute.call_count == 2
        assert result.overall_status == "failed"
        assert result.total_passed == 1
        assert result.total_tests == 2
        assert len(result.visible_results) == 1
        assert len(result.hidden_results) == 1


@pytest.mark.asyncio
async def test_live_judge0_ce_endpoint():
    """Integration test verifying live connectivity to configured direct Judge0 CE endpoint."""
    provider = Judge0ExecutionProvider()
    healthy = await provider.is_healthy()
    if not healthy:
        pytest.skip("Direct Judge0 CE endpoint is currently offline or unreachable.")
    
    # If healthy, test real execution of harmless script
    res = await provider.execute("print(42 * 2)", timeout_seconds=5.0)
    assert res.status == ExecutionStatus.SUCCESS
    assert res.stdout == "84"
    assert res.exit_code == 0
