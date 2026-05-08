# `describe_date_pandas.py`

## `src.ydata_profiling.model.pandas.describe_date_pandas.pandas_describe_date_1d` · *function*

## Summary:
Compute basic date-range statistics for a pandas datetime Series, convert the series to integer epoch seconds, optionally run a chi-square test on those integers, compute a histogram, and return the transformed values with the updated summary.

## Description:
This function performs pandas-specific, 1-dimensional summarization for datetime Series. It updates the provided summary dictionary with min/max datetimes and their difference, transforms the input Series into integer seconds, optionally attaches chi-square test results, and appends histogram statistics produced by histogram_compute.

Why this is extracted:
- Keeps pandas-specific datetime handling and numeric conversion isolated from higher-level profiling orchestration.
- Allows downstream numeric algorithms (chi-square, histogram) to operate on a numeric representation of dates.

Known callers:
- No direct callers are present in the available snapshot. It is intended to be called by a date-describing dispatcher in the profiling pipeline (for example, a describe_date_1d implementation for pandas).

## Args:
    config (Settings):
        - Profiling configuration object.
        - The function reads: config.vars.num.chi_squared_threshold (float).
        - Passed through and returned unchanged.
    series (pandas.Series):
        - A pandas Series containing datetime-like values.
        - The function calls series.min(), series.max(), and series.values.astype(np.int64).
    summary (dict):
        - Mutable dict that the function updates in place.
        - Required existing key: "n_distinct" (int). This value is passed to histogram_compute and used to determine binning.

## Returns:
    Tuple[Settings, numpy.ndarray, dict]
    - config: the same Settings instance passed in.
    - values: numpy.ndarray of integers produced by evaluating series.values.astype(np.int64) // 10**9.
        * These integers are epoch-second integer representations derived from the underlying datetime64[ns] values.
    - summary: the same dict object passed in, updated with at least the following keys:
        * "min": result of pd.Timestamp.to_pydatetime(series.min()) (a Python datetime).
        * "max": result of pd.Timestamp.to_pydatetime(series.max()) (a Python datetime).
        * "range": summary["max"] - summary["min"] (a datetime.timedelta).
        * optionally "chi_squared": result of chi_square(values) when config.vars.num.chi_squared_threshold > 0.0.
        * keys added/updated by histogram_compute(config, values, summary["n_distinct"]) — by default histogram_compute uses the key name "histogram" and stores the tuple returned by numpy.histogram.

## Raises:
    - The function does not explicitly raise custom exceptions. Exceptions from called operations may propagate:
        * Errors from pd.Timestamp.to_pydatetime if series.min()/series.max() are not convertible.
        * Errors from series.values.astype(np.int64) if values are not representable as int64 datetime64[ns].
        * Errors raised by chi_square or histogram_compute (these functions may raise their own exceptions).
    Callers should ensure preconditions (see Constraints) to avoid propagating errors.

## Constraints:
Preconditions:
    - series should contain datetime-like values compatible with pandas Timestamp / datetime64[ns].
    - summary must contain the key "n_distinct" (int) prior to calling this function.
    - If the series may contain nulls (NaT) or be empty, callers should handle those cases (for example by dropping nulls) before invoking this function; this function does not perform null-dropping itself.

Postconditions:
    - summary is mutated in place and will contain "min", "max", "range", and the histogram results; it may also contain "chi_squared".
    - values is a numpy.ndarray of integer epoch seconds derived from the input series.
    - config is returned unchanged.

## Side Effects:
    - Mutates the provided summary dict in place.
    - Calls external helper functions: chi_square(values) and histogram_compute(config, values, summary["n_distinct"]).
    - No file, network, stdout, or global state side effects occur within this function.

## Control Flow:
flowchart TD
    A[Start] --> B[Compute min = series.min(), max = series.max()]
    B --> C[Convert min/max to Python datetimes via pd.Timestamp.to_pydatetime]
    C --> D[Set summary['range'] = max - min]
    D --> E[Convert series values to int64 seconds: values = series.values.astype(np.int64) // 10**9]
    E --> F{config.vars.num.chi_squared_threshold > 0.0?}
    F -- Yes --> G[summary['chi_squared'] = chi_square(values)]
    F -- No --> H[Skip chi-square]
    G --> I[summary.update(histogram_compute(config, values, summary['n_distinct']))]
    H --> I
    I --> J[Return (config, values, summary)]

## Examples:
    # Example (pseudocode - assumes preconditions satisfied)
    import pandas as pd
    # config must define config.vars.num.chi_squared_threshold
    config = Settings(...)
    series = pd.Series(pd.date_range("2021-01-01", periods=3, freq="D"))
    summary = {"n_distinct": int(series.nunique())}

    config, values, summary = pandas_describe_date_1d(config, series, summary)

    # After call:
    # - values: array of integer seconds
    # - summary contains keys "min", "max", "range", and histogram info
    # Error handling:
    # - If series may contain NaT values, drop them before calling or ensure upstream null-handling is applied.

