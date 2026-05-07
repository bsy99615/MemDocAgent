# `image.py`

## `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage` · *class*

## Summary:
HTMLImage is a presentation layer component that renders image content using HTML templates.

## Description:
HTMLImage is responsible for generating HTML representations of image data within the ydata-profiling report generation system. It extends the core Image class to provide HTML-specific rendering capabilities by utilizing Jinja2 templates. This class serves as a concrete implementation of the abstract render() method defined in the base Renderable class.

The component is typically instantiated by report generation processes when image content needs to be displayed in HTML reports. It leverages the parent class's initialization to store image metadata and content, then transforms this data into HTML markup using a predefined template.

## State:
- content: dict - Contains image-related data including "image", "image_format", "alt", and "caption" keys. This dictionary is inherited from the parent Renderable class and populated during initialization by the parent Image.__init__ method.
- item_type: str - Set to "image" by the parent Image class constructor, identifying this component type.
- name: str (inherited) - Optional identifier for the image component.
- anchor_id: str (inherited) - Optional anchor identifier for HTML linking.
- classes: str (inherited) - Optional CSS classes for styling.

The content dictionary must contain:
- "image": str - Path or URL to the image resource
- "image_format": ImageType - Format specification for the image
- "alt": str - Alternative text for accessibility
- "caption": str (optional) - Caption text for the image

## Lifecycle:
- Creation: Instances are created by passing image path/URL, image format, and alternative text to the parent Image.__init__ method. The caption parameter is optional.
- Usage: The render() method is called to generate HTML markup. This method internally uses templates.template("diagram.html").render(**self.content) to process the stored content.
- Destruction: No special cleanup is required as this is a simple data container with no resources to manage.

## Method Map:
```mermaid
graph TD
    A[HTMLImage] --> B[Image]
    B --> C[ItemRenderer]
    C --> D[Renderable]
    D --> E{render()}
    E --> F[templates.template("diagram.html").render(**self.content)]
```

## Raises:
- ValueError: Raised by the parent Image.__init__ method when the image parameter is None, with a descriptive message indicating the alt and caption values.

## Example:
```python
# Create an HTMLImage instance
from ydata_profiling.report.presentation.flavours.html.image import HTMLImage
from ydata_profiling.report.presentation.core.image import ImageType

# Assuming we have an image file path and format
image = "path/to/image.png"
image_format = ImageType.PNG
alt_text = "Sample chart visualization"

# Create the HTML image component
html_image = HTMLImage(
    image=image,
    image_format=image_format,
    alt=alt_text,
    caption="Chart showing data distribution"
)

# Render to HTML
html_output = html_image.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage.render` · *method*

## Summary:
Renders an HTML representation of an image using a Jinja2 template.

## Description:
This method implements the HTML-specific rendering logic for image components. It takes the image data stored in `self.content` and renders it using the `diagram.html` template. This method is part of the HTML presentation flavour and is responsible for generating the HTML markup that displays images in web-based reports.

## Args:
    None - This is an instance method that operates on `self`.

## Returns:
    str: A string containing the HTML-rendered representation of the image.

## Raises:
    None explicitly raised - However, underlying template rendering may raise Jinja2 exceptions if template processing fails.

## State Changes:
    Attributes READ: 
    - self.content: Contains the image data including image path, format, alt text, and caption
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - `self.content` must contain valid keys for the template (image, image_format, alt, caption)
    - The `diagram.html` template must exist in the template directory
    - The Jinja2 environment must be properly initialized
    
    Postconditions:
    - Returns a valid HTML string representation of the image
    - Does not modify the instance state

## Side Effects:
    None - This method is pure and does not cause any I/O operations or external service calls. It only processes internal state and returns a string.

