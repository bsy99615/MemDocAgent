# `text_rank.py`

## `sumy.summarizers.text_rank.TextRankSummarizer` · *class*

*No documentation generated.*

### `sumy.summarizers.text_rank.TextRankSummarizer.stop_words` · *method*

## Summary:
Sets the instance's stop-word set to an immutable, normalized collection derived from the provided iterable of tokens, replacing any previously configured stop words.

## Description:
This method is the property setter for the summarizer's stop words. Typical callers:
- Client or pipeline code that configures a TextRankSummarizer instance before running summarization (e.g., summarizer.stop_words = ["and", "the", ...]).
- Configuration utilities or language-specific factories that load stop-word lists and assign them to the summarizer.

Lifecycle / context:
- Called during the configuration stage, before __call__ is invoked to produce a summary. The stored stop words are consulted by _to_words_set when converting sentences to token sets for graph-weight computations.

Why a separate method:
- Encapsulates normalization (via normalize_word) and immutability (frozenset) in one place so callers don't need to perform these steps manually.
- Keeps input validation and canonicalization centralized and consistent with other normalizing helpers (normalize_word and stem_word).

## Args:
    words (iterable): An iterable of tokens (commonly strings or bytes accepted by normalize_word).
        - Allowed values: any iterable where each element is acceptable to the instance's normalize_word function.
        - Not allowed: a single string if the intent is to provide multi-token list (a plain string will be iterated character-by-character). Use a list/tuple/generator of tokens instead.

## Returns:
    None

## Raises:
    TypeError: If words is not iterable (e.g., None or a non-iterable object).
    Any exception propagated from normalize_word: normalize_word may raise (for example, encoding-related errors or other errors from to_unicode/.lower()); these exceptions are not caught and will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.normalize_word (the method is invoked for each token)
    Attributes WRITTEN:
        - self._stop_words is replaced with a new frozenset containing the normalized token values

## Constraints:
    Preconditions:
        - The instance must provide a callable normalize_word (this is guaranteed by the AbstractSummarizer contract).
        - The caller should pass an iterable of tokens (not a single string unless single-token behavior is intended).
    Postconditions:
        - self._stop_words is a frozenset of normalized tokens (duplicates removed, order not preserved).
        - Subsequent calls (e.g., _to_words_set) will test membership against this frozenset and therefore perform token filtering using the normalized forms.

## Side Effects:
    - Mutates the summarizer instance by replacing self._stop_words.
    - No I/O, network access, or external service calls occur.
    - No mutation of the provided words iterable is performed (the method only iterates it).

## Implementation notes / reimplementation hints:
    - Use map(self.normalize_word, words) to lazily apply normalization over the input iterable.
    - Wrap the mapped sequence in frozenset(...) to deduplicate tokens and make the set immutable.
    - Do not catch exceptions from normalize_word; allow them to bubble up so callers can detect invalid input or encoding errors.
    - Be mindful that passing a plain string will produce stop-words for each character; require callers to pass a sequence/iterable of tokens to avoid this pitfall.

### `sumy.summarizers.text_rank.TextRankSummarizer.__call__` · *method*

## Summary:
Orchestrates TextRank summarization for a parsed document: checks required dependencies, computes per-sentence TextRank scores, and returns the top-ranked sentences (preserving original document order). Does not modify summarizer instance state.

## Description:
- Known callers and pipeline stage:
    - Called by summarization pipelines or client code that instantiate a TextRankSummarizer and invoke it to produce a summary: summarizer_instance(document, sentences_count).
    - Typical lifecycle: After a document has been parsed into sentence objects (document.sentences) and tokenized, this method is invoked as the algorithm's entry point to produce the final summary.

- Why this is a separate method:
    - Implements the public callable interface for this summarizer: it performs high-level orchestration tasks that should remain consistent across summarizer implementations (dependency check, rating computation, and selection). Delegating scoring to rate_sentences and selection to the shared _get_best_sentences helper keeps algorithm-specific logic encapsulated and reuses shared behavior from AbstractSummarizer.

