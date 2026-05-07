# `folium.py`

## `folium.folium.GlobalSwitches` · *class*

## Summary:
Container Element that holds two global boolean flags (no_touch and disable_3d) used by the folium rendering/templating system to expose map-wide switches. It is a minimal value object subclassing Element.

## Description:
GlobalSwitches is a tiny Element subclass whose sole purpose is to store two boolean flags:
- no_touch: intended to indicate whether touch-specific interactions should be treated as disabled.
- disable_3d: intended to indicate whether any 3D-related UI or rendering should be disabled.

The class itself does not implement or enforce any UI or rendering behavior — it only stores the flags and a stable element name so other parts of the system (templates or rendering code) can read these flags if they choose. Typical usage is to construct a GlobalSwitches instance and add it to the folium Map or Figure instance (using the Element API) so it is present in the map's element tree at render time. That consumption of the flags (reading them during template rendering) occurs outside this class.

Motivation / responsibility:
- Provide a single, named Element that aggregates global boolean switches for a map.
- Encapsulate the flags behind a consistent Element interface so the rendering system can reference them like any other Element.

Known callers / instantiation scenarios:
- Map-building code that wants to expose global toggles to templates or rendering logic will instantiate this class and attach it to the Map/Figure. The class does not itself hook into Map internals.

## State:
- Class attribute:
  - _template (jinja2.Template)
    - Type: jinja2.Template
    - Value in source: an empty Template placeholder
    - Role: placeholder compatible with Element's template-based rendering; currently empty in the source.
- Instance attributes set by __init__:
  - _name: str
    - Assigned value: "GlobalSwitches"
    - Invariant: must remain the identifier for the element instance; callers should not modify it.
  - no_touch: bool-like
    - Type: expected bool
    - Default: False (when not provided)
    - Notes: the constructor assigns the provided value directly; no runtime coercion or type checking is performed. Downstream code should treat this as a boolean.
  - disable_3d: bool-like
    - Type: expected bool
    - Default: False (when not provided)
    - Notes: same behavior and constraints as no_touch.

Inherited state and behavior:
- Inherits Element behaviors (attachment to parent, rendering helpers, etc.). Any state or invariants on Element apply (not redefined here).

Class invariants:
- After construction, _name == "GlobalSwitches".
- no_touch and disable_3d should be treated as boolean flags by code that consumes the object; the class itself does not enforce boolean types.

## Lifecycle:
Creation:
- Constructor signature: GlobalSwitches(no_touch=False, disable_3d=False)
- Both parameters are optional.
- Implementation steps performed:
  1. Call Element.__init__ via super().__init__().
  2. Set self._name to "GlobalSwitches".
  3. Assign self.no_touch and self.disable_3d from the constructor arguments.

Usage:
- Typical sequence:
  1. Instantiate GlobalSwitches with desired flags.
  2. Add the instance to a Map or Figure using the Element API (for example, using add_child provided by the map/figure). This makes the element available to the rendering step.
  3. Rendering or template code external to this class may read no_touch and disable_3d and take action.
- There are no other methods on this class; no ordering or method-call requirements beyond adding to the element tree prior to render if templates are expected to see it.

Destruction:
- No explicit cleanup required. The object has no external resources and is collected by normal garbage collection.
- If removed from a parent, follow the Element/Map API for detaching children; GlobalSwitches defines no special removal behavior.

## Method Map:
flowchart LR
    A[Call GlobalSwitches(no_touch, disable_3d)] --> B[Element.__init__ via super()]
    B --> C[Set self._name = "GlobalSwitches"]
    C --> D[Assign self.no_touch and self.disable_3d]
    D --> E[map.add_child(instance) or figure.add_child(instance)]
    E --> F[Render pipeline (external) may read flags]

Notes: The only internal methods invoked are Element.__init__ and attribute assignments. All rendering/consumption steps are external to this class.

## Raises:
- The constructor does not explicitly raise exceptions.
- Potential runtime exceptions:
  - Exceptions raised by Element.__init__ (called via super().__init__) can propagate (these are defined by the Element base class and not introduced by GlobalSwitches).
  - No type or value validation is performed here; if downstream code assumes booleans and receives incompatible types, errors may occur later during consumption.
- Summary: GlobalSwitches itself is safe to construct with any arguments; callers are responsible for supplying sensible boolean values.

## Example:
- Instantiate with both flags enabled/disabled and attach to a map:
  switches = GlobalSwitches(no_touch=True, disable_3d=False)
  map.add_child(switches)
  (Render the map via the usual folium/Map rendering workflow; templates or rendering code outside this class can then inspect switches.no_touch and switches.disable_3d.)

Implementation guidance for reimplementation:
- Subclass Element.
- Provide a class-level _template placeholder compatible with the project's template system.
- Implement __init__ to call super().__init__(), set self._name = "GlobalSwitches", and store the two boolean parameters as instance attributes defaulting to False.
- Do not attempt to implement rendering logic in this class; keep it as a passive container for the two flags so templates or other rendering code can decide how to act on them.

### `folium.folium.GlobalSwitches.__init__` · *method*

## Summary:
Initializes the GlobalSwitches object state by recording two global boolean flags (no_touch and disable_3d) and setting the object's name; has no return value.

