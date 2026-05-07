# `dual_map.py`

## `folium.plugins.dual_map.DualMap` · *class*

## Summary:
A dual-map visualization component that displays two synchronized map views side-by-side or vertically stacked.

## Description:
The DualMap class creates two synchronized map instances that can be displayed either horizontally (side-by-side) or vertically. This component is useful for comparing geographic data, viewing the same location from different perspectives, or creating split-screen map visualizations. It inherits from JSCSSMixin and MacroElement, providing automatic JavaScript/CSS resource management and element composition capabilities.

The class manages two underlying Map instances (m1 and m2) that share the same location and configuration but are positioned differently based on the selected layout. Children added to the DualMap are automatically synchronized between both maps, with special handling for LayerControl elements to ensure proper functionality.

## State:
- m1 (Map): First map instance positioned on the left/top
- m2 (Map): Second map instance positioned on the right/bottom  
- children_for_m2 (list): List of tuples containing (child, name, index) for tracking children to be added to m2
- children_for_m2_copied (list): List of child IDs that have already been copied to m2 to prevent duplication
- layout (str): Layout configuration, either "horizontal" or "vertical"
- location (list or None): Center coordinates for both maps as [latitude, longitude]

## Lifecycle:
- Creation: Instantiate with location and layout parameters. The constructor automatically creates two Map instances with appropriate positioning and sizing based on the layout. The width and height are set to 50% for horizontal layout and 100%/50% for vertical layout respectively.
- Usage: Add child elements using add_child() method. These children will be added to both maps. Call fit_bounds() or keep_in_front() to synchronize map behaviors.
- Destruction: Cleanup occurs automatically through parent-child relationship management when the DualMap is removed from its parent Figure.

## Method Map:
```mermaid
graph TD
    A[DualMap.__init__] --> B[super().__init__()]
    B --> C[Validate layout parameter]
    C --> D[Create m1 Map instance with width=50%, height=100% if horizontal else 100%, 50%]
    D --> E[Create m2 Map instance with appropriate positioning]
    E --> F[Setup figure with both maps]
    F --> G[Initialize children tracking lists]
    
    A --> H[DualMap.add_child] --> I[m1.add_child(child, name, index)]
    I --> J[Store child info for m2 with index handling]
    
    A --> K[DualMap.render] --> L[super().render()]
    L --> M[Process children_for_m2]
    M --> N{Child ID in copied list?}
    N -- Yes --> O[Skip child]
    N -- No --> P[deep_copy(child)]
    P --> Q{Is LayerControl?}
    Q -- Yes --> R[child_copy.reset()]
    Q -- No --> S[Add to m2]
    S --> T[Render child_copy]
    T --> U[Add child._id to copied list]
    
    A --> V[DualMap.fit_bounds] --> W[m1.fit_bounds(args, kwargs)]
    W --> X[m2.fit_bounds(args, kwargs)]
    
    A --> Y[DualMap.keep_in_front] --> Z[m1.keep_in_front(args)]
    Z --> AA[m2.keep_in_front(args)]
```

## Raises:
- ValueError: When layout parameter is not "horizontal" or "vertical"
- AssertionError: When width, height, left, top, or position arguments are passed to the constructor (these are internally managed and will cause assertion failure)

## Example:
```python
import folium

# Create a dual map with horizontal layout
dual_map = folium.plugins.DualMap(
    location=[40.7128, -74.0060],  # New York City
    layout="horizontal"
)

# Add a marker to both maps
folium.Marker(
    location=[40.7128, -74.0060],
    popup="New York City"
).add_to(dual_map)

# Add a tile layer to both maps
folium.TileLayer(
    tiles="OpenStreetMap",
    name="OpenStreetMap"
).add_to(dual_map)

# Fit both maps to show a specific bounding box
bounds = [[40.7, -74.1], [40.8, -73.9]]
dual_map.fit_bounds(bounds)

# Display the dual map
dual_map._repr_html_()
```

### `folium.plugins.dual_map.DualMap.__init__` · *method*

## Summary:
Initializes a DualMap instance with two synchronized map views arranged according to the specified layout.

