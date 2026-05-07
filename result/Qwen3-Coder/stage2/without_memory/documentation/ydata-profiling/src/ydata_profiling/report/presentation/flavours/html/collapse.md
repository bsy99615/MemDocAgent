# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse` · *class*

## Summary:
HTMLCollapse is a presentation component that renders collapsible UI elements in HTML format.

## Description:
HTMLCollapse implements the HTML rendering for collapsible sections in data profiling reports. It extends the abstract Collapse class to provide concrete HTML implementation using Jinja2 templates. This component is typically used to create interactive collapsible sections that can be expanded or collapsed by users in web-based data profiling dashboards.

The class is instantiated with a ToggleButton and a content item, and renders them as an HTML collapsible element using a predefined template.

## State:
- `content`: dict containing "button" (ToggleButton instance) and "item" (Renderable instance) keys
- The content dictionary is inherited from the parent Renderable class
- The button and item are stored in the content dictionary and accessed via template rendering

## Lifecycle:
- Creation: Instantiate with a ToggleButton and Renderable item
- Usage: Call render() method to generate HTML string representation
- Destruction: No special cleanup required as it's a simple data container

## Method Map:
```mermaid
graph TD
    A[HTMLCollapse] --> B[render]
    B --> C[templates.template("collapse.html")]
    C --> D[Template Rendering]
    D --> E[self.content]
```

## Raises:
- No explicit exceptions raised by __init__
- Template rendering may raise Jinja2 template-related exceptions if template is missing or malformed

## Example:
```python
from ydata_profiling.report.presentation.core import ToggleButton
from ydata_profiling.report.presentation.flavours.html.collapse import HTMLCollapse

# Create a toggle button
button = ToggleButton("Click me")

# Create a content item (assumed to exist)
content_item = SomeRenderable()

# Create collapse component
collapse = HTMLCollapse(button, content_item)

# Render to HTML
html_output = collapse.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse.render` · *method*

## Summary:
Renders a collapsible HTML component using a Jinja2 template.

## Description:
This method generates HTML markup for a collapsible UI element by rendering the 'collapse.html' template with the content stored in self.content. The content contains a button and an item that will be displayed when collapsed. This method is part of the HTML presentation flavour implementation for ydata profiling reports and provides a standardized way to render collapsible sections in HTML reports.

The method exists as a separate implementation because it encapsulates the specific HTML rendering logic for collapsible components, allowing for consistent presentation across different report sections while maintaining clean separation between data structure and presentation logic.

## Args:
    None

## Returns:
    str: HTML string representation of the collapsible component containing a button and associated content

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing at least "button" and "item" keys
    - The 'collapse.html' template must exist in the templates directory
    - The template variables must match the structure expected by collapse.html template
    
    Postconditions:
    - Returns a properly formatted HTML string for a collapsible component with button and content

## Side Effects:
    None

