# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo` · *class*

## Summary:
HTMLVariableInfo is a presentation layer component that renders variable information as HTML content using a Jinja2 template.

## Description:
The HTMLVariableInfo class serves as a concrete implementation of the VariableInfo abstract base class specifically designed for HTML report generation. It provides the HTML rendering capability for variable-level information within data profiling reports. This class bridges the gap between variable metadata stored in the parent VariableInfo class and its presentation in HTML format.

This component is typically instantiated by factory methods or constructors within the HTML presentation module when generating HTML reports that require variable information display. The class leverages Jinja2 templating to produce semantically correct HTML output based on the variable metadata contained in its content attribute.

## State:
- Inherits all attributes from VariableInfo parent class:
  - anchor_id (str): Unique identifier for HTML anchors referencing this variable
  - var_name (str): Human-readable name of the variable being described
  - var_type (str): Data type classification of the variable (e.g., 'Numeric', 'Categorical')
  - alerts (List[Alert]): Collection of alert objects indicating issues or notable characteristics of the variable
  - description (str): Detailed description or explanation of the variable's purpose or characteristics
  - style (Style): Styling configuration object that controls the visual presentation of the variable information
- content (dict): Dictionary containing variable metadata that gets passed to the HTML template during rendering

## Lifecycle:
- Creation: Instantiated with the same parameters as VariableInfo parent class, typically through factory methods in the HTML presentation module
- Usage: Called via the render() method to generate HTML output for variable information display
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLVariableInfo.render()] --> B[templates.template("variable_info.html")]
    B --> C[Template Rendering]
    C --> D[HTML Output]
```

## Raises:
- jinja2.TemplateNotFound: When the "variable_info.html" template is not found in the Jinja2 environment
- TypeError: If required arguments are missing or incorrectly typed during instantiation
- AttributeError: If content attribute is not properly initialized in parent class

## Example:
```python
# Typical usage in HTML report generation
from ydata_profiling.report.presentation.flavours.html.variable_info import HTMLVariableInfo
from ydata_profiling.config import Style
from ydata_profiling.model.alerts import Alert

# Create sample data
alerts = [Alert("Missing values detected", "warning")]
style = Style(primary_colors=["#377eb8"])

# Create HTML variable info instance
html_variable_info = HTMLVariableInfo(
    anchor_id="var_age",
    var_name="age",
    var_type="Numeric",
    alerts=alerts,
    description="Age of participants in years",
    style=style
)

# Generate HTML output
html_output = html_variable_info.render()
# Returns rendered HTML string for variable information display
```

### `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo.render` · *method*

## Summary:
Renders variable information as HTML using the 'variable_info.html' Jinja2 template.

## Description:
Generates HTML markup for variable information by rendering the 'variable_info.html' template with the content stored in self.content. This method is part of the HTML presentation flavour implementation for variable information displays and overrides the abstract render() method from VariableInfo base class.

## Args:
    None

## Returns:
    str: HTML string containing the formatted variable information

## Raises:
    jinja2.TemplateNotFound: When the 'variable_info.html' template is not found in the Jinja2 environment

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary-like object that can be unpacked with ** operator
    - The Jinja2 template environment must be properly initialized
    - The 'variable_info.html' template must exist in the template directory
    
    Postconditions:
    - Returns a valid HTML string
    - Does not modify the instance state

## Side Effects:
    None - Pure function with no external side effects beyond template rendering

