# `summarizer.py`

## `src.ydata_profiling.model.summarizer.BaseSummarizer` · *class*

## Summary:
A minimal summarizer adapter that delegates summarization work to the inherited Handler pipeline and returns the pipeline's "summary" element (third item) as a dict.

## Description:
BaseSummarizer is a thin adapter class built on top of Handler. Its sole public helper is summarize(config, series, dtype), which forwards the provided arguments to the Handler.dispatch mechanism and extracts the pipeline-produced summary.

Typical scenario:
- A profiling system constructs a Handler (or a Handler-derived class) with per-Visions-type pipelines that, when invoked for a type, return a 3-tuple whose third element is a dictionary representing the computed summary for the given series.
- Callers that need only the final summary dictionary (and not the other tuple items returned by the pipeline) use BaseSummarizer.summarize as a convenience to run the pipeline and obtain the third element.

Motivation / responsibility boundary:
- Keeps summarization call sites simple by encapsulating the details of how the Handler pipeline is invoked (stringifying the dtype, passing metadata) and by returning only the summary payload.
- Does not implement or alter any summarization algorithms — those live in pipeline callables registered with the Handler. BaseSummarizer enforces the precondition that the pipeline's return value is indexable and that the third element is a dict.

Known callers / factories:
- Profiling code that constructs a summarizer/handler from a collection of summary algorithms and a VisionsTypeset and then uses summarize to obtain per-column summaries.
- Any code that previously used Handler.handle directly but wants the summary dict only.

## State:
BaseSummarizer defines no new instance attributes. It inherits the public Handler state:

- mapping: Dict[str, List[Callable]]
    - Type: dict mapping stringified Visions type identifiers to ordered lists of callables (pipelines).
    - Invariants:
        * Each value is a sequence (list-like) of callables.
        * After Handler construction, mapping entries for derived types are prepended with ancestor handlers according to the typeset.base_graph DAG.
- typeset: VisionsTypeset
    - Type: VisionsTypeset
    - Invariant: typeset.base_graph must be a DAG (topological sortable).

Preconditions specific to summarize:
- The pipeline associated with str(dtype) must be callable via Handler.handle(config, series, metadata) and must return an iterable/sequence/two-or-more-element object such that indexing/unpacking into three values is valid.
- The third return element (index 2) must be a dict representing the summary. If the pipeline returns a different shape or type, summarize will raise a standard Python unpacking error or a downstream TypeError.

Class invariants:
- Instances must remain valid Handler objects (mapping and typeset consistent). summarize does not mutate Handler state.

## Lifecycle:
Creation:
- Instantiate by calling the constructor inherited from Handler.
- Required constructor arguments (from Handler):
    - mapping: Dict[str, List[Callable]] — mapping for pipelines keyed by str(Visions type).
    - typeset: VisionsTypeset — used by Handler to complete DAG propagation.
- No BaseSummarizer-specific constructor parameters or initialization steps.

Usage:
- Typical usage pattern:
    1. Construct the Handler-backed summarizer (BaseSummarizer(mapping, typeset)).
    2. For each column/series to profile, call summarize(config, series, dtype).
- summarize behavior:
    - It calls self.handle(str(dtype), config, series, {"type": str(dtype)}).
    - It unpacks the returned value into three variables and returns the third (summary).
- Sequencing: There is no required ordering of multiple summarize calls. summarize is stateless with respect to Handler mapping (aside from side effects of pipeline callables, if any).

Destruction / cleanup:
- No cleanup responsibilities. BaseSummarizer does not open resources and does not implement context-management. Discard the object as usual; rely on Python garbage collection.

## Method Map:
graph TD
    A[summarize(config, series, dtype)] --> B[self.handle(str(dtype), config, series, {"type": str(dtype)})]
    B --> C[composed pipeline (via Handler.compose)]
    C --> D[pipeline callables execute -> produce a result R]
    D --> E[unpack R into (_, _, summary)]
    E --> F[return summary (dict)]

Notes:
- The pipeline (C) is the Handler-constructed list of callables for the given dtype (including ancestor handlers); its concrete behavior and side effects depend on the registered functions.

## Raises:
BaseSummarizer.summarize does not raise its own bespoke exceptions but propagates errors from its dependencies. Common failure modes:

- ValueError / TypeError (unpacking error)
    - Trigger: The return value from self.handle(...) is not an iterable of length >= 3 (e.g., returns a single dict), causing unpacking "_, _, summary" to fail.
- Any exception raised by Handler.handle or by pipeline callables:
    - Examples include TypeError, AttributeError, ValueError, RuntimeError raised by pipeline logic.
    - Handler construction-time errors (KeyError, networkx.NetworkXUnfeasible, TypeError) can be raised earlier when the handler/Handler-derived object was instantiated rather than at summarize time.
- Note: summarize itself calls str(dtype) and constructs simple metadata; str(dtype) itself should not raise for valid Visions type objects. If dtype is malformed, str(dtype) may still succeed but pipeline lookup may return [] causing composition to run an empty pipeline — in that case Handler.handle behavior determines the resulting exception or return.

## Example:
- Purpose: run the summarizer pipeline for a pandas Series and get the summary dict.

