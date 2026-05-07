# `missing.py`

## `src.ydata_profiling.visualisation.missing.get_font_size` · *function*

## Summary:
Choose a numeric font size (points) for labeling columns in plots by selecting a base size from the column count and scaling it down proportionally if labels are long.

## Description:
This small utility encapsulates a heuristic used by plotting code to pick a font size that balances readability and space constraints when drawing column labels in missing-value visualisations.

Typical callers:
- Plotting routines that render column labels for missing-value visualisations (for example, functions that produce missing-bar, missing-heatmap, or missing-matrix plots).
- Any other visualization helper that needs a consistent, heuristic font size based on the number and length of labels.

Why this is a separate function:
- Centralises the font-sizing policy so multiple plot types use a consistent rule.
- Keeps plot rendering code simpler by separating visual-sizing logic from layout/painting logic.
- Makes it easy to adjust the sizing heuristic in one place.

## Args:
    columns (List[str]):
        - A non-empty list of label values (strings are expected).
        - Each element must support len(); the function uses len(label) to determine label lengths.
        - The result depends on:
            * len(columns) — determines the base font size tier
            * max(len(label) for label in columns) — determines a shrink multiplier

## Returns:
    float: Suggested font size in points.
    - Calculation steps:
        1. Select a base font size according to number of columns:
            - len(columns) < 20  -> base = 13.0
            - 20 <= len(columns) < 40 -> base = 12.0
            - 40 <= len(columns) < 60 -> base = 10.0
            - len(columns) >= 60 -> base = 8.0
        2. Compute multiplier = min(1.0, 20.0 / max_label_length)
        3. Return base * multiplier
    - Behavior notes:
        - If the longest label length <= 20, multiplier is 1.0 and the font size equals the base.
        - If the longest label length > 20, the font size is reduced proportionally (e.g., 20.0 / length).
    - Value range:
        - A positive float not exceeding the chosen base value for the computed column-count tier.

## Raises:
    ValueError:
        - Raised by calling max(...) on an empty sequence when columns == [].
    ZeroDivisionError:
        - Occurs if max_label_length == 0 (for example, columns contains only empty strings), because the code computes 20.0 / max_label_length.
    TypeError:
        - If any element in columns does not support len() (e.g., None), len(label) will raise TypeError.

## Constraints:
    Preconditions:
        - columns must be a non-empty iterable of items that implement __len__.
        - To avoid ZeroDivisionError, at least one label should have length > 0.
    Postconditions:
        - The function returns a deterministic positive float (unless an exception is raised).
        - No external state is modified.

## Side Effects:
    - None. Pure computation: no I/O, no global mutation, no external calls.

## Control Flow:
flowchart TD
    Start((Start))
    Start --> EmptyCheck{columns empty?}
    EmptyCheck -- Yes --> RaiseValueError[Raise ValueError (max on empty)]
    EmptyCheck -- No --> ComputeMax[Compute max_label_length = max(len(label) for label in columns)]
    ComputeMax --> ChooseBase[Choose base font_size by len(columns) (13,12,10,8)]
    ChooseBase --> ComputeMultiplier[Compute multiplier = min(1.0, 20.0 / max_label_length)]
    ComputeMultiplier --> PossibleZeroDiv{max_label_length == 0?}
    PossibleZeroDiv -- Yes --> RaiseZeroDiv[Raise ZeroDivisionError (20.0/0)]
    PossibleZeroDiv -- No --> Multiply[font_size = base * multiplier]
    Multiply --> Return[Return font_size]
    RaiseZeroDiv --> End((End))
    RaiseValueError --> End
    Return --> End

## Examples:
- Small set of short labels (no reduction):
    - Input: columns = ['age', 'height', 'weight']
    - len(columns) = 3 -> base = 13.0
    - max_label_length = 6 -> multiplier = min(1.0, 20.0/6) = 1.0
    - Returned font size = 13.0

- Many columns with a long label (scaled down):
    - Input: columns = ['c' * 25 for _ in range(25)]  (25 columns, each label length 25)
    - len(columns) = 25 -> base = 12.0
    - max_label_length = 25 -> multiplier = min(1.0, 20.0/25) = 0.8
    - Returned font size = 12.0 * 0.8 = 9.6

