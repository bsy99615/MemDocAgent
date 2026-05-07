# `float_image.py`

## `folium.plugins.float_image.FloatImage` · *class*

## Summary:
A floating image overlay component for folium maps that displays images at fixed positions relative to the map viewport.

## Description:
The FloatImage class extends MacroElement to create a floating image overlay on folium maps. It enables users to display images at fixed positions relative to the map viewport using percentage-based positioning. This class is particularly useful for adding logos, annotations, or decorative elements to maps without affecting the map's geographic content. The component integrates seamlessly with folium's rendering system through inheritance from MacroElement.

## State:
- image (str): Path or URL to the image resource to be displayed
- bottom (int): Vertical position from the bottom of the map container in percentage (default: 75)
- left (int): Horizontal position from the left of the map container in percentage (default: 75)
- css (dict): Additional CSS properties to apply to the image element
- _name (str): Internal identifier set to "FloatImage"
- _template (Template): Jinja2 template used for generating the HTML structure of the floating image element

## Lifecycle:
- Creation: Instantiate with image path/URL and optional positioning parameters (bottom, left)
- Usage: Automatically rendered as part of folium's HTML generation when added to a map
- Destruction: Managed by folium's garbage collection and map lifecycle management

## Method Map:
```mermaid
graph TD
    A[FloatImage.__init__] --> B[MacroElement.__init__]
    B --> C[Set _name="FloatImage"]
    C --> D[Store image, bottom, left, css]
    D --> E[Uses _template for HTML rendering]
```

## Raises:
- None explicitly raised in __init__
- Inheritance from MacroElement may raise exceptions from parent initialization

## Example:
```python
import folium
from folium.plugins import FloatImage

# Create a map
m = folium.Map([0, 0], zoom_start=2)

# Add a floating image
float_img = FloatImage(
    'https://example.com/image.png',
    bottom=10,
    left=10,
    opacity=0.8
)
float_img.add_to(m)

# Display the map
m
```

### `folium.plugins.float_image.FloatImage.__init__` · *method*

## Summary:
Initializes a floating image overlay component with specified image, positioning, and styling properties.

## Description:
The `__init__` method sets up the FloatImage component by initializing its parent class, setting the internal name identifier, and storing the image resource path/URL along with positioning and CSS properties. This method establishes the foundational configuration for the floating image overlay that will be rendered on folium maps.

## Args:
- image (str): Path or URL to the image resource to be displayed
- bottom (int): Vertical position from the bottom of the map container in percentage (default: 75)
- left (int): Horizontal position from the left of the map container in percentage (default: 75)
- **kwargs: Additional CSS properties to apply to the image element

## Returns:
- None: This method initializes instance attributes but does not return a value

## Raises:
- None explicitly raised in this method
- May propagate exceptions from `super().__init__()` if parent class initialization fails

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: 
  - `self._name` set to "FloatImage"
  - `self.image` set to the provided image parameter
  - `self.bottom` set to the provided bottom parameter
  - `self.left` set to the provided left parameter
  - `self.css` set to the provided kwargs dictionary

## Constraints:
- Preconditions: The `image` parameter must be a valid string representing a path or URL
- Postconditions: The instance will have `_name="FloatImage"`, and all provided parameters will be stored as instance attributes

## Side Effects:
- None: This method performs only attribute assignments and does not cause I/O operations or external service calls

