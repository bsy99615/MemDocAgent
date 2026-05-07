# `scroll_zoom_toggler.py`

## `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler` · *class*

## Summary:
A folium plugin class inheriting from MacroElement for scroll zoom toggling functionality.

## Description:
The ScrollZoomToggler class is a minimal folium plugin that extends MacroElement. It serves as a base implementation for a plugin that would provide scroll zoom toggle functionality in folium maps. The class is structured to integrate with folium's element system through inheritance, though the actual implementation details (such as the template) appear incomplete in the provided code.

## State:
- _name: str, set to "ScrollZoomToggler" - establishes the element identifier in folium's rendering system
- _template: Template object - currently initialized as empty (implementation appears incomplete)

## Lifecycle:
- Creation: Instantiate with `ScrollZoomToggler()` - no parameters required
- Usage: Intended to be added to folium.Map instances via `add_child()` method
- Destruction: Managed by folium's automatic cleanup mechanisms

## Method Map:
```mermaid
graph TD
    A[ScrollZoomToggler.__init__] --> B[MacroElement.__init__]
    B --> C[Sets _name="ScrollZoomToggler"]
```

## Raises:
- No explicit exceptions documented in the constructor
- Inherits potential exceptions from MacroElement initialization

## Example:
```python
import folium
from folium.plugins import ScrollZoomToggler

# Create a folium map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create the scroll zoom toggler plugin instance
toggler = ScrollZoomToggler()

# Add it to the map (this would typically provide UI controls)
m.add_child(toggler)
```

### `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler.__init__` · *method*

## Summary:
Initializes a ScrollZoomToggler instance by calling the parent MacroElement constructor and setting its identifying name.

## Description:
The constructor initializes a ScrollZoomToggler plugin instance by calling the parent MacroElement constructor and setting the internal `_name` attribute to "ScrollZoomToggler". This naming convention is essential for folium's element identification and rendering system. This method exists as a separate implementation to maintain proper inheritance chain and establish the plugin's identity within folium's element hierarchy.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "ScrollZoomToggler" to uniquely identify this element in folium's rendering system

## Constraints:
    Preconditions: None
    Postconditions: 
        - The instance is properly initialized as a MacroElement subclass
        - The instance has a unique identifier "_name" set to "ScrollZoomToggler"
        - The instance is ready to be added to folium.Map instances via add_child()

## Side Effects:
    None

