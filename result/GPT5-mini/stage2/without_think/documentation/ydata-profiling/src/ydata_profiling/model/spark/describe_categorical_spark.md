# `describe_categorical_spark.py`

## `src.ydata_profiling.model.spark.describe_categorical_spark.describe_categorical_1d_spark` · *function*

## Summary:
Extracts up to the first five rows of a Spark DataFrame into a pandas object and stores them in the provided summary dict under the "first_rows" key, unless categorical redaction is enabled in the configuration.

## Description:
This helper encapsulates the small, Spark-specific step of sampling a few rows for human-readable preview in a categorical-variable summary. It reads the configuration flag at config.vars.cat.redact; if redaction is disabled (False), it collects at most five rows from the Spark DataFrame to the driver as a pandas object and inserts that into summary["first_rows"]. The function returns the (possibly unchanged) config, the original DataFrame, and the (possibly updated) summary dict.

Known callers within the repository graph:
- No direct callers were found in the provided repository graph for this function. Typical usage (outside the available graph) is from a higher-level profiling pipeline that dispatches per-column summary routines for categorical columns and aggregates their results into a column summary dict.

Why this logic is extracted:
- Responsibility boundary: this function isolates the Spark-to-pandas sampling and redaction check from the heavier categorical summarization algorithms (which run on a pandas Series or on aggregated statistics). Separating the preview extraction keeps the summarization algorithms backend-agnostic and centralizes the driver-side collection logic and redaction policy in one place.

## Args:
    config (Settings): Global profiling configuration object. The implementation reads config.vars.cat.redact (expected boolean) to decide whether to fetch first rows. Must expose a nested attribute path vars.cat.redact.
    df (pyspark.sql.DataFrame): The Spark DataFrame containing the column(s) being summarized. Not modified by this function (the original DataFrame reference is returned).
    summary (dict): Mutable dictionary that accumulates the column summary. If redaction is disabled, this dict will be mutated in-place by setting summary["first_rows"] to a pandas object representing up to the first five rows.

Notes on parameter interdependencies:
- The function depends specifically on config.vars.cat.redact. If that attribute path does not exist or is not a boolean, an AttributeError or unexpected behavior may occur.
- The df parameter is used only to collect up to five rows; the function assumes df has the expected column(s) present.

## Returns:
Tuple[Settings, DataFrame, dict]
- The same config object passed in (unchanged).
- The same df object passed in (unchanged).
- The summary dict passed in; may be mutated in-place. If redaction is disabled, summary will contain a "first_rows" entry after return:
    - summary["first_rows"] = df.limit(5).toPandas().squeeze("columns")
      - If the resulting pandas DataFrame has a single column, squeeze("columns") will return a pandas.Series; otherwise it will be a pandas.DataFrame.
- If redaction is enabled (True), the function returns the inputs unchanged and does not add "first_rows".

## Raises:
- AttributeError: If config, config.vars, or config.vars.cat is missing, accessing config.vars.cat.redact will raise AttributeError.
- Any exception raised by the Spark toPandas conversion or underlying Spark operations can propagate (for example, pyspark.sql.utils.SparkException, ValueError, MemoryError) when calling df.limit(5).toPandas(). These are not caught by the function.
- TypeError: If df is not a DataFrame-like object implementing limit and toPandas methods, calling them may raise TypeError or AttributeError.

## Constraints:
Preconditions:
- A valid Settings-like config object with attribute path vars.cat.redact must be provided.
- df must be a pyspark.sql.DataFrame (or duck-typed equivalent) connected to an active SparkSession so that limit and toPandas are callable.
- summary must be a mutable mapping (dict) intended to hold summary keys.

Postconditions:
- The function guarantees that it returns the original config and df objects unchanged.
- If redaction is disabled, summary will contain a "first_rows" key mapping to a pandas.DataFrame or pandas.Series representing up to the first five rows collected from df.
- If redaction is enabled, summary is unchanged by this function.

## Side Effects:
- Network / driver memory: When redaction is disabled, df.limit(5).toPandas() collects data from executors to the driver. This can consume driver memory and network bandwidth, though limited to at most five rows.
- No file I/O, global variable mutation, or external service calls are performed by this function itself.
- The summary dict passed in is mutated in-place when "first_rows" is added.

## Control Flow:
flowchart TD
    A[Start] --> B{config.vars.cat.redact?}
    B -- True --> C[Do not collect preview]
    C --> D[Return config, df, summary (unchanged)]
    B -- False --> E[df.limit(5).toPandas() -> pandas_df]
    E --> F[pandas_df.squeeze("columns") -> preview]
    F --> G[summary["first_rows"] = preview]
    G --> D[Return config, df, summary (with first_rows)]

## Examples:
Example 1 — Redaction disabled (typical):
- Given a valid config where config.vars.cat.redact is False and df is a Spark DataFrame:
- Call describe_categorical_1d_spark(config, df, summary)
- After return, inspect summary["first_rows"] to show a pandas.DataFrame or pandas.Series of up to five rows for preview.

Example 2 — Redaction enabled:
- Given config.vars.cat.redact is True:
- Call describe_categorical_1d_spark(config, df, summary)
- After return, "first_rows" will not be present in summary.

Example 3 — Error handling when running in resource-constrained environments:
- When calling the function in environments with constrained driver memory, wrap the call in try/except to catch exceptions from toPandas (e.g., MemoryError or SparkException) and handle by logging and skipping preview collection; the function itself will propagate these exceptions if they occur.

