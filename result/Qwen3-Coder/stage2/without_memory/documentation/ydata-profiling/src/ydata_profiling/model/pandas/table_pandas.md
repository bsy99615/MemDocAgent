# `table_pandas.py`

## `src.ydata_profiling.model.pandas.table_pandas.pandas_get_table_stats` · *function*

## Summary:
Computes comprehensive statistical summaries for a pandas DataFrame including size metrics, missing value counts, and variable type distributions.

## Description:
This function aggregates detailed statistics about a pandas DataFrame by processing both the DataFrame structure and variable-level statistics. It serves as the pandas-specific implementation for table statistics computation, overriding the base `get_table_stats` function that raises NotImplementedError. The computed statistics are used for data profiling and quality assessment.

## Args:
    config (Settings): Configuration object containing profiling settings, including memory_deep flag for deep memory calculation
    df (pd.DataFrame): The pandas DataFrame to analyze
    variable_stats (dict): Dictionary containing statistics for each column/variable in the DataFrame

## Returns:
    dict: Dictionary containing comprehensive table statistics including:
        - n: Number of rows in the DataFrame
        - n_var: Number of columns in the DataFrame  
        - memory_size: Total memory usage of the DataFrame
        - record_size: Average memory usage per record
        - n_cells_missing: Total count of missing values across all columns
        - n_vars_with_missing: Count of columns containing at least one missing value
        - n_vars_all_missing: Count of columns where all values are missing
        - p_cells_missing: Percentage of missing cells relative to total cells
        - types: Dictionary mapping variable types to their counts

## Raises:
    None explicitly raised - though underlying pandas operations may raise exceptions for invalid inputs

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - df must be a valid pandas DataFrame
        - variable_stats must be a dictionary with properly formatted variable summaries
        
    Postconditions:
        - Returns a dictionary with all expected keys populated
        - Memory calculations use config.memory_deep setting for deep vs shallow measurement
        - All missing value computations handle edge cases where n=0

## Side Effects:
    None - Pure function with no external state mutation or I/O operations

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
    G --> H[Process variable_stats]
    H --> I{series_summary has n_missing?}
    I -- Yes --> J{n_missing > 0?}
    J -- Yes --> K[n_vars_with_missing += 1]
    K --> L[n_cells_missing += n_missing]
    L --> M{n_missing == n?}
    M -- Yes --> N[n_vars_all_missing += 1]
    N --> O[Continue processing]
    J -- No --> O
    I -- No --> O
    O --> P[Calculate p_cells_missing]
    P --> Q[Update with types counter]
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
print(stats['n'])  # Number of rows
print(stats['n_cells_missing'])  # Total missing values
print(stats['types'])  # Variable type distribution
```

