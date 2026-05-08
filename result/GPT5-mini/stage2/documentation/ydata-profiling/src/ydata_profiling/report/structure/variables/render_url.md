# `render_url.py`

## `src.ydata_profiling.report.structure.variables.render_url.render_url` · *function*

## Summary:
Assembles template variables for rendering a URL-typed column in the HTML report by creating the necessary presentation objects (frequency tables, metadata table, info block) and returning a dictionary of template parts ready for rendering.

## Description:
This function converts a per-variable summary for a URL column into presentation-layer template variables. It:
- Calls render_common(config, summary) to obtain base template variables.
- Builds frequency-table data for the full URL and for each URL component (scheme, netloc, path, query, fragment) using freq_table(...).
- Instantiates FrequencyTable objects for the full URL and each component, places them inside a tabbed Container assigned to the "bottom" key.
- Creates a VariableInfo, a summary Table (distinct/missing/memory), and a single FrequencyTableSmall (from value_counts_without_nan) and places them together in a grid Container assigned to the "top" key.
- Returns the enriched template_variables dict for the rendering pipeline.

Known callers / usage context:
- No direct callers were present in the provided snippet. In the repository, this function is intended to be invoked by the variable-rendering stage of the report generator when a variable has been classified as URL-like (i.e., the per-variable dispatcher that selects a renderer based on variable type).

Reason for being a dedicated function:
- URL rendering requires assembling multiple component-specific frequency tables and UI elements; extracting that logic isolates URL-specific presentation concerns from generic renderers and keeps the rendering pipeline modular and testable.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Used attributes (must exist on the object):
            * config.n_freq_table_max (int): max rows to include in per-part frequency tables.
            * config.vars.cat.n_obs (int): max rows to include in the small frequency table for observed categories.
            * config.vars.cat.redact (bool): whether displayed frequency labels should be redacted.
            * config.html.style (opaque): passed to presentation constructors as the style parameter.
        - If any required attribute is missing, AttributeError will occur on access.

    summary (dict)
        - Type: dict
        - Required keys (exact names accessed in the code):
            * "varid" (str)
            * "varname" (str)
            * "n" (int)
            * "n_distinct" (int)
            * "p_distinct" (numeric)
            * "n_missing" (int)
            * "p_missing" (numeric)
            * "memory_size" (int)
            * "alert_fields" (iterable of str)
            * "alerts" (list or dict)
            * "description" (str)
            * "value_counts_without_nan" (mapping of value -> count)
            * "scheme_counts" (mapping)
            * "netloc_counts" (mapping)
            * "path_counts" (mapping)
            * "query_counts" (mapping)
            * "fragment_counts" (mapping)
        - Interdependencies:
            * render_common(config, summary) must return a dict containing the key "freq_table_rows" — this function reads template_variables["freq_table_rows"] to build the Full FrequencyTable.
        - Missing any required key will raise KeyError.

## Returns:
    dict: The template_variables dictionary (original dict returned by render_common augmented with additional keys). Keys that are added or updated:
        - "freqtable_scheme", "freqtable_netloc", "freqtable_path", "freqtable_query", "freqtable_fragment":
            * Each is the object returned by freq_table(freqtable=summary["{part}_counts"], n=summary["n"], max_number_to_print=config.n_freq_table_max).
            * These are the data used to populate corresponding FrequencyTable widgets.
        - "bottom":
            * A Container instance (sequence_type="tabs") containing FrequencyTable instances in this order:
              [Full, Scheme, Netloc, Path, Query, Fragment].
            * Each FrequencyTable is constructed from either template_variables["freq_table_rows"] (Full) or the corresponding "freqtable_{part}" entry.
        - "top":
            * A Container instance (sequence_type="grid") containing:
              - VariableInfo(summary["varid"], summary["varname"], "URL", summary["alerts"], summary["description"], style=config.html.style)
              - Table([...]) summarizing Distinct, Distinct (%), Missing, Missing (%), Memory size where values are formatted via fmt / fmt_percent / fmt_bytesize.
              - FrequencyTableSmall(freq_table(... from value_counts_without_nan), redact=config.vars.cat.redact)
        - All keys originally returned by render_common are preserved unless overwritten.

    Edge cases:
        - If any of the frequency mappings are empty, freq_table(...) will be called with an empty mapping; FrequencyTable objects for those parts will still be created and included in the containers.
        - If render_common does not provide "freq_table_rows", an exception will be raised when attempting to construct the Full FrequencyTable.

