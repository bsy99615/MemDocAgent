# `measure_control.py`

## `folium.plugins.measure_control.MeasureControl` · *class*

## Summary:
A Folium plugin that adds interactive measurement controls to Leaflet maps, enabling users to measure distances and areas on the map.

## Description:
The MeasureControl class implements a Folium plugin that integrates the leaflet-measure JavaScript library into Folium maps. It allows users to measure distances and areas directly on the map by drawing lines and polygons. This control appears as an overlay button in the specified position on the map and provides a user interface for performing measurements.

This class is designed to be instantiated and added to a Folium Figure object, where it automatically handles the inclusion of required JavaScript and CSS resources from the leaflet-measure library.

## State:
- _name: str, set to "MeasureControl" - identifies the element type in the rendering system
- options: dict, contains processed configuration options for the measurement control including:
  - position: str, determines where the control appears on the map (default: "topright")
  - primary_length_unit: str, primary unit for length measurements (default: "meters")
  - secondary_length_unit: str, secondary unit for length measurements (default: "miles")
  - primary_area_unit: str, primary unit for area measurements (default: "sqmeters")
  - secondary_area_unit: str, secondary unit for area measurements (default: "acres")

## Lifecycle:
- Creation: Instantiate with optional configuration parameters to customize measurement units and control position
- Usage: Add to a Folium Figure using add_child() method; rendering automatically includes required JS/CSS resources
- Destruction: No explicit cleanup required; relies on parent Element's lifecycle management

## Method Map:
```mermaid
graph TD
    A[MeasureControl.__init__] --> B[super().__init__()]
    B --> C[self._name = "MeasureControl"]
    C --> D[self.options = parse_options(...)]
    D --> E[Inherits JSCSSMixin.render()]
    E --> F[Automatically loads leaflet-measure JS/CSS]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if not properly contained within a Figure context

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add measurement control with custom settings
measure_control = folium.plugins.MeasureControl(
    position='topleft',
    primary_length_unit='kilometers',
    secondary_length_unit='miles',
    primary_area_unit='sqkm',
    secondary_area_unit='acres'
)

# Add the control to the map
m.add_child(measure_control)

# The map now displays a measurement control button that allows users to measure distances and areas
```

### `folium.plugins.measure_control.MeasureControl.__init__` · *method*

## Summary:
Initializes a MeasureControl instance with configurable measurement units and display position for interactive map measurements.

## Description:
Configures the measurement control with customizable units for length and area measurements, along with positioning options. This method sets up the internal state required for rendering the leaflet-measure control in Folium maps, establishing the control's appearance and behavior.

The method inherits from the JSCSSMixin and MacroElement base classes, ensuring proper integration with Folium's rendering system and automatic inclusion of required JavaScript/CSS resources.

## Args:
    position (str): Position of the control on the map. Defaults to "topright". Valid values are typically "topleft", "topright", "bottomleft", "bottomright".
    primary_length_unit (str): Primary unit for length measurements. Defaults to "meters". Common values include "meters", "kilometers", "feet", "yards".
    secondary_length_unit (str): Secondary unit for length measurements. Defaults to "miles". Common values include "miles", "kilometers", "yards", "feet".
    primary_area_unit (str): Primary unit for area measurements. Defaults to "sqmeters". Common values include "sqmeters", "sqkm", "sqfeet", "sqyards".
    secondary_area_unit (str): Secondary unit for area measurements. Defaults to "acres". Common values include "acres", "hectares", "sqkm", "sqmeters".
    **kwargs: Additional keyword arguments passed to the parent class initialization for extended configuration.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MeasureControl" to identify the element type in the rendering system
    - self.options: Set to the parsed options dictionary containing all configuration parameters in camelCase format for compatibility with the leaflet-measure JavaScript library

## Constraints:
    Preconditions:
    - The object must be properly initialized as a subclass of JSCSSMixin and MacroElement
    - All string parameters should be valid unit identifiers recognized by the underlying leaflet-measure library
    Postconditions:
    - self._name is set to "MeasureControl" 
    - self.options contains all provided configuration parameters in camelCase format
    - The instance is ready for rendering within a Folium Figure context

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state for later rendering.

