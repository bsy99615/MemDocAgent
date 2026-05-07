# `beautify_icon.py`

## `folium.plugins.beautify_icon.BeautifyIcon` · *class*

## Summary:
A customizable marker icon class that enhances map markers with beautified styling using the BeautifyMarker library.

## Description:
The BeautifyIcon class creates enhanced marker icons for folium maps by leveraging the BeautifyMarker JavaScript library. It allows customization of icon appearance through various visual properties like shape, colors, borders, and text. This class is typically used when creating map markers that require more visually appealing designs than standard folium markers.

This class serves as a bridge between Python folium configurations and the JavaScript BeautifyMarker library, automatically managing the required CSS and JavaScript resources through its JSCSSMixin inheritance.

## State:
- _name (str): Set to "BeautifyIcon" to identify the element type
- options (dict): Dictionary of configuration options processed through parse_options, containing:
  - icon (str, optional): Icon name from Font Awesome or similar icon sets
  - icon_shape (str, optional): Shape type from ICON_SHAPE_TYPES list
  - border_width (int): Width of the icon border in pixels (default: 3)
  - border_color (str): Color of the icon border in hex format (default: "#000")
  - text_color (str): Color of text within the icon in hex format (default: "#000")
  - background_color (str): Background color of the icon in hex format (default: "#FFF")
  - inner_icon_style (str): Additional CSS styles for inner icons
  - spin (bool): Whether to enable spinning animation (default: False)
  - isAlphaNumericIcon (bool): Flag indicating if numeric icon is used
  - text (str or int): Text content for alphanumeric icons
- ICON_SHAPE_TYPES (list): Valid icon shape types including "circle", "circle-dot", "doughnut", "rectangle-dot", "marker", and None
- default_js (list): CDN URLs for BeautifyMarker JavaScript resources
- default_css (list): CDN URLs for BeautifyMarker CSS resources

## Lifecycle:
- Creation: Instantiate with desired styling parameters; automatically registers default JS/CSS resources
- Usage: Add to folium Map or FeatureGroup using add_child() method
- Rendering: During map rendering, JSCSSMixin automatically includes required JavaScript and CSS from CDN
- Destruction: No special cleanup required; relies on parent Element's lifecycle management

## Method Map:
```mermaid
graph TD
    A[BeautifyIcon.__init__] --> B[super().__init__()]
    B --> C[self._name = "BeautifyIcon"]
    C --> D[parse_options(...)]
    D --> E[self.options = parsed_options]
    E --> F[return]
```

## Raises:
- None: The constructor does not explicitly raise exceptions, though underlying framework methods may raise exceptions during rendering if resources are unavailable.

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a beautified marker with custom styling
icon = folium.plugins.BeautifyIcon(
    icon='star',
    icon_shape='circle',
    border_color='#FF0000',
    background_color='#FFFF00',
    text_color='#0000FF',
    border_width=5
)

# Add marker to map
folium.Marker(
    location=[45.5236, -122.6750],
    icon=icon,
    popup='Custom Marker'
).add_to(m)

# Display the map
m
```

### `folium.plugins.beautify_icon.BeautifyIcon.__init__` · *method*

## Summary:
Initializes a BeautifyIcon instance with customizable styling parameters for map markers.

## Description:
Configures a BeautifyIcon object with visual properties such as icon shape, colors, borders, and text content. This method processes all provided styling parameters through the parse_options utility to convert them to the appropriate camelCase format required by the underlying JavaScript library, and stores them in the options dictionary for later use during map rendering.

## Args:
    icon (str, optional): Name of the icon from Font Awesome or similar icon sets. Defaults to None.
    icon_shape (str, optional): Shape type for the icon, must be one of "circle", "circle-dot", "doughnut", "rectangle-dot", "marker", or None. Defaults to None.
    border_width (int): Width of the icon border in pixels. Defaults to 3.
    border_color (str): Color of the icon border in hex format. Defaults to "#000".
    text_color (str): Color of text within the icon in hex format. Defaults to "#000".
    background_color (str): Background color of the icon in hex format. Defaults to "#FFF".
    inner_icon_style (str): Additional CSS styles for inner icons. Defaults to "".
    spin (bool): Whether to enable spinning animation. Defaults to False.
    number (int or str, optional): Numeric value to display as an alphanumeric icon. Defaults to None.
    **kwargs: Additional keyword arguments passed to the parse_options utility for further processing.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying framework methods may raise exceptions during rendering if resources are unavailable.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "BeautifyIcon"
    - self.options: Set to the processed dictionary of styling options from parse_options

## Constraints:
    Preconditions:
    - All color parameters must be valid hex color codes
    - icon_shape must be one of the predefined values in ICON_SHAPE_TYPES
    - border_width must be a non-negative integer
    - number parameter, when provided, should be convertible to string for display
    
    Postconditions:
    - self._name is set to "BeautifyIcon"
    - self.options contains all provided parameters converted to camelCase format
    - The isAlphaNumericIcon flag is properly set based on whether number is provided

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

