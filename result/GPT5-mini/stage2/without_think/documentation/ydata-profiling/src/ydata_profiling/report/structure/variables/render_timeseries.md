# `render_timeseries.py`

## `src.ydata_profiling.report.structure.variables.render_timeseries._render_gap_tab` · *function*

## Summary:
Constructs and returns a presentation Container that contains a small table of gap statistics and an image (matplotlib Figure) visualizing missing-value gaps for a time-series variable — the assembled "Gap analysis" UI fragment for a variable report.

## Description:
This function produces two presentation items from a time-series variable summary:
1. A Table named "Gap statistics" containing five rows (number of gaps, min, max, mean, std) with each value formatted for display using the configured precision.
2. An Image item that wraps the matplotlib Figure returned by the plotting helper which highlights gap regions on the time-series.

Known callers and typical stage:
- Called by the time-series variable rendering pipeline when assembling per-variable report tabs. It is invoked when a variable summary dictionary includes a "gap_stats" entry and a "varid" (used to anchor UI elements). Typical trigger: the profiler has computed gap statistics for a datetime-indexed or time-series variable and the report generator is building the "Gap analysis" tab.

Why this is a dedicated function:
- Encapsulates the formatting, table construction, plotting call and anchoring logic for gap analysis into a single reusable unit. This boundary keeps the higher-level tab assembly code concise and ensures consistent naming/anchoring/formatting rules for gap-analysis components.

## Args:
    config (Settings):
        Settings instance used for formatting and presentation parameters. Required attributes read by this function:
        - config.report.precision (int): forwarded to fmt_numeric and fmt_timespan_timedelta.
        - config.html.style (Style): passed as the Table.style.
        - config.plot.image_format (ImageType): used for Image.image_format and Container.image_format.
        The function expects these attributes to exist and be valid.

    summary (dict):
        Required shape and keys:
        - "varid" (str): variable identifier used to construct anchor IDs:
            * image anchor_id -> f"{summary['varid']}_gap_plot"
            * container anchor_id -> f"{summary['varid']}_gap_analysis"
        - "gap_stats" (dict) containing:
            - "gaps": a sequence (supports len(...)) of gap-range objects. Each gap is passed directly as the x argument to matplotlib.axes.Axes.fill_between in the plotting helper, so each gap must be an index-like iterable of x-coordinates or a slice-like/array-like object acceptable to ax.fill_between.
            - "series": either a pandas.Series or a list of pandas.Series (the plotting helper accepts both forms).
            - "min", "max", "mean", "std": timespan-like or numeric values acceptable to fmt_timespan_timedelta (e.g., pandas.Timedelta or numeric seconds).
        Notes on interdependencies:
        - "gaps" and "series" are both forwarded to the plotting helper and must be compatible (e.g., if series is a list, gaps should be a list with matching structure so that zip(series, gaps, ...) in the plot helper works).

## Returns:
    Container:
        - sequence_type: "grid"
        - image_format: config.plot.image_format
        - name: "Gap analysis"
        - anchor_id: f"{summary['varid']}_gap_analysis"
        - content['items']: a 2-item sequence:
            1. Table instance (name="Gap statistics", style=config.html.style)
                - content["rows"]: list[dict] with five entries, each dict has:
                    - "name" (str): label (e.g., "number of gaps", "min", "max", "mean", "std")
                    - "value" (str): formatted value produced by:
                        * "number of gaps": fmt_numeric(len(summary["gap_stats"]["gaps"]), precision=config.report.precision)
                        * other rows: fmt_timespan_timedelta(summary["gap_stats"][key], precision=config.report.precision)
                - content["style"]: config.html.style
            2. Image instance
                - content["image"]: the matplotlib.figure.Figure returned by plot_timeseries_gap_analysis(config, series, gaps)
                - content["image_format"]: config.plot.image_format
                - content["alt"]: "Gap plot"
                - content["name"]: empty string (the function passes name="")
                - anchor_id: f"{summary['varid']}_gap_plot"

    Edge-case notes:
        - The function always returns a Container object if it completes normally; it does not return None.
        - The Table and Image objects are presentation-layer items; their render() methods are renderer-specific and are not implemented by these classes.

## Raises:
    KeyError:
        - If summary lacks "varid" or "gap_stats", or if gap_stats is missing any required key ("gaps", "series", "min", "max", "mean", "std"), a KeyError will be raised when the missing key is accessed.

    TypeError / ValueError / matplotlib/pandas-related exceptions:
        - fmt_numeric and fmt_timespan_timedelta may raise TypeError/ValueError (or propagate other formatting exceptions) if values or precision are incompatible.
        - plot_timeseries_gap_analysis may raise matplotlib, pandas, or other runtime exceptions if "series" or "gaps" are malformed, or if plotting operations fail.
        - Image constructor may raise ValueError if the image argument is None; in this function a Figure object is supplied (unless the plot helper returns None), so a None Figure would cause Image.__init__ to raise.
    These exceptions propagate; _render_gap_tab does not catch them.

