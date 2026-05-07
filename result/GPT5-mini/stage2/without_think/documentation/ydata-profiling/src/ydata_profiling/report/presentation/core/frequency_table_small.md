# `frequency_table_small.py`

## `src.ydata_profiling.report.presentation.core.frequency_table_small.FrequencyTableSmall` · *class*

## Summary:
A small, backend-agnostic item renderer representing a compact frequency table. It packages the table rows and a redaction flag for presentation backends and defines the rendering contract (render() must be implemented by concrete backends).

## Description:
FrequencyTableSmall is a lightweight presentation model used by the report presentation pipeline to represent a compact frequency table (e.g., top value frequencies for a column). It does not perform any rendering itself; instead it stores the content required by renderers and signals the required item type ("frequency_table_small").

Scenarios and callers:
- Instantiate when you want to hand a compact frequency table (rows of values and counts) to the presentation layer without choosing a concrete output format.
- The report/presentation pipeline (the code that iterates over ItemRenderer instances and converts them into final output fragments) is the typical caller. That pipeline will either:
  - replace this item with a rendered fragment by calling a concrete subclass's render(), or
  - use a concrete renderer implementation that knows how to render items labeled with item_type "frequency_table_small".
- This class is a distinct abstraction to separate data (rows + redact metadata) from presentation logic (HTML, JSON, templates, etc.). This makes it easy to target multiple output backends without modifying the data model.

## State:
- Constructor parameters:
  - rows (List[Any]) — required
    - The list of rows to display in the compact frequency table. Each row's structure is application-dependent (commonly a tuple or dict containing the observed value, its count, and optionally a percentage).
    - No structural validation is performed by FrequencyTableSmall itself; callers should provide rows in a format the renderer backend expects.
  - redact (bool) — required
    - When True, the presentation backend is expected to alter/redact sensitive values in the rendered output.
  - **kwargs — forwarded to ItemRenderer:
    - name (Optional[str]) — optional display name for the item (if supported by the parent class)
    - anchor_id (Optional[str]) — optional anchor id used for in-page linking (if supported)
    - classes (Optional[str]) — optional CSS/class string for presentation (if supported)

- Stored attributes (inherited / set during initialization):
  - item_type (str)
    - Value: always "frequency_table_small" (set by this class via ItemRenderer)
    - Invariant: item_type == "frequency_table_small"
  - content (dict)
    - Keys:
      - "rows": List[Any] (the same object/value passed in as rows)
      - "redact": bool (the same boolean passed in)
    - Invariant: "rows" in content and "redact" in content

- Other inherited attributes forwarded via kwargs (if provided):
  - name: Optional[str]
  - anchor_id: Optional[str]
  - classes: Optional[str]

Class invariants:
- After __init__, the instance must have item_type == "frequency_table_small" and content must be a dict with keys "rows" and "redact".
- The class itself does not mutate content during rendering; render implementations should treat content as read-only unless they explicitly document otherwise.

## Lifecycle:
- Creation:
  - Instantiate with rows (List[Any]) and redact (bool). Optionally pass name, anchor_id, classes as keyword arguments.
  - Example: FrequencyTableSmall(rows=[("a", 10), ("b", 5)], redact=False)
- Usage:
  - No rendering is provided by this base class. The presentation pipeline or a concrete renderer subclass should call render() to obtain the renderable representation.
  - Typical sequence:
    1. Create instance with rows + redact.
    2. Pass instance to presentation pipeline or register it with a renderer.
    3. A concrete renderer (either a subclass that overrides render() or an external dispatcher that knows how to render item_type "frequency_table_small") produces the final output fragment.
- Destruction:
  - No special cleanup is required. The class does not open resources or maintain external handles. It is safe to let instances be garbage-collected normally.

## Method Map:
graph LR
    A[FrequencyTableSmall.__init__(rows, redact, **kwargs)] --> B[ItemRenderer.__init__(item_type, content, **kwargs)]
    A --> C[content["rows"], content["redact"] set]
    D[repr()] -->|returns| E["FrequencyTableSmall"]
    F[render()] -.->|raises| G[NotImplementedError]
    B --> H[Renderable (stores content/name/anchor_id/classes)]

(Note: render() is intentionally unimplemented in this base class; concrete renderers must override it.)

## Raises:
- __init__:
  - The constructor does not raise any exceptions explicitly. It forwards arguments to ItemRenderer.__init__ and relies on the parent classes to validate kwargs if they do so.
