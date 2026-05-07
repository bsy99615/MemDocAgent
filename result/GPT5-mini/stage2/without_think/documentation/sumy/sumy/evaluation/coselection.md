# `coselection.py`

## `sumy.evaluation.coselection.f_score` · *function*

## Summary:
Compute the F-score (weighted harmonic mean of precision and recall) for two collections of items; returns a float in [0.0, 1.0] that balances precision and recall according to a supplied weight (beta).

## Description:
This function retrieves precision and recall for the evaluated (system-selected) items against the reference (ground-truth) items, applies the standard F_beta formula, and returns the resulting score. It is intended for use in evaluation pipelines that compare sets of sentence identifiers or sentence objects produced by a summarizer or selection algorithm to a reference set.

Known callers within the codebase:
- No direct callers were discovered in the available repository snapshot.
- Typical use cases: summary-evaluation code and scoring pipelines that compute set-based metrics for predicted vs. gold sentences; it is called once precision and recall semantics (set-based overlap) are appropriate.

Why this logic is extracted into its own function:
- Encapsulates the F_beta scoring semantics (combining precision and recall) in a single, testable routine.
- Keeps metric composition separate from the low-level set-handling, validation, and numeric ratio computation implemented by the shared precision/recall helper functions.
- Offers a stable API for downstream code to request an F-score without duplicating the formula or the error handling around degenerate inputs.

## Args:
    evaluated_sentences (iterable[Hashable]):
        Collection of items chosen/selected by the system (treated as the "retrieved" set).
        - Items must be hashable (strings, ints, or objects implementing __hash__) because precision/recall convert the inputs to sets.
        - Duplicates are ignored (the function uses unique items only).
    reference_sentences (iterable[Hashable]):
        Collection of ground-truth/reference items (treated as the "relevant" set).
        - Also converted to a set; duplicates ignored.
    weight (float, optional):
        Non-negative numeric weight controlling the relative importance of recall vs. precision.
        - Default: 1.0.
        - Interpreted as the conventional beta parameter: the function internally squares this value (weight **= 2) and uses beta^2 in the F_beta formula.
        - Allowed values: any numeric value accepted by Python arithmetic; callers should pass weight >= 0 for meaningful metric semantics. Negative weights are not prohibited by the code but produce non-standard results and are not recommended.

Interdependencies:
    - precision() and recall() are called with the same evaluated_sentences and reference_sentences; both functions impose their own preconditions: each input must yield a non-empty set after deduplication and contain only hashable elements (otherwise ValueError or TypeError may be raised).

## Returns:
    float:
        The weighted F-score computed as:
            if denominator == 0.0:
                return 0.0
            else:
                return ((beta^2 + 1) * p * r) / (beta^2 * p + r)
        where:
            - p is precision(evaluated_sentences, reference_sentences) ∈ [0.0, 1.0]
            - r is recall(evaluated_sentences, reference_sentences) ∈ [0.0, 1.0]
            - beta is the provided weight argument (the function squares it internally)
        All returned values are floats in [0.0, 1.0].
        Edge cases:
            - If both precision and recall are 0.0 (no overlap), the function returns 0.0.
            - If the computed denominator equals 0.0, the function returns 0.0 to avoid division by zero.

## Raises:
    ValueError:
        Propagated from precision() or recall() if either input collection is empty after conversion to a set.
        - Underlying helper message: "Both collections have to contain at least 1 sentence."
    TypeError:
        May be raised during set conversion inside precision() / recall() if any element in the inputs is unhashable (for example, a list). This is not raised directly by f_score but will surface from the underlying helpers.

## Constraints:
    Preconditions:
        - evaluated_sentences and reference_sentences must be iterables of hashable items.
        - After deduplication (set conversion), both collections must contain at least one element, otherwise precision() or recall() will raise ValueError.
        - The caller should pass a non-negative numeric weight (beta). The function does not validate negativity; negative values are allowed by the code but yield non-standard metric behavior.
    Postconditions:
        - Inputs are not mutated by this function.
        - The returned value is a float; when preconditions are satisfied it is in [0.0, 1.0].
        - No I/O or external state is modified.

## Side Effects:
    - None performed by f_score itself.
    - Any exceptions arise from in-memory operations performed by precision() and recall(); there is no file, network, stdout, or global-state interaction.

## Control Flow:
flowchart TD
    Start --> CallPrecision
    Start --> CallRecall
    CallPrecision --> p_value["p = precision(...)"]
    CallRecall --> r_value["r = recall(...)"]
    p_value --> SquareWeight["weight **= 2  (beta^2)"]
    r_value --> SquareWeight
    SquareWeight --> ComputeDenominator["denominator = beta^2 * p + r"]
    ComputeDenominator --> CheckZero{"denominator == 0.0?"}
    CheckZero -- Yes --> ReturnZero["return 0.0"]
    CheckZero -- No --> ComputeF["return ((beta^2 + 1) * p * r) / denominator"]
    ReturnZero --> End
    ComputeF --> End

