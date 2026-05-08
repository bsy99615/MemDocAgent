# `describe_numeric_pandas.py`

## `src.ydata_profiling.model.pandas.describe_numeric_pandas.mad` · *function*

## Summary:
Compute the median absolute deviation (MAD) of a numeric array — a robust scalar measure of dispersion equal to the median of the absolute deviations from the array's median.

## Description:
- Known callers within the codebase:
    - No direct internal callers were found during analysis of this module. The function is implemented as a small utility intended to be used by higher-level numeric summary routines (for example, numeric-describing algorithms or aggregation helpers) that need a robust scale metric.
- Context and typical trigger:
    - Used when a summary/statistics pipeline requires a robust measure of variability that is less sensitive to outliers than standard deviation.
- Why this logic is extracted into its own function:
    - The operation is a single well-defined statistical computation (median of absolute deviations) and is useful in multiple places. Extracting it:
        - centralizes correct computation,
        - clarifies intent at call sites,
        - avoids duplication,
        - allows consistent handling of edge-cases (NaN/empty inputs) and future enhancements (e.g., nan-aware variants).
- Implementation boundary:
    - This function performs the pure numerical computation only; it does not perform NaN filtering, dtype coercion, or input validation beyond relying on numpy semantics. Callers are responsible for pre-processing (e.g., dropping or imputing NaNs) if they want a specific NaN-handling policy.

## Args:
    arr (np.ndarray):
        1-D numpy array (or array-like accepted by numpy) containing numeric values.
        - Expected to be numeric (integers or floats). Mixed/non-numeric dtypes may cause runtime errors.
        - The function signature annotates the parameter as np.ndarray; numpy will accept array-like inputs (lists, pandas Series) because numpy functions convert inputs internally.
        - No default value.

## Returns:
    np.ndarray:
        - Per the function signature, the annotated return type is np.ndarray.
        - Practical behavior: the function returns a numpy scalar (for example numpy.float64 or numpy.int64) representing the median absolute deviation:
            median(|arr - median(arr)|).
        - The value is non-negative. If all elements are equal, the returned value is 0.
        - If any element in arr is NaN (and no pre-filtering is done), the result will be NaN because numpy.median propagates NaN (numpy.nanmedian would be required to ignore NaNs).
        - For empty input arrays, numpy.median produces NaN (with a runtime warning) — this function returns that NaN.

## Raises:
    - The function does not explicitly raise exceptions.
    - Runtime/TypeError:
        - If arithmetic arr - numpy.median(arr) is not defined for the input (for example, non-numeric or incompatible types), a TypeError or other numpy error may be raised by numpy operations.
    - No ValueError is raised by this function itself for empty inputs; numpy.median returns NaN for empty arrays (with a runtime warning).

## Constraints:
- Preconditions:
    - Caller should ensure arr is array-like and contains numeric data if a numeric MAD is desired.
    - If NaN values should be ignored, caller must filter them (e.g., arr = arr[~numpy.isnan(arr)]) or use a nan-aware alternative before calling.
- Postconditions:
    - The function returns a single numeric scalar value (numpy scalar) representing the MAD under numpy's semantics.
    - No mutation of input arr occurs.

## Side Effects:
    - None: the function performs pure computation using numpy and does not perform I/O, mutate external state, or call external services.

## Control Flow:
flowchart TD
    A[Start: receive arr] --> B[Compute m = median(arr)]
    B --> C[Compute deviations = abs(arr - m)]
    C --> D[Compute mad = median(deviations)]
    D --> E[Return mad]

## Examples:
- Basic usage with a numpy array:
    import numpy as np
    arr = np.array([1.0, 2.0, 2.0, 100.0])
    # median(arr) == 2.0
    # deviations == [1.0, 0.0, 0.0, 98.0] -> median == 0.5
    mad_value = mad(arr)
    # mad_value is a numpy scalar, e.g., numpy.float64(0.5)

- All-equal values:
    arr = np.array([5, 5, 5])
    mad_value = mad(arr)  # returns 0

- Handling NaNs (recommended pre-filtering):
    arr = np.array([1.0, numpy.nan, 2.0])
    # mad(arr) -> numpy.nan
    arr_filtered = arr[~numpy.isnan(arr)]
    mad_value = mad(arr_filtered)  # compute MAD on non-NaN values

