# `item_renderer.py`

## `src.ydata_profiling.report.presentation.core.item_renderer.ItemRenderer` · *class*

## Summary:
Represents an abstract, typed renderable item in the presentation layer — a small wrapper that pairs a semantic item_type (string) with a content payload and common presentation metadata inherited from Renderable.

## Description:
ItemRenderer is an abstract subclass of Renderable used to represent a single report/presentation item that has:
- a declared item_type (semantic identifier), and
- a content payload (application-specific data) plus optional metadata (name, anchor_id, classes) managed by Renderable.

When to instantiate:
- Instantiate a concrete subclass (ItemRenderer is abstract) when you need a consistent object that holds content and metadata and exposes a render() method implemented by the subclass to produce the final representation (HTML fragment, JSON fragment, visualization spec, etc.).
- Typical callers: presentation factories, report builders, or higher-level render orchestration code that create specific item renderers (e.g., table renderer, histogram renderer, text block renderer) and call render().

Motivation and responsibility boundary:
- Centralizes the semantic item_type alongside the payload and shared presentation metadata.
- Leaves actual rendering to concrete subclasses; does not assume rendering format or side effects.
- Enforces a minimal, consistent initialization pattern so downstream code can rely on the presence of item_type and the content dict reference.

## State:
Attributes (including inherited):

- item_type: str
  - What: semantic identifier for the kind of item (e.g., "table", "image", "summary").
  - Type: str (constructor annotated as str). No runtime enforcement beyond annotation.
  - Constraints: conventionally a non-empty short identifier, but ItemRenderer does not validate; callers should validate if necessary.
  - Invariant: set during __init__ and not modified by ItemRenderer.

- content: Dict[str, Any] (inherited from Renderable)
  - What: primary data payload used by the renderer; structure is application-specific.
  - Type: dict-like mapping (Renderable expects a dict); recommended type: Dict[str, Any].
  - Behavior: Renderable.__init__ stores the passed dict reference on self.content and may mutate it by inserting "name", "anchor_id", and "classes" keys if those parameters are provided. Because the same dict object is retained, callers should be aware of shared-mutability side effects.

- name (property -> str) (inherited)
  - What: optional friendly name stored at content["name"] if provided during construction.
  - Access: reading self.name returns content["name"].
  - Edge: if no name was provided and content lacks "name", accessing self.name raises KeyError.

- anchor_id (property -> str) (inherited)
  - What: optional anchor identifier stored at content["anchor_id"] if provided.
  - Edge: reading without it being set raises KeyError.

- classes (property -> str) (inherited)
  - What: optional CSS classes or similar stored at content["classes"] if provided.
  - Edge: reading without it being set raises KeyError.

Inherited utility methods of note (from Renderable):
- __str__(): returns the class name (self.__class__.__name__). Useful for debugging/logging.
- convert_to_class(cls, obj, flv): classmethod that mutates obj.__class__ = cls (keeps instance data but changes its class). Present on ItemRenderer via inheritance; use with care as it changes type at runtime.

Class invariants:
- self.content is the exact dict reference passed to the constructor.
- self.item_type is set after initialization.
- Properties name/anchor_id/classes exist in content only if the corresponding constructor arguments were provided; callers should not assume their presence.

## Lifecycle:
Creation:
- Constructor signature:
  - item_type: str (required)
  - content: Dict[str, Any] (required)
  - name: Optional[str] = None
  - anchor_id: Optional[str] = None
  - classes: Optional[str] = None
- Instantiation requirement: ItemRenderer is abstract; instantiate a concrete subclass that implements render().

Usage pattern:
1. Create a content dict (fresh or shared, depending on desired mutability).
2. Instantiate a concrete ItemRenderer subclass with item_type and content (optionally name/anchor_id/classes).
3. Optionally inspect metadata properties (self.name, self.anchor_id, self.classes) — guard access if these were not provided.
4. Call render() on the concrete instance to obtain the final output.
5. No automatic cleanup is provided by ItemRenderer; if subclasses acquire external resources, they must implement cleanup.

Destruction / cleanup:
- None provided. ItemRenderer does not manage resources (no context-manager protocol, no close()). Subclasses that allocate resources must provide their own cleanup.

## Method Map:
graph LR
  SubclassInit[ConcreteSubclass.__init__] --> ItemInit[ItemRenderer.__init__]
  ItemInit --> RenderableInit[Renderable.__init__]
  RenderableInit --> AssignContent[self.content assigned (mutates dict with name/anchor_id/classes if provided)]
  ItemInit --> AssignType[self.item_type assigned]
  Instance[Concrete instance ready] --> RenderCall[ConcreteSubclass.render() called by caller]
  Instance --> StrCall[__str__() -> class name]
  ItemRendererClass --> ConvertToClass[convert_to_class(cls, obj, flv) (inherited utility)]

(Interpretation: Concrete subclass initialization should call ItemRenderer.__init__, which delegates to Renderable.__init__. After construction, caller invokes render(). Utility methods __str__ and convert_to_class are available via inheritance.)

