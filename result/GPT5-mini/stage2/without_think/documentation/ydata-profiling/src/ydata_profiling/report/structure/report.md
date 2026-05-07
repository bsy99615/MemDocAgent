# `report.py`

## `src.ydata_profiling.report.structure.report.get_missing_items` · *function*

*No documentation generated.*

## `src.ydata_profiling.report.structure.report.render_variables_section` · *function*

## Summary:
Constructs and returns a list of presentation Variable objects for every column described in dataframe_summary by combining the summary data, alert information, configured descriptions, and type-specific renderer output.

## Description:
This function iterates over dataframe_summary.variables and, for each variable (column):
- Collects and formats alerts that relate to the column (handling both a single alert list and a tuple-of-alert-lists structure).
- Builds a template variable mapping that merges the raw summary values with:
  - a per-column description (if enabled in config),
  - formatted alerts,
  - a computed varid (hash of the column name),
  - alert fields set.
- Normalizes the variable "type" when the summary reports a list of possible types (e.g., resolves compatible multi-type combos such as {"Numeric","Categorical"} -> "Categorical"), and validates incompatible type lists.
- Looks up a renderer for the resolved variable type using get_render_map(), and merges the renderer's output into the template variables.
- Optionally determines whether the variable should be ignored (rejected) based on AlertType.REJECTED and config.reject_variables.
- Wraps an optional detailed bottom panel into a Collapse controlled by a ToggleButton.
- Constructs a presentation Variable object with the resolved top/bottom content, anchor_id, name and ignore flag and appends it to the returned list.

Known callers:
- No explicit callers are provided in the supplied context. This function is intended to be invoked by higher-level report assembly code that builds the "variables" section of a profiling report. Typical placement: the report-structure builder stage that assembles the per-variable panels after computing dataset overview and correlations.

Why this is a separate function:
- Centralizes the transformation from raw variable summaries + alerts to presentation-layer Variable objects.
- Encapsulates alert handling, type normalization, and renderer lookup so that the rest of the report-building pipeline can work with a uniform list of Variable objects.
- Keeps presentation logic (ToggleButton / Collapse / Variable creation) separate from data-summary generation.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Used fields:
            * config.variables.descriptions: mapping of column_name -> description string
            * config.show_variable_description: bool, whether to include descriptions
            * config.reject_variables: bool, whether to mark variables as ignored if they have a REJECTED alert
        - Constraints: config must provide the above attributes with expected types.

    dataframe_summary (BaseDescription):
        - Type: ydata_profiling.model.BaseDescription (or compatible object)
        - Required attributes/shape (as used by this function):
            * dataframe_summary.variables: a mapping (e.g., dict) where keys are column names (strings) and values are per-column summary dictionaries. Each summary dict is expected to contain at least the "type" key and may include items that renderers expect (e.g., "top", "bottom", counts, etc.).
            * dataframe_summary.alerts: either:
                - a single iterable (e.g., list) of alert objects, or
                - a tuple of alert iterables (each element is an iterable of alert objects) used for grouped summaries.
              Alert objects must have attributes:
                - column_name (used to select alerts for the current column)
                - fmt() method (returns a formatted alert representation used in template "alerts")
                - fields (iterable of field names touched by the alert)
                - alert_type (e.g., members of AlertType enum)
        - Interdependencies: each element of dataframe_summary.variables is processed while referencing dataframe_summary.alerts to compute per-variable alert info.

## Returns:
    list[Variable]:
        - A list of presentation Variable objects (ydata_profiling.report.presentation.core.Variable), one per entry in dataframe_summary.variables, in the same iteration order as dataframe_summary.variables.items().
        - Each Variable is constructed with:
            * top: template_variables["top"] (renderer-provided or summary-provided)
            * bottom: either None or a Collapse containing detailed content (renderer-provided)
            * anchor_id: template_variables["varid"] (hash of the column name)
            * name: the column name (idx)
            * ignore: boolean indicating whether the variable should be excluded/marked as ignored (True when config.reject_variables is True and the column has an AlertType.REJECTED)
        - Edge cases:
            * If a renderer supplies no "bottom" key or provides a None bottom, the Variable.bottom will be None.
            * If dataframe_summary.alerts is a tuple, the returned "alerts" template entry is a tuple preserving per-summary-list alert formatting.

## Raises:
    ValueError:
        - Condition: If the summary["type"] is a list and the set of types contains more than one element and is not one of the supported multi-type combinations:
            {"Numeric", "Categorical"}, {"Categorical", "Unsupported"}, or {"Categorical", "Text"}.
        - Message example: "Types for {idx} are not compatible: {types}"
    KeyError (possible, implicit):
        - Condition: If a per-variable summary dict lacks the "type" key, accessing summary["type"] will raise KeyError. This is not explicitly raised by the function but is a likely failure mode when inputs are malformed.
    Any exception raised by the renderer:
        - Condition: The render_map lookup returns a callable and that callable may raise its own exceptions; those propagate upward.

## Constraints:
    Preconditions:
        - dataframe_summary.variables must be an iterable mapping (dictionary-like) of column_name -> summary dict.
        - Each summary dict must include a "type" entry (either a string or a list of strings).
        - Alert objects in dataframe_summary.alerts must implement column_name, fields, alert_type, and fmt() as described above.
        - config must contain the attributes referenced in Args and those attributes must be correct types.

    Postconditions:
        - The returned value is a list whose length equals the number of items iterated in dataframe_summary.variables.
        - Each returned Variable object's anchor_id equals hash(column_name) for that column.
        - If config.reject_variables is True, any variable with an AlertType.REJECTED in its alert_types set will have ignore=True; otherwise ignore=False for all variables.

