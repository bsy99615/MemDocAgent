# `collapse.py`

## `src.ydata_profiling.report.presentation.core.collapse.Collapse` · *class*

## Summary:
Represents a collapsible UI element that groups a ToggleButton (the control) and a Renderable item (the collapsible content). It is an ItemRenderer specialization with item_type "collapse" and holds the button and item in its content mapping.

## Description:
Collapse is a thin presentation-layer object used to model a collapsible widget in the reporting/presentation system. Instantiate Collapse when you need to present a piece of content that can be shown/hidden by a toggle control. The class itself does not implement rendering — subclasses or platform-specific renderers should implement render() to produce the final output (HTML, JSON, etc).

Typical callers/factories:
- Any report builder that assembles presentation components will create a ToggleButton and a Renderable (e.g., a panel, table or nested group) and then bundle them using Collapse(button, item, **kwargs).
- Deserialization routines that rebuild object graphs from a serialized representation will call Collapse.convert_to_class(...) to restore a previously-serialized object into a Collapse instance and recursively convert nested content.

Motivation and responsibility boundary:
- Collapse enforces a consistent content structure for collapsible widgets: exactly two primary children, named "button" and "item".
- It delegates actual presentation rendering to subclasses or external renderers; Collapse's responsibility is structural (type, content mapping, and conversion logic).

## State:
Public attributes inherited or set by Collapse:

- item_type (str)
  - Value: "collapse"
  - Invariant: always equals "collapse" for instances created via __init__ (set by calling ItemRenderer.__init__).
  - Purpose: identifies the renderer type for dispatch/templating.

- content (Dict[str, Any]) — inherited from Renderable
  - Required keys:
    - "button": ToggleButton
      - Type: ToggleButton (or an object compatible with toggle behavior)
      - Valid values: an instance of ToggleButton (or subclass). If absent or of wrong type, behavior is undefined and downstream renderers may raise errors.
    - "item": Renderable
      - Type: Renderable (or a subclass instance)
      - Valid values: any Renderable instance to be shown/hidden.
  - Optional keys (populated when corresponding kwargs are supplied to the constructor via the Renderable base):
    - "name": str — user-facing or internal name
    - "anchor_id": str — identifier for anchors/links
    - "classes": str — CSS or style classes
  - Invariant: content is a dict and, for correctly constructed instances, contains at least "button" and "item".

Notes about __init__ parameters:
- button: ToggleButton — required; expected to be an instance of ToggleButton (or subclass). There are no runtime type checks in the source; callers must ensure the correct type.
- item: Renderable — required; expected to be an instance of Renderable (or subclass).
- **kwargs: forwarded to ItemRenderer / Renderable constructor. Typical keyword args:
  - name: Optional[str] — will be stored in content["name"] if provided.
  - anchor_id: Optional[str] — stored in content["anchor_id"].
  - classes: Optional[str] — stored in content["classes"].

Class invariants:
- After construction, instance.item_type == "collapse".
- content is a dict and, when constructed as intended, content["button"] and content["item"] reference the passed objects.
- convert_to_class may change an object's __class__ to Collapse; any code that relies on isinstance(obj, Collapse) should be aware that convert_to_class mutates obj in-place.

## Lifecycle:
Creation:
- Instantiate by calling Collapse(button, item, **kwargs).
  - Required: button (ToggleButton), item (Renderable).
  - Optional kwargs: name, anchor_id, classes — passed through to the base Renderable constructor and stored in content.

Usage:
- Typical sequence:
  1. Construct ToggleButton and item Renderable.
  2. Create Collapse(button, item, name=..., anchor_id=..., classes=...).
  3. Pass Collapse instance to a renderer that dispatches on item_type or class and calls its render() method.
  4. A concrete renderer/subclass should implement render() to produce the final representation (e.g., HTML snippet combining button and item, arranging collapsed state).
- convert_to_class is used during deserialization reconstruction:
  - Given a generic Renderable-like object (for example reconstructed from JSON) whose content dict contains nested serializations for "button" and "item", call Collapse.convert_to_class(obj, flv) to:
    - set obj.__class__ to Collapse
    - call flv on obj.content["button"] and obj.content["item"] if present
  - flv must be a callable capable of converting nested content representations into their proper Renderable/ItemRenderer instances (mutating objects in-place or returning reconstructed instances per the deserialization strategy used).

