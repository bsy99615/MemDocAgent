# `feedback.py`

## `zxcvbn.feedback.get_feedback` · *function*

## Summary:
Generates user-friendly feedback for password strength based on match analysis and score evaluation.

## Description:
Analyzes password matching sequences to provide targeted feedback for improving password strength. This function serves as the main interface for generating user-facing feedback messages that guide users toward creating stronger passwords. It determines appropriate warnings and suggestions based on the weakest match in the password analysis and the overall strength score.

The function is designed to be called after password analysis is complete, providing structured feedback to help users understand weaknesses in their passwords and how to improve them.

## Args:
    score (int): Numeric password strength score (typically 0-4) where higher values indicate stronger passwords
    sequence (list[dict]): List of match dictionaries identifying patterns found in the password, each containing pattern information including 'token' key for length comparison

## Returns:
    dict: Feedback dictionary with 'warning' (str) and 'suggestions' (list[str]) keys containing user guidance messages. The structure is always consistent with these two keys present.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - score must be a numeric value
        - sequence must be a list of dictionaries with match information
        - Each match dictionary must contain at least a 'token' key for length comparison
    
    Postconditions:
        - Returned dictionary always contains 'warning' and 'suggestions' keys
        - When score > 2, returns empty suggestions list
        - When sequence is empty, returns default suggestions about using words
        - When get_match_feedback returns None, provides fallback feedback

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_feedback] --> B{len(sequence) == 0?}
    B -- Yes --> C[Return default feedback with 2 suggestions]
    B -- No --> D{score > 2?}
    D -- Yes --> E[Return empty suggestions]
    D -- No --> F[Find longest match in sequence]
    F --> G[Call get_match_feedback(longest_match, len(sequence) == 1)]
    G --> H{get_match_feedback returns None?}
    H -- Yes --> I[Create feedback with extra suggestion]
    H -- No --> J[Insert extra suggestion at beginning of suggestions]
    J --> K{warning field empty?}
    K -- Yes --> L[Set warning to empty string]
    K -- No --> L
    L --> M[Return feedback]
    I --> M
```

## Examples:
    Example 1 - Strong password feedback:
    ```python
    score = 3
    sequence = [{'token': 'password'}, {'token': '123'}]
    result = get_feedback(score, sequence)
    # Returns: {'warning': '', 'suggestions': []}
    ```

    Example 2 - Weak password with multiple matches:
    ```python
    score = 1
    sequence = [{'token': 'abc'}, {'token': 'password123'}]
    result = get_feedback(score, sequence)
    # Returns: Feedback based on longest match ('password123') plus extra suggestion
    ```

    Example 3 - Empty sequence (no matches found):
    ```python
    score = 0
    sequence = []
    result = get_feedback(score, sequence)
    # Returns: {'warning': '', 'suggestions': ['Use a few words, avoid common phrases.', 'No need for symbols, digits, or uppercase letters.']}
    ```

## `zxcvbn.feedback.get_match_feedback` · *function*

## Summary:
Generates user-friendly feedback for password strength matches based on pattern type, providing warnings and suggestions to improve password security.

## Description:
This function analyzes different password matching patterns identified by the zxcvbn algorithm and generates appropriate feedback messages. It serves as a centralized feedback generator that routes to specific handlers based on match patterns. The function distinguishes between various weak password patterns such as dictionary words, spatial keyboard patterns, repeated characters, sequences, regex matches, and date patterns, providing tailored warnings and improvement suggestions for each.

## Args:
    match (dict): Dictionary containing match information with keys including:
        - 'pattern' (str): Type of pattern matched (e.g., 'dictionary', 'spatial', 'repeat', 'sequence', 'regex', 'date')
        - Additional pattern-specific keys depending on the pattern type (e.g., 'turns' for spatial patterns, 'base_token' for repeat patterns, 'regex_name' for regex patterns)
    is_sole_match (bool): Flag indicating if this is the only match in the password

## Returns:
    dict or None: A dictionary containing:
        - 'warning' (str): Warning message about the match weakness
        - 'suggestions' (list[str]): List of suggestions for improving password strength
    Returns None when no specific feedback is available for the pattern type (when the pattern is not one of the handled types or when a conditional branch doesn't return a value)

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - match must be a dictionary with at least a 'pattern' key
        - match must contain pattern-specific keys required for processing
        - is_sole_match must be a boolean value
    
    Postconditions:
        - When returning a dictionary, it always contains 'warning' and 'suggestions' keys
        - When returning None, no feedback is available for that pattern type

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_match_feedback] --> B{match['pattern'] == 'dictionary'?}
    B -- Yes --> C[Call get_dictionary_match_feedback]
    B -- No --> D{match['pattern'] == 'spatial'?}
    D -- Yes --> E{match['turns'] == 1?}
    E -- Yes --> F[warning = Straight rows of keys]
    E -- No --> G[warning = Short keyboard patterns]
    D -- No --> H{match['pattern'] == 'repeat'?}
    H -- Yes --> I{len(match['base_token']) == 1?}
    I -- Yes --> J[warning = Repeats like "aaa"]
    I -- No --> K[warning = Repeats like "abcabcabc"]
    H -- No --> L{match['pattern'] == 'sequence'?}
    L -- Yes --> M[warning = Sequences like "abc"]
    L -- No --> N{match['pattern'] == 'regex'?}
    N -- Yes --> O{match['regex_name'] == 'recent_year'?}
    O -- Yes --> P[warning = Recent years are easy to guess]
    O -- No --> Q[Implicitly return None]
    N -- No --> Q[Implicitly return None]
    Q --> R{match['pattern'] == 'date'?}
    R -- Yes --> S[warning = Dates are often easy to guess]
    R -- No --> T[Implicitly return None]
    U[Return result or None]
```

