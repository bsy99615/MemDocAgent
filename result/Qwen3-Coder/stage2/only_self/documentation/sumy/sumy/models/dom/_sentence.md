# `_sentence.py`

## `sumy.models.dom._sentence.Sentence` · *class*

## Summary:
Represents a text sentence or heading with tokenized word access and equality comparison capabilities.

## Description:
The Sentence class encapsulates a textual segment (either a regular sentence or a heading) and provides efficient access to its constituent words through tokenization. It's designed to be immutable once created and supports equality comparison based on text content and heading status. The class leverages caching for efficient word access and follows Python 2/3 compatibility patterns.

This abstraction separates text content from processing logic, making it suitable for text summarization and natural language processing tasks where sentences need to be compared, processed, or analyzed independently.

## State:
- `_text` (str): The raw Unicode text content of the sentence, stripped of leading/trailing whitespace
- `_cached_property_words` (list[str]): Cached list of words obtained from tokenization, automatically computed on first access
- `_tokenizer` (Tokenizer): Tokenizer instance used to convert text to words
- `_is_heading` (bool): Boolean flag indicating whether this sentence represents a heading

## Lifecycle:
- Creation: Instantiate with text content, tokenizer, and optional heading flag
- Usage: Access `words` property for tokenized content, compare with `==` operator, or use in hash-based collections
- Destruction: Automatic cleanup through Python's garbage collection

## Method Map:
```mermaid
flowchart TD
    A[Create Sentence] --> B{Access words property}
    B --> C[Call tokenizer.to_words()]
    C --> D[Cache result in _cached_property_words]
    D --> E[Return cached words]
    
    A --> F[Compare with ==]
    F --> G[Check _is_heading and _text equality]
    
    A --> H[Hash calculation]
    H --> I[Hash (_is_heading, _text)]
```

## Raises:
- None explicitly raised during initialization
- `AssertionError` may be raised during equality comparison if comparing with non-Sentence objects

## Example:
```python
# Create a sentence
sentence = Sentence("Hello world!", tokenizer_instance, is_heading=False)

# Access words (computed and cached on first access)
word_list = sentence.words  # Returns ['Hello', 'world!']

# Check if it's a heading
print(sentence.is_heading)  # False

# Compare sentences
other_sentence = Sentence("Hello world!", tokenizer_instance, is_heading=False)
print(sentence == other_sentence)  # True

# Create a heading
heading = Sentence("Introduction", tokenizer_instance, is_heading=True)
print(heading.is_heading)  # True
```

### `sumy.models.dom._sentence.Sentence.__init__` · *method*

## Summary:
Initializes a Sentence object with text content, tokenizer, and heading status.

## Description:
Constructs a Sentence instance by storing the provided text after Unicode conversion and stripping, the tokenizer for text processing, and a boolean flag indicating if the sentence is a heading. This method serves as the primary constructor for Sentence objects within the DOM model hierarchy.

## Args:
    text (str): The textual content of the sentence, which will be converted to Unicode and stripped of leading/trailing whitespace.
    tokenizer (object): A tokenizer object used for processing the sentence text, typically for tokenization or parsing operations.
    is_heading (bool, optional): Flag indicating whether this sentence represents a heading element. Defaults to False.

## Returns:
    None: This method initializes instance attributes but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying conversions may raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._text: Stores the Unicode-converted and stripped text content
    - self._tokenizer: Stores the provided tokenizer object
    - self._is_heading: Stores the boolean representation of the heading flag

## Constraints:
    Preconditions:
    - text should be convertible to Unicode string
    - tokenizer should be a valid object suitable for text processing
    - is_heading should be convertible to boolean
    
    Postconditions:
    - self._text contains the Unicode-converted and stripped text
    - self._tokenizer contains the provided tokenizer object
    - self._is_heading contains a boolean value representing heading status

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes instance attributes.

### `sumy.models.dom._sentence.Sentence.words` · *method*

## Summary:
Returns a cached list of word tokens extracted from the sentence's text content.

## Description:
Provides access to the word tokens derived from the sentence's text using the assigned tokenizer. This property implements a cached retrieval mechanism that stores the tokenized result after the first access, preventing redundant processing of identical text content.

The method delegates the actual tokenization to the assigned tokenizer's `to_words` method. This property is typically accessed during text processing pipelines where word-level analysis is required.

## Args:
    None: This is a property getter with no parameters.

## Returns:
    list[str]: A list of word tokens extracted from the sentence's text content. The exact format depends on the tokenizer implementation. Subsequent calls return the same cached list.

## Raises:
    AttributeError: If `self._tokenizer` or `self._text` attributes are not properly initialized, or if the tokenizer lacks a `to_words` method.

## State Changes:
    Attributes READ: 
    - self._tokenizer: Accessed to call its `to_words` method
    - self._text: Passed as input to the tokenizer's `to_words` method
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Sentence instance must have been properly initialized with valid `_text` and `_tokenizer` attributes
    - The `_tokenizer` attribute must have a callable `to_words` method
    
    Postconditions:
    - The returned list of words is cached for subsequent accesses
    - The method will always return the same list of words for the same sentence content

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only accesses internal attributes and calls methods on the tokenizer object.

### `sumy.models.dom._sentence.Sentence.is_heading` · *method*

## Summary:
Returns whether this sentence is classified as a heading element.

## Description:
This property provides read-only access to the internal `_is_heading` flag that determines if the sentence represents a heading in the document structure. It is used to distinguish between regular text sentences and heading elements during document processing and analysis.

## Args:
    None

