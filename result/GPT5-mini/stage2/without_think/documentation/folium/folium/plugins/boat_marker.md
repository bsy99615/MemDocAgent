# `boat_marker.py`

## `folium.plugins.boat_marker.BoatMarker` · *class*

## Summary:
A folium map marker that represents a boat with optional heading and wind data, and which automatically registers the client-side leaflet.boatmarker JavaScript resource when rendered.

## Description:
BoatMarker is a small plugin-style Marker subclass that augments a standard map marker with boating-related attributes: heading, wind_heading, and wind_speed. It mixes in JSCSSMixin so that the external JavaScript implementation (leaflet.boatmarker) is included in the HTML document head when the element is rendered as part of a Figure/Map.

Typical usage scenarios:
- Place a boat-like marker on a folium Map where you want to visualize the vessel's orientation (heading) and optionally wind direction/speed.
- Use when a front-end JavaScript plugin (leaflet.boatmarker) is required; BoatMarker ensures that plugin's JS URL is registered with the Figure header before rendering.

Known callers / creation sites:
- Constructed by application code that creates folium markers for display on a Map/Figure. After construction, the instance is expected to be attached to the document root (Map/Figure) via the library's element-tree API (for example, Map.add_child(element) or element.add_to(map)) so that rendering can occur.

Motivation and responsibility:
- Responsibility: capture and store boat-specific metadata (heading, wind_heading, wind_speed) and provide the required resource hook (via default_js) so the leaflet.boatmarker client library is available at render time.
- Boundary: BoatMarker does not itself implement rendering templates in Python beyond storing options and declaring the JS dependency; actual HTML/JS emission is performed by the Element/Marker rendering pipeline and the JSCSSMixin resource registration.

## State:
Attributes set by __init__:
- _name (str)
    - Value set to "BoatMarker".
    - Invariant: remains the identity name used by Element/Marker systems.
- heading (int | float)
    - Default: 0
    - Semantics: user-supplied numeric orientation for the boat. The class stores the value as provided; no validation is performed here.
    - Valid values: any numeric value accepted by callers; no clamping or normalization is applied by this class.
- wind_heading (int | float | None)
    - Default: None
    - Semantics: optional numeric heading for wind. None indicates "no wind heading provided".
- wind_speed (int | float)
    - Default: 0
    - Semantics: optional numeric wind speed. Stored as-provided; no units are enforced by this class.
- options (dict[str, Any])
    - Populated by parse_options(**kwargs).
    - Contents: camelCased keys derived from kwargs (snake_case converted to camelCase) with any entries whose value was None removed.
    - Example: passing color='red', max_zoom=12 -> options {'color': 'red', 'maxZoom': 12}
Class attributes:
- _template (jinja2.Template)
    - Present but empty in this source. Actual rendering behavior is provided by the Marker/Element rendering pipeline.
- default_js (list[tuple[str, str]])
    - Contains a single pair:
        ("markerclusterjs", "https://unpkg.com/leaflet.boatmarker/leaflet.boatmarker.min.js")
    - This list is consumed by JSCSSMixin during rendering to register the external JS library in the Figure header.

Class invariants:
- options is a dict with no values equal to None (parse_options drops None-valued kwargs).
- _name equals "BoatMarker".
- default_js remains iterable of 2-tuples so JSCSSMixin can iterate and register resources.

## Lifecycle:
Creation:
- Instantiate with required and optional parameters:
    - location (required): a location object accepted by the Marker base class (commonly a (lat, lon) pair or similar). This class forwards location to its Marker superclass.
    - popup (optional): forwarded to Marker.
    - icon (optional): forwarded to Marker.
    - heading (optional, default 0): numeric heading value.
    - wind_heading (optional, default None): numeric or None.
    - wind_speed (optional, default 0): numeric value.
    - **kwargs: arbitrary option names/values that will be normalized via parse_options and stored on self.options.
- Example constructor call:
    BoatMarker(location=(lat, lon), heading=45, wind_speed=5, color='blue')

Usage:
1. Instantiate BoatMarker with required location and any desired metadata.
2. Attach the instance to a Map/Figure using the application/library element-tree API (for example Map.add_child or element.add_to(map)).
3. When the element is rendered as part of the root Figure:
    - JSCSSMixin will register entries from default_js into the Figure.header (so the client-side leaflet.boatmarker script becomes available).
    - The standard Marker/Element render sequence will serialize the marker and its options to HTML/JS. The BoatMarker instance's heading/wind_* attributes and options are available to that serialization process.

