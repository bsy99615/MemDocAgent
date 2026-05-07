# `minimap.py`

## `folium.plugins.minimap.MiniMap` · *class*

## Summary:
A MacroElement plugin that adds a Leaflet "mini map" overview control to a folium Map. It wraps a TileLayer and a normalized options dictionary and registers required JS/CSS assets via JSCSSMixin.

## Description:
MiniMap is intended to be instantiated and attached to a folium Map (or other Element tree) to display a small overview map control (the leaflet-minimap plugin). The class is responsible for:
- Selecting or constructing the TileLayer used by the mini map.
- Normalizing constructor keyword options into a camelCased options dict (via parse_options) suitable for front-end use.
- Declaring the external JavaScript and CSS resources required by the leaflet-minimap plugin (via class attributes default_js and default_css) so JSCSSMixin can register them when rendering.

Known caller pattern:
- Create a MiniMap instance and add it to a Map using the Map.add_child / add_control style API. Rendering is performed by the Element/MacroElement pipeline; MiniMap itself does not perform DOM insertion in __init__.

Motivation / responsibility boundary:
- Encapsulates integration details for the leaflet-minimap plugin (resource declaration, tile layer selection, option normalization).
- Leaves rendering, registration to the Figure header, and actual JS generation to JSCSSMixin and the MacroElement/Template rendering pipeline.

## State:
Class attributes (declared in source):
- _template (jinja2.Template)
    - Type: jinja2.Template
    - Purpose: template used during rendering to produce the HTML/JS for the control. The provided snippet defines a Template object but its string content is empty in the snippet; a real template should use self.tile_layer and self.options.
- default_js (list[tuple[str, str]])
    - Value:
        [
            (
                "Control_MiniMap_js",
                "https://cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.js",
            )
        ]
    - Purpose: Declares the plugin JavaScript resource for JSCSSMixin to register.
    - Invariant: iterable of (name, url) pairs.
- default_css (list[tuple[str, str]])
    - Value:
        [
            (
                "Control_MiniMap_css",
                "https://cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.css",
            ),
        ]
    - Purpose: Declares the plugin CSS resource for JSCSSMixin to register.
    - Invariant: iterable of (name, url) pairs.

Instance attributes (set by __init__):
- _name (str)
    - Value after init: "MiniMap"
    - Role: Element name used by MacroElement/Element system.
- tile_layer (folium.raster_layers.TileLayer)
    - Type: TileLayer instance
    - How set:
        - If tile_layer argument is None -> TileLayer() is called and assigned.
        - If tile_layer is already an instance of TileLayer -> assigned directly.
        - Otherwise -> TileLayer(tile_layer) is called and assigned.
    - Invariant: always a TileLayer instance when __init__ returns.
    - Caller constraints: any value passed that is not a TileLayer will be forwarded to TileLayer(...); callers must ensure this value is valid for TileLayer's constructor.
- options (dict[str, Any])
    - Type: dict whose keys are camelCase strings and whose values are the provided options (no values equal to None).
    - How set: result of parse_options(...) called with the constructor keyword parameters (position, width, height, collapsed_width, collapsed_height, zoom_level_offset, zoom_level_fixed, center_fixed, zoom_animation, toggle_display, auto_toggle_display, minimized) plus any **kwargs.
    - Invariant: keys are camelCased; any parameter with value None is omitted (parse_options behavior).

Mapping of constructor parameters to normalized option key names (via parse_options camelization):
- position (str) -> "position"; default: "bottomright"
- width (int) -> "width"; default: 150
- height (int) -> "height"; default: 150
- collapsed_width (int) -> "collapsedWidth"; default: 25
- collapsed_height (int) -> "collapsedHeight"; default: 25
- zoom_level_offset (int) -> "zoomLevelOffset"; default: -5
- zoom_level_fixed (int | None) -> "zoomLevelFixed"; default: None (omitted from options when None)
- center_fixed (bool) -> "centerFixed"; default: False
- zoom_animation (bool) -> "zoomAnimation"; default: False
- toggle_display (bool) -> "toggleDisplay"; default: False
- auto_toggle_display (bool) -> "autoToggleDisplay"; default: False
- minimized (bool) -> "minimized"; default: False
- **kwargs -> additional keys; each key will be camelized (camelCase) and included unless its value is None

## Lifecycle:
Creation:
- Constructor signature:
    MiniMap(
        tile_layer=None,
        position="bottomright",
        width=150,
        height=150,
        collapsed_width=25,
        collapsed_height=25,
        zoom_level_offset=-5,
        zoom_level_fixed=None,
        center_fixed=False,
        zoom_animation=False,
        toggle_display=False,
        auto_toggle_display=False,
        minimized=False,
        **kwargs
    )
