# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse` · *class*

## Summary:
HTMLCollapse represents a collapsible UI component that renders as an HTML element using Jinja2 templating.

## Description:
The HTMLCollapse class implements the HTML presentation layer for collapsible components. It extends the base Collapse class to provide concrete HTML rendering capabilities by utilizing Jinja2 templates. This class is typically instantiated when converting existing Renderable objects to HTML presentation format, particularly for collapsible sections in reports.

The motivation for this distinct abstraction is to separate the logical structure of collapsible components (handled by Collapse) from their HTML presentation rendering (handled by HTMLCollapse). This enables flexible presentation layers while maintaining consistent component behavior across different output formats.

## State:
- Inherits all attributes from Collapse parent class including:
  - button: ToggleButton instance that controls the collapse state
  - item: Renderable instance containing the content that gets collapsed/expanded
  - content: Dictionary containing the button and item components
  - item_type: String identifier set to "collapse" that defines this component type
  - name: Optional string identifier for the component (inherited from Renderable)
  - anchor_id: Optional string for HTML anchor identification (inherited from Renderable)
  - classes: Optional CSS classes for styling (inherited from Renderable)

## Lifecycle:
Creation: Instantiate with a ToggleButton and Renderable object, similar to the parent Collapse class. The HTMLCollapse constructor accepts the same parameters as Collapse.
Usage: The render() method is called during HTML report generation to produce the final HTML markup for the collapsible component.
Destruction: No explicit cleanup required; inherits standard object destruction behavior.

## Method Map:
```mermaid
graph TD
    A[HTMLCollapse Constructor] --> B[Collapse.__init__]
    B --> C[Sets item_type="collapse"]
    C --> D[Stores button and item in content]
    
    E[render] --> F[templates.template("collapse.html")]
    F --> G[template.render(**self.content)]
    G --> H[Returns rendered HTML string]
```

## Raises:
- TemplateNotFound: If the "collapse.html" template is not found in the Jinja2 environment
- UndefinedError: If required variables are missing from self.content when rendering the template

## Example:
```python
# Create a toggle button
toggle_btn = ToggleButton("Show Details")

# Create a content item
content_item = Text("This is collapsible content")

# Create an HTML collapse component
html_collapse = HTMLCollapse(toggle_btn, content_item)

# Render to HTML
html_output = html_collapse.render()
# Returns HTML string with the collapsible structure
```

### `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse.render` · *method*

## Summary:
Renders a collapsible HTML component using the collapse.html template with the component's content data.

## Description:
This method implements the HTML rendering logic for collapsible components by utilizing a Jinja2 template. It takes the pre-structured content from the parent Collapse class and renders it into a complete HTML representation that includes both the toggle button and collapsible content item.

The method is called during the HTML report generation phase when a Collapse component needs to be converted into its HTML presentation form. It's separated from inline logic to maintain clean separation of concerns between data structure and presentation rendering.

## Args:
    None: This method takes no arguments beyond the implicit self parameter.

## Returns:
    str: A string containing the complete HTML markup for the collapsible component, including both the toggle button and the collapsible content area.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying template rendering may raise Jinja2-related exceptions if template processing fails.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing the button and item components that define the collapsible structure
    
    Attributes WRITTEN: 
    - None: This method is read-only and doesn't modify any instance attributes.

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing the required keys for the collapse.html template
    - The collapse.html template must be available in the template environment
    - The template expects specific keys in self.content (typically 'button' and 'item')
    
    Postconditions:
    - The returned string is valid HTML representing a collapsible component
    - The method preserves all data from self.content in the rendered output

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only processes internal data and returns a string.

