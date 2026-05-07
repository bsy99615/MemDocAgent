# `dropdown.py`

## `src.ydata_profiling.report.presentation.core.dropdown.Dropdown` · *class*

## Summary:
Represents a presentation-layer "dropdown" item renderer: a structural wrapper that holds dropdown metadata (name, id, anchor, CSS classes, layout hint) and two kinds of child data — a sequence of selectable entries and a Container that defines the per-entry template — for consumption by a concrete renderer implementation.

## Description:
Dropdown is an ItemRenderer specialization used to model dropdown UI components in the report presentation tree. It centralizes the data needed by renderers to produce a dropdown: the identity and styling information, a sequence of item values (content['items']), and a Container template describing how each item should be rendered (content['item']).

When to instantiate:
- In factories that transform a report specification or serialized structure into a typed presentation tree.
- When building interactive report UIs where each dropdown option is itself a structured Renderable (label + metadata).
- When deserializing generic Renderable-like objects and converting them back into typed Dropdown instances (use convert_to_class for this).

Why this abstraction:
- Keeps dropdown-specific metadata and child structure in one place.
- Allows the rendering system to rely on a consistent content layout for dropdowns while leaving rendering output format (HTML, JSON, component tree) to renderer implementations.
- Provides a lightweight conversion hook (convert_to_class) to restore runtime typing after deserialization.

Responsibility boundary:
- Stores structure and metadata. It does not implement rendering (render raises NotImplementedError) and does not enforce runtime type checking of children. Renderers and higher-level factories are responsible for supplying correct Renderable/Container instances.

## State:
All state lives on the inherited Renderable.content dictionary. Dropdown.__init__ constructs and stores the following keys:

- name (str)
    - Source: name parameter to __init__.
    - Semantic: human-readable label for the dropdown.
    - Presence: included in content if provided.

- id (str)
    - Source: id parameter.
    - Semantic: unique identifier used by renderers and/or the DOM.
    - Constraint: expected to be a string; Dropdown does not validate format.

- items (list)
    - Source: items parameter.
    - Type: list (sequence) — expected to contain Renderable instances or values the renderer knows how to handle.
    - Invariant: iterating content['items'] yields the logical selectable entries for the dropdown.

- item (Container)
    - Source: item parameter (must be a Container instance).
    - Semantic: template/structure used by renderers to render each entry in content['items'].
    - Note: convert_to_class will explicitly call the provided flv callback on this Container to allow in-place conversion.

- anchor_id (str)
    - Source: anchor_id parameter.
    - Semantic: anchor identifier used for linking; may be an empty string if caller provides one.

- classes (str)
    - Source: classes parameter (constructor accepts a list[str], Dropdown stores " ".join(classes) into content["classes"]).
    - Constraint: classes must be an iterable of strings; passing non-string elements will raise TypeError when joining.

- is_row (bool)
    - Source: is_row parameter.
    - Semantic: layout hint (True means render items in a row); interpretation is renderer-specific.

Notes about forwarded kwargs:
- Any additional keyword arguments passed to Dropdown.__init__ are forwarded to ItemRenderer.__init__ and Renderable.__init__. Those base initializers accept name, anchor_id, and classes (strings) and will set content["name"], content["anchor_id"], and content["classes"] based on arguments provided there. If a caller provides the same key both in Dropdown explicit parameters and in kwargs, Renderable.__init__ may overwrite the corresponding content key. Callers should avoid passing duplicate metadata through kwargs.

Class invariants:
- After initialization, self.content is a dict that contains at least the keys set above (subject to caller-provided values).
- content['classes'] is always a string (result of " ".join on the classes list provided at construction).
- content['items'] is a sequence (typically list) containing the logical dropdown entries.
- The instance's runtime class is Dropdown unless altered externally (for example, by convert_to_class on another object).

## Lifecycle:
Creation:
- Constructor signature (positional/keyword parameters):
    - name: str
    - id: str
    - items: list
    - item: Container
    - anchor_id: str
    - classes: list
    - is_row: bool
    - **kwargs: additional keyword args forwarded to ItemRenderer/Renderable (commonly used keys: name, anchor_id, classes as strings)
