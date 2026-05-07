# `marker_cluster.py`

## `folium.plugins.marker_cluster.MarkerCluster` · *class*

## Summary:
A folium Layer plugin that groups many point Markers into an interactive Leaflet.markercluster cluster on a map, improving visualization and performance when many markers are present.

## Description:
MarkerCluster collects Marker children from a provided list of geographic locations (and optional aligned popups/icons) and exposes options that control client-side clustering behavior through the Leaflet.markercluster JavaScript/CSS referenced by the class-level default_js/default_css. Instantiate this class when you want automatic creation of Marker instances from raw coordinates or when you want to aggregate many markers into clustered groups on render.

Typical usage:
- Create a MarkerCluster with locations (and optionally popups/icons/options), then add it to a folium.Map using map.add_child(...) or marker_cluster.add_to(map).
- You can also create an empty MarkerCluster and add Marker children later using the inherited add_child API.

Motivation and responsibility:
- Responsibility: convert Python-side Marker specifications into a Layer that, when rendered, emits the JS/CSS and configuration needed for Leaflet.markercluster to cluster markers in the browser.
- Boundary: MarkerCluster does not implement clustering logic in Python — the clustering is performed by the Leaflet.markercluster library in the browser. MarkerCluster only validates and constructs Marker children and stores configuration for template rendering.

## Constructor Parameters (detailed):
- locations (iterable or None)
  - Type: iterable of location specifiers (e.g., (lat, lon) tuples, lists, or other formats accepted by folium.utilities.validate_locations)
  - Default: None
  - Behavior: if provided, locations is passed through validate_locations(...) to normalize/validate coordinates. For each validated location, a Marker is created and added as a child.
  - Constraints/Edge cases:
    - If locations is None, no automatic Marker children are created.
    - If locations is provided, popups/icons (if truthy) are expected to be indexable sequences aligned with locations; otherwise indexing will raise IndexError.
    - Any exception raised by validate_locations is propagated.

- popups (sequence-like or None)
  - Type: sequence/indexable (e.g., list) or None
  - Default: None
  - Behavior: if truthy, each created Marker will receive popup=popups[i] for the corresponding location index; if falsy/None, no popup is passed to Marker.
  - Constraint: must be indexable and at least as long as locations if used.

- icons (sequence-like or None)
  - Type: sequence/indexable of folium Icon-like objects or None
  - Default: None
  - Behavior: if truthy, each created Marker will receive icon=icons[i] for the corresponding location index; if falsy/None, no icon is passed to Marker.
  - Constraint: must be indexable and at least as long as locations if used.

- name (str or None)
  - Type: str or None
  - Default: None
  - Behavior: forwarded to Layer.__init__ to name the layer in folium internals.

- overlay (bool)
  - Type: bool
  - Default: True
  - Behavior: forwarded to Layer.__init__; controls whether the layer is treated as an overlay.

- control (bool)
  - Type: bool
  - Default: True
  - Behavior: forwarded to Layer.__init__; controls whether the layer appears in LayerControl.

- show (bool)
  - Type: bool
  - Default: True
  - Behavior: forwarded to Layer.__init__; initial visibility on the map.

- icon_create_function (str or None)
  - Type: str or None
  - Default: None
  - Behavior: a string that should contain a JavaScript function (or function name) used client-side to create cluster icons. It is stored in self.icon_create_function and rendered into the client-side template.
  - Constraint: if provided, must be a str; otherwise the constructor raises AssertionError.

- options (dict or None) — legacy
  - Type: dict or None
  - Default: None
  - Behavior: a legacy way to pass Leaflet.markercluster options. If provided, this dict is merged into kwargs (kwargs.update(options)). Prefer passing plugin options as keyword arguments directly.
  - Note: keys in options/kwargs are parsed by parse_options(...) and stored in self.options.

- **kwargs
  - Type: additional keyword options passed through to parse_options(...)
  - Behavior: used to build the self.options dict representing configuration for the client-side plugin.

## State:
Public and notable instance attributes after construction:

- _name (str)
  - Value: "MarkerCluster"
  - Role: identifier used by folium's Layer internals.

- options (dict)
  - Value: result of parse_options(**kwargs) after merging legacy options into kwargs (if options provided).
  - Role: holds plugin configuration that will be emitted into the client-side JavaScript template.

- icon_create_function (str | None)
  - Value: stored string if provided, else None.
  - Role: client-side function used to generate cluster icons.

- children (inherited container of child layers/markers)
  - Value: Marker instances added either by the constructor (when locations is supplied) or via add_child afterwards.
  - Invariant: child entries created from constructor locations will have their location set to the corresponding validated coordinate and their popup/icon set per popups/icons inputs.

