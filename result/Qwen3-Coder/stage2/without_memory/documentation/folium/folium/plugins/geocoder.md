# `geocoder.py`

## `folium.plugins.geocoder.Geocoder` · *class*

## Summary:
A geocoder plugin for folium maps that integrates Leaflet Control Geocoder functionality.

## Description:
The Geocoder class provides a geocoding control for folium maps, enabling address search capabilities through integration with the Leaflet Control Geocoder library. It inherits from JSCSSMixin and MacroElement to properly manage JavaScript and CSS dependencies for the geocoder functionality. This component adds a searchable geocoding interface to folium maps, allowing users to find locations by address.

## State:
- _name: str, set to "Geocoder" - identifies this component type
- options: dict, configured via parse_options with parameters like collapsed, position, and defaultMarkGeocode
- default_js: list of tuples containing JavaScript library names and URLs for Leaflet Control Geocoder
- default_css: list of tuples containing CSS library names and URLs for Leaflet Control Geocoder
- _template: Jinja2 Template object (empty in provided code, likely defined elsewhere)

## Lifecycle:
- Creation: Instantiate with optional parameters (collapsed=False, position="topright", add_marker=True)
- Usage: Add to a folium.Map instance using add_child() method
- Destruction: Managed automatically by folium's rendering system

## Method Map:
```mermaid
graph TD
    A[Geocoder.__init__] --> B[super().__init__]
    A --> C[parse_options]
    B --> D[JSCSSMixin.__init__]
    C --> E[options dict]
    D --> F[JSCSSMixin.render]
    F --> G[Add JS/CSS links to figure header]
```

## Raises:
- AssertionError: If the component is not properly integrated into a folium Figure during rendering
- AssertionErrors from parse_options if invalid options are provided (though not explicitly shown in current code)

## Example:
```python
import folium
from folium.plugins import Geocoder

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Add geocoder plugin
geocoder = Geocoder(collapsed=False, position="topleft")
m.add_child(geocoder)

# The map now has a geocoder control that allows address searching
```

### `folium.plugins.geocoder.Geocoder.__init__` · *method*

## Summary:
Initializes a geocoder plugin with configurable display options and marker behavior.

## Description:
Configures the geocoder control with display settings and marker placement options. This method sets up the internal state required for rendering the geocoder interface in Leaflet maps.

## Args:
    collapsed (bool): Whether the geocoder control should be collapsed by default. Defaults to False.
    position (str): Position of the geocoder control on the map. Defaults to "topright".
    add_marker (bool): Whether to add a marker when a location is geocoded. Defaults to True.
    **kwargs: Additional keyword arguments passed to the geocoder configuration.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    AssertionError: If any of the provided options are not valid for the geocoder control.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Geocoder"
    - self.options: Set to parsed options dictionary containing collapsed, position, and defaultMarkGeocode settings

## Constraints:
    Preconditions: None
    Postconditions: The object is properly initialized with geocoder-specific options and name set.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

