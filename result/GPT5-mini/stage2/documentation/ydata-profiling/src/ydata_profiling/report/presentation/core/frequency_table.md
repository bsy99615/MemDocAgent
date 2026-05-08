# `frequency_table.py`

## `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable` · *class*

## Summary:
Represents a presentation-layer renderer for a variable's frequency table. It stores the table data (rows) and a redact flag and provides the render() hook to produce a presentation-ready representation; __repr__ returns a stable identifier.

## Description:
FrequencyTable is an ItemRenderer specialization that packages frequency-table data for the presentation/reporting pipeline. It should be instantiated by parts of the report generator (or factories) that prepare presentation items for a single variable's frequency distribution. Typical callers assemble the rows (label/value and counts) and decide whether values must be redacted, then create a FrequencyTable and hand it to the renderer pipeline for final rendering.

The class exists to separate data (rows + redact flag) from presentation logic (render). FrequencyTable is a thin data-holder with metadata (item_type) and an overridable render() method so different output formats (HTML, JSON, UI widget) can be produced by concrete implementations or by consumers that subclass/extend FrequencyTable.

Responsibilities and boundaries:
- Responsibility: hold frequency-table content and expose a rendering hook.
- Not responsible for: computing frequencies, redaction policy enforcement beyond a boolean flag, or performing I/O. Frequency computation and sensitive-data decisions are the caller's responsibility; render() should only convert provided content to a presentation format.

## State:
Attributes (public surface as provided by ItemRenderer):
- item_type (str)
  - Value: "frequency_table"
  - Invariant: always equals the literal "frequency_table" for instances constructed by this class.
- content (dict)
  - Expected keys:
    - "rows": list
      - Type: list (or list-like iterable) of row entries. The exact row shape is implementation-dependent (commonly dicts like {"label": str, "count": int} or tuples (value, count)).
      - Valid values: empty list permitted to indicate no observed categories.
    - "redact": bool
      - Type: bool
      - Semantics: when True, renderers must avoid exposing raw sensitive label/value strings; when False, raw labels may be shown.
- name (Optional[str])
  - Passed through from ItemRenderer via kwargs; optional user-facing identifier.
- anchor_id (Optional[str])
  - Optional anchor id used by some presentation targets.
- classes (Optional[str])
  - Optional CSS/class string for HTML renderers.

Class invariants:
- item_type == "frequency_table"
- content is a dict containing keys "rows" and "redact"
- content["rows"] is list-like and content["redact"] is boolean (implementations may validate but code does not enforce at construction time)

## Lifecycle:
Creation:
- Instantiate with two required parameters:
  - rows: list — a list-like collection describing frequency rows.
  - redact: bool — whether display values should be redacted.
- Optional keyword-only parameters (forwarded to ItemRenderer via kwargs): name, anchor_id, classes.
- Example conceptual constructor: create FrequencyTable with rows list and redact flag; pass name/anchor_id/classes as needed.

Usage:
- Typical sequence:
  1. Instantiate FrequencyTable(rows, redact, name=..., anchor_id=..., classes=...).
  2. Optionally include the instance in a collection of renderers or pass to a report assembly routine.
  3. The report renderer calls render() to obtain a presentation (HTML fragment, JSON-serializable dict, or framework-specific widget).
  4. repr(instance) returns "FrequencyTable" and can be used for logging/debugging.
- Ordering: there is no required call order beyond construction before render(); __repr__ may be called at any time.

Destruction / cleanup:
- No special cleanup responsibilities. FrequencyTable does not open resources and is not a context manager. Rely on Python garbage collection.

## Method Map:
graph LR
  A[__init__(rows, redact, **kwargs)] --> B[item_type = "frequency_table"]
  A --> C[content = {"rows": rows, "redact": redact}]
  A --> D[name/anchor_id/classes stored by ItemRenderer]
  E[__repr__()] --> F[returns "FrequencyTable"]
  G[render()] --> H[NotImplementedError (must be overridden by concrete renderer)]

(Interpretation: __init__ sets up item_type and content; __repr__ returns a stable identifier; render is an abstract hook.)