Class-level attributes (constants):
- _template (jinja2.Template): jinja2 template used by folium rendering (defined but empty in this source snippet).
- default_js, default_css (list[tuple[str,str]]): lists of asset name/URL pairs for Leaflet.markercluster JS/CSS. These are required resources for the plugin and are included automatically by folium when rendering.

Class invariants:
- After __init__, icon_create_function is either None or a str.
- options is always a dict (result of parse_options).
- _name equals "MarkerCluster".

## Lifecycle:
Creation:
- Call MarkerCluster(...) with the parameters described above. If options (legacy dict) is provided it is merged into keyword arguments. The constructor:
  1. merges options into kwargs if options is not None,
  2. calls Layer.__init__ with name/overlay/control/show,
  3. sets self._name,
  4. if locations provided: validates locations and creates child Marker instances for each location with aligned popups/icons,
  5. sets self.options = parse_options(**kwargs),
  6. asserts that icon_create_function is a str if provided and stores it.

Usage:
- After instantiation, add the MarkerCluster to a folium.Map via map.add_child(cluster) or cluster.add_to(map).
- The folium rendering pipeline will include the plugin JS/CSS (default_js/default_css), emit the template (self._template) and pass self.options and self.icon_create_function into the template to initialize client-side clustering.
- Additional Marker children can be added or removed via add_child/remove_child (inherited methods) before rendering; they will be included in the cluster.

Destruction / cleanup:
- No explicit Python-level cleanup. Removal or omission from the final rendered map prevents inclusion of the cluster. Client-side resources are managed in the browser.

## Method Map:
flowchart LR
    Init[__init__] --> MergeOptions{options legacy?}
    MergeOptions -- yes --> UpdateKwargs[kwargs.update(options)]
    MergeOptions -- no --> SkipUpdate
    Init --> CallSuper[Layer.__init__(name,overlay,control,show)]
    Init --> SetName[_name = "MarkerCluster"]
    Init --> CheckLocations{locations provided?}
    CheckLocations -- yes --> Validate[validate_locations(locations)]
    Validate --> CreateMarkers[for i, location -> Marker(location, popup=popups and popups[i], icon=icons and icons[i])]
    CreateMarkers --> AddChildren[add_child(Marker...)]
    Init --> ParseOptions[self.options = parse_options(**kwargs)]
    Init --> IconAssert[assert isinstance(icon_create_function, str) if provided]
    IconAssert --> Ready[Instance ready; add to Map]

Note: add_child, parse_options, validate_locations and Marker are external calls (folium utilities) invoked during initialization; their behavior is delegated to those components.

## Raises:
- AssertionError
  - Condition: icon_create_function is provided but is not an instance of str (the constructor uses assert isinstance(icon_create_function, str)).

- IndexError
  - Condition: popups or icons are truthy but shorter than locations; indexing popups[i] or icons[i] will raise IndexError during Marker creation.

- Exceptions propagated from validate_locations(...)
  - Condition: invalid or malformed locations as determined by validate_locations; exact exception types/messages come from that utility and are propagated.

- Exceptions propagated from Marker(...) creation
  - Condition: if creating a Marker for a validated location raises an error (e.g., invalid popup/icon), that exception will propagate out of __init__.

## Example:
Minimal creation and usage steps (no import lines shown):

1) Create a map (example uses an existing folium.Map instance named my_map).
2) Create a MarkerCluster from a list of coordinates and add it to the map:

   coords = [(51.5, -0.1), (51.495, -0.083), (51.49, -0.1)]
   popups = ['A', 'B', 'C']             # must be index-aligned with coords if provided
   cluster = MarkerCluster(
       locations=coords,
       popups=popups,
       icon_create_function='function(cluster) { return L.divIcon({html: cluster.getChildCount()}); }',
       maxClusterRadius=50              # example plugin option passed through kwargs/parse_options
   )
   cluster.add_to(my_map)              # or my_map.add_child(cluster)

3) Alternatively create an empty cluster and add markers later:
   empty_cluster = MarkerCluster()
   empty_cluster.add_child(Marker((51.5, -0.1), popup='point A'))
   empty_cluster.add_to(my_map)

Notes:
- If you need to pass many plugin options, pass them as keyword arguments (the legacy options dict is also supported and merged).
- icon_create_function must be a JavaScript string. The constructor only asserts its type; folium will render it into the client-side template as-is.

