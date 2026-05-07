# `plot.py`

## `src.ydata_profiling.visualisation.plot.format_fn` · *function*

## Summary:
Convert an epoch timestamp (seconds since 1970-01-01) into a human-readable local datetime string formatted as YYYY-MM-DD HH:MM:SS for use as a matplotlib tick label.

## Description:
format_fn is a small helper intended to be used as a matplotlib tick formatter (for example via matplotlib.ticker.FuncFormatter) when the data axis contains Unix epoch timestamps (seconds). It delegates numeric → datetime conversion to the central utility convert_timestamp_to_datetime and then formats the resulting naive datetime in local time using the fixed format "%Y-%m-%d %H:%M:%S".

Known callers in this repository snapshot:
- None discovered in the provided snapshot. Typical usage is as a FuncFormatter for plotting code that renders integer/float epoch timestamps on an axis.

Why this logic is extracted:
- Centralizes label formatting so all time tick labels use the same datetime conversion and string format.
- Keeps plotting code concise by isolating conversion and formatting concerns.
- Allows consistent handling of edge cases (negative timestamps, large values) via the shared convert_timestamp_to_datetime utility instead of duplicating that logic inline in multiple plot routines.

## Args:
    tick_val (int):
        - Value passed by matplotlib for a tick position (annotated as int in the signature).
        - Expected to be a numeric Unix epoch timestamp representing seconds since 1970-01-01 (can be negative for dates before the epoch).
        - Although annotated as int, the function will accept numeric runtime values (e.g., floats). See Returns and Constraints for float/negative behavior.
    tick_pos (Any):
        - Position index argument passed by matplotlib (unused by this function).
        - Accepted but ignored; callers may pass whatever matplotlib provides.

## Returns:
    str:
        - A string representing the local naive datetime corresponding to tick_val, formatted with the pattern "%Y-%m-%d %H:%M:%S".
        - Possible outcomes and edge behaviors:
            * Positive integer tick_val: converted to datetime.fromtimestamp and formatted (sub-second precision exists in the datetime but is not shown because the format does not include microseconds).
            * Positive float tick_val: convert_timestamp_to_datetime preserves fractional seconds in the resulting datetime; however, this function's format string does not display microseconds so the fractional part is not visible in the returned string.
            * Negative float tick_val: convert_timestamp_to_datetime truncates the float toward zero via int() before applying the negative offset; fractional part is discarded before formatting.
            * If conversion raises an exception (see Raises), the exception propagates and no string is returned.

## Raises:
    Any exception raised by convert_timestamp_to_datetime will propagate. In practice these may include:
    - OverflowError: when the numeric value is too large to represent as a datetime on the host platform.
    - OSError: datetime.fromtimestamp may raise OSError for out-of-range timestamps on some platforms.
    - TypeError or ValueError: if tick_val is non-numeric or otherwise invalid for conversion.
    Exact trigger point: the call to convert_timestamp_to_datetime(tick_val).strftime(...) — exceptions may originate from convert_timestamp_to_datetime or datetime.strftime when given an invalid datetime.

## Constraints:
Preconditions:
    - tick_val must be numeric and within the representable datetime range of the executing Python platform (typically years 1..9999). Supplying non-numeric values (None, NaN, non-coercible strings) will raise TypeError/ValueError.
    - The function assumes local-time semantics because convert_timestamp_to_datetime returns a naive datetime (tzinfo is None).
Postconditions:
    - If no exception is raised, the function returns a string in the fixed "%Y-%m-%d %H:%M:%S" format. No external state is modified.

## Side Effects:
    - None. The function performs pure computation; it does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    A[Start: receive tick_val, tick_pos]
    B{Is tick_val numeric and within representable range?}
    C[Call convert_timestamp_to_datetime(tick_val)]
    D[Call .strftime("%Y-%m-%d %H:%M:%S") on returned datetime]
    E[Return formatted string]
    F[Raise propagated exception (OverflowError,OSError,TypeError,ValueError)]
    A --> B
    B -- yes --> C --> D --> E
    B -- no --> F

## Examples:
Example 1 — typical matplotlib usage as a tick formatter:
    # Create a FuncFormatter using this function and apply to an axis's x-axis major formatter.
    # (Example shows intended call site; it does not define functions or imports.)
    ax.xaxis.set_major_formatter(FuncFormatter(format_fn))

Example 2 — behavior with positive float epoch timestamps:
    # If a tick value is 1609459200.5 (2021-01-01 00:00:00.5 local time),
    # convert_timestamp_to_datetime preserves the .5 seconds internally,
    # but format_fn returns "2021-01-01 00:00:00" because microseconds are not included in "%S".

Example 3 — behavior with negative float epoch timestamps:
    # If a tick value is -1.9, convert_timestamp_to_datetime truncates to -1 second before conversion.
    # format_fn formats the resulting datetime (1970-01-01 00:00:00 + timedelta(seconds=-1)) accordingly.
    # Fractional part (.9) is discarded in this branch.

Example 4 — defensive use with error handling:
    try:
        label = format_fn(value, position)
    except (TypeError, ValueError):
        # handle non-numeric or otherwise invalid tick_val
        handle_invalid_tick()
    except (OverflowError, OSError):
        # handle timestamps out of representable range on this platform
        handle_out_of_range()

## `src.ydata_profiling.visualisation.plot._plot_word_cloud` · *function*

## Summary:
Creates and returns a matplotlib Figure containing one or more word clouds built from pandas Series of token→frequency mappings.

## Description:
This helper produces a single-row matplotlib Figure where each subplot displays a word cloud generated from a pandas Series. Each Series is treated as a mapping from token (Series.index) to numeric frequency (Series.values).

Known callers and usage context:
    - Intended to be invoked by higher-level visualization or report-generation code when a word-cloud representation of token frequencies is required (for example, when visualizing the most frequent tokens for a text or categorical variable in a profiling report).
    - Typical pipeline stage: after computing token frequencies for a variable, the report generator calls this function to convert those frequencies into a visual widget embedded in the report.
    - It is a small, focused utility so other plotting functions can delegate word-cloud details (layout, WordCloud parameters, axis handling) to it.

Why this logic is extracted:
    - Encapsulates the specifics of WordCloud creation and matplotlib subplot wiring so calling code can remain focused on selecting and preparing the frequency Series. Centralizing plotting parameters (image size, background color, random seed) ensures consistent visuals across the codebase and simplifies testing and maintenance.

## Args:
    series (Union[pd.Series, List[pd.Series]]):
        A pandas Series or a list of pandas Series. Each Series must be convertible via Series.to_dict() to a mapping token -> numeric frequency.
        - Expected types: pandas.Series for each element. If a non-Series object with a compatible to_dict() method is passed, behavior depends on that object's to_dict() output.
        - If a single Series is provided, the function wraps it into a list internally.
        - Empty list: allowed; the function will return an empty Figure (no subplots created).
    figsize (tuple, optional):
        Tuple of two numbers (width, height) in inches passed to matplotlib.figure(). Defaults to (6, 4).
        - Must be a length-2 tuple of numeric values.

Interdependencies:
    - Each Series.to_dict() result must produce keys (tokens) and numeric frequency values appropriate for WordCloud.generate_from_frequencies. The function performs no additional validation or normalization of frequencies.

## Returns:
    matplotlib.figure.Figure
        A matplotlib Figure object containing one row of subplots (one Axes per Series). Each Axes contains the corresponding word cloud image and has its axis visibility turned off.
        - If series is a single Series: Figure with 1 subplot.
        - If series is a list of N Series: Figure with N subplots arranged in 1 row.
        - If series is an empty list: an empty Figure is returned (no Axes added).

## Raises:
    - The function does not raise custom exceptions.
    - Exceptions from underlying libraries may propagate:
        * pandas errors if Series.to_dict() fails.
        * wordcloud.errors or ValueError/TypeError from WordCloud.generate_from_frequencies if the frequency mapping is invalid (e.g., non-numeric frequencies, empty mapping that WordCloud cannot handle).
        * matplotlib errors if figure creation or adding subplots fails (for example, invalid figsize).
    - Callers should catch and handle these exceptions if they require robust failure modes.

## Constraints:
Preconditions:
    - matplotlib and wordcloud libraries must be importable and functional in the environment.
    - Each provided Series should contain token-like index values and numeric frequency values; otherwise WordCloud may fail or produce meaningless output.

Postconditions:
    - Returns a matplotlib Figure object. If one or more valid Series were provided, the Figure contains corresponding Axes with word-cloud images and axis display turned off.

## Side Effects:
    - Allocates matplotlib Figure and Axes objects and registers them with matplotlib's state (pyplot). This affects in-memory state of matplotlib (the new Figure appears in pyplot.figs).
    - Uses the WordCloud library to create image data in memory. No file I/O, external network calls, or global variable mutations are performed by this function.

## Implementation details (exact parameters used):
    - The function constructs WordCloud with:
        background_color="white"
        random_state=123
        width=300
        height=200
        scale=2
    - Word clouds are created via WordCloud(...).generate_from_frequencies(word_dict)
    - Subplot placement uses: plot.add_subplot(1, len(series), i + 1)
    - Axis visibility is disabled for each subplot via ax.axis("off")

## Control Flow:
flowchart TD
    Start --> IsList{series is list?}
    IsList -- No --> Wrap[Wrap single Series into list]
    Wrap --> CreateFig[plot = plt.figure(figsize=figsize)]
    IsList -- Yes --> CreateFig
    CreateFig --> ForEach{for each (i, series_data) in enumerate(series)}
    ForEach --> ToDict[word_dict = series_data.to_dict()]
    ToDict --> MakeWC[wordcloud = WordCloud(background_color="white", random_state=123, width=300, height=200, scale=2).generate_from_frequencies(word_dict)]
    MakeWC --> AddAx[ax = plot.add_subplot(1, len(series), i+1)]
    AddAx --> Show[ax.imshow(wordcloud)]
    Show --> Off[ax.axis("off")]
    Off --> LoopEnd{more series?}
    LoopEnd -- Yes --> ForEach
    LoopEnd -- No --> Return[return plot]
    Return --> End

## Examples:

Example 1 — single Series (happy path)
    import pandas as pd
    s = pd.Series({'apple': 10, 'banana': 5, 'orange': 2})
    fig = _plot_word_cloud(s)
    # Display in a notebook:
    # display(fig)
    # Save to file:
    # fig.savefig("wordcloud_single.png")

Example 2 — multiple Series (comparison)
    s1 = pd.Series({'red': 8, 'blue': 4})
    s2 = pd.Series({'cat': 10, 'dog': 7})
    fig = _plot_word_cloud([s1, s2], figsize=(10, 4))
    # fig contains two side-by-side word clouds

Example 3 — error handling
    try:
        bad_series = pd.Series({('tuple',): 'not-a-number'})
        fig = _plot_word_cloud(bad_series)
    except Exception as exc:
        # Handle or log the failure originating from pandas or WordCloud
        print("Failed to create word cloud:", exc)

## `src.ydata_profiling.visualisation.plot._plot_histogram` · *function*

## Summary:
Render a histogram as a matplotlib bar plot and return the Axes used to draw it, supporting either a single set of bin edges or a list of per-label bin-edge arrays (stacked multi-label rendering).

## Description:
This helper creates a new matplotlib Figure and Axes, draws bar(s) for histogram counts using the provided bin edges and series values, and configures axis label formatting, visibility, and colors according to the provided Settings.

Known callers within the repository snapshot:
- No direct callers were discovered in the provided snapshot. Typical usage is from higher-level visualization or profiling code that prepares histogram bin edges and counts and delegates rendering to this function during report generation.

Why this logic is extracted:
- Isolates plotting concerns (figure/axes creation, bar layout, axis formatting and visibility) from upstream data-preparation logic (computing histograms, grouping by label). This makes the plotting step reusable and keeps upstream code focused on computing series and bins.
- Centralizes consistent behaviors: use of config-based colors, x-axis label toggling, date tick formatting, and y-axis visibility.

## Args:
    config (Settings):
        - A configuration object (ydata_profiling.config.Settings) expected to expose:
            * config.html.style._labels (sequence of label names)
            * config.html.style.primary_colors (sequence of color strings)
            * config.plot.histogram.x_axis_labels (bool flag)
        - Missing these attributes will raise AttributeError at runtime.
    series (numpy.ndarray):
        - If bins is a single array (not a list): a 1-D array-like of histogram heights with length equal to len(bins) - 1.
        - If bins is a list (multi-label mode): an indexable sequence such that series[idx] is the height/count array corresponding to bins[idx]. Typically a 2-D ndarray or list-of-arrays with length matching the number of labels (n_labels = len(config.html.style._labels)).
    bins (Union[int, numpy.ndarray, list[numpy.ndarray]]):
        - Expected forms:
            * A single array-like of bin edges (e.g., numpy.ndarray of shape (n_bins+1,)). In this common case the function computes diff = np.diff(bins) and draws one bar series.
            * A list/sequence of bin-edge arrays (one per label). In that case the function loops over labels and draws one bar series per label, using the corresponding color and alpha.
        - Although the signature allows an int, the implementation calls numpy.diff on bins when bins is not a list. Passing an int (number of bins) will cause a TypeError. Therefore pass actual bin-edge arrays when calling this function.
    figsize (tuple, optional):
        - Figure size passed to matplotlib.figure.Figure (width, height) in inches. Default: (6, 4).
    date (bool, optional):
        - If True, the x-axis major formatter is set to FuncFormatter(format_fn) so tick values are converted to human-readable datetime labels (expects epoch timestamp numeric tick values). Default: False.
    hide_yaxis (bool, optional):
        - If True, hides the y-axis (removes the axis and label). Default: False.