- Required: All parameters in the signature have no default values in the source; callers must supply them. (Although Renderable accepts None for name/anchor_id/classes, the Dropdown signature indicates these parameters are expected — pass empty strings if not applicable.)
- What the constructor does:
    1. Builds a content dict:
       {
         "name": name,
         "id": id,
         "items": items,
         "item": item,
         "anchor_id": anchor_id,
         "classes": " ".join(classes),
         "is_row": is_row,
       }
    2. Calls ItemRenderer.__init__("dropdown", content, **kwargs) which delegates to Renderable.__init__(content, ...).
    3. ItemRenderer sets item_type = "dropdown"; Renderable stores the content dict on the instance and applies any name/anchor_id/classes passed through kwargs (potentially overwriting same-named keys in content).

Usage:
- Typical call sequence:
    1. Instantiate: d = Dropdown(name, id, items, item_container, anchor_id, classes, is_row)
    2. A rendering system or renderer subclass obtains d and calls d.render() to produce output. Because Dropdown.render() is unimplemented, the renderer must either implement a subclass of Dropdown with render or provide rendering logic that inspects content and produces output.
    3. For deserialization: create a generic Renderable-like object with content matching the keys, then call Dropdown.convert_to_class(obj, flv) to convert it into a Dropdown instance and convert its 'item' Container recursively.
- Sequencing constraints:
    - No special ordering beyond create-before-render. Ensure the provided item Container and each element in items are valid Renderable-like objects before rendering.

Destruction:
- No explicit cleanup or context manager behavior is required. Dropdown holds in-memory Python objects only.

## Method Map:
flowchart LR
    Init[Dropdown.__init__] --> BuildContent[Build content dict with keys: name,id,items,item,anchor_id,classes,is_row]
    BuildContent --> CallParent[Call ItemRenderer.__init__("dropdown", content, **kwargs)]
    CallParent --> RenderableInit[Renderable.__init__(store content, apply kwargs)]
    Init --> Repr[__repr__ => "Dropdown"]
    Init --> Render[render() -> NotImplementedError]
    ClassMethod[convert_to_class(cls,obj,flv)] --> MutateClass[obj.__class__ = cls]
    MutateClass --> MaybeFLV[if "item" in obj.content: flv(obj.content["item"])]

## Method details:
- __repr__(self) -> str
    - Returns the literal string "Dropdown". Intended for simple debug/inspection.

- render(self) -> Any
    - Raises NotImplementedError by design.
    - Contract for implementers: A concrete renderer or a subclass must override render() to return the presentation output (type and semantics determined by the renderer, e.g., HTML string, JSON, component tree).

- convert_to_class(cls, obj: Renderable, flv: Callable) -> None  (classmethod)
    - Behavior:
        - Mutates obj.__class__ to be cls (Dropdown).
        - If obj.content contains key "item", calls flv(obj.content["item"]) to allow recursive conversion of that Container.
    - Important: convert_to_class does NOT iterate over or convert content['items']; conversion of the items list is the caller's responsibility or handled at a different stage in the conversion pipeline.
    - flv signature: Callable[[Renderable], Any] — a callback that performs conversion/processing on the passed Renderable-like object in-place (commonly used to convert nested Container objects to their corresponding classes).

## Raises:
- __init__:
    - TypeError when trying to join classes elements that are not strings: " ".join(classes) will raise TypeError if any element is not str.
    - Any exceptions raised by ItemRenderer.__init__ or Renderable.__init__ (for example, if content is not a dict-like object) will propagate.
    - Note: Dropdown does not perform explicit type validation on items or item; downstream code may raise exceptions if items are unexpected types.

- render:
    - Always raises NotImplementedError on this base class.

- convert_to_class:
    - May raise AttributeError or TypeError if obj.__class__ is not writable or if obj.content is missing/incorrectly structured.
    - Any exception raised by the flv callback will propagate.

## Example:
- Instantiation (conceptual lines; avoid passing duplicate metadata in kwargs):
    name = "choose_color"
    id = "dropdown-1"
    items = [item1, item2]                 # item1/item2 are Renderable instances or values the renderer understands
    item_container = Container(items=[], sequence_type="ul")  # a Container describing per-entry structure
    anchor_id = "anchor-choose-color"
    classes = ["btn", "btn-dropdown"]
    is_row = False

    d = Dropdown(name, id, items, item_container, anchor_id, classes, is_row)

- Rendering:
    - A renderer inspects d.content and the d.item Container and produces the final UI.
    - Calling d.render() on this base class will raise NotImplementedError; implement a renderer-specific subclass or rendering routine.

- Deserialization / conversion:
    - Suppose obj is a generic Renderable-like object with the same content keys:
      Dropdown.convert_to_class(obj, flv)
    - Provide flv such that flv(container_obj) will convert the container_obj into the appropriate Container subclass (for example, Container.convert_to_class or other conversion utilities).
    - After conversion, obj.__class__ is Dropdown and obj.content["item"] has been processed by flv.

