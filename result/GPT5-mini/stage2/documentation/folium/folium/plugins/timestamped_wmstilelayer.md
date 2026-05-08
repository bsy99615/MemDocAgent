# `timestamped_wmstilelayer.py`

## `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers` · *class*

## Summary:
A Folium plugin Layer that groups one or more WMS tile layers and prepares configuration to display them as a time-enabled (timestamped) sequence using the leaflet-timedimension client libraries.

## Description:
Use this class when you want to display WMS (Web Map Service) tile layers that change over time (timestamps) on a Folium map, driven by the leaflet-timedimension JavaScript plugin and related assets. Instantiate the plugin with either a single WmsTileLayer or an iterable of WmsTileLayer objects; the class collects them and exposes configuration options that the front-end timedimension control expects.

Typical usage patterns:
- Create one or more folium.raster_layers.WmsTileLayer instances (each representing the same WMS endpoint with different time parameters or timestamps).
- Instantiate TimestampedWmsTileLayers with that WmsTileLayer or a list of them.
- Add the created TimestampedWmsTileLayers instance to a folium.Map (as it subclasses Layer) so that the map rendering includes the required JS/CSS assets and the timedimension controls.

Motivation and responsibility boundary:
- This class acts as the Python-side representation of a Leaflet timedimension-enabled grouping of WMS tile layers. It collects layer instances and prepares two option dictionaries (options and options_control) which are intended to be used by the plugin template (a jinja2.Template instance stored in _template) to render the necessary JavaScript initialization on the client side.
- The class does not itself implement map rendering or client-side animation; it stores configuration and references to WmsTileLayer instances and relies on Folium's template rendering and assets inclusion (via JSCSSMixin and Layer base class) to realize client behavior.

## State:
Public attributes created/used by __init__ and their types/constraints:

- _template: jinja2.Template
  - Purpose: Jinja2 template used to render the plugin's client-side initialization. In this source it is an empty Template() placeholder.
  - Invariant: should be a Template instance. Rendering logic outside this class is expected to fill/consume it.

- default_js: list[tuple[str, str]]
  - Purpose: Module-level list of (name, url) tuples for JavaScript assets required by the plugin (jquery, jquery-ui, iso8601-js-period, leaflet-timedimension).
  - Invariant: static list used by JSCSSMixin to include JS in the map.

- default_css: list[tuple[str, str]]
  - Purpose: Module-level list of (name, url) tuples for CSS assets required by the plugin (highlight.js style and timedimension control CSS).
  - Invariant: static list used by JSCSSMixin to include CSS in the map.

- _name: str
  - Set to "TimestampedWmsTileLayers" in __init__.
  - Purpose: internal identifier used by Layer/folium for naming.

- options: dict
  - Populated by parse_options(period=period, time_interval=time_interval).
  - Purpose: Option set intended for the timedimension configuration (e.g., specifying time period and whether the data represent an interval).
  - Constraint: The precise keys/values are delegated to parse_options; caller should pass period as an ISO 8601 duration string (e.g., "P1D") and time_interval as a boolean or value acceptable to parse_options.

- options_control: dict
  - Populated by parse_options(position="bottomleft", auto_play=auto_play, player_options={...}).
  - Purpose: Option set intended for the timedimension player/control UI (position, autoplay, player-specific options).
  - Constraint: transition_time is converted to int before inclusion in player_options; loop is passed through as-is.

- layers: list[WmsTileLayer] or any assigned value
  - If the provided data argument is an instance of WmsTileLayer, layers is set to a single-element list [data].
  - Otherwise layers is set to the raw data argument.
  - Expected usage: an iterable of WmsTileLayer instances. The class does not forcibly validate or coerce non-WmsTileLayer iterables beyond the single-instance check.

Notes on __init__ parameters and defaults:
- data: required. Either a single WmsTileLayer instance or an iterable (typically list/tuple) of WmsTileLayer instances.
- transition_time: int | int-like, default 200. Converted via int(transition_time) and used as player_options['transitionTime'].
- loop: bool, default False. Passed into player_options['loop'].
- auto_play: bool, default False. Passed into options_control.
- period: str, default "P1D". Expected as an ISO 8601 duration string, used in options via parse_options.
- time_interval: bool | value acceptable to parse_options, default False. Indicates whether each layer entry represents an interval rather than an instant.
- name: optional str, default None. Passed to Layer.__init__ as the Layer name.

