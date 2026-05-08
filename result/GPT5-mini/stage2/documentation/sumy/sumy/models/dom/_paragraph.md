# `_paragraph.py`

## `sumy.models.dom._paragraph.Paragraph` · *class*

## Summary:
Container for a sequence of Sentence objects that provides cached, read-only access to non-heading sentences, heading sentences, and the flattened sequence of words across all contained sentences.

## Description:
Paragraph groups Sentence instances passed at construction and exposes three derived, cached views:
- sentences: tuple of Sentence objects where Sentence.is_heading is False
- headings: tuple of Sentence objects where Sentence.is_heading is True
- words: tuple of token strings obtained by concatenating Sentence.words for each contained Sentence in order

Use Paragraph when you already have Sentence objects (for example, produced by a tokenizer/parser) and need a lightweight paragraph-level container to query headings, sentences, or the paragraph's token stream. Paragraph does not mutate the Sentence instances it contains; it stores the collection as a tuple and computes derived values lazily.

## State:
Defined __slots__:
- _sentences (tuple[Sentence])
  - Set in __init__ to tuple(sentences_iterable). Preserves order from the provided iterable.
  - Invariant: every element is an instance of sumy.models.dom._sentence.Sentence.
- _cached_property_sentences
  - Created on first access to the sentences property by cached_property.
  - Holds tuple of Sentence objects filtered with not s.is_heading.
- _cached_property_headings
  - Created on first access to the headings property by cached_property.
  - Holds tuple of Sentence objects filtered with s.is_heading.
- _cached_property_words
  - Created on first access to the words property by cached_property.
  - Holds a tuple of token strings produced by flattening s.words for every Sentence in _sentences, preserving sentence and token order.

Types and values:
- Constructor parameter sentences: any iterable yielding Sentence instances; converted to tuple internally.
- sentences property: tuple[Sentence] (non-heading sentences)
- headings property: tuple[Sentence] (heading sentences)
- words property: tuple[str] (flattened tokens)

Class invariants:
- _sentences remains the original tuple passed at construction.
- Each cached property, once computed, is stored on the instance under the attribute name "_cached_property_" + property_name and does not change afterwards.
- The order of tokens in .words matches the iteration order of _sentences and the order of tokens inside each Sentence.words.

## Lifecycle:
Creation:
- Call Paragraph(sentences_iterable).
- __init__ converts the iterable to tuple and verifies element types.

Usage:
- Access any of the properties in any order:
  - paragraph.sentences computes and caches tuple(s for s in _sentences if not s.is_heading).
  - paragraph.headings computes and caches tuple(s for s in _sentences if s.is_heading).
  - paragraph.words computes and caches tuple(chain(*(s.words for s in _sentences))).
- Each Sentence.words access may itself be cached (Sentence implements its own cached_property) and typically calls the tokenizer's to_words method to produce tokens.

Destruction / Cleanup:
- No external resources or cleanup methods; normal garbage collection applies.

## Method Map:
flowchart LR
    Init[__init__(sentences)] --> Store[_sentences = tuple(sentences)]
    Store --> SentProp[.sentences property]
    Store --> HeadProp[.headings property]
    Store --> WordsProp[.words property]
    SentProp --> SentCache[_cached_property_sentences set to tuple(filter not s.is_heading)]
    HeadProp --> HeadCache[_cached_property_headings set to tuple(filter s.is_heading)]
    WordsProp --> WordsCache[_cached_property_words set to tuple(chain(*(s.words for s in _sentences)))]
    WordsProp --> SentenceWords[access each Sentence.words -> tokenizer.to_words(text)]
Notes:
- cached_property stores each property's value under "_cached_property_" + property_name (e.g., _cached_property_words).

## Raises:
- TypeError("Only instances of class 'Sentence' are allowed."):
  - Raised by __init__ if any element in the provided iterable is not an instance of sumy.models.dom._sentence.Sentence.
  - The check is performed by isinstance(sentence, Sentence) for each item in the tuple(sentences).

