# `sum_basic.py`

## `sumy.summarizers.sum_basic.SumBasicSummarizer` · *class*

## Summary:
An extractive summarizer implementing the SumBasic algorithm: rates sentences by average per-word document probabilities, repeatedly selects the best sentence, updates word probabilities, and returns the top sentences chosen for a summary.

## Description:
SumBasicSummarizer is a concrete AbstractSummarizer subclass that implements the SumBasic selection/rating strategy. It is intended to be instantiated directly (or by higher-level factories) and then called as a function with a parsed Document-like object and a desired sentence count. Typical call pattern used by pipelines:
- Instantiate summarizer (optionally provide a custom stemmer via the base-class constructor).
- Optionally configure the stop word set (summarizer.stop_words = iterable_of_words).
- Produce a summary by calling summarizer(document, sentences_count).

Responsibilities and boundaries:
- Implements SumBasic-specific scoring and selection logic; delegates token normalization/stemming to AbstractSummarizer (normalize_word, stem_word) and the final sentence-selection output ordering to AbstractSummarizer._get_best_sentences.
- Does not perform document parsing or tokenization; expects a document object whose .sentences attribute is an iterable of sentence objects and where each sentence exposes a .words iterable of tokens.
- Does not manage external resources or perform I/O.

When to use:
- Use this class when you need a simple, unsupervised extractive summarizer based on document-level term frequencies and progressive re-weighting of selected words (the SumBasic approach).

## State:
Instance attributes (declared/used by this class or inherited):
- _stop_words (frozenset):
    - Type: frozenset[str] (strings in canonical normalized form).
    - Default: frozenset() (empty).
    - Invariant: always a frozenset of normalized words (normalization uses self.normalize_word).
    - Access: read via stop_words property; set via stop_words setter which normalizes and freezes the provided iterable.
- _stemmer (callable) — inherited from AbstractSummarizer:
    - Type: callable(normalized_word) -> stem
    - Default: the base-class null_stemmer (returns normalized token or lowercased unicode).
    - Invariant: must be callable for the life of the instance.

Notes about helper methods (members referenced by this class):
- normalize_word(token): inherited static/pure helper that converts to unicode and lowercases the token. Used for canonicalizing tokens and for normalizing stop words.
- stem_word(token): inherited helper that calls normalize_word(token) then applies the configured _stemmer; used to obtain stems.
- _get_best_sentences(sentences, count, rating): inherited helper used to transform ratings into the final selected sentences ordered by original document order.

Class invariants:
- _stop_words is always a frozenset of normalized tokens (no duplicates, membership queries are efficient).
- _stemmer is callable (the AbstractSummarizer constructor enforces this).
- All token comparisons for stop-word filtering should be performed in the token form consistent with how stop words were stored (stop words are normalized).

## Lifecycle:
Creation:
- Constructor: no class-specific __init__; SumBasicSummarizer inherits AbstractSummarizer.__init__(stemmer=null_stemmer).
- Required argument: none. Optional argument: stemmer (callable) if a custom stemmer is required.
- Example instantiation: create an instance with default stemmer by calling SumBasicSummarizer().

Configuration (optional):
- Set stop words via the attribute setter: summarizer.stop_words = iterable_of_words
    - Each provided word will be normalized by self.normalize_word before insertion into the internal frozenset.
    - If words is not iterable or normalization raises an error, that exception propagates.

Usage:
- Invoke the instance as a callable: summarizer(document, sentences_count)
    - document must have a .sentences attribute; each sentence must have a .words iterable.
    - sentences_count is passed through to the selection helper and dictates how many sentences are returned (the concrete selection behavior follows AbstractSummarizer._get_best_sentences semantics).
- Typical internal call sequence (high-level):
    1. __call__ reads document.sentences and calls _compute_ratings(sentences).
    2. _compute_ratings builds an initial TF mapping (_compute_tf) and a per-sentence list of content words (_get_content_words_in_sentence).
    3. Repeatedly:
       - select best sentence index via _find_index_of_best_sentence(word_freq, sentences_as_words),
       - pop that sentence and assign a rating (0, -1, -2, ...),
       - update word_freq via _update_tf(word_freq, best_sentence_words) (squares values for the words present).
    4. After ratings are computed, __call__ delegates to _get_best_sentences(document.sentences, sentences_count, ratings) which returns selected sentences in document order.
- Required sequencing: no special ordering is required by callers other than calling the instance after any desired configuration. Internally, other helper methods assume the data initialization performed by _compute_tf and the parallel lists alignment during the selection loop.

Destruction:
- No explicit cleanup is required. The class does not open resources requiring manual release.

## Method Map:
graph LR
    A[__call__(document, sentences_count)] --> B[_compute_ratings(sentences)]
    B --> C[_compute_tf(sentences)]
    C --> D[_get_all_content_words_in_doc(sentences)]
    D --> E[_get_all_words_in_doc(sentences)]
    E --> F[_stem_words(words)]
    F --> G[stem_word(token)]
    B --> H[_get_content_words_in_sentence(sentence)]
    H --> I[_normalize_words(words)]
    I --> J[_filter_out_stop_words(words)]
    J --> F[_stem_words(words)]
    B --> K[_find_index_of_best_sentence(word_freq, sentences_as_words)]
    K --> L[_compute_average_probability_of_words(word_freq, content_words)]
    B --> M[_update_tf(word_freq, words_to_update)]
    A --> N[_get_best_sentences(sentences, count, ratings)](inherited)

(Flow explanation: __call__ orchestrates rating computation then defers final sentence selection to AbstractSummarizer._get_best_sentences. Rating computation composes TF computation, per-sentence content extraction (normalize → filter → stem), repeated selection (_find_index_of_best_sentence) and in-place TF updates (_update_tf).)

## Raises:
Exceptions that can be raised by SumBasicSummarizer (directly or by inherited behavior), and when they occur:

- ValueError (from AbstractSummarizer.__init__):
    - Trigger: Constructing the instance with a non-callable stemmer argument. Example: SumBasicSummarizer(stemmer=42) will raise ValueError("Stemmer has to be a callable object").

- AttributeError:
    - Trigger: Calling summarizer(document, sentences_count) when document has no .sentences attribute, or when any sentence lacks a .words attribute and a method attempts to access it.

- TypeError:
    - Trigger: Passing non-iterable arguments where iterables are expected (e.g., non-iterable sentences), or when normalization/stemming routines receive invalid token types. TypeErrors from underlying helpers propagate.

