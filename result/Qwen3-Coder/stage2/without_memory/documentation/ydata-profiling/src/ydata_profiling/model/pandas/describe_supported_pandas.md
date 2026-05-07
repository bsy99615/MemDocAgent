# `describe_supported_pandas.py`

## `src.ydata_profiling.model.pandas.describe_supported_pandas.pandas_describe_supported` · *function*

## Summary:
Computes and enriches series description with statistical measures for pandas Series data.

## Description:
Processes a pandas Series description dictionary to calculate key statistical properties including distinct value counts, uniqueness metrics, and updates the description with these computed statistics. This function implements the pandas-specific version of the abstract `describe_supported` algorithm and is typically used in data profiling pipelines to enhance series metadata with descriptive statistics.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (pd.Series): The pandas Series being analyzed
    series_description (dict): Dictionary containing existing series metadata including 'count' and 'value_counts_without_nan' keys

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing the unchanged config, the unchanged series, and the updated series_description with additional statistical fields

## Raises:
    None: This function does not explicitly raise exceptions, but will propagate KeyError if required keys are missing from series_description

## Constraints:
    Preconditions:
        - series_description must contain 'count' key with numeric value
        - series_description must contain 'value_counts_without_nan' key with valid count data structure
        - series must be a valid pandas Series
    
    Postconditions:
        - The returned series_description dictionary will contain additional keys: 'n_distinct', 'p_distinct', 'is_unique', 'n_unique', 'p_unique'
        - All original keys from series_description are preserved in the returned dictionary

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_describe_supported] --> B[Extract count from series_description]
    B --> C[Extract value_counts_without_nan from series_description]
    C --> D[Calculate distinct_count = len(value_counts)]
    D --> E[Calculate unique_count = value_counts.where(value_counts == 1).count()]
    E --> F[Create stats dictionary with computed metrics]
    F --> G[Update series_description with stats]
    G --> H[Return config, series, updated_description]
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

updated_config, updated_series, updated_description = pandas_describe_supported(config, series, series_description)
# updated_description now contains additional statistical fields:
# 'n_distinct': 3, 'p_distinct': 0.5, 'is_unique': False, 'n_unique': 0, 'p_unique': 0.0
```

