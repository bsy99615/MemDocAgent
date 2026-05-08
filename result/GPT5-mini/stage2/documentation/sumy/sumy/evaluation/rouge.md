# `rouge.py`

## `sumy.evaluation.rouge._get_ngrams` · *function*

## Summary:
Extracts all unique n-grams from a sequence (tokens or characters) and returns them as a set of tuples.

## Description:
This helper computes every contiguous subsequence of length n from the provided sequence and stores each n-gram as an immutable tuple in a set (deduplicated). Known callers within the provided code context: none explicitly found in the retrieved snippet. Typical usage: called by ROUGE-style evaluation functions or other text-comparison utilities to obtain the set of n-grams for a sentence or token list so that overlaps (precision/recall/F-measure) between summaries and references can be computed.

Responsibility boundary: isolates the pure computation of n-grams (sequence slicing and tuple conversion) from any scoring, counting, or normalization logic; extracted to keep n-gram derivation consistent and reusable across multiple evaluation routines.

## Args:
    n (int): The n-gram size. Intended to be a positive integer (n >= 1). If n is larger than len(text), the function returns an empty set. If n == 0 the function will return a set containing a single empty tuple for non-negative-length sequences (behavior is defined by slicing semantics but not meaningful for ROUGE).
    text (Sequence): A sequence supporting len(), indexing and slicing (for example, a list/tuple of tokens, or a string for character n-grams). Each n-gram is produced from contiguous slices text[i:i+n].

Notes on interdependencies:
    - The function assumes that n and text are compatible with Python sequence semantics. No internal normalization or tokenization is performed here.

## Returns:
    set[tuple]: A set of tuples where each tuple is an n-length contiguous slice from the input sequence.
    - If 1 <= n <= len(text): returns up to (len(text) - n + 1) unique n-grams (duplicates removed by the set).
    - If n > len(text): returns an empty set.
    - If n == 0 and text is a sequence with length L >= 0: returns a set containing a single empty tuple (()).
    - The order of n-grams is not preserved (set is unordered).

## Raises:
    - TypeError: If text does not support len() or slicing (e.g., text is None or an incompatible type), or if n is not an integer type that works correctly with subtraction and range. These errors are raised implicitly by Python operations used (len(), slicing, range()).
    - No custom exceptions are raised by this function.

## Constraints:
Preconditions:
    - text must be a sequence type (supports len(), indexing and slicing).
    - n should be an integer; intended use is n >= 1 for meaningful n-grams.
Postconditions:
    - All returned tuples have length n when n >= 1 and n <= len(text).
    - The returned set contains only unique n-grams extracted from contiguous slices of text.
    - The size of the returned set <= max(0, len(text) - n + 1).

## Side Effects:
    - None. This function performs no I/O and does not mutate the input sequence or any external/global state.

## Control Flow:
flowchart TD
    Start([Start]) --> CalcLen[/"text_length = len(text)"/]
    CalcLen --> CalcMax[/"max_index_ngram_start = text_length - n"/]
    CalcMax --> CheckLoop{max_index_ngram_start >= 0?}
    CheckLoop -- Yes --> LoopStart[/"for i in range(max_index_ngram_start + 1)"/]
    LoopStart --> Slice[/"ngram = tuple(text[i:i+n])"/]
    Slice --> AddSet[/"ngram_set.add(ngram)"/]
    AddSet --> LoopStart
    CheckLoop -- No --> End([Return empty set])
    LoopStart --> End([Return ngram_set])

## Examples:
Example 1 — token n-grams (typical ROUGE use case):
    text = ["the", "cat", "sat", "on", "the", "mat"]
    n = 2
    result -> {("the", "cat"), ("cat", "sat"), ("sat", "on"), ("on", "the"), ("the", "mat")}

Example 2 — n larger than sequence:
    text = ["a", "b"]
    n = 3
    result -> set()  # empty set, no 3-grams exist

Example 3 — character n-grams (string input):
    text = "abcde"
    n = 3
    result -> {("a","b","c"),("b","c","d"),("c","d","e")}  # each character becomes an element in the tuple

Example 4 — edge-case n == 0 (defined by slicing semantics; generally avoid):
    text = ["x", "y"]
    n = 0
    result -> {()}  # single empty tuple

Usage recommendation:
    - Validate inputs before calling: ensure n is an integer >= 1 and that text is a tokenized sequence when used in ROUGE evaluation pipelines.
    - Do not rely on n == 0 behavior; treat n >= 1 as the contract for meaningful results.

## `sumy.evaluation.rouge._split_into_words` · *function*

## Summary:
Concatenate tokens from an iterable of Sentence objects into one flat list, preserving sentence and token order.

## Description:
This helper validates that each element of the provided iterable is a Sentence and then extends a result list with the tokens returned by each Sentence.words property. It centralizes the common pattern of type-checking Sentence objects and flattening their token lists for downstream evaluation or comparison tasks (for example, preparing input for n-gram based metrics like ROUGE).

Known callers in provided context:
- No explicit callers were provided in the supplied code snapshot. In this codebase the function is typically invoked by evaluation/metrics routines that need a single token sequence representing multiple Sentence objects (for instance, ROUGE or other summarization scorers).

Why this is a separate function:
- Encapsulates validation and flattening behavior to avoid duplicating the "is-instance + extend words" pattern across evaluation routines, giving a single, consistent place to control error messaging and ordering semantics.

## Args:
    sentences (iterable[Sentence]):
        - Any iterable (list, tuple, generator, etc.) whose elements are instances of sumy.models.dom.Sentence (or subclasses).
        - Each Sentence must provide a .words cached property (Sentence.words) which yields an iterable of tokens for that sentence.
        - Allowed values: any iterable. An empty iterable is valid and yields an empty list.
        - Not accepted: None or other non-iterable objects (these will cause a TypeError when the function attempts to iterate), or iterables containing non-Sentence elements (these cause a ValueError described below).

## Returns:
    list:
        - A newly allocated list containing all tokens from each Sentence in the input, appended in input order.
        - Token element types are exactly whatever Sentence.words yields (commonly strings/unicode tokens produced by the tokenizer). The function does not coerce token types.
        - Edge cases:
            - Empty input -> returns [].
            - Sentence with no tokens (Sentence.words is empty) contributes nothing to the result but processing continues.
        - The returned list is independent of Sentence instances (mutating it will not modify Sentence objects).

## Raises:
    ValueError:
        - Raised explicitly by this function when any element in the provided iterable is not an instance of Sentence.
        - Exact message: "Object in collection must be of type Sentence"
        - The exception is raised as soon as a non-Sentence element is encountered; earlier elements already processed remain unaffected.

    TypeError:
        - Not raised explicitly in the code, but the function will raise a TypeError if the supplied sentences argument is not iterable (e.g., None) because the for-loop will attempt to iterate over it.
        - Callers that might supply None or a non-iterable should guard or handle TypeError.

    Propagated exceptions from tokenizer:
        - Accessing Sentence.words delegates to the Sentence.tokenizer.to_words implementation. Any exceptions raised by the tokenizer (ValueError, RuntimeError, etc.) will propagate out of this function unchanged. The function does not catch or wrap those exceptions.

## Constraints:
    Preconditions:
        - sentences must be an iterable of Sentence objects.
        - Each Sentence must be properly constructed (valid text and tokenizer) so that accessing .words does not error.
    Postconditions:
        - Returns a list whose length equals the sum of lengths of all Sentence.words iterables for the provided sentences.
        - If the function returns normally, no element in the returned list is a Sentence instance (only token elements).

## Side Effects:
    - This function itself has no direct side effects (no I/O, no global state mutation).
    - Indirect side effects may occur if Sentence.words or the underlying tokenizer perform caching, logging, or other operations when tokenizing; those side effects are defined by the tokenizer and Sentence implementation, not by this function.

## Control Flow:
flowchart TD
    Start --> EnterLoop
    EnterLoop --> ForEachSentence
    ForEachSentence --> IsSentence{Is element an instance of Sentence?}
    IsSentence -- No --> RaiseValue[Raise ValueError: "Object in collection must be of type Sentence"]
    IsSentence -- Yes --> GetWords[Access s.words (may invoke tokenizer)]
    GetWords --> ExtendList[Extend full_text_words with tokens]
    ExtendList --> More{More sentences?}
    More -- Yes --> ForEachSentence
    More -- No --> Return[Return full_text_words]
    RaiseValue --> End
    Return --> End

## Examples:
- Typical usage:
    sentences = [Sentence("Hello world", tokenizer), Sentence("Goodbye", tokenizer)]
    result = _split_into_words(sentences)
    # result might be ['Hello', 'world', 'Goodbye'] depending on tokenizer behavior

- Handling an empty input:
    sentences = []
    result = _split_into_words(sentences)  # result == []

- Error handling when input may be invalid:
    try:
        result = _split_into_words(maybe_sentences)
    except TypeError:
        # maybe_sentences was None or not iterable
        handle_non_iterable()
    except ValueError as exc:
        # one of the items was not a Sentence
        handle_invalid_item(exc)
    except Exception:
        # propagate or log unexpected tokenizer errors
        raise

## Complexity:
    Time complexity: O(total_tokens) — iterates sentences and extends the result by each sentence's token list.
    Space complexity: O(total_tokens) for the returned list (plus any temporary overhead from extend operations).

## `sumy.evaluation.rouge._get_word_ngrams` · *function*

## Summary:
Return the set of all unique word n-grams (as tuples of tokens) found across a non-empty collection of Sentence objects.

