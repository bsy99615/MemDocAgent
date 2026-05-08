# `polyline_offset.py`

## `folium.plugins.polyline_offset.PolyLineOffset` · *class*

## Summary:
A Folium plugin Element representing a Leaflet polyline that supports a client-side "offset" option and automatically registers the leaflet-polylineoffset JavaScript asset when rendered.

## Description:
PolyLineOffset is a lightweight subclass of PolyLine that mixes in JSCSSMixin to ensure the leaflet-polylineoffset client-side library is included in the Figure header before rendering. Instantiate this class when you want the standard PolyLine behavior (validated locations, canonicalized rendering options, optional popup/tooltip children) plus a per-polyline offset value that will be passed to the frontend plugin.

Typical scenarios:
- Creating a map layer that should render a polyline displaced from its original path on the client (for visual separation of overlapping lines).
- Replacing PolyLine in code that requires the leaflet-polylineoffset plugin without changing further rendering or styling logic.

Known callers / factories:
- Any map- or layer-building code that currently instantiates folium.vector_layers.PolyLine and needs an offset capability; typical usage is map.add_child(PolyLineOffset(...)).
- The class is safe to use anywhere a PolyLine instance is accepted by the MacroElement container APIs.

Motivation / responsibility boundary:
- Responsibility: extend PolyLine by attaching an "offset" option into the element's options dictionary and declare the required client-side JS asset so the frontend library is available at render time.
- Boundary: PolyLineOffset does not implement rendering or client-side offset logic — it only prepares the server-side element state and resource declarations. The actual offset behavior is implemented by the leaflet-polylineoffset JavaScript loaded into the page.

## State:
- Class attributes
    - default_js: list[tuple[str, str]]
        - Type: list of (name, url) pairs
        - Default value in this class:
            [("polylineoffset", "https://cdn.jsdelivr.net/npm/leaflet-polylineoffset@1.1.1/leaflet.polylineoffset.min.js")]
        - Purpose: Declares the external JS resource that JSCSSMixin will register on the Figure.header when the element is rendered.
        - Invariant: Iterable of 2-tuples (name, url). The mixin iterates with "for name, url in self.default_js".
    - default_css: inherited from JSCSSMixin/Element (empty by default unless overridden); not modified here.

- Instance attributes (inherited or set during __init__)
    - locations (list)
        - Origin: populated by BaseMultiLocation / PolyLine via validate_locations(locations).
        - Description: normalized list (possibly nested) of coordinate pairs that define the polyline.
        - Invariant: present and normalized to coordinate pairs after successful construction.
    - options (dict)
        - Origin: created/normalized by PolyLine via path_options(line=True, **kwargs) from the kwargs passed to __init__.
        - Description: canonical Leaflet-style options used by the element's template/JSON output.
        - Behavior in this class: after the PolyLine constructor runs, PolyLineOffset updates options with {"offset": offset} so the final options include an "offset" key.
        - Typical keys: stroke, color, weight, opacity, smoothFactor, noClip, etc., plus the offset key added by this class.
    - _name (str)
        - Value set by this class: "PolyLineOffset"
        - Purpose: human-readable element name used by MacroElement/templating machinery.
    - Popup/Tooltip children
        - If popup or tooltip arguments are supplied, Popup/Tooltip children are present among the element's children (wrapped if necessary) — this behavior is inherited from PolyLine/BaseMultiLocation.

- __init__ parameters and constraints
    - locations (required): any input accepted by validate_locations. Must be a non-empty iterable of coordinate pairs (or nested iterables accepted by validation).
    - popup (optional): None or Popup instance or object coercible to string. If not a Popup instance, it will be wrapped by the BaseMultiLocation constructor.
    - tooltip (optional): same semantics as popup.
    - offset (optional, default=0): value assigned into options["offset"].
        - Recommended type: numeric (int or float) representing the offset value expected by the client-side plugin (commonly pixel offset or plugin-specific unit). The class does not validate the numeric type; non-numeric values will be stored as-is in options.
    - **kwargs: forwarded to PolyLine/path_options for standard path styling options (color, weight, opacity, smoothFactor, etc.). Keys will be normalized by path_options.

