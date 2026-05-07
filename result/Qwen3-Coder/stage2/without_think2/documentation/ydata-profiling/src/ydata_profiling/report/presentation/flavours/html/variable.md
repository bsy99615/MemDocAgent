# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable` · *class*

## Summary:
HTMLVariable is a concrete implementation of the Variable class that renders variable report content using HTML templates.

## Description:
The HTMLVariable class serves as a specialized renderer for variable components within the HTML presentation flavour of ydata-profiling reports. It extends the base Variable class to provide HTML-specific rendering capabilities by utilizing Jinja2 templates. This class is responsible for transforming structured variable content into properly formatted HTML output that can be embedded in web-based profiling reports.

The class is typically instantiated by report generation logic when creating HTML representations of variable data. It follows the standard pattern of inheriting variable content structure from its parent class while implementing the specific rendering behavior required for HTML output.

## State:
- Inherits all attributes from Variable class including:
  - item_type: str - Set to "variable" by constructor, identifies this component type
  - content: dict - Dictionary containing "top" and "bottom" renderable sections, and "ignore" flag
  - name: Optional[str] - Human-readable identifier (inherited from Renderable)
  - anchor_id: Optional[str] - Unique identifier for HTML anchors (inherited from Renderable)
  - classes: Optional[str] - CSS classes for styling (inherited from Renderable)

## Lifecycle:
- Creation: Instantiate with required `top` parameter and optional `bottom` and `ignore` parameters, inheriting from Variable class
- Usage: Call `render()` method to generate HTML output using the "variable.html" template
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLVariable.render] --> B[templates.template("variable.html")]
    B --> C[Template.render(**self.content)]
    C --> D[HTML String Output]
```

## Raises:
- jinja2.TemplateNotFound: When the "variable.html" template is not found in the Jinja2 environment
- KeyError: If required keys are missing from self.content when passed to template.render()

## Example:
```python
# Create a variable with top content
top_content = Text("Variable Name: age")
bottom_content = Table([["Mean", "25.5"], ["Std Dev", "5.2"]])

# Create HTMLVariable instance
html_variable = HTMLVariable(top=top_content, bottom=bottom_content, ignore=False)

# Render to HTML
html_output = html_variable.render()  # Returns formatted HTML string
```

### `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable.render` · *method*

## Summary:
Renders the HTML template for a variable report using the stored content.

## Description:
This method generates HTML output for a variable presentation by rendering the "variable.html" template with the content stored in the instance. It serves as the primary rendering mechanism for variable-specific report elements in the HTML presentation flavour. The method leverages the parent Variable class's content structure, which contains top and bottom sections for variable information.

## Args:
    None

## Returns:
    str: The rendered HTML string containing the formatted variable report content.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The instance must have a content attribute containing the data needed for template rendering. The content dictionary must include the required keys expected by the "variable.html" template.
    Postconditions: The returned string is a valid HTML representation of the variable content.

## Side Effects:
    None