- Many columns, very long label (more reduction):
    - Input: 75 columns, one label length 50
    - len(columns) = 75 -> base = 8.0
    - max_label_length = 50 -> multiplier = 20.0/50 = 0.4
    - Returned font size = 8.0 * 0.4 = 3.2

- Error cases and safe usage:
    - columns = [] -> calling the function raises ValueError. Validate input before calling or catch ValueError.
    - columns = ['', ''] -> max_label_length == 0 -> calling the function raises ZeroDivisionError.
    - Safe pattern:
        - Ensure columns is non-empty and at least one label has length > 0, or wrap the call in try/except to handle ValueError and ZeroDivisionError.

## `src.ydata_profiling.visualisation.missing.plot_missing_matrix` · *function*

## Summary:
Render a missingness matrix plot for the provided boolean presence mask and column labels, adjust layout, and return the resulting image reference (data URI or asset path) as a string suitable for embedding in reports.

## Description:
This function is a small orchestration wrapper that:
- Calls the low-level missing_matrix plotting helper to draw a grid where present (not-missing) cells are colored and missing cells are white.
- Adjusts subplot spacing to fixed margins appropriate for this plot.
- Encodes and returns the produced figure using the project's image-export helper.

Known callers within the codebase:
- No direct static callers were discovered in the repository scan. Typical call sites (conceptually) are report-generation or visualization pipelines that build a missing-values section (e.g., a "missing" page in a profiling report) and need a ready-to-embed image string.

Why this is extracted into its own function:
- Keeps the high-level orchestration (choose fontsize, apply theme color, fine-tune margins, and export image) separate from the pixel/figure drawing implementation (missing_matrix) and the export/encoding logic (plot_360_n0sc0pe).
- Enforces a consistent visual style and pipeline: compute fontsize → draw → adjust → export.
- Makes it easy to reuse or test the export step independently of plotting internals.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: holds plot/export configuration and theme colors used by the function.
        - Expected fields (accessed by this function):
            * config.html.style.primary_colors[0] — a hex color string used as the plot "present" color
            * config.plot.missing.force_labels — a boolean indicating whether to force x-axis labels
            * Other fields may be read later by plot_360_n0sc0pe (e.g., config.plot.image_format, config.html.inline, config.html.assets_path, config.plot.dpi)
        - The Settings object is read but not mutated.

    notnull (Any):
        - Type: a boolean mask representing presence (True) and absence (False).
        - Expected shapes/semantics:
            * Must be indexable by boolean assignment into an array shaped (nrows, len(columns)), i.e., it should be a numpy boolean array, pandas DataFrame/ndarray-like mask, or any object that when used as an index matches the grid shape constructed by the plotting helper.
            * The caller should ensure that notnull is compatible with height = nrows and width = len(columns); mismatched shapes will raise indexing or broadcasting errors in the plotting helper.
        - This function does not validate or transform notnull beyond passing it into missing_matrix.

    columns (List[str]):
        - Type: list of column labels (strings).
        - Constraints:
            * Must be non-empty (get_font_size will raise on empty input).
            * Each element must support len(); extremely long labels can reduce computed fontsize.
        - Used to set x-axis tick labels and to compute a heuristic fontsize.

    nrows (int):
        - Type: integer number of rows to display/plot (passed as height to the plotting helper).
        - Expected values:
            * Positive integer representing the displayed number of rows.
            * Should match the first dimension of notnull (or be compatible via broadcasting in the plotting helper).

Interdependencies and derived values:
- The function computes fontsize as get_font_size(columns) / 20 * 16 (equivalently get_font_size(columns) * 0.8).
- The present-color is computed as hex_to_rgb(config.html.style.primary_colors[0]).
- Fixed figsize is (10, 4).
- The labels flag is taken from config.plot.missing.force_labels.

## Returns:
    str:
        - The returned string is produced by plot_360_n0sc0pe(config).
        - Possible return forms:
            * If config.html.inline is True and image_format == "png": a data URI string like "data:image/png;base64,<payload>" (base64-encoded PNG).
            * If config.html.inline is True and image_format == "svg": the raw SVG string.
            * If config.html.inline is False: a relative asset path string (e.g., "<prefix>/images/<uuid>.png") where the image file has been written under config.html.assets_path.
        - On success, the function returns the string that callers can embed directly into HTML reports or reference as an asset path.

