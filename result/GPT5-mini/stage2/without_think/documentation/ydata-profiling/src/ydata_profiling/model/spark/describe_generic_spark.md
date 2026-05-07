# `describe_generic_spark.py`

## `src.ydata_profiling.model.spark.describe_generic_spark.describe_generic_spark` · *function*

## Summary:
Compute dataset-level counts for a Spark DataFrame and update the provided summary dictionary with total row count, proportion missing, non-missing count, and a placeholder memory size.

## Description:
This function performs a minimal Spark-specific augmentation of a dataset-level summary:
- It materializes the row count by calling DataFrame.count(), then uses that value to set/compute:
  - summary["n"] — total number of rows
  - summary["p_missing"] — proportion of missing values computed as summary["n_missing"] / n
  - summary["count"] — number of non-missing rows computed as n - summary["n_missing"]
  - summary["memory_size"] — set to 0 (placeholder)
- Known callers within the provided code context: no direct callers were present in the provided file context. Typically, this function is invoked by a Spark-specific profiling pipeline stage or wrapper that collects per-column summaries and then computes/updates dataset-level aggregates.
- Reason for extraction: this logic isolates Spark-specific materialization (df.count()) and summary mutation from the generic summary algorithms. It keeps Spark I/O and action-triggering behavior contained in one place, allowing the generic algorithms to remain backend-agnostic.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: configuration object passed through for API consistency. This function does not read or modify config; it returns it unchanged.
    df (DataFrame):
        - Type: pyspark.sql.DataFrame
        - Purpose: the Spark DataFrame whose total row count is needed.
        - Constraint: must be a valid, materializable Spark DataFrame. Calling this function triggers a Spark action (df.count()).
    summary (dict):
        - Type: dict
        - Purpose: mutable mapping representing the (partial) dataset-level summary. This function reads and writes keys on this dict.
        - Required keys before call:
            - "n_missing": numeric (int or float) representing the number of missing values (across the dataset or the considered context).
        - Post-call: the function will set/overwrite the keys "n", "p_missing", "count", and "memory_size".
        - Interdependencies: "p_missing" and "count" are computed from "n_missing" and the computed n.

## Returns:
    Tuple[Settings, DataFrame, dict]
        - The function returns the same config and df objects it received (unchanged), and the same summary dict object after in-place mutation.
        - The returned summary contains at least the following keys:
            - "n": integer row count (df.count())
            - "p_missing": summary["n_missing"] / n (float)
            - "count": n - summary["n_missing"] (int or float)
            - "memory_size": 0 (int)
        - Edge-case/possible values:
            - If summary["n_missing"] > n, then "p_missing" > 1 and "count" will be negative — the function does not clamp or validate this.
            - If values in summary["n_missing"] are floats, returned "count" may be float.

## Raises:
    - KeyError:
        - Condition: if "n_missing" is not present in the summary dict, attempting to read summary["n_missing"] will raise KeyError.
    - ZeroDivisionError:
        - Condition: if df.count() == 0, the computation summary["n_missing"] / length will raise ZeroDivisionError because of division by zero.
    - TypeError:
        - Condition: if summary["n_missing"] is not a numeric type that supports division/subtraction with an integer (e.g., None or a non-numeric string), Python will raise a TypeError (or a related error) during arithmetic.
    - pyspark-related exceptions:
        - Condition: calling df.count() runs a Spark job; Spark runtime errors (e.g., pyspark.sql.utils.SparkException, network/cluster failures) can propagate from that call.

## Constraints:
    Preconditions:
        - The caller must provide a summary dict that already contains a numeric "n_missing" value.
        - The DataFrame must be valid and accessible to the Spark context; calling this function will trigger a Spark action.
    Postconditions (guarantees after successful return):
        - summary contains updated keys "n", "p_missing", "count", and "memory_size".
        - The function returns the same config and df objects unchanged.

## Side Effects:
    - Spark job: calling df.count() triggers a Spark action that materializes the DataFrame to compute the row count. This can be expensive and may interact with cluster resources, executors, storage, and network.
    - In-place mutation: the supplied summary dict is mutated in place. The caller's reference to the dict will observe the updates.
    - No file, database, or network I/O is performed explicitly by this function beyond what Spark performs when materializing the DataFrame.
    - No global variables are modified by this function.

## Control Flow:
flowchart TD
    Start --> CountRows[df.count()]
    CountRows --> Set_n[set summary["n"] = n]
    Set_n --> Compute_p_missing{summary contains "n_missing"?}
    Compute_p_missing -- Yes --> ComputeValues[compute p_missing and count]
    Compute_p_missing -- No --> RaiseKeyError[KeyError thrown]
    ComputeValues --> Set_memory_size[set summary["memory_size"] = 0]
    Set_memory_size --> Return[return (config, df, summary)]
    CountRows -->|n == 0| DivisionByZero[division during p_missing -> ZeroDivisionError]

## Examples:
Typical (happy-path) usage:
    - Given a Spark DataFrame df and a summary dict that already has "n_missing":
        summary = {"n_missing": 10}
        config, df, summary = describe_generic_spark(config, df, summary)
        # After return:
        # - summary["n"] is an integer equal to df.count()
        # - summary["p_missing"] == summary["n_missing"] / summary["n"]
        # - summary["count"] == summary["n"] - summary["n_missing"]
        # - summary["memory_size"] == 0

Defensive wrapper to avoid ZeroDivisionError:
    - If callers cannot guarantee non-empty DataFrame, they should guard first:
        n = df.count()
        if n == 0:
            # Decide on desired behavior: set p_missing to 0, leave count 0, or skip computation
            summary["n"] = 0
            summary["p_missing"] = 0.0
            summary["count"] = 0
            summary["memory_size"] = 0
        else:
            config, df, summary = describe_generic_spark(config, df, summary)

Error handling for missing "n_missing":
    - Ensure the input summary contains "n_missing" before calling:
        if "n_missing" not in summary:
            summary["n_missing"] = compute_n_missing_somehow()
        config, df, summary = describe_generic_spark(config, df, summary)

