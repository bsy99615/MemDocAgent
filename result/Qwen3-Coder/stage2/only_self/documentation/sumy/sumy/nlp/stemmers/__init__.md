# `__init__.py`

## `sumy.nlp.stemmers.__init__.null_stemmer` · *function*

*No documentation generated.*

## `sumy.nlp.stemmers.__init__.Stemmer` · *class*

## Summary:
A language-aware stemmer that provides word stemming functionality for various languages, with special handling for specific languages and fallback to NLTK stemmers.

## Description:
The Stemmer class serves as a unified interface for applying stemming operations to words in different languages. It handles special cases for languages like Czech, Slovak, Hebrew, Chinese, Japanese, Korean, Ukrainian, and Greek with custom stemmer functions, while falling back to NLTK's Snowball stemmers for other languages. This abstraction allows users to stem words without worrying about language-specific implementation details.

The class is typically instantiated by passing a language identifier to its constructor, which then selects the appropriate stemming algorithm. It can be used as a callable object where the __call__ method applies the selected stemmer to individual words.

## State:
- `_stemmer`: callable function that performs the actual stemming operation
  - Type: function/callable
  - Valid range: Any callable that accepts a string and returns a stemmed string
  - Invariant: Always refers to a valid stemming function after initialization
- `SPECIAL_STEMMERS`: class attribute mapping language names to specific stemmer functions
  - Type: dict
  - Keys: lowercase language names ('czech', 'slovak', 'hebrew', 'chinese', 'japanese', 'korean', 'ukrainian', 'greek')
  - Values: stemmer functions

## Lifecycle:
- Creation: Instantiate with a language parameter (string)
- Usage: Call the instance with a word string to get the stemmed version
- Destruction: No explicit cleanup required; uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[Stemmer.__init__] --> B{Language in SPECIAL_STEMMERS?}
    B -- Yes --> C[Set _stemmer to special stemmer]
    B -- No --> D[Construct stemmer class name]
    D --> E[Attempt to get stemmer class from nltk_stemmers_module]
    E --> F{Class found?}
    F -- No --> G[raise LookupError]
    F -- Yes --> H[Set _stemmer to stem method]
    I[Stemmer.__call__] --> J[_stemmer(word)]
```

## Raises:
- `LookupError`: Raised when a stemmer is not available for the specified language and no suitable NLTK stemmer can be found

## Example:
```python
# Create a stemmer for English
english_stemmer = Stemmer('english')

# Stem a word
stemmed_word = english_stemmer('running')  # Returns 'run'

# Create a stemmer for Czech
czech_stemmer = Stemmer('czech')
stemmed_word = czech_stemmer('běží')  # Uses special Czech stemmer

# This will raise LookupError for unsupported language
try:
    unsupported_stemmer = Stemmer('unsupported_language')
except LookupError:
    print("Stemmer not available for this language")
```

### `sumy.nlp.stemmers.__init__.Stemmer.__init__` · *method*

## Summary:
Initializes a Stemmer instance with the appropriate stemming algorithm for the specified language.

## Description:
The Stemmer constructor sets up the internal stemmer based on the provided language parameter. It first normalizes the language name, then attempts to use a special-purpose stemmer for specific languages (like Czech, Greek, Ukrainian) before falling back to NLTK's Snowball stemmers for other languages. This method ensures that the appropriate stemming algorithm is selected and stored in the internal `_stemmer` attribute for later use.

This logic is encapsulated in its own method because it contains complex conditional logic for selecting the right stemmer implementation and proper error handling when a stemmer is not available for a requested language.

## Args:
    language (str): Language identifier for which to initialize the stemmer. This can be any language code that is recognized by the system, including ISO codes or common language names.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    LookupError: Raised when a stemmer is not available for the specified language and no suitable NLTK stemmer can be found.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - `_stemmer`: Set to either a special stemmer function or an NLTK stemmer method

## Constraints:
    Preconditions:
    - The language parameter must be a valid string that can be normalized by the `normalize_language` utility function
    - The Stemmer class must have a `SPECIAL_STEMMERS` class attribute defined with appropriate mappings
    - The `nltk.stem.snowball` module must be available for fallback stemmer selection
    
    Postconditions:
    - The `_stemmer` attribute will be set to a callable function that can stem words
    - If a special stemmer exists for the language, it will be used
    - If no special stemmer exists, an NLTK stemmer will be attempted and used
    - If neither is available, a LookupError will be raised

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only sets internal object attributes.

### `sumy.nlp.stemmers.__init__.Stemmer.__call__` · *method*

## Summary:
Invokes the stemmer on a given word and returns its stemmed form.

## Description:
This method implements the callable interface for the Stemmer class, allowing instances to be called directly with a word parameter. It delegates the stemming operation to the appropriate stemmer function stored in `self._stemmer`.

## Args:
    word (str): The input word to be stemmed.

## Returns:
    str: The stemmed version of the input word.

## Raises:
    LookupError: When an NLTK stemmer is requested for a language that doesn't have a corresponding stemmer class.

## State Changes:
    Attributes READ: self._stemmer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Stemmer instance must have been properly initialized with a valid language.
    Postconditions: The returned string is the stemmed version of the input word according to the selected stemmer algorithm.

## Side Effects:
    None

