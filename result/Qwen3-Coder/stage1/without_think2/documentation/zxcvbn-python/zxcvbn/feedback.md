# `feedback.py`

## `zxcvbn.feedback.get_feedback` · *function*

## Summary:
Generates user feedback for password strength analysis results, providing warnings and suggestions to improve password security based on the weakest match found.

## Description:
Analyzes the results of password strength evaluation to provide actionable feedback to users. This function determines the most significant weakness in a password by identifying the longest matching token and generating appropriate feedback messages. It serves as the final step in translating password analysis results into human-readable guidance for users.

Known callers within the codebase:
- Called from password strength analysis functions during the feedback generation phase
- Triggered after all password matching patterns have been identified and scored

## Args:
    score (int): The overall password strength score (0-4) from the analysis
    sequence (list[dict]): A list of match dictionaries representing identified patterns in the password

## Returns:
    dict: A dictionary containing feedback information with:
        - 'warning' (str): A warning message about the weakest pattern found
        - 'suggestions' (list[str]): A list of suggestions for improving the password

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - The sequence parameter must be a list of dictionaries
        - Each dictionary in sequence must contain a 'token' key
        - Score must be an integer between 0 and 4
    Postconditions:
        - Always returns a dictionary with 'warning' and 'suggestions' keys
        - The returned warning string is either empty or contains a translated message
        - The suggestions list is always returned, potentially empty

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_feedback] --> B{len(sequence) == 0?}
    B -- Yes --> C[Return basic feedback]
    B -- No --> D{score > 2?}
    D -- Yes --> E[Return empty feedback]
    D -- No --> F[Find longest match]
    F --> G[Get match feedback]
    G --> H{Feedback exists?}
    H -- Yes --> I[Insert extra feedback at beginning]
    H -- No --> J[Create new feedback with extra feedback]
    J --> K[Return feedback]
```

## Examples:
Example 1 - Strong password feedback:
    Input: score=3, sequence=[{'token': 'password'}]
    Output: {'warning': '', 'suggestions': []}

Example 2 - Weak password feedback:
    Input: score=1, sequence=[{'token': '123', 'pattern': 'sequence'}]
    Output: {'warning': 'Sequences like "abc" or "6543" are easy to guess.', 'suggestions': ['Add another word or two. Uncommon words are better.', 'Avoid sequences.']}

## `zxcvbn.feedback.get_match_feedback` · *function*

## Summary:
Generates user feedback for different types of password matches identified during strength analysis, providing warnings and suggestions to improve password security.

## Description:
This function analyzes various password matching patterns (dictionary words, spatial key patterns, repeated characters, sequences, regex matches, and dates) and returns appropriate feedback messages with warnings and suggestions to help users create stronger passwords. The logic is extracted into its own function to separate feedback generation from the core matching algorithms, enabling cleaner code organization and easier maintenance of feedback messages.

Known callers within the codebase:
- Called from password strength analysis functions when processing individual match results
- Typically triggered during the feedback generation phase of password evaluation

## Args:
    match (dict): A dictionary containing match information with the following required keys:
        - 'pattern' (str): The type of pattern matched (e.g., 'dictionary', 'spatial', 'repeat', 'sequence', 'regex', 'date')
        - Additional pattern-specific keys depending on the pattern type
    is_sole_match (bool): Indicates whether this is the only match in the password

## Returns:
    dict: A dictionary containing feedback information with:
        - 'warning' (str): A warning message about the weakness of the matched pattern
        - 'suggestions' (list[str]): A list of suggestions for improving the password

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - The match dictionary must contain a 'pattern' key with valid pattern types
        - Pattern-specific keys must be present for the respective pattern types
    Postconditions:
        - Always returns a dictionary with 'warning' and 'suggestions' keys
        - The returned warning string is either empty or contains a translated message
        - The suggestions list is always returned, potentially empty

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
    E -- No --> G[warning = short keyboard message]
    D -- No --> H{match['pattern'] == 'repeat'?}
    H -- Yes --> I{len(base_token) == 1?}
    I -- Yes --> J[warning = single repeat message]
    I -- No --> K[warning = multi repeat message]
    H -- No --> L{match['pattern'] == 'sequence'?}
    L -- Yes --> M[warning = sequence message]
    L -- No --> N{match['pattern'] == 'regex'?}
    N -- Yes --> O{match['regex_name'] == 'recent_year'?}
    O -- Yes --> P[warning = recent year message]
    N -- No --> Q{match['pattern'] == 'date'?}
    Q -- Yes --> R[warning = date message]
    S[Return feedback dict] --> T[End]
```

## Examples:
Example 1 - Spatial pattern feedback:
    Input: {'pattern': 'spatial', 'turns': 1}, False
    Output: {'warning': 'Straight rows of keys are easy to guess.', 'suggestions': ['Use a longer keyboard pattern with more turns.']}

Example 2 - Sequence pattern feedback:
    Input: {'pattern': 'sequence'}, False
    Output: {'warning': 'Sequences like "abc" or "6543" are easy to guess.', 'suggestions': ['Avoid sequences.']}

## `zxcvbn.feedback.get_dictionary_match_feedback` · *function*

## Summary:
Generates user feedback for dictionary-based password matches, providing warnings and suggestions to improve password strength.

## Description:
This function analyzes a dictionary match found in a password and generates appropriate feedback messages. It provides both warning messages about the weakness of the matched word and suggestions for improving the password. The function is designed to be called during password strength analysis to give users actionable feedback.

The logic is extracted into its own function to separate the feedback generation concern from the core matching algorithm, allowing for cleaner code organization and easier maintenance of feedback messages.

## Args:
    match (dict): A dictionary containing match information with the following required keys:
        - 'dictionary_name' (str): Name of the dictionary used for matching (e.g., 'passwords', 'english', 'surnames')
        - 'token' (str): The matched token from the password
        - Optional keys:
            - 'rank' (int): Rank of the password in the common passwords list (if applicable)
            - 'guesses_log10' (float): Log10 of the number of guesses needed to crack
            - 'reversed' (bool): Whether the token was reversed
            - 'l33t' (bool): Whether l33t substitutions were used
    is_sole_match (bool): Indicates whether this is the only match in the password

## Returns:
    dict: A dictionary containing two keys:
        - 'warning' (str): A warning message about the weakness of the matched word (empty string if no warning)
        - 'suggestions' (list[str]): A list of suggestions for improving the password (empty list if no suggestions)

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - The match dictionary must contain 'dictionary_name' and 'token' keys
        - The match dictionary may optionally contain 'rank', 'guesses_log10', 'reversed', 'l33t'
    Postconditions:
        - Always returns a dictionary with 'warning' and 'suggestions' keys
        - The returned warning string is either empty or contains a translated message
        - The suggestions list is always returned, potentially empty

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
    U[Generate suggestions] --> V[Return warning and suggestions]
```

## Examples:
    Example 1 - Top 10 common password:
        Input: {'dictionary_name': 'passwords', 'rank': 5, 'token': 'password', 'reversed': False, 'l33t': False}, True
        Output: {'warning': 'This is a top-10 common password.', 'suggestions': []}

    Example 2 - Common name suggestion:
        Input: {'dictionary_name': 'male_names', 'token': 'john', 'reversed': False, 'l33t': False}, False
        Output: {'warning': 'Common names and surnames are easy to guess.', 'suggestions': []}
        
    Example 3 - Capitalization suggestion:
        Input: {'dictionary_name': 'english', 'token': 'Password', 'reversed': False, 'l33t': False}, False
        Output: {'warning': '', 'suggestions': ["Capitalization doesn't help very much."]}

