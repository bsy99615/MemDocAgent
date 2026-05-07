# `root.py`

## `src.ydata_profiling.report.presentation.core.root.Root` · *class*

## Summary:
Represents the top-level "report" item in the presentation layer. Root is an ItemRenderer that holds the report's body, footer, and style metadata and defines the canonical content mapping for a report; it does not implement rendering itself.

## Description:
Root is the canonical container used to represent a complete report in the presentation layer. It centralizes the structure expected by downstream renderers/serializers by providing a consistent content mapping with the keys "body", "footer", and "style".

When to instantiate:
- Use Root when assembling a full report from component Renderable objects (the body and footer) together with a Style configuration.
- Typical callers: report builders and presentation factories that produce a final report object to be rendered or serialized.

Motivation and responsibility boundary:
- Responsibility: supply a stable, well-known structure for a report so rendering/serialization code can assume where to find the main parts.
- Boundary: Root defines content organization and metadata only; actual rendering format (HTML, JSON, UI component) is the responsibility of a concrete subclass that overrides render().

## State:
Attributes and invariants (what exists on an instance after construction):

- item_type: str
  - Value: the literal "report".
  - Set by ItemRenderer.__init__ via the call in Root.__init__.
  - Invariant: remains "report" for the instance's lifetime.

- content: dict[str, Any]
  - Created in Root.__init__ exactly as:
    {"body": body, "footer": footer, "style": style}
  - Expected member types:
    - "body": Renderable (or an object implementing the Renderable contract)
    - "footer": Renderable
    - "style": Style (from ydata_profiling.config)
  - Invariant: content is a mapping and contains "body", "footer", and "style" immediately after construction.
  - Mutability note: the same dict object is stored and shared by reference; mutations to content are visible to external holders of the dict.

- name: str (stored as content["name"])
  - The constructor requires name: str and passes it to the parent initializer; consequently, content["name"] will be set to the provided value during construction.
  - Access via the Renderable naming property will succeed (no KeyError) because the constructor always supplies name.

- anchor_id: Optional[str] (stored as content["anchor_id"] only if provided)
  - Root forwards **kwargs to the parent initializer; if an anchor_id keyword argument is supplied, Renderable.__init__ will write content["anchor_id"].
  - Not guaranteed to exist unless caller supplies it.

- classes: Optional[str] (stored as content["classes"] only if provided)
  - Same semantics as anchor_id: only present if provided via kwargs.

Class invariants:
- content remains a mapping object for the lifetime of the instance.
- content["body"], content["footer"], content["style"], and content["name"] exist immediately after __init__ returns.
- anchor_id and classes exist only if supplied by the caller via kwargs.

Representation:
- __repr__ returns "Root".

## Lifecycle:
Creation:
- Constructor signature (exact):
  - __init__(self, name: str, body: Renderable, footer: Renderable, style: Style, **kwargs)
  - name: required string; will be stored as content["name"].
  - body: required Renderable (or object compatible with Renderable contract); stored at content["body"].
  - footer: required Renderable; stored at content["footer"].
  - style: required Style; stored at content["style"].
  - **kwargs: forwarded to Renderable/ItemRenderer (common optional keys: anchor_id, classes).

Usage:
- Typical sequence:
  1. Create body and footer as concrete Renderable instances.
  2. Instantiate Root with required parameters (and optional anchor_id/classes).
  3. Optionally inspect metadata: e.g., root.content["name"], root.content.get("anchor_id").
  4. Call render() on a concrete subclass of Root (Root.render raises NotImplementedError; do not call on Root itself).
- Ordering constraints:
  - No method ordering is enforced by Root; however, rendering requires a concrete subclass.
  - If relying on convert_to_class for deserialization, ensure nested parts are converted as needed (via the flv callable) before rendering.

Destruction / Cleanup:
- Root itself manages no external resources and provides no context-manager or close behavior. Subclasses that allocate resources must implement their own cleanup.

## Method Map:
flowchart TD
    Init[Root.__init__(name, body, footer, style, **kwargs)] --> SetItemType[item_type="report" set via ItemRenderer]
    Init --> CreateContent[content set: {"body":body,"footer":footer,"style":style}]
    CreateContent --> WriteName[content["name"] = name]
    CreateContent --> Inherit[Renderable.__init__ may write anchor_id/classes if provided]
    InstanceReady[Root instance ready] --> Inspect[Inspect metadata via content or properties]
    InstanceReady --> Convert[Root.convert_to_class(obj, flv)]
    Convert --> SetClass[obj.__class__ = cls]
    SetClass --> IfBody{if "body" in obj.content}
    IfBody --> FLVBody[flv(obj.content["body"])]
    SetClass --> IfFooter{if "footer" in obj.content}
    IfFooter --> FLVFooter[flv(obj.content["footer"])]
    InstanceReady --> RenderCall[concrete_subclass.render(**kwargs)]
    RenderCall --> Output[final presentation output]

