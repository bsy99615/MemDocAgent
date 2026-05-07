# `minimap.py`

## `folium.plugins.minimap.MiniMap` · *class*

## Summary:
A MiniMap control that displays a smaller overview map within a larger folium map visualization.

## Description:
The MiniMap class implements a minimap control for folium maps that shows a smaller overview of the main map. This control allows users to quickly navigate and orient themselves within large map visualizations by providing a bird's-eye view of the entire map area. The minimap can be positioned anywhere on the main map and customized with various size, zoom, and display options.

This class is particularly useful for large-scale mapping applications where users need to understand their current location within a broader geographic context. It integrates seamlessly with folium's rendering system and automatically includes required JavaScript and CSS resources.

## State:
- tile_layer: A TileLayer object representing the base layer displayed in the minimap. Can be None (creates default TileLayer), a TileLayer instance, or a string URL for a tile service.
- options: Dictionary of configuration options parsed from constructor parameters using parse_options, converted to camelCase keys for JavaScript compatibility.
- _name: String identifier set to "MiniMap" for internal tracking and rendering purposes.

## Lifecycle:
- Creation: Instantiate with optional tile_layer and configuration parameters. The tile_layer parameter can be None, a TileLayer object, or a string URL for a tile service.
- Usage: Add to a folium.Map instance using the add_child() method. The minimap will automatically include required JavaScript and CSS resources from CDN when rendered within a folium Figure context.
- Destruction: Cleanup is handled automatically when the map is destroyed or when the element is removed from the map.

## Method Map:
```mermaid
graph TD
    A[MiniMap.__init__] --> B[Super().__init__]
    B --> C[Set _name="MiniMap"]
    C --> D{tile_layer is None?}
    D -- Yes --> E[Create default TileLayer()]
    D -- No --> F{tile_layer is TileLayer?}
    F -- Yes --> G[Use tile_layer directly]
    F -- No --> H[Create TileLayer(tile_layer)]
    G --> I[Parse options with parse_options]
    H --> I
    I --> J[Return initialized MiniMap]
```

## Raises:
- None explicitly raised by __init__, though underlying implementations in parent classes (JSCSSMixin, MacroElement) may raise exceptions during rendering if not properly contained within a Figure context.

## Example:
```python
import folium
from folium.plugins import MiniMap

# Create a base map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a minimap with default settings
minimap = MiniMap()
m.add_child(minimap)

# Create a minimap with custom settings
custom_minimap = MiniMap(
    tile_layer="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    position="topright",
    width=200,
    height=200,
    zoom_level_offset=-3
)
m.add_child(custom_minimap)

# Create a minimap with existing TileLayer
tile_layer = folium.TileLayer("OpenStreetMap")
existing_layer_minimap = MiniMap(tile_layer=tile_layer)
m.add_child(existing_layer_minimap)
```

### `folium.plugins.minimap.MiniMap.__init__` · *method*

## Summary:
Initializes a MiniMap plugin instance with configurable display properties and tile layer settings.

## Description:
Configures a minimap control for folium maps with customizable positioning, sizing, and behavior options. This constructor handles the setup of the underlying tile layer and processes configuration options for the minimap's visual and functional properties.

## Args:
    tile_layer (TileLayer or str or None): The tile layer to display in the minimap. If None, creates a default TileLayer. If already a TileLayer instance, uses it directly. Otherwise, treats as a layer specification to create a TileLayer from.
    position (str): Position of the minimap control on the map. Defaults to "bottomright".
    width (int): Width of the minimap in pixels when expanded. Defaults to 150.
    height (int): Height of the minimap in pixels when expanded. Defaults to 150.
    collapsed_width (int): Width of the minimap in pixels when collapsed. Defaults to 25.
    collapsed_height (int): Height of the minimap in pixels when collapsed. Defaults to 25.
    zoom_level_offset (int): Offset applied to the zoom level of the minimap. Defaults to -5.
    zoom_level_fixed (int or None): Fixed zoom level for the minimap. If None, uses dynamic zoom. Defaults to None.
    center_fixed (bool): Whether to fix the center of the minimap. Defaults to False.
    zoom_animation (bool): Whether to enable zoom animation. Defaults to False.
    toggle_display (bool): Whether to enable toggling display. Defaults to False.
    auto_toggle_display (bool): Whether to automatically toggle display. Defaults to False.
    minimized (bool): Whether the minimap starts minimized. Defaults to False.
    **kwargs: Additional keyword arguments passed to the options parser.

## Returns:
    None: This method initializes the instance and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MiniMap"
    - self.tile_layer: Set based on the tile_layer parameter
    - self.options: Set to parsed options dictionary

## Constraints:
    Preconditions:
        - The class must inherit from MacroElement and JSCSSMixin
        - tile_layer parameter must be compatible with TileLayer constructor when not None or TileLayer instance
    Postconditions:
        - self._name is set to "MiniMap"
        - self.tile_layer is always a TileLayer instance
        - self.options is a dictionary with camelCase keys

## Side Effects:
    None: This method performs no I/O operations or external service calls.