## Description:
This method is the initializer for the GlobalSwitches element. It performs the minimal setup required to represent global UI/behavior switches on the instance:
- Known callers: None found in the provided source context. This is the object's constructor and is invoked whenever a GlobalSwitches instance is created.
- Lifecycle stage: Called at object instantiation time (the beginning of the object's lifecycle).
- Reason for separation: Encapsulates the creation-time assignment of global switch flags and the element name so that instances always have a consistent minimal state immediately after construction. Keeping this logic in __init__ ensures callers need not perform additional setup steps after instantiation.

## Args:
    no_touch (bool): Optional. When True, indicates that "no touch" behavior should be enabled at a global level. Default is False.
    disable_3d (bool): Optional. When True, indicates that 3D-related features should be disabled globally. Default is False.

## Returns:
    None

## Raises:
    This method does not explicitly raise any exceptions. It delegates to the base class initializer via super().__init__ which may raise exceptions if the base class enforces preconditions; none are raised by this method itself.

## State Changes:
Attributes READ:
    - None local to this method (the implementation does not read any existing self.<attr> values).
    - Calls super().__init__ (which may read or modify base-class state; that behavior is not defined here).

Attributes WRITTEN:
    - self._name: set to the string "GlobalSwitches".
    - self.no_touch: set to the passed-in no_touch argument.
    - self.disable_3d: set to the passed-in disable_3d argument.

## Constraints:
Preconditions:
    - No special preconditions are required by this method beyond a valid instance context (self must be a correctly allocated object).
    - Argument types: callers are expected to pass booleans for no_touch and disable_3d. The code does not enforce types.

Postconditions:
    - After the call, self._name is "GlobalSwitches".
    - After the call, self.no_touch equals the provided no_touch argument (typically a bool).
    - After the call, self.disable_3d equals the provided disable_3d argument (typically a bool).
    - The method returns None.

## Side Effects:
    - Invokes the base class initializer via super().__init__(), which may have side effects not visible here.
    - Mutates the instance by setting three attributes (self._name, self.no_touch, self.disable_3d).
    - No I/O, network, or filesystem operations are performed by this method itself.

## `folium.folium.Map` · *class*

## Summary:
Represents a Leaflet map container element that aggregates layers, global options, and rendering helpers for embedding interactive maps in HTML pages or Jupyter displays.

## Description:
The Map class is the primary high-level container used to build and render interactive maps. Instantiate Map when you need to:
- Create a map focused on a geographic location and zoom level,
- Add raster TileLayers, vector layers, and other map elements as children,
- Render the map to HTML (for embedding into pages or notebooks),
- Open the rendered map in a web browser, or produce a PNG via an automated browser.

Typical callers / factories:
- Applications or notebooks that build map visualizations.
- Higher-level helper functions which instantiate Map and then add layers.
- When displayed in a Jupyter notebook, IPython display will call the special repr methods (_repr_html_ or _repr_png_) to show the map.

Motivation and responsibility:
Map encapsulates the map-level configuration (location, zoom, CRS, tile source, drawing options) and coordinates how children (layers, features, controls) are attached and rendered within a Figure. It separates map configuration from layer implementations and from the Figure/HTML container concerns; Map uses helper utilities and MacroElement/JSCSSMixin to manage templating and resource injection.

## State:
Public and notable instance attributes (established during __init__ unless otherwise noted):

- _name (str)
  - Value set to "Map".
  - Identifies the element type used by MacroElement machinery.

- _env (jinja2.Environment-like)
  - Set from an external ENV object used for templating. Used internally by rendering.

- _template (jinja2.Template)
  - Class attribute; a jinja2 Template used by MacroElement rendering (empty template in provided source).

- default_js, default_css
  - Class attributes referencing default JS/CSS resource lists (bound to module-level _default_js/_default_css).

- _png_image (bytes or None)
  - Cache for PNG bytes captured by _to_png. Initially None; set to PNG bytes on first successful screenshot capture.

- png_enabled (bool)
  - Controls whether _repr_png_ returns a PNG. Defaults to False.

- location (list[float])
  - Two-element [lat, lon] list representing the initial map center.
  - If constructor location is None, set to [0, 0]; otherwise set to the result of validate_location(location).
  - validate_location is used to verify/normalize the provided location; any validation errors from that helper will propagate.

- width, height, left, top (str or numeric)
  - Values obtained by calling _parse_size on the corresponding constructor args. These represent CSS sizes/positions for the map container.
  - Caller may pass CSS-like strings or numeric values acceptable to _parse_size (see utilities).

- position (str)
  - Layout position for the map container (constructor default "relative").

- crs (str)
  - Coordinate reference system identifier (constructor default "EPSG3857").

- control_scale (bool)
  - Whether to show a scale control on the map. Default False.

- options (dict-like)
  - Populated via parse_options(...) with keys such as max_bounds, zoom, zoom_control, prefer_canvas and any additional **kwargs passed to __init__. Represents options that will be used by the front-end mapping library.

- global_switches (GlobalSwitches instance)
  - Created with the no_touch and disable_3d constructor flags to control global interaction features. (GlobalSwitches type is referenced in code and used in render.)

- objects_to_stay_in_front (list)
  - Empty list initially. Objects appended via keep_in_front(...) are stored here; intended for layers that must remain visually above others.

Class invariants:
- After __init__, location is always set (never left as None).
- options is always populated (a dict-like object returned by parse_options).
- The instance will always be attached to a Figure via Figure().add_child(self) in __init__ (see lifecycle).

## Lifecycle:
Creation:
- Constructor signature:
    def __init__(location=None,
                 width="100%", height="100%",
                 left="0%", top="0%",
                 position="relative",
                 tiles="OpenStreetMap", attr=None,
                 min_zoom=0, max_zoom=18, zoom_start=10,
                 min_lat=-90, max_lat=90, min_lon=-180, max_lon=180,
                 max_bounds=False, crs="EPSG3857",
                 control_scale=False, prefer_canvas=False,
                 no_touch=False, disable_3d=False,
                 png_enabled=False, zoom_control=True,
                 **kwargs)
- Required arguments: none (all parameters have defaults).
- Behavior on location:
  - If location is None: set self.location = [0, 0] and force zoom_start = 1.
  - Else: set self.location = validate_location(location) (validation errors propagate).
- Tile handling:
  - If tiles is an instance of TileLayer: the tiles TileLayer is added as a child.
  - Else if tiles is truthy (e.g., a string): a TileLayer is constructed with the provided tiles, attr, min_zoom, max_zoom and added as a child. If tiles is falsy (None/False), no tile layer will be added.
- The Map instance is immediately attached to a newly created Figure via Figure().add_child(self).

Usage (typical flow):
1. Instantiate Map(...) to create a map container.
2. Add layers/controls via add_child(child) inherited from MacroElement or high-level helpers on Map (fit_bounds, choropleth).
3. Optionally call keep_in_front(...) to mark objects that should render above others.
4. Render flow:
   - In notebook/IPython: IPython will call _repr_html_ to embed HTML; Map._repr_html_ ensures it is in a Figure and delegates to the Figure’s _repr_html_.
   - When programmatically rendering: call get_root().render() to obtain the HTML string; Map.render(**kwargs) will ensure required header elements (global_switches and CSS) are present before MacroElement.render runs.
5. To open in a real browser: call show_in_browser(), which writes a temporary HTML file and calls webbrowser.open and waits until KeyboardInterrupt (Ctrl+C) to return.
6. To obtain a PNG: set png_enabled=True, then IPython may call _repr_png_ which returns _to_png(); or call _to_png(delay=..., driver=...) manually. _to_png uses Selenium to launch a headless browser (Firefox by default), navigates to the rendered temporary HTML file, captures a screenshot of the element with class "folium-map", caches it in _png_image and returns the PNG bytes.

Destruction / cleanup:
- Map does not implement an explicit close() or context manager.
- _to_png ensures that any local selenium driver it created is quit() before returning; callers that pass a custom driver are responsible for driver lifecycle.
- show_in_browser runs until interrupted and relies on the OS/browser to manage browser state.

## Method Map:
Mermaid-style diagram showing method relationships and typical invocation order:

graph LR
    __init__ --> Figure_add_child["Figure().add_child(self)"]
    __init__ --> add_child_tile["add_child(TileLayer) if tiles provided"]
    __init__ --> options["parse_options(...) -> options"]
    __init__ --> global_switches["GlobalSwitches(no_touch, disable_3d)"]
    _repr_html_ --> ensure_attached["add_to(Figure()) if _parent is None"]
    _repr_html_ --> Figure__repr_html_
    render --> get_root["get_root() -> Figure"]
    render --> header_add["figure.header.add_child(global_switches/css)"]
    render --> MacroElement_render["super().render(...)"]
    show_in_browser --> get_root_render["get_root().render() -> html"]
    show_in_browser --> temp_html_filepath["temp_html_filepath(html) -> fname"]
    show_in_browser --> webbrowser_open["webbrowser.open(fname)"]
    _repr_png_ --> _to_png
    _to_png --> selenium_driver["create headless Firefox driver if driver None"]
    _to_png --> temp_html_filepath
    _to_png --> driver_get_and_screenshot["driver.get(file:///fname); find class folium-map; screenshot"]
    fit_bounds --> add_child_fitbounds["add_child(FitBounds(...))"]
    choropleth --> add_child_choropleth["add_child(Choropleth(...))"]
    keep_in_front --> append_objects["objects_to_stay_in_front.append(...)"]

## Raises:
- __init__:
  - Propagates exceptions raised by helper utilities called during initialization. Examples (not exhaustive):
    - validate_location(location): any error this helper raises for invalid location inputs will propagate.
    - _parse_size(width/height/left/top): errors from parsing size strings/values will propagate.
    - parse_options(...): errors from invalid option values will propagate.
    - TileLayer(...) construction: if tiles arguments are invalid, TileLayer construction may raise.
  - Note: the Map constructor itself does not explicitly raise typed exceptions; it permits propagation of errors from its callees.

- _to_png:
  - If Selenium is not available, or the requested driver (Firefox) or its binary/geckodriver is not present or cannot be started, Selenium will raise its own exceptions which propagate (e.g., WebDriverException).
  - If the DOM element with class "folium-map" cannot be found, Selenium will raise a selection exception which propagates.

- show_in_browser:
  - May raise exceptions originating from temp_html_filepath or webbrowser.open in platform-specific failure modes.

## Example:
Create and display a basic map with a named tile layer, then save a PNG using Selenium (requires selenium and geckodriver):

from folium.folium import Map
from folium.raster_layers import TileLayer

# Create a map centered on New York City
m = Map(location=[40.7128, -74.0060], zoom_start=12, tiles="OpenStreetMap")

# Add an explicit tile layer (alternative to passing tiles string)
tile = TileLayer(tiles="Stamen Toner")
m.add_child(tile)

# Mark an element to remain in front (example object)
m.keep_in_front(tile)

# Display in browser (blocks until Ctrl+C)
# m.show_in_browser()

# Produce a PNG (requires selenium and a working Firefox/geckodriver)
# m.png_enabled = True
# png_bytes = m._to_png(delay=3)  # or rely on _repr_png_ when enabled

Note:
- For automated PNG generation, the environment must have Selenium and an appropriate browser driver available. If you wish to manage driver lifecycle yourself, pass a configured Selenium WebDriver instance to _to_png(driver=your_driver).
- In notebook contexts, the map's HTML representation is returned via _repr_html_ which ensures Map is attached to a Figure before delegating to the Figure renderer.

### `folium.folium.Map.__init__` · *method*

## Summary:
Initializes a Map instance's configuration and layout state, attaches the new Map into a Figure, configures global switches and rendering options, and optionally adds a base TileLayer child. This sets the Map object's attributes so it is ready to have additional children (markers, controls, layers) added and to be rendered.

## Description:
Known callers and invocation context:
- Called whenever user code or library code constructs a new Map instance (e.g., map_obj = Map(...)). It runs at object construction time and represents the initial setup phase of the map-building pipeline.
- Typical lifecycle stage: creation/initialization stage — immediately after an Element/Map object is constructed and before additional layers, controls, or the rendering step are run.

Why this logic is a separate initializer:
- The method centralizes all map-level configuration (layout sizes and positions, geographic center, zoom limits, coordinate reference system, rendering switches, and top-level JavaScript options) so downstream code and templates can rely on a consistent set of attributes. It also attaches the Map into a Figure and wires an initial tile source, operations that belong conceptually to object initialization rather than later processing.

## Args:
    location (sized, indexable | None): Optional initial geographic center as (lat, lon). If None, Map.location is set to [0, 0] and zoom_start is forced to 1. If provided, it is validated and normalized by validate_location and stored as a list of two floats. Valid inputs include list/tuple of two numeric-convertible values (and certain array-like types handled by validate_location).
    width (int | float | str): Width of the map container. Passed to _parse_size which returns (value: float, unit: "px"|"%"). Accepts numeric pixel values (> 0) or percentage strings/numeric strings representing 0..100. Default: "100%".
    height (int | float | str): Height of the map container. Same parsing/constraints as width. Default: "100%".
    left (int | float | str): Left CSS offset of the container, parsed by _parse_size. Default: "0%".
    top (int | float | str): Top CSS offset of the container, parsed by _parse_size. Default: "0%".
    position (str): CSS position style for the map container (for example "relative" or "absolute"). Default: "relative".
    tiles (TileLayer instance | str | falsy): Base tile specification. If a TileLayer instance is supplied, it is added as a child unchanged. If a truthy non-TileLayer value (commonly a string like "OpenStreetMap") is supplied, a TileLayer is constructed with that value and added as a child. If tiles is falsy (e.g., False, None, empty string), no tile layer is added. Default: "OpenStreetMap".
    attr (str | None): Attribution string passed through to TileLayer when a new TileLayer is constructed. Default: None.
    min_zoom (int): Minimum zoom accepted by the TileLayer constructor when a TileLayer is created here. Default: 0.
    max_zoom (int): Maximum zoom passed to TileLayer when created. Default: 18.
    zoom_start (int): Initial zoom level used to populate self.options (unless overridden to 1 when location is None). Default: 10.
    min_lat (float): Minimum latitude to use when max_bounds is requested. Default: -90.
    max_lat (float): Maximum latitude to use when max_bounds is requested. Default: 90.
    min_lon (float): Minimum longitude to use when max_bounds is requested. Default: -180.
    max_lon (float): Maximum longitude to use when max_bounds is requested. Default: 180.
    max_bounds (bool): If True, constructs a max_bounds array [[min_lat, min_lon], [max_lat, max_lon]] and passes it to parse_options (as maxBounds). If False, max_bounds is not included. Default: False.
    crs (str): Coordinate reference system identifier stored on the Map (e.g., "EPSG3857"). Default: "EPSG3857".
    control_scale (bool): Whether to expose a control-scale option on the Map instance. The boolean is stored on self.control_scale. Default: False.
    prefer_canvas (bool): Passed to parse_options as preferCanvas. Default: False.
    no_touch (bool): Passed to GlobalSwitches(no_touch, disable_3d) to create a global flags element. Default: False.
    disable_3d (bool): Passed to GlobalSwitches to indicate disabling 3D. Default: False.
    png_enabled (bool): Stored on the Map instance as png_enabled and controls whether a PNG snapshot may be produced elsewhere in the code. Default: False.
    zoom_control (bool): Included in options (zoomControl). Default: True.
    **kwargs: Additional map option keywords. These are forwarded to utilities.parse_options (which camel-cases keys and omits None values) and become self.options after parsing. Keys should be snake_case (or already camelCase); values that are None are dropped. Any exceptions from camelization or later validation can propagate.

## Returns:
    None (constructor). Effect: the Map instance (self) is initialized and mutated in-place; it is attached to a new Figure as a child and may have a TileLayer child added.

## Raises:
    Exceptions can propagate from the helper functions called during initialization:
    - TypeError: Raised by validate_location if the provided location is not sized or not indexable (see validate_location contract). Condition: invalid location shape or non-indexable input.
    - ValueError: Raised by validate_location for invalid numeric conversion or NaN coordinates; raised by _parse_size for invalid size values (e.g., non-parsable strings, pixel values <= 0, percent out of 0..100). Conditions: invalid location contents or invalid width/height/left/top values.
    - AttributeError / TypeError: May be raised by parse_options if camelization of kwargs keys fails (e.g., non-str keys) or by other parsing steps; these are propagated.
    - Any exceptions raised by TileLayer construction or methods (when tiles is truthy and a TileLayer is instantiated) will propagate.
    - Any exceptions from the Element/Figure API invoked here (super().__init__ or Figure().add_child(self) or self.add_child(...)) will propagate.

## State Changes:
Attributes READ:
    - None of the method's own self.<attr> fields are read before assignment; the initializer does not depend on prior Map instance attributes. It does read the module-level ENV to assign self._env (ENV must exist in module scope).

Attributes WRITTEN:
    - self._name (str): set to "Map".
    - self._env: assigned from module-level ENV.
    - self._png_image: set to None.
    - self.png_enabled (bool): set from the png_enabled argument.
    - self.location (list[float]): set to [0, 0] if location is None, otherwise validate_location(location) result.
    - self.width (tuple[float, str]): result of _parse_size(width) — (value, "px"|"%").
    - self.height (tuple[float, str]): result of _parse_size(height).
    - self.left (tuple[float, str]): result of _parse_size(left).
    - self.top (tuple[float, str]): result of _parse_size(top).
    - self.position (str): set from the position argument.
    - self.crs (str): set from the crs argument.
    - self.control_scale (bool): set from the control_scale argument.
    - self.options (dict): normalized map options returned by parse_options, including keys derived from max_bounds (if enabled), zoom, zoomControl, preferCanvas, and any other kwargs after camelization and omission of None values.
    - self.global_switches (GlobalSwitches): new GlobalSwitches(no_touch, disable_3d) instance assigned.
    - self.objects_to_stay_in_front (list): initialized as an empty list.
    - Children (Element tree): The Map instance is attached to a Figure via Figure().add_child(self). In addition, a TileLayer child may be added via self.add_child(tiles) or self.add_child(tile_layer, name=tile_layer.tile_name).

## Constraints:
Preconditions:
    - If location is provided, it must satisfy validate_location requirements: sized, indexable, length == 2, and each coordinate convertible to float and not NaN.
    - width, height, left, top must be acceptable to _parse_size:
        * numeric int/float -> treated as pixels and must be > 0
        * string -> parsed as percentage (0..100) or numeric string (treated as percentage)
        * otherwise _parse_size raises ValueError
    - kwargs keys should be string-like so utilities.parse_options can camelize them; values of None will be omitted.
    - The module-level name ENV must exist (the initializer assigns it to self._env).

Postconditions:
    - After return, the Map instance has the attributes listed above populated with normalized and validated values (or defaults where appropriate).
    - The Map is part of a Figure (it has been added as a child of a newly created Figure()).
    - If tiles was provided or truthy, the Map has a TileLayer child (either the provided TileLayer instance or a newly constructed TileLayer).
    - self.options is a dict ready for downstream serialization into frontend/Leaflet options.

## Side Effects:
    - Attaches the Map to a Figure: Figure().add_child(self) is invoked (mutates the new Figure and establishes the element tree relation).
    - May instantiate a TileLayer and add it as a child of the Map (mutates Map's child list).
    - Constructs a GlobalSwitches element and assigns it to self.global_switches (no external I/O).
    - No file, network, or browser I/O occurs directly in this method. Any I/O or external calls would occur in functions/classes invoked later (not in this initializer).

### `folium.folium.Map._repr_html_` · *method*

## Summary:
Return an HTML representation of the Map suitable for rich display (e.g., in Jupyter/IPython), ensuring the Map is attached to a Figure during rendering and restoring the Map's parent state afterward.

## Description:
This method is the special IPython/Jupyter HTML repr hook: when a Map instance is displayed in an interactive (HTML-capable) frontend, the frontend calls this method to obtain HTML for rendering.

Known callers and contexts:
- IPython/Jupyter notebook and lab display machinery (implicitly invoked when a Map is the result of a cell or is passed to display()).
- Any code that explicitly calls obj._repr_html_(**kwargs) to obtain the HTML representation of the Map.
- Higher-level rendering routines that delegate HTML generation to the Map's parent Figure (e.g., when composing multiple Elements inside a Figure).

Why this is a separate method:
- _repr_html_ is the standard protocol for returning HTML representations to rich frontends; it must be implemented as a discrete method so the interactive environment can call it directly.
- The method encapsulates the transient attachment of the Map to a Figure instance and delegates actual HTML generation to the Figure's own _repr_html_. This keeps Map's rendering responsibilities small and delegates document-level rendering to Figure.

## Args:
    **kwargs: dict
        Arbitrary keyword arguments forwarded to the parent's _repr_html_ method. There are no further constraints on the keys; they are passed through as-is.

## Returns:
    str
        The HTML string returned by the parent Figure's _repr_html_ method. This is the HTML that should be embedded in the frontend. No value other than the parent's return value is produced by this method.

## Raises:
    AttributeError
        If after attaching to a Figure the code attempts to call self._parent._repr_html_ but self._parent is missing or does not provide _repr_html_, an AttributeError will propagate.
    Any exception raised by self.add_to(Figure()) or by the parent's _repr_html_ will propagate unchanged.

## State Changes:
Attributes READ:
    self._parent
        Checked to determine whether the Map is already attached to a parent Figure.

Attributes WRITTEN:
    self._parent
        - If self._parent is None at entry: self.add_to(Figure()) will set a parent (the new Figure) and after the parent's _repr_html_ returns this method sets self._parent back to None.
        - If self._parent is not None at entry: this method does not modify self._parent.

Note: add_to(Figure()) is invoked when self._parent is None; add_to is expected to attach the Map to the new Figure (mutating Map and the Figure). This method explicitly resets self._parent to None when it attached the Figure itself.

## Constraints:
Preconditions:
    - The Map instance must have an add_to method and a _parent attribute (this is true for Map instances constructed via the class in this module).
    - If self._parent is not None, it is expected to be an object that implements _repr_html_(**kwargs) (typically a Figure).

Postconditions:
    - The return value is the string returned by the parent Figure's _repr_html_.
    - If self._parent was None on entry, it will be None on exit (the method restores the Map's parent state).
    - If self._parent was non-None on entry, it remains unchanged on exit.

## Side Effects:
    - Temporarily attaches the Map to a new Figure when no parent exists by calling self.add_to(Figure()). This mutates both the Map (setting _parent) and the temporary Figure (adding the Map as a child) for the duration of the call.
    - Delegates HTML generation to the parent Figure's _repr_html_. Any side effects performed by that method (rendering, resource gathering, template rendering) will occur.
    - No direct I/O, network access, or browser-opening occurs inside this method itself; however, side effects from the parent Figure's rendering (such as generating files or accessing resources) may happen and will propagate.

### `folium.folium.Map._to_png` · *method*

## Summary:
Produces and caches a PNG image (bytes) of the map by rendering the map's HTML in a Selenium-driven browser, capturing the element with class "folium-map", and storing the resulting PNG bytes on the instance for later reuse.

## Description:
This private helper centralizes the steps required to produce a PNG snapshot of the Map's current rendered HTML. When called and no cached image exists (self._png_image is None), the method:
- Renders the map HTML via self.get_root().render().
- Writes the HTML to a temporary file using the temp_html_filepath context manager and obtains its filename.
- Uses a Selenium WebDriver (the provided driver or a newly-created headless Firefox driver) to open the file URL, makes the browser fullscreen, waits for delay seconds, locates the element with class name "folium-map", takes a PNG screenshot of that element, and calls driver.quit().
- Assigns the captured PNG bytes to self._png_image and returns them.

Known callers and invocation context:
- The snippet does not show explicit callers. This method is intended for internal use by higher-level code that needs an image representation (for example, display or export utilities). It is separated to keep browser/setup/screenshot/caching logic in one place.

Why this is a separate method:
- The operation touches external systems (filesystem and Selenium), includes waiting and element selection, and implements caching. Encapsulation avoids duplicating these responsibilities across callers.

## Args:
    delay (int | float) = 3
        Seconds to wait after loading the page and before taking the screenshot. The value is passed directly to time.sleep(delay); supplying a negative value will cause time.sleep to raise ValueError.
    driver (selenium.webdriver.* | None) = None
        Optional Selenium WebDriver to use. If None, the method creates a headless Firefox driver using webdriver.Firefox with firefox.options.Options and the --headless argument.

## Returns:
    bytes
        Binary PNG image data returned by the Selenium element's screenshot_as_png. If self._png_image was already set on entry, the method returns the cached bytes immediately and performs no browser or file I/O.

## Raises:
    Propagates exceptions raised by underlying calls, including but not limited to:
    - Selenium errors raised during driver creation, navigation (driver.get), element lookup (driver.find_element), screenshot retrieval (element.screenshot_as_png), or driver operations (driver.fullscreen_window, driver.quit).
    - I/O or temporary-file errors from temp_html_filepath or filesystem operations.
    - ValueError from time.sleep if a negative delay is passed.
    The method does not wrap these exceptions; they propagate to the caller. If an exception occurs during generation, self._png_image is not updated by this method.

## State Changes:
    Attributes READ:
    - self._png_image: checked to decide whether to generate a new PNG or return the cached value.
    - The Map's root element via self.get_root() and its render() result to obtain the HTML.

    Attributes WRITTEN:
    - self._png_image: assigned to the newly-captured PNG bytes when generation succeeds.

## Constraints:
    Preconditions:
    - The HTML produced by self.get_root().render() must include an element with class "folium-map"; otherwise driver.find_element("class name", "folium-map") will raise an exception.
    - If no driver is supplied, a functioning headless Firefox/Gecko driver must be available in the environment (geckodriver and Firefox), otherwise driver creation will fail.
    - The execution environment must permit starting a headless browser.
    - delay should be non-negative to avoid ValueError from time.sleep.

    Postconditions:
    - On successful generation, self._png_image contains the PNG bytes of the ".folium-map" element and is returned.
    - If self._png_image was already set at call time, no generation steps are performed and the cached bytes are returned unchanged.

## Side Effects:
    - May start a headless Firefox browser process via Selenium when driver is None.
    - Writes HTML to a temporary file path using the temp_html_filepath context manager (the method uses the filename provided by that context manager).
    - Calls driver.fullscreen_window() and time.sleep(delay) to allow the page to settle.
    - Calls driver.quit() after taking the screenshot in the generation path; therefore, if a caller provides a driver and generation runs, that driver will be quit by this method.
    - If an exception occurs before the driver.quit() call, the driver process may remain running (the method does not perform additional cleanup in exception paths).
    - The browser loading the map HTML may perform network requests (e.g., for tile layers) as part of normal page load.

### `folium.folium.Map._repr_png_` · *method*

## Summary:
Return a PNG snapshot of the map for rich display consumers when PNG output is enabled; otherwise return None.

## Description:
Known callers and lifecycle context:
- The IPython/Jupyter rich display system (objects with _repr_png_ are queried when the notebook attempts to render an object as PNG). Typical invocation occurs when a Map instance is the result of the last expression in a notebook cell or when a display/displayhook requests available rich representations.
- Other tooling that follows the Python rich display protocol may also call this method to obtain a PNG rendering for viewers or exporters.

Why this is a separate method:
- The name and signature implement the IPython rich-display protocol. Keeping this small wrapper separate allows quick checking of whether PNG rendering is enabled (cheap) and delegates the heavy work (browser rendering, screenshot capture and caching) to _to_png. This separation avoids performing expensive I/O or process startup when PNG output is disabled and makes testing and reuse easier.

## Args:
    None.

## Returns:
    bytes | None
    - bytes: PNG image data (raw PNG file bytes) when png rendering is enabled and _to_png succeeds.
    - None: when png rendering is disabled (self.png_enabled is False). No exception is raised in this case.

## Raises:
    - Any exception raised by the delegated _to_png call is propagated unchanged. Typical possible exceptions include:
        * Selenium WebDriver-related exceptions (e.g., failure to start a browser, missing driver executable).
        * File I/O errors from creating or reading the temporary HTML file.
        * Errors raised while rendering or interacting with the browser DOM (element not found).
    - The method itself performs no additional catching; callers should handle or allow propagation of these exceptions.

## State Changes:
Attributes READ:
    - self.png_enabled: boolean flag read to decide whether to produce a PNG.

Attributes WRITTEN:
    - None directly by this method.
    - Indirectly (via calling self._to_png()), self._png_image may be set to the PNG bytes on first successful generation; subsequent calls will return the cached bytes.

## Constraints:
Preconditions:
    - self.png_enabled must be set (bool). If False, the method will return None and perform no further actions.
    - If self.png_enabled is True, the environment must satisfy the requirements of _to_png: a working Selenium WebDriver installation (browser driver binaries and compatible browser), ability to create temporary files, and access to spawn/terminate subprocesses.

Postconditions:
    - If png rendering is disabled (png_enabled is False): the Map object is unchanged and the method returns None.
    - If png rendering is enabled and _to_png completes successfully: the method returns PNG bytes and self._png_image will contain (or already contain) those bytes afterward (cached).
    - If _to_png raises: no guarantees are made about caching; exceptions propagate and the Map object's state may be partially changed depending on where the failure occurred inside _to_png.

## Side Effects:
    - When png_enabled is True, calling this method typically triggers the following side effects via _to_png:
        * Launching a headless browser process (Selenium WebDriver).
        * Writing a temporary HTML file to disk for the rendered map.
        * Navigating the browser to a file:// URL, rendering the page, and interacting with the DOM to locate the map container.
        * Capturing a PNG screenshot of the map DIV and quitting the browser process.
        * Caching the PNG bytes on self._png_image.
        * Waiting/sleep (a brief delay) to allow the page to render before taking the screenshot.
    - No external network calls are required by this method itself (the browser navigates to a local temporary file), but the browser process is started and killed which affects system processes.

### `folium.folium.Map.render` · *method*

## Summary:
Ensures the Map instance is attached to a Figure, injects required global switches and CSS style elements into the parent Figure's header, and then delegates rendering to the superclass render implementation — affecting the Figure's header but not creating new Map attributes.

## Description:
This method is invoked as part of the HTML rendering lifecycle for the map element. Typical call sites (within this class) include:
- _to_png(): calls self.get_root().render() to produce HTML before creating a screenshot.
- show_in_browser(): calls self.get_root().render() to obtain HTML that is written to a temporary file and opened in a browser.
- _repr_html_(): when the Map is embedded in environments that request HTML, the element-tree render of the root Figure will call down into each child's render method, including this one.

Purpose and rationale:
- The method centralizes the logic required to make a Map display correctly in a browser: it verifies that the Map is contained inside a Figure and ensures the Figure.header contains a set of shared elements needed by the map (global feature switches and specific CSS to make the map occupy the full page).
- Keeping these header additions here avoids duplicating the same header injection logic elsewhere and ensures the Map element itself is responsible for declaring the assets and styles it needs prior to full render.

## Args:
    **kwargs: Arbitrary keyword arguments forwarded to the superclass render method. These are not interpreted by this method; they are passed through to MacroElement.render (or the nearest superclass implementation).

## Returns:
    The return value of the superclass render call (super().render(**kwargs)). This method itself acts as a pass-through for the superclass return value; callers should treat the return value as whatever the rendering infrastructure produces.

## Raises:
    AssertionError: If self.get_root() does not return an instance of branca.element.Figure.
    - Trigger condition: The Map is not attached to a Figure instance when render() is called.
    - Assertion message (exact): "You cannot render this Element if it is not in a Figure."

## State Changes:
    Attributes READ:
        - self.global_switches: read to add into the figure header.
        - self.get_root(): invoked to obtain the root Figure (reads internal parent linkage as implemented by the element tree).

    Attributes WRITTEN:
        - None on the Map instance itself (this method does not assign to any self.<attr> fields).

    External object mutations:
        - figure.header: this method calls figure.header.add_child(...) three times to add:
            1) self.global_switches with the name "global_switches"
            2) an Element containing page-level CSS (name "css_style")
            3) an Element containing #map CSS (name "map_style")
        These header modifications mutate the Figure's header state (its list/dict of child elements).

