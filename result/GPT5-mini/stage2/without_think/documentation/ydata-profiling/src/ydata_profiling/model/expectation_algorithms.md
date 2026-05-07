# `expectation_algorithms.py`

## `src.ydata_profiling.model.expectation_algorithms.generic_expectations` · *function*

## Summary:
Apply a small, rule-based set of Great Expectations to a single column based on its precomputed summary and return the unchanged (name, summary, batch) tuple after mutating the batch with expectation calls.

## Description:
This helper centralizes three generic expectations that commonly apply to many columns:
- Always assert that the column exists on the batch.
- If the column has zero missing values, assert values are not null.
- If the column is fully unique (p_unique == 1.0), assert values are unique.

Known callers:
- No direct callers were found in the provided memory snapshot. Typical usage is from a dataset-profiling stage that maps per-column summary statistics to Great Expectations expectations (i.e., a profiling-to-expectation builder pipeline).

Reason for extraction:
- Keeps simple, repeatable mapping logic in one place so higher-level profiling code can compose column-specific rules without duplicating the conditional expectation logic.

## Args:
    name (str)
        Column identifier on which to apply expectations. Must be a valid column name for the provided `batch`.
    summary (dict)
        Mapping of precomputed per-column statistics. This function expects at least:
            - "n_missing": numeric count of missing values (0 indicates no missing data).
            - "p_unique": numeric proportion of unique values (1.0 indicates all values are unique).
        The function accesses these keys directly (summary["n_missing"], summary["p_unique"]); missing keys raise KeyError.
    batch (Any)
        An object that implements the called Great Expectations-style methods:
            - expect_column_to_exist(name)
            - expect_column_values_to_not_be_null(name)
            - expect_column_values_to_be_unique(name)
        The function ignores the return values of these calls and relies on their side effects on `batch` (e.g., adding expectations to a suite).
    *args
        Additional positional arguments are accepted for compatibility with generic call signatures but are ignored.

Interdependencies:
- The p_unique check is only meaningful if summary["p_unique"] is numeric. If it is computed with floating-point arithmetic, exact equality to 1.0 can be fragile; see Constraints for guidance.

## Returns:
    Tuple[str, dict, Any]
        The exact (name, summary, batch) inputs are returned unchanged by value (the `batch` object may be mutated by its expectation-method calls). This return shape supports pipeline patterns that pass items through after applying side effects.

## Raises:
    KeyError
        If `summary` does not contain "n_missing" or "p_unique".
    TypeError
        If `summary` is not a subscriptable mapping (e.g., None), or if types inside `summary` do not support the equality/comparison operations used.
    AttributeError
        If `batch` lacks any of the called expectation methods.
    Any exception raised by the called expectation methods
        The expectation calls themselves may raise library-specific exceptions; these propagate to the caller.

## Constraints:
Preconditions:
    - `name` must identify an existing or intended column name for `batch`.
    - `summary` must be a mapping with numeric "n_missing" and "p_unique" entries.
    - `batch` must implement the three expectation methods referenced above.

Postconditions:
    - batch.expect_column_to_exist(name) has been invoked.
    - If summary["n_missing"] == 0, batch.expect_column_values_to_not_be_null(name) has been invoked.
    - If summary["p_unique"] == 1.0, batch.expect_column_values_to_be_unique(name) has been invoked.
    - The function returns (name, summary, batch).

Floating-point caution:
    - When p_unique is computed (floating-point), exact equality summary["p_unique"] == 1.0 may fail when the true value is extremely close to 1.0 (e.g., 0.9999999). If callers compute p_unique via division, validate or normalize that value (for example, round to a fixed number of decimals or compare with a tolerance) before passing it into this function.

Recommended caller-side validations:
    - Normalize or validate summary keys before calling to avoid KeyError and to make p_unique comparisons robust.
    - Ensure `batch` has the required methods to avoid unattractive AttributeError propagation.

## Side Effects:
    - No file, network, or stdout I/O is performed directly.
    - The function mutates external state only via the `batch` object: calling expectation methods will typically add expectations to an expectation suite, modify internal batch state, or register validation rules depending on `batch` implementation.
    - No global state or persistent external resources are modified by this function itself.

## Control Flow:
flowchart TD
    Start --> ExistCall[call expect_column_to_exist(name)]
    ExistCall --> MissingCheck{summary["n_missing"] == 0 ?}
    MissingCheck -- Yes --> NotNullCall[call expect_column_values_to_not_be_null(name)]
    MissingCheck -- No --> SkipNotNull[skip not-null expectation]
    NotNullCall --> UniqueCheck{summary["p_unique"] == 1.0 ?}
    SkipNotNull --> UniqueCheck
    UniqueCheck -- Yes --> UniqueCall[call expect_column_values_to_be_unique(name)]
    UniqueCheck -- No --> SkipUnique[skip unique expectation]
    UniqueCall --> End[return (name, summary, batch)]
    SkipUnique --> End

