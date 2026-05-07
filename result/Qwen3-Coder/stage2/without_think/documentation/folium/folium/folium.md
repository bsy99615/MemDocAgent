# `folium.py`

## `folium.folium.GlobalSwitches` · *class*

## Summary:
Manages global configuration switches for folium map rendering, specifically controlling touch interaction and 3D rendering behavior.

## Description:
The GlobalSwitches class serves as a configuration container that defines global behavioral settings for folium maps. It is typically instantiated internally by folium's map rendering system and integrated into the map's element tree. This class allows users to control whether touch interactions are enabled and whether 3D rendering features are disabled, which can be important for compatibility with different devices or rendering contexts.

## State:
- no_touch (bool): When True, disables touch interaction controls for the map. Defaults to False.
- disable_3d (bool): When True, disables 3D rendering features. Defaults to False.
- _name (str): Set to "GlobalSwitches" to identify this element type in the rendering system.
- _template (Template): Jinja2 template object, likely used for rendering global switch configurations in HTML output.

## Lifecycle:
- Creation: Instantiated with optional boolean parameters no_touch and disable_3d, both defaulting to False
- Usage: Automatically integrated into folium's element tree during map rendering as part of the HTML generation process
- Destruction: Managed automatically by the parent Element's lifecycle management

## Method Map:
```mermaid
graph TD
    A[GlobalSwitches.__init__] --> B[Element.__init__]
    B --> C[Sets _name="GlobalSwitches"]
    C --> D[Stores no_touch and disable_3d flags]
    D --> E[Initializes _template with empty Template]
```

## Raises:
- No explicit exceptions are raised by the constructor based on the provided code

## Example:
```python
# Create global switches with default settings
switches = GlobalSwitches()

# Create global switches with custom settings
switches = GlobalSwitches(no_touch=True, disable_3d=True)
```

### `folium.folium.GlobalSwitches.__init__` · *method*

## Summary:
Initializes a GlobalSwitches object with configuration options for touch support and 3D rendering.

## Description:
Configures global switches for folium map rendering, specifically controlling touch interaction and 3D visualization capabilities. This method sets up the object's state with configurable flags that affect how the map behaves in different environments.

## Args:
    no_touch (bool): Disables touch interaction features. Defaults to False.
    disable_3d (bool): Disables 3D rendering capabilities. Defaults to False.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "GlobalSwitches"
        - self.no_touch: Set to the provided no_touch parameter value
        - self.disable_3d: Set to the provided disable_3d parameter value

## Constraints:
    Preconditions: None
    Postconditions: The GlobalSwitches object is properly initialized with the specified configuration options.

## Side Effects:
    None: This method does not produce any side effects beyond initializing object attributes.

## `folium.folium.Map` · *class*

## Summary:
Represents a Folium map visualization that can be rendered as HTML, exported as PNG, or displayed in a web browser.

## Description:
The Map class is the central component of the Folium library for creating interactive web maps. It serves as the main container for all map elements including markers, layers, and controls. The class manages the map's configuration, rendering pipeline, and various display modes.

This class is designed to be instantiated with various parameters that control the initial map view, tile sources, and display properties. It provides methods for rendering the map to HTML, displaying it in a browser, exporting to PNG format, and adjusting the map view to fit specific geographical bounds.

