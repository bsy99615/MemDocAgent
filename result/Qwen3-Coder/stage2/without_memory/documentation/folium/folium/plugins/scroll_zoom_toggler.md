# `scroll_zoom_toggler.py`

## `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler` · *class*

## Summary:
A folium plugin component that provides UI controls to toggle scroll zoom functionality on interactive maps.

## Description:
The ScrollZoomToggler class is a folium plugin that adds scroll zoom toggle functionality to interactive maps. It inherits from MacroElement to integrate with folium's templating and rendering system. This component allows users to enable or disable scroll-based zoom interactions on the map, providing more control over map navigation behavior. The plugin is typically used in web mapping applications where scroll zoom might interfere with other user interactions.

## State:
- _name: str, set to "ScrollZoomToggler" - identifies this component in folium's element hierarchy
- _template: Template - a Jinja2 template object (currently empty in the provided code snippet) that would contain the HTML/JavaScript implementation for the scroll zoom toggle UI controls

## Lifecycle:
- Creation: Instantiate with `ScrollZoomToggler()` - no parameters required
- Usage: Automatically integrated into folium map rendering through MacroElement inheritance
- Destruction: Managed by folium's element lifecycle management system

## Method Map:
```mermaid
graph TD
    A[ScrollZoomToggler.__init__] --> B[MacroElement.__init__]
    B --> C[Sets _name="ScrollZoomToggler"]
```

## Raises:
- None explicitly documented in the provided code
- May inherit exceptions from MacroElement parent class (full implementation details not visible)

## Example:
```python
import folium
from folium.plugins import ScrollZoomToggler

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add the scroll zoom toggler plugin
scroll_toggle = ScrollZoomToggler()
m.add_child(scroll_toggle)

# The map now includes UI controls to toggle scroll zoom functionality
```

### `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler.__init__` · *method*

*No documentation generated.*

