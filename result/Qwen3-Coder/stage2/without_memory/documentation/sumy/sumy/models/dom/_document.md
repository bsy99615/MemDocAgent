# `_document.py`

## `sumy.models.dom._document.ObjectDocumentModel` · *class*

## Summary:
Object-oriented document model that aggregates content from multiple paragraphs into unified collections of sentences, headings, and words.

## Description:
The ObjectDocumentModel serves as a container for document paragraphs and provides convenient access to aggregated content across all paragraphs. It's designed to be a lightweight wrapper that enables efficient access to document components without requiring explicit iteration over individual paragraphs.

This class is typically instantiated by document processors or parsers that construct document structures from raw text input. It acts as an abstraction layer that allows downstream components to access document content uniformly regardless of internal paragraph structure.

## State:
- `_paragraphs`: tuple of paragraph objects, containing the document's structural units
  - Type: tuple of paragraph objects
  - Valid range: Must contain paragraph objects with `sentences`, `headings`, and `words` attributes
  - Invariant: Once set in __init__, remains immutable

## Lifecycle:
- Creation: Instantiate with an iterable of paragraph objects that have `sentences`, `headings`, and `words` attributes
- Usage: Access aggregated properties (sentences, headings, words) as needed; properties are lazily computed and cached on first access
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[ObjectDocumentModel] --> B[paragraphs]
    A --> C[sentences]
    A --> D[headings]
    A --> E[words]
    C --> F[chain(*paragraph.sentences)]
    D --> G[chain(*paragraph.headings)]
    E --> H[chain(*paragraph.words)]
```

## Raises:
- None explicitly raised in __init__
- However, passing non-iterable or paragraph objects without required attributes may cause AttributeError during property access

## Example:
```python
# Create paragraphs with content
paragraph1 = Paragraph(sentences=[...], headings=[...], words=[...])
paragraph2 = Paragraph(sentences=[...], headings=[...], words=[...])

# Create document model
doc_model = ObjectDocumentModel([paragraph1, paragraph2])

# Access aggregated content (computed lazily on first access)
all_sentences = doc_model.sentences  # Returns tuple of all sentences
all_headings = doc_model.headings     # Returns tuple of all headings  
all_words = doc_model.words           # Returns tuple of all words
```

### `sumy.models.dom._document.ObjectDocumentModel.__init__` · *method*

## Summary:
Initializes the document model with a collection of paragraphs, storing them as an immutable tuple.

## Description:
Constructs an ObjectDocumentModel instance by converting the provided paragraphs iterable into an immutable tuple and storing it as the internal representation of document paragraphs. This method serves as the primary constructor for initializing document models with paragraph data.

## Args:
    paragraphs: An iterable of paragraph objects that will be converted to a tuple and stored internally.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._paragraphs

## Constraints:
    Preconditions: The paragraphs parameter must be iterable and convertible to a tuple.
    Postconditions: The self._paragraphs attribute will contain an immutable tuple representation of the input paragraphs.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `sumy.models.dom._document.ObjectDocumentModel.paragraphs` · *method*

## Summary:
Returns the tuple of paragraph objects that make up this document model.

## Description:
This method provides read-only access to the internal collection of paragraphs stored in the document model. It serves as a property getter that exposes the paragraph data without allowing modification of the internal storage.

## Args:
    None

## Returns:
    tuple: A tuple containing all paragraph objects belonging to this document model. The returned tuple is immutable and represents the complete paragraph structure of the document.

## Raises:
    None

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The ObjectDocumentModel instance must have been properly initialized with a sequence of paragraphs.
    Postconditions: The returned tuple is always the same object reference as stored internally (due to tuple immutability).

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.sentences` · *method*

## Summary:
Returns a flattened tuple of all sentences from all paragraphs in the document.

## Description:
This method aggregates sentences from all paragraphs in the document into a single immutable tuple. As a cached property, it computes the flattened sentence collection only once and caches the result for subsequent accesses, improving performance for repeated invocations.

## Args:
    None

## Returns:
    tuple: A tuple containing all sentences from all paragraphs in the document, flattened into a single sequence.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self._paragraphs must be iterable
    - Each item in self._paragraphs must have a .sentences attribute that is iterable
    Postconditions:
    - Returns a tuple containing all sentences from all paragraphs
    - The result is cached for performance optimization

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.headings` · *method*

## Summary:
Returns a flattened tuple containing all heading sentences from all paragraphs in the document model.

## Description:
Extracts and combines all heading sentences from each paragraph in the document model into a single tuple. This method provides a convenient way to access all headings in the document regardless of which paragraph they appear in. The method is implemented as a cached property, so the result is computed once and then cached for subsequent calls.

## Args:
    None

## Returns:
    tuple[Sentence]: A tuple containing all Sentence objects that represent headings across all paragraphs in the document. Returns an empty tuple if no headings exist.

## Raises:
    None

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have been initialized with a sequence of Paragraph objects, and each Paragraph must have a valid headings property.
    Postconditions: The returned tuple contains only Sentence objects where is_heading is True, and the order preserves the sequential order of paragraphs and sentences within each paragraph.

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.words` · *method*

## Summary:
Returns a flattened tuple containing all words from all paragraphs in the document model.

## Description:
Extracts and concatenates all words from each paragraph stored in the document model. This method provides a convenient way to access all textual content in a single flat structure for processing or analysis.

## Args:
    None

## Returns:
    tuple[str]: A tuple containing all words from all paragraphs in the document, flattened into a single sequence.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self._paragraphs must be iterable containing objects with a 'words' property
    - Each paragraph's 'words' property must return an iterable of strings
    
    Postconditions:
    - Returns a tuple of strings representing all words in the document
    - Order of words preserves the order of paragraphs and words within each paragraph

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.__unicode__` · *method*

## Summary:
Returns a string representation of the document model showing the paragraph count.

## Description:
This method provides a human-readable string representation of the ObjectDocumentModel instance, indicating the total number of paragraphs in the document. It is part of the Python 2/3 compatibility setup using the unicode_compatible decorator.

## Args:
    None

## Returns:
    str: A formatted string in the format "<DOM with X paragraphs>" where X is the number of paragraphs.

## Raises:
    None

## State Changes:
    Attributes READ: self.paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have a paragraphs property that returns an iterable
    Postconditions: The returned string format is consistent and includes the paragraph count

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.__repr__` · *method*

## Summary:
Returns a string representation of the document model by delegating to its string conversion method.

## Description:
This method provides a string representation of the ObjectDocumentModel instance by delegating to the instance's `__str__` method. This is a standard Python convention where `__repr__` delegates to `__str__` to provide a clean string representation of the object.

The implementation is minimal and straightforward: `return self.__str__()`. This indicates that the actual string formatting logic is implemented elsewhere (likely in a parent class or through inheritance) and this method simply exposes that functionality through the standard `__repr__` interface.

## Args:
    None

## Returns:
    str: A string representation of the document model, as determined by the `__str__` method implementation.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._paragraphs (accessed indirectly through the delegated __str__ method)
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The instance must be properly initialized with paragraphs and the `__str__` method must be callable
    Postconditions: Returns a string representation of the document model

## Side Effects:
    None

