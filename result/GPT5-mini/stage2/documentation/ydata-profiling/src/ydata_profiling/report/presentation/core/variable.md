# `variable.py`

## `src.ydata_profiling.report.presentation.core.variable.Variable` · *class*

## Summary:
Represents a presentation "variable" item that holds a top and optional bottom Renderable payload plus an ignore flag; it is a typed ItemRenderer wrapper that delegates actual rendering to subclasses or concrete implementations.

## Description:
Variable is a small, semantic wrapper used in the presentation/reporting layer to group two nested renderable elements (a mandatory top element and an optional bottom element) together under the item_type "variable". Typical uses:
- Created by presentation factories or report builders that assemble complex UI/report fragments composed of nested Renderable items.
- Used when a logical report "variable" consists of two sub-components (primary/top view and an optional secondary/bottom view) where both sub-components themselves implement the Renderable protocol.

Motivation and responsibility boundary:
- Encapsulates the tuple (top, bottom, ignore) in the standardized ItemRenderer/Renderable content dictionary so presentation orchestration code can treat a variable item uniformly (inspect metadata, call render, convert nested literals to renderable classes).
- Does not implement rendering itself (render raises NotImplementedError). Concrete subclasses or runtime-converted instances must implement render() to produce the final output format (HTML, JSON fragment, widget, etc.).
- Enforces the presence of the semantic item_type "variable" and a consistent content structure for downstream code.

Known callers/factories:
- Presentation factories that build report variable blocks.
- Report builders that compose multiple ItemRenderer instances into sections.
- Conversion utilities that call Variable.convert_to_class to convert plain objects into Variable instances and then convert nested content via the provided flv callable.

## State:
Instance attributes (stored inside self.content dictionary; no separate attributes are set by Variable itself):

- content (dict) — inherited from Renderable via ItemRenderer.
  - Keys injected by Variable.__init__:
    - "top": Renderable
      - Type: Renderable (annotation). Semantically required: the primary renderable element for the variable.
      - Constraint: callers should pass a Renderable-like object; Variable does not validate at runtime. Must not be None.
      - Invariant: present in content after __init__ with the value passed by the caller.
    - "bottom": Optional[Renderable]
      - Type: Renderable or None.
      - Constraint: optional; may be None if no secondary view is required.
      - Invariant: present in content after __init__ (value may be None).
    - "ignore": bool
      - Type: bool
      - Default: False (if not explicitly provided, Variable.__init__ sets False by default).
      - Semantic use: hint to report logic that this variable should be ignored/omitted in certain processing steps.
  - Additional keys inherited from Renderable (may be set via kwargs passed through __init__):
    - "name": str (optional)
    - "anchor_id": str (optional)
    - "classes": str (optional)

Other implicit properties (from ItemRenderer / Renderable):
- item_type: str
  - Value: "variable" (set by the constructor call to ItemRenderer).
  - Invariant: remains the semantic type for the instance.

Class invariants:
- self.content is a dictionary-like mapping for the instance lifetime.
- After construction, keys "top", "bottom", and "ignore" exist in content (even if bottom is None).
- The instance expects that content["top"] (the top element) is a Renderable or a compatible object; many helpers (e.g., convert_to_class) assume nested renderables exist and will attempt to process them.

## Lifecycle:
Creation:
- Constructor signature:
  - top: Renderable (required) — primary nested Renderable item.
  - bottom: Optional[Renderable] = None — optional secondary nested Renderable.
  - ignore: bool = False — flag with semantic meaning for downstream logic.
  - **kwargs: optional keyword arguments forwarded to ItemRenderer/Renderable (commonly name, anchor_id, classes).
- How it initializes:
  - Calls ItemRenderer.__init__("variable", {"top": top, "bottom": bottom, "ignore": ignore}, **kwargs).
  - As a result, self.item_type == "variable" and self.content is the exact dict literal passed (the dictionary is created by Variable.__init__ and retained by Renderable).

