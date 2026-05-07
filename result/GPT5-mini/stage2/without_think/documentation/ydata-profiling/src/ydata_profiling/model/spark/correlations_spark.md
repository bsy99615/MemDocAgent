# `correlations_spark.py`

## `src.ydata_profiling.model.spark.correlations_spark.spark_spearman_compute` · *function*

## Summary:
Call the Spark-native correlation routine to compute Spearman pairwise correlations for numeric columns and return the result as a pandas DataFrame indexed and labeled by the numeric column names.

## Description:
This function is a thin wrapper that delegates the actual work to a Spark-specific helper that computes a dense correlation matrix on the driver and then converts that matrix into a pandas.DataFrame with matching row/column labels.

Known callers within the codebase:
- No direct call sites were found in the repository memory for this exact function. It is intended for use by higher-level Spark correlation orchestration code that decides to use a native Spark backend for Spearman correlations.

Why this logic is extracted:
- Keeps backend selection and result conversion separate from the Spark wiring. The helper encapsulates Spark-specific steps (column selection, VectorAssembler and Correlation calls), while this wrapper enforces the API contract expected by the rest of the profiling code (i.e., a pandas DataFrame result).

## Args:
    config (ydata_profiling.config.Settings):
        Profiling/settings object from the host application. This wrapper does not inspect config itself but accepts it to match the higher-level API used by other correlation backends. Passing None is not supported by the static type but will only matter if callers expect config-driven behavior; the function does not read config.
    df (pyspark.sql.DataFrame):
        Spark DataFrame containing the dataset. The DataFrame must contain the columns referenced by summary; numeric columns should be numeric-compatible Spark types.
    summary (dict):
        Per-column metadata mapping column name -> column description dict. Each description must include a "type" key whose value is a string. Columns with description["type"] == "Numeric" are selected for the correlation computation. The ordering of numeric columns follows the iteration order of summary.items().

## Returns:
    pandas.DataFrame
        Square DataFrame (n x n) holding the computed Spearman correlation matrix. Rows and columns are labeled and ordered by the numeric column names returned from the Spark helper (interval_columns). Each cell (i, j) is the Spearman correlation between interval_columns[i] and interval_columns[j].

    Notes:
    - Although the function signature may be annotated with an Optional return, in normal successful execution it always returns a pandas.DataFrame. Errors raise exceptions instead of returning None.
    - If a single numeric column is present, a 1x1 DataFrame is returned.

## Raises:
    NameError:
        If the constant SPARK_CORRELATION_SPEARMAN is not defined in the module scope at runtime, evaluating the corr_type argument will raise a NameError when this function is invoked.
    Any exception propagated from _compute_spark_corr_natively:
        Typical examples include:
        - pyspark.sql.utils.AnalysisException: raised when no numeric columns are selected, a referenced column is missing in df, or df.select(*columns) fails.
        - pyspark.ml.util.IllegalArgumentException or other pyspark.ml errors: raised when VectorAssembler or Correlation.corr is given incompatible inputs or an unsupported method string.
        - Any other Spark-related runtime errors that occur during assembler.transform(...) or Correlation.corr(...).head() will propagate unchanged.

## Constraints:
Preconditions:
    - summary is a dict-like mapping whose values are dicts containing a "type" key.
    - For every column with description["type"] == "Numeric", df must contain that column and it must be numeric-compatible.
    - A SparkSession must be active and compatible with pyspark.ml.feature.VectorAssembler and pyspark.ml.stat.Correlation.

Postconditions:
    - On success, the function returns a pandas.DataFrame with both index and columns equal to the ordered list of numeric column names used in the computation; the DataFrame values are the Spearman correlation coefficients, materialized on the driver.

## Side Effects:
    - Triggers Spark jobs via the underlying helper: assembling features and computing correlations across the cluster.
    - Collects the full correlation matrix to the driver and materializes it in memory as a numpy array and then as a pandas.DataFrame; this can be memory-intensive for large numbers of numeric columns.
    - No filesystem, network, or global Python state is directly modified by this wrapper itself (side effects come from the underlying Spark calls).

