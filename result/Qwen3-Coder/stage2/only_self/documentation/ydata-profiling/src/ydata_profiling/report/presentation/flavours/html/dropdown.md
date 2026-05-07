# `dropdown.py`

## `src.ydata_profiling.report.presentation.flavours.html.dropdown.HTMLDropdown` · *class*

## Summary:
HTMLDropdown is a concrete implementation of the Dropdown renderable component that generates HTML markup for dropdown UI elements using Jinja2 templates.

## Description:
The HTMLDropdown class provides HTML-specific rendering capabilities for dropdown components in report presentations. It inherits from the abstract Dropdown class and implements the render() method to produce HTML output using a predefined Jinja2 template. This class serves as a bridge between the abstract dropdown presentation layer and concrete HTML generation, enabling the creation of interactive dropdown elements in web-based reports.

This class is typically instantiated by the report generation pipeline when HTML output is required, particularly when dropdown components are needed to organize hierarchical content in generated reports. It is part of the HTML presentation flavour of the ydata-profiling report generation system.

## State:
- Inherits all attributes from Dropdown parent class including:
  - name: str - Human-readable identifier for the dropdown
  - id: str - Unique identifier for the dropdown element  
  - items: list - List of items that populate the dropdown menu
  - item: Container - The container holding the content to be displayed when dropdown is activated
  - anchor_id: str - HTML anchor ID for linking to this dropdown element
  - classes: str - CSS classes for styling the dropdown (joined from list input)
  - is_row: bool - Flag indicating whether the dropdown should be rendered in row orientation
  - content: dict - Dictionary containing all configuration parameters inherited from Renderable base class

## Lifecycle:
- Creation: Instantiate with all required Dropdown parameters including name, id, items, item (Container), anchor_id, classes (list), and is_row boolean
- Usage: Called by the report generation system when HTML output is needed, specifically when a dropdown component needs to be rendered to HTML
- Destruction: Relies on Python garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[HTMLDropdown.render] --> B[templates.template("dropdown.html").render(**self.content)]
```

## Raises:
- TemplateNotFound: If the "dropdown.html" template is not found in the Jinja2 environment
- UndefinedError: If required variables are missing from self.content when rendering the template

## Example:
```python
# Create a dropdown with associated content
dropdown_item = Container(items=[text_component], sequence_type="list")
dropdown = HTMLDropdown(
    name="Data Overview",
    id="data-overview-dropdown",
    items=["summary", "details", "analysis"],
    item=dropdown_item,
    anchor_id="overview-anchor",
    classes=["dropdown-class", "custom-style"],
    is_row=True
)

# Render to HTML
html_output = dropdown.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.dropdown.HTMLDropdown.render` · *method*

## Summary:
Renders the HTML dropdown component by applying the dropdown template to the component's content configuration.

## Description:
This method generates HTML markup for a dropdown UI element by rendering the predefined "dropdown.html" Jinja2 template with the component's configuration data. The method serves as the concrete implementation of the abstract render method inherited from the Dropdown base class, specifically tailored for HTML presentation.

The render method is typically called during the report generation pipeline when HTML output is being constructed. It transforms the structured configuration data stored in self.content into properly formatted HTML that can be embedded in larger HTML documents.

This method is part of the HTML presentation flavour implementation and is responsible for converting dropdown components into their HTML representation. It leverages the Jinja2 templating engine to apply consistent formatting and structure to dropdown elements, enabling interactive dropdown menus in generated reports.

The method exists to separate the presentation logic from the data model, following the MVC pattern where Dropdown represents the model and HTMLDropdown handles the view rendering. This design allows for different presentation flavours (HTML, JSON, etc.) to be implemented while maintaining consistent data structures.

## Args:
    None - This method takes no arguments beyond the implicit self parameter.

## Returns:
    str - A string containing the rendered HTML markup for the dropdown component.

## Raises:
    jinja2.exceptions.TemplateNotFound: If the "dropdown.html" template is not found in the template registry
    jinja2.exceptions.UndefinedError: If required variables from self.content are missing when rendering the template
    Exception: Any other exception that may occur during template rendering or processing

## State Changes:
    Attributes READ:
        - self.content: Dictionary containing configuration parameters for the dropdown component, including title, id, items, and other dropdown-specific properties
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - self.content must be a dictionary containing valid keys expected by the dropdown.html template
        - The "dropdown.html" template must be available in the template registry
        - All required template variables must be present in self.content
    Postconditions:
        - Returns a valid HTML string representation of the dropdown component
        - The returned HTML is properly formatted according to the template specification

## Side Effects:
    None - This method is pure and does not cause any external I/O operations or mutations to objects outside the instance.

