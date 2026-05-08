# `search.py`

## `folium.plugins.search.Search` · *class*

## Summary:
A MacroElement wrapper that integrates the Leaflet.Search plugin with a folium Map, enabling on-map search functionality over a supported layer (GeoJson, TopoJson, MarkerCluster, or FeatureGroup).

## Description:
This class represents the folium-side integration of the Leaflet.Search plugin. Instantiate it when you want an on-map search box that looks up features from one of the supported layer types and recenters/zooms the map to matched features. The Search instance is intended to be added as a child to a folium.Map (for example via map.add_child(search_instance) or map.add_child(...)).

Known callers/factories:
- Typically created directly by application code when constructing a map (there are no internal factory functions in this module).
- The element is rendered by folium's rendering pipeline when the parent Map is rendered (e.g., map._repr_html_(), map.save()).

Motivation and responsibility boundary:
- Responsibility: provide configuration and validation for Leaflet.Search, collect static resources (JS/CSS) needed for the plugin, and validate that the target layer and map context are compatible.
- This class does not itself implement the search algorithm — it configures and injects the required plugin assets and renders the templated JavaScript that will be executed in the browser. It also validates the existence of the search label inside feature properties for GeoJson/TopoJson layers before rendering.

## State:
- _template: jinja2.Template
  - Purpose: template used by MacroElement to render plugin configuration into the map's HTML/JS.
  - Note: The class defines a Template object (content omitted in the provided source) that will be rendered by MacroElement.render.

- default_js: list[tuple[str, str]]
  - CDN name and URL for the Leaflet.Search JavaScript file.
  - Invariants: remains a list of (name, url) tuples.

- default_css: list[tuple[str, str]]
  - CDN name and URL for the Leaflet.Search CSS file.
  - Invariants: remains a list of (name, url) tuples.

- layer: GeoJson | TopoJson | MarkerCluster | FeatureGroup
  - The layer to index and search.
  - Constraint: must be an instance of one of these four types; otherwise __init__ raises AssertionError.

- search_label: Optional[str]
  - The property name (within features' properties) to search for.
  - If None, search may rely on alternate plugin configuration (behavior depends on the JS template); when provided, it must exist among keys derived from the layer's feature properties (checked by test_params).

- search_zoom: Optional[int]
  - If provided, this integer will be used as the zoom level when the map centers on a found result.
  - No explicit validation in code; callers should provide an integer (or None).

- geom_type: str (default "Point")
  - Expected geometry type string for matched features (passed through to plugin configuration).
  - No strict validation; plugin behavior depends on values acceptable to Leaflet.Search.

- position: str (default "topleft")
  - Position of the search control on the map (e.g., 'topleft', 'topright', 'bottomleft', 'bottomright').
  - No explicit validation in code; must be a position accepted by Leaflet controls.

- placeholder: str (default "Search")
  - Placeholder text displayed in the search input control.

- collapsed: bool (default False)
  - Whether the control is collapsed initially.

- options: dict
  - Parsed keyword arguments (parse_options(**kwargs)) forwarded as plugin options.
  - Valid values depend on parse_options behavior and plugin-supported options; parse_options typically returns a dict mapping option names to JSON-serializable values.

Class invariants:
- layer is one of the allowed layer types throughout the instance lifetime.
- After render() completes, test_params has been called with a keys value consistent with the layer type.
- The Search instance must be attached to a folium.Map (self._parent is a Map) prior to rendering; render() asserts this.

## Lifecycle:
Creation:
- Required argument:
  - layer: an instance of GeoJson, TopoJson, MarkerCluster, or FeatureGroup.
- Optional constructor arguments (with defaults):
  - search_label: None
  - search_zoom: None
  - geom_type: "Point"
  - position: "topleft"
  - placeholder: "Search"
  - collapsed: False
  - **kwargs: any additional plugin options passed through parse_options

Usage (typical sequence):
1. Instantiate: search = Search(layer, search_label='propName', search_zoom=12, ...)
2. Attach: map.add_child(search) — MacroElement attaches to the Map and sets search._parent to the Map.
3. Render: When map rendering is triggered (map.save, map._repr_html_(), etc.), Search.render() is called by the MacroElement/Map rendering pipeline. Render performs:
   - Determination of keys (property names) if the layer is GeoJson or TopoJson.
   - Calling test_params(keys) to assert correctness (search_label present if provided; parent is Map).
   - Delegating to MacroElement.render to render the template and include JS/CSS assets.
4. Browser-time: The templated JS/CSS runs client-side to activate Leaflet.Search behavior.

Destruction / cleanup:
- No explicit destruction API (no close/cleanup methods). Removal must be handled by removing the Search from the Map children before rendering or by not including it at render time. There are no context managers.

## Method Map:
graph LR
    A[__init__(layer, ...)] --> B[layer attribute set]
    B --> C[add to Map via map.add_child(search) => _parent set]
    C --> D[render(**kwargs)]
    D --> E{determine keys}
    E -->|GeoJson| F[get first feature properties keys]
    E -->|TopoJson| G[get object_path -> objects[obj_name].geometries[0].properties keys]
    E -->|MarkerCluster/FeatureGroup| H[keys = None]
    F --> I[test_params(keys)]
    G --> I
    H --> I
    I --> J[asserts: search_label in keys if provided; _parent is Map]
    J --> K[super().render(**kwargs) -> template rendered; JS/CSS injected]

Notes:
- test_params is invoked by render and not typically called directly by client code.
- There are no additional public methods exposed beyond __init__ and render/test_params (inherited MacroElement methods exist).

## Raises:
- AssertionError:
  - From __init__: if layer is not an instance of (GeoJson, MarkerCluster, FeatureGroup, TopoJson).
    - Message: "Search can only index FeatureGroup, MarkerCluster, GeoJson, and TopoJson layers at this time."
  - From test_params:
    - If search_label is provided and keys is not None but search_label not in keys:
      - Message: "The label '<search_label>' was not available in <keys>"
    - If the Search instance's _parent is not a folium.Map:
      - Message: "Search can only be added to folium Map objects."
- IndexError / KeyError / AttributeError:
  - Possible when reading layer.data for GeoJson or TopoJson if the layer data structure does not match the expected geojson/topojson layout (e.g., no features array, empty features, unexpected keys). These are not explicitly caught by Search and will propagate.

## Example:
1) Basic flow (textual example):
m = Map(location=[45.5236, -122.6750], zoom_start=13)
g = GeoJson(data=geojson_feature_collection)
search = Search(layer=g, search_label='name', search_zoom=15, placeholder='Find feature...')
m.add_child(search)
# When m.save('map.html') or rendering occurs, Search.render() validates parameters and injects the Leaflet.Search JS/CSS and configuration into the map.

