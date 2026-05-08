# `semicircle.py`

## `folium.plugins.semicircle.SemiCircle` · *class*

## Summary:
Represents a Leaflet semicircle marker layer: a circular sector centered at a geographic location, described either by (direction, arc) or by (start_angle, stop_angle), with styling and radius options prepared for front-end rendering.

## Description:
Instantiate this class to place a semicircle (a portion of a circle) on a Folium/Leaflet map. It prepares normalized options and registers the external leaflet-semicircle JavaScript asset (via the JSCSSMixin rendering pipeline) so the browser can draw the semicircle using the plugin.

Scenarios to instantiate:
- When you need to visualize directional coverage, field-of-view, or any radial sector centered on a map point.
- Typical flow: create the SemiCircle, add it to a Map/Figure (e.g., map.add_child(...)), then render the map. The element's rendering will include registering the plugin JS and emitting the semicircle geometry and options.

Motivation and responsibility:
- Responsibility: hold the data needed to render a semicircle and prepare a normalized options dictionary using shared utilities (path_options and parse_options).
- Resource registration: SemiCircle declares the required JS asset in its class attribute default_js. The JSCSSMixin (mixed in) is responsible for registering the class's default_js entries with the Figure header at render time; JSCSSMixin's own class-level default_js is empty by default, but subclasses provide their own lists.

## State:
- Class attributes:
    - _template (jinja2.Template): placeholder template used by the Element rendering pipeline (empty here).
    - default_js (list[tuple[str, str]]): The semicircle plugin script declared on this class:
        - Value: [("semicirclejs", "https://cdn.jsdelivr.net/npm/leaflet-semicircle@2.0.4/Semicircle.min.js")]
        - Invariant: an iterable of (name, url) pairs; JSCSSMixin will register these on the Figure header when the element is rendered.

- Instance attributes set by __init__:
    - _name (str): set to "SemiCircle".
    - direction (tuple[float, float] | None):
        - When direction and arc are provided together: (direction, arc).
        - Otherwise: None.
        - Invariant: direction is non-None exactly when arc is non-None and start_angle/stop_angle are both None.
    - options (dict[str, Any]):
        - Built from path_options(line=False, radius=radius, **kwargs) then updated with parse_options(start_angle=..., stop_angle=...).
        - Keys are camelCase (as produced by those utilities) and include style and geometry options accepted by the front-end plugin (for example: color, fillColor, fill, stroke, weight, opacity, fillOpacity, radius when provided, and startAngle/stopAngle when provided).
        - Invariant: startAngle/stopAngle appear in options only when the corresponding __init__ parameters were provided (parse_options omits None).

Notes on types and constraints:
- The class does not itself coerce types; path_options and parse_options handle key normalization and omission of None values. Numeric expectations (for radius and angles) are not strictly enforced in __init__; invalid types will likely fail during serialization or in the front-end plugin.
- For precise expectations and validation of location, consult the Marker/Element base class (location handling/validation is delegated to the superclass).

## Lifecycle:
- Creation:
    - Signature:
        SemiCircle(location, radius, direction=None, arc=None, start_angle=None, stop_angle=None, popup=None, tooltip=None, **kwargs)
    - Required:
        - location: passed to the Marker superclass (the base class is responsible for any validation about shape/type).
        - radius: a value supplied to path_options; if falsy (0, False, None) path_options treats radius as absent.
    - Angle specification rule (mutual exclusivity):
        - Valid if and only if the following holds (pseudologic):
            (direction is None and arc is None and start_angle is not None and stop_angle is not None)
            OR
            (direction is not None and arc is not None and start_angle is None and stop_angle is None)
        - If this is not satisfied, __init__ raises ValueError.
- Usage:
    1. Instantiate with one of the two allowed angular specifications and any style kwargs.
    2. Add to a Map/Figure or call add_to(map).
    3. On render:
        - JSCSSMixin registers the entries in SemiCircle.default_js with the Figure header so the plugin script is included in the document head.
        - The Element rendering pipeline emits the semicircle parameters (location and options) to the front end.
- Destruction:
    - No explicit cleanup. Resource registration is handled at render time by the Figure header; removal is the host's responsibility.

