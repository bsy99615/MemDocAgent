# `missing.py`

## `src.ydata_profiling.model.missing.missing_bar` · *function*

## Summary:
Specification to compute per-column missingness statistics from a DataFrame, delegate drawing to the repository's plotting helper, and return a serialized image string suitable for embedding in a report.

## Description:
This document specifies the intended behavior and implementation steps for the model-layer function that prepares data for and renders a "missing values" bar chart.

Known concrete visualisation helper available in the codebase (use when implementing):
- src.ydata_profiling.visualisation.plot.missing_bar(
    notnull_counts: pd.Series,
    nrows: int,
    figsize: Tuple[float, float] = (25, 10),
    fontsize: float = 16,
    labels: bool = True,
    color: Tuple[float, ...] = (0.41, 0.41, 0.41),
    label_rotation: int = 45,
) -> matplotlib.axis.Axis

Known callers:
- No direct callers were discovered in the available snapshot. The intended integration point is the report generation pipeline where the "missing data" section for variables is assembled.

Why a separate function:
- Responsibility separation: this function isolates data preparation (counts, sorting, filtering) and output-format decisions (serialize to SVG/PNG) from the raw drawing code. The visualisation helper focuses purely on plotting; this function focuses on preparing inputs and producing an embeddable output.

## Args:
    config (Settings)
        - Type: Settings-like object (repository configuration).
        - Role: optional source of plotting/rendering preferences. Implementations must not assume specific attributes exist on Settings; use getattr(config, "attribute_name", default) to read optional values.
        - Suggested/readable option names (implementation MAY choose different names; these are recommendations):
            * plot_missing_figsize -> Tuple[float, float] (recommended default: (25, 10))
            * plot_missing_fontsize -> float (recommended default: 16)
            * plot_missing_labels -> bool (recommended default: True)
            * plot_missing_color -> Tuple[float, ...] (recommended default: (0.41, 0.41, 0.41))
            * plot_missing_label_rotation -> int (recommended default: 45)
            * plot_missing_render -> str, one of {"svg", "png"} (recommended default: "svg")
        - Interdependencies: none required; if an option is missing or None, the function MUST substitute sensible defaults.

    df (Any)
        - Expected Type: pandas.DataFrame or DataFrame-like object that supports:
            * df.notnull() producing a boolean DataFrame
            * .sum(axis=0) on the result to compute per-column non-null counts
            * .shape to obtain number of rows/columns
        - Behavior if invalid: The function should raise TypeError when df is None or lacks required attributes.

## Returns:
    str
    - Specification for implementer: return a serialized image string representing the missingness bar chart.
    - Two recommended formats to choose between (implementation MUST use one consistently and document which):
        1. SVG text: the raw SVG XML string (utf-8). Advantage: embeddable directly into HTML.
        2. PNG data URI: "data:image/png;base64,<base64-data>" where <base64-data> is the base64 of the PNG bytes.
    - Edge-case returns:
        - When df has zero columns (shape[1] == 0): return an empty string "" (preferred) or raise ValueError("No columns to plot") if the downstream pipeline expects exceptions for missing content.
        - When df has zero rows (shape[0] == 0): return an empty string "" (preferred) so the report can omit the plot gracefully.

## Raises:
    TypeError:
        - If df is None or does not support .notnull(), .sum(axis=0), or .shape.
    ValueError (optional):
        - If the implementer chooses strict behavior for empty datasets, raise ValueError("No columns to plot") when df.shape[1] == 0.
    Propagated exceptions:
        - Exceptions raised by the plotting helper or Matplotlib (IOError, MemoryError, etc.) may propagate; implementations should document and, where appropriate, catch/log them during report generation.

## Constraints:
    Preconditions:
        - config is a Settings-like object (may be a plain namespace in tests).
        - df is a DataFrame-like object as described above.
    Postconditions:
        - The function does not mutate df in-place.
        - The function returns a string (possibly empty) and has released Matplotlib resources (no lingering open figures).

## Side Effects:
    - Creates Matplotlib figure and axis objects in memory.
    - Implementations MUST clean up figures after rendering (e.g., fig.clf(), matplotlib.pyplot.close(fig)) to avoid memory leaks.
    - No file I/O, network calls, or global state mutation are required by this function by default.

## Control Flow:
flowchart TD
    Start[Start: missing_bar(config, df)] --> Validate{df is DataFrame-like?}
    Validate -- no --> RaiseTypeError[Raise TypeError or return ""]
    Validate -- yes --> ComputeCounts[Compute notnull_counts = df.notnull().sum(axis=0)]
    ComputeCounts --> CheckCols{Are there any columns?}
    CheckCols -- no --> ReturnEmpty[Return "" or raise ValueError]
    CheckCols -- yes --> SortAndFilter[Sort and optionally filter notnull_counts]
    SortAndFilter --> ReadConfig[Read plotting options from config via getattr(..., default)]
    ReadConfig --> CallViz[Call visualisation.plot.missing_bar(notnull_counts, nrows, **plot_kwargs) -> ax]
    CallViz --> GetFig[fig = ax.get_figure()]
    GetFig --> Render{render format: svg or png}
    Render -- svg --> SerializeSVG[Save figure to buffer as SVG -> obtain UTF-8 string]
    Render -- png --> SerializePNG[Save as PNG -> base64-encode -> data URI]
    SerializeSVG --> Cleanup[Close/clear figure]
    SerializePNG --> Cleanup
    Cleanup --> Return[Return serialized string]
    Return --> End[End]

