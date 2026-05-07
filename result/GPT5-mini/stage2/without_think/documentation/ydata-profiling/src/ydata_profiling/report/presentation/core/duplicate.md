# `duplicate.py`

## `src.ydata_profiling.report.presentation.core.duplicate.Duplicate` · *class*

## Summary:
A small ItemRenderer subclass that encapsulates duplicate-row results (a pandas.DataFrame) as renderer content and identifies itself with the item_type "duplicate".

## Description:
Duplicate is a presentation-layer wrapper that stores a DataFrame containing duplicate-row information under the content key "duplicate" and registers the renderer type as "duplicate". It does not implement rendering itself — render() raises NotImplementedError — so the class exists as a thin, well-typed container used by the report-generation/presentation pipeline or by renderer factories that expect an ItemRenderer instance with item_type == "duplicate".

Typical instantiation scenarios:
- A data-profiling pipeline detects duplicate rows and wants to hand those results to a presentation component. Instead of passing a raw DataFrame, it creates a Duplicate instance which provides a consistent interface with other ItemRenderer-derived items.
- A renderer factory or subclass will accept a Duplicate instance and implement render() to produce HTML, JSON or other presentation formats.

Motivation and boundary:
- Responsibility: hold the duplicates DataFrame in the standardized ItemRenderer content dict and identify the item_type. It does not perform duplicate detection or any rendering — those concerns are outside this class.
- Separation: keeps presentation-layer data (how to render) separate from detection logic and rendering implementations.

## State:
Attributes provided/managed by this class (direct or inherited):

- item_type (str)
  - Value: the literal string "duplicate"
  - Invariant: item_type == "duplicate"
  - Set in __init__ via ItemRenderer super call and assignment.

- content (dict)
  - Structure: {"duplicate": pandas.DataFrame}
  - The 'duplicate' key MUST map to the DataFrame passed to __init__. No transformation is performed by Duplicate.
  - Invariant: "duplicate" in content and content["duplicate"] is the original object supplied as the duplicate argument (expected to be a pandas.DataFrame or DataFrame-like object).

- name (Optional[str])
  - Inherited from ItemRenderer constructor (may be None). Typically used as a human-readable label or identifier in the presentation layer.

- anchor_id (Optional[str]) and classes (Optional[str])
  - Passed via **kwargs to ItemRenderer. These are presentation hints (anchor identifiers or CSS classes) managed by the parent.

Notes about types:
- The constructor's duplicate parameter is annotated as pd.DataFrame in the source. In practice this means a pandas.DataFrame object is expected; any object with equivalent interface may work but that is not enforced by Duplicate (no runtime type checks).

Class invariants:
- After __init__, the instance must satisfy:
  - self.item_type == "duplicate"
  - isinstance(self.content, dict)
  - "duplicate" in self.content

## Lifecycle:
Creation:
- Call signature: Duplicate(name: str, duplicate: pandas.DataFrame, **kwargs)
  - name: required positional argument in the source signature.
  - duplicate: expected pandas.DataFrame (the duplicate rows).
  - **kwargs: forwarded to ItemRenderer; commonly include anchor_id and classes.

Usage:
- Construction stores the DataFrame in content and registers item_type.
- Consumers should treat Duplicate as an item descriptor: pass it to presentation components or renderer factories.
- Before attempting to obtain a rendered output, a concrete renderer must implement render() for this object. Calling Duplicate.render() on this class raises NotImplementedError.

Typical sequence:
1. Instantiate Duplicate with name and DataFrame.
2. Pass Duplicate instance to a renderer/factory that understands item_type "duplicate".
3. The renderer invokes Duplicate.content["duplicate"] to access the DataFrame and returns the final presentation (HTML/markdown/json/etc).

Destruction / cleanup:
- Duplicate has no external resources or open handles. No explicit cleanup, context management, or close() is required.

## Method Map:
flowchart LR
    A[Duplicate.__init__] --> B[ItemRenderer.__init__ (stores content,name,anchor_id,classes)]
    B --> C[item_type set to "duplicate"]
    A --> D[content["duplicate"] holds DataFrame]
    E[render()] -. NotImplemented .-> F[Must be implemented by renderer/factory]

