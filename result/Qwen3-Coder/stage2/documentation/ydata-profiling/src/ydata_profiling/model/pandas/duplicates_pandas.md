# `duplicates_pandas.py`

## `src.ydata_profiling.model.pandas.duplicates_pandas.pandas_get_duplicates` · *function*

## Summary:
Identifies and analyzes duplicate records in a pandas DataFrame, returning statistical metrics and optionally the actual duplicate rows.

## Description:
The `pandas_get_duplicates` function performs duplicate detection on a pandas DataFrame by analyzing specified columns for repeated combinations. It calculates duplicate statistics and can return the actual duplicate rows up to a configured limit. This function is specifically designed for pandas DataFrames and implements the duplicate detection logic for the ydata-profiling library.

The function is called as part of the profiling pipeline when duplicate analysis is requested. It separates the concerns of duplicate detection from other profiling operations, allowing for modular design and easier testing.

## Args:
    config (Settings): Configuration object containing profiling settings, specifically the duplicates configuration with head and key parameters.
    df (pd.DataFrame): Input pandas DataFrame to analyze for duplicate records.
    supported_columns (Sequence): Sequence of column names to consider when identifying duplicate row combinations.

## Returns:
    Tuple[Dict[str, Any], Optional[pd.DataFrame]]: A tuple containing:
        - Dictionary with duplicate-related statistics including "n_duplicates" (count) and "p_duplicates" (percentage)
        - Optional DataFrame containing the actual duplicate rows, sorted by count in descending order, or None if no duplicates found or head is set to 0

## Raises:
    ValueError: When the duplicates key parameter conflicts with an existing column name in the DataFrame.

## Constraints:
    Preconditions:
        - The config parameter must be a valid Settings instance with a properly initialized Duplicates configuration
        - The df parameter must be a valid pandas DataFrame
        - The supported_columns parameter must be a sequence of valid column identifiers
    
    Postconditions:
        - The returned metrics dictionary will always contain "n_duplicates" and "p_duplicates" keys
        - When duplicates are found and head > 0, the second element of the tuple will contain a DataFrame with duplicate rows
        - When no duplicates are found or head <= 0, the second element of the tuple will be None

## Side Effects:
    None: This function does not perform any I/O operations or modify external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_get_duplicates] --> B{head > 0?}
    B -->|No| C[Return empty metrics, None]
    B -->|Yes| D{supported_columns and len(df) > 0?}
    D -->|No| E[Set metrics to zeros, return metrics, None]
    D -->|Yes| F{duplicates_key in df.columns?}
    F -->|Yes| G[Raise ValueError]
    F -->|No| H[Find duplicated rows]
    H --> I[Group by supported_columns and count]
    I --> J[Calculate n_duplicates and p_duplicates]
    J --> K[Return metrics and nlargest duplicates]
```

## Examples:
```python
from src.ydata_profiling.config import Settings
import pandas as pd

# Basic usage
config = Settings()
df = pd.DataFrame({'A': [1, 2, 1, 3], 'B': [4, 5, 4, 6]})
supported_columns = ['A', 'B']

metrics, duplicates_df = pandas_get_duplicates(config, df, supported_columns)
print(metrics['n_duplicates'])  # Shows count of duplicate rows
print(metrics['p_duplicates'])  # Shows percentage of duplicate rows

# With head = 0 (no duplicates returned)
config.duplicates.head = 0
metrics, duplicates_df = pandas_get_duplicates(config, df, supported_columns)
print(duplicates_df)  # None

# With conflicting column name (raises ValueError)
config.duplicates.key = 'A'
try:
    pandas_get_duplicates(config, df, supported_columns)
except ValueError as e:
    print(str(e))  # Error message about conflicting column name
```

