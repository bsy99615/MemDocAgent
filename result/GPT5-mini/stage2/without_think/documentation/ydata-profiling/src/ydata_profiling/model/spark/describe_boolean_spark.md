# `describe_boolean_spark.py`

## `src.ydata_profiling.model.spark.describe_boolean_spark.describe_boolean_1d_spark` · *function*

## Summary:
Extracts the first (most frequent) value and its frequency from a precomputed value_counts structure and stores them into the provided summary dictionary under the keys "top" and "freq". Returns the unchanged config and DataFrame together with the updated summary.

## Description:
This helper is intended for use by a Spark-based column description pipeline when the boolean-value frequency distribution has already been computed and placed into the summary dict under the "value_counts" key.

Known callers within the codebase:
- No direct callers were found in the inspected code snapshots. Conceptually, this function is used as the final step of a Spark-specific boolean summarization step: after computing value counts for a column (value_counts), call this function to extract the top value and frequency into the canonical summary dict.

Why this logic is extracted:
- Responsibility boundary: isolates the small, Spark-specific piece of logic that converts a DataFrame-like value_counts object into the generic summary dict shape expected by the rest of the profiling pipeline. This keeps the higher-level profiling orchestration independent from Spark Row/first() semantics and keeps mutation of the summary centralized.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: profiling configuration object passed through the pipeline; not inspected or modified by this function.
    df (DataFrame):
        - Type: pyspark.sql.DataFrame
        - Purpose: the Spark DataFrame being profiled; not inspected or modified by this function.
    summary (dict):
        - Type: dict
        - Purpose: accumulator for column summary statistics.
        - Required content: must contain a key "value_counts" whose value is a Spark DataFrame-like object with at least one row. The first row is expected to present two accessible elements: the value (index 0) and its count/frequency (index 1).
        - Interdependencies: after calling, summary will be mutated in-place to include the keys "top" and "freq" derived from summary["value_counts"]. The function relies on the pre-existence of "value_counts" and its first row.

## Returns:
    Tuple[Settings, DataFrame, dict]:
        - First element: the same config object passed in (unchanged).
        - Second element: the same df passed in (unchanged).
        - Third element: the same summary dict passed in, mutated in-place to include:
            - "top": the value taken from the first element of the first row of value_counts
            - "freq": the count taken from the second element of the first row of value_counts

    Edge-case return behavior:
        - If the call succeeds, returned objects are identical to inputs except summary now has "top" and "freq".
        - The function does not return alternative structures for empty or invalid input; such cases will result in exceptions (see Raises).

## Raises:
    - KeyError:
        - Trigger: summary does not contain the "value_counts" key (accessing summary["value_counts"]).
    - AttributeError:
        - Trigger: the object stored at summary["value_counts"] has no .first() method.
    - TypeError:
        - Trigger: value_counts.first() returns None (or a non-indexable object) and the code attempts to index it (top[0] / top[1]).
    - IndexError:
        - Trigger: value_counts.first() returns a sequence/Row with fewer than two elements such that top[0] or top[1] are invalid.
    - Other exceptions raised by the underlying value_counts.first() call may propagate (for example, runtime exceptions from Spark).

## Constraints:
    Preconditions:
        - The caller must have placed a computed value_counts into summary["value_counts"].
        - That value_counts must be a DataFrame-like object supporting .first() and yielding a row-like object where the first two positions correspond to (value, count).
    Postconditions:
        - summary contains keys "top" and "freq" set to the first row's value and count, respectively.
        - config and df are returned unchanged.

## Side Effects:
    - Mutates the passed-in summary dict in-place by adding/updating the keys "top" and "freq".
    - No I/O, network access, stdout/stderr output, or external state mutation beyond the in-memory summary dict.
    - No other global state is touched.

## Control Flow:
flowchart TD
    Start(["Start"])
    ReadVC[/"Retrieve value_counts = summary['value_counts']"/]
    GetFirst[/"Call top = value_counts.first()"/]
    UpdateSummary[/"Update summary with {'top': top[0], 'freq': top[1]}" /]
    Return["Return (config, df, summary)"]
    Start --> ReadVC --> GetFirst --> UpdateSummary --> Return
    ReadVC -. If 'value_counts' missing .-> ErrorKey[/"KeyError raised"/]
    GetFirst -. If .first() missing .-> ErrorAttr[/"AttributeError raised"/]
    GetFirst -. If first() returns insufficient/invalid row .-> ErrorIndex[/"TypeError/IndexError raised"/]

## Examples:
- Typical (conceptual) example:
    - Precondition: summary contains a computed Spark value_counts where the first row represents the most frequent boolean and its count. For example, the first row is equivalent to ("True", 125).
    - Effect: after calling, summary["top"] == "True" and summary["freq"] == 125. The same config and DataFrame objects are returned.

- Failure example (conceptual):
    - If summary lacks "value_counts", the function raises KeyError immediately.
    - If value_counts.first() returns None (no rows) or a row with fewer than two elements, the function will raise TypeError or IndexError when attempting to access top[0] or top[1].

Notes:
- This function intentionally performs minimal validation and relies on upstream computation to supply a well-formed "value_counts". Callers should ensure value_counts exists and contains at least one (value, count) row before invoking this function.

