# `pattern.py`

## `folium.plugins.pattern.StripePattern` · *class*

## Summary:
Represents a reusable stripe fill pattern element for a Folium Map layer that provides client-side stripe pattern behavior via an external Leaflet.pattern JavaScript plugin.

## Description:
StripePattern is a MacroElement/JSCSSMixin subclass that packages the configuration for a stripe pattern and integrates the required client-side JavaScript dependency. It should be instantiated when a map layer or style needs an on-map repeating stripe pattern (for example, to use as a fill pattern for polygons or shapes). Typical callers are user code that creates map overlays or other plugins which accept a pattern-like object and attach it to a Leaflet layer; the element is attached to a Map when rendered.

Motivation and responsibility boundary:
- StripePattern's responsibility is to collect stripe-specific configuration (angle, widths, colors, opacities) and expose that configuration to the Folium rendering system so the corresponding client-side Leaflet.pattern script can use it.
- It does not itself draw shapes on the map or enforce how the pattern is applied to layers; it only holds options and makes sure the required JavaScript is declared for inclusion in the rendered map HTML.

## State:
- _template (jinja2.Template)
  - Value: An empty Template instance as created in the class body.
  - Invariant: Remains the Template object used by MacroElement for rendering. Source code shows Template() created with no content.

- default_js (list[tuple[str, str]])
  - Value: [("pattern", "https://teastman.github.io/Leaflet.pattern/leaflet.pattern.js")]
  - Purpose: Declares the external JavaScript resource (Leaflet.pattern) required for client-side pattern rendering. Inherits behavior from JSCSSMixin/MacroElement for inclusion.

- _name (str)
  - Set in __init__ to "StripePattern".
  - Purpose: Identifies the element by name to Folium/MacroElement systems.

- options (dict-like)
  - Value: Whatever is returned by folium.utilities.parse_options when called with the provided constructor parameters and any supplied **kwargs.
  - Source: Assigned directly from parse_options(...) call in __init__.
  - Caller constraints: Callers may supply additional keyword options via **kwargs; parse_options will determine the final structure. This component does not validate or transform options beyond delegating to parse_options.

- parent_map (Map | None)
  - Initial value: None (set in __init__).
  - Updated in render(): set to the Map instance found by get_obj_in_upper_tree(self, Map) when the element is being rendered into a parent map.
  - Invariant: Either None (before render) or a reference to the containing folium.folium.Map instance after render() runs.

Constructor parameters (all provided as named parameters with defaults in the signature):
- angle (default 0.5)
  - Passed through to parse_options.
- weight (default 4)
  - Passed through to parse_options.
- space_weight (default 4)
  - Passed through to parse_options.
- color (default "#000000")
  - Passed through to parse_options.
- space_color (default "#ffffff")
  - Passed through to parse_options.
- opacity (default 0.75)
  - Passed through to parse_options.
- space_opacity (default 0.0)
  - Passed through to parse_options.
- **kwargs
  - Any additional keyword options will be forwarded to parse_options and included in options.

Class invariants:
- After construction, _name is "StripePattern", options holds the parse_options result, and parent_map is None.
- After render() runs, parent_map references the Map that contains this element.

## Lifecycle:
Creation:
- Instantiate by calling StripePattern(...) with any subset of the constructor parameters (all have defaults) or additional keyword options. No required positional arguments.

Usage:
1. Create the element: instantiate StripePattern with desired parameters.
2. Add to a folium Map or a layer container that will be attached to a Map. When the parent map is being rendered, StripePattern.render(...) will be called.
3. On render(): parent_map will be resolved using folium.utilities.get_obj_in_upper_tree(self, Map), stored in parent_map, and MacroElement.render(...) will execute to complete rendering (including emitting template and registering default_js through JSCSSMixin/MacroElement behaviors).

Destruction / Cleanup:
- StripePattern holds no external resources or file handles and does not implement explicit cleanup. There is no context manager or close() method; normal Python garbage collection applies. Cleanup of included JavaScript or DOM artifacts is handled client-side by Leaflet/HTML lifecycle, not by this class.

