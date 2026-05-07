# `table.py`

## `src.ydata_profiling.report.presentation.core.table.Table` · *class*

## Summary:
Represents a presentation-layer table item: a small, typed renderer object that groups a sequence of rows with presentation style and optional name/caption metadata. It is a lightweight container intended to be subclassed to implement concrete rendering.

## Description:
Table provides the common data/metadata shape used for table-like report items. It packages:
- rows: the row data (application-specific sequence),
- style: a Style instance that describes visual choices (colors/theme/logo), and
- optional name and caption metadata.

Table itself does not produce output; its render() method deliberately raises NotImplementedError. Instantiate Table only when you intend to subclass it (or when a higher-level factory supplies a concrete renderer that overrides render()). Typical callers:
- presentation factories and report builders that construct table items before handing them to format-specific renderers,
- concrete table renderer subclasses that accept a Table instance or subclass instance and implement render() to emit HTML/JSON/visualization specs.

Motivation / responsibility boundary:
- Centralizes the "table" semantic type and its required payload shape so downstream code can rely on content["rows"] and content["style"] being present.
- Leaves formatting and output responsibilities to concrete subclasses or rendering layers; Table enforces payload structure but not output format.

## State:
Public attributes (inherited behavior from ItemRenderer / Renderable apply):

- item_type (str)
  - Value: "table" (set by Table.__init__ via ItemRenderer)
  - Invariant: remains "table" for all Table instances.

- content (dict-like)
  - Keys established by Table.__init__:
    - "rows": Sequence (the provided rows parameter)
        - Type hint: typing.Sequence
        - Expected semantics: an ordered collection of row values (each row can be any application-specific structure: tuple, list, dict, etc.)
        - Note: typing.Sequence is only an annotation; Table does not enforce the interface at runtime.
    - "style": Style
        - Type: ydata_profiling.config.Style (a pydantic model)
        - Semantics/constraints: Style enforces its own validation (pydantic). Accessing style.primary_color may raise IndexError if style.primary_colors == [].
    - "name": Optional[str]
        - Stored verbatim in content as provided (possibly None).
        - Access via ItemRenderer.name property will return content["name"] (may be None); accessing name only raises KeyError if the "name" key is absent — Table always writes the key (even if value is None).
    - "caption": Optional[str]
        - Stored verbatim in content under "caption" (possibly None).
  - Invariant: content is the exact dict passed to ItemRenderer.__init__ (shared-reference semantics). Mutating the dict externally or by other code will be visible on the Table instance.

- __repr__():
  - Returns the literal string "Table". Useful for debugging/logging.

Notes on __init__ parameters:
- rows (Sequence): required positional (or keyword) argument; no runtime type check performed by Table itself.
- style (Style): required; relies on Style being a validated pydantic object (validation occurs at Style construction).
- name (Optional[str]): default None. Table places this value into content["name"] (it does not pass it to ItemRenderer as the separate name parameter).
- caption (Optional[str]): default None. Placed into content["caption"].
- **kwargs: forwarded to ItemRenderer.__init__ (e.g., anchor_id or classes if the caller provides them). These keyword arguments are not interpreted by Table but passed upward.

Class invariants:
- self.item_type == "table"
- self.content contains keys "rows", "style", "name", and "caption" after construction (keys present, values may be None).
- render() is abstract in Table and must be implemented by subclasses before producing output.

## Lifecycle:
Creation:
- Instantiate with required arguments:
  - rows: a Sequence of row data
  - style: a Style instance
  - optionally name and caption
  - any additional kwargs are forwarded to the ItemRenderer/Renderable constructor (e.g., anchor_id, classes).
- Typical call: Table(rows=..., style=..., name="...", caption="...") — but note: Table.render() is not implemented, so a raw Table instance is not directly useful for rendering.

Usage:
- Intended pattern:
  1. Construct a Table (often done by a factory or report builder).
  2. Pass the Table (or a subclass instance that implements render()) to rendering code that calls render().
  3. Concrete subclasses implement render() to produce the final representation (HTML fragment, JSON, visualization spec, etc.).
- Ordering constraints:
  - No special sequencing other than constructing before calling render().
  - No context-manager protocol or explicit destruction required by Table itself.

Destruction / cleanup:
- Table manages no external resources. No close() or context-manager cleanup is required. Subclasses that allocate resources must perform their own cleanup.

