# `describe_text_spark.py`

## `src.ydata_profiling.model.spark.describe_text_spark.describe_text_1d_spark` · *function*

## Summary:
Collects sample rows from a Spark DataFrame for text variable analysis when redaction is disabled.

## Description:
This function serves as a Spark-specific implementation for gathering sample data from text variables during profiling. When the redaction setting is disabled, it retrieves the first five rows from the DataFrame and stores them in the summary dictionary for display purposes. This allows users to see actual text content while maintaining privacy when redaction is enabled.

## Args:
    config (Settings): Configuration object containing profiling settings, specifically the text redaction flag
    df (DataFrame): Spark DataFrame containing text data to sample
    summary (dict): Dictionary to store profiling results, including sample rows when redaction is disabled

## Returns:
    Tuple[Settings, DataFrame, dict]: The unchanged input parameters packaged as a tuple for chaining operations

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - config must be a valid Settings object with vars.text.redact attribute
    - df must be a valid PySpark DataFrame
    - summary must be a mutable dictionary object
    
    Postconditions:
    - If redact is False, summary will contain a "first_rows" key with sampled data
    - All input parameters remain unchanged

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_text_1d_spark] --> B{redact enabled?}
    B -- Yes --> C[Return unchanged]
    B -- No --> D[Get first 5 rows from df]
    D --> E[Convert to Pandas Series]
    E --> F[Store in summary[first_rows]]
    F --> G[Return unchanged params]
```

## Examples:
    # Basic usage in profiling pipeline
    config = Settings()
    df = spark.createDataFrame([(1, "hello"), (2, "world")], ["id", "text"])
    summary = {}
    
    result_config, result_df, result_summary = describe_text_1d_spark(config, df, summary)
    
    # With redaction disabled
    config.vars.text.redact = False
    # summary["first_rows"] will contain first 5 rows as pandas Series
    
    # With redaction enabled  
    config.vars.text.redact = True
    # summary remains unchanged
```

