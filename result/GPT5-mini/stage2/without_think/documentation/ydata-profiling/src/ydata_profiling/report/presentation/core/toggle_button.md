# `toggle_button.py`

## `src.ydata_profiling.report.presentation.core.toggle_button.ToggleButton` · *class*

## Summary:
Represents a small presentation item that encapsulates a labeled toggle control payload. ToggleButton is a concrete class wrapper around ItemRenderer that sets the semantic item_type to "toggle_button" and stores a single content key "text". It delegates actual rendering to subclasses or callers (render() is intentionally not implemented).

## Description:
ToggleButton is intended for use anywhere the presentation layer needs a standardized "toggle" item: a UI control or a fragment that toggles visibility of content (for example, "Show details" / "Hide details" controls in a report). It centralizes the item_type ("toggle_button") and the primary payload key ("text") so higher-level presentation code can treat toggle items uniformly.

Typical creation points:
- Presentation factories and report builders that assemble lists of ItemRenderer instances.
- Higher-level render orchestration code that needs a semantic toggle item and will either:
  - subclass ToggleButton and implement render(), or
  - wrap/convert a ToggleButton instance into a concrete renderer before actual output generation.

Motivation and responsibility boundary:
- Responsibility: supply a consistent semantic identifier ("toggle_button") and content payload {"text": <label>} for toggle items.
- Boundary: ToggleButton does not implement rendering logic. It is a thin, typed container that relies on subclasses or external renderers to produce the final representation (HTML, JSON, or other).

## State:
Attributes (inherited and introduced/initialized by ToggleButton)

- item_type: str
  - Value after initialization: the literal string "toggle_button".
  - Invariant: remains "toggle_button" for the lifetime of the instance.

- content: dict
  - Value after initialization: a dict containing at minimum the key "text" with the value passed to __init__ (i.e., {"text": text}).
  - Expected shape: {"text": <str>} is the intended usage; ItemRenderer/Renderable may additionally populate content["name"], content["anchor_id"], and content["classes"] if corresponding kwargs are provided.
  - Invariant: self.content is the exact dict object created in __init__ and assigned by the ItemRenderer initialization chain.

- text (implicit): str
  - There is no attribute named text on the instance; instead the label value is stored at content["text"]. Callers should read/write that key on the content dict.

- name, anchor_id, classes (optional, inherited via Renderable/ItemRenderer)
  - May be available at content["name"], content["anchor_id"], content["classes"] if provided via kwargs during construction.
  - Accessing these via inherited property accessors (if used) may raise KeyError when absent.

Notes on mutability and constraints:
- ToggleButton does not validate the type of text at runtime; the annotation is text: str but no enforcement occurs in ToggleButton itself—callers should provide a string.
- Because content is a live dict reference, external code that holds the same dict may observe mutations.

## Lifecycle:
Creation:
- Constructor signature: __init__(text: str, **kwargs)
  - text (str): label or caption for the toggle; stored as content["text"].
  - **kwargs: forwarded to ItemRenderer / Renderable. Typical kwargs include:
    - name (Optional[str]) — friendly name stored at content["name"]
    - anchor_id (Optional[str]) — anchor id stored at content["anchor_id"]
    - classes (Optional[str]) — css/classes stored at content["classes"]
  - Example instantiation: tb = ToggleButton("Show details")

Usage:
1. Instantiate with the desired label: ToggleButton("My label", name="toggle-1")
2. Inspect metadata or payload:
   - tb.item_type == "toggle_button"
   - tb.content -> {"text": "My label"} plus optional keys added by Renderable
3. Prepare for rendering:
   - Either subclass ToggleButton and override render() to return the final representation, or pass the instance to renderer code that knows how to transform item_type + content into output.
4. Call render() on the concrete renderer. For ToggleButton itself, calling render() will raise NotImplementedError (see Raises).