## Example:
- Given Sentence objects sentence1, sentence2, sentence3:
  - paragraph = Paragraph([sentence1, sentence2, sentence3])
  - non_heading_sentences = paragraph.sentences    # tuple of Sentence where is_heading is False
  - heading_sentences = paragraph.headings         # tuple of Sentence where is_heading is True
  - all_tokens = paragraph.words                   # flattened tuple[str] of tokens in paragraph order
  - unicode_summary = paragraph.__unicode__()      # returns "<Paragraph with %d headings & %d sentences>" % (len(headings), len(sentences))

Implementation notes for reimplementation:
- Convert input to tuple to preserve order and create a fixed container.
- Enforce type checks against the actual Sentence class and raise the exact TypeError message shown above.
- Implement cached properties by computing the value once and storing it on the instance under "_cached_property_<name>" to match behavior.
- Compute words with itertools.chain to preserve ordering and avoid nested tuples.

### `sumy.models.dom._paragraph.Paragraph.__init__` · *method*

## Summary:
Normalize and validate an iterable of Sentence objects and store them on the instance as an immutable sequence.

## Description:
This initializer is executed when a new Paragraph object is created. It takes an iterable of Sentence instances, converts it to a tuple, validates that every element is an instance of the Sentence class, and stores the tuple on the instance.

Known callers and context:
- Instantiation time: called whenever client code or other modules construct a Paragraph (for example, when building a document model from parsed DOM or when converting tokenized sentences into a higher-level paragraph model). This method is invoked as part of the Paragraph object's construction lifecycle.
- There are no side-effecting responsibilities beyond validating and storing the sentences; it exists to encapsulate the normalization and validation logic required whenever a Paragraph is created so callers don't need to perform these checks themselves.

Why this logic is its own method:
- Placing validation and normalization in the initializer centralizes invariants for Paragraph instances (ensuring paragraphs always hold a tuple of Sentence objects). This prevents repetition and ensures downstream code can rely on the internal representation (an immutable tuple) and element types.

## Args:
    sentences (iterable of Sentence): An iterable yielding items that must each be an instance of the Sentence class. The iterable may be any Python iterable (list, tuple, generator, etc.). There is no default value — the argument is required.

## Returns:
    None: As an initializer, it does not return a value. After execution, the instance attribute self._sentences will contain a tuple of the provided Sentence instances.

## Raises:
    TypeError: Raised if any element in the provided iterable is not an instance of Sentence. The exact message produced by the implementation is:
        "Only instances of class 'Sentence' are allowed."
    This exception is raised at the first non-Sentence element encountered during iteration.

## State Changes:
    Attributes READ:
        - None of self's attributes are read by this method.

    Attributes WRITTEN:
        - self._sentences (tuple[Sentence]): Set to a tuple containing the validated Sentence instances converted from the given iterable.

## Constraints:
    Preconditions:
        - The caller must provide an iterable. If a non-iterable is passed, Python will raise the appropriate error when attempting tuple(iterable) (e.g., TypeError).
        - Each yielded element must be an instance of Sentence; otherwise a TypeError is raised.

    Postconditions:
        - On successful return, self._sentences is guaranteed to be a tuple (immutable sequence) and every element of that tuple is an instance of Sentence.
        - No further normalization is performed (elements are stored as provided, in the same order).

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - The only mutation is assigning the tuple to self._sentences (no mutation of the passed-in iterable is performed).

### `sumy.models.dom._paragraph.Paragraph.sentences` · *method*

## Summary:
Returns a tuple of the paragraph's content sentences (excluding heading sentences) and caches that result on first access.

## Description:
This cached property filters the Paragraph's internal sentence sequence and exposes only non-heading Sentence objects in their original order. Known internal callers include:
- Paragraph.__unicode__ which calls len(self.sentences) to report the number of non-heading sentences.
- Any external consumer that iterates or slices paragraph.sentences to process textual sentences (e.g., summarizers or downstream pipelines).

