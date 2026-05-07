# `folium.plugins`

## Tree:
plugins/
├── antpath.py
├── beautify_icon.py
├── boat_marker.py
├── dual_map.py
├── feature_group_sub_group.py
├── float_image.py
├── fullscreen.py
├── geocoder.py
├── groupedlayercontrol.py
├── heat_map.py
├── locate_control.py
├── marker_cluster.py
├── measure_control.py
├── minimap.py
├── mouse_position.py
├── pattern.py
├── polyline_offset.py
├── polyline_text_path.py
├── scroll_zoom_toggler.py
├── search.py
├── semicircle.py
├── side_by_side.py
├── tag_filter_button.py
├── terminator.py
├── time_slider_choropleth.py
├── timestamped_geo_json.py
├── timestamped_wmstilelayer.py
└── vectorgrid_protobuf.py

## Role:
Provides extended interactive mapping capabilities for folium maps through specialized plugins that add advanced visualization and user interaction features.

## Description:
The plugins module serves as a collection of specialized extensions to folium's base mapping functionality. These plugins enhance the basic map capabilities by providing advanced visualization techniques, interactive controls, and specialized markers that are not part of folium's core features. This module acts as a centralized location for all folium extension plugins, maintaining a consistent API while offering diverse mapping capabilities.

## Components:
*   **antpath** - Creates animated paths showing movement along routes with customizable speed and styling
*   **beautify_icon** - Enhances marker icons with better styling options including custom colors, shapes, and fonts
*   **boat_marker** - Adds specialized boat markers for maritime applications with rotation and size customization
*   **dual_map** - Enables side-by-side comparison of two different maps with synchronized navigation
*   **feature_group_sub_group** - Provides hierarchical organization of map features through nested feature groups
*   **float_image** - Displays floating images on maps with customizable positioning, sizing, and opacity
*   **fullscreen** - Adds fullscreen toggle functionality to maps with customizable button placement
*   **geocoder** - Integrates geocoding capabilities for converting addresses to coordinates and vice versa
*   **groupedlayercontrol** - Offers advanced layer control with grouping capabilities for organizing map layers
*   **heat_map** - Creates heatmaps from point data for density visualization with customizable color schemes
*   **locate_control** - Adds location detection and tracking controls with accuracy indicators
*   **marker_cluster** - Groups nearby markers to improve performance on dense datasets with customizable clustering algorithms
*   **measure_control** - Provides distance and area measurement tools with real-time calculation display
*   **minimap** - Displays a smaller overview map within the main map with customizable size and position
*   **mouse_position** - Shows real-time mouse coordinates on the map with customizable coordinate formats
*   **pattern** - Adds patterned line styles for enhanced visual representation of routes and boundaries
*   **polyline_offset** - Offsets polylines to create parallel lines for multi-route visualization
*   **polyline_text_path** - Places text along polyline paths for route labeling and annotation
*   **scroll_zoom_toggler** - Controls scroll zoom behavior on maps with enable/disable toggling
*   **search** - Implements search functionality for map features with customizable search parameters
*   **semicircle** - Draws semicircular shapes for geographic visualization with customizable radius and direction
*   **side_by_side** - Creates side-by-side comparison views of maps with synchronized panning and zooming
*   **tag_filter_button** - Adds filtering buttons based on feature tags for dynamic map content filtering
*   **terminator** - Displays day/night terminator on world maps
*   **time_slider_choropleth** - Creates time-varying choropleth maps with slider controls for temporal data visualization
*   **timestamped_geo_json** - Displays GeoJSON data with temporal dimensions and playback controls
*   **timestamped_wmstilelayer** - Shows time-series WMS tile layers with temporal dimension support
*   **vectorgrid_protobuf** - Renders vector grid data using protobuf encoding for efficient large-scale data visualization