## Description:
This function computes the union of n-gram sets produced from each Sentence in the provided collection. For each Sentence, it extracts that sentence's token list (via the helper that flattens Sentence.words) and then computes contiguous n-length token tuples using the n-gram helper; the per-sentence n-gram sets are merged into a single set which is returned.

Known callers and typical context:
- Intended for use in ROUGE-style evaluation and other n-gram overlap computations that compare token sequences extracted from Sentence objects (e.g., summary vs. reference comparisons). No specific call sites were found in the provided snippet, but typical triggers are metric computation functions in an evaluation pipeline that need the set of word n-grams for precision/recall/F-measure calculations.

Why this logic is factored out:
- Encapsulates the pattern "for each Sentence: obtain its tokens, compute n-grams, merge results" so that higher-level scoring code does not duplicate type-checking, tokenization, or n-gram extraction logic. It centralizes sizing preconditions (non-empty collection and positive n) and the union semantics for n-grams.

## Args:
    n (int):
        - Positive integer (n > 0).
        - Represents the size of the n-grams (number of tokens per n-gram).
        - The function asserts n > 0; calling with n <= 0 triggers AssertionError.
    sentences (sized iterable[Sentence]):
        - A non-empty sized iterable (supports len()) whose elements are instances of sumy.models.dom.Sentence (or compatible subclasses).
        - The function asserts len(sentences) > 0; calling with an empty collection triggers AssertionError.
        - Note: Because the function calls len(sentences), generators without __len__ are not acceptable unless wrapped in a sized container (list/tuple). Each element should be a Sentence instance; otherwise, the internal helper will raise ValueError.

Interdependencies:
    - The function relies on _split_into_words([sentence]) to turn a single Sentence into a token list.
    - It relies on _get_ngrams(n, token_list) to compute n-grams from that token list.

## Returns:
    set[tuple]:
        - A set containing unique n-gram tuples (each tuple contains n token elements) aggregated across all provided Sentence objects.
        - If at least one sentence contains at least n tokens, returned set contains tuples of length n.
        - If no sentence has n or more tokens (for example all sentences are shorter than n), the returned set will be empty.
        - The return value is a new set; the function does not preserve ordering.

## Raises:
    AssertionError:
        - If len(sentences) <= 0 (empty collection).
        - If n <= 0.
    TypeError (implicit):
        - If sentences does not support len() (e.g., passing None or a plain generator without len) the call to len(sentences) will raise TypeError.
    ValueError (propagated from helper):
        - If any element provided to the internal _split_into_words call is not a Sentence instance, _split_into_words raises ValueError ("Object in collection must be of type Sentence"). Because this function calls _split_into_words with one-element lists, a non-Sentence element in the input will cause that ValueError.
    Any exceptions raised by Sentence.words or the tokenizer:
        - Accessing Sentence.words may propagate tokenizer-specific exceptions (ValueError, RuntimeError, etc.); these propagate unchanged.

## Constraints:
Preconditions:
    - sentences must be a sized iterable (supports len()) and must not be empty.
    - Every element of sentences should be a properly constructed Sentence such that accessing .words does not raise unexpected errors.
    - n must be an integer and greater than zero.

Postconditions:
    - On successful return, the result is a set whose elements are tuples of tokens of length n (when any such n-grams exist).
    - No input objects are mutated by this function.
    - If the function returns normally, it guarantees that len(sentences) > 0 and n > 0 (because of the assertions).

## Side Effects:
    - None performed directly. The function does not perform I/O, mutate globals, or persist state.
    - Indirect side effects can occur when accessing Sentence.words if the tokenizer has caching or other side effects; those are defined by the tokenizer/Sentence implementation, not by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> AssertNonEmpty{"assert len(sentences) > 0"}
    AssertNonEmpty --> AssertN{"assert n > 0"}
    AssertN --> InitSet[/"words = set()"/]
    InitSet --> ForEachSentence[/"for sentence in sentences"/]
    ForEachSentence --> WrapSentence[/"call _split_into_words([sentence]) -> token_list"/]
    WrapSentence --> GetNgrams[/"call _get_ngrams(n, token_list) -> ngram_set"/]
    GetNgrams --> UpdateUnion[/"words.update(ngram_set)"/]
    UpdateUnion --> MoreSentences{more sentences?}
    MoreSentences -- Yes --> ForEachSentence
    MoreSentences -- No --> Return[/"return words (set of tuples)"/]
    Return --> End([End])

## Examples:
Typical usage (conceptual):
    # Given a list of Sentence objects, each providing .words via its tokenizer
    n = 2
    sentences = [s1, s2, s3]  # each is a sumy.models.dom.Sentence
    bigram_set = _get_word_ngrams(n, sentences)
    # bigram_set is a set of 2-token tuples aggregated across the sentences

Edge cases:
    - Empty input:
        _get_word_ngrams(2, [])  # raises AssertionError because the function requires a non-empty collection
    - Non-sized iterable:
        gen = (s for s in sentences_list)
        _get_word_ngrams(2, gen)  # likely raises TypeError at len(gen)
    - Element not a Sentence:
        _get_word_ngrams(1, [not_a_sentence])  # raises ValueError from _split_into_words

Usage recommendations:
    - Ensure sentences is a non-empty list or tuple of Sentence objects (not a generator).
    - Validate or sanitize inputs before calling if callers cannot guarantee those preconditions.

## `sumy.evaluation.rouge._get_index_of_lcs` · *function*

## Summary:
Return a 2-tuple containing the results of calling len() on each of two input objects.

## Description:
Known callers within the provided codebase:
    - None discovered in the provided repository scan.

Purpose and rationale:
    - A small utility that centralizes the two-length retrieval operations into a single callable. The function's current behavior is intentionally minimal: it delegates to Python's built-in len() for each argument and returns the two results as a tuple. Keeping this as a separate function makes it straightforward to replace or extend the length/index computation in one place if needed.

## Args:
    x (object): First input. Must be an object for which len(x) is a valid operation (i.e., implements __len__).
    y (object): Second input. Same requirement as x.
    Notes:
        - There are no other constraints or interdependencies between x and y.
        - The function does not modify x or y.

## Returns:
    tuple[int, int]: A tuple (len(x), len(y)) where each element is the integer value returned by Python's len() for the corresponding argument.
        - The returned integers are exactly whatever len() returns for each argument.
        - If len() returns an unusual value due to a custom __len__ implementation, that value is returned unchanged.

## Raises:
    - TypeError: Propagated if len(x) or len(y) is invalid for the provided object(s) (for example, when passing None or an object without __len__).
    - Any exception raised by the __len__ implementation of x or y will propagate unchanged.

## Constraints:
    Preconditions:
        - Both x and y must be acceptable operands for Python's len() built-in.
    Postconditions:
        - On successful return, no side effects have occurred and the tuple (len(x), len(y)) is returned.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or its inputs.

## Control Flow:
flowchart TD
    Start --> CallLenX
    CallLenX --> CallLenY
    CallLenY --> ReturnTuple
    ReturnTuple --> End

    Start([Start])
    CallLenX([Call len(x)])
    CallLenY([Call len(y)])
    ReturnTuple([Return (len(x), len(y))])
    End([End])

## Examples:
    Example 1 — strings:
        Input: x = "hello", y = "world!"
        Output: (5, 6)

    Example 2 — lists:
        Input: x = [1, 2, 3], y = []
        Output: (3, 0)

    Example 3 — invalid input:
        Input: x = None, y = "ok"
        Behavior: len(None) raises TypeError; the exception propagates from this function. Callers must validate inputs or handle the exception.

Implementation note:
    - Reimplement by returning (len(x), len(y)). Do not swallow exceptions; allow len() exceptions to propagate.

## `sumy.evaluation.rouge._len_lcs` · *function*

## Summary:
Return the integer length of the longest common subsequence (LCS) between two indexable sequences.

## Description:
Known callers within the codebase:
    - No direct callers were discovered in the available repository scan. The function is intended for use by ROUGE-L or other sequence-comparison routines that need the LCS length between two sequences.

Context and rationale:
    - This function centralizes the small, focused step of obtaining the final LCS length from the full dynamic-programming table produced by the LCS routine. Callers can obtain the final LCS length without needing to construct or inspect the full DP table themselves.

Implementation dependencies and error propagation:
    - This function delegates work to two helpers: a function that builds the LCS DP table and a function that returns the index pair (len(x), len(y)). Any exception raised by those helpers — including exceptions raised by Python's len() on x or y, by __getitem__ implementations during table construction, or by element comparison — will propagate unchanged to the caller.

## Args:
    x (Sequence): First input sequence. Must support len(x) and integer indexing x[i] for 0 <= i < len(x). Typical types: str, list, tuple, or other indexable containers (including domain objects that provide __len__ and __getitem__, e.g., models.dom.Sentence).
    y (Sequence): Second input sequence. Same requirements as x.

    Notes:
        - Elements of x and y must be comparable with ==, because the underlying LCS algorithm compares elements.
        - There are no additional interdependencies between x and y.
        - This function does not mutate x or y.

## Returns:
    int: The length of the longest common subsequence of x and y.
        - The returned value is the DP table entry for (len(x), len(y)).
        - For empty inputs (one or both sequences empty), the return value is 0.
        - The return value is always a non-negative integer.