- Required arguments: none (all have defaults).
- Steps performed in __init__:
    1. Call super().__init__() to initialize ancestor classes (MacroElement / JSCSSMixin).
    2. Set self._name = "MiniMap".
    3. Resolve and set self.tile_layer according to the tile_layer argument (None -> TileLayer(); TileLayer instance -> use; otherwise TileLayer(tile_layer)).
    4. Build self.options = parse_options(...) with the above keyword parameters and any additional kwargs (result omits None values and converts keys to camelCase).

Usage:
- Typical order:
    1. Create instance: minimap = MiniMap(...)
    2. Attach to a Map/Figure: map.add_child(minimap) or equivalent.
    3. On rendering of the Map/Figure:
        - JSCSSMixin registers the declared default_js and default_css into the Figure.header (this happens only when get_root() returns a Figure).
        - MacroElement rendering/render pipeline will render the MiniMap's template using self.tile_layer and self.options (the snippet defines a Template placeholder; a complete implementation should render JS to instantiate the leaflet-minimap control).
- Sequencing requirements:
    - MiniMap should be added to a Figure (Map) before render is triggered. JSCSSMixin raises an AssertionError if render runs outside of a Figure root.

Destruction / cleanup:
- MiniMap provides no explicit cleanup methods. Resources (JS/CSS links) are registered on the Figure.header at render time; their removal is the responsibility of the Figure/header API or by removing the element from the Element tree before re-rendering.

## Method Map:
flowchart LR
    A[Call MiniMap.__init__(...)] --> B{tile_layer arg?}
    B -- None --> C[create default TileLayer() and assign to self.tile_layer]
    B -- TileLayer instance --> D[assign tile_layer to self.tile_layer]
    B -- Other --> E[call TileLayer(tile_layer) and assign to self.tile_layer]
    C --> F[call parse_options(...) with constructor kwargs]
    D --> F
    E --> F
    F --> G[self.options = parsed dict (camelCased keys, no None values)]
    G --> H[Attach to Map/Figure via add_child]
    H --> I[Figure.render triggers Element.render()]
    I --> J[JSCSSMixin registers default_js/default_css in Figure.header]
    J --> K[MacroElement renders _template using self.tile_layer and self.options]

## Raises:
MiniMap.__init__ does not explicitly raise new exceptions, but the following exceptions may propagate from delegated operations or ancestor behavior:
- Exceptions from TileLayer(...) constructor:
    - When tile_layer is not None and not an instance of TileLayer, MiniMap calls TileLayer(tile_layer). Any TypeError/ValueError or custom exceptions thrown by TileLayer's constructor will propagate up.
- Exceptions from parse_options(**kwargs):
    - parse_options camelizes keys; if keys are non-string or camelize fails, AttributeError or TypeError may be raised.
- Exceptions from ancestor initializers (MacroElement.__init__ or JSCSSMixin-related initialization) if they validate state that is not satisfied.
- AssertionError during rendering:
    - If the element's render path is invoked while the element is not attached to a Figure, JSCSSMixin's render raises an AssertionError (the mixin requires get_root() to return a Figure before registering JS/CSS).

## Example:
1) Default MiniMap:
   minimap = MiniMap()
   map.add_child(minimap)
   # On map rendering, the default TileLayer is used and the leaflet-minimap JS/CSS
   # resources (default_js/default_css) are registered into the Figure header.

2) Custom tile URL and options:
   minimap = MiniMap(
       tile_layer="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
       position="bottomleft",
       width=120,
       height=120,
       minimized=True
   )
   map.add_child(minimap)
   # parse_options will convert width,height,minimized,position to camelCase keys
   # and store them in minimap.options; zoom_level_fixed is omitted if left as None.

Implementation notes:
- Preserve the exact class-level default_js/default_css tuples so JSCSSMixin can register the plugin assets.
- Do not register JS/CSS during __init__; rely on JSCSSMixin.render to add resources only when a Figure root exists.
- Keep the tile_layer resolution logic identical (None -> TileLayer(); TileLayer instance -> use; otherwise forward to TileLayer(value)) to match expected behavior.

### `folium.plugins.minimap.MiniMap.__init__` · *method*

## Summary:
Initializes a MiniMap plugin instance by setting its identifying name, creating or assigning an internal TileLayer, and normalizing/storing the MiniMap configuration options on the instance.

## Description:
This constructor is invoked when a developer or library code creates a MiniMap object (typically during map composition, e.g., when a user does minimap = MiniMap(...) and then adds it to a folium.Map). It runs at object construction time — before the plugin is added to a map — and prepares internal state required later for rendering and serialization into the Leaflet/JavaScript representation.

