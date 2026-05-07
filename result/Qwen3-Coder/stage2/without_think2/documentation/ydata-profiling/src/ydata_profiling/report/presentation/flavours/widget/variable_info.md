# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo` · *class*

## Summary:
WidgetVariableInfo is a presentation layer class that renders variable metadata and alerts as an interactive HTML widget for Jupyter notebook environments.

## Description:
This class implements the widget-based rendering of variable information within the ydata-profiling report system. It inherits from VariableInfo and provides a concrete implementation of the render() method that generates interactive HTML widgets using ipywidgets. The class serves as a bridge between variable metadata stored in the VariableInfo parent class and the interactive visualization capabilities available in Jupyter environments.

The WidgetVariableInfo class is part of a multi-flavour presentation system where different rendering approaches (widget, HTML, etc.) can be used to display the same underlying data. This particular implementation leverages ipywidgets to create rich, interactive displays that integrate seamlessly with Jupyter notebook workflows.

## State:
- Inherits all attributes from VariableInfo parent class:
  - anchor_id: str - Unique identifier for HTML anchor points
  - var_name: str - Human-readable name of the variable
  - var_type: str - Data type classification of the variable
  - alerts: List[Alert] - Collection of data quality alerts associated with this variable
  - description: str - Detailed description or explanation of the variable
  - style: Style - Styling configuration for report appearance
- content: dict - Dictionary containing variable metadata and alert information (inherited from Renderable parent)

## Lifecycle:
- Creation: Instantiate with all required parameters from VariableInfo parent class
- Usage: Call render() method to generate widgets.HTML object for Jupyter display
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetVariableInfo.render] --> B[templates.template("variable_info.html")]
    B --> C[HTML template rendering]
    C --> D[widgets.HTML()]
    D --> E[Jupyter widget display]
```

## Raises:
- jinja2.TemplateNotFound: When the "variable_info.html" template cannot be found in the Jinja2 environment
- TypeError: When widgets.HTML constructor receives invalid arguments (though this is unlikely given the controlled input)

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.model.alerts import Alert, AlertType
from ydata_profiling.report.presentation.flavours.widget.variable_info import WidgetVariableInfo

# Create sample alerts
alert1 = Alert(AlertType.HIGH_CORRELATION, column_name="var1")
alerts = [alert1]

# Create style configuration
style = Style(primary_colors=["#377eb8"])

# Create widget variable info instance
widget_var_info = WidgetVariableInfo(
    anchor_id="var1-anchor",
    var_name="Variable 1",
    var_type="Numeric",
    alerts=alerts,
    description="This is a sample numeric variable",
    style=style
)

# Render as Jupyter widget
html_widget = widget_var_info.render()
# The html_widget can now be displayed directly in a Jupyter cell
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo.render` · *method*

## Summary:
Renders variable metadata and alert information as an HTML widget for display in Jupyter environments.

## Description:
This method implements the rendering logic for variable information specifically designed for widget-based presentation in Jupyter notebooks. It takes the stored variable metadata and alerts, processes them through an HTML template, and returns a widgets.HTML object that can be displayed directly in notebook cells. The method leverages the HTML template system to ensure consistent formatting while maintaining the flexibility to display variable-specific information.

The render method is part of the WidgetVariableInfo class, which inherits from VariableInfo and implements the abstract render() method defined in the ItemRenderer base class. This approach allows for consistent rendering behavior across different presentation flavours (widget, html, etc.) while providing flavour-specific implementations.

## Args:
    None

## Returns:
    widgets.HTML: An interactive HTML widget containing formatted variable information and alerts that can be rendered in Jupyter environments.

## Raises:
    jinja2.TemplateNotFound: When the "variable_info.html" template cannot be found in the Jinja2 environment.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The Jinja2 template environment must be properly initialized
        - The "variable_info.html" template must exist in the template directory
        - self.content must be a dictionary containing all required template variables
    Postconditions:
        - Returns a valid widgets.HTML object with properly rendered content
        - The returned widget contains all variable metadata and alerts in HTML format

## Side Effects:
    None

