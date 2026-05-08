# `map.py`

## `folium.map.Layer` · *class*

## Summary:
Represents a generic map layer element that stores layer metadata used by higher-level map/figure containers. It provides named, toggleable layer state (overlay/control/show) but implements no rendering itself.

## Description:
Layer is a lightweight abstraction that holds the common metadata for a layer-like element. It is intended to be instantiated when a developer or a subclass needs an object that:

- Carries a stable name (layer_name) for identification in a parent container.
- Exposes flags that control whether it is an overlay (overlay), whether it should appear in UI layer controls (control), and whether it is initially visible (show).

Behavioral notes derived from the source:
- If the caller provides name=None, the constructor obtains a name by calling the instance method get_name(), which must be provided by the class or an ancestor (Layer itself does not implement get_name()).
- Layer itself does not define rendering methods; it only stores metadata. Any visual or DOM contributions are the responsibility of subclasses or container objects that use Layer instances.

## State:
Attributes set by __init__ (public):

- layer_name (str)
    - Description: Identifier for the layer.
    - Set by: name parameter if provided; otherwise result of self.get_name().
    - Expected type: string (the implementation does not enforce type at runtime; callers should provide or expect a string).
    - Default behavior: If name is None, the inherited get_name() method is invoked and its return value is used.

- overlay (bool)
    - Description: Whether the layer is treated as an overlay (True) or a base layer (False).
    - Valid values: True or False
    - Default: False

- control (bool)
    - Description: Whether the layer should be included in UI layer controls.
    - Valid values: True or False
    - Default: True

- show (bool)
    - Description: Whether the layer should be shown (visible) by default when added to a parent container.
    - Valid values: True or False
    - Default: True

Class invariants (expected, not enforced by Layer):
- layer_name should remain a stable identifier for the lifetime of the object.
- overlay, control, and show should remain booleans; callers/users should not replace them with non-boolean values.

## Lifecycle:
Creation:
- Instantiate by calling Layer(name=None|str, overlay=False|bool, control=True|bool, show=True|bool).
- Required arguments: none; all parameters have defaults.
- If name is omitted or None, Layer.__init__ calls self.get_name() to obtain an identifier. An implementation must ensure that get_name() exists on the class or an ancestor.

Usage:
- Typical sequence:
    1. Instantiate Layer (explicit name or rely on inherited get_name()).
    2. Optionally adjust attributes (overlay/control/show) before attaching to a parent container.
    3. Attach the Layer instance to a parent container (such as a map/figure) that consumes the metadata and performs rendering/control behavior.
- There is no required method-call ordering enforced by Layer itself beyond the constructor; attaching to a parent container is the usual next step.

Destruction / cleanup:
- Layer defines no explicit destruction or cleanup responsibilities. It has no close(), __exit__, or similar resource-management APIs. Any cleanup required by subclasses or containers must be implemented by those components.

## Method Map:
A small call-flow diagram (Mermaid format) showing how __init__ interacts with superclass initialization and the conditional name resolution:

graph TD
    A[Caller -> Layer.__init__(name, overlay, control, show)] --> B[super().__init__() (MacroElement.__init__)]
    B --> C{name is not None?}
    C -- yes --> D[layer_name := name]
    C -- no --> E[layer_name := self.get_name() (inherited)]
    D --> F[set overlay, control, show attributes]
    E --> F
    F --> G[Layer instance ready]

## Raises:
- Layer.__init__ does not explicitly raise any exceptions in the provided source.
- If the inherited get_name() method raises an exception when name is None, that exception will propagate through Layer.__init__. Callers that rely on implicit name resolution should be prepared to handle exceptions from get_name().

## Example (usage described in prose):
- Create with explicit name:
    - Call Layer(name="My Layer", overlay=True, control=True, show=False).
    - The instance will have layer_name = "My Layer", overlay = True, control = True, show = False.
- Create without explicit name:
    - Call Layer() with no arguments.
    - Layer.__init__ will call self.get_name() and set layer_name to that return value.
- After creation:
    - Attach the Layer instance to a parent container (for example, a map or figure object) that is responsible for rendering and using the metadata stored on the Layer.
    - No cleanup method is required on Layer itself; removal/cleanup behavior is the responsibility of the parent container or subclasses.

### `folium.map.Layer.__init__` · *method*

## Summary:
Initializes a Layer instance by delegating to the superclass initializer and storing canonical layer metadata (layer_name, overlay, control, show) on the object.

## Description:
This constructor is invoked during object creation (Layer(...) or subclass construction) to establish the common, non-rendering metadata that identifies and configures a layer for containing objects (maps, figures, or layer-management controls). Typical callers:
- Direct instantiation in user code (for generic layer containers).
- Subclass __init__ methods that call super().__init__(...) to inherit common metadata handling before adding subclass-specific state.
- Factory or container code that constructs a layer before attaching it to a map/figure.

Lifecycle stage: called at construction time (object creation). It runs immediately after Python allocates the instance and before the instance is used or attached to a parent container.

Why this is a separate method:
- Centralizes and standardizes metadata initialization shared across many layer subclasses and callers.
- Keeps subclass constructors simple: subclasses can focus on visual or data-specific initialization and call the Layer constructor to get a consistent identifier and control flags.
- Isolates conditional name resolution (use provided name or fallback to get_name()) so that naming semantics are consistent across the codebase.

## Args:
    name (str | None): Optional explicit name for the layer. If provided, its value is assigned to layer_name. If None, the constructor calls self.get_name() to obtain a fallback name. Default: None.
    overlay (bool): Whether this layer should be treated as an overlay (True) or as a base layer (False). Default: False.
    control (bool): Whether this layer should be included in UI layer controls (True) or omitted (False). Default: True.
    show (bool): Whether the layer should be visible/showing by default when added to a parent container. Default: True.

Notes on types and allowed values:
- The implementation does not enforce types at runtime; callers should pass values of the documented types. overlay, control, and show are expected to be booleans; non-boolean truthy/falsy values will be accepted but are non-ideal.
- name is expected to be a human-readable identifier (string). If name is None, get_name() must return a usable identifier.

## Returns:
    None

## Raises:
    Any exception raised by the superclass initializer (super().__init__()) will propagate.
    Any exception raised by self.get_name() will propagate when name is None.
    No additional exceptions are explicitly raised by this constructor.

Examples of possible propagated exceptions:
- AttributeError if get_name is not defined on the instance and name is None.
- Any errors raised during superclass initialization (e.g., if MacroElement.__init__ requires certain conditions).

## State Changes:
Attributes READ:
    - None explicitly read from self by this method. (Note: self.get_name() is invoked when name is None; that method may read instance attributes, but such reads occur inside get_name(), not inside this __init__.)

Attributes WRITTEN:
    - self.layer_name: set to name if name is not None, otherwise set to the value returned by self.get_name().
    - self.overlay: set to the overlay argument value.
    - self.control: set to the control argument value.
    - self.show: set to the show argument value.

## Constraints:
Preconditions:
    - The object must be a valid instance whose MRO provides a working superclass constructor (the call to super().__init__() must be appropriate).
    - If name is None, the instance must implement get_name() (in the class or a base class) and get_name() must return a suitable identifier.
    - Callers should supply booleans for overlay, control, and show to avoid type ambiguity.

Postconditions:
    - After return, the instance has layer_name, overlay, control, and show attributes set as described.
    - No additional invariants are enforced; downstream code should treat these attributes as authoritative metadata for the layer.

## Side Effects:
    - Calls super().__init__(), which may perform additional initialization or set attributes defined in base classes (this may have side effects defined by the superclass).
    - Calls self.get_name() when name is None; behavior and side effects depend on that implementation.
    - No I/O, network requests, or global state modifications are performed by this constructor itself.

## `folium.map.FeatureGroup` · *class*

## Summary:
Represents a named, toggleable map feature group layer that holds front-end options for client-side rendering; it is a lightweight Layer subclass that collects a tile/name identifier and normalized rendering options.

## Description:
FeatureGroup is a small concrete subclass of Layer intended to group map features (markers, polygons, etc.) under a single toggleable layer entry. Instantiate this class when you need a logical grouping that:
- Carries a stable tile/name identifier (used by parent containers and UI layer controls).
- Supplies a dictionary of normalized options prepared for front-end (JavaScript/Leaflet) consumption.

Known callers / creation sites:
- Typical usage is direct instantiation by application code that builds a folium Map or by higher-level factory code that aggregates layers before attaching them to a map/figure.
- Parent containers (map/figure) that accept Layer-like objects will read FeatureGroup metadata (tile_name, options, overlay/control/show) when rendering.

Motivation and responsibility boundary:
- FeatureGroup exists so grouping-related metadata and client-side options can be packaged as a Layer-like object without implementing rendering itself. Rendering and DOM insertion remain the responsibility of the parent container or other subclasses that know how to serialize MacroElement/Template content.

## State:
Public / instance attributes initialized by __init__ (types and constraints):

- _template (jinja2.Template)
    - Type: Template
    - Value in this file: an empty Template() object assigned at class level.
    - Role: placeholder/template used by the MacroElement/Element rendering pipeline. In this implementation the template contains no content; subclasses or the rendering pipeline may rely on this attribute's presence.

- _name (str)
    - Type: str
    - Value set by constructor: the literal "FeatureGroup"
    - Invariant: remains the identifier of the class/type for templating or inspection; callers should not rely on it for the layer's display name.

- tile_name (str)
    - Type: str
    - How set: If constructor argument name is not None, tile_name := name; otherwise tile_name := self.get_name()
    - Valid values: any string returned/provided by callers or get_name(); callers should ensure the value is meaningful and unique within a parent container if required.
    - Notes: get_name is inherited (not implemented in Layer in the provided memory); exceptions from get_name propagate to the caller.

- options (dict[str, Any])
    - Type: dict
    - How set: parse_options(**kwargs) is called with remaining keyword arguments; parse_options converts keys from snake_case to camelCase and omits any entries whose value is None.
    - Valid values: mapping from camelCase option names (strings) to arbitrary values; keys with None values are not present.
    - Invariant: options never contains a key whose value is None (parse_options filters those out).

- overlay, control, show (inherited from Layer)
    - Types: bool
    - Values: set by the constructor arguments overlay, control, show (FeatureGroup defaults overlay=True, control=True, show=True).
    - Role: metadata flags consumed by parent containers / UI layer control widgets.

Class invariants:
- tile_name must be present (string) after construction.
- options is a dict (possibly empty) and must not contain None values.
- overlay/control/show are booleans.

## Lifecycle:
Creation:
- Constructor signature:
    FeatureGroup(name=None, overlay=True, control=True, show=True, **kwargs)
- Required args: none
- Typical instantiation:
    - Provide name (string) to force a specific tile_name, OR omit name/pass None to let the instance call self.get_name() to obtain a name.
    - Provide any client-side options as keyword args (these are normalized by parse_options).

Usage:
1. Instantiate FeatureGroup using the constructor above.
2. Read layer metadata:
    - tile_name used by parent containers as the displayed or internal name.
    - overlay/control/show used to decide layer grouping and UI control inclusion.
3. Attach the FeatureGroup instance to a parent container (map/figure) which is responsible for actual rendering/DOM insertion.
4. Optionally inspect or modify options (a normal dict) before or after attachment; note that parent containers may have already serialized the options into templates/JS when attached.

Sequencing constraints:
- If name is None, get_name() is invoked during construction — ensure any required state that get_name() relies upon is available at construction time.
- There is no explicit teardown API on FeatureGroup; parent containers manage removal/cleanup.

Destruction / cleanup:
- No explicit destruction method (no close(), __exit__, or similar). Removal or cleanup of any DOM/state is handled by the parent container or by the rendering pipeline. FeatureGroup holds only in-memory metadata and a Template object.

## Method Map:
flowchart LR
    A[Caller -> FeatureGroup.__init__(name, overlay, control, show, **kwargs)] --> B[super().__init__(name, overlay, control, show)]
    B --> C{name is not None?}
    C -- Yes --> D[tile_name := name]
    C -- No --> E[tile_name := self.get_name() (inherited)]
    D --> F[options := parse_options(**kwargs)]
    E --> F
    F --> G[FeatureGroup instance ready (_name="FeatureGroup", tile_name, options, overlay/control/show)]

## Raises:
Exceptions that may be raised by __init__ (direct or indirect):

- Any exception raised by parse_options (propagated)
    - Typical sources:
        - Errors from camelize when keys are not strings (e.g., AttributeError or TypeError).
    - Trigger: supplying keyword argument names that are not valid strings or otherwise break camelize, or internal errors of camelize.

- Any exception raised by get_name() when name is None (propagated)
    - Trigger: if the inherited get_name() implementation raises, that exception will propagate to FeatureGroup.__init__.

- Exceptions from the Layer superclass __init__ (propagated)
    - Trigger: if Layer.__init__ performs validation that fails (not shown in the provided fragment), those exceptions propagate.

## Example:
- Creating with an explicit name and options:
    - Create: FeatureGroup(name="RoadsLayer", overlay=True, control=True, color='blue', max_zoom=12)
    - Effect:
        - tile_name == "RoadsLayer"
        - overlay == True, control == True
        - options == {'color': 'blue', 'maxZoom': 12}  (snake_case keys converted to camelCase; keys with None would be omitted)

- Creating without explicit name (implicit name resolution):
    - Create: fg = FeatureGroup()
    - Effect:
        - If fg.get_name() returns "FeatureGroup_1", then tile_name == "FeatureGroup_1"
        - options == {} (no kwargs provided)
    - Note: if get_name() raises, construction will fail with whatever exception get_name() raises.

