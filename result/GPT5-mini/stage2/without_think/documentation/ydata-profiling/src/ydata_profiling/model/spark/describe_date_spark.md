# `describe_date_spark.py`

## `src.ydata_profiling.model.spark.describe_date_spark.date_stats_spark` · *function*

## Summary:
Computes the minimum and maximum values of the first column in a PySpark DataFrame and returns them as a Python dict with keys "min" and "max".

## Description:
This function extracts the first column name from the provided PySpark DataFrame, constructs aggregate expressions to compute that column's minimum and maximum, runs a DataFrame aggregation, and returns the aggregated result as a Python dictionary.

Known callers within the codebase:
- This function is part of the Spark-specific summary/description utilities and is intended to be invoked by higher-level date summarization pipelines when summarizing a single-date column in a Spark DataFrame. (Call sites in the repository were not provided in the task input; callers typically call this during a column-wise profiling step.)

Why this logic is extracted into its own function:
- It isolates the Spark-specific aggregation logic for date-like columns (min/max) so that higher-level profiling code can call a uniform interface for summarizing a single column without inlining Spark expressions repeatedly. The function enforces the single-responsibility boundary: compute and return min/max for the first column of the supplied DataFrame.

## Args:
    df (pyspark.sql.DataFrame):
        - A PySpark DataFrame containing at least one column.
        - The function operates on df.columns[0] (the first column in the DataFrame's schema/order).
    summary (dict):
        - A dictionary passed for API compatibility with other summary functions in the profiling pipeline.
        - This parameter is not used by this function (ignored).

Interdependencies:
- The function references F (short for pyspark.sql.functions) in its implementation. The module namespace must provide F (commonly available if the module does `import pyspark.sql.functions as F`). If F is not present, a NameError/UnboundLocalError will occur.

## Returns:
    dict:
        - A Python dictionary containing exactly two keys: "min" and "max".
        - Values are the aggregated minimum and maximum taken from the first column of the DataFrame. Types of the values follow the PySpark to Python conversion rules (e.g., timestamps typically become datetime.datetime objects, numeric types become native Python numbers, nulls map to None).
        - Possible return examples:
            * {'min': datetime.datetime(2020, 1, 1, 0, 0), 'max': datetime.datetime(2021, 12, 31, 0, 0)}
            * {'min': None, 'max': None} when the aggregate yields NULLs (e.g., all values are null).
        - The returned dict is created by calling Row.asDict() on the aggregated Row returned by df.agg(...).first().

Edge-case returns:
- If the aggregation returns a Row with None values (common when input column contains only nulls), the dict values will be None.
- If df.agg(...).first() unexpectedly returns None (unlikely for an aggregation but possible in some runtime contexts), calling .asDict() will raise an AttributeError (see Raises).

## Raises:
    IndexError:
        - Condition: df.columns is empty and df.columns[0] is attempted — i.e., the DataFrame has no columns.
    NameError (or UnboundLocalError):
        - Condition: the name F (pyspark.sql.functions alias) is not defined in the module namespace when this function executes.
    AttributeError:
        - Condition: df.agg(...).first() returns None, and the code attempts to call .asDict() on None.
    pyspark.sql.utils.AnalysisException or other PySpark runtime exceptions:
        - Condition: any Spark-side errors during aggregation (e.g., invalid column metadata, execution failures). These exceptions are propagated from PySpark and are not caught by this function.

## Constraints:
Preconditions:
    - df must be a valid pyspark.sql.DataFrame instance.
    - df must have at least one column (otherwise IndexError is raised).
    - The module namespace must provide F (an alias for pyspark.sql.functions) or equivalent symbols used in the expression (min, max, col).
Postconditions:
    - On successful return, a dict with keys "min" and "max" is returned.
    - The input DataFrame is not mutated by this function.

## Side Effects:
    - No I/O (no file, network, or stdout operations).
    - No mutation of global variables within the function itself.
    - No persistence or writes to external systems.
    - The only external interaction is the Spark execution engine when df.agg(...) is executed; this triggers computation on the Spark cluster.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckCols{df.columns exists and len>0?}
    CheckCols -- No --> RaiseIndexError([Raise IndexError])
    CheckCols -- Yes --> BuildExpr([Build aggregate expressions: min, max on first column])
    BuildExpr --> CallAgg([Call df.agg(*expr)])
    CallAgg --> GetFirst([Call .first() on aggregated DataFrame])
    GetFirst --> FirstIsNone{first_row is None?}
    FirstIsNone -- Yes --> RaiseAttributeError([Attempting .asDict() on None -> AttributeError])
    FirstIsNone -- No --> AsDict([Call .asDict() on Row]) --> ReturnDict([Return dict with keys "min","max"])
    ReturnDict --> End([End])

## Examples:
Typical usage (happy path):
    - Given a PySpark DataFrame `df` whose first column is a timestamp or date column:
        result = date_stats_spark(df, {})
        # result -> {'min': datetime.datetime(...), 'max': datetime.datetime(...)}

Handling a DataFrame with only nulls:
    - Aggregation will produce None aggregates:
        result = date_stats_spark(df_with_only_nulls, {})
        # result -> {'min': None, 'max': None}

Defensive calling (recommended when DataFrame schema may be empty or the module alias F may be missing):
    - Verify prerequisites before calling:
        if len(df.columns) == 0:
            raise ValueError("Input DataFrame must have at least one column")
        # Ensure pyspark.sql.functions is available as F in the module scope
        # Then call the function and handle PySpark exceptions as needed.

## `src.ydata_profiling.model.spark.describe_date_spark.describe_date_1d_spark` · *function*

## Summary:
Produces a 1-dimensional date summary for a single-column Spark DataFrame: computes min/max and range for the first column, converts that column to UNIX timestamps (seconds), computes a histogram (bins determined by configuration and distinct-count), and returns the updated config, transformed DataFrame, and an updated summary dict containing min, max, range and histogram data.

## Description:
This function is a Spark-specific implementation of a 1D date summarization step used in the profiling pipeline. Typical callers are the column-wise profiling orchestrator that dispatches to type-specific summary functions when profiling a single date-like column in a PySpark DataFrame. It is extracted so that Spark-specific transformations (aggregations and RDD-based histogram computation) and summary mutations are contained in one place rather than inlined into higher-level profiling code; this keeps responsibilities clear: compute date min/max, convert values to numeric timestamps, compute histogram, and update the shared summary state.

Known callers / usage context:
- Called during the profiling step for a single date/timestamp column in a Spark-based profiling pipeline (e.g., the Spark branch of a "describe column" dispatcher).
- It expects to be run on a DataFrame whose first column (df.columns[0]) is the target date-like column.

Why separated:
- Encapsulates Spark API usage (DataFrame aggregation, withColumn + unix_timestamp, and RDD.histogram) so higher-level code can remain implementation-agnostic.

## Args:
    config (Settings):
        - Profiling configuration object.
        - Required nested attribute: config.plot.histogram.bins (an integer).
        - When config.plot.histogram.bins == 0, the function asks Spark to choose binning automatically ("auto").
    df (pyspark.sql.DataFrame):
        - A PySpark DataFrame containing at least one column.
        - The function operates exclusively on df.columns[0] (the first column in schema order).
        - On return, this DataFrame is a modified version where the first column has been replaced by its unix timestamp representation.
    summary (dict):
        - A mutable dictionary representing partial summary state for the column.
        - Required key: "n_distinct" (an integer) is read to limit the requested number of histogram bins when config.plot.histogram.bins != 0.
        - The function updates this dict in-place with keys: "min", "max", "range", and "histogram".

Interdependencies between parameters:
    - config.plot.histogram.bins and summary["n_distinct"] are used together to compute the number of bins passed to Spark's histogram routine.

## Returns:
    Tuple[Settings, pyspark.sql.DataFrame, dict]:
        - config: The same Settings object passed in (returned unchanged).
        - df: The input DataFrame with the first column transformed to UNIX timestamps (seconds since epoch). The column type becomes a numeric (integer/long) column where nulls remain null.
        - summary: The input summary dict updated in-place and also returned. New/updated keys:
            * "min": value from date_stats_spark (the minimum value of the original first column, type depends on Spark->Python conversion; may be datetime or numeric, or None).
            * "max": value from date_stats_spark (maximum; similar type considerations).
            * "range": computed as summary["max"] - summary["min"]. The result type depends on the operand types (e.g., a timedelta-like difference or numeric difference). If min/max are None, this subtraction will raise TypeError.
            * "histogram": a tuple (counts_array, bin_edges_array)
                - counts_array: numpy.ndarray of histogram bin counts (1D integer/float array).
                - bin_edges_array: numpy.ndarray of bin edge values (1D array). For numeric timestamps, edges are numeric epoch-second values; len(bin_edges_array) == len(counts_array) + 1 for bucket-style histograms.
        - Edge-case returns:
            * If the column contains only nulls, "min" and "max" may be None; histogram computation or range subtraction may subsequently raise errors as described in Raises.

## Raises:
    IndexError:
        - Condition: df has no columns (accessing df.columns[0] triggers IndexError).
    KeyError:
        - Condition: summary does not contain "n_distinct" and config.plot.histogram.bins != 0 (the code accesses summary["n_distinct"] without a fallback).
    TypeError:
        - Condition: summary["min"] or summary["max"] is None (or otherwise incompatible) so that summary["max"] - summary["min"] is not a supported subtraction.
    NameError (or UnboundLocalError):
        - Condition: the module-level alias F (pyspark.sql.functions) is not defined; the function calls F.unix_timestamp(...) and will fail if F is missing.
    ValueError / pyspark exceptions:
        - Conditions: invalid bins argument passed to RDD.histogram or runtime issues during Spark operations. RDD.histogram can raise ValueError for invalid bin specifications; Spark execution may raise various pyspark.sql.utils.* exceptions during aggregation or RDD operations. These are propagated to the caller.

## Constraints:
Preconditions:
    - df must be a valid pyspark.sql.DataFrame instance with at least one column.
    - The first column of df must be date-like (datetime, timestamp, or string in an accepted date format) for unix_timestamp to produce meaningful numeric timestamps.
    - config.plot.histogram.bins must be an integer (0 means "auto"); non-integer or malformed config may cause errors.
    - summary must include "n_distinct" when config.plot.histogram.bins != 0.
    - Module-level symbol F (alias for pyspark.sql.functions) must be available in the module namespace.

Postconditions (guaranteed on successful return):
    - summary contains updated keys: "min", "max", "range", and "histogram".
    - df's first column is converted to UNIX timestamp numeric values (nulls preserved).
    - The function returns the tuple (config, df, summary).

## Side Effects:
    - No filesystem, network, or stdout/stderr I/O is performed by the function itself.
    - The function triggers Spark computations: an aggregation to compute min/max (via date_stats_spark) and an RDD.histogram job on the selected column — these cause execution on the Spark cluster.
    - The summary dict passed in is mutated in-place.
    - No global variables are modified by the function itself.

## Control Flow:
flowchart TD
    Start([Start]) --> GetColName[Get first column name: col_name = df.columns[0]]
    GetColName --> CallDateStats[Call date_stats_spark(df, summary) -> stats]
    CallDateStats --> UpdateMinMax[Update summary with min/max from stats]
    UpdateMinMax --> ComputeRange[Compute summary["range"] = max - min]
    ComputeRange --> ConvertCol[Convert column: df = df.withColumn(col_name, F.unix_timestamp(...))]
    ConvertCol --> ReadBins[Read bins = config.plot.histogram.bins]
    ReadBins --> DecideBins{bins == 0?}
    DecideBins -- Yes --> binsArgAuto[Set bins_arg = "auto"]
    DecideBins -- No --> binsArgMin[Set bins_arg = min(bins, summary["n_distinct"])]
    binsArgAuto --> ComputeHist[Call RDD.histogram(bins_arg)]
    binsArgMin --> ComputeHist
    ComputeHist --> UpdateHist[Update summary["histogram"] = (array(hist), array(bin_edges))]
    UpdateHist --> Return([Return config, df, summary])
    Return --> End([End])

## Examples (usage / behavior described in prose):
    - Happy path: A profiler determines a column is date-like and constructs summary = {"n_distinct": 50}. config.plot.histogram.bins == 20. The function will compute min/max of that date column, calculate range = max - min, convert every cell in the column to UNIX seconds, request min(20, 50) = 20 bins from the RDD.histogram, receive bin edges and counts, and set summary["histogram"] to (numpy array of counts, numpy array of bin edges). It will return the same config, the DataFrame with the first column as numeric timestamps, and the mutated summary dict.
    - When config.plot.histogram.bins == 0: the function supplies "auto" to the RDD.histogram so Spark chooses binning heuristically.
    - Edge-case guidance: If the column contains only nulls, date_stats_spark may return {'min': None, 'max': None}; in that case the subtraction for "range" will raise TypeError and histogram behavior may be undefined. Callers should validate that min/max are not None (or handle TypeError) before relying on "range" or the histogram.

