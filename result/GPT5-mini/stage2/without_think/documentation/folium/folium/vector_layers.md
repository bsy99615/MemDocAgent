# `vector_layers.py`

## `folium.vector_layers.path_options` · *function*

## Summary:
Produces a canonical dictionary of Leaflet-style path rendering options from flexible Python kwargs and the two convenience flags (line, radius). The result normalizes option names (via camelize), applies sensible defaults, and collects extra properties required by specific vector types.

## Description:
This utility centralizes conversion and defaulting logic for visual options used by Folium vector layers (e.g., polylines, polygons, circles). It has three responsibilities:
1. Normalize incoming option names using camelize.
2. Apply sane defaults for common styling properties.
3. Conditionally include extra properties used by specific vector types (line-specific options and numeric radius).

Known callers within a Folium-style codebase:
- Low-level vector-layer constructors and helpers that need a normalized, ready-to-serialize options dict for Leaflet layers (for example: polyline/polygon/circle constructors or internal rendering helpers). Specific call sites are not enumerated here; this function is intended to be a shared utility used wherever consistent path options are required.

Why this function is extracted:
- Avoids duplication of option normalization and default values across multiple layer implementations.
- Centralizes Leaflet option naming and defaults, making updates to styling behavior simple and consistent.
- Encapsulates shape-specific option handling (line and radius) outside of layer constructors.

## Args:
    line (bool, optional)
        Default: False.
        When True, include line-specific extra options:
            - smoothFactor (float, default 1.0)
            - noClip (bool, default False)
        Typical usage: set by polyline/line-like layer constructors.

    radius (bool|int|float, optional)
        Default: False.
        If truthy (not False, 0, or None), include a "radius" entry with this value in the returned dict. Typical usage: numeric radius for circle-like layers.

    **kwargs
        Arbitrary style options. All provided keys are passed through camelize(key) before further processing.
        Important notes about camelize behavior:
            - camelize converts underscore-separated names into camelCase by joining segments and capitalizing subsequent segments.
            - The original casing of the first segment is preserved (e.g., "fill_color" -> "fillColor"; "Fill_color" -> "FillColor").
        Recognized/populated keys (accepts snake_case or camelCase forms thanks to camelize):
            - color (str): default "#3388ff". Stroke color.
            - fillColor (str|False): default False. If truthy, fill is enabled and fillColor is used; if False, fillColor is set to color and fill is determined by the 'fill' kwarg.
            - fill (bool): default False (only used when fillColor is not truthy).
            - gradient (any JSON-serializable structure): default None. If not None, included verbatim.
            - smoothFactor (float): default 1.0 when line=True (consumed when line True).
            - noClip (bool): default False when line=True (consumed when line True).
            - stroke (bool): default True.
            - weight (int|float): default 3.
            - opacity (float): default 1.0.
            - lineCap (str): default "round".
            - lineJoin (str): default "round".
            - dashArray (str|None): default None.
            - dashOffset (str|None): default None.
            - fillOpacity (float): default 0.2.
            - fillRule (str): default "evenodd".
            - bubblingMouseEvents (bool): default True.
        Any kwargs not handled above are not included in the returned dict (they remain unused by this function).

## Returns:
    dict:
        A mapping of canonical camelCase Leaflet option names to concrete values. The returned dict always includes the core styling keys (stroke, color, weight, opacity, lineCap, lineJoin, dashArray, dashOffset, fill, fillColor, fillOpacity, fillRule, bubblingMouseEvents) with either provided or default values.
        Conditionally included keys:
            - smoothFactor, noClip (when line=True)
            - radius (when radius argument is truthy)
            - gradient (when provided and not None)
        Edge-case behavior:
            - If fillColor is provided and truthy, the returned 'fill' key will be True.
            - If fillColor is False or not provided, fillColor is set to the chosen stroke color and 'fill' is read from kwargs with default False.

## Raises:
    - This function does not explicitly raise exceptions under normal operation.
    - Potential exceptions may originate from camelize if non-string keys are used; callers should provide string-like keys for kwargs.
    - Any exception raised by camelize will propagate.

## Constraints:
    Preconditions:
        - Keys of kwargs should be strings (or objects camelize can handle).
        - Values intended for JSON serialization (if the returned dict will be serialized for the front end) should be JSON-serializable.
        - If you intend to include radius, pass a truthy numeric value (0 and False are treated as absent).

    Postconditions:
        - The returned dict uses camelized option names (with first-segment casing preserved) and contains defaults for all documented keys.
        - No external state is modified.

## Side Effects:
    - None. The function performs no I/O, network calls, or global state mutation. It only constructs and returns a plain dict.

## Control Flow:
flowchart TD
    A[Start: call path_options(line, radius, **kwargs)] --> B[camelize all kwargs keys (first-segment case preserved)]
    B --> C{line is True?}
    C -- Yes --> D[extra_options.smoothFactor = kwargs.pop("smoothFactor",1.0)]
    D --> E[extra_options.noClip = kwargs.pop("noClip",False)]
    C -- No --> E
    E --> F{radius is truthy?}
    F -- Yes --> G[extra_options.radius = radius]
    F -- No --> H
    G --> H
    H --> I[color = kwargs.pop("color","#3388ff")]
    I --> J[fillColor = kwargs.pop("fillColor", False)]
    J --> K{fillColor truthy?}
    K -- Yes --> L[fill = True]
    K -- No --> M[fillColor = color; fill = kwargs.pop("fill", False)]
    L --> N
    M --> N
    N --> O[gradient = kwargs.pop("gradient", None)]
    O --> P{gradient is not None?}
    P -- Yes --> Q[extra_options.gradient = gradient]
    P -- No --> R
    Q --> R
    R --> S[Build default dict by popping many keys with defaults]
    S --> T[default.update(extra_options)]
    T --> U[return default]

## Examples:
Example 1 — Line/polyline options
    opts = path_options(line=True, color="#ff0000", weight=5, smooth_factor=0.8)
    # Result: dict with smoothFactor=0.8 (consumed via camelize from smooth_factor), color="#ff0000", weight=5, and other defaults.

Example 2 — Circle with radius and explicit fill color
    opts = path_options(radius=10, color="#00ff00", fillColor="#880088", fillOpacity=0.6)
    # Result includes: radius=10, color="#00ff00", fill=True, fillColor="#880088", fillOpacity=0.6

Example 3 — Snake_case keys and first-segment casing preserved
    opts = path_options(color="#123456", Fill_color="#abcdef", line_cap="butt")
    # camelize preserves first segment casing:
    # "color" -> "color", "Fill_color" -> "FillColor", "line_cap" -> "lineCap"
    # Returned dict uses these camelized keys.

Example 4 — Gradient inclusion
    opts = path_options(gradient=[{"0.0": "red"}, {"1.0": "blue"}])
    # gradient included verbatim under key "gradient".

## `folium.vector_layers.BaseMultiLocation` · *class*

## Summary:
A lightweight MacroElement base class that stores a validated collection of geographic locations and optionally attaches a Popup and/or Tooltip as children.

## Description:
BaseMultiLocation exists to centralize common initialization and bounding-box behavior for elements that represent multiple geographic points (for example: polyline-like or multi-marker layers). It accepts raw location inputs, normalizes and validates them via the shared validate_locations utility, and attaches optional Popup and Tooltip children (wrapping plain strings into Popup/Tooltip objects when necessary).

Typical scenarios to instantiate:
- When implementing or constructing a layer-like object that needs to keep a collection of coordinates and optionally expose a popup/tooltip for each feature or for the whole layer.
- Test code that needs a minimal MultiLocation-capable MacroElement to exercise layout or bounding aggregation logic.

Motivation and responsibility:
- Responsibility: normalize/validate location inputs and attach optional UI children consistently across subclasses.
- Boundary: does not perform rendering itself (rendering is handled by MacroElement/Element templates). It only stores locations and children and provides a convenience bounding-box method.

Known callers:
- Consumer code that builds layer objects and needs to encapsulate multiple coordinates into a MacroElement before attaching to a Map/Figure.
- Map/viewport utilities that compute extents by calling the instance method _get_self_bounds (for example, Map.fit_bounds-like aggregators).

## State:
- locations (list)
    - Type: list (returned by validate_locations)
    - Contents: same nesting structure as the input, with every leaf coordinate pair normalized to a list of two floats [lat, lon] (see validate_locations for exact normalization rules).
    - Invariants:
        - Always present after __init__ returns (unless validate_locations raised an exception).
        - Each leaf is a list of two floats (unless validate_locations raised).
    - Caller constraints: pass an iterable acceptable to validate_locations (non-empty iterable of coordinate pairs or nested iterables). validate_locations will raise TypeError for non-iterable inputs or ValueError for empty iterables or invalid leaves.

- Popup/Tooltip children (not stored in explicit attributes by this class)
    - If popup parameter is supplied and not an instance of folium.map.Popup, the constructor will create a Popup using Popup(str(popup)) and add it as a child via add_child.
    - If tooltip parameter is supplied and not an instance of folium.map.Tooltip, the constructor will create a Tooltip using Tooltip(str(tooltip)) and add it as a child via add_child.
    - Invariants:
        - After __init__, if popup was provided, an element of type Popup will be present among this object's children (accessible via the MacroElement child-management API).
        - After __init__, if tooltip was provided, an element of type Tooltip will be present among this object's children.
    - Note: The actual child container and APIs are provided by the MacroElement superclass; BaseMultiLocation only calls self.add_child(...).

Class invariants:
- self.locations is always the validated return value of validate_locations(locations) performed during construction.
- If popup/tooltip were supplied, corresponding MacroElement children have been added by the end of __init__.

## Lifecycle:
Creation
- Signature: __init__(locations, popup=None, tooltip=None)
    - locations: required; any iterable structure accepted by validate_locations (see its documentation).
    - popup: optional; either a folium.map.Popup instance or any object coercible to a string (will be wrapped by Popup(str(popup))).
    - tooltip: optional; either a folium.map.Tooltip instance or any object coercible to a string (will be wrapped by Tooltip(str(tooltip))).
- Behavior:
    1. Calls MacroElement.__init__() via super().__init__() (establishes element framework state).
    2. Calls validate_locations(locations) and assigns the result to self.locations. validate_locations performs input normalization and validation.
    3. If popup is not None:
         - If popup is already an instance of Popup, calls self.add_child(popup).
         - Else constructs Popup(str(popup)) and calls self.add_child(...) with it.
    4. If tooltip is not None:
         - If tooltip is already an instance of Tooltip, calls self.add_child(tooltip).
         - Else constructs Tooltip(str(tooltip)) and calls self.add_child(...) with it.

