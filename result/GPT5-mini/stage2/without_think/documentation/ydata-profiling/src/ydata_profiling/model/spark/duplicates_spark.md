# `duplicates_spark.py`

## `src.ydata_profiling.model.spark.duplicates_spark.spark_get_duplicates` · *function*

## Summary:
Compute duplicate rows in a PySpark DataFrame according to the runtime configuration and return summary metrics plus a small sample of duplicate groups.

## Description:
This function is intended to be used as the Spark-specific implementation for detecting duplicate rows during dataset profiling. It:

- Reads configuration from config.duplicates (uses the head and key attributes).
- Short-circuits if reporting a sample of duplicates is disabled (head == 0) or if no supported columns or rows are present.
- Groups by all DataFrame columns, counts occurrences per unique row, and retains only groups with count > 1.
- Returns overall duplicate metrics and, if requested, a pandas DataFrame with up to head duplicate groups ordered by frequency.

Known callers:
- No direct callers were discovered in the provided code context. Typical usage is from a higher-level profiling pipeline that invokes a Spark variant of duplicate detection when a DataFrame is being analyzed.

Reason for extraction:
- The logic is extracted to isolate Spark-specific duplicate-detection behavior (groupBy / aggregation / conversion to pandas) from generic profiling orchestration. This keeps engine-specific operations centralized and testable, and avoids inlining expensive Spark operations in general profiling code.

## Args:
    config (Settings):
        - A configuration object exposing a duplicates namespace with at least:
            * head: int — maximum number of duplicate groups to return (0 disables returning a sample).
            * key: str — the column name to use for storing the duplicate count in the returned sample.
        - The function only reads config.duplicates.head and config.duplicates.key.
    df (pyspark.sql.DataFrame):
        - The Spark DataFrame to analyze for duplicates.
        - Must be a valid Spark DataFrame instance with a columns attribute and supporting groupBy/agg/filter/orderBy/limit/toPandas/count operations.
    supported_columns (Sequence):
        - A sequence (e.g., list) of columns considered supported by the engine.
        - If empty or falsy, duplicate detection is skipped and zero metrics are returned.

Interdependencies:
    - If config.duplicates.key matches any name in df.columns the function raises ValueError to avoid clobbering existing columns.

## Returns:
    Tuple[Dict[str, Any], Optional[pandas.DataFrame]]:
        - metrics: dict with keys:
            * "n_duplicates" (int): number of distinct duplicate groups found (i.e., unique rows that appear more than once).
            * "p_duplicates" (float): proportion of duplicate groups relative to total number of rows in df (computed as n_duplicates / df.count()).
        - sample: pandas.DataFrame or None
            * If a sample is requested (config.duplicates.head > 0) and duplicates exist, returns a pandas DataFrame containing up to head duplicate groups.
            * The sample DataFrame contains all original DataFrame columns plus one extra column named config.duplicates.key containing the integer duplicate count for that row.
            * Rows are ordered by the duplicate count descending.
            * If no sample is requested or no duplicates are found, returns None.

Edge-case returns:
    - If config.duplicates.head == 0: returns empty metrics dict and None.
    - If supported_columns is falsy or df.count() == 0: returns metrics with n_duplicates = 0 and p_duplicates = 0.0, and None for the sample.

## Raises:
    ValueError:
        - Raised when config.duplicates.key is present in df.columns. Exact condition:
          if config.duplicates.key in df.columns: raise ValueError("Duplicates key (...) may not be part of the DataFrame ...")

Other exceptions:
    - Spark runtime exceptions may be raised by called DataFrame operations (groupBy, agg, count, toPandas, etc.) in case of cluster issues, schema problems, or resource exhaustion. These are not explicitly trapped here.

## Constraints:
Preconditions:
    - config must provide duplicates.head (int) and duplicates.key (str).
    - df must be a valid Spark DataFrame object and accessible in the current Spark session.
    - Calling this function will at times call df.count() which triggers a full job; callers should be aware this is an expensive operation.

Postconditions:
    - If a pandas sample is returned, it contains at most config.duplicates.head rows and an extra integer column named config.duplicates.key with counts > 1.
    - metrics["n_duplicates"] and metrics["p_duplicates"] reflect counts computed from the DataFrame at the time of invocation.

## Side Effects:
    - Executes Spark actions that may trigger jobs:
        * df.count() is called (can be expensive).
        * duplicated_df.count() is called (another Spark action).
        * duplicated_df.limit(...).toPandas() collects up to head rows to the driver as a pandas DataFrame (can use driver memory).
    - No reads/writes to files, databases, or external networks are performed by this function itself.
    - No global variables are mutated.

## Control Flow:
flowchart TD
    Start --> GetHead{n_head = config.duplicates.head}
    GetHead --> |n_head == 0| ReturnEmpty
    GetHead --> |n_head != 0| CheckSupported
    CheckSupported --> |not supported_columns or df.count() == 0| ReturnZeroMetrics
    CheckSupported --> |supported and df has rows| CheckKey
    CheckKey --> |duplicates_key in df.columns| RaiseValueError
    CheckKey --> |key not in columns| BuildDuplicatedDF
    BuildDuplicatedDF --> ComputeMetrics
    ComputeMetrics --> ReturnSample
    ReturnEmpty --> End[Return metrics={}, None]
    ReturnZeroMetrics --> EndZero[Return metrics with zeros, None]
    RaiseValueError --> EndErr[Raise ValueError]
    ReturnSample --> EndSample[Return metrics, pandas.DataFrame sample]

## Examples:
Example usage (sketch — assumes a Settings-like object and an active Spark session):

    from pyspark.sql import SparkSession
    from types import SimpleNamespace

    spark = SparkSession.builder.getOrCreate()
    df = spark.createDataFrame(
        [(1, "a"), (1, "a"), (2, "b")],
        schema=["id", "val"]
    )

    # Minimal config-like object
    config = SimpleNamespace(duplicates=SimpleNamespace(head=10, key="__duplicates__"))

    supported_columns = ["id", "val"]

    try:
        metrics, sample_df = spark_get_duplicates(config, df, supported_columns)
    except ValueError as exc:
        # Handle the case where the configured key collides with a DataFrame column
        raise

    # metrics -> {"n_duplicates": 1, "p_duplicates": 1/3}
    # sample_df -> pandas DataFrame with columns ["id", "val", "__duplicates__"]

Notes:
    - Because the implementation calls df.count() and duplicated_df.count(), callers should avoid invoking this function repeatedly on large DataFrames without caching or otherwise minimizing repeated scans.
    - Converting to pandas via toPandas() can blow up driver memory if head is large; choose head conservatively.

