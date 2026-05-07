# `boat_marker.py`

## `folium.plugins.boat_marker.BoatMarker` · *class*

## Summary:
A specialized marker class for displaying boat-oriented elements on folium maps with heading and wind information.

## Description:
The BoatMarker class extends folium's standard Marker functionality to represent boats on interactive maps. It provides enhanced visualization capabilities for maritime applications by incorporating boat-specific properties such as heading direction and wind conditions. This class is designed to work with the Leaflet.BoatMarker JavaScript library, enabling boats to be displayed with proper orientation and environmental data.

This class should be instantiated when creating interactive boat markers on folium maps, particularly in maritime navigation, fleet tracking, or sailing applications. It is typically created by map components when adding specialized boat markers to maps.

## State:
- heading: int or float - Boat's heading direction in degrees (0-360), default is 0
- wind_heading: int, float, or None - Wind direction in degrees (0-360), default is None
- wind_speed: int or float - Wind speed measurement, default is 0
- _name: str - Set to "BoatMarker" for internal identification
- _template: Template - Jinja2 template for rendering the boat marker HTML, currently empty
- options: dict - Processed keyword arguments converted to camelCase format via parse_options()

## Lifecycle:
Creation: Instantiate with required location parameter and optional heading, wind_heading, wind_speed parameters. The location must be a valid coordinate pair [latitude, longitude].
Usage: Add to a folium map using add_child() method. The render() method will automatically handle JavaScript/CSS inclusion through JSCSSMixin inheritance.
Destruction: Managed automatically by folium's rendering system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[BoatMarker.__init__] --> B[super().__init__]
    B --> C[Set _name to "BoatMarker"]
    C --> D[Set heading, wind_heading, wind_speed]
    D --> E[Parse kwargs with parse_options]
    E --> F[BoatMarker.render]
    F --> G[JSCSSMixin.render]
    G --> H[Marker.render]
    H --> I[super().render()]
```

## Raises:
- ValueError: When render() is called and location is None (inherited from Marker)
- AssertionError: When the element is not contained within a Figure instance during rendering (inherited from JSCSSMixin)

## Example:
```python
import folium

# Create a boat marker at a specific location
boat = folium.plugins.BoatMarker(
    location=[40.7128, -74.0060],
    heading=45,
    wind_heading=90,
    wind_speed=15
)

# Add to a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)
m.add_child(boat)
```

### `folium.plugins.boat_marker.BoatMarker.__init__` · *method*

## Summary:
Initializes a BoatMarker instance with location, heading, wind information, and optional popup/icon parameters.

## Description:
The BoatMarker.__init__ method constructs a specialized marker for maritime applications by setting up the boat's position, orientation (heading), and environmental conditions (wind heading and speed). This method extends the standard Marker functionality to support boat-specific visualization properties and integrates with folium's rendering system through JSCSSMixin inheritance.

This initialization method is called during the creation phase of a BoatMarker object, typically when developers instantiate boat markers for display on folium maps. The method properly configures the object's state and prepares it for rendering with the Leaflet.BoatMarker JavaScript library.

## Args:
    location (list[float]): Geographic coordinates [latitude, longitude] defining the boat's position on the map.
    popup (Popup, optional): Popup element to display additional information when the marker is clicked. Defaults to None.
    icon (Icon, optional): Custom icon to override the default marker appearance. Defaults to None.
    heading (int or float, optional): Boat's heading direction in degrees (0-360), where 0° is north. Defaults to 0.
    wind_heading (int, float, or None, optional): Wind direction in degrees (0-360), where 0° is north. Defaults to None.
    wind_speed (int or float, optional): Wind speed measurement. Defaults to 0.
    **kwargs: Additional keyword arguments passed to parse_options for JavaScript configuration.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    ValueError: When render() is called and location is None (inherited from Marker).
    AssertionError: When the element is not contained within a Figure instance during rendering (inherited from JSCSSMixin).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "BoatMarker" for internal identification
        - self.heading: Assigned the heading parameter value
        - self.wind_heading: Assigned the wind_heading parameter value
        - self.wind_speed: Assigned the wind_speed parameter value
        - self.options: Set to parsed kwargs through parse_options()

## Constraints:
    Preconditions:
        - The location parameter must be a valid coordinate pair [latitude, longitude]
        - All numeric parameters (heading, wind_heading, wind_speed) should be within reasonable ranges
        - The BoatMarker must be added to a folium Figure instance before rendering
    Postconditions:
        - The object is properly initialized with all specified parameters
        - The _name attribute is set to "BoatMarker"
        - The heading, wind_heading, and wind_speed attributes are assigned their respective values
        - The options dictionary contains processed keyword arguments in camelCase format

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes and calls the parent class constructor.

