# `beautify_icon.py`

## `folium.plugins.beautify_icon.BeautifyIcon` · *class*

## Summary:
BeautifyIcon is a folium map element that creates customized marker icons with enhanced visual styling using the BeautifyMarker library.

## Description:
BeautifyIcon enables the creation of visually appealing map markers with customizable shapes, colors, and text elements. It inherits from JSCSSMixin and MacroElement to integrate seamlessly with folium's rendering system and automatically include required JavaScript and CSS dependencies. This class is particularly useful for creating distinctive map markers that go beyond standard Leaflet marker styling.

## State:
- _name (str): Set to "BeautifyIcon" to identify the element type in folium's rendering system
- options (dict): Configuration dictionary containing all icon properties processed by parse_options
- ICON_SHAPE_TYPES (list): Class constant defining valid icon shape types including "circle", "circle-dot", "doughnut", "rectangle-dot", "marker", and None
- default_js (list): Class attribute containing URL for the BeautifyMarker JavaScript library
- default_css (list): Class attribute containing URL for the BeautifyMarker CSS stylesheet

## Lifecycle:
- Creation: Instantiate with desired icon properties; automatically registers default JS/CSS dependencies
- Usage: Add to folium Map or FeatureGroup objects; rendering automatically includes required resources
- Destruction: Managed by folium's garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[BeautifyIcon.__init__] --> B[super().__init__()]
    B --> C[parse_options()]
    C --> D[self.options = ...]
    D --> E[return]
```

## Raises:
- None explicitly raised by __init__
- Inherited exceptions from JSCSSMixin and MacroElement during rendering (e.g., AssertionError if not contained in Figure)

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Create a beautified marker with custom properties
icon = folium.plugins.BeautifyIcon(
    icon='star',
    icon_shape='circle',
    border_color='#FF0000',
    background_color='#FFFF00',
    text_color='#0000FF'
)

# Add marker to map
folium.Marker(
    location=[40.7128, -74.0060],
    icon=icon,
    popup='Custom Marker'
).add_to(m)

# The marker will display with a yellow circle background, red border, and blue star icon
```

### `folium.plugins.beautify_icon.BeautifyIcon.__init__` · *method*

## Summary:
Initializes a BeautifyIcon object with customizable icon properties and configuration options.

## Description:
Configures the BeautifyIcon instance by setting its name and processing various visual styling parameters through the parse_options utility function. This method establishes the foundational configuration for rendering beautified icons in folium maps, handling both standard icon properties and special numeric icon handling.

## Args:
    icon (str, optional): The icon name to display. Defaults to None.
    icon_shape (str, optional): The shape of the icon container. Defaults to None.
    border_width (int): Width of the icon border in pixels. Defaults to 3.
    border_color (str): Color of the icon border in hex format. Defaults to "#000".
    text_color (str): Color of the icon text in hex format. Defaults to "#000".
    background_color (str): Background color of the icon in hex format. Defaults to "#FFF".
    inner_icon_style (str): Additional CSS styles for the inner icon. Defaults to "".
    spin (bool): Whether the icon should spin continuously. Defaults to False.
    number (int, optional): Numeric value to display instead of icon. Defaults to None.
    **kwargs: Additional keyword arguments passed to parse_options for further configuration.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "BeautifyIcon"
    - self.options: Set to the processed dictionary from parse_options

## Constraints:
    Preconditions:
    - All color parameters should be valid hex color codes
    - border_width should be a non-negative integer
    - number parameter, when provided, should be convertible to string for display
    
    Postconditions:
    - self._name is set to "BeautifyIcon"
    - self.options contains properly formatted camelCase keys with non-None values
    - The isAlphaNumericIcon option is correctly set based on whether number is provided

## Side Effects:
    None: This method performs no I/O operations or external service calls.

