# `polyline_offset.py`

## `folium.plugins.polyline_offset.PolyLineOffset` · *class*

## Summary:
PolyLineOffset is a specialized folium vector layer that renders geographic polylines with configurable offset functionality using the leaflet-polylineoffset JavaScript library.

## Description:
PolyLineOffset extends the standard PolyLine class to add support for offsetting polylines, allowing users to create parallel lines or offset routes for visualization purposes. It inherits from JSCSSMixin and PolyLine, enabling automatic JavaScript/CSS dependency management through JSCSSMixin and polyline rendering capabilities through PolyLine. This class is particularly useful for creating route networks, parallel paths, or visualizing directional offsets in geographic data visualization.

## State:
- locations (list[list[float]]): Geographic coordinate pairs stored as [latitude, longitude] lists, validated through inherited BaseMultiLocation functionality
- _name (str): Set to "PolyLineOffset" to identify this element type in Folium's rendering system
- options (dict): Configuration dictionary containing styling options and the offset parameter, updated with {"offset": offset}
- offset (int): Numeric offset value applied to the polyline, defaults to 0 (no offset)

## Lifecycle:
- Creation: Instantiate with required locations parameter and optional popup/tooltip. The constructor calls super().__init__() to initialize parent classes and sets the element name and offset option
- Usage: Used as part of a Folium map by adding it to the map's elements. The rendering system automatically handles JavaScript/CSS dependencies through JSCSSMixin's render() method
- Destruction: Managed automatically through Folium's element lifecycle management system

## Method Map:
```mermaid
graph TD
    A[PolyLineOffset.__init__] --> B[super().__init__(locations, popup=popup, tooltip=tooltip)]
    B --> C[self._name = "PolyLineOffset"]
    C --> D[self.options.update({"offset": offset})]
```

## Raises:
- TypeError: May be raised by validate_locations() inherited from BaseMultiLocation when locations is not an iterable with coordinate pairs
- ValueError: May be raised by validate_locations() inherited from BaseMultiLocation when locations is empty or contains invalid coordinate data

## Example:
```python
import folium

# Create a map centered on a location
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Define locations for a route
locations = [
    [40.7128, -74.0060],  # New York
    [37.7749, 122.4194],  # San Francisco
    [34.0522, -118.2437]  # Los Angeles
]

# Create a polyline with positive offset (shifted right)
offset_polyline = folium.plugins.PolyLineOffset(
    locations,
    offset=10,  # Offset in meters
    popup="Offset Route",
    tooltip="Route with offset",
    color="red",
    weight=5
)

# Add the polyline to the map
m.add_child(offset_polyline)

# Display the map
m
```

### `folium.plugins.polyline_offset.PolyLineOffset.__init__` · *method*

## Summary:
Initializes a PolyLineOffset instance with geographic locations, optional interactive elements, and offset configuration for polyline rendering.

## Description:
The __init__ method constructs a PolyLineOffset object by calling the parent PolyLine constructor with location data and optional popup/tooltip elements, then sets the element name to "PolyLineOffset" and configures the offset property for polyline positioning. This method serves as the primary constructor for creating offset-enabled polylines in Folium maps, allowing users to specify horizontal displacement of polylines from their original geographic positions.

## Args:
- locations (list[list[float]]): Required list of geographic coordinate pairs [latitude, longitude] defining the polyline path
- popup (Popup, optional): Optional popup element to display information when clicking the polyline
- tooltip (Tooltip, optional): Optional tooltip element to display information on hover
- offset (float, optional): Horizontal offset distance for polyline positioning in pixels. Defaults to 0
- **kwargs: Additional keyword arguments passed to parent PolyLine constructor for styling options

## Returns:
- None: This method initializes the object state but does not return a value

## Raises:
- TypeError: Raised by parent PolyLine.validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: Raised by parent PolyLine.validate_locations() when locations is empty or contains invalid coordinate data
- AssertionError: May be raised by parent PolyLine or inherited classes if invalid arguments are provided

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: 
  - self._name: Set to "PolyLineOffset" to identify this element type in Folium's rendering system
  - self.options: Updated with offset configuration via dict.update() to store the offset parameter

## Constraints:
- Preconditions: 
  - locations must be a valid iterable containing coordinate pairs
  - Each coordinate pair must contain valid latitude (-90 to 90) and longitude (-180 to 180) values
- Postconditions:
  - self._name is set to "PolyLineOffset"
  - self.options contains the offset configuration under the "offset" key

## Side Effects:
- None: This method performs no I/O operations or external service calls