## Args:
    document (object)
        - A parsed document object exposing an iterable/sequence attribute `sentences`.
        - Each sentence object is expected to have attributes used by downstream helpers (for example: sentence.words). The exact sentence shape is documented by the parser producing `document`.
        - Precondition: `document.sentences` must be a finite iterable (list or another container). If it is a generator, it will be fully consumed by selection and therefore exhausted.

    sentences_count (int or callable or other count policy)
        - Forwarded directly to AbstractSummarizer._get_best_sentences as the selection policy.
        - Common values:
            - int: number of top sentences to select (non-negative).
            - string "NN%": percentage specifiers supported by ItemsCount when used.
            - callable: a selector callable that accepts the sorted per-sentence info iterable and returns the selected info objects.
        - The method does not validate the type; invalid values will cause _get_best_sentences or ItemsCount to raise.

## Returns:
    tuple
        - A tuple of selected sentence objects drawn from document.sentences, ordered by their original document order.
        - If document.sentences is empty, returns an empty tuple ().
        - The cardinality and exact membership are determined by the TextRank scores (computed by rate_sentences) and by the count policy passed through sentences_count.
        - Edge cases:
            - If sentences_count requests more items than available, the selection policy determines the result (commonly all available sentences are returned).
            - If the rating mapping lacks an entry for a sentence, a KeyError will propagate from _get_best_sentences.

## Raises:
    ValueError
        - Raised immediately if NumPy is not available. The dependency check invoked by _ensure_dependencies_installed raises a ValueError instructing the user to install NumPy (exact check: numpy is None -> raise ValueError(...)).
    Any exception propagated from called helpers
        - Exceptions raised by rate_sentences, _create_matrix, numpy operations (e.g., numpy.linalg errors), or _get_best_sentences propagate unchanged. Examples include TypeError, KeyError (if rating is a mapping missing keys), ValueError, and NumPy-specific errors. This method does not catch or translate those exceptions.

## State Changes:
- Attributes READ:
    - self.epsilon (used transitively by rate_sentences / power_method)
    - self.damping (used transitively by _create_matrix)
    - self._ZERO_DIVISION_PREVENTION (used transitively by _create_matrix)
    - self._stop_words (used transitively by _to_words_set)
    - self._stemmer (accessed transitively via stem_word when token stemming occurs)
    - Note: __call__ invokes instance methods (rate_sentences) that read these attributes; they are listed because they are required to compute ratings.

- Attributes WRITTEN:
    - None. This method and the helpers it directly calls do not modify instance attributes.

## Constraints:
- Preconditions:
    - NumPy must be importable (module-level numpy is not None) or __call__ will raise ValueError.
    - document.sentences must be a finite iterable of sentence objects. If a generator is passed it will be consumed.
    - Each sentence must be compatible with the expectations of rate_sentences: typically sentence.words is an iterable of tokens acceptable to normalize_word/stem_word.
    - sentences_count must satisfy the contract expected by AbstractSummarizer._get_best_sentences (int, percentage string, or compatible callable).

- Postconditions:
    - Returns a tuple of sentence objects selected by TextRank scores and ordered by their original position in the input document.
    - No instance attributes are mutated by this call.

## Side Effects:
- Consumes the provided sentences iterable:
    - The selection helper fully enumerates the sentences iterable (it materializes lists during sorting). If document.sentences is a generator, it will be exhausted by this call.
- No I/O, logging, or network calls are performed by this method itself.
- Calls into NumPy: numeric computations (matrix creation, dot products, norms) occur in rate_sentences/_create_matrix/power_method; NumPy may raise errors that propagate.
- No external resources are opened or closed by this method.

## Behavior Notes and Examples:
- Empty document:
    - If document.sentences is empty or falsy, the method returns () immediately (no further computation).
