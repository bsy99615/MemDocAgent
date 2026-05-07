# `mouse_position.py`

## `folium.plugins.mouse_position.MousePosition` · *class*

## Summary:
A folium plugin that displays mouse coordinates on the map as a control element.

## Description:
The MousePosition class implements a Leaflet-based control that shows the current mouse coordinates when hovering over a folium map. It inherits from JSCSSMixin and MacroElement, making it compatible with folium's rendering system and automatically including required JavaScript and CSS resources from the Leaflet.MousePosition plugin. This control is useful for debugging map interactions and providing coordinate information to users.

## State:
- _name (str): Set to "MousePosition" to identify the element type
- _template (Template): Jinja2 template for rendering the control (currently empty, populated by Leaflet plugin)
- options (dict): Configuration options parsed via parse_options, including position, separator, empty_string, lng_first, num_digits, and prefix
- lat_formatter (str): Function to format latitude values, defaults to "undefined" when not provided
- lng_formatter (str): Function to format longitude values, defaults to "undefined" when not provided
- default_js (list): List of (name, url) tuples for Leaflet.MousePosition JavaScript resources
- default_css (list): List of (name, url) tuples for Leaflet.MousePosition CSS resources

## Lifecycle:
- Creation: Instantiate with optional configuration parameters; the class handles automatic inclusion of required JS/CSS resources
- Usage: Add to a folium Figure using add_child(); during rendering, the control will appear on the map according to the position parameter
- Destruction: No special cleanup required; relies on parent class lifecycle management

## Method Map:
```mermaid
graph TD
    A[MousePosition.__init__] --> B[super().__init__()]
    B --> C[Set _name to "MousePosition"]
    C --> D[parse_options()]
    D --> E[Set lat_formatter and lng_formatter]
    E --> F[Return initialized object]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if not properly contained within a Figure context

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

# The mouse position control will appear in the top right corner
# showing coordinates as the user moves the mouse over the map
```

### `folium.plugins.mouse_position.MousePosition.__init__` · *method*

## Summary:
Initializes a MousePosition plugin that displays mouse coordinates on a folium map.

## Description:
Configures the mouse position display plugin with various formatting and positioning options. This method sets up the core configuration parameters that control how mouse coordinates are displayed on the map, including positioning, formatting separators, and coordinate formatting functions.

## Args:
    position (str): Position of the mouse position display on the map. Defaults to "bottomright".
    separator (str): Separator string between latitude and longitude values. Defaults to " : ".
    empty_string (str): String to display when coordinates are unavailable. Defaults to "Unavailable".
    lng_first (bool): Whether to display longitude before latitude. Defaults to False.
    num_digits (int): Number of decimal digits to display for coordinates. Defaults to 5.
    prefix (str): Prefix string to add before coordinate values. Defaults to "".
    lat_formatter (callable or None): Function to format latitude values. Defaults to None.
    lng_formatter (callable or None): Function to format longitude values. Defaults to None.
    **kwargs: Additional options passed to the underlying JavaScript implementation.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MousePosition" 
    - self.options: Set to parsed options dictionary from parse_options
    - self.lat_formatter: Set to provided formatter or "undefined"
    - self.lng_formatter: Set to provided formatter or "undefined"

## Constraints:
    Preconditions:
    - The class must inherit from MacroElement and JSCSSMixin
    - All parameter values must be compatible with their intended use in JavaScript context
    - Position parameter must be one of the valid folium map position values
    
    Postconditions:
    - self._name is set to "MousePosition"
    - self.options contains properly formatted camelCase options
    - Formatters are either provided functions or default to "undefined" string

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

