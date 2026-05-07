# `_sentence.py`

## `sumy.models.dom._sentence.Sentence` · *class*

*No documentation generated.*

### `sumy.models.dom._sentence.Sentence.__init__` · *method*

## Summary:
Initializes a Sentence object with text content, tokenizer, and heading status.

## Description:
Constructs a Sentence instance by storing the provided text after Unicode conversion and stripping, the tokenizer for text processing, and a boolean flag indicating if the sentence is a heading. This method prepares the fundamental attributes required for sentence representation in the document object model.

## Args:
    text (str or bytes): The textual content of the sentence, which will be converted to Unicode and stripped of leading/trailing whitespace.
    tokenizer: An object responsible for tokenizing text, likely used for further processing of the sentence content.
    is_heading (bool, optional): Flag indicating whether this sentence represents a heading section. Defaults to False.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying operations like to_unicode() may raise exceptions for invalid inputs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._text: Stores the Unicode-converted and stripped text content
    - self._tokenizer: Stores the provided tokenizer object
    - self._is_heading: Stores the boolean heading status

## Constraints:
    Preconditions:
    - The text parameter should be convertible to Unicode string
    - The tokenizer parameter should be a valid object for text processing
    - The is_heading parameter should be convertible to boolean
    
    Postconditions:
    - self._text contains the Unicode-converted and stripped text
    - self._tokenizer contains the provided tokenizer object
    - self._is_heading contains a boolean value representing heading status

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only assigns values to instance attributes.

### `sumy.models.dom._sentence.Sentence.words` · *method*

## Summary:
Returns a list of words tokenized from the sentence's text content.

## Description:
Provides access to the tokenized representation of the sentence's text. This property is cached to avoid repeated tokenization operations, making subsequent accesses more efficient. The method delegates to the associated tokenizer to perform the actual word extraction process.

## Args:
    None

## Returns:
    list[str]: A list of string tokens representing the words in the sentence. The exact format and content depends on the implementation of the associated tokenizer's `to_words` method.

## Raises:
    AttributeError: If `self._tokenizer` or `self._text` are not properly initialized on the Sentence instance.

## State Changes:
    Attributes READ: 
    - self._text: The raw text content of the sentence
    - self._tokenizer: The tokenizer object used to tokenize the text
    
    Attributes WRITTEN: 
    - None (this is a property, not a method that modifies state)

## Constraints:
    Preconditions:
    - The Sentence instance must have been properly initialized with valid `_text` and `_tokenizer` attributes
    - Both `self._text` and `self._tokenizer` must be non-None values
    
    Postconditions:
    - Returns a list of strings representing the tokenized words
    - The returned list is cached after first access for performance optimization

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.is_heading` · *method*

## Summary:
Returns whether this sentence represents a heading element in the document structure.

## Description:
This property provides read-only access to the internal `_is_heading` flag that indicates whether the sentence should be treated as a heading (such as a title or section header) rather than regular text content. This distinction is important for document analysis and summarization algorithms that need to preserve heading structure when generating summaries.

## Args:
    None

## Returns:
    bool: True if this sentence is a heading, False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: self._is_heading
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Sentence object must be properly initialized with a valid `_is_heading` value.
    Postconditions: The returned value is always a boolean, reflecting the immutable nature of the heading flag.

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__eq__` · *method*

## Summary:
Compares two Sentence objects for equality based on heading status and text content.

## Description:
This method implements the equality operator (`==`) for Sentence objects, determining if two sentences are equivalent based on their heading status and textual content. It is used primarily in data structures that require comparing sentence objects, such as when checking for duplicates or verifying sentence identity in summarization algorithms.

## Args:
    sentence (Sentence): Another Sentence instance to compare against this object.

## Returns:
    bool: True if both sentences have identical `_is_heading` values and `_text` content; False otherwise.

## Raises:
    AssertionError: When the provided argument is not an instance of Sentence class.

## State Changes:
    Attributes READ: 
    - self._is_heading
    - self._text
    - sentence._is_heading
    - sentence._text

## Constraints:
    Preconditions:
    - The argument must be an instance of Sentence class (enforced by assertion)
    - Both objects must be properly initialized Sentence instances

    Postconditions:
    - Returns a boolean value indicating equality of the two Sentence objects
    - The comparison is based solely on the internal state (_is_heading and _text)

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only compares internal attributes of the objects.

### `sumy.models.dom._sentence.Sentence.__ne__` · *method*

## Summary:
Defines the inequality comparison operation between two Sentence objects.

## Description:
This method implements the `!=` operator for Sentence objects by returning the logical negation of the equality comparison. It is automatically called when the `!=` operator is used between two Sentence instances.

## Args:
    sentence (Sentence): Another Sentence object to compare against.

## Returns:
    bool: True if the sentences are not equal, False if they are equal.

## Raises:
    AssertionError: When the provided argument is not an instance of Sentence class.

## State Changes:
    Attributes READ: _is_heading, _text
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The argument must be an instance of Sentence class.
    Postconditions: Returns a boolean value indicating inequality.

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__hash__` · *method*

## Summary:
Computes and returns a hash value based on the sentence's heading status and text content.

## Description:
This method implements the standard Python `__hash__` protocol for the Sentence class, enabling instances to be used as dictionary keys or members of sets. It creates a hash from a tuple containing the sentence's heading status (`_is_heading`) and its text content (`_text`). This implementation ensures consistency with the `__eq__` method, which also compares these same attributes.

## Args:
    None

## Returns:
    int: A hash value computed from the tuple (self._is_heading, self._text)

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self._is_heading: Boolean indicating if the sentence is a heading
    - self._text: String containing the sentence text content

## Constraints:
    Preconditions:
    - The object must be properly initialized with `_is_heading` and `_text` attributes
    - The `_text` attribute should be a string that can be hashed
    - The `_is_heading` attribute should be a boolean that can be hashed
    
    Postconditions:
    - The returned hash value remains consistent for the same object state
    - Objects considered equal by `__eq__` will have identical hash values

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__unicode__` · *method*

## Summary:
Returns the Unicode string representation of the sentence object.

## Description:
This special method provides the Unicode string representation of a Sentence object by returning its underlying text content. It is called automatically when the built-in `unicode()` function is applied to a Sentence instance or when the object is used in string contexts requiring Unicode representation.

## Args:
    None

## Returns:
    unicode: The Unicode string representation of the sentence's text content.

## Raises:
    None

## State Changes:
    Attributes READ: self._text
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Sentence object must be properly initialized with a valid text content stored in self._text.
    Postconditions: The returned value is a Unicode string representing the sentence's text content.

## Side Effects:
    None

### `sumy.models.dom._sentence.Sentence.__repr__` · *method*

## Summary:
Returns a string representation indicating whether this is a heading or regular sentence, followed by its textual content.

## Description:
This method provides a human-readable representation of a Sentence object for debugging and logging purposes. It determines whether the sentence is a heading based on the `_is_heading` attribute and formats the output accordingly. When called, it returns a string that identifies the object type and displays its content.

## Args:
    None

## Returns:
    str: A formatted string in the form "<Heading: text_content>" or "<Sentence: text_content>" where text_content is the Unicode representation of the sentence's text.

## Raises:
    None

## State Changes:
    Attributes READ: self._is_heading, self._text
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be a Sentence instance with valid _is_heading and _text attributes.
    Postconditions: The returned string accurately reflects the sentence type and content.

## Side Effects:
    None

