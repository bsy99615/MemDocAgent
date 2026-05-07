# `_document.py`

## `sumy.models.dom._document.ObjectDocumentModel` · *class*

## Summary:
Container for document structure that aggregates content from multiple paragraph objects.

## Description:
ObjectDocumentModel serves as a wrapper around multiple paragraph objects, providing unified access to document elements. It's typically created by document parsing systems that process raw text into structured paragraph representations. The class enables efficient access to document components while leveraging lazy evaluation for performance optimization.

## State:
- `_paragraphs`: tuple of paragraph objects, immutable after initialization
- `paragraphs`: property returning the stored paragraphs tuple
- `sentences`: cached property returning flattened content from all paragraphs
- `headings`: cached property returning flattened content from all paragraphs  
- `words`: cached property returning flattened content from all paragraphs

The class maintains that `_paragraphs` is always a tuple of paragraph objects, and cached properties are computed once and memoized upon first access.

## Lifecycle:
- Creation: Instantiate with an iterable of paragraph objects
- Usage: Access properties in any order; sentences, headings, and words are computed once and cached on first access
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[ObjectDocumentModel.__init__] --> B[Store paragraphs as tuple]
    B --> C[ObjectDocumentModel.paragraphs]
    B --> D[ObjectDocumentModel.sentences]
    B --> E[ObjectDocumentModel.headings]
    B --> F[ObjectDocumentModel.words]
    D --> G[chain(*sentences)]
    E --> H[chain(*headings)]
    F --> I[chain(*words)]
```

## Raises:
- None explicitly raised in __init__
- Any exceptions would stem from the paragraph objects when accessing their properties

## Example:
```python
# Create paragraphs (assumed to exist)
paragraphs = [paragraph1, paragraph2, paragraph3]

# Instantiate the document model
doc_model = ObjectDocumentModel(paragraphs)

# Access document elements
print(doc_model.paragraphs)  # Returns tuple of paragraphs
print(doc_model.sentences)   # Returns flattened sentences from all paragraphs (computed once)
print(doc_model.headings)    # Returns flattened headings from all paragraphs (computed once)
print(doc_model.words)       # Returns flattened words from all paragraphs (computed once)
print(repr(doc_model))       # "<DOM with 3 paragraphs>"
```

### `sumy.models.dom._document.ObjectDocumentModel.__init__` · *method*

## Summary:
Initializes an ObjectDocumentModel instance by storing the provided paragraphs as an immutable tuple.

## Description:
This constructor method initializes an ObjectDocumentModel instance by converting the input paragraphs into an immutable tuple for storage. The ObjectDocumentModel represents a document structure composed of multiple paragraphs, where each paragraph is typically a text segment or content unit. This implementation ensures immutability of the paragraph collection after initialization, preventing accidental modification of the document structure.

## Args:
    paragraphs (iterable): An iterable of paragraph objects that constitute the document content. These are typically text segments or paragraph representations that form the structural units of the document.

## Returns:
    None: This method initializes the object state but does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._paragraphs - stores the input paragraphs as an immutable tuple

## Constraints:
    Preconditions: The paragraphs parameter must be iterable and convertible to a tuple
    Postconditions: The self._paragraphs attribute will contain an immutable tuple of the input paragraphs

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only stores data locally.

### `sumy.models.dom._document.ObjectDocumentModel.paragraphs` · *method*

## Summary:
Returns the tuple of paragraph objects stored in this document model.

## Description:
Provides access to the immutable collection of paragraph objects that constitute the document model. This property serves as a read-only interface to the internal `_paragraphs` storage, allowing external code to retrieve all paragraphs without modifying the document structure.

## Args:
    None

## Returns:
    tuple: An immutable tuple containing all paragraph objects in the document model. Each paragraph object maintains its original type and structure as defined by the paragraph implementation.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The document model must have been properly initialized with a sequence of paragraph objects
    - The `_paragraphs` attribute must be set to a tuple of paragraph objects
    
    Postconditions:
    - Returns an immutable tuple containing all paragraph objects
    - The returned tuple is identical to the internal storage and should not be modified externally

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.sentences` · *method*

