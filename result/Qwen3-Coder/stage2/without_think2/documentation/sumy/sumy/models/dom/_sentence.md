# `_sentence.py`

## `sumy.models.dom._sentence.Sentence` · *class*

## Summary:
Represents a textual sentence or heading with associated metadata and tokenization capabilities.

## Description:
The Sentence class encapsulates a textual unit (either a regular sentence or a heading) along with its tokenization information. It provides a standardized interface for text processing operations while maintaining efficient access to word-level representations through caching. This abstraction enables consistent handling of document elements regardless of their semantic role (heading vs. body text).

## State:
- `_text` (str): The Unicode string representation of the sentence content, stripped of leading/trailing whitespace
- `_cached_property_words`: Cached result of word tokenization, automatically managed by the `@cached_property` decorator
- `_tokenizer`: Reference to a tokenizer object capable of converting text to word lists
- `_is_heading` (bool): Flag indicating whether this sentence represents a heading rather than regular text

The constructor parameters have the following constraints:
- `text`: Must be convertible to Unicode string via `to_unicode()` function
- `tokenizer`: Must be a valid tokenizer object with a `to_words()` method
- `is_heading`: Optional boolean parameter with default value False

Class invariants:
- The `_text` field is always stored in Unicode format and stripped of whitespace
- The `_is_heading` field is always a boolean value
- Word tokenization results are cached and remain consistent for the lifetime of the instance

## Lifecycle:
Creation: Instantiate using `Sentence(text, tokenizer, is_heading=False)` where:
- `text` is the textual content (converted to Unicode and stripped)
- `tokenizer` is a valid tokenizer object
- `is_heading` is an optional boolean flag

Usage: Access properties like `words` (cached), `is_heading`, and use comparison operators (`==`, `!=`). The `words` property triggers tokenization on first access and caches the result.

Destruction: No explicit cleanup required; Python's garbage collector handles memory management.

## Method Map:
```mermaid
graph TD
    A[Constructor] --> B[Set _text, _tokenizer, _is_heading]
    B --> C[words property]
    C --> D[to_words() call]
    D --> E[Cached result]
    A --> F[is_heading property]
    F --> G[Return _is_heading]
    A --> H[__eq__ method]
    H --> I[Compare _is_heading and _text]
    A --> J[__hash__ method]
    J --> K[Hash tuple (_is_heading, _text)]
    A --> L[__unicode__ method]
    L --> M[Return _text]
    A --> N[__repr__ method]
    N --> O[Return formatted string]
```

## Raises:
- `AssertionError`: In `__eq__` method when comparing with non-Sentence objects
- `UnicodeDecodeError`: Potentially raised by `to_unicode()` during initialization if text contains invalid UTF-8 sequences

## Example:
```python
# Create a sentence instance
sentence = Sentence("Hello world!", tokenizer_instance, is_heading=False)

# Access word tokens (triggers tokenization on first access)
word_list = sentence.words  # Returns tokenized words

# Check if it's a heading
is_heading = sentence.is_heading  # Returns False

# Compare sentences
other_sentence = Sentence("Hello world!", tokenizer_instance, is_heading=False)
are_equal = sentence == other_sentence  # True

# String representation
repr_str = repr(sentence)  # "<Sentence: Hello world!>"
```

### `sumy.models.dom._sentence.Sentence.__init__` · *method*

## Summary:
Initializes a Sentence object with text content, tokenizer, and heading status.

## Description:
Constructs a Sentence instance by normalizing the input text to Unicode, storing the provided tokenizer, and setting the heading flag. This method serves as the primary constructor for Sentence objects within the DOM model, preparing the object's internal state for subsequent text processing operations.

## Args:
    text (Any): The raw text content for the sentence, which will be converted to Unicode and stripped of leading/trailing whitespace.
    tokenizer (Any): A tokenizer object used for tokenizing the sentence text during processing.
    is_heading (bool, optional): Flag indicating whether this sentence represents a heading. Defaults to False.

## Returns:
    None: This method does not return a value.

## Raises:
    UnicodeDecodeError: When the text parameter contains invalid UTF-8 sequences that cannot be decoded.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._text: Stores the Unicode-normalized and stripped text content
    - self._tokenizer: Stores the provided tokenizer object
    - self._is_heading: Stores the boolean heading status

## Constraints:
    - Preconditions: The text parameter must be convertible to a Unicode string
    - Postconditions: The self._text attribute contains a stripped Unicode string, self._tokenizer contains the provided tokenizer, and self._is_heading contains a boolean value

## Side Effects:
    - Invokes to_unicode() function which may decode bytes objects
    - Calls bool() conversion on is_heading parameter

### `sumy.models.dom._sentence.Sentence.words` · *method*

## Summary:
Returns a tuple of word tokens extracted from the sentence's text using the assigned tokenizer.

## Description:
This property method provides access to the word tokens of a sentence by leveraging the associated tokenizer's `to_words` method. It is designed to be a cached property, ensuring efficient repeated access without redundant processing. The method is typically invoked during text analysis and summarization pipelines where individual word tokens are needed for further processing such as frequency analysis or similarity calculations.

## Args:
    None

