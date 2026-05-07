# `fullscreen.py`

## `folium.plugins.fullscreen.Fullscreen` · *class*

## Summary:
A Folium plugin that adds a fullscreen toggle control to Leaflet maps using the Leaflet.fullscreen library.

## Description:
The Fullscreen class implements a Leaflet fullscreen control that allows users to toggle between normal and fullscreen map views. It inherits from JSCSSMixin and MacroElement to properly integrate JavaScript and CSS resources into Folium maps. This component is typically added to Folium Map objects to provide fullscreen functionality to viewers.

## State:
- _name: str, set to "Fullscreen" - identifies the component type for Folium's internal tracking
- options: dict - processed configuration options for the fullscreen control, including position, titles, and button settings
- default_js: list of tuples - CDN URLs for the Leaflet.fullscreen JavaScript library
- default_css: list of tuples - CDN URLs for the Leaflet.fullscreen CSS styles

## Lifecycle:
- Creation: Instantiate with optional configuration parameters such as position, title, and button settings
- Usage: Add to a Folium Map object using the add_child() method
- Destruction: Managed automatically by Folium's rendering system when the map is rendered

## Method Map:
```mermaid
graph TD
    A[Fullscreen.__init__] --> B[super().__init__()]
    B --> C[parse_options processing]
    C --> D[JSCSSMixin.render]
    D --> E[Figure.header.add_child]
    E --> F[JavascriptLink/CssLink]
```

## Raises:
- AssertionError: When invalid options are passed to parse_options (if the base class validates options)

## Example:
```python
import folium
from folium.plugins import Fullscreen

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add fullscreen control
fullscreen = Fullscreen(position='topright', title='Expand Map', title_cancel='Exit Fullscreen')
m.add_child(fullscreen)

# The map will now have a fullscreen toggle button in the top right corner
```

### `folium.plugins.fullscreen.Fullscreen.__init__` · *method*

## Summary:
Initializes a Fullscreen plugin with configurable positioning and labeling options.

## Description:
Configures the fullscreen functionality for a Folium map by setting up the plugin's name and processing configuration options. This method establishes the basic properties needed for rendering the fullscreen control in the map interface.

## Args:
    position (str): Position of the fullscreen button on the map. Defaults to "topleft".
    title (str): Title text for the fullscreen button when not in fullscreen mode. Defaults to "Full Screen".
    title_cancel (str): Title text for the fullscreen button when in fullscreen mode. Defaults to "Exit Full Screen".
    force_separate_button (bool): Whether to force the fullscreen button to appear separately. Defaults to False.
    **kwargs: Additional keyword arguments passed to the options parser.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: If any option provided doesn't match the expected type or is not in the valid options list (inherited from parent classes).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Fullscreen" to identify the plugin type
    - self.options: Set to parsed options dictionary containing position, title, title_cancel, and force_separate_button

## Constraints:
    Preconditions: 
    - The class must inherit from MacroElement and JSCSSMixin
    - All provided arguments must be compatible with the expected types for the options parsing
    
    Postconditions:
    - self._name is set to "Fullscreen"
    - self.options contains a properly formatted dictionary of configuration options

## Side Effects:
    None: This method performs no I/O operations or external service calls.

