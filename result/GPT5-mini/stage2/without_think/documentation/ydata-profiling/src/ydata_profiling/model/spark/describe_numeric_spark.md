# `describe_numeric_spark.py`

## `src.ydata_profiling.model.spark.describe_numeric_spark.numeric_stats_spark` · *function*

## Summary:
Compute eight standard univariate numeric aggregations for the DataFrame's first column and return them as a dictionary keyed by aggregation name.

## Description:
This function collects a fixed set of numeric summary statistics (mean, std, variance, min, max, kurtosis, skewness, sum) for the first column in the provided Spark DataFrame and returns those aggregates as a mapping from the alias names to their scalar results.

Known callers within the codebase:
- None were discovered in the immediate provided context. The function is intended for use within Spark-based profiling or summary pipelines that operate column-by-column on large datasets and require a compact numeric summary for a single column.

Why this logic is extracted:
- Single responsibility: it isolates the Spark aggregation expressions and the mechanics of executing them into one reusable operation.
- Reuse and testability: profiling flows can call this helper for any numeric column without embedding aggregation logic repeatedly.
- Separation of concerns: higher-level summary composition (e.g., combining aggregation results with histogram or distribution analysis) remains outside this function.

## Args:
    df (pyspark.sql.DataFrame)
        The Spark DataFrame to summarize. The function unconditionally targets the first column in df.columns (i.e., df.columns[0]).
        Preconditions:
            - df must expose .columns (sequence of column names) and support .agg(...) returning a DataFrame.
            - df must have at least one column, otherwise indexing df.columns[0] raises IndexError.
    summary (dict)
        Provided for API compatibility; ignored by this implementation. Callers may pass configuration here in other implementations, but this function does not read or mutate it.

## Returns:
    dict
        A dictionary produced by converting the Spark Row returned by df.agg(...).first() into a Python dict via asDict(). The dictionary contains these keys (exactly these names):
            - "mean"
            - "std"
            - "variance"
            - "min"
            - "max"
            - "kurtosis"
            - "skewness"
            - "sum"
        Value characteristics:
            - Values are the raw results of the corresponding Spark aggregation.
            - Typical types: floats for mean/std/variance/kurtosis/skewness, numeric (int/float/Decimal) for min/max/sum — exact runtime types depend on Spark's dtype handling and the column's type.
            - Aggregates computed over empty or all-null input rows are represented as None (Spark returns null for those aggregations).
        Note:
            - The function does not include the column name in the returned dict — only aggregation aliases are returned.

## Raises:
    IndexError
        If df.columns is empty and df.columns[0] is accessed.
    AttributeError
        If df.agg(...).first() returns None (unexpected), calling .asDict() will raise AttributeError("'NoneType' object has no attribute 'asDict'").
        Also raised if the passed object is not Spark DataFrame-like and lacks expected methods (.columns, .agg, .first, .asDict).
    pyspark.sql.utils.AnalysisException or other Spark runtime exceptions
        Propagated from Spark during query planning or execution (e.g., invalid aggregation on unsupported column types, cluster execution failures). The function does not catch Spark exceptions.

## Constraints:
Preconditions:
    - A well-formed Spark DataFrame with at least one column.
    - The caller intends the first column to be the target for numeric summarization.
Postconditions:
    - The function triggers Spark computation (agg) and returns a dictionary mapping the eight aggregation names to their computed scalar values or None.
    - The input DataFrame is not mutated.

## Side Effects:
    - Triggers Spark job execution (distributed computation) when df.agg(...) is executed.
    - No external I/O, file, or network calls beyond what Spark itself performs as part of computation.
    - No modification of global variables or the input DataFrame.

## Control Flow:
flowchart TD
    Start --> CheckColumns
    CheckColumns -->|len(df.columns) == 0| RaiseIndexError
    CheckColumns -->|len(df.columns) > 0| BuildExpr
    BuildExpr --> CallAgg
    CallAgg --> FirstRow
    FirstRow -->|Row object| AsDict
    FirstRow -->|None| RaiseAttributeError
    AsDict --> ReturnDict
    ReturnDict --> End

## Implementation recipe (step-by-step guidance to reimplement):
1. Ensure pyspark.sql.functions is accessible (commonly imported as an alias such as F) or use fully-qualified names to build aggregation expressions.
2. Read the target column name with column = df.columns[0]; guard for IndexError if df has no columns.
3. Construct an expressions list where each item is a Spark aggregation expression on the target column and aliased to the desired key:
    - mean(column).alias("mean")
    - stddev(column).alias("std")
    - variance(column).alias("variance")
    - min(column).alias("min")
    - max(column).alias("max")
    - kurtosis(column).alias("kurtosis")
    - skewness(column).alias("skewness")
    - sum(column).alias("sum")
4. Call df.agg(*expressions) to produce a single-row DataFrame with the aggregations, then call .first() to obtain the Row.
5. Convert the Row to dict with asDict() and return it.
6. Optional caller-side safety: verify the result of .first() is not None before calling asDict(); if None, return a dict with the eight keys set to None or raise a clearer exception.

## Examples (usage and expected outcomes — no source code included):
- Typical successful summary:
    - Context: first column contains numeric values [1, 2, 3].
    - Outcome: returned dict will include mean=2.0, std and variance reflecting the distribution, min=1, max=3, sum=6, and numeric kurtosis/skewness values computed by Spark.
- Empty or all-null column:
    - Context: first column has no non-null values.
    - Outcome: Spark aggregate functions produce nulls; returned dict will map the keys to None.
- Error scenarios and handling advice:
    - If df has zero columns: catch IndexError and handle as "column missing".
    - If Spark raises an execution error during aggregation: catch Spark exceptions at the pipeline level and log/handle according to your application's fault policy.
    - To avoid unexpected AttributeError when .first() returns None, check for None and fallback to a safe default mapping if needed.

## `src.ydata_profiling.model.spark.describe_numeric_spark.describe_numeric_1d_spark` · *function*

*No documentation generated.*

