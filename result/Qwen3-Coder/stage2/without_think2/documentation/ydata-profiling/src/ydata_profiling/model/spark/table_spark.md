# `table_spark.py`

## `src.ydata_profiling.model.spark.table_spark.spark_get_table_stats` · *function*

## Summary:
Computes comprehensive statistics for a Spark DataFrame including cell and variable missing value counts, data types distribution, and missing value percentages.

## Description:
This function processes Spark DataFrame statistics to calculate various table-level metrics such as total rows, columns, missing values, and data type distributions. It serves as a Spark-specific implementation that complements the base table statistics computation by aggregating information from variable-level statistics.

The function is designed to be called during the profiling process when analyzing Spark DataFrames, extracting key metadata about the dataset structure and quality indicators like missing data patterns. It specifically handles Spark DataFrame operations and computes missing value statistics that are then used for data profiling reports.

## Args:
    config (Settings): Configuration object containing profiling settings
    df (DataFrame): Spark DataFrame to analyze
    variable_stats (dict): Dictionary containing variable-level statistics keyed by column names, where each entry should have an 'n_missing' field

## Returns:
    dict: Dictionary containing table-level statistics including:
        - n: Number of rows in the DataFrame
        - n_var: Number of columns in the DataFrame
        - n_cells_missing: Total number of missing cells across all columns
        - n_vars_with_missing: Number of variables (columns) with at least one missing value
        - n_vars_all_missing: Number of variables (columns) with all values missing
        - p_cells_missing: Percentage of missing cells relative to total cells
        - types: Dictionary mapping data types to their frequency counts

## Raises:
    None explicitly raised - relies on underlying Spark operations which may raise exceptions during DataFrame operations

## Constraints:
    Preconditions:
        - df must be a valid PySpark DataFrame
        - variable_stats must be a dictionary with variable summary information
        - Each entry in variable_stats should contain either 'n_missing' key or be skipped
    
    Postconditions:
        - Result dictionary always contains all keys defined in the function
        - All computed percentages are bounded between 0 and 1
        - Types counter is properly constructed from variable type information

## Side Effects:
    - Triggers Spark computation via df.count() operation
    - May cause distributed computation across Spark cluster nodes
    - No external I/O operations or state mutations

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_table_stats] --> B[df.count() to get n]
    B --> C[Initialize result dict with n and n_var]
    C --> D[Initialize table_stats counters]
    D --> E{Iterate variable_stats}
    E --> F{series_summary has n_missing and > 0?}
    F -->|Yes| G[Increment n_vars_with_missing]
    G --> H[Add n_missing to n_cells_missing]
    H --> I{series_summary["n_missing"] == n?}
    I -->|Yes| J[Increment n_vars_all_missing]
    J --> K[Continue iteration]
    F -->|No| K
    K --> L{result["n"] * result["n_var"] > 0?}
    L -->|Yes| M[Calculate p_cells_missing]
    M --> N[Assign p_cells_missing to result]
    L -->|No| O[Set p_cells_missing = 0]
    O --> N
    N --> P[Copy remaining stats to result]
    P --> Q[Construct types counter]
    Q --> R[Return result]
```

## Examples:
    # Basic usage with sample data
    config = Settings()
    df = spark.createDataFrame([(1, None), (2, "value")], ["id", "name"])
    variable_stats = {
        "id": {"n_missing": 0, "type": "numeric"},
        "name": {"n_missing": 1, "type": "string"}
    }
    stats = spark_get_table_stats(config, df, variable_stats)
    # Returns: {'n': 2, 'n_var': 2, 'n_cells_missing': 1, 'n_vars_with_missing': 1, 
    #          'n_vars_all_missing': 0, 'p_cells_missing': 0.25, 'types': {'numeric': 1, 'string': 1}}