Interdependencies and expectations:
- When bins is a list, its length and the length of series (or series' first dimension) should match n_labels = len(config.html.style._labels). The function indexes both bins[idx] and series[idx] over range(n_labels).
- config.html.style.primary_colors must provide at least one color (used for single-bin case) and at least n_labels colors for multi-label cases.

## Returns:
    matplotlib.axes.Axes
    - The function returns the Axes instance used to draw the histogram (the variable named plot in the implementation).
    - Note: the source code's return annotation is plt.Figure, but the actual returned object is the Axes created by fig.add_subplot(111). Callers should therefore treat the return as the Axes (matplotlib.axes.Axes / AxesSubplot).
    - The returned Axes has the bars drawn and formatting applied (tick labels possibly removed, y-axis visibility adjusted, x-axis formatter set if date=True).

## Raises:
    - AttributeError: if the provided config object lacks expected attributes (e.g., html.style._labels or html.style.primary_colors or plot.histogram.x_axis_labels).
    - IndexError: if bins and series lengths/indices do not align with config.html.style._labels length in multi-label mode.
    - TypeError: if bins is an int or otherwise non-iterable in the single-array branch, numpy.diff(bins) will raise; also if series is not indexable or has incompatible shape when passed to plot.bar.
    - Any exception raised by numpy or matplotlib during figure/axes creation and plotting (ValueError, TypeError, etc.) will propagate.

## Constraints:
Preconditions:
    - config must be a Settings object with the attributes used by the function (see Args).
    - bins must be an array-like sequence of bin edges (or a list/sequence of such arrays for multi-label mode). Do not pass an integer number-of-bins here — the implementation expects edges.
    - series must align shape-wise with bins:
        * Single-array bins: len(series) == len(bins) - 1.
        * List-of-bins: len(series) (or series indexability) must match n_labels and each series[idx] length should equal len(bins[idx]) - 1.
Postconditions:
    - A new matplotlib Figure and Axes have been created and mutated (bars drawn, labels/formatting applied).
    - The returned Axes contains the plotted bars and formatting (x-axis formatter set if date True; x tick labels possibly removed; y-axis visible/hidden per hide_yaxis).

## Side Effects:
    - Creates a new matplotlib.figure.Figure and associated Axes (fig = plt.figure(...); plot = fig.add_subplot(111)).
    - Mutates the created Figure/Axes state (adds bars, sets tick formatter, clears tick labels, sets ylabel or hides y-axis).
    - No file, network, or external-system I/O is performed.
    - No global variables are explicitly mutated by this function itself, but matplotlib's global state (current figure) may be affected because a new figure is created; callers should use an appropriate matplotlib context manager if they need to isolate state.

## Control Flow:
flowchart TD
    Start[Start: receive args]
    CheckBins{Is bins a list?}
    Multi[Multi-label rendering]
    Single[Single histogram rendering]
    CreateFig[Create fig and axes via plt.figure & fig.add_subplot]
    LoopLabels[For idx in reversed(range(n_labels)): compute diff, draw bars, optional date formatter, optional clear x-ticklabels, optional hide y-axis]
    AfterMulti[Optionally call fig.xticklabels([]); optionally set fig.supylabel("Frequency")]
    DrawSingle[Compute diff, draw single bar series, optional date formatter, optionally clear x-ticklabels]
    ReturnAx[Return the Axes instance]
    Error[Exceptions propagate (TypeError/IndexError/AttributeError/etc.)]
    Start --> CheckBins
    CheckBins -- yes --> Multi
    CheckBins -- no --> Single
    Multi --> CreateFig --> LoopLabels --> AfterMulti --> ReturnAx
    Single --> CreateFig --> DrawSingle --> ReturnAx
    LoopLabels -->|mismatched shapes or config missing| Error
    DrawSingle -->|bins not array-like| Error

## Examples:
Example (single bin-edge array):
    # Given bin edges and computed counts (series)
    # bins_array: numpy array of shape (n_bins+1,)
    # series: numpy array of shape (n_bins,)
    ax = _plot_histogram(config, series, bins_array, figsize=(6,4), date=False, hide_yaxis=False)
    # ax is the matplotlib Axes where bars were drawn; you can further customize or call plt.show()

Example (multi-label mode with list-of-bins):
    # bins_list: list of numpy arrays, one per label
    # series_per_label: list or 2-D array where series_per_label[idx] corresponds to bins_list[idx]
    ax = _plot_histogram(config, series_per_label, bins_list, figsize=(8,4), date=True, hide_yaxis=True)

Example (defensive/error-handling):
    try:
        ax = _plot_histogram(config, series, bins, date=True)
    except AttributeError:
        # handle missing configuration attributes
        handle_missing_config()
    except (TypeError, IndexError, ValueError):
        # handle malformed bins or mismatched series shape
        handle_bad_histogram_inputs()

## `src.ydata_profiling.visualisation.plot.plot_word_cloud` · *function*

## Summary:
Creates a word-cloud visualization from a pandas Series of token→frequency counts, renders it using matplotlib, and returns an image reference (inline image data or asset file path) produced by the report image exporter.

## Description:
This thin adaptor composes two responsibilities:
1. Delegates creation of a matplotlib Figure containing word cloud imagery to the focused helper _plot_word_cloud, which produces a one-row Figure with one subplot per Series provided.
2. Delegates exporting/serializing the currently-active matplotlib Figure to the report/image backend and returns the resulting image reference or inline data via plot_360_n0sc0pe.

Known callers and usage context:
- Typical callers: higher-level report-generation or visualization orchestration code within the profiling pipeline that needs to embed a word-cloud visualization for a variable (for example: variable-level HTML report builders or visualization utilities).
- Trigger stage: called after token frequencies have been computed for a variable and a visual representation is required.
- Note: repository-wide automated search for concrete call sites failed during documentation generation; the above describes intended usage.

Why this logic is extracted:
- Separates concerns: _plot_word_cloud handles WordCloud creation, subplot wiring and axis display details; plot_360_n0sc0pe handles exporting/encoding and persistence (inline vs asset). This function composes those steps so callers provide only configuration and the frequency Series.

## Args:
    config (Settings):
        The global profiling Settings object controlling output format and HTML behavior.
        - Consulted by plot_360_n0sc0pe for image_format, html.inline, dpi, and assets path/prefix.
        - Must be initialized; specifically config.plot.image_format and config.html.inline are used. When html.inline is False, config.html.assets_path must be set.
    word_counts (pandas.Series):
        A pandas Series mapping token (index) -> numeric frequency (values).
        - Expected: 1-D pandas.Series (or an object acceptable to _plot_word_cloud that exposes to_dict()).
        - Values should be numeric (int/float) or convertible to numeric types accepted by WordCloud.generate_from_frequencies.
        - The Series is forwarded unchanged to _plot_word_cloud(series=word_counts).

Interdependencies:
- The final exported form depends on config.plot.image_format and config.html.inline; plot_360_n0sc0pe selects encoding and whether to write a file or return inline data.

## Returns:
    str
        A string reference to the generated image. Forms include:
        - Inline SVG string when config.html.inline is True and image_format == "svg".
        - Base64-encoded PNG data string when config.html.inline is True and image_format == "png".
        - A relative file path suffix (string) under config.html.assets_path when config.html.inline is False (e.g., "<assets_prefix>/images/<uuid>.png" or ".svg").

## Raises:
    - This function does not raise custom exceptions itself but allows underlying exceptions to propagate (consistent with _plot_word_cloud behavior).
    - ValueError: Raised by plot_360_n0sc0pe when the configured/selected image format is unsupported (plot_360_n0sc0pe raises ValueError('Can only 360 n0sc0pe "png" or "svg" format.')).
    - ValueError: Raised by plot_360_n0sc0pe if config.html.inline is False and config.html.assets_path is None ("config.html.assets_path may not be none").
    - Propagated exceptions from underlying libraries (may originate in _plot_word_cloud or during export):
        * pandas-related exceptions if Series.to_dict() fails.
        * wordcloud.exceptions or ValueError/TypeError from WordCloud.generate_from_frequencies if the frequency mapping is invalid (e.g., non-numeric frequencies or otherwise invalid input).
        * matplotlib-related exceptions during figure creation, saving, or file I/O (e.g., invalid figsize or file write permission errors).

## Constraints:
Preconditions:
    - matplotlib and wordcloud are importable and functional in the environment.
    - config is a valid Settings instance with plot.image_format and html.inline set; when html.inline is False, config.html.assets_path must point to a writable location.
    - word_counts is a pandas.Series mapping token-like index values to numeric frequencies.

Postconditions:
    - A matplotlib Figure containing the word-cloud image(s) will have been created by _plot_word_cloud and then exported/serialized by plot_360_n0sc0pe.
    - plot_360_n0sc0pe closes the matplotlib Figure (plt.close()) before returning, so the caller receives an image reference string and does not need to close any figures opened internally.

## Side Effects:
    - Allocates a matplotlib Figure and Axes via _plot_word_cloud; these are registered with matplotlib state briefly until plot_360_n0sc0pe closes the Figure.
    - May write an image file to disk when config.html.inline is False (plot_360_n0sc0pe writes under config.html.assets_path and returns the file suffix).
    - No network I/O or mutation of global profiling library state occurs beyond matplotlib's temporary state while the Figure is open.

## Control Flow:
flowchart TD
    Start --> CallMakeFig[_plot_word_cloud(series=word_counts)]
    CallMakeFig --> CallExport[plot_360_n0sc0pe(config)]
    CallExport --> ReturnResult[return image_reference (str)]
    ReturnResult --> End

Notes:
- _plot_word_cloud returns a matplotlib.figure.Figure containing the drawn word cloud(s); it does not close the Figure.
- plot_360_n0sc0pe inspects config to choose export behavior (inline png/svg or file), saves/encodes the current Figure, calls plt.close(), and returns the resulting string.

## Examples:

Example 1 — Basic usage
    image_ref = plot_word_cloud(config, pd.Series({'apple': 10, 'banana': 5}))
    # image_ref: inline base64 PNG or SVG string when config.html.inline is True, else a assets file path suffix.

Example 2 — Error handling
    try:
        image_ref = plot_word_cloud(config, bad_series)
    except ValueError as exc:
        # Likely causes: unsupported image format or missing assets_path when not inline
        logger.error("Export error: %s", exc)
    except Exception as exc:
        # Handle WordCloud/pandas/matplotlib errors propagated from helper functions
        logger.exception("Failed to create/export word cloud: %s", exc)

## `src.ydata_profiling.visualisation.plot.histogram` · *function*

## Summary:
Render a histogram into an embeddable image/reference string by drawing the bars using the module's internal plotting helper, applying final tick/layout adjustments, and serializing the Matplotlib figure for embedding or asset storage.

## Description:
Call chain and responsibility:
- This function calls the internal helper _plot_histogram(...) (defined in the same module) to create the Matplotlib Figure and Axes and to draw the histogram bars and local axis formatting.
    - Note: the standalone documentation for _plot_histogram in the snapshot stated "No direct callers were discovered"; this histogram function is an explicit caller present in the same file.
- After receiving the Axes from _plot_histogram, histogram sets x-axis tick rotation (90° if date=True else 45°) and calls tight_layout() on the figure.
- It then calls plot_360_n0sc0pe(config, ...) to serialize the current Matplotlib figure to a string (inline SVG or base64-encoded PNG) or to save the image file on disk and return the asset suffix.
- Responsibility boundaries:
    - _plot_histogram: create Figure/Axes, draw bars, apply per-bar/axis formatting and visibility rules.
    - histogram (this function): orchestrate the final tick rotation and tight layout, then obtain the serialized image.
    - plot_360_n0sc0pe: handle serialization to inline bytes or writing the figure to disk and closing the figure.

Why separated:
- Keeps data-preparation, drawing, layout adjustments, and serialization in modular steps so each concern can be maintained and tested independently. This function enforces consistent final presentation (rotation, layout) and the high-level contract of producing an embeddable image string from prepared histogram data.

## Args:
    config (Settings):
        - A ydata_profiling.config.Settings instance. The helpers expect fields such as:
            * config.html.inline (bool)
            * config.plot.image_format (string; allowed: "png", "svg")
            * config.html.assets_path (required when inline is False)
            * config.plot.dpi (used when saving PNG)
            * config.html.style.* (colors/labels used by _plot_histogram)
        - Missing attributes will raise AttributeError when accessed by the helpers.
    series (numpy.ndarray):
        - Histogram counts/heights.
        - If bins is a single bin-edge array: 1-D array of length len(bins) - 1.
        - If bins is a sequence/list of bin-edge arrays (multi-label): indexable such that series[idx] corresponds to counts for bins[idx].
        - Incompatible shapes or non-indexable series will cause TypeError/IndexError/ValueError during plotting.
    bins (Union[numpy.ndarray, Sequence[numpy.ndarray]]):
        - Expected to be a bin-edge array (shape (n_bins + 1,)) or a sequence/list of such arrays for multi-label rendering.
        - Passing an integer (number-of-bins) is not supported by the underlying implementation and will usually raise a TypeError when numpy.diff is applied.
    date (bool, optional):
        - If True, tick rotation is set to 90° and the underlying plotting logic may use date-specific formatters. Default: False.

Interdependencies:
- Shapes/lengths must align:
    - Single-array bins: len(series) == len(bins) - 1
    - List-of-bins: number of series entries must match number of labels/colors expected by _plot_histogram (typically from config.html.style._labels); each series[idx] length must equal len(bins[idx]) - 1.

## Returns:
    str
    - The string returned by plot_360_n0sc0pe:
        * Inline SVG string if config.html.inline is True and format == "svg"
        * Base64-encoded PNG data string if config.html.inline is True and format == "png"
        * Filesystem suffix/path string pointing to the saved image asset if config.html.inline is False
    - The returned value is ready for embedding in HTML or referencing as an asset.
    - The Matplotlib figure created during drawing is closed by plot_360_n0sc0pe before the string is returned.

## Raises:
    - AttributeError: if config lacks required fields accessed by _plot_histogram or plot_360_n0sc0pe.
    - ValueError: raised by plot_360_n0sc0pe for unsupported image formats (only "png" and "svg" allowed) or when config.html.assets_path is None while inline is False.
    - TypeError / IndexError / ValueError: propagated when bins or series are malformed or misaligned, or when numpy/matplotlib operations fail (e.g., passing an int for bins triggers numpy.diff TypeError).
    - Other exceptions from Matplotlib or file I/O performed by plot_360_n0sc0pe will propagate to the caller.

## Constraints:
Preconditions:
    - config is a valid Settings object with plotting and HTML attributes used by the helpers.
    - bins must be array-like bin-edge arrays (or a list thereof); do not pass an integer number-of-bins.
    - series must align with bins shapes as described above.
Postconditions:
    - The histogram has been drawn, the corresponding Matplotlib figure has been serialized (in-memory or on-disk), and the figure has been closed.
    - No active Matplotlib figure for this plot remains after return.

## Side Effects:
    - _plot_histogram creates and mutates a Matplotlib Figure and Axes (adds bars, sets formatters/labels, may hide y-axis).
    - plot_360_n0sc0pe saves the figure either to an in-memory buffer (BytesIO/StringIO) or to disk under config.html.assets_path, and calls plt.close() to close the figure.
    - No network or database I/O is performed by this function itself; file writes may occur when config.html.inline is False (performed by plot_360_n0sc0pe).
    - Matplotlib global state (current figure) is momentarily affected until plt.close() runs.

## Control Flow:
flowchart TD
    Start[Start: histogram(config, series, bins, date)]
    CallPlot[_plot_histogram(config, series, bins, date, figsize=(7,3)) -> Axes 'plot']
    SetRotation{date True?}
    Rotate90[plot.xaxis.set_tick_params(rotation=90)]
    Rotate45[plot.xaxis.set_tick_params(rotation=45)]
    Tight[plot.figure.tight_layout()]
    Serialize[plot_360_n0sc0pe(config) -> image_str]
    Return[Return image_str]
    Error[Propagate exceptions from helpers/Matplotlib/I/O]
    Start --> CallPlot
    CallPlot --> SetRotation
    SetRotation -- yes --> Rotate90
    SetRotation -- no --> Rotate45
    Rotate90 --> Tight
    Rotate45 --> Tight
    Tight --> Serialize
    Serialize --> Return
    CallPlot -->|error| Error
    Serialize -->|error| Error

## Examples:
Example (single bin-edge array, inline PNG):
    # Preconditions:
    # - config.html.inline == True
    # - config.plot.image_format == "png"
    # - bins_array: numpy array of shape (n_bins + 1,)
    # - counts: numpy array of shape (n_bins,)
    image_str = histogram(config, counts, bins_array, date=False)
    # image_str is a base64-encoded PNG string suitable for embedding in HTML

Example (multi-label bins, date ticks, on-disk asset):
    # Preconditions:
    # - config.html.inline == False
    # - config.plot.image_format == "svg"
    # - bins_list: list of numpy arrays (one per label)
    # - counts_per_label: list or 2-D array matching bins_list shapes
    suffix = histogram(config, counts_per_label, bins_list, date=True)
    # suffix is the asset suffix under config.html.assets_path for the saved SVG file

Example (defensive usage):
    try:
        out = histogram(config, series, bins, date=False)
    except AttributeError as exc:
        handle_config_error(exc)
    except ValueError as exc:
        handle_value_error(exc)
    except (TypeError, IndexError) as exc:
        handle_input_error(exc)

## `src.ydata_profiling.visualisation.plot.mini_histogram` · *function*

## Summary:
Render a small (thumbnail) histogram from precomputed series and bin edges, adjust x-tick styling for compact display, and return an encoded image reference (inline string or asset path) suitable for embedding in HTML reports.

## Description:
Known callers:
- No direct callers were discovered in the provided repository snapshot. Typical callers are higher-level profiling/report-generation code that needs a compact histogram thumbnail (for example, a column-summary table cell or a small preview chart) and therefore prepares histogram bin edges and counts and delegates rendering to this function.

Context / when to use:
- Use this to produce a compact, consistently-sized histogram image for inclusion in HTML reports or other UI elements. It is intended for visualization layers that already computed histogram counts and bin edges and only require rendering and encoding.

Why this logic is extracted:
- Encapsulates the presentation-specific steps for producing a small (3 x 2.25 in) histogram image: invoking a plotting helper, enforcing a compact layout, standardizing x-tick font size and rotation based on whether ticks represent dates, and returning a serialized image string or asset path via the project's centralized image-export utility. This keeps upstream code focused on data preparation and centralizes image encoding/output behavior.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Required attributes (accessed transitively by this function and helpers):
            * config.html.inline (bool)
            * config.plot.image_format.value (str) or config.plot.image_format
            * config.plot.dpi (int) (if saving png)
            * config.html.assets_path (Path or str) and config.html.assets_prefix (str) when html.inline is False
        - Purpose: controls plot style, export format, and whether the image is embedded inline or saved as an asset.
    series (numpy.ndarray):
        - Type: numpy.ndarray (or any array-like indexable sequence)
        - Semantic: histogram heights/counts corresponding to the provided bins.
        - Allowed forms:
            * 1-D array of length equal to len(bins) - 1 when bins is a single bin-edge array.
            * 1-D/2-D indexable structure (e.g., list-of-arrays or 2-D ndarray) for per-label/multi-label histograms where each element corresponds to a bins entry (this function simply forwards to the plotting helper).
        - Note: This function does not compute histograms from raw values; pass precomputed counts/heights.
    bins (Union[int, numpy.ndarray]):
        - Type (declared): Union[int, numpy.ndarray]
        - Practical requirement: must be an array-like of bin edges (numpy.ndarray or sequence) or a list/sequence of such arrays for multi-label rendering.
        - Important: Although the annotation includes int, the underlying plotting helper expects bin-edge arrays and will call numpy.diff on bins; passing an int (number of bins) will raise a TypeError. Do not pass an integer here.
    date (bool, optional):
        - Type: bool
        - Default: False
        - If True: x-axis styling is adjusted for date labels (smaller font and 90° rotation). If False: uses slightly larger font and 45° rotation.
        - Interdependency: date only affects tick font size and rotation; it does not perform any conversion of numeric tick values here (the histogram helper optionally sets a date formatter if requested).

## Returns:
    str
    - A string representing the rendered image. The exact form depends on config and the configured image format (see plot_360_n0sc0pe behavior):
        * If config.html.inline is True:
            - If image_format == "svg": returns the raw SVG markup string (text).
            - If image_format == "png": returns a data URI / base64-encoded PNG string (prefixed with data:image/png;base64,...).
        * If config.html.inline is False:
            - Returns a relative asset path string (suffix) where the image file was saved (e.g., "assets_prefix/images/<uuid>.png" or ".svg").
    - The returned string is suitable for embedding in HTML (inline) or referencing an asset path in generated report markup.

## Raises:
    - Any exception raised by the plotting helper:
        * AttributeError: if config lacks expected attributes referenced by _plot_histogram or plot_360_n0sc0pe (e.g., missing html or plot fields).
        * TypeError / ValueError / IndexError: if bins and series shapes or types are incompatible, or if bins is an invalid type (e.g., an int).
    - ValueError from plot_360_n0sc0pe:
        * If the image format configured is not "png" or "svg", plot_360_n0sc0pe raises ValueError('Can only 360 n0sc0pe "png" or "svg" format.').
        * If config.html.inline is False and config.html.assets_path is None, plot_360_n0sc0pe raises ValueError("config.html.assets_path may not be none").
    - Any matplotlib or numpy exceptions raised during figure creation, drawing, saving, or closing will propagate.

## Constraints:
Preconditions (must be true before calling):
    - config must be a valid Settings object with the html and plot configuration fields used by the helper functions.
    - bins must be provided as bin-edge arrays (not an integer number of bins). For multi-label usage, bins should be a list/sequence of bin-edge arrays whose length aligns with the series structure and (for multi-label mode) with config.html.style._labels length.
    - series must align shape-wise with bins:
        * Single-array bins: len(series) == len(bins) - 1.
        * List-of-bins: series must be indexable and have compatible lengths for each bins[idx].
Postconditions (guaranteed after return, unless an exception is raised):
    - A plot was created (via _plot_histogram) and configured (facecolor set to white, x-tick font size and rotation set, and tight_layout applied).
    - The matplotlib state used to save the image has been consumed by plot_360_n0sc0pe, which calls plt.savefig(...) and plt.close(), so the generated figure will be closed before control returns.
    - A string referencing the image (inline content or saved asset path) is returned.

## Side Effects:
    - Creates and draws on a new matplotlib Figure and Axes (via _plot_histogram).
    - Mutates the created Figure/Axes: sets facecolor, changes x-axis tick label font sizes, tick rotation, and calls tight_layout() on the figure.
    - Calls plot_360_n0sc0pe which saves the current figure (either to an in-memory buffer or to disk) and closes the matplotlib figure(s) via plt.close(). This affects matplotlib's global state (current figure cleared).
    - No network I/O is done by this function directly. If config.html.inline is False, a file is written to the configured html.assets_path by plot_360_n0sc0pe.
    - No global application state (other than matplotlib's runtime state) or external databases are modified by this function.

## Control Flow:
flowchart TD
    Start[Start: mini_histogram called with (config, series, bins, date)]
    CallPlot[_plot_histogram(config, series, bins, figsize=(3,2.25), date=date, hide_yaxis=True)]
    SetFace[Set axes facecolor to "w"]
    AdjustTicks[For each major x-axis tick: set label fontsize (6 if date else 8); set rotation (90 if date else 45)]
    TightLayout[Call plot.figure.tight_layout()]
    Export[Call plot_360_n0sc0pe(config) -> image_str]
    ReturnStr[Return image_str]
    Error[Exceptions propagate from helpers or matplotlib/numpy]
    Start --> CallPlot
    CallPlot --> SetFace
    SetFace --> AdjustTicks
    AdjustTicks --> TightLayout
    TightLayout --> Export
    Export --> ReturnStr
    CallPlot -->|error| Error
    TightLayout -->|error| Error
    Export -->|error (e.g., unsupported format or missing assets_path)| Error

## Examples:
Example (basic usage; inline SVG):
    # Precondition: config.plot.image_format.value == "svg" and config.html.inline == True
    # series: numpy array of counts matching bins
    # bins: numpy array of bin edges (length = n_bins + 1)
    try:
        img_svg = mini_histogram(config, series, bins, date=False)
        # img_svg contains raw SVG markup and can be embedded directly in HTML.
    except ValueError as exc:
        # Handle unsupported image format or missing assets_path if config is non-inline
        handle_export_error(exc)
    except (TypeError, IndexError, AttributeError) as exc:
        # Handle malformed bins/series or missing configuration fields
        handle_input_or_config_error(exc)

Example (png inline base64 data URI):
    # Precondition: config.plot.image_format.value == "png" and config.html.inline == True
    img_data_uri = mini_histogram(config, series, bins, date=True)
    # img_data_uri is a "data:image/png;base64,..." string suitable for <img src="...">

Example (asset file saved to disk):
    # Precondition: config.html.inline == False and config.html.assets_path is set
    img_asset_path = mini_histogram(config, series, bins)
    # img_asset_path is a string suffix referencing the saved file (e.g., "prefix/images/<uuid>.png")

## `src.ydata_profiling.visualisation.plot.get_cmap_half` · *function*

## Summary:
Produces a new LinearSegmentedColormap built from the upper half of the input colormap's sampled color range (samples from 0.5 to 1.0).

## Description:
This utility samples the latter 50% interval of an existing matplotlib colormap (the numerical positions between 0.5 and 1.0) and constructs a new LinearSegmentedColormap from those sampled colors. It is intended for reuse by plotting utilities that need a colormap restricted to the second half of the original colormap's gradient.

Known callers within typical plotting workflows:
- Higher-level plotting functions in this visualization module that need a derived colormap covering only part of the original scale (e.g., for fills, heatmaps, or legends). There are no explicit direct callers shown in the provided function snippet; callers are generally other plotting helpers that centralize colormap manipulations.

Why this is a separate function:
- Centralizes the sampling and construction logic for "half" colormaps so multiple plotting functions share a consistent sampling strategy (positions, sample count, and returned colormap type/name) and to avoid duplicating array-construction and from_list calls.

## Args:
    cmap (Union[Colormap, LinearSegmentedColormap, ListedColormap]):
        A matplotlib colormap-like object.
        Required properties:
        - Exposes an integer-like attribute `N` (the number of discrete sample points).
        - Is callable with a numeric 1-D array of sample positions (e.g., cmap(samples)) and returns an array of RGBA values.
        Notes:
        - Typical values: objects from matplotlib.pyplot.get_cmap(...) or instances of ListedColormap/LinearSegmentedColormap.
        - The function uses integer floor division (cmap.N // 2) to determine the number of samples; this matters when cmap.N is odd.

## Returns:
    LinearSegmentedColormap:
        A new matplotlib.colors.LinearSegmentedColormap named "cmap_half".
        Details:
        - Number of samples taken: num = cmap.N // 2 (integer floor division).
        - Sample positions: numpy.linspace(0.5, 1.0, num) — includes both endpoints when num >= 1.
        - colors array shape: (num, 4) when cmap returns RGBA floats; values are typically in [0.0, 1.0].
        - The returned colormap maps a normalized [0, 1] input to the sampled colors in the same relative order as they appeared in the input colormap's [0.5, 1.0] interval.
        Edge cases:
        - If num == 0 (e.g., cmap.N in {0,1}), the sampled colors array will be empty; constructing a colormap from an empty list will propagate an error from matplotlib (see Raises).

## Raises:
    - The function itself does not explicitly raise custom exceptions, but can propagate exceptions from its calls:
        * AttributeError / TypeError if `cmap` does not have attribute `N` or is not callable as expected.
        * ValueError (or other exceptions raised by matplotlib) if the list of colors passed to LinearSegmentedColormap.from_list is empty or invalid.
    Exact trigger examples:
        - If getattr(cmap, "N", None) is missing or non-integer-like, cmap.N // 2 will raise a TypeError/AttributeError.
        - If cmap.N // 2 evaluates to 0, numpy.linspace produces an empty array; passing the resulting empty color list to LinearSegmentedColormap.from_list will typically cause matplotlib to raise a ValueError.

## Constraints:
    Preconditions:
        - `cmap` must be a matplotlib-compatible colormap object with:
            * integer-like `N` attribute (N >= 0)
            * callable behavior returning RGBA arrays for numeric sample inputs
        - For meaningful (non-empty) output, require cmap.N >= 2.
    Postconditions:
        - A LinearSegmentedColormap instance named "cmap_half" is returned when no exception is raised.
        - The returned colormap represents the original colormap's sampled colors from its [0.5, 1.0] interval, mapped into a full [0, 1] domain of the new colormap.

## Side Effects:
    - None. No I/O, no global state mutation; only constructs and returns a new colormap object.

## Control Flow:
flowchart TD
    Start([Start]) --> HasN{Does cmap expose integer-like N and is callable?}
    HasN -- No --> PropagateAttrError[AttributeError/TypeError propagated]
    HasN -- Yes --> NumSamples[Compute num = cmap.N // 2]
    NumSamples --> NumZero{Is num == 0?}
    NumZero -- Yes --> SamplesEmpty[Create empty samples array via np.linspace]
    SamplesEmpty --> ColorsEmpty[colors = cmap(empty_samples) => empty array]
    ColorsEmpty --> FromListEmpty[Call LinearSegmentedColormap.from_list with empty colors -> matplotlib raises]
    NumZero -- No --> Samples[Create samples = np.linspace(0.5, 1.0, num)]
    Samples --> Colors[colors = cmap(samples)]
    Colors --> FromList[Return LinearSegmentedColormap.from_list('cmap_half', colors)]

## Examples:
    Example 1 — typical usage
    from matplotlib import pyplot as plt
    base = plt.get_cmap("viridis")
    half = get_cmap_half(base)
    plt.imshow(data, cmap=half)

    Example 2 — defensive handling for small/invalid colormaps
    import matplotlib.pyplot as plt
    cmap = plt.get_cmap("tab10")  # ListedColormap with few discrete colors
    n = getattr(cmap, "N", 0)
    if n // 2 == 0:
        # Fallback: use original colormap or choose a different strategy
        use_cmap = cmap
    else:
        use_cmap = get_cmap_half(cmap)

    Example 3 — catching propagated errors
    try:
        half = get_cmap_half(some_cmap)
    except (AttributeError, TypeError, ValueError) as exc:
        # Handle missing attributes or invalid/empty color lists
        logger.warning("Could not construct half-colormap: %s", exc)
        half = some_cmap  # safe fallback

## `src.ydata_profiling.visualisation.plot.get_correlation_font_size` · *function*

## Summary:
Returns a recommended matplotlib font size for correlation-plot labels based on the number of labels; returns None when no adjustment is recommended.

## Description:
This helper maps the quantity of labels (typically axis or tick labels in a correlation heatmap / matrix) to a small integer font size when many labels are present, enabling plots to remain legible at high label counts.

Known callers within the analyzed scope:
- No direct callers were identified within the local scan of this file. Typical usage (not a concrete caller) is from plotting utilities that determine tick/annotation font sizes for correlation matrices or pairwise plots when rendering many features.

Why this logic is extracted:
- Centralizes threshold logic for font-size selection so multiple plotting functions can consistently decide when to override default font sizes. It isolates the mapping policy (label-count → font-size) from rendering code to make tuning thresholds straightforward and testable.

## Args:
    n_labels (int):
        Number of labels (ticks or variables) that will be displayed on the plot.
        - Expected to be a non-negative integer.
        - If a non-integer numeric type (e.g., float) is passed, Python's comparison semantics apply; values will be compared to the integer thresholds. Passing a value of an incompatible type (e.g., str, object) will typically raise a TypeError during comparison.
        - There are no additional configurable parameters; behavior is purely based on the numeric thresholds below.

## Returns:
    Optional[int]:
        Recommended font size as a small integer when the number of labels exceeds configured thresholds; otherwise None which indicates "do not override" (i.e., use the default font size).
        Possible return values:
        - 4 when n_labels > 100
        - 5 when 80 < n_labels <= 100
        - 6 when 50 < n_labels <= 80
        - 8 when 40 < n_labels <= 50
        - None when n_labels <= 40 (no recommendation / keep default)

## Raises:
    This function does not explicitly raise exceptions. However:
    - A TypeError may be raised by the comparison operators if n_labels is of a type that cannot be compared to integers (for example, comparing a string to an integer).
    - No ValueError or custom exceptions are raised by the function itself.

## Constraints:
Preconditions:
    - Caller should pass an integer (or a numeric type comparable to integers).
    - The intent is to call this function before setting font properties for a plot; the caller must interpret None as "leave font size unchanged".

Postconditions:
    - If an integer is returned, it is one of {4, 5, 6, 8} depending on n_labels.
    - If None is returned, no font-size override is recommended.

## Side Effects:
    - None. The function is pure: it has no I/O, does not mutate external state, and does not call external services.

## Control Flow:
flowchart TD
    A[Start] --> B{n_labels > 100?}
    B -- Yes --> C[Return 4]
    B -- No --> D{n_labels > 80?}
    D -- Yes --> E[Return 5]
    D -- No --> F{n_labels > 50?}
    F -- Yes --> G[Return 6]
    F -- No --> H{n_labels > 40?}
    H -- Yes --> I[Return 8]
    H -- No --> J[Return None]

## Examples:
- Typical usage in a plotting helper (illustrative results shown, not full plotting code):
    - get_correlation_font_size(120) -> 4
    - get_correlation_font_size(95)  -> 5
    - get_correlation_font_size(60)  -> 6
    - get_correlation_font_size(45)  -> 8
    - get_correlation_font_size(40)  -> None  (no override; use default font size)

- Notes on error handling:
    - Prefer passing an int. If input comes from external source (e.g., len(list_of_columns)), you can guard:
        - If n_labels is not an int or is negative, normalize or validate before calling to avoid unexpected comparison errors.

## `src.ydata_profiling.visualisation.plot.correlation_matrix` · *function*

*No documentation generated.*

## `src.ydata_profiling.visualisation.plot.scatter_complex` · *function*

## Summary:
Render a 2D plot of a complex-valued pandas Series (real parts on the x axis, imaginary parts on the y axis) and export the resulting image via the shared export helper; returns an encoded image string or an asset file path depending on configuration.

## Description:
This function draws the real vs. imaginary scatter of the provided pandas Series and delegates saving/encoding/closing of the figure to plot_360_n0sc0pe(config). It encapsulates visualization details (axis labels, color selection, and the decision between hexbin aggregation and point scatter) so higher-level report code can request a complex-number plot without handling plotting/export mechanics.

Known callers:
- No direct callers were discovered in the scanned repository metadata for this exact function name. It is intended for use inside the profiling/visualisation pipeline when rendering columns/Series containing complex numbers.

Reason for extraction:
- Keeps plotting concerns for complex-valued series in one place and reuses a common export/save policy (plot_360_n0sc0pe) across different plot types.

## Args:
    config (Settings)
        - The configuration object used by the profiling/visualisation system.
        - Required/used attributes (must be present on the object passed in):
            * config.html.style.primary_colors: sequence[str] — the first element (index 0) is used as the base color for the scatter path or to create a colormap for hexbin.
            * config.plot.scatter_threshold: int — threshold to decide between hexbin (aggregated) and scatter plotting.
            * config.plot.image_format: an enum-like object with a .value attribute that is either "png" or "svg"; used by plot_360_n0sc0pe.
            * config.html.inline: bool — when True, the image is returned inline (base64 or raw SVG); when False, the image is written to disk and a relative path suffix is returned.
            * config.html.assets_path (required when config.html.inline is False): path-like — base folder where assets will be written.
            * config.html.assets_prefix (when saving to disk): string prefix used when building the saved file path suffix.
            * config.plot.dpi (when image_format is "png" and saving inline/non-inline): integer DPI for PNG output.
        - Failures due to missing attributes will raise attribute access errors from Python when referenced.

    series (pandas.Series)
        - A pandas Series (or Series-like object) containing complex numbers or values exposing `.real` and `.imag` properties/attributes (numpy/pandas numeric dtypes are acceptable).
        - The function plots series.real (x) against series.imag (y).
        - For pure-real numeric values, `.imag` is typically 0 and the plot will be on the x-axis.
        - Type: pandas.Series

Parameter interdependencies:
- The plotting primitive chosen depends on len(series) > config.plot.scatter_threshold. If len(series) is greater than the threshold, a hexbin with a seaborn-derived colormap is drawn; otherwise a simple scatter of points is drawn (note: equality goes to the scatter branch — i.e., len == threshold -> scatter).

## Returns:
    str
    - The function returns whatever plot_360_n0sc0pe(config) returns. Concretely:
        * If config.html.inline is True and image_format == "png": a base64-encoded PNG data string suitable for embedding (constructed by base64_image with MIME "image/png").
        * If config.html.inline is True and image_format == "svg": the raw SVG XML string saved to the buffer.
        * If config.html.inline is False: a relative file path suffix string where the image file was written (constructed as "<assets_prefix>/images/<uuid>.<ext>").
    - The function itself does not alter the content of the returned string — it simply returns the export helper's result.

## Raises:
    ValueError (raised by plot_360_n0sc0pe):
        - If config.plot.image_format.value is not one of "png" or "svg":
            ValueError('Can only 360 n0sc0pe "png" or "svg" format.')
        - If config.html.inline is False and config.html.assets_path is None:
            ValueError("config.html.assets_path may not be none")
    IndexError:
        - If config.html.style.primary_colors is empty, accessing index 0 will raise IndexError.
    AttributeError / TypeError:
        - If `series` does not expose `.real` or `.imag`, or if config is missing required attributes, attribute access will raise AttributeError.
        - Any type mismatch when matplotlib functions are called may raise TypeError (propagated from underlying libraries).
    (Note: These last exceptions are not explicitly raised in the function but will propagate from attribute access or library calls.)

## Constraints:
Preconditions:
    - A matplotlib pyplot object named plt (matplotlib.pyplot) must be available in the module context (the function uses plt.ylabel, plt.xlabel, plt.hexbin, plt.scatter).
    - seaborn.light_palette (the code refers to seaborn via the alias `sns.light_palette`) must be available as either seaborn.light_palette or the module-level name `sns` must reference seaborn. If `sns` is undefined, a NameError will occur.
    - config must contain the attributes enumerated in Args.

Postconditions:
    - A matplotlib figure with labeled axes ("Real" on x axis and "Imaginary" on y axis) has been drawn and saved/encoded by plot_360_n0sc0pe.
    - plot_360_n0sc0pe calls plt.close(), so no open figure remains on return.

## Side Effects:
    - Mutates the global matplotlib pyplot state by setting labels and drawing either a hexbin or scatter on the current Axes.
    - Delegates to plot_360_n0sc0pe which will either:
        * Return an inline image representation (base64 PNG string or raw SVG string), or
        * Write an image file to disk under config.html.assets_path and return the relative suffix string.
    - No network access, database writes, or other external side effects are performed by this function itself.

## Control Flow:
flowchart TD
    A[Start] --> B[Set ylabel "Imaginary" and xlabel "Real"]
    B --> C[Read color = config.html.style.primary_colors[0]]
    C --> D{len(series) > config.plot.scatter_threshold?}
    D -- Yes --> E[Create colormap via seaborn.light_palette(color, as_cmap=True)]
    E --> F[Call plt.hexbin(series.real, series.imag, cmap=cmap)]
    D -- No --> G[Call plt.scatter(series.real, series.imag, color=color)]
    F --> H[Call plot_360_n0sc0pe(config)]
    G --> H
    H --> I[plot_360_n0sc0pe saves/encodes image and calls plt.close()]
    I --> J[Return export string or file suffix]
    J --> K[End]

## Examples:
Note: The real codebase uses a typed Settings class; the examples below show a minimal runtime-config object that provides the attributes required by scatter_complex so the example is runnable without the full project Settings.

Example 1 — inline PNG (small series -> scatter):
    from types import SimpleNamespace
    import pandas as pd
    from types import SimpleNamespace

    # Minimal config-like object for demonstration
    config = SimpleNamespace()
    config.html = SimpleNamespace()
    config.html.style = SimpleNamespace()
    config.html.style.primary_colors = ["#1f77b4"]  # must have at least one color
    config.html.inline = True
    config.html.assets_path = None
    config.html.assets_prefix = "assets"

    config.plot = SimpleNamespace()
    config.plot.scatter_threshold = 100
    config.plot.image_format = SimpleNamespace(value="png")  # mimic enum-like .value
    config.plot.dpi = 96

    series = pd.Series([complex(x, x * 0.5) for x in range(50)])  # 50 points -> scatter

    try:
        image_str = scatter_complex(config, series)
        # image_str: base64-encoded PNG data string (suitable for embedding in HTML)
    except Exception as exc:
        # Handle configuration or plotting errors (ValueError, IndexError, AttributeError, etc.)
        raise

Example 2 — non-inline SVG saved to assets (large series -> hexbin):
    # Reuse config from above, but save to disk
    config.html.inline = False
    config.html.assets_path = "/tmp"  # must be set when inline=False
    config.plot.image_format = SimpleNamespace(value="svg")
    series = pd.Series([complex(x, x) for x in range(200)])  # 200 points -> hexbin

    try:
        result = scatter_complex(config, series)
        # result: a suffix path like "assets/images/<uuid>.svg"
    except ValueError as e:
        # Possible reasons: unsupported image format or missing assets_path
        raise

Edge cases and implementation notes:
    - If len(series) == config.plot.scatter_threshold the function chooses the scatter branch (the condition is strictly greater: >).
    - If series is empty, matplotlib will produce an empty plot; no exception is raised by the function itself.
    - If config.html.style.primary_colors is empty, accessing index 0 raises IndexError.
    - The code expects seaborn to be available via the module name `sns` or that seaborn.light_palette is reachable; ensure the module imports align (e.g., import seaborn as sns).
    - Invalid image formats or missing assets_path (when inline is False) are validated and will raise ValueError from plot_360_n0sc0pe.

## `src.ydata_profiling.visualisation.plot.scatter_series` · *function*

## Summary:
Creates a 2D scatter-style visualisation from a pandas Series of paired values, using a hex-binned density plot when the series is large and a point scatter plot when it is small; returns the string produced by the report-rendering helper.

## Description:
Known callers within the provided snapshot:
    - No direct callers were retrieved from the provided code snapshot. 

Typical usage context:
    - This function is intended to be used in the visualization/report-generation stage of a profiling pipeline to render a bivariate numeric relationship (x, y) into the current matplotlib axes, and to obtain the final serialized/embedded representation produced by the downstream helper (returned as a string).

Reason for extraction:
    - Encapsulates the decision logic that chooses between a density-based hexbin (for many points) and a simple scatter plot (for few points), applies axis labels and a consistent colour from the profiling configuration, and delegates final output serialization to plot_360_n0sc0pe. Extracting this behaviour keeps plotting decisions consistent and reusable across the report generation code.

## Args:
    config (Settings):
        - The profiling Settings object used to obtain visual style and plotting thresholds.
        - Must provide at least:
            * config.html.style.primary_colors: an indexable sequence (e.g., list) whose first element is a color understood by seaborn/matplotlib.
            * config.plot.scatter_threshold: an integer threshold used to switch plotting mode.
        - If these attributes are missing or primary_colors is empty, attribute or index errors may occur.
    series (pandas.Series):
        - A pandas Series whose elements are 2-element iterables (e.g., tuples or lists) representing (x, y) coordinates for each point.
        - Allowed values: each element must be unpackable into exactly two numeric-like values. The series length may be zero or more.
        - The function converts the series to a list and performs zip(*series.tolist()) to produce two sequences (x-values and y-values).
        - Interdependency: the element structure (two items per element) is required for correct unpacking; mismatched element shapes will raise an error.
    x_label (str, optional):
        - Label text to set on the x-axis. Defaults to "Width".
    y_label (str, optional):
        - Label text to set on the y-axis. Defaults to "Height".

## Returns:
    str:
        - The return value is the string returned by plot_360_n0sc0pe(config).
        - The content and semantics of this string are determined entirely by plot_360_n0sc0pe; this function simply returns it unchanged.
        - Typical consumer usage: embed or include the returned string in HTML/markup produced by the reporting pipeline. (Do not assume format — treat as opaque here.)

## Raises:
    - AttributeError:
        - If config or nested attributes (e.g., config.html, config.html.style) are missing, attribute access may raise AttributeError.
    - IndexError:
        - If config.html.style.primary_colors exists but is empty, accessing index 0 will raise IndexError.
    - TypeError:
        - If an element of series is not an iterable of length >= 2, unpacking via zip(*series.tolist()) and then calling plt.scatter(*data) or plt.hexbin(*data) can raise TypeError (e.g., missing required positional arguments).
        - If series is empty, zip(*series.tolist()) yields no iterables; calling plt.scatter(*data) or plt.hexbin(*data) with no arguments can raise TypeError for missing positional parameters.
    - Any matplotlib/seaborn errors:
        - Underlying plotting calls (seaborn.light_palette, pyplot.scatter, pyplot.hexbin) may raise their own errors if provided invalid color values or invalid array types. These are not explicitly caught.

## Constraints:
Preconditions:
    - config must be a Settings-like object with the attributes noted above.
    - series must be a pandas.Series instance whose elements are 2-item iterables (x,y).
    - A matplotlib figure/axes context should be available (this function writes to the current axes via pyplot).

Postconditions:
    - The current matplotlib axes will have x and y axis labels set to x_label and y_label.
    - A scatter or hexbin layer will have been drawn on the current axes using the primary colour from the config.
    - The function will return whatever string plot_360_n0sc0pe(config) returns.

## Side Effects:
    - Mutates global matplotlib state:
        * Calls pyplot.xlabel(x_label) and pyplot.ylabel(y_label).
        * Calls pyplot.hexbin(...) or pyplot.scatter(...), which draw on the active axes.
    - Reads settings from config (no mutation of config).
    - Calls seaborn.light_palette(...) to create a colormap when hexbin is used.
    - No file, network, database, or stdout I/O is performed directly by this function.
    - Delegates to plot_360_n0sc0pe(config) which may have its own side effects (not described here).

## Control Flow:
flowchart TD
    A[Start] --> B{series length > config.plot.scatter_threshold?}
    B -- Yes --> C[Compute color via config.html.style.primary_colors[0]]
    C --> D[Create cmap with seaborn.light_palette(color, as_cmap=True)]
    D --> E[Compute data = zip(*series.tolist())]
    E --> F[Call pyplot.hexbin(*data, cmap=cmap)]
    F --> G[Call plot_360_n0sc0pe(config) and return its string]
    B -- No --> C2[Compute color via config.html.style.primary_colors[0]]
    C2 --> E2[Compute data = zip(*series.tolist())]
    E2 --> F2[Call pyplot.scatter(*data, color=color)]
    F2 --> G2[Call plot_360_n0sc0pe(config) and return its string]

## Examples:
Conceptual example (no imports shown — describe steps):

1) Prepare a Settings-like object (config) where:
    - config.html.style.primary_colors is a non-empty sequence (e.g., ["#2b8cbe", ...])
    - config.plot.scatter_threshold is an integer threshold (e.g., 500)

2) Prepare a pandas Series named pts where each element is a 2-tuple:
    - Example structure: pts = Series([(x1, y1), (x2, y2), ...])

3) Call scatter_series:
    - result_str = scatter_series(config, pts, x_label="Sepal length", y_label="Petal width")

4) Handle possible errors:
    - Wrap call in try/except to catch AttributeError/IndexError/TypeError if config or series are malformed:
        - If series may be empty, check len(pts) > 0 before calling or handle the TypeError raised by matplotlib.