## Methods (reimplementation-level detail):
- __init__(self, name: str, body: Renderable, footer: Renderable, style: Style, **kwargs) -> None
  - Behavior:
    - Calls ItemRenderer.__init__ with:
      - item_type = "report"
      - content = {"body": body, "footer": footer, "style": style}
      - name=name and any passed **kwargs forwarded
    - After return, self.item_type == "report" and self.content contains the keys "body", "footer", "style", and "name".
  - Caller responsibilities:
    - Provide body and footer that follow the Renderable contract (i.e., have a content mapping; typically concrete Renderable subclasses).
    - Provide an appropriate Style object.

- __repr__(self) -> str
  - Returns: "Root"

- render(self, **kwargs) -> Any
  - Raises: NotImplementedError
  - Intended to be overridden by subclasses that produce the final representation of the report.
  - Do not call Root.render directly; call render() on a subclass instance that implements it.

- @classmethod convert_to_class(cls, obj: Renderable, flv: Callable) -> None
  - Behavior:
    1. Mutates obj.__class__ = cls (assigns the class object to the instance's __class__ attribute).
    2. If "body" is a key in obj.content, calls flv(obj.content["body"]).
    3. If "footer" is a key in obj.content, calls flv(obj.content["footer"]).
  - Inputs:
    - obj: expected to have a content mapping (compatible with Renderable).
    - flv: callable used to convert or visit nested content elements (caller-defined).
  - Side effects and caveats:
    - Assigning to obj.__class__ may raise TypeError if the new class is incompatible with the object's layout.
    - convert_to_class assumes obj.content is a mapping; AttributeError will be raised if not.
    - flv should handle the types it receives; exceptions from flv propagate to the caller.

## Raises:
- __init__:
  - TypeError: if required arguments (name, body, footer, style) are missing (Python-level call-site error).
  - No explicit runtime type validation is performed; supplying incompatible types may surface errors later in processing.
- render:
  - NotImplementedError: Root.render raises this immediately.
- convert_to_class:
  - TypeError: possible when assigning to obj.__class__ if classes are incompatible (Python-level).
  - AttributeError: if obj has no content attribute or if obj.content is not a mapping.
  - Any exceptions raised by flv will propagate.

## Example:
(Conceptual; requires concrete Renderable subclasses and a concrete Root subclass that implements render.)

1) Prepare components:
   - body = ConcreteRenderableBody(...)   # implements render()
   - footer = ConcreteRenderableFooter(...)  # implements render()
   - style = Style(...)  # configuration object

2) Instantiate Root:
   - root = Root(name="monthly-report", body=body, footer=footer, style=style, anchor_id="rpt-2026-04")

   After this call:
   - root.content == {"body": body, "footer": footer, "style": style, "name": "monthly-report"} (anchor_id present if provided)

3) Convert an existing object into this class (advanced/deserialization scenario):
   - Root.convert_to_class(existing_obj, flv=converter_func)
   - After conversion, existing_obj.__class__ is Root (or the cls used) and converter_func has been applied to nested parts (body/footer) when present.

4) Render (only on a concrete subclass implementing render):
   - output = concrete_root.render()  # concrete_root must subclass Root and implement render()

Best practices:
- Prefer explicit construction of Root instances (rather than runtime class mutation) unless implementing deserialization/rehydration where convert_to_class is justified.
- Ensure body/footer are concrete Renderable instances to avoid errors during downstream rendering.
- Use a fresh dict for content where external mutation should be avoided; Root already constructs its own content mapping for the primary keys.

### `src.ydata_profiling.report.presentation.core.root.Root.__init__` · *method*

## Summary:
Initializes a Root instance by creating the canonical report content mapping (body, footer, style) and delegating metadata (name, optional anchor_id/classes) and item_type ("report") initialization to the parent initializers; the call sets up the object's essential state for downstream rendering/serialization.

## Description:
- Known callers and lifecycle stage:
    - Invoked by report builders and presentation factories when assembling a complete report object from component Renderable objects (the body and footer) together with a Style configuration.
    - This constructor is executed during object creation (construction) and prepares the object for later conversion or rendering by concrete subclasses.
