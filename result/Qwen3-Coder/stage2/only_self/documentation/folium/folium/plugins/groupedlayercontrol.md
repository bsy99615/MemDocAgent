# `groupedlayercontrol.py`

## `folium.plugins.groupedlayercontrol.GroupedLayerControl` · *class*

## Summary:
A grouped layer control for Leaflet maps that organizes map layers into logical groups with optional exclusive selection behavior.

## Description:
The GroupedLayerControl class implements a Leaflet-based layer control that allows users to organize map overlays into named groups. It provides functionality to manage visibility of layers within groups, with support for exclusive selection within groups where only one layer can be active at a time. This control is particularly useful for managing complex map visualizations where layers need to be logically grouped and toggled.

This class inherits from JSCSSMixin and MacroElement, making it compatible with Folium's rendering system and automatically including required JavaScript and CSS dependencies for the Leaflet Grouped Layer Control plugin.

## State:
- _name (str): Set to "GroupedLayerControl" to identify the element type
- options (dict): Configuration options parsed from keyword arguments using parse_options, converted to camelCase format
- layers_untoggle (set): Set of layer names that should be initially hidden/unselected
- grouped_overlays (dict): Nested dictionary mapping group names to layer name mappings

## Lifecycle:
- Creation: Instantiate with groups parameter containing layer groupings, optional exclusive_groups flag, and additional options
- Usage: Add to a Folium Map object using add_child() method; rendering automatically handles JS/CSS inclusion
- Destruction: No special cleanup required; relies on parent class lifecycle management

## Method Map:
```mermaid
graph TD
    A[GroupedLayerControl.__init__] --> B[super().__init__()]
    B --> C[self._name = "GroupedLayerControl"]
    C --> D[self.options = parse_options(**kwargs)]
    D --> E{exclusive_groups}
    E -- True --> F[self.options["exclusiveGroups"] = list(groups.keys())]
    F --> G[self.layers_untoggle = set()]
    G --> H[self.grouped_overlays = {}]
    H --> I[for group_name, sublist in groups.items()]
    I --> J[self.grouped_overlays[group_name] = {}]
    J --> K[for element in sublist]
    K --> L[self.grouped_overlays[group_name][element.layer_name] = element.get_name()]
    L --> M{not element.show}
    M -- True --> N[self.layers_untoggle.add(element.get_name())]
    N --> O[element.control = False]
    O --> P[if exclusive_groups]
    P --> Q[for element in sublist[1:]]
    Q --> R[self.layers_untoggle.add(element.get_name())]
```

## Raises:
- None explicitly raised by __init__, though parent class initialization may raise exceptions if used outside proper context

## Example:
```python
import folium

# Create a sample map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create some sample layers
tile_layer = folium.TileLayer(name='Base Map')
overlay1 = folium.FeatureGroup(name='Overlay 1')
overlay2 = folium.FeatureGroup(name='Overlay 2')

# Group layers into categories
groups = {
    'Transportation': [overlay1],
    'Environment': [overlay2]
}

# Create grouped layer control
control = folium.plugins.GroupedLayerControl(groups=groups, exclusive_groups=True)

# Add layers and control to map
m.add_child(tile_layer)
m.add_child(overlay1)
m.add_child(overlay2)
m.add_child(control)

# The control will show two groups: Transportation and Environment
# Within each group, only one layer can be selected at a time due to exclusive_groups=True
```

### `folium.plugins.groupedlayercontrol.GroupedLayerControl.__init__` · *method*

## Summary:
Initializes a grouped layer control with configurable groups of map overlays and optional exclusive group behavior.

## Description:
Configures the grouped layer control by processing input groups of map elements, setting up exclusive group options, and managing layer visibility states. This method establishes the internal data structures needed to control grouped overlays in folium maps, determining which layers should be initially hidden and how groups interact with each other. The method also configures each element's control property to False, effectively removing them from standard layer controls.

## Args:
    groups (dict[str, list]): Dictionary mapping group names (str) to lists of map overlay elements that belong to that group. Each element must have layer_name and get_name() methods, and a show attribute.
    exclusive_groups (bool): If True, makes groups mutually exclusive, preventing multiple layers within the same group from being visible simultaneously. Defaults to True.
    **kwargs: Additional options passed to the control, converted to camelCase format for JavaScript compatibility.

## Returns:
    None: This method initializes the object's internal state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "GroupedLayerControl" 
    - self.options: Set to parsed keyword arguments (dict with camelCase keys)
    - self.layers_untoggle: Initialized as an empty set, populated with layer names that should be hidden
    - self.grouped_overlays: Initialized as an empty dict, populated with group mappings to layer names

## Constraints:
    Preconditions:
        - groups parameter must be a dictionary mapping string keys to lists of map element objects
        - Each element in groups must have layer_name and get_name() methods
        - Each element in groups must have a show attribute (boolean)
        - Elements must support setting control attribute to False
    Postconditions:
        - self._name is set to "GroupedLayerControl"
        - self.options contains processed keyword arguments in camelCase format
        - self.layers_untoggle contains names of layers that should be hidden by default
        - self.grouped_overlays contains organized group-to-layer mappings
        - Each element in groups has its control attribute set to False

## Side Effects:
    Mutates: Each element in the groups parameter has its control attribute set to False.
    None: This method performs no I/O operations or external service calls. It only manipulates internal object state and modifies the control properties of input elements.

