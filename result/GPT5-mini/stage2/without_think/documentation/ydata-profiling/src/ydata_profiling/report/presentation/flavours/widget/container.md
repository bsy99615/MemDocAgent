# `container.py`

## `src.ydata_profiling.report.presentation.flavours.widget.container.get_name` · *function*

## Summary:
Return a stable textual identifier for a Renderable item: prefer an explicit human-readable name when available; otherwise fall back to the item's anchor_id.

## Description:
This small utility is used by presentation code that needs a canonical label or identifier for a Renderable object (for example, when constructing widget titles, section headers, navigation anchors, or keys in layout maps). It encapsulates the simple selection logic so callers do not need to repeatedly check both metadata fields.

Known callers within the codebase:
- No direct callers were found in the inspected source snapshot. Typical callers include:
  - Container implementations and widget-based presentation builders that need to derive a display name or stable anchor for items before rendering.
  - Report composition utilities that produce titles, table-of-contents entries, or widget labels.

Why this logic is extracted:
- Responsibility boundary: centralizes the fallback rule (use name if present, else anchor_id) so higher-level layout code can assume a single canonical identifier without inlining attribute presence checks. It keeps metadata-selection semantics consistent across presentations and avoids duplicating hasattr/attribute-access patterns.

## Args:
    item (Renderable): A Renderable instance (or any object implementing equivalent attributes) from which to obtain an identifier.
        - Expected attributes:
            - name (optional): preferred textual label. On Renderable, this is a property exposing content["name"] and will raise KeyError if the key is absent.
            - anchor_id (used as fallback): fallback identifier, typically content["anchor_id"] on Renderable and may raise KeyError if absent.
        - The function accepts any object; it does not enforce type at runtime beyond accessing the named attributes.

## Returns:
    str: The identifier string chosen for the item.
        - If the item has an accessible name attribute, its value is returned.
        - Otherwise, the function returns the value of item.anchor_id.
        - Possible edge-case return values include any value stored under those attributes (not strictly validated to be str by this function); callers may wish to cast to str if needed.

## Raises:
    KeyError:
        - If accessing item.name raises KeyError (for example, Renderable.name property raises KeyError when the underlying content mapping lacks "name"), that exception will propagate because hasattr internally calls getattr and does not catch non-AttributeError exceptions.
        - If the code reaches the fallback branch and item.anchor_id access raises KeyError (e.g., missing "anchor_id" in the Renderable.content), that KeyError will propagate.
    AttributeError:
        - If item lacks both attributes entirely and attribute access raises AttributeError, that exception will propagate when attempting to read item.anchor_id.
    Any other exceptions raised by attribute access (e.g., TypeError from a misbehaving property) will propagate.

## Constraints:
Preconditions:
    - The caller should pass an object with at least one of the attributes name or anchor_id accessible without raising unexpected exceptions.
    - For Renderable instances: prefer constructing them with either name or anchor_id present in their content dict; otherwise callers must handle potential KeyError.

Postconditions:
    - If the function returns normally, the returned value is the item.name if that attribute was accessible when checked by hasattr(), otherwise item.anchor_id.
    - No mutation is performed on the item.

## Side Effects:
    - None. The function performs attribute reads only and does not perform I/O, mutate global state, or call external services.
    - Note: attribute access may trigger custom property code in the item that has side effects; those are external to this function.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckName{hasattr(item, "name")?}
    CheckName -->|True| ReturnName[return item.name]
    CheckName -->|False| ReturnAnchor[return item.anchor_id]
    ReturnName --> End([End])
    ReturnAnchor --> End

## Examples:
1) Typical use when item has a name:
    - Given a Renderable with content["name"] = "Overview":
      - get_name(item) -> "Overview"

2) Fallback use when name is absent but anchor_id present:
    - Given a Renderable with content["anchor_id"] = "sec-1" and no "name":
      - get_name(item) -> "sec-1"

3) Handling missing metadata (error handling example):
    - If a caller cannot guarantee the presence of either key, guard the call:
      - try:
          identifier = get_name(item)
        except KeyError:
          identifier = "<unknown>"

Notes and implementation caveat:
- For Renderable, the name/anchor_id attributes are implemented as properties that read the underlying content mapping and raise KeyError if the keys are absent. Because hasattr only suppresses AttributeError, calling hasattr(item, "name") may itself raise KeyError if the property access raises KeyError. Therefore callers who expect missing metadata to be a normal condition may prefer to inspect item.content directly (e.g., item.content.get("name") or item.content.get("anchor_id")) to avoid propagating KeyError from property access.

## `src.ydata_profiling.report.presentation.flavours.widget.container.get_tabs` · *function*

## Summary:
Create an ipywidgets.Tab whose children are the rendered outputs of the provided renderable items and whose tab titles are derived from each item's canonical identifier.

## Description:
This helper composes a Tab widget for widget-based presentations. For each Renderable in items it:
- calls render() to obtain the widget-like child to display in a tab pane,
- uses get_name(item) to choose a stable title (prefer name, fall back to anchor_id).

Known callers within the codebase and typical calling context:
- No direct callers were found in the inspected snapshot. Typical callers include:
  - widget-based presentation builders that convert a list of section renderables into a tabbed UI,
  - container implementations responsible for arranging multiple Renderable elements as tabs for interactive reports.
- Typical pipeline stage: invoked during final presentation composition when a list of Renderable sections (already created and populated with content/metadata) must be presented as an interactive tabbed control in an IPython/Jupyter frontend.

Why this logic is extracted:
- Responsibility boundary: centralizes the details of turning Renderable objects into an ipywidgets.Tab (rendering children + deriving titles) so callers do not need to repeat the two-step pattern (call render, choose name, construct Tab, set titles).
- Reuse & clarity: keeps widget composition code concise and ensures consistent title derivation across different places that present Renderable lists as tabs.

## Args:
    items (List[Renderable])
        - A sequence (list-like) of Renderable instances (or objects implementing the same interface).
        - Each element is expected to implement:
            - render() -> a widget-like object acceptable to ipywidgets.Tab.children (typically an ipywidgets.Widget),
            - name and/or anchor_id metadata accessible by get_name().
        - Interdependencies:
            - The function relies on get_name(item) to return a usable title; if get_name raises (KeyError, AttributeError), the exception propagates.
            - The object returned by item.render() must be compatible with ipywidgets Tab children; otherwise ipywidgets may raise when assigning children.

