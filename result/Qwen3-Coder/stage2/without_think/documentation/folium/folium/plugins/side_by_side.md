# `side_by_side.py`

## `folium.plugins.side_by_side.SideBySideLayers` · *class*

## Summary:
A map layer component that displays two Leaflet layers side-by-side with a draggable divider for comparison.

## Description:
The SideBySideLayers class is a specialized map layer that enables side-by-side comparison of two different map layers. It inherits from both JSCSSMixin and Layer, allowing it to manage JavaScript/CSS resources and behave as a standard map layer. This component is specifically designed to display two map layers in parallel with an interactive divider that users can drag to compare the layers.

## State:
- layer_left: The left map layer to be displayed in the side-by-side comparison. Type: Any folium Layer object.
- layer_right: The right map layer to be displayed in the side-by-side comparison. Type: Any folium Layer object.
- _name: String identifier for the component, hardcoded to "SideBySideLayers". Type: str.
- default_js: Class attribute containing the JavaScript library URL for leaflet-side-by-side functionality. Type: list of tuples.

## Lifecycle:
- Creation: Instantiate with two layer objects (layer_left and layer_right) as required arguments. The control parameter is set to False by default, meaning this layer won't appear in the standard layer control.
- Usage: Once added to a folium Map object, the component will render both layers side-by-side with interactive divider functionality.
- Destruction: No special cleanup required; relies on standard Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[SideBySideLayers.__init__] --> B[Layer.__init__(control=False)]
    B --> C[Set _name = "SideBySideLayers"]
    C --> D[Set layer_left and layer_right]
    D --> E[Inherits default_js from JSCSSMixin]
```

## Raises:
- No explicit exceptions are raised by the constructor itself.
- The component will raise exceptions during rendering if it's not properly contained within a folium Figure context (inherited from JSCSSMixin).

## Example:
```python
import folium
from folium.plugins import SideBySideLayers

# Create two different map layers
layer1 = folium.TileLayer('OpenStreetMap')
layer2 = folium.TileLayer('CartoDB positron')

# Create side-by-side comparison
side_by_side = SideBySideLayers(layer1, layer2)

# Add to a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
side_by_side.add_to(m)

# The map will display both layers side-by-side with a draggable divider
```

### `folium.plugins.side_by_side.SideBySideLayers.__init__` · *method*

## Summary:
Initializes a SideBySideLayers object with two map layers to be displayed side-by-side.

## Description:
The `__init__` method constructs a SideBySideLayers instance that manages two map layers for side-by-side comparison. This method initializes the parent Layer class with control disabled (meaning it won't appear in the layer control UI), assigns the provided left and right layers, and sets the component name to "SideBySideLayers".

This method is implemented as a separate constructor to encapsulate the initialization logic for the side-by-side layer functionality, ensuring proper inheritance setup and attribute assignment before the object is used in map rendering operations.

## Args:
    layer_left (Layer): The left map layer to be displayed in the side-by-side comparison.
    layer_right (Layer): The right map layer to be displayed in the side-by-side comparison.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    No explicit exceptions are raised by this constructor.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "SideBySideLayers" 
    - self.layer_left: Assigned the layer_left parameter value
    - self.layer_right: Assigned the layer_right parameter value

## Constraints:
    Preconditions:
    - Both layer_left and layer_right parameters must be valid Layer instances
    - The parent Layer class initialization must succeed
    
    Postconditions:
    - The object's _name attribute is set to "SideBySideLayers"
    - The layer_left and layer_right attributes reference the provided layer objects
    - The object is initialized with control=False, preventing it from appearing in the layer control UI

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal object attributes.

