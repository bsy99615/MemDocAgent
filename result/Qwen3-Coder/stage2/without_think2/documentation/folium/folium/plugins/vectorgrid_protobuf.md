# `vectorgrid_protobuf.py`

## `folium.plugins.vectorgrid_protobuf.VectorGridProtobuf` · *class*

## Summary:
VectorGridProtobuf is a Folium map layer class that integrates Leaflet.VectorGrid to display vector tile data in protobuf format on interactive maps.

## Description:
VectorGridProtobuf implements a specialized map layer that renders vector tiles using the Leaflet.VectorGrid library. It extends JSCSSMixin and Layer base classes to provide automatic JavaScript dependency management and standard layer functionality. This class displays vector tile data from a specified URL endpoint, commonly used for rendering map features like roads, buildings, or other geographic vector data in a performant manner.

## State:
- layer_name (str): Unique identifier for the layer, defaults to "VectorGridProtobufLayer" if not provided
- url (str): URL endpoint providing vector tile data in protobuf format
- _name (str): Internal identifier set to "VectorGridProtobuf"
- options (dict, optional): Configuration options for the vector grid rendering
- _template (Template): Jinja2 template for rendering the vector grid JavaScript
- default_js (list): List of default JavaScript dependencies including Leaflet.VectorGrid library

## Lifecycle:
- Creation: Instantiate with URL endpoint, optional layer name, and configuration options
- Usage: Add to a Folium Map instance using add_child() method
- Destruction: Managed by parent Map object's lifecycle management

## Method Map:
```mermaid
graph TD
    A[VectorGridProtobuf.__init__] --> B[super().__init__()]
    B --> C[layer_name = layer_name if layer_name else "VectorGridProtobufLayer"]
    C --> D[self.url = url]
    D --> E[self._name = "VectorGridProtobuf"]
    E --> F[options handling]
    F --> G[Template setup]
```

## Raises:
- None explicitly raised in __init__
- May propagate exceptions from parent class initialization

## Example:
```python
import folium

# Create a vector grid layer from a protobuf tile endpoint
vector_layer = folium.plugins.VectorGridProtobuf(
    url="https://example.com/tiles/{z}/{x}/{y}.pbf",
    layer_name="MyVectorLayer",
    options={"vectorTileLayerStyles": {"myLayer": {"color": "blue"}}}
)

# Add to map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
m.add_child(vector_layer)
```

### `folium.plugins.vectorgrid_protobuf.VectorGridProtobuf.__init__` · *method*

## Summary:
Initializes a VectorGridProtobuf layer with URL, layer name, and optional configuration options.

## Description:
This method configures the VectorGridProtobuf layer by setting its identifying name, data source URL, and optional rendering options. It inherits from the Layer base class to establish standard layer properties and uses JSCSSMixin for JavaScript/CSS dependency management. The method prepares the layer for integration into a Folium map by setting up its internal state and configuration parameters.

## Args:
    url (str): The URL endpoint for the vector grid protobuf data source
    layer_name (str): Unique identifier for the layer; defaults to "VectorGridProtobufLayer" if not provided
    options (dict, optional): Additional configuration options for the vector grid layer

## Returns:
    None: This method initializes the object's state but does not return a value

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.layer_name: Set to provided layer_name or default value
    - self.url: Set to provided URL value
    - self._name: Set to fixed value "VectorGridProtobuf"
    - self.options: Conditionally set if options parameter is provided

## Constraints:
    Preconditions:
    - url parameter must be a valid string representing a URL endpoint
    - layer_name parameter, if provided, must be a string
    - options parameter, if provided, must be a dictionary
    Postconditions:
    - self.layer_name will be set to either the provided name or default value
    - self.url will be set to the provided URL
    - self._name will be set to "VectorGridProtobuf"
    - self.options will be set if options parameter is provided

## Side Effects:
    None: This method performs only local state initialization and does not cause external I/O or mutations

