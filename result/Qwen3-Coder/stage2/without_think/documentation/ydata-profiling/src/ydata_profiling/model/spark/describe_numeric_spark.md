# `describe_numeric_spark.py`

## `src.ydata_profiling.model.spark.describe_numeric_spark.numeric_stats_spark` · *function*

## Summary:
Computes comprehensive descriptive statistics for a single numeric column in a Spark DataFrame.

## Description:
This function calculates fundamental statistical measures including mean, standard deviation, variance, minimum, maximum, kurtosis, skewness, and sum for a single numeric column within a Spark DataFrame. It serves as a core component in the data profiling pipeline for Spark-based datasets, extracting statistical summaries that inform data quality assessments and distribution analysis. The function expects a DataFrame with exactly one column and applies PySpark aggregation functions to compute these statistics efficiently.

## Args:
    df (DataFrame): A PySpark DataFrame containing exactly one numeric column to analyze
    summary (dict): A dictionary containing summary configuration or metadata (currently unused in implementation)

## Returns:
    dict: A dictionary containing computed statistical measures with keys: 'mean', 'std', 'variance', 'min', 'max', 'kurtosis', 'skewness', 'sum'. Each value represents the corresponding statistical measure for the single column in the DataFrame, or None if the computation cannot be performed.

## Raises:
    IndexError: When the DataFrame contains zero columns (accessing df.columns[0])
    AttributeError: When the DataFrame column does not support the statistical operations being performed (e.g., non-numeric data type)

## Constraints:
    Preconditions:
        - Input DataFrame must contain exactly one column
        - The single column must contain numeric data compatible with PySpark statistical functions
        - Column names must be accessible via df.columns[0]
    
    Postconditions:
        - Returns a dictionary with exactly 8 keys representing the computed statistics
        - All returned values are numeric (float or int) or None if computation fails

## Side Effects:
    None: This function performs no I/O operations or external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[Start numeric_stats_spark] --> B{DataFrame has columns?}
    B -- No --> C[Throw IndexError]
    B -- Yes --> D[Extract column name]
    D --> E[Build statistical expressions using F. functions]
    E --> F[Execute aggregation with df.agg()]
    F --> G[Get first result with .first()]
    G --> H[Convert to dictionary with .asDict()]
    H --> I[Return result]
```

## Examples:
```python
# Basic usage
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
spark = SparkSession.builder.appName("test").getOrCreate()
df = spark.createDataFrame([(1,), (2,), (3,)], ["value"])
result = numeric_stats_spark(df, {})
print(result)  # {'mean': 2.0, 'std': 1.0, 'variance': 1.0, ...}

# With different data
df2 = spark.createDataFrame([(10.5,), (20.3,), (30.1,)], ["scores"])
result2 = numeric_stats_spark(df2, {})
print(result2)  # Statistical measures for the scores column
```

## `src.ydata_profiling.model.spark.describe_numeric_spark.describe_numeric_1d_spark` · *function*

## Summary
Computes comprehensive descriptive statistics and derived metrics for a single numeric column in a Spark DataFrame, updating the summary dictionary with detailed numerical analysis.

## Description
This function serves as the core statistical computation component for numeric data profiling in Spark environments. It builds upon basic numeric statistics to derive additional metrics such as quantiles, central tendency measures, dispersion indicators, and distribution characteristics. The function processes a Spark DataFrame containing a single numeric column and enriches the provided summary dictionary with extensive statistical information that enables data quality assessment and distribution analysis.

The function is designed to be part of a larger data profiling pipeline where it handles the computational heavy lifting for numeric variable analysis in distributed Spark computing environments. It specifically computes both basic statistics (mean, std, variance, min, max, etc.) and advanced metrics (quantiles, skewness, kurtosis, median absolute deviation, etc.).

## Args
- config (Settings): Configuration object containing profiling settings and plot parameters
- df (DataFrame): PySpark DataFrame containing exactly one numeric column to analyze
- summary (dict): Dictionary containing existing summary information and metadata that gets updated with computed statistics

## Returns
- Tuple[Settings, DataFrame, dict]: Returns the unchanged config, df, and the updated summary dictionary containing all computed statistics

## Raises
- IndexError: When the DataFrame contains zero columns (accessing df.columns[0])
- AttributeError: When the DataFrame column does not support the statistical operations being performed (e.g., non-numeric data type)

## Constraints
- Preconditions:
  - Input DataFrame must contain exactly one column
  - The single column must contain numeric data compatible with PySpark statistical functions
  - Column names must be accessible via df.columns[0]
  - Summary dictionary must contain required keys like "value_counts", "n_distinct", "n", "value_counts_without_nan"
  
- Postconditions:
  - The summary dictionary is updated with numerous statistical measures
  - All returned values are numeric (float or int) or None if computation fails

## Side Effects
- Modifies the input summary dictionary in-place by adding new key-value pairs
- Performs Spark SQL operations including aggregations and approxQuantile computations
- May involve distributed computing operations across Spark executors

## Control Flow
```mermaid
flowchart TD
    A[Start describe_numeric_1d_spark] --> B[Compute base stats with numeric_stats_spark]
    B --> C[Extract value_counts from summary]
    C --> D[Calculate infinite values count]
    D --> E[Calculate zero values count]
    E --> F[Calculate negative values count]
    F --> G[Compute quantiles using approxQuantile]
    G --> H[Calculate median from 50% quantile]
    H --> I[Calculate MAD (Median Absolute Deviation)]
    I --> J[Calculate derived percentages]
    J --> K[Calculate additional metrics (range, iqr, cv)]
    K --> L[Set monotonic flag to 0]
    L --> M[Filter out infinity values from histogram data]
    M --> N[Compute histogram using histogram_compute]
    N --> O[Return updated config, df, and summary]
```

## Examples
```python
# Basic usage in a profiling pipeline
from ydata_profiling.config import Settings
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("profiling").getOrCreate()
config = Settings()

# Create sample DataFrame with numeric data
df = spark.createDataFrame([(1,), (2,), (3,), (4,), (5,)], ["values"])

# Initialize summary dictionary with required fields
summary = {
    "value_counts": value_counts_df,
    "n_distinct": 5,
    "n": 5,
    "value_counts_without_nan": value_counts_without_nan_series
}

# Compute comprehensive statistics
updated_config, updated_df, updated_summary = describe_numeric_1d_spark(config, df, summary)

# The summary now contains all computed statistics including:
# Basic statistics: min, max, mean, std, variance, skewness, kurtosis, sum
# Count metrics: n_infinite, n_zeros, n_negative
# Quantiles: 5%, 25%, 50% (median), 75%, 95%
# Derived metrics: mad, p_negative, range, iqr, cv, p_zeros, p_infinite
# Additional properties: monotonic flag, histogram data
```

