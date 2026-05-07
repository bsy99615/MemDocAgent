# `typeset_relations.py`

## `src.ydata_profiling.model.typeset_relations.is_nullable` · *function*

## Summary:
Return True when the provided pandas Series contains at least one non-null (non-NA) value; otherwise return False.

## Description:
This function examines a pandas Series and reports whether there exists at least one non-null element. It implements a single, small predicate used to decide a "nullable" relation for a series within a typeset/type-detection pipeline.

Known callers:
- No direct callers were discovered in the provided code snapshot. In the codebase this function is intended to be used by predicates or rules that evaluate relations (e.g., "nullable" relation checks) for a Series during profiling or type-inference stages.

Why this logic is extracted:
- The check is small but conceptually distinct (a predicate on a Series). Extracting it to a dedicated function:
  - Makes the intent explicit and testable.
  - Provides a stable interface for the broader typeset/relations machinery, which may pass a shared `state` dict for consistency with other relation predicates.
  - Allows substitution or extension (e.g., more complex nullability rules) without changing call sites.

## Args:
    series (pandas.Series):
        The pandas Series to evaluate. Expected to implement the pandas Series API, specifically the count() method which returns the number of non-NA values.
    state (dict):
        A dictionary intended for carrying state between predicate calls. In this implementation the parameter is accepted for API compatibility but is not read or modified.

## Returns:
    bool:
        True if series.count() > 0, i.e., the Series contains at least one non-null (non-NA) value.
        False if series.count() == 0, i.e., the Series is empty or all values are NA/NULL.

    Possible return scenarios:
    - True: Series has one or more non-null entries (e.g., [1, NaN] -> True).
    - False: Series is empty (length 0) or all entries are null/NA (e.g., [NaN, None] -> False).

## Raises:
    No exceptions are raised explicitly by this function.
    Potential runtime exceptions that can occur due to invalid inputs:
    - AttributeError: if `series` does not have a `count` attribute (e.g., series is None or not a pandas Series-like object).
    - Any exception propagated from pandas.Series.count(), for example if a broken custom Series-like object raises inside count().

## Constraints:
    Preconditions:
    - `series` should be a pandas.Series or a Series-like object providing a count() method that returns the number of non-NA observations as an integer.
    - `state` should be a dict if callers expect to reuse it across predicates; however, this function does not inspect or mutate it.

    Postconditions:
    - The function returns a boolean and makes no modifications to `series` or `state`.
    - No external side effects are performed.

## Side Effects:
    - None. The function does not perform I/O, network calls, global state mutation, database writes, or caching.
    - It does not mutate the input Series or the provided `state` dict.

## Control Flow:
flowchart TD
    Start([Start]) --> ComputeCount{Call series.count()}
    ComputeCount --> IsPositive{count > 0?}
    IsPositive -- Yes --> ReturnTrue([Return True])
    IsPositive -- No --> ReturnFalse([Return False])

## Examples:
Example 1 — non-empty with non-null value:
    import pandas as pd
    s = pd.Series([1, None, numpy.nan])
    result = is_nullable(s, {})
    # result == True because there is one non-null value (1)

Example 2 — all nulls or empty:
    import pandas as pd
    s_all_null = pd.Series([None, numpy.nan])
    result = is_nullable(s_all_null, {})
    # result == False because there are no non-null values

Example 3 — empty series:
    import pandas as pd
    s_empty = pd.Series([], dtype=float)
    result = is_nullable(s_empty, {})
    # result == False

Notes:
- The function intentionally ignores the `state` parameter; callers may pass a shared state dict to keep a uniform predicate signature across the relations API.
- If you need a different definition of "nullable" (for example, treating certain sentinel values as null or requiring a minimum count threshold), implement a replacement function and keep the same signature for compatibility.

## `src.ydata_profiling.model.typeset_relations.try_func` · *function*

## Summary:
Wraps a predicate-like function so that any exception raised while evaluating it is caught and the wrapper returns False instead, preserving the wrapped function's metadata.

## Description:
This decorator factory returns a wrapper around a function that is expected to accept a pandas Series (and optional args/kwargs) and produce a boolean-like result indicating whether the Series satisfies some relation or property. When invoked, the wrapper will call the original function and return its result; if any exception is raised during that call, the wrapper will suppress the exception and return False.

Known callers within a typical codebase context:
- No explicit call sites were provided with this task. In the repository this lives in (typeset_relations), the intended and common usage is to apply this decorator to individual relation-check functions that accept a pandas Series and return a boolean result (for example, "is_numeric_series" or "is_string_series"). These relation-checking functions are then used by higher-level type-detection logic to decide if a Series belongs to a given type.

Why this logic is extracted as a decorator:
- It centralizes the error-suppression policy used for many small predicate functions that probe properties of Series objects (e.g., dtype checks, element-wise inspections). By wrapping those functions with try_func, callers get a robust boolean reply instead of having to handle exceptions at every call site. This enforces a clear responsibility boundary: the wrapped function handles the actual check, and try_func guarantees a safe boolean outcome even on unexpected input or runtime errors.

## Args:
    fn (Callable): A callable to wrap. Expected signature: fn(series: pandas.Series, *args, **kwargs) -> bool (or bool-like).
        - The wrapper does not validate fn's signature beyond calling it with (series, *args, **kwargs).
        - Interdependency: the caller of the returned wrapper must supply a pandas.Series as the first positional argument; otherwise fn may raise (which will be caught and result in False).

## Returns:
    Callable: A wrapper function with the same metadata as fn (functools.wraps is used). The wrapper has signature inner(series: pandas.Series, *args, **kwargs) -> bool.
    - Normal case: returns whatever fn(series, *args, **kwargs) returns (expected to be bool or bool-like).
    - Exception case: if fn raises any exception when invoked, the wrapper returns False.
    - Note: although the wrapper's annotation is bool, if fn returns a non-bool value (e.g., None or an object), that value will be returned unchanged in the non-exception path.

## Raises:
    - The wrapper is designed not to propagate exceptions raised by fn; therefore, it does not raise exceptions originating from fn.
    - No exceptions are explicitly raised by the wrapper implementation itself.
    - Important: because a bare except is used, system-exiting exceptions such as KeyboardInterrupt and SystemExit will also be caught and suppressed (converted to a False return), which can obscure intended process control signals.

## Constraints:
Preconditions:
    - fn must be a callable.
    - The first argument passed to the returned wrapper should be a pandas.Series (or an object acceptable to fn). If fn cannot handle the provided first argument, it may raise; that exception will be caught and the wrapper will return False.

