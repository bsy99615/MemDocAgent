# `feature_group_sub_group.py`

## `folium.plugins.feature_group_sub_group.FeatureGroupSubGroup` · *class*

## Summary:
A Folium layer class that creates subgroups within feature groups for hierarchical map organization using the leaflet.featuregroup.subgroup JavaScript plugin.

## Description:
The FeatureGroupSubGroup class implements a subgroup functionality that allows for nested organization of map features within Leaflet-based Folium maps. It leverages the leaflet.featuregroup.subgroup JavaScript library to enable hierarchical grouping of geographic features. This class is designed to be used within existing FeatureGroups to create nested organizational structures for map layers.

The class inherits from both JSCSSMixin for JavaScript/CSS resource management and Layer for standard map layer properties, making it suitable for integration into Folium's map rendering system. It is intended to work with the leaflet.featuregroup.subgroup JavaScript plugin which provides the client-side functionality for subgroup management.

## State:
- _group: str - The parent group identifier that this subgroup belongs to (passed as required parameter to __init__)
- _name: str - The name assigned to this subgroup (hardcoded to "FeatureGroupSubGroup" in current implementation, overriding any name parameter)
- _template: Template - Empty Jinja2 template (indicating incomplete implementation for HTML rendering)
- layer_name: str - Inherited from Layer class, represents the unique identifier for this layer
- overlay: bool - Inherited from Layer class, indicates if this layer is treated as an overlay (defaults to True)
- control: bool - Inherited from Layer class, indicates if this layer appears in map controls (defaults to True)
- show: bool - Inherited from Layer class, indicates initial visibility of this layer (defaults to True)

The __init__ parameters have these defaults and constraints:
- group: Required string parameter identifying the parent feature group
- name: Optional string, defaults to None (but overridden by hardcoded "FeatureGroupSubGroup")
- overlay: Boolean, defaults to True
- control: Boolean, defaults to True
- show: Boolean, defaults to True

Class invariants:
- The _group attribute must be a valid string identifier for a parent feature group
- All inherited Layer properties (overlay, control, show) must be boolean values
- The _name is currently hardcoded to "FeatureGroupSubGroup" regardless of the name parameter passed to __init__
- The _template is initialized but empty, suggesting incomplete implementation for HTML rendering

## Lifecycle:
Creation: Instantiate using FeatureGroupSubGroup(group, name=None, overlay=True, control=True, show=True)
Usage: Typically added to a parent FeatureGroup or Map object to create nested grouping structures
Destruction: Managed by Folium's garbage collection and parent element lifecycle management

## Method Map:
```mermaid
graph TD
    A[FeatureGroupSubGroup.__init__] --> B[super().__init__()]
    A --> C[self._group = group]
    A --> D[self._name = "FeatureGroupSubGroup"]
    B --> E[Layer.__init__]
    E --> F[Layer sets layer_name, overlay, control, show]
```

## Raises:
- No explicit exceptions are raised by the __init__ method based on the provided code
- However, the parent Layer.__init__ or JSCSSMixin.__init__ may raise exceptions if validation is performed

## Example:
```python
import folium

# Create a base map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a parent feature group
parent_group = folium.FeatureGroup(name="Parent Group")

# Create a subgroup within the parent group
sub_group = folium.plugins.FeatureGroupSubGroup(
    group="Parent Group", 
    name="Sub Group", 
    overlay=True, 
    control=True, 
    show=True
)

# Add the subgroup to the parent group
parent_group.add_child(sub_group)

# Add the parent group to the map
m.add_child(parent_group)
```

### `folium.plugins.feature_group_sub_group.FeatureGroupSubGroup.__init__` · *method*

## Summary:
Initializes a FeatureGroupSubGroup instance with a parent group reference and standard layer properties, overriding any provided name parameter.

## Description:
The __init__ method constructs a FeatureGroupSubGroup object that represents a subgroup within a parent feature group. This method sets up the basic layer properties inherited from the Layer class while establishing the relationship to a parent group. Notably, the name parameter is overridden internally to always use "FeatureGroupSubGroup", regardless of the value provided.

This initialization method is part of the FeatureGroupSubGroup class which implements hierarchical grouping functionality for Folium maps using the leaflet.featuregroup.subgroup JavaScript plugin. The method ensures proper inheritance from both Layer and JSCSSMixin classes while setting up the required group relationship.

## Args:
    group (str): Required identifier for the parent feature group that this subgroup belongs to.
    name (str, optional): Name for the subgroup. Defaults to None. Note: This parameter is overridden internally to "FeatureGroupSubGroup".
    overlay (bool, optional): Whether this subgroup should be treated as an overlay. Defaults to True.
    control (bool, optional): Whether this subgroup should appear in map controls. Defaults to True.
    show (bool, optional): Whether this subgroup should be initially visible. Defaults to True.

## Returns:
    None: This method initializes the object state but does not return a value.

## Raises:
    No explicit exceptions are raised by this method based on the provided implementation.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._group: Set to the provided group parameter
    - self._name: Hardcoded to "FeatureGroupSubGroup" (overriding any provided name parameter)
    - self.layer_name: Set by parent Layer.__init__ (inherited from Layer class)
    - self.overlay: Set by parent Layer.__init__ (inherited from Layer class)
    - self.control: Set by parent Layer.__init__ (inherited from Layer class)
    - self.show: Set by parent Layer.__init__ (inherited from Layer class)

## Constraints:
    Preconditions:
    - The group parameter must be a valid string identifier for a parent feature group
    - All boolean parameters (overlay, control, show) must be boolean values
    
    Postconditions:
    - The object will have a _group attribute set to the provided group parameter
    - The object will have _name set to "FeatureGroupSubGroup" (regardless of name parameter)
    - The object will inherit all Layer properties (overlay, control, show, layer_name)

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