## Raises:
    Any exception raised by the underlying helpers will propagate unchanged. Typical exceptions include:
        - TypeError: If len(x) or len(y) is invalid (for example, x or y is None or does not implement __len__), the TypeError raised by len() will propagate.
        - IndexError or other exceptions from __getitem__: If indexing of x or y during DP table construction raises, that exception will propagate.
        - Any exception raised by custom __len__, __getitem__, or element comparison implementations will propagate.

    Note:
        - The function itself does not catch or convert exceptions raised by its helpers; callers should validate inputs or handle exceptions as appropriate.

## Constraints:
Preconditions:
    - Both x and y must be indexable sequences: len(x) and len(y) must be valid integers and indexing x[i], y[j] must be supported for 0 <= i < len(x) and 0 <= j < len(y).
    - Elements must be comparable using equality (==).

Postconditions:
    - No mutation of x or y.
    - No I/O or global state changes.
    - Returns an integer equal to the LCS length for the full sequences, unless an exception from helpers is raised.

## Side Effects:
    - None. The function performs only in-memory operations via its helpers; it performs no I/O, network calls, logging, or global state mutation.

## Control Flow:
flowchart TD
    Start --> Call_lcs
    Call_lcs --> Call_get_index
    Call_get_index --> Access_table
    Access_table --> Return_result
    Return_result --> End

    Start([Start])
    Call_lcs([table = _lcs(x, y)])
    Call_get_index([n,m = _get_index_of_lcs(x, y)])
    Access_table([result = table[n, m]])
    Return_result([return result])
    End([End])

## Examples:
    Example 1 — strings (happy path):
        Input: x = "abcde", y = "ace"
        Typical usage:
            result = _len_lcs(x, y)
        Behavior: result == 3 (LCS "ace").

    Example 2 — lists and domain objects:
        Input: x = ["the", "cat"], y = ["the", "dog"]
        Typical usage:
            result = _len_lcs(x, y)
        Behavior: result == 1 (common element "the").

    Example 3 — empty sequence:
        Input: x = [], y = [1, 2]
        Typical usage:
            result = _len_lcs(x, y)
        Behavior: result == 0

    Example 4 — invalid input (error propagation):
        Input: x = None, y = "ok"
        Typical usage with error handling:
            try:
                result = _len_lcs(x, y)
            except TypeError:
                # handle invalid input type (len(None) raises TypeError)
                result = 0
        Behavior: The TypeError raised during length computation propagates; callers must validate or handle it.

## `sumy.evaluation.rouge._lcs` · *function*

## Summary:
Computes the dynamic-programming table of longest-common-subsequence (LCS) lengths for all prefix pairs of two indexable sequences and returns that table.

## Description:
Known callers:
    - No explicit callers were discovered in the available repository scan. 
    - Typical usage: This function is intended as a helper for ROUGE-L / LCS-based evaluation routines that need the LCS length between two sequences (for example, to compute precision, recall, or F-measure based on longest common subsequence).

Why this is a separate function:
    - The LCS dynamic programming table construction is a discrete, self-contained algorithmic step used by higher-level ROUGE or sequence-comparison code. Extracting it into a helper centralizes the DP logic, keeps callers focused on metric computation (rather than table construction), and makes it easier to test or swap the LCS implementation independently.

## Args:
    x (Sequence): First input sequence. Must support len(x) and integer indexing x[i] for 0 <= i < len(x). Elements must be comparable with ==. Examples: string, list, tuple, or other indexable container (e.g., models.dom.Sentence if used in this codebase).
    y (Sequence): Second input sequence. Same requirements as x.

    Notes:
        - There are no additional interdependencies between x and y beyond both being indexable and having a len().
        - Both arguments are read-only; this function does not modify x or y.

## Returns:
    dict[tuple[int, int], int]:
        A dictionary representing the DP table where each key is a tuple (i, j) with 0 <= i <= n and 0 <= j <= m (n = len(x), m = len(y)). Each value is an integer equal to the length of the LCS of the prefixes x[:i] and y[:j].

        Important points:
            - The entry (0, j) and (i, 0) are 0 for all i, j (empty-prefix cases).
            - The final LCS length for the full sequences is available at table[(n, m)].
            - All returned integers are >= 0.
            - For empty inputs (n == 0 or m == 0) the table contains only zeros for all valid (i, j) pairs.

## Raises:
    TypeError:
        - Propagated if len(x) or len(y) is invalid for the provided objects (for example, if either is None or an object without __len__). This originates from the underlying _get_index_of_lcs helper (which calls len()).
    IndexError / Any exception from __getitem__:
        - If x[i-1] or y[j-1] raises when accessed, that exception will propagate. Under normal, valid inputs (objects implementing __len__ and index access consistent with len), indexing in the loops is within bounds.
    Any exception raised by _get_index_of_lcs or by element comparison (==) will propagate unchanged.

## Constraints:
    Preconditions:
        - x and y must be indexable sequences: len(x) and len(y) must be valid and integer-indexing must be supported for indices 0..len(x)-1 and 0..len(y)-1.
        - Elements returned by x[i] and y[j] must be comparable using ==.

    Postconditions:
        - Returns a dict table with keys covering every (i, j) pair for i in 0..len(x) and j in 0..len(y).
        - table[(i, j)] equals the length of the longest common subsequence between x[:i] and y[:j].
        - The function performs no mutations to x or y and has no side effects.

## Side Effects:
    - None. The function performs pure in-memory computation and does not perform I/O, network access, or mutate global state.

## Control Flow:
flowchart TD
    Start --> GetLengths
    GetLengths --> InitTable
    InitTable --> OuterLoop_i
    OuterLoop_i --> InnerLoop_j
    InnerLoop_j --> CheckBaseCase
    CheckBaseCase -->|i==0 or j==0| SetZero
    CheckBaseCase -->|else| CheckEqual
    CheckEqual -->|x[i-1] == y[j-1]| SetDiagonalPlusOne
    CheckEqual -->|x[i-1] != y[j-1]| SetMaxNeighbor
    SetZero --> InnerLoopNext
    SetDiagonalPlusOne --> InnerLoopNext
    SetMaxNeighbor --> InnerLoopNext
    InnerLoopNext --> InnerLoop_j
    InnerLoop_j -->|j <= m| InnerLoop_j
    InnerLoop_j -->|j > m| OuterLoopNext
    OuterLoopNext --> OuterLoop_i
    OuterLoop_i -->|i <= n| OuterLoop_i
    OuterLoop_i -->|i > n| ReturnTable
    ReturnTable --> End

    Start([Start])
    GetLengths([Call _get_index_of_lcs -> (n,m)])
    InitTable([table = {}])
    OuterLoop_i([for i in 0..n])
    InnerLoop_j([for j in 0..m])
    CheckBaseCase([if i==0 or j==0])
    SetZero([table[i,j] = 0])
    CheckEqual([elif x[i-1] == y[j-1]])
    SetDiagonalPlusOne([table[i,j] = table[i-1,j-1] + 1])
    SetMaxNeighbor([table[i,j] = max(table[i-1,j], table[i,j-1])])
    InnerLoopNext([advance j / continue])
    OuterLoopNext([advance i / continue])
    ReturnTable([return table])
    End([End])

## Examples:
    Example 1 — simple strings:
        Input: x = "abcde", y = "ace"
        Behavior: len(x) = 5, len(y) = 3. The DP table is filled and table[(5, 3)] == 3 (the LCS is "ace").
        Returned table contains entries for all pairs (i, j) with i in 0..5 and j in 0..3; the final LCS length is found at table[(5, 3)].

    Example 2 — empty sequence:
        Input: x = [], y = [1, 2]
        Behavior: len(x) = 0, len(y) = 2. Every table[(i, j)] is 0. The returned table includes keys (0,0), (0,1), (0,2) and values all equal to 0; table[(0,2)] == 0.

    Error example:
        If x is None, calling this function will raise TypeError when len(x) is attempted inside _get_index_of_lcs; the exception is not caught here and will propagate to the caller.

Implementation note:
    - The returned table is a mapping keyed by (i, j) tuples rather than a nested list. Callers typically inspect table[(n, m)] to get the final LCS length, and may optionally reconstruct an LCS by backtracking through the table if needed.

## `sumy.evaluation.rouge._recon_lcs` · *function*

## Summary:
Backtracks the LCS dynamic-programming table and returns one longest common subsequence between two indexable sequences as an ordered tuple of elements.

## Description:
Known callers:
    - No explicit callers were discovered in the available repository scan.
    - Typical usage: used by ROUGE-L or other LCS-based evaluation routines that need the actual matched subsequence (for reporting, alignment, or further analysis). Callers supply the two sequences to compare; this function computes the DP table internally and reconstructs an LCS from it.

Why this logic is a separate function:
    - Reconstruction/backtracking is a distinct algorithmic step from computing the LCS length table. Extracting it keeps metric computation code focused on scoring, centralizes backtracking and tie-breaking behavior, and makes the LCS-reconstruction logic easier to test and maintain.

## Args:
    x (Sequence):
        - Type: any indexable sequence (supports len(x) and x[i] for 0 <= i < len(x)).
        - Examples: str, list, tuple, or domain objects that implement __len__ and __getitem__ (e.g., models.dom.Sentence).
        - Requirement: element comparisons use ==; elements must be comparable with equality.
    y (Sequence):
        - Type and requirements: same as x.
    Notes:
        - There are no default values.
        - Both arguments are read-only for this function; no in-place mutation occurs.

## Returns:
    tuple:
        - A tuple containing the elements (the values from x / y) that form one valid longest common subsequence, in the order they appear in x.
        - If there are no common elements, returns an empty tuple ().
        - If multiple different subsequences share the maximum length, this function deterministically returns one of them; the chosen subsequence is influenced by the backtracking tie-breaking implemented in the function (see Control Flow). The exact returned sequence depends only on the inputs and the DP table, not on external state.

