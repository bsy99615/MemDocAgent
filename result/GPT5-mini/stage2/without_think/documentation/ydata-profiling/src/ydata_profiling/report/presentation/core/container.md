# `container.py`

## `src.ydata_profiling.report.presentation.core.container.Container` · *class*

## Summary:
Represents a sequence-like wrapper of Renderable items that carries rendering semantics via a sequence_type string and delegates most rendering behavior to subclasses.

## Description:
Container is an abstract container abstraction that groups an ordered sequence of Renderable items together and records whether the group is nested. It is intended to be instantiated by code that builds presentation trees for reports (for example, by factories that traverse a report specification and construct renderable nodes). Typical callers create Container instances when they need to represent a list/sequence/collection of child renderables that should be rendered together under a specific sequence_type (an identifier describing how a renderer should treat the sequence).

The class itself does not implement concrete rendering logic — subclasses must implement render() to produce the final presentation output. Container centralizes the following responsibilities:
- Hold the child items and auxiliary metadata (nested flag and any extra kwargs) in a single content dict stored on the Renderable base.
- Provide stable string and repr representations used for debugging and logging.
- Offer a class-level conversion utility (convert_to_class) to transform a generic Renderable-like object into this Container subclass and recursively apply a provided conversion function to its items.

Responsibility boundary:
- Container stores and exposes structural metadata only. It does not validate item types at runtime nor implement rendering semantics — those are the responsibility of concrete subclasses and any caller-provided conversion functions.

## State:
- content (inherited from Renderable): dict[str, Any]
    - 'items' (mandatory semantic key): Sequence[Renderable]
        - Type: sequence (e.g., list or tuple) whose elements are expected to be Renderable instances (no runtime enforcement in Container.__init__).
        - Invariant: If present, iteration over this sequence yields the logical children of the container.
    - 'nested' (mandatory semantic key): bool
        - Default: False when not specified by caller.
        - Semantics: True when this container represents a nested subsequence in a larger structure; renderers may interpret this to change indentation/format.
    - Additional keys: any extra keyword arguments passed into Container.__init__ are merged into content and therefore become part of stored state. Keys name, anchor_id, classes may also be present (set by Renderable.__init__ when corresponding parameters are supplied).
- sequence_type (attribute on Container instances): str
    - Type: str
    - Semantics: A short identifier describing how child items should be presented (e.g., "ul", "ol", "table-row", or any renderer-defined token). Container does not interpret or validate the string itself.
    - Invariant: Must remain a string for the lifetime of the instance.

Class invariants:
- content is always a dict assigned by Renderable.__init__.
- If content contains 'items', it should be a sequence of objects that implement Renderable semantics (i.e., provide a render() method); Container does not enforce or coerce this.
- sequence_type exists and is a str after __init__ completes.

## Lifecycle:
Creation:
- Required positional arguments:
    - items: Sequence[Renderable] — the child items of the container. The value is stored into content['items'].
    - sequence_type: str — describes how to render the sequence.
- Optional arguments:
    - nested: bool = False — whether this container is nested.
    - name: Optional[str] = None — if provided, Renderable.__init__ stores this under content['name'].
    - anchor_id: Optional[str] = None — if provided, stored under content['anchor_id'].
    - classes: Optional[str] = None — if provided, stored under content['classes'].
    - **kwargs: Any additional key/value pairs to be merged into content.
- Implementation note: Container constructs a dict args = {"items": items, "nested": nested}, updates it with kwargs, and passes that dict to Renderable.__init__ as the content argument. After calling the base initializer it sets self.sequence_type = sequence_type.

Usage:
- Typical usage sequence:
    1. Instantiate a concrete subclass of Container (or instantiate Container itself only if used purely as a structural placeholder).
    2. Optionally inspect or mutate content keys (e.g., content['items']).
    3. Call render() on the concrete subclass to produce output. Container.render() raises NotImplementedError; callers must use a subclass that implements render.
    4. __str__ and __repr__ can be used at any time to obtain human-readable descriptions useful in logs or debugging.
