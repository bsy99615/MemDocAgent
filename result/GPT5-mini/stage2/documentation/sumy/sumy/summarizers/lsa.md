# `lsa.py`

## `sumy.summarizers.lsa.LsaSummarizer` · *class*

*No documentation generated.*

### `sumy.summarizers.lsa.LsaSummarizer.stop_words` · *method*

## Summary:
Configure the summarizer's stop-word set by normalizing each provided token and storing the resulting immutable set on the instance.

## Description:
This property setter is invoked when client code assigns an iterable of stop words to the summarizer (for example: summarizer.stop_words = ['the', 'and']). Typical callers are configuration or pipeline code that prepares an LsaSummarizer instance before invoking it to produce a summary; it should be called during the setup phase (before __call__ is executed) so downstream methods such as _create_dictionary will exclude the configured stop words.

This logic is implemented as a setter to:
- Ensure consistent preprocessing by applying the instance's normalize_word to every supplied token.
- Store the stop words as an immutable frozenset for safe, efficient membership testing during summarization.
- Keep configuration separate from runtime logic (no inlining inside _create_dictionary), enabling reuse and clearer intent.

## Args:
    words (iterable): Iterable of tokens acceptable to self.normalize_word (commonly str or bytes). Each item will be passed to self.normalize_word and the normalized results are collected. There is no default; the setter requires one argument.

## Returns:
    None: As a property setter it does not return a value. The observable effect is that self._stop_words is replaced.

## Raises:
    TypeError: If words is not iterable (e.g., None or an object that does not support iteration), attempting to map over it will raise TypeError.
    Exception propagated from self.normalize_word: Any exception raised while normalizing an item (for example text conversion or lowercasing errors) will propagate unchanged.
    TypeError: If any normalized item is unhashable, frozenset(...) construction will raise TypeError. (normalize_word in AbstractSummarizer normally returns text which is hashable.)

## State Changes:
    Attributes READ:
        - self.normalize_word (method): called for each item in the provided iterable to produce the canonical token used in the stop-word set.
    Attributes WRITTEN:
        - self._stop_words: replaced on the instance with a frozenset of normalized tokens (shadows any class-level default).

## Constraints:
    Preconditions:
        - The instance must implement a working normalize_word method (AbstractSummarizer provides this).
        - The provided words iterable must yield items valid for normalize_word.
    Postconditions:
        - self._stop_words is an immutable frozenset containing the normalized tokens.
        - Duplicate tokens (after normalization) are removed.
        - Subsequent summarization steps that check membership against self._stop_words (e.g., _create_dictionary) will exclude these normalized tokens.

## Side Effects:
    - Mutates only the summarizer instance by assigning to self._stop_words.
    - No I/O, no network calls, and no mutation of the input iterable by this setter.

## Notes and example:
    - This setter stores the stop words as an instance attribute; it does not modify any other objects.
    - It intentionally normalizes tokens here so downstream code can compare stems/normalized forms consistently (performance benefit from frozenset membership checks).
    - Example usage (conceptual):
        - After constructing an LsaSummarizer, configure stop words before summarization:
          summarizer.stop_words = ['the', 'and', 'of']
    - If you need to clear stop words, assign an empty iterable: summarizer.stop_words = [] which sets self._stop_words to frozenset().

### `sumy.summarizers.lsa.LsaSummarizer.__call__` · *method*

## Summary:
Produces an extractive summary using Latent Semantic Analysis: builds a term-by-sentence matrix from the parsed document, applies SVD, scores sentences by their projection on retained singular dimensions, and returns the top-ranked sentences as an ordered tuple. The method does not mutate the summarizer instance.

## Description:
This is the LSA pipeline entry point invoked when the summarizer instance is called with (document, sentences_count). It orchestrates the algorithmic steps and reuses helper methods implemented on the class:
1. Ensures numeric dependencies (NumPy) are available.
2. Builds a vocabulary (dictionary) of stemmed, non-stop words from document.words.
3. Constructs a numeric term-by-sentence matrix (words_count × sentences_count) with raw term counts.
4. Converts raw counts to smoothed term-frequency values in-place.
5. Calls a singular value decomposition routine to obtain factor matrices (u, sigma, v_matrix).
6. Computes a numeric rank for each sentence using sigma and v_matrix.
7. Uses the inherited selection helper to pick the best sentences by passing a rating callable that yields ranks in sentence order.

