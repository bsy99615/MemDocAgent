# `table_spark.py`

## `src.ydata_profiling.model.spark.table_spark.spark_get_table_stats` · *function*

## Summary:
Computes comprehensive table-level statistics for Spark DataFrames including row/column counts, missing value metrics, and data type distributions.

## Description:
This function processes Spark DataFrame statistics by aggregating information from variable-level summaries to compute table-level metrics. It's specifically designed for Spark DataFrames and extracts key statistical information needed for data profiling reports. The function calculates fundamental table properties such as total rows and columns, missing value counts and percentages, and data type distributions across all variables.

The function is part of the Spark-specific profiling implementation and is called as part of the data profiling pipeline when working with Spark DataFrames. It's extracted from inline logic to provide a clean separation between Spark-specific data processing and general profiling logic.

## Args:
    config (Settings): Configuration object containing profiling settings and parameters
    df (DataFrame): Spark DataFrame for which to compute statistics
    variable_stats (dict): Dictionary containing variable-level statistics, where keys are variable names and values are dictionaries with variable metadata

## Returns:
    dict: Dictionary containing table-level statistics with the following keys:
        - "n": Total number of rows in the DataFrame (int)
        - "n_var": Total number of columns in the DataFrame (int)  
        - "n_cells_missing": Total count of missing cells across all variables (int)
        - "n_vars_with_missing": Count of variables that contain at least one missing value (int)
        - "n_vars_all_missing": Count of variables where all values are missing (int)
        - "p_cells_missing": Proportion of missing cells relative to total cells (n * n_var) (float)
        - "types": Dictionary mapping data type names to their counts (dict)

## Raises:
    None explicitly raised - relies on underlying Spark operations that may raise exceptions

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - df must be a valid Spark DataFrame
        - variable_stats must be a dictionary with variable metadata
        - Each entry in variable_stats should contain "n_missing" key when missing values are present
    
    Postconditions:
        - Returned dictionary always contains "n", "n_var", "n_cells_missing", "n_vars_with_missing", "n_vars_all_missing", "p_cells_missing", and "types" keys
        - All numeric values in returned dictionary are non-negative integers or floats
        - "p_cells_missing" is always between 0 and 1 (inclusive)

## Side Effects:
    - Triggers Spark computation via df.count() operation
    - No external I/O operations or state mutations beyond Spark job execution

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_table_stats] --> B[df.count() to get n]
    B --> C[Initialize result dict with n and n_var]
    C --> D[Initialize table_stats counters]
    D --> E[Iterate through variable_stats]
    E --> F{Has n_missing key?}
    F -->|Yes| G[Check if n_missing > 0]
    G -->|Yes| H[Increment n_vars_with_missing]
    H --> I[Add n_missing to n_cells_missing]
    I --> J{series_summary[n_missing] == n?}
    J -->|Yes| K[Increment n_vars_all_missing]
    K --> L[Continue iteration]
    F -->|No| L
    L --> M{result[n] * result[n_var] > 0?}
    M -->|Yes| N[Calculate p_cells_missing]
    N --> O[Assign p_cells_missing to result]
    M -->|No| P[Set p_cells_missing = 0]
    P --> O
    O --> Q[Copy all table_stats to result]
    Q --> R[Compute types Counter]
    R --> S[Return result]
```

## Examples:
```python
from pyspark.sql import SparkSession
from ydata_profiling.config import Settings
from src.ydata_profiling.model.spark.table_spark import spark_get_table_stats

# Setup
spark = SparkSession.builder.appName("Test").getOrCreate()
df = spark.createDataFrame([(1, "A", None), (2, None, "C")], ["id", "name", "value"])
variable_stats = {
    "id": {"n_missing": 0, "type": "numeric"},
    "name": {"n_missing": 1, "type": "string"}, 
    "value": {"n_missing": 1, "type": "string"}
}

# Compute table statistics
config = Settings()
stats = spark_get_table_stats(config, df, variable_stats)

# Result would contain:
# {
#     "n": 2, 
#     "n_var": 3,
#     "n_cells_missing": 2,
#     "n_vars_with_missing": 2,
#     "n_vars_all_missing": 0,
#     "p_cells_missing": 0.3333333333333333,
#     "types": {"numeric": 1, "string": 2}
# }
```