## Control Flow:
flowchart TD
    A[Start: receive config, df, summary] --> B[Call _compute_spark_corr_natively(df, summary, corr_type=SPARK_CORRELATION_SPEARMAN)]
    B --> C{Does call succeed?}
    C -->|yes| D[Receive (matrix, num_cols)]
    D --> E[Convert matrix to pandas.DataFrame(index=num_cols, columns=num_cols)]
    E --> F[Return DataFrame]
    C -->|no| G[Exception propagates to caller (no return)]

## Examples:
Typical usage:
    # summary maps columns to metadata, marking numeric columns with {"type": "Numeric"}
    # config is the profiling Settings object; df is a pyspark.sql.DataFrame
    try:
        spearman_df = spark_spearman_compute(config, df, summary)
        # spearman_df is a pandas.DataFrame with rows/columns named by numeric columns
        # Access correlation between "age" and "income" as:
        corr_age_income = spearman_df.loc["age", "income"]
    except NameError:
        # SPARK_CORRELATION_SPEARMAN constant missing — ensure module-level constant is defined
        raise
    except Exception as exc:
        # Handle Spark errors such as missing columns, no numeric columns, or incompatible dtypes
        # Inspect exc (e.g., AnalysisException) to determine corrective actions
        raise

## `src.ydata_profiling.model.spark.correlations_spark.spark_pearson_compute` · *function*

## Summary:
Convert the dense numeric correlation matrix computed by the Spark-native helper into a pandas DataFrame labeled with the numeric column names so callers get a driver-resident, human-friendly correlation table.

## Description:
- Known callers:
    - Higher-level Spark correlation orchestration code within the profiling pipeline that requires a pandas DataFrame representation of Pearson correlations for reporting or downstream processing. Typically this function is invoked when the system decides to compute correlations using the Spark backend and specifically requests Pearson correlations for numeric columns.
- Responsibility boundary:
    - This function is a thin adapter: it delegates the actual Spark computation to _compute_spark_corr_natively and converts its result (a dense numeric matrix and ordered column list) into a pandas DataFrame with appropriate row/column labels. It exists to separate Spark-specific computation (handled by the helper) from data formatting and API-level return types expected by the rest of the codebase.

## Args:
    config (Settings):
        Configuration object for the profiling run. Not inspected by this function but included for API consistency with other correlation functions; it may be used by callers to decide which backend to call.
    df (pyspark.sql.DataFrame):
        Spark DataFrame containing the dataset to analyze. Must contain the columns referenced by summary. Numeric columns should be numeric Spark dtypes (or convertible by VectorAssembler) as required by the Spark helper.
    summary (dict):
        Per-column summary mapping column name -> dict. Each column dict must include a "type" key whose value is the string "Numeric" for columns to be included. The ordering of numeric columns in the resulting DataFrame follows the iteration order used by the helper when selecting numeric columns.

Notes on interdependencies:
    - This function relies on _compute_spark_corr_natively to:
        1) select numeric columns from summary,
        2) assemble features and compute the correlation matrix using Spark,
        3) return (matrix, interval_columns).
      The function expects matrix to be a 2-D numeric array-like object (e.g., numpy.ndarray) and interval_columns to be an ordered list of column names. If the helper raises, the exception propagates.

## Returns:
    pandas.DataFrame
    - A square pandas DataFrame whose rows and columns are labeled with the ordered numeric column names returned by the helper.
    - The DataFrame's values are the numeric Pearson correlation coefficients; element (i, j) corresponds to the correlation between interval_columns[i] and interval_columns[j].
    - Edge cases:
        - If exactly one numeric column is present, the returned DataFrame will be 1x1.
        - If the helper raises an exception (e.g., no numeric columns found, missing column in df, incompatible dtypes, unsupported correlation method), this function does not return a value because the exception propagates.

Important note about implementation / runtime mismatch:
    - The function's annotation and body reference pd.DataFrame (pandas alias pd). Ensure that pandas has been imported as the alias pd in the module where this function is implemented. If pandas is only imported as 'import pandas' and not as 'import pandas as pd', calling this function will raise a NameError for pd.

