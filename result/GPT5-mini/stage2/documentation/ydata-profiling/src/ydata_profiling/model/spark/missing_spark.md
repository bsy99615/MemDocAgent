# `missing_spark.py`

## `src.ydata_profiling.model.spark.missing_spark.MissingnoBarSparkPatch` · *class*

## Summary:
A small wrapper object that adapts a PySpark DataFrame to a minimal pandas-like missing-value API expected by downstream code that calls df.isnull().sum() and len(df).

## Description:
This class exists to provide a tiny compatibility shim so code written for pandas-style DataFrames (which commonly call df.isnull().sum() and len(df)) can interoperate with a PySpark DataFrame without modifying the caller. Typical callers are visualization or missing-value analysis utilities that expect df.isnull() to return an object exposing a sum() method and expect len(df) to return the dataset size.

The wrapper is not a full replacement of pandas functionality — it only implements the narrow interface required by the downstream code:
- isnull() returns an object on which .sum() can be invoked.
- sum() returns the underlying PySpark DataFrame previously supplied to the wrapper.
- __len__ returns the original dataset size supplied at construction, or None if not provided.

This class is intended to be constructed at the place where a pandas-like DataFrame is expected, then used in place of the result of a pandas DataFrame's isnull() call (commonly via a monkey-patch or adapter layer).

Responsibility boundary:
- The class does not compute or transform missing-value summaries itself.
- It does not validate DataFrame column membership or compute column-wise null counts.
- It only reliably preserves and returns references given at construction (df, columns, original_df_size).

## State:
Attributes (public):
- df (pyspark.sql.DataFrame)
    - Type: DataFrame
    - Meaning: The underlying PySpark DataFrame that should be returned by sum().
    - Invariants: The attribute holds the same object reference passed to __init__. The class does not mutate this object.
- columns (Optional[List[str]])
    - Type: list of strings or None
    - Meaning: Optional list of column names the caller may have requested to consider; stored for reference by the caller or external utilities.
    - Valid values: None or list[str]. No validation performed on contents.
- original_df_size (Optional[int])
    - Type: int or None
    - Meaning: The length (number of rows) of the dataset as known outside of this wrapper. Returned by __len__.
    - Valid values: None or non-negative integer (the class does not enforce non-negativity, but callers should pass a non-negative int).

Class invariants:
- After construction, attributes df and columns remain as assigned; methods rely only on those stored values.
- __len__ returns exactly original_df_size (which may be None).

## Lifecycle:
Creation:
- Instantiate by calling MissingnoBarSparkPatch(df, columns=None, original_df_size=None)
- Required argument:
    - df: a pyspark.sql.DataFrame instance (no runtime type check is performed by the class).
- Optional arguments:
    - columns: list[str] or None; default None.
    - original_df_size: int or None; default None.

Usage (typical sequence):
1. Create the wrapper with the PySpark DataFrame and optional metadata.
2. Call isnull() on the wrapper instance to obtain an object that exposes sum().
    - In this implementation, isnull() returns the wrapper instance itself.
3. Call sum() on the object returned by isnull() to retrieve the underlying DataFrame. sum() returns the stored df attribute.
4. Use len(wrapper_instance) to retrieve the original_df_size value (or None if not set).

Sequencing requirements:
- No strict ordering is enforced by the class. isnull() then sum() is the intended usage pattern.
- __len__ can be invoked at any time after construction.

Destruction:
- No cleanup, context management, or resource finalization is required by this class.
- It does not hold external resources beyond the references provided at construction; normal garbage collection semantics apply.

## Method Map:
flowchart LR
    A[constructor: MissingnoBarSparkPatch(df, columns, original_df_size)] --> B[isnull() -> returns self]
    B --> C[sum() -> returns df (the stored DataFrame)]
    A --> D[__len__() -> returns original_df_size]

## Methods (behavioral summary)
- __init__(df: DataFrame, columns: List[str] | None = None, original_df_size: int | None = None)
    - Stores the provided arguments on the instance with identical names.
    - No data validation or transformation is performed.
- isnull() -> Any
    - Returns self. Purpose: provide an object that exposes a sum() method to mimic pandas-like chaining (df.isnull().sum()).
- sum() -> DataFrame
    - Returns the stored df attribute (the underlying PySpark DataFrame).
    - Intended to serve as the "unwrapped" result for downstream usage after the isnull()/sum() call sequence.
- __len__() -> Optional[int]
    - Returns original_df_size exactly as supplied at construction (may be None).

