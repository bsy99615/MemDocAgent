# `describe_boolean_spark.py`

## `src.ydata_profiling.model.spark.describe_boolean_spark.describe_boolean_1d_spark` · *function*

## Summary:
Extracts the most frequent value and its count from boolean data summary statistics for Spark DataFrames.

## Description:
Processes a boolean data summary dictionary to identify the most frequently occurring value and its frequency count. This function is part of the Spark-specific data profiling pipeline for boolean columns, extracting key statistical information from value counts. It is typically called as part of the boolean data description process in Spark environments.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): Spark DataFrame containing the boolean data
    summary (dict): Dictionary containing summary statistics including 'value_counts' key

## Returns:
    Tuple[Settings, DataFrame, dict]: Returns the unchanged configuration, DataFrame, and updated summary dictionary with 'top' and 'freq' keys added

## Raises:
    AttributeError: If value_counts does not have a .first() method
    IndexError: If the first row of value_counts does not contain at least two elements
    Exception: Potentially other exceptions from Spark DataFrame operations

## Constraints:
    Preconditions:
    - The summary dictionary must contain a 'value_counts' key
    - The 'value_counts' value must be a valid Spark DataFrame or similar structure with a .first() method
    - The first row of value_counts must have at least two columns to extract [0] and [1]

    Postconditions:
    - The summary dictionary will contain 'top' and 'freq' keys
    - The returned summary dictionary will have the same structure as the input but with additional keys

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_boolean_1d_spark] --> B{summary has value_counts?}
    B -- Yes --> C[Extract value_counts]
    C --> D[Call value_counts.first()]
    D --> E{first() successful?}
    E -- Yes --> F[Extract top = first[0], freq = first[1]]
    F --> G[Update summary with top and freq]
    G --> H[Return config, df, summary]
    E -- No --> I[Raise exception]
    B -- No --> J[Raise exception]
```

## Examples:
    # Typical usage in Spark boolean profiling pipeline
    config, df, summary = describe_boolean_1d_spark(settings, spark_df, {
        "value_counts": spark_value_counts_df
    })
    # Result: summary now contains 'top' and 'freq' keys with most frequent value and count