Destruction:
- No special cleanup is required.
- Collapse does not provide context-management or close() hooks. If nested items require cleanup, the caller is responsible for invoking those.

## Method Map:
Graph of primary method relationships and typical invocation order:

mermaid
graph LR
    A[construct: Collapse(button,item,**kwargs)] --> B[item_type set to "collapse"]
    A --> C[content: {"button": button, "item": item, ...}]
    D[renderer/dispatcher] --> E[collapse.render()] 
    F[deserializer] --> G[Collapse.convert_to_class(obj, flv)]
    G --> H[flv(obj.content["button"]), flv(obj.content["item"])]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style G fill:#ff9,stroke:#333,stroke-width:1px

## Methods (behavioral summary):
- __init__(self, button: ToggleButton, item: Renderable, **kwargs)
  - Initializes a Collapse by calling ItemRenderer.__init__("collapse", {"button": button, "item": item}, **kwargs).
  - Side effect: content dict is created/assigned on the instance and the base Renderable may inject "name", "anchor_id", "classes" if provided.

- __repr__(self) -> str
  - Returns the static string "Collapse".
  - Useful for debugging and textual representations.

- render(self) -> Any
  - Abstract in this class: raises NotImplementedError().
  - Concrete subclasses or external renderers should implement this method to return the actual representation (HTML, JSON fragment, structured object) for the collapse widget.

- @classmethod convert_to_class(cls, obj: Renderable, flv: Callable) -> None
  - Mutates obj.__class__ to be cls (i.e., Collapse).
  - If "button" in obj.content: calls flv(obj.content["button"]).
  - If "item" in obj.content: calls flv(obj.content["item"]).
  - Purpose: recursion-friendly deserialization hook to rebuild nested Renderable types after reading a neutral representation.
  - Expected behavior for flv: a callable that accepts a Renderable-like object or serialized container and converts/mutates it into the appropriate runtime object(s). The exact return contract depends on the deserialization design; Collapse.convert_to_class treats flv as a mutator/caller-only (does not use any return value).

## Raises:
- __init__: does not raise explicit exceptions in source code.
  - However, passing non-compatible types (for example, non-ToggleButton for button or non-Renderable for item) may lead to runtime errors elsewhere (AttributeError, TypeError) when calling renderers or when other code expects the button/item to implement specific interfaces.
- render(): raises NotImplementedError() by design; subclasses must override to provide concrete rendering.
- convert_to_class: does not itself raise explicit exceptions in the source; if obj is missing .content or flv raises, those exceptions will propagate.

## Example:
- Creating a Collapse instance:
  - Create a ToggleButton instance (toggle) and a Renderable instance (content_item).
  - collapse = Collapse(toggle, content_item, name="details", anchor_id="collapse-details", classes="my-collapse")
  - Pass collapse to a renderer that inspects collapse.item_type or isinstance(collapse, Collapse) and calls collapse.render().

- Using convert_to_class during deserialization:
  - Suppose obj is a generic Renderable-like object reconstructed from JSON that has obj.content == {"button": button_repr, "item": item_repr, ...}
  - Define flv(child_obj): a function that inspects child_obj and converts it into a concrete ItemRenderer/Renderable (possibly by calling child_class.convert_to_class recursively).
  - Call Collapse.convert_to_class(obj, flv) to convert obj into a Collapse and recursively convert its children.