- KeyError:
    - Trigger: During scoring, lookup into the word frequency mapping may fail if a sentence contains a token not present in the mapping passed to _compute_average_probability_of_words or if the rating mapping passed to _get_best_sentences is missing a sentence key. Such key errors propagate.

- ArithmeticError/Other numeric exceptions:
    - Trigger: If numeric values in the word frequency mapping are not arithmetic-compatible (e.g., multiplying non-numeric types in _update_tf), arithmetic operations may raise TypeError or other exceptions.

- Any exception raised by normalize_word, stem_word, or the configured _stemmer:
    - normalize_word may raise errors when converting bytes to text or calling .lower(); a custom stemmer may raise its own exceptions. These propagate out of the summarizer.

Notes:
- SumBasicSummarizer does not catch exceptions thrown by helper methods; callers should anticipate propagation from normalization, stemming, mapping lookups, and numeric operations.

## Example:
- Creation:
    - Instantiate using the default stemmer: create a SumBasicSummarizer() instance.
    - Optionally supply a custom stemmer callable to the constructor if specialized stemming is required.
- Configuration:
    - Set stop words before summarization: assign an iterable of words to summarizer.stop_words; each word will be normalized (lowercased/converted to unicode) and stored in a frozenset.
- Summarization call:
    - Provide a parsed document object with a .sentences iterable where each sentence has a .words iterable of tokens.
    - Call the instance with the document and desired sentence count: summarizer(document, sentences_count)
    - The returned value is whatever AbstractSummarizer._get_best_sentences yields (commonly a tuple/list of selected sentence objects in original document order).
- Behavior summary:
    - The algorithm computes document-level TF as normalized-and-stemmed content-word frequencies, converts those to probabilities, rates sentences by average probability of their content words, selects the best sentence, squares the probabilities for words in the selected sentence (decreasing their future influence), and repeats until all sentences are scored; ratings are then used to pick the top sentences.

Implementation notes for reimplementation:
- Use the provided sequence of helper operations as shown in the Method Map; ensure stop words are normalized before membership tests.
- Ratings mapping: the implementation assigns integer scores in decreasing sequence starting at 0 for the first-selected sentence, then -1, -2, ... This numeric convention makes larger numbers correspond to earlier selections.
- Maintain alignment between sentences_list and sentences_as_words while popping by index during the selection loop.
- Ensure _update_tf mutates the local word_freq mapping in-place (squaring values) before the next selection iteration.

### `sumy.summarizers.sum_basic.SumBasicSummarizer.stop_words` · *method*

## Summary:
Sets the summarizer's stop-word set by normalizing each provided word and storing them as an immutable frozenset, updating the object's internal stop-word state used during content-word filtering.

## Description:
Known callers and context:
- Typically invoked by client/configuration code via attribute assignment (e.g., summarizer.stop_words = iterable_of_words) during summarizer setup or before calling the summarizer on a document.
- There are no internal direct calls to the setter inside SumBasicSummarizer; the summarization pipeline (e.g., __call__) expects stop words to be configured beforehand so that sentence content-word filtering excludes them.

Why this logic is a separate setter:
- Normalizing each stop word and storing them as a frozenset centralizes the normalization and deduplication logic in one place.
- Using a frozenset provides efficient membership tests during sentence filtering elsewhere in the class (e.g., _filter_out_stop_words).
- Implementing normalization here keeps callers concise (they supply raw words) and ensures a consistent canonical form for comparisons.

## Args:
    words (iterable[str]): An iterable of words/tokens to be treated as stop words. Each element will be passed to self.normalize_word before being added to the internal set.
    - Allowed values: any iterable whose items are acceptable input for self.normalize_word (e.g., str tokens).
    - Empty iterable is allowed and yields an empty stop-word set.

## Returns:
    None
    - Side effect: updates self._stop_words in-place. The method does not return a value.

## Raises:
    TypeError: If 'words' is not iterable (raises while attempting to iterate/map or when frozenset is constructed).
    Any exception raised by self.normalize_word for a specific element will propagate (e.g., ValueError, TypeError) — the setter does not catch or wrap such exceptions.

## State Changes:
    Attributes READ:
        - self.normalize_word (method) — invoked for each element in words
    Attributes WRITTEN:
        - self._stop_words (frozenset) — replaced with a frozenset of normalized words

## Constraints:
    Preconditions:
        - The object must have a callable self.normalize_word method available.
        - The caller should provide an iterable of items compatible with self.normalize_word.
    Postconditions:
        - After the call, self._stop_words is a frozenset containing the result of applying self.normalize_word to each element of the provided iterable (duplicates removed).
        - Subsequent membership checks against self.stop_words (the property) will consult this frozenset.

## Side Effects:
    - Mutates the summarizer instance by replacing self._stop_words.
    - No I/O or external service calls are performed.
    - No modification to objects outside self besides possible exceptions propagated from normalize_word.

### `sumy.summarizers.sum_basic.SumBasicSummarizer.__call__` · *method*

## Summary:
Acts as the callable entry point for the summarizer: given a document and desired sentence count, it computes per-sentence ratings and returns the selection produced by the summarizer's selection routine. This method itself does not mutate the summarizer's attributes.

## Description:
This method is the public call operator for the summarizer object, allowing user code or other library code to produce a summary by invoking the summarizer instance like a function (e.g., summarizer(document, 5)). It performs two steps in sequence:
1. Reads the sentences collection from the provided document.
2. Delegates rating computation to self._compute_ratings and sentence selection to self._get_best_sentences, then returns the selection.

Known callers and context:
- Intended to be called by client code or higher-level summary pipelines when a summary is requested. Typical usage is in the summarization stage of a pipeline where a parsed Document object (containing sentence objects) is supplied along with the desired number of sentences.
- This method encapsulates the high-level flow (compute ratings → select best sentences) so that callers need not know internal scoring or selection details. The concrete scoring and selection behavior is implemented in the helper methods it delegates to.

Why this is a separate method:
- It provides a simple, uniform public interface (callable object) while delegating algorithmic details to smaller helper methods. This separation keeps the public API concise and makes testing/overriding of the rating and selection strategies easier.

## Args:
    document (object):
        - Required. An object that exposes a sentences attribute (accessed as document.sentences).
        - The sentences attribute is expected to be a sequence/iterable of sentence objects the summarizer can evaluate.
    sentences_count (int):
        - Required. The number of sentences to select for the summary.
        - The method does not validate the numeric range; validation or behavior for non-positive or out-of-range values is the responsibility of the delegated helper methods.