## Implementation steps (precise algorithm):
1. Validate input:
    - If df is None or not hasattr(df, "notnull") or not hasattr(df, "shape"), raise TypeError("df must be a DataFrame-like object").
2. Compute non-null counts:
    - Compute a pandas Series: notnull_counts = df.notnull().sum(axis=0)
3. Handle trivial cases:
    - If notnull_counts.empty (no columns), return "" (or raise ValueError if the project prefers).
    - If df.shape[0] == 0 (no rows), return "".
4. Sort for presentation:
    - Optionally sort notnull_counts for stable, informative ordering, e.g., notnull_counts = notnull_counts.sort_values(ascending=False)
5. Collect plotting kwargs from config:
    - Use getattr(config, "plot_missing_figsize", (25, 10)), etc., for the suggested option names above. Validate types and fall back to defaults if invalid.
6. Call the plotting helper:
    - Use the known helper signature: viz_missing_bar(notnull_counts, nrows=df.shape[0], figsize=..., fontsize=..., labels=..., color=..., label_rotation=...)
    - The helper returns an Axis (ax); retrieve fig = ax.get_figure().
7. Serialize the figure:
    - If using SVG: create an in-memory buffer, call fig.savefig(buffer, format="svg"), then decode bytes to an UTF-8 string.
    - If using PNG: save PNG to buffer, base64-encode bytes, and format as a data URI "data:image/png;base64,<b64>".
8. Cleanup:
    - Call fig.clf() and matplotlib.pyplot.close(fig) (or equivalent) to free resources.
9. Return the serialized string.

## Examples (usage patterns, not verbatim code):
- Typical integration: The report builder calls this function after computing variable-level summaries; the returned SVG string is embedded directly into the HTML section for missing data.
- Empty-data handling: When building multi-variable reports, check for an empty string return and omit the plot for that variable instead of failing the entire report.

Notes:
- The Settings attribute names and defaults listed are recommendations to ensure consistent appearance across reports. If the project Settings object already defines plotting options with different names, adapt the getattr calls accordingly.
- Because the original function body is unimplemented in the repository snapshot, this specification defines the expected and tested behavior for new implementations.

## `src.ydata_profiling.model.missing.missing_matrix` · *function*

## Summary:
Intended to produce a missingness-matrix visualization for a table-like object and return it as a string for embedding in reports; currently a placeholder that raises NotImplementedError.

## Description:
Current behavior:
    - The function is an unimplemented stub. Calling it will raise NotImplementedError.

Known callers within the codebase:
    - None discovered in a static scan of the repository.

Why this logic is extracted into its own function:
    - Responsibility separation: preparing a boolean presence/absence matrix, downsampling rows, rendering a visualization and returning an embeddable string are distinct concerns that higher-level report-generation code should not duplicate. Centralizing this behavior simplifies report templates and ensures consistent visualization across the project.

Note:
    - The remainder of this document provides detailed, clearly-labeled implementation guidance so a developer can implement the intended behavior. Those sections describe suggested inputs, outputs, constraints, side-effects and an algorithm — they are not assertions about the current code (which only raises NotImplementedError).

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: configuration holder for visualization and sampling parameters.
        - Expected fields (implementation guidance only — may be absent; implementations should apply sensible defaults):
            * plot.missing.matrix.height: int (desired number of rows to display)
            * plot.missing.matrix.figsize: tuple[float, float]
            * plot.missing.matrix.color: tuple[float, ...] (RGB floats 0..1)
            * plot.missing.matrix.fontsize: float
            * plot.missing.matrix.labels: bool
            * plot.missing.matrix.label_rotation: int
        - The function must NOT mutate the Settings object.

    df (Any):
        - Type: Any object with DataFrame-like semantics (typical: pandas.DataFrame)
        - Required capabilities:
            * df.shape -> tuple[int, int] (n_rows, n_cols)
            * df.columns -> iterable of column labels
            * df.notnull() or df.isnull() -> DataFrame-like boolean mask
            * Selection by integer positions (e.g., df.iloc[indices]) to sample rows
        - If df is None or lacks required interfaces, the current implementation raises NotImplementedError — an implemented version should raise a TypeError or ValueError (see Implementation guidance).

## Returns:
    - Current implementation: never returns; it raises NotImplementedError.
    - Intended return (implementation guidance):
        * Type: str
        * Representation: an image encoded as a string suitable for embedding (recommended: PNG data URI "data:image/png;base64,<payload>").
        * Content: a rendered image where white pixels indicate missing values and colored pixels indicate present (not-missing) values, sized according to configuration and sampling.

## Raises:
    - NotImplementedError:
        * Condition: This is raised unconditionally by the current function body.
    - (Implementation guidance): A future implementation might raise TypeError, ValueError, or RuntimeError for invalid inputs or rendering failures; these are not raised by the current stub.

