# `table_pandas.py`

## `src.ydata_profiling.model.pandas.table_pandas.pandas_get_table_stats` · *function*

## Summary:
Computes comprehensive statistics for a pandas DataFrame by aggregating variable-level statistics and calculating derived table-level metrics.

## Description:
This function serves as a pandas-specific implementation that aggregates variable-level statistics into comprehensive table-level statistics. It calculates fundamental metrics like row count, column count, memory usage, and missing value distributions. The function is designed to be called during profiling workflows where detailed statistical analysis of data tables is required.

The logic is extracted into its own function to separate concerns between data aggregation and statistical computation, allowing for easier testing and maintenance of the table-level statistics calculation logic independently from the underlying data structure handling.

## Args:
    config (Settings): Configuration object containing profiling settings, particularly the memory_deep flag for deep memory calculation
    df (pd.DataFrame): The pandas DataFrame to analyze
    variable_stats (dict): Dictionary containing variable-level statistics keyed by column names

## Returns:
    dict: A dictionary containing comprehensive table-level statistics including:
        - n: Number of rows in the DataFrame
        - n_var: Number of columns in the DataFrame  
        - memory_size: Total memory usage of the DataFrame
        - record_size: Average memory usage per record
        - n_cells_missing: Total number of missing cells across all variables
        - n_vars_with_missing: Number of variables containing missing values
        - n_vars_all_missing: Number of variables where all values are missing
        - p_cells_missing: Proportion of missing cells relative to total possible cells
        - types: Dictionary counting occurrences of each variable type

## Raises:
    None explicitly raised - relies on pandas operations which may raise standard exceptions

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - df must be a valid pandas DataFrame
        - variable_stats must be a dictionary with variable summary data
        - Each entry in variable_stats should contain a "n_missing" key if missing value tracking is desired
    
    Postconditions:
        - All returned statistics are computed based on the input DataFrame and variable statistics
        - The returned dictionary contains all expected keys with appropriate numeric values

## Side Effects:
    None - This function is pure and does not modify any external state or perform I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_get_table_stats] --> B{df.empty?}
    B -- Yes --> C[n = 0]
    B -- No --> D[n = len(df)]
    C --> E[memory_size = df.memory_usage(deep=config.memory_deep).sum()]
    D --> E
    E --> F[record_size = memory_size/n if n>0 else 0]
    F --> G[Initialize table_stats dict]
    G --> H[Iterate through variable_stats.values()]
    H --> I{series_summary has n_missing AND n_missing > 0?}
    I -- Yes --> J[Increment n_vars_with_missing]
    I -- Yes --> K[Add n_missing to n_cells_missing]
    I -- Yes --> L{series_summary["n_missing"] == n?}
    L -- Yes --> M[Increment n_vars_all_missing]
    J --> N[Continue iteration]
    K --> N
    M --> N
    I -- No --> N
    N --> O[Calculate p_cells_missing]
    O --> P[Update table_stats with types counter]
    P --> Q[Return table_stats]
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