## Constraints:
    Preconditions:
        - The Map must be part of an element tree whose root is a branca.element.Figure (i.e., self.get_root() must return a Figure). If this is not true, render() will raise an AssertionError.
    Postconditions:
        - After successful completion, the parent Figure.header is guaranteed to contain child elements named "global_switches", "css_style", and "map_style" (added or overwritten according to header.add_child behavior).
        - The method returns whatever the superclass render returns.

## Side Effects:
    - Mutates the Figure.header (adds three children as described above).
    - Delegates to super().render(**kwargs), which may perform further mutations to the element tree or produce the HTML/text rendering output (side effects depend on the superclass implementation).
    - No direct I/O, network, or filesystem operations are performed by this method itself.

### `folium.folium.Map.show_in_browser` · *method*

## Summary:
Opens a temporary HTML file containing the rendered map in the user's default web browser and blocks the calling thread until the user interrupts (Ctrl+C). Does not modify the Map object's persistent state.

## Description:
- What it does: Renders the Map into an on-disk temporary HTML file, launches that file in the system's default web browser, prints an informational message to stdout, and then enters a blocking sleep loop until the user interrupts with KeyboardInterrupt (Ctrl+C). The temporary file is removed automatically when the context manager from temp_html_filepath exits.
- Known callers and lifecycle stage:
    - Commonly invoked directly by application or interactive code when the developer/user wants to preview the map in an external browser. It is not called automatically by the rendering pipeline.
    - Related internal callers in the Map class:
        - _to_png: also calls self.get_root().render() but uses the temporary file differently (for automated screenshot capture).
    - Typical invocation stage: presentation/preview stage after the Map has been configured and (critically) attached to a Figure so that rendering is possible.
