# `fullscreen.py`

## `folium.plugins.fullscreen.Fullscreen` · *class*

## Summary:
A Folium plugin element that packages the Leaflet Fullscreen control: it records the control's initialization options and declares the external JS/CSS assets required to enable fullscreen behavior in the browser.

## Description:
Fullscreen is a minimal MacroElement subclass (mixed with JSCSSMixin) intended to be instantiated and attached to a Folium Map/Figure to enable a fullscreen control in the rendered output.

When you create a Fullscreen instance you provide configuration options (position, title strings, and other plugin options). The constructor normalizes those options using folium.utilities.parse_options (which camel-cases keys and omits entries with value None) and stores the result in self.options. The class also declares the exact JavaScript and CSS resources required by the leaflet.fullscreen plugin using the class attributes default_js and default_css; the JSCSSMixin base class is responsible for registering those resources on the Figure header at render time.

Typical scenarios:
- Callers create a Fullscreen instance and add it to a Map/Figure (for example via the map/figure add_child API). Rendering the map/figure will cause the document head to include the declared CSS/JS resources and the Fullscreen element to be considered for template rendering and client-side initialization.

Motivation and responsibility:
- Bundle the frontend resource links for the Leaflet fullscreen plugin with a normalized options bag for client-side initialization.
- Keep responsibilities small: this class stores options and resource declarations. Resource registration is handled by JSCSSMixin; template/render plumbing is provided by MacroElement (the exact MacroElement behavior is part of the broader Element/MacroElement system, which is not included here).

## State:
- Class attributes
    - _template (jinja2.Template): Set to Template() in the source. This is an intentionally empty Template() placeholder in the class as shipped.
    - default_js (list[tuple[str, str]]): One entry containing the JavaScript resource name and CDN URL:
        - ("Control.Fullscreen.js", "https://cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.js")
    - default_css (list[tuple[str, str]]): One entry containing the CSS resource name and CDN URL:
        - ("Control.FullScreen.css", "https://cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.css")

- Instance attributes (established in __init__)
    - _name (str): "Fullscreen"
        - Purpose: identifies the element within the Element/MacroElement system.
    - options (dict[str, Any]): Result of calling parse_options(...) with the constructor arguments.
        - Keys: camelCased option names (parse_options transforms snake_case to camelCase).
        - Values: the provided values except any entries exactly equal to None are removed.
        - Typical keys (after camelization) produced from the constructor arguments:
            - position (from position)
            - title (from title)
            - titleCancel (from title_cancel)
            - forceSeparateButton (from force_separate_button)
        - Additional kwargs passed into the constructor are included in options after camelization unless their value is None.
    - Invariants:
        - options is always a dict after construction.
        - default_js/default_css remain class-level iterables of 2-tuples as shown above.

## Lifecycle:
- Creation
    - Constructor signature:
        - position: str = "topleft"
        - title: str = "Full Screen"
        - title_cancel: str = "Exit Full Screen"
        - force_separate_button: bool = False
        - **kwargs: additional option names/values forwarded to parse_options
    - On construction the class:
        1. Calls super().__init__() (MacroElement / Element initialization behavior depends on the broader Element system).
        2. Sets self._name = "Fullscreen".
        3. Calls parse_options(...) with the provided args/kwargs and assigns the result to self.options.

- Usage
    1. Instantiate: fs = Fullscreen(...).
    2. Attach to a Map/Figure via the map/figure add_child API (or equivalent).
    3. When the enclosing Figure/Map is rendered:
        - The JSCSSMixin behavior (provided by folium.elements.JSCSSMixin) will register the entries in default_js and default_css with the Figure.header so the CDN JS/CSS files are included once in the document head.
        - The Fullscreen instance's options dict is available to any rendering/template mechanism used by the Element/MacroElement system for emitting initialization JavaScript; the exact rendering behavior depends on the MacroElement implementation and the _template content (the class _template is an empty Template placeholder in this source).
    - No other runtime API is required on the Fullscreen instance for normal operation.

- Destruction / cleanup
    - Fullscreen implements no teardown or context-manager interfaces. Registered JS/CSS entries are added to the Figure.header during rendering by JSCSSMixin; removing those entries (if needed) must be performed via the Figure/header API or by removing the element before re-rendering.

## Method Map:
flowchart LR
    I[Fullscreen.__init__(position, title, title_cancel, force_separate_button, **kwargs)]
    I --> S[sets self._name = "Fullscreen"]
    S --> O[sets self.options = parse_options(...)]
    O --> A[Add to Map/Figure (map.add_child(fs))]
    A --> R[Render Map/Figure]
    R --> J[JSCSSMixin registers default_js/default_css on Figure.header]
    J --> M[MacroElement/Element rendering pipeline may use _template and self.options]
    M --> E[Client-side initialization (via emitted JS) enables fullscreen control]

(Notes: MacroElement/Element rendering behavior is part of the broader Element system and is not specified here; JSCSSMixin registration behavior is described in its documentation.)

