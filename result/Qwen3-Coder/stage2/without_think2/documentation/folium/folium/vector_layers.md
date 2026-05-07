# `vector_layers.py`

## `folium.vector_layers.path_options` · *function*

## Summary:
Generates a dictionary of styling options for vector path elements in Folium maps, supporting both line and polygon rendering with customizable appearance properties.

## Description:
The `path_options` function processes various styling parameters to create a standardized configuration dictionary for rendering vector paths (lines and polygons) in Folium maps. It handles conversion of snake_case parameter names to camelCase for JavaScript compatibility using the `camelize` utility function, manages conditional styling based on whether the path represents a line or has a radius, and provides sensible defaults for all visual properties. This function centralizes path styling logic to ensure consistent appearance across different map layers while allowing flexible customization through keyword arguments.

## Args:
    line (bool): Flag indicating whether the path should be treated as a line (default: False). When True, additional line-specific options like smoothFactor and noClip are processed.
    radius (bool or float): Radius value for circular path elements (default: False). When provided, this value is added to the extra_options dictionary.
    **kwargs: Additional styling parameters that can include stroke, color, weight, opacity, lineCap, lineJoin, dashArray, dashOffset, fill, fillColor, fillOpacity, fillRule, bubblingMouseEvents, smoothFactor, noClip, and gradient.

## Returns:
    dict: A dictionary containing all processed styling options for vector paths, including:
        - Basic path properties: stroke, color, weight, opacity, lineCap, lineJoin, dashArray, dashOffset
        - Fill properties: fill, fillColor, fillOpacity, fillRule
        - Mouse event handling: bubblingMouseEvents
        - Extra options: smoothFactor, noClip, radius, gradient (when applicable)
        - All keys are in camelCase format for JavaScript compatibility

## Raises:
    None

## Constraints:
    - Precondition: All input parameters must be compatible with their expected types (boolean, numeric, string, etc.)
    - Postcondition: The returned dictionary contains all expected path styling properties with appropriate defaults
    - The function relies on the `camelize` utility function to convert snake_case parameter names to camelCase for JavaScript compatibility

## Side Effects:
    - Modifies the input kwargs dictionary by popping processed keys
    - Uses the `camelize` utility function to transform parameter names

## Control Flow:
```mermaid
flowchart TD
    A[Start path_options] --> B[Camelize kwargs keys]
    B --> C{line=True?}
    C -- Yes --> D[Set extra_options with smoothFactor, noClip]
    C -- No --> E[extra_options = {}]
    D --> F[Process radius parameter]
    E --> F
    F --> G[Extract color with default #3388ff]
    G --> H[Extract fillColor with default False]
    H --> I{fillColor truthy?}
    I -- Yes --> J[Set fill=True]
    I -- No --> K[Set fill_color = color, fill = kwargs.pop(fill, False)]
    J --> L[Process gradient]
    K --> L
    L --> M[Build default dict with basic path properties]
    M --> N[Update default with extra_options]
    N --> O[Return result]
```

## Examples:
    >>> path_options(line=True, color="red", weight=5)
    {'stroke': True, 'color': 'red', 'weight': 5, 'opacity': 1.0, 'lineCap': 'round', 'lineJoin': 'round', 'dashArray': None, 'dashOffset': None, 'fill': False, 'fillColor': 'red', 'fillOpacity': 0.2, 'fillRule': 'evenodd', 'bubblingMouseEvents': True, 'smoothFactor': 1.0, 'noClip': False}

    >>> path_options(radius=10, fillColor="blue")
    {'stroke': True, 'color': '#3388ff', 'weight': 3, 'opacity': 1.0, 'lineCap': 'round', 'lineJoin': 'round', 'dashArray': None, 'dashOffset': None, 'fill': False, 'fillColor': 'blue', 'fillOpacity': 0.2, 'fillRule': 'evenodd', 'bubblingMouseEvents': True, 'radius': 10}
