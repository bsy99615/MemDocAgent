# `fullscreen.py`

## `folium.plugins.fullscreen.Fullscreen` · *class*

## Summary:
A Leaflet fullscreen control plugin that adds a full-screen toggle button to folium maps.

## Description:
The Fullscreen class implements a Leaflet fullscreen control that allows users to toggle between normal and full-screen view modes for folium maps. It inherits from JSCSSMixin and MacroElement, making it a standard folium control component that automatically manages its JavaScript and CSS dependencies. This control is typically added to map objects to enhance user experience by providing full-screen viewing capabilities.

## State:
- _name: str, set to "Fullscreen" indicating the element type
- options: dict, containing parsed configuration options including position, titles, and button settings
- default_js: list of tuples, specifies the JavaScript resource URL for the fullscreen control
- default_css: list of tuples, specifies the CSS resource URL for the fullscreen control

## Lifecycle:
- Creation: Instantiate with optional configuration parameters like position, titles, and button behavior
- Usage: Add to a folium Map object using the add_child() method or similar
- Destruction: Managed automatically through folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[Fullscreen.__init__] --> B[super().__init__]
    B --> C[parse_options]
    C --> D[Set self.options]
    D --> E[Set self._name]
```

## Raises:
- None explicitly raised by __init__, though parent classes may raise exceptions during rendering if not properly contained in a Figure context

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

# The map now includes a fullscreen toggle button in the top right corner
```

### `folium.plugins.fullscreen.Fullscreen.__init__` · *method*

## Summary:
Initializes a Fullscreen control plugin for folium maps with configurable positioning and labeling options.

## Description:
Configures the Fullscreen control by setting its name identifier and processing user-defined options for positioning, button labels, and display behavior. This method establishes the foundational configuration that determines how the fullscreen toggle appears and functions within a folium map interface.

## Args:
    position (str): Position of the fullscreen button on the map. Defaults to "topleft". Valid values are typically "topleft", "topright", "bottomleft", "bottomright".
    title (str): Text label for the fullscreen button when not in fullscreen mode. Defaults to "Full Screen".
    title_cancel (str): Text label for the fullscreen button when in fullscreen mode. Defaults to "Exit Full Screen".
    force_separate_button (bool): Whether to force the fullscreen button to appear separately from other controls. Defaults to False.
    **kwargs: Additional keyword arguments passed to the parse_options utility for further customization.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "Fullscreen" to identify the control type
        - self.options: Set to the processed dictionary of configuration options

## Constraints:
    Preconditions:
        - The class must inherit from MacroElement and JSCSSMixin
        - All provided arguments must be compatible with their expected types
    Postconditions:
        - The instance is properly initialized with a unique name identifier
        - Configuration options are processed and stored for later use in rendering

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal state.