Notes for implementers:
- Reimplementation must adhere to the Renderable/ItemRenderer contract: Renderable stores content dict and optionally populates "name", "anchor_id", "classes"; ItemRenderer adds an item_type attribute.
- The convert_to_class pattern intentionally mutates obj.__class__ to avoid allocating a new object during deserialization; implementers should preserve this behavior for compatibility with existing deserialization logic.
- Implement concrete renderers separately; do not implement presentation output in this structural class unless you intend to provide a platform-specific variation.

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__init__` · *method*

## Summary:
Initializes the Collapse presentation object by setting its renderer type to "collapse" and storing the provided toggle control and collapsible content in the instance's content mapping.

## Description:
Known callers and context:
- Report builders and presentation assemblers that compose UI widgets will call this during construction when they need a collapsible element combining a ToggleButton and a nested Renderable.
- Deserialization routines that reconstruct object graphs may call Collapse.convert_to_class(...) after creating a generic Renderable-like object; however, direct construction via this __init__ is used when programmatically building reports.
Lifecycle stage:
- Invoked at object construction time to create a structural container for a two-part collapsible widget (control + content).
Why this is its own method:
- Encapsulates the structural contract for a collapse widget (ensuring the content mapping contains "button" and "item") and delegates rendering to concrete renderers/subclasses.
- Keeps construction logic small, explicit, and consistent across the presentation system instead of inlining the mapping creation at call sites.

## Args:
    button (ToggleButton): Required. The toggle control that will show/hide the content. Expected to be an instance of ToggleButton or a compatible subclass.
    item (Renderable): Required. The content to be collapsed/expanded. Expected to be an instance of Renderable or subclass.
    **kwargs: Optional keyword arguments forwarded to the ItemRenderer / Renderable constructor. Supported keys:
        name (str, optional): If provided and not None, stored as content["name"].
        anchor_id (str, optional): If provided and not None, stored as content["anchor_id"].
        classes (str, optional): If provided and not None, stored as content["classes"].
    Notes on kwargs:
        - Only the named optional parameters (name, anchor_id, classes) are accepted by the upstream constructors. Passing unknown kwargs will raise a TypeError when forwarded to ItemRenderer.__init__.

## Returns:
    None — constructors do not return a value. The effect is reflected in modifications to the instance state (see State Changes).

## Raises:
    TypeError: If unexpected keyword arguments are passed in **kwargs (since ItemRenderer.__init__ expects only name, anchor_id, classes), a TypeError will be raised by the super call.
    No explicit type-checking errors are raised by this constructor itself for incorrect button/item types; however, passing objects that do not meet ToggleButton or Renderable expectations may cause runtime errors later in renderers or when consumers access expected attributes.

## State Changes:
    Attributes READ:
        - None from self (constructor uses only passed arguments and super calls).
    Attributes WRITTEN:
        - self.content (dict): assigned via Renderable.__init__ (called by ItemRenderer.__init__) to a dict that contains at least:
            - "button": the passed button object (stored by this constructor)
            - "item": the passed item object (stored by this constructor)
          Additionally, if kwargs include name/anchor_id/classes (not None), those keys are added to self.content by Renderable.__init__.
        - self.item_type (str): set to "collapse" by ItemRenderer.__init__.

## Constraints:
    Preconditions:
        - button should be a ToggleButton (or subclass) instance; item should be a Renderable (or subclass) instance for correct subsequent behavior.
        - kwargs must be limited to the optional parameters accepted by ItemRenderer.__init__: name, anchor_id, classes. Unexpected kwargs will raise TypeError.
    Postconditions:
        - After return, self.item_type == "collapse".
        - self.content is a dict containing at least the keys "button" and "item" referencing the objects passed in.
        - If name/anchor_id/classes were provided (and not None), those keys exist in self.content with the provided string values.

## Side Effects:
    - Stores references to the provided button and item in self.content (no deep copy). Mutations to the passed objects after construction will be observable via the Collapse instance.
    - No I/O, external service calls, or global state mutations occur.
    - No rendering is performed; this constructor purely builds the structural state.

## Edge cases and implementation notes:
    - The constructor performs no runtime type-checking; callers are responsible for providing compatible objects.
    - If callers rely on the presence of content["name"], content["anchor_id"], or content["classes"], they must provide them via kwargs; otherwise, accessing the corresponding properties will raise KeyError.
    - This constructor intentionally forwards kwargs to the base constructors to centralize handling of common metadata (name, anchor_id, classes).

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__repr__` · *method*

## Summary:
Returns a stable, human-readable short representation for the object: the literal string "Collapse".

## Description:
Known callers and context:
- The built-in repr() function (repr(obj)) and Python's interactive object display will call this method to obtain a textual representation.
- Debugging and logging code that calls repr() on objects, and code that serializes or inspects renderable components for diagnostics, may invoke this method.
- When objects are shown inside containers (lists, dicts) or in debugging tools, the container's representation will use this method for each element.

Lifecycle stage:
- Invoked any time a string representation of the object is required (debugging, logging, interactive inspection, or templating/render pipeline diagnostics).
- It is called after the object has been constructed; there is no special lifecycle stage required beyond instantiation.

Rationale for being a separate method:
- Providing a concise, consistent representation for this specific subclass improves readability in logs and debugging output and distinguishes Collapse objects from other renderable items.
- Overriding __repr__ keeps representation logic centralized and trivial, avoiding repetition in external utility code.

## Args:
None — this method takes only the implicit self parameter.

