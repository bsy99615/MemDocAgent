# `heat_map.py`

## `folium.plugins.heat_map.HeatMap` · *class*

## Summary:
A heatmap layer implementation for folium maps that visualizes density or intensity of geographic data points.

## Description:
The HeatMap class creates a heatmap visualization layer for folium maps, displaying geographic data points with varying intensity levels. It inherits from JSCSSMixin and Layer, making it compatible with folium's map rendering system and enabling automatic inclusion of required JavaScript resources. This class is designed to visualize spatial distributions of data points, such as population density, crime incidents, or any geospatial dataset with intensity values.

The class accepts geographic coordinates (latitude, longitude) along with optional intensity values and processes them through folium's utility functions for data normalization and validation. It integrates with Leaflet's heatmap plugin through the leaflet-heat.js library.

## State:
- data (list): A list of data points where each point is a list containing [latitude, longitude, intensity_value]. Latitude and longitude are validated numeric values, and intensity_value is optional.
- options (dict): Configuration options for the heatmap visualization, including min_opacity, max_zoom, radius, blur, and gradient settings.
- _name (str): Class identifier set to "HeatMap" for internal tracking.
- default_js (list): JavaScript resources required for heatmap functionality, specifically leaflet-heat.js.

## Lifecycle:
- Creation: Instantiate with geographic data and optional configuration parameters. The constructor processes data through validation and normalization.
- Usage: Once added to a folium Map object, the heatmap will render automatically when the map is displayed.
- Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[HeatMap.__init__] --> B[super().__init__()]
    B --> C[if_pandas_df_convert_to_numpy(data)]
    C --> D[validate_location(line[:2])]
    D --> E[self.data = [...]]
    E --> F[parse_options(...)]
    F --> G[self.options = ...]
    A --> H[_get_self_bounds()]
    H --> I[Calculate data bounds]
```

## Raises:
- ValueError: Raised when the input data contains NaN values.
- Warning: Issued when the deprecated max_val parameter is provided.

## Example:
```python
import folium
import numpy as np

# Create sample data: [latitude, longitude, intensity]
data = [
    [40.7128, -74.0060, 10],
    [34.0522, -118.2437, 25],
    [41.8781, -87.6298, 15]
]

# Create a heatmap layer
heatmap = folium.plugins.HeatMap(data)

# Add to a map
m = folium.Map([40.7128, -74.0060], zoom_start=10)
heatmap.add_to(m)

# Display the map
m
```

### `folium.plugins.heat_map.HeatMap.__init__` · *method*

## Summary:
Initializes a HeatMap layer with geographic data points and styling options.

## Description:
Constructs a HeatMap layer that visualizes density of geographic points on a map. This method processes input data, validates geographic coordinates, and configures visualization parameters for the heatmap rendering.

## Args:
    data (array-like): Geographic data points, each containing at least latitude and longitude coordinates followed by intensity values. Can be a list, tuple, numpy array, or pandas DataFrame.
    name (str, optional): Name for the heat map layer. Defaults to None.
    min_opacity (float): Minimum opacity of the heatmap. Defaults to 0.5.
    max_zoom (int): Maximum zoom level for the heatmap. Defaults to 18.
    radius (int): Radius of influence for each data point. Defaults to 25.
    blur (int): Blur radius for smoothing the heatmap. Defaults to 15.
    gradient (dict, optional): Color gradient configuration for the heatmap. Defaults to None.
    overlay (bool): Whether the heatmap should be treated as an overlay. Defaults to True.
    control (bool): Whether the heatmap should appear in the layer control. Defaults to True.
    show (bool): Whether the heatmap should be initially visible. Defaults to True.
    **kwargs: Additional styling options passed to the heatmap renderer.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    ValueError: If the data contains NaN values.
    TypeError: If location coordinates cannot be validated or converted to numeric values.
    ValueError: If location coordinates contain invalid values (non-numeric or NaN).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "HeatMap"
    - self.data: Set to validated and processed geographic data points
    - self.options: Set to parsed styling options

## Constraints:
    Preconditions:
    - Data must contain valid geographic coordinates (latitude and longitude)
    - Data must not contain NaN values
    - Each data point must have at least two numeric values for coordinates
    Postconditions:
    - self._name is set to "HeatMap"
    - self.data contains validated geographic coordinates with intensity values
    - self.options contains properly formatted styling parameters

## Side Effects:
    - Issues a deprecation warning if max_val parameter is provided
    - Converts pandas DataFrames to numpy arrays
    - Validates geographic coordinates for all data points
    - Processes and normalizes styling options for JavaScript rendering

### `folium.plugins.heat_map.HeatMap._get_self_bounds` · *method*

## Summary:
Calculates the geographic bounding box that encompasses all data points in the heatmap.

## Description:
Computes the minimum and maximum latitude/longitude coordinates from the heatmap data points to establish the bounding region. This method is used internally by the Folium framework to determine the appropriate map view when rendering heatmaps.

## Args:
    self: The HeatMap instance containing the data points to bound

## Returns:
    list[list[float | None]]: A nested list representing the bounding box with format [[min_lat, min_lon], [max_lat, max_lon]], where each coordinate can be None if no data is available

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.data must be iterable containing coordinate points
    - Each point in self.data should have at least two numeric elements representing [latitude, longitude]
    Postconditions:
    - Returns a properly formatted bounding box structure
    - Handles None values gracefully through none_min/none_max utilities

## Side Effects:
    None