Notes:
    - If you want the points plotted as (x-array, y-array) instead of a Series of pairs, transform your data first (e.g., create a Series of tuples or use custom plotting otherwise).
    - This function writes to the current matplotlib axes; if you need an isolated figure, create a new figure/axes context before calling (e.g., via pyplot.figure()).

## `src.ydata_profiling.visualisation.plot.scatter_pairwise` · *function*

## Summary:
Create and save/encode a pairwise scatter visualization for two pandas Series — use a hexbin density plot for large series (gridsize=15) or a simple scatter for small series — and return the image string or asset path produced by the shared image exporter.

## Description:
This function:
- Sets the current matplotlib axes labels using the provided x_label and y_label.
- Selects the plot color from config.html.style.primary_colors[0].
- Computes a boolean mask of entries where both series are non-missing: (series1.notna() & series2.notna()).
- If len(series1) > config.plot.scatter_threshold it plots a hexbin density plot (plt.hexbin) using a seaborn-generated light colormap; otherwise it plots a standard scatter (plt.scatter).
- Delegates saving/encoding/closing of the matplotlib figure to plot_360_n0sc0pe(config) and returns that function's string result.

Known callers:
- None discovered in the scanned snapshot. Typical usage is from the report/visualisation pipeline when rendering pairwise plots in profiling reports (i.e., part of the plotting/report generation stage).

Why this is a separate function:
- Encapsulates the pairwise plotting policy (threshold decision, masking, color selection, and exact plotting call) and centralizes delegation to the shared exporter. This promotes reuse and keeps plotting and exporting concerns separated.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Use:
            * config.html.style.primary_colors[0] — first color used for scatter or seed for colormap.
            * config.plot.scatter_threshold — integer threshold; compare with len(series1) to pick hexbin vs scatter.
            * Other config fields are used indirectly by plot_360_n0sc0pe (e.g., config.plot.image_format, config.plot.dpi, config.html.inline, config.html.assets_path, config.html.assets_prefix).
        - Constraint: config.html.style.primary_colors must contain at least one item (otherwise indexing [0] raises IndexError).

    series1 (pd.Series)
        - Type: pd.Series
        - Description: Data for the x-axis. The function uses series1.notna() for masking and len(series1) for thresholding.
        - Note: The length (len(series1)) — not the number of non-missing pairs — controls whether hexbin is used.

    series2 (pd.Series)
        - Type: pd.Series
        - Description: Data for the y-axis. Masked together with series1 via (series1.notna() & series2.notna()) before plotting.

    x_label (str)
        - Type: str
        - Description: Text set on the x-axis using plt.xlabel.

    y_label (str)
        - Type: str
        - Description: Text set on the y-axis using plt.ylabel.

Interdependencies:
    - The boolean mask is computed elementwise using pandas semantics: (series1.notna() & series2.notna()). If series1 and series2 have different indices, pandas will align indices during the boolean operation; callers should prefer index-aligned series for predictable pairing.

## Returns:
    str
    - The returned string is exactly the value produced by plot_360_n0sc0pe(config):
        * If config.html.inline is True and image_format == "svg": raw SVG text (string).
        * If config.html.inline is True and image_format == "png": a base64-encoded PNG data string suitable for inline embedding.
        * If config.html.inline is False: a relative file path suffix (string) created under config.html.assets_path where the image was written.
    - The matplotlib figure will have been closed by plot_360_n0sc0pe before this function returns.

## Raises:
    IndexError
        - Condition: config.html.style.primary_colors is empty (accessing [0] triggers IndexError).

    ValueError
        - Condition: propagated from plot_360_n0sc0pe when an unsupported image format is configured or when config.html.assets_path is None while saving to disk.

    matplotlib errors / TypeErrors
        - Condition: plotting functions (plt.hexbin, plt.scatter) may raise errors if provided incompatible data types; these exceptions are propagated.

    Any other exceptions raised by plot_360_n0sc0pe (I/O, encoding) will propagate.

## Constraints:
Preconditions:
    - A valid matplotlib pyplot context (current figure/axes) is available. It's recommended to call this inside the library's manage_matplotlib_context or otherwise ensure a fresh figure.
    - seaborn must be available in the module namespace as sns because the function calls sns.light_palette(...). If seaborn is not aliased to sns in the module, a NameError will occur.
    - series1 and series2 should be pd.Series (index alignment will affect masking behavior).
    - config must be a Settings instance with the expected attributes (html.style.primary_colors, plot.scatter_threshold, etc.).

Postconditions:
    - An image representing the plotted pairwise view has been saved/encoded by plot_360_n0sc0pe.
    - The current matplotlib figure has been closed (no open figure remains).
    - The return value is the exporter string (inline data or asset path).

## Side Effects:
    - Mutates matplotlib.pyplot current figure/axes by setting labels and drawing (hexbin or scatter).
    - plot_360_n0sc0pe will save the figure to memory or disk and call plt.close(), causing the figure to be closed.
    - May write files to disk when config.html.inline is False and config.html.assets_path is set.
    - No network calls or global state mutations outside matplotlib and filesystem.

## Control Flow:
flowchart TD
    A[Start] --> B[plt.xlabel(x_label); plt.ylabel(y_label)]
    B --> C[color = config.html.style.primary_colors[0]]
    C --> D[indices = series1.notna() & series2.notna()]
    D --> E{len(series1) > config.plot.scatter_threshold?}
    E -- true --> F[cmap = sns.light_palette(color, as_cmap=True)]
    F --> G[plt.hexbin(series1[indices], series2[indices], gridsize=15, cmap=cmap)]
    E -- false --> H[plt.scatter(series1[indices], series2[indices], color=color)]
    G --> I[result = plot_360_n0sc0pe(config)]
    H --> I[result = plot_360_n0sc0pe(config)]
    I --> J[plt closed inside exporter; return result]

## Examples:
Basic usage (with context manager):
    from ydata_profiling.visualisation.context import manage_matplotlib_context
    import pandas as pd

    s1 = pd.Series([0.1, 0.2, None, 0.4])
    s2 = pd.Series([1.0, None, 0.8, 0.6])

    # config must be initialized appropriately for your environment
    with manage_matplotlib_context(config):
        image_str_or_path = scatter_pairwise(config, s1, s2, x_label="A", y_label="B")
    # image_str_or_path is as described in Returns

Edge-case: no overlapping non-missing pairs
    - If (series1.notna() & series2.notna()).any() is False, the function will still produce an image (axes with no points) and return the exporter result. Check for this condition beforehand if you want to skip plotting:
        if not ((s1.notna() & s2.notna()).any()):
            handle_no_data_case()

Error handling example:
    try:
        with manage_matplotlib_context(config):
            out = scatter_pairwise(config, s1, s2, "X", "Y")
    except IndexError:
        # likely config.html.style.primary_colors was empty
        fix_config_colors()
    except ValueError as e:
        # image export problem (see plot_360_n0sc0pe)
        handle_export_error(e)

Notes:
    - The decision to use hexbin is based solely on len(series1), not on the count of non-missing paired observations.
    - The hexbin call uses a fixed gridsize of 15 and a colormap constructed via sns.light_palette(color, as_cmap=True).
    - Because the function relies on pyplot global state and the exporter closes the figure, callers should not expect to continue modifying the same figure after the call returns.

## `src.ydata_profiling.visualisation.plot._plot_stacked_barh` · *function*

## Summary:
Renders a horizontal stacked bar plot from a pandas Series and returns the Axes and (optionally) the Legend.

## Description:
This helper builds a compact horizontal stacked bar chart where each segment represents one value from the input Series. Each segment receives a color from the supplied colors list, and segments larger than 8% of the total are annotated with percentage and absolute value labels (when the Matplotlib API supports bar_label).

Known callers within the provided context:
- No direct callers were found in the provided file-level context. In typical usage this function is invoked by the package's visualization/reporting code to visualize categorical distributions or frequency summaries as a compact stacked bar.

Why this logic is extracted:
- Drawing a small, consistently styled stacked horizontal bar (with label placement, color handling, and optional legend) is a self-contained visualization task reused by higher-level report generation. Extracting it keeps the caller code concise and centralizes decisions about sizing, labeling thresholds, legend handling, and axis configuration.

## Args:
    data (pd.Series):
        Series of numeric values to visualize. The Series index provides the labels for each segment; values are used as segment widths.
        - Expected to be numeric (int/float). If values are non-numeric, a TypeError or ValueError may be raised by Matplotlib when plotting.
        - If data.sum() == 0, a ZeroDivisionError will occur when computing percentages (see Raises).
    colors (List):
        Iterable of color specifications (matplotlib-acceptable color strings or tuples). Each color is paired with the corresponding element of `data` using zip; the number of plotted segments equals the minimum length of `data` and `colors`.
        - If colors has fewer entries than data, remaining data entries will be omitted (zip truncation).
        - If colors has more entries than data, extra colors are ignored.
    hide_legend (bool, default False):
        When False (default), a legend is added to the axes and returned. When True, no legend is created and the returned legend value is None.

## Returns:
    Tuple[plt.Axes, matplotlib.legend.Legend]:
        - plt.Axes: The Matplotlib Axes object containing the rendered stacked horizontal bar. The axes are created by this function (via plt.subplots) and are returned to the caller so the caller can further modify, save, or embed the figure.
        - matplotlib.legend.Legend: The legend instance if one was created (hide_legend is False). If hide_legend is True, this value is None.

## Raises:
    ZeroDivisionError:
        Raised when data.sum() == 0 because the function computes percentages using x / data.sum().
    Exceptions raised by Matplotlib (TypeError, ValueError):
        If `data` contains values or `colors` contains entries not acceptable to Matplotlib plotting functions, Matplotlib may raise type/formatting errors when calling barh or when interrogating patch facecolors.
    Indexing/Attribute errors:
        The function assumes barh returns a container with at least one Rectangle patch; if Matplotlib behaviour changes, attribute access on rects[0] may raise errors.

## Constraints:
Preconditions:
    - `data` must be a pandas Series whose index yields meaningful labels; values should be numeric for correct width computation and percentage labeling.
    - The caller must have Matplotlib available and a pyplot alias (`plt`) in scope consistent with the module (the function creates a new Figure/Axes via plt.subplots).
    - Prefer non-negative values in `data` for visually meaningful stacked widths; negative widths are not validated and will produce unexpected visuals.

Postconditions:
    - A new Matplotlib Figure and Axes have been created and populated with horizontal bar segments corresponding to the zipped values of `data` and `colors`.
    - The returned Axes has axis lines turned off, x-limits set to [0, sum(data)], and y-limits set to [0.4, 1.6].
    - If hide_legend is False, a legend is attached to the axes and returned; otherwise the legend return value is None.

## Side Effects:
    - Creates a Matplotlib Figure and Axes (plt.subplots). This mutates Matplotlib's state by creating objects in the current Matplotlib backend.
    - May modify global Matplotlib rcParams indirectly via figure/axes creation (standard Matplotlib behavior).
    - No file or network I/O is performed.
    - No mutation of the input Series `data` or external global variables in the module is performed.

## Control Flow:
flowchart TD
    Start --> CreateFigure[Create Figure and Axes via plt.subplots]
    CreateFigure --> ConfigureAxes[Turn axis off; set xlim to (0, sum(data)); set ylim to (0.4, 1.6)]
    ConfigureAxes --> LoopSegments[For each (x, label, color) in zip(data, labels, colors)]
    LoopSegments --> DrawRect[Draw horizontal bar segment (barh) at left=starts]
    DrawRect --> GetColor[Extract segment facecolor (r,g,b,_)]
    GetColor --> ChooseTextColor[If r*g*b < 0.5 then text_color = "white" else "darkgrey"]
    ChooseTextColor --> ComputePct[pc_of_total = x / data.sum() * 100]
    ComputePct --> CheckAnnotate{pc_of_total > 8 AND ax has bar_label?}
    CheckAnnotate -->|Yes| Annotate[Call ax.bar_label(...) with percentage and count]
    CheckAnnotate -->|No| SkipAnnotate[Do not annotate]
    Annotate --> IncrementStart[starts += x]
    SkipAnnotate --> IncrementStart
    IncrementStart --> LoopSegments
    LoopSegments --> AfterLoop[After loop completes]
    AfterLoop --> LegendCheck{hide_legend is False?}
    LegendCheck -->|True| CreateLegend[Create legend; assign to legend variable]
    LegendCheck -->|False| NoLegend[legend = None]
    CreateLegend --> ReturnAxes[Return (ax, legend)]
    NoLegend --> ReturnAxes

