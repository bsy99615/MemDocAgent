# `feature_group_sub_group.py`

## `folium.plugins.feature_group_sub_group.FeatureGroupSubGroup` · *class*

## Summary:
FeatureGroupSubGroup is a folium map layer class that creates nested feature groups for organizing map elements within hierarchical group structures.

## Description:
FeatureGroupSubGroup extends the Layer base class to provide functionality for creating nested feature groups in folium maps. It allows users to organize map elements into hierarchical groupings, where subgroups can be contained within larger feature groups. This class inherits from both JSCSSMixin and Layer, enabling automatic inclusion of required JavaScript dependencies for the leaflet.featuregroup.subgroup library.

## State:
- _group: Instance attribute storing the parent group reference that this subgroup belongs to
- _name: Instance attribute storing the name of this subgroup, hardcoded to "FeatureGroupSubGroup"
- layer_name: Inherited from Layer class, stores unique identifier for the layer
- overlay: Inherited from Layer class, indicates whether this layer is an overlay (True) or base layer (False). Default is False.
- control: Inherited from Layer class, controls whether this layer appears in the map's layer control interface. Default is True.
- show: Inherited from Layer class, determines initial visibility of the layer on the map. Default is True.

## Lifecycle:
- Creation: Instantiate with a parent group and optional parameters for name, overlay status, control visibility, and show state
- Usage: Add to a folium Map instance using add_child() method
- Destruction: Managed by parent Map object's lifecycle management

## Method Map:
```mermaid
graph TD
    A[FeatureGroupSubGroup.__init__] --> B[super().__init__()]
    B --> C[self._group = group]
    C --> D[self._name = "FeatureGroupSubGroup"]
    D --> E[Return initialized instance]
```

## Raises:
- None explicitly raised in __init__
- May propagate exceptions from parent class initialization

## Example:
```python
import folium

# Create a base map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a parent feature group
parent_group = folium.FeatureGroup(name="Parent Group")

# Create a subgroup within the parent group
sub_group = folium.plugins.FeatureGroupSubGroup(group=parent_group, name="Sub Group")

# Add elements to the subgroup
folium.Marker([45.524, -122.675], popup="Marker 1").add_to(sub_group)
folium.Marker([45.525, -122.676], popup="Marker 2").add_to(sub_group)

# Add subgroup to parent group
parent_group.add_child(sub_group)

# Add parent group to map
m.add_child(parent_group)

# The map now displays a hierarchical grouping in the layer control
```

### `folium.plugins.feature_group_sub_group.FeatureGroupSubGroup.__init__` · *method*

## Summary:
Initializes a FeatureGroupSubGroup instance that creates a nested feature group within a parent group, inheriting layer properties from the Layer base class.

## Description:
The __init__ method configures a FeatureGroupSubGroup object by initializing its parent Layer class with provided parameters and establishing its relationship with a parent group. This specialized layer type enables hierarchical organization of map elements within folium maps, allowing nested feature group structures where subgroups are contained within parent feature groups. The method overrides the name attribute to always use "FeatureGroupSubGroup" regardless of the provided name parameter.

## Args:
    group (any): The parent group object that this subgroup belongs to
    name (str, optional): Unique identifier for the subgroup. Defaults to None
    overlay (bool): Indicates whether this is an overlay layer. Defaults to True
    control (bool): Controls visibility in the map's layer control. Defaults to True
    show (bool): Determines initial visibility on the map. Defaults to True

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._group: Set to the provided group parameter
    - self._name: Set to "FeatureGroupSubGroup" (overriding any provided name)

## Constraints:
    Preconditions:
    - The group parameter must be a valid object reference
    - Parent Layer class initialization must succeed
    Postconditions:
    - self._group is assigned the provided group value
    - self._name is set to "FeatureGroupSubGroup"
    - Layer properties (overlay, control, show) are properly initialized through parent class

## Side Effects:
    None: This method performs no I/O operations or external service calls

