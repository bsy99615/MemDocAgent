# `_document.py`

## `sumy.models.dom._document.ObjectDocumentModel` · *class*

*No documentation generated.*

### `sumy.models.dom._document.ObjectDocumentModel.__init__` · *method*

## Summary:
Sets the instance's paragraphs storage to an immutable tuple built from the provided iterable, establishing the instance invariant that paragraphs are accessed through self._paragraphs.

## Description:
This initializer consumes the supplied iterable of paragraph-like objects and stores a tuple snapshot on the new instance. The conversion guarantees a stable, indexable, and immutable container for other methods to rely on.

Known callers:
    - No direct callers were discovered in the provided repository snapshot. In normal use this method is executed automatically when an ObjectDocumentModel is instantiated (during document construction/parsing).

Why this is a separate method:
    - Converting the input to a single, consistent internal representation (tuple) is a fundamental instance creation step. Centralizing it in __init__ ensures all instances begin with the same invariant and avoids repeating this conversion elsewhere.

## Args:
    paragraphs (iterable): Required. Any Python iterable whose elements represent paragraphs (e.g., list, tuple, generator, iterator). The iterable is iterated once to build the internal tuple; elements are preserved in iteration order.

## Returns:
    None: As with all Python __init__ methods, it does not return a value.

## Raises:
    TypeError: Raised if paragraphs is not iterable (for example, passing None or an object that does not implement the iterator protocol) because calling tuple(paragraphs) attempts to iterate it.
    Note: The method does not perform element-level type validation; it will accept any element objects yielded by the iterable.

## State Changes:
    Attributes READ:
        - None (the initializer does not read other instance attributes)
    Attributes WRITTEN:
        - self._paragraphs (tuple): Assigned to tuple(paragraphs). This attribute will exist after __init__ completes.

## Constraints:
    Preconditions:
        - paragraphs must be a Python iterable. If paragraphs is a single-use iterable (e.g., a generator), it will be exhausted by this call.
    Postconditions:
        - self._paragraphs is a tuple containing the elements yielded by iterating the provided paragraphs, in the same order.
        - The tuple contains the same element object references as the iterable produced (no deep copy of elements is performed).
        - Mutating the original iterable object (if it was a mutable sequence) after this call does not change self._paragraphs; however, mutating the objects stored as elements will be observable through self._paragraphs because elements are stored by reference.
        - Building the tuple requires allocating memory proportional to the number of elements (O(n) memory).

## Edge cases and examples:
    - If paragraphs is a string (e.g., 'abc'), self._paragraphs will be a tuple of single-character strings: ('a', 'b', 'c').
    - If paragraphs is already a tuple, tuple(paragraphs) creates a new tuple with the same element references (shallow copy semantics).
    - If paragraphs is a generator or iterator, its elements will be consumed; subsequent iteration over that generator will yield nothing.
    - Large or infinite iterables: this method attempts to realize all elements into memory; it is not safe for infinite iterables and may be impractical for very large iterables.

## Side Effects:
    - No I/O or external service calls.
    - Mutates only the new instance by setting self._paragraphs; it does not mutate the provided iterable or the element objects themselves.

### `sumy.models.dom._document.ObjectDocumentModel.paragraphs` · *method*

## Summary:
Returns the document's stored paragraphs as an immutable sequence, exposing the object's internal paragraph tuple without copying it.

## Description:
This read-only property exposes the sequence of paragraph objects that were provided when the ObjectDocumentModel instance was constructed. It is used wherever callers need to inspect or iterate the document's paragraphs; within this class it is referenced by __unicode__ to compute the paragraph count. The logic is separated into its own property to provide a stable, documented public accessor and to enforce that callers receive an immutable tuple (the internal representation) rather than relying on direct attribute access.

Known callers and usage context:
- ObjectDocumentModel.__unicode__ / __str__ / __repr__: reads the number of paragraphs via len(self.paragraphs) when producing a textual representation of the DOM.
- External consumers (summarizers, serializers, or traversal code): iterate over the returned tuple to access paragraph-level data (sentences, headings, words).
- The property's separation keeps a simple, consistent API surface for the model and prevents callers from depending on internal attribute naming.

Why this is a separate property:
- Encapsulates the internal representation (tuple) so the class can guarantee immutability of the returned sequence.
- Provides a stable public API for accessing paragraphs instead of exposing _paragraphs directly.
- Keeps intent explicit and documents that callers should treat the returned value as read-only.

## Args:
None.

