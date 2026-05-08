# `src.ydata_profiling.report.structure.variables`

## Tree:
variables/
├── render_boolean.py
├── render_categorical.py
├── render_common.py
├── render_complex.py
├── render_count.py
├── render_date.py
├── render_file.py
├── render_generic.py
├── render_image.py
├── render_path.py
├── render_real.py
├── render_text.py
├── render_timeseries.py
└── render_url.py

## Role:
Provide presentation-layer assembly for per-variable report sections: transform a profiler's per-variable summary dict and global Settings into template-ready presentation objects (VariableInfo, Table, FrequencyTable, Image, Container, etc.). Each file implements the assembly logic for one variable type (categorical, numeric, date, URL, path, timeseries, etc.) or shared helpers used by those renderers.

## Description:
- Where and when used:
  - These renderers are invoked during the "report rendering" stage after the statistics collection stage has produced a per-variable summary (one summary dict per column). A variable-dispatcher chooses a renderer from this module based on the variable type and calls it with (config, summary). Typical callers are the per-variable orchestration code in the report generation pipeline and higher-level modules that assemble the full HTML report.
- Why grouped:
  - All components in this module share the responsibility of presentation assembly for individual variables. Grouping them keeps type-specific layout and inclusion rules together while separating presentation concerns from summary computation and plotting helpers. This enforces a cohesion principle: "take summary data + Settings -> produce presentation objects for one variable."

## Components:
List of public functions (one-line role each). See component-level docs for implementation details and examples.

- render_common(config: Settings, summary: dict) -> dict
  - Build and return base template variables ("freq_table_rows", "firstn_expanded", "lastn_expanded") by delegating to freq_table and extreme_obs_table.

- render_boolean(config: Settings, summary: dict) -> dict
  - Assemble presentation objects for boolean variables (info block, metrics table, small & full frequency tables, optional categorical plots).

- render_categorical(config: Settings, summary: dict) -> dict
  - Assemble presentation objects for categorical/text variables: info, metrics, compact/full frequency tables, optional length/characters/words subsections, and plots.

- _get_n(value) -> Union[int, float, list]
  - Helper: normalize/compute total counts from a pandas-like object or a list of such objects (used by categorical/unicode renderers).

- render_categorical_frequency(config: Settings, summary: dict, varid: str) -> Table
  - Build the small "Unique" Table showing n_unique and p_unique.

- render_categorical_length(config: Settings, summary: dict, varid: str) -> (Table, Image)
  - Build a "Length" summary Table and a length histogram Image.

- render_categorical_unicode(config: Settings, summary: dict, varid: str) -> (Table, Container)
  - Build Unicode/characters overview Table and a tabs Container with FrequencyTables for characters, categories, scripts, blocks.

- render_generic(config: Settings, summary: dict) -> dict
  - Provide a minimal presentation payload for unsupported variable types (VariableInfo + small Table).

- render_complex(config: Settings, summary: dict) -> dict
  - Build presentation for complex-number variables: metadata, numeric metrics, and a complex-plane scatter Image.

- render_count(config: Settings, summary: dict) -> dict
  - Build presentation for count/numeric-like variables: info, numeric metrics, mini and full histograms, frequency and extreme-value tables.

- render_real(config: Settings, summary: dict) -> dict
  - (Numeric real renderer) Build presentation for real-valued numeric variables (mirrors render_count semantics for general numeric types).

- render_date(config: Settings, summary: dict) -> dict
  - Build presentation for date variables: info, min/max tables, mini/full histograms.

- render_path(config: Settings, summary: dict) -> dict
  - Augment categorical rendering with path-specific frequency tables (full path, stem, name, extension, parent, anchor) and an Overview table.

- render_file(config: Settings, summary: dict) -> dict
  - Populate file-specific UI (file-size histograms and date frequency tables) by calling render_path and appending a "File" tab.

- render_text(config: Settings, summary: dict) -> dict
  - Build presentation for text variables; conditionally delegates to render_categorical when redaction is enabled and otherwise adds words/length/characters blocks and wordclouds.

- render_timeseries(config: Settings, summary: dict) -> dict
  - Build presentation for time-series variables: stats tables, histograms, time-series plots, gap analysis, ACF/PACF, and frequency tables.

