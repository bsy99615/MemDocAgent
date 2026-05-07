# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable` · *class*

## Summary:
A concrete renderer that produces an ipywidgets.VBox for a correlation-table item: it renders the item's name as an <h4> heading and captures a visual representation of the correlation matrix inside an ipywidgets.Output widget.

## Description:
WidgetCorrelationTable is the "widget" flavour renderer for correlation-table items. It is a thin subclass of CorrelationTable that implements the render() method to produce interactive Jupyter-compatible widgets (ipywidgets + IPython display) for inclusion in notebook-based reports or dashboards.

When to use:
- Use this class when you want the correlation matrix displayed inline in a Jupyter notebook or lab environment where ipywidgets and IPython display semantics are available.
- Typical callers are report assembly or rendering code that receives an item (or creates one) and dispatches to the appropriate renderer based on item_type == "correlation_table". The renderer is instantiated (or the subclass instance is created) and render() is invoked to obtain a widgets.VBox that can be placed into the notebook output.

Motivation / Responsibility:
- Encapsulates widget-specific display logic (Output capture and HTML heading) so higher-level render dispatchers remain flavour-agnostic.
- Keeps all IPython/ipwidgets usage confined to the widget-flavour renderer.

## State:
This class does not introduce new persistent attributes beyond those inherited from CorrelationTable / ItemRenderer / Renderable. It reads state from inherited attributes at render time.

Inherited / Read attributes:
- content : dict
  - Required keys accessed by render():
    * "correlation_matrix" (any object with an IPython display representation; typically a pandas.DataFrame)
      - Type: normally pandas.DataFrame (not enforced by this class)
      - Usage: passed to IPython.core.display.display(...) inside the Output context to capture the visual representation
    * "name" (string or object convertible to str)
      - Type: str-like
      - Usage: formatted into an HTML heading: "<h4>{name}</h4>"

Class invariants:
- The instance must have a content mapping with keys "correlation_matrix" and "name" at the time render() is called; otherwise render() will raise KeyError.
- No internal mutation: render() does not modify self or content.

## Lifecycle:
Creation:
- WidgetCorrelationTable inherits CorrelationTable.__init__ and does not override __init__. Instantiate it using the same constructor signature as CorrelationTable:
  - Required:
    * name: str
    * correlation_matrix: typically a pandas.DataFrame
  - Optional:
    * Any additional kwargs accepted by the parent ItemRenderer / Renderable classes (commonly anchor_id, classes).
- Example constructor shape (conceptual): WidgetCorrelationTable(name: str, correlation_matrix: pd.DataFrame, **kwargs)

Usage:
1. Instantiate (as above) or obtain an instance from a factory/dispatcher that constructs correlation-table renderers.
2. Call render() to obtain an ipywidgets.VBox representing the item:
   - render() behavior:
     a. Create an ipywidgets.Output() instance and enter its context manager.
     b. Call IPython.core.display.display(self.content["correlation_matrix"]) so the matrix's rich representation is captured into the Output widget.
     c. Create an ipywidgets.HTML widget with "<h4>{self.content['name']}</h4>".
     d. Return widgets.VBox([name_html_widget, output_widget]).
3. Insert the returned VBox into the Jupyter display area (e.g., return it from a cell, display it inside another ipywidgets container, or add it to a dashboard).

Sequencing and constraints:
- render() may be called multiple times; each call constructs fresh widget instances and captures display output anew.
- The runtime must provide IPython and ipywidgets for meaningful output (typical environment: Jupyter notebook/lab). Outside that environment the widgets may still be constructed but will not display as expected.

Destruction / Cleanup:
- No explicit cleanup methods are provided. Widgets are normal Python objects and follow standard garbage collection when no longer referenced.
- If embedding into longer-lived applications, callers are responsible for keeping references to or disposing widget objects as required by the host application.

## Method Map:
graph TD
    A[render()] --> B[Output() created]
    B --> C[with out: display(content["correlation_matrix"])]
    A --> D[HTML widget created with "<h4>{content['name']}</h4>"]
    A --> E[VBox([HTML, Output]) returned]

(Interpretation: render() creates an Output, captures the display of the correlation matrix into it, creates an HTML heading, and composes both into a VBox which it returns.)

## Raises:
- KeyError
  - Trigger: If self.content does not contain "correlation_matrix" or "name", render() accesses self.content[...] and will raise KeyError.