Usage:
- Typical sequence:
  1. Instantiate: provide a top renderable and optionally a bottom renderable and metadata kwargs.
  2. Optionally inspect metadata or nested content via instance.content (or the inherited properties if name/anchor_id/classes were provided).
  3. Convert nested literal objects to concrete renderable classes if necessary by calling Variable.convert_to_class on an object that contains the corresponding content dict (often done by factory code).
  4. Call render() on a concrete Variable subclass or on a Variable instance that has had render implemented/attached. Note: Variable.render() raises NotImplementedError — calling it on this base class will raise.
- Required sequencing:
  - No strict ordering is enforced by the class, but calling render() should only be done on instances where a concrete implementation is available (subclass or runtime-modified class). If convert_to_class is used to convert nested elements, it should generally be run before render so nested items are ready.

Destruction / cleanup:
- Variable does not manage external resources and provides no cleanup or context-manager protocol.
- If nested top/bottom renderables allocate resources, their cleanup is the responsibility of those concrete classes; Variable does not call close() or similar automatically.

## Method Map:
graph LR
  U[Caller] --> InitCall[Variable.__init__(top, bottom=None, ignore=False, **kwargs)]
  InitCall --> ItemRendererInit[ItemRenderer.__init__("variable", content_dict, **kwargs)]
  ItemRendererInit --> RenderableInit[Renderable.__init__(content_dict, name?, anchor_id?, classes?)]
  RenderableInit --> InstanceReady[Variable instance with content keys: top,bottom,ignore]
  InstanceReady --> StrCall[__str__() -> formatted multiline description using top/bottom string representations]
  InstanceReady --> ReprCall[__repr__() -> "Variable"]
  InstanceReady --> RenderCall[render() -> raises NotImplementedError unless subclass overrides]
  InstanceReady --> ConvertClassCall[Variable.convert_to_class(obj, flv)]
  ConvertClassCall --> MutateClass[obj.__class__ = Variable (or subclass)]
  MutateClass --> FVIP[if content.top is not None -> flv(content.top)]
  MutateClass --> FVBOT[if content.bottom is not None -> flv(content.bottom)]

(Interpretation: __init__ delegates to ItemRenderer/Renderable chain. convert_to_class mutates runtime class and applies flv to nested entries if present. render is abstract and must be implemented by concrete types.)

## Methods (behavior summary):
- __init__(top, bottom=None, ignore=False, **kwargs)
  - Behavior: constructs content dict {"top": top, "bottom": bottom, "ignore": ignore} and passes it to ItemRenderer with item_type "variable" and any metadata kwargs.
  - Notes: does not validate types of top/bottom beyond the type hints.

- __str__():
  - Returns a short multiline textual description starting with "Variable\n", followed by "- top: <str(top)>" and "- bottom: <str(bottom)>". Newlines inside the str() of nested elements are indented with a tab.
  - Helpful for debugging/logging of the nested structure.

- __repr__():
  - Returns the literal string "Variable".

- render() -> Any
  - In this class, raises NotImplementedError.
  - Contract: concrete subclasses must implement render() to produce the presentation output (HTML, JSON, visualization spec, etc.).