## Raises:
- The class itself does not raise any exceptions explicitly.
- Potential runtime errors are limited to those that arise from misuse of the stored df object by callers (for example, if callers assume df has specific columns or schema). The constructor performs no type checks; passing an object that is not a pyspark.sql.DataFrame will not raise at construction time but may cause errors later when callers operate on the returned value.

## Example:
- Intent: allow code that expects pandas behavior for missing-value inspection to run against a PySpark DataFrame without changing the caller.
- Typical usage pattern (expressed as prose and a single-line instantiation):
    1. Instantiate the adapter with a PySpark DataFrame and known dataset length:
       patch = MissingnoBarSparkPatch(df, columns=['col1','col2'], original_df_size=12345)
    2. The downstream code expects to do: result = patch.isnull().sum()
       - patch.isnull() returns the same patch object.
       - calling .sum() returns the original PySpark DataFrame passed in as df.
    3. Getting the dataset length from the wrapper: n = len(patch)  -> yields 12345

Notes and recommendations:
- Because this class is intentionally minimal, any caller that needs accurate missing-value counts or column-level summaries must compute them using PySpark APIs separately; this wrapper only provides compatibility for call sites that expect a pandas-style isnull().sum() expression to be present.
- If you require validation (e.g., verifying df is a DataFrame or that original_df_size is non-negative), perform those checks before or after constructing the wrapper; the class will accept and retain whatever values are passed in.

### `src.ydata_profiling.model.spark.missing_spark.MissingnoBarSparkPatch.__init__` · *method*

## Summary:
Store the provided Spark DataFrame and optional metadata (selected columns and original row count) on the instance so the object can act as a lightweight pandas-like wrapper for missingness operations.

## Description:
This constructor initializes the minimal state required for the wrapper object used by the class's patched methods (isnull, sum, and __len__). It assigns the provided arguments directly to instance attributes without validation or transformation.

Known/expected usage context:
- The instance is intended to be created when adapting a pyspark.sql.DataFrame into a minimal pandas-like interface required by missingness visualization or analysis utilities. For example, code that needs to call wrapper.isnull().sum() or len(wrapper) on a Spark-backed dataset would construct this object first.
- Lifecycle stage: called at the moment of adapting/wrapping a Spark DataFrame, before invoking the wrapper's isnull(), sum(), or __len__ methods.

Why this is a separate method:
- Separating initialization keeps state setup explicit and isolated from the behavior implemented in isnull, sum, and __len__. The other methods read these attributes and rely on them being present.

## Args:
    df (pyspark.sql.DataFrame):
        The Spark DataFrame to wrap. Required; stored as-is on self.df. No copying or type checking is performed by this constructor.
    columns (List[str] | None, optional):
        Optional list of column names to indicate which columns operations should consider. If None, no column restriction is recorded. Default: None.
    original_df_size (int | None, optional):
        Optional integer representing the original number of rows in the DataFrame. Stored on self.original_df_size and returned by __len__ as-is. If None, __len__ will return None. Default: None.

## Returns:
    None
    The constructor does not return a value; it initializes instance attributes self.df, self.columns, and self.original_df_size.

## Raises:
    This constructor contains no explicit raise statements and does not perform type validation.
    - If incorrect types are supplied (for example, a non-DataFrame for df), subsequent method calls that assume the correct types may raise errors elsewhere.

## State Changes:
    Attributes READ:
        None — the constructor does not read existing instance attributes.
    Attributes WRITTEN:
        self.df (set to the df argument)
        self.columns (set to the columns argument)
        self.original_df_size (set to the original_df_size argument)

## Constraints:
    Preconditions:
        - None enforced by this constructor. Callers are responsible for providing appropriate argument types if downstream methods expect them.
    Postconditions:
        - After construction, the instance has attributes self.df, self.columns, and self.original_df_size equal to the passed arguments (which may be None).
        - The other methods in this class can access these attributes; specifically, isnull() and sum() operate conceptually on self.df, and __len__ returns self.original_df_size.

## Side Effects:
    - No I/O, logging, or external calls are performed.
    - Only mutation is assigning attributes on self; no global state is modified.

## Minimal usage example:
    # Given a pyspark.sql.DataFrame `df_spark` and an optional columns list:
    wrapper = MissingnoBarSparkPatch(df=df_spark, columns=['a', 'b'], original_df_size=1000)
    # Downstream expectations (defined by other methods of this class):
    wrapper.isnull().sum()   # isnull returns self; sum returns the wrapped DataFrame (self.df)
    len(wrapper)             # returns 1000 (value stored in original_df_size)

