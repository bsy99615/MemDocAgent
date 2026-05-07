# `timestamped_wmstilelayer.py`

## `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers` · *class*

## Summary:
TimestampedWmsTileLayers is a specialized folium layer class that enables time-series visualization of WMS (Web Map Service) tile layers with temporal dimension support.

## Description:
This class extends folium's Layer base class to provide functionality for displaying WMS tile layers that change over time. It integrates with Leaflet TimeDimension plugin to enable interactive time-based visualization of geospatial data. The class is designed to be used within folium maps to create animated or time-controlled visualizations of WMS data sources.

The class is typically instantiated by users who want to visualize temporal WMS data, such as weather patterns, satellite imagery, or other geospatial datasets that vary over time periods.

## State:
- _name (str): Class identifier set to "TimestampedWmsTileLayers" 
- options (dict): Configuration options for time dimension handling, including period and time_interval settings
- options_control (dict): Control panel configuration including position, auto_play flag, and player options
- layers (list): Collection of WmsTileLayer objects or list of WmsTileLayer objects to be displayed over time
- default_js (list): List of JavaScript dependencies required for time dimension functionality
- default_css (list): List of CSS dependencies required for time dimension UI controls

## Lifecycle:
- Creation: Instantiate with data (WmsTileLayer or list of WmsTileLayer), optional time configuration parameters
- Usage: Add to a folium Map object using add_child() method; rendering automatically includes required JS/CSS dependencies
- Destruction: Managed by folium's garbage collection and parent Element lifecycle management

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
- No explicit exceptions are raised by the __init__ method based on the provided code
- However, underlying parent class constructors or parse_options may raise exceptions in edge cases

## Example:
```python
import folium
from folium.raster_layers import WmsTileLayer

# Create a WMS layer
wms_layer = WmsTileLayer(
    url='https://example.com/wms',
    layers='temperature',
    name='Temperature'
)

# Create timestamped version
timestamped_layer = folium.plugins.TimestampedWmsTileLayers(
    data=wms_layer,
    transition_time=500,
    auto_play=True,
    period="P1D"
)

# Add to map
m = folium.Map(location=[0, 0], zoom_start=2)
m.add_child(timestamped_layer)
```

### `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers.__init__` · *method*

## Summary:
Initializes a TimestampedWmsTileLayers object with time-series WMS tile layer capabilities, configuring time dimension options and layer storage.

## Description:
Configures the TimestampedWmsTileLayers instance by calling the parent Layer constructor with specific overlay settings, setting the internal class name, parsing time dimension options and control panel options using folium's parse_options utility, and normalizing the input data parameter into a consistent layers list format. This method establishes the foundational configuration needed for time-based visualization of WMS layers in folium maps.

## Args:
    data (WmsTileLayer or list[WmsTileLayer]): Single WMS tile layer or list of WMS tile layers to be displayed over time
    transition_time (int): Duration in milliseconds for transitions between time steps, defaults to 200
    loop (bool): Whether to loop playback when reaching the end of the time series, defaults to False
    auto_play (bool): Whether to automatically start playback when the control panel loads, defaults to False
    period (str): ISO 8601 duration string defining the time period for data, defaults to "P1D"
    time_interval (bool): Whether to enable time interval functionality, defaults to False
    name (str): Name for the layer, defaults to None

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    None: This method does not explicitly raise exceptions, though underlying parent class initialization may raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TimestampedWmsTileLayers"
    - self.options: Set to parsed time dimension options dictionary containing period and time_interval
    - self.options_control: Set to parsed control panel options dictionary containing position, auto_play, and player_options
    - self.layers: Set to a list containing either the single WmsTileLayer or the provided list of WmsTileLayer objects

## Constraints:
    Preconditions:
    - data parameter must be either a WmsTileLayer instance or a list of WmsTileLayer instances
    - transition_time must be convertible to integer
    - All parameters must be properly formatted according to their expected types
    
    Postconditions:
    - self._name is set to "TimestampedWmsTileLayers"
    - self.options contains parsed time dimension configuration with period and time_interval
    - self.options_control contains parsed control panel configuration with position, auto_play, and player_options
    - self.layers is always a list of WmsTileLayer objects

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

