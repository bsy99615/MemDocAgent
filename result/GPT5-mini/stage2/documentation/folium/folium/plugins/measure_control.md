# `measure_control.py`

## `folium.plugins.measure_control.MeasureControl` · *class*

## Summary:
MeasureControl is a Folium plugin element representing a Leaflet measurement control; it collects configuration options for the control and exposes the JavaScript/CSS asset references required to render a client-side measure widget.

## Description:
MeasureControl is intended to be instantiated by client code that wants to add a distance/area measuring control to a folium map. Typical usage is to construct an instance with desired settings and add it to a folium.Map or another MacroElement container so the widget's assets and configuration are included in the rendered HTML.

The class is a thin integration layer:
- It stores configuration options provided by the caller (position and unit choices).
- It declares two class-level lists (default_js and default_css) containing the remote URLs of the Leaflet measure plugin assets.
- It relies on folium.utilities.parse_options to normalize the provided keyword arguments into a camelCased options dictionary suitable for passing to front-end code.

MeasureControl exists as a distinct abstraction to:
- Collect and canonicalize measurement-control configuration in Python-land.
- Expose the JavaScript/CSS resource references required for the control to function when the folium map is rendered.

Known callers/factories:
- Typical callers are user code constructing a plugin and then attaching it to a folium.Map (e.g., map.add_child(MeasureControl(...))). No factory functions are defined in this module.

## State:
Attributes and invariants present on instances after __init__:

- _template : jinja2.Template
  - Type: Template
  - Purpose: Template placeholder used by MacroElement for rendering. In this source the Template is instantiated but empty (no template content).
  - Invariant: Always present on the class; value is a Template instance.

- default_js : list[tuple[str, str]]
  - Type: list of (name, url) tuples
  - Default value (class-level):
    - ("leaflet_measure_js", "https://cdn.jsdelivr.net/gh/ljagis/leaflet-measure@2.1.7/dist/leaflet-measure.min.js")
  - Purpose: Reference(s) to JavaScript asset(s) required by the measure control. By convention JSCSSMixin/MacroElement consumers will read this to include assets in the generated page.

- default_css : list[tuple[str, str]]
  - Type: list of (name, url) tuples
  - Default value (class-level):
    - ("leaflet_measure_css", "https://cdn.jsdelivr.net/gh/ljagis/leaflet-measure@2.1.7/dist/leaflet-measure.min.css")
  - Purpose: Reference(s) to CSS asset(s) required by the measure control.

- _name : str
  - Type: string
  - Set in __init__ to "MeasureControl".
  - Purpose: Human-readable identifier used by MacroElement for diagnostic or registration purposes.

- options : dict[str, Any]
  - Type: dictionary mapping option names to values
  - Construction: Produced by calling folium.utilities.parse_options with the parameters passed to __init__.
  - Semantics and invariants:
    - All keys are camelCased (parse_options converts snake_case to camelCase).
    - Keys whose provided value was exactly None are omitted (parse_options filters out None-valued entries).
    - No further validation or coercion is performed by MeasureControl itself — values are preserved as passed.
    - Typical keys created from the constructor parameters: "position", "primaryLengthUnit", "secondaryLengthUnit", "primaryAreaUnit", "secondaryAreaUnit" (camelized forms).
  - Example contents after default construction:
    - {'position': 'topright', 'primaryLengthUnit': 'meters', 'secondaryLengthUnit': 'miles', 'primaryAreaUnit': 'sqmeters', 'secondaryAreaUnit': 'acres'}

Constructor (__init__) parameters and constraints:
- position: str = "topright"
  - Description: placement of the control in the Leaflet map UI (string passed through as-is into options).
  - Constraint: No validation in this class; callers should provide a Leaflet-appropriate position string.

- primary_length_unit: str = "meters"
  - Description: primary length unit label/value passed to front-end config.

- secondary_length_unit: str = "miles"
  - Description: secondary length unit label/value passed to front-end config.

- primary_area_unit: str = "sqmeters"
  - Description: primary area unit label/value passed to front-end config.

