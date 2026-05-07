# `folium.py`

## `folium.folium.GlobalSwitches` · *class*

## Summary:
A configuration element that manages global switch settings for folium map rendering, controlling touch interaction and 3D rendering behaviors.

## Description:
The GlobalSwitches class represents a configuration element that sets global flags for folium map rendering. It is designed to control low-level rendering behaviors such as touch interaction handling and 3D rendering capabilities. This class is typically instantiated internally by folium when creating map objects and is not usually created directly by end users.

The class inherits from Element, making it compatible with folium's element system for HTML template rendering and map composition. It provides two key configuration options that affect how maps behave in different environments.

## State:
- no_touch (bool): When True, disables touch interaction features for the map. Defaults to False.
- disable_3d (bool): When True, disables 3D rendering capabilities for the map. Defaults to False.
- _name (str): Set to "GlobalSwitches" to identify this element type in folium's element hierarchy.

## Lifecycle:
- Creation: Instantiated with optional boolean parameters no_touch and disable_3d, defaults to False for both.
- Usage: Automatically integrated into folium map objects during map construction and rendering.
- Destruction: Managed automatically by folium's element lifecycle management system.

## Method Map:
```mermaid
graph TD
    A[GlobalSwitches.__init__] --> B[Element.__init__]
    B --> C[Sets _name="GlobalSwitches"]
    C --> D[Sets no_touch parameter]
    D --> E[Sets disable_3d parameter]
```

## Raises:
- No explicit exceptions are raised by the constructor based on the provided source code.

## Example:
```python
# Typically created internally by folium
switches = GlobalSwitches(no_touch=True, disable_3d=False)
# Used internally by folium when rendering maps
```

### `folium.folium.GlobalSwitches.__init__` · *method*

## Summary:
Initializes a GlobalSwitches object with configuration options for touch and 3D rendering behavior.

## Description:
This constructor method sets up the GlobalSwitches object, which is used to configure global rendering options for folium maps. It inherits from the Element base class and initializes key configuration flags that affect how the map behaves in different environments.

## Args:
    no_touch (bool): When True, disables touch interactions for the map. Defaults to False.
    disable_3d (bool): When True, disables 3D rendering features. Defaults to False.

## Returns:
    None: This method initializes the object's state and does not return a value.

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
    None: This method performs only local object initialization and has no external side effects.

## `folium.folium.Map` · *class*

## Summary:
Represents an interactive Leaflet map that can be customized with various layers, controls, and styling options.

## Description:
The Map class serves as the main container for creating interactive web maps using Leaflet.js. It provides a high-level interface for configuring map properties such as location, zoom level, tile layers, and coordinate reference systems. The class is designed to be instantiated by users who want to create maps with custom features and visualizations.

This class acts as the central hub for all map-related functionality in Folium, managing the map's configuration, rendering process, and integration with various map components like markers, polygons, and tile layers. It inherits from JSCSSMixin and MacroElement, providing JavaScript/CSS handling capabilities and element management.

## State:
- location: list[float], default [0, 0] - The initial center coordinates of the map [latitude, longitude]
- width: tuple[int, str], parsed from string - Width of the map container (e.g., "100%", 800)
- height: tuple[int, str], parsed from string - Height of the map container (e.g., "100%", 600)
- left: tuple[int, str], parsed from string - Left positioning of the map container
- top: tuple[int, str], parsed from string - Top positioning of the map container
- position: str, default "relative" - CSS positioning property for the map container
- crs: str, default "EPSG3857" - Coordinate Reference System for the map
- control_scale: bool, default False - Whether to display the scale control
- options: dict - Configuration options for the Leaflet map instance
- global_switches: GlobalSwitches - Object containing global map switches (no_touch, disable_3d)
- objects_to_stay_in_front: list - Objects that should remain in front of other map elements
- png_enabled: bool, default False - Whether PNG rendering is enabled
- _png_image: bytes or None - Cached PNG image of the map
- _name: str, fixed "Map" - Internal identifier for the map element
- _env: Environment - Jinja2 template environment for rendering
- _template: Template - Jinja2 template for HTML rendering (empty in provided code)

## Lifecycle:
Creation: Instantiate with location, size, and other configuration parameters. The constructor handles initialization of map properties, setting up the parent-child relationship with a Figure, and adding default tile layers.

Usage: Add map features using methods like add_child(), fit_bounds(), and keep_in_front(). Render the map using render() or display it in browser using show_in_browser().

Destruction: The map object manages its own cleanup through the parent-child relationship with Figure elements. When the map is no longer referenced, Python's garbage collection handles cleanup.