Postconditions:
    - The wrapper will never allow exceptions raised by fn to propagate; instead, it guarantees that the caller receives a value (either fn's return value or False).
    - Metadata of fn (name, docstring) is preserved via functools.wraps.

## Side Effects:
    - No I/O (no file, network, or stdout interactions) are performed by the wrapper itself.
    - No global state is modified by try_func or the produced wrapper.
    - The only subtle external effect is masking exceptions (including KeyboardInterrupt/SystemExit) that would otherwise propagate and potentially terminate or alter higher-level control flow.

## Control Flow:
flowchart TD
    A[Call wrapper with (series, *args, **kwargs)] --> B{Call fn(series, *args, **kwargs)}
    B -- success --> C[Return fn's result]
    B -- exception (any) --> D[Catch exception]
    D --> E[Return False]

## Examples:
- Typical usage pattern (described):
    1. Define a small predicate function that checks a property of a pandas.Series (for example, inspecting dtype or attempting an operation that may fail on some Series).
    2. Apply this decorator to that function when registering or composing relation checks, so callers can rely on a boolean result instead of requiring try/except at each call site.
    3. When invoking the decorated function, handle the False return value as an indication that either the test failed or an error occurred during evaluation.

- Error-handling scenario (described):
    - Suppose a predicate attempts an operation that can raise (e.g., conversion to numeric). With try_func, if conversion raises for a particular Series, the decorator converts that failure into a False outcome. The caller can then treat False uniformly (e.g., skip that relation) rather than dealing with exceptions.

## `src.ydata_profiling.model.typeset_relations.string_is_bool` · *function*

## Summary:
Returns True when every non-null string element of the given Series (excluding categorical Series) matches one of the provided boolean-string tokens (case-insensitive); otherwise returns False.

## Description:
This predicate is used during typeset/type-detection to determine whether a string Series represents boolean values encoded as text (for example "true"/"false", "yes"/"no"). Typical callers are higher-level type-inference routines that iterate over predicate functions to label a Series' semantic type. The function enforces three responsibilities:
- Exclude categorical-typed Series immediately (categorical Series are not considered string-encoded booleans here).
- Normalize null-handling via the series_handle_nulls decorator (records presence of NaNs in the shared state and drops them before testing; short-circuits to False if the series becomes empty after dropping NaNs).
- Protect against runtime errors within the string-inspection logic via try_func (any exception thrown while performing the string checks is suppressed and treated as test failure / False).

Why this is a separate function:
- Isolates the logic that determines whether textual tokens map to boolean semantics (case-insensitive lookup against a provided mapping), keeping null-handling and exception-safety policies consistent through decorators rather than repeated inline code.

Known callers within the codebase and typical context:
- Invoked by type-detection pipelines that accept a pandas.Series and a shared mutable state dict, where this predicate is one of several checks used to identify whether a Series should be treated as a boolean-like string column. Callers pass a mapping of allowed string tokens (k) and expect a boolean outcome indicating whether the Series matches that mapping.

## Args:
    series (pandas.Series):
        The Series to evaluate. It may contain missing values. The series will be inspected element-wise using the pandas string accessor (series.str).
    state (dict):
        A mutable state dictionary shared across related predicate calls. The series_handle_nulls decorator will populate state["hasnans"] on first invocation and may mutate it (True if any NaNs present in the original series, otherwise False).
    k (Dict[str, bool]):
        A mapping whose keys are the accepted string tokens that represent boolean values (examples: "true", "false", "yes", "no"). Keys are compared case-insensitively because the function lower-cases each element before membership testing. The associated boolean values in k are not used by this function beyond providing the set of accepted tokens (only k.keys() is consulted).

Interdependencies and notes:
- k.keys() is used as the allowed token set; ensure keys are the lower-case canonical tokens or rely on case-insensitive matching performed by the function.
- state must be a mutable mapping (e.g., dict) because it will be assigned state["hasnans"] by the series_handle_nulls decorator if that key is absent.

## Returns:
    bool:
        True if and only if:
          - the series is not a pandas categorical dtype, and
          - after nulls are handled (dropped if state["hasnans"] is True or not present), every remaining element's lower-cased string representation is present in k.keys().
        Otherwise returns False.

Possible return-value scenarios / edge cases:
- False is returned if the series has categorical dtype (early return), if any element (after null-dropping) does not match any key in k (case-insensitive), if the series becomes empty after dropping NaNs (series_handle_nulls short-circuits to False), or if an exception occurs during the string-inspection step (try_func suppresses exceptions and returns False).
- True can be returned for an empty series only in the narrow case when the series is empty and had no NaNs recorded by series_handle_nulls (pandas' .all() on an empty boolean Series yields True). Note: series_handle_nulls only short-circuits empty-result cases when the original series had NaNs and dropna() produces an empty series; an originally empty series with no NaNs will reach the tester and may produce True.

## Raises:
    - The tester's runtime exceptions are suppressed by try_func and converted to a False return; they do not propagate.
    - Exceptions that occur before the tester is invoked (for example from the categorical-type check) will propagate. Concretely:
        * If the categorical-type check (pdt.is_categorical_dtype(series)) raises (e.g., due to an unexpected input type), that exception will propagate.
        * If the provided state is not a mutable mapping and series_handle_nulls tries to assign state["hasnans"], a TypeError may be raised by that decorator and will propagate (series_handle_nulls does not suppress exceptions).

## Constraints:
Preconditions:
    - series should be a pandas.Series (or Series-like object exposing .str, .hasnans, .dropna(), .empty).
    - state must be a mutable mapping (e.g., dict).
    - k should be a mapping with string keys representing accepted boolean tokens.

Postconditions:
    - If the function returns normally, state["hasnans"] will be set (if not already present) to reflect whether the original series contained NaNs.
    - No other global state is modified by this function; its side-effect on state is limited to setting state["hasnans"] via the series_handle_nulls decorator.

## Side Effects:
    - Mutates the provided state mapping by setting state["hasnans"] if it was absent.
    - No file, network, or stdout I/O is performed.
    - Exceptions raised inside the string-testing logic are swallowed (converted to False) by the try_func decorator; exceptions raised prior to the tester are not suppressed.

## Control Flow:
flowchart TD
    Start --> IsCategorical{pdt.is_categorical_dtype(series)?}
    IsCategorical -- Yes --> ReturnFalseCategorical[Return False (categorical series)]
    IsCategorical -- No --> NAHandling[series_handle_nulls applied]
    NAHandling --> SetHasNans{state["hasnans"] present? If not, set state["hasnans"]=series.hasnans}
    SetHasNans --> DropNA{if state["hasnans"] == True then series2 = series.dropna()}
    DropNA --> EmptyAfterDrop{series2.empty?}
    EmptyAfterDrop -- Yes --> ReturnFalseEmpty[Return False (all-NA series)]
    EmptyAfterDrop -- No --> CallTester[Call tester under try_func]
    CallTester --> TrySuccess{tester computes s.str.lower().isin(k.keys()).all()}
    TrySuccess -- True --> ReturnTrue[Return True]
    TrySuccess -- False --> ReturnFalseTest[Return False]
    CallTester --> TryException[Exception in tester -> try_func catches]
    TryException --> ReturnFalseException[Return False]

## Examples:
- Typical usage:
    state = {}
    s = pandas.Series(["True", "FALSE", "true"])
    k = {"true": True, "false": False}
    result = string_is_bool(s, state, k)
    # result == True
    # state["hasnans"] is set to False

- Example with nulls:
    state = {}
    s = pandas.Series(["True", None, "false", numpy.nan])
    k = {"true": True, "false": False}
    result = string_is_bool(s, state, k)
    # series_handle_nulls will set state["hasnans"] = True, drop NaNs, tester runs on ["True","false"]
    # result == True

- Example with categorical dtype:
    state = {}
    s = pandas.Series(pd.Categorical(["true", "false"]))
    k = {"true": True, "false": False}
    result = string_is_bool(s, state, k)
    # result == False (categorical series is excluded early)

- Example with non-string values or mismatched tokens:
    state = {}
    s = pandas.Series([1, 0, 1])         # integers, no .str operations possible
    k = {"true": True, "false": False}
    result = string_is_bool(s, state, k)
    # The string-access operation inside tester will raise or produce non-matches;
    # try_func ensures such internal errors produce False, so result == False

## `src.ydata_profiling.model.typeset_relations.string_to_bool` · *function*

## Summary:
Converts each string in a pandas Series to a boolean by lowercasing the string and looking it up in a provided mapping; values not present in the mapping are left as missing (NaN/NA).

## Description:
This helper performs two simple operations in sequence: normalize string values to lowercase, then map those normalized tokens to boolean values using the provided dictionary.

Known callers within the provided codebase snapshot:
    - No direct callers were discovered in the provided repository snapshot. The function is defined in the typeset relations utilities and is intended to be invoked by pipeline code that classifies or normalizes textual boolean-like tokens (e.g., "yes"/"no", "true"/"false") into actual boolean values.

Why this logic is extracted into its own function:
    - Encapsulates the common pattern of lowercasing and mapping string tokens to booleans so multiple callers can reuse the same, well-documented behavior.
    - Keeps mapping-details (the mapping dictionary) outside of inline code, enabling centralized tests and easier customization of token-to-boolean mappings.
    - Maintains a uniform function signature (series, state, k) compatible with pipeline callbacks where state is passed along even when unused.

## Args:
    series (pandas.Series):
        Input one-dimensional labeled array of values to convert. Typically contains string-like values (object or string dtype), but may contain missing values. The function invokes the pandas string accessor to lowercase each element before mapping.
    state (dict):
        A pipeline state dictionary passed through for signature compatibility. This function does not read or modify it.
    k (Dict[str, bool]):
        A mapping from lowercase string tokens to boolean values. The function lowercases each input value before lookup, so keys in this mapping should be lowercase if they are intended to match.

## Returns:
    pandas.Series:
        A new Series whose i-th element is the mapping result for the lowercased version of the i-th element of the input series. Possible return values:
            - True or False when the lowercased string matches a key in k.
            - Missing value (pandas.NA or numpy.nan) when the lowercased value is not present in k or when the input element is missing / not string-like.
        The returned Series preserves the index of the input series and has the same length.

## Raises:
    - The function does not explicitly raise exceptions in its body, but it may propagate exceptions raised by pandas operations:
        - AttributeError: may occur if the provided `series` object does not support the pandas .str accessor (for example if a non-Series object is passed).
        - TypeError or ValueError: may be raised by pandas Series.str.lower or Series.map if invalid input types are supplied (for example, if `k` is of an unexpected type that Series.map cannot interpret).
    Documented here so callers can handle or validate inputs before calling.

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series (or pandas-compatible Series-like object). The function expects to use the pandas string accessor.
        - Keys in `k` should correspond to lowercased tokens because the function lowercases values before lookup.
    Postconditions:
        - The returned Series has the same length and index as `series`.
        - Every input element is lowercased (conceptually) prior to lookup; therefore, the result depends solely on the lowercased representation of the original values and the mapping `k`.

## Side Effects:
    - None. This function performs no I/O, does not modify external global state, and does not mutate the input Series (it returns a new Series view/result).

## Control Flow:
flowchart TD
    Start[Start]
    A[Receive inputs: series, state, k]
    B[Call series.str.lower()]
    C[Call .map(k) on lowercased series]
    D[Return mapped Series]
    Start --> A --> B --> C --> D

## Examples (illustrative, described without embedding source code):
    Example 1 — Typical usage:
        - Input series values: "Yes", "no", "TRUE", "unknown", missing
        - Mapping k: {"yes": True, "no": False, "true": True}
        - Behavior: each input is lowercased ("yes","no","true","unknown", missing) then looked up in k.
        - Result: mapped booleans where present: True, False, True; "unknown" and missing map to missing (NaN/NA).

    Example 2 — Handling unexpected types:
        - If the input `series` contains non-string objects, pandas' string accessor will produce missing values for entries that cannot be lowercased; those entries will then map to missing after .map(k).
        - If a caller wants to enforce strict behavior (e.g., raise on unknown tokens), validate inputs or post-process the returned Series to detect and handle missing values.

    Example 3 — Signature compatibility in pipelines:
        - The `state` parameter is intentionally present for pipeline compatibility; it can be passed through unchanged by callers that thread a shared state across transformation callbacks.

## `src.ydata_profiling.model.typeset_relations.numeric_is_category` · *function*

## Summary:
Return whether a numeric pandas Series should be treated as a categorical variable because it contains a small number of distinct values (between 1 and a configurable threshold, inclusive).

## Description:
This function determines if a numeric-valued column is "low-cardinality" and therefore better classified as categorical by the profiling/type-inference pipeline.

Known callers within the codebase:
- Not listed in the immediate context provided. Conceptually, this is intended to be called by the dataset profiling/type-detection logic when deciding whether a numeric variable should be considered categorical (for example, from a typeset/relationship detector that evaluates multiple heuristics for variable typing).

Why this is a separate function:
- Encapsulates a single, testable heuristic: the decision that a numeric variable is categorical if its number of unique values is within a configurable low-cardinality threshold.
- Keeps the type-detection pipeline modular, allowing the threshold to be configured centrally via Settings and enabling easy unit testing and reuse.

## Args:
    series (pd.Series):
        The pandas Series to inspect. Expected to be a one-dimensional pandas Series containing numeric or numeric-like values.
        Note: pandas.Series.nunique() is used; by pandas default, NaN/NA values are excluded from the unique count (dropna=True).
    state (dict):
        Context/state dictionary passed through the type-detection pipeline. This function does not read or modify state (parameter present for API compatibility with other detectors).
    k (Settings):
        Global configuration object. The function reads k.vars.num.low_categorical_threshold, which should be an integer-like value defining the maximum number of distinct values for the series to be considered categorical.

Interdependencies:
- The decision depends on the threshold value available at k.vars.num.low_categorical_threshold. If that attribute is missing or not an integer-like value, an exception may be raised when attempting to read or compare it.

## Returns:
    bool:
        True if the series contains at least one unique (non-NA) value and at most k.vars.num.low_categorical_threshold unique (non-NA) values.
        False otherwise.

Possible return cases:
- True: 1 <= series.nunique() <= threshold
- False:
    - series.nunique() == 0 (empty or all-NA series)
    - series.nunique() > threshold
    - threshold < 1 (configuration that makes the predicate impossible)

## Raises:
    AttributeError:
        If the Settings object `k` does not have the attribute chain vars.num.low_categorical_threshold, or if `series` is not a pandas Series and lacks nunique().
    TypeError:
        If `series` is of an unexpected type that causes pandas to raise a TypeError when calling nunique, or if the comparison between n_unique and threshold is invalid due to an incompatible type for threshold.
    Any exceptions thrown by pandas.Series.nunique() may propagate (e.g., if `series` is malformed).

## Constraints:
Preconditions:
- `series` should be a pandas Series (or an object with a nunique() method that behaves like pandas.Series.nunique).
- `k` must expose an integer-like value at k.vars.num.low_categorical_threshold.
- Caller should be prepared to handle False for empty or all-null series.

Postconditions:
- No mutation of `series`, `state`, or `k` is performed.
- The function deterministically returns a boolean based solely on the unique-value count and configuration threshold.

## Side Effects:
- None. The function performs no I/O, does not mutate inputs, and makes no external service calls.

## Control Flow:
flowchart TD
    A[Start: receive series, state, k] --> B[Compute n_unique = series.nunique()]
    B --> C[Read threshold = k.vars.num.low_categorical_threshold]
    C --> D{Is 1 <= n_unique <= threshold?}
    D -->|Yes| E[Return True]
    D -->|No| F[Return False]

## Examples (usage and edge cases, described in prose):
- Typical use: Call during type-detection for a numeric column. If the series has 3 distinct values and the configured low_categorical_threshold is 5, the function returns True and the column may be treated as categorical by downstream logic.
- Empty or all-null series: series.nunique() returns 0, so the function returns False.
- Threshold misconfiguration: If k.vars.num.low_categorical_threshold == 0, the function will always return False because the lower bound requires at least 1 unique value.
- Robustness note: Since `state` is unused here, callers may pass a pipeline state dict for signature compatibility; the function will ignore it.

## `src.ydata_profiling.model.typeset_relations.to_category` · *function*

## Summary:
Convert a pandas Series into the pandas nullable string dtype while ensuring values that represented missingness after an intermediate string cast are restored to real missing values.

## Description:
This helper normalizes a column to a textual (nullable) pandas string Series. Implementation steps:
1. Record whether the original Series contained any missing values (series.hasnans).
2. Cast all values to Python strings (series.astype(str)).
3. If the original Series had any missing values, replace the literal strings "nan" and "<NA>" in the whole Series with an actual missing marker (NumPy NaN, np.nan).
4. Cast the result to the pandas nullable "string" dtype and return it.

Known callers within the provided snapshot:
    - No explicit callers were found in the provided project snapshot. The function is intended for use in data profiling/type-conversion pipelines where columns should be coerced to a consistent textual representation (for example, canonicalizing categorical/text columns prior to profiling or relation detection).

Why this logic is extracted:
    - The function encapsulates a subtle two-step conversion pattern required to avoid turning originally-missing values into the literal strings "nan" or "<NA>" after casting to str, while also ensuring the final dtype is pandas' nullable string dtype. Centralizing the pattern prevents duplication and clarifies the contract for callers.

## Args:
    series (pandas.Series): The input Series to convert. Must be a pandas Series; the function does not accept plain numpy arrays or lists.
    state (dict): An opaque dictionary for caller context. This function does not read from or modify this argument; it is present for API compatibility with caller pipelines.

## Returns:
    pandas.Series
    - The returned Series preserves the input Series' index and has dtype "string" (pandas' nullable string/ExtensionDtype).
    - Values are the stringified representation of the original values except:
        * If the original Series contained any missing values (series.hasnans is True), then any occurrences of the exact strings "nan" or "<NA>" anywhere in the Series are replaced with a true missing marker (NumPy NaN, np.nan) before the final cast.
        * If the original Series did not contain missing values (series.hasnans is False), literal strings "nan" and "<NA>" present in the data remain as string values (they are not converted to missing).
    - The function always returns a new Series object (the input Series is not modified in-place).

## Raises:
    - The function itself does not explicitly raise exceptions.
    - Underlying pandas methods may raise exceptions:
        * Series.astype("string") may raise if the running pandas version does not support the "string" dtype or if other astype constraints are violated.
        * Series.replace calls may raise for unexpected dtype or object issues (rare).
    - Callers should allow these exceptions to propagate or handle them externally.

## Constraints:
    Preconditions:
        - The first argument must be a pandas.Series instance.
        - pandas must support casting to the "string" dtype (modern pandas versions). If running on an older pandas without the nullable string dtype, astype("string") may fail.
    Postconditions:
        - The returned Series has dtype "string" and the same index as the input.
        - If the input had any missing values, any literal "nan" and "<NA>" strings in the output will have been converted back to missing values.

## Side Effects:
    - None visible: no file, network, stdout/stderr I/O, and no mutation of global variables.
    - The function creates and returns a new Series; it does not modify the provided Series in-place.

## Control Flow:
flowchart TD
    Start[Start: receive series] --> CheckHasNaNs{series.hasnans?}
    CheckHasNaNs -->|False| CastStr[val = series.astype(str)]
    CheckHasNaNs -->|True| CastStr
    CastStr --> IfHasNaNs{had missing originally?}
    IfHasNaNs -->|True| ReplaceNan[val = val.replace("nan", np.nan)]
    ReplaceNan --> ReplaceAngle[val = val.replace("<NA>", np.nan)]
    IfHasNaNs -->|False| ReplaceAngle
    ReplaceAngle --> FinalCast[return val.astype("string")]
    FinalCast --> End[End]

## Examples:
Example 1 — input with real missing value:
    import pandas as pd, numpy as np
    s = pd.Series([1, np.nan, "a"])
    out = to_category(s, state={})
    # out.tolist() == ["1", <missing>, "a"]
    # out.dtype == "string"

Example 2 — input with literal "nan" string only (no real missing values):
    s = pd.Series(["nan", "b"])  # series.hasnans == False
    out = to_category(s, state={})
    # out.tolist() == ["nan", "b"]  # "nan" remains a string
    # out.dtype == "string"

Example 3 — input with mixed: originally had missing values and also literal "nan":
    s = pd.Series(["nan", np.nan, "c"])  # series.hasnans == True
    out = to_category(s, state={})
    # Because had missing values, all "nan" / "<NA>" string occurrences are replaced
    # out.tolist() == [<missing>, <missing>, "c"]
    # out.dtype == "string"

Notes and caution:
    - Important gotcha: If the original Series contains any missing values, this function will convert every occurrence of the exact strings "nan" and "<NA>" in the entire Series into missing values. This can unintentionally convert legitimate data that happens to be the literal string "nan" into a missing marker. Callers that need to preserve literal "nan" strings even when some entries are missing should pre-process the data or avoid using this conversion.

## `src.ydata_profiling.model.typeset_relations.series_is_string` · *function*

## Summary:
Performs a conservative, fast heuristic to determine whether a pandas Series should be treated as textual data by checking that the first up-to-five values are Python strings and that converting the whole Series to str preserves every element exactly.

## Description:
This helper implements a two-stage check used in typeset/schema inference to decide whether a column is string-like:
1. Quick probe: examine series.values[0:5] and require every inspected element to be a Python str instance.
2. Roundtrip equality: attempt series.astype(str) and compare element-wise to the original series values; the series is string-like only if every element equals its string-cast representation.

Known callers:
- No explicit callers were present in the provided snapshot. Conventionally, this function is invoked by a typeset-detection or column-typing pipeline when deciding whether to classify a pandas Series as textual/string. It is intentionally isolated so the detection pipeline can reuse and unit-test this specific heuristic.

Why this logic is a separate function:
- Encapsulates a reproducible policy for string-detection.
- Limits performance cost by probing only a small prefix before doing a potentially expensive full-series cast.
- Centralizes exception handling for conversion failures.

## Args:
    series (pd.Series):
        The pandas Series to evaluate. The function reads series.values and may examine up to the first five elements (slice series.values[0:5]).
        Accepts any Series dtype. If the Series is shorter than five elements, the probe inspects all available elements.
    state (dict):
        Unused placeholder present for API compatibility with the surrounding pipeline. The function does not read from or modify this dict; callers may pass an empty dict or any mapping.

## Returns:
    bool:
        True if the Series is considered string-like by this heuristic; otherwise False.

    Detailed return conditions:
    - Immediately returns False if any of the elements in series.values[0:5] is not an instance of Python str.
    - If the probe passes, attempts to compute series.astype(str).values == series.values and returns True only if every element compares equal.
    - If astype(str) or the comparison raises TypeError or ValueError, the function catches the exception and returns False.

    Edge cases:
    - Empty Series: the initial all(...) over an empty slice yields True; the subsequent comparison on empty arrays yields True (empty all), so the function returns True for an empty Series.
    - Nulls in the first five elements (None, numpy.nan, pandas.NA): these are not instances of Python str and will cause the function to return False during the initial probe.
    - Nulls occurring after the first five elements: behavior depends on whether astype(str) produces values equal to the original null representations. Typically, stringifying nulls changes their representation (e.g., numpy.nan -> 'nan'), causing the comparison to fail and the function to return False.

## Raises:
    This function does not raise exceptions as part of normal operation. It catches TypeError and ValueError from series.astype(str) or the equality comparison and returns False in those cases. Other exceptions (e.g., MemoryError) are not explicitly handled and may propagate.

## Constraints:
    Preconditions:
    - The first argument must be a pandas Series-like object exposing .values slicing and supporting .astype(str). The function assumes series.values is indexable.
    - No other preconditions; the state parameter may be any mapping.

    Postconditions:
    - The input Series is not mutated.
    - A boolean is returned indicating the string-like decision.

## Side Effects:
    - None. No I/O, no global state mutation, and no external service calls. The function performs in-memory operations only.

## Control Flow:
flowchart TD
    Start([Start])
    Probe[Check series.values[0:5]]
    ProbeCond{All inspected elements isinstance(v, str)?}
    Cast[Attempt series.astype(str)]
    Compare[Compare casted values to original values element-wise]
    AllEqual{All elements equal after conversion?}
    ExceptErr([TypeError or ValueError during cast/comparison])
    ReturnFalse([Return False])
    ReturnTrue([Return True])

    Start --> Probe
    Probe --> ProbeCond
    ProbeCond -- No --> ReturnFalse
    ProbeCond -- Yes --> Cast
    Cast -- Exception --> ExceptErr --> ReturnFalse
    Cast -- Success --> Compare --> AllEqual
    AllEqual -- Yes --> ReturnTrue
    AllEqual -- No --> ReturnFalse

## Examples:
Note: example snippets assume pd refers to pandas and numpy is available in the caller's scope; imports are omitted here for brevity.

1) Simple textual series (expected True)
    s = pd.Series(["alpha", "beta", "gamma"])
    result -> True
    Explanation: first three values are str and astype(str) preserves every element.

2) Numeric series (expected False)
    s = pd.Series([1, 2, 3])
    result -> False
    Explanation: the first element is not a Python str so the quick probe fails.

