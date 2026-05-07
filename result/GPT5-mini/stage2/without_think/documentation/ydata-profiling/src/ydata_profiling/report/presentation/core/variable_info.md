# `variable_info.py`

## `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo` · *class*

## Summary:
Represents a presentation-layer item that bundles metadata about a single dataset variable (identifier, name, semantic type, alerts, and description) into a structured payload for downstream rendering. It is a typed ItemRenderer with item_type fixed to "variable_info".

## Description:
VariableInfo is a lightweight presentation object used by report/presentation factories and report builders to encapsulate descriptive metadata about one data variable for rendering in reports (HTML, JSON, visualization specs, etc.). It does not itself implement rendering — render() is deliberately abstract (raises NotImplementedError) and must be implemented by a concrete renderer in the presentation layer that knows how to convert the payload into the final representation.

Typical callers
- Presentation factories or report builders that prepare the content for a variable (e.g., variable summary blocks, detail panels).
- Higher-level report orchestration code which collects multiple VariableInfo instances and calls their render() implementations (via specific concrete subclasses) to produce the report output.

Motivation and responsibility boundary
- Responsibility: carry a consistent, named payload describing a single variable and provide a stable semantic item_type ("variable_info") so presentation code can dispatch on item type.
- Boundary: does not decide rendering format or implement rendering logic; it is purely a content/metadata container with a stable semantic identity.

## State:
Attributes (inherited and set during initialization)

- item_type: str
  - Value: always "variable_info"
  - Invariant: set by the constructor and not changed by VariableInfo.

- content: dict
  - Structure: keys and values produced exactly as passed to ItemRenderer.__init__:
      - "anchor_id": str
      - "var_name": str
      - "description": str
      - "var_type": str
      - "alerts": List[Alert]
      - "style": Style
  - Behavior: The same dict reference passed to ItemRenderer; callers should be aware of shared-mutability if they reuse the dict object elsewhere.

- __repr__() -> str
  - Returns the exact string "VariableInfo". This is deterministic and relied on by logging/debug code that identifies instances.

Constructor parameters (and caller constraints)
- anchor_id (str): identifier used as an in-page anchor or stable ID for the variable block. Caller must supply a string; no validation is performed.
- var_name (str): display name or column name of the variable. Caller must supply a string.
- var_type (str): semantic type identifier for the variable (e.g., "Numeric", "Categorical", or project-specific type tags). The class does not enforce a fixed vocabulary; callers should use consistent tags expected by renderers.
- alerts (List[Alert]): a list of Alert objects relevant to the variable (may be empty). The constructor accepts the list as-is; it does not clone or validate element types at runtime.
- description (str): textual description, summary, or tooltip content for the variable. May be empty.
- style (Style): a Style object (from ydata_profiling.config) conveying presentation preferences. Must be provided by the caller; VariableInfo does not validate properties of Style.
- **kwargs: forwarded to ItemRenderer (and ultimately to Renderable); typical kwargs include optional metadata slots like name or classes. These are inserted into content by Renderable.__init__ when provided.

Class invariants
- After construction:
  - self.item_type == "variable_info"
  - self.content is a dict and contains the keys "anchor_id", "var_name", "description", "var_type", "alerts", and "style" with the values provided to the constructor.
  - No other invariants are enforced by VariableInfo itself.

## Lifecycle:
Creation
- Instantiate by calling VariableInfo(anchor_id, var_name, var_type, alerts, description, style, **kwargs).
- The constructor forwards a content dict to ItemRenderer.__init__ along with the fixed item_type "variable_info".

Usage
- Typical sequence:
  1. Presentation factory constructs VariableInfo with the appropriate metadata.
  2. The factory (or report builder) passes the instance to presentation code that knows how to render items with item_type "variable_info".
  3. A concrete subclass of VariableInfo (or a separate renderer that accepts VariableInfo.content) implements render() and produces the final output (HTML fragment, JSON fragment, visualization spec, etc.).