## Method Map:
flowchart LR
    A[User] --> B[Instantiate SemiCircle(...)]
    B --> C[Marker.__init__(location, popup, tooltip)]
    C --> D[set _name = "SemiCircle"]
    D --> E[direction = (direction, arc) or None]
    E --> F[options = path_options(line=False, radius=radius, **kwargs)]
    F --> G[options.update(parse_options(start_angle=..., stop_angle=...))]
    G --> H[validate exclusivity of angle arguments -> raise ValueError if invalid]
    H --> I[instance ready]
    I --> J[Add to Figure/Map]
    J --> K[Figure.render triggers element.render]
    K --> L[JSCSSMixin registers SemiCircle.default_js on Figure.header]
    L --> M[Element rendering emits semicircle with location and options]

## Raises:
- ValueError:
    - Raised by __init__ when the caller does not provide exactly one of the two allowed angle specifications. Concretely, if the boolean condition described in Lifecycle under "Angle specification rule" is false, the constructor raises:
      "Invalid arguments. Either provide direction and arc OR start_angle and stop_angle"
- Propagated exceptions:
    - Exceptions from path_options or parse_options (for example, errors from camelize when keys are not strings) will propagate.
    - Exceptions from the Marker/Element superclass (for example, invalid location) will propagate.

## Example:
- Using direction and arc:
    1. Create:
        sem = SemiCircle(location=(37.77, -122.42), radius=200, direction=45, arc=90, color="#3388ff", fill=True)
    2. Add to map:
        m.add_child(sem)  # or sem.add_to(m)
    3. Render the map. On render, the leaflet-semicircle JS (declared on the class) will be registered via JSCSSMixin and the semicircle will be drawn using sem.options and sem.location.

- Using start/stop angles:
    1. Create:
        sem2 = SemiCircle(location=(37.77, -122.42), radius=150, start_angle=0, stop_angle=180, fillColor="#00ff00", fillOpacity=0.4)
    2. Add and render as above.

Notes and best practices:
- Provide either (direction, arc) or (start_angle, stop_angle), never both or neither.
- Prefer supplying numeric types (int/float) for radius and angles; the class does not perform numeric validation itself.
- For details on valid location formats and behavior of popup/tooltip parameters, refer to the Marker/Element base class documentation.
- If you need to customize or override the JS/CSS resources, override the class attributes default_js/default_css on a subclass rather than mutating them at runtime.

### `folium.plugins.semicircle.SemiCircle.__init__` · *method*

## Summary:
Initializes a SemiCircle instance by forwarding location and popup/tooltip to the Marker superclass, preparing normalized rendering options (including radius and angle parameters), storing the directional or angular specification, and validating that exactly one style of angle specification is provided.

## Description:
Known callers and invocation context:
- Typically invoked directly by application code when creating a semicircle layer to add to a Folium map (for example: SemiCircle(...); then map.add_child(instance) or instance.add_to(map)).
- Invoked during the object construction phase (the constructor call); it runs before the element is attached to a Map/Figure and before any rendering/JS registration occurs.

Why this logic is a separate method:
- Encapsulates constructor-specific responsibilities: forwarding base-class initialization (location, popup, tooltip), building and normalizing the options dict using shared utilities (path_options and parse_options), and enforcing the mutual-exclusivity rule for angle specification.
- Keeps higher-level code and rendering logic focused on lifecycle and resource registration; option normalization and validation belong in the initializer where instance state is established.

## Args:
    location (Any)
        - Passed unchanged to the Marker superclass constructor. The Marker/Element base class is responsible for any validation or normalization of accepted location formats (e.g., lat/lng tuples).
        - Required.
    radius (Any)
        - Passed to path_options as the radius argument; path_options treats falsy values (e.g., False, 0, None) as absent and will omit a radius entry from the resulting options in that case.
        - Expected to be a numeric value (int or float) when a radius is intended, but the constructor does not coerce or strictly validate the numeric type.
        - Required (the parameter must be supplied in the call signature; semantically a semicircle without a radius is unusual but allowed if radius is falsy).
    direction (float | int | None, optional)
        - Direction angle in degrees (centered direction for the semicircle) when using the (direction, arc) specification.
        - Default: None.
    arc (float | int | None, optional)
        - Arc width in degrees paired with direction to define the semicircle sector.
        - Default: None.
    start_angle (float | int | None, optional)
        - Start angle (degrees) when using the (start_angle, stop_angle) specification.
        - Default: None.
    stop_angle (float | int | None, optional)
        - Stop angle (degrees) paired with start_angle.
        - Default: None.
    popup (Any, optional)
        - Passed to Marker.__init__ and handled by the base class (e.g., Popup content or object).
        - Default: None.
    tooltip (Any, optional)
        - Passed to Marker.__init__ and handled by the base class (e.g., Tooltip content or object).
        - Default: None.
    **kwargs
        - Arbitrary styling and rendering keyword options forwarded to path_options (which camel-cases keys and applies defaults). Examples include color, fill, fillColor, weight, opacity, etc.
        - Keys should be strings acceptable to the path_options utility (path_options will camelize keys and may raise if keys are non-string types).