## Returns:
str — Always returns the literal string "Collapse".
- Possible values: exactly "Collapse".
- Edge cases: None. The return value is constant and does not depend on object state.

## Raises:
None — this implementation does not raise exceptions.

## State Changes:
Attributes READ:
- None. This method does not access any attributes on self.

Attributes WRITTEN:
- None. The method does not modify self or any of its attributes.

## Constraints:
Preconditions:
- self should be a properly instantiated Collapse object (constructed via Collapse.__init__); no other preconditions are required.

Postconditions:
- The object remains unchanged after the call.
- A string "Collapse" is returned.

## Side Effects:
- None. The method performs no I/O, no external service calls, and does not mutate objects outside self.

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.render` · *method*

## Summary:
Describe the rendering contract for a collapsible presentation item that composes a ToggleButton and a nested Renderable and returns a composed, serializable representation without mutating the renderer's state. Note that in the repository the method currently raises NotImplementedError.

## Description:
Current implementation:
- The method implementation in the source raises NotImplementedError; it is a placeholder and must be implemented to produce usable output.

Verifiable provenance of data available to render:
- Collapse.__init__ constructs this renderer via ItemRenderer and passes content={"button": button, "item": item}. Therefore self.content is expected to contain keys "button" and "item".
- ItemRenderer.__init__ sets self.item_type (the ItemRenderer "type" tag) and delegates to Renderable.__init__.
- Renderable.__init__ stores the provided content dict at self.content and, if name/anchor_id/classes were given to construction, inserts them as entries "name", "anchor_id", and "classes" into self.content.
- ToggleButton.render in this codebase is also declared but currently raises NotImplementedError (so nested renders may themselves be unimplemented in this repository snapshot).

Why this method exists separately:
- The Collapse renderer's responsibility is to take two nested renderables (button and item) and produce a single consistent serialized representation describing the collapse. That composition logic should be centralized to ensure consistency across the presentation layer.

## Args:
None (signature: render(self) -> Any)

## Returns:
Any — a serializable representation (implementer-defined) that must include rendered forms of the two nested components. Required content (minimum contract):
- "button": the value produced by calling render() on self.content["button"]
- "item": the value produced by calling render() on self.content["item"]

Optional additions (implementer may include):
- Any metadata copied from self.content such as "name", "anchor_id", or "classes" if the consumer of the serialized form expects them.
Notes:
- The concrete type (dict, tuple, custom object) is not enforced by the Collapse class; choose a structure consistent with the surrounding rendering pipeline and document it.
- If a nested renderer returns None, the implementation should either include the None in the returned representation or document a normalization rule (for example, omit the key).

Minimal recommended returned structure (descriptive example, not prescriptive):
- {"button": <button_serialized>, "item": <item_serialized>, "name": <opt_name_if_present>, "anchor_id": <opt_anchor_if_present>}

## Raises:
- NotImplementedError: as present now in the source — calling this exact implementation will raise NotImplementedError.
Recommended behavior for concrete implementations:
- KeyError: if "button" or "item" are absent from self.content and your implementation requires them (raise with a clear message).
- TypeError: if the objects stored under "button" or "item" do not expose a callable render() method and your implementation requires render() to exist.

## State Changes:
Attributes READ:
- self.content (reads self.content["button"], self.content["item"], and optionally "name", "anchor_id", "classes")
- self.item_type (readable attribute set by ItemRenderer)
Attributes WRITTEN:
- None. A correct implementation must not mutate self.content, self.item_type, or other persistent attributes of self during rendering. Rendering should be a pure serialization step.

## Constraints:
Preconditions (what must be true before calling):
- self.content is a dict containing keys:
    - "button": an object (preferably ToggleButton instance) that exposes a callable render() method.
    - "item": an object (preferably a Renderable instance) that exposes a callable render() method.
- If the code has invoked Collapse.convert_to_class on a previously deserialized object, that utility will set obj.__class__ = Collapse and call flv on nested entries; ensure convert_to_class has run if the object was created from plain data.
Postconditions (what is guaranteed by an implementation that follows this contract):
- The returned value contains serialized representations for both the button and the item per the minimal contract above.
- No attributes of self are mutated.

## Side Effects:
- The method will call render() on the nested button and item; any side effects originate in those nested renderers.
- Collapse.render itself should avoid performing I/O or other external side effects; any such behavior must be documented explicitly by the implementer.

## Implementation guidance (step-by-step, without prescribing code syntax):
1. Validate input shape:
   - Confirm that "button" and "item" exist in self.content. If not present, raise KeyError with a clear message (for example: "Collapse.content must contain 'button' and 'item'").
   - Confirm that each nested value has a callable render attribute. If not, raise TypeError with a message explaining the expectation.
2. Invoke nested renders in a safe order (typically render the button first, then the item), capturing their returned serialized values.
3. Compose a container that includes at least the keys "button" and "item" mapped to their serialized outputs. Optionally include "name", "anchor_id", and "classes" copied from self.content if required by your presentation schema.
4. Return the composed representation. Do not modify self.content or other self attributes.
5. Document any deviations from this minimal contract for downstream consumers (for example, omitting keys when nested renders return None, or including additional metadata fields).

## Notes on nested renderer availability:
- Because ToggleButton.render and other nested Renderable.render implementations may themselves be unimplemented in this snapshot, a complete system requires implementing those nested renderers (or using placeholders) before Collapse.render can produce a fully usable serialized output.

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.convert_to_class` · *method*