## Examples:
Basic happy-path (inline call):
generic_expectations("user_id", {"n_missing": 0, "p_unique": 1.0}, ge_batch)

Typical robust caller pattern (validation + error handling; described in steps):
1. Validate/normalize summary:
    - Ensure "n_missing" and "p_unique" keys exist.
    - If p_unique is computed, convert to a float and apply rounding or a tolerance check:
        e.g., treat values >= 0.999999 as 1.0, or round to 6 decimal places.
2. Ensure `batch` implements expectation methods (duck-type check) or handle AttributeError gracefully.
3. Call generic_expectations(name, summary, batch) inside a try/except block to capture and report library-specific errors:
    - Catch KeyError to provide a clearer diagnostic if summary is incomplete.
    - Catch AttributeError to indicate `batch` is not Great Expectations-compatible.
    - Let expectation-method exceptions bubble up or wrap them with contextual information for troubleshooting.

Example error-handling pattern (conceptual):
- If summary is missing required keys, raise a descriptive ValueError before calling.
- If batch lacks required methods, construct or convert an appropriate GE batch object, or log and skip the column.

These practices make behavior deterministic and the profiling pipeline easier to debug when expectation calls fail.

## `src.ydata_profiling.model.expectation_algorithms.numeric_expectations` · *function*

## Summary:
Apply a standard set of Great Expectations expectations for numeric columns to the provided batch and return the (name, summary, batch) triplet. The function enforces numeric types, optional monotonicity, and optional min/max bounds on the column.

## Description:
Known callers within the codebase:
- The profiling/expectation-generation stage that iterates profile summaries for each column and applies column-specific expectation algorithms. This function is intended to be invoked for columns identified as numeric by the profiler.
- Any orchestrator that builds a Great Expectations expectation suite from a column summary (e.g., a "profile to expectations" connector).

Typical trigger:
- Called after a column's summary (statistics and detected properties) has been produced; invoked when the profiler determines the column should be treated as numeric.

Why this logic is extracted:
- Encapsulates numeric-specific expectations (type constraints, monotonicity, bounds) in one place for reusability and testability.
- Keeps the profiler/orchestrator code concise by separating the "what expectations to add for numeric columns" decision logic from the traversal and orchestration logic.

## Args:
    name (str):
        Column name for which expectations are added. Must be the identifier recognized by the batch object.
    summary (dict):
        A mapping of column summary properties used to decide which expectations to add. Expected keys:
          - "monotonic_increase" (bool): If true, add an increasing expectation.
          - "monotonic_increase_strict" (bool): If present, passed as the "strictly" argument when monotonic_increase is true.
          - "monotonic_decrease" (bool): If true, add a decreasing expectation.
          - "monotonic_decrease_strict" (bool): If present, passed as the "strictly" argument when monotonic_decrease is true.
          - "min" (numeric, optional): Inclusive lower bound for expect_column_values_to_be_between when present.
          - "max" (numeric, optional): Inclusive upper bound for expect_column_values_to_be_between when present.
        Notes and constraints:
          - monotonic_* keys are accessed directly (summary["monotonic_increase"]), so they must exist in the dict; otherwise a KeyError will be raised.
          - _strict keys are only read if the corresponding monotonic flag is true; they must exist in that case, or a KeyError will be raised.
          - The function treats non-boolean truthy/falsey values as truthy/falsey (no explicit type coercion is enforced).
    batch (Any):
        Object representing a Great Expectations Batch/DataAsset (or a test stub) exposing the following methods used by this function:
          - expect_column_values_to_be_in_type_list(column, type_list, meta=...)
          - expect_column_values_to_be_increasing(column, strictly=...)
          - expect_column_values_to_be_decreasing(column, strictly=...)
          - expect_column_values_to_be_between(column, min_value=..., max_value=...)
        The function will call these methods; batch is mutated (its expectation suite is modified).

    *args:
        Currently unused; accepted for API compatibility with other expectation algorithm functions.

## Returns:
    Tuple[str, dict, Any]
    - The returned tuple is (name, summary, batch).
    - The batch returned is the same object passed in, mutated by side-effect: expectation calls have been applied to it.
    - There are no alternative return types; the function always returns this 3-tuple unless an exception is raised during execution.

## Raises:
    KeyError:
        - If "monotonic_increase" or "monotonic_decrease" keys are missing from summary (they are accessed directly).
        - If a monotonic_* flag is true but the corresponding monotonic_*_strict key is missing, the subsequent access raises KeyError.
    AttributeError:
        - If the provided batch object does not expose any of the required expectation methods, attribute access will raise AttributeError.
    ImportError:
        - If great_expectations is not installed or ProfilerTypeMapping cannot be imported at runtime, the internal import will raise ImportError.
    Any exception raised by the batch.expect_* methods:
        - The underlying Great Expectations expectation methods may raise their own errors (e.g., validation of arguments); these will propagate.

