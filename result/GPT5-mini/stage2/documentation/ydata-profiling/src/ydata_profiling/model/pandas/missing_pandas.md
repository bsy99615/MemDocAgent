# `missing_pandas.py`

## `src.ydata_profiling.model.pandas.missing_pandas.pandas_missing_bar` · *function*

## Summary:
Compute per-column non-null counts from a pandas DataFrame and delegate rendering of a missing-values bar chart to the plotting layer; returns the opaque visualization identifier produced by the plotting subsystem.

## Description:
This function is a Pandas-specific adapter that converts a DataFrame into the primitive inputs required by the generic plotting routine plot_missing_bar. It computes, for each DataFrame column, how many non-null values exist and forwards:
- notnull_counts: counts per column,
- nrows: total number of rows in the DataFrame,
- columns: list of column labels

Known callers:
- No direct callers were found in the provided code snapshot. Typical caller scenarios: higher-level profile/report generation code that assembles missing-data diagnostics for a DataFrame and requests a bar visualization for missing/available values as part of a profiling report.

Why this logic is extracted:
- Separates DataFrame-specific preprocessing (counting non-nulls, extracting columns and row counts) from visualization concerns. This keeps plotting code generic and testable while confining pandas semantics to a small adapter.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Description: Global configuration object passed through to the plotting layer (controls styling, color, labels, and other visual options).
        - Constraints: Must be non-None and compatible with the plotting functions that will read fields such as html.style.primary_colors and plot.missing.force_labels.
    df (pandas.DataFrame):
        - Type: pandas.DataFrame
        - Description: The DataFrame to profile for missing values.
        - Required operations: len(df), df.isnull().sum(), and df.columns must be supported.
        - Notes: df.columns may be of any hashable type (strings, numbers, tuples for MultiIndex). The plotting layer's type annotation expects List[str]; if column labels are not strings, they will be passed as-is (see Constraints below).

Interdependencies:
- None between parameters beyond the expectation that config is valid for the plotting layer; df is independent.

## Returns:
    str:
        - The return value is forwarded unchanged from plot_missing_bar and represents the visualization artefact identifier created by the plotting subsystem (for example an HTML snippet id, a serialized widget identifier, or a filename). Treat it as opaque.
        - In the provided plotting implementation, plot_missing_bar ultimately returns the value from plot_360_n0sc0pe(config), typed as str.

Edge-case and propagated returns:
- If the plotting layer returns None, that None is returned.
- If the plotting layer raises an exception, that exception propagates and is not converted.

## Raises:
- AttributeError / TypeError:
    - If df does not implement isnull(), columns, or __len__() in a compatible way, Python will raise AttributeError or TypeError when those operations are attempted.
- Any Exception raised by plot_missing_bar or deeper plotting utilities:
    - The function does not catch exceptions from the visualization layer; they bubble up to the caller unchanged.

## Constraints:
Preconditions:
- config must be a valid Settings instance for the plotting utilities to read expected configuration fields.
- df must be a DataFrame-like object with accessible columns, len(), and isnull().sum() semantics.

Potential issues and recommendations:
- Type of notnull_counts: computed as len(df) - df.isnull().sum(), which yields a pandas.Series of integer counts indexed by df.columns. The plotting layer accepts a sequence of counts; it is passed as-is. Callers expecting a pure Python list may convert it before calling.
- Column label types: list(df.columns) preserves original label types. If df.columns contains non-string labels (e.g., tuples from a MultiIndex), the plotting function that is annotated to accept List[str] may behave unexpectedly. If needed, pre-convert column labels to strings before calling this adapter.
- MultiIndex columns: list(df.columns) will produce a list of tuples; downstream plotting code may need to handle tuple labels or be given stringified labels.

Postconditions:
- The input DataFrame is not mutated.
- A plotting operation will have been requested; matplotlib global state (current figure, axes) may have been created or modified by the plotting layer.

## Side Effects:
- Invokes plot_missing_bar which:
    - Performs plotting operations that create/modify matplotlib figures and axes (affects plt.gcf(), axes grid visibility, and subplot layout).
    - Calls plotting helpers that may perform additional side effects (e.g., creating images, returning HTML snippets) depending on the plotting backend.
- No direct file I/O, network I/O, or global variable mutations are performed by this function itself; any such behavior would originate from the plotting layer and will propagate.