```

## `folium.vector_layers.BaseMultiLocation` · *class*

## Summary:
BaseMultiLocation is an abstract base class for vector layers that manage multiple geographic locations, providing common functionality for location validation, popup and tooltip integration, and bounding box computation.

## Description:
The BaseMultiLocation class serves as a foundation for implementing vector layers that handle collections of geographic coordinates. It extends MacroElement to integrate with Folium's rendering system and provides standardized behavior for validating location data, attaching interactive elements (popups and tooltips), and calculating spatial bounds. This class is designed to be subclassed by concrete implementations like GeoJson, CircleMarker, and other multi-location vector layers.

## State:
- locations (list[list[float]]): Validated geographic coordinate pairs stored as a list of [latitude, longitude] lists. This attribute is initialized through validate_locations() and maintains the original nesting structure of the input.
- _name (str): Inherited from MacroElement, identifies this element type in Folium's rendering system
- _children (dict): Inherited from MacroElement, stores child elements like Popup and Tooltip objects

## Lifecycle:
- Creation: Instantiate with a locations parameter (required) and optional popup/tooltip parameters. The constructor validates locations and processes popup/tooltip arguments.
- Usage: Typically used as a base class for vector layer implementations. The _get_self_bounds() method is called during map rendering to compute the spatial extent.
- Destruction: Managed automatically through Folium's element lifecycle management system

## Method Map:
```mermaid
graph TD
    A[BaseMultiLocation.__init__] --> B[super().__init__()]
    B --> C[self.locations = validate_locations(locations)]
    C --> D{popup is not None?}
    D -- Yes --> E[self.add_child(popup if isinstance(popup, Popup) else Popup(str(popup)))]
    D -- No --> F{tooltip is not None?}
    F -- Yes --> G[self.add_child(tooltip if isinstance(tooltip, Tooltip) else Tooltip(str(tooltip)))]
    F -- No --> H[End]
    
    I[BaseMultiLocation._get_self_bounds] --> J[return get_bounds(self.locations)]
```

## Raises:
- TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data
- AssertionError: May be raised by Popup and Tooltip constructors if invalid arguments are provided

## Example:
```python
# Create a BaseMultiLocation instance with multiple coordinates
locations = [[40.7128, -74.0060], [37.7749, 122.4194], [34.0522, -118.2437]]

# Add a popup and tooltip
popup = Popup("New York City")
tooltip = Tooltip("Major US city")

# Create the base multi-location element
multi_location = BaseMultiLocation(locations, popup=popup, tooltip=tooltip)