- Ordering constraints:
    - There is no required method call ordering at the Container API level beyond normal Python object lifetime. However render() should be called only on instances whose subclass implements render.

Destruction / cleanup:
- Container does not manage resources (file handles, network, etc.) and does not provide close/cleanup hooks or context manager behavior. No explicit destruction steps are required.

## Method behaviors (detailed):

- __init__(items: Sequence[Renderable], sequence_type: str, nested: bool = False, name: Optional[str] = None, anchor_id: Optional[str] = None, classes: Optional[str] = None, **kwargs) -> None
    - Stores items and nested in a dict and merges **kwargs into it, then passes that dict to Renderable.__init__ as the content.
    - After base initialization, sets self.sequence_type to the provided sequence_type string.
    - Guarantees: self.content is a dict containing at least 'items' and 'nested' keys (subject to callers not removing them afterwards).
    - Does not validate or coerce elements of items; callers are expected to supply Renderable instances.

- __str__() -> str
    - Produces a multi-line text description:
        - First line is "Container".
        - If content contains 'items', iterates enumerate(content['items']) and for each item:
            - Calls str(item), replaces any newline in that string with a newline character followed by a single tab character ("\n\t") to indent multi-line child descriptions.
            - Appends a line "- {index}: {indented item string}" for each item where {index} is the integer index (starting at 0).
    - Edge behavior: If content['items'] contains objects whose __str__ raises an exception, that exception propagates. If 'items' key is absent, returns "Container\n".

- __repr__() -> str
    - If content contains a 'name' key, returns "Container(name={name})" where {name} is the literal value of content['name'].
    - Otherwise returns the string "Container".

- render() -> Any
    - Abstract placeholder in Container: it raises NotImplementedError().
    - Contract: subclasses must override render() to return the renderer-specific representation of this container (type and semantics are renderer-defined).

- convert_to_class(cls, obj: Renderable, flv: Callable) -> None  (classmethod)
    - Side effects:
        - Mutates obj.__class__ to be cls (i.e., makes obj an instance of this Container subclass at runtime).
        - If obj.content contains 'items', iterates each item in obj.content['items'] and calls flv(item).
    - Expected flv signature: Callable[[Renderable], Any] — a function that will perform conversion/processing on each child Renderable (typically performing the same kind of class conversion on nested nodes). Container does not inspect flv's return value and relies on flv to perform necessary in-place conversions or side-effects.
    - Notes:
        - This method performs in-place mutation of obj.__class__; callers must ensure this is safe in their environment.
        - No type checking is performed on items — flv should be prepared to handle whatever objects are present.

## Method Map:
flowchart LR
    A[Create Container.__init__] --> B[content dict: 'items','nested', plus kwargs]
    B --> C[Renderable.__init__(content)]
    C --> D[set sequence_type on instance]
    D --> E[Use container: inspect content, call subclass.render()]
    E --> F[__str__ / __repr__ used for debugging]
    D --> G[convert_to_class (classmethod)]
    G --> H[mutate obj.__class__ to cls]
    H --> I[for each item in obj.content['items'] call flv(item)]

## Raises:
- __init__: does not explicitly raise type-specific exceptions. However:
    - If callers pass objects that are not suitable for use by Renderable.__init__ (e.g., non-dict content via monkey-patching), runtime errors may occur elsewhere.
    - No argument validation is performed, so typical Python TypeErrors may arise later if items are used in ways that assume Renderable behavior.
- __str__: may propagate exceptions thrown by item.__str__.
- render: raises NotImplementedError by design to force subclass implementation.
- convert_to_class: may raise AttributeError or TypeError if obj does not have a writable __class__ attribute or if obj.content is not subscriptable as expected; flv may raise user-defined exceptions.

