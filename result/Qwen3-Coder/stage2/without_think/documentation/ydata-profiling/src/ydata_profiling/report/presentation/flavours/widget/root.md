# `root.py`

## `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot` · *class*

## Summary:
WidgetRoot is a concrete implementation of the Root class that renders report presentations using ipywidgets VBox containers.

## Description:
WidgetRoot serves as the widget-based presentation layer for ydata-profiling reports, specifically designed to render complete profiling reports within Jupyter notebook environments using ipywidgets. It inherits from the abstract Root class and provides a concrete implementation of the render method that creates a vertical box layout containing the report body and footer components.

This class is typically instantiated automatically by the report generation pipeline and is not meant to be created directly by end-users. It bridges the gap between the abstract report structure defined by Root and the concrete widget-based rendering required for interactive notebook displays.

## State:
- Inherits all state from Root class including:
  - item_type: str - Set to "report" by constructor
  - content: dict - Contains "body" (Renderable), "footer" (Renderable), and "style" (Style) keys
  - name: str - Human-readable identifier for the report
  - anchor_id: str - Optional anchor identifier
  - classes: str - Optional CSS classes

## Lifecycle:
- Creation: Instantiated with the same parameters as Root (name, body, footer, style) - typically handled by report generation pipeline
- Usage: Called internally by report rendering systems; render() method returns a widgets.VBox containing body and footer widgets
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetRoot.render] --> B[widgets.VBox construction]
    B --> C[self.content["body"].render()]
    B --> D[self.content["footer"].render()]
    C --> E[Body widget rendering]
    D --> F[Footer widget rendering]
```

## Raises:
- No explicit exceptions raised by WidgetRoot.__init__
- May propagate exceptions from underlying render() calls on body/footer components

## Example:
```python
# WidgetRoot is typically created and used internally by the reporting system
# Example of how it would be used in a report generation context:

from ydata_profiling.report.presentation.flavours.widget.root import WidgetRoot
from ydata_profiling.report.presentation.core.html import HTML
from ydata_profiling.config import Style

# Create body and footer renderables (these would typically be created by the system)
body_content = HTML("Report Body Content")
footer_content = HTML("Report Footer")

# Create style configuration
style_config = Style(primary_colors=["#0000ff"])

# WidgetRoot would be instantiated internally by the report generation pipeline
# root_widget = WidgetRoot(
#     name="my_report",
#     body=body_content,
#     footer=footer_content,
#     style=style_config
# )

# To render the complete report:
# widget_output = root_widget.render()
# This would return a widgets.VBox containing the body and footer widgets
```

### `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot.render` · *method*

## Summary:
Renders the report root as a vertical box widget containing body and footer content.

## Description:
This method constructs a widget-based representation of the complete report by combining the body and footer renderables into a vertical box layout. It's called during the widget presentation rendering phase of report generation, specifically when creating interactive Jupyter notebook displays.

The method is part of the widget flavor implementation and is responsible for orchestrating the rendering of report components into a single ipywidgets.VBox container that can be displayed in Jupyter environments.

## Args:
    **kwargs: Additional keyword arguments passed through to underlying render methods (though not directly used in current implementation).

## Returns:
    widgets.VBox: A vertical box widget containing the rendered body and footer components arranged vertically.

## Raises:
    AttributeError: If self.content does not contain required "body" or "footer" keys, or if those keys don't have render methods.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing "body" and "footer" renderable elements
    - self.content["body"]: Renderable element for the main report content
    - self.content["footer"]: Renderable element for the report footer
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing "body" and "footer" keys
    - Both self.content["body"] and self.content["footer"] must be renderable objects with render() methods
    - The renderable objects must return valid widget objects when their render() method is called
    
    Postconditions:
    - Returns a widgets.VBox instance containing two child widgets
    - The body widget appears before the footer widget in the vertical arrangement

## Side Effects:
    None: This method doesn't perform I/O operations or mutate external state, though the underlying render() calls on body and footer may have side effects.