## Examples:
1) Basic usage (F1, equal weight):
    try:
        score = f_score(['s1','s2'], ['s1','s2','s3'])  # default weight=1.0 -> F1
        # precision = 1.0, recall = 2/3 -> F1 = (1+1) * 1.0 * (2/3) / (1*1.0 + 2/3) = 0.8
    except (ValueError, TypeError) as exc:
        # handle invalid inputs (empty collections or unhashable elements)
        raise

2) Emphasize recall (beta > 1):
    # weight=2.0 -> beta^2 = 4.0; recall is favored over precision
    score_recall_favored = f_score(evaluated, reference, weight=2.0)

3) Emphasize precision (beta < 1):
    # weight=0.5 -> beta^2 = 0.25; precision is favored over recall
    score_precision_favored = f_score(evaluated, reference, weight=0.5)

4) Handling degenerate overlap:
    # No overlap between sets -> precision = recall = 0.0 -> denominator == 0.0 -> returns 0.0
    f_score(['a'], ['b'])  # returns 0.0

5) Error handling (empty after deduplication):
    try:
        f_score([], ['s1'])  # precision/recall helper will raise ValueError
    except ValueError as e:
        # expected: "Both collections have to contain at least 1 sentence."
        handle_error(e)

## `sumy.evaluation.coselection.precision` · *function*

## Summary:
Return the precision-style overlap score: the fraction of unique evaluated (selected) items that appear in the reference set, as a float in [0.0, 1.0].

## Description:
This function is a minimal, metric-specific wrapper around a generic overlap helper. It invokes the underlying helper with the reference collection as the numerator and the evaluated collection as the denominator to compute how many of the system-selected items are correct according to the reference (precision).

Known callers within the codebase:
- No direct callers discovered in the available repository snapshot. Typically used by summary-evaluation code to compute coselection precision between predicted (evaluated) sentences and gold/reference sentences.

Why this is a separate function:
- Encapsulates metric semantics (precision) and provides a clear, stable API with the conventional argument order (evaluated first, reference second), avoiding caller confusion about numerator/denominator ordering in the lower-level utility.
- Keeps high-level metric naming separate from the generic numeric routine that handles set conversion and validation.

## Args:
    evaluated_sentences (iterable[Hashable]):
        Collection of items chosen or selected by the system (denominator).
        - Items must be hashable (e.g., strings, integers, or objects implementing __hash__).
        - The collection is converted to a set internally; duplicates are ignored and ordering is not considered.
    reference_sentences (iterable[Hashable]):
        Collection of ground-truth/reference items (numerator).
        - Also converted to a set; duplicates ignored.
    Interdependencies:
        - Both iterables must contain at least one element after deduplication (see Raises).
        - All items must be hashable or set conversion will raise TypeError.

## Returns:
    float:
        The ratio common_count / chosen_count, where:
        - common_count = |set(evaluated_sentences) ∩ set(reference_sentences)|
        - chosen_count = |set(evaluated_sentences)|
        Characteristics:
        - Value is in [0.0, 1.0].
        - 1.0 means every unique evaluated item appears in the reference.
        - 0.0 means no evaluated item appears in the reference.
        - Computation is based on unique items only; duplicate inputs do not change the result.

## Raises:
    ValueError:
        If either evaluated_sentences or reference_sentences is empty after conversion to a set.
        Exact message produced by the underlying helper: "Both collections have to contain at least 1 sentence."
    TypeError:
        May be raised during set conversion if any element in the inputs is unhashable (for example, a list). This error is not explicitly raised by this wrapper but will surface from the frozenset/set conversion used by the helper.

## Constraints:
    Preconditions:
        - Both arguments are iterables of hashable items.
        - Each iterable contains at least one element (non-empty after deduplication).
    Postconditions:
        - Inputs are not mutated by this function.
        - The return value is a float in [0.0, 1.0].
        - No I/O or external side effects occur.

## Side Effects:
    - None. Purely in-memory computation; no file, network, stdout, or global-state mutation.

## Control Flow:
flowchart TD
    Start --> precision_called
    precision_called --> CallHelper(reference_as_numerator,evaluated_as_denominator)
    CallHelper --> HelperConvertsToSets
    HelperConvertsToSets --> HelperChecksEmpty
    HelperChecksEmpty -- any empty --> RaiseValueError
    HelperChecksEmpty -- both non-empty --> ComputeIntersection
    ComputeIntersection --> ComputeRatio
    ComputeRatio --> ReturnFloat
    RaiseValueError --> End
    ReturnFloat --> End