# Get the bounding box for these locations
bounds = multi_location._get_self_bounds()
print(bounds)  # [[34.0522, -118.2437], [40.7128, 122.4194]]
```

### `folium.vector_layers.BaseMultiLocation.__init__` · *method*

## Summary:
Initializes a BaseMultiLocation object with geographic coordinates and optional interactive elements.

## Description:
Configures the BaseMultiLocation instance by validating input geographic coordinates and setting up associated popup and tooltip elements. This method serves as the constructor for multi-location vector layers, establishing the foundational geographic data and interactive features for map rendering. The method leverages the parent MacroElement class initialization and processes popup/tooltip arguments through Folium's element system by adding them as child elements.

## Args:
    locations (array-like): A potentially nested structure containing geographic coordinates. Can be a list, tuple, NumPy array, or pandas DataFrame of coordinate pairs. Supports both flat lists like [[lat, lon], [lat, lon]] and nested structures like [[[lat, lon]], [[lat, lon]]].
    popup (Popup or str, optional): An optional popup element or string to display when interacting with the location markers. Defaults to None.
    tooltip (Tooltip or str, optional): An optional tooltip element or string to display when hovering over the location markers. Defaults to None.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: If locations is not an iterable with coordinate pairs, or if coordinate values cannot be indexed.
    ValueError: If locations is empty or contains invalid coordinate data such as non-numeric values or improperly formatted coordinate pairs.
    AssertionError: If tooltip style parameter is not a string during Tooltip instantiation.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.locations (validated coordinate data)

## Constraints:
    Preconditions:
    - Input locations must be an iterable structure that can contain coordinate pairs
    - If popup is provided, it must be either a Popup instance or convertible to a string
    - If tooltip is provided, it must be either a Tooltip instance or convertible to a string
    
    Postconditions:
    - self.locations contains validated coordinate pairs in list format
    - Popup and tooltip elements are added as child elements if provided

## Side Effects:
    None

### `folium.vector_layers.BaseMultiLocation._get_self_bounds` · *method*

## Summary:
Computes the geographic bounding box that encompasses all locations in the multi-location vector layer.

## Description:
This method calculates the minimum and maximum latitude/longitude coordinates from all locations in the vector layer to determine its spatial extent. It serves as a standardized interface for retrieving the geographic bounds of multi-location vector elements like markers, lines, or polygons.

The method is called during map rendering operations when determining the appropriate zoom level and center point for displaying the vector layer. It encapsulates the logic for computing bounds from the stored locations, making it reusable across different vector layer implementations.

## Args:
    None

## Returns:
    list[list[float | None]]: A nested list representing the bounding box with format [[min_lat, min_lon], [max_lat, max_lon]]. Each coordinate can be None if no valid coordinates are provided.

## Raises:
    None explicitly raised, though underlying `get_bounds` function may raise standard Python exceptions for malformed inputs.

## State Changes:
    Attributes READ: self.locations
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The `self.locations` attribute must contain valid geographic coordinate data
    - Locations should be in a format compatible with the `get_bounds` utility function
    
    Postconditions:
    - Returns a list of exactly two lists, each containing two numeric values or None
    - The result represents a valid bounding box with min/max coordinates

## Side Effects:
    None

## `folium.vector_layers.PolyLine` · *class*

## Summary:
PolyLine is a vector layer class that renders geographic polylines on Folium maps, supporting customizable styling and interactive elements.

## Description:
The PolyLine class implements a vector layer for displaying connected line segments on interactive maps. It inherits from BaseMultiLocation to leverage shared functionality for managing multiple geographic coordinates, popup attachments, and bounding box calculations. This class is specifically designed for creating polyline visualizations that connect a series of geographic points, making it suitable for representing routes, paths, or linear geographic features.

## State:
- locations (list[list[float]]): Validated geographic coordinate pairs stored as a list of [latitude, longitude] lists. This attribute is initialized through validate_locations() and maintains the original nesting structure of the input, inherited from BaseMultiLocation
- _name (str): Identifier for this element type in Folium's rendering system, set to "PolyLine"
- options (dict): Styling configuration dictionary for the polyline, created by path_options() with line=True flag
- _children (dict): Child elements like Popup and Tooltip objects, inherited from MacroElement

## Lifecycle:
- Creation: Instantiate with required locations parameter and optional popup/tooltip. The constructor validates locations through BaseMultiLocation's initialization and sets up styling options
- Usage: Typically used as part of a Folium map by adding it to the map's elements. The rendering system calls internal methods to generate the appropriate JavaScript representation
- Destruction: Managed automatically through Folium's element lifecycle management system

## Method Map:
```mermaid
graph TD
    A[PolyLine.__init__] --> B[super().__init__(locations, popup=popup, tooltip=tooltip)]
    B --> C[self._name = "PolyLine"]
    C --> D[self.options = path_options(line=True, **kwargs)]
```

## Raises:
- TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs
- ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data
- AssertionError: May be raised by Popup and Tooltip constructors if invalid arguments are provided

## Example:
```python
import folium

# Create a map centered on New York
m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Define a route connecting multiple cities
locations = [
    [40.7128, -74.0060],  # New York
    [37.7749, 122.4194],  # San Francisco
    [34.0522, -118.2437]  # Los Angeles
]