- Why this logic is a separate method:
    - The Root constructor centralizes the report-specific content layout (the fixed keys "body", "footer", "style") so downstream renderers can reliably locate the main parts of a report.
    - It delegates generic metadata handling and item_type bookkeeping to ItemRenderer / Renderable to avoid duplicating metadata insertion logic (name, anchor_id, classes) and to preserve a consistent initialization pattern across renderable items.

## Args:
    name (str):
        Required. Friendly identifier for the report. This value will be recorded in the instance content mapping as content["name"].
    body (Renderable):
        Required. The report body as a Renderable (or object compatible with the Renderable contract). Stored at content["body"].
    footer (Renderable):
        Required. The report footer as a Renderable. Stored at content["footer"].
    style (Style):
        Required. A Style configuration object (ydata_profiling.config.Style). Stored at content["style"].
    **kwargs:
        Optional keyword arguments forwarded to the parent initializer (Renderable/ItemRenderer). Common options:
        - anchor_id (str): if provided, Renderable.__init__ will write content["anchor_id"].
        - classes (str): if provided, Renderable.__init__ will write content["classes"].
        Other kwargs accepted by the parent initializers are forwarded unchanged.

## Returns:
    None
    - As a constructor, it returns None but ensures the instance state is initialized (see Postconditions).

## Raises:
    TypeError:
        - A Python-level TypeError will occur if required positional arguments are omitted at call site.
        - A TypeError may be raised indirectly by the parent initializers if they attempt operations incompatible with the provided arguments (rare given this implementation).
    Any exception raised by parent initializers:
        - Because Root.__init__ delegates to ItemRenderer/Renderable.__init__, any exception those initializers raise (e.g., errors when writing into content if it were not a mapping) will propagate.

## State Changes:
- Attributes READ:
    - None of self's attributes are read by this method prior to initialization.
- Attributes WRITTEN (directly or indirectly as a result of this call):
    - self.item_type
        - Set to the string literal "report" by the ItemRenderer.__init__ invoked via super().__init__.
    - self.content
        - Assigned to the dict {"body": body, "footer": footer, "style": style} by the parent initializer.
    - content["name"]
        - Written by Renderable.__init__ when the name argument is forwarded; after construction content contains the supplied name.
    - content["anchor_id"] and/or content["classes"]
        - Written only if corresponding kwargs are provided; these keys are set by Renderable.__init__.

Notes:
    - The content dict stored on the instance is the exact dict created here (no defensive copy). Callers and external code that hold a reference to that dict will observe mutations.

## Constraints:
- Preconditions:
    - name must be a string (semantic expectation; not strictly type-checked at runtime).
    - body and footer should implement the Renderable contract (i.e., be Renderable instances or compatible objects) to avoid downstream errors during rendering.
    - style should be a Style instance (from ydata_profiling.config); passing an incompatible object may not error here but may cause later failures.
- Postconditions:
    - self.item_type == "report"
    - self.content is a mapping containing at least the keys: "body", "footer", "style", and (after parent init) "name".
    - content["body"] is the same object passed as body; content["footer"] is the same object passed as footer; content["style"] is the same style object passed in.
    - content may contain "anchor_id" and "classes" only if these were provided via kwargs.

## Side Effects:
    - No I/O or network calls are performed.
    - Mutates the instance by assigning item_type and content and (via parent initializer) may write metadata keys into the content dict.
    - The content dict is shared by reference; subsequent external mutations to that dict are visible on the instance and vice versa.
    - Forwarding **kwargs to the parent may trigger additional side effects defined by the parent initializers (e.g., inserting metadata keys).

### `src.ydata_profiling.report.presentation.core.root.Root.__repr__` · *method*

## Summary:
Return a stable, human-readable identifier for the object; calling this method does not modify the object's state.

## Description:
Provides the canonical string representation for a Root instance. It is directly used by Python's built-in repr() (i.e., repr(root_instance)). It also serves as the fallback representation when str(root_instance) is invoked and the class does not define __str__ (Python will then call __repr__). Common contexts where this representation appears:
- repr(root_instance)
- Interactive REPL displays and debugging tools that call repr() on objects
- Logging or diagnostic output that explicitly uses repr()

This logic is implemented as a dedicated method to:
- Ensure a single, consistent textual identifier for Root instances across the codebase.
- Make it straightforward for subclasses to override representation behavior without altering other logic.
- Keep representation concerns separated from functional code paths.

## Args:
    None

## Returns:
    str: Always returns the literal string "Root". There are no computed variants or conditional outputs.

## Raises:
    None

## State Changes:
    Attributes READ : None
    Attributes WRITTEN : None

