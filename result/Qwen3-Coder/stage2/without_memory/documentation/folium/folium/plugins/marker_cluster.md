# `marker_cluster.py`

## `folium.plugins.marker_cluster.MarkerCluster` · *class*

## Summary:
A MarkerCluster is a specialized layer that groups nearby markers into clusters for improved performance and visual clarity on maps.

## Description:
The MarkerCluster class provides a mechanism to efficiently display large numbers of markers on a Leaflet map by automatically grouping nearby markers into clusters. This helps reduce visual clutter when displaying dense marker datasets, improving map readability and performance. It inherits from JSCSSMixin and Layer, making it compatible with folium's map rendering system and providing the necessary JavaScript/CSS dependencies for the leaflet.markercluster plugin.

This class is typically instantiated when creating maps with many markers that would otherwise overwhelm the visualization. It serves as a container for individual Marker objects and manages their clustering behavior through the leaflet.markercluster JavaScript library.

## State:
- _name (str): Set to "MarkerCluster" to identify the layer type
- default_js (list[tuple]): Contains URLs for the markercluster JavaScript library
- default_css (list[tuple]): Contains URLs for the markercluster CSS files
- locations (list): Validated coordinate pairs for marker placement
- popups (list): Optional popup information for each marker
- icons (list): Optional custom icons for each marker
- icon_create_function (str or None): JavaScript function string for customizing cluster icons
- options (dict): Parsed options for the marker cluster configuration

The constructor parameters have these defaults and constraints:
- locations=None: Iterable of coordinate pairs, validated using validate_locations
- popups=None: Optional list of popup objects or strings matching marker count
- icons=None: Optional list of icon objects matching marker count
- name=None: Layer name, defaults to class name
- overlay=True: Whether the layer is an overlay
- control=True: Whether to show in the layer control
- show=True: Whether the layer is initially visible
- icon_create_function=None: Custom JavaScript function for cluster icons
- options=None: Legacy parameter for passing additional options
- **kwargs: Additional options passed to the marker cluster configuration

## Lifecycle:
Creation: Instantiate with optional locations, popups, icons, and configuration options. Locations are validated and converted to Marker children.
Usage: Markers are automatically clustered by the underlying leaflet.markercluster library when the map is rendered.
Destruction: Cleanup is handled automatically through the parent Layer class mechanisms.

## Method Map:
```mermaid
graph TD
    A[MarkerCluster.__init__] --> B[Layer.__init__]
    A --> C[validate_locations]
    A --> D[parse_options]
    A --> E[add_child(Marker)]
    B --> F[JSCSSMixin.render]
    F --> G[Add JS/CSS links to figure header]
```

## Raises:
- TypeError: When locations parameter is not iterable with coordinate pairs
- ValueError: When locations is empty
- AssertionError: When icon_create_function is provided but is not a string

## Example:
```python
import folium
from folium.plugins import MarkerCluster

# Create a basic map
m = folium.Map([45.5236, -122.6750], zoom_start=13)

# Create marker cluster
marker_cluster = MarkerCluster(
    locations=[[45.524, -122.669], [45.523, -122.673]],
    popups=["Popup 1", "Popup 2"],
    icons=[None, None],
    name="My Markers"
)

# Add to map
m.add_child(marker_cluster)

# Render the map
m.save("map.html")
```

### `folium.plugins.marker_cluster.MarkerCluster.__init__` · *method*

## Summary:
Initializes a marker cluster layer that groups nearby markers into clusters for better visualization.

## Description:
Configures a marker cluster layer with optional initial markers, styling options, and clustering behavior. This method sets up the cluster's basic properties and optionally adds initial markers to the cluster.

## Args:
    locations (list, optional): List of marker coordinates to initialize the cluster with. Defaults to None.
    popups (list, optional): List of popup objects or strings for each marker. Defaults to None.
    icons (list, optional): List of icon objects for each marker. Defaults to None.
    name (str, optional): Name of the marker cluster layer. Defaults to None.
    overlay (bool): Whether the layer should be an overlay. Defaults to True.
    control (bool): Whether to include the layer in the layer control. Defaults to True.
    show (bool): Whether the layer should be shown initially. Defaults to True.
    icon_create_function (str, optional): JavaScript function to customize cluster icons. Defaults to None.
    options (dict, optional): Legacy dictionary of options. Defaults to None.
    **kwargs: Additional keyword arguments passed to the clustering options parser.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    AssertionError: When icon_create_function is provided but is not a string.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MarkerCluster"
    - self.options: Set to parsed options from kwargs
    - self.icon_create_function: Set to provided icon_create_function value

## Constraints:
    Preconditions:
    - If icon_create_function is provided, it must be a string
    - Locations must be valid coordinate pairs if provided
    - Popups and icons lists must match the length of locations if provided
    
    Postconditions:
    - The object is initialized as a Layer with proper name and control settings
    - If locations are provided, they are validated and converted to Marker objects
    - All marker children are properly added to the cluster

## Side Effects:
    - Adds Marker child elements to the cluster when locations are provided
    - Calls validate_locations() to sanitize coordinate data
    - Calls parse_options() to process configuration parameters
    - May raise assertion error if icon_create_function is not a string

