# `geocoder.py`

## `folium.plugins.geocoder.Geocoder` · *class*

## Summary:
A geocoding control element that integrates Leaflet Control Geocoder functionality into folium maps.

## Description:
The Geocoder class implements a geocoding control that allows users to search for locations on a map using the Leaflet Control Geocoder library. It provides a user interface element that can be added to folium maps to enable address lookup and location marking capabilities. This class inherits from JSCSSMixin and MacroElement, making it compatible with folium's rendering system and automatically managing JavaScript/CSS dependencies.

## State:
- _name (str): Set to "Geocoder" to identify the element type in folium's element hierarchy
- options (dict): Dictionary of configuration options processed through parse_options, including:
  - collapsed (bool): Whether the geocoder control is initially collapsed
  - position (str): Position of the control on the map (default: "topright")
  - defaultMarkGeocode (bool): Whether to automatically mark geocoded locations on the map
- default_js (list): Class attribute containing URL references to the Leaflet Control Geocoder JavaScript library
- default_css (list): Class attribute containing URL references to the Leaflet Control Geocoder CSS styles

## Lifecycle:
- Creation: Instantiate with optional parameters for control appearance and behavior
- Usage: Add to a folium Figure using add_child() method; rendering automatically handles JS/CSS inclusion
- Destruction: Managed by folium's element lifecycle; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[Geocoder.__init__] --> B[super().__init__()]
    B --> C[self._name = "Geocoder"]
    C --> D[self.options = parse_options(...)]
    D --> E[Inherits JSCSSMixin.render()]
    E --> F[Automatically includes JS/CSS resources]
```

## Raises:
- None explicitly raised by __init__
- Inherited from JSCSSMixin: AssertionError when rendered outside of a Figure context

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

# The geocoder control will appear in the specified position
# and automatically mark locations when searched
```

### `folium.plugins.geocoder.Geocoder.__init__` · *method*

## Summary:
Initializes a geocoding control element with configurable display and behavior options.

## Description:
Configures the geocoding control by setting its identification name and processing display options for integration with Leaflet Control Geocoder. This method establishes the basic configuration state required for the geocoder to function within folium maps, including control positioning, visibility state, and marker behavior.

## Args:
    collapsed (bool): Whether the geocoder control is initially collapsed. Defaults to False.
    position (str): Position of the control on the map. Defaults to "topright".
    add_marker (bool): Whether to automatically mark geocoded locations on the map. Defaults to True.
    **kwargs: Additional keyword arguments passed to parse_options for further configuration.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Geocoder" to identify the element type
    - self.options: Set to the processed dictionary of configuration options

## Constraints:
    Preconditions:
        - The method must be called on an instance of the Geocoder class
        - All keyword arguments must be valid for the parse_options function
    Postconditions:
        - The object's _name attribute is set to "Geocoder"
        - The object's options attribute contains properly formatted configuration options

## Side Effects:
    None: This method performs no I/O operations or external service calls.