## Example (usage pattern described in prose):
1. Prepare a sequence of child objects that implement the Renderable contract (each must implement render and be representable via str/repr).
2. Instantiate a concrete Container subclass (or Container as a structural placeholder) with:
   - items set to the prepared sequence,
   - sequence_type set to an identifier string describing rendering semantics,
   - optional nested, name, anchor_id, classes and any additional metadata as keyword arguments.
3. The constructor stores the items and metadata in content and sets sequence_type on the instance.
4. To produce output, call render() on a concrete subclass that implements render; if you call render() on Container directly, a NotImplementedError is raised.
5. When reconstructing object graphs from a generic Renderable-like object (for example, after deserialization), call ContainerSubclass.convert_to_class(obj, flv) to mutate obj into an instance of the subclass and apply flv to each child item so they can also be converted appropriately.

Notes:
- Container is a lightweight structural abstraction: it centralizes storage of child sequences and metadata and delegates rendering and type validation to external code and subclasses.

### `src.ydata_profiling.report.presentation.core.container.Container.__init__` · *method*

## Summary:
Initializes a Container instance by storing its child items and metadata into the inherited content dictionary and setting the container's sequence_type attribute.

## Description:
This constructor is called when a presentation-tree node representing a sequence of child renderables is created. Typical callers include report/presentation builders and factory functions that traverse a report specification and construct renderable nodes; it is invoked during the construction phase of the presentation pipeline, before any rendering is performed.

The logic is implemented as a dedicated method to centralize the creation of the content mapping passed to the Renderable base class (ensuring 'items' and 'nested' are present and allowing additional metadata via **kwargs) and to set the sequence_type attribute on the instance. Keeping this behavior in __init__ avoids duplicating content-merging and base-class initialization patterns across multiple container-like subclasses.

## Args:
    items (Sequence[Renderable]):
        A sequence (e.g., list or tuple) of child objects expected to follow the Renderable contract (i.e., provide a render() method). Container does not enforce the type at runtime but assumes callers supply renderable-like objects.
    sequence_type (str):
        An opaque identifier that describes how renderers should treat the sequence of items (examples: "ul", "ol", "table-row", or any renderer-defined token). The value is stored directly on the instance and is not validated by Container.
    nested (bool, optional, default=False):
        Whether this container is a nested subsequence within a larger structure. Stored under the 'nested' key of the content mapping.
    name (Optional[str], optional, default=None):
        If provided, passed to the Renderable base class which will store it in content["name"].
    anchor_id (Optional[str], optional, default=None):
        If provided, passed to Renderable.__init__ which will store it in content["anchor_id"].
    classes (Optional[str], optional, default=None):
        If provided, passed to Renderable.__init__ which will store it in content["classes"].
    **kwargs:
        Arbitrary additional key/value metadata merged into the content dictionary. These keys become part of self.content and are visible to renderers and other code.

Notes on argument interactions:
    - The constructor first builds args = {"items": items, "nested": nested} then updates it with **kwargs. Therefore, if kwargs contains the keys "items" or "nested", those values will overwrite the corresponding positional parameters. Callers should avoid passing conflicting keys in kwargs unless intentional overriding is desired.

## Returns:
    None

## Raises:
    - This constructor does not explicitly raise its own exceptions.
    - It may propagate exceptions raised by Renderable.__init__ (for example, if that initializer were changed to require specific content shapes) or by Python operations used here (though the existing code only constructs and updates a dict and calls the base initializer). Any runtime errors coming from mis-typed arguments (e.g., passing a non-hashable key in **kwargs) will propagate as normal Python exceptions.

## State Changes:
Attributes READ:
    - None on self are read by this method (all inputs are provided via parameters).

Attributes WRITTEN:
    - self.content (assigned by Renderable.__init__): becomes the dict containing at least the keys "items" and "nested" plus any keys supplied in **kwargs. If name/anchor_id/classes were provided, Renderable.__init__ will add those keys into this dict as well.
    - self.sequence_type: set to the provided sequence_type string.
    - Additionally, individual keys inside the content dict are created or updated (e.g., content["items"], content["nested"], content.update(**kwargs), and possibly content["name"], content["anchor_id"], content["classes"] from the base initializer).