This logic is separated into its own (cached) property because:
- It expresses a well-scoped concept (content sentences vs. headings) used repeatedly across the codebase.
- Filtering can be performed once and reused; caching avoids repeated iteration and re-evaluation of Sentence.is_heading for performance.
- Keeping heading separation centralized prevents duplication and ensures consistent ordering and filtering semantics.

## Args:
None (accessed as a zero-argument property on Paragraph instances).

## Returns:
tuple[Sentence, ...]
- A tuple containing the same Sentence objects (by reference) from self._sentences for which Sentence.is_heading is False.
- The ordering is the same as in self._sentences, with all heading sentences removed.
- Edge cases:
  - Returns an empty tuple if self._sentences is empty or if every sentence has is_heading == True.

## Raises:
- No exceptions are raised by this property when Paragraph invariants are satisfied.
- Implicit exceptions:
  - AttributeError may occur if elements of self._sentences do not expose an is_heading attribute (this is prevented by Paragraph.__init__ which enforces Sentence instances).
  - TypeError may have already been raised at Paragraph construction time if non-Sentence objects were passed to __init__.

## State Changes:
Attributes READ:
- self._sentences: iterated to produce the filtered tuple.
- For each element s in self._sentences, reads s.is_heading (the Sentence.is_heading property).

Attributes WRITTEN:
- self._cached_property_sentences: on first access the computed tuple is stored by the cached_property implementation (one-time mutation to cache the value). No other attributes on self are modified.

## Constraints:
Preconditions:
- The Paragraph object must have been constructed with an iterable of Sentence instances (Paragraph.__init__ enforces this and will raise TypeError otherwise).
- Sentence.is_heading must be a valid property on each Sentence instance (this is true for the bundled Sentence class).

Postconditions:
- After the first access, self._cached_property_sentences exists and subsequent accesses return the same tuple object (no re-computation).
- The returned tuple contains only Sentence objects with is_heading == False, in the same order as the original _sentences.

## Side Effects:
- No I/O or external service interactions.
- Mutates the Paragraph instance by setting the cached attribute (self._cached_property_sentences) on first access; no other side effects.

### `sumy.models.dom._paragraph.Paragraph.headings` · *method*

## Summary:
Returns a tuple of the sentences from this paragraph that are marked as headings, caching the result on the instance.

## Description:
This attribute / method filters the paragraph's internal sentence list and produces an immutable tuple containing only those Sentence objects whose is_heading property is True. It is implemented as a cached property in the Paragraph class so that the filtering is performed once per instance and reused on subsequent accesses.

Known internal callers:
    - Paragraph.__unicode__: uses the length of this tuple to build a textual representation of the Paragraph.
    - Other components in the summarization pipeline may read this property to separate heading sentences from body sentences (no additional internal callers were observed in the provided module snapshot).

Why this is a separate method:
    - The logic isolates the "which sentences are headings" concern and makes the intent explicit.
    - Decorating it as a cached property avoids repeated computation and keeps the Paragraph API ergonomic (attribute-like access).

## Args:
    None (accessed as a property). There are no parameters to call.

## Returns:
    tuple[Sentence, ...]: A tuple containing the Sentence instances from self._sentences for which Sentence.is_heading evaluates to True.
    - If no sentences are marked as headings, returns an empty tuple.
    - The tuple preserves the original order of sentences as stored in self._sentences.

## Raises:
    - AttributeError: If the Paragraph instance is not properly initialized and does not have the internal attribute _sentences.
    - AttributeError: If any element in self._sentences does not expose an is_heading attribute (this would typically indicate invalid construction of the Paragraph).
    - No TypeError is raised by this method itself; construction-time checks in Paragraph.__init__ raise TypeError if non-Sentence objects are passed when the Paragraph was created.

## State Changes:
Attributes READ:
    - self._sentences: the internal tuple of Sentence objects is iterated and inspected.
    - Sentence.is_heading: the property getter on each Sentence instance is read.

