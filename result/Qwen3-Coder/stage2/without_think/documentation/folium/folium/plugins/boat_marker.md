# `boat_marker.py`

## `folium.plugins.boat_marker.BoatMarker` · *class*

## Summary:
A marker class that inherits from JSCSSMixin and Marker for specialized map visualization.

## Description:
The BoatMarker class is a specialized marker implementation that inherits from both JSCSSMixin and Marker. It is designed to work with the Leaflet.BoatMarker JavaScript library to provide enhanced marker functionality for map visualization. The class extends the basic Marker functionality by adding properties for boat-specific data including heading, wind heading, and wind speed.

## State:
- heading (int or float): The direction the boat is pointing, measured in degrees from north (0°). Default is 0.
- wind_heading (int or float or None): The direction the wind is coming from, measured in degrees from north. Default is None.
- wind_speed (int or float): The speed of the wind affecting the boat, typically in knots or mph. Default is 0.
- _name (str): Class identifier set to "BoatMarker" for internal tracking and rendering.
- options (dict): Configuration options processed via parse_options() for additional marker behavior.

## Lifecycle:
- Creation: Instantiate with location and optional parameters (heading, wind_heading, wind_speed, popup, icon, etc.). The constructor calls the parent Marker's __init__ method and sets the class name.
- Usage: Add to a folium Map or Figure using standard element addition methods. The marker will automatically include required JavaScript resources when rendered.
- Destruction: Managed automatically by folium's element lifecycle management.

## Method Map:
```mermaid
graph TD
    A[BoatMarker.__init__] --> B[super().__init__()]
    B --> C[Set _name="BoatMarker"]
    C --> D[Set heading, wind_heading, wind_speed]
    D --> E[Process options with parse_options]
    E --> F[Finish initialization]

    G[BoatMarker.render] --> H[super().render()]
    H --> I[Include JS resources via JSCSSMixin]
    I --> J[Render with template and options]
```

## Raises:
- ValueError: When render() is called and the marker's location attribute is None, requiring location assignment before direct map addition.
- AssertionError: When the element is not contained within a Figure context during rendering, with message "You cannot render this Element if it is not in a Figure."

## Example:
```python
import folium

# Create a map centered on a maritime area
m = folium.Map(location=[45.5236, -122.6750], zoom_start=10)

# Create a boat marker with heading and wind data
boat = folium.plugins.BoatMarker(
    location=[45.5236, -122.6750],
    heading=45,  # Boat pointing northeast
    wind_heading=270,  # Wind coming from west
    wind_speed=15,  # 15 knots wind
    popup="Sailing vessel at position",
    icon=folium.Icon(color='blue', icon='ship')
)

# Add boat marker to map
boat.add_to(m)

# Render the map
m.save("boat_map.html")
```

### `folium.plugins.boat_marker.BoatMarker.__init__` · *method*

## Summary:
Initializes a BoatMarker object with geographic location, heading, wind conditions, and configurable options for display on folium maps.

## Description:
The BoatMarker constructor creates a specialized marker for nautical applications that displays boat-like icons with directional orientation and wind information. This method sets up the base marker functionality through inheritance and adds boat-specific attributes for rendering boat-like visualizations with proper heading and wind data.

This logic is encapsulated in its own method to separate the initialization concerns of the base Marker functionality from the boat-specific attributes, allowing for clean inheritance and extension of marker behavior while maintaining the specialized boat visualization features.

## Args:
    location (list[float]): Geographic coordinates [latitude, longitude] for the boat marker position.
    popup (Popup or None, optional): Popup element to display additional information when clicking the marker. Defaults to None.
    icon (Icon or None, optional): Custom icon element to modify marker appearance. Defaults to None.
    heading (float, optional): Direction the boat is pointing in degrees (0° = North, 90° = East). Defaults to 0.
    wind_heading (float or None, optional): Wind direction in degrees (0° = North, 90° = East). Defaults to None.
    wind_speed (float, optional): Wind speed measurement. Defaults to 0.
    **kwargs: Additional configuration options passed to the parent Marker class and processed via parse_options.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though parent class initialization may raise exceptions for invalid parameters.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "BoatMarker" string
    - self.heading: Set to the provided heading value
    - self.wind_heading: Set to the provided wind_heading value
    - self.wind_speed: Set to the provided wind_speed value
    - self.options: Set to parsed keyword arguments from kwargs

## Constraints:
    Preconditions:
    - The location parameter must be a valid geographic coordinate pair [latitude, longitude]
    - All numeric parameters (heading, wind_heading, wind_speed) should be valid numbers
    - The parent Marker class validation applies to location, popup, and icon parameters
    Postconditions:
    - The object is properly initialized with all specified attributes
    - The _name attribute is set to "BoatMarker"
    - All provided parameters are stored as instance attributes
    - Additional keyword arguments are processed and stored in the options dictionary

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

