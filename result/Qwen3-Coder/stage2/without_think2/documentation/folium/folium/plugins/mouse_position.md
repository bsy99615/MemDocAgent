# `mouse_position.py`

## `folium.plugins.mouse_position.MousePosition` · *class*

## Summary:
MousePosition is a folium plugin that adds a mouse position indicator control to interactive maps, displaying latitude and longitude coordinates as the user moves the mouse over the map.

## Description:
The MousePosition class implements a Leaflet.js control that shows the current mouse coordinates in real-time on the map. It inherits from JSCSSMixin and MacroElement to integrate seamlessly with folium's rendering system and automatically include required JavaScript/CSS dependencies. This component is typically used to enhance user experience by providing spatial context during map interactions.

## State:
- position (str): Position of the control on the map, defaults to "bottomright"
- separator (str): String used to separate latitude and longitude values, defaults to " : "
- empty_string (str): Text displayed when coordinates are unavailable, defaults to "Unavailable"
- lng_first (bool): Whether to display longitude before latitude, defaults to False
- num_digits (int): Number of decimal digits to display for coordinates, defaults to 5
- prefix (str): Prefix string added before coordinate values, defaults to ""
- lat_formatter (callable or str): Function or string for formatting latitude values, defaults to "undefined"
- lng_formatter (callable or str): Function or string for formatting longitude values, defaults to "undefined"
- options (dict): Parsed options dictionary containing all configuration parameters in camelCase format
- _name (str): Internal identifier set to "MousePosition"

## Lifecycle:
- Creation: Instantiate with optional configuration parameters; automatically registers default JavaScript/CSS dependencies
- Usage: Add to a folium.Map instance using the add_child() method or similar
- Destruction: Managed by folium's map rendering system; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[MousePosition.__init__] --> B[super().__init__()]
    B --> C[parse_options()]
    C --> D[Set lat_formatter/lng_formatter]
    D --> E[End initialization]
```

## Raises:
- None explicitly raised by __init__
- Inherited exceptions from MacroElement/JSCSSMixin during rendering (e.g., AssertionError if not contained in Figure)

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

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
Initializes a MousePosition plugin instance with configurable display options for mouse coordinates.

## Description:
Configures the MousePosition plugin by setting up its display properties and formatting options. This method establishes the core configuration that determines how mouse coordinates are displayed on the map, including positioning, separators, number formatting, and custom formatters.

## Args:
    position (str, optional): Position of the mouse position display on the map. Defaults to "bottomright".
    separator (str, optional): Separator string between latitude and longitude values. Defaults to " : ".
    empty_string (str, optional): String to display when coordinates are unavailable. Defaults to "Unavailable".
    lng_first (bool, optional): Whether to display longitude before latitude. Defaults to False.
    num_digits (int, optional): Number of decimal digits to display for coordinates. Defaults to 5.
    prefix (str, optional): Prefix string to prepend to coordinate values. Defaults to "".
    lat_formatter (callable, optional): Custom formatter function for latitude values. Defaults to None.
    lng_formatter (callable, optional): Custom formatter function for longitude values. Defaults to None.
    **kwargs: Additional options passed to the parent class initialization.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MousePosition"
    - self.options: Set to parsed options dictionary from parse_options
    - self.lat_formatter: Set to provided formatter or "undefined"
    - self.lng_formatter: Set to provided formatter or "undefined"

## Constraints:
    Preconditions:
    - All provided arguments must be of the correct type
    - Position must be a valid position string recognized by the map UI
    - num_digits must be a non-negative integer
    
    Postconditions:
    - self._name is set to "MousePosition"
    - self.options contains properly formatted camelCase options
    - Formatters are either provided functions or default to "undefined" string

## Side Effects:
    None