## Examples:
Example 1 — common usage:
    - Prepare a pandas Series where the index contains segment labels and values are counts or weights.
    - Provide a color list aligned in order with the Series values (same length or longer).
    - Call the function to obtain the Axes for further composition or saving.

    Example call (conceptual):
    data = pd.Series([50, 30, 20], index=["A", "B", "C"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    ax, legend = _plot_stacked_barh(data, colors, hide_legend=False)
    # Then save or further customize ax, e.g. ax.figure.savefig(...)

Example 2 — zero-sum safety:
    - If data.sum() == 0, the function will attempt to compute percentages and will raise ZeroDivisionError.
    - The caller should guard against zero totals if that is a possible input:
    if data.sum() == 0:
        handle_empty_case()
    else:
        ax, legend = _plot_stacked_barh(data, colors)

Notes and implementation hints:
    - The function uses zip(data, labels, colors), so any mismatch in lengths results in truncation to the shortest iterable.
    - Percentage annotation uses a threshold of 8% of the total; this threshold is hard-coded.
    - The function checks for bar_label availability on the axes (hasattr(ax, "bar_label")) to maintain compatibility with Matplotlib versions lacking that API.

## `src.ydata_profiling.visualisation.plot._plot_pie_chart` · *function*

## Summary:
Builds a 4x4 inch pie chart from a pandas Series and returns the Axes containing the plot and the Legend object (or None), with slice labels formatted as percentage plus integer counts.

## Description:
Creates a matplotlib pie chart using numeric values in the supplied pandas Series. The function constructs an autopct formatter that computes the absolute count per slice by multiplying the percentage (provided by matplotlib) with the series total and rounding to the nearest integer. Plot appearance details (figure size, slice text color, legend placement and styling) are fixed by this helper so callers get consistent pie-chart rendering without repeating matplotlib setup.

Known callers:
- Not listed in the immediate scan. Intended for use by higher-level visualisation utilities that need to render categorical distributions / value counts as pie charts within the ydata_profiling.visualisation package.

Why this logic is extracted:
- Encapsulates pie-chart layout, label formatting, and legend creation to provide a single, reusable, consistent plotting primitive for the visualisation module.

## Args:
    data (pandas.Series)
        1-D labelled array of numeric slice sizes. The series index provides the labels used for the legend.
        - Expected element types: numeric (int, float). NaNs are not specially handled here and are passed to matplotlib, which may raise or render accordingly.
        - The function uses data.index.values as legend labels when hide_legend is False.
    colors (List)
        Sequence of matplotlib-compatible color specifications (strings, RGB tuples, hex codes, etc.).
        - Should be at least as long as `data` for distinct colors; matplotlib will cycle colors if fewer are provided.
    hide_legend (bool, optional)
        If True, the function intentionally does not create or return a legend. Defaults to False.

Interdependencies:
- Legend labels are directly taken from data.index.values; ensure `data` has meaningful index labels when hide_legend is False.

## Returns:
    tuple(matplotlib.axes.Axes, matplotlib.legend.Legend | None)
    - Axes: the matplotlib Axes object containing the pie chart (a new figure/subplot is created with figsize=(4, 4)).
    - Legend or None: If hide_legend is False, a matplotlib.legend.Legend is created with:
        * handles: the wedges returned by plt.pie
        * labels: data.index.values
        * fontsize: "large"
        * bbox_to_anchor: (0, 0)
        * loc: "upper left"
      If hide_legend is True, the second element returned is None.

## Raises:
    - No exceptions are raised explicitly by this function.
    - It propagates any exceptions raised by the underlying matplotlib calls (e.g., errors from plt.subplots, plt.pie, plt.legend) such as when invalid input types or values are provided.

## Constraints:
Preconditions:
    - `data` must be a pandas.Series of numeric slice sizes. Values should preferably be non-negative and meaningful for pie representation.
    - `colors` should be a sequence of valid matplotlib color specifications.

Postconditions:
    - A new matplotlib Figure/ Axes with the pie chart is created (via plt.subplots(figsize=(4, 4))) and returned.
    - If hide_legend is False, a Legend object is created and returned with the configured handles and labels.

## Side Effects:
    - Calls into matplotlib.pyplot: creates a new Figure and Axes (plt.subplots) and mutates matplotlib state by plotting (plt.pie) and possibly adding a legend (plt.legend).
    - No file, network, or external I/O is performed.
    - No global variables within this module are modified.

## Detailed behaviour (implementation-specific facts):
    - The autopct formatter is created by make_autopct(values) and, for each slice percentage pct, computes:
        total = np.sum(values)
        val = int(round(pct * total / 100.0))
      and returns the label string formatted as "{pct:.1f}%  ({val:d})".
    - The pie call uses textprops={"color": "w"} so the autopct/text drawn on slices will be white.
    - The figure size is fixed to (4, 4) inches in plt.subplots call.
    - Legend formatting parameters are exactly: fontsize="large", bbox_to_anchor=(0, 0), loc="upper left".

## Control Flow:
flowchart TD
    Start --> Define_make_autopct
    Define_make_autopct --> Create_figure_axes[plt.subplots(figsize=(4,4))]
    Create_figure_axes --> Call_plt_pie(plt.pie with data, autopct=make_autopct(data), textprops={"color":"w"}, colors=colors)
    Call_plt_pie --> Receive_wedges
    Receive_wedges --> Check_hide_legend{hide_legend?}
    Check_hide_legend -- true --> Set_legend_None
    Check_hide_legend -- false --> Create_legend(plt.legend(wedges, data.index.values, fontsize="large", bbox_to_anchor=(0,0), loc="upper left"))
    Set_legend_None --> Return(ax, None)
    Create_legend --> Return(ax, legend)

## Examples:
Typical usage:
    import pandas as pd
    data = pd.Series([120, 80, 30], index=["cat", "dog", "mouse"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    ax, legend = _plot_pie_chart(data, colors, hide_legend=False)
    # ax contains the pie; legend is a Legend anchored at (0,0) with labels ["cat","dog","mouse"]

Hiding legend:
    ax, legend = _plot_pie_chart(data, colors, hide_legend=True)
    assert legend is None

Handling exceptions:
    try:
        ax, legend = _plot_pie_chart(data, colors)
    except Exception as err:
        # Matplotlib may raise errors for invalid input; handle or re-raise as appropriate
        raise

## `src.ydata_profiling.visualisation.plot.cat_frequency_plot` · *function*

## Summary:
Renders a categorical-frequency visualization (stacked horizontal bar or pie chart) for the provided categorical counts and returns the serialized image reference (inline image string or asset file path) produced by the project's image-export utility.

## Description:
This function selects plot parameters from the given configuration (colors and plot type), prepares a color sequence sized to the data, delegates drawing to small, focused helpers (a compact horizontal stacked-bar renderer or a pie-chart renderer), and then exports the produced Matplotlib figure using the project's plot_360_n0sc0pe utility.

Known callers:
- No direct callers were discovered in the provided file-level context. Typically this function is invoked by the visualization/reporting layer of the profiling pipeline when rendering a categorical variable's frequency breakdown for inclusion in an HTML report or saved asset.
- Typical trigger: the profiling/report generation code needs a compact visual representation of a categorical distribution and calls this function with the report Settings and the value counts (pandas.Series) to get back an embeddable image string or asset path.

Why this is a separate function:
- It centralizes configuration lookup (colors, plot type), color-length normalization, and the choice between two plotting primitives. This keeps higher-level report generation code concise and ensures consistent rendering and export behavior (including legend handling and final image export) across all places that need the same visualization.

## Args:
    config (Settings):
        Configuration object providing plotting and HTML/export options accessed in this function:
        - config.plot.cat_freq.colors: Optional[List[str]] or None — base colors for segments. If None, defaults to Matplotlib rcParams color cycle.
        - config.plot.cat_freq.type: str — expected values 'bar' or 'pie' (case-sensitive).
        - config.vars.cat.redact: bool — if True, legend creation is suppressed when calling the plotting helpers.
        - config.html.inline / config.html.assets_path / config.html.assets_prefix / config.plot.image_format / config.plot.dpi: Used transitively by plot_360_n0sc0pe when exporting the final image.
        Preconditions: config must expose the above attributes (typical Settings instance from ydata_profiling).

    data (pandas.Series or list[pandas.Series]):
        - If plot type is 'pie': a pandas.Series of numeric slice sizes (index provides labels). Passing a list here is unsupported by the implementation and will be forwarded as-is to the pie helper (likely causing an error).
        - If plot type is 'bar': either
            * a pandas.Series mapping labels -> numeric counts (the most common case), or
            * a list of pandas.Series objects: the function will call the stacked-bar helper for each Series in the list in iteration order. Note: only the plot/legend returned from the last element will be used for export (see edge case below).
        - Values should be numeric (int/float). NaNs or non-numeric values are not specially handled and will be passed to Matplotlib, which may raise an error.

## Returns:
    str
    - A string produced by plot_360_n0sc0pe representing the exported image:
        * If config.html.inline is True and image_format is "svg": the raw SVG string.
        * If config.html.inline is True and image_format is "png": a base64-encoded "data:" image string (image/png).
        * If config.html.inline is False: a relative asset path suffix (string) where the image was written under config.html.assets_path.
    - The returned string is suitable for embedding directly into generated HTML (inline) or for inclusion as a path to a saved asset (non-inline).
    - The function always delegates the actual saving/encoding/closing of the Matplotlib figure to plot_360_n0sc0pe.

## Raises:
    ValueError:
        - If config.plot.cat_freq.type is not one of 'bar' or 'pie', a ValueError is raised with a message indicating the valid choices.

    Exceptions raised by helpers or Matplotlib (propagated):
        - _plot_stacked_barh may raise ZeroDivisionError when data.sum() == 0 (it computes percentages), TypeError/ValueError if non-numeric values or invalid colors are supplied.
        - _plot_pie_chart will propagate Matplotlib errors if the input is not acceptable (e.g., wrong shape/type).
        - plot_360_n0sc0pe may raise ValueError for unsupported image types or if config.html.assets_path is None when inline is False.
    Notes:
        - If data is provided as a list while plot_type == 'pie', the list will be forwarded to _plot_pie_chart which expects a pandas.Series; this mismatch will likely raise an exception from Matplotlib or the helper.

## Constraints:
Preconditions:
    - The config argument must be a valid Settings object containing the attributes mentioned in Args.
    - Matplotlib must be available and usable in the execution environment.
    - For meaningful visuals, data values should be non-negative numeric counts; zero totals may produce exceptions in the stacked-bar helper.

Postconditions:
    - One or more Matplotlib Figures/Axes are created by the helper(s), and the image is saved/encoded and the matplotlib state is closed by plot_360_n0sc0pe (it calls plt.savefig(...) and plt.close()).
    - The return value is the exported image string or asset path; no open Matplotlib figures remain after this call (helpers create figures; plot_360_n0sc0pe closes them).

## Side Effects:
    - Calls into Matplotlib via helper functions: creates Figure/Axes objects and draws plots.
    - Delegates to plot_360_n0sc0pe which performs plt.savefig(...) and plt.close(), possibly writing files to disk when config.html.inline is False (writes to config.html.assets_path).
    - No network I/O beyond local filesystem writes (when inline is False).
    - No mutation of the passed pandas.Series objects or global module variables beyond normal Matplotlib state changes.

## Control Flow:
flowchart TD
    Start --> GetColors[Read colors from config.plot.cat_freq.colors]
    GetColors --> ColorsDefault{colors is None?}
    ColorsDefault -->|Yes| UseRcParams[Use plt.rcParams['axes.prop_cycle'].by_key()['color']]
    ColorsDefault -->|No| KeepColors[Use provided colors]
    UseRcParams --> EnsureLength
    KeepColors --> EnsureLength
    EnsureLength[Ensure colors length >= len(data); repeat colors if necessary] --> GetPlotType[Read plot_type from config.plot.cat_freq.type]
    GetPlotType --> IsBar{plot_type == "bar"?}
    IsBar -->|Yes| DataIsList{isinstance(data, list)?}
    DataIsList -->|Yes| LoopList[For each Series v in data: call _plot_stacked_barh(v, colors, hide_legend=config.vars.cat.redact)]
    DataIsList -->|No| CallStacked[_plot_stacked_barh(data, colors, hide_legend=config.vars.cat.redact)]
    LoopList --> AfterPlot[After loop ends, use last (plot, legend) returned]
    CallStacked --> AfterPlot
    AfterPlot --> IsPie{plot_type == "pie"?}
    IsPie -->|Yes| CallPie[_plot_pie_chart(data, colors, hide_legend=config.vars.cat.redact)]
    IsPie -->|No| InvalidType[Raise ValueError("'... ' is not a valid plot type! Expected values are ['bar', 'pie']")]
    CallPie --> AfterPlot2[Receive (plot, legend)]
    AfterPlot2 --> Export[Call plot_360_n0sc0pe(config, bbox_extra_artists=[] if legend is None else [legend], bbox_inches="tight")]
    InvalidType --> EndError[Error raised]
    Export --> Return[result string]
    EndError --> Return[error]

## Examples:
Example 1 — Bar plot (common case):
    import pandas as pd
    # data: counts per category
    data = pd.Series([120, 80, 30], index=["cat", "dog", "mouse"])
    # config: must be a Settings instance with plot.cat_freq.type == "bar"
    config.plot.cat_freq.type = "bar"
    config.plot.cat_freq.colors = None  # or a list of colors
    config.vars.cat.redact = False
    result_str = cat_frequency_plot(config, data)
    # result_str is either an inline image string (if config.html.inline) or a saved asset path suffix.

Example 2 — Bar plot with multiple series (list):
    # Render multiple stacked-bar visuals by passing a list of Series.
    # Note: the function will iterate over the list and call the bar helper for each element,
    # but only the final produced plot/legend will be exported and returned.
    series_list = [
        pd.Series([50, 30, 20], index=["A", "B", "C"]),
        pd.Series([10, 5, 85], index=["x", "y", "z"]),
    ]
    config.plot.cat_freq.type = "bar"
    result_str = cat_frequency_plot(config, series_list)
    # The returned image corresponds to the visualization of series_list[-1].

Example 3 — Pie chart:
    data = pd.Series([50, 30, 20], index=["A", "B", "C"])
    config.plot.cat_freq.type = "pie"
    config.vars.cat.redact = False
    result_str = cat_frequency_plot(config, data)

Example 4 — Handling invalid plot type:
    config.plot.cat_freq.type = "histogram"
    try:
        cat_frequency_plot(config, data)
    except ValueError as err:
        # err message will indicate valid plot types ['bar', 'pie']
        handle_invalid_config(err)

Notes and implementation hints:
    - Only 'bar' and 'pie' are supported; passing other strings will raise ValueError.
    - Passing a list of Series is explicitly handled only for the 'bar' plot type; for 'pie' the implementation expects a single Series.
    - Legend creation is controlled via config.vars.cat.redact and will be passed to the image exporter as bbox_extra_artists when present so that tight bounding-box exports include the legend.

## `src.ydata_profiling.visualisation.plot.create_comparison_color_list` · *function*

## Summary:
Returns a list of hex color strings for comparison plots: if the configured primary color list is considered "smaller" than the configured labels collection, generate a gradient colormap matching the number of labels; otherwise return the configured primary color list unchanged.

## Description:
This utility extracts two values from a Settings-like configuration object: a list of primary colors and a collection of labels. It compares those two values and, when the comparison evaluates to True, synthesizes a LinearSegmentedColormap interpolating from the first primary color to the second (or black if a second color is not available) with as many discrete entries as there are labels; the colormap entries are converted to hex strings and returned.

Known callers within the repository:
- No direct callers were found in the available repository graph for this function. Typical usage (outside this repository graph) is from plotting/visualisation code that needs a color for each category or label when constructing side-by-side or comparison plots.

Why this logic is its own function:
- Responsibility separation: encapsulates the policy for deciding whether to reuse user-provided primary colors or to synthesize a larger color palette that matches the number of labels.
- Reuse: centralizes the colormap creation logic so multiple plotting routines can call it consistently.
- Testability: makes the color-list creation deterministic and easy to unit test in isolation.

## Args:
    config (Settings):
        - Type: Settings-like object with namespace attributes
            - config.html.style.primary_colors: expected to be a sequence (list/tuple) of color strings (typically hex strings such as "#RRGGBB").
            - config.html.style._labels: expected to be a sequence (list/tuple) of labels (any objects where len(labels) is meaningful). The code treats this as a collection whose length determines the number of required colors.
        - Notes:
            - The function performs the expression `colors < labels` as its decision criterion. For predictable behavior in Python 3, both attributes should be sequences (e.g., lists) so that lexicographic comparison is defined and meaningful.
            - The function does not coerce types: if attributes are missing or of incompatible types, standard Python exceptions will be raised.

## Returns:
    List[str]:
        - A list of color strings in hex format (e.g., "#rrggbb").
        - Normal return paths:
            1) If the comparison `colors < labels` evaluates to False: returns the original config.html.style.primary_colors unchanged (the same object assigned to the local variable `colors`).
            2) If the comparison evaluates to True: returns a new list with len(labels) entries (the colormap N equals len(labels)). Each entry is rgb2hex(cmap(i)) for i in range(cmap.N).
        - Edge/degenerate cases:
            - If len(labels) == 0 and the comparison is True, an attempt is made to build a colormap with N == 0; behavior depends on matplotlib implementation and may raise a ValueError or yield a colormap with cmap.N == 0 resulting in an empty list being returned.
            - If primary_colors already has length >= len(labels) but `colors < labels` still evaluates True due to lexicographic ordering, the function will still generate the gradient palette.

## Raises:
    - AttributeError:
        - If `config.html` or `config.html.style` or the attributes `primary_colors` / `_labels` are missing.
    - IndexError:
        - If the comparison evaluates True and `primary_colors` is empty, the code accesses `colors[0]` and raises IndexError.
    - TypeError:
        - If `colors < labels` attempts to compare incompatible types (for example, a list vs an int), Python will raise TypeError.
    - ValueError (possible, raised by matplotlib):
        - If matplotlib.colors.LinearSegmentedColormap.from_list is called with N that is invalid (for example N == 0), matplotlib may raise ValueError; this propagates out of the function.

## Constraints:
    Preconditions:
        - config must expose html.style.primary_colors and html.style._labels attributes.
        - primary_colors should be a sequence of color specifications (strings) for predictable results.
        - _labels should be a sequence whose length is the intended number of distinct colors when a generated palette is required.
    Postconditions:
        - The function returns a list of hex color strings.
        - No external state is modified by this function.

## Side Effects:
    - None: the function performs no I/O, does not mutate global state, and does not call external services. It only reads from the provided config object and constructs in-memory color data.

## Control Flow:
flowchart TD
    A[Start] --> B[Read config.html.style.primary_colors -> colors]
    B --> C[Read config.html.style._labels -> labels]
    C --> D{colors < labels ?}
    D -- No --> E[Return colors (original list)]
    D -- Yes --> F[init = colors[0]]
    F --> G{len(colors) >= 2 ?}
    G -- Yes --> H[end = colors[1]]
    G -- No --> I[end = "#000000"]
    H --> J[Create LinearSegmentedColormap from [init, end] with N = len(labels)]
    I --> J
    J --> K[Build list: [rgb2hex(cmap(i)) for i in range(cmap.N)]]
    K --> L[Return generated color hex list]
    E --> End
    L --> End

## Examples:
- Example 1 (typical successful generation):
    - Given config.html.style.primary_colors = ["#ff0000"] and config.html.style._labels = ["A", "B", "C"]:
      - The comparison `colors < labels` evaluates True (both are sequences); the function uses init="#ff0000" and end="#000000" (fallback) and generates 3 interpolated colors returned as ["#rrggbb", "#rrggbb", "#rrggbb"] (three hex strings forming a gradient from red to black).

- Example 2 (no generation — reuse configured colors):
    - Given config.html.style.primary_colors = ["#ff0000", "#00ff00", "#0000ff"] and config.html.style._labels = ["A", "B"]:
      - If `colors < labels` evaluates False, the original list ["#ff0000", "#00ff00", "#0000ff"] is returned unchanged.

- Example 3 (error handling guidance):
    - If config.html.style.primary_colors is an empty list and `colors < labels` is True:
      - The function will attempt to access colors[0] and raise IndexError. Calling code should validate that primary_colors is non-empty before invoking this function or catch IndexError/AttributeError/TypeError as appropriate.

Notes / Implementation hints:
- The comparison operator (`<`) is used verbatim in the code; it performs lexicographic comparison for sequences in Python. If the intent is to compare counts (number of colors vs number of labels), consider changing the condition to len(colors) < len(labels) for more predictable behavior.
- The generated list elements are produced by matplotlib.colors.rgb2hex and therefore are normalized hex strings (lowercase/uppercase may depend on matplotlib version).

## `src.ydata_profiling.visualisation.plot._format_ts_date_axis` · *function*

## Summary:
Apply concise, human-readable date formatting to a matplotlib axis when the provided pandas Series uses a DatetimeIndex so the x-axis tick locator and formatter display concise dates.

## Description:
This helper inspects the index of the provided pandas Series and, if it is a pandas.DatetimeIndex, sets the axis x-axis major locator to matplotlib.dates.AutoDateLocator and the major formatter to matplotlib.dates.ConciseDateFormatter(locator). This centralizes the logic for consistent datetime x-axis formatting across plotting functions.

Known callers within the codebase:
- Plotting helpers that render time-based series inside this module (for example: line-plotting utilities, autocorrelation/partial-autocorrelation plotting helpers, or any function that creates a figure/axis for series visualization). Typical usage is to call this function immediately after creating or receiving an axis and before drawing time series data so tick layout/labels are reasonable for date/time scales.

Why extracted:
- Consolidates datetime axis formatting in one place to avoid duplicating locator/formatter setup.
- Keeps plotting functions focused on data rendering while offloading presentation details of date tick formatting to a small, testable helper.
- Makes it easier to update date-formatting behavior for all plots by changing one function.

## Args:
    series (pandas.Series):
        The series whose index will be inspected. The function only checks the type of series.index (it does not modify the series).
        - Required properties: must have an .index attribute.
        - Typical value: a Series with a pandas.DatetimeIndex when plotting time series.
    axis (matplotlib.axis.Axis):
        The matplotlib axis object to modify. The function will access axis.xaxis and call set_major_locator and set_major_formatter on it.
        - Expected type: a Matplotlib Axis (for example the object returned by pyplot.subplots() or pyplot.gca()).

Interdependencies:
- None between parameters beyond the fact that series.index controls whether modifications occur; axis is always the target of modifications when the condition holds.

## Returns:
    matplotlib.axis.Axis
    The same axis object passed in, potentially mutated. If series.index is a pandas.DatetimeIndex, the axis.xaxis major locator and formatter will be set; otherwise the axis is returned unchanged.

Possible return cases:
- If series.index is a pandas.DatetimeIndex: axis with axis.xaxis.major locator set to AutoDateLocator and major formatter set to ConciseDateFormatter tied to that locator.
- If series.index is not a pandas.DatetimeIndex: the axis is returned with no modifications performed by this function.

## Raises:
    AttributeError:
        - If the provided axis does not have an xaxis attribute (e.g., a non-matplotlib object), accessing axis.xaxis will raise AttributeError.
        - If the provided series does not have an index attribute (unlikely for pandas.Series, but possible if a non-conforming object is passed), accessing series.index may raise AttributeError.
    (No exceptions are explicitly raised by the function; the above are the implicit exceptions that can occur when preconditions are violated.)

## Constraints:
Preconditions:
- `series` should be a pandas.Series or an object exposing an `.index` attribute (the code checks `isinstance(series.index, pd.DatetimeIndex)`).
- `axis` must be a Matplotlib axis-like object that exposes an `.xaxis` attribute with methods set_major_locator and set_major_formatter.

Postconditions:
- If preconditions hold and series.index is a pandas.DatetimeIndex, axis.xaxis.major locator will be an AutoDateLocator instance and axis.xaxis.major formatter will be a ConciseDateFormatter bound to that locator.
- The function returns the same axis object (mutated if the condition applied).

## Side Effects:
- Mutates the provided axis object by calling axis.xaxis.set_major_locator(locator) and axis.xaxis.set_major_formatter(ConciseDateFormatter(locator)) when the series index is a DatetimeIndex.
- No I/O, network calls, global state mutation, or external service calls.

## Control Flow:
flowchart TD
    A[Start: _format_ts_date_axis(series, axis)] --> B{series.index is instanceof pandas.DatetimeIndex?}
    B -- Yes --> C[Create AutoDateLocator instance]
    C --> D[axis.xaxis.set_major_locator(locator)]
    D --> E[axis.xaxis.set_major_formatter(ConciseDateFormatter(locator))]
    E --> F[Return axis (modified)]
    B -- No --> G[Return axis (unchanged)]

## Examples (prose):
1) Typical usage for a time series plot:
- Given a pandas.Series whose index is a pandas.DatetimeIndex, create a matplotlib figure and axis (for example via pyplot.subplots()).
- Call this function with the series and the axis before or after plotting the data. When the series index is datetime-like, the x-axis tick locator and formatter will be set so tick labels present concise, well-spaced date/time labels.

2) Non-datetime case:
- If the series index is not a pandas.DatetimeIndex (e.g., integer RangeIndex or categorical index), this function performs no change to the axis and returns it as-is. Plotting proceeds with the axis's previous tick configuration.

