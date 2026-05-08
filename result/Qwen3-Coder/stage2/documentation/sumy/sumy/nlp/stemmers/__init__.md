# `__init__.py`

## `sumy.nlp.stemmers.__init__.null_stemmer` · *function*

## Summary:
Converts any input object to a lowercase Unicode string representation.

## Description:
The null_stemmer function serves as a basic text normalization utility that transforms input objects into standardized lowercase Unicode strings. It acts as a fallback stemmer in the system, providing minimal text processing by ensuring consistent Unicode representation and case normalization. This function is particularly useful when more sophisticated stemming algorithms are not required or when dealing with inputs that don't need linguistic processing.

The function extracts this logic into its own component to provide a consistent interface for text normalization across different parts of the system, separating concerns between raw text processing and linguistic analysis. It ensures that all text inputs are normalized to a common format regardless of their original type or case.

## Args:
    object (Any): Any Python object that can be converted to a Unicode string. This could be a string, bytes, integer, float, or any other object type that can be processed by the underlying to_unicode function.

## Returns:
    str: A lowercase Unicode string representation of the input object. The returned string will always be in lowercase regardless of the input case, and will be properly encoded as a Unicode string. In Python 3, this will be a str type; in Python 2, this will be a unicode type.

## Raises:
    UnicodeDecodeError: When attempting to decode bytes objects that contain invalid UTF-8 sequences.

## Constraints:
    Preconditions:
    - Input object must be a valid Python object that can be processed by the to_unicode function
    - The to_unicode function must be available and properly configured for Unicode conversion
    
    Postconditions:
    - Always returns a Unicode string (str type in Python 3, unicode type in Python 2)
    - The returned string is guaranteed to be in lowercase
    - Input object is not modified

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[null_stemmer called] --> B{Convert to_unicode}
    B --> C{Apply .lower()}
    C --> D[Return lowercase Unicode string]
```

## Examples:
    # Convert string to lowercase Unicode
    result = null_stemmer("Hello World")
    # Returns: u"hello world" (Python 2) or "hello world" (Python 3)
    
    # Convert bytes to lowercase Unicode
    result = null_stemmer(b"HELLO WORLD")
    # Returns: u"hello world" (Python 2) or "hello world" (Python 3)
    
    # Convert number to lowercase Unicode
    result = null_stemmer(123)
    # Returns: u"123" (Python 2) or "123" (Python 3)
```

## `sumy.nlp.stemmers.__init__.Stemmer` · *class*

## Summary:
A language-aware stemmer that applies appropriate stemming algorithms based on the specified language, with special handling for certain languages and fallback to NLTK Snowball stemmers.

## Description:
The Stemmer class provides a unified interface for applying stemming operations to words in various languages. It maintains a registry of special-case stemmers for specific languages and falls back to NLTK's Snowball stemmers for languages not explicitly handled. This abstraction allows users to apply stemming without needing to know the underlying implementation details or language-specific algorithms.

The class is typically instantiated by passing a language identifier to its constructor, and then used by calling the instance with a word to be stemmed.

## State:
- `_stemmer`: Function object that performs the actual stemming operation. Initially set to `null_stemmer`, then replaced with an appropriate stemmer function based on the language specification.
- `SPECIAL_STEMMERS`: Class-level dictionary mapping language names to their respective stemmer functions. Contains special-case stemmers for Czech, Slovak, Hebrew, Chinese, Japanese, Korean, Ukrainian, and Greek languages.

## Lifecycle:
- Creation: Instantiate with a language string parameter. The constructor normalizes the language name and selects an appropriate stemmer function from NLTK's snowball stemmers or special-case implementations.
- Usage: Call the instance with a word string to get its stemmed form. The __call__ method delegates to the selected stemmer function.
- Destruction: No explicit cleanup required; uses standard Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[Stemmer.__init__] --> B{Language in SPECIAL_STEMMERS?}
    B -- Yes --> C[Set _stemmer to SPECIAL_STEMMER]
    B -- No --> D[Construct NLTK stemmer class name]
    D --> E[Get stemmer class from nltk.stem.snowball]
    E --> F{Class found?}
    F -- No --> G[raise LookupError]
    F -- Yes --> H[Set _stemmer to stem() method]
    A --> I[Return]
    I --> J[Stemmer.__call__]
    J --> K[_stemmer(word)]
```

## Raises:
- `LookupError`: Raised when a stemmer is not available for the specified language and no suitable NLTK stemmer can be found in nltk.stem.snowball.

## Example:
```python
# Create a stemmer for English
english_stemmer = Stemmer('english')
stemmed_word = english_stemmer('running')  # Returns 'run'

# Create a stemmer for Czech
czech_stemmer = Stemmer('czech')
stemmed_word = czech_stemmer('běží')  # Uses Czech-specific stemmer
```

### `sumy.nlp.stemmers.__init__.Stemmer.__init__` · *method*

## Summary:
Initializes a Stemmer instance with an appropriate stemming algorithm for the specified language.

## Description:
The Stemmer.__init__ method configures the instance to use the correct stemming algorithm based on the provided language parameter. It first normalizes the language name, then attempts to use a special-case stemmer if available for that language. If no special stemmer exists, it dynamically constructs and retrieves the appropriate NLTK Snowball stemmer class. This method sets up the internal `_stemmer` attribute to point to the selected stemming function.

This logic is encapsulated in its own method rather than being inlined because it contains complex conditional logic for selecting different stemming approaches, error handling for unsupported languages, and dynamic class resolution. Separating this into its own method makes the code more readable, testable, and maintainable.

## Args:
    language (str): Language identifier for which to select a stemming algorithm. This can be a language name (e.g., 'english', 'french') or ISO language code (e.g., 'en', 'fr'). The language will be normalized to ensure consistent lookup.

## Returns:
    None: This method does not return a value. It initializes the instance's internal state.

## Raises:
    LookupError: Raised when a stemmer is not available for the specified language and no suitable NLTK stemmer can be found in nltk.stem.snowball.

## State Changes:
    Attributes READ: 
    - self.SPECIAL_STEMMERS (class attribute)
    
    Attributes WRITTEN:
    - self._stemmer (instance attribute)

## Constraints:
    Preconditions:
    - The language parameter must be a string that can be processed by the normalize_language function
    - The SPECIAL_STEMMERS dictionary must be properly initialized with language mappings
    - The nltk.stem.snowball module must be importable and contain the required stemmer classes
    
    Postconditions:
    - The self._stemmer attribute will be set to a callable function that performs stemming
    - If a special stemmer exists for the language, self._stemmer will reference that special stemmer
    - If no special stemmer exists, self._stemmer will reference the stem() method of an NLTK Snowball stemmer class
    - If no suitable stemmer can be found, a LookupError will be raised instead

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state beyond initializing the instance's internal attributes.

### `sumy.nlp.stemmers.__init__.Stemmer.__call__` · *method*

## Summary:
Applies the selected language-specific stemmer to the input word.

## Description:
This method serves as the primary interface for stemming words using the language-specific stemmer configured during object initialization. It delegates to the appropriate stemmer based on the language setting, which can be either a specialized stemmer for specific languages (like Czech, Ukrainian, Greek) or a NLTK-based stemmer for standard languages.

## Args:
    word (str): The input word to be stemmed.

## Returns:
    str: The stemmed version of the input word.

## Raises:
    LookupError: When a stemmer is not available for the specified language during initialization.

## State Changes:
    Attributes READ: self._stemmer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Stemmer object must have been initialized with a valid language.
    Postconditions: The returned string is the stemmed version of the input word according to the selected language's stemming rules.

## Side Effects:
    None

