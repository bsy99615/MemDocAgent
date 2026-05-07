# `lex_rank.py`

## `sumy.summarizers.lex_rank.LexRankSummarizer` · *class*

## Summary:
Implements the LexRank extractive summarization algorithm as a concrete AbstractSummarizer: it builds a TF/IDF-weighted sentence similarity graph, converts similarities to a thresholded row-stochastic transition matrix, computes sentence importance via the power method, and returns the top-ranked sentences.

## Description:
This class provides a ready-to-use LexRank summarizer. Typical usage:
- Create an instance (optionally providing a custom stemmer via the inherited AbstractSummarizer constructor).
- Optionally configure stop words by assigning an iterable to the stop_words property (each token will be normalized before being stored).
- Invoke the instance as a callable with a Document object and the requested number of sentences: instance(document, sentences_count).
The Document argument must expose .sentences (an ordered iterable) whose elements are sentence objects exposing .words (an iterable of raw token strings).

Responsibility boundary:
- Implements only the LexRank algorithm steps: token preprocessing, TF and IDF computation, construction of a thresholded similarity/transition matrix, computation of stationary scores (power iteration), and selection of best sentences.
- Delegates token normalization/stemming and final selection ordering to inherited helpers: normalize_word, stem_word, and _get_best_sentences from AbstractSummarizer.
- Does not perform I/O, persist state across runs, or manage external resources.

When to instantiate:
- Instantiate once per summarization configuration (stemmer, stop words, threshold/epsilon override if desired), then call repeatedly on different Document objects.

## State:
Instance attributes (directly defined or inherited and used):
- threshold (float)
  - Default: 0.1 (class attribute)
  - Role: similarity threshold used in _create_matrix; a pairwise cosine similarity strictly greater than this value becomes an edge.
  - Valid values: numeric (float-like). Typical range [0.0, 1.0]; values outside that range may affect edge selection semantics.
  - Invariant: remains a float-like numeric unless reassigned by caller.

- epsilon (float)
  - Default: 0.1 (class attribute)
  - Role: convergence tolerance for the power_method iterative routine.
  - Valid values: positive float (epsilon > 0 recommended). Larger values cause earlier termination (coarser convergence).

- _stop_words (frozenset)
  - Default: empty frozenset() (class attribute)
  - Role: set of normalized tokens to exclude from sentence token lists during preprocessing.
  - Invariant: always stored as a frozenset of normalized tokens (strings) when set via the stop_words setter. Never mutated in-place (immutable).

Inherited state (from AbstractSummarizer):
- _stemmer (callable)
  - Set by AbstractSummarizer.__init__. Must be callable for stem_word to work correctly.
  - Invariant: callable for lifetime of instance.

Class invariants:
- _stemmer is callable.
- _stop_words is a frozenset of normalized tokens (or the initial empty frozenset).
- threshold and epsilon are numeric and used by algorithmic steps without implicit validation.

## Lifecycle:
Creation:
- Construct by calling the class (no explicit __init__ defined here). It inherits AbstractSummarizer.__init__(stemmer=null_stemmer).
  - If a custom stemmer is passed to the constructor and it is not callable, AbstractSummarizer.__init__ raises ValueError("Stemmer has to be a callable object").

Configuration:
- Set stop words before calling the summarizer by assigning an iterable of tokens to the property stop_words. Each token will be passed through normalize_word and the stored set becomes a frozenset.

Usage (typical call sequence):
1. Call summarizer(document, sentences_count).
2. __call__ performs:
   - _ensure_dependencies_installed(): ensures NumPy is available; raises a clear ValueError if not.
   - Preprocessing: for each sentence in document.sentences, call _to_words_set(sentence) to obtain a list of normalized + stemmed tokens with stop words removed.
   - Early exit: if no sentences (empty document.sentences or all sentences filtered to empty), returns tuple() immediately.
   - TF computation: _compute_tf(sentences_words) returns a list of per-sentence normalized term-frequency dicts.
   - IDF computation: _compute_idf(sentences_words) returns a dict mapping terms to math.log(N / (1 + n_j)).
   - Matrix construction: _create_matrix(sentences_words, threshold, tf_metrics, idf_metrics) produces an N x N row-normalized transition matrix (numpy.ndarray).
   - Scoring: power_method(matrix, epsilon) computes a stationary score vector (numpy.ndarray).
   - Mapping: pair original sentence objects with their scores and call _get_best_sentences(document.sentences, sentences_count, ratings) to select and return the top sentences in original order.
3. No explicit destruction or cleanup is required. The summarizer uses only in-memory data and does not open resources that need closing.

Destruction:
- No context-manager or close method; normal garbage collection suffices. Subclasses that allocate external resources must implement their own cleanup.

## Method Map (call dependencies and typical invocation order):
graph TD
    A[Caller: summarizer(document, sentences_count)] --> B[__call__]
    B --> C[_ensure_dependencies_installed]
    B --> D[_to_words_set (per sentence)]
    B --> E[_compute_tf]
    B --> F[_compute_idf]
    B --> G[_create_matrix]
    G --> H[cosine_similarity (per pair)]
    B --> I[power_method]
    I --> J[numpy.dot, numpy.linalg.norm]
    B --> K[_get_best_sentences]
    L[stop_words setter] --> M[self._stop_words updated]
    D --> N[self.normalize_word -> self.stem_word]
    E --> O[_find_tf_max]

