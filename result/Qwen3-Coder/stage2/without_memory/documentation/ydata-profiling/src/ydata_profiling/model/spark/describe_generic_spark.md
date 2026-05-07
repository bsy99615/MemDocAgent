# `describe_generic_spark.py`

## `src.ydata_profiling.model.spark.describe_generic_spark.describe_generic_spark` · *function*

## Summary:
Updates summary statistics for a Spark DataFrame by computing row counts and related metrics.

## Description:
This function processes a Spark DataFrame to calculate fundamental statistics such as total row count, missing value percentages, and count of non-missing values. It's designed as a Spark-specific variant of a generic description function and updates the provided summary dictionary in-place with computed metrics.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): Spark DataFrame to analyze
    summary (dict): Dictionary containing summary statistics that will be updated with computed values

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the unchanged config, the original DataFrame, and the updated summary dictionary

## Raises:
    None explicitly raised, but Spark operations may raise exceptions related to DataFrame processing

## Constraints:
    Preconditions:
    - The input DataFrame must be a valid PySpark DataFrame
    - The summary dictionary must be mutable and contain keys 'n_missing' and 'memory_size' (though 'memory_size' is set to 0)
    - The 'n_missing' key in summary must have a numeric value
    
    Postconditions:
    - The summary dictionary is modified in-place to include:
      * 'n': Total number of rows in the DataFrame
      * 'p_missing': Proportion of missing values (n_missing / n)
      * 'count': Count of non-missing values (n - n_missing)
      * 'memory_size': Set to 0 (placeholder for memory calculation)

## Side Effects:
    - Modifies the input summary dictionary in-place by adding/updating keys
    - Triggers a Spark job execution via df.count() operation

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_generic_spark] --> B[Get DataFrame row count]
    B --> C[Update summary['n'] with count]
    C --> D[Calculate p_missing = n_missing / n]
    D --> E[Update summary['p_missing']]
    E --> F[Calculate count = n - n_missing]
    F --> G[Update summary['count']]
    G --> H[Set summary['memory_size'] = 0]
    H --> I[Return config, df, summary]
```

## Examples:
    # Basic usage
    config = Settings()
    spark_df = spark.createDataFrame([(1, None), (2, "value")], ["id", "value"])
    summary = {"n_missing": 1}
    updated_config, updated_df, updated_summary = describe_generic_spark(config, spark_df, summary)
    
    # After execution, summary contains:
    # {
    #     "n_missing": 1,
    #     "n": 2,
    #     "p_missing": 0.5,
    #     "count": 1,
    #     "memory_size": 0
    # }

