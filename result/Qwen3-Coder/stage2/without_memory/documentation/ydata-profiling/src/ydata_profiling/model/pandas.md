# `src.ydata_profiling.model.pandas`

## Tree:
pandas/
├── correlations_pandas.py
├── dataframe_pandas.py
├── describe_boolean_pandas.py
├── describe_categorical_pandas.py
├── describe_counts_pandas.py
├── describe_date_pandas.py
├── describe_file_pandas.py
├── describe_generic_pandas.py
├── describe_image_pandas.py
├── describe_numeric_pandas.py
├── describe_path_pandas.py
├── describe_supported_pandas.py
├── describe_text_pandas.py
├── describe_timeseries_pandas.py
├── describe_url_pandas.py
├── discretize_pandas.py
├── duplicates_pandas.py
├── imbalance_pandas.py
├── missing_pandas.py
├── sample_pandas.py
├── summary_pandas.py
├── table_pandas.py
├── timeseries_index_pandas.py
└── utils_pandas.py

## Role:
Provides pandas-specific implementations for data profiling operations.

## Description:
This module contains all pandas-specific implementations for data profiling functionality. It serves as the core backend for analyzing pandas DataFrames and Series, providing detailed statistical summaries, correlation matrices, missing data visualizations, and specialized processing for different data types like text, images, URLs, and time series.

The module is consumed by the main profiling pipeline and provides the low-level implementations that handle pandas-specific operations such as DataFrame preprocessing, type detection, and statistical computations.