### `src.ydata_profiling.model.spark.missing_spark.MissingnoBarSparkPatch.isnull` · *method*

## Summary:
Returns the wrapper instance unchanged to support pandas-like chaining (e.g., calling .isnull().sum()) so that a subsequent .sum() call on the returned object is routed to the wrapper's implementation.

## Description:
This method exists solely to mimic the behavior of pandas DataFrame.isnull() in the Spark wrapper used by the missingness visualisation pipeline. In this project the wrapper implements a .sum() method that returns the unwrapped Spark DataFrame; returning self here makes expressions like wrapper.isnull().sum() evaluate to the wrapped DataFrame.

Known callers and lifecycle stage:
- No concrete call sites were retrieved from the local code during documentation generation. Conceptually, it is invoked during missingness computations and visualisation code that expects pandas-like semantics (i.e., code that calls DataFrame.isnull().sum() to compute counts of missing values). It is therefore called at the data-analysis stage when computing missing-value summaries prior to plotting.

Why this is a separate method:
- It is a tiny adapter to preserve pandas-like chaining semantics without modifying the calling code. Keeping it as a distinct method makes the intention explicit (provide an isnull() hook) and isolates the compatibility shim from the .sum() implementation.

## Args:
- None

## Returns:
- MissingnoBarSparkPatch (self)
  - The method returns the same wrapper instance on which it was called. The function signature uses a generic Any return type, but the concrete returned value is self (the MissingnoBarSparkPatch instance).
  - Typical usage: wrapper.isnull().sum() — the .sum() call is resolved by the wrapper.

## Raises:
- None. This method performs no validation and does not raise exceptions.

## State Changes:
- Attributes READ: None (the method body does not access any self attributes).
- Attributes WRITTEN: None (the method does not modify any self attributes).
- Note: Returning self does not mutate the object.

## Constraints:
- Preconditions:
  - The wrapper instance (self) must be a valid, initialized MissingnoBarSparkPatch object (i.e., __init__ has been called so attributes like self.df exist). Although this method does not access those attributes, the surrounding code expects the wrapper to be properly constructed.
- Postconditions:
  - The method returns the identical object reference passed as self.
  - No attributes on self are changed.

## Side Effects:
- None. The method does not perform I/O, external calls, or mutate objects outside of returning the reference to self.

### `src.ydata_profiling.model.spark.missing_spark.MissingnoBarSparkPatch.sum` · *method*

## Summary:
Return the underlying Spark DataFrame held by the patch object so callers that expect DataFrame-like `.isnull().sum()` behaviour receive the original DataFrame.

## Description:
This method is part of a small patch class that adapts a pyspark DataFrame to a pandas-like missingness API. The typical call pattern that reaches this method is:
- Caller: code that calls df.isnull().sum() on a Spark DataFrame that has been wrapped by MissingnoBarSparkPatch.isnull(), where isnull() returns the patch object so that subsequent .sum() calls invoke this method.
Lifecycle/context: invoked during missingness computation or visualization pipelines when the code attempts to compute per-column null counts using a pandas-style chain (isnull().sum()). Implemented as a separate method to clearly encapsulate the unwrapping behaviour (returning the original DataFrame) and to keep the isnull() shim minimal and easily testable.

## Args:
    self: MissingnoBarSparkPatch
        - Implicit reference to the instance. No additional parameters.

## Returns:
    pyspark.sql.DataFrame
        - The exact object stored in self.df is returned unchanged.
        - Possible values: a valid Spark DataFrame instance, or whatever object was provided to the constructor (if an invalid value was passed).
        - Edge case: if self.df is None (or not a DataFrame), None (or that object) is returned; the method does not coerce or validate the type.

## Raises:
    - This method does not explicitly raise exceptions.
    - Indirect exceptions may occur if consumers assume a DataFrame and then call DataFrame-only methods on the returned object; those exceptions originate from the consumer code, not from this method.

## State Changes:
    Attributes READ:
        - self.df
    Attributes WRITTEN:
        - None (the method does not modify any attributes)

## Constraints:
    Preconditions:
        - The instance must have been initialized such that self.df exists (the constructor sets this attribute).
        - Callers expecting DataFrame semantics should ensure the wrapped object is actually a pyspark.sql.DataFrame.
    Postconditions:
        - The method returns the same object referenced by self.df and leaves the instance state unchanged.

