# `_summarizer.py`

## `sumy.summarizers._summarizer.AbstractSummarizer` · *class*

## Summary:
An abstract base class that defines the public summarizer interface and common helpers (word normalization/stemming and top-sentence selection) for concrete summarizer implementations.

## Description:
AbstractSummarizer encapsulates the minimal shared behavior required by all concrete summarizers:
- Exposes a canonical callable interface (instance(document, sentences_count)) that subclasses must implement to produce a summary.
- Provides normalization and stemming helpers (normalize_word, stem_word) so all summarizers can use a consistent token canonicalization policy.
- Provides a reusable selection helper (_get_best_sentences) that ranks, selects, and restores original document order for top-rated sentences.

When to instantiate:
- Never instantiate AbstractSummarizer directly for summarization; it is intended to be subclassed. Concrete summarizer implementations provided by the project (or user-defined ones) will inherit from this class and implement the __call__ method.
- Typical callers/factories: pipeline code that chooses and constructs a specific Summarizer subclass (e.g., language or algorithm specific implementations) and then invokes the instance with a parsed document and desired sentence count.

Responsibility boundary:
- AbstractSummarizer enforces the public API and provides generic helpers; it does not implement any summarization algorithm itself. All algorithm-specific logic (scoring, candidate generation, post-processing) must live in subclasses overriding __call__.

## State:
Attributes (instance-level)
- _stemmer (callable)
  - Type: callable(token) -> any
  - Default: null_stemmer (a callable that converts its input to unicode and lowercases it)
  - Valid values: any callable accepting a single token argument. __init__ verifies callability and raises ValueError otherwise.
  - Invariant: self._stemmer must remain a callable for the lifetime of the instance (used by stem_word).
  - Usage: invoked by stem_word after normalize_word to obtain a token stem.

No other attributes are defined by the base class; subclasses may add their own state (caches, counters, language metadata). There are no protected or public fields beyond _stemmer guaranteed by this class.

Class invariants:
- After construction, _stemmer is callable.
- normalize_word is a pure function and does not depend on instance state.
- _get_best_sentences is a pure helper: it does not mutate instance state and returns a tuple of selected sentence objects.

## Lifecycle:
Creation
- Constructor signature: accepts a single optional parameter stemmer (default: null_stemmer).
- Caller responsibility: supply a callable if custom stemming behavior is required. The constructor raises ValueError if stemmer is not callable.

Usage (typical sequence)
1. Construct a concrete subclass instance, providing a custom stemmer only if needed.
2. Prepare a parsed document object appropriate for the concrete summarizer (document representation is implementation-specific; usually contains an ordered sequence of sentence objects).
3. Invoke the instance as a callable with two arguments: (document, sentences_count).
   - document: a parsed document (type and shape validated/expected by the subclass).
   - sentences_count: commonly an int or a count-selection policy usable by the helper _get_best_sentences. Subclasses can accept other forms but must document them.
4. Inside a subclass's __call__, the implementation typically:
   - tokenizes/iterates sentences,
   - uses normalize_word and stem_word for token normalization or feature extraction,
   - computes a per-sentence rating,
   - uses _get_best_sentences to select the highest-rated sentences, or returns its own selection.
5. The final result should be an ordered collection (tuple/list) of sentence objects representing the summary.

Destruction / cleanup
- The base class requires no explicit cleanup. There is no context manager protocol, close(), or finalizer provided by AbstractSummarizer.
- If subclasses allocate external resources (files, network clients, large caches), they must implement their own cleanup.

## Method Map:
A simple call-dependency graph showing public helpers and typical call relationships.

graph TD
    A[Constructor: __init__(stemmer)] --> B[_stemmer set]
    C[normalize_word(word)] --> D[to_unicode(word).lower()]
    B --> E[stem_word(word)]
    E --> C
    E --> F[self._stemmer(normalized_word)]
    G[__call__(document,sentences_count) - abstract] --> H[Concrete subclass implementation]
    H --> E
    H --> I[_get_best_sentences(sentences,count,rating)]
    I --> J[Create per-sentence infos: SentenceInfo(sentence,order,rating)]
    J --> K[Sort infos by rating (desc)]
    K --> L[Apply count policy (ItemsCount or callable)]
    L --> M[Sort selected infos by order (asc)]
    M --> N[Return tuple of selected sentence objects]

