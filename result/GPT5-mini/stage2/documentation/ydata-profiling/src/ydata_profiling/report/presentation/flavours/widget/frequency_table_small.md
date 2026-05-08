# `frequency_table_small.py`

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.WidgetFrequencyTableSmall` · *class*

## Summary:
A notebook (ipywidgets) renderer for the compact frequency-table presentation model; it converts the stored frequency rows into an ipywidgets.VBox using the notebook-specific helper.

## Description:
WidgetFrequencyTableSmall is a concrete renderer subclass of FrequencyTableSmall intended for Jupyter notebook (ipywidgets) output. It exists to implement the render() contract declared by the FrequencyTableSmall model by delegating to the frequency_table_nb function, which converts the stored rows into a widgets.VBox composed of FloatProgress bars and Labels.

Typical instantiation scenarios:
- When the presentation pipeline chooses the "widget" / notebook flavour for report output, it will create or receive instances of this class (or a factory will instantiate this class) to render small frequency tables directly into notebook UI elements.
- It is used when you have already-prepared frequency rows (the data aggregation/formatting step is complete) and you want an ipywidgets-based visual representation in a Jupyter notebook.

Responsibility boundary:
- This class is solely responsible for mapping FrequencyTableSmall content (read-only) into an ipywidgets.VBox. It does not perform data aggregation, validation beyond what frequency_table_nb expects, or mutate the stored content.
- Presentation logic for non-notebook backends (HTML, JSON, templates) is out of scope; those backends should implement their own FrequencyTableSmall subclasses.

## State:
Inherited from FrequencyTableSmall (documented in the parent class):
- item_type (str)
  - Value: "frequency_table_small"
  - Invariant: item_type == "frequency_table_small"

- content (dict)
  - Keys:
    - "rows": List[Any]
      - The exact expected structure is a nested list where rows[0] is an iterable of dictionaries. Each dictionary must contain the keys "label", "count", "n", and "extra_class" (see frequency_table_nb for details).
      - No structural validation is done by this class; incorrect shapes will cause frequency_table_nb (and thus render) to raise.
    - "redact": bool
      - Indicates whether sensitive values should be redacted by presentation layers; this class does not apply redaction itself (the underlying frequency_table_nb renders values as provided).
  - Invariant: "rows" and "redact" keys exist in content after construction.

- Additional inherited optional fields forwarded via kwargs:
  - name: Optional[str]
  - anchor_id: Optional[str]
  - classes: Optional[str]

Notes on __init__ parameters (inherited):
- rows: List[Any] — required by FrequencyTableSmall; must be provided by callers.
- redact: bool — required by FrequencyTableSmall; must be provided.
- No additional constructor parameters are defined on WidgetFrequencyTableSmall itself; it inherits initialization behavior.

Class invariants:
- After construction, content must contain "rows" and "redact", and item_type must equal "frequency_table_small".
- render() must not mutate self.content.

## Lifecycle:
Creation:
- Instantiate via the FrequencyTableSmall constructor (WidgetFrequencyTableSmall(...) will accept the same constructor parameters as its parent; typical call supplies rows and redact along with optional name/anchor_id/classes).
- Example: widget_renderer = WidgetFrequencyTableSmall(rows=[{"label":"A","count":10,"n":20,"extra_class":""}], redact=False)

Usage:
- Primary operation: call widget_renderer.render() to obtain an ipywidgets.VBox ready for display in a Jupyter notebook.
- Expected call order:
  1) Construct the instance (provide rows and redact).
  2) Call render() exactly when you want to convert the stored rows into an ipywidgets.VBox.
  3) Display the returned widgets.VBox in a notebook cell, or embed it into a larger ipywidgets layout.
- There are no other lifecycle methods; the returned widgets remain managed by the caller and the Jupyter environment.

Destruction / cleanup:
- No explicit cleanup or context-management methods are required or provided.
- Instances and created widget objects rely on Python garbage collection; if widgets are displayed in the notebook, their lifecycle is governed by the notebook frontend and ipywidgets.

## Method Map:
flowchart TD
    A[Caller] --> B[WidgetFrequencyTableSmall.render()]
    B --> C[access self.content["rows"]]
    C --> D[frequency_table_nb(rows)]
    D --> E[returns widgets.VBox]
    E --> F[Caller displays VBox in notebook]

- render() delegates to frequency_table_nb and returns the resulting widgets.VBox. The function frequency_table_nb performs the per-row widget construction (FloatProgress + Label) and sets styles for special extra_class values.

## Raises:
WidgetFrequencyTableSmall.render() does not itself explicitly raise errors but may propagate exceptions raised by frequency_table_nb or by accessing content:

- KeyError:
  - If self.content does not contain the "rows" key (e.g., malformed content), a KeyError will be raised when render accesses content["rows"].
  - If rows[0] contains dictionaries missing required keys ("label", "count", "n", "extra_class"), frequency_table_nb will raise KeyError when it accesses them.

- IndexError:
  - If content["rows"] is empty or not indexable as expected (frequency_table_nb accesses rows[0]), an IndexError will be raised.

- TypeError:
  - If content["rows"] is None or not subscriptable, or if row items are not mapping-like, TypeError can propagate from frequency_table_nb or Python indexing.

- ValueError / widget-related exceptions:
  - ipywidgets.FloatProgress or widgets.Label construction inside frequency_table_nb may raise widget-specific exceptions or ValueError when given inappropriate types; those exceptions propagate to the caller.

Guidance:
- Callers should ensure content["rows"] conforms to the expected nested-list-of-dicts structure before calling render() if they need to avoid these propagated exceptions.

## Example:
1) Typical usage in a notebook-oriented presentation pipeline:

    # Assume upstream aggregation produced rows in the expected format
    rows = [
        [
            {"label": "A", "count": 40, "n": 100, "extra_class": ""},
            {"label": "B", "count": 30, "n": 100, "extra_class": "other"},
            {"label": "Missing", "count": 5, "n": 100, "extra_class": "missing"},
        ]
    ]
    widget_renderer = WidgetFrequencyTableSmall(rows=rows, redact=False)
    vbox = widget_renderer.render()  # returns an ipywidgets.VBox
    # In a Jupyter notebook cell:
    display(vbox)

2) Error case (illustrative):

    # Missing rows[0] will cause IndexError when rendering
    bad_rows = []
    widget_renderer = WidgetFrequencyTableSmall(rows=bad_rows, redact=False)
    try:
        widget_renderer.render()
    except IndexError:
        # Handle or log the malformed input upstream
        pass

Notes:
- This class is a thin adapter: it does no validation beyond what frequency_table_nb expects and simply returns the ipywidgets.VBox produced by that helper.

### `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.WidgetFrequencyTableSmall.render` · *method*

## Summary:
Returns an ipywidgets VBox representing the compact frequency table by rendering the stored rows; it does not mutate the object's content.

## Description:
This method is the widget-flavour implementation of the FrequencyTableSmall rendering contract. It is typically called by the presentation pipeline when converting a FrequencyTableSmall item into a notebook-oriented (ipywidgets) fragment as part of the report rendering lifecycle (the pipeline that iterates over presentation items and produces final output for a specific flavour — here, the "widget" / notebook flavour).

Known callers and context:
- The report/presentation pipeline or a widget-specific renderer that selects this concrete renderer for items whose item_type is "frequency_table_small".
- Invocation happens at the rendering stage: after data aggregation constructs a FrequencyTableSmall instance (with content["rows"] prepared), the pipeline calls this render() to obtain a widgets.VBox suitable for display in a Jupyter notebook.

Why this is a standalone method:
- Rendering notebook widgets requires ipywidgets-specific construction; separating it into a dedicated method (and delegating actual widget construction to frequency_table_nb) isolates widget creation from the data model and from other output flavours (HTML, JSON, etc.). This promotes reuse and testability of the widget-specific rendering logic.

## Args:
- None (implicit dependency: uses self.content set by FrequencyTableSmall)

## Returns:
- widgets.VBox
    - A vertical container (ipywidgets.VBox) produced by frequency_table_nb when passed the stored rows (self.content["rows"]).
    - Practical contract: the returned VBox contains one widgets.HBox per frequency-row dictionary in the first sublist of rows (i.e., rows[0]) as described by frequency_table_nb.
    - Edge-case returns:
        - If rows[0] is empty, an empty VBox (no children) is returned by frequency_table_nb.
        - If widget construction fails, exceptions from ipywidgets (ValueError/TypeError) will propagate instead of returning a VBox.

## Raises:
- KeyError: if self.content does not contain the "rows" key (accessing self.content["rows"]).
- IndexError: can be raised indirectly by frequency_table_nb when rows is an empty list or missing the expected first element (frequency_table_nb accesses rows[0]).
- TypeError: if self.content["rows"] is not subscriptable as expected or row items are not mapping-like; such errors may arise in frequency_table_nb and propagate.
- Any widget-construction exceptions (ValueError, TypeError) raised by ipywidgets.FloatProgress or widgets.Label are propagated unchanged.

## State Changes:
- Attributes READ:
    - self.content (specifically self.content["rows"])
- Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
- Preconditions:
    - The instance must adhere to FrequencyTableSmall invariants: self.content exists and contains keys "rows" and "redact".
    - self.content["rows"] must be a list-like object with at least one element (rows[0]) as required by frequency_table_nb.
    - Each element of rows[0] should be a dictionary containing keys: "label", "count", "n", and "extra_class" (see frequency_table_nb for exact expectations).
- Postconditions:
    - On success, returns an ipywidgets.VBox containing widget children corresponding to rows[0].
    - self.content remains unchanged.

## Side Effects:
- Creates ipywidgets objects (FloatProgress, Label, HBox, VBox) in memory. When the returned VBox is displayed in a Jupyter notebook, visual UI elements will be produced.
- No I/O (file/network) or global state mutation occurs.

## Implementation notes for re-implementation:
- The method is a single responsibility wrapper: fetch self.content["rows"] and pass it to the notebook-specific renderer frequency_table_nb, returning its result unchanged.
- Do not attempt to validate or transform rows here — validation and the detailed rendering behavior live in frequency_table_nb; allow exceptions from that function to propagate so callers can handle them appropriately.

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.frequency_table_nb` · *function*

