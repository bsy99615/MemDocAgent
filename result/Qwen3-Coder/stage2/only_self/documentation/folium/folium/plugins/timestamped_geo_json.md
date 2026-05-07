# `timestamped_geo_json.py`

## `folium.plugins.timestamped_geo_json.TimestampedGeoJson` · *class*

## Summary:
A folium plugin for displaying GeoJSON data with temporal dimensions, enabling time-based visualization on interactive maps.

## Description:
TimestampedGeoJson is a specialized folium element that renders GeoJSON features with associated timestamps, allowing users to visualize geospatial data that changes over time. It integrates with Leaflet TimeDimension library to provide interactive playback controls, time sliders, and temporal filtering capabilities. This class is specifically designed for time-series geospatial data visualization, offering playback controls, speed adjustment, and temporal navigation that standard GeoJSON layers lack.

The class intelligently handles different data input formats (file-like objects, dictionaries, or string URLs) and manages JavaScript/CSS dependencies for the time dimension functionality. It provides extensive configuration options for playback behavior including transition times, looping, auto-play, and speed controls.

## State:
- _template: Template - Empty Jinja2 template (required by MacroElement base class)
- default_js: list[tuple[str, str]] - Default JavaScript dependencies for time dimension functionality
- default_css: list[tuple[str, str]] - Default CSS dependencies for time dimension controls
- data: str - The GeoJSON data, either embedded (as string) or referenced externally (as URL/path)
- embed: bool - Flag indicating whether the GeoJSON data is embedded (True) or referenced externally (False)
- add_last_point: bool - Whether to add the last point of the time series to the map
- period: str - ISO 8601 period string defining the time interval between data points
- date_options: str - Format string for displaying dates in the time slider
- duration: str - Duration string for time dimension control, or "undefined" if None
- options: dict - Configuration options for the time dimension player, including playback settings and UI controls

## Lifecycle:
- Creation: Instantiate with GeoJSON data and optional configuration parameters
- Usage: Add to a folium Map instance using `map.add_child(timestamped_geojson)` followed by `map.render()` 
- Destruction: Managed automatically through folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[TimestampedGeoJson.__init__] --> B[TimestampedGeoJson.render]
    B --> C[super().render()]
    A --> D[TimestampedGeoJson._get_self_bounds]
    D --> E[get_bounds()]
```

## Raises:
- AssertionError: When attempting to render the element outside of a Map context
- ValueError: When trying to compute bounds of non-embedded GeoJSON data

## Example:
```python
import folium
import json

# Example 1: Basic usage with embedded GeoJSON data
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "time": "2023-01-01T00:00:00Z"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-122.4194, 37.7749]
            }
        }
    ]
}

# Create map and add timestamped GeoJSON layer
m = folium.Map([37.7749, -122.4194], zoom_start=10)
timestamped_layer = folium.plugins.TimestampedGeoJson(
    geojson_data,
    transition_time=500,
    auto_play=True,
    loop=True
)
m.add_child(timestamped_layer)
m.save('map_with_timestamped_geojson.html')

# Example 2: Using external GeoJSON file reference
external_geojson_path = "path/to/your/data.geojson"
m2 = folium.Map([37.7749, -122.4194], zoom_start=10)
timestamped_layer2 = folium.plugins.TimestampedGeoJson(
    external_geojson_path,
    transition_time=1000,
    auto_play=False,
    loop=False,
    period="P1D"  # Daily period
)
m2.add_child(timestamped_layer2)
m2.save('map_external_geojson.html')
```

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.__init__` · *method*

## Summary:
Initializes a TimestampedGeoJson object that renders time-series GeoJSON data with interactive playback controls.

## Description:
Configures a TimestampedGeoJson element for displaying GeoJSON features that change over time. This method handles data preprocessing, option setup, and initialization of visualization parameters for time-based geographic data.

