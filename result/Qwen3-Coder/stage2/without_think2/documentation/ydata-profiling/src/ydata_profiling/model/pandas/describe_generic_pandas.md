# `describe_generic_pandas.py`

## `src.ydata_profiling.model.pandas.describe_generic_pandas.pandas_describe_generic` · *function*

## Summary:
Updates a summary dictionary with basic statistics and metadata for a pandas Series.

## Description:
This function computes and adds fundamental statistical properties to a summary dictionary for a given pandas Series. It calculates the total length, missing value proportions, count of non-missing values, and memory usage. This function serves as a standardized way to enrich summary statistics with common metadata across different data profiling operations.

## Args:
    config (Settings): Configuration object containing profiling settings, particularly the memory_deep flag for memory usage calculation.
    series (pd.Series): The pandas Series to analyze and summarize.
    summary (dict): Dictionary containing existing summary statistics that will be updated with new computed values.

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing the unchanged config, series, and the updated summary dictionary.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
        - The series parameter must be a valid pandas Series object.
        - The summary dictionary must be mutable and contain an "n_missing" key with a numeric value.
        - The config parameter must be a valid Settings object with a memory_deep attribute.
    Postconditions:
        - The summary dictionary will contain the following keys: "n", "p_missing", "count", and "memory_size".
        - All values in the summary dictionary remain unchanged except for the added keys.

## Side Effects:
    - Modifies the input summary dictionary in-place via the update() method.
    - Calls series.memory_usage() which may trigger memory allocation or access patterns depending on the deep parameter.

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_describe_generic] --> B{length > 0?}
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
    # Resulting summary contains: {"n_missing": 1, "n": 4, "p_missing": 0.25, "count": 3, "memory_size": 40}