## Examples:
    Example 1 - Spatial pattern feedback (single turn):
    ```python
    match = {'pattern': 'spatial', 'turns': 1}
    result = get_match_feedback(match, False)
    # Returns: {'warning': 'Straight rows of keys are easy to guess.', 'suggestions': ['Use a longer keyboard pattern with more turns.']}
    ```

    Example 2 - Repeat pattern feedback (single character repeat):
    ```python
    match = {'pattern': 'repeat', 'base_token': 'aaa'}
    result = get_match_feedback(match, False)
    # Returns: {'warning': 'Repeats like "aaa" are easy to guess.', 'suggestions': ['Avoid repeated words and characters.']}
    ```

    Example 3 - Sequence pattern feedback:
    ```python
    match = {'pattern': 'sequence'}
    result = get_match_feedback(match, False)
    # Returns: {'warning': 'Sequences like "abc" or "6543" are easy to guess.', 'suggestions': ['Avoid sequences.']}
    ```

    Example 4 - Regex pattern feedback (recent year):
    ```python
    match = {'pattern': 'regex', 'regex_name': 'recent_year'}
    result = get_match_feedback(match, False)
    # Returns: {'warning': "Recent years are easy to guess.", 'suggestions': ['Avoid recent years.', 'Avoid years that are associated with you.']}
    ```

    Example 5 - Unhandled pattern (returns None):
    ```python
    match = {'pattern': 'other_pattern'}
    result = get_match_feedback(match, False)
    # Returns: None
    ```

## `zxcvbn.feedback.get_dictionary_match_feedback` · *function*

## Summary:
Generates user-friendly feedback for dictionary-based password matches, providing warnings about common patterns and suggestions for improvement.

## Description:
This function analyzes dictionary match results from the zxcvbn password strength estimator to generate human-readable feedback. It provides specific warnings about the strength of dictionary-based matches and offers actionable suggestions to improve password security. The function distinguishes between different types of dictionary matches (passwords, English words, names) and applies different feedback rules based on match characteristics such as rank, sole match status, and pattern modifications.

## Args:
    match (dict): Dictionary containing match information with keys including:
        - 'dictionary_name' (str): Name of the dictionary used for matching
        - 'rank' (int): Rank of the matched word in the dictionary (for passwords)
        - 'guesses_log10' (float): Log10 of the number of guesses needed to crack
        - 'reversed' (bool): Whether the token was reversed
        - 'l33t' (bool): Whether l33t substitutions were used
        - 'token' (str): The matched token
    is_sole_match (bool): Flag indicating if this is the only match in the password

## Returns:
    dict: A dictionary containing:
        - 'warning' (str): Warning message about the match strength, or empty string
        - 'suggestions' (list[str]): List of suggestions for improving password strength

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - match must be a dictionary with required keys ('dictionary_name', 'token')
        - match must contain optional keys ('rank', 'guesses_log10', 'reversed', 'l33t') if referenced
        - is_sole_match must be a boolean value
    
    Postconditions:
        - Returned dictionary always contains 'warning' and 'suggestions' keys
        - 'warning' is always a string (empty if no warning)
        - 'suggestions' is always a list of strings

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_dictionary_match_feedback] --> B{dictionary_name == 'passwords'?}
    B -- Yes --> C{is_sole_match AND NOT l33t AND NOT reversed?}
    C -- Yes --> D{rank <= 10?}
    D -- Yes --> E[warning = top-10 common password]
    D -- No --> F{rank <= 100?}
    F -- Yes --> G[warning = top-100 common password]
    F -- No --> H[warning = very common password]
    C -- No --> I{guesses_log10 <= 4?}
    I -- Yes --> J[warning = similar to commonly used password]
    I -- No --> K[warning = '' (empty)]
    B -- No --> L{dictionary_name == 'english'?}
    L -- Yes --> M{is_sole_match?}
    M -- Yes --> N[warning = word by itself is easy to guess]
    M -- No --> O[warning = '' (empty)]
    L -- No --> P{dictionary_name in [surnames,male_names,female_names]?}
    P -- Yes --> Q{is_sole_match?}
    Q -- Yes --> R[warning = names/surnames by themselves are easy to guess]
    Q -- No --> S[warning = common names/surnames are easy to guess]
    P -- No --> T[warning = '' (empty)]
    U[Generate suggestions] --> V[Return warning and suggestions]
```

## Examples:
    Example 1 - Common password match:
    ```python
    match = {
        'dictionary_name': 'passwords',
        'rank': 5,
        'guesses_log10': 6,
        'reversed': False,
        'l33t': False,
        'token': 'password'
    }
    result = get_dictionary_match_feedback(match, True)
    # Returns: {'warning': 'This is a top-10 common password.', 'suggestions': []}
    ```

    Example 2 - Capitalization suggestion:
    ```python
    match = {
        'dictionary_name': 'english',
        'rank': 1000,
        'guesses_log10': 8,
        'reversed': False,
        'l33t': False,
        'token': 'Password'
    }
    result = get_dictionary_match_feedback(match, False)
    # Returns: {'warning': '', 'suggestions': ["Capitalization doesn't help very much."]}
    ```