- Typical usage pattern:
    1. fg = FeatureGroup(name="MyGroup", show=False, opacity=0.7)
    2. attach fg to a Map or Figure container that reads fg.tile_name and fg.options and renders the layer group accordingly
    3. no explicit cleanup on fg is required; the container manages lifecycle responsibilities

### `folium.map.FeatureGroup.__init__` · *method*

## Summary:
Initialize the FeatureGroup instance by delegating basic layer initialization to the superclass, setting the internal type identifier, establishing the layer's tile/display name, and normalizing any front-end option keyword arguments into a dictionary stored on the instance.

## Description:
- Known callers and lifecycle stage:
    - Typically constructed directly by application code that builds a folium Map or by higher-level factory/aggregation code that prepares layers before attaching them to a Map or Figure.
    - Parent containers (Map, Figure) construct or receive FeatureGroup instances during the map-building phase and then read the instance metadata (tile_name, options, overlay/control/show) when rendering or building layer control UIs.
- Why this is a separate method:
    - The initializer centralizes three responsibilities that must occur together at object creation time:
        1. Invoke the Layer superclass initialization (to establish common Layer metadata such as overlay/control/show),
        2. Record the concrete element type (_name) for identification/templating, and
        3. Normalize arbitrary keyword options for front-end consumption (parse_options).
    - Keeping this logic inside __init__ ensures these invariants (presence of tile_name, a normalized options dict, and the class identifier) hold immediately after construction and prevents duplication across places that create FeatureGroup objects.

## Args:
    name (str | None): Optional human/internal name for the layer. If provided (not None), it is used verbatim as tile_name. If omitted or None, the instance calls self.get_name() to obtain a name; callers should ensure get_name() is callable and returns a sensible string at construction time.
    overlay (bool): Whether the layer should be treated as an overlay in parent layer controls. Defaults to True.
    control (bool): Whether the layer should appear in layer control widgets. Defaults to True.
    show (bool): Whether the layer should be shown by default in the UI. Defaults to True.
    **kwargs: Arbitrary keyword options intended for front-end (JavaScript/Leaflet) configuration. These are passed to folium.utilities.parse_options which:
        - Converts snake_case keys to camelCase (via camelize),
        - Omits any keys whose value is exactly None,
        - Returns a dict mapping camelCase keys to the given values.

## Returns:
    None. As an initializer, it does not return a value; instead it mutates the new instance so that subsequent reads (tile_name, options, overlay/control/show) reflect the initialized metadata.

## Raises:
    - Any exception raised by Layer.__init__ (propagated). Condition: if the superclass initializer performs validation or other work that fails (e.g., invalid argument types), those exceptions propagate.
    - Any exception raised by self.get_name() when name is None (propagated). Condition: if the inherited get_name() method raises (for example, due to missing state required by get_name), that exception will bubble up.
    - Any exception raised by parse_options (propagated). Conditions include:
        - camelize raising AttributeError/TypeError if non-string keys are provided in kwargs or keys are otherwise invalid for camelize,
        - Unexpected errors inside parse_options or other utilities it calls.
    - No new exceptions are introduced by this __init__; all errors originate from the calls it makes (super().__init__, get_name, parse_options).

## State Changes:
- Attributes READ:
    - self.get_name (method): invoked if name is None to generate tile_name.
- Attributes WRITTEN (directly in this method):
    - self._name: set to the literal string "FeatureGroup".
    - self.tile_name: set to the provided name argument if not None; otherwise set to the result of self.get_name().
    - self.options: set to the dict returned by parse_options(**kwargs) — a mapping of camelCase keys to values with any None-valued entries removed.
- Attributes WRITTEN (indirectly via superclass call):
    - The call to super().__init__(name=name, overlay=overlay, control=control, show=show) may set attributes on self such as overlay, control, show and possibly a name attribute depending on the Layer implementation. Those superclass attributes should be considered initialized by this constructor invocation.

## Constraints:
- Preconditions:
    - If name is None, self.get_name() must be callable and able to return an identifier (commonly a string); otherwise construction will fail with whatever exception get_name raises.
    - kwargs keys are expected to be str-like (snake_case or already camelCase). Non-string keys can cause camelize (invoked inside parse_options) to raise AttributeError/TypeError.
    - Callers should not rely on passing None-valued kwargs to intentionally set options to null in the produced options dict — parse_options will omit keys whose values are exactly None.
- Postconditions:
    - After successful return:
        - self._name == "FeatureGroup".
        - self.tile_name is set (either to the provided name value or the value returned by self.get_name()).
        - self.options is a dict whose keys are camelCase strings and which contains no entries whose value is None.
        - Metadata flags overlay/control/show will reflect values established by the superclass initialization (as passed into this constructor).

## Side Effects:
    - No I/O, network access, or external service calls are performed by this method itself.
    - The method mutates the instance (self) by assigning attributes described above.
    - Any side effects or additional mutations arise only from:
        - Layer.__init__ (called via super()) which may perform further initialization on the instance, and
        - parse_options/camelize, which perform pure in-memory transformations and may raise exceptions for invalid keys.

## `folium.map.LayerControl` · *class*

## Summary:
LayerControl is a MacroElement that collects metadata about child Layer instances attached to a map/figure and organizes them into ordered maps of base layers, overlays, and a set of layers that should be "untoggleable" (tracked in layers_untoggle) prior to template rendering.

## Description:
LayerControl exists to gather and expose which child layers of a parent map/figure are (a) base layers vs overlays, (b) intended to appear in the UI control, and (c) initially visible. It is intended to be attached to a Map/Figure (as a MacroElement child) so that on render it inspects the parent's children, filters those that are instances of Layer and have control==True, and builds three ordered dictionaries used by the layer control template:

- base_layers: OrderedDict mapping Layer.layer_name -> Layer.get_name() for non-overlay layers.
- overlays: OrderedDict mapping Layer.layer_name -> Layer.get_name() for overlay layers.
- layers_untoggle: OrderedDict mapping Layer.layer_name -> Layer.get_name() for layers that should not be toggled on by the control UI (constructed by the rules in render).

Typical callers / instantiation scenarios:
- Create a LayerControl and add it to a Map (or Figure) that already has Layer-like children (tile layers, feature groups, etc.). The map/figure's rendering lifecycle will invoke LayerControl.render(), which populates the dictionaries and then delegates to MacroElement.render() to perform template rendering.

Motivation and responsibility boundary:
- LayerControl's responsibility is metadata collection and organization for the client-side layer toggling control. It does not itself render or manage DOM nodes beyond what the MacroElement/_template provides; the visual behavior is implemented in the template and on the client-side JavaScript that consumes the prepared dictionaries.

## State:
Attributes created by __init__ and their types / invariants:

- _name (str)
    - Type: str
    - Value set to "LayerControl"
    - Invariant: immutable identifier for the element (used by MacroElement machinery).

- _template (jinja2.Template)
    - Type: Template
    - Purpose: Jinja2 template used by MacroElement.render() to emit HTML/JS. In the source it is a Template object; its contents control final output. Implementations should not assume its internals here.

- options (dict[str, Any])
    - Type: dict
    - Source: result of folium.utilities.parse_options(...) called with the constructor parameters.
    - Contents: camelCased keys (parse_options behavior) and values passed through; keys with value None are omitted.
    - Valid values: any value accepted by parse_options (note parse_options may raise if camelize fails for unusual key types).
    - Example keys typically: position, collapsed, autoZIndex in camelCase form (e.g., "position", "collapsed", "autoZIndex").

- base_layers (collections.OrderedDict)
    - Type: OrderedDict[str, str]
    - Meaning: mapping from Layer.layer_name (dict key) to Layer.get_name() (dict value) for base (non-overlay) layers discovered at render time.
    - Invariant: keys are unique by layer_name; values are whatever the Layer.get_name() method returns (expected to be str).

- overlays (collections.OrderedDict)
    - Type: OrderedDict[str, str]
    - Meaning: mapping from Layer.layer_name to Layer.get_name() for layers marked as overlay==True.

- layers_untoggle (collections.OrderedDict)
    - Type: OrderedDict[str, str]
    - Meaning: collection of layers that are considered "untoggleable" by the control logic. Populated during render by:
        * adding base layer keys if more than one base layer exists (the code sets layers_untoggle for a base layer once len(base_layers) > 1), and
        * adding overlay keys for overlays that have show==False.
    - Invariant: subset of keys present in base_layers ∪ overlays after render.

Notes on Layer/parent expectations:
- render() inspects self._parent._children.values(). Therefore, LayerControl expects to be attached to a parent object with a _children mapping whose values are objects that may be instance-checkable against folium.map.Layer and that expose attributes: layer_name (str), overlay (bool), control (bool), show (bool), and a method get_name() returning a str. If these expectations are not met, AttributeError or TypeError may propagate.

## Lifecycle:
Creation:
- Constructor signature: LayerControl(position="topright", collapsed=True, autoZIndex=True, **kwargs)
    - position (str): default "topright". Passed to parse_options; expected to be accepted by client-side template.
    - collapsed (bool): default True. Passed to parse_options.
    - autoZIndex (bool): default True. Passed to parse_options.
    - **kwargs: additional key/value options; keys are passed through parse_options which camelizes keys and removes None values.
- The constructor:
    1. calls super().__init__() (MacroElement initialization).
    2. sets self._name = "LayerControl".
    3. builds self.options = parse_options(...).
    4. initializes base_layers, overlays, layers_untoggle as empty OrderedDicts.

Usage / expected call sequence:
1. Instantiate LayerControl with desired options.
2. Add the LayerControl to a Map or Figure (e.g., map.add_child(layer_control) or map.add_control(layer_control), depending on the hosting API). When added, MacroElement machinery typically sets the element's _parent reference.
3. The map's rendering lifecycle (or an explicit call) will invoke LayerControl.render(**kwargs). render() performs:
    - reset() to clear the three OrderedDicts,
    - iterate through self._parent._children.values(),
    - for each child that is an instance of Layer and has child.control == True:
        * obtain key = child.layer_name
        * if child.overlay is False: add to base_layers; if base_layers length > 1 mark key->name in layers_untoggle
        * else (overlay True): add to overlays; if child.show is False mark key->name in layers_untoggle
    - finally call super().render() to execute MacroElement render behavior (template rendering).
4. After render completes, the three OrderedDicts reflect the parent's layer organization and are used by the template to produce HTML/JS for the layer switcher UI.

Destruction / cleanup:
- LayerControl has no explicit cleanup API. It relies on parent/container removal semantics defined by MacroElement/Map implementations. No files, sockets, or other resources are held by LayerControl.

