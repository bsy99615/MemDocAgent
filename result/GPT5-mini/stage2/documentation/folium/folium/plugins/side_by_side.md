# `side_by_side.py`

## `folium.plugins.side_by_side.SideBySideLayers` · *class*

## Summary:
A minimal folium Layer subclass that groups two layers (left and right) for a side-by-side comparison UI and declares the client-side JS resource required to render a draggable side-by-side splitter.

## Description:
SideBySideLayers encapsulates the intent to present two map layers side-by-side with a movable divider (the "side-by-side" UI). It is a tiny plugin-like Layer subclass that:
- accepts two layer-like objects (the left and right layers),
- sets up required JavaScript resources via the JSCSSMixin so the frontend can create the side-by-side control,
- and relies on the broader folium rendering pipeline to attach those resources and to render the element inside a Map/Figure.

Typical scenarios to instantiate:
- When you want to add an interactive side-by-side comparison of two raster or tile layers to a folium map.
- Caller pattern: construct two layers (tile layer, image overlay, or any folium layer-like Element) and pass them to SideBySideLayers(layer_left, layer_right) then add the resulting object to the Map/Figure before rendering.

Motivation and responsibility:
- Responsibility: pair two layers and declare the external JavaScript asset required to drive the side-by-side UI. It leaves rendering and DOM integration to the folium Element/Layer rendering system and the Map/Figure container.
- Boundary: does not validate the rendering semantics of the supplied layers, does not implement the client-side UI itself (that is handled by the external JS resource referenced in default_js), and does not register itself as a control in the layer UI (it sets control=False).

## State:
Attributes created or declared on the class/instance (public):

- _template (jinja2.Template)
    - Type: jinja2.Template
    - Value: an empty Template instance in the source (Template()).
    - Role: placeholder template used by folium's Element rendering system. In this class it is empty; concrete rendering content must be supplied by the surrounding folium system or by extending this class.

- default_js (list[tuple[str, str]])
    - Type: list of (name, url) pairs
    - Value (as declared): [
        ("leaflet.sidebyside", "https://cdn.jsdelivr.net/gh/digidem/leaflet-side-by-side@gh-pages/leaflet-side-by-side.min.js")
      ]
    - Role: JSCSSMixin will register each (name, url) pair on the Figure header before rendering so the client-side library is available.

- _name (str)
    - Type: str
    - Value set in __init__: "SideBySideLayers"
    - Role: human/technical identifier for the layer element used by folium's Layer/Element system.

- layer_left (object)
    - Type: any object (expected: a folium Layer-like Element, e.g., TileLayer, ImageOverlay, FeatureGroup)
    - Constraint: must be a renderable layer or Element that the Map/Figure knows how to render; the class does not perform runtime type checking.
    - Invariant: intended to represent the content shown on the left side of the divider.

- layer_right (object)
    - Type: any object (expected: a folium Layer-like Element)
    - Constraint: same as layer_left.
    - Invariant: intended to represent the content shown on the right side of the divider.

Class/instance invariants:
- layer_left and layer_right should remain valid renderable layer objects for the duration they are attached to a Map/Figure.
- control flag for this Layer is set to False (via Layer.__init__(control=False)) — invariant: this instance will not present itself as a layer control entry by default.
- default_js should remain an iterable of 2-tuples (name, url).

## Lifecycle:
Creation:
- Constructor signature: SideBySideLayers(layer_left, layer_right)
    - Required positional arguments:
        - layer_left: left-hand layer (renderable layer-like Element)
        - layer_right: right-hand layer (renderable layer-like Element)
    - During construction the class:
        - calls Layer.__init__(control=False) to initialize Layer metadata with control disabled,
        - sets _name to "SideBySideLayers",
        - stores layer_left and layer_right on the instance,
        - inherits default_js from the class attribute (declared above) and JSCSSMixin behavior is available for render-time registration of the JS asset.
    - No other runtime validation is performed by __init__.