## Method Map:
flowchart TD
    A[__init__] --> B[parse_options(...)] 
    A --> C[_name = "StripePattern"] 
    A --> D[parent_map = None]
    E[add to Map / render called] --> F[render(**kwargs)]
    F --> G[get_obj_in_upper_tree(self, Map)]
    G --> H[parent_map set]
    F --> I[MacroElement.render(**kwargs)]
    I --> J[JSCSSMixin / MacroElement include default_js]

## Raises:
- __init__:
  - Propagates any exceptions raised by super().__init__() (MacroElement / its bases).
  - Propagates any exceptions raised by folium.utilities.parse_options(...) called with the provided arguments.
  - The constructor itself contains no explicit raises; any raised exceptions are from delegated calls above.

- render:
  - Propagates any exceptions raised by get_obj_in_upper_tree(self, Map) or by the superclass render() implementation.

## Example (prose):
1. Create a pattern instance with non-default angle and colors:
   - Instantiate StripePattern(angle=0.8, weight=6, color="#ff0000", space_color="#ffffff").
2. Attach it to a map or to a layer that accepts pattern configuration. When the enclosing Map is rendered to HTML, StripePattern.render() will resolve the parent map and ensure the Leaflet.pattern JavaScript is declared for inclusion.
3. There is no explicit cleanup required by the Python object; after rendering, the generated HTML/JS will apply the pattern client-side when Leaflet draws layers.

Notes and integration hints:
- The exact structure of options and how a map layer consumes them is determined by the external Leaflet.pattern plugin and the folium.utilities.parse_options function; this class intentionally delegates option construction to parse_options and inclusion of the external JS to the JSCSSMixin/MacroElement machinery.
- To understand how options map to client-side fields, inspect the Leaflet.pattern plugin documentation and the parse_options implementation if you need strict schema validation or to add additional option keys.

### `folium.plugins.pattern.StripePattern.__init__` · *method*

## Summary:
Initializes a StripePattern plugin instance by recording a plugin name, parsing and storing rendering options, and preparing the instance to be attached to a Map.

## Description:
This constructor is invoked when a StripePattern object is created — typically by user code that constructs the plugin prior to attaching it to a Map (for example, by calling map.add_child(stripe_pattern) or otherwise adding the plugin to a map). The method centralizes initialization logic so option defaults and option parsing are handled exactly once at construction time rather than being duplicated at attachment time.

It performs three responsibilities:
- Call the parent constructor to perform base MacroElement/JSCSSMixin initialization.
- Normalize and store all pattern-related options via folium.utilities.parse_options so the rest of the plugin code can rely on a single normalized options dict.
- Initialize plugin bookkeeping (name and parent_map).

Keeping this logic in its own method (the class constructor) ensures a StripePattern instance is always in a consistent state immediately after creation and before any later lifecycle steps (rendering, attaching to a map, etc.).

Known callers and lifecycle stage:
- Called when user code or other library code constructs a StripePattern instance. Invocation occurs during object construction (before the plugin is attached to a Map or used for rendering).
- After __init__ returns, typical next steps are adding the instance to a Map or otherwise using the stored options to produce the pattern's JavaScript/CSS output.

## Args:
    angle (float, optional):
        Rotation parameter for the stripe pattern. Default: 0.5.
    weight (int, optional):
        Thickness of the stripe lines. Default: 4.
    space_weight (int, optional):
        Thickness of the spaces between stripes. Default: 4.
    color (str, optional):
        Color used for the stripes (string, commonly a CSS color such as a hex string). Default: "#000000".
    space_color (str, optional):
        Color used for the spaces between stripes (string, commonly a CSS color such as a hex string). Default: "#ffffff".
    opacity (float, optional):
        Opacity applied to the stripe color. Default: 0.75.
    space_opacity (float, optional):
        Opacity applied to the space color. Default: 0.0.
    **kwargs:
        Additional keyword options are accepted and forwarded to folium.utilities.parse_options; any supported extra options should be provided here.

Notes on types and validation:
- The constructor itself does not enforce value ranges; instead it forwards all provided options to parse_options for normalization/validation. The defaults shown reflect the argument defaults in the constructor signature.

## Returns:
    None
    - As a constructor, it does not return a value. The effect is the mutation of instance attributes described below.

## Raises:
    - This method does not explicitly raise exceptions itself.
    - Any exceptions raised by the parent constructor or by folium.utilities.parse_options (for example, due to invalid option types or values) will propagate to the caller.

