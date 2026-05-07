# `dual_map.py`

## `folium.plugins.dual_map.DualMap` · *class*

## Summary:
DualMap is a Folium plugin that creates a synchronized dual-map interface, allowing two interactive maps to be displayed side-by-side or stacked with synchronized panning and zooming.

## Description:
The DualMap class enables the creation of synchronized map views, useful for comparing geographic data, viewing the same location from different perspectives, or displaying related datasets simultaneously. It creates two underlying Map instances that share the same location and synchronization behavior through the Leaflet.Sync library. The class supports both horizontal (side-by-side) and vertical (stacked) layouts for the dual maps.

This abstraction exists to provide a clean, reusable interface for creating synchronized dual-map displays without requiring manual implementation of the synchronization logic or complex HTML/CSS positioning. It leverages Folium's existing Map infrastructure while extending it to manage two synchronized map instances.

## State:
- m1 (Map): First map instance positioned on the left/top side
- m2 (Map): Second map instance positioned on the right/bottom side  
- children_for_m2 (list): List of tuples containing (child_object, name, index) to be copied to m2
- children_for_m2_copied (list): List of child IDs that have already been copied to m2 to prevent duplication
- _template (Template): Jinja2 template for rendering the dual map HTML
- default_js (list): List of JavaScript dependencies including Leaflet.Sync library

## Lifecycle:
- Creation: Instantiate with location and layout parameters; automatically creates two Map instances with appropriate positioning
- Usage: Add map elements to the DualMap instance (which forwards to m1); these elements are automatically synchronized to m2 during rendering
- Destruction: Managed by Python garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[DualMap.__init__] --> B[super().__init__()]
    B --> C[Validate layout parameter]
    C --> D[Create m1 Map with layout-specific sizing]
    D --> E[Create m2 Map with layout-specific sizing]
    E --> F[Add m1 and m2 to Figure]
    F --> G[Add self to Figure]
    G --> H[Initialize children tracking lists]
    
    A --> I[DualMap.add_child] --> J[m1.add_child]
    J --> K[Store child info for m2 copying]
    
    A --> L[DualMap.render] --> M[super().render()]
    M --> N[Copy children from m1 to m2]
    N --> O[Handle LayerControl special case]
    O --> P[Add copied child to m2]
    P --> Q[Render copied child]
    Q --> R[Track copied child IDs]
    
    A --> S[DualMap.fit_bounds] --> T[m1.fit_bounds]
    T --> U[m2.fit_bounds]
    
    A --> V[DualMap.keep_in_front] --> W[m1.keep_in_front]
    W --> X[m2.keep_in_front]
```

## Raises:
- ValueError: Raised when layout parameter is not "horizontal" or "vertical"
- AssertionError: Raised when width, height, left, top, or position arguments are passed to the constructor (these are internally managed)

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

# Add a tile layer to both maps
folium.TileLayer("OpenStreetMap").add_to(dual_map)

# Render the dual map
html_output = dual_map._repr_html_()
```

### `folium.plugins.dual_map.DualMap.__init__` · *method*

## Summary:
Initializes a DualMap instance with two synchronized map views, setting up the underlying map objects and validation for layout configuration.

## Description:
The `__init__` method constructs a DualMap object by creating two underlying Map instances (m1 and m2) that will be synchronized. It validates the layout parameter and sets appropriate positioning and sizing for the maps based on the chosen layout. The method also initializes tracking lists for managing child elements that need to be duplicated between the two maps during rendering.

This logic is encapsulated in its own method to separate the initialization concerns from the rest of the DualMap class functionality, ensuring proper setup of the dual map structure before any operations like adding children or rendering occur.

## Args:
- location (list or tuple, optional): Center coordinates [latitude, longitude] for both maps. Defaults to None.
- layout (str): Layout orientation for the dual maps. Must be either "horizontal" or "vertical". Defaults to "horizontal".
- **kwargs: Additional keyword arguments passed to the underlying Map constructors.

