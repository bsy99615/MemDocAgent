# `root.py`

## `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot` · *class*

## Summary:
HTMLRoot is a presentation layer class that renders report content as HTML using Jinja2 templates.

## Description:
HTMLRoot is responsible for generating complete HTML reports by rendering the structured content from the profiling process. It inherits from the abstract Root class and implements the render method to produce HTML output. This class serves as the entry point for HTML report generation in the ydata-profiling library's presentation layer.

The class extracts navigation items from the report sections and uses a Jinja2 template to render the complete HTML structure, combining the report content with navigation elements and additional keyword arguments.

## State:
- content: Dictionary containing the report structure with keys "body", "footer", and "style"
- name: String identifier for the report (inherited from Renderable)
- anchor_id: String identifier for anchoring within the report (inherited from Renderable)
- classes: String containing CSS classes (inherited from Renderable)

The content dictionary follows this structure:
- body: Renderable object containing the main report content (with nested content["items"] structure)
- footer: Renderable object containing footer content  
- style: Renderable object containing styling information

## Lifecycle:
- Creation: Instantiated with name, body, footer, and style parameters inherited from Root constructor
- Usage: Called via render() method which processes the content and returns HTML string
- Destruction: No special cleanup required as it's a stateless renderer

## Method Map:
```mermaid
graph TD
    A[HTMLRoot.render] --> B[Extract nav_items]
    B --> C[templates.template("report.html").render]
    C --> D[Return HTML string]
```

## Raises:
- NotImplementedError: Inherited from parent Root class (though HTMLRoot overrides this)
- Template rendering errors: If the report.html template is missing or malformed

## Example:
```python
# Create HTMLRoot instance (typically done by framework)
root = HTMLRoot(name="my_report", body=body_section, footer=footer_section, style=style_section)

# Render to HTML
html_output = root.render(custom_param="value")
```

### `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot.render` · *method*

*No documentation generated.*

