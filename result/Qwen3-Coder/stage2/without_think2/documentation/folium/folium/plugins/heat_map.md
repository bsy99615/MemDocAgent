# `heat_map.py`

## `folium.plugins.heat_map.HeatMap` · *class*

## Summary:
HeatMap is a folium map layer that visualizes spatial data density using heat mapping techniques, rendering data points as a smooth gradient overlay on the map.

## Description:
The HeatMap class creates a heatmap visualization layer that displays the density of geographic data points on a map. It inherits from JSCSSMixin and Layer, providing the necessary infrastructure for JavaScript/CSS dependencies and map layer management. This class is designed to work with spatial data represented as coordinate pairs with optional intensity values, rendering them as a visually appealing heat map overlay.

## State:
- data: List of validated location points, each containing [latitude, longitude, intensity_value] where intensity_value is optional
- options: Dictionary of heatmap configuration options parsed from constructor parameters
- _name: String identifier set to "HeatMap" for layer management
- default_js: Class attribute containing JavaScript dependency URL for leaflet-heat library

## Lifecycle:
- Creation: Instantiate with data points and optional configuration parameters
- Usage: Add to a folium Map instance using add_child() method
- Destruction: Managed by parent Map object's lifecycle

## Method Map:
```mermaid
graph TD
    A[HeatMap.__init__] --> B[super().__init__()]
    B --> C[data = if_pandas_df_convert_to_numpy(data)]
    C --> D[self.data = [validate_location(line[:2]), *line[2:]] for line in data]
    D --> E[Check for NaN values using np.any(np.isnan(self.data))]
    E --> F[Parse options with parse_options()]
    F --> G[Set self.options]
    
    A --> H[_get_self_bounds()]
    H --> I[Calculate bounding box from data points]
    I --> J[Return bounds]
```

## Raises:
- ValueError: Raised when data contains NaN values
- Warning: Issued when max_val parameter is provided (deprecated)

## Example:
```python
import folium
import numpy as np

# Create sample data points
data = [[40.7128, -74.0060, 10], [37.7749, 122.4194, 20], [51.5074, 0.1278, 15]]

# Create a map centered on New York
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Add heat map layer
heatmap = folium.plugins.HeatMap(data, radius=30, blur=10)
m.add_child(heatmap)

# Display the map
m
```

### `folium.plugins.heat_map.HeatMap.__init__` · *method*

## Summary:
Initializes a HeatMap layer with data points and configuration options for visualization on a folium map.

## Description:
The `__init__` method sets up the HeatMap layer by processing input data, validating coordinates, and configuring visualization parameters. It inherits from `Layer` and prepares the layer for rendering on a map with heat intensity visualization. This method handles data conversion from pandas DataFrames to NumPy arrays, validates geographic coordinates, and processes various styling options for the heatmap visualization.

## Args:
    data (array-like): A collection of data points where each point contains at least two numeric values representing latitude and longitude, followed by optional intensity values. Can be a list, tuple, NumPy array, or pandas DataFrame.
    name (str, optional): Name of the layer. Defaults to None.
    min_opacity (float): Minimum opacity of the heatmap. Defaults to 0.5.
    max_zoom (int): Maximum zoom level for the heatmap. Defaults to 18.
    radius (int): Radius of each point in pixels. Defaults to 25.
    blur (int): Blur radius for smoothing the heatmap. Defaults to 15.
    gradient (dict, optional): Color gradient configuration for the heatmap. Defaults to None.
    overlay (bool): Whether to add the layer as an overlay. Defaults to True.
    control (bool): Whether to add the layer to the layer control. Defaults to True.
    show (bool): Whether the layer should be shown initially. Defaults to True.
    **kwargs: Additional keyword arguments for further customization.

## Returns:
    None: This method initializes the object's state and does not return any value.

## Raises:
    ValueError: If the data contains NaN values.
    Warning: If the deprecated `max_val` parameter is provided.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "HeatMap"
    - self.data: Processed data with validated coordinates
    - self.options: Configuration options parsed into camelCase format

## Constraints:
    Preconditions:
    - Input data must be convertible to a NumPy array
    - Each data point must contain at least two numeric values for latitude and longitude
    - Data must not contain any NaN values
    - All coordinate values must be valid numeric representations
    
    Postconditions:
    - self._name is set to "HeatMap"
    - self.data contains validated coordinate points with optional intensity values
    - self.options contains properly formatted configuration options

## Side Effects:
    - Issues a deprecation warning if max_val parameter is provided
    - Converts pandas DataFrames to NumPy arrays
    - Validates geographic coordinates
    - Processes configuration options into camelCase format

### `folium.plugins.heat_map.HeatMap._get_self_bounds` · *method*

## Summary:
Computes the bounding box coordinates that encompass all data points in the heatmap.

## Description:
This method calculates the minimum and maximum latitude and longitude coordinates from the heatmap's data points to establish the geographic bounds. It processes each point in the dataset sequentially, updating the running minimum and maximum values using specialized utility functions that handle None values gracefully.

The method is designed as a separate utility function to encapsulate the bounding box calculation logic, making it reusable and testable independently from the main heatmap rendering process. This separation allows for clear distinction between data processing and visualization concerns.

## Args:
    self: The HeatMap instance containing the data attribute

## Returns:
    list[list[float | None]]: A nested list representing the bounding box with format [[min_lat, min_lon], [max_lat, max_lon]], where each coordinate can be None if no data points exist

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The self.data attribute must be initialized with valid coordinate data
    Postconditions: The returned bounds represent the complete geographic extent of all data points

## Side Effects:
    None

