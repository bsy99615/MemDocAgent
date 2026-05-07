# `greek.py`

## `sumy.nlp.stemmers.greek.stem_word` · *function*

## Summary:
Stems Greek words by applying morphological analysis with multiple grammatical tags to find the most appropriate root form.

## Description:
This function applies stemming to Greek words by utilizing the greek-stemmer library with various grammatical tags. It serves as a wrapper around the external Greek stemmer to handle word normalization, tag iteration, and candidate selection. The function is designed to work with Greek text processing pipelines where morphological reduction is needed.

## Args:
    word (str): The Greek word to be stemmed. Must be a string containing Greek characters.

## Returns:
    str: The stemmed version of the input word. For words shorter than 4 characters, returns the lowercase version of the word unchanged. For longer words, returns the shortest valid stem candidate found among all grammatical tag combinations, or the original word if no valid stems are found.

## Raises:
    ValueError: When the required 'greek-stemmer' library is not installed, indicating that the user needs to install it via 'pip install greek-stemmer-pos'.

## Constraints:
    Preconditions:
        - Input word must be a string
        - The greek-stemmer library must be installed in the environment
    Postconditions:
        - Returns a lowercase string representation of the stemmed word
        - For words with length less than 4, returns the original word in lowercase
        - For longer words, returns the shortest valid stem candidate or original word

## Side Effects:
    - Raises ImportError if the greek-stemmer library is not available
    - Makes external library calls to the greek-stemmer package

## Control Flow:
```mermaid
flowchart TD
    A[Start stem_word] --> B{Word length < 4?}
    B -- Yes --> C[Return word.lower()]
    B -- No --> D[Initialize stem_candidates set]
    D --> E[Iterate through _TOTAL_TAGS]
    E --> F[Call gr_stemmer.stem_word(word.lower(), tag)]
    F --> G{Try-catch TypeError/ValueError}
    G -- Success --> H{stemmed != None AND last_char in _CONSONANTS?}
    H -- Yes --> I[Add stemmed to stem_candidates]
    H -- No --> J[Continue loop]
    G -- Exception --> J
    J --> K{End of _TOTAL_TAGS?}
    K -- No --> E
    K -- Yes --> L[Return min(stem_candidates or [word], key=len).lower()]
```

## Examples:
    # Basic usage with a valid Greek word
    result = stem_word("παιδιά")
    # Returns: "παιδ" (or similar stem)
    
    # Short word (less than 4 characters)
    result = stem_word("καλη")
    # Returns: "καλη"
    
    # Word with no valid stems found
    result = stem_word("ενα")
    # Returns: "ενα" (original word)

