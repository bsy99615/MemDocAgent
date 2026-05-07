# `folium.py`

## `folium.folium.GlobalSwitches` · *class*

## Summary:
Manages global configuration switches for folium map rendering, specifically controlling touch interaction and 3D rendering behaviors.

## Description:
The GlobalSwitches class provides a mechanism to configure global settings for folium maps. It inherits from Element and allows users to control whether touch interactions are enabled and whether 3D rendering features are disabled. This class is typically used internally by folium to manage global rendering options that affect the entire map display.

The no_touch flag controls whether the map will respond to touch events (useful for disabling touch interactions on desktop browsers or for mobile-specific configurations). The disable_3d flag controls whether 3D rendering features are enabled in the map visualization.

## State:
- no_touch (bool): When True, disables touch interaction capabilities for the map. Defaults to False.
- disable_3d (bool): When True, disables 3D rendering features. Defaults to False.
- _name (str): Set to "GlobalSwitches" to identify this element type.
- _template (Template): Jinja2 template object (currently defined but empty in source code).

## Lifecycle:
- Creation: Instantiate with optional no_touch and disable_3d boolean parameters
- Usage: Typically used internally by folium when rendering maps
- Destruction: Managed automatically through Element lifecycle

## Method Map:
```mermaid
graph TD
    A[GlobalSwitches.__init__] --> B[Element.__init__]
    B --> C[Sets _name="GlobalSwitches"]
    C --> D[Sets no_touch and disable_3d attributes]
```

## Raises:
- No explicit exceptions raised during initialization

## Example:
```python
# Create global switches with default settings
switches = GlobalSwitches()

# Create global switches with custom settings
switches = GlobalSwitches(no_touch=True, disable_3d=True)
```

### `folium.folium.GlobalSwitches.__init__` · *method*

## Summary:
Initializes a GlobalSwitches object with configuration options for touch and 3D rendering behavior.

## Description:
Configures global rendering switches for folium maps, specifically controlling touch interaction and 3D rendering capabilities. This method sets up the object's state with boolean flags that influence how the map behaves in different environments. The GlobalSwitches class is typically used internally by folium to manage global configuration settings.

## Args:
    no_touch (bool): Disables touch interaction features when True. Defaults to False.
    disable_3d (bool): Disables 3D rendering features when True. Defaults to False.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "GlobalSwitches" string
    - self.no_touch: Set to the provided no_touch parameter value
    - self.disable_3d: Set to the provided disable_3d parameter value

## Constraints:
    Preconditions: None
    Postconditions: The GlobalSwitches object is properly initialized with the specified configuration flags.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

## `folium.folium.Map` · *class*

## Summary:
Represents an interactive map element that can be rendered in HTML and displayed in a browser, built using Leaflet.js.

## Description:
The Map class is the central component for creating interactive maps in folium. It serves as the main container for all map-related elements such as markers, layers, and controls. Users instantiate this class to create a map canvas with customizable properties like location, zoom level, tile sources, and styling. The class inherits from JSCSSMixin and MacroElement, providing automatic JavaScript/CSS resource management and element composition capabilities.

The Map class is designed to be the foundation for building complex geospatial visualizations. It handles the core map configuration, rendering pipeline, and integration with Leaflet.js through templating and JavaScript injection. It supports various map tile providers, coordinate reference systems, and interactive features like zoom controls and scale indicators.