## Raises:
    - Any exception raised by get_font_size(columns):
        * ValueError if columns is an empty sequence (max() on empty).
        * ZeroDivisionError if all provided labels are empty strings (max label length == 0).
        * TypeError if an element of columns does not support len().
    - Any exception raised by hex_to_rgb(config.html.style.primary_colors[0]) if the color value is missing or malformed (implementation-dependent).
    - Any exception from missing_matrix(...) if the provided notnull mask is shape-incompatible with (nrows, len(columns)) or contains unexpected types (commonly IndexError, ValueError, or TypeError originating from numpy/matplotlib operations).
    - Any exception propagated from plot_360_n0sc0pe(config):
        * ValueError if an unsupported image format is configured.
        * ValueError if config.html.inline is False but config.html.assets_path is None.
    - Note: This function does not catch these exceptions; it lets them propagate to the caller.

## Constraints:
Preconditions (what must be true before calling):
    - columns must be a non-empty list-like of strings (or objects supporting len()) and not all empty.
    - nrows should be a positive integer consistent with the notnull mask.
    - notnull must be a boolean mask broadcastable/indexable into the grid of shape (nrows, len(columns)).
    - config must provide the fields accessed above (theme color and plot/export settings). Missing config attributes can cause AttributeError or ValueError downstream.

Postconditions (guarantees after return):
    - A string referencing the generated image is returned (data URI or asset path), unless an exception is raised.
    - Matplotlib state relating to the saved figure is cleaned up by plot_360_n0sc0pe (it calls plt.close()); the function itself adjusts subplot spacing prior to saving.
    - The Settings object and the notnull/columns inputs are not mutated by this function.

## Side Effects:
    - Mutates Matplotlib global state temporarily by creating figures/axes inside missing_matrix and adjusting subplot parameters (plt.subplots_adjust). The image-export helper closes the figure before returning (so resources are freed).
    - May write an image file to disk when config.html.inline is False (writes to config.html.assets_path). The path returned in that case is a relative suffix; the actual file is created by plot_360_n0sc0pe.
    - No network I/O is performed by this function itself; any network effects would be indirect via custom Settings behavior (not standard).
    - No global variables in the codebase are mutated (beyond Matplotlib state described above).

## Control Flow:
flowchart TD
    Start((Start))
    Start --> ComputeFontsize[Compute fontsize = get_font_size(columns) / 20 * 16]
    ComputeFontsize --> ComputeColor[Compute color = hex_to_rgb(config.html.style.primary_colors[0])]
    ComputeColor --> CallMissingMatrix[Call missing_matrix(notnull, height=nrows, columns=columns, figsize=(10,4), fontsize=..., color=..., labels=...)]
    CallMissingMatrix --> SubplotAdjust[Call plt.subplots_adjust(left=0.1,right=0.9,top=0.7,bottom=0.2)]
    SubplotAdjust --> Export[Call plot_360_n0sc0pe(config) to save/encode and close figure]
    Export --> ReturnResult[Return the resulting string (data URI or asset path)]
    CallMissingMatrix -->|error| PropagateError[Propagate exception to caller]
    Export -->|error| PropagateError

## Examples:
- Typical inline-PNG usage (conceptual):
    1) Prepare inputs:
        - config: Settings with config.html.inline = True and config.plot.image_format = "png"
        - notnull: a boolean numpy array shaped (nrows, n_columns)
        - columns: list of column names (non-empty)
        - nrows: integer equal to notnull.shape[0]
    2) Call:
        - result_string = plot_missing_matrix(config, notnull, columns, nrows)
    3) result_string will be a "data:image/png;base64,..." string suitable for embedding in an <img> tag.

- Handling possible errors:
    - If columns == []:
        - get_font_size(columns) raises ValueError. Callers should validate columns is non-empty or wrap the call:
            try:
                img = plot_missing_matrix(config, notnull, columns, nrows)
            except ValueError as e:
                # handle missing/invalid column labels
                ...

    - If the runtime should produce a file asset but config.html.assets_path is not set:
        - plot_360_n0sc0pe(config) raises ValueError("config.html.assets_path may not be none").
        - Ensure config.html.assets_path is set or use inline mode.

