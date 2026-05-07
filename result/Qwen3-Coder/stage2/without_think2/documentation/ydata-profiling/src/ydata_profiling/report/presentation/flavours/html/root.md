# `root.py`

## `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot` · *class*

## Summary:
HTMLRoot is a concrete implementation of the Root class that renders report content as HTML using Jinja2 templating.

## Description:
HTMLRoot serves as the HTML-specific renderer for report structures, inheriting from the abstract Root class. It implements the render() method to generate complete HTML reports by processing report sections into navigation items and combining them with the full report content using a Jinja2 template. This class is responsible for the final transformation of structured report data into HTML format for web presentation.

The class is typically instantiated by the report generation pipeline when HTML output is required. It enforces the responsibility boundary of HTML-specific rendering while maintaining the structural integrity of the report hierarchy defined by its parent Root class.

## State:
- content: dict - Contains the complete report structure with keys "body", "footer", and "style"
- item_type: str - Inherited from Root, set to "report" to identify this as a report container
- name: str - Optional identifier for the report, stored in content dictionary
- anchor_id: str - Optional unique identifier for HTML anchors, stored in content dictionary  
- classes: str - Optional CSS classes for the rendered report, stored in content dictionary

## Lifecycle:
- Creation: Instantiate with name (str), body (Renderable), footer (Renderable), style (Style), and optional metadata parameters. The constructor inherits from Root and sets up the content structure.
- Usage: Called during report generation when HTML output is needed. The render() method extracts navigation items from report sections and renders the complete HTML using templates.template("report.html").
- Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[HTMLRoot.render] --> B[Extract nav_items]
    B --> C[Process self.content["body"].content["items"]]
    C --> D[Call templates.template("report.html").render()]
    D --> E[Return HTML string]
```

## Raises:
- None explicitly raised by this class's render() method
- However, underlying template rendering may raise exceptions from jinja2 or template loading

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.core.renderable import Renderable
from ydata_profiling.report.presentation.flavours.html.root import HTMLRoot

# Create report components
style = Style()
body = Renderable({"content": "Main report content"})
footer = Renderable({"content": "Report footer"})

# Create HTML root container
html_root = HTMLRoot(
    name="My Report",
    body=body,
    footer=footer,
    style=style
)

# Render to HTML
html_output = html_root.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot.render` · *method*

## Summary:
Renders the HTML report by generating navigation items and combining them with report content using a Jinja2 template.

## Description:
This method constructs navigation items from report sections and renders the complete HTML report using the 'report.html' Jinja2 template. It processes the body content to extract section information for navigation and combines it with the full report content and additional keyword arguments.

The method is part of the HTML root renderer implementation and is called during the report generation pipeline when converting the report structure to HTML format. It serves as the concrete implementation of the abstract render() method inherited from Root, overriding the base implementation that raises NotImplementedError.

Known callers include the report generation pipeline components that require HTML output. This logic is separated into its own method to encapsulate the HTML rendering concerns and maintain clean separation between data structure management and presentation logic.

## Args:
    **kwargs: Arbitrary keyword arguments passed through to the Jinja2 template rendering process

## Returns:
    str: The complete HTML-rendered report as a string

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: self.content, self.content["body"], self.content["body"].content["items"]
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing a "body" key with a content structure
    - self.content["body"] must have a content attribute with an "items" key
    - Each item in self.content["body"].content["items"] must have "name" and "anchor_id" attributes
    - templates.template("report.html") must successfully retrieve the Jinja2 template

    Postconditions:
    - Returns a properly formatted HTML string representing the complete report
    - Navigation items are correctly extracted from report sections

## Side Effects:
    I/O: Calls templates.template() which likely performs file system operations to load the template
    Template rendering: Invokes Jinja2 template engine which may perform additional I/O operations