Attributes WRITTEN:
    - The method body does not directly assign any attributes. However, because the method is decorated with cached_property, accessing this attribute will typically cause the cached_property mechanism to store the computed tuple on the instance (implementation detail: stored in the slot _cached_property_headings per Paragraph.__slots__). Thus, the first access results in a mutation of the instance's cached-property storage.

## Constraints:
Preconditions:
    - The Paragraph instance must have been constructed properly; self._sentences must be a sequence/iterable of Sentence instances.
    - Each Sentence must implement the is_heading property (Sentence.is_heading returns a boolean).

Postconditions:
    - The method returns an immutable tuple of Sentence objects with is_heading == True.
    - Subsequent accesses will return the same tuple instance (served from cache) until the instance is discarded or the cached_property is explicitly invalidated (no invalidation mechanism is implemented here).

## Side Effects:
    - Mutates the paragraph instance by storing the computed value in the cached-property storage (e.g., _cached_property_headings). There are no I/O operations or external service calls.

### `sumy.models.dom._paragraph.Paragraph.words` · *method*

## Summary:
Return a cached, flattened tuple containing every token produced by each Sentence in the Paragraph, preserving sentence order and including any heading sentences. The value is computed once and then cached on the Paragraph instance.

## Description:
This cached property computes tuple(chain(*(s.words for s in self._sentences))) — concatenating the token sequences from every Sentence in self._sentences in order. The property is decorated with cached_property, so the computed tuple is stored by the cached_property mechanism on the Paragraph instance and reused on subsequent accesses.

Why this is a separate property:
- Flattening per-sentence token sequences into a paragraph-level token stream is a distinct, reusable operation; exposing it as a cached property avoids repeated recomputation.

Known callers and lifecycle:
- There are no callers shown in this module. External consumers may read this property during text-processing or analysis stages, but specific call sites are not present in the provided source.

## Args:
- None (accessed as a parameterless cached property on a Paragraph instance)

## Returns:
- tuple: The concatenation of all Sentence.words sequences for s in self._sentences (i.e., tuple(chain(*(s.words for s in self._sentences)))).
  - Order: tokens are ordered by sentence (all tokens from the first Sentence, then the second, etc.).
  - Element type: exactly the element type produced by each Sentence.words (the property performs no conversion).
  - Empty paragraph: returns an empty tuple () when self._sentences is empty.

## Raises:
- This property does not explicitly raise new exceptions in its body; however, exceptions may propagate:
  - Any exception raised while evaluating Sentence.words (for example, from the tokenizer) will propagate.
  - TypeError or other iteration-related exceptions will propagate if any s.words is not iterable.
- Note: Paragraph.__init__ validates that items in self._sentences are Sentence instances and will raise TypeError at construction time if that contract is violated; that TypeError is raised during construction, not by this property.

## State Changes:
Attributes READ:
- self._sentences (iterates over the tuple of Sentence instances held by the Paragraph)
- For each sentence s, reads s.words (accessing the Sentence.cached_property)

Attributes WRITTEN:
- The cached_property mechanism stores the computed tuple on the Paragraph instance (so the instance is mutated to record the cached value). No other Paragraph attributes are modified by this property.
- Accessing s.words may also cause the Sentence instance to cache its token sequence (via its cached_property); that is a mutation of the Sentence instance, not of external systems.

## Constraints:
Preconditions:
- The Paragraph instance must have been constructed using an iterable of Sentence instances (Paragraph.__init__ enforces this).
- Each Sentence.words must be an iterable of tokens.

Postconditions:
- The returned value equals tuple(chain(*(s.words for s in self._sentences))).
- The computed tuple is cached on the Paragraph instance via the cached_property decorator so subsequent accesses return the cached value rather than recomputing.

## Side Effects:
- Caches the computed tuple on the Paragraph instance (mutation of instance state via the cached_property mechanism).
- May trigger evaluation and caching of Sentence.words on each Sentence instance when accessed.
- No I/O, network calls, or modifications to global state occur within this property itself.