## Methods detail (behavioral summary):
- __init__(rows: list, redact: bool, **kwargs)
  - Stores item_type and content by delegating to ItemRenderer.__init__.
  - Does not perform deep validation of rows or redact.
  - Accepts optional kwargs forwarded to ItemRenderer (name, anchor_id, classes).
- __repr__() -> str
  - Deterministically returns the string "FrequencyTable". No side effects.
- render() -> Any
  - Current implementation raises NotImplementedError.
  - Intended to be overridden by concrete renderers to return a presentation-ready structure.
  - Recommended contract for overridden implementations:
    - Read-only: should not mutate self or self.content.
    - Input: read rows = self.content["rows"], redact = self.content["redact"].
    - Output: a JSON-serializable structure (dict/list/primitives) or an HTML string suitable for the report pipeline.
    - Edge cases:
      - If rows is empty, return an empty-table representation (e.g., empty list of rows or empty HTML table) instead of None.
      - If redact is True, mask or omit raw values in returned representation (e.g., replace label with "[REDACTED]").
    - Error handling (recommended): raise ValueError for missing keys or invalid shapes, TypeError for invalid element types.

## Raises:
- __init__: The FrequencyTable.__init__ implementation does not explicitly raise exceptions. Runtime errors may propagate from ItemRenderer or Renderable if invalid kwargs are provided; FrequencyTable does not validate types at construction.
- render: As implemented in this class, calling render() will raise NotImplementedError. Concrete subclasses or overrides should implement error handling appropriate for the chosen output format.

## Example (conceptual usage):
1. Prepare rows, e.g., a list of entries where each entry describes a category label and its count.
2. Instantiate FrequencyTable with rows and redact flag (and optional name/anchor_id/classes).
3. Pass the instance into the report assembly or call its render() method (note: render() in this base class raises NotImplementedError; override in a subclass or implement a renderer that consumes the content).
4. Use repr(instance) for logging; it returns the constant "FrequencyTable".

## Implementation guidance checklist (for reimplementing the class):
- Subclass ItemRenderer and call its __init__ with:
  - item_type = "frequency_table"
  - content = {"rows": rows, "redact": redact}
  - forward any allowed kwargs (name, anchor_id, classes)
- Implement __repr__ to return the constant string "FrequencyTable".
- Keep render() abstract (raise NotImplementedError) or provide a concrete rendering that:
  - Reads content["rows"] and content["redact"]
  - Returns a serializable presentation (dict or HTML string)
  - Does not mutate instance state and handles empty rows/redaction appropriately

### `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable.__init__` · *method*

## Summary:
Initialize the FrequencyTable presentation item by packaging the provided rows and redact flag into the renderer's content and setting the item's type to the literal "frequency_table"; optional presentation metadata is forwarded to the parent initializer.

## Description:
Called during the report-assembly stage by report generators or item-factory utilities that have computed a variable's frequency rows and determined whether raw values must be redacted. This constructor centralizes how frequency-table content and the item_type are created so downstream renderers and the presentation pipeline can rely on a consistent content shape.

This logic is implemented as a dedicated initializer to:
- ensure a consistent item_type ("frequency_table") for all frequency-table items,
- keep the construction of the content dict (rows + redact) localized and predictable,
- forward shared presentation metadata (name, anchor_id, classes) to the shared ItemRenderer/Renderable initialization logic instead of duplicating that handling.

## Args:
    rows (list):
        A list-like collection describing frequency rows for a single variable.
        - Typical element shapes: dicts like {"label": str, "count": int} or tuples (value, count).
        - Allowed values: any list-like object; an empty list is valid to indicate no observed categories.
        - This initializer does not perform deep validation of element types or element shapes.
    redact (bool):
        Boolean flag indicating whether raw label/value strings should be treated as sensitive.
        - True: downstream renderers are expected to mask or avoid exposing raw values.
        - False: downstream renderers may display raw labels/values.
    **kwargs:
        Optional presentation metadata forwarded to ItemRenderer (and ultimately Renderable).
        Common supported keys:
        - name (Optional[str]): human-readable identifier for the item (default: None).
        - anchor_id (Optional[str]): optional anchor identifier for some renderers (default: None).
        - classes (Optional[str]): optional CSS/class hint for HTML renderers (default: None).
        Unexpected kwargs will be forwarded to the parent initializer and may cause errors there.