# Create a styled polyline with popup and tooltip
polyline = folium.PolyLine(
    locations,
    popup="Coastal Route",
    tooltip="Route from NYC to LA",
    color="blue",
    weight=5,
    opacity=0.8
)

# Add the polyline to the map
m.add_child(polyline)

# Display the map
m
```

### `folium.vector_layers.PolyLine.__init__` · *method*

## Summary:
Initializes a PolyLine vector layer with geographic coordinates, interactive elements, and styling options.

## Description:
The PolyLine.__init__ method constructs a polyline vector layer by calling the parent class constructor to validate locations and attach interactive elements, setting the element name to "PolyLine", and configuring styling options through path_options. This method serves as the primary constructor for creating polyline visualizations on Folium maps, handling both basic location data and advanced styling parameters.

## Args:
    locations (list[list[float]]): A list of geographic coordinate pairs [latitude, longitude] defining the polyline path. Must be a valid iterable structure containing numeric coordinates.
    popup (Popup or str, optional): Interactive popup element or string to display when clicking the polyline. Defaults to None.
    tooltip (Tooltip or str, optional): Interactive tooltip element or string to display on hover. Defaults to None.
    **kwargs: Additional styling parameters for the polyline including color, weight, opacity, and other path options.

## Returns:
    None: This is a constructor method that initializes the object's state and does not return a value.

## Raises:
    TypeError: Raised by validate_locations() when locations is not an iterable with coordinate pairs.
    ValueError: Raised by validate_locations() when locations is empty or contains invalid coordinate data.
    AssertionError: May be raised by Popup and Tooltip constructors if invalid arguments are provided.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "PolyLine" to identify this element type in Folium's rendering system
    - self.options: Set to the result of path_options(line=True, **kwargs) for styling configuration

## Constraints:
    Preconditions:
    - locations must be a valid iterable structure containing geographic coordinate pairs
    - popup and tooltip parameters must be valid Popup or Tooltip instances or convertible strings
    - All kwargs must be valid styling parameters for path_options function
    
    Postconditions:
    - self._name is set to "PolyLine"
    - self.options contains a complete styling configuration dictionary
    - The parent BaseMultiLocation class is properly initialized with validated locations

## Side Effects:
    - Calls super().__init__() to initialize parent class functionality (BaseMultiLocation)
    - Invokes validate_locations() to process and validate the locations parameter
    - Calls path_options() to generate styling configuration
    - May add popup and tooltip as child elements through parent class mechanisms

## `folium.vector_layers.Polygon` · *class*

## Summary:
Polygon is a vector layer class that renders geographic polygon shapes on Folium maps, inheriting location management and interactive element support from BaseMultiLocation.

## Description:
The Polygon class implements a specialized vector layer for displaying closed polygonal regions on interactive maps. It inherits from BaseMultiLocation to leverage standardized location validation, popup/tooltip integration, and bounding box calculation capabilities. This class is designed to represent geographic areas defined by collections of coordinate points, making it suitable for overlaying regions, boundaries, or zones on maps. Common usage includes displaying administrative boundaries, environmental zones, or custom geographic regions with customizable styling.

## State:
- locations (list[list[float]]): Geographic coordinate pairs defining the polygon vertices, validated through BaseMultiLocation's initialization process
- _name (str): Class identifier set to "Polygon" for Folium's rendering system
- options (dict): Styling configuration dictionary generated by path_options() that controls visual appearance including stroke, fill, color, and other rendering properties

## Lifecycle:
- Creation: Instantiated with required locations parameter and optional popup/tooltip arguments, followed by path_options processing for styling
- Usage: Typically rendered as part of a Folium map through the standard rendering pipeline, where _get_self_bounds() is called to compute spatial extent
- Destruction: Managed automatically through Folium's element lifecycle management system

## Method Map:
```mermaid
graph TD
    A[Polygon.__init__] --> B[super().__init__(locations, popup, tooltip)]
    B --> C[self._name = "Polygon"]
    C --> D[self.options = path_options(line=True, **kwargs)]
