# `render_boolean.py`

## `src.ydata_profiling.report.structure.variables.render_boolean.render_boolean` · *function*

## Summary:
Builds and returns the presentation template variables for a boolean variable: metadata block, metrics table, small frequency summary, a full frequency table tab, and optional categorical frequency plot(s).

## Description:
This function is invoked during the report rendering pipeline for boolean variables. A typical caller is the per-variable renderer dispatcher that selects render_boolean for variables identified as boolean after the profiling/summary collection step. It constructs presentation-layer objects (VariableInfo, Table, FrequencyTableSmall, FrequencyTable, Image, Container) and inserts them into the template_variables dict produced by render_common(config, summary).

Responsibility boundary:
- Encapsulates all presentation assembly logic for boolean variables (no data summarization or plotting internals).
- Leaves formatting and plotting implementations to the imported helpers (fmt, fmt_percent, fmt_bytesize, freq_table, cat_frequency_plot) and to the presentation classes (Container, Table, Image, etc.).
- Mutates the template_variables dict returned by render_common(config, summary) and returns it for downstream rendering.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Required attributes used:
            * vars.bool.n_obs (int): max items to show in the small frequency table (assigned to max_number_to_print)
            * plot.image_format (str): passed to Image(image_format=...)
            * plot.cat_freq.show (bool): whether to consider adding categorical frequency plot(s)
            * plot.cat_freq.max_unique (int): used with show to decide whether to add plots; plots are added only if show is True and max_unique > 0
            * html.style (object): style object passed to VariableInfo and Table; also expected to provide _labels (sequence of strings) when value_counts_without_nan is a list
        - No defaults; must be a populated Settings instance.

    summary (dict)
        - Type: dict
        - Required keys read by this function:
            * "varid" (str): base anchor id used to build anchors (e.g., f"{varid}frequency_table")
            * "varname" (str): displayed variable name
            * "description" (str): description text passed to VariableInfo
            * "alerts" (iterable): alerts passed to VariableInfo
            * "alert_fields" (iterable of str): used to set 'alert' booleans in the metrics table (checks membership of specific metric names)
            * "n_distinct" (int)
            * "p_distinct" (float, 0..1)
            * "n_missing" (int)
            * "p_missing" (float, 0..1)
            * "memory_size" (int, bytes)
            * "value_counts_without_nan": either
                - a list of frequency-series objects (one per plot) OR
                - a single frequency-series object (for one plot)
              The items are forwarded to cat_frequency_plot or to freq_table as appropriate.
            * "n" (int): total number of observations passed to freq_table
        - Note: this function relies on render_common(config, summary) to provide template_variables that include "freq_table_rows"; render_common must populate "freq_table_rows" prior to this function using the same summary.

Interdependencies:
- If summary["value_counts_without_nan"] is a list, its length is expected to match (or be compatible with) len(config.html.style._labels). The code indexes config.html.style._labels[idx] for each series; if the label list is shorter, an IndexError can occur.

## Returns:
    dict
        - The function returns the same template_variables dict produced by render_common(config, summary), after adding:
            * "top": Container([VariableInfo(...), Table(...), FrequencyTableSmall(...)], sequence_type="grid")
            * "bottom": Container(items, sequence_type="tabs", anchor_id=f"{varid}bottom")
              where items always begins with a FrequencyTable rendered from template_variables["freq_table_rows"], and may include plot Image(s) depending on config and summary.
        - The returned dict contains presentation objects (not primitive JSON): VariableInfo, Table, FrequencyTableSmall, FrequencyTable, Image, Container.

Possible return shapes (examples):
- Minimal (plots disabled): "top" grid + "bottom" tabs with a single FrequencyTable.
- With plots and single-series value_counts_without_nan: "bottom" tabs with FrequencyTable and one Image.
- With plots and list-series: "bottom" tabs with FrequencyTable and a Container(batch_grid) holding multiple Image objects.

## Raises:
    KeyError
        - Accessing missing summary keys (e.g., "varid", "n_distinct", "value_counts_without_nan") or missing template_variables["freq_table_rows"] (if render_common omitted it) will raise KeyError.

    AttributeError
        - If config lacks expected nested attributes (e.g., config.plot, config.html), attribute access will raise AttributeError.

    IndexError
        - If summary["value_counts_without_nan"] is a list and config.html.style._labels is shorter than that list, the expression config.html.style._labels[idx] will raise IndexError.

    TypeError
        - If summary["value_counts_without_nan"] is of an unexpected type for cat_frequency_plot or freq_table, or if config.html.style._labels is not subscriptable, TypeError may be raised by underlying calls.

Note: The function does not explicitly catch any exceptions; errors propagate to callers.

