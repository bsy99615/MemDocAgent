# `antpath.py`

## `folium.plugins.antpath.AntPath` · *class*

## Summary:
AntPath creates animated paths on Leaflet maps using the leaflet-ant-path JavaScript library.

## Description:
The AntPath class implements an animated path visualization for folium maps. It extends BaseMultiLocation to handle multiple geographic coordinates and JSCSSMixin to manage JavaScript dependencies. This class is used to create visually animated routes or paths that travel along a set of coordinates, commonly used for representing movement or trajectories on maps.

## State:
- locations: list[list[float]] - Geographic coordinates in [latitude, longitude] format for the path
- popup: Popup or None - Interactive popup element associated with the path
- tooltip: Tooltip or None - Interactive tooltip element associated with the path
- _name: str - Class identifier set to "AntPath"
- options: dict - Configuration options for the animated path including:
  - paused: bool - Whether the animation is initially paused (default: False)
  - reverse: bool - Whether the animation travels in reverse direction (default: False)
  - hardwareAcceleration: bool - Enables hardware acceleration for smoother animations (default: False)
  - delay: int - Delay between animation steps in milliseconds (default: 400)
  - dashArray: list[int] - Array defining dash pattern for the path (default: [10, 20])
  - weight: int - Width of the path line in pixels (default: 5)
  - opacity: float - Opacity level of the path (default: 0.5)
  - color: str - Color of the path line (default: "#0000FF")
  - pulseColor: str - Color of the animated pulse effect (default: "#FFFFFF")

## Lifecycle:
- Creation: Instantiate with locations parameter containing geographic coordinates, and optional popup and tooltip elements. Additional animation options can be passed via keyword arguments.
- Usage: Add to a folium.Map instance using add_child(). The animation will be rendered when the map is displayed in a browser.
- Destruction: Managed automatically by folium's element hierarchy system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[AntPath.__init__] --> B[BaseMultiLocation.__init__]
    B --> C[validate_locations(locations)]
    C --> D[super().__init__()]
    D --> E[set _name="AntPath"]
    E --> F[path_options(line=True, **kwargs)]
    F --> G[update options with animation settings]
    G --> H[End init]
```

## Raises:
- TypeError: From BaseMultiLocation.validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: From BaseMultiLocation.validate_locations() when locations is empty or contains invalid coordinate data
- TypeError: From BaseMultiLocation.validate_locations() when coordinate data cannot be properly indexed

## Example:
```python
import folium

# Create a map
m = folium.Map([40.7128, -74.0060], zoom_start=10)

# Define path coordinates
locations = [
    [40.7128, -74.0060],  # New York
    [37.7749, -122.4194], # San Francisco
    [34.0522, -118.2437]  # Los Angeles
]

# Create animated path with custom options
ant_path = folium.plugins.AntPath(
    locations=locations,
    popup='Animated Route',
    tooltip='Travel Path',
    color='red',
    weight=3,
    delay=200,
    pulse_color='yellow'
)

# Add to map
m.add_child(ant_path)

# Display the map
m
```

### `folium.plugins.antpath.AntPath.__init__` · *method*

## Summary:
Initializes an AntPath object with location coordinates and configurable animation properties.

## Description:
Configures an animated path visualization on a folium map with customizable appearance and animation parameters. This method sets up the internal state for rendering an animated path that moves along a set of coordinates with configurable speed, style, and behavior.

## Args:
    locations (list): List of coordinate pairs (latitude, longitude) defining the path route.
    popup (Popup, optional): Popup message to display on click. Defaults to None.
    tooltip (Tooltip, optional): Tooltip to display on hover. Defaults to None.
    **kwargs: Additional styling and animation options including:
        - paused (bool): Whether animation starts paused. Defaults to False.
        - reverse (bool): Whether to animate in reverse direction. Defaults to False.
        - hardware_acceleration (bool): Enable hardware acceleration. Defaults to False.
        - delay (int): Animation delay in milliseconds. Defaults to 400.
        - dash_array (list): Dash pattern for the path. Defaults to [10, 20].
        - weight (int): Path line weight. Defaults to 5.
        - opacity (float): Path opacity. Defaults to 0.5.
        - color (str): Path color in hex format. Defaults to "#0000FF".
        - pulse_color (str): Pulse color in hex format. Defaults to "#FFFFFF".

## Returns:
    None: This method initializes the object's state and doesn't return a value.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "AntPath"
        - self.options: Initialized with path_options and updated with animation parameters

## Constraints:
    Preconditions:
        - locations must be a list of coordinate pairs
        - Each coordinate pair must contain valid latitude and longitude values
    Postconditions:
        - self._name is set to "AntPath"
        - self.options contains all configured path and animation properties

## Side Effects:
    None