This logic is kept in the constructor because it:
- Ensures the instance has a valid TileLayer object (always a folium.raster_layers.TileLayer) for rendering the minimap tiles.
- Centralizes option normalization (via parse_options) so downstream code can rely on a canonical, camelCased options dict with None values removed.
- Calls the base class initializer to set up MacroElement-internal state needed by the folium element lifecycle.

## Args:
    tile_layer (None | TileLayer | Any): Optional. If None, a default TileLayer() instance is created. If an instance of TileLayer is passed, it is assigned directly to self.tile_layer. Otherwise, the value is passed as the single argument to TileLayer(...) to construct a TileLayer (typical values here are tile URL templates, other TileLayer initialization parameters, or objects accepted by TileLayer).
        Default: None
    position (str): Control position on the map container. Typical Leaflet control positions are "topleft", "topright", "bottomleft", "bottomright". The value is passed through to parse_options unchanged and will be camelCased if necessary.
        Default: "bottomright"
    width (int): Width in pixels of the minimap control.
        Default: 150
    height (int): Height in pixels of the minimap control.
        Default: 150
    collapsed_width (int): Width in pixels when the minimap is collapsed.
        Default: 25
    collapsed_height (int): Height in pixels when the minimap is collapsed.
        Default: 25
    zoom_level_offset (int): Relative zoom offset applied to the minimap compared to the main map.
        Default: -5
    zoom_level_fixed (int | None): If provided, fixes the minimap to a concrete zoom level; None means no fixed zoom (minimap follows offset behavior).
        Default: None
    center_fixed (bool): If True, the minimap's center is fixed and does not follow the main map's center.
        Default: False
    zoom_animation (bool): If True, minimap updates include zoom animation (behavior delegated to front-end).
        Default: False
    toggle_display (bool): If True, a toggle control to show/hide the minimap will be enabled.
        Default: False
    auto_toggle_display (bool): If True, minimap display may toggle automatically under certain UI interactions (delegated to front-end plugin).
        Default: False
    minimized (bool): If True, the minimap is initially shown in its minimized/collapsed form.
        Default: False
    **kwargs: Additional keyword options accepted by the front-end plugin. Keys and values are forwarded to parse_options and will be camelCased and filtered (entries with value None are removed).

## Returns:
    None. The constructor returns None but mutates the instance state (see State Changes).

## Raises:
    Any exception raised by the called constructors or helpers may propagate:
    - Exceptions from TileLayer(...) (TypeError, ValueError, etc.) if the provided tile_layer value is not acceptable to TileLayer's constructor.
    - Exceptions from parse_options (or its internal camelize) such as AttributeError or TypeError if kwargs contain keys that are not string-like or otherwise incompatible with the normalization routine.
    - Exceptions raised by the base class __init__ (MacroElement.__init__) may also propagate.

## State Changes:
    Attributes READ:
        - None of the instance attributes are explicitly read before being overwritten. The method does call isinstance(tile_layer, TileLayer) which references the TileLayer class object in module scope.
    Attributes WRITTEN:
        - self._name (str): set to the literal "MiniMap".
        - self.tile_layer (TileLayer): set to a TileLayer instance (created here or assigned from the argument).
        - self.options (dict[str, Any]): set to the result of parse_options(...), containing camelCased option names with any None-valued entries removed.
    Other effects on self:
        - The base-class initializer is executed (via super().__init__()), which may write additional MacroElement-internal attributes (not enumerated here).

## Constraints:
    Preconditions:
        - The caller should ensure tile_layer is either None, already an instance of folium.raster_layers.TileLayer, or a value acceptable to TileLayer(...) constructor.
        - Keys in **kwargs should be string-like (parse_options expects string keys; non-string keys can cause camelize to raise).
    Postconditions:
        - After return, self._name == "MiniMap".
        - self.tile_layer is guaranteed to be an instance of TileLayer.
        - self.options is a dict whose keys are camelCased forms of the provided option names and which contains no entries whose value was None.

## Side Effects:
    - Instantiates a TileLayer object when tile_layer is None or when tile_layer is not already a TileLayer instance; this runs TileLayer.__init__ and any side effects it contains.
    - Calls parse_options, which is a pure in-memory normalization routine (no I/O).
    - Calls the MacroElement base-class constructor (super().__init__()), which may perform internal initialization (e.g., registering template names or internal IDs) but does not perform external I/O by itself in typical implementations.
    - No network, filesystem, or other external I/O is performed directly in this constructor.