3) Empty series (expected True)
    s = pd.Series([], dtype=object)
    result -> True
    Explanation: empty probe passes and comparison over empty arrays yields all True.

4) Series with leading null (expected False)
    s = pd.Series([None, "a", "b"])
    result -> False
    Explanation: None is not an instance of str, so the function returns False during the prefix probe.

5) Mixed types where stringification changes representation (expected False)
    s = pd.Series([numpy.datetime64("2020-01-01"), "2020-01-01"])
    result -> False
    Explanation: even if some values are strings, the initial probe inspects prefix elements (which may include non-str types) causing False, or the astype conversion produces different representations and the final comparison fails.

Usage notes:
- The function favors precision over recall: it returns True only when the series is already composed of Python strings (in the inspected prefix) and the entire column survives a roundtrip through str without representation changes.
- Because astype(str) can be expensive for large Series, the fast prefix probe avoids unnecessary full-cast in many negative cases.

## `src.ydata_profiling.model.typeset_relations.string_is_category` · *function*

## Summary:
Decides whether a text (string-typed) pandas Series should be classified as a categorical variable by checking unique-count and unique-ratio thresholds and ensuring it is not boolean-like text.

## Description:
This predicate is used during typeset / type-detection to determine whether a Series of textual values should be treated as a categorical variable. It is typically called by higher-level type-inference routines that iterate over a set of predicate functions to assign a semantic type to each column in a DataFrame. Typical callers run this check as part of a pipeline that inspects each Series along with a shared mutable state dict.

