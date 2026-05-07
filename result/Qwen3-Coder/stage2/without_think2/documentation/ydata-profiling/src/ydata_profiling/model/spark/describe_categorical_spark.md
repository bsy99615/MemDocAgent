# `describe_categorical_spark.py`

## `src.ydata_profiling.model.spark.describe_categorical_spark.describe_categorical_1d_spark` · *function*

## Summary:
Conditionally extracts first five rows from a Spark DataFrame for categorical variable summaries when redaction is disabled.

## Description:
This function provides Spark-specific handling for categorical data summaries by conditionally retrieving sample data from the DataFrame. When redaction is disabled in the configuration, it extracts the first five rows from the Spark DataFrame and converts them to a Pandas Series for inclusion in the summary statistics. This enables detailed inspection of categorical data samples in reports while respecting privacy settings. The function maintains the standard interface expected by the profiling pipeline while adapting to Spark's distributed computing environment.

## Args:
    config (Settings): Configuration object containing profiling settings, specifically the redact flag for categorical variables
    df (DataFrame): Spark DataFrame containing categorical data to process
    summary (dict): Dictionary containing existing summary statistics that may be augmented with first_rows data

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the unchanged config, df, and potentially updated summary dictionary with first_rows key

## Raises:
    None explicitly raised - relies on underlying Spark operations which may raise exceptions during toPandas() conversion

## Constraints:
    Preconditions:
        - config must be a valid Settings object with vars.cat.redact attribute accessible
        - df must be a valid PySpark DataFrame
        - summary must be a mutable dictionary object
    
    Postconditions:
        - The returned tuple maintains the same reference to config and df objects
        - If redact is False, summary dictionary will contain a "first_rows" key with first 5 rows as Pandas Series
        - If redact is True, summary remains unchanged

## Side Effects:
    - Converts Spark DataFrame to Pandas DataFrame via toPandas() operation
    - May cause memory pressure when processing large DataFrames due to Pandas conversion
    - No external I/O operations or state mutations beyond the summary dictionary modification

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_categorical_1d_spark] --> B{redact == False?}
    B -- Yes --> C[Get first 5 rows from df]
    C --> D[Convert to Pandas Series]
    D --> E[Store in summary[first_rows]]
    E --> F[Return config, df, summary]
    B -- No --> F
```

## Examples:
    # Basic usage with redaction disabled
    config = Settings()
    config.vars.cat.redact = False
    spark_df = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")], ["id", "category"])
    summary = {}
    result_config, result_df, result_summary = describe_categorical_1d_spark(config, spark_df, summary)
    # result_summary will contain "first_rows" key with first 5 rows
    
    # Usage with redaction enabled
    config.vars.cat.redact = True
    result_config, result_df, result_summary = describe_categorical_1d_spark(config, spark_df, summary)
    # result_summary remains unchanged (no first_rows added)