Known callers / pipeline stage:
- Called by external code or pipeline components that perform summarization by invoking the summarizer instance: summarizer(document, sentences_count).
- Typical usage: after parsing raw text into a Document object with .words and .sentences populated.

Why a dedicated method:
- The sequence of SVD-based operations and the dependency checks form a cohesive algorithm that benefits from being encapsulated in a single __call__ override that leverages smaller helper methods for clarity and reuse.

## Args:
    document (object): Parsed document with required attributes:
        - .words: iterable of token strings (used to build the dictionary).
        - .sentences: ordered iterable (list-like) of sentence objects; each sentence object must expose .words (an iterable of tokens).
      Note: document.sentences is consumed when selecting sentences; if it is a generator it will be exhausted.
    sentences_count (int | str | callable | other count-policy): Selection policy forwarded to AbstractSummarizer._get_best_sentences.
        - Common forms: int (number of sentences), percentage string like "30%", or a callable selector; see AbstractSummarizer._get_best_sentences for precise accepted forms.

## Returns:
    tuple: Tuple of selected sentence objects (items are the same objects from document.sentences), ordered by their original position in the input.
        - Returns an empty tuple () immediately if the constructed dictionary is empty (no candidate words).
        - Otherwise returns between 0 and len(document.sentences) sentences depending on sentences_count and selection policy.

## Raises:
    ValueError:
        - If NumPy is not available: raised by _ensure_dependecies_installed().
          Exact message: "LSA summarizer requires NumPy. Please, install it by command 'pip install numpy'."
    AssertionError:
        - May be raised by _compute_ranks if sigma length does not match v_matrix.shape[0]. The helper raises AssertionError with message "Matrices should be multiplicable".
    Any exception propagated from helpers or NumPy:
        - Exceptions from normalize_word or the configured stemmer used in _create_dictionary (e.g., TypeError or encoding errors) propagate.
        - Exceptions raised by the singular value decomposition routine (e.g., numpy.linalg.LinAlgError or TypeError) propagate.
        - Any exception raised by _get_best_sentences (e.g., KeyError if rating mapping is used incorrectly, or errors from the count policy) will propagate.
    Note: This method does not catch or wrap exceptions from called helpers — they propagate to the caller.

## State Changes:
Attributes READ:
    - self._stop_words: checked by _create_dictionary to exclude stop words.
    - self._stemmer (via stem_word): used to compute stems when building the dictionary.
Attributes WRITTEN:
    - None. The method assigns to local variables only; it does not modify instance attributes.

## Constraints:
Preconditions:
    - NumPy must be importable (checked by _ensure_dependecies_installed()).
    - document must implement .words and .sentences; each sentence must implement .words.
    - The singular_value_decomposition callable used in the module must return a triple (u, sigma, v_matrix) compatible with the following expectations:
        - sigma is a 1-D sequence/array of singular values (length k).
        - v_matrix is a 2-D array with shape (k, sentences_count) so that v_matrix.T yields a column vector per sentence.
      If these shape contracts are violated, _compute_ranks will assert and an AssertionError or other error will be raised.
    - sentences_count must be acceptable to AbstractSummarizer._get_best_sentences.
Postconditions:
    - The summarizer instance remains unchanged (no instance attributes modified).
    - The returned tuple contains the chosen sentence objects in original document order.
    - If the vocabulary was too small relative to sentences, a warning may have been issued (see Side Effects).

## Side Effects:
    - May emit a warning via warnings.warn in _create_matrix when words_count < sentences_count. Exact warning text:
      "Number of words (%d) is lower than number of sentences (%d). LSA algorithm may not work properly."
    - Consumes document.sentences (if it is a generator it will be exhausted).
    - Allocates numeric arrays and performs an SVD; this can be memory- and CPU-intensive.
    - The numeric matrix returned by _create_matrix is mutated in-place by _compute_term_frequency (but this matrix is a local variable and not stored on self).
    - No file I/O, network calls, or persistent external state changes are performed by this method.

