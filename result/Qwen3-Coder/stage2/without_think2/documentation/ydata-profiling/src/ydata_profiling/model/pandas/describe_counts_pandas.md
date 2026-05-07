# `describe_counts_pandas.py`

## `src.ydata_profiling.model.pandas.describe_counts_pandas.pandas_describe_counts` · *function*

## Summary:
Analyzes a pandas Series to determine hashability, compute value counts, and identify missing values while updating summary statistics.

## Description:
This function processes a pandas Series to compute value counts while handling missing values appropriately. It determines whether the series values are hashable, which affects how value counts are processed and sorted. The function updates the summary dictionary with various computed statistics including value counts, missing value counts, and ordering information. This logic is extracted into a separate function to encapsulate the complexity of handling different data types and missing value scenarios, providing a clean interface for series analysis.

## Args:
    config (Settings): Configuration settings object containing analysis parameters
    series (pandas.Series): Input pandas Series to analyze
    summary (dict): Dictionary to be updated with computed statistics and metadata

## Returns:
    Tuple[Settings, pandas.Series, dict]: The unchanged config, series, and updated summary dictionary

## Raises:
    None explicitly raised - uses bare except clause for hashability check

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - series must be a pandas Series
        - summary must be a mutable dictionary
    Postconditions:
        - summary dictionary will contain keys: 'hashable', 'value_counts_without_nan', 'ordering', 'n_missing'
        - The returned tuple maintains the original config and series unchanged

## Side Effects:
    - Modifies the input summary dictionary by adding/updating keys
    - No external I/O operations or state mutations beyond the summary update

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{Can create set from index?}
    B -- Yes --> C[Set hashable=True]
    B -- No --> D[Set hashable=False]
    C --> E[Filter positive value counts]
    D --> F[Get missing count via isna()]
    E --> G{Has null index?}
    G -- Yes --> H[Calculate n_missing]
    G -- No --> I[n_missing = 0]
    H --> J[Remove null values from counts]
    I --> J
    J --> K[Update summary with value_counts_without_nan]
    K --> L{Can sort index?}
    L -- Yes --> M[Set ordering=True]
    L -- No --> N[Set ordering=False]
    F --> O[Set ordering=False]
    M --> P[Update summary with sorted value counts]
    N --> P
    O --> P
    P --> Q[Update summary with ordering and n_missing]
    Q --> R[Return config, series, summary]
```

## Examples:
    # Basic usage with a hashable series
    config = Settings()
    series = pd.Series([1, 2, 2, 3, None])
    summary = {}
    result_config, result_series, result_summary = pandas_describe_counts(config, series, summary)
    
    # Usage with unhashable series (will set hashable=False)
    unhashable_series = pd.Series([{'a': 1}, {'a': 1}, None])
    summary = {}
    result_config, result_series, result_summary = pandas_describe_counts(config, unhashable_series, summary)

