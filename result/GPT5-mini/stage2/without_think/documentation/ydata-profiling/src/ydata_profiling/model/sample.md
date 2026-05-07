# `sample.py`

## `src.ydata_profiling.model.sample.Sample` · *class*

## Summary:
A lightweight Pydantic model that represents a named sample record with an identifier, an associated payload, and an optional caption.

## Description:
This class is a simple data container implemented as a Pydantic BaseModel. Instantiate it when you need to carry a single "sample" unit through the profiling pipeline or across APIs in a typed way (for example: storing the sample's id, its payload, a human-readable name, and an optional caption). It intentionally contains no behavior beyond what BaseModel provides (validation, serialization, etc.).

Known contextual notes:
- The repository also defines a different Report/UI class with the same short name (ydata_profiling.report.presentation.core.sample.Sample) which is a renderer for presentation. That renderer is distinct from this Pydantic model; do not confuse them.
- No specific factory function is required to create instances — call the constructor directly with the required fields.

## State:
- id (str)
  - Type: str
  - Role: Unique identifier for the sample.
  - Constraints: The class annotation declares a string; no additional checks (non-empty, format) are enforced by this model itself.

- data (T)
  - Type: T (module-level generic TypeVar)
  - Role: Payload associated with the sample. Can be any type; the annotation is a generic placeholder.
  - Constraints: The concrete type for T is not specified in this class definition. Runtime validation behavior for this field depends on how T is defined/bound elsewhere — if T is left as an unbound TypeVar, the field behaves effectively like an unannotated/Any field from a runtime-validation perspective.

- name (str)
  - Type: str
  - Role: Human-readable name for the sample.
  - Constraints: Declared as string; no further invariants enforced here.

- caption (Optional[str])
  - Type: Optional[str]
  - Role: Optional descriptive caption for the sample.
  - Default: None

Class invariants:
- All four attributes exist on an instance after construction (caption may be None).
- The declared types are used by Pydantic's validation on instantiation; this model does not enforce any additional semantic invariants (e.g., non-empty strings or unique constraints).

## Lifecycle:
- Creation:
  - Instantiate directly using the BaseModel constructor:
    Example: Sample(id="s1", data=<payload>, name="My sample", caption="optional text")
  - Required fields: id, data, name
  - Optional: caption (defaults to None)

- Usage:
  - Typical operations are reading fields, serializing to dict/JSON with BaseModel methods, or passing the object to other components.
  - There are no instance methods beyond those inherited from Pydantic's BaseModel in this class definition.

- Destruction / Cleanup:
  - No explicit cleanup is required. The class does not manage external resources or open handles. Standard Python garbage collection applies.

## Method Map:
flowchart TD
    A[Caller] --> B[Sample.__init__ (Pydantic BaseModel)]
    B --> C[Field validation (id, data, name, caption)]
    C --> D[Instance created]
    D --> E[Use: access attributes / .dict() / .json() / pass to other components]

(Note: the class has no custom methods; creation and validation are delegated to BaseModel machinery.)

## Raises:
- pydantic.ValidationError
  - Trigger: Raised by Pydantic during instantiation if provided values do not satisfy the annotated types (for id, name, caption) or if required fields are missing.
  - Notes: Because data is annotated with a TypeVar (T), validation behavior for data depends on how T is defined in module scope. If T is not concretely constrained, Pydantic may not validate the payload beyond general conversion rules.

## Example:
Create and use a Sample instance (illustrative):

- Create:
  Sample(id="sample-123", data={"col": [1, 2, 3]}, name="minimal sample")

- With caption:
  Sample(id="s-1", data=[1,2,3], name="example", caption="This is a short caption")

- Typical usage:
  s = Sample(id="s-1", data={"x": 1}, name="demo")
  # Access fields:
  s.id            # "s-1"
  s.data          # {"x": 1}
  s.dict()        # Pydantic-provided dict serialization
  s.json()        # Pydantic-provided JSON serialization

Implementation notes for re-creating this class:
- Subclass pydantic.v1.BaseModel and declare four fields with the annotated types shown above.
- Do not add custom validation or methods unless you intend to enforce additional invariants; doing so will change the class contract.

## `src.ydata_profiling.model.sample.get_sample` · *function*

## Summary:
Currently unimplemented; intended to produce a list of lightweight Sample records that represent representative rows and/or per-column examples extracted from the provided tabular input for profiling and reporting purposes.

## Description:
Current implementation status:
- The current function body raises NotImplementedError unconditionally. No runtime behavior is implemented in the shipped source.

Known callers within the provided repository snapshot:
- No direct callers of this function were verifiably found in the provided code snapshot. (Search for repository-wide call sites returned no results in the available context.)
- Note: The ProfileReport.get_sample method exists in the codebase but returns an internal description set and does not directly call this function in the provided snapshot.

Why this logic should be extracted into its own function:
- Sampling logic is a cross-cutting concern used by presentation/reporting code; keeping it centralized ensures consistent formatting of Sample objects, easier unit testing, and reuse across multiple report renderers or export formats.
- Separating sampling from rendering keeps responsibilities small: this function is responsible for choosing representative payloads and packaging them into the Sample Pydantic model; rendering and UI concerns remain elsewhere.

## Args:
    config (Settings):
        The profiling configuration container. Type is ydata_profiling.config.Settings (may be a simple object or Pydantic model in the codebase).
        - The shipped code does not read any attributes from it (function is unimplemented).
        - When reimplementing, treat config as a source of optional sampling parameters (see "Implementation guidance" below). Implementations MUST handle missing attributes by using sane defaults.

    df (T):
        Generic dataset input. The function signature uses a TypeVar T; the shipped code does not restrict or validate T.
        - Current behavior: no validation (function unimplemented).
        - Suggested supported concrete runtime types when implementing: pandas.DataFrame, pandas.Series, sequence of dict-like records, mapping of column->sequence, numpy.ndarray (records).
        - Implementations SHOULD validate runtime type and raise a TypeError for unsupported inputs.

## Returns:
    List[Sample]:
        - Current behavior: none (function raises NotImplementedError).
        - Intended contract (for a reimplementation): an ordered list of Sample Pydantic objects (see src.ydata_profiling.model.sample.Sample). Each Sample must include:
            - id (str): identifier for the sample record (e.g., "row:0", "col:age").
            - data (T): a compact, serializable payload (row dict, Series, small DataFrame slice, or a dict of examples).
            - name (str): a short human-readable label.
            - caption (Optional[str]): brief optional metadata (may be None).
        - The list may be empty when the input has no data or when sampling parameters request zero samples.

## Raises:
    NotImplementedError:
        - The current shipped implementation raises NotImplementedError unconditionally.

    (When reimplementing, the following are recommended:)
    TypeError:
        - Recommended to raise when df is of an unsupported runtime type (e.g., not DataFrame/Series/sequence/mapping).
    ValueError:
        - Recommended to raise when numeric sampling parameters read from config are negative.

## Constraints:
    Preconditions:
        - For the current code: none beyond passing two arguments; the function immediately raises NotImplementedError.
        - For a reimplementation:
            * config must be non-null (implementation should handle None defensively).
            * df should be non-null and contain data when row-based sampling is requested.

    Postconditions (for a reimplementation):
        - The function returns a list of Sample objects meeting the schema above.
        - Returned Sample.data objects are compact (not the full dataset) and suitable for inclusion in serialized reports.
        - It is strongly recommended that implementers ensure Sample.id values are unique within the returned list to help downstream consumers; note that the Sample Pydantic model itself does not enforce uniqueness.

## Side Effects:
    - Current function: none beyond raising NotImplementedError.
    - Recommended practice for reimplementation: avoid writing files, making network calls, or mutating the input df. Sampling should be a pure/functional operation on the input.

## Control Flow (suggested behavior for reimplementation):
flowchart TD
    Start[Start: get_sample(config, df)]
    Start --> CheckNotNull{config or df is None?}
    CheckNotNull -- Yes --> RaiseType[raise TypeError]
    CheckNotNull -- No --> DetectType[Detect runtime type of df]
    DetectType --> UnsupportedType{Unsupported type?}
    UnsupportedType -- Yes --> RaiseType2[raise TypeError]
    UnsupportedType -- No --> ReadConfig[Read sampling params from config (with defaults)]
    ReadConfig --> ValidateCounts{Any count < 0?}
    ValidateCounts -- Yes --> RaiseValue[raise ValueError]
    ValidateCounts -- No --> CollectHead[Collect head rows if head_count > 0]
    CollectHead --> CollectTail[Collect tail rows if tail_count > 0]
    CollectTail --> CollectRandom[Collect random rows if random_count > 0 (use seed if provided)]
    CollectRandom --> PerColumn[Collect per-column examples if requested]
    PerColumn --> Deduplicate[Deduplicate samples]
    Deduplicate --> BuildSamples[Construct Sample objects]
    BuildSamples --> Return[Return List[Sample]]
    Return --> End[End]

Notes: The above flowchart is a recommended algorithmic flow; it is not the current function behavior.

## Implementation guidance (detailed, to enable reimplementation):
- Defaults to consider (implementers should use these unless overridden via config):
    * head = 3
    * tail = 0
    * random = 0
    * per_column = 3
    * random_state = None
    * strategy = "mixed"  # options might include "rows", "per_column", "mixed"

- Validation:
    * Ensure counts are ints and >= 0; otherwise raise ValueError.
    * If df has fewer rows than requested head/tail/random counts, gracefully reduce counts to available rows.

- Sampling mechanics:
    * For pandas.DataFrame:
        - head: df.head(head).to_dict(orient="records")
        - tail: df.tail(tail).to_dict(orient="records")
        - random: df.drop(index=head_and_tail_indices).sample(n=random, random_state=seed).to_dict(orient="records")
    * For Series: treat as single-column DataFrame unless a different behavior is desired.
    * For sequence of records: use list slicing for head/tail and random.choice with sampling without replacement for random rows.
    * Per-column examples: for each column, collect up to per_column distinct values (prefer most frequent), represented as {"column": name, "examples": [...], "n_unique": int}.

- Sample construction:
    * id: deterministic within a call, for example f"row:{index}" or f"col:{colname}".
    * name: short label like "row: 0" or "col: age (examples)".
    * caption: optionally annotate with "head", "tail", "random", or metadata like "n_unique=42".
    * data: use primitive types and small containers (lists, dicts) to ease JSON serialization.

- Determinism:
    * If random_state/seed is provided, use it for all random sampling to make results reproducible.

## Examples (for a reimplemented version):
Example — DataFrame:
    import pandas as pd
    from ydata_profiling.model.sample import get_sample, Sample

    df = pd.DataFrame({"a": [1,2,3,4], "b": ["x","y","x","z"]})
    cfg = type("C", (), {})()
    cfg.sample_head_count = 2
    cfg.sample_random_count = 1
    cfg.sample_per_column_count = 2
    cfg.sample_random_state = 0

    # After reimplementing get_sample according to this spec:
    samples = get_sample(cfg, df)
    # samples -> List[Sample], e.g. head rows, one random row, and per-column example Samples

Caveat:
- The above examples and behavior are prescriptive guidance to enable reimplementation. The only verified fact in the shipped code is the function signature and that it raises NotImplementedError.

## `src.ydata_profiling.model.sample.get_custom_sample` · *function*

## Summary:
Creates a single-element list containing a Pydantic Sample model representing a user-supplied custom sample payload and normalizes missing metadata keys on the input dictionary.

## Description:
This helper constructs and returns one Sample instance (wrapped in a list) with id "custom" using the information found in the provided dictionary. It guarantees that the input dictionary contains the keys "name" and "caption" (inserting them with a None value if missing) before creating the Sample.

Known callers:
- No direct callers were discovered in a repository-wide static scan for references to this function. Typical usage is as a small factory helper inside profiling setup or pipeline code that needs to convert a user-provided mapping into the internal Sample model format for further processing or rendering.

Why this logic is a separate function:
- Encapsulates the small but important normalization and construction logic for a "custom" sample in one place so callers don't need to duplicate key normalization (ensuring "name" and "caption" exist) and Sample instantiation details. This isolates input normalization, makes unit testing easier, and centralizes the decision to use the fixed id "custom".

## Args:
    sample (dict):
        A mapping containing at least a "data" key. This dict may optionally include:
        - "name": human-readable name for the sample (expected type: str). If absent, the function inserts name: None.
        - "caption": optional descriptive caption for the sample (expected type: Optional[str]). If absent, the function inserts caption: None.
        Notes:
        - The function mutates this dict in-place to add missing "name" or "caption" keys.
        - The "data" value is passed directly to Sample.data; its validation is governed by the Sample model (see Raises).

## Returns:
    list[Sample]:
        A list containing exactly one Sample instance:
        - samples[0].id == "custom"
        - samples[0].data == sample["data"] (the value from the input dict)
        - samples[0].name == sample["name"] (possibly None)
        - samples[0].caption == sample["caption"] (possibly None)
    Edge cases:
        - The returned list is always length 1 when the function returns successfully.
        - The Sample instance is created by pydantic.BaseModel and may coerce or validate fields according to that model's annotations.

## Raises:
    KeyError:
        Trigger: If the input dict does not contain a "data" key, accessing sample["data"] raises KeyError.
    pydantic.ValidationError:
        Trigger: When Sample(...) is called, Pydantic validation may raise ValidationError if provided values violate the Sample model's type requirements (for example, if Sample.name is declared as str but None is provided, or data fails validation). Because this function sets missing "name" to None, a ValidationError is a possible outcome if the Sample model requires a non-None string for name.

## Constraints:
    Preconditions:
        - The caller must pass a dict-like object (mapping) that supports key access and assignment (sample["..."]).
        - The dict must include a "data" key whose value is acceptable to the Sample model.
    Postconditions:
        - On successful return, the original dict contains "name" and "caption" keys (if they were missing, they are now set to None).
        - The function returns a single-element list with a Sample instance having id "custom".

## Side Effects:
    - Mutates the provided sample dict in-place by inserting "name" and/or "caption" keys when they are absent.
    - No file, network, or other external I/O is performed.
    - No global state is modified.
    - May trigger Pydantic validation behavior (and its side effects such as raising ValidationError) when constructing the Sample model.

## Control Flow:
flowchart TD
    Start --> IsDict{input is a dict-like mapping?}
    IsDict -- No --> Raise[TypeError / downstream KeyError when accessing keys]
    IsDict -- Yes --> HasName{"'name' in sample?"}
    HasName -- No --> InsertName[set sample['name']=None]
    HasName -- Yes --> KeepName[leave sample['name']]
    HasCaption{"'caption' in sample?"} -->|No| InsertCaption[set sample['caption']=None]
    HasCaption -->|Yes| KeepCaption[leave sample['caption']]
    InsertName --> HasCaption
    KeepName --> HasCaption
    InsertCaption --> Construct[Call Sample(id='custom', data=sample['data'], name=sample['name'], caption=sample['caption'])]
    KeepCaption --> Construct
    Construct --> Validation{Pydantic validation passes?}
    Validation -- Yes --> Return[Return [Sample(...)]] 
    Validation -- No --> RaiseValidation[pydantic.ValidationError]

## Examples:
- Minimal valid input:
  Provide a mapping that contains "data". The function will add missing metadata, build a Sample, and return [Sample].
  Example (conceptual): input dict has {"data": {"col": [1,2,3]}}; after call the dict will also have "name": None and "caption": None; the return value is a one-element list whose Sample.data equals {"col":[1,2,3]} and id is "custom".

- With explicit metadata:
  If input dict already contains "name" and/or "caption", their values are preserved and passed into the Sample constructor.

- Error handling:
  If the "data" key is missing, the caller should catch KeyError and surface a descriptive error. If the Sample model enforces non-None name (or other stricter validation), the caller should catch pydantic.ValidationError and report an invalid sample payload back to the user.

Notes for implementers:
- Because the function mutates the passed-in dict, callers that must preserve the original dict should pass a shallow copy.
- If typed safety is desired, callers should ensure sample["name"] is a str (or adjust the Sample model to accept None for name).

