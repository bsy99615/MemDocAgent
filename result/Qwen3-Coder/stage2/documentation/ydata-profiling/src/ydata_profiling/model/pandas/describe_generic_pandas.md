# `describe_generic_pandas.py`

## `src.ydata_profiling.model.pandas.describe_generic_pandas.pandas_describe_generic` · *function*

## Summary:
Computes and updates descriptive statistics for a pandas Series within a profiling summary.

## Description:
Processes a pandas Series to calculate fundamental statistical measures including total count, missing value percentages, and memory usage, updating the provided summary dictionary with these metrics. This function serves as a specialized implementation for pandas Series data types within the broader profiling framework.

## Args:
    config (Settings): Configuration object containing profiling settings, particularly the memory_deep flag for memory usage calculation.
    series (pd.Series): The pandas Series to analyze and compute statistics for.
    summary (dict): Dictionary containing existing summary statistics that will be updated with new computed values.

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing the unchanged config, the unchanged series, and the updated summary dictionary with new statistical entries.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
    - The series parameter must be a valid pandas Series object
    - The summary dictionary must contain an "n_missing" key with numeric value
    - Config parameter must be a valid Settings object
    
    Postconditions:
    - The summary dictionary will contain updated keys: "n", "p_missing", "count", and "memory_size"
    - The returned tuple maintains the same objects with updated summary

## Side Effects:
    - Modifies the input summary dictionary in-place via the update() method
    - Calls series.memory_usage() which may involve memory allocation/deallocation
    - No external I/O operations or state mutations beyond the summary dictionary modification

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_describe_generic] --> B{series length > 0?}
    B -- Yes --> C[Calculate p_missing = n_missing / length]
    B -- No --> D[Set p_missing = 0]
    C --> E[Update summary with n, p_missing, count, memory_size]
    D --> E
    E --> F[Return (config, series, summary)]
```

## Examples:
    # Basic usage
    config = Settings()
    series = pd.Series([1, 2, None, 4])
    summary = {"n_missing": 1}
    updated_config, updated_series, updated_summary = pandas_describe_generic(config, series, summary)
    
    # Resulting summary contains: {"n_missing": 1, "n": 4, "p_missing": 0.25, "count": 3, "memory_size": <bytes>}

