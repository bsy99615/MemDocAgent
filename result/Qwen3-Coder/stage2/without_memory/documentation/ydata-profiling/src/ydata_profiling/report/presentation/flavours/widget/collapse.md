# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse` · *class*

## Summary:
WidgetCollapse renders an interactive collapsible panel using ipywidgets, supporting both correlation and variable type collapses with dynamic UI updates.

## Description:
WidgetCollapse is a presentation layer component that transforms a collapsible structure into an interactive ipywidgets-based UI element. It's designed to be used in Jupyter notebook environments where interactive visualizations are needed. The component creates a toggle button that controls the visibility of associated content, with different behaviors for correlation vs variable type collapses.

This class serves as a concrete implementation of the abstract Collapse base class, specifically tailored for the widget presentation flavour. It enables users to interactively show/hide content sections in data profiling reports.

## State:
- content: dict containing "button" (ToggleButton instance) and "item" (Renderable instance) keys
- The button must have an anchor_id attribute that determines collapse type
- The item contains the content to be shown/hidden
- anchor_id of button determines whether collapse is "correlation" or "variable" type
- The button's anchor_id must be either "toggle-correlation-description" for correlation type or any other value for variable type

## Lifecycle:
- Creation: Instantiate with a ToggleButton and Renderable item
- Usage: Call render() method to generate ipywidgets.VBox containing the interactive collapse UI
- The render() method sets up event observers for interactive behavior using observe() method
- No explicit destruction needed as ipywidgets handle cleanup automatically

## Method Map:
```mermaid
graph TD
    A[WidgetCollapse.render()] --> B{button.anchor_id == "toggle-correlation-description"}
    B -->|True| C[Set collapse = "correlation"]
    B -->|False| D[Set collapse = "variable"]
    C --> E[toggle_func with grid layout implementation]
    D --> E
    E --> F[toggle_func({"new": False})]
    F --> G[toggle.children[0].observe(toggle_func)]
    G --> H[return widgets.VBox([toggle, item])]
```

## Raises:
- None explicitly raised by __init__ (inherits from Collapse)
- May raise exceptions from underlying ipywidgets operations during render()

## Example:
```python
from ydata_profiling.report.presentation.flavours.widget.collapse import WidgetCollapse
from ydata_profiling.report.presentation.core.toggle_button import ToggleButton
from ydata_profiling.report.presentation.flavours.widget.toggle_button import WidgetToggleButton

# Create a toggle button for correlation
toggle_button = ToggleButton("Show Correlation Details", anchor_id="toggle-correlation-description")

# Create content to be collapsed
content_item = SomeRenderableClass(...)

# Create the collapse widget
collapse_widget = WidgetCollapse(toggle_button, content_item)

# Render the widget
widget_container = collapse_widget.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.collapse.WidgetCollapse.render` · *method*

## Summary:
Renders a collapsible widget interface with toggle functionality that displays or hides content based on user interaction, with different behaviors for correlation vs variable collapses.

## Description:
This method creates a collapsible UI component consisting of a toggle button and associated content area. Based on the button's anchor_id attribute, it applies different styling behaviors when toggling visibility. It initializes the display state to collapsed and sets up event observers to handle user interactions.

The method distinguishes between two collapse types:
1. Correlation collapse: Applies grid layout styling to child elements when expanded
2. Variable collapse: Simple display toggling for the entire item

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container holding the toggle button and collapsible item

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content, self.content["button"].anchor_id
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain "button" and "item" keys with valid renderable objects
    - The button's anchor_id must be either "toggle-correlation-description" or another value
    - Both button and item must have valid render() methods that return appropriate widget objects
    
    Postconditions:
    - Returns a properly initialized widgets.VBox containing the rendered toggle and item
    - The toggle button is configured with an observer for state changes
    - The initial display state is set to collapsed (display="none")
    - For correlation collapses, grid layout properties are applied to child boxes
    - For variable collapses, simple display property is toggled

## Side Effects:
    - Configures event observers on the toggle button's children via observe() method
    - Modifies layout properties (display, grid_template_columns) of child widgets during runtime
    - Creates ipywidgets objects that will be displayed in Jupyter environments