(Interpretation: __call__ orchestrates preprocessing via _to_words_set, TF/IDF metrics, matrix construction (which calls cosine_similarity), then power_method and selection via _get_best_sentences. stop_words setter is a configuration path used prior to calling.)

## Raises:
Exceptions that callers must be aware of and their trigger conditions:

- ValueError (construction)
  - Trigger: passing a non-callable as stemmer to the inherited constructor (AbstractSummarizer.__init__). Message: "Stemmer has to be a callable object".

- ValueError (runtime)
  - Trigger: calling __call__ when the module-level numpy variable is None. _ensure_dependencies_installed raises:
    "LexRank summarizer requires NumPy. Please, install it by command 'pip install numpy'."

- KeyError (runtime)
  - Trigger: cosine_similarity indexes tf1[term], tf2[term], or idf_metrics[term] for terms found in the sentence iterables. If TF/IDF mappings do not contain an expected key (e.g., inconsistent preprocessing inputs), a KeyError may be raised.

- ZeroDivisionError (runtime)
  - Trigger: calling power_method with a matrix of shape (0, 0) causes division 1.0 / sentences_count to attempt division by zero (len(matrix) == 0). The code does not explicitly guard against empty matrices in power_method; callers must ensure non-empty matrices or avoid invoking power_method on empty matrices (in practice __call__ returns early for empty documents).

- TypeError / ValueError (runtime)
  - Trigger: malformed inputs to methods (e.g., non-iterable sentence.words, non-numeric threshold/epsilon, or passing non-array-like to power_method) will cause underlying Python/NumPy operations to raise TypeError or ValueError.

Note: many potential exceptions are propagated from helper methods (normalize_word, stem_word, _get_best_sentences) per AbstractSummarizer semantics.

## Example (prose demonstration):
1. Instantiate a LexRankSummarizer (optionally pass a callable stemmer to the constructor).
2. Configure stop words: assign an iterable of tokens to summarizer.stop_words; each token will be normalized when stored.
3. Prepare a Document object with an ordered .sentences iterable. Each sentence must expose a .words iterable of raw token strings produced by a tokenizer.
4. Request a summary by calling the summarizer like a function with the Document and an integer sentences_count. The summarizer returns a tuple of selected sentence objects (length <= sentences_count) taken from the input document, ordered as in the original document.
5. No cleanup is needed for the summarizer instance itself.

Implementation notes for reimplementation:
- Preprocess tokens in _to_words_set by calling normalize_word on each raw token and then stem_word on the normalized token; exclude tokens present in the stored _stop_words frozenset. Preserve token order and duplicates.
- Compute per-sentence TF as Counter(term_counts) then normalize each term by dividing by the sentence's maximum term count (use _find_tf_max to safely return 1 for empty counters).
- Compute IDF as idf(term) = ln(N / (1 + n_j)) where N is number of sentences and n_j is the number of sentences containing the term (counted with membership tests).
- Build an N x N numpy matrix of pairwise cosine similarities, threshold into binary edges (> threshold -> 1 else 0), count outgoing edges per row, then divide each row by its degree (use degree=1 when degree==0 to avoid division-by-zero).
- Use the power method: initialize a uniform probability vector of length N (1/N each), iteratively multiply by the transposed matrix until the L2 norm difference between successive vectors <= epsilon, and return the converged vector.
- Final selection delegates to _get_best_sentences(document.sentences, sentences_count, ratings_mapping) where ratings_mapping maps original sentence objects to their numeric score.

### `sumy.summarizers.lex_rank.LexRankSummarizer.stop_words` · *method*

## Summary:
Set the summarizer's stop-word set by normalizing each supplied token and storing the result as an immutable frozenset on the instance.

## Description:
This is the property setter used to configure which tokens should be treated as stop words by the summarizer. Typical callers:
- External client code configuring the summarizer before calling it (e.g., summarizer.stop_words = iterable_of_tokens). This is a configuration/lifecycle step performed prior to invoking the summarizer on a document.
- The summarizer's internal methods read the stored set; notably, _to_words_set filters sentence tokens against self._stop_words when building sentence word lists used by scoring.

This logic exists as a dedicated setter (property) so normalization and immutability are applied in one centralized place. Centralizing avoids repeating normalization logic in multiple places, ensures the stored set is hashable/efficient (frozenset) and prevents accidental mutation after configuration.

## Args:
    words (iterable[str]): An iterable of tokens (typically strings) representing stop words. Each element will be passed to self.normalize_word before being added to the stored set. There is no default value in this setter — it is invoked only when the caller assigns to the property.

## Returns:
    None: The setter does not return a value; it updates the instance state (self._stop_words).

## Raises:
    No exceptions are explicitly raised by this setter. Runtime exceptions raised by:
    - Passing a non-iterable as words (e.g., TypeError when attempting to iterate), or
    - self.normalize_word raising an exception for particular inputs,
    will propagate to the caller.

## State Changes:
    Attributes READ:
        - (calls) self.normalize_word (method) for each input token; no self.<attr> fields are read from this method's body.
    Attributes WRITTEN:
        - self._stop_words is replaced with a frozenset containing the normalized tokens.