## Constraints:
Preconditions:
    - config must expose the required attributes (see Args). The config values must be valid (e.g., config.report.precision an int, config.html.style a Style instance).
    - summary must include the keys and compatible types described above.
    - Each gap element must be usable as the x parameter for matplotlib.axes.Axes.fill_between (e.g., array-like x-values or slice-like objects).
    - If series is a list, it should align in structure with gaps and labels expected by the plotting helper.

Postconditions:
    - No mutation of the input summary dict is performed by this function.
    - A Container instance is returned whose content contains the Table and Image items described above.

## Side Effects:
    - Calls plot_timeseries_gap_analysis(...) which:
        * Creates and configures a matplotlib Figure and Axes.
        * May modify pyplot state (the current figure/axes) transiently (typical matplotlib behavior).
        * Returns a Figure object (the Image payload).
      As a result, this function indirectly causes creation of matplotlib objects and associated memory usage. It does not save files or perform network I/O itself.
    - No I/O, database, or external service calls are performed by _render_gap_tab.

## Control Flow:
flowchart TD
    Start([Start _render_gap_tab]) --> ReadSummary[Read summary['gap_stats'] and summary['varid']]
    ReadSummary --> BuildStats[Build gap_stats list of 5 dict rows using fmt_numeric and fmt_timespan_timedelta]
    BuildStats --> CreateTable[Instantiate Table(rows=gap_stats, name="Gap statistics", style=config.html.style)]
    CreateTable --> CallPlot[Call plot_timeseries_gap_analysis(config, series, gaps)]
    CallPlot --> ReceiveFig{"plot returns Figure (or raises)"}
    ReceiveFig -- raises --> PropagateError([Propagate plotting/formatting exception])
    ReceiveFig -- ok --> CreateImage[Instantiate Image(Figure, image_format=config.plot.image_format, alt="Gap plot", name="", anchor_id=f"{varid}_gap_plot")]
    CreateImage --> CreateContainer[Instantiate Container([Table, Image], sequence_type="grid", image_format=config.plot.image_format, name="Gap analysis", anchor_id=f"{varid}_gap_analysis")]
    CreateContainer --> Return([Return Container])

## Examples (usage described in prose):
Required summary shape (illustrative):
- summary = {
    "varid": "ts_1",
    "gap_stats": {
        "gaps": [gap1, gap2, ...],                     # gap_i are index-like/array-like sequences passed to ax.fill_between
        "series": series_or_list_of_series,           # pandas.Series or list[pandas.Series]
        "min": timedelta_or_numeric,
        "max": timedelta_or_numeric,
        "mean": timedelta_or_numeric,
        "std": timedelta_or_numeric,
    }
  }

Typical usage flow:
1. Report builder computes gap statistics and prepares the summary dictionary above.
2. The builder calls _render_gap_tab(config, summary).
3. If inputs are valid, the function returns a Container containing:
   - A Table named "Gap statistics" with formatted values (strings).
   - An Image whose content["image"] is a matplotlib.figure.Figure visualizing the gaps; the Image has anchor_id "<varid>_gap_plot" and name set to an empty string.
4. The report rendering layer later takes the returned Container and invokes renderer-specific code to convert Table and Image into final HTML/visual output.

Notes and implementation hints for reimplementation:
- Ensure the "gaps" elements satisfy matplotlib.fill_between's x-parameter contract (array-like x coordinates, or use appropriate numpy/pandas index slices).
- Use config.report.precision consistently for numeric/time formatting to match other report fragments.
- Preserve anchor_id naming convention exactly (f"{varid}_gap_plot" and f"{varid}_gap_analysis") to maintain internal navigation/fragment links in generated reports.

## `src.ydata_profiling.report.structure.variables.render_timeseries.render_timeseries` · *function*

## Summary:
Builds the presentation template for a numeric time-series variable by formatting summary statistics, creating presentation objects (tables, frequency tables, containers, images) and invoking plotting utilities; returns a template_variables dict ready for the HTML report renderer.

## Description:
This function is invoked by the report-generation layer when rendering a numeric time-series variable. Typical callers are the variable-dispatch or template-assembly code that selects a renderer based on a variable's inferred type and provides the pre-computed summary and global Settings.

Responsibility boundary:
- Input: reads the profiler Settings and a single-variable summary dictionary (pre-computed statistics and plotting data).
- Work: formats numeric values, marks alert rows, calls plotting helper functions to produce image payloads, constructs presentation-layer objects (VariableInfo, Table, Image, Container, FrequencyTable), and assembles them into the template_variables mapping.
- Output: returns the assembled template_variables dict; it does not perform statistical computation or mutate the summary/config objects.