Notes:
- __call__ is abstract and must be overridden by subclasses; it is the public entry-point.
- normalize_word and stem_word are helpers that are safe to call from subclasses.
- _get_best_sentences is a static helper suitable for reuse by subclasses when a "score then pick top N" approach is used.

## Behavior and detailed method semantics (enough to implement)
- __init__(stemmer=null_stemmer)
  - Accepts: stemmer (callable). Default is null_stemmer.
  - Enforces: raises ValueError("Stemmer has to be a callable object") if stemmer is not callable.
  - Effect: sets self._stemmer = stemmer.

- __call__(document, sentences_count)
  - Abstract; base implementation raises NotImplementedError("This method should be overriden in subclass").
  - Contract for implementers: accept a parsed document and a sentences_count value; return an ordered iterable (tuple or list) of sentence objects drawn from the input document that together form the summary.

- normalize_word(word) [@staticmethod]
  - Returns: to_unicode(word).lower()
  - Preconditions: word must be acceptable to to_unicode (bytes or object convertible to text).
  - Exceptions: any exception raised by to_unicode or by calling .lower() on its result is propagated.

- stem_word(word)
  - Returns: self._stemmer(normalize_word(word))
  - Preconditions:
    - Instance must have been constructed with a callable _stemmer.
    - word must be acceptable to normalize_word.
  - Exceptions: any exception raised by normalize_word or by the stemmer is propagated.

- _get_best_sentences(sentences, count, rating, *args, **kwargs) [@staticmethod]
  - Purpose: given an iterable of sentences, a count policy, and a rating provider, return a tuple of selected sentences ordered by original document order.
  - Inputs:
    - sentences: finite iterable of sentence objects. The function will enumerate it (exhausting generators).
    - count: either a callable(selector) -> iterable of info-objects, or a non-callable passed to ItemsCount(count) to produce such a callable.
    - rating: either a callable rating(sentence, *args, **kwargs) -> comparable value, or a dict-like mapping from sentence -> rating. If mapping is used, positional and keyword args MUST be empty.
    - *args, **kwargs: forwarded to rating if rating is callable; forbidden when rating is mapping-like.
  - Internal info object (SentenceInfo): the implementation creates per-sentence info entries each exposing attributes:
    - sentence: original sentence object
    - order: zero-based ordinal index in the input iterable
    - rating: numeric or comparable score produced by rating(sentence, *args, **kwargs)
    (Note: the concrete code uses a namedtuple-like SentenceInfo with fields (sentence, order, rating). Implementers should create such a structure.)
  - Algorithm:
    1. Resolve rate:
       - If rating is a mapping (isinstance(rating, dict)), assert not args and not kwargs, then set rate = lambda s: rating[s].
       - Otherwise use the provided callable rating as rate.
    2. Enumerate sentences; build infos = (SentenceInfo(sentence, order, rate(sentence, *args, **kwargs)) for order, sentence in enumerate(sentences))
    3. Sort infos by rating descending (highest first).
    4. Ensure count is callable; if not, wrap it with ItemsCount(count).
    5. Apply count callable to the sorted infos to obtain selected infos.
    6. Sort selected infos by order ascending to restore document order.
    7. Return a tuple of i.sentence for each selected info, in document order.
  - Edge cases and errors:
    - If rating is a mapping and args or kwargs are provided: AssertionError is raised.
    - If rating is a mapping and a sentence is absent from the mapping: KeyError will be raised when rating lookup occurs.
    - ItemsCount behavior: if count is a string like "30%", ItemsCount will compute percentage of the total; if numeric, truncates to int; other unsupported types raise ValueError.
    - If count is larger than the number of sentences, the selection callable determines how many are returned (commonly all available).
    - The function materializes lists during sorting; memory usage is O(number of input sentences).
    - All exceptions from user-provided callables (rating, ItemsCount(), count-callable, or the stemmer) propagate unchanged.

## Raises:
- __init__:
  - ValueError if the provided stemmer parameter is not callable.

- normalize_word:
  - Propagates exceptions from to_unicode (e.g., UnicodeDecodeError) or from .lower()

- stem_word:
  - Propagates exceptions from normalize_word or from the configured stemmer callable.

