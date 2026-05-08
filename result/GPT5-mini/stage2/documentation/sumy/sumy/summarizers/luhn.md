# `luhn.py`

## `sumy.summarizers.luhn.LuhnSummarizer` · *class*

## Summary:
LuhnSummarizer is a concrete summarizer implementing Luhn's heuristic: it selects sentence scores based on clusters of frequent (significant) word stems and returns the top N sentences from a parsed document.

## Description:
When instantiated (optionally with a custom stemmer inherited from AbstractSummarizer), LuhnSummarizer implements the Luhn algorithm pipeline:
- Determine "significant" stems from the document token stream using normalization, stemming, stop-word filtering and a term-frequency model (TfDocumentModel).
- Score each sentence by detecting contiguous chunks of tokens around significant stems and applying Luhn's numeric scoring rule to each chunk.
- Choose the best sentences by delegating ranking/selection to AbstractSummarizer._get_best_sentences, passing rate_sentence as the scoring function.

Typical callers:
- Summarization pipelines and user code that create a LuhnSummarizer instance and call it with (document, sentences_count).
- Any factory selecting a summarizer algorithm that expects a callable summarizer.

Responsibility boundary:
- This class defines Luhn-specific term selection and sentence-scoring logic.
- It relies on AbstractSummarizer for normalization/stemming helpers and for the generic sentence selection (_get_best_sentences).
- It relies on TfDocumentModel for term-frequency based selection of candidate significant stems.

## State:
Attributes (with default values when not overridden):
- max_gap_size (int) — default: 4
  - Meaning: number of consecutive non-significant tokens that terminates a chunk. Must be >= 1 for correct behavior.
  - Invariant: interpreted as a positive integer during chunk extraction.
- significant_percentage (number: int or float) — default: 1
  - Meaning: fraction/multiplier applied to the total number of (filtered & stemmed) tokens to compute how many top terms to request from TfDocumentModel: best_words_count = int(len(tokens) * significant_percentage).
  - Typical valid range: >= 0. Common use is in [0.0, 1.0], but >1.0 is tolerated (TfDocumentModel returns at most available terms). Negative values will likely cause TfDocumentModel to raise ValueError.
- _stop_words (frozenset) — default: frozenset()
  - Stored value: immutable frozenset of normalized tokens (normalize_word applied). Used to filter tokens before stemming.
  - Invariant: always a frozenset; elements must be hashable (normalized strings).

Inherited state (from AbstractSummarizer):
- _stemmer (callable)
  - Provided at construction time (via base class __init__). Default is project null_stemmer. Must be callable; otherwise AbstractSummarizer.__init__ raises ValueError.

Notes on methods that read or write state:
- stop_words property setter replaces self._stop_words with a normalized frozenset.
- Other methods read max_gap_size, significant_percentage, _stop_words and the inherited stem/normalize helpers but do not mutate instance state.

## Lifecycle:
Creation:
- Instantiate by calling the constructor of the subclass (LuhnSummarizer). No explicit __init__ is defined in this class, so the constructor is AbstractSummarizer.__init__(stemmer=null_stemmer).
- Optional parameter: stemmer (callable) — if provided to the constructor, it must be callable or AbstractSummarizer.__init__ will raise ValueError.

Configuration (recommended before use):
- Optionally set stop_words via the property: summarizer.stop_words = iterable_of_words
  - Each token will be normalized with normalize_word and stored as a frozenset.

Usage:
1. Ensure document is parsed and tokenized into:
   - document.words: iterable of token strings (used to compute significant stems)
   - document.sentences: iterable of sentence objects where each sentence exposes .words (iterable of tokens)
2. Invoke the instance: summarizer(document, sentences_count)
   - sentences_count can be an int, a percent string like "30%", or a callable selection policy accepted by AbstractSummarizer._get_best_sentences.
3. Internally, the invocation runs:
   - _get_significant_words(document.words)
   - _get_best_sentences(document.sentences, sentences_count, self.rate_sentence, significant_stems)
   - rate_sentence will call _get_chunk_ratings -> _get_chunk_rating and __remove_trailing_zeros as needed.

Destruction:
- No explicit cleanup required. The class provides no context manager or close method. Standard garbage collection applies.

Sequencing constraints:
- stop_words should be set (if needed) before calling the instance to affect term selection.
- Do not mutate summarizer attributes that are read during scoring (max_gap_size, significant_percentage) during an active scoring operation.