## Returns:
    bool: True if the sentence is a heading, False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: self._is_heading
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Sentence object must be properly initialized with a valid `_is_heading` value.
    Postconditions: The returned value is always a boolean representing the heading status.

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__eq__` · *method*

## Summary:
Compares two Sentence objects for equality based on heading status and text content.

## Description:
Implements the equality comparison operator (==) for Sentence objects. This method determines if two Sentence instances are equivalent by comparing their heading status (`_is_heading`) and text content (`_text`). It is automatically invoked when using the == operator between Sentence objects and is part of Python's object comparison protocol.

## Args:
    sentence (Sentence): Another Sentence object to compare against this instance.

## Returns:
    bool: True if both sentences have identical `_is_heading` status and `_text` content; False otherwise.

## Raises:
    AssertionError: When the provided argument is not an instance of Sentence class.

## State Changes:
    Attributes READ: 
    - self._is_heading: Reads the heading status of this sentence
    - self._text: Reads the text content of this sentence
    - sentence._is_heading: Reads the heading status of the compared sentence
    - sentence._text: Reads the text content of the compared sentence
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The argument must be an instance of Sentence class (checked via assertion)
    - Both sentences must have comparable text and heading status
    
    Postconditions:
    - Returns a boolean value indicating equality of the two sentences
    - Does not modify either sentence object's state

## Side Effects:
    None: This method performs no I/O operations, external service calls, or mutations to objects outside self.

### `sumy.models.dom._sentence.Sentence.__ne__` · *method*

## Summary:
Implements the "not equal" comparison operator for Sentence objects, returning True when two sentences are not identical.

## Description:
This method defines the behavior of the `!=` operator for Sentence instances. It returns True if the current sentence differs from the provided sentence in either text content or heading status, and False if they are identical. The method delegates to the `__eq__` method and negates its result to determine inequality.

## Args:
    sentence (Sentence): Another Sentence object to compare against for inequality

## Returns:
    bool: True if the sentences differ in text content or heading status; False if they are identical

## Raises:
    AssertionError: When the provided argument is not an instance of Sentence class

## State Changes:
    Attributes READ: 
    - self._is_heading: Used to compare heading status
    - self._text: Used to compare text content

## Constraints:
    Preconditions:
    - The input parameter must be an instance of Sentence class
    - Both sentences must have compatible text representations
    
    Postconditions:
    - Returns a boolean value indicating inequality between sentences
    - The comparison is symmetric: sentence_a != sentence_b is equivalent to sentence_b != sentence_a

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__hash__` · *method*

## Summary:
Computes and returns a hash value based on the sentence's heading status and text content.

## Description:
Implements Python's magic method for object hashing, enabling Sentence instances to be used in hash-based collections like sets and as dictionary keys. This method generates a hash from a tuple containing the sentence's heading status (`_is_heading`) and text content (`_text`), ensuring consistency with the `__eq__` method which performs identical comparisons.

## Args:
    None: This method takes no arguments beyond the implicit `self` parameter.

## Returns:
    int: An integer hash value uniquely representing this sentence's state.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: 
    - self._is_heading: Reads the heading status flag
    - self._text: Reads the text content of the sentence

## Constraints:
    Preconditions:
    - The object must be properly initialized with `_is_heading` and `_text` attributes
    - The `_is_heading` attribute must be boolean convertible
    - The `_text` attribute must be hashable (typically string-like)
    
    Postconditions:
    - Returns a consistent hash value for equivalent Sentence objects
    - Hash value remains stable throughout the object's lifetime

## Side Effects:
    None: This method performs no I/O operations, external service calls, or mutations to objects outside self.

### `sumy.models.dom._sentence.Sentence.__unicode__` · *method*

## Summary:
Returns the Unicode string representation of the sentence's text content.

## Description:
This method provides the Unicode string representation of the sentence by returning its internal `_text` attribute. It's part of the Python 2/3 compatibility layer that ensures consistent string handling across different Python versions. The method is typically called indirectly through Python's built-in string conversion mechanisms or when the `unicode()` function is applied to a Sentence object.

This method serves as a core interface for accessing the textual content of a sentence in Unicode format, making it suitable for display, processing, and comparison operations while maintaining cross-version compatibility.

## Args:
    None

## Returns:
    str: A Unicode string containing the sentence's text content without leading/trailing whitespace.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self._text: The internal text content of the sentence, stored as a Unicode string

## Constraints:
    Preconditions:
    - The Sentence object must be properly initialized with a valid `_text` attribute
    - The `_text` attribute must contain a Unicode string representation of the sentence content
    
    Postconditions:
    - Returns a Unicode string representation of the sentence's text content
    - The returned string contains the original text with leading/trailing whitespace stripped

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__repr__` · *method*

## Summary:
Returns a string representation identifying the sentence type (Heading or Sentence) and its content.

## Description:
This method implements the standard Python `__repr__` protocol to provide a clear, unambiguous string representation of a Sentence object. It's primarily intended for debugging and development purposes, allowing developers to quickly distinguish between regular sentences and heading sentences in the DOM tree structure.

The representation format is "<Heading: content>" or "<Sentence: content>", where "content" represents the textual content of the sentence. This helps differentiate heading elements from regular text elements during debugging sessions.

## Args:
    None

## Returns:
    str: A formatted string representation in the form "<Heading: content>" or "<Sentence: content>" where content is the textual content of the sentence.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self._is_heading: Determines whether to label as "Heading" or "Sentence"
    - self._text: Accessed through the __str__ method to obtain content representation

## Constraints:
    Preconditions:
    - The object must be properly initialized with valid _text and _is_heading attributes
    - The __str__ method must be callable and return a meaningful string representation of the sentence's text
    
    Postconditions:
    - Returns a consistent string format for debugging purposes
    - The returned string clearly identifies the sentence type and content

## Side Effects:
    None

