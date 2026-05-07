# `float_image.py`

## `folium.plugins.float_image.FloatImage` · *class*

## Summary:
A floating image overlay plugin for folium maps that positions an image at specified coordinates with customizable CSS styling.

## Description:
The FloatImage class creates a floating image overlay that can be positioned anywhere on a folium map using CSS positioning. It extends MacroElement to integrate with folium's rendering system and allows users to display images with custom positioning and styling. This class is typically used to add decorative or informational images to maps without affecting the map's layout.

## State:
- image (str or image data): Path, URL, or image data for the image to display
- bottom (int): Distance from the bottom of the map container in percentage (default: 75)
- left (int): Distance from the left of the map container in percentage (default: 75)
- css (dict): Additional CSS properties to apply to the image element
- _name (str): Set to "FloatImage" to identify this element type in folium's rendering system
- _template (Template): Jinja2 template for rendering the HTML - should define the image HTML structure with positioning, currently empty in implementation

## Lifecycle:
- Creation: Instantiate with image path/URL, optional bottom/left positioning, and additional CSS properties
- Usage: Add to a folium.Map instance using the add_child() method
- Destruction: Managed automatically by folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[FloatImage.__init__] --> B[MacroElement.__init__]
    A --> C[Set _name="FloatImage"]
    A --> D[Store image, bottom, left, css]
    A --> E[Initialize empty _template]
```

## Raises:
- None explicitly raised in the constructor
- May raise exceptions from parent MacroElement initialization

## Example:
```python
import folium
from folium.plugins import FloatImage

# Create a map
m = folium.Map([45.372, -121.666], zoom_start=10)

# Add a floating image
float_image = FloatImage(
    'https://example.com/image.png',
    bottom=10,
    left=10,
    opacity=0.8,
    z_index=1000
)
float_image.add_to(m)

# Display the map
m
```

### `folium.plugins.float_image.FloatImage.__init__` · *method*

## Summary:
Initializes a FloatImage object with image data and positioning parameters for map overlay.

## Description:
Configures a floating image overlay that can be positioned anywhere on a folium map using CSS positioning. This method sets up the core attributes needed for rendering the image overlay, including the image source, positioning coordinates, and CSS styling options.

## Args:
    image (str or image data): Path, URL, or image data for the image to display
    bottom (int): Distance from the bottom of the map container in percentage (default: 75)
    left (int): Distance from the left of the map container in percentage (default: 75)
    **kwargs: Additional CSS properties to apply to the image element

## Returns:
    None: This method initializes object attributes and does not return a value

## Raises:
    None explicitly raised in this method
    May raise exceptions from parent MacroElement initialization

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "FloatImage" to identify this element type
    - self.image: Stores the image source/path/data
    - self.bottom: Stores bottom positioning percentage
    - self.left: Stores left positioning percentage
    - self.css: Stores additional CSS properties as a dictionary

## Constraints:
    Preconditions:
    - image parameter must be a valid path, URL, or image data
    - bottom and left parameters should be integers representing percentages (0-100)
    - **kwargs should contain valid CSS property-value pairs
    
    Postconditions:
    - self._name is set to "FloatImage"
    - All provided parameters are stored as instance attributes
    - Object is ready for use in folium map rendering

## Side Effects:
    None: This method performs only attribute assignments and does not cause I/O operations or external service calls

