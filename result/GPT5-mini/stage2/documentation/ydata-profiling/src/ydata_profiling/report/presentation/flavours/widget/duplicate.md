# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate` · *class*

## Summary:
A presentation-flavour renderer that converts a Duplicate presentation item into an ipywidgets.VBox containing a heading and captured display output for the duplicated rows.

## Description:
WidgetDuplicate is the widget (ipywidgets/IPython) flavour implementation for presenting duplicate-row results inside an interactive Jupyter-like environment. It exists to separate widget-specific UI composition from the data-carrying Duplicate item: given an instance whose content contains the duplicate payload and a display name, WidgetDuplicate.render() produces an ipywidgets.VBox containing (1) an HTML header and (2) an Output widget that captured the IPython display of the duplicate object (commonly a pandas.DataFrame).

Typical callers / instantiation contexts:
- The interactive report renderer or widget-flavour renderer dispatcher that converts presentation items into ipywidgets for insertion into a notebook UI.
- A renderer factory or dashboard builder that needs to include duplicate-row results as part of a larger ipywidgets layout.

Motivation and responsibility boundary:
- Responsibility: produce a self-contained ipywidgets.VBox for a duplicate presentation item using IPython.display for any rich representation.
- Boundary: does not detect duplicates or mutate the Duplicate/WidgetDuplicate instance. It only reads the presentation content and composes widgets; other flavours (HTML, JSON) should be implemented in other renderers.

## State:
- Inherited attributes (from Duplicate / ItemRenderer):
  - content (dict)
    - Expected keys used by this class:
      - "duplicate": Any IPython-displayable object (commonly a pandas.DataFrame). Type: object — typically pandas.DataFrame.
      - "name": str — a short label or title to show in the header. Type: str.
    - Notes/constraints:
      - WidgetDuplicate.render() directly subscripts self.content for both keys. Both keys must be present and subscriptable; otherwise a KeyError or TypeError will be raised.
      - The class does not validate types at construction time; callers must ensure the values are appropriate for display.
  - item_type (str)
    - Inherited from Duplicate (value "duplicate"). This class does not modify item_type.
  - Any other attributes available on the instance are not read or written by WidgetDuplicate.

Class invariants:
- The instance must provide a mapping-like self.content with at least the keys "duplicate" and "name".
- WidgetDuplicate does not change instance state; self.content remains unchanged after render().

## Lifecycle:
Creation:
- Instantiate via the same mechanism that constructs Duplicate-derived presentation items (e.g., the Duplicate constructor or a factory that returns a WidgetDuplicate wrapper). There are no additional constructor parameters on this subclass; it relies on the base-class initialization to populate self.content (containing "duplicate"/"name").

Usage:
1. Ensure the environment supports IPython display and ipywidgets (Jupyter notebook, JupyterLab, or similar).
2. Call widget_instance.render() to obtain an ipywidgets.VBox.
3. Insert the returned VBox into the notebook UI or combine it with other widgets in a layout.
- Typical sequencing: construct Duplicate-like item → pass to widget flavour renderer/dispatcher that selects WidgetDuplicate → call render() once per presentation instance.
- The render method can be called multiple times; each call creates new widget objects and does not reuse or mutate prior widgets on the instance.

Destruction / cleanup:
- No explicit cleanup method is provided. Widgets created by render() are managed by the ipywidgets machinery. If widgets must be programmatically closed, callers should call the ipywidgets.Widget.close() method on returned widgets (not provided by this class).
- There is no context manager or close() in WidgetDuplicate itself.

## Method Map:
flowchart LR
    A[WidgetDuplicate.render()] --> B[create ipywidgets.Output() as out]
    B --> C[with out: IPython.display.display(self.content["duplicate"])]
    A --> D[create ipywidgets.HTML header from self.content["name"]]
    C --> E[Output captures display result]
    D --> F[widgets.VBox([header, out]) returned]

(Invoked order: render() → create Output → capture display(...) → create HTML header → compose and return VBox)

## Raises:
- KeyError: If self.content is a mapping but missing "duplicate" or "name", attempting to access self.content["duplicate"] or self.content["name"] raises KeyError.
- TypeError: If self.content is None or not subscriptable (no __getitem__), subscripting will raise TypeError.
- Any exception propagated from IPython.display.display: if rendering the supplied "duplicate" object raises an exception, that exception will propagate out of render() (not caught by this method).
- RuntimeError / ImportError: If the runtime environment lacks IPython or ipywidgets, earlier imports or widget construction may fail (these are raised at import-time or widget construction time, not by render() itself).