Destruction / cleanup:
- ToggleButton does not manage external resources and provides no cleanup methods or context manager protocol. If a subclass allocates resources, that subclass must implement cleanup.

## Method Map:
graph LR
  Init[ToggleButton.__init__(text, **kwargs)] --> SuperInit[ItemRenderer.__init__("toggle_button", {"text": text}, **kwargs)]
  SuperInit --> ContentSet[self.content contains {"text": text}]
  Instance[ToggleButton instance] --> Repr[__repr__() -> "ToggleButton"]
  Instance --> RenderCall[render() -> raises NotImplementedError unless overridden]
  Note[Typical usage: subclass or external renderer provides concrete render implementation] --> RenderCall

(Interpretation: construction delegates to ItemRenderer/Renderable which assigns content; after creation callers inspect fields and rely on a concrete render implementation either by subclassing or external handling.)

## Raises:
- __init__:
  - ToggleButton.__init__ does not explicitly raise exceptions. However, misuse of **kwargs that are not accepted by ItemRenderer/Renderable may result in a TypeError arising from the superclass constructor.
  - If you pass a non-dict-like object where Renderable expects a dict via subclassing or modification, downstream operations may raise TypeError or AttributeError (these are not raised by ToggleButton itself).

- render:
  - Calling ToggleButton.render() will raise NotImplementedError. This is intentional to signal that ToggleButton does not provide a concrete rendering and must be subclassed or otherwise converted before being used in output generation.

- __repr__:
  - No exceptions are expected; __repr__ returns the literal string "ToggleButton".

## Example:
1) Create a ToggleButton instance:
   tb = ToggleButton("Show details")

   After creation:
   - tb.item_type == "toggle_button"
   - tb.content == {"text": "Show details"}
   - repr(tb) -> "ToggleButton"

2) Attempting to render without implementing render():
   - tb.render()  # raises NotImplementedError

3) Typical integration pattern (described, not code-defining):
   - Provide a concrete renderer that accepts ItemRenderer instances (or specifically item_type "toggle_button") and produces the final output. Alternatively, define a subclass that overrides render() to produce the desired representation (HTML fragment, JSON block, etc.). The overriding render() should read content["text"] for its label and may consult content["name"], content["anchor_id"], or content["classes"] if provided.

4) Example of safe inspection prior to rendering:
   - if "text" in tb.content:
         label = tb.content["text"]
     else:
         handle_missing_label()

Best practices:
- Pass a fresh dict for content via other ItemRenderer subclasses if you want to avoid external mutation, but ToggleButton itself constructs its own content dict so callers need not provide it.
- Always implement or supply a concrete render path before integrating ToggleButton instances into final rendering steps.

### `src.ydata_profiling.report.presentation.core.toggle_button.ToggleButton.__init__` · *method*

## Summary:
Initializes a ToggleButton presentation item by setting its semantic type to "toggle_button" and creating the content payload containing the provided text; updates the instance state via the parent ItemRenderer initializer.

## Description:
This constructor is called when a concrete ToggleButton instance is created by presentation factories, report builders, or other report construction code as part of the presentation assembly phase (i.e., when individual UI/presentation items are instantiated before rendering). Typical callers build a list of ItemRenderer subclasses (tables, text blocks, toggle buttons, etc.) and instantiate this class to represent a toggleable UI element with a label.

The logic is in its own constructor to centralize the semantic item_type ("toggle_button") and to enforce a consistent content payload shape (a dict containing the "text" key) so downstream renderers and templates can rely on that contract. It delegates shared metadata handling (name, anchor_id, classes) and storage semantics to ItemRenderer / Renderable by forwarding kwargs rather than duplicating that logic.

## Args:
    text (str): The label or visible text for the toggle button. Expected to be a string; the code does not enforce non-emptiness but downstream renderers typically expect a human-readable label.
    **kwargs: Forwarded to ItemRenderer / Renderable. Known/expected keyword arguments include:
        name (Optional[str]): Optional friendly name to be stored on the content dict as "name".
        anchor_id (Optional[str]): Optional anchor identifier stored as "anchor_id".
        classes (Optional[str]): Optional CSS classes or similar stored as "classes".
    The constructor will forward any provided kwargs to the superclass; unknown kwargs with no matching parameter on the parent will raise a TypeError from the parent call.