- _get_best_sentences:
  - AssertionError if rating is a mapping and non-empty args/kwargs are provided.
  - KeyError if rating is a mapping and a sentence key is missing.
  - Any exceptions raised by the rating callable, ItemsCount construction, or the count callable will propagate.

- __call__ (base):
  - NotImplementedError to force subclasses to implement summarization behavior.

## Example (how to use in practice)
1. Prepare a concrete summarizer class that inherits from AbstractSummarizer and implements __call__(document, sentences_count). Typical __call__ steps:
   - Iterate the document's sentences.
   - For each token in a sentence, call normalize_word(token) or stem_word(token) to build features.
   - Compute a numeric score per sentence (the rating callable used below).
   - Call _get_best_sentences(sentences, sentences_count, rating) to obtain the top sentences selected by score and returned in original order.
   - Return the chosen sentences as a tuple or list.

2. Constructing an instance:
   - Use the default stemmer by invoking the concrete summarizer without arguments, or pass a custom callable that accepts a single normalized token and returns its stem.

3. Performing summarization:
   - Provide the concrete summarizer instance with a parsed document and a sentences_count (commonly an int or a string like "30%") and call the instance: the subclass's __call__ should return the summary.

4. Cleanup:
   - No cleanup is required for AbstractSummarizer itself. If the concrete summarizer uses external resources, ensure the subclass documents and implements any necessary cleanup.

Notes for implementers:
- Ensure SentenceInfo is implemented as a simple container with attributes sentence, order, rating (a namedtuple or small class is appropriate).
- Because normalize_word delegates to to_unicode, follow the project's text-encoding expectations (UTF-8 for bytes).
- Keep helper methods stateless so multiple threads may call normalize_word and _get_best_sentences safely if subclass state is not mutated.

### `sumy.summarizers._summarizer.AbstractSummarizer.__init__` · *method*

## Summary:
Validates and stores the stemmer callable on the instance, ensuring the summarizer has a usable stemming function.

## Description:
Known callers and lifecycle stage:
- Called during construction of any concrete Summarizer subclass that delegates stemmer initialization to the base class (typically via super().__init__(stemmer)).
- Typical instantiation happens in pipeline/factory code that chooses a concrete summarizer implementation and constructs it before using it to summarize a document.

Why this logic is a separate method:
- Centralizes the single responsibility of validating and assigning the stemming strategy used by all summarizers.
- Keeps subclass constructors simple (they can accept a stemmer parameter and forward it to this base initializer) and guarantees a consistent invariant (_stemmer is callable) across all subclasses.

## Args:
    stemmer (callable, optional): A callable that accepts a single token (string) and returns a stem/normalized form.
        - Default: null_stemmer (imported from nlp.stemmers), a callable that converts input to unicode and lowercases it.
        - Allowed values: any callable object. The callable is not further type-checked beyond being callable; it may raise its own exceptions when invoked later.
        - Typical behavior expected: accept a normalized token (string) and return a stem or canonical form.

## Returns:
    None

## Raises:
    ValueError: If the provided stemmer argument is not callable.
        - Exact message raised by the implementation: "Stemmer has to be a callable object"

## State Changes:
    Attributes READ:
        - None (the method does not read any existing self.<attr> fields)

    Attributes WRITTEN:
        - self._stemmer: set to the provided stemmer argument when validation passes

## Constraints:
    Preconditions:
        - The caller must provide either no argument (to use the default null_stemmer) or a callable object as stemmer.
        - No requirements on other instance attributes; this method works on a fresh or partially-initialized instance.

    Postconditions:
        - After successful completion, self._stemmer exists and is the same object passed as stemmer.
        - The invariant that self._stemmer is callable holds for the lifetime of the instance unless mutated later by other code.

## Side Effects:
    - Mutates the instance by assigning to self._stemmer.
    - No I/O, no network calls, and no mutation of objects outside self.
    - No invocation of the stemmer occurs during construction; any exceptions from the stemmer itself are deferred until it is later called (e.g., via stem_word).

### `sumy.summarizers._summarizer.AbstractSummarizer.__call__` · *method*

## Summary:
Defines the public summarization entry-point on a summarizer instance; the base implementation is abstract and raises NotImplementedError — subclasses must implement the logic that produces a summary from a document given a requested sentence count.