- convert_to_class(cls, obj: Renderable, flv: Callable) -> None  (classmethod)
  - Behavior:
    - Sets obj.__class__ = cls (mutates the runtime class of the given obj).
    - If obj.content contains a non-None "top" value, calls flv(obj.content["top"]).
    - If obj.content contains a non-None "bottom" value, calls flv(obj.content["bottom"]).
  - Purpose: used when converting a previously-built plain object into a Variable instance (or subclass) at runtime and recursively ensuring nested items are also converted/processed by the provided flv callable.
  - Caller contract:
    - flv must be a callable that accepts a nested content object and performs whatever conversion is necessary (commonly, flv will be a function that sets the nested object's class or otherwise prepares it as a Renderable).
  - Caution:
    - Assigning to obj.__class__ can raise Python TypeError if the new class has an incompatible layout (this is a Python-level constraint).
    - flv may raise any exception depending on its implementation; convert_to_class does not catch exceptions.

## Raises:
- __init__:
  - No explicit exceptions raised by Variable.__init__ itself. Because it constructs a dict and forwards kwargs to ItemRenderer/Renderable, typical runtime exceptions are unlikely here.
  - Indirect/runtime errors:
    - TypeError/AttributeError if kwargs cause Renderable.__init__ to write into a content mapping that does not support item assignment (not applicable here because Variable creates the content dict itself).
    - If callers violate assumed contracts (e.g., mutate content to non-mapping later), subsequent operations may raise.

- render():
  - Always raises NotImplementedError in this base class. Calling render() on Variable without a concrete implementation is an error.

- convert_to_class():
  - May raise TypeError when assigning obj.__class__ = cls if Python deems the assignment incompatible with the object's layout.
  - flv(obj.content["..."]) calls may raise whatever exceptions flv can raise (TypeError, ValueError, etc.); these are propagated.

## Example:
(Assume SomeRenderable is a concrete class implementing Renderable.render.)

1) Construct top and optional bottom renderables:
   top = SomeRenderable(content_top)
   bottom = SomeRenderable(content_bottom)

2) Create a Variable instance:
   var = Variable(top=top, bottom=bottom, ignore=False, name="age", anchor_id="var-age")

3) Inspect nested content or metadata:
   # Access direct content dict (safe): top_item = var.content["top"]
   # Read metadata set via kwargs:
   display_name = var.content.get("name")    # or var.content["name"] if present

4) Convert a plain object into a Variable at runtime (advanced usage):
   # obj is an object with a content dict that mirrors Variable's structure
   Variable.convert_to_class(obj, flv=lambda nested: SomeRenderable.convert_to_class(nested, lambda x: x))

5) Rendering (requires a concrete implementation):
   # If using a subclass that implements render:
   output = var.render()   # Only valid if var is an instance of a concrete subclass that overrides render(); otherwise this call raises NotImplementedError.

Notes:
- Because Variable does not implement render(), it is effectively an abstract grouping type; use a subclass or runtime conversion to a concrete class before attempting to render.
- Use convert_to_class only when you control the object shapes and the provided flv callable is prepared to convert nested items; conversion mutates obj.__class__ and nested structure in place.

### `src.ydata_profiling.report.presentation.core.variable.Variable.__init__` · *method*

## Summary:
Initializes the Variable instance by storing the provided top and optional bottom Renderable plus an ignore flag inside the instance content mapping and setting the semantic item_type to "variable". The call arranges instance state but does not perform rendering or validate nested renderables.

## Description:
- Known callers and lifecycle stage:
    - Presentation factories and report builders that assemble report fragments call this constructor when creating a "variable" presentation item composed of two nested renderables (primary/top and optional secondary/bottom). 
    - Typically invoked during the report assembly phase before any conversion of nested literals to concrete renderable classes and before calling render() on the instance.
- Why this logic is a separate method:
    - The constructor encapsulates the specific content layout required for the "variable" semantic type (the keys "top", "bottom", "ignore") and delegates common storage/metadata handling to the ItemRenderer/Renderable base classes. Separating this logic keeps the content schema centralized and allows presentation orchestration code to rely on a consistent item_type and content shape for downstream processing.

## Args:
    top (Renderable): Required. The primary nested renderable for this variable. Semantically expected to be an object implementing the Renderable protocol. The constructor does not perform runtime type validation; callers should supply a compatible object and should not pass None unless intentionally leaving the slot empty (not recommended).
    bottom (Optional[Renderable], optional): Secondary nested renderable or None. Defaults to None. If provided, it should be a Renderable-like object; no runtime checks are performed here.
    ignore (bool, optional): Flag indicating whether this variable should be ignored by certain downstream processing steps. Defaults to False.
    **kwargs: Additional keyword arguments forwarded to the ItemRenderer / Renderable constructor (commonly metadata such as name, anchor_id, classes). These are passed through unchanged.

