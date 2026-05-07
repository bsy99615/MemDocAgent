# `pattern.py`

## `folium.plugins.pattern.StripePattern` · *class*

## Summary:
StripePattern is a folium plugin class that defines stripe patterns for use in Leaflet maps through the Leaflet.pattern JavaScript library.

## Description:
StripePattern enables the creation of custom striped visual patterns for map features in folium. It inherits from JSCSSMixin and MacroElement to integrate with folium's rendering system and automatically manage JavaScript dependencies. This class is primarily intended for internal use by folium's plugin system to create patterned map elements, particularly for styling polygons and other geometric features with striped appearances.

## State:
- _name (str): Set to "StripePattern" to identify this element type in folium's rendering system
- options (dict): Configuration dictionary for stripe pattern properties (angle, weight, colors, etc.), processed via parse_options to convert snake_case to camelCase keys
- parent_map (Map or None): Reference to the parent Map object that contains this pattern, set during rendering via get_obj_in_upper_tree
- default_js (list): Class attribute containing the URL for the Leaflet.pattern JavaScript library dependency
- _template (Template): Class attribute containing the Jinja2 template for rendering (currently empty)

## Lifecycle:
- Creation: Instantiate with optional pattern configuration parameters (angle, weight, colors, etc.) through __init__
- Usage: Typically added internally to folium Map objects; during rendering, render() method identifies parent Map and calls parent rendering
- Destruction: No explicit cleanup required; relies on parent Element's lifecycle management

## Method Map:
```mermaid
graph TD
    A[StripePattern.__init__] --> B[super().__init__()]
    B --> C[Set _name to "StripePattern"]
    C --> D[Process options via parse_options]
    D --> E[Initialize parent_map to None]
    
    F[StripePattern.render] --> G[Find parent Map via get_obj_in_upper_tree]
    G --> H[Set parent_map reference]
    H --> I[Call super().render() for standard rendering]
```

## Raises:
- ValueError: May be raised by get_obj_in_upper_tree if the pattern is not contained within a Map object during rendering
- AssertionError: Could potentially be raised by parent classes during rendering if validation fails

## Example:
```python
import folium

# Create a map
m = folium.Map([0, 0], zoom_start=2)

# Create a stripe pattern (typically used internally by folium plugins)
pattern = folium.plugins.StripePattern(
    angle=45,
    weight=6,
    space_weight=2,
    color="#ff0000",
    space_color="#ffff00",
    opacity=0.8
)

# Add pattern to map (this would typically be handled by folium's internal systems)
# m.add_child(pattern)  # Not typically called directly

# Render the map
m.save("map_with_pattern.html")
```

### `folium.plugins.pattern.StripePattern.__init__` · *method*

## Summary:
Initializes a StripePattern object with configurable styling options for creating striped patterns in Folium maps.

## Description:
Configures the StripePattern instance by setting its name, parsing styling options, and initializing the parent map reference. This method establishes the foundational properties needed for rendering stripe patterns on map elements.

## Args:
    angle (float, optional): Rotation angle of the stripes in radians. Defaults to 0.5.
    weight (int, optional): Width of the solid stripes. Defaults to 4.
    space_weight (int, optional): Width of the transparent spaces between stripes. Defaults to 4.
    color (str, optional): Color of the solid stripes in hex format. Defaults to "#000000".
    space_color (str, optional): Color of the transparent spaces in hex format. Defaults to "#ffffff".
    opacity (float, optional): Opacity of the solid stripes (0.0 to 1.0). Defaults to 0.75.
    space_opacity (float, optional): Opacity of the transparent spaces (0.0 to 1.0). Defaults to 0.0.
    **kwargs: Additional keyword arguments passed to the parse_options function for further customization.

## Returns:
    None: This method initializes the object's attributes but does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "StripePattern" string
    - self.options: Set to parsed dictionary of styling options
    - self.parent_map: Set to None

## Constraints:
    Preconditions:
    - All provided arguments must be compatible with their respective types
    - The angle parameter should be a numeric value representing radians
    - Color parameters should be valid hex color codes
    - Opacity parameters should be numeric values between 0.0 and 1.0
    
    Postconditions:
    - The object's _name attribute is set to "StripePattern"
    - The options dictionary contains properly formatted camelCase keys
    - The parent_map attribute is initialized to None

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `folium.plugins.pattern.StripePattern.render` · *method*

## Summary:
Sets the parent map reference and renders the pattern element within the map's rendering context.

## Description:
This method establishes the parent map relationship for the pattern element and delegates rendering to the parent class. It is called during the map rendering lifecycle when the pattern needs to be included in the final HTML output. The method ensures that the pattern element has proper access to its containing map context before proceeding with standard rendering.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method

## Returns:
    None: This method does not return a value

## Raises:
    ValueError: When get_obj_in_upper_tree cannot find a Map ancestor in the object hierarchy
    AssertionError: When the element is not properly contained within a Figure during rendering

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.parent_map (assigned the result of get_obj_in_upper_tree)

## Constraints:
    Preconditions: The pattern element must be added to a Map object's children hierarchy and must have a `_parent` attribute
    Postconditions: The self.parent_map attribute is set to the containing Map instance

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects

## `folium.plugins.pattern.CirclePattern` · *class*

