# `vectorgrid_protobuf.py`

## `folium.plugins.vectorgrid_protobuf.VectorGridProtobuf` · *class*

## Summary:
Represents a Folium plugin layer that stores metadata for a Mapbox VectorTile (protobuf) tile source and registers the Leaflet.VectorGrid JavaScript dependency so the front-end library is available when the map is rendered.

## Description:
VectorGridProtobuf is a small plugin class that combines Layer metadata semantics with JSCSSMixin resource registration. Its responsibilities are strictly metadata and dependency registration:

- Store the remote vector-tile protobuf URL (url) and an optional options object (options) that is intended for use by client-side Leaflet.VectorGrid code.
- Ensure the Leaflet.VectorGrid JavaScript library is declared as a dependency (via default_js) so the script is injected into the Figure header during rendering.

Important boundary: The class does not contain or provide working client-side template code to instantiate the Leaflet.VectorGrid layer in the browser. The class contains an empty _template (jinja2.Template()) in the source; therefore, producing client-side JavaScript that actually creates the Leaflet.VectorGrid.Protobuf layer must be provided elsewhere (a template, an extending subclass, or by the caller). VectorGridProtobuf only prepares the metadata and registers the external script.

Use cases:
- Add an instance to a folium.Map (or other Element/Layer container) when you want to include a VectorTile/protobuf layer and ensure the required Leaflet.VectorGrid script is present in the rendered HTML.
- Combine with a custom template or a higher-level integration that knows how to consume url and options to instantiate the front-end layer.

Motivation:
- Keep server-side code minimal: do not perform validation, fetching, or rendering of tiles. Provide metadata and resource declarations so the front-end can perform tile fetching and rendering.

## State:
Class-level attributes
- _template
    - Type: jinja2.Template
    - Value in source: an empty Template() instance
    - Notes: In the provided source the template is empty — there is no built-in client-side instantiation. Subclasses or external templates are expected to implement the HTML/JS that uses url/options.

- default_js
    - Type: list[tuple[str, str]]
    - Value in source: [("vectorGrid", "https://unpkg.com/leaflet.vectorgrid@latest/dist/Leaflet.VectorGrid.bundled.js")]
    - Purpose: JSCSSMixin will iterate this list at render time to add the named JavaScript resource(s) to the Figure.header.
    - Invariant: should remain an iterable of 2-tuples (name, url). Invalid items will cause errors during rendering.

Instance attributes (set during __init__)
- layer_name (str)
    - How set: if the caller provides a truthy layer_name argument it is used; otherwise the constructor assigns the string "VectorGridProtobufLayer".
    - Notes: The constructor always passes this value to Layer.__init__ as name. Layer may set additional metadata based on the name.

- url
    - Type: expected string (URL or URL template)
    - How set: required positional parameter to __init__; assigned directly to self.url.
    - Constraints: not validated by this class. Callers should provide a valid vector-tile protobuf URL or template.

- _name
    - Type: str
    - Value: "VectorGridProtobuf"
    - Purpose: internal element type identifier used by folium/Element systems.

- options (optional)
    - Type: any (conventionally dict)
    - How set: assigned to self.options only if the options argument passed to __init__ is not None.
    - Constraint: If options is None, the instance will not have an options attribute created by this constructor.
    - Semantics: intended to hold the JavaScript configuration for Leaflet.VectorGrid (e.g., styling callbacks, rendererFactory). No validation or serialization is performed here.

Class invariants:
- default_js must be an iterable of (name, url) pairs for JSCSSMixin to function correctly.
- layer_name and url are expected to remain stable after initialization; options may or may not exist depending on constructor input.

## Lifecycle:
Creation:
- Constructor signature: VectorGridProtobuf(url, layer_name, options=None)
    - url (required): vector tile protobuf URL or URL template (string). No server-side validation.
    - layer_name (required positional but can be falsy): if truthy its value is used; otherwise default "VectorGridProtobufLayer" is used.
    - options (optional): recommended to be a JSON-serializable dict if provided. If omitted (None), no options attribute is set by the constructor.

Instantiation effects (in order):
1. Determine self.layer_name := layer_name if truthy else "VectorGridProtobufLayer".
2. Call Layer.__init__(name=self.layer_name) to register Layer metadata.
3. Set self.url := url.
4. Set self._name := "VectorGridProtobuf".
5. If options is not None, set self.options := options.

Usage:
- Typical sequence:
    1. Instantiate with a valid url and desired layer_name/options.
    2. Add the instance to a folium.Map (or other container) using add_child or equivalent.
    3. When the Figure containing the element is rendered:
       - JSCSSMixin registers the Leaflet.VectorGrid script specified in default_js with the Figure.header.
       - Any template or client-side code that consumes the layer metadata (url and options) must be provided separately; VectorGridProtobuf itself does not perform client-side instantiation.
- Required order: attach to a Figure before render; otherwise JSCSSMixin's render will assert a Figure root.

Destruction / cleanup:
- No explicit cleanup API. Resource registration is performed at render time by JSCSSMixin. Removing the layer or its registered script requires manipulation of the Figure/header or element tree outside this class.

