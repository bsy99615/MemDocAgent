# `correlation_table.py`

## `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable` · *class*

## Summary:
Represents a presentation-ready "correlation_table" item that wraps a correlation matrix for rendering by a concrete renderer. It defines the structural content and identity for correlation-table renderers but does not implement rendering itself.

## Description:
Use this class when you need a standardized item object that carries a correlation matrix to the presentation layer. Typical callers create an instance and hand it to a renderer/factory that knows how to convert the contained matrix into HTML, JSON, or another output format.

This class exists to:
- Encapsulate the minimal, consistent payload for correlation-table presentation: an item_type identifier ("correlation_table") and a content dictionary containing the correlation matrix under the key "correlation_matrix".
- Provide a consistent base for concrete renderers to inherit from and implement the actual render() method.

CorrelationTable is intentionally lightweight: it delegates storage and common presentation attributes (name, anchor_id, classes) to its parent classes (ItemRenderer / Renderable) and enforces the item_type and content shape required for correlation-table presentation.

Known callers/factories:
- Any presentation layer code that assembles items for a report and dispatches them to specific renderers. (This class defines the item contract; concrete renderers or higher-level report builders instantiate or accept it.)

## State:
- name (constructor parameter)
  - Type: str
  - Purpose: Optional human-readable identifier for the item (passed to parent constructors).
  - Constraints: Provided as a positional or keyword argument; CorrelationTable does not validate its contents.

- correlation_matrix (constructor parameter, stored inside content)
  - Type: pd.DataFrame
  - Purpose: The actual correlation matrix to be presented; stored in the content dictionary under the key "correlation_matrix".
  - Constraints: No runtime type enforcement is performed by CorrelationTable; callers should supply a pandas DataFrame to match the type annotation.

- item_type (inherited from ItemRenderer)
  - Type: str
  - Value: "correlation_table"
  - Invariant: After initialization, item_type is set to the literal string "correlation_table" and should not be modified by normal usage.

- content (inherited storage, passed to parent constructor)
  - Type: dict
  - Shape: {"correlation_matrix": pd.DataFrame}
  - Invariant: content contains the correlation matrix under the "correlation_matrix" key.

- Additional inherited attributes (forwarded via ItemRenderer to Renderable)
  - anchor_id: Optional[str] (if supplied via kwargs)
  - classes: Optional[str] (if supplied via kwargs)
  - These are accepted via **kwargs and forwarded to parent constructors; CorrelationTable itself does not define or validate them.

Class invariants:
- item_type == "correlation_table"
- content is a dict with a "correlation_matrix" key whose value is intended to be a pandas DataFrame (no internal enforcement).

## Lifecycle:
Creation:
- Instantiate by calling the constructor with:
  - Required: name: str, correlation_matrix: pd.DataFrame
  - Optional: any additional keyword arguments supported by ItemRenderer / Renderable (commonly anchor_id and classes).
- Example signature shape: CorrelationTable(name: str, correlation_matrix: pd.DataFrame, **kwargs)

Usage:
- After creation, the instance is a complete item describing a correlation table but is abstract with respect to rendering.
- Typical usage patterns:
  1. Create instance and pass to a renderer dispatcher which selects a concrete renderer based on item_type.
  2. Alternatively, subclass CorrelationTable and override render() to produce the desired output directly.
- Required sequencing:
  - There is no special ordering required after construction; however, to obtain output you must call a concrete renderer's render method or call an overridden render() in a subclass. Calling CorrelationTable.render() directly will raise NotImplementedError.

Destruction / Cleanup:
- CorrelationTable holds references to a pandas DataFrame; it has no explicit cleanup behavior (no context manager or close method). Standard Python garbage collection applies.

## Method Map:
graph LR
    A[__init__(name, correlation_matrix, **kwargs)] --> B[item_type = "correlation_table"]
    A --> C[content = {"correlation_matrix": correlation_matrix}]
    B --> D[Inherited attributes set via ItemRenderer -> Renderable]
    E[__repr__()] --> F["returns 'CorrelationTable'"]
    G[render()] --> H["raises NotImplementedError (must be implemented by concrete renderer)"]

