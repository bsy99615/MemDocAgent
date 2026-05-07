# `describe_timeseries_pandas.py`

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.stationarity_test` · *function*

## Summary:
Performs an Augmented Dickey-Fuller unit root test to determine if a time series is stationary.

## Description:
This function applies the Augmented Dickey-Fuller (ADF) test to assess the stationarity of a time series. It drops any null values from the series before testing and returns both a boolean indicating stationarity status and the test's p-value. The test compares the computed p-value against a significance threshold configured in the settings to make the stationarity determination.

## Args:
    config (Settings): Configuration object containing the significance threshold for the stationarity test via `config.vars.timeseries.significance`.
    series (pd.Series): A pandas Series representing the time series data to test for stationarity.

## Returns:
    Tuple[bool, float]: A tuple where the first element is a boolean indicating whether the series is stationary (True if p-value < significance threshold), and the second element is the p-value from the ADF test.

## Raises:
    None explicitly raised by this function, though the underlying `adfuller` function may raise exceptions for invalid inputs.

## Constraints:
    Preconditions:
        - The `series` parameter must be a valid pandas Series.
        - The `config` parameter must contain a properly initialized `vars.timeseries.significance` attribute.
    Postconditions:
        - The returned boolean accurately reflects whether the p-value is less than the significance threshold.
        - The returned p-value is a float between 0 and 1.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start stationarity_test] --> B{config.vars.timeseries.significance}
    B --> C[Drop NaN values from series]
    C --> D[Perform ADF test]
    D --> E[Extract p-value]
    E --> F[p_value < significance_threshold?]
    F -->|Yes| G[Return (True, p_value)]
    F -->|No| H[Return (False, p_value)]
```

## Examples:
    # Assuming config has significance set to 0.05
    result = stationarity_test(config, pd.Series([1, 2, 3, 4, 5]))
    is_stationary, p_val = result
    print(f"Is stationary: {is_stationary}, P-value: {p_val}")

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.fftfreq` · *function*

## Summary:
Computes the discrete Fourier transform frequency bins for a given signal length and sample spacing.

## Description:
This function calculates the frequency bins associated with the discrete Fourier transform (DFT) of a signal. It is used in time series analysis to determine the frequencies corresponding to the DFT coefficients. The function implements the equivalent of scipy.fftpack.fftfreq but with a custom implementation for performance reasons.

## Args:
    n (int): The length of the FFT (number of samples in the signal). Must be a positive integer.
    d (float): The sample spacing (inverse of the sampling rate). Defaults to 1.0. Must be a positive float.

## Returns:
    np.ndarray: An array of frequency bin values corresponding to the DFT coefficients. The array has the same length as n and contains positive and negative frequencies arranged appropriately for the FFT.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - n must be a positive integer
        - d must be a positive float
    
    Postconditions:
        - The returned array has length n
        - The frequency bins are properly ordered for FFT processing

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start fftfreq(n, d)] --> B[val = 1.0 / (n * d)]
    B --> C[N = (n - 1) // 2 + 1]
    C --> D[results = np.empty(n, int)]
    D --> E[p1 = np.arange(0, N, dtype=int)]
    E --> F[results[:N] = p1]
    F --> G[p2 = np.arange(-(n // 2), 0, dtype=int)]
    G --> H[results[N:] = p2]
    H --> I[return results * val]
```

## Examples:
    >>> fftfreq(4, 0.5)
    array([ 0.   ,  0.5  , -0.5  , -0.   ])
    
    >>> fftfreq(5, 1.0)
    array([ 0.   ,  0.25 ,  0.5  , -0.5  , -0.25])
```

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.seasonality_test` · *function*

## Summary:
Determines the presence of seasonal patterns in a time series by analyzing frequency components from FFT analysis and identifies dominant seasonal periods.

## Description:
Analyzes a time series to detect seasonal patterns by performing Fast Fourier Transform (FFT) and identifying significant frequency peaks. This function is part of the time series profiling pipeline and helps identify recurring patterns in temporal data. It is typically called during automated time series analysis to characterize the periodic nature of the data.