## Method Map:
```mermaid
graph TD
    A[Map.__init__] --> B[Figure.add_child]
    A --> C[TileLayer.add_child]
    A --> D[parse_options]
    A --> E[GlobalSwitches]
    
    F[Map.render] --> G[super().render]
    F --> H[figure.header.add_child]
    
    I[Map.show_in_browser] --> J[temp_html_filepath]
    I --> K[webbrowser.open]
    
    L[Map.fit_bounds] --> M[FitBounds.add_child]
    
    N[Map.choropleth] --> O[Choropleth.add_child]
    
    P[Map.keep_in_front] --> Q[objects_to_stay_in_front.append]
    
    R[Map._to_png] --> S[webdriver.Firefox]
    R --> T[temp_html_filepath]
    R --> U[driver.screenshot]
```

## Raises:
- ValueError: When location coordinates are invalid or cannot be parsed
- TypeError: When location is not a sized variable or contains non-numerical values
- AssertionError: When map rendering is attempted outside of a Figure context

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

# Fit the map to show all features
m.fit_bounds([[40.7, -74.1], [40.8, -73.9]])

# Display the map in browser
m.show_in_browser()
```

### `folium.folium.Map.__init__` · *method*

## Summary:
Initializes a Map object with configurable display properties, location settings, and tile layers.

## Description:
Configures the base map instance with positioning, sizing, coordinate reference system, and tile layer settings. This method establishes the foundational properties of a Folium map, including its geographical bounds, visual dimensions, and rendering options.

## Args:
    location (list, optional): Initial map center coordinates [latitude, longitude]. Defaults to None, which centers the map at [0, 0].
    width (str): Map width as percentage or pixel value. Defaults to "100%".
    height (str): Map height as percentage or pixel value. Defaults to "100%".
    left (str): Map left offset as percentage or pixel value. Defaults to "0%".
    top (str): Map top offset as percentage or pixel value. Defaults to "0%".
    position (str): CSS position property. Defaults to "relative".
    tiles (str or TileLayer): Tile layer source identifier or TileLayer instance. Defaults to "OpenStreetMap".
    attr (str, optional): Tile layer attribution string. Defaults to None.
    min_zoom (int): Minimum zoom level allowed. Defaults to 0.
    max_zoom (int): Maximum zoom level allowed. Defaults to 18.
    zoom_start (int): Initial zoom level. Defaults to 10.
    min_lat (float): Minimum latitude bound. Defaults to -90.
    max_lat (float): Maximum latitude bound. Defaults to 90.
    min_lon (float): Minimum longitude bound. Defaults to -180.
    max_lon (float): Maximum longitude bound. Defaults to 180.
    max_bounds (bool): Whether to restrict map to bounding box. Defaults to False.
    crs (str): Coordinate Reference System. Defaults to "EPSG3857".
    control_scale (bool): Whether to show scale control. Defaults to False.
    prefer_canvas (bool): Whether to prefer canvas rendering. Defaults to False.
    no_touch (bool): Disable touch interactions. Defaults to False.
    disable_3d (bool): Disable 3D features. Defaults to False.
    png_enabled (bool): Enable PNG export capability. Defaults to False.
    zoom_control (bool): Show zoom controls. Defaults to True.
    **kwargs: Additional options passed to map configuration.

## Returns:
    None: This is a constructor method that initializes the Map instance.

## Raises:
    TypeError: When location is not a sized variable (list, tuple, etc.).
    ValueError: When location doesn't contain exactly 2 numerical values or contains NaNs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "Map"
    - self._env: Set to ENV
    - self._png_image: Set to None
    - self.png_enabled: Set to png_enabled parameter
    - self.location: Set based on location parameter
    - self.width: Set by parsing width parameter
    - self.height: Set by parsing height parameter
    - self.left: Set by parsing left parameter
    - self.top: Set by parsing top parameter
    - self.position: Set to position parameter
    - self.crs: Set to crs parameter
    - self.control_scale: Set to control_scale parameter
    - self.options: Set by parsing options
    - self.global_switches: Set to GlobalSwitches instance
    - self.objects_to_stay_in_front: Initialized as empty list

## Constraints:
    Preconditions:
    - Location values must be convertible to float
    - Location must contain exactly 2 values (latitude, longitude)
    - Width and height must be valid size specifications (percentage or numeric)
    - Zoom levels must be integers within reasonable ranges
    
    Postconditions:
    - Map instance is properly initialized with default or provided values
    - Map has a valid coordinate reference system
    - Map has appropriate default zoom level when no location is provided

## Side Effects:
    - Creates and adds a Figure element to the map hierarchy
    - May create and add TileLayer child elements
    - Sets up global switches for map behavior

### `folium.folium.Map._repr_html_` · *method*

## Summary:
Returns the HTML representation of the map for Jupyter notebook display, ensuring proper parent-child relationship for rendering.

## Description:
This special method is invoked by Jupyter notebooks to display HTML representations of Map objects. It ensures that the map has a proper parent container (Figure) before generating its HTML representation, which is necessary for correct rendering in notebook environments. When the map doesn't have a parent, it temporarily creates one, generates the HTML, and then cleans up the temporary parent reference.

## Args:
    **kwargs: Additional keyword arguments passed to the parent's _repr_html_ method

## Returns:
    str: HTML string representation of the map suitable for Jupyter notebook display

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._parent
    Attributes WRITTEN: self._parent (temporarily modified during execution)

## Constraints:
    Preconditions: The map object must be properly initialized
    Postconditions: The returned HTML string represents a valid HTML view of the map

## Side Effects:
    None

### `folium.folium.Map._to_png` · *method*

## Summary:
Converts the map to a PNG image by rendering it in a browser and taking a screenshot.

## Description:
This method renders the map as HTML, opens it in a headless Firefox browser, waits for the page to load, and captures a screenshot of the map element. The resulting PNG image is cached in the instance for future calls.

## Args:
    delay (int): Number of seconds to wait before taking the screenshot. Defaults to 3.
    driver: Optional Selenium WebDriver instance to use. If None, creates a new headless Firefox driver.

## Returns:
    bytes: PNG image data of the rendered map.

## Raises:
    None explicitly raised, but may raise Selenium-related exceptions if browser automation fails.

## State Changes:
    Attributes READ: self._png_image, self.get_root()
    Attributes WRITTEN: self._png_image

## Constraints:
    Preconditions: The map must be properly initialized with valid HTML content.
    Postconditions: The PNG image is stored in self._png_image and returned.

## Side Effects:
    I/O: Creates temporary HTML file and deletes it after use.
    External service calls: Uses Selenium WebDriver with Firefox browser.
    Browser automation: Launches and quits Firefox process.

### `folium.folium.Map._repr_png_` · *method*

## Summary:
Returns a PNG image representation of the map for Jupyter notebook display when PNG rendering is enabled.

## Description:
This method implements the IPython/Jupyter display protocol for PNG output. When a Map object is displayed in a Jupyter notebook cell, Jupyter looks for special methods like `_repr_png_()` to determine how to render the object. This method checks if PNG rendering is enabled via the `png_enabled` attribute and returns the PNG image data if available.

The method delegates to `_to_png()` which uses Selenium WebDriver to render the map as a PNG screenshot. This enables rich visual display of interactive maps directly in Jupyter notebooks without requiring separate HTML rendering.

## Args:
    None

## Returns:
    bytes or None: PNG image data as bytes if PNG rendering is enabled, otherwise None

## Raises:
    None

## State Changes:
    Attributes READ: self.png_enabled, self._png_image
    Attributes WRITTEN: self._png_image (only when it's None and needs to be populated)

## Constraints:
    Preconditions: The Map instance must be properly initialized with appropriate attributes
    Postconditions: If PNG rendering is enabled, the method will return PNG image data or None

## Side Effects:
    I/O: May initialize a Selenium WebDriver and perform headless browser operations via _to_png() method
    External service calls: Uses Selenium WebDriver to render the map as PNG

### `folium.folium.Map.render` · *method*

## Summary:
Configures and renders a Map object by setting up HTML/CSS structure and integrating global configuration.

## Description:
This method prepares a Map object for rendering by ensuring it's contained within a Figure context, adding necessary CSS styles for proper layout, and incorporating global configuration switches. It serves as the primary entry point for rendering Map objects in the folium framework.

The method is specifically designed to handle the unique requirements of Map rendering, including proper HTML/CSS setup and integration with the parent rendering system. It ensures that the map has appropriate styling and configuration before the actual rendering occurs.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method for further customization.

## Returns:
    None: This method performs side effects and does not explicitly return a value.

## Raises:
    AssertionError: When the Map object is not contained within a Figure context.

## State Changes:
    Attributes READ: 
    - self.global_switches: Configuration switches for global map settings
    - self._parent: Accessed indirectly via get_root() to verify containment
    
    Attributes WRITTEN:
    - No direct attribute modifications on self

## Constraints:
    Preconditions:
    - The Map object must be added to a Figure container before calling this method
    - The Map object must have a valid global_switches attribute configured during initialization
    
    Postconditions:
    - The Map's root figure will contain properly configured CSS styles for html/body and #map
    - The Map's global_switches will be added to the figure header
    - The rendering process will be initiated through the parent class

## Side Effects:
    - Adds CSS style elements to the figure header (html/body and #map styling)
    - Adds global_switches element to the figure header
    - Calls the parent class's render method which handles the actual HTML generation

### `folium.folium.Map.show_in_browser` · *method*

## Summary:
Displays the map in a web browser by generating a temporary HTML file and opening it in the default browser.

## Description:
This method renders the current map as HTML content, saves it to a temporary file, and opens it in the user's default web browser. It then enters an infinite loop to keep the application running until manually interrupted, allowing the user to view the map in the browser.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - None (method doesn't read any instance attributes directly)
    
    Attributes WRITTEN:
    - None (method doesn't modify any instance attributes)

## Constraints:
    Preconditions:
    - The map must have been properly initialized with valid configuration
    - The map must be part of a Figure (which happens during initialization)
    - The `webbrowser` module must be available and functional on the system
    
    Postconditions:
    - A temporary HTML file containing the rendered map is created and opened in the browser
    - The application continues running until interrupted by Ctrl+C

## Side Effects:
    - Creates a temporary HTML file in the system's temporary directory
    - Opens the system's default web browser
    - Prints informational messages to stdout
    - Blocks execution until Ctrl+C is pressed

### `folium.folium.Map.fit_bounds` · *method*

## Summary:
Adjusts the map view to fit specified geographic bounds with optional padding.

## Description:
Configures the map to display a specific geographic area defined by bounding coordinates. This method adds a FitBounds child element to the map that will automatically adjust the zoom level and center to ensure the specified bounds are visible within the map viewport.

## Args:
    bounds (list): A list of two coordinate pairs defining the southwest and northeast corners of the bounding box in [latitude, longitude] format.
    padding_top_left (tuple, optional): Padding in pixels for the top-left corner as (x, y). Defaults to None.
    padding_bottom_right (tuple, optional): Padding in pixels for the bottom-right corner as (x, y). Defaults to None.
    padding (tuple, optional): Uniform padding in pixels for all sides as (x, y). Defaults to None.
    max_zoom (int, optional): Maximum zoom level to use when fitting bounds. Defaults to None.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The bounds parameter must be a valid list of two coordinate pairs in [latitude, longitude] format.
    Postconditions: The map's view will be adjusted to fit the specified bounds, potentially changing the zoom level and center coordinates.

## Side Effects:
    None: This method does not cause external I/O or mutate objects outside the map instance.

### `folium.folium.Map.choropleth` · *method*

## Summary:
Issues a deprecation warning and adds a choropleth layer to the map using the Choropleth class.

## Description:
This method provides a deprecated interface for adding choropleth layers to a Folium map. When called, it issues a FutureWarning indicating that this method is deprecated and recommends using the standalone Choropleth class instead. The method creates a Choropleth object with the provided arguments and adds it as a child element to the map.

## Args:
    *args: Variable length argument list passed directly to the Choropleth constructor.
    **kwargs: Arbitrary keyword arguments passed directly to the Choropleth constructor.

## Returns:
    None

## Raises:
    FutureWarning: Always raised to indicate deprecation of this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method can be called on any Map instance.
    Postconditions: The Map instance will have a Choropleth child element added to it.

## Side Effects:
    Issues a FutureWarning to the user about deprecation.
    Creates a Choropleth object and adds it as a child to the map instance.

### `folium.folium.Map.keep_in_front` · *method*

## Summary:
Appends map elements to a list that ensures they remain visually in front of other map elements during rendering.

## Description:
This method adds one or more map elements to the `objects_to_stay_in_front` list, which controls the rendering order of map features. Elements in this list are rendered with higher z-index priority, ensuring they appear above other map elements such as base layers, markers, or shapes. This functionality is particularly useful for UI elements like popups, tooltips, or custom overlays that should remain visible regardless of map interactions or layer changes.

The method is typically called when adding interactive elements that need to maintain visibility above map layers, such as custom markers, popup windows, or control elements.

## Args:
    *args (object): One or more map elements (such as markers, popups, tooltips, or custom features) that should remain visually in front of other map elements. These objects must be compatible with folium's rendering system.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: `self.objects_to_stay_in_front` - appends the provided objects to this list

## Constraints:
    Preconditions: The objects passed must be valid folium map elements that support the rendering system.
    Postconditions: The provided objects are added to the `objects_to_stay_in_front` list in the order they were passed.

## Side Effects:
    None: This method only modifies the internal state of the Map object by appending to a list.