## Returns:
    None
    - The constructor returns None; effects are limited to mutating the new instance.

## Raises:
    This initializer does not explicitly raise exceptions.
    - Runtime exceptions may propagate from ItemRenderer.__init__ or from ancestor initializers if they validate or reject arguments (for example, TypeError for invalid argument types or unexpected keyword arguments). Such exceptions originate in parent initializers, not from this method's explicit logic.

## State Changes:
Attributes READ:
    - None from the existing instance state (only constructor arguments are used).
Attributes WRITTEN (directly or via parent initializers):
    - self.item_type (str): set to the literal "frequency_table".
    - self.content (dict): set to a dictionary containing the keys "rows" and "redact" (constructed from the provided arguments).
    - self.name (Optional[str]): may be set by the parent initializer if provided in kwargs.
    - self.anchor_id (Optional[str]): may be set by the parent initializer if provided in kwargs.
    - self.classes (Optional[str]): may be set by the parent initializer if provided in kwargs.

## Constraints:
Preconditions:
    - rows should be a list-like collection suitable for downstream renderers to iterate over.
    - redact should be a boolean; non-boolean values are not coerced here and may lead to unexpected renderer behavior.
    - If passing kwargs, prefer only supported metadata keys (name, anchor_id, classes) unless the parent initializer is known to accept others.

Postconditions:
    - After construction:
        - self.item_type == "frequency_table"
        - self.content is a dict containing keys "rows" and "redact" populated from the corresponding constructor arguments
        - Optional presentation metadata (name, anchor_id, classes) is set on the instance if accepted by the parent initializer

## Side Effects:
    - No I/O, network access, or external service calls.
    - Mutates the new instance by setting attributes listed above.
    - The initializer itself does not mutate the contents of the rows argument; it places the rows value into the content structure for later consumption by renderers.

### `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable.__repr__` · *method*

## Summary:
Returns a stable, human-readable identifier for the renderer ("FrequencyTable") used when the object is represented as text; it does not modify the object's state.

## Description:
This method is the textual representation hook used by Python's built-in repr() (and often indirectly by str(), logging, and interactive REPL displays). It is invoked when code or tooling needs a concise identifier for the object during debugging, logging, or tests, for example:
- When a developer calls repr(instance) or prints a collection containing the instance.
- When logging or debugging tools render the object.
- When unit tests assert on object representations for readability.

This logic is separated into its own method to:
- Provide a consistent, minimal representation across all FrequencyTable instances regardless of internal state.
- Avoid exposing internal content (such as rows or redact flags) in logs or repr output.
- Make it trivial to override or customize representation behavior in subclasses or during debugging.

## Args:
None.

## Returns:
str: The literal string "FrequencyTable". This is invariant for all instances and is returned in all cases (no conditional branches).

Edge-case return values:
- There are no alternative return values; the method always returns the same constant.

## Raises:
None. This method does not raise any exceptions.

## State Changes:
Attributes READ:
- None. The implementation does not access any self.<attr> fields.

Attributes WRITTEN:
- None. The implementation does not modify self or any external state.

## Constraints:
Preconditions:
- self must be a valid instance of FrequencyTable (no additional state requirements).

Postconditions:
- No object state is changed.
- The method returns the constant string "FrequencyTable".

## Side Effects:
- None. No I/O, no external service calls, and no mutations to objects outside self.

## Implementation notes (for reimplementation):
- Implement as a parameterless instance method that returns the exact string "FrequencyTable".
- Keep the implementation trivial and side-effect free so repr() remains inexpensive and safe in debug/logging contexts.
- Maintain the constant spelling and capitalization to preserve any external expectations (tests or logging parsers) that look for this exact identifier.

### `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable.render` · *method*

## Summary:
Produce a presentation-ready representation of the frequency-table content held on the instance. The current implementation is abstract and raises NotImplementedError; a concrete implementation should read the stored rows and redact flag and return a serializable presentation (e.g., HTML string, JSON-serializable dict, or a UI widget representation) without mutating the object state.

