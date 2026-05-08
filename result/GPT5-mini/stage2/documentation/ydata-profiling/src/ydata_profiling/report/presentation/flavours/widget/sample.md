# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample` · *class*

## Summary:
A concrete Sample renderer that produces an ipywidgets vertical box containing a title (the sample name) and an Output widget showing the sample payload. Intended for use in Jupyter/IPython notebook environments.

## Description:
WidgetSample is a minimal, notebook-friendly renderer for Sample items. It reads the sample payload and presentation metadata placed into the inherited content dictionary (from Sample / Renderable) and returns an ipywidgets.VBox that can be displayed in a Jupyter notebook.

Typical instantiation: callers create a Sample payload (a pandas.DataFrame) and construct a WidgetSample instance via the inherited Sample constructor (see State and Lifecycle). The WidgetSample.render() method is then invoked to obtain an ipywidgets.VBox that contains:
- a header (HTML) with the sample name, taken from content["name"], and
- an ipywidgets.Output widget that captures the output of IPython.core.display.display(self.content["sample"]).

Motivation and responsibility boundary:
- Purpose: provide a thin adapter between the report data model (Sample) and notebook UI widgets.
- Responsibility: perform rendering into ipywidgets using IPython display facilities; it intentionally does not modify the Sample content or perform heavy formatting of the DataFrame.
- Not responsible for: creating the DataFrame, managing long-running resources, or falling back to non-notebook render targets. It assumes an IPython/Jupyter display environment.

## State:
Inherited attributes (this class does not add new persistent attributes):
- content: Dict[str, Any]
  - Required keys (used by WidgetSample.render()):
    - "sample": pandas.DataFrame (or any object displayable by IPython.display.display)
      - Expectation: a table-like payload suitable for display. No runtime type checking is performed by WidgetSample.
    - "name": str
      - Expectation: human-readable identifier used as the HTML header text. Sample.__init__ is expected to provide this.
  - Optional keys (present in Sample but not used by WidgetSample):
    - "caption": Optional[str] (ignored by this renderer)
    - "anchor_id", "classes": Optional metadata forwarded by Sample/Renderable (ignored by this renderer)
- item_type: str (inherited)
  - Value: "sample" (set by Sample). WidgetSample does not change this.

Class invariants:
- self.content is the same dict created by Sample.__init__ and must contain at least "sample" and "name" when render() is called.
- WidgetSample.render() does not mutate content.

Constraints and environment:
- Designed for Jupyter/IPython. The output capture and display behavior rely on IPython.core.display.display and ipywidgets.Output; rendering outside an IPython environment may not produce visible results.
- No defensive validation: missing or malformed keys will raise standard exceptions (see Raises).

## Lifecycle:
Creation:
- WidgetSample does not define its own constructor; it inherits Sample.__init__. To create an instance, call the Sample constructor signature (in the same module hierarchy) with:
  - name (str): required name stored as presentation metadata
  - sample (pandas.DataFrame): the DataFrame or displayable payload to show
  - caption (Optional[str]): optional caption (default None)
  - **kwargs: forwarded to Renderable/ItemRenderer (e.g., anchor_id, classes)
- After construction, the instance's content dict must contain content["sample"] and content["name"] for render() to succeed.

Usage:
- Primary operation: call instance.render() (no parameters).
- Typical sequence:
  1. Prepare a pandas.DataFrame containing the sample rows.
  2. Instantiate the Sample-derived renderer (WidgetSample) using the inherited constructor (pass name and sample).
  3. Call render() to obtain an ipywidgets.VBox.
  4. In a notebook cell, display the returned widgets.VBox (printing it has no effect; use IPython.display.display or let the notebook cell render the widget).
- Ordering: There is no required call ordering beyond providing valid content before render(); render() is idempotent and stateless with respect to instance fields.

Destruction / cleanup:
- No explicit cleanup required. The returned widgets are regular ipywidgets objects; their lifecycle follows standard widget ownership semantics in the notebook front-end.
- WidgetSample does not implement context-manager methods or close hooks.

## Method Map:
graph LR
  A[caller] --> B[WidgetSample.render()]
  B --> C[Create Output() widget]
  C --> D[with out: display(self.content["sample"])]
  D --> E[Create HTML header from content["name"]]
  E --> F[Return widgets.VBox([header_HTML, out])]

(Interpretation: render constructs an Output widget, captures the display(self.content["sample"]) into it, creates an HTML widget with the name, and returns a VBox containing both.)

