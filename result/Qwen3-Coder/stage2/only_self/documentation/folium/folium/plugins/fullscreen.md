# `fullscreen.py`

## `folium.plugins.fullscreen.Fullscreen` · *class*

## Summary:
A Leaflet fullscreen control plugin that adds a full-screen toggle button to folium maps.

## Description:
The Fullscreen class implements a Leaflet fullscreen control that allows users to toggle between normal and full-screen view modes for folium maps. It inherits from JSCSSMixin and MacroElement, making it compatible with folium's element system and automatically managing JavaScript/CSS dependencies. This component provides a user interface control that enhances map interactivity by enabling full-screen viewing.

## State:
- _name: str, set to "Fullscreen" - identifies this element type
- options: dict, processed configuration options including position, titles, and button settings
- default_js: list of tuples containing JS resource names and URLs for the fullscreen control
- default_css: list of tuples containing CSS resource names and URLs for the fullscreen control

## Lifecycle:
- Creation: Instantiate with optional configuration parameters (position, titles, etc.)
- Usage: Add to a folium.Map instance using add_child() method
- Rendering: During map rendering, JSCSSMixin automatically includes required JS/CSS resources

## Method Map:
```mermaid
graph TD
    A[Fullscreen.__init__] --> B[super().__init__()]
    B --> C[self._name = "Fullscreen"]
    C --> D[self.options = parse_options(...)]
    D --> E[Inherits from JSCSSMixin]
    E --> F[Automatic JS/CSS inclusion during render()]
```

## Raises:
- None explicitly raised by __init__
- AssertionError may occur during render() if not properly contained within a Figure context (inherited from JSCSSMixin)

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add fullscreen control
fullscreen = folium.plugins.Fullscreen(
    position='topright',
    title='Expand me',
    title_cancel='Exit full screen'
)
m.add_child(fullscreen)

# The fullscreen control will appear in the top right corner
```

### `folium.plugins.fullscreen.Fullscreen.__init__` · *method*

## Summary:
Initializes a Fullscreen control element with configurable positioning and display options.

## Description:
Configures the Fullscreen control by setting its name to "Fullscreen" and processing initialization parameters through the parse_options utility. This method establishes the control's basic properties and prepares it for integration into folium maps with customizable appearance and behavior.

## Args:
    position (str): Position of the fullscreen button on the map. Defaults to "topleft".
    title (str): Title text displayed when not in fullscreen mode. Defaults to "Full Screen".
    title_cancel (str): Title text displayed when in fullscreen mode. Defaults to "Exit Full Screen".
    force_separate_button (bool): Whether to force the fullscreen button to appear separately. Defaults to False.
    **kwargs: Additional keyword arguments passed to parse_options for further customization.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "Fullscreen"
        - self.options: Set to the processed dictionary from parse_options

## Constraints:
    Preconditions:
        - The class must inherit from MacroElement and JSCSSMixin
        - All arguments must be compatible with the parse_options utility
    Postconditions:
        - self._name is set to "Fullscreen"
        - self.options contains properly formatted camelCase key-value pairs

## Side Effects:
    None: This method performs no I/O operations or external service calls.

