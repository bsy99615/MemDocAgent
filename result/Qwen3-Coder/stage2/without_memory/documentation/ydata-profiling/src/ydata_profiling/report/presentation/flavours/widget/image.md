# `image.py`

## `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage.render` · *method*

## Summary:
Renders an image widget with optional caption, handling SVG and raster image formats differently.

## Description:
Creates an interactive HTML widget displaying an image with proper formatting based on image type. For SVG images, it applies responsive styling and removes height attributes. For other image formats, it generates standard HTML img tags with alt text. When a caption is provided, it displays the image and caption in a vertical box layout.

## Args:
    None

## Returns:
    widgets.Widget: An ipywidgets.Widget instance containing either a single HTML widget or a VBox containing an image and caption.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content["image"], self.content["image_format"], self.content["alt"], self.content["caption"]
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must contain "image" key with valid image data
    - self.content must contain "image_format" key with valid ImageType enum value
    - self.content must contain "alt" key with alt text for non-SVG images
    
    Postconditions:
    - Returns a valid ipywidgets.Widget instance
    - SVG images are rendered with max-width: 100% styling
    - Non-SVG images are rendered with proper src and alt attributes
    - Caption is properly formatted with gray color and italic styling when present

## Side Effects:
    None