## Summary:
Render a list of frequency rows into an ipywidgets vertical box where each frequency row becomes a horizontal item containing a progress bar and a count label; special row classes ("missing" and "other") use different progress bar styles.

## Description:
This function converts the first group of frequency rows from a nested rows structure into a widgets.VBox suitable for display in Jupyter notebooks. Each entry in the first sub-list (rows[0]) is expected to be a dictionary describing a frequency bucket (label, count, total n, and an "extra_class" marker). The function iterates those dictionaries and constructs a widgets.HBox per row containing:
- an ipywidgets.FloatProgress configured with the row's count and total n (and a bar_style based on extra_class), and
- an ipywidgets.Label showing the raw count as text.

Known callers:
- This function itself has no callers in the provided file. It is intended to be used by presentation code that assembles notebook-specific (ipywidgets) renderings of frequency tables in the report generation pipeline (i.e., code paths that need a small inline frequency table widget for notebook/interactive flavours). Do not assume this function performs data aggregation — it only renders already-prepared row dictionaries.

Why this logic is extracted:
- Separation of concerns: rendering ipywidgets for notebook output is kept separate from data aggregation and formatting. This function enforces the responsibility boundary of converting a standardized row structure into a visual widget representation so rendering code can be re-used and tested independently.

## Args:
    rows (List[List[dict]]):
        - A nested list where the first element (rows[0]) is the list of frequency-row dictionaries to render.
        - Each frequency-row dictionary must contain the following keys:
            * "label": value convertible to str; used as the FloatProgress.description.
            * "count": numeric (int or float) indicating the item count; used as FloatProgress.value and shown in the Label.
            * "n": numeric (int or float) indicating the total (max) for the progress bar; used as FloatProgress.max.
            * "extra_class": str flag used to select the FloatProgress.bar_style. Expected values:
                - "missing"  -> bar_style="danger"
                - "other"    -> bar_style="info"
                - any other -> bar_style="" (default/empty)
        - Interdependencies:
            * "count" should be within [0, n] for the progress bar to represent a valid fraction. If count is outside this range the FloatProgress widget will reflect that value but visual semantics may be broken.
            * rows must be non-empty (function accesses rows[0]).

