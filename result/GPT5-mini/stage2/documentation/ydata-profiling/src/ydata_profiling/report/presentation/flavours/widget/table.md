# `table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.table.get_table` · *function*

## Summary:
Builds an ipywidgets two-column GridspecLayout for display in Jupyter frontends from a list of row dictionaries, applying an "error" color to any row marked as an alert.

## Description:
Converts a list of simple row descriptions (dictionaries) into a UI widget that displays each row as a left (name) / right (value) pair. For items that include an "alert" key with a truthy value, both the name and value strings are wrapped using the shared fmt_color formatter with the CSS variable var(--jp-error-color1) to visually indicate problems.

Known callers within the provided context:
- No direct callers were present in the provided file-level context. In the broader project this function is intended for use by presentation layers that render summary tables (for example, notebook-renderers or widget-builders) which transform domain Table-like structures into ipywidgets for interactive display.

Why this function is extracted:
- Centralizes conversion of a serializable row representation into concrete ipywidgets widgets and enforces consistent alert styling. This keeps widget construction and alert-formatting separate from data-collection logic and higher-level layout composition.

## Args:
    items (List[Dict[str, Any]]):
        - A list of dictionaries defining rows. Each dictionary must include:
            - "name": typically a string (displayed in the left column).
            - "value": typically a string (displayed in the right column).
        - Optional key:
            - "alert": truthy/falsy. If truthy, the "name" and "value" are formatted via fmt_color(..., "var(--jp-error-color1)").
        - Interdependencies:
            - "name" and "value" are required for each entry; missing keys cause KeyError when accessed.
        - Mutability note:
            - The function does not modify the input list or its dictionaries; it only reads values.

## Returns:
    GridspecLayout
        - A newly-constructed ipywidgets.GridspecLayout with rows == len(items) and 2 columns.
        - Each cell contains an ipywidgets.HTML widget:
            - cell (row, 0): HTML containing the (possibly color-wrapped) name.
            - cell (row, 1): HTML containing the (possibly color-wrapped) value.
        - Edge-case return values:
            - If len(items) == 0, a GridspecLayout is constructed with 0 rows; exact front-end behavior depends on ipywidgets and the notebook environment (no extra handling is performed here).

## Raises:
    - KeyError: if any item lacks the "name" or "value" key (accesses item["name"] and item["value"] directly).
    - Exceptions propagated from dependencies:
        - ipywidgets.GridspecLayout(...) may raise an exception for invalid dimensions.
        - widgets.HTML(...) may raise if provided an unacceptable value.
        - fmt_color(...) may raise for unexpected input types.
    - The function itself does not wrap or convert these exceptions; they propagate to the caller.

## Constraints:
    Preconditions:
        - items must be an iterable (commonly a list) of dictionaries.
        - Each dictionary must contain "name" and "value".
        - Caller should run in an environment with ipywidgets available if they intend to render the result.
    Postconditions:
        - On success, returns a GridspecLayout with one HTML widget per table cell and no mutation to the provided items list.

## Side Effects:
    - No file, network, or global state side effects.
    - Allocates ipywidgets objects (GridspecLayout and HTML); if displayed, these objects may initiate front-end messages in a notebook environment.
    - Calls fmt_color to produce HTML strings; fmt_color is expected to be a pure formatter (no side effects assumed).

## Control Flow:
flowchart TD
    Start --> CreateLayout[Create GridspecLayout(rows=len(items), cols=2)]
    CreateLayout --> ForEach[For each (row_id, item) in enumerate(items)]
    ForEach --> ReadFields[Read name = item["name"], value = item["value"]]
    ReadFields --> HasAlert{ "alert" in item and item["alert"] ? }
    HasAlert -->|yes| Colorize[Apply fmt_color(name, error_color) and fmt_color(value, error_color)]
    HasAlert -->|no| NoColor[Keep name and value as-is]
    Colorize --> MakeHTML[Create widgets.HTML for name and value]
    NoColor --> MakeHTML
    MakeHTML --> Assign[Assign to table[row_id,0] and table[row_id,1]]
    Assign --> ForEach
    ForEach --> End[Return table]