## Constraints:
Preconditions (for a correct implementation):
    - config must be provided (Settings instance).
    - df must be a table-like object with at least one column.
    - The runtime environment must have Matplotlib available for rendering.

Postconditions (for a correct implementation):
    - Returns a valid image string (data URI) that represents the requested missingness matrix.
    - Does not mutate df or config.
    - Cleans up Matplotlib resources (closes the figure) before returning.

## Side Effects:
Current implementation:
    - Raises NotImplementedError; no I/O or persistent state changes.

Implementation guidance (expected side effects of an implemented function):
    - Allocates memory proportional to sampled_rows * n_columns.
    - Creates Matplotlib Figure/Axis objects and must close them to free resources.
    - Emits warnings via warnings.warn for large inputs or when downsampling is applied.
    - Does not perform file-system writes or network calls (recommended); image encoding should be done in-memory.

## Control Flow:
(The flowchart below describes a recommended implementation; it is not executed by the current stub.)
flowchart TD
    Start --> ValidateInputs
    ValidateInputs -->|df None or missing methods| RaiseError
    ValidateInputs --> ExtractConfigOrDefaults
    ExtractConfigOrDefaults --> DetermineSampleHeight
    DetermineSampleHeight -->|height >= n_rows| SelectAllRows
    DetermineSampleHeight -->|height < n_rows| SampleRowsEvenly
    SelectAllRows --> ComputeNotNullMask
    SampleRowsEvenly --> ComputeNotNullMask
    ComputeNotNullMask --> CallPlotHelper
    CallPlotHelper -->|Axis returned| SaveFigureToBuffer
    SaveFigureToBuffer --> EncodeBase64
    EncodeBase64 --> BuildDataURI
    BuildDataURI --> CloseFigure
    CloseFigure --> ReturnDataURI

## Implementation guidance (step-by-step algorithm for reimplementation):
1. Validate inputs:
    - If df is None or does not expose .columns and .shape, raise TypeError("df must be a DataFrame-like object").
    - If df has zero columns (df.shape[1] == 0), raise ValueError("df must contain at least one column").

2. Read configuration with safe fallbacks:
    - height: desired number of rows to display. Suggested default: min(100, n_rows) or a constant such as 100.
    - figsize: default (25, 10)
    - color: default (0.41, 0.41, 0.41)
    - fontsize: default 16
    - labels: default True
    - label_rotation: default 45

3. Determine rows to visualize:
    - Let n_rows, n_cols = df.shape.
    - If height >= n_rows or height <= 0: use all rows.
    - If height < n_rows: sample row indices evenly: numpy.linspace(0, n_rows - 1, num=height, dtype=int), then select rows via df.iloc[indices].

4. Build boolean mask:
    - Compute notnull_mask = sampled_df.notnull().to_numpy(dtype=bool) (or equivalent).
    - Ensure mask shape is (displayed_height, n_cols).

5. Call the plotting helper:
    - Use the project's visualization function (example import path):
        from ydata_profiling.visualisation.plot.missing_matrix import missing_matrix as plot_missing_matrix
    - Call with parameters:
        ax = plot_missing_matrix(notnull_mask, columns=list(sampled_df.columns), height=displayed_height, figsize=figsize, color=color, fontsize=fontsize, labels=labels, label_rotation=label_rotation)
    - Extract fig = ax.figure.

6. Encode into a data URI:
    - Use io.BytesIO() and fig.savefig(buffer, format="png", bbox_inches="tight")
    - buffer.seek(0); payload = base64.b64encode(buffer.read()).decode("ascii")
    - data_uri = f"data:image/png;base64,{payload}"

7. Cleanup:
    - Call matplotlib.pyplot.close(fig) to release resources.

8. Return:
    - Return data_uri string.

## Examples (implementation guidance):
Example (pseudocode):
    from ydata_profiling.config import Settings
    config = Settings()  # or load project settings
    try:
        img_uri = missing_matrix(config, df)  # after implementing the stub
        html = f'<img src="{img_uri}" alt="Missingness matrix" />'
    except NotImplementedError:
        # current behavior: function not implemented
        handle_missing_function()

Notes for maintainers:
    - Keep the current stub (raising NotImplementedError) until a concrete implementation is provided.
    - When implementing, add unit tests that verify behavior across edge cases: empty df, single-column df, tall vs wide tables, very large tables (ensure warnings trigger), and resource cleanup.

## `src.ydata_profiling.model.missing.missing_heatmap` · *function*

## Summary:
Currently a stub that raises NotImplementedError; intended to compute pairwise correlations of column-wise missingness and return a rendered heatmap as a string for embedding in a report.

## Description:
This function in the current source is unimplemented and immediately raises NotImplementedError. The documentation below therefore has two parts:
1. Current behavior (what the present function does): it raises NotImplementedError().
2. Intended behavior and a step-by-step implementation plan that a developer can follow to implement the feature.

Known callers within the codebase and typical context:
- No call-sites were identified for the current stub implementation in the available code graph. In a complete profiling pipeline, this function would typically be called during the "missingness analysis" stage to produce a visualization that is embedded in the final report.

