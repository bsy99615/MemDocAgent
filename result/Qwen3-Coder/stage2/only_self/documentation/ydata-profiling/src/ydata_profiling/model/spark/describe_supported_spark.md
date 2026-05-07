# `describe_supported_spark.py`

## `src.ydata_profiling.model.spark.describe_supported_spark.describe_supported_spark` · *function*

## Summary:
Computes and updates descriptive statistics for Spark DataFrame series, including distinct value counts, uniqueness metrics, and percentage calculations.

## Description:
This function processes a Spark DataFrame summary dictionary to compute additional statistical measures related to value uniqueness and distinctness. It calculates the number and percentage of distinct values, identifies if all values are unique, and computes the number and percentage of unique values. The function modifies the summary dictionary in-place and returns the updated configuration, DataFrame, and summary.

The function is part of the Spark-specific profiling implementation and serves as a bridge between the general profiling logic and Spark-specific data processing capabilities. It extracts information from the existing summary structure and enriches it with additional metrics that are meaningful for Spark DataFrames.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (DataFrame): Spark DataFrame containing the data series to analyze
    summary (dict): Dictionary containing existing summary statistics for the series

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the unchanged configuration, the unchanged DataFrame, and the updated summary dictionary with additional computed statistics

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The summary dictionary must contain a "count" key with numeric value
    - The summary dictionary must contain a "value_counts" key with a Spark DataFrame
    - The "value_counts" DataFrame must have columns that support the .count() operation
    
    Postconditions:
    - The summary dictionary will contain the following keys:
      * "n_distinct": Number of distinct values
      * "p_distinct": Percentage of distinct values (0 if count is 0)
      * "is_unique": Boolean indicating if all values are unique
      * "n_unique": Number of unique values (appearing exactly once)
      * "p_unique": Percentage of unique values

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_supported_spark] --> B[Extract count from summary]
    B --> C[Calculate n_distinct from value_counts.count()]
    C --> D[Update summary with n_distinct]
    D --> E[Calculate p_distinct = n_distinct / count if count > 0]
    E --> F[Update summary with p_distinct]
    F --> G[Filter value_counts where count == 1]
    G --> H[Calculate n_unique from filtered count]
    H --> I[Update summary with n_unique]
    I --> J[Calculate is_unique = n_unique == count]
    J --> K[Update summary with is_unique]
    K --> L[Calculate p_unique = n_unique / count]
    L --> M[Update summary with p_unique]
    M --> N[Return config, series, summary]
```

## Examples:
    # Basic usage with a Spark DataFrame
    config = Settings()
    spark_df = spark.createDataFrame([(1,), (2,), (3,)], ["col1"])
    summary = {"count": 3, "value_counts": spark_df.groupBy("col1").count()}
    
    updated_config, updated_series, updated_summary = describe_supported_spark(config, spark_df, summary)
    
    # The summary now contains additional keys:
    # - "n_distinct": 3
    # - "p_distinct": 1.0
    # - "is_unique": True
    # - "n_unique": 3
    # - "p_unique": 1.0

