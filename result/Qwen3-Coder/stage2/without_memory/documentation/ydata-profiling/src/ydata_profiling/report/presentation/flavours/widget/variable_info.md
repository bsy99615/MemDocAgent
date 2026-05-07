# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo` · *class*

## Summary:
WidgetVariableInfo is a presentation layer component that renders variable information as an interactive HTML widget for Jupyter environments.

## Description:
This class implements the widget-based rendering of variable information in the ydata-profiling report system. It extends VariableInfo to provide a concrete implementation for creating interactive HTML widgets that display variable metadata such as name, type, description, and alerts. The component is specifically designed for use in Jupyter notebook environments where ipywidgets are supported.

The class serves as a bridge between the abstract variable information representation and its concrete widget-based visualization, enabling interactive exploration of variable properties within notebook interfaces.

## State:
- content: dict - Contains all variable metadata including anchor_id, var_name, description, var_type, alerts, and style. This is inherited from the Renderable base class.
- anchor_id: str - Unique identifier for the variable element, used for navigation and linking.
- var_name: str - Name of the variable being described.
- var_type: str - Data type of the variable (e.g., 'numeric', 'categorical').
- alerts: List[Alert] - List of alert objects indicating potential issues with the variable.
- description: str - Detailed description of the variable's characteristics.
- style: Style - Styling configuration for the widget appearance.

## Lifecycle:
- Creation: Instantiated with the same parameters as VariableInfo, requiring anchor_id, var_name, var_type, alerts, and description, plus optional style and kwargs.
- Usage: Called via the render() method which returns a widgets.HTML object containing the formatted variable information.
- Destruction: No explicit cleanup required as ipywidgets handle their own lifecycle management.

## Method Map:
```mermaid
graph TD
    A[WidgetVariableInfo] --> B[VariableInfo]
    B --> C[ItemRenderer]
    C --> D[Renderable]
    D --> E[render()]
    E --> F[widgets.HTML]
    F --> G[template("variable_info.html")]
```

## Raises:
- Template rendering errors if the "variable_info.html" template is missing or malformed.
- Any exceptions raised by ipywidgets.HTML constructor when processing the rendered template content.

## Example:
```python
# Create a variable info widget
widget_info = WidgetVariableInfo(
    anchor_id="var_1",
    var_name="age",
    var_type="numeric",
    alerts=[],
    description="Age of individuals in years"
)

# Render the widget for display in Jupyter
html_widget = widget_info.render()
display(html_widget)
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo.render` · *method*

## Summary:
Renders variable information as an interactive HTML widget for Jupyter environments.

## Description:
Creates and returns an ipywidgets.HTML object containing formatted variable metadata by rendering the 'variable_info.html' template with the instance's content data. This method is part of the widget-based presentation flavour for data profiling reports, specifically designed for Jupyter notebook environments where interactive widgets are supported.

## Args:
    None - This is an instance method that operates on self

## Returns:
    widgets.HTML: An interactive HTML widget containing the formatted variable information

## Raises:
    jinja2.exceptions.TemplateError: If the 'variable_info.html' template cannot be rendered due to missing variables or template syntax errors
    AttributeError: If self.content is not properly initialized or missing required keys for template rendering

## State Changes:
    Attributes READ: self.content (used to populate template variables)
    Attributes WRITTEN: None - This method is read-only

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing keys expected by the 'variable_info.html' template (typically including: anchor_id, var_name, description, var_type, alerts, style)
    - The 'variable_info.html' template must be available in the templates module
    - This method should only be called in Jupyter environments where ipywidgets is available
    
    Postconditions:
    - Returns a valid widgets.HTML object ready for display in Jupyter notebooks
    - The returned widget contains properly formatted HTML content

## Side Effects:
    None - This method is pure and doesn't cause external I/O or state changes beyond returning a widget object

