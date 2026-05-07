# `description.py`

## `src.ydata_profiling.model.description.BaseAnalysis` · *class*

## Summary:
A lightweight container for analysis metadata that stores a title and start/end timestamps and exposes a computed duration (either a single timedelta or a list of timedeltas).

## Description:
BaseAnalysis represents the minimal metadata for an analysis run: a human-readable title and start/end times. It is intended to be instantiated when a component needs to record the timing span of an analysis step and to provide a simple convenience property to obtain the duration.

Motivation and responsibility boundary:
- Encapsulates the pair of timestamps and the logic to compute elapsed time(s).
- Keeps timing-related concerns localized (storage of start/end and computation of duration).
- Does not perform validation beyond simple runtime type checks in the duration property; callers are responsible for setting consistent types and matching list lengths if lists are used.

Typical scenarios for instantiation:
- At the beginning and end of a profiling/reporting step to record when the step started and ended.
- As a simple data holder when aggregating analysis metadata for logging or display.

## State:
Public attributes and their types (as present in the source):

- title: str
  - Description: Human-readable name for the analysis.
  - Constraints: Any string. No runtime validation in __init__.

- date_start: Union[datetime, List[datetime]]
  - Description: Start time(s) for the analysis.
  - Declared types: The class-level annotation allows either a single datetime or a list of datetimes.
  - __init__ signature: The constructor parameter is declared as datetime (see Lifecycle). Callers should provide a datetime when invoking __init__. The attribute may later hold a list if assigned after construction.
  - Invariant guidance: If set to a list, date_end should also be a list of at least the same length.

- date_end: Union[datetime, List[datetime]]
  - Description: End time(s) for the analysis.
  - Declared types: Class-level annotation allows either a single datetime or a list of datetimes.
  - __init__ signature: The constructor parameter is declared as datetime (see Lifecycle). The attribute may later hold a list if assigned after construction.
  - Invariant guidance: When lists are used, lengths should match date_start's list length to avoid index errors.

Class invariants (recommended and relied upon by duration):
- Either both date_start and date_end are datetimes, or both are lists of datetimes.
- If they are lists, they should have the same length. The code does not enforce this, but failing to maintain it may raise an IndexError when computing durations.

## Lifecycle:
Creation:
- Constructor signature (exact as in source): BaseAnalysis(title: str, date_start: datetime, date_end: datetime) -> None
  - Required arguments:
    - title: str
    - date_start: datetime
    - date_end: datetime
  - Note: Although the class-level attribute annotations allow lists, the __init__ parameters are declared as datetime. The constructor simply assigns the provided values to the attributes without further type conversion or validation.

Usage:
- After instantiation, the primary interaction is reading the duration property:
  - If both attributes are datetimes, duration returns a single timedelta equal to date_end - date_start.
  - If both attributes are lists of datetimes, duration returns a list of timedeltas where each element is date_end[i] - date_start[i] for i from 0 to len(date_start)-1.
- There is no required method call ordering beyond setting the attributes such that the duration property's type checks succeed when accessed.

Destruction / cleanup:
- No special cleanup is required. The class holds only simple Python objects; there are no open resources, context manager protocol, or close methods.

## Method Map:
Mermaid flowchart showing relationships and decision points:

flowchart TD
    A[__init__(title, date_start, date_end)] --> B[set title, date_start, date_end]
    B --> C[duration property accessed]
    C --> D{are date_start and date_end datetimes?}
    D -- yes --> E[return date_end - date_start (timedelta)]
    D -- no --> F{are date_start and date_end lists?}
    F -- yes --> G[return [date_end[i] - date_start[i] for i in range(len(date_start))] (list[timedelta])]
    F -- no --> H[raise ValueError()]

Notes on the flow:
- Accessing duration performs runtime isinstance checks to select behavior.
- When lists are used, the implementation iterates up to len(date_start) and indexes into date_end; mismatched lengths can cause IndexError.

## Raises:
- __init__:
  - No exceptions are raised by the constructor in the provided implementation.

- duration (property):
  - ValueError: Raised when the pair (date_start, date_end) is neither both datetimes nor both lists (i.e., when the type combination is unsupported).
  - IndexError: Not explicitly raised by the code, but likely to surface if date_start and date_end are lists of differing lengths because duration indexes date_end[i] for i in range(len(date_start)). This is an observable runtime failure mode and should be guarded against by callers if lists are used.
  - Other exceptions: If date_start or date_end hold values that are neither datetimes nor lists (for example, None or other types), the code will fall into the ValueError branch or may raise TypeError when subtraction is attempted; callers should ensure the attributes are datetimes or lists of datetimes.

