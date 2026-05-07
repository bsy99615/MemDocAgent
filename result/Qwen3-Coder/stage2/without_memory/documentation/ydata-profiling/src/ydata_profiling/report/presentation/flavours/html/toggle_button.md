# `toggle_button.py`

## `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton` · *class*

## Summary:
HTMLToggleButton is a presentation layer component that renders toggle button UI elements using HTML templates.

## Description:
This class implements the HTML rendering for toggle buttons in the ydata-profiling report generation system. It extends the abstract ToggleButton class and provides concrete HTML rendering functionality by utilizing Jinja2 templates. The component is typically instantiated by report generation logic when creating interactive UI elements for data profiling reports.

## State:
- `content` (dict): Inherited from Renderable base class, contains the data needed for template rendering including the button text and other properties
- `item_type` (str): Inherited from ItemRenderer, set to "toggle_button" string
- `name` (Optional[str]): Inherited from Renderable, optional identifier for the component
- `anchor_id` (Optional[str]): Inherited from Renderable, optional anchor identifier for HTML linking
- `classes` (Optional[str]): Inherited from Renderable, optional CSS classes for styling

The `content` dictionary must contain at least a "text" key as required by the ToggleButton parent class constructor.

## Lifecycle:
- Creation: Instantiate with a text parameter and optional keyword arguments for name, anchor_id, and classes
- Usage: Call the `render()` method to generate HTML output
- Destruction: No special cleanup required; uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLToggleButton.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Renderable.render]
    D --> E[HTMLToggleButton.render]
    E --> F[templates.template("toggle_button.html").render]
```

## Raises:
- None explicitly raised by the constructor
- The render method may raise TemplateNotFound or other template-related exceptions if the "toggle_button.html" template is missing

## Example:
```python
# Create a toggle button
button = HTMLToggleButton("Show Details")

# Render to HTML
html_output = button.render()
# Returns rendered HTML string using the toggle_button.html template
```

### `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton.render` · *method*

## Summary:
Renders the toggle button as an HTML string using a Jinja2 template.

## Description:
This method implements the abstract render method from ToggleButton to generate HTML markup for a toggle button component. It leverages the Jinja2 templating engine to process the button's content data and return the resulting HTML string.

## Args:
    None

## Returns:
    str: An HTML string representation of the toggle button component

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary-like object that can be unpacked with **kwargs
    - The "toggle_button.html" template must exist in the template directory
    - The Jinja2 environment must be properly initialized
    
    Postconditions:
    - Returns a valid HTML string
    - Does not modify the instance state

## Side Effects:
    None

