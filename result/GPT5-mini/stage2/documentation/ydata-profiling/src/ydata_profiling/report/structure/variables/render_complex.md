# `render_complex.py`

## `src.ydata_profiling.report.structure.variables.render_complex.render_complex` · *function*

## Summary:
Constructs presentation-ready components for a complex-valued variable summary: a top grid with variable metadata and two statistic tables, and a bottom tabbed pane containing a complex-plane scatter image. Returns a template-variables dictionary suitable for the report rendering pipeline.

## Description:
This function is part of the variable-rendering stage in the report generation pipeline. It converts a pre-computed statistical summary for a complex-valued variable into presentation objects (info card, tables, placeholder, image container) that templates expect.

Known callers and context:
- Called by higher-level variable rendering/orchestration code in the report generation pipeline when a variable has been classified as complex (e.g., a renderer-dispatch function that selects render_complex for complex dtype). Typical trigger: building the per-variable section of an HTML report after the summary statistics for each variable have been computed.
- The function is intentionally isolated to keep presentation assembly separate from summary computation and plotting logic. This separation enforces a responsibility boundary: assemble presentation objects given summary data and config, but do not compute statistics or generate layout templates.

## Args:
    config (Settings):
        - An instance of the project's Settings/configuration object.
        - Required attributes used by this function:
            * config.plot.image_format (str): image output format passed to the Image constructor (e.g., "png", "svg").
            * config.html.style (dict or style-type expected by presentation classes): styling passed to VariableInfo and Table constructors.
            * config.report.precision (int): number of decimal places used by fmt_numeric for numeric formatting.
        - Preconditions: config must provide these attributes; missing attributes will raise AttributeError at runtime.

    summary (dict):
        - A dictionary with pre-computed statistics and metadata for a single complex-valued variable.
        - Required keys (names, expected types, and meaning):
            * "varid" (str): unique identifier for the variable (used for anchors).
            * "varname" (str): human-readable variable name.
            * "alerts" (list[str] or similar): any alert messages for this variable.
            * "description" (str): textual description of the variable (may be empty).
            * "n_distinct" (int): number of distinct values.
            * "p_distinct" (float): proportion distinct (0.0 - 1.0).
            * "n_missing" (int): count of missing values.
            * "p_missing" (float): proportion missing (0.0 - 1.0).
            * "memory_size" (int): size in bytes used by this variable (for bytesize formatting).
            * "mean" (number or complex): mean of values (may be complex-like representation expected by fmt_numeric).
            * "min" (number or complex): minimum value.
            * "max" (number or complex): maximum value.
            * "n_zeros" (int): number of zero-valued entries.
            * "p_zeros" (float): proportion zeros (0.0 - 1.0).
            * "scatter_data" (any): plotting data expected by scatter_complex(config, scatter_data).
        - Interdependencies:
            * Numeric-formatting calls use config.report.precision; if numeric values are None or not numeric, fmt_numeric may return a placeholder string or raise an error depending on its implementation.
            * "scatter_data" must be in the shape and format expected by the scatter_complex plotting helper.

## Returns:
    dict:
        - A dictionary with exactly two keys used by report templates:
            * "top": a Container instance (sequence_type="grid") containing, in order:
                - VariableInfo object (constructed with varid, varname, fixed title "Complex number (&Copf;)", alerts, description, style=config.html.style)
                - Table object summarizing distinct/missing/memory-size metrics
                - Table object summarizing numeric metrics (mean, min, max, zeros)
                - HTML placeholder object (empty)
            * "bottom": a Container instance (sequence_type="tabs", anchor_id=summary["varid"]) containing a single Image item:
                - Image contains the output of scatter_complex(config, summary["scatter_data"]), uses image_format from config.plot.image_format, alt text "Scatterplot", caption "Scatterplot in the complex plane", name "Scatter", and anchor_id f"{varid}scatter".
        - The returned objects are presentation-layer objects (VariableInfo, Table, Container, HTML, Image). The exact runtime types and attributes depend on the presentation core implementation; the contract is that templates can consume these objects to render the section.

