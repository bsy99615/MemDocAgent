# `src.ydata_profiling.model.pandas`

## Tree:
    - pandas/
      - correlations_pandas.py
      - dataframe_pandas.py
      - describe_boolean_pandas.py
      - describe_categorical_pandas.py
      - describe_counts_pandas.py
      - describe_date_pandas.py
      - describe_file_pandas.py
      - describe_generic_pandas.py
      - describe_image_pandas.py
      - describe_numeric_pandas.py
      - describe_path_pandas.py
      - describe_supported_pandas.py
      - describe_text_pandas.py
      - describe_timeseries_pandas.py
      - describe_url_pandas.py
      - discretize_pandas.py
      - duplicates_pandas.py
      - imbalance_pandas.py
      - missing_pandas.py
      - sample_pandas.py
      - summary_pandas.py
      - table_pandas.py
      - timeseries_index_pandas.py
      - utils_pandas.py

## Role:
    Provides pandas-specific implementations for data profiling operations, including descriptive statistics, data type handling, and specialized analysis functions for various data types.

## Description:
This module contains all pandas-specific implementations for data profiling operations. It provides concrete implementations of abstract profiling interfaces that operate directly on pandas DataFrames and Series, handling the low-level mechanics of data analysis, statistical computation, and data type detection for the ydata-profiling library.

The module is organized around specific data types and analysis domains:
- Core descriptive statistics for different data types (numeric, categorical, text, etc.)
- Specialized analysis functions for specific data categories (images, paths, URLs, time series)
- Utility functions for data manipulation and transformation
- Infrastructure for data sampling, missing value analysis, and duplicate detection

Primary consumers include the main profiling pipeline components that require pandas-specific implementations for data processing and statistical analysis.

## Components:
    - Correlations: Implements correlation analysis between pandas Series
    - Dataframe: Handles DataFrame-level profiling operations
    - Boolean: Describes boolean data types
    - Categorical: Describes categorical data types
    - Counts: Describes count data types
    - Date: Describes date/time data types
    - File: Describes file data types
    - Generic: Generic data type descriptions
    - Image: Describes image data types with metadata extraction
    - Numeric: Describes numeric data types with statistical measures
    - Path: Describes file path data types
    - Supported: Describes supported data types with value counts
    - Text: Describes text data types with character and word analysis
    - Timeseries: Describes time series data with seasonal and stationarity analysis
    - URL: Describes URL data types with component analysis
    - Discretize: Provides discretization utilities for numerical data
    - Duplicates: Identifies and analyzes duplicate rows in DataFrames
    - Imbalance: Calculates imbalance scores for categorical data
    - Missing: Provides missing value analysis and visualization
    - Sample: Retrieves samples from DataFrames for reporting
    - Summary: Computes comprehensive summaries of Series data
    - Table: Computes table-level statistics from variable summaries
    - TimeseriesIndex: Extracts time index characteristics
    - Utils: Utility functions for data processing and statistical operations

## Public API:
    - Correlations: `pandas_correlations_1d`
    - Dataframe: `pandas_describe_dataframe`
    - Boolean: `pandas_describe_boolean_1d`
    - Categorical: `pandas_describe_categorical_1d`
    - Counts: `pandas_describe_counts_1d`
    - Date: `pandas_describe_date_1d`
    - File: `pandas_describe_file_1d`
    - Generic: `pandas_describe_generic_1d`
    - Image: `pandas_describe_image_1d`
    - Numeric: `pandas_describe_numeric_1d`
    - Path: `pandas_describe_path_1d`
    - Supported: `pandas_describe_supported`
    - Text: `pandas_describe_text_1d`
    - Timeseries: `pandas_describe_timeseries_1d`
    - URL: `pandas_describe_url_1d`
    - Discretize: `Discretizer` class with `discretize_dataframe` method
    - Duplicates: `pandas_get_duplicates`
    - Imbalance: `column_imbalance_score`
    - Missing: `pandas_missing_bar`, `pandas_missing_heatmap`, `pandas_missing_matrix`
    - Sample: `pandas_get_sample`
    - Summary: `pandas_describe_1d`, `pandas_get_series_descriptions`
    - Table: `pandas_get_table_stats`
    - TimeseriesIndex: `pandas_get_time_index_description`
    - Utils: `weighted_median`

## Dependencies:
    - Internal: `src.ydata_profiling.config`, `src.ydata_profiling.model.base`, `src.ydata_profiling.model.typeset`
    - External: `pandas`, `numpy`, `matplotlib`, `scipy`, `PIL`, `imagehash`, `urllib.parse`, `os`, `tqdm`

## Constraints:
    - All functions must accept and return pandas objects consistently
    - Functions should handle edge cases gracefully without raising exceptions
    - Thread-safety: Functions should be stateless or use thread-local storage
    - Memory usage should be optimized for large datasets
    - All data transformations should preserve DataFrame structure and column order

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

