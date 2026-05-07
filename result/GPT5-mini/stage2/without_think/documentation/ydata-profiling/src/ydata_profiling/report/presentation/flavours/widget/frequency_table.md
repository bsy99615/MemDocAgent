# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.get_table` · *function*

## Summary:
Assemble a 3-column ipywidgets grid from a list of row widget triplets and return it wrapped in a VBox for display.

## Description:
This helper builds a visual table using ipywidgets by placing provided widget triples into a GridspecLayout with three columns and one row per item. It is intended for the presentation layer that has already created per-row widgets (e.g., a left label, a progress bar, and a right count) and needs to assemble them into a single displayable widget.

Known callers and context:
- There are no explicit callers in the provided snippet. The function is part of the widget flavour of the reporting presentation layer and is intended to be used wherever a simple 3-column frequency table widget is required (for example, when rendering FrequencyTable instances into ipywidgets).

Why this is a separate function:
- It centralizes the layout logic (creating a GridspecLayout and placing widgets into cells) so that higher-level rendering code can focus on data-to-widget creation. This improves reuse and keeps rendering code concise.

## Args:
    items (List[Tuple[widgets.Label, widgets.FloatProgress, widgets.Label]]):
        A sequence (typically a list) of rows to include in the table. Each row must be a 3-tuple in this order:
        1. left cell widget (commonly widgets.Label, but any ipywidgets.Widget is acceptable)
        2. middle cell widget (commonly widgets.FloatProgress or another progress-type widget)
        3. right cell widget (commonly widgets.Label showing the count)
        Notes:
        - The function does not validate widget types beyond relying on ipywidgets to accept the assigned widget objects.
        - items may be empty; see Constraints for behavior guidance.
        - Each element of items must be an iterable of exactly three elements; otherwise unpacking will fail.

## Returns:
    VBox
        A widgets.VBox containing a single GridspecLayout:
        - The GridspecLayout has rows = len(items) and cols = 3.
        - For each row i (0-based), the widgets are placed as:
            * table[i, 0] = left widget
            * table[i, 1] = middle widget
            * table[i, 2] = right widget
        Edge cases:
        - If items is empty, a GridspecLayout with 0 rows is created and returned inside a VBox. Rendering behavior for an empty GridspecLayout depends on the ipywidgets version and frontend; callers that need a visible placeholder should supply a placeholder row instead.

## Raises:
    - ValueError or TypeError from Python unpacking:
        * If any item in items does not contain exactly three elements, the tuple unpacking in the for-loop will raise ValueError (not caught inside the function).
        * If an item is not iterable, a TypeError may be raised during unpacking.
    - TypeError/ValueError from ipywidgets:
        * If len(items) is not a non-negative integer or if GridspecLayout rejects the provided dimensions, GridspecLayout(...) may raise an exception.
        * Assigning a widget to table[row, col] may raise exceptions if ipywidgets rejects the assignment. These exceptions originate from ipywidgets and are not handled here.
    - The function itself does not raise custom exceptions.

## Constraints:
    Preconditions:
    - items must be a sequence (or other iterable) for which len(items) is valid and each element unpacks into exactly three values.
    - The caller is responsible for preparing widgets appropriate for display in the given columns. The function will not coerce or convert non-widget values.

    Postconditions:
    - On successful return, the returned VBox contains a GridspecLayout with the supplied widgets placed at the correct row/column coordinates.
    - The original widget objects are referenced (not copied); their state remains under the caller's control.

## Side Effects:
    - No filesystem, network, or stdout I/O occurs.
    - No global state is mutated.
    - The only side effect is creation and arrangement of ipywidgets objects; rendering these widgets in a Jupyter frontend will affect the frontend display.

## Control Flow:
flowchart TD
    Start[Start] --> CreateTable[Create GridspecLayout(rows=len(items), cols=3)]
    CreateTable --> ForLoop{enumerate(items)}
    ForLoop --> Unpack[Unpack (label, progress, count)]
    Unpack --> AssignLabel[Set table[row_id,0] = label]
    AssignLabel --> AssignProgress[Set table[row_id,1] = progress]
    AssignProgress --> AssignCount[Set table[row_id,2] = count]
    AssignCount --> Next{More items?}
    Next -->|Yes| ForLoop
    Next -->|No| Wrap[Return VBox([table])]
    Wrap --> End[End]