## Examples:
- Basic overlap (duplicates in evaluated collapse):
    evaluated_sentences = ['s4', 's2', 's2']    # dedup -> {'s4','s2'}
    reference_sentences = ['s1', 's2', 's3']    # -> {'s1','s2','s3'}
    Result: precision(evaluated_sentences, reference_sentences) -> 1 / 2 -> 0.5

- All evaluated items present:
    evaluated_sentences = ['s1', 's2']
    reference_sentences = ['s1', 's2', 's3']
    Result -> 1.0

- No overlap:
    evaluated_sentences = ['a', 'b']
    reference_sentences = ['x', 'y']
    Result -> 0.0

- Empty-collection error:
    evaluated_sentences = []
    reference_sentences = ['s1']
    Result -> raises ValueError("Both collections have to contain at least 1 sentence.")

- Unhashable-item error:
    evaluated_sentences = [['a']]   # list is unhashable
    reference_sentences = [['a']]
    Result -> raises TypeError during set conversion

## `sumy.evaluation.coselection.recall` · *function*

## Summary:
Computes the recall of evaluated sentences against a reference set — the fraction of reference items that appear among the evaluated items.

## Description:
This function is a thin wrapper that delegates the numeric computation to a shared helper which computes an overlap ratio between two collections. It interprets the first argument (evaluated_sentences) as the set of retrieved/selected items and the second argument (reference_sentences) as the set of relevant/reference items; the result is the proportion of reference items that were retrieved.

Known callers within the codebase:
- No direct callers were discovered in the available repository snapshot. Typical call sites are evaluation utilities and scoring pipelines that compute standard information-retrieval metrics (recall) for sets of sentence identifiers or sentence objects after selection or summarization steps.

Why this logic is extracted:
- Provides a clear, semantically named entrypoint for the recall metric while reusing the generic set-overlap ratio implementation.
- Keeps metric naming and intent separate from the low-level set handling, validation, and ratio calculation performed by the helper function.

## Args:
    evaluated_sentences (iterable[Hashable]):
        Items considered as retrieved/selected (numerator). Can be any iterable of hashable elements (e.g., strings, ints, objects with __hash__).
        Duplicates are ignored (the collection is treated as a set).
    reference_sentences (iterable[Hashable]):
        Items considered as relevant/reference (denominator). Also must be an iterable of hashable elements and is treated as a set.
    Interdependencies:
        - Both iterables must contain at least one element (non-empty after conversion to a set); otherwise a ValueError is raised.
        - All items must be hashable; attempting to use unhashable items will raise a TypeError when converting to a set.

## Returns:
    float:
        The recall value computed as:
            (number of unique items present in both evaluated_sentences and reference_sentences)
            divided by
            (number of unique items in reference_sentences)
        Properties:
        - Value is in the closed interval [0.0, 1.0].
        - 1.0 indicates every reference item was found among evaluated items.
        - 0.0 indicates no reference items were found.
        - Computation uses unique items only; duplicate elements in inputs do not increase counts.

## Raises:
    ValueError:
        Raised when either evaluated_sentences or reference_sentences is empty after converting to a set.
        Error message (from the underlying helper): "Both collections have to contain at least 1 sentence."
    TypeError:
        May be raised when converting the inputs to sets if any contained item is unhashable (for example, lists). This is a consequence of set conversion rather than an explicit check.

## Constraints:
    Preconditions:
        - Both inputs are iterables of hashable elements.
        - Both inputs contain at least one element each.
    Postconditions:
        - The function performs no mutation of the provided iterables.
        - The returned float is between 0.0 and 1.0 inclusive.
        - No I/O or external state is modified.

## Side Effects:
    - None. The function performs only in-memory computations and delegates entirely to a pure helper; it does not perform file or network I/O, print to stdout, or modify global state.

## Control Flow:
flowchart TD
    Start --> ConvertInputsToSets
    ConvertInputsToSets --> CheckReferenceEmpty
    CheckReferenceEmpty -- reference empty --> RaiseValueError
    CheckReferenceEmpty -- reference non-empty --> ComputeIntersection
    ComputeIntersection --> CountIntersectionAndReference
    CountIntersectionAndReference --> ComputeRatio
    ComputeRatio --> ReturnFloat
    RaiseValueError --> End
    ReturnFloat --> End

## Examples:
- Typical usage:
    Inputs: evaluated_sentences = ['s2', 's3'], reference_sentences = ['s1', 's2']
    Result: recall -> 0.5 (only 's2' of two reference items was retrieved)