Why this logic is extracted to its own function:
- Encapsulates all logic for computing and rendering a missingness correlation heatmap so other parts of the pipeline can request the visualization without reimplementing matrix computation or plotting details.
- Simplifies unit testing and separation of concerns: computation of missingness, plotting parameters, and rendering/formatting for the report are separated.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: Configuration object controlling plotting and rendering options (figsize, fontsize, cmap, output format, strict/error behavior).
        - Note: The current stub does not inspect config because it immediately raises NotImplementedError. An implemented version should gracefully read plotting/render options from this object.

    df (Any):
        - Type: Expected to be a pandas.DataFrame or DataFrame-like object that supports isnull(), shape, and column indexing.
        - Purpose: The dataset to analyze for column-wise missingness.
        - Note: The current stub does not use df because it raises NotImplementedError. An implemented version should coerce df to pandas.DataFrame if necessary.

## Returns:
    str:
        - Current behavior: There is no return because the function raises NotImplementedError.
        - Intended behavior when implemented: a string containing the rendered heatmap suitable for embedding into the report. Possible formats include:
            * An HTML snippet with an inline base64 PNG (<img src="data:image/png;base64,...">).
            * An HTML <div> containing an SVG.
            * A filesystem path to a saved image (string).
        - Edge-case returns (recommended behavior when implemented):
            * If df has fewer than 2 columns, return an informative empty snippet (e.g., a short HTML paragraph) rather than throwing, unless config.strict requests an exception.

## Raises:
    NotImplementedError:
        - Condition: The function body currently contains a single statement that raises NotImplementedError() unconditionally.
    (Recommendations for a future implementation)
    ValueError:
        - To raise if df cannot be coerced to a DataFrame-like object.
    TypeError:
        - To raise if config is not a Settings instance and required config fields cannot be read.
    RuntimeError:
        - To raise if rendering fails irrecoverably (e.g., matplotlib/seaborn exceptions that cannot be recovered).

## Constraints:
Preconditions:
    - Present code: none beyond Python function call semantics. The current function will always raise NotImplementedError on invocation.
    - For a future implementation: df must be coercible to pandas.DataFrame and config must provide plotting/rendering choices or defaults.

Postconditions (intended once implemented):
    - The function returns a str (non-None) representing the visualization or a clearly documented fallback snippet.
    - Input df is not mutated.

## Side Effects:
    - Present code: none beyond raising NotImplementedError.
    - Intended implementation may:
        * Allocate in-memory image buffers (BytesIO).
        * Optionally write image files to disk if config requests external assets.
        * Emit warnings via the warnings module for degenerative inputs (e.g., <2 columns).
        * Close matplotlib figures to avoid memory leaks.

## Control Flow:
flowchart TD
    Start([Start])
    CallFunc[Call missing_heatmap(config, df)]
    RaisesNI{Function implemented?}
    RaiseNI[Raise NotImplementedError -> End]
    ToImplement[Coerce df to pandas.DataFrame]
    CheckDF{Is df None or empty?}
    NotEnough[Return informative empty snippet]
    ComputeMask[Compute missingness boolean matrix: df.isnull()]
    IfCols{Number of columns < 2?}
    ComputeCorr[Compute pairwise correlation of missingness vectors]
    MakeMask[Build triangular mask to hide duplicates]
    ReadConfig[Read plotting/render params from config with safe defaults]
    CallPlot[Call visualization.plot.missing_heatmap(corr, mask, ...)]
    ConvertToString[Convert matplotlib figure to base64 HTML or save and return path]
    ReturnResult[Return rendered string]
    End([End])

    Start --> CallFunc --> RaisesNI
    RaisesNI -- Yes --> RaiseNI
    RaisesNI -- No --> ToImplement --> CheckDF
    CheckDF -- Yes --> NotEnough --> End
    CheckDF -- No --> ComputeMask --> IfCols
    IfCols -- Yes --> NotEnough --> End
    IfCols -- No --> ComputeCorr --> MakeMask --> ReadConfig --> CallPlot --> ConvertToString --> ReturnResult --> End

## Implementation guidance (explicit, reimplementable steps):
The following algorithm is a concrete recommended implementation for a developer to follow if they replace the NotImplementedError:

1. Validate inputs
    - If not isinstance(config, Settings): raise TypeError("config must be a Settings instance")
    - Attempt: df = pandas.DataFrame(df). If this raises (TypeError/ValueError), raise ValueError("df must be a DataFrame-like object")

2. Short-circuit for trivial inputs
    - If df is None or df.shape[1] < 2:
        * Use warnings.warn("Not enough variables to compute missingness correlations") and return a short HTML snippet or an empty string depending on project conventions.

3. Compute missingness matrix
    - missing_bool = df.isnull().astype(int)  # DataFrame of 0/1 missing indicators

4. Compute pairwise correlation
    - Use Pearson correlation by default:
        corr = missing_bool.corr(method="pearson")
    - Alternative (optional): allow "jaccard" similarity via config; if chosen, compute pairwise Jaccard indices.

5. Build mask for plotting
    - import numpy as np
    - mask = np.triu(np.ones(corr.shape, dtype=bool))

