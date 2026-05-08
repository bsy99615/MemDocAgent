# `dataframe_spark.py`

## `src.ydata_profiling.model.spark.dataframe_spark.spark_check_dataframe` · *function*

## Summary:
Verify that the provided object is a pyspark DataFrame and emit a runtime warning if it is not. The function performs only this check and returns None.

## Description:
Known callers:
- No direct callers were found in the repository graph for this function. It is intended as a small, reusable runtime guard to be invoked before Spark-specific processing (for example, prior to calling Spark preprocessing or profiling routines).

Responsibility and rationale for being a separate function:
- Encapsulates a single responsibility: a uniform isinstance check against pyspark.sql.DataFrame and a single, consistent warning message when the check fails.
- Centralizes the check so that callers do not duplicate the exact isinstance logic or warning text, making future changes (e.g., raising an exception instead of warning, or changing the message) simple and localized.

## Args:
    df (DataFrame): The value expected to be an instance of pyspark.sql.DataFrame (as imported at module level: from pyspark.sql import DataFrame).
        - Required; no default.
        - Any Python object may be passed; the function will test whether it is an instance of DataFrame.
        - There are no other parameters and no interdependencies.

## Returns:
    None

    - The function does not return any value. Its observable effect is either no action (if the input is a DataFrame) or emission of a warning (if it is not).

## Raises:
    None

    - The function body contains no raise statements. It will not raise exceptions itself.
    - Note: if this module failed to import because pyspark is not installed, the function would not be available — that import-time failure is outside this function's body.

## Constraints:
Preconditions:
    - The module must be importable so that DataFrame (pyspark.sql.DataFrame) is defined at module scope.
    - Callers should not rely on this function to enforce type safety; it only warns and does not stop execution.

Postconditions:
    - The input object is not mutated.
    - If the input was not a DataFrame, a warning with the exact message "df is not of type pyspark.sql.dataframe.DataFrame" has been emitted via the warnings module; otherwise, no warning is emitted by this function.

## Side Effects:
    - Emits a runtime warning using warnings.warn(...) when the input is not an instance of pyspark.sql.DataFrame. The emitted text is exactly:
      "df is not of type pyspark.sql.dataframe.DataFrame"
    - No file, network, stdout, database, cache, or global-variable mutation occurs.
    - Callers can control, capture, or suppress the warning via the standard warnings API (for example, using warnings.filterwarnings or warnings.catch_warnings) — the function itself does not provide controls for that.

## Control Flow:
flowchart TD
    Start --> CheckType{isinstance(df, DataFrame)?}
    CheckType -- Yes --> NoAction[No warning emitted]
    NoAction --> End[Return None]
    CheckType -- No --> EmitWarn[Call warnings.warn("df is not of type pyspark.sql.dataframe.DataFrame")]
    EmitWarn --> End

## Examples (usage patterns described in prose):
- Happy path:
  - Caller passes a pyspark.sql.DataFrame instance. The function performs the isinstance check and returns None without emitting any warnings. Use this as a non-intrusive guard before Spark-specific operations.

- Non-DataFrame input:
  - Caller passes an object that is not a pyspark DataFrame (e.g., a pandas DataFrame, list, dict, or None). The function calls warnings.warn with the exact message above and then returns None. Execution continues; callers must handle the fact that the object is not a DataFrame if necessary.

- Controlling the warning from caller code:
  - If a caller wants to suppress or capture the advisory message, they should use the standard warnings API (for example, apply a filter to ignore the message or use a context manager to capture warnings) around the call to this function. The function itself does not change warning filters or logger configuration.

## `src.ydata_profiling.model.spark.dataframe_spark.spark_preprocess` · *function*

## Summary:
Intended to filter out Spark DataFrame columns whose Spark data type string begins with "MapType"; however, as implemented it will raise a NameError when any MapType columns are detected because the warning call uses an undefined variable. If no MapType columns are present, it returns the original DataFrame unchanged.

## Description:
This function provides a small Spark-specific preprocessing step that detects columns whose dataType string starts with "MapType" and — in the intended design — returns a DataFrame selecting only the non-MapType columns. The detection is implemented by an inner helper that inspects the string form of a column's dataType via df.select(column).schema[0].dataType.

Important implementation note drawn from the source:
- The function currently calls warnings.warn(f) when MapType columns are found. The variable f is not defined anywhere in the function, so Python will raise NameError before the function can compute and return the filtered DataFrame. Therefore, in the current source the filtering path does not complete successfully.

Known callers:
- No direct callers were found in the available repository scan. Conceptually, this function is intended to be invoked as the Spark branch of the preprocessing step in the profiling pipeline prior to downstream profiling computations.

Why this is a separate function:
- Encapsulates Spark-specific heuristics (MapType column removal) away from higher-level pipeline code.
- Provides an isolated place to adjust detection rules or add config-driven behavior in the future.
- Makes unit testing and maintenance of Spark-specific preprocessing easier.