## Constraints:
Preconditions:
    - The caller should provide a sequence-like object for items (the class assumes iteration/indexing semantics typical of sequences). The constructor does not enforce this but downstream code (renderers) will expect it.
    - sequence_type should be a string if renderers expect string tokens; Container does not validate the type but stores it as-is.

Postconditions:
    - After __init__ returns, self.content is a dict and contains at least:
        - "items": (the items value provided originally, unless overridden by kwargs)
        - "nested": (the nested flag provided originally, unless overridden by kwargs)
      Any additional keys passed via **kwargs are present in self.content. If name/anchor_id/classes were provided, those keys are present in self.content (set by Renderable.__init__).
    - self.sequence_type is set to the provided sequence_type value and remains available for renderer logic.

## Side Effects:
    - Mutates the instance by assigning self.content (via the base class initializer) and self.sequence_type.
    - Merges **kwargs into the content mapping; these values are stored and visible outside the constructor (no defensive copy is performed).
    - No I/O or external service calls are made.
    - Because kwargs can overwrite the "items" and "nested" keys, callers may observe that the final stored items/nested differ from the direct positional arguments if conflicting kwargs are passed.

### `src.ydata_profiling.report.presentation.core.container.Container.__str__` · *method*

## Summary:
Return a human-readable, multi-line string representation of this Container and its contained items, with child items' lines indented for readability.

## Description:
This method implements the stringification logic used when str(container) or print(container) is called. It produces a simple textual summary beginning with a "Container" header and, when the container holds an "items" entry in its content mapping, lists each item by index and the string form of the item. Each newline inside an item's string is replaced with a newline followed by a tab character to indent multi-line item representations.

Known callers and context:
- Implicit callers: Python's built-in str() and print() when invoked on a Container instance.
- Typical usage: debugging, logging, or any diagnostic pipeline step that needs a compact textual overview of a Container and its children.
- No explicit callers are required by the method; it is a convenience for human-readable output and debugging rather than for rendering HTML or structured output.

Why this is a separate method:
- Separating __str__ keeps a concise, human-oriented summary distinct from render() (which is abstract and intended for structured presentation). This avoids inlining ad-hoc debug formatting in rendering logic and centralizes how Containers are displayed as text.

## Args:
    None

## Returns:
    str: A multi-line string. Format details:
        - Always starts with "Container\n".
        - If self.content contains an "items" key with an iterable of items, each item is appended as a line prefixed "- {index}: " followed by str(item).
        - If an item's string contains newline characters, each newline is replaced by "\n\t" so subsequent lines are indented.
        - If no "items" key exists in self.content, the method returns just "Container\n".

    Edge-case returns:
        - If "items" exists but is an empty iterable, the result is "Container\n" (with no item lines appended).
        - If items are present but their string conversion yields empty strings, item lines appear with an empty name (e.g., "- 0: ").

## Raises:
    Any exception raised while computing the string for items will propagate:
        - TypeError: If "items" exists but its value is not iterable, enumeration will raise TypeError.
        - Any exception raised by an individual item's __str__ implementation will propagate (e.g., custom __str__ that raises).
    No exceptions are explicitly raised by this method itself.

## State Changes:
    Attributes READ:
        - self.content (read access)
            * Specifically checks for the key "items" and reads self.content["items"] when present.

    Attributes WRITTEN:
        - None. This method does not modify self or any external object.

## Constraints:
    Preconditions:
        - self.content must be a mapping (typically a dict) as established by Renderable.__init__. The method assumes membership testing ("items" in self.content) and indexing (self.content["items"]) are supported.
        - If present, self.content["items"] should be an iterable (preferably Sequence[Renderable]) for enumeration to succeed.
    Postconditions:
        - No mutation of self.content or other attributes occurs.
        - The returned string reflects the current snapshot of self.content and its items at the time of call.