Why extracted into its own function:
- Encapsulates the rules that combine cardinality (absolute unique-value count), relative uniqueness (unique-value ratio), and exclusion of boolean-like text into a single reusable predicate.
- Keeps threshold interpretation (percentage vs absolute) in one place, preventing duplication and ensuring consistent behavior across the type-detection pipeline.
- Delegates boolean-text detection to string_is_bool to preserve separation of concerns (categorical detection vs boolean-text detection).

Known callers within the codebase and context:
- Type-detection and typeset construction routines that walk DataFrame columns and evaluate several predicate functions (e.g., string_is_bool, numeric checks) to assign a semantic type to each Series. This function is a building block of that detection stage.

## Args:
    series (pandas.Series):
        The column values to evaluate. Expected to be a pandas.Series (or Series-like) whose .nunique() and .size properties are defined. The series may contain missing values; the presence of missing values influences behavior only insofar as string_is_bool (called here) may observe and record them.
    state (dict):
        A mutable mapping shared between predicate calls in the detection pipeline. This function itself does not write into state, but it calls string_is_bool(series, state, ...), which may set state["hasnans"]. Provide a dict-like object if you want the pipeline to record NaN presence.
    k (Settings-like object):
        A configuration object exposing at least the following attributes:
          - k.vars.cat.percentage_cat_threshold
            * Type: numeric (float or int)
            * Semantics: a threshold used to decide whether the proportion of unique values is small enough for categorical membership.
            * Interpretation: if <= 1, it is treated as a proportion (e.g., 0.05 = 5%); if > 1, it is treated as an absolute maximum allowed unique-value proportion (see Returns for exact comparison).
          - k.vars.cat.cardinality_threshold
            * Type: int
            * Semantics: the maximum allowed absolute number of unique values for a Series to be considered categorical.
          - k.vars.bool.mappings
            * Type: mapping (used by string_is_bool)
            * Semantics: mapping of accepted textual boolean tokens (keys are tokens like "true","false","yes","no"). Only the keys are used by string_is_bool to decide boolean-likeness.

