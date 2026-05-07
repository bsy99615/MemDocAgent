# `folium.py`

## `folium.folium.GlobalSwitches` · *class*

## Summary:
A configuration class for global switches that controls touch and 3D rendering behaviors in Folium maps.

## Description:
The GlobalSwitches class serves as a configuration container for global rendering options in Folium maps. It inherits from Element and provides flags to control touch interactions and 3D rendering capabilities. This class is typically instantiated internally by Folium when creating map objects and is used to configure global behavior settings that affect the entire map's rendering characteristics.

## State:
- no_touch (bool): When True, disables touch interactions on the map. Defaults to False.
- disable_3d (bool): When True, disables 3D rendering features. Defaults to False.
- _name (str): Class identifier set to "GlobalSwitches" by constructor.

## Lifecycle:
- Creation: Instantiated with optional boolean parameters no_touch and disable_3d, both defaulting to False.
- Usage: Typically used internally by Folium map rendering system to apply global configuration settings.
- Destruction: No special cleanup required as it inherits from Element base class.

## Method Map:
```mermaid
graph TD
    A[GlobalSwitches.__init__] --> B[Element.__init__]
    B --> C[Sets _name="GlobalSwitches"]
```

## Raises:
- No exceptions are explicitly raised by the constructor.

## Example:
```python
# Create global switches with default settings
switches = GlobalSwitches()

# Create global switches with custom settings
switches = GlobalSwitches(no_touch=True, disable_3d=True)

# The class is typically used internally by Folium
# and not directly instantiated by end users
```

### `folium.folium.GlobalSwitches.__init__` · *method*

## Summary:
Initializes a GlobalSwitches object with configuration options for touch and 3D rendering behavior.

## Description:
This method sets up the initial state of a GlobalSwitches instance, configuring whether touch interactions and 3D rendering features should be disabled. It inherits from the base Element class and initializes key attributes that control global rendering behaviors in the folium map context.

## Args:
    no_touch (bool): When True, disables touch interaction features for the map. Defaults to False.
    disable_3d (bool): When True, disables 3D rendering capabilities. Defaults to False.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to the string "GlobalSwitches"
    - self.no_touch: Set to the value of the no_touch parameter
    - self.disable_3d: Set to the value of the disable_3d parameter

## Constraints:
    Preconditions: None
    Postconditions: The instance will have its _name attribute set to "GlobalSwitches" and the boolean flags no_touch and disable_3d will be properly initialized.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

## `folium.folium.Map` · *class*

## Summary:
The Map class represents a Folium interactive web map that serves as the main container for all map elements and configurations.

## Description:
The Map class is the central component in Folium for creating interactive web maps. It inherits from JSCSSMixin and MacroElement, providing the foundational structure for map rendering with JavaScript and CSS dependencies. Users instantiate this class to create map objects that can be populated with markers, polygons, choropleths, and other geographical features. The class manages core map properties like location, zoom level, tile layers, and coordinate reference systems while serving as a container for all other map elements.

## State:
- location: list[float] - Center coordinates [latitude, longitude] of the map; defaults to [0, 0] when None is provided
- width: tuple[float, str] - Width dimension parsed by _parse_size() method; defaults to "100%"
- height: tuple[float, str] - Height dimension parsed by _parse_size() method; defaults to "100%"
- left: tuple[float, str] - Left positioning parsed by _parse_size() method; defaults to "0%" (Note: This will cause ValueError if passed to _parse_size due to zero value constraint)
- top: tuple[float, str] - Top positioning parsed by _parse_size() method; defaults to "0%" (Note: This will cause ValueError if passed to _parse_size due to zero value constraint)
- position: str - CSS positioning style; defaults to "relative"
- crs: str - Coordinate Reference System identifier; defaults to "EPSG3857"
- control_scale: bool - Whether to display scale control; defaults to False
- options: dict - Configuration options for Leaflet map, processed by parse_options()
- global_switches: GlobalSwitches instance - Controls global map behaviors like touch and 3D rendering
- objects_to_stay_in_front: list - Collection of map objects that should appear above others
- _png_image: bytes or None - Cached PNG screenshot of the map
- png_enabled: bool - Flag indicating whether PNG screenshots are enabled