## Raises:
- __init__ (ItemRenderer) itself does not explicitly raise.
- Indirect/observable exceptions:
  - TypeError or AttributeError depending on misuse, e.g., if content is not a dict-like object and downstream code assumes dict methods.
  - KeyError when accessing name, anchor_id, or classes properties if those keys are not present in content. These keys are only inserted by Renderable.__init__ when the corresponding constructor arguments are not None.
  - Subclass render() implementations may raise domain-specific exceptions.

## Example:
(Assume ConcreteItemRenderer is a concrete subclass that implements render(). The following demonstrates typical usage without defining the subclass.)

1) Prepare content:
   content = {"data": [1, 2, 3]}

2) Instantiate concrete renderer:
   item = ConcreteItemRenderer("table", content, name="Summary Table", anchor_id="tbl-1")

3) Inspect metadata (guarded access if uncertain):
   if "name" in item.content:
       display_name = item.name

4) Produce final representation:
   output = item.render()

5) Note: access to item.name when "name" key is absent will raise KeyError; handle accordingly.

Best practices:
- Pass a fresh dict for content if you do not want Renderable.__init__ to mutate an external object.
- Validate item_type in caller code if downstream logic depends on a restricted set of type identifiers.
- Prefer explicit cleanup in subclasses if they manage resources.

### `src.ydata_profiling.report.presentation.core.item_renderer.ItemRenderer.__init__` · *method*

## Summary:
Initializes an ItemRenderer instance by delegating common presentation metadata setup to the Renderable base class and storing the semantic item_type; as a result the instance will have self.content (the exact dict passed, possibly mutated with metadata) and self.item_type set.

## Description:
Known callers and context:
- Called indirectly when constructing any concrete subclass of ItemRenderer during object instantiation (ConcreteSubclass.__init__ should call ItemRenderer.__init__).
- Typical callers are presentation factories, report builders, or higher-level render orchestration code that create specific renderers (e.g., table, image, histogram, or text renderers).
- Invocation occurs during the object construction lifecycle as part of initializing a renderable item before render() is called.

Why this is a separate method:
- Centralizes shared initialization logic for all concrete item renderers (preserving a consistent pattern for content and metadata handling).
- Delegates common metadata assignment to Renderable.__init__ while ensuring each ItemRenderer keeps an explicit semantic item_type.
- Keeps concrete subclasses focused on rendering behavior (render()) rather than repeating boilerplate metadata setup.

## Args:
    item_type (str):
        Semantic identifier for the kind of item (e.g., "table", "image", "summary").
        - Required. Annotated as str but not runtime-validated; callers should pass a short non-empty identifier by convention.
    content (dict):
        Primary data payload used by the renderer. The exact structure is application-specific.
        - Required. The same dict object passed in is retained on self.content.
        - Must be a mutable mapping that supports item assignment (i.e., content[key] = value), since Renderable.__init__ may insert metadata keys.
    name (Optional[str], default=None):
        Optional friendly name. If not None, Renderable.__init__ will insert content["name"] = name.
    anchor_id (Optional[str], default=None):
        Optional anchor identifier. If not None, Renderable.__init__ will insert content["anchor_id"] = anchor_id.
    classes (Optional[str], default=None):
        Optional CSS/classes string. If not None, Renderable.__init__ will insert content["classes"] = classes.

## Returns:
    None
    - As an initializer, it returns None implicitly.
    - Side-effect: the instance's attributes are set (see State Changes).

## Raises:
    TypeError:
        Raised if the provided content does not support item assignment (e.g., if content is an immutable or non-mapping object). This can occur inside Renderable.__init__ when attempting to set content["name"]/["anchor_id"]/["classes"].
    (No other exceptions are explicitly raised by ItemRenderer.__init__; subclasses or callers may raise additional exceptions.)

## State Changes:
Attributes READ:
    - None on self prior to delegation; the initializer does not read existing instance attributes.

Attributes WRITTEN:
    - self.content: assigned to the exact dict provided as the content argument by Renderable.__init__.
    - self.content["name"]: may be written if name is not None (set by Renderable.__init__).
    - self.content["anchor_id"]: may be written if anchor_id is not None (set by Renderable.__init__).
    - self.content["classes"]: may be written if classes is not None (set by Renderable.__init__).
    - self.item_type: assigned to the provided item_type value by ItemRenderer.__init__.

## Constraints:
Preconditions:
    - item_type should be a string (annotation); callers should ensure it represents a valid semantic identifier if the rest of the system depends on a restricted set.
    - content must be a mutable mapping (dict-like) that supports item assignment; otherwise a TypeError may be raised.

Postconditions:
    - self.item_type == item_type (the passed item_type is stored on the instance).
    - self.content is the identical object passed as content.
    - If name/anchor_id/classes were provided (not None), the corresponding keys ("name", "anchor_id", "classes") are present in self.content with the provided values.

## Side Effects:
    - Mutates the provided content dict by adding metadata keys ("name", "anchor_id", "classes") when their corresponding arguments are provided.
    - No I/O, network calls, or external service interactions occur in this initializer.
    - No resource allocation or cleanup responsibilities are introduced here; subclasses that acquire external resources must manage them separately.