## Returns:
    widgets.Tab
        - An ipywidgets.Tab instance whose .children attribute is the list of rendered outputs (in the same order as items) and whose tab labels are set to the values returned by get_name(item).
        - Edge cases:
            - If items is empty, returns an empty Tab with no children.
            - Titles are set for indices 0..n-1 where n == len(items); all titles correspond to items in the same order.

## Raises:
    - Propagated exceptions from get_name(item):
        - KeyError: when get_name attempts to access metadata (e.g., Renderable.name or anchor_id) and the underlying property raises KeyError (this can happen for Renderable if the content mapping lacks those keys).
        - AttributeError: if the item lacks both name and anchor_id attributes and attribute access fails.
    - Exceptions from item.render():
        - Any exception raised by a concrete render() implementation will propagate (e.g., TypeError, ValueError, runtime errors raised by rendering logic).
    - Exceptions from ipywidgets when assigning children or setting titles:
        - TypeError/ValueError: may be raised by the ipywidgets library if the provided children are not acceptable widget objects or if set_title is used incorrectly. These will propagate.

## Constraints:
Preconditions:
    - items must be an iterable of objects that expose render() and metadata (name/anchor_id) as described above.
    - For safe usage with Renderable instances, ensure each Renderable has either "name" or "anchor_id" present in its content mapping before calling this function (to avoid KeyError).
    - The consumer environment should have ipywidgets available and a frontend that can render widgets (e.g., Jupyter Notebook/Lab) for the result to be interactive.

Postconditions:
    - The returned Tab contains as children the sequence [item.render() for item in items] (same order).
    - Each child at index i has its tab label set to get_name(items[i]).
    - No mutation is performed on the provided items themselves by this function (only the Tab object is constructed).

## Side Effects:
    - Constructs an ipywidgets.Tab object and assigns its .children and titles. No file or network I/O is performed.
    - No global state or external mutable state in the repository is mutated.
    - Note: calling item.render() may have side effects if the concrete Renderable implementation performs them (e.g., lazy computation or caching); such side effects are implementation-dependent and not caused by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> PrepareLists[Initialize children = [], titles = []]
    PrepareLists --> ForEach{for each item in items}
    ForEach --> CallRender[item.render() -> child]
    CallRender --> AppendChild[children.append(child)]
    AppendChild --> CallGetName[get_name(item) -> title]
    CallGetName --> AppendTitle[titles.append(title)]
    AppendTitle --> NextItem{more items?}
    NextItem -->|Yes| ForEach
    NextItem -->|No| CreateTab[tab = widgets.Tab()]
    CreateTab --> SetChildren[tab.children = children]
    SetChildren --> SetTitlesLoop[for id, title in enumerate(titles)]
    SetTitlesLoop --> SetTitleCall[tab.set_title(id, title)]
    SetTitleCall --> TitleLoopMore{more titles?}
    TitleLoopMore -->|Yes| SetTitlesLoop
    TitleLoopMore -->|No| ReturnTab[return tab]
    ReturnTab --> End([End])

## Examples:
1) Basic happy path (items have names or anchor_ids and render returns widgets):
    - Given a list of Renderable instances, each with a render() that returns an ipywidgets.Widget and metadata providing a name (or anchor_id),
      calling get_tabs(items) returns a Tab whose panes show each rendered widget and whose tab labels are the items' names.

2) Empty items list:
    - If items == [], the function returns a Tab with no children; no exception is raised.

3) Handling missing metadata (defensive usage):
    - If callers cannot guarantee that each Renderable has either name or anchor_id, guard against KeyError:
        - try:
            tab = get_tabs(items)
          except KeyError:
            # fallback behavior: create safe titles from item.content or use placeholders
            safe_titles = [it.content.get("name") or it.content.get("anchor_id") or "<unknown>" for it in items]
            # build Tab manually or pre-populate items with fallback metadata

4) Handling render errors:
    - Since item.render() may raise, callers that need robustness should catch exceptions around the call that constructs tabs (or validate items/renderability before calling get_tabs).

## `src.ydata_profiling.report.presentation.flavours.widget.container.get_list` · *function*

## Summary:
Create an ipywidgets vertical container by rendering a sequence of Renderable objects and returning a widgets.VBox whose children are the rendered results.

## Description:
A minimal helper in the widget presentation flavour that transforms a sequence of Renderable instances into a single vertical ipywidgets container.

Intended usage context:
- Used by widget-based presentation code that has already assembled Renderable items (e.g., sections, small components) and needs to compose them into a vertical layout for display in Jupyter-like frontends.
- The function is purposefully small to encapsulate the iteration-and-assemble pattern so higher-level layout code does not duplicate this logic.

Why this logic is extracted:
- Single responsibility: isolates the conversion from Renderable -> widget children and the construction of widgets.VBox.
- Reuse: centralizes this composition step for the widget flavour so changes to how children are collected or a different container type can be made in one place.

## Args:
    items (List[Renderable]):
        - Annotated type: List[Renderable]. At runtime the function only requires that 'items' is iterable; any iterable of Renderable-like objects (objects with a callable render() method) will work.
        - Each element must implement render() which returns an object acceptable as an ipywidgets child (commonly an ipywidgets.Widget).
        - Allowed values:
            - An empty sequence: valid; produces an empty VBox.
            - A sequence containing Renderable instances: valid.
        - Disallowed / will fail at runtime:
            - items is None (TypeError when attempting iteration).
            - elements that are None or lack render(): AttributeError when attempting to call render().

## Returns:
    widgets.VBox
    - A newly constructed ipywidgets.VBox whose children are the outputs of calling item.render() for each item in items, preserving order.
    - If items is empty, the returned VBox has zero children.
    - The function returns the VBox object directly; it does not automatically display it.

## Raises:
    The function does not raise new exceptions itself but lets underlying exceptions propagate:
    - TypeError: if items is not iterable (e.g., None).
    - AttributeError: if an element does not implement render().
    - Any exception raised by item.render() will propagate unchanged.
    - ipywidgets/traitlets errors (e.g., traitlets.TraitError) can occur if a render() result is not valid as a VBox child.