## Returns:
    None: As a constructor, it returns the newly-initialized instance. There is no explicit return value.

## Raises:
    TypeError: If the forwarded kwargs include unexpected keyword arguments that the parent initializer does not accept.
    (No exceptions are explicitly raised by this method itself. Indirect errors may occur in the parent initializer if unexpected types are provided.)

## State Changes:
Attributes READ:
    - (none) The constructor does not read any pre-existing self.<attr> fields.

Attributes WRITTEN:
    - self.item_type: set to the literal string "toggle_button" by ItemRenderer.__init__.
    - self.content: set to a newly-created dict {"text": text} by passing it to ItemRenderer.__init__; Renderable.__init__ (invoked by the parent) stores the dict reference on self.content.
    - content keys "name", "anchor_id", "classes": may be inserted into self.content by Renderable.__init__ when the corresponding kwargs are provided.

## Constraints:
Preconditions:
    - The caller should provide a text value that is meaningful for display (recommended: non-empty str). The code only has a type annotation; no runtime type enforcement occurs here.
    - If callers pass kwargs, they must match the parameters accepted by ItemRenderer / Renderable (commonly name, anchor_id, classes) to avoid a TypeError.

Postconditions:
    - After initialization, self.item_type == "toggle_button".
    - After initialization, self.content is a dict and contains at least the key "text" mapping to the provided text value.
    - If name, anchor_id, or classes were provided via kwargs, those keys will exist in self.content with the provided values.
    - The content dict stored on self.content is the same dict object created here (i.e., callers should be aware of mutability if they hold a reference).

## Side Effects:
    - Calls ItemRenderer.__init__ (and transitively Renderable.__init__), which stores the provided content dict on the instance and may mutate that dict by inserting metadata keys ("name", "anchor_id", "classes") if corresponding kwargs are provided.
    - No I/O, network access, or other external interactions occur.
    - Because the code creates a new dict for content, it does not mutate external objects passed by the caller.

### `src.ydata_profiling.report.presentation.core.toggle_button.ToggleButton.__repr__` · *method*

## Summary:
Returns a concise, constant textual representation identifying the object as a ToggleButton for debugging and display purposes.

## Description:
This method provides the canonical representation used by Python's built-in repr() to identify the object. Typical callers include:
- The built-in repr(obj) and interactive REPL inspection when an instance is printed or logged.
- Logging or debugging utilities that call repr() to show object identity.
- Any code that explicitly calls instance.__repr__() to obtain a stable identifier.

Within the report rendering system, this method is kept separate from render() and other display logic so that:
- It offers a stable, lightweight identifier suitable for logs and developer-facing messages.
- It remains independent from the object's rendering/state serialization logic (render() handles output generation and may be complex or raise NotImplementedError).

Keeping this as its own method ensures a predictable, side-effect-free identity string regardless of object state.

## Args:
This method takes no arguments beyond self.

## Returns:
str: Always returns the constant string "ToggleButton". There are no runtime variations or alternate values.

## Raises:
This method does not raise any exceptions.

## State Changes:
Attributes READ:
- None. This implementation does not access any self.<attr> fields.

Attributes WRITTEN:
- None. This method does not modify object state.

## Constraints:
Preconditions:
- The instance should be a properly constructed ToggleButton object (i.e., __init__ has been executed). No other conditions are required.

Postconditions:
- The method returns the constant string "ToggleButton".
- No attributes of self or external state are modified.

## Side Effects:
- None. The method performs no I/O, external calls, or mutations outside the instance.

### `src.ydata_profiling.report.presentation.core.toggle_button.ToggleButton.render` · *method*

