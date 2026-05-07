# `heat_map.py`

## `folium.plugins.heat_map.HeatMap` · *class*

## Summary:
HeatMap is a folium layer class that renders heat maps on interactive maps using the Leaflet.heat JavaScript library.

## Description:
The HeatMap class creates a heat map visualization layer that displays density or intensity of geographic data points on a folium map. It inherits from JSCSSMixin and Layer, making it compatible with folium's map rendering system and providing automatic JavaScript/CSS resource management. This class is typically instantiated by users who want to visualize spatial data distributions, such as population density, crime incidents, or any point-based dataset with geographic coordinates.

The class processes input data through several utility functions to ensure proper formatting and validation before passing it to the underlying JavaScript library for rendering. It automatically handles conversion of pandas DataFrames to numpy arrays and validates geographic coordinate formats.

## State:
- data: List of data points, where each point contains [latitude, longitude, intensity_value] coordinates. Latitude and longitude must be valid numeric values, and intensity values are optional.
- options: Dictionary of configuration options for the heat map, including min_opacity, max_zoom, radius, blur, and gradient settings
- _name: String identifier set to "HeatMap" for internal tracking
- _template: Jinja2 template for HTML rendering (empty in the provided code)
- default_js: List of JavaScript resources required for heat map functionality, including leaflet-heat.js
- layer_name: Inherited from Layer class, uniquely identifies this layer in the map
- overlay: Inherited from Layer class, determines if this is an overlay layer (defaults to True)
- control: Inherited from Layer class, determines if this layer appears in map controls (defaults to True)
- show: Inherited from Layer class, determines initial visibility (defaults to True)

The __init__ parameters have the following defaults and constraints:
- data: Required parameter, expects a list-like structure of geographic points with format [lat, lon, intensity] where lat and lon are numeric coordinates
- name: Optional string, defaults to None (auto-generated)
- min_opacity: Float, defaults to 0.5
- max_zoom: Integer, defaults to 18
- radius: Integer, defaults to 25
- blur: Integer, defaults to 15
- gradient: None or dict, defaults to None
- overlay: Boolean, defaults to True
- control: Boolean, defaults to True
- show: Boolean, defaults to True

Class invariants:
- data must contain valid geographic coordinates (latitude, longitude) with optional intensity values
- data cannot contain NaN values
- All data points must be properly formatted as [lat, lon, ...] where lat and lon are valid numeric values
- The data structure must be compatible with folium's coordinate validation system

## Lifecycle:
Creation: Instantiate using HeatMap(data, **kwargs) where data is a list of [lat, lon, intensity] points
Usage: Add to a folium.Map object using map.add_child(heatmap_instance)
Destruction: Cleanup is handled by folium's parent classes and garbage collection

## Method Map:
```mermaid
graph TD
    A[HeatMap.__init__] --> B[super().__init__()]
    A --> C[if_pandas_df_convert_to_numpy(data)]
    A --> D[validate_location(line[:2]) for line in data]
    A --> E[Parse data to ensure [lat, lon, intensity] format]
    A --> F[Check for NaN values in data]
    A --> G[Warn about deprecated max_val parameter]
    A --> H[parse_options(...) for JS configuration]
    A --> I[Set self.data and self.options]
    I --> J[HeatMap._get_self_bounds]
    J --> K[Calculate bounding box from data points]
```

## Raises:
- ValueError: Raised when data contains NaN values or when coordinate validation fails
- Warning: Raised when max_val parameter is provided (deprecated)
- TypeError: May be raised by validate_location if data format is invalid
- ValueError: May be raised by validate_location if data format is invalid

## Example:
```python
import folium
import numpy as np

# Basic usage with simple coordinate data
data = [
    [40.7128, -74.0060, 10],  # New York City with intensity 10
    [34.0522, -118.2437, 25], # Los Angeles with intensity 25
    [41.8781, -87.6298, 15]   # Chicago with intensity 15
]

# Create heatmap with default settings
heatmap = folium.plugins.HeatMap(data)

# Add to map centered on New York
map_obj = folium.Map([40.7128, -74.0060], zoom_start=10)
map_obj.add_child(heatmap)

# Advanced usage with customization
custom_heatmap = folium.plugins.HeatMap(
    data,
    radius=30,           # Size of each heat point
    blur=10,             # Blur radius for smoothing
    gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'red', 1.0: 'black'},
    min_opacity=0.3,     # Minimum opacity of heat points
    max_zoom=15          # Maximum zoom level for heat effect
)

# Using with pandas DataFrame (automatically converted)
import pandas as pd
df = pd.DataFrame([
    [40.7128, -74.0060, 10],
    [34.0522, -118.2437, 25],
    [41.8781, -87.6298, 15]
])
heatmap_from_df = folium.plugins.HeatMap(df)

# Multiple heatmaps on same map
map_with_multiple = folium.Map([40.7128, -74.0060], zoom_start=10)
heatmap1 = folium.plugins.HeatMap(data, name='Heatmap 1')
heatmap2 = folium.plugins.HeatMap(data, name='Heatmap 2', overlay=False)
map_with_multiple.add_child(heatmap1)
map_with_multiple.add_child(heatmap2)
```