## Constraints:
Preconditions:
    - summary must be a dict containing at least the keys "monotonic_increase" and "monotonic_decrease" (even if their values are False).
    - name must be a valid column identifier for the batch.
    - batch must implement the expectation methods used by this function.
Postconditions:
    - batch will have had one or more expectations added to its expectation suite corresponding to:
        * a type-list expectation enforcing integer/float types,
        * optionally a monotonic increase or decrease expectation,
        * optionally a between expectation if "min" or "max" appear in summary.
    - The returned tuple (name, summary, batch) is guaranteed after successful execution.

## Side Effects:
    - Mutates the supplied batch by invoking its expect_* methods; the batch's expectation suite or internal state will be changed.
    - No file I/O, network calls, stdout/stderr writes, or global state modifications are performed by this function itself.
    - External service calls: none directly; however, the batch implementation may perform side effects when adding expectations (depending on user-provided Batch/DataAsset implementation).

## Control Flow:
flowchart TD
    Start --> ImportProfiler
    ImportProfiler --> BuildTypeList
    BuildTypeList --> ExpectTypeList
    ExpectTypeList --> CheckMonotonicIncrease
    CheckMonotonicIncrease -->|True| ExpectIncreasing
    CheckMonotonicIncrease -->|False| CheckMonotonicDecrease
    ExpectIncreasing --> CheckMonotonicDecrease
    CheckMonotonicDecrease -->|True| ExpectDecreasing
    CheckMonotonicDecrease -->|False| CheckMinMax
    ExpectDecreasing --> CheckMinMax
    CheckMinMax -->|min or max present| ExpectBetween
    CheckMinMax -->|neither present| Return
    ExpectBetween --> Return
    Return --> End

## Examples:
Typical happy-path usage (conceptual; batch must supply the required methods):
- Given a column summary that detected monotonic increase and bounds:
    name = "age"
    summary = {
        "monotonic_increase": True,
        "monotonic_increase_strict": False,
        "monotonic_decrease": False,
        "min": 0,
        "max": 120
    }
    numeric_expectations(name, summary, batch)
  Result:
    - batch.expect_column_values_to_be_in_type_list("age", [...numeric types...], meta={...}) is called.
    - batch.expect_column_values_to_be_increasing("age", strictly=False) is called.
    - batch.expect_column_values_to_be_between("age", min_value=0, max_value=120) is called.
    - Function returns ("age", summary, batch) with the batch mutated to include these expectations.

Error handling example:
- If the summary omits monotonic flags:
    summary = {"min": 0, "max": 10}
    Calling numeric_expectations(name, summary, batch) will raise KeyError because the function expects summary["monotonic_increase"] and summary["monotonic_decrease"] to exist.
- To guard against this, ensure the profiler always includes monotonic flags (False when not detected), or wrap the call:
    try:
        numeric_expectations(name, summary, batch)
    except KeyError as e:
        handle_missing_summary_key(e)

Implementation notes for reimplementation:
- ProfilerTypeMapping.INT_TYPE_NAMES and .FLOAT_TYPE_NAMES are concatenated to produce the allowed numeric types list.
- Use meta={"notes": {"format": "markdown", "content": ["The column values should be stored in one of these types."]}} when adding the type-list expectation.
- Only call increasing/decreasing expectation if the corresponding boolean flag in summary is truthy; pass strictly=summary["monotonic_increase_strict"] (or monotonic_decrease_strict) when doing so.
- Only call between expectation if at least one of "min" or "max" exists in summary (use summary.get("min") and summary.get("max") when calling to allow None).

## `src.ydata_profiling.model.expectation_algorithms.categorical_expectations` · *function*

## Summary:
Determines whether to add a Great Expectations "values to be in set" expectation for a categorical-like column and, if so, instructs the provided batch object to register that expectation using the observed distinct values.

## Description:
This function inspects summary statistics for a single column (number of distinct values and proportion distinct). If the column appears categorical by either having a small absolute number of distinct values or a low proportion of distinct values, the function calls the batch object's expect_column_values_to_be_in_set with the observed non-NaN values.

Known callers:
- Not present in this single-file snippet. In the profiling pipeline this function is intended to be invoked per-column by a module that maps column summaries to expectation-generating functions (i.e., the part of the profiler that builds expectations for each column based on its summary statistics).

Why this logic is extracted:
- Responsibility boundary: encapsulates the decision rule and the single side effect (adding a Great Expectations expectation) for categorical-like columns, keeping profiling/summary-to-expectation mapping modular and testable. This makes it easy to reuse or replace the categorical heuristic without altering higher-level profiling orchestration.