- Typical flow:
    1. Ensure NumPy is available.
    2. If sentences exist, compute a rating mapping via self.rate_sentences(document) — a dict mapping sentence -> numeric rank.
    3. Delegate selection to self._get_best_sentences(document.sentences, sentences_count, ratings) and return the resulting tuple.
- Example invocation:
    - summary = summarizer(document, 3)
      This returns up to 3 top-ranked sentences (depending on selection policy) in their original document order.

### `sumy.summarizers.text_rank.TextRankSummarizer._ensure_dependencies_installed` · *method*

## Summary:
Performs a guard check that the module-level NumPy binding is present and raises a clear ValueError if it is missing; does not mutate the object.

## Description:
Known callers and context:
- TextRankSummarizer.__call__(document, sentences_count) — invoked at the start of the summarization pipeline to verify that NumPy is available before performing matrix operations or ranking. This is the visible caller in the class.
- Indirectly protects downstream methods that rely on NumPy (for example _create_matrix and power_method) by failing fast with a user-facing message when NumPy is absent.

Why this is a separate method:
- Centralizes the dependency check and user-facing error message so the guard is not duplicated across multiple entry points.
- Keeps the public call path (.__call__) concise and makes the dependency requirement explicit in one place.
- Implemented as a static method because it does not need access to instance state.

## Args:
None.

## Returns:
None. The function either returns normally (no value) when the module-level name `numpy` is not None, or it raises an exception as described below.

## Raises:
ValueError: Raised exactly when the module-level variable `numpy` is present in the module namespace and equals None. The error message raised is:
"LexRank summarizer requires NumPy. Please, install it by command 'pip install numpy'."

Note: If the module-level name `numpy` is not defined in the module namespace at all, referencing it will raise a NameError before the ValueError check; this function assumes the name exists in the module scope.

## State Changes:
Attributes READ:
- module-level: numpy

Attributes WRITTEN:
- none (no attributes of self or module are modified)

## Constraints:
Preconditions:
- The module must contain a binding named `numpy` (typically injected by the import statement). If that binding is missing, a NameError will occur when this function executes.

Postconditions:
- If the function returns normally, the module-level `numpy` binding was not None at call time (though it might not be a proper NumPy module — this function only checks non-None).
- If `numpy` was None, a ValueError has been raised and normal execution is aborted.

## Side Effects:
- No I/O (no file, network, or console output).
- No external service calls.
- The only observable effect is raising a ValueError when the check fails (interrupting normal control flow).
- Because it is a static method, it does not mutate instance state or any external objects.

### `sumy.summarizers.text_rank.TextRankSummarizer.rate_sentences` · *method*

## Summary:
Maps each sentence in the provided document to a numeric TextRank score by building the sentence transition matrix and extracting its stationary distribution via power iteration; does not modify the summarizer instance.

## Description:
Known callers and lifecycle stage:
- Called by TextRankSummarizer.__call__ during the sentence-rating stage of the summarization pipeline. __call__ invokes this method after ensuring dependencies are installed and the document contains at least one sentence.
- This method is the bridge between graph construction and ranking: it builds the transition matrix for the document (via _create_matrix) and computes the sentence importance scores (via power_method).

Why this is a separate method:
- Separates concerns: matrix construction (_create_matrix), iterative eigenvector computation (power_method), and the high-level mapping of results to sentence objects. Keeping this logic separate improves testability and clarity.

## Args:
    document (object):
        - A document-like object that exposes a .sentences attribute which is an iterable/sequence of sentence-like objects.
        - Each sentence will be used as a key in the returned dictionary and will be passed (indirectly) to _create_matrix, so sentences must be compatible with _to_words_set (i.e., provide a .words attribute that _to_words_set can process).
        - Precondition: document.sentences should be non-empty when calling this method (TextRankSummarizer.__call__ enforces this).