## Edge cases and important behavior notes:
    - Empty dictionary: If all tokens are stop words or no tokens are found, _create_dictionary returns an empty mapping and the method returns () without performing matrix construction, TF smoothing, or SVD.
    - Vocabulary smaller than sentence count: A warning is emitted but processing continues.
    - SVD contract: The method calls singular_value_decomposition(matrix, full_matrices=False). The implementation of singular_value_decomposition is expected to be compatible with NumPy's svd outputs or otherwise provide (u, sigma, v_matrix) satisfying the shape conditions above. Mismatch will cause assertion or shape-related errors in subsequent steps.
    - Rank ordering dependency: The method obtains ranks as an iterator (ranks = iter(self._compute_ranks(sigma, v))) and supplies a rating callable lambda s: next(ranks) to _get_best_sentences. This relies on _get_best_sentences enumerating sentences in the same order as document.sentences and invoking the rating callable exactly once per sentence in that order. If a different enumeration order or multiple calls per sentence occur, rank-sentence alignment will break.
    - Numerical stability: SVD on large or ill-conditioned matrices may raise numerical errors; such exceptions pass through to the caller.

## Implementation-level hints (to reimplement this method):
    - Use helper methods on the class: _ensure_dependecies_installed, _create_dictionary, _create_matrix, _compute_term_frequency, _compute_ranks, _get_best_sentences.
    - Expect dictionary to be a dict mapping stem -> integer index (0..words_count-1).
    - The matrix is a 2-D numeric array with shape (words_count, sentences_count); ensure consistent ordering of columns with document.sentences.
    - singular_value_decomposition must return (u, sigma, v_matrix) where v_matrix has one row per retained singular value and one column per sentence; compute_ranks expects this shape.
    - Pass a rating callable to _get_best_sentences that yields ranks sequentially in the same order as sentences are enumerated.

### `sumy.summarizers.lsa.LsaSummarizer._ensure_dependecies_installed` · *method*

## Summary:
Checks that the optional external dependency NumPy is available and raises a clear error if it is not; it does not modify the summarizer's state when NumPy is present.

## Description:
This private helper is invoked at the start of the summarization pipeline to ensure required runtime dependencies are present before performing numeric operations (SVD, matrix creation, etc.).

Known callers:
- LsaSummarizer.__call__ — called at the start of the summarization operation before any matrix or SVD work is performed.

Rationale for a separate method:
- Centralizes the dependency check in one place so the check can be easily reused or extended (for example, adding other optional dependencies or more detailed diagnostics) without cluttering the main summarization flow.
- Keeps __call__ focused on the summarization pipeline logic rather than environment validation.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError:
        - Raised exactly when the module-level name 'numpy' is None (i.e., NumPy is not importable in the runtime).
        - Exact message: "LSA summarizer requires NumPy. Please, install it by command 'pip install numpy'."

## State Changes:
    Attributes READ:
        - None of the instance attributes are read by this method.
        - It does rely on the module-level symbol 'numpy' imported in the module scope.

    Attributes WRITTEN:
        - None. The method does not modify any attributes of self or module-level state.

## Constraints:
    Preconditions:
        - No precondition on self or its attributes is required.
        - The module-level import for NumPy exists; the method checks whether that import succeeded (numpy is not None).

    Postconditions:
        - On normal return, NumPy is available (the module-level 'numpy' is not None).
        - If NumPy is unavailable, a ValueError is raised and the summarization operation should not proceed.

## Side Effects:
    - No I/O, network, or filesystem activity.
    - No mutation of external objects.
    - The only observable effect is raising an exception when NumPy is missing, which prevents further summarizer operations that depend on NumPy.

### `sumy.summarizers.lsa.LsaSummarizer._create_dictionary` · *method*

## Summary:
Constructs and returns a vocabulary dictionary that maps each unique, non-stop, stemmed token from the provided document to a sequential integer index (0-based). The method reads instance helpers and stop-word state but does not modify the summarizer instance.

