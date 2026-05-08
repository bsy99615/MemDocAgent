# `render_path.py`

## `src.ydata_profiling.report.structure.variables.render_path.render_path` · *function*

## Summary:
Renders path-specific profiling sections for a variable by building frequency tables and an "Overview" table, and returns a template dictionary (report fragment) augmented with path-related presentation components.

## Description:
This function is used during the report-generation stage of the profiling pipeline when a variable has been identified as a path-like categorical variable. Typical callers and context:
- The variable rendering pipeline that assembles the full variable report (called when variable type is "path").
- Called after summary statistics for the variable have been computed and a summary dict (see Args) is available.
Trigger condition: invoked when the profiling flow decides to render a "Path" variable section (path-specific structure rendering).

Reason for extraction:
- Encapsulates the path-specific rendering logic (construction of frequency tables for different path parts and the overview table) separately from generic categorical rendering. This keeps responsibilities separated: generic categorical rendering lives in render_categorical, while render_path handles the path-specific augmentation and layout assembly.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Required attributes used:
            * n_freq_table_max (int) - maximum number of frequency rows to display per freq table.
            * vars.cat.redact (bool) - whether frequency tables should redact values.
            * report.precision (int) - numeric formatting precision for numeric summary values.
            * html.style (str or object) - style used when creating summary Table.
        - No default; must be a Settings instance (or object with the listed attributes).

    summary (dict):
        - Type: dict
        - Required keys (must be present; otherwise the function will raise KeyError):
            * "varid" (str): a unique identifier used to build anchor ids.
            * "n" (int): total number of observations (used by freq_table).
            * "common_prefix" (str or None): computed common path prefix.
            * "n_stem_unique" (int): count of unique stems.
            * "n_name_unique" (int): count of unique names.
            * "n_suffix_unique" (int): count of unique suffixes/extensions.
            * "n_parent_unique" (int): count of unique parent directories.
            * "n_anchor_unique" (int): count of unique anchors.
            * For each path part in ["name","parent","suffix","stem","anchor"], there must be a "{part}_counts" key whose value is a frequency table-like structure accepted by freq_table (commonly a pandas Series or dict mapping value -> count).
        - Interdependencies:
            * The function forwards summary and parts of its content to render_categorical and to freq_table; render_categorical is expected to return a template_variables dict containing at least "top", "bottom", and "freq_table_rows" keys or similar structure used below.

## Returns:
    dict: template_variables
    - This is the template dictionary returned by render_categorical(config, summary) but augmented and mutated in-place:
        * Added keys:
            - "freqtable_name", "freqtable_parent", "freqtable_suffix", "freqtable_stem", "freqtable_anchor":
                Each contains the result of freq_table(...) for the corresponding part (the structure produced by the project's frequency table utility).
        * Modified contents:
            - template_variables["top"].content["items"][0].content["var_type"] is set to the literal "Path".
            - template_variables["bottom"].content["items"] has an appended Container named "Path" (a tab container) which contains:
                - an "Overview" Container (with a Table of summary statistics),
                - FrequencyTable items for "Full", "Stem", "Name", "Extension", "Parent", "Anchor".
        * The function returns the same template_variables dict (the original object mutated).

Possible edge-case return values:
- If render_categorical returns a template_variables structure that does not contain the expected nested keys ("top", "bottom", etc.), the function will raise KeyError when trying to access or mutate those keys (see Raises).

## Raises:
    KeyError:
        - If any required key in summary is missing (e.g., "varid", "n", "common_prefix", "n_stem_unique", "name_counts", etc.), a KeyError will be raised at the access site.
        - If render_categorical(config, summary) returns a dict that does not contain the nested keys used by this function (notably "top" or "bottom"), the code that mutates template_variables["top"].content or appends to template_variables["bottom"].content["items"] will raise a KeyError.
    AttributeError / TypeError:
        - If config lacks the required attributes (n_freq_table_max, vars.cat.redact, report.precision, html.style) attribute access may raise AttributeError.
        - If objects returned by render_categorical or freq_table do not implement expected attributes or indexing, access may cause TypeError/AttributeError.

## Constraints:
Preconditions:
- config must be a Settings-like object with attributes n_freq_table_max (int), vars.cat.redact (bool), report.precision (int), and html.style.
- summary must be a dict containing all keys listed in Args.
- render_categorical(config, summary) must return a dict with nested presentation structure:
    * template_variables["top"].content["items"][0].content exists and is a mutable mapping allowing assignment to "var_type".
    * template_variables["bottom"].content["items"] exists and supports .append(...).
    * template_variables["freq_table_rows"] must be present for the "Full" FrequencyTable.
- freq_table must accept the provided summary["{part}_counts"] and return a frequency-table representation compatible with FrequencyTable and the report presentation layer.

Postconditions:
- The returned template_variables:
    * has additional "freqtable_{part}" keys for each path part,
    * has "top" variable type set to "Path",
    * has a new "Path" Container appended under template_variables["bottom"].content["items"] that aggregates the overview and frequency tables for path parts.

## Side Effects:
- Mutates the dict returned by render_categorical(config, summary) in place (adds keys and appends the path Container to template_variables["bottom"].content["items"]).
- Instantiates presentation objects (Container, Table, FrequencyTable); these are in-memory objects representing report components and do not perform I/O by themselves.
- No network, file, or external database I/O is performed by this function.

## Control Flow:
flowchart TD
    A[Start: render_path(config, summary)] --> B[Extract varid, n_freq_table_max, redact]
    B --> C[Call render_categorical(config, summary) -> template_variables]
    C --> D[For each path_part in [name,parent,suffix,stem,anchor]]
    D --> E[freq_table = freq_table(summary[f"{path_part}_counts"], n=summary["n"], max_number_to_print=n_freq_table_max)]
    E --> F[Assign template_variables["freqtable_{path_part}"] = freq_table]
    F --> G[Set template_variables["top"].content["items"][0].content["var_type"] = "Path"]
    G --> H[Build Overview Table (Container -> Table) with common_prefix and unique counts]
    H --> I[Build path_items list (Overview + FrequencyTable('Full') + FrequencyTable for each part)]
    I --> J[Create path_tab = Container(path_items, name="Path", sequence_type="tabs", anchor_id=f"{varid}path")]
    J --> K[Append path_tab to template_variables["bottom"].content["items"]]
    K --> L[Return template_variables]

## Examples:
Example usage scenario (described as steps; do not treat these as executable snippet):
1. Preconditions:
    - The profiling pipeline computed a summary dict for a column containing filesystem-like paths. This summary contains counts per path part and aggregate statistics (see Args).
    - A Settings instance is available containing display and formatting options.

2. Calling:
    - Call render_path with the Settings instance and the summary dict.
    - The function invokes render_categorical to get a baseline template_variables and then augments it with path-specific frequency tables and an Overview table.

3. Expected result:
    - The returned dictionary is ready to be serialized into the report: it includes the "Path" tab under template_variables["bottom"], with an Overview table showing common prefix and unique counts, and frequency tables for the full path and its components (stem, name, extension, parent, anchor).
    - If any required keys are missing in summary, the caller should catch KeyError and either supply the missing data or skip path rendering.

4. Error handling recommendation:
    - Wrap the call in try/except KeyError to detect missing summary fields:
        * On KeyError: log which key is missing and fall back to a more generic categorical rendering or skip rendering the path-specific section.
    - Validate that render_categorical returned the expected template structure before calling render_path (or assert presence of "top" and "bottom" keys) if the caller cannot tolerate exceptions.