Usage
- Typical method call order:
    1. Instantiate: layer = BaseMultiLocation(locations, popup=..., tooltip=...)
    2. Optionally attach to a Map/Figure via the MacroElement container APIs (e.g., map.add_child(layer)) — MacroElement container behavior is external to this class.
    3. Consumers that need the spatial extent call layer._get_self_bounds() to obtain a two-point bounding box computed from self.locations.
- There is no special required sequencing beyond construction before calling _get_self_bounds.

Destruction / cleanup
- No explicit cleanup is implemented by this class; no close() method or context-manager support. Cleanup is handled by the element container (removing children) or by Python garbage collection.

## Method Map:
flowchart LR
    A[__init__(locations, popup=None, tooltip=None)] --> B[super().__init__()]
    B --> C[self.locations = validate_locations(locations)]
    C --> D{popup is not None?}
    D -- Yes --> E[if isinstance(popup, Popup) then add_child(popup) else add_child(Popup(str(popup)))]
    D -- No --> F
    C --> G{tooltip is not None?}
    G -- Yes --> H[if isinstance(tooltip, Tooltip) then add_child(tooltip) else add_child(Tooltip(str(tooltip)))]
    G -- No --> I
    I --> END[Construction complete]
    END --> J[_get_self_bounds() -> get_bounds(self.locations)]

## Raises:
Exceptions that may be raised during construction or by _get_self_bounds (propagated from utilities and child constructors):

During __init__:
- TypeError
    - If validate_locations raises TypeError because the provided locations is not iterable.
    - If str(popup) or str(tooltip) triggers a TypeError from the object's __str__ implementation (rare).
- ValueError
    - If validate_locations raises ValueError (e.g., when locations is an empty iterable) or if validate_location (used internally) raises for invalid leaf coordinate pairs.
- AssertionError or other exceptions raised by Popup(...) or Tooltip(...) constructors (for example, Tooltip may assert that style is a str if provided). See Popup and Tooltip documentation for constructor-specific errors.
- Any exception raised by MacroElement.__init__ or MacroElement.add_child (propagated).

During _get_self_bounds:
- IndexError
    - If get_bounds iterates a coordinate with fewer than two elements (propagated from get_bounds/iter_coords).
- TypeError
    - If comparisons in bounding computation fail because coordinate components are not mutually comparable (propagated from get_bounds/none_min/none_max).
- Any other exception raised by get_bounds or the iter_coords helper (for example AttributeError, KeyError) will propagate upward.

Notes:
- Errors raised by BaseMultiLocation are generally propagated from the helper utilities it uses:
    - validate_locations: raises TypeError for non-iterable inputs and ValueError for empty inputs or invalid leaf coordinates.
    - Popup/Tooltip constructors: may raise AssertionError or other exceptions according to their own validation logic.
    - get_bounds: may raise IndexError or TypeError, or propagate exceptions from iter_coords; these are not intercepted by BaseMultiLocation.
- Callers should consult the documented behavior of validate_locations, Popup, Tooltip, and get_bounds for the precise error conditions and messages.

## Example:
1) Basic instantiation with string popup and tooltip:
    locations = [[51.5, -0.1], [51.6, -0.2], [51.55, -0.15]]
    layer = BaseMultiLocation(locations, popup="My popup text", tooltip="Info")

    # After construction:
    # - layer.locations is a list of validated [lat, lon] float pairs (see validate_locations).
    # - A Popup and a Tooltip instance have been added as children (wrapping the provided strings).

2) Query the bounds for the layer (caller should handle possible exceptions from get_bounds):
    bounds = layer._get_self_bounds()
    # bounds is of the form [[min0, min1], [max0, max1]] where entries are numeric or None.

3) Attaching to a Map/Figure:
    # Use the MacroElement container API (map.add_child(layer) or equivalent) to include this layer in rendering.
    # Rendering and lifecycle interactions are governed by the MacroElement framework.

### `folium.vector_layers.BaseMultiLocation.__init__` · *method*

## Summary:
Initializes the element by validating and storing a collection of geographic locations and optionally attaching a Popup and/or Tooltip child to the element, updating the object's stored locations and child elements.

## Description:
Known callers and typical context:
- Called during object construction when creating any layer-like MacroElement that represents multiple coordinates (for example, multi-marker layers, grouping elements, or polyline-like layers).
- Higher-level code that builds map layers or tests that exercise multi-location behavior will instantiate this class to establish normalized location state before adding the element to a Map/Figure.
- Map/viewport utilities or container code that compute extents will use the instance later (for example by calling an instance method such as _get_self_bounds()) after construction.

Why this is its own method:
- Construction responsibilities (normalizing/validating coordinates and consistently attaching optional UI children) are common to many multi-location elements. Encapsulating these steps in the initializer centralizes validation and child-attachment behavior so subclasses can reuse it and so bounding/extent utilities can rely on a stable, validated self.locations value.

## Args:
    locations (iterable-like): Required. Any value accepted by the shared validate_locations(locations) utility (e.g., an iterable of coordinate pairs or nested iterables). validate_locations performs normalization and returns a list-like structure where each leaf coordinate is normalized to a two-element numeric sequence. The constructor does not itself validate shapes beyond delegating to validate_locations.
    popup (folium.map.Popup or any, optional): If provided and already an instance of Popup, it is attached directly as a child. Otherwise, it is coerced to a string via str(popup) and wrapped in a new Popup instance which is then attached. Default is None (no popup child added).
    tooltip (folium.map.Tooltip or any, optional): If provided and already an instance of Tooltip, it is attached directly as a child. Otherwise, it is coerced to a string via str(tooltip) and wrapped in a new Tooltip instance which is then attached. Default is None (no tooltip child added).

## Returns:
    None. The constructor returns no value; its effect is to mutate the instance (self).

## Raises:
    TypeError:
        - If validate_locations raises TypeError (e.g., when locations is not iterable).
        - If the object's __str__ raises TypeError when coercing popup or tooltip with str(...).
        - If MacroElement.__init__ or MacroElement.add_child raises TypeError.
    ValueError:
        - If validate_locations raises ValueError (e.g., for empty input or invalid coordinate leaves).
    Any exception propagated from:
        - validate_locations (any of its documented exceptions),
        - Popup(...) or Tooltip(...) constructors (their own validation assertions/errors),
        - MacroElement.__init__ or add_child (initialization or child-management errors).
    Notes:
        - This constructor does not catch or convert exceptions; all exceptions from utilities and child constructors propagate directly to the caller.

## State Changes:
Attributes READ:
    - (none) — this initializer does not read any existing self.<attr> fields prior to assignment; it only uses the input arguments and base-class initialization.

Attributes WRITTEN:
    - self.locations: set to the value returned by validate_locations(locations).
    - MacroElement child state (via self.add_child(...)): if popup and/or tooltip are provided, Popup and/or Tooltip instances are added to the element's children collection maintained by the MacroElement base class. The exact storage (child list/dict) is provided by MacroElement; this method mutates that child container via add_child.

## Constraints:
Preconditions:
    - The locations argument must be acceptable to validate_locations: typically an iterable (non-empty, nested or flat) of coordinate pairs or coordinate-like sequences. If this precondition is not met, validate_locations will raise.
    - If popup or tooltip are provided and are not Popup/Tooltip instances, they must be convertible to a string via str(...). If conversion raises, the constructor will propagate that error.
    - MacroElement.__init__ must succeed (no preconditions in this method that bypass the base-class initialization).

Postconditions:
    - self.locations exists and equals the normalized/validated return value of validate_locations(locations).
    - If a popup argument was supplied, a Popup instance will be present among this element's children (either the same object passed in if already a Popup, or a newly constructed Popup wrapping str(popup)).
    - If a tooltip argument was supplied, a Tooltip instance will be present among this element's children (similarly either the original or a new Tooltip wrapping str(tooltip)).
    - The constructed object is ready for subsequent operations such as bounding calculations or being added to a Map/Figure.

## Side Effects:
    - Calls MacroElement.__init__() (base-class initialization).
    - Calls validate_locations(locations) which may inspect/iterate the provided locations argument.
    - May construct new Popup/Tooltip instances (side effect: these constructors may perform validation or other internal initializations).
    - Calls self.add_child(...) to mutate the MacroElement-managed child collection (this affects state external to the local stack frame).
    - Calls to str(popup) or str(tooltip) use the provided objects' __str__ implementations (which can have arbitrary side effects).
    - No network, file I/O, or other external resource I/O is performed by this method itself.

## Implementation Notes (for correct reimplementation):
    - Ensure you call the superclass initializer before assigning or adding children: super().__init__() must execute first to set up MacroElement internals.
    - Use the shared validate_locations utility to perform normalization and validation; assign its return value directly to self.locations.
    - For popup and tooltip handling:
        - If popup is not None:
            - If isinstance(popup, Popup): call self.add_child(popup)
            - Else: create Popup(str(popup)) and call self.add_child(...) with the new instance.
        - If tooltip is not None:
            - If isinstance(tooltip, Tooltip): call self.add_child(tooltip)
            - Else: create Tooltip(str(tooltip)) and call self.add_child(...) with the new instance.
    - Do not swallow exceptions from validate_locations, Popup/Tooltip constructors, or add_child; let them propagate to the caller.

### `folium.vector_layers.BaseMultiLocation._get_self_bounds` · *method*

## Summary:
Compute and return the 2D bounding box for this layer's stored locations and leave the object's location attribute unchanged.

## Description:
This method delegates bounding-box computation to the shared get_bounds utility using the already-validated self.locations. It is a thin wrapper so callers can obtain the layer's spatial extent without needing to know how locations are validated or iterated.

Known callers and context:
- No direct callers were found in the supplied repository snapshot.
- Typical callers (not present in the snapshot) include map-level layout or viewport routines that aggregate child-layer extents (for example: a Map.fit_bounds implementation or a layer-group bounds aggregator) or any external code that queries a layer for its geographic extent.
- Lifecycle stage: invoked when a consumer needs the geographic extent after the layer has been constructed (i.e., after __init__ has set self.locations via validate_locations).

Why this logic is a separate method:
- Encapsulates the binding between the instance's stored locations and the common get_bounds computation, making it easy to override in subclasses or to mock during testing.
- Keeps calling code concise and consistent by centralizing how an object's own locations are passed to the shared bounding-box helper.

## Args:
    None

## Returns:
    list[list[float|int|None], list[float|int|None]]
    - Shape: [[min0, min1], [max0, max1]] where each entry is either a numeric value (int or float) or None.
    - Semantics:
        - min0/min1 are the minimum observed values for coordinate axis 0 and axis 1 across all points in self.locations.
        - max0/max1 are the maximum observed values for the same axes.
    - Edge-case return values:
        - If no coordinates are present in self.locations, returns [[None, None], [None, None]].
        - If exactly one coordinate (a, b) is present, returns [[a, b], [a, b]].