Notes and implementation hints:
    - The plotting helper missing_matrix expects the boolean mask to align with (height=nrows, width=len(columns)). It uses boolean indexing to write color/white pixels into an RGB grid; therefore correct mask shape is critical.
    - The effective fontsize is a scaled version of the project's get_font_size heuristic: fontsize_effective = get_font_size(columns) * 0.8.
    - The function uses a fixed figsize of (10, 4) and fixed subplot margins; if different layout is desired, consider calling missing_matrix directly or adjusting config before calling.
    - The function intentionally leaves error handling to callers so report-generation code can choose how to surface or recover from errors (e.g., show a placeholder image or a textual warning).

## `src.ydata_profiling.visualisation.missing.plot_missing_bar` · *function*

## Summary:
Render a missing-values bar chart into the current Matplotlib figure, adjust layout and grid visibility, and return a serialized image reference (inline SVG/PNG or asset path) according to the provided config.

## Description:
This small visualization helper delegates the actual drawing to the lower-level plotting helper, then performs presentation tweaks (disable grid lines and adjust subplot margins) before serializing the figure using the repository's image-export helper.

Known callers and typical context:
- Report-generation pipeline components that assemble the "missing values" section of a profiling report. These callers compute per-column non-null counts (notnull_counts) and call this function to produce an embeddable image string.
- Higher-level model-layer helpers that prepare data and call visualization functions (e.g., a missing-values model function) typically call this function after computing notnull_counts and deciding row-count (nrows).
- In short: invoked during report rendering after non-null counts are computed and before embedding the resulting image into HTML or assets.

Why this logic is extracted:
- Separates drawing parameters/layout adjustments and image-export concerns from where non-null counts are computed.
- Keeps plotting/serialization consistent across the codebase by centralizing color/font/label decisions and using the shared export helper (plot_360_n0sc0pe).
- Makes the visualization step reusable from different callers without duplicating Matplotlib/serialization boilerplate.

## Args:
    config (Settings):
        - A Settings-like object containing rendering preferences and HTML exporting configuration.
        - Required nested attributes (accessed directly by this function):
            * config.html.style.primary_colors: indexable (first element used as hex color string)
            * config.plot.missing.force_labels: bool (passed as labels)
            * config.plot.image_format and config.html.inline / config.html.assets_path may be read indirectly by plot_360_n0sc0pe
        - If these attributes are missing, an AttributeError will be raised by attribute access.

    notnull_counts (list or pandas.Series):
        - Sequence-like of per-column non-null counts (integers).
        - Length should match len(columns). The plotting helper expects numeric counts that support division by nrows.
        - Accepts either a pandas.Series (recommended) or a list/NumPy array of integers.

    nrows (int):
        - Number of rows in the original dataset (denominator used to compute percentages in the bar plot).
        - Must be a positive integer (nrows > 0). If nrows == 0, division by zero will occur.

    columns (List[str]):
        - List of column names corresponding to notnull_counts. Used to compute an appropriate font size via get_font_size.
        - Must be non-empty and contain string-like elements supporting len(). If empty, get_font_size will raise ValueError; if the longest label has length 0, get_font_size may raise ZeroDivisionError.

## Returns:
    str:
        - A serialized representation of the rendered image determined by plot_360_n0sc0pe(config).
        - Possible return values:
            * Inline SVG string (UTF-8 XML) when config.html.inline is True and image_format == "svg".
            * A data URI string "data:image/png;base64,<base64-data>" when config.html.inline is True and image_format == "png".
            * A file-path suffix (string) pointing into the configured assets folder when config.html.inline is False (e.g., "prefix/images/<uuid>.svg" or ".png").
        - The exact format depends on Settings (config.plot.image_format and config.html.inline). See plot_360_n0sc0pe for exact serialization behavior.

## Raises:
    AttributeError:
        - If required nested attributes are missing on the provided config object (e.g., config.html, config.html.style, config.html.style.primary_colors, config.plot.missing.force_labels) the function's direct attribute access will raise AttributeError.

    TypeError:
        - If notnull_counts is None or not a sequence-like that supports element-wise division by nrows (this will typically surface inside missing_bar).

    ZeroDivisionError:
        - If nrows == 0 (division by zero when computing percentage in missing_bar).
        - If columns contains only empty strings, get_font_size may compute 20.0 / 0 and raise ZeroDivisionError.

    ValueError:
        - If get_font_size is called with an empty columns list it will raise ValueError.
        - plot_360_n0sc0pe may raise ValueError for unsupported image formats or if config.html.assets_path is None when config.html.inline is False.

    ValueError / TypeError / other exceptions from helpers:
        - hex_to_rgb can raise ValueError if the configured color string is not a valid hex color.
        - Matplotlib or underlying helpers may raise exceptions during plotting or saving (e.g., MemoryError, OSError); these propagate unless handled by callers.

