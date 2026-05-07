# `polyline_text_path.py`

## `folium.plugins.polyline_text_path.PolyLineTextPath` · *class*

## Summary:
PolyLineTextPath is a folium map element that renders text along a polyline path using the Leaflet TextPath plugin.

## Description:
PolyLineTextPath enables the display of text labels that follow the path of a polyline on a folium map. It leverages the Leaflet TextPath JavaScript library to achieve this functionality. This class is typically used to annotate routes, paths, or lines on interactive maps with descriptive text that follows the geometric shape of the polyline.

## State:
- _name (str): Class attribute set to "PolyLineTextPath" identifying the element type
- _template (Template): Jinja2 template for rendering the JavaScript component (currently empty)
- default_js (list): Class attribute containing JavaScript dependencies including leaflet-textpath library
- polyline (object): Reference to the polyline object that the text will follow
- text (str): The text string to be displayed along the polyline
- options (dict): Configuration options processed through parse_options for the Leaflet TextPath plugin

## Lifecycle:
- Creation: Instantiate with a polyline object, text string, and optional configuration parameters
- Usage: Add to a folium Map or FeatureGroup using the add_child() method
- Destruction: Managed automatically through folium's element lifecycle management

## Method Map:
```mermaid
graph TD
    A[PolyLineTextPath.__init__] --> B[super().__init__()]
    B --> C[self._name = "PolyLineTextPath"]
    C --> D[self.polyline = polyline]
    D --> E[self.text = text]
    E --> F[self.options = parse_options(...)]
    F --> G[Return initialized instance]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if improperly configured

## Example:
```python
import folium

# Create a map
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Create a polyline
polyline = folium.PolyLine(
    locations=[[40.7128, -74.0060], [40.7589, -73.9851]],
    color='blue'
)

# Create text path along the polyline
text_path = folium.plugins.PolyLineTextPath(
    polyline=polyline,
    text='Route Name',
    repeat=True,
    offset=10
)

# Add both to the map
m.add_child(polyline)
m.add_child(text_path)

# Display the map
m
```

### `folium.plugins.polyline_text_path.PolyLineTextPath.__init__` · *method*

## Summary:
Initializes a PolyLineTextPath element that renders text along a polyline path on a folium map.

## Description:
Configures a PolyLineTextPath instance by storing references to the polyline and text, processing configuration options, and setting up the element's identification. This method establishes the foundational state required for rendering text along a polyline using the Leaflet TextPath plugin.

## Args:
    polyline (object): Reference to a folium polyline object that the text will follow
    text (str): The text string to be displayed along the polyline path
    repeat (bool): Whether to repeat the text along the entire path. Defaults to False
    center (bool): Whether to center the text on the path. Defaults to False
    below (bool): Whether to place the text below the path. Defaults to False
    offset (int): Offset in pixels from the path. Defaults to 0
    orientation (int): Orientation angle in degrees. Defaults to 0
    attributes (dict): Additional HTML attributes for the text element. Defaults to None
    **kwargs: Additional keyword arguments passed to the options parser

## Returns:
    None: This method initializes the object's state but does not return a value

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "PolyLineTextPath" to identify the element type
    - self.polyline: Stores reference to the polyline object
    - self.text: Stores the text string to display
    - self.options: Stores processed configuration options

## Constraints:
    Preconditions:
    - polyline parameter must be a valid folium polyline object
    - text parameter must be a string
    - All keyword arguments must be valid for the parse_options function
    
    Postconditions:
    - self._name is set to "PolyLineTextPath"
    - self.polyline references the provided polyline object
    - self.text contains the provided text string
    - self.options contains processed configuration options

## Side Effects:
    None