## Constraints:
    Preconditions:
        - No preconditions on the object state; the method is stateless and requires no setup.
    Postconditions:
        - The instance is unchanged after the call.
        - The caller receives the string "Root".

## Side Effects:
    - None. The method performs no I/O, external calls, or mutations of objects outside the instance.

### `src.ydata_profiling.report.presentation.core.root.Root.render` · *method*

## Summary:
Abstract top-level rendering contract for the report object that, when implemented, produces the final rendered representation of the entire report. The base implementation does not change object state (it simply raises NotImplementedError); concrete subclasses must implement the composition of body, footer, and style into the final output.

## Description:
- Known callers and lifecycle stage:
    - Called by the final stage of the presentation pipeline (report builders, presentation factories, or orchestration code) when the assembled report must be converted into an output artifact (e.g., HTML string, JSON document, framework-specific widget).
    - Typical caller patterns: orchestration code constructs a Root instance (Root holds content["body"], content["footer"], and content["style"]) and then invokes render() to obtain the final representation to write to disk, send over an API, or embed into a larger document.

- Why this logic is its own method:
    - render() is the polymorphic entry point for producing the final representation of the report. The Root class is the top-level container for report elements (body, footer, style) and must expose a single, overridable method to produce the final output. Placing this logic in its own method enables different output formats and rendering backends (HTML, JSON, templating engines, etc.) to be implemented as subclasses without changing report construction logic.

- Implementation contract (for subclasses):
    - The base Root.render raises NotImplementedError. Subclasses must override render(**kwargs) to:
        1. Read self.content["body"] and self.content["footer"] (both provided as Renderable in Root.__init__) and self.content["style"] (a Style).
        2. Typically, invoke the child renderers (e.g., body.render(**kwargs), footer.render(**kwargs)) or otherwise obtain rendered fragments from them, then combine those fragments using style information to produce the final artifact.
        3. Return the final representation (type is implementation-defined — e.g., str, dict, or framework-specific object).
    - The method accepts arbitrary keyword arguments (**kwargs). Subclasses should document any expected keys and may forward **kwargs to child renderers (recommended) to allow caller-level control of rendering options.

## Args:
    **kwargs: Any
        - Arbitrary, implementation-defined rendering options. Typically forwarded to child renderers (body/ footer) or consumed by the top-level renderer to control formatting, resource resolution, or output mode.
        - No concrete keys are required by the base class.

## Returns:
    Any
        - The final rendered representation of the entire report.
        - Common return types: str (e.g., HTML), dict (e.g., JSON-serializable structure), or a renderer-specific object (e.g., a templating engine result or a report model).
        - Edge cases:
            - If child renderers return None or raise, the subclass implementation must decide whether to propagate exceptions, substitute placeholders, or fail fast. The base class imposes no policy.

## Raises:
    NotImplementedError
        - The base implementation (Root.render) unconditionally raises NotImplementedError. Callers should only call this method on concrete Root subclasses that implement the method.
    Subclass-specific exceptions
        - Concrete implementations may raise other exceptions (IOError, ValueError, TypeError, domain-specific errors) as appropriate when rendering fails or when preconditions are violated.

## State Changes:
- Attributes READ:
    - self.content (the content dict)
    - self.content["body"] (expected to be a Renderable)
    - self.content["footer"] (expected to be a Renderable)
    - self.content["style"] (Style)
    - self.name (optional; may be used for metadata or anchor generation)
- Attributes WRITTEN:
    - Base implementation: none (the base method raises NotImplementedError and does not modify state).
    - Subclass implementations: permitted to modify self.content or nested objects (for example, to add generated anchors, inject metadata, or cache rendered fragments). Any modifications should be documented by the subclass and kept minimal unless necessary.

## Constraints:
- Preconditions:
    - An instance of Root must have been constructed with content containing keys "body", "footer", and "style" (Root.__init__ sets these).
    - content["body"] and content["footer"] are expected to be Renderable instances (or compatible objects with a render(**kwargs) method) — callers constructing Root should ensure this.
    - If the subclass relies on additional invariants (e.g., non-empty body), it must validate and raise clear exceptions.

- Postconditions:
    - On successful completion, the method returns the final report representation.
    - The method does not promise to leave self.content unchanged unless documented by the concrete subclass; callers should not rely on in-place invariants unless documented.

## Side Effects:
    - The base method itself has no side effects (it raises NotImplementedError). Concrete implementations commonly:
        - Call child.render(**kwargs) on body/footer which may cause further computation, resource allocation, or I/O depending on child implementations.
        - Perform I/O indirectly (writing files, loading external assets, or triggering network calls) if the chosen rendering backend requires it.
        - Mutate the content dict or child renderables (e.g., to insert anchors or caching structures); such mutations are implementation-specific and should be documented by the subclass.

