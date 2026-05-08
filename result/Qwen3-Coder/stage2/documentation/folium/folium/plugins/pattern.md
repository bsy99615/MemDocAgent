# `pattern.py`

## `folium.plugins.pattern.StripePattern` · *class*

## Summary:
A StripePattern class that defines stripe patterns for use in Leaflet map visualizations through the folium framework.

## Description:
The StripePattern class is a specialized element that defines stripe patterns for use in Leaflet-based maps within folium. It inherits from JSCSSMixin and MacroElement, enabling it to manage JavaScript dependencies and integrate with folium's rendering system. This class provides configuration options for creating stripe patterns with customizable angles, weights, colors, and opacities. The pattern is intended to be used as a style definition that can be referenced by other map elements.

## State:
- angle: float, default 0.5 - Rotation angle of the stripes in radians (0.0 to 2π)
- weight: int, default 4 - Width of the stripe lines in pixels (positive integers)
- space_weight: int, default 4 - Width of the spaces between stripes in pixels (positive integers)
- color: str, default "#000000" - Color of the stripe lines in hex format
- space_color: str, default "#ffffff" - Color of the spaces between stripes in hex format
- opacity: float, default 0.75 - Opacity of the stripe lines (0.0 to 1.0)
- space_opacity: float, default 0.0 - Opacity of the spaces between stripes (0.0 to 1.0)
- parent_map: None or Map instance - Reference to the parent map object, set during rendering via get_obj_in_upper_tree
- _name: str, fixed value "StripePattern" - Name identifier for the pattern type
- options: dict - Processed options dictionary containing all pattern configuration parameters, converted to camelCase keys via parse_options
- _template: Template instance - Jinja2 template for rendering the pattern (empty in current implementation)

## Lifecycle:
- Creation: Instantiate with optional styling parameters. The class automatically registers its JavaScript dependency through default_js.
- Usage: Add to a folium Map or compatible container. During rendering, the render() method locates the parent Map and prepares the pattern for display.
- Destruction: No explicit cleanup required; relies on parent class lifecycle management.

## Method Map:
```mermaid
graph TD
    A[StripePattern.__init__] --> B[super().__init__]
    B --> C[Set _name]
    C --> D[parse_options]
    D --> E[Set options and parent_map=None]
    E --> F[StripePattern.render]
    F --> G[get_obj_in_upper_tree]
    G --> H[Set parent_map]
    H --> I[super().render]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if not properly contained within a Map context (via get_obj_in_upper_tree or JSCSSMixin)

## Example:
```python
import folium
from folium.plugins import StripePattern

# Create a map
m = folium.Map([0, 0], zoom_start=2)

# Create a stripe pattern with custom styling
pattern = StripePattern(
    angle=0.785,  # 45 degrees in radians
    weight=6,
    color="#ff0000",
    opacity=0.8
)

# The pattern would typically be referenced by other map elements
# that support pattern styling, such as polygon fills or markers
```

### `folium.plugins.pattern.StripePattern.__init__` · *method*

## Summary:
Initializes a StripePattern object with configurable styling options for map overlays.

## Description:
Constructs a StripePattern instance that defines visual stripe patterns for map elements. This method sets up the object's name, processes styling parameters through folium's standard option parsing mechanism, and initializes the parent map reference to None.

## Args:
    angle (float, optional): Rotation angle of the stripes in radians. Defaults to 0.5.
    weight (int, optional): Width of the stripe lines in pixels. Defaults to 4.
    space_weight (int, optional): Width of the spacing between stripes in pixels. Defaults to 4.
    color (str, optional): Color of the stripe lines in hex format. Defaults to "#000000".
    space_color (str, optional): Color of the background/spaces in hex format. Defaults to "#ffffff".
    opacity (float, optional): Opacity of the stripe lines (0.0 to 1.0). Defaults to 0.75.
    space_opacity (float, optional): Opacity of the background/spaces (0.0 to 1.0). Defaults to 0.0.
    **kwargs: Additional styling options that will be converted to camelCase keys.

## Returns:
    None: This method initializes the object state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "StripePattern"
        - self.options: Set to parsed styling options dictionary
        - self.parent_map: Set to None

## Constraints:
    Preconditions:
        - All provided arguments must be compatible with their expected types
        - Color values should be valid hex color codes
        - Numeric values should be within reasonable ranges for pixel measurements
    Postconditions:
        - The object is properly initialized with default or provided values
        - self._name is set to "StripePattern"
        - self.options contains all valid styling parameters in camelCase format
        - self.parent_map is initialized to None

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `folium.plugins.pattern.StripePattern.render` · *method*

## Summary:
Sets the parent map reference and invokes the parent rendering logic for a StripePattern element.

## Description:
This method establishes the relationship between the StripePattern instance and its containing Map by traversing upward through the object hierarchy to find the parent Map instance. It then delegates to the parent class's render method to complete the rendering process. This approach allows the pattern to be properly integrated into the map's rendering pipeline and ensures that required JavaScript/CSS resources are included.

The method is part of the rendering lifecycle for folium map elements, specifically designed to ensure that pattern elements can access their parent map context for proper integration with Leaflet's pattern functionality.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method for rendering configuration.

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: Raised by get_obj_in_upper_tree when no parent Map object is found in the object hierarchy.

## State Changes:
    Attributes READ: 
        - None explicitly read
    
    Attributes WRITTEN:
        - self.parent_map: Set to the parent Map object found by get_obj_in_upper_tree

## Constraints:
    Preconditions:
        - The StripePattern instance must be added to a Map object before rendering
        - The parent Map object must be reachable through the _parent hierarchy
        - The instance must be contained within a Figure context for proper rendering
    
    Postconditions:
        - self.parent_map is set to the parent Map instance
        - The parent render method is called with provided kwargs

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state beyond setting the parent_map attribute.

## `folium.plugins.pattern.CirclePattern` · *class*

## Summary:
A pattern class for creating circular patterns in folium maps using Leaflet.pattern plugin.

## Description:
The CirclePattern class represents a circular pattern that can be used to style map features in folium visualizations. It leverages the Leaflet.pattern JavaScript library to create repeating circular patterns on map elements. This class is designed to be used as part of folium's plugin system for advanced map styling capabilities.

## State:
- width: int, default 20 - Width of the pattern tile in pixels
- height: int, default 20 - Height of the pattern tile in pixels  
- radius: int, default 12 - Radius of the circle in the pattern
- weight: float, default 2.0 - Stroke width of the circle
- color: str, default "#3388ff" - Stroke color of the circle
- fill_color: str, default "#3388ff" - Fill color of the circle
- opacity: float, default 0.75 - Stroke opacity of the circle
- fill_opacity: float, default 0.5 - Fill opacity of the circle
- parent_map: str or None - Name of the parent map instance, set during rendering

## Lifecycle:
- Creation: Instantiate with optional pattern parameters to define circle properties
- Usage: Add to a folium Map instance, then render to include JavaScript dependencies
- Destruction: No explicit cleanup required, relies on parent element's lifecycle management

## Method Map:
```mermaid
graph TD
    A[CirclePattern.__init__] --> B[super().__init__]
    B --> C[parse_options for circle]
    C --> D[parse_options for pattern]
    D --> E[Set parent_map to None]
    
    F[CirclePattern.render] --> G[get_obj_in_upper_tree]
    G --> H[Get Map instance name]
    H --> I[Set parent_map]
    I --> J[super().render]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if not properly contained in a Map context