- Class invariants
    - After __init__ completes successfully:
        - self._name == "PolyLineOffset"
        - self.locations is set and valid per validate_locations
        - self.options is a dict containing the canonicalized path options plus an "offset" key whose value equals the offset passed to __init__
    - default_js remains an iterable of name/url pairs and will be used by JSCSSMixin during render.

## Lifecycle:
- Creation (how to instantiate)
    - Constructor signature (conceptual):
        - PolyLineOffset(locations, popup=None, tooltip=None, offset=0, **kwargs)
    - Required: locations (see validate_locations).
    - Optional: popup, tooltip, offset (default 0), and any PolyLine style kwargs.
    - On construction:
        1. The class delegates to the PolyLine (and ultimately BaseMultiLocation) initializer to validate locations, set children, and produce the canonical options dict.
        2. It sets self._name = "PolyLineOffset".
        3. It updates self.options with {"offset": offset}.

- Usage (typical sequence)
    1. Instantiate: instance = PolyLineOffset(locations, offset=5, color="blue", weight=3)
    2. Attach to a Map/Figure: map.add_child(instance) or equivalent container API.
    3. When the containing Figure/Map is rendered:
        - JSCSSMixin.render will register the JS resource(s) listed in default_js onto Figure.header (ensuring the leaflet-polylineoffset script is included once in the page).
        - The usual MacroElement/Template rendering takes place, serializing self.locations and self.options (including the offset) into the frontend code that will call the plugin.
    - There is no required call ordering beyond constructing before attaching and ensuring rendering happens on a Figure that exposes a header.

- Destruction / cleanup
    - PolyLineOffset does not define explicit cleanup methods. Registered JS resources are attached to the Figure.header by JSCSSMixin; removal, if required, must be performed using Figure/header APIs or by manipulating the element/container prior to render. Normal Python garbage collection applies.

## Method Map:
flowchart LR
    A[Call PolyLineOffset(locations, popup=None, tooltip=None, offset=0, **kwargs)] --> B[PolyLine.__init__ (BaseMultiLocation.__init__)]
    B --> C[validate_locations(locations) -> self.locations]
    C --> D{popup provided?}
    D -- Yes --> E[wrap/add Popup child]
    D -- No --> F[continue]
    C --> G{tooltip provided?}
    G -- Yes --> H[wrap/add Tooltip child]
    G -- No --> F
    F --> I[self._name set to "PolyLine" by PolyLine, then overridden to "PolyLineOffset"]
    I --> J[self.options = path_options(line=True, **kwargs)]
    J --> K[PolyLineOffset: self.options.update({"offset": offset})]
    K --> L[Instance ready: attach to Map/Figure]
    L --> M[Figure.render() / Element.render()]
    M --> N[JSCSSMixin.render: get_root() -> Figure?]
    N -- no --> X[AssertionError raised]
    N -- yes --> O[register default_js entries on Figure.header]
    O --> P[continue MacroElement/Template rendering (emit options & locations to client)]
    P --> Q[Client loads leaflet-polylineoffset and uses options['offset'] to render offset polyline]

## Raises:
- Exceptions potentially raised during construction (propagated from supercalls):
    - TypeError: if validate_locations or other utilities reject the provided types (e.g., non-iterable locations).
    - ValueError: if validate_locations rejects the value (e.g., empty location sequence or malformed coordinates).
    - Exceptions from Popup/Tooltip constructors or wrapping code if popup/tooltip values are invalid.
    - Exceptions from path_options if kwargs contain invalid values or types.
  Note: PolyLineOffset itself does not perform additional validation and therefore does not raise new exception types beyond those raised by PolyLine/BaseMultiLocation/path_options.

- Exceptions during rendering:
    - AssertionError raised by JSCSSMixin.render if the element is rendered while not attached to a Figure (get_root() is not a Figure). Message originates from the mixin and indicates the element must be in a Figure to register resources.
    - Any exceptions raised while registering resources on Figure.header (e.g., duplicate name handling or invalid header API) will propagate.