Steps:
1. Ensure you have a Handler-compatible mapping and a VisionsTypeset:
    - mapping should include an entry for str(dtype) and for any ancestor types expected by the typeset's base_graph.
    - The pipeline functions registered for the type must return a 3-tuple (first two elements can be any values; third must be the summary dict).
2. Instantiate the summarizer (inherited constructor from Handler):
    - summarizer = BaseSummarizer(mapping, typeset)
3. Call summarize:
    - summary_dict = summarizer.summarize(config, series, dtype)
4. Use summary_dict — a dictionary describing properties of the series (counts, dtype-specific statistics, etc.)

Edge-case example:
- If the pipeline returns only the dict (not a 3-tuple), the call will raise an unpacking error. Ensure pipeline authors return a consistent triple if BaseSummarizer.summarize is used.

### `src.ydata_profiling.model.summarizer.BaseSummarizer.summarize` · *method*

## Summary:
Execute the per-type handler pipeline for the given Visions dtype against the provided pandas Series and return the pipeline-produced summary dictionary (the third element produced by the pipeline). This method does not modify the summarizer's internal state.

## Description:
- Known callers / context:
    - Invoked by the profiling/summarization stage that constructs a description for a single column/Series after the variable's Visions type has been determined. Typical callers include the profiler orchestration code that builds BaseDescription objects and other reporting components which need the summary dict for a variable.
    - Lifecycle stage: called during the summarization phase of profiling, once config, the column data, and the detected dtype are known.

- Why this is a separate method:
    - Centralizes the convention that the handler pipeline returns a 3-tuple (or 3-element iterable) whose third element is the summary dict. Encapsulating the call and extraction avoids repeating the unpacking logic at many call sites and isolates the mapping from Visions dtype to pipeline invocation in one place.

## Args:
    config (Settings):
        - Profiling configuration controlling algorithmic behavior, thresholds, toggles, etc.
        - Required; no default.
    series (pd.Series):
        - The pandas Series (column) to summarize. May contain missing values.
        - Required; no default.
    dtype (Type[VisionsBaseType]):
        - The Visions type class identifying which per-type pipeline to run. The method uses str(dtype) to look up the pipeline in the Handler's mapping.
        - Required; must be a VisionsBaseType subclass present (ideally) in the Handler mapping.

## Returns:
    dict:
        - The value bound to the name summary after unpacking the iterable returned by self.handle(...). In canonical pipelines this is a dict describing the Series (statistics, histograms, type-specific metadata).
        - Edge cases:
            * If the pipeline returns a non-dict as its third element, that value is returned unchanged.
            * If the pipeline returns a value that is not an iterable or an iterable with a length other than exactly 3, unpacking fails (see Raises).

## Raises:
    ValueError:
        - Trigger: if the value returned by self.handle(...) is an iterable with length not equal to 3, the statement "_, _, summary = ..." raises ValueError:
            * "not enough values to unpack" when fewer than 3 items are returned.
            * "too many values to unpack (expected 3)" when more than 3 items are returned.
    TypeError:
        - Trigger: if self.handle(...) returns a non-iterable (e.g., None) or an object that cannot be unpacked into three variables, Python raises TypeError.
    Any exception propagated from self.handle(...):
        - The method does not catch exceptions raised during handler pipeline composition or execution (for example, TypeError, AttributeError, ValueError, RuntimeError raised within pipeline callables or compose). These exceptions will propagate to the caller.

## State Changes:
- Attributes READ:
    - self.handle (the Handler.handle method is accessed and invoked)
- Attributes WRITTEN:
    - None. The method does not mutate self.

## Constraints:
- Preconditions:
    - self must have a working Handler.handle method (BaseSummarizer inherits Handler). Handler should have been initialized correctly with a mapping and typeset earlier.
    - dtype should be a VisionsBaseType subclass so that str(dtype) corresponds to the intended handler mapping key; otherwise the pipeline's behavior (and its return value shape) may be unexpected.
    - series must be a pandas Series (annotated as pd.Series in the signature).
    - config must be a Settings instance expected by the pipeline functions.
- Postconditions:
    - On successful return, self is unchanged.
    - The returned object is exactly the third element from the iterable returned by self.handle(str(dtype), config, series, {"type": str(dtype)}).

## Side Effects:
- The method itself performs no I/O or external calls.
- Indirect side effects may occur if the pipeline functions invoked by Handler.handle perform I/O, mutate the series or other passed-in objects, or change external state (logging, caching). Such side effects originate from the pipeline functions and are not handled by summarize.

## `src.ydata_profiling.model.summarizer.PandasProfilingSummarizer` · *class*

## Summary:
A concrete summarizer that registers pandas-profiling's default per-Visions-type summary algorithms and delegates execution to the BaseSummarizer/Handler pipeline to produce per-column summary dictionaries.

## Description:
PandasProfilingSummarizer is the ready-to-use summarizer used by ydata-profiling to analyze pandas Series according to Visions-inferred types. On construction it builds an internal mapping from stringified Visions types (e.g., "Numeric", "Text", "DateTime", etc.) to ordered lists of summary functions (the describe_* algorithms imported in this module). It then delegates the heavy lifting to the inherited Handler-based pipeline via BaseSummarizer, so callers can obtain the pipeline-produced summary dict using BaseSummarizer.summarize(config, series, dtype).