- Defensive example with type checking / error handling:
    import numpy as np
    try:
        arr = np.array(["a", "b", "c"])  # non-numeric
        mad_value = mad(arr)  # likely raises TypeError during subtraction
    except Exception as e:
        # handle or re-raise with context
        raise TypeError("mad: input must be numeric array-like") from e

## `src.ydata_profiling.model.pandas.describe_numeric_pandas.numeric_stats_pandas` · *function*

## Summary:
Return a dictionary containing eight basic numeric aggregate statistics computed from a pandas Series: mean, std, variance, min, max, kurtosis, skewness, and sum.

## Description:
This function invokes pandas Series reduction methods and packages their direct outputs into a dictionary with fixed keys. It exists solely to centralize and standardize the set of basic numeric aggregates produced for a single Series so that other profiling code can consume a consistent summary.

Known callers within the provided code snippet:
- None explicitly present in the provided source. The function is intended for use by higher-level profiling routines that assemble per-column numeric summaries.

Responsibility boundary:
- Computes only the listed numeric aggregates by delegating to pandas Series methods.
- Does not perform null handling, dtype coercion, histogram computation, hashing, or statistical tests.

## Args:
    series (pd.Series):
        - The pandas Series to summarize.
        - Must be an instance providing pandas reduction methods (mean, std, var, min, max, kurt, skew, sum).
        - No other parameters are accepted.

## Returns:
    Dict[str, Any]:
        - A dictionary with these keys and values (each value is the direct result of the pandas Series call shown):
            "mean"     : series.mean()
            "std"      : series.std()
            "variance" : series.var()
            "min"      : series.min()
            "max"      : series.max()
            "kurtosis" : series.kurt()
            "skewness" : series.skew()
            "sum"      : series.sum()
        - Values are the raw outputs from pandas (commonly numpy scalars or Python floats). If pandas returns NaN for a statistic (e.g., due to all-missing data), that NaN is returned verbatim.
        - The function returns exactly these eight keys in the dictionary on every successful call.

## Raises:
    - The function does not explicitly raise exceptions.
    - Exceptions (TypeError, ValueError, or pandas-specific errors) may be raised by the underlying pandas reduction methods if the Series dtype or contents do not support the requested reductions. Those exceptions are propagated to the caller.

## Constraints:
Preconditions:
    - The caller must supply a pd.Series (otherwise attribute access will fail).
    - For meaningful numeric aggregates, the Series should contain numeric-compatible data; otherwise pandas will determine the result or raise.

Postconditions:
    - A dictionary with the eight listed keys is returned.
    - The input Series is not modified.

## Side Effects:
    - None: no I/O, no global state mutation, no network or file access. Only in-memory calls to pandas reduction methods occur.

## Control Flow:
flowchart TD
    Start --> Input[Receive series (pd.Series)]
    Input --> CallReductions["Call mean(), std(), var(), min(), max(), kurt(), skew(), sum() on series"]
    CallReductions --> Assemble["Assemble results into dict with fixed keys"]
    Assemble --> Return["Return resulting dict"]
    CallReductions -->|pandas returns NaN for statistic| NaNNote["Statistic value(s) may be NaN per pandas behavior"]
    NaNNote --> Return

## Examples:
Example 1 — typical numeric series:
- Given series = pd.Series([1.0, 2.0, None])
- numeric_stats_pandas(series) returns a dict with keys "mean","std","variance","min","max","kurtosis","skewness","sum", where values equal the corresponding series.method() results (NaN for metrics pandas cannot compute).

Example 2 — guarding against dtype errors:
- If the Series may contain non-numeric objects, callers can guard:
    try:
        stats = numeric_stats_pandas(series)
    except Exception as e:
        # handle or fallback (e.g., coerce dtype or skip numeric summary)
        raise

Usage note:
- Combine this function's output with other per-column summaries (null counts, histograms, unique counts) elsewhere in the profiling pipeline to produce full column reports.

## `src.ydata_profiling.model.pandas.describe_numeric_pandas.numeric_stats_numpy` · *function*

## Summary:
Compute common numeric summary statistics for a pandas Series using numpy operations and value-count weights (produces mean, std, variance, min, max, kurtosis, skewness, and sum).

## Description:
This function calculates a compact set of numeric summaries from:
- present_values: a numpy array of the series' non-missing observations,
- series: the original pandas Series (used to compute kurtosis and skewness),
- series_description: a dictionary that must include the pandas value-counts for non-missing values under the key "value_counts_without_nan".