## Returns:
    widgets.VBox
        - A vertical box (ipywidgets.VBox) containing one widgets.HBox per dictionary in rows[0].
        - Each HBox contains, in order:
            1) widgets.FloatProgress configured with value=row["count"], min=0, max=row["n"], description=str(row["label"]), bar_style as determined by extra_class.
            2) widgets.Label containing the string representation of row["count"].
        - Edge cases:
            * If rows[0] is an empty list, an empty VBox (no children) is returned.
            * If some row fields are present but have unexpected types, a VBox will still be returned only if widget construction does not raise — otherwise an exception will propagate.

## Raises:
    IndexError:
        - If rows is an empty list or otherwise does not contain an element at index 0 (accessing rows[0] triggers this).
    KeyError:
        - If any expected key ("extra_class", "count", "n", or "label") is missing from a row dictionary and the function attempts to access it.
    TypeError:
        - If rows is not subscriptable as expected (e.g., None or non-sequence) or if row items are not mappings supporting string-key access.
    ValueError / widget-related exceptions:
        - ipywidgets.FloatProgress or widgets.Label construction may raise ValueError/TypeError if given non-numeric values where numeric types are required; such exceptions propagate.

## Constraints:
Preconditions:
    - rows must be a list-like object with at least one element.
    - rows[0] must be an iterable of dictionaries with the keys "label", "count", "n", and "extra_class".
    - row["n"] should be numeric and non-negative (recommended) because it is used as FloatProgress.max.
