# `polyline_text_path.py`

## `folium.plugins.polyline_text_path.PolyLineTextPath` · *class*

## Summary:
A Folium plugin that renders text along a polyline on a Leaflet map using the leaflet-textpath JavaScript library.

## Description:
The PolyLineTextPath class is a specialized map element that enables text to be displayed along the path of a polyline on a Leaflet-powered map. It leverages the leaflet-textpath JavaScript library to achieve this effect, allowing developers to annotate polylines with text labels that follow the curve of the line. This component is particularly useful for creating route annotations, labeling paths, or adding descriptive text along geographic features.

This class is intended to be instantiated by developers who want to add text annotations along existing polylines in their Folium maps. It follows the standard Folium pattern of inheriting from MacroElement and JSCSSMixin to handle map rendering and JavaScript/CSS resource management.

## State:
- _name (str): Set to "PolyLineTextPath" to identify the element type in the map rendering system
- polyline: Reference to the polyline object that the text will follow
- text (str): The text string to be displayed along the polyline
- options (dict): Processed configuration options for text positioning and appearance, converted from snake_case to camelCase using parse_options

## Lifecycle:
- Creation: Instantiate with a polyline object, text string, and optional configuration parameters
- Usage: Add to a Folium map using the add_child() method or similar container mechanisms
- Destruction: Managed automatically by the Folium rendering system when the map is disposed

## Method Map:
```mermaid
graph TD
    A[PolyLineTextPath.__init__] --> B[super().__init__]
    B --> C[set _name]
    C --> D[set polyline]
    D --> E[set text]
    E --> F[parse_options]
    F --> G[return]
```

## Raises:
- None explicitly raised by __init__, though underlying parent class constructors may raise exceptions if improperly used outside of a Folium Figure context

## Example:
```python
import folium
from folium.plugins import PolyLineTextPath

# Create a map
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Create a polyline
polyline = folium.PolyLine(
    locations=[[40.7128, -74.0060], [40.7589, -73.9851]],
    color='blue'
)

# Add text along the polyline
text_path = PolyLineTextPath(
    polyline=polyline,
    text='Route Name',
    repeat=True,
    offset=10
)

# Add both to the map
m.add_child(polyline)
m.add_child(text_path)

# Display the map
m
```

### `folium.plugins.polyline_text_path.PolyLineTextPath.__init__` · *method*

## Summary:
Initializes a PolyLineTextPath object that renders text along a polyline on a Leaflet map.

## Description:
Configures a PolyLineTextPath instance by setting up the element name, storing references to the polyline and text content, and processing configuration options for text positioning and appearance. This method establishes the foundational state required for rendering text along a polyline using the leaflet-textpath JavaScript library.

The method inherits from MacroElement and JSCSSMixin to integrate properly with Folium's map rendering system and automatically include required JavaScript/CSS resources. It processes all configuration parameters through the parse_options utility to ensure proper camelCase formatting for JavaScript compatibility.

## Args:
    polyline (object): Reference to the polyline object that the text will follow. This should be a valid folium polyline element.
    text (str): The text string to be displayed along the polyline. Must be a valid string.
    repeat (bool): Whether to repeat the text along the entire length of the polyline. Defaults to False.
    center (bool): Whether to center the text along the polyline. Defaults to False.
    below (bool): Whether to place the text below the polyline. Defaults to False.
    offset (int): Vertical offset in pixels for text positioning. Defaults to 0.
    orientation (int): Rotation angle in degrees for text orientation. Defaults to 0.
    attributes (dict): Additional HTML attributes to apply to the text element. Defaults to None.
    **kwargs: Additional keyword arguments passed to the parse_options utility for further configuration.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying parent class constructors may raise exceptions if improperly used outside of a Folium Figure context.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN:
        - self._name: Set to "PolyLineTextPath" to identify the element type in the map rendering system
        - self.polyline: Set to the provided polyline parameter value
        - self.text: Set to the provided text parameter value
        - self.options: Set to the processed dictionary of configuration options from parse_options

## Constraints:
    Preconditions:
        - The polyline parameter must be a valid folium polyline element
        - The text parameter must be a string
        - All keyword arguments must be compatible with the parse_options utility
    Postconditions:
        - The object is properly initialized with all required attributes
        - The _name attribute is set to "PolyLineTextPath"
        - The polyline and text attributes are assigned the provided values
        - The options dictionary contains properly formatted camelCase keys with non-None values

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes and calls parent constructors.

