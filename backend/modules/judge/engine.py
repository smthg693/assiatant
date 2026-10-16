"""Judge engine — runs individual tests against learner code via the execution provider.

Key security property: hidden test expected outputs are NEVER sent to Judge0.
The learner code + test call is sent for execution; the returned output is
compared against the expected value on the trusted backend.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from modules.execution.judge0 import (
    ExecutionResult,
    ExecutionStatus,
    get_execution_provider,
)

logger = logging.getLogger(__name__)


class ExecutionServiceUnavailableError(Exception):
    """Raised when Judge0 execution service is unavailable, unreachable, or fails internally."""
    def __init__(self, message: str = "Code execution service is currently unavailable. Please try again."):
        super().__init__(message)
        self.message = message


@dataclass
class TestOutcome:
    """Result of a single test evaluation."""
    test_number: int
    is_hidden: bool
    outcome: str  # passed, wrong_output, runtime_error, timeout
    # Visible tests: include call, expected, actual
    # Hidden tests: include only test_number and outcome
    call_expression: Optional[str] = None
    expected_display: Optional[str] = None
    actual_display: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class JudgeResult:
    """Result of judging all tests for a submission."""
    overall_status: str  # passed, failed
    visible_results: list[TestOutcome] = field(default_factory=list)
    hidden_results: list[TestOutcome] = field(default_factory=list)
    total_passed: int = 0
    total_tests: int = 0


def _parse_input_args(input_args_json: str) -> list:
    """Parse input_args safely, handling both standard JSON and Python repr strings."""
    try:
        return json.loads(input_args_json)
    except Exception:
        import ast
        return ast.literal_eval(input_args_json)


def _build_test_harness(learner_code: str, function_name: str, input_args_json: str) -> str:
    """Build a complete Python script that runs one test.
    
    The script:
    1. Defines the learner's function
    2. Calls it with the test inputs
    3. Prints the result as a repr for exact comparison
    
    Security: The expected output is NOT included in this script.
    """
    args = _parse_input_args(input_args_json)
    args_str = ", ".join(repr(a) for a in args)
    
    # We use repr() on the result so we can do exact string comparison
    # against repr(expected). This handles types correctly.
    harness = f"""{learner_code}

# --- Test harness (do not modify) ---
import json as __json__
try:
    __result__ = {function_name}({args_str})
    print(repr(__result__))
except Exception as __e__:
    import sys as __sys__
    print(f"RUNTIME_ERROR: {{type(__e__).__name__}}: {{__e__}}", file=__sys__.stderr)
    __sys__.exit(1)
"""
    return harness


def _normalize_output(output: str) -> str:
    """Normalize output for comparison."""
    return output.strip()


def _compare_output(actual_repr: str, expected_repr: str) -> bool:
    """Compare actual output (repr of result) against expected (repr of expected).
    
    Both should be Python repr strings. We normalize whitespace.
    """
    actual = _normalize_output(actual_repr)
    expected = _normalize_output(expected_repr)
    return actual == expected


async def run_single_test(
    learner_code: str,
    function_name: str,
    input_args_json: str,
    expected_output: str,
    test_number: int,
    is_hidden: bool,
    timeout_seconds: float = 10.0,
) -> TestOutcome:
    """Run a single test case against learner code via Judge0.
    
    The expected output is ONLY used for comparison on the backend.
    It is never sent to Judge0 or included in the execution harness.
    """
    provider = get_execution_provider()
    harness = _build_test_harness(learner_code, function_name, input_args_json)
    
    # Build call expression for display (visible tests only)
    args = _parse_input_args(input_args_json)
    args_str = ", ".join(repr(a) for a in args)
    call_expr = f"{function_name}({args_str})"
    
    exec_result: ExecutionResult = await provider.execute(
        source_code=harness,
        timeout_seconds=timeout_seconds,
    )
    
    # Map execution result to test outcome
    if exec_result.status == ExecutionStatus.TIMEOUT:
        outcome = TestOutcome(
            test_number=test_number,
            is_hidden=is_hidden,
            outcome="timeout",
        )
        if not is_hidden:
            outcome.call_expression = call_expr
            outcome.expected_display = expected_output
            outcome.error_message = "Execution timed out"
        return outcome
    
    if exec_result.status in (
        ExecutionStatus.RUNTIME_ERROR,
        ExecutionStatus.COMPILATION_ERROR,
    ):
        outcome = TestOutcome(
            test_number=test_number,
            is_hidden=is_hidden,
            outcome="runtime_error",
        )
        if not is_hidden:
            outcome.call_expression = call_expr
            outcome.expected_display = expected_output
            # Show error type but not raw details for hidden tests
            error_msg = exec_result.stderr or exec_result.error_message
            # Sanitize: don't show full traceback with line numbers from harness
            if error_msg:
                lines = error_msg.strip().split("\n")
                # Show just the last line (the actual error)
                outcome.error_message = lines[-1] if lines else "Runtime error"
            else:
                outcome.error_message = "Runtime error occurred"
        return outcome
    
    if exec_result.status == ExecutionStatus.INTERNAL_ERROR:
        err_msg = exec_result.error_message or "Code execution service is currently unavailable. Please try again."
        logger.error("Execution provider internal error on test %d: %s", test_number, err_msg)
        raise ExecutionServiceUnavailableError(err_msg)
    
    # SUCCESS — compare output
    actual_output = _normalize_output(exec_result.stdout)
    is_correct = _compare_output(actual_output, expected_output)
    
    if is_correct:
        outcome = TestOutcome(
            test_number=test_number,
            is_hidden=is_hidden,
            outcome="passed",
        )
        if not is_hidden:
            outcome.call_expression = call_expr
            outcome.expected_display = expected_output
            outcome.actual_display = actual_output
        return outcome
    else:
        outcome = TestOutcome(
            test_number=test_number,
            is_hidden=is_hidden,
            outcome="wrong_output",
        )
        if not is_hidden:
            outcome.call_expression = call_expr
            outcome.expected_display = expected_output
            outcome.actual_display = actual_output
        return outcome


async def judge_submission(
    learner_code: str,
    tests: list[dict],
    timeout_per_test: float = 10.0,
) -> JudgeResult:
    """Run all tests for a submission and return the aggregated result.
    
    Args:
        learner_code: The learner's submitted code
        tests: List of test dicts with keys: function_name, input_args, expected_output, 
               test_number, is_hidden
        timeout_per_test: Timeout for each individual test execution
    
    Returns:
        JudgeResult with outcomes for all tests
    """
    visible_results = []
    hidden_results = []
    total_passed = 0
    
    for test in tests:
        outcome = await run_single_test(
            learner_code=learner_code,
            function_name=test["function_name"],
            input_args_json=test["input_args"],
            expected_output=test["expected_output"],
            test_number=test["test_number"],
            is_hidden=test["is_hidden"],
            timeout_seconds=timeout_per_test,
        )
        
        if outcome.outcome == "passed":
            total_passed += 1
        
        if outcome.is_hidden:
            hidden_results.append(outcome)
        else:
            visible_results.append(outcome)
    
    overall = "passed" if total_passed == len(tests) else "failed"
    
    return JudgeResult(
        overall_status=overall,
        visible_results=visible_results,
        hidden_results=hidden_results,
        total_passed=total_passed,
        total_tests=len(tests),
    )
