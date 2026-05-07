# `renderable.py`

## `src.ydata_profiling.report.presentation.core.renderable.Renderable` · *class*

## Summary:
Renderable is an abstract base type representing an item that can produce a presentation output (via render) and that carries generic metadata in a content dictionary (including optional name, anchor_id, and classes).

## Description:
Renderable is intended as the minimal protocol/abstraction for presentation elements in the reporting system. Concrete renderable types (subclasses) implement the render() method to produce a representation suitable for the output pipeline (HTML fragment, JSON structure, widget object, etc.). Typical callers are report builders and presentation factories that:
- create concrete subclass instances (or convert existing plain objects into a Renderable subclass via convert_to_class),
- read metadata (name, anchor_id, classes) for layout or navigation,
- call render() when composing the final output.

Motivation and responsibility boundary:
- Intent: separate metadata (content dict) from rendering logic so that many different output kinds can be produced from the same metadata-driven structure.
- Responsibility: store and expose generic metadata and mandate a render() contract. It does not implement rendering itself, nor manage resource lifecycles beyond holding the content dict. It also provides a utility to mutate an object's class for dynamic conversion (convert_to_class), but that utility does not alter content.

Known usage patterns:
- Instantiate a concrete subclass with a content dict (or supply name/anchor_id/classes to be inserted into content).
- Call properties name/anchor_id/classes to access metadata (these expect the keys to exist in content).
- Call render() on concrete subclass instances to obtain presentation output.
- Optionally call Renderable.convert_to_class(sub_obj, flv) to change sub_obj's runtime class to a Renderable subclass (see warnings below).

## State:
- content: Dict[str, Any]
  - Purpose: primary storage for all data and metadata for the renderable object.
  - Constraints: must be a mutable mapping (dict-like). The class stores the object as-is; it does not copy it.
  - Invariants: content is expected to remain a mapping while the instance is in use. Keys commonly present:
    - "name": str — optional; if present accessible via name property.
    - "anchor_id": str — optional; if present accessible via anchor_id property.
    - "classes": str — optional; if present accessible via classes property.
  - Notes: the constructor will write the above keys if corresponding init parameters are provided; otherwise those keys are not created automatically. The properties assume the keys exist and will raise KeyError if they are absent.

- name (property) -> str
  - Accessor reading content["name"].
  - Valid values: any value stored under content["name"]; callers typically expect str.
  - Behavior: raises KeyError if "name" not present in content.

- anchor_id (property) -> str
  - Accessor reading content["anchor_id"].
  - Behavior: raises KeyError if "anchor_id" not present in content.

- classes (property) -> str
  - Accessor reading content["classes"].
  - Behavior: raises KeyError if "classes" not present in content.

Class invariants:
- content remains a dictionary-like object for the lifetime of the instance.
- If the instance was created with name/anchor_id/classes parameters, the corresponding keys exist in content for all subsequent method calls.
- Subclasses must not assume additional internal attributes exist unless they document and maintain them; the Renderable base guarantees only the presence of content and the three optional keys.

## Lifecycle:
Creation:
- Constructor signature:
  - content: Dict[str, Any] (required)
  - name: Optional[str] = None
  - anchor_id: Optional[str] = None
  - classes: Optional[str] = None
- Behavior:
  - Stores the provided content dict as self.content (no copy).
  - If name is not None, writes content["name"] = name.
  - If anchor_id is not None, writes content["anchor_id"] = anchor_id.
  - If classes is not None, writes content["classes"] = classes.
- Notes for callers:
  - Provide a mutable mapping; the instance will share it by reference.
  - If you plan to access the name/anchor_id/classes properties, either supply them via constructor or include corresponding keys in the content dict before passing it in.

Usage:
- Sequence:
  1. Instantiate a concrete subclass (or convert an object into a Renderable subclass using convert_to_class).
  2. Optionally read metadata via name, anchor_id, classes.
  3. Call render() on the concrete subclass to obtain the output. The render method is abstract in this base class and must be implemented by subclasses.
  4. Use __str__ to obtain the class name for logging or debugging.
- Required ordering:
  - There is no required strict method ordering enforced by the class; however, calling properties that expect keys before those keys exist will raise KeyError.
  - render() should be implemented and callable at any point after instantiation.

