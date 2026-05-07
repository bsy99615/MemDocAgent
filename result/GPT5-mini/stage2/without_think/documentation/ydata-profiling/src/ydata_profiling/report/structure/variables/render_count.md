# `render_count.py`

## `src.ydata_profiling.report.structure.variables.render_count.render_count` · *function*

## Summary:
Compose and return presentation-ready template variables for a numeric/count variable by taking a computed summary and producing formatted tables, variable header info, and histogram images inserted into the template dictionary used by the report renderer.

## Description:
This function transforms a per-variable summary dict into presentation objects suitable for inclusion in the final report. It:
- Starts from a base template dict from render_common(config, summary) and uses its outputs to create FrequencyTable and extreme-value tables.
- Builds a VariableInfo header and two Table objects (distinct/missing metrics and numeric distribution metrics) using the report formatters.
- Generates a mini histogram and a full histogram (via mini_histogram and histogram) and embeds them in Image presentation objects.
- Arranges the created objects into two main Containers placed under template_variables["top"] and template_variables["bottom"].

Typical invocation context:
- Called by the variable-level rendering pipeline in the report generator when rendering a numeric or count-type variable. The function assumes the summary dict is already computed by the profiling/statistics stage and that render_common produces frequency/extreme-value rows to be displayed.

Why separated:
- Keeps UI composition and formatting concerns separate from statistical computation. This function centralizes presentation layout for numeric/count variables and reuses formatters and plotting utilities.

## Args:
    config (Settings):
        - Type: Settings (or an object with the same attribute structure).
        - Accessed attributes (exactly):
            * config.plot.image_format (str): passed to Image(image_format=...).
            * config.html.style (any): passed as style=config.html.style to Table and VariableInfo constructors.
            * config.report.precision (int): passed as precision to fmt_numeric for numeric formatting.
            * config.n_extreme_obs (int): used in the display name of the extreme-value FrequencyTables (label only).
        - Behavior: Attributes are accessed directly; missing nested attributes raise AttributeError.

    summary (dict):
        - Type: dict containing pre-computed values for this variable.
        - Required keys (all read directly and will raise KeyError if absent):
            * "varid" (str) — used as anchor_id for the bottom Container and as VariableInfo id.
            * "varname" (str) — used in VariableInfo.
            * "alerts" (list) — passed to VariableInfo.
            * "description" (str) — passed to VariableInfo.
            * "n_distinct" (int) — shown in table1 via fmt.
            * "p_distinct" (float) — shown in table1 via fmt_percent.
            * "n_missing" (int) — shown in table1 via fmt.
            * "p_missing" (float) — shown in table1 via fmt_percent.
            * "mean" (numeric) — shown in table2 via fmt_numeric.
            * "min" (numeric) — shown in table2 via fmt_numeric.
            * "max" (numeric) — shown in table2 via fmt_numeric.
            * "n_zeros" (int) — shown in table2 via fmt.
            * "p_zeros" (float) — shown in table2 via fmt_percent.
            * "memory_size" (int) — shown in table2 via fmt_bytesize.
            * "histogram" (tuple/list of length >= 2) — passed as *summary["histogram"] to plotting functions; summary["histogram"][1] must support len() so bins can be computed.
        - Interdependencies:
            * The formatters (fmt, fmt_numeric, fmt_percent, fmt_bytesize) determine how non-numeric or missing numeric values are displayed; this function delegates formatting to those helpers.

