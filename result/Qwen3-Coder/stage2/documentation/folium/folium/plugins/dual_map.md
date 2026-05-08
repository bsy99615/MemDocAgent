# `dual_map.py`

## `folium.plugins.dual_map.DualMap` · *class*

## Summary:
A dual-map visualization component that displays two synchronized map views side-by-side or vertically for comparison and interactive exploration.

## Description:
The DualMap class creates two synchronized map instances that can be arranged horizontally or vertically, enabling users to compare different map views or interact with the same geographic area from two perspectives. This component is particularly useful for comparing map layers, examining spatial relationships, or providing dual-view navigation capabilities.

The class inherits from JSCSSMixin and MacroElement, providing automatic JavaScript/CSS resource management and map element functionality. It manages two internal Map instances (m1 and m2) that are positioned absolutely and synchronized using the Leaflet.Sync library.

## State:
- m1 (Map): First map instance positioned at the top/left of the container
- m2 (Map): Second map instance positioned at the bottom/right of the container
- children_for_m2 (list): List of child elements to be added to m2, stored as tuples of (child, name, index)
- children_for_m2_copied (list): List of child element IDs that have already been copied to m2 to prevent duplication
- layout (str): Layout orientation, either "horizontal" or "vertical"
- width (str): Width of each map, "50%" for horizontal layout, "100%" for vertical
- height (str): Height of each map, "100%" for horizontal layout, "50%" for vertical

## Lifecycle:
- Creation: Instantiate with location and layout parameters. The constructor initializes two Map instances with appropriate positioning and sizing.
- Usage: Add child elements using add_child(), which automatically adds them to both maps. Call render() to process and synchronize children between maps.
- Destruction: Cleanup is handled automatically through Python's garbage collection when the object is removed from its parent container.

## Method Map:
```mermaid
graph TD
    A[DualMap.__init__] --> B[Set layout validation]
    B --> C[Create m1 Map with layout-specific sizing]
    C --> D[Create m2 Map with layout-specific sizing]
    D --> E[Setup Figure with both maps and self]
    
    F[DualMap.add_child] --> G[m1.add_child]
    G --> H[Store child info for m2 processing]
    
    I[DualMap.render] --> J[Super().render()]
    J --> K[Process children_for_m2]
    K --> L{Child already copied?}
    L -- Yes --> M[Skip]
    L -- No --> N[Deep copy child]
    N --> O{Is LayerControl?}
    O -- Yes --> P[Reset LayerControl]
    P --> Q[Add to m2]
    Q --> R[Render child]
    R --> S[Mark as copied]
    
    T[DualMap.fit_bounds] --> U[m1.fit_bounds]
    U --> V[m2.fit_bounds]
    
    W[DualMap.keep_in_front] --> X[m1.keep_in_front]
    X --> Y[m2.keep_in_front]
```

## Raises:
- ValueError: Raised when layout parameter is not "horizontal" or "vertical"
- AssertionError: Raised when width, height, left, top, or position arguments are passed to the constructor (these are controlled internally)

## Example:
```python
import folium

# Create a dual map with horizontal layout
dual_map = folium.plugins.DualMap(
    location=[40.7128, -74.0060],  # New York City
    layout="horizontal"
)

# Add a marker to both maps
folium.Marker([40.7128, -74.0060], popup="New York City").add_to(dual_map)

# Add different tile layers to each map
folium.TileLayer('OpenStreetMap').add_to(dual_map)
folium.TileLayer('CartoDB positron').add_to(dual_map)

# Render the dual map
html_output = dual_map._repr_html_()
```

### `folium.plugins.dual_map.DualMap.__init__` · *method*

## Summary:
Initializes a dual map visualization with two synchronized map instances arranged either horizontally or vertically.

## Description:
Creates a DualMap instance containing two Map objects that can be displayed side-by-side or stacked vertically. This method sets up the internal structure including two map instances that are positioned absolutely within a container, with configuration options for layout orientation and map initialization parameters.

## Args:
    location (list or tuple, optional): Center coordinates [latitude, longitude] for both maps. Defaults to None.
    layout (str): Layout orientation for the dual maps. Must be either "horizontal" or "vertical". Defaults to "horizontal".
    **kwargs: Additional keyword arguments passed to the underlying Map constructors.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    ValueError: Raised when the layout parameter is not "horizontal" or "vertical".
    AssertionError: Raised when width, height, left, top, or position arguments are passed in kwargs (these are controlled internally).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.m1: First map instance with absolute positioning
    - self.m2: Second map instance with absolute positioning  
    - self.children_for_m2: Empty list for tracking child elements to be added to m2
    - self.children_for_m2_copied: Empty list for tracking copied child element IDs