## Side Effects:
    - None: the method performs no I/O, network access, or external mutation. Its only effect is to produce and return a string.
    - Note: calling str(item) may execute user-defined code inside item's __str__, which could have side effects if an item's implementation does so; such effects are outside this method's control.

### `src.ydata_profiling.report.presentation.core.container.Container.__repr__` · *method*

## Summary:
Returns a concise string representation of the Container that includes its contained "name" when present; does not modify the object's state.

## Description:
This method implements the Python object representation protocol used by builtin repr() and by interactive debugging/logging tools. Typical callers and contexts:
- The built-in repr(container_instance) call, including interactive REPL display and debugging sessions.
- Logging or diagnostic code that formats objects using %r or repr().
- Test assertions or error messages that include object representations.

It is implemented as a dedicated method (rather than inlined elsewhere) to provide a single, overridable canonical representation for Container instances and to follow Python's data model convention for object string representations. Keeping this logic in __repr__ allows subclasses or other parts of the system to rely on a stable, human-readable representation without duplicating formatting logic.

## Args:
This method takes no explicit arguments.

## Returns:
str: A short textual representation.
- If the container's content mapping contains the key "name", returns "Container(name=<value>)" where <value> is the raw value of self.content["name"] converted to string via the f-string formatting (None becomes "None", non-string objects are stringified).
- If the "name" key is absent, returns the literal "Container".

Edge cases:
- If "name" is present but set to None, the returned string will be "Container(name=None)".
- The method makes no guarantee about quoting or escaping of special characters contained in the name value; any newlines or braces in the name will appear verbatim in the returned string.

## Raises:
This method does not explicitly raise exceptions under the class invariants. Possible exceptions only occur if the object state violates assumed invariants:
- TypeError: If self.content is None or a type that does not support membership testing ("name" in self.content) or indexing (self.content["name"]).
- Exception from user-defined mapping types' __contains__ or __getitem__ implementations if those methods raise.

Under normal usage (Renderable/Container initialization sets self.content to a dict-like mapping), no exceptions are raised.

## State Changes:
Attributes READ:
- self.content (inspected for membership of the key "name")
- self.content["name"] (read when the "name" key exists)

Attributes WRITTEN:
- None. The method does not modify self or any external object.

## Constraints:
Preconditions:
- self.content must be a mapping-like object that supports membership testing and indexing (e.g., a dict). This is satisfied by the class constructors in this module, which set self.content to a dict.
- No other particular attribute initialization is required, but calling code should expect a stable mapping in self.content.

Postconditions:
- No mutation occurs on self or on external state.
- The method returns a deterministic string based on the current value of self.content["name"] (if present) or the constant "Container".

## Side Effects:
- None. The method performs no I/O, logging, or external service calls, and does not mutate objects outside of local temporary variables.

### `src.ydata_profiling.report.presentation.core.container.Container.render` · *method*

## Summary:
An abstract placeholder that enforces subclasses to provide a concrete rendering implementation; calling this base implementation raises NotImplementedError.

## Description:
This method is the rendering entry defined on Container (a Renderable-like component). The implementation in this file contains only a single statement that raises NotImplementedError, i.e., it provides no rendering behavior itself.

Known callers and context:
- No call sites or callers are present in this file. Callers, if any, are located elsewhere in the codebase and are not visible here.
- The presence of Renderable.render as an abstractmethod (in the Renderable base class) establishes that implementers are expected to provide a render() method. This implementation intentionally refuses to render so that subclasses must override it.

Why this is a separate method:
- It provides the canonical interface method (render) that subclasses must implement to return their presentation representation. The base implementation raises to ensure an override is supplied.

## Args:
- None

## Returns:
- Any
  - The base implementation does not return; it always raises NotImplementedError.
  - Subclass implementations determine the concrete return type and structure.

## Raises:
- NotImplementedError
  - Raised unconditionally by this method implementation.
  - Trigger condition: invoking Container.render() (or this specific implementation) directly.

## State Changes:
- Attributes READ:
  - None (the method body reads no attributes)
