# `correlations.py`

## `src.ydata_profiling.report.structure.correlations.get_correlation_items` · *function*

## Summary:
Constructs the renderable "Correlations" section for a report by converting the correlation matrices present in the summary into Image and CorrelationTable renderable items and grouping them into Containers; returns a top-level Container (tabs) when there are items or None when no correlations are available.

## Description:
This function is called by report-building/structure code when assembling the "Correlations" section of a profiling report. It encapsulates the logic for turning the correlation matrices discovered during profiling (summary.correlations) into presentation-layer items (images and optional tables) and arranging them into Container nodes with appropriate metadata (names, anchor ids, sequence types).

Why this is a separate function:
- It centralizes the mapping from correlation-summary data to presentation items and the policy decisions about when to include tables vs. only heatmaps.
- It keeps presentation construction separate from profiling logic (summary generation) and rendering logic (concrete renderer implementations), making unit-testing and changes to presentation layout easier.

Known callers:
- No concrete call sites were available in the provided context. Typical callers are report-structure assembly functions which build the report tree and collect the various sections (e.g., a correlations-section factory invoked by the top-level report builder).

## Args:
    config (Settings):
        - Configuration object exposing plotting and HTML/presentation options used to control:
            * config.plot.image_format: image format passed to Image items (e.g., svg or png).
            * config.plot.correlation.cmap and other plot.* options used by plot.correlation_matrix (indirectly).
            * config.correlation_table: boolean flag that toggles inclusion of correlation tables alongside heatmaps.
            * config.html.style._labels: sequence of descriptive labels used as per-item names when summary entries are lists.
        - Preconditions: config must provide these attributes; otherwise AttributeError will be raised by attribute access.

    summary (BaseDescription):
        - Summary object produced by the profiling pipeline that must include:
            * summary.correlations: a mapping/dict-like object whose keys are correlation method names and whose values are either:
                - a pandas.DataFrame (a single correlation matrix), or
                - a list of pandas.DataFrame (multiple matrices, for example one per variable group/label).
        - Allowed keys (expected by this function): "pearson", "spearman", "kendall", "phi_k", "cramers", "auto".
        - Interdependencies:
            * If a value in summary.correlations is a list, this function uses config.html.style._labels to name/batch the per-item images/tables; their lengths are not validated — mismatches do not raise here but may produce confusing output.

## Returns:
    Optional[Renderable]:
        - Returns a Container renderable representing the "Correlations" section when at least one correlation item was created.
            * Container.content['items'] is a list of Renderable items; the top-level Container has:
                - sequence_type = "tabs"
                - name = "Correlations"
                - anchor_id = "correlations_tab"
            * Each item inside may be:
                - an Image (single heatmap) or a Container (tabs or batch_grid containing Images), or
                - a Container that groups a diagrams grid and a tables grid into tabs (if config.correlation_table is True).
        - Returns None when no correlation matrices were present in summary.correlations (i.e., no items were appended).
        - All images are created by calling plot.correlation_matrix(...) and then wrapped in Image objects; tables are created as CorrelationTable instances.

## Raises:
    KeyError:
        - If summary.correlations contains a key not present in the function's local key_to_data mapping, the lookup key_to_data[key] raises KeyError.

    ValueError:
        - May be raised indirectly by Image.__init__ if the returned image payload from plot.correlation_matrix(...) is None and Image enforces non-None payload (Image.__init__ raises ValueError when image is None).

    Propagated exceptions from dependency calls:
        - Any exception raised by plot.correlation_matrix (for example due to invalid matrix/data types), by Image, CorrelationTable, or Container constructors will propagate through this function. The function does not catch exceptions.

