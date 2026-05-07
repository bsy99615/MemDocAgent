# `timeseries_index_pandas.py`

## `src.ydata_profiling.model.pandas.timeseries_index_pandas.pandas_get_time_index_description` · *function*

## Summary:
Return concise statistics describing a pandas DataFrame's time-like index (number of series, row count, index start/end, and average period) or an empty dict if the index is not time-like.

## Description:
This helper inspects df.index and, when the index is time-like (either numeric dtype or a pandas.DatetimeIndex), computes a small set of descriptors used in time-series profiling: count of time-series columns, table length, minimum and maximum index values, and the average interval between consecutive index entries.

Known callers:
- No direct callers were present in the supplied code snapshot. The function is written as a small, replaceable implementation intended to be invoked by higher-level profiling logic when describing pandas DataFrame indexes.

Typical trigger:
- Called during dataset profiling when the profiler needs a concise description of the DataFrame index for time-series analysis. If the index is not numeric and not a pandas.DatetimeIndex, the function returns {} so profiling logic can skip time-index reporting.

Why this logic is extracted:
- Encapsulates index-specific computations (min/max, numeric diffing, datetime timedelta conversion) so higher-level code can remain implementation-agnostic and avoid duplicating index-handling logic across different dataframe backends.

## Args:
    config (Settings)
        - Type: Settings
        - Description: Configuration object for profiling. Present for API consistency; not used by this function.
    df (pandas.DataFrame)
        - Type: pandas.DataFrame
        - Description: DataFrame whose index is to be analyzed. The function expects df.index to be either:
            * a numeric-index type (pandas index with numeric dtype), or
            * a pandas.DatetimeIndex.
        - If the index is neither, the function returns an empty dict and performs no further computations.
    table_stats (dict)
        - Type: dict
        - Description: Precomputed table-level statistics required by the function:
            * table_stats["types"] should be a mapping from type names to counts (the function reads table_stats["types"].get("TimeSeries", 0)).
            * table_stats["n"] must be present and is read directly as the table length (number of rows). If "n" is missing, a KeyError will be raised.

## Returns:
    dict
    - If df.index is not numeric and not a pandas.DatetimeIndex: returns {}.
    - Otherwise, returns a dict with these keys:
        * "n_series" (int): table_stats["types"].get("TimeSeries", 0) — number of time-series columns reported by the precomputed types.
        * "length" (int or numeric): table_stats["n"] (the number of rows in the DataFrame).
        * "start" (index scalar): df.index.min() — the minimum index value (type depends on the index; e.g., numpy scalar for numeric index, pandas.Timestamp for DatetimeIndex).
        * "end" (index scalar): df.index.max() — the maximum index value.
        * "period" (float | numpy scalar | pandas.Timedelta | numpy.nan | pandas.NaT):
            - Computed as the mean of the absolute differences between consecutive index entries: abs(numpy.diff(df.index)).mean()
            - If the index is numeric: a numeric mean (numpy scalar / float).
            - If the index is a pandas.DatetimeIndex: the intermediate numpy timedelta mean is converted with pandas.Timedelta(...) before returning; the returned value is a pandas.Timedelta when conversion yields a valid timedelta.
            - Edge cases:
                + If the index has fewer than 2 elements, numpy.diff yields an empty array and the mean is numpy.nan; the returned "period" will be numpy.nan for numeric indexes and may be pandas.NaT (or an equivalent missing-timedelta representation) for DatetimeIndex after conversion.

## Raises:
    KeyError
        - Condition: Raised if table_stats does not contain the "n" key because the function accesses table_stats["n"] directly.
    (No other exceptions are explicitly raised by the function; exceptions or warnings from pandas/numpy operations — e.g., if df.index operations fail due to an unexpected index structure — will propagate.)

## Constraints:
    Preconditions:
        - df must be a pandas.DataFrame.
        - table_stats must be a dict containing the "n" key. table_stats["types"] should be a mapping if callers expect accurate "n_series".
        - The function should only be called when profiling code can accept an empty dict to indicate a non-time-like index.

    Postconditions:
        - If a non-empty dict is returned, it always contains the keys: "n_series", "length", "start", "end", and "period".
        - If an empty dict is returned, that unambiguously indicates the index was neither numeric nor a pandas.DatetimeIndex.

## Side Effects:
    - None. The function performs in-memory inspection and computations only. It does not perform I/O, mutate input objects, or change external/global state.

## Control Flow:
flowchart TD
    Start --> CheckIndex{is_numeric_dtype(df.index) OR isinstance(df.index, pandas.DatetimeIndex)?}
    CheckIndex -- No --> ReturnEmpty[return {}]
    CheckIndex -- Yes --> ReadStats[read n_series = table_stats["types"].get("TimeSeries",0) and length = table_stats["n"]]
    ReadStats --> ComputeStartEnd[start = df.index.min(); end = df.index.max()]
    ComputeStartEnd --> ComputeDiff[period = abs(numpy.diff(df.index)).mean()]
    ComputeDiff --> IsDatetime{isinstance(df.index, pandas.DatetimeIndex)?}
    IsDatetime -- Yes --> Convert[period = pandas.Timedelta(period)]
    IsDatetime -- No --> Keep[period unchanged]
    Convert --> ReturnDict[return {n_series,length,start,end,period}]
    Keep --> ReturnDict

## Examples:
Example A — Numeric index (typical profiling pipeline):
    # Precondition: df is a DataFrame with a numeric index and table_stats contains "n" and "types".
    result = pandas_get_time_index_description(config, df, table_stats)
    # Possible result:
    # {"n_series": 2, "length": 100, "start": 0, "end": 99, "period": 1.0}

Example B — DatetimeIndex (period returned as pandas.Timedelta):
    # Precondition: df.index is a pandas.DatetimeIndex with at least two timestamps.
    result = pandas_get_time_index_description(config, df, table_stats)
    # Possible result:
    # {"n_series": 1, "length": 10,
    #  "start": Timestamp('2020-01-01 00:00:00'),
    #  "end": Timestamp('2020-01-10 00:00:00'),
    #  "period": Timedelta('1 days 00:00:00')}

Example C — Insufficient index length:
    # If df.index has only one element, "period" will be NaN (numeric) or a missing-timedelta representation (e.g., pandas.NaT) after conversion.
    result = pandas_get_time_index_description(config, df_single_row, table_stats)
    # Possible result:
    # {"n_series": 0, "length": 1, "start": <value>, "end": <value>, "period": numpy.nan}