## Control Flow:
flowchart TD
    Start --> ComputeNotNull
    ComputeNotNull[Compute notnull_counts = len(df) - df.isnull().sum()] --> PrepareArgs
    PrepareArgs[Prepare nrows = len(df) ; columns = list(df.columns)] --> CallPlotMissingBar
    CallPlotMissingBar[Call plot_missing_bar(config, notnull_counts, nrows, columns)] --> PlotLayer
    PlotLayer[plot_missing_bar: calls missing_bar() -> adjusts matplotlib axes and layout -> returns plot_360_n0sc0pe(config) result] --> ReturnValue
    ReturnValue --> End

## Examples:
Example 1 — Typical usage
    from ydata_profiling.config import Settings
    import pandas as pd

    cfg = Settings()  # valid Settings instance required by plotting layer
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10.0, None, 30.0],
        "flag": [True, False, None],
    })

    viz_id = pandas_missing_bar(cfg, df)
    # viz_id is an opaque string produced by the plotting subsystem (embed or reference as appropriate)

Example 2 — Empty DataFrame
    empty_df = pd.DataFrame(columns=["a", "b"])
    # len(empty_df) == 0, df.isnull().sum() == 0 for each column, so notnull_counts will be a Series of zeros
    viz_id = pandas_missing_bar(cfg, empty_df)

Example 3 — Non-string / MultiIndex columns
    df_multi = pd.DataFrame([[1, 2]], columns=pd.MultiIndex.from_tuples([("a", 1), ("b", 2)]))
    # list(df_multi.columns) yields a list of tuples; the plotting function receives those tuples as labels.
    # If the plotting backend expects strings, convert labels first:
    df_multi.columns = [f"{c}" for c in df_multi.columns]
    viz_id = pandas_missing_bar(cfg, df_multi)

## `src.ydata_profiling.model.pandas.missing_pandas.pandas_missing_matrix` · *function*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
Produces a serialized missing-data matrix visualization for a pandas DataFrame by delegating to the shared plotting routine and returns the resulting plot representation as a string.

## Description:
- Known callers within the codebase:
    - No direct callers were discovered during inspection of the immediate module assets. This function is intended to be invoked by higher-level report-generation or profiling routines that accept a pandas DataFrame and a Settings object and need a missing-data matrix visualization.
- Context and typical invocation:
    - Called during the "missing data visualization" stage of a profiling pipeline to convert a DataFrame's null/not-null pattern into the inputs required by the plotting layer and obtain a serialized visualization artifact.
- Why this function is separate:
    - Responsibility separation: it converts DataFrame-level information (columns, number of rows, not-null boolean matrix) into the parameter set expected by the generic plotting function. Extracting this logic keeps plotting code generic (operating on primitive arrays and lists) and keeps DataFrame-specific extraction in a thin adapter layer.

## Args:
    config (Settings):
        - Type: Settings
        - Description: Configuration object that controls style and plotting options (colors, label forcing, etc.). Passed through to the plotting routine.
    df (pandas.DataFrame):
        - Type: pandas DataFrame
        - Description: The source table whose missing-value pattern will be visualized.
        - Notes:
            - The function reads df.columns and df.notnull().values and uses len(df) for nrows.
            - Column order is preserved via list(df.columns).
            - Duplicate column names are preserved (no deduplication is performed).

## Returns:
    str:
        - A string representing the serialized plot produced by the plotting pipeline (the exact format is determined by the downstream plotting function; typically an HTML/URI/JSON payload or other serialized plot representation).
        - Edge cases:
            - For an empty DataFrame (zero rows or zero columns), the returned string is whatever the plotting pipeline produces for that input (likely an empty/placeholder visualization string). The function itself does not transform or sanitize the plotting output.

## Raises:
    - No exceptions are explicitly raised by this function.
    - Possible runtime exceptions that may propagate:
        - AttributeError or TypeError: if the provided `df` does not expose `.columns`, `.notnull()`, or has unexpected types (i.e., if df is not a pandas DataFrame-like object).
        - Any exceptions raised by the called plotting routines (plot_missing_matrix -> missing_matrix -> plotting internals) will propagate up unchanged.

## Constraints:
- Preconditions:
    - `config` must be a valid Settings instance (the plotting layer will index into config.html.style.primary_colors and config.plot.missing.force_labels).
    - `df` must be a pandas DataFrame or DataFrame-like object providing `.columns`, `.notnull().values`, and len(df).