## Constraints:
Preconditions:
    - items should be an iterable of objects that implement a callable render() method.
    - Each render() call should return a value acceptable to ipywidgets.VBox children.

Postconditions:
    - Returns a widgets.VBox whose children list matches the sequence of render() outputs.
    - Does not mutate the input iterable or the Renderable objects (only calls their render() methods).

## Side Effects:
    - Allocates ipywidgets.Widget objects (the VBox and whatever widgets are returned by render()). In notebook environments these objects register with the frontend and consume frontend resources.
    - No file, network, or global state is modified by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckIterable{items iterable?}
    CheckIterable -->|no| PropagateTypeError[TypeError propagated on iteration]
    CheckIterable -->|yes| Iterate[For each item in items: call item.render()]
    Iterate -->|render() raises| PropagateRenderError[Underlying exception propagated]
    Iterate -->|all OK| Collect[Collect render results into list]
    Collect --> ConstructVBox[Create widgets.VBox(children=list_of_results)]
    ConstructVBox -->|construction raises| PropagateWidgetError[ipywidgets/traitlets error propagated]
    ConstructVBox --> ReturnVBox([Return VBox])

## Examples:
- Basic:
    items = [r1, r2, r3]  # each rN implements Renderable.render() -> ipywidgets.Widget
    vbox = get_list(items)
    # vbox.children is a tuple of the three rendered widgets
    # display(vbox)  # to show in a notebook

- Defensive wrapper:
    def safe_get_list(items):
        rendered = []
        for i, item in enumerate(items):
            try:
                rendered.append(item.render())
            except Exception as e:
                logger.exception("Failed to render item %d: %s", i, e)
        return widgets.VBox(rendered)

## `src.ydata_profiling.report.presentation.flavours.widget.container.get_named_list` · *function*

## Summary:
Constructs an ipywidgets vertical layout that pairs each Renderable item with a bolded label (its canonical name) and the item's rendered presentation, returning a top-level VBox containing one VBox per item.

## Description:
get_named_list is a small presentation helper used when building widget-based UIs for reports. For each Renderable in the provided sequence it:
- derives a label using the shared get_name(item) utility (prefer name, then anchor_id),
- creates an ipywidgets.HTML node containing the label wrapped in a strong tag,
- obtains the presentation output by calling item.render(),
- groups the label and rendered output into an inner ipywidgets.VBox,
- collects all inner VBoxes into an outer ipywidgets.VBox and returns it.

Known callers and typical context:
- No direct callers were discovered in the inspected snapshot. Typical callers include widget-based presentation builders, report composition utilities, or any code that needs to present a sequence of Renderable items as titled widgets (for example, when rendering Container.content['items'] for a widget flavour).
- Typical pipeline stage: after a list of Renderable objects has been constructed (possibly converted to widget-flavour renderables), get_named_list is called to produce a widget that can be displayed in an IPython/Jupyter frontend.

Why this logic is extracted:
- Responsibility boundary: centralizes the pairing of a canonical label with an item's rendered representation so that higher-level layout code does not need to duplicate label-selection (get_name) or widget-grouping logic.
- Reuse and clarity: keeps presentation assembly consistent across places that need a labeled list of Renderables and isolates HTML label formatting in one location.

## Args:
    items (List[Renderable]):
        - A sequence (list) of objects implementing the Renderable protocol (i.e., providing a render() method and typically exposing metadata such as name and anchor_id).
        - Each element is expected to:
            * support get_name(item) (i.e., have a name or anchor_id accessible), and
            * implement render() to produce an object accepted as a child by ipywidgets (commonly another widget).
        - No default value. The function does not validate element types at runtime; it only iterates and uses attribute access/calls.

## Returns:
    ipywidgets.widgets.VBox:
        - A top-level VBox whose children are one inner VBox per item in items.
        - Each inner VBox contains exactly two children in order:
            1. an ipywidgets.HTML widget with text "<strong>{label}</strong>" where label is the result of get_name(item),
            2. the object returned by item.render() (typically a widget or widget-compatible object).
        - Length guarantee: if the input sequence has N items, the returned outer VBox will contain N inner VBoxes in the same order.
        - Edge-case return values:
            * If items is empty, the function returns an empty VBox (outer VBox with no children).
            * If item.render() returns None or a type not accepted by ipywidgets, the outer VBox construction may fail (see Raises).

## Raises:
    KeyError:
        - Propagates if get_name(item) accesses a Renderable property that raises KeyError (e.g., Renderable.name or Renderable.anchor_id when their backing content keys are absent). This arises because get_name uses attribute access that may raise KeyError for Renderable.
    AttributeError:
        - Propagates if an item does not expose expected attributes and attribute access fails (for example, if item lacks render or name/anchor_id and that absence leads to an AttributeError during get_name or the call to item.render()).
    Any exception raised by item.render():
        - item.render() is called for each item; any exception it raises (ValueError, TypeError, etc.) will propagate out of get_named_list.
    TypeError / ipywidgets-specific errors:
        - ipywidgets.widgets.VBox may raise TypeError or a widget-construction error if any child is not a valid ipywidgets child (for example, None or an incompatible type). Such exceptions are raised by ipywidgets and will propagate.

## Constraints:
Preconditions:
    - The caller must provide an iterable/list-like object for items. The function expects to iterate in Python order.
    - Each item should implement the Renderable protocol: attribute access for label selection (name or anchor_id via get_name) and a callable render() method that returns a widget-like object. If these are not true, the call may raise exceptions described above.
Postconditions:
    - On normal completion, an ipywidgets.VBox is returned whose children represent the labeled items in the same order as the input sequence.
    - The function performs no mutation of the items list or the Renderable instances (it only reads metadata and calls render()).

## Side Effects:
    - No direct I/O (no file, network, or stdout IO) is performed by get_named_list itself.
    - Indirect side effects may occur:
        * Accessing item.name or item.anchor_id may run property code that mutates external state (this is external to get_named_list).
        * item.render() may perform side effects (allocating widgets, accessing data, raising exceptions).
    - No global state, caches, or persistent storage are modified by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> Iterate{for each item in items}
    Iterate --> GetName[get_name(item)]
    GetName --> CreateHTML[widgets.HTML("<strong>{label}</strong>")]
    CreateHTML --> CallRender[item.render()]
    CallRender --> InnerVBox[widgets.VBox([HTML, render_output])]
    InnerVBox --> Collect[append inner VBox to list]
    Collect --> Iterate
    Iterate -->|all items processed| OuterVBox[widgets.VBox(list_of_inner_VBoxes)]
    OuterVBox --> Return([Return outer VBox])
    Return --> End([End])

