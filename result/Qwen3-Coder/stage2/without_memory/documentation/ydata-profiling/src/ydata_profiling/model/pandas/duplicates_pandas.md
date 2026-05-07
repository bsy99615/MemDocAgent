# `duplicates_pandas.py`

## `src.ydata_profiling.model.pandas.duplicates_pandas.pandas_get_duplicates` · *function*

## Summary:
Identifies and analyzes duplicate rows in a pandas DataFrame based on specified columns, returning duplicate statistics and optionally a sample of duplicate records.

## Description:
This function implements the pandas-specific duplicate detection logic for profiling reports. It determines duplicate rows based on a set of supported columns, counts occurrences, and provides statistical metrics about the duplication in the dataset. The function ensures the duplicates key column doesn't conflict with existing DataFrame columns and handles various edge cases such as empty DataFrames or zero head limits.

## Args:
    config (Settings): Configuration object containing duplicate detection settings including head limit and key name
    df (pd.DataFrame): Input DataFrame to analyze for duplicates
    supported_columns (Sequence): Collection of column names to consider when identifying duplicates

## Returns:
    Tuple[Dict[str, Any], Optional[pd.DataFrame]]: A tuple containing:
        - metrics (Dict[str, Any]): Dictionary with duplicate statistics including 'n_duplicates' (count) and 'p_duplicates' (percentage)
        - duplicated_rows (Optional[pd.DataFrame]): DataFrame with duplicate records and their counts, limited to the configured head number, or None if no duplicates or head limit is 0

## Raises:
    ValueError: When the configured duplicates key column name conflicts with an existing column in the DataFrame

## Constraints:
    Preconditions:
        - config must be a valid Settings object with duplicates configuration
        - df must be a valid pandas DataFrame
        - supported_columns must be a sequence of column names
    Postconditions:
        - Returns a tuple with metrics dictionary and optional DataFrame
        - If head limit is 0, returns empty DataFrame (None) regardless of duplicates presence
        - Metrics always include 'n_duplicates' and 'p_duplicates' keys

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{head > 0?}
    B -- No --> C[Return empty metrics, None]
    B -- Yes --> D{supported_columns and len(df) > 0?}
    D -- No --> E[Set metrics to zeros, return metrics, None]
    D -- Yes --> F{duplicates_key in df.columns?}
    F -- Yes --> G[Raise ValueError]
    F -- No --> H[Find duplicated rows]
    H --> I[Group by supported_columns]
    I --> J[Count duplicates]
    J --> K[Calculate metrics]
    K --> L[Return metrics and nlargest duplicates]
```

## Examples:
    # Basic usage with duplicates
    config = Settings()
    df = pd.DataFrame({'A': [1, 2, 1], 'B': [3, 4, 3]})
    supported_columns = ['A', 'B']
    metrics, duplicates_df = pandas_get_duplicates(config, df, supported_columns)
    # Returns metrics with n_duplicates=1, p_duplicates=0.5, and duplicates_df with the duplicate row
    
    # Usage with head limit of 0
    config.duplicates.head = 0
    metrics, duplicates_df = pandas_get_duplicates(config, df, supported_columns)
    # Returns metrics with zeros, duplicates_df=None
``

