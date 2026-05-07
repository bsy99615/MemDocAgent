# `fullscreen.py`

## `folium.plugins.fullscreen.Fullscreen` · *class*

## Summary:
Fullscreen is a folium plugin that adds a full-screen toggle control to Leaflet maps, enabling users to expand the map to fill the entire browser window.

## Description:
The Fullscreen class implements a Leaflet fullscreen control that allows users to toggle between normal map view and full-screen mode. It inherits from JSCSSMixin and MacroElement to integrate seamlessly with folium's rendering system and automatically include required JavaScript and CSS dependencies. This control is typically added to folium maps to enhance user experience by providing full-screen viewing capabilities.

## State:
- _name (str): Set to "Fullscreen" to identify the element type
- options (dict): Configuration options parsed from constructor parameters including position, titles, and button settings via parse_options()
- default_js (list): List of JavaScript dependencies required for fullscreen functionality, including Control.Fullscreen.js from CDN
- default_css (list): List of CSS dependencies required for fullscreen styling, including Control.FullScreen.css from CDN
- _template (Template): Empty Jinja2 template (likely intended for HTML generation but not implemented in current version)

## Lifecycle:
- Creation: Instantiate with optional configuration parameters; automatically registers default JS/CSS dependencies through JSCSSMixin inheritance
- Usage: Add to a folium.Map instance using the add_child() method; rendered automatically during map generation through the JSCSSMixin rendering mechanism
- Destruction: Managed by folium's element lifecycle; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[Fullscreen.__init__] --> B[super().__init__()]
    B --> C[Set _name="Fullscreen"]
    C --> D[parse_options()]
    D --> E[options set with position, title, title_cancel, force_separate_button]
    E --> F[return]
    
    G[Map.render()] --> H[JSCSSMixin.render()]
    H --> I[Get root element]
    I --> J[Add JS/CSS links to figure header]
    J --> K[Render parent MacroElement]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if dependencies are improperly configured or if the element is not properly contained within a Figure object

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add fullscreen control
fullscreen = folium.plugins.Fullscreen(
    position='topright',
    title='Expand to Full Screen',
    title_cancel='Exit Full Screen'
)
m.add_child(fullscreen)

# The map now includes a fullscreen toggle button in the top right corner
# When clicked, it will toggle between normal view and full screen mode
```

### `folium.plugins.fullscreen.Fullscreen.__init__` · *method*

## Summary:
Initializes a Fullscreen plugin instance with configurable display options and properties.

## Description:
Configures the Fullscreen plugin by setting its name and processing initialization parameters into a structured options dictionary. This method establishes the plugin's identity and prepares its configuration for rendering in a Folium map interface.

## Args:
    position (str): Position of the fullscreen button on the map. Defaults to "topleft".
    title (str): Title text for the fullscreen button. Defaults to "Full Screen".
    title_cancel (str): Title text for the exit fullscreen button. Defaults to "Exit Full Screen".
    force_separate_button (bool): Whether to force the fullscreen button to appear separately. Defaults to False.
    **kwargs: Additional keyword arguments passed to the parent class constructor.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Fullscreen" to identify the plugin type
    - self.options: Set to the processed dictionary of configuration options

## Constraints:
    Preconditions:
    - The parent class (MacroElement) must be properly initialized
    - All provided arguments must be compatible with the parent class constructor
    
    Postconditions:
    - The instance's _name attribute is set to "Fullscreen"
    - The instance's options attribute contains a properly formatted dictionary of configuration parameters

## Side Effects:
    None