## State:
- location (list): Center coordinates of the map as [latitude, longitude]. Defaults to [0, 0] when no location is specified.
- width (tuple): Width of the map container in pixels or percentage format (value, unit).
- height (tuple): Height of the map container in pixels or percentage format (value, unit).
- left (tuple): Left positioning of the map container (value, unit).
- top (tuple): Top positioning of the map container (value, unit).
- position (str): CSS positioning property for the map container ('absolute', 'relative', etc.).
- crs (str): Coordinate Reference System identifier (defaults to 'EPSG3857').
- control_scale (bool): Whether to display a scale control on the map.
- options (dict): Configuration options for the Leaflet map, including zoom settings and controls.
- global_switches (GlobalSwitches): Object managing global map behavior flags like touch interaction and 3D rendering.
- objects_to_stay_in_front (list): Collection of map objects that should remain visually in front of other elements.
- png_enabled (bool): Flag indicating whether PNG screenshot capability is enabled.
- _png_image (bytes or None): Cached PNG image data when screenshots are taken.
- _name (str): Fixed value "Map" identifying this element type.
- _env (Environment): Jinja2 environment for template rendering.
- _template (Template): Jinja2 template object (empty in source code).

## Lifecycle:
- Creation: Instantiate with location, dimensions, tile provider, and other configuration options. The constructor automatically initializes the map with a default view centered at [0, 0] if no location is provided.
- Usage: Add child elements like markers, layers, and controls using the add_child() method. Render the map using the render() method to generate HTML output.
- Destruction: Cleanup occurs automatically through the Element's parent-child relationship management when the map is removed from its parent Figure.

## Method Map:
```mermaid
graph TD
    A[Map.__init__] --> B[super().__init__()]
    B --> C[Set _name = "Map"]
    C --> D[Set _env = ENV]
    D --> E[Set _png_image = None]
    E --> F[Set png_enabled]
    F --> G{location is None?}
    G -- Yes --> H[Set location = [0, 0]]
    G -- No --> I[Set location = validate_location(location)]
    H --> J[Figure().add_child(self)]
    I --> J
    J --> K[Set width, height, left, top, position]
    K --> L[Set max_bounds_array]
    L --> M[Set crs, control_scale]
    M --> N[Set options via parse_options]
    N --> O[Set global_switches]
    O --> P[Initialize objects_to_stay_in_front]
    P --> Q{tiles is TileLayer?}
    Q -- Yes --> R[add_child(tiles)]
    Q -- No --> S[Create TileLayer and add_child]
    
    A --> T[Map.render] --> U[get_root()]
    U --> V[assert isinstance(figure, Figure)]
    V --> W[Add global_switches to figure.header]
    W --> X[Add CSS styles to figure.header]
    X --> Y[super().render(**kwargs)]
    
    A --> Z[Map.show_in_browser] --> AA[temp_html_filepath]
    AA --> AB[webbrowser.open(fname)]
    AB --> AC[time.sleep(100) loop]
    
    A --> AD[Map.fit_bounds] --> AE[Add FitBounds child]
    
    A --> AF[Map.choropleth] --> AG[Warn and add Choropleth child]
    
    A --> AH[Map.keep_in_front] --> AI[Append to objects_to_stay_in_front]
```

## Raises:
- ValueError: When location coordinates cannot be validated or parsed (via validate_location).
- AssertionError: When the map is rendered without being contained within a Figure instance.
- ValueError: When size specifications cannot be parsed (via _parse_size).

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
folium.Marker(
    location=[40.7128, -74.0060],
    popup="New York City"
).add_to(m)

# Fit the map to show a specific bounding box
bounds = [[40.7, -74.1], [40.8, -73.9]]
m.fit_bounds(bounds)