- There is no required ordering of other methods; callers normally only call render() after construction.

Destruction / cleanup
- VariableInfo does not allocate external resources and does not implement any cleanup protocol (no close(), __enter__/__exit__, or similar). If subclasses hold resources, they must provide their own cleanup.

## Method Map:
graph LR
  Caller[Presentation factory / report builder] --> Init[VariableInfo.__init__]
  Init --> ItemInit[ItemRenderer.__init__]
  ItemInit --> RenderableInit[Renderable.__init__ (assigns self.content and optional metadata)]
  Instance[VariableInfo instance ready] --> RenderCall[ConcreteSubclass.render() or external renderer consumes instance.content]
  Instance --> ReprCall[__repr__() -> "VariableInfo"]
  RenderCall --> Output[final presentation output (HTML/JSON/spec)]

(Note: render() in VariableInfo raises NotImplementedError; a concrete subclass or an external renderer must provide the final conversion.)

## Raises:
- __init__: No explicit exceptions are raised by VariableInfo itself. Because the constructor accepts and stores provided values without validation, errors typically arise later if callers pass incompatible objects (for example, a non-Style object where a Style instance is expected) or if downstream renderers expect specific types.
- render(): always raises NotImplementedError in this class. Callers must not call VariableInfo.render() directly unless they expect this exception; instead, use a concrete renderer implementation.

## Example:
1) Creating a VariableInfo instance (typical factory usage):
   - Provide the required metadata and optional kwargs for metadata insertion:
     instance = VariableInfo(
         anchor_id="var-age",
         var_name="age",
         var_type="Numeric",
         alerts=[alert_obj1, alert_obj2],
         description="Age of the respondent in years.",
         style=style_obj,
         name="Age variable block"
     )
   - At this point:
     - instance.item_type == "variable_info"
     - instance.content["var_name"] == "age"
     - instance.content["alerts"] references the same list passed in.

2) Rendering (expected pattern):
   - VariableInfo.render() in this base class raises NotImplementedError.
   - Implement a concrete subclass (or a renderer that accepts instance.content) that overrides render() to produce the output. Example responsibilities for render():
     - Read metadata from self.content (anchor_id, var_name, var_type, alerts, description, style).
     - Format or transform these into the final representation (e.g., an HTML snippet or JSON fragment).
     - Return the final object (type Any — typically a string for HTML, a dict for a JSON fragment, or another serializable structure).

3) Handling alerts and style:
   - The alerts list is supplied verbatim; renderers should iterate and format Alert objects according to presentation conventions.
   - The style object conveys visual preferences; renderers decide which Style fields to apply.

