# `src.ydata_profiling.model.spark`

## Tree:
spark/
├── correlations_spark.py
├── dataframe_spark.py
├── describe_boolean_spark.py
├── describe_categorical_spark.py
├── describe_counts_spark.py
├── describe_date_spark.py
├── describe_generic_spark.py
├── describe_numeric_spark.py
├── describe_supported_spark.py
├── describe_text_spark.py
├── duplicates_spark.py
├── missing_spark.py
├── sample_spark.py
├── summary_spark.py
├── table_spark.py
└── timeseries_index_spark.py

## Role:
Handles Spark-specific data profiling operations and computations for distributed DataFrame analysis.

## Description:
The spark module provides a comprehensive set of functions and classes specifically designed for analyzing PySpark DataFrames within the ydata-profiling framework. This module bridges the gap between traditional pandas-based profiling and distributed Spark computing by implementing equivalent functionality for Spark DataFrames while leveraging Spark's distributed processing capabilities.

The module is organized around the core profiling tasks: data type detection, descriptive statistics computation, missing data analysis, duplicate detection, correlation analysis, and sample generation. Each component is designed to work seamlessly with Spark's distributed architecture while maintaining compatibility with the broader profiling framework.

## Components:
*   **correlations_spark**: Implements correlation computation functions (Pearson, Spearman, Kendall, Cramér's V, Phi-K) for Spark DataFrames
*   **dataframe_spark**: Provides DataFrame validation and preprocessing utilities for Spark environments
*   **describe_boolean_spark**: Specialized handlers for boolean data type profiling in Spark
*   **describe_categorical_spark**: Handles categorical data profiling with Spark-specific optimizations
*   **describe_counts_spark**: Computes value counts and missing value statistics for Spark DataFrames
*   **describe_date_spark**: Processes date/time data for profiling in Spark environments
*   **describe_generic_spark**: Computes basic descriptive statistics for Spark DataFrames
*   **describe_numeric_spark**: Implements comprehensive numeric variable profiling for Spark
*   **describe_supported_spark**: Adds distinct value and uniqueness statistics to Spark DataFrame summaries
*   **describe_text_spark**: Manages text variable profiling with Spark-specific considerations
*   **duplicates_spark**: Detects and quantifies duplicate records in Spark DataFrames
*   **missing_spark**: Provides missing data analysis and visualization capabilities for Spark DataFrames
*   **sample_spark**: Generates sample data from Spark DataFrames with appropriate Spark handling
*   **summary_spark**: Coordinates the overall profiling process for Spark DataFrames
*   **table_spark**: Computes table-level statistics for Spark DataFrames
*   **timeseries_index_spark**: Placeholder for time series index analysis in Spark environments

## Public API:
*   **spark_check_dataframe(config, df)**: Validates that input is a PySpark DataFrame
*   **spark_preprocess(config, df)**: Filters out MapType columns from Spark DataFrames
*   **spark_get_duplicates(config, df, supported_columns)**: Identifies duplicate records in Spark DataFrames
*   **spark_get_sample(config, df)**: Creates head samples from Spark DataFrames
*   **spark_get_table_stats(config, df, variable_stats)**: Computes comprehensive table statistics for Spark DataFrames
*   **spark_get_time_index_description(config, df, table_stats)**: Placeholder for time index description extraction
*   **spark_describe_1d(config, series, summarizer, typeset)**: Processes Spark DataFrame series for statistical profiling
*   **spark_get_series_descriptions(config, df, summarizer, typeset, pbar)**: Processes Spark DataFrame columns in parallel for descriptive statistics
*   **spark_missing_bar(config, df)**: Computes missing data bar chart visualization for Spark DataFrames
*   **spark_missing_heatmap(config, df)**: Generates missing data heatmap visualization for Spark DataFrames
*   **spark_missing_matrix(config, df)**: Creates missing data matrix visualization for Spark DataFrames
*   **spark_pearson_compute(config, df, summary)**: Computes Pearson correlation matrix for Spark DataFrames
*   **spark_spearman_compute(config, df, summary)**: Computes Spearman correlation matrix for Spark DataFrames
*   **spark_kendall_compute(config, df, summary)**: Computes Kendall correlation matrix for Spark DataFrames
*   **spark_cramers_compute(config, df, summary)**: Placeholder for Cramér's V correlation computation for Spark DataFrames
*   **spark_phi_k_compute(config, df, summary)**: Computes phi-k correlation matrix for Spark DataFrames
*   **spark_check_dataframe(df)**: Validates that input is a PySpark DataFrame
*   **spark_preprocess(config, df)**: Filters out MapType columns from Spark DataFrames
*   **describe_boolean_1d_spark(config, df, summary)**: Extracts most frequent value from boolean data summary for Spark
*   **describe_categorical_1d_spark(config, df, summary)**: Processes categorical data summary for Spark DataFrames
*   **describe_counts_spark(config, series, summary)**: Computes value counts and missing value statistics for Spark DataFrames
*   **date_stats_spark(df, summary)**: Computes minimum and maximum date values from Spark DataFrames
*   **describe_date_1d_spark(config, df, summary)**: Processes date column data in Spark DataFrames for profiling
*   **describe_generic_spark(config, df, summary)**: Computes basic descriptive statistics for Spark DataFrames
*   **describe_numeric_1d_spark(config, df, summary)**: Computes comprehensive descriptive statistics for numeric Spark DataFrames
*   **numeric_stats_spark(df, summary)**: Computes fundamental statistical measures for numeric Spark DataFrames
*   **describe_supported_spark(config, series, summary)**: Adds distinct value and uniqueness statistics to Spark DataFrame summaries
*   **describe_text_1d_spark(config, df, summary)**: Collects sample rows from Spark DataFrames for text variable analysis
*   **MissingnoBarSparkPatch**: A Spark DataFrame patch class enabling missing data visualization for PySpark DataFrames

## Dependencies:
*   **Internal imports**:
    *   `src.ydata_profiling.config.Settings`: Configuration management for profiling settings
    *   `src.ydata_profiling.model.summarizer.BaseSummarizer`: Statistical summarization base class
    *   `src.ydata_profiling.model.spark.dataframe_spark`: Spark DataFrame validation and preprocessing
    *   `src.ydata_profiling.model.spark.missing_spark`: Missing data analysis and visualization
    *   `src.ydata_profiling.model.spark.sample_spark`: Sample generation for Spark DataFrames
    *   `src.ydata_profiling.model.spark.summary_spark`: Overall profiling coordination
    *   `src.ydata_profiling.model.spark.table_spark`: Table-level statistics computation
    *   `src.ydata_profiling.model.spark.duplicates_spark`: Duplicate detection functionality
    *   `src.ydata_profiling.model.spark.correlations_spark`: Correlation computation functions
    *   `src.ydata_profiling.model.spark.describe_boolean_spark`: Boolean data profiling
    *   `src.ydata_profiling.model.spark.describe_categorical_spark`: Categorical data profiling
    *   `src.ydata_profiling.model.spark.describe_counts_spark`: Value counts computation
    *   `src.ydata_profiling.model.spark.describe_date_spark`: Date data profiling
    *   `src.ydata_profiling.model.spark.describe_generic_spark`: Generic statistics computation
    *   `src.ydata_profiling.model.spark.describe_numeric_spark`: Numeric data profiling
    *   `src.ydata_profiling.model.spark.describe_supported_spark`: Support statistics computation
    *   `src.ydata_profiling.model.spark.describe_text_spark`: Text data profiling
    *   `src.ydata_profiling.model.spark.timeseries_index_spark`: Time series index analysis
    *   `src.ydata_profiling.utils.common`: Common utility functions
    *   `src.ydata_profiling.utils.helpers`: Helper functions for profiling operations
    *   `src.ydata_profiling.utils.multiprocessing`: Multiprocessing utilities for parallel processing
    *   `src.ydata_profiling.utils.plotting`: Plotting utilities for visualization
    *   `src.ydata_profiling.utils.spark`: Spark-specific utility functions
    *   `src.ydata_profiling.utils.types`: Type definitions and utilities
    *   `src.ydata_profiling.utils.validation`: Validation utilities
*   **External imports**:
    *   `pyspark.sql.DataFrame`: PySpark DataFrame class for distributed data processing
    *   `pyspark.sql.functions`: PySpark SQL functions for data manipulation
    *   `pyspark.sql.types`: PySpark data types for schema definition
    *   `pyspark.ml.feature.VectorAssembler`: Spark ML feature assembler for correlation computation
    *   `pyspark.ml.stat.Correlation`: Spark ML statistical correlation functions
    *   `numpy`: Numerical computing library for mathematical operations
    *   `pandas`: Data analysis library for data manipulation and visualization
    *   `warnings`: Python warnings module for issuing deprecation and configuration warnings
    *   `collections.Counter`: Counter class for frequency calculations
    *   `typing`: Type hinting utilities for better code documentation
    *   `concurrent.futures.ThreadPoolExecutor`: Threading utilities for parallel processing
    *   `tqdm`: Progress bar library for monitoring long-running operations

## Constraints:
*   **Thread-safety**: Most functions are stateless and thread-safe when used with immutable inputs
*   **Initialization prerequisites**: All functions assume valid Spark session context and properly initialized configuration objects
*   **Data type requirements**: Functions expect PySpark DataFrames as input and may raise errors for incompatible data types
*   **Memory considerations**: Some functions perform operations that may cause memory pressure (e.g., converting Spark DataFrames to Pandas)
*   **Performance considerations**: Functions leverage Spark's distributed computing capabilities but may still have performance implications for very large datasets
*   **Configuration constraints**: Functions depend on specific configuration settings being properly initialized in the Settings object
*   **Spark version compatibility**: Some functions may require specific Spark versions for certain features (e.g., VectorAssembler handleInvalid parameter)

---

## Files

- [`correlations_spark.py`](spark/correlations_spark.md)
- [`dataframe_spark.py`](spark/dataframe_spark.md)
- [`describe_boolean_spark.py`](spark/describe_boolean_spark.md)
- [`describe_categorical_spark.py`](spark/describe_categorical_spark.md)
- [`describe_counts_spark.py`](spark/describe_counts_spark.md)
- [`describe_date_spark.py`](spark/describe_date_spark.md)
- [`describe_generic_spark.py`](spark/describe_generic_spark.md)
- [`describe_numeric_spark.py`](spark/describe_numeric_spark.md)
- [`describe_supported_spark.py`](spark/describe_supported_spark.md)
- [`describe_text_spark.py`](spark/describe_text_spark.md)
- [`duplicates_spark.py`](spark/duplicates_spark.md)
- [`missing_spark.py`](spark/missing_spark.md)
- [`sample_spark.py`](spark/sample_spark.md)
- [`summary_spark.py`](spark/summary_spark.md)
- [`table_spark.py`](spark/table_spark.md)
- [`timeseries_index_spark.py`](spark/timeseries_index_spark.md)