## Examples:
1) Typical (happy-path) usage:
    - Given a list of Renderable widget objects (each render() returns a widget and each has either name or anchor_id), calling get_named_list(items) produces a VBox whose children are titled sections for each item that can be displayed in a Jupyter notebook cell.

2) Empty list:
    - If items == [], the function returns an empty ipywidgets.VBox (no children).

3) Calling code that must tolerate missing metadata:
    - If callers cannot guarantee that items provide name or anchor_id via Renderable properties, protect the call:
        - Suggestion: precompute safe labels using item.content.get("name") or item.content.get("anchor_id") before passing items to get_named_list, or catch KeyError around get_named_list and supply fallback UI.

Notes:
    - Because get_named_list relies on get_name(item) and item.render(), callers should ensure those operations are well-behaved (do not raise unwanted exceptions) before calling this helper in batch rendering paths.
    - The function intentionally keeps UI assembly minimal: label formatting is a simple HTML strong tag and no additional styling or classes are added here; callers that need custom styling should post-process the returned VBox or use a different builder.

## `src.ydata_profiling.report.presentation.flavours.widget.container.get_row` · *function*

## Summary:
Create an ipywidgets.GridBox row from a list of Renderable items, choosing a fixed column layout based on the number of items and placing each item's rendered widget as a child.

## Description:
This function composes a horizontal row for the widget-based presentation flavour by:
- Determining a grid column layout depending on the number of supplied Renderable items (1 through 4).
- Calling render() on each Renderable to obtain the child widget(s) to be placed inside the GridBox.
- Returning a configured widgets.GridBox ready for insertion into a larger widget UI.

Known callers within the provided code snapshot:
- No direct callers were identified in the supplied source fragments. The function is intended for use by widget-flavour report builders or presentation code that assemble rows of Renderable elements into a widget-based UI.

Typical trigger/context:
- Used during presentation composition where several Renderable elements (cards, small panels, charts, controls) should be placed in a single horizontal row with a predetermined set of column widths.

Reason for extraction:
- Encapsulates the mapping from number-of-items to column layout so callers do not repeat layout strings and so the widget presentation remains consistent across the report.

## Args:
    items (List[Renderable]):
        - A list of objects implementing the Renderable protocol (i.e., providing a render() method and content metadata).
        - Expected length: 1, 2, 3, or 4. Length 0 or >4 is not supported and will raise ValueError.
        - Interdependency: the function calls item.render() for each element and therefore expects each render() call to produce a widget instance compatible with ipywidgets children (typically an instance of widgets.Widget). The function does not coerce or validate the returned objects.

## Returns:
    widgets.GridBox
        - A GridBox whose .children are the sequence of objects returned by item.render() (in the same order as items).
        - The GridBox.layout.width is set to "100%".
        - The GridBox.layout.grid_template_columns is chosen as:
            * 1 item: "100%"
            * 2 items: "50% 50%"
            * 3 items: "25% 25% 50%"
            * 4 items: "25% 25% 25% 25%"
        - Edge / special cases:
            * The function does not return None. It either returns a configured GridBox or raises an exception for unsupported input lengths.
            * If any item.render() returns an object incompatible with ipywidgets children, the returned GridBox may fail to display correctly or ipywidgets may raise an error at widget construction/render time.

## Raises:
    ValueError:
        - Raised when len(items) is not one of 1, 2, 3, or 4. The exact message in code is "Layout undefined for this number of columns".
    Propagated exceptions (not explicitly raised here but possible):
        - Any exception raised by item.render() (TypeError, AttributeError, etc.) will propagate out of get_row.
        - ipywidgets-related errors triggered while creating GridBox.children (or interacting with the front-end) will propagate.

## Constraints:
    Preconditions:
        - items must be a sequence (List-like) of Renderable instances.
        - The caller should ensure 1 <= len(items) <= 4. Passing 0 or >4 is invalid.
        - Each item's render() should produce an ipywidgets.Widget-compatible object for proper display in the GridBox.
    Postconditions:
        - The returned GridBox has layout.width == "100%" and layout.grid_template_columns equal to the mapping listed above.
        - The GridBox.children iterate the rendered outputs in the original items order.
        - No mutation of the supplied Renderable instances or their content is performed by this function.

## Side Effects:
    - No I/O, network calls, global state mutation, or external service interactions are performed.
    - The function calls each item's render() method; side effects of those render() implementations (if any) may occur (e.g., caching, lazy computation inside render()).
    - The function constructs ipywidgets objects in memory; their lifecycle and display depend on the caller inserting them into a Jupyter front-end.

## Control Flow:
flowchart TD
    Start --> CheckLen["Compute n = len(items)"]
    CheckLen -->|n == 1| Layout1["layout = width:100% / grid_template_columns: '100%'"]
    CheckLen -->|n == 2| Layout2["layout = width:100% / grid_template_columns: '50% 50%'"]
    CheckLen -->|n == 3| Layout3["layout = width:100% / grid_template_columns: '25% 25% 50%'"]
    CheckLen -->|n == 4| Layout4["layout = width:100% / grid_template_columns: '25% 25% 25% 25%'"]
    CheckLen -->|otherwise| Raise["Raise ValueError('Layout undefined for this number of columns')"]
    Layout1 --> RenderChildren["children = [item.render() for item in items]"]
    Layout2 --> RenderChildren
    Layout3 --> RenderChildren
    Layout4 --> RenderChildren
    RenderChildren --> CreateGridBox["Create widgets.GridBox(children, layout=layout)"]
    CreateGridBox --> Return["Return GridBox"]
    Raise --> End

## Examples (usage guidance; described in narrative steps rather than raw code):
Example 1 — Typical usage with three small card-like renderables:
1. Ensure you have three Renderable instances whose render() returns widget-compatible objects (for example, widgets.HTML, widgets.Output, or other widgets.Widget instances).
2. Call get_row with the list of these three renderables.
3. The function returns a GridBox with width "100%" and columns "25% 25% 50%"; place that GridBox inside a parent container (e.g., a VBox) so it appears in the UI.