3) Error handling:
- If a caller passes a non-matplotlib object as axis, the call will likely raise AttributeError when the helper tries to access axis.xaxis. Callers should validate or ensure they supply a proper matplotlib axis.

Notes:
- This function is intentionally small and defensive: it only applies date formatting when the index is explicitly a pandas.DatetimeIndex. It does not attempt to coerce strings or numbers into datetimes; callers that require coercion should convert the index to a DatetimeIndex before calling this helper.

## `src.ydata_profiling.visualisation.plot.plot_timeseries_gap_analysis` · *function*

## Summary:
Draws one or more time series and shaded gap regions onto a matplotlib axis and returns the image representation produced by the repository's saver utility.

## Description:
This function creates a matplotlib Figure and Axes, plots either a single pandas.Series or a list of Series, overlays translucent rectangular shaded regions for each provided gap, applies concise datetime axis formatting when a Series has a DatetimeIndex, and then delegates saving/encoding/closing to plot_360_n0sc0pe.

Known callers and context:
- Used by the report/visualization stage of profiling pipelines that need to visualize time-series data with gaps highlighted. Typical callers prepare the Series and gap intervals and call this function immediately before embedding or saving the result into a profile report.
- It relies on helper utilities:
  - create_comparison_color_list(config) to produce the color palette used for plotting. Note: create_comparison_color_list is a shared utility; according to its own documentation it has no direct callers discovered in the repository graph, but this function invokes it to obtain colors.
  - _format_ts_date_axis(series, ax) to set AutoDateLocator/ConciseDateFormatter when appropriate.
  - plot_360_n0sc0pe(config) to save/encode the created figure and close it.

Why this logic is extracted:
- Centralizes plotting, consistent axis formatting, and gap-highlighting presentation rules.
- Delegates image encoding/saving to a single utility, separating drawing from output concerns.
- Enables reuse across multiple report-generating routines and simplifies testing of visualization behavior.

## Args:
    config (Settings):
        - Type: Settings-like object. Indirectly required attributes:
            * config.html.style.primary_colors (sequence of str) — used by create_comparison_color_list.
            * config.html.style._labels (sequence) — used when plotting multiple series.
            * Other config fields read later by plot_360_n0sc0pe (e.g., config.plot.image_format, config.plot.dpi, config.html.inline, config.html.assets_path, config.html.assets_prefix).
        - Missing attributes will raise AttributeError via helper functions.

    series (pandas.Series | list[pandas.Series]):
        - If a single pandas.Series:
            * The Series must support pandas.Series.plot and expose .index.
            * If the index is a pandas.DatetimeIndex, concise date formatting is applied to the x-axis.
        - If a list of pandas.Series:
            * Each element is plotted separately and compared visually.
            * A global vertical range is computed across all series (min_ and max_) and used for gap shading.
        - Note: the function checks `isinstance(series, list)` to determine the multi-series branch; passing other iterables (e.g., tuple) will take the single-series branch unless explicitly a list.

    gaps (pandas.Series | list[pandas.Series]):
        - Matches the function signature: Union[pd.Series, List[pd.Series]].
        - Expected shapes:
            * Single-series mode: `gaps` should be an iterable of gap x-coordinate collections (each element `gap` is passed as the x argument to Axes.fill_between). Examples: slices of the Series.index, numpy arrays of timestamps, or pandas.Index objects.
            * Multi-series mode (when `series` is a list): `gaps` must be a list-like with one element per series; each element (here named `gaps_`) is itself an iterable of gap x-coordinate collections for that series.
        - Important: when `series` is a list, the function uses zip(series, gaps, colors, labels). Unequal lengths among these four iterables will silently truncate to the shortest sequence.

    figsize (tuple) = (6, 3)
        - Tuple specifying (width, height) in inches passed to matplotlib.figure(figsize=figsize).

## Returns:
    str
    - The function returns the value returned by plot_360_n0sc0pe(config). Although the function is annotated as returning matplotlib.figure.Figure, in practice it returns:
        * If config.html.inline is True and image_format == "svg": raw SVG text (str).
        * If config.html.inline is True and image_format == "png": a base64 data-URL string (str).
        * If config.html.inline is False: a string suffix/relative path indicating where the image file was saved.
    - If plot_360_n0sc0pe raises an exception, this function propagates that exception instead of returning.

## Raises:
    - AttributeError:
        * If expected attributes are missing on config (e.g., config.html, config.html.style), or if axis-like objects expected by helpers are malformed.
    - IndexError:
        * If create_comparison_color_list(config) returns an empty list and the code attempts to access colors[0] (single-series branch) or colors is shorter than series list and colors[i] is accessed.
    - ValueError:
        * Propagated from plot_360_n0sc0pe for unsupported image formats or missing config.html.assets_path when saving to disk.
    - TypeError:
        * If incompatible types are passed to helpers (e.g., non-iterable gaps elements or invalid comparisons inside create_comparison_color_list).
    - Any matplotlib / pandas plotting errors raised by Series.plot, ax.fill_between, or min()/max() operations will propagate.

## Constraints:
Preconditions:
    - `series` must be a pandas.Series or a Python list of pandas.Series.
    - Each Series must support .plot and expose .index (DatetimeIndex expected if date formatting is desired).
    - `gaps` must conform to the shapes described above (iterables of x-values acceptable to Axes.fill_between).
    - config must expose the fields required by create_comparison_color_list and plot_360_n0sc0pe.

Postconditions:
    - The created matplotlib figure is saved/encoded and closed by plot_360_n0sc0pe (no open figure remains in pyplot state).
    - The returned value is a string representing the saved/encoded image or a file path suffix.

## Side Effects:
    - Creates a matplotlib Figure and Axes (plt.figure, fig.add_subplot).
    - Calls pandas.Series.plot to draw lines on the axis.
    - Mutates the axis by calling _format_ts_date_axis (which may set AutoDateLocator and ConciseDateFormatter).
    - Calls ax.yaxis.set_major_locator(MaxNLocator(integer=True)).
    - Calls ax.fill_between to draw shaded gap regions.
    - Calls plot_360_n0sc0pe(config) which saves the figure (either to memory buffers or to disk) and calls plt.close(); therefore I/O occurs (memory or disk) depending on config.
    - Does not mutate the Series objects themselves.

## Implementation details (behavior exactly matching the source):
    - Creates figure: fig = plt.figure(figsize=figsize)
    - Adds axis: ax = fig.add_subplot(111)
    - colors = create_comparison_color_list(config)
    - If isinstance(series, list):
        * min_ = min(s.min() for s in series)
        * max_ = max(s.max() for s in series)
        * labels = config.html.style._labels
        * Loops: for serie, gaps_, color, label in zip(series, gaps, colors, labels):
            - serie.plot(ax=ax, label=label, color=color, alpha=0.65)
            - _format_ts_date_axis(serie, ax)
            - ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            - For each gap in gaps_: ax.fill_between(x=gap, y1=min_, y2=max_, color=color, alpha=0.25)
    - Else (single-series):
        * series.plot(ax=ax)
        * _format_ts_date_axis(series, ax)
        * ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        * For each gap in gaps: ax.fill_between(x=gap, y1=series.min(), y2=series.max(), color=colors[0], alpha=0.25)
    - Returns: plot_360_n0sc0pe(config)

    - Note the explicit alpha values used by the implementation:
        * Line alpha for each plotted series: 0.65
        * Gap shading alpha for fill_between: 0.25

## Control Flow:
flowchart TD
    Start[Start] --> CreateFig[fig = plt.figure(figsize)]
    CreateFig --> AddAx[ax = fig.add_subplot(111)]
    AddAx --> Colors[colors = create_comparison_color_list(config)]
    Colors --> IsList{isinstance(series, list)?}
    IsList -- Yes --> ComputeMinMax[min_ = min(s.min() for s in series); max_ = max(s.max() for s in series)]
    ComputeMinMax --> Labels[labels = config.html.style._labels]
    Labels --> ForEachSeries[for serie, gaps_, color, label in zip(series, gaps, colors, labels)]
    ForEachSeries --> PlotSerie[serie.plot(ax=ax, label=label, color=color, alpha=0.65)]
    PlotSerie --> FormatAxis[_format_ts_date_axis(serie, ax)]
    FormatAxis --> SetYLocator[ax.yaxis.set_major_locator(MaxNLocator(integer=True))]
    SetYLocator --> ForGap[for gap in gaps_: ax.fill_between(x=gap, y1=min_, y2=max_, color=color, alpha=0.25)]
    ForGap --> LoopEnd[continue next serie]
    LoopEnd --> AfterAllSeries[after looping all series]
    IsList -- No --> SinglePlot[series.plot(ax=ax)]
    SinglePlot --> FormatAxis2[_format_ts_date_axis(series, ax)]
    FormatAxis2 --> SetYLocator2[ax.yaxis.set_major_locator(MaxNLocator(integer=True))]
    SetYLocator2 --> ForEachGap[for gap in gaps: ax.fill_between(x=gap, y1=series.min(), y2=series.max(), color=colors[0], alpha=0.25)]
    ForEachGap --> AfterAllSeries
    AfterAllSeries --> DelegateSave[return plot_360_n0sc0pe(config)]
    DelegateSave --> End[End]

## Examples (concise usage lines; adapt objects as needed):
1) Single Series (inline PNG expected):
    - Prepare a pandas.Series `series` with a pandas.DatetimeIndex and a list `gaps` where each gap is a slice or index-like sequence of timestamps that fill_between accepts.
    - Example invocation:
      result = plot_timeseries_gap_analysis(config, series, gaps, figsize=(6,3))
    - `result` will be a base64 PNG data string when config.html.inline is True and image_format == "png".

2) Multiple Series comparison:
    - Provide `series` as a Python list of pandas.Series and `gaps` as a list where gaps[i] is the iterable of x-values marking gaps for series[i]. Ensure config.html.style._labels has at least as many entries as the number of series (or accept truncation).
    - Example invocation:
      result = plot_timeseries_gap_analysis(config, [series_A, series_B], [gaps_A, gaps_B])

3) Defensive usage patterns:
    - Validate color palette availability to avoid IndexError:
      colors = create_comparison_color_list(config)
      if not colors:
          raise ValueError("No colors available for plotting")
    - When saving to disk (config.html.inline is False), ensure config.html.assets_path is set to a valid directory; otherwise plot_360_n0sc0pe will raise ValueError.

Notes:
- Implementation mismatch: the function signature annotates a matplotlib.figure.Figure return type, but it actually returns a string from plot_360_n0sc0pe(config). Treat the return as the saved/encoded image representation (string).
- Be aware of zip() truncation if lists (series, gaps, colors, labels) differ in length; any trailing elements beyond the shortest are ignored.

## `src.ydata_profiling.visualisation.plot.plot_overview_timeseries` · *function*

*No documentation generated.*

## `src.ydata_profiling.visualisation.plot._plot_timeseries` · *function*

## Summary:
Creates a new Matplotlib figure and a single subplot, plots a single pandas Series or a list of Series onto that subplot (using configured colors/labels for comparisons), applies concise datetime x-axis formatting when appropriate, and returns the created Axes for further customization or embedding.

## Description:
This function coordinates figure/axis creation and the plotting of time series. It:
- Calls pyplot.figure(figsize=figsize) and fig.add_subplot(111) to create a new Figure and a single Axes (named `plot` in the implementation).
- If `series` is a list, obtains labels from config.html.style._labels and a list of colors from create_comparison_color_list(config), then iterates over zip(series, colors, labels) and for each element:
  - Calls serie.plot(color=color, label=label, alpha=0.75) to draw the series onto the current Axes (pandas returns the Axes used by the plotting call).
  - Calls _format_ts_date_axis(serie, ax) to apply concise date formatting to the x-axis when serie.index is a DatetimeIndex.
- If `series` is a single pandas.Series, plots it using the first configured primary color (config.html.style.primary_colors[0]) and then calls _format_ts_date_axis(series, ax).
- Returns the Axes object created by fig.add_subplot(111).

Why this is a separate helper:
- Encapsulates figure/axis creation and consistent date-axis formatting so callers only need to supply data and configuration.
- Centralizes color/label handling for comparison plots via create_comparison_color_list(config).
- Avoids duplicating plotting+formatting logic across the codebase.

## Args:
    config (Settings)
        - Type: Settings object (repository config) exposing nested attributes:
            * config.html.style.primary_colors: sequence of color strings (e.g., ["#rrggbb", ...]).
            * config.html.style._labels: sequence of labels (length used when generating comparison palettes).
        - Notes: Missing nested attributes will raise AttributeError at runtime when accessed.

    series (Union[list, pandas.Series])
        - Type: Either a pandas.Series or a list/iterable of pandas.Series-like objects.
        - Behavior:
            * Single-series branch: `series` is treated as a single pandas.Series and plotted with color config.html.style.primary_colors[0].
            * Multi-series branch: `series` is treated as a list. The function will call create_comparison_color_list(config) and zip(series, colors, labels) to iterate. Because zip truncates to the shortest iterable, any extra series beyond the number of colors or labels will be ignored.
        - Requirements: Each series (or list element) must implement .plot(...) and expose an .index attribute (Datetimelike index causes date-formatting to be applied).

    figsize (tuple, optional)
        - Type: tuple of two numeric values (width, height) in inches.
        - Default: (6, 4)
        - Notes: Values are forwarded to pyplot.figure(figsize=figsize). Non-numeric or malformed tuples will cause Matplotlib to raise TypeError/ValueError.

## Returns:
    matplotlib.axes.Axes
    - The Axes instance created by fig.add_subplot(111) and used for plotting. It contains the plotted artists (Line2D objects) and may have had its x-axis major locator and formatter modified by _format_ts_date_axis.
    - Important: The function's type annotation in source declares matplotlib.figure.Figure, but the actual returned object is the Axes instance. Callers should depend on an Axes return value.

## Raises:
    AttributeError
        - If config, config.html, or config.html.style are missing (accessing config.html.style._labels or config.html.style.primary_colors).
        - If an element of `series` lacks an .index attribute such that _format_ts_date_axis(series, ax) or series.plot accesses missing attributes.

    IndexError
        - If create_comparison_color_list(config) attempts to access colors[0] when primary_colors is empty; this originates from the color-list helper and will propagate.

    TypeError
        - If `series` is neither a list nor a pandas.Series and lacks a .plot method, calling .plot will raise AttributeError/TypeError.
        - If figsize is not a tuple of two numeric values, Matplotlib may raise TypeError.

    ValueError
        - Matplotlib may raise ValueError for invalid figsize values or invalid plotting arguments; such exceptions propagate.

Notes on provenance of exceptions:
- The function itself performs direct attribute access to config.html.style._labels and config.html.style.primary_colors (multi-series and single-series branches respectively) — missing attributes cause AttributeError directly on access.
- Color generation errors (IndexError, ValueError) can arise from create_comparison_color_list.
- Plotting errors come from pandas.Series.plot and Matplotlib internals.

## Constraints:
Preconditions:
    - config must expose html.style.primary_colors and html.style._labels when plotting a list of series.
    - Elements passed as series (single or list members) must support the .plot method and have an .index attribute.
    - If concise date formatting is desired, the series.index should be a pandas.DatetimeIndex (the formatting helper checks isinstance(series.index, pd.DatetimeIndex)).

Postconditions:
    - A new Figure and Axes have been created and registered with Matplotlib.
    - The returned Axes contains the plotted series (or contains no artists if an empty list was supplied).
    - If any plotted series had a DatetimeIndex, the returned Axes.xaxis has been updated with AutoDateLocator and ConciseDateFormatter via _format_ts_date_axis.

## Side Effects:
    - Creates a Matplotlib Figure and Axes (mutates Matplotlib global state by adding a new figure).
    - Draws onto the created Axes via pandas.Series.plot (this registers artists with the figure).
    - Mutates the returned Axes by applying date formatting when appropriate.
    - No file, network, or persistent external state modifications occur.

## Control Flow:
flowchart TD
    A[Start] --> B[fig = pyplot.figure(figsize=figsize)]
    B --> C[plot = fig.add_subplot(111)]
    C --> D{isinstance(series, list)?}
    D -- Yes --> E[labels = config.html.style._labels]
    E --> F[colors = create_comparison_color_list(config)]
    F --> G[for each (serie,color,label) in zip(series, colors, labels):]
    G --> G1[ax = serie.plot(color=color, label=label, alpha=0.75)]
    G1 --> G2[_format_ts_date_axis(serie, ax)]
    G2 --> H[after loop -> return plot (Axes)]
    D -- No --> I[ax = series.plot(color=config.html.style.primary_colors[0])]
    I --> J[_format_ts_date_axis(series, ax)]
    J --> H

## Examples:
1) Single-series plot with datetime index
    - Preconditions:
        * series is a pandas.Series with a pandas.DatetimeIndex
        * config.html.style.primary_colors is a non-empty sequence
    - Outcome:
        * New figure and Axes created, series plotted using the first primary color, x-axis formatted with concise date ticks, Axes returned.

2) Comparison plot with multiple series
    - Preconditions:
        * series is a list of pandas.Series
        * config.html.style._labels is a sequence at least as long as the number of desired plotted series (or create_comparison_color_list will generate colors matching len(labels))
    - Outcome:
        * For each triple from zip(series, colors, labels) a line is plotted with color and label; if there are more series than labels/colors, extra series are ignored due to zip truncation.
        * Returned Axes contains multiple Line2D artists and possibly modified x-axis formatting.

3) Edge case: empty list
    - If series == []:
        * The for-loop is not executed; no artists are added to the Axes.
        * The function still returns the newly created Axes (empty plot).

Usage guidance:
    - Validate config.html.style.primary_colors is non-empty before calling if you cannot tolerate IndexError from color generation.
    - If you require the Figure object, use returned_axes.figure to obtain it from the returned Axes.

## `src.ydata_profiling.visualisation.plot.mini_ts_plot` · *function*

## Summary:
Creates a compact thumbnail of one or more time series, applies compact tick styling and tight layout, then saves/encodes the resulting figure and returns an image reference string suitable for embedding in a report.

## Description:
mini_ts_plot delegates actual drawing to the shared helper _plot_timeseries(config, series, figsize=...) which creates a Matplotlib Figure and Axes, draws the provided series (single pandas.Series or list of Series) onto that Axes, and returns the Axes instance. mini_ts_plot assigns that returned Axes to the local variable `plot` and then:
- Rotates x-axis major tick labels by 45 degrees.
- Sets the Matplotlib y-tick global rc label size to 3 using the pyplot rc interface (plt.rc).
- Iterates the Axes' major ticks and sets each tick label font size to 6 when the function determines the provided series object has a pandas.DatetimeIndex, otherwise to 8.
- Calls plot_360_n0sc0pe(config) to save or encode the active Matplotlib figure; plot_360_n0sc0pe closes the figure and returns a string (inline base64/SVG or a saved-file suffix) that the report can embed or reference.

Known callers / usage context:
- Intended for report-generation stages that need a small embedded visualization (e.g., variable detail cards or compact overview charts). No concrete call-sites were present in the provided snapshot, but its role is to produce a ready-to-use image string for HTML reports.

Why this logic is a separate function:
- Encapsulates compact thumbnail styling consistently (tick rotation, reduced font sizes, tight layout).
- Reuses existing plotting logic (_plot_timeseries) and image-export logic (plot_360_n0sc0pe) so callers do not have to manage Matplotlib figure creation or file/inline saving details.

## Args:
    config (Settings)
        - Type: repository Settings object.
        - Required nested attributes (used by helpers):
            * config.plot.image_format (or config.plot.image_format.value if needed by plot_360_n0sc0pe)
            * config.plot.dpi (used when saving PNG)
            * config.html.inline (controls inline vs asset-file behavior)
            * If config.html.inline is False: config.html.assets_path must be non-None
        - Missing nested attributes will cause AttributeError when accessed by _plot_timeseries or plot_360_n0sc0pe.

    series (Union[list, pandas.Series])
        - Type: Either a single pandas.Series or a list/iterable of pandas.Series-like objects (each element must implement .plot(...) and generally will be a pandas.Series).
        - Important notes on behavior:
            * _plot_timeseries interprets a list by plotting each element in the list and returns the Axes used for plotting.
            * mini_ts_plot later evaluates isinstance(series.index, pandas.DatetimeIndex) to decide x-tick font sizes. If you pass a pandas.Series, that check detects a DatetimeIndex correctly. If you pass a plain Python list of Series, series.index resolves to the list.index method (a callable) — this will not be an instance of pandas.DatetimeIndex, so mini_ts_plot will use the non-datetime fontsize branch (8) rather than the datetime branch (6). Thus, passing a list prevents mini_ts_plot from detecting datetime x-axes for per-tick font-size reduction.
            * If you pass an object that truly lacks an .index attribute (e.g., a generator or an arbitrary object without .index), accessing series.index will raise an AttributeError.

    figsize (Tuple[float, float], optional)
        - Type: (width, height) in inches forwarded to _plot_timeseries → pyplot.figure(figsize=...).
        - Default: (3, 2.25)
        - Constraints: Non-numeric or improperly-sized tuples will cause Matplotlib to raise TypeError/ValueError.

## Returns:
    str
    - Meaning:
        * If config.html.inline is True:
            - For image_format == "svg": returns the raw SVG string of the saved figure.
            - For image_format == "png": returns a base64-encoded image string (data URI) produced by plot_360_n0sc0pe.
        * If config.html.inline is False:
            - Returns a relative asset-path suffix string where the image file was written; the caller can combine this with config.html.assets_path to form the full path or URL.
    - The returned string is produced by plot_360_n0sc0pe and follows its exact encoding/format semantics.

## Raises:
    AttributeError
        - If an object without an .index attribute is passed as series (e.g., some generators or custom objects), the isinstance(series.index, pandas.DatetimeIndex) access will raise AttributeError.
        - If config lacks required nested attributes used by _plot_timeseries or plot_360_n0sc0pe.

    ValueError
        - Propagated from plot_360_n0sc0pe when config.plot.image_format is not one of the supported formats ("png" or "svg").
        - Propagated from plot_360_n0sc0pe when config.html.inline is False but config.html.assets_path is None.

    TypeError / IndexError / Matplotlib-related exceptions
        - Errors raised by _plot_timeseries or Matplotlib/pandas plotting internals (invalid figsize, plotting parameters, or color-list generation errors) propagate up unchanged.

## Constraints:
Preconditions:
    - config must expose the plot and html settings used by the helpers (see Args).
    - series elements (or the series itself) should implement .plot(...) and typically be pandas.Series; otherwise plotting will raise at the pandas/Matplotlib layer.
    - For correct datetime-based per-tick font-size reduction, pass a pandas.Series (not a plain list) so series.index is a DatetimeIndex.

