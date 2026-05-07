# `root.py`

## `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot` · *class*

## Summary:
HTMLRoot is a concrete implementation of the Root class that renders complete profiling reports as HTML documents.

## Description:
HTMLRoot serves as the specialized renderer for HTML-based profiling reports, inheriting from the generic Root class. It implements the render method to transform structured report content into a complete HTML document using Jinja2 templating. This class is typically instantiated by report generation pipelines and is responsible for producing the final HTML output that users see when viewing profiling results in a web browser.

The class extracts navigation items from report sections and integrates them with the main report content before applying the report.html template. It bridges the gap between structured report data and HTML presentation, making it a crucial component in the HTML report generation pipeline.

## State:
- Inherits all state from Root class including:
  - item_type: str - Set to "report" by parent constructor, identifying this as a report-level renderer
  - content: dict - Contains "body", "footer", and "style" keys with respective Renderable objects
  - name: str - Human-readable identifier for the report
  - anchor_id: str - Optional anchor identifier, inherited from Renderable parent
  - classes: str - Optional CSS classes, inherited from Renderable parent

## Lifecycle:
- Creation: Instantiated with the same parameters as Root (name, body, footer, style)
- Usage: Called by report generation pipelines during HTML report rendering process
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLRoot.render] --> B[Extract nav_items from body sections]
    B --> C[Prepare template context with content and nav_items]
    C --> D[templates.template("report.html").render]
    D --> E[Return HTML string]
```

## Raises:
- None explicitly raised by HTMLRoot.render(), though underlying template rendering may raise Jinja2-related exceptions

## Example:
```python
# Typical usage in report generation pipeline
from ydata_profiling.report.presentation.flavours.html.root import HTMLRoot
from ydata_profiling.report.presentation.core.html import HTML
from ydata_profiling.config import Style

# Create body and footer renderables
body_content = HTML("Report Body Content")
footer_content = HTML("Report Footer")

# Create style configuration
style_config = Style(primary_colors=["#0000ff"])

# Create HTMLRoot instance (typically done internally by report generator)
html_root = HTMLRoot(
    name="my_report",
    body=body_content,
    footer=footer_content,
    style=style_config
)

# Render the HTML report (called internally by pipeline)
html_output = html_root.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot.render` · *method*

## Summary:
Renders the HTML report by processing navigation items from the body content and applying the report template.

## Description:
This method generates a complete HTML report by extracting navigation items from the report body sections and rendering them using the Jinja2 report.html template. It serves as the concrete implementation of the render method for HTML-based report generation, transforming the structured report content into a formatted HTML string.

The method is called during the HTML report generation pipeline when a complete HTML report needs to be produced from the structured content hierarchy.

## Args:
    **kwargs: Additional keyword arguments passed to the Jinja2 template engine for customization of the rendered output.

## Returns:
    str: A complete HTML string representing the formatted report with navigation items and all content sections properly rendered.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying template rendering may raise Jinja2-related exceptions.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing the report structure with body, footer, and style elements
    - self.content["body"].content["items"]: Collection of sections used to build navigation items
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain a "body" key with a content structure that has an "items" attribute
    - Each item in self.content["body"].content["items"] must have "name" and "anchor_id" attributes
    - The report.html template must be available in the templates module
    
    Postconditions:
    - Returns a valid HTML string with proper navigation structure
    - All content from self.content is properly embedded in the rendered template

## Side Effects:
    Template rendering: Invokes Jinja2 template engine which may perform file I/O to load the report.html template
    String construction: Creates a new HTML string from template rendering and content merging