Additional note about imports:
- The module imports check_dataframe and preprocess from ydata_profiling.model.dataframe, but these imports are not used within this function's body.

## Args:
    config (ydata_profiling.config.Settings):
        - Purpose: configuration object for preprocessing.
        - Current behavior: accepted but unused in the implementation; no properties are read or validated.
        - Allowed values: any Settings instance (function does not inspect it).

    df (pyspark.sql.DataFrame):
        - Purpose: the Spark DataFrame to examine and possibly filter.
        - Requirements:
            * Must expose df.columns (iterable of column names).
            * df.select(column_name) must return a DataFrame whose .schema is indexable (schema[0]) and whose schema[0].dataType can be stringified.
        - Notes: The function uses df.select(column).schema[0].dataType for type detection and thus relies on Spark schema behavior.

## Returns:
    pyspark.sql.DataFrame
    - If df contains no MapType columns (per the detection rule), returns the original df unchanged.
    - If df contains one or more MapType columns, the intended return value is a DataFrame selecting only non-MapType columns (df.select(*columns_to_keep)). However, due to the undefined variable in the warnings.warn call, the function will raise NameError before returning in that case (see Raises).
    - Edge cases:
        * If all columns are MapType, the code would compute columns_to_keep as an empty list and attempt df.select() with zero columns — behavior depends on Spark version (may yield an empty-schema DataFrame or produce an error). The current source does not guard against this.

## Raises:
    NameError
        - Condition: When one or more MapType columns are detected, the function executes warnings.warn(f). Because f is undefined in the function scope, Python raises NameError and aborts execution before returning the filtered DataFrame.

    AttributeError
        - Possible when df lacks .select or .columns attributes (this will propagate from attempting to access those).

    IndexError
        - Possible when df.select(column).schema is empty or indexing [0] is invalid (propagates from schema access).

    Any pyspark-related exceptions
        - Any exceptions thrown by df.select(...) or schema/dataType access will propagate.

## Constraints:
Preconditions:
    - Caller must pass a valid pyspark.sql.DataFrame-like object with accessible columns and schema introspection as described above.
    - pyspark must be available in the runtime and the DataFrame must support .select and .schema operations used in the function.

Postconditions:
    - If the function returns normally (only possible when no MapType columns are detected in the current source), the returned DataFrame equals the input df (identity preserved).
    - The function does not mutate the input DataFrame in-place.

## Side Effects:
    - Intended: emit a runtime warning (via warnings.warn) when MapType columns are detected.
    - Actual (current source): the warnings.warn call uses an undefined variable and will raise NameError instead of emitting a warning, so no warning is emitted and an exception is raised.
    - No I/O (file, network) or global state mutation is performed by this function.

## Control Flow:
flowchart TD
    Start([Start])
    Detect["Detect MapType columns using _check_column_map_type for each df.columns"]
    HasMap{Are MapType columns present?}
    Warn["Call warnings.warn(f)  (undefined 'f' in source)"]
    NameError[/NameError raised due to undefined 'f'/]
    ComputeKeep["Compute columns_to_keep = non-MapType columns"]
    ReturnFiltered["Return df.select(*columns_to_keep)"]
    ReturnOriginal["Return original df"]
    Start --> Detect --> HasMap
    HasMap -- Yes --> Warn --> NameError
    NameError -.-> EndErr([Exception raised])
    HasMap -- No --> ReturnOriginal --> EndOK([Return original df])
    NameError --- ComputeKeep
    ComputeKeep --> ReturnFiltered --> EndFiltered([Return filtered df])

Notes:
- The actual runtime path for "HasMap == Yes" leads to NameError before the filtered DataFrame is returned. The flow shows the intended subsequent steps after the warning call, but the current source prevents reaching them.

## Examples (described in prose):
1) No MapType columns (actual working path):
    - Input: Spark DataFrame whose each column's schema[0].dataType string does not start with "MapType".
    - Outcome: spark_preprocess returns the same DataFrame object unchanged.

2) With MapType columns (actual behavior of provided source):
    - Input: Spark DataFrame with one or more MapType columns.
    - Outcome: A NameError is raised due to the undefined variable used in warnings.warn(f), so the caller receives an exception instead of a filtered DataFrame.

3) Recommended usage after fixing the warning call (implementation suggestion):
    - Modify the warnings.warn call to include a concrete message (e.g., warnings.warn(f"Removing MapType columns: {columns_to_remove}")).
    - Consider inspecting df.schema (StructType) once and iterating its fields for efficiency instead of calling df.select(column) for each column.
    - Add a guard for the case where columns_to_keep is empty (all columns are MapType) to define explicit behavior (e.g., return an empty-dataframe with documented schema or raise a ValueError).

