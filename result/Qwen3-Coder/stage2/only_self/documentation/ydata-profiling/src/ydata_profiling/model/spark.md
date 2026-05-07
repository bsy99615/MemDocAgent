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
Handles Spark-specific data profiling operations and statistical computations for distributed data processing environments.

## Description:
This module provides Spark DataFrame-specific implementations of data profiling functionality. It bridges the gap between the general profiling framework and Apache Spark's distributed computing capabilities, enabling efficient analysis of large-scale datasets that don't fit in memory. The module contains specialized functions for computing descriptive statistics, handling different data types, managing missing values, detecting duplicates, and generating visualizations tailored for Spark environments.

## Components:
- **spark_check_dataframe**: Validates PySpark DataFrame input types
- **spark_preprocess**: Filters out incompatible MapType columns from DataFrames
- **spark_pearson_compute**: Computes Pearson correlation matrices for numeric Spark columns
- **spark_spearman_compute**: Computes Spearman rank correlation matrices for numeric Spark columns
- **spark_kendall_compute**: Computes Kendall rank correlation matrices (placeholder)
- **spark_cramers_compute**: Computes Cramér's V correlation coefficients for categorical variables (placeholder)
- **spark_phi_k_compute**: Computes phi-k correlations between categorical and numerical variables
- **_compute_spark_corr_natively**: Core utility for computing correlation matrices using native Spark methods
- **describe_boolean_1d_spark**: Processes boolean data summary statistics
- **describe_categorical_1d_spark**: Handles categorical variable description with redaction support
- **describe_counts_spark**: Computes value counts and missing value statistics for Spark DataFrames
- **date_stats_spark**: Computes minimum and maximum date values from Spark DataFrame columns
- **describe_date_1d_spark**: Processes date columns to compute temporal statistics and histograms
- **describe_generic_spark**: Updates summary statistics for Spark DataFrames with row counts
- **describe_numeric_1d_spark**: Computes comprehensive descriptive statistics for numeric Spark columns
- **numeric_stats_spark**: Calculates fundamental statistical measures for numeric Spark columns
- **describe_supported_spark**: Computes distinct value counts and uniqueness metrics for Spark DataFrames
- **describe_text_1d_spark**: Processes text data summary with conditional first-row sampling
- **spark_get_duplicates**: Detects duplicate rows in Spark DataFrames
- **MissingnoBarSparkPatch**: Adapts PySpark DataFrames for missing data visualization functions
- **spark_missing_bar**: Generates bar chart visualizations for missing value distributions
- **spark_missing_heatmap**: Creates heatmap visualizations showing missing value pattern correlations
- **spark_missing_matrix**: Generates matrix visualizations for missing data patterns (implementation not shown)
- **spark_get_sample**: Retrieves data samples from Spark DataFrames with head sampling support
- **spark_describe_1d**: Processes Spark DataFrame columns to generate descriptive statistics
- **spark_get_series_descriptions**: Generates descriptive statistics for all Spark DataFrame columns in parallel
- **spark_get_table_stats**: Computes comprehensive table-level statistics for Spark DataFrames
- **spark_get_time_index_description**: Provides Spark-specific time index descriptive information

## Public API:
- **spark_check_dataframe(config, df)**: Validates PySpark DataFrame input types
- **spark_preprocess(config, df)**: Filters out MapType columns from DataFrames
- **spark_pearson_compute(config, df, summary)**: Computes Pearson correlation matrix for numeric columns
- **spark_spearman_compute(config, df, summary)**: Computes Spearman correlation matrix for numeric columns
- **spark_kendall_compute(config, df, summary)**: Computes Kendall correlation matrix (placeholder)
- **spark_cramers_compute(config, df, summary)**: Computes Cramér's V correlation matrix (placeholder)
- **spark_phi_k_compute(config, df, summary)**: Computes phi-k correlation matrix for mixed data types
- **describe_boolean_1d_spark(config, df, summary)**: Extracts boolean data statistics
- **describe_categorical_1d_spark(config, df, summary)**: Processes categorical variable descriptions
- **describe_counts_spark(config, series, summary)**: Computes value counts and missing statistics
- **date_stats_spark(df, summary)**: Computes date range statistics
- **describe_date_1d_spark(config, df, summary)**: Processes date column statistics and histograms
- **describe_generic_spark(config, df, summary)**: Updates generic DataFrame statistics
- **describe_numeric_1d_spark(config, df, summary)**: Computes numeric column descriptive statistics
- **numeric_stats_spark(df, summary)**: Calculates basic numeric statistics
- **describe_supported_spark(config, series, summary)**: Computes distinct value and uniqueness metrics
- **describe_text_1d_spark(config, df, summary)**: Processes text data summary
- **spark_get_duplicates(config, df, supported_columns)**: Detects duplicate rows in DataFrames
- **MissingnoBarSparkPatch(df, columns=None, original_df_size=None)**: Adapter for missing data visualization
- **spark_missing_bar(config, df)**: Generates missing data bar chart visualization
- **spark_missing_heatmap(config, df)**: Creates missing data heatmap visualization
- **spark_get_sample(config, df)**: Retrieves data samples from Spark DataFrames
- **spark_describe_1d(config, series, summarizer, typeset)**: Processes Spark columns for descriptive statistics
- **spark_get_series_descriptions(config, df, summarizer, typeset, pbar)**: Computes statistics for all DataFrame columns
- **spark_get_table_stats(config, df, variable_stats)**: Computes table-level statistics
- **spark_get_time_index_description(config, df, table_stats)**: Extracts time index descriptive information

## Dependencies:
- **Internal imports**:
  - `ydata_profiling.config.Settings`: Configuration management for profiling settings
  - `ydata_profiling.model.summarizer.BaseSummarizer`: Statistical computation interface
  - `visions.VisionsTypeset`: Type inference system for data type detection
  - `tqdm`: Progress bar for long-running operations
- **External imports**:
  - `pyspark.sql.DataFrame`: Core Spark DataFrame class
  - `pyspark.sql.functions`: Spark SQL functions for data manipulation
  - `numpy`: Numerical computing library for statistical operations
  - `pandas`: Data analysis library for compatibility with visualization tools
  - `matplotlib.pyplot`: Visualization library for creating plots
  - `missingno`: Library for missing data visualization
  - `collections.Counter`: Data structure for counting occurrences

## Constraints:
- All functions require valid PySpark DataFrame inputs
- Configuration objects must be properly initialized Settings instances
- Functions that process numeric data expect numeric columns compatible with Spark statistical functions
- Memory considerations apply when converting Spark DataFrames to Pandas for visualization
- Some operations (like random sampling) are not fully implemented for Spark and issue warnings
- Thread safety: Functions are generally stateless and safe for concurrent execution
- Initialization prerequisites: Spark session must be active for all Spark operations

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