## Args:
    series (pd.Series): Input time series data to analyze for seasonality. Must contain numeric values.
    mad_threshold (float): Multiplier for median absolute deviation (MAD) based threshold calculation for peak detection. Defaults to 6.0. Must be non-negative.

## Returns:
    dict: A dictionary containing:
        - 'seasonality_presence' (bool): True if significant seasonal patterns are detected, False otherwise
        - 'seasonalities' (list): List of identified seasonal periods (inverted frequencies) if seasonality is present, empty list otherwise

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input series must be a valid pandas Series with numeric data
        - Series should not contain NaN values (assumed to be handled upstream)
        - mad_threshold must be a non-negative float
    
    Postconditions:
        - Function always returns a dictionary with the specified keys
        - Seasonal periods are returned as inverted frequencies (period = 1/frequency)

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start seasonality_test] --> B[Call get_fft(series)]
    B --> C[Call get_fft_peaks(fft, mad_threshold)]
    C --> D[Check if peaks exist (len(peaks.index) > 0)]
    D -->|True| E[Transform peaks["freq"] to seasonal periods using 1/x]
    E --> F[Return result with seasonality_presence=True and seasonalities]
    D -->|False| G[Return result with seasonality_presence=False and empty seasonalities]
```

## Examples:
    # Basic usage
    result = seasonality_test(time_series_data)
    if result["seasonality_presence"]:
        print(f"Detected seasonal periods: {result['seasonalities']}")
    else:
        print("No significant seasonality detected")
        
    # Custom MAD threshold
    result = seasonality_test(time_series_data, mad_threshold=8.0)
    print(f"Seasonality presence: {result['seasonality_presence']}")
```

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.get_fft` · *function*

## Summary:
Computes the Fast Fourier Transform (FFT) of a time series and returns frequency-domain representation with amplitude values.

## Description:
This function performs a Fast Fourier Transform on a time series to convert it from the time domain to the frequency domain. It extracts the positive frequency components and their corresponding amplitudes in decibels, making it suitable for spectral analysis of time series data. The function is typically called as part of time series profiling operations to analyze the frequency characteristics of the data.

## Args:
    series (pd.Series): Input time series data to transform. Must contain numeric values.

## Returns:
    pd.DataFrame: A DataFrame containing two columns:
        - 'freq': Positive frequency values (float64)
        - 'ampl': Amplitude values in decibels (float64)

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input series must be a valid pandas Series with numeric data
        - Series should not contain NaN values (assumed to be handled upstream)
    
    Postconditions:
        - Output DataFrame always contains positive frequency values
        - Amplitude values are in decibel scale (10 * log10 of power spectral density)
        - Output DataFrame has the same number of rows as the number of positive frequency components

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start get_fft(series)] --> B[Convert series to numpy array]
    B --> C[Compute FFT using _pocketfft.fft]
    C --> D[Calculate power spectral density as |FFT|²]
    D --> E[Compute frequency bins using fftfreq(len(data_psd), 1.0)]
    E --> F[Filter positive frequencies (fftfreq_ > 0)]
    F --> G[Transform amplitudes to decibels: 10 * log₁₀(power)]
    G --> H[Return DataFrame with freq and ampl columns]
```

## Examples:
    >>> import pandas as pd
    >>> series = pd.Series([1, 2, 3, 4, 5])
    >>> result = get_fft(series)
    >>> print(result)
       freq  ampl
    0  0.0   ...
    1  0.2   ...
    2  0.4   ...
```

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.get_fft_peaks` · *function*

## Summary:
Identifies and filters significant frequency peaks from FFT amplitude data using statistical thresholds and frequency clustering.

## Description:
Processes Fast Fourier Transform (FFT) results to detect meaningful frequency components by applying median absolute deviation (MAD) based filtering and removing closely spaced peaks. This function serves as a preprocessing step for time series analysis to extract dominant frequencies while eliminating noise-induced false positives.