## Examples:
Typical input to display a small summary table (conceptual example, imports omitted):
- Prepare rows:
    - rows = [
        {"name": "Missing values", "value": "5 (0.4%)"},
        {"name": "Unique values", "value": "120"},
        {"name": "Warnings", "value": "3", "alert": True}
      ]
- Convert to widget:
    - widget_table = get_table(rows)
- Render in a notebook:
    - Use the notebook display mechanism (for example, display(widget_table)) to show the two-column layout. The "Warnings" row will have name and value colored using the Jupyter error color variable.

Validation and error-handling patterns:
- Pre-validate input to avoid KeyError:
    - If items are dynamically generated or may omit keys, sanitize with a list comprehension that provides defaults:
        - filtered = [r for r in rows if "name" in r and "value" in r]
    - Or wrap the call in try/except to capture KeyError and handle missing fields gracefully:
        - try:
            widget = get_table(rows)
          except KeyError as e:
            handle_missing_key(e)

Performance and ergonomics:
- Lightweight: widget construction is linear in the number of rows.
- For very large lists consider paginating or summarizing before converting to widgets to avoid creating many widget objects.

Notes:
- This function focuses purely on presentation widget construction; it does not perform escaping or HTML sanitization beyond whatever fmt_color and widgets.HTML provide. If input strings may contain untrusted HTML, sanitize beforehand.

## `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable` · *class*

## Summary:
Represents the widget-flavour concrete Table renderer that builds an ipywidgets.VBox containing a two-column GridspecLayout table (via get_table) and an optional italicized caption. Its single responsibility is to convert the Table payload (self.content) into ipywidgets widgets for display in Jupyter frontends.

## Description:
WidgetTable is a minimal concrete renderer subclassing the generic Table presentation item. Instantiate it when you have a Table payload (rows, style, optional name/caption) and you need an ipywidgets-based visual representation suitable for embedding in a Jupyter notebook UI.

Typical creation/usage scenarios:
- A report builder or presentation factory creates a WidgetTable (using Table.__init__ inherited behavior) with a rows sequence and a validated Style object, then calls render() to obtain a VBox widget to display inside a notebook or compose into a larger layout.
- Use this subclass when the presentation target is an interactive notebook; other flavours (HTML, JSON) use different concrete renderers.

Responsibility boundary:
- WidgetTable is strictly a view-layer concern. It does not mutate the underlying rows or other content, does not perform sanitization/escaping beyond what its dependencies provide, and does not manage external resources. It delegates per-row widget construction to the module-level get_table helper and only composes the returned widget with an optional caption.

## State:
Inherited state (from Table):
- item_type (str)
  - Value: "table"
  - Invariant: must remain "table" for WidgetTable instances.
- content (dict-like)
  - Keys guaranteed by Table.__init__:
    - "rows": Sequence[Any]
      - Typical shape expected by get_table: List[Dict[str, Any]] where each dict contains:
        - "name" (str): left-column display string (required)
        - "value" (str): right-column display string (required)
        - Optional "alert" (truthy/falsy): if truthy, name and value will be formatted with fmt_color(..., "var(--jp-error-color1)").
      - Valid range/values: any sequence length >= 0. If empty, get_table returns a GridspecLayout with 0 rows (frontend behavior may vary).
      - Invariant: content["rows"] reference is preserved (Table stores the reference; external mutation is visible).
    - "style": Style
      - Type: Style (pydantic model). WidgetTable does not use style directly in render(), but the presence is part of Table's invariant.
    - "name": Optional[str]
      - May be None; WidgetTable does not use name in render().
    - "caption": Optional[str]
      - If not None, render() will create a widgets.HTML containing the caption wrapped with <em>...</em>.
      - Caller must ensure caption is a value acceptable to widgets.HTML (typically a str). Passing non-string objects may raise when widgets.HTML constructs the widget.

WidgetTable-specific attributes:
- None. WidgetTable adds no new instance attributes beyond those set by Table.__init__.

Class invariants:
- self.item_type == "table"
- self.content contains the keys "rows", "style", "name", and "caption" after construction.
- render() does not modify self.content or the objects within it.

