# `measure_control.py`

## `folium.plugins.measure_control.MeasureControl` · *class*

## Summary:
MeasureControl is a folium plugin that adds interactive measurement capabilities to Leaflet maps, allowing users to measure distances and areas directly on the map interface.

## Description:
MeasureControl provides an interface for measuring distances and areas on interactive maps by integrating the leaflet-measure library. It inherits from JSCSSMixin and MacroElement to ensure proper JavaScript and CSS dependencies are loaded when the map is rendered. This class serves as a bridge between folium's Python API and the leaflet-measure JavaScript library, enabling users to perform measurements without writing custom JavaScript code.

## State:
- _name (str): Set to "MeasureControl" to identify the element type in the rendering pipeline
- options (dict): Configuration options for the measurement control, processed through parse_options to convert snake_case to camelCase keys
- default_js (list): Class attribute containing the URL to the leaflet-measure JavaScript library
- default_css (list): Class attribute containing the URL to the leaflet-measure CSS stylesheet

## Lifecycle:
- Creation: Instantiate with optional configuration parameters for positioning and unit settings
- Usage: Add to a folium.Map instance using the add_child() method; rendering automatically handles JS/CSS inclusion
- Destruction: Managed by folium's map rendering system; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[MeasureControl.__init__] --> B[super().__init__()]
    B --> C[self._name = "MeasureControl"]
    C --> D[self.options = parse_options(...)]
    D --> E[Return initialized object]
    
    F[Map.add_child] --> G[MeasureControl.render()]
    G --> H[JSCSSMixin.render()]
    H --> I[Figure.header.add_child]
    I --> J[JavascriptLink]
    I --> K[CssLink]
    J --> L[super().render()]
    K --> L
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if the element is not properly contained within a Figure

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Add measurement control
measure = folium.plugins.MeasureControl(
    position='topright',
    primary_length_unit='kilometers',
    secondary_length_unit='miles'
)
m.add_child(measure)

# The map now includes an interactive measurement tool in the top-right corner
```

### `folium.plugins.measure_control.MeasureControl.__init__` · *method*

## Summary:
Initializes a MeasureControl instance with configurable units and positioning options for measuring distances and areas on a map.

## Description:
Configures the measurement control plugin by setting up its display position and unit preferences for length and area measurements. This method establishes the core configuration options that determine how the measurement tool appears and functions on the map interface.

## Args:
    position (str): Map position for control display, defaults to "topright"
    primary_length_unit (str): Primary unit for length measurements, defaults to "meters"
    secondary_length_unit (str): Secondary unit for length measurements, defaults to "miles"
    primary_area_unit (str): Primary unit for area measurements, defaults to "sqmeters"
    secondary_area_unit (str): Secondary unit for area measurements, defaults to "acres"
    **kwargs: Additional options passed to the parent class initialization

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MeasureControl"
    - self.options: Set to parsed options dictionary from parse_options

## Constraints:
    Preconditions: 
    - All string arguments must be valid unit identifiers recognized by the underlying measurement library
    - Position argument must be a valid map control position identifier
    - Arguments should conform to expected naming conventions for the measurement system

    Postconditions:
    - The instance is properly initialized with default or provided configuration values
    - The _name attribute is set to "MeasureControl" for proper identification
    - Options are stored in a format compatible with JavaScript-based rendering

## Side Effects:
    None