## Raises:
    - Any exception raised by _compute_spark_corr_natively will propagate unmodified. Common examples include:
        - pyspark.sql.utils.AnalysisException: when selected numeric columns are missing from df or selection is invalid.
        - pyspark.ml.util.IllegalArgumentException or other pyspark.ml errors: if VectorAssembler or Correlation.corr fails because of incompatible dtypes or an unsupported correlation method.
        - NameError: if pandas is not imported under the alias pd but the function refers to pd.DataFrame (module-level import mismatch).
    - The function performs no additional validation or exception handling.

## Constraints:
Preconditions:
    - summary must be a mapping where values are dicts containing a "type" key.
    - For every column labeled "Numeric" in summary, df must contain that column and it should be numeric-compatible for Spark's VectorAssembler.
    - A SparkSession must be active; the helper uses pyspark.ml APIs.
Postconditions:
    - On success, returns a pandas DataFrame created from the dense correlation matrix collected to the driver with rows/columns labeled by the numeric column names.
    - No in-place mutation of df or global state occurs.

## Side Effects:
    - Indirectly causes Spark jobs to run via the helper (vector assembly and correlation computation).
    - Materializes a potentially large correlation matrix on the driver; can increase driver memory usage substantially for many numeric columns.
    - No filesystem, network, or global-variable side effects are introduced by this wrapper itself.

## Control Flow:
flowchart TD
    Start[Start: call with config, df, summary] --> CallHelper[_compute_spark_corr_natively(df, summary, corr_type=SPARK_CORRELATION_PEARSON)]
    CallHelper --> |success| Unpack[Receive (matrix, num_cols)]
    Unpack --> BuildDF[Construct pandas DataFrame from matrix with index=num_cols and columns=num_cols]
    BuildDF --> Return[Return pandas DataFrame]
    CallHelper --> |raises exception| Propagate[Exception propagates to caller (no return)]

## Examples:
- Typical usage:
    Provide a summary mapping where numeric columns are marked as "Numeric". Call the function to obtain a labeled pandas DataFrame of Pearson correlations:
    df_result = spark_pearson_compute(config, df, summary)
    # df_result is a pandas.DataFrame whose index and columns are the numeric column names; values are Pearson coefficients

- Usage with basic error handling:
    try:
        df_result = spark_pearson_compute(config, df, summary)
    except Exception as exc:
        # Inspect exc to determine cause: no numeric columns in summary; missing df column; unsupported corr_type; or pandas alias NameError
        # Fix the issue (validate summary and df, ensure pandas alias) and retry
        raise

## `src.ydata_profiling.model.spark.correlations_spark._compute_spark_corr_natively` · *function*

## Summary:
Compute pairwise correlations for numeric columns in a Spark DataFrame using Spark MLlib, returning the dense correlation matrix collected to the driver and the ordered list of numeric column names.

## Description:
This function:
- Filters the provided DataFrame to columns marked as numeric in the provided per-column summary.
- Uses pyspark.ml.feature.VectorAssembler to assemble those numeric columns into a single vector column.
- Calls pyspark.ml.stat.Correlation.corr on the assembled vectors with the provided correlation method, collects the result to the driver, converts it to a dense 2-D array, and returns that matrix together with the ordered list of numeric columns.

Known callers within the codebase:
- No direct callers are present in this file. It is intended to be used by higher-level Spark correlation orchestration code that selects a native Spark backend for correlation computation.

Why extracted:
- Encapsulates Spark-specific steps (column selection, VectorAssembler configuration including version-dependent handleInvalid behavior, and invocation of Correlation.corr) so callers can remain backend-agnostic and avoid duplicating Spark wiring logic.

## Args:
    df (pyspark.sql.DataFrame):
        Spark DataFrame containing the data. Must contain the columns referenced by summary; numeric columns should be of numeric Spark dtypes (or convertible to numeric for VectorAssembler).
    summary (dict):
        Mapping of column name -> column description (dict). Each description must include a "type" key whose value is a string. Columns where description["type"] == "Numeric" are selected for correlation.
        Example: {"age": {"type": "Numeric"}, "gender": {"type": "Categorical"}, ...}
        Note: The function determines interval_columns by iterating over summary.items() and selecting those with type "Numeric"; the ordering of interval_columns follows that iteration order.
    corr_type (str):
        Correlation method string forwarded to Spark's Correlation.corr (commonly "pearson" or "spearman"). The string is passed verbatim to the Spark API.

