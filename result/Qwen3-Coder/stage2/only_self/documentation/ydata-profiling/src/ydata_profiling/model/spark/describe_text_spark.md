# `describe_text_spark.py`

## `src.ydata_profiling.model.spark.describe_text_spark.describe_text_1d_spark` · *function*

## Summary:
Processes text data summary for Spark DataFrames, conditionally extracting first rows based on redaction settings.

## Description:
This function serves as a Spark-specific implementation for text data description. It checks the redaction configuration and, if redaction is disabled, extracts the first five rows from the DataFrame and stores them in the summary dictionary. This allows for displaying sample text data while respecting privacy settings.

## Args:
    config (Settings): Configuration object containing text processing settings including redaction flag
    df (DataFrame): Spark DataFrame containing text data to be processed
    summary (dict): Dictionary containing summary statistics and metadata for the dataset

## Returns:
    Tuple[Settings, DataFrame, dict]: Returns the same input parameters in a tuple, allowing for method chaining and continued processing

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
        - config must be a valid Settings object with vars.text.redact attribute
        - df must be a valid PySpark DataFrame
        - summary must be a mutable dictionary object
    
    Postconditions:
        - If redaction is disabled, summary dictionary will contain a "first_rows" key with the first 5 rows
        - All input parameters remain unchanged in their respective positions

## Side Effects:
    - May perform Spark operations (df.limit(), df.toPandas()) when redaction is disabled
    - Modifies the summary dictionary by adding a "first_rows" key when redaction is disabled
    - Triggers potential Pandas conversion from Spark DataFrame when redaction is disabled

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_text_1d_spark] --> B{redact enabled?}
    B -- Yes --> C[Return config, df, summary]
    B -- No --> D[Get first 5 rows from df]
    D --> E[Convert to Pandas Series]
    E --> F[Store in summary["first_rows"]]
    F --> G[Return config, df, summary]
```

## Examples:
    # Basic usage with redaction enabled
    config = Settings()
    config.vars.text.redact = True
    result_config, result_df, result_summary = describe_text_1d_spark(config, spark_df, summary_dict)
    
    # Usage with redaction disabled
    config = Settings()
    config.vars.text.redact = False
    result_config, result_df, result_summary = describe_text_1d_spark(config, spark_df, summary_dict)
    # result_summary will now contain "first_rows" key with first 5 rows

