# `beautify_icon.py`

## `folium.plugins.beautify_icon.BeautifyIcon` · *class*

## Summary:
A class for creating customized beautified marker icons in folium maps with enhanced visual styling capabilities.

## Description:
The BeautifyIcon class provides a mechanism to create visually appealing marker icons for folium maps by leveraging the leaflet-beautify-marker library. It allows extensive customization of icon appearance including shapes, colors, borders, and text elements. This class is typically used when creating map markers that require more sophisticated styling than basic marker icons provide.

The class inherits from JSCSSMixin and MacroElement, enabling automatic inclusion of required JavaScript and CSS resources when rendered in a folium Figure context. It integrates with the leaflet-beautify-marker library hosted on a CDN to provide enhanced marker styling capabilities.

## State:
- _name: String identifier set to "BeautifyIcon" for internal tracking
- _template: Jinja2 Template object (currently empty, intended for rendering icon HTML)
- options: Dictionary containing all icon configuration options processed through parse_options
- ICON_SHAPE_TYPES: Class constant list defining valid icon shape types including "circle", "circle-dot", "doughnut", "rectangle-dot", "marker", and None
- default_js: Class attribute containing URL to the leaflet-beautify-marker JavaScript library
- default_css: Class attribute containing URL to the leaflet-beautify-marker CSS library

## Lifecycle:
- Creation: Instantiate with desired icon properties via __init__ method
- Usage: Add to a folium Map or Figure object to render the customized icon
- Destruction: Automatic cleanup handled by parent classes when the map is disposed

## Method Map:
```mermaid
graph TD
    A[BeautifyIcon.__init__] --> B[parse_options]
    B --> C[super().__init__()]
    C --> D[Set _name="BeautifyIcon"]
    D --> E[Store options]
```

## Raises:
- None explicitly raised by __init__ method
- Inherited exceptions from parent classes (JSCSSMixin, MacroElement) when used outside of a Figure context

## Example:
```python
import folium

# Create a beautified marker with custom properties
icon = folium.plugins.BeautifyIcon(
    icon='star',
    icon_shape='circle',
    border_color='#FF0000',
    background_color='#FFFF00',
    text_color='#0000FF'
)

# Add to a map
m = folium.Map([0, 0], zoom_start=2)
folium.Marker([0, 0], icon=icon).add_to(m)
```

### `folium.plugins.beautify_icon.BeautifyIcon.__init__` · *method*

## Summary:
Initializes a BeautifyIcon instance with customizable icon properties and rendering options.

## Description:
Configures a BeautifyIcon object with various visual styling options including icon shape, border properties, colors, and text formatting. This method sets up the internal options dictionary that will be used to render the icon in a folium map visualization.

## Args:
    icon (str, optional): The icon name to display. Defaults to None.
    icon_shape (str, optional): The shape of the icon container. Defaults to None.
    border_width (int): Width of the icon border in pixels. Defaults to 3.
    border_color (str): Color of the icon border in hex format. Defaults to "#000".
    text_color (str): Color of the text/icon content in hex format. Defaults to "#000".
    background_color (str): Background color of the icon in hex format. Defaults to "#FFF".
    inner_icon_style (str): Additional CSS styles to apply to the inner icon element. Defaults to "".
    spin (bool): Whether to enable spinning animation for the icon. Defaults to False.
    number (int, optional): Numeric value to display as text within the icon. Defaults to None.
    **kwargs: Additional keyword arguments passed to the parent class initialization.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "BeautifyIcon"
    - self.options: Set to the parsed options dictionary from parse_options()

## Constraints:
    Preconditions:
        - The class must inherit from JSCSSMixin and MacroElement
        - All color parameters should be valid hex color codes
        - border_width should be a non-negative integer
    Postconditions:
        - self._name is set to "BeautifyIcon"
        - self.options contains properly formatted camelCase keys with non-None values
        - The object is ready for rendering in a folium map context

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

