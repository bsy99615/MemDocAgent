# `src.ydata_profiling.model.spark`

## Tree:
    - spark/
        - correlations_spark.py
        - dataframe_spark.py
        - describe_boolean_spark.py
        - describe_categorical_spark.py
        - describe_counts_spark.py
        - describe_date_spark.py
        - describe_generic_spark.py
        - describe_numeric_spark.py
        - describe_supported_spark.py
        - describe_text_spark.py
        - duplicates_spark.py
        - missing_spark.py
        - sample_spark.py
        - summary_spark.py
        - table_spark.py
        - timeseries_index_spark.py

## Role:
Provides Spark-specific implementations of data profiling and analysis functions to support distributed computing environments.

## Description:
This module contains specialized implementations of data profiling functions tailored for PySpark DataFrames. It enables the ydata-profiling library to analyze large-scale datasets distributed across Spark clusters while maintaining compatibility with the standard profiling interface. The module handles Spark-specific considerations such as distributed computation, DataFrame type handling, and integration with Spark's MLlib for statistical operations.

The components in this module are primarily consumed by the main profiling pipeline when working with PySpark DataFrames, ensuring that profiling operations scale appropriately for big data workloads. They are grouped together under a single module to maintain consistency in the profiling architecture and to provide a unified interface for Spark-based data analysis.

## Components:
- _compute_spark_corr_natively: Computes correlation matrices using native Spark MLlib functions
- spark_cramers_compute: Placeholder for Cramér's V correlation computation (not implemented)
- spark_kendall_compute: Placeholder for Kendall correlation computation (not implemented)
- spark_pearson_compute: Computes Pearson correlation matrix for numeric columns
- spark_phi_k_compute: Computes phi-k correlation for mixed data types using phik library
- spark_spearman_compute: Computes Spearman rank correlation matrix for numeric columns
- spark_check_dataframe: Validates that input is a PySpark DataFrame
- spark_preprocess: Filters out MapType columns incompatible with profiling
- describe_boolean_1d_spark: Extracts frequency information for boolean data in Spark
- describe_categorical_1d_spark: Handles categorical data sampling with redaction support
- describe_counts_spark: Computes value counts and missing data statistics for Spark
- date_stats_spark: Extracts min/max date values from Spark date columns
- describe_date_1d_spark: Processes date columns for profiling with histograms
- describe_generic_spark: Computes basic statistics for Spark DataFrames
- describe_numeric_1d_spark: Computes comprehensive numeric statistics for Spark columns
- numeric_stats_spark: Calculates basic numeric statistics for Spark columns
- describe_supported_spark: Computes distinct and uniqueness metrics for Spark DataFrames
- describe_text_1d_spark: Retrieves sample text data from Spark DataFrames with redaction
- spark_get_duplicates: Identifies duplicate rows in Spark DataFrames
- MissingnoBarSparkPatch: Adapter class for missingno library compatibility with Spark
- spark_missing_bar: Generates missing value bar charts for Spark DataFrames
- spark_missing_heatmap: Creates missing value correlation heatmaps for Spark DataFrames
- spark_missing_matrix: Produces interactive missing data matrix visualizations for Spark
- spark_get_sample: Retrieves samples from Spark DataFrames with head-only support
- spark_describe_1d: Computes descriptive statistics for Spark DataFrame columns using summarizers and type inference
- spark_get_series_descriptions: Processes all columns in a Spark DataFrame in parallel
- spark_get_table_stats: Computes comprehensive table-level statistics for Spark DataFrames
- spark_get_time_index_description: Describes time index properties for Spark DataFrames

## Public API:
- spark_check_dataframe(config, df): Validates PySpark DataFrame input
- spark_preprocess(config, df): Removes incompatible MapType columns
- spark_get_duplicates(config, df, supported_columns): Identifies duplicate rows
- spark_get_sample(config, df): Retrieves samples from Spark DataFrames
- spark_describe_1d(config, series, summarizer, typeset): Computes column statistics using summarizer and type inference logic
- spark_get_series_descriptions(config, df, summarizer, typeset, pbar): Processes all columns in parallel
- spark_get_table_stats(config, df, variable_stats): Computes table-level statistics
- spark_get_time_index_description(config, df, table_stats): Describes time index properties
- spark_pearson_compute(config, df, summary): Computes Pearson correlation matrix
- spark_spearman_compute(config, df, summary): Computes Spearman correlation matrix
- spark_phi_k_compute(config, df, summary): Computes phi-k correlation matrix
- spark_cramers_compute(config, df, summary): Placeholder for Cramér's V correlation
- spark_kendall_compute(config, df, summary): Placeholder for Kendall correlation
- spark_missing_bar(config, df): Generates missing value bar chart
- spark_missing_heatmap(config, df): Creates missing value heatmap
- spark_missing_matrix(config, df): Produces missing data matrix visualization
- describe_boolean_1d_spark(config, df, summary): Processes boolean data statistics
- describe_categorical_1d_spark(config, df, summary): Handles categorical data sampling
- describe_counts_spark(config, series, summary): Computes value counts and missing stats
- date_stats_spark(df, summary): Extracts date min/max values
- describe_date_1d_spark(config, df, summary): Processes date columns for profiling
- describe_generic_spark(config, df, summary): Computes basic DataFrame statistics
- describe_numeric_1d_spark(config, df, summary): Computes comprehensive numeric statistics
- numeric_stats_spark(df, summary): Calculates basic numeric statistics
- describe_supported_spark(config, series, summary): Computes distinct and uniqueness metrics
- describe_text_1d_spark(config, df, summary): Retrieves sample text data with redaction

## Dependencies:
- Internal: ydata_profiling.config.Settings, ydata_profiling.model.summarizer.BaseSummarizer, ydata_profiling.model.typeset.VisionsTypeset
- External: pyspark.sql.DataFrame, pyspark.sql.functions, pyspark.ml.stat.Correlation, pyspark.ml.feature.VectorAssembler, pandas, numpy, matplotlib, missingno

## Constraints:
- All functions must accept PySpark DataFrames as input
- Functions must preserve the original DataFrame and configuration objects unchanged
- Spark-specific operations should leverage distributed computing capabilities
- Memory-intensive operations should be optimized for Spark's distributed nature
- Thread safety is not required as functions operate on single DataFrame instances

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

