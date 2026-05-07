# `image.py`

## `src.ydata_profiling.report.presentation.core.image.Image` · *class*

## Summary:
Represents an image element in a report presentation with associated metadata like format, alternative text, and optional caption.

## Description:
The Image class is used to encapsulate image data and metadata for inclusion in report presentations. It extends ItemRenderer to provide standardized handling of image elements. This class serves as a distinct abstraction for managing image content in reports, separating image data from presentation logic.

## State:
- image: str - Path or URL to the image resource
- image_format: ImageType - Format specification for the image (e.g., PNG, JPEG)
- alt: str - Alternative text for accessibility
- caption: Optional[str] - Optional descriptive caption for the image
- item_type: str - Set to "image" by constructor, identifies the element type
- content: dict - Dictionary containing all image metadata (image, image_format, alt, caption)

## Lifecycle:
- Creation: Instantiate with image path/URL, format, and alt text; optional caption
- Usage: Typically rendered through parent class mechanisms, though render() is abstract
- Destruction: Inherits standard object cleanup from ItemRenderer parent

## Method Map:
```mermaid
graph TD
    A[Image.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    A --> D[Validation: image is not None]
    C --> E[Image.render()]
    E --> F[NotImplementedError]
```

## Raises:
- ValueError: When the image parameter is None, with message including alt and caption information

## Example:
```python
from ydata_profiling.config import ImageType

# Create an image with caption
img = Image(
    image="path/to/chart.png",
    image_format=ImageType.PNG,
    alt="Bar chart showing sales data",
    caption="Figure 1: Monthly sales trends"
)

# Create an image without caption
img_no_caption = Image(
    image="path/to/graph.jpg",
    image_format=ImageType.JPEG,
    alt="Line graph of temperature changes"
)
```

### `src.ydata_profiling.report.presentation.core.image.Image.__init__` · *method*

## Summary:
Initializes an image presentation component with image data, format, and accessibility attributes.

## Description:
Configures an image rendering component by validating image content and setting up the underlying presentation structure. This method ensures proper initialization of image-specific properties while maintaining compatibility with the presentation layer's rendering system.

## Args:
    image (str): The image content/data as a string
    image_format (ImageType): The format of the image (either 'svg' or 'png')
    alt (str): Alternative text for accessibility
    caption (Optional[str]): Optional caption text for the image, defaults to None
    **kwargs: Additional keyword arguments passed to parent initializer

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    ValueError: When the image parameter is None, with descriptive error message including alt and caption values

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.item_type (set to "image")
        - self.content (populated with image, image_format, alt, and caption data)

## Constraints:
    Preconditions:
        - The image parameter must not be None
        - image_format must be a valid ImageType enum value ('svg' or 'png')
    Postconditions:
        - The object is properly initialized with item_type set to "image"
        - The content dictionary contains all provided image metadata

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.image.Image.__repr__` · *method*

## Summary:
Returns a string representation identifying the Image class type.

## Description:
This method provides a minimal string representation of the Image object, returning the literal string "Image". It is used primarily for debugging and development purposes to quickly identify the type of object when printed or inspected.

## Args:
    None

## Returns:
    str: The string "Image" that identifies this object as an Image instance.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: None

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.image.Image.render` · *method*

## Summary:
Renders image content into a presentation-ready format for report generation.

## Description:
This abstract method defines the interface for converting image data into a format suitable for inclusion in reports and presentations. As an abstract method in the Image class hierarchy, it must be implemented by concrete subclasses to provide specific rendering logic for different image types. The method serves as the core interface for transforming image content into presentation elements that can be embedded in HTML reports or other output formats.

## Args:
    None

## Returns:
    Any: A presentation-ready representation of the image, typically a string containing HTML markup, base64-encoded image data, or other format compatible with the reporting framework's rendering pipeline.

## Raises:
    NotImplementedError: When invoked on the abstract base Image class without a concrete implementation in a subclass.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing image metadata and raw data
    - self.item_type: String identifier indicating the type of image item
    - Other inherited attributes from Renderable base class
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Image instance must be properly initialized with valid content
    - Subclasses must implement this method with appropriate rendering logic
    - The content dictionary should contain valid image data and metadata
    
    Postconditions:
    - Returns a format-compatible representation that integrates with the reporting system
    - The returned value maintains the semantic meaning of the original image data

## Side Effects:
    None

