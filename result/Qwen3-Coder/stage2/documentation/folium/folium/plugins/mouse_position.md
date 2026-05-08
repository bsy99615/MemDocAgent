# `mouse_position.py`

## `folium.plugins.mouse_position.MousePosition` · *class*

## Summary:
A mouse position control that displays latitude and longitude coordinates as the user moves the mouse over a folium map.

## Description:
The MousePosition class implements a Leaflet.js control that shows the current mouse coordinates (latitude and longitude) in real-time as users interact with a folium map. It is designed to be added as a control to folium maps and provides customizable formatting options for the displayed coordinates. This class inherits from JSCSSMixin and MacroElement, making it compatible with folium's rendering system and enabling automatic inclusion of required JavaScript and CSS resources.

## State:
- _name: str, set to "MousePosition" - identifies this element in folium's element registry
- options: dict, contains parsed configuration options for the mouse position control including:
  - position: str, default "bottomright" - control positioning on the map
  - separator: str, default " : " - character(s) separating latitude and longitude
  - empty_string: str, default "Unavailable" - text shown when coordinates are unavailable
  - lng_first: bool, default False - whether to display longitude before latitude
  - num_digits: int, default 5 - number of decimal digits to show
  - prefix: str, default "" - text prefix to add before coordinates
- lat_formatter: str or callable, default "undefined" - formatter for latitude values
- lng_formatter: str or callable, default "undefined" - formatter for longitude values

## Lifecycle:
- Creation: Instantiate with optional configuration parameters to customize display behavior
- Usage: Add to a folium.Map instance using the add_child() method or similar
- Destruction: Automatically cleaned up when the map is destroyed or the element is removed

## Method Map:
```mermaid
graph TD
    A[MousePosition.__init__] --> B[super().__init__]
    B --> C[parse_options]
    C --> D[Set lat_formatter/lng_formatter]
    D --> E[Element registration]
```

## Raises:
- None explicitly raised by __init__ in the provided code
- May raise exceptions from parent classes during rendering if not properly contained in a Figure context

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add mouse position control with default settings
mouse_position = folium.plugins.MousePosition()
m.add_child(mouse_position)

# Add mouse position control with custom settings
custom_mouse_position = folium.plugins.MousePosition(
    position='topleft',
    separator=' | ',
    empty_string='No coords',
    lng_first=True,
    num_digits=3
)
m.add_child(custom_mouse_position)
```

### `folium.plugins.mouse_position.MousePosition.__init__` · *method*

## Summary:
Initializes a MousePosition control with configurable display options for mouse coordinates.

## Description:
Configures the MousePosition control by setting up its display properties and initializing parent class functionality. This method prepares the control for rendering on a folium map by processing configuration options and establishing default formatting behaviors for latitude and longitude values.

## Args:
    position (str): Position of the control on the map, defaults to "bottomright". Valid positions are 'topright', 'topleft', 'bottomright', 'bottomleft'.
    separator (str): Character(s) separating latitude and longitude in display, defaults to " : ".
    empty_string (str): Text shown when coordinates are unavailable, defaults to "Unavailable".
    lng_first (bool): Whether to display longitude before latitude, defaults to False.
    num_digits (int): Number of decimal digits to show in coordinate display, defaults to 5.
    prefix (str): Text prefix to add before coordinates, defaults to "".
    lat_formatter (callable or str): Formatter for latitude values, defaults to None (which becomes "undefined").
    lng_formatter (callable or str): Formatter for longitude values, defaults to None (which becomes "undefined").
    **kwargs: Additional options passed to the parent class initialization.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions under normal operation.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MousePosition" to identify this element
    - self.options: Set to the processed dictionary of configuration options
    - self.lat_formatter: Set to the provided formatter or "undefined" default
    - self.lng_formatter: Set to the provided formatter or "undefined" default

## Constraints:
    Preconditions:
    - The class must inherit from MacroElement and JSCSSMixin
    - All parameter values must be compatible with their intended use in JavaScript rendering
    - The parent class initialization must succeed
    
    Postconditions:
    - self._name is set to "MousePosition"
    - self.options contains a properly formatted dictionary of configuration options
    - Formatters are either provided functions or default to "undefined" string

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object state.

