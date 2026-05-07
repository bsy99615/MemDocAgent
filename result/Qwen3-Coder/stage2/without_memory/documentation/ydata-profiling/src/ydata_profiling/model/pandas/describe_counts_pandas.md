# `describe_counts_pandas.py`

## `src.ydata_profiling.model.pandas.describe_counts_pandas.pandas_describe_counts` · *function*

## Summary:
Computes value counts and related statistics for a pandas Series, determining hashability and ordering properties for profiling purposes.

## Description:
This function analyzes a pandas Series to compute value counts while preserving NaN values, determines if the index is hashable, and calculates missing value counts. It updates the provided summary dictionary with computed statistics including value counts without NaN, ordering status, and missing value counts. The function is designed to be part of a data profiling pipeline where detailed statistical information about series data is required.

The logic is extracted into its own function to separate the concerns of value counting and statistical computation from the main profiling workflow, allowing for better modularity and testability of the data analysis components.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (pd.Series): The pandas Series to analyze for value counts and statistics
    summary (dict): Dictionary to be updated with computed statistics and metadata

## Returns:
    Tuple[Settings, pd.Series, dict]: The original arguments returned unchanged, but with the summary dictionary updated with computed statistics including:
        - hashable: Boolean indicating if the series index is hashable
        - value_counts_without_nan: Series of value counts excluding NaN values
        - value_counts_index_sorted: Series with sorted index values (when ordering is possible)
        - ordering: Boolean indicating if index values can be ordered
        - n_missing: Count of missing values in the series

## Raises:
    None explicitly raised - uses a broad except clause that catches all exceptions when checking hashability

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - series must be a valid pandas Series
        - summary must be a mutable dictionary
    
    Postconditions:
        - The summary dictionary will contain updated keys related to value counts and series properties
        - All input parameters remain unchanged except for the modified summary dictionary

## Side Effects:
    - Modifies the provided summary dictionary in-place by adding computed statistics
    - No external I/O operations or state mutations beyond updating the summary dictionary

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_describe_counts] --> B{Can compute value_counts?}
    B -- Yes --> C{Is index hashable?}
    C -- Yes --> D[Compute value_counts_with_nan]
    D --> E[Filter positive counts]
    E --> F[Check for null index values]
    F --> G{Any null indices?}
    G -- Yes --> H[Calculate n_missing from null values]
    H --> I[Create value_counts_without_nan]
    G -- No --> J[n_missing = 0]
    J --> I
    I --> K[Try sort_index for ordering]
    K --> L{Sort successful?}
    L -- Yes --> M[Set ordering = True]
    L -- No --> N[Set ordering = False]
    M --> O[Update summary with value_counts_index_sorted]
    N --> O
    O --> P[Update summary with value_counts_without_nan]
    P --> Q[Update summary with hashable = True]
    Q --> R[End]
    
    C -- No --> S[Calculate n_missing via isna().sum()]
    S --> T[Set ordering = False]
    T --> U[Update summary with hashable = False]
    U --> R
    
    B -- No --> V[Set hashable = False]
    V --> W[Calculate n_missing via isna().sum()]
    W --> X[Set ordering = False]
    X --> Y[Update summary with hashable = False]
    Y --> R
```

## Examples:
    # Basic usage with a simple series
    config = Settings()
    series = pd.Series([1, 2, 2, 3, None])
    summary = {}
    result_config, result_series, result_summary = pandas_describe_counts(config, series, summary)
    
    # The summary now contains:
    # {
    #     'hashable': True,
    #     'value_counts_without_nan': pd.Series([1, 2, 3], index=[1, 2, 3]),
    #     'ordering': True,
    #     'n_missing': 1
    # }

