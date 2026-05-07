# `sample_spark.py`

## `src.ydata_profiling.model.spark.sample_spark.spark_get_sample` · *function*

## Summary:
Retrieves a list of data samples from a Spark DataFrame based on configuration settings, supporting only head sampling due to Spark limitations.

## Description:
This function extracts data samples from a Spark DataFrame according to the sampling configuration specified in the Settings object. It specifically implements head sampling functionality while issuing warnings for unsupported tail and random sampling features in Spark environments. The function serves as a Spark-specific implementation of the general sampling interface, providing a consistent way to retrieve sample data for profiling reports.

Known callers within the codebase:
- Called by Spark-specific profiling pipelines when generating sample sections for reports
- Invoked during report construction phases when data samples are needed for display in Spark environments

This logic is extracted into its own function rather than being inlined because it encapsulates Spark-specific sampling behavior, separates concerns between data access and report generation, and provides a clean interface for different data engine implementations (pandas vs Spark) to handle sampling consistently.

## Args:
- config (Settings): Configuration object containing sampling parameters including head, tail, and random sample sizes. The samples attribute controls how many rows to extract from different parts of the dataset.
- df (DataFrame): Spark DataFrame from which to extract samples. Must be a valid PySpark DataFrame object.

## Returns:
- List[Sample]: A list containing Sample objects representing the requested data samples. Currently only includes head samples when n_head > 0, and returns an empty list for empty DataFrames or when no head samples are configured.

## Raises:
- None: This function does not raise exceptions directly, though underlying Spark operations may raise exceptions.

## Constraints:
- Preconditions:
  - config must be a valid Settings object with proper sampling configuration
  - df must be a valid PySpark DataFrame that can be queried
- Postconditions:
  - Returns a list of Sample objects with appropriate metadata
  - Empty DataFrames result in empty sample lists
  - Head sampling respects the configured n_head limit

## Side Effects:
- Issues warnings via Python's warnings module when tail or random sampling is requested but not supported in Spark
- Triggers Spark operations to convert DataFrame to Pandas format for sample data extraction

## Control Flow:
```mermaid
flowchart TD
    A[spark_get_sample called] --> B{DataFrame empty?}
    B -->|Yes| C[Return empty samples list]
    B -->|No| D[Get n_head from config]
    D --> E{n_head > 0?}
    E -->|Yes| F[Extract head sample with df.limit(n_head).toPandas()]
    F --> G[Create Sample object with id="head"]
    G --> H[Add to samples list]
    H --> I[Get n_tail from config]
    I --> J{n_tail > 0?}
    J -->|Yes| K[Warn about tail not implemented for Spark]
    K --> L[Get n_random from config]
    L --> M{n_random > 0?}
    M -->|Yes| N[Warn about random not implemented for Spark]
    N --> O[Return samples list]
    E -->|No| P[Skip head sample]
    P --> Q[Get n_tail from config]
    Q --> R{n_tail > 0?}
    R -->|Yes| S[Warn about tail not implemented for Spark]
    S --> T[Get n_random from config]
    T --> U{n_random > 0?}
    U -->|Yes| V[Warn about random not implemented for Spark]
    V --> W[Return samples list]
```

## Examples:
```python
from pyspark.sql import SparkSession
from ydata_profiling.config import Settings
from ydata_profiling.model.spark.sample_spark import spark_get_sample

# Create Spark session and DataFrame
spark = SparkSession.builder.appName("test").getOrCreate()
df = spark.createDataFrame([(1, "a"), (2, "b"), (3, "c")], ["id", "value"])

# Configure sampling
config = Settings()
config.samples.head = 2  # Get first 2 rows
config.samples.tail = 0  # Disable tail sampling
config.samples.random = 0  # Disable random sampling

# Extract samples
samples = spark_get_sample(config, df)
print(len(samples))  # Output: 1 (head sample)
print(samples[0].id)  # Output: "head"
print(samples[0].name)  # Output: "First rows"

# With empty DataFrame
empty_df = spark.createDataFrame([], ["id", "value"])
empty_samples = spark_get_sample(config, empty_df)
print(len(empty_samples))  # Output: 0
```