## Summary:
Set the object's runtime class to the calling class and recursively invoke a provided conversion function on any nested "button" and "item" entries in the object's content, mutating the object's identity.

## Description:
This classmethod replaces obj.__class__ with cls and then, if present, passes obj.content["button"] and obj.content["item"] to the provided callable flv. It is an override for subclasses of ItemRenderer (here: Collapse) to ensure that nested elements inside the object's content are processed the same way as the object itself.

Known callers and lifecycle stage:
- No direct call-sites are present in the provided source snapshot. Typical callers are deserialization/factory routines that reconstruct a tree of Renderable instances from a generic representation (e.g., dicts or partially-typed objects) and need to convert generic Renderable objects into concrete renderer classes.
- This method is intended to be invoked during the reconstruction/initialization phase of a presentation/rendering pipeline, after a generic object has been created and before rendering.

Rationale for being a separate method:
- The base Renderable.convert_to_class only sets the object's class. Collapse.convert_to_class is responsible for additional bookkeeping specific to Collapse: recursively converting nested "button" and "item" content entries. Keeping this logic separate avoids duplicating recursive conversion logic at call-sites and isolates Collapse-specific behavior in the type that owns the structure.

## Args:
    cls (type): The class object to assign to obj.__class__. In typical usage this is the Collapse class (or a Collapse subclass) because the method is a classmethod.
    obj (Renderable): The instance whose class will be changed. Must have a content attribute that is a dict-like mapping.
    flv (Callable): A callable expected to accept the nested entries (e.g., a Renderable or nested structure) and perform conversion/mutation in-place. Expected signature: Callable[[Renderable], Any] or Callable[[Any], Any]. The return value of flv is ignored.

## Returns:
    None

## Raises:
    TypeError: If assigning cls to obj.__class__ is invalid (for example, if the new class has an incompatible instance layout with the current object), Python will raise TypeError.
    AttributeError: If obj does not have a content attribute (i.e., it is not a Renderable or does not follow the expected interface), attribute access will raise AttributeError.
    Any exception raised by flv will propagate unchanged (e.g., if flv assumes a specific type for the nested entries and that assumption is violated).

## State Changes:
    Attributes READ:
        obj.content
        obj.content["button"] (only read if the "button" key exists)
        obj.content["item"] (only read if the "item" key exists)
    Attributes WRITTEN:
        obj.__class__ is assigned to cls

## Constraints:
    Preconditions:
        - obj must be an object compatible with Renderable: it must expose a content attribute that is a dict-like mapping.
        - cls must be a class appropriate for obj (i.e., assignment-compatible). In CPython this typically requires compatible instance layout; otherwise assignment will fail with TypeError.
        - flv must be a callable able to handle the nested objects stored under "button" and "item" (if present); flv is expected to perform any necessary in-place conversions or mutations.

    Postconditions:
        - After successful return, obj.__class__ is cls.
        - If obj.content contained "button" and/or "item", flv has been invoked on each corresponding value (in the order: button then item), though their state after flv depends on flv's behavior.
        - No return value is produced; the conversion work is done by mutation.

## Side Effects:
    - Mutates obj.__class__, changing the object's runtime type and behavior (method resolution, isinstance/issubclass checks, etc.).
    - Calls flv on nested content entries; flv may further mutate those objects or raise exceptions.
    - No I/O or external service calls are performed by this method itself.