Usage:
- Typical order:
    1. Create the two layers you want to compare (tile/image/feature layers).
    2. Instantiate SideBySideLayers with these two layers.
    3. Add the SideBySideLayers instance to a folium Map or Figure object (Map is the usual container).
    4. Add the individual left and right layers to the same map/container as appropriate (depending on folium usage patterns the plugin may expect those layers to be present in the map DOM).
    5. Render the Map/Figure; at render time:
       - JSCSSMixin will register the JavaScript resource(s) listed in default_js into the Figure header (this requires the element to be attached to a Figure/Map),
       - the frontend script referenced by the registered JS resource will be available to instantiate the side-by-side control in the browser.

- Required sequencing:
    - The SideBySideLayers instance must be attached to a Map/Figure before the folium rendering process is invoked; JSCSSMixin's resource registration happens during render and asserts that a Figure root exists.
    - The supplied layer_left and layer_right should be attached to the Map or otherwise accessible in the DOM when the client-side script runs.

Destruction / cleanup:
- SideBySideLayers implements no explicit destructor or cleanup API. It relies on folium's Element/Map container lifecycle for removal. Any cleanup of the external JS resources or UI components (in the browser) is handled by the client-side library or by removal of the element from the folium Figure DOM.

## Method Map:
flowchart LR
    A[Caller creates layer_left & layer_right] --> B[Call SideBySideLayers(layer_left, layer_right)]
    B --> C[Layer.__init__(control=False) called]
    C --> D[Instance: _name set to "SideBySideLayers"; layer_left/layer_right stored]
    D --> E[Add instance to Map/Figure]
    E --> F[Render Map/Figure]
    F --> G[JSCSSMixin registers default_js to Figure.header]
    G --> H[Client-side JS (leaflet-side-by-side) runs in browser to create UI]

## Raises:
Possible exceptions that can surface during construction and later rendering:

- TypeError
    - Trigger: Python will raise TypeError if the constructor is called with the wrong number of arguments (e.g., missing layer_right). This is a standard Python function-call error, not explicit validation in this class.

- AssertionError (raised at render time, not in __init__)
    - Trigger: if the JSCSSMixin.render logic runs while the element is not attached to a Figure/Map root, JSCSSMixin asserts the root is a Figure and will raise AssertionError. Therefore ensure the instance is added to a Map/Figure before the render pipeline that triggers mixin behavior.

- Any exceptions raised by Layer.__init__ or by downstream rendering
    - Trigger: Layer.__init__ may in other implementations call get_name() or otherwise depend on ancestor behavior. If those calls raise, the exception propagates. Similarly, errors constructing or adding JavascriptLink/CssLink by the JSCSSMixin (during render) will propagate.

Note: SideBySideLayers itself performs no type-checking of layer_left/layer_right; incorrect types will only surface later when rendering or when the client-side JS expects particular DOM elements.

## Example:
1. Prepare two renderable layers (examples: a tile layer of recent imagery and another tile layer of historical imagery).
2. Create the plugin object: instantiate SideBySideLayers(left_layer, right_layer) supplying the two layers as positional arguments.
3. Add the SideBySideLayers instance to the map/figure using the container's add-child (or equivalent) API.
4. Ensure the two underlying layers are also added to the same map so their DOM/tiles will be available.
5. Render the map. During the render:
   - the default_js entry ("leaflet.sidebyside", URL) will be registered into the Figure header by JSCSSMixin,
   - when the map HTML is opened in a browser, the referenced client-side library will create the draggable side-by-side control to compare the left and right layers.

Implementation notes for reimplementation:
- Reimplementing this class requires:
  - subclassing a folium Element/Layer base that accepts control keyword and stores layer metadata,
  - including a mixin or logic that registers the given JS URL(s) into the document head when rendering,
  - storing the two supplied layer objects as instance attributes,
  - setting a stable internal name such as "SideBySideLayers".
- This class intentionally keeps runtime logic minimal and defers rendering and UI behavior to the external JS library referenced in default_js.

### `folium.plugins.side_by_side.SideBySideLayers.__init__` · *method*

## Summary:
Initializes a SideBySideLayers instance by disabling layer controls, assigning a stable internal name, and storing the two supplied layer objects for left/right side-by-side display.