## Side Effects:
    - None. The method performs no I/O, logging, or external service calls and does not mutate objects outside of returning the stored reference.

### `src.ydata_profiling.model.spark.missing_spark.MissingnoBarSparkPatch.__len__` · *method*

## Summary:
Return the stored original number of rows so the object participates in Python's sizing protocol.

## Description:
Implements the sizing protocol (__len__) to allow built-in len() and other consumers that query object length to retrieve the preserved original dataframe size. This is useful when the patch object proxies for a DataFrame in code paths that expect a sized container.

Known callers and typical context:
- Invoked implicitly by built-in len(instance).
- Typically called by any code that treats this object as a sized container (for example, visualization or reporting code that queries the number of rows). No specific in-class callers are defined.

Why this is a separate method:
- Providing __len__ adheres to Python's standard protocol for sized objects and keeps callers agnostic to whether they are dealing with a real DataFrame or this patch object. Encapsulating access to original_df_size in __len__ avoids duplicating attribute access logic throughout the codebase.

## Args:
None.

## Returns:
Optional[int]
- The current value of self.original_df_size.
- If original_df_size was set during initialization, an int is returned (typically a non-negative integer representing row count).
- If original_df_size was left unset, None is returned.

## Raises:
- None explicitly raised by this method.
- Note: If the instance lacks the attribute original_df_size (which contradicts the class initializer contract), Python will raise AttributeError when the attribute is accessed. That AttributeError is not raised by this method's logic but by attribute resolution.

## State Changes:
Attributes READ:
- self.original_df_size

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- The instance should have been constructed with the original_df_size attribute present (the class __init__ sets original_df_size to the provided value or None).
- When used as a row count, original_df_size is expected to be an integer (commonly non-negative).

Postconditions:
- The method does not modify the object state.
- The return value equals the value of self.original_df_size at call time (may be None).

## Side Effects:
- None. The method performs no I/O, does not call external services, and does not mutate objects outside self.

## Typical usage note:
- Use len(patch_instance) to obtain the preserved row count; this call is equivalent to accessing patch_instance.original_df_size but uses the standard sizing protocol so external code need not rely on attribute access.

## `src.ydata_profiling.model.spark.missing_spark.spark_missing_bar` · *function*

## Summary:
Compute per-column counts of missing (null or NaN) values from a PySpark DataFrame and delegate rendering of a missing-values bar chart to the visualisation helper, returning the serialized image string produced by the visualiser.

## Description:
This function runs a PySpark aggregation to count missing entries (null or NaN) for every column in the provided DataFrame, converts the aggregated single-row result to a pandas object, and passes those per-column counts to the plotting helper to produce an embeddable image string (SVG/PNG data URI, depending on the visualiser).

Known callers within the codebase:
- No direct callers were discovered in the provided snapshot. Intended usage is within the report-generation pipeline when generating the "missing data" visualization for a Spark DataFrame.

Typical trigger/context:
- Called when a report or profile needs a missing-values bar chart for a dataset that is stored as a PySpark DataFrame. This isolates the PySpark aggregation logic from plotting code.

Responsibility boundary:
- This function is responsible only for:
  - computing per-column missing-value counts on a PySpark DataFrame (null OR NaN),
  - converting the aggregated counts to a pandas-compatible structure,
  - calling the visualisation function plot_missing_bar and returning its serialized result.
- It does not perform any plotting itself, nor does it attempt to manage figure serialization — that is delegated to plot_missing_bar.

Why extracted:
- Aggregation using PySpark (server-side) is different from in-memory pandas operations; extracting this logic keeps Spark-specific code separate from generic plotting code and allows the visualisation helpers to remain DataFrame-agnostic.

## Args:
    config (Settings):
        - Type: Settings (repository configuration object).
        - Purpose: Supplies plotting/rendering configuration used by the visualisation helper. The function forwards config to plot_missing_bar without reading specific attributes itself.
        - Constraints: Treated as an opaque configuration object here. The function will pass it through; missing attribute values are handled by the plotting helper.

    df (pyspark.sql.DataFrame):
        - Type: PySpark DataFrame (from pyspark.sql).
        - Purpose: Source dataset whose per-column missing (null or NaN) counts will be computed.
        - Requirements:
            * Must have attribute .columns (iterable of column names).
            * Must support df.agg(...) with column expressions built by pyspark.sql.functions.
            * Must support df.count() returning integer row count.
        - Interdependencies:
            * The function uses pyspark.sql.functions.isnull and isnan combined with when/count; behaviour of isnan depends on column types (numeric vs non-numeric). Non-numeric columns may not be meaningful for isnan.

