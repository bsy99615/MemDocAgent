# `image.py`

## `src.ydata_profiling.report.presentation.core.image.Image` · *class*

## Summary:
Represents an image element in the profiling report presentation layer, used to display visualizations and charts.

## Description:
The Image class is a specialized renderer for displaying images within profiling reports. It extends ItemRenderer to provide a structured way to represent image elements with associated metadata like alternative text and captions. This class is typically instantiated by report generation components when creating visualizations for data profiling reports.

## State:
- `image` (str): Path or URL to the image resource, cannot be None
- `image_format` (ImageType): Format of the image (svg or png) 
- `alt` (str): Alternative text describing the image for accessibility
- `caption` (Optional[str]): Optional caption text for the image
- `item_type` (str): String identifier set to "image" by constructor
- `content` (dict): Dictionary containing all image metadata including image path, format, alt text, and caption

## Lifecycle:
- Creation: Instantiate with image path/URL, format, and alt text; caption is optional
- Usage: Typically rendered by presentation layer components during report generation
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph LR
    A[Image.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Image.render()]
    D --> E[Abstract method implementation]
```

## Raises:
- ValueError: When the image parameter is None, with descriptive error message including alt and caption values

## Example:
```python
from ydata_profiling.config import ImageType
from ydata_profiling.report.presentation.core.image import Image

# Create an image element for a report
img = Image(
    image="path/to/chart.svg",
    image_format=ImageType.svg,
    alt="Distribution chart of age variable",
    caption="Figure 1: Age distribution histogram"
)

# The image would typically be rendered by the presentation layer
# img.render()  # Would raise NotImplementedError in this base class
```

### `src.ydata_profiling.report.presentation.core.image.Image.__init__` · *method*

## Summary:
Initializes an Image object with image data, format, and accessibility attributes.

## Description:
Constructs an Image instance by validating the image parameter and initializing the parent ItemRenderer with image metadata. This method ensures that image data is properly validated before creating the image representation.

## Args:
    image (str): The image data or path to be displayed.
    image_format (ImageType): The format of the image (e.g., PNG, JPEG).
    alt (str): Alternative text for accessibility purposes.
    caption (Optional[str]): Optional caption for the image. Defaults to None.
    **kwargs: Additional keyword arguments passed to the parent constructor.

## Returns:
    None: This method initializes the object and does not return a value.

## Raises:
    ValueError: When the image parameter is None, with a descriptive error message including alt and caption values.

## State Changes:
    Attributes READ: 
    - alt (used in error message)
    - caption (used in error message)
    Attributes WRITTEN: 
    - self.item_type (set to "image")
    - Other attributes inherited from ItemRenderer parent class

## Constraints:
    Preconditions:
    - The image parameter must not be None
    - image_format must be a valid ImageType value
    - alt must be a non-empty string
    
    Postconditions:
    - The object is initialized with item_type set to "image"
    - All provided parameters are stored in the content dictionary passed to parent constructor

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `src.ydata_profiling.report.presentation.core.image.Image.__repr__` · *method*

## Summary:
Returns a string representation of the Image object for debugging and logging purposes.

## Description:
Implements the standard Python `__repr__` magic method to provide a clear textual representation of Image objects. This method is automatically called by Python's built-in repr() function and various debugging tools when displaying Image instances.

The method is part of the Image class hierarchy that inherits from ItemRenderer, and follows the common pattern of returning a string that identifies the object type. This implementation provides a simple, consistent representation that helps developers quickly identify Image objects during debugging sessions.

## Args:
    None

## Returns:
    str: Always returns the literal string "Image" regardless of the object's internal state.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "Image"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.image.Image.render` · *method*

## Summary:
Abstract method that must be implemented by subclasses to generate presentation-ready image content.

## Description:
This abstract method defines the interface for rendering image components within the presentation layer of the ydata-profiling framework. As part of the ItemRenderer base class hierarchy, it establishes a contract that concrete implementations must fulfill to generate appropriate presentation output for image data.

The method is intentionally left unimplemented in the base Image class to allow different rendering strategies (HTML, markdown, etc.) while maintaining a consistent interface across all image presentation components. In the context of the ydata-profiling library, this typically returns HTML or other presentation markup that can be embedded in reports or dashboards.

## Args:
    None

## Returns:
    Any: Expected to return a presentation-ready representation of the image content, typically HTML string or similar markup format, but raises NotImplementedError in the base implementation.

## Raises:
    NotImplementedError: Always raised by this base implementation to enforce that subclasses must provide concrete rendering logic.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: None

## Side Effects:
    None