## Returns:
    dict:
        - Mapping from each sentence object in document.sentences to a numeric rank (float-like).
        - The ranks are taken directly from the NumPy array returned by power_method (typically numpy.float64 values).
        - The order is determined by zipping document.sentences with the ranks returned from power_method; normally every sentence is present as a key.
        - Edge cases:
            * If power_method returns fewer ranks than there are sentences (unexpected), zip will silently truncate and some sentences will be omitted from the returned mapping.
            * Ranks are not normalized further by this method; they have the magnitude and scale produced by power_method (which typically converges to a stochastic-like stationary vector).

## Raises:
    - Any exception raised by self._create_matrix(document) (e.g., AttributeError if document/sentences lack expected attributes, AssertionError from _rate_sentences_edge, NumPy exceptions).
    - Any exception raised by self.power_method(matrix, self.epsilon) (e.g., ZeroDivisionError if power_method attempts 1.0 / 0 when called with an empty matrix; NumPy-related errors).
    - TypeError when building the return dictionary if sentence objects are unhashable (dict keys must be hashable).
    - Note: TextRankSummarizer.__call__ typically prevents the empty-document case and checks that NumPy is available; calling rate_sentences directly without those guards may surface the above errors.

## State Changes:
    Attributes READ:
        - self._create_matrix: used to produce the transition matrix.
        - self.power_method: used to compute the rank vector.
        - self.epsilon: numeric tolerance (class default 1e-4) passed to power_method.

    Attributes WRITTEN:
        - None. This method does not mutate any self.<attr> fields.

## Constraints:
    Preconditions:
        - NumPy must be available (the class enforces this via _ensure_dependencies_installed before typical calls).
        - document.sentences must be an iterable/sequence whose length n > 0.
        - Each sentence must be acceptable to _create_matrix/_to_words_set (i.e., expose .words and produce tokenizable values).
        - For correct probabilistic interpretation, self.epsilon should be a small positive float (class default 1e-4).

    Postconditions:
        - Returns a dict mapping a subset or all of document.sentences to numeric ranks computed from the provided document.
        - No attributes of self are modified.
        - No mutation of the provided document or its sentence objects is performed.

## Side Effects:
    - Calls instance methods _create_matrix(document) and power_method(matrix, epsilon); any side effects or exceptions from those methods will propagate.
    - No I/O, no network calls.
    - Does not modify external objects (document or sentences) or perform persistent state changes.

### `sumy.summarizers.text_rank.TextRankSummarizer._create_matrix` · *method*

## Summary:
Constructs the sentence-to-sentence transition (weight) matrix used by the TextRank algorithm for the current document and returns the damped matrix used by the pagerank-like power iteration; does not modify the summarizer instance.

## Description:
Known callers and lifecycle stage:
- Called by TextRankSummarizer.rate_sentences(document) during the sentence-rating stage. rate_sentences invokes this method to build the matrix whose dominant eigenvector (computed by power_method) yields sentence ranks.
- This method runs after token preprocessing (each sentence is converted to a term list by _to_words_set) and before power iteration.

Why this is a separate method:
- Encapsulates the graph construction and damping/teleportation logic used by TextRank so it can be tested independently and kept distinct from ranking logic (power_method) and higher-level control flow (rate_sentences / __call__).

## Args:
    document (object): A document-like object exposing a .sentences attribute that is an iterable/sequence of sentence-like objects. Each sentence is passed to self._to_words_set; therefore each sentence must be compatible with that helper (i.e., have a .words attribute and satisfy the expectations of _to_words_set).

## Returns:
    numpy.ndarray:
        - A 2-D square NumPy array of shape (n, n) where n == number of sentences in document.sentences.
        - dtype: floating-point (NumPy default float, typically float64).
        - Semantics: matrix[i, j] is the probability/weight of transitioning from sentence i to sentence j after applying normalization and damping/teleportation.
        - Typical property: for rows where at least one non-zero similarity exists, the row sums to 1. For rows whose similarity weights are all zero, the row sum equals (1.0 - self.damping) (see Edge Cases below).