## Method Map:
graph TD
  A[Table.__init__(rows, style, name=None, caption=None, **kwargs)] --> B[ItemRenderer.__init__("table", content_dict, **kwargs)]
  B --> C[Renderable.__init__ assigns/merges metadata if kwargs include anchor_id/classes]
  A --> D[content keys set: rows, style, name, caption]
  E[Caller] -->|calls| F[instance.render()]
  F -->|NotImplemented| G[NotImplementedError] 
  H[repr(instance)] -->|returns| I["Table"]

(Interpretation: Table.__init__ builds the content dict and delegates to ItemRenderer.__init__; callers should invoke render() on a concrete subclass — calling render() on Table will raise NotImplementedError. __repr__ returns "Table".)

## Raises:
- __init__:
  - Table.__init__ itself does not explicitly raise exceptions.
  - Indirect/possible runtime exceptions:
    - TypeError / AttributeError if callers pass objects that do not conform to expected usage (e.g., content consumers expect dict methods).
    - Any exceptions raised by Style construction (pydantic.ValidationError) will occur earlier when the caller constructs the Style instance.
- render():
  - Raises NotImplementedError by design in Table. Subclasses must override render() to produce output.

## Example:
- Typical instantiation:
  - Provide a sequence of rows and a Style instance. After construction, content holds the provided values under the keys "rows", "style", "name", and "caption".
  - Because Table.render() is not implemented, to obtain output you must use or create a concrete renderer that overrides render().

- Usage sketch (described in prose):
  1) A report builder constructs a Style (validated by Style).
  2) The builder creates a Table with rows and the Style, e.g., rows could be a list of tuples or dicts representing table rows.
  3) The builder passes the Table instance to a concrete renderer (or instantiates a concrete Table subclass) which implements render() and returns the final fragment (HTML/JSON/etc.).
  4) No explicit cleanup is required for Table.

Practical notes and best practices:
- Prefer passing a fresh dict to other APIs if you want to avoid shared-mutation surprises — Table stores its payload in content and retains the reference.
- Because Table injects name and caption into content (even if None), code that checks for the presence of a "name" key should account for None values (KeyError will not be raised for name/caption presence when created via Table).
- Implementers of concrete renderers should validate or coerce rows into the expected internal representation before rendering to avoid runtime errors for unusual sequences (e.g., generators, empty sequences).

### `src.ydata_profiling.report.presentation.core.table.Table.__init__` · *method*

## Summary:
Initializes a Table presentation item by packaging the provided rows, style, and optional metadata into the renderer's content payload and delegating to the ItemRenderer constructor; as a result, the instance's semantic item_type and content payload are populated.

## Description:
Known callers and context:
- Presentation factories, report builders, and higher-level code that assemble report items call this during report construction to create a typed table payload. This occurs during the "presentation assembly" phase of report generation, before any format-specific rendering (HTML/JSON/etc.).
- Concrete table renderer subclasses (or rendering orchestration code) may also call this when constructing subclass instances that implement render().

Why this logic is a separate method:
- Centralizes the "table" semantic item_type and enforces a consistent content shape ("rows", "style", "name", "caption") consumed by downstream renderers.
- Keeps payload construction separate from rendering so format-specific rendering code can rely on a uniform input structure; it also avoids duplicating payload-shaping logic across renderers.

## Args:
    rows (Sequence):
        - Description: The table's row data. Each element represents a row; row element structure (tuple, list, dict, etc.) is application-specific.
        - Type: typing.Sequence
        - Allowed values: any sequence (including empty); generators are allowed but may be consumed by downstream code that expects indexable/iterable sequences.
        - Default: no default; required positional/keyword argument.

    style (Style):
        - Description: Presentation style object describing visual choices (colors, themes, etc.). Expected to be an instance of ydata_profiling.config.Style (a pydantic model).
        - Type: Style
        - Allowed values: a valid Style instance. Style validation happens when the Style is constructed (not in this __init__).
        - Default: required.

    name (Optional[str], optional):
        - Description: Optional friendly name or identifier for the table. Stored in the content payload under the "name" key.
        - Type: Optional[str]
        - Allowed values: any string or None.
        - Default: None.

    caption (Optional[str], optional):
        - Description: Optional caption text for the table. Stored in the content payload under the "caption" key.
        - Type: Optional[str]
        - Allowed values: any string or None.
        - Default: None.

    **kwargs:
        - Description: Arbitrary keyword arguments forwarded to ItemRenderer / Renderable base class (commonly used keys include anchor_id and classes).
        - Recognized/typical forwarded keys:
            - anchor_id (Optional[str]) — an anchor identifier that Renderable may store in content["anchor_id"].
            - classes (Optional[str]) — CSS classes that Renderable may store in content["classes"].
        - Behavior: Any kwargs are forwarded unchanged to super().__init__.