## State Changes:
Attributes READ:
    - None of self's public attributes are read by this method prior to writing (the method calls super().__init__ which may initialize parent state, but the constructor does not read instance attributes explicitly).

Attributes WRITTEN:
    - self._name: set to the string "StripePattern".
    - self.options: set to the dictionary/object returned by parse_options(...) containing the parsed/normalized options.
    - self.parent_map: set to None (placeholder until the plugin is attached to a Map).

## Constraints:
Preconditions:
    - No preconditions are enforced by this constructor itself; callers may pass values of appropriate types (see Args). Any validation requirements are delegated to parse_options.

Postconditions:
    - After construction returns:
        * self._name == "StripePattern"
        * self.options contains a parsed/normalized mapping for angle, weight, space_weight, color, space_color, opacity, space_opacity and any additional normalized keys from **kwargs
        * self.parent_map is initialized to None

## Side Effects:
    - Calls super().__init__() which runs parent initialization logic (MacroElement/JSCSSMixin). This may register internal base-class state but performs no external I/O here.
    - Calls folium.utilities.parse_options(...) to normalize/validate options; this is a pure/utility operation (no external I/O expected).
    - No network, filesystem I/O, or mutations of objects external to this instance are performed directly by this constructor.

### `folium.plugins.pattern.StripePattern.render` · *method*

## Summary:
Set the element's parent_map to the nearest ancestor Map and then perform the standard MacroElement render pass; updates the object's parent_map attribute prior to template/resource rendering.

