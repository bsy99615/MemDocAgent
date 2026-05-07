# `search.py`

## `folium.plugins.search.Search` · *class*

## Summary:
A folium plugin that adds interactive search functionality to map layers using the Leaflet Search library.

## Description:
The Search class enables users to search for features within specific folium layers (FeatureGroup, MarkerCluster, GeoJson, TopoJson) by providing a searchable interface on the map. It integrates with the Leaflet Search JavaScript library to provide real-time searching capabilities based on feature properties.

This class serves as a bridge between folium's Python interface and the Leaflet Search JavaScript plugin, allowing developers to add search functionality to their interactive maps with minimal configuration.

## State:
- layer: The folium layer (GeoJson, MarkerCluster, FeatureGroup, or TopoJson) to be indexed for search
- search_label: Optional property name to use as the search key (defaults to None)
- search_zoom: Optional zoom level to set when a search result is found (defaults to None)
- geom_type: Geometry type to filter by (defaults to "Point")
- position: Position of the search control on the map (defaults to "topleft")
- placeholder: Placeholder text for the search input field (defaults to "Search")
- collapsed: Whether the search control starts collapsed (defaults to False)
- options: Additional options parsed via folium.utilities.parse_options
- _template: Jinja2 template for the JavaScript rendering (currently empty/placeholder)
- default_js: List of default JavaScript resources (Leaflet.Search.js CDN link)
- default_css: List of default CSS resources (Leaflet.Search.css CDN link)

## Lifecycle:
- Creation: Instantiate with a valid folium layer and optional configuration parameters
- Usage: Add to a folium Map instance using `map.add_child(search_instance)`
- Rendering: Called automatically when the map is rendered, which handles JS/CSS injection and parameter validation
- Destruction: Managed by folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[Search.__init__] --> B[Validate layer type]
    B --> C[Set instance attributes]
    C --> D[Search.render]
    D --> E[test_params]
    E --> F[super().render()]
```

## Raises:
- AssertionError: When the layer is not one of the supported types (GeoJson, MarkerCluster, FeatureGroup, TopoJson)
- AssertionError: When the Search element is not added to a folium Map object

## Example:
```python
import folium
from folium.plugins import Search
from folium.features import GeoJson

# Create a sample map
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Create a GeoJson layer with some data
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Central Park", "type": "park"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-74.01, 40.78], [-74.01, 40.75], [-73.98, 40.75], [-73.98, 40.78], [-74.01, 40.78]]]
            }
        }
    ]
}

geojson_layer = GeoJson(geojson_data)
m.add_child(geojson_layer)

# Create search functionality
search = Search(
    layer=geojson_layer,
    search_label="name",  # Search by name property
    placeholder="Search places...",
    collapsed=False
)

# Add search to map
m.add_child(search)

