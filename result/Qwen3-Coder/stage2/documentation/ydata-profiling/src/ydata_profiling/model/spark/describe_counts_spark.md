# `describe_counts_spark.py`

## `src.ydata_profiling.model.spark.describe_counts_spark.describe_counts_spark` · *function*

## Summary:
Computes value counts and missing value statistics for Spark DataFrames and updates the summary dictionary with the results.

## Description:
Processes a Spark DataFrame to calculate value frequencies, missing value counts, and organizes the data for statistical profiling. This function extracts the Spark-specific implementation of value counting logic that would normally be handled by the generic `describe_counts` function. It transforms the Spark DataFrame into appropriate summary statistics that can be used for data profiling.

## Args:
    config (Settings): Configuration settings for the profiling process
    series (DataFrame): Input Spark DataFrame containing the data to analyze
    summary (dict): Dictionary to store computed statistics and results

## Returns:
    Tuple[Settings, DataFrame, dict]: The unchanged config, the original series, and the updated summary dictionary containing:
        - n_missing: Count of missing/null values
        - value_counts: Spark DataFrame with value counts (persisted)
        - value_counts_index_sorted: Pandas Series with sorted values and counts
        - value_counts_without_nan: Pandas Series with counts excluding NaN values

## Raises:
    None explicitly raised - though underlying Spark operations may raise exceptions

## Constraints:
    Preconditions:
        - series must be a valid Spark DataFrame
        - summary must be a mutable dictionary
        - config must be a valid Settings object
    
    Postconditions:
        - The summary dictionary will contain the keys: 'n_missing', 'value_counts', 'value_counts_index_sorted', and 'value_counts_without_nan'
        - The value_counts in summary will be a persisted Spark DataFrame
        - All returned values maintain their original types and relationships

## Side Effects:
    - Persists Spark DataFrames in memory (value_counts and value_counts_index_sorted)
    - Converts Spark DataFrames to Pandas objects for indexing operations
    - Modifies the input summary dictionary in-place
    - May cause memory pressure due to persistence of large DataFrames

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_counts_spark] --> B[Group by all columns and count]
    B --> C[Sort by count descending and persist]
    C --> D[Sort by first column ascending]
    D --> E[Calculate missing values count]
    E --> F[Convert sorted data to Pandas Series]
    F --> G[Update summary with n_missing]
    G --> H[Update summary with value_counts (persisted)]
    H --> I[Update summary with value_counts_index_sorted]
    I --> J[Compute value_counts_without_nan]
    J --> K[Update summary with value_counts_without_nan]
    K --> L[Return config, series, summary]
```

## Examples:
    # Typical usage in profiling pipeline
    config = Settings()
    spark_df = spark.createDataFrame([(1,), (2,), (None,)], ["values"])
    summary = {}
    
    config, series, summary = describe_counts_spark(config, spark_df, summary)
    
    # Access computed statistics
    missing_count = summary["n_missing"]
    value_counts_df = summary["value_counts"]
    sorted_values = summary["value_counts_index_sorted"]
```

