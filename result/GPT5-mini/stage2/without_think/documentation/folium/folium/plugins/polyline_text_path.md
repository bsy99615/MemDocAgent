# `polyline_text_path.py`

## `folium.plugins.polyline_text_path.PolyLineTextPath` · *class*

## Summary:
Represents a Folium plugin element that attaches text labels along the path of an existing polyline layer and ensures the required leaflet textpath JavaScript is included when rendering.

## Description:
Use this class to attach a textual label that follows the shape of an existing polyline on a Folium map. The component does not itself draw geometry — it holds a reference to an existing polyline object and configuration options that a template (rendered into the map) will use to apply text along that polyline via the leaflet-textpath plugin.

Typical scenarios:
- After creating a PolyLine (or another layer representing a path) and adding it to a map, instantiate PolyLineTextPath with that polyline and the text to be displayed, then add the PolyLineTextPath instance to the map so the frontend plugin can render the text along the path.
- This class is a MacroElement subclass and is intended to be added to a folium.Map or folium.FeatureGroup like other folium elements.

Motivation and responsibility boundary:
- Encapsulates the data needed to render text along an existing polyline using the leaflet-textpath plugin and registers the plugin's JavaScript resource (default_js). It does not implement rendering logic itself; rendering is handled by folium's templating/MacroElement machinery and the external leaflet.textpath library included via default_js.

## State:
Attributes created or used by this class (visible in the source):

- _template
  - Type: jinja2.Template
  - Value: an empty Template object in the provided source (placeholder expected to be populated in the real package)
  - Invariant: present on the class for MacroElement rendering; not modified in __init__.

- default_js
  - Type: list[tuple[str, str]]
  - Value: [("polylinetextpath", "https://cdn.jsdelivr.net/npm/leaflet-textpath@1.2.3/leaflet.textpath.min.js")]
  - Purpose: Declares the JavaScript resource (name and URL) required by this plugin so folium can include it when rendering the map.

- _name
  - Type: str
  - Set in __init__ to "PolyLineTextPath"
  - Invariant: identifies the element's name for debugging/inspection; not otherwise validated.

- polyline
  - Type: object (stored as-is)
  - Set from the __init__ parameter polyline.
  - Invariant: stored reference to the existing polyline layer or object. The class does not validate type or properties of this object.

- text
  - Type: object (stored as-is; typically expected to be str)
  - Set from the __init__ parameter text.
  - Invariant: stored text content used by the frontend plugin. No encoding or length checks are performed here.

- options
  - Type: dict (result returned by folium.utilities.parse_options)
  - Created by calling parse_options(...) with the provided __init__ parameters (repeat, center, below, offset, orientation, attributes, plus any **kwargs).
  - Invariant: contains option keys/values as produced by parse_options. The class does not inspect or mutate options after assignment.

Notes on __init__ parameters and their defaults (as seen in source):
- polyline: required positional parameter, stored to self.polyline.
- text: required positional parameter, stored to self.text.
- repeat: default False
- center: default False
- below: default False
- offset: default 0
- orientation: default 0
- attributes: default None
- **kwargs: passed through to parse_options

Class invariants:
- After initialization, self._name, self.polyline, self.text, and self.options are defined.
- default_js and _template are class-level attributes present on the class.

## Lifecycle:
Creation:
- Instantiate with PolyLineTextPath(polyline, text, repeat=False, center=False, below=False, offset=0, orientation=0, attributes=None, **kwargs)
- Required arguments: polyline and text.
- The constructor calls parse_options to produce the options dictionary and sets basic attributes; it calls the superclass __init__ via super().__init__().

Usage:
- Typical usage pattern:
  1. Create and add a PolyLine (or similar path layer) to a folium.Map.
  2. Instantiate PolyLineTextPath with that polyline and the desired text and options.
  3. Add the PolyLineTextPath instance to the same folium.Map (or FeatureGroup).
  4. When the map is rendered, folium uses MacroElement machinery and the class's _template (and default_js) so that the leaflet-textpath script receives the polyline, text, and options to render text along the path on the client.
- Methods: This class only defines __init__ in the provided source. Rendering and HTML/JS emission are provided by MacroElement and the (empty in-source) _template.

Destruction / cleanup:
- No explicit cleanup is required. There are no context manager interfaces or close methods in this class.

## Method Map:
(Only methods shown in the provided source are listed.)

flowchart LR
    A[Instantiate PolyLineTextPath] --> B[super().__init__()]
    B --> C[set _name = "PolyLineTextPath"]
    C --> D[assign polyline]
    C --> E[assign text]
    C --> F[options = parse_options(...)]
    F --> G[class ready to be added to a Map]
Note: actual template rendering and JavaScript inclusion occur later in MacroElement rendering flow, which calls the class's _template and uses default_js.

## Raises:
- The __init__ method itself does not explicitly raise exceptions in the source.
- parse_options is called inside __init__; any exceptions raised by parse_options (e.g., invalid option values) will propagate out of __init__. This class does not catch or translate those exceptions.

## Example:
- Basic usage outline (conceptual; not source code included here):
  1. Create a PolyLine on a folium.Map and add it to the map.
  2. Create a PolyLineTextPath with that polyline and text, optionally setting repeat, center, offset, etc.
  3. Add the PolyLineTextPath to the map so the rendering engine can include the textpath JavaScript and initialize the text-on-path behavior.

