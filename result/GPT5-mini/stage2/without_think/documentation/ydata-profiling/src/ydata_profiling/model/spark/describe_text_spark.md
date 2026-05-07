# `describe_text_spark.py`

## `src.ydata_profiling.model.spark.describe_text_spark.describe_text_1d_spark` · *function*

## Summary:
Collect up to five example text values from a Spark DataFrame into the provided summary dictionary unless text redaction is enabled.

## Description:
This helper reads the text-redaction flag from the configuration and, when redaction is disabled, collects up to the first five rows of the provided Spark DataFrame into driver memory (pandas) and stores them under summary["first_rows"]. It is a small, focused utility used during text-column profiling to capture representative sample values for reporting or inspection.

Known callers within the repository:
- No direct callers were found in the available code graph for this function. Typical callers are profiling pipelines that assemble per-column summaries for text variables (e.g., a text/one-dimensional descriptor step invoked from a higher-level "describe column" or "profile column" routine).

Why this logic is extracted:
- Responsibility boundary: isolates the logic that (a) respects the global/text-level redaction policy and (b) performs the costly collect-to-driver operation for sampling first rows. Extracting this keeps the profiling pipeline modular so the sampling and privacy policy check are centralized and reusable.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Required: yes
        - Expected structure: config.vars.text.redact must be a boolean-like flag (truthy => redact enabled).
        - Notes: Only the vars.text.redact attribute is read. If this attribute is missing or not boolean, behavior follows Python truthiness rules (may raise AttributeError if vars/text missing).
    df (pyspark.sql.DataFrame):
        - Type: pyspark.sql.DataFrame
        - Required: yes
        - Notes: The function limits this DataFrame to the first 5 rows using df.limit(5) and then calls toPandas() to collect those rows into driver memory. The DataFrame should be the column-level frame (typically one text column) but the function does not enforce column count.
    summary (dict):
        - Type: dict
        - Required: yes (mutable mapping)
        - Purpose: in-place target where the key "first_rows" will be set when redaction is disabled.
        - Interdependencies: the function mutates this dict in-place and also returns it as the third element of the returned tuple.

## Returns:
    Tuple[Settings, pyspark.sql.DataFrame, dict]
        - The function returns the three inputs (config, df, summary) as a convenience to be used in functional pipelines.
        - The returned summary may have been mutated: when redaction is disabled, summary["first_rows"] will be present and will contain the pandas representation of the sampled rows.
        - Possible values stored in summary["first_rows"]:
            * pandas.Series — if the collected pandas DataFrame has a single column (squeeze("columns") reduces columns axis).
            * pandas.DataFrame — if the collected pandas DataFrame has more than one column (squeeze will keep DataFrame).
            * Not present — if config.vars.text.redact is truthy (redaction enabled).

## Raises:
    - The function itself does not explicitly raise exceptions.
    - However, calls invoked by the implementation may raise and those exceptions propagate:
        * pyspark-related exceptions (for example, Py4JJavaError) if the Spark job fails during df.limit(...) or df.toPandas().
        * MemoryError or pandas-related errors when converting to pandas if the collected data is too large for driver memory.
        * AttributeError if config or its nested attributes (vars, text, redact) are missing.
    - Caller responsibility: any exception from underlying libraries is not swallowed and will surface to the caller.

## Constraints:
    Preconditions:
        - A valid Settings object with config.vars.text.redact accessible (or at least the attribute path exists).
        - df must be a valid pyspark.sql.DataFrame and SparkSession must be active for df.limit(...).toPandas() to succeed.
        - summary must be a mutable dict (or mapping that supports item assignment).
    Postconditions:
        - The same config and df objects are returned unchanged (no deep mutation of config or df is performed here).
        - If redaction is disabled, summary will contain the key "first_rows" whose value is the pandas representation (Series or DataFrame) of up to five collected rows.
        - No other keys in summary are touched by this function.

## Side Effects:
    - In-place mutation: writes/overwrites summary["first_rows"] when redaction is disabled.
    - Data movement: calls df.limit(5).toPandas(), which collects data from executors to the driver; this can increase driver memory usage and may cause OOM for unexpectedly wide or complex rows.
    - No file, network, or external database IO is performed by this function itself beyond the standard Spark operations used to retrieve data from the cluster.

## Control Flow:
flowchart TD
    A[Start: call describe_text_1d_spark(config, df, summary)] --> B{config.vars.text.redact truthy?}
    B -- Yes --> C[Skip sampling; return config, df, summary unmodified]
    B -- No --> D[Execute df.limit(5).toPandas().squeeze("columns")]
    D --> E[Assign result to summary["first_rows"]]
    E --> C

## Examples:
1) Typical usage when redaction is disabled (happy path):
    - Preconditions: config.vars.text.redact is False, Spark session active, df is a column-level DataFrame.
    - Outcome: summary["first_rows"] set to a pandas.Series (single column) or pandas.DataFrame (multiple columns).
    - Example call:
      config, df, summary = describe_text_1d_spark(config, df, summary)
      # After call: if not redacted, summary["first_rows"] contains up to 5 sample values.

2) When redaction is enabled:
    - Preconditions: config.vars.text.redact is True.
    - Outcome: no sample is collected; summary is left unchanged.
    - Example call:
      config, df, summary = describe_text_1d_spark(config, df, summary)
      # After call: "first_rows" not added to summary.

3) Error handling example (driver OOM or Spark failure):
    - Wrap calls that invoke this function in try/except to catch and handle propagated exceptions:
      try:
          config, df, summary = describe_text_1d_spark(config, df, summary)
      except Exception as exc:
          # Handle or log: possible Py4JJavaError, MemoryError, AttributeError for missing config attributes
          handle_sampling_error(exc)

Notes and implementation hints for reimplementation:
    - Respect the privacy flag (config.vars.text.redact) before collecting any data.
    - Use df.limit(5) to avoid unnecessary work on large datasets; convert to pandas only when needed and be mindful of driver memory.
    - Assign the pandas result to summary["first_rows"]; do not deep-copy summary unless required by caller semantics.
    - Keep the function side-effect behavior (mutating summary) consistent with surrounding pipeline expectations.