## Method Map:
graph TD
    A[call: summarizer(document, sentences_count)] --> B[_get_significant_words(document.words)]
    B --> C[TfDocumentModel(words_tuple)]
    C --> D[most_frequent_terms(best_words_count)]
    D --> E[filter terms by model.term_frequency > 1]
    A --> F[_get_best_sentences(document.sentences, sentences_count, rate_sentence, significant_stems)]
    F --> G[for each sentence: rate_sentence(sentence, significant_stems)]
    G --> H[_get_chunk_ratings(sentence, significant_stems)]
    H --> I[_get_chunk_rating(chunk)]
    I --> J[__remove_trailing_zeros(chunk)]
    I --> K[return numeric rating]
    H --> L[return tuple of chunk ratings]
    G --> M[return max(chunk ratings) or 0]
    F --> N[select top sentences and return them in document order]

Notes:
- _get_best_sentences is provided by AbstractSummarizer; it expects rate_sentence to accept (sentence, significant_stems).
- TfDocumentModel is used only inside _get_significant_words.

## Raises:
Constructor:
- ValueError if a non-callable stemmer is supplied to AbstractSummarizer.__init__ (inherited behavior).

stop_words setter:
- TypeError if provided words is not iterable or if normalize_word returns unhashable values (frozenset creation will raise).
- Any exception raised by normalize_word will propagate.

__call__(document, sentences_count):
- Propagates exceptions from:
  - _get_significant_words (normalize_word, stem_word, TfDocumentModel.__init__, TfDocumentModel.most_frequent_terms).
  - AbstractSummarizer._get_best_sentences (Errors from rating callable, selection policy, or mapping misuse).
- Does not perform extra validation; callers should supply documents with .words and .sentences.

_get_significant_words(words):
- Propagates exceptions from normalize_word and stem_word.
- TfDocumentModel.most_frequent_terms may raise ValueError for a negative requested count (occurs if significant_percentage < 0).