- Exceptions from IPython.display.display
  - Trigger: If the object in content["correlation_matrix"] raises during its rich-display logic (custom display hook, broken __repr__, etc.), that exception will propagate from the display call.
- Exceptions from ipywidgets constructors
  - Trigger: If ipywidgets.Output() or ipywidgets.HTML(...) cannot be constructed due to environment or configuration issues, those exceptions are propagated.

## Example:
Create a widget renderer instance and obtain a VBox for display (conceptual; assumes `df` is a pandas.DataFrame and the environment is a Jupyter notebook):

1. Instantiate (constructor mirrors CorrelationTable):
   - widget_item = WidgetCorrelationTable(name="Correlation matrix", correlation_matrix=df)

2. Render to widgets:
   - vbox = widget_item.render()

3. Display in a notebook:
   - display(vbox)

Notes:
- Each call to render() returns new widget instances; keep a reference to vbox if you need to reuse or later remove it from a layout.
- If you create the instance in non-notebook environments, the widgets may be constructed but not rendered visually. Ensure ipywidgets and IPython display are available for intended behavior.

### `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable.render` · *method*

## Summary:
Constructs and returns an ipywidgets VBox containing a heading and an Output widget that captures and displays the correlation matrix held in the instance's content.

## Description:
This method is the widget-flavour renderer for a correlation-table item. It is intended to be called during the report rendering step when the "widget" presentation flavour is used (for example, by a renderer dispatcher that selects WidgetCorrelationTable for items whose item_type is "correlation_table"). Typical callers are higher-level report assembly or rendering code that iterates over prepared items and invokes their concrete render() implementations to obtain displayable widget objects.

This logic is separated into its own method because:
- It encapsulates widget-specific construction (ipywidgets Output and HTML) and the display semantics (capturing IPython output inside an Output widget).
- It keeps presentation details localized to the widget renderer subclass (WidgetCorrelationTable) rather than being mixed into generic rendering/dispatch logic.
- It allows easy substitution with other flavours (HTML, JSON) by implementing other renderers that produce different output types from the same item content.

## Args:
    None

## Returns:
    ipywidgets.VBox
        - A vertical box widget containing two children:
            1. An ipywidgets.HTML widget with the item's name rendered inside an <h4> element.
            2. An ipywidgets.Output widget that contains the result of calling IPython.display.display(...) on content["correlation_matrix"].
        - The returned VBox is a fully constructed widget hierarchy ready to be inserted into a Jupyter notebook cell output area or used inside other ipywidgets layouts.
        - Edge cases:
            - If content["name"] exists but is an empty string, the HTML header will be empty but still present.
            - If content["correlation_matrix"] is present but has no printable representation, the Output widget may appear empty.

## Raises:
    KeyError
        - If self.content does not contain the key "correlation_matrix" or "name", attempting to access self.content["correlation_matrix"] or self.content["name"] will raise KeyError.
    Any exception raised by IPython.display.display or widget constructors
        - If the object stored in content["correlation_matrix"] raises during its display logic (for example, an object with a broken __repr__ or custom display hook), that exception will propagate.
        - If ipywidgets cannot construct Output or HTML widgets due to environment issues, corresponding exceptions from ipywidgets will propagate.

## State Changes:
    Attributes READ:
        - self.content (reads self.content["correlation_matrix"] and self.content["name"])
    Attributes WRITTEN:
        - None (the method does not modify self or other external objects; it constructs and returns new widget instances)

## Constraints:
    Preconditions:
        - self.content must be a mapping (dict-like) that contains:
            * "correlation_matrix": typically a pandas.DataFrame (or any object with an IPython display representation)
            * "name": a string or string-convertible value used as the heading text
        - IPython display machinery and ipywidgets must be available in the runtime for meaningful visual output (typical environment: Jupyter notebook/lab).
    Postconditions:
        - The returned object is an ipywidgets.VBox with child 0 being an HTML widget containing "<h4>{name}</h4>" and child 1 being an Output widget that has captured the displayed representation of content["correlation_matrix"].
        - No mutation has been performed on self; the instance state remains unchanged.

## Side Effects:
    - Creates two ipywidgets objects (HTML and Output) and composes them into a VBox; these widgets exist outside self and are returned to the caller.
    - Calls IPython.core.display.display(...) inside the context manager of the Output widget; this causes the visual representation of content["correlation_matrix"] to be rendered into the Output widget (i.e., it captures display output rather than printing to the notebook's main output stream).
    - No external I/O (network, filesystem) is performed by this method; side effects are limited to widget construction and in-memory display rendering.