## Returns:
    None — the constructor returns None by Python convention. Its observable effect is to initialize instance state (self.item_type and self.content).

## Raises:
    - This __init__ implementation does not explicitly raise. However, errors raised by super().__init__ (ItemRenderer/Renderable constructors) may propagate. Examples include:
        - TypeError or AttributeError if the forwarded kwargs or the base constructors attempt invalid operations on the provided content mapping (not expected here because a dict is created locally).
        - Any exception raised by ItemRenderer/Renderable.__init__ for unusual inputs will propagate unchanged.

## State Changes:
- Attributes READ:
    - None from self (this method does not inspect existing instance attributes).
- Attributes WRITTEN:
    - self.content: assigned indirectly via the base class constructors to the dict created here: {"top": top, "bottom": bottom, "ignore": ignore}. After return, this dict is the instance's authoritative content mapping.
    - self.item_type: assigned by ItemRenderer.__init__ to the literal "variable".
    - Additionally, Renderable.__init__ may write the metadata keys "name", "anchor_id", and "classes" into self.content if corresponding kwargs were supplied; these are also written during construction.

## Constraints:
- Preconditions:
    - Callers should provide a meaningful Renderable for top (and bottom when used). The code does not enforce non-None or type checks; providing incompatible types or None may lead to errors in later processing (e.g., when convert_to_class or render is invoked).
    - The instance is expected to be used (rendered or converted) only after nested renderables are prepared as needed by the application (for example, after any required convert_to_class steps).
- Postconditions:
    - After __init__ completes:
        - self.item_type == "variable"
        - self.content is a dict containing the keys "top", "bottom", and "ignore" with the exact values passed in (bottom may be None, ignore will be the provided bool).
        - If kwargs included name/anchor_id/classes, those keys will also exist in self.content (written by Renderable.__init__).

## Side Effects:
    - No I/O or external service calls.
    - Mutates the new instance's class-level state by initializing self.item_type and self.content via the base-class constructors.
    - Does not mutate objects passed in as top/bottom beyond storing their references in the content dict.
    - No global state is changed; no files/sockets/databases are touched.

### `src.ydata_profiling.report.presentation.core.variable.Variable.__str__` · *method*

## Summary:
Return a human-readable string representation of the Variable by converting its "top" and "bottom" Renderable contents to strings and embedding them with simple indentation; does not modify the object.

## Description:
This method is invoked when the Variable instance is converted to a string (for example via str(variable_instance), print(variable_instance), or when included in logging or debugging output). It exists as a dedicated method to produce a concise textual summary of the nested Renderable content, applying a small normalization step to keep multi-line content visually indented and readable.

The method:
- Calls str() on self.content["top"] and self.content["bottom"] to obtain their textual representations.
- Replaces every newline character in those textual representations with a newline followed by a tab character ('\n' -> '\n\t') so that multi-line content appears indented in the combined output.
- Constructs and returns a short block starting with "Variable\n" followed by "- top: {top_text}" and "- bottom: {bottom_text}".

Keeping this formatting logic in its own method centralizes how Variable objects are presented as text, ensuring consistent indentation and layout across debugging and logging use cases.

## Args:
This method takes no arguments.

## Returns:
str: A single string with the following structure:
    Variable
    - top: {top_text}- bottom: {bottom_text}
Where:
- {top_text} is str(self.content["top"]) with every '\n' replaced by '\n\t'.
- {bottom_text} is str(self.content["bottom"]) with every '\n' replaced by '\n\t'.
Notes:
- If either content value is None, str(None) yields the literal "None" and that string is used.
- There is no automatic newline inserted between the "- top: ..." and "- bottom: ..." segments by this method; they are concatenated directly.