2) TopoJson example notes:
- If layer is a TopoJson instance, ensure layer.object_path is set such that object_path.split(".")[-1] yields the object key present under layer.data["objects"][<obj_name>] and that the object has at least one geometry with properties.

Implementation hints for reimplementation:
- Ensure you inherit behavior from MacroElement to participate in folium's rendering pipeline.
- Expose default_js and default_css so that JSCSSMixin picks up plugin resources.
- test_params must verify search_label presence only when keys are provided (GeoJson/TopoJson paths) and must assert that _parent is a Map before rendering.
- In render(), detect layer type to extract property keys deterministically from the first feature/geometry (as in the original code) and pass these keys to test_params.

### `folium.plugins.search.Search.__init__` · *method*

## Summary:
Initialize the Search plugin element by validating the provided layer and storing configuration options on the instance for later rendering.

## Description:
This initializer is called when creating a new Search element to be added to a folium.Map. Typical callers:
- Application code that creates a Search instance during map construction (e.g., search = Search(layer, search_label='name')).
- The instance is subsequently attached to a Map via map.add_child(search), and folium's rendering pipeline calls Search.render() later.

This logic exists as an initializer to:
- Validate that the provided layer is one of the supported layer types early (fail-fast).
- Establish the instance state (attributes and parsed options) that render() and other methods will rely on.
- Keep validation and state setup centralized so render/test_params can assume a consistent internal representation.

## Args:
    layer (GeoJson | TopoJson | MarkerCluster | FeatureGroup):
        The layer whose features will be indexed by the client-side Leaflet.Search plugin.
        Required. Must be an instance of one of the listed folium feature/collection classes.
    search_label (Optional[str], default=None):
        Name of the feature property to search for (e.g., "name"). If provided, render-time checks will assert that this key exists in the layer's properties for GeoJson/TopoJson layers.
    search_zoom (Optional[int], default=None):
        Zoom level to set when a search result is selected. If None, the plugin's default zoom behavior is used.
    geom_type (str, default="Point"):
        Geometry type passed through to the plugin configuration (commonly "Point", but the plugin may accept other geometry descriptors).
    position (str, default="topleft"):
        Position of the search control on the map. Expected values are the Leaflet control positions (e.g., 'topleft', 'topright', 'bottomleft', 'bottomright').
    placeholder (str, default="Search"):
        Placeholder text displayed in the search input control.
    collapsed (bool, default=False):
        Whether the control is rendered in a collapsed state initially.
    **kwargs:
        Additional plugin options. These are forwarded through parse_options(**kwargs) and stored on the instance as a dict in self.options. The allowed keys/values depend on the plugin and parse_options behavior.