## Description:
This method is the canonical entry-point used by client code to produce a summary from a parsed document. Typical usage is to instantiate a concrete Summarizer subclass and call it with (document, sentences_count) at the stage where a document has been parsed and tokenized into sentences. The base implementation exists so all summarizers share the same callable signature and can be invoked interchangeably by pipelines or user code.

Why this is a separate method:
- It defines the public contract (signature, expected behavior) that all summarizer implementations must follow.
- Keeping it as an overridable method lets different summarization algorithms implement their own selection/ranking strategies while retaining a consistent external API.
- Helper methods on this class (stem_word, normalize_word, _get_best_sentences) are available to subclasses; separating algorithm implementation into __call__ keeps algorithm-specific logic out of the shared helpers.

## Args:
    document (object):
        An implementation-specific representation of the input to summarize (a parsed Document object, typically containing sentences). The AbstractSummarizer does not assume a concrete type; subclasses should document and validate the expected document shape.
    sentences_count (int or callable):
        The requested number of sentences to include in the summary. Concrete implementations commonly accept:
        - an integer n to request n sentences, or
        - a callable (or other protocol) accepted by the helper _get_best_sentences (see class helper) that selects/counts items.
        Subclasses may accept additional forms but should validate and document them.

## Returns:
    Iterable of sentence objects (implementation-specific):
        Concrete implementations should return an ordered collection (tuple/list) of sentence objects drawn from the input document representing the summary. The exact sentence type/structure is implementation-defined; many subclass implementations use the class helper _get_best_sentences which returns a tuple of sentences.

## Raises:
    NotImplementedError:
        Always raised by this base implementation. Subclasses MUST override __call__ to provide actual summarization behavior. If a caller invokes AbstractSummarizer.__call__ directly (i.e., on an instance whose class did not override this method), this exception is raised with the message "This method should be overriden in subclass".

## State Changes:
    Attributes READ:
        None in the base implementation. (Subclasses may read self._stemmer via stem_word or other attributes defined on the instance.)
    Attributes WRITTEN:
        None in the base implementation. Subclasses may update internal caches or state if needed, but such mutations are not performed by AbstractSummarizer.__call__ itself.

## Constraints:
    Preconditions:
        - The caller should provide a parsed document object appropriate for the concrete summarizer implementation.
        - sentences_count must be meaningful to the concrete implementation (commonly an int >= 0 or a callable accepted by _get_best_sentences).
    Postconditions:
        - For a properly implemented subclass: the returned value is an ordered collection of sentences selected from the provided document; the base method makes no guarantees because it is abstract.

## Side Effects:
    - The base implementation performs no I/O, external calls, or mutations outside of raising NotImplementedError.
    - Subclass implementations may perform I/O, call external services, or mutate document objects; such side effects are implementation-specific and must be documented by the subclass.

### `sumy.summarizers._summarizer.AbstractSummarizer.stem_word` · *method*

## Summary:
Convert the given token to the normal form and return its stem by invoking the summarizer's configured stemmer; does not modify object state.

## Description:
This method is a small helper used to obtain the stemmed form of a single token. It first normalizes the token (via normalize_word) and then calls the instance's configured stemmer (self._stemmer) with that normalized token.

Known callers and context:
- Intended callers are subclasses of AbstractSummarizer and other summarization pipeline code that need a canonical stem for a token during preprocessing or feature extraction. There are no further callers within this file; subclasses implement summarization logic and typically invoke this helper when they need to stem individual words.
- Lifecycle stage: invoked during token-level preprocessing or scoring inside a summarizer's __call__ implementation or other internal summarization steps.

Why this is a separate method:
- Encapsulates the common two-step operation (normalize then stem) so subclasses can reuse consistent normalization + stemming behavior without duplicating code.
- Allows the stemmer implementation to be swapped by passing a different callable into AbstractSummarizer.__init__ while keeping downstream code unchanged.

## Args:
    word (any): A token value to be stemmed. It will be passed to normalize_word (which converts it to a unicode string and lowercases it) before stemming. The method accepts any value that normalize_word/to_unicode can handle.

## Returns:
    Any: The return value produced by the configured stemmer when called with the normalized token. Typically this is a string (the stem), but the exact type and value depend on the stemmer callable provided during construction. No guarantees are made about immutability or exact type beyond "whatever the stemmer returns."

