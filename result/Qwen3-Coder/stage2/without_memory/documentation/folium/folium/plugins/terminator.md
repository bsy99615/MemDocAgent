# `terminator.py`

## `folium.plugins.terminator.Terminator` · *class*

## Summary:
A folium plugin that integrates the Leaflet terminator plugin to display day/night boundaries on interactive maps.

## Description:
The Terminator class provides integration with the Leaflet.terminator plugin, which visualizes the terminator line (the boundary between day and night) on map displays. This plugin is commonly used to show the current position of sunlight on Earth's surface. The class follows folium's standard plugin architecture by inheriting from JSCSSMixin and MacroElement to handle JavaScript dependencies and rendering.

## State:
- `_name`: str, set to "Terminator" - identifies this element in folium's rendering system
- `default_js`: list of tuples containing JavaScript dependency information - specifies the Leaflet terminator plugin URL to load
- `_template`: Template object - currently empty, but would contain HTML/JavaScript template for rendering the terminator overlay

## Lifecycle:
- Creation: Instantiate with `Terminator()` - no parameters required
- Usage: Add to a folium.Map instance using `map.add_child(Terminator())`
- Destruction: Managed automatically by folium's rendering system when the map is disposed

## Method Map:
```mermaid
graph TD
    A[Terminator.__init__] --> B[JSCSSMixin.render]
    B --> C[Figure.header.add_child]
    C --> D[JavascriptLink(url)]
```

## Raises:
- AssertionError: If the Terminator element is not added to a Figure (via JSCSSMixin.render)

## Example:
```python
import folium
from folium.plugins import Terminator

# Create a map
m = folium.Map(location=[0, 0], zoom_start=2)

# Add the terminator plugin
terminator = Terminator()
m.add_child(terminator)

# Display the map
m
```

### `folium.plugins.terminator.Terminator.__init__` · *method*

## Summary:
Initializes a Terminator plugin instance and sets its identifying name for use in folium maps.

## Description:
This method constructs a Terminator plugin by calling the parent class constructors and establishing the plugin's identifying name. The Terminator plugin is used to draw terminator lines (day/night boundaries) on folium maps. This initialization ensures proper setup within the folium rendering framework.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._name

## Constraints:
    Preconditions: The class must inherit from MacroElement and JSCSSMixin
    Postconditions: The instance will have its _name attribute set to "Terminator"

## Side Effects:
    None

