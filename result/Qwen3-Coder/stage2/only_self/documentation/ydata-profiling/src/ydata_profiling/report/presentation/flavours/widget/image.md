# `image.py`

## `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage` · *class*

## Summary:
WidgetImage is a presentation layer component that renders image elements as interactive Jupyter widgets, specifically designed for use in Jupyter notebook environments.

## Description:
The WidgetImage class serves as a concrete implementation of the abstract Image class within the ydata-profiling report presentation system. It transforms image metadata into interactive ipywidgets.Widget objects that can be displayed in Jupyter notebooks. This class is particularly useful for creating dynamic, interactive reports where images need to be rendered with proper styling and optional captions.

The class handles two main image formats differently: SVG images (which receive special styling for responsive display and have height attributes removed) and raster images (which are rendered with appropriate HTML img tags). It also supports optional captions that appear below the image with styled text.

## State:
- Inherits all attributes from the parent Image class including:
  - image: str - Path or URL to the image resource
  - image_format: ImageType - Format of the image (PNG, JPEG, SVG, etc.)
  - alt: str - Alternative text for accessibility purposes
  - caption: Optional[str] - Optional caption text for the image
  - item_type: str - Fixed value "image" indicating the type of presentation element
  - content: dict - Dictionary containing all image metadata including image, image_format, alt, and caption

## Lifecycle:
- Creation: Instantiate with image path/URL, image format, and alternative text. Caption is optional.
- Usage: Call render() method to generate a widgets.Widget object for display in Jupyter notebooks
- Destruction: Managed by Python's garbage collection when no longer referenced

## Method Map:
```mermaid
flowchart TD
    A[WidgetImage.render] --> B[Extract image content from self.content]
    B --> C[Check image_format in self.content]
    C --> D{image_format equals ImageType.SVG?}
    D -->|Yes| E[Replace "svg " with "svg style=\"max-width: 100%\" "]
    E --> F[Remove height attributes using regex]
    D -->|No| G[Create img HTML tag with src and alt attributes]
    F --> H[Create widgets.HTML with processed SVG]
    G --> H
    H --> I[Check for caption in self.content]
    I --> J{caption exists and is not None?}
    J -->|Yes| K[Create caption widget with styled em text]
    K --> L[Wrap widget and caption in widgets.VBox]
    J -->|No| M[Return widget directly]
    L --> N[Return widgets.VBox]
    M --> N
```

## Raises:
- No explicit exceptions raised by __init__ (inherited from parent class)
- The render method may raise exceptions from ipywidgets.HTML or ipywidgets.VBox construction if invalid parameters are passed

## Example:
```python
from ydata_profiling.config import ImageType
from ydata_profiling.report.presentation.flavours.widget.image import WidgetImage

# Create an SVG image with caption
svg_image = WidgetImage(
    image="<svg>...</svg>",
    image_format=ImageType.SVG,
    alt="Interactive chart",
    caption="Figure 1: Interactive visualization"
)

# Render the widget for display in Jupyter
widget = svg_image.render()

# Create a PNG image without caption
png_image = WidgetImage(
    image="https://example.com/chart.png",
    image_format=ImageType.PNG,
    alt="Static chart"
)

# Render the widget for display in Jupyter
widget = png_image.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage.render` · *method*

## Summary:
Renders an image widget for display in Jupyter environments with appropriate formatting and optional caption support.

## Description:
Converts image content into a Jupyter widgets HTML widget, applying specific formatting for SVG images and standard HTML img tags for other formats. The method handles optional captions by wrapping the image in a VBox container with styled caption text.

This method is specifically designed for the widget presentation flavour of ydata-profiling reports, converting image data into interactive Jupyter widgets that maintain proper sizing and accessibility features.

## Args:
    None

## Returns:
    widgets.Widget: A Jupyter widgets HTML widget containing the formatted image. For images with captions, returns a VBox containing both the image and caption widgets; for images without captions, returns just the image widget.

## Raises:
    KeyError: When self.content does not contain required keys "image", "image_format", or "alt" (for non-SVG images)

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain keys "image" and "image_format"
    - For non-SVG images, self.content must contain key "alt"
    - self.content["image_format"] must be a valid ImageType enum value
    - The image content must be properly formatted HTML for the respective image type
    
    Postconditions:
    - Returns a valid ipywidgets.Widget object
    - SVG images have max-width: 100% styling applied and height attributes removed
    - Non-SVG images are wrapped in proper HTML img tags with src and alt attributes
    - Caption styling follows color #999 with italic formatting
    - If caption is present and not None, returns VBox with image and caption widgets

## Side Effects:
    None

