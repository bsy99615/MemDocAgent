# `measure_control.py`

## `folium.plugins.measure_control.MeasureControl` · *class*

## Summary:
A folium plugin that adds interactive measurement controls to maps using the leaflet-measure JavaScript library.

## Description:
The MeasureControl class provides measurement capabilities for folium maps by integrating the leaflet-measure JavaScript plugin. It allows users to measure distances and areas directly on the map. This class inherits from JSCSSMixin and MacroElement, making it compatible with folium's rendering system and enabling automatic inclusion of required JavaScript and CSS resources.

This control is typically used when creating interactive maps that require users to measure geographic distances or areas. It provides a user-friendly interface for measuring tools that appear as overlays on the map.

## State:
- _name: str, set to "MeasureControl" - identifies the element type in folium's rendering system
- options: dict, contains configuration options for the measurement control including:
  - position: str, default "topright" - placement of the control on the map
  - primary_length_unit: str, default "meters" - primary unit for length measurements
  - secondary_length_unit: str, default "miles" - secondary unit for length measurements  
  - primary_area_unit: str, default "sqmeters" - primary unit for area measurements
  - secondary_area_unit: str, default "acres" - secondary unit for area measurements
- default_js: list of tuples, specifies the leaflet-measure JavaScript library URL to include
- default_css: list of tuples, specifies the leaflet-measure CSS stylesheet URL to include

## Lifecycle:
- Creation: Instantiate with optional configuration parameters to customize measurement units and control positioning
- Usage: Add to a folium.Map instance using the add_child() method or similar mechanism
- Destruction: Automatically cleaned up when the map is destroyed or the element is removed from the map

## Method Map:
```mermaid
graph TD
    A[MeasureControl.__init__] --> B[super().__init__]
    B --> C[JSCSSMixin.__init__]
    C --> D[MacroElement.__init__]
    D --> E[Set _name="MeasureControl"]
    E --> F[parse_options]
    F --> G[options dict populated]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if not properly contained in a Figure context

## Example:
```python
import folium
from folium.plugins import MeasureControl

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add measure control with custom settings
measure = MeasureControl(
    position='topleft',
    primary_length_unit='kilometers',
    secondary_length_unit='miles',
    primary_area_unit='sqkm',
    secondary_area_unit='acres'
)

# Add the measure control to the map
m.add_child(measure)

# The map now includes an interactive measurement tool in the top left corner
```

### `folium.plugins.measure_control.MeasureControl.__init__` · *method*

## Summary:
Initializes a MeasureControl instance with configurable measurement units and positioning options.

## Description:
Configures the measurement control by setting up its name, position, and unit preferences for distance and area measurements. This method establishes the core configuration that determines how the measurement control appears on the map and what units it displays measurements in.

The initialization process involves calling the parent class constructors to establish the proper inheritance chain, setting the element name to "MeasureControl" for identification within folium's rendering system, and processing all provided configuration options through the parse_options utility function to convert them to the appropriate format for the underlying JavaScript library.

## Args:
    position (str): Map position for control placement, defaults to "topright"
    primary_length_unit (str): Primary unit for length measurements, defaults to "meters"
    secondary_length_unit (str): Secondary unit for length measurements, defaults to "miles"
    primary_area_unit (str): Primary unit for area measurements, defaults to "sqmeters"
    secondary_area_unit (str): Secondary unit for area measurements, defaults to "acres"
    **kwargs: Additional configuration options passed to the JavaScript library

## Returns:
    None: This method initializes the object's state but does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MeasureControl" 
    - self.options: Populated with processed configuration options

## Constraints:
    Preconditions:
    - The object must be properly instantiated as part of the folium plugin hierarchy
    - All provided string arguments must be valid unit identifiers recognized by the JavaScript library
    - The parent classes (JSCSSMixin, MacroElement) must be properly initialized
    
    Postconditions:
    - The object's _name attribute is set to "MeasureControl"
    - The options dictionary contains all provided configuration parameters in camelCase format
    - The object is ready for rendering within a folium Figure context

## Side Effects:
    None: This method performs no I/O operations or external service calls