Interdependencies:
- The decision depends jointly on the cardinality_threshold (absolute cap) and the percentage_cat_threshold (relative cap which can be proportion or absolute depending on its numeric value). The function also returns False if the series is boolean-like text per string_is_bool.

## Returns:
    bool:
        True if and only if all of the following conditions hold:
          1. The number of unique values n_unique satisfies 1 <= n_unique <= cardinality_threshold.
          2. The proportion n_unique / series.size satisfies the configured unique-threshold rule:
               - If percentage_cat_threshold <= 1: requires n_unique / series.size < percentage_cat_threshold (strictly less).
               - If percentage_cat_threshold > 1: requires n_unique / series.size <= percentage_cat_threshold (less-or-equal).
          3. The series is NOT detected as boolean-like text by string_is_bool(series, state, k.vars.bool.mappings).
        Otherwise returns False.

Possible return-value scenarios and edge cases:
- Returns False for an empty series (series.size == 0) because n_unique will be 0 and fail the 1 <= n_unique check.
- Division by zero is avoided by short-circuiting: the proportion test is only evaluated when 1 <= n_unique is true, which ensures series.size >= 1 when the division occurs.
- If series contains values that string_is_bool recognizes as textual booleans (e.g., "true"/"false"), the function returns False to avoid labeling such columns as categorical.
- If n_unique equals cardinality_threshold and percentage_cat_threshold is > 1, the proportion comparison uses <= and may still pass (subject to proportion test). If percentage_cat_threshold <= 1 the proportion test uses strict <.

## Raises:
    - This function does not raise any new exceptions by design; however, exceptions from underlying operations may propagate:
        * If the provided series is not a pandas.Series or lacks .nunique()/.size, AttributeError or TypeError may propagate from those calls.
        * Exceptions raised by string_is_bool may propagate if they occur before its internal try-suppression logic (string_is_bool suppresses many runtime errors within its string-testing stage, but may propagate errors raised by categorical-type checks or by improper state types).
    - No exceptions are explicitly raised by this function.

## Constraints:
Preconditions:
    - series should be a pandas.Series (or behave like one) exposing .nunique(), .size, and suitable values for element counting.
    - state should be a mutable mapping (e.g., dict) if the caller expects string_is_bool to record NaN presence into state["hasnans"].
    - k must expose the nested attributes listed above (k.vars.cat.percentage_cat_threshold, k.vars.cat.cardinality_threshold, k.vars.bool.mappings).

Postconditions:
    - The function returns a boolean classification result.
    - The provided state may be mutated by string_is_bool (for example state["hasnans"] may be set) but this function itself does not perform additional mutations.

## Side Effects:
    - No I/O (file, network, stdout) is performed.
    - May cause state["hasnans"] to be created/updated via the call to string_is_bool.
    - May allow exceptions from underlying pandas operations or string_is_bool to propagate (see Raises).

## Control Flow:
flowchart TD
    Start --> ComputeNUnique[n_unique = series.nunique()]
    ComputeNUnique --> GetThresholds[unique_threshold = k.vars.cat.percentage_cat_threshold<br/>threshold = k.vars.cat.cardinality_threshold]
    GetThresholds --> CheckCardinality{1 <= n_unique <= threshold?}
    CheckCardinality -- No --> ReturnFalseCardinality[Return False]
    CheckCardinality -- Yes --> ComputeRatio[n_unique / series.size -> ratio]
    ComputeRatio --> CompareThreshold{unique_threshold <= 1?}
    CompareThreshold -- Yes --> RatioCheckStrict{ratio < unique_threshold?}
    CompareThreshold -- No --> RatioCheckNonStrict{ratio <= unique_threshold?}
    RatioCheckStrict -- No --> ReturnFalseRatio[Return False]
    RatioCheckNonStrict -- No --> ReturnFalseRatio[Return False]
    RatioCheckStrict -- Yes --> CallIsBool[Call string_is_bool(series, state, k.vars.bool.mappings)]
    RatioCheckNonStrict -- Yes --> CallIsBool
    CallIsBool --> IsBool{string_is_bool returned True?}
    IsBool -- Yes --> ReturnFalseBoolLike[Return False (boolean-like strings)]
    IsBool -- No --> ReturnTrue[Return True]

## Examples:
- Typical positive case:
    state = {}
    s = pandas.Series(["red", "blue", "red", "green", "blue"])
    # Create a minimal settings-like object:
    k = object()
    k.vars = object()
    k.vars.cat = object()
    k.vars.bool = object()
    k.vars.cat.cardinality_threshold = 10
    k.vars.cat.percentage_cat_threshold = 0.5   # treated as 50% threshold (proportion)
    k.vars.bool.mappings = {"true": True, "false": False}
    result = string_is_category(s, state, k)
    # n_unique = 3, series.size = 5 -> ratio = 0.6 -> 0.6 < 0.5 is False -> result == False

- Typical negative (categorical) case where proportion is small:
    state = {}
    s = pandas.Series(["A", "A", "B", "A", "A", "B", "A", "B", "A", "A"])
    k.vars.cat.cardinality_threshold = 50
    k.vars.cat.percentage_cat_threshold = 0.2  # 20%
    # n_unique = 2, series.size = 10 -> ratio = 0.2 -> since percentage_cat_threshold <= 1, check uses strict '<'
    # ratio < 0.2 is False (0.2 < 0.2 is False) so this would return False (not classified as categorical by this rule)
    # If percentage_cat_threshold were 0.21, result would be True (0.2 < 0.21)

- Boolean-like exclusion:
    state = {}
    s = pandas.Series(["true", "false", "true"])
    k.vars.cat.cardinality_threshold = 10
    k.vars.cat.percentage_cat_threshold = 1.0
    k.vars.bool.mappings = {"true": True, "false": False}
    result = string_is_category(s, state, k)
    # string_is_bool(s, state, mappings) returns True -> string_is_category returns False

## `src.ydata_profiling.model.typeset_relations.string_is_datetime` · *function*

## Summary:
Return True when at least one value in the given Series can be parsed into a pandas datetime; otherwise return False. Any error during parsing results in False.

## Description:
Determines whether a pandas Series of (typically) string values should be considered a datetime column by attempting to convert the Series to datetimes and checking whether any non-NaT values remain.

Known callers and context:
- Used by the typeset/typing pipeline when the system must decide whether a column that is currently represented as strings should be interpreted as datetime. In the supplied code excerpts there are no explicit call sites shown; in the larger codebase this function is typically invoked during type-detection/relations evaluation for a DataFrame column.
- Typical trigger: the pipeline inspects a column inferred as "string" and asks "is this a datetime in string form?" This function answers that question.

Why this logic is extracted:
- It encapsulates the boolean decision (is any value parseable to a datetime) and centralizes the error-handling policy (on any exception, treat the series as not datetime). Separating this from the conversion logic (string_to_datetime) keeps responsibilities distinct: one function performs conversion, this function interprets the conversion result to a boolean decision.

## Args:
    series (pd.Series):
        The pandas Series to test. Elements are typically strings but may include other types pandas.to_datetime accepts (ints, datetimes, NaN, None).
        The Series can be empty or contain nulls; behavior for these cases is documented below.
    state (dict):
        Contextual state passed through from the typeset pipeline. Present for API compatibility and potential future extensions; the current implementation only forwards it to string_to_datetime and does not otherwise inspect or mutate it.

## Returns:
    bool:
        True if at least one element in the converted datetime Series is not NaT (i.e., at least one value was successfully parsed to a real datetime).
        False otherwise. This includes:
        - The converted Series is entirely NaT (no successfully parsed datetimes) -> returns False.
        - The converted Series is empty -> returns False (Series.isna().all() returns True on empty Series).
        - Any exception is raised during conversion (string_to_datetime) -> function catches it and returns False.

## Raises:
    This function does not propagate exceptions from the conversion step: it catches all exceptions (bare except) and returns False. Therefore callers should not expect this function to raise. If callers need exception details they must call string_to_datetime directly or wrap another conversion that preserves exceptions.

## Constraints:
    Preconditions:
    - The first argument should be a pandas Series. Passing other types may cause string_to_datetime to raise; such exceptions are suppressed and will result in a returned False.
    - The caller should be aware that a False result is conservative: it means "no confidently parsed datetimes" or "an error occurred", not necessarily that no element resembles a datetime string.

    Postconditions:
    - The function returns a boolean and does not mutate the input Series.
    - No exceptions escape this function (because of the broad except); instead False is returned on error.