## Args:
    name (str):
        Column name (identifier) for which expectations will be generated. Must be a valid key or identifier understood by the batch object.
    summary (dict):
        Column summary dictionary expected to include the following keys:
            - "n_distinct" (int): count of distinct (unique) values in the column (including or excluding NaNs as used by upstream summary).
            - "p_distinct" (float): proportion (0.0-1.0) of distinct values relative to total non-null rows.
            - "value_counts_without_nan" (mapping): mapping-like object (e.g., dict) whose keys are the distinct non-NaN values observed in the column; keys will be used to form the allowed set.
        Types and presence of these keys are required for correct behavior; see Constraints for details.
    batch (Any):
        An object representing a Great Expectations "batch" (or a compatible object) that must implement:
            expect_column_values_to_be_in_set(column_name: str, value_set: set)
        The function will call that method when the categorical heuristic is triggered.
    *args:
        Additional positional arguments are accepted but ignored by this function.

## Returns:
    Tuple[str, dict, Any]: The function returns the input triple (name, summary, batch) unchanged.
    - This return is intended to allow chaining in pipelines that thread (column_name, summary, batch) through multiple expectation-algorithm functions.

## Raises:
    KeyError:
        If summary is missing any of the required keys ("n_distinct", "p_distinct", "value_counts_without_nan"), a KeyError will be raised when the missing key is accessed.
    TypeError:
        If summary["n_distinct"] or summary["p_distinct"] are not comparable to numeric thresholds (e.g., non-numeric types), comparisons may raise TypeError.
    AttributeError:
        If the provided batch object does not implement expect_column_values_to_be_in_set, an AttributeError will be raised when attempting to call it.
    Any exceptions raised by batch.expect_column_values_to_be_in_set will propagate unchanged.

## Constraints:
Preconditions:
- summary must be a mapping with keys:
    - "n_distinct": integer-like count of distinct values
    - "p_distinct": float-like proportion in [0.0, 1.0]
    - "value_counts_without_nan": mapping from observed (non-NaN) values to counts
- name must be a valid column identifier recognized by batch.
- batch must implement expect_column_values_to_be_in_set(column_name, value_set).
- The function assumes value_counts_without_nan.keys() yields all allowable non-null values to include in the set.

Postconditions:
- The input values (name, summary, batch) are returned unchanged.
- If either summary["n_distinct"] < 10 OR summary["p_distinct"] < 0.2 is true, then batch.expect_column_values_to_be_in_set(name, allowed_set) will have been invoked with allowed_set equal to the set of keys from summary["value_counts_without_nan"].
- No new local or global variables are persisted by this function beyond the side effect on batch.

## Side Effects:
- Calls batch.expect_column_values_to_be_in_set(name, allowed_set) when the categorical heuristic triggers. This mutates the state of the batch object (for example, by adding an expectation) or otherwise triggers whatever side effects that method implements.
- No file I/O, network I/O, stdout/stderr printing, or global state mutation occurs within this function itself.

## Control Flow:
flowchart TD
    A[Start] --> B{summary contains keys?}
    B -- No --> E[KeyError raised when missing key is accessed]
    B -- Yes --> C{summary["n_distinct"] < 10 OR summary["p_distinct"] < 0.2 ?}
    C -- True --> D[Call batch.expect_column_values_to_be_in_set(name, set(summary["value_counts_without_nan"].keys()))]
    C -- False --> F[Do nothing]
    D --> G[Return (name, summary, batch)]
    F --> G

## Examples (prose):
- Typical successful usage in profiling:
    1. A profiling loop produces a summary dict for the column "country" containing n_distinct=7, p_distinct=0.01, and value_counts_without_nan mapping observed countries to counts.
    2. The pipeline calls this function with name="country", the summary, and the current batch object.
    3. Because n_distinct (7) < 10, the function calls batch.expect_column_values_to_be_in_set("country", {"US","CA","MX",...}).
    4. The function returns the original tuple to allow chaining additional expectation generation functions.

- Handling missing summary keys:
    - If the upstream summarizer omitted "p_distinct", calling this function will raise KeyError at the first access. The caller should validate or populate summary keys before invoking this helper.

- Handling non-Great-Expectations batch objects:
    - If batch is a stub used in testing, ensure it exposes expect_column_values_to_be_in_set to avoid AttributeError.

## `src.ydata_profiling.model.expectation_algorithms.path_expectations` · *function*

## Summary:
Returns its inputs (name, summary, batch) unchanged — a no-op adapter that conforms to an expectation-algorithm callable signature.

## Description:
This function implements a minimal, identity-style expectation algorithm interface: it accepts a name, a summary dict, a batch object, and any additional arguments, and returns a 3-tuple (name, summary, batch) without modification.

Known callers within the provided repository snapshot:
- No call sites were found in the provided code context. If present in the full project, this function is typically used as a default or passthrough expectation builder in pipelines that expect a callable with signature (name, summary, batch, *args) and a return of (name, summary, batch).

