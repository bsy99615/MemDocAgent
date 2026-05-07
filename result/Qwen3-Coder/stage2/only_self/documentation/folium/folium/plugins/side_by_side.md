# `side_by_side.py`

## `folium.plugins.side_by_side.SideBySideLayers` · *class*

## Summary:
A Folium plugin that displays two map layers side-by-side using Leaflet's side-by-side comparison functionality.

## Description:
The SideBySideLayers class creates a specialized map layer that allows users to compare two different map layers side-by-side. It leverages the leaflet-side-by-side JavaScript library to provide an interactive comparison interface. This component is particularly useful for visualizing differences between map datasets, such as before/after satellite imagery, different basemap styles, or overlay comparisons.

This class inherits from both JSCSSMixin (for JavaScript/CSS resource management) and Layer (for standard map layer functionality), making it compatible with Folium's map rendering system while providing the specialized side-by-side comparison capability. Note that the _template attribute is currently defined as an empty Template, suggesting it may be intended for future implementation or extension.

## State:
- layer_left: The left map layer to be displayed in the side-by-side comparison
- layer_right: The right map layer to be displayed in the side-by-side comparison
- _name: String identifier set to "SideBySideLayers" for internal tracking
- default_js: Class attribute containing the URL to the leaflet-side-by-side JavaScript library
- _template: Empty Jinja2 Template (currently unimplemented)

## Lifecycle:
- Creation: Instantiate with two map layers as arguments (layer_left, layer_right)
- Usage: Add to a Folium Map object using map.add_child() method
- Destruction: Managed automatically by Folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[SideBySideLayers.__init__] --> B[super().__init__(control=False)]
    B --> C[self._name = "SideBySideLayers"]
    C --> D[self.layer_left = layer_left]
    D --> E[self.layer_right = layer_right]
    E --> F[Inherits render() from JSCSSMixin]
    F --> G[Automatically includes leaflet-side-by-side JS]
```

## Raises:
- No explicit exceptions are raised by the __init__ method
- However, the parent classes may raise exceptions if invalid parameters are passed to them

## Example:
```python
import folium

# Create two different map layers
tile_layer_1 = folium.TileLayer('OpenStreetMap')
tile_layer_2 = folium.TileLayer('CartoDB positron')

# Create side-by-side comparison
side_by_side = folium.plugins.SideBySideLayers(tile_layer_1, tile_layer_2)

# Add to a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
m.add_child(side_by_side)

# The resulting map will show both layers side-by-side with a draggable divider
```

### `folium.plugins.side_by_side.SideBySideLayers.__init__` · *method*

## Summary:
Initializes a SideBySideLayers object with two map layers for side-by-side comparison.

## Description:
Configures a side-by-side map layer comparison widget that displays two map layers simultaneously. This method sets up the internal state of the component by storing the left and right layers and configuring the component's identification name.

## Args:
    layer_left (Layer): The first map layer to display on the left side of the comparison
    layer_right (Layer): The second map layer to display on the right side of the comparison

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    None: This method does not explicitly raise exceptions, though parent class initialization may raise exceptions if invalid parameters are passed

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "SideBySideLayers" for internal identification
    - self.layer_left: Stores the left map layer reference
    - self.layer_right: Stores the right map layer reference

## Constraints:
    Preconditions:
    - Both layer_left and layer_right must be valid folium Layer objects
    - The layers should be compatible for side-by-side display
    
    Postconditions:
    - The object is initialized with proper layer references
    - The component name is set to "SideBySideLayers"
    - The control flag is set to False (preventing automatic addition to map controls)

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal object state.

