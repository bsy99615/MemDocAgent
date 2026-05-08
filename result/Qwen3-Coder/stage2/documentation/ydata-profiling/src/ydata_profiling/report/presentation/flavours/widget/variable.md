# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable` · *class*

## Summary:
WidgetVariable is a presentation class that renders variable content as a vertical box of ipywidgets, organizing top and bottom content sections for display in Jupyter environments.

## Description:
WidgetVariable is a concrete implementation of the Variable base class designed specifically for rendering variable information in Jupyter notebook environments using ipywidgets. It inherits from Variable and implements the render() method to create a vertical arrangement of widgets representing the variable's top and bottom content sections.

This class serves as a bridge between the abstract variable presentation model and concrete widget-based rendering, enabling interactive visualization of variable statistics and metadata within Jupyter notebooks. It's typically used during report generation when creating widget-based presentations.

## State:
- Inherits all attributes from Variable class:
  - item_type: str - Set to "variable" by parent constructor
  - content: dict - Contains structured data with:
    - "top": Renderable - Required content for the top section (rendered as first widget)
    - "bottom": Optional[Renderable] - Optional content for the bottom section (rendered as second widget if present)
    - "ignore": bool - Flag indicating whether this variable should be ignored during rendering (default: False)
  - name: str (inherited from Renderable) - Optional human-readable identifier
  - anchor_id: str (inherited from Renderable) - Optional HTML anchor identifier
  - classes: str (inherited from Renderable) - Optional CSS classes for styling

## Lifecycle:
- Creation: Instantiate with required top Renderable and optional bottom Renderable and ignore flag
- Usage: Call render() method to generate a widgets.VBox containing the rendered top and bottom content
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetVariable.render()] --> B[widgets.VBox]
    A --> C[self.content["top"].render()]
    A --> D{self.content["bottom"] is not None}
    D -->|True| E[self.content["bottom"].render()]
    D -->|False| F[Skip bottom rendering]
```

## Raises:
- AttributeError: May be raised if content keys are missing or if render() method is not properly implemented on top/bottom content objects
- TypeError: May occur if the rendered content from top/bottom sections doesn't conform to expected widget types

## Example:
```python
# Create top and bottom content as widgets
top_widget = widgets.HTML("<h3>Age Variable</h3>")
bottom_widget = widgets.Table(data=[["Mean", "25.5"], ["Std Dev", "5.2"]])

# Create WidgetVariable instance
variable = WidgetVariable(top=top_widget, bottom=bottom_widget)

# Render to ipywidgets VBox
widget_box = variable.render()  # Returns widgets.VBox with both widgets arranged vertically
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable.render` · *method*

## Summary:
Renders variable content as a vertical box layout containing top and optional bottom sections using ipywidgets.

## Description:
This method implements the rendering logic for WidgetVariable instances, organizing the variable's top and bottom content sections into a vertical box layout (VBox) suitable for Jupyter notebook environments. The method is called during the report generation pipeline when widget-based presentations are required.

The render method follows a standard pattern where it first renders the required top content, then conditionally adds the bottom content if it exists. This approach allows for flexible variable presentation where bottom sections are optional.

## Args:
    None

## Returns:
    widgets.VBox: A VBox widget containing the rendered top content and optionally the rendered bottom content as child widgets.

## Raises:
    AttributeError: If self.content["top"] or self.content["bottom"] do not have a render method, or if self.content is not properly initialized.
    TypeError: If the rendered content from top or bottom sections is not compatible with VBox children requirements.

## State Changes:
    Attributes READ:
    - self.content: Dictionary containing "top" and "bottom" keys with Renderable objects
    - self.content["top"]: Renderable object for the top section
    - self.content["bottom"]: Optional Renderable object for the bottom section (may be None)

    Attributes WRITTEN:
    - None: This method does not modify any instance attributes

## Constraints:
    Preconditions:
    - self.content must be a dictionary with "top" key containing a valid Renderable instance
    - self.content["top"] must have a render() method that returns a valid widget
    - self.content["bottom"] (if present) must be either None or a valid Renderable instance with a render() method

    Postconditions:
    - Returns a widgets.VBox instance containing rendered content
    - The VBox contains at least the top section content
    - If bottom content exists, it is appended as a second child to the VBox

## Side Effects:
    None: This method does not perform any I/O operations or external service calls. It only creates and returns widget objects.

