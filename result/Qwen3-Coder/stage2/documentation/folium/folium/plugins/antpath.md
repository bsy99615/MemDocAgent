# `antpath.py`

## `folium.plugins.antpath.AntPath` · *class*

## Summary:
Represents an animated ant path visualization layer for folium maps using the leaflet-ant-path JavaScript library.

## Description:
The AntPath class creates an animated path visualization on folium maps that simulates an ant moving along a route. It extends the functionality of BaseMultiLocation to handle multiple geographic coordinates and inherits JavaScript/CSS resource management from JSCSSMixin. This class is specifically designed to render animated paths that move along a predefined route, commonly used for visualizing routes with motion effects in interactive maps.

The class integrates with the leaflet-ant-path JavaScript library which provides the animation capabilities. It accepts a series of geographic locations and various styling parameters to customize the appearance and behavior of the animated path.

## State:
- locations (list): Geographic coordinate data representing the path points, validated through BaseMultiLocation's validation process. Each location is typically a [latitude, longitude] pair.
- popup (Popup or None): Optional popup element that can be attached to the path visualization.
- tooltip (Tooltip or None): Optional tooltip element that can be attached to the path visualization.
- _name (str): Class identifier set to "AntPath" for internal tracking.
- options (dict): Dictionary of styling and behavioral options for the ant path, including:
  - paused (bool): Whether the animation is initially paused. Default: False
  - reverse (bool): Whether the animation moves in reverse direction. Default: False
  - hardwareAcceleration (bool): Whether to enable hardware acceleration for smoother animations. Default: False
  - delay (int): Delay between animation frames in milliseconds. Default: 400
  - dashArray (list): Dash pattern for the path line. Default: [10, 20]
  - weight (int): Width of the path line in pixels. Default: 5
  - opacity (float): Opacity of the path line. Default: 0.5
  - color (str): Color of the path line in hex format. Default: "#0000FF"
  - pulseColor (str): Color of the animated pulse effect. Default: "#FFFFFF"

## Lifecycle:
- Creation: Instantiate with required locations parameter and optional popup/tooltip. Additional styling options can be passed via keyword arguments.
- Usage: Once added to a folium.Map object, the ant path will be rendered with animation when the map is displayed in a browser.
- Destruction: Automatic cleanup occurs through folium's element lifecycle management when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[AntPath.__init__] --> B[BaseMultiLocation.__init__]
    B --> C[validate_locations]
    C --> D[JSCSSMixin.__init__]
    D --> E[Set _name="AntPath"]
    E --> F[Call path_options()]
    F --> G[Update options with custom kwargs]
    G --> H[Return]
```

## Raises:
- TypeError: Raised by BaseMultiLocation.validate_locations() when locations is not an iterable or contains invalid data types.
- ValueError: Raised by BaseMultiLocation.validate_locations() when locations is empty or contains invalid coordinate data.

## Example:
```python
import folium

# Create a sample map
m = folium.Map([40.7128, -74.0060], zoom_start=10)

# Define path coordinates
locations = [
    [40.7128, -74.0060],  # New York
    [37.7749, 122.4194],  # San Francisco
    [34.0522, -118.2437]  # Los Angeles
]

# Create ant path with custom styling
ant_path = folium.plugins.AntPath(
    locations=locations,
    color='#FF0000',
    weight=3,
    delay=200,
    pulse_color='#FFFFFF'
)

# Add to map
m.add_child(ant_path)

# Save or display the map
# m.save('ant_path_map.html')
```

### `folium.plugins.antpath.AntPath.__init__` · *method*

## Summary:
Initializes an AntPath object with geographic locations and configurable animation options for animated map paths.

## Description:
Configures the AntPath instance by initializing parent classes, setting the element name to "AntPath", and establishing default styling and animation parameters. This method prepares the object for rendering as an animated path on folium maps, supporting features like pausing, reversing, hardware acceleration, and customizable visual properties.

## Args:
    locations (list): List of geographic coordinate pairs [latitude, longitude] defining the path geometry.
    popup (Popup or None): Optional popup element to display when clicking on the path. Defaults to None.
    tooltip (Tooltip or None): Optional tooltip element to display on hover. Defaults to None.
    **kwargs: Additional styling and animation parameters including:
        - paused (bool): Whether the animation is initially paused. Defaults to False.
        - reverse (bool): Whether to animate in reverse direction. Defaults to False.
        - hardware_acceleration (bool): Enable hardware acceleration for smoother animation. Defaults to False.
        - delay (int): Animation delay in milliseconds. Defaults to 400.
        - dash_array (list): Dash pattern for the path. Defaults to [10, 20].
        - weight (int): Path line weight in pixels. Defaults to 5.
        - opacity (float): Path opacity. Defaults to 0.5.
        - color (str): Path color in hex format. Defaults to "#0000FF".
        - pulse_color (str): Color of the animated pulse effect. Defaults to "#FFFFFF".

## Returns:
    None: This method initializes the object state and returns nothing.

## Raises:
    TypeError: Raised by parent classes when locations is not an iterable or contains invalid data types.
    ValueError: Raised by parent classes when locations is empty or contains invalid coordinate data.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "AntPath"
        - self.options: Initialized with path styling and animation options

## Constraints:
    Preconditions:
        - locations must be a valid iterable of geographic coordinate pairs
        - All coordinate values must be within valid latitude (-90 to 90) and longitude (-180 to 180) ranges
        - Parent class validation requirements must be satisfied
    Postconditions:
        - self._name is set to "AntPath"
        - self.options contains a complete dictionary of path styling and animation parameters
        - The object is ready for rendering in a folium map context

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

