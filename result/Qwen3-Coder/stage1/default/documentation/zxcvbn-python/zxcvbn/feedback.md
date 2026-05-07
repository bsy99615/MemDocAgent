# `feedback.py`

## `zxcvbn.feedback.get_feedback` · *function*

## Summary:
Generates user feedback for password strength based on match analysis and score.

## Description:
This function analyzes a sequence of password matches and provides tailored feedback to help users create stronger passwords. It serves as the main feedback generator in the zxcvbn password strength estimation system, determining appropriate warnings and suggestions based on the strength score and match patterns identified in the password.

The function determines feedback based on:
1. Empty sequence (returns basic feedback)
2. High strength score (>2) (returns empty feedback)
3. Low strength score (analyzes longest match and provides specific feedback)

## Args:
    score (int): Numeric strength score (typically 0-4) indicating password strength
    sequence (list): List of match objects, each expected to have a 'token' key

## Returns:
    dict: Dictionary containing 'warning' and 'suggestions' keys with feedback information

## Raises:
    None explicitly raised in this function

## Constraints:
    Preconditions:
    - score should be a numeric value representing password strength
    - sequence should be iterable (list-like structure)
    - Each item in sequence should be a dictionary-like object with a 'token' key
    
    Postconditions:
    - Returns a dictionary with 'warning' and 'suggestions' keys
    - 'warning' is always a string
    - 'suggestions' is always a list of strings

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_feedback] --> B{len(sequence) == 0}
    B -- True --> C[Return basic feedback]
    B -- False --> D{score > 2}
    D -- True --> E[Return empty feedback]
    D -- False --> F[Find longest match]
    F --> G[Call get_match_feedback]
    G --> H{get_match_feedback result}
    H -- Truthy --> I[Insert extra feedback at start]
    H -- Falsy --> J[Create new feedback with extra feedback]
    I --> K[Return feedback]
    J --> K
```

## Examples:
    # Basic usage with weak password
    feedback = get_feedback(0, [{'token': 'password', 'pattern': 'dictionary'}])
    # Returns: {'warning': '', 'suggestions': ['Add another word or two. Uncommon words are better.']}

    # Usage with strong password
    feedback = get_feedback(3, [{'token': 'mypassword', 'pattern': 'dictionary'}])
    # Returns: {'warning': '', 'suggestions': []}
```

## `zxcvbn.feedback.get_match_feedback` · *function*

## Summary:
Generates user-friendly feedback for password strength matches based on pattern type, providing warnings and suggestions to improve password security.

## Description:
This function serves as a feedback dispatcher that generates appropriate warnings and suggestions for different types of password patterns identified by the zxcvbn strength analyzer. It handles various pattern types including dictionary words, spatial keyboard patterns, repeated characters, sequences, regex matches, and date patterns.

The logic is extracted into its own function to separate feedback generation concerns from the core matching algorithm, enabling easier maintenance, testing, and localization of feedback messages without affecting the underlying pattern matching logic.

## Args:
    match (dict): A dictionary containing match information with keys including:
        - 'pattern' (str): The type of pattern matched (e.g., 'dictionary', 'spatial', 'repeat')
        - Other pattern-specific keys depending on the pattern type
    is_sole_match (bool): Indicates whether this match is the only match found in the password

## Returns:
    dict or None: A dictionary containing 'warning' and 'suggestions' keys, or None if no specific feedback is generated for the pattern type. The returned dictionary has:
        - 'warning' (str): Human-readable warning message about the match
        - 'suggestions' (list[str]): List of suggestion messages for improving password strength

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - match must be a dictionary with at least a 'pattern' key
        - is_sole_match must be a boolean value
    
    Postconditions:
        - When a match pattern is handled, returns a dictionary with 'warning' and 'suggestions' keys
        - When a match pattern is not handled, returns None (implicit)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_match_feedback] --> B{match['pattern'] == 'dictionary'?}
    B -- Yes --> C[Call get_dictionary_match_feedback]
    B -- No --> D{match['pattern'] == 'spatial'?}
    D -- Yes --> E{match['turns'] == 1?}
    E -- Yes --> F[warning = straight rows]
    E -- No --> G[warning = short keyboard patterns]
    D -- No --> H{match['pattern'] == 'repeat'?}
    H -- Yes --> I{len(match['base_token']) == 1?}
    I -- Yes --> J[warning = repeats like "aaa"]
    I -- No --> K[warning = repeats like "abcabcabc"]
    H -- No --> L{match['pattern'] == 'sequence'?}
    L -- Yes --> M[warning = sequences like "abc"]
    L -- No --> N{match['pattern'] == 'regex'?}
    N -- Yes --> O{match['regex_name'] == 'recent_year'?}
    O -- Yes --> P[warning = recent years]
    N -- No --> Q{match['pattern'] == 'date'?}
    Q -- Yes --> R[warning = dates are easy to guess]
    Q -- No --> S[Return None]
    C --> T[Return feedback]
    F --> T
    G --> T
    J --> T
    K --> T
    M --> T
    P --> T
    R --> T