## Description:
Known callers and lifecycle:
- No concrete call sites for this method are present in the provided context. In typical usage this method is invoked by the report rendering pipeline at the presentation stage when assembling the report output for a single variable's frequency distribution.
- The method is part of a family of ItemRenderer subclasses responsible for converting an item’s content dict (provided at construction) into the final renderable representation consumed by the report generator.

Why this is a separate method:
- Rendering logic is presentation-specific (HTML/JSON/widget) and varies by output target. Encapsulating it in a dedicated render() method allows swapping or overriding presentation formats without changing the data model or the report pipeline.
- Keeping rendering separate enables tests to assert on rendered output shape and allows reusing the same content with different renderers.

Implementation guidance (recommended; not enforced by current code):
- Read rows = self.content["rows"] and redact = self.content["redact"].
- Validate that rows is a list (or an iterable) before rendering; if rows is empty, return an empty-table representation rather than None.
- Respect the redact flag: when redact is True, mask or replace sensitive display values (e.g., with a fixed string like "[REDACTED]" or by omitting raw values) while still presenting counts.
- Produce a serializable representation suitable for the report pipeline. Common choices:
    - A dict with standardized keys (e.g., {"type": "frequency_table", "rows": [{"label": ..., "count": ...}, ...]})
    - An HTML fragment (string) containing a <table> for inclusion in HTML reports
    - A JSON-serializable structure for API/JS consumption
- Ensure that the returned structure uses only JSON-serializable primitives (str, int, float, bool, None, list, dict) or objects known to the report renderer.

## Args:
This method takes no explicit arguments beyond self.

## Returns:
Any
- The current signature permits any return type. The concrete implementation should return a presentation object appropriate for the report pipeline:
    - JSON/dict structure describing the table, or
    - A string (HTML fragment), or
    - A framework-specific widget/markup object used elsewhere in the renderer.
- Edge cases:
    - If rows is an empty list, return an empty-table representation (e.g., an empty list of rows or an empty HTML table), not None.
    - If redact is True, the value fields in the returned representation must not contain raw sensitive values.

## Raises:
- NotImplementedError: This method as implemented raises NotImplementedError unconditionally. Concrete subclasses or future implementations must override this method to provide rendering behavior.
- (Recommendation) Implementations MAY raise:
    - ValueError if self.content lacks required keys or if rows is not an iterable of expected elements.
    - TypeError if rows contains elements of an unsupported type for rendering.
  These recommended exceptions are not raised by the current method but are suggested for robust implementations.

## State Changes:
Attributes READ:
- self.content (the dict assigned in __init__)
    - Specifically, self.content["rows"]
    - Specifically, self.content["redact"]
- self.item_type (readonly metadata; typically "frequency_table")

Attributes WRITTEN:
- None. The method should not mutate self or self.content; it is intended to be a pure transformation from content -> presentation.

## Constraints:
Preconditions:
- The instance must have been constructed via FrequencyTable.__init__, so self.content exists and includes the keys "rows" and "redact".
- Implementers should assume:
    - "rows" is present and is a list-like collection of row entries (the concrete shape of each entry is implementation-dependent).
    - "redact" is present and is a boolean.

Postconditions:
- After a successful call, self remains unchanged.
- The method returns a serializable presentation of the frequency table ready for consumption by the outer report renderer.

## Side Effects:
- The current method implementation has no side effects other than raising NotImplementedError.
- Recommended implementations should avoid side effects. In particular, render() should not:
    - Perform I/O (file, network)
    - Mutate global state
    - Modify the instance attributes (self.content or others)
- If an implementation must perform expensive computation, consider caching or moving that work outside render() to keep render() fast and idempotent.

## Minimal step-by-step implementation checklist for implementers:
1. Read rows = self.content["rows"]; assert it is iterable.
2. Read redact = bool(self.content.get("redact", False)).
3. Map each row element into a presentation row: decide on fields (e.g., "label"/"value" and "count").
4. If redact is True, replace or mask displayable values.
5. Assemble and return a serializable representation (dict or string) suitable for the report renderer.
6. Do not modify self or self.content; raise clear exceptions for invalid input shapes.