6. Read plotting parameters (with safe defaults)
    - figsize, fontsize, labels, label_rotation, cmap, normalized_cmap, cbar
    - Fall back to sensible defaults if config entries are missing.

7. Plot and render
    - Delegate plotting to ydata_profiling.visualisation.plot.missing_heatmap:
        from ydata_profiling.visualisation.plot.missing_heatmap import missing_heatmap as plot_missing_heatmap
        ax = plot_missing_heatmap(corr, mask=mask, figsize=figsize, fontsize=fontsize, labels=labels, label_rotation=label_rotation, cmap=cmap, normalized_cmap=normalized_cmap, cbar=cbar)
    - Convert axis to image:
        figure = ax.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        data = base64.b64encode(buffer.read()).decode("ascii")
        html = f'<img src="data:image/png;base64,{data}" alt="Missingness heatmap" />'
        matplotlib.pyplot.close(figure)
        return html

8. Error handling
    - Wrap plotting and conversion in try/except. On exceptions:
        * If config has strict mode, raise RuntimeError with the plotting exception chained.
        * Otherwise, warnings.warn and return a fallback string describing the failure.

## Examples (intended usage — will raise NotImplementedError until implemented):
Example: calling the current stub
    try:
        html = missing_heatmap(config, df)
    except NotImplementedError:
        # The function is a stub in the current codebase
        handle_stub_case()

Example: expected usage after implementing the recommended algorithm
    html_snippet = missing_heatmap(config, df)
    # html_snippet is safe to embed in the report HTML

Notes:
    - The present source raises NotImplementedError; any behavior beyond that is a recommended implementation plan and not the current behavior.
    - Implementers should add unit tests that verify behavior for:
        * DataFrames with zero/one/two/many columns.
        * DataFrames with no missing values.
        * Very wide DataFrames (consider downsampling or disabling annotation).

## `src.ydata_profiling.model.missing.get_missing_active` · *function*

## Summary:
Return the subset of missingness-diagram configurations that are enabled and valid for the table statistics provided, i.e., the diagrams that should be generated for the dataset.

## Description:
This function constructs a canonical mapping of available missingness visualizations ("bar", "matrix", "heatmap") to their metadata and plotting functions, then filters that mapping according to two things:
1. The repository configuration flag for each diagram (config.missing_diagrams[name] must be truthy).
2. Minimal data requirements expressed using table_stats (for example, requiring a minimum number of variables with missing values).

Known callers:
- None discovered by static scan in the provided snapshot.
- Typical usage (integration context): invoked by the report-generation or dashboard assembly code during the "missingness analysis" / "visualisations selection" stage, when deciding which missingness diagrams to produce and embed in the report for a given dataset.

Why this logic is extracted:
- Responsibility separation: centralizes the selection logic (available diagrams, per-diagram minimum-data requirements, and config gating) in a single place so the rest of the report pipeline can simply iterate over the resulting active mapping and render each enabled diagram. This prevents duplication and ensures consistent behavior across the reporting code.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings (or Settings-like object).
        - Required attributes:
            * missing_diagrams: a mapping (e.g., dict) that is indexable by diagram name and yields a truthy/falsey flag indicating whether that diagram is enabled. The function performs config.missing_diagrams[name].
        - Notes:
            * If config has no attribute missing_diagrams, an AttributeError will be raised.
            * If config.missing_diagrams exists but lacks a required key for a diagram, a KeyError will be raised.

    table_stats (dict)
        - Type: dict
        - Required keys:
            * "n_vars_with_missing" (int): number of variables (columns) that contain at least one missing value.
            * "n_vars_all_missing" (int): number of variables that are entirely missing (all values missing).
        - Notes:
            * These keys are accessed directly; missing keys produce a KeyError.
            * Values are compared to per-diagram integer thresholds (min_missing).

## Returns:
    Dict[str, Any]
    - A filtered mapping containing only the diagrams that passed both the configuration and data-availability checks.
    - Keys: diagram name strings such as "bar", "matrix", "heatmap".
    - Values: the original per-diagram settings dictionaries (containing at least the fields present in the source: "min_missing", "name", "caption", "function").
    - Possible return shapes:
        * Non-empty dict with one or more diagram entries when some diagrams are active.
        * Empty dict {} when no diagram passes the filters (e.g., all disabled in config or the data fails thresholds).

## Raises:
    AttributeError
        - If config does not expose the attribute missing_diagrams (e.g., config has no missing_diagrams attribute), an AttributeError will occur at runtime.

    KeyError
        - If config.missing_diagrams exists but does not contain an entry for one of the canonical diagram names ("bar", "matrix", "heatmap"), attempting to read config.missing_diagrams[name] raises KeyError.
        - If table_stats does not contain "n_vars_with_missing" or "n_vars_all_missing", accessing table_stats[...] raises KeyError.

    (No other exceptions are raised directly by this function. Exceptions occurring when the stored "function" objects are later called are not raised here.)

## Constraints:
Preconditions:
    - config must be a Settings-like object with attribute missing_diagrams that is indexable with the canonical diagram names.
    - table_stats must be a dict containing at least the integer keys "n_vars_with_missing" and "n_vars_all_missing".
    - The per-diagram "min_missing" thresholds in the built-in mapping are integer values (0 or 2 in the current implementation).

