# `geocoder.py`

## `folium.plugins.geocoder.Geocoder` · *class*

## Summary:
Represents a Folium plugin that adds a Leaflet geocoder control to a map. It packages the control's configuration and required JS/CSS references and exposes the configuration as an options mapping used when rendering the control.

## Description:
Instantiate this class when you want to attach a client-side geocoder control (Leaflet Control.Geocoder) to a Folium map. The class collects the control options and registers the external JavaScript and CSS resources required by the Leaflet geocoder control. Typical usage is to create a Geocoder instance and add it to an existing folium.Map (for example via the map's add_child or the plugin's add_to(map) helper).

Responsibility boundary:
- This class is responsible only for preparing configuration and resource references for the Leaflet geocoder control and exposing them to the folium rendering pipeline (MacroElement).
- It does not itself perform geocoding, network requests, or provide geocoder implementations; it merely integrates the external Control.Geocoder assets and options into the Folium/Leaflet environment.

Known callers/factories:
- Typical callers are user code that composes folium maps and plugins (create Geocoder(...) then add to a folium.Map).
- Folium map-building utilities that accept plugin instances and attach them to maps via add_child/add_to.

## State:
- _template (jinja2.Template)
  - Type: jinja2.Template
  - Purpose: Template used by MacroElement when rendering the control into the map HTML. In the current source the template is present but contains no content.
  - Invariant: Always a jinja2.Template instance.

- default_js (list[tuple[str, str]])
  - Type: list of 2-tuples (name, url)
  - Value: Contains at least one tuple ("Control.Geocoder.js", "https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js")
  - Purpose: Declares the JavaScript resource required for the geocoder control.
  - Invariant: Each entry is a (filename, URL) tuple of strings.

- default_css (list[tuple[str, str]])
  - Type: list of 2-tuples (name, url)
  - Value: Contains at least one tuple ("Control.Geocoder.css", "https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css")
  - Purpose: Declares the CSS resource required for the geocoder control.
  - Invariant: Each entry is a (filename, URL) tuple of strings.

- _name (str)
  - Type: str
  - Value set in __init__: "Geocoder"
  - Purpose: Identifies the element in folium's element tree.
  - Invariant: Equals "Geocoder" for all instances.

- options (dict)
  - Type: dict
  - How created: Returned value of folium.utilities.parse_options called with the __init__ arguments.
  - Contents and semantics: Contains configuration keys that will be passed to the client-side Leaflet control when rendered. Standard keys populated by __init__ include:
    - collapsed: bool (from collapsed parameter)
    - position: str (from position parameter)
    - defaultMarkGeocode: bool (from add_marker parameter)
    - plus any additional keys supplied via **kwargs forwarded to parse_options.
  - Valid values/constraints:
    - collapsed: boolean
    - position: typical Leaflet control positions are strings like 'topleft', 'topright', 'bottomleft', 'bottomright' (the class accepts any string; validation is performed by the consuming JavaScript/Leaflet environment if applicable)
    - defaultMarkGeocode: boolean
  - Invariant: options is a mapping (dict-like) produced by parse_options and remains unchanged unless modified by user code after instantiation.

## Lifecycle:
- Creation:
  - Constructor signature: Geocoder(collapsed=False, position="topright", add_marker=True, **kwargs)
    - collapsed (bool): whether the control is initially collapsed. Default: False.
    - position (str): Leaflet control position. Default: "topright".
    - add_marker (bool): whether the control should add a marker when a geocode result is selected. Mapped to the option defaultMarkGeocode. Default: True.
    - **kwargs: any additional configuration keys forwarded to parse_options and included in options.
  - On instantiation, MacroElement.__init__ is called (via super()), _name is set to "Geocoder" and options is set to the result of parse_options(...).

- Usage:
  - Typical sequence:
    1. Instantiate a Geocoder with desired options.
    2. Attach to a folium.Map via map.add_child(geocoder) or geocoder.add_to(map).
    3. Render the map (Folium collects MacroElement instances, includes default_js/default_css assets and injects the options into the rendered HTML/JS).
  - There is no required explicit ordering between configuration and adding to the map beyond constructing the instance before adding it to the map.

- Destruction / cleanup:
  - No explicit cleanup methods are provided by this class.
  - Resource lifecycle (loading/unloading of JS/CSS) is managed by the rendered HTML and client-side environment; server-side there is no open resource to close.

## Method Map:
- High-level flow of important calls and dependencies:

graph LR
    U[User code] --> |instantiate| Init[Geocoder.__init__]
    Init --> SuperInit[MacroElement.__init__]
    Init --> Parse[parse_options(collapsed, position, defaultMarkGeocode, **kwargs)]
    Init --> SetOptions[options = dict(...)]
    Geocoder --> |exposes| default_js
    Geocoder --> |exposes| default_css
    User code --> |attach| Map[folium.Map.add_child / add_to]
    Map --> |renders| Template[_template] & options & default_js/default_css

