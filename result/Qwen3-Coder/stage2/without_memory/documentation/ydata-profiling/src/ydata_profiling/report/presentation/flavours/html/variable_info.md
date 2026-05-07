# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo` · *class*

## Summary:
HTMLVariableInfo is a presentation layer component that renders variable information as HTML content using Jinja2 templates.

## Description:
This class implements the HTML rendering interface for variable information in data profiling reports. It extends VariableInfo to provide HTML-specific rendering capabilities by utilizing the Jinja2 templating engine. The component is typically instantiated by report generation processes when creating HTML output for variable summaries.

The motivation for this distinct abstraction is to separate the presentation logic (HTML rendering) from the data model (VariableInfo), allowing for different presentation formats (HTML, JSON, etc.) to be implemented while maintaining consistent data structures.

## State:
- anchor_id (str): Unique identifier for the HTML element, used for navigation and linking
- var_name (str): Name of the variable being described
- var_type (str): Data type of the variable (e.g., 'numeric', 'categorical')
- alerts (List[Alert]): List of alert objects containing warnings or issues about the variable
- description (str): Detailed description of the variable's characteristics
- style (Style): Styling configuration for the rendered HTML element
- content (dict): Dictionary containing all the above fields, inherited from parent class

All attributes are initialized through the parent class constructor and are immutable after instantiation.

## Lifecycle:
- Creation: Instantiated by passing required parameters to the parent VariableInfo constructor, which internally sets up the content dictionary
- Usage: Called via the render() method to generate HTML string output
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLVariableInfo.render()] --> B[templates.template("variable_info.html")]
    B --> C[template.render(**self.content)]
```

## Raises:
- Exception: Any exceptions that may occur during Jinja2 template rendering process (including template-related errors)

## Example:
```python
# Create instance
variable_info = HTMLVariableInfo(
    anchor_id="var_1",
    var_name="age",
    var_type="numeric",
    alerts=[],
    description="Age of individuals in years"
)

# Render HTML
html_output = variable_info.render()
# Returns rendered HTML string using the variable_info.html template
```

### `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo.render` · *method*

## Summary:
Renders variable information as an HTML string using a predefined template.

## Description:
This method implements the HTML-specific rendering logic for variable information by delegating to a Jinja2 template engine. It takes the stored variable metadata and formats it according to the "variable_info.html" template structure.

## Args:
    None

## Returns:
    str: A formatted HTML string containing the variable information

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing keys: 'anchor_id', 'var_name', 'description', 'var_type', 'alerts', 'style'
    - The "variable_info.html" template must exist in the template directory
    
    Postconditions:
    - Returns a valid HTML string representation of the variable information
    - Does not modify any instance state

## Side Effects:
    None

