# `toggle_button.py`

## `src.ydata_profiling.report.presentation.flavours.widget.toggle_button.WidgetToggleButton` · *class*

## Summary:
Renders the semantic ToggleButton payload (content["text"]) as an ipywidgets.ToggleButton wrapped in an ipywidgets.HBox and returns that HBox for display in Jupyter notebook UIs.

## Description:
WidgetToggleButton is the concrete widget-based renderer for the abstract ToggleButton presentation item. It converts the ToggleButton.content payload (which must include a "text" key) into a visual ipywidgets.ToggleButton placed inside an HBox container. Use this class when producing interactive notebook (ipywidgets) output for items with item_type "toggle_button".

Typical callers:
- Presentation factories or report builders that map semantic presentation items to widget renderers.
- Render orchestration code that needs widget-output for toggle items in a Jupyter environment.

Motivation / Responsibility boundary:
- Responsibility: read the ToggleButton content and produce a simple widget representation (labelled ToggleButton + layout).
- Boundary: does not attach external event handlers, persist widget state outside the returned widget, or implement behavior beyond basic layout and labelling.

## State:
Inherited state (from ToggleButton):
- content: dict
  - Required key: "text" -> str (the label used for the toggle)
  - Expected shape: {"text": "<label>", ...optional metadata...}
  - Invariant: WidgetToggleButton reads content["text"] at render time; content must support __getitem__ with key "text".

WidgetToggleButton-specific state:
- No new persistent instance attributes are introduced. All widget objects are created locally inside render().

Constraints and notes:
- The implementation expects ipywidgets to be available at import time.
- content["text"] should ideally be a string. Non-string values will be coerced by ipywidgets to a string when used as the ToggleButton description.
- Layout property values (e.g., "fit-content", "100%") depend on frontend support; unsupported values may be ignored or rendered differently by the frontend, but the method itself does not raise on such mismatch.

## Lifecycle:
Creation:
- Instantiate via the ToggleButton constructor inherited from the base class:
  - Required: text (str) — e.g., WidgetToggleButton("Show details")
  - Optional kwargs forwarded to ItemRenderer/Renderable (e.g., name, anchor_id, classes)

Usage:
1. Instantiate:
   - tb = WidgetToggleButton("Show details")
2. Render:
   - box = tb.render()
   - box is an ipywidgets.HBox containing a single ipywidgets.ToggleButton
     - The ToggleButton's description equals tb.content["text"]
     - The ToggleButton's layout.width is set to "fit-content"
     - The HBox layout properties set are align_items, display, flex_flow, and width
3. Display:
   - Use display(box) in a Jupyter notebook to show the control.

Sequencing:
- There is no required ordering besides instantiating the object before calling render(). Each call to render() constructs new widget instances based on the current content dictionary.

Destruction / cleanup:
- No explicit cleanup is required by this class. Widgets are standard ipywidgets objects managed by the Jupyter widget machinery. If callers attach custom handlers or external resources, they are responsible for cleanup.

## Method Map:
graph TD
  render --> create_toggle[create widgets.ToggleButton(description=self.content["text"])]
  create_toggle --> set_toggle_layout[set toggle.layout.width = "fit-content"]
  set_toggle_layout --> create_box[create widgets.HBox([toggle])]
  create_box --> set_box_layouts[set toggle_box.layout.align_items/display/flex_flow/width]
  set_box_layouts --> return_box[return toggle_box]

(Flow: render reads content["text"], creates a ToggleButton, configures its layout, wraps it in an HBox, configures the HBox layout, and returns the HBox.)

## Raises:
- KeyError: If self.content lacks the "text" key, accessing self.content["text"] raises KeyError.
- AttributeError / TypeError: If self.content does not support item access (i.e., is not dict-like) attempting self.content["text"] may raise AttributeError or TypeError.
- ImportError: If ipywidgets is not installed, importing widgets will fail at module import time (before render() is called). This is an environmental failure, not raised by render().
- Note: Setting layout values will not raise exceptions in this method; however, the frontend may ignore or render them differently if it does not support specific CSS/value combinations.

