# `scroll_zoom_toggler.py`

## `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler` · *class*

## Summary:
Represents a minimal MacroElement subclass named "ScrollZoomToggler" that carries a Jinja2 template placeholder and an element name; intended as a plugin-like element for folium's templating/rendering system.

## Description:
This class is a very small subclass of branca.element.MacroElement. It declares a class-level _template attribute (a jinja2.Template instance created at class-definition time) and sets the element instance name to "ScrollZoomToggler" during initialization.

Scenarios:
- Instantiate when you need a MacroElement-derived object that identifies itself as "ScrollZoomToggler" and carries a Jinja2 Template object at the class level.
- Typical callers: any code that constructs or registers MacroElement plugins or extensions (for example, a map-building routine that aggregates MacroElement instances). This class itself does not implement rendering or map integration logic — those responsibilities belong to the MacroElement base class and the template content.

Motivation and responsibility boundary:
- This class exists to provide a distinct MacroElement subclass with a named identity and a place to store a Jinja2 template used by the macro-rendering pipeline.
- It intentionally does not implement template content or additional behavior; it is a thin container that relies on MacroElement for lifecycle and rendering.

## State:
Attributes (visible from the source):
- _template (jinja2.Template)
    - Type: jinja2.Template
    - Initialization: created at class definition time via Template() with no arguments in the current source.
    - Valid values: any jinja2.Template instance; in the provided source the Template() call is invoked without content (see caveats in Raises).
    - Invariants: expected to be a Template instance readable by MacroElement rendering code.

- _name (str)
    - Type: str
    - Initialization: set to "ScrollZoomToggler" in __init__.
    - Valid values: any string; by design this instance uses the fixed value "ScrollZoomToggler".
    - Invariants: once constructed, _name should remain a string identifier for the element.

Notes on __init__ parameters:
- The class __init__ takes no parameters and requires no arguments to instantiate.
- No defaulted parameters exist beyond the implicit ones shown in the source.

Class invariants:
- Every instance will have _name == "ScrollZoomToggler" and will reference the class-level _template attribute.
- The effectiveness of this class as a MacroElement depends on the MacroElement base class and on _template being a valid jinja2.Template.

## Lifecycle:
Creation:
- Instantiate with no arguments: instance = ScrollZoomToggler()
- Internally, __init__ calls the MacroElement base constructor via super().__init__() and then sets self._name = "ScrollZoomToggler".

Usage:
- After creation, the object exposes the _name attribute and will reference the class-level _template.
- Typical usage pattern in the broader system:
  - Create instance.
  - Register or add it to a rendering/aggregation container provided by MacroElement consumers (e.g., a map or parent element). (Note: the mechanisms for registration/addition belong to MacroElement and are not implemented here.)

Destruction / cleanup:
- This class does not define any cleanup methods (no close, __exit__, or similar). Resource management is delegated to the MacroElement base class or to external code that uses instances.

## Method Map:
flowchart LR
    A[ScrollZoomToggler.__init__] --> B[MacroElement.__init__ (super call)]
    B --> C[set self._name = "ScrollZoomToggler"]
    C --> D[instance ready: holds _template (class) and _name (instance)]

(Explanation: the only method defined here is __init__, which calls the base class __init__ and then assigns the name.)

## Raises:
- No exceptions are explicitly raised by the ScrollZoomToggler source.
- Caveat: The class-level initialization calls jinja2.Template() with no arguments. Depending on the installed jinja2 version or runtime, calling Template() without a source string may raise a TypeError or other exception at import or class-definition time. If you intend to use this class, ensure _template is initialized with a valid template string or Template-compatible arguments (for example, Template("...")) to avoid such runtime errors.

## Example:
Create an instance and inspect its visible attributes:

1) Instantiate:
    toggler = ScrollZoomToggler()

2) Inspect state:
    assert getattr(toggler, "_name") == "ScrollZoomToggler"
    template_obj = ScrollZoomToggler._template
    # template_obj is the class-level jinja2.Template created at class definition.

3) Integration note:
    # To use this object in rendering, pass it to the host system's MacroElement consumer
    # (for example, an object that accepts MacroElement instances). The actual add/attach
    # mechanism is provided by the MacroElement base class or host code and is not implemented here.

### `folium.plugins.scroll_zoom_toggler.ScrollZoomToggler.__init__` · *method*

## Summary:
Initializes the instance by delegating construction to the MacroElement base class and setting the instance identifier name to the fixed string "ScrollZoomToggler", ensuring the object has the expected element identity for folium/branca rendering pipelines.

## Description:
This constructor is called when an instance of the ScrollZoomToggler MacroElement subclass is created (for example: toggler = ScrollZoomToggler()). Typical callers are map-building or plugin-registration code that constructs MacroElement-derived objects prior to adding them to a map or other container that consumes MacroElement instances.

Lifecycle stage:
- Invocation occurs at object creation time (instantiation).
- After this call returns the instance is ready to be registered/added to MacroElement consumers.

Why this logic is in its own method:
- The constructor must call the MacroElement base class initializer to establish base-class state and then assign a subclass-specific identifier (_name). Keeping this small amount of initialization in __init__ maintains the class's clear responsibility: set up base state and provide a distinct element name used by templating/rendering logic. It is intentionally minimal and not inlined elsewhere because construction semantics belong in the initializer.

## Args:
- None

## Returns:
- None (returns the newly created instance implicitly). No meaningful return value is produced by the method.

## Raises:
- This __init__ function does not explicitly raise exceptions itself.
- Exceptions that may propagate:
    - Any exception raised by MacroElement.__init__ will propagate unchanged.
    - Import-time or class-definition issues are possible if the class-level _template was initialized incorrectly (for example, if jinja2.Template(...) at class definition raised). Those are not raised by this __init__ call but can surface earlier during import.

## State Changes:
- Attributes READ:
    - None explicitly read from self by this method.
    - Note: MacroElement.__init__ (invoked via super().__init__()) may read or modify other attributes; those are implementation details of the base class and not accessed directly here.

- Attributes WRITTEN:
    - self._name (str): set to "ScrollZoomToggler"

## Constraints:
- Preconditions:
    - No arguments are required; the call must be performed on a newly allocated instance of the ScrollZoomToggler class (i.e., as part of normal instantiation).
    - MacroElement base class must be available and its __init__ must be callable.

- Postconditions:
    - After the call completes, self._name is guaranteed to be the string "ScrollZoomToggler".
    - The instance will reference the class-level _template attribute (a jinja2.Template) created at class definition time; the instance is ready for any MacroElement registration/consumption steps provided by the surrounding system.

## Side Effects:
- Calls MacroElement.__init__ via super().__init__(), which may perform additional mutations (registering the instance, setting up internal structures, etc.) depending on MacroElement's implementation.
- No I/O, network calls, or external service interactions are performed directly by this method.

