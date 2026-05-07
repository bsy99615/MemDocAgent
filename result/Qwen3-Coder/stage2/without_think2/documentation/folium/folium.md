# `folium`

## Repository Overview

### Tree Structure
```
folium/
└── folium/
```

### Purpose
Folium is a Python library that enables the creation of interactive Leaflet maps from Python environments. It simplifies the process of visualizing geospatial data by providing a high-level interface to Leaflet.js, a popular JavaScript library for interactive maps. Folium allows developers to create maps with various layers, markers, polygons, heatmaps, and other geospatial visualizations directly from Python code.

### Target Users
- Data scientists and analysts working with geospatial data
- Developers building web applications with map visualizations
- Researchers creating interactive geographic dashboards
- Anyone needing to visualize spatial data in an interactive web format

### Position in Ecosystem
Folium serves as a bridge between Python-based data processing workflows and interactive web mapping. It functions as a standalone visualization library that integrates seamlessly with popular Python data science tools like pandas, GeoPandas, and NumPy. Folium can be used independently or as part of larger data analysis pipelines to create publishable, interactive maps.

### Architecture
Folium follows a layered architecture pattern:
1. **Data Layer**: Handles geospatial data input (GeoJSON, coordinates, etc.)
2. **Rendering Layer**: Converts Python objects into Leaflet-compatible JavaScript
3. **Output Layer**: Generates HTML with embedded JavaScript for browser rendering

The system uses a pipeline approach where data flows from Python objects through transformation layers to produce interactive HTML map outputs.

### Entry Points
1. **API Import**: `import folium` - Provides access to core map creation and visualization classes
2. **Map Creation**: `folium.Map()` - Main entry point for creating base maps
3. **Layer Addition**: Various methods like `add_child()`, `add_layer()` for adding map features

### Core Features
1. **Base Map Creation** - Create interactive Leaflet maps with customizable tiles
2. **Marker Support** - Add markers with popups and tooltips
3. **Geospatial Layers** - Support for polygons, circles, rectangles, and GeoJSON layers
4. **Heatmap Visualization** - Create density heatmaps from point data
5. **Layer Management** - Organize and control visibility of map layers
6. **HTML Output Generation** - Export maps as standalone HTML files or embeddable components

### Dependencies
- **Leaflet.js**: JavaScript mapping library for browser rendering
- **Jinja2**: Template engine for HTML generation
- **Requests**: HTTP client for fetching map tiles
- **NumPy**: Numerical operations for coordinate handling
- **Pandas**: Data manipulation for geospatial datasets

### Configuration
Folium supports configuration through:
- Map center coordinates and zoom levels
- Tile provider selection
- Layer opacity and visibility settings
- Custom CSS styling options

### Extension Points
1. **Custom Layers**: Extend with custom Leaflet layer implementations
2. **Tile Providers**: Add new tile providers via configuration
3. **Plugins**: Integrate with Leaflet plugins through custom layer classes
4. **Template Customization**: Override Jinja2 templates for HTML output

---

## Modules

- [`folium`](folium.md)
- [`folium/plugins`](folium/plugins.md)

