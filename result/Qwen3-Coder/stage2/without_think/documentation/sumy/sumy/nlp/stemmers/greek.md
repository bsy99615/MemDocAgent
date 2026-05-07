# `greek.py`

## `sumy.nlp.stemmers.greek.stem_word` · *function*

## Summary:
Applies morphological stemming to Greek words using multiple part-of-speech tags to extract the root form.

## Description:
This function performs Greek word stemming by applying the greek-stemmer library with various grammatical tags to find the most appropriate root form. It is designed for preprocessing Greek text in natural language processing applications. The function attempts to stem the input word using different part-of-speech categories defined in the module's _TOTAL_TAGS constant, filters valid stem candidates based on consonant endings defined in the module's _CONSONANTS constant, and returns the shortest valid stem. For words shorter than 4 characters, it returns the word unchanged in lowercase.

## Args:
    word (str): The Greek word to be stemmed. Must be a string containing Greek characters.

## Returns:
    str: The stemmed version of the input word. Returns the original word in lowercase if it's shorter than 4 characters, or the shortest valid stem candidate if available.

## Raises:
    ValueError: When the required 'greek-stemmer' library is not installed, with a descriptive message instructing the user to install it via 'pip install greek-stemmer-pos'.

## Constraints:
    Preconditions:
        - Input word must be a string
        - The 'greek-stemmer' Python package must be installed
        - The global constants _TOTAL_TAGS and _CONSONANTS must be properly defined in the module scope
    
    Postconditions:
        - Returns a lowercase string representation of the stemmed word
        - If word length < 4, returns the original word in lowercase
        - If no valid stems are found, returns the original word in lowercase

## Side Effects:
    - Raises ImportError if the greek-stemmer library is not available
    - No persistent state changes or I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start stem_word] --> B{Word length < 4?}
    B -- Yes --> C[Return word.lower()]
    B -- No --> D[Initialize stem_candidates]
    D --> E[Iterate through _TOTAL_TAGS]
    E --> F[Call gr_stemmer.stem_word(word.lower(), tag)]
    F --> G{Try-catch TypeError/ValueError}
    G -- Success --> H{stemmed and last_char in _CONSONANTS?}
    H -- Yes --> I[Add stemmed to stem_candidates]
    H -- No --> J[Continue]
    G -- Exception --> K[Continue loop]
    E --> L{stem_candidates empty?}
    L -- Yes --> M[Return word.lower()]
    L -- No --> N[Return min(stem_candidates, key=len).lower()]
```

## Examples:
    # Basic usage
    result = stem_word("παιδιά")
    # Returns stemmed version of the Greek word
    
    # Short word (less than 4 characters)
    result = stem_word("το")
    # Returns "το" (unchanged)
    
    # Word requiring stemming
    result = stem_word("παιδικός")
    # Returns the stemmed form like "παιδ"