### `sumy.models.dom._paragraph.Paragraph.__unicode__` · *method*

## Summary:
Return a concise human-readable text describing how many headings and sentences the Paragraph currently contains.

## Description:
Produces a one-line textual representation intended for debugging, logging, or any context where the Paragraph is converted to text. Typical invocation paths include:
- When the Paragraph is converted to a text representation by compatibility shims (for example, a unicode/str wrapper provided by a unicode_compatible decorator in the module).
- When callers explicitly call str() or otherwise format the object for logs or debugging.

Note: The method body itself contains no other call sites; the above are common external use cases rather than discovered in-file call references.

This behavior is implemented as a dedicated method to centralize the textual representation so that all callers receive a consistent, easy-to-read summary without duplicating formatting logic across the codebase.

## Args:
    None

## Returns:
    str: A text string formatted exactly as "<Paragraph with X headings & Y sentences>" where:
        - X is the integer result of len(self.headings)
        - Y is the integer result of len(self.sentences)

    Edge cases:
        - If headings or sentences are empty iterables, X or Y will be 0.
        - The method does not coerce values; it relies on Python's built-in len() semantics.

## Raises:
    AttributeError: If the Paragraph instance does not have the attribute self.headings or self.sentences (missing attribute access).
    TypeError: If self.headings or self.sentences exists but does not support the len() operation (for example, if either is None or an object without __len__).

## State Changes:
    Attributes READ:
        - self.headings
        - self.sentences

    Attributes WRITTEN:
        - None. The method does not modify any attributes.

## Constraints:
    Preconditions:
        - The Paragraph instance must have attributes named headings and sentences.
        - Those attributes should be sized iterables (support __len__) for clean operation.

    Postconditions:
        - The Paragraph object is not modified.
        - A formatted str is returned that reflects the lengths of the two attributes at call time.

## Side Effects:
    - None. The method performs no I/O, network access, or mutation of external objects.

### `sumy.models.dom._paragraph.Paragraph.__repr__` · *method*

## Summary:
Delegates the object's official string representation to its informal string conversion by returning the result of calling the instance's __str__() method. Does not modify object state.

## Description:
This method is a thin wrapper that returns exactly whatever self.__str__() produces. It is typically invoked by Python built-ins and tooling that request an object's representation:
- Known callers / invocation contexts:
    - Built-in repr(obj) and interactive REPL display
    - Logging frameworks or debugging utilities that call repr()
    - When a Paragraph instance appears inside container types (lists, tuples, dicts) and the container's repr is produced
  There are no callers inside this module shown in the provided source; it is used externally by standard Python machinery.

This logic is factored into its own method so that the canonical representation used by repr() is identical to the instance's __str__ output, centralizing formatting behavior in one place (the __str__ implementation) rather than duplicating it inside __repr__.

## Args:
    None

## Returns:
    str or any: The return value of calling self.__str__(). In normal/expected use this will be a text string describing the Paragraph (e.g., produced by a __str__ or __unicode__ implementation). If the __str__ method returns a non-string value, that exact value is returned unchanged.

## Raises:
    Any exception raised by self.__str__() is propagated unchanged. No additional exceptions are raised by this wrapper itself.

## State Changes:
    Attributes READ:
        - None directly. This method does not access attributes itself; calling self.__str__() may read attributes or cached properties (for example, headings or sentences) depending on the __str__ implementation.
    Attributes WRITTEN:
        - None. This method does not modify any attributes.

## Constraints:
    Preconditions:
        - self must be a valid Paragraph instance (i.e., properly initialized). The presence of a callable __str__ attribute is expected (objects always inherit a callable __str__ from object), but the returned value's type and correctness depend on the Paragraph.__str__ implementation.
    Postconditions:
        - No mutation of self is performed.
        - The function returns immediately with the value returned by self.__str__().

## Side Effects:
    - None directly. Any side effects originate from the __str__ implementation invoked (for example: computing cached properties, triggering lazy evaluation, or raising exceptions). This method performs no I/O and makes no external service calls.

