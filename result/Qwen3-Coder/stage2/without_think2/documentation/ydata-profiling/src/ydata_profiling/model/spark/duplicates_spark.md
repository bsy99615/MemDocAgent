# `duplicates_spark.py`

## `src.ydata_profiling.model.spark.duplicates_spark.spark_get_duplicates` · *function*

## Summary:
Analyzes a Spark DataFrame to identify duplicate rows based on all columns, returning duplicate statistics and optionally the actual duplicate records.

## Description:
This function performs duplicate detection on Spark DataFrames by grouping all columns and counting occurrences. It serves as a Spark-specific implementation within the profiling framework, providing consistent duplicate analysis capabilities across different data processing backends.

The function is designed to work with the ydata-profiling framework's configuration system, allowing users to control whether duplicate rows are returned and how many to include in results. It handles edge cases such as empty DataFrames and invalid configurations gracefully.

## Args:
    config (Settings): Configuration object controlling duplicate detection behavior, including:
        - config.duplicates.head: Number of duplicate rows to return (0 means none)
        - config.duplicates.key: Column name to use for duplicate counts
    df (DataFrame): Input Spark DataFrame containing the data to analyze for duplicates
    supported_columns (Sequence): Sequence of column names that are eligible for duplicate detection analysis

## Returns:
    Tuple[Dict[str, Any], Optional[DataFrame]]: A tuple containing:
        - Dictionary with duplicate statistics including 'n_duplicates' (count) and 'p_duplicates' (percentage)
        - Optional Spark DataFrame containing the actual duplicate rows ordered by count descending, or None if not requested

## Raises:
    ValueError: When the configured duplicates key conflicts with existing column names in the DataFrame

## Constraints:
    Preconditions:
        - config must be a valid Settings instance
        - df must be a valid Spark DataFrame
        - supported_columns must contain column names that exist in df
    
    Postconditions:
        - Returned dictionary will contain structured duplicate statistics
        - Returned DataFrame (if present) will contain only rows identified as duplicates according to the specified columns

## Side Effects:
    None: Function does not perform I/O operations or modify external state directly. However, it triggers Spark operations that may cause computation.

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_duplicates] --> B{config.duplicates.head == 0?}
    B -- Yes --> C[Return empty metrics, None]
    B -- No --> D{No supported_columns OR df.count() == 0?}
    D -- Yes --> E[Set metrics to zero, return metrics, None]
    D -- No --> F{duplicates_key in df.columns?}
    F -- Yes --> G[Raise ValueError]
    F -- No --> H[Group by all columns and count occurrences]
    H --> I[Filter groups with count > 1]
    I --> J[Calculate n_duplicates and p_duplicates]
    J --> K[Order by count desc, limit head rows, convert to Pandas]
    K --> L[Return metrics dict and duplicate DataFrame]
```

## Examples:
Basic usage with duplicate detection enabled:
```python
from ydata_profiling.config import Settings
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("test").getOrCreate()
config = Settings()
config.duplicates.head = 5  # Return top 5 duplicates

# Create test DataFrame
df = spark.createDataFrame([(1, "a"), (2, "b"), (1, "a"), (3, "c")], ["id", "value"])

# Analyze for duplicates
metrics, duplicates = spark_get_duplicates(config, df, ["id", "value"])

print(f"Found {metrics['n_duplicates']} duplicates")
if duplicates is not None:
    print("Duplicate rows:")
    print(duplicates)
```

