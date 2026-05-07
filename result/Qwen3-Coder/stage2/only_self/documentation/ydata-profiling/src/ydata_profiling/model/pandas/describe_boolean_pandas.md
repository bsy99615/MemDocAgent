# `describe_boolean_pandas.py`

## `src.ydata_profiling.model.pandas.describe_boolean_pandas.pandas_describe_boolean_1d` · *function*

## Summary:
Processes and enriches summary statistics for boolean data series by calculating top value frequency and imbalance score.

## Description:
This function enhances the summary statistics for boolean data by extracting the most frequent value and its count, and computing an imbalance score to measure the distribution skewness of boolean values. It serves as a specialized processor for boolean data types within the profiling framework, ensuring consistent statistical reporting across different data types.

The function is typically called as part of the data profiling pipeline when analyzing boolean columns, particularly after initial value counting operations have been performed. It's designed to be used in conjunction with other describe_*_1d functions to maintain uniform processing patterns across different data types.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (pd.Series): The boolean data series being analyzed
    summary (dict): Dictionary containing pre-computed summary statistics including "value_counts_without_nan"

## Returns:
    Tuple[Settings, pd.Series, dict]: Returns the unchanged config, series, and updated summary dictionary with additional keys:
        - "top": Most frequent value in the series
        - "freq": Frequency count of the most frequent value  
        - "imbalance": Imbalance score measuring distribution skewness

## Raises:
    None explicitly raised - however, underlying operations may raise exceptions if summary data is malformed or missing required keys.

## Constraints:
    Preconditions:
        - The summary dictionary must contain "value_counts_without_nan" key with valid pandas Series data
        - The value_counts Series should have at least one entry
        - The series should contain boolean data (though not validated in this function)

    Postconditions:
        - The summary dictionary will contain "top", "freq", and "imbalance" keys
        - All input parameters remain unchanged

## Side Effects:
    - Modifies the input summary dictionary in-place by adding new keys
    - No external I/O operations or state mutations beyond the summary update

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{summary["value_counts_without_nan"] exists?}
    B -- Yes --> C[Extract value_counts]
    C --> D[Update summary with "top" and "freq"]
    D --> E[Calculate imbalance score]
    E --> F[Return config, series, summary]
    B -- No --> G[Exception/Undefined behavior]
```

## Examples:
```python
# Typical usage in profiling pipeline
config = Settings()
series = pd.Series([True, False, True, True, False])
summary = {"value_counts_without_nan": pd.Series([True: 3, False: 2])}

config, series, summary = pandas_describe_boolean_1d(config, series, summary)
# Result: summary contains "top": True, "freq": 3, "imbalance": score
```

