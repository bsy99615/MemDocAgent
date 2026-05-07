# `semicircle.py`

## `folium.plugins.semicircle.SemiCircle` · *class*

## Summary:
A SemiCircle class that represents a semicircular shape element for folium maps, capable of rendering partial circles with customizable direction or angle ranges.

## Description:
The SemiCircle class extends JSCSSMixin and Marker to create interactive semicircular shapes on folium maps. It leverages the leaflet-semicircle JavaScript library to render semicircles with either directional/arcing specifications or explicit angular ranges. This class serves as a specialized visualization tool for representing partial circular areas, such as coverage zones, directional signals, or angular measurements on geographic maps.

## State:
- location (list[float]): Geographic coordinates [latitude, longitude] defining the center point of the semicircle
- _name (str): Class identifier set to "SemiCircle" for internal Folium processing
- direction (tuple or None): Pair of (direction, arc) values when specifying semicircle via direction and arc, otherwise None
- options (dict): Configuration options for semicircle rendering including radius, line styling, and angular parameters
- _template (Template): Jinja2 template for rendering the semicircle HTML (empty in current implementation)
- default_js (list): JavaScript dependencies including leaflet-semicircle library from CDN

## Lifecycle:
- Creation: Instantiate with location, radius, and either direction/arc OR start_angle/stop_angle parameters
- Usage: Add to a folium map using add_child() method, then render within a Figure context
- Destruction: Managed automatically through the Element parent-child relationship system

## Method Map:
```mermaid
graph TD
    A[SemiCircle.__init__] --> B[super().__init__()]
    B --> C[self._name = "SemiCircle"]
    C --> D{direction and arc provided?}
    D -- Yes --> E[self.direction = (direction, arc)]
    D -- No --> F[self.direction = None]
    E --> G[self.options = path_options(line=False, radius=radius, **kwargs)]
    F --> G
    G --> H[self.options.update(parse_options(start_angle=start_angle, stop_angle=stop_angle))]
    H --> I{Validation check}
    I -- Invalid --> J[raise ValueError]
    I -- Valid --> K[End]

    K --> L[SemiCircle.render]
    L --> M[super().render()]
```

## Raises:
- ValueError: When invalid argument combinations are provided (must specify either direction/arc OR start_angle/stop_angle, but not both)

## Example:
```python
import folium

# Create a semicircle using direction and arc specification
semicircle1 = folium.plugins.SemiCircle(
    location=[40.7128, -74.0060],
    radius=1000,
    direction=90,  # Eastward
    arc=180        # Half circle
)

# Create a semicircle using angular range specification
semicircle2 = folium.plugins.SemiCircle(
    location=[37.7749, -122.4194],
    radius=2000,
    start_angle=0,
    stop_angle=180
)

# Add to map
m = folium.Map([40.7128, -74.0060], zoom_start=12)
m.add_child(semicircle1)
m.add_child(semicircle2)
```

### `folium.plugins.semicircle.SemiCircle.__init__` · *method*

## Summary:
Initializes a SemiCircle element with location, radius, and directional parameters for rendering semicircular shapes on folium maps.

## Description:
The SemiCircle.__init__ method configures a semicircular marker element by setting its geographic location, radius, and angular parameters. It inherits from Marker and extends its functionality to support semicircular rendering with customizable direction or angle ranges. This method enforces mutually exclusive parameter combinations to ensure valid semicircle specifications and prepares the necessary options dictionary for JavaScript rendering through the leaflet-semicircle library.

## Args:
    location (array-like): Geographic coordinates as [latitude, longitude] for the circle center.
    radius (float): Radius of the semicircle in meters.
    direction (float, optional): Direction in degrees for the semicircle orientation. Defaults to None.
    arc (float, optional): Arc size in degrees for the semicircle. Defaults to None.
    start_angle (float, optional): Starting angle in degrees for the semicircle. Defaults to None.
    stop_angle (float, optional): Ending angle in degrees for the semicircle. Defaults to None.
    popup (Popup or str, optional): Popup element or HTML string to display on click. Defaults to None.
    tooltip (Tooltip or str, optional): Tooltip element or text to display on hover. Defaults to None.
    **kwargs: Additional styling options passed to path_options function.

## Returns:
    None

## Raises:
    ValueError: When invalid parameter combinations are provided. Must specify either both direction and arc parameters OR both start_angle and stop_angle parameters, but not both combinations simultaneously.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN:
    - self._name: Set to "SemiCircle"
    - self.direction: Set to tuple of (direction, arc) if both are provided, otherwise None
    - self.options: Set to path_options dictionary with line=False and radius parameters

## Constraints:
    Preconditions:
    - Location must be a valid coordinate pair
    - Either provide both direction and arc parameters OR both start_angle and stop_angle parameters
    - Cannot mix direction/arc with start_angle/stop_angle parameter combinations
    
    Postconditions:
    - self._name is always set to "SemiCircle"
    - self.direction is properly configured based on parameter combinations
    - self.options contains all required path styling parameters for semicircle rendering

## Side Effects:
    - Calls super().__init__() to initialize parent Marker class with location, popup, and tooltip
    - Calls path_options() to process styling parameters for semicircle rendering
    - Calls parse_options() to process angle-related parameters for JavaScript compatibility