## Constraints:
Preconditions:
    - config must be a Settings-like object with the nested attributes used here (see Args).
    - notnull_counts must be numeric counts aligned with columns, and nrows must be > 0.
    - columns must be non-empty and contain items with a non-zero length to avoid get_font_size raising.

Postconditions:
    - The current Matplotlib figure has been rendered and serialized by plot_360_n0sc0pe; the returned string references the saved image (inline or asset path).
    - The figure is closed by plot_360_n0sc0pe (it calls plt.close()), so no lingering open figure remains after return.
    - Grid lines for all axes in the current figure are disabled and subplot margins adjusted (left=0.1, right=0.9, top=0.8, bottom=0.3) prior to serialization.

## Side Effects:
    - Manipulates the current Matplotlib figure/axes (creates or reuses the current figure via the missing_bar helper).
    - Disables grid lines on every axis present in the current figure.
    - Adjusts subplot margins via plt.subplots_adjust.
    - Triggers image serialization that may:
        * Return an inline SVG or PNG data URI (no filesystem I/O), or
        * Write a file under config.html.assets_path when config.html.inline is False (filesystem I/O). This behavior is controlled by plot_360_n0sc0pe and Settings.
    - No other global state is intentionally mutated by this function beyond Matplotlib figure state and potential file writes performed by the export helper.

## Control Flow:
flowchart TD
    Start((Start))
    Start --> CallMissingBar[Call missing_bar(notnull_counts, nrows, figsize=(10,5), fontsize=get_font_size(columns), color=hex_to_rgb(config.html.style.primary_colors[0]), labels=config.plot.missing.force_labels)]
    CallMissingBar --> PlotCreated{missing_bar succeeds?}
    PlotCreated -- No --> PropagateException[Propagate plotting/validation exception]
    PlotCreated -- Yes --> DisableGrid[For each axis in current figure: set grid(False)]
    DisableGrid --> AdjustLayout[plt.subplots_adjust(left=0.1,right=0.9,top=0.8,bottom=0.3)]
    AdjustLayout --> Serialize[return plot_360_n0sc0pe(config)]
    Serialize --> ReturnResult[Return serialized string or propagate errors from plot_360_n0sc0pe]
    ReturnResult --> End((End))

## Examples:
- Typical usage (inline SVG preferred in many report contexts):
    - Preconditions: config.html.inline == True and config.plot.image_format == "svg"
    - Call:
        try:
            image_str = plot_missing_bar(config, notnull_counts, nrows, columns)
            # image_str is an SVG string that can be embedded directly in an HTML report.
        except (AttributeError, ValueError, ZeroDivisionError) as exc:
            # Handle missing config attributes or invalid input gracefully:
            # - log the problem, fall back to an alternative rendering, or omit the plot.
            handle_plot_error(exc)

- Defensive calling pattern to avoid empty-label errors:
    try:
        if not columns:
            # skip plotting or provide a default single empty label to avoid get_font_size ValueError
            image_str = ""
        else:
            image_str = plot_missing_bar(config, notnull_counts, nrows, columns)
    except ZeroDivisionError:
        # likely nrows == 0 or columns contain only empty strings; skip or supply defaults
        image_str = ""

- When config.html.inline is False (assets mode), be prepared to receive a file-path suffix:
    result = plot_missing_bar(config, notnull_counts, nrows, columns)
    # result might be 'assets-prefix/images/<uuid>.svg' — the caller must combine it with config.html.assets_path to form the absolute path when embedding.

Notes:
- This function assumes the callers have already validated/constructed notnull_counts and columns appropriately (lengths aligned and nrows positive). If you need robustness against missing Settings attributes, wrap attribute access (getattr) or validate config before calling.
- The underlying plotting helper missing_bar expects a pandas.Series in its canonical usage; passing a Series is recommended to preserve index/label behavior.