## Returns:
    None
    - As a Python constructor, it does not return a value; instead it initializes the instance state (see State Changes).
    - Edge cases: If parent constructors raise, no instance is returned.

## Raises:
    - The method itself does not explicitly raise exceptions.
    - It may propagate exceptions raised by:
        - ItemRenderer or Renderable constructors invoked via super().__init__ (TypeError for invalid kwargs, or other runtime errors).
        - Validation errors originating from the Style object (pydantic.ValidationError) if the caller constructed an invalid Style prior to calling this constructor.
    - Note: calling render() on a raw Table instance raises NotImplementedError (Table is intended to be subclassed and does not implement render()) — this is unrelated to __init__ but relevant to post-construction use.

## State Changes:
Attributes READ:
    - None. This constructor does not read any existing self.<attr> fields.

Attributes WRITTEN / Established:
    - self.item_type
        - Value set to the literal string "table" via the ItemRenderer base constructor.
    - self.content
        - A dict is created in this __init__ and passed to ItemRenderer; after construction, self.content references that dict.
        - The dict contains at least the keys:
            - "rows": the provided rows argument
            - "style": the provided Style instance
            - "name": the provided name argument (may be None)
            - "caption": the provided caption argument (may be None)
        - Additionally, Renderable.__init__ (via ItemRenderer) may insert keys such as "anchor_id" or "classes" into the same content dict if those values are supplied through forwarded kwargs.

## Constraints:
Preconditions:
    - The caller should provide:
        - rows that are a Sequence or behave like a sequence for downstream consumers.
        - style that is an instance of Style (validity enforced when Style was constructed).
    - No runtime type enforcement is performed here; incorrect types may lead to downstream runtime errors.

Postconditions:
    - After successful construction:
        - self.item_type == "table"
        - self.content is a dict containing keys "rows", "style", "name", and "caption" (their values may be None except for "rows" and "style", which were provided).
        - Metadata forwarded via kwargs (e.g., anchor_id, classes) may also be present in self.content if Renderable handled them.
        - The instance is ready to be passed to renderers, but calling render() on Table itself will raise NotImplementedError unless overridden.

## Side Effects:
    - No I/O or network access is performed.
    - Mutations:
        - The newly created content dict is stored on the instance (self.content). Because this dict is a fresh dict created inside the constructor, the constructor does not mutate caller-owned dictionaries, but it stores references to the provided rows and style objects; mutating those objects elsewhere will be reflected in self.content.
        - Forwarded kwargs may trigger Renderable.__init__ to write additional keys into self.content (e.g., "anchor_id" or "classes").
    - No external services or global state is modified by this constructor.

### `src.ydata_profiling.report.presentation.core.table.Table.__repr__` · *method*

## Summary:
Return a concise, stable string representation for the Table instance used for debugging and display purposes.

## Description:
This method provides the object's representation as a short, human-readable class identifier. It is invoked by the Python runtime whenever a representation of the object is requested, for example via the built-in repr() function, when printing containers that include the object, in debugger displays, or when explicit logging/diagnostics call repr(instance). It is typically executed during inspection or logging phases of the presentation/reporting pipeline (e.g., while building or debugging report components), not during core rendering logic.

Keeping this logic in its own __repr__ method ensures a single, consistent textual representation for the class that is independent from render() or other behavior. It is intentionally trivial and separated from render() because __repr__ is meant for short-identifying text, whereas render() produces full presentation output (and is not implemented in this base class).

## Args:
    None

## Returns:
    str: The constant string "Table". This value is always returned and there are no alternative return values or modes.

## Raises:
    None

## State Changes:
    Attributes READ:
        - None. This method does not access any self.<attr> attributes.

    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self is an instantiated object of the Table class (normal Python object semantics). There are no other preconditions; the method does not rely on object initialization of any attributes.

    Postconditions:
        - No state on the object is changed.
        - Calling repr(instance) (or equivalent) will return the string "Table".

## Side Effects:
    - None. This method performs no I/O, no external calls, and does not mutate objects other than returning a string.

### `src.ydata_profiling.report.presentation.core.table.Table.render` · *method*

## Summary:
Defines the abstract rendering contract for a table presentation item; the base implementation does not render and always raises NotImplementedError — subclasses must override this method to produce the final representation (HTML, JSON, widget, etc.).

