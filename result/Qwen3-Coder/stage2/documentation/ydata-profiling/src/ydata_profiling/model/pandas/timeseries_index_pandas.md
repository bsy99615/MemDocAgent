# `timeseries_index_pandas.py`

## `src.ydata_profiling.model.pandas.timeseries_index_pandas.pandas_get_time_index_description` · *function*

## Summary:
Extracts descriptive statistics about a DataFrame's time series index, returning metadata such as series count, length, start/end timestamps, and average period.

## Description:
This function validates that a DataFrame has a suitable time series index (numeric or DatetimeIndex) and computes key statistical properties of that index for profiling purposes. It serves as a pandas-specific implementation of the abstract time index description functionality.

The function is typically called during data profiling when analyzing time series datasets to gather metadata about the temporal structure of the data.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (pd.DataFrame): Input DataFrame whose index will be analyzed for time series properties
    table_stats (dict): Dictionary containing table-level statistics including type counts and row count

## Returns:
    dict: A dictionary containing time series index metadata with keys:
        - "n_series": Number of time series in the dataset (default 0 if not found)
        - "length": Total number of rows in the DataFrame
        - "start": Minimum value in the index
        - "end": Maximum value in the index
        - "period": Average time interval between consecutive index values (as Timedelta for datetime indices, otherwise as numeric)

## Raises:
    None explicitly raised - returns empty dict for invalid index types

## Constraints:
    Preconditions:
        - df must be a pandas DataFrame
        - table_stats must be a dictionary containing "types" and "n" keys
        - df.index must be either numeric or DatetimeIndex for meaningful results
    
    Postconditions:
        - Returns empty dict if index is not numeric or DatetimeIndex
        - Returns dict with all five keys when index is valid

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{Index is numeric or DatetimeIndex?}
    B -- No --> C[Return empty dict]
    B -- Yes --> D[Get n_series from table_stats]
    D --> E[Get length from table_stats]
    E --> F[Get start from df.index.min()]
    F --> G[Get end from df.index.max()]
    G --> H[Calculate period using np.diff()]
    H --> I{Is DatetimeIndex?}
    I -- Yes --> J[Convert period to Timedelta]
    I -- No --> K[Return period as-is]
    J --> L[Return result dict]
    K --> L
```

## Examples:
    # Valid numeric index
    config = Settings()
    df = pd.DataFrame({'value': [1, 2, 3]}, index=[10, 20, 30])
    table_stats = {"types": {"TimeSeries": 1}, "n": 3}
    result = pandas_get_time_index_description(config, df, table_stats)
    # Returns: {'n_series': 1, 'length': 3, 'start': 10, 'end': 30, 'period': 10.0}

    # Valid datetime index
    dates = pd.date_range('2020-01-01', periods=3, freq='D')
    df = pd.DataFrame({'value': [1, 2, 3]}, index=dates)
    table_stats = {"types": {"TimeSeries": 1}, "n": 3}
    result = pandas_get_time_index_description(config, df, table_stats)
    # Returns: {'n_series': 1, 'length': 3, 'start': Timestamp('2020-01-01'), 'end': Timestamp('2020-01-03'), 'period': Timedelta('1 days')}
```

