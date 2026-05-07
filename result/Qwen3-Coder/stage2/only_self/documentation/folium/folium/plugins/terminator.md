# `terminator.py`

## `folium.plugins.terminator.Terminator` · *class*

## Summary:
A folium plugin that integrates Leaflet's terminator plugin to display day/night terminator lines on interactive maps.

## Description:
The Terminator class implements a folium-compatible map element that displays the day/night terminator line on maps using the Leaflet.terminator JavaScript library. This line represents the boundary between day and night on Earth's surface, showing where the sun is shining and where it's dark.

This class follows folium's plugin architecture pattern, inheriting from JSCSSMixin for JavaScript/CSS resource management and MacroElement for map element integration. It serves as a bridge between folium's Python interface and the Leaflet.js terminator functionality.

## State:
- _name: str, set to "Terminator" - identifies this element type in folium's rendering system
- default_js: list of tuples - contains JavaScript library URL for Leaflet.terminator plugin
- _template: jinja2.Template - empty template (likely populated in full implementation)

## Lifecycle:
- Creation: Instantiate with `Terminator()` - no parameters required
- Usage: Add to a folium.Map or folium.Figure using `map.add_child(terminator_instance)`
- Rendering: During map rendering, JSCSSMixin automatically loads the required JavaScript library
- Destruction: Managed by folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[Terminator.__init__] --> B[super().__init__()]
    B --> C[self._name = "Terminator"]
    C --> D[Inherits JSCSSMixin capabilities]
    D --> E[Automatic JS/CSS loading during render()]
```

## Raises:
- AssertionError: May be raised by JSCSSMixin.render() if the element is not properly contained within a Figure instance during rendering

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[0, 0], zoom_start=2)

# Create and add terminator plugin
terminator = folium.plugins.Terminator()
m.add_child(terminator)

# The terminator line will be displayed on the map
# when rendered, showing the day/night boundary
```

### `folium.plugins.terminator.Terminator.__init__` · *method*

## Summary:
Initializes a Terminator plugin instance, setting its name identifier for use in folium maps.

## Description:
This constructor initializes a Terminator plugin instance by calling the parent class constructors and setting the internal name attribute. The Terminator plugin is used to draw terminator lines (day/night boundaries) on folium maps.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "Terminator" string

## Constraints:
    Preconditions:
        - Must be called on an instance of Terminator class
        - Parent classes (MacroElement, JSCSSMixin) must be properly initialized
    Postconditions:
        - Instance has _name attribute set to "Terminator"
        - Parent class initialization is completed

## Side Effects:
    None