## Description:
- Known callers and context:
    - Called during the LSA summarization preprocessing step when converting a document's token stream into a vocabulary used to build the term-by-sentence or term-by-document matrix prior to singular value decomposition.
    - Typically invoked once per input document (or per corpus unit) while preparing data for matrix construction and decomposition.
- Why this logic is its own method:
    - Vocabulary extraction (normalization, stemming, stop-word filtering, and index assignment) is a focused preprocessing task reused by matrix-building code. Encapsulating it improves modularity, testability, and clarity of the LSA pipeline.

## Args:
    document (object): Required. An object exposing an iterable of token values via the attribute `words` (i.e., `document.words`). Each token is expected to be a string or a type accepted by self.normalize_word and self.stem_word.

## Returns:
    dict[str, int]: Mapping from stemmed token (string) to a unique integer index.
    - Indices are assigned sequentially in the order tokens are first encountered (first-seen order), starting at 0.
    - If no tokens survive normalization/stemming/stop-word filtering, an empty dictionary is returned.

## Raises:
    AttributeError:
        - If `document` does not have a `words` attribute.
        - If the summarizer instance does not have `self._stop_words` defined.
    Any exception raised by self.normalize_word or self.stem_word (for example, TypeError for unsupported token types) will propagate to the caller.
    (The method itself does not raise custom exceptions.)

## State Changes:
- Attributes READ:
    - self._stop_words: consulted for membership tests to exclude stop words.
    - self.normalize_word(word): invoked to normalize each token.
    - self.stem_word(normalized_word): invoked to stem each normalized token.
- Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
- Preconditions:
    - `document.words` must be an iterable of tokens. Each token should be acceptable input to self.normalize_word.
    - self._stop_words must be defined on the instance and be a container supporting membership tests (e.g., set, frozenset, or list). For best performance use a set-like container to achieve O(1) membership checks.
    - Methods self.normalize_word and self.stem_word must be callable and should return strings (the implementation assumes that stemmed outputs are hashable strings usable as dict keys).
- Postconditions:
    - Returned dictionary includes only tokens that:
        1) appeared in `document.words`,
        2) after normalization and stemming are not present in self._stop_words,
        3) are unique (duplicates removed),
        4) are mapped to contiguous integer indices starting at 0 in the order they were first seen.

## Side Effects:
- No file I/O, network calls, or changes to global state are performed.
- The method calls self.normalize_word and self.stem_word; any side effects from those methods (if present) will occur but are not introduced here.

## Examples (illustrative, plain description):
- If document.words is ["The", "cat", "sat", "on", "the", "mat"] and stop words include "the" and "on", and normalization/stemming lowercases and stems to base forms, a possible returned dictionary is {"cat": 0, "sat": 1, "mat": 2}.
- If document.words is empty or all tokens are stop words after normalization/stemming, the method returns an empty dict.

## Determinism and ordering:
- The mapping is deterministic with respect to the order of tokens in document.words and the deterministic behavior of normalize_word and stem_word. Different ordering of input tokens will produce different index assignments, though the set of keys will be the same if the same unique tokens appear.

### `sumy.summarizers.lsa.LsaSummarizer._create_matrix` · *method*

## Summary:
Builds and returns a term-by-sentence numeric matrix (vocabulary × sentences) where each cell contains the raw occurrence count of a stemmed word in a specific sentence. The produced matrix reflects the ordering of document.sentences and uses dictionary indices to map stems to rows.

## Description:
Known callers and lifecycle stage:
- Called by LsaSummarizer.__call__ as part of the LSA pipeline. In that pipeline, the method is invoked after a vocabulary (dictionary) has been produced and before term-frequency smoothing and SVD are applied.
- Typical usage: the summarizer builds the dictionary from document.words, then invokes this method to produce the initial numeric representation of the document suitable for numeric linear-algebra operations.

Why this is a separate method:
- Matrix construction is a distinct, testable step of the LSA algorithm: it converts corpus tokens into a dense numeric representation. Keeping it separate improves readability, allows independent testing, and isolates data-shaping details from higher-level algorithm steps (TF smoothing, SVD, ranking).

