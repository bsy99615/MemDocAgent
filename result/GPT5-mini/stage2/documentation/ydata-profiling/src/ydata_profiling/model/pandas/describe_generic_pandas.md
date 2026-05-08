# `describe_generic_pandas.py`

## `src.ydata_profiling.model.pandas.describe_generic_pandas.pandas_describe_generic` · *function*

## Summary:
Enriches an existing summary dictionary with generic, pandas-specific aggregate values (total length, proportion missing, non-missing count, and series memory usage) and returns the original inputs with the updated summary.

## Description:
This function computes and appends basic generic statistics for a pandas Series into a provided summary dictionary. It is a thin adapter around derived counts and pandas' memory accounting, intended to run after lower-level summary computation has populated the summary with at least the number of missing values.

Known callers:
    - No direct callers were discovered in the provided code snapshot. Typical callers are higher-level profiling or summarization orchestration code within the ydata_profiling.model.* pipeline that assemble column summaries after core summary algorithms (for example, after an algorithm that writes "n_missing" into the summary).

Why this is a separate function:
    - Responsibility boundary: it centralizes the bookkeeping of a fixed set of generic summary fields (n, p_missing, count, memory_size) that are common to pandas-backed summarization steps.
    - Reuse: by isolating pandas-specific finalization logic, other components can reuse the same finalization without duplicating memory accounting and missing-value proportion logic.
    - Testability: isolates simple derived computations for independent unit testing.

## Args:
    config (Settings):
        - Type: Settings
        - Purpose: Provides configuration flags used during summarization.
        - Required attributes: must expose `memory_deep` (a boolean or truthy/falsey value) which is passed to pandas' memory_usage as the `deep` argument.
    series (pd.Series):
        - Type: pandas Series (annotated in code as pd.Series)
        - Purpose: The column data for which generic statistics are computed.
        - Constraints: should be an instance compatible with pandas Series API (supports len() and memory_usage(deep=...)).
    summary (dict):
        - Type: dict (mutable mapping)
        - Purpose: An existing partial summary for the series; this function updates it in-place.
        - Required keys before call: must contain "n_missing" (an integer count of missing values). If "n_missing" is absent, a KeyError will occur.

## Returns:
    Tuple[Settings, pd.Series, dict]
        - The function returns the original `config` and `series` values unchanged, plus the same `summary` object that has been updated in-place with the following keys:
            * "n" (int): the total number of elements in the series (len(series)).
            * "p_missing" (float): the proportion of missing values; computed as summary["n_missing"]/n when n > 0, otherwise 0.
            * "count" (int): the number of non-missing values; n - summary["n_missing"].
            * "memory_size": the value returned by series.memory_usage(deep=config.memory_deep) (value and units are determined by pandas; typically an integer representing bytes).
        - Edge cases:
            * When the series length is 0, "p_missing" is set to 0 to avoid division by zero.
            * The function performs an in-place update of the provided summary dict and returns that same object.

## Raises:
    - KeyError: if "n_missing" is not present in the provided summary dict (the code accesses summary["n_missing"] directly).
    - Any exceptions raised by pandas Series operations:
        * If `len(series)` or `series.memory_usage(...)` is called on an object that does not implement the expected pandas Series methods, those calls may raise TypeError/AttributeError or pandas-specific exceptions. These are not raised by this function directly; they are propagated from the underlying calls.

## Constraints:
    Preconditions:
        - `summary` must already contain a numeric "n_missing" key (integer count of missing values).
        - `series` must be a pandas-compatible Series (implementing len(...) and memory_usage(deep=...)).
        - `config` must expose an attribute `memory_deep` (used as the `deep` argument to memory_usage).
    Postconditions (guarantees after return):
        - The `summary` dict will contain/overwrite the keys "n", "p_missing", "count", and "memory_size" as defined above.
        - The returned `config` and `series` references are the same objects passed in (no copies are made by this function).

## Side Effects:
    - Mutates the provided `summary` dict in-place via summary.update(...).
    - No I/O, network access, global state mutation, or external service calls are made by this function.

## Control Flow:
flowchart TD
    Start([Start])
    A[Compute length = len(series)]
    B{length > 0?}
    C[Compute p_missing = summary["n_missing"] / length]
    D[Set p_missing = 0]
    E[Compute count = length - summary["n_missing"]]
    F[Compute memory_size = series.memory_usage(deep=config.memory_deep)]
    G[summary.update({"n","p_missing","count","memory_size"})]
    End([Return config, series, summary])

    Start --> A --> B
    B -- Yes --> C
    B -- No --> D
    C --> E
    D --> E
    E --> F --> G --> End

## Examples (usage scenario described):
    - Typical pipeline step:
        1. A lower-level summary algorithm computes per-column statistics and writes "n_missing" into `summary`.
        2. Call this function with the profiling `config`, the column `series`, and the partial `summary`.
        3. After return, read the returned `summary` to obtain "n", "p_missing", "count", and "memory_size" for reporting or further processing.

    - Error handling guideline:
        * Before calling, ensure "n_missing" is present in `summary`. If "n_missing" might be absent, guard or compute it first to avoid KeyError.

