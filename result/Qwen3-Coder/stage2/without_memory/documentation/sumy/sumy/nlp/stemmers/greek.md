# `greek.py`

## `sumy.nlp.stemmers.greek.stem_word` · *function*

## Summary:
Applies morphological stemming to Greek words using part-of-speech tagging to select the most linguistically appropriate stem.

## Description:
This function implements Greek word stemming by leveraging the greek-stemmer library with multiple part-of-speech tags to find the best stem candidate. It serves as a robust wrapper that handles edge cases like short words and missing dependencies while ensuring linguistic validity of the output stems.

## Args:
    word (str): The Greek word to be stemmed. Must be a string containing Greek characters. The word should be in lowercase for optimal performance.

## Returns:
    str: The stemmed version of the input word. For words with fewer than 4 characters, returns the original word in lowercase. For longer words, returns the shortest valid stem candidate that ends with a consonant, or the original word if no valid stems are found.

## Raises:
    ValueError: When the required 'greek-stemmer' Python package is not installed, providing installation instructions.

## Constraints:
    Preconditions:
        - Input word must be a string
        - The 'greek-stemmer' Python package must be installed
    Postconditions:
        - Output is always returned in lowercase
        - For words shorter than 4 characters, the original word is returned unchanged
        - For longer words, the returned stem ends with a consonant character (based on _CONSONANTS constant)

## Side Effects:
    - Raises ImportError if greek-stemmer package is not installed
    - No persistent state changes or I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start stem_word] --> B{Word length < 4?}
    B -- Yes --> C[Return word.lower()]
    B -- No --> D[Initialize stem_candidates set]
    D --> E[Iterate through _TOTAL_TAGS]
    E --> F[Call gr_stemmer.stem_word(word.lower(), tag)]
    F --> G{Try-catch TypeError/ValueError}
    G -- Success --> H{stemmed != None AND last char in _CONSONANTS?}
    H -- Yes --> I[Add stemmed to stem_candidates]
    H -- No --> J[Continue]
    G -- Exception --> K[Continue loop]
    E --> L{stem_candidates empty?}
    L -- Yes --> M[Return word.lower()]
    L -- No --> N[Return min(stem_candidates, key=len).lower()]
```

## Examples:
    # Basic usage with valid Greek word
    result = stem_word("παιδιά")  # Returns stemmed version like "παιδ"
    
    # Short word (less than 4 chars)
    result = stem_word("το")     # Returns "το" (unchanged)
    
    # Error case (requires greek-stemmer package)
    # ValueError: Greek stemmer requires greek-stemmer. Please, install it by command 'pip install greek-stemmer-pos'.

