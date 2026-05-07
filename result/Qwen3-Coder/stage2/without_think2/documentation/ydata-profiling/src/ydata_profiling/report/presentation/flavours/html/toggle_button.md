# `toggle_button.py`

## `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton` · *class*

## Summary:
HTMLToggleButton is a concrete implementation of the ToggleButton class that renders toggle button components as HTML markup.

## Description:
This class specializes the abstract ToggleButton interface for HTML output format. It provides the specific rendering logic needed to convert toggle button data into HTML-compatible markup. The component is designed to be used within the ydata-profiling report generation pipeline where interactive toggle buttons are required in HTML reports.

The class leverages Jinja2 templating to generate consistent HTML structure while allowing customization through the content dictionary. It serves as a bridge between the abstract report item model and its HTML presentation layer.

## State:
- content: dict - Dictionary containing the toggle button's configuration including text label and other properties. Required field. The dictionary must contain at least a "text" key for the button label, and may include additional keys expected by the "toggle_button.html" template.
- item_type: str - Class attribute set to "toggle_button" by parent class, identifying this as a toggle button item type.
- name: Optional[str] - Human-readable identifier for the item, stored in content dictionary.
- anchor_id: Optional[str] - Unique identifier for HTML anchors, stored in content dictionary.
- classes: Optional[str] - CSS classes to apply to the rendered item, stored in content dictionary.

## Lifecycle:
- Creation: Instantiate with required text parameter and optional metadata (name, anchor_id, classes) through parent class constructor
- Usage: Call render() method to generate HTML output; typically invoked during HTML report generation
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLToggleButton.__init__] --> B[ToggleButton.__init__]
    B --> C[ItemRenderer.__init__]
    C --> D[render()]
    D --> E[templates.template("toggle_button.html")]
    E --> F[template.render(**self.content)]
```

## Raises:
- jinja2.TemplateNotFound: When the "toggle_button.html" template cannot be found in the Jinja2 environment

## Example:
```python
# Create a toggle button instance
button = HTMLToggleButton(
    text="Show Details",
    name="details-toggle",
    anchor_id="toggle-anchor"
)

# Render to HTML
html_output = button.render()
# Returns HTML string with toggle button structure
```

### `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton.render` · *method*

## Summary:
Renders an HTML toggle button component by processing the button's content through a Jinja2 template.

## Description:
This method implements the HTML-specific rendering logic for toggle button components. It retrieves the predefined "toggle_button.html" template and renders it using the button's content dictionary as context data. The method serves as the concrete implementation of the abstract render() method defined in the parent ToggleButton class, specifically tailored for HTML output format.

The render method is invoked during the HTML report generation pipeline when a toggle button component needs to be converted into its HTML representation. This allows for consistent, reusable HTML structure while maintaining flexibility in the button's content and styling through the content dictionary.

## Args:
    None

## Returns:
    str: A string containing the HTML-rendered toggle button component, with the button's text content properly inserted into the template structure.

## Raises:
    jinja2.TemplateNotFound: When the "toggle_button.html" template cannot be found in the Jinja2 environment.

## State Changes:
    Attributes READ: 
        - self.content: Dictionary containing the button's configuration including text label and other properties
    Attributes WRITTEN: 
        - None

## Constraints:
    Preconditions:
        - The HTMLToggleButton instance must have a properly initialized content dictionary
        - The Jinja2 template environment must be properly configured with the "toggle_button.html" template
        - The content dictionary must contain all required variables expected by the template
    Postconditions:
        - Returns a valid HTML string representing the toggle button
        - The returned HTML maintains proper semantic structure for the toggle button component

## Side Effects:
    None

