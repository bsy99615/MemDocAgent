# `geocoder.py`

## `folium.plugins.geocoder.Geocoder` · *class*

## Summary:
A geocoder plugin for folium maps that provides address search functionality using the Leaflet Control Geocoder library.

## Description:
The Geocoder class implements a map control that allows users to search for geographic locations by address using the Leaflet Control Geocoder library. It integrates seamlessly with folium's map rendering system and provides a user-friendly interface for geocoding operations. This class is designed to be instantiated as part of a folium Figure to add geocoding capabilities to interactive maps.

## State:
- _name: String identifier set to "Geocoder" that uniquely identifies this element type
- _template: Jinja2 Template object (currently empty) that defines the HTML template for rendering the geocoder control
- options: Dictionary containing configuration options processed through parse_options, including:
  - collapsed (bool): Whether the geocoder control is initially collapsed
  - position (str): Position of the control on the map (default: "topright")
  - defaultMarkGeocode (bool): Whether to add a marker at the geocoded location
- default_js: Class attribute listing the JavaScript dependency for leaflet-control-geocoder
- default_css: Class attribute listing the CSS dependency for leaflet-control-geocoder

## Lifecycle:
- Creation: Instantiate with optional parameters collapsed, position, add_marker, and additional keyword arguments
- Usage: Add to a folium Figure using the standard map.add_child() method
- Destruction: Automatically handled by folium's element management system when the figure is disposed

## Method Map:
```mermaid
graph TD
    A[Geocoder.__init__] --> B[super().__init__()]
    B --> C[Set self._name]
    C --> D[parse_options]
    D --> E[Set self.options]
```

## Raises:
- None explicitly raised by __init__, though parent classes may raise exceptions during rendering if not properly contained in a Figure context

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Add geocoder control
geocoder = folium.plugins.Geocoder(
    collapsed=False,
    position="topleft",
    add_marker=True
)
m.add_child(geocoder)

# The map now includes a geocoder control in the top-left corner
```

### `folium.plugins.geocoder.Geocoder.__init__` · *method*

## Summary:
Initializes a geocoder control with configurable display options and positioning.

## Description:
Configures the geocoder control by setting up its display properties, positioning, and marker behavior. This method prepares the geocoder element for integration into folium maps by initializing parent classes and processing configuration options.

## Args:
    collapsed (bool): Whether the geocoder control is initially collapsed. Defaults to False.
    position (str): Position of the control on the map. Defaults to "topright".
    add_marker (bool): Whether to add a marker at the geocoded location. Defaults to True.
    **kwargs: Additional keyword arguments passed to the options parser.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though parent class initialization may raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Geocoder" to identify this element type
    - self.options: Set to the processed dictionary of configuration options

## Constraints:
    Preconditions:
        - The object must be properly initialized as a subclass of MacroElement and JSCSSMixin
        - All keyword arguments must be valid for the parse_options function
    Postconditions:
        - self._name is set to "Geocoder"
        - self.options contains processed configuration options in camelCase format
        - Parent classes are properly initialized

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only modifies internal object state.