- render():
  - NotImplementedError — always raised by this base implementation to indicate subclasses must implement rendering logic.

## Example:
1) Basic instantiation and inspection:
    instance = FrequencyTableSmall(rows=[("A", 42), ("B", 7)], redact=False)
    print(repr(instance))  # -> "FrequencyTableSmall"
    # The presentation pipeline is expected to call instance.render(), but calling it on this base class raises:
    try:
        instance.render()
    except NotImplementedError:
        # Expected for the base class; replace with a concrete renderer for actual output
        pass

2) Typical subclass override pattern (conceptual, described in prose):
    - A concrete backend would subclass FrequencyTableSmall and implement render() to:
      - Read self.content["rows"] and self.content["redact"]
      - Apply any redaction or escaping as required
      - Produce a backend-specific fragment (e.g., an HTML string, a JSON-serializable dict, or a template-rendered object)
    - The subclass' render() should avoid mutating self.content unless that mutation is intentionally part of the contract and explicitly documented.

### `src.ydata_profiling.report.presentation.core.frequency_table_small.FrequencyTableSmall.__init__` · *method*

## Summary:
Initialize the instance as a compact presentation item for a frequency table by storing the provided rows and redaction flag in the instance content and setting the item type to "frequency_table_small".

## Description:
This constructor packages the data required to render a compact frequency table and delegates base initialization to ItemRenderer and Renderable. It is typically called during the report construction/presentation pipeline when a compact frequency summary (e.g., top values and counts for a column) is produced and must be handed to presentation backends or concrete renderers.

This logic is separated into its own constructor to keep the presentation data model (content dict and item_type) distinct from rendering logic; FrequencyTableSmall only models data (rows + redact metadata) and does not implement rendering itself.

## Args:
    rows (List[Any]):
        Sequence of rows for the compact frequency table. Each element's structure is application-dependent (commonly a tuple or dict containing the value and its count, optionally percentage). No structural validation is performed here; callers must supply rows in the format expected by downstream renderers.
    redact (bool):
        Boolean flag that instructs renderers whether values should be redacted. Expected True or False; non-bool values are accepted at runtime but may be misinterpreted by renderers.
    **kwargs:
        Only these keyword arguments are accepted and forwarded to ItemRenderer / Renderable:
        - name (Optional[str]): stored in content["name"] when provided
        - anchor_id (Optional[str]): stored in content["anchor_id"] when provided
        - classes (Optional[str]): stored in content["classes"] when provided

        Passing any keyword argument other than name, anchor_id, or classes will cause a TypeError to be raised by the parent constructor (ItemRenderer.__init__), because it does not accept arbitrary kwargs.

## Returns:
    None
    The initializer returns None and its observable effect is to mutate the instance state (set content and item_type).

## Raises:
    TypeError:
        If kwargs include keys other than the allowed set (name, anchor_id, classes), the call will fail with a TypeError raised by ItemRenderer.__init__ due to unexpected keyword arguments.
    KeyError (indirect / on later access):
        If name, anchor_id, or classes are not provided, attempting to read Renderable.name, Renderable.anchor_id, or Renderable.classes will raise KeyError because those properties access content[...] directly. This KeyError is not raised during construction, but is a direct consequence of the postcondition when optional keys are omitted.

## State Changes:
    Attributes READ:
        - None (the constructor does not read pre-existing instance attributes)
    Attributes WRITTEN:
        - self.content (dict): assigned via Renderable.__init__ and will contain at minimum:
            - "rows": the rows argument (the same object/reference provided)
            - "redact": the redact boolean
            - optionally "name", "anchor_id", "classes" if provided via kwargs
        - self.item_type (str): set to "frequency_table_small" by ItemRenderer.__init__

## Constraints:
    Preconditions:
        - rows should be a list-like object (List[Any]); passing None or a non-iterable is not validated and may cause downstream failures in renderers.
        - redact should be a boolean for correct redaction semantics; non-bool truthy/falsy values will be accepted but may be ambiguous.
        - Only name, anchor_id, and classes are valid kwargs. Any other kwargs will raise TypeError at construction.
    Postconditions:
        - self.item_type == "frequency_table_small"
        - self.content is a dict containing at least the keys "rows" and "redact" mapped to the provided values
        - If name/anchor_id/classes were supplied, the corresponding keys exist in self.content with the supplied values