Typical usage context:
- Intended for numeric summarization steps inside a profiling pipeline where callers prepare present_values and a value-counts summary (e.g., higher-level numeric description functions). No direct callers were found in the provided snippets; the function is designed to be invoked by numeric summarizers in the describe_numeric_* flow.

Why this logic is its own function:
- Centralizes the choices about how to compute mean and sum (weighted by value counts) and enforces ddof=1 for sample std/variance. This prevents duplication of weighting/aggregation logic across the profiling codebase and keeps numeric-stat computation consistent.

## Args:
    present_values (np.ndarray):
        1-D numeric numpy array of the Series' non-missing values.
        - Expected dtype: numeric (integers or floats).
        - Expected shape: (n,) where n >= 0.
        - Typical source: series.dropna().values
    series (pd.Series):
        Original pandas Series (may contain NaN). Only used for series.kurt() and series.skew(), which themselves ignore NA by pandas convention.
    series_description (Dict[str, Any]):
        A dictionary containing metadata for the series. Required key:
        - "value_counts_without_nan": a pandas.Series-like object produced by value_counts() on the non-NA subset:
            * index: unique observed values (numeric)
            * values: integer counts for each unique value
        - Typical example: vc = series.dropna().value_counts(); series_description["value_counts_without_nan"] = vc

Interdependencies:
- present_values should correspond to the same non-missing observations summarized by series_description["value_counts_without_nan"]. Inconsistencies between them will produce mismatched summary statistics (e.g., mean vs. std derived from different datasets).

## Returns:
Dict[str, Any] with keys (all numeric scalars or numpy/pandas scalar types):
    "mean":
        Weighted average of unique values computed as numpy.average(index_values, weights=vc.values).
    "std":
        Sample standard deviation of present_values computed with numpy.std(present_values, ddof=1).
        - If len(present_values) < 2, result will be NaN (numpy emits a RuntimeWarning; no exception is raised).
    "variance":
        Sample variance of present_values computed with numpy.var(present_values, ddof=1).
    "min":
        Minimum value among unique observed values (np.min(index_values)).
    "max":
        Maximum value among unique observed values (np.max(index_values)).
    "kurtosis":
        series.kurt() result (pandas behavior; may be NaN if insufficient data).
    "skewness":
        series.skew() result (pandas behavior; may be NaN if insufficient data).
    "sum":
        Weighted sum computed as np.dot(index_values, vc.values), equivalent to summing present_values.

Edge-case return notes:
- Empty inputs:
    * If present_values is empty, "std" and "variance" will be NaN (numpy behavior with ddof=1).
    * If vc (value_counts_without_nan) is empty, np.average, np.min, np.max, or np.dot will fail (see Raises).
- Non-numeric index_values or counts will cause type errors during numeric operations.

## Raises:
    KeyError:
        If "value_counts_without_nan" is missing from series_description.
    ValueError:
        - np.min(np.array([])) or np.max(np.array([])) raises ValueError for empty index_values.
        - np.dot with mismatched shapes may raise ValueError.
    TypeError:
        - If index_values or vc.values are non-numeric types incompatible with numpy numeric operations.
    Behavior dependent on numpy/pandas versions:
        - If the sum of weights (vc.values) is zero, numpy.average may return NaN or raise an error depending on numpy version and configuration.
    Notes:
        - numpy.std/var with ddof=1 on arrays of length < 2 produce NaN and emit a RuntimeWarning rather than raising an exception.

## Constraints:
Preconditions:
    - present_values must be a numeric 1-D numpy array representing the same non-missing observations summarized in series_description["value_counts_without_nan"].
    - series_description["value_counts_without_nan"] must be a pandas Series-like value-counts object with numeric index and numeric counts.
Postconditions:
    - Returns a dict containing the eight numeric summary measures.
    - Inputs are not mutated.

## Side Effects:
    - None observable: no I/O, no external state mutation, no network calls.
    - May emit numpy/pandas runtime warnings (e.g., insufficient degrees of freedom), which are not caught by this function.

