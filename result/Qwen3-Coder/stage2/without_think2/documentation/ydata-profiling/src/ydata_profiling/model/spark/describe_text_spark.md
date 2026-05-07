# `describe_text_spark.py`

## `src.ydata_profiling.model.spark.describe_text_spark.describe_text_1d_spark` · *function*

## Summary:
Retrieves first rows from a Spark DataFrame for text data summary when redaction is disabled.

## Description:
This function implements Spark-specific logic for extracting sample text data from a PySpark DataFrame. It's designed to work with the profiling pipeline to collect first few rows of text data for display in reports, but only when redaction is disabled. The function acts as a bridge between the core profiling logic and Spark-specific data access patterns.

The function is extracted to encapsulate Spark-specific operations (like converting to Pandas) while maintaining the same interface as other similar functions in the codebase, enabling a consistent abstraction layer across different data backends.

## Args:
    config (Settings): Configuration object containing application settings, specifically the text redaction flag (`config.vars.text.redact`)
    df (DataFrame): PySpark DataFrame containing text data to sample
    summary (dict): Dictionary containing existing summary statistics that may be updated with first_rows data

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the unchanged config, df, and potentially updated summary dictionary

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - config must be a valid Settings object with vars.text.redact attribute accessible
        - df must be a valid PySpark DataFrame
        - summary must be a mutable dictionary
    
    Postconditions:
        - The returned tuple maintains the same reference to config and df objects
        - If redaction is disabled, summary dictionary will contain "first_rows" key with first 5 rows converted to Pandas Series
        - If redaction is enabled, summary remains unchanged

## Side Effects:
    - Converts Spark DataFrame to Pandas DataFrame via toPandas() when redaction is disabled
    - May modify the summary dictionary by adding a "first_rows" key
    - Uses DataFrame.limit(5) operation which may trigger Spark computation

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_text_1d_spark] --> B{redact == False?}
    B -- Yes --> C[Get first 5 rows from df]
    C --> D[Convert to Pandas]
    D --> E[Squeeze columns to Series]
    E --> F[Store in summary[first_rows]]
    B -- No --> G[Skip row retrieval]
    F --> H[Return config, df, summary]
    G --> H
```

## Examples:
    # Basic usage with redaction disabled
    config = Settings()
    config.vars.text.redact = False
    df = spark.createDataFrame([(1, "hello"), (2, "world")], ["id", "text"])
    summary = {}
    result_config, result_df, result_summary = describe_text_1d_spark(config, df, summary)
    # result_summary will contain "first_rows" key with first 5 rows as Pandas Series
    
    # Usage with redaction enabled (no side effects)
    config.vars.text.redact = True
    result_config, result_df, result_summary = describe_text_1d_spark(config, df, summary)
    # result_summary remains unchanged, no conversion occurs

