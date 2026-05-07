# `table_pandas.py`

## `src.ydata_profiling.model.pandas.table_pandas.pandas_get_table_stats` · *function*

## Summary:
Computes comprehensive statistical summaries for a pandas DataFrame including size metrics, missing value counts, and variable type distributions.

## Description:
This function aggregates metadata and statistical information from a pandas DataFrame and its associated variable statistics. It serves as the pandas-specific implementation of table statistics computation within the ydata-profiling framework. The function is typically called during data profiling pipelines when detailed table-level information is needed for report generation.

The logic is extracted into its own function to separate concerns between DataFrame processing and statistical aggregation, allowing for different implementations (pandas, polars, etc.) while maintaining a consistent interface.

## Args:
    config (Settings): Configuration object containing profiling settings, including memory deep calculation flag
    df (pd.DataFrame): The pandas DataFrame to analyze
    variable_stats (dict): Dictionary containing per-variable statistics with keys like 'n_missing' and 'type'

## Returns:
    dict: Dictionary containing comprehensive table statistics with keys:
        - 'n': Number of rows in the DataFrame
        - 'n_var': Number of columns in the DataFrame  
        - 'memory_size': Total memory usage in bytes
        - 'record_size': Average memory usage per record
        - 'n_cells_missing': Total count of missing values across all variables
        - 'n_vars_with_missing': Count of variables containing at least one missing value
        - 'n_vars_all_missing': Count of variables where all values are missing
        - 'p_cells_missing': Percentage of missing cells relative to total cells
        - 'types': Dictionary mapping variable types to their counts

## Raises:
    None explicitly raised - all operations are safe and handle edge cases internally

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - df must be a pandas DataFrame
        - variable_stats must be a dictionary with properly formatted variable summaries
        
    Postconditions:
        - All returned statistics are computed accurately based on input data
        - Empty DataFrames are handled gracefully with zero values
        - Missing value calculations account for all edge cases

## Side Effects:
    None - This function is pure and has no side effects

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_get_table_stats] --> B{df.empty?}
    B -- Yes --> C[n = 0]
    B -- No --> D[n = len(df)]
    C --> E[memory_size = df.memory_usage()]
    D --> E
    E --> F[record_size = memory_size/n if n>0 else 0]
    F --> G[Initialize table_stats dict]
    G --> H[Process variable_stats]
    H --> I{series_summary has n_missing?}
    I -- Yes --> J{n_missing > 0?}
    J -- Yes --> K[n_vars_with_missing++]
    J -- Yes --> L[n_cells_missing += n_missing]
    J -- Yes --> M{series_summary[n_missing] == n?}
    M -- Yes --> N[n_vars_all_missing++]
    K --> O
    L --> O
    N --> O
    I -- No --> O
    O --> P[table_stats["p_cells_missing"] = n_cells_missing/(n*n_var) if n>0 and n_var>0 else 0]
    P --> Q[table_stats.update(types counter)]
    Q --> R[Return table_stats]
```

## Examples:
```python
# Basic usage
config = Settings()
df = pd.DataFrame({'A': [1, 2, None], 'B': [4, None, 6]})
variable_stats = {
    'A': {'n_missing': 1, 'type': 'numeric'},
    'B': {'n_missing': 1, 'type': 'numeric'}
}
stats = pandas_get_table_stats(config, df, variable_stats)
print(stats['n'])  # Output: 3
print(stats['n_cells_missing'])  # Output: 2
```