## Args:
    document (object): Parsed document object with these required attributes:
        - .sentences: an ordered iterable (e.g., list) of sentence objects. The order defines the columns of the returned matrix.
          Each sentence object must expose .words: an iterable of token strings (raw or normalized).
        - .words is not used by this method but is typically present when this method is called by the pipeline.
    dictionary (dict[str,int]): Mapping from stemmed-word string -> row index (0-based). Keys are expected to be stems produced by self.stem_word (or otherwise compatible with it). Values must be integers in the range [0, len(dictionary)-1]; they define the row positions in the matrix.

## Returns:
    numpy.ndarray:
        - 2-D array with shape (words_count, sentences_count) where:
            words_count == len(dictionary)
            sentences_count == len(document.sentences)
        - dtype: float (NumPy default float64 when created with numpy.zeros).
        - Semantics: matrix[row, col] contains the number of occurrences (as a numeric value) of the stem corresponding to row in the sentence at column col.
        - Edge-case returns:
            * If words_count == 0, returns an array with shape (0, sentences_count).
            * If sentences_count == 0, returns an array with shape (words_count, 0).

## Raises:
    AttributeError:
        - If document has no .sentences attribute or if any sentence object lacks .words, iteration will raise AttributeError when accessing these attributes.
    IndexError:
        - If dictionary contains an index value outside the range [0, words_count-1], assignment matrix[row, col] += 1 will raise IndexError.
    TypeError / ValueError:
        - If dictionary is not sized or its values are not integers, numpy.zeros((words_count, sentences_count)) or indexing may raise TypeError or ValueError.
    Any exception raised by self.stem_word:
        - If the stemmer raises (e.g., due to unexpected token types), that exception propagates.
    Note: The method itself does not explicitly catch exceptions; errors from NumPy or from attribute access propagate to the caller.

## State Changes:
Attributes READ:
    - self.stem_word (method): invoked to compute stems for tokens. The method object is read from the instance.
Attributes WRITTEN:
    - None. The method mutates only local variables and the returned NumPy array; it does not modify instance attributes.

## Constraints:
Preconditions:
    - The caller must provide:
        * A document with an ordered iterable .sentences attribute where each sentence has an iterable .words.
        * A dictionary mapping stems (strings) to contiguous integer row indices (0..words_count-1).
    - The dictionary keys must be compatible with the output of self.stem_word called on tokens from sentence.words, otherwise matches will not occur.
    - NumPy must be available (numpy imported). In typical usage this is enforced earlier by _ensure_dependecies_installed().
Postconditions:
    - The returned matrix is fully populated with raw occurrence counts for stems that appear both in sentences and in the given dictionary.
    - The order of columns corresponds exactly to the order of document.sentences enumeration performed inside the method.
    - No attributes on self are modified.

## Side Effects:
    - Emits a warning via warnings.warn if len(dictionary) < len(document.sentences). The warning message is:
      "Number of words (%d) is lower than number of sentences (%d). LSA algorithm may not work properly."
    - Allocates a NumPy array of shape (words_count, sentences_count) and increments its elements; this uses memory proportional to words_count × sentences_count.
    - Iterates over all tokens in each sentence; if sentence.words or dictionary are generators or have side effects, those side effects will occur during iteration.
    - No file I/O, network calls, or persistent external state modifications are performed.

## Implementation details sufficient for reimplementation:
- Compute words_count = len(dictionary) and sentences_count = len(document.sentences).
- If words_count < sentences_count, call warnings.warn with the exact message shown above (substitute integers).
- Create a NumPy array initialized to zeros with shape (words_count, sentences_count) (use numpy.zeros).
- For each sentence in document.sentences, enumerate columns with increasing integer index col starting at 0.
- For each token in sentence.words, compute stem = self.stem_word(token) (use the same stemming logic as used to build dictionary).
- If stem is present in dictionary, use row = dictionary[stem] and increment matrix[row, col] by 1 (matrix[row, col] += 1).
- After processing all sentences, return the matrix (do not modify self or other objects).
- Ensure column iteration order exactly matches the order in which document.sentences is enumerated so downstream ranking aligns columns with sentences.