## Constraints:
    Preconditions:
        - self.normalize_word must be a callable method on the instance that accepts individual tokens and returns their normalized form (commonly a string).
        - words must be an iterable of tokens (strings or values acceptable to normalize_word).
    Postconditions:
        - After the call, self._stop_words is a frozenset containing the normalized representations of the items from words.
        - Subsequent reads of self._stop_words (for example by _to_words_set) will see the immutable, normalized set immediately.

## Side Effects:
    - Mutates only the instance attribute self._stop_words (assigns a new frozenset).
    - No I/O, no network calls, and no modifications of objects outside this instance are performed by this setter.

### `sumy.summarizers.lex_rank.LexRankSummarizer.__call__` · *method*

## Summary:
Runs the LexRank summarization pipeline on a Document: converts each sentence to a filtered list of normalized + stemmed tokens, computes TF and IDF statistics, constructs a thresholded and row-normalized sentence similarity matrix, computes sentence importance scores with the power method, and returns the top-ranked sentences. The call does not modify the summarizer's persistent attributes.

## Description:
This method is the high-level orchestration of the LexRank algorithm and is intended to be invoked by external code that needs an extractive summary, for example an application-level summarization routine that calls the summarizer as a callable (summarizer(document, n)). It is executed during the summarization stage after a Document object (with sentences) has been prepared.

It is implemented as a dedicated method because it composes several independent steps (preprocessing, TF/IDF computation, matrix construction, iterative scoring, and selection). Keeping this orchestration separate enables testing and overriding of individual steps (_to_words_set, _compute_tf, _compute_idf, _create_matrix, power_method, _get_best_sentences) in subclasses.

High-level flow:
1. Verify NumPy is available (_ensure_dependencies_installed).
2. Convert each sentence to a filtered list of tokens via _to_words_set.
3. If there are no sentences in the document, return an empty tuple immediately.
4. Compute term-frequency metrics per sentence (_compute_tf) and inverse document frequency across sentences (_compute_idf).
5. Build the sentence similarity (transition) matrix with _create_matrix using self.threshold and the TF/IDF metrics.
6. Compute importance scores by calling power_method(matrix, self.epsilon).
7. Pair original sentence objects with their scores and pass them to _get_best_sentences to select and return the top sentences.

## Args:
    document (object):
        - Required. Must provide a .sentences iterable (e.g., list) of sentence objects.
        - Each sentence object must provide .words (an iterable of token strings). Tokens are passed through the summarizer's normalize_word and stem_word helpers inside _to_words_set.
    sentences_count (int):
        - Required. Number of sentences requested for the summary.
        - Expected to be an integer. This method does not validate ranges (e.g., negative values); callers should provide a sensible non-negative integer.

## Returns:
    tuple:
        - Delegates final selection to self._get_best_sentences and returns whatever that method returns (typically a tuple of sentence objects from document.sentences).
        - If document.sentences is empty (no sentences to process), returns an empty tuple() immediately.
        - The length of the returned tuple will be <= sentences_count depending on _get_best_sentences behavior.

## Raises:
    ValueError:
        - If NumPy is not importable, _ensure_dependencies_installed raises and propagates:
          "LexRank summarizer requires NumPy. Please, install it by command 'pip install numpy'."
    (Other exceptions may be raised by helper methods if inputs are malformed; those are not explicitly raised here.)

## State Changes:
    Attributes READ:
        - self.threshold (float): used when constructing the adjacency/thresholded similarity matrix.
        - self.epsilon (float): used as the convergence tolerance passed to power_method.
        - self._stop_words / self.stop_words (via _to_words_set): used to filter tokens in each sentence.
        - Helper methods (normalize_word, stem_word) are invoked to transform tokens but are not attributes.

    Attributes WRITTEN:
        - None. This method does not assign to or persistently modify attributes on self.

    Local objects created (not stored on self):
        - sentences_words: list[list[str]] — list of token lists for each sentence (duplicates preserved).
        - tf_metrics: list[dict[str, float]] — per-sentence normalized term-frequency metrics.
        - idf_metrics: dict[str, float] — inverse document frequency values for terms.
        - matrix: numpy.ndarray (shape: N x N) — row-normalized transition matrix.
        - scores: numpy.ndarray (shape: N,) — importance vector returned by power_method.
        - ratings: dict mapping sentence objects -> numeric score (numpy.float64 or float).

## Constraints:
    Preconditions:
        - document must have a .sentences iterable; each sentence must expose .words (iterable of strings).
        - NumPy must be available in the runtime, otherwise a ValueError is raised.
        - sentences_count should be an integer; meaningful behavior for negative values is not defined here.

    Postconditions:
        - The summarizer instance's state (threshold, epsilon, stop_words, etc.) is unchanged.
        - The method returns a tuple produced by _get_best_sentences, containing sentence objects selected from document.sentences.

## Side Effects:
    - Allocates temporary NumPy arrays (matrix, degree and probability vectors) during computation.
    - No disk, network I/O, or external service calls are performed.
    - Does not mutate the Document or sentence objects; all operations read .sentences and .words only.

