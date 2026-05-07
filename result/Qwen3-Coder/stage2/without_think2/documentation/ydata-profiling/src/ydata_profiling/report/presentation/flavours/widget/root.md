# `root.py`

## `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot` · *class*

## Summary:
WidgetRoot is a concrete implementation of the Root class that renders report components as ipywidgets.VBox containers.

## Description:
WidgetRoot serves as the widget-based presentation layer for ydata-profiling reports. It extends the abstract Root class to provide a concrete implementation of the render() method that produces a vertical box layout containing the report's body and footer components. This class is specifically designed for environments where interactive Jupyter widgets are supported, such as Jupyter notebooks.

The motivation for this distinct abstraction is to separate the conceptual report structure (handled by Root) from its widget-specific rendering implementation. WidgetRoot ensures that report components are properly arranged in a vertical stack using ipywidgets.VBox, maintaining the semantic structure while providing the appropriate visual presentation for widget-based interfaces.

## State:
- Inherits all state from Root class including:
  - item_type: str - Set to "report" 
  - content: dict - Contains "body", "footer", and "style" keys with respective renderable components
  - name: str - Optional human-readable identifier
  - anchor_id: str - Optional unique identifier for HTML anchors  
  - classes: str - Optional CSS classes for styling

## Lifecycle:
- Creation: Instantiated with the same parameters as Root (name, body, footer, style, and optional metadata). The constructor inherits from Root and sets up the content structure.
- Usage: Called during report generation when widget-based rendering is required. The render() method is invoked to produce a widgets.VBox containing the rendered body and footer components.
- Destruction: No special cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[WidgetRoot.render] --> B[body.render()]
    A --> C[footer.render()]
    B --> D[widgets.VBox]
    C --> D
    D --> E[Return VBox]
```

## Raises:
- None explicitly raised by WidgetRoot's render() method
- However, underlying render() calls on body and footer components may raise exceptions if those components are improperly configured

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.core.renderable import Renderable
from ydata_profiling.report.presentation.flavours.widget.root import WidgetRoot

# Create report components
style = Style()
body = Renderable({"content": "Main report content"})
footer = Renderable({"content": "Report footer"})

# Create widget-based root container
root = WidgetRoot(
    name="My Report",
    body=body,
    footer=footer,
    style=style
)

# Render to widget
widget = root.render()
# widget is now a widgets.VBox containing the body and footer
```

### `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot.render` · *method*

## Summary:
Renders the widget-based report structure by combining body and footer components into a vertical box layout.

## Description:
This method implements the rendering logic for the WidgetRoot class, which is responsible for creating a widget-based representation of a report. It takes the body and footer components stored in the content dictionary and renders them using their respective render methods, then combines them into a vertical box layout using ipywidgets.VBox.

The method is called during the report generation pipeline when a widget-based visualization of the complete report is required. It serves as the concrete implementation of the abstract render() method inherited from Root, providing the specific widget rendering behavior for this presentation flavour.

## Args:
    **kwargs: Arbitrary keyword arguments that are passed through to the underlying widget rendering operations (though not directly consumed by this method)

## Returns:
    widgets.VBox: A vertical box widget containing the rendered body and footer components stacked vertically

## Raises:
    None explicitly raised by this method, though underlying render() calls on body and footer components may raise exceptions

## State Changes:
    Attributes READ: self.content["body"], self.content["footer"]
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain both "body" and "footer" keys with valid renderable components
    - Both body and footer components must have working render() methods that return compatible widget types
    - The method assumes the presence of ipywidgets module for VBox creation
    
    Postconditions:
    - Returns a widgets.VBox instance containing the properly rendered components
    - The returned widget maintains the vertical stacking order of body followed by footer

## Side Effects:
    I/O: Creates ipywidgets.VBox instance and calls render() methods on child components
    External service calls: None
    Mutations to objects outside self: None

