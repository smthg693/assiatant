"""Mistake detection across 5 required categories.

Categories:
- off_by_one: Off-by-one errors in indexing/ranges
- unhandled_short_input: Missing edge case for short/empty inputs
- print_not_return: Using print() instead of return
- boundary_comparison: Wrong comparison operator at boundaries (< vs <=, etc.)
- mutates_input: Unintended mutation of input data

Detection uses:
1. Static analysis of the submitted code (AST where possible)
2. Evidence from failed test outcomes (which tests failed and how)
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass

from modules.judge.engine import TestOutcome


@dataclass
class MistakeDetection:
    """A detected mistake with its category and evidence."""
    category: str
    evidence: str
    confidence: float  # 0.0 to 1.0


def detect_print_not_return(code: str, outcomes: list[TestOutcome]) -> MistakeDetection | None:
    """Detect if learner used print() instead of return.
    
    Evidence:
    - Code contains print() calls
    - All/most tests return None (repr = 'None')
    """
    has_print = "print(" in code
    
    # Check if any visible test got 'None' as output
    none_outputs = 0
    visible_count = 0
    for o in outcomes:
        if not o.is_hidden and o.outcome == "wrong_output":
            visible_count += 1
            if o.actual_display and o.actual_display.strip() == "None":
                none_outputs += 1
    
    if has_print and none_outputs > 0:
        return MistakeDetection(
            category="print_not_return",
            evidence=f"Your function uses print() but returns None. Found {none_outputs} test(s) where the function returned None instead of the expected value.",
            confidence=0.9,
        )
    
    # Even without print, if all results are None
    if visible_count > 0 and none_outputs == visible_count:
        return MistakeDetection(
            category="print_not_return",
            evidence="Your function returns None for all test cases. Make sure you're using 'return' to give back the result.",
            confidence=0.7,
        )
    
    return None


def detect_off_by_one(code: str, outcomes: list[TestOutcome]) -> MistakeDetection | None:
    """Detect off-by-one errors.
    
    Evidence:
    - Some tests pass but boundary-adjacent tests fail
    - Range/slice operations with numeric offsets
    - Actual output close to expected (e.g., list differs by one element)
    """
    # Check if there are range/slice operations
    has_range = "range(" in code
    has_slice = bool(re.search(r'\[.*:.*\]', code))
    
    if not (has_range or has_slice):
        return None
    
    # Look for visible tests where output is close but wrong
    for o in outcomes:
        if not o.is_hidden and o.outcome == "wrong_output" and o.actual_display and o.expected_display:
            # Check if lists differ by one element
            try:
                actual = eval(o.actual_display)  # Safe: this is our own output
                expected = eval(o.expected_display)
                if isinstance(actual, list) and isinstance(expected, list):
                    if abs(len(actual) - len(expected)) == 1:
                        return MistakeDetection(
                            category="off_by_one",
                            evidence=f"Test {o.test_number}: Output list has {len(actual)} elements but expected {len(expected)}. Check your range/slice boundaries.",
                            confidence=0.8,
                        )
                    if len(actual) == len(expected) and len(actual) > 0 and actual != expected:
                        if (actual[0] == 0 and expected[0] == 1) or (actual[0] == 1 and expected[0] == 0):
                            return MistakeDetection(
                                category="off_by_one",
                                evidence=f"Test {o.test_number}: Sequence starts from {actual[0]} instead of {expected[0]}. Check your loop range start.",
                                confidence=0.85,
                            )
                        if actual[:-1] == expected[1:] or actual[1:] == expected[:-1]:
                            return MistakeDetection(
                                category="off_by_one",
                                evidence=f"Test {o.test_number}: Elements appear shifted by one position. Check your range start/stop values.",
                                confidence=0.85,
                            )
                elif isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
                    # Numeric off-by-one
                    if abs(actual - expected) <= 2 and actual != expected:
                        return MistakeDetection(
                            category="off_by_one",
                            evidence=f"Test {o.test_number}: Your result is {actual} but expected {expected}. This looks like an off-by-one error.",
                            confidence=0.7,
                        )
            except Exception:
                pass
    
    return None


def detect_unhandled_short_input(code: str, outcomes: list[TestOutcome]) -> MistakeDetection | None:
    """Detect missing edge case handling for empty/short inputs.
    
    Evidence:
    - Tests with empty lists/strings or zero/small inputs fail
    - Runtime errors on short inputs (IndexError, etc.)
    """
    for o in outcomes:
        if not o.is_hidden and o.outcome in ("wrong_output", "runtime_error"):
            if o.call_expression:
                # Check if the test uses empty/short inputs
                is_short_input = any(pattern in o.call_expression for pattern in [
                    "[]", "''", '""', ", 0)", "(0)", "(1)", "[0]",
                ])
                if is_short_input:
                    if o.outcome == "runtime_error":
                        return MistakeDetection(
                            category="unhandled_short_input",
                            evidence=f"Test {o.test_number}: Runtime error on input {o.call_expression}. Your function doesn't handle empty or very short inputs.",
                            confidence=0.9,
                        )
                    else:
                        return MistakeDetection(
                            category="unhandled_short_input",
                            evidence=f"Test {o.test_number}: Wrong output for {o.call_expression}. Consider adding a check for empty or short inputs.",
                            confidence=0.7,
                        )
    
    return None


def detect_boundary_comparison(code: str, outcomes: list[TestOutcome]) -> MistakeDetection | None:
    """Detect wrong comparison operators at boundaries (< vs <=, > vs >=).
    
    Evidence:
    - Boundary test cases fail (e.g., exactly 40 for pass mark)
    - Code uses < where <= might be needed (or vice versa)
    """
    # Look for comparison operators
    has_lt = " < " in code and " <= " not in code.replace(" < ", "")
    has_gt = " > " in code and " >= " not in code.replace(" > ", "")
    
    if not (has_lt or has_gt):
        return None
    
    for o in outcomes:
        if not o.is_hidden and o.outcome == "wrong_output" and o.actual_display and o.expected_display:
            try:
                actual = eval(o.actual_display)
                expected = eval(o.expected_display)
                if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
                    if abs(actual - expected) == 1:
                        op = "<" if has_lt else ">"
                        return MistakeDetection(
                            category="boundary_comparison",
                            evidence=f"Test {o.test_number}: Off by 1 at a boundary. Check whether you need '{op}' or '{op}=' in your comparison.",
                            confidence=0.8,
                        )
            except Exception:
                pass
    
    return None


def detect_mutates_input(code: str, outcomes: list[TestOutcome]) -> MistakeDetection | None:
    """Detect unintended mutation of input data.
    
    Evidence:
    - Code uses in-place operations (.sort(), .reverse(), .append(), etc.)
    - Or uses list assignment that modifies the original
    """
    mutation_patterns = [
        r'\.sort\s*\(', r'\.reverse\s*\(', r'\.append\s*\(',
        r'\.extend\s*\(', r'\.insert\s*\(', r'\.pop\s*\(',
        r'\.remove\s*\(', r'\.clear\s*\(',
    ]
    
    mutations_found = []
    for pattern in mutation_patterns:
        if re.search(pattern, code):
            mutations_found.append(pattern.replace(r'\s*\(', '(').replace(r'\.', '.').rstrip('\\'))
    
    if not mutations_found:
        return None
    
    # Only flag if there are failing tests (mutation might be intentional and correct)
    has_failures = any(o.outcome != "passed" for o in outcomes)
    if not has_failures:
        return None
    
    clean_names = [m.replace("\\", "").replace(r"\s*\(", "(") for m in mutations_found]
    
    return MistakeDetection(
        category="mutates_input",
        evidence=f"Your code uses in-place operations ({', '.join(mutations_found[:3])}). This might modify the original input, causing unexpected results in later tests.",
        confidence=0.6,
    )


def detect_mistakes(code: str, outcomes: list[TestOutcome]) -> list[MistakeDetection]:
    """Run all mistake detectors and return detected mistakes.
    
    Returns only high-confidence detections, one per category max.
    """
    detectors = [
        detect_print_not_return,
        detect_off_by_one,
        detect_unhandled_short_input,
        detect_boundary_comparison,
        detect_mutates_input,
    ]
    
    mistakes = []
    for detector in detectors:
        result = detector(code, outcomes)
        if result and result.confidence >= 0.5:
            mistakes.append(result)
    
    return mistakes