## Implementation notes (for reimplementation):
    - _to_words_set produces a list of normalized and stemmed token strings for a sentence, excluding tokens in the stop-word set; duplicates are preserved.
    - If document.sentences is empty, the method returns tuple() immediately; it does not attempt TF/IDF or matrix construction.
    - scores is computed exactly as scores = self.power_method(matrix, self.epsilon) and then paired with sentences via zip(document.sentences, scores).
    - ratings is a plain dict mapping each sentence object (as used in document.sentences) to the corresponding numeric score from the power method.
    - Final selection and ordering semantics depend on _get_best_sentences; this method delegates selection entirely to that helper.

### `sumy.summarizers.lex_rank.LexRankSummarizer._ensure_dependencies_installed` · *method*

## Summary:
Performs a guard check that the module-level NumPy object is present; raises a clear ValueError if the module-level name `numpy` is None. The call has no effect on object state when it returns.

## Description:
This function encapsulates a single, explicit dependency check: it inspects the module-level name `numpy` and ensures it is not None. No callers are visible in the provided snippet. The function exists to centralize the user-facing error message and the dependency check in one place rather than duplicating the same guard and message at multiple call sites.

This method does not attempt to import NumPy itself; it only tests the value of the name `numpy` already present in the module namespace.

## Args:
None.

## Returns:
None. The function either completes silently (when `numpy` is not None) or raises an exception. There is no return value.

## Raises:
ValueError: Raised exactly when the module-level variable `numpy` is None. The raised message is:
"LexRank summarizer requires NumPy. Please, install it by command 'pip install numpy'."

Note: If the module-level name `numpy` is not defined at all in the module namespace, calling this function will raise a NameError before the ValueError check — the code assumes `numpy` exists in the module scope.

## State Changes:
Attributes READ:
    - module-level: numpy

Attributes WRITTEN:
    - none

## Constraints:
Preconditions:
    - The module-level name `numpy` must be defined in the module namespace (otherwise a NameError will occur when the function references it).

Postconditions:
    - If the function returns normally, `numpy` was not None at the time of the check.
    - If `numpy` was None, a ValueError is raised and execution is interrupted.

## Side Effects:
    - No I/O or external service calls.
    - No mutations of objects outside the function.
    - The only observable effect is raising ValueError when the check fails (which stops normal control flow).

### `sumy.summarizers.lex_rank.LexRankSummarizer._to_words_set` · *method*

## Summary:
Convert a sentence's raw tokens into a list of stemmed terms while excluding configured stop words; this prepares a sentence's token set for TF/IDF and similarity computations without mutating summarizer state.

## Description:
Known callers and context:
- LexRankSummarizer.__call__ invokes this method during summarization to build sentences_words:
  sentences_words = [self._to_words_set(s) for s in document.sentences]
  It is executed early in the LexRank pipeline, immediately before TF/IDF metrics are computed and the similarity matrix is built.
- Lifecycle stage: token normalization → stop-word filtering → stemming; this method encapsulates that entire preprocessing step for a single sentence.

Why this is a separate method:
- Encapsulates token canonicalization and stop-word filtering used across several later steps (TF computation, IDF computation, cosine similarity), improving readability and testability.
- Keeps __call__ focused on high-level algorithm flow and allows consistent reuse of normalization/stemming logic across sentences.

## Args:
    sentence (Sentence-like): An object that exposes a .words attribute (an iterable/sequence of raw token strings). In this codebase, this is sumy.models.dom._sentence.Sentence whose .words is produced by the tokenizer (typically a list of text tokens).

## Returns:
    list: A list of terms obtained by applying the summarizer's stemming function to each normalized token from the sentence, excluding tokens present in self._stop_words.
    - Element type: the return type of self.stem_word (commonly str), because stemmers can return any hashable or comparable token representation.
    - Empty list is returned when sentence.words is empty or when all tokens are filtered out as stop words.

## Raises:
    Any exception raised by the underlying helpers or iteration will propagate:
    - Exceptions from sentence.words iteration (e.g., if tokenizer raises).
    - Exceptions from self.normalize_word (e.g., encoding/Unicode errors).
    - Exceptions from self.stem_word (e.g., if the configured stemmer callable raises).
    No exceptions are explicitly raised by this method itself.

## State Changes:
    Attributes READ:
        - self._stop_words
        - self.normalize_word (method used for normalization)
        - self.stem_word (method used to obtain token stems)
    Attributes WRITTEN:
        - None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - sentence must provide a .words iterable of raw tokens (strings or objects acceptable to normalize_word).
        - The instance must have been constructed with a callable stemmer (AbstractSummarizer enforces this invariant), because stem_word ultimately invokes that callable.
        - self._stop_words must be an iterable/frozenset of normalized tokens (LexRankSummarizer.stop_words setter normalizes stop-words already).
    Postconditions:
        - Returns a list of stemmed tokens corresponding to non-stop tokens in the input sentence.
        - Does not change the summarizer instance state.

## Side Effects:
    - No I/O or external service interaction.
    - No mutation of objects outside self (it consumes sentence.words but does not modify the sentence).
    - The method may call other instance methods (normalize_word and stem_word) which may themselves raise exceptions; those exceptions propagate to the caller.