### `sumy.summarizers.lsa.LsaSummarizer._compute_term_frequency` · *method*

## Summary:
Normalizes term frequencies column-wise in the provided 2-D numeric matrix using max-frequency normalization with additive smoothing, mutating the matrix in-place and returning the same array.

## Description:
This method converts raw term counts (or other positive weights) in each column into normalized term frequencies by dividing each entry by the maximum value found in that column and then applying additive smoothing:
    normalized = smooth + (1.0 - smooth) * (value / max_in_column)

Known callers / pipeline context:
    - Invoked from the LSA summarization preprocessing step when building or preparing the term-by-sentence (or term-by-document) matrix prior to singular value decomposition (SVD).
    - It is part of the feature-normalization stage in the LsaSummarizer pipeline: after constructing a numeric matrix that maps terms to sentences/documents, this method produces scaled frequencies that reduce the influence of very frequent terms and stabilize later SVD computations.

Why this is a separate method:
    - The normalization is a distinct, reusable transformation applied to the numeric matrix that is conceptually separate from matrix construction and the SVD step. Encapsulating it in its own method improves readability, allows reuse in tests or alternative pipelines, and keeps numerical/normalization logic isolated for easier maintenance.

## Args:
    matrix (numpy.ndarray): A 2-D numeric array with shape (rows, cols).
        - Interpretation: rows typically index documents/sentences, cols index terms/features.
        - Requirement: array-like supporting numpy.max(matrix, axis=0), indexing, and assignment (i.e., a numpy.ndarray or compatible object). Best used with a floating-point dtype to preserve fractional values.
    smooth (float, optional): Additive smoothing constant in the interval [0.0, 1.0).
        - Default: 0.4
        - Allowed range: 0.0 <= smooth < 1.0
        - Effect: when smooth > 0, the output values are bounded away from 0; smooth controls how strongly the raw normalized frequency is blended toward 1.0.

## Returns:
    numpy.ndarray:
        - The same matrix object passed in (mutated in-place).
        - Each entry matrix[i, j] is replaced by:
            smooth + (1.0 - smooth) * (matrix[i, j] / max_column_j)
          when max_column_j != 0.
        - Columns whose maximum is zero are left unchanged (all entries remain zero).
        - Possible return edge values:
            * If smooth == 0.0: pure max-normalized values in [0.0, 1.0] (assuming non-negative inputs).
            * As smooth approaches 1.0: output values approach 1.0.
            * If columns contain NaN or Inf, numpy semantics apply and NaN/Inf may propagate into results.

## Raises:
    AssertionError:
        - Raised immediately if smooth is outside the allowed interval (0.0 <= smooth < 1.0), due to the assert at the start of the method.
    Other exceptions:
        - The implementation assumes matrix provides .shape, supports numpy.max(..., axis=0), and allows numeric indexing and assignment. If a non-conforming object is passed, numpy or Python will raise appropriate exceptions (e.g., AttributeError, IndexError, TypeError) — these are not explicitly raised by this method.

## State Changes:
    Attributes READ:
        - None of self.* attributes are read by this method (it does not access the instance state).
    Attributes WRITTEN:
        - None of self.* attributes are modified by this method.
    Mutations to arguments / external objects:
        - The provided matrix argument is mutated in-place: many of its entries are overwritten with smoothed, normalized floating-point values. The returned object is the same reference as the input.

## Constraints:
    Preconditions:
        - matrix must be two-dimensional (matrix.ndim == 2). The code assumes matrix.shape returns (rows, cols).
        - Columns represent features/terms whose per-column maximum is meaningful for normalization.
        - Prefer passing a floating dtype array (e.g., float32 or float64). If an integer-typed numpy array is passed, assignments of float results will be cast back to integers (truncation/rounding), which will distort normalization.
        - smooth must satisfy 0.0 <= smooth < 1.0 (enforced by assertion).
    Postconditions:
        - After the call, for every column j with max_column_j != 0, all entries matrix[i, j] lie in the interval [smooth, smooth + (1.0 - smooth) * 1.0] = [smooth, 1.0].
        - Columns with max_column_j == 0 remain unchanged (typically all zeros).
        - The returned object is the same numpy.ndarray reference supplied as matrix.