## Example:
- Create and add a PolyLineOffset to a map (conceptual sequence):
    1. Prepare locations: locations = [[lat1, lon1], [lat2, lon2], [lat3, lon3]]
    2. Instantiate with an offset and visual options:
       instance = PolyLineOffset(locations, offset=6, color="red", weight=4)
    3. Attach to a Map/Figure:
       m.add_child(instance)
    4. Render the Map/Figure (normal Folium rendering). When rendering occurs:
       - The leaflet-polylineoffset JS is registered into the document head (via JSCSSMixin.default_js).
       - The element's template will serialize options including "offset": 6 for use by the client-side plugin.

Notes and best practices:
- Provide numeric offset values (int or float) appropriate to the expectations of the client-side plugin (commonly pixel units). Although the class stores whatever value is passed, non-numeric values may lead to client-side errors.
- Pass standard PolyLine styling kwargs (color, weight, opacity, smoothFactor, etc.) via **kwargs — they will be normalized by path_options.
- Keep default_js class attribute unchanged unless you intentionally need a different plugin URL; overriding must follow the JSCSSMixin contract: default_js must remain an iterable of (name, url) pairs.

### `folium.plugins.polyline_offset.PolyLineOffset.__init__` · *method*

## Summary:
Initializes the PolyLineOffset instance by delegating core initialization to the PolyLine base class, setting the element name to "PolyLineOffset", and storing the provided offset value into the instance options.

## Description:
- Known callers and context:
    - Constructed directly by user code or by higher-level code that instantiates plugin objects; invoked at object construction time when a PolyLineOffset is created (i.e., before the instance is added to a map or otherwise used).
    - There are no internal helper methods in this snippet that call this initializer; its role is the class constructor invoked during normal instantiation.

- Why this is a dedicated method:
    - Initialization must perform the PolyLine base-class setup (locations, popup, tooltip, other kwargs) and then apply plugin-specific state (set the plugin name and offset option). Keeping this logic in the constructor centralizes instance setup and ensures the offset option is present immediately after creation.

## Args:
    locations (sequence): Required. The geographic coordinates describing the polyline. Typically a list/sequence of (lat, lon) or [lat, lon] points consistent with PolyLine expectations.
    popup (optional): Optional. Popup content or object associated with the polyline; forwarded to the PolyLine base class. Default: None.
    tooltip (optional): Optional. Tooltip content or object associated with the polyline; forwarded to the PolyLine base class. Default: None.
    offset (int | float, optional): Numeric offset value to be stored in the instance options under the "offset" key. Default: 0.
    **kwargs: Additional keyword arguments forwarded directly to the PolyLine base-class initializer.

## Returns:
    None. As a constructor, it does not return a value; it constructs and initializes the instance.

## Raises:
    This method does not explicitly raise exceptions. Exceptions raised by the underlying PolyLine.__init__ (for example, due to invalid locations or bad kwargs) will propagate to the caller.

## State Changes:
- Attributes READ:
    - self.options: the existing options mapping provided/created by the base class is accessed so it can be updated with the offset value.
- Attributes WRITTEN:
    - self._name: set to the string "PolyLineOffset".
    - self.options["offset"]: set/updated to the provided offset value.
    - Note: Many other instance attributes (e.g., storage of locations, popup, tooltip) are set by the base-class initializer; this method relies on that behavior but does not reassign those attributes itself.

## Constraints:
- Preconditions:
    - The PolyLine base class must accept and correctly initialize with the supplied locations, popup, tooltip, and **kwargs. In practice, locations should be a sequence of valid geographic coordinate pairs acceptable to PolyLine.
    - self.options should exist after the base-class initializer runs (this method assumes self.options is present and is a mutable mapping).
- Postconditions:
    - After completion, self._name == "PolyLineOffset".
    - After completion, "offset" is present in self.options with the value equal to the provided offset argument.
    - The instance has been through the PolyLine initialization (locations, popup, tooltip, and any effect of **kwargs).

## Side Effects:
    - No I/O or external service calls are performed.
    - Mutates the instance (self) by setting attributes described above.
    - Any exceptions from the base-class initializer may propagate out of this constructor.