## Returns:
    The return value is exactly whatever self._get_best_sentences(document.sentences, sentences_count, ratings) returns.
    - Typically this will be an iterable (for example, a list or tuple) of sentence objects drawn from document.sentences.
    - If the helper selection method chooses to return an empty sequence (e.g., when sentences_count <= 0 or there are no sentences), that empty sequence is returned directly.
    - No additional post-processing is performed in this method.

## Raises:
    AttributeError:
        - If the provided document object does not have a sentences attribute, the attribute access (document.sentences) will raise AttributeError.
    Any exception raised by self._compute_ratings or self._get_best_sentences:
        - Exceptions raised by the delegated helper methods (for example ValueError for invalid arguments, TypeError, or custom exceptions) are not caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - None of the object's data attributes are directly read by this method (it only calls methods on self).
    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - document must provide a sentences attribute that is an iterable of sentence objects.
        - sentences_count should be an integer (the method does not enforce type; if a non-integer is passed, behavior depends on the helper methods).
    Postconditions:
        - No modifications to the summarizer instance are made.
        - The method returns the unmodified result produced by the selection helper (_get_best_sentences) based on the ratings computed by _compute_ratings.

## Side Effects:
    - This method performs no I/O and makes no external service calls itself.
    - Any side effects are entirely dependent on the implementations of self._compute_ratings and self._get_best_sentences; such side effects (if present) will be observed by callers because exceptions are propagated and return values are forwarded unchanged.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._get_all_words_in_doc` · *method*

## Summary:
Flatten all token sequences from the given sentences and return a list of their stems (tokens after normalization + stemming), preserving the document and word order.

## Description:
This helper is called during summarizer execution when the algorithm needs every token from a document (not filtered by stop words). Known direct callers:
- _get_all_content_words_in_doc (SumBasicSummarizer) — uses this method to obtain all words before filtering and normalizing content words.
Indirect callers / pipeline context:
- _compute_tf -> _compute_ratings -> __call__ — therefore this method is invoked during the term-frequency computation step of the summarization pipeline (i.e., when a Summarizer instance is producing a summary for a document).

Why this is its own method:
- It centralizes the "flatten + stem" step so multiple other helpers can reuse consistent stemming behavior (via _stem_words / stem_word) and so the code remains concise and readable. Separating this logic avoids duplicating the flattening or stemming code in multiple places and ensures consistent ordering guarantees.

## Args:
    sentences (iterable): Iterable (e.g., list, tuple, generator) of sentence-like objects.
        - Each sentence object is expected to expose an attribute `words` which itself is an iterable of tokens.
        - Token type: any object accepted by the summarizer's normalization/stemming pipeline (commonly str or bytes).

## Returns:
    list: A list of stemmed tokens produced by self._stem_words over every token from every sentence.
        - Ordering: results preserve the original ordering: for sentences in the iterable, tokens are processed in sentence order and within each sentence in token order.
        - Element type: the return element type is whatever self.stem_word returns (commonly str). If the configured stemmer returns other types, those types are returned unchanged.
        - Empty input handling: if `sentences` is empty or all sentences contain zero words, an empty list is returned.

## Raises:
    AttributeError: If any item in `sentences` does not have a `.words` attribute.
    Any exception propagated from:
        - self._stem_words, which calls self.stem_word for each token (for example, exceptions from normalize_word or the configured stemmer).
    Notes:
        - Exceptions from user-provided stemmer or normalization functions are not caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - self._stem_words (method) — invoked to perform per-token stemming
        - self.stem_word (method) — indirectly invoked by _stem_words
        - self._stemmer (attribute, read by stem_word) — used by stem_word to compute stems
    Attributes WRITTEN:
        - None. This method does not mutate instance attributes.

## Constraints:
    Preconditions:
        - Caller must provide an iterable of sentence-like objects.
        - Each sentence must expose a `words` iterable.
        - The instance must have a valid stemmer configured (inherited invariant: self._stemmer is callable); if not, stem_word will raise when invoked.
    Postconditions:
        - Returns a flat list whose length equals the total number of tokens yielded by all sentence.words iterables.
        - The returned list contains the stemmed form of every input token in document order.

## Side Effects:
    - No I/O is performed.
    - No mutation of objects outside `self` (the method does not modify sentence objects or global state).
    - The only observable effect is the CPU work of calling normalization/stemming functions; any side effects produced by user-supplied stemmer/normalizer (if they have side effects) will occur here and propagate.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._get_content_words_in_sentence` · *method*

## Summary:
Return the list of content words for a sentence after normalization, stop-word filtering, and stemming; does not modify the sentence or summarizer state.

## Description:
This method is invoked when the summarizer needs a sentence represented as a cleaned list of content tokens (used to compute sentence ratings and select best sentences). Known caller in this codebase:
- _compute_ratings — called as part of the summarization pipeline when building sentences_as_words: list(self._get_content_words_in_sentence(s) for s in sentences). This occurs during the summarization stage after the document has been parsed into Sentence objects and before sentence scoring and selection.

This logic is extracted into its own method to encapsulate the three-step transformation (normalize → filter stop words → stem) in a single reusable unit. Separating it improves clarity, avoids duplication (the same steps are performed elsewhere in the algorithm), and makes it easier to override or test each step in subclasses.

## Args:
    sentence (object): A sentence-like object that exposes an attribute `words` which is an iterable (e.g., list or tuple) of token values. Each token is passed to the normalizer and stemmer; typically tokens are strings but the method will accept any object accepted by the underlying normalize_word and stem_word implementations.

## Returns:
    list[str]: A list containing the stemmed, normalized content words (i.e., stop words removed). The list preserves the relative order of the tokens remaining after filtering. Returns an empty list when the input sentence contains no content words or when `sentence.words` is empty.

## Raises:
    AttributeError: If `sentence` does not have a `words` attribute (accessing `sentence.words`).
    TypeError or other exceptions raised by underlying helpers: If `sentence.words` is not iterable or if elements of `sentence.words` are not acceptable to the underlying normalize_word or stem_word implementations, those errors are propagated (e.g., TypeError, ValueError). This method does not catch or wrap exceptions coming from `_normalize_words`, `_filter_out_stop_words`, or `_stem_words`.

