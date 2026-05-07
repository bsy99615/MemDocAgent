# `semicircle.py`

## `folium.plugins.semicircle.SemiCircle` · *class*

## Summary:
Represents a semicircular shape element for folium maps that displays a partial circle with customizable direction or angle range.

## Description:
The SemiCircle class creates semicircular shapes on folium maps using the leaflet-semicircle JavaScript library. It allows users to define semicircles either by specifying a direction and arc angle, or by defining start and stop angles. This class extends the Marker base class to provide geographic positioning capabilities while adding specialized semicircle rendering features.

The class is designed to be used when creating map visualizations that require partial circular elements, such as directional indicators, angular ranges, or sector representations on geographic maps.

## State:
- location (list[float]): Geographic coordinates [latitude, longitude] for the semicircle center point. Validated using validate_location() function.
- direction (tuple or None): Pair of (direction, arc) values defining the semicircle's orientation and size. When provided, start_angle and stop_angle must be None.
- options (dict): Configuration options for semicircle styling including radius, stroke properties, and fill properties. Processed using path_options() and parse_options() functions.
- _name (str): Class identifier set to "SemiCircle" for internal tracking and rendering.

## Lifecycle:
Creation: Instantiate with location and radius, plus either direction/arc OR start_angle/stop_angle parameters. The constructor validates parameter combinations and processes styling options.
Usage: Add to a folium Map or Figure using standard element addition methods. Call render() to generate JavaScript representation.
Destruction: Managed automatically by folium's element lifecycle management.

## Method Map:
```mermaid
flowchart TD
    A[SemiCircle.__init__] --> B[super().__init__()]
    B --> C[Set _name="SemiCircle"]
    C --> D{direction and arc provided?}
    D -- Yes --> E[Set direction=(direction, arc)]
    D -- No --> F[Set direction=None]
    E --> G[Set options=path_options(...)]
    F --> G
    G --> H[Update options with parse_options(...)]
    H --> I{Parameter validation?}
    I -- Invalid --> J[raise ValueError]
    I -- Valid --> K[Finish init]

    L[SemiCircle.render] --> M[super().render()]
```

## Raises:
- ValueError: When the constructor receives invalid parameter combinations. Specifically raised when neither both direction/arc nor both start_angle/stop_angle parameters are provided, or when both parameter sets are provided simultaneously.

## Example:
```python
import folium

# Create a map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a semicircle using direction and arc parameters
semicircle1 = folium.plugins.SemiCircle(
    location=[45.5236, -122.6750],
    radius=1000,
    direction=90,  # Eastward
    arc=180        # Half circle
)

# Create a semicircle using start and stop angle parameters
semicircle2 = folium.plugins.SemiCircle(
    location=[45.5236, -122.6750],
    radius=1500,
    start_angle=0,
    stop_angle=180
)

# Add semicircles to map
semicircle1.add_to(m)
semicircle2.add_to(m)

# Render the map
m.save("semicircle_example.html")
```

### `folium.plugins.semicircle.SemiCircle.__init__` · *method*

## Summary:
Initializes a SemiCircle object with geographic location, radius, and angular parameters for defining the semicircle shape.

## Description:
Configures a semicircle marker element for folium maps with specified geographic coordinates, radius, and angular positioning. The semicircle can be defined either by directional parameters (direction and arc) or by angular limits (start_angle and stop_angle), but not both combinations simultaneously. This method sets up the internal state and configuration options required for rendering the semicircle on a map.

## Args:
    location (list[float]): Geographic coordinates [latitude, longitude] defining the center point of the semicircle.
    radius (float): Radius of the semicircle in meters.
    direction (float, optional): Direction angle in degrees for the semicircle orientation. Must be used with arc parameter.
    arc (float, optional): Arc size in degrees defining the extent of the semicircle. Must be used with direction parameter.
    start_angle (float, optional): Starting angle in degrees for the semicircle. Must be used with stop_angle parameter.
    stop_angle (float, optional): Ending angle in degrees for the semicircle. Must be used with start_angle parameter.
    popup (Popup, optional): Popup element to display when clicking the semicircle.
    tooltip (Tooltip, optional): Tooltip element to display when hovering over the semicircle.
    **kwargs: Additional styling options passed to path_options function for configuring the semicircle appearance.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    ValueError: When invalid argument combinations are provided - either both direction/arc and start_angle/stop_angle combinations are specified, or neither combination is provided.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "SemiCircle"
        - self.direction: Set to tuple (direction, arc) if both are provided, otherwise None
        - self.options: Set to path_options configuration dictionary

## Constraints:
    Preconditions:
        - location must be a valid geographic coordinate pair [latitude, longitude]
        - radius must be a positive numeric value
        - Either provide both direction and arc parameters OR provide both start_angle and stop_angle parameters, but not both combinations
    Postconditions:
        - self._name is set to "SemiCircle"
        - self.direction is properly configured as a tuple or None
        - self.options contains valid path configuration options
        - The object is ready for rendering in a folium map context

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