## Example:
- Creation with single datetimes and reading duration:
  - Instantiate with a string title and two datetime objects.
  - Access the duration property to obtain a timedelta representing the elapsed time (date_end - date_start).

- Using lists (assignment after construction) and reading duration:
  - Although the constructor parameters are declared as datetime, the attributes are public and may be reassigned to lists of datetimes.
  - If date_start and date_end are both lists of datetime objects of equal length, accessing duration returns a list of timedeltas computed element-wise.
  - If the lists have different lengths, accessing duration will attempt to index past the shorter list and raise IndexError.

Implementation notes for reimplementation:
- Follow the exact constructor signature title: str, date_start: datetime, date_end: datetime and assign them directly to attributes.
- Implement duration as a read-only property that:
  - Checks for the datetime pair case and returns date_end - date_start.
  - Checks for the list pair case and returns a list comprehension computing per-index differences up to len(date_start).
  - Raises ValueError for any other type combination.
- Do not add additional implicit validation unless callers require it; the original implementation intentionally keeps validation minimal and raises ValueError on unsupported type combinations.

### `src.ydata_profiling.model.description.BaseAnalysis.__init__` · *method*

## Summary:
Initializes the BaseAnalysis instance by storing the provided title, date_start, and date_end on the object, establishing the minimal state required for later analysis properties (e.g., duration).

## Description:
This initializer is executed at object construction time when a BaseAnalysis or any subclass instance is created. Typical usage is during the setup phase of an analysis/reporting pipeline where an analysis object is instantiated and then used to compute or expose derived properties (for example, the duration property defined on the class).

Known callers:
- No explicit callers are present in this file. In practice this method is invoked by:
  - Direct construction of BaseAnalysis instances.
  - Constructors of subclasses that call super().__init__(...) to initialize shared attributes.

Why this is a separate method:
- Centralizes shared attribute initialization so subclasses reuse and extend a consistent state layout (title, date_start, date_end) instead of reimplementing the same assignments in each subclass.

## Args:
    title (str):
        - The human-readable title for the analysis.
        - Type requirement: str (no runtime validation is performed here).
        - No default; must be supplied by the caller.
    date_start (datetime):
        - Start point(s) of the analysis period.
        - Annotated in the __init__ signature as datetime, but class-level annotations and other methods in the class (e.g., duration) indicate this attribute may also be a list of datetime objects. The initializer performs no type conversion or validation.
        - No default; must be supplied by the caller.
    date_end (datetime):
        - End point(s) of the analysis period.
        - Same type notes as date_start: typically a datetime or a list of datetime objects; no runtime validation in __init__.
        - No default; must be supplied by the caller.

## Returns:
    None

## Raises:
    This initializer does not raise any exceptions itself.
    Note: downstream methods (for example, the duration property) will raise ValueError if date_start/date_end have incompatible types (mixed scalar vs list). Also, if lists of unequal length are provided, subsequent index-based computations may raise IndexError elsewhere.

## State Changes:
Attributes READ:
    - None (the method does not read existing instance attributes).

Attributes WRITTEN:
    - self.title: set to the provided title argument.
    - self.date_start: set to the provided date_start argument (shallow assignment).
    - self.date_end: set to the provided date_end argument (shallow assignment).

## Constraints:
Preconditions:
    - Caller must supply title, date_start, and date_end.
    - Title should be a string (the method does not validate this).
    - To avoid errors later, callers should provide date_start and date_end of compatible shapes:
        * Both should be datetime instances, or
        * Both should be lists of datetime instances of equal length.
    - Mixing a scalar datetime with a list for the other argument will later cause the duration property to raise ValueError.

Postconditions:
    - After return, the instance has attributes title, date_start, and date_end assigned exactly to the provided objects (no copies).
    - No validation guarantees are made beyond assignment.

## Side Effects:
    - No I/O, no logging, and no external service calls.
    - Assignments are shallow: if mutable objects (e.g., lists) are passed for date_start/date_end, external mutations to those objects will be reflected on the instance because references are stored directly.

### `src.ydata_profiling.model.description.BaseAnalysis.duration` · *method*

## Summary:
Compute and return the elapsed time(s) between the instance's end and start timestamp(s); does not modify the object's state.

## Description:
This read-only property returns the difference (end - start) for the timestamps stored on the instance. The implementation performs explicit type checks and supports exactly two shapes for the attributes:
- Two datetime.datetime instances: returns a single datetime.timedelta.
- Two list objects (python list) of datetime.datetime instances: returns a list of datetime.timedelta computed element-wise using indices 0..len(date_start)-1.