## Args:
    fft (pd.DataFrame): DataFrame containing FFT results with columns 'ampl' (amplitude) and 'freq' (frequency)
    mad_threshold (float): Multiplier for MAD-based threshold calculation. Defaults to 6.0. Must be non-negative.

## Returns:
    Tuple[float, pd.DataFrame, pd.DataFrame]: A tuple containing:
        - threshold (float): The calculated amplitude threshold used for peak filtering
        - orig_peaks (pd.DataFrame): All detected peaks before applying the amplitude threshold
        - peaks (pd.DataFrame): Filtered peaks that exceed the threshold and are not clustered

## Raises:
    None explicitly raised

## Constraints:
    - Preconditions: Input fft DataFrame must contain 'ampl' and 'freq' columns with numeric data
    - Postconditions: Returned DataFrames maintain the original column structure but may have different row counts
    - The function assumes that fft['ampl'] contains non-negative values after filtering

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_fft_peaks] --> B[pos_fft = fft.loc[fft["ampl"] > 0]]
    B --> C[median = pos_fft["ampl"].median()]
    C --> D[pos_fft_above_med = pos_fft[pos_fft["ampl"] > median]]
    D --> E[mad = abs(pos_fft_above_med["ampl"] - pos_fft_above_med["ampl"].mean()).mean()]
    E --> F[threshold = median + mad * mad_threshold]
    F --> G[peak_indices = find_peaks(fft["ampl"], threshold=0.1)]
    G --> H[peaks = fft.loc[peak_indices[0], :]]
    H --> I[orig_peaks = peaks.copy()]
    I --> J[peaks = peaks.loc[peaks["ampl"] > threshold].copy()]
    J --> K[peaks["Remove"] = [False] * len(peaks.index)]
    K --> L[peaks.reset_index(inplace=True)]
    L --> M{Loop over peaks}
    M --> N[Current peak index]
    N --> O[Inner loop over remaining peaks]
    O --> P{Check frequency ratio}
    P --> Q[fraction = (peaks.loc[idx2, "freq"] / curr) % 1]
    Q --> R{fraction < 0.01 OR fraction > 0.99}
    R --> S[Set Remove=True]
    S --> T[Continue to next peak]
    T --> U{End inner loop}
    U --> V{End outer loop}
    V --> W[Filter out removed peaks]
    W --> X[Drop Remove column]
    X --> Y[Return threshold, orig_peaks, peaks]
```

## Examples:
    # Basic usage with default parameters
    threshold, orig_peaks, filtered_peaks = get_fft_peaks(fft_data)
    
    # Usage with custom MAD threshold
    threshold, orig_peaks, filtered_peaks = get_fft_peaks(fft_data, mad_threshold=8.0)
    
    # Handling edge case where no peaks are found
    try:
        threshold, orig_peaks, filtered_peaks = get_fft_peaks(fft_data)
        if len(filtered_peaks) == 0:
            print("No significant peaks found")
    except Exception as e:
        print(f"Error processing FFT peaks: {e}")
        
    # Processing time series data for frequency analysis
    import pandas as pd
    from scipy.signal import find_peaks
    
    # Sample FFT data
    fft_data = pd.DataFrame({
        'freq': [1.0, 2.0, 3.0, 4.0, 5.0],
        'ampl': [0.1, 5.2, 0.3, 8.7, 0.2]
    })
    
    threshold, orig_peaks, filtered_peaks = get_fft_peaks(fft_data)
    print(f"Threshold: {threshold}")
    print(f"Original peaks count: {len(orig_peaks)}")
    print(f"Filtered peaks count: {len(filtered_peaks)}")

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.identify_gaps` · *function*

## Summary:
Detects and characterizes gaps in time series data by analyzing differences between consecutive values.

## Description:
Analyzes a pandas Series to identify gaps or discontinuities in time series data. The function computes differences between consecutive elements, determines a minimum gap size based on a tolerance factor, and returns both statistical information about significant gaps and the actual gap values. This is particularly useful for time series profiling to understand data irregularities and missing values patterns.

