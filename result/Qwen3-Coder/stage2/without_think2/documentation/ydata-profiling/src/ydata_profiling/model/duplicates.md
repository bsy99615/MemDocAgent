# `duplicates.py`

## `src.ydata_profiling.model.duplicates.get_duplicates` · *function*

## Summary:
Analyzes a DataFrame to identify and report duplicate rows based on specified columns, returning both statistics and optionally the duplicate rows themselves.

## Description:
This function implements duplicate detection logic for data profiling workflows. It examines a DataFrame using specified columns to identify rows that appear more than once, generating comprehensive statistics about the duplicates while optionally returning the actual duplicate records for detailed inspection.

The function is designed as a reusable component within the profiling framework, enabling consistent duplicate analysis across different profiling modules while maintaining clear separation of concerns.

## Args:
    config (Settings): Configuration object controlling duplicate detection behavior, including whether to return duplicate rows.
    df (T): Input DataFrame containing the data to analyze for duplicates, where T is a type variable representing DataFrame-like objects.
    supported_columns (Sequence): Sequence of column names that are eligible for duplicate detection analysis.

## Returns:
    Tuple[Dict[str, Any], Optional[T]]: A tuple containing:
        - Dictionary with duplicate statistics including counts, percentages, and metadata about duplicate occurrences
        - Optional DataFrame containing the actual duplicate rows (when enabled via configuration), or None if not requested

## Raises:
    NotImplementedError: This function is currently not implemented and will raise this exception when invoked.

## Constraints:
    Preconditions:
        - config must be a valid Settings instance
        - df must be a valid DataFrame-like object with the specified columns
        - supported_columns must contain column names that exist in df
    
    Postconditions:
        - Returned dictionary will contain structured duplicate statistics
        - Returned DataFrame (if present) will contain only rows identified as duplicates according to the specified columns

## Side Effects:
    None: Function does not perform I/O operations or modify external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start get_duplicates] --> B{Implemented?}
    B -- No --> C[Raise NotImplementedError]
    B -- Yes --> D[Validate configuration and inputs]
    D --> E[Filter DataFrame by supported_columns]
    E --> F[Identify duplicate rows using groupby or similar technique]
    F --> G[Calculate duplicate statistics (count, percentage)]
    G --> H[Generate result tuple with statistics and optional duplicates]
    H --> I[Return (statistics_dict, optional_duplicates_df)]
```

## Examples:
Typical usage within the profiling framework:
```python
# Configure duplicate detection settings
config = Settings()
config.duplicate_rows = True  # Enable returning duplicate rows

# Analyze DataFrame for duplicates
stats, duplicates = get_duplicates(config, df, ['column1', 'column2'])

# stats contains duplicate counts and percentages
# duplicates contains actual duplicate rows if enabled
```

