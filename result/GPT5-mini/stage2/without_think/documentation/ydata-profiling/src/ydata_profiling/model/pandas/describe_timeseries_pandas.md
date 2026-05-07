# `describe_timeseries_pandas.py`

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.stationarity_test` · *function*

## Summary:
Runs the Augmented Dickey-Fuller (ADF) test on a pandas Series and returns a boolean indicating stationarity at the configured significance level together with the raw p-value.

## Description:
This function retrieves a significance threshold from the provided config object, calls statsmodels.tsa.stattools.adfuller on the non-missing values of the supplied pandas Series (series.dropna()), and returns whether the resulting p-value is strictly less than the configured threshold plus the p-value itself.

Call context:
- The function body does not reference other functions in this file; it is a utility intended to be used by time-series analysis or summarization code that needs a consistent stationarity decision based on a configurable threshold.

Why a separate function:
- Centralizes threshold lookup, NaN handling (dropna), the adfuller invocation, and the p-value-to-boolean conversion so that callers do not duplicate these steps and behavior remains consistent.

## Args:
    config (Settings):
        - Configuration object expected to expose the attribute path config.vars.timeseries.significance.
        - The function reads this attribute and uses its value as the decision threshold; the function performs no validation of the numeric range or type beyond what Python naturally enforces during comparison.
    series (pandas.Series):
        - A one-dimensional pandas Series containing the observations to test.
        - The function calls series.dropna() internally; the cleaned series is passed to adfuller and must satisfy adfuller's input requirements (numeric values, sufficient length/variation).

Interdependencies:
- The function depends on the presence of config.vars.timeseries.significance. If this attribute path is missing, attribute access will raise an exception before running the test.

## Returns:
    Tuple[bool, float]
    - (is_stationary, p_value)
    - is_stationary (bool): True if p_value < significance_threshold, otherwise False.
    - p_value (float): The p-value returned by adfuller, taken from the adfuller result tuple at index 1.

Notes on return values:
- p_value is returned exactly as extracted from adfuller; it may be a numpy scalar (e.g., numpy.float64).
- There is no special-case return for empty or invalid input; in those cases adfuller will raise and no tuple is returned.

## Raises:
- Propagates any exception raised by statsmodels.tsa.stattools.adfuller when called with series.dropna(). Typical examples (raised by adfuller) include:
    - ValueError for inputs that are too short or have no variation.
    - TypeError if the series contains non-numeric types incompatible with the test.
- AttributeError (or related) if config.vars.timeseries.significance is not present on the provided config object.
- The function intentionally does not catch or wrap these exceptions.

## Constraints:
Preconditions:
- config must provide config.vars.timeseries.significance.
- series must be a pandas.Series whose non-missing values are valid input for adfuller.

Postconditions:
- No mutation of the input series or config.
- Returns a tuple whose first element is the boolean comparison result and second element is the adfuller p-value if no exception occurred.

## Side Effects:
- No file, network, or stdout IO.
- No mutation of global state.
- External call to statsmodels.tsa.stattools.adfuller; any side effects caused by that function are external to this function.

## Control Flow:
flowchart TD
    Start([Start])
    A[Read significance_threshold = config.vars.timeseries.significance]
    B[cleaned = series.dropna()]
    C[Call adfuller(cleaned)]
    D[Extract p_value = adfuller_result[1]]
    E{p_value < significance_threshold}
    F[Return (True, p_value)]
    G[Return (False, p_value)]
    Start --> A --> B --> C --> D --> E
    E -- True --> F
    E -- False --> G

(Note: the function does not itself validate cleaned; if cleaned is empty or invalid, adfuller will raise an exception and no return occurs.)

## Examples:
Typical usage pattern (illustrative):
- Preconditions: config.vars.timeseries.significance exists and is set (e.g., 0.05). 's' is a pandas Series.
- Usage:
    try:
        is_stationary, pval = stationarity_test(config, s)
    except Exception as e:
        # Handle or log the error (e.g., insufficient data for the test)
        is_stationary, pval = False, float("nan")
    if is_stationary:
        # proceed with stationary-specific logic
        pass
    else:
        # proceed with non-stationary-specific logic
        pass

Edge-case handling:
- To avoid exceptions in callers, validate that the series has a sufficient number of non-missing numeric observations before calling this function (e.g., check series.dropna().size).

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.fftfreq` · *function*

## Summary:
Compute the discrete Fourier-transform sample frequencies for a signal of length n and sample spacing d, returning an array of frequency bins (cycles per unit of d) ordered to match numpy.fft.fftfreq.

## Description:
This small helper constructs the frequency axis used when analyzing the discrete Fourier transform (DFT) of a sequence of length n sampled every d units. It returns an array of length n containing frequencies corresponding to the outputs of an FFT: starting at 0, ascending through positive frequencies up to the Nyquist (or floor((n-1)/2) bin), then continuing with the negative-frequency bins.

Known callers and typical usage context:
- Used in spectral analysis steps: after computing an FFT of a timeseries of length n with sample spacing d, callers use this function to obtain the matching frequency values for plotting or peak detection.
- Typical pipeline stage: prepare time-series data -> compute FFT (e.g., via numpy.fft.fft) -> call this function to obtain frequencies -> pair frequencies with spectral magnitudes for analysis.
- Extracted into a dedicated function to ensure a single, testable implementation of FFT frequency bin generation that mirrors numpy.fft.fftfreq ordering and scaling.

