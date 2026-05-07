# `describe_generic_spark.py`

## `src.ydata_profiling.model.spark.describe_generic_spark.describe_generic_spark` · *function*

## Summary:
Computes basic descriptive statistics for a Spark DataFrame and updates the summary dictionary with count, missing value percentages, and memory size information.

## Description:
This function processes a Spark DataFrame to calculate fundamental statistics such as total row count, missing value proportions, and sets memory size to zero. It serves as a Spark-specific implementation of generic data description logic, extracting common statistical computations from the broader profiling pipeline. The function is designed to work with PySpark DataFrames and integrates with the ydata-profiling configuration system.

## Args:
    config (Settings): Configuration object containing profiling settings and parameters
    df (DataFrame): PySpark DataFrame to analyze
    summary (dict): Dictionary containing summary statistics that will be updated with computed values

## Returns:
    Tuple[Settings, DataFrame, dict]: Returns the unchanged config, the original DataFrame, and the updated summary dictionary

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The input DataFrame must be a valid PySpark DataFrame
    - The summary dictionary must be mutable and contain key "n_missing"
    - The config parameter must be a valid Settings object

    Postconditions:
    - The summary dictionary will contain updated keys: "n", "p_missing", "count", and "memory_size"
    - The returned tuple maintains the original DataFrame and config unchanged

## Side Effects:
    - Modifies the input summary dictionary in-place by adding/updating keys
    - Triggers a Spark computation via df.count() which may cause data shuffling and processing

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_generic_spark] --> B[df.count() to get length]
    B --> C[Update summary["n"] = length]
    C --> D[Update summary["p_missing"] = summary["n_missing"] / length]
    D --> E[Update summary["count"] = length - summary["n_missing"]]
    E --> F[Set summary["memory_size"] = 0]
    F --> G[Return (config, df, summary)]
```

## Examples:
    # Basic usage with a Spark DataFrame
    from ydata_profiling.config import Settings
    config = Settings()
    spark_df = spark.createDataFrame([(1, "a"), (2, "b"), (None, "c")], ["id", "value"])
    summary = {"n_missing": 1}
    result_config, result_df, result_summary = describe_generic_spark(config, spark_df, summary)
    
    # Resulting summary will contain:
    # {
    #     "n": 3,
    #     "p_missing": 0.3333333333333333,
    #     "count": 2,
    #     "memory_size": 0
    # }
    
    # Usage in a profiling context
    # This function would typically be called internally by the profiling framework
    # when processing Spark DataFrames for statistical summaries