## Raises:
    - No exceptions are raised explicitly by this method.
    - The following exceptions may propagate from called helpers or NumPy operations:
        * Any exception from self._to_words_set (e.g., from normalize_word/stem_word or sentence.words access).
        * Any exception from self._rate_sentences_edge (e.g., AssertionError, TypeError).
        * NumPy errors (e.g., if NumPy operations receive malformed shapes), though typical inputs avoid these.
    - Note: callers (e.g., __call__) ensure numpy is available via _ensure_dependencies_installed; invoking _create_matrix without NumPy present will result in a NameError or similar unless dependency checks were performed earlier.

## State Changes:
    Attributes READ:
        - self._to_words_set (method): used to produce token sequences for each sentence.
        - self._rate_sentences_edge (method): used to compute pairwise similarity ratings between sentence token lists.
        - self._ZERO_DIVISION_PREVENTION (float): small positive constant added to denominators to avoid division-by-zero.
        - self.damping (float): damping factor used in teleportation (typical default 0.85).

    Attributes WRITTEN:
        - None. The method does not mutate any self.<attr> attributes.

## Constraints:
    Preconditions:
        - document.sentences must be an iterable/sequence of sentence-like objects acceptable to self._to_words_set.
        - self.damping should be a numeric value; for expected TextRank behavior it should lie in [0.0, 1.0]. Values outside this range will still produce a numeric matrix but will violate the probabilistic interpretation.
        - self._ZERO_DIVISION_PREVENTION must be a small positive float (the implementation assumes it prevents division-by-zero when a row's sum is zero).

    Postconditions:
        - The returned array has shape (n, n) where n == len(document.sentences).
        - For any row i whose pre-teleportation normalized similarity weights sum to 1, the returned row i sums to 1. For a row i whose pre-teleportation similarity weights are all zero, the returned row i sums to (1.0 - self.damping).
        - No attributes on self are modified.

## Behavior / Implementation details (sufficient to reimplement):
    1. Build a list of token sequences: sentences_as_words = [self._to_words_set(sent) for sent in document.sentences].
    2. Let n = len(sentences_as_words). Create a square weights array initialized to zeros with shape (n, n).
    3. For every pair (i, j) with 0 <= i <= j < n:
         - Compute rating = self._rate_sentences_edge(sentences_as_words[i], sentences_as_words[j]).
         - Assign weights[i, j] = rating and weights[j, i] = rating (weights are symmetric at this stage).
    4. Normalize each row in-place by dividing by the row sum plus self._ZERO_DIVISION_PREVENTION:
         - row_sums = weights.sum(axis=1)  # shape (n,)
         - weights = weights / (row_sums[:, numpy.newaxis] + self._ZERO_DIVISION_PREVENTION)
       This broadcasting yields rows that sum to ~1 when row_sums > 0; rows that were all zeros remain all zeros because 0 / tiny -> 0.
    5. Apply teleportation (add the uniform probability to every entry and scale by damping):
         - teleport = numpy.full((n, n), (1.0 - self.damping) / n)
         - result = teleport + self.damping * weights
    6. Return result.

## Edge Cases and Notes:
    - Empty document.sentences (n == 0): the method builds shapes (0, 0) and returns an empty (0, 0) NumPy array; callers typically check for empty documents before invoking rate_sentences/__call__.
    - If a given row has no non-zero similarity ratings (row sum == 0 before normalization), the normalization step leaves that row as zeros due to the added tiny denominator. After teleportation that row's entries all equal (1 - damping) / n *and* the damping contribution is zero, so the row sum equals (1 - damping) (not 1). This is the degenerate-case behavior of the implementation and is mitigated in practice when sentences share tokens with others.
    - When all rows have at least one non-zero similarity value per row, the returned matrix is row-stochastic (each row sums to 1).
    - The initial symmetric weight assignment (weights[i,j] = weights[j,i]) is overwritten by per-row normalization which can break symmetry.
    - Performance: this method computes O(n^2) pairwise ratings; cost is dominated by _rate_sentences_edge which itself is O(len(words_i) * len(words_j)). For large documents this can be expensive.

## Side Effects:
    - No I/O, no network calls.
    - Calls instance helpers _to_words_set and _rate_sentences_edge; exceptions from those methods propagate.
    - Does not mutate the provided document or sentence objects (only reads them).

### `sumy.summarizers.text_rank.TextRankSummarizer._to_words_set` · *method*

## Summary:
Produce a list of stems for the tokens in a sentence by normalizing each token, filtering out tokens present in the instance stop-word set, and applying the configured stemmer; the method does not modify the summarizer's state.

## Description:
- Call sites and pipeline stage:
    - TextRankSummarizer._create_matrix calls this method once per sentence when building sentence representations for pairwise similarity/rating.
    - rate_sentences calls _create_matrix, so _to_words_set is invoked during the rating phase of TextRank summarization prior to matrix construction and power-iteration ranking.
- Purpose of separation:
    - Centralizes token preprocessing (normalization → stop-word filtering → stemming) so _create_matrix and other ranking logic operate on a consistent token representation.
    - Isolates normalization/stemming/stop-word concerns for easier testing and potential reuse.

## Args:
    sentence (object): A sentence object (required).
        - Expected attribute: `sentence.words` — an iterable of tokens (commonly str or bytes) acceptable to AbstractSummarizer.normalize_word.
        - The method will iterate sentence.words once.

## Returns:
    list: A list containing the result of applying self.stem_word to each normalized token that is not present in self._stop_words.
    - Order: preserves the original iteration order of sentence.words (except filtered tokens).
    - Duplicates: preserved (if a token occurs multiple times it may produce repeated stems).
    - Empty list returned when sentence.words is empty or all tokens are filtered by stop words.

## Raises:
    AttributeError: If the provided `sentence` object lacks the attribute `words`.
    TypeError: If `sentence.words` exists but is not iterable (iteration will raise TypeError).
    Any exception propagated from:
        - self.normalize_word(token): e.g., encoding-related errors raised by to_unicode() or .lower().
        - self.stem_word(normalized_token): exceptions from the configured stemmer callable.
    (All such exceptions are not caught by the method and will propagate to the caller.)

## State Changes:
    Attributes READ:
        - self._stop_words: membership tests are performed against normalized tokens.
        - self.normalize_word: called once per token via map to produce normalized tokens used for filtering and passed to stem_word.
        - self.stem_word: called for each token that passes the stop-word filter.
    Attributes WRITTEN:
        - None. The method performs no assignments to instance attributes.

## Constraints:
    Preconditions:
        - self._stop_words should contain normalized tokens (the class's stop_words setter enforces normalization when setting stop words).
        - self.normalize_word and self.stem_word must be callable. AbstractSummarizer guarantees these helpers exist; stem_word typically re-invokes normalize_word internally.
        - sentence.words must be an iterable yielding tokens acceptable to normalize_word.
    Postconditions:
        - Returned list equals [self.stem_word(w) for w in map(self.normalize_word, sentence.words) if w not in self._stop_words].
        - The summarizer instance is unchanged.

## Side Effects:
    - No I/O, no network access.
    - Does not mutate the sentence object or the iterable returned by sentence.words.
    - Potential double-normalization: because AbstractSummarizer.stem_word typically computes self._stemmer(normalize_word(word)), passing an already-normalized token into stem_word will cause normalize_word to be invoked again inside stem_word. This is benign but may be slightly redundant.

## Implementation notes and edge cases:
    - The method uses map(self.normalize_word, sentence.words) to lazily apply normalization; the subsequent list comprehension forces iteration and applies the stop-word filter and stemming.
    - The method's name suggests a "set" but it returns a list; callers rely on this list preserving order and duplicates (e.g., _rate_sentences_edge counts occurrences).
    - If self._stop_words is empty (the default frozenset()), no tokens are filtered.
    - The element type returned depends on the configured stemmer; do not assume str if a custom stemmer returns other types.

### `sumy.summarizers.text_rank.TextRankSummarizer._rate_sentences_edge` · *method*

## Summary:
Computes a numeric similarity weight for an undirected edge between two sentences represented as lists of token strings; returns a non-negative float used as the pairwise weight in the TextRank sentence graph.

## Description:
This helper is called while constructing the sentence-to-sentence weight matrix in the TextRank pipeline. Known callers:
- TextRankSummarizer._create_matrix: invoked for every pair (i, j) of sentences to compute the symmetric weight used in the adjacency/transition matrix.
- Indirect caller chain: TextRankSummarizer.rate_sentences -> _create_matrix -> _rate_sentences_edge; the resulting matrix is fed to power_method to produce final sentence ranks.

This logic is extracted into its own method to encapsulate the pairwise edge scoring rule (token overlap normalized by sentence lengths), keep _create_matrix readable, and allow a single, testable location for tuning or replacing the edge-rating strategy.

## Args:
    words1 (list[str]): Sequence of normalized, stemmed token strings for the first sentence.
        - Typical values: tokens produced by TextRankSummarizer._to_words_set (stop words removed, normalization and stemming applied).
        - May be empty; duplicates are allowed (the function counts occurrences).
    words2 (list[str]): Sequence of normalized, stemmed token strings for the second sentence.
        - Same constraints as words1.

## Returns:
    float: Non-negative weight representing similarity between sentences.
        - 0.0 when there is no token overlap (rank == 0).
        - If both sentences contain exactly one token each (so the normalization denominator becomes zero), returns float(rank) (i.e., 0.0 or 1.0).
        - Otherwise returns rank / (log(len(words1)) + log(len(words2))) where rank is the integer sum of occurrences of words from words1 in words2.
        - The return value is a Python float; no guarantees are made about an upper bound other than being non-negative.

## Raises:
    AssertionError:
        - If rank != 0 but either len(words1) == 0 or len(words2) == 0 (this represents an internal inconsistency and is asserted).
        - If the computed normalization term is (numerically) zero but rank is not 0 or 1 (an impossible state for properly-formed inputs, but asserted defensively).

## State Changes:
    Attributes READ:
        - None (method is a static utility; it does not access self attributes).
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - words1 and words2 must be sequences (support len() and .count()) of hashable tokens (normally strings).
        - Typical callers provide lists of strings; the algorithm relies on .count() on words2 for frequency counts.
        - If both inputs are empty, the function will short-circuit and return 0.0 (rank will be 0).
    Postconditions:
        - Returns a float weight >= 0.0.
        - If return != 0.0 then at least one token from words1 appears in words2.
        - The function will not perform any I/O or mutate its inputs.

## Side Effects:
    - None. The function performs only pure computation on the provided sequences and returns a float.

## Implementation notes and rationale:
    - rank is computed as sum(words2.count(w) for w in words1). This counts duplicates in words1 and multiplicity of matches in words2, thereby favoring stronger overlap when tokens repeat.
    - denom = log(len(words1)) + log(len(words2)) is equivalent to log(len(words1) * len(words2)); the logarithmic scaling reduces the impact of sentence length on the raw overlap count.
    - The special-case check for denom numerically equal to zero protects against division-by-zero when both sentence lengths are 1 (log(1) == 0). In that case the function returns rank as float (0.0 or 1.0).
    - Early return when rank == 0 avoids computing logs for empty inputs and reflects that no overlap yields zero edge weight immediately.
    - Because duplicates are possible, the returned value can exceed 1.0 in some degenerate inputs; typical inputs from _to_words_set are short token lists where values remain in a small range.

### `sumy.summarizers.text_rank.TextRankSummarizer.power_method` · *method*

*No documentation generated.*