## Lifecycle:
- Creation: Instantiate with location, dimensions, tile settings, and other configuration parameters
- Usage: Add map elements using add_child() method, then render to HTML or display in browser
- Destruction: Managed automatically by Python garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[Map.__init__] --> B[super().__init__()]
    B --> C[Set _name = "Map"]
    C --> D[Validate location or set default]
    D --> E[Create Figure and add self as child]
    E --> F[Parse size parameters]
    F --> G[Process CRS and scale control]
    G --> H[Parse options with parse_options]
    H --> I[Create GlobalSwitches]
    I --> J[Initialize objects_to_stay_in_front]
    J --> K{tiles is TileLayer?}
    K -- Yes --> L[Add tiles directly]
    K -- No --> M[Create TileLayer and add it]
    L --> N[End]
    M --> N
    
    A --> O[Map.fit_bounds] --> P[FitBounds.add_child]
    A --> Q[Map.choropleth] --> R[Choropleth.add_child]
    A --> S[Map.keep_in_front] --> T[Append to objects_to_stay_in_front]
    A --> U[Map.render] --> V[Super render]
    A --> W[Map.show_in_browser] --> X[temp_html_filepath]
    A --> Y[Map._repr_html_] --> Z[Figure._repr_html_]
    A --> AA[Map._repr_png_] --> AB[Map._to_png]
```

## Raises:
- ValueError: Raised by validate_location() when location coordinates are invalid, or by _parse_size() when size parameters cannot be parsed (e.g., zero values for left/top)
- AssertionError: Raised by render() when the map is not contained within a Figure
- ValueError: Raised by _parse_size() when size parameters cannot be parsed

## Example:
```python
import folium

