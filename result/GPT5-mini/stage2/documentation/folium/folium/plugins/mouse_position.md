# `mouse_position.py`

## `folium.plugins.mouse_position.MousePosition` · *class*

## Summary:
A folium plugin element that displays the current mouse cursor geographic coordinates on the map and injects the required Leaflet MousePosition JS/CSS assets when rendered.

## Description:
MousePosition is a small plugin element intended to be attached to a folium Map (or another Element/Figure tree) to show live latitude/longitude under the cursor in a map corner. Instantiate this class when you want an unobtrusive readout of coordinates (with configurable formatting and ordering) to appear on the rendered map.

Scenarios / callers:
- Typical usage is to construct a MousePosition and add it to a folium.Map via map.add_child(mouse_position) or map.add_child(...). It is a UI plugin and therefore used by application code that builds a folium Map for HTML output.
- This class is implemented as a MacroElement subclass (template-based rendering) and also mixes in JSCSSMixin so that the required external JS/CSS URLs specified in default_js / default_css are automatically registered with the Figure header when the element is rendered.

Motivation / responsibility:
- Encapsulates the configuration and resource registration required to use the third-party Leaflet.MousePosition control.
- Responsibility boundary: prepare and hold the plugin options and formatter placeholders, and rely on MacroElement/JSCSSMixin to perform rendering and asset injection. It does not itself perform any DOM manipulation outside of template rendering.

## State:
Class attributes
- _template (jinja2.Template): A Jinja2 Template object used by the MacroElement rendering pipeline. In the source the template is provided (an empty Template instance in the file snippet) and is used by the MacroElement rendering step to produce the HTML/JS for the control.
- default_js (list[tuple[str, str]]): A list containing one (name, url) tuple for the Leaflet.MousePosition JavaScript resource:
    - ("Control_MousePosition_js", "https://cdn.jsdelivr.net/gh/ardhi/Leaflet.MousePosition/src/L.Control.MousePosition.min.js")
    - Invariant: iterable of 2-tuples (name, url).
- default_css (list[tuple[str, str]]): A list containing one (name, url) tuple for the Leaflet.MousePosition CSS resource:
    - ("Control_MousePosition_css", "https://cdn.jsdelivr.net/gh/ardhi/Leaflet.MousePosition/src/L.Control.MousePosition.min.css")
    - Invariant: iterable of 2-tuples (name, url).

Instance attributes (set by __init__)
- _name (str): Set to "MousePosition". Used by the Element/MacroElement framework to identify the element.
- options (dict[str, Any]): The plugin options, produced by calling folium.utilities.parse_options(...) with the provided constructor arguments. Keys are camelCased (e.g., num_digits -> numDigits, empty_string -> emptyString, lng_first -> lngFirst) and any argument with value None is omitted per parse_options behavior.
    - Typical keys (after camelization): position, separator, emptyString, lngFirst, numDigits, prefix, plus any additional kwargs passed through.
    - Invariant: options contains no values that are exactly None (parse_options filters them out).
- lat_formatter (str): A string expressing a JavaScript formatter for the latitude, or the literal "undefined" if no formatter was supplied (the code sets lat_formatter = lat_formatter or "undefined").
    - Valid values: any object provided by the caller; typical expected use is a JavaScript function name or expression (as a string). If None is provided, the attribute is the string "undefined".
- lng_formatter (str): Same contract as lat_formatter but for longitude.
    - Valid values: string (JS formatter) or "undefined".

Class invariants:
- default_js and default_css remain iterables of 2-tuples.
- options is always a dict with camelCased keys and no None values after construction.
- lat_formatter and lng_formatter are never None after construction; they are strings (either the provided value or "undefined").

## Lifecycle:
Creation:
- Call the constructor with zero or more keyword arguments. No positional arguments are required.

Constructor signature (keyword parameters and defaults)
- position (str) = "bottomright"
- separator (str) = " : "
- empty_string (str) = "Unavailable"
- lng_first (bool) = False
- num_digits (int) = 5
- prefix (str) = ""
- lat_formatter (Optional[Any]) = None
- lng_formatter (Optional[Any]) = None
- **kwargs: passed through to parse_options and included in options after camelization if not None

How to instantiate:
- mouse_pos = MousePosition()
- mouse_pos = MousePosition(position='topright', num_digits=6, prefix='Coord: ')

Usage / typical sequence:
1. Instantiate MousePosition with desired configuration.
2. Add it to a folium.Map or appropriate Element tree (e.g., map.add_child(mouse_pos)).
3. When the Map/Figure is rendered:
   - The JSCSSMixin will register default_js and default_css with the Figure header so the external JS/CSS are included in the page.
   - The MacroElement rendering machinery will render the element's _template into the page, using self.options, lat_formatter, lng_formatter as context (the template uses these attributes to emit the JavaScript that creates the Leaflet control).
4. There is no explicit cleanup API on this object. Assets are registered on the containing Figure during render; removal must be handled by manipulating the Figure/header if necessary.

Destruction:
- No destructor, close method, or context manager; normal Python garbage collection applies. There are no file handles or network connections to close.

## Method Map:
flowchart LR
    A[__init__] --> B[set _name = "MousePosition"]
    B --> C[options = parse_options(...)]
    C --> D[lat_formatter/lng_formatter set (value or "undefined")]
    D --> E[instance ready to be added to a Map]
    E --> F[When rendering:]
    F --> G[JSCSSMixin registers default_js/default_css on Figure.header]
    F --> H[MacroElement uses _template and instance attrs to render JS control]