## State Changes:
    Attributes READ:
        self.stop_words (accessed indirectly via _filter_out_stop_words)
    Attributes WRITTEN:
        None — the method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - `sentence` must have a `words` attribute referencing an iterable of tokens.
        - The summarizer instance should have valid implementations of `normalize_word` and `stem_word` (inherited or provided by subclasses), and `stop_words` should be set (the class default is a frozenset()).
    Postconditions:
        - The returned value is a new list of tokens (strings) that have been normalized, filtered against the summarizer's stop words, and stemmed.
        - Neither `self` nor the `sentence` object are mutated by this call.

## Side Effects:
    - No I/O, no network calls, and no mutations of objects outside `self` (the method only returns a new list).
    - Any side effects are those produced by the underlying normalize/stem functions if they themselves have side effects; this method does not introduce additional side effects.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._stem_words` · *method*

## Summary:
Transforms an iterable of tokens into a list of token stems by applying the instance's stemming helper to each token; does not modify the summarizer's state.

## Description:
Known callers and pipeline context:
- Called by SumBasicSummarizer._get_all_words_in_doc when collecting every token from all sentences in the document before further filtering/normalization.
- Called by SumBasicSummarizer._get_content_words_in_sentence after normalization and stop-word filtering to produce stemmed content tokens for per-sentence computations.
- These calls occur during the summarization pipeline inside __call__ (through _compute_tf and _compute_ratings) when the algorithm gathers features (stems / term frequencies) used to score sentences.

Why this is a separate method:
- Centralizes the "map a token sequence to stems" operation so multiple places reuse consistent stemming logic.
- Improves readability of higher-level methods (_get_all_words_in_doc, _get_content_words_in_sentence).
- Facilitates testing and mocking of stemming behavior in isolation.
- Keeps the implementation a single simple mapping operation; separation avoids duplicated comprehension code across the class.

## Args:
    words (iterable): An iterable of token objects (commonly strings or objects acceptable to normalize_word/stem_word).
        - Required: must be an iterable (e.g., list, tuple, generator) of tokens.
        - Elements must satisfy the preconditions expected by stem_word (i.e., acceptable to normalization and the configured stemmer).
        - No default value.

## Returns:
    list: A list containing the result of applying self.stem_word to each input token, in the same order as the input iterable.
        - Element type: the return type of stem_word (commonly str), determined by the configured stemmer callable.
        - Edge cases:
            - If words is an empty iterable, returns an empty list.
            - If words is a generator, the generator will be consumed and a list of stems returned.

## Raises:
    TypeError: If the provided words argument is not iterable (raised when attempting to iterate it).
    Any exception raised by stem_word: propagated unchanged. Concretely this includes exceptions coming from normalize_word (e.g., Unicode/encoding errors) or from the configured stemmer callable (e.g., ValueError) — these are not caught here.

## State Changes:
    Attributes READ:
        - self.stem_word (method) — invoked for each token (implicitly reads self._stemmer and uses normalize_word via stem_word).
    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - The instance must be properly constructed such that stem_word is callable (the AbstractSummarizer constructor invariant: self._stemmer is callable).
        - words must be an iterable whose elements are acceptable inputs to stem_word/normalize_word.
    Postconditions:
        - The returned list has length equal to the number of items iterated from words.
        - For every index i, return[i] == self.stem_word(original_token_i).
        - The method does not modify the instance state or the input iterable items (unless the configured stemmer has side effects; see Side Effects).

## Side Effects:
    - Direct: None. This method itself performs no I/O and does not mutate instance attributes.
    - Indirect: If a custom stemmer (configured on the instance) performs side effects (logging, caching, external calls, or in-place mutation of token objects), those effects may occur because stem_word invokes that stemmer for every token. Any such external side effects are not suppressed here.

Implementation note:
- A correct reimplementation is a simple ordered mapping over the iterable, producing a concrete list, e.g.:
    - materialize and return [self.stem_word(w) for w in words]
- Preserve input order and one-to-one correspondence between inputs and outputs.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._normalize_words` · *method*

## Summary:
Converts an iterable of tokens into a list of normalized text tokens by applying the instance normalization policy to each element; does not mutate object state.

## Description:
Known callers and pipeline stage:
- _get_content_words_in_sentence: invoked when extracting content words from a sentence as part of per-sentence feature computation for scoring.
- _get_all_content_words_in_doc: invoked when collecting and normalizing all content words across the document to compute term-frequency (TF) statistics.
Lifecycle/context: Called during the token-normalization stage of the summarization pipeline, prior to stemming and frequency computations.

Rationale for being a separate method:
- Centralizes repeated logic (map each token through normalize_word) so callers need not duplicate the iteration and mapping.
- Improves readability and makes it straightforward for subclasses to override batch normalization behavior without changing many call sites.

## Args:
    words (iterable): An iterable of token-like objects (e.g., str, bytes, or other objects acceptable to normalize_word). Each element will be passed to self.normalize_word in order.

## Returns:
    list[str]: A list of normalized text tokens (Python str) produced by calling self.normalize_word on each input token.
    - The returned list preserves the iteration order and length of the input iterable.
    - If the input is empty, an empty list is returned.

## Raises:
    - TypeError: If the provided words argument is not iterable (raised when attempting to iterate).
    - Any exception raised by self.normalize_word for any element. Examples include (but are not limited to) UnicodeDecodeError, TypeError, or AttributeError originating from the underlying to_unicode conversion or .lower() call in normalize_word.
    - Exceptions are not caught here; they propagate to the caller.

## State Changes:
    Attributes READ:
    - None (the method does not read or depend on instance attributes; it only invokes self.normalize_word which itself is a pure helper).

    Attributes WRITTEN:
    - None (this method does not modify any self.<attr> attributes).

## Constraints:
    Preconditions:
    - The caller must provide an iterable of tokens.
    - Each token must be acceptable to the project's normalize_word implementation (i.e., convertible to text by to_unicode and lowerable).

    Postconditions:
    - Returns a list of normalized strings corresponding one-to-one with the input tokens.
    - The method does not modify the original iterable or the instance state.

