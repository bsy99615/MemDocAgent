# `marker_cluster.py`

## `folium.plugins.marker_cluster.MarkerCluster` · *class*

## Summary:
MarkerCluster is a folium map layer that groups nearby markers into clusters for improved performance and visualization when displaying large numbers of geographic markers.

## Description:
The MarkerCluster class implements a clustering mechanism for markers in folium maps, automatically grouping closely positioned markers into clusters to enhance map readability and performance. It inherits from JSCSSMixin and Layer, making it a proper map layer that can be added to folium maps. The class is designed to handle large datasets efficiently by reducing visual clutter and improving user experience when viewing many markers simultaneously.

## State:
- _name (str): Set to "MarkerCluster" to identify this specific layer type internally
- default_js (list[tuple]): Class attribute containing JavaScript dependencies for marker clustering functionality
- default_css (list[tuple]): Class attribute containing CSS dependencies for marker clustering styling
- icon_create_function (str or None): Optional JavaScript function string for customizing cluster icon creation
- options (dict): Configuration options parsed from keyword arguments, converted to camelCase format

## Lifecycle:
- Creation: Instantiate with optional locations, popups, icons, and clustering options
- Usage: Add to a folium Map instance using add_child() method, then render within a Figure context
- Destruction: Managed automatically through the Element parent-child relationship system

## Method Map:
```mermaid
graph TD
    A[MarkerCluster.__init__] --> B[super().__init__()]
    B --> C[self._name = "MarkerCluster"]
    C --> D{locations is not None?}
    D -- Yes --> E[validate_locations(locations)]
    E --> F{for each location}
    F --> G[Marker(location, popup, icon)]
    G --> H[add_child(Marker)]
    D -- No --> I[Continue]
    I --> J[parse_options(**kwargs)]
    J --> K{icon_create_function is not None?}
    K -- Yes --> L[assert isinstance(icon_create_function, str)]
    K -- No --> M[Continue]
    M --> N[End]

    N --> O[MarkerCluster.render]
    O --> P[super().render()]
```

## Raises:
- AssertionError: When icon_create_function is provided but is not a string
- ValueError: When render() is called and location has not been assigned (inherited from Marker)
- AssertionError: When trying to render outside of a Figure context (inherited from parent class)

## Example:
```python
import folium
from folium.plugins import MarkerCluster

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Create marker cluster
marker_cluster = MarkerCluster(
    locations=[[40.7128, -74.0060], [37.7749, 122.4194]],
    popups=["New York", "San Francisco"],
    name="US Cities"
)

# Add to map
m.add_child(marker_cluster)

# Or add individual markers to cluster
marker_cluster.add_child(folium.Marker([41.8781, -87.6298], popup="Chicago"))
```

### `folium.plugins.marker_cluster.MarkerCluster.__init__` · *method*

## Summary:
Initializes a MarkerCluster object with optional locations, popups, icons, and clustering configuration options.

## Description:
The MarkerCluster.__init__ method sets up a marker clustering layer that groups nearby markers into clusters for improved performance and visualization when displaying large numbers of geographic markers. It initializes the parent Layer class with standard layer configuration, sets the internal name to "MarkerCluster", and optionally adds markers to the cluster based on provided location data. The method also processes clustering options and validates custom icon creation functions.

## Args:
    locations (array-like, optional): Geographic coordinates as [latitude, longitude] pairs. Defaults to None.
    popups (array-like, optional): Popup elements or HTML strings for each marker. Defaults to None.
    icons (array-like, optional): Custom icon instances for each marker. Defaults to None.
    name (str, optional): Unique identifier for the layer. Defaults to None.
    overlay (bool): Indicates if the layer is an overlay. Defaults to True.
    control (bool): Determines if the layer appears in the map controls. Defaults to True.
    show (bool): Controls whether the layer is initially visible. Defaults to True.
    icon_create_function (str, optional): JavaScript function string for customizing cluster icon creation. Defaults to None.
    options (dict, optional): Legacy dictionary of clustering options. Defaults to None.
    **kwargs: Additional options passed to the clustering configuration.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: When icon_create_function is provided but is not a string.
    ValueError: When locations is empty or contains invalid coordinate data.
    TypeError: When locations is not an iterable with coordinate pairs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MarkerCluster"
    - self.icon_create_function: Set to provided icon_create_function or None
    - self.options: Set to parsed options dictionary

## Constraints:
    Preconditions:
    - If locations is provided, it must be a valid iterable structure containing coordinate pairs
    - If icon_create_function is provided, it must be a string
    - All keyword arguments must be valid for the parent Layer class initialization
    
    Postconditions:
    - The object is properly initialized as a Layer with name "MarkerCluster"
    - If locations are provided, they are validated and converted to Marker children
    - Options are parsed and stored in camelCase format
    - Icon create function is validated if provided

## Side Effects:
    - Adds Marker children to the cluster when locations are provided
    - Calls validate_locations() to process location input
    - Calls parse_options() to process clustering configuration
    - May raise exceptions during validation of inputs