Why this logic is extracted:
- It enforces a stable, documented interface (input and output shape) for expectation-algorithm plugins or callbacks while providing a safe no-op fallback. Keeping this logic separate avoids inlining trivial passthrough behavior and makes it explicit when a pipeline wants a no-op expectation algorithm.

## Args:
    name (str): Identifier for the expectation or the dataset element being processed. No internal validation is performed.
    summary (dict): A dictionary summarizing computed statistics or metrics for the named entity. The function does not mutate or validate this dict.
    batch (Any): An opaque batch object representing the data context. Can be any type; the function returns it unchanged.
    *args: Additional positional arguments are accepted for API compatibility but are ignored by this function.

Interdependencies:
- There are no interdependencies between parameters in this function; each argument is passed through and returned as-is.

## Returns:
    Tuple[str, dict, Any]: A 3-tuple containing exactly (name, summary, batch) — the same objects passed in, in the same order.
    - No transformation or deep copy is performed; returned values are the same object references provided as inputs.
    - There are no alternative or sentinel return values.

## Raises:
    - This function does not raise any exceptions by itself.
    - Exceptions may still propagate from caller-provided objects if they implement behavior during evaluation (none occurs in the function as written).

## Constraints:
Preconditions:
    - None enforced by the function. Callers should ensure that 'name' being a str and 'summary' being a dict are satisfied if later stages rely on those types.

Postconditions:
    - The function will return a tuple of length 3 containing the same object references provided as arguments.
    - No mutation of the inputs is performed by this function.

## Side Effects:
    - None. The function performs no I/O, no network calls, and does not mutate external state or global variables.

## Control Flow:
flowchart TD
    Start(["Start"]) --> ReceiveInputs["Receive inputs: name, summary, batch, *args"]
    ReceiveInputs --> ReturnTuple["Return (name, summary, batch)"]
    ReturnTuple --> End(["End"])

## Examples:
Typical usage (conceptual, showing input -> output):

- Example 1: Basic passthrough
    Input:
        name = "column_A"
        summary = {"count": 100, "nulls": 3}
        batch = <BatchObject>
    Output:
        ("column_A", {"count": 100, "nulls": 3}, <BatchObject>)

- Example 2: Called from a pipeline expecting an expectation-algorithm callable
    Context:
        A profiling pipeline invokes a list of expectation algorithms, each expected to accept (name, summary, batch, *args) and return (name, summary, batch).
    Behavior:
        Using this function in the list results in a no-op contribution — the pipeline receives the same name, summary, and batch objects unmodified.

Notes:
    - Because this is an identity/passthrough implementation, prefer it when you need a placeholder algorithm or when debugging pipelines to isolate changes introduced by other expectation functions.

## `src.ydata_profiling.model.expectation_algorithms.datetime_expectations` · *function*

## Summary:
If the column summary dictionary contains "min" or "max", invoke the Great Expectations batch to add a between-expectation for the named datetime column; always return the original (name, summary, batch) tuple.

## Description:
This function checks whether the summary mapping contains either the key "min" or the key "max". If at least one of those keys is present (membership test), it calls batch.expect_column_values_to_be_between with:
- the column identifier (name) as the first argument,
- min_value set to summary.get("min"),
- max_value set to summary.get("max"),
- parse_strings_as_datetimes set to True.

The function does not validate, normalize, or otherwise transform summary values; its sole responsibility is to translate the presence of summary bounds into a single call on the provided batch object. No iteration or additional side effects are performed.

Known callers in provided context:
- None in the provided source snippet. The function is self-contained and intended to be used wherever per-column expectation builders are invoked; the exact call sites are not present in the supplied code.

Why extracted:
- Encapsulates the single translation step from summary bounds to a Great Expectations between-expectation call, keeping this concern separate from iteration or summary generation logic.

## Args:
    name (str):
        Column identifier forwarded as the column argument to the batch method.
    summary (dict):
        Mapping in which membership for the keys "min" and/or "max" is tested.
        - The function uses summary.get("min") and summary.get("max") to supply values to the batch call.
        - Presence of a key (even if its value is None) triggers the expectation call because the membership check is used.
        - If a key is absent, summary.get(...) returns None and that None will be passed as the corresponding parameter when the batch call occurs.
    batch (Any):
        Object expected to implement the method:
            expect_column_values_to_be_between(column, min_value=..., max_value=..., parse_strings_as_datetimes=...)
        The function invokes that method when appropriate; otherwise batch is left untouched.
    *args:
        Additional positional arguments are accepted and ignored. They exist only to preserve a broader callable signature.

## Returns:
    Tuple[str, dict, Any]:
        A tuple (name, summary, batch) returning the identical objects passed in.
        - If the batch method was called, batch may be mutated by that method; the function itself does not construct or replace these objects.