## Returns:
tuple
    An immutable tuple containing the paragraph objects stored in this document. Each element is the paragraph object originally passed to ObjectDocumentModel.__init__. Edge cases:
    - If the instance was correctly constructed, this is always a tuple (possibly empty).
    - If the instance was not initialized correctly and the internal attribute is missing, attribute access may raise AttributeError (see Raises).

## Raises:
AttributeError
    If the instance does not have the internal attribute _paragraphs (for example, if __init__ was not run), attempting to access this property will raise AttributeError. No other exceptions are raised by this property itself.

## State Changes:
Attributes READ:
    - self._paragraphs

Attributes WRITTEN:
    - None (this property does not modify any attributes)

## Constraints:
Preconditions:
    - The ObjectDocumentModel instance must have been initialized so that self._paragraphs exists (ObjectDocumentModel.__init__ sets this to tuple(paragraphs)).
    - Paragraph objects inside the tuple are expected (by other parts of the system) to provide attributes such as sentences, headings, and words, but this property makes no structural checks.

Postconditions:
    - The returned value is the same tuple object stored at self._paragraphs (no copy is made).
    - The internal state of the instance is unchanged by calling this property.

## Side Effects:
    - None. No I/O, no external service calls, and no mutation of objects outside self occur when reading this property.

### `sumy.models.dom._document.ObjectDocumentModel.sentences` · *method*

## Summary:
Return a flattened, immutable tuple containing every sentence from every paragraph in the document; the value is computed on first access and cached for subsequent accesses by the cached_property decorator.

## Description:
This property collects each paragraph's .sentences iterable and concatenates them into a single tuple, preserving paragraph order and sentence order within each paragraph. It provides a single, canonical sentence-level view of the document so callers do not need to traverse paragraphs themselves.

Known callers and lifecycle:
- No internal callers are present in the provided module snapshot. The property is part of the public ObjectDocumentModel API and is intended for external consumers that operate on sentence-level units (for example, summarizers, ranking algorithms, or tokenizers).
- Typical usage: after constructing an ObjectDocumentModel, consumers access doc.sentences during analysis or processing pipelines that require iterating over all sentences.

Why this is a separate property:
- Encapsulates and centralizes flattening logic so multiple callers do not duplicate it.
- Because it is decorated with @cached_property, the potentially-expensive materialization happens once and the cached tuple is reused, improving performance for repeated accesses.

## Args:
- None.

## Returns:
- tuple: A tuple containing, in order, every element yielded by each paragraph's .sentences iterable. If there are no paragraphs or all .sentences iterables are empty, an empty tuple is returned.
- Element types: Elements are whatever each paragraph exposes via .sentences (commonly sentence objects). This method does not validate or convert element types.

## Raises:
- AttributeError: If any entry of self._paragraphs does not have a .sentences attribute, attribute lookup will raise AttributeError during iteration.
- TypeError: If a paragraph's .sentences attribute exists but is not iterable, attempting to iterate it will raise TypeError.
- Any exceptions raised while evaluating a paragraph's .sentences (for example, if that property raises) will propagate unchanged.

## State Changes:
- Attributes READ:
    - self._paragraphs (populated in __init__ as a tuple)
- Attributes WRITTEN:
    - The function body does not assign to any self.<attr>. However, the @cached_property decorator on the class causes the computed tuple to be cached on the instance when first accessed (i.e., subsequent accesses return the stored value rather than recomputing). That caching/storage is performed by the cached_property descriptor, not by this function body.

## Constraints:
- Preconditions:
    - The instance must have been initialized with self._paragraphs set (ObjectDocumentModel.__init__ stores paragraphs as a tuple).
    - Each item in self._paragraphs must expose a .sentences attribute that is iterable.
- Postconditions:
    - The returned value is a tuple that is the concatenation, in order, of each paragraph's .sentences iterable.
    - After the first access, the cached_property descriptor will cause subsequent accesses to return the same tuple instance (no recomputation), assuming the cached_property implementation follows standard descriptor caching semantics.

## Side Effects:
- No I/O or network activity.
- No mutation of external objects is performed by this method itself.
- The primary side effect is caching: on first access the computed tuple is stored via the cached_property descriptor on the instance; this increases memory usage proportional to the size of the flattened sentence list.
- Large documents will materialize all sentences into memory at once; callers that wish to avoid this should iterate paragraphs and their sentences lazily instead of using this property.

### `sumy.models.dom._document.ObjectDocumentModel.headings` · *method*

## Summary:
Return a flattened, read-only tuple containing all heading items from every paragraph in this document model; computed from the instance's paragraphs and intended to be treated as a cached attribute.

## Description:
This method aggregates the headings provided by each paragraph in the document and returns them as a single flat tuple in paragraph order.

