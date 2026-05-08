# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable` · *class*

## Summary:
HTMLVariable is a presentation class that renders variable content using an HTML template.

## Description:
HTMLVariable is a concrete implementation of the Variable class specifically designed for HTML report generation. It inherits from Variable and implements the render() method to generate HTML output by rendering the variable content through a Jinja2 template. This class serves as a bridge between structured variable data and its HTML presentation in ydata-profiling reports.

The class is typically instantiated by the report generation system when creating HTML representations of variables. It expects its parent Variable class to have properly structured content with top and bottom sections that can be rendered through the template.

## State:
- Inherits all attributes from Variable class including:
  - item_type: str - Set to "variable" by parent constructor
  - content: dict - Contains structured data with keys:
    - "top": Renderable - Required content for the top section
    - "bottom": Optional[Renderable] - Optional content for the bottom section
    - "ignore": bool - Flag indicating whether this variable should be ignored during rendering (default: False)
  - name: str (inherited from Renderable) - Optional human-readable identifier
  - anchor_id: str (inherited from Renderable) - Optional HTML anchor identifier
  - classes: str (inherited from Renderable) - Optional CSS classes for styling

## Lifecycle:
- Creation: Instantiated with the standard Variable constructor parameters (top Renderable, optional bottom Renderable, optional ignore flag)
- Usage: Called by the report generation system to render variable content as HTML via the render() method
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLVariable.render()] --> B[templates.template("variable.html")]
    B --> C[Template.render(**self.content)]
    C --> D[HTML Output]
```

## Raises:
- jinja2.TemplateNotFound: When the "variable.html" template is not found in the Jinja2 environment
- KeyError: When self.content dictionary doesn't contain required keys expected by the template
- AttributeError: When self.content is None or improperly structured

## Example:
```python
# Typical usage in report generation
from ydata_profiling.report.presentation.flavours.html.variable import HTMLVariable
from ydata_profiling.report.presentation.core import Variable

# Create variable content (typically done internally by report generator)
top_section = Text("Age Variable Statistics")
bottom_section = Table([["Mean", "25.5"], ["Std Dev", "5.2"]])

# HTMLVariable is created and rendered automatically by the system
variable = Variable(top=top_section, bottom=bottom_section)
html_variable = HTMLVariable(top=top_section, bottom=bottom_section)

# Render to HTML (called internally by report generation)
html_output = html_variable.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable.render` · *method*

## Summary:
Renders variable presentation content using the HTML template system.

## Description:
This method generates HTML output for variable presentation elements by rendering the "variable.html" template with the content stored in the instance. It serves as the core rendering mechanism for variable-type presentation components in the HTML report generation pipeline.

The method is part of the HTMLVariable class, which extends the base Variable class to provide HTML-specific rendering capabilities. It leverages the global template system to fetch and render the appropriate HTML template with the structured content data.

This method is specifically designed to be overridden in subclasses and provides a standardized interface for HTML-based variable rendering throughout the ydata-profiling system.

## Args:
    None - This method takes no parameters beyond the implicit self reference.

## Returns:
    str - A string containing the rendered HTML output for the variable presentation element, typically containing structured content with top and bottom sections.

## Raises:
    jinja2.TemplateNotFound - When the "variable.html" template cannot be found in the Jinja2 environment.
    AttributeError - If self.content is not properly initialized or does not contain the expected structure (top/bottom sections).

## State Changes:
    Attributes READ:
    - self.content: Dictionary containing structured data for rendering with keys:
      * "top": Renderable object for the variable header/content
      * "bottom": Optional Renderable object for detailed statistics/visualizations
      * "ignore": Boolean flag indicating if the variable should be skipped
    - self.item_type: Inherited from Variable class, identifies this as a variable-type presentation element

    Attributes WRITTEN:
    - None: This method does not modify any instance attributes

## Constraints:
    Preconditions:
    - The global Jinja2 environment must be properly initialized
    - The "variable.html" template must exist in the template directory
    - self.content must be a dictionary with valid keys for template rendering
    - The HTMLVariable instance must be properly initialized with required content
    - The top section of content must be a valid Renderable object

    Postconditions:
    - Returns a valid HTML string representation of the variable content
    - Does not alter the state of the HTMLVariable instance
    - The returned HTML follows the expected structure defined by the variable.html template

## Side Effects:
    None - This method is pure and does not perform any I/O operations or mutate external state.