## Raises:
    The function does not raise exceptions by itself. Exceptions that may propagate:
    - AttributeError if batch does not provide expect_column_values_to_be_between.
    - Any exception raised by batch.expect_column_values_to_be_between (e.g., validation, type, runtime errors) will propagate to the caller.

## Constraints:
    Preconditions:
        - summary must support membership testing (the "in" operator) and the .get method.
        - batch must implement expect_column_values_to_be_between with the keyword parameters used in the call.
        - name should be a valid column identifier for the batch context (the function makes no check; failures will originate from the batch method).
    Postconditions:
        - If at least one of "min" or "max" keys existed in summary, batch.expect_column_values_to_be_between(...) will have been invoked with the exact keyword arguments shown in Description.
        - If neither key existed, no method on batch is called.
        - The returned tuple uses the same object identities as the inputs.

## Side Effects:
    - Calls batch.expect_column_values_to_be_between(...) when a key is present; any side effects are those performed by that method (typically registering an expectation in Great Expectations).
    - The function itself performs no I/O, network access, file writes, or global state mutation.

## Control Flow:
flowchart TD
    Start[Start: datetime_expectations(name, summary, batch, *args)] --> Check{"min" in summary OR "max" in summary?}
    Check -- No --> ReturnNoCall[Return (name, summary, batch) without calling batch]
    Check -- Yes --> CallBatch[Call batch.expect_column_values_to_be_between(name, min_value=summary.get("min"), max_value=summary.get("max"), parse_strings_as_datetimes=True)]
    CallBatch --> ReturnAfterCall[Return (name, summary, batch) after batch method call]

## Examples:
- Both keys present (values forwarded as-is):
    Given summary contains "min" and "max", the function calls batch.expect_column_values_to_be_between with min_value equal to summary.get("min") and max_value equal to summary.get("max"), and parse_strings_as_datetimes=True; then returns (name, summary, batch).

- Only "max" present:
    Given summary contains "max" but not "min", the function calls batch.expect_column_values_to_be_between with min_value=None and max_value equal to summary.get("max"), and parse_strings_as_datetimes=True; then returns inputs.

- Key present with value None:
    Given summary contains "min" with value None (i.e., "min" in summary is True), the membership test triggers the call; summary.get("min") returns None and None is passed as min_value to the batch method.

- No keys present:
    Given summary lacks both "min" and "max", the function makes no call on batch and returns (name, summary, batch) unchanged.

## `src.ydata_profiling.model.expectation_algorithms.image_expectations` · *function*

## Summary:
Returns the provided name, summary, and batch tuple unchanged; acts as a simple pass-through adapter for image expectation pipelines.

## Description:
This function accepts a canonical trio of parameters used by higher-level expectation/profile code (a string identifier, a dictionary summary, and an arbitrary batch object) and returns them unchanged as a tuple. In the provided source context this is the entire function body — no transformation, validation, or side effects are performed.

Known callers within the provided context:
- No direct callers were identified in the supplied file or pre-loaded context. Treat this function as a small adapter or placeholder that can be called by expectation-building pipelines or profiling orchestrators which expect a (name, summary, batch) signature.

Responsibility boundary:
- Responsibility is solely to relay the given inputs back to the caller in the expected tuple shape (name, summary, batch). Any validation, mutation, or processing of these objects is intentionally outside this function's scope.

## Args:
    name (str): A string identifier for the expectation or image field. Expected to be a textual name but not validated at runtime.
    summary (dict): A dictionary containing computed summary statistics or metadata about the image(s). The function does not inspect or mutate this dict.
    batch (Any): An opaque batch object representing the image data, dataset partition, or data loader; type and structure are not enforced.
    *args: Additional positional arguments are accepted but ignored. They are included only to allow flexible call signatures from callers that pass extra context.

Notes on interdependencies:
- The function does not enforce or depend on specific contents of summary or batch. Type hints document intended types but there is no runtime type checking or coercion.

## Returns:
    Tuple[str, dict, Any]: A 3-tuple containing (name, summary, batch) — the exact objects passed in (no copies are made by the function).
    - Normal return: returns the same object references provided as inputs.
    - Edge cases: If callers pass unexpected types (e.g., name not a str), the function will still return the inputs unchanged; no type errors are raised by this function itself.

## Raises:
    - This function does not raise any exceptions directly.
    - Any exceptions that originate from external code (e.g., if callers compute the arguments prior to calling) are not handled here.

## Constraints:
Preconditions:
    - None enforced programmatically. Callers should supply:
        * name as a string (for semantic correctness),
        * summary as a dict of summary statistics/metadata,
        * batch as the batch-like object the rest of the pipeline expects.
