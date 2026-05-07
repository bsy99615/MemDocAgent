# `antpath.py`

## `folium.plugins.antpath.AntPath` · *class*

## Summary:
AntPath is a folium plugin class that renders animated ant-like paths on Leaflet maps, creating a visual effect of a moving line that traverses a series of geographic coordinates.

## Description:
The AntPath class implements an animated path visualization for folium maps by leveraging the leaflet-ant-path JavaScript library. It inherits from JSCSSMixin for JavaScript/CSS dependency management and BaseMultiLocation for handling multiple geographic coordinates. This class is designed to create visually appealing animated routes that simulate movement along a path, commonly used for displaying vehicle trajectories, flight paths, or any sequential geographic data visualization.

## State:
- locations (list[list[float]]): Geographic coordinate pairs stored as [latitude, longitude] lists, validated through BaseMultiLocation inheritance
- _name (str): Set to "AntPath" to identify this element type in Folium's rendering system
- options (dict): Dictionary of styling and animation options for the ant path, including:
  - paused (bool): Whether the animation is initially paused (default: False)
  - reverse (bool): Whether the animation moves in reverse direction (default: False)
  - hardwareAcceleration (bool): Enables hardware acceleration for smoother animations (default: False)
  - delay (int): Delay between animation frames in milliseconds (default: 400)
  - dashArray (list[int]): Array defining the dash pattern for the path (default: [10, 20])
  - weight (int): Width of the path line in pixels (default: 5)
  - opacity (float): Opacity level of the path (default: 0.5)
  - color (str): Color of the path line in hex format (default: "#0000FF")
  - pulseColor (str): Color of the pulse effect at the moving point (default: "#FFFFFF")

## Lifecycle:
- Creation: Instantiate with required locations parameter and optional popup/tooltip. The constructor validates locations and sets up default styling options through BaseMultiLocation's validation and JSCSSMixin's dependency management.
- Usage: During map rendering, the class leverages its inheritance from BaseMultiLocation for location validation and JSCSSMixin for automatic inclusion of the required JavaScript library. The rendering process generates appropriate HTML/JavaScript for the animated path.
- Destruction: Managed automatically through Folium's element lifecycle management system.

## Method Map:
```mermaid
graph TD
    A[AntPath.__init__] --> B[super().__init__()]
    B --> C[self._name = "AntPath"]
    C --> D[self.options = path_options(line=True, **kwargs)]
    D --> E[self.options.update({...})]
    E --> F[End]
```

## Raises:
- TypeError: Raised by BaseMultiLocation.validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: Raised by BaseMultiLocation.validate_locations() when locations is empty or contains invalid coordinate data

## Example:
```python
import folium

# Create a sample map
m = folium.Map([40.7128, -74.0060], zoom_start=10)

# Define a path with multiple coordinates
locations = [
    [40.7128, -74.0060],  # New York City
    [37.7749, -122.4194], # San Francisco
    [34.0522, -118.2437]  # Los Angeles
]

# Create an animated ant path with custom styling
ant_path = folium.plugins.AntPath(
    locations=locations,
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
Initializes an AntPath object with geographic locations and configurable animation properties for creating animated dashed paths on folium maps.

## Description:
The AntPath.__init__ method sets up the foundational configuration for an animated dashed path visualization on folium maps. It inherits from BaseMultiLocation to handle geographic coordinate management and extends JSCSSMixin for proper JavaScript/CSS dependency rendering. This method configures both the core path properties (like color, weight, opacity) and animation-specific parameters (paused, reverse, delay) that control how the dashed line animates across the map.

This initialization logic is separated from other methods to ensure proper inheritance chain execution and centralized configuration setup before the path becomes part of a map rendering pipeline. The method processes both standard path options and custom animation parameters through the path_options utility function.

## Args:
    locations (list[list[float]]): List of [latitude, longitude] coordinate pairs defining the path geometry
    popup (Popup or str, optional): Popup element or string to display when clicking on the path
    tooltip (Tooltip or str, optional): Tooltip element or string to display on hover over the path
    **kwargs: Additional styling and animation parameters including:
        - paused (bool): Whether animation starts paused (default: False)
        - reverse (bool): Whether animation moves in reverse direction (default: False)
        - hardware_acceleration (bool): Enable hardware acceleration (default: False)
        - delay (int): Animation delay in milliseconds (default: 400)
        - dash_array (list[int]): Dash pattern array (default: [10, 20])
        - weight (int): Path line weight in pixels (default: 5)
        - opacity (float): Path opacity (default: 0.5)
        - color (str): Path color in hex format (default: "#0000FF")
        - pulse_color (str): Pulse color in hex format (default: "#FFFFFF")

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    TypeError: From BaseMultiLocation.__init__ when locations is not iterable with coordinate pairs
    ValueError: From BaseMultiLocation.__init__ when locations is empty or contains invalid coordinates
    AssertionError: From Popup/Tooltip constructors if invalid arguments are provided

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "AntPath" to identify this element type
        - self.options: Dictionary containing path styling and animation options

## Constraints:
    Preconditions:
        - locations must be a valid iterable of coordinate pairs [lat, lng]
        - Each coordinate pair must contain valid numeric latitude (-90 to 90) and longitude (-180 to 180) values
        - popup and tooltip parameters must be valid Popup/Tooltip objects or convertible strings
    Postconditions:
        - self._name is set to "AntPath"
        - self.options contains all configured path and animation properties
        - The object is ready for inclusion in a folium map rendering pipeline

## Side Effects:
    - Calls super().__init__() to establish inheritance chain with BaseMultiLocation
    - Processes and consumes kwargs parameters through path_options and dict.pop operations
    - Sets up internal state for JavaScript/CSS rendering via JSCSSMixin inheritance