- Attributes WRITTEN:
  - None (the method body writes no attributes)

## Constraints:
- Preconditions:
  - The caller should invoke render() only on instances whose class overrides this method; invoking this base implementation will raise.
- Postconditions:
  - For this implementation: a NotImplementedError is raised and the object state remains unchanged.
  - For correctly overridden implementations: a presentation-specific object (type Any) is returned as defined by the subclass.

## Side Effects:
- This base implementation has no side effects: no I/O, no external service calls, and no mutations of objects outside self.
- Note: side effects may exist in subclass overrides but are not described here.

### `src.ydata_profiling.report.presentation.core.container.Container.convert_to_class` · *method*

## Summary:
Assign the provided class object to an instance's __class__ and, if the instance's content contains an "items" iterable, call a provided conversion function on each item. The method mutates the instance's runtime type and processes nested children in-place.

## Description:
This function sets obj.__class__ to the value passed as the first argument (named cls) and then checks whether obj.content contains the key "items". If so, it iterates over the iterable stored at obj.content["items"] and invokes flv(item) for every element.

Known callers and lifecycle stage:
- Typically invoked by deserialization / reconstruction or factory routines in the presentation pipeline that need to convert a generic Renderable-like object into a more specific renderer class. In such routines, callers supply the target class as the first argument and a conversion function (flv) that recursively converts nested entries.
- This conversion step is expected to occur during object reconstruction or initialization, before rendering, so that method resolution and type-specific behavior are correct for subsequent operations.

Why this logic is a separate method:
- Assigning a new runtime class and recursively converting nested children is a focused operation tied to the target class's structure (here: a Container). Encapsulating it:
  - keeps reconstruction code centralized and simple,
  - lets callers provide the conversion callback flv that controls how nested items are processed,
  - allows similar utilities for other types to handle their own nested keys consistently.

## Args:
    cls (type):
        The class object to assign to obj.__class__. The function expects this to be a class type (the intended runtime class for obj), but does not itself enforce that via a decorator; assignment compatibility is enforced by Python at runtime.
    obj (Renderable):
        The instance whose __class__ will be changed. Must expose a content attribute that behaves like a dict/mapping.
    flv (Callable):
        A callable invoked for each element in obj.content["items"] when present. Expected signature: Callable[[Any], Any] or Callable[[Renderable], Any]. The function is called for side effects; its return value is ignored.

## Returns:
    None
    - The function does not return a value; its effects are observable through mutated obj and any nested items processed by flv.

## Raises:
    TypeError:
        - If assigning cls to obj.__class__ is invalid because the target class has an incompatible instance layout (Python raises TypeError).
        - If obj.content["items"] exists but is not iterable, attempting to iterate may raise TypeError.
    AttributeError:
        - If obj has no content attribute, accessing obj.content will raise AttributeError.
    Any exception raised by flv:
        - Exceptions thrown by the flv callable propagate unchanged to the caller.

## State Changes:
    Attributes READ:
        obj.content
        obj.content["items"] (only accessed if the "items" key exists)
    Attributes WRITTEN:
        obj.__class__ is assigned to cls

## Constraints:
    Preconditions:
        - obj must be an object compatible with a Renderable-like interface: it must provide a content attribute that is a mapping.
        - If obj.content contains "items", the associated value must be iterable (e.g., list or tuple); otherwise iteration will fail.
        - cls must be a class object; additionally, it must be assignment-compatible with the current object's instance layout, or assignment will raise TypeError.
        - flv must be a callable that can process the elements stored in obj.content["items"] (if present).
    Postconditions:
        - After successful completion, obj.__class__ equals the cls argument.
        - If obj.content contained an "items" iterable, flv has been invoked on each element in iteration order. No further guarantees are made about modifications made by flv.

## Side Effects:
    - Mutates obj.__class__, changing the object's runtime type, which affects method resolution and isinstance checks.
    - Calls flv on each nested item; flv may mutate those items or raise exceptions.
    - No I/O or external service calls are performed by this function itself.