(Note: the class has no public methods beyond construction; MacroElement provides render/attachment behavior used when the instance is added to a Map.)

## Raises:
- The Geocoder.__init__ implementation does not explicitly raise exceptions.
- parse_options may raise exceptions for invalid arguments; such exceptions would propagate through __init__. The class itself performs no additional validation or error raising.

## Example:
- Create a Geocoder with the control visible in the top-right and markers enabled:
  1) Construct a Geocoder instance with collapsed=False, position="topright", add_marker=True.
  2) Add the Geocoder instance to an existing folium.Map using the map's add_child method or the plugin's add_to(map) helper.
  3) When the map is rendered, the Control.Geocoder JavaScript and CSS will be included and the options mapping will be passed to the client-side control.

### `folium.plugins.geocoder.Geocoder.__init__` · *method*

## Summary:
Initializes a Geocoder plugin instance by calling the MacroElement constructor, setting the element name, and producing the options mapping that will be exposed to the Folium rendering pipeline.

## Description:
Known callers and context:
- User code that composes folium maps and plugins: typically invoked during map construction when a developer writes Geocoder(...) and then attaches the instance to a folium.Map via add_child or add_to.
- Folium map-building utilities that accept plugin instances and attach them to maps; these utilities construct plugin objects before rendering the map.
Lifecycle stage:
- This constructor is called when creating the plugin object prior to attaching it to a folium.Map and prior to rendering. It prepares configuration and element identity so that the map can collect assets (JS/CSS) and options for client-side rendering.

Why this logic is separated:
- Encapsulates plugin initialization responsibilities (calling the parent initializer and assembling options) in one place to keep instantiation deterministic and concise.
- Keeps option parsing and default mapping centralized (via parse_options) so rendering and resource registration code can rely on a consistent self.options structure.
- Avoids inlining parse_options or name-setting at the call site, improving maintainability and reusability of the plugin.

## Args:
    collapsed (bool): Whether the geocoder control is initially collapsed. Default: False.
    position (str): Leaflet control position string (e.g., 'topleft', 'topright', 'bottomleft', 'bottomright'). The constructor accepts any string; Leaflet will interpret it at render time. Default: "topright".
    add_marker (bool): If True, mapped to the client-side option defaultMarkGeocode to indicate whether a marker should be placed for geocode results. Default: True.
    **kwargs: Additional option key/value pairs forwarded to parse_options and merged into the resulting options mapping. Keys should be strings expected by the client-side control; values should be serializable to JSON for embedding in the rendered HTML/JS.

## Returns:
    None: As a constructor, this method does not return a value. After the call, the instance is initialized and ready to be attached to a folium.Map.

## Raises:
    Any exception raised by parse_options will propagate out of this constructor. Examples include type or value validation errors originating from parse_options if invalid option types or values are provided. The constructor itself performs no additional explicit validation or raises.

## State Changes:
Attributes READ:
    - None (the constructor does not read existing self.<attr> fields; it invokes the parent initializer and then sets attributes)

Attributes WRITTEN:
    - self._name (str): set to the literal "Geocoder".
    - self.options (dict-like): set to the mapping returned by parse_options(...) containing at minimum the keys collapsed, position, and defaultMarkGeocode (from add_marker), plus any keys supplied via **kwargs.
    - Implicit parent initialization via super().__init__ may set or register additional MacroElement-inherited attributes (not directly read or modified here by name).

## Constraints:
Preconditions:
    - The caller should pass values that make sense for the target client-side control: collapsed and add_marker should be booleans (or truthy/falsey values that parse_options accepts), position should be a string representing a Leaflet control position, and kwargs keys/values should be JSON-serializable.
    - No attributes on self are required to be pre-initialized before calling this constructor (the constructor calls the parent initializer).

Postconditions:
    - self._name == "Geocoder"
    - self.options is a dictionary-like mapping produced by parse_options and includes at least:
        - "collapsed": the value passed as collapsed
        - "position": the value passed as position
        - "defaultMarkGeocode": the value passed as add_marker
      plus any additional keys forwarded from **kwargs.
    - The object is a valid MacroElement-derived plugin instance ready to be added to a folium.Map.

## Side Effects:
    - Calls MacroElement.__init__ via super(), which initializes the base MacroElement state necessary for attachment and rendering (this may register the element internally within the Folium element model).
    - Calls folium.utilities.parse_options to construct the options mapping (no I/O; purely local computation).
    - No network I/O or filesystem access occurs in this constructor.