Responsibility boundary:
- This function only computes frequency bin values. It does not compute FFTs, normalize magnitudes, or validate input series content beyond the numeric/shape expectations for n and d.

## Args:
    n (int):
        Number of samples in the discrete signal (length of the FFT output).
        - Required: integer.
        - Valid range: n > 0 (positive integer). Passing n == 0 or n < 0 results in exceptions from Python/numpy (see Raises).
    d (float, optional):
        Sample spacing (time or distance between successive samples). Defaults to 1.0.
        - Must be non-zero; d == 0 causes a division-by-zero error.
        - Units: returned frequencies are in cycles per unit of d.

Interdependencies:
    - The returned frequencies are scaled by 1.0 / (n * d). Therefore both n and d directly determine magnitude and sign of frequency values; passing invalid values (zero or inappropriate types) will raise errors.

## Returns:
    numpy.ndarray:
        One-dimensional numpy array of length n (dtype float) with the frequency bins in cycles per unit of d.
        - Ordering: [0, 1/(n*d), 2/(n*d), ..., floor((n-1)/2)/(n*d), -(n//2)/(n*d), ..., -1/(n*d)]
        - For n >= 1: the array contains floating-point values (e.g., float64).
        - The result matches numpy.fft.fftfreq(n, d) in value and ordering.

## Raises:
    ZeroDivisionError:
        - Trigger: when n == 0 or d == 0, the expression 1.0 / (n * d) causes a division by zero.
    ValueError:
        - Trigger: when n is negative; numpy.empty(n, int) (or other array construction) raises ValueError for negative sizes.
    TypeError:
        - Trigger: when n is not an integer-like value accepted by numpy array-size operations (e.g., passing a float that cannot be used as a size) or d is not numeric; underlying numpy/Python operations will raise TypeError.
Note:
    - The function does not explicitly raise these exceptions; they occur in the numeric division and numpy array creation operations used internally.

## Constraints:
Preconditions:
    - n must be a positive integer (n > 0).
    - d must be a non-zero numeric value (float or convertible to float).
    - Callers should validate or ensure these preconditions before calling to avoid upstream exceptions.

Postconditions:
    - On successful return, the resulting numpy.ndarray has length n and the frequencies are scaled by 1/(n*d).
    - The ordering and values are consistent with numpy.fft.fftfreq(n, d).

## Side Effects:
    - None. The function does not perform I/O, modify global state, or contact external services. It only performs local numeric computations and numpy array allocations.

## Control Flow:
flowchart TD
    Start --> ComputeVal[Compute val = 1.0 / (n * d)]
    ComputeVal -->|division by zero (n==0 or d==0)| RaiseZeroDiv[ZeroDivisionError]
    ComputeVal -->|success| Allocate[Allocate results = empty(n, int)]
    Allocate -->|n < 0| RaiseValueError[ValueError from numpy.empty]
    Allocate -->|n is not integer-like| RaiseTypeError[TypeError from numpy functions]
    Allocate --> ComputeN[Compute N = (n - 1) // 2 + 1]
    ComputeN --> BuildP1[Create p1 = arange(0, N, dtype=int)]
    ComputeN --> BuildP2[Create p2 = arange(-(n // 2), 0, dtype=int)]
    BuildP1 --> Fill1[Assign results[:N] = p1]
    BuildP2 --> Fill2[Assign results[N:] = p2]
    Fill1 --> Multiply[Return results * val]
    Fill2 --> Multiply

## Examples:
- Typical usage:
    - Input: n = 8, d = 1.0
    - Call: freqs = fftfreq(8, 1.0)
    - Output: numpy array [0.0, 0.125, 0.25, 0.375, -0.5, -0.375, -0.25, -0.125]
      (frequencies are in cycles per unit of d)

- Minimal valid input:
    - Input: n = 1, d = 2.0
    - Call: freqs = fftfreq(1, 2.0)
    - Output: numpy array [0.0]  (single zero-frequency bin)

- Error handling examples (usage patterns):
    - Guard against zero spacing:
        try:
            freqs = fftfreq(n, d)
        except ZeroDivisionError:
            # handle invalid sample spacing or zero-length n
            raise ValueError("n and d must be non-zero; ensure n>0 and d!=0")
    - Guard against invalid n:
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer")
Notes:
    - This implementation mirrors numpy.fft.fftfreq; if callers require exact numpy semantics for corner cases, they can use numpy.fft.fftfreq directly. Use this function when you want a local, dependency-light way to generate the same frequency ordering and scaling.

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.seasonality_test` · *function*

## Summary:
Detects whether a time series contains significant periodic (seasonal) components by locating peaks in its frequency spectrum and returns a boolean flag plus a list of detected season periods (in samples).

## Description:
This helper computes a frequency-domain representation of the input series (via get_fft), finds spectral peaks (via get_fft_peaks), and interprets their frequency locations as candidate seasonal periods by taking the reciprocal (1 / frequency). It is extracted as a focused, reusable step that isolates the decision logic for seasonality detection and the conversion from frequency peaks to period estimates; callers do not need to manage FFT computation or peak-selection details.

Known callers and typical usage context:
- No explicit direct callers are present in the provided snippet. Typical callers are higher-level time-series summarization or profiling functions (for example, a describe_timeseries_1d routine) that need to report whether a series appears seasonal and the estimated seasonal periods during dataset profiling.
- Typical pipeline stage: called after basic cleaning and null-handling, during feature extraction or summary-statistic computation for a single numeric time series.

Why this is a separate function:
- Encapsulates: (1) orchestration of FFT → peak detection → period conversion and (2) a simple, consistent output format used by downstream reporting. This separation prevents duplication of spectral analysis logic and improves testability.

## Args:
    series (pandas.Series):
        - Description: 1-D sequence of numeric samples representing the time series to analyze.
        - Constraints: should be convertible to a 1-D NumPy array (series.to_numpy()); numeric dtype is expected. NaN or infinite values are not explicitly removed by this function and will propagate into the FFT/peak logic.
    mad_threshold (float, optional):
        - Description: Threshold parameter forwarded to get_fft_peaks that controls how aggressively spectral peaks are selected (the exact interpretation depends on get_fft_peaks implementation).
        - Allowed values: any finite float; typical default is 6.0 which biases selection toward peaks that are strong relative to local MAD-based noise estimates.
        - Default: 6.0
    Notes on interdependencies:
        - The function relies on get_fft to produce a frequency table whose "freq" values are in units of cycles per sample (positive frequencies), and on get_fft_peaks to return a pandas-like DataFrame or similar mapping with a column/key named "freq". If get_fft_peaks returns a different structure, this function will fail.

## Returns:
    dict with the following keys:
    - "seasonality_presence" (bool):
        - True if at least one spectral peak (as returned in the peaks structure) was detected; False otherwise.
    - "seasonalities" (list[float]):
        - A list of estimated seasonal periods expressed in samples (float). Each element is computed as 1 / freq where freq is the spectral peak frequency (cycles per sample).
        - If no peaks are detected, this list is empty.
        - If any freq value is zero (unexpected for positive-frequency spectra) the reciprocal will produce +inf per IEEE floating-point behavior; callers should handle/infer that case as needed.

All return values are produced deterministically from the outputs of get_fft and get_fft_peaks: the presence flag is based on whether peaks has any rows (len(peaks.index) > 0), and seasonalities is derived by transforming peaks["freq"] using 1 / freq and converting to a Python list.

## Raises:
    - This function does not raise exceptions explicitly.
    - Exceptions raised by dependencies may propagate:
        - Errors from get_fft (e.g., TypeError/ValueError on invalid series input).
        - Errors from get_fft_peaks (e.g., if it expects different input types).
        - AttributeError/KeyError if the returned peaks object does not have an index attribute or does not contain a "freq" column/key.
        - ZeroDivisionWarning does not raise by default, but a reciprocal of zero will produce +inf; numpy/pandas warnings or errors may propagate depending on configuration.

## Constraints:
    Preconditions:
    - Caller must supply a pandas.Series representing a one-dimensional numeric time series.
    - get_fft must return frequency values in cycles per sample and get_fft_peaks must return an object with:
        - an index supporting len(peaks.index)
        - a column/key named "freq" containing numeric (non-null) frequency values
    - The sampling interval assumption (inherited from get_fft) is 1.0 sample unit; therefore 1 / freq yields period in samples.

    Postconditions:
    - The returned dictionary always contains the two keys "seasonality_presence" and "seasonalities".
    - If seasonality_presence is False then seasonalities is an empty list.
    - If seasonality_presence is True then seasonalities is a list of floats (may include +inf or NaN if peaks["freq"] contains 0 or NaN).

## Side Effects:
    - None intrinsic: the function performs only in-memory computations and returns a new Python dict.
    - No I/O (files, network) is performed.
    - No mutation of the input series or global state is performed.
    - Any side effects originate from get_fft or get_fft_peaks if those functions perform side effects (not expected in typical implementations).

## Control Flow:
flowchart TD
    A[Start: call seasonality_test(series, mad_threshold)] --> B[Compute fft = get_fft(series)]
    B --> C[Compute peaks via get_fft_peaks(fft, mad_threshold)]
    C --> D{Are there any peaks? (len(peaks.index) > 0)}
    D -- No --> E[seasonality_presence = False; seasonalities = []]
    D -- Yes --> F[seasonality_presence = True]
    F --> G[Compute seasonalities = peaks["freq"].transform(1 / x) -> list]
    E --> H[Return {"seasonality_presence": False, "seasonalities": []}]
    G --> H[Return {"seasonality_presence": True, "seasonalities": [...]}]

## Examples:
- Typical detected season example (described):
    - Input: a pandas.Series containing a pure sinusoid with a period of 10 samples (for example, samples generated using sin(2π * (1/10) * t) for t = 0..N-1). After FFT and peak selection, get_fft_peaks should identify a peak near frequency 0.1 cycles/sample.
    - Behavior: seasonality_presence will be True and seasonalities will contain a value near 10.0 (the estimated samples-per-cycle).

- No-seasonality example (described):
    - Input: a pandas.Series of uncorrelated white noise.
    - Behavior: get_fft_peaks typically finds no prominent spectral peaks; seasonality_presence will be False and seasonalities will be an empty list.

- Error handling guidance (described):
    - If the series contains non-numeric data or a dtype that cannot be converted to a numeric 1-D array, calling code should catch the propagated exception (TypeError/ValueError) and either coerce/clean the data or skip seasonality detection for that series.
    - If the returned seasonalities include +inf or NaN values, handle these as indicators of degenerate or invalid frequency results (e.g., zero-frequency peaks or missing data) and treat them as "no reliable seasonality" for downstream reporting.

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.get_fft` · *function*

## Summary:
Produces a one-sided frequency table (positive frequency bins) and corresponding power amplitude in decibels from a 1-D pandas Series using a fast Fourier transform.

## Description:
- Known callers:
    - No direct callers are present in the provided snippet. This helper is intended for time-series analysis/summarization code that needs a frequency-domain representation.
- Why this function exists:
    - Encapsulates the low-level FFT computation and conversion to a power (squared magnitude) expressed in decibels, returning only strictly positive frequency components. This keeps callers focused on higher-level analysis (peak finding, feature extraction) without duplicating FFT boilerplate.

## Args:
    series (pandas.Series): 1-D time-domain samples.
        - Expected content: numeric values (real or complex). The function calls series.to_numpy(), so any dtype acceptable to NumPy/SciPy FFT routines is allowed.
        - Length: any non-negative integer. No reshaping or dimensional checks are performed beyond the Series -> 1-D array conversion.
        - Note: NaN or infinite values in the Series are not handled explicitly and will propagate into the FFT and subsequent numeric results.

## Returns:
    pandas.DataFrame: DataFrame with two columns:
        - "freq" (float): strictly positive frequency bins extracted from the FFT frequency generator (units: cycles per sample, because the sampling interval parameter is fixed at 1.0).
        - "ampl" (float): power amplitude for each positive frequency expressed in decibels, computed as 10 * log10(|FFT|^2) where |FFT|^2 is the squared magnitude of the complex FFT value.
    - All rows correspond elementwise: ampl[i] is the 10*log10 of the power at freq[i].
    - Edge-case return values:
        - If the input length yields no strictly positive frequencies (e.g., very short inputs), the returned DataFrame will be empty but will still have columns ["freq", "ampl"].
        - Where the power is exactly zero, ampl will be -inf (IEEE float) because log10(0) -> -inf. NaN inputs will produce NaN entries in the output where they affect the computation.

## Raises:
    - The function does not raise exceptions explicitly.
    - Errors thrown by underlying calls may propagate:
        - TypeError/ValueError if series.to_numpy() or the FFT routine cannot process the input dtype/shape.
        - Any exceptions raised by the FFT implementation, numpy absolute/log operations, or fft frequency generator will propagate unchanged to the caller.
    - Note: computing log10 of non-positive values yields -inf or NaN per NumPy rules rather than raising.

## Constraints:
- Preconditions:
    - The caller must pass a pandas.Series representing a 1-D sequence of samples.
    - The sampling interval is assumed to be 1.0 (hard-coded), so frequency units are cycles per sample.
    - Module-level names referenced by the function (FFT routine and fftfreq) must be available in the execution scope; otherwise a NameError will occur when calling the function.
- Postconditions:
    - The returned DataFrame contains exactly as many rows as there are strictly positive entries in the frequency array produced for the input length.
    - The "freq" column is the positive subset of fftfreq(N, 1.0) and is aligned with "ampl".

## Side Effects:
    - None: the function performs only in-memory numeric computations and returns a new pandas DataFrame. It does not perform I/O, mutate globals, or change the input Series.

## Control Flow:
flowchart TD
    A[Start: receive pandas.Series] --> B[Convert to numpy array: series.to_numpy()]
    B --> C[Compute complex FFT: _pocketfft.fft(array)]
    C --> D[Compute power: abs(FFT) ** 2]
    D --> E[Compute frequency bins: fftfreq(N, 1.0)]
    E --> F[Select positive-frequency indices: fftfreq > 0]
    F --> G[Extract positive freq: freq = fftfreq[pos_ix]]
    D --> H[Extract positive power: power_pos = power[pos_ix]]
    H --> I[Convert to dB: ampl = 10 * log10(power_pos)]
    G --> J[Build DataFrame {"freq": freq, "ampl": ampl}]
    I --> J
    J --> K[Return DataFrame]

## Examples:
- Typical usage:
    - Compute the positive-frequency power spectrum (dB) of a sampled signal (sampling interval assumed 1.0).
    Example:
        import pandas as pd
        import numpy as np

        t = np.linspace(0, 1, 128, endpoint=False)
        signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
        series = pd.Series(signal)

        spectrum_df = get_fft(series)
        # spectrum_df["freq"] contains positive-frequency bins (cycles per sample)
        # spectrum_df["ampl"] contains power in decibels for each bin

- Short input handling:
    - Empty or single-element inputs produce an empty DataFrame (no positive-frequency bins):
        empty_df = get_fft(pd.Series(dtype=float))
        # empty_df has columns ["freq", "ampl"] and zero rows

- Error propagation example:
    try:
        df = get_fft(bad_series)  # bad_series is not convertible to a numeric 1-D array
    except Exception as e:
        # Underlying TypeError/ValueError or library-specific exceptions are propagated
        handle_error(e)

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.get_fft_peaks` · *function*

*No documentation generated.*

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.identify_gaps` · *function*

## Summary:
Detects large gaps in a monotonically increasing pandas Series by computing consecutive differences and returning statistics for differences that exceed a tolerance-based threshold, plus the pairs of values that bracket each detected gap.

## Description:
This helper isolates the logic for identifying unusually large jumps between successive entries in an ordered Series.

Known callers within the provided codebase:
- None discovered in the supplied context. (If used elsewhere, typical callers are higher-level time-series summarization routines that need to report or visualize missing intervals or sampling irregularities.)

Why this is a separate function:
- Encapsulates the gap-detection logic so other code can reuse a consistent definition of "large gap" (based on mean positive difference scaled by gap_tolerance) and receive both the numeric gap statistics and the actual value pairs that bracket each gap. Keeps higher-level reporting code free of diff/threshold calculation details.

## Args:
    gap (pandas.Series):
        A 1-dimensional pandas Series containing ordered values (timestamps or numeric values).
        - The function compares consecutive values in this Series (via gap.diff()).
        - The Series must be ordered in the sense that meaningful "gaps" are represented by positive differences between consecutive entries.
        - The Series' index is used to locate anchors; the implementation assumes the index supports positional integer indexing when slicing by positions (common when the index is a RangeIndex or integer index). If the index is a DatetimeIndex or other non-integer labels, anchors will still be computed, but the subsequent positional indexing (i - 1) may raise a runtime error.
    is_datetime (bool):
        If True, differences are treated as pandas Timedelta objects and zero is set to pd.Timedelta(0). If False, differences are numeric and zero is the integer 0.
        - Choose True when gap contains datetime-like values (so diff() yields Timedelta objects).
    gap_tolerance (int, optional; default=2):
        Multiplier applied to the mean of the positive (non-zero) differences to form a threshold. Allowed values: positive integers (>=1) are meaningful.
        - Effect: min_gap_size = gap_tolerance * mean_of_positive_diffs. Differences larger than this threshold are considered "large gaps".
        - Interdependency: If there are no positive (non-zero) differences, the computed mean will be NaN and the function will return empty results (see Returns).

## Returns:
    Tuple[pandas.Series, list]
    - gap_stats (pandas.Series):
        A Series containing the subset of positive consecutive differences that are strictly greater than the computed threshold (min_gap_size). This Series keeps the same index positions as the diff() result for those differences.
        - If no positive differences exist or none exceed the threshold, this will be an empty Series (dtype depends on gap.diff()).
    - gaps (list):
        A list of 2-element numpy arrays; each element is the pair of original gap values (the value immediately before and after the detected anchor) that bracket a detected large difference.
        - Example element: array([value_at_position_i_minus_1, value_at_position_i], dtype=...)
        - If no gaps are detected, this list is empty.

## Raises:
    - The function does not explicitly raise custom exceptions.
    - Possible runtime exceptions that may propagate:
        * TypeError or ValueError if comparisons (diff > zero) are invalid for the Series' dtype.
        * TypeError or IndexError if the Series index labels are non-integer (for example a DatetimeIndex) because the code uses expressions like (i - 1) assuming anchor values can be used as integer positions. To avoid this, ensure the Series index supports integer positional addressing or reset the index before calling this function.

## Constraints:
Preconditions:
    - gap must be a pandas.Series with at least one element (ideally >=2 to have a meaningful diff()).
    - Values in gap should be ordered; meaningful "gaps" require monotonic (or at least non-decreasing) successive values.
    - gap_tolerance should be a positive integer (default 2).
    - If is_datetime is True, gap values should be datetime-like so gap.diff() returns Timedelta objects.

Postconditions:
    - Returned gap_stats contains only positive differences larger than gap_tolerance * mean_of_positive_differences.
    - Returned gaps lists the original value-pairs that bracket each identified gap, in the same order as anchors were found.

## Side Effects:
    - No I/O (no file, network, or stdout interactions).
    - No mutation of the input Series object (the function only reads from it).
    - No external state changes.

## Control Flow:
flowchart TD
    A[Start] --> B[Compute zero: Timedelta(0) if is_datetime else 0]
    B --> C[diff = gap.diff()]
    C --> D[non_zero_diff = diff where diff > zero]
    D --> E[min_gap_size = gap_tolerance * mean(non_zero_diff)]
    E --> F[gap_stats = non_zero_diff where non_zero_diff > min_gap_size]
    E --> G[anchors = indices where diff > min_gap_size]
    G --> H{anchors empty?}
    H -- Yes --> I[Return gap_stats (maybe empty), gaps = []]
    H -- No --> J[For each anchor i -> append pair (value at i-1, value at i) to gaps]
    J --> I[Return gap_stats, gaps]

## Examples:

1) Numeric series (regular case)
    # gap: numeric readings sampled over time (index is integer positions)
    s = pandas.Series([0.0, 0.1, 0.15, 5.0, 5.1, 10.0])
    gap_stats, gaps = identify_gaps(s, is_datetime=False, gap_tolerance=2)
    # gap_stats: Series with differences greater than threshold (e.g., between 0.15 and 5.0, and between 5.1 and 10.0 if they exceed threshold)
    # gaps: [[0.15, 5.0], [5.1, 10.0]] (numpy arrays)

2) Datetime series (timestamps)
    # Series values are timestamps but the index is integer positions (common if you store timestamps as values)
    times = pandas.Series([
        pandas.Timestamp("2023-01-01 00:00:00"),
        pandas.Timestamp("2023-01-01 00:01:00"),
        pandas.Timestamp("2023-01-01 00:02:00"),
        pandas.Timestamp("2023-01-01 00:10:00"),
    ])
    gap_stats, gaps = identify_gaps(times, is_datetime=True, gap_tolerance=2)
    # gap_stats: Timedelta Series with entries > min_gap_size (e.g., 8 minutes)
    # gaps: [[Timestamp('2023-01-01 00:02:00'), Timestamp('2023-01-01 00:10:00')]]

3) Defensive usage when index is non-integer:
    # If your Series uses a DatetimeIndex as the index labels, reset to default integer index first:
    safe_series = original_series.reset_index(drop=True)
    gap_stats, gaps = identify_gaps(safe_series, is_datetime=True)
    # This avoids runtime errors due to subtraction (i - 1) on non-integer index labels.

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.compute_gap_stats` · *function*

## Summary:
Computes statistics about gaps in a time-series' sampling by inspecting the series' index (after dropping null observations) and returning numeric summary statistics and the list of detected gap intervals.

## Description:
This function examines the original series' index (not the series values) to find unusually large gaps between successive observations and summarizes those gaps with basic statistics.

Known callers within the supplied codebase:
- No direct callers were discovered in the provided context. Typical callers are higher-level time-series summarization or profiling routines that need to report sampling irregularities, missing intervals, or anomalous time jumps.

Why this is a separate function:
- It encapsulates the steps required to (1) prepare the index values (drop NA, reset index), (2) detect large gaps (delegates to identify_gaps), and (3) compute summary statistics from the detected gaps. This isolates index-based gap detection and aggregation from the rest of the timeseries summarization logic so other parts of the code can reuse a consistent, well-documented gap-summary result.

## Args:
    series (pandas.Series):
        A 1-D pandas Series whose index encodes the sampling points (e.g., timestamps or numeric sample positions).
        - The function drops NaN-valued observations from the series before computing gaps; the presence of NaNs in the series' values therefore only affects which observations are considered, not the gap-detection logic itself.
        - Precondition: the series' index must represent ordered sampling positions (monotonic or at least ordered as stored). Common cases:
            * If the Series uses a DatetimeIndex, gaps are treated as timedeltas.
            * Otherwise, gaps are treated as numeric differences between adjacent index values.
        - Interdependency: The function inspects series.index to set is_datetime and then resets the index so that identify_gaps receives a Series containing the original index values (integer positional index after reset). Therefore, identify_gaps will operate on the original index values (timestamps or numbers) rather than on the series' values.

## Returns:
    dict
    A dictionary with the following keys (this reflects the actual runtime return value; note the function's annotated return type is pandas.Series but the implementation returns a dict):
        - "min": numeric or timedelta
            The minimum detected "large gap" value (gap_stats.min()). If no gaps were detected, this will typically be NaN.
        - "max": numeric or timedelta
            The maximum detected "large gap" value (gap_stats.max()). If no gaps were detected, this will typically be NaN.
        - "mean": numeric or timedelta
            The mean of detected large gaps (gap_stats.mean()). If no gaps were detected, this will typically be NaN.
        - "std": numeric or timedelta
            The standard deviation of detected large gaps. Implemented as gap_stats.std() when more than one gap exists; otherwise 0 when gap_stats has length <= 1.
        - "series": pandas.Series
            The original input series (unchanged except that the function used dropna() and reset_index() internally for computation — the returned "series" is the original object passed to the function).
        - "gaps": list
            The list of gap bracket pairs produced by identify_gaps; each element is a 2-element numpy array [value_before, value_after] that brackets a detected gap. If no gaps are detected, this is an empty list.

Edge-case return behavior:
    - If the input series has no non-NaN observations, identify_gaps will operate on an empty series and gap_stats will be empty; "min", "max", and "mean" will be NaN; "std" will be 0; "gaps" will be [].
    - If exactly one large gap is detected, "std" is explicitly set to 0 by this function (the implementation uses 0 when len(gap_stats) <= 1).

## Raises:
    - The function does not explicitly raise exceptions.
    - Possible exceptions that may propagate:
        * Any exceptions raised by identify_gaps (e.g., due to incompatible dtypes or unexpected values) will propagate.
        * TypeErrors or ValueErrors may occur if index values do not support ordering/differencing in a way identify_gaps expects.
    - Note: because compute_gap_stats resets the index (reset_index()) and passes the original index values to identify_gaps, many index-label-related IndexError/TypeError issues are avoided; remaining errors will typically originate from invalid index value types or from identify_gaps logic.

## Constraints:
Preconditions:
    - The input must be a pandas.Series.
    - The series.index must meaningfully represent sampling order (timestamps or numeric sample positions). The function relies on the index values to detect gaps.
    - Values in the series are allowed to be NaN; these entries are dropped before gap computation.

Postconditions (guarantees after return):
    - The function returns a dict containing summary statistics computed from the subset of detected "large" gaps (as produced by identify_gaps) and the raw list of gap bracket pairs.
    - The original input series object is returned inside the dict under the "series" key unchanged by this function.

## Side Effects:
    - No file, network, or stdout I/O is performed.
    - No global state is mutated.
    - The input series object is not modified in place by this function (dropna() and reset_index() are called on temporary objects; the original series reference is included in the returned dict but not mutated).

## Control Flow:
flowchart TD
    A[Start: compute_gap_stats(series)] --> B[gap = series.dropna()]
    B --> C[index_name = gap.index.name if set else "index"]
    C --> D[gap = gap.reset_index()[index_name]  (now Series of original index values)]
    D --> E[is_datetime = isinstance(series.index, pd.DatetimeIndex)]
    E --> F[call identify_gaps(gap, is_datetime) -> (gap_stats, gaps)]
    F --> G[Compute stats dict fields:
        min = gap_stats.min()
        max = gap_stats.max()
        mean = gap_stats.mean()
        std = gap_stats.std() if len(gap_stats) > 1 else 0
        series = original input series
        gaps = gaps returned by identify_gaps]
    G --> H[Return stats dict]
    H --> I[End]

## Examples (descriptive, end-to-end):
1) Typical datetime-indexed series:
    - Input: A pandas Series of measurements sampled at timestamps (Series.index is a DatetimeIndex). Some measurements may be missing (NaN).
    - Effect: compute_gap_stats drops NaNs, extracts the original timestamp values (the index) and passes them to identify_gaps with is_datetime=True. The returned dict contains min/max/mean/std of large time deltas between consecutive timestamps and a list of timestamp pairs that bracket each detected large gap.

2) Numeric-indexed sampling (e.g., integer sample positions):
    - Input: A pandas Series where the index is numeric (sample numbers) or the index contains numeric values stored as labels.
    - Effect: compute_gap_stats treats the index values as numeric and uses identify_gaps with is_datetime=False to detect unusually large numeric jumps in the index. Returned statistics and gap pairs reflect numeric differences.

3) Defensive behavior on empty or sparse data:
    - If the input series has no non-NaN rows or fewer than two observations after dropna(), identify_gaps will produce empty gap_stats and gaps -> compute_gap_stats returns min/max/mean as NaN and std as 0, with an empty gaps list.

Notes:
    - The function's type annotation claims it returns a pandas.Series, but the implementation returns a dict with the keys described above. Callers should expect and handle a dict at runtime.

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.pandas_describe_timeseries_1d` · *function*

## Summary:
Combines numeric summarization with time-series-specific diagnostics to produce a consolidated statistics dictionary for a single pandas Series; returns the (possibly normalized) config and series along with the augmented stats.

## Description:
This function is a single-column time-series summarizer that orchestrates multiple analysis steps:
1. Delegates numeric summarization and initial cleaning/normalization to describe_numeric_1d, which returns an updated config, a (possibly transformed) series, and a baseline stats dict.
2. Detects spectral seasonality using seasonality_test(series) and records whether any seasonal components were found.
3. Runs a stationarity decision (Augmented Dickey–Fuller) via stationarity_test(config, series) and records the returned p-value and a boolean decision that treats a series as stationary only if the ADF test indicates stationarity and no seasonality was detected.
4. Computes sampling-gap statistics from the series' index via compute_gap_stats(series) and stores the resulting summary.

Known callers and typical usage context:
- Typical callers are higher-level time-series profiling routines (for example, a module-level describe_timeseries_1d or a dataset-level profiling pipeline) that iterate over DataFrame columns to produce per-variable summaries during dataset profiling.
- Typical trigger: called after loading data and before assembling a report; used for per-column feature inspection in a profiling run.

Why this logic is a separate function:
- Separates orchestration of multiple specialized diagnostics (numeric summary, spectral analysis, stationarity test, gap detection) into one reusable unit so callers can obtain a consolidated stats dict without managing each diagnostic call and the exact keys used in the stats dict. This enforces a consistent output schema for time-series column summaries and centralizes combination logic (e.g., interpreting stationarity jointly with seasonality).

## Args:
    config (Settings):
        - Type: Settings
        - Description: Global configuration object used by subroutines (stationarity_test reads config.vars.timeseries.significance). The function forwards this object to describe_numeric_1d and stationarity_test and returns it (possibly modified) as the first element of the result tuple.
        - Constraints: Must provide the expected attributes used by helper functions (notably config.vars.timeseries.significance for stationarity_test). No in-function validation is performed here.

    series (pandas.Series):
        - Type: pd.Series
        - Description: One-dimensional sequence of observations for the variable being profiled. The index is expected to encode sampling positions (timestamps or numeric positions) for gap analysis.
        - Constraints:
            * Must be convertible to types expected by describe_numeric_1d and seasonality_test (numeric dtype).
            * May contain NaNs; describe_numeric_1d and compute_gap_stats handle nulls in their own ways (see Notes).
        - Interdependencies: The series returned by describe_numeric_1d may be a cleaned or transformed variant of the provided series; this function uses the post-describe_numeric_1d series for all subsequent tests.

    summary (dict):
        - Type: dict
        - Description: Per-call summary metadata passed into describe_numeric_1d. This function forwards it to describe_numeric_1d but does not inspect or modify it directly.

## Returns:
    Tuple[Settings, pandas.Series, dict]
    - The returned tuple contains:
        1) config (Settings): The same config object passed in, possibly modified by describe_numeric_1d.
        2) series (pd.Series): The series returned from describe_numeric_1d (may be cleaned/converted).
        3) stats (dict): A dictionary containing baseline numeric stats augmented with time-series diagnostics. At minimum, the function sets/overwrites the following keys in stats:
            - "seasonal" (bool): result of seasonality_test(series)["seasonality_presence"] — True if any spectral peak(s) indicative of seasonality were detected.
            - "stationary" (bool): True if stationarity_test(config, series) indicated stationarity (p_value < configured threshold) AND no seasonality was detected (i.e., is_stationary and not stats["seasonal"]). This enforces that seasonal series are not treated as stationary even if the ADF test returns a low p-value.
            - "addfuller" (float): the raw p-value returned by stationarity_test (the ADF test p-value).
            - "series" (pd.Series): the (post-describe_numeric_1d) series object used for analysis.
            - "gap_stats" (dict): the dictionary returned by compute_gap_stats(series) containing gap summary keys such as "min", "max", "mean", "std", "series", and "gaps".
        - The function returns the augmented stats dict; it merges or overwrites keys on the stats object provided by describe_numeric_1d.

