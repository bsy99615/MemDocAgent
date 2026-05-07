# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo` · *class*

## Summary:
HTML implementation of the VariableInfo class that renders variable metadata using an HTML template.

## Description:
The HTMLVariableInfo class provides a concrete implementation for rendering variable information in HTML format. It inherits from VariableInfo and implements the render() method to generate HTML output using a Jinja2 template. This class serves as part of the HTML presentation flavour in the ydata-profiling report generation system, specifically handling the formatting and display of variable metadata within HTML reports.

This class is designed to work within the report generation pipeline where VariableInfo objects are created with metadata and then rendered into appropriate formats based on the selected presentation flavour. The HTML implementation focuses solely on transforming the stored variable information into properly formatted HTML content.

## State:
- Inherits all attributes from VariableInfo parent class including:
  - anchor_id: str - Unique identifier for HTML anchor points
  - var_name: str - Human-readable name of the variable
  - var_type: str - Data type classification of the variable
  - alerts: List[Alert] - Collection of data quality alerts associated with this variable
  - description: str - Detailed description or explanation of the variable
  - style: Style - Styling configuration for report appearance
- content: dict - Dictionary containing variable metadata that gets passed to the template engine

## Lifecycle:
- Creation: Instantiate with required parameters inherited from VariableInfo parent class
- Usage: Call render() method to generate HTML output from stored content
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLVariableInfo.render] --> B[templates.template("variable_info.html")]
    B --> C[Template.render(**self.content)]
    C --> D[HTML String Output]
```

## Raises:
- jinja2.TemplateNotFound: When the "variable_info.html" template is not found in the Jinja2 environment

## Example:
```python
from ydata_profiling.report.presentation.flavours.html.variable_info import HTMLVariableInfo
from ydata_profiling.config import Style
from ydata_profiling.model.alerts import Alert, AlertType

# Create sample alerts
alert1 = Alert(AlertType.HIGH_CORRELATION, column_name="var1")
alerts = [alert1]

# Create style configuration
style = Style(primary_colors=["#377eb8"])

# Create HTML variable info instance
html_var_info = HTMLVariableInfo(
    anchor_id="var1-anchor",
    var_name="Variable 1",
    var_type="Numeric",
    alerts=alerts,
    description="This is a sample numeric variable",
    style=style
)

# Render the HTML output
html_output = html_var_info.render()
# Returns formatted HTML string with variable information
```

### `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo.render` · *method*

## Summary:
Renders variable information using an HTML template and the object's content dictionary.

## Description:
This method implements the rendering logic for HTML variable information by utilizing a Jinja2 template. It takes the content stored in the object's content attribute and renders it using the "variable_info.html" template. The method serves as the concrete implementation of the abstract render() method required by the inheritance hierarchy.

The method is called during the HTML report generation pipeline when variable information needs to be formatted for display in the final HTML output. This separation allows for consistent rendering behavior while enabling different template implementations across presentation flavours.

This method is specifically designed to work with the VariableInfo class hierarchy, where content is pre-populated with variable metadata during object initialization. The separation of concerns ensures that the rendering logic is decoupled from the data structure management.

## Args:
    None

## Returns:
    str: The rendered HTML string containing the formatted variable information.

## Raises:
    jinja2.TemplateNotFound: When the "variable_info.html" template is not found in the Jinja2 environment.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The object must have a valid content dictionary populated with required data (typically via VariableInfo.__init__)
        - The global Jinja2 environment must be properly initialized
        - The "variable_info.html" template must exist in the template directory
    Postconditions:
        - Returns a properly formatted HTML string
        - The content dictionary remains unchanged

## Side Effects:
    None