## Implementation notes (for reimplementation):
- The constructor merges options (legacy dict) into kwargs, calls the parent Layer constructor, sets the internal name, optionally validates and iterates locations to instantiate Marker objects, stores parsed options via parse_options(**kwargs), and enforces that icon_create_function is a string if supplied.
- Keep error propagation behavior consistent: do not swallow exceptions from validate_locations or Marker creation, and allow IndexError/AssertionError to bubble up so callers see misaligned input or invalid types.

### `folium.plugins.marker_cluster.MarkerCluster.__init__` · *method*

## Summary:
Initializes the MarkerCluster plugin instance, sets up its identity and options, and (optionally) creates and attaches child Marker objects from a sequence of locations.

## Description:
This constructor is invoked when a MarkerCluster plugin is instantiated (typically by user code that constructs a plugin and then adds it to a Map via map.add_child(plugin) or by calling plugin.add_to(map)). It establishes plugin metadata, parses and stores configuration options, and — if a list of locations is provided — validates those locations and creates Marker children for each.

Placing this logic in a dedicated constructor:
- centralizes initialization of plugin state (name, options, icon creation function),
- ensures location validation and marker creation occur immediately on construction so the resulting instance is ready to be attached to a map,
- keeps option-parsing and legacy-options handling (the deprecated options dict) localized to object construction.

## Args:
    locations (iterable|None): Optional iterable of location entries (e.g., (lat, lng) pairs or other forms accepted by validate_locations). If provided, entries are validated via validate_locations and each entry results in a child Marker being created and added. Default: None.
    popups (sequence|None): Optional sequence of popup values corresponding by index to locations. If truthy, popups[i] is passed as the popup for the i-th Marker. If None or falsy, no popup is attached. Default: None.
    icons (sequence|None): Optional sequence of icon objects corresponding by index to locations. If truthy, icons[i] is passed as the icon for the i-th Marker. If None or falsy, no icon is attached. Default: None.
    name (str|None): Name passed to the parent Layer initializer. Default: None.
    overlay (bool): Passed through to the parent Layer initializer; controls whether the layer is an overlay. Default: True.
    control (bool): Passed through to the parent Layer initializer; controls whether the layer has a layer control entry. Default: True.
    show (bool): Passed through to the parent Layer initializer; controls whether the layer is shown by default. Default: True.
    icon_create_function (str|None): Optional JavaScript function source (as a string) used by the marker-clustering frontend to customize cluster icons. If provided, it must be a str (an assertion enforces this). Default: None.
    options (dict|None): Legacy container for configuration options. If provided, its keys are merged into kwargs (overwriting any same-named keys present in kwargs).
    **kwargs: Additional keyword options passed to parse_options to build self.options.

## Returns:
    None: This is an initializer; it constructs and mutates the instance in-place. No value is returned.

## Raises:
    AssertionError: If icon_create_function is not None but is not an instance of str.
    IndexError: If popups or icons is a sequence shorter than locations and the code attempts to access popups[i] or icons[i] for some index i.
    Any exception raised by validate_locations: If locations argument is invalid, validate_locations may raise (propagated).
    Any exception raised by parse_options: If option parsing fails, that exception is propagated.

## State Changes:
Attributes READ:
    - None of the instance attributes are read explicitly by this __init__ before they are set (note: parent __init__ may read or initialize attributes internally).

Attributes WRITTEN:
    - self._name (str): Set to the literal "MarkerCluster".
    - self.options (dict): Set to the result of parse_options(**kwargs) after merging legacy options.
    - self.icon_create_function (str|None): Set to the provided icon_create_function (after the type assertion when non-None).
    - child collection / internal layer state: Mutated by calls to self.add_child(...) for each provided location (this registers Marker instances as children of this layer).

## Constraints:
Preconditions:
    - If icon_create_function is provided, it must be a str (otherwise an AssertionError is raised).
    - If locations, popups, and icons are provided, they should be index-aligned sequences; otherwise an IndexError can occur when accessing popups[i] or icons[i].
    - kwargs and options should be valid inputs for parse_options (parse_options will validate/transform them and may raise on invalid values).

Postconditions:
    - self._name == "MarkerCluster".
    - self.options contains the parsed options produced by parse_options after merging any legacy options dict into kwargs.
    - self.icon_create_function is assigned the provided value (or None).
    - If locations were provided and validated, there will be one child Marker added to this instance per validated location, each constructed with the corresponding popup and icon (if provided and available).

## Side Effects:
    - Calls self.add_child(...) repeatedly when locations is provided; this mutates the instance's child registry and constructs Marker objects.
    - Calls validate_locations(locations) and parse_options(**kwargs); any exceptions from those utilities propagate outward.
    - No file I/O or network I/O is performed directly by this method; side effects are limited to object construction and mutation (including constructing Marker instances).