## Raises:
    TypeError:
        - If either x or y is not suitable for len() (propagated from the internal length helper).
    IndexError or other exceptions from __getitem__:
        - If indexing x[i-1] or y[j-1] raises, that exception will propagate.
    Any exception from internal helpers:
        - Exceptions raised by _lcs or _get_index_of_lcs propagate unchanged.
    RecursionError:
        - Backtracking is implemented recursively and may raise RecursionError for very large inputs if Python's recursion depth is exceeded.

## Constraints:
    Preconditions:
        - x and y must be indexable sequences with valid len() and indexing for indices 0..len(x)-1 and 0..len(y)-1.
        - Element equality (==) must be meaningful for the sequence elements.
    Postconditions:
        - Returns a tuple that is a valid LCS of x and y (i.e., elements appear in the same relative order in both sequences and the length equals the LCS length).
        - No mutation of x or y; no I/O or external side effects.

## Side Effects:
    - None. Pure in-memory computation; no file, network, stdout, or global state modifications.

## Control Flow:
flowchart TD
    Start --> BuildTable
    BuildTable([table = _lcs(x, y)])
    BuildTable --> GetIndices
    GetIndices([i, j = _get_index_of_lcs(x, y) (usually len(x), len(y))])
    GetIndices --> Backtrack
    subgraph Backtracking
        Backtrack([_recon(i, j) recursive])
        Backtrack --> CheckBase
        CheckBase{if i==0 or j==0}
        CheckBase -->|true| ReturnEmptyList
        CheckBase -->|false| CheckEqual
        CheckEqual{if x[i-1] == y[j-1]}
        CheckEqual -->|true| RecurseDiagonalAndAppend[(recurse (i-1,j-1) and append (element,i))]
        CheckEqual -->|false| CompareNeighbors
        CompareNeighbors{if table[i-1,j] > table[i,j-1]}
        CompareNeighbors -->|true| RecurseUp[(recurse (i-1,j))]
        CompareNeighbors -->|false| RecurseLeft[(recurse (i,j-1))]
        RecurseDiagonalAndAppend --> Backtrack
        RecurseUp --> Backtrack
        RecurseLeft --> Backtrack
        ReturnEmptyList --> ExitBacktrack
    end
    Backtracking --> MapToElements([map (element,index) pairs to tuple of elements])
    MapToElements --> ReturnTuple([return tuple])
    ReturnTuple --> End

Notes on tie-breaking:
    - When table[i-1, j] == table[i, j-1], the implementation chooses the "left" branch (recurse to (i, j-1)). This deterministic choice affects which valid LCS is returned when multiple LCS values of the same length exist.

## Examples:
    Example 1 — strings:
        Call: _recon_lcs("abcde", "ace")
        Result: ('a', 'c', 'e')

    Example 2 — simple tie (different valid LCS sequences of same length):
        Inputs: x = ['a', 'b', 'c'], y = ['b', 'a', 'c']
        Possible LCSs of length 2 include ('a', 'c') and ('b', 'c'); this function returns one valid LCS. Which one is returned is deterministic and influenced by the backtracking tie-break rule (see Control Flow), but callers should not rely on a specific choice unless they rely on the implementation details.

    Example 3 — empty sequence:
        Call: _recon_lcs([], [1, 2])
        Result: ()

    Example 4 — defensive usage:
        When inputs may be invalid or very large, validate or guard the call:
            try:
                lcs = _recon_lcs(suspected_sequence_x, suspected_sequence_y)
            except (TypeError, IndexError, RecursionError) as exc:
                handle_error(exc)

## `sumy.evaluation.rouge.rouge_n` · *function*

## Summary:
Computes the ROUGE-N recall score between two collections of Sentence objects by dividing the count of overlapping n-grams in the evaluated collection by the total number of n-grams in the reference collection.

## Description:
This function is used to compute a ROUGE-style overlap metric (ROUGE-N recall) between a candidate summary (evaluated_sentences) and one or more reference sentences (reference_sentences). It:

- Validates that both collections are non-empty sized iterables.
- Extracts the set of unique word n-grams from each collection using the helper _get_word_ngrams(n, sentences).
- Computes the size of the intersection of the two n-gram sets.
- Returns the ratio overlapping_count / reference_count.

Known callers and typical context:
- No direct callers were found in the provided snippet of the codebase. Typical callers are higher-level evaluation code in a summarization evaluation pipeline that computes ROUGE scores (e.g., functions that aggregate precision/recall/f-measure for summaries vs. reference summaries).
- Typical trigger: after tokenization and sentence segmentation when an evaluator needs to compute n-gram recall between an automatically-generated summary and one or more human reference summaries.

Why this logic is factored out:
- Isolates the ROUGE-N recall computation from n-gram extraction and sentence/token handling.
- Keeps boundary responsibility focused: this function performs the ratio computation and relies on _get_word_ngrams for tokenization and n-gram generation, preventing duplication of n-gram aggregation and allowing callers to use the same scoring logic with different tokenizers or n values.

## Args:
    evaluated_sentences (sized iterable[Sentence]):
        - A non-empty sized iterable (e.g., list or tuple) whose elements are instances of sumy.models.dom.Sentence (or compatible objects exposing .words).
        - Required: len(evaluated_sentences) > 0. If len(...) <= 0 the function raises ValueError.
        - Note: generators without __len__ are not acceptable unless converted to a sized container first.

    reference_sentences (sized iterable[Sentence]):
        - A non-empty sized iterable (e.g., list or tuple) of Sentence instances representing the reference set.
        - Required: len(reference_sentences) > 0. If len(...) <= 0 the function raises ValueError.
        - The denominator of the returned ratio is computed from the set of n-grams extracted from this collection.

    n (int, optional):
        - The n-gram order (number of tokens per n-gram). Must be an integer > 0.
        - Default: 2 (bigrams).
        - If n <= 0, underlying helpers may raise AssertionError or otherwise fail.

Interdependencies:
- This function calls _get_word_ngrams(n, sentences) for each collection; therefore, its behavior depends on that helper's interpretation of Sentence and tokenization (including how Sentence.words is computed).

## Returns:
    float:
        - The ROUGE-N recall score: number of overlapping unique n-grams divided by the number of unique n-grams in the reference collection.
        - Value is computed as overlapping_count / reference_count and therefore is a float in the mathematical range [0.0, 1.0] when reference_count > 0.
        - Edge-case returns:
            * If there are no overlapping n-grams, returns 0.0.
            * If all reference n-grams overlap, returns 1.0.
        - Note: If reference_count is 0 (no reference n-grams exist because all reference sentences are shorter than n), the function will raise a ZeroDivisionError (see Raises).

## Raises:
    ValueError:
        - If len(evaluated_sentences) <= 0 or len(reference_sentences) <= 0, the function raises ValueError with message "Collections must contain at least 1 sentence." as enforced at the beginning of the function.

    ZeroDivisionError:
        - If the reference collection contains zero unique n-grams (reference_count == 0), the final division overlapping_count / reference_count will raise ZeroDivisionError. This occurs when no reference sentence contains at least n tokens.

    TypeError:
        - If evaluated_sentences or reference_sentences do not support len() (for example, passing a plain generator) the initial len(...) call will raise TypeError.

    AssertionError / ValueError / other exceptions (propagated from helpers):
        - If n <= 0, _get_word_ngrams or its helpers may assert and raise AssertionError.
        - If an element of the provided collections is not a Sentence instance, _get_word_ngrams (or its inner helper) may raise ValueError indicating an invalid element type.
        - Any exceptions raised while accessing Sentence.words or by the tokenizer will propagate unchanged.

## Constraints:
Preconditions:
    - Both evaluated_sentences and reference_sentences must be sized iterables with len(...) > 0.
    - n must be an integer greater than 0.
    - Each element in the collections should be a valid Sentence such that accessing .words succeeds.

Postconditions:
    - No input objects are mutated by this function.
    - If the function returns normally, it guarantees that the returned numeric value equals the ratio of the sizes of the intersection of unique n-gram sets to the size of the reference unique n-gram set.
    - If the function returns, reference_count > 0 (otherwise a ZeroDivisionError would have been raised).

## Side Effects:
    - None directly performed by this function: no I/O, no global state mutation, no network calls.
    - Indirect side effects may occur if accessing Sentence.words triggers caching or tokenizer side effects; those are properties of Sentence/tokenizer implementations, not this function.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckNonEmpty{"len(evaluated) > 0 AND len(reference) > 0 ?"}
    CheckNonEmpty -- No --> RaiseValueError[/"raise ValueError('Collections must contain at least 1 sentence.')"/]
    CheckNonEmpty -- Yes --> CallGetEval[/"evaluated_ngrams = _get_word_ngrams(n, evaluated_sentences)"/]
    CallGetEval --> CallGetRef[/"reference_ngrams = _get_word_ngrams(n, reference_sentences)"/]
    CallGetRef --> CountRef[/"reference_count = len(reference_ngrams)"/]
    CountRef --> CheckRefCount{"reference_count == 0 ?"}
    CheckRefCount -- Yes --> DivisionError[/"ZeroDivisionError on return overlapping_count / reference_count"/]
    CheckRefCount -- No --> Intersect[/"overlapping_ngrams = evaluated_ngrams ∩ reference_ngrams"/]
    Intersect --> CountOverlap[/"overlapping_count = len(overlapping_ngrams)"/]
    CountOverlap --> ReturnRatio[/"return overlapping_count / reference_count (float)"/]
    ReturnRatio --> End([End])

