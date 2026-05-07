# `time_slider_choropleth.py`

## `folium.plugins.time_slider_choropleth.TimeSliderChoropleth` · *class*

## Summary:
TimeSliderChoropleth is a map layer component that displays choropleth data with temporal visualization capabilities, allowing users to animate geographic data over time using a slider interface.

## Description:
This class implements a time-series choropleth map layer that visualizes geographic data with different styles at various time points. It extends the standard Layer functionality with time-based styling capabilities, enabling interactive temporal visualization of geospatial data through a slider interface. The component is designed to work with folium's map rendering system and integrates with D3.js for advanced temporal controls.

The class is typically instantiated by map creators or visualization libraries that need to display geographic data with temporal dimensions. It serves as a specialized layer type for time-series geospatial analysis.

## State:
- data: Processed GeoJSON data structure containing geographic features (processed by GeoJson.process_data(GeoJson({}), data))
- timestamps: Sorted list of timestamp identifiers extracted from styledict keys
- styledict: Dictionary mapping geographic features to their styling configurations at different timestamps
- init_timestamp: Integer index specifying the initial timestamp to display
- layer_name: String identifier for the layer (inherited from Layer base class)
- overlay: Boolean flag indicating if this is an overlay layer (inherited from Layer)
- control: Boolean flag indicating if this appears in map controls (inherited from Layer)
- show: Boolean flag indicating initial visibility (inherited from Layer)
- _template: Jinja2 template for HTML rendering (currently empty template)
- default_js: List of default JavaScript resources including d3v4 library

## Lifecycle:
Creation: Instantiate with data, styledict, and optional layer configuration parameters
Usage: Typically added to a folium.Map object using add_child() method
Destruction: Managed by folium's parent element lifecycle management

## Method Map:
```mermaid
graph TD
    A[TimeSliderChoropleth.__init__] --> B[Layer.__init__]
    B --> C[GeoJson.process_data(GeoJson({}), data)]
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
# Create time-slider choropleth layer
data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Region A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-100, 40], [-100, 50], [-90, 50], [-90, 40], [-100, 40]]]
            }
        }
    ]
}

# Define styling for different timestamps
styledict = {
    "feature1": {
        "2020": {"color": "red", "weight": 2},
        "2021": {"color": "blue", "weight": 3},
        "2022": {"color": "green", "weight": 4}
    }
}

# Create the layer
layer = TimeSliderChoropleth(
    data=data,
    styledict=styledict,
    name="time_series_choropleth",
    overlay=True,
    control=True,
    show=True,
    init_timestamp=0
)

# Add to map
map.add_child(layer)
```

### `folium.plugins.time_slider_choropleth.TimeSliderChoropleth.__init__` · *method*

## Summary:
Initializes a time slider choropleth layer with geospatial data and styling information for temporal visualization.

## Description:
The constructor sets up a time slider choropleth layer that displays geospatial data with different styles at various time points. It processes input data, validates styling dictionaries, extracts timestamps, and configures initial timestamp settings for temporal visualization.

This method is separated from other logic to ensure proper initialization of the time slider choropleth layer, handling data processing, validation, and timestamp extraction before setting up the layer's state. It follows the standard Folium pattern of calling super().__init__() for base layer setup while adding specialized time-series functionality.

## Args:
- data: Geospatial data to be displayed, processed by GeoJson.process_data
- styledict: Dictionary mapping features to their styling dictionaries for different timestamps
- name: Optional string identifier for the layer, defaults to None
- overlay: Boolean flag indicating if layer should be treated as overlay, defaults to True
- control: Boolean flag indicating if layer should appear in map controls, defaults to True
- show: Boolean flag indicating if layer should be initially visible, defaults to True
- init_timestamp: Integer index for initial timestamp selection, defaults to 0

## Returns:
    None

## Raises:
- ValueError: When styledict is not a dictionary or when any value in styledict is not a dictionary

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: 
  - self.data: Processed geospatial data from GeoJson.process_data
  - self.timestamps: Sorted list of timestamp identifiers extracted from styledict
  - self.styledict: Original styledict parameter stored for reference
  - self.init_timestamp: Normalized initial timestamp index

## Constraints:
- Preconditions:
  - styledict must be a dictionary
  - Each value in styledict must be a dictionary
  - init_timestamp must be within the valid range [-len(timestamps), len(timestamps))
- Postconditions:
  - self.data contains processed geospatial data
  - self.timestamps contains sorted timestamp identifiers
  - self.styledict contains the original styling dictionary
  - self.init_timestamp contains a normalized timestamp index

## Side Effects:
- Calls GeoJson.process_data() which may involve data parsing and validation
- Modifies instance attributes to store processed data and configuration
- May raise ValueError exceptions during validation steps