Known callers and lifecycle:
- Consumers typically access this property during post-processing, reporting, or profiling steps to display or log the duration of an analysis run or multiple runs.
- There are no internal callers within BaseAnalysis; it is a convenience accessor for external code.

Why this is a separate property:
- Centralizes and reuses the elapsed-time computation for both single and batched (list) timestamp representations.
- Avoids duplicating type checking and subtraction logic throughout the codebase and provides a stable API for consumers.

## Args:
- None (reads instance attributes).

## Returns:
- Union[datetime.timedelta, List[datetime.timedelta]]
  - If both self.date_start and self.date_end are datetime.datetime instances:
    - Returns a single datetime.timedelta equal to (self.date_end - self.date_start).
  - If both are python list objects:
    - Returns a list of datetime.timedelta where element i is (self.date_end[i] - self.date_start[i]) for i in range(len(self.date_start)).
    - If self.date_start is an empty list, an empty list is returned.
  - Timedelta values may be negative if a corresponding end is earlier than its start.

## Raises:
- ValueError: raised unconditionally (with no message) when the pair of attributes does not match one of the two supported shapes:
    * Not both datetime.datetime instances, and not both python list instances.
    Examples that trigger this ValueError:
      - self.date_start is a datetime and self.date_end is a list (or vice versa).
      - self.date_start is a tuple while self.date_end is a tuple (tuples are not accepted because the code checks for list).
- IndexError: may be raised during list handling if self.date_end has fewer elements than self.date_start (because the code indexes self.date_end[i] for i in range(len(self.date_start))).
- TypeError or other exceptions: may propagate if subtraction is not supported between the provided elements (e.g., elements are not datetime instances).

## State Changes:
- Attributes READ:
    - self.date_start
    - self.date_end
- Attributes WRITTEN:
    - None (the property is pure with respect to object state).

## Constraints:
Preconditions:
- Exactly one of these must hold before calling:
  - Both self.date_start and self.date_end are instances of datetime.datetime.
  - Both self.date_start and self.date_end are python list instances, and their elements are objects that support subtraction yielding a datetime.timedelta (commonly datetime.datetime).
- The implementation checks for python list specifically (isinstance(..., list)); passing other sequence types (tuple, deque, numpy array) will not match and will lead to ValueError.
- For lists, ensure self.date_end has at least len(self.date_start) elements to avoid IndexError.

Postconditions:
- The object state (its attributes) is unchanged.
- The caller receives either a timedelta or a list of timedeltas representing end - start for each pair.

## Side Effects:
- None. No I/O, logging, or external service calls. Only local attribute reads and arithmetic (subtraction) operations occur.
- Any exceptions from invalid inputs propagate to the caller.

## Examples:
- Single timestamps:
  - If self.date_start is datetime(2021,1,1,12,0,0) and self.date_end is datetime(2021,1,1,12,00,10), the property returns a timedelta of 10 seconds.
- List of timestamps:
  - If self.date_start is [t0, t1] and self.date_end is [u0, u1], the property returns [u0 - t0, u1 - t1]. If the lists are empty, returns [].

## `src.ydata_profiling.model.description.TimeIndexAnalysis` · *class*

*No documentation generated.*

### `src.ydata_profiling.model.description.TimeIndexAnalysis.__init__` · *method*

## Summary:
Initializes a TimeIndexAnalysis instance by storing the provided time-index summary parameters on the object.

## Description:
This constructor assigns the provided summary values (number of series, length, start/end bounds, period, and optional frequency) to instance attributes so the object holds a compact description of a time index analysis.

Known callers and context:
- No callers were available in the provided source context. In typical usage the method is invoked when a TimeIndexAnalysis object is instantiated as part of a profiling/analysis pipeline that constructs this object to summarize time-index characteristics for a dataset or variable.

Why this logic is a separate method:
- As the class initializer, this method centralizes and documents how the instance state is created. Keeping attribute assignment in __init__ follows standard object construction patterns and separates object creation from later analysis or representation logic.

## Args:
    n_series (int): Number of distinct time series represented. No runtime validation is performed by this method.
    length (int): Total number of time index entries (length of the index). No runtime validation is performed by this method.
    start (Any): Lower bound / first value of the time index. Type is not enforced here; commonly a datetime or timestamp-like value.
    end (Any): Upper bound / last value of the time index. Type is not enforced here; commonly a datetime or timestamp-like value.
    period (float): Estimated or measured period between observations. No validation is performed by this method.
    frequency (Optional[str], optional): Optional string describing frequency (for example 'D', 'H', etc.). Defaults to None.