## Control Flow:
flowchart TD
    A[Start]
    A --> B[vc = series_description["value_counts_without_nan"]]
    B --> C[index_values = vc.index.values]
    C --> D{index_values and vc.values numeric and non-empty?}
    D -->|Yes| E[Compute mean = np.average(index_values, weights=vc.values)]
    E --> F[Compute std = np.std(present_values, ddof=1)]
    F --> G[Compute variance = np.var(present_values, ddof=1)]
    G --> H[Compute min = np.min(index_values); max = np.max(index_values)]
    H --> I[Compute kurtosis = series.kurt(); skewness = series.skew()]
    I --> J[Compute sum = np.dot(index_values, vc.values)]
    J --> K[Return result dict]
    D -->|No| L[Numeric operations will raise ValueError/TypeError or produce NaN]
    L --> M[Exception or NaN propagate to caller]

## Examples (concise usage and error handling guidance):
- Basic usage (sequence of operations; not a function definition):
    present_values = series.dropna().values
    vc = series.dropna().value_counts()
    series_description = {"value_counts_without_nan": vc}
    result = numeric_stats_numpy(present_values, series, series_description)
    # result is a dict with keys: mean, std, variance, min, max, kurtosis, skewness, sum

- Handling empty series (recommended caller-side guard):
    if series.dropna().empty:
        # Skip numeric summarization or supply defaults
        result = {k: numpy.nan for k in ("mean","std","variance","min","max","kurtosis","skewness","sum")}
    else:
        result = numeric_stats_numpy(series.dropna().values, series, {"value_counts_without_nan": series.dropna().value_counts()})

- Type validation recommendation:
    Ensure the series dtype is numeric (e.g., pandas.api.types.is_numeric_dtype(series)) before calling this function to avoid TypeError from numpy operations.

## `src.ydata_profiling.model.pandas.describe_numeric_pandas.pandas_describe_numeric_1d` · *function*

## Summary:
Compute and append numeric summary statistics for a single pandas Series into a provided summary dictionary and return (config, series, stats). The function augments the input summary with counts (negatives, zeros, infinities), central-tendency and dispersion measures, quantiles, monotonicity flags, an optional chi-squared statistic, a histogram, and other derived metrics.

## Description:
This pandas-specific numeric summarizer finalizes numeric column statistics as part of the profiling pipeline after null-handling and basic counts have been prepared by earlier steps. It exists to centralize the logic that:
- computes counts derived from value_counts (negatives, zeros, infinities),
- chooses between a pandas-IntegerDtype branch and a numpy branch,
- prepares arrays used for robust/finite-only computations,
- calls specialized helpers for core numeric aggregates, MAD, chi-squared, and histogram generation,
- formats quantile keys and derives ratio/monotonicity metrics.

Why extracted:
- Keeps pandas-specific handling (nullable IntegerDtype, pandas reduction semantics) separate from generic numeric summarizers.
- Ensures consistent post-processing (quantiles formatting, monotonicity codes, CV/IQR) across profiling outputs.

Note on dependency documentation:
- The standalone documentation for mad previously noted that "no direct internal callers were found during analysis of this module." That analysis did not detect every usage site. In the current source, pandas_describe_numeric_1d does call mad(present_values) — so callers do exist even if earlier scans did not list them. The documentation here therefore documents the actual call relationships present in the implementation.

Known callers (typical):
- Higher-level numeric description orchestrators such as describe_numeric_1d or pandas dispatchers within the profiling pipeline that compute per-column summaries and then finalize numeric properties via this function.

Key responsibility boundary:
- Expects certain precomputed items in the input summary (notably "value_counts_without_nan", "n", "n_distinct"); does not compute initial null counts or value_counts itself.
- Does not fully sanitize inputs for NaNs before calling helpers: it passes present_values (which may include NaNs) to numeric_stats_numpy and directly to mad; it separately constructs finite_values (with numpy.isfinite) for operations that require finite-only input (chi-square, histogram). Callers and helpers share responsibility for how NaNs are handled:
    - mad: the mad utility uses numpy.median semantics (NaNs propagate) and is called here with present_values as provided by this function.
    - numeric_stats_numpy: expects a value-counts entry in summary and will operate under numpy/pandas semantics; pandas_describe_numeric_1d passes the raw present_values and the original series so helpers compute kurtosis/skew via series and weighted mean/sum via the value_counts.
    - numeric_stats_pandas: called for IntegerDtype and delegates to pandas reductions which themselves follow pandas NaN semantics.

