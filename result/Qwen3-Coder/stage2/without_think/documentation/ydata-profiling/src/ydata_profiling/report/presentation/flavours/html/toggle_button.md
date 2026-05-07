# `toggle_button.py`

## `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton` · *class*

## Summary:
Represents an HTML implementation of a toggle button UI component for interactive report presentations.

## Description:
The HTMLToggleButton class provides a concrete implementation of a toggle button specifically designed for HTML report generation. It extends the abstract ToggleButton class and implements the render method to produce HTML markup using a Jinja2 template. This component enables interactive functionality in generated HTML reports, allowing users to expand/collapse sections or switch between different views of data presentation.

This class serves as a specialized renderer that bridges the abstract toggle button concept with concrete HTML output, making it suitable for integration into web-based data profiling reports.

## State:
- content: dict - Contains the data needed for rendering the toggle button, including at least a "text" key for the button label as defined by the parent ToggleButton class. Additional keys may be required by the toggle_button.html template.
- name: Optional[str] - Human-readable name for the button, inherited from Renderable
- anchor_id: Optional[str] - Unique identifier for HTML anchors, inherited from Renderable  
- classes: Optional[str] - CSS classes for styling, inherited from Renderable

## Lifecycle:
- Creation: Instantiate with text parameter (required) and optional keyword arguments for name, anchor_id, and classes, following the ToggleButton constructor interface
- Usage: Call render() method to generate HTML string representation of the toggle button
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLToggleButton.render()] --> B[templates.template("toggle_button.html")]
    B --> C[template.render(**self.content)]
    C --> D[HTML string output]
```

## Raises:
- jinja2.TemplateNotFound: When the "toggle_button.html" template is not found in the Jinja2 environment
- KeyError: When self.content does not contain required keys expected by the template
- TypeError: When self.content contains incompatible types for template rendering

## Example:
```python
# Create a toggle button instance
button = HTMLToggleButton(text="Show Details")

# Render to HTML
html_output = button.render()
# Returns HTML string using the toggle_button.html template with button content
```

### `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton.render` · *method*

## Summary:
Renders the toggle button HTML using a Jinja2 template with the button's content data.

## Description:
Generates HTML markup for a toggle button by rendering the "toggle_button.html" template with the button's content data. This method is part of the HTML presentation flavour implementation for toggle buttons in ydata profiling reports.

The method is called during the report generation pipeline when HTML content needs to be rendered for toggle button components. It leverages the Jinja2 templating system to produce properly formatted HTML that can be embedded in larger HTML documents.

## Args:
    None - This is an instance method that operates on self

## Returns:
    str - The rendered HTML string containing the toggle button markup

## Raises:
    jinja2.TemplateNotFound: When the "toggle_button.html" template is not found in the Jinja2 environment
    KeyError: When self.content does not contain required keys expected by the template

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing the button's text content and potentially other properties
    - self.item_type: Inherited from ToggleButton, identifies this as a toggle button type
    - self.name: Inherited from Renderable, human-readable name for the button
    - self.anchor_id: Inherited from Renderable, unique identifier for HTML anchors
    - self.classes: Inherited from Renderable, CSS classes for styling

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing at least the "text" key
    - The global jinja2_env must be properly initialized
    - The "toggle_button.html" template must exist in the Jinja2 environment
    
    Postconditions:
    - Returns a valid HTML string representation of the toggle button
    - Does not modify any instance state

## Side Effects:
    None - This method is pure and has no side effects beyond template rendering

