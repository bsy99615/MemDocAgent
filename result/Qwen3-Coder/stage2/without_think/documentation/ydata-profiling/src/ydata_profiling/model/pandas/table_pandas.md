# `table_pandas.py`

## `src.ydata_profiling.model.pandas.table_pandas.pandas_get_table_stats` · *function*

## Summary:
Computes comprehensive statistical summaries for a pandas DataFrame including size metrics, missing data counts, and variable type distributions.

## Description:
This function aggregates metadata and statistics from individual column analyses to provide a complete overview of a pandas DataFrame's structure and content characteristics. It serves as a pandas-specific implementation that calculates table-level metrics such as memory usage, missing value patterns, and data type distributions.

The function is designed to work with the profiling pipeline where individual column statistics are already computed and passed in via the `variable_stats` parameter. Rather than recomputing column-level statistics, it aggregates them into higher-level table statistics.

## Args:
    config (Settings): Configuration settings that control analysis behavior, particularly the `memory_deep` flag for deep memory calculation
    df (pd.DataFrame): The pandas DataFrame to analyze
    variable_stats (dict): Dictionary containing pre-computed statistics for each column/variable in the DataFrame

## Returns:
    dict: A dictionary containing comprehensive table-level statistics including:
        - n: Number of rows in the DataFrame
        - n_var: Number of columns in the DataFrame  
        - memory_size: Total memory usage of the DataFrame
        - record_size: Average memory usage per record
        - n_cells_missing: Total count of missing values across all columns
        - n_vars_with_missing: Count of columns containing at least one missing value
        - n_vars_all_missing: Count of columns where all values are missing
        - p_cells_missing: Proportion of missing cells relative to total possible cells
        - types: Dictionary mapping data types to their frequency counts

## Raises:
    None explicitly raised - all operations are defensive against empty DataFrames and missing keys

## Constraints:
    Preconditions:
        - config must be a valid Settings object
        - df must be a valid pandas DataFrame
        - variable_stats must be a dictionary with column statistics
        - Each entry in variable_stats should contain either 'n_missing' key or be safely skipped
    
    Postconditions:
        - Returned dictionary always contains all defined keys
        - All numeric calculations handle division by zero gracefully
        - Memory calculations use the deep parameter from config

## Side Effects:
    None - This function is pure and has no side effects

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_get_table_stats] --> B{DataFrame empty?}
    B -- Yes --> C[n = 0]
    B -- No --> D[n = len(df)]
    C --> E[memory_size = df.memory_usage(deep=config.memory_deep).sum()]
    D --> E
    E --> F[record_size = memory_size/n if n>0 else 0]
    F --> G[Initialize table_stats dict]
    G --> H[Iterate through variable_stats]
    H --> I{series_summary has n_missing?}
    I -- No --> J[Continue loop]
    I -- Yes --> K{n_missing > 0?}
    K -- No --> J
    K -- Yes --> L[n_vars_with_missing += 1]
    L --> M[n_cells_missing += n_missing]
    M --> N{n_missing == n?}
    N -- No --> O[Continue loop]
    N -- Yes --> P[n_vars_all_missing += 1]
    P --> O
    O --> Q[Calculate p_cells_missing]
    Q --> R[Update with types counter]
    R --> S[Return table_stats]
```

## Examples:
```python
# Basic usage with sample data
import pandas as pd
from ydata_profiling.config import Settings

# Sample DataFrame
df = pd.DataFrame({
    'A': [1, 2, None, 4],
    'B': [None, None, None, None],
    'C': ['x', 'y', 'z', 'w']
})

# Mock variable stats (in real usage, these would come from column analysis)
variable_stats = {
    'A': {'n_missing': 1, 'type': 'numeric'},
    'B': {'n_missing': 4, 'type': 'numeric'}, 
    'C': {'n_missing': 0, 'type': 'categorical'}
}

config = Settings()
result = pandas_get_table_stats(config, df, variable_stats)

print(result['n'])  # Number of rows: 4
print(result['n_vars_with_missing'])  # Columns with missing values: 2
print(result['n_vars_all_missing'])  # Columns with all missing values: 1
```

