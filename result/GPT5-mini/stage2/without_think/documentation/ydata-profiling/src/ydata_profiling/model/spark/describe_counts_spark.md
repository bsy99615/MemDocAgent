# `describe_counts_spark.py`

## `src.ydata_profiling.model.spark.describe_counts_spark.describe_counts_spark` · *function*

## Summary:
Compute value counts for a single Spark DataFrame "series" column, persist the full Spark counts, and return a summary updated with missing-value counts and two sampled pandas Series of the top values (all and without NaN).

## Description:
This function is the Spark-specific implementation of value-counts extraction for a single-column series represented as a pyspark.sql.DataFrame. It:
- groups the input DataFrame by the series column(s) and computes counts,
- persists the full Spark DataFrame of counts,
- computes the number of missing values (nulls) for the series,
- materializes two sampled pandas Series (limited to 200 rows) for use in downstream reporting: one sorted by the series values and one that excludes NaNs.

Known callers:
- No direct callers were found in the local repository snapshot. Conceptually, this function is intended to be called by the profiling pipeline's Spark dispatch layer when generating column summaries for Spark-backed datasets (i.e., it implements the Spark variant of describe_counts).

Why this is a separate function:
- Encapsulates Spark-specific operations (groupBy, persist, toPandas, dropna) and the transfer of results into driver-side Python objects.
- Keeps the Spark implementation isolated from non-Spark summary algorithms, enabling a pluggable architecture where describe_counts (generic API) can dispatch to describe_counts_spark for Spark engines.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: profiling configuration object passed through unchanged. Not used internally by this function but returned to keep the same (config, series, summary) pipeline signature.
    series (pyspark.sql.DataFrame):
        - Type: pyspark.sql.DataFrame
        - Required properties:
            * Must represent the series to be described and must contain at least one column.
            * The first column (series.columns[0]) is treated as the value column used for indexing the pandas Series outputs.
        - Typical shape: a single-column DataFrame like df.select("col_name").
    summary (dict):
        - Type: dict
        - Mutable dictionary which this function updates in-place with computed statistics and objects.

Interdependencies:
- The function expects series.columns to be indexable and non-empty; summary must be a mutable mapping. config is passed through.

## Returns:
Tuple[Settings, pyspark.sql.DataFrame, dict]
    - The same config object passed in (unchanged).
    - The same series DataFrame passed in (unchanged).
    - The summary dict passed in, updated with the following keys:
        * "n_missing" -> int
            - Number of rows where the series value is null. If no null counts row exists in the computed counts DataFrame, this will be 0.
        * "value_counts" -> pyspark.sql.DataFrame
            - The full Spark DataFrame produced by grouping the series and counting occurrences. This DataFrame is persisted (cache) before return.
            - Schema: [<value_column(s)>, "count"]
        * "value_counts_index_sorted" -> pandas.Series
            - A pandas Series (length up to 200) created by sorting the Spark counts by the series value (ascending), limiting to 200 rows, converting to pandas, setting the series value as the index, and squeezing to a Series of counts.
            - Index: unique series values; Values: integer counts.
        * "value_counts_without_nan" -> pandas.Series
            - Similar to value_counts_index_sorted but excludes rows with null values (uses value_counts.dropna()) and is limited to 200 rows.

Edge cases in return:
- If there are no nulls, "n_missing" will be 0.
- If the series has fewer than 200 unique values, the pandas Series will contain fewer entries.
- value_counts is a persisted Spark DataFrame — consumer code should unpersist it when no longer needed to free executor memory.

## Raises:
No exceptions are explicitly raised in the function body, but calling it can surface runtime errors originating from PySpark and pandas:
    - IndexError: if series.columns is empty (accessing series.columns[0]).
    - AttributeError: if the provided series is not a DataFrame or lacks expected members (columns, groupBy).
    - pyspark.sql.utils.AnalysisException or Py4JJavaError: if groupBy / sort / dropna / toPandas are invoked with invalid column names or there are Spark-side errors.
    - MemoryError or pandas-related errors: if toPandas receives more data than available driver memory (mitigated by limit(200) in this function).

Callers should catch and handle these exceptions according to their error-handling policy.

## Constraints:
Preconditions:
    - series must be a valid pyspark.sql.DataFrame with at least one column.
    - The calling context must have an active SparkSession.
    - summary must be a mutable dict (mapping) provided by the caller.

Postconditions (guaranteed after return):
    - summary contains keys "n_missing", "value_counts", "value_counts_index_sorted", "value_counts_without_nan" with the types and meanings described above.
    - The Spark DataFrame assigned to summary["value_counts"] is persisted (cached) in the Spark session.

## Side Effects:
    - Caching: calls persist() on the Spark value_counts DataFrame (summary["value_counts"]); this changes executor-side cache state.
    - Driver memory usage: calls to toPandas() transfer up to 200 rows from executors to the driver for each of two conversions; that data is materialized as pandas.Series objects in driver memory.
    - No files, network calls, or global variable mutations are performed by this function itself beyond interacting with the Spark session.

## Control Flow:
flowchart TD
    A[Start: receive (config, series, summary)] --> B{series.columns non-empty?}
    B -- No --> E[Raise IndexError or AttributeError at runtime]
    B -- Yes --> C[Compute value_counts = series.groupBy(series.columns).count()]
    C --> D[Sort value_counts by "count" descending and persist]
    D --> F[Compute value_counts_index_sorted = value_counts sorted by series.columns[0] ascending]
    F --> G[Find n_missing by filtering rows where series.columns[0] is null and taking first().count]
    G --> H[If no row -> n_missing = 0; else n_missing = row["count"]]
    H --> I[Convert value_counts_index_sorted.limit(200) -> toPandas() -> set_index -> squeeze => pandas Series]
    I --> J[Set summary["n_missing"], summary["value_counts"] (persisted), summary["value_counts_index_sorted"]]
    J --> K[Compute summary["value_counts_without_nan"] via value_counts.dropna().limit(200).toPandas()...]
    K --> L[Return (config, series, summary)]

## Examples:
Example usage (conceptual; assumes an active SparkSession `spark` and Settings object `config`):

    # Given a DataFrame `df` with a column "category":
    series_df = df.select("category")  # single-column DataFrame
    summary = {}

    config, series_df, summary = describe_counts_spark(config, series_df, summary)

    # After call:
    # - summary["n_missing"] is an int (number of nulls in "category")
    # - summary["value_counts"] is a persisted Spark DataFrame with columns ["category","count"]
    # - summary["value_counts_index_sorted"] is a pandas.Series indexed by category values (up to 200 entries)
    # - summary["value_counts_without_nan"] is a pandas.Series of counts excluding nulls (up to 200 entries)

Error handling example:

    try:
        config, series_df, summary = describe_counts_spark(config, series_df, summary)
    except (IndexError, AttributeError, Exception) as exc:
        # Handle Spark or data errors (logging, fallback, or re-raise)
        raise

Notes:
- Consumers that no longer need the persisted Spark DataFrame should call summary["value_counts"].unpersist() to release executor memory.
- This function intentionally returns the config and series unchanged to match the profiling pipeline signature, allowing it to be used interchangeably with non-Spark variants.