## Summary:
Defines an abstract contract for producing the toggle button's presentation output; the base implementation raises NotImplementedError and does not modify the object's state. Concrete subclasses must override this method to produce the final representation (e.g., HTML string, JSON fragment, or widget) using the instance payload.

## Description:
- Known callers and lifecycle context:
    - Typical callers are presentation factories, report builders, and render orchestration code that construct ItemRenderer instances during report assembly and call render() during the final rendering phase to produce output fragments included in the report.
    - Lifecycle example: construct ToggleButton (during report building) -> store it in a collection of renderables -> orchestrator iterates renderables and calls render() on each to assemble the final report output.
- Rationale for being a separate method:
    - Polymorphism and separation of concerns: different presentation targets require different rendering logic, so render() is an overridable method implemented by concrete ToggleButton subclasses. The constructor fixes the semantic item_type and payload; render() converts that payload into the presentation artifact.

## Args:
    None (instance method; only self).

## Returns:
    Any
    - Base implementation: does not return; it raises NotImplementedError.
    - Concrete implementations: should return the final presentation artifact. Typical return types:
        - str: HTML fragment for HTML reports.
        - dict: JSON-serializable representation for JSON or API outputs.
        - Framework-specific widget/object used by the presentation framework.
    - Edge-case behavior:
        - An implementation may intentionally return None to indicate "no output"; callers should handle or filter None if that is allowed by the surrounding orchestration.

## Raises:
    NotImplementedError
    - Exact condition: always raised by this base method implementation (calling ToggleButton.render() when not overridden).
    - Implementations may also raise:
        - KeyError: if they access self.content["text"] but the key is missing (note: ToggleButton.__init__ initially sets content["text"], but content is mutable).
        - ValueError/TypeError: if they validate and reject invalid payload values or types.

## State Changes:
- Base method behavior:
    - Attributes READ: none (the base method raises immediately and performs no reads).
    - Attributes WRITTEN: none.
- Expectations for concrete implementations (explicitly separated from base behavior):
    - Typical reads:
        - self.content (a dict) — specifically, implementations are expected to read self.content["text"] as the toggle label because ToggleButton.__init__ initializes the payload with that key.
        - Optionally self.content.get("name"), self.content.get("anchor_id"), self.content.get("classes") if metadata is needed.
        - self.item_type if renderer selection or payload tagging is required.
    - Typical writes:
        - Implementations should avoid mutating self.content unless such mutation is intentional and documented. Any mutation is visible to other code because ItemRenderer retains the same dict reference.

## Constraints:
- Preconditions:
    - The instance should have been constructed via ToggleButton.__init__, which sets:
        - self.item_type == "toggle_button"
        - self.content is a dict containing the key "text" with the constructor-provided label.
    - Do not call this base method on ToggleButton instances unless you expect a NotImplementedError.
- Postconditions:
    - Base method: raises NotImplementedError; no state change.
    - Concrete implementation: should return the presentation artifact (unless None is a documented, intentional outcome) and should not perform undocumented mutations to unrelated instance state.

## Side Effects:
- Base method: none.
- Possible side effects for concrete implementations (must be documented by implementers if present):
    - Mutating self.content (shared mutable dict).
    - I/O or resource registration (e.g., writing files, registering CSS/JS assets, network calls) — generally discouraged inside render() unless the surrounding system expects it.
    - Emitting or registering assets into global registries used by the report generator.

## Implementation guidance (for implementers):
1. Override render() in the subclass; do not call super().render() (it raises).
2. Read the toggle label from label = self.content["text"]. Validate type/emptiness if required and raise ValueError/TypeError with a clear message on invalid input.
3. Choose a return type consistent with the rest of the presentation layer (prefer str for HTML pipelines).
4. Avoid mutating self.content unless the mutation is part of the documented contract.
5. Document any side effects (I/O, registry mutations) and exceptions that may be raised so callers can handle them.