- Why a separate method: This user-facing preview behavior (create temporary file, open browser, and block until user cancels) is a distinct side-effectful workflow that mixes I/O and blocking behavior. Keeping it as a separate method avoids inlining these side effects into rendering logic and allows callers to choose whether to preview the map.

## Args:
    None

## Returns:
    None
    - The method does not return any value (implicitly returns None).
    - In normal operation it blocks until user interrupt; on KeyboardInterrupt the method swallows the exception and returns None after cleaning up.

## Raises:
    - OSError:
        - Raised if underlying OS-level file operations inside temp_html_filepath fail (e.g., failure creating or writing the temporary file, permission errors, disk full). These errors propagate out of this method.
    - TypeError:
        - Can be raised if get_root().render() yields a non-bytes/non-str object and temp_html_filepath attempts to write it as bytes; this will propagate.
    - Any exception raised by self.get_root() or by the rendering process:
        - For example, if rendering asserts that the element is not in a Figure, those assertion errors (AssertionError) or other exceptions raised by render() will propagate.
    - Note: KeyboardInterrupt is caught and suppressed by this method (it does not propagate to the caller).

## State Changes:
- Attributes READ:
    - None explicitly read by attribute name in this method. The method calls self.get_root(), which may in turn access internal attributes (e.g., parent pointers) — but show_in_browser itself does not directly read any self.<attr> fields.
- Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
- Preconditions:
    - The Map must be in a renderable state: self.get_root() must return a root Figure (or an object whose render() returns a str or bytes containing valid HTML). If the Map is not attached to a Figure, rendering may raise (for example, an AssertionError from the render() implementation).
    - The rendering output of self.get_root().render() must be a str (UTF-8 encodable) or bytes; temp_html_filepath expects one of those types.
    - The environment must permit temporary file creation and removal (write permissions to the system temp directory).
- Postconditions:
    - When the method returns (normally after a KeyboardInterrupt), the temporary HTML file created by temp_html_filepath has been removed (the context manager ensures cleanup).
    - The Map object remains unchanged (no attributes modified).
    - No exception will be propagated for a KeyboardInterrupt (it is swallowed); other exceptions during rendering or file I/O will propagate to the caller.

## Side Effects:
- I/O:
    - Creates a temporary .html file on disk and writes the rendered HTML to it (via temp_html_filepath).
    - Removes the temporary file when the context manager exits.
- External interactions:
    - Launches the system default web browser via webbrowser.open(fname). This requests the OS to open the generated file in a browser window/tab.
    - Prints an informational message to stdout telling the user that the browser should have opened and how to return (Ctrl+C).
- Threading / blocking:
    - Blocks the calling thread indefinitely by sleeping in a loop (time.sleep(100) in a while True). The intended way to stop blocking is by sending KeyboardInterrupt (Ctrl+C). The method catches KeyboardInterrupt and then returns.
