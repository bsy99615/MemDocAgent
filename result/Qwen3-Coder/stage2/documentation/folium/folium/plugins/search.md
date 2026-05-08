# `search.py`

## `folium.plugins.search.Search` · *class*

## Summary:
A search control plugin for folium maps that enables searching within GeoJson, MarkerCluster, FeatureGroup, and TopoJson layers.

## Description:
The Search class implements a client-side search functionality for folium maps by integrating with the Leaflet.Search JavaScript library. It allows users to search for features within specific map layers based on property values. The search control appears as a UI element on the map and can filter features in supported layer types.

This class is designed as a distinct abstraction to encapsulate the complexity of integrating external JavaScript search functionality with folium's map rendering system. It provides a clean interface for configuring search behavior while maintaining compatibility with folium's element hierarchy and rendering pipeline.

## State:
- layer: The folium layer object (GeoJson, MarkerCluster, FeatureGroup, or TopoJson) to be indexed for searching
- search_label: Optional string specifying which property field to use for search matching
- search_zoom: Optional integer specifying zoom level to set when a search result is found
- geom_type: String indicating geometry type, defaults to "Point"
- position: String positioning of the search control, defaults to "topleft"
- placeholder: String displayed in the search input field, defaults to "Search"
- collapsed: Boolean indicating whether the search control starts collapsed, defaults to False
- options: Dictionary of additional options parsed via parse_options for JavaScript integration
- _template: Jinja2 template for rendering the search control HTML (empty in provided code)
- default_js: List of tuples specifying JavaScript dependencies for Leaflet.Search
- default_css: List of tuples specifying CSS dependencies for Leaflet.Search

## Lifecycle:
- Creation: Instantiate with a valid folium layer and optional configuration parameters
- Usage: Add to a folium Map instance using the standard add_child() method
- Rendering: Automatically handles JavaScript/CSS inclusion and HTML generation when rendered within a Map context
- Destruction: Managed by folium's element lifecycle system

## Method Map:
```mermaid
graph TD
    A[Search.__init__] --> B[Search.test_params]
    B --> C[Search.render]
    C --> D[JSCSSMixin.render]
    D --> E[MacroElement.render]
    E --> F[Super().render]
```

## Raises:
- AssertionError: Raised during initialization if the layer is not one of the supported types (GeoJson, MarkerCluster, FeatureGroup, TopoJson)
- AssertionError: Raised during rendering if the Search element is not added to a folium Map instance

## Example:
```python
import folium
from folium.plugins import Search
from folium.features import GeoJson

# Create a sample map
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Create a GeoJson layer
geojson_layer = GeoJson(
    data={
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
)

# Add the GeoJson layer to the map
m.add_child(geojson_layer)

# Create a search control that searches by name property
search = Search(
    layer=geojson_layer,
    search_label="name",
    placeholder="Search locations...",
    position="topright"
)

# Add the search control to the map
m.add_child(search)

# The map now includes a search control that can find features by name
```

### `folium.plugins.search.Search.__init__` · *method*

## Summary:
Initializes a Search plugin for folium maps that enables client-side searching within specified map layers.

## Description:
Configures a search control that integrates with Leaflet.Search to enable users to search for features within GeoJson, MarkerCluster, FeatureGroup, or TopoJson layers. This method validates the input layer type and sets up all configuration parameters for the search functionality.

The Search plugin is designed as a distinct abstraction to encapsulate the complexity of integrating external JavaScript search functionality with folium's map rendering system. It provides a clean interface for configuring search behavior while maintaining compatibility with folium's element hierarchy and rendering pipeline.

## Args:
    layer (GeoJson, MarkerCluster, FeatureGroup, TopoJson): The folium layer object to be indexed for searching. Must be one of the supported layer types.
    search_label (str, optional): Property field name to use for search matching. Defaults to None.
    search_zoom (int, optional): Zoom level to set when a search result is found. Defaults to None.
    geom_type (str): Geometry type to search for, defaults to "Point".
    position (str): Position of the search control on the map, defaults to "topleft".
    placeholder (str): Text displayed in the search input field, defaults to "Search".
    collapsed (bool): Whether the search control starts collapsed, defaults to False.
    **kwargs: Additional options passed to the underlying JavaScript library.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    AssertionError: Raised if the layer parameter is not an instance of GeoJson, MarkerCluster, FeatureGroup, or TopoJson.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.layer: Stores the validated layer object
    - self.search_label: Stores the search label configuration
    - self.search_zoom: Stores the search zoom configuration
    - self.geom_type: Stores the geometry type configuration
    - self.position: Stores the position configuration
    - self.placeholder: Stores the placeholder text configuration
    - self.collapsed: Stores the collapsed state configuration
    - self.options: Stores additional parsed options

## Constraints:
    Preconditions:
        - The layer parameter must be an instance of one of: GeoJson, MarkerCluster, FeatureGroup, or TopoJson
        - All parameters must be of the correct type as specified in the method signature
    Postconditions:
        - All instance attributes are properly initialized with provided values
        - The layer attribute contains a valid folium layer object
        - The options attribute contains parsed keyword arguments in camelCase format

## Side Effects:
    None: This method has no side effects beyond initializing object attributes.

### `folium.plugins.search.Search.test_params` · *method*

## Summary:
Validates search configuration parameters against layer data properties and parent map context.

## Description:
Performs parameter validation for the search functionality by checking that the specified search label exists in the layer's property keys (when applicable) and that the search control is properly attached to a folium Map instance. This validation ensures that the search feature can operate correctly with the provided layer configuration.

## Args:
    keys (tuple[str] or None): Collection of property keys from layer data, typically extracted from GeoJSON or TopoJSON features. When None, the validation for search_label existence is skipped.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: When search_label is specified but not found in the layer property keys (for GeoJson/TopoJson layers) or when _parent is not a Map instance.

## State Changes:
    Attributes READ: self.search_label, self._parent
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - If keys is not None and search_label is not None, then search_label must exist in keys
    - _parent must be an instance of folium.Map
    
    Postconditions:
    - Parameter validation is completed successfully
    - Search control is confirmed to be attached to a valid Map instance

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects. It only performs assertion checks to validate internal state and parameters.

### `folium.plugins.search.Search.render` · *method*

## Summary:
Validates search parameters against layer properties and initiates rendering process.

## Description:
The render method extracts property keys from GeoJSON or TopoJSON layers to validate that the specified search_label exists in the layer data, then performs parameter validation before executing the parent class's rendering logic. This method is invoked during the map rendering lifecycle to prepare search controls for display.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method for rendering configuration

## Returns:
    None: This method does not return a value

## Raises:
    AssertionError: When search_label is not found in layer properties (for GeoJson/TopoJson layers) or when _parent is not a Map instance

## State Changes:
    Attributes READ: self.layer, self.search_label, self._parent
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.layer must be an instance of GeoJson, TopoJson, FeatureGroup, or MarkerCluster
    - self._parent must be a Map instance
    - If search_label is specified, it must exist in the layer's property keys for GeoJson/TopoJson layers
    
    Postconditions:
    - Parameter validation is completed successfully
    - Parent rendering process is initiated with provided kwargs

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects. The actual rendering of JavaScript/CSS resources occurs in the parent class's render method through JSCSSMixin inheritance.

