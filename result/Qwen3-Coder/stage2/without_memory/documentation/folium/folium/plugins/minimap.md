# `minimap.py`

## `folium.plugins.minimap.MiniMap` · *class*

## Summary:
A MiniMap control that displays a smaller overview map within a larger map, allowing users to navigate and track their position on the main map.

## Description:
The MiniMap class implements a minimap control for folium maps by integrating with the Leaflet minimap JavaScript plugin. It provides a smaller view of the map that updates as the user navigates the main map, helping users orient themselves and quickly navigate to different areas. This class is typically instantiated by developers who want to add a minimap to their folium map visualizations.

## State:
- tile_layer: TileLayer instance representing the map tiles displayed in the minimap
- options: Dictionary containing configuration options for the minimap control
- _name: String identifier set to "MiniMap" for internal tracking
- default_js: List of tuples containing JavaScript library names and URLs for the minimap plugin
- default_css: List of tuples containing CSS library names and URLs for the minimap styling

## Lifecycle:
- Creation: Instantiate with optional tile_layer and configuration parameters
- Usage: Add to a folium.Map instance using the add_child() method
- Destruction: Managed automatically by folium's rendering system when the map is destroyed

## Method Map:
```mermaid
graph TD
    A[MiniMap.__init__] --> B[super().__init__()]
    A --> C[tile_layer handling]
    A --> D[parse_options for configuration]
    B --> E[JSCSSMixin.render]
    E --> F[Add JS/CSS links to figure header]
```

## Raises:
- AssertionError: When invalid options are passed to parse_options (if the parent class validation is triggered)

## Example:
```python
import folium
from folium.plugins import MiniMap

# Create a base map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a minimap with default settings
minimap = MiniMap()

# Add the minimap to the main map
m.add_child(minimap)

# Or create a minimap with custom settings
custom_minimap = MiniMap(
    position='topleft',
    width=200,
    height=200,
    zoom_level_offset=-3
)

m.add_child(custom_minimap)
```

### `folium.plugins.minimap.MiniMap.__init__` · *method*

## Summary:
Initializes a MiniMap plugin with configurable positioning, sizing, and display options.

## Description:
Configures the MiniMap plugin by setting up its tile layer source and various display properties. This method establishes the foundational configuration for the minimap widget that will be rendered in folium maps.

## Args:
    tile_layer (TileLayer or str or None): The tile layer to display in the minimap. If None, creates a default TileLayer. If a string, treats it as a URL template. If a TileLayer instance, uses it directly.
    position (str): Position of the minimap on the map. Defaults to "bottomright".
    width (int): Width of the minimap in pixels. Defaults to 150.
    height (int): Height of the minimap in pixels. Defaults to 150.
    collapsed_width (int): Width of the minimap when collapsed in pixels. Defaults to 25.
    collapsed_height (int): Height of the minimap when collapsed in pixels. Defaults to 25.
    zoom_level_offset (int): Offset applied to the zoom level. Defaults to -5.
    zoom_level_fixed (int or None): Fixed zoom level for the minimap. Defaults to None.
    center_fixed (bool): Whether to fix the center position. Defaults to False.
    zoom_animation (bool): Whether to enable zoom animation. Defaults to False.
    toggle_display (bool): Whether to enable toggle display functionality. Defaults to False.
    auto_toggle_display (bool): Whether to automatically toggle display. Defaults to False.
    minimized (bool): Whether the minimap starts minimized. Defaults to False.
    **kwargs: Additional keyword arguments passed to the options parser.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    AssertionError: If invalid options are provided to parse_options.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: _name, tile_layer, options

## Constraints:
    Preconditions: None
    Postconditions: The MiniMap instance is properly initialized with configured properties.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

