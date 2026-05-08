# `sample.py`

## `src.ydata_profiling.report.presentation.core.sample.Sample` · *class*

## Summary:
Represents a typed presentation item that wraps a pandas DataFrame sample together with an optional caption and presentation metadata; it is a concrete ItemRenderer subclass that encodes the semantic item_type "sample". It does not perform rendering itself — subclasses must implement render(), which consumes instance state.

## Description:
Sample is a light-weight adapter used by the reporting/presentation layer to carry a DataFrame (a small dataset sample) and an optional caption as the renderer's content payload. Typical callers are presentation factories, report builders, or higher-level orchestration code that create sample items to be rendered within a larger report (for example, a data preview table in a report section).

Motivation and responsibilities:
- Encapsulates the semantic type "sample" so downstream render orchestration can identify and handle samples uniformly.
- Stores the actual pandas DataFrame under the content dict (content["sample"]) and stores an optional caption under content["caption"].
- Forwards presentation metadata (e.g., name, anchor_id, classes) to the ItemRenderer / Renderable base classes via kwargs.
- Leaves rendering unspecified: render() raises NotImplementedError — concrete renderers (HTML/JSON/Table renderers) must implement the rendering logic that reads instance state (self.content).

Notes about imports and types:
- The constructor annotates the sample parameter as pd.DataFrame. When reimplementing, ensure you import pandas as pd (or change the annotation to pandas.DataFrame) so the annotation resolves correctly.

## State:
Attributes (inherited and set during initialization)

- item_type: str
  - Value: the literal string "sample" (set by the constructor call to the base class).
  - Invariant: remains "sample" for the lifetime of the instance.

- content: Dict[str, Any]
  - Keys set by Sample.__init__:
    - "sample": pandas.DataFrame
      - What: the DataFrame passed to the constructor.
      - Constraint: Sample does not validate the object type at runtime; callers should pass a pandas.DataFrame. If a non-DataFrame is given, downstream renderers that expect DataFrame operations will fail.
      - Invariant: content["sample"] is the exact object reference passed in (no defensive copy).
    - "caption": Optional[str] (may be None)
      - What: optional caption text describing the sample.
      - Behavior: always present as a key in content (value may be None).
  - Inherited behavior: Renderable.__init__ may also insert "name", "anchor_id", and "classes" into the same dict when corresponding arguments are provided (see lifecycle).

- name: str (inherited presentation metadata)
  - Provided via the required name parameter of Sample.__init__; stored by Renderable infrastructure (access via self.name property if present).
  - Invariant: Sample requires a name argument when constructing; Renderable expects name to be stored in content.

- anchor_id, classes: Optional[str] (inherited, may be set via kwargs)
  - Passed through from Sample.__init__ **kwargs; if present, Renderable.__init__ will set content["anchor_id"] and/or content["classes"].

Class invariants:
- self.item_type == "sample"
- self.content is the same dict object passed to the base constructor call (shared-mutability).
- content contains the keys "sample" and "caption" immediately after construction; "name"/"anchor_id"/"classes" exist in content only if provided via constructor arguments (name is required for Sample).

## Lifecycle:
Creation:
- Constructor signature to implement:
  - __init__(self, name: str, sample: pandas.DataFrame, caption: Optional[str] = None, **kwargs)
    - name (str): required human-friendly identifier stored as presentation metadata (forwarded to Renderable).
    - sample (pandas.DataFrame): required DataFrame to display/export.
    - caption (Optional[str]): optional caption text; default is None.
    - **kwargs: forwarded to ItemRenderer/Renderable (commonly anchor_id: Optional[str], classes: Optional[str]).
- The constructor must call the ItemRenderer constructor with:
  - item_type: the literal "sample"
  - content: a dict containing {"sample": sample, "caption": caption}
  - name=name
  - and forward **kwargs

Usage:
- After instantiation, callers may read metadata (guard access to anchor_id/classes if unsure they were provided) and should expect content["sample"] to be the original DataFrame.
- Typical sequence:
  1. Create a pandas.DataFrame containing the sample rows.
  2. Instantiate Sample(name="...", sample=df, caption="...")
  3. Either call sample_instance.render() directly (when using a concrete subclass) or pass the Sample instance to a rendering pipeline/orchestration component. In both cases, render() implementations take no parameters and must read from the instance state (self.content) to produce the representation.
  4. The concrete renderer accesses sample_instance.content["sample"] and produces a representation.

Rendering:
- Sample.render() is intentionally abstract and raises NotImplementedError by default. Concrete subclasses must override render() to produce the final representation. Implementations should not expect external parameters; they must rely on the instance's content and metadata.

Destruction / cleanup:
- Sample does not provide any cleanup hooks. If a subclass implements resources that require cleanup, it must provide its own close()/__exit__()/context-manager support.

