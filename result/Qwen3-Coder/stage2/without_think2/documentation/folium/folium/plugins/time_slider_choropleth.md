# `time_slider_choropleth.py`

## `folium.plugins.time_slider_choropleth.TimeSliderChoropleth` · *class*

## Summary:
TimeSliderChoropleth is a folium plugin that creates an interactive choropleth map with a time slider control, enabling visualization of geospatial data that changes over time.

## Description:
This class implements a specialized map layer that displays choropleth-style geographic data with temporal dimensions. It allows users to visualize how geographic features change over time through an interactive slider control. The class inherits from JSCSSMixin and Layer, making it compatible with folium's map rendering system and providing automatic JavaScript/CSS dependency management.

The component is designed to work with geospatial data represented as GeoJSON features, where each feature can have different styling applied at various time points. It processes the data to extract temporal information and prepares the necessary structure for time-based visualization.

## State:
- data: Processed GeoJSON data representing geographic features (processed via GeoJson.process_data)
- timestamps: Sorted list of time points extracted from styledict keys
- styledict: Dictionary mapping feature identifiers to their time-based styling configurations
- init_timestamp: Initial time index to display when the map loads
- layer_name: Unique identifier for the map layer (inherited from Layer)
- overlay: Boolean indicating if this is an overlay layer (inherited from Layer)
- control: Boolean controlling visibility in map controls (inherited from Layer)
- show: Boolean controlling initial visibility (inherited from Layer)
- _template: Jinja2 template for rendering the component (empty in current implementation)
- default_js: List of default JavaScript dependencies including d3v4 library

## Lifecycle:
- Creation: Instantiate with data, styledict, and optional layer configuration parameters
- Usage: Add to a folium.Map instance using add_child() method
- Destruction: Managed by folium's map lifecycle management

## Method Map:
```mermaid
graph TD
    A[TimeSliderChoropleth.__init__] --> B[Layer.__init__]
    B --> C[data = GeoJson.process_data(GeoJson({}), data)]
    C --> D[Validate styledict structure]
    D --> E[Extract and sort timestamps]
    E --> F[Validate init_timestamp range]
    F --> G[Set instance attributes]
```

## Raises:
- ValueError: Raised when styledict is not a dictionary or when any value in styledict is not a dictionary
- AssertionError: Raised when init_timestamp is outside the valid range [-len(timestamps), len(timestamps))

## Example:
```python
import folium
from folium.plugins import TimeSliderChoropleth

# Sample data
data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"id": "A", "name": "Region A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-100, 40], [-100, 50], [-90, 50], [-90, 40], [-100, 40]]]
            }
        }
    ]
}

# Styling dictionary with time-based styles
styledict = {
    "A": {
        "2020": {"color": "red", "weight": 2},
        "2021": {"color": "blue", "weight": 3},
        "2022": {"color": "green", "weight": 4}
    }
}

# Create the time slider choropleth
time_slider = TimeSliderChoropleth(
    data=data,
    styledict=styledict,
    name="Time Slider Choropleth"
)

# Add to map
m = folium.Map(location=[40, -95], zoom_start=4)
time_slider.add_to(m)
```

### `folium.plugins.time_slider_choropleth.TimeSliderChoropleth.__init__` · *method*

## Summary:
Initializes a TimeSliderChoropleth layer with geospatial data and timestamped styling information.

## Description:
This method sets up the TimeSliderChoropleth object by processing input data, validating styling dictionaries, extracting timestamps, and configuring initial display settings. It inherits from Layer and JSCSSMixin to provide standard layer management and resource handling capabilities. The method ensures proper validation of input parameters and prepares the layer for temporal visualization through timestamped styling.

## Args:
    data (Any): Geospatial data to be processed and displayed, typically GeoJSON formatted.
    styledict (dict): Dictionary mapping features to their timestamped style configurations.
    name (str, optional): Name of the layer for identification. Defaults to None.
    overlay (bool): Whether the layer should be added as an overlay. Defaults to True.
    control (bool): Whether the layer should appear in the layer control. Defaults to True.
    show (bool): Whether the layer should be visible initially. Defaults to True.
    init_timestamp (int): Initial timestamp index to display. Defaults to 0.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: If styledict is not a dictionary or if any value in styledict is not a dictionary.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.data, self.timestamps, self.styledict, self.init_timestamp

## Constraints:
    Preconditions: 
    - styledict must be a dictionary
    - Each value in styledict must also be a dictionary
    - init_timestamp must be within valid range [-len(timestamps), len(timestamps))
    Postconditions:
    - self.data contains processed geospatial data
    - self.timestamps contains sorted unique timestamps from styledict
    - self.styledict preserves the original styledict
    - self.init_timestamp is normalized to a positive index

## Side Effects:
    None: This method performs no I/O operations or external service calls.

