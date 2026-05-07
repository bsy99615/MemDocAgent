# `terminator.py`

## `folium.plugins.terminator.Terminator` · *class*

## Summary:
A Leaflet.js terminator plugin wrapper that displays the day/night terminator on a map.

## Description:
The Terminator class is a folium plugin that wraps the Leaflet.js terminator plugin. It inherits from JSCSSMixin and MacroElement and is designed to be added to folium maps to display the day/night terminator line.

## State:
- _name: str, set to "Terminator" - identifies this element type in folium's element hierarchy
- default_js: list of tuples - specifies the external JavaScript dependency for the terminator plugin, pointing to https://unpkg.com/@joergdietrich/leaflet.terminator
- _template: Template object - contains the HTML template for rendering the terminator element

## Lifecycle:
- Creation: Instantiate with no arguments. The constructor calls super().__init__() and sets the element name to "Terminator".
- Usage: Add to a folium Map object using add_child().
- Destruction: Managed automatically by folium's element lifecycle system.

## Method Map:
```mermaid
graph TD
    A[Terminator.__init__] --> B[super().__init__]
    B --> C[Sets _name="Terminator"]
```

## Raises:
- None explicitly raised by __init__

## Example:
```python
import folium
from folium.plugins import Terminator

# Create a map
m = folium.Map(location=[0, 0], zoom_start=2)

# Add the terminator plugin
terminator = Terminator()
m.add_child(terminator)

# The terminator line will be displayed on the map
```

### `folium.plugins.terminator.Terminator.__init__` · *method*

## Summary:
Initializes a Terminator instance and sets its identifying name to "Terminator".

## Description:
Constructs a new Terminator object by calling the parent class constructors and establishing the element's identifying name. This method is part of the standard folium element initialization process, ensuring the Terminator is properly registered within folium's element hierarchy with the correct type identifier.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._name (set to "Terminator")

## Constraints:
    Preconditions: None
    Postconditions: The Terminator instance has been initialized with _name = "Terminator"

## Side Effects:
    None