## Summary:
Returns a flattened tuple containing all sentences from all paragraphs in the document.

## Description:
This method aggregates sentences from all paragraphs in the document into a single tuple. It accesses the `_paragraphs` attribute to retrieve sentences from each paragraph and flattens them using `itertools.chain`. The result is cached using the `cached_property` decorator to avoid recomputation on subsequent calls.

## Args:
    None

## Returns:
    tuple[str]: A tuple containing all sentences from all paragraphs in the document, in order.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have a `_paragraphs` attribute containing paragraph objects with a `sentences` property
    Postconditions: Returns a tuple of strings representing all sentences in the document

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.headings` · *method*

## Summary:
Returns a flattened tuple of all heading elements from all paragraphs in the document model.

## Description:
Extracts and combines all heading elements from each paragraph in the document model into a single tuple. This method is implemented as a cached property, ensuring the computation is performed only once and the result is reused for subsequent calls.

## Args:
    None

## Returns:
    tuple: A tuple containing all heading elements from all paragraphs in the document. Each heading element maintains its original type and structure as defined by individual paragraph implementations.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The document model must have been initialized with a sequence of paragraph objects
    - Each paragraph object in self._paragraphs must have a valid 'headings' property that returns an iterable
    
    Postconditions:
    - Returns a tuple containing all heading elements from all paragraphs
    - The returned tuple is immutable and cached for performance

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.words` · *method*

## Summary:
Returns a flattened tuple containing all words from all paragraphs in the document model.

## Description:
This method aggregates all words from every paragraph in the document model into a single flat tuple. It's designed as a convenience property to provide easy access to all textual words in the document without having to manually iterate through paragraphs and their constituent sentences.

The method is implemented as a cached property, meaning it computes the result once and caches it for subsequent calls. This optimization is important because extracting words from all sentences across all paragraphs can be computationally expensive.

## Args:
    None

## Returns:
    tuple[str]: A flat tuple containing all words from all paragraphs in the document, in order of appearance.

## Raises:
    None

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self._paragraphs must be initialized and contain only Paragraph objects
    - Each Paragraph object must have a valid words property that returns a tuple of strings
    
    Postconditions:
    - Returns a tuple of strings representing all words in the document
    - The returned tuple maintains the sequential order of words as they appear in the original document

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.__unicode__` · *method*

## Summary:
Returns a string representation of the document model showing the number of paragraphs it contains.

## Description:
This method implements the `__unicode__` magic method to provide a human-readable string representation of the ObjectDocumentModel instance. It displays the total number of paragraphs in the document, making it easier to identify and debug document instances.

## Args:
    None

## Returns:
    str: A formatted string in the format "<DOM with X paragraphs>" where X is the number of paragraphs in the document.

## Raises:
    None

## State Changes:
    Attributes READ: self.paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have a `paragraphs` attribute that supports the `len()` function.
    Postconditions: The returned string is always in the format "<DOM with X paragraphs>" where X is the length of self.paragraphs.

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.__repr__` · *method*

## Summary:
Returns the string representation of the document object by delegating to the object's `__str__` method.

## Description:
This method provides the official string representation of the `ObjectDocumentModel` instance. It delegates to the object's `__str__` method to produce a human-readable representation. This follows Python conventions where `__repr__` should return an unambiguous representation suitable for debugging and logging.

## Args:
    None

## Returns:
    str: A string representation of the document object, typically containing structural information about the document such as paragraph count.

## Raises:
    None

## State Changes:
    Attributes READ: self (the instance itself)
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have a valid `__str__` method implemented
    Postconditions: The returned string accurately represents the object's state

## Side Effects:
    None

