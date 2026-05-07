# `marker_cluster.py`

## `folium.plugins.marker_cluster.MarkerCluster` · *class*

## Summary:
A marker clustering layer that groups nearby markers into clusters for improved map performance.

## Description:
The MarkerCluster class provides a folium layer that organizes multiple markers into clusters to enhance map performance and reduce visual clutter when displaying large numbers of markers. This class serves as a container for marker elements and integrates with the leaflet.markercluster JavaScript library to provide dynamic clustering behavior that adapts to map zoom levels.

This class is typically instantiated when creating maps that need to display numerous markers efficiently. It accepts initial marker locations and creates Marker child elements, which are then managed by the underlying clustering JavaScript library.

## State:
- locations (list, optional): A list of geographic coordinates to be clustered. Each coordinate should be a [latitude, longitude] pair. Validated using validate_locations().
- popups (list, optional): A list of popup content associated with each location. Must correspond positionally to the locations list.
- icons (list, optional): A list of icon objects associated with each location. Must correspond positionally to the locations list.
- icon_create_function (str, optional): A JavaScript function string that defines how cluster icons are created. Must be a valid JavaScript function when provided.
- options (dict, optional): Legacy parameter for passing additional options to the underlying marker cluster implementation.
- _name (str): Class attribute set to "MarkerCluster" indicating the type of layer.

## Lifecycle:
- Creation: Instantiate with optional locations, popups, icons, and standard layer configuration parameters. Locations are validated and converted to Marker children during initialization.
- Usage: Markers are added to the cluster via the add_child method, and the cluster is rendered as part of a folium Figure. The clustering behavior is handled automatically by the leaflet.markercluster JavaScript library.
- Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[MarkerCluster.__init__] --> B[Layer.__init__]
    A --> C[validate_locations(locations)]
    C --> D{locations provided?}
    D -- Yes --> E[Loop through locations]
    E --> F[Create Marker for each location]
    F --> G[add_child(Marker)]
    D -- No --> H[Skip marker creation]
    A --> I[parse_options(**kwargs)]
    I --> J[Validate icon_create_function]
    J --> K[Set self.icon_create_function]
```

## Raises:
- AssertionError: Raised when icon_create_function is provided but is not a string type.
- TypeError: Raised by validate_locations() when locations is not an iterable.
- ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data.

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Create a marker cluster
marker_cluster = folium.plugins.MarkerCluster(
    name="My Marker Cluster",
    overlay=True,
    control=True
)

# Add markers to the cluster
marker_cluster.add_child(folium.Marker([40.7128, -74.0060], popup="New York"))
marker_cluster.add_child(folium.Marker([37.7749, 122.4194], popup="San Francisco"))

# Add cluster to map
m.add_child(marker_cluster)

# Or create cluster with initial locations
locations = [[40.7128, -74.0060], [37.7749, 122.4194]]
popups = ["New York", "San Francisco"]
marker_cluster = folium.plugins.MarkerCluster(
    locations=locations,
    popups=popups,
    name="Preloaded Markers"
)
```

### `folium.plugins.marker_cluster.MarkerCluster.__init__` · *method*

## Summary:
Initializes a MarkerCluster instance with optional marker locations and configuration options.

## Description:
Configures a MarkerCluster layer that groups nearby markers into clusters for improved map performance. This method sets up the cluster's basic properties, validates and processes initial marker data if provided, and prepares the cluster for rendering in a folium map.

The method handles the legacy 'options' parameter by merging it into the kwargs, calls the parent Layer constructor to establish base layer properties, and optionally creates Marker child elements from provided location data. It also validates the icon_create_function parameter and processes all remaining options for the underlying JavaScript library.

## Args:
    locations (list, optional): A list of geographic coordinates to be clustered. Each coordinate should be a [latitude, longitude] pair. Defaults to None.
    popups (list, optional): A list of popup content associated with each location. Must correspond positionally to the locations list. Defaults to None.
    icons (list, optional): A list of icon objects associated with each location. Must correspond positionally to the locations list. Defaults to None.
    name (str, optional): Unique identifier for the layer. If None, defaults to the result of `self.get_name()`. Defaults to None.
    overlay (bool): Indicates whether this layer should be treated as an overlay (True) or base layer (False). Defaults to True.
    control (bool): Controls whether this layer appears in the layer control UI. Defaults to True.
    show (bool): Determines if this layer is initially visible. Defaults to True.
    icon_create_function (str, optional): A JavaScript function string that defines how cluster icons are created. Must be a valid JavaScript function when provided. Defaults to None.
    options (dict, optional): Legacy parameter for passing additional options to the underlying marker cluster implementation. Defaults to None.
    **kwargs: Additional keyword arguments passed to the underlying JavaScript marker cluster library.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    AssertionError: Raised when icon_create_function is provided but is not a string type.
    TypeError: Raised by validate_locations() when locations is not an iterable.
    ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MarkerCluster"
    - self.options: Set to parsed options from kwargs
    - self.icon_create_function: Set to provided icon_create_function value

## Constraints:
    Preconditions:
        - If locations is provided, it must be iterable and contain valid coordinate data
        - If icon_create_function is provided, it must be a string type
        - All other parameters must be of their expected types
    Postconditions:
        - Instance is properly initialized as a MarkerCluster layer
        - If locations are provided, corresponding Marker children are added to the cluster
        - All options are properly parsed and stored
        - The _name attribute is set to "MarkerCluster"

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes instance attributes and potentially adds child Marker elements to the cluster.