## Returns:
    None

## Raises:
    None — the constructor performs direct assignments and does not raise exceptions itself.

## State Changes:
Attributes READ:
    - None (the method does not read any pre-existing self attributes)

Attributes WRITTEN:
    - self.n_series
    - self.length
    - self.start
    - self.end
    - self.period
    - self.frequency

## Constraints:
Preconditions:
    - The method does not enforce any type or value constraints; callers are responsible for supplying appropriate types and valid values for their application (e.g., integers for n_series and length, sensible start/end values, positive period if applicable).

Postconditions:
    - After invocation, the instance will have the six attributes listed above bound to the provided argument values (exactly as passed).

## Side Effects:
    - None. The constructor only assigns values to attributes on self and does not perform I/O, external service calls, or mutate objects outside self.

## `src.ydata_profiling.model.description.BaseDescription` · *class*

## Summary:
A minimal, plain-data container that aggregates all profiling outputs (analysis metadata, table-wide statistics, per-variable summaries, correlations, missingness, alerts, samples, duplicates, and package metadata) so downstream renderers and serializers can consume a single coherent object.

## Description:
BaseDescription is a thin structural holder intended to be populated by profiling analyzers and then passed to report builders, serializers, or tests. The class declares public attributes that store results produced by different analysis stages; it does not compute or validate statistics itself.

Scenarios where to instantiate:
- Profiling/report pipelines create an instance, populate its attributes as analysis steps complete, and hand it to report renderers or exporters.
- Unit tests or mocks may construct a BaseDescription and set only the fields relevant to the test.

Motivation and responsibility boundary:
- Responsibility: collect and transport profiling artifacts produced elsewhere.
- Boundary: no computation or heavy validation; producers (analyzers) compute and validate, consumers (renderers/serializers) read and render or export.

Relation to BaseAnalysis (explicitly aligned):
- The analysis attribute holds a BaseAnalysis instance. BaseAnalysis is a lightweight metadata container with:
  - constructor signature: BaseAnalysis(title: str, date_start: datetime, date_end: datetime) -> None
  - public attributes: title (str), date_start (Union[datetime, List[datetime]]), date_end (Union[datetime, List[datetime]])
  - duration property: returns either a timedelta (date_end - date_start) when both are datetimes, or a list of timedeltas when both are lists; it raises ValueError if types are mixed/unsupported. Although BaseAnalysis __init__ accepts datetimes, callers may later assign lists to date_start/date_end — callers must ensure lists are consistent in length when used.
- When populating BaseDescription.analysis, create a BaseAnalysis instance using the constructor above (with datetimes) and, if necessary, reassign list values intentionally and carefully, following BaseAnalysis rules.

Known callers / factories:
- Profiling pipeline components that orchestrate table-level, variable-level, correlation, and missingness analyses.
- Report builders that accept BaseDescription to render HTML/JSON reports.

## State:
Public attributes, expected types, and semantics. All attributes are public and typically optional unless the producing pipeline guarantees them.

- analysis: BaseAnalysis
  - Type: BaseAnalysis
  - Semantics: profiling run metadata (title, date_start, date_end, and duration via BaseAnalysis).
  - Construction guidance: instantiate via BaseAnalysis(title, date_start, date_end) where date_start and date_end are datetime objects. If lists are used later, ensure they follow BaseAnalysis constraints.

- time_index_analysis: Optional[TimeIndexAnalysis]
  - Type: Optional / opaque
  - Semantics: holds time-index-specific analysis results when profiling time-series or time-indexed data; may be None if not applicable.

- table: Any
  - Type: Any (recommended: mapping/dict with table-level summary)
  - Semantics: table-wide statistics such as n_rows, n_columns, memory usage. Keys are convention-based between producers and consumers.

- variables: Dict[str, Any]
  - Type: dict mapping column name to per-variable summary (commonly dicts or VariableDescription objects)
  - Semantics: contains per-column statistics and artifacts (histograms, type inference, distinct counts).

- scatter: Any
  - Type: Any (optional)
  - Semantics: artifacts used for scatter/pairwise visualizations.

- correlations: Dict[str, Any]
  - Type: mapping from correlation method name to correlation matrix or summary
  - Semantics: stores correlation outputs (e.g., "pearson": matrix-like structure).

- missing: Dict[str, Any]
  - Type: mapping describing missingness information
  - Semantics: per-variable missing counts/percentages and global patterns.