## Examples (usage described in prose):
- Typical sequence:
  1. Higher-level code constructs per-row widgets, for example:
     - a left label widget showing the category name,
     - a FloatProgress widget configured with a value and max to visualize relative frequency,
     - a right label widget showing the absolute count or formatted percentage.
  2. Those triples are collected into a list in display order.
  3. The list is passed to this function which returns a VBox containing the assembled table.
  4. The caller inserts or displays the returned VBox in the notebook or composes it into a larger report widget.

- Practical guidance:
  - If your data source can produce rows with missing elements, validate or filter rows before calling get_table to avoid unpacking errors.
  - If you must handle zero-row results robustly across ipywidgets versions, either provide a single placeholder row (e.g., a label stating "No data") or check len(items) and skip rendering the table entirely.

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable` · *class*

## Summary:
WidgetFrequencyTable is a concrete FrequencyTable renderer that converts frequency-table data into an ipywidgets VBox containing a 3-column visual table (label, progress bar, count) suitable for Jupyter notebook display.

## Description:
WidgetFrequencyTable implements the abstract render() hook of FrequencyTable to produce an interactive widget representation of a variable's frequency distribution. It is intended to be instantiated by the reporting code that assembles a FrequencyTable (or its subclass) and then calls render() when a notebook/ipython widget output is desired.

Typical callers/factories:
- Report assembly code that constructs FrequencyTable-like items and selects a widget-based presentation flavour for notebook output.
- Any code that constructs a WidgetFrequencyTable instance via the FrequencyTable constructor signature and calls render() to obtain a widgets.VBox.

Motivation and responsibility boundary:
- Purpose: map frequency row data to a three-column ipywidgets layout where each row shows (left) the category label, (middle) a FloatProgress visualizing relative frequency, and (right) the absolute count.
- Boundary: This class only performs presentation logic. It does not compute frequencies, perform redaction policy decisions beyond reading the redact flag (it does not currently alter labels based on redact); it expects callers to supply prepared row data in the expected shape.

## State:
Attributes inherited from FrequencyTable (relevant here):
- item_type (str)
  - Value: "frequency_table"
  - Invariant: remains "frequency_table"
- content (dict)
  - Required keys used by this implementation:
    - "rows": sequence
      - Expected shape for WidgetFrequencyTable:
        - content["rows"] must be a non-empty sequence whose first element (content["rows"][0]) is itself an iterable of per-row dictionaries.
        - Each per-row dictionary must contain the keys:
          - "label" (str-like): the category label to display on the left cell
          - "count" (numeric): absolute count used as the FloatProgress value and shown on the right
          - "n" (numeric): the maximum/total used as FloatProgress max (commonly total sample size)
          - "extra_class" (str): one of "missing", "other", or any other string; controls progress bar style:
            * "missing" -> bar_style="danger"
            * "other" -> bar_style="info"
            * otherwise -> bar_style="" (default)
        - Example per-row dict: {"label": "A", "count": 5, "n": 100, "extra_class": ""}
      - Notes:
        - It is acceptable for content["rows"][0] to be an empty iterable (resulting in an empty table).
        - If content["rows"] is empty (no first element), an IndexError will be raised when render() runs.
    - "redact": bool
      - Although present (per FrequencyTable contract), this WidgetFrequencyTable implementation does not automatically redact label strings; callers should prepare rows accordingly if redaction is required.
- name, anchor_id, classes (optional): forwarded metadata; not used by render().

Class invariants:
- item_type == "frequency_table"
- content is a dict containing at least the key "rows" whose first element is iterable and contains per-row dicts with keys listed above.

## Lifecycle:
Creation:
- Instantiate using the FrequencyTable constructor signature:
  - Required positional args:
    - rows (list-like): in this flavour the top-level rows argument should be provided such that content["rows"][0] yields the iterable of per-row dicts described in State.
    - redact (bool): whether values are considered sensitive (this implementation will not mask labels automatically).
  - Optional kwargs forwarded from FrequencyTable/ItemRenderer: name, anchor_id, classes.

Usage:
- Typical sequence:
  1. Construct WidgetFrequencyTable(rows, redact, name=..., anchor_id=..., classes=...).
     - Ensure rows is a sequence whose first element is the iterable of row dicts (see State).
  2. Call render() to receive an ipywidgets.VBox containing the assembled table.
  3. Display the returned VBox in an IPython/Jupyter environment (e.g., display(obj.render())) or embed it in a larger widget layout.
- Ordering requirements:
  - There is no required ordering of other methods; render() may be called multiple times. render() reads self.content at call time and does not mutate instance state.

Destruction / cleanup:
- No explicit cleanup or context-manager behavior. The returned widgets are regular ipywidgets objects; lifecycle is managed by the caller and the notebook frontend. Delete references to allow GC when no longer needed.

## Method Map:
flowchart TD
  A[render()] --> B[reads self.content["rows"][0]]
  B --> C[for each row in rows: create widgets.Label(row["label"])]
  C --> D[create widgets.FloatProgress(value=row["count"], min=0, max=row["n"], bar_style=...)]
  D --> E[create widgets.Label(str(row["count"]))]
  E --> F[collect per-row triplet into items list]
  F --> G[call get_table(items)]
  G --> H[return VBox (assembled table)]

## Raises:
The implementation performs direct indexing and dictionary access; when preconditions are not met the following exceptions can be raised at runtime:
- IndexError:
  - If content["rows"] exists but is empty, accessing content["rows"][0] raises IndexError.
- KeyError:
  - If content lacks "rows" key, content["rows"] will raise KeyError.
  - If a row dictionary misses any required key ("label", "count", "n", "extra_class"), row[...] will raise KeyError.
- TypeError / ValueError:
  - If rows is not indexable or content["rows"][0] is not iterable, TypeError may occur.
  - If "count" or "n" values are not numeric, constructing FloatProgress or assigning widget values may raise errors propagated from ipywidgets.
  - If an item in the collected items does not have exactly three elements (this cannot occur here because items are constructed consistently), the called get_table may raise unpacking-related exceptions if misused; in the provided implementation items are well-formed.
- Widget-related exceptions:
  - Errors raised by ipywidgets during GridspecLayout creation or widget assignment (propagated from get_table).

## Behavior and edge cases:
- Progress bar bar_style mapping:
  - extra_class == "missing" -> bar_style="danger" (visual emphasis)
  - extra_class == "other" -> bar_style="info"
  - otherwise -> bar_style="" (default)
- Redaction:
  - Although FrequencyTable provides a "redact" flag in content, WidgetFrequencyTable does not apply label masking. If redaction is required, callers should pre-mask labels before passing them in rows.
- Empty table handling:
  - If content["rows"][0] is an empty iterable, render() passes an empty items list to get_table which returns a VBox wrapping an empty GridspecLayout (see get_table contract).
  - If content["rows"] is empty (no first element), render() raises IndexError.

## Example:
- Conceptual creation and usage (prose form):
  1. Prepare rows_for_widget as an iterable of per-row dicts:
     - e.g., rows_for_widget = [
         {"label": "cat_A", "count": 10, "n": 100, "extra_class": ""},
         {"label": "MISSING", "count": 5, "n": 100, "extra_class": "missing"},
         {"label": "other", "count": 2, "n": 100, "extra_class": "other"},
       ]
  2. Supply the top-level rows argument so that content["rows"][0] == rows_for_widget:
     - top_level_rows = [rows_for_widget]
  3. Instantiate the widget renderer:
     - widget_table = WidgetFrequencyTable(top_level_rows, redact=False)
  4. Render to obtain a displayable VBox:
     - vbox = widget_table.render()
  5. Display vbox in a Jupyter notebook (e.g., using display(vbox)).

Notes:
- If you require automatic redaction of labels, transform labels in rows_for_widget before creating the WidgetFrequencyTable instance.
- Ensure numeric types for "count" and "n" (int or float) to avoid widget errors.

### `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable.render` · *method*

## Summary:
Create an ipywidgets VBox containing a 3-column visual frequency table built from self.content["rows"], converting each frequency row into a (left label, progress bar, right label) widget triplet and assembling them with get_table.

## Description:
- Known callers and context:
    - The report/presentation pipeline invokes this method when rendering a FrequencyTable instance for the "widget" flavour (ipywidgets) as part of the presentation stage of report generation. Callers prepare frequency data (rows) and then call this render() to obtain a widget suitable for inclusion in a notebook or widget-based report layout.
    - Lifecycle stage: invoked at presentation time (after frequency computation and any redaction decisions).
- Why this logic is a separate method:
    - This method encapsulates UI-specific construction (ipywidgets creation and bar-style mapping) so that the data-holder (FrequencyTable) can be converted into multiple presentation formats by different concrete renderers. Keeping widget layout and styling here avoids inlining UI code in higher-level report assembly or in generic data objects.

## Args:
    None

## Returns:
    ipywidgets.VBox
        - The VBox returned wraps a GridspecLayout table produced by get_table(items).
        - Each row in the table corresponds to one entry in self.content["rows"][0] and contains three widgets in this order:
            1. widgets.Label(str(row["label"])) — left cell
            2. widgets.FloatProgress(value=row["count"], min=0, max=row["n"], bar_style=...) — middle cell
            3. widgets.Label(str(row["count"])) — right cell
        - bar_style mapping:
            * row["extra_class"] == "missing" -> "danger"
            * row["extra_class"] == "other" -> "info"
            * otherwise -> "" (no special style)
        - Edge-case returns:
            * If items is empty (e.g., rows iterable is empty), get_table will return a VBox containing a GridspecLayout with 0 rows (frontend rendering may vary across ipywidgets versions).
            * The function always returns the get_table result on successful construction; it does not return None.

## Raises:
    - KeyError:
        * If self.content is missing or does not contain the "rows" key.
        * If a row dict is missing any of the expected keys: "label", "count", "n", or "extra_class".
    - IndexError:
        * If self.content["rows"] is an indexable sequence but is empty, accessing [0] raises IndexError.
    - ValueError, TypeError (from ipywidgets or Python unpacking):
        * If get_table or widgets.FloatProgress is called with invalid types or invalid dimensions (e.g., non-iterable rows, an item not unpackable into three values, or GridspecLayout rejecting a 0/negative dimension).
        * If row["n"] is an invalid numeric value for FloatProgress (behavior governed by ipywidgets).
    - Any exceptions raised by ipywidgets constructors/assignments may propagate (these are not caught here).

## State Changes:
- Attributes READ:
    - self.content (specifically self.content["rows"])
- Attributes WRITTEN:
    - None (the method does not mutate self or self.content)

## Constraints:
- Preconditions:
    - self.content must be a mapping containing a "rows" key.
    - self.content["rows"] must be indexable and non-empty (since the implementation accesses self.content["rows"][0]).
    - The first element of self.content["rows"] (rows variable) must be an iterable of row entries.
    - Each row entry must be a mapping-like object with the keys:
        * "label" — convertible to str
        * "count" — numeric (used as FloatProgress.value)
        * "n" — numeric (used as FloatProgress.max)
        * "extra_class" — str or value comparable to "missing"/"other"
- Postconditions:
    - A VBox is returned containing a GridspecLayout with one row per element in rows and three columns; the original self.content remains unchanged.
    - The ordering of rows in the returned widget matches the iteration order of rows.
    - No mutation occurs on row objects or on self.

## Side Effects:
- Creates ipywidgets.Widget objects (widgets.Label, widgets.FloatProgress, GridspecLayout, VBox) that are returned to the caller; creation may allocate frontend resources when displayed.
- No filesystem, network, or global state side effects.
- Exceptions from ipywidgets constructors or get_table are propagated to the caller.