Known callers and usage context:
- Accessed whenever external code or other components need the document-level list of headings (e.g., during DOM traversal, indexing, or summarization pipelines). It is a property on the DOM model, so callers use it like an attribute (document.headings).
- Within the ObjectDocumentModel class, it is defined alongside other cached properties (sentences, words) to provide commonly-requested flattened views of paragraph-level data.

Why this logic is a separate method/property:
- It encapsulates the common pattern of collecting and flattening per-paragraph heading iterables into a document-level sequence.
- Being a (cached) property avoids repeating this flattening logic at each call site and allows potential caching of the result for repeated access.

## Args:
None.

## Returns:
tuple
- A tuple containing the concatenation of each paragraph's headings iterables, in the same order as self._paragraphs.
- If there are no paragraphs or no headings, returns an empty tuple.

Element types:
- The tuple's element type is exactly the type yielded by each paragraph.headings iterable. This documentation does not assume a concrete element type because paragraph implementations determine it (commonly heading nodes or strings).

## Raises:
- This function does not explicitly raise exceptions in its body.
- Implicit errors that may propagate:
    - TypeError (or another iteration-related exception) may occur if any paragraph.headings is not an iterable (for example, a non-iterable value), because itertools.chain expects iterable arguments.
    - Any exception raised while accessing self._paragraphs or a paragraph's headings attribute will propagate to the caller.

## State Changes:
Attributes READ:
- self._paragraphs — the method iterates over this tuple to obtain each paragraph.

Attributes WRITTEN:
- None by this method's body. (Note: the method is declared with @cached_property at the class level; the caching decorator itself may store the computed tuple on the instance as a cached attribute. That caching side-effect is produced by the decorator implementation, not by this method body.)

## Constraints:
Preconditions:
- self._paragraphs must be an iterable (the class stores it as a tuple in __init__).
- Each element p in self._paragraphs must expose a headings attribute that itself is an iterable of heading items.

Postconditions:
- The method returns a tuple whose elements are the flattened sequence of items produced by iterating each paragraph.headings in order.
- The method does not mutate self._paragraphs or the paragraph objects.

## Side Effects:
- No I/O, network calls, or external service interactions.
- No mutation of external objects by this method's body.
- The only potential side-effect is caching behavior if the @cached_property decorator stores the computed value on the instance; that is external to this method's implementation.

### `sumy.models.dom._document.ObjectDocumentModel.words` · *method*

## Summary:
Returns a flattened tuple containing every word token from all paragraphs in the document and (on first access) caches that tuple on the instance.

## Description:
This property gathers the .words sequences from each paragraph stored in self._paragraphs, flattens them into a single sequence and returns it as an immutable tuple. It is implemented as a cached property (imported from utils and applied on the class), so the first access computes and stores the result on the instance; subsequent accesses return the cached tuple without recomputing.

Known callers and usage context:
- Any component that needs a document-level sequence of words (for example: token-level feature extractors, summarization scorers, indexing or search pre-processing). These consumers typically access this property during document analysis or feature extraction stages of a text-processing pipeline.
- It is invoked when callers read document.words; because it is cached, it is intended to be used when multiple accesses are expected and recomputation would be wasteful.

Why this is a separate method/property:
- The logic performs a standard transformation (collect and flatten paragraph-level word sequences) that is useful across multiple consumers. Centralizing and caching it avoids repetition and repeated traversal of paragraph lists.

## Args:
    None

## Returns:
    tuple: An immutable tuple containing all elements yielded by each paragraph's .words attribute, concatenated in paragraph order. Elements are the same objects produced by Paragraph.words (commonly token strings or token objects) — the method does not modify or re-wrap them.
    - If self._paragraphs is empty, returns an empty tuple.
    - The method always returns a tuple; it never returns None.

## Raises:
    AttributeError: propagated if any paragraph in self._paragraphs does not have a .words attribute.
    TypeError: propagated if any paragraph's .words is not iterable (so chain cannot iterate it).
    Note: the method itself does not explicitly raise exceptions; exceptions arise from malformed paragraph objects or non-iterable .words values and are not caught.

## State Changes:
Attributes READ:
    - self._paragraphs: iterated to collect paragraph-level .words sequences

Attributes WRITTEN:
    - None by the method body itself.
    - Indirect / decorator effect: because the method is decorated with cached_property at the class level, the cached_property implementation will typically store the computed tuple on the instance (e.g., self.words) on first access. That write is a side-effect of the decorator rather than this method's body.

## Constraints:
Preconditions:
    - self._paragraphs must be an iterable of paragraph-like objects.
    - Each paragraph object must expose a .words attribute that is itself iterable (e.g., list/tuple/generator of tokens).