## Lifecycle:
Creation:
- Instantiate using Table's constructor signature (WidgetTable inherits Table.__init__):
  - Required: rows (Sequence), style (Style instance)
  - Optional: name (str|None) default None, caption (str|None) default None
  - Additional kwargs forwarded to ItemRenderer.__init__ are allowed (e.g., anchor_id, classes).
- Typical instantiation:
  - Provide a sequence of row dicts and a validated Style instance; create WidgetTable(rows=rows, style=style, name="...", caption="...").

Usage:
- Call render() to produce an ipywidgets.VBox containing:
  1. The table widget returned by get_table(self.content["rows"]) (an ipywidgets.GridspecLayout).
  2. Optionally, an ipywidgets.HTML caption widget (if content["caption"] is not None).
- Ordering and sequencing:
  - No special sequencing requirements beyond constructing the instance before calling render().
  - render() is idempotent with respect to instance state: repeated calls produce new widget objects based on the current content snapshot (any external mutations to content["rows"] or content["caption"] will be reflected on next render()).

Destruction / cleanup:
- No explicit cleanup is required. Widget objects returned by render() are standard ipywidgets objects; their lifecycle is managed by the Python/Jupyter runtime and the notebook frontend. If you embed widgets in persistent UI structures, manage references as appropriate to allow garbage collection.

## Method Map:
flowchart TD
    Render[WidgetTable.render()] --> CallGetTable[get_table(self.content["rows"])]
    CallGetTable --> TableWidget[GridspecLayout (rows x 2) with widgets.HTML children]
    Render --> CheckCaption{self.content["caption"] is not None?}
    CheckCaption -->|Yes| MakeCaption[widgets.HTML(f'<em>{caption}</em>')]
    CheckCaption -->|No| SkipCaption[no caption widget]
    TableWidget --> Assemble[items = [table_widget]; append caption if any]
    MakeCaption --> Assemble
    Assemble --> ReturnVBox[return VBox(items)]

Notes on the method graph:
- get_table constructs the two-column grid and the HTML cell widgets for each row; WidgetTable only composes that result into a VBox along with an optional caption.

## Raises:
WidgetTable.render() does not raise new exceptions itself but propagates exceptions from its dependencies and from malformed content:
- KeyError:
  - Possible if self.content is missing "rows" or "caption" keys (Table.__init__ normally prevents this; KeyError can occur if content was externally mutated).
  - Also possible indirectly if get_table expects fields inside each row dict ("name", "value") and a row is missing keys — get_table will raise KeyError.
- Exceptions from get_table:
  - ValueError/TypeError due to invalid items (e.g., not iterable, wrong shape), ipywidgets errors when creating a GridspecLayout, or fmt_color raising for unexpected inputs.
- Exceptions from widgets.HTML:
  - If caption is of an unacceptable type or ipywidgets rejects the content, widgets.HTML(...) may raise.
- Any exception raised during widget construction propagates to the caller; WidgetTable.render() does not wrap these exceptions.

## Example:
- Construct a WidgetTable and render it to obtain an ipywidgets.VBox (usage described in prose; adapt imports and Style construction to your environment):
  1. Prepare a sequence of rows in the expected shape:
     - rows = [
         {"name": "Missing values", "value": "5 (0.4%)"},
         {"name": "Unique values", "value": "120"},
         {"name": "Warnings", "value": "3", "alert": True}
       ]
  2. Create or obtain a validated Style instance (pydantic Style) required by Table.
  3. Instantiate the renderer (inherited Table.__init__ signature):
     - widget_table = WidgetTable(rows=rows, style=style, name="Summary", caption="Dataset summary")
  4. Render to widgets:
     - vbox = widget_table.render()
     - The returned vbox.children[0] is the GridspecLayout table; if caption was provided, vbox.children[1] is an HTML widget with the italicized caption.
  5. Display in a notebook (e.g., using display(vbox) in a Jupyter environment) to see the constructed table and caption.