Postconditions:
    - The returned dict only includes diagrams where:
        1) config.missing_diagrams[name] is truthy, and
        2) table_stats["n_vars_with_missing"] >= settings["min_missing"], and
        3) for the "heatmap" diagram additionally:
           table_stats["n_vars_with_missing"] - table_stats["n_vars_all_missing"] >= settings["min_missing"]
    - The function does not mutate config or table_stats.
    - The returned values are references to the same per-diagram setting dicts constructed in the function (i.e., no deep copy).

## Side Effects:
    - None: the function only constructs and returns an in-memory dictionary. It does not perform I/O, plotting, or external state mutation.
    - Note: the returned mapping contains "function" callables (missing_bar, missing_matrix, missing_heatmap); invoking those functions later will have their own side effects (plotting, resource allocation), but get_missing_active itself does not call them.

## Control Flow:
flowchart TD
    Start[Start]
    BuildMap[Build canonical missing_map with entries for: bar, matrix, heatmap]
    Iterate[For each (name, settings) in missing_map.items()]
    CheckConfig{config.missing_diagrams[name] is truthy?}
    CheckGlobalMin{table_stats["n_vars_with_missing"] >= settings["min_missing"]?}
    HeatmapExtraCond{Name == "heatmap"?}
    HeatmapCheck{(n_vars_with_missing - n_vars_all_missing) >= settings["min_missing"]?}
    Include[Include diagram in result]
    Exclude[Exclude diagram from result]
    Return[Return filtered mapping]
    End[End]

    Start --> BuildMap --> Iterate --> CheckConfig
    CheckConfig -- no --> Exclude --> Iterate
    CheckConfig -- yes --> CheckGlobalMin
    CheckGlobalMin -- no --> Exclude --> Iterate
    CheckGlobalMin -- yes --> HeatmapExtraCond
    HeatmapExtraCond -- no --> Include --> Iterate
    HeatmapExtraCond -- yes --> HeatmapCheck
    HeatmapCheck -- yes --> Include --> Iterate
    HeatmapCheck -- no --> Exclude --> Iterate
    Iterate --> Return --> End

## Examples:
Example 1 — simple enabled diagrams:
    - config.missing_diagrams = {"bar": True, "matrix": True, "heatmap": False}
    - table_stats = {"n_vars_with_missing": 3, "n_vars_all_missing": 0}
    - Result: entries for "bar" and "matrix" are returned (both meet min_missing == 0 and are enabled). "heatmap" is excluded by config flag.

Example 2 — heatmap requires partially-missing variables:
    - config.missing_diagrams = {"bar": True, "matrix": True, "heatmap": True}
    - table_stats = {"n_vars_with_missing": 3, "n_vars_all_missing": 2}
      Explanation: There are 3 columns with any missing values, but 2 columns are completely missing; only 1 column has partial missingness.
    - Since heatmap.min_missing == 2, heatmap condition requires (3 - 2) >= 2 → 1 >= 2 is false.
    - Result: "bar" and "matrix" are returned; "heatmap" is excluded because too few partially-missing variables.

Example 3 — no diagrams enabled:
    - config.missing_diagrams = {"bar": False, "matrix": False, "heatmap": False}
    - table_stats = {"n_vars_with_missing": 10, "n_vars_all_missing": 0}
    - Result: {} (empty dict) because all diagrams are disabled in config.

Notes and implementation hints:
    - The canonical mapping inside the function currently sets "min_missing" thresholds to 0 for "bar" and "matrix", and to 2 for "heatmap". Changing those thresholds requires updating the mapping in this function.
    - Callers should validate that config.missing_diagrams contains the expected keys or handle AttributeError/KeyError if they wish to be defensive.
    - The returned mapping can be iterated to call each diagram's "function" with the data when rendering the report.

## `src.ydata_profiling.model.missing.handle_missing` · *function*

## Summary:
Wraps a callable to catch ValueError raised by that callable and attempt to emit a warning; returns a wrapper callable that forwards arguments to the original function.

## Description:
This function returns a wrapper around a provided callable so that ValueError exceptions raised by the wrapped function are intercepted and trigger a warning flow instead of being directly re-raised by the wrapped code (intended behavior). The wrapper is implemented as an inner function that forwards positional and keyword arguments to the wrapped function and contains an inner helper warn_missing to issue the warning.

Known callers within the provided context:
- No call sites or importers of this specific function were available in the provided source context. It is intended for use wherever a callable might raise ValueError due to missing data and the caller wishes to surface a warning instead of failing immediately.

Why this logic is extracted into its own function:
- Responsibility boundary: isolates "ValueError -> user warning" logic from the main computation so multiple functions can share the same missing-data handling policy without duplicating error handling code.
- Reusability: provides a single place to modify how missing-value related errors are reported (for example, upgrading a warning to a logger message or changing the message format).

## Args:
    name (str): A short identifier used when composing the warning message about the missing data (e.g., column name). Must be a human-readable identifier.
    fn (Callable): The callable to wrap. The wrapper will call fn(*args, *kwargs) as written in the source.

