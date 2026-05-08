# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse` · *class*

## Summary:
WidgetCollapse is a concrete Collapse renderer for IPython widgets that composes a toggle control (button) and a collapsible content item into an ipywidgets.VBox, wiring the toggle to show/hide the content. It supports two display modes: a "variable" collapse (hide/show the whole item) and a special "correlation" layout toggle (show/hide per-child detail columns and adjust grid columns).

## Description:
WidgetCollapse implements the Collapse.render contract for the ipywidgets frontend. It is intended to be used when building notebook (ipywidgets) reports that need collapsible sections.

Typical instantiation:
- Created indirectly by constructing a Collapse instance (using the Collapse constructor) whose content contains:
  - "button": a Toggle-like Renderable that exposes an attribute anchor_id and a render() method returning an ipywidgets container with a first child that emits .observe events for "value" changes.
  - "item": a Renderable whose render() method returns an ipywidgets widget (container) whose layout and children will be manipulated to show/hide content.

Known callers/factories:
- Any report builder or renderer that dispatches on Collapse and targets the ipywidgets flavour will call WidgetCollapse.render() to produce the interactive widget pair.
- Deserialization paths that restore a Collapse instance and then call render on the flavour-specific class.

Responsibility boundary:
- WidgetCollapse is strictly a presentation adapter: it converts the abstract Collapse.content entries into an ipywidgets.VBox and wires an event handler. It does not manage persistence, serialization, or the creation of the contained button/item objects.

## State:
Inherited state (from Collapse / Renderable):
- content (Dict[str, Any])
  - Required keys:
    - "button"
      - Expected type: Renderable that models a toggle control.
      - Required attributes/behavior:
        - attribute anchor_id (str) used to select the "correlation" mode when equal to "toggle-correlation-description".
        - method render() -> ipywidgets.Widget (a container), and the returned widget must have a children sequence where children[0] is an observable widget (supports .observe).
    - "item"
      - Expected type: Renderable representing the collapsible content.
      - Required attributes/behavior:
        - method render() -> ipywidgets.Widget, typically a container with layout and children attributes that are manipulated by WidgetCollapse.
- No new persistent attributes are set on WidgetCollapse instances; render() builds and wires ephemeral widget objects and returns a VBox.

Valid values and invariants:
- content must be a dict containing at least "button" and "item".
- button.anchor_id is expected to be a string; if it equals "toggle-correlation-description", WidgetCollapse treats the rendered item as a correlation grid and applies per-child layout changes.
- The widget returned by button.render() must have at least one child accessible at index 0 which supports .observe(event_handler, names=["value"]) and provides event dicts containing a "new" boolean value.
- The widget returned by item.render() must support:
  - a .layout attribute with mutable properties grid_template_columns and display
  - a .children iterable of child widgets; individual children may be instances of ipywidgets.Box. For Box children, the code expects that c.children[1] exists and has a .layout.display attribute.

Class invariants to preserve between calls:
- After render() returns, the returned VBox contains the toggle widget as first child and the item widget as second child.
- The toggle is observed for "value" changes; the handler must accept event dicts with key "new" that are truthy/falsey.

## Lifecycle:
Creation:
- No WidgetCollapse-specific constructor arguments; the instance is created via Collapse(button, item, **kwargs) and then the rendering flavour dispatch will use WidgetCollapse to render it.
- Required: content["button"] and content["item"], as described above.

Usage (typical sequence):
1. Call render() on the WidgetCollapse instance.
2. render() calls:
   - determine mode: if content["button"].anchor_id == "toggle-correlation-description" then mode = "correlation" else mode = "variable".
   - toggle_widget = content["button"].render()
   - item_widget = content["item"].render()
   - define a toggle_func(event_dict) that:
     - for "variable" mode: sets item_widget.layout.display to "" when event_dict["new"] is truthy, or "none" otherwise.
     - for "correlation" mode: when event_dict["new"] is truthy, sets each child c of item_widget to have c.layout.grid_template_columns = "50% 50%"; for children that are ipywidgets.Box, also set c.children[1].layout.display = "" (or "none" otherwise).
   - call toggle_func({"new": False}) once to initialize the collapsed state to hidden.
   - register observers: toggle_widget.children[0].observe(toggle_func, names=["value"])
   - return widgets.VBox([toggle_widget, item_widget])
