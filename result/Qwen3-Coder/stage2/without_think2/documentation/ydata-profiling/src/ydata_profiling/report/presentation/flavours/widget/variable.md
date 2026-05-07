# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable` · *class*

## Summary:
WidgetVariable is a concrete implementation of the Variable class that renders variable content as a vertical box widget in Jupyter environments.

## Description:
WidgetVariable serves as a specialized renderer for variable components in the ydata-profiling report system, specifically designed for interactive Jupyter notebook environments. It inherits from the base Variable class and implements the render() method to produce a vertical box layout (VBox) containing the top and optional bottom content sections. This class enables the visualization of variable information in a structured, widget-based format that integrates seamlessly with Jupyter's interactive capabilities.

The class is typically instantiated by report generation logic when creating widget-based presentations of variable data. It follows the standard pattern of variable content organization with distinct top and bottom sections, making it suitable for displaying variable metadata and statistics in an organized manner.

## State:
- Inherits all state from Variable class including:
  - item_type: str - Set to "variable" by constructor
  - content: dict - Dictionary containing "top" and "bottom" keys with Renderable objects
  - name: Optional[str] - Human-readable identifier for the variable
  - anchor_id: Optional[str] - Unique identifier for HTML anchors
  - classes: Optional[str] - CSS classes for styling
- Additional state:
  - self.content["top"]: Renderable - Required field representing the primary content section
  - self.content["bottom"]: Optional[Renderable] - Optional field representing secondary content section, can be None

## Lifecycle:
- Creation: Instantiate with required `top` parameter and optional `bottom` and `ignore` parameters inherited from Variable parent class
- Usage: Call `render()` method to generate a widgets.VBox containing the rendered top and bottom content elements
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetVariable.render] --> B[content["top"].render()]
    B --> C[widgets.VBox construction]
    A --> D[content["bottom"].render()]
    D --> C
```

## Raises:
- AttributeError: If self.content["top"] or self.content["bottom"] do not have a render method
- TypeError: If self.content["top"] or self.content["bottom"] are not compatible with the render() interface

## Example:
```python
# Create top content (e.g., text describing the variable)
top_content = Text("Variable Name: age")

# Create bottom content (e.g., statistical table)
bottom_content = Table([["Mean", "25.5"], ["Std Dev", "5.2"]])

# Create WidgetVariable instance
widget_variable = WidgetVariable(top=top_content, bottom=bottom_content)

# Render to widget
widget = widget_variable.render()

# The result is a widgets.VBox containing both content sections stacked vertically
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable.render` · *method*

## Summary:
Renders a widget-based variable presentation by combining top and optional bottom content elements into a vertical box layout.

## Description:
This method constructs a vertical widget layout (VBox) containing the rendered top content and, optionally, the rendered bottom content. It serves as the primary rendering entry point for widget-based variable presentations in the ydata-profiling report system. The method follows the standard rendering pattern where content sections are rendered individually and assembled into a composite widget.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget containing the rendered top and bottom content elements.

## Raises:
    AttributeError: If self.content["top"] or self.content["bottom"] do not have a render method.
    TypeError: If self.content["top"] or self.content["bottom"] are not compatible with the render() interface.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary-like object with "top" and "bottom" keys
    - self.content["top"] must be an object with a render() method
    - self.content["bottom"] must either be None or an object with a render() method
    Postconditions: 
    - Returns a widgets.VBox instance containing rendered content
    - The VBox contains at least the top content element

## Side Effects:
    None