# Display the map
m.show_in_browser()
```

### `folium.folium.Map.__init__` · *method*

## Summary:
Initializes a Folium Map object with configurable geographic display properties and rendering options.

## Description:
The Map.__init__ method constructs a new map instance with customizable geographic parameters, size specifications, tile layers, and rendering behaviors. This constructor sets up the foundational configuration that determines how the map will be displayed and behave.

The method handles initialization tasks including:
- Setting up basic map properties like location, size, and positioning
- Configuring tile layers for geographic data visualization  
- Initializing global rendering switches for touch and 3D behaviors
- Establishing map bounds and coordinate reference systems

This logic is implemented as a separate method because it performs complex initialization that needs to be reusable and maintainable, especially given the numerous configuration options and the need to properly set up the underlying element hierarchy.

## Args:
    location (list, tuple, or None): Geographic center coordinates [latitude, longitude]. If None, defaults to [0, 0] with zoom level 1.
    width (str or number): Map width as percentage or pixels. Defaults to "100%".
    height (str or number): Map height as percentage or pixels. Defaults to "100%".
    left (str or number): Map left offset as percentage or pixels. Defaults to "0%".
    top (str or number): Map top offset as percentage or pixels. Defaults to "0%".
    position (str): CSS position property. Defaults to "relative".
    tiles (str or TileLayer): Tile layer source identifier or TileLayer instance. Defaults to "OpenStreetMap".
    attr (str or None): Tile layer attribution string. Defaults to None.
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
    zoom_control (bool): Whether to show zoom controls. Defaults to True.
    **kwargs: Additional options passed to the map rendering engine.

## Returns:
    None: This method initializes the object state and does not return a value.

## Raises:
    TypeError: If location is not a sized variable (doesn't support len()) or doesn't support indexing.
    ValueError: If location doesn't contain exactly two values, or if the values cannot be converted to floats, or if values contain NaN.

## State Changes:
    Attributes WRITTEN: 
        - self._name: Set to "Map"
        - self._env: Set to ENV global variable
        - self._png_image: Set to None
        - self.png_enabled: Set to png_enabled parameter value
        - self.location: Set to validated location or [0, 0] if location is None
        - self.width: Set to parsed width value
        - self.height: Set to parsed height value
        - self.left: Set to parsed left value
        - self.top: Set to parsed top value
        - self.position: Set to position parameter value
        - self.crs: Set to crs parameter value
        - self.control_scale: Set to control_scale parameter value
        - self.options: Set to parsed options dictionary
        - self.global_switches: Set to GlobalSwitches instance
        - self.objects_to_stay_in_front: Set to empty list

## Constraints:
    Preconditions:
        - Location parameter must be None or a valid geographic coordinate pair
        - Width, height, left, top parameters must be parseable by _parse_size
        - Zoom parameters must be integers within reasonable ranges
        - CRS must be a valid coordinate reference system identifier
    Postconditions:
        - Map object is initialized with proper default values
        - Map has a valid geographic center location
        - Map has configured dimensions and positioning
        - Map has appropriate tile layer setup
        - Map has valid global switch configurations

## Side Effects:
    - Adds a Figure element to the map's parent hierarchy via Figure().add_child(self)
    - May create and add TileLayer child elements to the map
    - Sets up global environment variables for map rendering

### `folium.folium.Map._repr_html_` · *method*

## Summary:
Returns the HTML representation of the map for Jupyter notebook display by ensuring proper parent-child relationship setup.

## Description:
This special method is invoked by Jupyter notebooks to display the map as HTML. When the map has no parent (i.e., `self._parent` is None), it temporarily creates a Figure object, adds itself to that figure, generates the HTML representation from the parent, and then cleans up by setting the parent reference back to None. When the map already has a parent, it directly delegates to the parent's `_repr_html_` method.

## Args:
    **kwargs: Additional keyword arguments passed to the parent's _repr_html_ method

## Returns:
    str: HTML string representation of the map suitable for Jupyter notebook display

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: self._parent (temporarily modified during execution)

## Constraints:
    Preconditions: The map object must be properly initialized and have valid configuration
    Postconditions: The returned HTML string represents a valid map visualization that can be rendered in Jupyter

## Side Effects:
    I/O: Creates a temporary Figure object when self._parent is None
    Mutation: Temporarily modifies self._parent during execution to enable proper HTML generation

### `folium.folium.Map._to_png` · *method*

## Summary:
Generates and caches a PNG screenshot of the map visualization using Selenium WebDriver.

## Description:
This method creates a PNG representation of the current map state by rendering the HTML content in a headless Firefox browser and taking a screenshot. The result is cached in `self._png_image` to avoid repeated expensive operations. This method is primarily used internally by `_repr_png_` to enable Jupyter notebook display of map visualizations.

## Args:
    delay (int): Time in seconds to wait for page rendering before taking screenshot. Defaults to 3.
    driver: Optional Selenium WebDriver instance. If None, a new headless Firefox driver is created.

## Returns:
    bytes: PNG image data as bytes representing the rendered map visualization.

## Raises:
    None

## State Changes:
    Attributes READ: self._png_image, self.get_root()
    Attributes WRITTEN: self._png_image

## Constraints:
    Preconditions:
    - The Map object must be properly initialized with valid configuration
    - The map must have been added to a Figure context before calling
    - Selenium WebDriver must be available in the environment
    
    Postconditions:
    - If called for the first time, `self._png_image` is set to the generated PNG data
    - Subsequent calls return the cached PNG data without re-rendering
    - The method is safe to call multiple times

## Side Effects:
    I/O: Creates temporary HTML file for rendering
    External dependency: Requires Selenium WebDriver and Firefox browser installation
    Resource management: Automatically quits the Selenium driver after use

### `folium.folium.Map._repr_png_` · *method*

## Summary:
Returns the PNG representation of the map for Jupyter notebook display when PNG rendering is enabled.

## Description:
This special method implements the IPython/Jupyter display protocol for PNG image representation. It is automatically invoked by Jupyter notebooks when displaying Map objects. The method checks if PNG rendering is enabled via the `png_enabled` attribute and, if so, generates and returns the PNG image data. This allows users to view map visualizations directly in Jupyter notebooks without needing to export to HTML.

## Args:
    None

## Returns:
    bytes or None: PNG image data as bytes when PNG rendering is enabled, None otherwise

## Raises:
    None

## State Changes:
    Attributes READ: self.png_enabled, self._to_png
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Map object must be properly initialized with valid configuration
    Postconditions: If PNG rendering is enabled, returns valid PNG image data; if disabled, returns None

## Side Effects:
    I/O: May trigger Selenium-based HTML rendering and screenshot capture when _to_png is called
    External dependency: Uses Selenium WebDriver for browser automation when generating PNGs

### `folium.folium.Map.render` · *method*

## Summary:
Injects CSS styling and global configuration elements into the map's rendering context before delegating to parent rendering logic.

## Description:
This method prepares the map element for HTML rendering by adding essential CSS styles and global configuration switches to the parent Figure's header. It ensures proper layout styling for the map container and includes necessary global configuration elements before continuing with the standard rendering process.

The method is part of the map rendering lifecycle, called when the map needs to be converted to HTML format. It's typically invoked internally during the rendering process when the map is part of a Figure context, rather than being called directly by user code.

## Args:
    **kwargs: Additional keyword arguments passed through to the parent render method for further processing

## Returns:
    None: This method does not return a value

## Raises:
    AssertionError: When the map element is not contained within a Figure instance, indicating improper usage

## State Changes:
    Attributes READ: 
    - self.global_switches (retrieved to add to figure header)
    - self.get_root() (called to obtain parent figure context)
    
    Attributes WRITTEN: 
    - No direct attribute modifications on self

## Constraints:
    Preconditions:
    - The map element must be added to a Figure instance before calling this method
    - The map element must have a valid global_switches attribute that can be added to a figure header
    
    Postconditions:
    - The figure's header contains CSS styles for html/body positioning and map container sizing
    - The figure's header contains the global_switches element for configuration
    - The parent render method is invoked with provided kwargs to complete the rendering process

## Side Effects:
    - Modifies the parent Figure's header by adding CSS style elements and the global_switches element
    - Invokes the parent class's render method which may perform additional rendering operations

### `folium.folium.Map.show_in_browser` · *method*

## Summary:
Displays the interactive map in a web browser by rendering it to HTML and opening in the default browser.

## Description:
This method renders the map's HTML representation to a temporary file and opens it in the user's default web browser. It provides a convenient way to view the interactive map without needing to manually save and open HTML files. The method blocks execution until the user interrupts it with Ctrl+C.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self (the Map instance, implicitly accessed through self.get_root())
    
    Attributes WRITTEN: 
    - None

## Constraints:
    Preconditions:
    - The Map instance must have been properly initialized with valid map data
    - The map must have a valid root element that can be rendered to HTML
    
    Postconditions:
    - A temporary HTML file is created and opened in the default web browser
    - Execution continues in a blocking loop until interrupted by Ctrl+C

## Side Effects:
    - Creates a temporary HTML file on the filesystem
    - Opens the default web browser to display the map
    - Blocks execution indefinitely until interrupted by Ctrl+C
    - Uses system resources for temporary file creation and browser launch

### `folium.folium.Map.fit_bounds` · *method*

## Summary:
Adjusts the map view to fit specified geographical bounds by adding a FitBounds control element.

## Description:
Configures the map to automatically adjust its zoom level and center coordinates to ensure that the provided geographical bounds are visible within the map viewport. This method creates a FitBounds control element and adds it to the map, which will execute the bounds-fitting logic when the map is rendered.

The fit_bounds method is particularly useful when you want to display a specific area or region on the map without manually calculating the appropriate zoom level and center coordinates. It provides a convenient way to programmatically control the initial map view or dynamically update it based on geographical data.

This logic is encapsulated in its own method rather than being inlined because it represents a distinct map configuration operation that can be reused and composed with other map operations. It also allows for clean separation of concerns between map creation and view configuration.

## Args:
    bounds (list): A list of two coordinate pairs [[lat1, lng1], [lat2, lng2]] representing the geographical boundaries to fit. Each coordinate pair should be in [latitude, longitude] format.
    padding_top_left (tuple, optional): Tuple of (left, top) padding in pixels to apply to the bounds. Defaults to None.
    padding_bottom_right (tuple, optional): Tuple of (right, bottom) padding in pixels to apply to the bounds. Defaults to None.
    padding (tuple, optional): Tuple of (left, top, right, bottom) padding in pixels to apply to all sides. Defaults to None.
    max_zoom (int, optional): Maximum zoom level to use when fitting bounds. Defaults to None.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised by this method, but underlying operations may raise exceptions from FitBounds initialization or add_child operations.

## State Changes:
    Attributes READ: 
        - None explicitly read from self
    Attributes WRITTEN:
        - None explicitly written to self

## Constraints:
    Preconditions:
        - Bounds parameter must be a list or tuple containing exactly two coordinate pairs
        - Each coordinate pair must be in [latitude, longitude] format
        - Coordinates must be valid numeric values
    Postconditions:
        - A FitBounds element is added to the map's child elements
        - The map's view configuration will be updated when rendered to fit the specified bounds

## Side Effects:
    - Adds a FitBounds child element to the map's element hierarchy
    - Modifies the map's child elements collection

### `folium.folium.Map.choropleth` · *method*

## Summary:
Adds a choropleth layer to the map by creating and registering a Choropleth feature.

## Description:
This method provides a deprecated interface for adding choropleth visualizations to a Folium map. It issues a FutureWarning indicating that users should instead instantiate the Choropleth class directly. The method forwards all arguments to the Choropleth constructor and registers the resulting choropleth layer with the map.

## Args:
    *args: Variable length argument list passed to the Choropleth constructor.
    **kwargs: Arbitrary keyword arguments passed to the Choropleth constructor.

## Returns:
    None: This method does not return a value.

## Raises:
    FutureWarning: Always raised to indicate deprecation of this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method assumes the calling object is a Map instance with an add_child method.
    Postconditions: The map object will have a new choropleth layer added to its children collection.

## Side Effects:
    Issues a FutureWarning to the user about deprecation.
    Creates a Choropleth object and adds it to the map's children collection.

### `folium.folium.Map.keep_in_front` · *method*

*No documentation generated.*