## Constraints:
    Preconditions:
    - layout must be either "horizontal" or "vertical"
    - kwargs must not contain width, height, left, top, or position keys
    - location parameter should be a valid coordinate pair if provided
    
    Postconditions:
    - Two map instances are created and configured with absolute positioning
    - Both maps are managed within a Figure container
    - Internal tracking structures for child element synchronization are initialized

## Side Effects:
    - Creates two map instances with specific positioning and sizing based on layout
    - Sets up a Figure container with both maps and the DualMap instance
    - Initializes internal tracking lists for managing child element synchronization between maps

### `folium.plugins.dual_map.DualMap._repr_html_` · *method*

## Summary:
Returns the HTML representation of the dual map for display in Jupyter environments.

## Description:
This method provides the HTML representation of the DualMap object for proper visualization in Jupyter notebook environments. It handles the case where the map has no parent by temporarily assigning it to a Figure, then delegates to the parent's `_repr_html_` method to generate the final HTML output. This ensures proper rendering regardless of whether the DualMap is already attached to a parent container.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent's `_repr_html_` method for customization.

## Returns:
    str: HTML string representation of the dual map suitable for Jupyter notebook display.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: self._parent (temporarily modified during execution)

## Constraints:
    Preconditions: The method assumes that if `self._parent` is None, the object can be added to a Figure.
    Postconditions: The method returns the HTML representation of the dual map without permanently modifying the object's parent relationship.

## Side Effects:
    Temporary modification of self._parent to a Figure instance when it was previously None.
    Calls to the parent's `_repr_html_` method which may involve template rendering and HTML generation.
    Restoration of self._parent to None after temporary assignment.

### `folium.plugins.dual_map.DualMap.add_child` · *method*

## Summary:
Adds a child element to the first map and records it for later addition to the second map in a dual map configuration.

## Description:
This method extends the standard add_child functionality by ensuring that child elements are added to both maps in a DualMap instance. It adds the child element to the first map (m1) and stores the child reference along with its name and index for later addition to the second map (m2) during the rendering phase.

The method is called during the initialization or modification phases of a DualMap instance when adding map elements like markers, layers, or controls that should appear in both views. The child elements are immediately added to m1 but stored for delayed addition to m2 to ensure proper synchronization between the two maps.

## Args:
    child: The element to be added to both maps. This can be any folium element such as Marker, TileLayer, or LayerControl.
    name (str, optional): A name to associate with the child element. Defaults to None.
    index (int, optional): The position at which to insert the child element in the second map. If None, the element is appended to the end of m2's children list. Defaults to None.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying add_child operations may raise exceptions from the parent classes.

## State Changes:
    Attributes READ:
        - self.m1: The first map instance in the dual map configuration
        - self.m2._children: The children collection of the second map (used to determine index when None)
        - self.children_for_m2: The list tracking children to be added to the second map
    
    Attributes WRITTEN:
        - self.children_for_m2: Appends a tuple of (child, name, index) to this list

## Constraints:
    Preconditions:
        - The DualMap instance must have been properly initialized with both m1 and m2 maps
        - The child element must be compatible with folium's map element system
        
    Postconditions:
        - The child element is added to m1 immediately via m1.add_child()
        - The child element is recorded for addition to m2 during the rendering phase
        - The recorded information includes the child reference, name, and insertion index
        - When index is None, it is replaced with the current length of m2._children before being stored

## Side Effects:
    None: This method does not perform any I/O operations or external service calls. It only modifies internal state and calls existing methods on map instances.

### `folium.plugins.dual_map.DualMap.render` · *method*

## Summary:
Renders child elements for the secondary map in a dual map configuration by creating deep copies of elements and adding them to the second map.

## Description:
This method is responsible for synchronizing child elements between two maps in a DualMap instance. It processes the list of children that were added to the first map but need to be replicated for the second map. The method ensures that each child element is properly copied and added to the secondary map (m2), with appropriate handling for LayerControl elements.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method.

## Returns:
    None: This method does not return any value.

## Raises:
    None explicitly raised by this method, though underlying operations may raise exceptions.