Implementation hints:
- Reimplementations must:
    - Build the content dict exactly as done in the original source, using " ".join(classes) for content["classes"].
    - Call ItemRenderer.__init__("dropdown", content, **kwargs) to ensure item_type is set and Renderable.__init__ stores the content.
    - Keep convert_to_class minimal: set obj.__class__ = cls and invoke flv on obj.content["item"] only if present (do not attempt to convert content['items'] here).

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.__init__` · *method*

## Summary:
Initializes the dropdown presentation node by assembling its content dictionary (name, id, items, item, anchor_id, classes, is_row) and delegating base initialization to the ItemRenderer/Renderable chain — causing the instance to hold that content and be typed as an item renderer of type "dropdown".

## Description:
This constructor builds the content payload that represents a dropdown UI element in the presentation tree and then calls the parent initializer to attach that payload to the instance and set rendering metadata (item_type). It is invoked when presentation nodes are constructed (for example, by report-building factories or rendering pipelines) at the time a dropdown node must be created and inserted into the renderable tree.

Why this is a separate method:
- It centralizes the dropdown-specific content layout (which keys the dropdown expects in content) instead of scattering that structure in callers.
- It delegates generic initialization (storage of content, optional name/anchor/classes handling, and setting item_type) to ItemRenderer/Renderable, keeping responsibilities separated: this method composes content; the base classes manage storage and shared behavior.

Known callers / lifecycle stage:
- Typically called by report assembly code that converts a report specification into a tree of Renderable objects (e.g., factory functions that create multiple container and item renderables).
- Called during construction time of the presentation model, before any render() calls on the node or before conversion utilities mutate classes of generic nodes.

## Args:
    name (str): Logical display name for the dropdown. Stored under content['name'].
    id (str): Identifier for the dropdown. Stored under content['id'].
    items (list): Sequence of child items (usually a list of Renderable or primitive descriptors) stored under content['items'].
    item (Container): A Container instance or container-like object stored under content['item'] that describes the per-item presentation template.
    anchor_id (str): Identifier string used for anchoring the dropdown in the UI. Stored under content['anchor_id'].
    classes (list): Sequence of CSS/class tokens (list of strings). They are joined with a single space to produce a single string stored under content['classes'].
    is_row (bool): Boolean flag stored under content['is_row'] indicating whether the dropdown should be presented inline (row) or as a block.
    **kwargs: Additional keyword arguments are forwarded to the superclass initializer (ItemRenderer.__init__), which will in turn forward recognized keywords to Renderable.__init__ (e.g., name, anchor_id, classes if provided as kwargs). Note that because this constructor already embeds name, anchor_id, and classes into the content dict, providing them again via kwargs will cause Renderable.__init__ to overwrite the corresponding keys in content if those keywords are non-None.

## Returns:
    None

## Raises:
    TypeError: If classes is not an iterable of strings (or contains non-string items) such that " ".join(classes) raises a TypeError.
    Any exception raised by ItemRenderer.__init__ or Renderable.__init__: for example, TypeError or KeyError may propagate if kwargs have unexpected types or Renderable's expectations are violated. This constructor does not perform additional validation and thus will propagate upstream exceptions raised by underlying calls.

## State Changes:
Attributes READ:
    - None (this method does not read any existing instance attributes; it only constructs a new content dict from the provided args).

Attributes WRITTEN:
    - self.content (dict): Assigned by the base Renderable.__init__ to the content dict constructed here. After init, content contains at least the keys: 'name', 'id', 'items', 'item', 'anchor_id', 'classes', 'is_row' (subject to later overrides by kwargs forwarded to the superclass).
    - self.item_type (str): Set by ItemRenderer.__init__ to the literal string "dropdown".
    - Indirectly, self.name / self.anchor_id / self.classes properties (property accessors defined on Renderable) will reflect values stored in self.content.

## Constraints:
Preconditions:
    - Caller should supply classes as an iterable of strings (e.g., list[str]) suitable for " ".join; otherwise a TypeError will occur.
    - item is expected to be a Container (or container-like Renderable) as the rest of the presentation pipeline expects that shape, although no runtime type check is performed here.
    - items should be a sequence (list/tuple) of child descriptors or Renderable instances as appropriate for downstream renderers; no runtime enforcement is done here.

Postconditions:
    - After return, self.content is defined and contains the provided keys/values, unless overwritten by kwargs forwarded to the superclass.
    - self.item_type is exactly "dropdown".
    - No I/O is performed and no external services are invoked.

## Side Effects:
    - Mutates the instance by setting self.content and self.item_type (via superclass initializers).
    - No file, network, or other external I/O occurs.
    - Does not validate or mutate the passed-in items or item beyond putting them into the content dict (i.e., it does not convert or copy them).

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.__repr__` · *method*

