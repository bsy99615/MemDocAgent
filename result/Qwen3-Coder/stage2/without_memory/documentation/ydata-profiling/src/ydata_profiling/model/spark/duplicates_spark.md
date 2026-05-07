# `duplicates_spark.py`

## `src.ydata_profiling.model.spark.duplicates_spark.spark_get_duplicates` · *function*

## Summary:
Identifies and analyzes duplicate rows in a Spark DataFrame, returning duplicate statistics and a sample of duplicate records.

## Description:
Processes a Spark DataFrame to detect duplicate rows based on all column values, computes duplicate metrics, and optionally returns a limited sample of duplicate records. This function is part of the profiling pipeline for Spark data and provides insights into data duplication patterns.

## Args:
    config (Settings): Configuration object containing duplicate detection settings, specifically `duplicates.head` and `duplicates.key`.
    df (DataFrame): Input Spark DataFrame to analyze for duplicates.
    supported_columns (Sequence): Sequence of column names that are supported for duplicate analysis.

## Returns:
    Tuple[Dict[str, Any], Optional[DataFrame]]: A tuple containing:
        - metrics (Dict[str, Any]): Dictionary with duplicate statistics including:
          * "n_duplicates": Number of duplicate rows found
          * "p_duplicates": Proportion of duplicate rows relative to total rows
        - duplicated_df (Optional[DataFrame]): Spark DataFrame containing duplicate records ordered by frequency (descending), limited to config.duplicates.head rows. Returns None if no duplicates found or head is set to 0.

## Raises:
    ValueError: When the configured duplicates key conflicts with an existing column name in the DataFrame.

## Constraints:
    Preconditions:
        - config.duplicates.head must be a non-negative integer
        - config.duplicates.key must be a string that doesn't conflict with existing DataFrame column names
        - df must be a valid Spark DataFrame
        - supported_columns must be a sequence of column names
    
    Postconditions:
        - If n_head is 0, returns empty metrics dict and None for duplicated_df
        - If no supported_columns or empty DataFrame, returns zero metrics and None for duplicated_df
        - If duplicates found, metrics contains valid counts and proportions
        - Returned DataFrame (when present) contains only rows with duplicate values

## Side Effects:
    - Executes Spark SQL operations on the input DataFrame
    - Calls df.count() twice (once for metrics calculation, once for duplicated_df.count())
    - Converts resulting Spark DataFrame to Pandas DataFrame for return
    - May trigger Spark job execution for the groupBy, agg, filter, and orderBy operations

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_duplicates] --> B{config.duplicates.head == 0?}
    B -- Yes --> C[Return empty metrics, None]
    B -- No --> D{No supported_columns OR df.count() == 0?}
    D -- Yes --> E[Set n_duplicates=0, p_duplicates=0.0]
    E --> F[Return metrics, None]
    D -- No --> G{duplicates_key in df.columns?}
    G -- Yes --> H[raise ValueError]
    G -- No --> I[Group by all columns, count occurrences]
    I --> J[Filter for count > 1]
    J --> K[Calculate n_duplicates and p_duplicates]
    K --> L[Order by count descending, limit to head]
    L --> M[Convert to Pandas DataFrame]
    M --> N[Return metrics and duplicated_df]
```

## Examples:
    # Basic usage with duplicate detection
    config = Settings()
    config.duplicates.head = 5
    config.duplicates.key = "duplicate_count"
    metrics, duplicates_df = spark_get_duplicates(config, spark_df, ["col1", "col2"])
    
    # Usage with head=0 (no duplicate samples)
    config.duplicates.head = 0
    metrics, duplicates_df = spark_get_duplicates(config, spark_df, ["col1", "col2"])
    # Returns empty metrics dict and None for duplicates_df
    
    # Usage with empty DataFrame
    empty_df = spark.createDataFrame([], schema)
    metrics, duplicates_df = spark_get_duplicates(config, empty_df, ["col1", "col2"])
    # Returns metrics with zeros and None for duplicates_df