## Example:
1) Basic creation and display:
   tb = WidgetToggleButton("Show details")
   box = tb.render()
   display(box)  # in a Jupyter notebook, shows a ToggleButton labeled "Show details"

2) Modify label before rendering:
   tb = WidgetToggleButton("Old")
   tb.content["text"] = "New label"
   display(tb.render())

3) Defensive usage if content may be incomplete:
   if isinstance(tb.content, dict) and "text" in tb.content:
       display(tb.render())
   else:
       tb.content["text"] = "Toggle"
       display(tb.render())

Implementation checklist (to reimplement render):
- Read label = self.content["text"]
- Create toggle = widgets.ToggleButton(description=label)
- Set toggle.layout.width = "fit-content"
- Create toggle_box = widgets.HBox([toggle])
- Set toggle_box.layout.align_items = "flex-end"
- Set toggle_box.layout.display = "flex"
- Set toggle_box.layout.flex_flow = "column"
- Set toggle_box.layout.width = "100%"
- Return toggle_box

### `src.ydata_profiling.report.presentation.flavours.widget.toggle_button.WidgetToggleButton.render` · *method*

## Summary:
Create and return an ipywidgets HBox that contains a labeled toggle control whose label is taken from the instance payload; this does not modify the instance state.

## Description:
This method builds a small widget fragment for the "widget" flavour of a toggle-button presentation item. It is intended to be called during the presentation rendering stage when a concrete widget-based representation is required (for example, by a report renderer or a presentation factory that converts ItemRenderer instances to ipywidgets components). Known callers include higher-level rendering code that iterates presentation items and calls the concrete renderer's render() to obtain a UI fragment.

The logic is factored into its own method because:
- It implements the widget-specific layout and instantiation details for the ToggleButton semantic item. Keeping widget construction here separates UI concerns from generic item payload management (handled by ToggleButton / ItemRenderer).
- Subclasses or flavour-specific renderers can provide alternative render implementations (HTML, JSON, or other UI frameworks) by overriding render() without changing payload semantics.

## Args:
    None

## Returns:
    widgets.HBox
    - A newly-created ipywidgets HBox containing a single widgets.ToggleButton.
    - The returned HBox has the following layout properties set:
        - align_items: "flex-end"
        - display: "flex"
        - flex_flow: "column"
        - width: "100%"
    - The contained ToggleButton has:
        - description set to the value of self.content["text"]
        - layout.width set to "fit-content"

## Raises:
    KeyError
    - If self.content does not contain the key "text", the attempt to read self.content["text"] raises KeyError.

    (No other exceptions are raised explicitly in this code. Errors originating from ipywidgets constructors or layout assignment will propagate as raised by those libraries.)

## State Changes:
    Attributes READ:
        - self.content (specifically self.content["text"]) — used to obtain the label for the ToggleButton.

    Attributes WRITTEN:
        - None. The method does not modify self or any attributes on self.

## Constraints:
    Preconditions:
        - The instance must have a content mapping with the key "text" (i.e., "text" in self.content).
        - The value at self.content["text"] should be a human-readable label (typically a str). While the code does not perform type validation, providing a non-string may lead to unexpected widget label formatting as determined by ipywidgets.

    Postconditions:
        - The instance is unchanged (no mutation to self).
        - A widgets.HBox object is returned that contains one widgets.ToggleButton whose description equals the original content["text"] value and whose layout and the HBox layout are set as described in Returns.

## Side Effects:
    - Constructs ipywidgets objects (widgets.ToggleButton and widgets.HBox). These are in-memory UI objects and may trigger front-end rendering when displayed by an ipywidgets-compatible environment (e.g., Jupyter notebook). The method itself does not call display() or perform I/O.
    - No external services, files, or network resources are accessed.