- Resource usage:
    - While blocked, the process retains any resources associated with the temporary file lifecycle and the open browser window (the browser typically loads the file and is independent of this process afterward).

### `folium.folium.Map.fit_bounds` · *method*

## Summary:
Adds a FitBounds instruction to the map so that, when rendered in the frontend, the map will pan/zoom to fit the provided geographic bounding box with the specified padding and max-zoom constraints. This mutates the map by adding a child element that encodes the fit-bounds instruction.

## Description:
Known callers and contexts:
- Library callers: typical usage is application or library code that is constructing or configuring a Map and wants the resulting map view to show a particular geographic area (for example, after adding markers or layers).
- Lifecycle stage: invoked after a Map has been instantiated and configured, but before or during rendering; the FitBounds child added by this method will be serialized into the map's template and executed in the browser when the map is displayed.
- Higher-level convenience: it is commonly used in user code as a concise way to ensure the map viewport contains a set of coordinates, rather than manually creating a FitBounds element and adding it.

Why this is a separate method:
- Encapsulates the common two-step pattern (create FitBounds + add it to the map) into a single, convenient API on Map.
- Keeps user code concise and self-documenting; separates the responsibility of creating a FitBounds element from other map configuration logic.
- Prevents duplication of the FitBounds construction pattern across callers.