## Args:
    config (Settings)
        - Profiling settings. Required fields used:
            * config.vars.num.chi_squared_threshold (float)
            * config.vars.num.quantiles (iterable of floats in [0,1])
            * config.plot.histogram and nested properties used by histogram_compute
        - Missing attributes will raise AttributeError.

    series (pandas.Series)
        - The series to summarize. Used both as a source of values and for pandas-specific properties:
            * series.dtype
            * series.is_monotonic_increasing / is_monotonic_decreasing
            * series.is_unique
            * series.quantile(quantiles)
            * series.kurt() and series.skew() (via numeric_stats_numpy)
        - May contain NA/NaN or infinite values; the function handles them according to numpy/pandas semantics described below.

    summary (dict)
        - Precomputed summary information that must include:
            * "value_counts_without_nan": pandas Series of value counts for non-NA values (index = values, values = integer counts)
            * "n": total number of observations (including NAs as provided by caller)
            * "n_distinct": number of distinct non-NA values
        - The dict is mutated in-place and returned as the stats object.

## Returns:
    Tuple[Settings, pandas.Series, dict]
        - (config, series, stats) where stats is the same dict object as the input summary after in-place augmentation.

Added/updated keys in stats (representative, not exhaustive):
    - Counts/ratios: "n_negative", "p_negative", "n_infinite", "n_zeros", "p_zeros", "p_infinite"
    - Basic numeric aggregates (via numeric_stats_pandas or numeric_stats_numpy): "mean","std","variance","min","max","kurtosis","skewness","sum"
    - "mad" (median absolute deviation) computed by mad(present_values) where present_values may contain NaN
    - Optional "chi_squared" (if config.vars.num.chi_squared_threshold > 0.0), computed on finite_values
    - "range" (max - min), quantile keys formatted as percentages (e.g., "25%"), "iqr", "cv"
    - Monotonicity indicators: "monotonic_increase","monotonic_decrease","monotonic_increase_strict","monotonic_decrease_strict","monotonic" (int code)
    - Histogram returned under the key supplied to histogram_compute (default "histogram")

Edge-case return notes:
- Numeric aggregates follow numpy/pandas semantics: eg std/var with ddof=1 may be NaN for n<2; median/mad may be NaN if input contains NaN and not filtered; min/max on empty arrays raise ValueError from numpy.
- If chi_squared_threshold <= 0.0, no "chi_squared" key is added.
- If required summary keys are absent, the function raises KeyError before producing stats.

## Raises:
    KeyError:
        - If summary lacks "value_counts_without_nan", "n", or "n_distinct", a KeyError will be raised on access.

    AttributeError:
        - If config or series lacks expected attributes (e.g., config.vars.num.quantiles).

    TypeError / ValueError:
        - Propagated from helper calls and numpy/pandas operations. Examples:
            * numeric operations on non-numeric value_counts.index or weights may raise TypeError/ValueError.
            * numpy.min/np.max on empty arrays will raise ValueError.
            * numeric_stats_numpy may raise KeyError if it expects "value_counts_without_nan" and it's missing.
    Notes:
        - The function intentionally does not catch these errors; it relies on callers to ensure preconditions or to handle exceptions.

## Constraints:
Preconditions:
    - summary must include "value_counts_without_nan" (a pandas Series), "n" (int), and "n_distinct" (int).
    - config.vars.num.quantiles must be an iterable of floats between 0 and 1.
    - The content of series and summary["value_counts_without_nan"] should correspond to the same dataset for meaningful aggregated results.

Postconditions:
    - summary (stats) is mutated in-place to include numeric statistics described above.
    - The original config and series objects are returned unchanged.

## Side Effects:
    - In-place mutation of the provided summary dict (stats = summary).
    - No I/O, no network, and no global state changes outside the mutated summary dict.
    - May emit numpy/pandas runtime warnings (e.g., insufficient degrees of freedom); warnings are not caught.

