# `toggle_button.py`

## `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton` · *class*

## Summary:
HTMLToggleButton is a concrete implementation of ToggleButton that renders interactive toggle buttons as HTML elements for use in web-based data profiling reports.

## Description:
HTMLToggleButton specializes the generic ToggleButton component for HTML presentation by implementing the render method to generate HTML markup using Jinja2 templates. This class enables interactive report elements that allow users to toggle visibility of report sections or filter content. It serves as a bridge between the abstract toggle button concept and its concrete HTML representation in the ydata profiling report system.

The component is typically instantiated by report generation systems when creating interactive elements for web-based data profiling reports. It leverages the parent ToggleButton's functionality for managing button state and metadata while providing HTML-specific rendering capabilities.

## State:
- content: dict - Contains the template context data including the button text and other metadata inherited from the parent ToggleButton class. This dictionary is passed directly to the Jinja2 template during rendering.
- text: str - The label text displayed on the toggle button, inherited from ToggleButton parent class
- item_type: str - Set to "toggle_button" by parent class, identifies this component type in the rendering system
- name: Optional[str] - Human-readable identifier for the button, inherited from parent class
- anchor_id: Optional[str] - Unique identifier for HTML anchors, inherited from parent class
- classes: Optional[str] - CSS classes for styling, inherited from parent class

## Lifecycle:
- Creation: Instantiate with text parameter and optional keyword arguments for name, anchor_id, and classes, inheriting all parameters from ToggleButton parent class
- Usage: Called by HTML presentation engines during report generation when rendering toggle button components
- Destruction: Standard Python object lifecycle management; no special cleanup required

## Method Map:
```mermaid
graph TD
    A[HTMLToggleButton.__init__] --> B[ToggleButton.__init__]
    B --> C[ItemRenderer.__init__]
    C --> D[content = {"text": text, ...}]
    D --> E[HTMLToggleButton.render()]
    E --> F[templates.template("toggle_button.html")]
    F --> G[Template.render(**self.content)]
    G --> H[HTML string output]
```

## Raises:
- jinja2.TemplateNotFound: When the "toggle_button.html" template is not found in the Jinja2 environment
- AttributeError: If self.content does not contain required keys expected by the template
- TypeError: If the template rendering fails due to incompatible data types in self.content

## Example:
```python
# Create a toggle button for report sections
toggle_button = HTMLToggleButton("Show Details", name="details_toggle")

# Render the HTML for inclusion in a report
html_output = toggle_button.render()

# Typical output would be HTML like:
# <button class="toggle-button" data-name="details_toggle">Show Details</button>
```

### `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton.render` · *method*

## Summary:
Renders the toggle button component as an HTML string using a Jinja2 template.

## Description:
This method implements the HTML rendering logic for toggle button components. It retrieves the "toggle_button.html" template from the global template environment and renders it with the content data stored in the component's content attribute. This method is part of the HTML presentation flavour implementation for toggle buttons in the ydata profiling report system.

The method serves as the concrete implementation of the abstract render() method required by the ItemRenderer base class, specifically tailored for HTML output generation. It leverages the Jinja2 templating system to produce structured HTML markup for toggle buttons that can be embedded in interactive reports.

## Args:
    None - This method takes no parameters beyond the implicit self reference.

## Returns:
    str - A string containing the rendered HTML markup for the toggle button component.

## Raises:
    jinja2.TemplateNotFound - When the "toggle_button.html" template is not found in the Jinja2 environment.
    TypeError - When self.content is not a dictionary or contains incompatible data types for template rendering.
    KeyError - When required keys are missing from self.content that are expected by the template.

## State Changes:
    Attributes READ:
        - self.content: Dictionary containing the data and metadata needed for template rendering
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The global Jinja2 template environment must be properly initialized
        - The "toggle_button.html" template must exist in the template directory
        - self.content must be a dictionary containing the required data structure expected by the template
    Postconditions:
        - Returns a valid HTML string representation of the toggle button
        - Does not modify the instance state

## Side Effects:
    None - This method is pure and has no side effects beyond template rendering.

