# `timestamped_geo_json.py`

## `folium.plugins.timestamped_geo_json.TimestampedGeoJson` · *class*

## Summary:
Represents a Folium plugin that displays time-enabled GeoJSON on a Leaflet map using the Leaflet.TimeDimension player; it wraps GeoJSON data (from a file-like object, a dict, or an external reference) and provides configuration for playback behavior.

## Description:
TimestampedGeoJson is a MacroElement + JSCSSMixin plugin that integrates time-aware GeoJSON layers with the Leaflet.TimeDimension player when added to a folium Map. Instantiate it when you have GeoJSON features (or a geometry) that include time information and you want an interactive time slider, play/pause controls, and configurable playback behavior on a folium Map.

Typical callers:
- Application code that builds folium Map instances and adds time-aware GeoJSON overlays.
- Any factory that prepares GeoJSON and needs to attach a time-control visualization to a Map.

Responsibility boundary:
- This class is responsible for:
  - Accepting GeoJSON data in one of three forms: a file-like object (with read()), a Python dict, or "other" (left as-is and treated as an external reference / raw string).
  - Preparing and storing playback options and UI assets (JS/CSS) required by the Leaflet.TimeDimension control.
  - Validating that it is added to a folium.Map at render-time.
- It does NOT:
  - Parse or validate the semantics of time properties inside the GeoJSON beyond JSON parsing and minimal normalization to a FeatureCollection for bounds computation.
  - Provide network access or read external URLs automatically when embed is False (it simply stores the reference given).

## State:
Instance attributes (names, types, defaults/constraints, invariants):

- _name (str)
  - Value: "TimestampedGeoJson"
  - Invariant: set on initialization and used by MacroElement machinery.

- embed (bool)
  - How set:
    - True if the provided data object has a read attribute (file-like), or if type(data) is dict.
    - False otherwise (e.g., when passing a URL string or a raw GeoJSON string and not a dict/file-like).
  - Invariant: indicates whether self.data contains embedded JSON text (True) or a non-embedded reference/raw value (False).

- data (str)
  - If embed is True and data was file-like: holds the result of data.read() (string).
  - If embed is True and data was a dict: holds json.dumps(data) (string).
  - If embed is False: holds the original data argument unchanged (could be a URL, filename, or already-serialized JSON string).
  - Constraint: When embed is True, data is expected to be JSON text; methods that parse it (e.g., _get_self_bounds) will call json.loads and may raise json.JSONDecodeError for invalid JSON.

- add_last_point (bool)
  - Default: True (converted via bool(add_last_point))
  - Purpose: configuration flag used by the template/JS (stored for template rendering).

- period (str)
  - Default: "P1D"
  - Value used by the client-side player configuration (ISO 8601 period string).

- date_options (str)
  - Default: "YYYY-MM-DD HH:mm:ss"
  - Formatting option passed through to the client-side time display.

- duration (str)
  - Default behavior: if duration is None, the instance attribute is set to the literal string "undefined". Otherwise it is set to the duration value wrapped in double quotes, e.g. '"PT1H"'.
  - Note: the code stores a string intended for direct injection into client-side template code; callers should pass a duration string (e.g., ISO8601 period) or None.

- options (dict)
  - Created by parse_options(...) in __init__ with these entries:
    - position: "bottomleft"
    - min_speed: float (default 0.1)
    - max_speed: int/float (default 10)
    - auto_play: bool (default True)
    - loop_button: bool (default False)
    - time_slider_drag_update: bool (default False)
    - speed_slider: bool (default True)
    - player_options: dict containing:
      - transitionTime: int (transition_time cast to int)
      - loop: bool (loop parameter)
      - startOver: True (hard-coded)
  - Constraint: parse_options may enforce additional formatting/validation (not defined here).

Class attributes:
- _template (jinja2.Template)
  - Template object used by MacroElement to render the necessary HTML/JavaScript. (Template content is external to this snippet.)
- default_js (list[tuple(str, str)])
  - A list of (name, url) tuples for required JS assets, including jquery, jqueryui, iso8601-js-period, leaflet.timedimension, and moment.
