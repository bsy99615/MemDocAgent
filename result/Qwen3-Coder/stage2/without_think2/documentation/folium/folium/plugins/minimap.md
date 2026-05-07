# `minimap.py`

## `folium.plugins.minimap.MiniMap` · *class*

## Summary:
A MiniMap widget that displays a smaller overview map within a larger map, allowing users to navigate and visualize their location within the broader map area.

## Description:
The MiniMap class implements a Leaflet minimap control that provides a smaller, simplified view of the main map. It allows users to quickly navigate the main map by clicking on the minimap or dragging the minimap's indicator. This component is particularly useful for large maps where users need to understand their current position relative to the entire map area. The minimap can be customized in size, position, and behavior through various configuration options.

This class inherits from JSCSSMixin and MacroElement, making it a proper folium map element that automatically handles JavaScript and CSS dependencies when rendered. It should be added to a folium.Map instance using the add_child() method.

## State:
- tile_layer: TileLayer instance representing the map tiles displayed in the minimap
  - Type: folium.raster_layers.TileLayer
  - Valid values: Any valid TileLayer instance or None (defaults to new TileLayer())
  - Default: None (creates new TileLayer instance)
- options: dict containing configuration options for the minimap control
  - Type: dict
  - Valid values: Dictionary with camelCase keys derived from constructor parameters via parse_options
  - Invariant: Contains all configuration parameters passed to constructor via parse_options
- _name: String identifier for the element
  - Type: str
  - Value: "MiniMap"
- _template: Jinja2 template for rendering the minimap HTML
  - Type: jinja2.Template
  - Value: Empty template (likely populated by parent classes)

## Lifecycle:
- Creation: Instantiate with optional tile_layer and configuration parameters
- Usage: Add to a folium.Map instance using the add_child() method
- Destruction: Managed by folium's map rendering system when the map is destroyed

## Method Map:
```mermaid
graph TD
    A[MiniMap.__init__] --> B[super().__init__()]
    B --> C[Set _name="MiniMap"]
    C --> D[Process tile_layer parameter]
    D --> E[Parse options with parse_options]
    E --> F[Return initialized MiniMap]
    
    G[folium.Map.add_child] --> H[MiniMap.render()]
    H --> I[JSCSSMixin.render()]
    I --> J[Add JS/CSS dependencies]
    J --> K[Render HTML with template]
```

## Raises:
- None explicitly raised by __init__
- AssertionError may be raised during rendering if the element is not contained within a Figure object

## Example:
```python
import folium
from folium.plugins import MiniMap

# Create a base map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add a minimap
minimap = MiniMap()
m.add_child(minimap)

# Or with custom tile layer and options
tile_layer = folium.TileLayer('OpenStreetMap')
minimap = MiniMap(tile_layer=tile_layer, position='topright', width=200, height=200)
m.add_child(minimap)
```

### `folium.plugins.minimap.MiniMap.__init__` · *method*

## Summary:
Initializes a MiniMap plugin instance with configurable display properties and tile layer settings.

## Description:
Configures the MiniMap plugin by setting up its tile layer source, positioning, sizing, and various display options. This method establishes the foundational configuration for the minimap widget that will be rendered in folium maps.

## Args:
    tile_layer (TileLayer or str, optional): The tile layer to use for the minimap. If None, creates a default TileLayer. If a string, treats it as a URL template. Defaults to None.
    position (str): Position of the minimap on the map. Valid values are 'topleft', 'topright', 'bottomleft', 'bottomright'. Defaults to 'bottomright'.
    width (int): Width of the minimap in pixels when expanded. Defaults to 150.
    height (int): Height of the minimap in pixels when expanded. Defaults to 150.
    collapsed_width (int): Width of the minimap in pixels when collapsed. Defaults to 25.
    collapsed_height (int): Height of the minimap in pixels when collapsed. Defaults to 25.
    zoom_level_offset (int): Offset applied to the zoom level of the minimap relative to the main map. Defaults to -5.
    zoom_level_fixed (int, optional): Fixed zoom level for the minimap. If None, uses dynamic zoom. Defaults to None.
    center_fixed (bool): Whether to fix the center of the minimap. Defaults to False.
    zoom_animation (bool): Whether to enable zoom animation. Defaults to False.
    toggle_display (bool): Whether to show a toggle button for the minimap. Defaults to False.
    auto_toggle_display (bool): Whether to automatically toggle display based on map size. Defaults to False.
    minimized (bool): Whether the minimap starts minimized. Defaults to False.
    **kwargs: Additional options passed to the underlying JavaScript implementation.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MiniMap"
    - self.tile_layer: Set to a TileLayer instance
    - self.options: Set to a dictionary of parsed options

## Constraints:
    Preconditions:
    - position must be one of 'topleft', 'topright', 'bottomleft', 'bottomright'
    - width, height, collapsed_width, collapsed_height must be positive integers
    - zoom_level_offset must be an integer
    - zoom_level_fixed must be an integer or None

    Postconditions:
    - self._name is set to "MiniMap"
    - self.tile_layer is always a TileLayer instance
    - self.options contains all provided parameters in camelCase format

## Side Effects:
    None: This method performs no I/O operations or external service calls.

