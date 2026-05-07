# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo` · *class*

## Summary:
WidgetVariableInfo renders variable information as an interactive HTML widget for Jupyter environments.

## Description:
This class implements the VariableInfo rendering interface specifically for widget-based presentations in Jupyter notebooks. It inherits from the core VariableInfo class and provides a concrete implementation that generates interactive HTML widgets using ipywidgets.

The implementation leverages the HTML template system to render variable metadata and statistics into a widgets.HTML widget, enabling rich, interactive data profiling visualizations within notebook environments. This presentation flavour is particularly useful for exploratory data analysis workflows where interactive visualization is beneficial.

## State:
- Inherits all attributes from VariableInfo parent class including `content` dictionary
- `content` attribute: Dictionary containing variable metadata and statistics to be rendered
- The class depends on the inherited content structure from VariableInfo for proper rendering

## Lifecycle:
- Creation: Instantiated with standard VariableInfo constructor parameters (typically content dictionary)
- Usage: Called via `render()` method to produce a `ipywidgets.HTML` widget instance
- Destruction: Managed automatically by ipywidgets lifecycle management system

## Method Map:
```mermaid
flowchart TD
    A[WidgetVariableInfo.__init__] --> B[WidgetVariableInfo.render]
    B --> C[templates.template("variable_info.html")]
    C --> D[widgets.HTML()]
```

## Raises:
- `jinja2.TemplateNotFound`: When the "variable_info.html" template is not found in the Jinja2 environment
- Inherited exceptions from VariableInfo parent class initialization

## Example:
```python
# Create a WidgetVariableInfo instance with variable content
content = {
    "name": "age",
    "type": "int",
    "count": 100,
    "missing": 0,
    "unique": 85
}
info = WidgetVariableInfo(content=content)

# Render as interactive HTML widget for Jupyter display
widget = info.render()

# Display in Jupyter notebook (widget automatically rendered)
widget
```

### `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo.render` · *method*

## Summary:
Renders variable information as an interactive HTML widget for display in Jupyter environments.

## Description:
Transforms structured variable metadata into an interactive HTML widget using a Jinja2 template. This method is part of the widget-based presentation flavour that enables rich, interactive reporting in Jupyter notebooks by converting data into ipywidgets.HTML objects.

## Args:
    None: This method takes no parameters beyond the implicit self reference.

## Returns:
    widgets.HTML: An ipywidgets HTML object containing formatted variable information including name, type, description, and quality alerts.

## Raises:
    jinja2.TemplateNotFound: When the "variable_info.html" template is not found in the Jinja2 environment.
    KeyError: When required keys are missing from self.content during template rendering.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing variable metadata with keys: anchor_id, var_name, var_type, alerts, description, and style
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain all required keys: anchor_id, var_name, var_type, alerts, description, style
    - The global jinja2_env must be properly initialized
    - The "variable_info.html" template must exist in the Jinja2 environment
    
    Postconditions:
    - Returns a valid widgets.HTML object ready for Jupyter display
    - Does not modify the object's internal state

## Side Effects:
    None: This method performs no I/O operations or external service calls beyond accessing the global template environment and creating an ipywidgets object.

## Usage Context:
This method is invoked during report generation when rendering variable information in Jupyter notebook environments. It's specifically designed for the widget presentation flavour that provides enhanced interactivity compared to static HTML rendering, making it ideal for exploratory data analysis in interactive development environments.