## Raises:
- KeyError:
  - Trigger: content["sample"] or content["name"] missing from self.content. Since WidgetSample assumes Sample.__init__ populated content appropriately, calling render() on instances not constructed via the expected Sample constructor or instances whose content was mutated may raise KeyError.
- Any exceptions raised by IPython.core.display.display:
  - Trigger: if display(self.content["sample"]) fails (for instance, if the payload's display logic raises), that exception will propagate out of render().
- Import/runtime issues:
  - If ipywidgets or IPython are unavailable in the runtime environment, constructing widgets or calling display() will raise ImportError/RuntimeError upstream; WidgetSample assumes these packages are present at import/runtime.

## Example (usage pattern):
1. Prepare a small pandas DataFrame to act as a sample payload.
2. Construct the renderer by calling the inherited Sample constructor (pass a name string and the DataFrame as the sample argument). Optionally provide a caption or other Renderable kwargs.
3. Call render() on the resulting WidgetSample instance to obtain an ipywidgets.VBox object.
4. In an IPython/Jupyter notebook cell, render the returned VBox (for example, place it as the last expression of the cell or pass it to IPython.display.display) to show the header and the sample output captured inside the Output widget.

Notes:
- WidgetSample intentionally ignores the "caption" content key. If a caption must be displayed, wrap or extend WidgetSample to include content["caption"] in the rendered layout.
- Because WidgetSample relies on the notebook environment to render ipywidgets, prefer using it only in interactive report views (Jupyter notebooks, Jupyter Lab). If programmatic export (HTML file) is required, use or implement a renderer that serializes the sample to HTML rather than relying on ipywidgets.

### `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample.render` · *method*

## Summary:
Renders the sample as an IPython widget VBox containing a header with the sample name and an Output widget that captures the rich display of the sample payload.

## Description:
This method is called by presentation/rendering code when a Sample renderer for the "widget" flavour must produce an interactive notebook UI fragment. Typical callers include report builders, presentation factories, or orchestration code that assemble item renderers into a larger notebook report or dashboard. It is invoked at the rendering stage of the report pipeline—i.e., after a WidgetSample instance has been constructed and the content dict (see Sample) populated.

The logic is encapsulated in its own method because rendering for the widget flavour involves UI construction and IPython display side effects that are specific to this presentation flavour. Keeping this in a separate method isolates UI concerns from data-preparation logic and allows alternate flavours (HTML, JSON, etc.) to implement their own render() without duplicating widget-specific code.

## Args:
    None

## Returns:
    ipywidgets.widgets.VBox
        - A vertical box widget containing two children:
            1) widgets.HTML — an HTML header element showing the sample name (content["name"]) rendered as "<h4>{name}</h4>".
            2) ipywidgets.Output — an Output widget that has captured the result of calling IPython.display.display(...) on content["sample"].
        - Edge cases:
            - If content["name"] is not a string, it will be converted to string when injected into the HTML.
            - If display(content["sample"]) produced no visual representation, the Output widget will be empty.

## Raises:
    KeyError
        - Condition: self.content does not contain the required keys "sample" or "name". Accessing self.content["sample"] or self.content["name"] will raise KeyError.
    TypeError
        - Condition: self.content is not a mapping/subscriptable object (so self.content[...] fails).
    Any exception raised by IPython.core.display.display
        - Condition: the display call for content["sample"] triggers an exception (these are propagated — the method does not catch them).

## State Changes:
    Attributes READ:
        - self.content (reads keys "sample" and "name"): reads the sample payload and the display name from the instance content dict.
    Attributes WRITTEN:
        - None: the method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.content must be a mapping-like object (dict) containing:
            * "sample": the payload to display (typically a pandas.DataFrame or another IPython-displayable object).
            * "name": a human-readable name for the sample (typically a str).
        - The environment must be an IPython-compatible frontend (e.g., Jupyter notebook/lab) for display output to be meaningful.
    Postconditions:
        - Returns an ipywidgets.VBox whose children are an HTML header and an Output widget that has captured the display of the sample payload.
        - No mutation to self or self.content is performed by this call.

## Side Effects:
    - Creates ipywidgets objects (widgets.HTML, ipywidgets.Output, widgets.VBox) in memory.
    - Calls IPython.core.display.display(content["sample"]) inside the Output widget context; this emits display messages to the IPython output capture system — in a notebook frontend this results in the sample being rendered inside the returned Output widget.
    - No filesystem, network I/O, or external service calls are performed by this method.