## Returns:
    tuple(matrix, interval_columns)
    - matrix (2-D numpy.ndarray):
        Dense square correlation matrix whose rows and columns correspond, in order, to interval_columns. The matrix is produced by calling .toArray() on Spark's DenseMatrix result (so it is materialized on the driver).
    - interval_columns (list[str]):
        Ordered list of column names included in the matrix; ordering equals the order in which numeric columns were encountered when iterating over summary.items().

Important note about the source annotation:
- Although the function signature in the source file annotates the return type as ArrayType, the implementation actually returns a Python tuple (matrix, interval_columns). Clients should rely on the runtime behavior (tuple) when integrating.

Edge-case return behavior:
- If a single numeric column is provided, the returned matrix will be 1x1 (a single-element 2-D array).
- If an exception occurs (see Raises), no value is returned; callers must handle exceptions.

## Raises:
    - pyspark.sql.utils.AnalysisException (or similar Spark error):
        If interval_columns is empty or if df.select(*interval_columns) is passed invalid or missing column names, Spark may raise an AnalysisException or other selection-related error. The function does not validate the presence of numeric columns before selecting.
    - pyspark.ml.util.IllegalArgumentException or other pyspark.ml errors:
        If VectorAssembler receives invalid input (for example incompatible dtypes) or if Correlation.corr receives an unsupported corr_type, the underlying Spark call will raise an appropriate exception. These exceptions are not caught and will propagate to the caller.
    - Any other exception raised by Spark during transform or correlation computation will propagate.

Exact trigger conditions to watch for:
- interval_columns is empty (no "Numeric" columns in summary) — df.select(*interval_columns) or VectorAssembler creation/transform will likely fail.
- A column named in summary is not present in df — df.select will fail with an analysis/argument error.
- corr_type is unsupported by Spark's Correlation.corr — that call will raise.

## Constraints:
Preconditions:
    - summary is a dict-like mapping whose values are dicts containing a "type" key.
    - For each column marked "Numeric" in summary, df must contain that column and it should be numeric-compatible.
    - A SparkSession must be active and compatible with the VectorAssembler and Correlation APIs.
Postconditions:
    - On success, the function returns a dense correlation matrix and the list of numeric columns used (interval_columns). The returned matrix is resident on the driver.

Version-specific behavior:
    - If pyspark.__version__ >= "2.4.0", VectorAssembler is constructed with handleInvalid="skip". Otherwise the assembler is created without that argument. This affects how rows with invalid (e.g., null) values are handled during transform.

## Side Effects:
    - Launches Spark jobs: assembler.transform(...) and Correlation.corr(...) cause distributed computation; Correlation.corr(...).head() collects the result to the driver.
    - Driver memory usage: the complete matrix is materialized on the driver; large numbers of numeric columns can cause high memory usage on the driver.
    - No filesystem, network, or global state is modified directly by this function beyond Spark's internal actions.

## Control Flow:
flowchart TD
    A[Start: receive df, summary, corr_type] --> B{Build variables map from summary}
    B --> C[Filter names where type == "Numeric" -> interval_columns]
    C --> D{interval_columns non-empty?}
    D -->|no| E[Attempt to select zero columns -> Spark raises -> exception propagates]
    D -->|yes| F[df = df.select(*interval_columns)]
    F --> G[Prepare assembler_args inputCols=df.columns, outputCol='corr_features']
    G --> H{pyspark.version >= 2.4.0?}
    H -->|yes| I[assembler_args['handleInvalid']='skip']
    H -->|no| J[assembler_args unchanged]
    I --> K[assembler = VectorAssembler(**assembler_args)]
    J --> K
    K --> L[df_vector = assembler.transform(df).select('corr_features')]
    L --> M[matrix_dense = Correlation.corr(df_vector, 'corr_features', method=corr_type).head()[0].toArray()]
    M --> N[Return (matrix_dense, interval_columns)]
    E --> O[No return (exception)]

