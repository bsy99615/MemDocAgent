# `describe_generic_spark.py`

## `src.ydata_profiling.model.spark.describe_generic_spark.describe_generic_spark` · *function*

## Summary:
Updates summary statistics for a Spark DataFrame by calculating row count and related metrics.

## Description:
This function processes a Spark DataFrame to compute basic statistical information including total row count, missing value percentages, and count of non-missing values. It's designed specifically for Spark DataFrames within the ydata-profiling framework and serves as a Spark-specific implementation of generic data description functionality.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): Spark DataFrame to analyze
    summary (dict): Dictionary containing summary statistics that will be updated with computed values

## Returns:
    Tuple[Settings, DataFrame, dict]: The unchanged config, the original DataFrame, and the updated summary dictionary

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The input DataFrame must be a valid PySpark DataFrame
    - The summary dictionary must contain keys "n_missing" and "memory_size" (though memory_size is set to 0)
    - The config parameter must be a valid Settings object
    
    Postconditions:
    - The summary dictionary will contain updated keys: "n", "p_missing", "count", and "memory_size"
    - The returned tuple maintains the same objects as the input parameters

## Side Effects:
    - Performs a Spark action (df.count()) which triggers computation of the DataFrame
    - Modifies the input summary dictionary in-place by adding/updating keys
    - No external I/O operations or state mutations beyond the summary dictionary modification

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_generic_spark] --> B[df.count() to get length]
    B --> C[Update summary["n"] = length]
    C --> D[Update summary["p_missing"] = summary["n_missing"] / length]
    D --> E[Update summary["count"] = length - summary["n_missing"]]
    E --> F[Update summary["memory_size"] = 0]
    F --> G[Return config, df, summary]
```

## Examples:
    # Basic usage
    config = Settings()
    spark_df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "value"])
    summary = {"n_missing": 0}
    updated_config, updated_df, updated_summary = describe_generic_spark(config, spark_df, summary)
    
    # Usage with missing values
    summary = {"n_missing": 1}
    updated_config, updated_df, updated_summary = describe_generic_spark(config, spark_df, summary)
    # updated_summary will contain: {"n_missing": 1, "n": 2, "p_missing": 0.5, "count": 1, "memory_size": 0}

