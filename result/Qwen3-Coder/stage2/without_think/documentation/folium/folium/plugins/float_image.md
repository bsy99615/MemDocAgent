# `float_image.py`

## `folium.plugins.float_image.FloatImage` · *class*

## Summary:
A floating image overlay plugin for folium maps that positions an image at fixed coordinates.

## Description:
The FloatImage class creates a floating image overlay element for folium maps. It inherits from MacroElement and is designed to position an image at specific coordinates relative to the map container. This class is intended to be used as a plugin component within folium map visualizations.

## State:
- image (str or file-like object): Path to image file or image data to display
- bottom (int): Distance from bottom of map container in percentage (default: 75)
- left (int): Distance from left of map container in percentage (default: 75)
- css (dict): Additional CSS properties to apply to the image element
- _name (str): Set to "FloatImage" to identify this element type

## Lifecycle:
- Creation: Instantiate with image path/file and optional positioning parameters (bottom, left)
- Usage: Add to a folium.Map instance using standard folium element addition methods
- Destruction: Managed by folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[FloatImage.__init__] --> B[MacroElement.__init__]
    A --> C[Set _name="FloatImage"]
    A --> D[Set image]
    A --> E[Set bottom]
    A --> F[Set left]
    A --> G[Set css]
```

## Raises:
- None explicitly raised in __init__
- May raise exceptions from parent MacroElement initialization

## Example:
```python
import folium
from folium.plugins import FloatImage

# Create a map
m = folium.Map([45.372, -121.667], zoom_start=12)

# Create float image overlay
float_image = FloatImage(
    'path/to/image.png',
    bottom=85,
    left=5
)

# Add to map
float_image.add_to(m)
```

### `folium.plugins.float_image.FloatImage.__init__` · *method*

## Summary:
Initializes a floating image overlay element with specified positioning and styling properties.

## Description:
Configures a FloatImage instance by setting its image source, positioning coordinates, and CSS styling properties. This method establishes the core configuration needed for rendering an image overlay at fixed coordinates within a folium map container.

## Args:
    image (str or file-like object): Path to image file or image data to display on the map
    bottom (int, optional): Distance from bottom of map container in percentage. Defaults to 75.
    left (int, optional): Distance from left of map container in percentage. Defaults to 75.
    **kwargs: Additional CSS properties to apply to the image element

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "FloatImage" to identify this element type
    - self.image: Set to the provided image parameter
    - self.bottom: Set to the provided bottom parameter
    - self.left: Set to the provided left parameter
    - self.css: Set to the provided keyword arguments dictionary

## Constraints:
    Preconditions:
    - The image parameter should be a valid path to an image file or image data
    - bottom and left parameters should be integers representing percentages (0-100)
    - The FloatImage instance should be properly initialized before being added to a folium map

    Postconditions:
    - All instance attributes are set according to provided parameters
    - The _name attribute is correctly set to "FloatImage"
    - The instance is ready for use as a folium map element

## Side Effects:
    None: This method performs only local attribute assignments and does not cause any I/O operations or external service calls