## State Changes:
    Attributes READ:
    - self.children_for_m2: List of tuples containing (child, name, index) for elements to be copied to m2
    - self.children_for_m2_copied: List tracking IDs of already-copied children to prevent duplication
    
    Attributes WRITTEN:
    - self.children_for_m2_copied: Appends child._id values to track which children have been processed

## Constraints:
    Preconditions:
    - self.children_for_m2 must be populated with valid child elements
    - self.m2 must be a valid Map instance
    - Each child in self.children_for_m2 must have an _id attribute
    
    Postconditions:
    - All children in self.children_for_m2 that haven't been copied yet are added to self.m2
    - Child elements are properly deep-copied to avoid reference conflicts
    - LayerControl elements are appropriately handled during the copying process

## Side Effects:
    - Calls deep_copy() to create copies of child elements
    - Modifies self.m2 by adding child elements
    - Invokes render() on copied child elements
    - Updates self.children_for_m2_copied list with new child IDs

### `folium.plugins.dual_map.DualMap.fit_bounds` · *method*

## Summary:
Adjusts the view of both maps in the dual map visualization to fit specified geographical bounds.

## Description:
The `fit_bounds` method configures both map instances within the dual map visualization to automatically adjust their viewports to encompass specified geographical boundaries. This method delegates the call to both `self.m1` and `self.m2` map instances, ensuring that both maps in the dual view are centered and zoomed appropriately to display the same geographical area.

This method is particularly useful when you want to programmatically set the view of both maps in a dual map configuration to show the same region, such as bounding boxes around points of interest, countries, or custom-defined areas. It maintains synchronization between the two maps in the dual view.

## Args:
- *args: Variable length argument list passed directly to the underlying `Map.fit_bounds` methods of both maps.
- **kwargs: Arbitrary keyword arguments passed directly to the underlying `Map.fit_bounds` methods of both maps.

## Returns:
- None: This method does not return a value.

## Raises:
- None explicitly raised by this method, though underlying validation may occur during map rendering or when the template is processed through the `FitBounds` class in the individual map instances.

## State Changes:
- Attributes READ: self.m1, self.m2
- Attributes WRITTEN: None

## Constraints:
- Preconditions: The arguments passed to this method must be valid arguments for the `Map.fit_bounds` method.
- Postconditions: Both `self.m1` and `self.m2` will have their viewports adjusted to fit the specified geographical bounds.

## Side Effects:
- Adds a `FitBounds` child element to both `self.m1` and `self.m2` map instances.
- The actual map adjustment is handled automatically by the folium map rendering system during the rendering phase for both maps.

### `folium.plugins.dual_map.DualMap.keep_in_front` · *method*

## Summary:
Moves map elements to the front of both maps in a dual map visualization, ensuring they appear above other map components in both views.

## Description:
The `keep_in_front` method ensures that specified map elements are rendered above other map components in both maps of a dual map visualization. This method operates on both `self.m1` and `self.m2` map instances, delegating the operation to each map's native `keep_in_front` method. It is particularly useful for bringing markers, popups, tooltips, or other interactive elements to the forefront of both map views simultaneously.

This method is part of the DualMap class's synchronization mechanism, maintaining consistent visual ordering across both maps in the dual view configuration. It follows the same pattern as other dual-map methods like `fit_bounds` that apply operations to both underlying maps.

## Args:
    *args: Variable length argument list of map elements (markers, popups, tooltips, etc.) to be kept in front of other map elements in both maps.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying map operations may raise exceptions from the parent classes.

## State Changes:
    Attributes READ:
        - self.m1: First map instance in the dual map configuration
        - self.m2: Second map instance in the dual map configuration
    
    Attributes WRITTEN:
        - Both self.m1.objects_to_stay_in_front and self.m2.objects_to_stay_in_front: Elements are appended to these lists

## Constraints:
    Preconditions:
        - The DualMap instance must have been properly initialized with both m1 and m2 maps
        - Each element in args must be a valid folium map element that can be rendered
        - Both maps must be properly initialized with their respective `objects_to_stay_in_front` lists
    
    Postconditions:
        - All elements in args are appended to the `objects_to_stay_in_front` list of both `self.m1` and `self.m2`
        - The list maintains the order of elements as they were added to both maps

## Side Effects:
    None: This method does not perform any I/O operations or external service calls. It only modifies internal state by calling methods on the underlying map instances.