Implementation notes for re-implementers
- Maintain the exact content keys used by this class so existing renderers that expect those keys continue to function.
- Preserve item_type == "variable_info".
- __repr__ returns the exact string "VariableInfo"; preserve this behavior for deterministic identification of instances.
- Do not call render() on this base class; provide a concrete implementation in a subclass or separate renderer.

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.__init__` · *method*

## Summary:
Initialize the VariableInfo presentation item by storing a semantic item type ("variable_info") and a content payload containing per-variable metadata (anchor id, variable name, type, description, alerts, and style) on the instance so it is ready for rendering by the presentation layer.

## Description:
This constructor is called when a VariableInfo renderable item is created as part of assembling a profiling report's per-variable section. Typical callers are presentation factories, report builders, or higher-level render orchestration code that construct report fragments for each variable (for example: variable summary panels, headers, or sidebars) during report generation.

The logic is separated into its own constructor because VariableInfo is a concrete ItemRenderer subclass that must:
- fix the semantic item_type to "variable_info" so downstream renderers can recognize it, and
- provide a content dict payload with a consistent set of keys used by templates or rendering components (anchor_id, var_name, description, var_type, alerts, style).

Keeping this initialization in the constructor centralizes the content layout and ensures every VariableInfo instance presents the same minimal payload shape to renderers.

## Args:
    anchor_id (str):
        Anchor identifier for HTML fragments or internal linking. Expected to be a short identifier (e.g., "var-age"). No runtime validation is performed here.
    var_name (str):
        Human-facing variable name (column name) shown in the UI.
    var_type (str):
        String name of the variable's semantic type (e.g., "Numeric", "Categorical"). Caller supplies this classification.
    alerts (List[Alert]):
        A list of Alert objects associated with the variable (may be empty). Alerts originate from the analysis stage and are carried into the presentation layer.
    description (str):
        Optional textual description or summary for the variable. May be an empty string.
    style (Style):
        Presentation style object (from ydata_profiling.config.Style) describing visual configuration to be used when rendering this item.
    **kwargs:
        Arbitrary keyword arguments forwarded to the parent ItemRenderer / Renderable constructor. Common keys include name, anchor_id, and classes; Renderable.__init__ may insert these keys into the content dict if provided. Any kwargs are passed through unchanged.

## Returns:
    None
    Constructor; does not return a value. After the call, the instance is initialized and ready for render() by the concrete renderer.

## Raises:
    None explicitly.
    The constructor itself does not raise. Indirect errors can occur later if callers misuse the instance (for example, accessing a metadata property that the underlying content dict lacks will raise KeyError). Also, wrong argument types may cause downstream errors but are not validated here.

## State Changes:
    Attributes READ:
        None from self are read by this method.

    Attributes WRITTEN:
        self.item_type
            - Set to the string "variable_info" by ItemRenderer.__init__.
        self.content
            - Set to the dict reference passed to ItemRenderer.__init__. That dict will contain at least the keys:
                - "anchor_id": anchor_id
                - "var_name": var_name
                - "description": description
                - "var_type": var_type
                - "alerts": alerts
                - "style": style
            - Note: Renderable.__init__ (invoked by ItemRenderer.__init__) may additionally insert or overwrite keys "name", "anchor_id", and "classes" into content if such values are present in the forwarded **kwargs. Because the same dict object is retained, callers should be aware of shared-mutation semantics.

## Constraints:
    Preconditions:
        - The caller should supply values with the types declared in the signature:
            anchor_id: str
            var_name: str
            var_type: str
            alerts: List[Alert]
            description: str
            style: Style
        - No argument validation is performed by this constructor; callers must ensure that alerts is an iterable/list of Alert objects and style is a valid Style instance.
    Postconditions:
        - After return, self.item_type == "variable_info".
        - After return, self.content is a dict containing the provided keys mapping to the provided argument values (see Attributes WRITTEN).
        - Any kwargs provided to the constructor have been forwarded to the ItemRenderer/Renderable initializer and may have modified content (inserting "name", "anchor_id", "classes").

## Side Effects:
    - No I/O, network, or filesystem operations are performed.
    - No external services are called.
    - The method mutates the instance by setting item_type and content. The content dict retained by the instance is the exact dict passed during construction; because Renderable.__init__ may also mutate that dict, callers should avoid passing in a shared mutable dict unless that is intentional.

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.__repr__` · *method*

## Summary:
Returns a stable, human-readable identifier string for the instance, used when the object is converted to a string representation.

## Description:
This method provides the object's canonical string representation and is invoked by Python built-ins and tooling that request an object's representation (for example, builtins.repr(), logging/formatting when using {!r}, and interactive shells or debuggers that display objects). It exists as a dedicated method so the class can control its printed identity consistently across all such contexts instead of relying on the default object representation provided by the runtime.

## Args:
    None

## Returns:
    str: Always returns the exact string "VariableInfo". There are no conditional branches — every invocation returns this constant.

## Raises:
    None

## State Changes:
    Attributes READ:
        None
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - No particular state or attribute values are required; the method does not inspect or depend on self.
    Postconditions:
        - Calling this method does not mutate the object.
        - The return value is guaranteed to be the constant string "VariableInfo".