## Method Map:
graph TD
    A[LayerControl.__init__] --> B[parse_options(position, collapsed, autoZIndex, **kwargs)]
    B --> C[set options dict]
    C --> D[initialize base_layers, overlays, layers_untoggle as OrderedDicts]
    D --> E[add to parent (Map/Figure) via MacroElement/parent API]
    E --> F[LayerControl.render(**kwargs) called during parent's render]
    F --> G[reset() clears OrderedDicts]
    G --> H[iterate self._parent._children.values()]
    H --> I{isinstance(item, Layer) and item.control?}
    I -- yes --> J{item.overlay?}
    J -- False --> K[base_layers[key]=item.get_name(); if len(base_layers)>1 set layers_untoggle[key]=item.get_name()]
    J -- True --> L[overlays[key]=item.get_name(); if not item.show set layers_untoggle[key]=item.get_name()]
    I -- no --> M[skip item]
    K --> N[after iteration -> call super().render()]
    L --> N
    M --> N

Note: super().render() delegates to MacroElement rendering, which uses _template to produce the final HTML/JS.

## Raises:
- During __init__:
    - Any exceptions thrown by parse_options or camelize invoked by parse_options (for example, AttributeError/TypeError if a non-string key is provided in kwargs) will propagate.
    - No other exceptions are explicitly raised by __init__ in the class body.

- During render():
    - AttributeError if self._parent is None or does not have a _children attribute or if child objects do not expose required attributes/methods (layer_name, overlay, control, show, get_name()).
    - TypeError or other exceptions if child.get_name() raises or returns unexpected types; these exceptions propagate.
    - No exceptions are caught inside render(); callers should ensure LayerControl is attached to a compliant parent before render is invoked.

## Example:
Minimal usage pattern (conceptual; concrete map API may vary):

1. Create control:
    - ctrl = LayerControl(position="topleft", collapsed=False)

2. Attach to a map-like parent that contains Layer-like children and that sets _parent on added children:
    - map.add_child(ctrl)  # MacroElement/Map API will set ctrl._parent

3. Render (normally invoked by the map rendering process):
    - ctrl.render()  # populates ctrl.base_layers, ctrl.overlays, ctrl.layers_untoggle, then delegates to MacroElement.render()

4. Inspect results (after render):
    - ctrl.base_layers  # OrderedDict of base layer_name -> name returned by get_name()
    - ctrl.overlays     # OrderedDict of overlay layer_name -> name
    - ctrl.layers_untoggle  # OrderedDict of layers that the control logic marked as untoggleable

Edge usage notes:
- If your parent has no children or no child is a Layer with control==True, the dictionaries remain empty after render.
- If two child Layers share the same layer_name, the latter processed will overwrite the earlier entry in the OrderedDict keys (standard dict behavior).
- Avoid passing non-string keys into LayerControl constructor kwargs; parse_options/camelize expect string-like keys and may raise otherwise.

### `folium.map.LayerControl.__init__` · *method*

## Summary:
Initializes a LayerControl instance by setting its name, normalizing and storing control options, and creating empty ordered registries for base layers, overlays, and untoggleable layers.

## Description:
Known callers and lifecycle:
    - Called when a developer or higher-level API constructs a LayerControl (e.g., LayerControl()) during map setup. 
    - This constructor runs during object instantiation, prior to adding the control to a Map and well before the rendering stage where render() populates layer registries from the parent map.
    - Typical pipeline: user code creates LayerControl -> options are normalized and stored -> control is added to a Map -> render() later inspects map children and fills base_layers/overlays.

Reason this logic is a separate method:
    - Keeps object initialization focused and testable: option normalization and the creation of empty registries are a distinct responsibility that should happen exactly once at creation.
    - Centralizes parse_options usage so callers or future maintainers do not need to duplicate camelCase conversion and None-filtering logic elsewhere.

## Args:
    position (str, optional): Default "topright".
        - Semantics: preferred control placement in the map UI. Common values used by Leaflet: "topleft", "topright", "bottomleft", "bottomright".
        - Passed through to parse_options unchanged; ultimately becomes a camelCase key in self.options (e.g., "position").
    collapsed (bool, optional): Default True.
        - Semantics: whether the control is initially collapsed.
    autoZIndex (bool, optional): Default True.
        - Semantics: whether the control should automatically assign z-indexes to layers.
    **kwargs: Additional keyword options forwarded to parse_options.
        - Behavior: keys are expected to be strings representing option names in snake_case or camelCase; parse_options will convert keys to camelCase and drop any entries whose value is exactly None.
        - Typical use: supply other Leaflet LayerControl options supported by the front-end. Keys that are not strings or that cause camelize to fail will raise errors from camelize/parse_options.

## Returns:
    None
    - The constructor does not return a value; it initializes instance attributes on self.

## Raises:
    - AttributeError or TypeError: may be raised by parse_options (via camelize) if a provided kwargs key is not a string or otherwise incompatible with camelize.
    - Any exception raised by parse_options will propagate out of the constructor (no internal catch). No other exceptions are explicitly raised here.

## State Changes:
    Attributes READ:
        - None of self.<attr> fields are read by this method prior to assignment.
        - The method does call super().__init__(), which may interact with inherited attributes, but this constructor does not directly read any existing self attributes.

    Attributes WRITTEN:
        - self._name (str): set to "LayerControl".
        - self.options (dict[str, Any]): set to the result of parse_options(position=..., collapsed=..., autoZIndex=..., **kwargs). Keys will be camelCase and values exclude any entries whose value was None.
        - self.base_layers (collections.OrderedDict): initialized to an empty OrderedDict intended to hold base-layer registration entries.
        - self.overlays (collections.OrderedDict): initialized to an empty OrderedDict intended to hold overlay-layer registration entries.
        - self.layers_untoggle (collections.OrderedDict): initialized to an empty OrderedDict intended to track layers that should not be toggled on certain conditions.

## Constraints:
    Preconditions:
        - No pre-existing requirements on self attributes (constructor handles initialization).
        - kwargs keys should be strings (recommended) and camelize-compatible to avoid exceptions during option normalization.
        - Callers should not expect any layer registries to be populated immediately after construction; they start empty and are filled later during render().

    Postconditions:
        - After successful return:
            * self._name == "LayerControl"
            * self.options is a dict whose keys are camelCase forms of provided option names and whose values exclude any keys that had value None.
            * self.base_layers, self.overlays, and self.layers_untoggle are empty OrderedDict instances ready to be populated later.
        - If parse_options raises, the constructor will not complete and no guarantee exists about the instance state.

## Side Effects:
    - Calls super().__init__(), which performs any initialization defined by the MacroElement parent (possible registration with internal structures of the parent class). No file I/O, network access, or external service calls occur here.
    - No mutation of global state occurs.
    - Exceptions from parse_options/camelize propagate to the caller; the constructor does not log, warn, or swallow such errors.

### `folium.map.LayerControl.reset` · *method*

## Summary:
Reinitializes the LayerControl's internal layer registries by replacing them with new, empty ordered mappings, returning the object to a clean state with no recorded base layers, overlays, or untoggle layer entries.

## Description:
- Known callers and invocation context:
    - No direct callers are specified in this file. This method is intended to be invoked whenever the LayerControl's recorded layer state must be cleared before re-populating it (for example, during map reinitialization, when programmatically rebuilding the control, or when re-attaching layers after significant changes). The exact call sites depend on the higher-level map-management logic and are not present in the method's source.
- Rationale for a dedicated method:
    - The logic resets multiple related attributes at once; grouping this behavior into a single method keeps higher-level code concise, prevents duplication, and ensures the three registries are always reset consistently.

## Args:
    None.

## Returns:
    None (implicitly returns None). The method's purpose is to mutate object state rather than produce a value.

## Raises:
    None. The implementation does not raise exceptions on its own. (If self is not a valid object or attribute assignment is blocked, Python will raise the usual AttributeError or TypeError.)

## State Changes:
- Attributes READ:
    - None (the method does not inspect existing values; it unconditionally overwrites them).
- Attributes WRITTEN:
    - self.base_layers: set to a new empty OrderedDict()
    - self.overlays: set to a new empty OrderedDict()
    - self.layers_untoggle: set to a new empty OrderedDict()

## Constraints:
- Preconditions:
    - The method must be called on a properly-initialized LayerControl instance (i.e., a Python object with attribute assignment permitted). There are no other preconditions; prior contents of the three attributes are ignored because they are overwritten.
- Postconditions:
    - After the call, self.base_layers, self.overlays, and self.layers_untoggle are all instances of collections.OrderedDict and are empty (len(...) == 0).
    - No other attributes are modified by this method.
    - The method guarantees the object contains fresh, empty registries suitable for subsequent population.

## Side Effects:
- Allocates three new OrderedDict objects and rebinds the three attributes to them.
- No I/O, network calls, logging, or interactions with external services occur.
- Any external references that previously pointed to the old OrderedDict objects will continue to reference those old objects (now orphaned unless held elsewhere); this method does not attempt to clear or mutate the old mappings in-place.

### `folium.map.LayerControl.render` · *method*

## Summary:
Prepare the LayerControl's internal mappings of available base layers, overlays, and layers that should be untoggled, then invoke the standard MacroElement rendering. This modifies the object's layer dictionaries so the template rendering step can generate the correct control UI.

## Description:
- Known callers and context:
    - Invoked during the rendering phase of a parent container (typically a Map or Figure) that iterates over and renders its child elements. In folium's lifecycle this method is called when the parent triggers rendering of its children (the Map/Figure rendering pipeline).
- Why this method exists separately:
    - It isolates the data-preparation step (collecting metadata from child Layer objects and populating base_layers/overlays/layers_untoggle) from the template rendering performed by the MacroElement superclass. This separation keeps template rendering deterministic and allows the LayerControl to compute its state based on the current set of children right before producing its HTML/JS output.

## Args:
- **kwargs: dict
    - Arbitrary keyword arguments forwarded to the superclass render implementation (MacroElement.render). There are no LayerControl-specific kwargs defined in this method; any provided kwargs are passed through.

## Returns:
- None
    - This method does not return a value. Its purpose is to mutate the LayerControl instance state and then call the superclass render logic.

## Raises:
- AttributeError:
    - If self._parent is None or if self._parent does not have a _children attribute (or _children is not a mapping-like object), attempting to access self._parent._children will raise AttributeError.
- Any exception raised by item.get_name():
    - When iterating child items, the code calls item.get_name(); any exception propagated by that call (for example if get_name is not implemented or raises internally) will propagate out of render.
- No explicit exceptions are raised by this method in normal operation; the above are implicit errors due to missing preconditions or errors in child objects.

## State Changes:
- Attributes READ:
    - self._parent (object): read to access its _children collection.
    - self._parent._children (mapping): iterated over to examine each child item.
    - self._parent._children.values() (iterable): each value is inspected.
- Attributes WRITTEN:
    - self.base_layers (collections.OrderedDict[str, str]): reset to empty OrderedDict() then populated with entries for child Layers where control is True and overlay is False. Keys are item.layer_name and values are item.get_name().
    - self.overlays (collections.OrderedDict[str, str]): reset to empty OrderedDict() then populated with entries for child Layers where control is True and overlay is True. Keys are item.layer_name and values are item.get_name().
    - self.layers_untoggle (collections.OrderedDict[str, str]): reset to empty OrderedDict() then populated with:
        - base layer entries when there is more than one base layer (first base layer remains toggled on by default, additional base layers are added here keyed by layer_name -> item.get_name()).
        - overlay entries for which item.show is False (i.e., overlays that are initially hidden).

## Constraints:
- Preconditions:
    - The LayerControl instance must be attached to a parent that exposes a _children mapping (self._parent is not None and has attribute _children). Typically this means the LayerControl has been added to a Map or Figure before render is invoked.
    - Child objects in self._parent._children.values() should either be instances of the Layer type (or subclasses) or any other objects — non-Layer objects are ignored by this method.
    - Child Layer objects are expected to provide attributes: layer_name (str), overlay (bool), control (bool), show (bool) and a method get_name() that returns a display name string.
- Postconditions:
    - After the call:
        - self.base_layers is an OrderedDict mapping base-layer identifiers (layer_name) to the corresponding display names returned by get_name(). If there were no base layers, the mapping is empty.
        - self.overlays is an OrderedDict mapping overlay-layer identifiers (layer_name) to display names. If there were no overlays, the mapping is empty.
        - self.layers_untoggle contains base layers beyond the first base layer and overlays that should start hidden (show == False). It may be empty if no such layers exist.
        - The MacroElement.render implementation has been invoked (super().render()), so subsequent template rendering or parent interaction has been performed as defined by the superclass.

## Side Effects:
- Calls item.get_name() on child Layer objects; those methods may have arbitrary side effects and may raise exceptions which will propagate.
- Calls super().render(), which triggers the MacroElement rendering process — that process typically generates HTML/JS snippets, may attach DOM elements to a parent Figure, and can perform I/O-like operations in-memory (template rendering). Any side effects of MacroElement.render (including modifications to other attributes or to the parent/figure) will occur.
- Mutates the LayerControl's OrderedDict attributes (base_layers, overlays, layers_untoggle). No external I/O is performed directly by this method.

## Complexity:
- Time complexity is O(n) where n is the number of children in self._parent._children, since the method makes a single pass through the parent's children.

## `folium.map.Icon` · *class*

## Summary:
Represents the configuration for a marker's visual icon. Icon gathers appearance parameters (marker color, glyph name, glyph color, CSS prefix and rotation) and normalizes them into a camelCase options dictionary that the MacroElement rendering pipeline will serialize to the front end.

## Description:
Use this class when you need to specify how a marker's icon should look. Icon is a data-holder MacroElement: it does not itself render HTML/JS but prepares self.options for templating/rendering by MacroElement subclasses.

Why this abstraction exists:
- Separates icon-related configuration from marker logic.
- Normalizes Python-style option names (snake_case) into camelCase and removes None values, producing a clean options mapping for the front-end.
- Centralizes the default behavior for icon CSS prefixing and rotation class construction.

Typical callers:
- Higher-level Marker or Feature classes that attach an Icon instance to themselves before rendering.
- Application code that wants access to the normalized options for custom templating or debugging.

## State:
- _template (jinja2.Template)
  - Type: Template
  - Purpose: Template placeholder used by MacroElement rendering (empty in this class).
  - Invariant: Always available as a class attribute; content defined elsewhere in MacroElement pipeline.

- color_options (set[str])
  - Type: set of str
  - Meaning: Approved marker color names used to warn users when they pass an unknown color.
  - Valid values: "red","darkred","lightred","orange","beige","green","darkgreen","lightgreen","blue","darkblue","cadetblue","lightblue","purple","darkpurple","pink","white","gray","lightgray","black"

- _name (str)
  - Type: str
  - Value: "Icon" after __init__
  - Purpose: identifies the element type to the MacroElement machinery.

- options (dict[str, Any])
  - Type: dict with camelCase keys (str) and corresponding values (Any)
  - Construction: result of calling folium.utilities.parse_options with:
      marker_color=color,
      icon_color=icon_color,
      icon=icon,
      prefix=prefix,
      extra_classes=f"fa-rotate-{angle}",
      plus any additional user **kwargs
  - Invariants:
    - No value equals None (parse_options omits None-valued entries).
    - Keys are camelCase (camelize applied inside parse_options).
    - If camelize/parse_options raises, the instance is not created.

Constructor parameters and constraints:
- color (str) — default "blue"
  - Semantics: marker background color name. If not in color_options, a warnings.warn is emitted (no exception).
- icon_color (str) — default "white"
  - Semantics: color for the icon glyph.
- icon (str) — default "info-sign"
  - Semantics: glyph name; interpretation depends on CSS prefix and loaded icon font.
- angle (int | str | Any) — default 0
  - Semantics: used to construct the extra_classes string "fa-rotate-{angle}". Any object convertible to str is acceptable.
- prefix (str) — default "glyphicon"
  - Semantics: CSS class prefix for icon families (e.g., "glyphicon", "fa").
- **kwargs
  - Semantics: additional icon options. Each key is normalized by parse_options (snake_case -> camelCase) and None-valued entries are removed.

Important collision constraint:
- The constructor passes explicit keyword arguments named marker_color, icon_color, icon, prefix, and extra_classes into parse_options and also forwards **kwargs. If the caller supplies any of these same keys as keyword arguments in **kwargs (for example by calling Icon(marker_color='x') ), Python will raise a TypeError at the call to parse_options because the same keyword would be provided twice. Avoid using these exact keys in extra kwargs. Use distinct names for custom keys.

## Lifecycle:
- Creation:
  - Instantiate with Icon(color=..., icon_color=..., icon=..., angle=..., prefix=..., **kwargs).
  - Sequence in __init__:
    1. MacroElement.__init__() is called via super().
    2. self._name is set to "Icon".
    3. If color not in color_options, warnings.warn(...) is invoked with stacklevel=2.
    4. self.options is set via parse_options(...). parse_options converts keys to camelCase and removes None-valued entries.
  - Typical instantiation requires no positional arguments.

- Usage:
  - Inspect or pass self.options to a MacroElement rendering context.
  - No additional API methods are provided on Icon; using code reads options and incorporates them into templates.

- Destruction / cleanup:
  - No explicit cleanup required. Icon does not manage external resources or implement context management.

## Method Map:
flowchart LR
    Start[constructor called] --> Super[call MacroElement.__init__()]
    Super --> SetName[self._name = "Icon"]
    SetName --> ColorCheck{color in color_options?}
    ColorCheck -->|No| Warn[warnings.warn(..., stacklevel=2)]
    ColorCheck -->|Yes| NoWarn[no warning]
    Warn --> ParseCall[call parse_options(marker_color=color, icon_color=icon_color, icon=icon, prefix=prefix, extra_classes=f"fa-rotate-{angle}", **kwargs)]
    NoWarn --> ParseCall
    ParseCall -->|kwargs contains any of marker_color, icon_color, icon, prefix, extra_classes| DupKeyError[Python TypeError: multiple values for keyword argument]
    ParseCall -->|camelize/parse_options raises| CamelizeError[Exception (e.g., AttributeError/TypeError) from camelize]
    ParseCall -->|success| SetOptions[self.options set to returned dict]
    SetOptions --> Ready[Icon instance ready for use]

## Raises:
- warnings.warn is used (does not raise) when color is not in color_options.
- TypeError: can occur during the call to parse_options if the caller passed any keys in **kwargs that duplicate the explicit argument names forwarded to parse_options (marker_color, icon_color, icon, prefix, extra_classes). Example: Icon(marker_color='x') will produce a TypeError.
- Any exception propagated from folium.utilities.parse_options or camelize:
  - AttributeError, TypeError, or other exceptions may arise if non-string keys are provided in kwargs or camelize cannot process a key. These exceptions will propagate out of __init__ and prevent instance creation.

## Example:
- Normal creation:
    icon = Icon(color="red", icon_color="white", icon="star", angle=90, prefix="fa")
    # icon._name == "Icon"
    # icon.options -> {'markerColor': 'red', 'iconColor': 'white', 'icon': 'star', 'prefix': 'fa', 'extraClasses': 'fa-rotate-90'}

- None-valued entries are omitted:
    icon = Icon(color="blue", icon_color=None)
    # icon.options -> {'markerColor': 'blue', 'icon': 'info-sign', 'prefix': 'glyphicon', 'extraClasses': 'fa-rotate-0'}
    # no 'iconColor' key because its value was None

- Dangerous (will raise TypeError) — do not do:
    # This raises TypeError because marker_color is provided twice when calling parse_options internally.
    icon = Icon(color="green", marker_color="yellow")

- Safe pattern for adding custom keys:
    # Use unique names that do not clash with forwarded names:
    icon = Icon(color="green", my_custom_option=123)
    # icon.options will include 'myCustomOption': 123 (camelized) alongside the standard keys

### `folium.map.Icon.__init__` · *method*

## Summary:
Initializes an Icon element by performing superclass initialization, validating the requested marker color, and building a normalized options dictionary (camelCase keys with None values removed) stored on the instance.

## Description:
This constructor is invoked when an Icon instance is created during the setup phase for a marker or other map element that needs an icon configuration. Typical callers include Marker and Feature classes that attach an Icon to themselves before the MacroElement rendering pipeline serializes options to the front end, and application code that constructs Icons directly for custom templating or debugging.

The logic is separate from rendering because Icon is a data-holder MacroElement: the constructor's responsibility is to normalize and validate configuration into a consistent self.options mapping used later by templating and serializers. Keeping this logic in __init__ centralizes defaults, color validation, and the construction of the rotation CSS class so downstream code can rely on a well-formed options dictionary.

## Args:
    color (str, optional):
        - Default: "blue"
        - Semantics: marker background color name. If the provided value is not a member of the class attribute color_options a warning is emitted (does not raise).
        - Valid values (color_options): "red", "darkred", "lightred", "orange", "beige", "green", "darkgreen", "lightgreen", "blue", "darkblue", "cadetblue", "lightblue", "purple", "darkpurple", "pink", "white", "gray", "lightgray", "black"

    icon_color (str, optional):
        - Default: "white"
        - Semantics: color for the icon glyph. If set to None, parse_options will omit the corresponding key from the final options dict.

    icon (str, optional):
        - Default: "info-sign"
        - Semantics: glyph name; interpretation depends on the CSS prefix and available icon fonts.

    angle (any, optional):
        - Default: 0
        - Semantics: used to build the rotation CSS class extraClasses as the string "fa-rotate-{angle}". Any object convertible to str is accepted; its string form is interpolated verbatim.

    prefix (str, optional):
        - Default: "glyphicon"
        - Semantics: CSS class prefix for the icon family (for example "glyphicon" or "fa").

    **kwargs:
        - Any additional keyword options to include in the icon options mapping.
        - Each key is passed to parse_options and therefore is camelized (snake_case -> camelCase) and entries with value exactly None are removed.
        - Important: Do not pass kwargs that use the exact keys forwarded explicitly by the constructor (marker_color, icon_color, icon, prefix, extra_classes). Supplying any of those same keys inside **kwargs will cause a Python TypeError when parse_options is called because the same keyword would be provided twice.

## Returns:
    None (constructor). On successful return the instance has been initialized and ready for use; self.options contains the normalized options dict.

## Raises:
    TypeError:
        - Trigger: If the caller passed any of the explicit forwarded keys inside **kwargs (for example marker_color, icon_color, icon, prefix, or extra_classes), the call to parse_options(marker_color=color, ..., **kwargs) will raise TypeError: multiple values for keyword argument '<key>'.

    Any exception propagated from parse_options or its helper camelize:
        - Examples: AttributeError or TypeError if a non-string key is passed and camelize fails, or other exceptions raised by camelize/parse_options.
        - Behavior: such exceptions propagate out of __init__ and prevent the instance from being created.

    Note: A warnings.warn is emitted (not raised) when color is not in color_options; the constructor continues execution after emitting the warning.

## State Changes:
    Attributes READ:
        - self.color_options: consulted to check whether the provided color is a known/approved value for color (used only to decide whether to warn).

    Attributes WRITTEN:
        - self._name: set to the literal string "Icon".
        - self.options: set to the dict returned by parse_options which contains camelCase keys and excludes any entries whose value was None.

    Other calls with side effects:
        - Calls super().__init__() (MacroElement.__init__), which may perform additional initialization steps on the instance (registration or template-related setup) depending on MacroElement implementation.

## Constraints:
    Preconditions:
        - The class or instance must provide color_options (a set of allowed color names). __init__ expects this attribute to exist and be iterable for membership testing.
        - Prefer passing string keys in **kwargs. Non-string keys may cause camelize in parse_options to raise.
        - Avoid passing keys in **kwargs named marker_color, icon_color, icon, prefix, or extra_classes to prevent duplicate-key TypeError.

    Postconditions:
        - self._name == "Icon".
        - self.options is a dict whose keys are camelCase strings (converted by parse_options/camelize), none of whose values are None, and which contains at least the explicitly forwarded entries unless those values were None (e.g., 'markerColor', 'icon', 'prefix', 'extraClasses' will be present per the inputs unless values were None or parse_options filtered them).
        - If parse_options or camelize raises, the instance may not be created and the postconditions are not established.

## Side Effects:
    - Emits a warnings.warn(...) with stacklevel=2 when the provided color is not in color_options.
    - Calls parse_options(...) which performs in-memory transformations (no I/O) to produce the normalized options dict.
    - Calls the superclass initializer via super().__init__(), which may have side effects defined by MacroElement (e.g., registering the element in a parent Figure or initializing template-related fields). No external I/O or network operations are performed by this constructor itself.

## `folium.map.Marker` · *class*

*No documentation generated.*

### `folium.map.Marker.__init__` · *method*

## Summary:
Initializes a Marker instance by setting its identity, normalizing its geographic location and options, and attaching optional child elements (icon, popup, tooltip), mutating the instance state so the marker is ready to be attached to an element tree and rendered.

## Description:
This constructor is invoked when creating a Marker object (typically by application code or factory functions), during the element-creation stage before any rendering. It performs three responsibilities:
1. Establishes marker identity and base attributes.
2. Normalizes and stores a validated location and the configuration options that control client-side behavior (draggability, auto-pan, etc.).
3. Attaches optional children (icon, popup, tooltip) to the marker so they become part of the element tree used by the rendering pipeline.

Why this is implemented as __init__:
- The logic belongs to object construction because it creates and configures the marker instance invariants required by the rendering lifecycle (e.g., a validated .location, a canonical .options dict, and properly-attached child elements). Keeping it inside __init__ centralizes initialization and avoids repeating validation/attachment logic elsewhere.

Known callers / call contexts:
- Direct user code constructing markers (e.g., Marker(...)).
- Higher-level helper functions or factories that create markers and add them to a Map or Figure.
- Any test or utility that programmatically creates a marker before attaching to a Map/Figure.

## Args:
    location (optional): Any sized, indexable container with two entries (latitude, longitude).
        - Accepted input shapes: list, tuple, numpy.ndarray or pandas.DataFrame (if those modules are available) — any object accepted by validate_location.
        - Behavior: If not None, passed to validate_location(...) which returns a list[float] of length 2; if None, the attribute self.location is set to None.
        - Errors: validate_location may raise TypeError or ValueError for invalid shapes or non-numeric values.

    popup (optional): Popup instance or any object convertible to a string.
        - If a Popup instance is provided, it is attached as a child of the marker.
        - If a non-Popup value is provided, it is coerced via Popup(str(popup)) and the resulting Popup instance is attached.
        - Default: None.

    tooltip (optional): Tooltip instance or any object convertible to a string.
        - If a Tooltip instance is provided, it is attached as a child of the marker.
        - If a non-Tooltip value is provided, it is coerced via Tooltip(str(tooltip)) and the resulting Tooltip instance is attached.
        - Default: None.

    icon (optional): An element-like object intended to represent the marker icon (commonly an Icon instance).
        - If provided, icon is attached as a child of the marker and also assigned to self.icon.
        - The exact accepted type is determined by the element framework's add_child behavior; invalid types may cause add_child or the child's constructor to raise.
        - Default: None.

    draggable (bool): Whether the marker is draggable on the client.
        - Default: False.
        - Note: This value is forwarded into options; parse_options receives draggable=draggable or None and autoPan=draggable or None so a False value results in those keys being omitted (parse_options filters out None).

    **kwargs: Additional keyword options forwarded to parse_options(...) and stored in self.options after normalization.
        - Behavior: kwargs keys are normalized to camelCase by parse_options and any entries whose value is exactly None are omitted.
        - These kwargs typically contain Leaflet option names expressed in Pythonic form (snake_case) and are used to customize front-end behavior.

## Returns:
    None

## Raises:
    - TypeError or ValueError: Any exception propagated from validate_location(location) when location is not None (invalid container shape, not indexable, wrong length, non-numeric or NaN values).
    - AttributeError/TypeError (or other exceptions): Any exception raised by parse_options(...) (for example due to invalid/non-string keys that camelize cannot handle) will propagate.
    - Exceptions from Popup(...) or Tooltip(...) constructors if popup/tooltip coercion is attempted and their initialization fails (these may raise AssertionError, TypeError, or other errors depending on their implementations).
    - Exceptions from add_child(...) if the element framework refuses to attach the supplied child (propagated from the underlying Element/MacroElement add_child implementation).
    - Note: __init__ does not itself raise new, explicit exceptions — it forwards exceptions raised by the helpers it calls.

## State Changes:
Attributes READ:
    - None of the marker's prior self.<attr> fields are read for conditional logic in this constructor (the method only assigns new attributes). It calls super().__init__(), which may read or initialize base-class state.

Attributes WRITTEN:
    - self._name (str): set to "Marker".
    - self.location (list[float] | None): set to the return of validate_location(location) if location is not None; otherwise None.
    - self.options (dict[str, Any]): set to the dict returned by parse_options(draggable=..., autoPan=..., **kwargs). Keys are camelCased and values with None are omitted.
    - self.icon (object) — written only when an icon is provided: assigned to the exact object passed in (after add_child is called).

Other observable mutations (via add_child):
    - When icon is provided: the icon object is attached as a child of this Marker. Observables from the element framework usually include adding the icon to self._children and setting icon._parent = self (these behaviors are provided by the element add_child implementation and are visible in the rendering framework).
    - When popup or tooltip are provided: a Popup or Tooltip instance (either supplied or created by coercion) is attached as a child of this Marker (similarly mutating the element tree and the child's _parent).

## Constraints:
Preconditions:
    - If location is provided, it must satisfy validate_location's expectations: sized, indexable, length 2, and both coordinates convertible to float and not NaN.
    - Keys in **kwargs should be strings or otherwise acceptable to the camelize function used by parse_options; non-string keys or types that break camelize may cause exceptions.
    - popup/tooltip when supplied as non-instance must be coercible to str (because the code calls str(popup) / str(tooltip) before wrapping).
    - The caller should not assume parse_options will preserve None-valued kwargs — None values are intentionally removed.

Postconditions:
    - After return, the Marker instance will have:
        * self._name == "Marker"
        * self.location either a list[float] of length 2 (if a location was provided and validated) or None
        * self.options a camelCased dictionary of option names to values with no entries equal to None
        * self.icon set to the provided icon object if one was provided; icon is also attached as a child
        * Any popup/tooltip present attached as children (and accessible via the element tree), ready for rendering by the Map/Figure pipeline

## Side Effects:
    - Mutation of the Marker object (attributes listed above).
    - Mutation of child objects via self.add_child(child):
        * The attached child will become part of the marker's element subtree (i.e., appear in self._children) and its _parent will be set to this Marker (observable effects depend on the element framework).
    - No I/O (no network or file operations) is performed by this constructor itself.
    - Potential side effects from called functions:
        * validate_location may convert numpy/pandas inputs to lists (allocating memory) but does not mutate the input.
        * parse_options and camelize perform in-memory transformations only.
        * Popup/Tooltip constructors may create Html/Element children and perform additional internal state changes on those objects.

## Implementation notes / edge cases to keep in mind:
    - Passing location=None intentionally yields self.location = None; downstream code that requires a concrete coordinate must handle this.
    - Because parse_options receives draggable=draggable or None, a default False draggable results in None being passed and therefore the 'draggable' and 'autoPan' keys will be omitted from self.options (parse_options filters out None).
    - If popup or tooltip are plain strings or other non-instance objects, they are wrapped using Popup(str(...)) or Tooltip(str(...)) — these coercions may alter escaping/HTML behavior depending on Popup/Tooltip implementations.
    - Errors raised during child attachment or coercion will prevent the Marker instance initialization from completing; callers should construct children first or handle exceptions when constructing a Marker.

### `folium.map.Marker._get_self_bounds` · *method*

## Summary:
Return the marker's bounding pair for map-bound calculations by producing a two-element list whose entries both reference the marker's current location (a zero-area bounds). This is a pure reader method and does not modify object state.

## Description:
This helper exposes a marker's bounds in the uniform child->container interface used when aggregating bounds from heterogeneous children. Because a marker represents a single geographic point, its bounds are represented as [location, location] (start and end of the bounding box are the same). The method is intentionally isolated so container code (for example, map utilities that compute overall bounds or "fit-to-bounds" features) can call a common ._get_self_bounds method on any child element without special-casing point-like children.

Known callers / invocation context:
- No direct callers were present in the available static graph for this repository snapshot. Conceptually, this method is invoked during bounds-aggregation steps performed by parent containers or map-level utilities at render/initialization time (for instance when deriving map bounds from child elements).
- The Marker.render method performs a runtime check that requires a non-None location before a Marker is added directly to a map; _get_self_bounds itself performs no such check.

Why this is a separate method:
- It provides a consistent interface for heterogeneous child elements (polygons, lines, markers) to expose bounds.
- Encapsulating point-specific bounds logic keeps container aggregation code simple and extensible.

## Args:
    None

## Returns:
    list:
        A Python list of exactly two elements: [self.location, self.location].
        - Typical successful case: when self.location is set to the normalized value produced by validate_location, each element is that same list of two floats [lat, lon].
        - If self.location is None (e.g., the marker was constructed without a location and not yet assigned one), the method returns [None, None].
        - The outer list object returned is newly created by the method, but both elements are references to the same object (the current self.location). Therefore, mutating the returned[0] or returned[1] will mutate self.location.

## Raises:
    None (this method does not raise exceptions).
    Note: callers that require numeric bounds should validate that self.location is not None and conforms to the expected two-float shape (Marker.__init__ uses validate_location when a location is supplied).

## State Changes:
    Attributes READ:
        - self.location

    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - No strict preconditions enforced by this method. For meaningful numeric bounds, self.location should be a list of two floats as produced by validate_location (this is the case when a location was supplied at construction).
        - Callers should handle the case where self.location is None.

    Postconditions:
        - The method returns a two-element list whose items are identical (both equal to and the same object as self.location at the time of the call).
        - The method does not modify self or any other object.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of globals or external objects performed by this method itself.
    - The returned structure contains references to a mutable object (self.location); mutations made by the caller to elements of the returned structure will affect self.location.
    
## Example (conceptual):
    - If self.location == [51.5, -0.1], the method returns a new list whose two entries both reference that same list: [[51.5, -0.1], [51.5, -0.1]]. Mutating returned[0][0] will change self.location[0].

### `folium.map.Marker.render` · *method*

## Summary:
Checks that the marker has a location assigned and then participates in the standard element rendering pipeline; does not mutate the marker's attributes itself.

## Description:
This method is invoked as part of the rendering lifecycle for map elements. Typical callers / invocation contexts:
- Map.render() (indirectly) when a Map and its children are being rendered for display.
- Map._to_png() and Map._repr_html_(), which call the root element's render() to produce output (PNG/HTML).
- The rendering traversal performed by the MacroElement/Element rendering machinery (i.e., the superclass render implementation will call this method for child elements).

The method exists separately to centralize a Marker-specific precondition (a marker must have an explicit location when it is added directly to a Map) before delegating to the generic rendering implementation provided by the MacroElement base class. Keeping this check here prevents silent rendering failures for markers without coordinates and keeps the location validation co-located with rendering-time semantics.

## Args:
None.

## Returns:
None. The method does not return a value; its role is to perform validation and participate in rendering side effects via the superclass call.

## Raises:
ValueError: Raised when self.location is None. Exact condition:
    - Trigger: the marker's location attribute is None at the time render() is called (which typically means the marker was created without a location and placed directly on a Map).
    - Message format: "{} location must be assigned when added directly to map.".format(self._name)

## State Changes:
Attributes READ:
    - self.location: checked to ensure a coordinate is present.
    - self._name: read to format the ValueError message when location is missing.

Attributes WRITTEN:
    - None directly by this method. The method performs no assignments to self attributes.

Note: The subsequent call to super().render() delegates to the MacroElement rendering pipeline, which may produce side effects or mutate objects outside this method (see Side Effects). Those mutations are not performed directly by Marker.render itself.

## Constraints:
Preconditions:
    - It's expected that the marker was configured with a valid location (e.g., via the constructor or by setting marker.location to a valid coordinate) before calling render() if the marker is attached directly to a Map.

Postconditions:
    - If no exception is raised, Marker.render will have delegated to the superclass render implementation; the marker will have been processed by the generic rendering pipeline (children and parent interactions handled by MacroElement.render).
    - The marker's own attributes (e.g., location, options) remain unchanged by this method.

## Side Effects:
- Calls super().render() which participates in the global rendering traversal. As a result:
    - Child elements (for example, attached icon, popup, or tooltip objects) will be processed by the rendering pipeline.
    - The rendering process may mutate container objects outside the marker (for example, the parent Figure/Map or header resources) because MacroElement.render is responsible for integrating element output into the overall document/figure. The exact mutations depend on the MacroElement implementation and are not performed directly by Marker.render.
- No direct I/O (file, network) or external service calls are made by Marker.render itself.

## `folium.map.Popup` · *class*

## Summary:
Represents a client-side popup element that wraps HTML content and rendering options for injection into a Figure/Map rendering pipeline.

## Description:
The Popup class packages HTML (either a string or an Element) and a small set of rendering flags/options so the Popup can produce the JavaScript/HTML snippet required to display a Leaflet-style popup in the final rendered document. Typical scenarios:
- Instantiate when you need a reusable popup widget that will be attached to a Map/Figure element and included in the final HTML/JS output.
- The Popup instance is intended to be attached into an element tree whose root is a branca.element.Figure (for example, by adding to a Map or Figure container) before the rendering step. The Figure/Map rendering routine calls render() on elements; Popup.render() appends the popup’s rendered template output into the Figure.script container.

Motivation and responsibility:
- Encapsulates HTML content, escaping behavior, and option normalization (camelCase keys, omission of None values).
- Keeps the popup-specific template rendering and script injection logic in one place so the element tree traversal can remain generic.

Known callers/factories:
- Map or Figure rendering pipeline (the element tree walker that calls render on each element).
- Any code that creates UI elements and adds them to a map/figure prior to serialization to HTML/JS.

## State:
Public and important instance attributes created by __init__ (names, types, defaults, invariants):

- _name: str
    - Value set to "Popup". Identifies the element type/name used by the element framework.

- header: Element
    - An empty Element instance created at construction time.
    - Immediately has its _parent attribute set to this Popup instance.
    - Purpose: reserved container for header content (kept as an Element for consistency with other element-based children).

- html: Element
    - An Element instance used to contain the Popup body content.
    - If the caller passed an Element for the html parameter, that Element is added as a child of this html Element.
    - If the caller passed a str for html, the string is escaped by escape_backticks(...) and wrapped in a branca.element.Html instance (created with script=(not parse_html)) which is then added to this html Element.
    - Invariant: html._parent is set to this Popup instance.

- script: Element
    - An Element instance intended to hold script fragments associated with the popup.
    - script._parent is set to this Popup instance.

- show: bool
    - Set from __init__ parameter show (default False).
    - Semantically indicates whether the popup should open immediately when added/rendered.

- lazy: bool
    - Set from __init__ parameter lazy (default False).
    - Carries a rendering-time directive (the code stores it; actual lazy behavior depends on templates/consumers).

- options: dict[str, Any]
    - Built by calling parse_options(...) with:
        - max_width (default "100%")
        - autoClose set to False if show or sticky else omitted (None values omitted by parse_options)
        - closeOnClick set to False if sticky else omitted
        - any additional kwargs forwarded from the caller
    - Guarantees (by parse_options behavior):
        - Keys are camelCase (camelize applied).
        - Entries whose values are exactly None are omitted.
    - Example resulting keys: maxWidth, autoClose, closeOnClick, and any other camelized kwargs.

Class invariants:
- header, html, and script attributes are Element instances whose _parent attribute references this Popup.
- options contains only camelCased keys and contains no entries with value None.
- _template must be a template-like object with a render(this=..., kwargs=...) method (the class defines _template as a jinja2.Template placeholder).

## Lifecycle:
Creation:
- Signature:
    - html: Optional[Element | str] = None
    - parse_html: bool = False
    - max_width: Union[str, int] = "100%"
    - show: bool = False
    - sticky: bool = False
    - lazy: bool = False
    - **kwargs: additional option key/value pairs to be camelized and filtered
- Behavior:
    - Calls Element.__init__() via super().__init__().
    - Initializes header, html, script Elements and sets their _parent to self.
    - Determines a boolean script := (not parse_html). This value is passed to the Html wrapper when html is a str.
    - If html is an Element: it is added as a child of self.html.
    - If html is a str: escape_backticks(html) is called and the result is wrapped in Html(..., script=script), then added to self.html.
    - Sets the show and lazy flags, and builds options via parse_options(...).
- Required callers must provide only the parameters above; no parameter is strictly required (all have defaults).

Usage / Methods:
- render(**kwargs)
    - Must only be called when the Popup is part of an element tree whose root is a branca.element.Figure; otherwise the method asserts and raises an AssertionError.
    - Typical invocation order in the rendering pipeline:
        1. rendering framework calls render on this Popup (or recursively on its parent)
        2. Popup.render() invokes render(**kwargs) on each child element in self._children
        3. Popup.render() obtains the Figure root via get_root() and asserts it is a Figure
        4. Popup.render() renders the class _template with context this=self and kwargs=kwargs and appends an Element containing that output to figure.script with name=self.get_name()
    - Side effects: mutates the root Figure's script Element by adding a child Element whose content is the rendered template output.

Destruction / cleanup:
- No explicit cleanup methods (no close(), no context manager support). The object relies on Python GC and the element framework lifecycle. Cleanup, if needed, is the responsibility of the container (removing children from the tree).

## Method Map:
flowchart LR
    A[__init__(...)] --> B[create header/html/script Elements and set _parent]
    B --> C[if html is Element -> html.add_child(html_element)]
    B --> D[elif html is str -> escape_backticks -> wrap in Html(script=not parse_html) -> html.add_child(Html)]
    B --> E[set show, lazy, options=parse_options(...)]
    E --> END[Popup is ready to be attached to an element tree]
    END --> F[render(**kwargs)]
    F --> G[for each child in self._children: child.render(**kwargs)]
    G --> H[figure = self.get_root(); assert isinstance(figure, Figure)]
    H --> I[figure.script.add_child(Element(self._template.render(this=self, kwargs=kwargs)), name=self.get_name())]

## Raises:
Exceptions that may be raised by __init__ and render (directly visible from the implementation and documented helper behavior):

- During __init__:
    - Any exception raised by escape_backticks if html is a str is unlikely since html is verified to be a str before calling; escape_backticks itself raises TypeError if given non-str input (the code ensures it's a str).
    - Exceptions raised by Html(...) or Element.add_child(...) may propagate (those constructors/methods belong to branca.element and may raise for invalid inputs).
    - Exceptions from parse_options(...) will propagate. parse_options may raise errors originating from camelize(...) if kwargs contain non-str keys (e.g., TypeError, AttributeError). parse_options semantics also mean invalid option types or keys could cause exceptions downstream if callers validate options later.

- During render(**kwargs):
    - AssertionError if the Popup is not attached to a Figure root. The exact assertion message in code is:
        "You cannot render this Element if it is not in a Figure."
    - Any exception raised by child.render(**kwargs) will propagate.
    - Any exception raised by the template rendering (self._template.render(...)) will propagate.

## Example:
- Create a Popup with a simple HTML string body and a fixed width, then render as part of a Figure/Map rendering lifecycle.

1) Instantiation:
    popup = Popup("Hello <b>world</b>", parse_html=False, max_width=300, show=True)

    Notes:
    - Because parse_html=False, the string is escaped for backticks and wrapped in a Html(...) object with script=True.
    - options will include maxWidth (from max_width) and autoClose=False (because show=True), but will omit closeOnClick unless sticky=True or explicitly provided.

2) Attachment and rendering (high-level):
    - Attach the popup to a map/figure element (e.g., map.add_child(popup) or via whatever element API your project provides).
    - During the map/figure rendering pass, Popup.render(**render_kwargs) will:
        * Call render on its children
        * Verify it is inside a Figure
        * Append the rendered popup template output to figure.script using the popup’s element name

3) Edge cases to consider when using Popup:
    - If you call popup.render() before the popup is attached to a Figure, an AssertionError will be raised.
    - Passing non-string, non-Element values for the html parameter results in no body being added (the constructor only handles Element or str).
    - Invalid kwargs (non-str keys that break camelize) may cause parse_options to raise; pass option names as normal Python identifiers (snake_case) or camelCase strings.