Edge-case returns:
- If the stemmer returns None or another non-string type, that value is propagated unchanged.
- If the stemmer raises an exception, that exception is propagated to the caller.

## Raises:
    Any exception raised by normalize_word/to_unicode or by the configured stemmer. This method does not raise its own new exceptions; it simply forwards exceptions raised by:
    - normalize_word (e.g., if the input cannot be converted to unicode)
    - self._stemmer (any exception from the stemmer implementation)

Note: AbstractSummarizer.__init__ raises ValueError if a non-callable is provided as the stemmer, so under normal construction self._stemmer should be callable.

## State Changes:
    Attributes READ:
        - self._stemmer : the stemmer callable configured at construction time
    Attributes WRITTEN:
        - None (this method does not modify any attributes)

## Constraints:
    Preconditions:
        - The AbstractSummarizer instance must have been constructed with a callable stemmer (AbstractSummarizer.__init__ enforces this).
        - The provided word must be acceptable to normalize_word (i.e., convertible to unicode by to_unicode).
    Postconditions:
        - No attributes on self are changed.
        - The normalized token is passed to the stemmer and the stemmer's return value is returned to the caller.

## Side Effects:
    - This method performs no I/O and does not itself call external services.
    - It invokes an external callable (self._stemmer), which may have side effects; any such side effects are determined by the stemmer implementation and are not introduced by this method itself.

### `sumy.summarizers._summarizer.AbstractSummarizer.normalize_word` · *method*

## Summary:
Converts the given word to a unicode/text string and returns a lowercase form suitable for downstream processing (for example, before stemming). This operation does not modify object state.

## Description:
Known callers:
- AbstractSummarizer.stem_word — called to normalize a token immediately before passing it to the configured stemmer.

Lifecycle / pipeline stage:
- This method is intended to be invoked during text normalization/token processing steps of the summarization pipeline whenever a word must be normalized to a canonical, lowercase text form prior to further processing (e.g., stemming, counting, matching).

Rationale for being a separate method:
- Centralizes normalization logic so all summarizers and the built-in stem_word implementation perform identical unicode conversion and lowercasing.
- Keeps stem_word small and readable by separating concerns (normalization vs. stemming).
- Allows subclasses or other helpers to reuse consistent normalization without duplicating to_unicode(...).lower().

## Args:
    word (Any): The input token to normalize. Must be an object acceptable to the repository's to_unicode converter (commonly a str/bytes-like object or other object with a sensible text representation).

## Returns:
    str: A text/unicode string (Python str) representing the input converted to unicode/text and lowercased. Example: input "Word" -> "word".

    Edge cases:
    - If the input is already a text string, it is returned lowercased.
    - If the input is not convertible, the conversion will fail and an exception from to_unicode will propagate (see Raises).

## Raises:
    - Any exception raised by the to_unicode conversion (for example, TypeError if the object cannot be converted to text). These exceptions are not caught here and will propagate to the caller.
    - Any exception raised by calling lower() on the converted value (unlikely when to_unicode returns a text string), e.g., AttributeError if to_unicode returns a non-text object without a lower method.

## State Changes:
    Attributes READ:
    - None (this is a static method; it does not read any self.<attr> attributes).

    Attributes WRITTEN:
    - None (this method does not modify object state).

## Constraints:
    Preconditions:
    - The caller should provide a value that is sensible to convert to text using to_unicode (commonly a string or bytes). There is no internal validation beyond calling to_unicode.

    Postconditions:
    - The return value is a text string in lowercase. No mutation of the input occurs.

## Side Effects:
    - None. This method performs pure data transformation and has no I/O, network, or global state side effects.

### `sumy.summarizers._summarizer.AbstractSummarizer._get_best_sentences` · *method*

## Summary:
Selects the highest-rated sentences from an iterable according to a provided rating and count policy, and returns the chosen sentence objects in their original document order.

## Description:
This helper performs the common selection step in a summarization pipeline: it computes a numeric rating for each input sentence, selects a subset of top-rated items based on the count policy, and returns the chosen sentences sorted by their original order (so the output preserves document order).

Typical callers (inferred usage):
- Summarizer code that, after computing per-sentence scores, needs to pick the top candidates to form the final summary.