## Raises:
    - IndexError: if underlying coordinate iteration yields a point with fewer than two elements (propagated from get_bounds).
    - TypeError: if comparisons required to compute minima/maxima fail because values are not mutually comparable (propagated from get_bounds).
    - Any exception raised by iter_coords or other helpers used by get_bounds (e.g., AttributeError, KeyError) will propagate upward.
    - Note: validate_locations is invoked during object initialization; invalid shapes that would have raised earlier will generally be surfaced at construction time, not here.

## State Changes:
    Attributes READ:
        - self.locations

    Attributes WRITTEN:
        - None (this method does not mutate self or external objects)

## Constraints:
    Preconditions:
        - The instance must have a self.locations attribute (set during __init__ by validate_locations).
        - self.locations must be an object acceptable to the coordinate iterator used by get_bounds (i.e., iter_coords should be able to yield coordinate tuples from it).
        - If caller expects numeric bounds, leaf coordinate tuples yielded must contain numeric, comparable values at indices 0 and 1.

    Postconditions:
        - Returns a two-point bounding box representing minima and maxima for the first two coordinate axes, as documented above.
        - self.locations remains unchanged.

## Side Effects:
    - None intrinsic: no network, file I/O, or global state mutation.
    - The method simply calls get_bounds and returns its result; any side effects from that helper (none expected) would be observable here.

## `folium.vector_layers.PolyLine` · *class*

## Summary:
Represents a Leaflet polyline layer: a multi-location vector element that stores validated coordinates, optional Popup/Tooltip children, and a canonical Leaflet-style options dictionary for line rendering.

## Description:
PolyLine is a thin, opinionated subclass of the shared multi-location MacroElement base (BaseMultiLocation). It exists to represent a polyline-like vector on a map: it accepts raw location inputs (in any form accepted by the shared validate_locations utility), optional popup and tooltip content (strings or Popup/Tooltip instances), and styling keyword arguments which are normalized and canonicalized into a Leaflet-friendly options dictionary via path_options(line=True).

Instantiate this class when you need a programmatic representation of a polyline that will be rendered by the MacroElement/HTML template machinery. Typical callers are map-building code or higher-level layer factories that construct vector layers and then attach them to a Map/Figure via the MacroElement container API.

Responsibilities and boundaries:
- Responsibility: validate/normalize the provided locations, attach optional Popup/Tooltip children, and prepare a canonical options dict suitable for JSON/Leaflet consumption.
- Boundary: PolyLine does not itself perform rendering or DOM insertion — rendering is handled by MacroElement/Template when the element is attached to a Map and the map is rendered. PolyLine does not implement geometry algorithms beyond delegating bounds computation to BaseMultiLocation.

## State:
- _template (jinja2.Template)
    - Type: Template
    - Description: A Jinja2 Template instance used by the MacroElement rendering system. In the source this attribute is initialized to Template() and therefore always holds a Template object; the content/layout of the template is external to PolyLine and used by MacroElement to produce client-side code.
    - Invariants: always present on the class.

- _name (str)
    - Type: str
    - Description: Human-readable element name used by the MacroElement framework. PolyLine sets this to "PolyLine" during initialization.
    - Invariants: equals "PolyLine" immediately after __init__ returns.

- locations (list)
    - Origin: populated by BaseMultiLocation.__init__ via validate_locations(locations)
    - Type: list (possibly nested) whose leaves are two-element lists of floats [lat, lon]
    - Valid values / constraints:
        - Must be an iterable acceptable to validate_locations (non-empty iterable of coordinate pairs or nested iterables).
        - Each leaf is normalized to two floats (validate_locations enforces this; see its documentation for details).
    - Invariants:
        - Present after construction unless validate_locations raised.
        - Each location leaf is a two-element numeric list.

- options (dict)
    - Type: dict[str, any]
    - Description: Canonical Leaflet-style style/options dictionary produced by calling path_options(line=True, **kwargs) with constructor kwargs.
    - Typical keys and semantics (drawn from path_options defaults):
        - stroke (bool), color (str), weight (int/float), opacity (float),
          lineCap (str), lineJoin (str), dashArray (str|None), dashOffset (str|None),
          fill (bool), fillColor (str|False), fillOpacity (float), fillRule (str),
          bubblingMouseEvents (bool)
        - Line-specific keys included because line=True: smoothFactor (float), noClip (bool)
        - Conditionally included: gradient, radius (not relevant for PolyLine since radius is not requested here)
    - Invariants:
        - Always present after __init__ returns.
        - Keys are camelCase (camelize applied by path_options), and values reflect defaults when not provided.

- Children (MacroElement children)
    - Popup and Tooltip instances may be added as children during construction if popup and/or tooltip arguments are provided.
    - Invariants:
        - If popup argument was supplied, a Popup instance will be present among children; if tooltip was supplied, a Tooltip instance will be present.

Class invariants:
- After construction, self.locations and self.options are both set and valid according to the constraints above.
- Any provided popup/tooltip have been normalized and added as children by BaseMultiLocation.

## Lifecycle:
Creation (how to instantiate)
- Required arguments:
    - locations: required. Any input accepted by validate_locations (see validate_locations for normalization rules). Must not be an empty iterable.
- Optional arguments:
    - popup: None or Popup instance or any object coercible to string. If not a Popup instance, BaseMultiLocation will wrap it with Popup(str(popup)) and add it as a child.
    - tooltip: None or Tooltip instance or any object coercible to string. If not a Tooltip instance, BaseMultiLocation will wrap it with Tooltip(str(tooltip)) and add it as a child.
    - **kwargs: Arbitrary style options consumed by path_options. Keys will be normalized (camelized) and defaults applied. Because PolyLine passes line=True to path_options, line-specific keys (smoothFactor, noClip) will be included.

Instantiation sequence (what happens inside __init__):
1. Call BaseMultiLocation.__init__(locations, popup=popup, tooltip=tooltip), which:
   - Initializes MacroElement base state,
   - Calls validate_locations(locations) and assigns the normalized result to self.locations,
   - Wraps and adds popup/tooltip children if provided.
2. Set self._name = "PolyLine".
3. Compute self.options = path_options(line=True, **kwargs) to produce a canonical options dict for line rendering.

Usage (typical method order)
- After instantiation, attach the element to a Map/Figure using the MacroElement container API (for example, map.add_child(instance) or equivalent).
- Consumers may call BaseMultiLocation._get_self_bounds() or the Map/viewport utilities to obtain the bounding box derived from self.locations (this delegates to get_bounds).
- No additional ordering constraints for methods beyond constructing before attaching/querying bounds.

Destruction and cleanup:
- PolyLine has no explicit cleanup methods (no close() or context-manager support). Removal from a Map or freeing instances is handled by the container or Python garbage collection.

## Method Map:
flowchart LR
    A[Call PolyLine(locations, popup=None, tooltip=None, **kwargs)] --> B[BaseMultiLocation.__init__()]
    B --> C[self.locations = validate_locations(locations)]
    C --> D{popup provided?}
    D -- Yes --> E[add_child(Popup(...) or Popup instance)]
    D -- No --> F
    C --> G{tooltip provided?}
    G -- Yes --> H[add_child(Tooltip(...) or Tooltip instance)]
    G -- No --> F
    F --> I[self._name = "PolyLine"]
    I --> J[self.options = path_options(line=True, **kwargs)]
    J --> K[Instance ready: attach to Map / call _get_self_bounds()]

(Note: rendering uses MacroElement and the instance _template during map rendering; template content is external to this class.)

## Raises:
Exceptions that may be raised during __init__ (all are propagated; PolyLine does not catch them):
- TypeError
    - If validate_locations raises TypeError because locations is not iterable or contains invalid types.
    - If camelize in path_options rejects non-string keys, or str(popup)/str(tooltip) raise TypeError.
- ValueError
    - If validate_locations raises ValueError (for example, when locations is empty or leaf coordinates are invalid).
- Any exceptions raised by Popup(...) or Tooltip(...) constructors when wrapping popup/tooltip values (could include AssertionError or other validation errors from those classes).
- Any exceptions from MacroElement.__init__ or MacroElement.add_child calls.
- Any unexpected exception from path_options (e.g., if a non-serializable gradient structure causes downstream serialization errors later during rendering).

Callers should treat these as originating from the helper utilities (validate_locations, path_options, Popup, Tooltip) and consult those components for precise error conditions.

## Example:
- Typical creation:
    - Provide a non-empty iterable of coordinate pairs (or nested iterables acceptable to validate_locations) and optional style kwargs.
    - Optional popup/tooltip may be provided as strings or as Popup/Tooltip instances; strings will be wrapped.

- Typical use sequence:
    1. Create the PolyLine instance with locations and style kwargs (e.g., color, weight, opacity).
    2. Attach the instance to a Map/Figure using the MacroElement container API (for example, map.add_child(instance)).
    3. Optionally request the bounding box from the instance (via BaseMultiLocation._get_self_bounds()) to compute viewport or fit bounds.
    4. Rendering occurs when the containing Map/Figure is rendered; no explicit render call is required on the PolyLine instance.

- Notes:
    - To control visual appearance, pass style kwargs accepted by path_options (snake_case or camelCase keys are accepted; they are normalized by camelize). Because PolyLine sets line=True, line-specific options such as smoothFactor and noClip are supported.
    - No explicit cleanup is required; remove the element from its container if you need to discard it before garbage collection.

### `folium.vector_layers.PolyLine.__init__` · *method*

## Summary:
Initializes a PolyLine element by validating and storing location coordinates, adding optional Popup/Tooltip children, setting the element name, and producing a canonical Leaflet-style options dictionary for line rendering.

## Description:
This constructor is called when a new PolyLine instance is created by application code that builds or composes map layers (for example, map-building routines, layer factories, or test code that instantiates vector layers). It runs during the object creation / initialization stage and prepares the instance to be attached to a Map or Figure via the MacroElement container API.

Why this logic lives in __init__:
- Location validation, optional child creation (popup/tooltip), element naming, and canonicalizing style options are intrinsic to object construction and must be performed before the element can be meaningfully used or rendered. Keeping this logic in the constructor centralizes initialization responsibilities and ensures the instance invariants (locations present, options canonicalized) hold immediately after construction.

Known callers / contexts:
- Application code that needs to draw polylines on a map constructs PolyLine(locations, ...) during the map composition step.
- Higher-level factories or utilities that create multiple layers programmatically will call this constructor as part of their assembly pipeline.

