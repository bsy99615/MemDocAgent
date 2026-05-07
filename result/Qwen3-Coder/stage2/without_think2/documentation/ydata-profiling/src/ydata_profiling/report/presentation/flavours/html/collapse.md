# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse` · *class*

## Summary:
HTMLCollapse is a concrete implementation of the Collapse component that generates HTML markup for collapsible UI elements using Jinja2 templating.

## Description:
The HTMLCollapse class provides the HTML-specific rendering behavior for collapsible components by implementing the abstract render() method defined in its parent Collapse class. It extends the Collapse hierarchy to produce HTML output for interactive collapsible sections in profiling reports.

This component follows the template pattern where the actual HTML generation is delegated to a Jinja2 template named "collapse.html". The class inherits all content structure from its parent Collapse class, which contains a button and item that are passed to the template for rendering. The HTMLCollapse class serves as the concrete implementation that bridges the abstract collapsible concept with HTML presentation.

## State:
- Inherits all attributes from Collapse parent class:
  - button: ToggleButton instance that controls the collapse/expand state
  - item: Renderable instance containing the content to be shown/hidden
  - item_type: String identifier set to "collapse" by constructor
  - content: Dictionary containing the button and item, inherited from Renderable parent class
  - name: Optional string identifier, inherited from Renderable parent class
  - anchor_id: Optional string for HTML anchors, inherited from Renderable parent class
  - classes: Optional CSS classes, inherited from Renderable parent class

## Lifecycle:
- Creation: Instantiate with a ToggleButton and Renderable item; optional name, anchor_id, and classes parameters
- Usage: Call render() method to generate HTML output by rendering the "collapse.html" template with the component's content
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLCollapse.render] --> B[templates.template("collapse.html")]
    B --> C[Jinja2 Template Rendering]
    C --> D[HTML Output String]
```

## Raises:
- None explicitly raised by HTMLCollapse.render()
- However, underlying template rendering may raise Jinja2-related exceptions if template structure is invalid or content is missing required keys

## Example:
```python
# Create a toggle button
toggle = ToggleButton("Show Details")

# Create content to be toggled
content = Text("This is hidden content")

# Create collapse component (HTML version)
collapse = HTMLCollapse(toggle, content)

# Generate HTML output
html_output = collapse.render()
# Returns HTML string with collapsible structure using collapse.html template
```

### `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse.render` · *method*

## Summary:
Generates HTML markup for a collapsible UI component by rendering a Jinja2 template with the component's content.

## Description:
This method implements the HTML-specific rendering logic for collapsible components. It takes the stored content dictionary (containing button and item data) and passes it to a Jinja2 template engine to generate the final HTML output. The method is part of the HTML presentation flavour implementation for collapsible components, providing the concrete rendering behavior that was abstracted in the parent Collapse class.

The render method is called during the HTML report generation pipeline when HTML output is being produced. It leverages the Jinja2 templating system to dynamically generate HTML based on the component's content, allowing for flexible and maintainable presentation logic separate from the component's data structure. The method accesses the Jinja2 environment through the templates module to retrieve and render the "collapse.html" template.

## Args:
    None

## Returns:
    str: HTML string containing the rendered collapsible component with its toggle button and associated content

## Raises:
    None

## State Changes:
    - Attributes READ: self.content
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: The self.content dictionary must contain the required keys expected by the "collapse.html" template, specifically 'button' and 'item'
    - Postconditions: The returned HTML string will be properly formatted according to the template specification

## Side Effects:
    - Template lookup and rendering via Jinja2 environment
    - No direct I/O operations or external service calls

