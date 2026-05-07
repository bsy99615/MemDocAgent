# `root.py`

## `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot` · *class*

## Summary:
WidgetRoot is a presentation layer class that renders report content using ipywidgets VBox layout.

## Description:
WidgetRoot is a concrete implementation of the Root class designed specifically for Jupyter notebook environments. It provides a widget-based interface for displaying report content by organizing the body and footer components within an ipywidgets.VBox container. This class is part of the widget presentation flavour system that enables interactive reporting in Jupyter notebooks.

The class is typically instantiated by the presentation framework when generating reports for Jupyter environments, and it serves as the root container for all report elements in widget-based presentations.

## State:
- content: dict containing "body" and "footer" keys, each mapping to Renderable objects
- The content dictionary is initialized by the parent Root class with body, footer, and style components
- All attributes are inherited from the parent Root class

## Lifecycle:
- Creation: Instantiated automatically by the presentation framework with body and footer Renderable objects
- Usage: Called via the render() method to generate a widgets.VBox widget containing the formatted report
- Destruction: No explicit cleanup required; relies on ipywidgets' garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetRoot.render] --> B[content["body"].render()]
    A --> C[content["footer"].render()]
    B --> D[widgets.VBox]
    C --> D
```

## Raises:
- None: The render method does not explicitly raise exceptions, though underlying render() calls on body and footer components may raise exceptions

## Example:
```python
# Typically created by the framework
root = WidgetRoot(name="report", body=body_component, footer=footer_component)

# Renders to ipywidgets.VBox
widget = root.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot.render` · *method*

## Summary:
Renders the widget-based report structure by combining the body and footer components into a vertical box layout.

## Description:
This method implements the rendering logic for the widget-based presentation flavour of the report. It creates a vertical box container (ipywidgets.VBox) that stacks the rendered body and footer components vertically. The method is part of the widget-specific implementation that differs from other presentation flavours like HTML or JSON.

The render method is called during the final presentation phase when the report needs to be displayed in a Jupyter notebook environment using ipywidgets. This approach allows for interactive widgets to be displayed inline.

## Args:
    **kwargs: Arbitrary keyword arguments that are passed through to the child render methods

## Returns:
    widgets.VBox: A vertical box widget containing the rendered body and footer components stacked vertically

## Raises:
    AttributeError: If self.content does not contain 'body' or 'footer' keys
    AttributeError: If either self.content["body"] or self.content["footer"] do not have a render method
    Exception: Any exceptions raised by the underlying render methods of body or footer components

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must contain both 'body' and 'footer' keys
    - Both self.content["body"] and self.content["footer"] must be Renderable objects with render() methods
    - The render() methods of body and footer must return compatible types that can be contained in a widgets.VBox
    
    Postconditions:
    - Returns a widgets.VBox instance
    - The returned VBox contains exactly two children: the rendered body and rendered footer

## Side Effects:
    None

