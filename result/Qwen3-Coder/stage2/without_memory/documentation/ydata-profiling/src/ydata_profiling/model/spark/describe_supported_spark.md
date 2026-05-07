# `describe_supported_spark.py`

## `src.ydata_profiling.model.spark.describe_supported_spark.describe_supported_spark` · *function*

## Summary:
Computes and updates statistical metrics for Spark DataFrame series profiling, including distinct value counts, uniqueness indicators, and percentage calculations.

## Description:
This function extends the basic profiling capabilities for Spark DataFrames by calculating additional statistical measures from the provided summary data. It modifies the summary dictionary in-place to include metrics such as the number and percentage of distinct values, uniqueness indicators, and unique value counts. The function serves as a Spark-specific implementation that complements the base `describe_supported` algorithm.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (DataFrame): Spark DataFrame containing the data series to profile
    summary (dict): Dictionary containing existing summary statistics that will be updated with new metrics

## Returns:
    Tuple[Settings, DataFrame, dict]: The unchanged config, series, and updated summary dictionary

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The summary dictionary must contain a "count" key with numeric value
    - The summary dictionary must contain a "value_counts" key with a Spark DataFrame
    - The "value_counts" DataFrame must have columns that support the .count() operation
    
    Postconditions:
    - The summary dictionary will contain updated keys: "n_distinct", "p_distinct", "is_unique", "n_unique", "p_unique"
    - All computed values are properly bounded (division by zero handled)

## Side Effects:
    - Modifies the input summary dictionary in-place by adding new keys
    - No external I/O operations or state mutations beyond the summary dictionary modification

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_supported_spark] --> B{summary["count"] > 0?}
    B -- Yes --> C[Calculate n_distinct]
    B -- No --> D[Set n_distinct = 0]
    C --> E[Update summary["n_distinct"]]
    D --> E
    E --> F[Calculate p_distinct = n_distinct / count]
    F --> G[Update summary["p_distinct"]]
    G --> H[Calculate n_unique]
    H --> I[Update summary["is_unique"]]
    I --> J[Update summary["n_unique"]]
    J --> K[Calculate p_unique = n_unique / count]
    K --> L[Update summary["p_unique"]]
    L --> M[Return config, series, summary]
```

## Examples:
    # Basic usage with a Spark DataFrame
    config = Settings()
    spark_df = spark.createDataFrame([(1,), (2,), (3,)], ["value"])
    summary = {"count": 3, "value_counts": spark_df}
    result_config, result_series, result_summary = describe_supported_spark(config, spark_df, summary)
    
    # Result summary will contain additional keys:
    # {"count": 3, "value_counts": spark_df, "n_distinct": 3, "p_distinct": 1.0, "is_unique": True, "n_unique": 3, "p_unique": 1.0}