### `folium.plugins.heat_map.HeatMap.__init__` · *method*

## Summary:
Initializes a HeatMap layer with geographic data and visualization options, setting up the underlying data structure and configuration for heat map rendering.

## Description:
The HeatMap.__init__ method constructs a heat map layer by processing input geographic data, validating its structure, and configuring visualization parameters. This method serves as the primary entry point for creating heat map visualizations in Folium, handling data conversion, validation, and option parsing to prepare the layer for rendering on interactive maps.

The method is designed as a dedicated constructor to encapsulate all initialization logic for heat map layers, separating concerns from other methods and ensuring proper setup before the layer is added to a map. It leverages utility functions for data conversion and validation while maintaining compatibility with existing Folium layer management patterns.

## Args:
    data: Geographic data points for the heat map, typically containing latitude/longitude coordinates and intensity values. Can be a list, tuple, numpy array, or pandas DataFrame.
    name (str, optional): Unique identifier for the layer. Defaults to None (auto-generated).
    min_opacity (float): Minimum opacity for the heat map. Defaults to 0.5.
    max_zoom (int): Maximum zoom level for the heat map. Defaults to 18.
    radius (int): Radius of influence for each data point. Defaults to 25.
    blur (int): Blur radius for smoothing the heat map. Defaults to 15.
    gradient (dict, optional): Color gradient configuration for the heat map. Defaults to None.
    overlay (bool): Whether the layer should be treated as an overlay. Defaults to True.
    control (bool): Whether the layer should appear in map controls. Defaults to True.
    show (bool): Whether the layer should be initially visible. Defaults to True.
    **kwargs: Additional options passed to the heat map renderer, converted to camelCase format.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    ValueError: Raised when the input data contains NaN values, as heat maps cannot process missing data.
    Warning: Issued when the deprecated `max_val` parameter is provided, indicating it's no longer necessary.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "HeatMap" to identify the layer type
    - self.data: Processed geographic data with validated coordinates
    - self.options: Dictionary of parsed visualization options

## Constraints:
    Preconditions:
    - Input data must contain valid geographic coordinates (latitude/longitude pairs)
    - Data cannot contain NaN values
    - All coordinate values must be convertible to floats
    - Input data structure must be compatible with list/tuple iteration
    
    Postconditions:
    - self._name is set to "HeatMap"
    - self.data contains properly validated geographic coordinates with intensity values
    - self.options contains processed visualization parameters in camelCase format
    - The object is ready for rendering in Folium maps

## Side Effects:
    - Processes input data through utility functions (if_pandas_df_convert_to_numpy, validate_location)
    - May emit a deprecation warning for the max_val parameter
    - Sets up internal state for heat map rendering

### `folium.plugins.heat_map.HeatMap._get_self_bounds` · *method*

## Summary:
Calculates the geographic bounding box that encompasses all data points in the heatmap.

## Description:
This method determines the minimum and maximum latitude and longitude coordinates from the heatmap data points to establish the spatial boundaries of the dataset. It's used internally by the HeatMap class to calculate the extent of the data for proper map rendering and coordinate system handling.

The method processes each data point sequentially, updating the running minimum and maximum values for latitude and longitude coordinates using safe comparison functions that handle None values appropriately. When no valid data points exist, it returns bounds initialized with None values.

## Args:
    None

## Returns:
    list[list[float | None]]: A nested list representing the bounding box with format [[min_lat, min_lon], [max_lat, max_lon]]. Each coordinate can be None if no valid data points exist or if the corresponding coordinate in the data is None.

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.data must be iterable containing coordinate points
    - Each point in self.data should have at least two numeric values representing latitude and longitude
    - Points may contain None values for missing coordinates
    
    Postconditions:
    - Returns a properly formatted bounding box structure with exactly two nested lists
    - The first nested list contains [min_lat, min_lon] 
    - The second nested list contains [max_lat, max_lon]
    - All None values in input data are safely handled

## Side Effects:
    None