Destruction / cleanup:
- Renderable does not manage external resources and provides no close() or context manager behavior.
- If a subclass allocates external resources, that subclass is responsible for implementing appropriate cleanup.

## Method Map:
- Methods and relations (textual summary):
  - __init__: initialize state (content and optional keys)
  - properties: name, anchor_id, classes -> read content keys
  - render (abstract): subclass must implement
  - __str__: returns class name
  - convert_to_class (classmethod): mutate obj.__class__ to this class; flv parameter is accepted but unused by the base.

- Mermaid diagram (flowchart):
flowchart TD
    A[Create instance: __init__(content, name?, anchor_id?, classes?)] --> B{content contains keys?}
    B -->|yes| C[Properties: name/anchor_id/classes read directly from content]
    B -->|no| C
    C --> D[Call render() on concrete subclass]
    D --> E[Use render output in report pipeline]
    E --> F[Optional: logging -> __str__ returns class name]
    A --> G[Optional: Renderable.convert_to_class(obj, flv) -> mutates obj.__class__]
    G --> D

## Raises:
- __init__: No exceptions are explicitly raised by the constructor itself (assuming a dict-like content is supplied). However:
  - If content is not a mapping and does not support item assignment (content["key"] = value), constructor assignments for name/anchor_id/classes will raise the underlying exception (e.g., TypeError).
- name / anchor_id / classes properties:
  - KeyError: if the requested key ("name", "anchor_id", or "classes") is not present in self.content.
  - TypeError/AttributeError: may be raised if self.content is mutated to a non-mapping during the instance lifetime.
- convert_to_class:
  - TypeError: Python can raise a TypeError when assigning to obj.__class__ if the new class is incompatible with the object's current layout (this is a Python-level constraint, e.g., when changing between built-in extension types or classes with incompatible C layouts). convert_to_class does not catch or translate these exceptions.
- Subclass render(): any exceptions raised by render are determined by subclass implementations.

## Implementation notes and constraints:
- convert_to_class signature accepts flv: Callable but the base implementation ignores that argument. It exists for API compatibility; callers may pass a factory or descriptor but the base implementation only writes obj.__class__ = cls.
- Because the base class stores the provided content by reference, mutating the content after construction will affect the Renderable instance (and vice versa).
- Properties assume the presence of the corresponding keys. To safely access metadata, callers should either:
  - ensure the content dict contains the keys before constructing the Renderable, or
  - use content.get("name") / get("anchor_id") directly on the instance's content dict to avoid KeyError.

## Example:
- Typical usage (illustrative, not a subclass implementation):
1) Prepare content and instantiate a subclass:
    content = {"data": {"value": 123}}
    r = SomeConcreteRenderableSubclass(content, name="summary", anchor_id="sec-1", classes="card")
2) Read metadata:
    section_name = r.name         # "summary"
    anchor = r.anchor_id          # "sec-1"
3) Render for output:
    output_fragment = r.render()
4) Logging:
    label = str(r)                # class name of r (e.g., "SomeConcreteRenderableSubclass")