## `src.ydata_profiling.visualisation.missing.plot_missing_heatmap` · *function*

## Summary:
Create and render a missingness correlation heatmap for a set of columns: choose figure size and font size heuristically, draw the heatmap using the provided correlation matrix and mask, adjust subplot margins for long label lists, and return a rendered image reference (inline image string or filesystem path) suitable for embedding in the report.

## Description:
This function is a small orchestration wrapper that prepares plot dimensions and label sizing, calls the lower-level plotting routine that paints the heatmap, performs final layout adjustments, and hands the active matplotlib figure to the rendering helper that produces the final string to embed in the report.

Known callers within the codebase and typical context:
- No explicit direct call sites were found in the provided snapshot. In typical usage it is invoked by the missingness/overview section of the report generation pipeline when a missingness heatmap is required (for example, during the "missingness analysis" stage of generating an HTML report).
- Typical trigger: the report generator has computed a pairwise missingness correlation matrix (corr_mat) and an upper/lower triangular mask (mask) for a selection of columns and calls this function to produce the embeddable image.

Why this is a separate function:
- Encapsulates layout heuristics (figure height and font selection) and final rendering steps so the low-level missing_heatmap plotting function remains focused on drawing.
- Centralises the rules that adapt plot sizing for wide tables (columns count) so all missingness visualisations behave consistently.
- Allows tests to exercise layout/size logic independently of rendering logic.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: Global plotting/rendering configuration (controls image format, dpi, html inline vs assets, color map selection through config.plot.missing.cmap, and labels forcing via config.plot.missing.force_labels).
        - Required: yes.

    corr_mat (Any):
        - Type: matrix-like (pandas.DataFrame, numpy.ndarray, or similar) representing pairwise correlation/similarity of column-wise missingness.
        - Expectations:
            * Square matrix with shape (n_columns, n_columns).
            * Index/column labels are optional; if present they should match the provided columns list.
        - The function does not validate the matrix shape; an incompatible shape may raise errors in the plotting helper.

    mask (Any):
        - Type: boolean mask matrix (numpy.ndarray or similar) with the same shape as corr_mat that indicates entries to hide in the heatmap (typically an upper- or lower-triangular mask).
        - Passing None is acceptable only if the underlying plotting routine accepts None; otherwise a shape mismatch may arise.

    columns (List[str]):
        - Type: list of strings representing the column names shown as x/y tick labels.
        - Constraints:
            * Must be non-empty (get_font_size will raise ValueError on empty list).
            * At least one label should have length > 0 (otherwise get_font_size may raise ZeroDivisionError as it divides by max label length).
        - Interdependencies:
            * The number of elements in this list drives figure height and (indirectly) font size adjustments:
                - If len(columns) > 10, the height is increased in tiers.
                - If len(columns) > 40, font size is further reduced and subplot margins are tightened.

## Returns:
    str:
        - A string representing the rendered image. The exact format depends on config:
            * If config.html.inline is True:
                - For "svg": a raw SVG string is returned.
                - For "png": a base64-encoded data URI string is returned (data:image/png;base64,...).
            * If config.html.inline is False:
                - A relative file path (string) under config.html.assets_path / (config.html.assets_prefix + '/images/...') is returned.
        - Edge cases:
            * The underlying plot_360_n0sc0pe helper may raise ValueError for unsupported image formats or if config.html.assets_path is None when inline is False — those errors are propagated.
            * If plotting fails (e.g., seaborn/matplotlib error), the function does not catch it; exceptions propagate to the caller.

## Raises:
    ValueError:
        - If columns == [], get_font_size will raise ValueError when computing max label length.
        - If config.html.inline is False and config.html.assets_path is None, the downstream plot_360_n0sc0pe call raises ValueError.
        - If plot_360_n0sc0pe determines an unsupported image_format, it raises ValueError.

    ZeroDivisionError:
        - If all labels in columns are empty strings (max label length == 0), get_font_size performs 20.0 / 0 and raises ZeroDivisionError.

    TypeError:
        - If elements of columns do not support len() (e.g., None), get_font_size will raise TypeError during max(len(...)).

    Any plotting-related exception from the underlying missing_heatmap or matplotlib/seaborn:
        - Examples: shape mismatch between corr_mat and mask, invalid data types for heatmap. These exceptions are propagated.

