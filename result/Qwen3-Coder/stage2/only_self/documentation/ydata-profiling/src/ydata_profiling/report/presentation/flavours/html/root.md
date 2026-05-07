# `root.py`

## `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot` · *class*

## Summary:
HTMLRoot is a presentation layer class that renders HTML reports by processing section navigation items and applying the report.html template.

## Description:
This class implements the HTML rendering functionality for report generation, inheriting from the core Root class. It serves as the final rendering endpoint that transforms structured report content into HTML output. The class is typically instantiated and used internally by the report generation pipeline when HTML output format is requested.

## State:
- content: Dictionary containing structured report data with expected hierarchy:
  - Must contain "body" key with nested "content" dictionary
  - "content" must contain "items" list of section objects  
  - Each section object must have "name" and "anchor_id" attributes
- Inherits all state management from the Root base class
- __init__ parameters: Accepts standard Root initialization parameters with no additional constraints

## Lifecycle:
- Creation: Instantiated with standard Root constructor, typically through factory methods in the presentation layer
- Usage: Called via render() method which processes content structure and returns HTML string
- Destruction: No special cleanup required; inherits standard object lifecycle

## Method Map:
```mermaid
graph TD
    A[HTMLRoot.render(**kwargs)] --> B[Extract nav_items from content]
    B --> C[Access self.content["body"].content["items"]]
    C --> D[Create (section.name, section.anchor_id) tuples]
    D --> E[Render template with: self.content + nav_items + kwargs]
    E --> F[templates.template("report.html").render(**self.content, nav_items=nav_items, **kwargs)]
    F --> G[Return HTML string]
```

## Raises:
- KeyError: If content structure doesn't contain expected keys ("body", "content", "items")
- AttributeError: If section items don't have "name" or "anchor_id" attributes
- Template rendering errors: From the underlying template engine when processing content

## Example:
```python
# Typical usage in report generation pipeline
root = HTMLRoot(content=report_content)

# Render HTML report with additional template variables
html_output = root.render(
    title="My Report", 
    author="John Doe",
    generated_at="2023-01-01"
)

# Returns complete HTML string with navigation and content
```

### `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot.render` · *method*

## Summary:
Generates an HTML representation of a report by extracting navigation items and rendering with a Jinja2 template.

## Description:
This method processes the report's body content to extract navigation items (section names and anchor IDs) and renders the complete HTML report using the 'report.html' template. It accesses the hierarchical content structure to build navigation metadata before combining it with the report's core content and additional parameters.

The method serves as the primary rendering entry point for HTML report generation, separating navigation data preparation from template rendering logic.

Known callers:
- Called during report generation pipeline when HTML output is requested
- Invoked by the presentation layer when converting report components to HTML format
- Part of the standard rendering workflow in the HTML presentation flavour

This logic is separated into its own method to encapsulate the HTML-specific rendering concerns and maintain clean separation between data preparation (navigation item creation) and template rendering.

## Args:
    **kwargs: Additional keyword arguments passed through to the Jinja2 template renderer

## Returns:
    str: Complete HTML string representation of the report containing all sections and navigation elements

## Raises:
    AttributeError: If self.content or its nested structure does not contain expected keys/attributes
    KeyError: If template "report.html" is not found in the template registry
    Exception: Any exceptions raised by the Jinja2 template rendering process

## State Changes:
    Attributes READ:
    - self.content: Accesses content dictionary containing body, footer, and style components
    - self.content["body"]: Accesses the body component's content structure
    - self.content["body"].content["items"]: Accesses the list of items in the body section

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain a "body" key with a content structure that has "items" 
    - Each item in self.content["body"].content["items"] must have "name" and "anchor_id" attributes
    - The "report.html" template must be available in the template registry
    - All items in body content must be properly initialized with name and anchor_id properties

    Postconditions:
    - Returns a complete HTML string representing the report with navigation structure
    - Navigation items are properly extracted from body content sections
    - Template rendering completes successfully with all required context variables

## Side Effects:
    Template rendering side effects (Jinja2 template engine operations)
    Potential I/O operations during template loading if templates are loaded from filesystem

