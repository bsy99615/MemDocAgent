# `sample_spark.py`

## `src.ydata_profiling.model.spark.sample_spark.spark_get_sample` · *function*

## Summary:
Creates a list of head samples from a Spark DataFrame according to configuration settings, with warnings for unsupported tail and random sampling options.

## Description:
The spark_get_sample function generates a list of Sample objects containing the first rows of a Spark DataFrame based on the configured head sample count. This function is specifically designed for Spark DataFrames and implements only the head sampling functionality, while issuing warnings for tail and random sampling options that are not yet supported in the Spark implementation.

The function first checks if the DataFrame is empty, returning an empty list if so. Then it creates a Sample object with the head data using the limit() operation followed by toPandas() conversion to ensure compatibility with the Sample class's expected data format. Tail and random sampling configurations are ignored with appropriate warnings.

## Args:
    config (Settings): Configuration object containing sampling parameters in the samples attribute. The samples attribute should define head, tail, and random integer values indicating how many samples of each type to generate.
    df (DataFrame): Input Spark DataFrame to sample from. Must be a valid PySpark DataFrame object.

## Returns:
    List[Sample]: A list containing at most one Sample object representing the head rows of the DataFrame. Returns an empty list if the DataFrame is empty or if head sampling is disabled (n_head = 0).

## Raises:
    None: This function does not raise exceptions directly, though underlying Spark operations may raise exceptions if the DataFrame is malformed or inaccessible.

## Constraints:
    Preconditions:
    - The config parameter must be a valid Settings object with properly initialized samples configuration
    - The df parameter must be a valid PySpark DataFrame object
    - The DataFrame should be accessible and readable by the Spark engine
    
    Postconditions:
    - Returns a list of Sample objects with valid metadata and data
    - Each Sample object's data field contains the appropriate subset of the original DataFrame
    - Empty DataFrames result in empty lists

## Side Effects:
    - Issues Python warnings when tail or random sampling is configured but not implemented for Spark
    - Converts Spark DataFrame to Pandas DataFrame via toPandas() operation
    - May trigger Spark computation when limit() or toPandas() operations are executed

## Control Flow:
```mermaid
flowchart TD
    A[spark_get_sample called] --> B[Check if DataFrame is empty]
    B --> C{Empty DataFrame?}
    C -->|Yes| D[Return empty samples list]
    C -->|No| E[Get head sample count from config]
    E --> F{Head count > 0?}
    F -->|Yes| G[Create head Sample with df.limit().toPandas()]
    F -->|No| H[Skip head sample creation]
    G --> I[Issue warnings for tail/random sampling]
    H --> I
    I --> J[Return samples list]
```

## Examples:
```python
from src.ydata_profiling.config import Settings
from pyspark.sql import SparkSession
from src.ydata_profiling.model.spark.sample_spark import spark_get_sample

# Initialize Spark session
spark = SparkSession.builder.appName("Test").getOrCreate()
df = spark.createDataFrame([(1, "a"), (2, "b"), (3, "c")], ["id", "value"])

# Configure sampling settings
config = Settings(samples=Samples(head=2, tail=2, random=2))

# Get samples (only head sampling will be implemented)
samples = spark_get_sample(config, df)

# Process the samples
for sample in samples:
    print(f"Sample {sample.name}: {len(sample.data)} rows")
    print(sample.data)
```