Class invariants:
- After __init__, _name is "TimestampedWmsTileLayers".
- options and options_control are dict-like objects returned by parse_options.
- default_js and default_css are static lists available on the class (used by JSCSSMixin).
- layers is intended to be a list/iterable of WmsTileLayer objects; if a single WmsTileLayer was passed, it is wrapped as a list.

## Lifecycle:
Creation:
- Call TimestampedWmsTileLayers(data, transition_time=200, loop=False, auto_play=False, period="P1D", time_interval=False, name=None)
- Required argument: data (WmsTileLayer or iterable of WmsTileLayer).
- The constructor calls Layer.__init__(name=name, overlay=True, control=False, show=True) through super(): the plugin is registered as an overlay layer type with no default control and shown by default.

Usage:
- Typical sequence:
  1. Create one or more WmsTileLayer instances pointing to the WMS service and configured with appropriate time parameters per-layer.
  2. Instantiate TimestampedWmsTileLayers with the WmsTileLayer or list of WmsTileLayer instances.
  3. Add the TimestampedWmsTileLayers instance to a folium.Map instance (using the Map.add_child or Map.add_layer API — Layer subclassing integrates with Folium's map rendering).
  4. Folium's rendering will include the default_js and default_css assets and render the _template with options/options_control/layers to initialize the client-side timedimension behavior.

Destruction / cleanup:
- The class has no explicit cleanup methods (no close(), context manager, or similar). Resource cleanup is handled by the browser client for assets and by Python GC for the objects. If any external resources (network or file handles) are created by contained WmsTileLayer instances, those should be managed by the user or the contained objects.

## Method Map:
Sequence and call dependencies (simple flowchart):

flowchart LR
    A[__init__ called] --> B[Layer.__init__(name, overlay=True, control=False, show=True)]
    A --> C[parse_options(period, time_interval) => options]
    A --> D[parse_options(position='bottomleft', auto_play, player_options={transitionTime:int(...), loop}) => options_control]
    A --> E[if isinstance(data, WmsTileLayer) then layers=[data] else layers=data]
    B --> F[object initialized; JSCSSMixin assets available via default_js/default_css]

## Raises:
Possible exceptions that may be propagated from __init__ (not explicitly raised by this class, but can originate from operations in __init__):
- TypeError or ValueError from int(transition_time) if transition_time cannot be converted to an integer.
- Any exception thrown by parse_options if provided arguments are invalid for that utility (e.g., invalid type/format for period or time_interval). The exact exceptions depend on parse_options implementation.
- No explicit TypeError is raised if data is not a WmsTileLayer or iterable; the class will accept the provided data as-is (but downstream rendering/template code may expect iterable/layer objects and thus raise later errors).

## Example:
Create plugin with a single WMS layer:
- Create a WmsTileLayer instance named wms1 (configured with the WMS server URL and time parameter).
- plugin = TimestampedWmsTileLayers(data=wms1, transition_time=300, loop=True, auto_play=True, period="P1D", time_interval=False, name="My Time WMS")
- Add plugin to folium.Map: map_object.add_child(plugin) (since this class subclasses Layer)

Create plugin with multiple WMS layers:
- Prepare a list wms_list = [wms_layer_t0, wms_layer_t1, wms_layer_t2]
- plugin = TimestampedWmsTileLayers(data=wms_list, transition_time=200, loop=False, auto_play=False)
- Add plugin to map as above.

Notes:
- Ensure transition_time is numeric or can be cast to int.
- Ensure each element in the provided iterable is a WmsTileLayer (or that the downstream template/render logic you use can handle the provided objects).

### `folium.plugins.timestamped_wmstilelayer.TimestampedWmsTileLayers.__init__` · *method*

## Summary:
Initialize the TimestampedWmsTileLayers Layer by registering it as a Folium overlay, preparing timedimension option dictionaries, and storing one or more WmsTileLayer instances for client-side, time-enabled rendering.

## Description:
This constructor is called when a developer instantiates the TimestampedWmsTileLayers plugin, typically during map setup before adding the plugin to a folium.Map. Common callers:
- User code that constructs the plugin directly (e.g., TimestampedWmsTileLayers(data=..., auto_play=True, ...)).
- Any higher-level helper that bundles plugin creation as part of map configuration.

Lifecycle stage:
- Invoked at object construction time to establish the plugin's internal state so the instance can be added to a folium.Map and rendered by Folium's template/asset system.

Rationale for a dedicated __init__:
- The initialization centralizes registration with the Layer base class (via super().__init__) and prepares all runtime configuration (options and options_control). Keeping this logic in __init__ ensures instances are fully-formed immediately after construction and that downstream template rendering can rely on consistent attributes.

## Args:
    data (WmsTileLayer | iterable[WmsTileLayer]):
        Required. Either a single folium.raster_layers.WmsTileLayer instance or an iterable (e.g., list/tuple) of WmsTileLayer instances.
        If a single WmsTileLayer is provided, it will be wrapped into a one-element list. If an iterable is provided, it is assigned as-is (no runtime validation beyond the single-instance check).
    transition_time (int | coercible to int, optional):
        Time in milliseconds for the client-side transition between frames. Default: 200.
        Converted using int(transition_time) before storing in player options.
    loop (bool, optional):
        Whether the client-side player should loop when it reaches the end. Default: False.
    auto_play (bool, optional):
        Whether the client-side player should start playing automatically. Default: False.
    period (str, optional):
        ISO 8601 duration string representing the time step/period for the timedimension (e.g., "P1D"). Default: "P1D".
        Passed to parse_options to populate the plugin's timedimension options.
    time_interval (bool | value accepted by parse_options, optional):
        Whether each layer entry represents a time interval rather than an instant. Default: False.
        Passed to parse_options along with period.
    name (str | None, optional):
        Optional display/internal name for the Layer, forwarded to Layer.__init__. Default: None.

## Returns:
    None
    - As a constructor, it does not return a value; it initializes the instance in-place. The instance is ready to be added to a folium.Map after successful initialization.

## Raises:
    TypeError or ValueError:
        If transition_time cannot be converted to int (raised by int()).
    Any exception raised by parse_options:
        If the provided period or time_interval values are invalid for parse_options; the specific exception types depend on that helper's implementation.
    Any exception raised by Layer.__init__ (super call):
        If the base Layer initialization rejects the provided name or other base-level invariants.
    Notes:
        The constructor performs no explicit validation of the data iterable; downstream template rendering or user code may raise errors if elements are not WmsTileLayer instances.

## State Changes:
Attributes READ:
    - None of the instance attributes are read prior to being set by this method.
    - The method does read and use passed-in arguments and calls into inherited initialization logic (Layer.__init__) and parse_options.

Attributes WRITTEN:
    - self._name : str
        Set to "TimestampedWmsTileLayers".
    - self.options : dict
        Result of parse_options(period=period, time_interval=time_interval).
    - self.options_control : dict
        Result of parse_options(position="bottomleft", auto_play=auto_play, player_options={...}).
    - self.layers : list[WmsTileLayer] | any
        If data is a WmsTileLayer instance, set to [data]; otherwise set to the provided data value (no coercion or validation).
    - Base-class state potentially modified via super().__init__:
        Layer.__init__ is invoked with name=name, overlay=True, control=False, show=True, and may set additional Layer-managed attributes.

## Constraints:
Preconditions:
    - Caller must supply a value for data; omission will cause a TypeError at construction time.
    - transition_time should be numeric or convertible to int; invalid values will raise when cast.
    - period should be a string in a form acceptable to parse_options (commonly an ISO 8601 duration).
    - If the caller intends correct runtime behavior, data should be a WmsTileLayer or an iterable of WmsTileLayer instances (this is not enforced here).

Postconditions:
    - After successful return:
        * self._name == "TimestampedWmsTileLayers"
        * self.options is a dict-like object returned by parse_options(period=..., time_interval=...)
        * self.options_control is a dict-like object returned by parse_options(position='bottomleft', auto_play=..., player_options={...})
        * self.layers is either a list containing the single provided WmsTileLayer or the raw data argument as provided
        * Layer.__init__ has been called with name=name, overlay=True, control=False, show=True (so base-layer state is initialized)

## Side Effects:
    - Calls Layer.__init__ via super().__init__, which may register or modify map-layer metadata used by Folium (no network I/O).
    - Calls parse_options (pure/utility function) twice to produce options dictionaries; parse_options may validate and transform inputs but is not expected to perform external I/O.
    - No direct I/O (file, network) occurs in this constructor itself.
    - No external objects are mutated except for assignment of self attributes; the provided data iterable/object is not copied (except when a single WmsTileLayer is wrapped in a new list), so if the caller mutates elements of the provided iterable after construction, those changes affect the plugin's layers.

