# `feedback.py`

## `zxcvbn.feedback.get_feedback` · *function*

## Summary:
Generates user-facing feedback for password strength analysis based on score and matched patterns.

## Description:
Processes password strength analysis results to provide actionable feedback to users. This function determines appropriate warnings and suggestions based on the password's strength score and the most significant pattern match found. It serves as the final layer in the feedback generation pipeline, combining match-specific feedback with general improvement recommendations.

The logic is extracted into its own function to separate the feedback generation concerns from the core matching and scoring algorithms, enabling cleaner code organization and easier testing of feedback presentation.

## Args:
    score (int): Password strength score ranging from 0 to 4, where higher values indicate stronger passwords
    sequence (list[dict]): List of match objects representing detected patterns in the password, each with pattern information

## Returns:
    dict: Feedback dictionary containing:
        - 'warning' (str): Warning message about password weaknesses
        - 'suggestions' (list[str]): List of improvement suggestions

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - score must be an integer between 0 and 4
        - sequence must be a list of dictionaries with match information
    Postconditions:
        - Always returns a dictionary with 'warning' and 'suggestions' keys
        - Empty sequence returns basic suggestions about using words
        - Score > 2 returns empty suggestions (strong password)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_feedback] --> B{len(sequence) == 0?}
    B -- Yes --> C[Return basic suggestions]
    B -- No --> D{score > 2?}
    D -- Yes --> E[Return empty suggestions]
    D -- No --> F[Find longest match]
    F --> G[Call get_match_feedback]
    G --> H{get_match_feedback result?}
    H -- Yes --> I[Insert extra feedback at beginning]
    H -- No --> J[Create new feedback with extra feedback]
    I --> K[Return feedback]
    J --> K
```

## Examples:
    >>> get_feedback(0, [{'token': 'password', 'pattern': 'dictionary'}])
    {'warning': 'Use a few words, avoid common phrases.', 'suggestions': ['Add another word or two. Uncommon words are better.']}

    >>> get_feedback(3, [{'token': 'mypassword', 'pattern': 'dictionary'}])
    {'warning': '', 'suggestions': []}
```

## `zxcvbn.feedback.get_match_feedback` · *function*

## Summary:
Generates user-facing feedback for password strength analysis based on detected matching patterns.

## Description:
Processes match data from zxcvbn's pattern matching algorithms to create human-readable feedback with warnings and suggestions for improving password strength. This function separates feedback generation logic from the core matching algorithms, enabling cleaner code organization and easier testing of feedback presentation.

## Args:
    match (dict): Dictionary containing match information with pattern type and related metadata
        - 'pattern' (str): Type of pattern detected ('dictionary', 'spatial', 'repeat', 'sequence', 'regex', 'date')
        - Additional pattern-specific keys depending on the pattern type
    is_sole_match (bool): Indicates whether this match is the only one found in the password

## Returns:
    dict or None: Feedback dictionary with 'warning' and 'suggestions' keys when a supported pattern is matched, 
                  or None if the pattern type is not handled or no feedback is applicable

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - match must be a dictionary with at least a 'pattern' key
        - match['pattern'] must be one of the supported pattern types
    Postconditions:
        - Returns a dictionary with 'warning' and 'suggestions' keys for handled pattern types
        - Returns None for unhandled pattern types or when no feedback is generated
        - All returned dictionaries contain both 'warning' and 'suggestions' keys

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
    Q -- Yes --> R[warning = dates]
    Q -- No --> S[Return None]
    F --> T[Return feedback]
    G --> T
    J --> T
    K --> T
    M --> T
    P --> T
    R --> T
```

## Examples:
    >>> match = {'pattern': 'spatial', 'turns': 1}
    >>> get_match_feedback(match, False)
    {'warning': 'Straight rows of keys are easy to guess.', 'suggestions': ['Use a longer keyboard pattern with more turns.']}

    >>> match = {'pattern': 'repeat', 'base_token': 'abc'}
    >>> get_match_feedback(match, True)
    {'warning': 'Repeats like "abcabcabc" are only slightly harder to guess than "abc".', 'suggestions': ['Avoid repeated words and characters.']}

## `zxcvbn.feedback.get_dictionary_match_feedback` · *function*

## Summary:
Generates user-facing feedback for dictionary-based password matches, including warnings about commonality and suggestions for improvement.

## Description:
Processes match data from zxcvbn's dictionary matching algorithm to create human-readable feedback. This function separates concerns by extracting feedback generation logic from the main matching process, allowing for cleaner code organization and easier testing of feedback generation.

## Args:
    match (dict): Dictionary containing match information with keys:
        - 'dictionary_name' (str): Name of the dictionary used for matching
        - 'rank' (int): Rank of the matched word/password in the dictionary
        - 'guesses_log10' (float): Log10 of the number of guesses needed to crack
        - 'l33t' (bool): Whether l33t substitutions were used
        - 'reversed' (bool): Whether the token was reversed
        - 'token' (str): The matched token
    is_sole_match (bool): Whether this is the only match in the password

## Returns:
    dict: Feedback dictionary with:
        - 'warning' (str): Warning message about password strength
        - 'suggestions' (list[str]): List of suggestions for improving password strength

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - match must be a dictionary with required keys
        - match['dictionary_name'] must be a string
        - match['token'] must be a string
    Postconditions:
        - Returns a dictionary with 'warning' and 'suggestions' keys
        - Warning string is empty if no warning applies
        - Suggestions list is empty if no suggestions apply

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_dictionary_match_feedback] --> B{dictionary_name == 'passwords'?}
    B -- Yes --> C{is_sole_match AND NOT l33t AND NOT reversed?}
    C -- Yes --> D{rank <= 10?}
    D -- Yes --> E[warning = top-10]
    D -- No --> F{rank <= 100?}
    F -- Yes --> G[warning = top-100]
    F -- No --> H[warning = very common]
    C -- No --> I{guesses_log10 <= 4?}
    I -- Yes --> J[warning = similar to common]
    I -- No --> K[warning = empty]
    B -- No --> L{dictionary_name == 'english'?}
    L -- Yes --> M{is_sole_match?}
    M -- Yes --> N[warning = word by itself]
    M -- No --> O[warning = empty]
    L -- No --> P{dictionary_name in [surnames,male_names,female_names]?}
    P -- Yes --> Q{is_sole_match?}
    Q -- Yes --> R[warning = names by themselves]
    Q -- No --> S[warning = common names]
    P -- No --> T[warning = empty]
    U[Generate suggestions] --> V[Return feedback dict]
```

## Examples:
    >>> match = {'dictionary_name': 'passwords', 'rank': 5, 'token': 'password'}
    >>> get_dictionary_match_feedback(match, True)
    {'warning': 'This is a top-10 common password.', 'suggestions': []}
    
    >>> match = {'dictionary_name': 'english', 'token': 'cat', 'reversed': True}
    >>> get_dictionary_match_feedback(match, True)
    {'warning': 'A word by itself is easy to guess.', 'suggestions': ['Reversed words aren\'t much harder to guess.']}