## Raises:
    - The function does not raise exceptions itself but allows exceptions from helper functions to propagate. Examples:
        * Any exception raised by describe_numeric_1d (e.g., TypeError/ValueError for invalid series inputs).
        * Any exception raised by seasonality_test (e.g., AttributeError/KeyError if its dependencies return unexpected structures).
        * Any exception raised by stationarity_test (e.g., ValueError from statsmodels.adfuller for too-short or invalid input; AttributeError if config.vars.timeseries.significance is missing).
        * Any exception raised by compute_gap_stats or its internal identify_gaps (e.g., TypeError for incompatible index types).
    - Callers should wrap the invocation if they need to handle or recover from these error conditions (for example, returning fallback stats on failure).

## Constraints:
    Preconditions:
    - The input series should be a pandas.Series whose values are numeric or convertible to numeric types; helper functions expect numeric data.
    - config must contain the attributes used by downstream helpers (notably config.vars.timeseries.significance).
    - describe_numeric_1d is expected to accept the provided summary dict and return a triple (config, series, stats). The caller must rely on that contract.

    Postconditions:
    - The returned stats dict will contain at least the keys "seasonal", "stationary", "addfuller", "series", and "gap_stats".
    - The "series" entry in stats references the series object returned by describe_numeric_1d and is the same object returned as the second element of the function's return tuple.
    - No global state or external resources are modified by this function itself; any mutations originate in helper functions if they mutate their inputs.

