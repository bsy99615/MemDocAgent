# `groupedlayercontrol.py`

## `folium.plugins.groupedlayercontrol.GroupedLayerControl` · *class*

## Summary:
A grouped layer control for Leaflet maps that organizes overlay layers into logical groups with optional exclusive selection behavior.

## Description:
The GroupedLayerControl class creates a Leaflet map control that allows users to organize overlay layers into named groups. It provides functionality to manage layer visibility with optional exclusive selection within groups, where only one layer per group can be active at a time. This control integrates with the folium ecosystem to render properly within map visualizations and automatically includes required JavaScript and CSS resources from leaflet-groupedlayercontrol plugin.

## State:
- _name (str): Set to "GroupedLayerControl" to identify the element type in the rendering pipeline
- options (dict): Configuration options parsed from keyword arguments using parse_options, converted to camelCase format
- layers_untoggle (set): Set of layer names that should be initially hidden/unselected
- grouped_overlays (dict): Nested dictionary mapping group names to layer name mappings
- default_js (list): Class attribute containing JavaScript resource specifications for the grouped layer control plugin
- default_css (list): Class attribute containing CSS resource specifications for the grouped layer control plugin
- _template (Template): Jinja2 template used for rendering the control HTML, currently empty in source

## Lifecycle:
- Creation: Instantiate with groups dictionary mapping group names to lists of layer elements, optional exclusive_groups flag (defaults to True), and additional keyword arguments for control configuration
- Usage: Add to a folium.Map instance using the add_child() method; the control will automatically render with appropriate JavaScript/CSS dependencies via JSCSSMixin
- Destruction: No explicit cleanup required; inherits standard folium element lifecycle management

## Method Map:
```mermaid
graph TD
    A[GroupedLayerControl.__init__] --> B[super().__init__()]
    B --> C[Set _name to "GroupedLayerControl"]
    C --> D[Parse options with parse_options(**kwargs)]
    D --> E{exclusive_groups?}
    E -- Yes --> F[Set exclusiveGroups in options]
    E -- No --> G[Skip exclusiveGroups]
    F --> H[Initialize layers_untoggle set]
    H --> I[Initialize grouped_overlays dict]
    I --> J[Process each group in groups]
    J --> K[Process each element in group sublist]
    K --> L[Map element.layer_name to element.get_name()]
    L --> M{element.show?}
    M -- No --> N[Add element.get_name() to layers_untoggle]
    M -- Yes --> O[Skip layers_untoggle addition]
    N --> P[Set element.control = False]
    O --> P
    P --> Q{exclusive_groups and sublist length > 1?}
    Q -- Yes --> R[Add remaining elements to layers_untoggle]
    Q -- No --> S[Skip]
    R --> T[Continue processing]
    S --> T
    T --> U[End initialization]
```

## Raises:
- AssertionError: May be raised by parent classes during rendering if the control is not contained within a Figure context

## Example:
```python
# Create a grouped layer control with two groups
from folium import Map
from folium.plugins import GroupedLayerControl

# Assuming you have overlay layers like TileLayer or FeatureGroup objects
# grouped_layers = {
#     'Base Maps': [tile_layer1, tile_layer2],
#     'Overlays': [feature_group1, feature_group2]
# }
#
# control = GroupedLayerControl(grouped_layers, exclusive_groups=True)
# map_instance.add_child(control)
```

### `folium.plugins.groupedlayercontrol.GroupedLayerControl.__init__` · *method*

## Summary:
Initializes a grouped layer control that organizes map overlays into collapsible groups with optional exclusive selection behavior.

## Description:
Configures the grouped layer control by processing the provided groups of map elements, setting up internal data structures for layer organization, and preparing control options for JavaScript rendering. This method establishes the hierarchical grouping structure that allows users to manage multiple map layers through collapsible groups in the map control panel.

## Args:
    groups (dict): A dictionary mapping group names (str) to lists of map overlay elements. Each element in the lists must have layer_name, get_name(), show, and control attributes.
    exclusive_groups (bool): When True, ensures only one layer per group can be active simultaneously. Defaults to True.
    **kwargs: Additional options passed to the control, converted to camelCase format for JavaScript compatibility.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "GroupedLayerControl" 
    - self.options: Set to parsed keyword arguments with camelCase keys
    - self.layers_untoggle: Initialized as an empty set
    - self.grouped_overlays: Initialized as an empty dictionary

## Constraints:
    Preconditions:
        - groups must be a dictionary with string keys and iterable values
        - Each element in groups.values() must have layer_name, get_name(), show, and control attributes
        - Elements must support the get_name() method that returns a string identifier
    Postconditions:
        - self._name is set to "GroupedLayerControl"
        - self.options contains properly formatted camelCase options
        - self.layers_untoggle contains names of layers that should be initially hidden
        - self.grouped_overlays contains organized mapping of groups to layer names

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only manipulates internal object state.

