# `timestamped_wmstilelayer.py`

## `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers` · *class*

## Summary:
A folium plugin for creating timestamped WMS tile layers that support temporal animation over time periods.

## Description:
The TimestampedWmsTileLayers class extends folium's Layer functionality to create interactive map layers that can display WMS (Web Map Service) tiles with temporal dimensions. This allows users to visualize geospatial data that changes over time, such as weather patterns, satellite imagery, or environmental monitoring data. The class integrates with leaflet-timeDimension library to provide playback controls and time-based filtering capabilities.

This component is particularly useful for creating animated maps that show how spatial data evolves over time periods. It accepts either a single WmsTileLayer or a collection of them, and provides configuration options for controlling the animation behavior including transition time, looping, and auto-play settings.

## State:
- layers: List of WmsTileLayer objects that represent the temporal layers to be displayed
- options: Dictionary of configuration options for time period handling, parsed via parse_options with period and time_interval parameters
- options_control: Dictionary of configuration options for the time control UI, including player settings like transition time and loop behavior
- _name: String identifier for the layer, hardcoded to "TimestampedWmsTileLayers"
- _template: Jinja2 Template object (empty in current implementation)
- default_js: List of tuples specifying default JavaScript resources required for time dimension functionality
- default_css: List of tuples specifying default CSS resources required for time dimension controls

## Lifecycle:
- Creation: Instantiated with data (single WmsTileLayer or list of WmsTileLayers), and optional configuration parameters
- Usage: Typically added to a folium.Map object, where it renders with time-based controls
- Destruction: Managed by folium's garbage collection system

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
- TypeError: Raised when data parameter is neither a WmsTileLayer instance nor a list-like object that can be assigned to self.layers

## Example:
```python
import folium
from folium.raster_layers import WmsTileLayer

# Create a WMS layer
wms_layer = WmsTileLayer(
    url="https://example.com/wms",
    layers="temperature",
    name="Temperature Data"
)

# Create timestamped WMS layers with animation controls
timestamped_layers = TimestampedWmsTileLayers(
    data=wms_layer,
    transition_time=500,
    loop=True,
    auto_play=True,
    period="P1D"
)

# Add to map
m = folium.Map(location=[40, -100], zoom_start=4)
timestamped_layers.add_to(m)
```

### `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers.__init__` · *method*

## Summary:
Initializes a TimestampedWmsTileLayers object with time-based visualization capabilities for WMS tile layers.

## Description:
Configures a timestamped WMS tile layer container that enables time-series visualization of WMS (Web Map Service) layers. This method sets up the core configuration options for temporal rendering, including transition timing, looping behavior, and automatic playback settings. The method accepts either a single WmsTileLayer or a collection of WmsTileLayers and properly structures them for time-based rendering.

## Args:
    data (WmsTileLayer or list[WmsTileLayer]): Single WMS tile layer or list of WMS tile layers to be time-stamped.
    transition_time (int): Duration in milliseconds for transitions between time steps. Defaults to 200.
    loop (bool): Whether to loop the animation when reaching the end. Defaults to False.
    auto_play (bool): Whether to automatically start the time series playback. Defaults to False.
    period (str): ISO 8601 duration string defining the time period for the time series. Defaults to "P1D".
    time_interval (bool): Whether to enable time interval selection. Defaults to False.
    name (str, optional): Unique identifier for the layer. Defaults to None.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TimestampedWmsTileLayers"
    - self.options: Configured with period and time_interval parameters
    - self.options_control: Configured with position, auto_play, and player_options
    - self.layers: Set to a list containing the data parameter (wrapped in list if single WmsTileLayer)

## Constraints:
    Preconditions:
    - The data parameter must be either a WmsTileLayer instance or a list-like object containing WmsTileLayer instances
    - All parameters must be of the correct type as specified in the method signature
    - transition_time must be convertible to integer
    Postconditions:
    - self._name is set to "TimestampedWmsTileLayers"
    - self.options contains parsed period and time_interval values
    - self.options_control contains parsed control options including player configuration
    - self.layers is always a list of WmsTileLayer instances

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