### `folium.map.Popup.__init__` · *method*

## Summary:
Initializes a Popup element by creating and wiring its child Element containers, storing display flags, normalizing rendering options, and inserting provided HTML content (either an Element or an escaped string) into the popup's body.

## Description:
- Known callers and context:
    - User code constructing UI elements (e.g., popup = Popup(...)) before adding the popup to a Map/Figure element tree.
    - Map or Figure factory/attachment helpers that create Popup instances and add them to the element tree.
    - Lifecycle stage: this constructor is invoked when the application creates a popup widget during setup; the instance is later attached to a Map/Figure and rendered during the figure/map rendering pass.
- Why this is a dedicated method:
    - Encapsulates element-creation, parent-child wiring, HTML content handling (including backtick-escaping and optional script extraction), and option normalization in one place so callers need only supply content and options; rendering logic and template emission are kept separate in render().

## Args:
    html (Optional[branca.element.Element or str], default=None)
        - If an Element instance: it will be added as a child of the popup's internal html container.
        - If a str: it will be sanitized with escape_backticks(...) and wrapped in a branca.element.Html object (Html(html, script=(not parse_html))) and then added as a child of the internal html container.
        - Any other type: ignored (no body child is added).
    parse_html (bool, default=False)
        - If True: indicates the provided HTML string should be parsed as HTML (the constructor sets the Html wrapper's script flag to False when parse_html is True).
        - If False: the Html wrapper will be created with script=True (script = not parse_html).
    max_width (Union[str, int], default="100%")
        - Value passed through to parse_options as max_width; typically a pixel integer or a percentage string (e.g., 300 or "100%").
    show (bool, default=False)
        - If True, the popup is flagged to be opened immediately when added/rendered; used to compute options (autoClose is forced False when show is True).
    sticky (bool, default=False)
        - If True, modifies options to make the popup "sticky" (closeOnClick forced False and autoClose forced False when sticky True).
    lazy (bool, default=False)
        - Recorded on the instance and intended as a rendering-time directive; no further behavior is performed by __init__ itself.
    **kwargs
        - Additional option key/value pairs forwarded to parse_options(...).
        - Keys are expected to be Python identifiers (snake_case or camelCase). parse_options will camelCase keys and omit entries whose value is exactly None.
        - If kwargs contain keys that are not valid for camelize(...) (e.g., non-str keys), exceptions from camelize/parse_options may propagate.

## Returns:
    None (constructor). After return, the instance attributes described below are populated and ready to be attached to an element tree.

## Raises:
    - Exceptions raised by Html(...) or Element.add_child(...) if those constructors/operations detect invalid inputs; these exceptions propagate unchanged.
    - Exceptions from parse_options(...):
        * TypeError or AttributeError can propagate when camelize(...) is applied to non-str keys (for example, passing None as a kwarg key).
    - No explicit ValueError or TypeError is raised by this constructor when html is an unexpected non-str/non-Element type; such values are simply ignored for adding body content.

## State Changes:
- Attributes READ:
    - None of this instance's existing self.<attr> fields are read prior to assignment in this method.
- Attributes WRITTEN:
    - self._name (set to "Popup")
    - self.header (new Element() instance)
    - self.html (new Element() instance)
    - self.script (new Element() instance)
    - self.header._parent (set to self)
    - self.html._parent (set to self)
    - self.script._parent (set to self)
    - self.show (set from argument)
    - self.lazy (set from argument)
    - self.options (set to the dict returned by parse_options(...))

## Constraints:
- Preconditions:
    - No precondition on self (this is the object's constructor).
    - If html is provided as a str, it must be a Python str (the code checks isinstance(html, str) before calling escape_backticks). If callers pass non-str-like objects and expect implicit coercion, they should call str(...) before passing.
    - Keys passed in **kwargs should be strings (normal Python identifiers). Non-string keys may cause camelize/parse_options to raise.
- Postconditions:
    - header, html, and script exist and have their _parent attribute referencing this Popup.
    - If html was an Element, it is now a child of self.html.
    - If html was a str, an Html wrapper containing the escaped string has been added as a child of self.html with its script flag set to (not parse_html).
    - self.show and self.lazy reflect the constructor arguments.
    - self.options is a dict whose keys are camelCased (via parse_options) and which contains no entries with value exactly None. autoClose is present and set to False if show or sticky is True; closeOnClick is present and set to False if sticky is True.

## Side Effects:
    - Mutates newly-created child Elements (self.header, self.html, self.script) by setting their _parent attributes to reference this Popup.
    - If an Element instance is provided as the html argument, that Element is added as a child of self.html (mutating both the provided Element's parent pointers/relations and self.html's children list via Element.add_child).
    - Calls escape_backticks(...) (pure function, no I/O) when wrapping a string html.
    - Calls parse_options(...) (pure transformation) which may call camelize(...); these are in-memory operations and do not perform I/O.
    - No network I/O, file I/O, or external service calls occur directly in this constructor.

## Implementation notes and edge cases:
    - script = not parse_html controls whether the Html wrapper is created with script=True (when parse_html is False) so that by default script fragments are preserved/separated unless the caller explicitly requests parse_html.
    - If html is None or an unsupported type, no content child is added and the popup body remains an empty Element instance (self.html).
    - Because parse_options omits keys with value None, autoClose or closeOnClick will be absent from self.options unless they are forced to False by the show/sticky logic or explicitly provided in kwargs with a non-None value.
    - Any exceptions stemming from invalid kwargs keys or from the Element/Html constructors will propagate to the caller; callers should validate or sanitize keys/values before instantiation if they need to guarantee no exceptions.

### `folium.map.Popup.render` · *method*

## Summary:
Renders this Popup into the map rendering pipeline: recursively renders child elements, ensures the Popup is attached to a Figure, and injects the Popup's rendered template output into the Figure's script container.

## Description:
This method is part of the element rendering pipeline used when a map (or its root Figure) is converted into HTML/JS for display. Typical callers and contexts:
- The Figure or Map rendering routine that walks the element tree to produce the final output. In that lifecycle stage, each element's render method is called so it can append its own JavaScript/HTML to the Figure.
- Parent container elements that iterate over their children and call child.render(**kwargs). This method itself also recursively calls render on its children.

Why this is a separate method:
- Rendering an element requires a sequence of steps (render children, confirm root, render template, and register script output). Encapsulating these steps in a single method keeps the element API consistent (all elements implement render) and allows uniform traversal and injection into the root Figure's script area without duplicating logic.

## Args:
    **kwargs: dict
        Arbitrary rendering-time keyword arguments forwarded to:
        - child.render(**kwargs) for each child element, and
        - the template render call as the "kwargs" variable in the template context.
        No specific keys are required by this method; contents are passed through to children and the template.

## Returns:
    None
    The method has no return value; its effect is to mutate the Figure's script element and to call child renderers.

## Raises:
    AssertionError:
        If the element is not attached to a Figure as its root. Trigger condition:
        - self.get_root() does not return an instance of branca.element.Figure.
        The exact message is: "You cannot render this Element if it is not in a Figure."
    Any exception raised by child.render(**kwargs) will propagate.
    Any exception raised during template rendering (self._template.render(...)) will propagate.

## State Changes:
    Attributes READ:
        self._children
            - Iterated over; each child is asked to render.
        self._template
            - Used to produce the string inserted into the Figure's script.
        (via method calls) self.get_root()
            - Read to obtain the Figure root for script injection.
        (via method calls) self.get_name()
            - Read to provide a name when adding the rendered Element to the Figure.script container.

    Attributes WRITTEN:
        None on self: this method does not modify attributes on self.

    External object mutations (see Side Effects):
        - The Figure's script element is modified by calling add_child(..., name=...), adding a new Element containing the rendered template output.

## Constraints:
    Preconditions:
        - self._template must be a templating object with a render(this=..., kwargs=...) method (e.g., a jinja2.Template or compatible object).
        - self._children must be a mapping of child elements where each child implements render(**kwargs).
        - The element must already be attached into a document tree whose root is a branca.element.Figure (i.e., get_root() must return a Figure instance).

    Postconditions:
        - All children in self._children have had their render(**kwargs) called (in iteration order).
        - The Figure root's script container has been appended with a new Element containing the rendered template output for this Popup, registered using this.get_name() as the child name.

## Side Effects:
    - Mutates the root Figure's script container by adding an Element child. This is the primary effect that causes the Popup's JavaScript/HTML to be included in the final rendered output.
    - Calls child.render(**kwargs) for each child, which may have further side effects (mutating other parts of the Figure/tree, raising exceptions, etc.).
    - Runs template rendering (string generation) via self._template.render(...). This is a CPU-bound operation and could raise template exceptions; it does not perform I/O itself unless the template rendering hooks or child renders do so.

## `folium.map.Tooltip` · *class*

## Summary:
A lightweight MacroElement that encapsulates tooltip text, optional inline style, and a validated set of display options suitable for attachment to map layers (e.g., Marker or GeoJson features).

## Description:
Tooltip holds the data necessary for the rendering pipeline (branca/MacroElement templates) to produce a Leaflet-style tooltip on the map. It does not itself render DOM or perform I/O — it only stores text, style, and an options dictionary which the template uses when generating JavaScript/HTML.

Use cases:
- Attach small explanatory text to a Marker, CircleMarker, Polygon, or other layer that supports MacroElement children.
- Provide configuration such as tooltip direction, offset, permanence, interactivity, and opacity.

Known callers / factories:
- Typically instantiated directly by application code and then attached using parent.add_child(tooltip) or passed into higher-level helper functions that create and attach tooltips.
- The folium rendering pipeline (MacroElement/Element/Map) reads Tooltip attributes during final rendering.

Responsibility boundary:
- Validate option names and types.
- Coerce text to string.
- Hold an optional inline style string.
- Does not perform rendering or lifecycle management beyond being a child element.

## State:
Class attributes
- _template (jinja2.Template)
  - Type: jinja2.Template
  - Value in source: an empty Template() instance.
  - Note: Template content for rendering is provided by the broader MacroElement/template system; Tooltip itself does not embed template text here.

- valid_options (dict[str, tuple[type, ...]])
  - Purpose: whitelist of allowed option keys (camelCase) mapped to tuples of accepted Python types.
  - Keys and types:
    - "pane": (str,)
    - "offset": (tuple,)
    - "direction": (str,)
    - "permanent": (bool,)
    - "sticky": (bool,)
    - "interactive": (bool,)
    - "opacity": (float, int)
    - "attribution": (str,)
    - "className": (str,)

Instance attributes (established during __init__)
- _name (str)
  - Value: "Tooltip" — used by MacroElement for identification.

- text (str)
  - Type: str
  - How set: coerced via str(text) in __init__.
  - Constraint: must be convertible to str; Tooltip will not validate HTML or length.

- options (dict[str, Any])
  - Type: dict mapping camelCase option names to validated values
  - How produced: result of parse_options(kwargs) called by __init__ after injecting sticky.
  - Constraint: every key in options must be present in valid_options and each value must be an instance of one of the allowed types for that key.
  - Invariant: after __init__, options always contains a "sticky" key (because __init__ injects sticky into kwargs).

- style (str) — optional
  - Type: str (only present if caller supplies a non-falsy style argument)
  - Constraint: __init__ asserts that style is a str when provided. The class does not validate CSS correctness; that is the caller's responsibility.

Notes on camelize and keys:
- The camelize() utility accepts arbitrary strings (it does not itself enforce membership in valid_options and will happily convert strings containing underscores, leading/trailing underscores, or even empty strings). Tooltip.parse_options will enforce that the camelized key exists in valid_options and that the corresponding value is of an allowed type.

## Lifecycle:
Creation
- Signature: Tooltip(text, style=None, sticky=True, **kwargs)
  - text (required): any object convertible to str; stored as str(text).
  - style (optional): inline CSS string; if provided must be a str or an AssertionError is raised.
  - sticky (optional, default True): boolean indicating whether the tooltip should stick to the cursor — this parameter is injected into kwargs and will override any sticky setting present in kwargs.
  - **kwargs: additional option names corresponding to valid_options keys (can be provided in snake_case; they will be camelized internally).

Initialization behavior (step-by-step)
1. Calls MacroElement.__init__() via super().__init__().
2. Sets self._name = "Tooltip".
3. Coerces and sets self.text = str(text).
4. Injects the sticky argument into kwargs (kwargs.update({"sticky": sticky})), therefore ensuring sticky passed positionally or by name will take precedence over any 'sticky' provided in kwargs.
5. Calls self.parse_options(kwargs):
   - camelize is applied to keys (so keys provided in snake_case are converted to camelCase).
   - Each camelized key is checked for membership in valid_options.
   - Each corresponding value is checked to be an instance of one of the types declared in valid_options for that key.
   - Returns a dict with camelCase keys mapped to validated values. That dict is stored in self.options.
6. If a truthy style is provided, asserts style is str and then sets self.style = style.

Usage
- Typical flow:
  1. Instantiate Tooltip.
  2. Attach to a parent MacroElement (e.g., marker.add_child(tooltip)).
  3. Let the Map / Figure / MacroElement rendering pipeline read tooltip._template, tooltip.text, tooltip.style, and tooltip.options when generating output.
- There are no public methods beyond those inherited from MacroElement; to change tooltip content/options after creation you must mutate attributes directly or create a new Tooltip instance.

Destruction / cleanup
- Tooltip provides no explicit cleanup methods or context-manager protocol. The hosting Map/Element lifecycle controls ultimate disposal.

## Method Map:
graph LR
    __init__ --> camelize[camelize keys]
    camelize --> parse_options[parse_options: validate keys & types]
    parse_options --> set_options[self.options = validated_dict]
    __init__ --> set_text[self.text = str(text)]
    __init__ --> set_name[self._name = "Tooltip"]
    __init__ --> set_style[if style: assert str and set self.style]

## parse_options (behavior summary)
- Input: kwargs (dict[str, Any]) — arbitrary keys; keys are camelized within the method.
- Output: dict[str, Any] with camelCase keys only, each key present in valid_options and each value an instance of a permitted type.
- Errors:
  - If a camelized key is not in valid_options, raises AssertionError with message: "The option {key} is not in the available options: {list(valid_options)}."
  - If a value's type does not match the allowed types for that key, raises AssertionError with message: "The option {key} must be one of the following types: {valid_options[key]}."

## Raises:
- AssertionError from __init__ when:
  - style is provided and is not a str:
    - Message: "Pass a valid inline HTML style property string to style."
- AssertionError from parse_options when:
  - A camelized option key is not present in valid_options:
    - Message: "The option {key} is not in the available options: {list(valid_options)}."
  - An option value fails the isinstance check against valid_options[key]:
    - Message: "The option {key} must be one of the following types: {valid_options[key]}."
- Note: str(text) conversion may raise if the object's __str__ raises; this is not handled by Tooltip.

## Example:
# Create a tooltip that does not follow the cursor, appears above the target, and has a small white background
tooltip = Tooltip(
    "Point of interest",
    style="background-color:white;padding:4px;border-radius:3px;",
    sticky=False,
    direction="top",
    offset=(0, -10),
    opacity=0.85,
)

# Attach to a marker-like parent that supports MacroElement children:
# marker.add_child(tooltip)

# After attachment, the rendering pipeline will read tooltip.text, tooltip.style, and tooltip.options.

### `folium.map.Tooltip.__init__` · *method*

## Summary:
Initializes the Tooltip instance by setting its element name, recording the tooltip text (coerced to a string), constructing and storing parsed options (including the sticky flag), and optionally validating and storing an inline style string.

## Description:
This constructor runs during object creation (when Tooltip(...) is called). It centralizes Tooltip-specific setup: identity (_name), normalization of the provided text, composition of options from keyword arguments plus the sticky flag, and validation of an optional style string.

Known callers and context:
- Invoked whenever a Tooltip is instantiated by user code or other library components while building or attaching tooltip elements to map layers. It is executed at construction time as part of the object's lifecycle.
- This logic is kept in __init__ because it performs construction-time normalization and validation required before the Tooltip is used (setting defaults, coercing types, validating style, and building the options structure).

## Args:
    text (any): Required. The tooltip content. The value is coerced via str(text) and stored as self.text (so None becomes "None", numbers are converted to their string form, etc.).
    style (str | None, optional): Inline HTML style string (for example, "color: red; font-weight: bold;"). Defaults to None. If the argument is falsy (None, empty string, False, 0), no style attribute is created. If the argument is truthy, it must be an instance of str or an AssertionError is raised.
    sticky (bool, optional): Whether the tooltip should be "sticky". Defaults to True. This value is inserted into the keyword arguments under the key "sticky" before option parsing.
    **kwargs: Additional option key/value pairs forwarded to self.parse_options after merging with {"sticky": sticky}.

## Returns:
    None: This is an initializer; it does not return a value.

## Raises:
    AssertionError: Raised when a truthy style value is provided that is not an instance of str. The assertion message is:
        "Pass a valid inline HTML style property string to style."
    Note: Exceptions raised by super().__init__() or by self.parse_options(...) may also propagate; those are not introduced by this constructor's own code.

## State Changes:
    Attributes READ:
        None. The constructor does not read existing instance attributes.
    Methods CALLED:
        self.parse_options(kwargs_with_sticky): Called to produce the options structure that is stored on the instance.
        super().__init__(): Called to allow parent-class initialization.
    Attributes WRITTEN:
        self._name (str): Set to "Tooltip".
        self.text (str): Set to the result of str(text).
        self.options (any): Set to the value returned by self.parse_options after merging kwargs with {"sticky": sticky}.
        self.style (str): Conditionally set if a truthy style was provided and passes the str type assertion.

## Constraints:
    Preconditions:
        - No type requirement on text (it will be coerced to str).
        - If a style attribute is desired, the caller must provide a truthy str; otherwise the attribute will not be created.
    Postconditions:
        - self._name == "Tooltip".
        - self.text contains the string representation of the input text.
        - self.options equals the return value of self.parse_options called with kwargs updated to include {"sticky": sticky}.
        - If a truthy str was provided for style, self.style is set to that string; otherwise self.style is not set by this constructor.

## Side Effects:
    - Calls super().__init__(), which may run parent-class initialization logic (the constructor itself performs no I/O).
    - Calls self.parse_options(...); any side effects from that method depend on its implementation (this constructor only forwards the merged kwargs and stores its return value).
    - No network, filesystem, or other external I/O is performed directly by this constructor.

### `folium.map.Tooltip.parse_options` · *method*

## Summary:
Normalize and validate a mapping of tooltip option names and values, returning a camelCased options dict suitable for assignment to the instance (e.g., self.options).

## Description:
This method is invoked during Tooltip construction to canonicalize and validate user-provided options before they are stored on the instance. Known callers:
- Tooltip.__init__: called immediately after building the kwargs passed to the constructor; its return value is assigned to self.options.

Purpose and rationale:
- Centralizes option normalization (camelCasing) and type validation so the __init__ remains focused on high-level initialization.
- Keeps validation logic in one place to allow reuse or direct testing without re-running the full constructor.

## Args:
    kwargs (dict): A mapping of option names (strings) to values. Keys may be in any case/style; they will be converted to camelCase via folium.utilities.camelize. Typical keys are those listed in Tooltip.valid_options (see class definition): "pane", "offset", "direction", "permanent", "sticky", "interactive", "opacity", "attribution", "className". Values must be instances of the types associated with each option in Tooltip.valid_options (for example, "opacity" must be float or int, "sticky" must be bool).

## Returns:
    dict: A new dictionary mapping camelCased option names to their validated values. The returned dict:
    - Contains only keys present (after camelizing) in self.valid_options.
    - Preserves the values provided (no coercion), assuming they pass isinstance checks.
    - Will be empty if input kwargs is empty.

## Raises:
    AssertionError: If any key (after camelizing) is not one of the keys in self.valid_options.
        - Message format: "The option {key} is not in the available options: {comma-separated-valid-options}."
    AssertionError: If any value is not an instance of the type(s) declared for that option in self.valid_options.
        - Message format: "The option {key} must be one of the following types: {type-tuple}."
    AttributeError / TypeError: If kwargs does not support .items() (i.e., it is not a mapping), iteration will fail. (This is a consequence of the implementation using kwargs.items().)

## State Changes:
    Attributes READ:
        - self.valid_options: used to determine allowed option names and their expected types.
    Attributes WRITTEN:
        - None. The method does not mutate self. (The caller commonly assigns the returned dict to self.options.)

## Constraints:
    Preconditions:
        - kwargs must be a mapping (supporting .items()) whose keys are strings (or convertible to strings) and values match the expected types for options after camelization.
    Postconditions:
        - Every key in the returned dict is present in self.valid_options.
        - Every returned value is an instance of the type(s) declared for that option.
        - Keys in the returned dict are camelCased forms of the original keys.

## Side Effects:
    - No I/O or external service calls.
    - Does not mutate objects outside of its local scope and does not modify self.
    - Calls folium.utilities.camelize to transform key names (pure function call, no side effects).

## `folium.map.FitBounds` · *class*

## Summary:
Represents a folium/Leaflet "fit bounds" macro element that stores a bounding box and normalized display options so the map frontend can zoom and pan to fit the provided bounds.

## Description:
FitBounds is a thin MacroElement subclass whose sole responsibility is to hold a bounds value and an options mapping that will be serialized into the map's frontend template. It is intended to be created when code needs to instruct the Leaflet map to fit its viewport to a particular geographic bounding box with optional padding and maximum zoom constraints.

Typical callers / usage contexts:
- Created by higher-level code that wants to add a "fit bounds" instruction to a map (for example, when centering or zooming a map to show all markers).
- Added to a Map or Layer via the usual MacroElement integration (e.g., map.add_child(FitBounds(...))). Note: MacroElement integration and rendering are the responsibility of the MacroElement base class and the surrounding folium rendering pipeline; FitBounds only stores data used by that pipeline.

Motivation:
- Encapsulates the two concerns required to issue a fit-bounds instruction to the frontend: the geometry describing the area to fit (bounds) and the UI/behavior options controlling padding and maximum zoom.
- Keeps option normalization consistent by reusing the shared parse_options helper so the keys are camelCased and None-valued options are omitted before rendering.

Responsibility boundary:
- Stores bounds and options; does not validate or coerce bounds into a canonical geographic type.
- Delegates option normalization (snake_case → camelCase, omission of None values) to folium.utilities.parse_options.
- Rendering and injection of the resulting data into JavaScript is handled by MacroElement and templating; FitBounds does not perform rendering itself.

## State:
Attributes set by this class (public surface visible after instantiation):

- _name (str)
    - Value: "FitBounds"
    - Invariant: constant string identifying the element; set in __init__.

- bounds (any)
    - Type: any Python object (stored as provided).
    - Expected/Recommended format: an iterable that defines a bounding box understood by Leaflet — typically a pair of coordinate pairs such as [[southWest_lat, southWest_lng], [northEast_lat, northEast_lng]] or an iterable of LatLng-like pairs. This class does not enforce shape or numeric conversion; callers should supply a valid bounds structure accepted by the frontend.
    - Invariant: stored value equals the value passed to __init__ (no internal normalization performed).

- options (dict[str, Any])
    - Type: dict
    - Construction: produced by calling folium.utilities.parse_options with the keyword arguments supplied to __init__ (padding_top_left, padding_bottom_right, padding, max_zoom).
    - Keys: camelCased versions of the kwargs names (for example, max_zoom -> maxZoom, padding_top_left -> paddingTopLeft, padding_bottom_right -> paddingBottomRight). Keys whose provided values were None are omitted.
    - Typical key/value expectations (not enforced by this class; these are conventional types used by Leaflet):
        - maxZoom (int)
        - paddingTopLeft (pair of ints or floats, e.g., [x, y])
        - paddingBottomRight (pair of ints or floats)
        - padding (pair of ints or floats or single numeric)
    - Invariant: contains only entries with non-None values; keys are camelCased strings.

- _template (jinja2.Template)
    - Type: Template
    - Purpose: Jinja2 template object used by MacroElement-based rendering. In this source the template is present as an attribute (empty in the provided source), and the rendering pipeline will use it when serializing to the final HTML/JS.

Class invariants:
- After construction, _name, bounds, and options must be present on the instance.
- options must be a dict with camelCased keys and no None values (this is guaranteed by parse_options for provided kwarg names).

## Lifecycle:
Creation:
- To instantiate, call:
    FitBounds(bounds, padding_top_left=None, padding_bottom_right=None, padding=None, max_zoom=None)
- Required positional argument:
    - bounds: any Python object (recommended: a two-element sequence of coordinate pairs as described above).
- Optional keyword arguments (defaults shown):
    - padding_top_left: default None
    - padding_bottom_right: default None
    - padding: default None
    - max_zoom: default None

What happens during __init__:
1. The MacroElement base class __init__ is invoked (super().__init__()).
2. _name is set to "FitBounds".
3. bounds is stored unchanged on the instance.
4. parse_options is called with the provided padding and max_zoom kwargs; the returned dict is stored on self.options. parse_options converts option names to camelCase and omits keys whose values are None.

Usage:
- Typical sequence:
    1. Create FitBounds instance with desired bounds and options.
    2. Add the instance to a Map or Figure using the MacroElement integration (e.g., map.add_child(fit_bounds_instance)).
    3. The folium rendering pipeline will render _template using instance state; that template typically serializes bounds and options into JavaScript to invoke Leaflet's fitBounds on the client side.

Destruction / cleanup:
- FitBounds does not allocate external resources and does not require explicit cleanup. It has no context-manager protocol, close() method, or special destruction behavior.

Method usage order:
- Only __init__ is defined on this class. After instantiation the consumer reads attributes and passes the object into the folium rendering pipeline; there are no further FitBounds-specific method calls.

## Method Map:
flowchart LR
    A[Instantiate FitBounds] --> B[MacroElement.__init__()]
    B --> C[set _name = "FitBounds"]
    C --> D[store bounds as-is on self.bounds]
    D --> E[call parse_options(padding_top_left=..., padding_bottom_right=..., padding=..., max_zoom=...)]
    E --> F[store returned dict on self.options]
    F --> G[Instance ready to be added to Map / rendering pipeline]

(Note: the only call dependency inside FitBounds is parse_options; rendering-time calls come from the MacroElement/template pipeline.)

## Raises:
- __init__ does not explicitly raise exceptions in this class's source.
- Exceptions that may propagate from called utilities:
    - Exceptions raised by parse_options (or the camelize call it uses) will propagate if they occur. In the normal usage shown in this class (passing the documented kwarg names), parse_options should not raise; unexpected internal errors or unusual inputs could surface exceptions from camelize (e.g., if non-string keys were passed to parse_options, which does not occur here) or other runtime errors in parse_options.
- No bounds validation is performed here; callers may receive rendering or frontend errors later if bounds is malformed.

## Example:
- Typical creation and usage pattern (conceptual; integration with Map handled by MacroElement/folium render pipeline):
    1) Construct with a bounding box and optional padding/max zoom:
       fit = FitBounds(bounds=[[51.5, -0.12], [51.6, -0.02]], padding=[10, 20], max_zoom=12)
    2) Add to a Map (pseudo-usage; Map.add_child is part of the broader folium API):
       my_map.add_child(fit)
    3) When the map is rendered, the FitBounds instance's options dict will contain camelCased keys (for example, {'padding': [10, 20], 'maxZoom': 12}) and the bounds value will be serialized into the template and used on the client to call Leaflet.fitBounds.

