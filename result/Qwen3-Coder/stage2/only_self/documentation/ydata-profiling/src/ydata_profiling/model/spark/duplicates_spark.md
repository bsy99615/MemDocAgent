# `duplicates_spark.py`

## `src.ydata_profiling.model.spark.duplicates_spark.spark_get_duplicates` · *function*

## Summary
Detects duplicate rows in a Spark DataFrame and returns duplicate statistics along with a limited sample of duplicate records.

## Description
The `spark_get_duplicates` function performs duplicate row detection on a Spark DataFrame using specified columns. It groups the data by all columns, counts occurrences, and identifies rows that appear more than once. The function returns statistical information about duplicate occurrences and a limited sample of the actual duplicate rows.

This function is part of the Spark-specific data profiling pipeline and is designed to work with PySpark DataFrames. It serves as the Spark implementation of duplicate detection that was previously stubbed out in the base `get_duplicates` function.

## Args
- config (Settings): Configuration object containing duplicate detection settings such as the maximum number of duplicate records to display (`head`) and labeling key (`key`)
- df (DataFrame): Input Spark DataFrame containing the data to analyze for duplicates
- supported_columns (Sequence): Sequence of column names to consider when determining duplicate rows

## Returns
- Tuple[Dict[str, Any], Optional[DataFrame]]: A tuple containing:
  - Dictionary with metadata about duplicate detection results including:
    - `n_duplicates`: Number of duplicate rows found
    - `p_duplicates`: Percentage of duplicate rows relative to total rows
  - DataFrame containing the actual duplicate rows, or None if no duplicates are found or if the configuration prevents their return

## Raises
- ValueError: When the duplicates key specified in config.duplicates.key conflicts with an existing column name in the DataFrame

## Constraints
- Preconditions:
  - The `config` parameter must be a valid Settings object with proper duplicate configuration
  - The `df` parameter must be a valid Spark DataFrame
  - The `supported_columns` parameter must be a sequence of valid column names present in the DataFrame
- Postconditions:
  - The returned dictionary will contain `n_duplicates` and `p_duplicates` keys with appropriate numeric values
  - The returned DataFrame (if not None) will contain only rows that are identified as duplicates

## Side Effects
- Performs Spark DataFrame operations that may trigger computation
- Converts the final duplicate result to Pandas DataFrame format
- May perform I/O operations when counting DataFrame rows

## Control Flow
```mermaid
flowchart TD
    A[spark_get_duplicates called] --> B{config.duplicates.head == 0?}
    B -->|Yes| C[Return empty metrics, None]
    B -->|No| D{No supported_columns OR df.count() == 0?}
    D -->|Yes| E[Set zero counts, return None]
    D -->|No| F{duplicates_key in df.columns?}
    F -->|Yes| G[Raise ValueError]
    F -->|No| H[Group by all columns, count occurrences]
    H --> I[Filter for counts > 1]
    I --> J[Calculate n_duplicates and p_duplicates]
    J --> K[Order by count descending, limit head]
    K --> L[Convert to Pandas DataFrame]
    L --> M[Return metrics and duplicates DataFrame]
```

## Examples
```python
from ydata_profiling.config import Settings
from pyspark.sql import SparkSession
from src.ydata_profiling.model.spark.duplicates_spark import spark_get_duplicates

# Create Spark session
spark = SparkSession.builder.appName("Test").getOrCreate()

# Configure duplicate detection
config = Settings(duplicates=Duplicates(head=5))

# Assuming df is a Spark DataFrame
try:
    metrics, duplicate_rows = spark_get_duplicates(config, df, ['col1', 'col2'])
    print(f"Found {metrics['n_duplicates']} duplicate rows")
    print(f"Percentage of duplicates: {metrics['p_duplicates']:.2%}")
    if duplicate_rows is not None:
        print(f"Displaying first {len(duplicate_rows)} duplicates")
except ValueError as e:
    print(f"Configuration error: {e}")
```

