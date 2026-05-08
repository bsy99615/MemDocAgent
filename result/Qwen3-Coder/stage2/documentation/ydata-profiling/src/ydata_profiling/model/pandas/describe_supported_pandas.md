# `describe_supported_pandas.py`

## `src.ydata_profiling.model.pandas.describe_supported_pandas.pandas_describe_supported` · *function*

## Summary:
Computes descriptive statistics for pandas Series including distinct counts, uniqueness metrics, and proportion calculations.

## Description:
Processes a pandas Series description dictionary to calculate additional statistical measures such as distinct value counts, unique value counts, and their respective proportions. This function serves as a pandas-specific implementation detail for generating comprehensive series summaries in data profiling workflows.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (pd.Series): The pandas Series being analyzed
    series_description (dict): Dictionary containing pre-computed series statistics including 'count' and 'value_counts_without_nan'

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing:
        - config: Original configuration settings unchanged
        - series: Original pandas Series unchanged  
        - stats: Updated dictionary with additional computed statistics including:
            - n_distinct: Number of distinct values (length of value_counts_without_nan)
            - p_distinct: Proportion of distinct values (distinct_count / count if count > 0 else 0)
            - is_unique: Boolean indicating if all values are unique (unique_count == count and count > 0)
            - n_unique: Number of unique values (appearing exactly once)
            - p_unique: Proportion of unique values (unique_count / count if count > 0 else 0)

## Raises:
    KeyError: If 'count' or 'value_counts_without_nan' keys are missing from series_description dictionary

## Constraints:
    Preconditions:
        - series_description must contain 'count' key with numeric value
        - series_description must contain 'value_counts_without_nan' key with valid pandas Series or similar object
        - count must be a non-negative number
    
    Postconditions:
        - Returned stats dictionary will contain all original series_description entries plus new computed statistics
        - Computed statistics include: n_distinct, p_distinct, is_unique, n_unique, p_unique

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_describe_supported] --> B[Extract count from series_description["count"]]
    B --> C[Extract value_counts from series_description["value_counts_without_nan"]]
    C --> D[Calculate distinct_count = len(value_counts)]
    D --> E[Calculate unique_count = value_counts.where(value_counts == 1).count()]
    E --> F[Create stats dictionary with computed values]
    F --> G[Update stats with original series_description]
    G --> H[Return config, series, stats]
```

## Examples:
    # Basic usage with typical series description
    config = Settings()
    series = pd.Series([1, 2, 2, 3, 3, 3])
    series_desc = {
        "count": 6,
        "value_counts_without_nan": pd.Series([1, 2, 3], index=[1, 2, 3])
    }
    result_config, result_series, result_stats = pandas_describe_supported(config, series, series_desc)
    
    # Result stats will include:
    # {"n_distinct": 3, "p_distinct": 0.5, "is_unique": False, "n_unique": 1, "p_unique": 0.167, ...}

