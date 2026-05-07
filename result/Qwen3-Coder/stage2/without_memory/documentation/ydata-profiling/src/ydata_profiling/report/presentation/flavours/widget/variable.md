# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable` · *class*

## Summary:
WidgetVariable is a presentation layer class that renders variable content as a vertical box of IPython widgets.

## Description:
WidgetVariable implements the rendering logic for variable content specifically for the widget presentation flavour. It extends the base Variable class to provide a concrete implementation of the render method that creates a vertical box layout (VBox) containing the rendered top content and optionally the rendered bottom content. This class is part of the ydata-profiling library's presentation layer, specifically designed for Jupyter notebook environments where interactive widgets are preferred.

## State:
- content: dict with keys "top" and "bottom", where:
  - "top" (Renderable): Required component that must be rendered first
  - "bottom" (Optional[Renderable]): Optional component that may be None
- The content dictionary is inherited from the parent Renderable class and contains the structured data for rendering
- All attributes are initialized through the parent Variable constructor

## Lifecycle:
- Creation: Instantiate with top Renderable and optional bottom Renderable parameters
- Usage: Call render() method to produce a widgets.VBox containing rendered content
- Destruction: No special cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetVariable.render()] --> B[content["top"].render()]
    A --> C{content["bottom"] is not None?}
    C -->|Yes| D[content["bottom"].render()]
    C -->|No| E[End]
    B --> F[widgets.VBox(items)]
    D --> F
```

## Raises:
- No explicit exceptions are raised by the WidgetVariable constructor

## Example:
```python
# Create a WidgetVariable with top and bottom content
top_widget = SomeRenderableClass(...)
bottom_widget = SomeRenderableClass(...)
widget_var = WidgetVariable(top=top_widget, bottom=bottom_widget)

# Render to IPython widgets VBox
vbox = widget_var.render()  # Returns widgets.VBox instance
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable.render` · *method*

## Summary:
Renders a variable presentation component as a vertical box widget containing top and optional bottom content.

## Description:
This method implements the rendering logic for WidgetVariable instances, creating a vertical box layout (VBox) that contains the rendered top content and optionally the rendered bottom content. It's part of the widget-based presentation flavour for ydata profiling reports.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box widget containing the rendered top content and, if present, the rendered bottom content.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content["top"] must be a Renderable instance with a render() method
    - self.content["bottom"] must either be None or a Renderable instance with a render() method
    - self.content must be a dictionary with "top" and "bottom" keys
    
    Postconditions:
    - Returns a widgets.VBox instance
    - The VBox contains at least the rendered top content
    - If bottom content exists, it's appended to the VBox items

## Side Effects:
    None