- _render_gap_tab(config: Settings, summary: dict) -> Container
  - Helper: assemble the "Gap analysis" container (gap statistics Table + gap plot Image) used by the timeseries renderer.

- render_url(config: Settings, summary: dict) -> dict
  - Build presentation for URL variables: full URL and per-part (scheme/netloc/path/query/fragment) frequency tables plus the standard top info block.

Mermaid dependency graph (internal relationships):
graph TD
  render_common --> render_count
  render_common --> render_real
  render_common --> render_boolean
  render_common --> render_categorical
  render_common --> render_url
  render_common --> render_path
  render_common --> render_date
  render_common --> render_timeseries
  render_categorical --> render_categorical_length
  render_categorical --> render_categorical_unicode
  render_categorical --> render_categorical_frequency
  render_text --> render_categorical
  render_path --> render_categorical
  render_file --> render_path
  render_timeseries --> _render_gap_tab

## Public API:
The symbols intended for use by the rest of the repository (signature, brief usage note).

- render_common(config: Settings, summary: dict) -> dict
  - Returns: dict with keys "freq_table_rows", "firstn_expanded", "lastn_expanded".
  - Usage note: called by other renderers as the bootstrap that converts freq/extreme helpers output into template rows.

- render_boolean(config: Settings, summary: dict) -> dict
  - Returns: template_variables dict containing "top" and "bottom".
  - Usage note: call for boolean-typed variable summaries. Expects render_common to supply freq_table_rows.

- render_categorical(config: Settings, summary: dict) -> dict
  - Returns: template_variables dict with "top" and "bottom" containers. Includes optional subsections (length, unicode, words) depending on config.
  - Usage note: main renderer for categorical/text-like columns. See component doc for required summary keys and optional keys.

- render_text(config: Settings, summary: dict) -> dict
  - Returns: template_variables dict similar to categorical; may delegate to render_categorical if redaction enabled.
  - Usage note: call when variable is classified as text. Honor config.vars.text.* flags.

- render_count / render_real (config: Settings, summary: dict) -> dict
  - Returns: template_variables with numeric summaries, mini/full histograms, frequency/extremes tables.
  - Usage note: call for count or real numeric columns; rely on render_common to populate frequency rows.

- render_date(config: Settings, summary: dict) -> dict
  - Returns: template_variables with date-specific histograms and min/max tables.
  - Usage note: histogram argument may be either a pair (edges, counts) or a list-of-pairs.

- render_url(config: Settings, summary: dict) -> dict
  - Returns: template_variables enriched with per-part freqtables and top info.
  - Usage note: expects keys like scheme_counts, netloc_counts, path_counts, query_counts, fragment_counts in summary.

- render_path(config: Settings, summary: dict) -> dict
  - Returns: template_variables mutated by appending a "Path" tab with Overview and per-part FrequencyTable items.
  - Usage note: calls render_categorical internally and mutates its return value.

- render_file(config: Settings, summary: dict) -> dict
  - Returns: template_variables mutated to include a "File" container (size histogram + date freq tables).
  - Usage note: delegates to render_path and then appends file-specific content.

- render_complex(config: Settings, summary: dict) -> dict
  - Returns: template_variables with a complex-plane scatter Image and relevant statistics tables.
  - Usage note: expects scatter data in summary["scatter_data"].

- render_timeseries(config: Settings, summary: dict) -> dict
  - Returns: template_variables including top info, quantile/descriptive stats, histograms, ts plots, gap analysis, acf/pacf, and frequency tables.
  - Usage note: summary must include series, histogram, freq_table_rows and other timeseries stats; see component doc for required keys.

- _get_n(value)
  - Returns: numeric total or list of totals.
  - Usage note: internal helper used by categorical/unicode renderers.

- render_categorical_length, render_categorical_unicode, render_categorical_frequency, _render_gap_tab
  - Usage note: helper entry points used by the categorical and timeseries renderers — consult their component docs before calling individually.

## Dependencies:
Internal (other repo modules/utilities used and why):
- ydata_profiling.report.structure.variables.render_common
  - Purpose: bootstrap frequency and extreme-value rows for all renderers.