Use cases:
- Instantiate when building the profiling pipeline for a DataFrame; profiling code/factories in the library create this summarizer with a VisionsTypeset and then call summarize for each column.
- Preferred when you want the standard set of summary algorithms shipped with pandas-profiling without manually assembling the mapping.

Responsibility boundary:
- This class only constructs and registers the canonical summary_map and forwards all runtime behavior to BaseSummarizer/Handler. It does not implement the summary algorithms themselves; those are the describe_* callables imported from model.summary_algorithms.

## State:
This class does not declare new persistent attributes itself; it relies on the Handler/BaseSummarizer state established during construction.

Inherited public state (populated by the super call):
- mapping: Dict[str, List[Callable]]
    - Type: dict mapping stringified Visions type identifiers to ordered lists of callables (pipelines).
    - Valid keys (as created by this class): "Unsupported", "Numeric", "DateTime", "Text", "Categorical", "Boolean", "URL", "Path", "File", "Image", "TimeSeries".
    - Each value is a list of callables drawn from the module's describe_* functions, for example:
        - "Numeric": [describe_numeric_1d]
        - "Text": [describe_text_1d]
        - "Unsupported": [describe_counts, describe_generic, describe_supported]
        - (and similarly for other keys listed above)
    - Invariant: Each mapping value must be an ordered iterable of callables that conform to the pipeline contract expected by Handler (callables applied in sequence and returning the agreed pipeline result form).
- typeset: VisionsTypeset
    - Type: VisionsTypeset
    - Invariant: typeset.base_graph must be a DAG (topologically sortable) so that Handler can propagate ancestor pipelines correctly.

Constructor (__init__) parameters:
- typeset (VisionsTypeset) — required. The VisionsTypeset describing type relationships used by Handler when merging pipelines across ancestor types.
- *args, **kwargs — forwarded to the parent constructor (Handler/BaseSummarizer). These are typically unused by callers but are accepted and passed through.

Class invariants:
- After construction, the Handler invariants must hold: mapping entries correspond to valid Visions type names (as produced by str(dtype)), mapping values are lists of callables, and the typeset forms a valid type graph. The summarizer makes no runtime modifications to mapping; pipelines themselves may have side effects depending on their implementations.

