# `describe_numeric_spark.py`

## `src.ydata_profiling.model.spark.describe_numeric_spark.numeric_stats_spark` · *function*

## Summary:
Computes comprehensive statistical measures for a single numeric column in a PySpark DataFrame.

## Description:
This function calculates various descriptive statistics for a single numeric column within a PySpark DataFrame. It extracts the first column from the DataFrame and computes mean, standard deviation, variance, minimum, maximum, kurtosis, skewness, and sum using PySpark's built-in aggregation functions. The result is returned as a dictionary containing these computed statistics.

The function is designed specifically for PySpark DataFrames and leverages Spark's distributed computing capabilities to efficiently compute these statistics across potentially large datasets.

## Args:
    df (DataFrame): A PySpark DataFrame containing exactly one numeric column
    summary (dict): A dictionary parameter that appears to be unused in the current implementation

## Returns:
    dict: A dictionary containing the computed statistics with keys: 'mean', 'std', 'variance', 'min', 'max', 'kurtosis', 'skewness', 'sum'
          Values are typically numeric (float or int) but may be null if computation cannot be performed on the data

## Raises:
    IndexError: When the DataFrame has no columns
    AttributeError: When DataFrame column operations fail due to invalid column references
    TypeError: When the DataFrame contains non-numeric data that cannot be aggregated

## Constraints:
    Preconditions:
        - The DataFrame must contain exactly one column
        - The single column must contain numeric data that can be aggregated
        - The DataFrame must be a valid PySpark DataFrame instance
    
    Postconditions:
        - Returns a dictionary with exactly 8 keys representing the computed statistics
        - All returned values are numeric (float or int) or null if computation cannot be performed

## Side Effects:
    - Executes Spark SQL aggregation operations on the input DataFrame
    - Triggers Spark job execution depending on DataFrame's lazy evaluation state
    - May cause performance overhead for very large datasets

## Control Flow:
```mermaid
flowchart TD
    A[Start numeric_stats_spark] --> B{DataFrame has columns?}
    B -- No --> C[Throw IndexError]
    B -- Yes --> D[Get first column name]
    E[Create aggregation expressions] --> F[Execute df.agg()]
    F --> G[Get first row result]
    G --> H[Convert to dictionary]
    H --> I[Return statistics dict]
```

## Examples:
```python
# Basic usage with a Spark DataFrame containing one numeric column
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
spark = SparkSession.builder.appName("test").getOrCreate()
data = [(1,), (2,), (3,), (4,), (5,)]
df = spark.createDataFrame(data, ["value"])
result = numeric_stats_spark(df, {})
print(result)
# Output: {'mean': 3.0, 'std': 1.414..., 'variance': 2.0, 'min': 1, 'max': 5, 'kurtosis': -1.3, 'skewness': 0.0, 'sum': 15}
```

## `src.ydata_profiling.model.spark.describe_numeric_spark.describe_numeric_1d_spark` · *function*

## Summary:
Computes comprehensive descriptive statistics for a single numeric column in a PySpark DataFrame, including central tendency, dispersion, shape, and special value counts.

## Description:
This function performs detailed statistical analysis on a single numeric column within a PySpark DataFrame. It extends basic statistical measures by computing additional metrics like skewness, kurtosis, quantiles, and specialized counts (zeros, negatives, infinite values). The function integrates with the broader profiling framework to populate a summary dictionary with rich statistical information for numerical data analysis.

The function is part of the Spark-specific profiling implementation and serves as a bridge between raw DataFrame statistics and the standardized summary format used throughout the ydata-profiling library. It handles special cases like infinite values, zero counts, and negative value counts while leveraging PySpark's distributed computing capabilities for efficient processing.

## Args:
    config (Settings): Configuration object containing profiling settings and plot parameters
    df (DataFrame): PySpark DataFrame containing exactly one numeric column to analyze
    summary (dict): Dictionary containing existing summary statistics and metadata about the column

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing the updated configuration, the original DataFrame, and the enriched summary dictionary with computed statistics

## Raises:
    None explicitly raised in the function body, though underlying PySpark operations may raise exceptions

## Constraints:
    Preconditions:
        - The DataFrame must contain exactly one column
        - The single column must contain numeric data that can be aggregated
        - The summary dictionary must contain required keys like 'value_counts', 'n_distinct', 'n'
        - The config object must be properly initialized with numerical variable settings
    
    Postconditions:
        - The summary dictionary is updated with numerous statistical measures
        - All computed statistics are stored as key-value pairs in the summary dictionary
        - The function preserves the original DataFrame and configuration objects unchanged

## Side Effects:
    - Executes multiple PySpark SQL aggregation operations on the input DataFrame
    - Triggers Spark job execution depending on DataFrame's lazy evaluation state
    - Modifies the input summary dictionary in-place by adding new key-value pairs
    - May cause performance overhead for very large datasets due to multiple Spark operations

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_numeric_1d_spark] --> B[Compute basic stats via numeric_stats_spark]
    B --> C[Extract and store basic stats in summary]
    C --> D[Calculate infinite value count]
    D --> E[Calculate zero count]
    E --> F[Calculate negative value count]
    F --> G[Compute quantiles using approxQuantile]
    G --> H[Calculate median and MAD]
    H --> I[Compute derived statistics (p_negative, range, iqr, cv, p_zeros, p_infinite)]
    I --> J[Update summary with monotonic flag]
    J --> K[Filter out infinity values from histogram data]
    K --> L[Compute histogram using histogram_compute]
    L --> M[Return updated config, df, and summary]
```

## Examples:
```python
# Basic usage with a Spark DataFrame containing one numeric column
from pyspark.sql import SparkSession
from ydata_profiling.config import Settings
spark = SparkSession.builder.appName("test").getOrCreate()
data = [(1,), (2,), (3,), (4,), (5,)]
df = spark.createDataFrame(data, ["value"])
config = Settings()
summary = {"value_counts": ..., "n_distinct": 5, "n": 5, "value_counts_without_nan": ...}

# Call the function to enrich summary with statistics
updated_config, updated_df, enriched_summary = describe_numeric_1d_spark(config, df, summary)

# The enriched_summary now contains comprehensive statistics including:
# min, max, mean, std, variance, skewness, kurtosis, sum, n_infinite, n_zeros, n_negative
# quantiles (25%, 50%, 75%, etc.), median, mad, p_negative, range, iqr, cv, p_zeros, p_infinite
```

