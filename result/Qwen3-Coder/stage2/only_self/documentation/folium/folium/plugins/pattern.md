# `pattern.py`

## `folium.plugins.pattern.StripePattern` · *class*

## Summary:
A Folium plugin class that creates stripe patterns for use in Leaflet maps via the Leaflet.pattern library.

## Description:
StripePattern is a specialized Folium element that generates stripe patterns for map features using the Leaflet.pattern JavaScript library. It allows users to define various visual properties of stripe patterns such as angle, weight, colors, and opacities. This class is intended to be used as part of the folium.plugins module ecosystem for advanced map styling capabilities.

The class inherits from JSCSSMixin to handle JavaScript/CSS resource loading and MacroElement for standard Folium element behavior. It integrates with Leaflet's pattern drawing capabilities through the external leaflet.pattern.js library.

## State:
- _name: str - Set to "StripePattern" to identify this element type
- options: dict - Configuration options parsed from constructor parameters using parse_options, including:
  * angle: float - Pattern angle in radians (default: 0.5)
  * weight: int - Width of the stripes (default: 4)
  * space_weight: int - Width of the spaces between stripes (default: 4)
  * color: str - Color of the stripes (default: "#000000")
  * space_color: str - Color of the spaces between stripes (default: "#ffffff")
  * opacity: float - Opacity of the stripes (default: 0.75)
  * space_opacity: float - Opacity of the spaces between stripes (default: 0.0)
- parent_map: Map or None - Reference to the parent Map object, set during rendering

## Lifecycle:
- Creation: Instantiate with optional configuration parameters to customize the stripe pattern appearance
- Usage: Add to a Folium Map or FeatureGroup using add_child() method, then render the map
- Destruction: No special cleanup required; relies on parent element lifecycle management

## Method Map:
```mermaid
graph TD
    A[StripePattern.__init__] --> B[super().__init__()]
    B --> C[parse_options for configuration]
    C --> D[Set _name to "StripePattern"]
    D --> E[Set parent_map to None]
    
    F[StripePattern.render] --> G[get_obj_in_upper_tree(self, Map)]
    G --> H[Set parent_map reference]
    H --> I[super().render(**kwargs)]
```

## Raises:
- ValueError: When get_obj_in_upper_tree fails to find a Map instance during render() execution
- AssertionError: Potentially raised by parent classes during initialization or rendering if validation fails

## Example:
```python
import folium
from folium.plugins import StripePattern

# Create a map
m = folium.Map([0, 0], zoom_start=2)

# Create a stripe pattern with custom settings
pattern = StripePattern(
    angle=0.785,  # 45 degrees in radians
    weight=6,
    space_weight=2,
    color="#ff0000",
    space_color="#ffff00",
    opacity=0.8
)

# Add pattern to map
m.add_child(pattern)

# Render the map (this will automatically include the pattern)
m.save("map_with_pattern.html")
```

### `folium.plugins.pattern.StripePattern.__init__` · *method*

## Summary:
Initializes a StripePattern object with configurable styling options for creating striped patterns in folium maps.

## Description:
Configures a StripePattern instance with visual properties such as angle, weight, colors, and opacities for rendering striped patterns on map overlays. This method sets up the pattern's configuration options and establishes its identity within the folium rendering system by calling the parent class initializer.

## Args:
    angle (float, optional): Rotation angle of the stripes in radians. Defaults to 0.5.
    weight (int, optional): Width of the stripe lines in pixels. Defaults to 4.
    space_weight (int, optional): Width of the spaces between stripes in pixels. Defaults to 4.
    color (str, optional): Color of the stripe lines in hex format. Defaults to "#000000".
    space_color (str, optional): Color of the spaces between stripes in hex format. Defaults to "#ffffff".
    opacity (float, optional): Opacity of the stripe lines (0.0 to 1.0). Defaults to 0.75.
    space_opacity (float, optional): Opacity of the spaces between stripes (0.0 to 1.0). Defaults to 0.0.
    **kwargs: Additional keyword arguments passed to the parent class initialization.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "StripePattern" to identify the element type
    - self.options: Set to parsed configuration options dictionary with camelCase keys
    - self.parent_map: Set to None initially

