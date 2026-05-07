# `describe_generic_pandas.py`

## `src.ydata_profiling.model.pandas.describe_generic_pandas.pandas_describe_generic` · *function*

## Summary:
Updates summary statistics for a pandas Series with length, missing value percentages, count, and memory usage information.

## Description:
This function computes and updates various descriptive statistics for a pandas Series within the summary dictionary. It calculates the total length, percentage of missing values, count of non-missing values, and memory usage of the series. This function is part of the pandas-specific data profiling implementation and is typically called during the data analysis phase when generating descriptive statistics for individual columns.

## Args:
    config (Settings): Configuration object containing profiling settings, specifically the memory_deep flag for memory usage calculation
    series (pd.Series): The pandas Series to analyze
    summary (dict): Dictionary containing existing summary statistics that will be updated with new computed values

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing the unchanged config, unchanged series, and the updated summary dictionary

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The series parameter must be a valid pandas Series
    - The summary parameter must be a dictionary containing an "n_missing" key
    - Config parameter must be a valid Settings object
    
    Postconditions:
    - The summary dictionary will contain updated keys: "n", "p_missing", "count", and "memory_size"
    - All input parameters remain unchanged except for the modified summary dictionary

## Side Effects:
    - Modifies the summary dictionary in-place by adding/updating keys
    - Calls series.memory_usage() which may involve memory allocation/deallocation
    - No external I/O operations or state mutations beyond modifying the summary dictionary

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{length > 0?}
    B -- Yes --> C[Calculate p_missing = n_missing / length]
    B -- No --> D[p_missing = 0]
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
    
    # Resulting summary will contain:
    # {"n_missing": 1, "n": 4, "p_missing": 0.25, "count": 3, "memory_size": <memory_usage_value>}
```

