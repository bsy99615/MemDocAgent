# `tag_filter_button.py`

## `folium.plugins.tag_filter_button.TagFilterButton` · *class*

## Summary:
Represents a Folium MacroElement plugin that exposes a Leaflet "tag filter" UI button; it holds runtime options and declares the external JavaScript and CSS assets required by the frontend plugin.

## Description:
TagFilterButton is a small Folium plugin-element that collects configuration data for the leaflet-tag-filter-button frontend control and ensures the control's JS/CSS dependencies are declared for inclusion in the HTML document. Instantiate this class when you want to add a tag-filter UI control to a map so the map's frontend can filter layers/markers by tag.

Typical scenarios:
- Create an instance with the plugin configuration (data + optional display options) and add it to a Folium Map/Figure so it will be rendered into the page.
- When the element is rendered as part of a Figure, the JSCSSMixin will register the entries in default_js and default_css into the Figure header so the browser loads the plugin assets.

Callers / factories:
- User code constructing map UI: TagFilterButton(...) and then adding to a map/figure via the usual Folium Element API (e.g., Map.add_child).
- There are no other factory methods in this class.

Motivation / responsibility boundary:
- Collect and normalize options (via folium.utilities.parse_options) into self.options for later templating/serialization.
- Declare the JS/CSS assets required by the frontend control (default_js/default_css).
- Do not perform rendering or manipulate the Figure header directly; registration of the assets happens during rendering using JSCSSMixin behavior.

## State:
- _template: jinja2.Template
    - Type: jinja2.Template
    - Purpose: template used to render frontend initialization code for this plugin (empty Template object in the current source).
    - Invariant: a Template object is present at the class level (may be empty).
- default_js: list[tuple[str, str]]
    - Type: list of (name, url) tuples
    - Default (class-level): [
        ("tag-filter-button.js", "https://cdn.jsdelivr.net/npm/leaflet-tag-filter-button/src/leaflet-tag-filter-button.js"),
        ("easy-button.js", "https://cdn.jsdelivr.net/npm/leaflet-easybutton@2/src/easy-button.js"),
      ]
    - Valid values: Iterable of 2-tuples (name, url). JSCSSMixin will iterate these and register each url as a JavascriptLink with the Figure header using name as the child name.
    - Invariant: each entry must be a 2-tuple (name, url).
- default_css: list[tuple[str, str]]
    - Type: list of (name, url) tuples
    - Default (class-level): [
        ("tag-filter-button.css", "https://cdn.jsdelivr.net/npm/leaflet-tag-filter-button/src/leaflet-tag-filter-button.css"),
        ("easy-button.css", "https://cdn.jsdelivr.net/npm/leaflet-easybutton@2/src/easy-button.css"),
        ("ripples.min.css", "https://cdn.jsdelivr.net/npm/css-ripple-effect@1.0.5/dist/ripple.min.css"),
      ]
    - Valid values & invariant: same contract as default_js but for CSS entries.
- _name: str
    - Type: str
    - Set in __init__ to "TagFilterButton".
    - Invariant: _name is a non-empty string identifying the element (used by Folium/Branca element system).
- options: dict[str, Any]
    - Type: dict returned from folium.utilities.parse_options
    - Contents: contains camelCased option keys with values that were not None (parse_options converts snake_case keys to camelCase and omits None-valued entries).
    - Keys present: guaranteed keys are those passed to __init__ with non-None values: data, icon, clearText, filterOnEveryClick, openPopupOnHover and any additional kwargs passed in (after camelization) unless a value was None.
    - Invariant: options is a dict (possibly empty) whose keys are camelCased strings and that contains no values equal to None.

Class invariants:
- default_js and default_css remain iterable of 2-tuples and are available at class level for JSCSSMixin to register.
- After construction, self.options is a dictionary (not None) prepared for templating/serialization.

## Lifecycle:
Creation:
- Constructor signature:
    TagFilterButton(
        data,
        icon="fa-filter",
        clear_text="clear",
        filter_on_every_click=True,
        open_popup_on_hover=False,
        **kwargs
    )
- Required argument:
    - data: plugin configuration payload to be passed through to the frontend. The class accepts any Python object for data; parse_options will include it in self.options if it is not None.
- Optional arguments (with constraints):
    - icon (str): default "fa-filter". Any string accepted; will appear in options as icon (after camelization).
    - clear_text (str): default "clear". Any string accepted.
    - filter_on_every_click (bool): default True. Any truthy/falsey value is accepted; parse_options does not coerce types.
    - open_popup_on_hover (bool): default False.
    - **kwargs: additional option keys accepted; keys will be camelized by parse_options and None-valued entries will be omitted.

Usage:
1. Instantiate: create TagFilterButton with desired parameters.
2. Attach to a Folium Map/Figure via the standard Element API (e.g., Map.add_child or equivalent).
3. Rendering: when the element's render method is invoked as part of the Figure render pipeline:
    - JSCSSMixin will attempt to register default_js and default_css entries on the Figure.header before delegating to the remaining rendering logic.
    - The (empty) _template may be used by MacroElement / Branca's rendering machinery if the template is populated in the future.
4. Typical ordering: instantiate -> add to figure/map -> render (resource registration happens at render).

Destruction / cleanup:
- TagFilterButton performs no special cleanup. Resource registration is handled by JSCSSMixin during render and persists in the Figure/header. Removing registered resources (if desired) is the responsibility of the Figure/header API.