Notes and recommendations for reimplementation:
- Keep the class lightweight: simply store the supplied bounds and normalize the option kwargs with parse_options so the rest of the folium rendering pipeline can serialize them.
- Do not perform bounds coercion in this class; if callers require validated numeric coordinates, validate them before constructing FitBounds (for example, by using a validate_location-like helper).
- Ensure parse_options behavior (camelCasing and omission of None values) is preserved when reproducing options normalization.

### `folium.map.FitBounds.__init__` · *method*

## Summary:
Initializes a FitBounds element by recording the provided bounds and normalizing optional display options; sets up the MacroElement base state.

## Description:
This constructor is called when a FitBounds element is created (typically by user code that wants the map to fit to a bounding box). It performs two responsibilities:
- Calls the MacroElement base constructor to perform standard element initialization.
- Stores the provided bounds on the instance and constructs an options dictionary from the optional parameters by delegating normalization to parse_options.

Known callers:
- No direct callers were discovered in the inspected module. In typical usage this class is instantiated directly by client code or higher-level helpers that add fit-bounds behavior to a map.

Why this is a separate method:
- Encapsulates element initialization and option normalization in one place so that creation of a FitBounds object always produces a consistently named element (self._name), a stored bounds payload, and a normalized options dict ready for serialization to the frontend.