## Side Effects:
    - No direct I/O (file, network, stdout) is performed by this function.
    - The function does not mutate global variables.
    - It may return (and thereby expose) a series object that was modified by describe_numeric_1d; any in-place mutations performed by describe_numeric_1d will be visible to callers.
    - External library code is invoked (statsmodels.adfuller indirectly via stationarity_test, FFT/peak routines indirectly via seasonality_test). Any side effects of those libraries (if any) are external to this function.

## Control Flow:
flowchart TD
    Start([Start]) --> A[Call describe_numeric_1d(config, series, summary)]
    A --> B{Did describe_numeric_1d return (config, series, stats) successfully?}
    B -- No --> Error[Propagate exception to caller]
    B -- Yes --> C[Call seasonality_test(series) -> seasonality_dict]
    C --> D[Set stats["seasonal"] = seasonality_dict["seasonality_presence"]]
    D --> E[Call stationarity_test(config, series) -> (is_stationary, p_value)]
    E --> F[Set stats["addfuller"] = p_value]
    F --> G[Set stats["stationary"] = is_stationary AND (not stats["seasonal"])]
    G --> H[Call compute_gap_stats(series) -> gap_stats_dict]
    H --> I[Set stats["gap_stats"] = gap_stats_dict]
    I --> J[Set stats["series"] = series]
    J --> End([Return (config, series, stats)])