Why this is a separate function:
- The selection procedure requires multiple well-defined steps (rate, global sort by rating, apply selection policy, restore original order). Encapsulating them prevents duplication, centralizes error conditions, and standardizes selection semantics across summarizers.

## Args:
    sentences (iterable): Iterable of sentence objects. The function fully consumes this iterable; if a generator is passed it will be exhausted.
    count (int or callable): 
        - If a non-callable (commonly an int), it is passed to ItemsCount(count) (imported from utils) to obtain a callable selector. ItemsCount is expected to return a callable that accepts an iterable of per-sentence info objects and returns an iterable of selected info objects.
        - If a callable, it must accept a single iterable of info objects (each exposing attributes 'sentence', 'order', 'rating') and return an iterable of selected info objects.
    rating (callable or dict-like): Two accepted forms:
        - Callable rating(sentence, *args, **kwargs) -> comparable value (used to rank sentences). The callable is invoked once per sentence as rate(s, *args, **kwargs).
        - Mapping-like object (e.g., dict) mapping sentence -> numeric rating. If a mapping is provided, additional positional and keyword arguments passed to this function are forbidden.
    *args: Positional arguments forwarded to the rating callable (only used when rating is callable).
    **kwargs: Keyword arguments forwarded to the rating callable (only used when rating is callable).

## Returns:
    tuple: A tuple of the selected sentence objects (the same objects yielded from the input iterable), ordered by their original position in the input. If no items are selected, an empty tuple is returned.

## Raises:
    AssertionError: If rating is a mapping (dict-like) but non-empty args or kwargs were provided. The code asserts not args and not kwargs.
    KeyError: If rating is a mapping and a sentence from the input iterable is not present as a key in the mapping (raised when mapping lookup occurs).
    TypeError / ValueError / Any exception from user callables: Any exception raised by the rating callable, ItemsCount(), or the count callable will propagate to the caller.
    Note: No exceptions are swallowed by this function.

## State Changes:
    Attributes READ:
        None (the function does not access or mutate external object attributes; it is a pure selection helper).
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - The input iterable 'sentences' must be finite and fully consumable by the function (it enumerates all items).
        - If rating is mapping-like, callers must not pass *args or **kwargs (otherwise AssertionError).
        - The rating callable or mapping must produce values that are mutually comparable (support ordering) so sorting by rating is valid.
        - ItemsCount(count) (when used) must return a callable compatible with the described contract.
    Postconditions:
        - The returned tuple contains zero or more sentences selected by the count policy and preserved in their original document order.
        - The function does not mutate the sentence objects or external state.

## Side Effects:
    - The function fully consumes the provided sentences iterable; generators will be exhausted.
    - Two sorts occur internally:
        1) All sentences are sorted by rating in descending order (global ranking).
        2) The selected items are sorted by original order to restore document order.
      As a result, memory usage scales with the number of input sentences (the implementation materializes lists when sorting).
    - No I/O, network calls, or external side effects are performed by the function itself.

## Edge cases and behavior notes:
    - Empty input: returns an empty tuple.
    - Duplicate sentence objects: allowed; if rating is a mapping, identical objects used as keys must be present accordingly.
    - If count > number of sentences, the selection callable (ItemsCount or custom) determines behavior; typically fewer than requested items are returned.
    - If count is a callable that expects a streaming input but the implementation provides a concrete list (because of prior sorting), the callable must accept an iterable/list; otherwise a TypeError may occur.
    - The per-sentence info objects used internally (referred to in code as SentenceInfo) are expected to expose attributes: 'sentence' (the original sentence object), 'order' (original zero-based index), and 'rating' (numeric score). The function returns the original 'sentence' attribute values from selected info objects.

## Algorithm (step-by-step):
    1. Determine 'rate' callable:
        - If rating is mapping-like, convert to rate = lambda s: rating[s] (and assert no args/kwargs).
        - Otherwise use the provided rating callable.
    2. Enumerate sentences and build per-sentence info objects: (sentence, order, rating).
    3. Sort all info objects by rating in descending order (highest rated first).
    4. Ensure 'count' is callable: if not, wrap via ItemsCount(count).
    5. Call the count callable with the sorted list of infos to obtain the selected infos.
    6. Sort the selected infos by their original order (ascending).
    7. Return a tuple of the 'sentence' from each selected info, in original document order.