```

## Raises:
- TypeError: Raised by validate_locations() inherited from BaseMultiLocation when locations is not an iterable with valid coordinate pairs
- ValueError: Raised by validate_locations() inherited from BaseMultiLocation when locations is empty or contains invalid coordinate data
- AssertionError: May be raised by Popup and Tooltip constructors if invalid arguments are provided

## Example:
```python
# Create a polygon representing a triangular region
locations = [
    [40.7128, -74.0060],  # New York City
    [37.7749, 122.4194],  # San Francisco
    [34.0522, -118.2437]  # Los Angeles
]

# Add interactive elements
popup = Popup("West Coast Triangle")
tooltip = Tooltip("California Region")

# Create polygon with custom styling
polygon = Polygon(
    locations,
    popup=popup,
    tooltip=tooltip,
    color="red",
    weight=2,
    fill=True,
    fillColor="yellow",
    fillOpacity=0.5
)

# The polygon is now ready to be added to a Folium map
```

### `folium.vector_layers.Polygon.__init__` · *method*

## Summary:
Initializes a Polygon vector layer with geographic coordinates and styling options.

## Description:
Configures a Polygon object by initializing its base class with location data and interactive elements, then sets the object's name identifier and styling options. This method establishes the fundamental properties required for rendering polygon shapes on Folium maps, including coordinate validation, popup/tooltip integration, and visual styling configuration. The method delegates location validation and interactive element setup to the parent BaseMultiLocation class, while specifically configuring the polygon's visual appearance through the path_options function.

## Args:
    locations (array-like): A potentially nested structure containing geographic coordinates. Can be a list, tuple, NumPy array, or pandas DataFrame of coordinate pairs. Supports both flat lists like [[lat, lon], [lat, lon]] and nested structures like [[[lat, lon]], [[lat, lon]]].
    popup (Popup or str, optional): An optional popup element or string to display when interacting with the polygon. Defaults to None.
    tooltip (Tooltip or str, optional): An optional tooltip element or string to display when hovering over the polygon. Defaults to None.
    **kwargs: Additional styling parameters that can include stroke, color, weight, opacity, lineCap, lineJoin, dashArray, dashOffset, fill, fillColor, fillOpacity, fillRule, bubblingMouseEvents, smoothFactor, noClip, and gradient.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: If locations is not an iterable with coordinate pairs, or if coordinate values cannot be indexed. Raised by validate_locations() inherited from BaseMultiLocation.
    ValueError: If locations is empty or contains invalid coordinate data such as non-numeric values or improperly formatted coordinate pairs. Raised by validate_locations() inherited from BaseMultiLocation.
    AssertionError: If tooltip style parameter is not a string during Tooltip instantiation.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Polygon" to identify this element type in Folium's rendering system
    - self.options: Set to a dictionary of styling options generated by path_options()

## Constraints:
    Preconditions:
    - Input locations must be an iterable structure that can contain coordinate pairs
    - If popup is provided, it must be either a Popup instance or convertible to a string
    - If tooltip is provided, it must be either a Tooltip instance or convertible to a string
    
    Postconditions:
    - self.locations contains validated coordinate pairs in list format (inherited from BaseMultiLocation)
    - self._name is set to "Polygon"
    - self.options contains processed styling configuration

## Side Effects:
    None

## `folium.vector_layers.Rectangle` · *class*

## Summary:
Rectangle is a vector layer class that renders rectangular areas on Folium maps using geographic bounds.

## Description:
The Rectangle class implements a vector layer for displaying rectangular regions on interactive maps. It inherits from BaseMultiLocation to leverage shared functionality for handling multiple geographic locations and integrates with Folium's rendering system through MacroElement inheritance. This class specifically creates rectangle-shaped overlays defined by geographic bounds, making it suitable for displaying areas such as building footprints, administrative boundaries, or any rectangular geographic region.

## State:
- bounds (list[list[float]]): Geographic coordinate pairs defining the rectangle's boundaries as [[min_lat, min_lon], [max_lat, max_lon]]. This attribute is inherited from BaseMultiLocation and validated through the parent's initialization process.
- _name (str): Set to "rectangle" to identify this element type in Folium's rendering system.
- options (dict): Dictionary of styling options for the rectangle, configured through path_options() with line=True to ensure proper rendering as a rectangular outline.

## Lifecycle:
- Creation: Instantiate with bounds parameter (required) and optional popup/tooltip parameters. The constructor validates bounds through BaseMultiLocation's initialization and sets up styling options.
- Usage: Typically used as part of a Folium map's layer stack. The rendering system automatically calls appropriate methods during map generation.
- Destruction: Managed automatically through Folium's element lifecycle management system.

## Method Map:
```mermaid
graph TD
    A[Rectangle.__init__] --> B[super().__init__(bounds, popup=popup, tooltip=tooltip)]
    B --> C[self._name = "rectangle"]
    C --> D[self.options = path_options(line=True, **kwargs)]