- Postconditions:
    - The DataFrame `df` is not modified by this function.
    - A string is returned which is the direct return value of the plotting routine invoked.

## Side Effects:
- Calls into the visualization layer which:
    - Constructs and modifies matplotlib state (the plotting functions call plotting primitives and adjust the current figure via subplots_adjust).
    - Reads values from the `config` object (e.g., primary colors and plot settings).
- No file or network I/O is performed by this function itself; any I/O would be performed only if the deeper plotting utilities perform it (not observed here).
- No global variables within this module are mutated by this function.

## Control Flow:
flowchart TD
    Start([Start])
    ValidateInputs{Is `config` a Settings\nand `df` a pandas DataFrame?}
    InvalidInputs([Raise or propagate\nAttributeError/TypeError])
    PrepareArgs[Prepare arguments:\ncolumns=list(df.columns)\nnotnull=df.notnull().values\nnrows=len(df)]
    CallPlot[Call plot_missing_matrix(config,\n columns, notnull, nrows)]
    PlotReturned([Receive serialized plot string])
    Return([Return plot string])
    Start --> ValidateInputs
    ValidateInputs -- No --> InvalidInputs
    ValidateInputs -- Yes --> PrepareArgs
    PrepareArgs --> CallPlot
    CallPlot --> PlotReturned
    PlotReturned --> Return

## Examples:
- Typical usage scenario (descriptive):
    - Given a completed Settings object named config (which contains HTML/style and plot settings) and a pandas DataFrame named df containing the dataset to profile, call this adapter to obtain the missing-data matrix visualization:
        - Invoke the adapter with the two arguments; it will extract column names, compute the boolean not-null matrix, and call into the plotting routine to get a serialized plot string.
    - Error handling:
        - If the caller cannot guarantee df is a DataFrame, wrap the call in a try/except that catches AttributeError and TypeError and either converts the input to a DataFrame or logs/raises a clearer error.
    - Example flow (pseudo-steps, not code):
        1. Ensure config is initialized and contains valid plotting style keys.
        2. Ensure df is a pandas DataFrame.
        3. Call the adapter to receive a serialized visualization string.
        4. Embed or render the returned string in the higher-level report.

## `src.ydata_profiling.model.pandas.missing_pandas.pandas_missing_heatmap` · *function*

## Summary:
Prepare a pairwise missingness correlation matrix for DataFrame columns that have variable missingness and delegate rendering to the visualisation layer, returning the visualiser's plot identifier string.

## Description:
This function identifies DataFrame columns whose null-indicator vectors are non-constant (variance > 0), computes the pairwise Pearson correlation matrix of those columns' isnull() indicator variables, constructs an upper-triangle mask for plotting a symmetric matrix, and forwards the results to the plotting routine plot_missing_heatmap.

Key implementation notes (directly reflecting the source code):
- Variance detection is performed with numpy.var(df.isnull(), axis="rows") and columns with resulting variance > 0 are selected by their integer indices.
- The DataFrame is sliced using iloc with those integer column indices before computing df.isnull().corr().
- A mask array is produced with numpy.zeros_like(corr_mat) and the upper triangle (including diagonal) is set True via numpy.triu_indices_from(mask).
- The visualiser is called as plot_missing_heatmap(config, corr_mat=corr_mat, mask=mask, columns=list(df.columns)) and its return value is returned.

Known callers and typical context:
- Invoked from the missingness visualization stage of the profiling pipeline (e.g., the backend-specific missing_heatmap wrapper in ydata_profiling.model.missing when the pandas backend is used).
- Used when building the missing-data section of a profile report after the DataFrame to be profiled has been selected.

Why extracted into its own function:
- Separates data-preparation (selecting columns, computing null-correlation and mask) from rendering/styling logic, allowing the visualiser to control figure sizing and layout independently.

## Args:
    config (Settings):
        - Configuration object carrying plotting settings used by the visualiser (e.g., config.plot.missing.cmap, config.plot.missing.force_labels).
    df (pandas.DataFrame):
        - The DataFrame to analyse for missingness.
        - Must implement isnull(), iloc indexing, and columns attributes compatible with pandas DataFrame semantics.

Interdependencies:
- The function relies on the visualiser expecting corr_mat, mask, and a list of column names. It converts the selected columns' integer indices into column names for the final call.

