# `describe_generic_spark.py`

## `src.ydata_profiling.model.spark.describe_generic_spark.describe_generic_spark` · *function*

## Summary:
Computes basic descriptive statistics for a Spark DataFrame and updates the summary dictionary with row counts and missing value metrics.

## Description:
This function processes a Spark DataFrame to calculate fundamental statistics such as total row count, missing value percentages, and count of non-missing values. It serves as a Spark-specific implementation of generic data description functionality, updating the summary dictionary with computed metrics while preserving the original configuration and DataFrame.

The function is designed to be part of a profiling pipeline where Spark DataFrames require statistical computation similar to what would be done with regular pandas DataFrames, but with Spark's distributed computing capabilities.

## Args:
    config (Settings): Configuration settings object containing profiling parameters
    df (DataFrame): Spark DataFrame to analyze
    summary (dict): Dictionary containing summary statistics that will be updated with computed values

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the original config, the original DataFrame, and the updated summary dictionary

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The input DataFrame must be a valid PySpark DataFrame
    - The summary dictionary must be mutable and contain 'n_missing' key with numeric value
    - Config parameter must be a valid Settings object
    
    Postconditions:
    - The summary dictionary will contain updated keys: 'n', 'p_missing', 'count', and 'memory_size'
    - The returned tuple preserves the original input values except for the modified summary

## Side Effects:
    - Computes the count of rows in the DataFrame via df.count() operation
    - Modifies the input summary dictionary in-place by adding/updating keys
    - Triggers Spark computation when df.count() is called

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_generic_spark] --> B[Get DataFrame row count]
    B --> C[Update summary['n'] with row count]
    C --> D[Calculate summary['p_missing'] = summary['n_missing'] / length]
    D --> E[Calculate summary['count'] = length - summary['n_missing']]
    E --> F[Set summary['memory_size'] = 0]
    F --> G[Return config, df, summary]
```

## Examples:
    # Basic usage
    config = Settings()
    spark_df = spark.createDataFrame([(1, "a"), (2, "b"), (None, "c")], ["id", "name"])
    summary = {"n_missing": 1}
    updated_config, updated_df, updated_summary = describe_generic_spark(config, spark_df, summary)
    
    # Resulting summary will contain:
    # {
    #     "n": 3,
    #     "p_missing": 0.3333333333333333,
    #     "count": 2,
    #     "memory_size": 0,
    #     "n_missing": 1
    # }