Postconditions:
    - Returns a tuple containing, in order, every element yielded by each paragraph.words in the same order as paragraphs in self._paragraphs.
    - After the first access, the computed tuple is cached on the instance (per cached_property behavior), so subsequent accesses return the cached tuple without recomputing.

## Side Effects:
    - No I/O or network calls.
    - No mutation of paragraph objects or the returned elements.
    - The only observable mutation is the caching of the computed tuple onto the instance by the cached_property decorator (if using a standard cached_property implementation).

### `sumy.models.dom._document.ObjectDocumentModel.__unicode__` · *method*

## Summary:
Returns a human-readable textual representation of the document that includes the number of paragraphs it contains.

## Description:
This method produces a one-line textual description intended for debugging, logging, or display when the object is coerced to a string. It is typically invoked during string conversions (for example, when code calls str(obj) or when __repr__ delegates to string conversion). In this class, __repr__ delegates to __str__, and string conversion paths are the common callers of this routine.

This logic is isolated as its own method because it encapsulates the object's canonical text representation (the format "<DOM with N paragraphs>") in a single place; keeping it separate avoids duplicating formatting logic in __str__/__repr__ and allows consistent representation across different string conversion hooks or compatibility layers.

## Args:
    None

## Returns:
    str: A text string of the exact form "<DOM with %d paragraphs>" where %d is replaced with the integer length of self.paragraphs. Because the module uses unicode_literals, this will be a text string type (unicode in Python 2 terms, str in Python 3 terms).

    Examples:
        "<DOM with 0 paragraphs>"
        "<DOM with 5 paragraphs>"

## Raises:
    AttributeError: If self.paragraphs is not present on the instance (for example, if the instance was not properly initialized and self._paragraphs was never set).
    TypeError: Possible if self.paragraphs exists but has no defined length (i.e., len(self.paragraphs) raises TypeError). This is unlikely for the provided class because __init__ stores paragraphs as tuple(paragraphs), which guarantees a sized sequence when initialization succeeds.

## State Changes:
    Attributes READ:
        self.paragraphs — property which returns self._paragraphs (the tuple of paragraph objects).
        self._paragraphs — (indirectly read via the paragraphs property)

    Attributes WRITTEN:
        None — this method does not mutate instance state.

## Constraints:
    Preconditions:
        - The ObjectDocumentModel instance must have been successfully initialized so that self._paragraphs exists and is a sequence (the class' __init__ converts the supplied paragraphs iterable into a tuple).
        - The paragraphs container must support len() (tuple does).

    Postconditions:
        - No changes to the instance state.
        - The returned string contains the integer value len(self.paragraphs) at the position of %d.

## Side Effects:
    - None. This method performs no I/O, does not call external services, and does not mutate objects outside self.

## Implementation notes for reimplementation:
    - Compute the paragraph count with len(self.paragraphs).
    - Format the exact literal pattern "<DOM with %d paragraphs>" using old-style (%) formatting or an equivalent that produces the identical textual pattern.
    - Do not alter or normalize the paragraphs attribute; only read it.

### `sumy.models.dom._document.ObjectDocumentModel.__repr__` · *method*

## Summary:
Return the result of calling the instance's __str__ method, providing the object's textual representation.

## Description:
- Known callers and contexts:
    - The built-in repr() function when invoked on an ObjectDocumentModel instance.
    - Python runtime when producing representations for interactive prompts, container reprs, logging, or debugging output that uses repr().
    - Any code that explicitly calls obj.__repr__() or uses formatting that requests an object's repr.
  These occur during inspection, debugging, or any step that needs a programmatic textual representation of the object.

- Rationale:
    - This implementation centralizes representation logic by delegating to __str__, avoiding duplication of formatting code between __str__ and __repr__.

## Args:
    None

## Returns:
    The direct return value of self.__str__(). Typically this is a str (the usual contract for __str__), but this method returns whatever __str__ returns.

## Raises:
    Any exception raised inside self.__str__() will propagate unchanged from __repr__. This method does not raise exceptions itself.

## State Changes:
- Attributes READ:
    - None by this method itself.
    - Any attribute access depends solely on the behavior of self.__str__() and is not determined here.
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - The instance must be properly constructed as an ObjectDocumentModel instance.
- Postconditions:
    - The object is not modified by this call.
    - The return value equals the direct result of invoking self.__str__() or an exception is propagated.

## Side Effects:
    - This method performs no I/O, network activity, or mutation of external objects.
    - The only observable action is calling self.__str__(), which may itself have side effects; those are outside the scope of this delegating method.