## Public API:
*   **antpath.AntPath** - Class for creating animated paths showing movement along routes
*   **beautify_icon.BeautifyIcon** - Class for enhancing marker icons with better styling options
*   **boat_marker.BoatMarker** - Class for adding specialized boat markers for maritime applications
*   **dual_map.DualMap** - Class for enabling side-by-side comparison of two different maps
*   **feature_group_sub_group.FeatureGroupSubGroup** - Class for hierarchical organization of map features
*   **float_image.FloatImage** - Class for displaying floating images on maps
*   **fullscreen.Fullscreen** - Class for adding fullscreen toggle functionality to maps
*   **geocoder.Geocoder** - Class for integrating geocoding capabilities
*   **groupedlayercontrol.GroupedLayerControl** - Class for advanced layer control with grouping
*   **heat_map.HeatMap** - Class for creating heatmaps from point data
*   **locate_control.LocateControl** - Class for location detection and tracking controls
*   **marker_cluster.MarkerCluster** - Class for grouping nearby markers to improve performance
*   **measure_control.MeasureControl** - Class for distance and area measurement tools
*   **minimap.MiniMap** - Class for displaying a smaller overview map within the main map
*   **mouse_position.MousePosition** - Class for showing real-time mouse coordinates
*   **pattern.Pattern** - Class for adding patterned line styles
*   **polyline_offset.PolyLineOffset** - Class for offsetting polylines to create parallel lines
*   **polyline_text_path.PolyLineTextPath** - Class for placing text along polyline paths
*   **scroll_zoom_toggler.ScrollZoomToggler** - Class for controlling scroll zoom behavior
*   **search.Search** - Class for implementing search functionality for map features
*   **semicircle.Semicircle** - Class for drawing semicircular shapes
*   **side_by_side.SideBySide** - Class for creating side-by-side comparison views
*   **tag_filter_button.TagFilterButton** - Class for adding filtering buttons based on feature tags
*   **terminator.Terminator** - Class for displaying day/night terminator
*   **time_slider_choropleth.TimeSliderChoropleth** - Class for time-varying choropleth maps
*   **timestamped_geo_json.TimestampedGeoJson** - Class for displaying temporal GeoJSON data
*   **timestamped_wmstilelayer.TimestampedWmsTileLayer** - Class for showing time-series WMS tile layers
*   **vectorgrid_protobuf.VectorGridProtobuf** - Class for rendering vector grid data using protobuf encoding

## Dependencies:
*   **Internal**: folium.core, folium.map, folium.features, folium.html
*   **External**: folium, branca, numpy, pandas (varies by plugin)

## Constraints:
*   All plugins require proper initialization with valid folium map objects
*   Some plugins may have specific data format requirements (e.g., timestamped data for time-based plugins)
*   Plugins should be added to maps in the correct order to avoid rendering conflicts
*   Certain plugins may have browser compatibility considerations
*   Time-based plugins require properly formatted timestamp data in ISO format
*   Marker cluster plugins require appropriate clustering configuration for optimal performance

---

## Files

- [`antpath.py`](plugins/antpath.md)
- [`beautify_icon.py`](plugins/beautify_icon.md)
- [`boat_marker.py`](plugins/boat_marker.md)
- [`dual_map.py`](plugins/dual_map.md)
- [`feature_group_sub_group.py`](plugins/feature_group_sub_group.md)
- [`float_image.py`](plugins/float_image.md)
- [`fullscreen.py`](plugins/fullscreen.md)
- [`geocoder.py`](plugins/geocoder.md)
- [`groupedlayercontrol.py`](plugins/groupedlayercontrol.md)
- [`heat_map.py`](plugins/heat_map.md)
- [`locate_control.py`](plugins/locate_control.md)
- [`marker_cluster.py`](plugins/marker_cluster.md)
- [`measure_control.py`](plugins/measure_control.md)
- [`minimap.py`](plugins/minimap.md)
- [`mouse_position.py`](plugins/mouse_position.md)
- [`pattern.py`](plugins/pattern.md)
- [`polyline_offset.py`](plugins/polyline_offset.md)
- [`polyline_text_path.py`](plugins/polyline_text_path.md)
- [`scroll_zoom_toggler.py`](plugins/scroll_zoom_toggler.md)
- [`search.py`](plugins/search.md)
- [`semicircle.py`](plugins/semicircle.md)
- [`side_by_side.py`](plugins/side_by_side.md)
- [`tag_filter_button.py`](plugins/tag_filter_button.md)
- [`terminator.py`](plugins/terminator.md)
- [`time_slider_choropleth.py`](plugins/time_slider_choropleth.md)
- [`timestamped_geo_json.py`](plugins/timestamped_geo_json.md)
- [`timestamped_wmstilelayer.py`](plugins/timestamped_wmstilelayer.md)
- [`vectorgrid_protobuf.py`](plugins/vectorgrid_protobuf.md)