## Returns:
    dict: The template_variables dictionary originally returned by render_common(config, summary), updated with the following keys (added/overwritten):
        - "top" (Container):
            * sequence_type: "grid"
            * contents: [VariableInfo, Table (table1), Table (table2), Image (mini_histo)]
            * VariableInfo built with:
                - id: summary["varid"]
                - name: summary["varname"]
                - type: literal string "Real number (&Ropf; / &Ropf;<sub>&ge;0</sub>)"
                - alerts: summary["alerts"]
                - description: summary["description"]
                - style: config.html.style
            * table1 entries (each dict has keys "name", "value", "alert"):
                - "Distinct": value=fmt(summary["n_distinct"])
                - "Distinct (%)": value=fmt_percent(summary["p_distinct"])
                - "Missing": value=fmt(summary["n_missing"])
                - "Missing (%)": value=fmt_percent(summary["p_missing"])
              table1 created with style=config.html.style
            * table2 entries:
                - "Mean": fmt_numeric(summary["mean"], precision=config.report.precision)
                - "Minimum": fmt_numeric(summary["min"], precision=config.report.precision)
                - "Maximum": fmt_numeric(summary["max"], precision=config.report.precision)
                - "Zeros": fmt(summary["n_zeros"])
                - "Zeros (%)": fmt_percent(summary["p_zeros"])
                - "Memory size": fmt_bytesize(summary["memory_size"])
              table2 created with style=config.html.style
            * mini_histo: Image of mini_histogram(config, *summary["histogram"]), image_format=config.plot.image_format, alt="Mini histogram"

        - "bottom" (Container):
            * sequence_type: "tabs"
            * anchor_id: summary["varid"]
            * contents: [
                Container(seqs, sequence_type="tabs", name="Histogram(s)", anchor_id="histograms"),
                FrequencyTable(template_variables["freq_table_rows"], name="Common values", anchor_id="common_values", redact=False),
                Container(evs_contents, sequence_type="tabs", name="Extreme values", anchor_id="extreme_values")
              ]
            * seqs is a list containing one Image created from histogram(config, *summary["histogram"]) with:
                - image_format=config.plot.image_format
                - alt="Histogram"
                - caption set exactly to "<strong>Histogram with fixed size bins</strong> (bins={len(summary['histogram'][1]) - 1})"
                - name="Histogram"
                - anchor_id="histogram"
            * evs_contents is:
                - FrequencyTable(template_variables["firstn_expanded"], name=f"Minimum {config.n_extreme_obs} values", anchor_id="firstn", redact=False)
                - FrequencyTable(template_variables["lastn_expanded"], name=f"Maximum {config.n_extreme_obs} values", anchor_id="lastn", redact=False)

    Notes on return contents and types:
        - template_variables must contain "freq_table_rows", "firstn_expanded", and "lastn_expanded" (populated by render_common) because those are used directly to construct FrequencyTable instances.
        - The function always returns the (possibly modified) template_variables dict on successful completion.

## Raises:
    - KeyError:
        - If any required key from summary is missing (explicit keys listed above).
        - If render_common(config, summary) returns a dict missing "freq_table_rows", "firstn_expanded", or "lastn_expanded".
    - AttributeError:
        - If required attributes are missing on config (plot, html, report nested attributes and their sub-attributes).
    - Any exception raised by called helpers:
        - fmt, fmt_numeric, fmt_percent, fmt_bytesize may raise on invalid input.
        - VariableInfo, Table, Image, Container, FrequencyTable constructors may raise if passed invalid types.
        - mini_histogram or histogram may raise if the histogram input is malformed.
      Such exceptions propagate unchanged.

## Constraints:
    Preconditions:
        - render_common(config, summary) must be callable and must return a dict with the keys: "freq_table_rows", "firstn_expanded", "lastn_expanded".
        - summary["histogram"] must be an indexable sequence whose second element supports len(); otherwise the caption computation and plotting calls may fail.
    Postconditions:
        - template_variables contains "top" and "bottom" keys populated as described.
        - No mutation of other template_variables keys is performed beyond adding/overwriting "top" and "bottom".

## Side Effects:
    - No file, network, or stdout/stderr I/O performed by this function directly.
    - Constructs presentation objects (VariableInfo, Table, Image, Container, FrequencyTable) and calls plotting helpers (mini_histogram, histogram); any side effects of those helpers will occur.
    - No global state is modified by this function.