## Examples:
Simple usage:
    # Prepare a summary dict where numeric columns are marked as "Numeric"
    summary = {"age": {"type": "Numeric"}, "income": {"type": "Numeric"}, "city": {"type": "Categorical"}}
    matrix, cols = _compute_spark_corr_natively(df, summary, "pearson")
    # 'cols' may be ["age", "income"]; 'matrix' is a 2x2 numpy.ndarray where matrix[0,1] is the correlation between "age" and "income"

Usage with basic error handling:
    try:
        matrix, cols = _compute_spark_corr_natively(df, summary, "spearman")
    except Exception as exc:
        # Inspect exc to determine whether it's caused by:
        # - no numeric columns in summary
        # - a missing column in df
        # - unsupported corr_type
        # Then fix the summary or DataFrame and retry.

Implementation guidance for callers:
    - Validate that at least one numeric column exists in summary and that those columns are present in df before calling to avoid Spark selection/assembler errors.
    - For many numeric columns (large dimensionality), ensure adequate driver memory because the full matrix is collected to the driver.

## `src.ydata_profiling.model.spark.correlations_spark.spark_kendall_compute` · *function*

*No documentation generated.*

## `src.ydata_profiling.model.spark.correlations_spark.spark_cramers_compute` · *function*

*No documentation generated.*

## `src.ydata_profiling.model.spark.correlations_spark.spark_phi_k_compute` · *function*

## Summary:
Compute a Phi-k correlation matrix for a selected set of columns from a PySpark DataFrame and return it as a pd.DataFrame (or None when no meaningful computation is possible).

## Description:
This function:
- Selects eligible columns for Phi-k computation using per-column summary metadata and a configuration threshold.
- Adds a constant "groupby" column to group all rows together and registers a GROUPED_MAP pandas UDF that runs phik.phik_matrix on each worker's pandas partition.
- Applies the grouped UDF, collects the result to the driver with toPandas(), and assembles a square pd.DataFrame correlation matrix with rows and columns equal to the selected column names.

Why extracted:
- Encapsulates selection rules (numeric vs categorical handling) and Spark-specific orchestration (schema creation, GROUPED_MAP pandas UDF setup, groupby.apply, and driver-side assembly).
- Keeps heavy numeric computation (phik.phik_matrix) executed on workers while centralizing the orchestration logic for reuse and testing.

Known callers / typical usage:
- Intended to be invoked by higher-level Spark profiling or correlation pipelines after summary metadata (types and n_distinct per column) are computed.
- No explicit callers were present in the provided snapshot; typical stage: "compute per-column summary" -> call this to compute Phi-k.

## Args:
    config (Settings)
        - Required attribute used: categorical_maximum_correlation_distinct (int).
        - Purpose: maximum allowed n_distinct for non-numeric (categorical) columns to be included.
    df (pyspark.sql.DataFrame)
        - The input Spark DataFrame. Must contain the column names referenced in `summary`.
    summary (dict)
        - Mapping from column_name (str) to metadata dict that must include:
            * "type" (str) — e.g., "Numeric", "Unsupported", etc.
            * "n_distinct" (int) — number of distinct values for the column.
        - Used to compute:
            * intcols = {col | type == "Numeric" and n_distinct > 1}
            * supportedcols = {col | type != "Unsupported" and 1 < n_distinct <= threshold}
        - selcols is list(supportedcols ∪ intcols). Note: union is performed on sets, so the resulting list order is not guaranteed.

Interdependencies:
- threshold = config.categorical_maximum_correlation_distinct determines the upper bound for categorical distinct counts.
- Numeric columns with >1 distinct value (intcols) are always included regardless of threshold.
- The pandas UDF receives interval_cols=list(intcols) so numeric columns are identified to phik.phik_matrix.

## Returns:
    Optional[pd.DataFrame]
    - None: returned immediately when len(selcols) <= 1 (i.e., zero or one selectable column; no correlation matrix to compute).
    - pd.DataFrame (square): when at least two columns are selected and the Spark DataFrame has rows:
        * Index: selcols
        * Columns: selcols
        * Values: floating-point Phi-k coefficients (UDF schema uses DoubleType).
    - Empty pd.DataFrame: returned when the input Spark DataFrame contains no rows (the function constructs and returns pd.DataFrame()).