## State:
- location: list[float] - The initial geographical center point of the map as [latitude, longitude]. Defaults to [0, 0] when no location is provided.
- width: tuple[float, str] - The width of the map container, parsed into a numeric value and unit (e.g., (100.0, '%')).
- height: tuple[float, str] - The height of the map container, parsed into a numeric value and unit (e.g., (100.0, '%')).
- left: tuple[float, str] - The left positioning of the map container, parsed into a numeric value and unit.
- top: tuple[float, str] - The top positioning of the map container, parsed into a numeric value and unit.
- position: str - CSS positioning property for the map container, defaults to "relative".
- crs: str - Coordinate Reference System identifier, defaults to "EPSG3857".
- control_scale: bool - Whether to enable the scale control on the map, defaults to False.
- options: dict - Configuration options for the Leaflet map, including zoom level, bounds, and other settings.
- global_switches: GlobalSwitches - Configuration object for global map behaviors like touch interaction and 3D rendering.
- objects_to_stay_in_front: list - Collection of map objects that should remain visually in front of other elements.
- png_enabled: bool - Flag indicating whether PNG export functionality is enabled, defaults to False.
- _png_image: bytes or None - Cached PNG image data when exported, initially None.
- _name: str - Identifier for the map element, hardcoded to "Map".
- _env: Environment - Jinja2 environment used for template rendering.
- _template: Template - Jinja2 template for the map HTML structure (empty in current implementation).

## Lifecycle:
- Creation: Instantiate with configuration parameters to define initial map properties and view. The constructor handles validation and setup of the map's initial state.
- Usage: Add map elements (markers, layers, etc.) using the add_child() method, then render using render() or display using show_in_browser().
- Destruction: Cleanup occurs automatically when the map is garbage collected or when explicitly removed from its parent container.

## Method Map:
```mermaid
graph TD
    A[Map.__init__] --> B[Super().__init__()]
    B --> C[Set _name="Map"]
    C --> D[Set _env to ENV]
    D --> E[Set _png_image to None]
    E --> F[Set png_enabled flag]
    F --> G{location is None?}
    G -- Yes --> H[Set location to [0, 0] and zoom_start to 1]
    G -- No --> I[Validate location with validate_location]
    H --> J[Create Figure and add self as child]
    I --> J
    J --> K[Parse size parameters with _parse_size]
    K --> L[Set positioning properties]
    L --> M[Process max_bounds array]
    M --> N[Set CRS and control_scale]
    N --> O[Parse options with parse_options]
    O --> P[Create GlobalSwitches]
    P --> Q[Initialize objects_to_stay_in_front]
    Q --> R{tiles is TileLayer?}
    R -- Yes --> S[Add tiles directly via add_child]
    R -- No --> T[Create TileLayer and add it via add_child]
    
    A --> U[Map.render] --> V[Get root figure]
    V --> W[Assert figure is Figure]
    W --> X[Add global_switches to figure header]
    X --> Y[Add CSS styles to figure header]
    Y --> Z[Call super().render()]
    
    A --> AA[Map.show_in_browser] --> AB[Render to HTML]
    AB --> AC[Create temp HTML file]
    AC --> AD[Open in browser]
    AD --> AE[Wait for user interrupt]
    
    A --> AF[Map.fit_bounds] --> AG[Create FitBounds and add as child]
    
    A --> AH[Map.choropleth] --> AI[Warn and create Choropleth]
    AI --> AJ[Add Choropleth as child]
    
    A --> AK[Map.keep_in_front] --> AL[Append to objects_to_stay_in_front]
    
    A --> AM[Map._repr_html_] --> AN{Has parent?}
    AN -- No --> AO[Add to Figure and render]
    AN -- Yes --> AP[Render parent]
    
    A --> AQ[Map._repr_png_] --> AR{png_enabled?}
    AR -- No --> AS[Return None]
    AR -- Yes --> AT[Call _to_png()]
    
    A --> AU[Map._to_png] --> AV{Has cached image?}
    AV -- No --> AW[Create Selenium driver]
    AW --> AX[Render HTML]
    AX --> AY[Save to temp file]
    AY --> AZ[Load in browser]
    AZ --> BA[Take screenshot]
    BA --> BB[Cache image]
    BB --> BC[Return image]
```

## Raises:
- ValueError: Raised by validate_location when location coordinates are invalid or don't contain exactly two values.
- AssertionError: Raised by render() when the map is not contained within a Figure context.
- ValueError: Raised by _parse_size when size values cannot be parsed properly (negative values, invalid percentages).

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

# Render to HTML
html_content = m._repr_html_()

