# `locate_control.py`

## `folium.plugins.locate_control.LocateControl` · *class*

## Summary:
LocateControl is a folium plugin that adds a location finder control to Leaflet maps, enabling users to locate their current position on the map.

## Description:
The LocateControl class implements a Leaflet plugin that provides geolocation functionality for folium maps. It allows users to easily find and center their current location on the map. This control is particularly useful for applications that require user location services, such as mapping applications, location-based services, or navigation tools. The control integrates with the Leaflet LocateControl library and inherits from JSCSSMixin to handle JavaScript and CSS dependencies automatically.

## State:
- auto_start (bool): Determines whether the location finding should start automatically when the map loads. Default is False.
- options (dict): A dictionary of additional configuration options passed to the underlying Leaflet LocateControl plugin, processed through parse_options to convert snake_case keys to camelCase.
- _name (str): Class attribute identifying this element as "LocateControl" in the folium rendering system.

## Lifecycle:
- Creation: Instantiate with optional auto_start parameter and additional configuration options via keyword arguments
- Usage: Add to a folium.Map instance using the add_child() method or similar mechanisms
- Destruction: Managed automatically through folium's element lifecycle when the map is rendered and disposed

## Method Map:
```mermaid
graph TD
    A[LocateControl.__init__] --> B[super().__init__()]
    B --> C[JSCSSMixin.__init__]
    C --> D[MacroElement.__init__]
    D --> E[Set _name="LocateControl"]
    E --> F[Set auto_start]
    F --> G[Set options via parse_options]
```

## Raises:
- None explicitly raised by __init__
- Inherited exceptions from parent classes (JSCSSMixin, MacroElement) may be raised during rendering

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Add locate control that starts automatically
locate_control = folium.plugins.LocateControl(auto_start=True)
m.add_child(locate_control)

# Add locate control with custom options
locate_control = folium.plugins.LocateControl(
    auto_start=False,
    draw_circle=True,
    follow=True,
    set_view='move'
)
m.add_child(locate_control)
```

### `folium.plugins.locate_control.LocateControl.__init__` · *method*

## Summary:
Initializes a LocateControl instance with optional auto-start behavior and configurable options.

## Description:
Configures the LocateControl object by setting its name, auto-start flag, and processing additional options through the parse_options utility function. This method establishes the initial state of the control before it is added to a map.

## Args:
    auto_start (bool): Whether to automatically start location tracking when the control is initialized. Defaults to False.
    **kwargs: Additional configuration options that will be converted to camelCase format and filtered for None values.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "LocateControl" string literal
    - self.auto_start: Set to the provided auto_start boolean value
    - self.options: Set to the processed dictionary from parse_options function

## Constraints:
    Preconditions: 
    - The parent class constructor must accept no arguments
    - All kwargs must be valid keyword arguments for parse_options function
    
    Postconditions:
    - self._name is always set to "LocateControl"
    - self.auto_start is assigned the provided boolean value
    - self.options contains processed kwargs with camelCase keys and None-filtered values

## Side Effects:
    None