Ordering note:
- Because selcols is derived from a set union converted to a list, the ordering of index/columns in the returned pd.DataFrame can be non-deterministic; callers should re-order explicitly if a stable order is required.

## Raises:
    - pyspark.sql.utils.AnalysisException (or similar Spark error) if df.select(selcols) references missing columns.
    - Exceptions raised by Spark during groupby.apply, UDF execution, or toPandas() may propagate (e.g., serialization errors).
    - Exceptions from phik.phik_matrix (invalid inputs, unexpected dtypes) may propagate from the UDF.
    - MemoryError / OOM on the driver if toPandas() attempts to materialize a very large result.

## Constraints:
Preconditions:
    - `summary` must include entries for the expected columns with keys "type" (str) and "n_distinct" (int).
    - config.categorical_maximum_correlation_distinct should be an integer >= 1.
    - Input `df` must contain the column names referenced by selcols; otherwise df.select will error.

Postconditions:
    - No global state is mutated.
    - If a pd.DataFrame is returned (non-None), it is a square matrix of floats indexed and columned by selcols.

## Side Effects:
    - Executes Spark transformations and an action (groupby.apply and toPandas()) causing distributed computation.
    - Adds a temporary column named "groupby" with constant value 1 to the selected DataFrame to enable GROUPED_MAP application.
    - Calls phik.phik_matrix on worker-side pandas DataFrames.
    - Collects results to the driver using toPandas(), which can significantly increase driver memory usage.
    - Does not write to files, networks, or external persistent stores itself.

## Control Flow:
flowchart TD
    A[Start: receive config, df, summary]
    A --> B[threshold = config.categorical_maximum_correlation_distinct]
    B --> C[Compute intcols: Numeric cols with n_distinct > 1]
    B --> D[Compute supportedcols: type != 'Unsupported' and 1 < n_distinct <= threshold]
    C --> E[selcols = list(supportedcols ∪ intcols)]
    D --> E
    E --> F{len(selcols) <= 1 ?}
    F -- Yes --> G[Return None]
    F -- No --> H[Create groupby_df = df.select(selcols).withColumn("groupby", lit(1))]
    H --> I[Build output_schema: DoubleType field per selcol]
    I --> J[Register spark_phik pandas_udf (GROUPED_MAP) that calls phik.phik_matrix(df=pdf, interval_cols=list(intcols))]
    J --> K{groupby_df.head(1) has rows ?}
    K -- No --> L[Return empty pd.DataFrame()]
    K -- Yes --> M[Apply grouped UDF and collect: groupby_df.groupby("groupby").apply(spark_phik).toPandas()]
    M --> N[Use returned .values to build pd.DataFrame(values, columns=selcols, index=selcols)]
    N --> O[Return pd.DataFrame of Phi-k correlations]

## Examples (usage described in prose):
Normal usage:
- After computing per-column summaries (type and n_distinct), create or use a Settings-like object with categorical_maximum_correlation_distinct set (for example, 50).
- Ensure the Spark DataFrame `df` contains the columns referenced in the summary.
- Call the function with (config, df, summary).
- If it returns None, there were zero or one eligible columns (no matrix computed).
- If it returns an empty pd.DataFrame, the input Spark DataFrame had zero rows.
- Otherwise the returned pd.DataFrame is a square Phi-k correlation matrix; reorder its rows/columns if a deterministic order is required.

Error handling guidance:
- Wrap the call in try/except to handle pyspark.sql.utils.AnalysisException, Spark runtime exceptions, and phik errors if necessary.
- To avoid driver OOM when many columns are selected, consider reducing selcols (filter columns or sample rows) before invoking this function.

Implementation notes for reimplementation:
- The function creates a GROUPED_MAP pandas UDF with an explicit StructType schema where each field is DoubleType; the UDF receives a pandas DataFrame and returns the DataFrame produced by phik.phik_matrix.
- The function groups all rows by a constant "groupby" column (value 1) so the UDF is applied once over the entire dataset; it then collects the UDF results to the driver with toPandas() and reconstructs the final pd.DataFrame correlation matrix using .values and the selcols list for both columns and index.

