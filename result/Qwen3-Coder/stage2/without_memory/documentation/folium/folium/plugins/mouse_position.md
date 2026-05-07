# `mouse_position.py`

## `folium.plugins.mouse_position.MousePosition` · *class*

## Summary:
Displays mouse coordinates on a Folium map as a Leaflet control element.

## Description:
The MousePosition class creates a Leaflet map control that shows the current mouse coordinates when hovering over the map. It integrates with the Leaflet.MousePosition JavaScript plugin to provide real-time coordinate display in various formats. This class is typically used to enhance map interactivity by allowing users to see geographic coordinates at their cursor position.

## State:
- _name: str, set to "MousePosition" - identifies the element type
- _template: Template - Jinja2 template for HTML rendering (currently empty in source)
- options: dict - configuration options parsed via parse_options for positioning and formatting
- lat_formatter: str or callable - formatter for latitude values, defaults to "undefined" 
- lng_formatter: str or callable - formatter for longitude values, defaults to "undefined"
- default_js: list - JavaScript library URL for Leaflet.MousePosition plugin
- default_css: list - CSS file URL for Leaflet.MousePosition styling

## Lifecycle:
- Creation: Instantiate with optional configuration parameters for position, formatting, and display options
- Usage: Add to a Folium Map object using the add_child() method
- Destruction: Managed automatically by Folium's rendering system when the map is rendered

## Method Map:
```mermaid
graph TD
    A[MousePosition.__init__] --> B[super().__init__()]
    A --> C[Set _name to "MousePosition"]
    A --> D[parse_options for configuration]
    A --> E[Set formatters to "undefined" if None]
    B --> F[JSCSSMixin.render]
    F --> G[Add JS/CSS links to figure header]
    F --> H[Call parent render]
```

## Raises:
- AssertionError: If invalid options are passed to parse_options (though this is handled internally by the parent classes)

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add mouse position control
mouse_position = folium.plugins.MousePosition(
    position='topright',
    separator=' | ',
    empty_string='No coordinates'
)
m.add_child(mouse_position)

# The map now displays mouse coordinates in the top right corner
```

### `folium.plugins.mouse_position.MousePosition.__init__` · *method*

## Summary:
Initializes a MousePosition control that displays latitude and longitude coordinates when hovering over the map.

## Description:
This method sets up the configuration options for the MousePosition control, including positioning, formatting, and display settings. It initializes the control's properties and prepares it for rendering in a folium map. This is the constructor method for the MousePosition class.

## Args:
    position (str): Position of the control on the map. Defaults to "bottomright".
    separator (str): Separator between latitude and longitude values. Defaults to " : ".
    empty_string (str): Text displayed when coordinates are unavailable. Defaults to "Unavailable".
    lng_first (bool): Whether to display longitude before latitude. Defaults to False.
    num_digits (int): Number of decimal digits to display. Defaults to 5.
    prefix (str): Prefix added to coordinate values. Defaults to "".
    lat_formatter (callable or None): Function to format latitude values. Defaults to None.
    lng_formatter (callable or None): Function to format longitude values. Defaults to None.
    **kwargs: Additional keyword arguments passed to the parent class initialization.

## Returns:
    None: This method initializes the object instance and does not return a value.

## Raises:
    AssertionError: If any of the provided options don't meet validation requirements in parse_options.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MousePosition"
    - self.options: Set to parsed options dictionary
    - self.lat_formatter: Set to provided formatter or "undefined"
    - self.lng_formatter: Set to provided formatter or "undefined"

## Constraints:
    Preconditions:
    - The parent classes (JSCSSMixin, MacroElement) must be properly initialized
    - All provided arguments must be compatible with the expected types in parse_options
    
    Postconditions:
    - self._name is set to "MousePosition"
    - self.options contains validated and formatted configuration options
    - self.lat_formatter and self.lng_formatter are properly initialized

## Side Effects:
    None: This method doesn't perform any I/O operations or mutate external objects.

