# `time_slider_choropleth.py`

## `folium.plugins.time_slider_choropleth.TimeSliderChoropleth` · *class*

## Summary:
TimeSliderChoropleth creates interactive time-series choropleth maps with slider controls for geospatial data visualization.

## Description:
This class implements a time-slider choropleth map layer that visualizes geospatial data with temporal dimensions. It allows users to interactively explore geographic features that change over time through a slider interface. The class extends JSCSSMixin for JavaScript/CSS handling and Layer for map layer integration.

The component is designed to display geographical data where each feature can have different styling properties at different time points. It's particularly useful for visualizing phenomena like population changes, temperature variations, or any geospatial data that evolves over time.

## State:
- data: Processed geospatial data (GeoJson format) that has been processed through GeoJson.process_data
- styledict: Dictionary mapping feature identifiers to time-based styling configurations, where each value is itself a dictionary mapping timestamps to style properties
- timestamps: Sorted list of timestamp identifiers extracted from styledict keys
- init_timestamp: Integer index representing the initial time frame to display (can be negative for indexing from the end)
- name: String identifier for the layer (passed to parent Layer class)
- overlay: Boolean indicating if this is an overlay layer (passed to parent Layer class)
- control: Boolean indicating if a control should be added to the map (passed to parent Layer class)
- show: Boolean indicating if the layer should be initially visible (passed to parent Layer class)

## Lifecycle:
- Creation: Instantiate with data, styledict, and optional Layer parameters (name, overlay, control, show)
- Usage: The layer is typically added to a folium.Map object, which handles rendering and interaction
- Destruction: Cleanup is handled automatically when the map is destroyed or layer is removed

## Method Map:
```mermaid
graph TD
    A[TimeSliderChoropleth.__init__] --> B[super().__init__]
    A --> C[GeoJson.process_data]
    A --> D[Validate styledict structure]
    A --> E[Extract and sort timestamps]
    A --> F[Validate init_timestamp]
```

## Raises:
- ValueError: Raised when styledict is not a dictionary or when any value in styledict is not a dictionary
- AssertionError: Raised when init_timestamp is outside the valid range [-len(timestamps), len(timestamps))

## Example:
```python
import folium
from folium.plugins import TimeSliderChoropleth

# Sample data structure
data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"id": "A", "name": "Region A"},
            "geometry": {"type": "Polygon", "coordinates": [[...]]}
        }
    ]
}

# Styling dictionary with time series data
styledict = {
    "A": {
        "2020": {"color": "red", "weight": 2},
        "2021": {"color": "blue", "weight": 3},
        "2022": {"color": "green", "weight": 4}
    }
}

# Create the time slider choropleth layer
layer = TimeSliderChoropleth(
    data=data,
    styledict=styledict,
    name="Time Series Regions"
)

# Add to map
m = folium.Map([0, 0], zoom_start=2)
layer.add_to(m)
```

### `folium.plugins.time_slider_choropleth.TimeSliderChoropleth.__init__` · *method*

## Summary:
Initializes a TimeSliderChoropleth layer with geospatial data and styling configurations for time-series visualization.

## Description:
Configures a time slider choropleth layer by processing geospatial data, validating styling dictionaries, extracting time stamps, and setting initial timestamp configuration. This method establishes the foundational structure for rendering choropleth maps that change over time, enabling interactive time-series visualization of geographic data.

The method validates input parameters, processes geospatial data through GeoJson utilities, ensures proper dictionary structure for styling configurations, and prepares timestamp sequences for temporal navigation. It also handles negative indexing for initial timestamp selection.

## Args:
    data: Geospatial data to be visualized, processed through GeoJson utilities
    styledict (dict): Dictionary mapping features to their styling configurations over time, where each value is itself a dictionary of timestamp -> style mappings
    name (str, optional): Unique identifier for the layer. If None, defaults to the result of `self.get_name()`. Defaults to None.
    overlay (bool): Indicates whether this layer should be treated as an overlay (True) or base layer (False). Defaults to True.
    control (bool): Controls whether this layer appears in the layer control UI. Defaults to True.
    show (bool): Determines if this layer is initially visible. Defaults to True.
    init_timestamp (int): Initial timestamp index for the time slider, supporting negative indexing. Must be in the range [-len(timestamps), len(timestamps)). Defaults to 0.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: Raised when styledict is not a dictionary or when any value in styledict is not a dictionary.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.data: Processed geospatial data from the input data parameter using GeoJson.process_data
    - self.timestamps: Sorted list of unique timestamps extracted from styledict keys
    - self.styledict: Original styledict parameter stored for reference
    - self.init_timestamp: Normalized initial timestamp index

## Constraints:
    Preconditions: 
    - styledict must be a dictionary
    - Each value in styledict must be a dictionary
    - init_timestamp must be within the valid range [-len(timestamps), len(timestamps))
    Postconditions:
    - self.data contains processed geospatial data
    - self.timestamps contains sorted unique timestamps
    - self.styledict contains the original styledict
    - self.init_timestamp is normalized to a valid positive index

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes instance attributes.