## Raises:
    - KeyError: if any of the required keys listed under Args->summary are missing from the summary dict (the function indexes summary[...] directly).
    - AttributeError: if config lacks required attributes (config.plot.image_format, config.html.style, config.report.precision).
    - Propagated exceptions from called helpers:
        * Any exception raised by fmt, fmt_bytesize, fmt_numeric, fmt_percent if given invalid inputs.
        * Any exception raised by scatter_complex(config, scatter_data) if scatter data are invalid.
        * Any exception raised by the presentation constructors (VariableInfo, Table, Container, HTML, Image) when given invalid parameters.
    - The function itself does not catch exceptions: all such errors propagate to the caller.

## Constraints:
    Preconditions:
        - summary contains all required keys (see Args) and values are of expected types or at least compatible with the formatters and scatter_complex.
        - config contains the attributes used by the function.
        - Presentation constructors and helper formatters are available and behave as expected.

    Postconditions:
        - If no exception is raised, the function returns a dict with keys "top" and "bottom" as described above.
        - No mutation of input summary or config is performed by this function (it constructs new presentation objects only).

## Side Effects:
    - No I/O performed by this function itself (no file or network operations).
    - Calls scatter_complex(config, summary["scatter_data"]) which may create an in-memory image object or plot data; any I/O performed by scatter_complex is the responsibility of that function and is not performed here.
    - No modification of global variables, databases, or caches within this function.
    - Constructs presentation objects (VariableInfo, Table, Container, HTML, Image) which may hold references to data; these are returned to the caller.

## Control Flow:
flowchart TD
    Start --> ExtractVaridAndInit
    ExtractVaridAndInit --> CreateVariableInfo
    CreateVariableInfo --> BuildTable1
    BuildTable1 --> BuildTable2
    BuildTable2 --> CreatePlaceholder
    CreatePlaceholder --> MakeTopContainer
    MakeTopContainer --> PrepareScatter
    PrepareScatter --> CreateImageItem
    CreateImageItem --> MakeBottomContainer
    MakeBottomContainer --> AssembleTemplateVariables
    AssembleTemplateVariables --> Return
    Start[Start] -->|read config.plot.image_format & summary| ExtractVaridAndInit[Extract varid and init template_variables]
    MakeTopContainer -->|items: info, table1,table2,placeholder| MakeTopContainer
    MakeBottomContainer -->|items: [Image(scatter_complex(...))]| AssembleTemplateVariables

## Examples:
Example 1 — typical usage (happy path):
    # pseudo-code (not importing real classes)
    config = Settings(...)  # must provide plot.image_format, html.style, report.precision
    summary = {
        "varid": "var_3",
        "varname": "complex_feature",
        "alerts": [],
        "description": "Measured complex-valued feature in experiments",
        "n_distinct": 120,
        "p_distinct": 0.95,
        "n_missing": 5,
        "p_missing": 0.02,
        "memory_size": 8192,
        "mean": 1.23+0.45j,
        "min": -2.0+0.0j,
        "max": 3.5+1.2j,
        "n_zeros": 7,
        "p_zeros": 0.01,
        "scatter_data": <plotting-structure-expected-by-scatter_complex>,
    }
    template_vars = render_complex(config, summary)
    # template_vars["top"] is a Container (grid) with VariableInfo and two Tables
    # template_vars["bottom"] is a Container (tabs) with an Image for the scatter

Example 2 — defensive usage with error handling:
    try:
        template_vars = render_complex(config, summary)
    except KeyError as e:
        # summary was missing a required key; handle or re-run summary computation
        missing_key = e.args[0]
        logger.error("Missing summary key: %s", missing_key)
        raise
    except Exception as e:
        # Any formatting/plotting/presentation error propagated
        logger.exception("Failed to render complex variable section")
        raise

Notes for implementers:
    - Ensure the required summary keys are produced by the summary/aggregation stage before calling this function.
    - Keep formatting consistent with other variable renderers by using the same fmt, fmt_numeric, fmt_percent, and fmt_bytesize helpers.
    - Anchor IDs: the Image anchor_id is built as f"{varid}scatter" and the bottom Container uses anchor_id summary["varid"]; ensure these are unique within the report scope.

