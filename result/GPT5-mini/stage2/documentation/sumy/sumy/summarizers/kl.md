# `kl.py`

## `sumy.summarizers.kl.KLSummarizer` · *class*

## Summary:
KLSummarizer is a concrete summarizer implementing a greedy Kullback–Leibler (KL) divergence based sentence-selection algorithm. Given a parsed document it scores sentences by how little adding them would change a summary-to-document distribution (KL divergence) and returns the top sentences selected by the shared selection helper.

## Description:
KLSummarizer should be used when you want an extractive summary that selects whole sentences based on a KL-divergence criterion between a candidate summary distribution and the document-level term-frequency distribution. Typical callers are summarization pipelines that construct a concrete summarizer instance and call it as a callable with (document, sentences_count).

Responsibilities and boundaries:
- Compute a document-level normalized term-frequency (TF) distribution of content words.
- Repeatedly score candidate sentences by computing the KL divergence between a joint (candidate + current summary) distribution and the document TF distribution.
- Greedily select sentences with minimal KL divergence until all candidates are consumed; assign monotonic integer ratings (0, -1, -2, ...) representing selection order.
- Delegate final selection/count policy and original-order restoration to AbstractSummarizer._get_best_sentences.

This class does not:
- Mutate instance-level configuration (apart from reading class-level stop_words and inherited stemmer).
- Perform I/O or maintain persistent caches or external resources.

## State:
Attributes (public/class-level and inherited)
- stop_words (class attribute)
  - Type: frozenset (default: frozenset())
  - Description: membership set of tokens to treat as stop-words when extracting content words.
  - Valid values: any set-like container of hashable tokens (strings). In this class it is declared as a frozenset but may be shadowed by an instance attribute if a caller sets it.
  - Invariant: stop_words must support membership testing (x in stop_words).

Inherited (from AbstractSummarizer)
- _stemmer
  - Type: callable(token) -> stem
  - Constraint: must be callable; AbstractSummarizer.__init__ enforces this.
  - Purpose: used indirectly if subclass needs stemming (the KLS algorithm does not call stem_word by default but normalize_word is used).

Class invariants:
- Methods that rely on sentence objects expect sentence.words to be iterable and tokens to be hashable strings after normalization.
- The class does not change instance attributes during summarization; methods are effectively pure with respect to instance state.

## Lifecycle:
Creation:
- Instantiate normally; this class does not override __init__, so use the AbstractSummarizer constructor semantics:
  - Optionally pass a stemmer callable to the constructor of the concrete summarizer class (the base class will raise ValueError if stemmer is not callable).
  - You can override or set .stop_words on the class or instance prior to calling the summarizer.

Usage (typical sequence):
1. Prepare a parsed document object with an ordered iterable attribute document.sentences; each sentence must expose a .words iterable of tokens.
2. Call the summarizer instance as a callable: summarizer(document, sentences_count)
   - __call__ will:
     - Collect sentences = document.sentences
     - Call _compute_ratings(sentences) to compute per-sentence integer ratings (0, -1, -2, ...).
     - Pass sentences, the sentences_count policy, and the ratings mapping to AbstractSummarizer._get_best_sentences to obtain the final selected sentences ordered by their original document position.
3. Use the returned tuple/list of sentence objects as the extractive summary.

Destruction / cleanup:
- No cleanup required by this class; it does not open resources or require a close/context manager.

Sequencing requirements and ordering:
- __call__ -> _compute_ratings -> compute_tf and repeated calls to _joint_freq and _kl_divergence.
- _get_best_sentences runs after ratings are produced; it expects a rating for each candidate sentence (the current implementation of _compute_ratings provides one).

## Method Map:
flowchart TB
    A[__call__(document, sentences_count)]
    A --> B[_compute_ratings(sentences)]
    B --> C[compute_tf(sentences)  -> document TF (dict token->float)]
    B --> D[_get_content_words_in_sentence(sentence) for each sentence]
    D --> E[_normalize_words(words)]
    E --> F[normalize_word(token) (inherited)]
    D --> G[_filter_out_stop_words(words)]
    B --> H[while candidates remain: compute candidate joint distribution]
    H --> I[_joint_freq(candidate_words, summary_words) -> dict token->float]
    I --> J[_kl_divergence(summary_freq, doc_freq) -> float]
    H --> K[_find_index_of_best_sentence(kls) -> index]
    K --> L[pop best sentence from working list and record rating]
    B --> M[ratings dict: sentence -> int]
    A --> N[_get_best_sentences(sentences, sentences_count, ratings) (inherited)]
    N --> O[return tuple of selected sentences in original order]

Notes:
- The flowchart shows typical invocation order and major helper dependencies. The inherited helpers normalize_word and _get_best_sentences are required for correct operation.

## Detailed behavior of core methods (implementer guidance):
- __call__(document, sentences_count)
  - Inputs:
    - document: object with attribute sentences, an ordered iterable (preferably a sequence) of sentence objects.
    - sentences_count: selection policy forwarded to _get_best_sentences (int, percentage string like "30%", or a selector callable).
  - Output:
    - tuple of selected sentence objects (same objects from document.sentences), ordered by original document order.
  - Preconditions and constraints:
    - document.sentences should be a re-iterable sequence (list/tuple). If it is a single-pass iterator/generator, _compute_ratings will materialize and consume it causing downstream selection to see an exhausted iterable.
    - Sentence objects must be hashable (used as dict keys in ratings) or callers must accept potential TypeError when hashing fails.
  - Side effects: none on instance attributes.

- _compute_ratings(sentences)
  - Purpose: produce mapping sentence -> int (0, -1, -2, ...), where 0 is the first chosen sentence (best), then -1, etc.
  - Steps to implement:
    1. Compute document TF distribution: word_freq = compute_tf(sentences)
       - compute_tf flattens document content words, normalizes them, counts occurrences, and divides counts by total content word count (count must be > 0).
    2. Prepare working lists:
       - sentences_list = list(sentences) (materialize)
       - sentences_as_words = [ _get_content_words_in_sentence(s) for s in sentences ]
    3. Loop until sentences_list empty:
       - summary_as_word_list = _get_all_words_in_doc(summary) where summary is a list of chosen sentence objects
       - For each candidate words list s in sentences_as_words:
         - joint_freq = _joint_freq(s, summary_as_word_list) -> normalized frequencies summing ~1.0
         - score = _kl_divergence(joint_freq, word_freq)
       - Select index_to_remove = _find_index_of_best_sentence(kls)
       - Pop the best_sentence = sentences_list.pop(index_to_remove) and remove corresponding entry in sentences_as_words
       - Append best_sentence to summary
       - Assign ratings[best_sentence] = -1 * len(ratings) (0 first, then -1, -2, ...)
    4. Return ratings dict.
  - Important edge cases:
    - compute_tf may raise ZeroDivisionError if total content words == 0 (no non-stop tokens). The implementation does not guard against this.
    - Duplicate sentence object instances in input: each occurrence is treated as a separate candidate during selection; when inserted into ratings dict, later selections overwrite previous entries for the same object (final rating reflects last selection for that object).
    - Unhashable sentence objects raise TypeError when used as dict keys.

