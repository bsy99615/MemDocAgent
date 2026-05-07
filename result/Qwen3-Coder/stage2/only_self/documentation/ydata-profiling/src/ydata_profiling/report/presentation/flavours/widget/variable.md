# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable` · *class*

## Summary:
WidgetVariable is a presentation layer class that renders variable content as an interactive IPython widget VBox container.

## Description:
WidgetVariable extends the base Variable class to provide a concrete implementation for rendering variable information using ipywidgets. It serves as a bridge between the abstract variable presentation interface and the concrete widget-based UI components. This class is specifically designed for use in Jupyter notebook environments where interactive widgets are supported.

The class is typically instantiated by report generation components that need to display variable data in a structured, widget-based format. It leverages the parent Variable's content structure (with top and optional bottom sections) and transforms it into a hierarchical widget layout.

## State:
- content: dict - Inherited from Variable parent class, contains "top" and "bottom" keys where:
  - top: Renderable - Required content for primary variable information displayed at the top
  - bottom: Optional[Renderable] - Optional secondary content displayed below the top section, can be None
- ignore: bool - Inherited from Variable parent class, flag indicating whether this variable should be ignored during processing, defaults to False
- item_type: str - Class attribute identifying this as a "variable" type item, inherited from ItemRenderer

## Lifecycle:
- Creation: Instantiate with a required top Renderable object and optional bottom Renderable and ignore flag, inheriting from Variable constructor
- Usage: Call render() method to generate a widgets.VBox widget containing the structured content
- Destruction: Inherits standard Python object lifecycle management

## Method Map:
```mermaid
graph TD
    A[WidgetVariable.render()] --> B[content["top"].render()]
    B --> C{content["bottom"] is not None?}
    C -->|Yes| D[content["bottom"].render()]
    C -->|No| E[End]
    D --> E
    E --> F[widgets.VBox(items)]
```

## Raises:
- None explicitly raised by __init__ (inherits from Variable)
- The render() method may raise exceptions from underlying render() calls on content items

## Example:
```python
# Create top content (assumed to be another widget-renderable)
top_content = Text("Age Variable")
bottom_content = Table([["Min", "Max"], [18, 85]])

# Create WidgetVariable instance
widget_variable = WidgetVariable(top_content, bottom_content, ignore=False)

# Render to ipywidgets.VBox
widget_container = widget_variable.render()

# The result is a VBox containing the top content and optionally bottom content
# widget_container is a widgets.VBox instance that can be displayed in Jupyter notebooks
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable.render` · *method*

## Summary:
Renders a widget-based variable presentation by combining top and optional bottom content sections into a vertical box layout.

## Description:
This method implements the rendering logic for WidgetVariable instances, creating a vertical arrangement of widget components. It takes the top content section and optionally includes the bottom content section, returning them as a single widgets.VBox container. This method is part of the widget-based presentation flavour for data profiling reports.

The render method is specifically designed to handle the widget rendering workflow for variable elements, ensuring proper hierarchical organization of content in Jupyter notebook environments. It's called during the report generation process when widget-based visualizations are required.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container holding the rendered top and bottom content sections as widget components.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing "top" key with a renderable object
    - self.content["top"] must have a render() method that returns a widget
    - self.content["bottom"] may be None or must have a render() method that returns a widget
    
    Postconditions:
    - Returns a widgets.VBox instance containing properly rendered widget components
    - The returned VBox maintains the hierarchical structure of top followed by bottom content

## Side Effects:
    None