Notes about interdependencies:
- The wrapper forwards the positional and keyword arguments it receives to fn; however, due to a bug in the implementation (see Constraints), keyword arguments may not be forwarded as expected.

## Returns:
    Callable: A function (inner) with signature (*args, **kwargs) -> Any that:
      - On successful execution of fn, returns whatever fn returns.
      - If fn raises ValueError, the wrapper attempts to call an internal warn_missing helper (which issues a warnings.warn). The original ValueError is not explicitly re-raised by the wrapper in the source.
      - Because warn_missing as implemented will itself raise an exception at runtime (NameError), the wrapper may not suppress the original ValueError in practice and instead propagate a NameError.

Edge-case return values:
- If fn completes normally: the wrapper returns fn(...)'s return value.
- If fn raises ValueError:
    - Intended: None (by handling the exception and not returning a value).
    - Actual (per source): warn_missing will reference an undefined identifier and raise NameError; therefore, the wrapper will propagate NameError rather than returning None or suppressing the ValueError.

## Raises:
    - NameError: If fn raises ValueError, the except block calls warn_missing which invokes warnings.warn(f). Because f is not defined or the f-string content is missing in the source, a NameError will be raised at that point.
    - TypeError: If the wrapper is called with keyword arguments, the wrapper calls fn(*args, *kwargs) (note the single asterisk applied to kwargs). Passing a dict to *kwargs will expand its keys as positional arguments — if keys are not appropriate for positional parameters this can cause a TypeError during the call. Specifically:
        * If kwargs is non-empty, using *kwargs will iterate over the dict's keys and pass them as additional positional arguments to fn, likely producing an unexpected TypeError from fn or from Python if signature mismatch occurs.
    - Any exceptions raised by fn on the initial call (other than ValueError) will propagate unchanged.

## Constraints:
Preconditions:
    - name must be a valid string identifier (no enforcement in code; used for composing the intended warning).
    - fn must be callable and accept the positional and/or keyword arguments that will be forwarded by the wrapper. Note: due to a bug the forwarding of keyword arguments is incorrect.

Postconditions:
    - If fn completes normally, the wrapper returns fn(...)'s return value unchanged.
    - If fn raises ValueError, the source attempts to warn and swallow, but due to an implementation bug the wrapper will raise NameError instead of cleanly transforming the ValueError into a warning and returning None.

## Side Effects:
    - Emits a Python warning via warnings.warn when the except branch executes — intended side effect. In practice the call to warnings.warn uses an undefined format expression and will raise NameError before a warning can be emitted successfully.
    - No I/O, network, global state, or external service interactions are performed by the function itself.

## Control Flow:
flowchart TD
    A[Call wrapper inner(*args, **kwargs)] --> B[Call fn with forwarded args]
    B --> |fn returns successfully| C[Return fn(...) result]
    B --> |fn raises ValueError| D[Enter except block]
    D --> E[Call warn_missing(name, str(e))]
    E --> F[Attempt to warnings.warn(f) — f is undefined]
    F --> |NameError raised| G[NameError propagates out of wrapper]
    B --> |fn raises other exception| H[Other exception propagates out of wrapper]

## Examples:
1) Typical (successful) usage:
    - Suppose fn returns a DataFrame and does not raise ValueError:
      The wrapper will call fn with forwarded arguments and return the DataFrame unchanged.

2) Example showing problematic behavior when fn raises ValueError:
    - If fn raises ValueError("missing column"):
        The wrapper will catch ValueError and attempt to call warn_missing.
        warn_missing calls warnings.warn(f) where f is undefined in the source; this triggers a NameError which propagates to the caller.
        As a result, instead of receiving a warning and a None return, the caller sees a NameError.
    - Example flow (pseudo):
        wrapped = handle_missing("colA", fn)
        wrapped(df)  # If fn(df) raises ValueError -> NameError observed due to bug

3) Example showing risk with keyword arguments:
    - If the wrapper is invoked with keyword arguments, e.g. wrapped(a=1, b=2), the wrapper forwards them as fn(*args, *kwargs) which expands the dict keys as positional arguments. This will likely produce a TypeError or pass incorrect positional values to fn depending on fn's signature.

Implementation notes for a correct reimplementation:
    - Use fn(*args, **kwargs) to correctly forward keyword arguments.
    - Construct a meaningful warning message inside warn_missing, e.g. warnings.warn(f"Missing {missing_name}: {error}").
    - Decide whether to suppress the ValueError (return None or a sentinel) or re-raise after warning — document and implement that policy explicitly.

## `src.ydata_profiling.model.missing.get_missing_diagram` · *function*

## Summary:
Return a compact "missing" diagram dictionary for a DataFrame row/column selection by invoking a configured missing-data generator; returns None when no diagram can be produced.