## Raises:
Exceptions that may propagate from __init__:
- Any exceptions raised by parse_options:
    - AttributeError or TypeError if parse_options/camelize is given non-string-like keys (unlikely here since constructor passes fixed keyword names).
    - Any other exceptions thrown by camelize or parse_options will propagate; parse_options itself does not raise custom errors but relies on camelize.
- If callers pass unexpected types for parameters that later break template rendering or downstream JS generation, those errors will surface at render time (not during __init__), e.g., if lat_formatter is an object that cannot be represented in the template context as intended.

Notes on safety:
- The constructor performs no explicit type validation beyond using parse_options. Callers should pass values of the expected types (e.g., bool for lng_first, int for num_digits) to avoid surprising behavior in the template or frontend.

## Example:
- Create and add a MousePosition to a folium.Map (typical usage):
    1. Instantiate with defaults:
       mouse_pos = MousePosition()
    2. Or customize:
       mouse_pos = MousePosition(position='topright', num_digits=6, prefix='Coords: ', lng_first=True)
    3. Add to a map:
       m = folium.Map(location=[0, 0], zoom_start=2)
       m.add_child(mouse_pos)
    4. Render or save the map (the Map rendering will register external JS/CSS and render the control).

Notes:
- To provide custom JavaScript formatter functions, pass the formatter as a string that the template will insert into the JS context (e.g., lat_formatter="function(lat){return lat.toFixed(2) + '°'}"). If you pass None, the class sets the formatter attribute to the literal string "undefined", which the template can use directly when constructing the JS control.
- The final appearance and behavior depend on the external Leaflet.MousePosition library; MousePosition only supplies configuration and ensures the library is included in the rendered page.

### `folium.plugins.mouse_position.MousePosition.__init__` · *method*

## Summary:
Initializes a MousePosition plugin instance by performing base-class initialization, delegating option normalization to parse_options, and storing latitude/longitude formatter values (or the JavaScript token "undefined") on the instance.

## Description:
This constructor prepares an object that represents the MousePosition plugin for a folium Map. It performs three responsibilities at construction time:
- Calls the superclass constructor to perform MacroElement base initialization.
- Calls folium.utilities.parse_options(...) with the provided parameters (and any extra keyword options) and stores the returned result on the instance as self.options.
- Stores formatter values for latitude and longitude on the instance (self.lat_formatter and self.lng_formatter). If a formatter argument is falsy, it is replaced with the string "undefined" before storage.

Known callers and lifecycle:
- Typically invoked by user code during map assembly, for example: map.add_child(MousePosition(...)). The constructor runs when the plugin object is created (map setup phase).
- There are no internal callers in this module; this is the standard object constructor.

Why this logic is a separate method:
- As the __init__ method, it centralizes initialization (base-class setup, option normalization, attribute assignment) at object creation time. Separating initialization keeps construction concerns distinct from rendering and template logic executed later.

## Args:
    position (str, optional): Corner of the map where the coordinate display will appear. Default: "bottomright".
    separator (str, optional): Separator string between latitude and longitude when rendered. Default: " : ".
    empty_string (str, optional): Text to display when no coordinates are available. Default: "Unavailable".
    lng_first (bool, optional): Whether to display longitude before latitude. Default: False.
    num_digits (int, optional): Number of decimal places to show for numeric coordinates. Default: 5.
    prefix (str, optional): Text prefix added before the coordinate display. Default: "".
    lat_formatter (any, optional): A formatter for latitude values. If the provided value is falsy (e.g., None, '', False, 0), the constructor stores the literal string "undefined" instead. Default: None.
    lng_formatter (any, optional): A formatter for longitude values. Same falsy-to-"undefined" behavior as lat_formatter. Default: None.
    **kwargs: Additional keyword arguments forwarded unchanged to folium.utilities.parse_options. Valid keys and semantics depend on parse_options.

## Returns:
    None

## Raises:
    - This constructor does not raise exceptions explicitly.
    - Any exception raised by super().__init__ or by folium.utilities.parse_options will propagate to the caller (for example, TypeError, ValueError, or other exceptions emitted by those routines).

## State Changes:
Attributes READ:
    - None on self are read by this method. (The method uses only its parameters and calls super().__init__ and parse_options.)

Attributes WRITTEN:
    - self._name (str): Set to the literal "MousePosition".
    - self.options: Set to the exact value returned by parse_options(position=..., separator=..., empty_string=..., lng_first=..., num_digits=..., prefix=..., **kwargs).
    - self.lat_formatter: Set to lat_formatter if lat_formatter is truthy; otherwise set to the string "undefined".
    - self.lng_formatter: Set to lng_formatter if lng_formatter is truthy; otherwise set to the string "undefined".

## Constraints:
Preconditions:
    - The caller should supply parameter values consistent with their intended semantics (strings for textual parameters, bool for lng_first, int for num_digits). The constructor does not perform explicit type enforcement; invalid types may cause parse_options or superclass initialization to raise.
    - Any keys passed via **kwargs must be acceptable to folium.utilities.parse_options; invalid keys or values may cause parse_options to raise.

Postconditions:
    - After successful return, self._name == "MousePosition".
    - self.options holds whatever parse_options returned for the provided parameters and **kwargs (no in-constructor mutation beyond assignment).
    - For each of lat_formatter and lng_formatter: if the corresponding argument was truthy, the attribute equals that argument; if the argument was falsy (None, empty string, False, 0, etc.), the attribute equals the string "undefined".

## Side Effects:
    - Calls super().__init__(), which may cause base-class side effects (initialization behavior depends on MacroElement).
    - Calls folium.utilities.parse_options(...), which may perform validation/normalization and can raise exceptions; any side-effects from that function (logging, validation errors) occur here.
    - The constructor itself does not perform I/O (no file or network access) and does not mutate objects outside of setting attributes on self.

