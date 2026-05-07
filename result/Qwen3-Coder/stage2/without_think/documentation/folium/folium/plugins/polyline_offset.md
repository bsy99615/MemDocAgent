# `polyline_offset.py`

## `folium.plugins.polyline_offset.PolyLineOffset` · *class*

## Summary:
A polyline vector layer that supports offset rendering using the leaflet-polylineoffset JavaScript library.

## Description:
The PolyLineOffset class extends the standard PolyLine functionality by adding support for offset rendering of polylines on interactive maps. It leverages the leaflet-polylineoffset JavaScript plugin to enable drawing multiple parallel polylines with configurable offsets, useful for visualizing route variations, traffic patterns, or overlapping paths. This class inherits from both JSCSSMixin and PolyLine, where JSCSSMixin provides JavaScript and CSS resource management for map elements and PolyLine provides core polyline rendering capabilities.

This class is designed as a specialized polyline implementation that provides enhanced visualization capabilities through the offset feature, making it suitable for applications requiring multiple parallel line representations of geographic routes or paths.

## State:
- locations (list): Geographic coordinate data validated through BaseMultiLocation inheritance, containing [latitude, longitude] pairs or nested structures.
- popup (Popup or None): Optional popup element attached to the polyline for additional information display.
- tooltip (Tooltip or None): Optional tooltip element attached to the polyline for hover information.
- _name (str): Set to "PolyLineOffset" for Leaflet.js identification.
- options (dict): Path styling options including the "offset" key which determines the pixel offset distance for parallel line rendering.
- offset (int): Configurable offset value in pixels, defaults to 0. Positive values offset the line to the right, negative values to the left.

## Lifecycle:
- Creation: Instantiate with required locations parameter and optional popup/tooltip. The offset parameter defaults to 0.
- Usage: Automatically integrated into folium map rendering through the standard element system. The JavaScript library is loaded automatically via JSCSSMixin.
- Destruction: Handled automatically through parent class lifecycle management.

## Method Map:
```mermaid
flowchart TD
    A[PolyLineOffset.__init__] --> B[super().__init__]
    B --> C[Set _name = "PolyLineOffset"]
    C --> D[Update options with offset]
    D --> E[Return]
```

## Raises:
- TypeError: Inherited from PolyLine.validate_locations() when locations is not an iterable or contains invalid data types.
- ValueError: Inherited from PolyLine.validate_locations() when locations is empty or contains invalid coordinate data.

## Example:
```python
import folium

# Create a polyline with offset rendering
locations = [[40.7128, -74.0060], [37.7749, 122.4194], [34.0522, -118.2437]]  # NYC to SF to LA

# Create a main polyline (no offset)
main_polyline = folium.plugins.PolyLineOffset(locations, color="blue", weight=5)

# Create an offset polyline (shifted 10 pixels to the right)
offset_polyline = folium.plugins.PolyLineOffset(locations, color="red", weight=3, offset=10)

# Add to a map
m = folium.Map(location=[39.0, -98.0], zoom_start=4)
m.add_child(main_polyline)
m.add_child(offset_polyline)
```

### `folium.plugins.polyline_offset.PolyLineOffset.__init__` · *method*

## Summary:
Initializes a PolyLineOffset object with geographic locations, optional interactive elements, and configurable offset rendering for parallel line visualization.

## Description:
Configures a PolyLineOffset instance by initializing parent classes with geographic coordinates and styling options, setting the element name to "PolyLineOffset", and establishing the offset parameter for parallel line rendering. This constructor extends the standard PolyLine functionality to support offset-based rendering using the leaflet-polylineoffset JavaScript library.

The method is separated from inline logic to maintain clean inheritance and proper initialization of both the JSCSSMixin (for JavaScript/CSS resource management) and PolyLine (for core polyline rendering) parent classes. This design allows the PolyLineOffset to leverage existing functionality while adding the specialized offset feature.

## Args:
    locations (list): List of geographic coordinate pairs [latitude, longitude] defining the polyline path geometry.
    popup (Popup or None, optional): Interactive popup element to display additional information when clicking the polyline. Defaults to None.
    tooltip (Tooltip or None, optional): Interactive tooltip element to display information on hover. Defaults to None.
    offset (int, optional): Pixel offset distance for parallel line rendering. Positive values offset to the right, negative to the left. Defaults to 0.
    **kwargs: Additional styling options passed to the parent PolyLine class for line properties like color, weight, and opacity.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: Raised by parent classes when locations is not an iterable or contains invalid data types.
    ValueError: Raised by parent classes when locations is empty or contains invalid coordinate data.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "PolyLineOffset" for Leaflet.js identification
        - self.options: Updated with the offset parameter in the "offset" key

## Constraints:
    Preconditions:
        - locations must be a valid iterable of geographic coordinate pairs
        - All coordinate values must be within valid latitude (-90 to 90) and longitude (-180 to 180) ranges
        - Parent class validation requirements must be satisfied
    Postconditions:
        - self._name is set to "PolyLineOffset"
        - self.options contains the offset value for parallel line rendering
        - The object is properly initialized with all parent class functionality

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes and calls parent constructors.