## Returns:
    str
    - The return value is whatever plot_missing_heatmap returns; in this codebase that is a string identifier/representation produced by the visualiser (for example, an encoded plot fragment or internal plot id returned by plot_360_n0sc0pe).
    - There is always a return of a string produced by the plotting routine, even when no columns are selected (see edge case below).

## Raises:
    - This function does not raise custom exceptions directly but will propagate exceptions from underlying calls:
        * TypeError or AttributeError if `df` is not DataFrame-like (missing isnull, iloc or columns).
        * Exceptions from numpy/pandas when computing variance or correlation if inputs are malformed.
        * Exceptions from the plotting/visualisation layer (matplotlib or plot_missing_heatmap) if plotting fails.
    - Because the code uses numpy.var(..., axis="rows") as written, mismatches between numpy/pandas axis argument expectations could raise an exception in some versions/environments.

## Constraints:
Preconditions:
    - `config` must be a valid Settings instance compatible with the visualiser.
    - `df` must be a pandas.DataFrame (or provide equivalent isnull/iloc/columns behavior).
    - A plotting backend (matplotlib) and the visualisation functions must be available in the runtime.

Postconditions:
    - The visualisation side effects (figure creation and layout adjustments) have been executed by downstream plotting functions.
    - The function returns the string result produced by plot_missing_heatmap.

## Data shapes and types:
    - Intermediate: variance array from numpy.var(...) — one variance value per original DataFrame column (iterable of floats).
    - columns variable: list[int] — integer indices of original DataFrame columns selected for having variance > 0.
    - Sliced df: pandas.DataFrame with the selected subset of columns (can be zero columns).
    - corr_mat: pandas.DataFrame — square correlation matrix with index and columns equal to the selected column names; dtype float; entries are Pearson correlation coefficients in [-1.0, 1.0] where defined; may be empty (shape (0, 0)) if no columns selected.
    - mask: numpy.ndarray — an array with the same shape as corr_mat (shape (n, n)); boolean values where True marks the upper triangle (including diagonal) and False the lower triangle; may be an empty array if corr_mat is empty.

## Side Effects:
    - Triggers plotting actions in the visualiser (creation of matplotlib figures/axes, layout adjustments, and final plot encoding). These calls mutate matplotlib's global current figure/axes state.
    - No intentional writes to disk, network calls, or global variable modifications are performed by this function itself; any such behavior would be performed by the downstream visualiser.

## Control Flow:
flowchart TD
    Start --> ComputeIsnull[Call df.isnull()]
    ComputeIsnull --> ComputeVar[Compute variances using numpy.var(..., axis="rows")]
    ComputeVar --> SelectIdx[Select integer column indices with variance > 0]
    SelectIdx --> SliceDF[Slice DataFrame: df = df.iloc[:, selected_indices]]
    SliceDF --> ComputeCorr[Compute corr_mat = df.isnull().corr()]
    ComputeCorr --> CreateMask[Create mask = zeros_like(corr_mat); set upper-triangle True]
    CreateMask --> CallPlot[Call plot_missing_heatmap(config, corr_mat, mask, columns=list(df.columns))]
    CallPlot --> Return[Return visualiser string result]
    Return --> End

## Examples:
1) Typical usage in profiling pipeline (conceptual):
    - The profiler has assembled a pandas DataFrame `df` to examine for missingness patterns and has a Settings instance `config`.
    - It calls this function to obtain a rendered missingness heatmap fragment used in the report:
        - The function returns a string produced by the visualiser (e.g., an embedded HTML fragment or plot id) that the reporting pipeline includes in the output.

2) Edge case — no variable missingness:
    - If every original column is either fully present or fully missing, the variance step yields no indices (selected_indices is empty). The function slices to an empty-column DataFrame, corr_mat is an empty DataFrame (shape (0,0)), mask is an empty numpy array shape (0,0), and the visualiser is invoked with an empty columns list. The function still returns the string result produced by the visualiser (which may represent an empty/placeholder plot). Callers should inspect or guard for the empty case upstream if they require a non-empty visualization.

Implementation reminder:
    - This documentation describes behavior as implemented in the code; callers should not rely on pandas returning a copy versus a view from iloc — the function does not intentionally mutate the input DataFrame but pandas semantics may vary by version.