- compute_tf(sentences)
  - Implementation recipe:
    1. Use _get_all_content_words_in_doc(sentences) to obtain a flat list of normalized content words.
       - Note: this helper filters raw tokens against stop_words first and then normalizes survivors (contrasts with per-sentence helper where normalization happens first).
    2. If content_words_count == 0: dividing to compute relative frequencies will raise ZeroDivisionError.
    3. Count tokens with _compute_word_freq(list_of_words) returning token->int.
    4. For each token, produce relative frequency f / content_words_count (float).
  - Returns mapping token->float summing to ~1.0.

- _joint_freq(word_list_1, word_list_2)
  - Merge frequency counts of the two lists (use _compute_word_freq), add counts for shared keys, then divide each sum by total length = len(word_list_1) + len(word_list_2).
  - Raises ZeroDivisionError if both lists are empty.
  - Returned mapping token->float.

- _kl_divergence(summary_freq, doc_freq)
  - For each token w in summary_freq:
    - frequency = doc_freq.get(w); if truthy (non-zero), add frequency * log(frequency / summary_freq[w]) to accumulator.
  - Important constraints:
    - If summary_freq[w] == 0 and doc_freq[w] > 0 -> division-by-zero; implementers should ensure summary_freq values are > 0 or guard accordingly.
    - If doc_freq contains zero/absent tokens, they are skipped.
  - Returns float (0.0 if no tokens had truthy doc_freq entries).

- _get_content_words_in_sentence(sentence) vs _get_all_content_words_in_doc(sentences)
  - _get_content_words_in_sentence: normalize each token (normalize_word), then filter out tokens present in stop_words (membership tested against normalized tokens).
  - _get_all_content_words_in_doc: flattens raw tokens, filters raw tokens against stop_words first, then normalizes survivors.
  - This asymmetry matters: ensure which helper you use depending on whether stop_words contains raw or normalized tokens.

## Raises:
- Constructor (__init__):
  - KLSummarizer does not override __init__. It inherits AbstractSummarizer.__init__, which raises:
    - ValueError if the provided stemmer parameter is not callable.
- During summarization:
  - ZeroDivisionError:
    - compute_tf divides by the total number of content words; if that count is zero (document has no non-stop tokens), a ZeroDivisionError will be raised and propagate.
    - _joint_freq divides by total_len (len(list1) + len(list2)); if both lists are empty, ZeroDivisionError will be raised.
    - _kl_divergence can raise ZeroDivisionError if a doc_freq entry is positive but corresponding summary_freq[w] is zero.
  - TypeError:
    - If sentence objects are unhashable when used as keys in the returned ratings dict.
    - If token elements are unhashable and used as dict keys inside _compute_word_freq or in membership testing against stop_words.
    - If normalize_word or the stemmer raises due to invalid token types.
  - AttributeError:
    - If the provided document or sentence objects lack the expected attributes (.sentences or .words).
  - ValueError / TypeError from math.log or numeric operations if frequency values are negative or otherwise invalid (should not happen for proper distributions).
  - Index/ValueError:
    - _find_index_of_best_sentence will raise ValueError if called with an empty sequence or when min(kls) yields a value that cannot be matched by index (e.g., NaN equality issues).

## Example (usage & implementation notes):
- Preparation:
  - Ensure document is a parsed document object exposing document.sentences as a re-iterable sequence (list/tuple) of sentence objects.
  - Each sentence must expose .words (iterable of token strings or token-like objects).
  - Optionally set summarizer.stop_words to a set/frozenset of tokens appropriate for the token form used by your sentence.words (raw tokens vs normalized tokens).
- Typical use (described as steps, not source code):
  1. Instantiate the concrete summarizer (KLSummarizer inherits AbstractSummarizer so pass an optional stemmer callable to the base constructor if needed).
  2. Call the summarizer with (document, sentences_count):
     - The summarizer computes TF over the document's content words.
     - It then repeatedly scores candidate sentences by constructing joint distributions (sentence + current summary) and computing KL divergence against the document TF.
     - The algorithm greedily selects the candidate with smallest KL score each round, records a rating, and continues until all candidates are consumed.
     - Finally, it calls AbstractSummarizer._get_best_sentences(sentences, sentences_count, ratings) to apply the sentences_count selection policy and restore original order.
  3. Receive the summary as a tuple of sentence objects in original document order.
- Implementation tips:
  - Ensure your normalize_word and stop_words use the same token form (either raw or normalized) consistent with which helper you call for document vs sentence content words.
  - Defensive reification: callers should pass document.sentences as a concrete sequence (list/tuple) to avoid single-pass iterator exhaustion issues.
  - If you anticipate documents with few or no content words, guard compute_tf or callsites to avoid ZeroDivisionError or provide a fallback policy (not implemented by this class by default).

### `sumy.summarizers.kl.KLSummarizer.__call__` · *method*

## Summary:
Invokes the KL-summarizer pipeline on the provided parsed document: computes per-sentence ratings using the KL selection heuristic and returns the top sentences selected by the shared selection helper. This method does not persist state on the instance.

## Description:
This method is the public entry point used by summarization pipelines to produce a summary from a parsed document. Typical callers are pipeline code or user code that constructs a concrete summarizer instance and calls it as a callable with (document, sentences_count). It is invoked during the summarization stage after document parsing and tokenization.

Why this logic is a dedicated method:
- It defines the concrete summarizer's orchestration: compute sentence-level ratings using the KL-based algorithm, then delegate selection and order restoration to the shared helper. Keeping orchestration here keeps algorithm-specific rating logic in this class and reuse of generic selection behavior via _get_best_sentences.