## Returns:
    None

## Raises:
    AssertionError:
        If the provided layer is not an instance of (GeoJson, MarkerCluster, FeatureGroup, TopoJson).
        Exact message raised by the initializer:
        "Search can only index FeatureGroup, MarkerCluster, GeoJson, and TopoJson layers at this time."

    (Notes: No other exceptions are explicitly raised here. Errors originating from parse_options(**kwargs) or from unexpected types passed as arguments may propagate.)

## State Changes:
Attributes READ:
    - No existing self.<attr> fields are read from this initializer.
    - Calls external function parse_options and class constructors (via isinstance checks) and calls super().__init__().

Attributes WRITTEN:
    - self.layer: set to the provided layer argument.
    - self.search_label: set to the provided search_label argument.
    - self.search_zoom: set to the provided search_zoom argument.
    - self.geom_type: set to the provided geom_type argument.
    - self.position: set to the provided position argument.
    - self.placeholder: set to the provided placeholder argument.
    - self.collapsed: set to the provided collapsed argument.
    - self.options: set to the dict returned by parse_options(**kwargs).
    - Any initialization performed by super().__init__() (MacroElement) may set internal attributes (e.g., _parent), but this initializer does not modify them directly.

## Constraints:
Preconditions:
    - The caller must provide a non-null layer that is an instance of one of: GeoJson, MarkerCluster, FeatureGroup, TopoJson.
    - Argument types should be appropriate (search_label as str or None, search_zoom as int or None, geom_type/position/placeholder as str, collapsed as bool). The initializer does not perform strict type coercion beyond the layer type assertion.

Postconditions:
    - self.layer holds the provided layer and will remain an instance of the allowed types.
    - Configuration attributes (search_label, search_zoom, geom_type, position, placeholder, collapsed) reflect the values passed by the caller (or the documented defaults).
    - self.options is a dictionary produced by parse_options(**kwargs) suitable for later JSON serialization into the plugin configuration.
    - The instance is ready for attachment to a Map and subsequent render() calls to perform validation that depends on map context and layer contents.

## Side Effects:
    - Calls super().__init__() to initialize MacroElement base state (this may register template/container internals required for rendering).
    - Calls parse_options(**kwargs) to normalize/validate extra options; parse_options may transform inputs into JSON-serializable values and may raise if given unsupported input types.
    - No I/O, network calls, or browser interactions occur in __init__ itself.

### `folium.plugins.search.Search.test_params` · *method*

## Summary:
Validate that the configured search label exists among provided property keys (when available) and ensure the Search element is attached to a folium Map; raises AssertionError on failure.

## Description:
This method performs pre-render validation for a Search instance. Known callers:
- Search.render: render computes available keys from the underlying layer (for GeoJson and TopoJson) or passes None (for non-feature layers) and then calls test_params(keys=...) immediately before proceeding with rendering. This places test_params in the render-time validation stage of the Search lifecycle.

Reason for being a separate method:
- Centralizes the invariant checks (required label presence and correct parent type) so they can be reused and tested independently of render's data-preparation logic.

## Args:
    keys (tuple | None): The collection of property/key names available on the indexed layer's features as provided by the caller, or None when keys cannot be determined. The method does not enforce the element types inside keys; it only checks membership with the equality semantics of the 'in' operator.

## Returns:
    None
    - The method only performs assertions for validation and returns None when validations pass.

## Raises:
    AssertionError:
        - If keys is not None and self.search_label is not None, and self.search_label is not an element of keys.
          Exact message: "The label '{}' was not available in {}".format(self.search_label, keys)
        - If self._parent is not an instance of folium.Map (this includes the case where self._parent is None).
          Exact message: "Search can only be added to folium Map objects."

## State Changes:
    Attributes READ:
        - self.search_label
        - self._parent
    Attributes WRITTEN:
        - None (no attributes are modified)

## Constraints:
    Preconditions:
        - The Search instance has been constructed (attributes such as self.search_label exist).
        - The caller supplies keys which may be a tuple or other iterable or None; this method treats keys only as a container for membership checks.
        - Typically, self._parent is set when the element is added to a folium Map; if it is not set to a Map instance, the parent-type assertion will fail.

    Postconditions:
        - If no exception is raised:
            * If both keys and self.search_label were not None, then self.search_label is a member of keys.
            * self._parent is an instance of folium.Map.
        - No object state is mutated by this method.

## Side Effects:
    - No I/O or network calls.
    - No mutations to objects outside self.
    - The only observable effects are successful return (None) or raising AssertionError.