## Implementation notes (guidance for implementers):
    - Prefer composition: call body.render(**kwargs) and footer.render(**kwargs) to obtain sub-fragments and compose them with style information.
    - Keep side effects explicit: if the renderer writes files or performs network I/O, surface that behavior in method-level documentation and consider exposing a no-side-effect rendering mode (e.g., returning a string).
    - Be defensive: validate that content["body"] and content["footer"] implement render; provide clear error messages if they do not.
    - Document any expected keys in **kwargs (e.g., "assets_path", "inline_css", "optimize") at the subclass level.

### `src.ydata_profiling.report.presentation.core.root.Root.convert_to_class` · *method*

## Summary:
Change an existing Renderable-like object's runtime class to Root and recursively invoke the provided conversion callback on the object's "body" and "footer" content entries; this mutates the object's type and ensures nested parts are converted for the presentation pipeline.

## Description:
This classmethod is used during reconstruction/deserialization or factory-driven initialization of presentation trees. Typical callers are deserialization or factory routines that receive loosely-typed or generic Renderable-like objects and must convert them into concrete renderer instances (here: Root) before any rendering occurs.

When invoked, the method performs two focused steps:
1. Assigns cls to obj.__class__, changing the object's runtime type to the class on which this method is called (normally Root or a Root subclass).
2. If obj.content contains a "body" entry, calls flv(obj.content["body"]); then if obj.content contains a "footer" entry, calls flv(obj.content["footer"]). The flv callable is expected to perform any necessary in-place conversion of those nested entries (its return value is ignored).

Why this is a separate method:
- Converting runtime class and recursively handling Root-specific nested keys ("body" and "footer") is a cohesive operation tied to the Root structure. Encapsulating this logic avoids duplicating conversion and recursion at call sites and keeps Root-specific conversion behavior localized.

Known callers and lifecycle stage:
- Deserialization/reconstruction and presentation factory code that rebuilds a tree of Renderable instances from a generic representation.
- This method is expected to be invoked during object reconstruction/initialization, prior to any call to render() so that subsequent method resolution and type-specific behavior are correct.

## Args:
    cls (type): The class object to assign to obj.__class__. When called as Root.convert_to_class, cls will be Root (or a subclass).
    obj (Renderable): The instance to be reclassified. Must expose a content attribute that behaves like a dict-like mapping.
    flv (Callable[[Any], Any]): A callable invoked for side effects on nested entries. Expected to accept the values stored under obj.content["body"] and obj.content["footer"] when present. The callable's return value is ignored.

## Returns:
    None
    - No value is returned. All work is performed by mutating obj.__class__ and by invoking flv on nested content entries.

## Raises:
    TypeError:
        - If assigning cls to obj.__class__ is invalid because the target class has an incompatible instance layout (this is raised by Python runtime).
        - If flv is not callable and the code attempts to call it, Python will raise TypeError.
    AttributeError:
        - If obj does not have a content attribute (i.e., it is not a Renderable-like object), accessing obj.content will raise AttributeError.
    Any exception raised by flv:
        - Exceptions thrown by flv when processing the "body" or "footer" entries propagate unchanged to the caller.

## State Changes:
    Attributes READ:
        - obj.content (checked to determine presence of keys)
        - obj.content["body"] (read only if the "body" key exists)
        - obj.content["footer"] (read only if the "footer" key exists)
    Attributes WRITTEN:
        - obj.__class__ (assigned to cls)

## Constraints:
    Preconditions:
        - obj must be an instantiated Python object exposing a content attribute that is a mapping (dict-like). If content is missing or not mapping-like, behavior will raise AttributeError or other mapping-related exceptions.
        - cls must be a class object appropriate for assignment to obj.__class__ (assignment compatibility is enforced by the Python runtime).
        - flv must be a callable able to accept and process the values stored under "body" and "footer" if those keys exist; callers should ensure flv can handle None or any non-Renderable values that might be present.
    Postconditions:
        - On successful return, obj.__class__ is equal to the cls argument.
        - If obj.content contained "body" and/or "footer", flv has been invoked on each corresponding value in that order (body first, then footer). No guarantees are made about modifications performed by flv beyond their invocation.

## Side Effects:
    - Mutates obj.__class__, changing the object's runtime type immediately for all references.
    - Calls flv on nested content values ("body" and "footer") when present; flv may further mutate those objects or raise exceptions.
    - No I/O, networking, or external service calls are performed by this method itself.

