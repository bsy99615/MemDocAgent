# `timestamped_geo_json.py`

## `folium.plugins.timestamped_geo_json.TimestampedGeoJson` · *class*

## Summary:
A folium plugin for displaying time-series GeoJSON data with interactive timeline controls.

## Description:
The TimestampedGeoJson class enables visualization of geographic data that changes over time by creating an interactive timeline control. It allows users to play, pause, and scrub through temporal GeoJSON datasets on a map. This class is particularly useful for visualizing dynamic geographic phenomena such as weather patterns, movement trajectories, or historical events.

The class handles various data input formats including file objects, dictionaries, and raw GeoJSON strings. It embeds the data directly into the map output or references external data sources, and provides extensive configuration options for playback behavior including transition times, looping, auto-play settings, and speed controls.

## State:
- data: str - Raw GeoJSON data string or path to external data file
- embed: bool - Flag indicating whether data is embedded in the output (True) or referenced externally (False)
- add_last_point: bool - Whether to display the last point of each feature in the timeline
- period: str - ISO 8601 period string defining the time interval between data points (default: "P1D")
- date_options: str - Format string for displaying dates in the timeline control (default: "YYYY-MM-DD HH:mm:ss")
- duration: str or None - Duration string for the timeline playback (default: None)
- options: dict - Configuration options for the timeline player, including playback settings and UI controls

## Lifecycle:
- Creation: Instantiate with GeoJSON data and optional configuration parameters
- Usage: Add to a folium Map using the add_child() method, then render the map
- Destruction: Managed automatically by folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[TimestampedGeoJson.__init__] --> B[TimestampedGeoJson.render]
    B --> C[super().render]
    A --> D[TimestampedGeoJson._get_self_bounds]
    D --> E[get_bounds]
```

## Raises:
- AssertionError: In render() method when the element is not properly attached to a Map
- ValueError: In _get_self_bounds() when trying to compute bounds of non-embedded data

## Example:
```python
import folium
from folium.plugins import TimestampedGeoJson

# Create a sample GeoJSON with timestamps
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
                "coordinates": [0, 0]
            }
        }
    ]
}

# Create map and add timestamped geojson layer
m = folium.Map([0, 0], zoom_start=2)
timestamped_layer = TimestampedGeoJson(
    geojson_data,
    period="P1D",
    transition_time=200,
    auto_play=True,
    loop=True
)
m.add_child(timestamped_layer)
m.save("map.html")
```

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.__init__` · *method*

## Summary:
Initializes a TimestampedGeoJson object with configuration options and processes input GeoJSON data for time-series visualization.

## Description:
Configures the TimestampedGeoJson plugin by setting up data handling, playback options, and UI controls for interactive time-series GeoJSON visualization. This method determines how the GeoJSON data is embedded or referenced, processes various input formats, and configures the timeline player behavior including transition times, looping, auto-play settings, and speed controls.

## Args:
    data (str, dict, or file-like object): GeoJSON data in string format, dictionary representation, or file-like object with a read() method. Determines how data is handled (embedded vs external reference).
    transition_time (int, optional): Time in milliseconds for transitions between time steps. Defaults to 200.
    loop (bool, optional): Whether to loop playback when reaching the end. Defaults to True.
    auto_play (bool, optional): Whether to automatically start playback. Defaults to True.
    add_last_point (bool, optional): Whether to display the last point of each feature in the timeline. Defaults to True.
    period (str, optional): ISO 8601 period string defining time intervals between data points. Defaults to "P1D".
    min_speed (float, optional): Minimum playback speed multiplier. Defaults to 0.1.
    max_speed (float, optional): Maximum playback speed multiplier. Defaults to 10.
    loop_button (bool, optional): Whether to show a loop button in the UI. Defaults to False.
    date_options (str, optional): Format string for displaying dates in the timeline control. Defaults to "YYYY-MM-DD HH:mm:ss".
    time_slider_drag_update (bool, optional): Whether to update playback while dragging the time slider. Defaults to False.
    duration (str or None, optional): Duration string for timeline playback. Defaults to None.
    speed_slider (bool, optional): Whether to show a speed adjustment slider. Defaults to True.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying operations may raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TimestampedGeoJson"
    - self.embed: Boolean flag indicating data embedding status
    - self.data: Processed GeoJSON data string or path
    - self.add_last_point: Boolean flag for last point display
    - self.period: ISO 8601 period string
    - self.date_options: Date formatting string
    - self.duration: Formatted duration string or "undefined"
    - self.options: Dictionary of configuration options for the timeline player

## Constraints:
    Preconditions:
    - data parameter must be a string, dictionary, or object with a read() method
    - transition_time must be convertible to integer
    - min_speed and max_speed must be numeric values
    - period must be a valid ISO 8601 period string
    - duration must be a string or None
    Postconditions:
    - self._name is set to "TimestampedGeoJson"
    - self.embed is properly set based on data type
    - self.data is normalized to a string format
    - self.options contains properly formatted configuration options

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.render` · *method*

## Summary:
Validates that the TimestampedGeoJson element is properly attached to a Map object before delegating rendering to the parent class.

## Description:
This method ensures that the TimestampedGeoJson element can only be rendered when it has been properly added to a Map object. It performs a type assertion to verify the parent relationship and then calls the parent's render method to handle the actual rendering process. This validation prevents runtime errors that could occur if the element were rendered outside of a proper map context.

The method is separated from inline logic to enforce proper usage patterns and maintain consistency with folium's element architecture where all visual components must be children of a Map.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method

## Returns:
    None: This method does not return any value

## Raises:
    AssertionError: When the element's _parent attribute is not an instance of folium.folium.Map

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The element must have been added to a Map using add_child() before calling render()
    Postconditions: The element will be validated as being part of a Map before proceeding with rendering

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson._get_self_bounds` · *method*

## Summary:
Computes the geographical bounding box for the embedded GeoJSON data.

## Description:
Retrieves the minimum and maximum latitude/longitude coordinates that encompass all geographic features in the embedded GeoJSON data. This method is used to determine the spatial extent of the data for map view initialization or spatial queries.

## Args:
    None

## Returns:
    list[list[float | None]]: A bounding box represented as [[min_lat, min_lon], [max_lat, max_lon]] where:
        - First inner list contains minimum latitude and longitude
        - Second inner list contains maximum latitude and longitude
        - Values may be None if no coordinates are provided
        - Returns [[None, None], [None, None]] when no valid coordinates are found

## Raises:
    ValueError: When the GeoJSON data is not embedded (self.embed is False), indicating that bounds cannot be computed locally.

## State Changes:
    Attributes READ: self.embed, self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The instance must have embedded GeoJSON data (self.embed must be True)
        - The self.data attribute must contain valid JSON-formatted GeoJSON data
    Postconditions:
        - Returns a valid bounding box representation
        - All returned coordinates are either numeric values or None

## Side Effects:
    None

