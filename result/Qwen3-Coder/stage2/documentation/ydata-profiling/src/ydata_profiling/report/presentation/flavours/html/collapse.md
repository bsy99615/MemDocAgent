# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse` · *class*

## Summary:
HTMLCollapse renders a collapsible UI component as HTML using a Jinja2 template.

## Description:
The HTMLCollapse class is an HTML presentation implementation of the abstract Collapse UI component. It transforms a collapsible interface element (consisting of a toggle button and content item) into its HTML representation. This class is part of the HTML presentation flavour and is responsible for generating the appropriate HTML markup for collapsible sections in reports.

The class is typically instantiated by the HTML presentation layer when converting Collapse components to their HTML representation. It leverages Jinja2 templating to generate the final HTML output.

## State:
- Inherits all attributes from Collapse parent class:
  - button: ToggleButton instance that controls the collapse state
  - item: Renderable instance that gets shown/hidden when the collapse is toggled
  - content: Dictionary containing the button and item components
  - item_type: String identifier set to "collapse" indicating this is a collapse component

## Lifecycle:
- Creation: Instantiated with a Collapse object (typically created via Collapse constructor or convert_to_class method)
- Usage: Call render() method to generate HTML string representation
- Destruction: No explicit cleanup required as it inherits from Renderable

## Method Map:
```mermaid
graph TD
    A[HTMLCollapse.render] --> B[templates.template("collapse.html")]
    B --> C[template.render(**self.content)]
```

## Raises:
- None explicitly documented, but inherits any exceptions from parent Collapse class

## Example:
```python
# Assuming a Collapse object exists with proper button and item components
collapse_component = Collapse(toggle_button, content_item)
html_collapse = HTMLCollapse(collapse_component)
html_output = html_collapse.render()  # Returns HTML string
```

### `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse.render` · *method*

## Summary:
Renders the HTML representation of a collapsible component using a Jinja2 template.

## Description:
This method generates the HTML markup for a collapsible UI element by rendering the 'collapse.html' template with the component's content data. It transforms the internal representation of the collapsible component into a complete HTML string that can be embedded in web reports.

The method is part of the HTML presentation flavour implementation for collapsible components, providing the concrete rendering logic that was abstract in the parent Collapse class. It specifically renders the collapse component by unpacking its content dictionary and passing it to the Jinja2 template engine.

## Args:
    None

## Returns:
    str: A complete HTML string representing the collapsible component with its toggle button and content item.

## Raises:
    jinja2.exceptions.TemplateNotFound: If the 'collapse.html' template file is not found in the template directory
    jinja2.exceptions.UndefinedError: If the template tries to access undefined variables from self.content
    AttributeError: If self.content is not properly initialized as a dictionary

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing the button and item components that will be passed to the template
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing the necessary data for the collapse.html template
    - The 'collapse.html' template must exist in the template directory
    - self.content should contain keys expected by the collapse.html template (typically 'button' and 'item')
    Postconditions:
    - Returns a properly formatted HTML string that represents the collapsible component

## Side Effects:
    None directly, but relies on the global jinja2 environment for template resolution and rendering