## Side Effects:
    - No I/O is performed (no file/network/stdout).
    - No global state is mutated by this function.
    - It constructs UI/presentation objects (ToggleButton, Collapse, Variable) but does not render or display them; side effects are limited to object instantiation.
    - The function calls into renderer callables returned by get_render_map(); those callables might produce side effects if they are implemented to do so (this function does not itself create such side effects).

## Control Flow:
flowchart TD
    A[Start: get_render_map()] --> B[For each (idx, summary) in dataframe_summary.variables]
    B --> C{Is dataframe_summary.alerts a tuple?}
    C -- No --> D[Collect alerts as flat list, alert_fields as set, alert_types as set]
    C -- Yes --> E[Collect alerts as tuple-of-lists, alert_fields as set across summaries, alert_types as set across summaries]
    D --> F[Build template_variables base: varname, varid, alerts, description, alert_fields]
    E --> F
    F --> G[template_variables.update(summary)]
    G --> H{Is summary["type"] a list?}
    H -- No --> I[variable_type = summary["type"]]
    H -- Yes --> J[types = set(summary["type"])]
    J --> K{len(types) == 1?}
    K -- Yes --> I
    K -- No --> L{types is one of allowed multi-type combos?}
    L -- Yes --> I[variable_type resolved to "Categorical"]
    L -- No --> M[Raise ValueError]
    I --> N[render_map_type = render_map.get(variable_type, render_map["Unsupported"])]
    N --> O[template_variables.update(render_map_type(config, template_variables))]
    O --> P{config.reject_variables?}
    P -- Yes --> Q[ignore = AlertType.REJECTED in alert_types]
    P -- No --> Q[ignore = False]
    O --> R{"bottom" in template_variables and not None?}
    R -- Yes --> S[btn = ToggleButton("More details", anchor_id=varid); bottom = Collapse(btn, bottom_content)]
    R -- No --> T[bottom = None]
    S --> U[var = Variable(top, bottom, anchor_id, name, ignore)]
    T --> U[var = Variable(top, None, anchor_id, name, ignore)]
    U --> V[append var to templs]
    V --> B
    B --> W[Return templs (list of Variables)]

## Examples:
- High-level usage (conceptual):
    1. After computing a BaseDescription for a dataset, call render_variables_section(config, dataframe_summary).
    2. The returned list contains Variable presentation objects for each column. These objects can be inserted into the report tree or root container for rendering.

- Example scenario (described in words):
    Given:
      - config.show_variable_description = True
      - config.variables.descriptions contains {'age': 'Age in years'}
      - dataframe_summary.variables contains {'age': {'type': 'Numeric', 'top': <render block>}}
      - dataframe_summary.alerts contains alerts with column_name == 'age'
    Then:
      - The function will create a template for "age" with varid=hash('age'), include the description "Age in years", populate alerts with formatted alert strings, resolve variable_type='Numeric', call the Numeric renderer, and append a Variable object representing the 'age' panel to the returned list.

## `src.ydata_profiling.report.structure.report.get_duplicates_items` · *function*

## Summary:
Produce a list of Duplicate renderable objects from the provided duplicate-analysis result; returns an empty list when there are no valid duplicates to render.

## Description:
Transforms the input duplicates value into presentation-layer Duplicate renderables suitable for inclusion in a report. The function accepts either a single pd.DataFrame or a Python list of pd.DataFrame objects and maps them to Duplicate instances, assigning names from configuration when a list is provided. All created Duplicate objects receive anchor_id="duplicates".

No known callers were found in the provided code context.

Why this is a separate function:
- Isolates the mapping and naming policy for duplicates (single vs. multi) from higher-level report composition code.
- Enforces the early-abort rule when the provided list contains any None element.

## Args:
- config (Settings)
    - Type: Settings
    - Description: Global configuration object. The function reads config.html.style._labels (expected to be an indexable sequence of strings) to name Duplicate items when duplicates is supplied as a list.
    - Constraint: config.html.style._labels must be indexable up to the number of items enumerated when duplicates is a list.

- duplicates (pd.DataFrame)
    - Type (as annotated in the function signature): pd.DataFrame
    - Actual accepted runtime forms:
        - None: treated as "no duplicates" — the function returns an empty list.
        - a single pd.DataFrame: converted to a single Duplicate named "Most frequently occurring".
        - a list of pd.DataFrame objects: each entry is converted to one Duplicate; labels are taken from config.html.style._labels by index.
    - Important implementation detail: the function checks isinstance(duplicates, list) to detect the multi-item case. Other sequence types (e.g., tuple) are NOT treated as a list and will follow the single-DataFrame branch.

## Returns:
- List[Renderable]
    - Description: A list of Duplicate renderable objects (possibly empty).
    - Return cases:
        - [] (empty list):
            - duplicates is None
            - len(duplicates) == 0 (applies to an empty DataFrame or empty list)
            - duplicates is a list and any element in that list is None (the function returns immediately without producing any items)
        - [Duplicate(...)]:
            - duplicates is a single non-empty pd.DataFrame — a single Duplicate is returned with name "Most frequently occurring" and anchor_id "duplicates".
        - [Duplicate(...), ...]:
            - duplicates is a list of pd.DataFrame objects with no None elements. Each Duplicate.name is taken from config.html.style._labels at the corresponding index; anchor_id is "duplicates".

