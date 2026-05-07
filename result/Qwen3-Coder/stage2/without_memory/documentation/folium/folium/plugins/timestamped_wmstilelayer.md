# `timestamped_wmstilelayer.py`

## `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers` · *class*

## Summary:
A time-series WMS tile layer container that enables temporal visualization of geospatial data in Folium maps.

## Description:
The TimestampedWmsTileLayers class is a specialized map layer that displays time-series Web Map Service (WMS) tile layers with temporal controls. It inherits from JSCSSMixin and Layer to integrate with Folium's map rendering system and provides functionality for managing WMS data that changes over time, including playback controls and time interval management.

## State:
- data: Union[WmsTileLayer, list[WmsTileLayer]] - The WMS tile layer(s) to display with temporal controls
- _name: str - Fixed value "TimestampedWmsTileLayers" identifying this layer type
- options: dict - Configuration options for time period handling including 'period' and 'time_interval'
- options_control: dict - Configuration for the temporal control UI including position, auto_play, and player_options
- layers: list[WmsTileLayer] - Internal storage of WMS layers, normalized to a list format
- transition_time: int - Duration in milliseconds for transitions between time steps (default: 200)
- loop: bool - Whether to loop playback when reaching the end (default: False)
- auto_play: bool - Whether to automatically start playback (default: False)
- period: str - ISO 8601 period string defining time intervals (default: "P1D")
- time_interval: bool - Whether to enable time interval controls (default: False)
- name: str - Optional name for the layer (default: None)

## Lifecycle:
- Creation: Instantiate with WMS data and optional configuration parameters
- Usage: Add to a Folium map using the add_child() method
- Destruction: Managed automatically by Folium's garbage collection when removed from the map

## Method Map:
```mermaid
graph TD
    A[TimestampedWmsTileLayers.__init__] --> B[super().__init__]
    A --> C[parse_options for period/time_interval]
    A --> D[parse_options for control settings]
    A --> E[Normalize data to layers list]
    B --> F[Layer initialization]
    C --> G[options attribute setup]
    D --> H[options_control attribute setup]
    E --> I[layers attribute setup]
```

## Raises:
- AssertionError: When invalid options are provided to parse_options (though this is handled internally)
- TypeError: When data is not a WmsTileLayer or list of WmsTileLayers

## Example:
```python
import folium
from folium.raster_layers import WmsTileLayer

# Create a WMS layer
wms_layer = WmsTileLayer(
    url='https://example.com/wms',
    layers=['temperature'],
    name='Temperature Data'
)

# Create timestamped layer
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
Initializes a TimestampedWmsTileLayers object that manages time-series WMS tile layers for interactive map visualizations.

## Description:
Configures the timestamped WMS tile layer plugin with time-based display controls and layer management capabilities. This method sets up the core properties and options needed for displaying time-series geospatial data from WMS services in a folium map interface.

## Args:
    data (WmsTileLayer or iterable): Single WmsTileLayer instance or iterable of WmsTileLayer instances to display over time
    transition_time (int): Duration in milliseconds for layer transitions. Defaults to 200
    loop (bool): Whether to loop playback when reaching the end. Defaults to False
    auto_play (bool): Whether to automatically start playback. Defaults to False
    period (str): ISO 8601 period string defining the time interval. Defaults to "P1D"
    time_interval (bool): Whether to enable time interval filtering. Defaults to False
    name (str): Name identifier for the layer. Defaults to None

## Returns:
    None: This is an initializer method that configures object state

## Raises:
    AssertionError: If invalid options are passed to parse_options (though this is handled internally)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TimestampedWmsTileLayers"
    - self.options: Configured with time period and interval settings
    - self.options_control: Configured with control settings including transition time and loop behavior
    - self.layers: Set to a list containing the provided data (converted to list if single WmsTileLayer)

## Constraints:
    Preconditions:
    - data must be either a WmsTileLayer instance or an iterable of WmsTileLayer instances
    - transition_time must be convertible to integer
    - period must be a valid ISO 8601 period string
    - time_interval must be boolean
    
    Postconditions:
    - self._name is set to "TimestampedWmsTileLayers"
    - self.options contains parsed time-related configuration
    - self.options_control contains parsed control configuration
    - self.layers is always a list of WmsTileLayer instances

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