## Notes and implementation details (for reimplementation):
    - Implementation steps:
        1. Iterate tokens from sentence.words.
        2. Normalize each token via self.normalize_word.
        3. Skip any normalized token present in self._stop_words (stop words are expected in normalized form).
        4. For tokens that pass the filter, compute stem = self.stem_word(normalized_token) and collect stems into a list.
        5. Return the collected list.
    - The method uses normalized tokens for stop-word membership checks; LexRankSummarizer.stop_words setter ensures stop words are stored normalized.
    - Because AbstractSummarizer.stem_word performs normalization internally (it calls normalize_word again), calling stem_word on an already normalized token is safe (normalize is idempotent in typical implementations).
    - The returned list preserves the order of tokens as produced by the sentence tokenizer, subject to removal of stop words.

### `sumy.summarizers.lex_rank.LexRankSummarizer._compute_tf` · *method*

## Summary:
Compute term-frequency (TF) metrics for each sentence by normalizing raw term counts so the highest term frequency in a sentence becomes 1.0; returns one TF mapping per input sentence without modifying object state.

## Description:
This method is called by LexRankSummarizer.__call__ during the summarization pipeline after sentences have been converted to lists of normalized, stemmed words (see _to_words_set). It converts each sentence (an iterable of terms) into a Counter of term counts, then for each sentence produces a mapping from term -> normalized TF = count / max_count_in_sentence.

It is a separate method to:
- Isolate TF computation logic for clarity and testability.
- Allow reuse from other parts of the summarizer (or unit tests) without repeating code.
- Keep __call__ focused on the overall pipeline (TF/IDF, matrix creation, ranking).

## Args:
    sentences (Iterable[Iterable[str]]):
        An iterable of sentences, where each sentence is itself an iterable of terms (strings).
        - Typical input: a list of lists produced by _to_words_set (e.g., [['word1','word2'], ['word2','word3']]).
        - Terms must be hashable (strings are expected) because they are used as Counter keys.
        - Allowed values: any iterable-of-iterable structure; empty sequence and empty sentences are allowed.

## Returns:
    list[dict[str, float]]:
        A list with one dictionary per input sentence. Each dictionary maps terms present in that sentence to a normalized TF value (float).
        - Normalized TF formula: term_count / max_term_count_in_that_sentence.
        - Values are floats in the range (0.0, 1.0], except an empty sentence yields an empty dict.
        - If a sentence contains only one instance of a term (max count == 1), that term's TF will be 1.0.
        - If the input iterable is empty, an empty list is returned.

## Raises:
    This method does not raise exceptions itself in normal use.
    - If elements of sentences are not hashable (e.g., lists), Counter() will raise TypeError; callers must pass iterables of hashable terms (strings are expected).
    - No ZeroDivisionError can occur because _find_tf_max returns 1 when the sentence Counter is empty.

## State Changes:
    Attributes READ:
        - None of the object's instance attributes are read. The method calls self._find_tf_max (a helper) but does not access or mutate instance fields.

    Attributes WRITTEN:
        - None. This method does not modify self or mutate external objects passed in.

## Constraints:
    Preconditions:
        - Each sentence must be an iterable of hashable items (strings recommended).
        - Typical callers should provide sentences that are already normalized and stemmed (e.g., output of _to_words_set) to ensure consistent TF semantics.

    Postconditions:
        - Returns a list of per-sentence TF dictionaries whose keys are terms found in the corresponding input sentence and whose values are normalized floats as described above.
        - The input sentences iterable is not mutated by this method.

## Side Effects:
    - No I/O or external service calls.
    - No mutations to objects outside self; the method creates new Counter and dict objects only.
    - Relies on the helper self._find_tf_max to guard against empty Counters; no external side effects result from that call.

### `sumy.summarizers.lex_rank.LexRankSummarizer._find_tf_max` · *method*

## Summary:
Return the maximum term frequency from a mapping of term->count, with a safe default of 1 when the mapping is empty or falsy; does not modify input state.

## Description:
Known callers and context:
- Called from LexRankSummarizer._compute_tf while computing per-sentence term-frequency metrics during the summarization pipeline invoked by LexRankSummarizer.__call__. In that pipeline, each sentence is represented as a collections.Counter (mapping token -> integer count) and this helper determines the maximum raw frequency for normalization.

Why this is a separate method:
- Encapsulates the logic for obtaining a robust maximum term frequency including the empty-case default (1). Extracting this behavior keeps _compute_tf concise, makes the empty-case behavior explicit and testable, and centralizes any future changes to how the max frequency is chosen.

## Args:
    terms (Mapping[str, numbers.Number] or collections.Counter or any object with a values() iterable):
        Mapping-like object whose values are numeric term frequencies (integers or floats).
        - Allowed values: any mapping where values() yields comparable numeric values.
        - Falsy inputs (e.g., an empty mapping, empty Counter(), or None) are treated specially and produce the default return value (1).

## Returns:
    int or float:
        The maximum value among terms.values() when terms is truthy and contains at least one value.
        If terms is falsy or empty, returns the integer 1.
        - If the values are integers, the return will be an int; if they are floats, the return will be a float.

## Raises:
    No exceptions are explicitly raised by the function. However, callers should be aware of exceptions that can originate from the built-in operations used:
    - AttributeError: if the provided `terms` object does not implement a values() method (e.g., passing an object without values()).
    - TypeError: if values() yields elements that cannot be compared (for example, heterogeneous or non-orderable types in Python 3) so max(...) fails.
    These errors are direct consequences of calling max(...) on the iterable returned by terms.values().