3. In the notebook, user interactions with the toggle's observed child (typically a toggle button) will invoke toggle_func with event dicts produced by ipywidgets. The UI will be updated in-place.

Destruction / cleanup:
- WidgetCollapse does not implement explicit cleanup. The ipywidgets objects are returned to the caller and are subject to the caller's lifecycle. If the nested widgets require manual teardown, the caller must perform it.
- Observers registered on toggle_widget.children[0] persist as long as the widget exists. If the caller removes the widgets from the DOM and wants to avoid lingering callbacks, they should remove the observer or dispose the widget.

## Method Map:
mermaid
graph LR
    A[WidgetCollapse.render()] --> B[determine mode by button.anchor_id]
    B -->|correlation| C[define toggle_func for per-child Box handling and grid columns]
    B -->|variable| D[define toggle_func for whole-item display]
    C --> E[call toggle_func({"new": False}) to initialize hidden state]
    D --> E
    E --> F[register observer: toggle.children[0].observe(toggle_func, names=["value"])]
    F --> G[return widgets.VBox([toggle, item])]
    style A fill:#f9f,stroke:#333,stroke-width:1px

## Raises:
WidgetCollapse.render() does not explicitly raise custom exceptions, but the following runtime errors can occur given incorrect content or unexpected render() outputs:
- KeyError:
  - If content does not include "button" or "item".
- AttributeError:
  - If content["button"] or content["item"] lack expected attributes or methods (anchor_id, render()).
  - If the widget objects returned by render() do not expose the expected .children, .layout, or nested .layout properties.
- IndexError:
  - If toggle_widget.children is empty and access to children[0] is attempted.
- TypeError:
  - If an event dict supplied by ipywidgets does not contain the "new" key or its value is not truthy/falsey in the expected way.
Any of the above indicate a contract violation between WidgetCollapse and the provided button/item renderables.

## Example:
- Contextual usage (described in steps, not actual source code):
  1. Prepare a Toggle-like Renderable whose anchor_id equals "toggle-correlation-description" to enable the correlation mode, or any other anchor_id for the variable mode. Ensure its render() returns an ipywidgets container whose first child is an observable toggle widget.
  2. Prepare an item Renderable whose render() returns an ipywidgets container. In correlation mode, ensure the container's children include Box instances where the second sub-child (index 1) is the collapsible detail pane; the item.container should support changing layout.grid_template_columns.
  3. Create a Collapse instance with the prepared button and item.
  4. Call WidgetCollapse.render() via the flavour dispatch. The method returns an ipywidgets.VBox containing the toggle and the item.
  5. The render method initializes the display to collapsed (hidden) and wires the toggle so that user interactions show/hide content and adjust layouts as described above.
  6. If you remove the widget from view and wish to avoid retained callbacks, explicitly remove the observer or dispose the ipywidgets objects.

### `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse.render` · *method*

## Summary:
Compose and return an ipywidgets VBox containing a toggle control and its associated content item, initialize the content into the collapsed (hidden) state, and attach an observer so subsequent toggle changes show or hide the content (or adjust internal grid columns for correlation content).

## Description:
This method is called when a Collapse widget needs to produce its interactive representation for display (for example, during report assembly or when a parent widget renders children). Typical callers are higher-level rendering or layout routines that iterate over report components and call their render() methods to build the final UI.

The render logic is isolated because it must:
- obtain the already-constructed toggle and item widgets from self.content,
- decide between two distinct collapse behaviors (a "variable" collapse that hides the entire item, and a "correlation" collapse that hides specific subcomponents and adjusts grid columns),
- initialize the initial collapsed state synchronously before returning, and
- register an ipywidgets observer on the toggle to update layouts when the user changes the toggle.

Keeping this as a single method centralizes observer registration and layout mutation logic and prevents duplication across callers.

## Args:
None

## Returns:
widgets.VBox
- A VBox containing two children in order: [toggle_widget, item_widget].
- toggle_widget is the result of self.content["button"].render().
- item_widget is the result of self.content["item"].render().
- The returned VBox has its children already initialized to the collapsed state (see Postconditions). The method's return value is the fully assembled widget container suitable for display in an ipywidgets frontend.

## Raises:
These exceptions are not explicitly raised by the method but will be produced by Python when preconditions are violated:
- KeyError: if self.content does not contain the keys "button" and/or "item".
- AttributeError: if objects in self.content lack required attributes/methods:
  - If self.content["button"] has no attribute anchor_id.
  - If button.render() or item.render() is missing or does not return a widget-like object with the expected attributes (.children, .layout, .observe).
  - If toggle.children[0] exists but does not have an observe method.
  - If item or its children lack a .layout attribute or (for Box children) do not have at least two children such that children[1] has a .layout attribute.