## Side Effects:
    - No I/O or external service calls are performed.
    - The only observable side effect is the in-place mutation of the provided matrix argument.
    - Computational complexity is O(rows * cols) in time and O(cols) extra space for storing the per-column maxima.

### `sumy.summarizers.lsa.LsaSummarizer._compute_ranks` · *method*

## Summary:
Compute a numeric relevance score for each column of the provided V matrix using the supplied singular values and a dimensionality reduction policy; does not modify the object's state.

## Description:
Called during the summarization pipeline immediately after singular value decomposition (SVD) completes. In LsaSummarizer.__call__, the SVD of the term-by-sentence matrix produces sigma and v (the V matrix); this method consumes those to compute per-sentence ranks which are later consumed by _get_best_sentences to select top sentences. It is separated into its own method to encapsulate the ranking formula (powering singular values, applying dimensionality reduction, and aggregating contributions across components), making the logic easier to test and reuse independent of SVD or sentence-selection code.

Known callers and context:
- LsaSummarizer.__call__: after computing u, sigma, v from the matrix SVD, it invokes this method to obtain the iterable of per-sentence scores used to pick summary sentences.

Why separate:
- Keeps SVD and ranking concerns decoupled.
- Enables unit testing of ranking behavior (reduction, weighting, and numeric stability) without recomputing SVD.
- Makes dimensionality reduction parameters (MIN_DIMENSIONS, REDUCTION_RATIO) clearly centralized.

## Args:
    sigma (Sequence[float]):
        Sequence (e.g., tuple/list/ndarray) of singular values returned by SVD. Expected length N.
        Values are expected to be numeric (typically non-negative) and ordered in descending magnitude as produced by numpy.linalg.svd.
    v_matrix (numpy.ndarray):
        2D numeric matrix with shape (N, M) where N == len(sigma) and M is the number of sentence vectors.
        The method iterates over v_matrix.T (columns of V) to compute one rank per column.

## Returns:
    list[float]:
        A list of length M (number of columns of v_matrix) with a non-negative float rank for each column.
        Each value equals sqrt(sum_{i=0..N-1} powered_sigma[i] * (v_ij)^2) where powered_sigma[i] is s_i**2 for i in the retained dimensionality, otherwise 0.0.
        Edge cases:
        - If all retained powered_sigma entries are zero, returned ranks will be zeros.
        - If v_matrix has zero columns (M == 0), an empty list is returned.

## Raises:
    AssertionError:
        Raised with message "Matrices should be multiplicable" when len(sigma) != v_matrix.shape[0].
    Other runtime errors:
        Will propagate exceptions if v_matrix does not provide .shape or .T attributes, or if elements are non-numeric (TypeError/ValueError during numeric ops).

## State Changes:
    Attributes READ:
        - LsaSummarizer.MIN_DIMENSIONS (class attribute): used to determine minimum retained dimensions.
        - LsaSummarizer.REDUCTION_RATIO (class attribute): used to compute retained dimensionality fraction.
      Note: the method does not read or modify any instance attributes (no self.<attr> is changed).
    Attributes WRITTEN:
        - None. The method is pure with respect to the LsaSummarizer instance.

## Constraints:
    Preconditions:
        - len(sigma) must equal v_matrix.shape[0].
        - sigma must be an iterable of numeric values (singular values).
        - v_matrix must be a 2D numeric array-like object supporting .shape and .T iteration.
        - The class constants MIN_DIMENSIONS and REDUCTION_RATIO should be meaningful numeric values (MIN_DIMENSIONS >= 0, 0.0 <= REDUCTION_RATIO).
    Postconditions:
        - Returns a list of non-negative floats with length equal to the number of columns in v_matrix.
        - The returned ranks reflect only the top `dimensions` singular components (as determined by MIN_DIMENSIONS and REDUCTION_RATIO); components beyond that contribute 0.

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - Does not mutate self or the input v_matrix; however, if v_matrix is a view into mutable data and that data is concurrently modified by another thread, results may vary (no internal synchronization).
    - CPU-bound numeric computation only.

