# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse` · *class*

## Summary:
WidgetCollapse is a concrete implementation of the Collapse class that renders collapsible UI components using ipywidgets for Jupyter notebook environments.

## Description:
The WidgetCollapse class provides a concrete implementation for creating collapsible sections in Jupyter notebooks using ipywidgets. It extends the abstract Collapse base class and implements the render method to generate interactive toggle buttons and collapsible content areas. This component is specifically designed for widget-based user interfaces where users can expand or collapse sections of content.

The class distinguishes between two types of collapses: "correlation" and "variable", each with different display behaviors when toggled. It leverages the ipywidgets library to create interactive UI elements that respond to user input through event observation.

## State:
- Inherits all state from Collapse parent class including:
  - content: Dictionary containing "button" (ToggleButton instance) and "item" (Renderable instance) components
  - item_type: String identifier set to "collapse" 
  - name: Optional identifier for the element
  - anchor_id: Optional anchor identifier for HTML anchors
  - classes: Optional CSS classes for styling

## Lifecycle:
- Creation: Instantiate with a content dictionary containing "button" and "item" keys, where button is a ToggleButton instance and item is a Renderable instance
- Usage: Call render() method to generate the ipywidgets.VBox containing the toggle button and collapsible item
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetCollapse.render()] --> B[content["button"].render()]
    A --> C[content["item"].render()]
    B --> D[toggle_func definition]
    C --> E[toggle_func definition]
    D --> F[toggle_func({"new": False})]
    E --> G[toggle.children[0].observe(toggle_func, names=["value"])]
    G --> H[widgets.VBox([toggle, item])]
```

## Raises:
- None explicitly raised by WidgetCollapse.__init__ (inherits from Collapse)

## Example:
```python
# Create a toggle button
toggle_button = ToggleButton(text="Show Details")

# Create a content item (some renderable component)
content_item = Text("This is collapsible content")

# Create a collapse component
collapse = WidgetCollapse({"button": toggle_button, "item": content_item})

# Render the widget for display in Jupyter
widget_output = collapse.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse.render` · *method*

## Summary:
Renders a collapsible widget interface with toggle functionality that displays or hides content based on user interaction.

## Description:
Generates a widget-based collapsible interface consisting of a toggle button and a collapsible content item. The method dynamically creates either a correlation-specific or variable-specific toggle behavior based on the button's anchor_id attribute. This method is responsible for setting up the interactive toggle functionality using ipywidgets event observers.

The render method is called during the widget presentation pipeline when converting a Collapse component into its visual representation. It handles two distinct collapse behaviors:
1. Correlation collapse: Adjusts grid layout properties when content items contain Box widgets
2. Variable collapse: Controls simple display visibility for basic content items

The method initializes the collapsed state (display = "none") and attaches event handlers to enable interactive toggling between expanded and collapsed states.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container holding the toggle button and collapsible content item, properly configured with event handlers for interactive toggling.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content, self.content["button"], self.content["item"], self.content["button"].anchor_id
    Attributes WRITTEN: None (method is read-only)

## Constraints:
    Preconditions:
    - self.content must contain both "button" and "item" keys
    - self.content["button"] must have an anchor_id attribute
    - Both self.content["button"] and self.content["item"] must have render() methods available
    - The button's render() method must return a widget with a children[0] element that supports value observation
    
    Postconditions:
    - Returns a properly initialized widgets.VBox with two children: toggle button and content item
    - The returned VBox has proper event observers attached for toggle functionality
    - The initial state is set to collapsed (display = "none")
    - The toggle functionality is fully operational for interactive use

## Side Effects:
    - Attaches event observers to the toggle button's value change events via observe() method
    - Modifies layout properties of child widgets during runtime through layout.display and layout.grid_template_columns
    - Creates ipywidgets objects (VBox, Box) which may trigger UI updates in Jupyter environments