- IndexError: if toggle.children is empty and the code attempts to access toggle.children[0].
- TypeError: if self.content is not a mapping or if render() returns objects that are not widget-like and subsequent attribute access fails.

## State Changes:
Attributes READ:
- self.content: reads self.content["button"].anchor_id and calls render() on both self.content["button"] and self.content["item"].

Attributes WRITTEN:
- The method does not assign to any self.<attr>; it does not mutate the Collapse instance itself.

Mutations performed on returned widgets (external-state modifications):
- For both modes, the method mutates layout properties on the widget(s) returned by item.render():
  - "variable" mode: sets item.layout.display to "" (visible) when toggled on or to "none" (hidden) when toggled off.
  - "correlation" mode:
    - When toggled on: sets display = "" and grid = "50% 50%".
    - When toggled off: sets display = "none" and grid = "".
    - For each child c in item.children:
      - If c is an instance of ipywidgets.Box, sets c.children[1].layout.display to display (i.e., hide/show the second child of the Box).
      - For every child c (regardless of type), sets c.layout.grid_template_columns to grid (may set to empty string when collapsed).
- Attaches an observer callback to toggle.children[0] that listens for changes to the "value" trait and applies the same layout mutations on subsequent toggles.

## Constraints:
Preconditions (what must be true before calling):
- self.content must be a mapping with:
  - "button": an object with attribute anchor_id (string) and method render() -> widget. The code checks specifically whether button.anchor_id == "toggle-correlation-description" to select the "correlation" behavior; any other anchor_id uses the "variable" behavior.
  - "item": an object with method render() -> widget that has a .layout attribute and a .children iterable; children may include ipywidgets.Box instances whose second child (children[1]) has a .layout attribute.
- The returned toggle widget must have a children sequence where children[0] is the interactive subwidget that exposes .observe(name=..., handler) and the "value" trait to observe.

Postconditions (what the caller can expect after the call):
- The method returns a widgets.VBox whose children are [toggle_widget, item_widget].
- The item widget (and, for "correlation", some of its Box children's second child and all children grid templates) are in the collapsed/hidden state immediately after return because toggle_func({"new": False}) is invoked prior to returning.
  - For "variable" mode: item.layout.display == "none".
  - For "correlation" mode: for Box children c, c.children[1].layout.display == "none"; for all children c, c.layout.grid_template_columns == "" (empty string).
- An observer is registered on toggle.children[0] to update these same properties when the toggle value changes.

## Side Effects:
- Mutates the layout attributes of widgets produced by item.render(); these changes are visible in the UI.
- Registers a persistent observer on toggle.children[0]; the callback remains active after the method returns and will execute whenever that widget's "value" trait changes, modifying the item widget's layouts.
- No file, network, or external system I/O is performed.

## Implementation Notes (re-implementation hints)
- Determine collapse mode by comparing self.content["button"].anchor_id == "toggle-correlation-description".
- Call button_widget = self.content["button"].render() and item_widget = self.content["item"].render().
- Create toggle_func(widg) callback that expects a dict-like event with key "new" (the new boolean value of the toggle).
  - For "variable" mode: set item_widget.layout.display to "" when widg["new"] is truthy, otherwise "none".
  - For "correlation" mode: if widg["new"] is truthy set display = "" and grid = "50% 50%"; otherwise display = "none" and grid = "". Then iterate over item_widget.children; for each child c:
    - If isinstance(c, Box): set c.children[1].layout.display = display.
    - Set c.layout.grid_template_columns = grid.
- Initialize the collapsed state by calling toggle_func({"new": False}) before attaching the observer.
- Attach the observer to the first child of the toggle widget: toggle_widget.children[0].observe(toggle_func, names=["value"]). Guard against empty children if you want to avoid IndexError (the original implementation does not guard).
- Return widgets.VBox([toggle_widget, item_widget]).

## Example (conceptual):
- A parent renderer calls collapse_component.render(), receives a VBox, and displays it in a notebook. The content is initially collapsed. Interacting with the toggle's visible control (toggle.children[0]) expands/collapses the item; for correlation-type collapses this also toggles internal child visibility and two-column layout.

