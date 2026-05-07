# `table_spark.py`

## `src.ydata_profiling.model.spark.table_spark.spark_get_table_stats` · *function*

## Summary:
Computes comprehensive table-level statistics for Spark DataFrames including missing value counts, cell percentages, and variable type distributions.

## Description:
This function aggregates metadata and statistical information from a Spark DataFrame and its associated variable statistics to produce a standardized set of table-level metrics. It serves as the Spark-specific implementation of the table statistics computation, complementing the abstract `get_table_stats` function in the base model module.

The function is typically called during the profiling process when analyzing Spark DataFrames to gather essential metadata about the dataset structure and quality.

## Args:
    config (Settings): Configuration object containing profiling settings and parameters
    df (DataFrame): Spark DataFrame containing the data to analyze
    variable_stats (dict): Dictionary mapping variable names to their individual statistics

## Returns:
    dict: A dictionary containing comprehensive table-level statistics with keys:
        - "n": Number of rows in the DataFrame
        - "n_var": Number of columns in the DataFrame  
        - "n_cells_missing": Total count of missing cells across all variables
        - "n_vars_with_missing": Number of variables containing at least one missing value
        - "n_vars_all_missing": Number of variables where all values are missing
        - "p_cells_missing": Percentage of missing cells relative to total cells
        - "types": Dictionary mapping variable types to their counts

## Raises:
    None explicitly raised - relies on underlying Spark operations that may raise exceptions

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - df must be a valid PySpark DataFrame
        - variable_stats must be a dictionary with variable names as keys and statistics dictionaries as values
        - Each statistics dictionary in variable_stats must contain either "n_missing" key or be skipped
    
    Postconditions:
        - Result dictionary always contains all standard keys regardless of input data
        - All numerical values are properly calculated based on input data
        - Types counter is always populated even if no variables exist

## Side Effects:
    - Triggers Spark computation when calling df.count() to get row count
    - May cause distributed computation across Spark cluster nodes

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_table_stats] --> B[df.count() to get n]
    B --> C[Initialize result dict]
    C --> D[Initialize table_stats dict]
    D --> E[Iterate through variable_stats]
    E --> F{Has n_missing?}
    F -->|Yes| G[Increment n_vars_with_missing]
    G --> H[Add n_missing to n_cells_missing]
    H --> I{series_summary[n_missing] == n?}
    I -->|Yes| J[Increment n_vars_all_missing]
    J --> K[Continue iteration]
    F -->|No| K
    K --> L{result[n] * result[n_var] > 0?}
    L -->|Yes| M[Calculate p_cells_missing]
    M --> N[Assign p_cells_missing to result]
    L -->|No| O[Set p_cells_missing = 0]
    O --> N
    N --> P[Copy all table_stats to result]
    P --> Q[Build types counter]
    Q --> R[Return result]
```

## Examples:
```python
# Typical usage in profiling workflow
config = Settings()
df = spark.createDataFrame([(1, None), (2, "value")], ["id", "name"])
variable_stats = {
    "id": {"n_missing": 0, "type": "numeric"},
    "name": {"n_missing": 1, "type": "string"}
}
stats = spark_get_table_stats(config, df, variable_stats)
# Returns: {"n": 2, "n_var": 2, "n_cells_missing": 1, ...}
```

