# `geocoder.py`

## `folium.plugins.geocoder.Geocoder` · *class*

## Summary:
Geocoder is a folium plugin class that adds geocoding functionality to interactive maps by integrating the Leaflet Control Geocoder library.

## Description:
The Geocoder class enables users to search for locations by address or place name directly on a folium map. It inherits from JSCSSMixin and MacroElement to provide automatic JavaScript and CSS dependency management and integrates with Leaflet's geocoding control. This class is typically instantiated when creating interactive maps that require location search capabilities, often used in applications like mapping tools, location-based services, or geographic information systems.

## State:
- _name (str): Set to "Geocoder" to identify the element type in the rendering pipeline
- options (dict): Configuration options for the geocoder control, processed through parse_options to convert snake_case to camelCase keys
- default_js (list): List of JavaScript dependencies including the Leaflet Control Geocoder library
- default_css (list): List of CSS dependencies for styling the geocoder control
- _template (Template): Jinja2 template for rendering the geocoder control HTML, currently empty in the source

## Lifecycle:
- Creation: Instantiate with optional parameters like collapsed, position, and add_marker
- Usage: Automatically included in map rendering when added to a folium.Map instance
- Destruction: Managed by the parent Element's lifecycle when the map is disposed

## Method Map:
```mermaid
graph TD
    A[Geocoder.__init__] --> B[super().__init__()]
    B --> C[self._name = "Geocoder"]
    C --> D[self.options = parse_options(...)]
    D --> E[Inherits JSCSSMixin capabilities]
    E --> F[Automatic JS/CSS inclusion during render]
```

## Raises:
- None explicitly raised in __init__
- May raise exceptions from parent classes during rendering if dependencies aren't properly handled

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

# The map now includes a geocoding search bar in the top-left corner
```

### `folium.plugins.geocoder.Geocoder.__init__` · *method*

## Summary:
Initializes a Geocoder plugin instance with configurable display options and marker behavior.

## Description:
Configures the geocoder plugin by setting its name, parsing initialization parameters into JavaScript-compatible options, and establishing default behavior for UI display and marker placement. This method serves as the constructor for the Geocoder class, preparing the object for integration with folium maps.

## Args:
    collapsed (bool): Whether the geocoder control should be collapsed by default. Defaults to False.
    position (str): Position of the geocoder control on the map. Defaults to "topright".
    add_marker (bool): Whether to add a marker when a location is geocoded. Defaults to True.
    **kwargs: Additional keyword arguments passed to the underlying options parser.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Geocoder" to identify the plugin type
    - self.options: Set to the parsed options dictionary containing UI configuration

## Constraints:
    Preconditions: 
    - The parent class (MacroElement) must be properly initialized
    - All keyword arguments must be compatible with the parse_options function
    
    Postconditions:
    - The _name attribute is set to "Geocoder"
    - The options attribute contains a dictionary with properly formatted camelCase keys
    - The geocoder control will be displayed with the specified initial configuration

## Side Effects:
    None