## Method Map:
graph LR
  Ctor[Sample.__init__(name, sample, caption=None, **kwargs)] --> CallItem[ItemRenderer.__init__("sample", content_dict, name=name, **kwargs)]
  CallItem --> CallRenderable[Renderable.__init__(content_dict, name=name, anchor_id=..., classes=...)]
  InstanceReady[Sample instance ready] --> ReprCall[__repr__() -> "Sample"]
  InstanceReady --> RenderCall[render() -> NotImplementedError (override in subclass)]
  ConcreteSubclass[ConcreteSampleRenderer.render()] --> RenderCall
  Orchestration[Renderer orchestration] --> RenderCall

(Interpretation: constructor builds content dict and delegates to ItemRenderer/Renderable; __repr__ is trivial; render is abstract and should be implemented by concrete subclasses that read instance state. Rendering can be invoked directly or via a renderer orchestration component.)

## Raises:
- __init__:
  - No explicit exceptions raised by Sample.__init__ itself.
  - Possible runtime errors depending on arguments:
    - NameError at runtime if type annotation references pd.DataFrame but pandas was not aliased as pd in the module — when reimplementing, import pandas as pd or change the type annotation to pandas.DataFrame.
    - Type or attribute errors may arise later if content["sample"] is not a DataFrame but caller code or renderers assume DataFrame methods exist.
- render():
  - Raises NotImplementedError() by default to signal subclasses must implement rendering.
  - Concrete render implementations may raise domain-specific exceptions depending on rendering logic and content.

## Example:
from pandas import DataFrame  # or import pandas as pd and use pd.DataFrame

# Prepare a DataFrame sample
df = DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

# Instantiate a Sample item
sample_item = Sample(name="preview_1", sample=df, caption="First 3 rows")

# Inspect content (note: content is the same dict passed to base class)
assert sample_item.content["sample"] is df
assert sample_item.content["caption"] == "First 3 rows"

# __repr__ is simple
repr(sample_item)  # -> "Sample"

# Attempting to render on this class raises NotImplementedError;
# a concrete subclass must implement render() and will read instance state (self.content)
try:
    sample_item.render()
except NotImplementedError:
    print("render() must be implemented by a concrete renderer")

# Typical use: pass sample_item to a concrete renderer or call the concrete instance's render()
# which reads sample_item.content["sample"] and returns an HTML fragment, dict, or other representation.

### `src.ydata_profiling.report.presentation.core.sample.Sample.__init__` · *method*

## Summary:
Initializes a Sample presentation item by creating the content payload (holding a pandas DataFrame sample and optional caption) and registering the semantic item type "sample" on the instance; forwards display metadata (name, anchor_id, classes) to the parent initializer.

## Description:
This constructor is called when creating a presentation item that represents a small data sample (a pandas DataFrame) to be rendered in a report. Typical callers include presentation factories, report builders, and higher-level report construction code that assemble report sections and create concrete item renderers for display. It is invoked during the report-building lifecycle when an item representing a DataFrame sample needs to be packaged with presentation metadata before rendering.

The logic is encapsulated in its own method so that:
- The semantic item_type ("sample") and the content structure (a dict with the keys "sample" and "caption") are centralized and consistent across the codebase.
- Common metadata handling (name, anchor_id, classes) can be delegated to ItemRenderer/Renderable via super(), avoiding duplication of metadata wiring in every concrete item class.

## Args:
    name (str):
        Friendly name for the item. Passed through to the parent initializer and stored in the content (accessible via self.name / self.content["name"]) if provided.
    sample (pandas.DataFrame):
        The DataFrame instance that represents the sample data. Stored in the content under the key "sample".
    caption (Optional[str], default=None):
        Optional textual caption describing the sample. Stored in the content under the key "caption".
    **kwargs:
        Additional keyword arguments forwarded to the parent initializer (ItemRenderer / Renderable). Common/expected keys include anchor_id (str) and classes (str), which, when provided, are stored in content as "anchor_id" and "classes" respectively. Any other kwargs accepted by the parent initializer are also forwarded.

## Returns:
    None
    (This is an initializer; it does not return a value.)

## Raises:
    No exceptions are explicitly raised by this constructor.
    - Type errors or other exceptions may arise later if callers or downstream code assume types or keys that are not present (for example, accessing self.name when name was not provided will raise KeyError; ItemRenderer/Renderable may raise if they expect different content types).
    - There is no runtime validation here: incorrect types for sample or name are not checked and will not be flagged by this method.

## State Changes:
Attributes READ:
    - None from the instance (this initializer does not read existing instance attributes).