## Returns:
    None
    - As a constructor, it does not return a value; it initializes instance state or raises on invalid arguments.

## Raises:
    ValueError
        - Raised when the provided angle arguments do not satisfy the mutual-exclusivity rule. Concretely, the constructor accepts exactly one of these two specification styles:
            1) Provide both direction and arc, and leave start_angle and stop_angle as None.
            2) Provide both start_angle and stop_angle, and leave direction and arc as None.
        - If the call does not match one of the above valid forms (for example: only direction provided, or direction+arc and start_angle provided, or none of the pairs provided), the constructor raises:
            "Invalid arguments. Either provide direction and arc OR start_angle and stop_angle"
    Propagated exceptions
        - Exceptions raised by the Marker superclass (e.g., invalid location handling) will propagate unchanged.
        - Exceptions from path_options or parse_options (for instance, errors due to non-string kwargs keys or other internal checks) will propagate.

## State Changes:
Attributes READ:
    - None of self.* attributes are read prior to assignment in this method. The method relies on parameters and on calling the superclass constructor.

Attributes WRITTEN:
    - self._name (str)
        - Set to "SemiCircle".
    - self.direction (tuple[float|int, float|int] | None)
        - Set to (direction, arc) when both direction and arc are provided; otherwise set to None.
    - self.options (dict[str, Any])
        - Initially assigned the result of path_options(line=False, radius=radius, **kwargs) and then updated with the dict returned by parse_options(start_angle=start_angle, stop_angle=stop_angle). The final dict contains camelCase option keys and omits entries whose values were None (as per parse_options behavior).
    - Additionally, calling super().__init__(location, popup=popup, tooltip=tooltip) causes the Marker/Element base class constructor to set its own attributes on self (for example: attributes that represent location, popup, tooltip), but those are managed by the base class, not by this method directly.

## Constraints:
Preconditions:
    - The caller must supply a location and radius argument in the constructor call signature.
    - For angle specification, the caller must satisfy exactly one of these:
        * Both direction and arc are not None, and both start_angle and stop_angle are None.
        * Both start_angle and stop_angle are not None, and both direction and arc are None.
    - Keyword argument keys passed via **kwargs should be strings or otherwise acceptable to path_options and camelize; non-string keys may raise exceptions from those utilities.

Postconditions:
    - If no exception is raised:
        * self._name == "SemiCircle"
        * self.direction is either a 2-tuple (direction, arc) when direction/arc were provided, or None when start/stop angles were used.
        * self.options is a dict produced by path_options(line=False, radius=radius, **kwargs) and updated with parse_options(start_angle=..., stop_angle=...), thus containing normalized (camelCase) option names with None-valued options omitted.
        * The object is properly constructed and ready to be added to a Map/Figure for rendering; the semicircle parameters for rendering are available in self.location (set by Marker) and self.options.

## Side Effects:
    - Calls Marker.__init__(location, popup=popup, tooltip=tooltip), which mutates the instance (setting location/popup/tooltip-related attributes) and may perform base-class validation. Any side effects of the base class constructor (including raising exceptions) will occur.
    - Calls path_options and parse_options to build self.options; these functions are pure transformations (no I/O) but may raise exceptions (for instance if kwargs keys are not strings and camelize fails).
    - No I/O, network access, or global state mutation is performed directly by this method. The registration of external JS/CSS assets for SemiCircle is handled by JSCSSMixin at render time, not during __init__.

