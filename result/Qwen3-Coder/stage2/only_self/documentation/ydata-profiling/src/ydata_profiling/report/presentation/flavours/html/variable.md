# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable` · *class*

## Summary:
HTMLVariable is a presentation layer component that renders variable data as HTML using a Jinja2 template.

## Description:
The HTMLVariable class is a concrete implementation of the Variable base class specifically designed for HTML report generation. It provides the rendering logic to transform variable data into HTML format by utilizing the "variable.html" Jinja2 template. This class bridges the gap between structured variable data and its HTML presentation in profiling reports.

This class is typically instantiated by report generation components that need to display variable information in HTML format. It serves as a specialized renderer that ensures consistent HTML structure for variable elements within the profiling report.

## State:
- Inherits all attributes from Variable parent class:
  - top: Renderable - Required content for the primary variable information displayed at the top
  - bottom: Optional[Renderable] - Optional secondary content displayed below the top section
  - ignore: bool - Flag indicating whether this variable should be ignored during processing
  - item_type: str - Class attribute identifying this as a "variable" type item
  - content: dict - Dictionary containing the item's data and metadata, populated automatically during initialization
- No additional instance attributes beyond those inherited from parent classes

## Lifecycle:
- Creation: Instantiate with required top Renderable object and optional bottom Renderable and ignore flag, inheriting all initialization behavior from Variable parent class. The content dictionary is automatically populated with the provided arguments.
- Usage: Call render() method to generate HTML output using the "variable.html" template with the content dictionary as context
- Destruction: Inherits standard Python object lifecycle management

## Method Map:
```mermaid
graph TD
    A[HTMLVariable.render()] --> B[templates.template("variable.html")]
    B --> C[template.render(**self.content)]
    C --> D[HTML string output]
```

## Raises:
- jinja2.TemplateNotFound: When the "variable.html" template is not found in the Jinja2 environment
- Any exceptions raised by the parent Variable class during initialization (inherited from ItemRenderer and Renderable)
- Any exceptions that might occur during template rendering if the content structure is invalid

## Example:
```python
# Create top content for a variable
from ydata_profiling.report.presentation.flavours.html import Text, Table

top_content = Text("Age Variable")
bottom_content = Table([["Min", "Max"], [18, 85]])

# Create HTMLVariable instance
html_variable = HTMLVariable(top_content, bottom_content, ignore=False)

# Render to HTML
html_output = html_variable.render()
# Returns HTML string using variable.html template with content context
# The content dictionary contains: {"top": top_content, "bottom": bottom_content, "ignore": False}
```

### `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable.render` · *method*

## Summary:
Renders the variable content using an HTML template and returns the resulting HTML string.

## Description:
This method implements the HTML rendering logic for variable elements in profiling reports. It retrieves the "variable.html" template from the global template environment and renders it with the content data stored in the instance. This method is part of the HTML presentation flavour implementation for variable elements.

The method is called during the report generation pipeline when HTML output is required for variable information. It leverages the parent Variable class's content structure to populate the template variables.

## Args:
    None - This method takes no parameters beyond the implicit self reference.

## Returns:
    str: A string containing the rendered HTML output for the variable element.

## Raises:
    jinja2.TemplateNotFound: When the "variable.html" template is not found in the Jinja2 environment.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing the variable's data and metadata used for template rendering
    
    Attributes WRITTEN: 
    - None: This method does not modify any instance attributes.

## Constraints:
    Preconditions:
    - The global Jinja2 environment must be properly initialized
    - The "variable.html" template must exist in the Jinja2 environment
    - The self.content dictionary must be properly populated with data compatible with the template
    
    Postconditions:
    - Returns a valid HTML string representation of the variable content
    - Does not alter the instance's state

## Side Effects:
    None - This method is pure and has no side effects beyond template rendering.