## Returns:
None

## Raises:
- ValueError: Raised when the layout parameter is not "horizontal" or "vertical".
- AssertionError: Raised when any of the reserved keys ("width", "height", "left", "top", "position") are provided in kwargs.

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: 
  - self.m1: First map instance with layout-specific configuration
  - self.m2: Second map instance with layout-specific configuration
  - self.children_for_m2: Empty list initialized for tracking child elements to copy to m2
  - self.children_for_m2_copied: Empty list initialized for tracking already-copied child IDs

## Constraints:
- Preconditions: 
  - Layout must be either "horizontal" or "vertical"
  - Reserved keys (width, height, left, top, position) must not be present in kwargs
- Postconditions:
  - Two Map instances (m1 and m2) are created with appropriate configuration
  - Figure is properly configured with both maps and the DualMap instance as children
  - Tracking lists for children are initialized

## Side Effects:
- Creates two Map instances (m1 and m2) with specific configuration parameters
- Adds the two Map instances and the DualMap instance itself to a Figure container
- Initializes internal tracking lists for child element management

### `folium.plugins.dual_map.DualMap._repr_html_` · *method*

## Summary:
Generates HTML representation for Jupyter notebook display by managing parent-child relationships before delegating to parent's HTML rendering method.

## Description:
This method implements the Jupyter notebook display protocol for DualMap instances. When called in a Jupyter environment, it ensures the dual map has a valid parent container before delegating HTML generation to the parent's `_repr_html_` method. This is necessary because the dual map needs to be properly integrated into a Figure container to render correctly in notebook contexts. The method handles two cases: when `self._parent` is None (where it temporarily assigns a Figure as parent via `add_to()` and cleans up afterward) and when the parent already exists. This approach allows the dual map to be displayed properly in Jupyter notebooks while maintaining the correct parent-child hierarchy.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent's `_repr_html_` method for HTML generation customization

## Returns:
    str: HTML string representation of the dual map suitable for Jupyter notebook display

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: self._parent (temporarily modified in conditional branch)

## Constraints:
    Preconditions: The DualMap instance must be properly initialized with valid configuration
    Postconditions: The method returns valid HTML string that can be rendered in Jupyter notebooks

## Side Effects:
    Temporary modification of self._parent attribute when it is initially None

### `folium.plugins.dual_map.DualMap.add_child` · *method*

## Summary:
Adds a child element to the first map of a dual map instance and tracks it for synchronization with the second map.

## Description:
This method adds a child element to the first map (self.m1) in a DualMap instance and records the element for later addition to the second map (self.m2) during the rendering phase. This approach enables the synchronization of map elements between two separate map instances that are displayed side-by-side. The method ensures that when elements are added to the first map, they are also properly replicated and added to the second map with appropriate indexing.

## Args:
    child: The child element to be added to the first map. This can be any Folium element such as markers, layers, or controls.
    name (str, optional): A name to assign to the child element. Defaults to None.
    index (int, optional): The index position where the child should be inserted. If None, the child is appended to the end of the children list. Defaults to None.

## Returns:
    None: This method does not return any value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ:
        - self.m1: Used to add the child element via its add_child method
        - self.m2._children: Read to determine the index when None is provided
        - self.children_for_m2: Used to store the child element information for later processing
    Attributes WRITTEN:
        - self.children_for_m2: Appended with a tuple containing (child, name, index)

## Constraints:
    Preconditions:
        - The child parameter must be a valid Folium element that can be added to a Map
        - The DualMap instance must have been properly initialized with two Map instances (m1 and m2)
        - The method should only be called during the setup phase before rendering
    Postconditions:
        - The child element is added to self.m1
        - The child element information is stored in self.children_for_m2 for later processing
        - When index is None, it gets assigned to the length of self.m2._children to ensure proper ordering

## Side Effects:
    None: This method does not perform any I/O operations or mutate external objects beyond modifying the internal state of the DualMap instance.