## Examples:
Typical usage (happy path):
    # Given two non-empty lists of Sentence objects (Sentence(text, tokenizer))
    # and a tokenizer that produces word tokens via Sentence.words
    evaluated = [Sentence("The quick brown fox.", tokenizer), Sentence("Jumps high.", tokenizer)]
    reference = [Sentence("The quick brown fox jumps high.", tokenizer)]
    score = rouge_n(evaluated, reference, n=2)
    # score is a float: number of overlapping bigrams divided by number of reference bigrams

Handling reference n-gram shortage (avoid ZeroDivisionError):
    # If reference sentences are all shorter than n, reference_count will be 0 and rouge_n will raise ZeroDivisionError.
    # Guard before calling:
    reference_ngrams = _get_word_ngrams(3, reference)
    if len(reference_ngrams) == 0:
        # decide convention (e.g., treat as score 0.0 or skip)
        score = 0.0
    else:
        score = rouge_n(evaluated, reference, n=3)

Error example:
    # Passing empty evaluated or reference lists:
    rouge_n([], [Sentence("Ref", tokenizer)])  # raises ValueError
    rouge_n([Sentence("Eval", tokenizer)], [])  # raises ValueError

## `sumy.evaluation.rouge.rouge_1` · *function*

## Summary:
Computes the ROUGE-1 (unigram) recall score between an evaluated collection of sentences and a reference collection by delegating to the generic ROUGE-N implementation with n = 1.

## Description:
This function is a lightweight convenience wrapper around the more general rouge_n function, fixing the n-gram order to 1 (unigrams). It is used when callers specifically require the ROUGE-1 recall metric without supplying the n parameter.

Known callers and typical context:
- Higher-level summarization evaluation code that computes ROUGE metrics for candidate summaries against one or more reference summaries. Typical pipeline stage: after tokenization and sentence segmentation, an evaluator will call this to obtain the unigram recall score.
- This wrapper is intentionally small so other parts of the code can request ROUGE-1 without specifying n explicitly.

Why this logic is a separate function:
- Improves readability and discoverability for the common case of ROUGE-1.
- Encapsulates the fixed parameter (n = 1) so callers don't repeat it and so bindings/APIs can offer a clear ROUGE-1 function alongside rouge_n for other n values.
- Leaves the numeric logic, validation, and edge-case handling to rouge_n, keeping this function trivial and stable.

## Args:
    evaluated_sentences (sized iterable[Sentence]):
        - A non-empty sized iterable (e.g., list or tuple) of sumy.models.dom.Sentence instances (or compatible objects exposing .words).
        - Must support len(); passing a plain generator (without __len__) is not acceptable unless converted to a sized container first.
        - Interdependency: evaluated_sentences and reference_sentences are both validated by rouge_n; both must be non-empty.

    reference_sentences (sized iterable[Sentence]):
        - A non-empty sized iterable (e.g., list or tuple) of Sentence instances representing the reference set.
        - The denominator of the returned ratio is computed from the set of reference unigrams as produced by rouge_n/_get_word_ngrams.

## Returns:
    float:
        - The ROUGE-1 recall score computed by rouge_n(evaluated_sentences, reference_sentences, 1).
        - Represents (number of overlapping unique unigrams) / (number of unique unigrams in reference collection).
        - Typical range: 0.0 through 1.0 when reference contains at least one unigram.
        - Edge cases:
            * If there are no overlaps, returns 0.0.
            * If all reference unigrams overlap, returns 1.0.
            * If reference contains zero unigrams (e.g., all reference sentences shorter than 1 token, an unlikely tokenizer edge-case), a ZeroDivisionError may be raised by rouge_n.

## Raises:
    ValueError:
        - Propagated from rouge_n when either evaluated_sentences or reference_sentences has length 0 (rouge_n enforces non-empty sized iterables).

    ZeroDivisionError:
        - Propagated from rouge_n if the reference collection yields zero unique unigrams, causing a division by zero in the underlying computation.

    TypeError:
        - If callers pass objects that do not support len(), a TypeError may be raised when rouge_n attempts len(...) on the inputs.

    Other exceptions:
        - Any exceptions raised while extracting .words from Sentence instances or from the tokenizer will propagate unchanged.

## Constraints:
Preconditions:
    - Both inputs must be sized iterables with len(...) > 0.
    - Each element must be a Sentence or behave like one (supporting .words).
    - Tokenizer and Sentence.words must function correctly (no side-effect-causing failures).

Postconditions:
    - No mutation of the input sentence objects is performed by this wrapper itself.
    - The return value equals rouge_n(..., 1)'s returned float when no exception is raised.
    - Exceptions raised by rouge_n are propagated unchanged.

## Side Effects:
    - This wrapper performs no I/O, global state mutation, or network calls.
    - Any side effects are those of rouge_n or of reading Sentence.words (e.g., cached_property behavior) and are not introduced by this wrapper.

## Control Flow:
flowchart TD
    Start([Start]) --> CallRougeN[/"Call rouge_n(evaluated_sentences, reference_sentences, 1)"/]
    CallRougeN --> rougeNCheck{"rouge_n performs:\n- len checks\n- n-gram extraction\n- intersection/count/division"}
    rougeNCheck -- Error --> PropagateError[/"Propagate ValueError/ZeroDivisionError/TypeError or other exception"/]
    rougeNCheck -- Success --> ReturnValue[/"Return float score (unigram recall)"/]
    ReturnValue --> End([End])

## Examples:
Typical usage:
    # Given two non-empty lists of Sentence objects with a tokenizer:
    evaluated = [Sentence("The quick brown fox.", tokenizer), Sentence("Jumps high.", tokenizer)]
    reference = [Sentence("The quick brown fox jumps high.", tokenizer)]
    score = rouge_1(evaluated, reference)
    # score is a float: number of overlapping unigrams divided by number of reference unigrams

Handling potential ZeroDivisionError (defensive):
    # If the reference collection could yield zero unigrams (tokenizer edge-case),
    # guard by checking reference unigrams first via the lower-level helper:
    reference_unigrams = _get_word_ngrams(1, reference)
    if len(reference_unigrams) == 0:
        score = 0.0  # or choose another convention (skip, log, etc.)
    else:
        score = rouge_1(evaluated, reference)

Error examples:
    rouge_1([], reference)            # raises ValueError (empty evaluated_sentences)
    rouge_1(evaluated, [])            # raises ValueError (empty reference_sentences)
    rouge_1(generator_of_sentences, reference)  # may raise TypeError due to lack of len()

## `sumy.evaluation.rouge.rouge_2` · *function*

## Summary:
Computes the ROUGE-2 (bigram) recall score between an evaluated collection of sentences and a reference collection by delegating to the generic ROUGE-N implementation with n=2.

## Description:
This is a thin convenience wrapper around the generic rouge_n function that fixes the n-gram order to 2 (bigrams). It accepts two sized iterables of Sentence objects and returns the same recall-style ROUGE score that rouge_n computes.

Known callers within the codebase:
- No direct call sites were found in the provided snippets. Typical callers are higher-level summarization evaluation routines or scripts that compute ROUGE scores for candidate summaries against one or more human reference summaries. These callers typically invoke this function after text tokenization and sentence segmentation.

Why this logic is extracted into its own function:
- Provides a clear, named entry point for the commonly-used bigram variant of ROUGE, improving readability at call sites (rouge_2(...) instead of rouge_n(..., 2)).
- Enforces the responsibility boundary: this function is only responsible for selecting n=2 and delegating the actual computation to rouge_n, avoiding repetition of parameter constants and making the intent explicit.

## Args:
    evaluated_sentences (sized iterable[Sentence]):
        - A non-empty sized iterable (e.g., list or tuple) of sumy.models.dom.Sentence instances or compatible objects exposing a .words property.
        - Requirement: len(evaluated_sentences) > 0. Passing a container with length 0 will cause a ValueError to be raised by the delegated rouge_n.
        - Note: generators without __len__ are not acceptable unless converted to a sized container first (a TypeError may result from calling len()).

    reference_sentences (sized iterable[Sentence]):
        - A non-empty sized iterable (e.g., list or tuple) of Sentence instances representing the reference summaries.
        - Requirement: len(reference_sentences) > 0. If empty, rouge_n will raise ValueError.
        - The denominator of the returned ratio is derived from the set of unique bigrams extracted from this collection.

Interdependencies:
- This function simply forwards its inputs to rouge_n with n fixed to 2; therefore its behavior depends on rouge_n and the helper it uses (_get_word_ngrams), and on Sentence.words (which is provided by the Sentence implementation and its tokenizer).

## Returns:
    float:
        - The ROUGE-2 recall score: the number of overlapping unique bigrams (2-grams) between the evaluated and reference collections divided by the number of unique bigrams in the reference collection.
        - Range: when reference bigram count > 0, the returned value is a float in [0.0, 1.0].
        - Edge cases:
            * If there are no overlapping bigrams, returns 0.0.
            * If all reference bigrams overlap, returns 1.0.
            * If the reference collection contains zero unique bigrams (for example, all reference sentences are shorter than 2 tokens), the delegated computation will attempt a division by zero and raise ZeroDivisionError.