## Description:
- Known callers and context:
    - Typical caller: application code or higher-level folium helper that constructs two renderable layers (tile layers, image overlays, feature groups) and then creates a SideBySideLayers instance to enable a side-by-side comparison UI.
    - Lifecycle stage: invoked at object construction time immediately after creating the left/right layer objects and before adding the SideBySideLayers instance to a Map/Figure. Resource registration (via JSCSSMixin.default_js) and client-side initialization happen later during the folium render pipeline.
- Why this is a distinct method:
    - Encapsulates instance initialization responsibilities (superclass metadata initialization plus storing the two layer references) in a single place. Keeping initialization here avoids duplicating Layer base-class initialization logic and clearly separates construction from render-time behavior (resource registration and client-side UI setup), which belong to mixins and the rendering pipeline.

## Args:
    layer_left (object):
        - Description: Renderable layer-like element intended for the left side of the divider.
        - Expected types: instances of folium Layer-like elements (TileLayer, ImageOverlay, FeatureGroup, or other renderable Element). The class does not enforce a specific type.
        - Allowed values: any Python object that the folium rendering system can handle; passing None or a non-renderable object will not be checked here and will likely fail at render time.
    layer_right (object):
        - Description: Renderable layer-like element intended for the right side of the divider.
        - Expected types and constraints: same as layer_left.
    - Note: Both arguments are required positional parameters; there are no defaults.

## Returns:
    None
    - The constructor does not return a value; it initializes the instance in-place.

## Raises:
    TypeError
        - Condition: Python will raise a TypeError if the constructor is called with an incorrect number of positional arguments (e.g., omitting layer_right). This is the standard Python call-time error.
    Any exception raised by Layer.__init__ (propagated)
        - Condition: Because the constructor calls super().__init__(control=False), any exception raised during the parent initialization can propagate. Examples include:
            - Exception from a missing or failing get_name() implementation if Layer.__init__ attempts to resolve a layer name when no name argument is provided.
            - Any other initialization-time error raised by the Layer base class.
    Note: The SideBySideLayers.__init__ performs no argument type validation itself; errors related to non-renderable layers typically surface later during rendering or client-side execution.

## State Changes:
- Attributes READ:
    - None explicitly read from self by the method body. (The method delegates to Layer.__init__ which may call instance methods such as get_name(); those are not explicit attribute reads in this implementation.)
- Attributes WRITTEN:
    - self._name (str): set to the literal "SideBySideLayers".
    - self.layer_left (object): set to the provided layer_left argument.
    - self.layer_right (object): set to the provided layer_right argument.
    - Attributes set by the superclass call (via super().__init__(control=False)):
        - self.control (bool): set to False (disables inclusion in layer controls).
        - self.layer_name, self.overlay, self.show or equivalent metadata that Layer.__init__ initializes may also be created/overwritten by the parent constructor.

## Constraints:
- Preconditions:
    - The caller must supply two positional arguments (layer_left and layer_right).
    - For correct runtime behavior, layer_left and layer_right should be valid, renderable folium layer-like elements and should be added to the same Map/Figure before rendering.
    - The object should be attached to a Map/Figure before the folium render pipeline triggers mixin-based resource registration (JSCSSMixin requires a Figure root during render).
- Postconditions:
    - The instance will have:
        - control metadata disabled (self.control == False) as initialized by Layer.__init__(control=False).
        - an internal name set (self._name == "SideBySideLayers").
        - references to the two supplied layers stored on self.layer_left and self.layer_right.
    - The class-level default_js remains available (registered later during rendering by JSCSSMixin) and is not modified by this constructor.

## Side Effects:
- No I/O or network operations are performed in this method.
- Calls Layer.__init__(control=False) which mutates instance metadata (control, layer_name, overlay, show); those mutations are side effects of the parent initialization.
- No validation or registration of the provided layers occurs here; any errors related to registering JavaScript/CSS or rendering elements occur later in the render pipeline when the instance is attached to a Map/Figure and the JSCSSMixin is invoked.