## Args:
    bounds (Any):
        Required. The bounds payload provided by the caller. This constructor does not validate, normalize, or transform bounds; it stores the value exactly as provided on self.bounds.
    padding_top_left (Any, optional):
        Optional. If supplied (not None), passed through to parse_options and included in self.options (after key normalization). If None, it is omitted from self.options.
    padding_bottom_right (Any, optional):
        Optional. Same semantics as padding_top_left.
    padding (Any, optional):
        Optional. Same semantics as padding_top_left.
    max_zoom (Any, optional):
        Optional. If supplied (not None), included in self.options after normalization.

Notes on option processing:
- The options arguments are forwarded into folium.utilities.parse_options, which:
    * Converts option key names from snake_case to camelCase.
    * Removes any options whose value is exactly None.
    * Returns a dict mapping camelCase option keys to their original values.

## Returns:
    None
    - This is an initializer; no value is returned.

## Raises:
    - This method does not raise explicitly. Any exception raised by parse_options (for example, propagated exceptions from the camelize step if unusual non-string inputs were provided for option keys) or by MacroElement.__init__ will propagate to the caller.

## State Changes:
Attributes READ:
    - None of the instance attributes are read before being set in this method (only class/parent initializers are invoked).

Attributes WRITTEN:
    - self._name: set to the literal string "FitBounds".
    - self.bounds: assigned to the provided bounds argument (no validation or mutation).
    - self.options: assigned to the dict returned by parse_options(...) containing camelCased option keys and excluding entries with value None.