## Raises:
- KeyError: If self.content does not contain the keys "top" or "bottom", a KeyError will be raised when attempting to access them.
- Any exception raised by calling str() on the contained objects will propagate (for example, if an object's __str__ raises).

## State Changes:
Attributes READ:
- self.content (specifically self.content["top"] and self.content["bottom"])

Attributes WRITTEN:
- None. This method does not modify self or any of its attributes.

## Constraints:
Preconditions:
- self.content must be a mapping (dict-like) containing the keys "top" and "bottom" (these are set by the class __init__ in normal construction).
- The values stored under these keys should be convertible to strings (they may be None; str(None) is acceptable).

Postconditions:
- The method does not mutate self or its contents.
- It returns a deterministic string given the current values of self.content["top"] and self.content["bottom"] (subject to those objects' own __str__ behavior).

## Side Effects:
- None related to I/O or external services.
- No external objects are mutated by this method; it only reads content and returns a constructed string.

### `src.ydata_profiling.report.presentation.core.variable.Variable.__repr__` · *method*

## Summary:
Return a constant textual representation for the object: the literal string "Variable".

## Description:
Implements the class's __repr__ special method by unconditionally returning a constant string. The implementation contains no branching or use of instance state.

## Args:
None.

## Returns:
str: Always returns the exact string "Variable". There are no alternative return values.

## Raises:
None. The method body does not raise any exceptions.

## State Changes:
Attributes READ:
- None.

Attributes WRITTEN:
- None.

## Constraints:
Preconditions:
- None required; can be called on any instance of the class.

Postconditions:
- The object's state is unchanged.
- The caller receives the string "Variable".

## Side Effects:
- None (no I/O, no external calls, no mutation of self or other objects).

## Example:
- If instance is an instance of this class, then repr(instance) evaluates to "Variable".

### `src.ydata_profiling.report.presentation.core.variable.Variable.render` · *method*

## Summary:
Defines the rendering contract for a variable presentation item; it does not implement rendering itself and raises NotImplementedError in the base Variable class. Implementations should produce a presentation fragment (HTML/JSON/spec/object) that represents the variable by rendering its child Renderable parts (top and optional bottom) and respecting the ignore flag in the content.

## Description:
This method is the rendering entry point invoked by the presentation/report pipeline when producing the final report output for a variable item. Typical callers and lifecycle stage:
- Presentation factories, report builders, or render orchestration code call this method while composing the final output (for example, iterating the presentation tree and calling render() on each node).
- The method is invoked during the "render" stage of report generation after the presentation objects (Variable instances) have been created/populated.

Why this is a distinct method:
- Rendering a variable is a distinct responsibility that combines rendering of nested sub-items (the "top" and optional "bottom") and may apply variable-specific layout/formatting. Keeping it as a dedicated method isolates presentation composition logic from construction and metadata management and allows different output formats (HTML, JSON, widget specs) to provide their own implementations without altering the Variable data model.

Implementation contract for subclasses (what an implementer must do):
- Read the nested Renderable children stored in self.content under "top" and "bottom".
- If a nested child is present, call that child's render() and incorporate its result into the variable's final representation.
- Respect the "ignore" flag in self.content: if content["ignore"] is truthy, implementations should short-circuit rendering (e.g., return a neutral/empty fragment) or otherwise omit the visual representation, consistent with the surrounding pipeline's expectations.
- Do not mutate unrelated attributes on the Variable instance (implementations should avoid changing self.item_type or replacing self.content). Mutating nested content in place is allowed only if intentionally part of the rendering logic.
- Propagate or translate exceptions raised by nested render() calls as appropriate for the output format (implementer choice), but document any translation behavior in the concrete subclass.

## Args:
This method takes no explicit arguments.

Implicit inputs (read from instance state):
- self.content (dict-like) — required keys used by implementations:
    - "top" (Renderable): required for a meaningful variable rendering (implementations must handle the case where it is absent or None).
    - "bottom" (Optional[Renderable]): may be None or absent; implementations must handle both.
    - "ignore" (bool): when present and True, implementations should skip or short-circuit rendering.

Expected types:
- content["top"]: Renderable (or an object that implements .render())
- content["bottom"]: Optional[Renderable]
- content["ignore"]: bool (if absent, treat as False)

## Returns:
- type: Any
- semantics:
    - The return value is the concrete presentation fragment produced by the implementation (examples: an HTML string, a JSON/dict fragment, a visualization spec object, or a framework-specific widget).
    - If ignore is True, implementations may return a neutral/empty fragment (for example: None, an empty string, or an empty dict) — the precise neutral value is format-specific and must be documented by the concrete subclass.
    - If top is missing or None, implementations must decide on a sensible fallback (examples: return a placeholder fragment, raise an error, or return None); the chosen fallback must be documented by the subclass.

Edge-case return values:
- None: commonly used to indicate "nothing to render", especially when ignore is True.
- Empty container (e.g., "", {}, []): may be used where the pipeline expects a container fragment rather than None.
- An error/exception: implementations may raise if required content is missing and the implementation treats that as a fatal condition.

## Raises:
- NotImplementedError: the base Variable.render raises NotImplementedError unconditionally (so calling Variable.render on instances that did not override it will raise).
- KeyError: concrete implementations may raise KeyError if they assume required keys ("top") exist but they are absent from self.content; callers should guard if uncertain.
- Any exceptions raised by nested Renderable.render() calls are not suppressed by the base class; concrete implementations may propagate or translate them.

## State Changes:
Attributes READ:
- self.content (reads specific keys)
    - self.content["top"] — inspected and, if not None, its render() is invoked.
    - self.content["bottom"] — inspected and, if not None, its render() is invoked.
    - self.content.get("ignore") — inspected to decide whether to short-circuit rendering.
- (Indirect) nested Renderable instances' internal state may be read/used when their render() is called.

Attributes WRITTEN:
- None required by the contract. Implementations should not modify:
    - self.item_type
    - self.content reference (replacing the dict)
  Implementations may mutate nested content keys deliberately (e.g., to annotate child content), but such mutations should be documented and kept minimal.

## Constraints:
Preconditions (caller / object must satisfy before calling):
- self.content must be a dict-like mapping with zero or more of the keys "top", "bottom", "ignore".
- If present, self.content["top"] and self.content["bottom"] must be Renderable-like objects that expose a callable render() method.
- The reporting pipeline expects that concrete subclasses implement render(); calling the base class implementation (which raises NotImplementedError) is invalid in production.

Postconditions (guarantees after a successful call):
- The method returns a presentation fragment of type appropriate for the concrete subclass's output format.
- The Variable instance retains the same self.content mapping and self.item_type unless the implementation documents otherwise.
- Any side effects on nested renderables are implementation-dependent and must be documented by subclasses.

## Side Effects:
- Calls nested Renderable.render() methods; those calls may themselves perform I/O or allocate resources depending on their implementations.
- No direct I/O is mandated by this contract, but concrete implementations may produce strings (which is pure computation) or may write files, fetch remote resources, or perform other I/O as required by the output format — such behavior must be documented in the concrete subclass.
- No network or filesystem I/O is performed by the base class itself (it merely raises NotImplementedError); side effects occur only in concrete implementations.

## Implementation guidance / example patterns for reimplementation:
- Minimal safe pattern (pseudologic; implementer to choose actual return type):
    1. If self.content.get("ignore") is truthy:
         return neutral_fragment
    2. top = self.content.get("top")
       if top is None:
         return fallback_fragment or raise KeyError / ValueError (document chosen behavior)
       rendered_top = top.render()
    3. bottom = self.content.get("bottom")
       rendered_bottom = bottom.render() if bottom is not None else None
    4. Combine rendered_top and rendered_bottom into the format-appropriate container and return it.

- Document the chosen neutral_fragment, fallback behavior, and combination format in the concrete subclass so callers and higher-level pipeline code can handle the results consistently.

### `src.ydata_profiling.report.presentation.core.variable.Variable.convert_to_class` · *method*

## Summary:
Change an existing object's runtime class to the provided class and, if present, invoke a conversion callback on its "top" and "bottom" nested content entries, mutating the object's identity and recursively processing those children.

## Description:
This classmethod-style utility is used during reconstruction/deserialization or factory-driven initialization of presentation trees. It performs two focused steps:
1. Assigns the provided class object to obj.__class__, changing the object's runtime type (method resolution, isinstance checks, etc.).
2. If obj.content contains a "top" entry that is not None, calls flv(obj.content["top"]); similarly, if a non-None "bottom" entry exists, calls flv(obj.content["bottom"]). The flv callable is expected to perform any in-place conversion of those nested entries (its return value is ignored).

Known callers and lifecycle stage:
- Typical callers are deserialization/factory routines and presentation reconstruction code that receive loosely-typed or generic Renderable-like objects and need to convert them into concrete renderer instances before rendering.
- This method is invoked during object reconstruction/initialization, prior to any render() calls, so that subsequent method resolution and type-specific behavior are correct.

Why this is its own method:
- Assigning a new runtime class and processing Variable-specific nested keys ("top" and "bottom") are cohesive operations tied to the Variable structure. Encapsulating them:
  - centralizes conversion logic for Variable,
  - avoids duplicating recursion at call-sites,
  - lets callers provide a conversion callback (flv) that controls how nested parts are processed.

## Args:
    cls (type):
        The target class object to assign to obj.__class__. In typical use this is the Variable class (or a Variable subclass). The function expects a class object but does not enforce type beyond Python's runtime checks.
    obj (Renderable):
        The instance whose runtime class will be changed. Must expose a content attribute that behaves like a dict-like mapping (e.g., dict) and may contain "top" and/or "bottom" keys.
    flv (Callable[[Any], Any]):
        A callable invoked for side effects on nested entries. When present and non-None, obj.content["top"] and/or obj.content["bottom"] are passed to flv. Expected signature: Callable[[Any], Any] or Callable[[Renderable], Any]. The return value of flv is ignored by this method.

## Returns:
    None
    - No value is returned. All effects are performed by in-place mutation of obj and by invoking flv on nested entries when applicable.

## Raises:
    TypeError:
        - If assigning cls to obj.__class__ is invalid because the target class has an incompatible instance layout (this is raised by the Python runtime).
        - If flv is not callable and the implementation attempts to call it, Python will raise TypeError at the call-site.
    AttributeError:
        - If obj does not have a content attribute (i.e., it is not Renderable-like), accessing obj.content will raise AttributeError.
    Any exception raised by flv:
        - Exceptions thrown by the flv callable (e.g., due to type errors inside flv) propagate unchanged to the caller.

## State Changes:
Attributes READ:
    - obj.content (always read to check for keys)
    - obj.content["top"] (read only if the "top" key exists)
    - obj.content["bottom"] (read only if the "bottom" key exists)
Attributes WRITTEN:
    - obj.__class__ is assigned to cls

## Constraints:
Preconditions:
    - obj must be an instantiated Python object exposing a content attribute that is a mutable mapping (dict-like). If content is missing or is not mapping-like, behavior will raise AttributeError or mapping-related exceptions.
    - cls must be a class object compatible with assignment to obj.__class__ (in CPython, incompatible instance layouts, __slots__ differences, or extension types may cause TypeError).
    - flv must be a callable able to accept and process the values stored under "top" and "bottom" (if present). Callers are responsible for ensuring flv can handle None or non-Renderable values if those can occur.

Postconditions:
    - On successful return, obj.__class__ is equal to the provided cls.
    - If obj.content contained a non-None "top", flv has been invoked exactly once with that value. If obj.content contained a non-None "bottom", flv has been invoked exactly once with that value. The method makes no further guarantees about modifications performed by flv.

## Side Effects:
    - Mutates obj.__class__, changing the object's runtime type and therefore method resolution, attribute access semantics, and isinstance/issubclass checks for that object.
    - Calls the provided flv callable with obj.content["top"] and/or obj.content["bottom"] when present and non-None; flv may further mutate those nested objects or raise exceptions.
    - Performs no I/O, network, or external service calls.