## Raises:
    KeyError:
        - If any required key is missing from summary (e.g., "varid", "scheme_counts", "value_counts_without_nan", "n", etc.), a KeyError will be raised at the point of access.

    AttributeError:
        - If config lacks expected attributes (e.g., config.n_freq_table_max or config.vars.cat.n_obs), AttributeError will occur on attribute access.

    TypeError / other exceptions:
        - Presentation constructors (FrequencyTable, Table, Container, VariableInfo, FrequencyTableSmall) or helper functions (freq_table, fmt, fmt_percent, fmt_bytesize) may raise TypeError or other exceptions if input types are incompatible; those errors propagate out of this function.

## Constraints:
    Preconditions:
        - config and summary must be well-formed as described in Args.
        - render_common(config, summary) must return a dict with "freq_table_rows".
    Postconditions:
        - Returned template_variables contains "top" and "bottom" Containers populated with presentation objects for rendering the URL variable's section.
        - No external I/O or global state is modified by this function itself.

## Side Effects:
    - The function itself performs no I/O, logging, or network access.
    - It constructs presentation-layer objects and calls helper/formatter functions; any side effects those helpers or constructors have are not caused directly by this function.

## Control Flow:
flowchart TD
    Start[Start: render_url(config, summary)]
    Start --> RC{Call render_common(config, summary)}
    RC --> TV[template_variables = render_common(...)]
    TV --> SetKeys[Define url parts keys = ["scheme","netloc","path","query","fragment"]]
    SetKeys --> Loop[Loop over each url_part]
    Loop --> FT[freq_table(summary["{part}_counts"], n=summary["n"], max_number_to_print=config.n_freq_table_max) -> template_variables["freqtable_{part}"]]
    FT --> LoopEnd[After loop completes]
    LoopEnd --> FullFT[Create Full FrequencyTable using template_variables["freq_table_rows"]]
    FullFT --> PartFTs[Create FrequencyTable objects for Scheme/Netloc/Path/Query/Fragment using template_variables["freqtable_{part}"]]
    PartFTs --> ItemsList[items = [Full, Scheme, Netloc, Path, Query, Fragment]]
    ItemsList --> BottomContainer[template_variables["bottom"] = Container(items, sequence_type="tabs", anchor_id=f"{varid}urlstats")]
    BottomContainer --> Info[Create VariableInfo(summary["varid"], summary["varname"], "URL", ...)]
    Info --> SummaryTable[Create Table with Distinct / Distinct (%) / Missing / Missing (%) / Memory size]
    SummaryTable --> SmallFT[Create FrequencyTableSmall(freq_table(summary["value_counts_without_nan"], n=summary["n"], max_number_to_print=config.vars.cat.n_obs), redact=config.vars.cat.redact)]
    SmallFT --> TopContainer[template_variables["top"] = Container([info, table, fqm], sequence_type="grid")]
    TopContainer --> Return[Return template_variables]
    Return --> End[End]

## Examples:
Illustrative usage (descriptive steps — constructors are invoked in real code):
1. Ensure config exposes:
    - config.n_freq_table_max = integer (e.g., 20)
    - config.vars.cat.n_obs = integer (e.g., 5)
    - config.vars.cat.redact = boolean
    - config.html.style = style object/value

2. Ensure summary contains required keys (varid, varname, n, n_distinct, p_distinct, n_missing, p_missing, memory_size, alert_fields, alerts, description, value_counts_without_nan, scheme_counts, netloc_counts, path_counts, query_counts, fragment_counts).

3. Call render_url(config, summary).

4. After the call:
    - template_vars["top"] is a grid Container with VariableInfo, a Table of summary stats, and a small frequency table for observed values.
    - template_vars["bottom"] is a tabs Container with detailed FrequencyTable views for Full and each URL component.

Notes:
- This function delegates formatting (fmt, fmt_percent, fmt_bytesize) and frequency table generation to helper functions; the concrete appearance and structure of returned presentation objects depend on those helpers and on config.html.style.