## Raises:
    ValueError:
        - If evaluated_sentences or reference_sentences are sized iterables but have length 0. This check is performed by rouge_n which raises ValueError with a message like "Collections must contain at least 1 sentence."

    ZeroDivisionError:
        - If the reference collection yields zero unique bigrams (reference_count == 0), the final division overlapping_count / reference_count performed by rouge_n will raise ZeroDivisionError.

    TypeError:
        - If evaluated_sentences or reference_sentences do not support len() (e.g., a plain generator), attempting to call len(...) may raise TypeError before delegation to rouge_n.

    Other exceptions:
        - Any exceptions raised by rouge_n, the underlying _get_word_ngrams helper, or by accessing Sentence.words (such as tokenizer errors or assertion failures for invalid n) will propagate unchanged.

## Constraints:
Preconditions:
    - Both evaluated_sentences and reference_sentences must be sized iterables (support len()) and must each contain at least one Sentence object.
    - Individual elements must be compatible with Sentence.words access (i.e., Sentence instances or objects exposing a words attribute that returns token lists).
    - The function implicitly uses n = 2; callers who need a different n should call rouge_n directly.

Postconditions:
    - No input objects are mutated by this wrapper.
    - On successful return, the float represents the fraction of reference unique bigrams that also occur in the evaluated set.

## Side Effects:
    - This wrapper performs no I/O, network calls, or global state mutations.
    - Indirect side effects (such as caching) may occur when accessing Sentence.words, depending on the Sentence/tokenizer implementation; those side effects are outside the responsibility of this function.

## Control Flow:
flowchart TD
    Start([Start]) --> CallRougeN[/call rouge_n(evaluated_sentences, reference_sentences, 2)/]
    CallRougeN --> RougeNChecks{rouge_n: validate lenses and compute n-grams}
    RougeNChecks -- invalid len --> RaiseValueError[/"ValueError: Collections must contain at least 1 sentence."/]
    RougeNChecks -- reference n-grams == 0 --> RaiseZeroDivision[/"ZeroDivisionError on overlapping_count / reference_count"/]
    RougeNChecks -- valid --> ReturnScore[/"return float score (overlap / reference_count)"/]
    ReturnScore --> End([End])

## Examples:
Typical usage (happy path):
    # Given lists of Sentence objects constructed with an appropriate tokenizer:
    evaluated = [Sentence("The quick brown fox.", tokenizer), Sentence("Jumps high.", tokenizer)]
    reference = [Sentence("The quick brown fox jumps high.", tokenizer)]
    score = rouge_2(evaluated, reference)
    # score is a float equal to the fraction of reference unique bigrams found in evaluated.

Handling reference bigram shortage (avoid ZeroDivisionError):
    # If reference sentences are all shorter than 2 tokens, guard before calling:
    reference_bigrams = _get_word_ngrams(2, reference)
    if len(reference_bigrams) == 0:
        score = 0.0  # or handle according to your evaluation convention
    else:
        score = rouge_2(evaluated, reference)

Error example:
    rouge_2([], reference)            # raises ValueError
    rouge_2(evaluated, generator_of_refs)  # may raise TypeError because generator has no len()

## `sumy.evaluation.rouge._f_lcs` · *function*

## Summary:
Compute an F-like score from the length of a longest common subsequence (llcs) and two sequence lengths, returning a single floating-point measure that combines precision and recall derived from llcs.

## Description:
This helper computes recall and precision from the provided llcs and sequence lengths, derives a beta factor as the ratio of precision to recall, and returns the corresponding F-score using the formula:
(1 + beta^2) * recall * precision / (recall + beta^2 * precision)

Known callers:
    - No direct callers were present in the provided snapshot of the codebase. Conceptually, this function is intended to be invoked by higher-level ROUGE-L evaluation routines (within the same module) that compute or aggregate ROUGE-L precision/recall/F-measure for candidate summaries against references.

Why this is a separate function:
    - The numeric computation of the weighted F-score from llcs, m and n is a small, self-contained arithmetic operation. Extracting it isolates the mathematical formula, keeps higher-level evaluation code clearer, and centralizes edge-case behavior (division semantics) in one place.

## Args:
    llcs (int | float):
        - Length of the longest common subsequence between two sequences.
        - Expected to be non-negative.
        - Typical range: 0 <= llcs <= min(m, n).
    m (int | float):
        - Denominator used to compute recall (r_lcs = llcs / m).
        - Must be non-zero (m > 0) for the implementation to avoid a ZeroDivisionError.
    n (int | float):
        - Denominator used to compute precision (p_lcs = llcs / n).
        - Must be non-zero (n > 0) for the implementation to avoid a ZeroDivisionError.

Interdependencies:
    - llcs should not exceed m or n in normal usage (llcs <= min(m, n)).
    - The implementation requires r_lcs (llcs/m) to be non-zero because beta is computed as p_lcs / r_lcs; if r_lcs == 0 the function will raise a division-related error.

## Returns:
    float:
        - The computed F-like score using the derived beta factor.
        - For valid inputs (m > 0, n > 0, and llcs > 0 where llcs <= min(m, n)), the returned value is a float in the interval (0.0, 1.0], with 1.0 when llcs == m == n (perfect match).
        - The function does not return a special value for llcs == 0; instead it triggers a division error (see Raises).

## Raises:
    ZeroDivisionError:
        - If m == 0 or n == 0 (division by zero when computing recall or precision).
        - If llcs == 0 while m and n are non-zero (recall and precision become 0 and computing beta = p_lcs / r_lcs performs 0/0).
        - In summary, any situation that causes a division by zero in computing r_lcs, p_lcs, or beta will raise ZeroDivisionError.

## Constraints:
Preconditions:
    - m > 0 and n > 0 (to avoid immediate division by zero).
    - llcs is expected to be an integer or float satisfying 0 <= llcs <= min(m, n).
    - To avoid ZeroDivisionError in this implementation, require llcs > 0; if llcs == 0 you should handle that case before calling this function (for example, return 0.0).

Postconditions:
    - If the function returns normally, the result is a floating-point F-like score computed from r_lcs, p_lcs and their derived beta.
    - No input arguments are modified.

## Side Effects:
    - None. This function performs pure computation: no I/O, no global state mutation, no external calls.

## Control Flow:
flowchart TD
    Start([start]) --> ComputeR["r_lcs = llcs / m"]
    ComputeR --> ComputeP["p_lcs = llcs / n"]
    ComputeP --> ComputeBeta["beta = p_lcs / r_lcs"]
    ComputeBeta --> ComputeNum["num = (1 + beta^2) * r_lcs * p_lcs"]
    ComputeNum --> ComputeDenom["denom = r_lcs + (beta^2 * p_lcs)"]
    ComputeDenom --> Return["return num / denom"]
    ComputeR -.-> Error1["ZeroDivisionError if m == 0"]
    ComputeP -.-> Error2["ZeroDivisionError if n == 0"]
    ComputeBeta -.-> Error3["ZeroDivisionError if r_lcs == 0 (e.g., llcs == 0)"]

## Examples:
Example 1 — typical use (llcs > 0):
    # llcs = 2, m = 3, n = 4
    # r_lcs = 2/3 ≈ 0.6667
    # p_lcs = 2/4 = 0.5
    # beta = 0.5 / 0.6667 ≈ 0.75
    # returned ≈ 0.55
    try:
        score = _f_lcs(2, 3, 4)
    except ZeroDivisionError:
        # defensive handling if input may violate preconditions
        score = 0.0

Example 2 — defensive pattern for llcs == 0:
    # Because this implementation raises on llcs == 0, guard before calling:
    if llcs == 0:
        score = 0.0
    else:
        score = _f_lcs(llcs, m, n)

## `sumy.evaluation.rouge.rouge_l_sentence_level` · *function*

## Summary:
Compute a sentence-level ROUGE-L score between two collections of Sentence objects by flattening each collection into token sequences, measuring their longest common subsequence (LCS) length, and converting that into an F-like ROUGE-L score.

## Description:
This function is intended for sentence-level ROUGE-L evaluation: it accepts two collections (candidate/evaluated and reference) of sumy.models.dom.Sentence objects, converts each collection into a single flat token list, computes the length of the longest common subsequence between those token lists, and returns an F-like score derived from that LCS.

Known callers and usage context:
- No direct callers were discovered in the scanned codebase snapshot. Conceptually, it is invoked by ROUGE evaluation routines or test harnesses that compute sentence-level similarity between a produced sentence (or collection of sentences) and a reference sentence collection during summarization evaluation.
- Typical pipeline stage: after candidate and reference sentences are produced (or selected), this function is called to obtain a single scalar ROUGE-L score describing overlap at the sentence/token level.

Why this logic is factored out:
- The function composes three distinct responsibilities (flattening Sentence collections, computing LCS length, and converting LCS+lengths into an F-like score) using dedicated helpers. Factoring prevents duplication of token-flattening and numeric scoring logic across multiple evaluation routines and centralizes error/edge-case behavior (e.g., empty inputs or token sequences).

## Args:
    evaluated_sentences (sized iterable[Sentence]):
        - The candidate collection to evaluate. Must be a sized iterable (implements __len__) because the function checks its length.
        - Elements must be instances of sumy.models.dom.Sentence (or subclasses). Each Sentence must expose a .words property (an iterable of tokens).
        - The collection must contain at least one Sentence (len(evaluated_sentences) > 0) — otherwise a ValueError is raised.
        - Typical values: list[Sentence], tuple[Sentence]. Note: plain generators without a __len__ are not acceptable unless wrapped in a sized collection.

    reference_sentences (sized iterable[Sentence]):
        - The reference collection against which the candidate is compared. Same constraints as evaluated_sentences: must be sized, contain at least one Sentence, and hold Sentence instances.