```

## Raises:
- TypeError: Raised by validate_locations() in BaseMultiLocation when bounds is not an iterable with valid coordinate pairs
- ValueError: Raised by validate_locations() in BaseMultiLocation when bounds is empty or contains invalid coordinate data
- AssertionError: May be raised by Popup and Tooltip constructors if invalid arguments are provided

## Example:
```python
import folium

# Create a map centered on New York City
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Define bounds for a rectangular area (southwest corner, northeast corner)
bounds = [[40.7000, -74.0200], [40.7300, -73.9800]]

# Create a rectangle with custom styling
rectangle = folium.Rectangle(
    bounds=bounds,
    popup="Central Park Area",
    tooltip="Rectangle Overlay",
    color="blue",
    weight=2,
    fill=True,
    fillColor="lightblue",
    fillOpacity=0.5
)

# Add the rectangle to the map
rectangle.add_to(m)

# Display the map
m
```

### `folium.vector_layers.Rectangle.__init__` · *method*

## Summary:
Initializes a Rectangle vector layer with geographic bounds and styling options.

## Description:
Configures a Rectangle object for rendering rectangular geographic areas on Folium maps. This method sets up the object's identification name and styling options, inheriting bounds validation and popup/tooltip setup from its parent class.

## Args:
    bounds (list[list[float]]): Geographic coordinate pairs defining the rectangle's boundaries as [[min_lat, min_lon], [max_lat, max_lon]].
    popup (Popup, optional): Popup element to display when clicking on the rectangle. Defaults to None.
    tooltip (Tooltip, optional): Tooltip element to display on hover over the rectangle. Defaults to None.
    **kwargs: Additional styling parameters passed to path_options() for configuring line and fill properties.

## Returns:
    None

## Raises:
    TypeError: Raised by validate_locations() in BaseMultiLocation when bounds is not an iterable with valid coordinate pairs.
    ValueError: Raised by validate_locations() in BaseMultiLocation when bounds is empty or contains invalid coordinate data.
    AssertionError: May be raised by Popup and Tooltip constructors if invalid arguments are provided.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "rectangle" to identify this element type
        - self.options: Configured with styling options via path_options()

## Constraints:
    Preconditions:
        - bounds must be a valid iterable of two coordinate pairs
        - Each coordinate pair must contain valid latitude and longitude values
        - popup and tooltip must be instances of their respective classes or None
    Postconditions:
        - self._name is set to "rectangle"
        - self.options contains a properly formatted dictionary of styling options

## Side Effects:
    - Calls super().__init__() to initialize parent class with bounds, popup, and tooltip
    - Invokes path_options() function to process styling parameters
    - May raise exceptions from parent class initialization or popup/tooltip construction

## `folium.vector_layers.Circle` · *class*

## Summary:
A Circle class that represents a circular vector layer element for folium maps, capable of rendering circles with customizable radius and styling options at specific geographic locations.

## Description:
The Circle class extends the Marker base class to create circular vector elements that can be displayed on folium maps. While inheriting the basic marker functionality from Marker, Circle specializes in rendering circular geometries with configurable radius properties rather than standard marker icons. It serves as a visualization tool for representing geographic areas with fixed radii, such as buffer zones, coverage areas, or circular regions of interest.

## State:
- location (list[float] or None): Geographic coordinates [latitude, longitude] inherited from Marker parent class, validated through validate_location
- _name (str): Class identifier set to "circle" for internal Folium processing
- options (dict): Configuration options for circle styling, processed via path_options function including radius and various visual properties
- _template (Template): Jinja2 template for rendering the circle HTML (currently empty in implementation)

## Lifecycle:
- Creation: Instantiate with optional location, radius, popup, tooltip, and additional styling parameters
- Usage: Add to a map using add_child() method, then render within a Figure context
- Destruction: Managed automatically through the Element parent-child relationship system

## Method Map:
```mermaid
graph TD
    A[Circle.__init__] --> B[super().__init__()]
    B --> C[self._name = "circle"]
    C --> D[self.options = path_options(line=False, radius=radius, **kwargs)]
    D --> E[End]

    F[Circle.render] --> G[super().render()]