## Args:
    locations (iterable)
        Required. Any iterable accepted by the shared validate_locations utility (e.g., an iterable of 2-number coordinate pairs or nested iterables representing multiple segments). Values are normalized by validate_locations into a list of two-element numeric coordinate lists [lat, lon].
        Constraints:
            - Must be non-empty and iterable.
            - Leaves must represent numeric latitude/longitude values acceptable to validate_locations.
        Behavior on invalid input:
            - validate_locations can raise TypeError or ValueError (propagated).

    popup (None|str|Popup, optional)
        Default: None.
        If None: no popup is added.
        If a Popup instance: the instance is added as a child.
        If another value (commonly a string): BaseMultiLocation (superclass) will coerce it into a Popup by calling Popup(str(popup)) and add that child.
        Errors:
            - Popup(...) constructor may raise if wrapping fails; such exceptions propagate.

    tooltip (None|str|Tooltip, optional)
        Default: None.
        If None: no tooltip is added.
        If a Tooltip instance: the instance is added as a child.
        If another value: BaseMultiLocation will coerce it into a Tooltip by calling Tooltip(str(tooltip)) and add that child.
        Errors:
            - Tooltip(...) constructor may raise if wrapping fails; such exceptions propagate.

    **kwargs (mapping of style options)
        Arbitrary keyword arguments representing visual/style options (snake_case or camelCase). These are forwarded to path_options with line=True to produce a canonical Leaflet-style options dict.
        Behavior:
            - Keys are normalized (camelize) and defaults are applied by path_options.
            - Because line=True is passed, line-specific keys (e.g., smoothFactor, noClip) are included in the resulting options dict.
        Constraints:
            - Keys should be string-like (camelize expects strings); non-string keys may cause exceptions in camelize.
            - Values should be JSON-serializable if the returned options will later be serialized for frontend rendering.
        Typical keys include: color, weight, opacity, stroke, fill, fillColor, fillOpacity, smoothFactor, noClip, dashArray, lineCap, etc. For full canonicalization rules and defaults see the path_options utility documentation.

## Returns:
    None
    - As a constructor, __init__ does not return a value. After successful completion, the instance fields described in State Changes are guaranteed to be set.

## Raises:
    Any exception raised by the utilities invoked during initialization is propagated; PolyLine does not catch these internally. Typical raised exceptions include:
    - TypeError
        - If locations is not iterable or contains invalid element types (raised by validate_locations).
        - If camelize/path_options receive non-string-like keys or otherwise invalid input types.
        - If str(popup) or str(tooltip) raise TypeError when BaseMultiLocation attempts wrapping.
    - ValueError
        - If validate_locations determines the provided locations are invalid (e.g., empty sequence, invalid coordinate shapes).
    - Errors from Popup or Tooltip constructors if wrapping popup/tooltip values fails.
    - Any exceptions raised by MacroElement.__init__ or MacroElement.add_child during superclass initialization.
    - Any unexpected exceptions from path_options (e.g., if provided values are not JSON-serializable and later code attempts serialization).

## State Changes:
Attributes READ:
    - None of self's attributes are relied on prior to initialization; the constructor does not depend on pre-existing instance state. (All necessary work is performed by the superclass initializer and local calls.)

Attributes WRITTEN (set or mutated by this constructor and the invoked superclass constructor):
    - self.locations
        - Set by the superclass BaseMultiLocation.__init__ after calling validate_locations(locations). Becomes a normalized list of coordinate pairs.
    - self._children (or equivalent child container via MacroElement.add_child)
        - Mutated if popup and/or tooltip are provided: Popup/Tooltip instances are added as child elements.
    - self._name
        - Set explicitly in this constructor to the string "PolyLine".
    - self.options
        - Set explicitly to the dictionary returned by path_options(line=True, **kwargs). This is a canonical camelCase Leaflet-style options dict used for rendering.

## Constraints:
Preconditions (caller must ensure):
    - Provide a locations value acceptable to validate_locations (iterable of coordinate pairs or nested iterables). Passing an empty iterable or malformed coordinates will cause validate_locations to raise.
    - Provide string-like keys for styling kwargs (camelize expects string keys).
    - If popup/tooltip are non-instance values, they should be convertible to string via str(...) because BaseMultiLocation will call str() when wrapping.

Postconditions (guarantees after successful completion):
    - self.locations exists and contains normalized coordinate data (list of [lat, lon] pairs).
    - If popup was provided, a Popup instance is present among the element's children.
    - If tooltip was provided, a Tooltip instance is present among the element's children.
    - self._name == "PolyLine".
    - self.options is a dict with canonical camelCase keys and includes defaults; because line=True, line-specific keys are present (e.g., smoothFactor, noClip) according to path_options behavior.

## Side Effects:
    - Mutates the instance by setting attributes listed above (locations, _name, options) and possibly adding child elements (Popup/Tooltip) via MacroElement.add_child.
    - No I/O (file, network, or logging) is performed by this constructor itself.
    - No global state is modified.
    - Any exceptions raised by called utilities propagate to the caller and may interrupt construction.

## Implementation Notes (for reimplementation):
    - Call the superclass multi-location initializer with the provided locations and popup/tooltip (super().__init__(locations, popup=popup, tooltip=tooltip)). That call must:
        * Initialize MacroElement base state,
        * Validate and normalize locations using validate_locations and assign to self.locations,
        * Wrap popup and tooltip with Popup/Tooltip when necessary and add them as children.
    - Set the human-readable element name: self._name = "PolyLine".
    - Canonicalize visual options by calling path_options(line=True, **kwargs) and assign to self.options.
    - Do not catch exceptions from validate_locations, Popup/Tooltip constructors, or path_options; allow them to propagate so callers can handle input validation errors.

## `folium.vector_layers.Polygon` · *class*

## Summary:
Represents a polygon-shaped vector layer that stores one or more rings of geographic coordinates, optional Popup/Tooltip children, and a canonical set of Leaflet path-rendering options derived from constructor kwargs.

## Description:
Polygon is a lightweight MacroElement-based layer that holds validated geographic locations suitable for rendering a polygon (or multiple rings) and a ready-to-serialize options dictionary for client-side (Leaflet) rendering.

When to instantiate:
- When you need to represent a filled or stroked polygon on a map, possibly with holes (by supplying nested rings).
- When you want a MacroElement that exposes validated coordinates via .locations and styling options via .options for serialization into front-end templates.

Why this class exists:
- It centralizes location validation/normalization (delegated to BaseMultiLocation.validate_locations) and standardizes style option construction (delegated to path_options) for polygon/vector-like layers.
- It enforces the boundary between geometry data (locations) and presentation (options) while reusing common MacroElement child handling for Popup/Tooltip.

Known callers/factories:
- Any code constructing polygon layers for maps or tests needing a polygon MacroElement. Typically consumers call Polygon(...) and then attach it to a Map using MacroElement container APIs (e.g., map.add_child(polygon)).

## State:
- _template (jinja2.Template)
    - Type: jinja2.Template
    - Value: A Template instance defined at class level. Used by MacroElement rendering machinery during HTML/JS generation. The content is declared in the class source (empty in the provided snapshot); consumers should not modify it at runtime.
    - Invariant: Must remain a Template instance; MacroElement rendering expects this attribute.

- _name (str)
    - Type: str
    - Value: "Polygon"
    - Purpose: Human-readable identifier used by element frameworks and debugging/logging.

- locations (list)
    - Origin: Inherited and set by BaseMultiLocation.__init__ via validate_locations(locations).
    - Type: list preserving input nesting (flat list of [lat, lon] pairs, or nested lists for rings).
    - Content constraint: Each leaf is a list of two floats [lat, lon] as produced by validate_locations.
    - Caller constraints: Provide an iterable acceptable to validate_locations (must be iterable and non-empty; leaves must be indexable and convertible to float).
    - Invariant: After construction, self.locations equals the validated return value of validate_locations(locations).

- options (dict)
    - Origin: Set in this class's __init__ via path_options(line=True, **kwargs).
    - Type: dict[str, any]
    - Content: Canonical camelCase Leaflet path styling options. Because line=True was passed, line-specific keys (e.g., smoothFactor, noClip) will be present with defaults if not overridden. Optional keys (e.g., radius) are included only if requested.
    - Invariant: After construction, self.options is a plain dict suitable for JSON serialization (subject to the JSON-serializability of values provided by the caller).
    - Caller constraints: kwargs keys should be strings (or acceptable to camelize); values intended for front-end use should be JSON-serializable.

- Popup/Tooltip children (not direct attributes)
    - Behavior: If popup or tooltip arguments are supplied to __init__, BaseMultiLocation logic will add Popup and/or Tooltip objects as children of this Polygon instance (wrapping non-instance values in Popup(str(...)) / Tooltip(str(...))).
    - Invariant: After construction, if popup/tooltip were provided, MacroElement children include instances of Popup/Tooltip accordingly.

Class invariants:
- self.locations is always the validated list returned by validate_locations given the provided locations argument.
- self.options is always a dict returned by path_options(line=True, **kwargs).
- If popup/tooltip were provided to the constructor, corresponding child elements exist.

## Lifecycle:
Creation
- Signature: __init__(locations, popup=None, tooltip=None, **kwargs)
    - locations (required): Iterable accepted by validate_locations. Can be a flat list of coordinate pairs or nested lists (e.g., rings for polygons).
    - popup (optional): None or folium.map.Popup instance or any object coercible to string (wrapped in Popup).
    - tooltip (optional): None or folium.map.Tooltip instance or any object coercible to string (wrapped in Tooltip).
    - **kwargs: Arbitrary style/display options forwarded to path_options (these keys are camelized inside path_options). Example keys: color, fillColor, weight, fillOpacity, smooth_factor (becomes smoothFactor), etc.

Creation steps (what happens inside __init__):
1. Calls BaseMultiLocation.__init__(locations, popup=popup, tooltip=tooltip):
   - MacroElement.__init__ establishes element state.
   - validate_locations(normalizes + validates) and assigns to self.locations.
   - Adds Popup/Tooltip children if provided.
2. Sets self._name = "Polygon".
3. Calls path_options(line=True, **kwargs) and assigns the returned dict to self.options.

Usage
- Typical sequence:
    1. Instantiate: poly = Polygon(locations, popup="info", color="#3388ff", weight=4)
    2. Optionally attach to a Map/Figure: map.add_child(poly)
    3. Rendering: MacroElement rendering uses poly._template and poly.options/self.locations to produce client-side code (handled by the MacroElement framework).
    4. Consumers may call poly._get_self_bounds() (inherited from BaseMultiLocation) to obtain bounding box for these locations.
- Required ordering: Construction must complete before attaching to a container or calling bounds/serialization helpers.

