# `scroll_zoom_toggler.py`

## `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler` · *class*

## Summary:
A folium plugin that provides scroll zoom toggle functionality for interactive maps.

## Description:
The ScrollZoomToggler class creates a UI control element that allows users to enable or disable scroll zoom interactions on folium maps. As a subclass of MacroElement, it integrates with folium's rendering pipeline to add a toggle button that controls whether users can zoom the map using mouse wheel scrolling.

## State:
- `_name`: str, set to "ScrollZoomToggler" - uniquely identifies this element within folium's element registry
- `_template`: jinja2.Template object - contains the HTML/JavaScript template for the control element (currently empty in the implementation)

## Lifecycle:
- Creation: Instantiate with `ScrollZoomToggler()` - no parameters required
- Usage: Add to a folium map using `map.add_child(ScrollZoomToggler())` or similar methods
- Destruction: Managed automatically by folium's element lifecycle management system

## Method Map:
```mermaid
graph TD
    A[ScrollZoomToggler.__init__] --> B[MacroElement.__init__]
    B --> C[Sets _name="ScrollZoomToggler"]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent MacroElement.__init__ if called with invalid arguments

## Example:
```python
import folium
from folium.plugins import ScrollZoomToggler

# Create a folium map
m = folium.Map([45.5236, -122.6750], zoom_start=13)

# Add the scroll zoom toggler plugin to the map
toggler = ScrollZoomToggler()
m.add_child(toggler)

# The resulting map will include a control that lets users toggle scroll zoom
# This is particularly useful when you want to prevent accidental zooming
# or when implementing custom zoom controls
```

### `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler.__init__` · *method*

## Summary:
Initializes a ScrollZoomToggler instance, setting up the element name for folium's rendering system to enable scroll zoom toggle functionality.

## Description:
This method initializes a ScrollZoomToggler object by calling the parent MacroElement constructor and assigning the unique identifier "_name" to "ScrollZoomToggler". This naming convention is essential for folium's element registry and rendering pipeline to properly identify and manage this control element within the map interface. The ScrollZoomToggler provides a UI control that allows users to enable or disable scroll zoom interactions on folium maps.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this method
    - May raise exceptions from MacroElement.__init__() if called with invalid arguments

## State Changes:
    - Attributes READ: None
    - Attributes WRITTEN: 
        - self._name: Set to "ScrollZoomToggler" to identify this element in folium's element registry

## Constraints:
    - Preconditions: None
    - Postconditions: The instance will have its _name attribute set to "ScrollZoomToggler"

## Side Effects:
    - None