## Constraints:
    Preconditions:
    - All numeric parameters should be non-negative values
    - Color parameters should be valid hex color codes
    - Opacity parameters should be between 0.0 and 1.0 inclusive
    Postconditions:
    - The object is properly initialized with default or provided configuration
    - The _name attribute is set to "StripePattern"
    - The options dictionary contains properly formatted camelCase keys via parse_options()
    - Parent class initialization is completed successfully

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal object state.

### `folium.plugins.pattern.StripePattern.render` · *method*

## Summary:
Establishes the parent Map reference and manages JavaScript/CSS resource inclusion for the StripePattern element.

## Description:
This method performs two key functions during the rendering lifecycle: first, it identifies and stores the parent Map object by traversing upward through the element hierarchy using `get_obj_in_upper_tree`; second, it delegates rendering to the parent class (`JSCSSMixin.render`) which handles JavaScript and CSS resource management. This ensures the pattern element has proper context and dependencies when rendered in a folium map.

The method is separated from inline logic to maintain clean separation of concerns and enable proper inheritance chain execution. It's called automatically during the rendering process when the element is added to a Map.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method for further processing

## Returns:
    None: This method does not return a value

## Raises:
    ValueError: When the parent Map object cannot be found in the element hierarchy (raised by `get_obj_in_upper_tree`)
    AssertionError: When the element is not contained within a Figure instance (raised by `JSCSSMixin.render`)

## State Changes:
    Attributes READ: 
        - self._parent (inherited from parent classes)
        - self.default_js (inherited from JSCSSMixin)
        - self.default_css (inherited from JSCSSMixin)
    
    Attributes WRITTEN: 
        - self.parent_map (sets the parent Map reference)

## Constraints:
    Preconditions:
        - The StripePattern instance must be added to a Map hierarchy before rendering
        - The instance must have a valid `_parent` chain leading to a Map object
        - The instance must be contained within a Figure instance for proper JS/CSS handling
    
    Postconditions:
        - self.parent_map will contain a reference to the parent Map object
        - All JavaScript and CSS dependencies are added to the figure's header
        - The parent render method is called successfully

## Side Effects:
    - Modifies the figure's header by adding JavaScript and CSS link elements (via JSCSSMixin.render)
    - Sets the self.parent_map attribute to reference the parent Map object

## `folium.plugins.pattern.CirclePattern` · *class*

## Summary:
A Folium plugin class for defining circular patterns in Leaflet maps using the leaflet.pattern.js library.

## Description:
CirclePattern is an internal Folium plugin class designed to define circular pattern configurations for use with Leaflet's pattern plugin. It extends JSCSSMixin and MacroElement to integrate with Folium's rendering system and automatically includes the required leaflet.pattern.js JavaScript library. This class is typically used internally by other Folium components to define reusable circular pattern styles for map features like polygons or markers with pattern fills.

## State:
- width (int): Width of the pattern tile in pixels, defaults to 20
- height (int): Height of the pattern tile in pixels, defaults to 20  
- radius (int): Radius of the circle within the pattern, defaults to 12
- weight (float): Stroke width of the circle outline, defaults to 2.0
- color (str): Color of the circle stroke, defaults to "#3388ff" (blue)
- fill_color (str): Fill color of the circle, defaults to "#3388ff" (blue)
- opacity (float): Opacity of the circle stroke, defaults to 0.75
- fill_opacity (float): Opacity of the circle fill, defaults to 0.5
- parent_map (Map or None): Reference to the parent Map object, set during rendering
- options_pattern_circle (dict): Configuration options for the circle pattern in camelCase format
- options_pattern (dict): Configuration options for the pattern tile dimensions in camelCase format
- _template (Template): Jinja2 template for rendering the pattern (currently empty)

## Lifecycle:
- Creation: Instantiate with optional pattern parameters to define circle properties and tile size
- Usage: Add to a Folium Map instance, then call render() to include JavaScript resources and finalize the pattern definition
- Destruction: No explicit cleanup required; relies on parent element lifecycle management