(Interpretation: construction sets up item_type and content; __repr__ returns the class name string; render() is abstract and must be implemented elsewhere.)

## Raises:
- __init__: No explicit exceptions are raised by CorrelationTable itself. Because CorrelationTable accepts the correlation_matrix argument and places it into a dict passed to super().__init__, any exceptions would come from parent constructors (not from CorrelationTable directly). CorrelationTable does not perform runtime type checking; passing an incorrect type will not raise here but may cause errors downstream.
- render: Always raises NotImplementedError in this base class. Concrete subclasses or external renderer implementations must provide rendering behavior to avoid this exception.

## Example (usage pattern, described in prose):
1. Prepare a pandas DataFrame `df` representing the correlation matrix.
2. Instantiate the item:
   - Create CorrelationTable with a descriptive name and the DataFrame. Optionally provide anchor_id/classes via kwargs to control presentation metadata.
3. Deliver the created CorrelationTable instance to a renderer manager or factory that inspects item_type ("correlation_table") and dispatches a concrete renderer to produce output (HTML/JSON/image).
4. If you prefer embedding rendering logic directly, define a subclass that overrides render() to return the desired representation. Calling render() on the subclass instance yields the output; calling render() on the base CorrelationTable will raise NotImplementedError.

This class is intentionally a structured container / contract for correlation-table presentation; implementors should focus on providing a concrete renderer that consumes the content["correlation_matrix"] DataFrame.

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.__init__` · *method*

## Summary:
Initializes the item as a presentation-ready correlation table by setting the item's type and storing the provided correlation matrix in the content payload, forwarding remaining presentation metadata to parent constructors.

## Description:
This constructor is called during the report assembly / presentation-item creation step. Typical callers are report builders, presentation layer code, or renderer factories that create items to later be dispatched to concrete renderers. It is invoked when an object representing a correlation matrix must be packaged as a standardized presentation item (i.e., before any rendering step).

The logic is implemented here so that the CorrelationTable class enforces the item contract (fixed item_type "correlation_table" and the specific content shape {"correlation_matrix": ...}) in a single place rather than duplicating that setup across renderers or higher-level factories. Keeping this initialization here centralizes the payload shape and ensures consistency for any renderer that consumes correlation-table items.

## Args:
    name (str):
        Human-readable identifier for the item. Passed through to the parent constructors and stored as part of the instance metadata (commonly used for anchors/labels). Required.
    correlation_matrix (pd.DataFrame):
        The correlation matrix to present. Stored in the content dictionary under the key "correlation_matrix". Callers are expected to pass a pandas DataFrame (annotated in the source as pd.DataFrame).
    **kwargs:
        Additional keyword arguments accepted by the parent ItemRenderer / Renderable constructors. Commonly supported keys include:
        - anchor_id (Optional[str]): presentation anchor identifier to be forwarded to the parent.
        - classes (Optional[str]): presentation CSS classes or similar metadata.
        Any other kwargs are forwarded exactly to the parent constructors; CorrelationTable does not inspect or validate them.

## Returns:
    None (constructors do not return a value). On successful completion, the instance is initialized with the item_type and content set as described below.

## Raises:
    Any exception raised by parent constructors (ItemRenderer.__init__ or its parent Renderable.__init__) may propagate.
    CorrelationTable.__init__ itself performs no explicit validation and does not raise exceptions based on argument types or values. Therefore:
    - Passing a non-DataFrame correlation_matrix does not raise here, but may cause downstream errors in renderers.

## State Changes:
Attributes READ:
    - None (the constructor does not read existing instance attributes).

Attributes WRITTEN:
    - self.item_type (str): set to the literal "correlation_table" by the parent ItemRenderer.__init__ call.
    - self.content (dict): set (via parent Renderable.__init__) to {"correlation_matrix": correlation_matrix}.
    - self.name (Optional[str]): forwarded to and stored by parent constructors if provided.
    - self.anchor_id (Optional[str]): set if provided in kwargs and accepted by parents.
    - self.classes (Optional[str]): set if provided in kwargs and accepted by parents.

Note: item_type and content are established by the combination of this constructor and the parent constructors it calls.

## Constraints:
Preconditions:
    - name must be provided as a str (the constructor signature requires it).
    - correlation_matrix is expected to be a pandas DataFrame (pd.DataFrame) by callers; this constructor does not enforce that.
    - Any kwargs intended for presentation metadata (e.g., anchor_id, classes) should follow the types expected by the parent constructors.

Postconditions:
    - self.item_type == "correlation_table"
    - self.content is a dict containing the key "correlation_matrix" whose value is the same object passed as correlation_matrix
    - Parent-managed metadata fields (such as self.name, self.anchor_id, self.classes) are set according to the provided arguments/kwargs
    - No additional validation or mutation of correlation_matrix is performed by this constructor

## Side Effects:
    - Mutates the new instance by setting attributes noted above.
    - No I/O operations, network calls, or other external side effects are performed.
    - Exceptions thrown by parent constructors (e.g., due to invalid kwargs) will propagate out of this constructor.

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.__repr__` · *method*

