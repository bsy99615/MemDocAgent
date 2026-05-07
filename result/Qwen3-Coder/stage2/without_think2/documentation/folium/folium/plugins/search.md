# `search.py`

## `folium.plugins.search.Search` · *class*

## Summary:
Search is a folium plugin that adds interactive search functionality to map layers, enabling users to find and highlight geographic features by searching through their properties.

## Description:
The Search class implements an interactive search widget for folium maps that allows users to search through the properties of geographic features in supported map layers. It integrates with Leaflet's search plugin to provide a user-friendly interface for finding markers, polygons, or other geospatial features. The class is specifically designed to work with FeatureGroup, MarkerCluster, GeoJson, and TopoJson layers, making it suitable for searching collections of geographic data.

## State:
- layer: GeoJson, MarkerCluster, FeatureGroup, or TopoJson instance - The map layer to be indexed for search functionality
- search_label: str or None - The property key to use for searching within feature properties
- search_zoom: int or None - Zoom level to apply when a search result is selected
- geom_type: str - Type of geometry being searched (defaults to "Point")
- position: str - Position of the search control on the map (defaults to "topleft")
- placeholder: str - Placeholder text for the search input field (defaults to "Search")
- collapsed: bool - Whether the search control starts collapsed (defaults to False)
- options: dict - Additional configuration options passed through parse_options, with keys converted from snake_case to camelCase format

## Lifecycle:
- Creation: Instantiate with a supported layer and optional configuration parameters
- Usage: Add to a folium Map instance using add_child() method, then render the map
- Destruction: Managed automatically through the Element parent-child relationship system

## Method Map:
```mermaid
graph TD
    A[Search.__init__] --> B[super().__init__()]
    B --> C[Validate layer type]
    C --> D[Set instance attributes]
    D --> E[Parse options with parse_options]
    
    A --> F[Search.render] --> G[test_params]
    G --> H{Layer type}
    H -->|GeoJson| I[Get properties keys from features]
    H -->|TopoJson| J[Get properties keys from geometries]
    H -->|Other| K[Set keys = None]
    K --> L[test_params(keys)]
    L --> M[super().render()]
```

## Raises:
- AssertionError: When layer is not an instance of GeoJson, MarkerCluster, FeatureGroup, or TopoJson
- AssertionError: When search_label is specified but not found in available property keys
- AssertionError: When the Search element is not added to a folium Map instance

## Example:
```python
import folium
from folium.plugins import Search
from folium.features import GeoJson

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Create a GeoJson layer with properties
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Central Park", "type": "park"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-74.01, 40.71], [-74.01, 40.75], [-73.97, 40.75], [-73.97, 40.71], [-74.01, 40.71]]]
            }
        }
    ]
}

geojson_layer = GeoJson(geojson_data, name="Parks")
m.add_child(geojson_layer)

# Add search functionality
search = Search(
    layer=geojson_layer,
    search_label="name",
    placeholder="Search parks...",
    position="topright"
)
m.add_child(search)

# Render the map
html_output = m._repr_html_()
```

### `folium.plugins.search.Search.__init__` · *method*

## Summary:
Initializes a Search plugin instance that indexes map layers for searchable features.

## Description:
Configures a Search plugin to enable interactive searching capabilities on map layers. This method sets up the plugin's internal state by validating the target layer type and storing configuration parameters. The Search plugin currently supports FeatureGroup, MarkerCluster, GeoJson, and TopoJson layers for indexing.

## Args:
    layer (GeoJson, MarkerCluster, FeatureGroup, or TopoJson): The map layer to index for search functionality. Must be one of the supported layer types.
    search_label (str, optional): Custom label for search results. Defaults to None.
    search_zoom (int, optional): Zoom level to apply when searching. Defaults to None.
    geom_type (str): Geometry type for search indexing. Defaults to "Point".
    position (str): Position of the search control on the map. Defaults to "topleft".
    placeholder (str): Placeholder text for the search input field. Defaults to "Search".
    collapsed (bool): Whether the search control is initially collapsed. Defaults to False.
    **kwargs: Additional options passed to the underlying JavaScript implementation.

## Returns:
    None

## Raises:
    AssertionError: When the provided layer is not an instance of GeoJson, MarkerCluster, FeatureGroup, or TopoJson.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.layer: Stores the target map layer reference
    - self.search_label: Stores custom search label
    - self.search_zoom: Stores zoom level for search results
    - self.geom_type: Stores geometry type for indexing
    - self.position: Stores control position on map
    - self.placeholder: Stores input field placeholder text
    - self.collapsed: Stores collapse state of control
    - self.options: Stores processed additional options

## Constraints:
    Preconditions:
    - The layer parameter must be an instance of one of: GeoJson, MarkerCluster, FeatureGroup, or TopoJson
    - All string parameters must be valid UTF-8 encoded strings
    - Position parameter must be one of: topleft, topright, bottomleft, bottomright
    
    Postconditions:
    - All provided parameters are stored as instance attributes
    - The options attribute contains a properly formatted dictionary of camelCase options

## Side Effects:
    None

### `folium.plugins.search.Search.test_params` · *method*

## Summary:
Validates that the search configuration parameters are properly set and compatible with the parent map object.

## Description:
This method performs validation checks on the search plugin's configuration parameters. It ensures that when both `keys` and `search_label` are provided, the specified search label exists within the available keys. Additionally, it verifies that the search plugin is being added to a valid folium Map object. This validation occurs during the setup phase of the search plugin to prevent runtime errors due to invalid configurations. This method is typically called internally during the plugin initialization process when the search element is being added to a map.

## Args:
    keys (list[str] or None): A list of available search keys/labels. When None, no key validation is performed.

## Returns:
    None: This method does not return any value.

## Raises:
    AssertionError: When `self.search_label` is not found in `keys` (if both are provided), or when `self._parent` is not an instance of folium.Map.

## State Changes:
    Attributes READ: self.search_label, self._parent
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The method should only be called on instances of the Search class
        - `self.search_label` should be either None or a string value
        - `self._parent` should be set to a valid folium Map object before calling this method
        - `keys` should be a list of strings or None
    
    Postconditions:
        - If keys is not None and search_label is not None, then search_label must be present in keys
        - self._parent must be an instance of folium.Map

## Side Effects:
    None: This method performs only validation checks and does not cause any I/O operations or external service calls.

### `folium.plugins.search.Search.render` · *method*

## Summary:
Renders the search plugin by extracting property keys from GeoJSON or TopoJSON layers and validating configuration parameters.

## Description:
This method prepares the search plugin for rendering by determining available property keys from the associated layer's data structure. It validates that the configured search label exists in the layer's properties (when applicable) and ensures the parent map is properly set. The method serves as a critical setup step before the standard rendering process begins.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: When search_label is specified but not found in layer properties, or when the parent is not a Map instance.

## State Changes:
    Attributes READ: self.layer, self.search_label, self._parent
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The layer must be one of: GeoJson, MarkerCluster, FeatureGroup, or TopoJson
    - The parent must be a Map instance
    - If search_label is specified, it must exist in the layer's property keys (for GeoJson/TopoJson layers)

    Postconditions:
    - Property keys are extracted from GeoJson/TopoJson layers when applicable
    - Configuration validation occurs successfully via test_params
    - Parent render method is called with provided kwargs

## Side Effects:
    None: This method performs no I/O operations or external service calls.