## Method Map:
flowchart LR
    A[Call VectorGridProtobuf.__init__(url, layer_name, options)] --> B[set self.layer_name := layer_name or "VectorGridProtobufLayer"]
    B --> C[call Layer.__init__(name=self.layer_name)]
    C --> D[set self.url := url]
    D --> E[set self._name := "VectorGridProtobuf"]
    E --> F{options is not None?}
    F -- yes --> G[set self.options := options]
    F -- no --> H[do not create options attribute]
    G --> I[instance ready]
    H --> I
    I --> J[On render: JSCSSMixin registers default_js into Figure.header]
    J --> K[External template/client-side code (not provided here) must use url/options to create Leaflet.VectorGrid layer]

## Raises:
- __init__ does not explicitly raise exceptions.
- Possible propagated exceptions:
    - Exceptions from Layer.__init__(name=...) (unlikely here because a non-None name is always provided).
    - Errors during rendering if default_js is malformed (e.g., elements are not 2-tuples) or if Figure/header operations fail. These are raised during render by JSCSSMixin or Figure, not by this constructor.
    - Client-side failures (runtime JS errors) if the url or options are invalid; these occur in the browser, not in Python.

## Example:
- Instantiate and add to a folium.Map (conceptual steps):
    1. url = "https://tiles.example.com/tiles/{z}/{x}/{y}.pbf"
    2. layer = VectorGridProtobuf(url, layer_name="My Vector Tiles", options={"maxZoom": 14})
    3. map_object.add_child(layer)
    4. Render or save the map:
       - The Leaflet.VectorGrid script from default_js will be injected into the HTML head by JSCSSMixin.
       - You must also provide a client-side template (or extend this class with a template) that reads layer.url and layer.options and calls the appropriate Leaflet.VectorGrid.Protobuf constructor in JavaScript; VectorGridProtobuf does not supply that JavaScript template itself.

Notes and best practices:
- Pass a JSON-serializable dict for options when those options need to be embedded into templates.
- Do not mutate default_js at runtime on the class or ancestor classes; override it at subclass definition time if needed.
- Because _template is empty in the source, integrate this class with an existing plugin template or subclass it and provide a template that uses url and options to instantiate the front-end layer.

### `folium.plugins.vectorgrid_protobuf.VectorGridProtobuf.__init__` · *method*

## Summary:
Initializes a VectorGridProtobuf plugin instance by storing the tile URL, assigning a display layer name, invoking the base Layer initializer with that name, and (optionally) attaching runtime options to the instance.

## Description:
This constructor prepares a VectorGridProtobuf plugin object for use with folium maps. Typical usage is to create an instance and then add it to a folium.Map (for example, via map.add_child(plugin) or plugin.add_to(map)); the constructor is invoked at the moment the plugin object is created as part of the map-building lifecycle.

This logic is separated into its own initializer because it performs object setup tasks (establishing identifying attributes and storing configuration) that must occur when the instance is created and prior to any calls that rely on those attributes. The constructor also delegates name-based setup to the parent Layer class via super().__init__(name=...), so keeping this logic here ensures the subclass name and base-class initialization are coordinated.

## Args:
    url (str):
        A URL or URL template for requesting VectorTile / Protobuf tiles. The value is stored verbatim on the instance as self.url. The constructor does not validate or modify this string; callers should supply a valid tile endpoint or template (e.g., with {z}/{x}/{y} placeholders if required by the tile service).
    layer_name (str or None):
        Human-visible layer name used for the Layer base-class registration and for display in map controls. If a truthy string is provided it is used; otherwise the default "VectorGridProtobufLayer" is used.
    options (dict or None), optional:
        If provided (not None), this dictionary is assigned to self.options and can contain plugin-specific configuration keys. If omitted or None, no self.options attribute is set by this constructor.

## Returns:
    None
    (Constructor; initializes instance state and returns no value.)

## Raises:
    The constructor does not explicitly raise any exceptions. Any exceptions raised by the Layer base-class initializer (invoked via super().__init__(name=...)) or by attribute assignment (e.g., memory errors) may propagate to the caller.

## State Changes:
    Attributes READ:
        (none) — the method does not read any existing self.<attr> attributes; it only reads its parameters.
    Attributes WRITTEN:
        self.layer_name (str): set to layer_name if truthy, otherwise "VectorGridProtobufLayer".
        self.url (str): set to the provided url argument.
        self._name (str): set to the literal "VectorGridProtobuf".
        self.options (dict) — set only if the options argument is not None.
        Additionally, super().__init__(name=self.layer_name) is called which may initialize or modify base-class state (Layer-managed attributes).

## Constraints:
    Preconditions:
        - The caller should pass a meaningful url (typically a non-empty string). The constructor does not perform URL validation.
        - layer_name may be None or an empty/falsey value; in that case the default layer name is used.
        - If options is provided, it is expected to be a mapping (dict-like); the constructor does not enforce the type.
    Postconditions:
        - After return, self.layer_name, self.url, and self._name will be set as documented.
        - If options was not None, self.options exists and references the provided object.
        - The Layer base-class initializer has been invoked with name set to the resulting layer_name.

## Side Effects:
    - Calls the Layer base-class initializer via super().__init__(name=self.layer_name). Any side effects performed by that base initialization (registration with internal structures, setting of Layer attributes) will occur.
    - No network I/O, file I/O, or external service calls are performed by this constructor itself.
    - No global state or objects outside self are directly mutated by this method aside from potential base-class effects.