## Method Map:
flowchart LR
    Construct[Instantiate TagFilterButton(__init__)] --> ParseOptions[call parse_options(...)]
    ParseOptions --> SetOptions[self.options = dict returned by parse_options]
    Construct --> SetName[self._name = "TagFilterButton"]
    RenderTrigger[Figure.render() / element.render()] --> JSCSSMixinRegister[JSCSSMixin registers default_js/default_css on Figure.header]
    JSCSSMixinRegister --> MacroElementRender[continue with MacroElement rendering/template processing]
    SetOptions --> MacroElementRender

(Construct shows initialization path; RenderTrigger indicates what happens later at render time.)

## Raises:
- Exceptions propagated from folium.utilities.parse_options:
    - parse_options can raise exceptions propagated from its internal camelize implementation (for unusual/non-string keys). In the normal usage here (all keyword argument names are strings), parse_options should not raise. If a calling site passes unexpected key types or if camelize raises, that exception will bubble up from __init__.
    - parse_options will also drop any keys whose values are exactly None — this is not an error, but affects resulting options.
- Errors during rendering (not raised by __init__ but relevant to behavior):
    - AssertionError from JSCSSMixin.render if the element is rendered outside a Figure root (JSCSSMixin requires get_root() to return a Figure). This occurs at render-time, not during construction.
    - Any exceptions raised while creating JavascriptLink/CssLink or adding them to Figure.header will occur during rendering and will propagate to the caller.

## Example:
- Creation and inspection of normalized options (illustrative usage):
    btn = TagFilterButton(
        data=[{"tag": "park", "layerId": "layer1"}],
        icon="fa-filter",
        clear_text="All",
        filter_on_every_click=False
    )
    # After construction:
    # btn._name == "TagFilterButton"
    # btn.options might look like:
    # {
    #   "data": [{"tag": "park", "layerId": "layer1"}],
    #   "icon": "fa-filter",
    #   "clearText": "All",
    #   "filterOnEveryClick": False
    # }
- Typical integration:
    1. Create a TagFilterButton instance (as above).
    2. Add it to your Folium Map/Figure using the regular Element API (e.g., map.add_child(btn)).
    3. Render the map to HTML. During rendering, the JS/CSS URLs declared in default_js and default_css will be registered into the global document header by JSCSSMixin so the client-side plugin code is available.

### `folium.plugins.tag_filter_button.TagFilterButton.__init__` · *method*

## Summary:
Initializes the TagFilterButton plugin instance and stores its configuration by parsing provided options into the instance state.

## Description:
This constructor prepares a TagFilterButton plugin for use with a folium Map by:
- Calling the parent initializer to ensure the object is a valid MacroElement.
- Setting a stable internal name for the element.
- Parsing and storing the plugin configuration/options into self.options using folium.utilities.parse_options.

Known callers and typical context:
- Instantiated by application code or library users when they want to add a tag-filter button to a folium.Map.
- Typical usage: create TagFilterButton(...) and attach it to a folium.Map via map.add_child(tag_filter_button) or tag_filter_button.add_to(map).
- It is invoked at object construction time (plugin creation lifecycle), before the plugin is added to any map or rendered.

Why this logic is isolated:
- Parsing and validation of options are centralized via parse_options; keeping that call in __init__ ensures the instance always holds a canonical, validated options mapping immediately after construction. This separation avoids scattering validation logic across other methods and ensures consistent instance state.

## Args:
    data (any):
        Required. Passed through to parse_options; represents the data structure that the TagFilterButton will use to determine available tags and associated markers. The exact acceptable structure/format is defined by parse_options and the plugin's intended front-end expectations.
    icon (str, optional):
        CSS class for the button icon. Default: "fa-filter".
    clear_text (str, optional):
        Text label used for the "clear" action in the UI. Default: "clear".
    filter_on_every_click (bool, optional):
        If True, clicking a tag toggles filtering immediately on each click. Default: True.
    open_popup_on_hover (bool, optional):
        If True, hovering a tag will open associated popups. Default: False.
    **kwargs:
        Additional keyword options forwarded to parse_options for plugin-specific or future options.

## Returns:
    None
    - As a constructor, it does not return a value. On success, the instance fields (notably self.options) are populated.

## Raises:
    Any exception raised by parse_options will propagate out of this constructor.
    - parse_options may validate the inputs and raise exceptions (TypeError, ValueError, or custom exceptions) if the provided arguments are invalid. Those are not caught here and therefore will be visible to the caller.

## State Changes:
    Attributes READ:
        - None directly read from self in this method (the method does call super().__init__ which may access/initialize parent state, but this method does not explicitly read any existing self.<attr> values).
    Attributes WRITTEN:
        - self._name: set to the literal "TagFilterButton".
        - self.options: set to the value returned by parse_options(...), expected to be a mapping/dictionary-like set of plugin options.

## Constraints:
    Preconditions:
        - parse_options must be available and accept the provided arguments (data, icon, clear_text, filter_on_every_click, open_popup_on_hover, and any extra kwargs).
        - Callers should supply a data argument formatted per the plugin's requirements (see parse_options and TagFilterButton usage documentation). The constructor does not perform additional validation beyond what parse_options performs.

    Postconditions:
        - self._name is set to "TagFilterButton".
        - self.options holds the parsed/normalized options returned by parse_options (typically a dict-like mapping suitable for later template rendering or JavaScript initialization).
        - The instance is ready to be attached to a folium.Map (e.g., via add_to or add_child) and used by rendering logic which will read self.options.

## Side Effects:
    - Calls super().__init__(), which runs parent initialization logic (MacroElement and any mixins).
    - Calls parse_options(...), which may perform validation and transformation of inputs; any side effects or exceptions from parse_options are propagated.
    - No direct I/O, network calls, or filesystem operations are performed here by this method itself.

