# `sample_spark.py`

## `src.ydata_profiling.model.spark.sample_spark.spark_get_sample` · *function*

## Summary:
Retrieves a sample of data records from a Spark DataFrame based on configuration settings, specifically implementing the head sample functionality for Spark environments.

## Description:
This function extracts a sample of data from a PySpark DataFrame according to the sampling configuration settings. It is designed specifically for Spark environments and implements only the head sample functionality, with warnings issued for unsupported tail and random sampling options. The function serves as a specialized implementation within the multimethod sampling framework, providing Spark-specific sampling capabilities alongside other DataFrame types.

Known callers within the codebase include the profiling system components that require sample data for display purposes, particularly when processing Spark DataFrames. These callers typically invoke this function during the profiling process when sample data is needed for user presentation, often in conjunction with other sampling methods through the multimethod dispatch mechanism. The function is part of the multimethod `get_sample` system where specific implementations are selected based on DataFrame type through decorator-based dispatch.

This logic is extracted into its own function rather than being inlined to provide a clean separation between the Spark sampling interface and implementation details, enabling support for multiple DataFrame types while maintaining a consistent API. The function specifically handles Spark's unique characteristics and limitations, such as the need to convert to Pandas for sample data representation.

## Args:
    config (Settings): Configuration object containing sampling parameters such as sample size limits for head, tail, and random sampling
    df (DataFrame): Input PySpark DataFrame to sample from

## Returns:
    List[Sample]: A list containing Sample objects with the sampled data records. Currently only includes the head sample when configured, with empty list returned for empty DataFrames or when head sampling is disabled.

## Raises:
    None explicitly raised, though warnings are issued for unsupported sampling options (tail and random)

## Constraints:
    Preconditions:
        - config must be a valid Settings object with proper sampling configuration
        - df must be a valid PySpark DataFrame instance
    Postconditions:
        - The returned list contains Sample objects with properly formatted data
        - The number of samples respects the head configuration limit
        - Empty DataFrames result in empty sample lists
        - Tail and random sampling options issue warnings but don't raise exceptions

## Side Effects:
    - Issues warnings via Python warnings module for unsupported tail and random sampling features
    - Converts Spark DataFrame to Pandas format for sample data representation
    - May perform Spark operations (limit, toPandas) which could impact performance

## Control Flow:
```mermaid
flowchart TD
    A[spark_get_sample called] --> B{DataFrame empty?}
    B -->|Yes| C[Return empty samples list]
    B -->|No| D[Get head sample size]
    D --> E{Head sample size > 0?}
    E -->|Yes| F[Create head sample with df.limit().toPandas()]
    E -->|No| G[Skip head sample]
    F --> H[Add head sample to results]
    G --> H
    H --> I[Get tail sample size]
    I --> J{Tail sample size > 0?}
    J -->|Yes| K[Issue tail warning]
    J -->|No| L[Skip tail warning]
    K --> M[Get random sample size]
    M --> N{Random sample size > 0?}
    N -->|Yes| O[Issue random warning]
    N -->|No| P[Return samples list]
    L --> P
    O --> P
```

## Examples:
```python
# Basic usage with head sampling enabled
config = Settings()
config.samples.head = 5
df = spark.createDataFrame([(1, 'a'), (2, 'b'), (3, 'c')], ['id', 'value'])
samples = spark_get_sample(config, df)
# Returns a list with one Sample object containing first 5 rows as Pandas DataFrame

# Usage with empty DataFrame
config = Settings()
config.samples.head = 5
empty_df = spark.createDataFrame([], ['id', 'value'])
samples = spark_get_sample(config, empty_df)
# Returns empty list []

# Usage with head sampling disabled
config = Settings()
config.samples.head = 0
df = spark.createDataFrame([(1, 'a'), (2, 'b')], ['id', 'value'])
samples = spark_get_sample(config, df)
# Returns empty list []
```

