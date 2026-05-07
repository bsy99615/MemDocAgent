# `vectorgrid_protobuf.py`

## `folium.plugins.vectorgrid_protobuf.VectorGridProtobuf` · *class*

## Summary:
A Folium layer class for displaying vector grid data using the Leaflet.VectorGrid JavaScript library with Protobuf format support.

## Description:
VectorGridProtobuf represents a map layer that renders vector tile data in Protobuf format using the Leaflet.VectorGrid JavaScript library. This class extends Folium's Layer base class with JavaScript/CSS resource management capabilities through JSCSSMixin, enabling integration of vector tile layers into Folium maps.

This class is intended to be instantiated by map creators or layer factories when adding vector grid data to a Folium map. It provides the necessary infrastructure to load and display vector tiles from a specified URL while maintaining compatibility with Folium's layer management system and rendering pipeline.

## State:
- layer_name (str): Unique identifier for the layer, defaults to "VectorGridProtobufLayer" if not provided
- url (str): URL endpoint for fetching vector grid protobuf data
- _name (str): Internal name identifier set to "VectorGridProtobuf"
- options (dict, optional): Configuration options for the vector grid layer
- _template (Template): Jinja2 template for rendering the layer (currently empty)
- default_js (list): List of default JavaScript dependencies including Leaflet.VectorGrid library

## Lifecycle:
- Creation: Instantiate with url, layer_name, and optional options parameters
- Usage: Add to a Folium Map object using map.add_child() method; rendering automatically handles JavaScript/CSS inclusion via JSCSSMixin
- Destruction: Managed by Folium's garbage collection and parent class lifecycle

## Method Map:
```mermaid
graph TD
    A[VectorGridProtobuf.__init__] --> B[super().__init__(name=layer_name)]
    B --> C[Set self.url = url]
    C --> D[Set self._name = "VectorGridProtobuf"]
    D --> E[Set self.options = options if options is not None]
```

## Raises:
- No explicit exceptions are raised by the __init__ method based on the provided implementation
- Parent classes may raise exceptions during initialization or rendering if validation fails

## Example:
```python
import folium

# Create a vector grid layer
vector_grid = folium.plugins.VectorGridProtobuf(
    url="https://example.com/tiles/{z}/{x}/{y}.pbf",
    layer_name="MyVectorGrid",
    options={"vectorTileLayerStyles": {"myLayer": {"color": "red"}}}
)

# Add to a map
m = folium.Map(location=[0, 0], zoom_start=2)
m.add_child(vector_grid)
```

### `folium.plugins.vectorgrid_protobuf.VectorGridProtobuf.__init__` · *method*

## Summary:
Initializes a VectorGridProtobuf layer with a URL endpoint, layer name, and optional configuration options.

## Description:
Configures a vector grid layer that displays Protobuf-encoded vector tile data from a specified URL. This method sets up the layer's identification, URL endpoint, and optional styling configuration while ensuring proper inheritance from Folium's Layer base class.

The method handles default layer naming and ensures the layer integrates correctly with Folium's rendering system through inheritance from JSCSSMixin and Layer classes. It prepares the layer for rendering by setting up required attributes and calling the parent initialization chain.

## Args:
    url (str): URL endpoint for fetching vector grid protobuf data tiles
    layer_name (str): Unique identifier for the layer, defaults to "VectorGridProtobufLayer" if not provided
    options (dict, optional): Configuration options for the vector grid layer styling and behavior

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    No explicit exceptions are raised by this method directly
    Exceptions may be raised by parent class initializations (Layer.__init__, JSCSSMixin.__init__)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.layer_name: Set to provided layer_name or default value
    - self.url: Set to provided URL
    - self._name: Set to "VectorGridProtobuf"
    - self.options: Set to provided options dict if not None

## Constraints:
    Preconditions:
    - url must be a valid string representing a URL endpoint
    - layer_name must be a string or None
    - options must be a dictionary or None
    
    Postconditions:
    - self.layer_name is guaranteed to be a string
    - self.url is guaranteed to be set to the provided URL
    - self._name is guaranteed to be "VectorGridProtobuf"
    - self.options is either a dictionary or None

## Side Effects:
    None: This method performs no I/O operations or external service calls
    The method sets instance attributes but does not modify external state