```

## Examples:
    Example 1 - Spatial pattern feedback:
    ```python
    match = {'pattern': 'spatial', 'turns': 1}
    result = get_match_feedback(match, False)
    # Returns {'warning': 'Straight rows of keys are easy to guess.', 'suggestions': ['Use a longer keyboard pattern with more turns.']}
    ```

    Example 2 - Repeat pattern feedback:
    ```python
    match = {'pattern': 'repeat', 'base_token': 'aaa'}
    result = get_match_feedback(match, True)
    # Returns {'warning': 'Repeats like "aaa" are easy to guess.', 'suggestions': ['Avoid repeated words and characters.']}
    ```

    Example 3 - Sequence pattern feedback:
    ```python
    match = {'pattern': 'sequence'}
    result = get_match_feedback(match, False)
    # Returns {'warning': 'Sequences like "abc" or "6543" are easy to guess.', 'suggestions': ['Avoid sequences.']}
    ```

## `zxcvbn.feedback.get_dictionary_match_feedback` · *function*

## Summary:
Generates user-friendly feedback for dictionary-based password matches, providing warnings about common patterns and suggestions for improvement.

## Description:
This function analyzes a dictionary match from the zxcvbn password strength estimator and produces human-readable feedback including warnings about the strength of the matched word and suggestions for making passwords more secure. It's designed to be called during password strength analysis to provide actionable feedback to users.

The logic is extracted into its own function to separate the feedback generation concern from the core matching algorithm, allowing for easier maintenance and testing of feedback messages independently from the matching logic.

## Args:
    match (dict): A dictionary containing match information with keys including:
        - 'dictionary_name' (str): Name of the dictionary used for matching
        - 'rank' (int): Rank of the password in the common password list (if applicable)
        - 'guesses_log10' (float): Log10 of the number of guesses needed to crack
        - 'reversed' (bool): Whether the token was reversed
        - 'l33t' (bool): Whether l33t substitutions were used
        - 'token' (str): The matched token
    is_sole_match (bool): Indicates whether this match is the only match found in the password

## Returns:
    dict: A dictionary containing:
        - 'warning' (str): A human-readable warning message about the match, or empty string if no warning applies
        - 'suggestions' (list[str]): A list of suggestion messages for improving password strength

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - match must be a dictionary with required keys ('dictionary_name', 'token')
        - match may contain optional keys ('rank', 'guesses_log10', 'reversed', 'l33t')
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
    D -- Yes --> E[warning = top-10 common]
    D -- No --> F{rank <= 100?}
    F -- Yes --> G[warning = top-100 common]
    F -- No --> H[warning = very common]
    C -- No --> I{guesses_log10 <= 4?}
    I -- Yes --> J[warning = similar to common]
    I -- No --> K[warning = '' (empty)]
    B -- No --> L{dictionary_name == 'english'?}
    L -- Yes --> M{is_sole_match?}
    M -- Yes --> N[warning = word by itself]
    M -- No --> O[warning = '' (empty)]
    L -- No --> P{dictionary_name in [surnames,male_names,female_names]?}
    P -- Yes --> Q{is_sole_match?}
    Q -- Yes --> R[warning = names/surnames alone]
    Q -- No --> S[warning = common names/surnames]
    P -- No --> T[warning = '' (empty)]
    U[Generate suggestions] --> V[Return warning + suggestions]
```

## Examples:
    Example 1 - Common password:
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
    # Returns {'warning': 'This is a top-10 common password.', 'suggestions': []}
    ```

    Example 2 - Capitalization suggestion:
    ```python
    match = {
        'dictionary_name': 'english',
        'token': 'Password',
        'reversed': False,
        'l33t': False
    }
    result = get_dictionary_match_feedback(match, False)
    # Returns {'warning': '', 'suggestions': ["Capitalization doesn't help very much."]}
    ```