- Duplicates in inputs:
    Inputs: evaluated_sentences = ['s1', 's1', 's2'], reference_sentences = ['s1', 's1']
    Interpretation after deduplication: evaluated set = {'s1','s2'}, reference set = {'s1'}
    Result: recall -> 1.0 (the single reference item is present among evaluated items)

- Empty reference set:
    Inputs: evaluated_sentences = ['s1'], reference_sentences = []
    Result: raises ValueError explaining both collections must contain at least one sentence

- Unhashable items:
    Inputs: evaluated_sentences = [['a']], reference_sentences = [['a']]
    Result: TypeError raised during set conversion because list elements are unhashable

## `sumy.evaluation.coselection._divide_evaluation` · *function*

## Summary:
Computes the fraction of items from the denominator collection that also appear in the numerator collection (i.e., the proportion of chosen sentences that were present in the numerator).

## Description:
This helper computes a ratio used for coselection-style evaluation: how many unique items from a "chosen" (denominator) set are present in a reference or candidate (numerator) set, expressed as a float in [0.0, 1.0].

Known callers within the codebase:
- No direct callers discovered in the available repository snapshot. Typical usage is from evaluation utilities that measure overlap between two sets of sentence identifiers or sentence objects.

Why this logic is extracted:
- Separates the small, well-defined numeric computation (overlap ratio) from higher-level evaluation orchestration.
- Encapsulates set conversion, empty-collection validation, and ratio calculation in one place so callers can rely on a consistent semantics (unique items only, denominator-based normalization).

## Args:
    numerator_sentences (iterable[Hashable]):
        Collection of items treated as the numerator set. Items must be hashable (e.g., strings, integers, or objects implementing __hash__).
        The function converts this collection to a frozenset, therefore only unique elements are considered and ordering is ignored.
    denominator_sentences (iterable[Hashable]):
        Collection of items treated as the denominator (the set being normalized over; e.g., chosen/selected sentences).
        Also converted to a frozenset; duplicates and ordering are ignored.
    Interdependencies:
        - Both arguments are required and must be non-empty collections (see Raises).
        - Items in both collections must be hashable; otherwise converting to frozenset will raise a TypeError.

## Returns:
    float:
        The ratio common_count / chosen_count, where:
        - common_count is the number of unique items present in both denominator_sentences and numerator_sentences (set intersection).
        - chosen_count is the number of unique items in denominator_sentences.
        Behavior details and edge values:
        - Returns a float in the closed interval [0.0, 1.0].
        - If all denominator items are present in numerator, returns 1.0.
        - If none are present, returns 0.0.
        - The ratio is computed using unique items only (duplicates in input are collapsed before counting).

## Raises:
    ValueError:
        Raised when either numerator_sentences or denominator_sentences is empty after conversion to a set:
        "Both collections have to contain at least 1 sentence."
    TypeError:
        May be raised when attempting to convert the provided iterables to frozenset if any contained item is unhashable (e.g., a list). This is not explicitly raised by the function but is a direct consequence of using frozenset.

## Constraints:
    Preconditions:
        - Both numerator_sentences and denominator_sentences must be iterables of hashable items.
        - Each iterable must contain at least one element.
    Postconditions:
        - No input mutation: inputs are not modified by the function (they are converted to frozensets internally).
        - The returned value is a float between 0.0 and 1.0 inclusive.
        - The function does not perform any I/O or external side effects.

## Side Effects:
    - None. The function performs only in-memory computations and does not read/write files, network, stdout, or mutate external/global state.

## Control Flow:
flowchart TD
    Start --> ConvertToSet
    ConvertToSet --> CheckEmpty
    CheckEmpty -- any empty --> RaiseValueError
    CheckEmpty -- both non-empty --> ComputeIntersection
    ComputeIntersection --> ComputeCounts
    ComputeCounts --> AssertDenominatorNonZero
    AssertDenominatorNonZero --> ReturnRatio
    RaiseValueError --> End
    ReturnRatio --> End

## Examples:
- Basic overlap:
    numerator = ['s1', 's2', 's3']
    denominator = ['s2', 's4']
    Result: _divide_evaluation(numerator, denominator) -> 1/2 -> 0.5

- Duplicates collapsed:
    numerator = ['s1', 's1', 's2']
    denominator = ['s1', 's1']
    After set conversion both become {'s1','s2'} and {'s1'} respectively,
    Result -> 1.0

- Empty collection handling:
    numerator = []
    denominator = ['s1']
    Result -> raises ValueError("Both collections have to contain at least 1 sentence.")

- Unhashable items:
    numerator = [['a'], ['b']]   (lists are unhashable)
    denominator = [['a']]
    Result -> TypeError raised during conversion to frozenset (items must be hashable)