The function handles both datetime and numeric time series data through the is_datetime flag, making it versatile for different data types. It's typically called during time series profiling operations to characterize data gaps and irregularities.

## Args:
    gap (pandas.Series): A pandas Series containing time series data points, typically sorted chronologically
    is_datetime (bool): Flag indicating whether the data represents datetime values (True) or numeric values (False)
    gap_tolerance (int, optional): Multiplier to determine minimum significant gap size. Defaults to 2. Higher values require larger gaps to be considered significant.

## Returns:
    Tuple[pandas.Series, list]: A tuple containing:
        - gap_stats: A pandas Series with the actual gap sizes (differences) that exceed the minimum threshold
        - gaps: A list of arrays, each containing two consecutive values that define a detected gap (the value before and after the gap)

## Raises:
    None explicitly raised

## Constraints:
    - Preconditions: The input gap Series must be properly ordered and contain valid data points
    - Postconditions: The returned gap_stats Series will contain only gaps larger than the calculated threshold (gap_tolerance * average gap size)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start identify_gaps] --> B{is_datetime?}
    B -->|True| C[zero = pd.Timedelta(0)]
    B -->|False| D[zero = 0]
    C --> E[diff = gap.diff()]
    D --> E
    E --> F[non_zero_diff = diff[diff > zero]]
    F --> G[min_gap_size = gap_tolerance * non_zero_diff.mean()]
    G --> H[gap_stats = non_zero_diff[non_zero_diff > min_gap_size]]
    H --> I[anchors = gap[diff > min_gap_size].index]
    I --> J{For each anchor index}
    J --> K[gaps.append(gap.loc[gap.index[[i-1, i]]].values)]
    K --> L[Return gap_stats, gaps]
```

## Examples:
```python
import pandas as pd
from src.ydata_profiling.model.pandas.describe_timeseries_pandas import identify_gaps

# Example with datetime data
dates = pd.date_range('2020-01-01', periods=5, freq='D')
dates = dates.drop(dates[2])  # Create a gap by removing middle date
gap_series = pd.Series(dates)
gap_stats, gaps = identify_gaps(gap_series, is_datetime=True, gap_tolerance=2)

# Example with numeric data
numeric_data = pd.Series([1, 2, 3, 5, 6, 10, 11])
gap_stats, gaps = identify_gaps(numeric_data, is_datetime=False, gap_tolerance=1)
```

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.compute_gap_stats` · *function*

## Summary:
Computes statistical measures and gap information for time series data by analyzing the differences between consecutive values in the series index.

## Description:
Processes a pandas Series representing time series data to calculate gap statistics including minimum, maximum, mean, and standard deviation of gaps between consecutive observations. This function extracts gap information from the series index, handles both datetime and numeric time series, and identifies significant gaps in the data pattern. The function is typically called during time series profiling to characterize data irregularities and missing value patterns.

This logic is extracted into its own function to separate the gap analysis computation from the broader time series description logic, enforcing a clean responsibility boundary between data preprocessing and statistical analysis.

## Args:
    series (pd.Series): A pandas Series containing time series data with potentially irregular spacing in its index

## Returns:
    dict: A dictionary containing:
        - "min": Minimum gap size (float)
        - "max": Maximum gap size (float)
        - "mean": Mean gap size (float)
        - "std": Standard deviation of gap sizes (float, 0 if fewer than 2 gaps)
        - "series": Original input series
        - "gaps": List of arrays defining detected gaps (list of arrays)

## Raises:
    None explicitly raised

## Constraints:
    - Preconditions: Input series should be a valid pandas Series with an index that can be analyzed for gaps
    - Postconditions: The returned dictionary contains all requested statistical measures and gap information

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start compute_gap_stats] --> B[Drop NaN values from series]
    B --> C[Extract index name or default to "index"]
    C --> D[Reset index and extract index values]
    D --> E[Check if index is DatetimeIndex]
    E --> F[Call identify_gaps with gap data and datetime flag]
    F --> G[Calculate min, max, mean, std from gap_stats]
    G --> H[Construct result dictionary with all statistics]
    H --> I[Return stats dictionary]
