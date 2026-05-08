# `describe_counts_pandas.py`

## `src.ydata_profiling.model.pandas.describe_counts_pandas.pandas_describe_counts` · *function*

## Summary:
Computes value-count summaries for a pandas Series, detects whether its values are hashable, counts missing values, and records ordering information; returns the (possibly mutated) summary alongside the original config and series.

## Description:
This function inspects a pandas Series to produce count-related metadata and stores the results in the provided summary dictionary. It is typically executed as a low-level step in a data-profiling pipeline that needs discrete-value statistics (for example, when producing frequency tables and missing-value counts for a feature). The logic is extracted into its own function to centralize the series-level counting logic, to handle hashability and NaN treatment consistently, and to keep higher-level profiling code focused on orchestration rather than per-series details.

Known callers in provided snapshot:
- None explicitly identified in the provided source snapshot.
Typical usage context:
- Invoked by higher-level profiling or "describe" routines that iterate over dataset columns and aggregate per-column summaries.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: The global profiling configuration object passed through the profiling pipeline. This function does not read or modify config fields; it is passed through to keep a consistent (config, series, summary) contract with other pipeline steps.
        - Allowed values: any valid Settings instance; None is not expected.

    series (pd.Series):
        - Type: pandas.Series (annotated as pd.Series)
        - Purpose: The data column to be summarized.
        - Constraints: Should be a one-dimensional pandas Series. Elements may be of any dtype; the function detects whether elements are hashable and handles missing values.
        - Edge cases: If series contains unhashable elements (e.g., lists, dicts, other mutable containers), the function will set summary["hashable"] = False and will not attempt value_counts-based grouping.

    summary (dict):
        - Type: dict
        - Purpose: Mutable dictionary used to accumulate per-series summary fields. This dictionary is mutated in-place and then returned as part of the result tuple.
        - Expected initial state: may be empty or contain prior summary entries; keys written by this function may overwrite existing keys.
        - Interdependencies: The function writes several keys into this dict (see Returns / Postconditions).

## Returns:
    Tuple[Settings, pd.Series, dict]
    - The function returns the same config and series objects passed in (unchanged by this function), and the summary dict (mutated in place).
    - The summary dict will contain at minimum:
        - "hashable" (bool): True if series values are hashable (value_counts with dropna=False succeeded and index is convertible to a set), False otherwise.
        - "ordering" (bool): True if value_counts_without_nan index could be sorted (sort_index succeeded), False otherwise.
        - "n_missing" (int): Number of missing (NaN) entries counted.
      Additionally, when "hashable" is True, the following keys are added:
        - "value_counts_without_nan" (pandas.Series): counts of unique values excluding NaN and excluding values with count == 0; index are the unique values, values are counts.
        - Optionally "value_counts_index_sorted" (pandas.Series): same as value_counts_without_nan but sorted by index ascending; present only if index sorting succeeded (i.e., ordering is True).
    - Edge-case returns:
        - If values are unhashable, "value_counts_without_nan" and "value_counts_index_sorted" will not be present and value counting by unique-value grouping is skipped.
        - n_missing is computed either from counts (when hashable) or via series.isna().sum() (when unhashable), ensuring that n_missing is always set.

## Raises:
    - The function catches all exceptions raised when attempting to compute value_counts and when attempting to sort the value_counts index. As implemented, the function does not re-raise any exceptions; instead it falls back to conservative behavior:
        - If computing value_counts(dropna=False) or creating a set from the index fails (unhashable elements), the function sets summary["hashable"] = False and continues.
        - If sort_index on the counts fails with a TypeError (incomparable index types), the function sets ordering = False and continues.
    - No exceptions are explicitly raised by this function.

## Constraints:
Preconditions:
    - series must be a pandas.Series-like object exposing value_counts(dropna=...), index, and isna() operations consistent with pandas API.
    - summary must be a mutable mapping (dict-like) to receive result keys.
Postconditions:
    - summary will contain keys "hashable", "ordering", and "n_missing".
    - If summary["hashable"] is True, summary will also contain "value_counts_without_nan". If sorting succeeds, "value_counts_index_sorted" will also be present.
    - The returned config and series references are the same objects passed in (no new copy is returned).

## Side Effects:
    - Mutates the provided summary dictionary in-place by adding/updating keys described above.
    - No I/O (no file, network, or stdout/stderr operations).
    - No global state or external services are modified or called.

## Control Flow:
flowchart TD
    A[Start] --> B{Try compute value_counts(dropna=False) and build set(index)}
    B -->|Success| C[hashable = True]
    B -->|Exception| D[hashable = False]
    C --> E[Filter counts: keep counts > 0]
    E --> F{Index has null entries?}
    F -->|Yes| G[n_missing = sum(counts for null index)]
    F -->|Yes| H[value_counts_without_nan = counts without null index]
    F -->|No| I[n_missing = 0]
    F -->|No| J[value_counts_without_nan = counts]
    H --> K[summary["value_counts_without_nan"] = value_counts_without_nan]
    J --> K
    K --> L{Try sort_index(ascending=True)}
    L -->|Success| M[summary["value_counts_index_sorted"] set; ordering = True]
    L -->|TypeError| N[ordering = False]
    D --> O[n_missing = series.isna().sum(); ordering = False]
    N --> P[summary["ordering"]=ordering; summary["n_missing"]=n_missing]
    M --> P
    O --> P
    P --> Q[Return (config, series, summary)]

## Examples:
Example 1 — typical successful case:
    - Given a Series of hashable values with some NaNs:
        series = pd.Series(["a", "b", "a", None, "c", "a"])
        summary = {}
        config = Settings()  # placeholder Settings instance
        config_out, series_out, summary_out = pandas_describe_counts(config, series, summary)
    - After call:
        summary_out["hashable"] == True
        summary_out["n_missing"] == 1
        summary_out["value_counts_without_nan"] is a Series like: {"a": 3, "b": 1, "c": 1}
        summary_out["value_counts_index_sorted"] exists if the index values are comparable and sortable

Example 2 — unhashable values fallback:
    - Given a Series that contains unhashable elements (e.g., lists):
        series = pd.Series([[1, 2], [1, 2], None])
        summary = {}
        config = Settings()
        _, _, summary_out = pandas_describe_counts(config, series, summary)
    - After call:
        summary_out["hashable"] == False
        summary_out["ordering"] == False
        summary_out["n_missing"] == 1  # computed via series.isna().sum()
        No "value_counts_without_nan" or "value_counts_index_sorted" keys will be present.

Notes:
    - The function favors robustness: it avoids failing the entire profiling run due to unhashable values or incomparable indices, instead recording conservative metadata and continuing.
    - Callers relying on "value_counts_without_nan" should first check summary["hashable"] is True.