Interdependencies:
    - Both arguments must be non-empty sized iterables. The content (Sentence -> tokens) influences downstream behavior: if all Sentences are empty (no tokens), downstream numeric helpers may raise ZeroDivisionError.

## Returns:
    float:
        - A floating-point ROUGE-L F-like score computed from:
            * llcs = longest common subsequence length between the flattened evaluated token list and flattened reference token list
            * m = number of tokens in the flattened reference sequence
            * n = number of tokens in the flattened evaluated sequence
        - The returned value is the result of _f_lcs(llcs, m, n) and therefore represents the combined precision/recall F-like measure derived from LCS.
        - Typical range: (0.0, 1.0] for non-zero llcs and positive m,n. A perfect match (llcs == m == n) yields 1.0.
        - Edge-case: when llcs == 0 or when m == 0 or n == 0, the underlying _f_lcs implementation can raise ZeroDivisionError (see Raises). Callers that want a 0.0 score for no overlap should guard and return 0.0 before calling this function.

## Raises:
    ValueError:
        - Raised immediately by this function if either evaluated_sentences or reference_sentences has length 0.
        - Exact message produced by the implementation: "Collections must contain at least 1 sentence."

    ValueError (propagated from helper):
        - _split_into_words raises ValueError if any element within the supplied collections is not an instance of Sentence. That exception is propagated unchanged.

    TypeError (propagated from helper):
        - If either argument is not iterable (or not a sized iterable compatible with the initial len() check), TypeError may be raised (for example, len(None) raises TypeError) or during iteration. These exceptions are propagated.

    ZeroDivisionError (propagated from _f_lcs):
        - If the flattened token counts lead to invalid denominators in the F-like computation (for example, m == 0 or n == 0, or llcs == 0 produces 0/0 when computing beta), _f_lcs will raise ZeroDivisionError. This can occur when collections contain Sentences that produce zero tokens in aggregate; callers should guard or interpret such situations before calling if they prefer a defined numeric result (such as 0.0).

    Other exceptions:
        - Any exceptions raised by tokenization or by the LCS routine (for example, from custom __len__ / __getitem__ / equality operations on token objects) will propagate unchanged.

## Constraints:
Preconditions (must be true before calling):
    - evaluated_sentences and reference_sentences are sized iterables (support __len__ and iteration).
    - len(evaluated_sentences) > 0 and len(reference_sentences) > 0.
    - Each element in both iterables is a sumy.models.dom.Sentence instance with a working .words property.

Postconditions (guarantees after return):
    - No mutation of the provided Sentence objects or their token lists by this function.
    - If the function returns normally, the return value is a float produced by _f_lcs, reflecting the LCS-based F-like score for the token sequences derived from the inputs.
    - If the function returns normally, no global or external state has been altered by this function (it is pure with respect to external state).

## Side Effects:
    - This function performs no I/O, network access, or global state mutations itself.
    - Accessing Sentence.words may perform caching or other side effects defined by the Sentence/tokenizer implementation; those side effects are not controlled by this function and are implementation-dependent.

## Control Flow:
flowchart TD
    Start --> CheckLen
    CheckLen{len(evaluated_sentences)>0 and len(reference_sentences)>0?}
    CheckLen -- No --> RaiseEmpty[Raise ValueError("Collections must contain at least 1 sentence.")]
    CheckLen -- Yes --> SplitRef[_split_into_words(reference_sentences)]
    SplitRef --> SplitEval[_split_into_words(evaluated_sentences)]
    SplitEval --> ComputeM["m = len(reference_words)"]
    ComputeM --> ComputeN["n = len(evaluated_words)"]
    ComputeN --> ComputeLcs[_len_lcs(evaluated_words, reference_words)]
    ComputeLcs --> ComputeScore[_f_lcs(lcs, m, n)]
    ComputeScore --> Return[return score]
    RaiseEmpty --> End
    Return --> End

## Examples:
- Basic (happy path):
    - When you have two lists of Sentence objects with tokens, call this function to obtain their ROUGE-L sentence-level F-like score. If tokens overlap, the returned float quantifies that overlap combining precision and recall via LCS.

- Defensive pattern when candidate or reference may produce no tokens:
    - Because this implementation will raise on zero token counts or zero LCS in the numeric helper, callers that prefer a defined numeric value (0.0) for no-overlap cases should check token counts first:
        * Flatten tokens (or call helper) and if either flattened length is 0, treat score as 0.0; otherwise call rouge_l_sentence_level.

- Error-handling sketch:
    - If you may receive non-Sentence items or non-iterable arguments, guard or catch:
        * Catch ValueError to detect non-Sentence elements.
        * Catch TypeError for non-iterable or non-sized inputs.
        * Catch ZeroDivisionError if you choose not to pre-guard m/n/llcs == 0 scenarios and want to fallback to 0.0 or log an error.

## `sumy.evaluation.rouge._union_lcs` · *function*

## Summary:
Compute the ROUGE-L "union LCS" score between one reference sentence and a collection of evaluated sentences by forming the union of per-sentence LCS token matches and returning the ratio of unique matched tokens to the sum of matched-token counts across all evaluated sentences.

## Description:
This function is used during ROUGE-L style evaluation to quantify how much of the reference sentence is covered by the union of longest-common-subsequence (LCS) matches across multiple candidate (evaluated) sentences.

Known callers within the codebase:
- ROUGE evaluation routines that combine sentence-level comparisons into a summary-level measure (for example, functions that compute union-LCS-based recall/precision values). These callers typically invoke this function when they have:
    - a single reference Sentence (the gold sentence), and
    - a non-empty iterable of evaluated Sentence objects (candidate sentences).
  The typical pipeline stage: tokenization (via Sentence.words/_split_into_words), LCS reconstruction on token sequences (_recon_lcs), then aggregation of matches into a union-based score.

Why this is extracted:
- Encapsulates the aggregation logic that (a) computes per-evaluated-sentence LCS with the reference (after tokenization), (b) unions the element-level matches to avoid double-counting the same token across evaluated sentences, and (c) computes the final ratio. Separating this keeps higher-level ROUGE code focused on orchestration and makes the LCS-union aggregation easier to test and maintain.

## Args:
    evaluated_sentences (sized iterable[Sentence]):
        - A sized iterable (list, tuple, or another object implementing __len__) containing one or more instances of sumy.models.dom.Sentence.
        - The function checks len(evaluated_sentences) and will raise ValueError if it is 0.
        - Each element is passed to _split_into_words([element]) to obtain a flat list of tokens for that sentence; these token sequences are then passed to _recon_lcs.
        - If the container does not implement __len__, a TypeError will be raised at the initial len() call.
        - If the iterable itself is not iterable (e.g., None), a TypeError will be raised when attempting to iterate.
        - If any element in the iterable is not a Sentence, _split_into_words will raise ValueError which will propagate.

    reference_sentence (Sentence):
        - A single instance of sumy.models.dom.Sentence representing the reference (gold) sentence.
        - Passed as a single-element list to _split_into_words to produce the token sequence for the reference.
        - If not a Sentence, accessing .words via _split_into_words will raise a ValueError.

Notes on interdependencies:
    - _split_into_words([sentence]) produces an indexable sequence (list) of tokens; those lists are passed to _recon_lcs. Therefore, the constraints of _recon_lcs apply to the token sequences returned: sequences must be indexable and element equality (==) must be meaningful. The function itself does not call _recon_lcs with Sentence objects.

## Returns:
    float
        - The union-LCS ratio computed as:
            union_lcs_value = (number of unique tokens present in the union of all per-evaluated-sentence LCS matches)
                              /
                              (sum of per-evaluated-sentence LCS match counts)
        - Numeric range: typically (0, 1] when denominator > 0. A value of 1.0 indicates all matched tokens across evaluated sentences were distinct; values closer to 0 indicate heavy overlap.
        - If all per-sentence LCS results are empty (no common subsequences), the denominator becomes zero and a ZeroDivisionError is raised (see Raises).

## Raises:
    ValueError:
        - If evaluated_sentences is empty (len(evaluated_sentences) <= 0).
        - Exact message: "Collections must contain at least 1 sentence."
        - Propagated ValueError from _split_into_words if any element is not a Sentence (message: "Object in collection must be of type Sentence").

    TypeError:
        - If evaluated_sentences does not support len() (sized protocol) the initial len() call will raise TypeError.
        - If evaluated_sentences is not iterable (e.g., None), iteration will raise TypeError when the function attempts to iterate.
        - Other TypeError cases from helper functions (_split_into_words or _recon_lcs) will propagate.

    ZeroDivisionError:
        - If every per-evaluated-sentence LCS is empty so that combined_lcs_length == 0, the final division will raise a ZeroDivisionError.

    Propagated exceptions from helpers:
        - Any exception raised by _split_into_words (for example, ValueError) or _recon_lcs (TypeError, IndexError, RecursionError for very large inputs) will propagate unchanged.

## Constraints:
Preconditions:
    - evaluated_sentences must be a sized iterable (supporting __len__) containing at least one Sentence.
    - reference_sentence must be a Sentence.
    - Sentence.words must produce indexable token sequences whose elements support equality comparisons.

Postconditions:
    - If the function returns normally, it returns a float representing the union-LCS ratio as described above.
    - No mutation of Sentence objects occurs.
    - No I/O or external state changes are performed.

## Side Effects:
    - This function performs only in-memory computation. It does not perform any I/O, network calls, or mutate global state.
    - Indirect side effects may arise from accessing Sentence.words (for example, if the tokenizer caches tokens), but those are implementation details of Sentence and its tokenizer and are not performed by this function itself.