Postconditions:
    - The returned Axes instance created by _plot_timeseries has been adjusted:
        * x-axis tick labels rotated 45 degrees,
        * y-tick labelsize globally set to 3 via the pyplot rc interface,
        * per-tick label font sizes set to 6 (if series.index is a pandas.DatetimeIndex) or 8 (otherwise),
        * figure.tight_layout() applied to reduce clipping.
    - The active Matplotlib figure is saved/encoded and closed by plot_360_n0sc0pe; mini_ts_plot returns that image reference (string).

## Side Effects:
    - Alters Matplotlib global rc parameter for ytick labelsize (plt.rc("ytick", labelsize=3)).
    - Creates a Matplotlib Figure and Axes and draws artists on it (via _plot_timeseries which returns the Axes).
    - plot_360_n0sc0pe saves or encodes the active figure and calls plt.close(), so the figure is closed before the function returns.
    - If config.html.inline is False, an image file is written to disk by plot_360_n0sc0pe (filesystem I/O).

## Control Flow:
flowchart TD
    A[Call mini_ts_plot(config, series, figsize)] --> B[_plot_timeseries creates Figure & Axes and returns Axes assigned to `plot`]
    B --> C[plot.xaxis.set_tick_params(rotation=45)]
    C --> D[plt.rc("ytick", labelsize=3)]
    D --> E[for each tick in plot.xaxis.get_major_ticks()]
    E --> F{isinstance(series.index, pandas.DatetimeIndex)?}
    F -- Yes --> G[tick.label1.set_fontsize(6)]
    F -- No  --> H[tick.label1.set_fontsize(8)]
    G --> I[loop or exit]
    H --> I[loop or exit]
    I --> J[plot.figure.tight_layout()]
    J --> K[call plot_360_n0sc0pe(config) -> image string or asset path]
    K --> L[return image string]
    subgraph Errors
        M[series lacks .index attribute] --> N[AttributeError raised at isinstance(...) access]
        O[plot_360_n0sc0pe invalid format or missing assets_path] --> P[ValueError propagated]
        Q[_plot_timeseries/Matplotlib/pandas errors] --> R[TypeError/IndexError/... propagated]
    end

## Examples:
1) Standard single-series inline thumbnail (recommended)
    - Preconditions: my_series is a pandas.Series (optionally with a pandas.DatetimeIndex), config.html.inline = True, config.plot.image_format in {"png","svg"}.
    - Behavior: returns base64 PNG data URI (for PNG) or raw SVG markup (for SVG).
    - Usage pattern:
        try:
            image_ref = mini_ts_plot(config, my_series)
            # Insert image_ref into HTML (for PNG, it's a data URI; for SVG, it's raw SVG)
        except (ValueError, AttributeError) as exc:
            # ValueError: unsupported image format or missing assets_path when inline=False
            # AttributeError: series lacked an .index attribute

2) Multi-series plotting caveat
    - If you pass a plain list of pandas.Series (e.g., [s1, s2]), _plot_timeseries will plot both series and return the Axes, but mini_ts_plot's datetime detection check uses series.index — for a plain list this resolves to the list.index method, so the function will take the non-datetime branch (font size 8). To preserve datetime tick detection or to customize styling for multi-series plots, either:
        * Plot and customize manually:
            ax = _plot_timeseries(config, my_list_of_series, figsize=(3,2.25))
            # customize ax as needed
            image_ref = plot_360_n0sc0pe(config)
        * Or pass a single representative pandas.Series to mini_ts_plot if you want to use the datetime-specific small tick font behavior.

Notes:
    - mini_ts_plot is optimized for compact thumbnails; for larger or differently styled charts, call _plot_timeseries to obtain the Axes and perform custom styling before saving with plot_360_n0sc0pe.

## `src.ydata_profiling.visualisation.plot._get_ts_lag` · *function*

## Summary:
Return the appropriate maximum lag to use for time-series autocorrelation (ACF/PACF) calculations by taking the smaller of the configured lag and a series-length-derived bound.

## Description:
Known callers within this codebase:
- No direct callers were found in the available repository metadata for this function. In this codebase, this helper is typically used by time-series plotting/analysis routines that compute ACF/PACF before plotting, where the configured maximum lag must be constrained by the length of the available series.

Why this logic is a separate function:
- Encapsulates the policy for choosing an ACF/PACF lag bound (configuration value vs. data-dependent maximum). Keeping this logic in one place prevents duplicated calculations across multiple plotting or analysis functions and centralizes the behavior for easier testing and modification.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Description: A configuration object exposing configuration values at config.vars.timeseries.pacf_acf_lag.
        - Requirements: config.vars.timeseries.pacf_acf_lag should be an integer-like non-negative value representing the preferred maximum lag requested by configuration.
    series (pandas.Series):
        - Type: pandas.Series
        - Description: The time-series data for which ACF/PACF lags are being computed.
        - Requirements: The function uses len(series) to compute a data-dependent maximum lag. The series may be any pandas Series (numeric or otherwise), but its length must be an integer >= 0.

Interdependencies:
- The returned value depends on both config.vars.timeseries.pacf_acf_lag and len(series). If config's configured lag is larger than the data-dependent bound, the data-dependent bound is returned.

## Returns:
    int:
        - The selected maximum lag to use for ACF/PACF computations.
        - Behavior: returns the minimum of:
            * config.vars.timeseries.pacf_acf_lag (as provided in the Settings object)
            * floor(len(series) / 2) - 1 (data-dependent bound)
        - Edge cases:
            * For very short series, the data-dependent bound may be negative (for example, len(series) == 1 yields -1). The function returns that negative integer in such cases; callers should validate series length if a non-negative lag is required.

## Raises:
    - The function does not explicitly raise exceptions.
    - Implicit errors may occur if:
        * config does not have the attribute path config.vars.timeseries.pacf_acf_lag (AttributeError).
        * config.vars.timeseries.pacf_acf_lag is not comparable with an integer (TypeError) when computing the minimum.
        * len(series) is not defined on the provided series-like object (TypeError).

## Constraints:
Preconditions:
    - config must expose config.vars.timeseries.pacf_acf_lag.
    - series must be a sequence-like object with a defined length (len(series) must be valid).
    - To guarantee a non-negative return, callers should ensure len(series) >= 2 (len(series) == 2 returns 0).

Postconditions:
    - Returned value is less than or equal to the configured lag (config.vars.timeseries.pacf_acf_lag).
    - Returned value is less than or equal to floor(len(series) / 2) - 1.
    - The return value is an integer (possibly negative if the series is very short).

## Side Effects:
    - No I/O is performed.
    - No global state is mutated.
    - No external services are called.

## Control Flow:
flowchart TD
    A[Start] --> B[Read config.vars.timeseries.pacf_acf_lag as lag]
    B --> C[Compute max_lag_size = (len(series) // 2) - 1]
    C --> D{Compare lag and max_lag_size}
    D -->|lag <= max_lag_size| E[Return lag]
    D -->|lag > max_lag_size| F[Return max_lag_size]
    E --> G[End]
    F --> G[End]

## Examples:
1) Typical usage (mocking minimal Settings structure)
    from pandas import Series

    class _MockTimeseriesConfig:
        def __init__(self, pacf_acf_lag: int):
            self.pacf_acf_lag = pacf_acf_lag

    class _MockVars:
        def __init__(self, pacf_acf_lag: int):
            self.timeseries = _MockTimeseriesConfig(pacf_acf_lag)

    class _MockSettings:
        def __init__(self, pacf_acf_lag: int):
            self.vars = _MockVars(pacf_acf_lag)

    # Example series
    s = Series([1, 2, 3, 4, 5, 6])  # len = 6 -> floor(6/2)-1 = 3 - 1? (6//2)-1 = 3-1 = 2
    cfg = _MockSettings(pacf_acf_lag=10)
    # _get_ts_lag(cfg, s) will return min(10, 2) == 2

2) Handling short series
    s_short = Series([1])  # len = 1 -> (1//2)-1 = 0-1 = -1
    cfg = _MockSettings(pacf_acf_lag=5)
    # _get_ts_lag(cfg, s_short) will return min(5, -1) == -1
    # Caller should check for negative values if a non-negative lag is required:
    lag = _get_ts_lag(cfg, s_short)
    if lag < 0:
        raise ValueError("Series too short to compute ACF/PACF with a non-negative lag")

Notes:
- Callers that require non-negative lag values should validate and handle negative return values (e.g., by ensuring the series is sufficiently long or by applying a max(lag, 0) clamp).
- The function intentionally leaves the decision about negative lag handling to the caller to preserve transparency of the data-dependent bound.

## `src.ydata_profiling.visualisation.plot._plot_acf_pacf` · *function*

## Summary:
Generate side-by-side ACF and PACF plots for a pandas Series using the report theme color, export the figure (inline or to disk) via the project's image helper, and return the resulting image payload string.

## Description:
This helper produces a two-panel diagnostic figure (ACF on the left, PACF on the right) for a time-series variable and exports the figure using the project's image-export helper.

Relationship to other helpers:
- Calls _get_ts_lag(config, series) to determine the maximum lag to request from statsmodels. _get_ts_lag selects the minimum between the configured lag (config.vars.timeseries.pacf_acf_lag) and a data-dependent bound computed from the series length (floor(len(series)/2) - 1).
- Calls plot_360_n0sc0pe(config) to save or encode the created matplotlib figure and to close the plotting context.

Typical callers / usage context:
- Time-series variable profiling and visualization pipelines that generate per-variable diagnostic plots for inclusion in the profiling report. There is no enforced registry of callers in the repository; higher-level report code will call this function when an ACF/PACF visualization is needed.

Why this logic is extracted:
- Centralizes plotting, theming (color selection and facecolor adjustments), and final image export in one place so that higher-level reporting code only needs to request the image payload rather than manage matplotlib figure lifecycle, theme consistency, and saving/encoding details.

## Args:
    config (ydata_profiling.config.Settings):
        - The global settings object used across profiling/reporting.
        - Fields relied upon (accessed directly or indirectly):
            * config.html.style.primary_colors: indexable; index 0 provides the primary color used for plot elements.
            * config.vars.timeseries.pacf_acf_lag: used by _get_ts_lag to bound the requested lag.
            * config.plot.image_format, config.html.inline, config.plot.dpi, config.html.assets_path, config.html.assets_prefix: used transitively by plot_360_n0sc0pe.
        - Failure modes:
            * Missing or malformed attributes (e.g., html.style.primary_colors absent or empty) will raise AttributeError/IndexError when accessed.
    series (pandas.Series):
        - The time-series data to analyze. The function uses series.dropna() before plotting, so NaN values are removed.
        - len(series) is used indirectly by _get_ts_lag to compute a data-dependent lag bound.
        - If the series contains non-numeric types or otherwise incompatible values, statsmodels' plot_acf/plot_pacf may raise errors.
    figsize (tuple[int, int], optional) = (15, 5):
        - Matplotlib figure size specified as (width, height) in inches.

Interdependencies and notes:
    - Maximum lag: computed by calling _get_ts_lag(config, series). That helper returns min(config.vars.timeseries.pacf_acf_lag, floor(len(series)/2) - 1). If that value is negative (possible for very short series), it is passed through to statsmodels functions; callers should guard against short series if a non-negative lag is required.
    - Plot styling: uses the first color from config.html.style.primary_colors for lines and vertical confidence vlines. It also sets facecolor on any PolyCollection objects found in axis.collections to match the theme.

## Returns:
    str:
        - The string returned by plot_360_n0sc0pe(config).
        - Possible returned payloads (determined by plot_360_n0sc0pe behavior and configuration):
            * When config.html.inline is True and image_format is "svg": an SVG text string.
            * When config.html.inline is True and image_format is "png": a base64-encoded PNG payload (the exact wrapper/encoding format is determined by the project's base64 helper used inside plot_360_n0sc0pe).
            * When config.html.inline is False: a file path suffix (string) pointing to the saved image under config.html.assets_path, typically formatted as "{assets_prefix}/images/{uuid}.{ext}".
        - If plot_360_n0sc0pe raises, this function propagates that exception and does not return.

## Raises:
    - AttributeError / IndexError:
        * If config.html.style.primary_colors is missing or empty (accessing index 0).
    - Exceptions from _get_ts_lag:
        * If config.vars.timeseries.pacf_acf_lag is missing or invalid, _get_ts_lag may raise AttributeError or TypeError; these propagate.
    - Exceptions from statsmodels plotting (plot_acf / plot_pacf):
        * If series.dropna() is not suitable for ACF/PACF computation or the provided lags value is unacceptable, statsmodels functions may raise ValueError/TypeError (propagated).
    - Exceptions from plot_360_n0sc0pe:
        * ValueError('Can only 360 n0sc0pe "png" or "svg" format.') for unsupported image formats.
        * ValueError("config.html.assets_path may not be none") if html.inline is False but assets_path is None.
    - This function does not catch these exceptions; callers must handle or allow propagation.

## Constraints:
Preconditions:
    - config must provide the fields referenced above.
    - series must be a pandas.Series (or compatible) and support .dropna() and len().
    - To ensure non-negative lags for statsmodels, ensure len(series) >= 2 (len == 2 yields lag 0 from _get_ts_lag).
Postconditions:
    - A matplotlib figure with two axes (ACF and PACF) has been created and saved/encoded by plot_360_n0sc0pe, and plt.close() has been called by that helper.
    - Any PolyCollection objects in the two axes have had their facecolor set to the configured primary color.
    - The returned string is the output provided by the project's image exporter.

## Side Effects:
    - Creates matplotlib figure and axes via plt.subplots.
    - Mutates matplotlib artists (sets facecolor on PolyCollection objects).
    - Saves or encodes the figure via plot_360_n0sc0pe which may:
        * Write an image file to disk (when html.inline is False), or
        * Produce an in-memory SVG string or a base64-encoded PNG payload (when html.inline is True).
    - No network calls or external service interactions beyond file I/O when saving assets.

## Control Flow:
flowchart TD
    Start --> ReadColor[Get color = config.html.style.primary_colors[0]]
    ReadColor --> GetLag[lag = _get_ts_lag(config, series) (min(config var, floor(len/2)-1))]
    GetLag --> CreateFig[plt.subplots(1, 2, figsize=figsize)]
    CreateFig --> PlotACF[plot_acf(series.dropna(), lags=lag, ax=axes[0], title="ACF", fft=True, color=color)]
    PlotACF --> PlotPACF[plot_pacf(series.dropna(), lags=lag, ax=axes[1], title="PACF", method="ywm", color=color)]
    PlotPACF --> IterateAxes[For each axis in axes: iterate axis.collections]
    IterateAxes --> IsPoly{item is PolyCollection?}
    IsPoly -->|yes| SetFace[item.set_facecolor(color)]
    IsPoly -->|no| Skip
    SetFace --> Skip
    Skip --> Export[Call plot_360_n0sc0pe(config) to save/encode and close figure]
    Export --> ReturnResult[Return export string]
    ReturnResult --> End

## Examples:
1) Inline SVG output (typical in notebook/report generation):
    from pandas import Series
    # Minimal Settings-like mock for demonstration
    class _MockStyle: 
        def __init__(self, colors): self.primary_colors = colors
    class _MockHtml:
        def __init__(self):
            self.style = _MockStyle(["#336699"])
            self.inline = True
            self.assets_path = None
            self.assets_prefix = "assets"
    class _MockPlot:
        def __init__(self): 
            self.image_format = type("F", (), {"value": "svg"})()
            self.dpi = 96
    class _MockVarsTimeseries:
        def __init__(self, lag): self.pacf_acf_lag = lag
    class _MockVars:
        def __init__(self, lag): self.timeseries = _MockVarsTimeseries(lag)
    class _MockSettings:
        def __init__(self):
            self.html = _MockHtml()
            self.plot = _MockPlot()
            self.vars = _MockVars(lag=10)

    cfg = _MockSettings()
    s = Series([1.0, 2.2, 3.1, 4.6, 5.0, None, 6.3])
    # Call the helper
    image_str = _plot_acf_pacf(cfg, s, figsize=(12, 4))
    # image_str will be an SVG string (when inline & svg)

2) Guarding against short series:
    s_short = Series([1.0])  # len == 1 -> _get_ts_lag may return negative
    lag = _get_ts_lag(cfg, s_short)
    if lag < 0:
        # Skip plotting or handle as a special case
        raise ValueError("Series too short to produce ACF/PACF plots")
    image_payload = _plot_acf_pacf(cfg, s_short)

## `src.ydata_profiling.visualisation.plot._plot_acf_pacf_comparison` · *function*

*No documentation generated.*

## `src.ydata_profiling.visualisation.plot.plot_acf_pacf` · *function*

## Summary:
Dispatches to the appropriate ACF/PACF plotting helper: creates a single-variable ACF/PACF image for a pandas Series, or a comparison ACF/PACF image when given a list of series, and returns the image payload string produced by the underlying exporter.

## Description:
This function is a thin dispatcher that chooses between two plotting helpers based on the runtime type of the series argument:
- If series is a list, it calls the multi-series comparison helper _plot_acf_pacf_comparison(config, series, figsize) and returns that helper's result.
- Otherwise (commonly a pandas.Series), it calls the single-series plotting helper _plot_acf_pacf(config, series, figsize) and returns that helper's result.

Known callers and typical context:
- Time-series profiling and visualization pipelines that generate per-variable diagnostic plots for inclusion in profiling reports call this function when they need ACF/PACF visualizations for a variable.
- It is typically invoked during the per-variable visualization stage of a profiling report generation pipeline. The pipeline passes the global Settings object and the target data (a Series or a list of Series) and expects an encoded image payload or a saved image path in return.

Why this logic is extracted into its own function:
- Encapsulates the dispatch decision (single vs. comparison mode) so higher-level code does not need to handle the branching.
- Keeps callers simple: callers ask for an ACF/PACF image and receive the resulting payload string without managing matplotlib lifecycles, plotting details, or exporter behavior.
- Enforces a clear responsibility boundary: selecting which helper to run based on input shape and forwarding the configured figure size.

## Args:
    config (ydata_profiling.config.Settings):
        - Global settings object used across profiling/reporting.
        - Required sub-fields are accessed by the delegated helpers (see _plot_acf_pacf and _plot_acf_pacf_comparison):
            * config.html.style.primary_colors (indexable; [0] is used for theming in single-series helper)
            * config.vars.timeseries.pacf_acf_lag (used to bound requested lag)
            * config.plot.image_format, config.html.inline, config.plot.dpi, config.html.assets_path, config.html.assets_prefix (used by the image exporter)
        - Missing or malformed settings fields will cause the underlying helper to raise (AttributeError, IndexError, or helper-specific exceptions).
    series (Union[list, pandas.Series]):
        - If a pandas.Series (or compatible object), the function forwards it to the single-series helper; that helper will drop NA values before plotting.
        - If a list, the function forwards the list to the comparison helper; each element in the list is expected to be an individual Series-like object suitable for ACF/PACF plotting.
        - Note: Only an isinstance(series, list) test is performed; other sequence types (numpy arrays, tuples) are not treated as comparison-mode lists unless they are list instances.
    figsize (tuple[int, int], optional) = (15, 5):
        - Figure size in inches forwarded to the chosen helper.
        - Both helpers receive this value and use it when creating matplotlib figures.

Interdependencies and parameter notes:
    - When series is a list, ensure its elements are the expected Series-like objects for the comparison helper; this dispatcher does not validate element types.
    - Behavior and return value semantics are determined by the delegated helper. For single-series behavior and constraints, see the component documentation of _plot_acf_pacf.

## Returns:
    str:
        - The string returned by the selected helper (_plot_acf_pacf or _plot_acf_pacf_comparison).
        - Typical return values (dependent on configuration and exporter implementation):
            * Inline SVG text (e.g., when config.html.inline is True and image format is "svg")
            * Base64-encoded PNG payload (when inline True and image format is "png")
            * File path suffix pointing to a saved image under config.html.assets_path (when inline False)
        - If the underlying helper raises an exception, this dispatcher will propagate that exception and will not return a value.

## Raises:
    - Any exception raised by _plot_acf_pacf or _plot_acf_pacf_comparison:
        * AttributeError / IndexError: if required settings are missing or malformed (e.g., primary_colors absent).
        * ValueError / TypeError: from statsmodels plotting functions if the series content or lag argument is invalid.
        * ValueError from the image exporter for unsupported image formats or missing assets_path when required.
        * Any other exceptions propagated from the delegated helpers.
    - The dispatcher itself performs only a type check (isinstance(series, list)); it does not raise for unexpected non-list non-Series types beyond whatever the helper raises when called.

## Constraints:
Preconditions:
    - config must be a valid Settings-like object with the fields expected by the delegated helper.
    - For single-series mode, series should be a pandas.Series (or compatible) supporting dropna() and len().
    - For comparison mode, series must be a Python list whose elements are Series-like objects accepted by the comparison helper.
Postconditions:
    - The selected helper will have executed and, if successful, the returned string represents the generated ACF/PACF image (inline payload or saved file path).
    - No matplotlib figure handles remain open if the delegated helper follows the expected contract of closing the figure (delegated helpers are responsible for closing).

## Side Effects:
    - None directly performed by this dispatcher beyond calling the delegated helper.
    - The delegated helpers create matplotlib figures and mutate matplotlib artists; they may save files to disk or produce in-memory image payloads via the project's exporter.
    - No network calls are made by this dispatcher; file I/O or in-memory encoding may occur in the helpers.

## Control Flow:
flowchart TD
    Start --> IsList{isinstance(series, list)?}
    IsList -->|yes| CallCompare[_plot_acf_pacf_comparison(config, series, figsize)]
    CallCompare --> ReturnCompare[return string from comparison helper]
    IsList -->|no| CallSingle[_plot_acf_pacf(config, series, figsize)]
    CallSingle --> ReturnSingle[return string from single-series helper]
    ReturnCompare --> End
    ReturnSingle --> End

## Examples:
1) Single-series ACF/PACF (typical usage):
    - Call the function with a Settings object and a pandas.Series containing the time-series data.
    - The function dispatches to the single-series helper and returns an image payload string (SVG text, base64 PNG, or saved file path depending on config).

2) Comparison across multiple series:
    - Pass a Python list of Series-like objects as the series parameter.
    - The function dispatches to the comparison helper and returns the corresponding comparison-image payload string.

3) Error handling guidance:
    - Validate configuration fields required by the plotting helpers before calling.
    - For series that may be too short, pre-check the series length and skip calling this function when a negative lag would result (the single-series helper computes lag internally; short series can lead to statsmodels errors). Handle exceptions propagated from the called helper to provide user-friendly messages or fallbacks.

## `src.ydata_profiling.visualisation.plot._prepare_heatmap_data` · *function*

## Summary:
Prepare a rectangular count table suitable for heatmap plotting by binning a time-like (or ordered) "sortby" column and counting occurrences of an entity per bin; returns a DataFrame with one row per entity and one column per bin.

## Description:
This helper transforms a long-form DataFrame into an entities-by-bin frequency table:
- It bins values from a chosen "sortby" key into a fixed number of ordered bins (at most 50), counts how many rows for each entity fall into each bin, and returns the result as a DataFrame indexed by entity with integer bin labels as columns.
- Typical usage: called before drawing a heatmap to visualize how occurrences of entities distribute across an ordered axis (time or another sortable field). No explicit callers were discovered in the scanned code; it is intended to be used by visualization routines that render entity heatmaps.
- Responsibility boundary: only prepares and returns the aggregated frequency data. It does not plot, format colors, or perform higher-level selection logic beyond limiting returned entities by selection or truncation to max_entities.

## Args:
    dataframe (pandas.DataFrame):
        Source table containing at least the entity column and the sortby column (if provided).
    entity_column (str):
        Name of the column in dataframe that identifies the categorical entity (one entity value per row).
    sortby (Optional[Union[str, list]], default=None):
        If None, the function will use the DataFrame index (via reset_index) as the ordered key and will label that index column as "_index".
        If a string is provided it is treated as a single-column key; if a list is provided the first element is used as the sort key.
        The chosen sort key must be a datetime-like or otherwise sortable; if its dtype is object the function will attempt to convert it to datetime.
    max_entities (int, default=5):
        When selected_entities is not provided, the returned DataFrame is truncated to the first `max_entities` entities (based on the order present after grouping/pivoting).
        Must be non-negative; a value of 0 will return an empty DataFrame with the expected columns.
    selected_entities (Optional[List[str]], default=None):
        If provided, this list of entity identifiers (strings) explicitly selects which entities to return. When this argument is given, max_entities is ignored.
        The order of entities in the returned DataFrame follows the provided list order.