## State Changes:
    Attributes READ:
        - None (this is a static helper; it does not access self)
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - `terms` should be a mapping-like object (preferably a Counter or dict) whose values are numeric counts.
        - If `terms` is truthy, values() must yield at least one element and those elements must be mutually comparable by max().

    Postconditions:
        - Returns the numeric maximum of the provided values when terms is non-empty.
        - If `terms` is empty or otherwise falsy, returns 1.
        - The input `terms` is not modified.

## Side Effects:
    - None: no I/O, no network calls, and no mutation of objects outside this function.
    - Purely a read-only computation based on the provided mapping.

## Implementation notes / reimplementation hint:
    - Implement as a small, deterministic helper that examines the mapping's truthiness first and only calls max(...) when there are values to avoid a ValueError from max(empty).
    - Example intent (informational, not code): if terms is falsy -> return 1, else -> return max(terms.values()).

### `sumy.summarizers.lex_rank.LexRankSummarizer._compute_idf` · *method*

## Summary:
Compute and return a mapping from each unique term (token) observed across the provided tokenized sentences to its inverse document frequency (IDF) value (natural log). This is a pure computation with no side effects.

## Description:
Known callers and lifecycle:
- Called by LexRankSummarizer.__call__ during the summarization pipeline after sentence token sets are prepared and term-frequency (TF) metrics are computed. Typical call sequence in that pipeline:
  - sentences_words = [self._to_words_set(s) for s in document.sentences]
  - tf_metrics = self._compute_tf(sentences_words)
  - idf_metrics = self._compute_idf(sentences_words)
- The method runs in the stage that prepares statistics needed to build the sentence similarity matrix (used by _create_matrix and cosine_similarity).

Why this is a separate method:
- IDF calculation is a distinct statistical operation used by multiple subsequent steps (matrix creation, cosine similarity). Encapsulating it clarifies responsibilities, improves testability, and avoids duplicating logic.

## Args:
    sentences (Sequence[Iterable[str]]): A sequence (usually list) of sentences, where each sentence is an iterable of term tokens (strings). Each term must be hashable (usable as a dict key) and sentences must support membership testing ("term in sentence"). Terms are expected to be already normalized/stemmed by the caller.

## Returns:
    dict[str, float]: A dictionary mapping each distinct term to its IDF value computed as:
        idf(term) = ln(N / (1 + n_j))
    where:
      - N is the total number of sentences (len(sentences)),
      - n_j is the number of sentences that contain the term (counts sentence-level presence, not token frequency).
    Notes:
      - If the input sequence is empty, the function returns an empty dictionary.
      - IDF values are floats (natural logarithm). They may be positive, zero, or negative depending on term distribution.

## Raises:
    - The method does not explicitly raise any custom exceptions.
    - If callers provide inputs that do not meet the expected shapes/types (for example, sentences is None, elements are not iterable, or membership testing is unsupported), Python will raise built-in exceptions (TypeError or similar). These are not raised by explicit checks in this method.

## State Changes:
Attributes READ:
    - None. This method does not read or depend on instance attributes (it is a pure/static operation).
Attributes WRITTEN:
    - None. The method returns a new dictionary and does not modify inputs or object state.

## Constraints:
Preconditions:
    - The caller should pass a sequence of iterable token containers (each allowing iteration and membership testing).
    - Tokens should be hashable strings; normalization/stemming and stop-word removal should be performed by the caller before calling.

Postconditions:
    - The returned dictionary contains one entry per distinct term present in the provided sentences.
    - For every returned term, the value equals math.log(N / (1 + n_j)) where N == len(sentences) and n_j is the count of sentences that contain that term.
    - No inputs or external state are mutated.

## Side Effects:
    - None. No I/O, no external calls, and no mutation of input sentences or object attributes.

## Implementation notes / behavior details:
    - The function iterates terms in each sentence and computes idf only the first time a term is encountered (it checks idf_metrics membership to avoid recomputation).
    - n_j is computed by scanning all sentences and performing membership tests (term in s), so the count is the number of sentences that contain the term (not total occurrences).
    - The denominator uses (1 + n_j). In normal use where terms are collected from sentences, n_j will be at least 1; the +1 prevents division-by-zero if the formula were applied to a term with n_j == 0 in a different context.
    - Time complexity: potentially O(U * S) where U is the number of unique terms processed and S is the number of sentences (each unique term triggers a scan of all sentences to compute n_j).

### `sumy.summarizers.lex_rank.LexRankSummarizer._create_matrix` · *method*

## Summary:
Constructs and returns a row-normalized adjacency matrix representing sentence-to-sentence links based on pairwise cosine similarities, thresholding similarities into binary edges and converting each non-empty row into a probability distribution. The method does not modify instance attributes.

## Description:
This method builds an N x N numpy matrix (N = len(sentences)) used by the LexRank algorithm:
- For every ordered pair (i, j) it computes sim = self.cosine_similarity(sentence_i, sentence_j, tf_i, tf_j, idf_metrics).
- If sim > threshold the entry is set to 1.0 (an edge); otherwise it is set to 0.
- It counts the number of outgoing edges for each row (degree). After filling the matrix, each row is divided by its degree so that rows with at least one edge become row-stochastic (their elements sum to 1.0). Rows with zero outgoing edges are treated with degree = 1 to avoid division by zero; since these rows contain only zeros, they remain all zeros after normalization (sum == 0).
- The resulting matrix entries are therefore either 0.0 or 1.0/degree(row) for rows with edges.