## Example:
- Preconditions: running inside a Jupyter-like environment with ipywidgets available, and the WidgetDuplicate instance's self.content contains:
  - "duplicate": a pandas.DataFrame (or another IPython-displayable object)
  - "name": a short string title

- Typical sequence:
  1. Obtain or construct the Duplicate/WidgetDuplicate instance with appropriate content.
  2. Call vbox = widget_instance.render() to create the widget container.
  3. Place vbox into the notebook UI (e.g., returning it from the cell or displaying it inside a larger ipywidgets layout).
- Notes:
  - The header HTML is generated as "<h4>{name}</h4>" and will be interpreted as HTML by the ipywidgets.HTML widget; sanitize name beforehand if it may contain untrusted HTML.
  - If the duplicate object has a rich IPython representation (DataFrame, matplotlib figure, etc.), that representation is captured in the Output widget and displayed inside the returned VBox.

### `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate.render` · *method*

## Summary:
Renders the duplicate-item presentation as an ipywidgets.VBox containing a header (name) and an Output widget that displays the duplicate content, without mutating the WidgetDuplicate instance.

## Description:
This method is the widget-flavour renderer for a Duplicate presentation item. It is typically called by the notebook/interactive presentation pipeline or a renderer factory when building the widget-based report output for duplicate-row results. Typical callers include the widget-flavour renderer dispatcher or any code path that converts ItemRenderer-derived objects into ipywidgets for display in a Jupyter environment.

Lifecycle/context:
- Called after a Duplicate (or WidgetDuplicate) instance has been constructed and handed to the presentation layer that is producing a widget-based report.
- The pipeline expects render() to produce an ipywidgets widget (VBox) that can be inserted into the notebook UI or aggregated into a larger layout.

Why a separate method:
- Encapsulates widget-specific presentation logic (ipywidgets + IPython display call) for duplicates so the same Duplicate data container can be rendered in other flavours (HTML string, JSON) by different renderers without mixing UI code with the data container.
- Keeps presentation concerns (how to layout a header and capture display output) localized and testable.

## Args:
None.

## Returns:
ipywidgets.VBox
- The returned VBox contains two children in order:
  1. An ipywidgets.HTML widget whose value is a <h4> element containing self.content["name"] (rendered as HTML).
  2. An ipywidgets.Output widget that captured the result of calling IPython.display.display(self.content["duplicate"]) and thus shows the duplicate DataFrame or other displayable object.
- Edge cases:
  - If the display call produces no visible output for the provided object, the Output widget will be empty.
  - The method always returns a VBox instance (no None return path).

## Raises:
- KeyError: if self.content is a mapping but does not contain the "duplicate" or "name" keys (accessing self.content["duplicate"] or self.content["name"] will raise).
- TypeError: if self.content is not subscriptable (e.g., None or an object without __getitem__), subscripting will raise a TypeError.
- Any exception raised by IPython.display.display when attempting to render content may propagate (e.g., if the object supplied under "duplicate" has display logic that raises). These exceptions are not caught by this method.

## State Changes:
Attributes READ:
- self.content (reads the mapping)
- self.content["duplicate"] (reads the object to be displayed)
- self.content["name"] (reads the label used in the header)

Attributes WRITTEN:
- None. The method does not modify any self.<attr> fields on the instance.

## Constraints:
Preconditions:
- self.content must be a mapping-like object containing the keys "duplicate" and "name".
- self.content["duplicate"] should be an IPython-displayable object (commonly a pandas.DataFrame) to produce meaningful visual output when passed to display().
- The caller is expected to run this code in an environment with IPython display and ipywidgets available (e.g., a Jupyter notebook). While the code will construct widgets elsewhere, meaningful rendering requires such an environment.

Postconditions:
- A new ipywidgets.VBox instance is returned whose children are:
  - an ipywidgets.HTML containing "<h4>{self.content['name']}</h4>"
  - an ipywidgets.Output that captured whatever display() emitted for self.content["duplicate"]
- The WidgetDuplicate object remains unchanged (no attribute modifications).

## Side Effects:
- Uses IPython.display.display to render the duplicate object; however, because display() is called inside a with out: context manager, output is captured into the created Output widget rather than being sent directly to the global cell output.
- Allocates ipywidgets objects (Output, HTML, VBox) and may register them with the widget machinery. No network or filesystem I/O is performed.
- Security note: the header value is wrapped in widgets.HTML using raw string interpolation; if self.content["name"] contains HTML, it will be interpreted as HTML by the widget renderer (potential for accidental HTML rendering or injection if names are not sanitized).