## Method Map:
```mermaid
graph TD
    A[CirclePattern.__init__] --> B[super().__init__()]
    B --> C[Set _name to "CirclePattern"]
    C --> D[parse_options for circle options]
    D --> E[parse_options for pattern options]
    E --> F[Set parent_map to None]
    
    G[CirclePattern.render] --> H[get_obj_in_upper_tree(self, Map)]
    H --> I[Get parent map name]
    I --> J[super().render(**kwargs)]
```

## Raises:
- ValueError: When get_obj_in_upper_tree cannot find a Map instance in the parent hierarchy during render()

## Example:
```python
import folium
from folium.plugins import CirclePattern

# Create a map
m = folium.Map([0, 0], zoom_start=2)

# Create a circular pattern (typically used internally)
pattern = CirclePattern(
    width=30,
    height=30,
    radius=15,
    weight=3.0,
    color="#ff0000",
    fill_color="#ffff00"
)

# Add pattern to map (this would typically be used internally by folium)
m.add_child(pattern)

# Render the map
pattern.render()
```

### `folium.plugins.pattern.CirclePattern.__init__` · *method*

## Summary:
Initializes a CirclePattern object with configurable circle geometry and pattern dimensions for map rendering.

## Description:
Configures a CirclePattern instance by establishing visual properties for a circular shape and pattern dimensions. This constructor prepares the object for rendering in folium maps by creating two option dictionaries: one for circle-specific properties (geometry, styling) and another for overall pattern sizing. The method sets up the basic configuration needed for drawing circular patterns in map overlays.

## Args:
    width (int, optional): Width of the pattern area in pixels. Defaults to 20.
    height (int, optional): Height of the pattern area in pixels. Defaults to 20.
    radius (int, optional): Radius of the circle in pixels. Defaults to 12.
    weight (float, optional): Stroke width of the circle outline in pixels. Defaults to 2.0.
    color (str, optional): Outline color of the circle in hex format. Defaults to "#3388ff".
    fill_color (str, optional): Fill color of the circle in hex format. Defaults to "#3388ff".
    opacity (float, optional): Opacity of the circle outline (0.0 to 1.0). Defaults to 0.75.
    fill_opacity (float, optional): Opacity of the circle fill (0.0 to 1.0). Defaults to 0.5.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "CirclePattern" 
    - self.options_pattern_circle: Set to parsed options for circle geometry and styling
    - self.options_pattern: Set to parsed options for pattern dimensions
    - self.parent_map: Set to None

## Constraints:
    Preconditions:
    - All numeric parameters should be non-negative values
    - Color parameters should be valid hex color codes
    - Opacity values should be between 0.0 and 1.0
    Postconditions:
    - The object is properly initialized with default or provided parameters
    - The _name attribute is set to "CirclePattern"
    - Both options_pattern_circle and options_pattern dictionaries are populated with appropriate camelCase keys
    - The parent_map attribute is initialized to None

## Side Effects:
    None: This method performs no I/O operations or external service calls.

## Implementation Details:
The options_pattern_circle dictionary includes computed x and y values based on radius and weight, while options_pattern contains width and height parameters. These two dictionaries are used separately during rendering to define both the geometric properties of the circle and the overall pattern dimensions.

### `folium.plugins.pattern.CirclePattern.render` · *method*

## Summary:
Sets the parent map reference and delegates rendering to the parent class.

## Description:
The render method establishes the parent map reference by traversing up the element hierarchy to find the containing Map object, then calls the parent class's render method to handle the actual rendering process. This method is part of the rendering lifecycle for pattern elements in folium maps.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method.

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: When the parent Map object cannot be found in the element hierarchy (via get_obj_in_upper_tree).

## State Changes:
    Attributes READ: 
        - None directly accessed
    
    Attributes WRITTEN: 
        - self.parent_map: Set to the name of the parent Map object

## Constraints:
    Preconditions:
        - The CirclePattern instance must be added to a Map object within the folium tree hierarchy
        - The parent Map object must have a valid get_name() method
    
    Postconditions:
        - self.parent_map is set to the name of the containing Map
        - The rendering process continues through the parent class's render method

## Side Effects:
    - Sets the self.parent_map attribute to the parent Map's name
    - Triggers the parent class's render method which may involve JavaScript/CSS resource handling