## Args:
    bounds (any):
        The bounding geometry to fit. Commonly a two-element sequence of coordinate pairs (e.g., [[southWest_lat, southWest_lng], [northEast_lat, northEast_lng]]) or an iterable of LatLng-like pairs accepted by Leaflet. No coercion or validation is performed by this method; the value is passed to FitBounds unchanged.
    padding_top_left (Optional[tuple[float, float]] or None, default None):
        Padding in pixels to add to the top-left corner when fitting bounds. If None, the option is omitted.
    padding_bottom_right (Optional[tuple[float, float]] or None, default None):
        Padding in pixels to add to the bottom-right corner when fitting bounds. If None, the option is omitted.
    padding (Optional[tuple[float, float] | float] or None, default None):
        Global padding to apply when fitting bounds (either a pair [x, y] or a single numeric value). If None, the option is omitted.
    max_zoom (Optional[int] or None, default None):
        Maximum zoom level to use when fitting bounds. If None, the option is omitted.

## Returns:
    None
    - This method does not return a value. Its effect is to register a FitBounds element as a child of the Map for later rendering.

## Raises:
    - Any exception raised by FitBounds(...) during construction (for example, if underlying utilities raise), or by self.add_child(...) during addition will propagate to the caller. This method does not perform its own error handling.
    - There are no Map.fit_bounds-specific exceptions raised directly by this method.

## State Changes:
Attributes READ:
    - None explicitly read from self by the method body (the method only calls the instance method add_child).

Attributes WRITTEN:
    - None explicitly written by Map.fit_bounds itself. However, calling self.add_child(...) results in a mutation of the Map's internal children collection (the container managed by the MacroElement/Map rendering machinery) so that the new FitBounds element becomes part of the map's element tree and will be included during rendering.

## Constraints:
Preconditions:
    - self must be a Map instance (an object that provides add_child and participates in the folium rendering pipeline).
    - bounds should be provided in a format acceptable to the frontend/Leaflet for meaningful results; this method does not validate or coerce the bounds argument.

Postconditions:
    - A FitBounds instance constructed with the provided arguments has been added as a child of the Map (so it will be serialized and executed during rendering).
    - The FitBounds instance stores the bounds exactly as passed and an options dict containing any non-None padding/max_zoom values (camelCased) for the rendering pipeline to consume.