- secondary_area_unit: str = "acres"
  - Description: secondary area unit label/value passed to front-end config.

- **kwargs: additional keyword configuration options
  - Any extra options accepted by the underlying Leaflet measure plugin may be passed here using Python-style names (snake_case). These will be camelized and included in options unless their value is None.

Class invariants:
- options is always a dict whose keys are camelCase strings and which contains no entries with value None.
- _name is always the string "MeasureControl".

## Lifecycle:
Creation:
- Instantiate by calling MeasureControl(...) with optional parameters documented above. No positional-only arguments; all are keyword-friendly defaults.
- Example: ctrl = MeasureControl(position="topleft", primary_length_unit="meters")

Usage:
- After instantiation, attach the instance to a folium.Map or another MacroElement container so that folium's rendering pipeline can include its declared assets and options. Typical sequence:
  1. ctrl = MeasureControl(...)
  2. map.add_child(ctrl)  # or map.add_control(ctrl) depending on map API
  3. map._repr_html_() or map.save("map.html") to trigger rendering and inclusion of JS/CSS and options.
- There are no public mutator methods on this class in the source; to change options after construction, replace the options dict or construct a new MeasureControl.

Destruction / cleanup:
- No explicit cleanup methods (no close(), __exit__, or context management). Resource lifecycle (asset inclusion) is handled by the folium rendering pipeline; MeasureControl itself holds only lightweight Python data and Template placeholder.

Sequencing notes:
- There is no required call order after construction beyond adding the element to a Map before rendering. The value of options should be finalized before rendering.

## Method Map:
flowchart LR
    A[__init__] --> B[parse_options(...)]
    B --> C[set self.options (camelCased, None filtered)]
    A --> D[set _name = "MeasureControl"]
    A --> E[inherit default_js/default_css/_template from class]
    style A fill:#e3f2fd,stroke:#0277bd
    style B fill:#e8f5e9,stroke:#2e7d32
    style C fill:#fff3e0,stroke:#ef6c00

## Raises:
Possible exceptions that can propagate out of __init__:
- Any exception raised by folium.utilities.parse_options, typically:
  - AttributeError or TypeError: If caller passes non-string keys via **kwargs that break the camelize routine used by parse_options.
  - Exceptions originating from the camelize implementation if keys are not string-like.
- Note: MeasureControl itself performs no additional type checking and will not raise ValueError/TypeError for invalid option values — those would only arise if parse_options/camelize fail on the keys.

## Example:
- Typical instantiation and use (conceptual, non-executable in this doc block):
  - Create control with defaults:
      ctrl = MeasureControl()
      # ctrl.options == {
      #   'position': 'topright',
      #   'primaryLengthUnit': 'meters',
      #   'secondaryLengthUnit': 'miles',
      #   'primaryAreaUnit': 'sqmeters',
      #   'secondaryAreaUnit': 'acres'
      # }
  - Create control with custom units and an extra option:
      ctrl = MeasureControl(position='topleft', primary_length_unit='kilometers', showClearControl=True)
      # parse_options will camelize 'primary_length_unit' -> 'primaryLengthUnit'
      # and 'showClearControl' is kept as-is (assumed provided in Python-style if needed)
  - Attach to a folium Map (rendering step handled by folium):
      m = folium.Map(...)
      m.add_child(ctrl)
      m.save('map_with_measure.html')

Notes and caveats:
- MeasureControl does not itself render JavaScript initialization logic in the provided Template placeholder (Template is empty in this source). The presence of default_js and default_css ensures the asset URLs are available on the class; integration into the front-end (initialization of the Leaflet plugin with the options dict) depends on the folium rendering template pipeline and/or a filled-in MacroElement template in a consuming release.
- Because parse_options preserves values and only normalizes keys/removes None, callers must supply semantically-appropriate values expected by the front-end plugin (e.g., valid unit identifiers and position strings).

### `folium.plugins.measure_control.MeasureControl.__init__` · *method*

## Summary:
Initializes the MeasureControl instance by setting its human-readable name and building a canonical options dictionary (camelCased, no None values) from the provided position/unit parameters and any additional keyword options.