# Or display in browser
m.show_in_browser()

# Fit map to specific bounds
bounds = [[40.5, -74.2], [40.9, -73.8]]
m.fit_bounds(bounds)
```

### `folium.folium.Map.__init__` · *method*

## Summary:
Initializes a new Map object with specified geographical location, dimensions, and rendering options, setting up the foundational configuration for interactive map visualization.

## Description:
The Map.__init__ method constructs a new map instance by configuring core properties such as geographical center point, display dimensions, tile layers, and various rendering behaviors. This constructor establishes the fundamental state of the map object, including its coordinate reference system, zoom controls, and initial view parameters. It integrates with folium's element tree architecture by associating itself with a Figure container and setting up appropriate rendering options for the underlying JavaScript map library.

## Args:
    location (list, tuple, or None): Geographic coordinates [latitude, longitude] for the map's initial center point. If None, defaults to [0, 0] with zoom_start set to 1. Default is None.
    width (str or int): Width of the map container. Can be a percentage string (e.g., "100%") or numeric value interpreted as pixels. Default is "100%".
    height (str or int): Height of the map container. Can be a percentage string (e.g., "100%") or numeric value interpreted as pixels. Default is "100%".
    left (str or int): Left positioning offset of the map container. Default is "0%".
    top (str or int): Top positioning offset of the map container. Default is "0%".
    position (str): CSS positioning strategy for the map container. Default is "relative".
    tiles (str, TileLayer, or bool): Base tile layer specification. Can be a string identifier (like "OpenStreetMap"), a TileLayer instance, or boolean indicating whether to show tiles. Default is "OpenStreetMap".
    attr (str or None): Attribution text for the tile layer. Default is None.
    min_zoom (int): Minimum zoom level allowed for the map. Default is 0.
    max_zoom (int): Maximum zoom level allowed for the map. Default is 18.
    zoom_start (int): Initial zoom level when the map loads. Default is 10.
    min_lat (float): Minimum latitude boundary for map movement. Default is -90.
    max_lat (float): Maximum latitude boundary for map movement. Default is 90.
    min_lon (float): Minimum longitude boundary for map movement. Default is -180.
    max_lon (float): Maximum longitude boundary for map movement. Default is 180.
    max_bounds (bool): Whether to restrict map movement to the specified lat/lon bounds. Default is False.
    crs (str): Coordinate Reference System identifier. Default is "EPSG3857".
    control_scale (bool): Whether to display a scale control on the map. Default is False.
    prefer_canvas (bool): Whether to prefer canvas-based rendering over SVG. Default is False.
    no_touch (bool): Whether to disable touch interaction controls. Default is False.
    disable_3d (bool): Whether to disable 3D rendering features. Default is False.
    png_enabled (bool): Whether PNG export functionality is enabled. Default is False.
    zoom_control (bool): Whether to display zoom controls on the map. Default is True.
    **kwargs: Additional keyword arguments passed to the map rendering options parser.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: If location parameter is not a sized variable or doesn't support indexing.
    ValueError: If location doesn't contain exactly two values, or if coordinate values cannot be converted to floats, or if coordinate values contain NaN, or if size values cannot be parsed properly.

## State Changes:
    Attributes READ: 
        - None (this method initializes all attributes)
    Attributes WRITTEN:
        - self._name: Set to "Map"
        - self._env: Set to the global ENV variable
        - self._png_image: Set to None
        - self.png_enabled: Set to the provided png_enabled parameter
        - self.location: Set to [0, 0] if location is None, otherwise validated location coordinates
        - self.width: Set to parsed width value
        - self.height: Set to parsed height value
        - self.left: Set to parsed left value
        - self.top: Set to parsed top value
        - self.position: Set to the provided position parameter
        - self.crs: Set to the provided crs parameter
        - self.control_scale: Set to the provided control_scale parameter
        - self.options: Set to parsed options dictionary
        - self.global_switches: Set to a new GlobalSwitches instance
        - self.objects_to_stay_in_front: Initialized as empty list
        - self.tile_layer: Conditionally added via add_child() if tiles is a TileLayer or truthy string

## Constraints:
    Preconditions:
        - All size parameters (width, height, left, top) must be convertible to valid size specifications
        - Location coordinates must be valid numerical values when provided
        - Zoom parameters must be integers within reasonable ranges
        - CRS identifier must be a valid coordinate reference system string
    Postconditions:
        - The map object is properly initialized with all required attributes
        - The map is associated with a Figure container in the element tree
        - If tiles parameter is truthy, a tile layer is added to the map
        - The map's initial view is configured with appropriate zoom and location

## Side Effects:
    - Creates and associates a Figure container with the map object
    - May instantiate and add a TileLayer to the map's child elements
    - May create a GlobalSwitches instance for managing global rendering options
    - Uses the global ENV variable for template processing

### `folium.folium.Map._repr_html_` · *method*

## Summary:
Returns an HTML representation of the map for display in Jupyter notebooks by delegating to the parent element's HTML representation method.

## Description:
This special method is invoked by Jupyter notebooks to render the map as HTML. When the map doesn't have a parent element assigned, it creates a temporary parent Figure element, delegates the HTML rendering to that parent, and then cleans up the temporary reference. When a parent already exists, it directly delegates to the parent's HTML representation method.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent's _repr_html_ method

## Returns:
    str: HTML string representation of the map suitable for Jupyter notebook display

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: self._parent (temporarily set to None)

## Constraints:
    Preconditions: The method assumes that the parent's _repr_html_ method exists and can handle the provided kwargs
    Postconditions: If self._parent was originally None, it will be restored to None after processing

## Side Effects:
    None

### `folium.folium.Map._to_png` · *method*

## Summary:
Captures and returns a PNG screenshot of the map by rendering HTML in a headless browser.

## Description:
This private method generates a PNG screenshot of the entire folium map by rendering the HTML representation in a headless Firefox browser, taking a screenshot of the map container element, and caching the result. It's primarily used internally by `_repr_png_` for Jupyter notebook display and can be called directly for programmatic screenshot capture.

## Args:
    delay (int): Time in seconds to wait after page load before taking screenshot. Defaults to 3.
    driver (selenium.webdriver.Firefox): Optional existing WebDriver instance to reuse. Defaults to None.

## Returns:
    bytes: PNG image data as bytes representing the rendered map.

## Raises:
    None explicitly raised, but underlying Selenium operations may raise WebDriverException or other browser-related exceptions.

## State Changes:
    Attributes READ: self._png_image, self.get_root()
    Attributes WRITTEN: self._png_image

## Constraints:
    Preconditions:
    - Map instance must be properly initialized with valid configuration
    - Firefox WebDriver must be available if no driver is provided
    - The map must have been rendered to HTML before calling this method
    
    Postconditions:
    - If called for the first time, the PNG image is captured and cached in self._png_image
    - Subsequent calls return the cached image without re-rendering
    - The method is idempotent after the first execution

## Side Effects:
    I/O operations: Creates temporary HTML files for browser rendering
    External service calls: Requires Firefox WebDriver for headless browser automation
    Memory usage: Stores generated PNG data in self._png_image cache
    Process management: Spawns and terminates Firefox WebDriver process

### `folium.folium.Map._repr_png_` · *method*

## Summary:
Returns a PNG image representation of the map for Jupyter notebook display when PNG rendering is enabled.

## Description:
This special method implements the IPython/Jupyter display protocol for PNG representation. It is automatically called by Jupyter notebooks when displaying Map objects. The method checks the `png_enabled` flag and, if enabled, generates and returns a PNG screenshot of the map using Selenium WebDriver. When PNG rendering is disabled, it returns None to indicate that HTML representation should be used instead.

## Args:
    None

## Returns:
    bytes or None: PNG image data as bytes if PNG rendering is enabled, otherwise None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.png_enabled, self._to_png
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Map instance must be properly initialized with valid configuration
    Postconditions: If PNG is enabled and generated, the PNG image is cached in self._png_image for subsequent calls

## Side Effects:
    I/O operations: Creates temporary HTML files and uses Selenium WebDriver to capture screenshots
    External service calls: Requires Firefox WebDriver for headless browser automation
    Memory usage: Stores generated PNG data in self._png_image cache

### `folium.folium.Map.render` · *method*

## Summary:
Adds CSS styling and global configuration elements to the map's figure header before rendering the complete HTML output.

## Description:
This method prepares the map element for rendering by injecting essential CSS styles and global configuration switches into the figure's header. It ensures proper HTML layout and styling for the map display, then delegates to the parent class's rendering mechanism to generate the final HTML output. This method is typically called during the map rendering lifecycle when converting the map structure into HTML/JavaScript code.

The method is separated from inline logic to ensure consistent styling and configuration handling across all folium map elements, and to maintain clean separation of concerns between layout preparation and actual HTML generation.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method for final HTML generation.

## Returns:
    None: This method doesn't return any value.

## Raises:
    AssertionError: When the map element is not contained within a Figure instance, indicating improper usage.

## State Changes:
    Attributes READ: 
        - self.global_switches: Configuration switches for map behavior (touch, 3D rendering)
        - self.get_root(): Retrieves the parent figure container
    
    Attributes WRITTEN: 
        - figure.header: Modified by adding CSS style elements and global switches

## Constraints:
    Preconditions:
        - The map instance must be contained within a Figure instance (validated via self.get_root())
        - The map must have a valid global_switches attribute configured during initialization
        - All CSS style definitions must be properly formatted strings
        
    Postconditions:
        - The figure's header contains CSS styles for full-page layout and absolute positioning
        - The figure's header contains the global switches configuration
        - The parent Element.render() method is called with all provided kwargs for final HTML generation

## Side Effects:
    - Mutates the figure's header by adding child elements (CSS style elements and global switches)
    - Calls the parent Element.render() method which likely generates the final HTML output
    - May raise AssertionError if validation fails

### `folium.folium.Map.show_in_browser` · *method*

## Summary:
Displays the map in a web browser by rendering it to a temporary HTML file and opening it in the default browser.

## Description:
This method generates a complete HTML representation of the map, saves it to a temporary file, and opens it in the user's default web browser. It then waits indefinitely for user interruption (Ctrl+C) to allow the browser window to remain open. This method is primarily used for interactive map previewing during development or debugging.

The method is separated from inline logic to provide a clean interface for displaying maps in browsers without requiring manual HTML generation or file management. It leverages the existing rendering infrastructure of the folium map system.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised, but underlying operations may raise exceptions from:
    - File I/O operations during temporary file creation/deletion
    - Browser opening operations if the default browser cannot be launched
    - System-specific errors during sleep operations

## State Changes:
    Attributes READ: 
    - self._parent: Implicitly accessed through get_root() to retrieve the parent Figure object
    
    Attributes WRITTEN:
    - None

## Constraints:
    Preconditions:
    - The Map instance must be properly initialized with valid content
    - The Map instance must be contained within a Figure context (which happens automatically during Map initialization)
    - The system must have permission to create temporary files and launch the default web browser
    
    Postconditions:
    - A temporary HTML file is created containing the rendered map
    - The default web browser is launched with the temporary HTML file
    - The program enters an infinite loop waiting for user interruption

## Side Effects:
    - Creates a temporary HTML file on the filesystem
    - Opens the default web browser to display the map
    - Blocks execution indefinitely until Ctrl+C is pressed
    - May cause system resource consumption due to the infinite loop

### `folium.folium.Map.fit_bounds` · *method*

## Summary:
Adjusts the map view to fit specified geographical bounds by adding a FitBounds child element.

## Description:
The `fit_bounds` method configures the map to automatically adjust its viewport to encompass specified geographical boundaries. It creates a `FitBounds` element with the provided parameters and adds it as a child to the map, which triggers the map rendering system to set the appropriate map center and zoom level.

This method is commonly used to programmatically set map views to show specific regions, such as bounding boxes around points of interest, countries, or custom-defined areas. It's particularly useful when you have geographical coordinates defining an area you want to display and want the map to automatically zoom and pan to show that area.

## Args:
- bounds (list): A list of two coordinate pairs [[lat1, lon1], [lat2, lon2]] representing the geographical boundaries to fit. Each coordinate pair should contain valid latitude and longitude values.
- padding_top_left (list, optional): A list of two integers [x, y] representing pixel padding from the top-left corner. Defaults to None.
- padding_bottom_right (list, optional): A list of two integers [x, y] representing pixel padding from the bottom-right corner. Defaults to None.
- padding (list, optional): A list of two integers [x, y] representing uniform pixel padding from all sides. Defaults to None.
- max_zoom (int, optional): Maximum zoom level to use when fitting bounds. Defaults to None.

## Returns:
- None: This method does not return a value.

## Raises:
- None explicitly raised by this method, though underlying validation may occur during map rendering or when the template is processed through the `FitBounds` class.

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: None

## Constraints:
- Preconditions: The `bounds` parameter must contain valid geographical coordinates in the format [[latitude_min, longitude_min], [latitude_max, longitude_max]].
- Postconditions: The map will have a `FitBounds` child element added that will affect the map's viewport during rendering.

## Side Effects:
- Adds a `FitBounds` child element to the map's children collection.
- The actual map adjustment is handled automatically by the folium map rendering system during the rendering phase.

### `folium.folium.Map.choropleth` · *method*

## Summary:
Issues a deprecation warning and adds a choropleth layer to the map using the Choropleth class.

## Description:
This method provides a deprecated interface for adding choropleth layers to a folium Map. It issues a FutureWarning indicating that users should instead instantiate the Choropleth class directly. The method creates a Choropleth object with the provided arguments and adds it as a child to the map, enabling visualization of geospatial data with color-coded regions.

## Args:
    *args: Variable length argument list passed directly to the Choropleth constructor.
    **kwargs: Arbitrary keyword arguments passed directly to the Choropleth constructor.

## Returns:
    None: This method does not return a value.

## Raises:
    FutureWarning: Always raised to indicate deprecation of this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Map instance must be properly initialized.
    Postconditions: The choropleth layer is added to the map's children collection.

## Side Effects:
    Issues a FutureWarning to stdout.
    Creates a Choropleth object and adds it to the map's child elements.

### `folium.folium.Map.keep_in_front` · *method*

## Summary:
Appends map elements to a list that will be rendered in front of other map elements during rendering.

## Description:
The `keep_in_front` method adds one or more map elements to the `objects_to_stay_in_front` list, which is used during map rendering to ensure these elements are displayed above other map components. This functionality is commonly used to bring markers, popups, tooltips, or other interactive elements to the forefront of the map visualization, preventing them from being obscured by other map features like tile layers or overlays.

This method provides a clean interface for managing element ordering in folium maps, allowing users to specify which elements should maintain a higher visual priority during rendering. The method is intentionally simple and lightweight, serving as a direct accessor to modify the internal rendering order list.

## Args:
    *args: Variable length argument list of map elements (markers, popups, tooltips, etc.) to be kept in front of other map elements.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.objects_to_stay_in_front: Appended with each element in args

## Constraints:
    Preconditions:
        - The map object must be properly initialized with `objects_to_stay_in_front` as an empty list
        - Each element in args must be a valid folium map element that can be rendered
    Postconditions:
        - All elements in args are appended to the `objects_to_stay_in_front` list
        - The list maintains the order of elements as they were added

## Side Effects:
    None: This method does not produce any side effects beyond modifying the internal `objects_to_stay_in_front` list.