## Summary:
Returns a stable, short textual representation of the object suitable for debugging and display; does not modify the object's state.

## Description:
This method provides the object's official string representation used by Python's built-in repr() and by tools that inspect or log objects (for example, when printing lists of objects, debugging output, or logging). It is invoked whenever an object's representation is requested rather than when rendering the object's HTML or content (see render()).

Known callers and contexts:
- Python builtin repr(obj) and functions that call it (e.g., print(obj) when repr is used, logging, debuggers).
- Any library or internal code that formats or inspects objects for debugging or diagnostic output.

Why this is a separate method:
- Providing a dedicated __repr__ keeps a concise, stable textual identity for instances that is independent of the object's dynamic content or rendering logic. It is deliberately lightweight and separated from render()/convert_to_class() responsibilities to avoid pulling in rendering logic or object internals into the representation string.

## Args:
    None

## Returns:
    str: The fixed string "Dropdown". This value is always returned and does not depend on instance attributes.

## Raises:
    None

## State Changes:
    Attributes READ:
        - None (the implementation does not access any self.<attr> fields)
    Attributes WRITTEN:
        - None (the method does not modify self)

## Constraints:
    Preconditions:
        - The method must be called on an instantiated object (an instance of Dropdown or a subclass).
    Postconditions:
        - The object's state is unchanged.
        - The caller receives the string "Dropdown".

## Side Effects:
    - None. The method performs no I/O, no logging, and no mutation of external objects.

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.render` · *method*

## Summary:
Acts as the abstract rendering entry point for a Dropdown renderable. In this base implementation it does not modify state and always raises NotImplementedError; concrete subclasses or runtime-converted instances must implement this method to produce the presentation output.

## Description:
Known callers and lifecycle:
- No explicit callers are provided in the supplied snippets. By design, this method is expected to be invoked by the report presentation/rendering pipeline (the code that traverses a tree of Renderable instances and calls render() on each node) during the final presentation generation stage after the report model has been constructed.
- Typical usage: code that renders the report will iterate the renderable tree and call render() on each node. For Dropdown objects, the rendering pipeline should invoke an overridden Dropdown.render (or convert the object to a runtime-specific class that provides render) to obtain the presentation representation.

Why this is a separate method:
- render() is the canonical per-node rendering contract required by the Renderable abstraction; keeping rendering logic in a dedicated method allows different rendering backends or subclasses to implement format-specific output (e.g., HTML, JSON, dict tree) without changing the structural model.
- The method exists here as a required extension point: the base Dropdown provides the structural content (see __init__) while concrete renderers implement the presentation semantics.

## Args:
- None

## Returns:
- Any
    - In this base implementation there is no return because the method unconditionally raises NotImplementedError.
    - Implementations should return a renderer-defined representation of the dropdown (the exact type and structure are determined by the rendering backend).

## Raises:
- NotImplementedError
    - Raised unconditionally by this method as defined in the base Dropdown class. Callers should expect this unless the instance's class has been replaced or a subclass overrides render().

## State Changes:
- Attributes READ:
    - None performed by this base implementation.
    - Note for implementers: the Dropdown.__init__ populates self.content with keys that concrete implementations will commonly read: 'name', 'id', 'items', 'item', 'anchor_id', 'classes', 'is_row'. Any concrete render() may read these fields to produce output.
- Attributes WRITTEN:
    - None performed by this base implementation.

## Constraints:
- Preconditions:
    - The instance should be a properly constructed Dropdown (i.e., created via Dropdown.__init__ or converted into a subclass that preserves the content shape). The content dict will contain the keys listed above only if the instance was constructed with the corresponding parameters.
    - Callers must ensure the instance's class implements render() (either by using a concrete subclass or by applying convert_to_class) before invoking render() on an object intended to produce output.
- Postconditions:
    - The base method does not guarantee any state changes or outputs because it always raises NotImplementedError.
    - Implementations are free to mutate self.content or other attributes; such behavior must be documented on the concrete override.

## Side Effects:
- Base implementation: none (no I/O, no external calls, no mutations).
- Concrete implementations: may perform I/O, produce strings/HTML, allocate objects, or mutate nested child renderables. Those side effects are implementation-specific and must be documented by the overriding method.

Notes for implementers:
- If you implement render(), follow the Renderable contract: accept no arguments and return a renderer-appropriate representation. Use the content keys populated in Dropdown.__init__ to drive presentation:
    - content['items']: a sequence of child Renderable instances (if present)
    - content['item']: a single child Container-like Renderable used as the item template (if present)
    - content['is_row'], content['classes'], content['anchor_id'], content['name'], content['id'] — additional metadata to guide rendering
- The convert_to_class classmethod present on Dropdown is used by deserialization or conversion flows to mutate a generic Renderable into a Dropdown and to apply a conversion function to nested 'item' content; ensure any runtime class swapping preserves the semantics expected by your render() implementation.

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.convert_to_class` · *method*