# Create a basic map centered on New York City
m = folium.Map(
    location=[40.7128, -74.0060],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# Add a marker
folium.Marker([40.7128, -74.0060], popup="New York City").add_to(m)

# Render the map to HTML
html_string = m._repr_html_()

# Or display in browser
m.show_in_browser()
```

### `folium.folium.Map.__init__` · *method*

## Summary:
Initializes a Folium Map object with configurable display properties, tile layers, and geographic bounds.

## Description:
The Map.__init__ method sets up the foundational configuration for a Folium map instance. It establishes core properties like dimensions, positioning, geographic boundaries, and tile layer settings. The method handles location validation, initializes the map's HTML rendering environment, and configures various map options such as zoom levels, control visibility, and coordinate reference systems. This method is the primary entry point for creating map objects and is typically called during object instantiation.

## Args:
    location (list, tuple, or array-like, optional): Geographic center point as [latitude, longitude]. Defaults to None, which centers the map at [0, 0].
    width (str or int): Map width as percentage or pixel value. Defaults to "100%".
    height (str or int): Map height as percentage or pixel value. Defaults to "100%".
    left (str or int): Left positioning offset as percentage or pixel value. Defaults to "0%".
    top (str or int): Top positioning offset as percentage or pixel value. Defaults to "0%".
    position (str): CSS positioning strategy. Defaults to "relative".
    tiles (str or TileLayer): Base tile layer source. Defaults to "OpenStreetMap".
    attr (str, optional): Tile layer attribution text. Defaults to None.
    min_zoom (int): Minimum zoom level allowed. Defaults to 0.
    max_zoom (int): Maximum zoom level allowed. Defaults to 18.
    zoom_start (int): Initial zoom level. Defaults to 10.
    min_lat (float): Minimum latitude bound. Defaults to -90.
    max_lat (float): Maximum latitude bound. Defaults to 90.
    min_lon (float): Minimum longitude bound. Defaults to -180.
    max_lon (float): Maximum longitude bound. Defaults to 180.
    max_bounds (bool): Whether to enforce geographic bounds. Defaults to False.
    crs (str): Coordinate Reference System. Defaults to "EPSG3857".
    control_scale (bool): Whether to show scale control. Defaults to False.
    prefer_canvas (bool): Whether to prefer canvas rendering. Defaults to False.
    no_touch (bool): Whether to disable touch interactions. Defaults to False.
    disable_3d (bool): Whether to disable 3D rendering. Defaults to False.
    png_enabled (bool): Whether PNG export is enabled. Defaults to False.
    zoom_control (bool): Whether zoom controls are displayed. Defaults to True.
    **kwargs: Additional options passed to the map rendering engine.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: If location is provided but cannot be converted to a valid coordinate pair.
    ValueError: If location contains invalid coordinate values or exceeds geographic bounds.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Map"
    - self._env: Set to ENV
    - self._png_image: Set to None
    - self.png_enabled: Set to png_enabled parameter value
    - self.location: Set based on location parameter validation
    - self.width: Set via _parse_size(width)
    - self.height: Set via _parse_size(height)
    - self.left: Set via _parse_size(left)
    - self.top: Set via _parse_size(top)
    - self.position: Set to position parameter value
    - self.crs: Set to crs parameter value
    - self.control_scale: Set to control_scale parameter value
    - self.options: Set via parse_options() call
    - self.global_switches: Set to GlobalSwitches instance
    - self.objects_to_stay_in_front: Initialized as empty list

## Constraints:
    Precondition: The location parameter, if provided, must be convertible to a valid [latitude, longitude] pair.
    Precondition: Width, height, left, and top parameters must be parseable by _parse_size().
    Postcondition: The map object will have a valid configuration with appropriate defaults for all unspecified parameters.
    Postcondition: If location is None, the map will be centered at [0, 0] with zoom_start set to 1.

## Side Effects:
    - Creates and adds a Figure element to the map's parent hierarchy
    - May instantiate and add TileLayer child elements to the map
    - Sets up internal state for PNG export capability if png_enabled is True

### `folium.folium.Map._repr_html_` · *method*

## Summary:
Generates HTML representation of the map for Jupyter notebook display by establishing proper parent-child relationship before delegation.

## Description:
This method implements the Jupyter notebook display protocol by providing HTML output for the map visualization. When called in a Jupyter environment, it ensures the map has a valid parent container before delegating HTML generation to the parent's `_repr_html_` method. This is necessary because the map needs to be properly integrated into a Figure container to render correctly in notebook contexts.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent's `_repr_html_` method for HTML generation customization

## Returns:
    str: HTML string representation of the map suitable for Jupyter notebook display

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: self._parent (temporarily set to None in the conditional branch)

## Constraints:
    Preconditions: The Map instance must be properly initialized with valid configuration
    Postconditions: The method returns valid HTML string that can be rendered in Jupyter notebooks

## Side Effects:
    Temporary modification of self._parent attribute when it is initially None

### `folium.folium.Map._to_png` · *method*

## Summary:
Converts the map visualization to a PNG image by rendering it in a headless browser and taking a screenshot.

## Description:
This method renders the map as HTML, opens it in a headless Firefox browser, waits for the page to load, takes a screenshot of the map container, and caches the result. It's designed to capture the visual representation of the interactive map for export purposes.

## Args:
    delay (int): Number of seconds to wait after loading the HTML before taking the screenshot. Defaults to 3.
    driver (selenium.webdriver.Firefox): An optional pre-configured Selenium WebDriver instance. If None, a new headless Firefox driver is created.

## Returns:
    bytes: The PNG image data as bytes. Subsequent calls return the cached image data without re-rendering.

## Raises:
    Exception: Propagates any exceptions raised by Selenium WebDriver operations or file I/O.

## State Changes:
    Attributes READ: self._png_image, self.get_root()
    Attributes WRITTEN: self._png_image

## Constraints:
    Preconditions: The map must have been initialized and contain valid map data.
    Postconditions: The _png_image attribute is set to the PNG bytes after first call, and subsequent calls return the cached value.

## Side Effects:
    - Creates a temporary HTML file containing the rendered map
    - Launches a headless Firefox browser process
    - Takes a screenshot of the map element
    - Deletes the temporary HTML file after use
    - May block execution for the duration of the delay period

### `folium.folium.Map._repr_png_` · *method*

## Summary:
Returns the PNG representation of the map for display in Jupyter notebooks when PNG rendering is enabled.

## Description:
This method serves as a magic method for Jupyter notebook integration, allowing the map to be displayed as a PNG image when the notebook's display system requests a PNG representation. It acts as a conditional wrapper around the `_to_png` method, only generating the PNG if the `png_enabled` flag is set to True. This method is part of the IPython display protocol and enables rich media representation in interactive environments.

## Args:
    None

## Returns:
    bytes or None: The PNG image data as bytes if `png_enabled` is True, otherwise None.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.png_enabled, self._to_png
    Attributes WRITTEN: self._png_image (when generating new PNG data)

## Constraints:
    Preconditions: The method assumes that the Map instance has been properly initialized with a valid `png_enabled` attribute and that the `_to_png` method is available.
    Postconditions: If `png_enabled` is True, the method will either return cached PNG data or generate new PNG data via `_to_png`. The generated PNG data is stored in `self._png_image` for future use.

## Side Effects:
    I/O: May create temporary HTML files and launch a headless browser via Selenium when generating a new PNG image.
    External service calls: Uses Selenium WebDriver to render the map in a browser environment for PNG capture.

### `folium.folium.Map.render` · *method*

## Summary:
Renders the map element by adding CSS styles and global switches to the HTML figure header, then delegates to the parent rendering mechanism.

## Description:
This method prepares the map element for HTML rendering by injecting essential CSS styles and global configuration switches into the figure's header. It ensures proper styling of the HTML document and map container, and applies global rendering settings. The method is called during the map rendering pipeline when the complete HTML structure needs to be generated.

The method performs several key operations:
1. Retrieves the containing Figure object using get_root()
2. Validates that the element is properly contained within a Figure
3. Adds CSS styles for full-page layout and absolute positioning of the map container
4. Adds global configuration switches for touch and 3D rendering behavior
5. Delegates to the parent class's render method to complete the rendering process

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method for further customization.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: Raised when the map element is not contained within a Figure object, indicating improper initialization or usage.

## State Changes:
    Attributes READ: 
    - self.global_switches: Used to add global configuration settings to the figure header
    - self.get_root(): Called to retrieve the containing Figure object
    
    Attributes WRITTEN: 
    - No direct modifications to self attributes

## Constraints:
    Preconditions:
    - The map element must be contained within a Figure object (via add_child or similar mechanism)
    - The global_switches attribute must be properly initialized during object construction
    
    Postconditions:
    - The figure's header contains CSS styles for full-page layout and absolute positioning of the map container
    - The figure's header contains the global_switches element for configuration settings
    - The parent rendering logic is invoked to complete the rendering process

## Side Effects:
    - Adds CSS style elements to the figure header
    - Adds the global_switches element to the figure header
    - Invokes the parent class's render method to continue the rendering chain

### `folium.folium.Map.show_in_browser` · *method*

## Summary:
Displays the map in a web browser by rendering it to a temporary HTML file and opening it in the default browser.

## Description:
This method renders the current map object to an HTML representation, saves it to a temporary file, and opens it in the user's default web browser. It's designed for interactive exploration of maps during development or debugging sessions. The method blocks execution until the user interrupts it with Ctrl+C, allowing continuous viewing of the map.

The method leverages the `temp_html_filepath` utility to create a temporary HTML file containing the rendered map, then uses `webbrowser.open` to display it. It includes a blocking loop that waits for user interruption to prevent the program from exiting immediately.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self.get_root() (accesses the root figure element containing the map structure)
    - self.render() (renders the map to HTML string)
    
    Attributes WRITTEN: 
    - None

## Constraints:
    Precondition: The map object must be properly initialized and have a valid root figure element.
    Postcondition: The map HTML is rendered to a temporary file and opened in the browser.

## Side Effects:
    - Creates a temporary HTML file on the filesystem
    - Opens the default web browser to display the map
    - Blocks execution indefinitely until interrupted by Ctrl+C
    - May trigger system-level operations for file creation and browser launching

### `folium.folium.Map.fit_bounds` · *method*

## Summary:
Adjusts the map view to fit specified geographical bounds by adding a FitBounds component to the map's children.

## Description:
The fit_bounds method configures the map's viewport to encompass a given set of geographical coordinates. It creates a FitBounds component with the specified bounds and padding parameters, then adds it to the map's children collection. This method is typically used to programmatically center and zoom a map to display a specific area or set of markers.

This logic is encapsulated in its own method rather than being inlined because:
1. It provides a clean, intuitive interface for users to fit map bounds
2. It separates concerns by delegating the actual bounds-fitting logic to the dedicated FitBounds class
3. It allows for easy reuse and testing of the bounds-fitting functionality
4. It maintains consistency with Folium's pattern of adding components via add_child()

## Args:
- bounds (list): A list of two coordinate pairs [[lat1, lng1], [lat2, lng2]] representing the geographical boundaries to fit
- padding_top_left (list, optional): Padding for the top-left corner as [x, y] values. Defaults to None
- padding_bottom_right (list, optional): Padding for the bottom-right corner as [x, y] values. Defaults to None
- padding (list, optional): Uniform padding for all sides as [x, y] values. Defaults to None
- max_zoom (int, optional): Maximum zoom level to use when fitting bounds. Defaults to None

## Returns:
- None: This method does not return a value

## Raises:
- None explicitly raised by fit_bounds
- May raise exceptions from FitBounds constructor if invalid parameters are passed
- May raise exceptions from add_child if invalid parameters are passed

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: None

## Constraints:
- Preconditions: The bounds parameter must be a valid list of two coordinate pairs
- Postconditions: The map will have a FitBounds child component added to its children collection

## Side Effects:
- Adds a FitBounds component to the map's children collection
- No direct I/O operations or external service calls

### `folium.folium.Map.choropleth` · *method*

## Summary:
Adds a choropleth layer to the map by creating and registering a Choropleth feature.

## Description:
This method provides a deprecated interface for adding choropleth layers to a Folium map. It issues a FutureWarning to alert users that this method is deprecated and recommends using the standalone Choropleth class instead. The method creates a Choropleth instance with the provided arguments and registers it as a child element of the map.

## Args:
    *args: Variable length argument list passed directly to the Choropleth constructor.
    **kwargs: Arbitrary keyword arguments passed directly to the Choropleth constructor.

## Returns:
    None

## Raises:
    FutureWarning: Always raised due to the method being deprecated.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Map object must be properly initialized and callable.
    Postconditions: The Choropleth feature is added to the map's children collection via the add_child method.

## Side Effects:
    Issues a FutureWarning to the user about deprecation.
    Creates a new Choropleth instance.
    Calls self.add_child() to register the choropleth with the map.

### `folium.folium.Map.keep_in_front` · *method*

## Summary:
Adds map objects to a list that ensures they remain visually in front of other map elements during rendering.

## Description:
The keep_in_front method manages a collection of map objects that should maintain a higher visual z-index than other map elements. This is particularly useful for ensuring that certain features like markers, popups, or controls stay visible above layers such as choropleths or tile layers. The method is typically called during the map construction phase when specific objects need to be prioritized in the rendering order to ensure proper visual stacking.

This method exists as a separate component because it encapsulates the logic for managing visual priority of map elements, separating this concern from the core map rendering logic. It allows developers to declaratively specify which elements should stay in front without having to manually manage z-index properties.

## Args:
    *args: Variable length argument list of map objects to keep in front

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.objects_to_stay_in_front (list)
    Attributes WRITTEN: self.objects_to_stay_in_front (appends objects to the list)

## Constraints:
    Preconditions: The method assumes that self.objects_to_stay_in_front is initialized as an empty list in the Map class constructor
    Postconditions: All objects passed in args are appended to the self.objects_to_stay_in_front list in the order they were provided

## Side Effects:
    None

