# `semicircle.py`

## `folium.plugins.semicircle.SemiCircle` · *class*

## Summary:
Represents a semicircular shape element that can be added to folium maps, allowing visualization of partial circles with customizable direction or angular bounds.

## Description:
The SemiCircle class creates semicircular shapes on folium maps that can be defined either by specifying a direction and arc angle or by defining start and stop angles. It extends the Marker base class to provide positioning capabilities while incorporating JavaScript resources for rendering semicircles using the leaflet-semicircle library. This class is particularly useful for displaying directional data, angular ranges, or partial circular regions on interactive maps.

## State:
- location: list[float] - Geographic coordinates [latitude, longitude] for the circle center
- direction: tuple[float, float] or None - Direction and arc parameters when using direction-based specification
- options: dict - Styling options for the semicircle including radius, stroke properties, and color settings
- _name: str - Set to "SemiCircle" for internal identification

## Lifecycle:
- Creation: Instantiate with location and radius, plus either direction/arc OR start_angle/stop_angle parameters
- Usage: Add to a folium map using add_child() method; rendering automatically includes required JavaScript resources
- Destruction: Managed by folium's rendering system when the map is disposed

## Method Map:
```mermaid
graph TD
    A[SemiCircle.__init__] --> B[super().__init__]
    B --> C[Set _name to "SemiCircle"]
    C --> D[Validate parameter combinations]
    D --> E{Valid combination?}
    E -- Yes --> F[Set direction attribute]
    E -- No --> G[raise ValueError]
    F --> H[Set options with path_options]
    H --> I[Update options with parse_options]
    I --> J[End]
    G --> J
```

## Raises:
- ValueError: When invalid parameter combinations are provided (neither both direction/arc nor both start_angle/stop_angle are specified, or both combinations are provided)

## Example:
```python
import folium

# Create a map
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Create a semicircle using direction and arc parameters
semicircle1 = folium.plugins.SemiCircle(
    location=[40.7128, -74.0060],
    radius=1000,
    direction=45,  # Direction in degrees
    arc=180        # Arc angle in degrees
)

# Create a semicircle using start and stop angles
semicircle2 = folium.plugins.SemiCircle(
    location=[40.7128, -74.0060],
    radius=1500,
    start_angle=0,
    stop_angle=90
)

# Add to map
m.add_child(semicircle1)
m.add_child(semicircle2)
```

### `folium.plugins.semicircle.SemiCircle.__init__` · *method*

## Summary:
Initializes a SemiCircle object with geographic location, radius, and angular parameters for drawing semicircular shapes on folium maps.

## Description:
Configures a SemiCircle marker with positioning, size, and angular specifications for rendering semicircular shapes on interactive maps. This method sets up the object's state including name, directional parameters, and styling options while enforcing mutually exclusive parameter combinations for valid semicircle construction.

## Args:
    location (list[float]): Geographic coordinates [latitude, longitude] defining the circle center.
    radius (float): Radius of the semicircle in meters.
    direction (float, optional): Direction in degrees (0-360) for semicircle orientation. Defaults to None.
    arc (float, optional): Arc length in degrees (0-180) defining the semicircle extent. Defaults to None.
    start_angle (float, optional): Starting angle in degrees for semicircle arc. Defaults to None.
    stop_angle (float, optional): Ending angle in degrees for semicircle arc. Defaults to None.
    popup (Popup, optional): Popup information for the marker. Defaults to None.
    tooltip (Tooltip, optional): Tooltip information for the marker. Defaults to None.
    **kwargs: Additional styling options passed to path_options().

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    ValueError: When invalid parameter combinations are provided. Must specify either both direction and arc OR both start_angle and stop_angle, but not both combinations simultaneously.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "SemiCircle"
    - self.direction: Set to tuple (direction, arc) if both provided, otherwise None
    - self.options: Set to path_options() result with line=False and radius, updated with parsed start/stop angle options

## Constraints:
    Preconditions:
    - location must be a valid coordinate pair [lat, lng]
    - Either both direction and arc must be provided (with start_angle and stop_angle as None), or both start_angle and stop_angle must be provided (with direction and arc as None)
    - Cannot mix direction/arc with start_angle/stop_angle parameters
    - radius must be a positive numeric value

    Postconditions:
    - self._name is set to "SemiCircle"
    - self.direction contains valid parameter combination or None
    - self.options contains properly formatted styling options
    - Object is ready for rendering on folium maps

## Side Effects:
    None: This method performs no I/O operations or external service calls.