## Returns:
    tuple[str]: A tuple containing word tokens extracted from the sentence's text. Words are filtered to exclude non-word tokens based on the tokenizer's word pattern matching.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._text, self._tokenizer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The sentence instance must have valid `_text` and `_tokenizer` attributes initialized during construction.
    Postconditions: The returned tuple contains only valid word tokens as determined by the tokenizer's filtering mechanism.

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.is_heading` · *method*

## Summary:
Returns the boolean flag indicating whether this sentence represents a heading element.

## Description:
This property method provides read-only access to the internal `_is_heading` attribute that determines if the sentence instance corresponds to a heading in the document structure. It is used primarily during document processing and analysis to distinguish between regular text content and heading elements.

The method is implemented as a simple property getter that directly returns the internal boolean flag. This design choice allows for clean encapsulation while providing efficient access to the heading status without additional computation.

## Args:
    None

## Returns:
    bool: True if the sentence represents a heading element, False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: self._is_heading
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Sentence instance must be properly initialized with a valid `_is_heading` attribute.
    Postconditions: The returned value is always a boolean representing the heading status.

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__eq__` · *method*

## Summary:
Compares two sentence objects for equality based on their heading status and text content.

## Description:
This method implements the equality comparison operator (`==`) for Sentence objects. It is designed to determine if two sentences are equivalent by checking both their heading status and textual content. The method is part of the Sentence class's standard comparison protocol and ensures that two sentences are considered equal only when they have identical heading flags and text content.

## Args:
    sentence (Sentence): Another Sentence instance to compare against this object.

## Returns:
    bool: True if both the `_is_heading` flag and `_text` content are identical between the two sentences; False otherwise.

## Raises:
    AssertionError: When the provided argument is not an instance of the Sentence class.

## State Changes:
    Attributes READ: 
        - self._is_heading
        - self._text
        - sentence._is_heading
        - sentence._text

## Constraints:
    Preconditions:
        - The input parameter `sentence` must be an instance of the Sentence class.
    Postconditions:
        - The method returns a boolean value indicating equality of the two sentence objects.
        - The comparison is based solely on the `_is_heading` attribute and `_text` attribute.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only compares internal attributes of the objects.

### `sumy.models.dom._sentence.Sentence.__ne__` · *method*

## Summary:
Implements the inequality comparison operator for Sentence objects by negating the equality check result.

## Description:
This method defines the behavior of the `!=` operator when comparing two Sentence objects. It leverages the existing `__eq__` method to determine equality and returns the logical negation of that result. This approach ensures consistency between equality and inequality operations while maintaining the standard Python comparison semantics.

## Args:
    sentence (Sentence): Another Sentence object to compare against this instance

## Returns:
    bool: True if the sentences are not equal, False if they are equal

## Raises:
    AssertionError: When the provided argument is not an instance of Sentence class

## State Changes:
    Attributes READ: _is_heading, _text
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The argument must be an instance of Sentence class
    Postconditions: Returns a boolean value indicating inequality between the two objects

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__hash__` · *method*

## Summary:
Computes and returns a hash value for the sentence based on its heading status and text content.

## Description:
This method implements the `__hash__` special method to enable hashing of Sentence objects. It is used primarily for storing sentences in hash-based collections like sets and dictionaries. The hash is computed using a tuple containing the sentence's heading status and text content.

## Args:
    None

## Returns:
    int: An integer hash value uniquely representing the combination of the sentence's heading status and text content.

## Raises:
    TypeError: If either `self._is_heading` or `self._text` is not hashable.

## State Changes:
    Attributes READ: 
    - self._is_heading: Boolean indicating if the sentence is a heading
    - self._text: String containing the sentence text content

## Constraints:
    Preconditions:
    - The sentence object must have valid `_is_heading` and `_text` attributes
    - Both attributes should be hashable types (boolean and string respectively)

    Postconditions:
    - The returned hash value remains consistent for the same combination of `_is_heading` and `_text`
    - Hash values should be unique for different combinations of these attributes

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__unicode__` · *method*

## Summary:
Returns the Unicode representation of the sentence by returning its internal text field.

## Description:
This method provides a string representation of the sentence object by accessing its internal `_text` attribute. It is typically called during string conversion operations or when the object needs to be displayed as a Unicode string. The method serves as a standard interface for retrieving the sentence's textual content in Unicode format.

## Args:
    None

## Returns:
    str: The Unicode string representation of the sentence, which is the value stored in the `_text` attribute.

## Raises:
    None

## State Changes:
    Attributes READ: self._text
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `_text` attribute must be initialized and contain a valid string value.
    Postconditions: The returned value is guaranteed to be a Unicode string representing the sentence content.

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__repr__` · *method*

## Summary:
Returns a string representation of the sentence object that clearly identifies it as either a heading or regular sentence, including its textual content.

## Description:
This method provides a standardized string representation for Sentence objects that distinguishes between headings and regular sentences. It is automatically invoked when the object needs to be displayed or converted to a string, such as in debugging contexts or when printing the object. The method leverages the `_is_heading` attribute to determine the object type and uses `__str__()` to retrieve the textual content. In Python 2, `__str__()` typically calls `__unicode__()` and encodes to bytes, while in Python 3, `__str__()` is the primary string representation method.

## Args:
    None

## Returns:
    str: A formatted string in the pattern "<Type: Text>" where Type is either "Heading" or "Sentence" and Text is the textual content of the sentence.

## Raises:
    None

## State Changes:
    - Attributes READ: self._is_heading, self._text
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: The object must be properly initialized with valid values for _is_heading and _text
    - Postconditions: The returned string follows a consistent format for all Sentence instances

## Side Effects:
    - Invokes the __str__() method of the object (which in turn calls __unicode__() in Python 2)
    - Calls to_string() function for cross-version string compatibility