## Side Effects:
    - No I/O (files, network, stdout) is performed.
    - No global state is modified.
    - The function delegates to string_to_datetime which calls pandas.to_datetime; side effects are limited to in-memory allocations by pandas.

## Control Flow:
flowchart TD
    Start[Start]
    TryBlock[Try]
    Start --> TryBlock
    TryBlock --> CallConvert[string_to_datetime(series, state)]
    CallConvert --> IsNaAll{converted.isna().all()?}
    IsNaAll -- Yes --> ReturnFalse1[Return False]
    IsNaAll -- No --> ReturnTrue[Return True]
    TryBlock -.-> Except[except: (catch all)]
    Except --> ReturnFalse2[Return False]
    ReturnTrue --> End[End]
    ReturnFalse1 --> End
    ReturnFalse2 --> End

## Examples:
Example — typical usage:
    # Given a Series of date-like strings:
    s = pd.Series(["2020-01-01", "invalid", None])
    is_dt = string_is_datetime(s, state={})
    # is_dt -> True because at least one value ("2020-01-01") parses to a real datetime

Example — empty series and all-unparsable values:
    s_empty = pd.Series([], dtype=object)
    string_is_datetime(s_empty, {})  # -> False (empty series treated as no parseable datetime)

    s_bad = pd.Series(["not a date", None])
    string_is_datetime(s_bad, {})  # -> False (no value parsed to datetime)

Example — conversion error handling:
    # If conversion raises an unexpected exception (e.g., due to an unsupported dtype),
    # string_is_datetime will catch it and return False rather than propagating.
    try:
        result = string_is_datetime(maybe_problematic_series, {})
    except Exception:
        # This block will not be reached because string_is_datetime swallows exceptions.
        pass

Notes:
- If callers need to distinguish between "no parseable datetimes" and "conversion error", call string_to_datetime directly and handle exceptions or use pd.to_datetime with errors="coerce" according to the desired semantics.

## `src.ydata_profiling.model.typeset_relations.string_is_numeric` · *function*

## Summary:
Classify whether a pandas Series of string/object values should be treated as numeric: returns True when the series can be coerced to numeric values (with at least one non-NA numeric value) and is not deemed a low-cardinality numeric category; otherwise returns False.

## Description:
This function is part of the type-detection heuristics used by the profiling pipeline to decide if an object/string-typed column represents numeric data. It implements three responsibilities:
- Exclude boolean columns (actual bool dtype or object-typed-but-boolean) from being considered numeric.
- Attempt to coerce the series to float / numeric form and reject the series if coercion fails or yields only NA values.
- Defer to numeric_is_category to avoid classifying low-cardinality numeric-like series as numeric (they may be categorical).

Known callers:
- Type-detection and typeset/relationship heuristics in the profiling pipeline (the function is intended to be invoked when evaluating if an object/string column should be treated as numeric).
- It calls object_is_bool(series, state) to detect object-typed booleans and numeric_is_category(series, state, k) to decide whether a numeric-like series should instead be treated as categorical.

Why this is a separate function:
- Encapsulates a focused decision: whether non-numeric-typed series (often object or string) should be considered numeric for downstream numeric analyses. Keeping this heuristic isolated simplifies unit testing and lets other parts of the pipeline compose it with other detectors.

## Args:
    series (pd.Series):
        The candidate pandas Series. Expected to be one-dimensional. Typical inputs are object/string-typed Series, but the function accepts any Series type.
    state (dict):
        Pipeline state or context dictionary. Passed through to helper detectors (object_is_bool and numeric_is_category) for signature compatibility; this function does not read or modify state itself.
    k (Settings):
        Global configuration object used by numeric_is_category. The function itself does not read configuration directly, but numeric_is_category will consult k.vars.num.low_categorical_threshold.

Notes on parameter interdependencies:
- The final classification depends on numeric_is_category(series, state, k). If numeric_is_category raises due to a misconfigured k, that exception will propagate (see Raises).

## Returns:
    bool:
        - True:
            * The series is not boolean (neither pandas bool dtype nor object-dtype-all-boolean), AND
            * The series can be coerced to numeric (no exceptions during astype(float)/to_numeric), AND
            * The coercion produced at least one non-NA numeric value (i.e., not "all values coerced to NA"), AND
            * numeric_is_category(series, state, k) returned False (the numeric-like series is not classified as a low-cardinality category).
        - False:
            * The series is boolean (pandas bool dtype or object-dtype consisting exclusively of True/False), OR
            * Coercion to float/numeric fails (an exception is raised during astype(float) or pd.to_numeric), OR
            * Coercion succeeds but results in all NA values (the coerced series has missing values and zero non-missing count), OR
            * numeric_is_category(series, state, k) returned True (the numeric-like series should be treated as categorical).

Edge-case behaviors:
- Empty Series: astype(float) and pd.to_numeric typically succeed for empty series; numeric_is_category returns False for an empty series (nunique()==0). Therefore, this function will return True for an empty series under the current code (empty series is considered numeric by this routine).
- Partially numeric strings: a series with some numeric-like strings and some non-numeric strings will be coerced by pd.to_numeric with errors="coerce" — the function returns False only if all values become NA (i.e., no non-NA numeric values remain); otherwise it continues to numeric_is_category to make the final decision.
- If coercion produces some NAs but also some numeric values, the presence of non-NA numeric values means the function proceeds; it will return the negation of numeric_is_category.

## Raises:
    Exceptions may propagate from helper calls:
    - Any exception raised by pdt.is_bool_dtype(series) (pandas.api.types.is_bool_dtype) or object_is_bool(series, state) will propagate (object_is_bool is documented to allow dtype-check exceptions to propagate).
    - Exceptions raised by numeric_is_category(series, state, k) (e.g., AttributeError if k.vars.num.low_categorical_threshold is missing or TypeError from incompatible types) will propagate.
    Internally caught exceptions:
    - Any exception raised during the try block that attempts coercion (series.astype(float) or pd.to_numeric(...)) is caught by the function; when such an exception occurs the function returns False (no exception is propagated from that block).

## Constraints:
Preconditions:
    - Prefer passing a pandas.Series. The function expects pandas Series semantics for dtype checks and conversion methods.
    - The Settings object `k` should provide the configuration numeric_is_category expects (k.vars.num.low_categorical_threshold) to avoid propagated exceptions when numeric_is_category is invoked.

Postconditions:
    - No mutation of the input series, state, or k is performed.
    - The function returns a boolean and has no side effects.

## Side Effects:
    - None. The function performs pure in-memory inspection and uses pandas conversion utilities; it does not perform I/O, global state mutation, or external service calls.

## Control Flow:
flowchart TD
    Start --> CheckBool{pdt.is_bool_dtype(series) OR object_is_bool(series,state)?}
    CheckBool -- Yes --> ReturnFalseBool[Return False]
    CheckBool -- No --> TryConvert[Try: series.astype(float); r = pd.to_numeric(series, errors="coerce")]
    TryConvert -->|exception| ReturnFalseOnExcept[Return False]
    TryConvert -->|success| CheckAllNA{r.hasnans AND r.count() == 0?}
    CheckAllNA -- Yes --> ReturnFalseAllNA[Return False]
    CheckAllNA -- No --> CallNumericIsCategory[call numeric_is_category(series,state,k)]
    CallNumericIsCategory --> Decision{numeric_is_category == True?}
    Decision -- Yes --> ReturnFalseCat[Return False]
    Decision -- No --> ReturnTrueNumeric[Return True]

## Examples:
Note: examples assume pandas imported as pd and a valid Settings object k.

1) Typical numeric strings
    s = pd.Series(["1.5", "2.0", "3"])
    string_is_numeric(s, {}, k)  # -> True (coercible to numeric, not low-cardinality)

2) Mixed strings with some non-numeric values
    s = pd.Series(["1", "two", "3"])
    # pd.to_numeric will coerce "two" to NA but there are numeric values remaining
    string_is_numeric(s, {}, k)  # -> True or False depending on numeric_is_category (likely True)

3) All non-numeric strings
    s = pd.Series(["a", "b", "c"])
    string_is_numeric(s, {}, k)  # -> False (coercion yields all NA => rejected)

4) Boolean-like object dtype
    s = pd.Series([True, False], dtype="object")
    string_is_numeric(s, {}, k)  # -> False (object_is_bool returns True, booleans excluded)

5) Numeric-like but low-cardinality (treated as categorical)
    s = pd.Series(["1", "1", "2", "2"])
    # If k.vars.num.low_categorical_threshold == 2, numeric_is_category returns True
    string_is_numeric(s, {}, k)  # -> False (numeric-like but numeric_is_category == True)

6) Empty series
    s = pd.Series([], dtype="object")
    string_is_numeric(s, {}, k)  # -> True under current logic (coercion succeeds; numeric_is_category returns False)