Postconditions:
    - The function returns immediately and guarantees the output is a tuple of length 3 where:
        index 0 is the original name object,
        index 1 is the original summary dict object,
        index 2 is the original batch object.

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and does not mutate the provided inputs.

## Control Flow:
flowchart TD
    Start([Start])
    ReceiveInputs[/Receive (name, summary, batch, *args)/]
    IgnoreArgs[/Ignore extra *args/]
    ReturnResult([Return (name, summary, batch)])
    Start --> ReceiveInputs --> IgnoreArgs --> ReturnResult

## Examples:
Example 1 — Basic usage (happy path):
    # Given
    name = "image_column"
    summary = {"width_mean": 640, "height_mean": 480}
    batch = {"data": b"...", "count": 128}
    # Call
    result = image_expectations(name, summary, batch)
    # Result
    # result == ("image_column", {"width_mean": 640, "height_mean": 480}, {"data": b"...", "count": 128})

Example 2 — Extra args are ignored:
    # Given extra context passed by a caller
    context = {"profile_id": 123}
    result = image_expectations("img", {}, batch, context)
    # Result
    # result == ("img", {}, batch)
    # Note: the context argument is ignored by this function.

Example 3 — Non-standard types (no validation performed):
    result = image_expectations(42, ["unexpected", "summary"], None)
    # Result
    # result == (42, ["unexpected", "summary"], None)
    # No exception is raised by this function; callers are expected to ensure types are appropriate for downstream consumers.

## `src.ydata_profiling.model.expectation_algorithms.url_expectations` · *function*

## Summary:
Returns the provided name, summary, and batch values unchanged as a 3-tuple — acts as a placeholder/passthrough for URL-related expectation generation.

## Description:
This function is a minimal passthrough intended as the URL-specific expectation algorithm hook. It accepts a column identifier, its summary metadata, and the current batch object and returns them unchanged.

Known callers:
- No internal callers were identified in the provided repository snapshot. In typical usage within profiling pipelines, this function would be invoked by an expectation-generation orchestrator or a Great Expectations integration layer that enumerates column-specific expectation generators.

Why this logic is extracted:
- The function exists to provide a clear, replaceable boundary for URL-related expectation logic. Extracting it into its own function allows:
  - Future extension to implement URL-specific checks (e.g., pattern/regex expectations, valid URL parsing).
  - Easier testing and mocking when building expectation profiles.
  - A consistent API that other expectation-generating functions follow.

## Args:
    name (str): Identifier for the column or feature under inspection (for example, a column name). Required.
    summary (dict): Aggregated metadata about the column (e.g., counts, sample values, inferred types). The function does not inspect or mutate this dict; it forwards it as-is.
    batch (Any): The batch object or context passed by the profiling pipeline (type is intentionally generic; could be a data batch, dataframe slice, or pipeline context object). Required.
    *args: Variadic positional arguments — accepted for API compatibility with other expectation algorithm signatures; ignored by this implementation.

Interdependencies:
- There are no interdependencies between parameters enforced by this function. It simply forwards the positional arguments.

## Returns:
tuple[str, dict, Any]: A 3-tuple containing:
    - The original name argument (str).
    - The original summary argument (dict).
    - The original batch argument (Any).

Edge cases:
- If callers pass mutated objects for summary or batch, the returned tuple will contain references to those same objects (no defensive copy is made).
- If any argument is None, that None is returned in the corresponding tuple position.

## Raises:
- This function does not raise any exceptions directly.
- Indirect exceptions can occur if the caller's evaluation of the returned values triggers errors (for example, downstream code expecting non-None values).

## Constraints:
Preconditions:
    - The caller should pass three positional arguments with the intended semantics: a string name, a dict-like summary, and a batch/context object. The function does not validate types at runtime.
Postconditions:
    - The returned tuple contains exactly the three provided inputs in the same order and without modification.
    - No side-effecting state is modified by this function.

## Side Effects:
- None intrinsic to this function: no I/O, no network access, no global state mutation, and no logging.
- It returns references to the inputs; if those inputs are mutable and later mutated by the caller, those mutations affect the original objects.

## Control Flow:
flowchart TD
    Start --> ReceiveInputs[name, summary, batch, *args]
    ReceiveInputs --> ReturnTuple["Return (name, summary, batch)"]
    ReturnTuple --> End

## Examples:
Typical usage scenario (described in prose):
- A profiling orchestrator iterates over dataset columns. For a column identified as potentially containing URLs, it calls this function to obtain the inputs for a URL-expectation generator pipeline. With the current implementation, the call simply forwards the values, so downstream code receives the same name, summary, and batch objects and proceeds with expectation construction or further analysis.

Concrete example (behavior description, not source):
- Caller supplies name = "website", summary = {"count": 100, "unique": 80}, batch = <Batch object>.
- The function returns ("website", {"count": 100, "unique": 80}, <Batch object>).
- No validation occurs; if the caller expected the function to add URL-specific expectations, that would require implementing that logic in this function in future.