## Constraints:
Preconditions:
    - config must be a valid Settings object with the expected attributes used here:
        * config.plot.missing.cmap (string) — colormap
        * config.plot.missing.force_labels (bool)
        * config.plot.image_format and config.html.* used later by plot_360_n0sc0pe
    - columns must be a non-empty list-like of strings with at least one non-empty string (to avoid ZeroDivisionError).
    - corr_mat and mask should be compatible shapes (square matrices of equal shape), or the plotting helper may raise.

Postconditions:
    - The function returns a string describing where the plot image can be retrieved or an inline representation.
    - The active matplotlib figure used to render the image is closed by the downstream plot_360_n0sc0pe helper before return (so no lingering open figures remain).
    - No input objects are mutated by this function.

## Side Effects:
    - Creates a matplotlib figure and axes via the missing_heatmap routine.
    - Delegates to plot_360_n0sc0pe, which:
        * May write an image file to disk (when config.html.inline is False) under config.html.assets_path.
        * May allocate an in-memory buffer and produce a base64 string (when inline).
        * Always closes the matplotlib figure it saves (plt.close()).
    - No network calls are made by this function itself, but disk I/O may occur via plot_360_n0sc0pe.
    - No global state is intentionally modified by this function other than through matplotlib state while the figure exists.

## Control Flow:
flowchart TD
    Start((Start))
    Start --> ComputeHeight[Set height = 4; if len(columns) > 10 then height += int((len(columns)-10)/5); height = min(height,10)]
    ComputeHeight --> ComputeFont[font_size = get_font_size(columns)]
    ComputeFont --> FontAdjust{len(columns) > 40?}
    FontAdjust -- Yes --> ReduceFont[font_size /= 1.4]
    FontAdjust -- No --> KeepFont[font_size unchanged]
    ReduceFont --> CallPlot
    KeepFont --> CallPlot
    CallPlot[Call missing_heatmap(corr_mat, mask, figsize=(10,height), fontsize=font_size, cmap=config.plot.missing.cmap, labels=config.plot.missing.force_labels)]
    CallPlot --> AdjustSubplots{len(columns) > 40?}
    AdjustSubplots -- Yes --> SubplotTight[plt.subplots_adjust(left=0.1,right=0.9,top=0.9,bottom=0.3)]
    AdjustSubplots -- No --> SubplotNormal[plt.subplots_adjust(left=0.2,right=0.9,top=0.8,bottom=0.3)]
    SubplotTight --> Render[Return plot_360_n0sc0pe(config)]
    SubplotNormal --> Render
    Render --> End((End))
    CallPlot --> PlottingError{seaborn/matplotlib error?}
    PlottingError -- Yes --> Propagate[Exception propagates to caller]
    PlottingError -- No --> Continue

## Examples:
- Typical inline PNG usage (happy path):
    - Preconditions:
        * config.html.inline == True
        * config.plot.image_format in {"png", "svg"}
        * corr_mat is a square pandas.DataFrame of pairwise missingness correlations
        * mask is a boolean numpy.ndarray with the same shape as corr_mat
        * columns is a list of column names matching corr_mat columns
    - Outcome: the function returns a base64 data URI (for png) or raw SVG string (for svg) suitable for embedding in HTML.

- Example of robust caller usage with error handling (pseudocode, not actual code):
    - Validate that columns is non-empty and contains at least one non-empty string before calling to avoid ValueError/ZeroDivisionError arising from get_font_size.
    - Wrap the call in try/except to handle plotting/rendering errors:
        * Catch ValueError from plot_360_n0sc0pe when config is misconfigured and provide a fallback message or skip embedding the image.

Notes and implementation hints:
    - The function intentionally delegates heavy lifting to missing_heatmap (which draws the seaborn heatmap) and plot_360_n0sc0pe (which serializes/saves the matplotlib figure). When reimplementing, ensure those helpers close matplotlib figures to avoid memory leaks.
    - When preparing corr_mat and mask upstream, prefer to ensure they are numpy/pandas objects with compatible shapes to avoid runtime shape errors in seaborn.
    - If you need to make the function more defensive, consider validating shapes and types of corr_mat and mask here and returning a small informative HTML snippet instead of propagating plotting exceptions.