## Side Effects:
    - No I/O or external service calls occur.
    - The constructor mutates the new instance by setting self.content and self.item_type (via the parent constructors).
    - The provided rows object is stored by reference inside content; the constructor does not copy or mutate rows.

### `src.ydata_profiling.report.presentation.core.frequency_table_small.FrequencyTableSmall.__repr__` · *method*

## Summary:
Returns a stable, human-readable identifier for this renderer instance without modifying the object's state.

## Description:
Known callers and context:
- Invoked implicitly by Python built-ins and runtime facilities that request an object's representation, e.g., repr(renderer_instance), interactive REPL inspection, logging frameworks, container reprs, and f-strings that use the !r conversion.
- Typically used during debugging, logging, or when tool code or developers inspect renderer objects for identification purposes.
- In the lifecycle of a renderer object, this method is called at observation/inspection time; it is not part of the rendering pipeline and does not affect rendering state.

Why this is a separate method:
- __repr__ is the Python special method that the interpreter and standard library call to obtain an object's representation. Implementing it as a dedicated method provides a stable, concise identifier for the class and makes debugging and logging more informative. Keeping this logic isolated avoids duplicating identification logic elsewhere and ensures the representation remains constant regardless of instance state.

## Args:
None.

## Returns:
str
- Always returns the constant string "FrequencyTableSmall".
- There are no conditional or instance-dependent return values.

## Raises:
None.
- The method does not perform operations that raise exceptions under normal circumstances.

## State Changes:
Attributes READ:
- None. The implementation does not read any self.<attr> attributes.

Attributes WRITTEN:
- None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
- Caller must have a valid object reference (an instance of FrequencyTableSmall). The method does not require any particular initialization of instance attributes because it does not access them.

Postconditions:
- The method returns the string "FrequencyTableSmall".
- No state on the instance or external objects is modified.

## Side Effects:
- None. There is no I/O, no external service interaction, and no mutation of objects outside self.

### `src.ydata_profiling.report.presentation.core.frequency_table_small.FrequencyTableSmall.render` · *method*

## Summary:
Defines the rendering contract for a compact frequency-table presentation. The base implementation deliberately raises NotImplementedError; concrete backends must override this method to produce the renderable representation without mutating the object's stored content.

## Description:
This method is the rendering entry point for a FrequencyTableSmall item. In the current class it is intentionally unimplemented and raises NotImplementedError to signal that concrete presentation layers (for example HTML, JSON, or template-based renderers) must provide the actual rendering logic.

Known callers and context:
- Intended to be called by the report presentation/rendering phase where ItemRenderer instances are converted into final output fragments (e.g., when the report generator iterates over renderable items). The repository's presentation pipeline expects each ItemRenderer subclass to implement render().

Why this is its own method:
- Rendering behavior depends on the output target (HTML, JSON, template engine) and therefore cannot be implemented generically at construction time. Keeping rendering as a separate overridable method decouples data storage (the content dict set at init) from presentation concerns and allows multiple backends to reuse the same content model.

## Args:
None.

## Returns:
Any
- The concrete implementation decides the return type. Typical choices in the codebase are:
  - A string containing a rendered HTML fragment
  - A dictionary/serializable structure representing the table
  - A framework-specific renderable object
- The base method does not return; it raises NotImplementedError.

## Raises:
NotImplementedError
- Always raised by this base implementation to force subclass implementations to provide rendering logic.

## State Changes:
Attributes READ:
- The base method does not read any attributes (it immediately raises). Implementers are expected to read:
  - self.content["rows"] — the list of rows passed at construction (see __init__)
  - self.content["redact"] — boolean flag passed at construction controlling redaction behavior

Attributes WRITTEN:
- The base implementation writes none.
- Implementations should avoid mutating self.content; rendering should be a pure read-only operation on the item's stored data unless there is an explicit reason to update internal state.

## Constraints:
Preconditions:
- The instance must have been initialized (FrequencyTableSmall.__init__ stores content with "rows" and "redact"). Implementations may assume those keys exist in self.content.

Postconditions:
- For the base class: NotImplementedError is raised and no state change occurs.
- For valid overrides: the method returns a renderable representation derived from self.content and leaves self.content unchanged (unless an override documents and justifies mutation).

## Side Effects:
- The base method has no side effects other than raising NotImplementedError.
- Concrete implementations may perform presentation-specific side effects (e.g., escaping or templating). Implementers should avoid I/O (disk, network) in render(); such side effects should be handled outside of pure rendering if possible so rendering remains deterministic and testable.