## Returns:
    str
    - What it represents: The serialized image string produced by plot_missing_bar. In the repository this is the same format returned by the visualisation helper (commonly an SVG XML string or a data URI for a raster image).
    - Possible return shapes:
        * Normal case: a non-empty string containing serialized plot (e.g., SVG text or "data:image/png;base64,...").
        * Edge cases:
            - If the underlying visualiser chooses to return an empty string for empty input, this function will return that empty string.
            - If DataFrame has 0 columns, behavior follows PySpark's agg/toPandas chain (may raise or return an empty pandas object); the function will forward whatever plot_missing_bar returns or let exceptions propagate.
            - If DataFrame has a single column, the code uses toPandas().squeeze(axis="index") which can produce a scalar (int) instead of a pandas Series; that scalar will be passed into plot_missing_bar as the "notnull_counts" argument (plotting helper may accept or coerce it).

## Raises:
    - Any exceptions propagated from PySpark operations:
        * Py4JJavaError / pyspark.sql.utils.AnalysisException: if aggregation expressions are invalid for column types or columns are missing.
        * ValueError or TypeError originating from toPandas() conversion or from plot_missing_bar if it validates its inputs strictly.
    - MemoryError / OOM: unlikely here because only an aggregation result (one row) is collected to the driver via toPandas(), but if the number of columns is extremely large, converting the aggregated row to pandas could be heavy.
    - No explicit raises are thrown by this function itself; it does not validate inputs beyond relying on the called APIs — callers should be prepared to catch the above exceptions.

## Constraints:
    Preconditions:
    - A running Spark session with a valid pyspark.sql.DataFrame.
    - The DataFrame must expose a .columns iterable and support aggregation expressions used here.
    - The environment must have pandas and Matplotlib/visualisation dependencies available because plot_missing_bar will be invoked.

    Postconditions:
    - The function does not mutate the input DataFrame (df) in place.
    - The function returns the exact string returned by plot_missing_bar (which should be a serialized image string).
    - Any heavy computation is triggered on the Spark cluster (via df.agg(...)), and only the small aggregated result is collected to the driver.

## Side Effects:
    - Triggers a Spark aggregation job (df.agg(...)) and then collects the aggregated single-row result to the driver via toPandas(), which executes compute and network traffic.
    - No file I/O or external network calls are performed by this function directly.
    - Downstream plotting (plot_missing_bar) may create Matplotlib figures; resource cleanup is the responsibility of the visualiser (not this function).

## Control Flow:
flowchart TD
    Start[Start: spark_missing_bar(config, df)] --> BuildExpr[Build per-column when(isnull OR isnan) expressions]
    BuildExpr --> Agg[Run df.agg(*expressions)]
    Agg --> ToPandas[Collect the single-row result to driver via .toPandas()]
    ToPandas --> Squeeze[Squeeze axis='index' (possible Series or scalar)]
    Squeeze --> CallPlot[Call plot_missing_bar(config, notnull_counts=data_nan_counts, columns=df.columns, nrows=df.count())]
    CallPlot --> Return[Return string from plot_missing_bar]
    Return --> End[End]

## Examples:
- Typical usage in a report pipeline:
    try:
        img_str = spark_missing_bar(config, spark_df)
        if img_str:
            # embed img_str into HTML report (SVG or data URI)
            embed_in_report(img_str)
        else:
            # visualiser returned empty string — skip embedding
            skip_plot()
    except Exception as exc:
        # handle or log visualization failure without crashing full report generation
        logger.exception("Failed to create missing-values bar plot for Spark DataFrame: %s", exc)
        # optionally fall back to a textual summary or a placeholder image

- Notes on single-column DataFrame:
    # If df has only one column, the aggregated pandas result may be a scalar (int).
    # The visualiser might expect an indexable mapping (Series/list). If you need to ensure a Series:
    data_nan_counts = (
        df.agg(
            *[F.count(F.when(F.isnull(c) | F.isnan(c), c)).alias(c) for c in df.columns]
        )
        .toPandas()
        .squeeze(axis="index")
    )
    # If this yields a scalar, wrap it before calling spark_missing_bar:
    if isinstance(data_nan_counts, (int, float)):
        # convert to a mapping with the single column name (handled internally by the visualiser in many cases)
        data_nan_counts = pd.Series({df.columns[0]: int(data_nan_counts)})