```

## Raises:
- ValueError: When render() is called and location has not been assigned (inherited from parent Marker class)
- AssertionError: When trying to render the circle outside of a Figure context (inherited from parent class)

## Example:
```python
# Create a basic circle at a location with default radius
circle = Circle(
    location=[40.7128, -74.0060],
    popup="Circle Area",
    tooltip="NYC Circle"
)

# Create a circle with custom radius and styling
styled_circle = Circle(
    location=[37.7749, 122.4194],
    radius=1000,  # 1km radius
    color='red',
    fill_color='blue',
    fill_opacity=0.5
)

# Add circles to a map
map_instance.add_child(circle)
map_instance.add_child(styled_circle)
```

### `folium.vector_layers.Circle.__init__` · *method*

## Summary:
Initializes a Circle vector layer with location, radius, and styling options for rendering on folium maps.

## Description:
The `__init__` method sets up a Circle instance by initializing its parent Marker class with location, popup, and tooltip parameters, then configures the circle-specific attributes including its name identifier and styling options. This method establishes the foundational properties needed for rendering circular vector elements on interactive maps.

## Args:
    location (list[float] or None): Geographic coordinates [latitude, longitude] for the circle center. Defaults to None.
    radius (float): Radius of the circle in meters. Defaults to 50.
    popup (Popup or None): Popup message to display on click. Defaults to None.
    tooltip (Tooltip or None): Tooltip to display on hover. Defaults to None.
    **kwargs: Additional styling parameters passed to path_options for configuring visual properties like color, weight, fill, etc.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "circle" to identify this element type
    - self.options: Set to the result of path_options(line=False, radius=radius, **kwargs) for styling configuration

## Constraints:
    - Precondition: The location parameter should be a valid coordinate pair or None
    - Precondition: The radius parameter should be a numeric value
    - Postcondition: The instance will have _name set to "circle" and options configured for rendering

## Side Effects:
    - Calls the parent Marker.__init__ method to initialize inherited properties
    - Invokes the path_options function to process styling parameters

## `folium.vector_layers.CircleMarker` · *class*

## Summary:
A CircleMarker class that represents a circular marker element for folium maps, designed for displaying point features with customizable radius and styling options.

## Description:
The CircleMarker class extends the Marker base class to create circular markers that can be displayed on folium maps. Unlike regular markers, CircleMarkers are specifically designed for point features that require a circular visual representation with adjustable radius. This class is commonly used in vector layer rendering to display geographic points with consistent circular styling. CircleMarkers are typically created through direct instantiation or via factory methods in vector layer implementations.

## State:
- location (list[float] or None): Geographic coordinates [latitude, longitude] validated through validate_location, or None if not yet assigned
- _name (str): Class identifier set to "CircleMarker" for internal Folium processing
- options (dict): Configuration options for circle marker styling, processed via path_options including radius and other path properties
- _template (Template): Jinja2 template used for rendering the circle marker HTML (currently empty in implementation)

## Lifecycle:
- Creation: Instantiate with optional location, radius, popup, tooltip, and additional styling parameters
- Usage: Add to a map using add_child() method, then render within a Figure context (which internally calls render())
- Destruction: Managed automatically through the Element parent-child relationship system

## Method Map:
```mermaid
graph TD
    A[CircleMarker.__init__] --> B[super().__init__()]
    B --> C[self._name = "CircleMarker"]
    C --> D[self.options = path_options(line=False, radius=radius, **kwargs)]
    D --> E[End]

    F[CircleMarker.render] --> G[super().render()]