## Side Effects:
    - None. No I/O, no external service calls, and no mutation of objects outside of returning the new list. The only observable effect is the creation and return of the list of normalized tokens.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._filter_out_stop_words` · *method*

## Summary:
Return a new list containing only those tokens from the input iterable that are not present in the summarizer's configured stop-word set; does not modify instance state.

## Description:
Known callers and context:
- _get_content_words_in_sentence(sentence): called while extracting content words for a single sentence during rating computation. That caller first normalizes tokens and then calls this method.
- _get_all_content_words_in_doc(sentences): called while collecting all document words for TF computation; this caller passes previously stemmed tokens into this method.
- Indirect callers: _compute_tf and _compute_ratings use the above helpers, so this method is invoked as part of the summarizer's term-frequency computation and per-sentence scoring pipeline.

Why this is a dedicated method:
- Centralizes the stop-word membership check so subclasses or tests can override or mock stop-word filtering behavior by setting stop_words or overriding this method.
- Keeps token filtering logic separate from normalization/stemming helpers to improve readability and reuse across places that need stop-word removal.

## Args:
    words (iterable): Iterable of tokens (commonly strings) to be filtered. Tokens may be raw, normalized, or stemmed depending on the caller. Elements must be hashable (required for membership checks).

## Returns:
    list: A list containing elements from the input iterable, in the same order, excluding any element that is a member of self.stop_words.
    - If the input iterable is empty, returns an empty list.
    - Duplicates in the input are preserved if they are not stop words.

## Raises:
    TypeError: If any token in words is unhashable (membership check against self.stop_words requires hashable elements), or if words is not an iterable.
    Any exception raised by accessing self.stop_words (e.g., if a custom stop_words property raises) will propagate.

## State Changes:
    Attributes READ:
        - self.stop_words (property that returns the current stop-word container, by default a frozenset)
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - self.stop_words must be an iterable container supporting membership testing (the class provides a frozenset by default).
        - words must be an iterable; its elements should be comparable with elements of self.stop_words for meaningful filtering.
        - For predictable removal of stop words, callers should pass tokens in the same canonical form used to populate stop_words. In this class, stop_words are populated by normalize_word; therefore passing normalized tokens is recommended. Note: some internal callers pass normalized tokens, while others pass stemmed tokens — results depend on whether the token form matches entries in self.stop_words.
    Postconditions:
        - The returned list contains only tokens that are not present in self.stop_words.
        - No attributes on self are modified.
        - The input iterable is not mutated by this method (a new list is returned).

## Side Effects:
    - None: no I/O, no network access, and no mutation of objects outside the method (returns a new list and only reads self.stop_words).

### `sumy.summarizers.sum_basic.SumBasicSummarizer._compute_word_freq` · *method*

## Summary:
Count occurrences of each distinct item in the provided iterable and return a new dictionary mapping each item to its positive integer frequency; the function does not modify object state.

## Description:
A small utility that iterates over the provided iterable and tallies how many times each distinct item appears, returning the frequency mapping. Typical callers are components that need simple token/word frequency counts (for example, summarizer steps such as sentence scoring, weighting, or feature extraction). This logic is factored into a separate function to keep counting behavior isolated, making the intent explicit and allowing reuse wherever a frequency map is required.

## Args:
    list_of_words (iterable[Hashable]): An iterable (commonly a list) of hashable items (typically strings representing words or tokens). Any iterable type is accepted; elements must be hashable so they can be used as dictionary keys.

## Returns:
    dict: A dictionary where each key is a distinct item seen in list_of_words and each value is an int >= 1 giving the number of times that item appeared. If list_of_words yields no items, an empty dict is returned.

## Raises:
    TypeError:
        - If list_of_words is not iterable, iteration will raise a TypeError.
        - If any element in list_of_words is unhashable (e.g., a list or dict), attempting to use it as a dictionary key will raise a TypeError.
    Note: The function does not catch these exceptions; they propagate to the caller.

## State Changes:
    Attributes READ: None (the function does not access any self.<attr> attributes)
    Attributes WRITTEN: None (the function does not modify self or external objects)

## Constraints:
    Preconditions:
        - list_of_words must be an iterable.
        - Elements yielded by list_of_words must be hashable.

    Postconditions:
        - The returned dictionary contains one entry per distinct hashable item seen in list_of_words.
        - The sum of all integer values in the returned dictionary equals the number of items successfully iterated from list_of_words.
        - The input iterable and its elements are not modified by this function.

## Side Effects:
    - None. The function performs no I/O, network calls, or mutations of objects outside its local scope; it constructs and returns a new dictionary.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._get_all_content_words_in_doc` · *method*

## Summary:
Compute and return the document's content words by extracting all words from the provided sentences, removing stop words, and normalizing the remaining words.

## Description:
This internal helper runs three transformation steps in sequence:
1. Extract all words from the provided sentences by delegating to self._get_all_words_in_doc.
2. Remove stop words from that word list by delegating to self._filter_out_stop_words.
3. Normalize the remaining content words by delegating to self._normalize_words.

Known callers:
- Not discovered in the provided source context. This is an internal utility method intended to be used by the summarizer pipeline prior to building word frequencies or scoring sentences.

Why this is a separate method:
- Encapsulates a common three-step pipeline (extract → filter stop words → normalize) so other parts of the summarizer can obtain ready-to-use content words without duplicating these calls. It improves readability, reuse, and testability by composing smaller helper methods.

## Args:
    sentences (iterable): An iterable of sentence-like items (strings or sentence objects) acceptable to self._get_all_words_in_doc.
        - No default; must be provided.
        - Preconditions on element types/structure are delegated to self._get_all_words_in_doc.

## Returns:
    list or sequence: The direct return value of self._normalize_words called on the content words.
    - Typically a sequence of normalized word tokens (e.g., list[str]), but the exact container type and element type depend on the implementations of the three delegated helper methods.
    - If there are no content words (e.g., empty input or all words filtered as stop words), returns whatever self._normalize_words returns for an empty input (commonly an empty list).

## Raises:
    Propagates any exception raised by:
    - self._get_all_words_in_doc(sentences)
    - self._filter_out_stop_words(all_words)
    - self._normalize_words(content_words)
    No exceptions are raised directly by this method's body.

## State Changes:
Attributes READ:
    - None directly accessed. The method calls three instance methods which may read instance attributes; any attributes they read are not observable here.

Attributes WRITTEN:
    - None. This method does not assign to any self.<attr> fields.

## Constraints:
Preconditions:
    - sentences must be a valid input for self._get_all_words_in_doc. This method performs no validation beyond forwarding the argument to the helper methods.

