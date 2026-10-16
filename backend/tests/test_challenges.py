"""Tests verifying all challenges in the bank have correct specifications and working solutions."""

import json
import pytest
from challenges.bank import CHALLENGES

# Reference implementations of all challenges
REFERENCE_SOLUTIONS = {
    "last-k-total": """
def last_k_total(marks, k):
    if not marks or k <= 0:
        return 0
    return sum(marks[-k:])
""",
    "count-passes": """
def count_passes(marks):
    return sum(1 for m in marks if m >= 40)
""",
    "first-n-squares": """
def first_n_squares(n):
    return [i * i for i in range(1, n + 1)]
""",
    "middle-three": """
def middle_three(items):
    if len(items) < 3:
        return items
    mid = len(items) // 2
    return items[mid - 1:mid + 2]
""",
    "reverse-words": """
def reverse_words(sentence):
    return " ".join(word[::-1] for word in sentence.split(" "))
""",
    "fizzbuzz-list": """
def fizzbuzz_list(n):
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(i)
    return result
""",
    "flatten-nested": """
def flatten_nested(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_nested(item))
        else:
            result.append(item)
    return result
""",
    "unique-sorted": """
def unique_sorted(lst):
    return sorted(list(set(lst)))
""",
    "vowel-count": """
def vowel_count(text):
    counts = {}
    for ch in text.lower():
        if ch in "aeiou":
            counts[ch] = counts.get(ch, 0) + 1
    return counts
""",
    "max-consecutive": """
def max_consecutive(lst):
    if not lst:
        return 0
    max_c = cur_c = 1
    for i in range(1, len(lst)):
        if lst[i] == lst[i - 1]:
            cur_c += 1
            if cur_c > max_c:
                max_c = cur_c
        else:
            cur_c = 1
    return max_c
""",
    "sum-of-digits": """
def sum_of_digits(n):
    return sum(int(d) for d in str(abs(n)))
""",
    "is-palindrome-list": """
def is_palindrome_list(lst):
    return lst == lst[::-1]
""",
}


def test_challenge_bank_counts_and_structure():
    """Verify challenge bank meets all requirements:
    - 10+ original challenges
    - 3+ difficulty levels (easy, medium, hard)
    - 4+ concepts covered
    - Each challenge has 3+ visible tests and 5+ hidden tests
    """
    assert len(CHALLENGES) >= 10, f"Expected 10+ challenges, got {len(CHALLENGES)}"
    
    difficulties = {c["difficulty"] for c in CHALLENGES}
    assert "easy" in difficulties
    assert "medium" in difficulties
    assert "hard" in difficulties
    assert len(difficulties) >= 3, f"Expected 3+ difficulty levels, got {difficulties}"
    
    all_concepts = set()
    for c in CHALLENGES:
        for concept in c["concepts"].split(","):
            all_concepts.add(concept.strip())
    assert len(all_concepts) >= 4, f"Expected 4+ concepts, got {len(all_concepts)}"

    # Check test counts for each challenge
    for c in CHALLENGES:
        visible = [t for t in c["tests"] if not t["is_hidden"]]
        hidden = [t for t in c["tests"] if t["is_hidden"]]
        assert len(visible) >= 3, f"{c['slug']} has only {len(visible)} visible tests"
        assert len(hidden) >= 5, f"{c['slug']} has only {len(hidden)} hidden tests"


@pytest.mark.parametrize("challenge", CHALLENGES, ids=lambda c: c["slug"])
def test_reference_solutions_pass_all_tests(challenge):
    """Verify that the reference solution for every challenge passes all tests (visible and hidden)."""
    slug = challenge["slug"]
    assert slug in REFERENCE_SOLUTIONS, f"Missing reference solution for {slug}"
    
    env = {}
    exec(REFERENCE_SOLUTIONS[slug], env)
    
    for t in challenge["tests"]:
        fn_name = t["function_name"]
        assert fn_name in env, f"Function {fn_name} not found in reference solution for {slug}"
        fn = env[fn_name]
        
        import ast
        try:
            args = json.loads(t["input_args"])
        except Exception:
            args = ast.literal_eval(t["input_args"])
        result = fn(*args)
        
        actual_repr = repr(result).strip()
        expected_repr = t["expected_output"].strip()
        assert actual_repr == expected_repr, (
            f"{slug} test {t['test_number']} failed: "
            f"input={args}, expected={expected_repr}, got={actual_repr}"
        )