(Above describes dependencies and typical invocation order: construct -> parent init stores state -> renderer implements render.)

## Methods and behavior (reimplementation notes):
- __init__(self, name: str, duplicate: pandas.DataFrame, **kwargs)
  - Purpose: construct a Duplicate renderer item and store duplicate DataFrame under content key "duplicate".
  - Implementation detail (observed): Delegates to ItemRenderer constructor with:
    - item_type: "duplicate"
    - content: {"duplicate": duplicate}
    - passes name=name and **kwargs through
  - Postconditions: instance.item_type == "duplicate"; instance.content["duplicate"] is the object passed in.

- __repr__(self) -> str
  - Returns the string "Duplicate".
  - No side effects.

- render(self) -> Any
  - Intentionally unimplemented; raises NotImplementedError() in this class.
  - Consumers/implementers must override this method to produce presentation output (type depends on renderer contract — often str for HTML, dict for JSON, or other structured object).
  - Because render is not implemented, Duplicate behaves as a descriptor rather than a concrete renderer.

## Raises:
- __init__:
  - The constructor does not explicitly raise exceptions in the source.
  - Possible runtime exceptions may arise if ItemRenderer.__init__ validates arguments or if callers pass incompatible kwargs. Duplicate itself makes no type checks, so passing a non-DataFrame will not raise immediately here but may raise later when consuming code assumes a pandas.DataFrame.

- render:
  - Always raises NotImplementedError() as implemented in this class.

## Example:
- Create a Duplicate instance (assuming df is a pandas.DataFrame):
  duplicate_item = Duplicate(name="duplicates", duplicate=df)
- Typical usage:
  - Pass duplicate_item to a renderer factory that knows how to handle item_type "duplicate". The renderer will access duplicate_item.content["duplicate"] to obtain the DataFrame and produce output.
- Calling duplicate_item.render() on this class will raise NotImplementedError; the expected pattern is that a concrete renderer will subclass/accept Duplicate and provide an implementation of render() to produce the final presentation.

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.__init__` · *method*

## Summary:
Initialize the Duplicate presentation item by storing a pandas DataFrame under the "duplicate" content key and setting the item's type to "duplicate".

## Description:
This initializer constructs the object that the presentation layer uses to represent duplicate-row analysis results. It is invoked when a Duplicate renderable item is instantiated prior to rendering/output (i.e., during construction of the report's renderable items). The method centralizes the content shape and item_type so templates and renderers can rely on a consistent representation for duplicate items.

It is an initializer (constructor) because the class must ensure a consistent content dict and the canonical item_type are set at construction time; therefore this logic is not inlined at call sites.

## Args:
    name (str):
        Required human-readable name for the item. This value is forwarded to the Renderable constructor and will be stored in content["name"] by the Renderable base if provided.
    duplicate (pd.DataFrame):
        The pandas DataFrame containing duplicate-row information to present. This object is stored by reference in the content dict under the "duplicate" key.
    **kwargs:
        Optional keyword arguments forwarded to ItemRenderer / Renderable. Recognized keyword arguments by the base classes:
        - anchor_id (Optional[str]): If provided, Renderable will store it into content["anchor_id"].
        - classes (Optional[str]): If provided, Renderable will store it into content["classes"].
        Other kwargs are forwarded but have no defined effect in Renderable unless those names are accepted by future base-class versions.

## Returns:
    None
    (As an __init__, it does not return a value. After return the instance is fully constructed with its content and item_type set.)

## Raises:
    No exceptions are raised explicitly by this initializer itself.
    Note: Because Renderable.property accessors expect certain keys in content, accessing self.name, self.anchor_id, or self.classes will raise KeyError if the corresponding keys are absent. This initializer, given the signature, should ensure content["name"] is present because name is a required str parameter; however, if callers pass None or omit keys via non-idiomatic usage, KeyError can occur later when those properties are accessed.

## State Changes:
Attributes READ:
    - None explicitly read on self by this method.

Attributes WRITTEN:
    - self.content (dict): assigned to {"duplicate": duplicate} by this constructor (and then possibly augmented by Renderable.__init__ with "name", "anchor_id", "classes" if provided).
    - self.item_type (str): set to the literal "duplicate" (assigned in ItemRenderer.__init__).

## Constraints:
Preconditions:
    - name should be a str (the constructor signature requires str).
    - duplicate should be a pandas DataFrame (pd.DataFrame) or a compatible object; callers should provide a valid DataFrame.

Postconditions:
    - self.item_type == "duplicate".
    - self.content is a dict with at minimum the key "duplicate" mapping to the provided DataFrame.
    - If name/anchor_id/classes were provided (and not None), those keys exist in self.content with the supplied values.

## Side Effects:
    - No I/O, network, or external service calls occur.
    - The provided duplicate DataFrame is stored by reference in self.content (no copy is made here); therefore later mutations to that DataFrame by other code will be visible through this object's content.

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.__repr__` · *method*

