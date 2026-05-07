# `describe_supported_spark.py`

## `src.ydata_profiling.model.spark.describe_supported_spark.describe_supported_spark` · *function*

## Summary:
Computes and updates statistical measures for Spark DataFrame series including distinct counts, uniqueness metrics, and their proportions.

## Description:
This function enhances a summary dictionary with additional statistical information for Spark DataFrames. It calculates distinct value counts, unique value counts, and their respective proportions based on the existing summary data. The function serves as a Spark-specific implementation of the general profiling logic, extracting the computation of descriptive statistics from the main profiling pipeline to maintain clean separation of concerns.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (DataFrame): Spark DataFrame containing the data series to analyze (typically a single column of values)
    summary (dict): Dictionary containing existing summary statistics including 'count' and 'value_counts' keys

## Returns:
    Tuple[Settings, DataFrame, dict]: Returns the unchanged config, series, and updated summary dictionary with new keys: 'n_distinct', 'p_distinct', 'is_unique', 'n_unique', 'p_unique'

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - The summary dictionary must contain 'count' key with numeric value
        - The summary dictionary must contain 'value_counts' key with a Spark DataFrame
        - The 'value_counts' DataFrame must have columns that support the .count() operation
    Postconditions:
        - The summary dictionary will contain the following new keys:
          * 'n_distinct': Number of distinct values
          * 'p_distinct': Proportion of distinct values (n_distinct/count)
          * 'is_unique': Boolean indicating if all values are unique
          * 'n_unique': Number of unique values (appearing once)
          * 'p_unique': Proportion of unique values (n_unique/count)

## Side Effects:
    - Modifies the input summary dictionary in-place by adding new keys
    - No external I/O operations or state mutations beyond the summary dictionary modification

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{summary["count"] exists?}
    B -- Yes --> C[Get n_distinct = summary["value_counts"].count()]
    B -- No --> D[Error or fallback]
    C --> E[Update summary["n_distinct"] = n_distinct]
    E --> F[Calculate p_distinct = n_distinct / count if count > 0 else 0]
    F --> G[Update summary["p_distinct"] = p_distinct]
    G --> H[Get n_unique = summary["value_counts"].where("count == 1").count()]
    H --> I[Update summary["n_unique"] = n_unique]
    I --> J[Calculate is_unique = n_unique == count]
    J --> K[Update summary["is_unique"] = is_unique]
    K --> L[Calculate p_unique = n_unique / count]
    L --> M[Update summary["p_unique"] = p_unique]
    M --> N[Return (config, series, summary)]
```

## Examples:
    # Basic usage with a Spark DataFrame
    config = Settings()
    spark_df = spark.createDataFrame([(1,), (2,), (2,), (3,)], ["value"])
    summary = {"count": 4, "value_counts": spark_df.groupBy("value").count()}
    updated_config, updated_series, updated_summary = describe_supported_spark(config, spark_df, summary)
    
    # Resulting summary will contain:
    # {
    #   "count": 4,
    #   "value_counts": spark_df.groupBy("value").count(),
    #   "n_distinct": 3,
    #   "p_distinct": 0.75,
    #   "is_unique": False,
    #   "n_unique": 2,
    #   "p_unique": 0.5
    # }

