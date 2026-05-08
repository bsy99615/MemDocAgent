# `overview.py`

## `src.ydata_profiling.report.structure.overview.get_dataset_overview` · *function*

## Summary:
Builds and returns an "Overview" Container Renderable composed of two Tables: one with dataset-level statistics and one with counts per variable type.

## Description:
This function converts summary statistics stored in a BaseDescription-like object into presentation Renderables. It formats numeric metrics using the report's configured formatters and returns a Container containing:
- "Dataset statistics" Table: basic metrics (n_var, n, missing cells, missing percent) and optional rows for duplicate counts and memory usage when present in the summary.
- "Variable types" Table: one row per entry in summary.table["types"], showing the type name and a formatted count.

Known callers / usage context:
- Invoked by report-building code that assembles sections of the profiling report after a dataset summary is computed (for example, the module responsible for building the full report structure). Callers expect a Renderable suitable for inclusion in the report presentation pipeline.

Why extracted:
- Encapsulates presentation/layout logic (which fields to present, how to format them, and how to arrange Tables within a Container). Keeps rendering concerns separate from the code that computes dataset statistics.

## Args:
    config (Settings)
        - Type: Settings (project's configuration type)
        - Required attributes accessed:
            * config.html.style: passed as the `style` argument to Table constructors.
            * config.report.precision: passed as `precision` to fmt_numeric when formatting type counts.
        - No default.

    summary (BaseDescription)
        - Type: BaseDescription (or any object exposing a mapping-like attribute `.table`)
        - Required attribute:
            * summary.table: a mapping (e.g., dict) containing the dataset metrics described below.
        - Required keys in summary.table (accessed unconditionally; missing keys will raise KeyError):
            * "n_var" (numeric): number of variables/columns
            * "n" (numeric): number of observations/rows
            * "n_cells_missing" (numeric): total missing cells
            * "p_cells_missing" (numeric): missing cells proportion/percentage value accepted by fmt_percent
            * "types" (mapping[str, numeric]): mapping from variable type name to count
        - Optional keys (function checks presence before use):
            * "n_duplicates" (numeric): number of duplicate rows
            * "p_duplicates" (numeric): duplicate rows proportion/percentage accepted by fmt_percent
            * "memory_size" (numeric): total memory size in bytes
            * "record_size" (numeric): average record size in bytes
        - Notes on interdependencies:
            * If "n_duplicates" exists, function also expects "p_duplicates" to be present for the percent row (the code reads both when "n_duplicates" key is present).
            * If "memory_size" exists, function also expects "record_size" to be present (both are read when "memory_size" key is present).

## Returns:
    Renderable
        - Specifically returns a Container (from ydata_profiling.report.presentation.core) configured as:
            * contents (list): [dataset_info, dataset_types]
                - dataset_info: Table built from table_metrics; each row is a dict with keys:
                    - "name" (str): label shown in the table (e.g., "Number of variables")
                    - "value" (str): formatted value produced by formatter helpers (fmt_number, fmt_percent, fmt_bytesize)
                - dataset_types: Table constructed from summary.table["types"], where each row is:
                    - "name" (str): str(type_name) — the type name coerced to string
                    - "value" (str): fmt_numeric(count, precision=config.report.precision)
            * anchor_id: "dataset_overview"
            * name: "Overview"
            * sequence_type: "grid"
            * style: config.html.style (passed to both Table constructors)
        - Edge cases:
            * Optional metrics are omitted if their keys are absent from summary.table.
            * If summary.table["types"] is empty, the second Table will be created with zero rows.

## Raises:
    KeyError
        - Triggered when any required key is missing from summary.table:
            * Accessing summary.table["n_var"], summary.table["n"], summary.table["n_cells_missing"], summary.table["p_cells_missing"], or summary.table["types"] will raise KeyError if absent.
        - Additionally:
            * If "n_duplicates" is present but "p_duplicates" is missing, accessing summary.table["p_duplicates"] will raise KeyError.
            * If "memory_size" is present but "record_size" is missing, accessing summary.table["record_size"] will raise KeyError.

    TypeError / ValueError / other exceptions
        - May be raised by formatter helpers (fmt_number, fmt_percent, fmt_bytesize, fmt_numeric) if provided values are of incompatible types or invalid. Those exceptions originate from the formatters; this function does not catch them.

## Constraints:
    Preconditions:
        - config must provide html.style and report.precision attributes.
        - summary.table must be a subscriptable mapping with the required keys and values compatible with the formatting helpers.
        - Values passed to fmt_percent, fmt_number, fmt_bytesize, fmt_numeric should be numeric-like as expected by those helpers.

    Postconditions:
        - Returns a Container Renderable that encapsulates two Table Renderables reflecting the dataset overview.
        - Does not modify `config` or `summary` objects.

## Side Effects:
    - The function itself has no I/O (no file, network, or stdout operations) and does not mutate global state.
    - It constructs and returns Renderable objects; any rendering or I/O occurs later when these Renderables are consumed by the presentation layer.

## Control Flow:
flowchart TD
    Start --> Build_basic_table_metrics
    Build_basic_table_metrics --> Check_n_duplicates
    Check_n_duplicates -->|present| Extend_with_duplicate_rows
    Check_n_duplicates -->|absent| Skip_duplicate_extension
    Extend_with_duplicate_rows --> Check_memory_size
    Skip_duplicate_extension --> Check_memory_size
    Check_memory_size -->|present| Extend_with_memory_rows
    Check_memory_size -->|absent| Skip_memory_extension
    Extend_with_memory_rows --> Create_dataset_info_Table
    Skip_memory_extension --> Create_dataset_info_Table
    Create_dataset_info_Table --> Create_dataset_types_Table
    Create_dataset_types_Table --> Build_Container
    Build_Container --> Return_Container
    Return_Container --> End

## Examples:
Example usage with minimal objects (illustrative — actual Settings/BaseDescription constructors may differ):

    # Prepare a Settings-like object with required attributes
    class DummyConfig:
        class html:
            style = "primary"
        class report:
            precision = 2
    config = DummyConfig()

    # Prepare a BaseDescription-like object
    class DummySummary:
        pass
    summary = DummySummary()
    summary.table = {
        "n_var": 5,
        "n": 100,
        "n_cells_missing": 3,
        "p_cells_missing": 0.03,
        "types": {"Numeric": 3, "Categorical": 2},
        # Optional:
        "n_duplicates": 0,
        "p_duplicates": 0.0,
        "memory_size": 2048,
        "record_size": 20,
    }

    # Build the overview renderable
    try:
        overview = get_dataset_overview(config, summary)
        # `overview` is a Container with two Table children ready for the presentation layer.
    except KeyError as e:
        # Required summary.table key is missing
        raise e
    except Exception as e:
        # Formatter or other unexpected error
        raise e

## `src.ydata_profiling.report.structure.overview.get_dataset_schema` · *function*

## Summary:
Constructs a presentation Container for the dataset-level metadata by collecting selected metadata fields into a single Table and returning it as a Container ready for inclusion in the report.

## Description:
This function gathers a small, well-defined subset of dataset metadata (description, creator, author, URL, copyright holder and year), formats display values, and packages them into a Table wrapped in a Container. It is intended to be used during construction of the report overview section where a compact "Dataset" block is shown to users.

Known callers and typical call context:
- Typically called by the report-generation pipeline when assembling the overview/metadata section of a profiling report (i.e., the step that builds the "Dataset" panel of the overall report). It is meant to be invoked after metadata has been extracted or provided to the profiler configuration.
- No specific function names are required here; any report assembler that needs a presentation Container for dataset-level metadata will call this function.

Why this logic is extracted:
- Responsibility separation: isolates formatting and presentation of dataset-level metadata from the broader report assembly logic.
- Reuse: allows multiple report-building steps to obtain a consistently-formatted dataset panel without duplicating HTML/formatting logic.
- Testability: enables unit tests for metadata-to-presentation mapping independently of the rest of the report pipeline.

## Args:
    config (Settings):
        - Type: Settings (expected profiling configuration object).
        - Requirements: config must provide an attribute html.style, which is passed to the Table constructor as style.
        - Notes: The function does not validate or mutate config; it only reads config.html.style.
    metadata (dict):
        - Type: dict with string keys to values of any type that support len() or string conversion.
        - Recognized keys:
            - "description": displayed if present and non-empty (len() > 0).
            - "creator": displayed if present and non-empty.
            - "author": displayed if present and non-empty.
            - "url": displayed if present (value inserted into an HTML anchor tag as-is).
            - "copyright_holder": displayed if present and non-empty; will be combined with copyright_year when available.
            - "copyright_year": optional; used only when copyright_holder is present to include the year after the holder.
        - Interdependencies:
            - copyright_year is only meaningful if copyright_holder is present.
        - Allowed value shapes:
            - Values for the listed keys are typically strings, but any object with len() > 0 will be accepted for presence checks. Values are passed to a formatter function (fmt) before display except for "url", which is embedded directly into an anchor tag string.

## Returns:
    Container:
        - A presentation Container instance representing the "Dataset" section.
        - Contents:
            - One Table element (name="Dataset", anchor_id="metadata_dataset") whose rows are the collected metadata items. Each row is a mapping with keys "name" (label) and "value" (formatted display value).
        - Edge cases:
            - If no recognized metadata keys are present or all recognized keys are empty, the Table will be created with an empty list of rows. The function still returns a Container with that empty Table (no exception is raised).

## Raises:
    - This function does not explicitly raise exceptions in normal control flow.
    - However, callers should be aware that:
        - If config is None or lacks an html attribute with style, attribute access may raise AttributeError.
        - If metadata contains values whose formatting via fmt raises an exception, that exception will propagate.
        - If metadata values are objects for which len() is not supported, the len() call will raise a TypeError; the check is only performed for keys checked with len() > 0 ("description", "creator", "author", "copyright_holder").

## Constraints:
    Preconditions:
        - config must be a Settings-like object with a nested html.style attribute accessible for the Table constructor.
        - metadata must be a dict-like mapping of string keys to values. For keys checked with len(), values must support len() or be omitted.
    Postconditions:
        - The function always returns a Container instance (unless an exception occurs due to invalid config/metadata types or formatting errors).
        - The returned Container contains exactly one Table child named "Dataset" (anchor_id "metadata_dataset") and the Container itself is named "Dataset" with anchor_id "dataset" and sequence_type "grid".

## Side Effects:
    - No I/O (no file or network operations) is performed.
    - No global state is mutated.
    - The function constructs HTML snippets (an anchor tag for "url") and uses the formatting helper fmt for other values; these are purely in-memory presentation objects.
    - Potential security note: the "url" value is embedded directly into an HTML anchor tag without escaping in this function; callers should ensure URLs are trusted or sanitized to avoid producing unsafe HTML.

## Control Flow:
flowchart TD
    Start --> InitAboutDataset["about_dataset = []"]
    InitAboutDataset --> ForLoop["for key in ['description','creator','author']"]
    ForLoop --> KeyInMetadata{"key in metadata and len(metadata[key]) > 0?"}
    KeyInMetadata -->|yes| AppendFmt["append {'name': key.capitalize(), 'value': fmt(metadata[key])}"]
    KeyInMetadata -->|no| ContinueFor
    ContinueFor --> ForLoop
    ForLoop --> AfterFor
    AfterFor --> CheckURL{"'url' in metadata?"}
    CheckURL -->|yes| AppendURL["append {'name':'URL','value': '<a href=\"...\">...</a>'}"]
    CheckURL -->|no| AfterURL
    AppendURL --> AfterURL
    AfterURL --> CheckCopyright{"'copyright_holder' in metadata and len(...)>0?"}
    CheckCopyright -->|no| BuildContainer
    CheckCopyright -->|yes and 'copyright_year' not in metadata| AppendCopyrightNoYear["append formatted holder"]
    CheckCopyright -->|yes and 'copyright_year' in metadata| AppendCopyrightWithYear["append formatted holder and year"]
    AppendCopyrightNoYear --> BuildContainer
    AppendCopyrightWithYear --> BuildContainer
    BuildContainer --> ReturnContainer["return Container([Table(about_dataset, style=config.html.style)])"]
    ReturnContainer --> End

## Examples (usage and error handling described in prose):
- Typical successful usage:
    1. The report-building code has already created or received a Settings object `config` whose config.html.style is set to the desired table style.
    2. The profiling pipeline has a metadata dictionary containing dataset-level values collected from the source or user input. Example metadata keys that will be rendered: description, creator, author, url, copyright_holder, copyright_year.
    3. Call get_dataset_schema(config, metadata) to obtain a Container object that can be appended to the overall report presentation structure. The Container will contain a Table with rows for each present and non-empty metadata field.

- Handling missing or malformed inputs:
    - If metadata omits all recognized keys, the function returns a Container with an empty Table. The caller may check the table rows and omit rendering empty sections.
    - If config is missing html.style (e.g., config or html is None), an AttributeError may be raised; callers should validate config before calling.
    - If metadata values are of unexpected types that do not support len() checks, a TypeError may be raised; callers should normalize metadata (convert None to missing key, ensure strings or sequence-like values where appropriate) before calling.

## `src.ydata_profiling.report.structure.overview.get_dataset_reproduction` · *function*

## Summary:
Constructs a small presentation fragment that documents how to reproduce the profiling run (start/end times, duration, software version and a downloadable configuration), returning it as a Renderable container suitable for inclusion in the report overview.

## Description:
This function reads metadata from the provided summary (a BaseDescription) and the report Settings to produce a Container (sequence_type "grid") containing a single Table summarizing reproduction information. Typical callers are report-building code that assembles the Overview / Reproduction section of the final report (for example: an overview assembly function or higher-level report renderer that builds the report tree from a BaseDescription). The logic is extracted to its own function because it isolates the small, well-defined responsibility of producing the reproduction metadata presentation (formatting links and time spans, producing consistent table rows) so higher-level assembly code can remain focused on overall composition.

Known input fields accessed on summary:
- summary.package["ydata_profiling_version"] — software version string (required).
- summary.package["ydata_profiling_config"] — configuration JSON/text (required).
- summary.analysis.date_start — analysis start timestamp (used via fmt()).
- summary.analysis.date_end — analysis end timestamp (used via fmt()).
- summary.analysis.duration — analysis duration (used via fmt_timespan()).

Notes about local formatting:
- Two local single-value formatters are defined and decorated with list_args:
  - fmt_version: builds an HTML anchor linking to the project's GitHub page with the version embedded in the link text. Because of list_args, if version is a Python list, fmt_version will return a list of formatted anchors.
  - fmt_config: builds a data: URL anchor that triggers a download named config.json; because of list_args, a list of config strings results in a list of anchors.
- The general fmt function (imported) is used for date_start/date_end to produce safe, presentation-ready strings; fmt_timespan is used to render duration.

## Args:
    config (Settings):
        - The profiling report Settings instance. The function reads config.html.style to pass to the Table constructor.
        - Must expose attribute html.style (a Style instance or equivalent) — otherwise attribute access will fail.
    summary (BaseDescription):
        - A BaseDescription populated by the profiling analyzers.
        - Required fields (must be present and well-formed):
            * summary.package: a mapping containing the keys "ydata_profiling_version" (str or list[str]) and "ydata_profiling_config" (str or list[str]).
            * summary.analysis: an object exposing date_start, date_end, and duration. Commonly this is a BaseAnalysis whose duration property returns a timedelta (or a list of timedeltas if summary.analysis uses lists).

Interdependencies / input shapes:
- The function assumes summary.package contains the two keys above; if either key is missing a KeyError will be raised.
- The formatting functions are tolerant to receiving either a scalar or a Python list for the package values because the local formatters are decorated with list_args. If date_start/date_end are lists, the fmt function will be invoked with that list as-is (fmt's behavior for lists depends on its implementation and may return list-like results or raise if unsupported).

## Returns:
    Renderable
    - A Container instance (Renderable subclass/instance) with:
        * content['items'] containing a single Table instance.
        * name set to "Reproduction".
        * anchor_id set to "reproduction".
        * sequence_type set to "grid".
    - The contained Table has:
        * rows: a list of row dicts, each with keys "name" (str) and "value" (formatted str or list of formatted strings).
        * name: "Reproduction"
        * anchor_id: "overview_reproduction"
        * style: config.html.style (passed-through)
    - Possible return-value shapes:
        * Normal case: single Container containing a single Table with scalar-formatted row values (strings).
        * List-valued metadata case: if summary.package[...] entries are Python list instances, the decorated formatters produce lists for those row values (so Table rows may contain list values). The function always returns a Container object (never None).

## Raises:
    KeyError
        - If summary.package does not contain "ydata_profiling_version" or "ydata_profiling_config".
    AttributeError
        - If summary.analysis is missing or does not expose date_start/date_end/duration.
        - If config.html or config.html.style is absent (attribute access failure).
    ValueError
        - May propagate from summary.analysis.duration property if BaseAnalysis's duration raises ValueError for incompatible date_start/date_end shapes (see BaseAnalysis semantics).
    Any exceptions raised by the formatting utilities:
        - Exceptions from fmt(...) or fmt_timespan(...) (TypeError, ValueError, etc.) will propagate.
    Note: the function performs no try/except handling; callers should catch these exceptions if they may occur in their context.

## Constraints:
Preconditions:
    - summary must be a fully-populated BaseDescription (or equivalent) with the package and analysis fields described above.
    - config must provide an html.style attribute suitable for passing to Table.
Postconditions:
    - On successful return, the caller receives a Container ready to be rendered by the presentation pipeline; no global state is mutated.
    - The returned Container and Table share references to the passed style object (no defensive copy).

## Side Effects:
    - None performed by this function itself: it does not perform file I/O, network calls, logging, or mutation of global variables.
    - The generated HTML anchor in the "Download configuration" cell uses a data: URL (data:text/plain;charset=utf-8,...) but that merely embeds the config text in a clickable link — no network activity occurs at creation time.
    - All side effects originate from called helpers (fmt, fmt_timespan, quote) and are local computations only.

## Control Flow:
flowchart TD
    Start([Start get_dataset_reproduction]) --> ReadSummary[Read summary.package and summary.analysis]
    ReadSummary --> DefineFmtVersion[Define fmt_version (decorated with list_args)]
    DefineFmtVersion --> DefineFmtConfig[Define fmt_config (decorated with list_args)]
    DefineFmtConfig --> BuildRows[Build rows list:
        - Analysis started -> fmt(date_start)
        - Analysis finished -> fmt(date_end)
        - Duration -> fmt_timespan(duration)
        - Software version -> fmt_version(version)
        - Download configuration -> fmt_config(config_file)
    ]
    BuildRows --> CreateTable[Instantiate Table(rows, name="Reproduction", anchor_id="overview_reproduction", style=config.html.style)]
    CreateTable --> CreateContainer[Instantiate Container([Table], name="Reproduction", anchor_id="reproduction", sequence_type="grid")]
    CreateContainer --> Return[Return Container]

## Examples (usage described in prose):
- Typical happy-path usage:
    1. The profiling pipeline has produced a BaseDescription with summary.analysis set (date_start, date_end, duration) and summary.package containing "ydata_profiling_version" and "ydata_profiling_config".
    2. A report builder calls get_dataset_reproduction(config, summary) to obtain a Renderable fragment that documents when the analysis ran, how long it took, which ydata-profiling version was used, and provides a downloadable copy of the config.
    3. The returned Container is appended into the overview section of the report tree and later rendered by the renderer responsible for turning Renderable trees into HTML.

- Example of list-valued package fields:
    - If summary.package["ydata_profiling_version"] is a Python list of versions (a list instance), fmt_version (decorated by list_args) returns a list of anchor strings; that list becomes the value for the "Software version" row in the Table. The overall Container is still returned normally.

- Error-handling guidance:
    - If callers cannot guarantee summary.package contains the expected keys, wrap the call in a try/except for KeyError to provide a fallback reproduction fragment or to omit the reproduction block.
    - If BaseAnalysis.duration may raise ValueError because date_start/date_end use inconsistent shapes (e.g., one is a list and the other a datetime), catch ValueError and either compute a safe fallback duration string or skip the duration row.
    - If config.html.style might be missing in some Settings instances, guard attribute access (e.g., check hasattr(config, "html") and hasattr(config.html, "style")) before calling the function, or catch AttributeError on call.

## `src.ydata_profiling.report.structure.overview.get_dataset_column_definitions` · *function*

## Summary:
Create a presentation Container that lists variable (column) descriptions as a Table suitable for inclusion in the dataset overview.

## Description:
This function transforms a mapping of dataset column names to their textual definitions into a presentation-ready Container containing a single Table. The Table contains one row per column where each row has "name" set to the column identifier and "value" set to the formatted description using the project's formatter.

Known callers (from provided inputs): None explicitly identified in the supplied file-level context. Typical usage: invoked by the report-building pipeline when assembling the "Variables" section of a dataset overview report (i.e., where column-level human-readable descriptions must be displayed). Responsibility boundary: it handles only presentation assembly for column descriptions — it does not validate or enrich the definitions beyond applying the formatter.

Why this is extracted into a dedicated function:
- Keeps the report assembly code modular by encapsulating the conversion from a plain mapping to the report presentation objects (Table and Container).
- Centralizes formatting behavior for variable descriptions so other overview sections can reuse the same presentation contract (Table within a Container).
- Simplifies unit testing and potential future adjustments to presentation details (naming, anchor ids, layout).

## Args:
    config (Settings):
        - Type: Settings (project configuration object)
        - Required attributes used: config.html.style (style object/value passed to Table).
        - Precondition: config must be a valid Settings instance or an object exposing html.style; otherwise an AttributeError will occur.
    definitions (dict[str, Any]):
        - Type: mapping from column name to definition value
        - Keys: expected to be strings representing column identifiers (the function uses these as the displayed "name")
        - Values: arbitrary values accepted; each value is passed to fmt(value) before being placed in the Table "value" cell
        - Notes: order of rows follows the iteration order of definitions.items() (in Python 3.7+ this preserves insertion order).

## Returns:
    Container
    - What it represents: a presentation Container named "Variables" that holds a single Table presenting each variable/column and its formatted description.
    - Contents details:
        - Container.name == "Variables"
        - Container.anchor_id == "variable_descriptions"
        - Container.sequence_type == "grid"
        - The Container contains one Table with:
            - name: "Variable descriptions"
            - anchor_id: "variable_definition_table"
            - style: taken from config.html.style
            - rows: a list of dicts, each dict has:
                - "name": the original column key (as provided in definitions)
                - "value": fmt(value) where value is the corresponding definitions value
    - Edge cases:
        - If definitions is empty, the returned Container will hold a Table with an empty rows list.
        - fmt(value) determines the final string/representation of each value; any behavior of fmt (e.g., None handling) affects the Table cell contents.

## Raises:
    AttributeError:
        - If config is None or does not expose an html attribute with a style attribute (i.e., accessing config.html.style will raise AttributeError).
    AttributeError or TypeError:
        - If definitions is not a mapping or otherwise does not support .items(), attempting to iterate definitions.items() will raise AttributeError or TypeError.
    (No exceptions are explicitly raised by this function; the above reflect direct attribute/usage errors that will surface from the calls used.)

## Constraints:
    Preconditions:
        - Caller should supply a valid Settings-like object with config.html.style available.
        - Caller should supply a mapping-like definitions object (with items()) whose keys are displayable as names.
    Postconditions:
        - The function returns a Container with exactly one Table describing the provided definitions.
        - For each (column, value) pair in definitions.items(), there will be a corresponding row in the Table with "name" == column and "value" == fmt(value).
        - The Table's style reflects config.html.style.

## Side Effects:
    - No I/O is performed (no file or network access).
    - No mutation of external/global state is performed by this function.
    - The function calls fmt(value) (a formatter function) which may perform pure formatting; any side effects of fmt are outside the scope of this function.
    - No external services are invoked directly by this function.

## Control Flow:
flowchart TD
    Start["Start: get_dataset_column_definitions"] --> CheckDefinitions["Iterate definitions.items()"]
    CheckDefinitions --> BuildRows["For each (column, value): create {'name': column, 'value': fmt(value)}"]
    BuildRows --> CreateTable["Create Table(rows, name='Variable descriptions', anchor_id='variable_definition_table', style=config.html.style)"]
    CreateTable --> CreateContainer["Create Container([Table], name='Variables', anchor_id='variable_descriptions', sequence_type='grid')"]
    CreateContainer --> Return["Return Container"]
    Return --> End["End"]

## Examples:
- Typical (described in prose):
    1. A report builder has a mapping of human-written descriptions for a dataset's columns (e.g., {"age": "Age in years", "income": "Annual income in USD"}).
    2. The builder passes the global config (with HTML style settings) and that mapping to this function.
    3. The function returns a Container named "Variables" containing a Table named "Variable descriptions". The Table has two rows:
        - {"name": "age", "value": "<formatted 'Age in years'>"}
        - {"name": "income", "value": "<formatted 'Annual income in USD'>"}
    4. The report renderer receives the Container and embeds it in the overview page, producing a grid showing each variable and its formatted description.

- Error-handling scenario (described in prose):
    - If the caller passes config=None or a config object without an html.style attribute, the caller should catch AttributeError when invoking this function and ensure a proper Settings instance is supplied before retrying.

## `src.ydata_profiling.report.structure.overview.get_dataset_alerts` · *function*

## Summary:
Creates an Alerts presentation object for the dataset overview by normalizing the provided alerts input (either a flat list or a tuple-of-report alert lists) and computing the visible alert count (excluding rejected alerts).

## Description:
This function produces an Alerts instance configured for the overview's "Alerts" section. It accepts either:
- a flat iterable (commonly a list) of alert objects representing a single report, or
- a tuple of iterables where each element represents the alerts produced by a different report (e.g., multiple generated summaries to be compared).

Known callers within the provided context:
- No direct callers are present in the isolated source snippet supplied. In the broader reporting pipeline this function is intended to be invoked by the overview/summary assembly code when rendering the dataset-level overview (the step that builds the "Alerts" block in the generated report).

Why this logic is extracted:
- Responsibility separation: it centralizes the logic that normalizes different alert input shapes (single-report vs multi-report), computes the display count excluding rejected alerts, and constructs the Alerts presentation object. This keeps higher-level report rendering code focused on layout and sequencing rather than on alert-shape normalization and counting.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Required attributes used: config.html.style (used for the returned Alerts style).
        - Notes: The function does not validate Settings fully; it only reads config.html.style. If that attribute is missing an AttributeError will propagate.
    alerts (list or tuple):
        - Type: either:
            * a flat iterable (commonly list) of alert objects, or
            * a tuple of iterables, where each element is a collection (list/iterable) of alert objects for a specific report.
        - Each alert object is expected to have at least these attributes:
            * alert_type: comparable to values from ydata_profiling.model.alerts.AlertType (the function checks equality with AlertType.REJECTED to exclude from counts)
            * column_name: used to form combined keys when alerts is a tuple
        - Interdependencies:
            * If alerts is a tuple, the function assumes each tuple element corresponds to one "report index" and will produce per-index lists; therefore positions in combined lists correspond to tuple indices.

## Returns:
    Alerts
    - When alerts is not a tuple:
        * Returns an Alerts instance with:
            - alerts set to the same iterable passed in (no structural modification).
            - name set to "Alerts (N)" where N is the number of alerts whose alert_type != AlertType.REJECTED.
            - anchor_id set to "alerts".
            - style taken from config.html.style.
    - When alerts is a tuple:
        * Returns an Alerts instance with:
            - alerts set to a dict mapping keys of the form "{alert.alert_type}_{alert.column_name}" to lists of length len(alerts). Each list position corresponds to the report index in the input tuple; a position contains either the alert object for that report or None if that report had no alert for that key.
            - name set to "Alerts (N)" where N is the total number of non-REJECTED alerts across all reports.
            - anchor_id set to "alerts".
            - style taken from config.html.style.
    - Edge cases:
        * Empty input (empty list or empty tuple) returns an Alerts object with alerts set to the empty input shape (empty list or empty dict respectively) and name "Alerts (0)".
        * Duplicate alerts that share the same alert_type and column_name within the same report index will result in the last-seen alert occupying that report index in the combined list (i.e., potential overwrite).

## Raises:
    - AttributeError:
        * If config does not provide html.style (accessed as config.html.style), an AttributeError will be raised by attribute access.
        * If an alert in the provided alerts does not have alert_type or column_name attributes, an AttributeError will be raised when forming keys or comparing to AlertType.REJECTED.
    - TypeError:
        * If alerts is a tuple but contains non-iterable elements (so the comprehension or iteration fails), a TypeError may propagate.
    - Note: The function does not explicitly raise custom exceptions; most failures arise from missing attributes or incorrect input shapes and will propagate the underlying Python exception.

## Constraints:
Preconditions:
    - config must be a Settings-like object with config.html.style accessible.
    - alerts must be either:
        * a flat iterable of alert-like objects, or
        * a tuple whose elements are iterables of alert-like objects.
    - Each alert-like object must expose alert_type and column_name attributes and should be comparable against AlertType.REJECTED.

Postconditions:
    - The returned Alerts object will have:
        * name equal to "Alerts (X)" where X equals the number of alerts across the provided input whose alert_type != AlertType.REJECTED.
        * anchor_id set to "alerts".
        * style set to config.html.style.
    - If the input was a tuple, the returned alerts attribute is a dict mapping string keys to per-report-position lists (length equals number of reports). If input was not a tuple, the returned alerts attribute equals the original alerts iterable.

## Side Effects:
    - No I/O (files, network, stdout) are performed.
    - No global state is modified.
    - Only object construction occurs (an Alerts instance and, if applicable, an intermediate dict and lists).
    - No external services are called.

## Control Flow:
flowchart TD
    A[Start] --> B{isinstance(alerts, tuple)?}
    B -- yes --> C[Initialize count = 0]
    C --> D[Build combined_alerts dict keys for each alert across reports]
    D --> E[For each report index and its alerts:]
    E --> F[Place alert object at combined_alerts["type_column"][report_idx]]
    F --> G[Increment count by number of non-REJECTED alerts in that report]
    G --> H[Return Alerts(alerts=combined_alerts, name=f"Alerts (count)", anchor_id="alerts", style=config.html.style)]
    B -- no --> I[count = number of non-REJECTED alerts in alerts]
    I --> J[Return Alerts(alerts=alerts, name=f"Alerts (count)", anchor_id="alerts", style=config.html.style)]
    H --> K[End]
    J --> K

## Examples:
Example (single-report alerts):
    # Suppose `alerts` is a list of alert objects produced for the dataset (single report).
    # Calling the function will return an Alerts instance that wraps that list
    # and sets the visible count to exclude AlertType.REJECTED.
    instance = get_dataset_alerts(config, alerts)
    # instance.name -> "Alerts (N)"  (N excludes REJECTED alerts)
    # instance.alerts -> the same iterable passed in

Example (multi-report comparison using a tuple):
    # Suppose you have two reports' alerts: report_a_alerts and report_b_alerts,
    # and you pass alerts = (report_a_alerts, report_b_alerts).
    # The returned Alerts.alerts will be a dict:
    #   {
    #     "<alerttype>_<column>": [alert_or_None_for_report_a, alert_or_None_for_report_b],
    #     ...
    #   }
    # Each list has length 2 (one entry per report) and positions correspond to tuple indices.
    comparison = get_dataset_alerts(config, (report_a_alerts, report_b_alerts))
    # comparison.name -> "Alerts (M)"  (M = non-REJECTED alerts across both reports)
    # comparison.alerts -> dict keyed by "<alert_type>_<column_name>"

## `src.ydata_profiling.report.structure.overview.get_timeseries_items` · *function*

## Summary:
Constructs and returns a renderable Container for the "Time Series" overview: a statistics Table (number of series, length, start/end, period) and a tabs Container with two overview plots (original and scaled).

## Description:
This function builds the time-series overview section by:
- Accessing summary.time_index_analysis and reading its attributes (n_series, length, start, end, period).
- Formatting those values into a table_rows list and instantiating a Table with style=config.html.style and name="Timeseries statistics".
- Temporarily setting config.plot.dpi = 300 (backing up the original value), calling plot_overview_timeseries twice (scale=False and scale=True) to obtain plotting payloads, and constructing two image presentation items from those plotting results.
- Grouping the two image items into a Container with sequence_type="tabs" and anchor_id="ts_plot_overview".
- Returning a top-level Container (sequence_type="grid", anchor_id="timeseries_overview", name="Time Series") containing the table and the tabs container.

Why this logic is separated:
- Keeps formatting, plotting, and presentation wiring for the time-series overview in one place so the report builder can treat this as a single block.
- Makes the plotting DPI adjustment and figure generation explicit and testable.
- Enables reusing or modifying the time-series block without affecting other report sections.

Known callers / usage context:
- Intended to be used by the report-building pipeline when a profiling run produced a TimeIndexAnalysis attached to a BaseDescription. Typical trigger: the report generator discovers that summary.time_index_analysis is present and calls this function to include the time-series overview.

## Args:
    config (Settings)
        - The global configuration object. The function reads and mutates:
            * config.html.style (passed as style to Table)
            * config.plot.dpi (backed up and temporarily set to 300)
            * config.plot.image_format (passed to the image item constructor)
        - Must be a Settings instance (the function type-hints this).

    summary (BaseDescription)
        - A profiling result object. The function requires:
            * summary.time_index_analysis to exist and be an instance of TimeIndexAnalysis (the function asserts this).
            * summary.variables to be a mapping consumed by plot_overview_timeseries.
        - The function accesses these attributes on summary.time_index_analysis:
            - n_series
            - length
            - start
            - end
            - period

## Returns:
    Container (top-level)
    - The function returns a Container object constructed as:
        Container(
            [ts_info, ts_tab],
            anchor_id="timeseries_overview",
            name="Time Series",
            sequence_type="grid",
        )
      where:
        - ts_info is created as:
            Table(
                table_stats,
                name="Timeseries statistics",
                style=config.html.style
            )
          and table_stats is a list of dict rows with keys "name" and "value":
            * "Number of series" -> fmt_number(summary.time_index_analysis.n_series)
            * "Time series length" -> fmt_number(summary.time_index_analysis.length)
            * "Starting point" -> format_tsindex_limit(summary.time_index_analysis.start)
            * "Ending point" -> format_tsindex_limit(summary.time_index_analysis.end)
            * "Period" -> fmt_timespan_timedelta(summary.time_index_analysis.period)
        - ts_tab is created as:
            Container(
                [timeseries, timeseries_scaled],
                anchor_id="ts_plot_overview",
                name="",
                sequence_type="tabs",
            )
          where timeseries and timeseries_scaled are image presentation items constructed in the source via calls that look like:
            timeseries = ImageWidget(
                plot_overview_timeseries(config, summary.variables),
                image_format=config.plot.image_format,
                alt="ts_plot",
                name="Original",
                anchor_id="ts_plot_overview",
            )
            timeseries_scaled = ImageWidget(
                plot_overview_timeseries(config, summary.variables, scale=True),
                image_format=config.plot.image_format,
                alt="ts_plot_scaled",
                name="Scaled",
                anchor_id="ts_plot_scaled_overview",
            )
    - On successful completion this Container is returned. If the function raises, no Container is returned.

## Raises:
    AssertionError
        - Raised by the assert at the start if summary.time_index_analysis is not an instance of TimeIndexAnalysis.

    Any exception propagated from called functions/constructors:
        - fmt_number, fmt_timespan_timedelta, or other formatter helpers may raise if passed invalid input.
        - plot_overview_timeseries may raise matplotlib-related exceptions while creating figures.
        - The image presentation constructor (the code calls ImageWidget(...)) may raise (e.g., ValueError) if it enforces non-None payloads or validation checks.
    Notes:
        - The function does not catch exceptions. Because DPI restoration is done via a simple assignment rather than try/finally, an exception between setting and restoring config.plot.dpi may leave dpi in the modified state.

## Constraints:
    Preconditions:
        - config must have html.style and plot attributes.
        - summary.time_index_analysis must be present and be a TimeIndexAnalysis instance.
        - summary.variables must be structured as expected by plot_overview_timeseries.

    Postconditions:
        - If the function completes normally, config.plot.dpi is restored to its original value by assignment at the end of the function.
        - The returned Container contains the Table and the tabs Container precisely as constructed above.

## Side Effects:
    - Mutates config.plot.dpi (temporary change to 300, then reassignment to the backed-up value).
      Important: restore is not protected by try/finally in the shown code; exceptions could prevent restoration.
    - Allocates matplotlib figures via plot_overview_timeseries and passes them to image presentation constructors. The function itself does not close or free these figures.
    - Creates in-memory presentation objects (Table, Container, and two image-like items). No file/network I/O is performed by this function.

## Helper behavior (explicit, as written in source):
    format_tsindex_limit(limit: Any) -> str
        - If isinstance(limit, datetime): return limit.strftime("%Y-%m-%d %H:%M:%S")
        - Else: return fmt_number(limit)

    plot_overview_timeseries usage:
        - Called twice:
            * plot_overview_timeseries(config, summary.variables)
            * plot_overview_timeseries(config, summary.variables, scale=True)
        - The function result is passed as the first positional argument to the image item constructor.

    Image constructor call pattern (exact calls present in source):
        - Two calls to ImageWidget(...) with these kwargs:
            * image_format=config.plot.image_format
            * alt="ts_plot" / "ts_plot_scaled"
            * name="Original" / "Scaled"
            * anchor_id="ts_plot_overview" / "ts_plot_scaled_overview"
        - Note: In the repository snapshot provided, ImageWidget is used in the source code but its class/definition was not present in the local memory snapshot. Reimplementers should ensure an appropriate image presentation constructor exists (for example, the available Image class or a concrete ImageWidget that accepts the same arguments).

## Control Flow:
flowchart TD
  Start --> AssertType{assert summary.time_index_analysis is TimeIndexAnalysis}
  AssertType -- fail --> RaiseAssertion[AssertionError]
  AssertType -- pass --> BuildRows[Build table_stats list and format values]
  BuildRows --> CreateTable[Create Table(table_stats, name="Timeseries statistics", style=config.html.style)]
  CreateTable --> Backup[Backup dpi_bak = config.plot.dpi]
  Backup --> SetDPI[Set config.plot.dpi = 300]
  SetDPI --> Plot1[fig1 = plot_overview_timeseries(config, summary.variables)]
  SetDPI --> Plot2[fig2 = plot_overview_timeseries(config, summary.variables, scale=True)]
  Plot1 --> MakeImg1[timeseries = ImageWidget(fig1, image_format=..., alt="ts_plot", name="Original", anchor_id="ts_plot_overview")]
  Plot2 --> MakeImg2[timeseries_scaled = ImageWidget(fig2, image_format=..., alt="ts_plot_scaled", name="Scaled", anchor_id="ts_plot_scaled_overview")]
  MakeImg1 --> Restore[config.plot.dpi = dpi_bak]
  MakeImg2 --> Restore
  Restore --> CreateTabs[ts_tab = Container([timeseries, timeseries_scaled], anchor_id="ts_plot_overview", name="", sequence_type="tabs")]
  CreateTabs --> Return[Return Container([ts_info, ts_tab], anchor_id="timeseries_overview", name="Time Series", sequence_type="grid")]
  Return --> End

## Reimplementation checklist (step-by-step):
1. Validate summary.time_index_analysis is present and has attributes n_series, length, start, end, period.
2. Implement format_tsindex_limit as:
    - if isinstance(limit, datetime): format with "%Y-%m-%d %H:%M:%S"
    - else use your numeric formatting helper (fmt_number equivalent)
3. Create table_stats list with dict rows as shown above and instantiate Table(rows=table_stats, name="Timeseries statistics", style=config.html.style).
4. Backup original_dpi = config.plot.dpi.
5. Use try/finally to ensure restoration:
    try:
        config.plot.dpi = 300
        fig1 = plot_overview_timeseries(config, summary.variables)
        fig2 = plot_overview_timeseries(config, summary.variables, scale=True)
    finally:
        config.plot.dpi = original_dpi
6. Instantiate image items for fig1 and fig2 using your presentation-layer image constructor. The source passes the figure as the first positional argument and sets image_format=config.plot.image_format plus alt/name/anchor_id keyword args.
7. Create ts_tab = Container([timeseries, timeseries_scaled], anchor_id="ts_plot_overview", name="", sequence_type="tabs").
8. Return Container([ts_info, ts_tab], anchor_id="timeseries_overview", name="Time Series", sequence_type="grid").

## Examples:
Typical usage in a report builder (pseudocode):

try:
    ts_block = get_timeseries_items(config, summary)
    # pass ts_block to renderer
except AssertionError:
    # time-index analysis absent; skip time-series section
    pass
except Exception as exc:
    # plotting or formatting failed; log and continue rendering other sections
    logger.warning("Time-series overview failed: %s", exc)

Notes:
- The source explicitly uses an identifier ImageWidget for image construction; ensure your presentation layer exposes a compatible image constructor (or adapt to use the available Image class and translate arguments accordingly).
- For robust behavior, wrap plot generation and DPI mutation in try/finally so the original config.plot.dpi is restored even on exceptions.

## `src.ydata_profiling.report.structure.overview.get_dataset_items` · *function*

## Summary:
Assembles and returns the ordered list of Renderable items that comprise the dataset overview section of the profiling report.

## Description:
This function delegates construction of each overview sub-block to specialized helper builders and collects their results into a single ordered list. It does not implement presentation or formatting itself — it decides which sub-blocks to include based on available metadata, column descriptions, time-index analysis, and alerts, then forwards control to the appropriate helper functions.

Why this logic is extracted:
- Orchestrates inclusion and ordering of overview sub-blocks while keeping the presentation and formatting responsibilities inside dedicated helper functions.
- Makes it easy to change which blocks are present or their order without modifying formatting/plotting code.
- Simplifies testing of assembly logic independently from rendering or plotting.

Known callers / usage context:
- Higher-level report-building code that has computed a BaseDescription (summary) and has access to a Settings instance (config). Callers invoke this function when they want the overview section Renderables to append to the overall report tree.
- This function delegates to these helper builders (see their component docs for details and returned Renderable shapes): get_dataset_overview, get_dataset_schema, get_dataset_column_definitions, get_timeseries_items, get_dataset_alerts, get_dataset_reproduction.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Role: global profiling configuration passed through to helper builders.
        - Required attributes (accessed transitively via helpers):
            * config.dataset (and its dict() method) — used to build metadata forwarded to get_dataset_schema.
            * config.variables.descriptions — mapping of column -> description forwarded to get_dataset_column_definitions.
            * config.html.style and other style/plot attributes required by helpers (e.g., plot settings used by get_timeseries_items).
        - Note: get_dataset_items itself does not inspect presentation-level style attributes beyond forwarding config to helpers; the helper functions (for example get_dataset_overview) read config.html.style when constructing Tables.

    summary (BaseDescription)
        - Type: model.BaseDescription (or an object following the same contract).
        - Role: dataset summary containing tables, variables, time-index analysis, package, and analysis metadata as required by the helpers (see each helper's documentation for exact required keys/attributes).
        - Expected attributes (used by helpers):
            * summary.table (for dataset overview)
            * summary.time_index_analysis (truthy indicates time-series block should be included)
            * summary.variables, summary.package, summary.analysis as required by other helpers.

    alerts (list or tuple-like)
        - Type: an iterable of alert-like objects or a tuple of per-report iterables.
        - Role: forwarded unchanged to get_dataset_alerts when truthy.
        - Notes on handling:
            * get_dataset_items only checks alerts for truthiness (i.e., whether to call the alerts helper).
            * The helper get_dataset_alerts is responsible for normalization and counting; depending on the input shape it may return an Alerts object that wraps the same iterable, or one that contains a normalized dict keyed by combined alert identifiers (see get_dataset_alerts docs). Consult get_dataset_alerts for exact normalization and returned shapes.

## Returns:
    list[Renderable]
    - Deterministic ordered list of Renderable items corresponding to overview sub-blocks. Inclusion and ordering:
        1. get_dataset_overview(config, summary) — always included as the first element (this helper reads config.html.style when building Tables).
        2. get_dataset_schema(config, metadata) — included when metadata (derived from config.dataset.dict()) is non-empty and at least one metadata value has non-zero length. The metadata mapping forwarded is effectively the mapping returned by config.dataset.dict().
        3. get_dataset_column_definitions(config, column_details) — included when config.variables.descriptions contains any entries; column_details is a shallow copy of that mapping.
        4. get_timeseries_items(config, summary) — included if summary.time_index_analysis is truthy; this helper may perform plotting and temporarily mutate config.plot.dpi.
        5. get_dataset_alerts(config, alerts) — included if the alerts argument is truthy; the helper performs normalization/counting and returns an Alerts Renderable (which may wrap the original iterable or a normalized dict).
        6. get_dataset_reproduction(config, summary) — always appended as the final element.
    - Each element is the Renderable returned by the helper; see each helper's documentation for concrete structures (Container, Table, Image, Alerts).
    - Edge cases:
        * If metadata or column descriptions are empty, their helpers are not invoked and those Renderables are omitted.
        * If a helper raises, that exception propagates and no list is returned.

## Raises:
    - This function does not raise new errors itself; exceptions propagate from helpers and attribute accesses. Typical propagated exceptions include:
        * KeyError: missing required keys accessed by helpers (e.g., summary.table keys, summary.package keys).
        * AttributeError: missing attributes on config or on alert objects when helpers access expected fields.
        * AssertionError: raised by get_timeseries_items if summary.time_index_analysis is not the expected type.
        * TypeError/ValueError/plotting errors: from formatter helpers or plot_overview_timeseries invoked by helpers.
    - Because get_dataset_items performs no try/except around helper calls, callers should be prepared to catch these exceptions.

## Constraints:
    Preconditions:
        - config must be a Settings-like object exposing config.dataset, config.variables.descriptions, and config.html.style (helpers may require additional nested attributes).
        - summary must be a BaseDescription-like object with the attributes used by helpers (summary.table, summary.variables, summary.time_index_analysis, summary.package, summary.analysis).
        - alerts should be an iterable (list/tuple) of alert-like objects or an empty iterable.

    Postconditions:
        - On success, the function returns a list of Renderable objects in the order listed under Returns.
        - get_dataset_items itself does not intentionally mutate config or summary. However, helper functions may perform temporary mutations (for example, get_timeseries_items temporarily sets config.plot.dpi). Such mutations are performed by the helper functions and not reversed here if a helper fails mid-execution.

## Side Effects:
    - Indirect side effects may occur via helper functions:
        * get_timeseries_items temporarily modifies config.plot.dpi while generating plots; if that helper raises before restoring dpi, config.plot.dpi may remain altered.
        * Plot generation inside helpers may allocate figure objects (matplotlib) and the presentation layer is responsible for managing/closing them.
        * Formatters used by helpers may coerce types or raise exceptions.
    - get_dataset_items itself performs no I/O, network calls, or global state mutations.

## Control Flow:
flowchart TD
    Start --> AddOverview[get_dataset_overview(config, summary) -> items[0]]
    AddOverview --> BuildMetadata[metadata = config.dataset.dict() copy]
    BuildMetadata --> HasNonEmptyMetadata{"len(metadata)>0 AND any(len(v)>0 for v in metadata.values())?"}
    HasNonEmptyMetadata -->|yes| AddSchema[get_dataset_schema(config, metadata) appended]
    HasNonEmptyMetadata -->|no| SkipSchema
    AddSchema --> BuildColumnDetails[column_details = config.variables.descriptions copy]
    SkipSchema --> BuildColumnDetails
    BuildColumnDetails --> HasColumns{"len(column_details) > 0?"}
    HasColumns -->|yes| AddColumnDefs[get_dataset_column_definitions(config, column_details) appended]
    HasColumns -->|no| SkipColumnDefs
    AddColumnDefs --> CheckTimeIndex
    SkipColumnDefs --> CheckTimeIndex
    CheckTimeIndex -->|summary.time_index_analysis is truthy| AddTimeseries[get_timeseries_items(config, summary) appended]
    CheckTimeIndex -->|false| SkipTimeseries
    AddTimeseries --> CheckAlerts
    SkipTimeseries --> CheckAlerts
    CheckAlerts -->|alerts is truthy| AddAlerts[get_dataset_alerts(config, alerts) appended]
    CheckAlerts -->|false| SkipAlerts
    AddAlerts --> AddReproduction[get_dataset_reproduction(config, summary) appended]
    SkipAlerts --> AddReproduction
    AddReproduction --> ReturnItems[return items list]
    ReturnItems --> End

## Examples:
- Typical usage in a report builder (pseudo-prose):
    1. A profiling job computes `summary` (BaseDescription) and a `config` Settings instance is available.
    2. The report builder calls:
        items = get_dataset_items(config, summary, alerts)
    3. The builder appends `items` into the overall report presentation tree or hands them to a renderer.
    4. If summary contains time-index analysis, a Time Series block will be included and plotting may happen when constructing its Image items.

- Alert-handling note:
    - get_dataset_items only checks whether `alerts` is truthy. If truthy, it forwards the alerts to get_dataset_alerts which then decides whether to preserve the iterable or normalize it (see get_dataset_alerts documentation for returned shapes and counting behavior).

- Error handling example:
    try:
        items = get_dataset_items(config, summary, alerts)
    except KeyError as e:
        # required keys missing in summary/config; handle or omit overview
        handle_missing_metadata(e)
    except AssertionError:
        # unexpected time-index analysis type; skip timeseries
        handle_timeseries_assertion()
    except Exception as e:
        # formatter or plotting errors; log and render fallback
        fallback_overview()

