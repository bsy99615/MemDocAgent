# `side_by_side.py`

## `folium.plugins.side_by_side.SideBySideLayers` · *class*

## Summary:
SideBySideLayers is a folium plugin that enables the display of two map layers side-by-side with a draggable divider for comparison.

## Description:
This class implements a side-by-side map layer viewer that allows users to compare two different map layers by displaying them adjacent to each other with a draggable separator. It inherits from both JSCSSMixin and Layer, making it compatible with folium's map rendering system while providing the necessary JavaScript dependencies for the leaflet-side-by-side functionality.

The class is designed to be used when creating comparative visualizations of different map datasets or overlays, such as comparing satellite imagery with street maps, or different time periods of the same geographic area.

## State:
- layer_left: The left map layer to be displayed in the side-by-side view
- layer_right: The right map layer to be displayed in the side-by-side view
- _name: String identifier set to "SideBySideLayers" for internal tracking
- _template: Jinja2 template used for rendering the JavaScript component
- default_js: Class attribute containing JavaScript dependency URL for leaflet-side-by-side library

## Lifecycle:
- Creation: Instantiate with two map layers as arguments (layer_left, layer_right)
- Usage: Add to a folium Map instance using add_child() method
- Destruction: Managed by folium's map lifecycle management

## Method Map:
```mermaid
graph TD
    A[SideBySideLayers.__init__] --> B[super().__init__(control=False)]
    B --> C[self._name = "SideBySideLayers"]
    C --> D[self.layer_left = layer_left]
    D --> E[self.layer_right = layer_right]
```

## Raises:
- None explicitly raised in __init__
- May propagate exceptions from parent class initialization

## Example:
```python
import folium
from folium.plugins import SideBySideLayers

# Create two different map layers
layer1 = folium.TileLayer('OpenStreetMap')
layer2 = folium.TileLayer('CartoDB positron')

# Create side-by-side comparison
side_by_side = SideBySideLayers(layer1, layer2)

# Add to map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
side_by_side.add_to(m)
```

### `folium.plugins.side_by_side.SideBySideLayers.__init__` · *method*

## Summary:
Initializes a SideBySideLayers object with two map layers to be displayed side-by-side.

## Description:
The __init__ method sets up a SideBySideLayers instance by initializing its parent Layer class with control disabled, setting the internal name to "SideBySideLayers", and storing the left and right map layers that will be displayed side-by-side in the resulting visualization.

## Args:
    layer_left (Layer): The left map layer to be displayed in the side-by-side comparison
    layer_right (Layer): The right map layer to be displayed in the side-by-side comparison

## Returns:
    None: This method initializes the object's state but does not return a value

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "SideBySideLayers" string
    - self.layer_left: Assigned the layer_left parameter value
    - self.layer_right: Assigned the layer_right parameter value

## Constraints:
    Preconditions:
    - layer_left must be a valid Layer instance or subclass
    - layer_right must be a valid Layer instance or subclass
    - Both layers should be compatible for side-by-side display
    
    Postconditions:
    - self._name is set to "SideBySideLayers"
    - self.layer_left contains the provided left layer reference
    - self.layer_right contains the provided right layer reference
    - The object inherits control=False from its parent Layer class

## Side Effects:
    None: This method performs only local state initialization and has no external side effects

