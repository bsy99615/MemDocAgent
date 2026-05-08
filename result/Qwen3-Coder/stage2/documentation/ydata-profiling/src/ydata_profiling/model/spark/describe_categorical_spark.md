# `describe_categorical_spark.py`

## `src.ydata_profiling.model.spark.describe_categorical_spark.describe_categorical_1d_spark` · *function*

## Summary:
Processes categorical data summary for Spark DataFrames, optionally capturing first rows when redaction is disabled.

## Description:
This function serves as a Spark-specific implementation for describing categorical data by handling the extraction of sample rows when redaction is disabled. It acts as a bridge between the general categorical description logic and Spark DataFrame operations.

The function is typically called as part of the profiling pipeline when processing categorical variables in Spark environments. It integrates with the broader profiling framework by modifying the summary dictionary with sample data while preserving the original configuration and DataFrame.

## Args:
    config (Settings): Configuration settings containing categorical variable options, including redaction preferences
    df (DataFrame): Spark DataFrame containing the categorical data to be described
    summary (dict): Dictionary containing summary statistics and metadata about the data

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the unchanged config, df, and modified summary dictionary

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
        - config must be a valid Settings object with vars.cat.redact attribute
        - df must be a valid PySpark DataFrame
        - summary must be a mutable dictionary object
    
    Postconditions:
        - The returned config, df, and summary remain unchanged except for potential modification of summary when redaction is disabled
        - When redaction is disabled, summary will contain a "first_rows" key with sample data

## Side Effects:
    - When redaction is disabled, performs Spark DataFrame operations (limit() and toPandas()) which may cause I/O and computation overhead
    - Modifies the summary dictionary by adding a "first_rows" key when redaction is disabled

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_categorical_1d_spark] --> B{redact enabled?}
    B -- Yes --> C[Return unchanged config, df, summary]
    B -- No --> D[Get first 5 rows from df]
    D --> E[Convert to Pandas]
    E --> F[Store in summary["first_rows"]]
    F --> G[Return config, df, summary]
```

## Examples:
    # Basic usage in profiling pipeline
    config = Settings()
    spark_df = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")], ["id", "category"])
    summary = {}
    
    result_config, result_df, result_summary = describe_categorical_1d_spark(config, spark_df, summary)
    
    # With redaction enabled (no sample data added)
    config.vars.cat.redact = True
    result_config, result_df, result_summary = describe_categorical_1d_spark(config, spark_df, summary)
    # result_summary remains unchanged