### `folium.plugins.dual_map.DualMap.render` · *method*

## Summary:
Renders the DualMap by copying and adding child elements to the second map instance while managing duplicate prevention and special handling for LayerControl.

## Description:
This method extends the parent class's render functionality to specifically handle child elements that should be rendered on the second map instance (m2) of a DualMap. It processes children that were added via the add_child method, creates deep copies of them, and adds these copies to m2 while ensuring no duplicates are added. Special handling is implemented for LayerControl objects, which require reset() to clear their internal state before being added to the second map. The method is designed to work in conjunction with the DualMap's architecture where elements are initially added to m1 but also need to be replicated on m2 for synchronized viewing.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ:
    - self.children_for_m2: List of tuples containing (child, name, index) for elements to be copied to m2
    - self.children_for_m2_copied: List of IDs of children already copied to m2
    - self.m2: Second map instance where copied children are added
    Attributes WRITTEN:
    - self.children_for_m2_copied: Appends child._id values to prevent duplicate processing

## Constraints:
    Preconditions:
    - self.children_for_m2 must be a list of tuples containing (child, name, index)
    - self.children_for_m2_copied must be a list of IDs
    - self.m2 must be a valid Map instance
    Postconditions:
    - All children in self.children_for_m2 that haven't been copied yet are added to self.m2
    - Each copied child is rendered individually
    - Duplicate prevention ensures no child is processed twice
    - LayerControl objects have their state reset before being added to m2

## Side Effects:
    - Calls deep_copy() to create copies of child elements
    - Modifies self.m2 by adding child elements to it
    - Invokes render() on each copied child element
    - May invoke reset() on LayerControl objects to clear their internal state

### `folium.plugins.dual_map.DualMap.fit_bounds` · *method*

## Summary:
Adjusts the view of both maps in the dual map display to fit specified geographical bounds.

## Description:
This method synchronizes the zoom level and center of both underlying maps (m1 and m2) to ensure they both display the same geographical area defined by the provided bounds. It delegates the actual bounds-fitting logic to each individual map's fit_bounds method, ensuring both maps display the same view. This approach maintains synchronization between the two maps while allowing users to easily set the view for both maps simultaneously.

## Args:
    *args: Variable length argument list containing geographical bounds to fit. Typically expects a list of two coordinate pairs [[lat1, lng1], [lat2, lng2]].
    **kwargs: Arbitrary keyword arguments passed to each map's fit_bounds method, such as padding parameters.

## Returns:
    None: This method does not return any value.

## Raises:
    Exception: Any exceptions raised by the individual map's fit_bounds method will propagate up through this method.

## State Changes:
    Attributes READ: self.m1, self.m2
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Both self.m1 and self.m2 must be valid Map instances with appropriate geographical bounds support.
    Postconditions: Both maps will have their view adjusted to fit the specified geographical bounds.

## Side Effects:
    None: This method does not perform any I/O operations or mutate external objects.

### `folium.plugins.dual_map.DualMap.keep_in_front` · *method*

## Summary:
Delegates the keep_in_front operation to both underlying Map instances within a DualMap.

## Description:
The keep_in_front method ensures that specified map objects maintain visual priority in both sub-maps of a DualMap. When called, it propagates the keep_in_front operation to both self.m1 and self.m2, ensuring consistent visual stacking across both synchronized maps. This is particularly important for maintaining the same visual hierarchy in dual-map displays where users expect identical visual behavior in both views.

This method exists as a separate component because it provides a unified interface for managing visual priority across both maps in a DualMap, rather than requiring users to manually call keep_in_front on each map separately. It maintains consistency in the user experience across both synchronized views.

## Args:
    *args: Variable length argument list containing map objects to keep in front

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.m1, self.m2 (both Map instances)
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The DualMap instance must have been properly initialized with two Map instances (m1 and m2)
    Postconditions: Both self.m1.keep_in_front() and self.m2.keep_in_front() are called with identical arguments

## Side Effects:
    None