## Side Effects:
    - Mutation: adds a new child element (FitBounds) to the map's element tree via self.add_child(...). This side effect causes the map's internal state used for rendering to change.
    - No I/O or network calls are performed by this method itself.
    - Any exceptions from FitBounds construction or add_child will propagate to the caller.

### `folium.folium.Map.choropleth` · *method*

## Summary:
Emits a deprecation FutureWarning and constructs a folium.features.Choropleth from the provided arguments, then attaches that Choropleth as a child to the Map, mutating the map's element tree.

## Description:
Known callers and invocation context:
- Intended for use by user code during the map assembly phase (after creating a Map and before rendering/exporting) to add a choropleth layer. Typical invocation in user notebooks or scripts: create a Map instance, then call this method to add a choropleth layer to that Map.
- The repository's implementation uses this method as a backwards-compatibility shim; modern user code should instantiate folium.features.Choropleth directly and add it via the Map/Element APIs.

Why this logic is its own method:
- It is a thin compatibility wrapper preserved for the old API. The method centralizes the deprecation notice (so callers receive a consistent FutureWarning) and performs a single, common action: lazy-import the Choropleth class, construct it with the caller-supplied arguments, and attach it to the Map. The actual rendering and choropleth logic are implemented in the Choropleth class, so inlining that logic here would duplicate implementation and break separation of concerns.

## Args:
    *args: Positional arguments forwarded unchanged to folium.features.Choropleth constructor.
    **kwargs: Keyword arguments forwarded unchanged to folium.features.Choropleth constructor.
    Notes:
        - This method does not validate or normalize these arguments itself. Valid argument names, required parameters, acceptable value types, and default semantics are those of folium.features.Choropleth.
        - Common parameters users pass to the Choropleth constructor include a GeoJSON/data source and column/key specifications, but consult Choropleth's documentation for the authoritative list.

## Returns:
    None
    - The method does not return the newly created Choropleth. Its observable effect is the mutation of the Map's element tree (the created Choropleth becomes a child of the Map). Any references to the new layer must be obtained by the caller prior to or separately from this call (for example, by constructing the Choropleth instance directly instead of using this shim).

## Raises:
    ImportError / ModuleNotFoundError:
        - Trigger: the runtime import statement "from folium.features import Choropleth" fails (for example, due to a missing/invalid module or import error). The import exception propagates.
    Exceptions from Choropleth constructor:
        - Trigger: Choropleth(*args, **kwargs) raises (for example, TypeError for invalid argument types, ValueError for invalid parameter values, KeyError for missing expected keys). These exceptions are not caught and will propagate to the caller.
    Exceptions from Map.add_child:
        - Trigger: attaching the constructed Choropleth to the Map fails inside the Map/Element tree APIs (for example, if the Map instance is in an invalid state). Exceptions raised by the add_child implementation will propagate.

## State Changes:
Attributes READ:
    - The method calls the instance method add_child; it does not read any Map scalar attributes directly in its body. Any read behavior (for example, reading the Map's element-tree container) is performed by add_child and the Element/MacroElement infrastructure.

Attributes WRITTEN:
    - The Map's element tree is mutated: the created Choropleth instance is added as a child of the Map (the specific internal container mutated is managed by the Element/MacroElement add_child implementation).

## Constraints:
Preconditions:
    - self must be a properly initialized Map instance (normally created via Map(...)). The Map initializer sets up the element-tree context needed by add_child; invoking this method on a partially-initialized Map may cause errors.
    - The provided *args and **kwargs must satisfy folium.features.Choropleth's constructor requirements (types, required parameters). This method performs no argument validation itself.

Postconditions:
    - If the call completes without raising, the Map contains the new Choropleth child constructed with the same *args and **kwargs supplied to this method.
    - A FutureWarning with the following text will have been emitted via warnings.warn:
      "The choropleth  method has been deprecated. Instead use the new Choropleth class, which has the same arguments. See the example notebook 'GeoJSON_and_choropleth' for how to do this."
      (The warning is emitted with category FutureWarning.)
    - No return value is produced.

## Side Effects:
    - Emits a FutureWarning to inform users of deprecation (see exact message above).
    - Performs a lazy, in-function import of folium.features.Choropleth at call time.
    - Mutates the Map's element tree by adding the new Choropleth element (so subsequent rendering or export will include the layer).
    - Does not perform any file, network, or browser I/O itself.
    - Does not log, print, or return the created Choropleth instance.

### `folium.folium.Map.keep_in_front` · *method*

## Summary:
Appends one or more objects to the map's internal list of objects that should be kept visually in front when the map is rendered, mutating the map's internal state.

## Description:
Known callers and context:
    - No internal callers in the Map class implementation were found. This method is intended for use by client/user code (or by other library components) after creating or adding elements to the map and before rendering.
    - Typical lifecycle stage: invoked during map construction/configuration (after creating layers or UI elements) to mark specific objects so they will be rendered above other map content.

Why this is a separate method:
    - Centralizes management of the "keep in front" list so callers do not manipulate the internal list directly.
    - Provides a simple declarative API for users and other components to mark objects that require a persistent front rendering order without coupling that logic to rendering code.

## Args:
    *args (any): Zero or more objects to be marked to "stay in front".
        - Allowed values: any Python object; the method does not perform type checking.
        - Typical values: instances representing map elements (e.g., Element or MacroElement instances), but any object may be appended.
        - Behavior: each positional argument is appended to self.objects_to_stay_in_front in the same order as provided.
        - Note: passing an iterable as a single positional argument will append that iterable object as one entry (it will not be expanded).

## Returns:
    None

## Raises:
    None (the method performs no validation and does not raise exceptions itself).

## State Changes:
    Attributes READ:
        - self.objects_to_stay_in_front (the method accesses this list to append into it)
    Attributes WRITTEN:
        - self.objects_to_stay_in_front (one or more items are appended; the list is mutated in-place)

## Constraints:
    Preconditions:
        - The Map instance must have been initialized such that self.objects_to_stay_in_front exists and is a list. (In the Map implementation, this attribute is created in __init__.)
    Postconditions:
        - For each argument provided, that exact object will be appended to self.objects_to_stay_in_front, preserving argument order.
        - Duplicate objects are allowed and will be appended again (no de-duplication).
        - If called with no arguments, the method performs no changes.

## Side Effects:
    - Mutates the Map instance's internal list self.objects_to_stay_in_front.
    - No I/O, no network access, and no direct interaction with external services.
    - No validation or type enforcement is performed on the appended objects.

