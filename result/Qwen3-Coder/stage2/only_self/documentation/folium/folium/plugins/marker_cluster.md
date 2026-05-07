# `marker_cluster.py`

## `folium.plugins.marker_cluster.MarkerCluster` · *class*

## Summary:
A folium layer class that groups nearby markers into clusters for improved map performance and visualization.

## Description:
The MarkerCluster class implements marker clustering functionality for folium maps using the Leaflet.markercluster JavaScript library. It automatically groups markers that are geographically close together into clusters, which improves map performance and readability when displaying large numbers of markers. This class is particularly useful for visualizing datasets with many geographic points.

The class is typically instantiated by map components or directly by users who want to group markers into clusters. It inherits from JSCSSMixin to manage JavaScript and CSS dependencies, and from Layer to provide standard layer management capabilities.

## State:
- locations: list[list[float]] or None - Validated geographic coordinates [latitude, longitude] for markers, defaults to None
- popups: list[Popup] or None - Popups associated with each marker, defaults to None  
- icons: list[Icon] or None - Icons for each marker, defaults to None
- name: str or None - Layer name, defaults to None (auto-generated)
- overlay: bool - Whether layer is an overlay, defaults to True
- control: bool - Whether layer appears in map controls, defaults to True
- show: bool - Whether layer is initially visible, defaults to True
- icon_create_function: str or None - JavaScript function for creating cluster icons, defaults to None
- options: dict - Parsed options for marker cluster behavior, processed by parse_options()
- _name: str - Class identifier set to "MarkerCluster" for internal tracking

## Lifecycle:
Creation: Instantiate with optional locations, popups, icons, and layer configuration parameters. Locations are validated and Marker children are automatically created if provided.
Usage: Add to a folium Map using add_child() method. The rendering process automatically includes required JavaScript and CSS resources.
Destruction: Managed automatically by folium's rendering system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[MarkerCluster.__init__] --> B[super().__init__()]
    B --> C[self._name = "MarkerCluster"]
    C --> D{locations provided?}
    D -- Yes --> E[validate_locations(locations)]
    E --> F{for each location}
    F --> G[Marker(location, popup, icon)]
    G --> H[add_child(Marker)]
    D -- No --> I[skip marker creation]
    I --> J[parse_options(**kwargs)]
    J --> K{icon_create_function provided?}
    K -- Yes --> L[assert isinstance(icon_create_function, str)]
    K -- No --> M[return]
```

## Raises:
- AssertionError: When icon_create_function is provided but is not a string
- ValueError: When validate_locations encounters invalid coordinate data
- TypeError: When validate_locations receives non-iterable data

## Example:
```python
import folium

# Create a map
m = folium.Map([40.7128, -74.0060], zoom_start=10)

# Create marker cluster with locations
locations = [[40.7128, -74.0060], [37.7749, 122.4194], [41.8781, -87.6298]]
marker_cluster = folium.plugins.MarkerCluster(locations=locations)
m.add_child(marker_cluster)

# Or add markers individually to the cluster
marker = folium.Marker([40.7128, -74.0060])
marker_cluster.add_child(marker)

# Render the map
m.save('map.html')
```

### `folium.plugins.marker_cluster.MarkerCluster.__init__` · *method*

## Summary:
Initializes a marker cluster with optional locations, popups, and icons, setting up clustering behavior for map markers.

## Description:
The MarkerCluster.__init__ method constructs a marker clustering layer that groups nearby markers into clusters for better visualization on maps. It accepts location data along with associated popups and icons to create individual marker children, and configures clustering-specific options such as icon creation functions.

This method serves as the primary initialization point for creating marker cluster layers in folium maps. It properly handles the inheritance chain by calling the parent Layer.__init__ method, processes location data through validation, and sets up the clustering configuration options.

## Args:
    locations (list, optional): List of geographic coordinates [latitude, longitude] to create markers for. Defaults to None.
    popups (list, optional): List of popup objects corresponding to each location. Defaults to None.
    icons (list, optional): List of icon objects corresponding to each location. Defaults to None.
    name (str, optional): Name identifier for the marker cluster layer. Defaults to None.
    overlay (bool): Whether the layer should be treated as an overlay. Defaults to True.
    control (bool): Whether the layer should appear in map controls. Defaults to True.
    show (bool): Whether the layer should be initially visible. Defaults to True.
    icon_create_function (str, optional): JavaScript function string for customizing cluster icons. Defaults to None.
    options (dict, optional): Legacy dictionary of clustering options. Defaults to None.
    **kwargs: Additional keyword arguments for clustering configuration options.

## Returns:
    None: This method initializes the object state and does not return a value.

## Raises:
    AssertionError: When icon_create_function is provided but is not a string type.
    TypeError: When locations contains invalid coordinate data structures.
    ValueError: When locations is empty or contains invalid coordinate pairs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MarkerCluster"
    - self.options: Set to parsed options dictionary
    - self.icon_create_function: Set to provided icon_create_function or None
    - self.children: Populated with Marker children when locations are provided

## Constraints:
    Preconditions:
    - If locations is provided, it must be iterable with valid coordinate data
    - If icon_create_function is provided, it must be a string
    - All keyword arguments must be valid for the parent Layer class
    Postconditions:
    - The object is initialized as a Layer with proper name and visibility settings
    - If locations are provided, corresponding Marker children are added to the cluster via self.add_child()
    - Options are properly parsed and stored
    - Icon creation function is validated and stored

## Side Effects:
    - Adds Marker children to the cluster when locations are provided via self.add_child() calls
    - Calls validate_locations() to process location data
    - Calls parse_options() to process configuration options
    - May raise exceptions during validation of inputs