Additionally, the method calls:
    - MacroElement.__init__ via super().__init__(), which may modify base-class state (not inspected here).
    - folium.utilities.parse_options(...), which returns the normalized options dict.

## Constraints:
Preconditions:
    - The caller should provide a meaningful bounds object; this constructor does not enforce types or structure.
    - Option arguments should be passed as standard Python keyword values. The keys used here are fixed strings from the signature, so callers cannot pass unexpected key names through this constructor; parse_options will operate on these known keys.

Postconditions:
    - After return, self._name == "FitBounds".
    - self.bounds is identical to the passed bounds argument (no transformation was applied).
    - self.options is a dict containing only the options whose values were not None, with keys converted to camelCase by parse_options.

## Side Effects:
    - Invokes MacroElement.__init__ (base-class initialization).
    - Invokes parse_options, a pure function that performs in-memory normalization and may raise exceptions if internal helpers (e.g., camelize) encounter unexpected types. No I/O, network access, or global state mutation occurs here.

## `folium.map.CustomPane` · *class*

## Summary:
Represents a named Leaflet "pane" as a MacroElement: a small configuration container that records the pane's name, its CSS z-index, and whether the pane accepts pointer events.

## Description:
CustomPane is a lightweight MacroElement subclass whose sole responsibility is to carry three pane configuration values (name, z_index, pointer_events) that are intended to be used by the map rendering/templates to create a corresponding Leaflet pane in the generated map HTML/JS.