Why this is a separate function:
- Isolates presentation/layout concerns from summary computation.
- Allows reuse of summary data across multiple output formats and simplifies unit testing of rendering logic.

## Args:
- config (Settings)
    - Type: Settings (profiler configuration object).
    - Required fields accessed:
        - config.plot.image_format (str): format to pass to Image objects (e.g., "png", "svg").
        - config.html.style (str): style string forwarded to Table/Container constructors.
        - config.report.precision (int): decimal precision used by fmt_numeric.
        - config.n_extreme_obs (int): used to label extreme-values tables.
    - The function only reads config; it does not modify it.

- summary (dict)
    - Type: dict containing pre-computed metrics and plotting inputs for a single time-series variable.
    - Required keys and expected types/semantics:
        - varid: str|int — unique identifier used to build anchor_id strings.
        - varname: str — human-readable variable name.
        - alerts: list[str] — list of alert messages for the variable (displayed by VariableInfo).
        - description: str — a short textual description displayed in VariableInfo.
        - alert_fields: collection (list/set) of str — names of fields that should be visually flagged as alerts when present.
        - series: array-like or pandas.Series — raw or resampled time-series values provided to plotting functions and autocorrelation analysis.
        - histogram: either:
            - list of pairs: [(edges_1, counts_1), (edges_2, counts_2), ...], OR
            - two-element sequence: (edges, counts)
          The code branches on isinstance(summary["histogram"], list):
            - If list: the function constructs lists of edges ([x[0] for x in histogram]) and counts ([x[1] for x in histogram]) and calls histogram(config, edges_list, counts_list).
            - If not list: the function unpacks histogram and calls histogram(config, *summary["histogram"]).
          Note: an empty list for histogram will cause indexing into summary["histogram"][0] later and will raise IndexError.
        - freq_table_rows: list — rows used to create the FrequencyTable of common values.
        - firstn_expanded: list — rows to populate the "Minimum N values" FrequencyTable.
        - lastn_expanded: list — rows to populate the "Maximum N values" FrequencyTable.
        - n_distinct, p_distinct, n_missing, p_missing, n_infinite, p_infinite: ints/floats — distinct/missing/infinite counts and proportions.
        - mean, min, max, n_zeros, p_zeros, memory_size: numeric / int — used in the top summary tables.
        - percentiles: "5%","25%","50%","75%","95%" — numeric percentile values (strings as keys).
        - range, iqr, std, cv, kurtosis, mad, skewness, sum, variance: numeric — descriptive statistics.
        - monotonic: value interpretable by fmt_monotonic (e.g., indicator or enum).
        - addfuller: numeric — Augmented Dickey-Fuller p-value.
    - Interdependencies:
        - alert_fields membership toggles the "alert" flag on certain table rows.
        - histogram format dictates which histogram(...) invocation is used.

## Returns:
- dict
    - The function returns the template_variables dict originally produced by render_common(config, summary) with two keys added/overwritten:
        - "top": Container — a grid container holding:
            - VariableInfo (info),
            - Table (table1: distinct/missing/infinite metrics),
            - Table (table2: mean/min/max/zeros/memory),
            - Image (mini time-series plot).
        - "bottom": Container — a tabs container holding:
            - statistics Container (grid of quantile_statistics and descriptive_statistics Tables),
            - hist Image (histogram),
            - ts_plot Image (full time-series plot),
            - ts_gap object returned by _render_gap_tab(config, summary),
            - fq FrequencyTable (common values),
            - evs Container (two FrequencyTable tabs for min/max extreme values),
            - acf_pacf Image (ACF/PACF).
    - Anchor/ID conventions produced in outputs (important for downstream linking):
        - Statistics anchor_id: f"{varid}statistics"
        - Histogram anchor_id: f"{varid}histogram"
        - Common values anchor_id: f"{varid}common_values"
        - Extreme values anchor_id: f"{varid}extreme_values"
        - ACF/PACF anchor_id: f"{varid}acf_pacf"
        - Time-series plot anchor_id: f"{varid}_ts_plot"
        - Bottom container anchor_id: f"{varid}bottom"
    - The function always returns a dict when inputs are valid; plotting utilities might return placeholder images for empty data but Image objects will still be created.

## Raises:
- KeyError
    - Raised if any required key is missing from summary when the function attempts to access it (e.g., missing "series", "histogram", or "varid").
- IndexError
    - Can occur if summary["histogram"] is an empty list (code indexes [0][1] to compute caption), or if expected inner arrays have insufficient length.
