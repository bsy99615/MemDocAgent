# `duplicates_pandas.py`

## `src.ydata_profiling.model.pandas.duplicates_pandas.pandas_get_duplicates` · *function*

## Summary
Detects duplicate rows in a pandas DataFrame and calculates statistics about duplicate occurrences, returning both metadata and optional duplicate samples.

## Description
The `pandas_get_duplicates` function identifies duplicate rows in a pandas DataFrame based on specified columns and computes descriptive statistics about these duplicates. It serves as the pandas-specific implementation for duplicate detection within the ydata-profiling framework.

This function is extracted into its own component to separate the pandas-specific data manipulation logic from the general duplicate detection algorithm. This design allows for different implementations (pandas, polars, etc.) while maintaining a consistent interface for the profiling pipeline.

## Args
- config (Settings): Configuration object containing duplicate detection settings including `duplicates.head` (maximum number of duplicate records to return) and `duplicates.key` (column name to use for duplicate counts)
- df (pd.DataFrame): Input pandas DataFrame to analyze for duplicate rows
- supported_columns (Sequence): Sequence of column names to consider when determining duplicate rows

## Returns
- Tuple[Dict[str, Any], Optional[pd.DataFrame]]: A tuple containing:
  - Dictionary with metadata about duplicate detection results including:
    - "n_duplicates": Number of duplicate rows found
    - "p_duplicates": Proportion of duplicate rows relative to total rows
  - DataFrame containing the actual duplicate rows grouped by the duplicate criteria, sorted by count in descending order, or None if no duplicates are found or head setting is 0

## Raises
- ValueError: When the configured duplicates key column name conflicts with an existing column in the DataFrame

## Constraints
- Preconditions:
  - The `config` parameter must be a valid Settings object with proper duplicate configuration
  - The `df` parameter must be a valid pandas DataFrame
  - The `supported_columns` parameter must be a sequence of valid column names present in the DataFrame
- Postconditions:
  - The returned dictionary will contain "n_duplicates" and "p_duplicates" keys with numeric values
  - The returned DataFrame (if not None) will contain only rows that are identified as duplicates

## Side Effects
- None: This function does not perform any I/O operations or mutate external state

## Control Flow
```mermaid
flowchart TD
    A[Start pandas_get_duplicates] --> B{config.duplicates.head > 0?}
    B -->|No| C[Return empty metrics, None]
    B -->|Yes| D{supported_columns and df not empty?}
    D -->|No| E[Set metrics to zero, return metrics, None]
    D -->|Yes| F{duplicates_key in df.columns?}
    F -->|Yes| G[Raise ValueError]
    F -->|No| H[Find duplicated rows using df.duplicated()]
    H --> I[Filter df to only duplicated rows]
    I --> J[Group by supported_columns with dropna=False, observed=True]
    J --> K[Count occurrences and reset index with duplicates_key]
    K --> L[Calculate n_duplicates and p_duplicates]
    L --> M[Return metrics and nlargest duplicates by duplicates_key]
```

## Examples
```python
import pandas as pd
from ydata_profiling.config import Settings

# Configure duplicate detection
config = Settings()
config.duplicates.head = 5  # Show top 5 duplicate groups
config.duplicates.key = "duplicate_count"

# Create test DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Alice', 'Charlie'],
    'age': [25, 30, 25, 35],
    'city': ['NYC', 'LA', 'NYC', 'SF']
})

# Find duplicates
metrics, duplicate_rows = pandas_get_duplicates(config, df, ['name', 'age'])

print(f"Found {metrics['n_duplicates']} duplicate rows")
if duplicate_rows is not None:
    print("Duplicate rows:")
    print(duplicate_rows)
```

