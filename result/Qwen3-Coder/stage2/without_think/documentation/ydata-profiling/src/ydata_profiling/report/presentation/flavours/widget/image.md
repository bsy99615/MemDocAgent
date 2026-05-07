# `image.py`

## `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage` · *class*

## Summary:
WidgetImage is a presentation layer component that renders image elements as interactive Jupyter widgets for display in notebook environments.

## Description:
The WidgetImage class provides a concrete implementation of the abstract Image renderer specifically designed for Jupyter notebook environments using ipywidgets. It transforms image metadata into interactive HTML widgets that can be displayed directly in Jupyter notebooks. This class is part of the widget-based presentation flavour and is responsible for converting image data into widget representations suitable for interactive data exploration.

The class handles two main image formats differently: SVG images (which receive special styling and size adjustments) and raster images (which are converted to standard HTML img tags). It also supports optional captions that appear below the image with styled formatting.

## State:
- Inherits all state from the parent Image class including:
  - `content` (dict): Dictionary containing image metadata with keys:
    - `image` (str): Path or URL to the image resource
    - `image_format` (ImageType): Format indicator (svg or other formats)
    - `alt` (str): Alternative text for accessibility
    - `caption` (Optional[str]): Caption text for the image
- No additional instance attributes beyond inherited ones

## Lifecycle:
- Creation: Instantiated with standard Image constructor parameters (image path/URL, format, alt text, optional caption)
- Usage: Called by presentation layer components during report rendering when widget output is required via the render() method
- Destruction: Managed by Python's garbage collection; no explicit cleanup needed

## Method Map:
```mermaid
flowchart TD
    A[WidgetImage.render()] --> B[Extract image content from self.content]
    B --> C{Is SVG format?}
    C -->|Yes| D[Apply max-width styling to SVG]
    C -->|No| E[Create img HTML tag with src and alt attributes]
    D --> F[Create HTML widget]
    E --> F
    F --> G{Has caption?}
    G -->|Yes| H[Wrap in VBox with styled caption]
    G -->|No| I[Return HTML widget directly]
```

## Raises:
- No explicit exceptions raised by WidgetImage.__init__ (inherits from Image class)
- May raise exceptions from parent class initialization if invalid parameters are provided
- Potential runtime errors if image content is malformed or inaccessible

## Example:
```python
from ydata_profiling.config import ImageType
from ydata_profiling.report.presentation.flavours.widget.image import WidgetImage

# Create a widget image with SVG content
svg_image = WidgetImage(
    image="<svg width='300' height='200'>...</svg>",
    image_format=ImageType.svg,
    alt="Sample SVG chart showing distribution",
    caption="Figure 1: Distribution of values in dataset"
)

# Render the widget for display in Jupyter
widget = svg_image.render()

# Create a widget image with PNG content
png_image = WidgetImage(
    image="https://example.com/chart.png",
    image_format=ImageType.png,
    alt="Sample PNG chart showing trends"
)

# Render the widget for display in Jupyter
widget = png_image.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage.render` · *method*

## Summary:
Converts image content into an interactive ipywidgets.Widget for display in Jupyter environments.

## Description:
Transforms image data into a widget representation suitable for Jupyter notebook displays. This method processes SVG and raster images differently, applies responsive styling to SVGs, and optionally adds captions. The method is part of the widget-based presentation flavour for ydata-profiling reports.

## Args:
    None - This is a method of the WidgetImage class that operates on self.content

## Returns:
    widgets.Widget: Either a widgets.HTML widget containing the image, or a widgets.VBox containing both the image widget and caption widget when a caption is provided

## Raises:
    None - The method doesn't explicitly raise exceptions, though underlying widget creation may raise errors from ipywidgets

## State Changes:
    Attributes READ: 
    - self.content["image"] - The image source data (SVG content or image URL/path)
    - self.content["image_format"] - The format of the image (ImageType.svg or other)
    - self.content["alt"] - Alternative text for accessibility (for non-SVG images)
    - self.content["caption"] - Optional caption text for the image
    
    Attributes WRITTEN: None - This method is read-only and doesn't modify object state

## Constraints:
    Preconditions:
    - self.content must contain "image" key with valid image data
    - self.content must contain "image_format" key with valid ImageType value
    - For non-SVG images, self.content must contain "alt" key
    - self.content["image"] must not be None
    - self.content["image_format"] must be a valid ImageType enum value
    
    Postconditions:
    - Returns a valid ipywidgets.Widget object
    - If caption is present and not None, returns a widgets.VBox containing image and caption widgets
    - If no caption, returns just the image widget
    - SVG images receive responsive styling (max-width: 100% and height attribute removal)
    - Non-SVG images are wrapped in img tags with src and alt attributes

## Side Effects:
    None - This method performs no I/O operations or external service calls