Postconditions:
    - The returned VBox contains exactly len(rows[0]) children when rows[0] is an iterable of that many dictionaries and no exception occurs during widget construction.
    - No mutation of the input rows structure is performed.

## Side Effects:
    - No I/O operations (no file, network, or stdout activity).
    - No global state is mutated.
    - The only side effect is creation of ipywidgets objects (in-memory widget instances) which, when returned and displayed in a Jupyter notebook context, will produce visual UI elements.

## Control Flow:
flowchart TD
    Start --> Read_rows0[Set fq_rows = rows[0]]
    Read_rows0 --> ForEachRow{For each row in fq_rows}
    ForEachRow --> CheckExtraClass{row["extra_class"] == "missing?"}
    CheckExtraClass -- yes --> CreateMissingHBox[Create HBox with FloatProgress(bar_style="danger") + Label]
    CheckExtraClass -- no --> CheckOther{row["extra_class"] == "other?"}
    CheckOther -- yes --> CreateOtherHBox[Create HBox with FloatProgress(bar_style="info") + Label]
    CheckOther -- no --> CreateDefaultHBox[Create HBox with FloatProgress(bar_style="") + Label]
    CreateMissingHBox --> AppendItem[append HBox to items]
    CreateOtherHBox --> AppendItem
    CreateDefaultHBox --> AppendItem
    AppendItem --> ForEachRow
    ForEachRow --> AfterLoop[after loop completes]
    AfterLoop --> ReturnVBox[return VBox(items)]
    ReturnVBox --> End

## Examples:
Usage scenario (described):
    - Input: Data aggregation step upstream produces a list-of-lists where the first sub-list contains dictionaries describing the top frequency values and special buckets:
        * e.g., rows[0] might represent the top 5 most frequent categories plus one "other" bucket and one "missing" bucket. Each dictionary carries "label","count","n","extra_class".
    - Call context: A notebook-oriented rendering pipeline calls this function when generating the "small frequency table" widget for an interactive report page.
    - Outcome: The returned widgets.VBox can be displayed in a Jupyter notebook cell (or embedded into a larger ipywidgets layout). Each row displays a horizontal progress bar whose fill corresponds to count/n and a textual label showing the raw count. The "missing" bucket is styled with the danger color and the "other" bucket with the info color to visually distinguish them.

Notes:
    - This function is purely presentational: perform validation and aggregation upstream if you require stricter guarantees (e.g., normalizing counts, clamping count to [0, n], or ensuring non-negative n).

