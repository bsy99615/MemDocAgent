# `feedback.py`

## `zxcvbn.feedback.get_feedback` · *function*

## Summary:
Generates user-facing feedback for password strength analysis based on score and matched patterns, providing actionable suggestions to improve password security.

## Description:
Processes password strength analysis results to create human-readable feedback that guides users toward stronger passwords. This function serves as the main interface for generating feedback messages in the zxcvbn password strength estimation system, extracting meaningful insights from detected match patterns and providing targeted improvement suggestions.

The function is extracted from the main password strength analysis pipeline to encapsulate all feedback generation logic in one place, making it easier to maintain and localize messages. It handles three main cases: empty password analysis, strong passwords (score > 2), and weak passwords requiring feedback.

## Args:
    score (int): Numeric password strength score ranging from 0-4, where higher values indicate stronger passwords
    sequence (list[dict]): List of match dictionaries representing detected patterns in the password analysis, each containing pattern information

## Returns:
    dict: Feedback dictionary with two keys:
        - 'warning' (str): Human-readable warning message about the weakest password pattern
        - 'suggestions' (list[str]): List of suggestion messages for improving password strength, with at least one suggestion added

## Raises:
    None explicitly raised, but may raise KeyError if match dictionaries lack expected keys when passed to get_match_feedback

## Constraints:
    Preconditions:
        - score must be an integer between 0-4
        - sequence must be a list of dictionaries with match information
        - Each match dictionary must contain a 'token' key for length comparison
    Postconditions:
        - Returned dictionary always contains 'warning' and 'suggestions' keys
        - Suggestions list is always returned (possibly empty or with one extra suggestion)
        - Warning string is either a translated message or empty string

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_feedback] --> B{len(sequence) == 0?}
    B -- Yes --> C[Return basic feedback for empty password]
    B -- No --> D{score > 2?}
    D -- Yes --> E[Return empty feedback for strong password]
    D -- No --> F[Find longest match in sequence]
    F --> G[Call get_match_feedback with longest match]
    G --> H{get_match_feedback returns feedback?}
    H -- Yes --> I[Insert extra feedback at beginning]
    H -- No --> J[Create new feedback with extra feedback]
    J --> K[Return feedback]
    I --> K
```

## Examples:
    >>> get_feedback(0, [{'token': 'password'}])
    {'warning': 'Use a few words, avoid common phrases.', 'suggestions': ['Use a few words, avoid common phrases.', 'No need for symbols, digits, or uppercase letters.']}

    >>> get_feedback(3, [{'token': 'mypassword'}])
    {'warning': '', 'suggestions': []}
```

## `zxcvbn.feedback.get_match_feedback` · *function*

## Summary:
Generates user-facing feedback for password strength analysis based on detected match patterns, providing warnings and suggestions for improving password security.

## Description:
This function processes match dictionaries from password strength analysis and returns structured feedback containing warnings and suggestions tailored to specific password weaknesses. It serves as a central dispatcher that routes different match patterns to appropriate feedback generation logic, separating the feedback presentation layer from the core matching algorithms.

The function is extracted from the main password strength analysis pipeline to encapsulate all feedback generation logic in one place, making it easier to maintain and localize messages. It handles various password patterns including dictionary words, spatial keyboard patterns, repeated characters, sequences, regex matches, and date patterns.

## Args:
    match (dict): Dictionary containing match information with keys including:
        - 'pattern' (str): Type of pattern detected (e.g., 'dictionary', 'spatial', 'repeat')
        - Additional pattern-specific keys such as 'turns', 'base_token', 'regex_name'
    is_sole_match (bool): Boolean indicating whether this match is the only one in the password analysis

## Returns:
    dict or None: A dictionary containing:
        - 'warning' (str): Human-readable warning message about the match pattern
        - 'suggestions' (list[str]): List of suggestion messages for improving password strength
    Returns None when no specific feedback is available for the pattern (e.g., for 'regex' pattern except 'recent_year')

## Raises:
    None explicitly raised, but may raise KeyError if match dictionary lacks expected keys

