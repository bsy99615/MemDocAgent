# `image.py`

## `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage` · *class*

## Summary:
Represents an HTML-specific implementation for rendering image elements in profiling reports.

## Description:
The HTMLImage class is a concrete implementation of the Image renderer that specializes in generating HTML markup for image elements. It extends the base Image class and implements the render method to produce HTML output using Jinja2 templates. This class is part of the HTML presentation flavour and is responsible for converting image data into HTML-renderable format suitable for web-based profiling reports.

The class is typically instantiated by the report generation system when creating HTML representations of image elements such as charts, graphs, or other visualizations within profiling reports.

## State:
- Inherits all state from the parent Image class including:
  - `image` (str): Path or URL to the image resource
  - `image_format` (ImageType): Format of the image (svg or png)
  - `alt` (str): Alternative text describing the image for accessibility
  - `caption` (Optional[str]): Optional caption text for the image
  - `item_type` (str): String identifier set to "image" by constructor
  - `content` (dict): Dictionary containing all image metadata including image path, format, alt text, and caption
- Inherits content dictionary from Renderable base class containing all rendering data

## Lifecycle:
- Creation: Instantiated with image path/URL, format, and alt text; caption is optional, inherits from Image parent class
- Usage: Called by the HTML presentation layer during report generation when rendering image elements
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph LR
    A[HTMLImage.render()] --> B[templates.template("diagram.html")]
    B --> C[jinja2.Template.render()]
    C --> D[HTML output string]
```

## Raises:
- ValueError: Inherited from parent Image class when the image parameter is None
- TemplateNotFound: Potentially raised by jinja2.template() if "diagram.html" template is not found
- UndefinedError: Potentially raised by jinja2.render() if required variables are missing from content

## Example:
```python
from ydata_profiling.config import ImageType
from ydata_profiling.report.presentation.core.image import Image
from ydata_profiling.report.presentation.flavours.html.image import HTMLImage

# Create an HTML image element for a report
html_img = HTMLImage(
    image="path/to/chart.svg",
    image_format=ImageType.svg,
    alt="Distribution chart of age variable",
    caption="Figure 1: Age distribution histogram"
)

# Render the HTML output
html_output = html_img.render()
# Returns HTML string using diagram.html template with image data
```

### `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage.render` · *method*

## Summary:
Renders an HTML representation of an image element using the diagram.html Jinja2 template.

## Description:
This method generates HTML markup for displaying an image within a profiling report by rendering the diagram.html template with the image's content data. It's part of the HTML presentation flavour implementation for image elements, providing a concrete implementation of the abstract render method from the base Image class.

The method leverages the Jinja2 templating system to dynamically generate HTML content based on the image metadata stored in the content attribute. This approach allows for flexible presentation of image elements while maintaining consistency with the overall report generation architecture.

Known callers:
- Report generation pipeline during HTML report construction
- Presentation layer rendering components when processing image elements
- Template-based rendering systems that require HTML output for image display

This logic is separated into its own method to enable clean separation between the data representation (Image class) and its HTML presentation format, supporting the MVC pattern where the model (Image) is separate from the view (HTML rendering).

## Args:
    None: This method does not accept any parameters beyond the implicit self reference.

## Returns:
    str: A string containing the rendered HTML markup for the image element.

## Raises:
    jinja2.exceptions.TemplateNotFound: If the diagram.html template cannot be located
    jinja2.exceptions.UndefinedError: If required variables from self.content are missing in the template
    AttributeError: If self.content is not properly initialized or is not a dictionary

## State Changes:
    Attributes READ:
    - self.content: Dictionary containing image metadata (image path, format, alt text, caption) used for template rendering
    Attributes WRITTEN:
    - None: This method does not modify any instance attributes.

## Constraints:
    Preconditions:
    - The self.content attribute must be a dictionary containing valid keys expected by the diagram.html template
    - The diagram.html template must exist in the template directory
    - The jinja2 environment must be properly configured
    - The content dictionary should contain required keys such as image path, alt text, and potentially caption

    Postconditions:
    - The returned string contains valid HTML markup for the image element
    - The content dictionary remains unchanged after the call

## Side Effects:
    None: This method performs no I/O operations or external service calls beyond template rendering.

