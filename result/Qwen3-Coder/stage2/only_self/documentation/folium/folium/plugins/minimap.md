# `minimap.py`

## `folium.plugins.minimap.MiniMap` · *class*

## Summary:
A minimap control that displays a smaller version of the main map for navigation purposes.

## Description:
The MiniMap class creates a navigational control that displays a smaller view of the main map, allowing users to quickly navigate and orient themselves within the larger map area. It is designed to be added to folium maps as a control element and provides various configuration options for positioning, sizing, and behavior.

This class inherits from JSCSSMixin and MacroElement, making it compatible with folium's rendering system and automatically managing the inclusion of required JavaScript and CSS resources from the leaflet-minimap library.

## State:
- tile_layer: TileLayer object representing the base layer displayed in the minimap
- options: Dictionary of configuration options parsed from initialization parameters
- _name: String identifier set to "MiniMap" for internal tracking

## Lifecycle:
- Creation: Instantiate with optional tile_layer and configuration parameters
- Usage: Add to a folium.Map instance using add_child() method
- Rendering: During map rendering, the JSCSSMixin automatically includes required JS/CSS resources

## Method Map:
```mermaid
graph TD
    A[MiniMap.__init__] --> B[super().__init__()]
    B --> C[Set _name to "MiniMap"]
    C --> D{tile_layer is None?}
    D -- Yes --> E[Create default TileLayer()]
    D -- No --> F{tile_layer is TileLayer?}
    F -- Yes --> G[Use tile_layer directly]
    F -- No --> H[Create TileLayer(tile_layer)]
    G --> I[Parse options with parse_options()]
    H --> I
    I --> J[Store options]
```

## Raises:
- None explicitly raised by MiniMap.__init__
- However, underlying exceptions from TileLayer construction or parse_options could propagate

## Example:
```python
import folium

# Create a basic map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a minimap with default settings
minimap = folium.plugins.Minimap()
m.add_child(minimap)

# Create a minimap with custom settings
custom_minimap = folium.plugins.Minimap(
    position='topright',
    width=200,
    height=200,
    zoom_level_offset=-3
)
m.add_child(custom_minimap)

# Render the map
m.save('map.html')
```

### `folium.plugins.minimap.MiniMap.__init__` · *method*

## Summary:
Initializes a MiniMap control with configurable positioning, sizing, and behavior options.

## Description:
Configures a minimap control that displays a smaller version of the main map for navigation purposes. This method sets up the internal state of the MiniMap object including the base tile layer, positioning, dimensions, and various behavioral options. The minimap can be customized through numerous parameters affecting its appearance and functionality.

## Args:
    tile_layer (TileLayer or str or None, optional): Base layer for the minimap. If None, creates a default TileLayer. If already a TileLayer instance, uses it directly. Otherwise, wraps the argument in a TileLayer. Defaults to None.
    position (str, optional): Position of the minimap control on the map. Valid values are 'topleft', 'topright', 'bottomleft', 'bottomright'. Defaults to 'bottomright'.
    width (int, optional): Width of the minimap in pixels when expanded. Defaults to 150.
    height (int, optional): Height of the minimap in pixels when expanded. Defaults to 150.
    collapsed_width (int, optional): Width of the minimap in pixels when collapsed. Defaults to 25.
    collapsed_height (int, optional): Height of the minimap in pixels when collapsed. Defaults to 25.
    zoom_level_offset (int, optional): Offset applied to the zoom level of the minimap relative to the main map. Defaults to -5.
    zoom_level_fixed (int or None, optional): Fixed zoom level for the minimap. If None, uses dynamic zoom level. Defaults to None.
    center_fixed (bool, optional): Whether to fix the center of the minimap. Defaults to False.
    zoom_animation (bool, optional): Whether to enable smooth zoom transitions. Defaults to False.
    toggle_display (bool, optional): Whether to show a toggle button to expand/collapse the minimap. Defaults to False.
    auto_toggle_display (bool, optional): Whether to automatically toggle display based on map size. Defaults to False.
    minimized (bool, optional): Whether the minimap starts in minimized state. Defaults to False.
    **kwargs: Additional keyword arguments passed to the parse_options utility for further configuration.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None explicitly raised by this method. Exceptions from underlying TileLayer construction or parse_options may propagate.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "MiniMap"
    - self.tile_layer: Set to a TileLayer instance based on the tile_layer parameter
    - self.options: Set to a dictionary of parsed configuration options

## Constraints:
    Preconditions:
    - All numeric parameters should be non-negative integers where applicable
    - Position parameter must be one of the valid string values
    - tile_layer parameter must be either None, a TileLayer instance, or convertible to a TileLayer
    Postconditions:
    - self._name is set to "MiniMap"
    - self.tile_layer is always a TileLayer instance
    - self.options is always a dictionary with camelCase keys

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