## Description:
Creates two Map instances (m1 and m2) that are positioned side-by-side or vertically based on the layout parameter. The constructor handles validation of parameters and sets up the internal structure for managing children that will be synchronized between both maps. This method is responsible for establishing the basic dual-map framework and cannot accept certain keyword arguments that would conflict with internal positioning.

## Args:
    location (list or None): Center coordinates for both maps as [latitude, longitude]. Defaults to None.
    layout (str): Layout configuration for the dual map. Must be either "horizontal" or "vertical". Defaults to "horizontal".
    **kwargs: Additional keyword arguments passed to both Map instances. Cannot include width, height, left, top, or position.

## Returns:
    None: This is a constructor method that initializes the object's state.

## Raises:
    ValueError: When layout parameter is not "horizontal" or "vertical".
    AssertionError: When width, height, left, top, or position arguments are passed in kwargs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.m1: First Map instance with appropriate positioning
    - self.m2: Second Map instance with appropriate positioning  
    - self.children_for_m2: Empty list for tracking children to be added to m2
    - self.children_for_m2_copied: Empty list for tracking child IDs already copied to m2

## Constraints:
    Preconditions:
    - layout must be either "horizontal" or "vertical"
    - kwargs must not contain width, height, left, top, or position keys
    Postconditions:
    - Two Map instances (m1 and m2) are created and properly configured
    - A Figure is established with both maps and the DualMap itself as children
    - Tracking lists for children synchronization are initialized

## Side Effects:
    None: This method doesn't perform I/O operations or mutate external objects. It only initializes internal state.

### `folium.plugins.dual_map.DualMap._repr_html_` · *method*

## Summary:
Returns an HTML representation of the dual map for rich display in Jupyter environments, ensuring proper parent context setup.

## Description:
This method provides HTML rendering capability for DualMap objects, enabling rich display in Jupyter notebooks and other HTML-capable environments. When the DualMap has no parent (self._parent is None), it temporarily creates a Figure context by calling self.add_to(Figure()), then retrieves the HTML representation from the parent's _repr_html_ method, and finally restores the parent reference to None. When a parent exists, it simply delegates to the parent's _repr_html_ method.

## Args:
    **kwargs: Additional keyword arguments passed to the parent's _repr_html_ method

## Returns:
    str: HTML string representation of the dual map

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: self._parent (set to None temporarily during execution)

## Constraints:
    Preconditions: The object must be properly initialized with required attributes
    Postconditions: Returns valid HTML string representation of the dual map

## Side Effects:
    I/O: Creates a temporary Figure instance when self._parent is None
    Mutation: Temporarily modifies self._parent attribute during execution by setting it to None after use

### `folium.plugins.dual_map.DualMap.add_child` · *method*

## Summary:
Adds a child element to the first map and records it for synchronization with the second map in a dual map configuration.

## Description:
This method handles the addition of child elements to a DualMap instance. It adds the specified child element to the first map (m1) and stores the child information in a list (children_for_m2) for later addition to the second map (m2). This ensures that elements added to the dual map appear consistently on both maps while preserving proper ordering.

The method delegates the actual addition to m1 and manages the synchronization logic separately. This design allows for proper coordination between the two maps during rendering, where the stored child information is processed in the render() method.

## Args:
    child: The child element to be added to both maps
    name (str, optional): Name to assign to the child element. Defaults to None.
    index (int, optional): Position at which to insert the child element. If None, the child is added at the end of the second map's children list. Defaults to None.

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.m1, self.m2._children, self.children_for_m2
    Attributes WRITTEN: self.children_for_m2

## Constraints:
    Preconditions: 
    - self must be an instance of DualMap class
    - self.m1 must be a valid Map instance
    - self.m2 must be a valid Map instance
    
    Postconditions:
    - The child element is added to self.m1 via delegation
    - The child element information is stored in self.children_for_m2 for later processing
    - If index is None, the child is recorded with an index equal to the current length of self.m2._children

## Side Effects:
    None

### `folium.plugins.dual_map.DualMap.render` · *method*

## Summary:
Copies map children from the first map to the second map during rendering, ensuring proper synchronization and handling special cases like LayerControl elements.

## Description:
This method is responsible for synchronizing map elements between two internal maps (m1 and m2) during the rendering phase. It iterates through children that were added to the first map and copies them to the second map, maintaining proper ordering and handling special cases such as LayerControl elements which require reset operations.

