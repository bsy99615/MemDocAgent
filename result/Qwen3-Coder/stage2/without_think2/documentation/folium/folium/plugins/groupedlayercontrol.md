# `groupedlayercontrol.py`

## `folium.plugins.groupedlayercontrol.GroupedLayerControl` · *class*

## Summary:
GroupedLayerControl is a folium plugin that creates a grouped layer control for Leaflet maps, allowing users to organize map layers into logical groups with optional exclusive selection behavior.

## Description:
This class implements a grouped layer control that extends folium's base map functionality by providing a hierarchical organization of map layers. It allows developers to group related map overlays (such as different types of markers, polygons, or other visual elements) into named categories, making complex maps more navigable. The control supports exclusive group behavior where only one layer within a group can be active at a time.

The class inherits from JSCSSMixin and MacroElement, making it compatible with folium's rendering system and ensuring proper inclusion of required JavaScript and CSS dependencies.

## State:
- groups: Dictionary mapping group names (str) to lists of map overlay elements (typically folium Layer objects)
- exclusive_groups: Boolean flag (default True) indicating whether layers within groups are mutually exclusive
- options: Dictionary of parsed options passed to the underlying Leaflet plugin via parse_options()
- layers_untoggle: Set of layer names (str) that should be initially hidden/unselected
- grouped_overlays: Nested dictionary organizing overlay elements by group name and layer name

## Lifecycle:
- Creation: Instantiate with a groups dictionary and optional exclusive_groups flag
- Usage: Add to a folium.Map instance using the add_child() method
- Destruction: Managed automatically through folium's element lifecycle

## Method Map:
```mermaid
graph TD
    A[GroupedLayerControl.__init__] --> B[super().__init__()]
    B --> C[Set _name = "GroupedLayerControl"]
    C --> D[Parse options with parse_options()]
    D --> E{exclusive_groups?}
    E -- Yes --> F[Set exclusiveGroups in options]
    E -- No --> G[Continue]
    F --> G
    G --> H[Iterate through groups dictionary]
    H --> I[Initialize grouped_overlays entry for group]
    I --> J[Iterate through elements in group]
    J --> K[Store element.layer_name -> element.get_name() mapping]
    K --> L{element.show?}
    L -- No --> M[Add element.get_name() to layers_untoggle]
    L -- Yes --> N[Continue]
    M --> N
    N --> O[Set element.control = False]
    O --> P{exclusive_groups?}
    P -- Yes --> Q[Add subsequent elements to layers_untoggle]
    P -- No --> R[End]
    Q --> R
```

## Raises:
- None explicitly raised by __init__
- Inherited exceptions from JSCSSMixin and MacroElement base classes during rendering

## Example:
```python
import folium
from folium.plugins import GroupedLayerControl

# Create a basic map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add some sample layers (these would typically be created from folium.Layer objects)
marker = folium.Marker([45.5236, -122.6750], popup='Portland')
circle = folium.CircleMarker([45.5236, -122.6750], radius=50, color='red')

# Define groups for layer control
groups = {
    'Points of Interest': [marker],
    'Area Markers': [circle]
}

# Create and add grouped layer control
control = GroupedLayerControl(groups, exclusive_groups=True)
m.add_child(control)

# The map now displays a grouped layer control with exclusive selection
```

### `folium.plugins.groupedlayercontrol.GroupedLayerControl.__init__` · *method*

## Summary:
Initializes a GroupedLayerControl object that manages grouped overlays in a folium map with optional exclusive group behavior.

## Description:
Configures the GroupedLayerControl instance by setting up internal data structures for managing grouped map layers, processing layer visibility settings, and preparing options for JavaScript rendering. This method establishes the foundational state for controlling grouped overlays in a folium map interface, where layers can be organized into logical groups with optional mutual exclusivity.

## Args:
    groups (dict): A dictionary mapping group names (str) to lists of overlay elements that belong to each group. Each element in the lists must have layer_name and get_name methods, and a show attribute.
    exclusive_groups (bool): Flag indicating whether layers within each group should be mutually exclusive (only one can be active at a time). Defaults to True.
    **kwargs: Additional keyword arguments passed to configure control options, converted to camelCase format via parse_options.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "GroupedLayerControl"
    - self.options: Set to parsed keyword arguments with camelCase conversion
    - self.layers_untoggle: Initialized as an empty set and populated with layer names
    - self.grouped_overlays: Initialized as an empty dictionary and populated with group-layer mappings

## Constraints:
    Preconditions:
    - groups parameter must be a dictionary with string keys and iterable values
    - Each value in groups must contain elements with layer_name attribute and get_name() method
    - Each element in groups must have a show attribute (boolean) and control attribute
    - Elements must support the folium map element interface
    
    Postconditions:
    - self._name is set to "GroupedLayerControl"
    - self.options contains processed keyword arguments in camelCase format
    - self.layers_untoggle contains names of layers that should be initially hidden
    - self.grouped_overlays maps group names to dictionaries mapping layer_name to get_name() return values
    - Each element's control attribute is set to False

## Side Effects:
    - Modifies element.control attribute on each layer in groups to False
    - Adds layer names to self.layers_untoggle based on element.show status and exclusive_groups flag
    - Sets up internal data structures for layer grouping and control management
    - Populates self.grouped_overlays with mapping of group names to layer name mappings