Attributes WRITTEN:
    - self.item_type (written by ItemRenderer.__init__): set to the string "sample".
    - self.content (written by Renderable.__init__ via ItemRenderer.__init__): assigned the dict {"sample": sample, "caption": caption} (the exact dict object created here).
    - content["sample"]: stores the provided pandas.DataFrame reference.
    - content["caption"]: stores the provided caption (possibly None).
    - content["name"] / content["anchor_id"] / content["classes"]: may be inserted or mutated by the parent initializer if name (explicit param) or corresponding kwargs were provided.

Notes:
    - The content dict used for self.content is a new dict literal created here; therefore the initializer does not mutate any caller-provided dict. However, it stores a reference to the provided DataFrame (sample), so external mutations to that DataFrame will be reflected inside self.content["sample"].

## Constraints:
Preconditions:
    - Callers should pass a string for name and a pandas.DataFrame for sample as indicated by the type annotations. The constructor itself does not enforce these types.
    - If callers plan to read metadata properties (self.name, self.anchor_id, self.classes) without checking, they must ensure those values were supplied; otherwise KeyError may occur when accessing the corresponding properties implemented by Renderable/ItemRenderer.

Postconditions:
    - After construction:
        * self.item_type == "sample"
        * self.content is a dict with at least the keys "sample" and "caption" (values possibly None for caption).
        * self.content["sample"] references the same DataFrame object passed in.
        * If name or other metadata kwargs were provided, they will be present in self.content under their conventional keys (e.g., "name", "anchor_id", "classes") as handled by the parent initializer.
    - The instance is ready to be used by rendering code that expects an ItemRenderer with item_type "sample" and content containing a DataFrame under "sample".

## Side Effects:
    - No I/O or external service calls are made.
    - Stores a reference to the provided pandas.DataFrame in the instance content; mutating that DataFrame outside the object will affect the stored content.
    - Forwards kwargs to the parent initializer which may mutate the content dict by adding metadata keys (e.g., "name", "anchor_id", "classes").
    - No external objects (other than the DataFrame reference) are mutated by this method.

### `src.ydata_profiling.report.presentation.core.sample.Sample.__repr__` · *method*

## Summary:
Returns a concise, fixed textual representation for the presentation Sample object without modifying its state.

## Description:
This special-method implementation provides the object representation used by Python's built-in repr()/interactive prompts and by any logging or debugging code that requests an object's repr. Typical callers are:
- The built-in repr() and str() (when Python falls back to repr for containers or developer tools).
- Logging, debugging, or diagnostics that render object instances.
- Any presentation-layer code that inspects renderer instances and expects a short identifier.

In the profiling presentation pipeline this method helps tools and developers quickly identify the object type when printing collections of renderers or recording simple textual summaries. It is separated into its own method (rather than inlined in other code) because:
- It implements the standard object representation protocol so Python and third-party tools can call it uniformly.
- Encapsulating the representation here keeps representation logic centralized and easy to customize if a different textual identifier is later desired.

## Args:
None

## Returns:
str: Always returns the literal string "Sample". There are no alternate return values or state-dependent variations.

## Raises:
None: This method is pure and does not raise exceptions.

## State Changes:
Attributes READ:
- None (the method does not access any self.<attr> attributes)

Attributes WRITTEN:
- None (the method does not modify self or any external object)

## Constraints:
Preconditions:
- self must be a valid instance of the presentation Sample class (i.e., the method is invoked on an instantiated object).

Postconditions:
- The object state is unchanged.
- The caller receives the exact string "Sample".

## Side Effects:
- None. No I/O, no external service calls, and no mutation of objects outside self.

## Notes / Usage:
- Because the method returns a constant literal, its output is stable across process runs and independent of instance data.
- To obtain this representation, call repr(instance) or rely on Python to use repr when rendering containers, e.g., printing a list containing the object will include "Sample".
- If you need a representation that includes instance-specific details (name, caption, etc.), override or extend this method to incorporate those attributes.

### `src.ydata_profiling.report.presentation.core.sample.Sample.render` · *method*

## Summary:
Defines the rendering contract for a presentation-layer sample item: produce a final representation (HTML fragment, JSON/dict, visualization object, or other application-specific output) for the DataFrame payload stored on the instance. The base method is abstract and raises NotImplementedError; concrete subclasses must implement it to produce the actual rendered output without mutating the stored content.

## Description:
Known callers and invocation context:
- Called by presentation factories, report builders, and rendering orchestration code at the "render" stage of report generation, after all ItemRenderer instances have been created and configured.
- Typical lifecycle stage: final presentation/rendering phase when the profiling/report object serializes or composes UI fragments for display or export.

Why this logic is a separate method:
- render() is intentionally abstract to allow polymorphic rendering strategies for different output formats (HTML, JSON, images, widgets) and to keep presentation concerns decoupled from data-holding logic. Keeping rendering in a method allows the report generation pipeline to treat all ItemRenderer instances uniformly by calling render() on each.

