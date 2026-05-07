# `describe_boolean_spark.py`

## `src.ydata_profiling.model.spark.describe_boolean_spark.describe_boolean_1d_spark` · *function*

## Summary:
Extracts the most frequent value and its frequency from boolean data summary for Spark DataFrame processing.

## Description:
This function processes a boolean data summary dictionary to extract the top (most frequent) value and its frequency count, updating the summary with these values. It serves as a Spark-specific implementation that complements the base `describe_boolean_1d` algorithm by handling the Spark DataFrame context. The function is designed to work within the ydata-profiling pipeline where boolean data needs to be summarized with frequency information.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): Spark DataFrame containing the boolean data
    summary (dict): Dictionary containing boolean data summary information, including 'value_counts' key

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the unchanged config, df, and updated summary dictionary with 'top' and 'freq' keys added

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The summary dictionary must contain a 'value_counts' key with a valid Spark DataFrame or collection
    - The 'value_counts' should be ordered with the most frequent value first
    - The first item in value_counts must have at least two elements (value and frequency)

    Postconditions:
    - The summary dictionary will contain 'top' and 'freq' keys with appropriate values
    - The returned tuple maintains the original config and df unchanged

## Side Effects:
    - Modifies the input summary dictionary in-place by adding 'top' and 'freq' keys
    - No external I/O operations or state mutations beyond the summary update

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_boolean_1d_spark] --> B[value_counts = summary["value_counts"]]
    B --> C[top = value_counts.first()]
    C --> D[summary.update({"top": top[0], "freq": top[1]})]
    D --> E[Return config, df, summary]
```

## Examples:
    # Typical usage in Spark profiling pipeline
    config = Settings()
    spark_df = spark.createDataFrame([(True,), (False,), (True,)], ["bool_col"])
    summary = {"value_counts": spark_df.groupBy("bool_col").count()}
    
    updated_config, updated_df, updated_summary = describe_boolean_1d_spark(config, spark_df, summary)
    
    # Resulting summary will contain:
    # {"value_counts": ..., "top": True, "freq": 2}
```