Postconditions:
    - Returns the normalized content words produced by the helper pipeline (extract → filter → normalize).
    - Does not modify self or the sentences argument at the caller-visible attribute level (it only composes the results returned by helper methods).

## Side Effects:
    - No I/O or external service calls are made directly by this method.
    - Any side effects depend entirely on the implementations of the delegated methods; this method itself is a pure functional composition of their results.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._compute_tf` · *method*

## Summary:
Computes the term-frequency (TF) distribution for all content words in the provided sentences and returns a mapping from each normalized/stemmed content word to its relative frequency in the document.

## Description:
This method is called during summarization to produce the base word-probabilities used by the SumBasic ranking algorithm. Known callers:
- _compute_ratings(self, sentences): invokes this method at the start of rating computation to obtain document-level TFs.
- __call__(self, document, sentences_count): indirectly, via _compute_ratings, as part of the summarizer pipeline when generating a summary.

This logic is split into its own method to isolate and encapsulate TF computation (normalization, stop-word filtering, stemming and frequency normalization). Separating it makes the summarizer easier to test, reason about, and reuse in other steps (e.g., other ranking or weighting functions).

## Args:
    sentences (iterable): Iterable of sentence-like objects. Each sentence object must provide a .words attribute (an iterable of token strings). The method does not accept None. Typical input is the document.sentences collection passed from the summarizer entry point.

## Returns:
    dict: A mapping {word: tf} where:
        - word (str): a normalized and stemmed content word (strings produced by self.normalize_word and self.stem_word).
        - tf (float): the term frequency computed as (count of word occurrences among all content words) / (total count of content words).
    Notes:
        - All tf values are in the range (0, 1] for words present; collectively they sum to 1.0 when there is at least one content word.
        - If no content words are present (empty input or all tokens are filtered out as stop words), an empty dict is returned.

## Raises:
    TypeError: If `sentences` is not iterable or sentence items do not expose a .words attribute (this arises from underlying iterations; not explicitly raised in code).
    (No explicit exceptions are raised by the method itself; division by the total count is safe because frequencies are computed from the same content word list — if that list is empty the resulting dict comprehension is empty and no division occurs.)

## State Changes:
    Attributes READ:
        - self.stop_words (property) / self._stop_words: consulted indirectly through _get_all_content_words_in_doc and _filter_out_stop_words to exclude stop words.
        - self.normalize_word (method): used indirectly to normalize tokens.
        - self.stem_word (method): used indirectly to stem tokens.
    Attributes WRITTEN:
        - None. This method does not modify any self.* attributes.

## Constraints:
    Preconditions:
        - Each element in `sentences` must be a sentence-like object with a .words iterable of token strings.
        - The class must provide normalize_word and stem_word methods and a stop_words set (or property) — normally inherited from AbstractSummarizer.
    Postconditions:
        - The returned dict maps normalized/stemmed content words to float frequencies that sum to 1.0 if at least one content word exists.
        - No mutation of the summarizer object occurs.

## Side Effects:
    - No I/O, network calls, or interactions with external services.
    - No modifications to objects outside of local variables (the only mutations are to temporaries such as the frequency dict built and returned).
    - Indirectly reads summarizer configuration (stop words, normalizer/stemmer) via helper methods called.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._compute_average_probability_of_words` · *method*

## Summary:
Compute and return the arithmetic mean of the numeric frequencies/probabilities for the given sentence's content words; returns 0 when the sentence contains no content words. This function does not modify object state.

## Description:
This utility calculates the average value of entries looked up in the provided word-to-number mapping for each word in a sentence (content_words_in_sentence). It is intended for use during sentence scoring within the SumBasic summarization algorithm (i.e., as part of ranking / scoring sentences based on word probabilities). Having this logic factored into a separate function keeps the sentence-scoring code cleaner, makes the averaging behavior easy to test, and isolates the handling of the empty-sentence case.

Known/expected callers and context:
- Sentence-ranking or scoring routines inside the SumBasicSummarizer class (invoked as part of the summarization pipeline when computing a sentence score from per-word probabilities). The implementation shown does not reference self, so callers may invoke it as a helper/utility within the summarizer implementation.

Why this is a separate method:
- Encapsulates a single, well-defined operation (mean of mapped word values with an empty-sentence fallback).
- Improves readability, testability, and reuse within the summarizer's sentence-scoring workflow.

## Args:
    word_freq_in_doc (mapping[str->number]): A mapping (e.g., dict) providing a numeric value (frequency or probability) for each word key. Values should be numeric (int, float). The mapping must support item access by the words in content_words_in_sentence.
    content_words_in_sentence (iterable[str]): An iterable (e.g., list or tuple) of word keys whose mapped numeric values should be averaged. May be empty.

## Returns:
    float or int: The arithmetic mean of word_freq_in_doc[w] for every w in content_words_in_sentence.
    - If content_words_in_sentence is non-empty: returns the average as a numeric value (in Python 3 this will be a float if division yields a non-integer).
    - If content_words_in_sentence is empty: returns 0 (integer).

## Raises:
    KeyError: If any word w in content_words_in_sentence is not present as a key in word_freq_in_doc (caused by the expression word_freq_in_doc[w]).
    TypeError: If content_words_in_sentence is not iterable, or if the values retrieved from word_freq_in_doc are not numeric and cannot participate in numeric addition/division.
    (No explicit catches are performed in this function; exceptions from invalid input propagate to the caller.)

## State Changes:
    Attributes READ: None (this function is pure with respect to object state; it does not access self or read any object attributes).
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - word_freq_in_doc must be a mapping-like object that supports indexing with keys from content_words_in_sentence.
    - Values in word_freq_in_doc for the provided keys must be numeric (support addition and division).
    - content_words_in_sentence must be an iterable of keys compatible with the mapping.

    Postconditions:
    - The input mapping and iterable are not modified.
    - The return value is either the numeric mean of the mapped values (when content_words_in_sentence is non-empty) or 0 (when it is empty).