Practical notes and cautions:
- Sanitization responsibility: WidgetTable delegates per-row widget creation to get_table and uses widgets.HTML to construct the caption. Neither get_table nor widgets.HTML performs HTML sanitization beyond their own formatting behavior (fmt_color may wrap strings in HTML); therefore, if row values or caption may contain untrusted HTML, callers should sanitize or escape those strings before constructing the WidgetTable's content.
- Mutability: content is stored by reference. If the caller mutates content["rows"] after constructing WidgetTable but before calling render(), those changes will influence the produced widgets.
- Performance: rendering constructs ipywidgets objects per call; avoid rendering very large row lists directly in a notebook without pagination or summarization.

### `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable.render` · *method*

## Summary:
Returns an ipywidgets VBox that contains a rendered table widget built from the instance rows and an optional italicized caption; does not modify the renderer's stored content.

## Description:
- Known callers and lifecycle:
    - Invoked by presentation/rendering code in the widget (Jupyter) flavour of the reporting pipeline when a concrete Table renderer is asked to produce an ipywidgets-based representation. Typical callers are report builders or presentation factories that assemble report items for display in notebooks.
    - Lifecycle stage: called during the final render/compose phase of report generation, when domain data has already been converted into this Table instance's content payload and the pipeline needs a widget to insert into a notebook or a greater VBox layout.

- Why this is a separate method:
    - Encapsulates widget-construction concerns for this concrete Table renderer so higher-level code can remain agnostic about ipywidgets layout details. Keeping layout assembly here improves reuse and isolates the dependency on get_table and ipywidgets.HTML creation.

## Args:
    None

## Returns:
    ipywidgets.VBox
        - A VBox whose children list is constructed as follows:
            1. The first (and always present) child is the result of get_table(self.content["rows"]). Per the get_table contract, this is an ipywidgets.GridspecLayout with rows == len(rows) and 2 columns (each cell contains an ipywidgets.HTML widget).
            2. If self.content["caption"] is not None, the second child is an ipywidgets.widgets.HTML constructed from the caption string wrapped in <em>...</em>.
        - Edge cases:
            - If rows is empty, the first child is a GridspecLayout with 0 rows (frontend behavior may vary).
            - If caption is None, the VBox will contain only the table child.
            - Caption string is embedded verbatim inside <em> tags and passed to widgets.HTML (no extra escaping is performed here).

## Raises:
    - Any exception raised by get_table when called with the provided rows:
        * For example, KeyError if rows elements are dictionaries missing required keys (per get_table expectations), or other exceptions raised by ipywidgets during layout/widget construction.
    - Any exception raised by widgets.HTML when constructing the caption widget (e.g., if caption is of an unacceptable type).
    - KeyError is unlikely for well-formed Table instances because Table.__init__ guarantees the presence of "rows" and "caption" keys in self.content, but KeyError can occur if content has been externally mutated to remove those keys prior to calling render().

## State Changes:
- Attributes READ:
    - self.content (reads keys:)
        - self.content["rows"] — used as the input to get_table(...)
        - self.content["caption"] — read to decide whether to append a caption widget
- Attributes WRITTEN:
    - None — this method does not modify self or self.content.

## Constraints:
- Preconditions:
    - self.content must be a dict-like object containing the keys "rows" and "caption" (Table.__init__ normally ensures this).
    - self.content["rows"] should be in the shape expected by the module-level get_table function (a sequence of row dictionaries with the fields get_table expects, typically dictionaries with "name" and "value"); otherwise get_table may raise.
    - The runtime environment should have ipywidgets available if the caller intends to display the returned widget (construction itself requires ipywidgets imports to succeed).
- Postconditions:
    - Returns a VBox whose children are the assembled widgets described above.
    - self.content and other external objects referenced by rows are not mutated by this call.

## Side Effects:
- Allocates ipywidgets widget objects (GridspecLayout and possibly an HTML widget for the caption). When displayed in a Jupyter frontend, these widgets may cause front-end rendering activity and messaging.
- Does not perform any filesystem, network, or global state I/O.
- No mutation of objects outside self is performed by this method; the created widgets hold references to any widget objects contained in rows.