## Args:
    data: The GeoJSON data to display, which can be a file-like object, dictionary, or string/URL reference.
    transition_time (int): Duration in milliseconds for transitions between time steps. Defaults to 200.
    loop (bool): Whether to loop playback when reaching the end. Defaults to True.
    auto_play (bool): Whether to automatically start playback. Defaults to True.
    add_last_point (bool): Whether to add the last point to the timeline. Defaults to True.
    period (str): ISO 8601 period string defining the time interval. Defaults to "P1D".
    min_speed (float): Minimum playback speed multiplier. Defaults to 0.1.
    max_speed (float): Maximum playback speed multiplier. Defaults to 10.
    loop_button (bool): Whether to show a loop button in the control panel. Defaults to False.
    date_options (str): Format string for date display. Defaults to "YYYY-MM-DD HH:mm:ss".
    time_slider_drag_update (bool): Whether to update time during slider dragging. Defaults to False.
    duration (str): Total duration string for playback. Defaults to None.
    speed_slider (bool): Whether to show a speed adjustment slider. Defaults to True.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TimestampedGeoJson"
    - self.embed: Boolean flag indicating if data should be embedded
    - self.data: Processed GeoJSON data string
    - self.add_last_point: Boolean flag for last point handling
    - self.period: Time period string
    - self.date_options: Date formatting string
    - self.duration: Duration string or "undefined"
    - self.options: Dictionary of configuration options for the JavaScript component

## Constraints:
    Preconditions:
    - data parameter must be a file-like object, dict, or string/URL reference
    - transition_time must be convertible to integer
    - min_speed and max_speed must be numeric values
    - duration, if provided, must be a string
    Postconditions:
    - self._name is set to "TimestampedGeoJson"
    - self.data is properly formatted as a JSON string
    - self.options contains properly formatted camelCase configuration

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.render` · *method*

## Summary:
Validates that the TimestampedGeoJson element is properly attached to a Map object before proceeding with the standard rendering process.

## Description:
This method ensures that the TimestampedGeoJson element has been correctly added to a Map instance before allowing it to render. It performs a type assertion to confirm the parent is of type Map, which is a requirement for proper integration with the Leaflet.js map rendering system. After validation, it delegates to the parent class's render method to handle the actual rendering process.

The method exists as a separate validation step rather than being inlined because it enforces a critical constraint about the element's placement within the folium element hierarchy. This prevents runtime errors that could occur if the element were rendered without a proper map context.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method for rendering configuration.

## Returns:
    None: This method does not return any value.

## Raises:
    AssertionError: When the `_parent` attribute is not an instance of the Map class, indicating the element has not been properly added to a map.

## State Changes:
    Attributes READ: 
    - self._parent: The parent element that this TimestampedGeoJson is attached to
    
    Attributes WRITTEN: 
    - None: This method does not modify any attributes of the object itself

## Constraints:
    Preconditions:
    - The `_parent` attribute must be set to a valid Map instance before calling this method
    - The element must have been added to a Map using the `add_child()` method
    
    Postconditions:
    - The method will either complete successfully (returning None) or raise an AssertionError
    - The parent's render method will be called with the provided kwargs

## Side Effects:
    None: This method does not perform any I/O operations, external service calls, or mutations to objects outside the current instance.

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson._get_self_bounds` · *method*

## Summary:
Computes the geographical bounding box for embedded GeoJSON data.

## Description:
Retrieves the minimum and maximum latitude/longitude coordinates that encompass all geographic features in the embedded GeoJSON data. This method ensures the data is properly formatted as a GeoJSON FeatureCollection before calculating bounds.

## Args:
    None

## Returns:
    list[list[float]]: A bounding box represented as [[min_lat, min_lng], [max_lat, max_lng]] where coordinates are in longitude/latitude order. Returns [[None, None], [None, None]] when no valid coordinates exist.

## Raises:
    ValueError: When the GeoJSON data is not embedded (self.embed is False).

## State Changes:
    Attributes READ: self.embed, self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The instance must have embedded GeoJSON data (self.embed must be True)
    - The self.data attribute must contain valid JSON-formatted GeoJSON data
    - The GeoJSON data must contain geographic features with coordinates
    
    Postconditions:
    - Returns a properly formatted bounding box list
    - Does not modify any instance attributes

## Side Effects:
    None