5) Convert an existing object into a Renderable subclass (advanced/dangerous):
    RenderableSubclass.convert_to_class(existing_obj, lambda x: x)
   - Warning: convert_to_class mutates existing_obj.__class__ and may raise TypeError if classes are incompatible. Use sparingly and only with compatible plain Python objects.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__init__` · *method*

## Summary:
Initializes the Renderable instance by storing the provided content mapping on the object and, if provided, injects optional presentation metadata keys ("name", "anchor_id", "classes") into that content mapping.

## Description:
This constructor sets up the object's primary payload (self.content) for later rendering. It is invoked when a Renderable (or a subclass) instance is created — i.e., during object construction in the report rendering pipeline — and therefore runs as the first lifecycle step for any renderable component. The separation of this logic into its own initializer centralizes the canonical content normalization (ensuring the content mapping always exists as an attribute and optionally contains standard metadata keys) rather than duplicating that normalization in each subclass or external factory.

Known callers and context:
- Called whenever code constructs a Renderable or a subclass instance (for example, any code that performs Renderable(...) to create a renderable node in the report). There are no callers visible in this small snippet; the initializer is the natural entry point for all instance creation.

Why this is a separate method:
- The initializer is responsible for establishing the instance's state and performing minimal normalization of the provided content mapping. Keeping this behavior here ensures consistent handling of the content mapping across all subclasses and centralizes mutation of the content mapping.

## Args:
    content (Dict[str, Any]):
        A mapping that holds the payload for this renderable. Must support item assignment (i.e., content[key] = value). This mapping is stored directly on the instance (no deep copy) and therefore will be mutated in-place.
    name (Optional[str], optional):
        If provided (not None), the initializer will set content["name"] = name. Default: None.
    anchor_id (Optional[str], optional):
        If provided (not None), the initializer will set content["anchor_id"] = anchor_id. Default: None.
    classes (Optional[str], optional):
        If provided (not None), the initializer will set content["classes"] = classes. Default: None.

## Returns:
    None
    The initializer does not return a value; it constructs and mutates object state.

## Raises:
    TypeError:
        Triggered if the provided content object does not support item assignment and any of name, anchor_id, or classes is not None (e.g., content is None or an immutable mapping). The assignment content["..."] = ... will raise TypeError in such cases.
    Any exception raised by the caller-provided mapping on item assignment:
        If content implements custom behavior and raises other exceptions on item assignment, those will propagate.

## State Changes:
    Attributes READ:
        None from self are read prior to assignment.
    Attributes WRITTEN:
        self.content is assigned to the provided content object.
        The provided content object may be mutated in-place by adding the keys "name", "anchor_id", and/or "classes" when the corresponding arguments are not None.

## Constraints:
    Preconditions:
        - The caller must provide a mapping-like object for content (per the type annotation Dict[str, Any]). If name/anchor_id/classes are to be set, the mapping must support item assignment.
        - No other preconditions (there is no validation of key types or duplication of keys).
    Postconditions:
        - After initialization, self.content references the same object passed as content.
        - If name was not None, self.content["name"] equals the provided name.
        - If anchor_id was not None, self.content["anchor_id"] equals the provided anchor_id.
        - If classes was not None, self.content["classes"] equals the provided classes.
        - If any optional argument was None, the corresponding key is not written/modified by this method (it could still exist if provided in the incoming content).

## Side Effects:
    - Mutates the passed-in content mapping in-place when inserting the optional metadata keys.
    - Does not perform I/O or call external services.
    - No deep copying is performed; external references to the provided content will observe the mutations done here.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.name` · *method*

## Summary:
Returns the stored display name for this renderable by reading the "name" entry from the object's content mapping.

## Description:
This property accessor fetches the value stored under the "name" key in self.content and exposes it as the renderable's name. It is a simple, read-only view into the object's content map.

Known callers and lifecycle:
- There are no callers listed inside this class definition; the property is intended for use by presentation and rendering code that needs a canonical name for the renderable (for example: building headings, labels, anchors, or table-of-contents entries).
- Typical invocation happens after a Renderable is constructed and possibly mutated via its constructor (which may set content["name"] if a name argument was provided). Consumers read this property when assembling or rendering report elements.

Why this is a dedicated property:
- Centralizes access to the "name" value so callers don't need to access the content mapping directly.
- Provides a clear, documented contract and type expectation for the attribute.
- Keeps object internals encapsulated while remaining lightweight (no extra state or computation).

## Args:
- None. This is a parameterless property.

## Returns:
- str: The value stored at self.content["name"].
- Edge cases:
    - If the mapping contains a non-str value under "name", that value is returned as-is (the method does not coerce types), which may violate the declared return annotation.
    - If the mapping contains the value None, None will be returned (again, despite the annotation indicating str).

## Raises:
- KeyError: If the "name" key is not present in self.content, accessing self.content["name"] will raise KeyError.
    - Exact condition: the KeyError occurs when "name" is not a key in the content dict at call time.

## State Changes:
- Attributes READ:
    - self.content (reads: content["name"])
- Attributes WRITTEN:
    - None (this property does not modify self or any external state)

## Constraints:
- Preconditions:
    - self.content must be a mapping (e.g., dict) supporting __getitem__ with string keys.
    - The "name" key must be present in self.content prior to calling this property to avoid KeyError.