The method is called during the standard rendering lifecycle of the DualMap component and ensures that both maps display identical content while maintaining proper element state management.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method

## Returns:
    None: This method performs side effects and does not return a value

## Raises:
    None explicitly raised by this method, though underlying operations may raise exceptions

## State Changes:
    Attributes READ:
    - self.children_for_m2: List of (child, name, index) tuples representing children to be copied to m2
    - self.children_for_m2_copied: List of child IDs that have already been copied to prevent duplication
    
    Attributes WRITTEN:
    - self.children_for_m2_copied: Appends child._id values to track which children have been processed

## Constraints:
    Preconditions:
    - self.children_for_m2 must contain valid (child, name, index) tuples
    - self.m2 must be a valid Map instance
    - Child elements must support deep_copy operations
    
    Postconditions:
    - All children in self.children_for_m2 that haven't been copied yet are added to self.m2
    - LayerControl children have their reset() method called before being added to m2
    - Child elements are rendered in their new context

## Side Effects:
    - Modifies self.m2 by adding child elements to it
    - Calls render() on each copied child element
    - May trigger additional rendering operations on child elements
    - Updates self.children_for_m2_copied list with processed child IDs

### `folium.plugins.dual_map.DualMap.fit_bounds` · *method*

## Summary:
Adjusts the view of both maps in the dual map visualization to fit specified geographical bounds.

## Description:
Applies the fit_bounds functionality to both underlying maps (m1 and m2) of the DualMap instance. This ensures that both maps in the dual visualization are configured to display the same geographical bounds, maintaining synchronization between the two map views.

This logic is implemented as its own method rather than being inlined because it provides a convenient way to synchronize the view configuration of both maps simultaneously, which is the core functionality of the DualMap class. It maintains consistency between the two map views while preserving the individual map configurations.

## Args:
    *args: Variable length argument list passed directly to the fit_bounds method of each map.
    **kwargs: Arbitrary keyword arguments passed directly to the fit_bounds method of each map.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised by this method, but underlying operations may raise exceptions from the individual map's fit_bounds implementations.

## State Changes:
    Attributes READ: 
        - self.m1: First map instance in the dual map
        - self.m2: Second map instance in the dual map
    Attributes WRITTEN:
        - None: This method doesn't modify the DualMap instance's attributes directly

## Constraints:
    Preconditions:
        - Both self.m1 and self.m2 must be valid Map instances
        - Arguments passed to fit_bounds must be valid for the underlying Map.fit_bounds method
    Postconditions:
        - Both maps in the dual view will be configured to fit the same geographical bounds
        - The view configuration of both maps will be synchronized

## Side Effects:
    - Calls fit_bounds on both underlying Map instances (m1 and m2)
    - May add FitBounds control elements to both map instances' child collections

### `folium.plugins.dual_map.DualMap.keep_in_front` · *method*

## Summary:
Moves specified map elements to the front of the display layer stack in both sub-maps of the dual map.

## Description:
This method ensures that one or more map elements (markers, layers, etc.) are visually positioned in front of other map elements in both constituent maps (m1 and m2) of the DualMap. It delegates the operation to the underlying Map.keep_in_front method for each sub-map, maintaining synchronization between the two maps. This is useful for ensuring that certain elements like markers or popups remain visible when overlapping with other map features.

## Args:
    *args: Variable length argument list containing map elements to be moved to the front of the display order.

## Returns:
    None: This method does not return any value.

## Raises:
    Exception: This method may propagate exceptions raised by the underlying Map.keep_in_front calls if invalid arguments are passed.

## State Changes:
    Attributes READ: self.m1, self.m2
    Attributes WRITTEN: Both self.m1.objects_to_stay_in_front and self.m2.objects_to_stay_in_front are modified by appending elements to them.

## Constraints:
    Preconditions: The DualMap instance must be properly initialized with two valid Map instances (self.m1 and self.m2).
    Postconditions: All elements passed in *args will be added to the objects_to_stay_in_front list of both sub-maps, ensuring they appear visually in front of other elements.

## Side Effects:
    None: This method does not perform any I/O operations or external service calls. It only modifies internal state of the two sub-maps.