Example 2 — Error handling (caller responsibility):
1. Validate the number of items before calling if your code may produce variable-length lists. If the list length might be 0 or greater than 4, either adjust the list or catch ValueError from get_row and handle it (e.g., fall back to a stacked layout or split across multiple rows).
2. If item.render() could raise, callers that prefer resilient assembly should call render() on each item individually within try/except to isolate failing items before calling get_row.

Example 3 — Defensive validation (recommended when inputs are dynamic):
- If items come from untrusted or heterogeneous sources, consider asserting each item implements render() and optionally that item.render() returns an instance of ipywidgets.Widget before invoking get_row. This avoids widget-construction-time errors and makes failure modes explicit.

## `src.ydata_profiling.report.presentation.flavours.widget.container.get_batch_grid` · *function*

## Summary:
Create an ipywidgets GridBox that arranges a list of Renderable objects into a fixed-width grid with a specified number of columns (batch_size), optionally showing each item's title or subtitle above its rendered widget.

## Description:
This function constructs a grid layout for displaying multiple Renderable widgets in an IPython/Jupyter notebook environment. It computes a column template based on the requested batch_size and converts each Renderable into either:
- a plain rendered widget (item.render()), or
- a vertical box (VBox) containing an HTML title/subtitle followed by the rendered widget.

Known callers (from the provided context):
- No direct callers are available in the preloaded source context for this repository. Typically this function is invoked by higher-level presentation or container code that needs to render a collection of report widgets (for example, a container that lays out several summary widgets in rows/columns for a profiling report).

Why this logic is extracted:
- Responsibility boundary: centralizes the layout and presentation policy for batching Renderable items into a uniform grid (column sizing and title/subtitle handling). This avoids duplicating grid-layout code across multiple places that render lists of widgets and keeps presentation concerns separate from data/model logic.

## Args:
    items (List[Renderable]):
        A list of objects implementing the Renderable interface (expected to have a .name attribute and a .render() method that returns an ipywidget). Each item will be converted into a GridBox child according to the titles/subtitles flags.
    batch_size (int):
        The number of columns in the grid. Must be >= 1. The function computes each column width as int(100 / batch_size) percent (so widths are integer percentages and may be rounded down). If batch_size is 0 a ZeroDivisionError will be raised. If batch_size is larger than 100, column width will become 0% due to integer division — this may produce unusable layouts.
    titles (bool):
        If True (and subtitles is False), each item will be wrapped in a VBox whose first child is an HTML element containing the item's name rendered as a level-4 heading (<h4>).
    subtitles (bool):
        If True, each item will be wrapped in a VBox whose first child is an HTML element containing the item's name rendered as an emphasized level-5 heading (<h5><em>...</em></h5>). If both subtitles and titles are True, subtitles takes precedence (the code checks subtitles first).

Interdependencies:
    - titles and subtitles are mutually influential: subtitles wins when both are True.
    - batch_size controls only the CSS column width calculation; it does not affect how many items are placed per row beyond controlling column sizing.

## Returns:
    widgets.GridBox
        An ipywidgets.GridBox instance whose children are the rendered items (either raw item.render() results or widgets.VBox wrappers containing a heading HTML and the rendered widget), and whose layout is set using Layout(width="100%", grid_template_columns=...).
        - If items is empty, returns an empty GridBox with the computed layout.
        - The children list preserves the same order as the input items list.

## Raises:
    ZeroDivisionError:
        If batch_size == 0 due to the division int(100 / batch_size) used to compute column widths.
    AttributeError:
        If any item in items does not expose .name or .render(), the attempt to access item.name or call item.render() will raise an AttributeError (propagated from the attempted attribute access or call).
    Any exception raised by item.render():
        The function does not catch exceptions from item.render(); such exceptions propagate to the caller.

## Constraints:
Preconditions:
    - items must be an iterable (list) of Renderable-like objects that provide:
        * a .name attribute (string-like) used for the HTML title/subtitle when titles/subtitles is True.
        * a .render() method that returns a widget-like object compatible with ipywidgets children.
    - batch_size must be an integer >= 1 for meaningful layouts.
    - The caller should be running in an environment where ipywidgets can be displayed (e.g., Jupyter notebook/lab) to observe the widget output.

Postconditions:
    - Returns a GridBox whose layout.grid_template_columns is a space-separated string of batch_size entries each equal to f"{int(100 / batch_size)}%".
    - The returned GridBox.children list contains exactly len(items) elements in the same order as provided.

## Side Effects:
    - No file, network, or stdout I/O is performed.
    - No global state is mutated by this function.
    - It creates ipywidgets objects (HTML, VBox, GridBox) which are Python objects and may allocate memory; displaying them in a notebook triggers UI rendering but that is external to the function.
    - The function calls item.render() which may have side effects depending on the Renderable implementation; such side effects are not managed by get_batch_grid and will be propagated.

## Control Flow:
flowchart TD
    A[Start: compute layout] --> B{batch_size == 0?}
    B -- Yes --> E[Raise ZeroDivisionError during int(100 / batch_size)]
    B -- No --> C[Initialize empty out list]
    C --> D[For each item in items]
    D --> F{subtitles True?}
    F -- Yes --> G[Append VBox([HTML(h5 em name), item.render()])]
    F -- No --> H[titles True?]
    H -- Yes --> I[Append VBox([HTML(h4 name), item.render()])]
    H -- No --> J[Append item.render()]
    G --> K[Next item]
    I --> K
    J --> K
    K --> L{More items?}
    L -- Yes --> D
    L -- No --> M[Return GridBox(children=out, layout=layout)]
    E --> END[Exception propagates]

## Examples (usage described in prose):
1. Typical happy-path usage:
   - Prepare a list of Renderable objects where each implements .name (a short string) and .render() (returns an ipywidget such as an Output, HTML, or custom widget).
   - Call get_batch_grid(items, batch_size=3, titles=True, subtitles=False).
   - The function returns a GridBox with three equally sized columns (each column width computed as int(100/3)% -> "33% 33% 33%"). Each item will be displayed with its name as an <h4> heading above its widget.

