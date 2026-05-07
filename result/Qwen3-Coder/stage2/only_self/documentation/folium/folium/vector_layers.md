# `vector_layers.py`

## `folium.vector_layers.path_options` · *function*

## Summary:
Processes and normalizes vector layer styling options for paths, lines, and shapes.

## Description:
This utility function standardizes path styling parameters for use in Folium's vector layers, converting Python-style parameter names to camelCase and applying sensible defaults for visualization properties. It handles conditional logic for line-specific and radius-specific options while managing color and fill properties appropriately.

## Args:
    line (bool): When True, enables line-specific styling options like smoothFactor and noClip. Defaults to False.
    radius (bool or int/float): When provided, sets the radius property for circular elements. Defaults to False.
    **kwargs: Additional styling parameters that will be processed and converted to camelCase keys.

## Returns:
    dict: A dictionary containing normalized styling options for vector layers with keys such as stroke, color, weight, opacity, fill, fillColor, etc.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - All keyword arguments must be valid styling parameters
    - The radius parameter should be numeric when provided
    
    Postconditions:
    - Returns a dictionary with standardized camelCase keys
    - All styling parameters have appropriate default values
    - Color and fill properties are properly handled according to the logic

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start path_options] --> B{line=True?}
    B -- Yes --> C[Set extra_options with smoothFactor, noClip]
    B -- No --> D[extra_options = {}]
    C --> E{radius != False?}
    D --> E
    E -- Yes --> F[Update extra_options with radius]
    E -- No --> G[Continue]
    F --> G
    G --> H[Pop color with default #3388ff]
    H --> I{fillColor provided?}
    I -- Yes --> J[Set fill=True]
    I -- No --> K[Set fill_color = color]
    J --> L[Pop fill with default False]
    K --> L
    L --> M[Process gradient if provided]
    M --> N[Build default options dict]
    N --> O[Update default with extra_options]
    O --> P[Return result]
```

## Examples:
```python
# Basic usage with default values
options = path_options()
# Returns: {'stroke': True, 'color': '#3388ff', 'weight': 3, ...}

# With line styling enabled
options = path_options(line=True, smoothFactor=2.0)
# Returns: {'stroke': True, 'color': '#3388ff', 'weight': 3, 'smoothFactor': 2.0, 'noClip': False, ...}

# With radius parameter
options = path_options(radius=10, color='red')
# Returns: {'stroke': True, 'color': 'red', 'weight': 3, 'radius': 10, ...}

# With custom fill properties
options = path_options(fillColor='blue', fillOpacity=0.5)
# Returns: {'stroke': True, 'color': '#3388ff', 'weight': 3, 'fill': True, 'fillColor': 'blue', 'fillOpacity': 0.5, ...}
```

## `folium.vector_layers.BaseMultiLocation` · *class*

## Summary:
BaseMultiLocation is an abstract base class that provides common functionality for vector layers containing multiple geographic locations, including location validation, popup and tooltip integration, and bounding box computation.

## Description:
The BaseMultiLocation class serves as a foundation for implementing vector map layers that manage collections of geographic coordinates. It handles validation of location data, integration of interactive elements like popups and tooltips, and provides a standardized interface for calculating bounding boxes around location sets. This class is intended to be subclassed by concrete implementations such as GeoJson, Circle, and other multi-location vector layers in folium's mapping system.

## State:
- locations: list[list[float]] - Validated geographic coordinates in [latitude, longitude] format. Must contain at least one valid coordinate pair.
- popup: Popup or None - Optional interactive popup element associated with the location set. Stored as a child element.
- tooltip: Tooltip or None - Optional interactive tooltip element associated with the location set. Stored as a child element.

## Lifecycle:
Creation: Instantiate with a locations parameter containing geographic coordinates, and optional popup and tooltip elements. The constructor validates locations using validate_locations() and processes popup/tooltip arguments by converting strings to Popup/Tooltip objects if needed.
Usage: Typically used as a base class for other vector layer implementations. The _get_self_bounds() method is called to compute bounding boxes for map view calculations.
Destruction: Managed automatically by folium's element hierarchy system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[BaseMultiLocation.__init__] --> B[super().__init__()]
    B --> C[validate_locations(locations)]
    C --> D{popup is not None?}
    D -->|Yes| E[Popup(str(popup)) or popup]
    E --> F[add_child(popup)]
    D -->|No| G[Skip popup processing]
    G --> H{tooltip is not None?}
    H -->|Yes| I[Tooltip(str(tooltip)) or tooltip]
    I --> J[add_child(tooltip)]
    H -->|No| K[End init]
    F --> K
    J --> K
    K --> L[_get_self_bounds]
    L --> M[get_bounds(self.locations)]
```

## Raises:
- TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data
- TypeError: Raised by validate_locations() when coordinate data cannot be properly indexed

## Example:
```python
# Create a BaseMultiLocation with multiple coordinates
locations = [[40.7128, -74.0060], [37.7749, 122.4194], [34.0522, -118.2437]]

# Create with popup and tooltip
popup = Popup('New York City')
tooltip = Tooltip('Major US Cities')
layer = BaseMultiLocation(locations, popup=popup, tooltip=tooltip)

# Get bounding box
bounds = layer._get_self_bounds()
print(bounds)  # [[34.0522, -118.2437], [40.7128, -74.006]]
```

### `folium.vector_layers.BaseMultiLocation.__init__` · *method*

## Summary:
Initializes a BaseMultiLocation instance with geographic coordinates and optional interactive elements.

## Description:
Configures a BaseMultiLocation object by validating geographic location data and setting up optional popup and tooltip elements. This method serves as the constructor for vector layers that manage multiple geographic coordinates, handling data validation and element setup for interactive map features.

## Args:
    locations (list): A collection of geographic coordinates to be validated and stored. May contain nested structures of coordinate pairs.
    popup (Popup or str, optional): Interactive popup element or string to display when interacting with the location set. Defaults to None.
    tooltip (Tooltip or str, optional): Interactive tooltip element or string to display when hovering over the location set. Defaults to None.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs.
    ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data.
    TypeError: Raised by validate_locations() when coordinate data cannot be properly indexed.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.locations: Set to the validated location data returned by validate_locations()
        - self.popup: Set to the processed popup element (converted from string if needed)
        - self.tooltip: Set to the processed tooltip element (converted from string if needed)

## Constraints:
    Preconditions:
        - locations must be an iterable structure containing valid geographic coordinate data
        - popup, if provided, must be either a Popup instance or convertible to one via str()
        - tooltip, if provided, must be either a Tooltip instance or convertible to one via str()
    Postconditions:
        - self.locations contains validated coordinate data in list format
        - self.popup is either None or a Popup instance
        - self.tooltip is either None or a Tooltip instance

## Side Effects:
    - Calls validate_locations() to process and validate the input locations
    - May instantiate Popup or Tooltip objects if strings are provided
    - Adds popup and tooltip as child elements to the instance using add_child()

### `folium.vector_layers.BaseMultiLocation._get_self_bounds` · *method*

## Summary:
Computes and returns the bounding box coordinates for the geographic locations stored in this vector layer.

## Description:
This method calculates the minimum and maximum latitude/longitude coordinates that encompass all geographic locations in the vector layer. It serves as a utility for determining spatial boundaries for map view calculations or visualization purposes. The method is typically called during map rendering or when calculating the extent of vector layers.

## Args:
    None

## Returns:
    list[list[float]]: A bounding box represented as [[min_lat, min_lng], [max_lat, max_lng]]. Returns [[None, None], [None, None]] when no valid coordinates are found.

## Raises:
    KeyError: If expected keys like "features", "geometry", "coordinates" are missing from dictionary objects during coordinate extraction.
    TypeError: If input object is not a supported type or contains incompatible data structures during coordinate processing.
    IndexError: When _locations_mirror is called on empty iterables.
    TypeError: When coordinate values are not comparable during min/max operations.

## State Changes:
    Attributes READ: self.locations
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The self.locations attribute must contain valid geographic coordinate data
    - Coordinate values must be numeric (float or int) for proper bounding box calculation
    
    Postconditions:
    - Method returns a list of two coordinate pairs representing the bounding box
    - All coordinate values are numeric or None when no valid coordinates exist

## Side Effects:
    None

## `folium.vector_layers.PolyLine` · *class*

## Summary:
PolyLine is a vector layer class that renders multi-segment lines on interactive maps using Leaflet.js, designed for displaying geographic routes, paths, or linear features.

## Description:
The PolyLine class implements a vector layer for rendering connected line segments on folium maps. It inherits from BaseMultiLocation, which provides common functionality for handling multiple geographic coordinates, and integrates with folium's interactive elements like popups and tooltips. This class specifically creates polyline visualizations that can represent routes, boundaries, or any linear geographic feature on interactive maps.

The class is typically instantiated by users or through factory methods when creating map overlays that require line-based visualizations. It leverages the path_options utility function to process styling parameters and follows folium's standard pattern for rendering vector layers via JavaScript templates that are compatible with Leaflet.js.

## State:
- locations: list[list[float]] - Validated geographic coordinates in [latitude, longitude] format. Must contain at least one valid coordinate pair, inherited from BaseMultiLocation.
- popup: Popup or None - Optional interactive popup element associated with the line, inherited from BaseMultiLocation.
- tooltip: Tooltip or None - Optional interactive tooltip element associated with the line, inherited from BaseMultiLocation.
- _name: str - Class identifier set to "PolyLine", indicating this is a polyline layer.
- options: dict - Normalized styling options for the polyline, processed by path_options() with line=True flag, containing properties like stroke, color, weight, opacity, smoothFactor, noClip, etc.

## Lifecycle:
Creation: Instantiate with a locations parameter containing geographic coordinates, and optional popup and tooltip elements. The constructor validates locations using validate_locations() and processes styling parameters through path_options() with line=True flag.
Usage: Once created, the PolyLine instance becomes part of a folium map's element hierarchy and is rendered when the map is displayed through Leaflet.js JavaScript rendering.
Destruction: Managed automatically by folium's element hierarchy system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[PolyLine.__init__] --> B[super().__init__(locations, popup, tooltip)]
    B --> C[Set _name = "PolyLine"]
    C --> D[Set options = path_options(line=True, **kwargs)]
    D --> E[End initialization]
```

## Raises:
- TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data
- TypeError: Raised by validate_locations() when coordinate data cannot be properly indexed

## Example:
```python
import folium

# Create a simple polyline between two cities
locations = [[40.7128, -74.0060], [34.0522, -118.2437]]  # New York to Los Angeles
polyline = folium.PolyLine(locations, color='red', weight=3)

# Add to map
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
m.add_child(polyline)

# Create a polyline with popup and tooltip
locations = [[40.7128, -74.0060], [37.7749, 122.4194], [34.0522, -118.2437]]
popup = folium.Popup('Major US Cities')
tooltip = folium.Tooltip('Route between cities')
polyline = folium.PolyLine(locations, popup=popup, tooltip=tooltip, color='blue')

# Add to map
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
m.add_child(polyline)

# Create a complex polyline with advanced styling
locations = [[0, 0], [1, 1], [2, 2], [3, 3]]
polyline = folium.PolyLine(
    locations,
    color='green',
    weight=5,
    opacity=0.7,
    smooth_factor=1.0,
    no_clip=True
)
```

### `folium.vector_layers.PolyLine.__init__` · *method*

## Summary:
Initializes a PolyLine vector layer with geographic coordinates and styling options.

## Description:
Constructs a PolyLine instance that renders multi-segment lines on interactive maps. This method sets up the basic configuration including location data validation, interactive elements (popup and tooltip), and styling parameters for the polyline visualization.

The method calls the parent class constructor to handle location validation and interactive element setup, then configures the polyline-specific attributes including the layer name and styling options.

## Args:
    locations (list[list[float]]): List of [latitude, longitude] coordinate pairs defining the polyline path. Must contain at least one valid coordinate pair.
    popup (Popup or None, optional): Interactive popup element to display when clicking on the polyline. Defaults to None.
    tooltip (Tooltip or None, optional): Interactive tooltip element to display when hovering over the polyline. Defaults to None.
    **kwargs: Additional styling parameters for the polyline including color, weight, opacity, smoothFactor, noClip, etc.

## Returns:
    None: This method initializes the object state and does not return a value.

## Raises:
    TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs
    ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data
    TypeError: Raised by validate_locations() when coordinate data cannot be properly indexed

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "PolyLine" to identify this as a polyline layer
    - self.options: Set to processed styling options from path_options() with line=True flag

## Constraints:
    Preconditions:
    - locations must be a valid iterable containing coordinate pairs in [latitude, longitude] format
    - Each coordinate pair must be valid numeric values
    - popup and tooltip must be instances of their respective folium classes or None
    - All kwargs must be valid styling parameters for vector layers
    
    Postconditions:
    - self._name is set to "PolyLine"
    - self.options contains normalized styling parameters for the polyline
    - The object is ready for integration into a folium map

## Side Effects:
    None.

## `folium.vector_layers.Polygon` · *class*

*No documentation generated.*

## `folium.vector_layers.Rectangle` · *class*

## Summary:
Rectangle represents a rectangular geographic area on a map, implemented as a vector layer that renders a polygon with four corners defined by bounding coordinates.

## Description:
The Rectangle class creates a rectangular shape on a map using bounding coordinates. It inherits from BaseMultiLocation, which provides common functionality for vector layers with multiple geographic locations, including location validation, popup and tooltip integration, and bounding box computation. This class specifically implements a rectangle by defining its boundaries using two corner coordinates (minimum and maximum latitude/longitude values).

The Rectangle class is typically instantiated when users want to draw a rectangular region on a map with customizable styling options. It's commonly used for highlighting areas of interest, defining regions, or creating overlays with rectangular boundaries.

## State:
- bounds: list[list[float]] - Geographic bounding coordinates in [latitude, longitude] format, typically represented as [[min_lat, min_lon], [max_lat, max_lon]]. This is inherited from BaseMultiLocation.
- popup: Popup or None - Optional interactive popup element associated with the rectangle. Inherited from BaseMultiLocation.
- tooltip: Tooltip or None - Optional interactive tooltip element associated with the rectangle. Inherited from BaseMultiLocation.
- _name: str - Fixed value "rectangle" identifying this layer type.
- options: dict - Normalized styling options for the rectangle, processed by path_options() with line=True flag.

## Lifecycle:
Creation: Instantiate with bounds parameter containing geographic coordinates, and optional popup and tooltip elements. The constructor validates bounds using BaseMultiLocation's validation and processes styling options through path_options().
Usage: Typically used as part of a folium.Map object. The rectangle is rendered when the map is displayed, with automatic handling of bounds calculation and rendering through the parent class mechanisms.
Destruction: Managed automatically by folium's element hierarchy system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[Rectangle.__init__] --> B[super().__init__(bounds, popup=popup, tooltip=tooltip)]
    B --> C[Set _name = "rectangle"]
    C --> D[Set options = path_options(line=True, **kwargs)]
    D --> E[End]
```

## Raises:
- TypeError: Raised by validate_locations() when bounds is not an iterable with coordinate pairs
- ValueError: Raised by validate_locations() when bounds is empty or contains invalid coordinate data
- TypeError: Raised by validate_locations() when coordinate data cannot be properly indexed

## Example:
```python
import folium

# Create a map
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Create a rectangle with bounding coordinates
bounds = [[40.70, -74.02], [40.72, -74.00]]
rectangle = folium.Rectangle(
    bounds=bounds,
    popup="Central Park",
    tooltip="New York City",
    color='red',
    weight=2,
    fill=True,
    fillColor='blue',
    fillOpacity=0.5
)

# Add rectangle to map
m.add_child(rectangle)

# Display the map
m
```

### `folium.vector_layers.Rectangle.__init__` · *method*

## Summary:
Initializes a rectangular geographic area with specified bounds, popup, tooltip, and styling options.

## Description:
Configures a Rectangle vector layer by setting its geographic boundaries, interactive elements, and visual styling properties. This method establishes the core state of the rectangle including its name identifier, bounding coordinates, and rendering options.

The Rectangle class is typically instantiated when users want to draw a rectangular region on a map with customizable styling. The initialization process validates the bounding coordinates through the parent class and processes styling options through the path_options utility function.

## Args:
    bounds (list[list[float]]): Geographic bounding coordinates in [latitude, longitude] format, typically represented as [[min_lat, min_lon], [max_lat, max_lon]].
    popup (Popup or str, optional): Interactive popup element or string to display when clicking the rectangle. Defaults to None.
    tooltip (Tooltip or str, optional): Interactive tooltip element or string to display when hovering over the rectangle. Defaults to None.
    **kwargs: Additional styling parameters that will be processed by path_options() to configure line appearance, colors, and fill properties.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: Raised by validate_locations() when bounds is not an iterable with coordinate pairs
    ValueError: Raised by validate_locations() when bounds is empty or contains invalid coordinate data
    TypeError: Raised by validate_locations() when coordinate data cannot be properly indexed

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "rectangle" to identify this layer type
    - self.options: Set to processed styling options from path_options()

## Constraints:
    Preconditions:
    - bounds must be a valid iterable containing exactly two coordinate pairs [lat, lon]
    - Each coordinate pair must contain valid numeric latitude (-90 to 90) and longitude (-180 to 180) values
    - popup and tooltip parameters must be valid Popup/Tooltip objects or convertible strings
    - kwargs must contain valid styling parameter names for path_options()

    Postconditions:
    - self._name is set to "rectangle"
    - self.options contains normalized styling parameters with line=True flag applied
    - The object is ready for rendering on a folium map

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only modifies internal object state.

## `folium.vector_layers.Circle` · *class*

## Summary:
Represents a circular vector layer element that can be added to folium maps for displaying circular regions with customizable styling.

## Description:
The Circle class creates circular visual elements on folium maps at specified geographic coordinates. It extends the Marker base class to provide vector layer functionality for circular shapes, allowing users to define the center location, radius, and various styling properties. This class is typically instantiated when creating circular overlays on maps for visualization purposes.

## State:
- location: list[float] or None - Geographic coordinates [latitude, longitude] for the circle center, validated by validate_location()
- options: dict - Normalized styling options for the circle including stroke, color, weight, radius, fill properties, processed by path_options()
- _name: str - Class identifier set to "circle" for internal tracking and map rendering
- popup: Popup instance or None - Interactive popup information associated with the circle
- tooltip: Tooltip instance or None - Interactive tooltip information associated with the circle

## Lifecycle:
Creation: Instantiate with optional location, radius, popup, tooltip, and additional styling parameters. Location must be a valid coordinate pair or None. The constructor validates location and processes styling options through path_options().
Usage: Circles are typically added to maps using the add_child() method or similar attachment mechanisms. The render() method integrates the circle with the map's JavaScript rendering system.
Destruction: Managed automatically by folium's rendering system when the map is disposed.

## Method Map:
```mermaid
graph TD
    A[Circle.__init__] --> B[super().__init__ with location, popup, tooltip]
    B --> C[Set _name = "circle"]
    C --> D[path_options(line=False, radius=radius, **kwargs)]
    D --> E[Set self.options = result]
```

## Raises:
- ValueError: When render() is called and location is None, inherited from Marker parent class
- TypeError: When radius parameter is not numeric (implicitly through path_options validation)

## Example:
```python
# Create a basic circle at a location with default radius
circle = Circle([40.7128, -74.0060])

# Create a circle with custom radius and styling
circle = Circle([40.7128, -74.0060], radius=1000, color='red', fill=True, fillOpacity=0.5)

# Create a circle with popup and tooltip
from folium.map import Popup, Tooltip
popup = Popup('Circle Area')
tooltip = Tooltip('Circular Region')
circle = Circle([40.7128, -74.0060], radius=500, popup=popup, tooltip=tooltip)
```

## `folium.vector_layers.CircleMarker` · *class*

*No documentation generated.*

### `folium.vector_layers.CircleMarker.__init__` · *method*

## Summary:
Initializes a CircleMarker vector layer with specified location, radius, and optional popup/tooltip.

## Description:
Creates a circular marker element that can be added to folium maps. This method sets up the basic configuration including position, visual styling, and interactive elements. The CircleMarker inherits from Marker and extends it with vector layer capabilities for circular shapes.

## Args:
    location (list[float] or None): Geographic coordinates [latitude, longitude] for the marker center. Defaults to None.
    radius (int or float): Radius of the circle in pixels. Defaults to 10.
    popup (Popup or None): Popup element to display on marker click. Defaults to None.
    tooltip (Tooltip or None): Tooltip element to display on marker hover. Defaults to None.
    **kwargs: Additional styling parameters passed to path_options for vector layer customization.

## Returns:
    None: This method initializes the object state and does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "CircleMarker" string
    - self.options: Set to dictionary of normalized styling options from path_options

## Constraints:
    Preconditions:
    - location, if provided, must be a valid coordinate pair
    - radius must be numeric when provided
    - All kwargs must be valid styling parameters for vector layers
    
    Postconditions:
    - self._name is set to "CircleMarker"
    - self.options contains normalized styling parameters with proper camelCase keys
    - The object is ready for rendering as a vector layer

## Side Effects:
    None.