## Components:
- Discretizer: Class for discretizing numerical data into bins for correlation analysis
- Correlation functions: Multiple implementations for computing different types of correlations (Pearson, Spearman, Cramér's V, Phi-K, Kendall)
- Dataframe processors: Functions for checking and preprocessing DataFrames
- Descriptive statistics: Specialized functions for describing different data types (boolean, categorical, numeric, text, etc.)
- Missing data handlers: Functions for visualizing and analyzing missing data patterns
- Duplicate detection: Functions for identifying duplicate rows in DataFrames
- Imbalance scoring: Functions for measuring class imbalance in categorical data
- Sampling utilities: Functions for retrieving sample data from DataFrames
- Table statistics: Functions for computing overall table-level statistics
- Time series utilities: Functions for analyzing time series data properties

## Public API:
- pandas_auto_compute(config, df, summary) - Computes auto-correlations using appropriate methods
- pandas_cramers_compute(config, df, summary) - Computes Cramér's V correlation matrix
- pandas_kendall_compute(config, df, summary) - Computes Kendall correlation matrix
- pandas_pearson_compute(config, df, summary) - Computes Pearson correlation matrix
- pandas_phik_compute(config, df, summary) - Computes Phi-K correlation matrix
- pandas_spearman_compute(config, df, summary) - Computes Spearman correlation matrix
- pandas_check_dataframe(df) - Validates DataFrame type
- pandas_preprocess(config, df) - Preprocesses DataFrame for analysis
- pandas_describe_boolean_1d(config, series, summary) - Describes boolean data
- pandas_describe_categorical_1d(config, series, summary) - Describes categorical data
- pandas_describe_counts(config, series, summary) - Computes value counts for series
- pandas_describe_date_1d(config, series, summary) - Describes date/time data
- pandas_describe_file_1d(config, series, summary) - Describes file paths
- pandas_describe_generic(config, series, summary) - Generic series description
- pandas_describe_image_1d(config, series, summary) - Describes image paths
- pandas_describe_numeric_1d(config, series, summary) - Describes numeric data
- pandas_describe_path_1d(config, series, summary) - Describes file paths
- pandas_describe_supported(config, series, series_description) - Describes supported data types
- pandas_describe_text_1d(config, series, summary) - Describes text data
- pandas_describe_timeseries_1d(config, series, summary) - Describes time series data
- pandas_describe_url_1d(config, series, summary) - Describes URL data
- pandas_get_duplicates(config, df, supported_columns) - Finds duplicate rows
- pandas_missing_bar(config, df) - Creates bar chart of missing data
- pandas_missing_heatmap(config, df) - Creates heatmap of missing data patterns
- pandas_missing_matrix(config, df) - Creates matrix visualization of missing data
- pandas_get_sample(config, df) - Retrieves sample data from DataFrame
- pandas_describe_1d(config, series, summarizer, typeset) - Main 1D description function
- pandas_get_series_descriptions(config, df, summarizer, typeset, pbar) - Computes descriptions for all series
- pandas_get_table_stats(config, df, variable_stats) - Computes table-level statistics
- pandas_get_time_index_description(config, df, table_stats) - Gets time index description
- weighted_median(data, weights) - Computes weighted median

## Dependencies:
Internal: src.ydata_profiling.config.Settings, src.ydata_profiling.model.base.BaseSummarizer, src.ydata_profiling.typeset.ProfilingTypeSet, src.ydata_profiling.typeset.VisionsTypeset
External: pandas, numpy, scipy.stats, matplotlib.pyplot, seaborn, tqdm, multiprocessing, warnings, itertools, os, datetime, string, contextlib, collections.Counter, PIL.Image, PIL.ExifTags, imagehash, scipy.signal, statsmodels.tsa.stattools.adfuller, scipy.optimize, scipy.spatial.distance, scipy.cluster.hierarchy, scipy.cluster.vq, scipy.ndimage, scipy.interpolate, scipy.special, scipy.linalg, scipy.sparse, scipy.io, scipy.misc, scipy.fft, scipy.signal.windows, scipy.signal.spectral, scipy.signal.filter_design, scipy.signal.wavelets, scipy.signal.cwt, scipy.signal.filtfilt, scipy.signal.lfilter, scipy.signal.savgol_filter, scipy.signal.resample, scipy.signal.decimate, scipy.signal.upfirdn, scipy.signal.convolve, scipy.signal.correlate, scipy.signal.fftconvolve, scipy.signal.oaconvolve, scipy.signal.bilinear, scipy.signal.butter, scipy.signal.cheby1, scipy.signal.cheby2, scipy.signal.ellip, scipy.signal.bessel, scipy.signal.firwin, scipy.signal.firwin2, scipy.signal.remez, scipy.signal.sosfilt, scipy.signal.sosfiltfilt, scipy.signal.sosfreqz, scipy.signal.sosfilt_zi, scipy.signal.sosfiltfilt_zi

---

## Files

- [`correlations_pandas.py`](pandas/correlations_pandas.md)
- [`dataframe_pandas.py`](pandas/dataframe_pandas.md)
- [`describe_boolean_pandas.py`](pandas/describe_boolean_pandas.md)
- [`describe_categorical_pandas.py`](pandas/describe_categorical_pandas.md)
- [`describe_counts_pandas.py`](pandas/describe_counts_pandas.md)
- [`describe_date_pandas.py`](pandas/describe_date_pandas.md)
- [`describe_file_pandas.py`](pandas/describe_file_pandas.md)
- [`describe_generic_pandas.py`](pandas/describe_generic_pandas.md)
- [`describe_image_pandas.py`](pandas/describe_image_pandas.md)
- [`describe_numeric_pandas.py`](pandas/describe_numeric_pandas.md)
- [`describe_path_pandas.py`](pandas/describe_path_pandas.md)
- [`describe_supported_pandas.py`](pandas/describe_supported_pandas.md)
- [`describe_text_pandas.py`](pandas/describe_text_pandas.md)
- [`describe_timeseries_pandas.py`](pandas/describe_timeseries_pandas.md)
- [`describe_url_pandas.py`](pandas/describe_url_pandas.md)
- [`discretize_pandas.py`](pandas/discretize_pandas.md)
- [`duplicates_pandas.py`](pandas/duplicates_pandas.md)
- [`imbalance_pandas.py`](pandas/imbalance_pandas.md)
- [`missing_pandas.py`](pandas/missing_pandas.md)
- [`sample_pandas.py`](pandas/sample_pandas.md)
- [`summary_pandas.py`](pandas/summary_pandas.md)
- [`table_pandas.py`](pandas/table_pandas.md)
- [`timeseries_index_pandas.py`](pandas/timeseries_index_pandas.md)
- [`utils_pandas.py`](pandas/utils_pandas.md)