## Lifecycle:
Creation:
- Instantiate by calling PandasProfilingSummarizer(typeset, *args, **kwargs).
    - The initializer constructs the canonical summary_map (mapping Visions type names to the library's describe_* functions) and calls the parent constructor to register the map and validate/propagate it against the provided typeset.

Usage:
- Typical sequence:
    1. Create a VisionsTypeset instance that reflects the project's type hierarchy.
    2. Create the summarizer: PandasProfilingSummarizer(typeset).
    3. For each column to profile, call BaseSummarizer.summarize(config, series, dtype) (inherited). summarize will:
        - Convert the dtype to a string (str(dtype)).
        - Invoke the Handler/Handler-composed pipeline for that string type with the provided config and series.
        - Unpack the pipeline result and return the third element (the summary dict).
- There is no required explicit ordering of summarize calls; calls are independent (except for any pipeline-internal side effects).

Destruction / cleanup:
- No special cleanup. The class does not open external resources and does not implement context management. Dispose of the instance normally; rely on Python garbage collection.

## Method Map:
graph TD
    Init[PandasProfilingSummarizer.__init__(typeset,*args,**kwargs)] --> BuildMap[construct summary_map dict]
    BuildMap --> SuperInit[call BaseSummarizer/Handler.__init__(summary_map, typeset, ...)]
    SuperInit --> HandlerCompose[Handler validates/propagates mapping using typeset]
    HandlerCompose --> Ready[Instance ready to summarize]
    Ready --> Summarize[BaseSummarizer.summarize(config, series, dtype)]
    Summarize --> Handle[Handler.handle(str(dtype), config, series, {"type":str(dtype)})]
    Handle --> Pipeline[composed pipeline callables execute in order]
    Pipeline --> Return[Pipeline returns a (a, b, summary) tuple]
    Return --> Extract[BaseSummarizer extracts and returns summary (third element)]

(Notes: The class itself only implements __init__; summarization and pipeline execution use inherited methods.)

## Raises:
Exceptions that can be raised during __init__ (trigger conditions):
- networkx.NetworkXUnfeasible
    - Trigger: typeset.base_graph is not a DAG or Handler cannot compute a valid topological propagation when validating/propagating mapping.
- TypeError
    - Trigger: mapping or typeset have an incompatible type or the Handler constructor rejects the provided arguments (e.g., non-callable values in mapping lists).
- KeyError
    - Trigger: inconsistencies uncovered by Handler when resolving type names or required mappings for ancestor propagation.
- Any exception raised by Handler.__init__ or by operations that validate/compose the mapping (these are propagated unchanged).

Runtime exceptions (from summarization, not from __init__):
- When summarize is called (inherited behavior), callers may see:
    - ValueError / TypeError (unpacking error) if a pipeline returns a result that cannot be unpacked into the expected tuple of three elements.
    - Any exceptions raised by individual describe_* pipeline functions (TypeError, AttributeError, ValueError, etc.), propagated from the pipeline.

## Example:
- Typical usage pattern (prose):
    1. Prepare a VisionsTypeset describing your type relationships.
    2. Instantiate the summarizer: create PandasProfilingSummarizer(typeset). The instance will register the built-in describe_* algorithms for types such as Numeric, Text, DateTime, Categorical, Boolean, URL, Path, File, Image, TimeSeries, and Unsupported.
    3. For each pandas Series to profile, call the inherited summarize(config, series, dtype) method to obtain a summary dictionary (the third element produced by the pipeline).
    4. Use the returned dict in the profile report generation.

- Edge notes:
    - If you need a different set or order of algorithms for a given Visions type, either build a custom mapping and instantiate a Handler/BaseSummarizer directly, or subclass/modify the mapping before calling super.
    - Ensure the supplied VisionsTypeset matches the type names used as keys (str(dtype)) so Handler resolution finds the correct pipelines.

### `src.ydata_profiling.model.summarizer.PandasProfilingSummarizer.__init__` · *method*

## Summary:
Constructs a local mapping from string type categories to lists of 1D summary callables and forwards that mapping plus the provided VisionsTypeset to the superclass constructor.

## Description:
The constructor creates a local variable named summary_map that maps recognized data-type category names (strings) to lists of 1-dimensional summary functions imported from ydata_profiling.model.summary_algorithms. Immediately after building this dictionary it calls the superclass constructor with the exact arguments (summary_map, typeset, *args, **kwargs), forwarding any additional positional and keyword arguments unchanged.

Known callers and lifecycle context:
- Direct callsites are not present in this file; this method is invoked implicitly whenever the PandasProfilingSummarizer class is instantiated (i.e., any code that executes PandasProfilingSummarizer(...)).
- Typical lifecycle stage: object construction time — this runs during the initialization phase of a summarizer object before any summarization methods execute. Specific pipeline callsites (factory functions, higher-level profiling initializers) are outside the scope of this file and therefore not enumerated here.

Why this logic is its own method:
- The mapping of vision-type names to concrete summary algorithms is configuration specific to this subclass. Placing it in __init__ centralizes configuration that must be available to the superclass immediately during construction and keeps the subclass self-contained and easy to override in future subclasses.
- Keeping the mapping creation here avoids duplicating the mapping elsewhere and makes it straightforward for subclasses to alter or extend the mapping by overriding __init__.

## Args:
    typeset (visions.VisionsTypeset):
        A VisionsTypeset instance (annotated type). This object is forwarded to the superclass and is expected to provide the type-detection functionality required by the profiling system.
    *args:
        Additional positional arguments forwarded unchanged to the superclass constructor.
    **kwargs:
        Additional keyword arguments forwarded unchanged to the superclass constructor.

## Returns:
    None
    - As an initializer, it does not return a value; its observable effect is the constructed object (final instance initialization is performed by the invoked superclass constructor).

## Raises:
    - This method does not explicitly raise exceptions. Any exception raised during the call to super().__init__(summary_map, typeset, *args, **kwargs) is propagated to the caller.

## State Changes:
Attributes READ:
    - None on self within this method body.

Attributes WRITTEN:
    - None on self within this method body. The method creates a local summary_map and then delegates to the superclass constructor; any instance attributes created or modified are the responsibility of the superclass constructor.

## Constraints:
Preconditions:
    - The typeset argument should be compatible with the profiling system (annotated as VisionsTypeset). The method does not validate the typeset; it simply forwards it.
    - The callable names referenced (describe_numeric_1d, describe_text_1d, etc.) must be importable in the module context; they are referenced to build the mapping but not executed here.

Postconditions:
    - If construction completes without raising, the superclass constructor has been invoked with the constructed mapping and the provided typeset (plus any forwarded args/kwargs). The resulting instance is initialized according to the superclass's behavior.

## Side Effects:
    - No I/O, file, or network operations are performed by this method.
    - No summary callables are executed during initialization; only callable references are stored in the mapping and forwarded to the superclass.
    - Any instance attribute assignment or other side effects occur inside the superclass constructor invoked here, not in this method.

## Mapping constructed:
    - "Unsupported" → [describe_counts, describe_generic, describe_supported]
    - "Numeric"     → [describe_numeric_1d]
    - "DateTime"    → [describe_date_1d]
    - "Text"        → [describe_text_1d]
    - "Categorical" → [describe_categorical_1d]
    - "Boolean"     → [describe_boolean_1d]
    - "URL"         → [describe_url_1d]
    - "Path"        → [describe_path_1d]
    - "File"        → [describe_file_1d]
    - "Image"       → [describe_image_1d]
    - "TimeSeries"  → [describe_timeseries_1d]

## `src.ydata_profiling.model.summarizer.format_summary` · *function*

## Summary:
Recursively convert a BaseDescription dataclass or a mapping of summary values into a plain Python dict that uses JSON-friendly primitives (native dicts, lists, and scalars) by expanding dataclasses, pandas Series, and a specific numpy-array histogram tuple pattern.

## Description:
This function normalizes summary objects produced by the profiling pipeline so they are safe to serialize or include in reports. It is the centralized place to:
- Convert a BaseDescription dataclass snapshot into a mapping (via dataclasses.asdict).
- Replace any pandas.Series values with plain dicts (index -> value).
- Convert histogram-like tuples of two numpy.ndarray objects into {"counts": [...], "bin_edges": [...]}.

Known callers and context:
- The function is intended to be invoked right before serialization/report generation or when packaging a column/feature summary for output (for example: report builders, JSON exporters, or APIs that return feature descriptions). No specific call-sites were enumerated from the scanned source for this document; implementers should search the repository for direct invocations (format_summary(...)) to find concrete usages.
- Rationale for extraction: keeps conversion logic consistent and testable in a single place instead of duplicating conversions across multiple summary-producing components.

## Args:
    summary (Union[BaseDescription, dict])
        - If a BaseDescription instance is provided (the BaseDescription type imported from ydata_profiling.model), the function first calls dataclasses.asdict(summary) to obtain a plain nested dict. asdict performs a recursive conversion of dataclass fields to dictionaries for nested dataclasses.
        - If a dict-like mapping is provided, the function iterates summary.items() and normalizes each value.
        - Expectations:
            * Top-level mapping semantics (iteration via .items()) are used.
            * Keys are preserved as-is (including non-string keys) — the function does not coerce keys to strings.

## Returns:
    dict
        - A new dict (top-level) whose keys match the input mapping's keys and whose values have been normalized according to the following rules:
            1. dict -> recursively normalize every value (returned as a new dict).
            2. pandas.Series -> call Series.to_dict() to obtain a dict and then normalize that dict recursively.
            3. tuple of length 2 where both elements are numpy.ndarray (checked via isinstance(x, numpy.ndarray) using the numpy import alias) -> converted to
               {"counts": first_array.tolist(), "bin_edges": second_array.tolist()}.
            4. any other value -> returned unchanged (reference preserved).
        - Edge cases:
            * A tuple not of length 2, or of length 2 but with elements that are not numpy.ndarray, is returned unchanged (no conversion).
            * Standalone numpy.ndarray values (not part of the specific 2-tuple histogram pattern) are not converted and will remain numpy arrays in the returned dict.
            * pandas.Series converted to dicts will have their indices used as keys; those nested values are then normalized by the same rules.

## Raises:
    - The function does not explicitly raise application-level exceptions.
    - Exceptions that may propagate:
        * If isinstance(summary, BaseDescription) returns True but dataclasses.asdict is called on an object that is not a dataclass-compatible structure, dataclasses.asdict may raise TypeError — this is unlikely in normal use because BaseDescription is intended to be a dataclass.
        * If a value implements .items() or Series.to_dict() and those methods raise, those exceptions will propagate.
    - No exceptions are swallowed; the function allows underlying errors to surface.

## Constraints:
    Preconditions:
        - pandas and numpy must be available (the module imports pandas as pd and numpy as numpy).
        - The caller should pass either a BaseDescription instance or a mapping-like dict at the top level.
    Postconditions:
        - No pandas.Series instances remain in branches that the function traverses (they have been replaced by dicts).
        - Histogram-like 2-tuples of numpy arrays are replaced by dicts with "counts" and "bin_edges" lists.
        - The top-level return value is a dict; nested values may still contain non-serializable objects if they do not match the recognized patterns.

## Side Effects:
    - None. The function performs pure, functional transformations and does not mutate global state or perform I/O. Note:
        * If the input is a dict, values that are not transformed are returned by reference (no deep-copying of unchanged objects).
        * asdict produces a new dict for dataclass instances, so the original dataclass is not mutated.

## Control Flow:
flowchart TD
    Start[Start: receive summary] --> CheckDataclass{isinstance(summary, BaseDescription)?}
    CheckDataclass -- Yes --> Asdict[summary = asdict(summary)]
    CheckDataclass -- No --> ToIterate[Proceed to iterate summary.items()]
    Asdict --> ToIterate
    ToIterate --> ForEach[For each (k, v) in summary.items() apply fmt(v)]
    ForEach --> IsDict{Is v a dict?}
    IsDict -- Yes --> Recurse[Return {k: fmt(v) for k, v in v.items()}]
    IsDict -- No --> IsSeries{Is v a pandas.Series?}
    IsSeries -- Yes --> SeriesToDict[Call v.to_dict() then fmt(that dict)]
    IsSeries -- No --> IsTuple{Is v a tuple of length 2 and both elems are numpy.ndarray?}
    IsTuple -- Yes --> Histogram[Return {"counts": v[0].tolist(), "bin_edges": v[1].tolist()}]
    IsTuple -- No --> ReturnValue[Return v unchanged]
    Recurse --> Assign[Assign normalized value into top-level result]
    SeriesToDict --> Assign
    Histogram --> Assign
    ReturnValue --> Assign
    Assign --> NextOrEnd[Continue for next item or return result]
    NextOrEnd --> End[Return normalized dict]

## Implementation notes / Reimplementation checklist:
- Use dataclasses.asdict to convert BaseDescription instances to a nested dict snapshot.
- Implement a local recursive helper fmt(value) with this logic:
    1. If isinstance(value, dict): return {k: fmt(va) for k, va in value.items()}
    2. Elif isinstance(value, pandas.Series): return fmt(value.to_dict())
    3. Elif isinstance(value, tuple) and len(value) == 2 and all(isinstance(x, numpy.ndarray) for x in value):
         return {"counts": value[0].tolist(), "bin_edges": value[1].tolist()}
    4. Else: return value
- Apply fmt to every top-level value and return the constructed dict comprehension result.
- Keep the numpy import alias (numpy) and pandas alias (pandas / pd) consistent with module imports so isinstance checks resolve correctly.

## Examples (illustrative input -> output):
- Example A (histogram tuple + pandas Series):
    * Input (conceptual structure):
        {
            "hist": (numpy.array([1, 2, 3]), numpy.array([0.0, 1.0, 2.0, 3.0])),
            "freq": pandas.Series({"a": 10, "b": 5})
        }
    * Output:
        {
            "hist": {"counts": [1, 2, 3], "bin_edges": [0.0, 1.0, 2.0, 3.0]},
            "freq": {"a": 10, "b": 5}
        }

- Example B (BaseDescription dataclass with nested Series/tuples):
    * Input: BaseDescription(field1=pandas.Series(...), field2=(numpy.array(...), numpy.array(...)), other="x")
    * Processing:
        1. asdict(BaseDescription) -> {'field1': Series, 'field2': (ndarray, ndarray), 'other': 'x'}
        2. fmt converts field1 -> dict, field2 -> {"counts": [...], "bin_edges": [...]}, other unchanged.
    * Output: dict ready for JSON serialization.

Notes on what is intentionally not converted:
- Single numpy.ndarray objects (not in the specific 2-tuple histogram pattern) remain numpy arrays.
- Arbitrary custom objects are left untouched unless they match the handled cases (dict or pandas.Series or the histogram tuple).

This documentation is sufficient to reimplement the function and reproduce its behavior precisely.

## `src.ydata_profiling.model.summarizer._redact_column` · *function*

## Summary:
Replaces sensitive keys or values in specific per-column summary fields with deterministic REDACTED_<index> tokens and returns the (mutated) column summary dictionary.

## Description:
This helper is used to redact identifying or verbose information inside a column-level summary structure before further processing, serialization, or display. It locates a predefined set of fields that commonly contain detailed category/character/word/value counts or example rows and replaces either their keys or their values with generic REDACTED_<index> tokens.

Known callers:
- No direct callers are declared in this source fragment. In the typical profiling pipeline, this function is invoked from summarization code that prepares per-column summaries for export or UI rendering (i.e., immediately before a column summary is serialized or shown to a user).

Why this logic is isolated:
- Redaction is a single, well-scoped responsibility (masking sensitive content while preserving structure and counts). Extracting it into a separate function keeps summarization algorithms focused on computing statistics and centralizes masking behaviour (key vs value redaction and nested structures) so it can be audited or changed in one place.

## Args:
    column (Dict[str, Any]):
        - The per-column summary dictionary to redact.
        - Expected shape (when fields exist): column[field] is a mapping (dict).
        - The function inspects and mutates specific fields inside this dict; other keys are untouched.
        - Interdependencies:
            * For keys listed under "keys_to_redact", the code expects column[field] to be a dict mapping -> either (a) key -> primitive/count, or (b) key -> dict (i.e., nested dicts grouping counts). If some values are dict and some are not, see "Constraints / Edge cases".
            * For fields listed under "values_to_redact", the code similarly expects a dict mapping; if values are dicts the nested dicts will be value-redacted per inner key.

## Returns:
    Dict[str, Any]:
        - The same dictionary object passed in (mutated in-place) is returned.
        - All fields listed below that exist in the input will be replaced with redacted versions:
            * keys redacted (original values preserved) for:
                - block_alias_char_counts, block_alias_values, category_alias_char_counts,
                  category_alias_values, character_counts, script_char_counts,
                  value_counts_index_sorted, value_counts_without_nan, word_counts
            * values redacted (original keys preserved) for:
                - first_rows
        - If a field contains nested dicts (i.e., a dict whose values are dicts), each nested dict is redacted individually (keys or values depending on which list the outer field belongs to).

## Raises:
    - AttributeError:
        - If a field that exists in column is not a dict (does not have .values() or .items()), the function will attempt to call .values() / .items() and an AttributeError may be raised.
        - If an outer mapping contains a mix of dict and non-dict values and the function chooses the "nested dicts" branch (because any(value is dict) is True), calling redact_key/redact_value on a non-dict nested value will raise an AttributeError.
    - No exceptions are explicitly raised by the function; the above exceptions arise from invalid shapes of the input data.

## Constraints:
Preconditions:
    - column must be a mutable mapping (dict).
    - For each field present that the function targets, column[field] should be a dict mapping keys to either primitive values (counts, strings) or to dicts (nested groupings). Homogeneous inner types are expected per-field (all nested values should be dicts, or none should be dicts).
Postconditions:
    - For every targeted field present in the input:
        * If the field was key-redacted: every mapping at that position now has its keys replaced with "REDACTED_0", "REDACTED_1", ... in the same enumeration order; original values are preserved.
        * If the field was value-redacted: every mapping at that position now has its values replaced with "REDACTED_0", "REDACTED_1", ... where indices reflect enumeration order; original keys are preserved.
    - The function preserves the outer structure (which outer keys exist) but replaces the mapping(s) for the targeted fields.
    - The returned object is the same dict instance passed in, mutated in-place.

## Side Effects:
    - Mutates the input dict (column) in-place. No copies of the top-level column dict are made.
    - No I/O, network, external services, global state, file, or database interactions occur.

## Control Flow:
flowchart TD
    Start[Start: receive column dict]
    keysCheck{Field in keys_to_redact?}
    valuesCheck{Field in values_to_redact?}
    keysLoop[Iterate keys_to_redact list]
    valuesLoop[Iterate values_to_redact list]
    isPresentKeys[Field present in column?]
    isPresentValues[Field present in column?]
    inspectValsKeys[is any(column[field].values()) a dict?]
    inspectValsValues[is any(column[field].values()) a dict?]
    nestedKeysBranch[For each k,v -> redact_key(v) and set column[field][k] = redacted]
    flatKeysBranch[Set column[field] = redact_key(column[field])]
    nestedValuesBranch[For each k,v -> redact_value(v) and set column[field][k] = redacted]
    flatValuesBranch[Set column[field] = redact_value(column[field])]
    End[Return mutated column dict]

    Start --> keysLoop
    keysLoop --> keysCheck
    keysCheck --> isPresentKeys
    isPresentKeys -->|no| keysLoop
    isPresentKeys -->|yes| inspectValsKeys
    inspectValsKeys -->|any dict True| nestedKeysBranch
    inspectValsKeys -->|all non-dict| flatKeysBranch
    nestedKeysBranch --> keysLoop
    flatKeysBranch --> keysLoop

    keysLoop --> valuesLoop
    valuesLoop --> valuesCheck
    valuesCheck --> isPresentValues
    isPresentValues -->|no| valuesLoop
    isPresentValues -->|yes| inspectValsValues
    inspectValsValues -->|any dict True| nestedValuesBranch
    inspectValsValues -->|all non-dict| flatValuesBranch
    nestedValuesBranch --> valuesLoop
    flatValuesBranch --> valuesLoop

    valuesLoop --> End

## Examples:
Example 1 — simple key redaction:
- Input column contains:
    * "word_counts": {"apple": 10, "banana": 5}
- Behavior:
    * "word_counts" is in keys_to_redact, and its values are non-dict primitives.
    * After calling the function, "word_counts" will be replaced by {"REDACTED_0": 10, "REDACTED_1": 5}.
- The input dict object is mutated and also returned.

Example 2 — nested structures with value redaction:
- Input column contains:
    * "first_rows": {"row_1": {"colA": "Alice", "colB": 42}, "row_2": {"colA": "Bob", "colB": 17}}
- Behavior:
    * "first_rows" is in values_to_redact. The outer mapping's values are dicts, so each nested dict is processed by redact_value: for the first nested dict, keys are preserved and values become "REDACTED_0", "REDACTED_1", ...
    * After calling the function, "first_rows" will be:
        {"row_1": {"colA": "REDACTED_0", "colB": "REDACTED_1"},
         "row_2": {"colA": "REDACTED_0", "colB": "REDACTED_1"}}
- Note: The enumeration order of indices follows the iteration order of the inner dicts.

Edge-case example — mixed nested types (warning):
- If column["word_counts"] == {"groupA": {"a":1}, "groupB": 5}:
    * any(isinstance(v, dict) for v in column[field].values()) is True (because one value is a dict).
    * The code will attempt to call redact_key on both values. redact_key expects a dict and will raise AttributeError when invoked on the integer 5.
    * Therefore mixed inner types for a targeted field are unsupported and will likely raise an AttributeError.

## `src.ydata_profiling.model.summarizer.redact_summary` · *function*

## Summary:
Iterates over the per-variable summaries in a profile and, when configured, masks identifying categorical or text details by applying the column-level redaction routine; returns the (mutated) summary mapping.

## Description:
This function is a thin orchestrator that walks every column summary stored under summary["variables"] and invokes the centralized redaction helper on columns whose type and config flags indicate they should be masked.

Known callers within the profiling pipeline:
- The summarization/export stage of the profiling workflow — typically called immediately after the per-column summaries are computed and before the summary is serialized, stored, or displayed (i.e., just prior to writing a report or returning JSON to a UI). There are no explicit call-sites shown in the local fragment; usage is by the higher-level profiling/reporting pipeline.

Why this logic is extracted:
- Responsibility separation: summary generation algorithms compute statistics and examples; redaction is a separate concern (masking sensitive strings while preserving counts/structure). Extracting this decision loop keeps the filter/dispatching logic here while delegating the masking details to _redact_column, allowing audits or changes to masking behavior without touching summarization code.

## Args:
    summary (dict):
        - Full profile summary produced by the summarizer pipeline.
        - Required structure: must contain a top-level key "variables" that maps column names to per-column summary dicts.
        - Each per-column dict is expected to contain a "type" entry (string), for example "Categorical", "Text", "Numeric", etc.
        - The function mutates the per-column dict objects in-place via the redaction helper.
    config (Settings):
        - Configuration object (instance of Settings) controlling redaction flags.
        - The function reads:
            * config.vars.cat.redact (bool) — when True, categorical columns (col["type"] == "Categorical") are redacted.
            * config.vars.text.redact (bool) — when True, text columns (col["type"] == "Text") are redacted.
        - No other config fields are read.

Interdependencies:
    - The effect depends on both the column's "type" value and the corresponding config flag. A column is processed only if (config.vars.cat.redact and type == "Categorical") OR (config.vars.text.redact and type == "Text").

## Returns:
    dict:
        - The same summary object passed in, returned after in-place mutation.
        - For every targeted column (per the config/type check), the per-column dict will have been passed to _redact_column and thus modified in-place.
        - If no columns meet the criteria, the function returns the original object unchanged.

## Raises:
    - KeyError:
        - If the top-level key "variables" is missing from summary, summary["variables"] will raise KeyError.
        - If a per-column dict lacks the "type" key, accessing col["type"] raises KeyError.
    - AttributeError or other exceptions raised by _redact_column:
        - _redact_column mutates and expects certain dict shapes for fields it processes; if a targeted field is not a mapping or has mixed nested types, _redact_column may raise AttributeError (see its documentation). These exceptions propagate out of redact_summary.
    - TypeError:
        - If summary is not a mapping type (e.g., None or a list), attempting summary["variables"] will raise TypeError or a similar exception.

## Constraints:
Preconditions:
    - summary must be a mapping with a "variables" mapping.
    - Each value in summary["variables"].values() must be a mutable mapping (dict-like) and typically include a "type" key holding a string.
    - config must present the boolean flags at config.vars.cat.redact and config.vars.text.redact.

Postconditions:
    - For each per-column dict that satisfied the config/type condition, that dict has been passed to _redact_column and is therefore mutated according to that helper's contract (sensitive keys/values replaced with REDACTED_<index> tokens; mapping structure preserved).
    - Other columns are untouched.
    - The returned summary references the same top-level object passed in (no copy semantics are performed here).

Important implementation nuance:
    - The loop assigns the helper result to the local variable col (col = _redact_column(col)) but does not write that back into the enclosing mapping. This is safe because _redact_column mutates the passed dict in-place and returns the same instance. If _redact_column were to return a new dict instead of mutating in-place, this implementation would fail to persist the new dict into summary["variables"].

## Side Effects:
    - In-place mutation of the input summary: per-column dicts are modified directly.
    - No I/O, network access, global state, file, or database changes are performed by this function itself.
    - Any exceptions raised by _redact_column will propagate to the caller.

## Control Flow:
flowchart TD
    Start[Start: call redact_summary(summary, config)]
    varsExists{"variables" in summary?}
    iterate[Iterate through summary["variables"].items()]
    checkType{(config.vars.cat.redact AND type=="Categorical") OR (config.vars.text.redact AND type=="Text")}
    redactCall[Call _redact_column(col) which mutates col in-place]
    continueIter[Continue to next column]
    Return[Return mutated summary]

    Start --> varsExists
    varsExists -->|no| Error[Raise KeyError/TypeError]
    varsExists -->|yes| iterate
    iterate --> checkType
    checkType -->|yes| redactCall
    redactCall --> continueIter
    checkType -->|no| continueIter
    continueIter --> iterate
    iterate --> Return

## Examples:
Example — typical usage in a profiling pipeline
1) After computing the full profile summary (a dict with a "variables" mapping), call redact_summary(summary, config) just before serializing or returning the summary to an external consumer.
2) If config.vars.cat.redact is True, categorical columns will have their category keys/values masked. If config.vars.text.redact is True, text columns will have example text values masked.

Illustrative input / output (informal):

Input (simplified):
    summary = {
        "variables": {
            "user_name": {"type": "Text", "first_rows": {"r1": "Alice", "r2": "Bob"}},
            "color": {"type": "Categorical", "word_counts": {"red": 10, "blue": 5}},
            "age": {"type": "Numeric", "mean": 34.2}
        }
    }
    config.vars.text.redact = True
    config.vars.cat.redact = True

After calling redact_summary(summary, config):
    - summary["variables"]["user_name"]["first_rows"] will have text values replaced by REDACTED_0, REDACTED_1, ...
    - summary["variables"]["color"]["word_counts"] will have keys replaced by REDACTED_0, REDACTED_1, ... with counts preserved.
    - summary["variables"]["age"] remains unchanged.

Error-handling example:
    - If summary lacks "variables", the caller should catch KeyError and handle it (for example, validate the summary shape before calling redact_summary).
    - If _redact_column raises an AttributeError due to unexpected inner shapes, the caller can catch it to surface a clearer validation error or to skip redaction for that column.