# The map now has interactive search functionality
```

### `folium.plugins.search.Search.__init__` · *method*

## Summary:
Initializes a Search plugin instance that enables interactive search functionality for folium map layers.

## Description:
Configures a Search plugin to index and search features within a specified folium layer. This method validates the layer type and sets up all configurable parameters for the search functionality, including positioning, labeling, and zoom behavior.

## Args:
    layer (GeoJson, MarkerCluster, FeatureGroup, TopoJson): The folium layer to be indexed for search operations. Must be one of these supported layer types.
    search_label (str, optional): Property name to use as the search key. Defaults to None.
    search_zoom (int, optional): Zoom level to set when a search result is found. Defaults to None.
    geom_type (str): Geometry type to filter by during search. Defaults to "Point".
    position (str): Position of the search control on the map. Defaults to "topleft".
    placeholder (str): Placeholder text for the search input field. Defaults to "Search".
    collapsed (bool): Whether the search control starts collapsed. Defaults to False.
    **kwargs: Additional options passed to the underlying JavaScript library.

## Returns:
    None: This method initializes the instance and does not return a value.

## Raises:
    AssertionError: When the layer parameter is not one of the supported types (GeoJson, MarkerCluster, FeatureGroup, TopoJson).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.layer: Stores the validated layer reference
    - self.search_label: Stores the search label property name
    - self.search_zoom: Stores the zoom level for search results
    - self.geom_type: Stores the geometry type filter
    - self.position: Stores the control position
    - self.placeholder: Stores the input field placeholder text
    - self.collapsed: Stores the collapsed state flag
    - self.options: Stores processed keyword arguments

## Constraints:
    Preconditions:
        - The layer parameter must be an instance of GeoJson, MarkerCluster, FeatureGroup, or TopoJson
        - The layer must be added to a folium Map instance before rendering
    Postconditions:
        - All instance attributes are properly initialized with provided values
        - The options attribute contains processed keyword arguments in camelCase format

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes instance attributes.

### `folium.plugins.search.Search.test_params` · *method*

## Summary:
Validates search parameters against available layer properties and ensures the search control is attached to a valid folium Map object.

## Description:
The test_params method performs two critical validations for the search functionality: first, it verifies that the specified search_label exists in the available property keys when both keys and search_label are provided; second, it confirms that the search control is properly attached to a folium Map object. This validation occurs during the rendering process to prevent runtime errors due to invalid search configurations.

## Args:
    keys (tuple, list, or None): Collection of property keys available from the layer data, or None for unsupported layer types.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: When search_label is specified but not found in the available keys for GeoJson/TopoJson layers.
    AssertionError: When the search control is not added to a folium Map object.

## State Changes:
    Attributes READ:
        - self.search_label: The label to search for in layer properties
        - self._parent: The parent map object that must be an instance of folium.Map
    
    Attributes WRITTEN:
        - None: This method does not modify instance attributes

## Constraints:
    Preconditions:
        - The Search instance must be added to a folium Map object before calling this method
        - For GeoJson and TopoJson layers, if search_label is specified, it must exist in the layer's property keys
        - Keys parameter should be None for unsupported layer types or contain valid property key names
        
    Postconditions:
        - Search parameters are validated successfully before rendering
        - The search control is confirmed to be attached to a valid Map object

## Side Effects:
    - Performs assertion checks that may raise exceptions if validation fails
    - No external I/O or service calls

### `folium.plugins.search.Search.render` · *method*

## Summary:
Processes layer-specific metadata for search functionality and renders the search control with required JavaScript/CSS dependencies.

## Description:
The render method prepares search functionality by extracting property keys from GeoJson or TopoJson layers to validate search labels, then delegates rendering to parent classes. This method ensures that search parameters are validated against available layer properties before rendering the search control element. It handles three distinct layer types: GeoJson, TopoJson, and others, with special processing for the former two to extract searchable property information.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method for rendering configuration.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: When search_label is specified but not found in layer properties for GeoJson/TopoJson layers.
    AssertionError: When the search control is not added to a folium Map object.

## State Changes:
    Attributes READ:
        - self.layer: The layer object being searched
        - self.search_label: The label to search for in layer properties
        - self._parent: The parent map object
    
    Attributes WRITTEN:
        - None: This method does not modify instance attributes directly

## Constraints:
    Preconditions:
        - The Search instance must be added to a folium Map object before rendering
        - For GeoJson and TopoJson layers, the layer must have valid data structure with properties
        - If search_label is specified, it must exist in the layer's property keys
        - The layer must be one of the supported types (GeoJson, TopoJson, FeatureGroup, MarkerCluster)
        
    Postconditions:
        - Search parameters are validated against layer data
        - JavaScript and CSS dependencies are registered with the parent figure
        - The search control is prepared for rendering in the map interface

## Side Effects:
    - Validates layer data structure and property availability
    - Adds JavaScript and CSS dependencies to the parent figure's header
    - Calls parent render methods which may trigger additional rendering logic