Destruction / cleanup
- No explicit cleanup provided. Polygon instances rely on standard Python garbage collection and container APIs (MacroElement) to remove elements from a map. There is no close() or context-manager API.

## Method Map:
flowchart LR
    A[__init__(locations, popup=None, tooltip=None, **kwargs)] --> B[BaseMultiLocation.__init__()]
    B --> C[self.locations = validate_locations(locations)]
    C --> D{popup supplied?}
    D -- Yes --> E[add_child(Popup or Popup(str(popup)))]
    D -- No --> F
    C --> G{tooltip supplied?}
    G -- Yes --> H[add_child(Tooltip or Tooltip(str(tooltip)))]
    G -- No --> I
    I --> J[self._name = "Polygon"]
    J --> K[self.options = path_options(line=True, **kwargs)]
    K --> L[Ready: polygon holds validated locations + canonical options for rendering]

## Raises:
Exceptions are propagated from dependencies (Polygon itself performs no extra validation beyond delegating). Typical exceptions include:

- TypeError
    - If validate_locations raises TypeError because 'locations' is not iterable.
    - If camelize inside path_options is given a key it cannot handle (non-string), camelize may raise a TypeError.
    - If Popup/Tooltip string coercion triggers TypeError (rare, from __str__ of supplied objects).

- ValueError
    - If validate_locations raises ValueError (e.g., locations is empty) or if a leaf coordinate is invalid (wrong length, NaN) as validated by validate_location (propagated).

- Any exception raised by Popup or Tooltip constructors (e.g., assertion or type checks) when wrapping non-instance popup/tooltip values.

- Any exception raised by MacroElement.__init__ or MacroElement.add_child (propagated).

Notes on error surface:
- polygon.__init__ is thin: it delegates geometry validation to validate_locations and option normalization to path_options. Callers should validate inputs or be prepared to handle exceptions from those utilities.

## Example:
1) Simple polygon with default styling (flat ring):
    locations = [[51.5, -0.1], [51.6, -0.2], [51.55, -0.15]]
    poly = Polygon(locations, popup="Region info", color="#ff0000", weight=4)
    # After construction:
    # - poly.locations is a list of [lat, lon] float pairs.
    # - poly.options is a dict with camelized Leaflet options (contains color="#ff0000", weight=4, stroke/fill defaults, plus line-specific defaults like smoothFactor).
    # - a Popup child with text "Region info" has been added.

2) Polygon with multiple rings (outer ring + hole):
    outer = [[51.5, -0.1], [51.6, -0.2], [51.55, -0.15]]
    hole = [[51.52, -0.12], [51.53, -0.13], [51.525, -0.115]]
    rings = [outer, hole]   # nested sequence: validate_locations preserves nesting
    poly_with_hole = Polygon(rings, fillColor="#00ff00", fillOpacity=0.5)

3) Typical attachment to a map (MacroElement container API):
    m = Map(...)            # Map is the host container providing add_child
    m.add_child(poly)
    # Rendering and inclusion in the final map HTML/JS is handled by MacroElement/Map rendering logic.

See BaseMultiLocation and path_options documentation for deeper details about location validation/normalization and option defaults respectively.

### `folium.vector_layers.Polygon.__init__` · *method*

## Summary:
Initializes a Polygon MacroElement by validating and storing geographic locations, registering optional Popup/Tooltip children, setting a human-readable element name, and constructing a canonical Leaflet path-options dictionary (with line-specific defaults) from the provided kwargs.

## Description:
Known callers and lifecycle stage:
- Called by application code or tests when creating a polygon-shaped vector layer to add to a Map or other MacroElement container.
- This is part of object construction: invoked when a new Polygon instance is created (before the instance is added to a Map or serialized for rendering).
- Typical lifecycle: Polygon(...) -> map.add_child(polygon) -> MacroElement rendering uses polygon.locations and polygon.options.

Why this logic is a dedicated method:
- The constructor centralizes three responsibilities that belong together at construction time: location validation/normalization (delegated to the base-class constructor and validate_locations), optional child creation for Popup/Tooltip (also handled via the base-class constructor), and standardization of client-side styling options (delegated to path_options with line=True). Keeping this logic in __init__ ensures the instance is ready for serialization immediately after construction.

## Args:
    locations (iterable)
        Required. Iterable of geographic coordinates accepted by validate_locations.
        Accepted shapes:
            - Flat sequence of coordinate pairs: [[lat, lon], [lat, lon], ...]
            - Nested sequences for rings/holes: [[outer_ring], [hole1], ...]
        Constraints:
            - The iterable must be acceptable to validate_locations (iterable, non-empty, leaves indexable and convertible to float).
        Purpose:
            - Provides geometric coordinates that will be normalized/validated and stored on the instance.

    popup (folium.map.Popup | any | None), optional
        Default: None.
        If a Popup instance is provided it is attached as a child. If any other truthy object is provided, it is coerced (wrapped) into a Popup via Popup(str(popup)) as performed by the base-class constructor. If None, no Popup child is added.

    tooltip (folium.map.Tooltip | any | None), optional
        Default: None.
        If a Tooltip instance is provided it is attached as a child. If any other truthy object is provided, it is coerced (wrapped) into a Tooltip via Tooltip(str(tooltip)) as performed by the base-class constructor. If None, no Tooltip child is added.

    **kwargs
        Arbitrary style/display options forwarded to path_options(line=True, **kwargs).
        Behavior:
            - Keys are normalized to canonical camelCase by path_options (via camelize).
            - Common keys: color, fillColor, fill, weight, opacity, fillOpacity, smooth_factor (becomes smoothFactor), no_clip (becomes noClip), etc.
            - Values should be JSON-serializable if the returned options dict will be serialized for front-end rendering.
        Defaults:
            - path_options provides defaults for any omitted styling keys (e.g., color="#3388ff", weight=3, fillOpacity=0.2). Because line=True is passed, line-specific defaults (smoothFactor=1.0, noClip=False) are included.

## Returns:
    None
    - This is an initializer: it returns None and mutates the instance state so the object is ready for use/serialization.

## Raises:
    - Exceptions raised by validate_locations (propagated)
        * TypeError: if locations is not iterable or contains non-indexable leaves.
        * ValueError: if locations is empty or a leaf coordinate has incorrect shape or invalid numeric content.
    - Exceptions raised by Popup or Tooltip construction (propagated)
        * TypeError/ValueError: if the Popup/Tooltip constructors reject the provided argument or string coercion fails.
    - Exceptions raised by path_options or its helpers (propagated)
        * TypeError: if kwargs contain non-string keys that camelize cannot process or other type errors occur during option normalization.
    - Any exceptions propagated from MacroElement.__init__ or BaseMultiLocation.__init__ (propagated)
        * These include internal assertion or type errors raised by the MacroElement/parent constructors.

## State Changes:
Attributes READ:
    - None of this constructor's statements read previously-stored instance attributes (it delegates construction/assignment to the base-class constructor and utilities). (The method reads no existing self.<attr> values.)

Attributes WRITTEN:
    - self.locations
        * Set by the base-class constructor (BaseMultiLocation.__init__) to the return value of validate_locations(locations). The resulting structure is the validated/normalized coordinate list (preserves nested rings where provided).
    - self._name
        * Set to the literal string "Polygon".
    - self.options
        * Set to the dict returned by path_options(line=True, **kwargs). This dict contains canonical camelCase Leaflet option names and defaulted values appropriate for polygon rendering.
    - MacroElement child container (e.g., self._children or equivalent)
        * Potentially modified if popup or tooltip were supplied: Popup/Tooltip instances are added as children by the base-class constructor.

## Constraints:
Preconditions (caller must ensure):
    - locations must be an iterable in a shape acceptable to validate_locations (not an empty iterable; leaves must be indexable and convertible to floats).
    - kwargs must use keys usable by camelize (prefer string keys); values should be JSON-serializable if options will be serialized.
    - If popup/tooltip are non-None and not already Popup/Tooltip instances, they should be coercible to strings (str(popup)/str(tooltip)).

Postconditions (guarantees after return):
    - self.locations equals the validated list returned by validate_locations(locations).
    - self._name == "Polygon".
    - self.options is a plain dict produced by path_options(line=True, **kwargs) and contains canonical camelCase styling keys with defaults applied.
    - If popup or tooltip were provided, the instance has corresponding Popup/Tooltip child elements attached (accessible via the MacroElement child APIs).

## Side Effects:
    - No I/O, network calls, or global state mutation are performed.
    - The constructor mutates the instance (writes attributes described above) and may modify the MacroElement child container by adding Popup/Tooltip children.
    - No other objects outside the instance and the newly created child elements are mutated.

## Implementation Notes (for reimplementation):
    - Sequence must be:
        1. Call the base-class constructor with (locations, popup=popup, tooltip=tooltip) so that validate_locations is used and children are attached consistently with other multi-location layers.
        2. Set self._name to "Polygon".
        3. Build self.options by calling path_options(line=True, **kwargs).
    - Do not attempt to revalidate locations after base-class construction; rely on that centralized validation.
    - Do not inline option normalization: call the shared path_options utility to ensure consistent defaulting and key camelization across vector layers.

## `folium.vector_layers.Rectangle` · *class*

## Summary:
Represents a rectangular vector layer defined by a collection of boundary coordinates (typically two opposite corners). Stores validated boundary locations (delegated to BaseMultiLocation), a canonical Leaflet-style options dict (constructed for line-like vectors), and optionally attaches a Popup and/or Tooltip as children.

## Description:
Use this class when you need a rectangle-shaped vector element to add to a Folium-style map as a MacroElement. Rectangle subclasses BaseMultiLocation and its responsibilities are narrowly focused:

- Delegate location validation and normalization to BaseMultiLocation (which calls validate_locations).
- Use path_options(line=True, **kwargs) to produce a canonical dictionary of Leaflet-style rendering options for the rectangle.
- Set the element name to "rectangle" so the MacroElement/template system can identify and render the element.

Typical callers:
- Code that constructs rectangular overlays from coordinate bounds (for example, two opposite corners [[lat1, lon1], [lat2, lon2]]) and then adds the element to a Map/Figure via the container APIs (e.g., map.add_child(rectangle)). Note: attaching to a Map/Figure is performed by the MacroElement container APIs (external to Rectangle/BaseMultiLocation).

Motivation / Responsibility boundary:
- Rectangle does not perform client-side rendering itself; it prepares the data (locations and options) and children that a MacroElement template will render.
- Rectangle is a focused convenience subclass: it collects validated locations and styling options under the "rectangle" identity for downstream templating and serialization.