Destruction / cleanup:
- BoatMarker does not define any special cleanup or context-manager behavior. Resource registration is handled on render by JSCSSMixin and persists on the Figure/header. Removal of elements or header entries, if desired, must be handled by the host Figure/Map API.

## Method Map:
flowchart LR
    A[Instantiate BoatMarker] --> B[__init__]
    B --> C[super().__init__(location,popup=...,icon=...)]
    B --> D[set heading, wind_heading, wind_speed]
    B --> E[options = parse_options(**kwargs)]
    E --> F[store options dict on instance]
    A --> G[Attach to Map/Figure via element-tree API]
    G --> H[Figure.render()]
    H --> I[JSCSSMixin.render() registers default_js in Figure.header]
    I --> J[Marker/Element rendering serializes marker and options to HTML/JS]

Notes:
- The class itself exposes no additional public methods beyond what it inherits. The key interactions are the __init__ path and the render-time behavior provided by JSCSSMixin and Marker.

## Raises:
Exceptions that may propagate from __init__:
- Any exception raised by the Marker superclass __init__ (propagated as-is). Because Marker is not shown here, concrete exceptions are not enumerated in this document.
- Exceptions from parse_options(**kwargs):
    - If kwargs contains keys that are not valid inputs for the underlying camelize function, parse_options may raise TypeError or AttributeError. These exceptions propagate up through BoatMarker.__init__.
    - If kwargs include keys which cause camelization collisions that the application does not expect, the later key will overwrite the earlier one; this is not an exception but a potential gotcha.
- No explicit ValueError/AssertionError is raised by BoatMarker.__init__ itself in this source.

## Example:
- Create a BoatMarker, attach it to a map, and render (conceptual steps; actual map APIs may differ):

    1) Construct:
        marker = BoatMarker(location=(51.5, -0.1), heading=90, wind_heading=120, wind_speed=8, color='red')

    2) Attach to a Map/Figure (library-specific API):
        # e.g., map.add_child(marker) or marker.add_to(map)

    3) Render the Map/Figure:
        # The rendering process will cause:
        # - JSCSSMixin to register the leaflet.boatmarker JS file in the Figure header
        # - Marker/Element rendering to serialize the marker and include the heading/wind/options in emitted HTML/JS

Notes and best practices:
- Provide numeric headings and speeds in the units your front-end/plugin expects; BoatMarker performs no unit conversion or validation.
- Use keyword options that are valid for the client-side plugin; pass them as kwargs to the constructor (they will be camelCased by parse_options).
- Avoid passing non-string keys in kwargs (parse_options assumes string-like keys; non-string keys may raise).
- Because default_js is declared at class level and used by JSCSSMixin, do not mutate BoatMarker.default_js at runtime.

### `folium.plugins.boat_marker.BoatMarker.__init__` · *method*

## Summary:
Initializes a BoatMarker instance by delegating base marker setup to the Marker constructor, storing boat-specific metadata (heading, wind_heading, wind_speed), and normalizing any additional keyword options into self.options.

## Description:
- Known callers and call context:
    - Constructed directly by application code or libraries when creating markers for a folium Map/Figure. Typical lifecycle: instantiate BoatMarker during the element-creation stage, then attach the instance to a Map/Figure (for example map.add_child(marker) or marker.add_to(map)) before rendering.
    - This __init__ is invoked at object creation time (before render) to establish instance invariants required by the rendering pipeline.

- Why this logic is a distinct method:
    - Initialization separates concerns: the base Marker.__init__ handles geographic/location normalization and child attachment (icon/popup), while BoatMarker.__init__ focuses on boat-specific state and option normalization. Keeping this logic here keeps construction cohesive and ensures the client-side boat plugin receives a consistent options payload when the element is serialized.