## Args:
- None (the method uses instance state; no explicit parameters).

## Returns:
- Any
  - Semantic contract: a concrete representation of the sample item suitable for inclusion in the final report. Acceptable forms include (but are not limited to) a string (e.g., HTML), a dict/json-serializable structure, a visualization spec object, or a library-specific widget object.
  - Edge-case returns:
    - Implementations may return an empty string, empty dict, or None to denote "nothing to display" — if so, callers should document and handle these cases consistently. Prefer returning a consistent empty-type (e.g., {}) rather than None if the rest of the pipeline expects a serializable fragment.

## Raises:
- NotImplementedError
  - Condition: The base implementation raises NotImplementedError unconditionally. Concrete subclasses must override this method; otherwise calling Sample.render() will raise this exception.
- Recommended/expected errors for implementations (implementors should raise these where applicable):
  - TypeError: if the stored content does not contain the expected pandas.DataFrame under content["sample"] (e.g., if content["sample"] is not a pandas.DataFrame).
  - ValueError: if the DataFrame is present but in a state that cannot be rendered (implementation-specific, e.g., entirely empty when the renderer cannot meaningfully present empty tables).
  - Any domain-specific exceptions if the renderer performs I/O (file operations, image generation) and those operations fail.

## State Changes:
Attributes READ:
- self.content (the dict provided at construction)
- self.content["sample"] (expected to be a pandas.DataFrame)
- self.content.get("caption") (optional str or None)
- self.name (presentation name stored on content via parent class initialization)
- self.item_type (should be "sample" per this subclass's constructor)

Attributes WRITTEN:
- None required by the contract. Implementations SHOULD NOT mutate self.content in-place (including keys "sample" or "caption") unless explicitly intended and documented, because self.content is the canonical payload referenced elsewhere.

Note: the current base implementation does not read or write any attributes because it immediately raises NotImplementedError. The above lists express the intended/readable fields that an implementation will typically consult.

## Constraints:
Preconditions:
- The instance must have been initialized by Sample.__init__, so:
  - self.item_type == "sample"
  - self.content is a dict containing at least the key "sample"
  - self.content["sample"] should be a pandas.DataFrame (or the implementation must explicitly accept/convert other types)
- Callers should only call render() on concrete subclasses that override this method; calling the base implementation will raise NotImplementedError.

Postconditions:
- After a successful call, a renderable representation (as declared in Returns) is returned.
- Implementations should leave self.content unchanged unless documented otherwise.
- Implementations that allocate external resources (temporary files, image buffers) must either return safe handle objects or perform cleanup before returning.

## Side Effects:
- Implementations may perform I/O (writing image files, saving assets, calling visualization libraries that create temporary files). If so, they must document:
  - what files/locations are written,
  - whether they clean up temporary files,
  - and whether the returned representation contains references (paths/URLs) to those artifacts.
- Implementations might use significant CPU/memory when rendering large DataFrames; callers should be aware of potential performance and consider pre-filtering samples when necessary.
- Network calls or calls to external services are not part of the contract but are permitted if documented; such calls may raise network-related exceptions.

## Implementation guidance (for developers implementing a concrete render):
- Validate input early:
  - Check that "sample" exists in self.content; if missing, raise KeyError or a clearer TypeError with a helpful message.
  - Prefer explicit type checks: if not isinstance(self.content["sample"], pandas.DataFrame): raise TypeError("Sample.render expected a pandas.DataFrame in content['sample']")
- Behavior expectations:
  - Do not mutate self.content unless the mutation is intentional and documented.
  - For empty DataFrames, either return a minimal, well-documented "empty" representation (e.g., an empty table HTML string or {"empty": True}) or raise ValueError if emptiness is considered an error in your renderer.
  - Ensure the returned object is serializable if the renderer's output will be exported to JSON.
- Keep render() side-effect declarations explicit: document if it writes files, creates images, or relies on external libraries that require additional dependencies.
- Example implementation notes (descriptive, not code):
  - A simple HTML renderer might read the DataFrame from content["sample"], convert it to an HTML table fragment, optionally include caption (content.get("caption")) and name as metadata, and return the concatenated HTML string.
  - A renderer producing a JSON fragment could convert the DataFrame to records via DataFrame.to_dict(orient="records"), package it together with caption/name in a dict and return that dict.

## Summary of expected contract for callers and implementors:
- Callers: invoke render() on concrete Sample subclasses during the presentation/rendering stage and be prepared to handle Any-typed outputs. Do not call render() on the abstract base Sample class.
- Implementors: override render(), validate content["sample"] is a pandas.DataFrame (or clearly document alternative accepted types), produce a stable renderable object, avoid mutating instance state, and document any side-effects (I/O, external services).

