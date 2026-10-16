"""Complete challenge bank with 10+ original Python challenges.

Each challenge includes:
- Problem description, starter code, function signature
- Concept tags, difficulty level
- 3+ visible tests, 5+ hidden tests
- Edge cases
"""

from __future__ import annotations

CHALLENGES = [
    # ===================================================================
    # MANDATORY CHALLENGE 1: last-k-total
    # ===================================================================
    {
        "slug": "last-k-total",
        "title": "Last K Total",
        "description": (
            "Write a function `last_k_total(marks, k)` that returns the total "
            "of the last `k` marks in the list.\n\n"
            "- If `k` exceeds the list length, return the total of all marks.\n"
            "- If the list is empty or `k` is zero, return `0`.\n\n"
            "**Examples:**\n"
            "```python\n"
            "last_k_total([80, 90, 70, 60], 2)  # => 130\n"
            "last_k_total([80, 90, 70], 5)       # => 240\n"
            "last_k_total([], 3)                  # => 0\n"
            "```"
        ),
        "starter_code": "def last_k_total(marks, k):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "lists,slicing,edge-cases",
        "tests": [
            # VISIBLE (3)
            {"test_number": 1, "is_hidden": False, "function_name": "last_k_total", "input_args": "[[80, 90, 70, 60], 2]", "expected_output": "130"},
            {"test_number": 2, "is_hidden": False, "function_name": "last_k_total", "input_args": "[[80, 90, 70], 5]", "expected_output": "240"},
            {"test_number": 3, "is_hidden": False, "function_name": "last_k_total", "input_args": "[[], 3]", "expected_output": "0"},
            # HIDDEN (6)
            {"test_number": 4, "is_hidden": True, "function_name": "last_k_total", "input_args": "[[10, 20, 30, 40, 50], 0]", "expected_output": "0"},
            {"test_number": 5, "is_hidden": True, "function_name": "last_k_total", "input_args": "[[100], 1]", "expected_output": "100"},
            {"test_number": 6, "is_hidden": True, "function_name": "last_k_total", "input_args": "[[5, 10, 15], 3]", "expected_output": "30"},
            {"test_number": 7, "is_hidden": True, "function_name": "last_k_total", "input_args": "[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4]", "expected_output": "34"},
            {"test_number": 8, "is_hidden": True, "function_name": "last_k_total", "input_args": "[[-5, -10, 15], 2]", "expected_output": "5"},
            {"test_number": 9, "is_hidden": True, "function_name": "last_k_total", "input_args": "[[0, 0, 0], 2]", "expected_output": "0"},
        ],
    },
    # ===================================================================
    # MANDATORY CHALLENGE 2: count-passes
    # ===================================================================
    {
        "slug": "count-passes",
        "title": "Count Passes",
        "description": (
            "Write a function `count_passes(marks)` that counts how many "
            "marks in the list are greater than or equal to 40 (the pass mark).\n\n"
            "**Examples:**\n"
            "```python\n"
            "count_passes([55, 30, 40, 90, 10])  # => 3\n"
            "count_passes([10, 20, 30])           # => 0\n"
            "count_passes([])                     # => 0\n"
            "```"
        ),
        "starter_code": "def count_passes(marks):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "lists,iteration,comparison",
        "tests": [
            # VISIBLE (3)
            {"test_number": 1, "is_hidden": False, "function_name": "count_passes", "input_args": "[[55, 30, 40, 90, 10]]", "expected_output": "3"},
            {"test_number": 2, "is_hidden": False, "function_name": "count_passes", "input_args": "[[10, 20, 30]]", "expected_output": "0"},
            {"test_number": 3, "is_hidden": False, "function_name": "count_passes", "input_args": "[[]]", "expected_output": "0"},
            # HIDDEN (5)
            {"test_number": 4, "is_hidden": True, "function_name": "count_passes", "input_args": "[[40]]", "expected_output": "1"},
            {"test_number": 5, "is_hidden": True, "function_name": "count_passes", "input_args": "[[39]]", "expected_output": "0"},
            {"test_number": 6, "is_hidden": True, "function_name": "count_passes", "input_args": "[[100, 100, 100]]", "expected_output": "3"},
            {"test_number": 7, "is_hidden": True, "function_name": "count_passes", "input_args": "[[0, 40, 39, 41, 100]]", "expected_output": "3"},
            {"test_number": 8, "is_hidden": True, "function_name": "count_passes", "input_args": "[[40, 40, 40, 40]]", "expected_output": "4"},
        ],
    },
    # ===================================================================
    # MANDATORY CHALLENGE 3: first-n-squares
    # ===================================================================
    {
        "slug": "first-n-squares",
        "title": "First N Squares",
        "description": (
            "Write a function `first_n_squares(n)` that returns a list of the "
            "first `n` perfect squares: `[1, 4, 9, ..., n²]`.\n\n"
            "- If `n` is 0, return an empty list.\n\n"
            "**Examples:**\n"
            "```python\n"
            "first_n_squares(4)  # => [1, 4, 9, 16]\n"
            "first_n_squares(1)  # => [1]\n"
            "first_n_squares(0)  # => []\n"
            "```"
        ),
        "starter_code": "def first_n_squares(n):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "lists,math,iteration",
        "tests": [
            # VISIBLE (3)
            {"test_number": 1, "is_hidden": False, "function_name": "first_n_squares", "input_args": "[4]", "expected_output": "[1, 4, 9, 16]"},
            {"test_number": 2, "is_hidden": False, "function_name": "first_n_squares", "input_args": "[1]", "expected_output": "[1]"},
            {"test_number": 3, "is_hidden": False, "function_name": "first_n_squares", "input_args": "[0]", "expected_output": "[]"},
            # HIDDEN (5)
            {"test_number": 4, "is_hidden": True, "function_name": "first_n_squares", "input_args": "[5]", "expected_output": "[1, 4, 9, 16, 25]"},
            {"test_number": 5, "is_hidden": True, "function_name": "first_n_squares", "input_args": "[10]", "expected_output": "[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]"},
            {"test_number": 6, "is_hidden": True, "function_name": "first_n_squares", "input_args": "[2]", "expected_output": "[1, 4]"},
            {"test_number": 7, "is_hidden": True, "function_name": "first_n_squares", "input_args": "[3]", "expected_output": "[1, 4, 9]"},
            {"test_number": 8, "is_hidden": True, "function_name": "first_n_squares", "input_args": "[7]", "expected_output": "[1, 4, 9, 16, 25, 36, 49]"},
        ],
    },
    # ===================================================================
    # MANDATORY CHALLENGE 4: middle-three
    # ===================================================================
    {
        "slug": "middle-three",
        "title": "Middle Three",
        "description": (
            "Write a function `middle_three(items)` that returns the middle three "
            "items from a list.\n\n"
            "- If the list has fewer than three items, return the whole list.\n"
            "- Inputs always have odd length or fewer than three items.\n\n"
            "**Examples:**\n"
            "```python\n"
            "middle_three([1, 2, 3, 4, 5])        # => [2, 3, 4]\n"
            "middle_three([10, 20, 30, 40, 50, 60, 70])  # => [30, 40, 50]\n"
            "middle_three([5])                     # => [5]\n"
            "middle_three([])                      # => []\n"
            "```"
        ),
        "starter_code": "def middle_three(items):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "lists,slicing,edge-cases",
        "tests": [
            # VISIBLE (3)
            {"test_number": 1, "is_hidden": False, "function_name": "middle_three", "input_args": "[[1, 2, 3, 4, 5]]", "expected_output": "[2, 3, 4]"},
            {"test_number": 2, "is_hidden": False, "function_name": "middle_three", "input_args": "[[10, 20, 30, 40, 50, 60, 70]]", "expected_output": "[30, 40, 50]"},
            {"test_number": 3, "is_hidden": False, "function_name": "middle_three", "input_args": "[[5]]", "expected_output": "[5]"},
            # HIDDEN (6)
            {"test_number": 4, "is_hidden": True, "function_name": "middle_three", "input_args": "[[]]", "expected_output": "[]"},
            {"test_number": 5, "is_hidden": True, "function_name": "middle_three", "input_args": "[[1, 2]]", "expected_output": "[1, 2]"},
            {"test_number": 6, "is_hidden": True, "function_name": "middle_three", "input_args": "[[1, 2, 3]]", "expected_output": "[1, 2, 3]"},
            {"test_number": 7, "is_hidden": True, "function_name": "middle_three", "input_args": "[[1, 2, 3, 4, 5, 6, 7, 8, 9]]", "expected_output": "[4, 5, 6]"},
            {"test_number": 8, "is_hidden": True, "function_name": "middle_three", "input_args": "[['a', 'b', 'c', 'd', 'e']]", "expected_output": "['b', 'c', 'd']"},
            {"test_number": 9, "is_hidden": True, "function_name": "middle_three", "input_args": "[[10, 20, 30]]", "expected_output": "[10, 20, 30]"},
        ],
    },
    # ===================================================================
    # CHALLENGE 5: reverse-words
    # ===================================================================
    {
        "slug": "reverse-words",
        "title": "Reverse Words",
        "description": (
            "Write a function `reverse_words(sentence)` that takes a sentence and "
            "returns it with each word reversed, keeping word order.\n\n"
            "**Examples:**\n"
            "```python\n"
            "reverse_words('hello world')  # => 'olleh dlrow'\n"
            "reverse_words('Python')       # => 'nohtyP'\n"
            "reverse_words('')             # => ''\n"
            "```"
        ),
        "starter_code": "def reverse_words(sentence):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "strings,iteration,splitting",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "reverse_words", "input_args": "['hello world']", "expected_output": "'olleh dlrow'"},
            {"test_number": 2, "is_hidden": False, "function_name": "reverse_words", "input_args": "['Python']", "expected_output": "'nohtyP'"},
            {"test_number": 3, "is_hidden": False, "function_name": "reverse_words", "input_args": "['']", "expected_output": "''"},
            {"test_number": 4, "is_hidden": True, "function_name": "reverse_words", "input_args": "['a b c']", "expected_output": "'a b c'"},
            {"test_number": 5, "is_hidden": True, "function_name": "reverse_words", "input_args": "['racecar']", "expected_output": "'racecar'"},
            {"test_number": 6, "is_hidden": True, "function_name": "reverse_words", "input_args": "['one two three four']", "expected_output": "'eno owt eerht ruof'"},
            {"test_number": 7, "is_hidden": True, "function_name": "reverse_words", "input_args": "['Hi']", "expected_output": "'iH'"},
            {"test_number": 8, "is_hidden": True, "function_name": "reverse_words", "input_args": "['ab cd ef']", "expected_output": "'ba dc fe'"},
        ],
    },
    # ===================================================================
    # CHALLENGE 6: fizzbuzz-list
    # ===================================================================
    {
        "slug": "fizzbuzz-list",
        "title": "FizzBuzz List",
        "description": (
            "Write a function `fizzbuzz_list(n)` that returns a list of values from "
            "1 to `n` where:\n"
            "- Multiples of 3 and 5 → `'FizzBuzz'`\n"
            "- Multiples of 3 only → `'Fizz'`\n"
            "- Multiples of 5 only → `'Buzz'`\n"
            "- Otherwise → the integer itself\n\n"
            "Return an empty list if `n` is 0.\n\n"
            "**Examples:**\n"
            "```python\n"
            "fizzbuzz_list(5)   # => [1, 2, 'Fizz', 4, 'Buzz']\n"
            "fizzbuzz_list(15)  # last element is 'FizzBuzz'\n"
            "```"
        ),
        "starter_code": "def fizzbuzz_list(n):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "iteration,conditionals,math",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "fizzbuzz_list", "input_args": "[5]", "expected_output": "[1, 2, 'Fizz', 4, 'Buzz']"},
            {"test_number": 2, "is_hidden": False, "function_name": "fizzbuzz_list", "input_args": "[0]", "expected_output": "[]"},
            {"test_number": 3, "is_hidden": False, "function_name": "fizzbuzz_list", "input_args": "[3]", "expected_output": "[1, 2, 'Fizz']"},
            {"test_number": 4, "is_hidden": True, "function_name": "fizzbuzz_list", "input_args": "[1]", "expected_output": "[1]"},
            {"test_number": 5, "is_hidden": True, "function_name": "fizzbuzz_list", "input_args": "[15]", "expected_output": "[1, 2, 'Fizz', 4, 'Buzz', 'Fizz', 7, 8, 'Fizz', 'Buzz', 11, 'Fizz', 13, 14, 'FizzBuzz']"},
            {"test_number": 6, "is_hidden": True, "function_name": "fizzbuzz_list", "input_args": "[10]", "expected_output": "[1, 2, 'Fizz', 4, 'Buzz', 'Fizz', 7, 8, 'Fizz', 'Buzz']"},
            {"test_number": 7, "is_hidden": True, "function_name": "fizzbuzz_list", "input_args": "[30]", "expected_output": "[1, 2, 'Fizz', 4, 'Buzz', 'Fizz', 7, 8, 'Fizz', 'Buzz', 11, 'Fizz', 13, 14, 'FizzBuzz', 16, 17, 'Fizz', 19, 'Buzz', 'Fizz', 22, 23, 'Fizz', 'Buzz', 26, 'Fizz', 28, 29, 'FizzBuzz']"},
            {"test_number": 8, "is_hidden": True, "function_name": "fizzbuzz_list", "input_args": "[2]", "expected_output": "[1, 2]"},
        ],
    },
    # ===================================================================
    # CHALLENGE 7: flatten-nested
    # ===================================================================
    {
        "slug": "flatten-nested",
        "title": "Flatten Nested List",
        "description": (
            "Write a function `flatten_nested(lst)` that takes a nested list and "
            "returns a flat list of all elements.\n\n"
            "The list may be nested to any depth.\n\n"
            "**Examples:**\n"
            "```python\n"
            "flatten_nested([1, [2, 3], [4, [5, 6]]])  # => [1, 2, 3, 4, 5, 6]\n"
            "flatten_nested([[1, 2], [3, 4]])            # => [1, 2, 3, 4]\n"
            "flatten_nested([])                          # => []\n"
            "```"
        ),
        "starter_code": "def flatten_nested(lst):\n    # Your code here\n    pass\n",
        "difficulty": "hard",
        "concepts": "lists,recursion,iteration",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "flatten_nested", "input_args": "[[1, [2, 3], [4, [5, 6]]]]", "expected_output": "[1, 2, 3, 4, 5, 6]"},
            {"test_number": 2, "is_hidden": False, "function_name": "flatten_nested", "input_args": "[[[1, 2], [3, 4]]]", "expected_output": "[1, 2, 3, 4]"},
            {"test_number": 3, "is_hidden": False, "function_name": "flatten_nested", "input_args": "[[]]", "expected_output": "[]"},
            {"test_number": 4, "is_hidden": True, "function_name": "flatten_nested", "input_args": "[[1, 2, 3]]", "expected_output": "[1, 2, 3]"},
            {"test_number": 5, "is_hidden": True, "function_name": "flatten_nested", "input_args": "[[[[1]]]]", "expected_output": "[1]"},
            {"test_number": 6, "is_hidden": True, "function_name": "flatten_nested", "input_args": "[[[1, [2]], [3, [4, [5]]]]]", "expected_output": "[1, 2, 3, 4, 5]"},
            {"test_number": 7, "is_hidden": True, "function_name": "flatten_nested", "input_args": "[[[], [[], [1]]]]", "expected_output": "[1]"},
            {"test_number": 8, "is_hidden": True, "function_name": "flatten_nested", "input_args": "[[1, [2, [3, [4, [5]]]]]]", "expected_output": "[1, 2, 3, 4, 5]"},
        ],
    },
    # ===================================================================
    # CHALLENGE 8: unique-sorted
    # ===================================================================
    {
        "slug": "unique-sorted",
        "title": "Unique Sorted",
        "description": (
            "Write a function `unique_sorted(lst)` that returns a new list "
            "containing only the unique elements from the input, sorted in "
            "ascending order.\n\n"
            "**Examples:**\n"
            "```python\n"
            "unique_sorted([3, 1, 2, 3, 1])  # => [1, 2, 3]\n"
            "unique_sorted([5, 5, 5])         # => [5]\n"
            "unique_sorted([])                # => []\n"
            "```"
        ),
        "starter_code": "def unique_sorted(lst):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "lists,sorting,sets",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "unique_sorted", "input_args": "[[3, 1, 2, 3, 1]]", "expected_output": "[1, 2, 3]"},
            {"test_number": 2, "is_hidden": False, "function_name": "unique_sorted", "input_args": "[[5, 5, 5]]", "expected_output": "[5]"},
            {"test_number": 3, "is_hidden": False, "function_name": "unique_sorted", "input_args": "[[]]", "expected_output": "[]"},
            {"test_number": 4, "is_hidden": True, "function_name": "unique_sorted", "input_args": "[[1]]", "expected_output": "[1]"},
            {"test_number": 5, "is_hidden": True, "function_name": "unique_sorted", "input_args": "[[10, 5, 8, 5, 10, 3]]", "expected_output": "[3, 5, 8, 10]"},
            {"test_number": 6, "is_hidden": True, "function_name": "unique_sorted", "input_args": "[[1, 2, 3, 4, 5]]", "expected_output": "[1, 2, 3, 4, 5]"},
            {"test_number": 7, "is_hidden": True, "function_name": "unique_sorted", "input_args": "[[-3, -1, -2, -3]]", "expected_output": "[-3, -2, -1]"},
            {"test_number": 8, "is_hidden": True, "function_name": "unique_sorted", "input_args": "[[0, 0, 0, 0]]", "expected_output": "[0]"},
        ],
    },
    # ===================================================================
    # CHALLENGE 9: vowel-count
    # ===================================================================
    {
        "slug": "vowel-count",
        "title": "Vowel Count",
        "description": (
            "Write a function `vowel_count(text)` that returns a dictionary "
            "mapping each vowel (a, e, i, o, u) to the number of times it "
            "appears in the text. Only include vowels that appear at least once. "
            "Treat uppercase and lowercase the same.\n\n"
            "**Examples:**\n"
            "```python\n"
            "vowel_count('hello')       # => {'e': 1, 'o': 1}\n"
            "vowel_count('AEIOU')       # => {'a': 1, 'e': 1, 'i': 1, 'o': 1, 'u': 1}\n"
            "vowel_count('xyz')         # => {}\n"
            "```"
        ),
        "starter_code": "def vowel_count(text):\n    # Your code here\n    pass\n",
        "difficulty": "medium",
        "concepts": "strings,dictionaries,iteration",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "vowel_count", "input_args": "['hello']", "expected_output": "{'e': 1, 'o': 1}"},
            {"test_number": 2, "is_hidden": False, "function_name": "vowel_count", "input_args": "['AEIOU']", "expected_output": "{'a': 1, 'e': 1, 'i': 1, 'o': 1, 'u': 1}"},
            {"test_number": 3, "is_hidden": False, "function_name": "vowel_count", "input_args": "['xyz']", "expected_output": "{}"},
            {"test_number": 4, "is_hidden": True, "function_name": "vowel_count", "input_args": "['']", "expected_output": "{}"},
            {"test_number": 5, "is_hidden": True, "function_name": "vowel_count", "input_args": "['aaa']", "expected_output": "{'a': 3}"},
            {"test_number": 6, "is_hidden": True, "function_name": "vowel_count", "input_args": "['Hello World']", "expected_output": "{'e': 1, 'o': 2}"},
            {"test_number": 7, "is_hidden": True, "function_name": "vowel_count", "input_args": "['Python Programming']", "expected_output": "{'o': 2, 'a': 1, 'i': 1}"},
            {"test_number": 8, "is_hidden": True, "function_name": "vowel_count", "input_args": "['bcdfg']", "expected_output": "{}"},
        ],
    },
    # ===================================================================
    # CHALLENGE 10: max-consecutive
    # ===================================================================
    {
        "slug": "max-consecutive",
        "title": "Max Consecutive",
        "description": (
            "Write a function `max_consecutive(lst)` that returns the length "
            "of the longest run of consecutive equal elements in the list.\n\n"
            "Return `0` for an empty list.\n\n"
            "**Examples:**\n"
            "```python\n"
            "max_consecutive([1, 1, 2, 2, 2, 3])  # => 3\n"
            "max_consecutive([5])                   # => 1\n"
            "max_consecutive([])                    # => 0\n"
            "```"
        ),
        "starter_code": "def max_consecutive(lst):\n    # Your code here\n    pass\n",
        "difficulty": "medium",
        "concepts": "lists,iteration,tracking-state",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "max_consecutive", "input_args": "[[1, 1, 2, 2, 2, 3]]", "expected_output": "3"},
            {"test_number": 2, "is_hidden": False, "function_name": "max_consecutive", "input_args": "[[5]]", "expected_output": "1"},
            {"test_number": 3, "is_hidden": False, "function_name": "max_consecutive", "input_args": "[[]]", "expected_output": "0"},
            {"test_number": 4, "is_hidden": True, "function_name": "max_consecutive", "input_args": "[[1, 2, 3, 4]]", "expected_output": "1"},
            {"test_number": 5, "is_hidden": True, "function_name": "max_consecutive", "input_args": "[[7, 7, 7, 7, 7]]", "expected_output": "5"},
            {"test_number": 6, "is_hidden": True, "function_name": "max_consecutive", "input_args": "[[1, 1, 2, 2, 3, 3, 3, 3]]", "expected_output": "4"},
            {"test_number": 7, "is_hidden": True, "function_name": "max_consecutive", "input_args": "[['a', 'a', 'b', 'a', 'a', 'a']]", "expected_output": "3"},
            {"test_number": 8, "is_hidden": True, "function_name": "max_consecutive", "input_args": "[[1, 2, 1, 2, 1]]", "expected_output": "1"},
        ],
    },
    # ===================================================================
    # CHALLENGE 11 (bonus): sum-of-digits
    # ===================================================================
    {
        "slug": "sum-of-digits",
        "title": "Sum of Digits",
        "description": (
            "Write a function `sum_of_digits(n)` that returns the sum of all "
            "digits of the absolute value of `n`.\n\n"
            "**Examples:**\n"
            "```python\n"
            "sum_of_digits(123)   # => 6\n"
            "sum_of_digits(-456)  # => 15\n"
            "sum_of_digits(0)     # => 0\n"
            "```"
        ),
        "starter_code": "def sum_of_digits(n):\n    # Your code here\n    pass\n",
        "difficulty": "easy",
        "concepts": "math,strings,iteration",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "sum_of_digits", "input_args": "[123]", "expected_output": "6"},
            {"test_number": 2, "is_hidden": False, "function_name": "sum_of_digits", "input_args": "[-456]", "expected_output": "15"},
            {"test_number": 3, "is_hidden": False, "function_name": "sum_of_digits", "input_args": "[0]", "expected_output": "0"},
            {"test_number": 4, "is_hidden": True, "function_name": "sum_of_digits", "input_args": "[9]", "expected_output": "9"},
            {"test_number": 5, "is_hidden": True, "function_name": "sum_of_digits", "input_args": "[999]", "expected_output": "27"},
            {"test_number": 6, "is_hidden": True, "function_name": "sum_of_digits", "input_args": "[10]", "expected_output": "1"},
            {"test_number": 7, "is_hidden": True, "function_name": "sum_of_digits", "input_args": "[-100]", "expected_output": "1"},
            {"test_number": 8, "is_hidden": True, "function_name": "sum_of_digits", "input_args": "[12345]", "expected_output": "15"},
        ],
    },
    # ===================================================================
    # CHALLENGE 12 (bonus): is-palindrome-list
    # ===================================================================
    {
        "slug": "is-palindrome-list",
        "title": "Is Palindrome List",
        "description": (
            "Write a function `is_palindrome_list(lst)` that returns `True` if "
            "the list reads the same forwards and backwards, `False` otherwise.\n\n"
            "An empty list is a palindrome.\n\n"
            "**Examples:**\n"
            "```python\n"
            "is_palindrome_list([1, 2, 3, 2, 1])  # => True\n"
            "is_palindrome_list([1, 2, 3])         # => False\n"
            "is_palindrome_list([])                # => True\n"
            "```"
        ),
        "starter_code": "def is_palindrome_list(lst):\n    # Your code here\n    pass\n",
        "difficulty": "medium",
        "concepts": "lists,comparison,edge-cases",
        "tests": [
            {"test_number": 1, "is_hidden": False, "function_name": "is_palindrome_list", "input_args": "[[1, 2, 3, 2, 1]]", "expected_output": "True"},
            {"test_number": 2, "is_hidden": False, "function_name": "is_palindrome_list", "input_args": "[[1, 2, 3]]", "expected_output": "False"},
            {"test_number": 3, "is_hidden": False, "function_name": "is_palindrome_list", "input_args": "[[]]", "expected_output": "True"},
            {"test_number": 4, "is_hidden": True, "function_name": "is_palindrome_list", "input_args": "[[1]]", "expected_output": "True"},
            {"test_number": 5, "is_hidden": True, "function_name": "is_palindrome_list", "input_args": "[[1, 1]]", "expected_output": "True"},
            {"test_number": 6, "is_hidden": True, "function_name": "is_palindrome_list", "input_args": "[[1, 2]]", "expected_output": "False"},
            {"test_number": 7, "is_hidden": True, "function_name": "is_palindrome_list", "input_args": "[['a', 'b', 'a']]", "expected_output": "True"},
            {"test_number": 8, "is_hidden": True, "function_name": "is_palindrome_list", "input_args": "[[1, 2, 2, 1]]", "expected_output": "True"},
        ],
    },
]