## Control Flow:
flowchart TD
    Start --> CallRenderCommon[Call render_common(config, summary) -> template_variables]
    CallRenderCommon --> ReadConfig[Read config.plot.image_format, config.html.style, config.report.precision, config.n_extreme_obs]
    ReadConfig --> ValidateHistogram[Ensure summary["histogram"] has at least two elements]
    ValidateHistogram --> BuildInfo[Create VariableInfo(summary["varid"], summary["varname"], type_string, summary["alerts"], summary["description"], style=config.html.style)]
    BuildInfo --> BuildTable1[Create Table1 (Distinct / Missing) using fmt, fmt_percent]
    BuildTable1 --> BuildTable2[Create Table2 (Mean/Min/Max/Zeros/Memory) using fmt_numeric, fmt, fmt_percent, fmt_bytesize]
    BuildTable2 --> BuildMiniHisto[Call mini_histogram(config, *summary["histogram"]) -> Image mini_histo]
    BuildMiniHisto --> SetTop[Set template_variables["top"] = Container([info, table1, table2, mini_histo], sequence_type="grid")]
    SetTop --> BuildFullHisto[Call histogram(config, *summary["histogram"]) -> Image hist_img]
    BuildFullHisto --> MakeSeqs[seqs = [hist_img] with caption "<strong>Histogram with fixed size bins</strong> (bins={len(summary['histogram'][1]) - 1})"]
    MakeSeqs --> MakeFreqTable[Create FrequencyTable using template_variables["freq_table_rows"], name="Common values", anchor_id="common_values", redact=False]
    MakeFreqTable --> MakeEvs[Create evs Container with FrequencyTable(template_variables["firstn_expanded"], name=f"Minimum {config.n_extreme_obs} values", anchor_id="firstn", redact=False) and FrequencyTable(template_variables["lastn_expanded"], name=f"Maximum {config.n_extreme_obs} values", anchor_id="lastn", redact=False)]
    MakeEvs --> SetBottom[Set template_variables["bottom"] = Container([ Container(seqs,... anchor_id="histograms"), fq, evs ], sequence_type="tabs", anchor_id=summary["varid"])]
    SetBottom --> Return[Return template_variables]
    CallRenderCommon -->|missing keys| RaiseKeyError[KeyError]
    BuildMiniHisto -->|plot helper error| PropagateError[Propagate plotting/formatting error]
    BuildTable2 -->|formatter error| PropagateError

## Examples:
1) Concrete single-variable example (illustrative values and resulting structure):
    - Inputs:
        * config.plot.image_format = "png"
        * config.html.style = {"table_class": "pandas"}
        * config.report.precision = 2
        * config.n_extreme_obs = 3
        * summary = {
            "varid": "var_1",
            "varname": "count_col",
            "alerts": [],
            "description": "Number of items per row",
            "n_distinct": 5,
            "p_distinct": 0.05,
            "n_missing": 0,
            "p_missing": 0.0,
            "mean": 12.3456,
            "min": 0.0,
            "max": 100.0,
            "n_zeros": 10,
            "p_zeros": 0.10,
            "memory_size": 8000,
            "histogram": ([0,10,20,30], [0,10,20,30,40])  # (counts, bin_edges)
          }
    - Expected behavior:
        * render_common(config, summary) returns template_variables with keys:
            - "freq_table_rows" (e.g., [[{"label":"0","count":10,...}, ...]])
            - "firstn_expanded" (e.g., [[... top rows ...]])
            - "lastn_expanded" (e.g., [[... bottom rows ...]])
        * After render_count returns, template_variables contains:
            - "top": Container([...]) where:
                + VariableInfo.id == "var_1"
                + table1 shows "Distinct" -> fmt(5), "Distinct (%)" -> fmt_percent(0.05), etc.
                + table2 shows mean formatted to 2 decimal places (fmt_numeric(12.3456, precision=2) -> e.g., "12.35")
                + mini_histo is an Image with image_format "png" and alt "Mini histogram"
            - "bottom": Container([...]) where:
                + The histogram Image caption is exactly "<strong>Histogram with fixed size bins</strong> (bins={len(summary['histogram'][1]) - 1})" — for the example len(bin_edges)=5 so caption will read "... (bins=4)"
                + FrequencyTable for common values uses template_variables["freq_table_rows"] and anchor_id "common_values" with redact=False
                + Two FrequencyTables for extremes under anchor_ids "firstn" and "lastn", names include config.n_extreme_obs (3), redact=False

2) Defensive pre-call check pattern (descriptive):
    - Validate presence of required summary keys and config attributes before invoking render_count to convert KeyError/AttributeError into clearer user-facing error messages or to provide fallbacks (for example, populate missing histogram with empty arrays to avoid plot errors).

Usage note:
- This function is presentation-only: do not expect it to compute statistics or frequencies — pass a fully populated summary produced by the profiling/statistics stage (or ensure render_common and summary produce the required keys).