_rate_sentence and helpers:
- _get_chunk_rating asserts that the trimmed chunk length > 0; if this assertion fails it raises AssertionError (shouldn't occur for normal inputs because chunks are built starting with a significant marker).
- TypeError may arise if chunk elements are not summable (sum(chunk)).

_get_chunk_ratings:
- TypeError or AttributeError if sentence has no .words or if .words is not iterable.
- Propagates exceptions from stem_word and from _get_chunk_rating.

__remove_trailing_zeros:
- If the provided collection does not support len(), indexing, or slicing, Python will raise the respective TypeError/IndexError when operations are attempted.

## Example (how to use and expected shapes; pseudo-steps, not executable code):
1. Construct summarizer:
   - Provide a custom stemmer callable if desired, otherwise use the default: instantiate the summarizer (inherited constructor enforces stemmer is callable).
2. Optionally configure stop words:
   - Assign an iterable of tokens to summarizer.stop_words; each token will be normalized.
3. Prepare a document object with the minimal required attributes:
   - document.words: iterable of token strings (the global token stream for term selection).
   - document.sentences: iterable of sentence objects; each sentence must expose .words as an iterable of tokens.
4. Call the summarizer:
   - Call summarizer(document, sentences_count) where sentences_count is an int, a percent-string (e.g., "30%") or a callable selection policy accepted by AbstractSummarizer._get_best_sentences.
5. Result:
   - A tuple of selected sentence objects from document.sentences is returned, ordered by original document order.
6. No cleanup is required.

Implementation notes for reimplementation:
- Use normalize_word on input tokens before comparing against _stop_words.
- Use stem_word for canonical stems stored/compared with TfDocumentModel and significant_stems.
- Compute best_words_count as int(len(filtered_stems) * significant_percentage). If this equals 0, TfDocumentModel.most_frequent_terms(0) behavior returns all terms; final filter keeps only terms with model.term_frequency(term) > 1.
- In chunk detection, start a chunk only when encountering a significant stem; append 1 for significant tokens and 0 for non-significant tokens inside an open chunk. Close a chunk (set in_chunk False) when the last max_gap_size entries of the current chunk are all zeros.
- Before scoring a chunk, remove trailing zeros; if the chunk is reduced to length 0, the chunk-rating code asserts and will raise AssertionError (this situation should not occur if chunks are created as described, but document the assertion).

### `sumy.summarizers.luhn.LuhnSummarizer.stop_words` · *method*

## Summary:
Sets the summarizer's stop-word set by normalizing each provided token and storing the result as an immutable frozenset on the instance, replacing any previous stop-words.

## Description:
Known callers and context:
- Typical callers are client or pipeline configuration code that prepares a LuhnSummarizer before generating summaries (for example, after constructing the summarizer: summarizer.stop_words = my_iterable_of_tokens).
- Internally, the LuhnSummarizer later reads the stored set via self._stop_words (for example in _get_significant_words) during the summarization pipeline to filter out tokens considered stop-words.
- Lifecycle stage: configuration step prior to invoking the summarizer's __call__ method.

Why this logic is a separate setter:
- Centralizes normalization and freezing of stop-words so callers can pass arbitrary token iterables and rely on consistent canonicalization (via normalize_word) and immutability (frozenset).
- Keeps downstream code simple: other methods can rely on a ready-to-use, normalized, and hashable stop-word collection (self._stop_words) instead of repeating normalization and deduplication logic everywhere.

## Args:
    words (iterable): An iterable of tokens (any values acceptable to AbstractSummarizer.normalize_word, typically str/bytes). Each item will be passed to self.normalize_word before being added to the stop-word set.

## Returns:
    None: This is a setter; it does not return a value.

## Raises:
    TypeError: If the provided words argument is not iterable (raised when attempting to iterate or by map).
    Any exception raised by self.normalize_word for any token (for example conversion/encoding errors from to_unicode or related failures) will propagate unchanged.
    TypeError: If normalize_word returns an unhashable value for any token, frozenset(...) will raise TypeError.
    (Note: exceptions propagate; this method does not catch or wrap errors.)

## State Changes:
    Attributes READ:
        - None (no self.<attr> instance fields are read; the method calls self.normalize_word but does not read stored attributes)
    Attributes WRITTEN:
        - self._stop_words : set to a frozenset of normalized tokens (replacing any prior value)

## Constraints:
    Preconditions:
        - The instance must provide normalize_word (inherited from AbstractSummarizer); normalize_word must accept each token in words.
        - The normalized token values returned by normalize_word should be hashable (commonly strings) so frozenset construction succeeds.
    Postconditions:
        - self._stop_words is guaranteed to be a frozenset object (possibly empty) containing the normalized form of each token from the provided iterable, with duplicates removed.
        - The stored set is immutable (frozenset) and ready for membership testing (e.g., "if normalized in self._stop_words").

## Side Effects:
    - Mutates the instance by replacing/setting self._stop_words.
    - No I/O, external network calls, or global state changes are performed by this method itself.
    - Any side effects from normalize_word (if the override does something unusual) will also occur; this method does not introduce additional side effects beyond calling normalize_word and assigning self._stop_words.

### `sumy.summarizers.luhn.LuhnSummarizer.__call__` · *method*

## Summary:
Invokes the Luhn-specific sentence-scoring pipeline to produce the top N sentences from the given parsed document and returns them in the original document order.

## Description:
This method is the public entry point used by callers that request a Luhn summarization of a parsed document. Typical callers:
- Summarization pipelines and user code that construct a LuhnSummarizer instance and call it with (document, sentences_count) to obtain a summary.
- Any factory or orchestration code that selects a summarizer implementation and invokes it as a callable during the "summarize" stage.

Lifecycle stage:
- Called after a document has been parsed into sentence objects and tokenized into words (i.e., when document.words and document.sentences are available).
- This step occurs during the scoring-and-selection stage of summarization: identify significant word stems, then rate and pick the best sentences.

Why this is a separate method:
- Encapsulates the two-step Luhn flow (compute significant stems, then select top sentences using the base helper) in one concise, testable operation.
- Keeps high-level orchestration in the subclass while delegating generic selection logic to AbstractSummarizer._get_best_sentences and score computation to rate_sentence, preserving separation of concerns.

## Args:
    document (object):
        Parsed document object. Required attributes:
        - words: iterable/sequence of token strings (used to compute significant stems).
        - sentences: iterable/sequence of sentence objects (each sentence must expose .words iterable).
        The document type is not enforced here; callers must provide a structure compatible with the summarizer's helpers.
    sentences_count (int | str | callable):
        Selection policy for how many sentences to return.
        - Common values: int (number of sentences), string percentage like "30%", or a callable selection policy compatible with AbstractSummarizer._get_best_sentences (e.g., an ItemsCount wrapper or similar).
        - If a callable is provided, it must accept the sorted SentenceInfo iterable and return an iterable of selected SentenceInfo objects.

## Returns:
    tuple:
        A tuple of sentence objects selected from document.sentences, returned in the original document order.
        - If no sentences are selected (e.g., sentences_count resolves to 0 or the document has no sentences), an empty tuple is returned.
        - The sentences are the exact objects from document.sentences (no copies).

## Raises:
    Any exception raised by delegated helpers will propagate unchanged:
    - Exceptions from self._get_significant_words(document.words) (for example, from stemming/normalization or TfDocumentModel).
    - Exceptions from self._get_best_sentences(document.sentences, sentences_count, self.rate_sentence, words) including:
        - AssertionError if _get_best_sentences is given incompatible arguments (see AbstractSummarizer contract).
        - KeyError, ValueError, or any exception thrown by the rating callable (rate_sentence) or the count selection policy.
    This method itself performs no additional validation and does not swallow exceptions.

## State Changes:
Attributes READ:
    - None directly read as plain attributes by this method; it only calls instance methods (self._get_significant_words, self.rate_sentence, self._get_best_sentences).
Attributes WRITTEN:
    - None. This method does not mutate self or the passed document.

## Constraints:
Preconditions:
    - document must provide:
        - document.words: an iterable of tokens suitable for normalization/stemming.
        - document.sentences: an iterable of sentence objects, each exposing .words.
    - The configured stemmer and normalizer used by the instance must be callable and correct (guaranteed by construction of the summarizer).
    - sentences_count must be acceptable by AbstractSummarizer._get_best_sentences (int, percentage string, or callable selection policy).

Postconditions:
    - Returns a tuple of sentence objects (possibly empty) selected and ordered by their original document position.
    - Does not alter self or document state.

## Side Effects:
    - No I/O, network calls, or external resource usage performed by this method itself.
    - Side effects may occur indirectly because delegated helpers (normalizer, stemmer, TfDocumentModel, or user-provided rating/count callables) can raise exceptions or perform side effects; those will propagate.

## Implementation notes (for reimplementation):
    - Compute significant stems by calling the helper with the document's token stream:
        words = self._get_significant_words(document.words)
      This returns an iterable/tuple of stems expected by rate_sentence.
    - Use AbstractSummarizer._get_best_sentences to rank and pick top sentences:
        return self._get_best_sentences(document.sentences, sentences_count, self.rate_sentence, words)
      The method passes the rate function (rate_sentence) and the computed significant stems as additional arguments — rate_sentence must accept (sentence, significant_stems).
    - Keep this orchestration minimal: do not perform other transformations or mutate the document. Let the called helpers handle token normalization, stemming, and sentence rating/selection policy.

### `sumy.summarizers.luhn.LuhnSummarizer._get_significant_words` · *method*

## Summary:
Selects and returns the most significant word stems from a sequence of tokens in the context of the Luhn summarizer; does not modify object state.

## Description:
This method is called during the summarization pipeline to determine which word stems should be considered "significant" when scoring sentences. Known callers:
- LuhnSummarizer.__call__(document, sentences_count): invoked early in the summarization flow to compute significant stems from document.words before selecting best sentences.

Rationale for being a separate method:
- Encapsulates normalization, stemming, stop-word filtering, term-frequency modeling, and final frequency-based filtering into a single reusable step. Separating this logic improves testability and keeps the sentence-rating code focused on scoring rather than term selection.

## Args:
    words (iterable[str]):
        Iterable or sequence of token strings (for example, document.words). Each element will be passed to self.normalize_word; the normalized tokens are then filtered against self._stop_words and stemmed via self.stem_word.
        - Expected: an iterable that yields string-like tokens.
        - Not accepted: passing a raw string is not meaningful here (the method expects token sequence). If a non-iterable is given, TypeError may be raised by iteration or by downstream operations.

## Returns:
    tuple[str, ...]:
        A tuple of selected term keys (stems) chosen as significant. Returned terms are the ones returned by TfDocumentModel.most_frequent_terms(...) (which stores terms lowercased), further filtered to include only terms whose raw term frequency in the document is > 1.
        - Possible values:
            - empty tuple: when no stems meet the frequency>1 criterion or when input has no tokens.
            - tuple of one or more lowercased stem strings.
        - Ordering: the tuple preserves the ordering returned by TfDocumentModel.most_frequent_terms (descending by frequency, tie-broken by stable sort).

## Raises:
    Any exception raised by the following operations may propagate:
    - ValueError from TfDocumentModel.most_frequent_terms if the computed count is negative (triggered when self.significant_percentage < 0 and len(words) * significant_percentage yields a negative integer).
    - ValueError from TfDocumentModel.__init__ if a non-sequence/raw-string misuse occurs (not expected when passing a tuple of stems).
    - Exceptions raised by self.normalize_word or self.stem_word if those methods validate input and raise (propagated unchanged).

## State Changes:
    Attributes READ:
        - self.normalize_word (method): used to normalize each incoming token.
        - self.stem_word (method): used to reduce normalized tokens to stems.
        - self._stop_words (frozenset or set-like): consulted to filter out stop words (compared against normalized tokens).
        - self.significant_percentage (numeric): used to compute how many top terms to select (best_words_count = int(len(filtered_stems) * significant_percentage)).

    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - self.normalize_word and self.stem_word must be callable and accept a single token string.
        - self._stop_words should contain tokens in the same normalized form returned by self.normalize_word (the class's stop_words setter ensures normalization).
        - words must be an iterable of tokens (strings). If words yields non-string objects, normalize_word/stem_word must tolerate them or a TypeError may occur.
        - Typical intended range for self.significant_percentage is >= 0 (commonly in [0.0, 1.0]). Negative values will cause TfDocumentModel.most_frequent_terms to receive a negative count and raise ValueError.

    Postconditions:
        - The method returns a tuple of stems (strings) such that each returned stem has a raw document frequency > 1 (model.term_frequency(stem) > 1).
        - No attribute of self is modified.
        - If best_words_count computed is 0, the underlying TfDocumentModel.most_frequent_terms(0) behavior returns all terms, and the final filter still restricts to frequency>1.
        - Returned stems are in the normalized form used by TfDocumentModel (TfDocumentModel lowercases tokens at construction), so callers should treat them as normalized keys suitable for membership checks against TfDocumentModel.term_frequency.

## Side Effects:
    - Constructs a TfDocumentModel instance from the sequence of filtered stems; this creates an in-memory Counter of term frequencies but has no external I/O or side effects beyond normal memory allocation.
    - No I/O, no network calls, and no mutation of objects outside the method's local scope (other than creating the TfDocumentModel instance).
    - The method may propagate exceptions from normalize/stem/model construction called above.

## Implementation notes / behavior details (for reimplementation):
    - Normalization step: the method first maps self.normalize_word over the input tokens, then filters out tokens present in self._stop_words (comparison uses the normalized token).
    - Stemming step: applies self.stem_word to each remaining normalized token and collects stems into a tuple.
    - Frequency modeling: TfDocumentModel is instantiated with that tuple of stems; it lowercases stored keys internally and computes term frequencies.
    - Selection count: best_words_count = int(len(filtered_stems) * self.significant_percentage). If this evaluates to 0, pass 0 to most_frequent_terms which will (per TfDocumentModel) return all terms.
    - Final filtering: only terms with model.term_frequency(term) > 1 are returned (this removes hapax legomena).
    - Edge cases:
        - Empty input yields an empty tuple.
        - significant_percentage == 0 yields model.most_frequent_terms(0) => all terms, then filtered by frequency>1.
        - significant_percentage > 1 may cause best_words_count > number of distinct terms; model.most_frequent_terms will return at most the available terms (no error).
        - significant_percentage < 0 results in a negative count passed to most_frequent_terms and will raise ValueError as enforced by TfDocumentModel.

### `sumy.summarizers.luhn.LuhnSummarizer.rate_sentence` · *method*

## Summary:
Compute and return a single numeric score for a sentence by taking the maximum rating among all detected contiguous "chunks" that contain significant stems; returns 0 when no chunks are present.

## Description:
Known callers and lifecycle position:
- LuhnSummarizer.__call__: During summarization, __call__ computes significant stems and then delegates sentence scoring to this method as part of the sentence-ranking pipeline. The ranked scores are used by AbstractSummarizer._get_best_sentences to select top sentences for the final summary.
- AbstractSummarizer._get_best_sentences (indirect): this method receives rate_sentence as the per-sentence scoring callback used by the selection routine.

Why this method is separate:
- This method performs the final aggregation (reduce) step: it takes per-chunk ratings (computed by _get_chunk_ratings/_get_chunk_rating) and reduces them to a single sentence-level score by selecting the maximum. Separating aggregation from chunk detection/rating keeps responsibilities small and testable.

## Args:
    sentence (object): An object representing a sentence with a .words attribute (iterable of strings). Each element must be acceptable to self.stem_word (the summarizer's stemmer).
    significant_stems (iterable[str]): Collection of stem strings deemed significant (typically a tuple returned by _get_significant_words). Membership tests (stem in significant_stems) are performed by the chunking logic.

## Returns:
    float|int: The maximum numeric rating among all chunks in the sentence, or 0 when there are no chunks.
    - The chunk ratings originate from _get_chunk_rating, which returns either 0 (int) or significant_words**2 / words_count (evaluated as floating-point due to true division). Thus, callers should expect a numeric type (most often float).
    - If no chunks are found, this method returns the integer 0 (explicitly handled by the "if ratings else 0" logic).

## Raises:
    - No exceptions are explicitly raised by this method itself.
    - Exceptions from called helpers propagate:
        * AssertionError from _get_chunk_rating if it receives an empty chunk (the assertion words_count > 0 exists in _get_chunk_rating). Under the current implementation, _get_chunk_ratings constructs chunks with at least one element, so this assertion should not fire for well-formed sentence inputs.
        * Any other exception raised by self._get_chunk_ratings, self.stem_word, or other instance methods will propagate to the caller.

## State Changes:
Attributes READ (directly or indirectly):
    - Directly: calls self._get_chunk_ratings(sentence, significant_stems).
    - Indirectly (within helpers): self._get_chunk_ratings reads self.max_gap_size and calls self.stem_word and self._get_chunk_rating.
Attributes WRITTEN:
    - None. This method does not modify any self.<attr> fields or mutate the sentence object.

## Constraints:
Preconditions:
    - sentence must expose .words that is iterable and yields items acceptable to self.stem_word (usually plain word strings).
    - significant_stems must support membership tests (containment checks); using a tuple, list, or set is appropriate.
    - For correct operation, the summarizer should have its stop words and stemmer configured consistently (these are managed elsewhere in LuhnSummarizer).

Postconditions:
    - No mutation of self or sentence occurs.
    - The returned value is a non-negative numeric score (0 if no rated chunks exist).

## Side Effects:
    - None: no I/O, external calls, or global mutations. The method purely computes and returns a value based on inputs and helper methods.

## Implementation notes / references:
    - This method delegates chunk extraction to _get_chunk_ratings(sentence, significant_stems) which returns a tuple of ratings (one per chunk).
    - Each chunk rating is computed by _get_chunk_rating; that function removes trailing zeros, asserts the chunk is non-empty, and returns 0 for single-significant-word chunks or (significant_words**2 / words_count) otherwise.
    - Because of the "if ratings else 0" pattern, an empty tuple of ratings yields 0; if ratings exist, max(ratings) is returned.
    - Example (conceptual):
        * Given a sentence with multiple chunks rated [0.0, 2.25, 1.0], this method returns 2.25.
        * Given a sentence with no detected chunks, it returns 0.

### `sumy.summarizers.luhn.LuhnSummarizer._get_chunk_ratings` · *method*

## Summary:
Extracts contiguous chunks of significant/insignificant words from a sentence (based on provided significant stems), scores each chunk via the class's chunk-rating function, and returns a tuple of numeric ratings. The method does not modify the summarizer instance state.

## Description:
This method is invoked during per-sentence scoring to convert a sentence's token stream into scored "chunks" of nearby significant words.

Known callers and context:
- LuhnSummarizer.rate_sentence: calls this method to obtain chunk ratings for a single sentence; the sentence's score is the maximum chunk rating returned.
- The summarization pipeline: rate_sentence is passed as the rating callable to AbstractSummarizer._get_best_sentences when selecting top sentences in LuhnSummarizer.__call__. Thus, _get_chunk_ratings runs during the sentence-scoring stage of the summarization pipeline.
Why this logic is a separate method:
- It separates the chunk extraction (windowing / grouping of significant words) from numeric scoring (performed by _get_chunk_rating), improving testability and readability.

## Args:
    sentence (object):
        A sentence object that must expose an iterable/sequence attribute .words providing tokens in document order.
        - Each token is passed to self.stem_word(token) for comparison against significant_stems.
        - Typical sentence objects are those produced by the project's document parser (the exact class is not required, only the .words contract).

    significant_stems (iterable or container of hashable):
        Collection of canonical word stems considered "significant" (membership tests are performed: stem in significant_stems).
        - Expected to be the tuple/sequence produced by LuhnSummarizer._get_significant_words, but any container supporting membership tests is acceptable.
        - May be empty; in that case no chunks will be produced and an empty tuple is returned.

## Returns:
    tuple:
        A tuple of numeric ratings (int or float) produced by applying self._get_chunk_rating to each extracted chunk, in the same order chunks were discovered in the sentence.
        - If no chunk is found (no significant stems in the sentence), returns an empty tuple.
        - Numeric values derive from _get_chunk_rating: 0 for single-significant-word chunks; otherwise (significant_words**2) / chunk_length (float, due to true division).

## Raises:
    Propagated exceptions from called helpers:
        - Any exception raised by self.stem_word(word) for any token in sentence.words (for example, if normalization/stemming fails) is propagated.
        - Any exception raised by self._get_chunk_rating(chunk) is propagated (it may raise AssertionError if given an empty chunk after trimming, or TypeError if chunk contents are not summable).
    Implementation-level errors:
        - TypeError or AttributeError if sentence has no .words attribute or if .words is not iterable.

## State Changes:
    Attributes READ:
        - self.max_gap_size: used to determine how many consecutive non-significant tokens end a chunk.
        - self._stemmer (indirectly) via self.stem_word(token): the configured stemmer is read by stem_word while normalizing/stemming tokens.
    Attributes WRITTEN:
        - None. The method does not mutate attributes on self.

## Constraints:
    Preconditions:
        - sentence must have a .words iterable of tokens.
        - significant_stems must support membership testing (e.g., set, tuple, list).
        - self.max_gap_size must be a positive integer (>= 1). The algorithm relies on slicing the last max_gap_size tokens of the current chunk; zero or negative values are unsupported and may yield incorrect behavior.
        - self.stem_word must be callable and valid (ensured by AbstractSummarizer construction).

    Postconditions:
        - Returns an immutable tuple of per-chunk numeric ratings (possibly empty).
        - The method does not mutate the sentence object or the summarizer instance.
        - Every chunk passed to self._get_chunk_rating has at least one significant marker at the start (under normal preconditions), so _get_chunk_rating's assertion that chunk length > 0 should be satisfied.

## Algorithm / Behavior (detailed):
1. Initialize an empty list chunks = [].
2. Build a sentinel NONSIGNIFICANT_CHUNK = [0] * self.max_gap_size.
3. Iterate the sentence tokens in order:
   - For each token: compute stem = self.stem_word(token).
   - If stem is in significant_stems and currently not in a chunk:
       - Start a new chunk: set in_chunk = True and append [1] to chunks (initial significant marker).
   - Else if currently in a chunk:
       - Append is_significant_word = int(stem in significant_stems) (1 or 0) to the last chunk.
   - After updating chunks, if there is at least one chunk and the last chunk's trailing max_gap_size markers equal NONSIGNIFICANT_CHUNK (i.e., the last max_gap_size items are all zeros), then set in_chunk = False to close the chunk. The chunk list remains stored (the trailing zeros are not removed here).
4. After processing all tokens, compute ratings = tuple(map(self._get_chunk_rating, chunks)) and return it.
Notes:
- Trailing zeros within a chunk are removed later by _get_chunk_rating (via its helper __remove_trailing_zeros) before numeric scoring; this method leaves chunk content intact when handing it off to the rating function.
- Chunks are only created when a significant stem is encountered; single significant words produce a chunk [1] that will be rated 0 by _get_chunk_rating.

## Edge cases and examples:
    - Empty sentence (sentence.words empty) -> returns ().
    - No significant stems (significant_stems empty or sentence contains none) -> returns ().
    - Short gaps: consecutive non-significant tokens fewer than max_gap_size keep chunk open and appended as zeros; only when max_gap_size consecutive zeros appear is the chunk closed.
    - Single significant word separated by long gaps results in distinct chunks and each chunk is rated independently.

## Side Effects:
    - Calls self.stem_word(token) repeatedly; stem_word may call the configured stemmer which could have side effects (rare). Any side effects from the stemmer are not introduced by this method itself but they will occur if the stemmer has them.
    - No I/O or external service calls are performed by this method itself.

### `sumy.summarizers.luhn.LuhnSummarizer._get_chunk_rating` · *method*

## Summary:
Compute a numeric rating for a contiguous chunk of word-significance markers using Luhn's scoring formula; returns 0 for chunks with exactly one significant word, otherwise returns (significant_words ** 2) / chunk_length. The method does not modify the summarizer instance state.

## Description:
This method rates a single "chunk" produced during sentence scoring in the Luhn summarizer pipeline.

Known callers and context:
- LuhnSummarizer._get_chunk_ratings: invoked via map(self._get_chunk_rating, chunks) to compute a rating for each extracted chunk.
- LuhnSummarizer.rate_sentence: receives the tuple of chunk ratings from _get_chunk_ratings and uses the maximum rating as the sentence score.
- LuhnSummarizer.__call__: the sentence scoring function (rate_sentence) is used by the summarizer selection pipeline (via AbstractSummarizer._get_best_sentences) when selecting top sentences for the summary.

Why this is a separate method:
- Encapsulates the numeric scoring rule and the single-significant-word special case.
- Keeps chunk extraction logic separate from numeric evaluation, making the scoring rule easy to test, adjust, or replace independently.

## Args:
    chunk (Sequence[int] or Sequence[bool]):
        Sequence of markers for a contiguous chunk of words: 1/True indicates a significant word, 0/False a non-significant word.
        - The sequence may include trailing zeros (non-significant markers); these are removed by the private helper before rating.
        - Caller must supply a sequence type that supports len(), indexing/slicing, and summation.

## Returns:
    int or float:
        - Returns 0 (int) if exactly one significant word remains in the trimmed chunk.
        - Otherwise returns a numeric value computed as (significant_words ** 2) / words_count using true division (float). The module enables true division via from __future__ import division, so non-zero ratings are floats.
        - Edge case: an empty trimmed chunk is not allowed (see Raises).

## Raises:
    AssertionError:
        - Raised when the chunk becomes empty after removing trailing zeros (i.e., len(trimmed_chunk) == 0). The code asserts words_count > 0 to guard this precondition.
    TypeError:
        - If elements of chunk are not summable (e.g., contain non-numeric, non-bool types), sum(chunk) may raise TypeError. The method expects numeric-like markers (0/1 ints or booleans).

## State Changes:
    Attributes READ:
        - Does not read any of the summarizer's persistent attributes.
        - Calls the private helper self.__remove_trailing_zeros(collection), but that helper operates only on the provided collection and does not rely on instance attributes.
    Attributes WRITTEN:
        - None. This method does not modify self or other external state.

## Constraints:
    Preconditions:
        - chunk must support len(), indexing/slicing, and sum() (preferably a sequence of ints or booleans).
        - After trimming trailing zeros (via __remove_trailing_zeros), the resulting sequence must have length > 0, otherwise an AssertionError is raised.
        - In normal usage, chunks produced by _get_chunk_ratings start with a significant marker, satisfying the precondition.

    Postconditions:
        - The input sequence is not mutated by this method; trimming is done on a sliced copy returned by the helper.
        - The method returns a numeric rating as described and leaves the summarizer instance unchanged.

## Side Effects:
    - None: pure computation only. No I/O, network calls, or mutations of external objects occur.

### `sumy.summarizers.luhn.LuhnSummarizer.__remove_trailing_zeros` · *method*

## Summary:
Trim trailing elements equal to 0 from an indexable sequence and return a slice that excludes those trailing zeros; if non-empty, the returned sequence ends with a non-zero element.

## Description:
This private helper is used to remove trailing non-significant markers from a chunk before computing its numeric rating in the sentence-scoring pipeline. In this codebase it is called by LuhnSummarizer._get_chunk_rating as the first step when scoring a chunk produced by _get_chunk_ratings.

Why this is a separate method:
- Keeps the chunk-scoring logic focused on scoring rather than on normalization/preparation.
- Centralizes trimming behavior so it can be tested and reasoned about in isolation.
- Avoids code duplication if trimming is needed elsewhere within the class.

Known callers:
- LuhnSummarizer._get_chunk_rating — invoked during sentence rating to prepare the chunk (a sequence of 0/1 markers) for scoring.

## Args:
    collection (Sequence[int] or Sequence[bool] or any indexable & sliceable sequence):
        An indexable, sliceable sequence supporting len(collection), collection[index], and collection[:n].
        Typical elements are integers 0 or 1 (where 0 denotes a non-significant token). Booleans are also valid: False compares equal to 0 and will be treated as a trailing zero.

## Returns:
    Sequence:
        A slice of the input collection up to and including the last element that is not equal to 0.
        - For input with no trailing zeros, returns a slice equivalent to the original sequence (may or may not be the same object depending on the type).
        - For empty input or input where all elements are equal to 0, returns an empty slice (e.g., [] for lists, () for tuples).
        - The returned object follows Python slicing semantics of the input type.

Examples (illustrative):
    - [1, 0, 0] -> [1]
    - (1, 0, 0) -> (1,)
    - [True, False, False] -> [True]
    - [] -> []
    - [0, 0, 0] -> []

## Raises:
    TypeError or IndexError:
        If the provided collection does not implement the sequence protocol (len, indexing, slicing), Python will raise the appropriate built-in exception when those operations are attempted. The method does not perform explicit type checks or raise custom exceptions.

## State Changes:
    Attributes READ:
        None (this method does not access any self.<attr> attributes)
    Attributes WRITTEN:
        None (this method does not modify any self.<attr> attributes)

## Constraints:
    Preconditions:
        - collection must be a finite, indexable, and sliceable sequence.
        - Elements must be comparable to 0 using equality (e.g., ints, bools, or objects whose __eq__ supports comparison to 0).
    Postconditions:
        - The returned sequence contains no trailing elements equal to 0.
        - If the returned sequence is non-empty, its last element is not equal to 0.
        - len(result) <= len(collection).

## Complexity:
    - Time: O(n) in the worst case, where n is len(collection). Scans from the end until a non-zero element is found.
    - Space: O(m) where m is the length of the returned slice (a new sequence object is created by slicing for typical built-in sequence types).

## Side Effects:
    - No I/O or external calls.
    - Does not mutate the input collection (returns a slice). Behavior follows the slicing semantics of the input type.

