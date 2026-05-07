# `describe_boolean_spark.py`

## `src.ydata_profiling.model.spark.describe_boolean_spark.describe_boolean_1d_spark` · *function*

## Summary:
Extracts the most frequent value and its count from boolean data summary for Spark DataFrames.

## Description:
This function processes a summary dictionary containing value counts for boolean data in Spark DataFrames. It retrieves the top (most frequent) value and its frequency from the value_counts collection and updates the summary dictionary with these values. This is a Spark-specific implementation that operates on PySpark DataFrames.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): PySpark DataFrame being analyzed
    summary (dict): Dictionary containing summary statistics including value_counts

## Returns:
    Tuple[Settings, DataFrame, dict]: The unchanged config, df, and updated summary dictionary containing 'top' and 'freq' keys

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The summary dictionary must contain a 'value_counts' key with a valid Spark DataFrame or collection
    - The value_counts collection must have at least one element
    - The first element of value_counts must have at least two elements (index 0 and 1)

    Postconditions:
    - The summary dictionary will contain 'top' and 'freq' keys
    - The 'top' key contains the most frequent value from value_counts
    - The 'freq' key contains the frequency count of the most frequent value

## Side Effects:
    - Modifies the input summary dictionary in-place by adding 'top' and 'freq' keys
    - No external I/O operations or state mutations beyond the summary update

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_boolean_1d_spark] --> B{summary['value_counts'] exists?}
    B -- Yes --> C[Get first() element from value_counts]
    C --> D[Extract top[0] as value and top[1] as frequency]
    D --> E[Update summary with {'top': top[0], 'freq': top[1]}]
    E --> F[Return config, df, summary]
    B -- No --> G[Exception or undefined behavior]
```

## Examples:
    # Typical usage in Spark profiling workflow
    config, df, summary = describe_boolean_1d_spark(settings, spark_df, summary_dict)
    # After execution, summary_dict contains 'top' and 'freq' keys
    # representing the most frequent boolean value and its count