- Postconditions:
    - No mutation to self.content or other attributes occurs.
    - The caller receives the exact object stored in self.content["name"] (no copying or conversion).

## Side Effects:
- None: this accessor performs no I/O, external calls, or mutations to objects outside self.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.anchor_id` · *method*

## Summary:
Return the object's stored anchor identifier used for HTML anchors and cross-references; does not modify the object's state.

## Description:
This property accesses the Renderable instance's content mapping and returns the value stored under the "anchor_id" key. It is intended to provide a single, consistent accessor for the anchor identifier that render implementations or external presentation code can use when emitting anchor tags, fragment identifiers, or references.

Known callers and lifecycle context:
- There are no direct callers inside this class definition. In typical usage, render() implementations (subclasses of Renderable) and external presentation/report code call this property during the rendering or HTML assembly stage to obtain the element's anchor id.
- This logic is a separate property because the Renderable stores presentation metadata inside a shared content dict; exposing the anchor id via a dedicated property centralizes access, enforces a stable API, and makes it easier to override or extend in subclasses.

## Args:
None.

## Returns:
str
- The value of self.content["anchor_id"] as stored in the instance.
- By annotation the return type is str; at runtime this will be whatever value is present in the content mapping under the "anchor_id" key (so callers should not assume the value is non-null or strictly typed unless enforced elsewhere).

## Raises:
KeyError
- Raised when the content mapping does not contain the "anchor_id" key.
- No other exceptions are raised by this accessor itself.

## State Changes:
Attributes READ:
- self.content (the mapping holding presentation metadata), specifically the "anchor_id" entry.

Attributes WRITTEN:
- None. This property does not mutate the object.

## Constraints:
Preconditions:
- self.content must be a mapping (dict-like) containing a key "anchor_id". This is typically ensured by the Renderable.__init__ when an anchor_id argument is provided.
- Callers expecting a non-empty string should ensure that the "anchor_id" entry was set and is of the expected type before calling.

Postconditions:
- No mutation to self or external objects occurs.
- If the call returns successfully, the returned value equals the current value of self.content["anchor_id"].

## Side Effects:
- None. This accessor performs no I/O, external calls, or modifications to objects outside self.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.classes` · *method*

## Summary:
Return the value stored under the "classes" key of the renderable's internal content dictionary; this is a read-only accessor and does not modify object state.

## Description:
This property directly exposes the entry self.content["classes"] from the Renderable instance's backing content dictionary.

Known callers and context:
- There are no call sites inside this file that reference this property. The property is intended as a public accessor for presentation metadata carried on Renderable instances and is therefore typically read by rendering, templating, or serialization code elsewhere in the codebase.
- Within the Renderable lifecycle, this property is intended to be read after the instance has been constructed and its content mapping populated (for example, immediately prior to rendering or when serializing presentation metadata).

Why this is a separate property:
- Encapsulates access to the dict-backed storage behind a stable, documented attribute (the @property), so external code does not need to access the content dict directly.
- Provides a clear, Pythonic API for consumers to obtain CSS/classes metadata.

Implementation note (evidence):
- The property implementation is a single return statement returning self.content["classes"].
- The Renderable.__init__ will set self.content["classes"] when the optional classes parameter is provided (see Renderable.__init__).

## Args:
- None (property access)

## Returns:
- str: By annotation the property returns a str (def classes(self) -> str). At runtime the method returns the object stored at self.content["classes"] without type conversion; if that stored value is not a str, that value is returned as-is.

## Raises:
- KeyError: Raised when the "classes" key is absent from self.content because the implementation performs direct dict indexing (self.content["classes"]).
  - This can occur when the Renderable was constructed without providing the optional classes parameter and "classes" was not otherwise set in the content mapping.

## State Changes:
- Attributes READ:
  - self.content (the mapping is accessed)
  - self.content["classes"] (the specific mapping entry is read)
- Attributes WRITTEN:
  - None (the property performs no mutations)

