# `scroll_zoom_toggler.py`

## `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler` · *class*

## Summary:
A Folium plugin component that provides a UI toggle for enabling/disabling scroll zoom functionality on interactive maps.

## Description:
The ScrollZoomToggler class is a specialized macro element that extends the base MacroElement from branca. It enables users to control scroll zoom behavior on Folium maps through a dedicated UI control. This component allows developers to give end-users the ability to toggle scroll zoom on/off, providing more granular control over map interactions. The class is intended to be added to Folium map objects to enhance user experience.

## State:
- `_template`: A Jinja2 Template object (type: Template) - Used to define the HTML/JavaScript rendering logic for the scroll zoom toggle functionality. In the provided implementation, this template appears to be empty, suggesting it may be incomplete or require additional implementation.
- `_name`: A string identifier (type: str, value: "ScrollZoomToggler") - Set during initialization to uniquely identify this component within the Folium element hierarchy and ensure proper integration with the map rendering system.

## Lifecycle:
- Creation: Instantiate using `ScrollZoomToggler()` constructor with no arguments. The constructor calls the parent MacroElement's `__init__` method and sets the internal name to "ScrollZoomToggler".
- Usage: The component integrates automatically into Folium map rendering when added to a map object using `map.add_child()`. The actual scroll zoom toggle behavior would be implemented in the template content.
- Destruction: Cleanup is handled automatically by the Folium framework when the map is disposed or rendered.

## Method Map:
```mermaid
graph TD
    A[ScrollZoomToggler.__init__] --> B[MacroElement.__init__]
    B --> C[Sets _name="ScrollZoomToggler"]
```

## Raises:
- No explicit exceptions are raised by the `__init__` method in the provided implementation.
- Any exceptions would stem from the parent MacroElement class initialization, which are not specified in the provided code.

## Example:
```python
import folium
from folium.plugins import ScrollZoomToggler

# Create a map centered on Portland, OR
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add the scroll zoom toggler plugin to provide UI control
scroll_toggle = ScrollZoomToggler()
m.add_child(scroll_toggle)

# The resulting map will include a UI element allowing users to toggle scroll zoom
```

### `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler.__init__` · *method*

## Summary:
Initializes a ScrollZoomToggler instance by setting its name attribute and calling the parent class constructor.

## Description:
This method serves as the constructor for the ScrollZoomToggler class, which extends MacroElement from the branca library. It initializes the component by calling the parent's constructor and setting the internal `_name` attribute to "ScrollZoomToggler". This naming convention is crucial for proper integration with Folium's map rendering system and ensures the component is correctly identified within the element hierarchy.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to the string "ScrollZoomToggler"

## Constraints:
    Preconditions:
        - The class must inherit from MacroElement (which it does)
        - The parent class constructor must accept no arguments
    Postconditions:
        - The instance will have its `_name` attribute set to "ScrollZoomToggler"
        - The instance will be properly initialized as a MacroElement

## Side Effects:
    None

