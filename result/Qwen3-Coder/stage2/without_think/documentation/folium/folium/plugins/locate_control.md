# `locate_control.py`

## `folium.plugins.locate_control.LocateControl` · *class*

## Summary:
A control element that adds a locate button to a folium map, enabling users to find their current geographic position using browser geolocation.

## Description:
The LocateControl class implements a Leaflet.js plugin control that allows users to locate themselves on the map using their device's geolocation capabilities. It extends JSCSSMixin and MacroElement to integrate seamlessly with folium's map rendering system, automatically including required JavaScript and CSS resources. This control is typically added to a folium map to provide users with a "Find Me" button functionality.

## State:
- auto_start (bool): Determines whether the locate control should automatically start searching for the user's location when the map loads. Defaults to False.
- options (dict): A dictionary of additional configuration options passed to the underlying Leaflet LocateControl plugin, converted to camelCase format using parse_options.
- _name (str): Class attribute identifying this element as "LocateControl".
- _template (Template): Jinja2 template used for rendering the control's HTML representation (empty in current implementation).

## Lifecycle:
- Creation: Instantiate with optional auto_start parameter and additional configuration options via keyword arguments.
- Usage: Add to a folium.Map instance using the add_child() method. The control will automatically render with required JavaScript/CSS resources when the map is displayed.
- Destruction: No explicit cleanup required; inherits standard folium element lifecycle management.

## Method Map:
```mermaid
graph TD
    A[LocateControl.__init__] --> B[super().__init__]
    B --> C[JSCSSMixin.__init__]
    C --> D[MacroElement.__init__]
    D --> E[Set _name, auto_start, options]
    E --> F[Render map with LocateControl]
    F --> G[JSCSSMixin.render]
    G --> H[Include JS/CSS resources]
    H --> I[Leaflet LocateControl plugin]
```

## Raises:
- None explicitly raised by __init__ in the provided code, though parent classes may raise exceptions during rendering if not properly contained within a Figure context.

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add locate control that starts automatically
locate_control = folium.plugins.LocateControl(auto_start=True)
m.add_child(locate_control)

# Add locate control with custom options
locate_control_custom = folium.plugins.LocateControl(
    auto_start=False,
    draw_circle=True,
    follow=True,
    marker={'title': 'Your Location'}
)
m.add_child(locate_control_custom)
```

### `folium.plugins.locate_control.LocateControl.__init__` · *method*

## Summary:
Initializes a LocateControl instance with optional auto-start behavior and configuration options for the geolocation control.

## Description:
Configures a LocateControl element that enables users to find their current geographic position on a folium map. This method sets up the control's core properties including automatic startup behavior and additional configuration options, while establishing proper inheritance from JSCSSMixin and MacroElement parent classes.

## Args:
    auto_start (bool): Determines whether the locate control should automatically start searching for the user's location when the map loads. Defaults to False.
    **kwargs: Additional configuration options that will be processed by parse_options to convert snake_case keys to camelCase format.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though parent class constructors may raise exceptions during initialization.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "LocateControl" to identify the element type
        - self.auto_start: Set to the provided auto_start parameter value
        - self.options: Set to parsed keyword arguments using parse_options function

## Constraints:
    Preconditions:
        - The method must be called on an instance of LocateControl class
        - Parent class constructors (JSCSSMixin, MacroElement) must be able to handle the initialization
    Postconditions:
        - The instance will have _name set to "LocateControl"
        - The instance will have auto_start set to the provided value
        - The instance will have options dictionary populated with parsed configuration

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes and calls parent constructors.

