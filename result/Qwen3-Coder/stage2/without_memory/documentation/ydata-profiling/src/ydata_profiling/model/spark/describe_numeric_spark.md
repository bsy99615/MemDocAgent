# `describe_numeric_spark.py`

## `src.ydata_profiling.model.spark.describe_numeric_spark.numeric_stats_spark` · *function*

## Summary:
Computes comprehensive descriptive statistics for a single numeric column in a Spark DataFrame.

## Description:
This function calculates fundamental statistical measures including mean, standard deviation, variance, minimum, maximum, kurtosis, skewness, and sum for a single numeric column within a Spark DataFrame. It serves as a core utility for numeric data profiling in distributed computing environments.

The function is typically called during the data profiling phase when analyzing numeric columns in Spark DataFrames, particularly in the context of automated statistical summary generation for data quality assessment.

This logic is extracted into its own function to encapsulate the specific Spark SQL aggregation operations and provide a clean interface for numeric statistics computation, separating the statistical calculation logic from higher-level profiling workflows.

## Args:
    df (DataFrame): A PySpark DataFrame containing exactly one numeric column to analyze
    summary (dict): A dictionary containing summary configuration or metadata (currently unused in the implementation)

## Returns:
    dict: A dictionary containing computed statistics with keys: 'mean', 'std', 'variance', 'min', 'max', 'kurtosis', 'skewness', 'sum'

## Raises:
    Exception: May raise exceptions from Spark DataFrame operations if the DataFrame is empty or contains invalid data

## Constraints:
    Preconditions:
        - Input DataFrame must contain exactly one column
        - The single column must contain numeric data
        - DataFrame must not be empty
    
    Postconditions:
        - Returns a dictionary with all requested statistical measures
        - All returned values are numeric (float or int)

## Side Effects:
    - Executes Spark SQL aggregation operations on the input DataFrame
    - May trigger distributed computation in Spark cluster

## Control Flow:
```mermaid
flowchart TD
    A[Start numeric_stats_spark] --> B{DataFrame has column?}
    B -- Yes --> C[Extract column name]
    C --> D[Build aggregation expressions]
    D --> E[Execute df.agg()]
    E --> F[Get first row result]
    F --> G[Convert to dictionary]
    G --> H[Return statistics dict]
    B -- No --> I[Exception]
```

## Examples:
```python
# Basic usage
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("test").getOrCreate()
df = spark.createDataFrame([(1,), (2,), (3,), (4,)], ["values"])
stats = numeric_stats_spark(df, {})
print(stats)  # {'mean': 2.5, 'std': 1.29..., 'variance': 1.66..., ...}
```

## `src.ydata_profiling.model.spark.describe_numeric_spark.describe_numeric_1d_spark` · *function*

## Summary:
Computes comprehensive descriptive statistics for a numeric Spark DataFrame column and updates the summary dictionary with statistical measures.

## Description:
This function calculates various numerical statistics for a Spark DataFrame column, including central tendency measures, dispersion metrics, distribution shape indicators, and special value counts. It serves as a core component in the Spark-based data profiling pipeline, aggregating statistical information for numeric variables.

The function extracts numeric statistics from a Spark DataFrame, computes additional derived metrics like percentiles, median absolute deviation, and various ratios, and updates the provided summary dictionary with these computed values. This logic is extracted into its own function to encapsulate the complex statistical computation process and maintain clean separation of concerns in the profiling workflow.

## Args:
    config (Settings): Configuration object containing profiling settings and parameters
    df (DataFrame): Spark DataFrame containing the numeric data to analyze (assumed to have exactly one column)
    summary (dict): Dictionary containing existing summary statistics that will be updated with new computed values. Must contain keys: "value_counts", "n_distinct", "n", "value_counts_without_nan"

## Returns:
    Tuple[Settings, DataFrame, dict]: A tuple containing:
    - config: The unchanged configuration object
    - df: The unchanged Spark DataFrame
    - summary: The updated summary dictionary containing all computed statistics including:
        * Basic statistics: min, max, mean, std, variance, skewness, kurtosis, sum
        * Special value counts: n_infinite, n_zeros, n_negative
        * Quantiles: various percentiles including median (50%)
        * Derived metrics: median, mad, range, iqr, cv, p_negative, p_zeros, p_infinite
        * Additional properties: monotonic

## Raises:
    None explicitly raised in the provided code

## Constraints:
    Preconditions:
    - The DataFrame must contain exactly one column (as indexed by df.columns[0])
    - The summary dictionary must contain keys: "value_counts", "n_distinct", "n", "value_counts_without_nan"
    - The config object must have vars.num.quantiles attribute
    - All referenced columns in the DataFrame must be numeric or convertible to numeric types
    
    Postconditions:
    - The summary dictionary will contain all standard numeric statistics including min, max, mean, std, variance, skewness, kurtosis, sum, count of infinite values, count of zeros, count of negative values, quantiles (including median), median absolute deviation, and various percentages/ratios

## Side Effects:
    - Reads data from the Spark DataFrame through various Spark SQL operations
    - Performs aggregations and computations on Spark DataFrames using approxQuantile
    - Modifies the input summary dictionary in-place by adding new key-value pairs

## Control Flow:
```mermaid
flowchart TD
    A[Start describe_numeric_1d_spark] --> B[Compute basic stats via numeric_stats_spark]
    B --> C[Update summary with basic stats]
    C --> D[Calculate infinite values count using F.col().isin()]
    D --> E[Calculate zero values count using string filter]
    E --> F[Calculate negative values count using string filter]
    F --> G[Compute quantiles using df.stat.approxQuantile]
    G --> H[Calculate median from 50% quantile]
    H --> I[Compute median absolute deviation]
    I --> J[Calculate derived percentages and ratios]
    J --> K[Calculate derived metrics like range, iqr, cv]
    K --> L[Set monotonic flag to 0]
    L --> M[Prepare histogram data excluding infinities]
    M --> N[Call histogram_compute for histogram data]
    N --> O[Return updated config, df, summary]
```

## Examples:
```python
# Typical usage in Spark profiling workflow
config = Settings()
spark_df = spark.createDataFrame([(1,), (2,), (3,)], ["column_name"])
summary = {
    "value_counts": value_counts_df,
    "n_distinct": 3,
    "n": 3,
    "value_counts_without_nan": value_counts_series
}
updated_config, updated_df, updated_summary = describe_numeric_1d_spark(config, spark_df, summary)
# The updated_summary now contains all computed statistics
```

