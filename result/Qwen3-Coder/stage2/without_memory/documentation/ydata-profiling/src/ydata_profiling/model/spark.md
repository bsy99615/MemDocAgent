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
Provides Spark-specific implementations for data profiling operations, enabling efficient analysis of large-scale datasets using Apache Spark's distributed computing capabilities.

## Description:
This module serves as the Spark backend for the ydata-profiling library, implementing data profiling operations specifically optimized for Apache Spark DataFrames. It provides distributed computing equivalents of the core profiling functionality found in the standard implementation, allowing users to profile large datasets that don't fit in memory on a single machine.

The module is consumed primarily by the main profiling pipeline when working with Spark DataFrames, providing the necessary distributed implementations for:
- Statistical computations and correlations
- Data type detection and categorization  
- Missing data analysis
- Duplicate detection
- Sampling operations
- Table-level statistics computation

These components are grouped together because they represent the core profiling operations that need to be adapted for Spark's distributed architecture while maintaining the same interface and behavior as their pandas counterparts.

## Components:
- correlations_spark.py: Implements correlation calculations (Pearson, Spearman, Cramér's V, Phi-K) using Spark's built-in functions
- dataframe_spark.py: Provides utilities for validating and preprocessing Spark DataFrames
- describe_boolean_spark.py: Implements descriptive statistics for boolean data types in Spark
- describe_categorical_spark.py: Implements descriptive statistics for categorical data types in Spark
- describe_counts_spark.py: Computes value counts and related statistics for Spark DataFrames
- describe_date_spark.py: Implements descriptive statistics for date/time data types in Spark
- describe_generic_spark.py: Provides generic statistical measures applicable to all data types in Spark
- describe_numeric_spark.py: Implements descriptive statistics for numeric data types in Spark
- describe_supported_spark.py: Computes basic statistics for supported data types in Spark
- describe_text_spark.py: Implements descriptive statistics for text data types in Spark
- duplicates_spark.py: Detects and analyzes duplicate records in Spark DataFrames
- missing_spark.py: Provides missing data analysis tools for Spark DataFrames
- sample_spark.py: Implements sampling operations for Spark DataFrames
- summary_spark.py: Core summarization functions for Spark DataFrames
- table_spark.py: Computes table-level statistics for Spark DataFrames
- timeseries_index_spark.py: Time series index analysis for Spark DataFrames

## Public API:
- spark_check_dataframe(df: DataFrame) -> None: Validates that input is a Spark DataFrame
- spark_preprocess(config: Settings, df: DataFrame) -> DataFrame: Preprocesses Spark DataFrame by removing problematic map-type columns
- spark_describe_1d(config: Settings, series: DataFrame, summarizer: BaseSummarizer, typeset: VisionsTypeset) -> dict: Describes a single column in a Spark DataFrame
- spark_get_series_descriptions(config: Settings, df: DataFrame, summarizer: BaseSummarizer, typeset: VisionsTypeset, pbar: tqdm) -> dict: Computes descriptions for all columns in a Spark DataFrame
- spark_get_table_stats(config: Settings, df: DataFrame, variable_stats: dict) -> dict: Computes table-level statistics for a Spark DataFrame
- spark_get_duplicates(config: Settings, df: DataFrame, supported_columns: Sequence) -> Tuple[Dict[str, Any], Optional[DataFrame]]: Identifies duplicate records in a Spark DataFrame
- spark_missing_bar(config: Settings, df: DataFrame) -> str: Creates a bar chart visualization of missing data patterns
- spark_missing_heatmap(config: Settings, df: DataFrame) -> str: Creates a heatmap visualization of missing data correlations
- spark_missing_matrix(config: Settings, df: DataFrame) -> str: Creates a matrix visualization of missing data patterns
- spark_get_sample(config: Settings, df: DataFrame) -> List[Sample]: Retrieves samples from a Spark DataFrame
- spark_cramers_compute(config: Settings, df: DataFrame, summary: dict) -> Optional[pd.DataFrame]: Computes Cramér's V correlation matrix for Spark DataFrames (not implemented)
- spark_kendall_compute(config: Settings, df: DataFrame, summary: dict) -> Optional[pd.DataFrame]: Computes Kendall's tau correlation matrix for Spark DataFrames (not implemented)
- spark_pearson_compute(config: Settings, df: DataFrame, summary: dict) -> Optional[pd.DataFrame]: Computes Pearson correlation matrix for Spark DataFrames
- spark_phi_k_compute(config: Settings, df: DataFrame, summary: dict) -> Optional[pd.DataFrame]: Computes Phi-K correlation matrix for Spark DataFrames
- spark_spearman_compute(config: Settings, df: DataFrame, summary: dict) -> Optional[pd.DataFrame]: Computes Spearman correlation matrix for Spark DataFrames

## Dependencies:
Internal:
- src.ydata_profiling.config.Settings: Configuration object for profiling settings
- src.ydata_profiling.model.summarizers.BaseSummarizer: Abstract base class for summarization logic
- src.ydata_profiling.model.typeset.VisionsTypeset: Type inference and casting utilities
- src.ydata_profiling.visualisation.plot_missing_bar: Missing data visualization functions
- src.ydata_profiling.visualisation.plot_missing_heatmap: Missing data visualization functions
- src.ydata_profiling.visualisation.plot_missing_matrix: Missing data visualization functions
- src.ydata_profiling.model.sample.Sample: Sample data structure

External:
- pyspark.sql.DataFrame: Core Spark DataFrame class
- pyspark.sql.functions: Spark SQL functions for data manipulation
- pyspark.ml.feature.VectorAssembler: Spark ML feature assembly for correlation calculations
- pyspark.ml.stat.Correlation: Spark ML statistical correlation functions
- pandas: Required for data processing and visualization
- numpy: Required for numerical operations
- phik: Required for Phi-K correlation calculations
- tqdm: Progress bar for long-running operations
- multiprocessing: Used for parallel processing of column descriptions

## Constraints:
- All functions expect Spark DataFrames as input, not pandas DataFrames
- Functions must be called within a Spark session context
- Some operations may require significant memory allocation for large datasets
- Certain correlation methods (Cramér's V, Phi-K) require additional dependencies (phik)
- The module assumes proper Spark configuration for distributed execution
- Functions should be called in order respecting dependencies (e.g., preprocessing before analysis)

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