- ydata_profiling.report.structure.variables.render_categorical_length, render_categorical_unicode, render_categorical_frequency, _get_n
  - Purpose: provide reusable presentation assembly for categorical subsections (length, unicode, unique stats) and count normalization.
- ydata_profiling.report.presentation.core (VariableInfo, Table, FrequencyTable, FrequencyTableSmall, Container, Image, HTML)
  - Purpose: construct presentation objects returned in the template_variables dict.
- ydata_profiling.report.visualisation.* helpers (histogram, mini_histogram, mini_ts_plot, plot_acf_pacf, plot_timeseries_gap_analysis, cat_frequency_plot, plot_word_cloud, scatter_complex)
  - Purpose: produce plot/figure payloads wrapped by Image items.
- Formatting helpers (fmt, fmt_percent, fmt_bytesize, fmt_numeric, fmt_timespan_timedelta, fmt_monotonic, help)
  - Purpose: format metric values and hints shown in Tables.
- freq_table, extreme_obs_table
  - Purpose: build row lists consumed by FrequencyTable and FrequencyTableSmall.

External (third-party libraries and why):
- pandas
  - Purpose: frequency inputs are typically pandas.Series/DataFrame and many helper functions expect pandas-like interfaces (.sum(), .value_counts(), indexing).
- matplotlib (and its backends)
  - Purpose: plot helpers produce Figures used by Image objects.
- numpy
  - Purpose: numerical arrays used by plotting helpers (histogram bins, counts).
Note: the module itself mostly calls internal helpers; concrete plotting and data-shaping use the third-party libraries inside those helpers.

## Constraints:
- Preconditions callers must respect:
  - config must be a fully populated Settings-like object exposing the nested attributes required by each renderer (examples: config.html.style, config.plot.image_format, config.vars.cat.*, config.vars.text.* flags, config.n_freq_table_max, config.n_extreme_obs, config.report.precision). Missing attributes raise AttributeError.
  - summary must be the profiler-produced per-variable summary dict with the keys required by the chosen renderer. Each component-level doc lists exact required keys; missing keys will cause KeyError.
  - For list-shaped fields (e.g., summary["value_counts_without_nan"] as a list), callers must ensure any parallel arrays (like config.html.style._labels) align in length to avoid IndexError.
  - render_common must be callable and return the expected "freq_table_rows" etc.; most renderers call render_common internally and depend on its outputs.

- Ordering / initialization:
  - No global initialization is required beyond providing a valid Settings object and well-formed summary dict.
  - Renderers are pure presentation assemblers: they call helpers that may allocate figures/images but do not perform file I/O themselves.

- Thread-safety:
  - Renderers are effectively pure functions that construct in-memory objects; they do not modify global module-level state. However, plotting helpers (matplotlib) may manipulate global matplotlib state unless those helpers handle figure contexts correctly. Callers rendering concurrently should ensure the plotting backends used by the visualisation helpers are thread-safe or serialize plotting calls.

- Other constraints:
  - Anchor ids are constructed by concatenating varid with fixed suffixes (e.g., f"{varid}bottom", f"{varid}common_values"); the module does not sanitize varid — callers should ensure varid values are safe for HTML anchor usage if necessary.
  - Many renderers set redact flags on FrequencyTable/ FrequencyTableSmall according to config; callers that alter config at runtime will affect output.

---

## Files

- [`render_boolean.py`](variables/render_boolean.md)
- [`render_categorical.py`](variables/render_categorical.md)
- [`render_common.py`](variables/render_common.md)
- [`render_complex.py`](variables/render_complex.md)
- [`render_count.py`](variables/render_count.md)
- [`render_date.py`](variables/render_date.md)
- [`render_file.py`](variables/render_file.md)
- [`render_generic.py`](variables/render_generic.md)
- [`render_image.py`](variables/render_image.md)
- [`render_path.py`](variables/render_path.md)
- [`render_real.py`](variables/render_real.md)
- [`render_text.py`](variables/render_text.md)
- [`render_timeseries.py`](variables/render_timeseries.md)
- [`render_url.py`](variables/render_url.md)

