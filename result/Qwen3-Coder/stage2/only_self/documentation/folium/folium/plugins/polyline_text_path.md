# `polyline_text_path.py`

## `folium.plugins.polyline_text_path.PolyLineTextPath` · *class*

## Summary:
A Folium plugin that renders text along a polyline on a Leaflet map using the leaflet-textpath JavaScript library.

## Description:
The PolyLineTextPath class is designed to add text labels that follow the path of a polyline on a map. It extends JSCSSMixin and MacroElement to integrate with Folium's rendering system and provides a bridge to the leaflet-textpath JavaScript library. This allows users to annotate polylines with text that follows their shape, which is useful for labeling routes, paths, or other linear features on maps.

## State:
- _name (str): Class attribute set to "PolyLineTextPath" identifying this element type
- polyline: Reference to the polyline object that the text will follow
- text (str): The text string to be displayed along the polyline
- options (dict): Configuration options processed through parse_options for the leaflet-textpath library
- _template (Template): Jinja2 template for HTML rendering (empty in current implementation)
- default_js (list): List of tuples specifying JavaScript dependencies including leaflet-textpath library

## Lifecycle:
- Creation: Instantiate with a polyline object and text string, plus optional styling parameters
- Usage: Add to a Folium Figure using add_child() method; rendering automatically handles JavaScript/CSS inclusion
- Destruction: Managed by Folium's element lifecycle; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[PolyLineTextPath.__init__] --> B[super().__init__()]
    B --> C[Set _name="PolyLineTextPath"]
    C --> D[Store polyline reference]
    D --> E[Store text string]
    E --> F[Process options via parse_options]
    F --> G[Return initialized instance]
```

## Raises:
- None explicitly raised by __init__
- Inheritance from JSCSSMixin may raise AssertionError if used outside of a Figure context during rendering

## Example:
```python
import folium

# Create a map
m = folium.Map([45.5236, -122.6750], zoom_start=13)

# Create a polyline
polyline = folium.PolyLine(
    locations=[[45.5236, -122.6750], [45.5246, -122.6750]],
    color='blue'
)

# Add text along the polyline
text_path = folium.plugins.PolyLineTextPath(
    polyline=polyline,
    text='Sample Route',
    repeat=True,
    offset=10
)

# Add elements to map
m.add_child(polyline)
m.add_child(text_path)

# Render the map
m.save('map.html')
```