## `src.ydata_profiling.model.typeset_relations.string_to_datetime` · *function*

## Summary:
Coerces a pandas Series of strings (or mixed values) into a pandas datetime Series, choosing a pandas-call signature depending on the runtime pandas major version.

## Description:
This function centralizes the conversion of a pandas Series to datetime values and encapsulates a small compatibility branch for different pandas major versions.

Known callers within the provided context:
- No direct callers were found in the supplied code excerpts. In the codebase this typically acts as a helper used by the typeset/typing pipeline when a column's inferred type should be converted to datetime (for example, when mapping detected "string" representations of dates into actual datetime dtype). Callers in practice would pass a column (pd.Series) and a state dict coming from the typeset/relations pipeline.

Why this logic is extracted:
- The function isolates pandas-version-specific differences in how to call pandas.to_datetime. Extracting the branch avoids scattering compatibility checks across the codebase and centralizes any future changes needed for pandas API differences.
- It provides a clear single point to add common pre/post-processing (null handling, error semantics) in the future.

## Args:
    series (pd.Series):
        The pandas Series to convert. Elements are typically strings (e.g., "2020-01-01"), but may also be other types that pandas.to_datetime can parse (ints, datetime-like objects, NaT, None).
        The series may contain null values; pandas.to_datetime will preserve or coerce them according to its own rules.
    state (dict):
        A dictionary representing contextual state passed by the caller (for example, the typeset pipeline state). This parameter is accepted for API compatibility but is not used by the current implementation and has no effect on the result.

## Returns:
    pd.Series:
        A pandas Series with dtype datetime64[ns] (or an appropriate pandas datetime dtype) produced by pandas.to_datetime. The concrete dtype and behavior (e.g., timezone-awareness, nan/NaT handling) follow pandas.to_datetime semantics.
        Edge-case return behaviors:
        - If pandas.to_datetime succeeds, the returned Series contains parsed datetime objects (or NaT where parsing failed or where input was null, according to pandas rules).
        - If pandas.to_datetime returns an object-dtype Series (rare), the function returns that object as-is (no post-normalization is performed here).

## Raises:
    Propagates any exception raised by pandas.to_datetime called with the chosen signature.
    Typical exceptions that may be raised by pandas.to_datetime (and therefore by this function) include:
    - ValueError: if data contain values that cannot be parsed as datetimes under the invoked parsing rules.
    - TypeError or other pandas-internal errors if input types are incompatible.
    Note: the function does not catch or translate these exceptions; callers should handle them if they need different error semantics.

## Constraints:
    Preconditions:
    - The caller must provide a pandas Series as the first argument. Passing non-Series objects may lead to pandas errors.
    - The runtime pandas major version determines which pandas.to_datetime signature is used: when pandas_major_version() == 1 the function calls pd.to_datetime(series) otherwise it calls pd.to_datetime(series, format="mixed").
    Postconditions:
    - On successful return, the input series has been converted into a new pandas Series representing datetime values (the original input Series is not mutated by this function; pandas typically returns a new Series).
    - Any exceptions from pandas.to_datetime will be propagated to the caller.

## Side Effects:
    - No I/O (no file, network, stdout) is performed.
    - No global state is modified by this function.
    - The function calls into pandas (pandas.to_datetime), which may allocate memory for the resulting Series but has no external side effects beyond in-memory computation.

## Control Flow:
flowchart TD
    Start[Start]
    CheckVersion{is_pandas_1()?}
    Start --> CheckVersion
    CheckVersion -- Yes --> Call1[call pd.to_datetime(series)]
    CheckVersion -- No --> Call2[call pd.to_datetime(series, format="mixed")]
    Call1 --> Return[Return resulting pd.Series]
    Call2 --> Return
    Return --> End[End]
    Call1 -.-> Exception[Exception from pandas.to_datetime]
    Call2 -.-> Exception
    Exception --> End

## Examples:
Example 1 — typical usage (happy path):
    # Given a column of ISO date strings in a DataFrame column 'date_col':
    series = df["date_col"]  # pandas Series of strings like "2020-01-01"
    try:
        datetime_series = string_to_datetime(series, state={})
        # datetime_series is now a Series of dtype datetime64[ns]
    except Exception as exc:
        # Handle parse errors or log them; pandas exceptions are propagated
        raise

Example 2 — handling unparsable values by the caller:
    # If some values may not be parseable and you want to coerce them to NaT
    series = df["maybe_dates"]
    try:
        parsed = string_to_datetime(series, {})
    except ValueError:
        # Fall back to a safer conversion that coerces errors
        parsed = pd.to_datetime(series, errors="coerce")

Notes:
- Because this function defers to pandas.to_datetime without setting errors='coerce', callers that require non-raising behavior for unparsable strings should either wrap this call in try/except or perform a coercing conversion themselves.
- The 'state' argument exists for compatibility with the surrounding typeset pipeline and may be used in future extensions; currently it is ignored.

## `src.ydata_profiling.model.typeset_relations.string_to_numeric` · *function*

## Summary:
Converts a pandas Series of (possibly) string values to numeric values, coercing any non-convertible entries to NaN.

## Description:
Known callers within the codebase:
- No direct callers were discovered in the provided analysis memory for this exact symbol. In typical usage within a profiling/type-inference pipeline, this function is invoked during a typeset/relationship resolution stage where columns labeled as strings are tested for numeric conversion (e.g., to detect numeric-like string columns or to prepare numeric statistics).