## Summary:
Returns a stable, human-readable identifier string for the object ("CorrelationTable") without inspecting or modifying the instance state.

## Description:
Known callers and context:
- Invoked implicitly by Python's built-in repr() when an instance is passed to repr(), print() in contexts that use the object's repr, f-strings using {!r}, logging calls that include the object, or any tooling that requests an object's representation (debuggers, interactive REPL).
- Can be called explicitly as instance.__repr__() though the canonical usage is via repr(instance) or implicitly by print/formatting.
- Typically used during debugging, logging, or when code wants a compact textual identifier for the renderer object within reporting pipelines.

Lifecycle stage:
- This method may be called at any point after object construction whenever a string representation is needed. Because the method returns a constant literal and does not access instance attributes, it is safe to call even during or immediately after __init__.

Why this logic is a separate method:
- Providing an explicit __repr__ ensures a consistent, short identifier for instances of CorrelationTable across logs, tests, and debugging output.
- Keeping it separate avoids duplicating representation logic elsewhere and aligns with Python's protocol for object string representations, enabling standard utilities (repr, logging, etc.) to produce meaningful output.

## Args:
None.

## Returns:
str — The literal string "CorrelationTable". This value is constant for all instances of the class and does not depend on internal state. There are no other possible return values or special-case strings.

## Raises:
None. The method body performs a simple literal return and does not raise exceptions.

## State Changes:
Attributes READ:
- None. The method does not access any self.<attr> attributes.

Attributes WRITTEN:
- None. The method does not modify self or any external objects.

## Constraints:
Preconditions:
- The object must be an instance of CorrelationTable (normal method dispatch). No other preconditions on internal state are required because the method does not read attributes.

Postconditions:
- No mutation occurs on the instance.
- The caller receives the string "CorrelationTable".