## Control Flow:
flowchart TD
    Start --> ReadConfig["Read chi_squared_threshold and quantiles from config"]
    ReadConfig --> GetVC["value_counts = summary['value_counts_without_nan']"]
    GetVC --> NegIdx["negative_index = value_counts.index < 0"]
    NegIdx --> SetNegCounts["summary['n_negative'] = value_counts.loc[negative_index].sum(); p_negative = n_negative/n"]
    SetNegCounts --> InfIdx["infinity_index = value_counts.index.isin([inf, -inf]); set n_infinite"]
    InfIdx --> ZeroCount["Set n_zeros = 0; if 0 in value_counts.index then set n_zeros"]
    ZeroCount --> StatsAlias["stats = summary (alias; mutate in-place)"]
    StatsAlias --> IsIntegerDtype{"isinstance(series.dtype, IntegerDtype)?"}
    IsIntegerDtype -->|Yes| IntegerBranch["stats.update(numeric_stats_pandas(series)); present_values = series.astype(str(series.dtype).lower()); finite_values = present_values"]
    IsIntegerDtype -->|No| NumpyBranch["present_values = series.values; finite_values = present_values[np.isfinite(present_values)]; stats.update(numeric_stats_numpy(present_values, series, summary))"]
    IntegerBranch --> AfterNumeric
    NumpyBranch --> AfterNumeric
    AfterNumeric --> AddMAD["stats.update({'mad': mad(present_values)}) -- mad uses numpy.median semantics (NaNs propagate)"]
    AddMAD --> IfChiSq{"chi_squared_threshold > 0.0 ?"}
    IfChiSq -->|Yes| ChiSq["stats['chi_squared'] = chi_square(finite_values)"]
    IfChiSq -->|No| SkipChiSq
    ChiSq --> RangeQuant["Compute range, series.quantile(quantiles) formatted as '25%', set iqr, cv, p_zeros, p_infinite"]
    RangeQuant --> MonotonicFlags["Compute monotonic flags from series properties and set stats['monotonic'] code"]
    MonotonicFlags --> Histogram["Call histogram_compute(config, finite non-inf values, n_unique, weights=counts)"]
    Histogram --> Return["Return (config, series, stats)"]

## Examples:
Example 1 — typical float series:
    from ydata_profiling.config import Settings
    import pandas as pd
    import numpy as np

    cfg = Settings()  # must have vars.num.quantiles and vars.num.chi_squared_threshold set
    series = pd.Series([0.0, 1.0, 2.0, np.nan, np.inf, -np.inf])
    vc = series.dropna().value_counts()
    summary = {"value_counts_without_nan": vc, "n": len(series), "n_distinct": vc.size}

    config_out, series_out, stats = pandas_describe_numeric_1d(cfg, series, summary)
    # stats contains 'n_negative','n_infinite','n_zeros','mad','range','histogram','25%','50%','75%','monotonic', etc.

Example 2 — nullable IntegerDtype branch and NaN semantics:
    import pandas as pd
    from pandas.core.arrays.integer import IntegerDtype
    import numpy as np

    series = pd.Series([1, 2, None], dtype=IntegerDtype())
    vc = series.dropna().value_counts()
    summary = {"value_counts_without_nan": vc, "n": len(series), "n_distinct": vc.size}

    # numeric_stats_pandas will be used for base aggregates (pandas reductions handle NA according to pandas rules)
    cfg_out, s_out, stats = pandas_describe_numeric_1d(cfg, series, summary)
    # mad is computed from present_values produced by series.astype(...); mad will follow numpy median semantics (NaNs propagate)

Example 3 — defensive handling of missing summary keys:
    try:
        pandas_describe_numeric_1d(cfg, series, {})
    except KeyError:
        vc = series.dropna().value_counts()
        summary = {"value_counts_without_nan": vc, "n": len(series), "n_distinct": vc.size}
        pandas_describe_numeric_1d(cfg, series, summary)

Implementation notes for reimplementation:
- Use value_counts = summary["value_counts_without_nan"] and compute masks for negative and infinity index membership to set counts.
- For IntegerDtype: call numeric_stats_pandas(series), then create present_values by casting series.astype(str(series.dtype).lower()) (matching the original code's cast), and set finite_values = present_values for downstream steps.
- For non-IntegerDtype: set present_values = series.values (may include NaN), finite_values = present_values[np.isfinite(present_values)], and call numeric_stats_numpy(present_values, series, summary). Note: numeric_stats_numpy expects a value_counts entry in summary and uses series for kurt/skew; it will operate under numpy/pandas semantics for NaNs.
- Call mad(present_values) directly; mad uses numpy.median semantics and does not filter NaNs itself.
- Only compute chi_square on finite_values and when config.vars.num.chi_squared_threshold > 0.
- Format quantiles using series.quantile(quantiles).to_dict() and map percentile floats to percent strings using f"{percentile:.0%}".
- Build histogram via histogram_compute with finite non-inf value array and corresponding counts as weights; remove infinite values from the value_counts input using the infinity_index mask.