```

## Raises:
- ValueError: When render() is called and location has not been assigned (inherited from parent Marker class)
- AssertionError: When trying to render the marker outside of a Figure context (inherited from parent class)

## Example:
```python
# Create a basic circle marker at a location
circle_marker = CircleMarker(
    location=[40.7128, -74.0060],
    radius=15,
    popup="New York City",
    tooltip="NYC"
)

# Create a styled circle marker with custom colors
styled_circle = CircleMarker(
    location=[37.7749, 122.4194],
    radius=20,
    color='red',
    fillColor='orange',
    fillOpacity=0.5
)

# Add circle markers to a map
map_instance.add_child(circle_marker)
map_instance.add_child(styled_circle)
```

### `folium.vector_layers.CircleMarker.__init__` · *method*

## Summary:
Initializes a CircleMarker object with location, radius, and optional popup/tooltip features, setting up the object's name and styling options for vector rendering.

## Description:
The CircleMarker.__init__ method constructs a circle marker element for folium vector layers by initializing the parent Marker class and configuring essential properties for rendering. This constructor sets the marker's identification name to "CircleMarker" and prepares its styling options through the path_options function. The method inherits location validation from the parent Marker class and handles popup/tooltip setup through the standard Marker initialization process.

## Args:
    location (list[float] or None): Geographic coordinates [latitude, longitude] for the marker's position, validated by validate_location. Defaults to None.
    radius (int or float): Radius of the circle marker in pixels. Defaults to 10.
    popup (Popup or None): Optional popup element to display when the marker is clicked. Defaults to None.
    tooltip (Tooltip or None): Optional tooltip element to display when hovering over the marker. Defaults to None.
    **kwargs: Additional styling parameters passed to the path_options function for customizing the circle's appearance.

## Returns:
    None: This method initializes the object's state but does not return any value.

## Raises:
    TypeError: If location is not a sized variable or doesn't support indexing (inherited from validate_location).
    ValueError: If location doesn't contain exactly two values or contains non-numerical values (inherited from validate_location) or if location is None and render() is called (inherited from Marker).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "CircleMarker" to identify the element type for rendering
    - self.options: Configured with path_options containing styling properties for the circle marker

## Constraints:
    - Precondition: The location parameter should be a valid geographic coordinate pair or None
    - Postcondition: The CircleMarker instance is properly initialized with _name set to "CircleMarker" and options configured via path_options
    - The location parameter must be validated by validate_location before being stored

## Side Effects:
    - Calls the parent Marker.__init__ method which may add child elements (popup, tooltip) and validates the location parameter
    - Invokes the path_options function to process styling parameters for vector rendering