## Raises:
- __init__ (direct)
    - The Fullscreen.__init__ body does not explicitly raise exceptions, but the following errors may propagate:
        - Any exception raised by parse_options (e.g., AttributeError/TypeError when non-string keys are used or camelization fails) will propagate outward.
        - Any exception raised by super().__init__() will propagate (behavior depends on MacroElement implementation).
- During rendering (not in __init__):
    - JSCSSMixin.render (invoked as part of element rendering) may raise AssertionError if the element is rendered outside of a Figure (JSCSSMixin requires a Figure root).
    - Errors constructing or adding header link elements (JavascriptLink/CssLink) or from Figure.header.add_child may propagate during resource registration.

## Example:
- Conceptual usage (Python-like pseudocode):
    1. Create control:
       fs = Fullscreen(position="topright", title="Enter full screen", title_cancel="Exit full screen")
    2. Add to map/figure:
       my_map.add_child(fs)
    3. Render the map/figure (the rendering system will):
       - cause JSCSSMixin to add the two CDN links shown above to the document head,
       - and cause the Fullscreen element to be available to the rendering/template pipeline which can emit client-side initialization code using fs.options.

Notes and implementation hints:
- The class-level default_js and default_css values are the authoritative resource declarations; do not duplicate or change them unless intentionally updating the plugin version.
- Keep passed kwargs to the constructor as simple keyword arguments (strings, booleans, numbers). parse_options expects string keys and will camel-case them; values equal to None are filtered out.
- Because _template is an empty Template() in the shipped source, adding custom template content (if required) is a responsibility of higher-level code or of altering this class's _template; by itself Fullscreen only provides options and resource declarations.

### `folium.plugins.fullscreen.Fullscreen.__init__` · *method*

## Summary:
Initialize the Fullscreen plugin element by setting its identity and storing a normalized options dictionary derived from the provided constructor arguments.

## Description:
- Known callers and call context:
    - Typical callers are application code or libraries that instantiate the plugin and attach it to a Folium Map/Figure (e.g., fs = Fullscreen(...); my_map.add_child(fs)).
    - The constructor is invoked at object creation time (the creation stage of the element's lifecycle). After construction the instance is ready to be added to a Map/Figure and later rendered.
- Why this is a separate method:
    - The constructor centralizes element identity and option normalization so other code (renderers, mixins, and Map/Figure attachment logic) can rely on a consistent instance state (self._name and self.options).
    - Keeping option normalization in __init__ keeps callers simple and defers validation/serialization responsibilities to shared utilities (parse_options) rather than duplicating naming/None-filtering.

## Args:
    position (str, optional): Position hint for the control on the map. Default: "topleft".
        - Expected type: str.
        - Typical values: common Leaflet control positions such as "topleft", "topright", "bottomleft", "bottomright".
    title (str, optional): Label text used for the control's activate/enter-fullscreen UI. Default: "Full Screen".
        - Expected type: str.
    title_cancel (str, optional): Label text used for the control's deactivate/exit-fullscreen UI. Default: "Exit Full Screen".
        - Expected type: str.
    force_separate_button (bool, optional): Whether to force a separate button for canceling fullscreen. Default: False.
        - Expected type: bool.
    **kwargs: Additional keyword options forwarded to parse_options.
        - Keys are expected to be string-like option names (snake_case or other); parse_options will camelCase keys and drop any entries whose value is exactly None.
        - Values can be any Python objects; no coercion is performed by this constructor. Validation (if any) occurs later or elsewhere.

## Returns:
    None.
    - The method initializes instance state and does not produce a return value.

## Raises:
    - Any exception raised by super().__init__() will propagate (depends on MacroElement/Element base behavior).
    - Any exception raised by parse_options(...) will propagate. In particular:
        - AttributeError or TypeError may be raised if kwargs contain non-string keys that camelize/parse_options cannot process.
    - The constructor body itself contains no explicit raise statements; all observed exceptions come from invoked routines.

## State Changes:
- Attributes READ:
    - None (the method does not read any existing self.<attr> fields).
- Attributes WRITTEN:
    - self._name (str): set to "Fullscreen".
    - self.options (dict[str, Any]): set to the result returned by parse_options(...). After assignment this attribute is guaranteed to be a dict (barring exceptions from parse_options).

## Constraints:
- Preconditions:
    - No instance attributes are required to be set prior to calling this constructor (standard object construction). Callers should pass string-like keys for kwargs to avoid camelization errors.
    - If kwargs includes entries with value None, those entries will be omitted from the final options dict (parse_options filters them).
- Postconditions:
    - After successful return:
        - self._name == "Fullscreen"
        - self.options is a dict whose keys are camelCased forms of the provided keyword names (as processed by parse_options) and which contains no entries whose value is exactly None.
        - The provided default argument values are stored via parse_options unless filtered out by explicit None values.

## Side Effects:
    - Calls super().__init__(), which may perform base-class initialization side effects defined by MacroElement (these depend on that base class and are not part of this method).
    - Calls parse_options(...), a pure utility that performs in-memory key camelization and None-filtering (no I/O).
    - The method does not perform I/O, network access, template rendering, or registration of JS/CSS resources itself; resource registration occurs later during rendering via mixin/base-class mechanisms.