## Constraints:
- Preconditions:
  - self.content must be a mapping (dict-like) that supports __getitem__ with the key "classes".
  - Callers who require a string must ensure the value stored under "classes" is a str; the property does not validate or coerce the type.
  - The Renderable.__init__ will populate content["classes"] only if the optional classes parameter is provided; otherwise callers should ensure the key exists if they want to avoid KeyError.
- Postconditions:
  - The returned value equals the object previously stored at self.content["classes"].
  - The Renderable instance and its content mapping remain unchanged after the call.

## Side Effects:
- None. The property performs only an in-memory read; it does not perform I/O, network access, or mutate any external objects.

## Usage (prose example):
- After constructing or preparing a Renderable whose content mapping contains presentation metadata, read this property to obtain the CSS/classes string to include in rendered output or templates. If the property may be missing, guard the access (e.g., check "classes" in content) to avoid KeyError.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.render` · *method*

## Summary:
A no-argument abstract contract that produces a rendered representation of this object's content; does not implement rendering in the base class but defines what concrete subclasses must provide.

## Description:
- Known callers / lifecycle:
    - The base class does not call render itself. Concrete subclasses implement this method and it is invoked by the report/presentation rendering pipeline (i.e., by higher-level code that assembles report parts) to obtain the final representation for embedding or serialization.
    - The exact callers are not specified in this file; render is intended to be called at the final presentation stage when a Renderable instance is converted to an output form (for example: HTML fragments, JSON-serializable dicts, or other display formats).

- Why this is its own method:
    - The method is marked abstract in the base class to enforce a consistent interface across different kinds of renderable presentation components while allowing each subclass to produce an implementation-specific output (HTML, dict, plain text, etc.).
    - Keeping rendering logic in a dedicated method allows polymorphic substitution of different renderers without changing the report assembly code and isolates presentation concerns from data/storage concerns.

## Args:
    None

## Returns:
    Any
    - The return value is implementation-specific. Typical concrete return types include:
        - str — e.g., an HTML snippet or textual representation.
        - dict — e.g., a JSON-serializable structure describing the rendered element.
        - bytes — for binary payloads (less common).
    - Edge cases:
        - Implementations may return None to indicate "nothing to render", but callers should document how they treat None; the base class imposes no restriction.

## Raises:
    - The base abstract method does not raise exceptions.
    - Concrete implementations may raise exceptions appropriate to rendering (e.g., ValueError, KeyError, IOError) — callers should handle or propagate these as appropriate.
    - Note: accessing the convenience properties self.name, self.anchor_id, or self.classes in a subclass may raise KeyError if those keys are absent from self.content (see Preconditions).

## State Changes:
- Attributes READ:
    - The base method does not read any attributes.
    - Typical subclass implementations are expected to read from:
        - self.content (Dict[str, Any]) — the primary source of data to render.
        - Optionally the convenience properties: self.name, self.anchor_id, self.classes (these proxy into self.content).
- Attributes WRITTEN:
    - The base method does not modify any attributes.
    - Subclasses MAY mutate self.content (for example, to add derived fields or cached render artifacts), but such mutations are implementation-specific and should be documented by the subclass.

## Constraints:
- Preconditions:
    - self.content must be a Dict[str, Any] (the constructor requires this).
    - If a subclass uses the convenience properties self.name, self.anchor_id, or self.classes, those keys must be present in self.content; otherwise accessing those properties will raise KeyError because the properties directly index into self.content.
    - No other preconditions are enforced by the base class; concrete implementations may require additional keys or types inside self.content and should validate them locally.

- Postconditions:
    - The base method imposes no postconditions.
    - Implementations should guarantee a stable, documented return type (e.g., always return str containing valid HTML) to allow callers to consume the output reliably.
    - If a subclass mutates self.content, this should be clearly documented by that subclass.

## Side Effects:
    - The base abstract method has no side effects.
    - Concrete implementations may perform:
        - I/O (reading templates, loading assets).
        - Logging.
        - Mutations to self.content (caching intermediate results).
        - Calls to external libraries for templating or serialization.
    - Any side effects must be considered by callers; the base class does not constrain them.

## Implementation guidance for subclasses:
    - Keep this method focused on presentation: transform the data in self.content into the final output format without performing unrelated business logic.
    - Validate required keys from self.content at the start of the method and raise a clear exception (e.g., ValueError) if required data is missing or of the wrong type.
    - Prefer returning a deterministic, documented type (avoid returning different types in different situations unless callers accept that).
    - If the rendering step is expensive, consider caching the rendered result within self.content under a well-known key (and document that mutation) or using memoization at a higher level.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__str__` · *method*