```

## Examples:
```python
import pandas as pd
from src.ydata_profiling.model.pandas.describe_timeseries_pandas import compute_gap_stats

# Example with datetime data
dates = pd.date_range('2020-01-01', periods=5, freq='D')
dates = dates.drop(dates[2])  # Create a gap by removing middle date
series = pd.Series([10, 20, 30, 40, 50], index=dates)
result = compute_gap_stats(series)

# Example with numeric data
numeric_series = pd.Series([1, 2, 3, 5, 6, 10, 11], index=[1, 2, 3, 4, 5, 6, 7])
result = compute_gap_stats(numeric_series)
```

## `src.ydata_profiling.model.pandas.describe_timeseries_pandas.pandas_describe_timeseries_1d` · *function*

## Summary:
Performs comprehensive time series analysis on a single pandas Series by extending numeric statistics with seasonal pattern detection, stationarity testing, and gap analysis.

## Description:
This function serves as the primary entry point for time series profiling in the pandas backend. It builds upon basic numeric statistics to provide specialized time series insights including seasonality detection, stationarity assessment, and gap characterization. The function is typically invoked during automated profiling workflows when processing time series data, particularly when the configuration indicates the series should be treated as a time series.

The logic is extracted into its own function to maintain clear separation between general numeric data analysis and time series-specific analytical operations, ensuring that time series profiling remains modular and extensible.

## Args:
    config (Settings): Configuration object containing profiling settings including time series significance thresholds
    series (pd.Series): Input time series data to analyze
    summary (dict): Dictionary containing existing summary statistics for the series

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing:
        - Updated configuration object
        - The processed series (potentially cleaned of nulls)
        - Extended statistics dictionary with time series specific metrics including:
          * "seasonal" (bool): Whether seasonal patterns are detected
          * "stationary" (bool): Whether the series is stationary (considering seasonality)
          * "addfuller" (float): Augmented Dickey-Fuller test p-value
          * "series" (pd.Series): The input series
          * "gap_stats" (dict): Gap analysis results

## Raises:
    None explicitly raised by this function, though underlying functions may raise exceptions for invalid inputs.

## Constraints:
    Preconditions:
        - Input series must be a valid pandas Series
        - Config must contain properly initialized time series settings
        - Summary dictionary should be a valid mutable mapping
    
    Postconditions:
        - The returned statistics dictionary includes all time series specific metrics
        - The series is processed through null handling (though exact behavior depends on describe_numeric_1d)

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_describe_timeseries_1d] --> B[Call describe_numeric_1d]
    B --> C[Extract stats from describe_numeric_1d result]
    C --> D[Call seasonality_test(series)]
    D --> E[Store seasonality result in stats["seasonal"]]
    E --> F[Call stationarity_test(config, series)]
    F --> G[Calculate stationary = is_stationary AND NOT stats["seasonal"]]
    G --> H[Store p_value in stats["addfuller"]]
    H --> I[Store series in stats["series"]]
    I --> J[Call compute_gap_stats(series)]
    J --> K[Store gap_stats in stats["gap_stats"]]
    K --> L[Return (config, series, stats)]
```

## Examples:
    # Basic usage in time series profiling
    from ydata_profiling.config import Settings
    import pandas as pd
    
    config = Settings()
    series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    summary = {}
    
    updated_config, processed_series, extended_stats = pandas_describe_timeseries_1d(config, series, summary)
    
    # Access time series specific metrics
    print(f"Seasonal: {extended_stats['seasonal']}")
    print(f"Stationary: {extended_stats['stationary']}")
    print(f"ADF p-value: {extended_stats['addfuller']}")
    print(f"Gap stats: {extended_stats['gap_stats']}")
```