## Example:
```python
import folium
from folium.plugins import CirclePattern

# Create a map
m = folium.Map([0, 0], zoom_start=2)

# Create a circle pattern with custom properties
pattern = CirclePattern(
    width=30,
    height=30,
    radius=15,
    weight=3.0,
    color="red",
    fill_color="yellow"
)

# Add pattern to map (this will automatically include required JS)
m.add_child(pattern)

# Render the map
m.save("pattern_map.html")
```

### `folium.plugins.pattern.CirclePattern.__init__` · *method*

## Summary:
Initializes a CirclePattern object with configurable dimensions, visual properties, and rendering options for use in folium map patterns.

## Description:
Configures the CirclePattern instance by setting up its visual characteristics including size, radius, stroke properties, colors, and opacity values. This constructor prepares the pattern for rendering within folium map contexts by establishing the necessary options dictionaries and initializing core attributes. The pattern defines a circular shape that can be used as a fill pattern in map layers.

## Args:
    width (int): Width of the pattern area in pixels. Defaults to 20.
    height (int): Height of the pattern area in pixels. Defaults to 20.
    radius (int): Radius of the circle shape in pixels. Defaults to 12.
    weight (float): Stroke width of the circle in pixels. Defaults to 2.0.
    color (str): Border color of the circle in hex format. Defaults to "#3388ff".
    fill_color (str): Fill color of the circle in hex format. Defaults to "#3388ff".
    opacity (float): Border opacity of the circle (0.0 to 1.0). Defaults to 0.75.
    fill_opacity (float): Fill opacity of the circle (0.0 to 1.0). Defaults to 0.5.

## Returns:
    None: This method initializes the object and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "CirclePattern" string
    - self.options_pattern_circle: Set to parsed options dictionary for circle properties
    - self.options_pattern: Set to parsed options dictionary for pattern dimensions
    - self.parent_map: Set to None

## Constraints:
    Preconditions:
    - All numeric parameters should be non-negative values
    - Color parameters should be valid hex color codes
    - Opacity parameters should be between 0.0 and 1.0 inclusive
    Postconditions:
    - self._name is set to "CirclePattern"
    - Both options dictionaries are properly initialized with parsed values
    - parent_map is initialized to None

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `folium.plugins.pattern.CirclePattern.render` · *method*

## Summary:
Retrieves the parent map reference and delegates rendering to the parent class.

## Description:
This method establishes the parent map reference for the circle pattern by traversing upward through the object hierarchy to find the containing Map instance. It then delegates the actual rendering process to the parent class's render method. This is part of the standard rendering pipeline for folium map elements that need to maintain hierarchical relationships.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method.

## Returns:
    None: This method does not return any value.

## Raises:
    ValueError: When the parent Map object cannot be found in the object hierarchy, as raised by get_obj_in_upper_tree.

## State Changes:
    Attributes READ: 
        - None explicitly read from self attributes
    Attributes WRITTEN:
        - self.parent_map (set to the name of the parent Map object)

## Constraints:
    Preconditions:
        - The CirclePattern instance must be properly contained within a Map hierarchy
        - The instance must have a _parent attribute to enable traversal
    Postconditions:
        - self.parent_map will be set to the name of the parent Map object
        - The parent render method will be called with the provided kwargs

## Side Effects:
    None: This method does not perform any I/O operations or mutate external objects. It only sets an internal attribute and calls a parent method.

