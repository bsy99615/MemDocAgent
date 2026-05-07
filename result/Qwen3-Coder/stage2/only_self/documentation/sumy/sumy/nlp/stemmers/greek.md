# `greek.py`

## `sumy.nlp.stemmers.greek.stem_word` · *function*

## Summary:
Stems Greek words using morphological analysis with multiple POS tags and selects the shortest valid stem ending in a consonant.

## Description:
This function applies stemming to Greek words using the greek-stemmer library. It attempts to stem the input word using various grammatical tags and selects the shortest valid stem that ends with a consonant. For words shorter than 4 characters, it returns the lowercase version directly without stemming.

## Args:
    word (str): The Greek word to be stemmed.

## Returns:
    str: The stemmed version of the input word. Returns the lowercase original word if no valid stems are found or if the word is shorter than 4 characters.

## Raises:
    ValueError: When the required 'greek-stemmer' library is not installed.

## Constraints:
    Precondition: Input must be a string.
    Postcondition: Output is always returned in lowercase.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start stem_word] --> B{Word length < 4?}
    B -- Yes --> C[Return word.lower()]
    B -- No --> D[Initialize stem_candidates]
    D --> E[Iterate through _TOTAL_TAGS]
    E --> F[Call gr_stemmer.stem_word(word.lower(), tag)]
    F --> G{Try-catch TypeError/ValueError}
    G -- Success --> H{stemmed != None AND last_char in _CONSONANTS?}
    H -- Yes --> I[Add stemmed to stem_candidates]
    H -- No --> J[Continue loop]
    G -- Exception --> J
    E --> K{stem_candidates empty?}
    K -- Yes --> L[Return word.lower()]
    K -- No --> M[Return min(stem_candidates, key=len).lower()]
```

## Examples:
    >>> stem_word("ευχαριστώ")
    "ευχαριστ"
    
    >>> stem_word("καλημέρα")
    "καλημερ"
    
    >>> stem_word("α")
    "α"

