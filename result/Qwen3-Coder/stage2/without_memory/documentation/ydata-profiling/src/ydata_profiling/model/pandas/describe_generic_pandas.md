# `describe_generic_pandas.py`

## `src.ydata_profiling.model.pandas.describe_generic_pandas.pandas_describe_generic` · *function*

## Summary:
Computes and updates generic descriptive statistics for a pandas Series within a profiling context.

## Description:
This function calculates fundamental statistics for a pandas Series including total count, missing value proportions, and memory usage. It updates the provided summary dictionary with these computed values and returns the updated configuration, series, and summary. This function serves as a pandas-specific implementation of the generic describe functionality, extracting common statistical computations into a reusable component.

## Args:
    config (Settings): Configuration object containing profiling settings including memory_deep flag for memory usage calculation
    series (pd.Series): The pandas Series to analyze
    summary (dict): Dictionary containing existing summary statistics, particularly requiring 'n_missing' key for missing value calculations

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing the unchanged config object, the unchanged series object, and the summary dictionary with additional computed statistics added in-place

## Raises:
    KeyError: When the summary dictionary does not contain the required 'n_missing' key
    AttributeError: When the series object doesn't support the required methods (memory_usage, len)

## Constraints:
    Preconditions:
        - The summary dictionary must contain an 'n_missing' key with a numeric value
        - The series parameter must be a valid pandas Series object
        - The config parameter must be a properly initialized Settings object
    
    Postconditions:
        - The summary dictionary will contain the following keys: 'n', 'p_missing', 'count', 'memory_size'
        - All input parameters remain unchanged except for the updated summary dictionary

## Side Effects:
    - Modifies the input summary dictionary in-place via the update() method
    - Calls pandas Series memory_usage() method which may trigger memory allocation

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
```python
# Basic usage
config = Settings()
series = pd.Series([1, 2, None, 4])
summary = {"n_missing": 1}
updated_config, updated_series, updated_summary = pandas_describe_generic(config, series, summary)

# Resulting summary will contain:
# {'n': 4, 'p_missing': 0.25, 'count': 3, 'memory_size': <memory_usage_value>}
```

