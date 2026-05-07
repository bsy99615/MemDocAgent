# `describe_supported_spark.py`

## `src.ydata_profiling.model.spark.describe_supported_spark.describe_supported_spark` · *function*

## Summary
Computes and adds distinct value and uniqueness statistics to a Spark DataFrame summary dictionary.

## Description
Processes a summary dictionary containing count and value_counts information from a Spark DataFrame to calculate additional statistical measures including distinct value counts, uniqueness indicators, and their proportions. This function is part of the Spark-specific profiling pipeline and enhances the summary with metadata about the distribution characteristics of the data.

## Args
- config (Settings): Configuration object containing profiling settings and parameters
- series (DataFrame): Spark DataFrame being analyzed
- summary (dict): Dictionary containing summary statistics including 'count' and 'value_counts'

## Returns
- Tuple[Settings, DataFrame, dict]: The original config, series, and updated summary dictionary with additional computed statistics

## Raises
- None explicitly raised in the function body

## Constraints
- Preconditions: The summary dictionary must contain 'count' and 'value_counts' keys with valid data
- Postconditions: The summary dictionary will contain the following additional keys: 'n_distinct', 'p_distinct', 'is_unique', 'n_unique', 'p_unique'

## Side Effects
- Modifies the input summary dictionary in-place by adding new statistical keys
- No external I/O operations or state mutations beyond the summary dictionary modification

## Control Flow
```mermaid
flowchart TD
    A[Start] --> B{summary["count"] > 0?}
    B -- Yes --> C[Calculate n_distinct = summary["value_counts"].count()]
    B -- No --> D[n_distinct = 0]
    C --> E[Set summary["n_distinct"] = n_distinct]
    D --> E
    E --> F[Calculate p_distinct = n_distinct / count]
    F --> G[Set summary["p_distinct"] = p_distinct]
    G --> H[Calculate n_unique = summary["value_counts"].where("count == 1").count()]
    H --> I[Set summary["n_unique"] = n_unique]
    I --> J[Calculate is_unique = n_unique == count]
    J --> K[Set summary["is_unique"] = is_unique]
    K --> L[Calculate p_unique = n_unique / count]
    L --> M[Set summary["p_unique"] = p_unique]
    M --> N[Return config, series, summary]
```

## Examples
```python
from pyspark.sql import SparkSession
from ydata_profiling.config import Settings

spark = SparkSession.builder.appName("test").getOrCreate()
config = Settings()
series = spark.createDataFrame([(1,), (2,), (3,)], ["value"])
summary = {
    "count": 3,
    "value_counts": spark.createDataFrame([(1, 1), (2, 1), (3, 1)], ["value", "count"])
}

config, series, summary = describe_supported_spark(config, series, summary)
# summary now contains additional keys: n_distinct, p_distinct, is_unique, n_unique, p_unique
```