## State:
- _template (jinja2.Template)
    - Type: Template
    - Value: class attribute assigned to Template(...) (placeholder Template present on the class).
    - Invariant: Present as a Template instance; rendering content is supplied via this template in the MacroElement system.
- _name (str)
    - Type: str
    - Value: "rectangle"
    - Invariant: Identifies the element type for templating/serialization.
- locations (list)
    - Type: list
    - Source: Assigned in BaseMultiLocation.__init__ by calling validate_locations(bounds).
    - Valid values: non-empty iterable of coordinate pairs normalized to [lat, lon] floats per validate_locations rules.
    - Caller constraints: bounds must be an iterable accepted by validate_locations. A common expected shape is exactly two coordinate pairs representing opposite corners.
    - Invariants:
        - After __init__, self.locations equals the return value of validate_locations(bounds).
        - Each leaf coordinate is a list of two floats when validate_locations succeeds.
- options (dict)
    - Type: dict[str, any]
    - Source: result of path_options(line=True, **kwargs) called inside __init__.
    - Typical keys: stroke, color, weight, opacity, lineCap, lineJoin, dashArray, dashOffset, fill, fillColor, fillOpacity, fillRule, bubblingMouseEvents, and line-specific smoothFactor and noClip.
    - Invariants:
        - Always a dict after __init__.
        - Contains canonical camelCase option names as produced by path_options.
- Popup and Tooltip children
    - Not stored as direct attributes on Rectangle; BaseMultiLocation will add Popup/Tooltip instances as MacroElement children if popup or tooltip were provided.
    - Invariants: If popup/tooltip were provided, corresponding child elements are present among this object's children after construction.

Class invariants:
- self.locations is the validated value produced by validate_locations(bounds).
- self._name == "rectangle".
- self.options is a dict returned by path_options(line=True, **kwargs).
- Popup/Tooltip children exist after construction when requested.

## Lifecycle:
Creation
- Signature: __init__(bounds, popup=None, tooltip=None, **kwargs)
    - bounds (required): An iterable structure acceptable to validate_locations. Typical use: two corner coordinate pairs [[lat1, lon1], [lat2, lon2]].
    - popup (optional): Either a folium.map.Popup instance or any object coercible to str. If not a Popup instance, BaseMultiLocation will wrap it with Popup(str(popup)) and add it as a child.
    - tooltip (optional): Either a folium.map.Tooltip instance or any object coercible to str. If not a Tooltip instance, BaseMultiLocation will wrap it with Tooltip(str(tooltip)) and add it as a child.
    - **kwargs: Arbitrary style options forwarded to path_options(line=True, **kwargs). Keys are normalized with camelize; consult path_options for accepted keys and defaults.
- Construction steps:
    1. Call BaseMultiLocation.__init__(bounds, popup=popup, tooltip=tooltip), which:
         - Calls MacroElement.__init__(),
         - Validates and normalizes bounds via validate_locations and assigns self.locations,
         - Wraps and/or adds popup and tooltip children if provided.
    2. Set self._name = "rectangle".
    3. Compute self.options = path_options(line=True, **kwargs).

Usage
- Common sequence:
    1. Instantiate: rect = Rectangle(bounds, popup="text", color="#ff0000", weight=2)
    2. Optionally inspect or mutate options: rect.options["fill"] = True
    3. Add to a Map/Figure container using MacroElement APIs (e.g., map.add_child(rect)); note that adding to the map is handled by the container's MacroElement integration (external to Rectangle).
    4. Rendering occurs via the MacroElement/template system, which will use rect._template, rect._name, rect.locations, rect.options, and the child's list to produce client-side code.
    5. To get the bounding box, call the inherited helper rect._get_self_bounds().

Destruction / cleanup
- No explicit cleanup implemented. Instances are cleaned up by container lifecycle management or Python garbage collection. There is no close() or context-manager protocol.

## Method Map:
flowchart LR
    A[__init__(bounds, popup=None, tooltip=None, **kwargs)] --> B[BaseMultiLocation.__init__(bounds, popup, tooltip)]
    B --> C[MacroElement.__init__()]
    C --> D[self.locations = validate_locations(bounds)]
    D --> E{popup provided?}
    E -- Yes --> F[Wrap with Popup(str(popup)) or add existing Popup instance via add_child]
    E -- No --> G
    D --> H{tooltip provided?}
    H -- Yes --> I[Wrap with Tooltip(str(tooltip)) or add existing Tooltip instance via add_child]
    H -- No --> G
    G --> J[self._name = "rectangle"]
    J --> K[self.options = path_options(line=True, **kwargs)]
    K --> END[Rectangle ready: children, locations, options present]

## Raises:
Exceptions are propagated from BaseMultiLocation, path_options, and the utilities they use. Explicit conditions include:

During __init__:
- TypeError
    - If bounds is not iterable or otherwise invalid and validate_locations raises TypeError.
    - If kwargs contain non-string keys that camelize (used by path_options) cannot handle.
    - If str(popup) or str(tooltip) raises TypeError while wrapping (rare).
- ValueError
    - If validate_locations raises ValueError (for example, empty iterable or invalid coordinate leaves).
- Exceptions raised by Popup(...) or Tooltip(...) constructors when BaseMultiLocation wraps provided popup/tooltip inputs (e.g., constructor assertions or validation errors).
- Exceptions propagated from MacroElement.__init__ or MacroElement.add_child.

path_options considerations:
- path_options generally does not raise under normal operation, but it relies on camelize (which may raise on invalid key types); such exceptions will propagate.

General guidance:
- Prefer passing bounds as a non-empty iterable of coordinate pairs and use string-like keys for style kwargs to avoid camelize errors. Consult BaseMultiLocation, validate_locations, path_options, Popup and Tooltip documentation for precise error cases and messages.

## Example:
1) Typical creation with two-corner bounds and styling kwargs:
    bounds = [[51.49, -0.08], [51.5, -0.06]]  # two opposite corners (lat, lon)
    rect = Rectangle(bounds, popup="Area info", color="#3388ff", weight=4, fillColor="#3388ff")

    # After construction:
    # - rect.locations contains validated coordinates.
    # - rect._name == "rectangle"
    # - rect.options is a dict produced by path_options(line=True,...)
    # - A Popup child wrapping "Area info" exists (unless a Popup instance was passed).

2) Adding to a map (MacroElement container API, pseudocode):
    my_map.add_child(rect)

3) Inspect bounds via inherited helper:
    bbox = rect._get_self_bounds()
    # bbox is [[min_lat, min_lon], [max_lat, max_lon]] (values or None depending on coordinates)

Notes:
- Rectangle intentionally delegates validation and popup/tooltip wrapping to BaseMultiLocation and option normalization to path_options. For implementation details and exact validation/error semantics, consult those utilities' documentation.

### `folium.vector_layers.Rectangle.__init__` · *method*

## Summary:
Initialize a Rectangle MacroElement by validating and storing its boundary locations, setting the element identity to "rectangle", and computing canonical Leaflet-style rendering options (line-like) from provided style kwargs.

## Description:
This constructor is called when a Rectangle object is created (typically as part of the map-building phase when code constructs geometric overlays). Known callers and contexts:
- User code that creates rectangular overlays from coordinate bounds (for example, rect = Rectangle(bounds, popup="info", color="#ff0000")).
- Followed by adding the instance to a Map/Figure container via the MacroElement API (e.g., my_map.add_child(rect)). The add_child call and later rendering are external to this method.

Lifecycle stage:
- Invoked at object construction time. It is responsible for preparing validated location data and rendering options so the MacroElement/template system can serialize and render the rectangle to client-side Leaflet code.

Why this is a dedicated method:
- Construction requires coordinating validation/wrapping responsibilities from BaseMultiLocation (locations and child Popup/Tooltip handling) and normalization/defaulting responsibilities from path_options. Keeping this logic in __init__ centralizes object initialization semantics and leaves rendering and serialization to the MacroElement/template system.

## Args:
    bounds (iterable)
        Required. An iterable of coordinates acceptable to the shared validate_locations utility.
        Typical: exactly two coordinate pairs representing opposite corners: [[lat1, lon1], [lat2, lon2]].
        Each coordinate pair must be convertible to floats and conform to validate_locations' expectations.
    popup (folium.map.Popup or any)
        Optional, default: None.
        If a Popup instance is provided, it is attached as a child. Otherwise, a non-None value is coerced to str and wrapped in a Popup instance (handled by BaseMultiLocation) and attached as a child.
    tooltip (folium.map.Tooltip or any)
        Optional, default: None.
        If a Tooltip instance is provided, it is attached as a child. Otherwise, a non-None value is coerced to str and wrapped in a Tooltip instance (handled by BaseMultiLocation) and attached as a child.
    **kwargs
        Optional style and rendering keyword arguments forwarded to path_options(line=True, **kwargs).
        Accepted keys (snake_case or camelCase; will be normalized by camelize inside path_options) include but are not limited to:
            - color, stroke, weight, opacity, line_cap/lineCap, line_join/lineJoin,
              dash_array/dashArray, dash_offset/dashOffset,
              fill, fill_color/fillColor, fill_opacity/fillOpacity, fill_rule/fillRule,
              bubbling_mouse_events/bubblingMouseEvents,
              smooth_factor/smoothFactor, no_clip/noClip, gradient
        Note: Keys should be string-like values that camelize() can process.

## Returns:
    None
    The constructor returns None. After completion the instance guarantees that:
        - self.locations contains the validated/normalized coordinate list (set by BaseMultiLocation.__init__).
        - self._name == "rectangle".
        - self.options is a dict produced by path_options(line=True, **kwargs).

## Raises:
    Exceptions are not created by Rectangle.__init__ itself but may propagate from called utilities:
    - TypeError
        - If bounds is not iterable or contains non-coercible leaf values and validate_locations raises TypeError.
        - If kwargs contains keys of types camelize cannot handle (non-string-like), causing camelize to raise.
        - If coercion to str for popup/tooltip fails when wrapping (rare).
    - ValueError
        - If validate_locations rejects the provided bounds (e.g., empty iterable or invalid coordinate structure).
    - Any exception raised by Popup(...) or Tooltip(...) constructors when BaseMultiLocation wraps popup/tooltip inputs will propagate.
    - Any exceptions thrown by path_options (indirectly via camelize) will propagate.

## State Changes:
Attributes READ:
    - None (this __init__ does not read any pre-existing self.<attr> values; it delegates initialization to super()).