## Control Flow:
flowchart TD
    Start --> CheckNonEmpty
    CheckNonEmpty{len(evaluated_sentences) <= 0?}
    CheckNonEmpty -- Yes --> RaiseValue[Raise ValueError("Collections must contain at least 1 sentence.")]
    CheckNonEmpty -- No --> InitSets[Initialize lcs_union = set(), combined_lcs_length = 0]
    InitSets --> TokenizeReference[reference_words = _split_into_words([reference_sentence])]
    TokenizeReference --> ForEachEval[For each eval_s in evaluated_sentences]
    ForEachEval --> TokenizeEval[evaluated_words = _split_into_words([eval_s])]
    TokenizeEval --> ReconLCS[lcs = set(_recon_lcs(reference_words, evaluated_words))]
    ReconLCS --> Accumulate[combined_lcs_length += len(lcs); lcs_union = lcs_union.union(lcs)]
    Accumulate --> MoreEval{more evaluated_sentences?}
    MoreEval -- Yes --> ForEachEval
    MoreEval -- No --> ComputeRatio
    ComputeRatio --> Divide[union_lcs_value = len(lcs_union) / combined_lcs_length]
    Divide --> ReturnValue[return union_lcs_value]
    ReturnValue --> End

Notes:
    - If combined_lcs_length == 0 at Divide step, a ZeroDivisionError occurs.

## Complexity:
    - Time: For each evaluated sentence, _recon_lcs performs an LCS computation that is typically O(len(reference_tokens) * len(evaluated_tokens)). Total time is roughly the sum of those costs across all evaluated_sentences.
    - Space: Dominated by the LCS DP table inside _recon_lcs for each pairwise computation; plus O(u) extra for the union set where u is number of unique matched tokens.

## Examples:
    Example 1 — typical successful case:
        Given a reference sentence whose tokens are ['the', 'cat', 'sat'] and two evaluated sentences that yield LCS token lists of ['the', 'cat'] and ['cat', 'sat'] respectively:
            - per-sentence LCS sets: {'the', 'cat'} and {'cat', 'sat'}
            - lcs_union = {'the', 'cat', 'sat'} => union_lcs_count = 3
            - combined_lcs_length = 2 + 2 = 4
            - returned value = 3 / 4 = 0.75

    Example 2 — empty evaluated_sentences (error):
        If evaluated_sentences is an empty list, the function raises ValueError("Collections must contain at least 1 sentence.").

    Example 3 — no matches (division by zero):
        If each evaluated sentence has no LCS with the reference (all per-sentence LCS are empty), combined_lcs_length == 0 and the function raises ZeroDivisionError. Callers that need a 0.0 score in this scenario must guard against this exception and substitute the desired fallback.

    Defensive usage pattern:
        - Validate that evaluated_sentences is non-empty and sized before calling, or catch ValueError/TypeError.
        - After calling, be prepared to handle ZeroDivisionError if callers expect the possibility of no LCS matches.

## `sumy.evaluation.rouge.rouge_l_summary_level` · *function*

## Summary:
Aggregate union-LCS scores across reference sentences and return a summary-level ROUGE-L F-like score computed from the aggregated LCS length and the total token counts of the reference and evaluated collections.

## Description:
This function performs the final aggregation step of ROUGE-L summary evaluation: it validates both collections are non-empty, computes total token counts for references and evaluated sentences, sums the union-LCS value for each reference (calling _union_lcs), and returns the F-like score computed by _f_lcs.

Typical usage context:
- Invoked by summary-level evaluation code after candidate and reference summaries have been segmented into Sentence objects (i.e., tokenization and sentence splitting are already done). It orchestrates the helpers _split_into_words (to count tokens), _union_lcs (to compute per-reference union-LCS), and _f_lcs (to compute the final F-like score).

Why this is a separate function:
- Orchestrates and enforces collection-level preconditions (non-empty sequences), aggregates per-reference metrics, and delegates tokenization/LCS math to specialized helpers. Isolating this keeps higher-level evaluation code concise and centralizes the summary-level scoring rule.

## Args:
    evaluated_sentences (sized iterable[Sentence]):
        - A sized iterable (e.g., list or tuple) of sumy.models.dom.Sentence instances representing candidate (evaluated) sentences.
        - Must implement __len__ because the function calls len(evaluated_sentences).
        - If any element is not a Sentence, _split_into_words will raise ValueError("Object in collection must be of type Sentence") and that will propagate.
    reference_sentences (sized iterable[Sentence]):
        - A sized iterable (e.g., list or tuple) of sumy.models.dom.Sentence instances representing reference (gold) sentences.
        - Must implement __len__ because the function calls len(reference_sentences).
        - Each element is iterated and passed individually to _union_lcs; if an element is not a Sentence, _split_into_words will raise ValueError("Object in collection must be of type Sentence") and that will propagate.

Interdependencies:
- m is computed as len(_split_into_words(reference_sentences)): total number of tokens across reference_sentences.
- n is computed as len(_split_into_words(evaluated_sentences)): total number of tokens across evaluated_sentences.
- For each ref_s in reference_sentences, the function calls _union_lcs(evaluated_sentences, ref_s) and accumulates the returned numeric values into union_lcs_sum_across_all_references.
- The final return value is _f_lcs(union_lcs_sum_across_all_references, m, n). The constraints and exceptions of _split_into_words, _union_lcs, and _f_lcs therefore apply.

## Returns:
    float:
        - The F-like ROUGE-L score produced by _f_lcs where:
            * llcs = sum over references of _union_lcs(evaluated_sentences, ref_s)
            * m = total token count of reference_sentences
            * n = total token count of evaluated_sentences
        - Typical numeric range: (0.0, 1.0] for valid, non-degenerate inputs.
        - This function does not return a sentinel for no-overlap cases; instead, helper functions may raise exceptions in those cases (see Raises).

## Raises:
    ValueError:
        - Raised directly by this function if either input collection is empty:
            * Condition: len(evaluated_sentences) <= 0 or len(reference_sentences) <= 0
            * Exact message: "Collections must contain at least 1 sentence."
        - Propagated from _split_into_words if any element in the provided iterables is not a Sentence:
            * Message from helper: "Object in collection must be of type Sentence"

    TypeError:
        - If either argument does not support len() (i.e., is not a sized object), calling len(...) may raise TypeError.
        - If either argument is not iterable (e.g., None), helper calls that iterate over them will raise TypeError.
        - These TypeError conditions originate from Python built-ins or from the helper functions and propagate unchanged.

    ZeroDivisionError:
        - May be raised indirectly:
            * _union_lcs can raise ZeroDivisionError when the per-evaluated-sentence LCS lengths sum to zero (no matches across evaluated sentences), as documented in that helper.
            * _f_lcs raises ZeroDivisionError when m == 0 or n == 0, or when internal divisions (e.g., computing beta) encounter zero denominators (for example llcs == 0).
        - Callers that prefer a 0.0 score for no-match cases should catch ZeroDivisionError and substitute their chosen fallback.

    Other exceptions:
        - Any exceptions raised by Sentence.words or the tokenizer (e.g., from _split_into_words) will propagate.

## Constraints:
Preconditions:
    - Both evaluated_sentences and reference_sentences must be sized iterables containing at least one Sentence instance each.
    - Each Sentence must be valid such that accessing .words (via _split_into_words) yields token sequences whose elements support equality comparisons required by LCS computations.

Postconditions:
    - On normal return, returns a float F-like ROUGE-L score. Inputs are not mutated by this function.

## Side Effects:
    - The function does not perform I/O or mutate global state.
    - Accessing Sentence.words may trigger tokenizer-side effects (e.g., caching) defined by the Sentence/tokenizer implementations; those are not caused by this function itself but may occur during its execution.

## Control Flow:
flowchart TD
    Start --> CheckNonEmpty{len(evaluated_sentences) <= 0 OR len(reference_sentences) <= 0?}
    CheckNonEmpty -- Yes --> RaiseValue[Raise ValueError("Collections must contain at least 1 sentence.")]
    CheckNonEmpty -- No --> ComputeM["m = len(_split_into_words(reference_sentences))"]
    ComputeM --> ComputeN["n = len(_split_into_words(evaluated_sentences))"]
    ComputeN --> InitSum["union_lcs_sum_across_all_references = 0"]
    InitSum --> ForRef[For each ref_s in reference_sentences]
    ForRef --> AddUnion["union_lcs_sum_across_all_references += _union_lcs(evaluated_sentences, ref_s)"]
    AddUnion --> MoreRefs{more reference_sentences?}
    MoreRefs -- Yes --> ForRef
    MoreRefs -- No --> CallF["return _f_lcs(union_lcs_sum_across_all_references, m, n)"]
    CallF --> End

Notes:
    - Exceptions from helpers (_split_into_words, _union_lcs, _f_lcs) interrupt this flow and propagate unless caught by the caller.

## Examples:
Example 1 — typical usage with defensive handling:
    try:
        score = rouge_l_summary_level(evaluated_sentences, reference_sentences)
    except ValueError as exc:
        # Either collection empty or contained a non-Sentence element
        handle_invalid_input(exc)
    except ZeroDivisionError:
        # No LCS matches or zero-length token sequences led to a division error;
        # substitute an application-specific fallback, e.g.:
        score = 0.0

Example 2 — single reference (wrapped as a list):
    # Provide a single reference Sentence by wrapping it in a one-element iterable
    score = rouge_l_summary_level(evaluated_sentences, [single_reference_sentence])