## Summary:
Return a short textual identity for the object by producing its runtime class name.

## Description:
This implementation of the Python string-conversion hook returns the name of the object's class (the value of self.__class__.__name__). It provides the object's concise textual identity when converted to a string.

Known callers / contexts:
- Per Python semantics, this method is invoked when code calls str(instance) or when an instance is formatted/printed in contexts that use the __str__ hook.

Why this is a separate method:
- __str__ is the canonical Python hook for an object's user-friendly string representation; implementing it here centralizes that behavior and allows subclasses to override it to change how instances are presented as text.

## Args:
None.

## Returns:
str
- Exactly the value of self.__class__.__name__.
- Always the runtime class name string for normal Python classes.

## Raises:
None explicitly.
- The implementation does not raise under normal Python class semantics. Only unusual metaclass manipulations that remove or replace the __name__ attribute could cause an exception; such cases are outside the normal assumptions of this code.

## State Changes:
Attributes READ:
- self.__class__ (to access the object's type)
Attributes WRITTEN:
- None.

## Constraints:
Preconditions:
- self must be a live instance of a Python class (i.e., a valid object reference).
Postconditions:
- No mutation to the instance or external state.
- The return value equals the object's current class name at call time.

## Side Effects:
- None. The method performs no I/O, logging, network access, or modifications to external objects.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.convert_to_class` · *method*

## Summary:
A classmethod that mutates an instance in-place by assigning its runtime class to the class on which the method is called.

## Description:
This classmethod performs a single operation: it sets obj.__class__ = cls, causing the object's method resolution and type identity to change to cls.

Known callers and lifecycle context:
- No callers are present in the provided source. When used, it is typically invoked as ClassName.convert_to_class(obj, flv) to rebind an existing instance to ClassName.
- The method is intended for use in conversion or reclassification scenarios where an existing object's behavior should be changed without allocating a new object.

Why this is a separate method:
- Centralizes the single-step operation of reassigning an object's class so callers express intent (convert object to this class) instead of performing the assignment inline.
- Provides a single place to add compatibility checks or logging later if needed.

## Args:
    cls (type): The target class (the class object on which the method is invoked). In practice this will be Renderable or a Renderable subclass, but this is not enforced by the method.
    obj (Renderable): The instance whose __class__ will be reassigned. Must be an instantiated object (not a class).
    flv (Callable): Present in the signature but ignored by the current implementation; passing a callable has no effect.

## Returns:
    None

## Raises:
    TypeError: Raised by the Python runtime when the assignment is invalid. This occurs if the target class and the object's current class are incompatible in their internal layouts (for example, differing C-level memory layouts, incompatible use of __slots__, or other interpreter-level incompatibilities). The method does not catch or alter such exceptions.

## State Changes:
    Attributes READ:
        - None (the implementation does not read obj attributes or cls internals).
    Attributes WRITTEN:
        - obj.__class__: replaced with cls.

## Constraints:
    Preconditions:
        - obj must be a concrete Python object instance (not None, not a class object).
        - cls must be a valid Python class object.
        - For correct runtime behavior, cls should be compatible with obj's existing state (for example, if callers expect a 'content' attribute, cls methods/properties should work with that attribute). The method does not perform compatibility checks.

    Postconditions:
        - On successful return, obj.__class__ is equal to cls.
        - Subsequent method lookups, attribute access, and isinstance(obj, cls) will behave according to cls.
        - No other attributes of obj are modified by this method.

## Side Effects:
    - Mutates the runtime type of obj in-place; all references to the same object observe the type change immediately.
    - No I/O or external calls are made.
    - flv is unused and produces no side effects.

## Implementation note for reimplementation:
    - The implementation is a single-line assignment: obj.__class__ = cls (method is declared as a classmethod in the class definition). Any additional validation (type checks, compatibility assertions, logging) must be added by callers or by extending this method.

