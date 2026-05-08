# `describe_supported_spark.py`

## `src.ydata_profiling.model.spark.describe_supported_spark.describe_supported_spark` · *function*

## Summary:
Compute and attach Spark-driven distinct and unique value metrics to an existing summary dictionary, returning the unchanged config and series alongside the updated summary.

## Description:
This function augments a precomputed summary dict for a Spark-backed series by computing:
- the number of distinct values (n_distinct),
- the proportion of distinct values (p_distinct),
- the number and proportion of values that occur exactly once (n_unique, p_unique),
- a boolean indicating if every observation is unique (is_unique).

Known callers within the codebase:
- No direct call sites for this exact function were discovered in a local scan of the repository. The function is the Spark-specific counterpart meant to be invoked by the Spark profiling path in the profiling pipeline when the backend is Spark. It is designed to fit into the pipeline stage that adapts generic summary algorithms to concrete backends (Spark vs. pandas).

Why this logic is extracted:
- Backend encapsulation: isolates Spark DataFrame operations (.count(), .where()) from higher-level profiling orchestration.
- Reusability & testability: keeps Spark behavior centralized so it can be tested and maintained independently of pipeline flow control.

## Args:
    config (Settings)
        The profiling configuration carried through the pipeline. This function does not inspect or mutate config; it is returned unchanged.
    series (DataFrame)
        The Spark DataFrame or column holder representing the series being described. The function does not mutate or transform this object; it is returned unchanged.
    summary (dict)
        A mutable dictionary that must already contain:
            - "count" (int or numeric): total number of observations for the series.
            - "value_counts" (pyspark.sql.DataFrame-like): a Spark DataFrame with per-value frequency data and a column named "count".
        The function mutates this dict in-place by adding or overwriting the derived metrics.

Interdependencies:
- The numeric correctness of p_distinct and p_unique depends on the "count" matching the population used to compute "value_counts". Mismatches yield semantically incorrect proportions even though the function will compute values mechanically.

## Returns:
Tuple[Settings, DataFrame, dict]
    - config: identical to the input Settings (unchanged).
    - series: identical to the input DataFrame (unchanged).
    - summary: the same dict instance passed in, mutated to include/overwrite the following keys:
        * "n_distinct" (int): summary["value_counts"].count()
        * "p_distinct" (float): n_distinct / count if count > 0 else 0
        * "n_unique" (int): summary["value_counts"].where("count == 1").count()
        * "p_unique" (float): n_unique / count (note: division is unconditional)
        * "is_unique" (bool): (n_unique == count)

Edge-case return notes:
- If count == 0:
    * "p_distinct" is explicitly set to 0.
    * "p_unique" is computed as n_unique / count and will therefore raise ZeroDivisionError (see Raises) unless callers guard against count == 0.

## Raises:
    KeyError
        If summary lacks the "count" or "value_counts" keys, a KeyError will be raised when accessing them.
    AttributeError (or similar)
        If summary["value_counts"] does not provide Spark-like methods used here (.count(), .where(...).count()), attribute or type errors will be raised by those operations.
    ZeroDivisionError
        If summary["count"] == 0, computing "p_unique" performs n_unique / count unguarded and will raise ZeroDivisionError.
    Spark (engine) exceptions
        Underlying Spark operations may raise Spark-specific exceptions (e.g., AnalysisException, IOException) which propagate out of this function.

## Constraints:
Preconditions:
    - summary must contain:
        * an integer/number under "count",
        * a Spark DataFrame-like "value_counts" with a "count" column.
    - The value_counts DataFrame should correspond to the same sample/population as "count".
Postconditions:
    - summary will contain the keys "n_distinct", "p_distinct", "n_unique", "p_unique", and "is_unique" with computed values as specified.
    - config and series are returned unchanged.

## Side Effects:
    - Mutates the provided summary dict in-place (adds/overwrites keys).
    - Triggers Spark computation: calls to .count() and .where(...).count() will force Spark actions, which submit jobs to the Spark engine and consume cluster resources.
    - No file, network, or global state is modified by this function itself.

## Control Flow:
flowchart TD
    A[Start: receive config, series, summary] --> B{summary has "count" and "value_counts"?}
    B -- No --> E[Access raises KeyError or attribute-related exception]
    B -- Yes --> C[count = summary["count"]]
    C --> D[n_distinct = summary["value_counts"].count()]
    D --> F[set summary["n_distinct"] = n_distinct]
    F --> G{count > 0?}
    G -- Yes --> H[set summary["p_distinct"] = n_distinct / count]
    G -- No --> I[set summary["p_distinct"] = 0]
    H --> J[n_unique = summary["value_counts"].where("count == 1").count()]
    I --> J
    J --> K[set summary["n_unique"] = n_unique]
    K --> L[set summary["is_unique"] = (n_unique == count)]
    L --> M[set summary["p_unique"] = n_unique / count  (may raise ZeroDivisionError if count == 0)]
    M --> N[Return (config, series, summary)]

## Examples:
Example 1 — Typical successful call (descriptive):
- Preconditions:
    * summary["count"] == 100
    * summary["value_counts"] is a Spark DataFrame listing distinct values and a "count" column with frequencies
- After calling, summary contains:
    * "n_distinct": integer number of distinct values
    * "p_distinct": n_distinct / 100
    * "n_unique": integer number of values occurring exactly once
    * "p_unique": n_unique / 100
    * "is_unique": True only if n_unique == 100

Example 2 — Usage pattern with guarding against count == 0 (pseudo-code lines; avoid using function definitions or imports here):
config = Settings(...)          # existing config object
series = spark_df.select("col") # Spark DataFrame or column
value_counts = series.groupBy("col").count()  # Spark DataFrame with "count" column
summary = {"count": series.count(), "value_counts": value_counts}

# Guard to avoid ZeroDivisionError for p_unique
if summary["count"] == 0:
    summary["p_unique"] = 0
    summary["p_distinct"] = 0
    summary["n_unique"] = 0
    summary["n_distinct"] = 0
    summary["is_unique"] = False
else:
    config, series, summary = describe_supported_spark(config, series, summary)

# After this, summary contains the derived metrics or was prefilled when count == 0.

Error handling guidance:
- If skipping the function when count == 0 is acceptable, check count and avoid the call.
- Alternatively, pre-set p_unique = 0 prior to calling to avoid ZeroDivisionError, but pre-setting still requires deciding the semantics (e.g., whether n_unique should be 0 or computed).