2. Handling empty lists:
   - Calling get_batch_grid([], batch_size=4, titles=False, subtitles=False) returns an empty GridBox with the layout set for four columns; displaying it shows an empty area.

3. Error scenario:
   - If batch_size is passed as 0, a ZeroDivisionError will be raised while computing column widths; callers should validate batch_size before calling or catch the exception.
   - If any Renderable's render method raises, that exception propagates; callers should isolate or wrap render() implementations if needed.

Notes:
    - Because column widths use integer division, for some batch_size values the sum of computed column percentages may be less than 100% (e.g., batch_size=6 -> int(100/6)=16% per column -> total 96%). This is an artifact of integer truncation in the current implementation.
    - If more precise column sizing is required, callers should adjust batch_size or request a change in the implementation to use floating-point formatting (e.g., f"{100 / batch_size}%") instead of int().

## `src.ydata_profiling.report.presentation.flavours.widget.container.get_accordion` · *function*

## Summary:
Create an ipywidgets.Accordion whose panes are the rendered outputs of the given Renderable items and whose pane titles are the canonical identifiers (name or anchor_id) derived from each item.

## Description:
This function is used by widget-based presentation code to convert a sequence of Renderable objects into a single Accordion widget where each child pane contains one rendered item and the pane label is a stable identifier for that item.

Known callers and typical context:
- Presentation builders and layout renderers that convert Container-like structures or lists of Renderable items into ipywidgets-based UI components. For example, a Container-to-widget renderer that handles sequence_type "accordion" will collect child Renderable items and call this function to produce the UI component to embed in a Jupyter notebook or widget-based report.
- Any code that wants a compact grouped widget representation of several Renderable outputs with human-readable pane titles.

Why this is extracted:
- Responsibility separation: centralizes the mapping from Renderable -> (rendered widget, title) tuples and the construction of an Accordion so callers do not reimplement the same loop, title-fallback logic, and set_title bookkeeping. It encapsulates the widget-specific details (ipywidgets.Accordion usage and title assignment), keeping container/rendering code focused on layout decisions and data traversal.

## Args:
    items (List[Renderable]): Ordered sequence of objects implementing the Renderable contract.
        - Required behaviors of each item:
            - render() -> Any: should return an object acceptable as a child of ipywidgets.Accordion (typically an ipywidgets.Widget).
            - name or anchor_id: get_name(item) will be called to obtain a pane title; at least one of these should be accessible to avoid exceptions.
        - Interdependencies:
            - The title list and children list are built in the same iteration order; the i-th title corresponds to the i-th child produced by render().

## Returns:
    widgets.Accordion:
        - An instance of ipywidgets.Accordion constructed with children equal to [item.render() for item in items].
        - Each pane's title is set to the string/value returned by get_name(item) (set via accordion.set_title(index, title) for each index).
        - For an empty items list, an Accordion is still constructed with no children; callers should verify runtime behavior in their widget environment if necessary.

## Raises:
    - Any exception raised by item.render(): exceptions from the Renderable subclass's render implementation will propagate (e.g., ValueError, TypeError, custom exceptions).
    - Any exception raised by get_name(item): get_name may raise KeyError or AttributeError when item lacks name/anchor_id in a way that the get_name utility does not handle; those will propagate.
    - Exceptions from ipywidgets constructor or accordion.set_title: if ipywidgets rejects the provided children objects or titles, those exceptions (TypeError, TraitError from ipywidgets, etc.) will propagate.
    - The function does not catch or translate exceptions; callers should handle them if missing metadata or rendering failures are expected.

## Constraints:
Preconditions:
    - Caller passes an iterable of objects that conform to the minimal Renderable contract:
        - Implement render() that returns a widget-like object acceptable to ipywidgets.Accordion.
        - Expose metadata accessible to get_name (name or anchor_id) or callers must be prepared to handle exceptions from get_name.
    - The environment must have ipywidgets available; widgets.Accordion is imported from ipywidgets in the module.

Postconditions:
    - On normal return, the returned Accordion contains as many children as items passed in; pane i contains the output of items[i].render() and has title get_name(items[i]).
    - No mutation of the provided items list is performed by this function; side effects are limited to creating widget objects and possibly any side effects triggered by item.render().

## Side Effects:
    - The function constructs ipywidgets objects (in-memory widget instances). Creating widgets may register state in the notebook front-end when displayed later, but this function itself only returns the constructed widget.
    - item.render() may have arbitrary side effects defined by the Renderable implementation (mutating internal state, logging, raising exceptions). Those are external to this function.
    - No file, network I/O, global variable mutation, or database writes are performed by this function itself.

## Control Flow:
flowchart TD
    Start([Start]) --> InitLists{Create empty children & titles lists}
    InitLists --> ForEach[For each item in items]
    ForEach --> CallRender[item.render() -> child]
    CallRender --> AppendChild[append child to children]
    AppendChild --> CallGetName[get_name(item) -> title]
    CallGetName --> AppendTitle[append title to titles]
    AppendTitle --> LoopBack{More items?}
    LoopBack -->|Yes| ForEach
    LoopBack -->|No| MakeAccordion[accordion = widgets.Accordion(children=children)]
    MakeAccordion --> SetTitles[for id,title in enumerate(titles): accordion.set_title(id,title)]
    SetTitles --> ReturnAccordion[return accordion]
    ReturnAccordion --> End([End])

## Examples:
1) Typical usage in a notebook (happy path):
    - Prepare a list of Renderable items where each render() returns an ipywidgets.Widget and name or anchor_id is present.
    - Call the function to obtain an Accordion widget and display it in the notebook UI.

2) Defensive usage when metadata may be missing:
    - If callers cannot guarantee that each item has a name or anchor_id (get_name may raise KeyError), guard the call:
        - Iterate items and pre-validate names via item.content.get("name") or item.content.get("anchor_id") (avoids property KeyError), or
        - Wrap get_accordion(items) in try/except to handle propagated KeyError and fall back to a safe title list.

3) Handling render-time failures:
    - Because item.render() can raise, callers that build Accordion from heterogeneous items may prefer to render each item in a try/except and either:
        - replace failed child with a placeholder widget describing the error, or
        - omit the failing item from the children list and adjust titles accordingly before constructing the Accordion.

