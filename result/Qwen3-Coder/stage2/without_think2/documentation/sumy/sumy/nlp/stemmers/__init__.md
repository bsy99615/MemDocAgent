# `__init__.py`

## `sumy.nlp.stemmers.__init__.null_stemmer` · *function*

## Summary:
Converts an input object to a lowercase Unicode string representation.

## Description:
The null_stemmer function serves as a basic normalization utility that ensures consistent Unicode string processing by converting any input object to its lowercase Unicode representation. This function is typically used in text preprocessing pipelines where uniform string formatting is required regardless of input data types.

## Args:
    object (Any): The input object to be converted to lowercase Unicode string. Can be a Unicode string, bytes object, or any other object type that can be processed by the to_unicode compatibility function.

## Returns:
    str: Lowercase Unicode string representation of the input object. The function guarantees that the output is always a Unicode string in lowercase format.

## Raises:
    UnicodeDecodeError: When attempting to decode bytes objects that contain invalid UTF-8 sequences during the to_unicode conversion process.

## Constraints:
    - Preconditions: The input object must be a valid Python object that can be processed by the underlying to_unicode function
    - Postconditions: The returned value is always a Unicode string (str type in Python 3) in lowercase format

## Side Effects:
    - Invokes the to_unicode compatibility function which may decode bytes objects using UTF-8
    - Calls instance_to_unicode helper function for non-Unicode, non-bytes objects during the conversion process
    - No external I/O or state mutations beyond the internal Unicode conversion process

## Control Flow:
```mermaid
flowchart TD
    A[Start null_stemmer] --> B[to_unicode(object)]
    B --> C[object.lower()]
    C --> D[Return lowercase Unicode string]
```

## Examples:
    # Converting a Unicode string to lowercase
    result = null_stemmer(u"HELLO")  # Returns u"hello"
    
    # Converting bytes to lowercase Unicode
    result = null_stemmer(b"HELLO")  # Returns u"hello" (UTF-8 decoded and lowercased)
    
    # Converting integer to lowercase Unicode
    result = null_stemmer(42)  # Returns u"42" (converted via instance_to_unicode then lowercased)
```

## `sumy.nlp.stemmers.__init__.Stemmer` · *class*

## Summary:
A language-aware stemmer that selects appropriate stemming algorithms based on the specified language.

## Description:
The Stemmer class provides a unified interface for applying linguistic stemming to words in various languages. It automatically selects the most appropriate stemming algorithm based on the language specification, falling back to NLTK's built-in stemmers for standard languages and using specialized stemmers for specific languages like Czech, Ukrainian, and Greek.

This class serves as a factory and wrapper that abstracts away the complexity of choosing different stemming algorithms for different languages, providing a consistent interface regardless of the underlying implementation details.

## State:
- `_stemmer`: callable function that performs the actual stemming operation
  - Type: function
  - Valid range: Any callable that accepts a string and returns a stemmed string
  - Invariant: Always refers to a valid stemming function after initialization

## Lifecycle:
- Creation: Instantiate with a language identifier string (e.g., 'english', 'czech')
- Usage: Call the instance with a word string to get its stemmed form
- Destruction: No special cleanup required; uses Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Stemmer.__init__] --> B{Language in SPECIAL_STEMMERS?}
    B -- Yes --> C[SPECIAL_STEMMERS[language]]
    B -- No --> D[nltk.stem.snowball.<language>Stemmer]
    D --> E[stemmer_class().stem]
    C --> F[Set _stemmer]
    E --> F
    F --> G[Stemmer.__call__]
    G --> H[Return _stemmer(word)]
```

## Raises:
- `LookupError`: When a stemmer is not available for the specified language

## Example:
```python
# Create a stemmer for English
english_stemmer = Stemmer('english')
stemmed_word = english_stemmer('running')  # Returns 'run'

# Create a stemmer for Czech
czech_stemmer = Stemmer('czech')
stemmed_word = czech_stemmer('běží')  # Uses specialized Czech stemmer
```

### `sumy.nlp.stemmers.__init__.Stemmer.__init__` · *method*

## Summary:
Initializes a Stemmer instance with a specified language, selecting the appropriate stemming algorithm.

## Description:
The `__init__` method configures a Stemmer instance by determining the correct stemming algorithm based on the provided language. It first normalizes the language identifier using `normalize_language`, then checks if a specialized stemmer exists in `SPECIAL_STEMMERS` for that language. If not, it attempts to find and instantiate an NLTK stemmer for the language. This method sets up the internal `_stemmer` attribute that will be used for actual stemming operations.

## Args:
    language (str): Language identifier (e.g., 'english', 'czech') that determines which stemming algorithm to use.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    LookupError: When no stemmer is available for the specified language, specifically when an NLTK stemmer cannot be found for the language.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._stemmer: Set to either a specialized stemmer function from SPECIAL_STEMMERS or an NLTK stemmer's stem method

## Constraints:
    - Preconditions: The language parameter must be a valid string that can be processed by `normalize_language`
    - Postconditions: The `self._stemmer` attribute is initialized to a callable that accepts a string and returns a stemmed string

## Side Effects:
    - May raise `LookupError` if the language is not supported
    - Sets the internal `self._stemmer` attribute to a callable function
    - Calls `normalize_language` function to process the language parameter

### `sumy.nlp.stemmers.__init__.Stemmer.__call__` · *method*

## Summary:
Applies the appropriate stemming algorithm to transform a word into its root form based on the language configured for this stemmer instance.

## Description:
This method serves as the primary interface for performing word stemming operations. It delegates the actual stemming process to the internal `_stemmer` attribute, which is selected during object initialization based on the specified language. The method acts as a unified entry point that abstracts away the complexity of choosing the correct stemming algorithm.

The stemmer chooses the appropriate algorithm based on:
1. Specialized stemmers for Czech, Slovak, Hebrew, Chinese, Japanese, Korean, Ukrainian, and Greek
2. The NLTK Snowball stemmer for all other languages, using the language name to determine the correct stemmer class

## Args:
    word (str): The input word to be stemmed. Must be a string.

## Returns:
    str: The stemmed version of the input word. For languages without specialized stemmers, the NLTK Snowball stemmer is used.

## Raises:
    LookupError: When a stemmer is not available for the specified language during initialization.

## State Changes:
    Attributes READ: self._stemmer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The stemmer instance must have been properly initialized with a supported language.
    Postconditions: The returned value is the root form of the input word according to the selected stemming algorithm.

## Side Effects:
    None

