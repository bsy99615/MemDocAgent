# `table_spark.py`

## `src.ydata_profiling.model.spark.table_spark.spark_get_table_stats` · *function*

## Summary:
Computes comprehensive statistical summary for a Spark DataFrame including missing value counts, data types, and cell completeness metrics.

## Description:
Processes a Spark DataFrame to calculate key table-level statistics such as row count, column count, missing value distributions, and data type frequencies. This function serves as a Spark-specific implementation that extracts table-level metadata from variable statistics and DataFrame properties.

The function is designed to be called during the profiling process when detailed table statistics are required for Spark DataFrames. It's extracted from inline logic to provide a clean separation between data processing and statistical computation.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): Spark DataFrame to analyze
    variable_stats (dict): Dictionary containing variable-level statistics keyed by column names

## Returns:
    dict: Dictionary containing comprehensive table statistics with keys:
        - "n": Number of rows in the DataFrame
        - "n_var": Number of columns in the DataFrame
        - "n_cells_missing": Total number of missing cells across all columns
        - "n_vars_with_missing": Number of columns containing at least one missing value
        - "n_vars_all_missing": Number of columns where all values are missing
        - "p_cells_missing": Proportion of missing cells relative to total cells
        - "types": Dictionary mapping data types to their frequency counts

## Raises:
    None explicitly raised - relies on underlying Spark operations that may raise exceptions

## Constraints:
    Preconditions:
        - df must be a valid PySpark DataFrame
        - variable_stats must be a dictionary with column-based statistics
        - Each entry in variable_stats should contain "n_missing" key when missing values are present
    
    Postconditions:
        - Result dictionary always contains all defined keys
        - All computed percentages are between 0 and 1
        - Types dictionary contains counts for all observed data types

## Side Effects:
    - Triggers Spark computation via df.count() operation
    - May cause distributed computation across Spark cluster nodes

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_table_stats] --> B[df.count() to get n]
    B --> C[Initialize result dict with n and n_var]
    C --> D[Initialize table_stats dict]
    D --> E{variable_stats iteration}
    E --> F[Check if n_missing exists and > 0]
    F --> G{series_summary["n_missing"] == n}
    G --> H[Increment n_vars_all_missing]
    H --> I[Update n_cells_missing and n_vars_with_missing]
    I --> J[Calculate p_cells_missing]
    J --> K[Populate result with computed stats]
    K --> L[Aggregate types using Counter]
    L --> M[Return result dict]
```

## Examples:
    # Basic usage with sample data
    config = Settings()
    df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "name"])
    variable_stats = {
        "id": {"n_missing": 0, "type": "numeric"},
        "name": {"n_missing": 1, "type": "categorical"}
    }
    stats = spark_get_table_stats(config, df, variable_stats)
    # Returns: {"n": 2, "n_var": 2, "n_cells_missing": 1, "n_vars_with_missing": 1, ...}