Known callers and lifecycle context:
- Called during the LexRank summarization pipeline when constructing the sentence similarity graph prior to ranking (e.g., before running a PageRank-style iterative ranking).
- It is separated into its own method to encapsulate matrix construction (similarity computation, thresholding, degree counting, normalization) for clarity, reuse, and unit testing.

Performance characteristics:
- Time complexity: O(N^2 * cost_of_cosine_similarity).
- Space complexity: O(N^2) for the returned matrix.

## Args:
    sentences (Sequence): Sequence (e.g., list) of sentence objects used by self.cosine_similarity. Length N.
    threshold (float): Numeric threshold. A similarity strictly greater than this value is considered an edge.
    tf_metrics (Sequence): Sequence of term-frequency metrics (one per sentence) passed to self.cosine_similarity. Should align with `sentences` in ordering and length for expected behavior.
    idf_metrics (Mapping): Inverse-document-frequency metrics (e.g., dict token -> float) passed to self.cosine_similarity; treated read-only by this method.

## Returns:
    numpy.ndarray:
    - 2D float array with shape (N, N), dtype float (typically numpy.float64).
    - Possible values: 0.0 or 1.0/degree for rows with at least one edge, where degree is the number of entries that were > threshold for that row.
    - For rows with at least one edge, the row sums to 1.0 after normalization.
    - For rows with zero edges, the row remains all zeros (sum == 0).
    - If N == 0, returns an empty array with shape (0, 0).

## Raises:
    - The method does not explicitly raise exceptions. However:
        - If inputs are of incompatible types/shapes, self.cosine_similarity or numpy operations may raise TypeError or ValueError.
        - There is no division-by-zero exception in this implementation because rows with zero degree are set to degree = 1 before division.

## State Changes:
    Attributes READ:
        - Calls the instance method self.cosine_similarity (for each pair); reads no other instance attributes.
    Attributes WRITTEN:
        - None. The method does not assign or mutate any self.<attr> fields.

## Constraints:
    Preconditions:
        - sentences must be a sequence (len() defined); N = len(sentences).
        - tf_metrics should ideally have the same length as sentences. The method uses zip(sentences, tf_metrics) for iteration; if tf_metrics is shorter than sentences, iteration will be truncated to the shorter length and the remaining rows/columns in the returned matrix will remain zeros.
        - Each tf_metrics element and idf_metrics must be acceptable inputs to self.cosine_similarity.
        - threshold must be a numeric value (float-like).

    Postconditions:
        - The returned array has shape (N, N).
        - Entries are in [0.0, 1.0].
        - Any row with one or more similarities > threshold will sum to 1.0 after normalization.
        - Any row with zero similarities > threshold will be all zeros (sum == 0).

## Side Effects:
    - No I/O, no network calls.
    - Only side-effect is calling self.cosine_similarity; if that method has side effects, they will occur but are not caused by this method itself.
    - The method mutates and returns local numpy arrays; it does not mutate the input sequences or the instance state.

### `sumy.summarizers.lex_rank.LexRankSummarizer.cosine_similarity` · *method*

## Summary:
Computes the cosine similarity between two sentences using tf-idf weighted vectors and returns a normalized similarity score in [0.0, 1.0]; does not modify object state.

## Description:
This function calculates the cosine similarity between two sentence token sets by treating each sentence as a vector of term weights computed as tf * idf and returning the cosine of the angle between them. It is used when building the sentence-to-sentence similarity matrix during LexRank's matrix creation step.

Known callers and lifecycle stage:
- LexRankSummarizer._create_matrix: invoked for every ordered pair (row, col) of sentences while constructing the adjacency/transition matrix for the PageRank-like scoring. This occurs during the summarizer's __call__ pipeline after term-frequency (tf) and inverse-document-frequency (idf) metrics are computed.

Why this logic is a separate method:
- Encapsulates the tf-idf weighted cosine calculation so it can be reused and tested independently of matrix construction.
- Keeps _create_matrix focused on graph construction, thresholding and normalization, while this method isolates the numeric similarity computation.

## Args:
    sentence1 (iterable[str]):
        Sequence (typically a list) of normalized, stemmed token strings representing the first sentence.
        Each token must be hashable (strings are expected).
    sentence2 (iterable[str]):
        Sequence (typically a list) of normalized, stemmed token strings representing the second sentence.
    tf1 (Mapping[str, float]):
        Term-frequency metrics for sentence1. Expected to contain an entry for every term in sentence1.
        Values are normalized tf scores (floats), typically in range (0.0, 1.0].
    tf2 (Mapping[str, float]):
        Term-frequency metrics for sentence2. Expected to contain an entry for every term in sentence2.
        Values are normalized tf scores (floats).
    idf_metrics (Mapping[str, float]):
        Inverse-document-frequency metric for terms across the document. Expected to contain an entry for every term present in sentences.
        Values are floats; they may be negative, zero or positive (based on log formulation), but this implementation uses squared idf values.