Attributes WRITTEN or mutated:
    - self.locations
        - Written by BaseMultiLocation.__init__ invoked via super().__init__(bounds, popup=popup, tooltip=tooltip).
        - Contains the normalized/validated coordinates returned by validate_locations(bounds).
    - self._name
        - Set to the string "rectangle".
        - Used by the MacroElement/template system to identify the element type.
    - self.options
        - Set to the dict returned by path_options(line=True, **kwargs).
        - Holds canonical, camelCase Leaflet-style rendering options.
    - children list / MacroElement children
        - Potentially mutated by BaseMultiLocation.__init__ to add Popup/Tooltip child elements when popup or tooltip arguments are provided.

## Constraints:
Preconditions:
    - bounds must be an iterable acceptable to validate_locations (coordinate leaves convertible to floats).
    - kwargs keys should be string-like so camelize can normalize them.
    - If popup/tooltip are not Popup/Tooltip instances, they should be coercible to strings.

Postconditions:
    - self.locations is set to the validated/normalized bounds (non-empty list of coordinate pairs when validate_locations succeeds).
    - self._name == "rectangle".
    - self.options is a dict containing canonical camelCase option names; includes line-specific options (e.g., smoothFactor, noClip) because path_options was called with line=True.
    - If popup or tooltip were provided, corresponding child MacroElement instances exist among the object's children.

## Side Effects:
    - No I/O, network calls, or global state mutation.
    - May add child MacroElement instances (Popup/Tooltip) to self via BaseMultiLocation.__init__.
    - Exceptions from validate_locations, Popup/Tooltip construction, or path_options may be raised to the caller.

## Implementation notes / edge cases:
    - Passing a 'radius' key in **kwargs is accepted syntactically but radius semantics are not applicable to rectangles; path_options will include a radius key only if a truthy radius argument is passed. Rectangle passes line=True and forwards all kwargs as-is.
    - To avoid camelize-related errors, prefer string keys for style kwargs and use snake_case or camelCase consistently.
    - The heavy lifting of location validation and popup/tooltip wrapping is delegated to BaseMultiLocation; Rectangle's __init__ only orchestrates these calls and sets its own identifying and styling fields.

## `folium.vector_layers.Circle` · *class*

## Summary:
A lightweight subclass of Marker that represents a Leaflet circle overlay by recording a center location and a canonical Leaflet-style options dictionary (including a numeric radius).

## Description:
Circle collects and normalizes the configuration needed to represent a Leaflet Circle (center + radius + styling). It does not implement map rendering itself in this source excerpt; instead it prepares the attributes that the map/serialization layer (the Marker/map integration) will consume.

When to instantiate
- When you need to represent a circular overlay on a map and want a ready-to-serialize object that contains:
  - a center location (forwarded to the Marker base)
  - a numeric radius value (when provided and truthy)
  - a fully-normalized options dict (via path_options)

Why this abstraction exists
- Encapsulates the small, specific responsibility of collecting circle-specific parameters and producing a canonical options dict while reusing Marker behavior for generic marker handling.

Known callers / typical usage
- User code that creates map layers (e.g., map.add_child(Circle(...))).
- Any factory that builds vector overlays using shared utilities like path_options.

Responsibility boundary
- This class prepares identification (_name) and options; it does not itself handle templating/serialization logic beyond providing a Template object attribute (_template) and the options dict.

## State:
Class attributes
- _template (jinja2.Template)
    - Type: Template
    - Value in source: an instance created via Template() (empty template body in the provided source).
    - Constraint: must be a Template instance (the rendering pipeline may expect this attribute to exist).

Instance attributes (set during __init__)
- _name (str)
    - Default/set value: "circle"
    - Purpose: identifies the element type for downstream serialization/templating.
    - Invariant: always the string "circle" after construction.

- options (dict)
    - Type: dict
    - Produced by: path_options(line=False, radius=radius, **kwargs)
    - Guaranteed contents (per path_options contract):
        - Core styling keys: stroke (bool), color (str), weight (int|float), opacity (float), lineCap (str), lineJoin (str), dashArray (str|None), dashOffset (str|None), fill (bool), fillColor (str), fillOpacity (float), fillRule (str), bubblingMouseEvents (bool)
        - Conditionally included: radius (numeric) if the radius argument is truthy; smoothFactor and noClip are not included because line=False; gradient if provided and not None.
    - Key normalization: incoming kwargs keys are camelized (underscore -> camelCase) with first-segment casing preserved. For example, "fill_color" -> "fillColor", "Fill_color" -> "FillColor".
    - Constraints:
        - To include a radius key in options, pass a truthy numeric value for radius. Values False, 0, or None are treated as absent (no radius key).
        - kwargs keys should be string-like values acceptable to camelize; non-string keys may cause camelize to raise.

Additional inherited state
- The constructor forwards location, popup, and tooltip to the Marker superclass. Any attributes set by Marker (e.g., a stored .location) are not redefined here but will exist after super().__init__ completes.

Class invariants
- After construction:
    - self._name == "circle"
    - self.options is a dict following the rules above
    - self._template is a Template instance

## Lifecycle:
Creation
- Signature:
    - location (any) = None
        - Forwarded to Marker.__init__. Valid types are determined by Marker/map expectations (e.g., [lat, lng] lists or (lat, lng) tuples).
    - radius (int | float) = 50
        - If truthy (not 0, False, or None), included in options as options["radius"] = radius.
        - If falsy (0, False, None), options will not include a radius key.
    - popup (any) = None
        - Forwarded to Marker.__init__.
    - tooltip (any) = None
        - Forwarded to Marker.__init__.
    - **kwargs
        - Arbitrary styling and Leaflet options. Keys are normalized via camelize inside path_options.
- Constructor behavior (reimplementation steps):
    1. Call the parent constructor with the forwarded arguments: super().__init__(location, popup=popup, tooltip=tooltip).
    2. Set self._name = "circle".
    3. Compute self.options = path_options(line=False, radius=radius, **kwargs).

Usage
- Typical sequence:
    1. Instantiate: Circle(location=[lat, lon], radius=100, color="#ff0000", fill=True)
    2. Attach to a map or serialize via the surrounding folium/Marker integration (not implemented here).
- No additional Circle-specific methods must be called; there is no required ordering beyond successful construction.

Destruction / cleanup
- No explicit cleanup required by Circle itself. It stores only plain Python objects and a Jinja2 Template instance. Any map-related cleanup is handled by the map/Marker infrastructure.

## Method Map:
flowchart TD
    A[User calls Circle.__init__] --> B[Marker.__init__ called with location,popup,tooltip]
    B --> C[self._name set to "circle"]
    C --> D[path_options(line=False, radius=radius, **kwargs) called]
    D --> E[self.options assigned to returned dict]
    E --> F[Instance ready for map integration/serialization]

## Raises:
- Circle.__init__ does not explicitly raise exceptions in its own body.
- Possible propagated exceptions:
    - Exceptions from path_options (none expected under normal inputs). In particular, camelize called within path_options may raise if kwargs contain non-string/unacceptable keys.
    - Exceptions raised by Marker.__init__ (e.g., TypeError or ValueError if the parent validates location/popup/tooltip types).
- Reimplementation note: if you want fail-fast validation at the Circle level, validate location and radius before calling the parent or before calling path_options.

## Example:
- Creating a circle and inspecting its options (illustrative — path_options behavior used to show expected keys):

1) Create:
  circle = Circle(location=[51.5, -0.1], radius=100, color="#00ff00", fill_color="#00ff00", fill_opacity=0.6)

2) After construction, relevant attributes (approximate representation based on path_options rules):
  circle._name
    -> "circle"

  circle.options
    -> {
         "stroke": True,              # default from path_options
         "color": "#00ff00",          # provided
         "weight": 3,                 # default
         "opacity": 1.0,              # default
         "lineCap": "round",          # default (camelized from line_cap if provided)
         "lineJoin": "round",
         "dashArray": None,
         "dashOffset": None,
         "fill": True,                # because fillColor was provided and truthy
         "fillColor": "#00ff00",
         "fillOpacity": 0.6,
         "fillRule": "evenodd",
         "bubblingMouseEvents": True,
         "radius": 100                # included because radius argument is truthy
       }

Notes
- The exact set of keys and defaults follow the path_options utility contract (see its documentation). To ensure exact parity, call path_options(line=False, radius=..., **kwargs) instead of reimplementing the normalization logic locally.
- Avoid passing non-string keys in kwargs to prevent camelize-related errors.

### `folium.vector_layers.Circle.__init__` · *method*

*No documentation generated.*

## `folium.vector_layers.CircleMarker` · *class*

## Summary:
Represents a Leaflet-style circle marker layer with a single geographic location and styling options. It wraps Marker initialization and produces a normalized Leaflet options dictionary (via path_options) suitable for serializing a circle-style marker to the front end.

## Description:
CircleMarker is a lightweight vector-layer class intended for representing a circle rendered at a single latitude/longitude location. Instantiate this class when you need a small circle marker with configurable visual properties (radius, stroke/fill styling, opacity, etc.) that will be passed through to the underlying frontend Leaflet renderer.

Typical usage scenarios:
- Created directly by application code that builds a map (for example: CircleMarker(location=[lat, lon], radius=5, color="#f00")).
- Used whenever a single-point circular symbol is required and you want fine-grained style options rather than the default map marker icon.

What this class is responsible for:
- Accepting the geometric location and user-provided popup/tooltip and forwarding them to the Marker base class.
- Building a canonical options dict for the circle by calling path_options(line=False, radius=..., **kwargs). This ensures consistent option naming (camelCase), sensible defaults, and inclusion of the numeric radius when provided.

What this class does not do:
- It does not perform map placement itself — that is handled by the Marker base class and the map container that consumes these elements.
- It does not perform network I/O or rendering — it prepares data used by rendering templates.

See also:
- folium.vector_layers.path_options — for the detailed normalization rules and default values applied to styling kwargs.
- Marker (base class) — for semantics related to location, popup, tooltip and how the instance is attached to a map.

## State:
Public / instance attributes created or set in __init__:
- _template (jinja2.Template, class attribute)
    - Value in source: an instance of jinja2.Template (empty template content in the provided source).
    - Role: placeholder template used when the layer is rendered/serialized; left as a Template instance at class scope.
    - Constraints: template content is static as defined on the class; the class-level Template may be used by serialization code that reads it.

- _name (str)
    - Value set in __init__: "CircleMarker"
    - Role: identifies the element type; used by higher-level serialization/registration mechanisms.

- options (dict)
    - Type: dict[str, any]
    - Population: assigned by calling path_options(line=False, radius=radius, **kwargs) inside __init__.
    - Contents: canonical camelCase Leaflet-style rendering options (stroke, color, weight, opacity, fill, fillColor, fillOpacity, etc.), plus radius if the radius argument is truthy, and any other conditionally included keys that path_options returns (gradient, etc.).
    - Invariants:
        - Keys are camelCase (first-segment casing preserved) as produced by path_options.
        - The dictionary always contains the core style keys documented by path_options; radius appears only when the radius parameter passed to __init__ is truthy (non-zero and not False).
        - The values are expected to be JSON-serializable if they will be serialized for frontend rendering.