Notes:
- The function counts missing entries per column (null OR NaN). The naming of the visualiser parameter is not changed by this function — the computed "missing counts" are forwarded as the notnull_counts parameter name in the call to plot_missing_bar, matching the repository's current call pattern.
- Because the function uses toPandas() on a single-row aggregation, it is typically safe memory-wise (collected payload size scales with number of columns, not rows). Nonetheless, extremely wide DataFrames (very large number of columns) may require caution.

## `src.ydata_profiling.model.spark.missing_spark.spark_missing_matrix` · *function*

## Summary:
Adapt a PySpark DataFrame for the plotting utilities (by wrapping it), execute a Spark row-count, and return the missing-value matrix plot artifact as a string.

## Description:
This function performs three concise responsibilities in sequence:
1. Executes a Spark action to count rows of the provided DataFrame.
2. Wraps the original DataFrame with MissingnoBarSparkPatch to provide a minimal pandas-like compatibility surface expected by downstream plotting code.
3. Calls the plotting utility plot_missing_matrix with the wrapper's columns, the wrapper's notnull values, and the wrapper's length, then returns the resulting plot string.

Key observed call sequence in the implementation:
- The original DataFrame's count is obtained by calling df.count() inside the wrapper construction.
- The variable df is reassigned to the wrapper instance returned by MissingnoBarSparkPatch.
- plot_missing_matrix is called with:
    * config (Settings)
    * columns = df.columns  (the wrapper's stored columns)
    * notnull = df.notnull().values
    * nrows = len(df)  (uses the wrapper's __len__ which returns original_df_size)

Why this function exists separately:
- It centralises Spark-specific adaptation and the single Spark action (count) so higher-level report-generation code can remain dataframe-agnostic and need not duplicate wrapper/plot invocation logic.

Known callers:
- Higher-level profiling/report generation routines that request a missing-value matrix plot when the dataset is provided as a pyspark.sql.DataFrame.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Purpose: Controls styling and plotting parameters used by plot_missing_matrix.
        - Constraint: Must include the configuration keys referenced by plot_missing_matrix and nested utilities (for example, html.style.primary_colors and plot.missing.force_labels). Missing or malformed configuration fields will cause errors inside the plotting code.

    df (DataFrame)
        - Type: pyspark.sql.DataFrame (or an object exposing an equivalent API)
        - Purpose: The dataset to visualise.
        - Required attributes/methods before calling:
            * .columns — iterable/list of column names.
            * .count() — Spark action returning an integer row count.
        - After wrapping: the function expects the final df object to provide:
            * df.notnull().values — an array-like boolean mask or an object exposing a .values attribute that is array-like, suitable for plot_missing_matrix.
            * len(df) — wrapper.__len__ is expected to return the previously computed row count.

Interdependencies:
- The row count is computed once by df.count() and passed into the wrapper as original_df_size; len(df) used later is therefore expected to be cheap (no additional Spark action).

## Returns:
    str
        - Description: The string returned by plot_missing_matrix (in this codebase, the plotting chain ultimately returns an HTML/plot fragment string).
        - Notes:
            * The function returns whatever the plotting utility returns; callers should not assume more than "a string" (contents and format depend on the plotting implementation).
            * If plotting fails, an exception is raised and no string is returned.

## Raises:
    - Any exception raised by df.count(): e.g., Spark execution/planning errors, cluster connectivity errors (propagated as library-specific exceptions from the Spark API).
    - AttributeError if the provided df (or the wrapper) does not expose the attributes/methods accessed (e.g., .columns, .notnull, or if .notnull() lacks .values).
    - Exceptions from plot_missing_matrix or its dependencies (TypeError, ValueError, matplotlib errors) if the notnull mask is an incorrect shape/dtype or config is invalid.
    - This function does not catch exceptions; underlying exceptions propagate to the caller.

## Constraints:
    Preconditions:
        - The caller must accept that df.count() will be executed (this triggers a Spark job and can be expensive).
        - The Settings instance must include the keys the plotting utilities access.
        - Either the original DataFrame or the compatibility wrapper must provide a notnull() result whose .values is an array-like boolean mask compatible with plot_missing_matrix.

    Postconditions:
        - A Spark action to obtain a row count has been executed.
        - The plotting utility has been invoked with the columns, notnull mask, and nrows derived from the wrapper.
        - The function returns the plotting utility's string result or raises an exception if any step fails.

## Side Effects:
    - Executes df.count(): triggers a Spark job that scans/reads data as required by the underlying Spark plan.
    - Allocates memory and creates plot objects through plotting utilities (matplotlib, NumPy, etc.).
    - The function itself performs no file or network I/O and does not mutate global variables; any such side effects would originate from called utilities.

## Control Flow:
flowchart TD
    Start([start]) --> CountRows[Call original_df.count() — Spark action]
    CountRows --> Wrap[Create MissingnoBarSparkPatch(original_df, columns=<orig_columns>, original_df_size=<count>)]
    Wrap --> Reassign[Reassign df variable to wrapper]
    Reassign --> AccessNotnull[Call df.notnull().values]
    AccessNotnull --> PrepareCall[Prepare args: config, columns=df.columns, notnull, nrows=len(df)]
    PrepareCall --> CallPlot[Call plot_missing_matrix(config, columns, notnull, nrows)]
    CallPlot --> Return[Return plot string from plot_missing_matrix]
    Return --> End([end])

## Examples:
    Basic usage:
        # Given a valid Settings instance and a PySpark DataFrame 'sdf'
        html_fragment = spark_missing_matrix(config, sdf)
        # html_fragment is the string output of the plotting pipeline; embed it in the report.

    With error handling (recommended for production code):
        try:
            html_fragment = spark_missing_matrix(config, sdf)
        except Exception as exc:
            # df.count() or plotting may have failed; handle and log appropriately
            logger.exception("Unable to create missing matrix plot: %s", exc)
            html_fragment = "<!-- missing matrix unavailable -->"

Notes and recommendations:
    - To avoid the cost of df.count() on very large datasets, compute and cache the row count earlier and consider adapting the wrapper/plot path to accept a precomputed count to prevent an extra Spark job.
    - If plotting errors due to incorrect notnull mask shape, inspect the runtime value and shape/type of df.notnull().values before calling this function. Converting Spark column-wise null summaries into an explicit NumPy boolean mask of shape (nrows, ncols) is a reliable approach when needed.

## `src.ydata_profiling.model.spark.missing_spark.spark_missing_heatmap` · *function*

## Summary:
Prepares missingness data for a PySpark DataFrame, computes a missingness correlation matrix with an upper-triangle mask, and delegates rendering to the project's heatmap plotter, returning the plot helper's string/identifier.

## Description:
This function adapts a PySpark DataFrame for the missingness-visualisation pipeline, filters out columns without variation in missingness, computes the correlation of missingness between the remaining columns, constructs an upper-triangle mask, and calls the visualisation helper to render and return the plot.

Known callers and context:
- Called by higher-level profiling/report-generation code that needs a missingness heatmap for a PySpark dataset during report assembly or exploratory profiling.
- Typical pipeline stage: data-preparation → missingness analyses → visualization. This function lives in the data-preparation/adapter layer and hands off to the plotting layer.

Why this logic is extracted:
- Separates Spark-specific adaptation and column-selection logic from the plotting code so the visualiser can remain focused on rendering. This keeps concerns distinct: data preparation here, presentation in plot_missing_heatmap.

Important note about compatibility:
- The function wraps the provided pyspark DataFrame with MissingnoBarSparkPatch. Per the documented behavior of that class, MissingnoBarSparkPatch is a minimal compatibility shim: its isnull() returns the wrapper itself and sum() returns the underlying DataFrame; it does not compute column-wise null counts or provide a full pandas-like boolean DataFrame with .corr() and .iloc behavior.
- Therefore, for the subsequent operations in this function (np.var on df.isnull(), df.iloc slicing, and df.isnull().corr()) to succeed, the runtime must provide additional compatibility (for example, a separate adapter or monkey-patch that makes the wrapped object present pandas-like isnull/iloc/corr semantics) or the underlying object returned by sum() must be convertible to a pandas-like structure before these operations. If such extra adaptation is not present, the function may raise AttributeError / TypeError / ValueError at runtime.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Meaning: Global configuration consumed by the plotting helper (e.g., config.plot.missing.cmap and config.plot.missing.force_labels).
        - Required.

    df (pyspark.sql.DataFrame):
        - Type: pyspark.sql.DataFrame
        - Meaning: Input dataset. The function immediately calls df.count() and df.columns and wraps the DataFrame with MissingnoBarSparkPatch.
        - Required.

Interdependencies:
- The function relies on:
    - MissingnoBarSparkPatch (thin adapter). NOTE: that adapter alone does not implement full pandas-like missingness operations; additional adaptation may be required at runtime.
    - numpy functions: var, zeros_like, triu_indices_from.
    - plot_missing_heatmap: receives corr_mat, mask, and columns and returns a string/identifier.

## Returns:
    str:
    - The return value forwarded from plot_missing_heatmap (in observed implementation this is the string returned by plot_360_n0sc0pe(config)).
    - The function does not itself return None explicitly; any return value (or exception) originates from the plotting helper.

## Raises:
- Exceptions from Spark:
    - Any exception raised by df.count() (e.g., execution failure, cluster issues) will propagate directly.
- Exceptions from missingness adaptation and numeric operations:
    - If the wrapped/adapter object is not suitable for numpy.var(..., axis="rows"), .iloc slicing, or .corr(), AttributeError, TypeError, IndexError, or ValueError may be raised.
- Exceptions from plotting:
    - Any exception raised by plot_missing_heatmap (matplotlib/visualisation errors, missing config attributes) will propagate.

The function does not catch or transform exceptions.

## Constraints:
Preconditions:
- df must expose .columns and .count() (the function calls both immediately).
- Callers must ensure that, after wrapping with MissingnoBarSparkPatch, the object is usable with the subsequent operations in the code path:
    - np.var(df.isnull(), axis="rows") must be meaningful (i.e., df.isnull() must yield an array-like or pandas-like boolean structure).
    - df.iloc[:, columns] slicing must be supported to select columns by integer indices.
    - df.isnull().corr() must be supported and return a 2D correlation structure (numpy array or pandas DataFrame).
  Note: MissingnoBarSparkPatch by itself does not implement these computations — additional runtime adaptation (outside of this shim) is required for full compatibility.
- config must contain plotting configuration values used by the plotting helper.

Postconditions:
- The caller receives the plotting helper's return value. No global state is modified by this function.
- The function will have triggered a Spark count job via df.count().

## Side Effects:
- Triggers a Spark job when df.count() is called; this potentially materializes computation and can be expensive.
- No files, network I/O, databases, or global state are written by this function itself.
- The plotting helper will create matplotlib state (figures/axes); this function does not clean up matplotlib state.

## Control Flow:
flowchart TD
    Start([Start]) --> Count[Call df.count() (Spark job)]
    Count --> Wrap[Wrap with MissingnoBarSparkPatch(original_df_size=count, columns=df.columns)]
    Wrap --> Var[Compute var of missingness:\nnp.var(df.isnull(), axis="rows")]
    Var --> Select[Select indices where variance > 0]
    Select --> Subset[Subset df by indices: df = df.iloc[:, columns]]
    Subset --> Corr[Compute missingness correlation: corr_mat = df.isnull().corr()]
    Corr --> Mask[Create mask: mask = zeros_like(corr_mat); mask[triu_indices] = True]
    Mask --> Plot[Call plot_missing_heatmap(config, corr_mat, mask, columns=list(df.columns))]
    Plot --> Return[Return plotting helper's string]
    Return --> End([End])

Notes on branches:
- There is no explicit short-circuit for the case of zero selected columns. If no columns have variance > 0, an empty selection is used and corr_mat may be empty/degenerate — the plotting helper determines the outcome.

## Examples:
Typical usage (conceptual):
    try:
        plot_id = spark_missing_heatmap(config, spark_df)
        # use plot_id in report assembly
    except Exception as exc:
        # handle Spark or plotting failures
        logger.error("Could not create missingness heatmap: %s", exc)
        raise

Edge-case considerations:
- If all columns have constant missingness (no variance), the selected columns list will be empty. The plotting helper may render an empty plot or raise an exception; callers should handle this possibility.
- If the environment does not provide the extra adaptation required to let df.isnull(), df.iloc, and df.isnull().corr() behave like pandas equivalents, the function will fail; ensure a compatible adapter pipeline exists when using this helper.

Implementation guidance for reimplementation:
- Replicate the call sequence exactly: count the DataFrame, instantiate the minimal wrapper with columns and original size, compute variance across rows for df.isnull(), filter columns, select columns via .iloc, compute correlation on df.isnull(), create an upper-triangle mask via numpy, and call the plot_missing_heatmap helper with the correlation matrix, mask, and final column list.
- Be explicit in your runtime about how Spark DataFrames are converted or adapted into structures that support numpy.var, .iloc, and .corr() (for instance, converting appropriate columns to a pandas DataFrame or implementing a richer wrapper than MissingnoBarSparkPatch).

