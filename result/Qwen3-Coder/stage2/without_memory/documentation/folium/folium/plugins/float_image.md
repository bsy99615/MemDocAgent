# `float_image.py`

## `folium.plugins.float_image.FloatImage` · *class*

## Summary:
Displays an image at a fixed position on a folium map using CSS positioning.

## Description:
The FloatImage class creates a visual element that renders an image at a specific location on a folium map. It inherits from MacroElement, making it compatible with folium's rendering system. This component is typically used to overlay images such as logos, markers, or decorative elements at fixed coordinates on the map canvas.

## State:
- image (str or file-like object): Required parameter specifying the image source to display
- bottom (int): Vertical position from the bottom of the map container in pixels, defaults to 75
- left (int): Horizontal position from the left of the map container in pixels, defaults to 75
- css (dict): Additional CSS properties to apply to the image element, passed as keyword arguments
- _name (str): Set to "FloatImage" for internal identification within folium's element system

## Lifecycle:
- Creation: Instantiate with image parameter and optional positioning parameters
- Usage: Add to a folium.Map instance using the add_child() method or similar
- Destruction: Managed automatically by folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[FloatImage.__init__] --> B[MacroElement.__init__]
    B --> C[Sets _name="FloatImage"]
    C --> D[Stores image, bottom, left, css]
```

## Raises:
- None explicitly raised by the constructor based on available code
- May raise exceptions from parent MacroElement initialization if invalid parameters are passed

## Example:
```python
import folium
from folium.plugins import FloatImage

# Create a map
m = folium.Map([45.372, -121.667], zoom_start=12)

# Create a FloatImage with an image URL
float_image = FloatImage(
    'https://example.com/image.png',
    bottom=100,
    left=50,
    opacity=0.8
)

# Add to map
float_image.add_to(m)
```

### `folium.plugins.float_image.FloatImage.__init__` · *method*

## Summary:
Initializes a FloatImage object that renders a floating image element on folium maps.

## Description:
The FloatImage class implements a floating image element that can be positioned anywhere on a folium map canvas. This initialization method sets up the core configuration including the image source, positioning coordinates, and CSS styling properties. As a subclass of MacroElement, FloatImage integrates seamlessly with folium's rendering pipeline for map overlays.

This method is separated from other logic to provide a clean initialization interface that follows the standard pattern for folium plugin components. It ensures proper setup of all required attributes before the element is rendered in the map.

## Args:
    image (str): Path or URL to the image file to be displayed on the map
    bottom (int, optional): Bottom margin percentage (0-100) for image positioning. Defaults to 75
    left (int, optional): Left margin percentage (0-100) for image positioning. Defaults to 75
    **kwargs: Additional CSS styling parameters (e.g., width, height, opacity) to apply to the image element

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    None explicitly raised: This method doesn't contain explicit exception handling

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "FloatImage" to identify the element type
    - self.image: Stores the image source path/URL
    - self.bottom: Stores the bottom positioning percentage
    - self.left: Stores the left positioning percentage
    - self.css: Stores additional CSS styling parameters

## Constraints:
    Preconditions:
    - The image parameter must be a valid string path or URL
    - bottom and left parameters must be integers between 0 and 100 inclusive
    - kwargs should contain valid CSS property-value pairs
    
    Postconditions:
    - The object is properly initialized as a MacroElement subclass
    - All provided parameters are stored as instance attributes
    - self._name is consistently set to "FloatImage"

## Side Effects:
    None: This method performs only local attribute assignments and doesn't cause any I/O operations or external service calls