Inherited state (from Marker):
- location, popup, tooltip (not created explicitly by CircleMarker in the provided code, but forwarded to Marker.__init__). Exact attribute names and semantics are provided by the Marker base class; callers should consult Marker documentation for details.

Class invariants:
- _name == "CircleMarker"
- options is a plain dict constructed by path_options and therefore conforms to the pre/post-conditions of that helper (camelized keys, defaults filled, radius included only when truthy).

## Lifecycle:
Creation:
- Constructor signature:
    __init__(location=None, radius=10, popup=None, tooltip=None, **kwargs)
  - location: value forwarded to the Marker base constructor. Accepts whatever types Marker accepts for a single point (e.g., [lat, lon]); pass None if the concrete Marker semantics allow deferred assignment.
  - radius (int|float|bool): numeric radius value for the circle. Default: 10. If the value is truthy (not False, not 0, not None), path_options will include a "radius" key with this numeric value. If you pass 0 or False, radius is treated as absent by path_options.
  - popup, tooltip: forwarded to Marker.__init__ and handled by the base class.
  - **kwargs: visual/style options forwarded to path_options after normalization via camelize (see path_options docs). Use snake_case or camelCase; path_options normalizes keys.

Usage:
- Immediately after instantiation:
    1. Marker.__init__ is executed (forwarded by super().__init__).
    2. CircleMarker sets self._name and self.options.
- After construction, typical usage is to add the instance to a map/container that knows how to serialize MacroElement-like objects (the broader folium renderer). No additional method calls are required on CircleMarker to create its options.
- There is no required ordering of further method calls specific to CircleMarker itself beyond any ordering required by the Marker base class or the map container.

Destruction / cleanup:
- CircleMarker does not implement explicit cleanup, context management, or close() semantics in the provided source. Any cleanup or removal must be performed by the container or map that manages child elements (see Marker/map documentation for lifecycle management).

## Method Map:
flowchart TD
    A[Caller creates CircleMarker(...)] --> B[CircleMarker.__init__]
    B --> C[super().__init__(location, popup=popup, tooltip=tooltip)  # Marker.__init__]
    B --> D[path_options(line=False, radius=radius, **kwargs)]
    D --> E[self.options = returned dict]
    C --> F[self._name = "CircleMarker"]
    E --> G[instance ready for map/container serialization]

(Notes: The class defines no other instance methods in the provided source. The rendering/serialization step that consumes _template and options is external to this class.)

## Raises:
CircleMarker.__init__ does not explicitly raise exceptions in its body, but the following exceptions may propagate to the caller:
- Any exception raised by Marker.__init__ (e.g., if the base class validates location types or popup/tooltip and raises TypeError/ValueError). Consult the Marker implementation for precise error conditions.
- Any exception raised by path_options:
    - path_options will call camelize on kwargs keys and may raise if non-string/unexpected key types are provided (see path_options documentation).
    - path_options documents it does not explicitly raise under normal operation; unexpected input types (non-string keys, non-JSON-serializable values if serialization is later attempted) may result in propagated exceptions.
- Type errors from mis-typed arguments (for example passing a mapping where a numeric radius is expected) may surface when downstream code assumes certain types; callers should pass numeric radius values when a radius is intended.

## Example:
Example 1 — basic circle marker with default radius:
    Instantiate a circle marker at lat/lon with the default radius:
    - CircleMarker(location=[45.5236, -122.6750])
    Effect:
    - Marker base initializer is called with the location.
    - options will include radius=10 (default) and other styling defaults from path_options.

Example 2 — custom styling and explicit radius:
    Create a small red filled circle without stroke:
    - CircleMarker(location=[lat, lon], radius=4, color="#ff0000", stroke=False, fillColor="#ff0000", fillOpacity=0.6)
    Effect:
    - options will be the normalized dict returned by path_options with radius=4, stroke=False, color="#ff0000", fill=True, fillColor="#ff0000", fillOpacity=0.6.

Example 3 — omit radius:
    If you intentionally want radius omitted, pass 0 or False:
    - CircleMarker(location=[lat, lon], radius=0, color="#00f")
    Effect:
    - path_options treats radius=0 as absent; returned options will not include a "radius" key.

Notes:
- For exact option names, accepted keys, default values, and camelCase normalization rules, see the folium.vector_layers.path_options documentation. Rely on that utility for consistent styling semantics.

### `folium.vector_layers.CircleMarker.__init__` · *method*

## Summary:
Initializes a CircleMarker instance by delegating common marker setup to the Marker constructor, setting the element identity to "CircleMarker", and building a canonical Leaflet-style options dictionary (including a numeric radius) stored on the instance.

## Description:
- Known callers and call context:
    - User code constructing circle markers directly (e.g., CircleMarker((lat, lon), radius=...)) during map composition.
    - Higher-level layer/feature factories or convenience helpers that create CircleMarker instances and add them to a Map or FeatureGroup.
    - Tests and utilities that construct vector-layer instances prior to attaching them to a Map/Figure.
    - Lifecycle stage: invoked at object creation time (construction/initialization) before the instance is attached to any parent element and before rendering.

- Why this is a dedicated __init__ method:
    - Initialization consolidates three related responsibilities that must hold as invariants for the object lifecycle: delegating base Marker initialization (location, popup, tooltip attachment), defining the layer identity, and producing a normalized options dict configured for circle rendering. Keeping this logic in __init__ ensures each CircleMarker instance is ready for attachment and serialization immediately after construction.

## Args:
    location (optional)
        Type: sized, indexable container with two entries (latitude, longitude) — e.g., list/tuple/numpy.ndarray, or any type accepted by Marker.validate_location.
        Default: None
        Notes: If not None, Marker.__init__ will validate and convert this into a list[float] of length 2. Passing None leaves self.location as None.

    radius (int | float, optional)
        Default: 10
        Allowed values: any value treated truthily by Python (non-zero numbers, non-empty objects). path_options treats 0 and False as absent; therefore a numeric 0 will NOT include radius in resulting options.
        Behavior: When truthy, the numeric value is included in the canonical options dict under the "radius" key (path_options handles normalization). Non-numeric but truthy values are passed through to path_options and will appear under "radius" — callers should provide numeric values to match Leaflet expectations.

    popup (optional)
        Type: Popup instance or any object coercible to str
        Default: None
        Behavior: If provided, Marker.__init__ will attach the Popup instance directly, or coerce non-Popup values via Popup(str(popup)) before attaching.

    tooltip (optional)
        Type: Tooltip instance or any object coercible to str
        Default: None
        Behavior: Similar to popup — attached or coerced via Tooltip(str(tooltip)).

    **kwargs
        Type: mapping of style/behavior options (string keys expected)
        Behavior: Arbitrary Leaflet-style options may be supplied in snake_case or camelCase. These are forwarded to path_options(...) which:
            - camelizes keys,
            - applies defaults for stroke/fill/weight/etc.,
            - conditionally includes the radius key when radius is truthy,
            - omits entries whose value is exactly None.
        Important: Use string keys (or values acceptable to camelize). See folium.vector_layers.path_options for the canonical list of accepted styling keys and defaults.

## Returns:
    None
    - The constructor does not return a value; it mutates the instance so it is ready for use.

## Raises:
    - Any exception raised by Marker.__init__ (propagated):
        * TypeError or ValueError from location validation if location is invalid (e.g., wrong shape, non-numeric values).
        * Exceptions from Popup(...) or Tooltip(...) constructors if coercion fails.
        * Exceptions from add_child(...) while attaching children (propagated).
    - Exceptions propagated from path_options(...) or its helpers:
        * Errors from camelize if non-string/unexpected key types are used.
        * (No new exceptions are raised by this method itself; it forwards exceptions from its callees.)

## State Changes:
Attributes READ:
    - None directly from this method body. (It calls super().__init__(), which may read/initialize base state as described in Marker.__init__.)

Attributes WRITTEN:
    - self._name (str): set to "CircleMarker" (overrides the base-class name set by Marker.__init__).
    - self.options (dict): set to the dict returned by path_options(line=False, radius=radius, **kwargs). This canonical dict contains camelCased Leaflet options and may include "radius" when radius is truthy.
    - other attributes written by the base Marker constructor (via super().__init__):
        * self.location: set to the validated coordinate list or None.
        * child attachments (popup / tooltip): Popup/Tooltip instances attached to self (added to self._children and having their _parent set to this instance), if popup/tooltip were provided or coerced.
    - Note: Because this __init__ reassigns self.options after calling super().__init__, any options originally set by Marker.__init__ are replaced by the result of path_options.

## Constraints:
Preconditions:
    - If a location is provided, it must meet Marker.validate_location expectations: sized, indexable, length 2, and coordinates convertible to float (not NaN).
    - kwargs keys should be string-like values acceptable to camelize; non-string keys may raise in camelize/path_options.
    - popup/tooltip non-instance values must be coercible to str if they will be wrapped by Popup/Tooltip.
    - If you need a radius to appear in the front-end payload, pass a truthy numeric value (avoid 0 or False).

Postconditions:
    - After initialization:
        * self._name == "CircleMarker"
        * self.location is either a list[float] of length 2 (if location provided and validated) or None
        * self.options is a camelCased dict appropriate for Leaflet circle rendering, containing styling keys and (when radius is truthy) a "radius" entry with the provided value. It replaces any options produced by the base Marker constructor.
        * popup/tooltip, if provided, are attached as child elements of this CircleMarker instance.

## Side Effects:
    - Mutates the CircleMarker instance (attributes listed above).
    - May mutate child objects by attaching them (set child's _parent and add to this instance's children collection) via Marker.__init__.
    - No I/O, filesystem, or network operations are performed by this method itself.
    - External effects derive from callees: path_options performs in-memory transformations only; Popup/Tooltip constructors and add_child mutate element objects and the element tree.

## Implementation notes / edge cases:
    - Radius handling: path_options treats 0 and False as absence of radius; to include a radius you must pass a truthy value (e.g., 10). Non-numeric truthy radii are passed through but may lead to invalid front-end behavior.
    - Options behavior: this constructor delegates option normalization entirely to path_options(line=False, ...). Any kwargs whose value is None will be omitted from the final self.options dict.
    - Ordering: super().__init__ is invoked first to perform standard Marker setup (location validation and popup/tooltip attachment). This method then overwrites self._name and self.options to reflect CircleMarker semantics.
    - For full details of the canonical styling keys, defaults, and camelization rules, see folium.vector_layers.path_options documentation.

