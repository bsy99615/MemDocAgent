# `terminator.py`

## `folium.plugins.terminator.Terminator` · *class*

## Summary:
Declares the external Leaflet "terminator" JavaScript resource for use in a folium document and identifies the element as "Terminator". It is a minimal plugin-like Element whose primary role is resource declaration; it does not itself implement rendering logic.

## Description:
Terminator is a small Element-style class intended to be instantiated and attached to a folium Figure/Map so that the external script @joergdietrich/leaflet.terminator is made available in the rendered HTML document. The class combines:
- a class-level default_js list that names the external script URL, and
- an empty jinja2 Template object placed on the class as _template.

Behavioral responsibilities and boundaries:
- Responsibility: declare and expose the external JS resource via default_js and set an element name via _name.
- Resource registration: actual registration of default_js into the Figure header is performed by the JSCSSMixin (mixed into this class). JSCSSMixin requires that the element be attached to a Figure at render time; see JSCSSMixin documentation for exact preconditions and failure modes.
- Template rendering and how the _template is used are handled by the superclass chain (branca.element.MacroElement or other Element machinery). Terminator makes no assumptions about how that machinery works; it only provides the _template attribute.
- Terminator performs no validation of its default_js entries at construction time.

Scenarios for instantiation:
- When a map or plugin requires the @joergdietrich/leaflet.terminator client library to be loaded into the document head, create a Terminator instance and add it to the Map/Figure element tree prior to rendering.

Known callers/factories:
- Direct instantiation by application code (Terminator()) is expected. No factory methods exist on the class.

## State:
- Class attributes:
    - _template: jinja2.Template
        - Value in source: an empty jinja2.Template instance (Template()).
        - Constraint: must be an instance of jinja2.Template. The class provides the attribute; subclasses may replace it with a non-empty template if they need to inject HTML/JS content.
    - default_js: list[tuple[str, str]]
        - Value in source: [("terminator", "https://unpkg.com/@joergdietrich/leaflet.terminator")]
        - Each element must be a 2-tuple (name, url). JSCSSMixin iterates with "for name, url in self.default_js"; non-2-tuple entries will cause unpacking errors during rendering.
        - This attribute is a class-level declaration. Subclasses should override it at class definition time rather than mutating the inherited list to avoid shared-mutable-state issues.
- Instance attributes set by __init__:
    - _name: str
        - Value after construction: "Terminator"
        - Purpose: identifier used by the Element system; no additional semantics are introduced by this class.
- Class invariants:
    - default_js remains iterable of 2-tuples for the class lifetime.
    - _template is a jinja2.Template instance.
    - Every Terminator instance created via the provided constructor will have _name equal to "Terminator" unless the caller mutates it.

## Lifecycle:
- Creation:
    - Constructor signature: Terminator()
    - The constructor calls super().__init__() and then sets self._name = "Terminator".
    - No constructor arguments are accepted by this class.
- Usage (typical sequence):
    1. Instantiate the element with no arguments.
    2. Add the instance to a Map/Figure element tree using the Map/Figure API provided by the folium/branca Element system.
    3. Trigger rendering of the Figure/Map (for example, saving or rendering the map). At render time:
        - JSCSSMixin (present in the MRO) is responsible for registering entries from default_js into the Figure.header so that the external script URL is emitted in the HTML head. The element must be attached to a Figure for this to succeed.
        - The Element/MacroElement rendering machinery will (if implemented by the superclass) process the class-level _template and any additional rendering hooks; Terminator itself does not add rendering behavior.
- Destruction / cleanup:
    - Terminator holds no resources that require explicit cleanup. Any removal or de-registration of header resources is the responsibility of the Figure/header API or calling code.

## Method Map:
flowchart LR
    A[Terminator.__init__] --> B[call super().__init__()]
    B --> C[set self._name = "Terminator"]
    C --> D[instance exists with default_js declared at class-level]
    D --> E[When element is added to Figure and Figure.render() invoked]
    E --> F[JSCSSMixin registers each (name,url) from default_js on Figure.header]
    E --> G[Superclass Element/MacroElement rendering may use _template to inject content]

(Note: rendering details for MacroElement are external to this class and not asserted here.)

## Raises:
- __init__:
    - Terminator.__init__ does not explicitly raise exceptions itself.
    - Exceptions may be raised by super().__init__(); those are inherited from the superclass and depend on its implementation.
- Rendering-time exceptions (not raised by Terminator code directly, but possible when using Terminator):
    - AssertionError from JSCSSMixin if the element is not attached to a Figure at render time (see JSCSSMixin).
    - ValueError or TypeError during iteration/unpacking if default_js contains entries that are not 2-tuples.
    - Exceptions propagated from Figure.header.add_child if header registration fails (duplicate names, invalid child type, etc.).

## Example (prose steps):
- To use Terminator in a folium map:
    1. Prepare a folium Map or Figure object that will serve as the document root.
    2. Create a Terminator instance (no arguments required).
    3. Add the Terminator instance to the Map/Figure element tree via the map/figure API.
    4. Render or save the Map/Figure. During rendering, JSCSSMixin will ensure the script URL "https://unpkg.com/@joergdietrich/leaflet.terminator" is registered into the document head under the name "terminator" so that client-side code can use the library.
- To extend behavior:
    - Subclass Terminator and replace the class-level _template with a jinja2.Template containing initialization JavaScript that uses the registered script. Ensure default_js remains an iterable of (name, url) pairs.

References:
- JSCSSMixin documentation: explains how default_js/default_css are registered with a Figure.header and the requirement that the element be attached to a Figure before rendering.
- branca.element.MacroElement (external): Terminator provides a _template attribute; how that template is consumed depends on the MacroElement implementation and is not specified here.

### `folium.plugins.terminator.Terminator.__init__` · *method*

## Summary:
Initializes a Terminator plugin instance by delegating common setup to parent classes and setting the plugin identity string on the instance.

## Description:
Known callers and lifecycle:
- Called when a Terminator object is instantiated (e.g., by user code creating the plugin or by higher-level code that constructs plugin instances during map/plugin setup).
- Invoked at object construction time — this is the first user-facing lifecycle step for the plugin instance.

Why this logic is its own method:
- The constructor centralizes instance initialization: it delegates generic initialization to parent classes (ensuring MacroElement and JSCSSMixin behavior is established) and then sets the plugin-specific identity (_name). Keeping this minimal constructor makes the class consistent with other folium plugin implementations and separates generic parent initialization from subclass-specific state.

## Args:
- None

## Returns:
- None (constructor). No return value; the method's effect is to configure the new instance.

## Raises:
- None explicitly raised by this method. Any exceptions may come from parent class constructors invoked by super().__init__ (propagated as-is).

## State Changes:
Attributes READ:
- None (this method does not read any existing self.<attr> fields).

Attributes WRITTEN:
- self._name (str): set to "Terminator".

Additionally, by calling super().__init__(), this method causes the parent class initialization to run which may create or mutate other internal attributes belonging to MacroElement or JSCSSMixin.

## Constraints:
Preconditions:
- None required from callers. The method assumes a valid object is being constructed (Python ensures self is a new instance).

Postconditions:
- self._name is defined and equals the string "Terminator".
- Parent class initialization has completed (whatever state MacroElement and JSCSSMixin establish is guaranteed as if their __init__ methods were executed).

## Side Effects:
- Calls super().__init__() which triggers initialization behavior in parent classes (MacroElement, JSCSSMixin or their bases). Those parent initializers may register templates, set up internal fields, or perform other non-local mutations; this method itself performs no I/O and does not call external services.

