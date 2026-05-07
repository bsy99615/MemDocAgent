# `boat_marker.py`

## `folium.plugins.boat_marker.BoatMarker` · *class*

## Summary:
BoatMarker is a specialized marker class for folium maps that displays boat-shaped icons with orientation and wind direction indicators.

## Description:
BoatMarker extends the standard Marker class to provide specialized visualization for maritime applications. It renders boat-shaped markers on folium maps with configurable heading and wind information. The class leverages the leaflet.boatmarker JavaScript library to achieve the specialized boat marker rendering functionality. This abstraction allows developers to easily display boats with directional indicators on interactive maps, particularly useful for marine navigation, fleet tracking, or sailing applications.

## State:
- heading (int or float): Boat's current heading in degrees (0-360), defaults to 0
- wind_heading (int or float or None): Wind direction in degrees (0-360), defaults to None
- wind_speed (int or float): Wind speed measurement, defaults to 0
- _name (str): Class identifier set to "BoatMarker" for internal Folium processing
- options (dict): Additional configuration options processed via parse_options

## Lifecycle:
- Creation: Instantiate with location and optional heading, wind_heading, wind_speed parameters
- Usage: Add to a folium Map instance using add_child() method, then render within a Figure context
- Destruction: Managed automatically through the Element parent-child relationship system

## Method Map:
```mermaid
graph TD
    A[BoatMarker.__init__] --> B[super().__init__()]
    B --> C[self._name = "BoatMarker"]
    C --> D[self.heading = heading]
    D --> E[self.wind_heading = wind_heading]
    E --> F[self.wind_speed = wind_speed]
    F --> G[self.options = parse_options(**kwargs)]
    G --> H[End]

    I[BoatMarker.render] --> J[super().render()]
    J --> K[End]
```

## Raises:
- ValueError: When render() is called and location has not been assigned (inherited from Marker)
- AssertionError: When trying to render outside of a Figure context (inherited from parent classes)

## Example:
```python
import folium

# Create a boat marker at a specific location
boat = folium.plugins.BoatMarker(
    location=[40.7128, -74.0060],  # New York City coordinates
    heading=45,                    # Heading northeast
    wind_heading=90,               # Wind from the east
    wind_speed=15                  # Wind speed of 15 knots
)

# Add to a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)
m.add_child(boat)
```

### `folium.plugins.boat_marker.BoatMarker.__init__` · *method*

## Summary:
Initializes a BoatMarker instance with location, heading, wind direction, and additional configuration options.

## Description:
The BoatMarker.__init__ method sets up a specialized marker for maritime visualization by configuring the boat's orientation, wind conditions, and additional map options. This method extends the standard Marker initialization to include boat-specific properties like heading and wind data, while also setting up the necessary configuration for the leaflet.boatmarker JavaScript library integration.

## Args:
    location (array-like): Geographic coordinates as [latitude, longitude].
    popup (Popup or str, optional): Popup element or HTML string to display on marker click. Defaults to None.
    icon (Icon, optional): Custom icon for the marker. Defaults to None.
    heading (int or float): Boat's current heading in degrees (0-360). Defaults to 0.
    wind_heading (int or float or None): Wind direction in degrees (0-360). Defaults to None.
    wind_speed (int or float): Wind speed measurement. Defaults to 0.
    **kwargs: Additional options passed to the marker's configuration.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "BoatMarker"
    - self.heading: Set to provided heading value
    - self.wind_heading: Set to provided wind_heading value
    - self.wind_speed: Set to provided wind_speed value
    - self.options: Set to parsed kwargs dictionary

## Constraints:
    Preconditions:
    - Location must be a valid coordinate pair
    - Heading should be a numeric value representing degrees (0-360)
    - Wind heading should be a numeric value representing degrees (0-360) or None
    - Wind speed should be a numeric value
    
    Postconditions:
    - self._name is always set to "BoatMarker"
    - All provided parameters are stored as instance attributes
    - Additional options are processed through parse_options() for JavaScript compatibility

## Side Effects:
    - Calls super().__init__() to initialize parent Marker class
    - Calls parse_options() to process additional configuration options

