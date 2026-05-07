# `timestamped_wmstilelayer.py`

## `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers` · *class*

## Summary:
TimestampedWmsTileLayers is a specialized map layer class that enables time-series visualization of Web Map Service (WMS) tile layers with temporal controls in folium interactive maps.

## Description:
This class extends JSCSSMixin and Layer to create a time-enabled overlay that displays multiple WMS tile layers with temporal dimension support. It integrates with Leaflet TimeDimension library to provide playback controls and time-based layer switching. The class is designed to work with folium's map rendering system and automatically includes required JavaScript and CSS dependencies for temporal functionality.

The class accepts either a single WmsTileLayer or a list of WmsTileLayers and provides temporal controls for navigating through time-series data. It's particularly useful for visualizing geospatial data that changes over time, such as weather patterns, satellite imagery, or environmental monitoring data.

## State:
- layers: List of WmsTileLayer objects that represent the time-series data to be displayed
- options: Dictionary of temporal configuration options parsed from period and time_interval parameters
- options_control: Dictionary of player control options including transition time, looping, and autoplay settings  
- _name: String identifier set to "TimestampedWmsTileLayers" for internal tracking
- default_js: Class attribute containing list of default JavaScript dependencies for temporal functionality
- default_css: Class attribute containing list of default CSS dependencies for temporal controls

## Lifecycle:
- Creation: Instantiated with data (WmsTileLayer or list of WmsTileLayers), optional temporal parameters, and layer metadata
- Usage: Added to a folium Map instance via add_child() method; automatically handles JavaScript/CSS dependency injection through JSCSSMixin
- Destruction: Managed by folium's map lifecycle management system

## Method Map:
```mermaid
graph TD
    A[TimestampedWmsTileLayers.__init__] --> B[super().__init__()]
    B --> C[self._name = "TimestampedWmsTileLayers"]
    C --> D[self.options = parse_options(...)]
    D --> E[self.options_control = parse_options(...)]
    E --> F[Process data parameter]
    F --> G[Set self.layers]
```

## Raises:
- None explicitly raised in __init__
- May propagate exceptions from parent class initialization or parse_options function

## Example:
```python
import folium
from folium.raster_layers import WmsTileLayer

# Create a WMS layer
wms_layer = WmsTileLayer(
    url="https://example.com/wms",
    layers="temperature",
    name="Temperature Layer"
)

# Create timestamped layer with temporal controls
timestamped_layer = TimestampedWmsTileLayers(
    data=wms_layer,
    transition_time=500,
    loop=True,
    auto_play=True,
    period="P1D"
)

# Add to map
m = folium.Map(location=[40, -100], zoom_start=4)
m.add_child(timestamped_layer)
```

### `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers.__init__` · *method*

## Summary:
Initializes a TimestampedWmsTileLayers object with time-series WMS tile layers and configuration options.

## Description:
Configures the timestamped WMS tile layer container by setting up its name, options for time handling, and control panel settings. This method establishes the foundational structure for displaying time-series WMS data with interactive time controls.

## Args:
    data: Either a single WmsTileLayer instance or a list of WmsTileLayer instances representing the time-series data layers.
    transition_time (int): Duration in milliseconds for transitions between time steps. Defaults to 200.
    loop (bool): Whether to loop the animation when reaching the end. Defaults to False.
    auto_play (bool): Whether to automatically start playing the time series. Defaults to False.
    period (str): ISO 8601 duration string defining the time period. Defaults to "P1D".
    time_interval (bool): Whether to enable time interval display. Defaults to False.
    name (str): Name identifier for the layer. Defaults to None.

## Returns:
    None: This method initializes the object's attributes and does not return a value.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TimestampedWmsTileLayers"
    - self.options: Set to parsed options for time period and interval
    - self.options_control: Set to parsed options for control panel settings
    - self.layers: Set to either a list containing a single WmsTileLayer or the provided list of layers

## Constraints:
    Preconditions:
    - data must be either a WmsTileLayer instance or a list-like object containing WmsTileLayer instances
    - transition_time must be convertible to an integer
    - period must be a valid ISO 8601 duration string
    - time_interval must be a boolean value
    
    Postconditions:
    - self._name is set to "TimestampedWmsTileLayers"
    - self.options contains parsed time period and interval settings
    - self.options_control contains parsed control panel settings including transition time and loop behavior
    - self.layers is always a list of WmsTileLayer instances

## Side Effects:
    None