## Side Effects:
- None. There is no I/O, no external service interaction, and no mutation of objects outside self.

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.render` · *method*

## Summary:
Provides a render-time contract for producing a presentation-ready representation of the correlation matrix stored on the instance. Currently unimplemented (raises NotImplementedError). Implementers should produce a stable, renderable value (type Any) representing the stored pandas DataFrame without mutating the original data.

## Description:
Known callers and lifecycle:
- No direct callers were found in the inspected code snippets. Conceptually, this method is invoked during the presentation/report rendering stage of the pipeline for items of type "correlation_table".
- The method exists as a separated rendering hook so that data preparation (the correlation matrix) and presentation (HTML table, JSON-friendly structure, or a visualization payload) remain decoupled. This allows multiple renderer backends (HTML, JSON, notebook widgets, etc.) to implement format-specific logic without modifying data construction code.

Why this is a separate method:
- Keeps rendering concerns (formatting, rounding, table layout, HTML escaping, color/heatmap metadata) separate from data generation and storage.
- Allows subclasses or downstream renderer code to override presentation format without altering the stored content.

## Args:
- None.

## Returns:
- Any: a renderer-specific, presentation-ready object representing the correlation matrix.
  - Recommended/typical return value forms (implementer chooses one):
    - HTML string containing an HTML table of the correlation matrix (e.g., produced by pandas.DataFrame.to_html or equivalent).
    - A JSON-serializable dict describing the table and metadata, e.g. {"type": "table", "columns": [...], "data": [[...], ...], "format": {"float_precision": 3}}.
    - A framework-specific presentation object (for example, a plotting/visualization object) if the downstream consumer expects it.
  - Edge-case return values:
    - For an empty correlation matrix, return a semantically empty representation consistent with the chosen format (e.g., empty list, empty table HTML, or {"type":"empty"}). Avoid returning raw None unless the rest of the rendering pipeline treats None as "no output".

## Raises:
- NotImplementedError: the current implementation raises this unconditionally (method is intentionally abstract).
- Implemented versions SHOULD raise:
  - TypeError: if the stored correlation matrix is missing or is not a pandas DataFrame (see Preconditions).
  - ValueError: optionally if the DataFrame contains invalid data that prevents rendering (e.g., non-square matrix when a square correlation matrix is expected), depending on the chosen implementation policy.

## State Changes:
Attributes READ:
- self.content — specifically, the key "correlation_matrix" that CorrelationTable.__init__ stores in the content dict.
  - The constructor places the matrix in the content dict: {"correlation_matrix": correlation_matrix}.
- (Optionally) Any presentation-related config stored on the instance (e.g., self.name, self.classes) if the surrounding rendering framework exposes them; check the superclass for available fields before using them.

Attributes WRITTEN:
- None are required by contract. The implementation SHOULD be pure with respect to stored data (do not mutate self.content["correlation_matrix"]). Caching a derived presentation value on the instance (e.g., self._rendered) is permitted but must be documented and consistent across calls.

## Constraints:
Preconditions (required before calling):
- self.content exists and contains the key "correlation_matrix".
- The value at self.content["correlation_matrix"] should be a pandas DataFrame (pandas.DataFrame). This expectation is consistent with CorrelationTable.__init__ which accepts a DataFrame as correlation_matrix.
- The DataFrame should have meaningful index and column labels (matching variables) for human-readable presentation; if absent, the implementation should still produce a deterministic output (e.g., use integer positions).

Postconditions (guaranteed after a successful call):
- A renderable object of type Any is returned that accurately represents the input correlation matrix in the chosen presentation format.
- self.content is unchanged (unless the implementation documents and intentionally caches derived outputs).

## Side Effects:
- No I/O or network calls are required by the contract. Implementations should avoid performing file I/O, network access, or other external side effects.
- Memory allocation for formatted strings, arrays, or visualization objects is expected.
- Implementations may perform CPU work to format/round values, compute derived metadata (e.g., absolute-value masks), or generate style information (e.g., color scales).

## Implementation recipe (step-by-step guidance for reimplementation):
1. Retrieve the matrix:
   - matrix = self.content.get("correlation_matrix")
2. Validate:
   - If matrix is None, raise TypeError describing the missing key.
   - If not an instance of pandas.DataFrame, raise TypeError.
3. Handle empty matrices:
   - If matrix.empty is True, return an empty representation consistent with your chosen format (do not raise unless the pipeline expects errors).
4. Prepare formatting:
   - Decide on float precision (e.g., 2–4 decimal places) and how to represent NaNs or infinite values.
   - Optionally round or format numeric values for display only (do not modify the DataFrame in-place; operate on a copy).
5. Choose output format:
   - HTML path: convert to HTML using DataFrame.to_html with proper escaping and float format.
   - JSON/table path: convert index/columns to string labels and values to nested lists; include metadata (column labels, float precision).
   - Visualization path: create a heatmap payload or plotting object and return it (ensure the consumer knows how to render it).
6. Return the final representation:
   - Ensure the returned object matches the downstream renderer's expectations (e.g., JSON serializability if the report exporter writes JSON).

## Examples of decisions an implementer must make:
- Whether to return a plain HTML string, a JSON-serializable structure, or a framework-specific object.
- How to format floating-point numbers and handle NaNs.
- Whether to include additional metadata (variable names, value ranges, color mapping) in the returned object.

## Notes:
- The method is intentionally abstract in the current codebase. The documentation above spells out a clear contract so that different renderer implementations can be created consistently.
- When adding an implementation, keep rendering deterministic and side-effect-free with respect to the stored correlation matrix.

