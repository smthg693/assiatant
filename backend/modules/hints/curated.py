"""Curated hint ladders for all challenges.

Each challenge has 3+ ordered hints that progressively guide the learner
toward the solution without ever revealing it.

Hint levels:
1. Conceptual nudge — points toward the concept area
2. Debugging direction — points toward where the bug might be
3. Specific guidance — more targeted but still incomplete
"""

from __future__ import annotations

# Maps challenge_slug → list of ordered hints
CURATED_HINTS: dict[str, list[str]] = {
    # ---------------------------------------------------------------
    # MANDATORY CHALLENGE 1: last-k-total
    # ---------------------------------------------------------------
    "last-k-total": [
        "Think about how Python list slicing works with negative indices. "
        "What happens when you slice from the end of a list?",
        
        "Consider the edge cases: What should happen when k is 0? "
        "What about when k is larger than the list? Try tracing through "
        "your logic with these inputs by hand.",
        
        "Python's slice `marks[-k:]` gives you the last k elements — but "
        "be careful: `marks[-0:]` returns the entire list, not an empty list. "
        "You may need to handle k=0 as a special case before slicing.",
    ],
    
    # ---------------------------------------------------------------
    # MANDATORY CHALLENGE 2: count-passes
    # ---------------------------------------------------------------
    "count-passes": [
        "You need to count how many items meet a condition. Think about "
        "what comparison operator to use for 'greater than or equal to'.",
        
        "Make sure you're using `>=` rather than `>` for the pass mark "
        "boundary. A mark of exactly 40 should be counted as passing.",
        
        "A clean approach: use a loop with a counter, or a list comprehension "
        "with `len()`. Don't forget that `>=` includes the boundary value.",
    ],
    
    # ---------------------------------------------------------------
    # MANDATORY CHALLENGE 3: first-n-squares
    # ---------------------------------------------------------------
    "first-n-squares": [
        "The sequence is 1², 2², 3², ..., n². Think about what range of "
        "numbers you need to iterate over.",
        
        "Remember, the squares start from 1 (not 0). So you need `range(1, n+1)` "
        "rather than `range(n)`. Also consider what to return when n is 0.",
        
        "Use a list comprehension like `[i**2 for i in range(1, n+1)]` as "
        "your pattern. Make sure this naturally returns `[]` when n is 0.",
    ],
    
    # ---------------------------------------------------------------
    # MANDATORY CHALLENGE 4: middle-three
    # ---------------------------------------------------------------
    "middle-three": [
        "To find the middle three items, you need to figure out where the "
        "middle of the list is. Think about integer division to find the "
        "center index.",
        
        "The center of a list of length L is at index `L // 2`. From there, "
        "you want 3 elements spanning the center. But don't forget to handle "
        "lists with fewer than 3 items.",
        
        "For a list of length L, the middle three start at index `L//2 - 1` "
        "and end at `L//2 + 2`. If `len(items) < 3`, just return the whole list. "
        "Trace through [1,2,3,4,5] to verify: center is index 2, so slice [1:4].",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 5: reverse-words
    # ---------------------------------------------------------------
    "reverse-words": [
        "Start by splitting the sentence into individual words. Then think "
        "about how to reverse each word separately.",
        
        "Python's `split()` divides a string by spaces. String slicing with "
        "`[::-1]` reverses a string. How can you combine these two ideas?",
        
        "Split the sentence, reverse each word with `word[::-1]`, then join "
        "them back with `' '.join(...)`. Consider what happens with an empty string.",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 6: fizzbuzz-list
    # ---------------------------------------------------------------
    "fizzbuzz-list": [
        "The order of your conditions matters! Think about which check "
        "needs to come first: divisible by 3, by 5, or by both?",
        
        "Check 'divisible by both 3 and 5' FIRST, because if you check "
        "'divisible by 3' first, numbers like 15 will match that and never "
        "reach the 'both' check.",
        
        "Build a result list. For each i from 1 to n: if i%15==0 → 'FizzBuzz', "
        "elif i%3==0 → 'Fizz', elif i%5==0 → 'Buzz', else → i (the integer).",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 7: flatten-nested
    # ---------------------------------------------------------------
    "flatten-nested": [
        "This is a natural fit for recursion. Think about the base case: "
        "what happens when an element is NOT a list?",
        
        "For each element: if it's a list, recursively flatten it and extend "
        "your result. If it's not a list, just append it. How do you check "
        "if something is a list?",
        
        "Use `isinstance(item, list)` to check if an element is a list. "
        "Recursively process sublists and collect non-list elements into a flat result.",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 8: unique-sorted
    # ---------------------------------------------------------------
    "unique-sorted": [
        "Python has a built-in data structure that automatically removes "
        "duplicates. Then you need to put the remaining items in order.",
        
        "A `set` removes duplicates, and `sorted()` puts items in ascending "
        "order. Think about how to combine these two operations.",
        
        "The simplest approach is `sorted(set(lst))`. Make sure the original "
        "list isn't modified — `set()` and `sorted()` create new collections.",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 9: vowel-count
    # ---------------------------------------------------------------
    "vowel-count": [
        "You need to iterate through each character, check if it's a vowel, "
        "and count occurrences. Remember to handle both uppercase and lowercase.",
        
        "Convert each character to lowercase before checking. Use a dictionary "
        "to keep track of counts. Only include vowels that appear at least once.",
        
        "Loop through the text, convert to lower with `.lower()`, check if the "
        "character is in 'aeiou', and update a count dictionary. Don't include "
        "vowels with zero count in your result.",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 10: max-consecutive
    # ---------------------------------------------------------------
    "max-consecutive": [
        "You need to track the length of the current run of equal elements "
        "and remember the longest run you've seen so far.",
        
        "Walk through the list. If the current element equals the previous one, "
        "increment your current count. Otherwise, reset it to 1. Update the "
        "maximum after each step.",
        
        "Initialize `max_run = 0` and `current_run = 0`. For each element: "
        "if it equals the previous, `current_run += 1`, else `current_run = 1`. "
        "Update `max_run = max(max_run, current_run)`. Handle empty list by returning 0.",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 11: sum-of-digits
    # ---------------------------------------------------------------
    "sum-of-digits": [
        "You need to work with individual digits. Think about how to break "
        "a number into its digits. Don't forget about negative numbers.",
        
        "Use `abs()` to handle negative numbers first. Then you can either "
        "convert to a string and sum the digits, or use modulo/division.",
        
        "Convert to string: `sum(int(d) for d in str(abs(n)))`. Or use math: "
        "repeatedly take `n % 10` to get the last digit and `n // 10` to remove it.",
    ],
    
    # ---------------------------------------------------------------
    # CHALLENGE 12: is-palindrome-list
    # ---------------------------------------------------------------
    "is-palindrome-list": [
        "A palindrome reads the same forwards and backwards. Think about "
        "how to compare the list with its reverse.",
        
        "Python lets you reverse a list with `lst[::-1]`. Compare the original "
        "with the reversed version. What about empty lists?",
        
        "The simplest check is `lst == lst[::-1]`. This works for empty lists too "
        "(both sides are `[]`). Make sure you're returning True/False, not the list itself.",
    ],
}


def get_curated_hint(challenge_slug: str, level: int) -> str | None:
    """Get a curated hint for a challenge at a specific level.
    
    Args:
        challenge_slug: The challenge slug identifier
        level: 1-indexed hint level
    
    Returns:
        The hint text, or None if no curated hint exists at that level
    """
    hints = CURATED_HINTS.get(challenge_slug, [])
    if 1 <= level <= len(hints):
        return hints[level - 1]
    return None


def get_max_curated_level(challenge_slug: str) -> int:
    """Get the maximum hint level available for a challenge."""
    return len(CURATED_HINTS.get(challenge_slug, []))