## Side Effects:
    - None. The method performs no I/O, does not call external services, and does not modify objects outside self.

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.render` · *method*

## Summary:
Abstract rendering hook that must be overridden by concrete subclasses to produce a presentation artifact for a variable; the base implementation always raises NotImplementedError and performs no state changes.

## Description:
- Role and lifecycle: This method is called during the presentation/rendering stage of the reporting pipeline on an instantiated VariableInfo item. ItemRenderer (the base class) documents that callers are typically presentation factories, report builders, or render orchestration code that create renderable items and then call their render() methods.
- Why a separate method: render() is the designated polymorphic extension point for converting the variable-level payload (prepared at construction) into a final representation (HTML, JSON, visualization spec, widget, etc.). Keeping rendering logic in a concrete override lets different formats be implemented without changing the data-construction code.
- How data is provided to renderers: VariableInfo.__init__ builds a content mapping with keys anchor_id, var_name, var_type, alerts, description, and style and forwards that dict to ItemRenderer.__init__. ItemRenderer (via Renderable) stores that dict on self.content; Renderable.__init__ may also insert keys "name", "anchor_id", and "classes" into that same dict when those constructor arguments are provided.

## Args:
- None. The method is parameterless; implementations should use instance data available on self.content.

## Returns:
- Any: concrete subclasses decide the return type appropriate to their output format (commonly str for HTML fragments, dict for JSON fragments, or displayable objects for notebook renderers). Returning None is allowed only if the implementation intentionally performs direct side-effectful output (discouraged).
- Note: the base method does not return because it raises NotImplementedError.

## Raises:
- NotImplementedError: unconditionally raised by this base implementation. The condition is simply that VariableInfo.render() on this class was invoked (no override present).
- Concrete overrides may raise other exceptions; such exceptions must be documented by those subclasses.

## State Changes:
Attributes READ:
- Base implementation: none (raises immediately and performs no reads).
- Subclass implementations: should read the payload prepared at construction from self.content. VariableInfo.__init__ populates the content dict with the following keys and values:
    - "anchor_id": str
    - "var_name": str
    - "var_type": str
    - "alerts": List[Alert]
    - "description": str
    - "style": Style
  Access to these keys is done via self.content["key"] or via any accessors provided by ItemRenderer/Renderable.

Attributes WRITTEN:
- Base implementation: none.
- Subclasses: may write derived or cached attributes on the instance (for example, self._rendered_output) but must document any such attributes; ItemRenderer guarantees self.content is the same dict object passed at construction and thus is shared-mutability sensitive.

## Constraints:
Preconditions:
- The VariableInfo instance must have been constructed via its __init__ so the content dict contains the keys listed above.
- Implementations should not assume keys like "name", "anchor_id", or "classes" exist on self.content unless those metadata arguments were supplied during construction (Renderable only inserts them when provided).
- Implementations should validate or defensively handle unexpected types (for example, alerts not being a list) if they require stronger invariants.

Postconditions:
- Base implementation: raises NotImplementedError and leaves object state unchanged.
- Well-behaved subclass implementation: returns a presentation artifact consistent with its format and, unless documented by the subclass, leaves the constructor-provided payload in self.content unchanged.

## Side Effects:
- Base implementation: none (only raises).
- Subclass implementations (typical, must be documented by those subclasses):
    - Should prefer returning an in-memory artifact (no external I/O).
    - May call template engines or helper utilities (in-process calls).
    - Should avoid performing implicit external I/O (writing files, emitting notebook outputs) unless that behavior is explicitly required and documented.

## Implementation guidance for subclass authors:
- Override render() and read input data from self.content using the keys listed above.
- Do not rely on undocumented attribute names on self; rely on the ItemRenderer/Renderable contract that self.content is the payload dict.
- Handle missing or empty fields gracefully (empty alerts list, empty description).
- Return a consistent type for the renderer family (e.g., all HTML renderers return str).
- Document any new attributes added to self, any side effects, and any exceptions the override may raise.