- alerts: Any
  - Type: list or mapping of alert records (or None)
  - Semantics: detected issues (e.g., constant variables, high cardinality). Consumers should accept an empty list or None.

- package: Dict[str, Any]
  - Type: mapping for package/runtime metadata (versions, environment)
  - Semantics: used for reproducibility.

- sample: Any
  - Type: Any (recommended: small representative sample, e.g., list[dict] or DataFrame)
  - Semantics: optional example rows to display in reports.

- duplicates: Any
  - Type: Any (recommended: mapping with duplicate detection results)
  - Semantics: information about duplicate rows (counts, example indices or rows).

Class invariants and constraints:
- BaseDescription itself enforces no runtime invariants. Producers must ensure fields that readers expect to exist are set and shaped appropriately.
- Specifically for analysis (BaseAnalysis): date_start/date_end should remain consistent with BaseAnalysis expectations (either both datetimes or both lists of datetimes of matching length if lists are used).

## Lifecycle:
Creation:
- The source provides only attribute annotations; there is no explicit __init__ in the provided snippet. Two common patterns to create a usable object:
  1) Empty instance then assign attributes:
     - desc = BaseDescription()
     - desc.analysis = BaseAnalysis("Title", start_dt, end_dt)
     - desc.variables = {...}
  2) Dataclass / explicit initializer wrapper (recommended for convenience):
     - Implement a small factory or dataclass that accepts common fields (analysis, variables, table, ...) and returns a populated BaseDescription object.

Usage order:
- No strict ordering is required by BaseDescription. Typical pipeline:
  1) Create/instantiate BaseDescription.
  2) Immediately create and assign BaseAnalysis via its constructor with datetimes.
  3) Populate table and variables.
  4) Populate correlations, missing, scatter, duplicates, sample, alerts, and package as they become available.
  5) Pass to consumer (renderer/serializer) which should defensively check for missing/None attributes.

Destruction / cleanup:
- No explicit cleanup is required. If attributes reference external resources, producers must close them; BaseDescription does not manage resource lifetimes.

## Method Map:
flowchart LR
    A[Create BaseDescription] --> B[Create BaseAnalysis(title, date_start, date_end)]
    B --> C[Assign desc.analysis = BaseAnalysis instance]
    C --> D[Populate desc.table, desc.variables]
    D --> E[Populate desc.correlations, desc.missing, desc.sample, desc.alerts, desc.package, desc.duplicates]
    E --> F[Pass desc to renderer/serializer/test]
    F --> G[Export or discard]

Notes:
- The diagram emphasizes creation of BaseAnalysis with datetime args (per BaseAnalysis constructor) and the later population of other fields.

## Raises:
- Construction:
  - BaseDescription (as declared) has no explicit constructor and therefore raises no specific exceptions on instantiation aside from normal Python errors.
  - When creating BaseAnalysis to assign to desc.analysis, follow BaseAnalysis constructor: it does not raise on construction, but its duration property can raise ValueError if date_start/date_end types are unsupported.

- Attribute access:
  - Consumers may encounter AttributeError, TypeError, KeyError, or IndexError if they assume fields exist or have a particular shape. Producers and consumers must validate shapes where appropriate.

## Example:
- Typical creation and population (described as steps):
  1) Create a BaseDescription instance:
     - desc = BaseDescription()
  2) Create BaseAnalysis with datetimes and assign:
     - analysis = BaseAnalysis("Profiling run", date_start, date_end)
     - desc.analysis = analysis
  3) Populate variables and table:
     - desc.variables = {"col_a": {"type": "Numeric", "mean": 3.2}, "col_b": {"type": "Categorical", "unique": 5}}
     - desc.table = {"n_rows": 1000, "n_columns": 2}
  4) Optionally set correlations, missingness, sample, and alerts:
     - desc.correlations = {"pearson": {"col_a": {"col_b": 0.1}, ...}}
     - desc.sample = [{"col_a": 1.0, "col_b": "x"}, ...]
  5) Hand desc to renderer/serializer which reads these attributes and produces the final report.

Implementation guidance to reimplement BaseDescription:
- Implement a minimal class that only declares these attributes with type annotations.
- For convenience, prefer a dataclass with optional fields and defaults (None or empty dict) so callers can construct a populated instance in one step:
  - Example constructor signature recommendation (not enforced by original): BaseDescription(analysis: Optional[BaseAnalysis] = None, variables: Optional[Dict[str, Any]] = None, table: Optional[Any] = None, ...)
- Avoid embedding heavy validation logic; keep container semantics minimal and let analyzers enforce data shapes.

