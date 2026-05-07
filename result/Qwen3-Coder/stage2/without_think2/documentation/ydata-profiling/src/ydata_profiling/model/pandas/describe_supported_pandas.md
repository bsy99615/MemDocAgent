# `describe_supported_pandas.py`

## `src.ydata_profiling.model.pandas.describe_supported_pandas.pandas_describe_supported` · *function*

## Summary:
Computes and enriches statistical measures for pandas Series data, specifically calculating distinct and unique value counts along with their proportions.

## Description:
This function takes a pandas Series and its descriptive statistics, then calculates additional statistical properties such as the number and proportion of distinct values, whether the series contains unique values, and the count and proportion of unique values. It serves as a specialized processor for pandas data within the profiling framework, extending basic series descriptions with enhanced statistical insights.

The function is designed to be used as part of a pipeline where series data is processed through various descriptive functions. It's typically called after initial series analysis has been performed by other functions in the profiling system, particularly those that compute basic statistics like count and value counts.

This logic is extracted into its own function to separate concerns: while other functions may compute basic statistics, this function focuses specifically on deriving advanced statistical properties from existing computed values. This modularization allows for easier testing, maintenance, and extension of statistical computations without affecting the core data processing pipeline.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (pd.Series): The pandas Series being analyzed
    series_description (dict): Dictionary containing pre-computed statistics about the series, including 'count' and 'value_counts_without_nan'

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing the unchanged configuration, the original series, and an updated dictionary with additional statistical properties added to the original series_description. The updated dictionary includes keys: 'n_distinct', 'p_distinct', 'is_unique', 'n_unique', 'p_unique' along with all original keys from series_description.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The input series_description dictionary must contain keys 'count' and 'value_counts_without_nan'
    - The 'count' value should be a numeric value representing total observations
    - The 'value_counts_without_nan' should be a pandas Series or similar object with a length method
    
    Postconditions:
    - The returned dictionary will contain all original keys from series_description plus new keys: 'n_distinct', 'p_distinct', 'is_unique', 'n_unique', 'p_unique'

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B[Extract count from series_description]
    B --> C[Extract value_counts_without_nan from series_description]
    C --> D[Calculate distinct_count = len(value_counts_without_nan)]
    D --> E[Calculate unique_count = value_counts_without_nan.where(value_counts_without_nan == 1).count()]
    E --> F[Create stats dictionary with calculated values]
    F --> G[Update stats with series_description]
    G --> H[Return config, series, stats]
```

## Examples:
```python
# Typical usage in a profiling pipeline
config = Settings()
series = pd.Series([1, 2, 2, 3, 3, 3])
series_description = {
    "count": 6,
    "value_counts_without_nan": pd.Series([1, 2, 3]).value_counts()
}
result_config, result_series, result_stats = pandas_describe_supported(config, series, series_description)
```