## Raises:
- This function does not explicitly raise exceptions.
- Exceptions that may be propagated from operations inside the function (callers may want to guard against these):
    - IndexError: if duplicates is a list longer than the available entries in config.html.style._labels (accessing config.html.style._labels[idx] is out of range).
    - TypeError: if duplicate is a non-None object for which len(duplicates) is not supported.
    - AttributeError: if config does not expose html, style, or _labels as expected.
    - Exceptions raised by the Duplicate constructor (e.g., if the provided DataFrame does not meet Duplicate's internal expectations).

## Constraints:
- Preconditions:
    - config is a valid Settings object and config.html.style._labels is indexable.
    - If passing a list for duplicates, ensure it contains only pd.DataFrame objects (no None elements) and that labels exist for every index used.
- Postconditions:
    - Returned list contains zero or more Duplicate objects with anchor_id set to "duplicates".
    - The function does not modify its input arguments.

## Side Effects:
- The function itself performs no I/O, logging, or global-state mutation.
- Any side effects are the result of behaviors in the Duplicate constructor (not caused by this function).

## Control Flow:
flowchart TD
    Start --> CheckEmpty{duplicates is None or len(duplicates) == 0?}
    CheckEmpty -- Yes --> ReturnEmpty[Return []]
    CheckEmpty -- No --> IsList{isinstance(duplicates, list)?}
    IsList -- Yes --> HasNone{any(d is None for d in duplicates)?}
    HasNone -- Yes --> ReturnEmpty
    HasNone -- No --> ForEach[for idx, df in enumerate(duplicates): create Duplicate(duplicate=df, name=config.html.style._labels[idx], anchor_id="duplicates")]
    ForEach --> ReturnList[Return list of Duplicate items]
    IsList -- No --> Single[create Duplicate(duplicate=duplicates, name="Most frequently occurring", anchor_id="duplicates")]
    Single --> ReturnSingle[Return [Duplicate(...)]]

## Examples (narrative, no code):
- Single-DataFrame case:
    - Input: a non-empty pd.DataFrame representing the single most frequent duplicate group.
    - Output: a list with one Duplicate named "Most frequently occurring" and anchor_id "duplicates".
    - Note: if the DataFrame is empty (len == 0), the function returns [].

- List-of-DataFrames case:
    - Input: a Python list of pd.DataFrame objects and config where config.html.style._labels contains at least as many labels as the list length.
    - Output: one Duplicate per list element; Duplicate.name is taken from config.html.style._labels at the same index.
    - Important edge-case: if any element in the list is None, the function returns [] immediately (no partial results). If config.html.style._labels is too short, an IndexError will propagate.

- Non-list sequence (e.g., tuple) case:
    - If duplicates is a tuple of DataFrames, it is NOT treated as a list by the isinstance check; the function will attempt to treat the tuple as a single DataFrame value and create one Duplicate named "Most frequently occurring". Callers that intend multi-item behavior must pass a Python list.

## `src.ydata_profiling.report.structure.report.get_definition_items` · *function*

## Summary:
Return a list of Renderable items representing column definitions; produces a single Duplicate renderable named "Columns" with anchor_id "definitions" when a non-empty DataFrame is provided, otherwise returns an empty list.

## Description:
Creates presentation items for a definitions DataFrame used in the profiling report. The function performs a presence-and-non-emptiness check on the provided object and, only when that check succeeds, constructs one Duplicate renderable containing the provided object.

Known callers within the codebase:
- No direct callers were discovered in the provided retrieval of call sites. Based on the function's purpose and naming, it is intended to be invoked by report assembly or report-structure builder code that aggregates sections of a profiling report (for example, modules that collect overview, correlations, and definitions into a final report).

Why this logic is extracted:
- Encapsulates the decision logic whether to include a definitions section and the exact construction of the Duplicate renderable in a single place, avoiding duplication of the presence-check and construction at multiple call sites.

## Args:
    definitions (pd.DataFrame | None)
        The object expected to be a pandas DataFrame containing column definitions/metadata, or None.
        - Allowed values:
            * A pandas DataFrame (or any object supporting len()) with zero or more rows.
            * None, to indicate missing definitions.
        - Interdependencies:
            * If definitions is None or len(definitions) == 0, the function will not create a Duplicate and returns an empty sequence.

## Returns:
    Sequence[Renderable]
        Always returns a Python list object (typed as Sequence[Renderable]):
        - If definitions is None OR len(definitions) == 0: returns [] (empty list).
        - If definitions is not None AND len(definitions) > 0: returns [Duplicate(...)] — a list containing exactly one Duplicate renderable constructed with:
            * duplicate = definitions
            * name = "Columns"
            * anchor_id = "definitions"
        No other return shapes are produced by this function.

## Raises:
    - The function itself does not explicitly raise exceptions.
    - Possible exceptions that may propagate out of this function (not raised explicitly here):
        * TypeError or other exceptions from calling len(definitions) if definitions does not support len().
        * Any exceptions raised by the Duplicate constructor when invoked with the provided arguments.

## Constraints:
    Preconditions:
        - The caller should provide either None or an object appropriate for presentation (typically a pandas.DataFrame).
        - If providing a non-DataFrame object, it must support len() and be acceptable to the Duplicate constructor; otherwise an exception may be raised by len() or Duplicate.

    Postconditions:
        - The returned value is always a list.
        - If non-empty, the list will contain exactly one Duplicate renderable with the attributes listed in Returns.

## Side Effects:
    - This function performs no I/O and does not mutate global state.
    - It constructs and returns renderable wrapper objects; any I/O or rendering side effects occur later, when those renderables are processed by presentation/rendering code.

## Control Flow:
flowchart TD
    Start --> CheckDefinitions
    CheckDefinitions{definitions is not None AND len(definitions) > 0}
    CheckDefinitions -- True --> ConstructDuplicate[Construct Duplicate(duplicate=definitions, name="Columns", anchor_id="definitions")]
    ConstructDuplicate --> Append[Append Duplicate to items list]
    Append --> ReturnNonEmpty[Return items list containing the Duplicate]
    CheckDefinitions -- False --> ReturnEmpty[Return empty items list]
    ReturnEmpty --> End
    ReturnNonEmpty --> End

## Examples:
Example A — Non-empty pandas DataFrame (typical use):
- Given defs is a pandas.DataFrame with N > 0 rows:
    - items = get_definition_items(defs)
    - Result: items is a list with one element: a Duplicate renderable constructed with duplicate=defs, name="Columns", anchor_id="definitions".
    - Downstream: a report assembler would include this item when assembling sections to render.

Example B — None or empty DataFrame:
- Given defs is None OR defs is a pandas.DataFrame with zero rows:
    - items = get_definition_items(defs)
    - Result: items == [] (empty list).
    - Downstream: report assembler should skip rendering a definitions section when it receives an empty list.

Implementation notes for reimplementation:
- Perform the None check and then len() check exactly as in the source: if definitions is not None and len(definitions) > 0.
- Use the Duplicate constructor with the three keyword arguments duplicate, name, and anchor_id set as specified.
- Return a Python list (e.g., items = []; items.append(...); return items).

## `src.ydata_profiling.report.structure.report.get_sample_items` · *function*

## Summary:
Convert a provided sample payload into a list of presentation Renderable items — either individual Sample renderables or Container-wrapped batches of Sample renderables — suitable for inclusion in the report presentation tree.

## Description:
Converts the incoming "sample" payload (expected at runtime to be either an iterable/sequence of sample model objects or a tuple of sequences representing parallel sample batches) into a list of presentation Renderable objects:

- For a plain sequence/iterable (the common single-run case), each element becomes a presentation Sample renderable containing obj.data and metadata (name, anchor_id, caption).
- For a tuple of sequences (batch / comparison mode), the function zips the sequences together and for each zipped group creates a Container whose children are Sample renderables; the Container is marked with sequence_type "batch_grid" and includes batch metadata.

Known callers / typical call sites:
- Report-building and presentation-layer code that assembles a report tree or section containing sample previews (for example, higher-level "report structure" builders that add a dataset preview or per-variable sample sections).
- Presentation factories or orchestrators that convert model-level sample objects into Renderable instances before rendering. (No single-file call sites were provided in the snippet; the above describes typical usage contexts in this codebase.)

Why this logic is extracted:
- Responsibility separation: this function encapsulates the mapping between model-level sample objects (objects exposing id, data, name, caption) and presentation-level Renderable instances (Sample and Container). Extracting it centralizes transformation rules (label selection, batch grouping, anchoring) and keeps higher-level report builders focused on section composition rather than object-to-renderable conversion.

## Args:
    config (Settings)
        - The global Settings object used to obtain presentation labels and styling metadata.
        - Required to supply config.html.style._labels when building presentation Sample names in batched mode.
    sample (dict)
        - NOTE (important): although the function annotation declares `sample: dict`, at runtime the function treats `sample` as either:
            * a sequence/iterable of model-like sample objects (each object must provide attributes: id, data, name, caption), or
            * a tuple of sequences (e.g., (seq_a, seq_b, ...)) representing parallel sample streams to be displayed in batches.
        - Each sample element (obj) is expected to have the following attributes:
            * obj.data  -> payload passed to the presentation Sample (commonly a pandas.DataFrame)
            * obj.name  -> human-readable name (used for Sample.name or Container.name)
            * obj.id    -> string anchor id used for Sample.anchor_id
            * obj.caption -> optional caption string (may be None)
        - Interdependencies:
            * When sample is a tuple, config.html.style._labels is indexed by the element index to set per-column labels in the created Sample renderables. If that list is shorter than the number of items in a zipped group, an IndexError may occur.

## Returns:
    List[Renderable]
    - A list of presentation Renderable objects suitable for insertion into the report tree.
    - Possible returned element types:
        * presentation Sample (ydata_profiling.report.presentation.core.sample.Sample) objects when the input is a single sequence.
        * Container objects (ydata_profiling.report.presentation.core.container.Container) whose content['items'] is a sequence of Sample renderables when the input is a tuple of sequences (batched display).
    - Edge/empty-case returns:
        * If sample is empty (empty iterable) the function returns an empty list [].
        * If sample is an empty tuple, zip(*sample) yields no groups and the function returns [].
    - Postconditions:
        * Every returned item is a Renderable instance and has content populated with expected keys (Samples contain content["sample"] and content["caption"]; Containers contain content["items"] and content["nested"]).

## Raises:
The function itself contains no explicit raise statements but may propagate exceptions produced by its inputs or attribute access:
    - AttributeError
        * If elements of `sample` do not expose required attributes (id, data, name, caption), attribute access (obj.data, obj.name, obj.id, obj.caption) will raise AttributeError.
    - IndexError
        * In the tuple / batched branch the code uses config.html.style._labels[idx] for labels; if that list is shorter than the number of elements in a zipped group, an IndexError will be raised.
    - TypeError
        * If `sample` is provided as a non-iterable object (and is not a tuple or sequence), iteration or isinstance checks may raise TypeError in calling code or result in incorrect behaviour.
    - Any exceptions raised by slugify(s[0].name) if s[0].name cannot be converted to str are propagated (e.g., TypeError).
Note: These exceptions are caused by malformed inputs or misconfigured Settings; the function does not explicitly validate or catch them.

## Constraints:
Preconditions:
    - config must be a valid Settings instance that contains html.style._labels when batched labeling is required.
    - Input `sample` must be either:
        * a sequence/iterable of sample-model objects (each with data, id, name, caption), or
        * a tuple of sequences representing parallel sample streams (each inner sequence must be indexable/iterable and elements must provide the required attributes).
    - When using the tuple/batched mode, the caller should ensure inner sequences are aligned for zip semantics (note: zip will truncate to the shortest sequence).
Postconditions:
    - Returned items list contains only objects implementing the Renderable contract (i.e., .content dict and a render() implementation must exist on the concrete renderer used later).
    - No global state or external resources are modified by this function.

## Side Effects:
    - None: the function does not perform I/O, network access, or mutate external/global variables.
    - The only mutation is the creation of new Renderable objects (Sample and Container) returned to the caller; it does not mutate the provided sample objects.

## Control Flow:
flowchart TD
    Start[Start: call get_sample_items(config, sample)] --> IsTuple{isinstance(sample, tuple)?}
    IsTuple -->|Yes| ZipLoop[for each s in zip(*sample):]
    ZipLoop --> BuildSampleList[build list of presentation Sample renderables:
      for idx, obj in enumerate(s) -> Sample(sample=obj.data, name=config.html.style._labels[idx], anchor_id=obj.id, caption=obj.caption)]
    BuildSampleList --> MakeContainer[Container(items=list_of_Sample, sequence_type="batch_grid", batch_size=len(sample), anchor_id=f"sample_{slugify(s[0].name)}", name=s[0].name)]
    MakeContainer --> AppendContainer[append Container to items list]
    AppendContainer --> ZipLoop
    ZipLoop --> AfterTuple[after processing all zipped groups -> return items]
    IsTuple -->|No| SeqLoop[for each obj in sample:]
    SeqLoop --> MakeSample[Sample(sample=obj.data, name=obj.name, anchor_id=obj.id, caption=obj.caption)]
    MakeSample --> AppendSample[append Sample to items list]
    AppendSample --> SeqLoop
    SeqLoop --> AfterSeq[after processing sequence -> return items]

## Examples:
Example 1 — single sequence of sample-model objects (typical usage)
    # Suppose `samples` is a list of model-like objects where each has .data (DataFrame), .name, .id, .caption
    items = get_sample_items(config, samples)
    # Result: items is a list of presentation Sample renderables; each item.content["sample"] == obj.data

Example 2 — batched / tuple-of-sequences mode (parallel comparison)
    # Suppose sample_a and sample_b are lists aligned by index; provide as a tuple for side-by-side display
    items = get_sample_items(config, (sample_a, sample_b))
    # Result: items is a list of Container renderables; each Container.content["items"] is a sequence of Sample renderables,
    # and Container.content includes batch metadata: sequence_type="batch_grid", batch_size=len((sample_a, sample_b))

Example 3 — handling empty input
    items = get_sample_items(config, [])
    assert items == []

Notes and implementation hints for reimplementation:
    - Do not assume the type annotation `sample: dict` is correct; implement the function to accept a sequence/iterable or a tuple of sequences as described.
    - Use zip(*sample) (as in the original) to create grouped tuples when `sample` is a tuple; remember zip truncates to the shortest input sequence.
    - When creating per-column Sample names in the batch case, index into config.html.style._labels; ensure that list is long enough to avoid IndexError or guard accordingly if defensive behavior is required.
    - Use slugify(s[0].name) to create the container anchor_id; ensure s[0].name is convertible to str.

## `src.ydata_profiling.report.structure.report.get_interactions` · *function*

## Summary:
Constructs a list of presentation Container items that represent interaction plots between a set of x-variables and their y-variables; the result is a list of Renderable containers ready to be embedded in the report tree.

## Description:
This function transforms the interactions data structure (a nested mapping of x-column -> y-column -> plot(s)) into a list of presentation-layer Renderable objects. For each x-column it produces a Container whose children are either single Image-type widgets (one per y) or a batched Container of multiple z-dimension Image-type widgets (when multiple plots are provided for a single y). When a plot entry is an empty string, an HTML placeholder is used instead.

Known callers:
- No direct callers were found in the provided memory snapshot. In the codebase this function is intended to be invoked by report-building code that assembles the "interactions" section of a profile/report (i.e., a higher-level report generator that collects plots and converts them into presentation Renderable items).

Why this logic is extracted:
- Converts a raw nested plot data structure into a structured presentation tree (Renderable objects) with consistent anchor ids, names, batching and sequencing metadata. Extracting this logic centralizes the mapping rules (how lists vs single plots are handled, anchor id naming, batch sizing, sequence type selection) so higher-level report assembly code can remain declarative and focused on composition.

## Args:
    config (Settings):
        - The global settings object used for rendering metadata.
        - Required attributes used by this function:
            * config.plot.image_format: format string forwarded to ImageWidget construction.
            * config.html.style._labels: sequence of labels used as names for z-dimension plots (its length is used as the batch_size).
        - Type: Settings (from ydata_profiling.config). Must expose the attributes above at call time.

    interactions (dict):
        - Nested mapping holding the interaction plots.
        - Expected shape (informal):
            {
                x_col_1: {
                    y_col_a: splot_or_list,
                    y_col_b: splot_or_list,
                    ...
                },
                x_col_2: { ... },
                ...
            }
        - Interpretation of splot_or_list:
            * If splot is not a list: treated as a single plot (e.g., a path, HTML string, or image payload — the function forwards it to an Image-type widget).
            * If splot is a list: treated as multiple z-dimension plots. Each element zplot in the list is either:
                - a non-empty string representing a plot (forwarded to an Image-type widget), or
                - the empty string "" indicating that no plot is present for that label (in which case an HTML placeholder is used).
        - Keys x_col and y_col are used to build human-facing names and anchor ids.

Notes on interdependencies:
- The code depends on config.html.style._labels: when splot is a list, the function enumerates that list and uses the label at the same index as the item name; therefore the length and indexing of _labels must match the intended batching of zplots.

## Returns:
    list[Renderable]:
        - A list of Container instances (subclasses of Renderable) — one per x-column in the input interactions mapping.
        - Each returned Container (for an x-column) contains:
            * content['items']: a list of child Renderable objects corresponding to each y-column under that x-column. Each child is either:
                - an Image-type widget constructed with the single splot for that y, or
                - a Container (sequence_type "batch_grid") containing one Image-type widget per zplot (or HTML placeholder when a zplot is empty).
            * metadata keys on the Container include name (set to the x-column or y-column as appropriate), anchor_id (constructed via slugify), nested flag (outer container uses nested when total x-columns > 10), and sequence_type.
        - Edge cases:
            * If interactions is empty, the function returns an empty list.
            * If a splot list contains empty strings, those positions are represented by an HTML placeholder Renderable rather than an image.

## Raises:
    - The function does not explicitly raise exceptions.
    - Runtime errors may occur if:
        * config lacks the attributes accessed (e.g., config.plot.image_format or config.html.style._labels) — AttributeError will propagate.
        * config.html.style._labels is not indexable or its length is inconsistent with intended use — IndexError may propagate during enumeration/lookup.
        * Provided interaction structures are not mappings or contain unexpected types — TypeError/AttributeError may propagate when calling .items() or iterating.

## Constraints:
Preconditions:
    - interactions must be an iterable of (x_col, y_cols) pairs (i.e., a mapping supporting .items()).
    - Each y_cols must be a mapping supporting .items().
    - config must provide the attributes used in the function (plot.image_format and html.style._labels).

Postconditions:
    - The returned list has one Container-like Renderable per top-level key in interactions (iteration order of interactions.items()).
    - Each returned Container's content['items'] corresponds to the y-columns of that x-column in the same iteration order.
    - Anchor ids in the returned Renderables are deterministic and built by slugifying the original column names via slugify(x_col)/slugify(y_col).

## Side Effects:
    - Pure object construction only: the function instantiates Renderable-derived objects (Image-type widgets, Container, HTML) and composes them into a list. There is no file, network, or stdout I/O performed here.
    - No mutation of external state or global variables is performed by this function.
    - No external service calls.

## Control Flow:
flowchart TD
    Start[Start get_interactions] --> ForX[For each x_col, y_cols in interactions.items()]
    ForX --> InitItems[items = []]
    InitItems --> ForY[For each y_col, splot in y_cols.items()]
    ForY --> IsList{isinstance(splot, list)?}
    IsList -- No --> CreateSingleImage[Create ImageWidget(splot) with name=y_col and anchor interactions_x_y]
    CreateSingleImage --> AppendItem[items.append(image widget)]
    IsList -- Yes --> CreateBatchContainer[Create Container(sequence_type="batch_grid", batch_size=len(_labels), name=y_col)]
    CreateBatchContainer --> ForZ[For each idx, zplot in enumerate(splot)]
    ForZ --> IsEmptyZ{zplot == ""?}
    IsEmptyZ -- No --> CreateZImage[Create ImageWidget(zplot) name=config.html.style._labels[idx]]
    IsEmptyZ -- Yes --> CreatePlaceholder[Create HTML placeholder using config.html.style._labels[idx]]
    CreateZImage --> AddToBatch
    CreatePlaceholder --> AddToBatch
    AddToBatch --> ForZ
    ForZ --> AppendBatch[items.append(batch container)]
    AppendItem --> ForY
    AppendBatch --> ForY
    ForY --> AfterY[After processing all y_cols]
    AfterY --> MakeOuterContainer[Create Container(items, sequence_type="tabs" if len(items)<=10 else "select", name=x_col, nested=(len(interactions)>10))]
    MakeOuterContainer --> AppendTitems[titems.append(outer container)]
    AppendTitems --> ForX
    ForX --> End[Return titems list]

## Examples:
- Typical (conceptual) usage scenario:
    - A report builder collects interaction plot output into a nested dictionary where keys are x-column names and values are dicts mapping y-column names to either:
        * a single image payload (string/bytes) representing the interaction plot, or
        * a list of image payloads for additional z-dimension plots (with empty-string entries when a plot is missing).
    - The report builder calls get_interactions(config, interactions) to convert that structure into presentation Renderable Containers that include appropriate anchor ids, names and batching metadata. The returned list is then appended into the report's root presentation tree.

- Minimal concrete example (pseudo-call):
    interactions = {
        "age": {
            "income": "<image-payload-or-ref>",
            "education": ["<zplot1>", "", "<zplot3>"]
        }
    }
    items = get_interactions(config, interactions)
    # items is a list of Container Renderables that can be inserted into the report tree.

## `src.ydata_profiling.report.structure.report.get_report_structure` · *function*

## Summary:
Compose the top-level report presentation tree (Root) by assembling section Containers (Overview, Variables, Interactions, Correlations, Missing values, Sample, Duplicate rows) from the provided summary and configuration; returns a Root object ready for rendering.

## Description:
- Known callers:
    - No explicit in-repository call sites were provided in the supplied context. Typical callers are higher-level report builders that take a profiling Summary (BaseDescription) and Settings and produce a final renderable report (for example a function that serializes the Root to HTML or writes the report to disk). This function represents the report-structure assembly stage in the profiling pipeline immediately after summary generation and before rendering/serialization.
- Purpose and responsibility boundary:
    - This function orchestrates which major report sections are present and in what order. It does not implement the details of each section; instead it delegates construction of each section's Renderable items to specialized helpers:
        * get_dataset_items -> Overview container items
        * render_variables_section -> per-variable Variable items wrapped in a Dropdown
        * get_interactions -> interactions (scatter/interaction plots)
        * get_correlation_items -> correlations Container or None
        * get_missing_items -> missing values items
        * get_sample_items -> sample preview items
        * get_duplicates_items -> duplicate row renderables
    - The function enforces the overall structure and meta-level presentation choices (sequence_type for the top-level sections container, anchoring and naming for the major sections, whether to include or omit sections based on summary contents).
    - It also manages a one-step progress indicator (tqdm) controlled by config.progress_bar.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Required/used fields (directly read by this function):
            * config.progress_bar (bool): whether to show the progress bar; the function inverts this to compute tqdm.disable.
            * config.html.full_width (bool): passed to the top-level sections Container as full_width.
            * config.html.style: passed to the Root constructor as the style argument (must be a style-like object).
        - Note: many helpers called by this function read additional config fields (plot settings, labels, variable/duplicate naming, etc.). Those helper-level requirements are not re-checked here but must be satisfied at call time.

    summary (BaseDescription):
        - Type: ydata_profiling.model.BaseDescription (or compatible object)
        - Expected attributes accessed in this function:
            * summary.alerts: alerts container forwarded to get_dataset_items
            * summary.variables: mapping-like collection of variables (len(summary.variables) checked)
            * summary.scatter: interactions mapping passed to get_interactions
            * summary.sample: sample payload passed to get_sample_items
            * summary.duplicates: duplicates payload passed to get_duplicates_items
            * Other attributes required by delegated helpers (e.g., summary.correlations) are used inside those helpers; they must be present if the helpers depend on them.
        - Interdependencies:
            * Whether a section is included depends on the truthiness or length of these attributes (e.g., variables included only if len(summary.variables) > 0).

## Returns:
    Root
    - A Root presentation object containing:
        * title: "Root" (the root name passed to the Root constructor).
        * sections: a Container (sequence_type="sections") whose items are the assembled high-level section Renderable nodes in the order assembled in the function. The Container receives full_width=config.html.full_width.
            - Common items (present when corresponding inputs exist):
                1. Overview: Container wrapping the list returned by get_dataset_items(config, summary, alerts), named "Overview", anchor_id "overview", sequence_type "tabs".
                2. Variables: Dropdown (if summary.variables not empty) with items=list(summary.variables) and item=Container(render_variables_section(...), sequence_type="accordion", anchor_id "variables").
                3. Interactions: Container of get_interactions(...) items, sequence_type "tabs" if <=10 items else "select", anchor_id "interactions".
                4. Correlations: the Container returned by get_correlation_items(config, summary) (appended if not None).
                5. Missing values: Container wrapping get_missing_items(config, summary) when that list is non-empty, anchor_id "missing".
                6. Sample: Container wrapping sample items from get_sample_items(config, summary.sample) when non-empty, anchor_id "sample".
                7. Duplicate rows: Container wrapping duplicate_items from get_duplicates_items(config, summary.duplicates) when non-empty; sequence_type "batch_grid", batch_size=len(duplicate_items), anchor_id "duplicate".
        * footer: an HTML Renderable containing the static attribution string 'Report generated by <a href="https://ydata.ai/...">YData</a>.'
        * style: set to config.html.style passed to Root.
    - Edge-case returns:
        * The function always returns a Root instance (it does not return None). The Root may contain only the Overview section (and footer) if all other inputs are empty/absent.

## Raises:
    - This function does not explicitly raise exceptions itself.
    - It will propagate exceptions raised by:
        * Missing attributes on config or summary (AttributeError).
        * Incorrect types for summary attributes or helper return values (TypeError, ValueError).
        * Any exception originating from the delegated helper functions:
            - get_dataset_items, render_variables_section, get_interactions, get_correlation_items, get_missing_items, get_sample_items, get_duplicates_items.
        * tqdm may raise if given incompatible parameters, though this is unlikely with the current usage.
    - Practical examples of propagated errors:
        * AttributeError if config.html is missing.
        * KeyError/ValueError if a helper expects keys not present in summary.

## Constraints:
    Preconditions:
        - config must be a Settings-like object with at least:
            * progress_bar (bool)
            * html.full_width (bool)
            * html.style (style object)
        - summary must be a BaseDescription-like object exposing:
            * alerts, variables, scatter, sample, duplicates and any structures required by the specific helpers (e.g., summary.correlations for correlations).
        - Helpers must accept and correctly handle the values passed (they impose further preconditions for plotting, labels, etc.).

    Postconditions:
        - Returns a Root instance whose sections Container contains zero-or-more section Renderables in deterministic order (Overview first, then conditional sections as assembled).
        - The progress bar (if enabled) is advanced one step via pbar.update() before returning.
        - No input arguments (config, summary) are mutated by this function itself (helpers may mutate their inputs or config temporarily; such behavior is delegated to those helpers).

## Side Effects:
    - Progress display: when config.progress_bar is True, a tqdm progress bar instance is created; this may write to stdout/Jupyter output (tqdm side effect).
    - Object construction: instantiates many presentation Renderable objects (Container, Dropdown, HTML, Root and helper-produced items) but does not render or write them to disk.
    - Indirect side effects via helpers:
        * Plot generation performed by helpers (for correlations, timeseries, interactions) may create matplotlib figures and have typical plotting side effects (figure allocation) and must be managed/closed by those helpers or downstream code.
        * Helper constructors or renderers may perform I/O or other side effects — exceptions or I/O performed by helpers will propagate.
    - No direct file, network, database, or global-state mutations are performed in this function itself.

## Control Flow:
flowchart TD
    Start[Start: get_report_structure] --> Setup[tqdm(total=1, desc="Generate report structure", disable=not config.progress_bar)]
    Setup --> ReadAlerts[alerts = summary.alerts]
    ReadAlerts --> BuildSectionsInit[section_items = [Overview Container(get_dataset_items(...))]]
    BuildSectionsInit --> CheckVariables{len(summary.variables) > 0?}
    CheckVariables -- Yes --> AddVariables[append Dropdown(item=Container(render_variables_section(...)))]
    CheckVariables -- No --> SkipVariables
    AddVariables --> GetInteractions
    SkipVariables --> GetInteractions
    GetInteractions[get_interactions(config, summary.scatter) -> scatter_items] --> CheckScatter{len(scatter_items) > 0?}
    CheckScatter -- Yes --> AddInteractions[append Container(scatter_items, sequence_type="tabs" if <=10 else "select")]
    CheckScatter -- No --> SkipInteractions
    AddInteractions --> GetCorr
    SkipInteractions --> GetCorr
    GetCorr[get_correlation_items(config, summary) -> corr] --> CheckCorr{corr is not None?}
    CheckCorr -- Yes --> AddCorr[append corr]
    CheckCorr -- No --> SkipCorr
    AddCorr --> GetMissing
    SkipCorr --> GetMissing
    GetMissing[get_missing_items(config, summary) -> missing_items] --> CheckMissing{len(missing_items) > 0?}
    CheckMissing -- Yes --> AddMissing[append Container(missing_items, sequence_type="tabs")]
    CheckMissing -- No --> SkipMissing
    AddMissing --> GetSample
    SkipMissing --> GetSample
    GetSample[get_sample_items(config, summary.sample) -> sample_items] --> CheckSample{len(sample_items) > 0?}
    CheckSample -- Yes --> AddSample[append Container(sample_items, sequence_type="tabs")]
    CheckSample -- No --> SkipSample
    AddSample --> GetDuplicates
    SkipSample --> GetDuplicates
    GetDuplicates[get_duplicates_items(config, summary.duplicates) -> duplicate_items] --> CheckDup{len(duplicate_items) > 0?}
    CheckDup -- Yes --> AddDuplicates[append Container(duplicate_items, sequence_type="batch_grid", batch_size=len(duplicate_items))]
    CheckDup -- No --> SkipDup
    AddDuplicates --> BuildRoot
    SkipDup --> BuildRoot
    BuildRoot[sections = Container(section_items, name="Root", sequence_type="sections", full_width=config.html.full_width)] --> pbarUpdate[pbar.update()]
    pbarUpdate --> Footer[footer = HTML(attribution string)]
    Footer --> ReturnRoot[return Root("Root", sections, footer, style=config.html.style)]
    ReturnRoot --> End

## Examples:
- Typical usage (pseudo-code):
    try:
        root = get_report_structure(config, summary)
        # root is now a Renderable Root object; hand it to the renderer that serializes to HTML/PDF
        renderer.render(root, output="report.html")
    except Exception as e:
        # handle errors from helpers, missing fields, or plotting issues
        logger.error("Failed to assemble report structure: %s", e)
        raise

- Behavior-driven example:
    Given a summary with:
        - summary.alerts present,
        - summary.variables empty,
        - summary.scatter containing 2 interaction groups,
        - summary.correlations empty,
        - summary.sample non-empty,
        - summary.duplicates None,
    Then:
        - The returned Root will contain sections: Overview, Interactions (as tabs), Sample, and the footer. No Variables, Correlations, Missing values or Duplicate rows sections will be included.

Notes for reimplementation:
    - Keep the one-step progress bar behavior (tqdm total=1 and pbar.update() prior to returning) to preserve UX parity.
    - Preserve anchor_id and sequence_type choices used here (overview -> "overview", variables -> "variables-dropdown"/"variables", interactions -> "interactions", missing -> "missing", sample -> "sample", duplicate -> "duplicate"); these anchor ids are referenced elsewhere in the report generation/JS/CSS and must remain stable.
    - Do not inline helper logic; delegate to the helper functions and respect their return contracts (lists of Renderable or None for correlations).