Notes:
    - The function assumes get_name is available in the same module scope and follows its documented semantics (preferred name property; fallback to anchor_id). Because get_name can raise KeyError if metadata is absent, callers should either ensure items have metadata or handle exceptions.
    - The function does not coerce titles to str; if a title value is not a string, ipywidgets will accept or reject it depending on its expectations — callers may cast titles to str explicitly if necessary.

## `src.ydata_profiling.report.presentation.flavours.widget.container.WidgetContainer` · *class*

## Summary:
WidgetContainer is a Container subclass that renders a sequence of Renderable items into an ipywidgets.Widget according to the container's sequence_type (e.g., list, named_list, tabs, accordion, grid, batch_grid).

## Description:
WidgetContainer implements the Container.render() contract for the "widget" presentation flavour. When render() is called it dispatches to a small set of helper layout functions that convert the stored child Renderable objects (content['items']) into an ipywidgets.Widget appropriate for the requested sequence_type.

Typical instantiation scenario:
- A presentation factory or builder constructs a Container-like node with:
  - content['items']: an ordered sequence of Renderable instances,
  - content optionally including batch/grid metadata (see State),
  - sequence_type set to one of the recognised layout tokens ("list", "named_list", "tabs", "sections", "select", "accordion", "grid", "batch_grid").
- The factory then calls render() on the concrete WidgetContainer instance to obtain an ipywidgets widget to show in a Jupyter front-end.

Motivation / responsibility boundary:
- WidgetContainer centralizes the selection of widget layout semantics based on sequence_type and delegates the concrete widget assembly to the helper functions (get_list, get_named_list, get_tabs, get_accordion, get_row, get_batch_grid).
- It is intentionally thin: it does not implement layout logic itself, only the dispatching logic and contract that the result is an ipywidgets.Widget. All iteration/labeling/grid sizing logic belongs in the helper functions.

## State:
- Inherited and required state from Container/Renderable:
  - content: dict[str, Any]
    - 'items' (required for normal operation): sequence (e.g., list/tuple) of Renderable-like objects. Each element is expected to implement render() and (for some helpers) expose metadata such as name or anchor_id.
    - For batch_grid semantics:
      - 'batch_size' (required when sequence_type == "batch_grid"): int >= 1 indicating number of columns.
      - Optional flags used by get_batch_grid:
        - 'titles' (bool): defaults to True when absent; controls whether each item is displayed with an <h4> title.
        - 'subtitles' (bool): defaults to False when absent; if True, subtitles take precedence over titles and display <h5><em>...</em></h5>.
    - Other keys stored in content are ignored by WidgetContainer itself but may be used by child Renderable.render() implementations.
- sequence_type: str (inherited from Container initialization)
  - Valid runtime values handled by WidgetContainer: "list", "named_list", "tabs", "sections", "select", "accordion", "grid", "batch_grid".
  - Invariant: sequence_type remains a string during the object's lifetime.

Notes on invariants:
- content must be a dict and, for normal operation, must contain an iterable under the 'items' key.
- When sequence_type == "batch_grid", content must include a numeric 'batch_size' value; the implementation relies on it when calling get_batch_grid.

## Lifecycle:
Creation:
- Instantiate via the same pattern used for Container subclasses:
  - Provide items (sequence of Renderable) and a sequence_type string.
  - If sequence_type == "batch_grid", include content['batch_size'] (int) and optionally 'titles' and/or 'subtitles' booleans.
  - Example conceptual call (factory-style): create a WidgetContainer whose content dict contains keys 'items', 'nested' plus any kwargs; Container base sets sequence_type.

Usage / sequencing:
- After instantiation, call render() exactly when you need the widget representation.
- There is no required method-call ordering other than constructing the object before calling render().
- Typical usage sequence:
  1. Build or obtain Renderable children and metadata.
  2. Construct WidgetContainer (via a factory or constructor that populates content and sequence_type).
  3. Call widget = widget_container.render().
  4. Insert widget into the UI (for notebooks: display(widget)).

Destruction / cleanup:
- WidgetContainer has no special cleanup responsibilities. It returns ipywidgets.Widget objects whose lifecycle is managed by the caller and the ipywidgets framework. No explicit close() or context manager is required.

## Behavior (render):
- Signature: render(self) -> widgets.Widget
- Dispatch logic:
  - If sequence_type == "list":
      - Calls get_list(self.content["items"]) and returns the resulting widgets.VBox.
  - If sequence_type == "named_list":
      - Calls get_named_list(self.content["items"]) and returns the resulting widgets.VBox.
  - If sequence_type in ["tabs", "sections", "select"]:
      - Calls get_tabs(self.content["items"]) and returns the resulting widgets.Tab.
  - If sequence_type == "accordion":
      - Calls get_accordion(self.content["items"]) and returns the resulting widgets.Accordion.
  - If sequence_type == "grid":
      - Calls get_row(self.content["items"]) and returns the resulting widgets.GridBox.
  - If sequence_type == "batch_grid":
      - Calls get_batch_grid(
          self.content["items"],
          self.content["batch_size"],
          self.content.get("titles", True),
          self.content.get("subtitles", False),
        ) and returns the resulting widgets.GridBox.
  - Otherwise:
      - Raises ValueError("widget type not understood", self.sequence_type)

- Side effects:
  - Calls item.render() on each child Renderable (via the helper functions); any side effects from those render() calls may occur (mutations, caching, exceptions).
  - Constructs ipywidgets objects and returns them; actual frontend rendering occurs when the widget is displayed.

## Method Map:
flowchart LR
    A[call render()] --> B{sequence_type?}
    B --> |"list"| C[get_list(content['items']) -> widget]
    B --> |"named_list"| D[get_named_list(content['items']) -> widget]
    B --> |"tabs" or "sections" or "select"| E[get_tabs(content['items']) -> widget]
    B --> |"accordion"| F[get_accordion(content['items']) -> widget]
    B --> |"grid"| G[get_row(content['items']) -> widget]
    B --> |"batch_grid"| H[get_batch_grid(content['items'], content['batch_size'], content.get('titles',True), content.get('subtitles',False)) -> widget]
    B --> |other| I[raise ValueError("widget type not understood", sequence_type)]
    C --> Z[return widget]
    D --> Z
    E --> Z
    F --> Z
    G --> Z
    H --> Z