## Returns:
    float:
        A similarity score between 0.0 and 1.0 inclusive.
        - If both denominator terms are > 0: returns numerator / (sqrt(denominator1) * sqrt(denominator2)).
        - If either denominator is 0 (e.g., one or both sentences empty or their weighted-norm is zero): returns 0.0.

## Raises:
    KeyError:
        If a term present in sentence1 or sentence2 is not present in the corresponding tf mapping (tf1 or tf2) or not present in idf_metrics.
        This happens because the implementation indexes tf1[term], tf2[term], and idf_metrics[term] for terms derived from the sentence sequences.
    TypeError:
        If sentence1 or sentence2 are not iterable of hashable elements (frozenset construction or membership operations may raise TypeError), or if tf/idf mappings do not support indexing.

## State Changes:
    Attributes READ:
        None (method is static and does not read any self.<attr> fields)
    Attributes WRITTEN:
        None (method does not modify the instance)

## Constraints:
    Preconditions:
        - sentence1 and sentence2 should be iterables of tokens (strings) that correspond to the keys of tf1 and tf2 respectively.
        - tf1, tf2, and idf_metrics must provide numeric values (floats) for all terms present in the sentences.
        - Tokens must be hashable (strings are expected).
    Postconditions:
        - The returned float is always between 0.0 and 1.0 inclusive.
        - No external state or input mapping is modified by the call.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside the scope of local temporaries; input mappings and sentence iterables are not modified.

## Complexity:
    Time complexity per call is approximately O(U1 + U2), where U1 and U2 are the number of unique tokens in sentence1 and sentence2 respectively (dominated by set construction and summations over unique tokens). Memory usage is minimal and proportional to the size of the frozensets created for the two sentences.

### `sumy.summarizers.lex_rank.LexRankSummarizer.power_method` · *method*

## Summary:
Computes the stationary score vector for sentences by iteratively applying the transposed transition matrix until the L2 change between iterations falls below the given tolerance; does not modify object attributes.

## Description:
Known callers and lifecycle:
- Called from LexRankSummarizer.__call__ during summarization after the similarity/transition matrix is built (matrix created by _create_matrix). It is invoked to convert the sentence-to-sentence transition matrix into a score/ranking vector used to rate sentences.
- Typical invocation: scores = self.power_method(matrix, self.epsilon)

Purpose / rationale:
- Encapsulates the power-iteration logic used to find the principal eigenvector (stationary distribution) of the transition operator. Keeping this as a separate static method improves readability, testability, and reuse of the iterative convergence logic rather than inlining it inside the summarizer pipeline.

## Args:
    matrix (numpy.ndarray):
        A 2-dimensional square NumPy array-like transition matrix with shape (n, n), where n is the number of sentences.
        - Expected semantics: rows correspond to source sentences and are normalized so row sums equal 1 (row-stochastic matrix produced by _create_matrix).
        - Must be non-empty (n > 0).
    epsilon (float):
        Convergence tolerance. Iteration continues while the L2 norm of the difference between successive vectors is strictly greater than epsilon.
        - Expected: epsilon > 0 for reliable termination within a finite number of steps in practice.
        - Typical values: small positive floats (e.g., class default 0.1).

## Returns:
    numpy.ndarray:
        A 1-dimensional NumPy array of length n containing the converged score (stationary) vector.
        - The returned vector preserves the L1 sum of the initial vector (initial vector is uniform and sums to 1) when the input matrix has appropriate stochastic properties; in the LexRank pipeline this yields a probability-like distribution over sentences used as scores.
        - Values are non-negative when the input matrix has non-negative entries (as produced by _create_matrix).

## Raises:
    ZeroDivisionError:
        If matrix has zero rows (len(matrix) == 0), the initial uniform vector computation 1.0 / sentences_count triggers a division-by-zero.
    ValueError:
        May be raised by NumPy operations (e.g., numpy.dot or numpy.linalg.norm) if the provided matrix has incompatible shape or otherwise invalid contents.
    TypeError / AttributeError:
        May be raised if the provided matrix does not support required NumPy array operations or attributes (e.g., no .T), indicating an incorrect argument type.

## State Changes:
Attributes READ:
    - None (static method; does not access or read any self.<attr> attributes)
Attributes WRITTEN:
    - None (does not modify object attributes)

## Constraints:
Preconditions:
    - matrix must be a 2-D array-like with shape (n, n) and n >= 1.
    - epsilon should be a non-negative float; strictly positive epsilon is recommended to ensure timely termination.
    - For meaningful probabilistic scores, matrix entries should be non-negative and rows should be normalized to sum to 1 (this is guaranteed when using the summarizer's _create_matrix).

Postconditions:
    - Returns a numpy.ndarray p_vector such that successive application of transpose(matrix) to the initial uniform vector has converged in L2-norm to within epsilon.
    - If matrix is produced by _create_matrix (row-stochastic), the returned vector will preserve the sum-to-one property of the initial vector and can be treated as relative sentence scores.

## Side Effects:
    - No I/O, logging, or external service calls.
    - No mutation of objects outside the local scope; only local variables (transposed_matrix, p_vector, next_p, lambda_val) are used.
    - Potential heavy CPU usage for large n: each iteration performs a matrix-vector multiplication O(n^2), and the number of iterations depends on the matrix spectral gap and chosen epsilon.

