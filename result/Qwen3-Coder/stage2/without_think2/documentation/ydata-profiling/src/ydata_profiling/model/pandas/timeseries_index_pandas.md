# `timeseries_index_pandas.py`

## `src.ydata_profiling.model.pandas.timeseries_index_pandas.pandas_get_time_index_description` · *function*

## Summary:
Extracts descriptive statistics about a DataFrame's time index, including series count, length, start/end timestamps, and average period.

## Description:
This function analyzes the index of a pandas DataFrame to compute time-series metadata when the index is numeric or datetime-based. It serves as a pandas-specific implementation of time index description logic, providing key temporal characteristics for time-series data analysis.

The function is designed to be called from the profiling pipeline when analyzing time-series datasets, specifically when the DataFrame has a time-based index that needs statistical characterization. It acts as a bridge between the generic time index logic and pandas-specific implementations.

## Args:
    config (Settings): Configuration object containing profiling settings
    df (pd.DataFrame): Input DataFrame whose index will be analyzed for time-series properties
    table_stats (dict): Dictionary containing table-level statistics including type counts and row count with keys:
        - "types": Dictionary mapping data types to their counts
        - "n": Integer representing total number of rows in the DataFrame

## Returns:
    dict: A dictionary containing time index descriptive statistics with keys:
        - "n_series": Number of time series in the dataset (from table_stats["types"]["TimeSeries"] or 0)
        - "length": Total number of rows in the DataFrame (from table_stats["n"])
        - "start": Minimum value in the index
        - "end": Maximum value in the index
        - "period": Average time interval between consecutive index values (as float or Timedelta)

## Raises:
    None explicitly raised - returns empty dict for non-time-series indices

## Constraints:
    Preconditions:
        - df must be a pandas DataFrame
        - table_stats must be a dictionary containing "types" and "n" keys
        - Index must be either numeric or DatetimeIndex type
    
    Postconditions:
        - Returns empty dict if index is neither numeric nor DatetimeIndex
        - Returns dict with proper keys and calculated values when index is valid

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{Index is numeric or DatetimeIndex?}
    B -- No --> C[Return empty dict]
    B -- Yes --> D[Get n_series from table_stats["types"]["TimeSeries"] or 0]
    D --> E[Get length from table_stats["n"]]
    E --> F[Get start from df.index.min()]
    F --> G[Get end from df.index.max()]
    G --> H[Calculate period using np.diff and mean]
    H --> I{Is DatetimeIndex?}
    I -- Yes --> J[Convert period to Timedelta]
    I -- No --> K[Keep period as float]
    J --> L[Return result dict]
    K --> L
```

## Examples:
```python
# Basic usage with numeric index
config = Settings()
df = pd.DataFrame({'value': [1, 2, 3]}, index=[10, 20, 30])
table_stats = {"types": {"TimeSeries": 1}, "n": 3}
result = pandas_get_time_index_description(config, df, table_stats)
# Returns: {'n_series': 1, 'length': 3, 'start': 10, 'end': 30, 'period': 10.0}

# Usage with datetime index
dates = pd.date_range('2020-01-01', periods=3, freq='D')
df = pd.DataFrame({'value': [1, 2, 3]}, index=dates)
table_stats = {"types": {"TimeSeries": 1}, "n": 3}
result = pandas_get_time_index_description(config, df, table_stats)
# Returns: {'n_series': 1, 'length': 3, 'start': Timestamp('2020-01-01'), 'end': Timestamp('2020-01-03'), 'period': Timedelta('1 days')}

# Non-time series index returns empty dict
df = pd.DataFrame({'value': [1, 2, 3]}, index=['a', 'b', 'c'])
table_stats = {"types": {"TimeSeries": 1}, "n": 3}
result = pandas_get_time_index_description(config, df, table_stats)
# Returns: {}
```