## Side Effects:
    - None. This function performs no I/O, does not call external services, and does not mutate objects outside its local scope.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._update_tf` · *method*

## Summary:
Squares the term-frequency values for a set of keys in-place, updating the provided mapping so that each selected entry becomes its original value multiplied by itself.

## Description:
This helper performs an in-place update of the provided word frequency mapping by squaring the numeric value for each key listed in words_to_update. It is a focused utility extracted from summarization logic to isolate the numeric transformation (value := value * value) from higher-level flow control.

Known callers:
    - No direct callers were identified in the provided source snippet. In the original SumBasic summarization algorithm context, this function is typically invoked during the term-frequency updating step of a summarizer implementation when selected words' frequencies need to be re-weighted.

Why this is a separate method:
    - Encapsulates the precise numeric update rule (squaring) so higher-level summarizer code can remain focused on sentence/word selection and pipeline orchestration.
    - Makes the transformation easy to test in isolation and replace or modify without touching larger summarization logic.

## Args:
    word_freq (MutableMapping[Hashable, number]):
        A mutable mapping (commonly a dict) mapping word keys to numeric term-frequency values (integers or floats).
        Preconditions: must support item access and assignment (word_freq[key]) and have numeric values for keys that will be updated.
    words_to_update (Iterable[Hashable]):
        An iterable of keys that should be updated in word_freq. Each element is looked up in word_freq and used as the key to update the corresponding value.

## Returns:
    MutableMapping[Hashable, number]:
        Returns the very same mapping object passed in as word_freq (the mapping is mutated in-place).
        If words_to_update is empty, the original mapping is returned unchanged.

## Raises:
    KeyError:
        If any key in words_to_update is not present in word_freq, a KeyError will be raised at the first such missing key.
    TypeError:
        If a value for a key is not a numeric type that supports multiplication with itself, a TypeError (or other arithmetic-related exception) may be raised during the multiplication operation.

## State Changes:
    Attributes READ:
        - None of the form self.<attr> — this is a standalone function and does not access object attributes.
        - Reads entries from the provided word_freq mapping (word_freq[key]) for each key in words_to_update.
    Attributes WRITTEN:
        - None of the form self.<attr>.
        - Writes/mutates entries within the provided word_freq mapping: for each key w in words_to_update, word_freq[w] is replaced with word_freq[w] * word_freq[w].

## Constraints:
    Preconditions:
        - word_freq must be a mutable mapping with the keys referenced in words_to_update.
        - Values at those keys must be numeric (int/float) or otherwise support multiplication with themselves.
        - words_to_update must be an iterable of keys (hashable types matching keys of word_freq).
    Postconditions:
        - For every key k in words_to_update that existed in word_freq before the call, word_freq[k] == old_value * old_value.
        - Keys in word_freq not listed in words_to_update remain unchanged.
        - The returned object is the same mapping instance as the word_freq argument.

## Side Effects:
    - Mutates the provided word_freq mapping in-place.
    - No I/O, no network calls, and no external state is modified outside the passed-in mapping.

### `sumy.summarizers.sum_basic.SumBasicSummarizer._find_index_of_best_sentence` · *method*

## Summary:
Return the 0-based index of the sentence whose content words have the highest average value according to the provided word_freq mapping. The method does not modify object state.

## Description:
Scans the supplied list of sentences (each represented as an iterable of content words) and computes each sentence's average mapped value by delegating to the summarizer's average-computation helper. It selects and returns the index of the sentence with the maximum average.

Known callers and context:
- SumBasicSummarizer._compute_ratings: Called repeatedly while building the summary. At each iteration the summarizer determines which remaining sentence should be chosen next by passing the current per-word frequencies (word_freq) and the remaining sentences expressed as lists of content words (sentences_as_words) to this method. The caller then pops that index from parallel lists.
- Pipeline stage: sentence-scoring / selection phase of the SumBasic summarizer.

Why this is a separate method:
- Encapsulates scanning and comparison logic, keeping the selection loop concise.
- Makes tie-breaking and sentinel initialization explicit and testable.

## Args:
    word_freq (mapping[str, number]):
        Mapping from normalized/stemmed word to a numeric value (frequency or probability).
        - Must support indexing with words found in sentences_as_words.
        - Numeric values must support addition and division.
    sentences_as_words (iterable[iterable[str]]):
        Ordered iterable (e.g., list) where each element is an iterable of content words (strings) for a sentence.
        - Elements may be empty iterables (sentence with no content words).
        - The returned index is relative to this iterable (0-based).

## Returns:
    int:
        The 0-based index of the sentence with the highest average mapped value.
        - Tie-breaking: the first sentence encountered with the strictly highest average is returned (comparison uses >).
        - If sentences_as_words is empty, returns 0 (the caller must ensure non-empty lists before using this index for popping/access).
        - If no sentence produces a value greater than the initial sentinel (-1), the method returns 0 (the initial best_sentence_index).

## Raises:
    KeyError:
        Propagated if any word in any sentence is not present as a key in word_freq. This originates from the delegated average computation which looks up word_freq[w].
    TypeError:
        Propagated if sentences_as_words or its items are not iterable, or if values in word_freq are not numeric and arithmetic operations fail.
    Notes:
        The method itself does not perform explicit validation; exceptions from invalid inputs propagate to the caller.

## State Changes:
    Attributes READ:
        - None (the method does not read instance attributes).
        - It calls the instance helper _compute_average_probability_of_words via self, but that helper is stateless in practice and does not access instance attributes.
    Attributes WRITTEN:
        - None (no modifications to self or to the provided arguments are performed).

## Constraints:
    Preconditions:
        - word_freq must be indexable by every word appearing in sentences_as_words, unless the caller intends to handle KeyError.
        - Values in word_freq for those keys must be numeric.
        - If the caller plans to use the returned index to pop from parallel sequences, sentences_as_words must be non-empty and aligned (same ordering) with those sequences.
    Postconditions:
        - The method returns an integer index as described under Returns.
        - No mutation of input arguments or object state occurs.

## Edge cases and sentinel behavior:
    - The method initializes its comparison sentinel to -1 (min_possible_freq = -1). This makes the method return the first sentence with an average strictly greater than -1.
    - If all computed averages are <= -1 (possible only when word_freq contains values <= -1), no average will be greater than the sentinel and the method will return 0 (the initial best index), so callers should be aware of this behavior.
    - For sentences without content words the average helper returns 0; such sentences therefore compare as 0 against other averages.

## Side Effects:
    - None. No I/O or external calls. No mutation of objects outside the local scope.

## Example usage:
    # Given a summarizer instance, a word frequency mapping and a list of content-word lists:
    best_index = summarizer._find_index_of_best_sentence(word_freq, sentences_as_words)

### `sumy.summarizers.sum_basic.SumBasicSummarizer._compute_ratings` · *method*

## Summary:
Computes and returns an ordering (ratings) for the given sentences by repeatedly selecting the best sentence according to word-frequency based heuristics and updating word frequencies after each selection. The method does not mutate self attributes; it returns a mapping from each input sentence to an integer score encoding selection order (earlier-selected sentences have higher scores).

## Description:
This method is part of the extractive summarization pipeline. It is invoked during the summarizer's sentence-scoring stage to convert a collection of candidate sentences into a ranking used to choose summary sentences.

Known callers and lifecycle context:
- Called by higher-level summarizer logic (e.g., the public summarize() pipeline) when the summarizer needs sentence rankings. It represents the stage after computing initial term frequencies and before selecting the final ordered summary sentences.
- It is separated from the caller to encapsulate the iterative selection-and-update pattern of the SumBasic algorithm and to allow overriding or testing the ranking behavior independently.

Why this is its own method:
- The procedure contains a non-trivial loop (select best sentence, assign rating, update frequencies) that is clearer and reusable as a single, testable unit.
- It relies on several helper methods (_compute_tf, _get_content_words_in_sentence, _find_index_of_best_sentence, _update_tf). Keeping the orchestration here avoids duplicating the selection/update pattern elsewhere and preserves a single place to manage ordering semantics.

## Args:
    sentences (Iterable[Sentence-like]):
        An iterable (e.g., list, tuple, generator) of sentence objects accepted by the summarizer.
        Requirements on elements:
        - Each element must be acceptable to self._get_content_words_in_sentence(sentence) which returns the token/content words for that sentence.
        - Each element must be hashable (usable as a dict key) and distinguishable if distinct entries are required; if two elements compare equal (==) and have the same hash, they may overwrite each other in the returned mapping.
        If sentences is empty, the method returns an empty dict.

## Returns:
    dict:
        A mapping {sentence: score} where:
        - sentence is the same object taken from the input iterable (the method preserves the original sentence objects as keys).
        - score is an int representing selection order: the first selected sentence receives 0, the next -1, then -2, and so on (i.e., decreasing integers starting at 0).
        - The sign and numeric progression are chosen so that larger numbers correspond to earlier selections (0 > -1 > -2 ...). This ordering can be used to sort sentences descending to get the selection order.
        - If the input is empty, returns an empty dict.

## Raises:
    TypeError:
        If `sentences` is not iterable.
    IndexError:
        If a helper method returns an invalid index (e.g., _find_index_of_best_sentence returns an index outside the current sentences list length). Such errors propagate from the helper methods.
    Any exception raised by helper methods:
        The method delegates core computations to helper methods; any exceptions these helpers raise (e.g., when sentence objects are malformed, or when word-frequency structures are ill-formed) are propagated.

## State Changes:
    Attributes READ:
        - No direct self.<attr> fields are read by this method. Instead, it calls the following instance methods which may themselves read instance state:
            - self._compute_tf
            - self._get_content_words_in_sentence
            - self._find_index_of_best_sentence
            - self._update_tf
    Attributes WRITTEN:
        - This method does not assign to any self.<attr> attributes.
        - Local variables mutated: word_freq (local mapping, likely mutated in place by _update_tf), sentences_list, sentences_as_words, ratings.

## Constraints:
    Preconditions:
        - The class must implement the following helper methods with the described contracts (the correctness of _compute_ratings depends on them):
            - _compute_tf(sentences) -> MutableMapping[str, float|int]:
                Returns an initial word-frequency mapping computed from the provided sentences. The mapping must be mutable because _update_tf(word_freq, ...) is expected to modify it in place.
            - _get_content_words_in_sentence(sentence) -> List[str] or Iterable[str]:
                Returns the sequence of content words (tokens) for the given sentence. The returned list corresponds positionally to the sentence in the sentences iterable used to build sentences_as_words.
            - _find_index_of_best_sentence(word_freq, sentences_as_words) -> int:
                Given the current word frequency mapping and a list (aligned with sentences_list) of per-sentence word lists, returns the integer index of the sentence considered best under the scoring heuristic. The returned index must be valid for the current sentences_list/sentences_as_words (0 <= index < len(sentences_list)).
            - _update_tf(word_freq, best_sentence_words) -> None:
                Mutates word_freq in place to reduce (or otherwise adjust) frequencies based on the words present in the selected sentence so that subsequent selections reflect decreased importance of already-covered words.
        - Sentences should be provided in a stable order if deterministic selection is required.
        - Sentence objects should be hashable and, if uniqueness in the ratings mapping is required, distinct objects or distinct hashes/eq results must be used.

    Postconditions:
        - The returned dict contains exactly one key for each object that was present and popped from the input iterable (unless duplicate-equal keys overwrite prior entries because of hashing/equality).
        - The set of keys in the returned dict is (conceptually) the set of input sentence objects; values are unique integers in the sequence [0, -1, -2, ...] in the order sentences were selected.
        - The local word_freq mapping will have been modified by repeated calls to _update_tf. Changes are local to the mapping returned by _compute_tf; no class attributes are changed by this method itself.

## Side Effects:
    - No I/O or external service calls are performed.
    - Mutates the local word frequency mapping returned by _compute_tf via calls to _update_tf (in-place mutation of that local object).
    - Uses and may consume iterator input if `sentences` is a generator: the method converts sentences to a list early (list(sentences)), so calling code should be aware that generators will be exhausted.
    - Potential overwrite of entries in the returned dict if two different sentence objects are equal (same __hash__ and __eq__); this is a semantic side effect observable by callers.

## Example (conceptual):
    - Given three sentence objects s1, s2, s3:
        ratings = _compute_ratings([s1, s2, s3])
      Possible returned mapping:
        {s2: 0, s1: -1, s3: -2}
      Meaning s2 was selected first, then s1, then s3.

## Implementation notes for reimplementation:
    - Preserve the exact selection loop: build mutable word_freq, build parallel lists sentences_list and sentences_as_words, then loop while sentences_list not empty:
        1. best_index = self._find_index_of_best_sentence(word_freq, sentences_as_words)
        2. best_sentence = sentences_list.pop(best_index)
        3. ratings[best_sentence] = -len(ratings)
        4. best_sentence_words = sentences_as_words.pop(best_index)
        5. self._update_tf(word_freq, best_sentence_words)
    - Ensure that _find_index_of_best_sentence's returned index is used to pop both the sentence and its corresponding word-list so alignment is preserved.
    - Use list(sentences) at the start to avoid re-consuming generator inputs and to allow index-based popping.