- TypeError / ValueError
    - Propagated from called formatting helpers or plotting functions if inputs have incompatible types (for example, non-iterable histogram entries or non-numeric statistics).
- Note: The function does not raise custom exceptions; callers should validate inputs to present clearer error messages.

## Constraints:
- Preconditions:
    - config must expose the Settings attributes used in Args.
    - summary must contain all required keys with compatible types and non-empty histogram when using the list form.
- Postconditions:
    - Returned template_variables contains "top" and "bottom" keys populated with presentation objects that the templating layer can render without further modification.
    - No mutation of config or summary occurs.

## Side Effects:
- Calls plotting utilities which may allocate image buffers or compute graphs:
    - mini_ts_plot(config, summary["series"]) — mini plot used in the top grid.
    - histogram(config, ...) — produces histogram payload (list or unpacked form depending on summary["histogram"]).
    - plot_acf_pacf(config, summary["series"]) — produces ACF and PACF visual payload.
    - mini_ts_plot(config, summary["series"], figsize=(7, 3)) — produces the larger time-series image.
    - _render_gap_tab(config, summary) — produces the gap-analysis tab content (implementation resides in the same module).
  These calls do not perform file or network I/O at this layer; any such I/O would be performed by the plotting utilities themselves if configured.
- No global state is modified by this function.

## Control Flow:
flowchart TD
    Start --> RenderCommon[call render_common(config, summary)]
    RenderCommon --> BuildInfo[create VariableInfo(summary['varid'], summary['varname'], name, ...)]
    BuildInfo --> BuildTable1[create Table with distinct/missing/infinite rows]
    BuildTable1 --> BuildTable2[create Table with mean/min/max/zeros/memory rows]
    BuildTable2 --> MiniPlot[call mini_ts_plot(config, series)]
    MiniPlot --> SetTop[set template_variables["top"] = Container(...)]
    SetTop --> Quantiles[create quantile_statistics Table]
    Quantiles --> Descriptive[create descriptive_statistics Table]
    Descriptive --> StatisticsContainer[wrap quantile+descriptive as Container]
    StatisticsContainer --> HistogramBranch{is summary['histogram'] a list?}
    HistogramBranch -->|yes| HistList[call histogram(config, [x[0]...], [x[1]...])]
    HistogramBranch -->|no| HistTuple[call histogram(config, *summary['histogram'])]
    HistList --> BuildHist[create hist Image with computed caption]
    HistTuple --> BuildHist
    BuildHist --> FreqTable[create FrequencyTable from template_variables['freq_table_rows']]
    FreqTable --> ExtremeValues[create evs Container using firstn_expanded/lastn_expanded]
    ExtremeValues --> ACF_PACF[call plot_acf_pacf(config, series)]
    ACF_PACF --> TS_PLOT[call mini_ts_plot(config, series, figsize=(7,3))]
    TS_PLOT --> GapTab[call _render_gap_tab(config, summary)]
    GapTab --> SetBottom[set template_variables["bottom"] = Container([...])]
    SetBottom --> Return[return template_variables]
    Return --> End

## Examples (non-executable, end-to-end usage and error handling guidance):
- Typical workflow (described):
    1. Upstream component computes a summary dict for a time-series variable and ensures required keys are set (see Args.summary).
    2. The global Settings object is prepared with plot.image_format, html.style, report.precision, and n_extreme_obs.
    3. The report renderer calls this function with config and summary.
    4. The returned template_variables is merged into the report template context and rendered to HTML; the templating layer uses anchor IDs and object names to build the page.

- Error handling recommendation:
    - Validate the summary before calling:
        - Ensure required keys exist (especially "series", "histogram", "varid", and the percentiles).
        - If histogram can be empty, convert it to a two-element placeholder or handle the empty case upstream to avoid IndexError.
    - Catch KeyError and re-raise/convert to a clearer message that names the missing fields (for example: "timeseries render: summary missing keys ['histogram','series']").

## Implementation notes for reimplementers:
- Use the supplied formatting helpers consistently:
    - fmt() for integer-like counts,
    - fmt_percent() for proportions (0..1),
    - fmt_numeric(value, precision=config.report.precision) for floating point statistics,
    - fmt_bytesize() for memory_size,
    - fmt_monotonic() for monotonicity indicator.
- Preserve anchor_id naming (f"{varid}...") to keep stable report links.
- Replicate the histogram branching logic exactly:
    - If summary["histogram"] is a list: build two lists by extracting element 0 and element 1 from each item and pass those lists to the histogram helper.
    - If not a list: unpack the two-element sequence and pass both elements directly to histogram(...).
- When building captions for histograms, follow the pattern:
    - "<strong>Histogram with fixed size bins</strong> (bins={N})" where N is computed as len(counts) - 1 using the counts array referenced in the code path taken.