## Args:
    location (Any sized, indexable container):
        - Required positional argument.
        - Expected shape: an indexable container with two entries (latitude, longitude), e.g., tuple (lat, lon), list, numpy array.
        - Behavior: forwarded to Marker.__init__ which validates/normalizes it (validate_location). If None is passed, Marker.__init__ will set self.location = None.
    popup (Optional[Popup | Any], default=None):
        - Optional. If a Popup instance is provided it is attached as a child via Marker.__init__; if a non-Popup object is provided, Marker.__init__ typically coerces it (e.g., Popup(str(popup))).
    icon (Optional[element-like], default=None):
        - Optional. An element-like object (commonly an Icon) that, when provided, will be attached as a child of the Marker by Marker.__init__.
    heading (int | float, default=0):
        - Numeric orientation of the boat in degrees (or the unit expected by the front-end plugin). Stored as-provided; no validation or normalization is performed here.
    wind_heading (int | float | None, default=None):
        - Optional numeric wind heading; None indicates no wind heading supplied.
    wind_speed (int | float, default=0):
        - Numeric wind speed (units are not enforced by this class).
    **kwargs:
        - Arbitrary keyword options intended for the client-side plugin or marker customization.
        - Keys are expected to be string-like Python identifiers (snake_case typical). They are normalized by parse_options into camelCase keys and entries whose value is exactly None are omitted from the resulting dict.
        - Examples: color='red', max_zoom=12 -> options becomes {'color': 'red', 'maxZoom': 12}.

## Returns:
    None

## Raises:
    - Any exception raised by Marker.__init__ (propagated unchanged), including but not limited to:
        * TypeError or ValueError from location validation if the provided location is malformed or contains invalid/non-numeric coordinates.
        * Exceptions raised during popup/icon coercion or attachment (for example, errors from Popup/Icon constructors or from add_child).
    - Any exception raised by parse_options(**kwargs) (propagated unchanged), commonly:
        * AttributeError or TypeError if kwargs contains non-string-like keys that the camelize routine cannot process.
    - No new exceptions are raised explicitly by BoatMarker.__init__; it forwards exceptions from its calls.

## State Changes:
Attributes READ:
    - None of this method's own lines read existing self attributes for conditional logic. (It calls super().__init__ which may read/initialize base-class state internally.)

Attributes WRITTEN:
    - self._name (str):
        - Set to "BoatMarker", overriding the identity potentially set by the Marker base class.
    - self.heading (int | float):
        - Set to the provided heading argument (default 0).
    - self.wind_heading (int | float | None):
        - Set to the provided wind_heading argument (default None).
    - self.wind_speed (int | float):
        - Set to the provided wind_speed argument (default 0).
    - self.options (dict[str, Any]):
        - Set to the result of parse_options(**kwargs): keys are camelCased, and any entries whose value was exactly None are omitted.
        - Note: Marker.__init__ is called first and may initialize its own self.options; BoatMarker.__init__ then overwrites self.options with the normalized kwargs provided to BoatMarker.

Additional, indirect mutations (via super().__init__):
    - self.location, child attachments, and possibly other Marker attributes are initialized by Marker.__init__. If popup or icon were provided, they will be coerced/attached and their parent/child relationships mutated by the element framework.

## Constraints:
Preconditions:
    - location must satisfy Marker.validate_location expectations (sized, indexable, length 2, numeric coordinate values) if a concrete coordinate is required by downstream code.
    - kwargs keys should be string-like and acceptable to the camelize function used by parse_options; passing non-string or malformed keys risks AttributeError/TypeError.
    - popup/icon, if provided, must be valid for Marker.__init__ coercion/attachment (e.g., icon should be an element-like object the element-tree accepts).

Postconditions:
    - After returning successfully:
        * self._name == "BoatMarker"
        * self.heading equals the provided heading value
        * self.wind_heading equals the provided wind_heading value (possibly None)
        * self.wind_speed equals the provided wind_speed value
        * self.options is a dict with camelCased keys (derived from kwargs) and contains no entries whose value is None
        * The base-class initialization side effects (such as validated self.location and attached popup/icon children) have been applied by Marker.__init__ prior to BoatMarker-specific assignments.

## Side Effects:
    - Calls Marker.__init__(location, popup=popup, icon=icon) which:
        * Validates and normalizes location (may allocate memory or raise on invalid input).
        * May coerce and attach popup/icon child elements (mutating those objects and the marker's element tree).
    - Calls parse_options(**kwargs) which performs pure in-memory normalization (camelCase conversion and None-filtering); parse_options itself does not perform I/O or network calls but may raise on invalid keys.
    - No network, file I/O, or external service calls are performed directly by this method.