- default_css (list[tuple(str, str)])
  - A list of (name, url) tuples for required CSS assets, including highlight.js and leaflet.timedimension.control.css.

Class invariants:
- After __init__, _name is a non-empty string and options is a dict.
- If embed is True then data is a JSON text string; if embed is False then data is not parsed by the class until explicitly handled by external code or templates.
- The plugin must be attached to a folium.Map before render() is called; otherwise render asserts.

## Lifecycle:
Creation:
- Required argument:
  - data: one of
    - a file-like object with a read() method (the object itself is not stored; its read() output is stored),
    - a Python dict (which will be json.dumps'ed),
    - any other object (commonly a URL string, filename or already-serialized JSON string) which will be stored as-is and cause embed to be False.
- Optional keyword args (with defaults):
  - transition_time (int): 200
  - loop (bool): True
  - auto_play (bool): True
  - add_last_point (bool): True
  - period (str): "P1D"
  - min_speed (float): 0.1
  - max_speed (int): 10
  - loop_button (bool): False
  - date_options (str): "YYYY-MM-DD HH:mm:ss"
  - time_slider_drag_update (bool): False
  - duration (str or None): None (treated as undefined)
  - speed_slider (bool): True

Usage:
- Typical sequence:
  1. Instantiate TimestampedGeoJson with appropriate data and options.
  2. Add the instance to a folium.Map instance (via Map.add_child or Map.add) prior to rendering.
  3. When the map is rendered (Map._repr_html_ or saving the map), render() will be called which asserts that the element's parent is a folium.Map and then proceeds to MacroElement rendering behavior which uses _template and options.
  4. If bounds computation is needed by higher-level logic, call _get_self_bounds() (or the template rendering may call it indirectly). This requires embed==True.

Destruction / cleanup:
- There are no explicit resources to close; the class does not implement context manager methods or close(). Cleaning up is handled by Python GC and folium/Leaflet when the Map is discarded.

Sequencing notes:
- render() must only be executed when the plugin is a child of a folium.Map; otherwise an AssertionError is raised.
- _get_self_bounds() is only valid if embed is True; calling it otherwise raises ValueError.

## Method Map:
Flow of primary methods / interactions (typical invocation order):
graph TD
    A[__init__(data, ...)] --> B[set attributes: embed, data, options, etc.]
    B --> C[add to Map via Map.add_child(instance)]
    C --> D[render(**kwargs)]
    D --> E[MacroElement.render (parent behavior) -> template uses attributes]
    E --> F[_get_self_bounds() used only when embed == True, may be called by template or externally]

(Note: the class exposes render and _get_self_bounds as its runtime methods; the template rendering logic uses stored attributes and default_js/default_css to inject assets.)

## Raises:
Exceptions that can be raised directly by methods in this class:

- AssertionError (in render)
  - Trigger: render() is called when self._parent is not an instance of folium.folium.Map.
  - Message: "TimestampedGeoJson can only be added to a Map object."

- ValueError (in _get_self_bounds)
  - Trigger: _get_self_bounds() is called when embed is False.
  - Message: "Cannot compute bounds of non-embedded GeoJSON."

- json.JSONDecodeError (from json.loads inside _get_self_bounds)
  - Trigger: embed is True but self.data is not valid JSON text. This exception originates from the json library when attempting to parse invalid JSON.

- Any exceptions raised by parse_options(...) used in __init__
  - Trigger: invalid option values passed to parse_options; specifics depend on parse_options implementation (not included here).

## Example (usage described in prose):
1. Prepare GeoJSON input:
   - If you have a Python dict representing GeoJSON, pass it directly as the data argument; the class will embed it by json.dumps.
   - If you have a file-like object (opened file or io.StringIO) that contains GeoJSON, pass the file object; the constructor will read() it and embed the JSON text.
   - If you pass a string (for example, a URL or a pre-serialized JSON string) it will be stored as-is and embed will be False.

2. Instantiate the plugin with custom options as needed (e.g., transition_time, auto_play, period).

3. Attach the plugin to a folium.Map instance using the Map.add_child (or Map.add) method before rendering/saving the map.

4. If you need the geographic bounds of the embedded GeoJSON, ensure you passed embedable data (dict or file-like) and call _get_self_bounds(); if the JSON is invalid this will raise json.JSONDecodeError.

Notes:
- The stored duration value is prepared for inclusion in templates; None becomes the literal string "undefined", any other provided duration becomes a quoted string (e.g., '"PT1H"').
- The class exposes default_js and default_css lists which will be included by JSCSSMixin/MacroElement rendering to ensure client-side dependencies are available.

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.__init__` · *method*

## Summary:
Initializes the TimestampedGeoJson plugin instance, normalizing the provided geojson data and player configuration into instance attributes so the object is ready to be rendered/attached to a folium Map.

## Description:
Known callers and context:
- Typical callers are user code that constructs a TimestampedGeoJson instance to add a time-enabled GeoJSON layer to a folium Map (for example, calling Map.add_child(TimestampedGeoJson(...))). This method is invoked at object construction time (the class constructor), during the plugin creation phase of preparing map layers for rendering.
- It is also called whenever a plugin object is programmatically recreated (e.g., in tests or factory functions that instantiate the plugin).

Why this logic is its own method:
- The constructor centralizes data normalization (accept multiple forms of input: file-like, dict, or raw string) and player option parsing in one place. This keeps instantiation logic separate from rendering (template generation) and avoids repeating option parsing elsewhere. It ensures the object reaches a consistent internal representation immediately after creation.

## Args:
    data (file-like | dict | str):
        - file-like: any object with a read() method (e.g., an open file or StringIO). The content returned by read() is stored as the plugin data.
        - dict: a Python mapping representing GeoJSON. It will be serialized with json.dumps.
        - str: any string (typically a JSON string or a URL/path). Passed through as-is when not file-like or dict.
        - No implicit validation of GeoJSON structure is performed here.
    transition_time (int, default=200):
        - Milliseconds used for the player "transitionTime". Coerced to int when placed into player_options.
    loop (bool, default=True):
        - Whether the player loops playback.
    auto_play (bool, default=True):
        - Whether playback should start automatically.
    add_last_point (bool, default=True):
        - Whether the last point of a timeseries should be added/shown when rendering.
    period (str, default="P1D"):
        - ISO 8601 duration string that defines the period for timestamp grouping (kept as provided).
    min_speed (float, default=0.1):
        - Minimum playback speed passed to parse_options.
    max_speed (float, default=10):
        - Maximum playback speed passed to parse_options.
    loop_button (bool, default=False):
        - Whether to include a loop toggle button in the player UI.
    date_options (str, default="YYYY-MM-DD HH:mm:ss"):
        - Date formatting option string used by the player UI.
    time_slider_drag_update (bool, default=False):
        - Whether dragging the time slider updates the map continuously.
    duration (str | None, default=None):
        - If None, the instance attribute duration is set to the literal string "undefined".
        - If provided, the value is turned into a quoted string by surrounding it with double quotes (e.g., input 'PT1H' becomes '"PT1H"') to match downstream template usage.
    speed_slider (bool, default=True):
        - Whether to show a speed slider in the player UI.

## Returns:
    None
    - The constructor does not return a value; it initializes instance state.

## Raises:
    - This initializer does not explicitly raise any exceptions itself.
    - It may propagate exceptions thrown by json.dumps (if given non-serializable objects) or by parse_options (if invalid option values are supplied). Callers should validate their inputs or handle propagated exceptions.

## State Changes:
    Attributes READ:
        - None (the method does not read any pre-existing self.<attr> fields; it only invokes super().__init__ and sets attributes).
    Attributes WRITTEN:
        - self._name (str): set to "TimestampedGeoJson"
        - self.embed (bool): True when data was read from a file-like object or when data was a dict; False otherwise
        - self.data (str): the stored GeoJSON content or the raw input string; for dict input it is json.dumps(dict), for file-like input it is the result of data.read()
        - self.add_last_point (bool): normalized boolean value from the add_last_point arg
        - self.period (str): set to the provided period argument
        - self.date_options (str): set to the provided date_options argument
        - self.duration (str): set to "undefined" if duration is None, otherwise set to the provided duration wrapped in double quotes (e.g., '"PT1H"')
        - self.options (dict): result of parse_options(...) containing UI/player configuration, including a 'player_options' dict with transitionTime, loop, and startOver keys

## Constraints:
    Preconditions:
        - The caller must provide a `data` parameter that is one of:
            * a file-like object implementing read(), whose read() returns the GeoJSON text to embed, or
            * a Python dict representing GeoJSON (serializable by json.dumps), or
            * a string (raw JSON, path, or URL) to be used directly.
        - transition_time must be coercible to int (numeric-like); otherwise int(transition_time) will raise.
        - min_speed and max_speed should be numeric values acceptable to the downstream parse_options implementation.
    Postconditions:
        - After return, the instance has normalized fields (embed, data, add_last_point, period, date_options, duration, options) ready for template rendering.
        - self.options always contains a 'player_options' mapping with integer 'transitionTime', boolean 'loop', and 'startOver' set to True.

## Side Effects:
    - If `data` is file-like, data.read() is called (which may perform I/O and advance the file pointer). The method does not close the file-like object.
    - If `data` is a dict, json.dumps is called (CPU/memory cost; may raise TypeError for non-serializable values).
    - parse_options(...) is called to build self.options; any side effects or validations in parse_options will occur (errors from parse_options propagate).
    - No network calls or filesystem writes are performed by this method itself.

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson.render` · *method*

## Summary:
Checks that the element's parent is a folium Map and then delegates rendering to its superclass render implementation (MacroElement.render); no value is returned.

## Description:
This method enforces a runtime precondition — that the instance's _parent is a folium.folium.Map — and then calls the parent class's render routine to perform rendering. The class declaration shows TimestampedGeoJson inherits from MacroElement, so super().render(**kwargs) invokes MacroElement.render. This method exists to keep the Map-attachment validation local to the plugin while reusing the shared rendering logic provided by the superclass.

Known callers / lifecycle stage:
- Invoked when this element's render method is called as part of the rendering process for folium elements. The exact call site is any code that triggers element rendering and invokes child element render methods.

Why this is a separate method:
- Centralizes the Map-attachment check for this plugin before invoking the shared superclass rendering logic.

## Args:
    **kwargs: dict
        Arbitrary keyword arguments forwarded unchanged to the superclass render implementation. This method does not inspect or validate specific keys.

## Returns:
    None
    The method does not return a value; its effect is realized via side effects performed by the superclass render call.

## Raises:
    AssertionError
        If self._parent exists but is not an instance of folium.folium.Map. Exact assertion message:
        "TimestampedGeoJson can only be added to a Map object."
    AttributeError
        If the instance does not have a self._parent attribute (attempting to evaluate the assertion will raise this).
    Any exception raised by the invoked superclass render implementation (MacroElement.render) is propagated unchanged.

## State Changes:
Attributes READ:
    self._parent
        - Read to validate attachment to a Map.

Attributes WRITTEN:
    None directly by this method.
    Note: MacroElement.render (invoked here) may mutate this object or the parent Map (e.g., by registering resources or attaching rendering fragments); such mutations are performed by the superclass implementation, not by this method's body.

## Constraints:
Preconditions:
    - The instance must have an attribute self._parent.
    - self._parent must be an instance of folium.folium.Map for the assertion to pass.
    - Any initialization required by the superclass render implementation should have been completed prior to calling this method.

Postconditions:
    - The superclass render implementation (MacroElement.render) has been invoked for this element if no exception is raised.

## Side Effects:
    - Delegates to MacroElement.render, which may perform template rendering and mutate rendering-related state on this element or on the parent Map.
    - This method itself performs no direct I/O.

### `folium.plugins.timestamped_geo_json.TimestampedGeoJson._get_self_bounds` · *method*

## Summary:
Compute and return the geographic bounding box for this object's embedded GeoJSON data; raises if the GeoJSON is not embedded. This method does not modify the object's state.

## Description:
This helper parses the object's embedded GeoJSON (self.data), normalizes single Feature/Geometry inputs into a FeatureCollection, and delegates the actual bounding-box computation to folium.utilities.get_bounds with lonlat=True.

Known callers and context:
- No direct callers were discovered in the supplied repository snapshot.
- Typical usage: called by map-rendering or view-fitting code that needs the footprint/viewport for an embedded GeoJSON layer (for example, code that calls fit_bounds on the Map after a plugin is added). It is implemented as its own method so callers can obtain bounds without duplicating JSON parsing and normalization logic.

Why this logic is a separate method:
- Encapsulates parsing, normalization (wrapping single geometries/features into a FeatureCollection), and the final call to get_bounds in one place.
- Keeps render/fitting code concise and makes unit testing of bounds computation straightforward.

## Args:
    None.

## Returns:
    list[list[float|int|None], list[float|int|None]]
    - The method returns whatever folium.utilities.get_bounds returns when called with lonlat=True for the normalized GeoJSON:
        - Typical shape: [[min_lon, min_lat], [max_lon, max_lat]] when get_bounds returns raw bounds mirrored to lon/lat ordering.
        - If there are no coordinates, get_bounds will return [[None, None], [None, None]] (or its lonlat-mirrored equivalent).
        - If get_bounds delegates to a mirror helper, the exact axis order/representation follows that helper's contract; the important guarantee is that the return encodes min and max for the first two coordinate axes in the lon/lat orientation requested.

## Raises:
    ValueError:
        - Raised unconditionally if self.embed is falsy. Exact message from the code: "Cannot compute bounds of non-embedded GeoJSON."

    json.JSONDecodeError (or ValueError from json.loads in some Python versions):
        - Raised if self.data is not valid JSON text (this happens when self.embed is True but the stored self.data cannot be parsed by json.loads).

    IndexError, TypeError, or other exceptions raised by get_bounds / iter_coords:
        - If the normalized GeoJSON yields coordinate tuples with fewer than two elements, get_bounds may raise IndexError.
        - If coordinate values are of incompatible/comparable types, comparisons inside get_bounds may raise TypeError.
        - Any exception thrown by get_bounds (or the helpers it uses) will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.embed
        - self.data

    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.embed must be True (the method enforces this and raises ValueError otherwise).
        - self.data must contain a JSON-serializable representation of GeoJSON or a GeoJSON geometry (string parseable by json.loads).
        - If the embedded JSON is intended to yield 2D coordinates, the leaf coordinate containers yielded by iter_coords (used by get_bounds) must contain at least two elements.

    Postconditions:
        - The method returns a bounds object computed from the (possibly normalized) GeoJSON via get_bounds(..., lonlat=True).
        - No attributes on self are modified.
        - If the embedded data contains no coordinates, the returned bounds will contain None entries for mins and maxs as described by get_bounds.

## Side Effects:
    - Calls json.loads(self.data) to parse JSON (no external I/O).
    - Calls folium.utilities.get_bounds(data, lonlat=True) to compute bounds.
    - No network I/O, file I/O, or global state mutation is performed.
    - Exceptions from json.loads or get_bounds propagate to the caller.

## Behavior details and normalization rules:
    - If the parsed JSON object has a "features" key (i.e., is a FeatureCollection-like mapping), it is passed through to get_bounds unchanged.
    - Otherwise, the method attempts to interpret the parsed JSON as either:
        - A GeoJSON Feature mapping (a dict containing a "geometry" key), or
        - A raw Geometry mapping (e.g., a GeoJSON geometry object).
      If the parsed object is a raw geometry (not a dict with a "geometry" key), the method wraps it into a Feature object: {"type": "Feature", "geometry": data}.
      In either non-FeatureCollection case, the method then wraps the single Feature into a FeatureCollection: {"type": "FeatureCollection", "features": [data]} before calling get_bounds.

## Edge cases:
    - Non-embedded data: raises ValueError immediately.
    - Malformed JSON: json.loads raises JSONDecodeError.
    - Valid JSON that is not GeoJSON-like may lead to get_bounds raising (IndexError/TypeError) because iter_coords may not find valid coordinate tuples.
    - A single point yields identical min and max entries in the returned bounds (e.g., a single [lon, lat] -> [[lon, lat], [lon, lat]]).