## Args:
    document (object): Parsed document expected to expose an attribute `sentences`, which is an ordered iterable (preferably a sequence like list/tuple) of sentence objects. Each sentence object must be acceptable to the KLSummarizer content-word extraction helpers (i.e., expose `.words` or otherwise match the project's sentence API).
    sentences_count (int or callable or str): Selection policy describing how many sentences to select. Accepted forms:
        - int: number of sentences to select.
        - callable: a selector callable compatible with AbstractSummarizer._get_best_sentences (accepts an iterable of SentenceInfo-like objects and returns an iterable of selected infos).
        - str (e.g., "30%"): percentage string supported indirectly via the ItemsCount utility used by _get_best_sentences.
      The value is forwarded to AbstractSummarizer._get_best_sentences and must satisfy that helper's contract.

## Returns:
    tuple: A tuple of selected sentence objects (the same objects from document.sentences), ordered by their original document order. If no sentences are selected or the document has no sentences, an empty tuple is returned.

## Raises:
    AttributeError: If `document` has no attribute `sentences`.
    TypeError: If `document.sentences` is not iterable in a way the internal helpers expect.
    KeyError: Propagated from AbstractSummarizer._get_best_sentences if a rating mapping is missing a sentence key (unlikely with this implementation because _compute_ratings assigns a rating for every input sentence).
    Any exception raised by underlying helpers is propagated:
        - Exceptions from token normalization/stemming (normalize_word, stem_word).
        - Exceptions from _compute_ratings internals (e.g., division by zero if the document yields zero content words).
        - Exceptions from AbstractSummarizer._get_best_sentences or the provided `sentences_count` selector (AssertionError, ValueError, TypeError, etc.).
    Notes:
        - The method does not catch or convert exceptions; callers should handle exceptions from underlying helpers if needed.

## State Changes:
Attributes READ:
    - self.stop_words: indirectly read by _compute_ratings -> compute_tf -> _get_all_content_words_in_doc -> _filter_out_stop_words.
Attributes WRITTEN:
    - None. The method and its helpers do not mutate instance attributes; they construct and return local data structures only.

## Constraints:
Preconditions:
    - `document.sentences` must be a finite iterable of sentence objects.
    - Prefer passing a re-iterable sequence (list/tuple). If `document.sentences` is a generator or other single-pass iterator, it will be consumed by _compute_ratings (which materializes lists internally) and subsequently passed exhausted to _get_best_sentences, resulting in incorrect selection or an empty result.
    - The sentence objects must be hashable if any selection or mapping operations rely on them being dict keys (the implementation builds a rating dict keyed by sentence objects).
    - The `sentences_count` argument must be valid for AbstractSummarizer._get_best_sentences (int, a compatible callable, or a percentage string supported by ItemsCount).

Postconditions:
    - Returns a tuple of sentence objects selected by the KL-based rating and the provided `sentences_count` policy.
    - The instance's observable state is unchanged (no instance attributes are modified).
    - All intermediate ratings are local and discarded when the method returns.

## Side Effects:
    - Consumes the provided `document.sentences` iterable in callers' context: because _compute_ratings enumerates and materializes sentence lists, passing a single-pass iterator (generator) for `document.sentences` will be exhausted before selection and lead to incorrect or empty results. To avoid this, pass a concrete sequence (list or tuple) for `document.sentences`.
    - No I/O, network calls, or external resource usage are performed by this method itself; side effects are limited to local object allocations and potential exceptions propagated from helper calls.

### `sumy.summarizers.kl.KLSummarizer._get_all_words_in_doc` · *method*

## Summary:
Flattens an iterable of sentence-like objects into a single list containing every word from all sentences; does not modify object state.

## Description:
This helper extracts every item from the .words sequence of each sentence in the provided iterable and returns them as one flat list. It is intended for internal use when callers need a single list of all words across many sentences (for example, to compute frequencies or other corpus-level statistics). The function is separated into its own small helper to keep the word-extraction logic concise and reusable rather than repeated inline.

Known callers and context:
- No specific caller is shown in the provided snippet. Typical usage is from summarizer logic that operates over a collection of sentence objects and needs a flattened list of words (for token-level scoring, frequency counts, or similarity/divergence computations).

Why this is a separate method:
- Centralizes the simple but common operation of flattening sentence.word iterables, improving readability and avoiding duplicating the comprehension at each call site.

## Args:
    sentences (iterable): An iterable (e.g., list, tuple, generator) of sentence-like objects. Each element must expose a .words attribute that is itself an iterable of word elements (tokens, strings, or word objects). No specific length constraints.

## Returns:
    list: A new list containing all elements from every sentence.words iterable, in the order encountered (sentences in iteration order, then words in each sentence's .words iteration order).
    - If `sentences` is empty, returns an empty list.
    - The returned list is independent (a newly allocated list) and can be mutated by the caller without affecting the original sentences' .words sequences.

## Raises:
    TypeError: If `sentences` is not iterable (e.g., None) — raised by attempting to iterate over it.
    AttributeError: If an element in `sentences` does not have a .words attribute.
    Any exception raised by iterating the .words iterable (for example, if .words is not iterable) will propagate.

## State Changes:
Attributes READ:
    - None (the function does not read or depend on any self.<attr> attributes; it only uses the provided `sentences` parameter)

Attributes WRITTEN:
    - None (the function does not modify its inputs or any external state)

## Constraints:
Preconditions:
    - Each item in `sentences` must be an object with a .words attribute that is iterable.
    - The caller should not assume this function will deduplicate, normalize, or type-convert words; it simply returns items as they appear in .words.

Postconditions:
    - Returns a flat list whose length equals the sum of lengths of each sentence.words iterable.
    - No mutation of the original sentence objects or their .words iterables is performed by this function.

## Side Effects:
    - None: the function performs no I/O, logging, or external service calls. It only constructs and returns a new list.

### `sumy.summarizers.kl.KLSummarizer._get_content_words_in_sentence` · *method*

## Summary:
Return the sentence's words after normalizing each token and removing stop words; does not modify self or the input sentence.

## Description:
Known callers and context:
- _compute_ratings: called while converting all sentences to lists of content words as part of the KL-based sentence rating and summary construction pipeline.
- __call__: indirectly invokes this method when computing ratings during a summarization run.

Lifecycle / pipeline stage:
- Invoked during the rating computation stage of summarization: each sentence is converted into a normalized list of content words before frequency and divergence calculations are performed.

Why this is a separate method:
- Encapsulates the two-step transformation (normalization then stop-word filtering) as a clear reusable unit.
- Keeps _compute_ratings focused on ranking logic and allows consistent, testable normalization/filtering behavior in one place.

## Args:
    sentence (object): An object representing a sentence that must provide a .words attribute.
        - .words: an iterable (typically list) of string tokens (words) for the sentence.
        - Allowed values: any iterable of strings; may be empty.
        - No default.

## Returns:
    list[str]: A list of normalized content-word strings produced by:
        1. Applying self.normalize_word to each token in sentence.words.
        2. Removing any token present in self.stop_words.
    Possible/edge-case return values:
        - [] (empty list) when sentence.words is empty or when all tokens are filtered out as stop words.

## Raises:
    AttributeError: If the provided sentence does not have a .words attribute (accessing sentence.words will raise).
    TypeError: If sentence.words is None or not iterable (iteration in normalization will raise).
    Any exception raised by self.normalize_word is propagated (e.g., if normalize_word expects specific token types).

## State Changes:
    Attributes READ:
        - self.stop_words (used indirectly via _filter_out_stop_words)
    Attributes WRITTEN:
        - None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - self.normalize_word must be a callable that accepts a single token and returns a normalized string.
        - self.stop_words should be a container (e.g., set, frozenset) of strings representing stop words.
        - sentence.words must be an iterable of strings (tokens).
    Postconditions:
        - Returns a new list of strings; neither self nor the sentence object is mutated.
        - Every returned token is the result of normalize_word(token) and is not present in self.stop_words.

## Side Effects:
    - None: no I/O, no external service calls, and no mutation of objects outside of the temporary returned list.

### `sumy.summarizers.kl.KLSummarizer._normalize_words` · *method*

## Summary:
Normalize each token in the provided sequence by delegating to the instance's normalization helper and return a new list of normalized tokens. This operation does not modify the object state or the input sequence.

## Description:
Known callers and usage context:
- _get_content_words_in_sentence(sentence): called during per-sentence content-word extraction; invoked on sentence.words.
- _get_all_content_words_in_doc(sentences): called when collecting and normalizing all content words across the document (used by compute_tf).
- Usage lifecycle stage: invoked during token normalization / preprocessing steps of the summarization pipeline when sentence or document tokens must be canonicalized before counting, matching or further processing (e.g., before computing TF or joint distributions).

Why this is a separate method:
- Provides a single place to apply the canonical normalization policy (AbstractSummarizer.normalize_word) to a sequence of tokens, avoiding duplicated list comprehensions across the class.
- Improves readability and testability: callers express intent ("normalize these words") instead of repeating the normalization implementation.
- Encapsulates token-list handling (iterable -> list) so callers do not need to materialize or rebuild lists themselves.

## Args:
    words (iterable[Any]): An iterable (commonly a list or sequence) of token objects. Each token will be passed to self.normalize_word. There is no implicit filtering or type coercion beyond what normalize_word performs.

## Returns:
    list[str]: A new list containing the normalized form of each input token (the return values of self.normalize_word for each token), in the same order as the input iterable.
    - If the input iterable is empty, an empty list is returned.
    - The returned list length equals the number of items yielded by the input iterable (no items are removed by this method).

## Raises:
    - Any exception raised by self.normalize_word for a token is propagated to the caller. In the typical implementation of normalize_word this may include exceptions from text conversion or lowercasing (for example, TypeError or Unicode-related errors); these are not caught here.

## State Changes:
Attributes READ:
    - None (the method does not read or rely on mutable instance fields). It calls the instance method normalize_word, but does not inspect or mutate any self.<attr> fields.

Attributes WRITTEN:
    - None (no instance attributes are modified).

## Constraints:
Preconditions:
    - The caller must provide an iterable of tokens. Each token must be acceptable to self.normalize_word (i.e., satisfying the preconditions of normalize_word such as being convertible to text if required).
    - The summarizer instance must be a properly constructed object with a working normalize_word method (the base-class guarantees this helper exists).

Postconditions:
    - self is unchanged (no side effects on instance state).
    - The returned list contains self.normalize_word(token) for each token produced by the input iterable, preserving input order.

## Side Effects:
    - None: this method performs pure in-process computation and does not perform I/O, network calls, or mutate other objects beyond creating and returning the new list of normalized tokens.

### `sumy.summarizers.kl.KLSummarizer._filter_out_stop_words` · *method*

## Summary:
Returns a new list containing only those tokens from the input iterable that are not present in the summarizer's stop_words set; preserves input order and does not modify the summarizer state.

## Description:
Known callers and lifecycle context:
- KLSummarizer._get_content_words_in_sentence: called after words are normalized to remove stop words from a single sentence during per-sentence processing while computing ratings.
- KLSummarizer._get_all_content_words_in_doc: called on the document's full word list to remove stop words before (or before/after) normalization depending on the caller's workflow.
- These calls occur during the summarizer's __call__ pipeline while computing term frequencies (compute_tf) and sentence ratings (_compute_ratings) as part of producing a summary.

Why this is a separate method:
- The stop-word filtering is a small, reused operation used in multiple places (per-sentence and document-wide). Extracting it to a dedicated helper avoids duplication and centralizes the expected behaviour (literal membership test against self.stop_words), making intent and maintenance clearer.

## Args:
    words (iterable): An iterable of tokens (commonly str objects) to be filtered.
        - Expected element types: hashable tokens that can be tested for membership in a set (strings are typical).
        - Allowed containers: list, tuple, generator, etc.
        - Not allowed: None or non-iterable objects (will raise TypeError).

## Returns:
    list: A newly allocated list containing the elements from `words` for which the membership test (w not in self.stop_words) is True.
        - Order: preserves the original iteration order from `words`.
        - Empty list: returned when `words` is empty or all elements are stop words.
        - Does not modify the input iterable/object.

## Raises:
    TypeError: If `words` is not iterable, or if checking membership in `self.stop_words` requires hashing an unhashable element (e.g., a list) which raises TypeError.
    Any exception raised by evaluating `w not in self.stop_words` (for example if `self.stop_words` is not a set-like object that supports membership testing) will propagate unchanged.

## State Changes:
    Attributes READ:
        - self.stop_words : expected to be a set-like container used for membership checks (class defines stop_words = frozenset()).
    Attributes WRITTEN:
        - None. The method does not modify any attributes of self.

## Constraints:
    Preconditions:
        - self.stop_words must exist and support membership testing (i.e., `x in self.stop_words` should be valid).
        - `words` must be an iterable. Tokens in `words` should be hashable if `self.stop_words` is a set/frozenset.
        - Caller is responsible for supplying tokens in the same normalization/case form as entries in self.stop_words (this function performs a literal membership test and does not normalize tokens itself).
    Postconditions:
        - Returns a list with all tokens from `words` that are not present in `self.stop_words`.
        - self.stop_words and any other instance state remain unchanged.

## Side Effects:
    - No I/O, no network calls, and no mutation of external objects by this method.
    - The method returns references to the original token objects (no deep copy). If tokens are mutable, modifying them elsewhere will affect objects in the returned list.

### `sumy.summarizers.kl.KLSummarizer._compute_word_freq` · *method*

## Summary:
Produce a dictionary that counts how many times each distinct (hashable) token appears in the given iterable of tokens. The result is a pure value (no state mutation) used by the summarizer to build term-frequency maps.

## Description:
This static helper is used to convert a flat sequence of tokens into a simple frequency map:
- Known callers:
    - KLSummarizer.compute_tf: to compute document-level token counts that are later converted into term frequencies.
    - KLSummarizer._joint_freq: to compute per-part frequency maps when combining a candidate sentence with the current summary.
- Lifecycle / pipeline stage:
    - Called during rating computation for sentence ranking: first to derive the reference distribution for KL divergence, and subsequently to compute counts for candidate/joint lists.
- Why separate:
    - The counting logic is reused in multiple places; extracting it avoids duplication and clarifies intent.
    - Implemented as a static method (no access to self) to emphasize pure functionality.

## Args:
    list_of_words (iterable[hashable]): Iterable of tokens (commonly normalized strings). Must be iterable; elements must be hashable so they can be dictionary keys.

## Returns:
    dict: Mapping token -> int where the int is the number of occurrences of that token in list_of_words.
    - If list_of_words is empty, returns an empty dict.
    - All counts are positive integers (>= 1).
    - The sum of all counts equals len(list_of_words) (i.e., counts represent raw occurrences).

## Raises:
    TypeError: If list_of_words is not iterable, or if any element is unhashable (e.g., a list) such that it cannot be used as a dictionary key. These exceptions are not explicitly raised by this function but will naturally propagate from Python operations (iteration or dict key usage).

## State Changes:
    Attributes READ:
        - None (static function; does not read instance attributes)
    Attributes WRITTEN:
        - None (does not modify self or external objects)

## Constraints:
    Preconditions:
        - list_of_words must be an iterable of hashable items.
    Postconditions:
        - Returned dict contains one entry for each distinct element from list_of_words with accurate counts.
        - Input iterable is not modified by this function.

## Side Effects:
    - None: no I/O, no external service calls, and no mutation of objects outside the function. Only local data structures are created.

## Complexity:
    - Time: O(n) where n is the number of items in list_of_words (one pass to count).
    - Space: O(k) for the returned dictionary where k is the number of distinct tokens.

## Example (illustrative):
    - Input: ["apple", "banana", "apple"] → Output: {"apple": 2, "banana": 1}

### `sumy.summarizers.kl.KLSummarizer._get_all_content_words_in_doc` · *method*

## Summary:
Collects every token from the input sentences, removes tokens that are present in the instance stop-word set (membership checked on the raw token form), normalizes the remaining tokens, and returns the resulting list of normalized content words in document order.

## Description:
- Known callers and context:
    - KLSummarizer.compute_tf(sentences) — used during term-frequency computation for the whole document. The typical call chain in this summarizer is: __call__ -> _compute_ratings -> compute_tf -> _get_all_content_words_in_doc.
    - This method is invoked during the "build global word frequency / TF" pipeline step before scoring/summarization decisions are made.

- Why this is its own method:
    - It encapsulates the complete pipeline for producing normalized, stop-word-filtered tokens from an entire document (flattening, stop-word removal, normalization). Centralizing this logic ensures a single point of maintenance for the document-level token extraction used by frequency-based computations (e.g., TF calculation), and keeps compute_tf and other callers concise.

## Args:
    sentences (iterable):
        Iterable of sentence objects. Each sentence object must expose a sequence/iterable attribute named 'words' (for example, a list of token strings). The iterable must be finite (it will be fully consumed by a list comprehension).

## Returns:
    list[str]:
        A list of normalized token strings (the output of normalize_word applied to each token that passed the stop-word filter), preserving document order:
        - The outer order: sentences are processed in the order they appear in the iterable.
        - The inner order: within each sentence, tokens keep their original order.
        - Duplicate tokens are preserved (no uniqueness or deduplication is performed).
        - Empty input yields an empty list.

## Raises:
    Any exception raised by the underlying processing steps will propagate unchanged. Typical examples:
    - AttributeError: if a sentence object does not have a .words attribute.
    - TypeError: if 'sentences' is not iterable, or if a sentence.words value is not iterable in the expected way.
    - Any exception raised by normalize_word (for example encoding/decoding errors coming from to_unicode or calls to .lower()).
    - Any exception raised by membership testing against self.stop_words if stop_words is not a proper container (uncommon if the class is used as intended).

## State Changes:
    Attributes READ:
        - self.stop_words: used to determine which raw tokens to exclude via membership tests.
        - self.normalize_word (method): invoked by _normalize_words to canonicalize tokens. Note: normalize_word is pure and does not mutate state.

    Attributes WRITTEN:
        - None. This method does not modify instance attributes or external objects.

## Constraints:
    Preconditions:
        - Each item in 'sentences' must be a sentence-like object with a .words attribute that is iterable and yields tokens.
        - Because stop-word filtering is performed before normalization in this method, self.stop_words must be suitable for membership testing against the raw token forms present in sentence.words. If stop_words contains normalized tokens but sentence.words are raw forms, those stop-words will not be removed here (see NOTE below).
        - normalize_word must accept the token values yielded from sentence.words; otherwise normalize_word may raise.

    Postconditions:
        - The returned list contains normalized tokens derived from those original tokens that were NOT present in self.stop_words (tested against the raw token values).
        - The returned list preserves the flattened document ordering (sentence order and within-sentence token order).
        - The instance's state is unchanged.

    NOTE (behavioral detail important to callers/implementers):
        - This method filters raw tokens against self.stop_words and then normalizes the survivors. This is semantically different from the sentence-level helper _get_content_words_in_sentence (which normalizes first and then filters). Callers relying on normalized stop-word membership should either use the sentence-level helper or ensure self.stop_words is compatible with raw token forms.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of the input sentence objects is performed.
    - No global state is modified.

### `sumy.summarizers.kl.KLSummarizer.compute_tf` · *method*

## Summary:
Compute the normalized term-frequency distribution of content words found in the given sentences, returning a mapping from each normalized content-word to its relative frequency across the entire input. This method does not modify the object state.

## Description:
Known callers and context:
- Called by KLSummarizer._compute_ratings at the start of the KL-based summarization pipeline to obtain the document-level reference frequency distribution used in KL divergence calculations.
- Invoked during summarization when the algorithm needs a normalized distribution of content words for the whole document.

Why this logic is its own method:
- TF computation is a clear, reusable step (token collection, stop-word filtering, normalization, counting, and normalization to probabilities) used by multiple summarization routines. Encapsulating it facilitates testing, reuse, and separation of concerns from ranking logic.

Key helper behavior relied upon:
- self._get_all_content_words_in_doc(sentences): returns a flat list of normalized content-word tokens from all sentences (applies stop-word filtering and normalization).
- self._compute_word_freq(list_of_words): returns a dict mapping tokens to integer counts.
- Normalization and stop-word filtering are applied by the helper above; keys in the returned dict are normalized tokens (i.e., strings after self.normalize_word).

## Args:
    sentences (iterable): Iterable of Sentence-like objects. Each Sentence must expose a .words attribute (an iterable of raw token strings). No default.

## Returns:
    dict[str, float]: Mapping from normalized content-word to its relative frequency (floating-point). Each value equals count(word) / total_content_words.
    - When total_content_words > 0, values are in (0.0, 1.0] and the values sum to approximately 1.0 (floating-point rounding).
    - No in-place mutations are performed on sentences.

Illustrative example (numeric):
- If the content words across all sentences (after filtering and normalization) are ['apple', 'banana', 'apple'], the method returns {'apple': 2/3, 'banana': 1/3} (approximately {'apple': 0.6666667, 'banana': 0.3333333}).

## Raises:
    ZeroDivisionError: If there are no content words across all sentences (total_content_words == 0). The implementation divides raw counts by the total count without guarding against zero.
    AttributeError: If an element of sentences lacks the expected .words attribute (propagated from helper methods).
    Any exception raised by the helper methods (such as errors during normalization) will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.stop_words (class/instance attribute): used indirectly by _get_all_content_words_in_doc via _filter_out_stop_words.
        - self.normalize_word (instance method): used indirectly by _get_all_content_words_in_doc via _normalize_words to produce the keys in the returned mapping.
        - No other self.<attr> is read or assumed by compute_tf itself; it relies on its helper methods' behavior.
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - sentences must be an iterable of objects with a .words iterable of strings.
        - The token strings must be valid inputs for the class's normalization (self.normalize_word).
        - There should be at least one non-stop-word token across all sentences to avoid ZeroDivisionError.
    Postconditions:
        - The returned dictionary maps normalized content-word strings to floats equal to count/total_count.
        - The method performs no mutation of inputs or of self.

## Side Effects:
    - No I/O, logging, or network access.
    - No mutation of data outside the method (purely constructs and returns new dict).
    - CPU/memory use proportional to the number of tokens (creates intermediate lists and dicts).

### `sumy.summarizers.kl.KLSummarizer._joint_freq` · *method*

## Summary:
Compute the normalized joint frequency distribution over the union of tokens from two word lists and return a mapping token -> float probability; does not modify the object state.

## Description:
Known callers and context:
- KLSummarizer._compute_ratings: Called during the iterative sentence-selection stage of the KL-summarizer. For each candidate sentence, the method builds a joint distribution between the candidate's content words and the current summary's words to be used as the "summary" distribution in a KL divergence calculation.
- Lifecycle stage: invoked repeatedly while computing sentence ratings (ranking) to evaluate how adding a candidate sentence would change the summary distribution.

Why this is a separate method:
- Encapsulates the logic of merging two token-count maps and normalizing by the combined length; the counting logic is delegated to _compute_word_freq and reused elsewhere.
- Keeps _compute_ratings concise and isolates the normalization/merging behavior for easier testing and reasoning.

## Args:
    word_list_1 (sequence[hashable]): First sequence of tokens (commonly a list of normalized content words for a candidate sentence). Must support len() and iteration. Elements must be hashable (e.g., strings).
    word_list_2 (sequence[hashable]): Second sequence of tokens (commonly the flattened words present in the current summary). Same requirements as word_list_1.

Notes on allowed values:
- Either list may be empty, but not both simultaneously (see Raises).
- Typical callers supply lists of strings produced by normalization/filtering helpers; raw token types that are unhashable (e.g., lists) will raise TypeError.

## Returns:
    dict: Mapping token -> float where each float is the token's relative frequency in the concatenation of word_list_1 and word_list_2.
    - The keys are exactly the union of distinct tokens present in the two input lists.
    - The returned frequencies are computed as (count_in_list1 + count_in_list2) / (len(word_list_1) + len(word_list_2)).
    - If one list is empty and the other non-empty, the result is the normalized frequency of the non-empty list.
    - Floating rounding means the values sum to 1.0 within typical floating-point error.

## Raises:
    ZeroDivisionError: If both word_list_1 and word_list_2 are empty (total length == 0), the final normalization step divides by zero.
    TypeError: If either input is not iterable or contains unhashable elements; these errors propagate from iteration or dict key operations inside _compute_word_freq.

## State Changes:
Attributes READ:
    - self._compute_word_freq (method) — invoked to turn each input list into a token -> int count map.
Attributes WRITTEN:
    - None. The method does not modify any self.<attr> fields.

## Constraints:
Preconditions:
    - word_list_1 and word_list_2 must be sized iterables (support len()) and iterable for counting.
    - Elements must be hashable so they can be used as dictionary keys.
    - Preferably, tokens are normalized strings (as produced by the summarizer's normalization helpers) to produce meaningful merged distributions.

Postconditions:
    - When the call returns normally, it provides a dict whose values are non-negative floats summing to ~1.0 and whose keys are the union of distinct tokens from the inputs.
    - self is unchanged (no attributes are mutated).

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside the method except creating and returning a new dictionary.
    - Exceptions from invalid inputs (see Raises) may propagate to the caller.

## Complexity:
    - Time: O(n + m) where n = len(word_list_1), m = len(word_list_2) (one pass to build count maps and one pass to normalize).
    - Space: O(k) where k is the number of distinct tokens across both lists (for the returned dict).

### `sumy.summarizers.kl.KLSummarizer._kl_divergence` · *method*

## Summary:
Compute a scalar divergence score by summing doc-frequency-weighted log ratios for tokens present in the provided summary-frequency mapping. This pure function does not modify object state.

## Description:
This helper performs the numeric part of a KL-style divergence used by the KLSummarizer. For each token key in summary_freq it looks up the corresponding document frequency in doc_freq and, when present and truthy, adds doc_freq[w] * log(doc_freq[w] / summary_freq[w]) to an accumulator.

Known callers and call context:
- KLSummarizer._compute_ratings — invoked inside the greedy sentence-selection loop; for each candidate sentence a joint frequency distribution (sentence + current summary) is produced and passed as summary_freq while the document-level term frequencies are passed as doc_freq.
- Lifecycle stage: called repeatedly during summarization when scoring candidate sentences to decide which sentence to append next.

Why this is a separate method:
- Isolates the mathematical KL computation from the high-level selection logic for clarity and testability.
- Stateless and deterministic: implemented as a static helper so it can be unit tested separately and reused without requiring instance state.

## Args:
    summary_freq (Mapping[hashable, float]):
        Mapping of tokens to their frequency (typically relative frequency / probability) in the summary representation produced by upstream code (e.g., _joint_freq).
        - Expected: numeric (float) values >= 0 for meaningful results.
        - The function iterates exactly over summary_freq's keys.

    doc_freq (Mapping[hashable, float]):
        Mapping of tokens to their frequency (typically relative frequency / probability) in the full document (e.g., compute_tf output).
        - Expected: numeric (float) values >= 0.
        - Tokens absent or mapped to zero are treated as missing and skipped (contribute nothing).

## Returns:
    float:
        The accumulated sum:
        sum_{w in summary_freq} [ doc_freq[w] * log(doc_freq[w] / summary_freq[w]) ] for those w where doc_freq.get(w) is truthy.
        - If no keys in summary_freq have a truthy doc_freq entry, returns 0.0.
        - The returned value is a Python float (subject to typical floating-point precision).

## Raises:
    ZeroDivisionError:
        If for some token w present in summary_freq, summary_freq[w] == 0 and doc_freq.get(w) is truthy (positive), the division frequency / summary_freq[w] triggers a division-by-zero.

    ValueError:
        If any ratio passed to math.log is not within math.log's domain (e.g., negative values), math.log will raise ValueError. Under normal use with non-negative frequency distributions this should not occur.

    TypeError:
        If provided mappings contain non-numeric values that do not support division or multiplication, Python will raise a TypeError during arithmetic operations.

## State Changes:
    Attributes READ:
        None — the function is a static helper and does not read or require any instance attributes.

    Attributes WRITTEN:
        None — no mutations to self or to the provided mappings are performed.

## Constraints:
    Preconditions:
        - summary_freq and doc_freq are mapping-like objects supporting .get(key).
        - Values should be numeric (floats/ints) and non-negative for meaningful divergence values.
        - Callers should ensure summary_freq[w] > 0 for any token w where doc_freq[w] > 0 to avoid ZeroDivisionError if that is undesirable.

    Postconditions:
        - Inputs are unchanged.
        - The returned float equals the specified sum over summary_freq's keys with truthy doc_freq values.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of the provided mappings or external state.

### `sumy.summarizers.kl.KLSummarizer._find_index_of_best_sentence` · *method*

## Summary:
Return the index of the first occurrence of the smallest value in the provided sequence, without mutating any object state.

## Description:
This private helper centralizes the tie-breaking and selection rule used by KLSummarizer when choosing which sentence to pick next based on computed scores (Kullback–Leibler divergence values). It is called at the point in the summarization pipeline where a sequence of numeric scores (one per candidate sentence) has been produced and the algorithm needs the index of the best (minimum) score.

Known callers and context:
    - Called by sentence-selection routines inside an instance of KLSummarizer after Kullback–Leibler divergence (or analogous) scores have been computed for candidate sentences.
    - The exact caller function names are not present in the provided snippet; treat this as an internal utility used during the selection step of the summarization lifecycle.

Why this is a separate method:
    - Encapsulates the tie-breaking rule (first-min wins) and keeps caller code concise.
    - Makes it straightforward to change selection behavior or add logging/testing in one place.

## Args:
    kls (sequence[Comparable]): A non-empty sequence-like container of comparable values (typically numbers). Requirements:
        - Must be non-empty.
        - Must support min(kls) (elements mutually comparable using <).
        - Must implement an index(value) method (e.g., list, tuple, collections.deque).
        - Iterables that do not implement index() (for example, generator objects) are invalid and will raise AttributeError.

## Returns:
    int: Index of the first element in kls that equals the minimum value.
         - Guaranteed to be in the range [0, len(kls) - 1] for valid input.
         - If multiple elements share the minimum value, returns the index of the first occurrence.

## Raises:
    ValueError:
        - If kls is empty, min(kls) raises ValueError("min() arg is an empty sequence").
        - In a corner case where min(kls) returns a value that cannot be matched by equality (for example float('nan')), calling kls.index(min_value) may raise ValueError because equality comparisons can fail to find the element.
    TypeError:
        - If elements of kls are not mutually comparable, min(kls) raises TypeError.
    AttributeError:
        - If kls does not implement index(), calling kls.index(...) will raise AttributeError.
    Any exception produced by the underlying comparison or index operations may propagate.

## State Changes:
    Attributes READ:
        - None (the function does not access self or any object attributes)
    Attributes WRITTEN:
        - None (the function does not modify its arguments or object state)

## Constraints:
    Preconditions:
        - kls must be a non-empty sequence-like object implementing index(value).
        - Elements must be mutually comparable by min().
    Postconditions:
        - The returned integer is a valid index into kls pointing to an element equal to min(kls) (subject to the equality caveat noted above).
        - No mutation of kls or any external state occurs.

## Side Effects:
    - None. The function performs pure computation using built-in operations (min and sequence.index) and does not perform I/O, network calls, or alter external objects.

## Complexity:
    - Time: O(n) to compute min(kls) plus O(n) for kls.index(min_val) in the worst case; overall O(n) with two passes over the sequence.
    - Space: O(1) additional memory.

## Usage notes and example:
    - Valid examples of kls: [0.4, 0.1, 0.1], (2, 3, 1), collections.deque([5, 2, 3]).
    - Invalid examples: a generator expression (no index method), a numpy.ndarray (does not implement list-style index()) unless converted to a list first.
    - Edge-case: if kls contains floating-point NaN values, min(kls) may produce NaN but NaN != NaN, so index(min_val) can raise ValueError; consider sanitizing or handling NaNs before calling this method.

## Suggested alternative (implementation hint):
    - To avoid two passes (min + index) and to robustly handle cases like NaN, callers may compute the index and minimum in a single linear pass (tracking best_value and best_index) instead of using min(...) followed by index(...).

### `sumy.summarizers.kl.KLSummarizer._compute_ratings` · *method*

## Summary:
Computes a mapping of input sentence objects to integer ratings used to rank sentences for the KL-based summarizer; ratings are assigned in greedy selection order (0 for the first selected sentence, then -1, -2, ...). The method does not mutate the summarizer instance.

## Description:
- Known callers:
    - KLSummarizer.__call__(document, sentences_count): invoked during the summarization pipeline to obtain per-sentence scores before selecting the top sentences.
    - Lifecycle stage: rating computation phase, immediately prior to selection by _get_best_sentences.
- Why this logic is a separate method:
    - The algorithm requires multiple distinct steps (global term-frequency computation, repeated candidate scoring by KL divergence, greedy sentence selection and rating assignment). Factoring it out keeps __call__ concise, enables testing of the scoring algorithm in isolation, and separates algorithmic concerns from selection/policy logic.

## Args:
    sentences (iterable): A finite, ordered iterable of sentence objects. Each sentence object must expose a .words attribute (an iterable of token-like objects acceptable to the summarizer's normalization pipeline). The iterable is materialized internally (list(sentences)).

## Returns:
    dict: Mapping from sentence_object -> int.
        - Keys: the exact sentence object instances taken from the input iterable.
        - Values: integer ratings assigned in selection order:
            * 0 for the first (best) sentence chosen,
            * -1 for the second chosen,
            * -2 for the third, etc.
        - The mapping's length equals the number of unique sentence object instances that appear in the input (duplicate object references collapse to one key; see "Edge cases" below).

## Raises:
    ZeroDivisionError:
        - Raised if compute_tf(sentences) divides by zero because there are no content words across the document (content_words_count == 0). This happens when the input sentences are empty or every token is removed as a stop word.
    TypeError:
        - Raised if a sentence object is unhashable when used as a dict key.
    Propagated exceptions from helper methods:
        - Any exception raised by the following helper methods will propagate unchanged:
            * self.compute_tf
            * self._get_content_words_in_sentence
            * self._get_all_words_in_doc
            * self._joint_freq
            * self._kl_divergence
            * self._find_index_of_best_sentence
        - Example propagated errors include encoding/unicode errors from normalization or user exceptions thrown by custom stemmers or stop-word logic.

## State Changes:
- Attributes READ:
    - self.stop_words (via _filter_out_stop_words called from _get_content_words_in_sentence and compute_tf)
    - No other instance attributes are directly read or required by this method; helper methods may access additional class-level or instance-level behavior implicitly.
- Attributes WRITTEN:
    - None (the method does not assign to any self.<attr> fields).
- External objects mutated:
    - None. The method only creates and returns a new dict and local lists. It does not mutate sentence objects.

## Constraints:
- Preconditions:
    - sentences must be a finite iterable; it will be fully materialized as a list.
    - Each sentence must provide a .words iterable compatible with the normalizer and stop-word filtering (e.g., tokens convertible to text).
    - Sentence objects should ideally be hashable if the returned dict is to include them as keys without error.
- Postconditions:
    - For each input position, the method selects one sentence per loop iteration until every input position is removed from the working list; the returned dict contains one entry per unique sentence object with the rating corresponding to the last iteration in which that particular object instance was selected.
    - Ratings are monotonic in selection order (0, -1, -2, ...). Sorting sentences by rating descending yields the greedy selection order produced by the algorithm.
    - The summarizer instance (self) remains unmodified.

## Edge Cases and Behavior Notes:
- Empty input (no sentences) or no content words:
    - If the input contains no content words (e.g., all tokens are stop words or sentences empty), compute_tf will attempt to divide by zero and a ZeroDivisionError will be raised.
- Duplicate sentence object references:
    - If the same sentence object instance appears multiple times in the input iterable, each occurrence is treated as a separate candidate during selection (it will be popped when selected). Because the returned mapping uses the sentence object as the key, later selections overwrite earlier ratings for that object; the final value reflects the last selection iteration for that object.
- Unhashable sentence objects:
    - The method assigns sentences as dict keys; if a sentence object is unhashable, a TypeError will be raised when inserting into the dict.
- KL scoring behavior:
    - For each candidate sentence, a joint frequency distribution is computed between the candidate's content words and the current summary word list; the KL divergence between that joint distribution and the document term-frequency distribution (word_freq) is computed. The candidate with minimal KL divergence is chosen each iteration.
- Robustness of _find_index_of_best_sentence:
    - The helper _find_index_of_best_sentence returns the index of the minimal KL score in the computed list. Under normal operation the list is non-empty because the loop condition mirrors the working sentence list; if an unexpected empty list were passed, a ValueError would propagate.

## Performance:
- Time complexity (approximate):
    - O(N^2 * W) in the worst case, where N is number of sentences and W is average number of unique content words per sentence. Each iteration scores up to O(N) candidates and computing frequency/ divergence work over words contributes factor W.
- Memory complexity:
    - O(N + total_words): the method materializes sentences_list and sentences_as_words and builds frequency maps.

## Side Effects:
- No I/O, network, or filesystem side effects.
- Only local data structures are allocated; the method returns a new dict referencing input sentence objects.
- Caller should avoid mutating sentence objects used as keys while relying on the returned ratings map.