## Summary:
Returns a concise, human-friendly textual representation for the object — the constant string "Duplicate" — used when the object is converted to its representation form (e.g., by repr()).

## Description:
This method provides the object's textual identifier used in debugging, logging, interactive shells, and any code that calls the built-in repr() on the instance. Typical callers include:
- Python's built-in repr() (explicit calls or implicit via printing containers, logging, or debugging tools).
- Logging and debugging routines that include object representations in messages.
It is implemented as a dedicated method to override the default object representation and produce a stable, simple label for instances of Duplicate rather than exposing the default memory-address-based representation. Keeping this logic in its own method ensures that any textual representation is centralized and easily changed without affecting other rendering logic (such as render()).

## Args:
None

## Returns:
str
    - Always returns the literal string "Duplicate".
    - No other values are produced by this method.

## Raises:
None
    - This method does not raise exceptions.

## State Changes:
Attributes READ:
    - None. The method does not access or depend on any self attributes.

Attributes WRITTEN:
    - None. The method does not modify self or any of its attributes.

## Constraints:
Preconditions:
    - None. The method can be called on any instantiated Duplicate object.

Postconditions:
    - No change to the object's state.
    - Caller receives the string "Duplicate".

## Side Effects:
    - None. The method performs no I/O, does not call external services, and does not mutate objects outside self.

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.render` · *method*

## Summary:
Placeholder for converting the stored duplicate pandas.DataFrame into a presentation-specific representation. The current implementation is abstract and raises NotImplementedError.

## Description:
This instance method is intended to produce a rendered/presentation form of the duplicate data held by the object. The provided implementation is intentionally unimplemented — it raises NotImplementedError to force concrete subclasses or callers to provide a rendering implementation.

Known facts from the code:
- Duplicate.__init__ accepts duplicate: pandas.DataFrame and stores it in the instance content under the key "duplicate".
- This render method has no parameters and its body raises NotImplementedError.

Why this logic is a separate method:
- The method is abstract in this class so that different presentation implementations (HTML, JSON, UI widget, etc.) can supply their own conversion logic without changing the data-holder's construction.

## Args:
    None

## Returns:
    Any: The method's intended return type is unconstrained by this implementation and is implementation-dependent (for example, str, dict, or framework-specific UI objects). In the current source this method does not return because it raises NotImplementedError.

## Raises:
    NotImplementedError: Always raised by this implementation. This indicates the method is abstract and must be overridden before use.

## State Changes:
Attributes READ:
    - None by the current implementation (it immediately raises). 
    - NOTE for implementers: a concrete implementation will typically read self.content["duplicate"] (set by Duplicate.__init__) to produce the rendered output.

Attributes WRITTEN:
    - None. The current implementation performs no mutations.

## Constraints:
Preconditions:
    - The object must have been constructed using Duplicate.__init__, which requires duplicate to be a pandas.DataFrame; that DataFrame is available at self.content["duplicate"].
    - Do not call this base method directly in production code; it will raise NotImplementedError.

Postconditions:
    - As implemented: the call raises NotImplementedError and leaves object state unchanged.
    - For a proper override: the method should return a presentation result (type depending on the renderer contract) and should not be relied upon to mutate self.content unless explicitly specified by that override.

## Side Effects:
    - None in this implementation (no I/O, no external calls, no external mutations).
    - Concrete implementations may perform side effects (e.g., file I/O, network calls, or DOM/widget creation); such side effects must be documented on the overriding implementation.