## Description:
Known callers and context:
- Instantiated directly by user code when adding a measurement control to a folium.Map, e.g. map.add_child(MeasureControl(...)).
- Invoked during the construction lifecycle of a MeasureControl object; callers typically construct the control prior to attaching it to a Map and rendering the map HTML.
- The method is called exactly at object creation time (in __init__) and is not expected to be called again for an existing instance.

Why this logic is a separate method:
- The constructor's responsibilities are limited: delegate base-class initialization, store a stable identifier for the element, and normalize configuration into a single options dictionary consumed by the rendering pipeline. Normalization is delegated to the shared utility parse_options so this method remains lightweight and focused on wiring instance state rather than key normalization logic.

## Args:
    position (str): Placement of the control in the Leaflet map UI. Default: "topright".
        - Allowed values: any string accepted by the Leaflet control positioning (e.g., "topleft", "topright", "bottomleft", "bottomright"). No validation is performed here.
    primary_length_unit (str): Primary unit identifier for distance measurements. Default: "meters".
        - Semantic constraint: should be a unit string understood by the front-end plugin.
    secondary_length_unit (str): Secondary unit identifier for distance measurements. Default: "miles".
        - Semantic constraint: should be a unit string understood by the front-end plugin.
    primary_area_unit (str): Primary unit identifier for area measurements. Default: "sqmeters".
        - Semantic constraint: should be a unit string understood by the front-end plugin.
    secondary_area_unit (str): Secondary unit identifier for area measurements. Default: "acres".
        - Semantic constraint: should be a unit string understood by the front-end plugin.
    **kwargs: Additional keyword options passed to the underlying Leaflet measure plugin.
        - Keys are expected to be strings (snake_case or camelCase). Values may be any Python object appropriate for the plugin.
        - Behavior: All kwargs are forwarded to folium.utilities.parse_options which converts keys to camelCase and removes entries whose value is exactly None.

## Returns:
    None. The constructor initializes instance attributes and does not return a value.

## Raises:
    Any exception originating from super().__init__:
        - e.g., exceptions from MacroElement initialization if the base class raises.
    Any exception propagated from folium.utilities.parse_options:
        - AttributeError or TypeError if a kwargs key is not string-like and camelize (used by parse_options) fails.
        - Other exceptions thrown by camelize or parse_options implementation will propagate unchanged.
    Note: MeasureControl.__init__ itself performs no additional validation and does not raise ValueError/TypeError for invalid option values; such failures only occur if parse_options/camelize cannot process provided keys.

## State Changes:
    Attributes READ:
        - None explicitly read from self by this method. (It calls super().__init__ but does not access existing self attributes.)
    Attributes WRITTEN:
        - self._name (str): set to "MeasureControl".
        - self.options (dict[str, Any]): assigned the dictionary returned by parse_options; keys are camelCased and values are the provided values (None-valued entries removed).

    Additional notes:
        - Calling super().__init__ may initialize inherited MacroElement internals (for example, a Template placeholder _template) but those assignments occur in the base class initializer rather than in this method's explicit attribute writes.

## Constraints:
    Preconditions:
        - Caller must supply keyword arguments in a mapping-compatible form (standard Python keyword args); keys should be string-like so parse_options/camelize can operate on them.
        - No assumption is made about validity of option values beyond being acceptable to the front-end plugin; callers should provide semantically-correct unit and position strings.
    Postconditions:
        - self._name == "MeasureControl".
        - self.options is a dict whose keys are the camelCase forms of provided parameter names and kwargs, and which contains no entries whose value is None.
        - No additional validation of option values has been performed by this method.

## Side Effects:
    - Calls super().__init__(): may initialize inherited MacroElement state (e.g., template placeholder) and perform base-class side effects.
    - Calls folium.utilities.parse_options(...) to build the options dict. parse_options is a pure-in-memory transformation (no I/O); parse_options may call camelize which can raise on invalid key types.
    - No I/O, network access, or mutation of objects outside this instance is performed here.

