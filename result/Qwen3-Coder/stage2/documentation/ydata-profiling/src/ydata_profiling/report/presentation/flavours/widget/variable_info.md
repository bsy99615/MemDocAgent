# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo` · *class*

## Summary:
WidgetVariableInfo is a presentation layer class that renders variable information as an interactive HTML widget for use in Jupyter notebook environments.

## Description:
WidgetVariableInfo is a concrete implementation of VariableInfo designed specifically for rendering variable metadata within Jupyter notebook interfaces using ipywidgets. It extends the base VariableInfo class to provide a widget-based presentation layer that integrates seamlessly with interactive data analysis workflows.

This class serves as a bridge between structured variable information data and its visual representation in Jupyter environments, enabling users to interact with variable metadata through rich HTML widgets rather than static HTML output.

## State:
- Inherits all attributes from VariableInfo parent class:
  - anchor_id (str): Unique identifier for HTML anchors referencing this variable
  - var_name (str): Human-readable name of the variable being described
  - var_type (str): Data type classification of the variable (e.g., 'Numeric', 'Categorical')
  - alerts (List[Alert]): Collection of alert objects indicating issues or notable characteristics of the variable
  - description (str): Detailed description or explanation of the variable's purpose or characteristics
  - style (Style): Styling configuration object that controls the visual presentation of the variable information

## Lifecycle:
- Creation: Instantiate with all required parameters inherited from VariableInfo parent class
- Usage: Call render() method to generate a widgets.HTML widget containing formatted variable information
- Destruction: Managed automatically by Python's garbage collection or through widget disposal mechanisms

## Method Map:
```mermaid
graph TD
    A[WidgetVariableInfo.render()] --> B[templates.template("variable_info.html")]
    B --> C[HTML template rendering]
    C --> D[widgets.HTML()]
    D --> E[Interactive HTML widget]
```

## Raises:
- TemplateNotFound: When the "variable_info.html" template cannot be found in the Jinja2 environment
- TypeError: If any parent class constructor parameters are invalid or missing
- AttributeError: If self.content is not properly initialized in the parent class

## Example:
```python
# Create a VariableInfo instance (typically done through subclasses)
from ydata_profiling.config import Style
from ydata_profiling.model.alerts import Alert
from ydata_profiling.report.presentation.flavours.widget.variable_info import WidgetVariableInfo

# Create sample data
alerts = [Alert("Missing values detected", "warning")]
style = Style(primary_colors=["#377eb8"])

# Create variable info instance
variable_info = WidgetVariableInfo(
    anchor_id="var_123",
    var_name="age",
    var_type="Numeric",
    alerts=alerts,
    description="Age of participants in years",
    style=style
)

# Render as interactive HTML widget
widget = variable_info.render()
# widget is now a widgets.HTML object ready for display in Jupyter
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo.render` · *method*

## Summary:
Renders variable information as an interactive HTML widget for Jupyter environments.

## Description:
Converts variable metadata into an interactive HTML widget representation using the 'variable_info.html' Jinja2 template. This method overrides the abstract render() method from the VariableInfo base class to provide a widget-based presentation suitable for Jupyter notebook environments.

The method accesses the variable information stored in self.content and renders it using the shared HTML template, wrapping the result in an ipywidgets.HTML widget for interactive display.

## Args:
    None

## Returns:
    widgets.HTML: An ipywidgets.HTML object containing the formatted variable information that can be displayed in Jupyter notebooks.

## Raises:
    jinja2.TemplateNotFound: When the 'variable_info.html' template is not found in the Jinja2 environment.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing variable metadata (anchor_id, var_name, description, var_type, alerts, style)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary-like object that can be unpacked with ** operator
    - The Jinja2 template environment must be properly initialized
    - The 'variable_info.html' template must exist in the template directory
    
    Postconditions:
    - Returns a valid widgets.HTML object
    - Does not modify the instance state

## Side Effects:
    None - Pure function with no external side effects beyond widget creation.