## Description:
This method is executed during the rendering phase when a StripePattern element is being rendered as part of a map/figure render pass. Typical callers:
- The MacroElement rendering machinery (i.e., when the element's render method is invoked while producing HTML for a Figure/Map).
- The folium Map render pipeline when get_root().render() or Map.render(...) traverses and renders child elements.

Lifecycle/context:
- Called immediately before the element's template and resource injection are processed so that the pattern can reference the Map it belongs to.
- It exists as a dedicated method because it performs two distinct responsibilities that must run each render: (1) resolve and cache the nearest Map ancestor for later use by the pattern's template/JS, and (2) delegate to the standard MacroElement.render implementation to carry out templating and resource injection. Keeping this logic here centralizes the parent lookup and ensures it always runs before template rendering.

## Args:
    **kwargs: dict
        Arbitrary keyword arguments accepted and forwarded to the superclass render implementation. No keys are consumed by this method itself.

## Returns:
    None
    - The method does not return a value. It calls super().render(**kwargs) and does not return that result.

## Raises:
    ValueError
        - Raised when no Map ancestor can be found by walking the element's _parent chain. This occurs if the StripePattern is not attached to a parent-linked tree that contains a folium.Map instance (get_obj_in_upper_tree will raise ValueError in this case).
    TypeError / other exceptions
        - Propagates exceptions raised by get_obj_in_upper_tree (e.g., if an invalid cls were passed, though that does not happen here) and by the superclass render implementation. Any exceptions raised by super().render(**kwargs) will propagate unchanged.

## State Changes:
    Attributes READ:
        - self._parent (indirectly): read during ancestor traversal performed by get_obj_in_upper_tree(self, Map).
    Attributes WRITTEN:
        - self.parent_map: set to the nearest ancestor that is an instance of folium.folium.Map. This assignment overwrites any previous value.

## Constraints:
    Preconditions:
        - The StripePattern instance should be attached into a parent-linked tree (objects exposing the _parent attribute) that includes a folium.Map ancestor. If not, get_obj_in_upper_tree will raise ValueError.
        - No assumptions are made about the previous value of self.parent_map; it will be overwritten unconditionally.

    Postconditions:
        - If no exception is raised, self.parent_map is guaranteed to reference the nearest Map ancestor (an instance of folium.folium.Map) reached by following successive _parent attributes.
        - The standard MacroElement rendering side effects (template rendering and resource injection) will have been performed via the superclass call.

## Side Effects:
    - Mutates the StripePattern instance by setting self.parent_map.
    - Calls the superclass render implementation (MacroElement.render) which will perform template rendering and resource/JS/CSS injection into the render root; those operations may mutate the root/Figure/Map (for example, registering required JS/CSS resources) and produce output (HTML) as a side effect.
    - No direct I/O is performed by this method itself, but the delegated super().render may perform operations with observable effects on the rendering output.

## `folium.plugins.pattern.CirclePattern` · *class*

## Summary:
Represents a Leaflet pattern of repeated circles used as a fill pattern plugin element. It prepares the pattern configuration (pattern size and circle parameters), exposes those options to templating, and ensures the required Leaflet.pattern JavaScript asset is registered when rendered.

## Description:
CirclePattern should be instantiated when a developer wants to define a reusable circular fill pattern (for example to fill polygons with a repeating circle motif) using the Leaflet.pattern plugin. Typical usage is to create a CirclePattern instance, add it as a child of a Map (or to another element that is ultimately attached to a Map), and let the rendering pipeline attach the pattern resources and include pattern configuration in the rendered output.

Motivation / responsibility boundary:
- Packs together pattern-level options (tile width/height) and circle-specific parameters (radius, stroke weight, color, opacities) into two option dictionaries that are ready for serialization into Leaflet/Leaflet.pattern-friendly keys.
- Declares the external JS dependency required by the Leaflet.pattern plugin via default_js so that the JSCSSMixin base handles resource registration during rendering.
- Locates and records the enclosing Map's name at render-time so templates can reference the map instance in the generated JavaScript.

Known callers / typical creation sites:
- Callers will generally be application code that constructs a folium.Map instance and then creates a CirclePattern and adds it to that map (Map.add_child or equivalent). CirclePattern itself does not attach to a Map; callers must attach it into the Element tree.

## State:
- _template (jinja2.Template)
    - Type: jinja2.Template
    - Value in source: created as Template() (empty template object)
    - Note: template content is empty in the provided source; a real plugin template would normally reference options_pattern and options_pattern_circle to emit JavaScript.

- default_js (list[tuple[str, str]])
    - Type: list of (name, url) pairs
    - Value: [("pattern", "https://teastman.github.io/Leaflet.pattern/leaflet.pattern.js")]
    - Purpose: Declares the external JavaScript resource required by the Leaflet.pattern plugin. JSCSSMixin will register these links on the Figure header during render().

- _name (str)
    - Type: str
    - Value set in __init__: "CirclePattern"
    - Purpose: identification used by the Element/MacroElement machinery.

- options_pattern_circle (dict[str, Any])
    - Type: dict (camelCased keys produced by parse_options)
    - Contents (constructed from __init__ parameters):
        - x (number): horizontal offset of the circle pattern cell (value set to radius + 2 * weight)
        - y (number): vertical offset of the circle pattern cell (same as x)
        - weight (number): stroke weight for the circle outline (constructor param)
        - radius (number): radius of the circles (constructor param)
        - color (str): stroke color (constructor param)
        - fillColor (str): fill color (from constructor fill_color)
        - opacity (number): stroke opacity (constructor param)
        - fillOpacity (number): fill opacity (constructor param)
        - fill (bool): always True (set in constructor)
    - Note: keys result from parse_options, which camelizes Python names (e.g., fill_color -> fillColor) and removes None values.

- options_pattern (dict[str, Any])
    - Type: dict
    - Contents (constructed from __init__ parameters):
        - width (number): pattern tile width (constructor param)
        - height (number): pattern tile height (constructor param)

- parent_map (str or None)
    - Type: str or None
    - Initial value: None
    - Set during render(): assigned to the enclosing Map object's name by calling get_obj_in_upper_tree(self, Map).get_name()
    - Semantics: a string identifier (the Map.get_name() return) used by templates/JS emitted at render-time to reference the map instance. If the element is not attached underneath a Map, accessing parent_map requires calling render() first and will raise (see Raises).

Constructor (__init__) parameters and their default values (notes about expected types/semantics):
- width (default 20) — pattern tile width. Typical: positive int/float. Not validated by CirclePattern.
- height (default 20) — pattern tile height. Typical: positive int/float.
- radius (default 12) — radius of each circle. Typical: non-negative number.
- weight (default 2.0) — stroke thickness for circles. Typical: non-negative number.
- color (default "#3388ff") — stroke color string (e.g., hex or CSS color).
- fill_color (default "#3388ff") — fill color string.
- opacity (default 0.75) — stroke opacity; typical range [0.0, 1.0] but not enforced by this class.
- fill_opacity (default 0.5) — fill opacity; typical range [0.0, 1.0] but not enforced.

Class invariants:
- options_pattern and options_pattern_circle are always dictionaries (returned by parse_options) constructed in __init__.
- parent_map is None until render() is called; after render() succeeds it holds the enclosing Map's name (string).
- default_js remains a list/sequence of (name, url) pairs and is used by JSCSSMixin during rendering.

## Lifecycle:
Creation:
- Instantiate with optional args shown above. No required positional arguments.
- Example: cp = CirclePattern(radius=8, weight=1.5, color="#000000")

Attachment:
- The instance must be added into an Element tree that contains a Map ancestor (for example, m.add_child(cp) where m is a folium.Map); otherwise render() will fail when locating the Map.

Rendering / Usage:
1. Add CirclePattern instance into the Map (or into another MacroElement that is attached to the Map).
2. When the rendering pipeline calls CirclePattern.render(**kwargs):
    a. get_obj_in_upper_tree(self, Map) is invoked to find the nearest Map ancestor.
    b. parent_map is set to the returned Map object's name via get_name().
    c. super().render(**kwargs) is called to continue normal rendering. Because CirclePattern mixes in JSCSSMixin, default_js entries will be registered on the Figure header at render-time by the mixin before the rest of the element rendering proceeds.
3. A template (not present in the provided source) would typically use options_pattern and options_pattern_circle and parent_map to emit the JavaScript that registers the pattern with the Leaflet instance.

Destruction / cleanup:
- CirclePattern does not implement explicit cleanup. It relies on the Element/Figure lifecycle; resource registration is performed on the Figure header by JSCSSMixin and remains in that header. There is no context manager or close() method for CirclePattern.

Sequencing requirements:
- render() must be invoked after the CirclePattern is attached to a tree that includes a Map ancestor. The call to get_obj_in_upper_tree(self, Map) will raise ValueError if no Map ancestor exists.

## Method Map:
flowchart LR
    __init__ --> set_options_pattern["set options_pattern via parse_options(width,height)"]
    __init__ --> set_options_circle["set options_pattern_circle via parse_options(x,y,weight,radius,color,fillColor,opacity,fillOpacity,fill)"]
    __init__ --> set_name["_name = 'CirclePattern'"]
    __init__ --> parent_map_None["parent_map = None"]
    render --> find_map["get_obj_in_upper_tree(self, Map)"]
    find_map --> set_parent_map["parent_map = found_map.get_name()"]
    set_parent_map --> super_render["super().render(**kwargs)"]
    super_render --> JSCSSMixin_register["JSCSSMixin registers default_js on Figure header"]


## Raises:
- ValueError:
    - Condition: raised by get_obj_in_upper_tree(self, Map) inside render() when no Map ancestor is present in the Element parent chain.
    - Effect: render() will not complete and parent_map will remain unset (or unchanged).

- Exceptions propagated from parse_options (possible at construction time):
    - TypeError / AttributeError etc. if parse_options / its helper camelize cannot handle the constructed keys (extremely unlikely here because keys are standard strings) or if provided argument types are incompatible with downstream expectations.
    - Note: CirclePattern does not explicitly validate types or ranges of numeric/color arguments; invalid values may not raise here but could lead to runtime errors or incorrect behavior in the browser/plugin.

- Any exceptions raised by super().render(**kwargs):
    - These will propagate. In particular, JSCSSMixin.render will assert that the element is attached to a Figure (via get_root()) — if that assertion fails, rendering will raise AssertionError (propagated from JSCSSMixin behavior).

## Example:
- Create a map, add a CirclePattern, and trigger rendering (Map.render() or Figure render will invoke element.render()):

    from folium.folium import Map
    # Instantiate map
    m = Map(location=[0, 0], zoom_start=2)

    # Create a circle pattern with defaults
    pattern = CirclePattern()  # width=20, height=20, radius=12, weight=2.0, etc.

    # Attach to the map
    m.add_child(pattern)

    # Render the map (this will call pattern.render() as part of the pipeline):
    m.render()  # during render: get_obj_in_upper_tree finds Map, parent_map is set, default_js registered

Notes:
- Because the supplied _template in the source is empty, this class as given will not itself emit JavaScript for registering the pattern; the constructor prepares options and JSCSSMixin ensures the external plugin script is included during render. In a full implementation the template would reference options_pattern and options_pattern_circle and parent_map to register the pattern with the Leaflet.pattern plugin.
- The constructor does not enforce numeric or color value ranges; callers should pass sensible values (opacity in [0,1], positive width/height/radius) to avoid unexpected rendering behavior in the browser.

### `folium.plugins.pattern.CirclePattern.__init__` · *method*

## Summary:
Initializes a CirclePattern plugin instance by preparing two normalized option dictionaries (one for the pattern tile size and one for the circle drawn inside the tile), sets the element name, and initializes parent_map to None.

## Description:
This constructor is invoked when user code or other components instantiate a CirclePattern (i.e., at object creation time, before the instance is added to any Map). Its responsibilities are limited to preparing instance state needed to render a repeating circle pattern (the tile dimensions and the circle's drawing parameters) and calling the superclass constructor.

Why this logic is a separate method:
- Keeps object construction focused: it centralizes option normalization and initial attribute setup so other methods (e.g., add_to/map-attachment or rendering helpers) can assume these attributes exist and are correctly normalized.
- Reuses parse_options to ensure keys are converted to camelCase and None-valued entries are dropped, matching the front-end/Leaflet expectation for option shapes.

Known callers and context:
- Any code that creates a CirclePattern instance (for example, application code building a folium map with patterned fills). Typical lifecycle: instantiate CirclePattern -> (optionally) configure -> add the instance to a Map or another container element.

## Args:
    width (int | float) = 20
        Tile width for the repeating pattern. Supplied value is passed through parse_options and will be camelCased as "width" in the resulting dict. No type enforcement is performed here by this constructor.
    height (int | float) = 20
        Tile height for the repeating pattern. Supplied value is passed through parse_options and will be camelCased as "height".
    radius (int | float) = 12
        Radius of the circle that will be drawn inside each pattern tile. Used to compute the circle's center offsets (x and y). Value is forwarded to parse_options under the key "radius".
    weight (float) = 2.0
        Stroke weight (thickness) of the circle's outline. Used in the x/y computation and forwarded to parse_options under the key "weight".
    color (str) = "#3388ff"
        Stroke color for the circle. A color string (e.g., hex or named color); forwarded to parse_options as "color".
    fill_color (str) = "#3388ff"
        Fill color for the circle. Forwarded to parse_options as "fillColor" (camelCased).
    opacity (float) = 0.75
        Stroke opacity for the circle (expected in the 0..1 range but not enforced here). Forwarded to parse_options as "opacity".
    fill_opacity (float) = 0.5
        Fill opacity for the circle (expected in the 0..1 range but not enforced here). Forwarded to parse_options as "fillOpacity".

Notes on argument handling:
- The constructor does not perform explicit type or range validation. Each argument is passed to folium.utilities.parse_options which converts Python-style names to camelCase and omits any entries whose value is exactly None.
- If a caller passes None for any of these arguments, parse_options will drop that key from the resulting options dict.

## Returns:
    None
    (As a constructor, it initializes instance attributes and returns the new object; there is no explicit return value.)

## Raises:
    - No exceptions are raised explicitly by this constructor.
    - Indirect exceptions that may propagate:
        * Any exception raised by parse_options (for example, if underlying camelize fails, although this is unlikely given that keys here are literal strings).
        * Any exception raised by the superclass initializer invoked via super().__init__().
    These are not raised by this method's own logic but may surface to callers.

## State Changes:
Attributes READ:
    - None of self.<attr> fields are read prior to assignment in this constructor. (The constructor reads only its input arguments.)
Attributes WRITTEN:
    - self._name: set to "CirclePattern".
    - self.options_pattern_circle: set to the dict returned by parse_options for the circle-specific options.
    - self.options_pattern: set to the dict returned by parse_options for the pattern tile options.
    - self.parent_map: initialized to None.

Concrete assignment details:
- options_pattern_circle is created by calling parse_options with the following keyword args:
    x = radius + 2 * weight
    y = radius + 2 * weight
    weight = weight
    radius = radius
    color = color
    fill_color = fill_color
    opacity = opacity
    fill_opacity = fill_opacity
    fill = True
  After parse_options, keys are camelCased (e.g., "fill_color" -> "fillColor") and any value passed as None would be omitted.
- options_pattern is created by calling parse_options with:
    width = width
    height = height
  After parse_options, keys are camelCased (no change for these names).

## Constraints:
Preconditions:
    - No explicit preconditions enforced by the constructor. Callers are expected to provide sensible values (numeric widths/heights/radii/weights and valid color strings), but these are not validated here.
Postconditions:
    - self._name == "CirclePattern"
    - self.options_pattern_circle is a dict whose keys are the camelCased names of the provided circle-related args; the dict will include computed "x" and "y" entries (both equal to radius + 2 * weight) and an explicit "fill": True entry (subject to parse_options behavior: None-valued keys would be removed, but in this constructor the explicit fill=True will be present).
    - self.options_pattern is a dict containing camelCased "width" and "height" entries (unless the caller passed None for one of them, in which case that entry would be omitted).
    - self.parent_map is set to None.

## Side Effects:
    - Calls super().__init__() to run parent-class initialization logic. Specific side effects of the superclass initializer (if any) are not described here.
    - Calls folium.utilities.parse_options twice. parse_options performs in-memory normalization (camel-casing of keys and removal of None-valued keys); it does not perform I/O or network access.
    - No file, network, or other external I/O is performed by this constructor.

### `folium.plugins.pattern.CirclePattern.render` · *method*

## Summary:
Resolve and record the enclosing Map's identifier on the element, then invoke the superclass render routine. The element's state is updated to reflect which Map contains it; the method itself does not return a value.

## Description:
This method performs a small pre-render setup and then delegates rendering work to the superclass:

- It locates the nearest ancestor that is an instance of folium.folium.Map by walking the element's _parent links and stores that Map's name/identifier on self.parent_map.
- It calls the superclass render implementation with the provided keyword arguments to perform the remainder of the rendering work.

Known callers / lifecycle stage:
- Typically invoked during the rendering phase when a parent/container (for example, a Map or Figure) walks its children and calls each child's render method. The exact call sites are part of the broader rendering pipeline, not this method.
- It exists as part of the element's render lifecycle and is executed immediately before the element's templating/resource-registration behavior handled by the superclass.

Why this is a separate method:
- Isolates Map-resolution logic required for templating or JS generation from the generic rendering logic in the superclass. This ensures self.parent_map is available to templates or resource registration performed by the superclass.

## Args:
    **kwargs: dict
        Arbitrary keyword arguments forwarded unchanged to the superclass render method. The method does not inspect or mutate kwargs.

## Returns:
    None
        The method does not return the superclass's return value; it implicitly returns None.

## Raises:
    ValueError
        Raised by get_obj_in_upper_tree(self, Map) if no ancestor of type Map is found in the _parent chain. The ValueError message indicates that the top of the tree was reached without finding the requested class.
    AttributeError
        If the found Map ancestor does not expose a get_name() method (or if get_name is not callable), calling .get_name() will raise AttributeError.
    Any exception raised by the superclass render implementation
        Exceptions raised inside super().render(**kwargs) propagate out of this method unchanged.

## State Changes:
    Attributes READ:
        - self._parent (indirectly): traversed by get_obj_in_upper_tree to locate a Map ancestor.
    Attributes WRITTEN:
        - self.parent_map: assigned to the string/identifier returned by the enclosing Map's get_name().

## Constraints:
    Preconditions:
        - The element must be attached into a parent-linked tree where following _parent references upward will encounter an instance of folium.folium.Map; otherwise get_obj_in_upper_tree will raise ValueError.
        - The discovered Map ancestor must implement a get_name() method that returns the desired identifier.
    Postconditions:
        - On successful completion, self.parent_map is set to the value returned by Map.get_name() on the enclosing Map.
        - The method returns None (no return value).
        - Any side effects produced by super().render(**kwargs) (such as template rendering, resource registration, or child rendering) will have been performed; this method does not alter or suppress those side effects.

## Side Effects:
    - Mutates the element by setting self.parent_map.
    - Invokes get_obj_in_upper_tree (read-only traversal of _parent links; no I/O or global mutation).
    - Calls super().render(**kwargs), which may perform templating, resource injection, child rendering, or other side effects depending on the superclass implementation; those effects are implementation-dependent and not modified by this method.