## Description:
- Known callers and lifecycle stage:
    - Called by presentation factories, report builders, and higher-level render orchestration code during the final rendering/materialization pass of a report. A Table instance is created earlier in the report assembly pipeline (holding semantic data) and render() is invoked when producing the concrete output.
- Why this is a separate method:
    - Rendering is format- and backend-specific. Keeping render() as a dedicated, overridable method separates the semantic data model (rows, name, caption, style) from how that data is turned into the final representation. This enables multiple renderer implementations to consume the same Table objects and produce different outputs without changing the model.

## Args:
- None. All input is provided via the instance state that was set in Table.__init__ (see Preconditions).

## Returns:
- Any
    - The concrete renderer must return a final representation appropriate for the target output format:
        - str (e.g., HTML fragment)
        - dict (JSON-serializable structure)
        - framework-specific widget/object
    - The base implementation never returns (it raises NotImplementedError).
    - Implementations may return None only if their contract explicitly allows a no-op representation; otherwise callers should expect a non-None representation.

## Raises:
- NotImplementedError
    - Exact condition: the Table.render method defined on this class always raises NotImplementedError. Any attempt to call this base implementation will raise.
- Implementation-specific exceptions
    - Concrete renderers may raise other exceptions (TypeError, ValueError, IOError, etc.) depending on validation, I/O, or external library failures; such exceptions must be documented by the concrete implementation.

## State Changes:
- Attributes READ by base method:
    - None. The base Table.render does not access or mutate instance state; it only raises.
- Attributes WRITTEN by base method:
    - None.
- Attributes EXPECTED to be available for concrete implementations to READ (set by Table.__init__):
    - self.item_type (str): set to "table" by ItemRenderer.__init__.
    - self.content (dict): the content dict passed during construction. Keys guaranteed to exist (may have None values):
        - "rows" -> Sequence: the table rows passed to Table.__init__.
        - "name" -> Optional[str]: name provided at construction; may be None.
        - "caption" -> Optional[str]: caption provided at construction; may be None.
        - "style" -> Style: Style instance passed at construction.
- Attributes that implementations MAY WRITE:
    - None by default. Implementations that cache rendered output or attach metadata to self.content must document those mutations.

## Constraints:
- Preconditions (caller/implementer responsibilities before calling or implementing):
    - Table instances are constructed with content containing the keys "rows", "name", "caption", and "style". Concrete renderers may assume these keys exist but must handle None values for "name" and "caption".
    - self.content["rows"] should be a Sequence (e.g., list/tuple). Renderers should validate the shape of rows (e.g., list of lists vs list of dicts) according to their expectations and raise a clear exception if the format is invalid.
    - self.content["style"] should be a ydata_profiling.config.Style-compatible object. Renderers that rely on style attributes should validate them as needed.
- Postconditions (what implementers must guarantee after successful execution):
    - The overridden render() must return the final rendered representation (type and invariants are renderer-specific) and must not raise NotImplementedError.
    - If the implementation mutates instance state (e.g., caches the rendered output on the object), it must document that behavior and the mutated attributes.

## Side Effects:
- Base implementation: none beyond raising NotImplementedError.
- Possible side effects of concrete implementations (must be explicitly documented by those implementations):
    - I/O operations (writing files, saving images)
    - External library calls or subprocesses
    - Network calls (uploads)
    - Mutations to self.content or other objects passed into the constructor
    - Registration of static assets in global registries
    - Logging

## Implementation guidance for concrete renderers:
1. Do not call super().render() — the base raises NotImplementedError.
2. Typical implementation steps:
    - rows = self.content["rows"]  # expect a Sequence
    - name = self.content["name"]  # may be None
    - caption = self.content["caption"]  # may be None
    - style = self.content["style"]  # Style instance
    - Validate rows' shape and element types. If invalid, raise a clear exception (TypeError/ValueError).
    - Build the representation appropriate for your backend (HTML string, JSON dict, widget).
    - Optionally attach metadata or cache results on self (explicitly document any such mutation).
    - Return the representation.
3. Handle edge cases:
    - Empty rows: render a valid empty-table representation instead of failing.
    - None name/caption: omit or render empty metadata fields according to the output format.
    - Non-sequence rows: raise TypeError with a descriptive message.
4. Document all implementation-specific exceptions and side effects so callers can handle them.

## Examples (conceptual, describe only):
- HTML renderer: return an HTML string containing a <table> element constructed from rows; include <caption> if caption is not None.
- JSON renderer: return {"type": "table", "name": name, "caption": caption, "rows": rows, "style": style_serialized}.
- Widget renderer: return a framework-specific table widget constructed from rows and style.