Notes for future implementers:
- If URL-specific expectation logic is added, ensure to:
    - Preserve the API contract (return a 3-tuple of name, summary, batch or document any change).
    - Decide whether to mutate summary in-place (documented) or return a modified copy.
    - Add deterministic behavior and raise clear exceptions for invalid inputs if validation is required.

## `src.ydata_profiling.model.expectation_algorithms.file_expectations` · *function*

## Summary:
Invokes a Great Expectations file-level expectation on the provided batch for the given file name and returns the unchanged inputs.

## Description:
This small utility calls the batch's expect_file_to_exist method with the provided name to assert that a file exists according to the batch's Great Expectations engine. It does not modify the inputs; it merely triggers the expectation check on the batch object.

Known callers within this codebase:
- No callers were found in the available repository memory snapshot. This function is intended to be used in profiling pipelines where file-level expectations are executed on a batch/datasource object before or during profiling.

Why this logic is extracted:
- Extracting the single expectation call into its own function separates expectation orchestration from higher-level profiling logic. It enforces a clear responsibility boundary: this function is responsible only for invoking file existence expectations and returning the pipeline tuple (name, summary, batch). This makes it easier to plug, reuse, or mock the expectation call in tests or when composing multiple expectation algorithms.

## Args:
    name (str): The file identifier to check. Expected to be a filename or path fragment as understood by the batch.expect_file_to_exist implementation. No validation is performed here.
    summary (dict): Arbitrary metadata or accumulated summary information passed through the expectation pipeline. This function does not read or mutate the dictionary.
    batch (Any): An object that must implement a method expect_file_to_exist(name). Typically this is a Great Expectations Batch or Dataset-like object provided by the profiling pipeline.
    *args: Additional positional arguments are accepted for API compatibility but are ignored by this function.

Interdependencies:
- The only runtime dependency is that batch implements the expect_file_to_exist(name) method and behaves according to Great Expectations expectations semantics.

## Returns:
    Tuple[str, dict, Any]: A 3-tuple containing:
        - The same name value passed in (str).
        - The same summary dictionary passed in (dict).
        - The same batch object passed in (Any).

Edge-case returns:
- The function always returns the inputs unchanged if it completes normally. If the called expectation raises an exception, this function does not catch it and will not return.

## Raises:
    AttributeError: If the batch object does not implement expect_file_to_exist, an AttributeError will be raised when attempting to access the attribute.
    Any exception raised by batch.expect_file_to_exist: The function propagates any exception raised by the underlying expectation call (for example, validation failures or internal errors inside the batch/Great Expectations engine). No exceptions are caught or transformed here.

## Constraints:
Preconditions:
    - name must be a value the batch.expect_file_to_exist implementation accepts (commonly a string).
    - batch must be a non-null object exposing expect_file_to_exist(name).

Postconditions:
    - If the function returns normally, the expectation has been invoked on batch for the provided name.
    - The returned tuple contains the original name, summary, and batch objects (identity preserved).

## Side Effects:
    - Invokes batch.expect_file_to_exist(name), which may:
        * Record validation results within the batch/Great Expectations state.
        * Emit logs or metrics via the Great Expectations infrastructure.
        * Potentially mutate internal state of batch (depending on implementation).
    - No file I/O, network calls, or global state mutations are performed by this function itself; any I/O or external interactions are indirect effects of the batch.expect_file_to_exist implementation.

## Control Flow:
flowchart TD
    Start([Start])
    CallExpect[/"Call batch.expect_file_to_exist(name)"/]
    Success{Expectation call\ncompleted without raising}
    Error{Exception raised by\nexpectation call}
    Return[/"Return (name, summary, batch)"/]
    Propagate[/"Propagate exception to caller"/]
    Start --> CallExpect
    CallExpect -->|no exception| Success
    CallExpect -->|exception| Error
    Success --> Return
    Error --> Propagate

## Examples (usage pattern described, no direct code included):
- Typical pipeline usage:
    1. Obtain a Great Expectations batch/dataset object that represents file-based data (for example, a Batch for a CSV file or a FileDataset wrapper).
    2. Pass the file name (or identifier), a summary dictionary, and the batch object to this function as part of an expectation-algorithm pipeline.
    3. If the file exists according to the batch, the function returns the (name, summary, batch) tuple to allow downstream steps to continue.
    4. If the expectation fails or the batch raises an error, that exception propagates to the caller; the caller should catch and handle validation failures or missing-method errors as appropriate (for example, logging the failure or marking the profile run as invalid).

- Error handling guidance:
    - Wrap the call in a try/except block at the pipeline level if you need to continue profiling on other files when a single file expectation fails.
    - If you expect batches that might not implement expect_file_to_exist, check for the attribute or handle AttributeError to provide a clearer error message.

