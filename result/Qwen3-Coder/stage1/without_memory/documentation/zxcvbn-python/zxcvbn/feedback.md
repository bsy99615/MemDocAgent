# `feedback.py`

## `zxcvbn.feedback.get_feedback` · *function*

## Summary:
Generates human-readable feedback for password strength based on match analysis and score.

## Description:
This function provides user-friendly suggestions and warnings to help users create stronger passwords. It analyzes the most significant match in a sequence of password matches and generates appropriate feedback based on the password strength score.

The function is designed to be called during password strength evaluation to provide actionable feedback to users. It's extracted into its own function to separate the logic of generating feedback from the core matching and scoring algorithms.

## Args:
    score (int): The password strength score (typically 0-4). Higher values indicate stronger passwords.
    sequence (list[dict]): List of match objects containing pattern information and token data.

## Returns:
    dict: A dictionary with 'warning' string and 'suggestions' list containing feedback strings for improving password strength.

## Raises:
    None explicitly raised, but may raise exceptions from underlying get_match_feedback function calls.

## Constraints:
    Preconditions:
    - score should be an integer representing password strength
    - sequence should be a list of match dictionaries with 'pattern' and 'token' keys
    
    Postconditions:
    - Returns a dictionary with 'warning' and 'suggestions' keys
    - Suggestions list contains only strings

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_feedback] --> B{len(sequence) == 0?}
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
    {'warning': 'This is a commonly used password.', 'suggestions': ['Add another word or two. Uncommon words are better.']}
    
    >>> get_feedback(3, [{'token': 'mypassword', 'pattern': 'dictionary'}])
    {'warning': '', 'suggestions': []}
    
    >>> get_feedback(1, [])
    {'warning': '', 'suggestions': ['Use a few words, avoid common phrases.', 'No need for symbols, digits, or uppercase letters.']}
```

## `zxcvbn.feedback.get_match_feedback` · *function*

*No documentation generated.*

## `zxcvbn.feedback.get_dictionary_match_feedback` · *function*

*No documentation generated.*

