# `describe_date_spark.py`

## `src.ydata_profiling.model.spark.describe_date_spark.date_stats_spark` · *function*

## Summary:
Computes minimum and maximum date values from a Spark DataFrame column and returns them as a dictionary.

## Description:
This function extracts the first column from a Spark DataFrame and calculates the minimum and maximum date values across all rows. It's designed specifically for Spark DataFrame processing and returns the results in a dictionary format suitable for statistical summaries.

The function is part of the Spark-specific date profiling implementation, separating the date statistics computation logic from the general profiling framework. This extraction allows for optimized Spark operations while maintaining consistency with the broader profiling interface.

## Args:
    df (DataFrame): A PySpark DataFrame containing at least one column with date values
    summary (dict): A dictionary containing summary statistics (unused in current implementation)

## Returns:
    dict: A dictionary containing 'min' and 'max' keys with their respective date values

## Raises:
    IndexError: When the DataFrame has no columns
    Exception: Any underlying Spark execution errors during aggregation

## Constraints:
    Preconditions:
        - Input DataFrame must contain at least one column
        - Column data type should be compatible with date/time operations
    Postconditions:
        - Returns a dictionary with exactly 'min' and 'max' keys
        - Values are the actual minimum and maximum date values from the column

## Side Effects:
    - Executes Spark SQL aggregation operations on the input DataFrame
    - May trigger Spark job execution depending on DataFrame's lazy evaluation state

## Control Flow:
```mermaid
flowchart TD
    A[Start date_stats_spark] --> B{DataFrame has columns?}
    B -- No --> C[Throw IndexError]
    B -- Yes --> D[Get first column name]
    D --> E[Create min/max aggregation expressions]
    E --> F[Execute df.agg() with expressions]
    F --> G[Get first row result]
    G --> H[Convert to dictionary]
    H --> I[Return result]
```

## Examples:
```python
# Basic usage with a Spark DataFrame containing dates
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("test").getOrCreate()
df = spark.createDataFrame([(1, "2023-01-01"), (2, "2023-12-31")], ["id", "date_col"])
result = date_stats_spark(df, {})
print(result)  # Output: {'min': datetime.date(2023, 1, 1), 'max': datetime.date(2023, 12, 31)}
```

## `src.ydata_profiling.model.spark.describe_date_spark.describe_date_1d_spark` · *function*

## Summary:
Processes a Spark DataFrame date column to compute temporal statistics and histogram data for profiling.

## Description:
This function performs comprehensive date column analysis for Spark DataFrames by computing minimum and maximum values, calculating date ranges, converting timestamps to Unix format, and generating histogram data for visualization. It serves as the Spark-specific implementation of date profiling logic, working in conjunction with the broader profiling framework.

The function is designed to be called as part of the Spark data profiling pipeline, where it processes individual date columns and updates the summary statistics with temporal information and histogram data. It separates concerns by handling date-specific computations while maintaining compatibility with the standard profiling interface.

## Args:
    config (Settings): Configuration object containing plot settings, particularly histogram bin configuration
    df (DataFrame): PySpark DataFrame containing exactly one date column to analyze
    summary (dict): Dictionary containing existing summary statistics that will be updated with date-specific metrics

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the unchanged config, the modified DataFrame with Unix timestamp conversion applied to the date column, and the updated summary dictionary with date statistics and histogram data. The histogram data is stored as a tuple of numpy arrays: (histogram_counts_array, bin_edges_array), where counts represent frequency values and bin_edges represent the boundaries of histogram bins.

## Raises:
    IndexError: When the input DataFrame has no columns
    Exception: Any underlying Spark execution errors during aggregation or histogram computation

## Constraints:
    Preconditions:
        - Input DataFrame must contain exactly one column
        - The single column must contain date/time values compatible with Spark timestamp operations
        - Config must contain valid plot.histogram.bins setting
    Postconditions:
        - The DataFrame's date column is converted to Unix timestamp format (using pyspark.sql.functions.unix_timestamp)
        - Summary dictionary contains 'min', 'max', 'range', and 'histogram' keys
        - Histogram data consists of two numpy arrays representing counts and bin edges respectively

## Side Effects:
    - Executes Spark SQL aggregation operations to compute min/max values via date_stats_spark
    - Modifies the input DataFrame by converting date column to Unix timestamp format using pyspark.sql.functions.unix_timestamp
    - Triggers Spark job execution for histogram computation
    - Updates the summary dictionary in-place

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_date_1d_spark] --> B[Get column name from df.columns[0]]
    B --> C[Call date_stats_spark(df, summary)]
    C --> D[Update summary with min/max values]
    D --> E[Calculate range = max - min]
    E --> F[Convert date column to Unix timestamp using pyspark.sql.functions.unix_timestamp]
    F --> G[Calculate histogram bins argument based on config and n_distinct]
    G --> H[Compute histogram using rdd.histogram()]
    H --> I[Update summary with histogram data as (array(hist), array(bin_edges))]
    I --> J[Return (config, df, summary)]
```

## Examples:
```python
# Basic usage in Spark profiling pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from ydata_profiling.config import Settings

spark = SparkSession.builder.appName("profiling").getOrCreate()
config = Settings()

# Create sample DataFrame with date column
df = spark.createDataFrame([
    ("2023-01-01",),
    ("2023-06-15",),
    ("2023-12-31",)
], ["date_column"])

summary = {"n_distinct": 3}

# Process date column for profiling
config, processed_df, updated_summary = describe_date_1d_spark(config, df, summary)

# Access computed statistics
print(f"Min date: {updated_summary['min']}")
print(f"Max date: {updated_summary['max']}")
print(f"Date range: {updated_summary['range']}")
print(f"Histogram bins: {len(updated_summary['histogram'][1])}")
```