## Constraints:
    Preconditions:
        - match dictionary must contain a 'pattern' key
        - match dictionary may contain pattern-specific keys depending on the pattern type
    Postconditions:
        - Returned dictionary always contains 'warning' and 'suggestions' keys when returning a result
        - Warning string is either a translated message or empty string
        - Suggestions list is always returned (possibly empty)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_match_feedback] --> B{match['pattern'] == 'dictionary'?}
    B -- Yes --> C[Call get_dictionary_match_feedback]
    B -- No --> D{match['pattern'] == 'spatial'?}
    D -- Yes --> E{match['turns'] == 1?}
    E -- Yes --> F[warning = straight rows message]
    E -- No --> G[warning = short keyboard pattern message]
    D -- No --> H{match['pattern'] == 'repeat'?}
    H -- Yes --> I{len(base_token) == 1?}
    I -- Yes --> J[warning = single repeat message]
    I -- No --> K[warning = multi-repeat message]
    H -- No --> L{match['pattern'] == 'sequence'?}
    L -- Yes --> M[warning = sequence message]
    L -- No --> N{match['pattern'] == 'regex'?}
    N -- Yes --> O{regex_name == 'recent_year'?}
    O -- Yes --> P[warning = recent year message]
    N -- No --> Q[Return None]
    L -- No --> R{match['pattern'] == 'date'?}
    R -- Yes --> S[warning = date message]
    R -- No --> T[Return None]
    U[Build suggestions] --> V[Return feedback dict]
```

## Examples:
    >>> match = {'pattern': 'spatial', 'turns': 1}
    >>> get_match_feedback(match, False)
    {'warning': 'Straight rows of keys are easy to guess.', 'suggestions': ['Use a longer keyboard pattern with more turns.']}

    >>> match = {'pattern': 'repeat', 'base_token': 'aaa'}
    >>> get_match_feedback(match, True)
    {'warning': 'Repeats like "aaa" are easy to guess.', 'suggestions': ['Avoid repeated words and characters.']}

## `zxcvbn.feedback.get_dictionary_match_feedback` · *function*

## Summary:
Generates user-facing feedback for dictionary-based password matches, including warnings about commonality and suggestions for improvement.

## Description:
This function provides human-readable feedback for password strength analysis when a dictionary match is detected. It determines appropriate warnings based on the dictionary type, match characteristics, and commonality rankings, while also offering specific suggestions for strengthening passwords based on word patterns like capitalization, reversal, and l33t substitutions.

The function is extracted from the main password strength analysis logic to separate the feedback generation concern from the core matching algorithm, allowing for easier maintenance and potential localization of messages.

## Args:
    match (dict): Dictionary containing match information with keys:
        - 'dictionary_name' (str): Name of the dictionary used for matching
        - 'rank' (int): Rank of the matched word in the dictionary (lower is more common)
        - 'guesses_log10' (float): Log10 of the number of guesses required to crack
        - 'reversed' (bool): Whether the token was reversed
        - 'l33t' (bool): Whether l33t substitutions were used
        - 'token' (str): The matched token
    is_sole_match (bool): Whether this is the only match in the password analysis

## Returns:
    dict: A dictionary containing:
        - 'warning' (str): Human-readable warning message about the match, or empty string
        - 'suggestions' (list[str]): List of suggestion messages for improving password strength

## Raises:
    None explicitly raised, but may raise KeyError if match dictionary lacks expected keys

## Constraints:
    Preconditions:
        - match dictionary must contain required keys: 'dictionary_name', 'token'
        - match dictionary may optionally contain: 'rank', 'guesses_log10', 'reversed', 'l33t'
    Postconditions:
        - Returned dictionary always contains 'warning' and 'suggestions' keys
        - Warning string is either empty or a translated message
        - Suggestions list is always returned (possibly empty)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_dictionary_match_feedback] --> B{dictionary_name == 'passwords'?}
    B -- Yes --> C{is_sole_match AND NOT l33t AND NOT reversed?}
    C -- Yes --> D{rank <= 10?}
    D -- Yes --> E[warning = top-10 message]
    D -- No --> F{rank <= 100?}
    F -- Yes --> G[warning = top-100 message]
    F -- No --> H[warning = very common message]
    C -- No --> I{guesses_log10 <= 4?}
    I -- Yes --> J[warning = similar to common message]
    I -- No --> K[warning = empty]
    B -- No --> L{dictionary_name == 'english'?}
    L -- Yes --> M{is_sole_match?}
    M -- Yes --> N[warning = word by itself message]
    M -- No --> O[warning = empty]
    L -- No --> P{dictionary_name in [surnames,male_names,female_names]?}
    P -- Yes --> Q{is_sole_match?}
    Q -- Yes --> R[warning = names/surnames alone message]
    Q -- No --> S[warning = common names/surnames message]
    P -- No --> T[warning = empty]
    U[Build suggestions] --> V[Return warning + suggestions]
```

## Examples:
    >>> match = {'dictionary_name': 'passwords', 'rank': 5, 'token': 'password'}
    >>> get_dictionary_match_feedback(match, True)
    {'warning': 'This is a top-10 common password.', 'suggestions': []}
    
    >>> match = {'dictionary_name': 'english', 'token': 'hello', 'reversed': True}
    >>> get_dictionary_match_feedback(match, True)
    {'warning': 'A word by itself is easy to guess.', 'suggestions': ['Reversed words aren\'t much harder to guess.']}
```