## Returns:
    pandas.DataFrame:
        A DataFrame of shape (n_entities_returned, n_bins) where:
        - Index: entity identifiers (strings).
        - Columns: integer bin labels from 0 to nbins-1 (nbins is at most 50 and at most the number of unique sortby values).
        - Each cell contains the integer count of rows for that entity falling into the corresponding bin.
        Possible return shapes:
        - If selected_entities is provided: rows correspond to selected_entities in the provided order.
        - Otherwise: rows are the first max_entities entities (order determined by pivoting/grouping), and columns are bin indices.
        Edge-case returns:
        - If dataframe contains no rows or nbins evaluates to 0, downstream pandas functions (pd.cut, pivot_table) will raise exceptions; this function does not return a special empty sentinel.

## Raises:
    ValueError:
        Raised if the sortby key column has dtype object and pandas.to_datetime fails to parse it. The error message contains the offending column name and dtype, e.g.:
            "column <sortbykey> dtype <dtype> is not supported."
    KeyError, TypeError, ValueError (propagated from pandas):
        Other pandas-level errors can propagate, for example:
        - KeyError if entity_column or provided sortby key is missing from dataframe.
        - ValueError from pd.cut if bins <= 0 or invalid.
        These are not explicitly caught inside the function.

## Constraints:
    Preconditions:
        - dataframe must contain the column named by entity_column.
        - If sortby is provided, dataframe must contain the specified column(s); the primary sort key is the first element when a list is provided.
        - The sortby column must be convertible to datetime when its dtype is object, or already be a datetime-like/sortable dtype.
        - There must be at least one unique non-null value in the sortby key; otherwise nbins may become 0 and pd.cut will raise.
    Postconditions:
        - The returned DataFrame index contains entity identifiers (subset limited by selected_entities or by max_entities).
        - Columns are integer bin labels starting at 0 up to nbins-1, representing contiguous bins over the sorted key domain.
        - The aggregated counts in the DataFrame represent non-negative integer frequencies.

## Side Effects:
    - No I/O (no file, network, or stdout written).
    - No mutation of the original dataframe argument: a copy of relevant columns is taken before adding the temporary "__bins" column.
    - No external state or global variables are modified.

## Control Flow:
flowchart TD
    A[Start] --> B{sortby is None?}
    B -- Yes --> C[Create df = dataframe[entity_column].copy().reset_index(); set sortbykey = "_index"]
    B -- No --> D{sortby is str?}
    D -- Yes --> E[wrap sortby into list]
    D -- No --> F[use sortby list as-is]
    E --> G[cols = [entity_column, *sortby]; df = dataframe[cols].copy(); sortbykey = sortby[0]]
    F --> G
    C --> H{df[sortbykey].dtype == "O"?}
    G --> H
    H -- Yes --> I[try convert df[sortbykey] = pd.to_datetime(...)]
    I -- fail --> J[raise ValueError("column ... dtype ... is not supported.")]
    I -- success --> K[continue]
    H -- No --> K
    K --> L[nbins = min(50, df[sortbykey].nunique())]
    L --> M[df["__bins"] = pd.cut(..., bins=nbins, labels=range(nbins))]
    M --> N[df = df.groupby([entity_column,"__bins"])[sortbykey].count()]
    N --> O[df = df.reset_index().pivot_table(entity_column,"__bins",sortbykey).T]
    O --> P{selected_entities provided?}
    P -- Yes --> Q[df = df[selected_entities].T (rows = selected_entities)]
    P -- No --> R[df = df.T[:max_entities] (rows = first max_entities entities)]
    Q --> S[Return df]
    R --> S

## Examples:
Example (descriptive, end-to-end):
- Suppose dataframe has columns "user_id" and "event_time" with many timestamped rows per user.
- Call with sortby="event_time" and max_entities=3:
    The function will bin the event_time range into up to 50 bins, count events per user per bin, and return a DataFrame with up to 3 rows (one per user) and columns 0..(nbins-1) containing counts.
- If you want a specific set of users, pass selected_entities=["user_a","user_b"]; the result will contain exactly those rows in that order (or raise KeyError if some names are absent).

Notes:
- This function is primarily a data-preparation utility for visualizations; if you need different binning semantics (e.g., quantile-based bins), apply separate preprocessing before calling.
- Be careful when providing sortby columns that contain timezone-aware datetimes or mixed types; pandas.to_datetime will be used when dtype is object and may infer timezone-naive datetimes.

## `src.ydata_profiling.visualisation.plot._create_timeseries_heatmap` · *function*

## Summary:
Creates a Matplotlib Axes with a timeseries-style heatmap rendered from a 2-D pandas DataFrame, mapping numeric cell magnitude to a white→color gradient and returning the configured Axes.

## Description:
This helper function performs the following steps:
- Creates a new Figure and Axes via plt.subplots with the supplied figsize.
- Constructs a LinearSegmentedColormap using matplotlib.colors.LinearSegmentedColormap.from_list("report", ["white", color], N=64).
- Renders the DataFrame with ax.pcolormesh(df, edgecolors=ax.get_facecolor(), linewidth=0.25, cmap=cmap) and assigns the returned artist to the local variable pc.
- Sets the color limits with pc.set_clim(0, np.nanmax(df)).
- Configures y-tick positions to centered row positions and uses df.index as y-tick labels.
- Removes x-ticks, sets the x-axis label to "Time", and inverts the y-axis so the first DataFrame row appears at the top.

Known callers:
- No direct callers were found in the provided snapshot. Typically invoked by higher-level visualization or profiling routines that need a compact timeseries heatmap of binned numeric data.

Why this logic is extracted:
- Encapsulates Matplotlib-specific plotting and styling (figure/axes creation, colormap creation, pcolormesh arguments, tick placement and axis inversion). This keeps higher-level code clean and provides a single place to control the visual appearance of timeseries heatmaps.

## Args:
    df (pd.DataFrame)
        2-D input data to plot. Rows correspond to series/categories and columns to time bins.
        - The function expects a pandas.DataFrame instance; df.index is used for y-axis labels.
        - Cell values should be numeric or convertible to numeric; non-numeric values may cause underlying numpy/matplotlib calls to raise.
        - Zero rows or zero columns are possible inputs but may trigger errors downstream (see Raises).
    figsize (Tuple[int, int], optional)
        Figure size (width, height) in inches passed to plt.subplots. Default: (12, 5).
        - Typed as Tuple[int, int] per the function signature.
    color (str, optional)
        Color string used as the high end of the white→color colormap. Default: "#337ab7".
        - Supplied directly to LinearSegmentedColormap.from_list as the second color entry.

Parameter interdependencies:
- The color scaling upper bound is computed via np.nanmax(df); if df is empty or all-NaN, the behavior of np.nanmax and subsequent pc.set_clim(0, vmax) determines the result (see Raises and Notes).

## Returns:
    plt.Axes
    - The Matplotlib Axes instance created by plt.subplots and populated with the heatmap.
    - The pcolormesh artist added to the Axes is assigned to the local variable pc; callers can access it via ax.collections (e.g., the most recently added collection) if they need to manipulate color limits or create a colorbar.

Guaranteed Axes configuration on return:
- Y-ticks are set to [x + 0.5 for x in range(len(df))].
- Y-tick labels are set to df.index.
- X-ticks are cleared (ax.set_xticks([])).
- X-axis labeled "Time".
- Y-axis inverted (ax.invert_yaxis()).

## Raises:
    ValueError
        - If df has zero elements (e.g., zero rows or zero columns), the call to np.nanmax(df) will raise ValueError (originates from numpy: "zero-size array to reduction operation maximum").
    TypeError or ValueError
        - If df contains data that cannot be coerced to numeric arrays for plotting, underlying matplotlib/numpy calls (pcolormesh or array conversions) may raise TypeError or ValueError; this function propagates those exceptions.

Notes on all-NaN input:
- If df is non-empty but all values are NaN, np.nanmax(df) will typically return NaN (and may emit a RuntimeWarning). The code calls pc.set_clim(0, NaN) which Matplotlib accepts but yields undefined/meaningless color scaling (no exception from this function).

## Constraints:
Preconditions:
- df must be a pandas.DataFrame.
- figsize must be a Tuple[int, int] (per signature) with positive integers.
- color must be a string acceptable to Matplotlib color parsing.

Postconditions:
- A new Figure and Axes are created and populated with a pcolormesh representing df.
- Axis ticks/labels and orientation are configured as described above.

## Side Effects:
- Creates a Matplotlib Figure and Axes (plt.subplots) and adds artists to the Axes (pcolormesh). This mutates Matplotlib's global figure/axes state and may display figures depending on the backend.
- No file or network I/O.
- The input DataFrame is not modified.

## Control Flow:
flowchart TD
    Start --> Subplots[Call plt.subplots(figsize=figsize)]
    Subplots --> MakeCmap[Call matplotlib.colors.LinearSegmentedColormap.from_list("report", ["white", color], N=64)]
    MakeCmap --> Pcolormesh[Call ax.pcolormesh(df, edgecolors=ax.get_facecolor(), linewidth=0.25, cmap=cmap) -> pc]
    Pcolormesh --> ComputeVmax[Call np.nanmax(df)]
    ComputeVmax -->|df empty| RaiseValErr[ValueError raised by numpy]
    ComputeVmax -->|vmax computed| SetClim[Call pc.set_clim(0, vmax)]
    SetClim --> SetYticks[ax.set_yticks([x + 0.5 for x in range(len(df))])]
    SetYticks --> SetYlabels[ax.set_yticklabels(df.index)]
    SetYlabels --> ClearXTicks[ax.set_xticks([])]
    ClearXTicks --> LabelX[ax.set_xlabel("Time")]
    LabelX --> InvertY[ax.invert_yaxis()]
    InvertY --> ReturnAx[Return ax]

## Examples:
Basic usage:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    # Create a 5×24 DataFrame of numeric values
    df = pd.DataFrame(np.random.rand(5, 24),
                      index=["s1", "s2", "s3", "s4", "s5"],
                      columns=range(24))

    ax = _create_timeseries_heatmap(df, figsize=(12, 5), color="#337ab7")
    plt.show()

Accessing the pcolormesh artist and adding a colorbar:
    import matplotlib.pyplot as plt

    ax = _create_timeseries_heatmap(df)
    mesh = ax.collections[-1]  # the pcolormesh artist added by the function
    fig = ax.get_figure()
    fig.colorbar(mesh, ax=ax)

Defensive handling for empty or all-NaN DataFrame:
    if df.empty or df.shape[1] == 0:
        # avoid calling the function because np.nanmax will raise ValueError
        handle_empty()
    elif df.isna().all().all():
        # decide on imputation or skip plotting to avoid meaningless color scaling
        handle_all_nan()
    else:
        ax = _create_timeseries_heatmap(df)
        plt.show()

## `src.ydata_profiling.visualisation.plot.timeseries_heatmap` · *function*

## Summary:
Render a per-entity timeseries heatmap by binning an ordered key (typically a time column) into up to 50 bins, counting occurrences per entity per bin, and plotting those counts on a Matplotlib Axes; returns the configured Axes with aspect ratio set to 1.

## Description:
This function coordinates two responsibilities:
1. Preparing the rectangular, entities-by-bins count table by delegating to _prepare_heatmap_data. That helper bins a chosen "sortby" key and returns a DataFrame where each row is an entity and each column is an integer bin (0..nbins-1) containing counts.
2. Rendering that table as a timeseries-style heatmap by delegating to _create_timeseries_heatmap. That helper creates the Figure and Axes, draws a white→color pcolormesh, configures tick placement and axis orientation, and returns the Axes.

Typical callers / usage context:
- Visualization or profiling routines that need a compact visual summary of how occurrences of categorical entities are distributed over an ordered axis (most commonly timestamped events per entity). No direct callers were detected in the scanned code snapshot; it is intended to be invoked by higher-level reporting or interactive visualization code.

Why this logic is a separate function:
- Keeps concerns separated: data-aggregation logic (_prepare_heatmap_data) and Matplotlib rendering (_create_timeseries_heatmap) are specialized and reusable. This wrapper composes them and enforces a consistent aspect ratio (ax.set_aspect(1)) for the resulting Axes so heatmap cells appear square.

## Args:
    dataframe (pandas.DataFrame):
        Source table containing at least the entity column and, if sortby is provided, the sort key column.
        - Must be a pandas.DataFrame instance.
    entity_column (str):
        Column name identifying the categorical entity (one entity value per row).
        - This column must exist in `dataframe`; otherwise a KeyError will be raised by the preparation step.
    sortby (Optional[Union[str, list]], default=None):
        Ordered key used to bin rows. Behavior:
        - None: the function will use the DataFrame index (after reset_index()) and label that generated column as "_index".
        - str: treated as a single-column key.
        - list: the first element is used as the primary sort key.
        Notes:
        - If the chosen sortby key has dtype object, the preparer will attempt pandas.to_datetime conversion; failure produces ValueError.
    max_entities (int, default=5):
        When selected_entities is not provided, the prepared DataFrame is truncated to the first `max_entities` entities (order determined by grouping/pivoting in the preparer).
        - Must be non-negative. A value of 0 results in an empty DataFrame of the correct column shape (may cause downstream plotting errors).
        - Ignored if selected_entities is provided.
    selected_entities (Optional[List[str]], default=None):
        If provided, this explicit ordered list selects which entities to return/plot. When present, `max_entities` is ignored.
        - If any name in the list is missing, a KeyError will propagate from the preparer or pandas indexing.
    figsize (Tuple[int, int], default=(12, 5)):
        Figure size in inches forwarded to the plotting helper when creating the Figure and Axes.
        - Expected to be a (width, height) tuple of positive ints.
    color (str, default="#337ab7"):
        Color string used as the high end of the white→color colormap produced by the plotting helper.
        - Passed unchanged to the colormap creation in the plotting helper. Must be acceptable to Matplotlib color parsing.

Interdependencies:
- If selected_entities is provided, max_entities is ignored and the output entity order follows selected_entities.
- The validity of `sortby` influences whether _prepare_heatmap_data will convert types; certain `sortby` inputs can raise ValueError during conversion.

## Returns:
    plt.Axes
    - The Matplotlib Axes instance created and returned by _create_timeseries_heatmap, after this wrapper sets ax.set_aspect(1).
    - Guaranteed Axes configuration (inherited from the plotting helper plus the aspect enforcement):
        * A new Figure and Axes were created.
        * A pcolormesh visualizing the provided DataFrame was added to the Axes.
        * Y-ticks placed at centered row positions and labeled with the DataFrame index.
        * X-ticks cleared and X-axis labeled "Time".
        * Y-axis inverted so the first DataFrame row appears at the top.
        * Aspect ratio set to 1 (square cells).
    - If plotting fails (see Raises), no Axes will be returned.

## Raises:
    ValueError:
        - Propagated from _prepare_heatmap_data if a chosen `sortby` key of dtype object cannot be parsed to datetime. Message originates from the preparer and indicates the offending column name and dtype.
        - Propagated from _create_timeseries_heatmap (via numpy) when the prepared DataFrame is empty (e.g., zero rows or zero columns) and np.nanmax is invoked; numpy raises "zero-size array to reduction operation maximum".
    KeyError:
        - If `entity_column` or the chosen `sortby` key is missing from `dataframe`. This originates from pandas operations within the preparation helper and is not caught here.
    TypeError or ValueError:
        - If the prepared DataFrame contains values that cannot be coerced to numeric arrays for plotting, underlying matplotlib/numpy calls invoked by the plotting helper may raise TypeError or ValueError; these propagate.

Notes:
- This wrapper does not catch exceptions raised by either helper; it intentionally propagates them so callers can decide how to handle data or plotting errors.

## Constraints:
Preconditions:
    - `dataframe` must contain `entity_column`.
    - If `sortby` is provided (string or list), `dataframe` must contain the referenced column(s).
    - `figsize` should be a pair of positive integers.
    - `color` should be a Matplotlib-acceptable color string.
    - If `sortby` is of dtype object, its values should be parseable by pandas.to_datetime or already be datetime-like.

Postconditions (guarantees after successful return):
    - An Axes containing a timeseries heatmap has been created and returned.
    - The Axes aspect ratio is set to 1.
    - The underlying pcolormesh uses a white→color colormap with color limits set between 0 and the maximum non-NaN cell value of the prepared DataFrame (as computed by the plotting helper).

## Side Effects:
    - Creates a Matplotlib Figure and Axes (via the plotting helper) and adds artists (pcolormesh). This mutates Matplotlib's global figure/axes state and may display figures depending on the Matplotlib backend.
    - Does not perform file I/O or network I/O.
    - Does not mutate the original `dataframe` argument; the data-preparation helper copies columns and creates temporary columns during processing.
    - No global variables or external service calls are modified.

## Control Flow:
flowchart TD
    Start --> Prepare[Call _prepare_heatmap_data(dataframe, entity_column, sortby, max_entities, selected_entities)]
    Prepare -->|raises| PrepErr[Propagate ValueError/KeyError/TypeError]
    Prepare --> Plot[Call _create_timeseries_heatmap(df, figsize, color)]
    Plot -->|raises| PlotErr[Propagate ValueError/TypeError from plotting/numpy]
    Plot --> SetAspect[Call ax.set_aspect(1)]
    SetAspect --> ReturnAx[Return ax]

## Examples:
Example: typical end-to-end usage
    # Given a DataFrame `df` with columns "user_id" and "event_time" (many timestamped rows per user):
    ax = timeseries_heatmap(df, entity_column="user_id", sortby="event_time", max_entities=3, figsize=(10,4), color="#ff7f0e")
    # The returned Axes `ax` contains a heatmap of counts per user across time bins; use ax.get_figure().colorbar(ax.collections[-1], ax=ax) to add a colorbar if desired.

Example: selecting specific entities (ordered)
    # Provide exactly the list of entity identifiers you want to plot; max_entities is ignored.
    ax = timeseries_heatmap(df, entity_column="user_id", sortby="event_time", selected_entities=["alice","bob"], figsize=(8,3))

Example: defensive usage with error handling
    try:
        ax = timeseries_heatmap(df, entity_column="user_id", sortby="event_time")
    except KeyError as e:
        # missing required column: report to user or fall back
        handle_missing_column(e)
    except ValueError as e:
        # could be parsing failure for sortby or empty data leading to numpy error
        handle_bad_data(e)

Implementation note for re-creation:
    - To reimplement this function, call the data-preparation routine that returns an entities × bins DataFrame, pass that DataFrame to a plotting routine that creates a Figure/Axes and draws a pcolormesh with a white→color colormap, then set ax.set_aspect(1) and return the Axes. Ensure exceptions from data preparation and plotting are propagated.

## `src.ydata_profiling.visualisation.plot._set_visibility` · *function*

## Summary:
Makes all axis spines invisible and sets the tick-positioning mode for both x and y axes, returning the modified Matplotlib Axis.

## Description:
This small helper centralizes two common axis adjustments used when creating minimalist or embedded plots:
- It hides the four spines (top, right, bottom, left) on the provided Matplotlib Axis object.
- It sets the tick position mode for both the x and y axes by forwarding the tick_mark argument to each axis' set_ticks_position method.

Known callers in provided context:
- No direct callers were discovered in the provided source snapshot. Typical callers are visualization helper functions that prepare or finalize Matplotlib Axes for compact, annotation-only, or thumbnail-style plots (for example: small summary plots, heatmap insets, wordcloud axes). These callers typically invoke this function at the end of axes configuration when ticks/spines should be suppressed or set to a specific position.

Why this is a separate function:
- Encapsulates two related axis mutations (spine visibility and tick positioning) into a single reusable unit so multiple plot-generating functions can apply a consistent "minimal" styling without duplicating code. This enforces single-responsibility for axis-level visibility settings and reduces duplication across plotting utilities.

## Args:
    axis (matplotlib.axis.Axis):
        A Matplotlib Axis object (the typical object returned by pyplot.subplots()[1] or similar).
        The function mutates this object in-place by modifying its spines and axis tick positions.
    tick_mark (str, optional):
        String forwarded to axis.xaxis.set_ticks_position and axis.yaxis.set_ticks_position.
        Default: "none".
        Note: Valid values are determined by Matplotlib's Axis.set_ticks_position implementation (e.g., commonly 'none', 'top', 'bottom', 'left', 'right', 'both', 'default'). This function does not validate the value itself — invalid values may raise errors from Matplotlib.

Interdependencies:
- The function relies on axis.spines supporting the keys 'top', 'right', 'bottom', 'left' and on axis.xaxis and axis.yaxis exposing a set_ticks_position method.

## Returns:
    matplotlib.axis.Axis:
        The same Axis object passed in (returned for convenience). The Axis is modified in-place:
        - Each of axis.spines['top'|'right'|'bottom'|'left'] has visibility set to False.
        - axis.xaxis and axis.yaxis have had set_ticks_position(tick_mark) applied.

## Raises:
    KeyError:
        If axis.spines does not contain one of the expected anchors ('top', 'right', 'bottom', 'left'), attempting to access that spine will raise KeyError (propagated from the mapping access).
    Exception (from Matplotlib):
        If tick_mark is not accepted by Matplotlib's set_ticks_position, that method may raise a ValueError or other Matplotlib-specific exception. Such exceptions are propagated; this function does not catch or translate them.

## Constraints:
Preconditions:
- axis must be a valid Matplotlib Axis with:
    - a spines mapping containing the four anchors 'top', 'right', 'bottom', 'left',
    - xaxis and yaxis attributes exposing a set_ticks_position method.
- The caller should supply a tick_mark string that is valid for Matplotlib's Axis.set_ticks_position to avoid Matplotlib errors.

Postconditions:
- After successful return:
    - axis.spines['top'], axis.spines['right'], axis.spines['bottom'], axis.spines['left'] are all invisible (their visible property is False).
    - axis.xaxis and axis.yaxis have had their tick position set to the provided tick_mark.
    - The function returns the same Axis instance (mutated).

## Side Effects:
- Mutates the provided Axis object in-place (no copy is made).
- No I/O, network access, or global state mutation.
- No external service calls.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> ForLoop{for anchor in ['top','right','bottom','left']}
    ForLoop --> AccessSpine[axis.spines[anchor]]
    AccessSpine --> SetVisible[call set_visible(False)]
    SetVisible --> LoopNext{more anchors?}
    LoopNext -->|yes| ForLoop
    LoopNext -->|no| SetXTick[axis.xaxis.set_ticks_position(tick_mark)]
    SetXTick --> SetYTick[axis.yaxis.set_ticks_position(tick_mark)]
    SetYTick --> ReturnAxis[return axis]
    ReturnAxis --> End([End])

## Examples:
Example 1 — hide spines and remove ticks (common for thumbnails):
    fig, ax = pyplot.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax = _set_visibility(ax, tick_mark="none")
    # ax now has no visible spines and no tick markers shown

Example 2 — hide spines but show ticks on the bottom:
    fig, ax = pyplot.subplots()
    ax.scatter([0, 1], [0, 1])
    ax = _set_visibility(ax, tick_mark="bottom")
    # spines hidden; x and y tick position both set to 'bottom' per Matplotlib behavior

Example 3 — defensive caller usage with error handling:
    try:
        ax = _set_visibility(ax, tick_mark="invalid_value")
    except KeyError:
        # handle missing spine mapping
        raise
    except Exception as e:
        # catch Matplotlib errors resulting from invalid tick_mark
        raise RuntimeError("Invalid tick_mark or Matplotlib error") from e

## `src.ydata_profiling.visualisation.plot.missing_bar` · *function*

## Summary:
Creates a two-layer bar chart that visualizes per-column non-null proportions (percentage of non-missing values) and annotates each bar with the raw non-null counts; returns the Matplotlib Axis containing the percentage bars.

## Description:
This function accepts a pandas Series of per-column non-null counts and the total number of rows, computes the per-column non-missing percentage, and draws either a vertical bar chart (when the number of columns is small) or a horizontal bar chart (when many columns) with a secondary twin axis showing raw counts. The visual result is a compact missingness summary suitable for embedding in reports.

Known callers:
- src.ydata_profiling.model.missing.missing_bar — expected to prepare notnull_counts and nrows and then call this visual helper during report generation.
- No other direct callers discovered in the available snapshot; typical usage occurs in a report-building pipeline when rendering a "missing values" section.

Why this logic is extracted:
- Separates plotting concerns (how the missingness bars and labels are drawn) from data preparation and serialization responsibilities. This helper returns a Matplotlib Axis so higher-level code can serialize or further customize the figure and then clean up resources.