## Constraints:
    Preconditions:
        - config and summary are non-null and populated with the attributes/keys listed above.
        - render_common(config, summary) returns a dict that includes "freq_table_rows" (used to build the full FrequencyTable).
    Postconditions:
        - The returned dict contains "top" and "bottom" entries with presentation objects ready for the templating/rendering stage.
        - No global state is modified by the function itself.

## Side Effects:
    - This function performs no I/O (no filesystem, network, or stdout writes).
    - It mutates the dict returned by render_common(config, summary) by setting "top" and "bottom" keys.
    - Indirect side effects may occur later when rendering Image objects or when plotting functions (cat_frequency_plot) are executed by downstream components.

## Control Flow:
flowchart TD
    Start[Start: render_boolean(config, summary) called]
    Start --> var_setup[Read varid, n_obs_bool, image_format]
    var_setup --> template_vars[template_variables = render_common(config, summary)]
    template_vars --> make_info[Create VariableInfo(anchor_id=summary["varid"], alerts=summary["alerts"], var_type="Boolean", var_name=summary["varname"], description=summary["description"], style=config.html.style)]
    make_info --> make_table[Create Table with rows:
        - Distinct: value=fmt(summary["n_distinct"]), alert = "n_distinct" in summary["alert_fields"]
        - Distinct (%): value=fmt_percent(summary["p_distinct"]), alert = "p_distinct" in summary["alert_fields"]
        - Missing: value=fmt(summary["n_missing"]), alert = "n_missing" in summary["alert_fields"]
        - Missing (%): value=fmt_percent(summary["p_missing"]), alert = "p_missing" in summary["alert_fields"]
        - Memory size: value=fmt_bytesize(summary["memory_size"]), alert=False]
    make_table --> make_fqm[Create FrequencyTableSmall(freq_table(freqtable=summary["value_counts_without_nan"], n=summary["n"], max_number_to_print=n_obs_bool), redact=False)]
    make_fqm --> set_top[Set template_variables["top"] = Container([info, table, fqm], sequence_type="grid")]
    set_top --> items_init[items = [ FrequencyTable(template_variables["freq_table_rows"], name="Common Values (Table)", anchor_id=f"{varid}frequency_table", redact=False) ]]
    items_init --> show_check[Check show = config.plot.cat_freq.show and max_unique = config.plot.cat_freq.max_unique]
    show_check -->|show is False OR max_unique <= 0| set_bottom_no_plots[Set template_variables["bottom"] = Container(items, sequence_type="tabs", anchor_id=f"{varid}bottom") and RETURN]
    show_check -->|show True and max_unique > 0| plot_type_check[Is summary["value_counts_without_nan"] a list?]
    plot_type_check -->|Yes (list)| batch_images[For each idx, s in enumerate(summary["value_counts_without_nan"]): create Image(cat_frequency_plot(config, s), image_format=image_format, alt=config.html.style._labels[idx], name=config.html.style._labels[idx], anchor_id=f"{varid}cat_frequency_plot_{idx}"); wrap images in Container(sequence_type="batch_grid", batch_size=len(config.html.style._labels))]
    plot_type_check -->|No (single series)| single_image[Create Image(cat_frequency_plot(config, summary["value_counts_without_nan"]), image_format=image_format, alt="Common Values (Plot)", name="Common Values (Plot)", anchor_id=f"{varid}cat_frequency_plot")]
    batch_images --> append_and_return[Append Container to items; set template_variables["bottom"] and RETURN]
    single_image --> append_and_return

## Examples:
Example 1 — standard happy path (conceptual):
    - Preconditions: render pipeline has produced a boolean summary dict with all required keys and Settings config has plots enabled.
    - Call render_boolean(config, summary).
    - Result: template_variables with "top" (info, metrics, small freq) and "bottom" (tabs containing full frequency table and plot(s)).

Example 2 — plots disabled:
    - If config.plot.cat_freq.show is False or config.plot.cat_freq.max_unique <= 0, the returned template_variables["bottom"] contains only the FrequencyTable (no plot Image objects).

Example 3 — caution with multiple plot series:
    - If summary["value_counts_without_nan"] is a list of length L, the function will attempt to use config.html.style._labels[idx] for idx in 0..L-1. Ensure config.html.style._labels has at least L labels to avoid IndexError.

Implementation notes for reimplementation:
    - Use render_common(config, summary) to bootstrap template_variables; mutate it by adding "top" and "bottom".
    - Use fmt, fmt_percent, fmt_bytesize for formatting numeric metrics.
    - Use freq_table(..., max_number_to_print=config.vars.bool.n_obs) as input to FrequencyTableSmall.
    - Use cat_frequency_plot(config, series) to obtain the plotted image content for each series or the single series; pass config.plot.image_format to the Image constructor.
    - Always set redact=False on FrequencyTableSmall and FrequencyTable created here to ensure values are shown.

