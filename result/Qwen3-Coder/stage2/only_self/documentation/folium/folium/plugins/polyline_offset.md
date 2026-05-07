# `polyline_offset.py`

## `folium.plugins.polyline_offset.PolyLineOffset` · *class*

## Summary:
PolyLineOffset is a vector layer class that extends PolyLine to support offsetting polylines in Leaflet.js maps, enabling the creation of parallel lines for route visualization or map annotation purposes.

## Description:
The PolyLineOffset class provides enhanced polyline functionality by adding support for offset distances, allowing users to create parallel lines that are offset from the original path. This is particularly useful for visualizing multiple routes, creating road networks, or displaying alternative paths on maps. It inherits from both JSCSSMixin and PolyLine, combining the JavaScript/CSS resource management capabilities with the core polyline rendering functionality.

This class is typically instantiated when creating map overlays that require offset polyline features, often through direct instantiation by users or through factory methods in folium's plugin ecosystem. The offset functionality is implemented through the leaflet-polylineoffset JavaScript library, which is automatically included when the element is rendered.

## State:
- locations: list[list[float]] - Geographic coordinates in [latitude, longitude] format, inherited from PolyLine. Must contain at least one valid coordinate pair.
- popup: Popup or None - Optional interactive popup element, inherited from PolyLine.
- tooltip: Tooltip or None - Optional interactive tooltip element, inherited from PolyLine.
- _name: str - Class identifier set to "PolyLineOffset", distinguishing this from regular PolyLine.
- options: dict - Normalized styling options including offset parameter, inherited from PolyLine. The offset key is updated with the provided offset value.
- offset: int - Distance to offset the polyline from the original path in meters, defaulting to 0. Positive values offset to the right, negative values to the left, relative to the direction of the line.

## Lifecycle:
Creation: Instantiate with locations parameter containing geographic coordinates, optional popup and tooltip elements, and an optional offset parameter. The constructor validates locations using validate_locations() and processes styling parameters through path_options() with line=True flag, then updates options with the offset value. The default JavaScript library (leaflet-polylineoffset) is automatically included during rendering.
Usage: Once created, the PolyLineOffset instance becomes part of a folium map's element hierarchy and is rendered when the map is displayed through Leaflet.js JavaScript rendering, utilizing the leaflet-polylineoffset library.
Destruction: Managed automatically by folium's element hierarchy system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[PolyLineOffset.__init__] --> B[super().__init__(locations, popup, tooltip, **kwargs)]
    B --> C[Set _name = "PolyLineOffset"]
    C --> D[Update options with offset parameter]
    D --> E[End initialization]
```

## Raises:
- TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data
- TypeError: Raised by validate_locations() when coordinate data cannot be properly indexed

## Example:
```python
import folium

# Create a polyline with positive offset
locations = [[40.7128, -74.0060], [37.7749, 122.4194], [34.0522, -118.2437]]
polyline_offset = folium.plugins.PolyLineOffset(
    locations, 
    offset=10,  # Offset by 10 meters to the right
    color='blue',
    weight=3
)

# Add to map
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
m.add_child(polyline_offset)

# Create a polyline with negative offset (on opposite side)
locations = [[40.7128, -74.0060], [34.0522, -118.2437]]
polyline_offset_negative = folium.plugins.PolyLineOffset(
    locations,
    offset=-5,  # Negative offset of 5 meters
    color='red',
    weight=2
)

# Create a polyline with zero offset (default behavior)
locations = [[40.7128, -74.0060], [37.7749, 122.4194]]
polyline_default = folium.plugins.PolyLineOffset(
    locations,
    offset=0,  # No offset
    color='green',
    weight=4
)
```

### `folium.plugins.polyline_offset.PolyLineOffset.__init__` · *method*

## Summary:
Initializes a PolyLineOffset object with geographic coordinates and offset styling options.

## Description:
The constructor creates a polyline visualization with an additional offset parameter that allows for drawing parallel lines to represent route variations or offsets. This method extends the base PolyLine functionality by setting a custom name and adding offset configuration to the rendering options.

## Args:
    locations (list[list[float]]): List of [latitude, longitude] coordinate pairs defining the polyline path.
    popup (Popup or None, optional): Interactive popup element to display when clicking the polyline. Defaults to None.
    tooltip (Tooltip or None, optional): Interactive tooltip element to display on hover. Defaults to None.
    offset (float, optional): Offset distance for the polyline in map units. Defaults to 0.
    **kwargs: Additional styling arguments passed to the parent PolyLine class.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: Raised by parent class validation when locations is not an iterable with coordinate pairs.
    ValueError: Raised by parent class validation when locations is empty or contains invalid coordinate data.
    TypeError: Raised by parent class validation when coordinate data cannot be properly indexed.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "PolyLineOffset" to identify this specific polyline type
    - self.options: Updated with offset parameter and other styling options

## Constraints:
    Preconditions:
    - locations must be a valid iterable containing at least one [latitude, longitude] coordinate pair
    - Each coordinate must be a numeric value representing valid geographic coordinates
    - offset must be a numeric value (int or float)
    
    Postconditions:
    - self._name is set to "PolyLineOffset"
    - self.options dictionary contains the offset parameter
    - Parent class initialization is completed successfully

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only modifies internal object state.