## Constraints:
    Preconditions:
        - summary must provide a mapping attribute 'correlations'.
        - Each mapping value should be a pandas.DataFrame or a list of pandas.DataFrame. Non-conforming items will likely cause downstream exceptions in plot.correlation_matrix or CorrelationTable.
        - config must provide the attributes referenced above (config.plot.image_format, config.correlation_table, config.html.style._labels).
    Postconditions:
        - If the function returns a Container, the Container content contains an item per correlation-method entry in summary.correlations that had a valid value; the returned Container has sequence_type "tabs" and name "Correlations".
        - If the function returns None, no correlation-related presentation items were appended (items list empty).

## Side Effects:
    - Calls plot.correlation_matrix(config, data, vmin=vmin), which creates matplotlib figures/axes and returns a string payload representing the image (the plotting call itself has matplotlib side effects such as creating figures).
    - No file or network I/O is performed directly by this function. Any I/O performed is a consequence of operations inside plot.correlation_matrix or a renderer later consuming the returned Renderable items.
    - No global state in this function is mutated. The function constructs and returns presentation objects only.

## Control Flow:
flowchart TD
    Start --> CheckCorrelations
    CheckCorrelations{summary.correlations empty?}
    CheckCorrelations -- Yes --> BuildEmptyContainer
    BuildEmptyContainer --> CreateContainer
    CheckCorrelations -- No --> ForEachKey
    ForEachKey --> GetVminName["lookup vmin,name via key_to_data[key]"]
    GetVminName --> IsList{isinstance(item, list)?}
    IsList -- Yes --> BuildDiagramsLoop
    BuildDiagramsLoop --> DiagramsGrid["Container(diagrams, sequence_type=batch_grid)"]
    DiagramsGrid --> HasTables{config.correlation_table?}
    HasTables -- Yes --> BuildTablesLoop
    BuildTablesLoop --> TablesTab["Container(tables, sequence_type=batch_grid)"]
    TablesTab --> DiagramsTablesTab["Container([diagrams_grid, tables_tab], sequence_type=tabs)"]
    DiagramsTablesTab --> AppendItems
    HasTables -- No --> AppendItems
    IsList -- No --> BuildSingleDiagram["Image(plot.correlation_matrix(...))"]
    BuildSingleDiagram --> SingleHasTable{config.correlation_table?}
    SingleHasTable -- Yes --> BuildSingleTable["CorrelationTable(...)"] --> DiagramTableTabs["Container([diagram,table], sequence_type=tabs)"] --> AppendItems
    SingleHasTable -- No --> AppendItems
    AppendItems --> ForEachKey
    ForEachKey --> CreateContainer["Container(items, sequence_type=tabs, name='Correlations')"]
    CreateContainer --> AnyItems{len(items)>0?}
    AnyItems -- Yes --> ReturnContainer
    AnyItems -- No --> ReturnNone
    ReturnContainer --> End
    ReturnNone --> End

## Examples (usage pattern and considerations):
- Typical pipeline usage (described in steps, not code):
    1. A report assembly routine has collected profiling results in a BaseDescription-like object `summary` that contains `summary.correlations`, mapping names like "pearson" to DataFrame(s).
    2. The assembly routine calls get_correlation_items(config, summary).
    3. If the profiling step discovered correlation matrices:
        - The function returns a Container (tabs) that the caller inserts into the report tree.
        - If config.correlation_table is True the returned structure contains both heatmap Images and CorrelationTable items arranged under tabs; otherwise it contains only heatmap Image(s) arranged in a grid or single image(s).
    4. If no correlation matrices were present, the function returns None and the caller should omit the "Correlations" section.

- Error-awareness guidance:
    - If you see a KeyError propagated from this function, check summary.correlations keys — they must be one of the expected keys ("pearson","spearman","kendall","phi_k","cramers","auto").
    - If plotting fails (exceptions from plot.correlation_matrix), inspect the corresponding correlation matrix DataFrame for NaNs, invalid dtypes, or malformed shapes.
    - If Image.__init__ raises ValueError, it indicates the image payload returned by plot.correlation_matrix was None; investigate plotting configuration or the plot helper return contract.