Typical usage:
- Instantiate a CustomPane when you need a named pane with a specific stacking order (z-index) or to control whether the pane should receive pointer events.
- After creation the instance is intended to be attached to the map/parent element (for example, via the parent's add_child method) so that the map's rendering pipeline can consume the pane configuration and render the actual pane in the page.

Motivation:
- Encapsulates pane metadata separately from layers so multiple layers can reference a shared pane name and consistent z-index/pointer behavior.
- Keeps the pane configuration as a MacroElement so it participates in the folium element tree (inheritance) and can be rendered/serialized with other page elements.

## State:
Attributes (visible in the instance after initialization):

- _name: str
  - Value set to the literal "Pane".
  - Invariant: remains the class's internal type identifier for this element (code sets it unconditionally).

- name: str
  - Description: logical pane identifier used by templates/renderers to create or reference a Leaflet pane.
  - Constraints: no validation is performed in this class; callers should pass a non-empty string appropriate for use as an HTML/JS identifier (e.g., "overlayPane", "markerPane", or custom names).
  - No default — required positional parameter on initialization.

- z_index: int (default: 625)
  - Description: intended CSS stacking order for the pane; larger values render on top of smaller ones.
  - Constraints: this class stores the numeric value as-is; it does not validate the range or coerce types. Callers should pass an integer (or a value usable where a numeric z-index is expected).

- pointer_events: bool (default: False)
  - Description: signals whether the pane should receive pointer events (True) or not (False); stored as provided without transformation.
  - Constraints: class does not enforce type; callers should pass a boolean.

Class invariants:
- _name is always "Pane" after initialization.
- The instance always has attributes name, z_index, and pointer_events set during __init__.

## Lifecycle:
Creation:
- Constructor signature: CustomPane(name, z_index=625, pointer_events=False)
  - name: required; expected string.
  - z_index: optional; default 625.
  - pointer_events: optional; default False.
- The constructor calls super().__init__() and then sets _name, name, z_index, and pointer_events as instance attributes.

Usage:
- Typical sequence:
  1. Instantiate: pane = CustomPane("my-pane", z_index=650, pointer_events=True)
  2. Attach to a parent element that participates in folium's element tree (for example, a Map or other MacroElement supporting add_child): parent.add_child(pane)
  3. When the parent's rendering pipeline runs, the pane instance is expected to be inspected by map templates/renderers (the CustomPane itself does not implement rendering logic in this class; it only holds configuration).
- There are no additional methods on CustomPane; after instantiation its attributes are read by consumers.

Destruction / cleanup:
- The class provides no explicit cleanup API (no close, context manager, or teardown hook). Cleanup is handled by the containing element/tree if necessary.

## Method Map:
flowchart TD
    A[CustomPane.__init__(name, z_index, pointer_events)]
    A --> B[call super().__init__()  (MacroElement.__init__)]
    A --> C[set _name = "Pane"]
    A --> D[set name = name]
    A --> E[set z_index = z_index]
    A --> F[set pointer_events = pointer_events]

Notes:
- The diagram shows the only method executed during normal use is __init__, which delegates first to the parent initializer and then sets attributes.

## Raises:
- __init__ does not raise any exceptions explicitly.
- Possible errors are only those raised by the parent class's __init__ (MacroElement.__init__) if that parent enforces additional constraints — such behavior is outside this class's implementation and not present in this source.
- This class does not validate types or ranges; passing unexpected types (e.g., name=None) will not raise here but may cause downstream errors when renderers/templates expect particular types.

## Example:
- Create a custom pane and attach it to a map-like parent that supports add_child:

  1. Instantiate:
     - pane = CustomPane("labels-pane", z_index=700, pointer_events=True)

  2. Attach to a parent (typical parent is a Map or another MacroElement that exposes add_child):
     - parent.add_child(pane)

  3. After attaching, when the parent renders or serializes the element tree, the pane's attributes (name, z_index, pointer_events) should be available for templates or rendering code to use in producing the final HTML/JS that creates the Leaflet pane.

Implementation notes for re-creation:
- Minimal reimplementation requires:
  - A class named CustomPane that inherits from the project's MacroElement base.
  - A Template object assigned to _template (empty Template() is acceptable).
  - An __init__ that accepts (name, z_index=625, pointer_events=False), calls super().__init__(), sets self._name = "Pane", then assigns self.name, self.z_index, and self.pointer_events from the parameters.

### `folium.map.CustomPane.__init__` · *method*

## Summary:
Initializes a CustomPane instance by calling the MacroElement initializer and storing the pane metadata (logical name, CSS z-index, and pointer-events flag) on the object.

## Description:
Known callers and contexts:
- Application code or library code that needs to create a named Leaflet pane for use in map rendering (e.g., user code: pane = CustomPane("labels-pane", z_index=700, pointer_events=True)).
- Typical lifecycle stage: invoked at object-creation time when constructing a CustomPane prior to attaching it to a parent element (for example, parent.add_child(pane)) so that the map rendering pipeline can later read these attributes and render the corresponding Leaflet pane in the generated HTML/JS.

Why this logic is its own method:
- Separates instance initialization from other behaviors so the element participates correctly in the folium element tree (by invoking the parent MacroElement initializer).
- Keeps pane metadata setup localized and explicit, enabling other parts of the rendering pipeline to rely on a well-known set of attributes (_name, name, z_index, pointer_events) being present after construction.

## Args:
    name (str):
        Logical pane identifier used by renderers/templates to create or reference a Leaflet pane.
        Required positional parameter. The class does not validate value; callers should supply a non-empty string suitable for use as an HTML/JS identifier.
    z_index (int, optional):
        Intended CSS stacking order for the pane. Defaults to 625. The value is stored as-is; no range enforcement or type coercion is performed.
    pointer_events (bool, optional):
        Whether the pane should receive pointer events. Defaults to False. The value is stored as-is; callers should pass a boolean.

## Returns:
    NoneType:
        The initializer returns None (standard constructor behavior). The effect is conveyed via mutations to the instance attributes.

## Raises:
    Any exception raised by MacroElement.__init__:
        If the parent initializer (super().__init__()) raises (for example, due to parent-class constraints), that exception will propagate. This __init__ does not raise any exceptions explicitly.
    Note: This method does not validate argument types or values; passing inappropriate types (e.g., name=None) will not raise here but may lead to downstream errors during rendering.

## State Changes:
Attributes READ:
    - None from self (this method does not read existing self attributes before writing).
    - It does call super().__init__(), which may read/write parent-class state (not part of this method's direct reads).

Attributes WRITTEN:
    - self._name: set to the literal string "Pane".
    - self.name: set to the provided name argument.
    - self.z_index: set to the provided z_index argument.
    - self.pointer_events: set to the provided pointer_events argument.

## Constraints:
Preconditions:
    - No enforced preconditions in code: arguments are accepted and stored without type or value validation.
    - Recommended caller guarantees (not enforced):
        * name should be a non-empty string safe for use in HTML/JS identifiers.
        * z_index should be an integer or numeric value appropriate for CSS stacking context.
        * pointer_events should be a boolean.

Postconditions (guaranteed after call completes successfully):
    - The instance has attributes _name == "Pane", name, z_index, and pointer_events set to the supplied values.
    - The parent class initializer has been executed (super().__init__() was called), so any MacroElement initialization semantics have run prior to attribute assignment.

## Side Effects:
    - Mutates the instance by setting the attributes listed above.
    - Calls the parent initializer (MacroElement.__init__()), which may perform additional initialization or register the element with other structures (behavior depends on the parent class and is external to this method).
    - No I/O, network, or file-system operations are performed.