- Concrete steps conceptually:
  - poly = folium.PolyLine(locations=[...])
  - poly.add_to(map)
  - text_path = PolyLineTextPath(polyline=poly, text="Route A", repeat=True, center=False)
  - text_path.add_to(map)

This component does not itself provide methods to attach the text to the polyline beyond storing the reference and options; the actual attachment is achieved by the frontend leaflet.textpath plugin invoked during map rendering.

### `folium.plugins.polyline_text_path.PolyLineTextPath.__init__` · *method*

## Summary:
Initializes the PolyLineTextPath plugin instance by recording the target polyline and display text and by producing a normalized options dictionary on the instance.

## Description:
This constructor runs during object creation when user code or higher-level helpers instantiate PolyLineTextPath(polyline, text, ...). It executes before the plugin is added to a folium.Map or rendered. The instance created here is later added to a map (or feature group) so the MacroElement rendering machinery can emit the template and include the external leaflet.textpath JavaScript (declared via the class's default_js).

Why this logic is its own method:
- Centralizes all attribute assignments and options normalization for the plugin so callers always obtain a consistent instance state (name, polyline reference, text, and parsed options).
- Keeps option normalization (via parse_options) out of rendering and map-addition logic and ensures a single place to extend or modify initialization behavior.

Known callers / context:
- Direct instantiation in user code or helper utilities, e.g.:
    poly = folium.PolyLine(locations=...)
    poly.add_to(map)
    text_path = PolyLineTextPath(polyline=poly, text="Route A", repeat=True)
    text_path.add_to(map)
- Occurs during the creation phase of the plugin lifecycle, before template rendering and JS inclusion.

## Args:
    polyline (object)
        Required. Reference to an existing polyline-like element (typically a folium.PolyLine or similar layer). The constructor stores the object as-is; no runtime type-checking is performed here. The rendering pipeline and frontend leaflet.textpath expect this object to represent a path.

    text (str)
        Required. Text to render along the polyline. Stored as-is; no length/encoding checks are performed here.

    repeat (bool, optional)
        Whether to repeat the text along the path. Defaults to False.

    center (bool, optional)
        Whether to center the text along the path. Defaults to False.

    below (bool, optional)
        Whether to render the text beneath the path. Defaults to False.

    offset (int | float, optional)
        Pixel offset applied to the text position relative to the path. Defaults to 0.

    orientation (int | float, optional)
        Rotation/orientation applied to the text along the path. Defaults to 0.

    attributes (dict | None, optional)
        Additional attributes to pass to the frontend text element (e.g., SVG/text attributes). Defaults to None.

    **kwargs
        Any additional snake_case option names supported by the project; all are forwarded to parse_options which camelizes keys and removes entries with value None.

Note: Default values shown above match the constructor signature; no additional validation of individual argument types is performed here aside from what parse_options may enforce or reject.

## Returns:
    None
    As an initializer, the method does not return a value. It produces observable state on the instance (attributes described in State Changes).

## Raises:
    Propagated exceptions (this constructor does not catch them):
    - Any exception raised by super().__init__(), typically errors originating from parent class initialization (MacroElement / JSCSSMixin).
    - Any exception raised by parse_options(...). In practice, parse_options may propagate:
        * AttributeError: if a passed keyword key is not a string-like value and camelize is invoked on it.
        * TypeError: if camelize or subsequent processing fails due to incompatible key/value types.
    - Other exceptions can occur if callers pass unusual types as kwargs; parse_options itself does not raise custom exceptions but relies on camelize and standard errors.

## State Changes:
Attributes READ:
    - None explicitly read from self before assignment in this method. (Class-level attributes like default_js and _template exist but are not accessed here.)

Attributes WRITTEN:
    - self._name (str): set to "PolyLineTextPath"
    - self.polyline (object): set to the provided polyline argument
    - self.text (object, typically str): set to the provided text argument
    - self.options (dict[str, Any]): set to the result of parse_options(...), which contains camelCased keys and excludes keys whose value was None

Side-effect calls:
    - Calls super().__init__() to run parent initialization (MacroElement / JSCSSMixin).
    - Calls parse_options(...), a pure in-memory normalization function that camelizes keys and removes None-valued entries.

## Constraints:
Preconditions:
    - Caller must supply polyline and text positional arguments.
    - For kwargs: prefer string keys in snake_case; non-string keys may cause camelize to raise exceptions which will propagate.
    - If a caller expects validation beyond normalization (e.g., allowed option keys or value types), that validation is not performed here and must be performed elsewhere or rely on downstream components.

Postconditions:
    - Instance attributes are initialized as follows (on successful return):
        * self._name == "PolyLineTextPath"
        * self.polyline references the provided polyline object
        * self.text references the provided text object
        * self.options is a dict where:
            - all keys are camelCased forms of the provided snake_case kwargs (including repeat, center, below, offset, orientation, attributes)
            - no entries have a value of None (such keys were omitted)
    - The object is ready to be added to a folium.Map / FeatureGroup; subsequent MacroElement rendering will use the stored values and the class-level default_js to include the frontend library.

## Side Effects:
    - No file or network I/O is performed directly.
    - Parent class initialization via super().__init__() may perform additional side effects (e.g., registering template structures) outside this method.
    - parse_options(...) performs pure in-memory normalization (camelizing keys and dropping None values) and does not mutate external state.
    - No global state or external service is modified by this constructor.