## Summary:
Mutate a Renderable-like object's runtime class to the Dropdown subclass and, if present, apply a provided conversion function to the single nested "item" entry in the object's content.

## Description:
This classmethod is used during reconstruction/deserialization or factory-driven initialization of presentation trees. Callers typically pass a generic Renderable-like object (for example, an object created from a deserialized specification) together with a conversion callback (flv) that recursively converts nested nodes into their proper runtime classes. The method performs two focused steps: it assigns cls to obj.__class__, then — if obj.content contains the key "item" — it invokes flv on that value so nested content is converted or mutated in-place.

Known callers and lifecycle stage:
- Typical callers are deserialization/factory routines or reconstruction code in the presentation pipeline that need to convert loosely-typed nodes into concrete renderer classes before rendering.
- This method is invoked during the object reconstruction/initialization phase, prior to any render() calls.

Rationale for being a separate method:
- Converting the runtime class and handling the Dropdown-specific nested "item" key are cohesive operations tied to the Dropdown structure. Encapsulating this logic in a classmethod:
  - centralizes type-conversion logic for Dropdown,
  - avoids duplication at call-sites,
  - allows callers to provide a conversion function that controls how nested items are processed.

## Args:
    cls (type):
        The class object to assign to obj.__class__. In typical use this is the Dropdown class (or a subclass).
    obj (Renderable):
        The instance whose runtime class will be changed. Must expose a content attribute that behaves like a mapping (e.g., dict).
    flv (Callable):
        A callable invoked with the nested value stored under obj.content["item"] when present. Expected signature: Callable[[Any], Any] or Callable[[Renderable], Any]. The return value of flv is ignored; it is called for its side effects (in-place conversions/mutations).

## Returns:
    None
    - No value is returned. Success is observable via the mutated obj and any nested items processed by flv.

## Raises:
    TypeError:
        - If assigning cls to obj.__class__ is invalid because the target class has an incompatible instance layout, Python will raise TypeError.
        - If obj.content["item"] exists but is not of a type that flv can iterate/process as expected, flv may raise a TypeError (this comes from flv, not this method).
    AttributeError:
        - If obj does not have a content attribute (i.e., it is not Renderable-like), accessing obj.content will raise AttributeError.
    Any exception raised by flv:
        - Exceptions thrown by the flv callable propagate unchanged to the caller (for example, if flv assumes a specific contract for the nested value and that contract is violated).

## State Changes:
    Attributes READ:
        - obj.content (always read to check for the "item" key)
        - obj.content["item"] (read only if the "item" key exists)
    Attributes WRITTEN:
        - obj.__class__ is reassigned to cls

## Constraints:
    Preconditions:
        - obj must be an object compatible with the Renderable interface: it must provide a content attribute that is a mapping (dict-like).
        - cls must be a class object compatible with assignment to obj.__class__ (in CPython, incompatible instance layouts will raise TypeError).
        - flv must be a callable able to process the value stored under obj.content["item"] (if present); callers are responsible for ensuring flv handles None or non-Renderable values if those can occur.
    Postconditions:
        - After successful completion, obj.__class__ equals the provided cls.
        - If obj.content contained an "item" key, flv has been invoked exactly once with obj.content["item"] as its argument; any modifications to that nested value depend on flv's behavior.

## Side Effects:
    - Mutates obj.__class__, changing the object's runtime type and therefore its method resolution and isinstance behavior.
    - Calls the provided flv callable with obj.content["item"] when present; flv may further mutate that nested object or raise exceptions.
    - No I/O, network, or external service calls are performed by this method itself.