## Reimplementation checklist:
    - Accept a single parameter keys (iterable or None).
    - If both keys and self.search_label are not None, assert that self.search_label in keys using the exact formatted assertion message above.
    - Assert that isinstance(self._parent, Map) using the exact assertion message above.
    - Do not catch these AssertionError exceptions inside the method.

### `folium.plugins.search.Search.render` · *method*

## Summary:
Performs pre-render validation and metadata extraction for the Search plugin (extracts property keys from GeoJson/TopoJson layers and validates parameters), then delegates to the parent class to perform the actual rendering. This affects the object's rendering state by allowing the MacroElement rendering step to proceed (or by raising on invalid state).

## Description:
- Known callers and lifecycle:
    - Typically invoked during folium map rendering (for example, when folium.Map.render or folium.Map._repr_html_ constructs the HTML/JS for the map). It is the Search plugin's override of the MacroElement render hook and is called as part of the map/template rendering pipeline.
    - It may also be invoked directly by code that explicitly renders this element via MacroElement.render.
- Why this logic is a separate method:
    - The method bundles parameter validation and layer-specific metadata extraction (property keys) prior to rendering. Separating this into render ensures the Search instance validates that it can be rendered in the current context (correct parent type and valid search_label when applicable) and collects required keys for template generation before delegating the actual output generation to the superclass. This keeps validation and metadata gathering close to the render-time context and prevents inlining these checks elsewhere.

## Args:
    **kwargs: dict
        Arbitrary keyword arguments forwarded to the superclass (MacroElement) render method. No local kwargs are processed by this method; they are passed through to the base render implementation.

## Returns:
    None
    - The method does not return a value. Successful completion means superclass rendering was invoked without raising from this method.

## Raises:
    AssertionError
        - If the Search instance is not attached to a folium.Map when rendering (test_params asserts that self._parent is a Map). Exact trigger: self._parent is not an instance of folium.Map.
        - If keys (extracted from GeoJson/TopoJson) is not None and self.search_label is not None but self.search_label is not present in keys. Exact trigger: self.search_label not in keys.
    KeyError / IndexError / AttributeError (possible)
        - If a GeoJson or TopoJson layer does not have the expected nested structure (for example, missing "features", missing "properties", unexpected object_path format, or missing "geometries"), those underlying dictionary/list accesses will raise standard Python errors. These are not explicitly caught by the method.
    TypeError (possible)
        - If self.layer is an unexpected type that provides attributes but not the expected dict/list structures, attribute accesses may raise TypeError. The constructor normally restricts layer types, but malformed layer objects can cause these errors at render-time.

## State Changes:
- Attributes READ:
    - self.layer: inspected to determine whether it is a GeoJson, TopoJson, or another supported layer and to extract property keys from its data.
    - self.search_label: read by test_params to validate that the requested search label exists among extracted keys (if keys are available).
    - self._parent: read by test_params to assert that the Search instance is attached to a folium.Map prior to rendering.
- Attributes WRITTEN:
    - None directly within this method's body. Note: the call to super().render(**kwargs) may mutate attributes defined/managed by the MacroElement or Map (e.g., registering this element with its parent or modifying parent's render state), but this method itself does not assign to self.<attr>.

## Constraints:
- Preconditions:
    - The Search instance should have been constructed with a valid layer (constructor asserts that layer is one of GeoJson, MarkerCluster, FeatureGroup, or TopoJson). While that constructor assertion usually enforces layer type, render assumes:
        - If the layer is a GeoJson: layer.data is a mapping with "features" → list-like where features[0]["properties"] is a mapping of property names.
        - If the layer is a TopoJson: layer.object_path is a dotted path that identifies an object in layer.data["objects"], and layer.data["objects"][obj_name]["geometries"][0]["properties"] is a mapping of property names.
    - The Search instance must be attached to a folium.Map as its _parent before render is called; otherwise an AssertionError is raised.
- Postconditions:
    - If the method returns normally (no exception), then:
        - test_params passed: self._parent is a folium.Map and, if keys were available and self.search_label was provided, self.search_label was present among the keys.
        - The superclass render has been invoked, so the element has been processed by MacroElement.render (templates are rendered/queued and the element participates in the parent's rendered output).

## Side Effects:
- Delegates to the MacroElement render pipeline via super().render(**kwargs), which commonly:
    - Causes template rendering and the inclusion of the plugin's JS/CSS and initialization code in the final HTML/JS output for the parent Map.
    - May mutate the parent Map's internal state (for example, registering children, modifying the parent's rendering context). These effects stem from the superclass implementation, not this method directly.
- No external I/O (network, file) is performed by this method itself.

