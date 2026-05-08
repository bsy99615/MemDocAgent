# `render_generic.py`

## `src.ydata_profiling.report.structure.variables.render_generic.render_generic` · *function*

## Summary:
Create a small presentation payload for an "unsupported" variable: a VariableInfo + Table summary packaged into a top Container (grid) and an empty bottom slot. The result is a structural description (presentation objects) ready for downstream renderers.

## Description:
- Typical callers / context:
    - Report-building or presentation-factory code that assembles per-variable sections for output (HTML/JSON/spec) when a variable's type is not handled by specialized renderers. This function produces the canonical "generic" representation for variables with no special inspector.
- Why this is a separate function:
    - Encapsulates the rules for packaging descriptive metadata and a minimal summary table for unsupported variable types into the presentation-layer objects (VariableInfo, Table, HTML, Container). Extracting this logic avoids duplicating the same structure/format and centralizes how missing/memory statistics and alert flags are translated into presentation payloads.

## Args:
    config (Settings)
        - The global settings object from ydata_profiling.
        - Requirement: config.html must exist and config.html.style must be a Style object used for Table and VariableInfo style payloads. No further validation is performed here.
    summary (dict)
        - A mapping containing the variable's precomputed summary values. Required keys and expected types/semantics:
            * "varid" (str) — stable identifier/anchor for the variable block.
            * "varname" (str) — display name of the variable (column name).
            * "description" (str) — textual description or summary for the variable; may be empty.
            * "alerts" (List[Alert]) — list of Alert objects relevant to the variable (may be empty).
            * "n_missing" (int) — absolute count of missing values for the variable.
            * "p_missing" (float) — fractional missingness (commonly in 0..1).
            * "memory_size" (numeric) — memory footprint in bytes (int/float).
            * "alert_fields" (Iterable[str]) — collection of field-names used to determine whether a particular row should be marked as alerting (membership is tested using the row key strings "n_missing" and "p_missing").
        - Interdependencies:
            * The "alert" booleans for the table rows are computed by testing membership of the literal field names "n_missing" and "p_missing" in summary["alert_fields"].
        - Behavior when keys are missing:
            * Missing required keys will raise KeyError (see Raises).

## Returns:
    dict
    - A two-slot presentation payload with the following keys:
        * "top": Container instance (sequence_type="grid") whose content['items'] is the list: [VariableInfo, Table, HTML("")].
            - VariableInfo.content contains:
                - "anchor_id": summary["varid"]
                - "var_name": summary["varname"]
                - "description": summary["description"]
                - "var_type": the literal string "Unsupported"
                - "alerts": summary["alerts"] (same list reference)
                - "style": config.html.style
            - Table.content contains:
                - "rows": a sequence (list) of three row dictionaries with keys "name", "value", and "alert":
                    1) {"name": "Missing", "value": fmt(summary["n_missing"]), "alert": "n_missing" in summary["alert_fields"]}
                    2) {"name": "Missing (%)", "value": fmt_percent(summary["p_missing"]), "alert": "p_missing" in summary["alert_fields"]}
                    3) {"name": "Memory size", "value": fmt_bytesize(summary["memory_size"]), "alert": False}
                - "style": config.html.style
            - HTML("") is an HTML item wrapper containing an empty HTML string (content["html"] == "").
            - Note: VariableInfo, Table and HTML are structural renderable objects; they do not themselves produce final HTML until a concrete renderer's render() is invoked.
        * "bottom": None
    - The function always returns this dict shape on successful execution (no probabilistic returns).

## Raises:
    - KeyError:
        * If any required key (see Args) is absent from the summary dict (dictionary lookups like summary["varid"], summary["n_missing"], etc. are direct and will raise).
    - Any exception propagated from formatter helpers:
        * fmt(summary["n_missing"]) may raise exceptions if fmt's numeric formatting branch encounters an unexpected type/formatting error.
        * fmt_percent(summary["p_missing"]) may raise TypeError if p_missing is not numeric-like.
        * fmt_bytesize(summary["memory_size"]) may raise TypeError or ValueError if memory_size is not a numeric type compatible with abs(), division and the float format specifier.
    - Note: The function does not catch or wrap these exceptions; callers should validate inputs or handle exceptions as needed.

## Constraints:
- Preconditions:
    - config must be a Settings-like object with an html attribute exposing a style attribute (config.html.style).
    - summary must be a dict containing all required keys listed in Args.
    - summary["alert_fields"] must be an iterable supporting membership testing (the "in" operator).
- Postconditions:
    - On success, a dict with keys "top" (Container) and "bottom" (None) is returned.
    - The returned Container.content['items'] holds three presentation objects in the exact order: VariableInfo, Table, HTML (empty).
    - No mutation of config or summary is performed by this function (the returned objects reference some values from summary, e.g., the alerts list is reused by reference).

## Side Effects:
- This function performs no I/O, network calls, or global state mutation.
- It constructs presentation-layer objects and returns them; these objects hold references to provided inputs (e.g., alerts list and style), so subsequent mutation of those original objects by caller code will be visible through the returned objects.
- No files are written and no rendering is triggered here.

## Control Flow:
flowchart TD
    Start([Start]) --> ValidateInputs{summary has required keys?}
    ValidateInputs -- No --> KVError[KeyError raised]
    ValidateInputs -- Yes --> BuildInfo[Create VariableInfo with summary fields and config.html.style]
    BuildInfo --> BuildTable[Create Table with 3 rows:
      Missing -> fmt(n_missing), alert if "n_missing" in alert_fields;
      Missing (%) -> fmt_percent(p_missing), alert if "p_missing" in alert_fields;
      Memory size -> fmt_bytesize(memory_size), alert False]
    BuildTable --> CreateHTML[Create HTML("")]
    CreateHTML --> WrapContainer[Container([VariableInfo, Table, HTML("")], sequence_type="grid")]
    WrapContainer --> ReturnOut[Return {"top": Container, "bottom": None}]
    KVError --> End([End])
    ReturnOut --> End

## Examples:
- Conceptual example (inputs described, not runnable source here):
    - Given config where config.html.style is a Style object, and summary containing:
        * varid: "col_42"
        * varname: "col_42"
        * description: "No specialized renderer available for this type."
        * alerts: []  (empty list)
        * n_missing: 5
        * p_missing: 0.02
        * memory_size: 10240
        * alert_fields: ["p_missing"]
    - Outcome:
        * The VariableInfo will carry var_type "Unsupported", anchor_id "col_42", and the provided description/alerts/style.
        * Table rows will contain:
            - "Missing" with value fmt(5) (a formatted "5") and alert False (since "n_missing" not in alert_fields).
            - "Missing (%)" with value fmt_percent(0.02) ("2.0%") and alert True (because "p_missing" is in alert_fields).
            - "Memory size" with value fmt_bytesize(10240) (e.g., "10.0 KiB") and alert False.
        * The returned dict will have "top" set to a Container with those three items and "bottom" == None.

Notes:
- Because VariableInfo, Table and HTML are structural (render() is not implemented on these base objects), consumers of this function must pass the return value to the rendering layer or a concrete renderer that knows how to convert these items into final output.
- If callers need different row order, additional rows, or extra metadata, they must transform the returned objects (or build a custom renderer) before final rendering.

