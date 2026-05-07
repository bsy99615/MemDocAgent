# `tf.py`

## `sumy.models.tf.TfDocumentModel` · *class*

## Summary:
Represents a document as a term-frequency (TF) model: counts terms, exposes frequencies, ordering by frequency, and simple normalization utilities.

## Description:
TfDocumentModel aggregates word tokens into a term-frequency Counter and provides convenience accessors used by ranking/summarization algorithms. Instantiate it when you need:
- a compact representation of a document's term counts,
- to compute normalized term frequencies (relative to the document's most frequent term),
- to obtain the Euclidean magnitude of the term-frequency vector (for cosine similarity or vector normalization),
- to list the most frequent terms in a document.

Known callers/factories:
- Typical callers are summarizers or text-ranking modules that compute TF or TF-IDF features per document.
- If you provide a single string as the input `words`, you must pass a tokenizer exposing a `to_words(unicode_text) -> Sequence[str]` method that will be used to split the string into tokens.

Motivation / responsibility:
- Encapsulates TF bookkeeping for one document so downstream code does not manage Counter logic, max-frequency computation, or simple normalizations repeatedly.

## State:
Attributes (private)
- _terms (collections.Counter[str -> int])
  - What it stores: mapping from stored term (lowercased unicode string) to integer count.
  - Valid values: integer counts >= 1 for present keys; absent keys are implicitly zero.
  - Invariant: keys are stored as unicode lowercased strings (unicode.lower applied at construction).
- _max_frequency (int)
  - What it stores: the maximum single-term count in _terms, or 1 when _terms is empty.
  - Valid values: positive integer >= 1.
  - Invariant: if _terms is non-empty, _max_frequency == max(_terms.values()); if _terms empty, _max_frequency == 1.

Notes about initialization parameters:
- words (Sequence[str] or string)
  - If a sequence: must be an iterable/sequence of string-like tokens (each element is expected to be convertible to unicode and to have .lower()).
  - If a string: a tokenizer must be provided; the tokenizer's to_words() will be called with the unicode-converted string to produce the token sequence.
- tokenizer (optional)
  - Required only when `words` is a string. Must provide to_words(unicode_text) -> Sequence[str].

Class invariants:
- _terms keys are normalized (lowercase unicode) and counts are nonnegative integers.
- _max_frequency >= 1 always holds.
- magnitude is computed from the current _terms and may be zero if the model has no terms.

## Lifecycle:
Creation:
- Call the constructor with either:
  - a sequence of tokens: TfDocumentModel(tokens)
  - a raw string and a tokenizer: TfDocumentModel(raw_text, tokenizer=my_tokenizer)
- Required constructor behaviors:
  - If `words` is a string and tokenizer is None -> raises ValueError.
  - If `words` is neither a string nor a Sequence -> raises ValueError.

Usage / ordering:
- There is no strict order required for read-only operations. Typical usage:
  1. Instantiate model.
  2. Query most_frequent_terms(), term_frequency(), normalized_term_frequency(), magnitude, and terms as needed.
- Methods do not mutate object state after construction; repeated reads are safe and idempotent.
- No explicit destruction/cleanup is required; object holds only in-memory collections.

Destruction:
- No resources to close; no context-manager interface. Standard Python garbage collection applies.

## Method map (dependencies & typical invocation)
- Mermaid flowchart (method call dependencies and typical invocation order):

graph LR
    A[__init__] --> B[_terms Counter populated]
    B --> C[magnitude property]
    B --> D[terms property]
    B --> E[most_frequent_terms(count)]
    B --> F[term_frequency(term)]
    F --> G[normalized_term_frequency(term, smooth)]
    A --> H[__repr__]

## Methods and behavior (summary)
- magnitude -> float
  - Returns the Euclidean norm (L2 norm) of the term-frequency vector: sqrt(sum(count^2 for count in _terms.values())).
  - If the model is empty (no terms), returns 0.0.
- terms -> iterable
  - Returns an iterable view of stored terms (the keys of the internal Counter). Terms are the lowercased unicode strings stored at construction time.
- most_frequent_terms(count=0) -> tuple[str,...]
  - Returns terms sorted by descending frequency.
  - Parameters:
    - count (int): number of top terms to return. Default 0 means "return all terms" in descending frequency order.
  - Behavior and edge cases:
    - If count == 0: returns all terms, in descending frequency order.
    - If count > 0: returns at most `count` terms (slicing the sorted descending list).
    - If count < 0: raises ValueError("Only non-negative values are allowed for count of terms.").
    - Ties are broken by the ordering of sorted() applied to items with equal counts (stable sort on Python's tuple order).
- term_frequency(term) -> int
  - Returns the raw integer count for the exact key `term` from _terms, or 0 if the term is not present.
  - Important: lookup is exact (no automatic lowercasing). Since stored keys are lowercased at construction, callers should pass the term in the same normalized form (lowercased unicode) to get the expected result.
- normalized_term_frequency(term, smooth=0.0) -> float
  - Computes the normalized frequency relative to the document's most frequent term:
    - frequency = term_frequency(term) / _max_frequency
    - returns smooth + (1.0 - smooth) * frequency
  - Use-case: smooth is a floor value to prevent zero; typical values are in range [0.0, 1.0).
  - Recommended: smooth should be between 0.0 and 1.0 inclusive. If smooth is outside that range, the method will still compute a numeric result, but it may fall outside [0.0, 1.0] and therefore is not recommended.
  - Behavior when term absent: frequency will be 0, so returned value will be `smooth`.
- __repr__() -> str
  - Human-readable representation: "<TfDocumentModel {pformat(_terms)}>" where the Counter mapping is pretty-printed.

## Raises:
- __init__:
  - ValueError: "Tokenizer has to be given if ``words`` is not a sequence."
    - Trigger: words is a string (string_types) and tokenizer is None.
  - ValueError: "Parameter ``words`` has to be sequence or string with tokenizer given."
    - Trigger: words is neither a string nor a Sequence.
- most_frequent_terms:
  - ValueError: "Only non-negative values are allowed for count of terms."
    - Trigger: count < 0

## Example:
- Constructing from a token sequence:
  - tokens = ["The","quick","brown","fox","the","fox"]
  - model = TfDocumentModel(tokens)
  - model._terms -> Counter({'the':2,'fox':2,'quick':1,'brown':1}) (keys stored lowercased)
  - model.magnitude -> sqrt(2^2 + 2^2 + 1^2 + 1^2) = sqrt(10)
  - model.most_frequent_terms(1) -> ('the',) or ('fox',) depending on tie-breaker order
  - model.term_frequency('the') -> 2
  - model.normalized_term_frequency('the') -> 2 / 2 = 1.0 (smooth default 0.0 yields 1.0)

- Constructing from raw text (requires a tokenizer with to_words):
  - model = TfDocumentModel("Raw text...", tokenizer=my_tokenizer)
  - tokenizer.to_words() will be called with the unicode-converted input to produce tokens.

Notes / implementation hints for reimplementation:
- Ensure string/sequence detection matches this module's compatibility helpers: use the module's string_types and Sequence checks in the same order (string_types check first).
- When building the Counter, apply unicode.lower to each token (map(unicode.lower, words)) to normalize keys.
- Set _max_frequency to max(self._terms.values()) if any terms exist, otherwise 1 to avoid division by zero in normalized_term_frequency.
- magnitude should compute sqrt of sum of squared counts (L2 norm).

### `sumy.models.tf.TfDocumentModel.__init__` · *method*

## Summary:
Initialize the instance by converting the input document (sequence of tokens or raw string) into a normalized term-frequency representation and compute the maximum token frequency for later TF computations.

## Description:
This initializer is called when a TfDocumentModel object is created. It validates the incoming `words` argument, converts raw string input to a token sequence when a tokenizer is provided, normalizes tokens to lowercase unicode, counts token frequencies, and records the highest observed frequency.

Typical callers and context:
- Constructing a document-level TF model during preprocessing or feature-extraction pipelines, e.g. when transforming raw documents into term-frequency representations used by TF/IDF or similarity algorithms.
- Code that builds per-document statistics prior to computing relevance or similarity will instantiate this object.

Why this method exists separately:
- Centralizes input validation (sequence vs string + tokenizer) and token normalization/counting in one place so all downstream TF computations can assume consistent, precomputed attributes (_terms and _max_frequency).

## Args:
    words (Sequence[str] or string_types):
        - If a Sequence: an iterable of token strings (each element is expected to be string-like).
        - If a string (string_types): interpreted as raw document text and MUST be tokenized via the `tokenizer` argument.
        - No implicit coercion of non-string elements; elements should be compatible with the unicode.lower function used for normalization.
    tokenizer (optional):
        - Type: object providing a method to_words(text: unicode) -> Sequence[str].
        - Default: None
        - Required when `words` is a string. The method will be called as tokenizer.to_words(to_unicode(words)) to obtain a token sequence.

## Returns:
    None
    - As a constructor, it does not return a value. It sets instance attributes described below.

## Raises:
    ValueError:
        - If `words` is a string and `tokenizer` is None:
            Raises ValueError("Tokenizer has to be given if ``words`` is not a sequence.")
        - If `words` is neither a string nor a Sequence:
            Raises ValueError("Parameter ``words`` has to be sequence or string with tokenizer given.")

## State Changes:
Attributes READ:
    - None (the method does not read any existing self.<attr> fields).

Attributes WRITTEN:
    - self._terms (collections.Counter): Mapping from each normalized token (unicode, lower-cased) to its absolute frequency in the input token sequence.
    - self._max_frequency (int): The maximum frequency among values in self._terms; guaranteed to be >= 1 after initialization.

Concrete behavior:
    - If the final token sequence is non-empty, self._terms will be Counter({'token': count, ...}) and self._max_frequency == max(self._terms.values()).
    - If the final token sequence is empty (no tokens), self._terms will be an empty Counter() and self._max_frequency will be set to 1.

## Constraints:
Preconditions:
    - If `words` is a string, `tokenizer` must be non-None and implement to_words(unicode) -> Sequence[str].
    - If `words` is a Sequence, each element should be string-like (support lowercasing via unicode.lower).
    - The module-level helpers to_unicode and unicode (from _compat) are available and should be used for conversion and normalization in the same manner.

Postconditions:
    - After initialization, the instance has a deterministic, normalized token frequency map (self._terms) and a safe non-zero _max_frequency (>=1) suitable for later TF computations (avoids division-by-zero when normalizing by max frequency).

## Side Effects:
    - No file, network, or external I/O is performed by this method itself.
    - If `tokenizer.to_words` has side effects, those will occur (this initializer calls that method when `words` is a string).
    - Mutates only the newly constructed instance by assigning self._terms and self._max_frequency.

## Implementation notes (step-by-step for reimplementation):
    1. Check if `words` is a string (use string_types). If it is and `tokenizer` is None, raise the exact ValueError message: "Tokenizer has to be given if ``words`` is not a sequence."
    2. If `words` is a string and `tokenizer` is provided, call tokenizer.to_words(to_unicode(words)) to obtain a sequence of tokens. Use the same to_unicode helper to coerce the input to unicode before tokenization.
    3. If `words` is not a string and not an instance of Sequence, raise the exact ValueError message: "Parameter ``words`` has to be sequence or string with tokenizer given."
    4. Build a collections.Counter over tokens after normalizing each token via unicode.lower (i.e., apply unicode.lower to each element of the token sequence). Assign this Counter to self._terms.
    5. Compute self._max_frequency:
         - If self._terms is non-empty: set to the maximum value in self._terms.values().
         - If self._terms is empty: set to 1 (explicit default).
    6. Do not perform any additional normalization (such as filtering punctuation or stopwords) in this initializer — only lowercase and count as described.

## Example usage:
    - From a token sequence:
        TfDocumentModel(words=['This', 'is', 'this'])  # _terms -> Counter({'this':2,'is':1}), _max_frequency -> 2
    - From raw text with tokenizer:
        TfDocumentModel(words='Raw text', tokenizer=tokenizer)  # -> tokenizer.to_words(to_unicode('Raw text')) used first

### `sumy.models.tf.TfDocumentModel.magnitude` · *method*

## Summary:
Computes and returns the L2 (Euclidean) norm of the document's term-frequency vector as a non-negative float; does not modify the object.

## Description:
This read-only property calculates the Euclidean magnitude of the vector formed by the term frequencies stored in the model (self._terms). It iterates over the frequency counts and returns sqrt(sum(freq^2)).

Known callers and context:
- No direct callers are visible inside this class definition. In typical usage patterns, this property is queried when normalizing document vectors or computing similarity measures (for example, cosine similarity) during retrieval, ranking, or clustering pipelines. The property is evaluated at the point a caller needs the vector length for normalization or comparison.

Why this is a separate property:
- The magnitude is a reusable, self-contained computation over the model's internal term-frequency vector. Exposing it as a property avoids duplicating the L2-norm calculation across callers and provides a clear, semantic API for consumers that need the vector length.

## Args:
- None. This is a parameterless, read-only property.

## Returns:
- float: The Euclidean norm (L2) of the term-frequency vector.
  - Always >= 0.0.
  - If the model contains no terms (self._terms is empty), returns 0.0.
  - The return type is a Python float (result of math.sqrt).

## Raises:
- None. The implementation performs numeric operations on the values of self._terms; given the class invariant that self._terms is a collections.Counter of integer counts (set in __init__), no exceptions are raised by this method under normal class usage.

## State Changes:
- Attributes READ:
    - self._terms (reads its .values() to obtain frequency counts)
- Attributes WRITTEN:
    - None. This property does not mutate any attributes.

## Constraints:
- Preconditions:
    - self._terms must be a mapping-like object whose values are numeric (integers/floats). The class initializer constructs self._terms as a collections.Counter of lowercased tokens, so this precondition holds for instances created via the provided constructor.
- Postconditions:
    - The object state is unchanged.
    - The return value is the correct Euclidean norm computed from the current snapshot of self._terms.

## Side Effects:
- None. There is no I/O, no external service calls, and no mutation of objects outside self. The method performs a pure computation over in-memory data.

## Complexity:
- Time: O(n) where n is the number of unique terms (len(self._terms)).
- Space: O(1) additional space beyond iterating the term frequencies.

### `sumy.models.tf.TfDocumentModel.terms` · *method*

## Summary:
Returns an iterable view of the document's vocabulary terms (the keys of the internal term-frequency mapping) without modifying the object's state.

## Description:
This property exposes the set of distinct terms that appear in this document model. The underlying mapping (_terms) is a collections.Counter built in the object's constructor from the provided words; therefore the returned items reflect the vocabulary derived at initialization (each term is stored in lowercase). There are no internal callers of this property within the TfDocumentModel class; it exists to allow external components (for example, vectorizers, summarizers, or other consumers of document-term information) to iterate over the vocabulary when constructing vectors, computing similarities, or exporting the model.

This logic is provided as a distinct read-only property rather than inlined to:
- Provide a stable public API for accessing the model's vocabulary.
- Encapsulate access to the internal Counter so callers do not need to know implementation details.
- Allow future changes to the underlying storage (e.g., switching from Counter to another mapping) without changing callers.

## Args:
None.

## Returns:
- type: an iterable view of term strings (the result of self._terms.keys()).
- details: In Python 3 this is typically a keys-view (e.g., dict_keys) providing an iterable view over the vocabulary. In Python 2, this may be a list of strings.
- term values: each term is a lowercase text string (as produced by unicode.lower in the constructor).
- edge cases: if the model has no terms (empty input sequence), an empty iterable is returned.

## Raises:
None. This property does not raise exceptions itself. (It assumes the object has been properly initialized so that self._terms exists; otherwise attribute access will raise AttributeError as usual.)

## State Changes:
- Attributes READ: self._terms
- Attributes WRITTEN: None

## Constraints:
- Preconditions:
    - The TfDocumentModel instance must be initialized (its constructor sets self._terms). Calling terms on an uninitialized instance will raise AttributeError.
- Postconditions:
    - The internal state is unchanged.
    - The returned iterable reflects the vocabulary present in self._terms at the time of the call (it may reflect later mutations if the underlying mapping is mutated externally).

## Side Effects:
- None local to this method: no I/O, no external service calls.
- If external code mutates the returned view/object (possible depending on Python version/type), that can affect the underlying _terms mapping; the property itself performs no mutation.

### `sumy.models.tf.TfDocumentModel.most_frequent_terms` · *method*

## Summary:
Return an immutable sequence of the document's terms ordered by descending raw frequency (highest-frequency first). The returned terms are lowercased and the method does not modify the model's state.

## Description:
Known callers and context:
- Typically called by downstream components performing summarization, feature extraction, ranking, or indexing that need the most common tokens for a document after a TfDocumentModel has been constructed.
- Lifecycle: invoked after constructing TfDocumentModel (the constructor builds self._terms from input words). Used as a read-only inspection utility during analysis or feature-selection stages.

Why this is a separate method:
- Encapsulates the common pattern of ordering term-frequency pairs and selecting top-N terms so callers need not duplicate sorting/slicing logic.
- Provides a clear, intention-revealing API for consumers that need ranked term lists without depending on the internal Counter representation.

## Args:
    count (int, optional):
        - Default: 0
        - Semantics:
            * 0: return all distinct terms ordered by descending frequency.
            * positive integer N: return the top N terms (if fewer than N distinct terms exist, returns as many as available).
            * negative values: not allowed and will trigger a ValueError.
        - Type constraints and runtime behavior:
            * The method is implemented assuming an integer count. Passing a non-integer may lead to a TypeError:
                - If count is not comparable to 0 (e.g., a string), the comparison (count == 0 or count > 0) will raise TypeError.
                - If count is a numeric but non-integer (e.g., 2.0), the comparison to 0 succeeds; for positive non-integral values the method will attempt to slice the tuple with a non-integer and that will raise TypeError.
            * To avoid these issues, callers should pass a non-negative int.

## Returns:
    tuple[str]:
        - An immutable tuple of term strings ordered from most frequent to least frequent.
        - Terms are lowercased (the constructor lowercases words when building self._terms).
        - If count == 0: returns all terms.
        - If count > 0: returns the first count elements of the ordered tuple (possibly fewer if the document has fewer distinct terms).
        - If the document contains no terms: returns an empty tuple.

## Raises:
    ValueError:
        - Trigger: when count is negative (i.e., count < 0). The exact raised message is:
          "Only non-negative values are allowed for count of terms."
    TypeError:
        - Not explicitly raised by the method itself but may occur:
            * If count cannot be compared with 0 (e.g., a string) the initial comparison will raise TypeError.
            * If count is a numeric non-integer and > 0 (e.g., 2.0), slicing terms[:count] will raise TypeError because slice indices must be integers or None.
        - Recommendation: pass an int to avoid TypeError.

## State Changes:
    Attributes READ:
        - self._terms: read to obtain term-frequency pairs via self._terms.items()
    Attributes WRITTEN:
        - None. The method does not mutate self or any external objects.

## Constraints:
    Preconditions:
        - The TfDocumentModel instance must be initialized so that self._terms exists and maps term strings to numeric frequencies (the class constructor creates a collections.Counter).
        - Caller should pass a non-negative integer for count to avoid TypeError or ValueError.
    Postconditions:
        - self remains unchanged.
        - The returned tuple is sorted by descending raw frequency (highest first).
        - Terms in the returned tuple are lowercased, as produced by the constructor.

## Tie-breaking and determinism:
    - Terms with equal frequency are ordered according to Python's sort stability combined with the iteration order of self._terms.items() at the time of the call. The exact order for ties therefore depends on the underlying mapping's iteration order (which, on modern Python implementations, often reflects insertion order) but is deterministic for a given self._terms content and Python runtime.

## Complexity and memory:
    - Time: O(k log k) where k is the number of distinct terms (cost dominated by sorting).
    - Space: O(k) additional memory for the list/tuple of sorted terms returned.

## Side Effects:
    - No I/O, network, or external service interactions.
    - No mutations to objects outside self.
    - Purely reads in-memory state and returns a new tuple derived from it.

## Usage (prose example):
    - After constructing TfDocumentModel from a document's token list, call most_frequent_terms(10) to obtain the top ten most frequent (lowercased) terms for use in ranking or feature selection.

### `sumy.models.tf.TfDocumentModel.term_frequency` · *method*

## Summary:
Return the non-normalized count of occurrences for a given term in the document model, without modifying the model.

## Description:
Performs a direct lookup in the model's internal Counter produced at initialization and returns the stored integer count (or zero if missing). Known internal caller: normalized_term_frequency (used to compute a normalized frequency for the same document). This operation is isolated as its own method to centralize the mapping lookup and default-zero behavior, keeping other frequency-related methods simple and making the lookup easy to override in subclasses if needed.

## Args:
    term (hashable):
        The lookup key to query in the internal term mapping.
        - Typical usage: pass a string exactly in the canonical form used when the model was created (the class __init__ lowercases all input words via unicode.lower). The method does not perform normalization (lowercasing) itself.
        - Any hashable object may be used; unhashable objects (e.g., list) will raise a TypeError from the underlying mapping.

## Returns:
    int:
        - The exact non-negative integer count stored for the key in self._terms.
        - If the key is not present in the mapping, returns 0.

## Raises:
    TypeError:
        - If the provided term is unhashable (e.g., a list), the underlying mapping lookup will raise TypeError.
    AttributeError:
        - If self._terms does not exist (for example, if the instance was not properly initialized or has been mutated externally), attempting to access it will raise AttributeError.

## State Changes:
    Attributes READ:
        - self._terms
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The instance must have been initialized so that self._terms is a mapping-like object (the class __init__ sets it to a collections.Counter with lowercased string keys).
        - Callers should supply the term in the same canonical form (lowercased unicode strings) used by the model for reliable matches.
    Postconditions:
        - No mutation of self or external state.
        - The return value equals self._terms.get(term, 0) and is non-negative.

## Side Effects:
    - None. The method performs no I/O, makes no external calls, and does not mutate objects outside of self.

## Examples:
    - If the document contained the word "Example" twice, the internal mapping stores the key 'example' -> 2. Then:
        term_frequency('example') -> 2
        term_frequency('Example') -> 0  (unless the caller lowercases before lookup)
    - For a missing key:
        term_frequency('absent') -> 0

### `sumy.models.tf.TfDocumentModel.normalized_term_frequency` · *method*

## Summary:
Compute a smoothed, normalized term-frequency score for a given token in this document, returning a float that scales the raw count by the document's maximum term count and applies additive smoothing.

## Description:
This method is called on a TfDocumentModel instance when a normalized term frequency (TF) value is needed for weighting, ranking, or feature extraction. It performs two small steps — obtain the raw term count via term_frequency, normalize it by the document's maximum term count, then apply an additive smoothing parameter.

Known callers:
    - No callers within this repository were found during inspection. Typically invoked by scoring/feature extraction code that needs per-term TF values (e.g., TF-IDF calculation or ranking components).

Why this is a separate method:
    - Encapsulates normalization and smoothing logic in one reusable unit so other components can compute comparable TF scores without duplicating division and smoothing code.
    - Keeps term-frequency retrieval (term_frequency) single-responsibility and separates normalization concerns, making the behavior easy to override or mock in tests.

## Args:
    term (str):
        The token whose normalized frequency is requested. Note: keys stored in the model are lowercased when the model is constructed; callers should pass a token that matches the stored form (typically lowercased) for expected results.
    smooth (float, optional):
        Additive smoothing parameter. Defaults to 0.0.
        - Typical/expected range: 0.0 <= smooth <= 1.0 (not enforced). When in this range the returned value is bounded between smooth and 1.0.
        - The method accepts any float; passing values outside [0,1] will produce values outside the conventional [smooth, 1.0] interval.

## Returns:
    float:
        Computed as smooth + (1.0 - smooth) * (term_count / _max_frequency).
        - When smooth is in [0.0, 1.0] and under the class invariants, return value is in the closed interval [smooth, 1.0].
        - If the document contains no terms, _max_frequency is 1 (see class invariant) and term_count will be 0, so this method returns smooth.
        - Always a Python float.

## Raises:
    This method does not explicitly raise exceptions.
    - Under normal class invariants there is no division-by-zero because _max_frequency is set to max(self._terms.values()) if terms exist, otherwise 1.
    - If the instance's invariants have been violated externally (e.g., _max_frequency set to 0), a ZeroDivisionError could occur; such mutation is outside normal usage.

## State Changes:
    Attributes READ:
        - self._max_frequency (used to normalize the raw count)
        - self._terms (indirectly read through term_frequency)
    Attributes WRITTEN:
        - None. This method does not modify the instance state.

## Constraints:
    Preconditions:
        - The TfDocumentModel instance should have been constructed using its __init__, which ensures:
            * self._terms is a mapping (Counter) of lowercased tokens to integer counts.
            * self._max_frequency is an integer >= 1 (or at least non-zero) under normal use.
        - Caller should supply the term in the same form as stored keys (case-sensitive match); by convention use lowercased tokens.

    Postconditions:
        - The instance remains unchanged.
        - The returned float equals smooth + (1.0 - smooth) * (term_frequency(term) / self._max_frequency).

## Side Effects:
    - None. The method performs no I/O, network calls, or mutation of objects outside self.

### `sumy.models.tf.TfDocumentModel.__repr__` · *method*

## Summary:
Returns a concise, developer-facing textual representation of the object that includes a pretty-printed view of the instance's _terms attribute.

## Description:
This dunder representation is used when the object is inspected or converted to its official string form for debugging and logging (for example via the built-in repr(), when shown in an interactive REPL, or when included in log messages). It creates a single-line representation that embeds the pretty-printed contents of self._terms.

Known callers / invocation contexts:
- repr(instance) — explicit calls to produce the canonical representation.
- Interactive interpreter / debugger — when the object value is displayed.
- Logging or debugging code that formats objects into messages.
- Any code that uses format() or string interpolation that triggers __repr__.

Why this is a separate method:
- __repr__ is the standard Python protocol for an object's official string representation; implementing it as its own method provides a consistent, single place to control how the model is displayed.
- Keeping formatting logic here (using pprint.pformat) centralizes representation behavior and avoids duplicating pretty-printing elsewhere in the class or external utilities.

## Args:
This method takes no explicit arguments.

## Returns:
str (text)
- A string of the form "<TfDocumentModel %s>" where %s is the result of pprint.pformat(self._terms).
- If self._terms is empty, the formatted portion will be the printed representation of the empty container (e.g., "{}" or "[]").
- The return value is a textual representation intended for debugging; it is not guaranteed to be a stable serialization format.

## Raises:
- AttributeError: if the instance does not have the attribute _terms (accessing self._terms will raise).
- Any exception raised during formatting of contained items may propagate:
  - If an element inside self._terms has a __repr__ that raises an exception, that exception will propagate out of this method.
  - pprint.pformat itself generally handles nested containers safely, but exceptions from user-defined contained objects are not intercepted here.

## State Changes:
Attributes READ:
- self._terms

Attributes WRITTEN:
- None (this method does not mutate the instance)

## Constraints:
Preconditions:
- The object must have an attribute named _terms (typically set during initialization).
- The contents of _terms should be representable by Python's repr() protocol; otherwise, exceptions from contained objects' __repr__ may occur.

Postconditions:
- No state on the object is changed.
- A string describing the current state of self._terms is returned.

## Side Effects:
- No I/O, network access, or external service calls are performed.
- Only reads the in-memory attribute self._terms and calls pprint.pformat to create a textual representation; any side effects come only from user-defined __repr__ implementations on objects contained within _terms (those would be external to this method).

