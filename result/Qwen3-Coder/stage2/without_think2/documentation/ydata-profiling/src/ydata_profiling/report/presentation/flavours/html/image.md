# `image.py`

## `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage` · *class*

## Summary:
HTMLImage is a concrete implementation of the Image component that renders image data as HTML markup using Jinja2 templating.

## Description:
The HTMLImage class serves as the HTML-specific renderer for image components within the ydata-profiling reporting framework. It inherits from the core Image class and implements the render method to produce HTML-formatted output using the Jinja2 templating engine. This class is responsible for transforming image component data into properly structured HTML that can be embedded in web-based reports.

The class is typically instantiated automatically by the reporting system when generating HTML reports containing image components. It leverages the "diagram.html" template to ensure consistent HTML structure and styling for all rendered images. The implementation maintains the image data integrity by passing all content from the parent Image component directly to the template engine.

## State:
- Inherits all state from the parent Image class including image path, format, alternative text, and caption
- The content dictionary contains all image metadata including image, image_format, alt, and caption
- The item_type is inherited as "image" from the parent class
- Inherits content dictionary from Renderable parent class which stores component data and metadata
- Properties name, anchor_id, and classes are accessible from the parent Renderable class but are not directly used in this implementation

## Lifecycle:
- Creation: Instantiated with standard Image constructor parameters (image path, format, alt text, optional caption)
- Usage: Called during HTML report generation when the render() method is invoked on image components
- Destruction: Managed by Python garbage collection; no explicit cleanup required

## Method Map:
```mermaid
flowchart TD
    A[HTMLImage.render] --> B[templates.template("diagram.html")]
    B --> C[Jinja2 Template Rendering]
    C --> D[HTML String Output]
```

## Raises:
- No explicit exceptions raised by the render method
- Exceptions may occur during template rendering if the "diagram.html" template is missing or if content data is invalid
- The parent Image class initialization may raise ValueError if required parameters are missing
- KeyError may be raised when accessing properties from the content dictionary if keys are not present (inherited from Renderable)

## Example:
```python
# Create an HTML image component
html_image = HTMLImage(
    image="path/to/chart.png",
    image_format=ImageType.PNG,
    alt="Distribution chart of age variable"
)

# Render to HTML
html_output = html_image.render()
# Returns HTML string using diagram.html template
```

### `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage.render` · *method*

## Summary:
Renders an HTML representation of an image component using a Jinja2 template.

## Description:
The render method implements the HTML-specific rendering logic for image components by utilizing the Jinja2 templating engine. This method takes the image component's content data and renders it into a properly formatted HTML string using the "diagram.html" template. The method serves as the concrete implementation of the abstract render method inherited from the parent Image class, specifically tailored for HTML output format.

This method is called during the report generation pipeline when HTML-formatted content needs to be produced. It's part of the HTML presentation flavour implementation and is invoked by the reporting system when processing image components within HTML reports. The method delegates the actual rendering to the Jinja2 template system, passing all content data as keyword arguments.

The "diagram.html" template is responsible for structuring the HTML output to display image components properly within the generated reports. It expects the content dictionary from the image component to contain appropriate keys that map to HTML elements such as image source, alternative text, and formatting attributes.

## Args:
    None

## Returns:
    str: A string containing the HTML-rendered representation of the image component

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The self.content attribute must be a dictionary containing valid keys expected by the "diagram.html" template
    - The "diagram.html" template must be available in the Jinja2 environment
    - The parent Image class must have been properly initialized with valid content

    Postconditions:
    - Returns a valid HTML string representation of the image
    - The returned string follows the structure defined by the "diagram.html" template

## Side Effects:
    None