Why this logic is extracted:
- Centralizes the conversion policy (use of pandas' to_numeric with errors="coerce") so all callers get consistent behavior when attempting to interpret string-like data as numbers.
- Keeps a stable small adaptor function that matches a common callable signature (series, state) used by the surrounding pipeline, even if the pipeline sometimes passes an unused state object.

## Args:
    series (pd.Series):
        The input pandas Series containing the values to convert. The function treats each element as a candidate for numeric conversion.
        - Expected types: string-like, numeric, or mixed types that pandas.to_numeric can handle.
        - The function preserves the input Series' index.
    state (dict):
        An arbitrary state dictionary passed through by the caller for pipeline compatibility. This function does not read or modify this dict; it exists to match the expected callable signature in the surrounding pipeline.

## Returns:
    pd.Series:
        A new pandas Series with the same index as the input and values converted to numeric types where possible.
        - For values that can be parsed as integers or floats, numeric equivalents are returned.
        - For values that cannot be converted, the function returns numpy.nan (i.e., missing / NaN).
        - If the input contains non-convertible values, the resulting dtype will typically be a floating dtype (e.g., float64) because of the presence of NaN.
        - If the input Series is empty, an empty numeric Series with the same index is returned.

## Raises:
    This function itself does not raise conversion-related exceptions for non-convertible values because pandas.to_numeric is called with errors="coerce", which converts invalid parses to NaN. Exceptions may still arise from pandas if the provided input is of an unexpected shape/type that pandas cannot handle at all, but none are explicitly raised by this function.

## Constraints:
Preconditions:
    - The caller should pass a pandas Series (annotated as pd.Series). Although pandas.to_numeric accepts many array-like inputs, the declared signature expects a Series for index-preservation semantics.
    - The state argument may be any dict-like object (it is ignored by this function), but callers should supply a dict to conform to the typical pipeline contract.

Postconditions:
    - The returned Series has the same index as the input Series.
    - All entries are either numeric values (int/float as interpreted by pandas) or numpy.nan for values that could not be parsed.
    - The input Series and the provided state dict are not mutated by this function.

## Side Effects:
    - None. The function performs a pure data transformation: no I/O, no global state mutation, no external service calls, and it does not alter the input Series or the state dict.

## Control Flow:
flowchart TD
    Start([Start]) --> ToNumeric[/"Call pandas.to_numeric(series, errors='coerce')"/]
    ToNumeric --> CheckConvertible{Value convertible?}
    CheckConvertible -->|Yes| NumericValue([Return numeric value])
    CheckConvertible -->|No| NaNValue([Return numpy.nan])
    NumericValue --> End([End])
    NaNValue --> End

## Examples:
- Converting numeric-like strings and handling invalid entries:
    Given series = pd.Series(['10', '3.14', 'x']), state = {}
    The function returns a Series with values [10.0, 3.14, numpy.nan] (index preserved).

- Empty input:
    Given an empty Series with index [0, 1], state = {}
    The function returns an empty numeric Series with the same index.

Notes:
    - The state parameter is intentionally unused: it is present so the function conforms to the pipeline's expected callable signature (series, state).
    - Because errors are coerced, callers should check for resulting NaN values if they need to detect non-convertible entries (e.g., via isna()).

## `src.ydata_profiling.model.typeset_relations.to_bool` · *function*

## Summary:
Cast a pandas Series to an appropriate boolean dtype: use a module-level NA-capable boolean dtype when the Series contains missing values, otherwise use the standard boolean dtype.

## Description:
This function inspects the input Series for missing values (series.hasnans) and then delegates to pandas' casting mechanism to produce a boolean-typed Series:
- If series.hasnans is True, the function uses the module-level name hasnan_bool_name as the dtype argument to series.astype.
- If series.hasnans is False, the function uses the built-in bool dtype as the dtype argument to series.astype.
- The function returns the result of series.astype(dtype) and does not otherwise transform the data.

Callers:
- No direct call sites were present in the provided source snapshot. This helper is intended for use by higher-level type-normalization or profiling pipelines that need consistent policy for selecting an NA-capable boolean dtype versus the standard boolean dtype.

Why this is a separate function:
- Centralizes the policy "use NA-capable boolean when missing values exist" so that all callers use the same rule and to reduce duplication in casting logic across the codebase.

## Args:
    series (pd.Series): The pandas Series to cast. The object must support:
        - attribute .hasnans (boolean-like)
        - method .astype(dtype) used for casting

## Returns:
    pd.Series: The Series returned by series.astype(dtype) where:
        - dtype == bool  when series.hasnans is False
        - dtype == hasnan_bool_name (module-level identifier) when series.hasnans is True

    Additional notes:
        - The returned Series preserves the original index and length.
        - Depending on pandas internals, astype may return a view or a copy.
        - The function does not wrap or alter exceptions raised by pandas.astype; they propagate to the caller.

## Raises:
    - AttributeError: If the provided `series` has no .hasnans attribute (accessing series.hasnans triggers this).
    - NameError: If series.hasnans is True and the module-level name hasnan_bool_name is not defined in the module namespace (lookup of that global raises NameError).
    - TypeError or ValueError: May be raised by pandas.Series.astype if the selected dtype is invalid or incompatible with the Series' values. These exceptions are propagated from pandas.

## Constraints:
Preconditions:
    - The caller is expected to provide a pd.Series (or a Series-like object with .hasnans and .astype).
    - If the Series may contain missing values and you wish to use a specific NA-capable boolean dtype, ensure the module-level name hasnan_bool_name is defined before calling.

Postconditions:
    - The function returns series.astype(dtype) using the dtype chosen by presence of missing values.
    - The function performs no persistent side effects or global mutations.

## Side Effects:
    - No file, network, or stdout I/O.
    - No intentional mutation of globals; the function only reads the module-level name hasnan_bool_name.
    - Calls pandas.Series.astype which may internally allocate memory or raise exceptions.

## Control Flow:
flowchart TD
    Start["Start: to_bool(series)"]
    EvalHasnans["Evaluate series.hasnans"]
    AttrError["AttributeError (no .hasnans) - TERMINATE"]
    HasnansTrue{"hasnans == True"}
    HasnansFalse{"hasnans == False"}
    LookupHasnan["Lookup hasnan_bool_name"]
    NameError["NameError (hasnan_bool_name undefined) - TERMINATE"]
    SetBool["Set dtype = bool"]
    Cast["Call series.astype(dtype) -> return result\n(may raise TypeError/ValueError)"]
    Start --> EvalHasnans
    EvalHasnans -- attribute missing --> AttrError
    EvalHasnans -- True --> HasnansTrue
    EvalHasnans -- False --> HasnansFalse
    HasnansTrue --> LookupHasnan
    LookupHasnan -- defined --> Cast
    LookupHasnan -- undefined --> NameError
    HasnansFalse --> SetBool
    SetBool --> Cast

## Examples:
1) Basic usage when there are no missing values:
    import pandas as pd
    s = pd.Series([True, False, True])
    result = to_bool(s)
    # result.dtype will be a boolean dtype (no NA-capable dtype needed)

2) Define the module-level NA-capable dtype name before calling to avoid NameError:
    import pandas as pd
    import src.ydata_profiling.model.typeset_relations as tr

    # Option 1: string name recognized by pandas ('boolean' is the pandas nullable boolean name on compatible versions)
    tr.hasnan_bool_name = "boolean"

    # Option 2: dtype instance (safer across pandas versions)
    # tr.hasnan_bool_name = pd.BooleanDtype()

    s = pd.Series([True, None, False])
    result = tr.to_bool(s)
    # result will be cast using the dtype referenced by tr.hasnan_bool_name (e.g., pandas nullable boolean),
    # preserving the missing entry as <NA> if the chosen dtype supports it.

3) Defensive handling around possible errors:
    import pandas as pd
    import src.ydata_profiling.model.typeset_relations as tr

    # Ensure a fallback is available
    tr.hasnan_bool_name = "boolean"

    s = pd.Series([1, 2, None])  # values not boolean-compatible
    try:
        result = tr.to_bool(s)
    except (TypeError, ValueError) as exc:
        # pandas couldn't cast the data to the requested boolean dtype
        # Choose an alternate strategy, e.g., coerce manually or keep as object dtype
        result = s.astype(object)

## `src.ydata_profiling.model.typeset_relations.object_is_bool` · *function*

## Summary:
Determine whether an object-dtype pandas Series contains exclusively boolean values (True/False); returns True for an object-typed series where every element is a boolean, otherwise False.

## Description:
This function classifies a pandas Series that is stored with an object dtype as boolean-only when every element is either True or False. Implementation details:
- It first verifies the Series has an object dtype using the module's dtype check.
- If so, it tests membership of every element against the set {True, False} using an element-wise all(...) check wrapped in a try/except. If the membership test succeeds for all elements, the function returns True; if any element is not a member, or if the membership test raises an exception, it returns False.
- If the Series is not object dtype, the function immediately returns False.

Known callers within the codebase:
- No direct callers were found in the provided snapshot. This function is intended for use by type-detection routines that need to treat object-typed columns that actually contain booleans as boolean-type equivalents.

Why this logic is extracted:
- Encapsulating the object-dtype boolean detection ensures a single, consistent policy for classification (which values count as booleans, how exceptions are handled), keeps calling code concise, and centralizes future adjustments (e.g., extending accepted boolean representations).

## Args:
    series (pd.Series): The pandas Series to inspect. The function expects a Series so that the module dtype check and iteration semantics behave as in pandas.
    state (dict): Context/state dictionary provided for API compatibility with other detectors. This parameter is unused by the function and has no effect on the result.

## Returns:
    bool:
        - True:
            * series has object dtype, and
            * the generator all(item in {True, False} for item in series) evaluates to True.
            Note: an empty object-dtype Series yields True (vacuously, since all on an empty iterator returns True).
        - False:
            * series does not have object dtype (includes Series with dtype 'bool'), or
            * at least one element is not equal to True or False (e.g., strings "True"/"False", numbers, None, numpy.nan, pandas.NA), or
            * the element-membership check raises an exception (for example, if an element is unhashable and membership raises TypeError); such exceptions are caught and result in False.

## Raises:
    - Exceptions raised by the initial dtype check call propagate (the function does not catch exceptions raised by the dtype-checking call). For example, if the dtype check is invoked on a non-Series object and that call raises TypeError or ValueError, that exception will propagate out of this function.
    - No exceptions will be raised as a result of membership checks: any exception thrown during the element-wise membership test is caught and the function returns False.

## Constraints:
    Preconditions:
        - Prefer passing a pandas Series. The function assumes pandas Series semantics for dtype inspection and iteration.
    Postconditions:
        - The input Series and the provided state dict are not mutated.
        - The function returns a boolean classification and has no side effects.

## Side Effects:
    - None. The function performs pure inspection only — no I/O, no global state mutation, and no external service calls.

## Control Flow:
flowchart TD
    Start --> IsObject{is object dtype?}
    IsObject -- No --> ReturnFalseNonObject[Return False]
    IsObject -- Yes --> TryCheck[Try membership check]
    TryCheck -->|success| AllTrue{all items in {True,False}?}
    AllTrue -- True --> ReturnTrue[Return True]
    AllTrue -- False --> ReturnFalseNonAll[Return False]
    TryCheck -->|exception| ReturnFalseOnException[Return False]

## Examples:
Example 1 — all Python booleans in object dtype:
    s = pd.Series([True, False, True], dtype="object")
    object_is_bool(s, {})  # -> True

Example 2 — contains non-boolean or NA values:
    s = pd.Series([True, "False", None], dtype="object")
    object_is_bool(s, {})  # -> False

Example 3 — numpy boolean scalars:
    s = pd.Series([numpy.bool_(True), numpy.bool_(False)], dtype="object")
    object_is_bool(s, {})  # -> True

Example 4 — non-object dtype (bool dtype):
    s = pd.Series([True, False], dtype="bool")
    object_is_bool(s, {})  # -> False

Example 5 — empty object-dtype series:
    s = pd.Series([], dtype="object")
    object_is_bool(s, {})  # -> True (all on empty iterator is True)