## Examples:
1) Typical successful usage (illustrative, omit real code here):
    - Context: Profiling loop over DataFrame columns. For numeric time-series column "x", call this function to obtain per-column statistics used in a profiling report.
    - Outcome: The returned stats dict contains numeric summary fields (from describe_numeric_1d) plus:
        * "seasonal": True/False depending on spectral peaks
        * "stationary": True if ADF p-value < configured threshold and no seasonality
        * "addfuller": numeric p-value from the ADF test
        * "gap_stats": dict summarizing large sampling gaps detected in the series' index

2) Defensive calling pattern (recommended):
    - Before calling, verify that the series has a sufficient number of non-missing numeric observations to avoid adfuller errors: e.g., if series.dropna().size < required_min, skip stationarity_check or wrap call in try/except.
    - Example handling semantics:
        * If a stationarity_test raises (e.g., due to too few observations), catch the exception and set stats["stationary"] = False and stats["addfuller"] = float("nan") before proceeding to other diagnostics.

Notes and implementation remarks for reimplementation:
- The function assumes the contract of helper functions:
    * describe_numeric_1d(config, series, summary) -> Tuple[Settings, pd.Series, dict]
    * seasonality_test(series) -> dict containing "seasonality_presence"
    * stationarity_test(config, series) -> Tuple[bool, float]
    * compute_gap_stats(series) -> dict
- The "stationary" post-processing intentionally classifies seasonal series as non-stationary regardless of the ADF p-value to avoid mislabeling seasonally driven processes as stationary.
- Any reimplementation should preserve the key names in stats exactly as listed above to remain compatible with downstream report-generation code.

