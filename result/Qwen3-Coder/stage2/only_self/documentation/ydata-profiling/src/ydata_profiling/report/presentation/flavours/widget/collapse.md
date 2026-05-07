# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse` · *class*

## Summary:
WidgetCollapse is a concrete implementation of the Collapse class that renders collapsible UI components using ipywidgets for interactive report presentations.

## Description:
WidgetCollapse implements the rendering logic for collapsible sections in Jupyter notebook environments using ipywidgets. It creates interactive toggle buttons that can expand or collapse content sections, supporting two distinct collapse modes: "correlation" and "variable". This component is specifically designed for the widget-based presentation flavour of the ydata profiling report system.

The class determines its behavior mode based on the anchor_id of the contained toggle button. When the anchor_id equals "toggle-correlation-description", it operates in correlation mode which affects grid layout of nested content. In variable mode, it simply toggles the display property of the entire item.

The class is typically instantiated when converting existing Renderable objects to collapsible components using the convert_to_class method from the parent class. It leverages the ipywidgets library to create interactive UI elements that respond to user input through event observation.

## State:
- Inherits all state from Collapse parent class including:
  - button: ToggleButton instance that controls the collapse state
  - item: Renderable instance containing the content that gets collapsed/expanded
  - content: Dictionary containing the button and item components
  - item_type: String identifier set to "collapse" that defines this component type
  - name: Optional string identifier for the component (inherited from Renderable)
  - anchor_id: Optional string for HTML anchor identification (inherited from Renderable)
  - classes: Optional CSS classes for styling (inherited from Renderable)
- Additional behavior determined by content["button"].anchor_id:
  - When anchor_id equals "toggle-correlation-description", operates in "correlation" mode
  - Otherwise operates in "variable" mode

## Lifecycle:
- Creation: Instantiate with a ToggleButton and Renderable object, typically through the convert_to_class method from the parent class
- Usage: The render() method is called during report generation to produce the ipywidgets VBox containing the toggle button and collapsible item
- Destruction: Inherits standard Python object lifecycle management; no special cleanup required

## Method Map:
```mermaid
graph TD
    A[WidgetCollapse.render()] --> B[self.content["button"].render()]
    B --> C[self.content["item"].render()]
    C --> D[Conditional logic for collapse type based on anchor_id]
    D --> E[Creates appropriate toggle_func closure for collapse type]
    E --> F[toggle_func({"new": False}) - Initialize state]
    F --> G[toggle.children[0].observe(toggle_func, names=["value"])]
    G --> H[Return widgets.VBox([toggle, item])
```

## Raises:
- No explicit exceptions raised by WidgetCollapse.__init__() as it inherits from Collapse
- The render() method may raise exceptions from underlying ipywidgets operations if invalid widget structures are encountered

## Example:
```python
# Create a toggle button with correlation anchor ID
toggle_btn = ToggleButton("Show Correlation Details", anchor_id="toggle-correlation-description")

# Create a content item (could be any Renderable)
content_item = Text("Correlation analysis results...")

# Create a collapse component (typically done via convert_to_class)
collapse = Collapse(toggle_btn, content_item)

# Render the widget-based collapsible component
widget_output = collapse.render()  # Returns widgets.VBox

# For variable mode, use a button without the correlation anchor ID
toggle_btn_var = ToggleButton("Show Variable Details")
collapse_var = Collapse(toggle_btn_var, content_item)
widget_output_var = collapse_var.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse.render` · *method*

## Summary:
Renders a collapsible widget interface with toggle functionality that displays or hides content based on user interaction.

## Description:
Creates a collapsible UI component consisting of a toggle button and a collapsible item. The method dynamically determines the collapse behavior based on the button's anchor_id and sets up event observers to handle toggle interactions. This method is responsible for constructing the visual representation of a collapsible section in the widget-based presentation layer.

The render method distinguishes between two collapse types: "correlation" and "variable". For correlation collapses, it manages grid layout adjustments for nested Box components, while for variable collapses, it simply toggles the display property of the item. The initial state is set to collapsed (hidden) when the widget is first rendered.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container holding the toggle button and collapsible item widgets, arranged in a stacked layout. The container has the toggle button as the first child and the collapsible item as the second child.

## Raises:
    None

## State Changes:
    Attributes READ: self.content["button"], self.content["item"]
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain both "button" and "item" keys
    - Both self.content["button"] and self.content["item"] must have valid render() methods
    - The button's anchor_id must be either "toggle-correlation-description" or another value for variable collapse behavior
    
    Postconditions:
    - Returns a widgets.VBox containing exactly two children: the toggle button and the collapsible item
    - The returned VBox has proper event observers attached to the toggle button
    - The initial state of the collapsible item is collapsed (display="none" or equivalent)
    - The toggle button is properly configured with an observer for value changes

## Side Effects:
    - Attaches event observers to the toggle button's value change events via observe() method
    - Modifies layout properties of child widgets during runtime when toggled
    - Creates and returns ipywidgets objects that will be rendered in the UI