## Raises:
- ValueError("widget type not understood", sequence_type)
  - Trigger: sequence_type is not one of the handled tokens listed above.
- KeyError / TypeError / AttributeError / ZeroDivisionError / other exceptions from helper functions and their use of content:
  - If content lacks 'items' the helper calls will typically raise KeyError or a TypeError when attempting iteration.
  - If sequence_type == "batch_grid" and 'batch_size' is missing or zero, get_batch_grid may raise KeyError or ZeroDivisionError respectively.
  - Any exception that originates from:
    - accessing item metadata (e.g., get_name reading name/anchor_id) — KeyError or AttributeError,
    - item.render() implementations — arbitrary exceptions propagate,
    - ipywidgets construction/assignment — ipywidgets/traitlets errors (TypeError, TraitError).
  - WidgetContainer does not catch or translate these exceptions; they propagate to the caller.

## Example (usage pattern):
- Intended flow (descriptive):
  1. Prepare a list of Renderable items where each item implements render() and (if needed by the helper) provides name or anchor_id metadata.
  2. Construct a Container-like node so that content['items'] refers to the list and sequence_type is set to the desired layout token (for example, "tabs" or "batch_grid" with content['batch_size'] present).
  3. Call render() on the WidgetContainer to obtain an ipywidgets.Widget appropriate to the selected layout.
  4. Display or embed the returned widget in the Jupyter UI.

Notes / Implementation hints for reimplementation:
- The WidgetContainer.render implementation is a simple dispatcher: it should read self.sequence_type and call the corresponding helper function with arguments taken from self.content as shown above.
- Do not attempt to re-implement layout logic inside WidgetContainer; keep that code in the helper utilities so the dispatcher remains minimal and testable.
- Ensure that defaults for batch_grid flags mirror the documented behavior: titles default True, subtitles default False; subtitles take precedence when both True.
- Make no assumptions about the concrete types of content['items'] elements beyond that they expose render() and any required metadata; let helper functions and render() calls produce the final widget objects and raise on invalid inputs.

### `src.ydata_profiling.report.presentation.flavours.widget.container.WidgetContainer.render` · *method*

## Summary:
Selects and returns an ipywidgets widget that presents this container's content according to its configured sequence_type; does not mutate the container state.

## Description:
- Known callers / typical context:
    - Invoked by the widget-flavour rendering pipeline when a Container subclass (WidgetContainer) is being converted into a concrete ipywidgets representation for display in an IPython/Jupyter frontend.
    - Typical lifecycle stage: final presentation composition, after Container.content has been populated with child Renderable items and metadata (for example during report construction or when assembling a widget-based report page).
- Rationale for being a separate method:
    - Encapsulates the dispatch logic that maps a sequence_type string to the corresponding widget-construction helper (e.g., list, named_list, tabs, accordion, grid, batch_grid). Keeping this logic in one method avoids duplicating the mapping and centralizes error handling for unknown sequence types.

## Args:
    None (instance method uses self)

## Returns:
    widgets.Widget
    - A concrete ipywidgets.Widget instance produced by one of the helper builders:
        * widgets.VBox (from get_list or get_named_list),
        * widgets.Tab (from get_tabs),
        * widgets.Accordion (from get_accordion),
        * widgets.GridBox (from get_row or get_batch_grid),
      depending on self.sequence_type.
    - If content["items"] is empty, most helpers return an empty container widget (e.g., an empty Tab, VBox, Accordion, or GridBox) — the returned widget is still a widgets.Widget instance.

## Raises:
    - ValueError:
        - Raised exactly when self.sequence_type does not match any of the recognized cases:
          "list", "named_list", "tabs" / "sections" / "select", "accordion", "grid", or "batch_grid".
        - The code raises ValueError("widget type not understood", self.sequence_type).
    - KeyError:
        - Propagates if self.content lacks the "items" key (attempt to access self.content["items"]).
        - For sequence_type == "batch_grid", accessing self.content["batch_size"] without that key will raise KeyError.
    - Any exception propagated from the helper functions called:
        - Examples (not exhaustive; helpers may raise these as documented in their own docs):
            * TypeError or AttributeError if an item lacks the expected render() method or metadata.
            * ValueError from get_row when number of items is unsupported (e.g., len(items) not in 1..4).
            * ZeroDivisionError from get_batch_grid if batch_size == 0.
            * ipywidgets/traitlets errors (e.g., TraitError) if constructed children are not acceptable widget children.
            * Any exception raised by individual item.render() calls will propagate unchanged.

## State Changes:
- Attributes READ:
    - self.sequence_type
    - self.content (and, transitively, content["items"] and for "batch_grid" content["batch_size"], content.get("titles", ...), content.get("subtitles", ...))
- Attributes WRITTEN:
    - None — this method does not modify any self.<attr> attributes.

## Constraints:
- Preconditions:
    - self.sequence_type must be set to one of the supported types listed above. Otherwise ValueError is raised.
    - self.content must be a mapping that at minimum contains the "items" key whose value is an iterable of Renderable-like objects (objects implementing render()).
    - For sequence_type == "batch_grid", content must also contain "batch_size" (an int) and may optionally include "titles" and "subtitles" (booleans). batch_size must be >= 1 to avoid ZeroDivisionError in the helper.
    - Each element in content["items"] must be suitable for the chosen helper:
        * implement render() that returns an ipywidgets-compatible child, and
        * provide metadata required by the helper (e.g., name or anchor_id for named layouts) to avoid KeyError/AttributeError.
- Postconditions:
    - On successful return, a widgets.Widget instance representing the requested layout is returned and no attributes of the WidgetContainer instance have been changed.
    - The returned widget's children correspond (in order) to the results of rendering the items via the helper functions (which in turn call each item's render()).

## Side Effects:
- The method calls one of the helper builders (get_list, get_named_list, get_tabs, get_accordion, get_row, get_batch_grid). Those helpers:
    - Call item.render() for each element in content["items"], which may produce widget objects and may have side effects defined by the Renderable implementations (e.g., allocate state, raise exceptions, or perform lazy computation).
    - Construct ipywidgets objects (VBox, Tab, Accordion, GridBox) that allocate frontend resources when displayed; this method itself only returns the widget object.
- No I/O (file, network) or mutation of external/global state is performed directly by this method.