## Summary:
CirclePattern is a folium plugin element that defines circular pattern configuration options for map rendering.

## Description:
CirclePattern is a specialized folium element that prepares and stores configuration options for circular patterns used in map rendering. It inherits from JSCSSMixin and MacroElement, making it compatible with folium's rendering system. This class is designed to be added to folium Map objects and provides pattern configuration data that can be referenced by other map elements during the rendering process. It handles the setup of circular pattern properties including dimensions, radius, stroke, and fill characteristics.

## State:
- _name: str - Set to "CirclePattern" to identify the element type
- options_pattern_circle: dict - Configuration options for the circular pattern including x, y, weight, radius, color, fill_color, opacity, fill_opacity, and fill
- options_pattern: dict - Configuration options for the pattern dimensions including width and height
- parent_map: str or None - Stores the name of the parent Map object when rendered, initially set to None

## Lifecycle:
- Creation: Instantiate with optional parameters for pattern dimensions and styling
- Usage: Add to a folium Map object using add_child() method, then render to HTML
- Destruction: Managed automatically by Python garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[CirclePattern.__init__] --> B[super().__init__()]
    B --> C[Set _name = "CirclePattern"]
    C --> D[Configure options_pattern_circle]
    D --> E[Configure options_pattern]
    E --> F[Set parent_map = None]
    
    G[CirclePattern.render] --> H[get_obj_in_upper_tree(self, Map)]
    H --> I[Get parent map name]
    I --> J[Set parent_map]
    J --> K[super().render(**kwargs)]
```

## Raises:
- ValueError: Raised by get_obj_in_upper_tree when attempting to find a parent Map object during rendering if the element is not properly contained within a Map
- AssertionError: May be raised by parent classes during rendering if validation fails

## Example:
```python
import folium
from folium.plugins import CirclePattern

# Create a map
m = folium.Map([0, 0], zoom_start=2)

# Create a circle pattern with custom styling
pattern = CirclePattern(
    width=30,
    height=30,
    radius=15,
    weight=3.0,
    color="#ff0000",
    fill_color="#00ff00",
    opacity=0.8,
    fill_opacity=0.6
)

# Add pattern to map
m.add_child(pattern)

# The pattern configuration will be made available for use in other map elements
# that support pattern fills during the rendering process
```

### `folium.plugins.pattern.CirclePattern.__init__` · *method*

## Summary:
Initializes a CirclePattern object with configurable dimensions, visual properties, and rendering options for circular patterns in Folium maps.

## Description:
Configures the CirclePattern instance by setting up its name, visual properties, and pattern dimensions. This method establishes the foundational configuration for rendering circular patterns using Folium's pattern system, preparing the object for integration with map elements and JavaScript rendering.

## Args:
    width (int, optional): Width of the pattern area in pixels. Defaults to 20.
    height (int, optional): Height of the pattern area in pixels. Defaults to 20.
    radius (int, optional): Radius of the circle in pixels. Defaults to 12.
    weight (float, optional): Stroke weight of the circle outline in pixels. Defaults to 2.0.
    color (str, optional): Color of the circle stroke. Defaults to "#3388ff".
    fill_color (str, optional): Fill color of the circle. Defaults to "#3388ff".
    opacity (float, optional): Opacity of the circle stroke (0.0 to 1.0). Defaults to 0.75.
    fill_opacity (float, optional): Opacity of the circle fill (0.0 to 1.0). Defaults to 0.5.

## Returns:
    None: This method initializes the object's attributes and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "CirclePattern"
    - self.options_pattern_circle: Configured with circle-specific rendering options
    - self.options_pattern: Configured with pattern dimensions
    - self.parent_map: Initialized to None

## Constraints:
    Preconditions:
    - All numeric parameters (width, height, radius, weight, opacity, fill_opacity) should be non-negative
    - Color parameters should be valid CSS color strings
    - Parameters are validated through the parse_options function

    Postconditions:
    - The object is properly initialized with default or provided values
    - All configuration options are stored in the appropriate attribute dictionaries
    - The parent_map attribute is initialized to None

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `folium.plugins.pattern.CirclePattern.render` · *method*

## Summary:
Sets the parent map reference for the CirclePattern and delegates rendering to the parent class.

## Description:
This method establishes the connection between the CirclePattern instance and its containing Map object by retrieving the parent Map from the object hierarchy and storing its name. It then invokes the parent class's render method to complete the rendering process. This method is part of the rendering lifecycle for folium map elements, ensuring proper hierarchical linking before rendering occurs. The method uses `get_obj_in_upper_tree` to traverse up the object hierarchy to find the containing Map instance.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method

## Returns:
    None

## Raises:
    ValueError: When no parent Map object can be found in the object hierarchy, which occurs when the CirclePattern is not properly embedded within a Map structure

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.parent_map

## Constraints:
    Preconditions: The CirclePattern instance must be properly embedded within a Map hierarchy, and the object must have a `_parent` attribute to enable traversal
    Postconditions: The self.parent_map attribute is set to the name of the parent Map object returned by `get_obj_in_upper_tree`

## Side Effects:
    I/O: May trigger template rendering operations through the parent class
    External service calls: None
    Mutations to objects outside self: None

