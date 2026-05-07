# `timestamped_geo_json.py`

## `folium.plugins.timestamped_geo_json.TimestampedGeoJson` · *class*

## Summary:
TimestampedGeoJson is a folium plugin that displays GeoJSON data with temporal dimensions, enabling time-series visualization on interactive maps through a timeline slider interface.

## Description:
TimestampedGeoJson is a specialized folium plugin designed to visualize GeoJSON features that change over time. It wraps temporal geographic data in a time dimension control, allowing users to animate geographic features across time periods. This plugin integrates with the Leaflet TimeDimension library to provide interactive timeline controls for exploring temporal GeoJSON datasets. It serves as a container for temporal geographic data that can be added to folium Map instances.

## State:
- data: str - Raw GeoJSON data string or file-like object containing temporal geographic features
- embed: bool - Flag indicating whether data is embedded (True) or referenced externally (False)
- add_last_point: bool - Whether to add a last point to the animation timeline
- period: str - ISO 8601 period string defining time intervals (default "P1D")
- date_options: str - Format string for displaying dates (default "YYYY-MM-DD HH:mm:ss")
- duration: str or None - Duration string for animation playback or "undefined" if None
- options: dict - Configuration options for the time dimension player with camelCase keys

## Lifecycle:
- Creation: Instantiate with GeoJSON data and optional temporal configuration parameters
- Usage: Add to a folium Map instance using add_child() method, then call render() to generate HTML output
- Destruction: Managed automatically by Python garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[TimestampedGeoJson.__init__] --> B[super().__init__()]
    B --> C[Process data input (file-like, dict, or string)]
    C --> D[Set embed flag and data content]
    D --> E[Parse options with parse_options]
    E --> F[End]

    A --> G[TimestampedGeoJson.render] --> H[assert isinstance(self._parent, Map)]
    H --> I[super().render()]
    I --> J[End]

    A --> K[TimestampedGeoJson._get_self_bounds] --> L[Check embed flag]
    L --> M{embed?}
    M -- No --> N[raise ValueError]
    M -- Yes --> O[json.loads(self.data)]
    O --> P[Normalize GeoJSON structure]
    P --> Q[get_bounds(data, lonlat=True)]
    Q --> R[Return bounds]
```

## Raises:
- ValueError: Raised in _get_self_bounds() when attempting to compute bounds of non-embedded data
- AssertionError: Raised in render() when the element is not added to a Map instance

## Example:
```python
import folium
import json

# Create sample temporal GeoJSON data
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "time": "2023-01-01T00:00:00Z",
                "name": "Point A"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-74.0060, 40.7128]
            }
        }
    ]
}

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Add timestamped GeoJSON layer
timestamped_layer = folium.plugins.TimestampedGeoJson(
    geojson_data,
    period="P1D",
    transition_time=500,
    auto_play=True
)

# Add to map and render
m.add_child(timestamped_layer)
html_output = m._repr_html_()
```

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.__init__` · *method*

## Summary:
Initializes a TimestampedGeoJson plugin instance with geographic data and animation controls.

## Description:
Configures the TimestampedGeoJson plugin by processing input data, setting animation parameters, and preparing options for the JavaScript time slider component. This method handles different data input formats (file-like objects, dictionaries, or raw strings) and initializes the plugin's internal state for rendering animated geographic visualizations on Folium maps.

## Args:
    data (any): Geographic data in various formats - file-like object with read() method, dictionary, or string representation
    transition_time (int): Duration in milliseconds for each transition between timestamps. Defaults to 200
    loop (bool): Whether to loop the animation when reaching the end. Defaults to True
    auto_play (bool): Whether to automatically start the animation. Defaults to True
    add_last_point (bool): Whether to add the last point to the timeline. Defaults to True
    period (str): ISO 8601 period string defining the time interval. Defaults to "P1D"
    min_speed (float): Minimum animation speed multiplier. Defaults to 0.1
    max_speed (float): Maximum animation speed multiplier. Defaults to 10
    loop_button (bool): Whether to display a loop button in the control panel. Defaults to False
    date_options (str): Format string for displaying dates. Defaults to "YYYY-MM-DD HH:mm:ss"
    time_slider_drag_update (bool): Whether to update time during slider dragging. Defaults to False
    duration (str or None): Total duration string for the animation. Defaults to None
    speed_slider (bool): Whether to display a speed control slider. Defaults to True

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TimestampedGeoJson"
    - self.embed: Boolean flag indicating if data should be embedded
    - self.data: Processed geographic data string
    - self.add_last_point: Boolean flag for last point inclusion
    - self.period: Time period string
    - self.date_options: Date formatting string
    - self.duration: Duration string or "undefined"
    - self.options: Dictionary of parsed options for JavaScript component

## Constraints:
    Preconditions:
    - data parameter must be a file-like object with read() method, a dictionary, or a string
    - transition_time must be convertible to integer
    - All numeric parameters must be positive values
    - period must be a valid ISO 8601 period string format
    - duration must be a string or None
    
    Postconditions:
    - self._name is set to "TimestampedGeoJson"
    - self.embed is properly set based on data type
    - self.data contains processed geographic data
    - self.options contains properly formatted configuration for JavaScript component

## Side Effects:
    None

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.render` · *method*

## Summary:
Validates that the TimestampedGeoJson element is properly attached to a Map object before rendering.

## Description:
This method ensures that the TimestampedGeoJson element can only be rendered when it has been correctly added to a Map object. It performs a type assertion to verify that the element's parent is an instance of folium.folium.Map before delegating the rendering process to the parent class. This validation prevents runtime errors that would occur if the element were improperly attached to another container type.

The method exists as a separate override to enforce this critical constraint while preserving the standard rendering behavior for valid use cases. This design choice centralizes the validation logic and prevents misuse of the component.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method

## Returns:
    None: This method does not return any value

## Raises:
    AssertionError: When self._parent is not an instance of folium.folium.Map

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The element must be added to a Map object before calling this method
    Postconditions: The element maintains a valid parent-child relationship with a Map instance

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson._get_self_bounds` · *method*

## Summary:
Computes the geographic bounding box that encompasses all features in the embedded GeoJSON data.

## Description:
This method calculates the minimum and maximum latitude/longitude coordinates that define the spatial extent of the GeoJSON data. It serves as a helper method to determine map view boundaries or geographic scope for timestamped GeoJSON layers. The method validates that the GeoJSON is properly embedded before processing and normalizes various GeoJSON formats into a standard FeatureCollection structure.

## Args:
    None

## Returns:
    list[list[float | None]]: A nested list representing the bounding box with format [[min_lat, min_lon], [max_lat, max_lon]]. Each coordinate can be None if no valid coordinates are provided.

## Raises:
    ValueError: When the GeoJSON data is not embedded (self.embed is False), indicating that bounds computation cannot be performed on non-embedded data.

## State Changes:
    Attributes READ: self.embed, self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The instance must have self.embed set to True (GeoJSON data must be embedded)
    - The self.data attribute must contain valid JSON-formatted GeoJSON data
    - The GeoJSON data must contain geographic coordinates that can be parsed
    
    Postconditions:
    - Returns a valid bounding box representation regardless of input format
    - The returned coordinates are in longitude/latitude order due to lonlat=True parameter

## Side Effects:
    None

