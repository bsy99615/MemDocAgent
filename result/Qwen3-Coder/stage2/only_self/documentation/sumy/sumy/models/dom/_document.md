# `_document.py`

## `sumy.models.dom._document.ObjectDocumentModel` · *class*

## Summary:
Represents a document model that aggregates content from multiple paragraphs into unified collections of sentences, headings, and words.

## Description:
The ObjectDocumentModel serves as a container for document paragraphs and provides convenient access to aggregated content across all paragraphs. It's designed to be a lightweight wrapper that enables efficient access to document components without requiring manual iteration over individual paragraphs.

This class is typically instantiated by document processing pipelines that have already parsed text into paragraph objects. The class enforces a clean abstraction boundary between paragraph-level data structures and document-level aggregations.

## State:
- `_paragraphs`: tuple of paragraph objects, immutable after initialization
- `paragraphs`: property returning the stored paragraphs tuple
- `sentences`: cached property returning flattened sentences from all paragraphs
- `headings`: cached property returning flattened headings from all paragraphs  
- `words`: cached property returning flattened words from all paragraphs

The class maintains the invariant that `_paragraphs` is always a tuple of paragraph objects, and all cached properties are computed lazily and memoized.

## Lifecycle:
- Creation: Instantiate with an iterable of paragraph objects
- Usage: Access `paragraphs`, `sentences`, `headings`, or `words` properties as needed
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
- However, passing a non-iterable or iterable containing non-paragraph objects could cause runtime errors in property access methods

## Example:
```python
# Create with paragraph objects
paragraphs = [Paragraph(...), Paragraph(...)]
doc_model = ObjectDocumentModel(paragraphs)

# Access aggregated content
all_sentences = doc_model.sentences
all_headings = doc_model.headings
all_words = doc_model.words
```

### `sumy.models.dom._document.ObjectDocumentModel.__init__` · *method*

## Summary:
Initializes an ObjectDocumentModel with a collection of paragraph objects, storing them as an immutable tuple for efficient access.

## Description:
The constructor accepts an iterable of paragraph objects and stores them internally as a tuple. This design ensures the document's paragraph structure remains immutable after initialization, providing consistency for cached property computations and preventing accidental modification of the document's foundational data.

This method is typically called during document processing pipelines when text has been parsed into paragraph objects but before any aggregation operations are performed on the document content.

The separation of initialization logic into its own method allows for clean instantiation while keeping the rest of the class focused on providing aggregated views of the document content through properties like sentences, headings, and words.

## Args:
    paragraphs (Iterable[Paragraph]): An iterable collection of paragraph objects that constitute the document. Each item must be a valid Paragraph instance.

## Returns:
    None: This method initializes the object's internal state but does not return a value.

## Raises:
    None explicitly raised in this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._paragraphs

## Constraints:
    Preconditions:
    - The `paragraphs` parameter must be iterable
    - Each item in the `paragraphs` iterable must be a valid Paragraph object
    - The method assumes the caller has already processed text into appropriate paragraph structures
    
    Postconditions:
    - The internal `_paragraphs` attribute is set to a tuple containing all provided paragraph objects
    - The tuple is immutable and cannot be modified after initialization
    - The order of paragraphs is preserved from the input iterable

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.paragraphs` · *method*

## Summary:
Returns the tuple of paragraph objects that make up this document model.

## Description:
This property provides read-only access to the internal collection of paragraph objects that constitute the document model. It serves as a clean interface to access the document's structural components without exposing the internal implementation details.

The method is implemented as a simple property that directly returns the internal `_paragraphs` attribute, making it a straightforward accessor for the document's paragraph collection.

## Args:
    None

## Returns:
    tuple[Paragraph]: A tuple containing all Paragraph objects that make up this document model. Returns an empty tuple if the document contains no paragraphs.

## Raises:
    None

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The ObjectDocumentModel instance must be properly initialized
    - The `_paragraphs` attribute must be set to a tuple of Paragraph objects
    
    Postconditions:
    - Returns the exact same tuple object that was stored in `self._paragraphs`
    - The returned tuple is immutable and represents the document's paragraph structure at the time of access

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.sentences` · *method*

## Summary:
Returns a flattened tuple containing all sentences from all paragraphs in the document.

## Description:
This cached property aggregates sentences from all paragraphs stored in the document model. It's designed to provide efficient access to all textual sentences in the document without requiring manual iteration over paragraphs.

## Args:
    None

## Returns:
    tuple: A tuple containing all sentences from all paragraphs in the document, flattened into a single sequence.

## Raises:
    None

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self._paragraphs must be initialized and contain paragraph objects
    - Each paragraph object must have a sentences property that returns an iterable
    
    Postconditions:
    - Returns a tuple of sentences (immutable sequence)
    - Result is cached after first access for performance

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.headings` · *method*

## Summary:
Returns a flattened tuple of all heading sentences from all paragraphs in the document model.

## Description:
Extracts and combines all heading sentences from each paragraph in the document model into a single tuple. This method provides a convenient way to access all headings in the document regardless of which paragraph they appear in.

The method is implemented as a cached property, ensuring efficient repeated access without recomputation.

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
    Preconditions: 
    - self._paragraphs must be initialized and contain only Paragraph objects
    - Each Paragraph object must have a valid headings property that returns an iterable of Sentence objects
    
    Postconditions:
    - Returns a tuple of Sentence objects where each sentence has is_heading=True
    - The returned tuple maintains the order of paragraphs and sentences as they appear in the document

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.words` · *method*

## Summary:
Returns a flattened tuple containing all words from all paragraphs in the document.

## Description:
This method aggregates words from all paragraphs stored in the document model into a single flat tuple. It's designed to provide easy access to all textual content in word form for processing and analysis.

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
    - self._paragraphs must be iterable
    - Each item in self._paragraphs must have a .words property that returns an iterable
    Postconditions:
    - Returns a tuple of strings
    - All words from all paragraphs are included exactly once

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.__unicode__` · *method*

## Summary:
Returns a human-readable string representation of the document model showing paragraph count.

## Description:
Provides a string representation of the ObjectDocumentModel instance that displays the total number of paragraphs in the document. This method is primarily intended for debugging and development purposes, offering a quick visual indication of document structure.

The method is automatically called when:
- `str()` or `unicode()` is invoked on an ObjectDocumentModel instance
- The object is printed or displayed in interactive environments
- The `__repr__` method delegates to this method

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
    Preconditions: The object must be properly initialized with a valid list/tuple of paragraph objects
    Postconditions: The returned string provides a meaningful representation of the document model's structure

## Side Effects:
    None

### `sumy.models.dom._document.ObjectDocumentModel.__repr__` · *method*

## Summary:
Returns a string representation of the document model object for debugging purposes.

## Description:
This method provides a string representation of the ObjectDocumentModel instance, primarily intended for debugging and development purposes. It delegates to the object's `__str__` method, which should return a human-readable representation of the document model.

## Args:
    None

## Returns:
    str: A string representation of the document model object, typically showing the document structure and paragraph count.

## Raises:
    AttributeError: If the object's `__str__` method is not callable or does not exist.

## State Changes:
    Attributes READ: self._paragraphs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be properly initialized with a valid list/tuple of paragraph objects
    Postconditions: The returned string provides a meaningful representation of the document model's structure

## Side Effects:
    None

