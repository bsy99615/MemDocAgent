# `duplicates_spark.py`

## `src.ydata_profiling.model.spark.duplicates_spark.spark_get_duplicates` · *function*

## Summary:
Identifies and quantifies duplicate records in a Spark DataFrame, returning duplicate statistics and sample records.

## Description:
Processes a Spark DataFrame to detect duplicate rows based on all column values, calculating duplicate counts and percentages. This function extracts duplicate detection logic to enable reuse across different profiling contexts while maintaining clear separation between data processing and reporting concerns.

## Args:
    config (Settings): Configuration object containing duplicate detection settings including head count limit and key field name.
    df (DataFrame): Input Spark DataFrame to analyze for duplicates.
    supported_columns (Sequence): Sequence of column names that are supported for duplicate analysis.

## Returns:
    Tuple[Dict[str, Any], Optional[DataFrame]]: A tuple containing:
        - metrics (Dict[str, Any]): Dictionary with duplicate statistics including 'n_duplicates' (count) and 'p_duplicates' (percentage).
        - duplicated_df (Optional[DataFrame]): DataFrame containing sample duplicate records ordered by frequency, or None if no duplicates found or head count is zero.

## Raises:
    ValueError: When the configured duplicates key field name conflicts with an existing column in the DataFrame.

## Constraints:
    Preconditions:
        - Input DataFrame must be a valid Spark DataFrame
        - Config must contain valid duplicates configuration settings
        - Supported columns sequence should not contain unsupported column types
        
    Postconditions:
        - Returned metrics dictionary always contains 'n_duplicates' and 'p_duplicates' keys
        - If duplicates exist, returned DataFrame contains records with duplicate column combinations
        - If head count is 0, returns empty metrics and None for duplicate records
        - If no supported columns or empty DataFrame, returns zero metrics and None for duplicate records

## Side Effects:
    - Triggers Spark DataFrame operations including groupBy, agg, filter, and count
    - Converts resulting DataFrame to Pandas format for return (potentially memory-intensive)
    - May cause Spark job execution depending on DataFrame lazy evaluation state

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_duplicates] --> B{config.duplicates.head == 0?}
    B -- Yes --> C[Return empty metrics, None]
    B -- No --> D{No supported columns OR df.count() == 0?}
    D -- Yes --> E[Set metrics to 0, return]
    D -- No --> F{duplicates_key in df.columns?}
    F -- Yes --> G[Raise ValueError]
    F -- No --> H[Group by all columns, count occurrences]
    H --> I[Filter groups with count > 1]
    I --> J[Calculate n_duplicates and p_duplicates]
    J --> K[Order by count descending, limit to head count]
    K --> L[Convert to Pandas DataFrame]
    L --> M[Return metrics and duplicated_df]
```

## Examples:
    # Basic usage with duplicate detection
    config = Settings()
    df = spark.createDataFrame([(1, "A"), (2, "B"), (1, "A")], ["id", "value"])
    metrics, duplicates_df = spark_get_duplicates(config, df, ["id", "value"])
    # Returns metrics with n_duplicates=1, p_duplicates=0.33, and duplicates_df with the duplicate record
    
    # Usage with head count set to 0 (no sample records)
    config.duplicates.head = 0
    metrics, duplicates_df = spark_get_duplicates(config, df, ["id", "value"])
    # Returns empty metrics dict and None for duplicates_df
    
    # Usage with conflicting key name
    config.duplicates.key = "id"
    try:
        spark_get_duplicates(config, df, ["id", "value"])
    except ValueError as e:
        print(f"Configuration error: {e}")
        
    # Usage with empty DataFrame
    empty_df = spark.createDataFrame([], ["id", "value"])
    metrics, duplicates_df = spark_get_duplicates(config, empty_df, ["id", "value"])
    # Returns metrics with n_duplicates=0, p_duplicates=0.0, and None for duplicates_df

