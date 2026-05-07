# `boat_marker.py`

## `folium.plugins.boat_marker.BoatMarker` · *class*

## Summary:
A marker class for displaying boat icons on interactive maps with heading and wind information.

## Description:
The BoatMarker class extends folium's Marker class to represent a marker element on a Folium map that can be positioned at a specific geographic coordinate with optional heading, wind direction, and wind speed properties. This class is designed to work with the Leaflet.BoatMarker JavaScript plugin for enhanced boat visualization capabilities.

## State:
- location: list[float, float] - Geographic coordinates [latitude, longitude]
- heading: int/float value indicating boat direction in degrees (0° = North, 90° = East)
- wind_heading: int/float value indicating wind direction in degrees (None means no wind data)
- wind_speed: int/float value representing wind speed (default 0)
- options: dict containing additional marker options parsed from keyword arguments
- _name: string identifier set to "BoatMarker"

## Lifecycle:
- Creation: Instantiate with location coordinates and optional heading/wind parameters
- Usage: Add to a folium.Map instance using the add_child() method
- Destruction: Managed automatically by folium's map rendering system

## Method Map:
```mermaid
graph TD
    A[BoatMarker.__init__] --> B[Marker.__init__]
    A --> C[JSCSSMixin.__init__]
    B --> D[Super().__init__]
    C --> E[JSCSSMixin.render]
    E --> F[Load leaflet.boatmarker.js]
```

## Raises:
- ValueError: When location is not assigned during direct map addition (inherited from Marker)

## Example:
```python
import folium
from folium.plugins import BoatMarker

# Create a map
m = folium.Map([48.8566, 2.3522], zoom_start=10)

# Create a boat marker with heading and wind data
boat = BoatMarker(
    location=[48.8566, 2.3522],
    heading=45,  # Boat pointing northeast
    wind_heading=90,  # Wind coming from east
    wind_speed=15  # Wind speed of 15 knots
)

# Add to map
m.add_child(boat)
```

### `folium.plugins.boat_marker.BoatMarker.__init__` · *method*

## Summary:
Initializes a BoatMarker instance with location, heading, wind data, and optional popup/icon.

## Description:
This method constructs a BoatMarker object by initializing its parent Marker class and setting boat-specific attributes including heading, wind direction, and wind speed. It processes additional keyword arguments through the parse_options utility to configure marker options.

## Args:
    location (list or tuple): Latitude and longitude coordinates [lat, lng].
    popup (Popup, optional): Popup message to display on marker click. Defaults to None.
    icon (Icon, optional): Custom icon for the marker. Defaults to None.
    heading (int, optional): Boat heading in degrees (0-360). Defaults to 0.
    wind_heading (int, optional): Wind direction in degrees (0-360). Defaults to None.
    wind_speed (float, optional): Wind speed measurement. Defaults to 0.
    **kwargs: Additional options passed to the parent Marker class via parse_options.

## Returns:
    None: This method initializes the object's state rather than returning a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "BoatMarker"
    - self.heading: Set to the provided heading value
    - self.wind_heading: Set to the provided wind_heading value
    - self.wind_speed: Set to the provided wind_speed value
    - self.options: Set to parsed keyword arguments

## Constraints:
    Preconditions:
    - location must be a valid latitude/longitude coordinate pair
    - heading, wind_heading must be integers in range 0-360 if provided
    - wind_speed must be a numeric value
    
    Postconditions:
    - self._name is set to "BoatMarker"
    - All provided arguments are stored as instance attributes
    - self.options contains processed keyword arguments

## Side Effects:
    None: This method performs no I/O operations or external service calls.