## Args:
    notnull_counts (pd.Series):
        A pandas Series indexed by variable/column name containing integer non-null counts for each column.
        - Required shape: 1-D series with length >= 0.
        - Values are expected to be integers in [0, nrows]. The function does not coerce types; non-numeric values may cause plotting to fail.
    nrows (int):
        Total number of rows in the DataFrame used to compute percentages (denominator).
        - Expected to be >= 0. If 0, the division produces inf/NaN entries in percentage (see Constraints).
    figsize (Tuple[float, float], optional):
        Matplotlib figure size forwarded to pandas/Matplotlib plotting calls. Default: (25, 10).
    fontsize (float, optional):
        Font size used for axis tick labels and count labels. Default: 16.
    labels (bool, optional):
        Controls whether original axis tick labels are preserved on the "many columns" (horizontal) layout.
        - True: keep axis tick labels (column names) on primary axis; False: hide them (secondary axis still shows raw counts).
        - Default: True.
    color (Tuple[float, ...], optional):
        RGB or RGBA tuple of floats in [0, 1] supplying the bar color. Typical shape is (r, g, b).
        - Default: (0.41, 0.41, 0.41).
    label_rotation (int, optional):
        Rotation in degrees applied to x tick labels in the vertical-bar layout. Default: 45.

Interdependencies:
- notnull_counts and nrows are interdependent: percentage is computed as notnull_counts / nrows. Supplying inconsistent values (e.g., counts > nrows) will produce percentages >1 on the plot.

## Returns:
    matplotlib.axis.Axis:
        The primary Axis (ax0) containing the percentage bar plot:
        - For len(notnull_counts) <= 50: a vertical bar chart (percentage per column). The twin top axis (ax1) shows the raw non-null counts as tick labels aligned with the bars.
        - For len(notnull_counts) > 50: a horizontal bar chart (percentage) with a right-side twin axis (ax1) containing the raw counts as tick labels.
        Both the primary and twin axes are mutated by the function (tick labels, limits) and then passed through _set_visibility for consistent minimal styling. The returned object is the primary axis (ax0).

Possible edge-case returns:
- The function always returns an axis object when plotting succeeds. If passed an empty Series, it will return an axis corresponding to an empty plot (no bars). Plotting failures raise exceptions instead of returning None.

## Raises:
    - No explicit exceptions are raised by the function itself; exceptions from underlying libraries may propagate:
        * pandas/Matplotlib errors: If pandas.Series.plot or Matplotlib operations fail (e.g., invalid figsize, invalid color tuple), the original exception will propagate (TypeError, ValueError, etc.).
        * _set_visibility may raise KeyError if the axis object lacks expected spines (this documentation acknowledges that the _set_visibility helper's snapshot did not list direct callers, but this function does invoke that helper; any exception raised within _set_visibility will propagate).
    - Note on division by zero: passing nrows == 0 will not raise a Python ZeroDivisionError inside the function (pandas/numpy division yields inf/NaN), but later plotting or label formatting may raise errors or produce an invalid-looking chart.

## Constraints:
Preconditions:
- notnull_counts must be a pandas Series (pd.Series) or Series-like with numeric values and an index of label names.
- nrows should be an integer (ideally > 0). Upstream code should handle the special-case nrows == 0 or empty notnull_counts if a different behavior is desired.
- Matplotlib must be available and functioning because the function delegates to pandas.Series.plot and calls the local helper _set_visibility.

Postconditions:
- The returned Axis (ax0) contains percentage bars; a twin axis (ax1) exists and shows raw counts as tick labels.
- Both axes are passed through _set_visibility (spines hidden and tick positions set per that helper).
- The Matplotlib Figure associated with ax0 is left open; caller is responsible for serializing and closing/clearing the figure to avoid memory leaks.

## Side Effects:
- Creates/modifies Matplotlib objects (Figure and Axis instances) via pandas plotting.
- Mutates the provided axes (ax0 and its twin ax1) in-place: tick labels, tick positions, axis limits, and visibility settings via _set_visibility.
- No file I/O, network access, or global variable mutation occurs in this function.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> ComputePerc[Compute percentage = notnull_counts / nrows]
    ComputePerc --> CheckCountLen{len(notnull_counts) <= 50 ?}
    CheckCountLen -- Yes --> Vertical[Create vertical bar plot\nax0 = percentage.plot.bar(...)]
    Vertical --> SetXLabels[Set ax0 xticklabels (rotation, fontsize, ha='right')]
    SetXLabels --> TwinTop[ax1 = ax0.twiny()]
    TwinTop --> SyncTopTicks[ax1.set_xticks(ax0.get_xticks())\nax1.set_xlim(ax0.get_xlim())]
    SyncTopTicks --> SetTopLabels[ax1.set_xticklabels(notnull_counts, ha='left', fontsize=fontsize, rotation=label_rotation)]
    CheckCountLen -- No --> Horizontal[Create horizontal bar plot\nax0 = percentage.plot.barh(...)]
    Horizontal --> PrepareYLabels[ylabels = ax0.get_yticklabels() if labels else []]
    PrepareYLabels --> ApplyYLabels[ax0.set_yticklabels(ylabels, fontsize=fontsize)]
    ApplyYLabels --> TwinRight[ax1 = ax0.twinx()]
    TwinRight --> SyncRightTicks[ax1.set_yticks(ax0.get_yticks())\nax1.set_ylim(ax0.get_ylim())]
    SyncRightTicks --> SetRightLabels[ax1.set_yticklabels(notnull_counts, fontsize=fontsize)]
    SetTopLabels --> PostProcess
    SetRightLabels --> PostProcess
    PostProcess --> VisibilityLoop{for ax in [ax0, ax1]}
    VisibilityLoop --> CallSetVis[_set_visibility(ax)]
    CallSetVis --> EndReturn[Return ax0]
    EndReturn --> End([End])

## Examples:
Example 1 — Typical use in a report pipeline (happy path):
    # Prepare counts from a DataFrame "df"
    notnull_counts = df.notnull().sum(axis=0)
    ax = missing_bar(notnull_counts, nrows=df.shape[0])
    # ax now contains a percentage bar plot; obtain the figure to serialize:
    fig = ax.get_figure()
    # Caller should save/serialize fig (e.g., fig.savefig(buffer, format="svg")) and then close it:
    # fig.clf(); matplotlib.pyplot.close(fig)

Example 2 — Many columns (horizontal layout):
    # For a wide dataset with > 50 columns, pass the same inputs
    notnull_counts = df.notnull().sum(axis=0)
    ax = missing_bar(notnull_counts, nrows=df.shape[0], labels=False)
    # The returned axis shows horizontal bars; the right-side twin axis lists raw counts.

Example 3 — Defensive upstream handling for zero rows:
    # This function does not raise on nrows == 0 (pandas will produce inf/NaN), so guard earlier:
    if df.shape[0] == 0:
        # Skip plotting / return a placeholder
        svg = ""
    else:
        notnull_counts = df.notnull().sum(axis=0)
        ax = missing_bar(notnull_counts, nrows=df.shape[0])
        # serialize and close figure afterwards

Notes:
- The function relies on pandas.Series.plot methods and calls the local helper _set_visibility to apply consistent axis styling; exceptions raised by either pandas/Matplotlib or by _set_visibility may propagate to the caller.
- Upstream code (report generator) is responsible for figure serialization and cleanup to prevent memory leaks.

## `src.ydata_profiling.visualisation.plot.missing_matrix` · *function*

## Summary:
Renders a compact missingness matrix as a Matplotlib Axis where white cells represent missing values and colored cells represent present (not-null) values, and returns the configured Axis for embedding or further manipulation.

## Description:
This helper produces a pixel-style visualization of missingness for a table-like dataset. It expects a boolean mask describing which cells are present (not null) across a sampling of rows and the list of column names corresponding to the mask columns. The function constructs an RGB image grid, paints present cells with the provided color and missing cells white, places vertical separators between columns, configures tick labels and axis styling, then returns the Matplotlib Axis that contains the plot.

Known callers and typical pipeline stage:
- src.ydata_profiling.model.missing.missing_matrix (or other higher-level report generation code) — these callers pass a precomputed boolean presence mask (e.g., sampled_df.notnull().to_numpy()), a list of column labels, and a display height into this function. Typical stage: after sampling rows from a DataFrame and building a not-null boolean mask, call this function to obtain an Axis that visualizes missingness; the caller will usually save or embed the resulting figure.

Why this is a separate function:
- Extracts the visualization specifics (RGB grid construction, axis/tick layout, separators, and minimal styling) from higher-level data-preparation logic so callers can focus on sampling, configuration, and encoding/embedding results. It centralizes consistent visual appearance for missingness matrices across the codebase.

## Args:
    notnull (Any):
        Boolean mask describing presence for each cell to be displayed.
        Expected formats (examples):
            - numpy.ndarray of dtype bool with shape (height, width)
            - pandas.DataFrame or pandas.Series boolean mask such that when converted to a NumPy boolean array it yields shape (height, width)
        Requirement: the mask must have exactly `height` rows and `len(columns)` columns (or be convertible to that shape). The function uses the mask directly for NumPy advanced boolean indexing into an (height, width, 3) array.
    columns (List[str]):
        Sequence of column names for the columns visualized. Its length determines the width of the image (width = len(columns)). Typical: list(sampled_df.columns).
    height (int):
        Number of sampled rows represented by the mask (number of image rows). Must be a positive integer and must match the first dimension of `notnull`.
    figsize (Tuple[float, float], optional):
        Matplotlib figure size passed to plt.subplots. Default: (25, 10).
    color (Tuple[float, ...], optional):
        RGB triple (each component in range [0.0, 1.0]) used to paint present (not-null) cells. Default: (0.41, 0.41, 0.41).
        The function assigns this color directly into the image RGB channels.
    fontsize (float, optional):
        Font size used for tick labels. Default: 16.
    labels (bool, optional):
        Whether to display x-axis column labels. When False and the number of columns is large (> 50), labels will be cleared to avoid overcrowding. Default: True.
    label_rotation (int, optional):
        Rotation in degrees applied to x-axis column labels. Default: 45.

Notes about interdependencies:
- `height` must match the number of rows in `notnull`. `len(columns)` must match the number of columns in `notnull`.
- `color` must be compatible with NumPy assignment into an RGB image array (length-3 sequence of floatable values).

## Returns:
    matplotlib.axis.Axis:
        The Matplotlib Axis containing the rendered missingness matrix. The Axis is fully configured:
            - image drawn with imshow
            - x-axis ticks placed at each column position with provided labels (unless suppressed)
            - y-axis ticks shown at the first and last row positions
            - vertical separator lines drawn between columns
            - minimal styling applied via the module helper _set_visibility
        Caller can retrieve the Figure via ax.figure and save or encode the figure as needed.

## Raises:
    TypeError:
        - If `notnull` is of a type that cannot be used as a boolean mask for NumPy array assignment or cannot be converted to the expected shape.
    ValueError:
        - If `height` <= 0 or `len(columns)` == 0 (empty columns list). Passing an empty dimension will typically cause Matplotlib imshow to error.
        - If `color` is not a length-3 iterable of numeric values, NumPy assignment may raise a ValueError.
    IndexError / ValueError (NumPy-related):
        - If the boolean mask shape does not match (height, width), the assignment missing_grid[notnull] = color or missing_grid[~notnull] = [1,1,1] can raise broadcasting/indexing errors.
    Matplotlib exceptions:
        - Errors originating from plt.subplots(), ax.imshow(), or tick/label operations (for example, invalid tick label sequences) will propagate.

The function does not catch exceptions — errors are propagated to the caller.

## Constraints:
Preconditions:
- Matplotlib must be available and functional in the runtime (imports and backends).
- `height` is a positive integer.
- `columns` is a non-empty list of strings.
- `notnull` must be a boolean mask with shape (height, width) where width == len(columns), or be convertible to such shape.

Postconditions:
- On successful return:
    - A Matplotlib Axis has been created that visually encodes the provided presence mask: colored pixels for present cells, white for missing cells.
    - The Axis has separators between columns, ticks configured, and minimal spines/tick-position styling applied by _set_visibility.
    - The returned Axis is ready for figure-level operations (saving, encoding, embedding); it does not close the figure — the caller is responsible for saving/closing the Figure if desired.

## Side Effects:
- Allocates an in-memory NumPy array of shape (height, width, 3) roughly consuming 3 * height * width * 4 bytes (float32).
- Creates a Matplotlib Figure and Axis via plt.subplots; the created Figure remains open until explicitly closed by the caller (e.g., pyplot.close(ax.figure)), so callers should close large numbers of figures to avoid memory leaks.
- No file I/O, network calls, or global variable mutation are performed by this function.
- Mutates only the newly-created Matplotlib Axis and the local NumPy array; it does not mutate the input `notnull` or `columns`.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> ComputeWidth[width = len(columns)]
    ComputeWidth --> ValidateDims{height > 0 and width > 0?}
    ValidateDims -->|no| RaiseError[raise ValueError]
    ValidateDims -->|yes| CreateGrid[missing_grid = zeros((height,width,3), dtype=float32)]
    CreateGrid --> PaintPresent[missing_grid[notnull] = color]
    PaintPresent --> PaintMissing[missing_grid[~notnull] = [1,1,1]]
    PaintMissing --> CreateFigure[_, ax = plt.subplots(1,1,figsize=figsize)]
    CreateFigure --> ShowImage[ax.imshow(missing_grid, interpolation="none")]
    ShowImage --> ConfigureAxis[set aspect/grid/ticks/top]
    ConfigureAxis --> SetXTicks[ax.set_xticks(range(width)); ax.set_xticklabels(columns,...)]
    SetXTicks --> SetYTicks[ax.set_yticks([0,height-1]); set_yticklabels([1,height])]
    SetYTicks --> DrawSeparators[for each sep: ax.axvline(...)]
    DrawSeparators --> MaybeHideLabels{if not labels and width > 50}
    MaybeHideLabels -->|yes| ClearXLabels[ax.set_xticklabels([])]
    MaybeHideLabels -->|no| SkipClear[do nothing]
    SkipClear --> ApplyVisibility[ax = _set_visibility(ax)]
    ClearXLabels --> ApplyVisibility
    ApplyVisibility --> ReturnAxis[return ax]
    ReturnAxis --> End([End])

## Examples:
Example 1 — basic usage with a NumPy boolean mask:
    import numpy as np
    # Prepare a boolean mask: True == present, False == missing
    height = 50
    columns = ['col_a', 'col_b', 'col_c']
    # mask shape (height, 3)
    notnull_mask = np.random.rand(height, len(columns)) > 0.2
    ax = missing_matrix(notnull_mask, columns, height)
    fig = ax.figure
    # Save or encode the figure, then close to release resources
    fig.savefig("missing_matrix.png", bbox_inches="tight")
    pyplot.close(fig)

Example 2 — using pandas sampling upstream and suppressing labels for wide tables:
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({
        f"c{i}": np.random.choice([1.0, None], size=200, p=[0.8, 0.2])
        for i in range(120)
    })
    # Sample or choose height=100 rows; produce boolean notnull mask
    sampled = df.sample(n=100, random_state=0)
    notnull_mask = sampled.notnull().to_numpy(dtype=bool)
    columns = list(sampled.columns)
    ax = missing_matrix(notnull_mask, columns, height=100, labels=False)
    # Because labels=False and width>50, x labels will be hidden automatically
    fig = ax.figure
    # encode or save as desired
    fig.savefig("wide_missing_matrix.png", bbox_inches="tight")
    pyplot.close(fig)

Example 3 — defensive usage showing shape mismatch handling:
    # If height does not match the mask shape, the function will raise a NumPy/ValueError.
    try:
        notnull_mask = np.ones((10, 5), dtype=bool)
        # but pass height that does not match first dimension
        ax = missing_matrix(notnull_mask, ['a','b','c','d','e'], height=8)
    except Exception as e:
        # Handler should inspect and surface a helpful error to the user
        raise ValueError("notnull mask shape does not match provided height/columns") from e

## `src.ydata_profiling.visualisation.plot.missing_heatmap` · *function*

## Summary:
Render a correlation-style heatmap for pairwise missingness values and return the matplotlib Axes containing the plotted heatmap.

## Description:
This function draws a heatmap (using seaborn) for a numeric square matrix of pairwise missingness correlation/similarity values and applies presentation finishing touches (tick placement, tick rotation, visibility settings, and annotation formatting). It is intended to be called after computing a pairwise correlation matrix for missingness (for example, from df.isnull().corr()) and a boolean mask to hide redundant cells (e.g., an upper-triangle mask).

Known callers within the codebase and typical context:
- Typically invoked from higher-level "missingness analysis" routines that compute the missingness correlation matrix and then delegate plotting to this function. Example caller (pattern): compute corr = missing_bool.corr(); mask = np.triu(np.ones(corr.shape, dtype=bool)); ax = missing_heatmap(corr, mask, ...).
- In this repository the model-level missingness visualization function (src.ydata_profiling.model.missing.missing_heatmap) is expected to call this visualization helper once implemented.

Why this is a separate function:
- Encapsulates all plotting-specific details (seaborn usage, axis formatting, annotation post-processing) so that computation of the matrix and rendering/encoding can remain separate responsibilities.
- Makes the plotting behaviour reusable and testable independent of the data-preparation logic.

## Args:
    corr_mat (Any)
        - Type: Any  (expected: pandas.DataFrame, numpy.ndarray, or similar 2D numeric square matrix)
        - Description: Square matrix of pairwise values to plot (e.g., pairwise missingness correlations or similarities). Values must be numeric (or convertible to numeric strings) when annotations are enabled.
        - Required: yes

    mask (Any)
        - Type: Any (expected: numpy.ndarray or DataFrame-like boolean mask)
        - Description: Boolean mask with the same shape as corr_mat where True indicates cells that should be hidden by the heatmap (commonly used to hide the upper or lower triangle).
        - Required: yes

    figsize (Tuple[float, float], optional)
        - Default: (20, 12)
        - Description: Figure size in inches passed to matplotlib.pyplot.subplots when creating the plotting Axes.

    fontsize (float, optional)
        - Default: 16
        - Description: Font size used for tick labels and (indirectly) annotation font size (annotation font size is set to fontsize - 2).

    labels (bool, optional)
        - Default: True
        - Description: If True, enable seaborn annotation text (annot=True) so that numerical values appear in each visible cell. If False, annotations are disabled.

    label_rotation (int, optional)
        - Default: 45
        - Description: Rotation angle in degrees applied to the x-axis tick labels.

    cmap (str, optional)
        - Default: "RdBu"
        - Description: Matplotlib/seaborn colormap name used to color the heatmap.

    normalized_cmap (bool, optional)
        - Default: True
        - Description: If True, the function enforces a normalized color range by supplying vmin=-1 and vmax=1 to seaborn. If False, no vmin/vmax are provided and seaborn chooses the color scaling.

    cbar (bool, optional)
        - Default: True
        - Description: Whether to draw the colorbar alongside the heatmap.

    ax (matplotlib.axis.Axis, optional)
        - Default: None
        - Description and important note: Although an ax parameter appears on the function signature, the current implementation always creates a new figure and Axes with matplotlib.pyplot.subplots and overwrites any passed-in ax. In other words, any provided ax argument is ignored by this implementation.

## Returns:
    matplotlib.axis.Axis
        - Description: The matplotlib Axes instance containing the heatmap that was created and customized by the function.
        - Edge cases:
            * If labels=False then the returned Axes will contain no annotation Text objects.
            * The function does not close or return the Figure object; it returns the Axes attached to the created Figure. The caller may retrieve the Figure via ax.get_figure() if needed.

## Raises:
    - The function contains no explicit raise statements. However, runtime exceptions may be raised by underlying libraries or by annotation post-processing:
        * TypeError / ValueError from seaborn/matplotlib if corr_mat or mask have incompatible shapes or types.
        * ValueError when converting annotation text to float during the annotation post-processing loop if an annotation text is not a numeric string (for example, float("not-a-number") raises ValueError).
        * Other matplotlib/seaborn runtime errors (e.g., memory errors for extremely large matrices).

## Constraints:
    Preconditions:
        - corr_mat must be a 2D square matrix-like object (shape NxN) of numeric values or values that seaborn/matplotlib can display.
        - mask must be a boolean array-like with the same shape as corr_mat.
        - matplotlib and seaborn must be importable and working in the current environment.
    Postconditions:
        - A new matplotlib Figure and Axes are created (plt.subplots) and the returned Axes contains the rendered heatmap.
        - The function modifies the Axes in-place (tick placement, tick labels, patch visibility, annotation texts).
        - The function does not close the created Figure; caller is responsible for closing or saving the Figure if necessary.

## Side Effects:
    - Allocates a new matplotlib Figure and Axes object via matplotlib.pyplot.subplots.
    - Uses seaborn.heatmap to draw on the Axes.
    - Mutates the Axes object (tick placement, label rotation, text annotation content, patch visibility).
    - Does not close or destroy the Figure; failing to explicitly close or save the Figure may increase memory usage in long-running processes.
    - No file, network, or global state is written by this function itself.

## Control Flow:
flowchart TD
    Start([Start])
    CreateFig["Call plt.subplots(figsize) -> (fig, ax)"]
    NormArgs{"normalized_cmap == True?"}
    CallHeatmapLabels{"labels == True?"}
    seabornAnnot["Call sns.heatmap(..., annot=True, annot_kws={'size': fontsize-2}, **norm_args)"]
    seabornNoAnnot["Call sns.heatmap(..., annot=False, **norm_args)"]
    TickBottom["ax.xaxis.tick_bottom()"]
    SetXTicks["ax.set_xticklabels(..., rotation=label_rotation, fontsize=fontsize)"]
    SetYTicks["ax.set_yticklabels(..., fontsize=fontsize)"]
    SetVisibility["_set_visibility(ax) -> returns ax"]
    HidePatch["ax.patch.set_visible(False)"]
    AdjustText["for each text in ax.texts: parse float(text.get_text()) and reformat text ('<1', '1', '', round(t,1), etc.)"]
    ReturnAx["return ax"]
    End([End])

    Start --> CreateFig --> NormArgs
    NormArgs -- True --> CallHeatmapLabels
    NormArgs -- False --> CallHeatmapLabels
    CallHeatmapLabels -- True --> seabornAnnot
    CallHeatmapLabels -- False --> seabornNoAnnot
    seabornAnnot --> TickBottom
    seabornNoAnnot --> TickBottom
    TickBottom --> SetXTicks --> SetYTicks --> SetVisibility --> HidePatch --> AdjustText --> ReturnAx --> End

## Examples:
Example 1 — typical usage (assumes corr_mat is a pandas.DataFrame and mask is a boolean ndarray)
    # Prepare a mask to hide the upper triangle
    mask = numpy.triu(numpy.ones(corr_mat.shape, dtype=bool))
    ax = missing_heatmap(corr_mat, mask, figsize=(12, 10), fontsize=14, labels=True, label_rotation=45, cmap="RdBu", normalized_cmap=True, cbar=True)
    # Save the figure if desired
    fig = ax.get_figure()
    fig.savefig("missingness_heatmap.png", bbox_inches="tight")
    matplotlib.pyplot.close(fig)  # close when done to free memory

Example 2 — labels disabled (no numeric annotations)
    ax = missing_heatmap(corr_mat, mask, labels=False)
    # The returned Axes contains the heatmap but no text annotations.

Notes and implementation hints:
    - normalized_cmap=True sets vmin=-1 and vmax=1 when calling seaborn.heatmap. If your data is not normalized to the [-1,1] range, set normalized_cmap=False.
    - The function currently ignores any ax passed in via the signature and always creates its own Axes; if you need to plot into an existing Axes, either modify this function to accept and use the provided ax or extract plotting logic into a variant that accepts ax.
    - The final loop converts annotation text to float and then decides how to display it:
        * 0.95 <= t < 1 -> "<1"
        * -1 < t <= -0.95 -> ">-1"
        * t == 1 -> "1"
        * t == -1 -> "-1"
        * -0.05 < t < 0.05 -> "" (empty string — hides near-zero values)
        * otherwise -> round(t, 1)
    - Because the function mutates ax.texts, ensure annotations originate from numeric values; otherwise float(...) conversions may raise ValueError. If corr_mat may contain non-numeric strings, pre-convert or sanitize the matrix before calling this function.

