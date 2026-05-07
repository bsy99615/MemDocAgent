# `describe_boolean_spark.py`

## `src.ydata_profiling.model.spark.describe_boolean_spark.describe_boolean_1d_spark` · *function*

## Summary:
Extracts the most frequent value and its count from boolean data summary for Spark DataFrames.

## Description:
Processes a summary dictionary containing value counts for boolean data in Spark environments, identifying the top value and its frequency. This function is part of the Spark-specific data profiling pipeline for boolean variables, extracting key statistics needed for reporting.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): Spark DataFrame containing the boolean data
    summary (dict): Dictionary containing summary statistics including 'value_counts' key

## Returns:
    Tuple[Settings, DataFrame, dict]: The unchanged config, df, and updated summary dictionary with 'top' and 'freq' keys added

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The summary dictionary must contain a 'value_counts' key with valid Spark DataFrame data
    - The value_counts DataFrame must have at least one row
    - The first row of value_counts must have at least two columns (value and frequency)

    Postconditions:
    - The summary dictionary will contain 'top' and 'freq' keys with appropriate values
    - The returned tuple maintains the original config and df unchanged

## Side Effects:
    - Modifies the summary dictionary in-place by adding 'top' and 'freq' keys
    - No external I/O operations or state mutations beyond the summary update

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_boolean_1d_spark] --> B{summary['value_counts'] exists?}
    B -- Yes --> C[Get first row of value_counts]
    C --> D[Extract top value and frequency]
    D --> E[Update summary with 'top' and 'freq']
    E --> F[Return config, df, summary]
    B -- No --> G[Exception or undefined behavior]
```

## Examples:
    # Typical usage in profiling pipeline
    config, df, summary = describe_boolean_1d_spark(settings, spark_df, summary_dict)
    # After execution, summary contains 'top' and 'freq' keys