## Description:
This function is a small adapter that (1) guards against empty input DataFrames, (2) invokes a missing-data computation function (wrapped by the project's missing-data error handler), and (3) packages the result into a standard dictionary with metadata for downstream reporting or rendering.

Known callers within the provided context:
- No explicit call sites were found in the provided source snapshot. In the profiling pipeline this function is intended to be called when constructing per-variable or per-report missing-value visualizations as part of the dataset profiling steps (for example, during the "missing values" stage of a variable or dataset report).

Why this logic is extracted into its own function:
- Responsibility boundary: centralizes the small sequence of checks and packaging for missing-value diagrams (empty-DataFrame check, invoking the configured missing-generator, normalizing a non-None result into a fixed dictionary shape). This keeps callers simple and enforces a common output shape across different missing-function implementations.
- Reusability: allows multiple pipeline stages to request a missing diagram by passing different settings without duplicating the empty-check and packaging code.

## Args:
    config (Settings): Global profiling configuration object used by the missing-data generator. The function forwards this object to the underlying missing generator.
    df (pandas.DataFrame): The DataFrame (or DataFrame slice) on which the missing-data computation should run. Must support len(df).
    settings (Dict[str, Any]):
        - Required keys:
            * "name" (str): identifier to include in the returned dictionary under "name".
            * "function" (Callable): a callable (or descriptor) that will be passed into handle_missing and ultimately invoked as handle_missing(...)(config, df). The callable is expected to accept (config, df) or to be compatible with the wrapper returned by handle_missing.
            * "caption" (str): textual caption used in the returned dictionary under "caption".
        - Additional keys are allowed but ignored by this function.
    Notes on interdependencies:
        - settings["function"] must be suitable for wrapping by handle_missing(name, fn) and then being called with two positional arguments (config, df). If settings lacks any required key, a KeyError will be raised by this function at the point of access.

## Returns:
    Optional[Dict[str, Any]]:
        - None when:
            * df is empty (len(df) == 0), or
            * the wrapped missing-function returns None to signal that no diagram is available.
        - Otherwise, a dictionary with the following shape:
            {
                "name": settings["name"],
                "caption": settings["caption"],
                "matrix": <result from wrapped missing-function>
            }
        - The "matrix" value is returned verbatim from the wrapped missing-function and may be any structure that function chooses (commonly a 2D array, nested list, dict, or DataFrame-like object). No additional validation or transformation is performed.

## Raises:
    - KeyError: If settings does not contain "name", "function", or "caption".
    - Any exception propagated from handle_missing(...) or the wrapped function it returns. In particular:
        * Exceptions raised by the wrapped function (other than those specifically handled inside handle_missing) will propagate unchanged.
        * Note: the current implementation of handle_missing in the codebase has a known bug where handling a ValueError inside the wrapper may raise a NameError instead of cleanly emitting a warning; callers should be prepared for such exceptions when invoking get_missing_diagram.

## Constraints:
    Preconditions:
        - df must be a pandas.DataFrame or behave like one with a defined length (len(df)) and be appropriate for the configured missing-function.
        - settings must include the keys "name", "function", and "caption".
        - settings["function"] should be a callable compatible with being called via handle_missing(...)(config, df).

    Postconditions:
        - If a non-None dictionary is returned, it is guaranteed to contain keys "name" and "caption" copied from settings and "matrix" equal to the wrapped-function's return value.
        - No mutation of the input df or settings is performed by this function itself (mutations could occur inside the wrapped function).

## Side Effects:
    - This function itself performs no I/O, network calls, or global state mutations.
    - It calls handle_missing(...)(config, df). The wrapped function may issue warnings, log messages, or mutate external state; handle_missing is intended to convert certain ValueError errors into warnings (see handle_missing documentation). Due to a known bug in the current handle_missing implementation, handling a ValueError may instead raise a NameError.

## Control Flow:
flowchart TD
    Start[Start: get_missing_diagram(config, df, settings)] --> CheckEmpty{len(df) == 0?}
    CheckEmpty -- Yes --> ReturnNoneEmpty[Return None]
    CheckEmpty -- No --> BuildWrapper[Call handle_missing(settings["name"], settings["function"])]
    BuildWrapper --> InvokeWrapper[Invoke wrapper(config, df)]
    InvokeWrapper --> |wrapper returns None| ReturnNoneResult[Return None]
    InvokeWrapper --> |wrapper returns result| BuildDict[Construct {'name','caption','matrix'}]
    BuildDict --> ReturnDict[Return constructed dict]
    InvokeWrapper --> |wrapper raises exception| PropagateErr[Propagate exception to caller]

## Examples:
1) Typical usage (successful):
    - Given a non-empty DataFrame and a valid missing-function, the call returns a dict:
      settings = {"name": "missing_heatmap", "function": missing_fn, "caption": "Missing values"}
      result = get_missing_diagram(config, df, settings)
      # If missing_fn produces a matrix-like object, result will be:
      # {"name": "missing_heatmap", "caption": "Missing values", "matrix": <matrix>}

2) Empty DataFrame:
    - If df is empty (zero rows), the function returns None immediately:
      result = get_missing_diagram(config, empty_df, settings)  # -> None

3) Error handling recommendation:
    - Because the wrapped missing-function or handle_missing may raise exceptions, callers that integrate this function into a larger profiling pipeline should defensively handle exceptions:
      Try invoking get_missing_diagram(...) inside a try/except, log or record failures, and continue profile construction when possible.

4) Missing settings keys:
    - If settings is missing "name" or "caption" or "function", the function will raise KeyError at the access site. Callers should validate settings before calling or catch KeyError and handle it as a configuration error.

