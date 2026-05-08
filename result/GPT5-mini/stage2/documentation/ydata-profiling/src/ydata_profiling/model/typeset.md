# `typeset.py`

## `src.ydata_profiling.model.typeset.series_handle_nulls` · *function*

## Summary:
A decorator that normalizes handling of missing values for a predicate operating on a pandas Series: records whether the original series contained NaNs, drops them before invoking the predicate, and returns False if the series becomes empty after dropping NaNs.

## Description:
This decorator is intended to wrap boolean predicate functions that evaluate properties of a pandas Series during type inference. Typical callers are predicate functions in the same typeset/type-inference pipeline which have the signature (series, state, *args, **kwargs) -> bool. It is typically used during a type-detection stage where multiple predicate functions are evaluated for the same Series, and a shared mutable state dict is passed through the checks.

Reasons this logic is factored out into a decorator:
- Consolidates the common null-handling pattern (recording presence of NaNs, dropping them, and short-circuiting on fully-NA series) so individual predicates can assume they receive a NA-free Series.
- Ensures consistent state["hasnans"] behavior across predicates: the first predicate to run will populate the state entry and subsequent predicates can read it.
- Keeps predicate implementations focused on their core decision logic rather than repeated null-preparation boilerplate.

## Args:
    fn (Callable[..., bool]):
        The predicate function to wrap. Expected to accept at least the arguments:
            series: pd.Series
            state: dict
        and to return a bool. The decorator returns a wrapped function with the same boolean-returning contract.
        The wrapped function may also accept additional positional and keyword arguments (they will be forwarded).

Notes on interdependencies:
- The decorator requires the wrapped function to tolerate receiving a (possibly shorter) Series after dropna() is applied.
- The wrapped function may rely on state["hasnans"] being present after the first wrapped predicate has run; the decorator ensures it will be set on first invocation.

## Returns:
    Callable[..., bool]:
        A wrapper function with signature (series: pd.Series, state: dict, *args, **kwargs) -> bool.
        Behavior of the wrapper:
        - If "hasnans" not present in state, sets state["hasnans"] = series.hasnans (a boolean).
        - If state["hasnans"] is True:
            - Replaces series with series.dropna().
            - If the resulting series is empty, returns False immediately (the predicate is considered not satisfied for an all-NA series).
        - Otherwise (no NaNs or not all-NA after dropna), calls the original fn with the (possibly NA-trimmed) series and the same state and other args, and returns fn(...) result.

Possible return values and edge cases:
- False: returned early when the original series contained NaNs and after dropping them the series is empty.
- The boolean value returned by the wrapped fn: returned after NA handling when there remains some non-null data.
- Note: the wrapper does not convert non-boolean returns from fn; such behavior is dependent on fn (but the expected contract is a boolean).

## Raises:
    The decorator itself does not explicitly raise any exceptions.
    However:
    - Any exception raised by the wrapped predicate fn will propagate unchanged.
    - If the passed series-like object does not implement .hasnans or .dropna() as expected, an AttributeError or other pandas-related exception may occur.
    - The decorator does mutate the provided state dict; incorrect types for state (anything not a mutable mapping supporting item assignment) will raise a TypeError.

## Constraints:
Preconditions:
- series must be a pandas Series-like object that supports .hasnans and .dropna() and .empty property.
- state must be a mutable mapping (dict-like) that can store the "hasnans" boolean flag.
- The wrapped fn must accept the signature (series, state, *args, **kwargs) and return a boolean.

Postconditions:
- After the first wrapped invocation, state will contain the key "hasnans" with a boolean value describing whether the original series passed to that invocation contained any NA values.
- The wrapped predicate is invoked with a series that has had NA values removed when state["hasnans"] is True.
- No other global state or external resources are modified by the decorator.

## Side Effects:
- Mutates the provided state mapping by setting state["hasnans"] if it was absent.
- Does not perform any I/O, network calls, file system writes, or logging on its own.
- It forwards any side effects produced by the wrapped predicate fn.

## Control Flow:
flowchart TD
    Start --> CheckHasnansInState
    CheckHasnansInState{ "hasnans" in state? }
    CheckHasnansInState -->|No| SetHasnans
    SetHasnans --> HasNansFlag
    CheckHasnansInState -->|Yes| HasNansFlag
    HasNansFlag{ state["hasnans"] == True? }
    HasNansFlag -->|True| DropNA
    HasNansFlag -->|False| CallFn
    DropNA --> CheckEmpty
    CheckEmpty{ series.empty after dropna? }
    CheckEmpty -->|Yes| ReturnFalse
    CheckEmpty -->|No| CallFn
    CallFn --> ReturnResult
    ReturnFalse --> End
    ReturnResult --> End

## Examples (usage notes, no function definitions included):
- Typical scenario: a type-detection predicate that expects to operate on a non-null series is decorated so callers do not need to handle NaNs repeatedly. When the decorator runs it will:
    1) Record whether the input series originally contained NaNs into state["hasnans"] (if not already set).
    2) If NaNs were present, drop them and, if the series becomes empty, short-circuit and return False (indicating the predicate does not hold for an all-NA series).
    3) Otherwise, call the original predicate on the NA-trimmed series.

- Example invocation (conceptual):
    - series = a pandas Series that may contain NA values
    - state = {}
    - result = wrapped_predicate(series, state)
    After the call:
      - state["hasnans"] is set to True if the original series had any NaNs, otherwise False.
      - result is False if the original series was entirely NA; otherwise it is the wrapped predicate's boolean outcome on the non-null data.

- Error handling notes:
    - If the wrapped predicate relies on additional entries in state, the caller must populate them before invoking the wrapper.
    - Any exceptions from the wrapped predicate propagate; callers should catch them around the outer invocation if needed.

## `src.ydata_profiling.model.typeset.typeset_types` · *function*

*No documentation generated.*

## `src.ydata_profiling.model.typeset.Unsupported` · *class*

## Summary:
A minimal Visions type used as a sentinel to mark data (columns or values) that are unsupported or unclassifiable by the typeset. It subclasses visions.Generic and does not add behavior.

## Description:
Unsupported exists solely to provide an explicit Visions type object that signals "unsupported" data during profiling type inference and dispatch. It contains no conversions, relations, or validation logic; it is a passive marker used by the profiling pipeline when no other type applies or when a column should be excluded from type-specific handling.

When to instantiate:
- As a fallback marker when type inference fails to match any supported Visions types.
- In tests or tooling that need a concrete, recognizable Visions type to represent an unsupported classification.
- When the profiling workflow needs to tag columns to skip further type-specific processing (e.g., conversion, detailed statistics).

Motivation and responsibility:
- Motivation: make unsupported/unclassifiable data explicit in the type system so downstream code can branch on type identity instead of ad-hoc flags.
- Responsibility boundary: Unsupported only identifies unsupported data; it must not be relied upon to perform conversions, inference, or resource management. All such logic belongs to other types and relations in the typeset.

## State:
- Declared attributes: none (this class body is empty).
- Inherited attributes/state: any attributes or initialization logic come from visions.Generic; refer to visions.Generic documentation for details.
- __init__ parameters:
    - Unsupported does not implement its own __init__; instantiation uses visions.Generic.__init__.
    - Typical usage in this codebase expects no special constructor arguments, but callers must satisfy whatever signature visions.Generic.__init__ requires.
- Valid values / invariants:
    - An Unsupported instance is only an identity marker. There are no internal invariants defined in this subclass beyond those of the base class.
    - Code should not expect additional attributes, methods, or side effects from Unsupported instances.

## Lifecycle:
Creation:
- Instantiate with Unsupported(...) as needed. Because the class does not override __init__, any required constructor parameters are those of visions.Generic.
- Typical simple construction pattern (most code that uses marker types expects a no-arg construction; if this raises an error, consult visions.Generic.__init__).

Usage:
- Pattern: create or receive an Unsupported instance and use it as a sentinel in control flow.
- Common operations:
    1. Type checks: if isinstance(t, Unsupported): handle unsupported-case (skip, log, raise, or mark for special handling).
    2. Passing through generic code: code that accepts a Visions type should accept Unsupported but must not call type-specific conversion methods on it.
- No required ordering or lifecycle methods: Unsupported instances are passive and do not require setup or teardown calls.

Destruction:
- No special cleanup required; no context manager or close semantics are provided by this subclass.

## Method Map:
Minimal usage flow (Mermaid flowchart):

flowchart TD
    A[Create Unsupported instance] --> B{Use as type marker}
    B --> C[Type dispatch / branching]
    C --> D[Handle unsupported case (skip/log/record)]
    C --> E[Pass to generic handlers that tolerate Unsupported]

Notes:
- Unsupported defines no methods; the flow shows how the instance is typically routed in profiling logic.

## Raises:
- This file defines no explicit raises.
- Any exception raised on construction originates from visions.Generic.__init__ (if that constructor validates arguments or raises errors). Consult the Visions library for constructor-specific exceptions.

## Example:
A conservative example that creates the marker and demonstrates type-checking without assuming extra behavior:

import visions
from ydata_profiling.model.typeset import Unsupported

# Create the marker (no extra behavior added by this subclass)
u = Unsupported()  # If this raises, check visions.Generic.__init__ signature

# Use as a sentinel in profiling control flow
if isinstance(u, Unsupported):
    # Typical handling: skip profiling details for this column and log an informative message
    print("Column is marked as Unsupported — skipping detailed profiling.")

# The instance is a Visions subtype
assert isinstance(u, visions.Generic)

## `src.ydata_profiling.model.typeset.Numeric` · *class*

## Summary:
A Visions type describing "numeric" pandas Series (numeric dtype but not boolean), exposing type relations (including an inference path from Text) and a predicate to check whether a Series is numeric.

## Description:
Numeric is a subclass of visions.VisionsBaseType used by the type-inference and profiling machinery to:
- Identify whether a pandas.Series should be classified as numeric (explicit numeric dtype, excluding boolean).
- Provide relations so the inference engine can convert textual data to numeric values (Text -> Numeric) using a transformer.

Typical instantiation/use:
- Used by the profiling/type-inference engine when registering or checking column types.
- Callers typically retrieve relations via Numeric.get_relations() to build conversion/inference graphs, and call Numeric.contains_op(series, state) to decide if a given column is already numeric.

Why this abstraction exists:
- Centralizes the definition of numeric-ness and the allowed inference from text. It prevents scattering numeric detection logic across the codebase and makes transformations (text -> numeric) discoverable via Visions relations.

## State:
Numeric itself defines no instance attributes. Methods operate on inputs and an ephemeral state dict:

- contains_op parameters (signature exactly as implemented):
  - series (pandas.Series)
    - Type: pandas.Series
    - Post-decorator preconditions: if contains_op executes its core check, the series is non-empty and NaN-free (see Lifecycle / decorators below).
  - state (dict)
    - Type: dict
    - Usage: the series_handle_nulls decorator will set state["hasnans"] = series.hasnans if the key is not present. Callers may pass an empty dict() for a single evaluation or reuse a state dict across multiple checks in a pipeline.

Module-level names referenced (must be available at runtime):
- string_is_numeric, string_to_numeric: functions from typeset_relations used by get_relations() to decide if and how to infer numeric values from Text.
- config: a module-level configuration object referenced inside get_relations() (passed into string_is_numeric via partial). The relation callable expects this name to be defined; typically this will be an instance compatible with ydata_profiling.config.Settings.

Class invariants:
- contains_op returns True if and only if (after decorators processed the series) the series' dtype is numeric and not boolean.

## Lifecycle:
Creation:
- No constructor parameters. Create by calling Numeric() or use the class directly when registering types with Visions. The class is a static descriptor; instantiation is optional for most engines that operate on the class object.

Usage sequence (decorator and invocation details):
- get_relations()
  - Returns two TypeRelation objects:
    1. IdentityRelation(Unsupported)
    2. InferenceRelation(Text, relationship=lambda x,y: partial(string_is_numeric, k=config)(x,y), transformer=string_to_numeric)
  - Note: the relationship lambda captures and references a module-level name config; ensure this name is defined (typically a Settings instance) before the relation is evaluated, otherwise invoking the relation will raise NameError.

- contains_op(series: pandas.Series, state: dict) -> bool
  - Exact implementation signature: a @staticmethod decorated with @multimethod, @series_not_empty, and @series_handle_nulls (listed in source in that order).
  - Decorator application (bottom-to-top, as applied at runtime):
    1. series_handle_nulls (inner-most): 
       - If "hasnans" not in state, sets state["hasnans"] = series.hasnans.
       - If state["hasnans"] is True, it replaces the local series with series.dropna() before proceeding.
       - If dropna() yields an empty series, the decorator returns False immediately (contains_op not called).
    2. series_not_empty:
       - Ensures the series passed to the core check is non-empty; if empty, returns False.
    3. multimethod:
       - Enables multimethod dispatch (overload resolution) for contains_op; the presence of multimethod means contains_op participates in dispatch rules defined elsewhere.
    4. staticmethod:
       - contains_op is a static method: no self/cls parameter; call as Numeric.contains_op(series, state) or via an instance: Numeric().contains_op(series, state).

  - Core behavior (executed after decorators):
    - Uses pandas dtype predicates to decide numeric-ness:
      - Returns True exactly when the series' dtype is numeric (pandas.api.types.is_numeric_dtype) AND not boolean (not pandas.api.types.is_bool_dtype).
    - Return type: bool

Destruction:
- No resources or external connections are managed; no cleanup is required.

## Method Map:
flowchart TD
    GR[get_relations()] --> R1[IdentityRelation(Unsupported)]
    GR --> R2[InferenceRelation(Text)]
    R2 --> R2a[relationship -> partial(string_is_numeric, k=config)(x,y)]
    R2 --> R2b[transformer -> string_to_numeric]
    CO[contains_op(series,state)] --> D1[series_handle_nulls: set state["hasnans"], dropna() if needed]
    D1 --> D2[series_not_empty: return False if empty]
    D2 --> D3[multimethod dispatch layer]
    D3 --> D4[core: is_numeric_dtype(series) and not is_bool_dtype(series)]
    D4 --> RET[return True/False]

## Raises:
- NameError:
  - Trigger: get_relations() returns an InferenceRelation whose relationship lambda references module-level name config. If config is not defined when the relationship callable is executed, a NameError will be raised.
- AttributeError / TypeError:
  - Trigger: If contains_op is called with an argument that is not a pandas.Series (or does not implement .hasnans or .dropna()), the decorators or pandas dtype checks may raise AttributeError or TypeError.
- Propagated errors from relation/transformer functions:
  - string_is_numeric and string_to_numeric may raise exceptions depending on their implementation or the data passed; those exceptions propagate to the caller when the relation or transformer is invoked.

No other exceptions are raised explicitly by the Numeric class code shown.

## Example (conceptual; not executable source):
- Given a pandas Series s and an empty state dict:
  * Call Numeric.contains_op(s, state)
    - If s contains NaNs, state["hasnans"] will be set and s.dropna() will be used for the check.
    - If post-dropna the series is empty, contains_op returns False.
    - Otherwise, if s has a numeric pandas dtype and is not boolean, contains_op returns True; otherwise False.
- To discover how to convert textual columns to numeric:
  * Call Numeric.get_relations() to obtain the InferenceRelation(Text -> Numeric) that includes:
    - a relationship predicate (lambda invoking string_is_numeric with module config) and
    - a transformer string_to_numeric to perform the conversion when inference is applied.
  * Ensure a module-level config (typically a ydata_profiling.config.Settings instance) is available before evaluating the relationship; otherwise a NameError will occur.

Notes and caveats:
- contains_op is a staticmethod decorated with multimethod: it participates in multimethod dispatch and should be called with exactly two positional arguments: the pandas.Series and a dict-like state.
- The decorators enforce that contains_op's core check only runs on a non-empty, NaN-free series; callers relying on contains_op returning True can assume the input was non-empty and NaN-free at the time of the dtype check.
- The exact runtime behavior of the Text -> Numeric inference depends on the implementations of string_is_numeric/string_to_numeric and on the module-level config object referenced by the relation.

### `src.ydata_profiling.model.typeset.Numeric.get_relations` · *method*

## Summary:
Constructs and returns the relation descriptors that connect the Numeric type to other Visions types: an identity relation to Unsupported and an inference relation from Text that uses a string-to-numeric predicate and transformer.

## Description:
This static method returns the TypeRelation objects used by the Visions type-inference engine when building or querying the type-relation graph for dataset profiling. Typical callers and lifecycle stage:
- Called by the Visions framework or the VisionsBaseType machinery when the profiler or type-registry collects relations for all types (during type discovery / inference setup).
- The returned relations are later evaluated by the inference pipeline when deciding whether a given series matches Numeric (or when transforming a Text series to numeric).

Why this logic is in its own method:
- Visions expects each type to expose its relations declaratively via a standard static get_relations method. Separating relation construction into this method keeps type metadata centralized and discoverable without executing inference logic or instantiating the type.

## Args:
    None

## Returns:
    Sequence[TypeRelation]
        - A sequence (list) containing exactly two relation descriptors:
            1. IdentityRelation(Unsupported)
            2. InferenceRelation(
                   Text,
                   relationship=<callable (series: pd.Series, state: dict) -> bool>,
                   transformer=<callable (series: pd.Series, state: dict) -> pd.Series>
               )
        - The relationship callable is produced by binding the module-level configuration into string_is_numeric via functools.partial; when invoked it expects (series, state) and returns True if the Text series should be considered Numeric.
        - The transformer callable delegates to string_to_numeric and returns a pd.Series with numeric values (coerced where appropriate).
        - The method always returns a Sequence[TypeRelation]; it does not return None or other types.

## Raises:
    - NameError: If the module-level name `config` is not defined at the time this method is invoked, binding partial(string_is_numeric, k=config) will raise NameError.
    - TypeError / AttributeError: If the imported callables (string_is_numeric or string_to_numeric) are missing or not callable, creating the InferenceRelation or later invoking the returned callables will raise exceptions coming from those operations. (These exceptions originate from module-level references rather than this method's own logic.)

## State Changes:
    Attributes READ:
        - None. This is a static method and does not read or modify any self.<attr> attributes.
    Attributes WRITTEN:
        - None. The method does not mutate self or any instance attributes.

Module-level references read (not part of object state):
    - Unsupported (type used in IdentityRelation)
    - Text (type used as the source type in InferenceRelation)
    - string_is_numeric (callable used as the relationship predicate; expected signature: (pd.Series, dict, k: Settings) -> bool)
    - string_to_numeric (callable used as the transformer; expected signature: (pd.Series, dict) -> pd.Series)
    - config (module-level configuration value bound into the relationship callable; expected to be compatible with the `k` parameter of string_is_numeric)

## Constraints:
    Preconditions:
        - The module-level names listed above must be defined and importable when this method is called.
        - string_is_numeric must accept a `k` parameter compatible with the `config` value.
        - The Visions engine expects the relationship and transformer to accept (series: pd.Series, state: dict) as described; callers must pass those arguments when invoking the returned callables.

    Postconditions:
        - Returns a Sequence[TypeRelation] containing an IdentityRelation(Unsupported) and an InferenceRelation(Text, relationship=..., transformer=...).
        - The InferenceRelation's relationship callable has `config` bound (via partial) and therefore only requires (series, state) when invoked later.
        - No object (self) attributes or module-level globals are modified by this method.

## Side Effects:
    - Immediate: None. The method only constructs and returns descriptor objects.
    - Deferred: Evaluation of the returned relation callables (performed later by the type-inference engine) may perform conversions, raise exceptions, or mutate data depending on their implementations; such effects are caused by string_is_numeric, string_to_numeric, or by the code that invokes them, not by this method itself.

### `src.ydata_profiling.model.typeset.Numeric.contains_op` · *method*

## Summary:
Return True when the input pandas Series should be considered numeric: the series has a numeric dtype and is not a native boolean dtype. The call is a pure predicate and does not modify object state.

## Description:
Known callers and context:
- The typeset/type-inference dispatcher in the profiling pipeline that iterates over candidate Visions types and calls each type's contains_op for a DataFrame column. This predicate is evaluated during the profiling/type-detection stage to decide whether a column should be classified as Numeric.
- The method is declared in the Numeric Visions type class and is wrapped in the class by decorators (multimethod, series_not_empty, series_handle_nulls) in the original implementation; those wrappers handle multimethod dispatching, empty-series checks, and null-handling before this predicate executes.

Why this logic is its own method:
- Centralizes the dtype-based numeric detection rule for reuse and testing.
- Keeps the core check minimal and fast (dtype-level tests) while allowing surrounding decorators to manage empty-series and null semantics consistently.
- Separates concerns: a simple, deterministic predicate can be called wherever a numeric-membership test is needed without duplicating dtype-check logic.

## Args:
    series (pd.Series):
        A pandas Series representing a column to test. The function expects pandas dtype-inspection utilities to operate on this object (e.g., pandas.api.types.is_numeric_dtype).
    state (dict):
        A context dictionary passed by the profiling pipeline. This implementation does not read from or modify `state`; the parameter exists for API compatibility with other contains_op implementations.

## Returns:
    bool:
        - True when pandas.api.types.is_numeric_dtype(series) evaluates to True AND pandas.api.types.is_bool_dtype(series) evaluates to False.
        - False otherwise.
        Edge cases:
            - Empty Series and all-NA Series: in the original class these are typically handled by decorators (series_not_empty / series_handle_nulls). If called directly without those wrappers, pandas dtype checks may still treat empty/NA series according to pandas semantics; callers should rely on the decorators or precondition checks if vacuous truths are a concern.

## Raises:
    - The implementation contains no explicit try/except and does not raise custom exceptions.
    - Exceptions raised by pandas dtype-checking functions (for example, if `series` lacks the expected attributes or is not a pandas Series) will propagate (e.g., AttributeError or TypeError). Callers should ensure `series` is a valid pandas.Series or allow such exceptions to propagate.

## State Changes:
    Attributes READ:
        - None on a containing object (`self`). This is a static predicate and reads only the provided `series` argument.
    Attributes WRITTEN:
        - None. The function does not mutate `series`, `state`, or any external object.

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series (or an object providing dtype-inspection compatible with pandas' API).
        - In the class this function is decorated with wrappers that ensure non-empty and null-handled input; the core implementation assumes dtype checks are meaningful for the provided Series.
    Postconditions:
        - The method returns a boolean indicating numeric-membership according to the dtype-based rule described above.
        - No mutation of inputs or external state occurs.

## Side Effects:
    - None observable: the function performs only in-memory dtype checks and does not perform I/O, network access, or mutate external state.
    - CPU cost is minimal (dtype inspections are cheap); any expensive preprocessing (null-handling or emptiness checks) is expected to be performed by the surrounding decorators.

## `src.ydata_profiling.model.typeset.Text` · *class*

## Summary:
Visions type class that represents textual (string) columns for the ydata_profiling type-inference system. It defines the predicate used to decide whether a pandas Series should be classified as Text.

## Description:
Text is a subclass of visions.VisionsBaseType that exposes:
- get_relations(): static method returning relations between this type and others.
- contains_op(series: pd.Series, state: dict): static predicate determining whether a Series is textual according to the class's checks.

Intended use:
- Instances of Text are created and registered with a Visions typeset or used directly by ydata_profiling's type-inference pipeline. The inference engine calls contains_op for candidate Series during type detection.

Responsibility boundary:
- Text's responsibility is to return a boolean decision about textuality of a Series. It does not perform data mutation or conversions; it delegates content-level heuristics to helper predicates referenced in the source (e.g., series_is_string).

## State:
- The class defines no instance attributes in the provided source; it uses the default constructor inherited from visions.VisionsBaseType.
- There are no __init__ parameters defined in the shown source.
- The contains_op method accepts a `state` argument (type: dict) which is forwarded to helper predicates; Text does not define or validate keys inside this dict.

## Lifecycle:
Creation:
- Instantiate via the default constructor: Text()

Usage:
- Call Text.contains_op(series, state) to query whether a pandas Series should be treated as text by the profiling/type-inference logic.

Destruction:
- No cleanup or explicit destruction behavior is defined.

## Method Map:
graph LR
    A[Typeset / Registry] --> B[Text.get_relations()]
    A --> C[Text.contains_op(series, state)]
    C --> D[Decorators: multimethod, series_not_empty, series_handle_nulls]
    D --> E[Check: not pdt.is_categorical_dtype(series)]
    E --> F[Check: pdt.is_string_dtype(series)]
    F --> G[Check: series_is_string(series, state)]
    G -->|True| H[Return True]
    G -->|False| I[Return False]

## Methods (explicit)

get_relations() -> Sequence[TypeRelation]
- Signature: staticmethod with no parameters.
- Exact behavior in source: returns a list containing a single IdentityRelation instantiated with Unsupported:
    return [
        IdentityRelation(Unsupported),
    ]
- Return type: Sequence[TypeRelation] (as annotated in the source).
- Side effects: none in source.

contains_op(series: pd.Series, state: dict) -> bool
- Signature: staticmethod decorated with @multimethod, @series_not_empty, @series_handle_nulls and annotated as (series: pd.Series, state: dict) -> bool.
- Exact checks performed in source (all conditions must hold for the method body to return True):
    1. not pdt.is_categorical_dtype(series)
    2. pdt.is_string_dtype(series)
    3. series_is_string(series, state)
- The method body returns the boolean result of the conjunction of the three checks above.
- The decorators present in the source:
    - @multimethod — enables multimethod dispatch for the function (as applied in the source).
    - @series_not_empty — a decorator applied in the source (ensures the function is not executed on empty series per the decorator's contract).
    - @series_handle_nulls — applied in the source to apply null-handling behavior before the checks.
- Return value: bool (True iff all three checks evaluate to True after decorator processing).

## Raises:
- The source code does not explicitly raise exceptions in get_relations or contains_op.
- Possible exceptions that can propagate to callers (consistent with the code usage):
    - Exceptions raised by pdt.is_categorical_dtype or pdt.is_string_dtype if `series` does not provide the expected pandas Series interface (e.g., TypeError or AttributeError from misuse).
    - Exceptions raised by series_is_string(series, state) if that helper raises for invalid inputs or missing state keys.
- get_relations, as written, returns a sequence and does not raise in normal execution according to the source.

## Example:
1) Instantiate:
    text_type = Text()

2) Query textuality:
    result = text_type.contains_op(series=my_series, state={})
    # The call returns True exactly when:
    #   - not pdt.is_categorical_dtype(my_series) is True
    #   - pdt.is_string_dtype(my_series) is True
    #   - series_is_string(my_series, {}) returns True

3) Retrieve relations:
    relations = Text.get_relations()
    # relations is the sequence [IdentityRelation(Unsupported)] per the source.

## Implementation notes for reimplementation:
- Inherit (or mimic) visions.VisionsBaseType behavior.
- Implement get_relations as a staticmethod returning [IdentityRelation(Unsupported)].
- Implement contains_op as a static predicate decorated with multimethod, series_not_empty, and series_handle_nulls and perform the three checks in the order shown in the source:
    - not pdt.is_categorical_dtype(series)
    - pdt.is_string_dtype(series)
    - series_is_string(series, state)
- Ensure contains_op returns a boolean and does not introduce side effects in its body.

### `src.ydata_profiling.model.typeset.Text.get_relations` · *method*

## Summary:
Return the list of Visions TypeRelation objects that declare how this Text type relates to other Visions types; specifically registers an identity relation with the Unsupported type.

## Description:
This static method is used to declare type relations for the Text Visions type. The Visions type system calls such methods when constructing the relations graph or when performing type inference so it knows how types relate or can be converted to one another.

Known callers and context:
- No direct callers were found in the local repository snapshot. In practice, the Visions framework (via VisionsBaseType and the Visions relation/inference machinery) invokes get_relations on type classes during type registration and when building the relations graph used for type inference and conversion.
- This method is invoked at the type-definition / registration stage of the profiling pipeline (i.e., when the Visions-based type system is preparing or querying relations for the Text type).

Rationale for being a separate method:
- The Visions framework expects each type class to provide a get_relations method (typically a staticmethod) to supply TypeRelation declarations. Keeping this logic in its own method follows the Visions pattern: it cleanly separates relation declarations from detection/validation logic and allows the framework to discover relations via a consistent API.

## Args:
    None

## Returns:
    Sequence[TypeRelation]
    - A sequence containing TypeRelation instances that describe how this Text type relates to other types.
    - Concrete return value in this implementation:
        - [IdentityRelation(Unsupported)]
          This declares an identity relation between Text and the Unsupported Visions type.
    - Edge cases:
        - Always returns a list with a single IdentityRelation instance; never returns None or an empty list in this implementation.

## Raises:
    None

## State Changes:
    Attributes READ:
        - None (method is a staticmethod and does not read instance or class attributes)
    Attributes WRITTEN:
        - None (method is side-effect free and does not modify object state)

## Constraints:
    Preconditions:
        - None required; the method has no inputs and does not depend on external state.
        - It should be defined as a staticmethod on a VisionsBaseType-derived class for the Visions framework to discover it properly.
    Postconditions:
        - The returned value is a sequence of TypeRelation instances suitable for consumption by the Visions relation/inference subsystem.
        - Specifically, consumers can expect at least one IdentityRelation referencing Unsupported.

## Side Effects:
    - None. The method constructs and returns a small in-memory list; it performs no I/O, network calls, or mutations of objects outside the returned list.

### `src.ydata_profiling.model.typeset.Text.contains_op` · *method*

## Summary:
Return True when a pandas Series should be classified as textual: the series is not categorical, has a string-like dtype, and passes an element-level string-consistency check. This predicate does not modify object state.

## Description:
Known callers and context:
- The typeset/type-inference dispatcher in the profiling pipeline that iterates candidate Visions types and calls each type's contains_op for a DataFrame column. This predicate is evaluated during the profiling/type-detection stage to decide whether a column should be classified as Text.
- In the class definition this method is wrapped by decorators (multimethod, series_not_empty, series_handle_nulls). Those wrappers perform multimethod dispatching, ensure the series is non-empty, and handle nulls before this core predicate runs.

Why this logic is its own method:
- Encapsulates the Text-detection policy (dtype-level checks plus a content-consistency check) in a single, testable predicate.
- Keeps dtype/element-level checks separated from decorators and higher-level pipeline logic (null-handling, emptiness guards, registration).
- Reusable by any component that needs to determine whether a Series contains textual data without duplicating checks.

## Args:
    series (pandas.Series):
        Column values to test. Expected to be a pandas Series (or Series-like) with accessible .values and dtype semantics compatible with pandas' dtype-inspection utilities.
    state (dict):
        Context dictionary passed through the type-detection pipeline. This function does not mutate `state`; it forwards it to the helper series_is_string for possible context-aware checks.

## Returns:
    bool:
        - True when all of the following hold:
            * pandas.api.types.is_categorical_dtype(series) is False (i.e., the Series is not a pandas 'category' dtype),
            * pandas.api.types.is_string_dtype(series) is True (the Series is string/object-like according to pandas),
            * series_is_string(series, state) returns True (an element-level check confirming the series values are actual strings and consistent with str-casting).
        - False otherwise.
        Edge-case notes:
            - If the surrounding decorators (series_not_empty / series_handle_nulls) are not applied, an empty Series may evaluate to True due to vacuous truths in the helper checks; the class-level decorators are intended to prevent such cases during normal use.

## Raises:
    - The implementation has no explicit try/except around the three checks. Therefore:
        - Exceptions raised by pandas' dtype-checking functions (e.g., AttributeError if `series` is not a pandas Series) will propagate.
        - The called helper series_is_string catches TypeError and ValueError around its casting/comparison step, so those specific exceptions are handled by the helper and will not propagate from that code path.
    - Callers should pass a valid pandas.Series to avoid type-related exceptions.

## State Changes:
    Attributes READ:
        - None on `self` (this is a static predicate defined within the Text type and does not access instance attributes).
    Attributes WRITTEN:
        - None. The function does not mutate `series`, `state`, `self`, or any external object.

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series (or Series-like) with dtype semantics compatible with pandas.api.types helpers.
        - The type-detection framework is expected to apply decorators at the class level: @series_not_empty and @series_handle_nulls (ensures the Series is non-empty and nulls are handled before this predicate runs). Without those, empty or null-containing Series can lead to vacuous True/False behavior dependent on pandas semantics.
    Postconditions:
        - The method returns a boolean indicating whether the Series is textual according to the three checks described above.
        - No inputs or external state are modified.

## Side Effects:
    - None observable: performs only in-memory dtype and value inspections and calls the pure helper series_is_string; no I/O, network access, or persistent state mutation occurs.
    - CPU cost is minimal (dtype checks and short element-level checks). The element-level helper inspects only a small sample and performs a vectorized equality check; cost scales with series size but is generally low compared to I/O-bound operations.

## Implementation notes and reimplementation hints:
    - Use pandas dtype inspection helpers: is_categorical_dtype(series) and is_string_dtype(series) (the code uses these via the pdt alias).
    - Delegate element-level verification to series_is_string(series, state), which:
        * Verifies a small sample (first up to 5 values) are str instances,
        * Attempts to confirm that series.astype(str).values equals the original values elementwise, returning False if casting/comparison raises TypeError/ValueError.
    - Keep this predicate pure and side-effect free; apply null/empty guards and multimethod dispatch at the wrapper/decorator level rather than inside this function.

## `src.ydata_profiling.model.typeset.DateTime` · *class*

*No documentation generated.*

### `src.ydata_profiling.model.typeset.DateTime.get_relations` · *method*

## Summary:
Provides the static list of TypeRelation descriptors that declare how the DateTime Visions type relates to other types; returns the list without modifying any state.

## Description:
This staticmethod is defined on the DateTime Visions type and is used by the type-discovery / relation-collection stage of the Visions-based inference pipeline. Callers include code that inspects Visions types to build relation graphs or to determine allowed inferences for a dataset (for example, any code that iterates VisionsBaseType subclasses and calls their get_relations methods).

The method exists as its own static factory so relation declarations are:
- Declarative and discoverable without instantiating the type,
- Easy to test in isolation,
- Clearly separated from runtime inference logic that evaluates relationships or runs transformers.

## Args:
    None

## Returns:
    Sequence[TypeRelation]: A list containing exactly two TypeRelation instances in this order:
        1) IdentityRelation(Unsupported)
           - Constructed by directly calling IdentityRelation with the Unsupported type.
           - Conveys an identity-style relation involving the Unsupported type (as declared in the code).
        2) InferenceRelation(Text, relationship=lambda x, y: partial(string_is_datetime)(x, y), transformer=string_to_datetime)
           - Constructed by calling InferenceRelation with:
               - First positional argument: Text (the related Visions type).
               - relationship keyword: a lambda expression defined as lambda x, y: partial(string_is_datetime)(x, y).
                 This lambda, when invoked, calls partial(string_is_datetime) and immediately invokes it with the provided (x, y) arguments; in effect it forwards the two arguments to string_is_datetime via functools.partial.
               - transformer keyword: the object referenced by the name string_to_datetime (a callable imported in the module).
           - Purpose in the relation list: declares that DateTime can be inferred from Text under the predicate defined by the relationship callable and that string_to_datetime should be used as the transformer descriptor associated with that inference.

Edge cases:
    - The method itself always returns the same list literal; it does not return None or an empty sequence.
    - Any runtime errors that occur when the relation callables or transformer are later invoked (e.g., if string_is_datetime or string_to_datetime raise) are not raised by get_relations itself.

## Raises:
    None. The method constructs and returns relation objects only; it does not execute the relationship or transformer callables.

## State Changes:
    Attributes READ:
        - None on self (method is a staticmethod and does not access instance attributes).
        - Reads module-level names Text, Unsupported, partial, string_is_datetime, and string_to_datetime (these must be defined/imported for this function to construct the relations).
    Attributes WRITTEN:
        - None (no mutation of object, module, or global state).

## Constraints:
    Preconditions:
        - This function must be called in a context where IdentityRelation and InferenceRelation are available (they are imported in the module).
        - The symbols Text and Unsupported must be defined Visions types in the same module/scope.
        - string_is_datetime and string_to_datetime must be defined in the import scope (they are referenced by name).
    Postconditions:
        - The caller receives a Sequence[TypeRelation] of length 2 where:
            * element 0 is an IdentityRelation constructed with Unsupported
            * element 1 is an InferenceRelation constructed with Text and the specific relationship lambda and transformer reference shown in the source

## Side Effects:
    - None. The method performs no I/O and does not mutate external state; it only constructs and returns relation descriptor objects.

## Usage note:
    - Typical usage is to enumerate get_relations() across VisionsBaseType subclasses during the setup or analysis phase of type inference. The relationship and transformer values returned here are descriptors; they are expected to be invoked later by the inference engine (not by get_relations).

### `src.ydata_profiling.model.typeset.DateTime.contains_op` · *method*

## Summary:
Returns True when the provided pandas Series should be considered datetime-like by either being a pandas datetime64 dtype or by containing only built-in datetime.date / datetime.datetime objects among its non-missing values.

## Description:
This function is used as the "contains" operation for a DateTime type checker: it determines whether a candidate series contains datetime-like values so that a higher-level type-inference routine can classify the series as a datetime type. Typical callers are the type-detection machinery that iterates over candidate types for a column during profiling or schema inference; it is invoked during the type-detection / inference stage of the profiling pipeline. This logic is kept in its own callable because the check requires two distinct tests (a fast dtype-based test and a slower per-element type check on non-null values) and is reused wherever a boolean predicate is needed to decide whether a series belongs to the DateTime type.

## Args:
    series (pd.Series):
        A pandas Series representing a column of data to test. The function expects Series methods like dropna(), apply(), and dtype inspection to be available.
    state (dict):
        A dictionary intended to hold contextual state for the type-checking process. This implementation does not read or modify state; the argument is accepted for API compatibility with the type-checking framework.

## Returns:
    bool:
        - True if at least one of the following holds:
            * The series has a pandas datetime64 dtype (pdt.is_datetime64_any_dtype(series) is True).
            * All non-missing values in the series are instances of datetime.date or datetime.datetime.
        - False otherwise.
        Edge cases:
            - If the series is empty or all values are missing (after dropna() the Series is empty), the per-element check (.all() on an empty boolean Series) evaluates to True, causing the function to return True unless the dtype check already returned True. In other words, an all-NA series will make the fallback check evaluate to True; callers should be aware of this vacuous-true behavior.

## Raises:
    There are no explicit raises in the implementation. However:
        - AttributeError or similar exceptions may be raised if the provided `series` does not behave like a pandas Series (missing expected methods such as dropna or apply).
        - Any exceptions raised by pdt.is_datetime64_any_dtype(...) or by the element-wise type() call will propagate to the caller.

## State Changes:
    Attributes READ:
        - None on a containing object (function is stateless). The function reads only the provided `series` argument.
    Attributes WRITTEN:
        - None. The function does not mutate the series or any external objects.

## Constraints:
    Preconditions:
        - `series` should be a pandas Series or an object that provides dropna(), apply(), and dtype inspection compatible with pandas.
        - The function expects that element types can be inspected with Python's built-in type().
    Postconditions:
        - The function returns a boolean indicating whether the series is considered datetime-like according to the two checks described above. No mutation of inputs or external state occurs.

## Side Effects:
    - None observable: the function does not perform I/O, network access, or mutate objects outside of local temporaries. It does not change the provided `series` (dropna() and apply() are called on temporary intermediate Series).

## `src.ydata_profiling.model.typeset.Categorical` · *class*

## Summary:
Represents the "categorical" data type in the Visions-based typing system used by the profiling library. It defines how to recognize categorical pandas Series and how categorical type relates to other types (e.g., Numeric, Text) for inference and transformation.

## Description:
The Categorical class is a Visions type subclass that:
- Determines whether a pandas Series should be considered categorical (contains_op).
- Declares type relations used by the Visions type-inference engine (get_relations): which other types can be inferred as categorical and which transformers/relationship checks to use.

When to instantiate:
- You normally do not need to instantiate this class directly; the Visions type system or the profiling framework registers and instantiates it when constructing the set of types for dataset inference.
- It can be instantiated manually with no constructor arguments if you need to register or test it in isolation.

Why it exists:
- Separates the categorical-type identification logic from other type logics (Numeric, Text, Unsupported).
- Provides the inference rules (relations) describing how and when other types or values should be treated as categorical (including the transformer to convert values into categories).

## State:
This class defines no instance attributes of its own; it relies on inherited behavior from visions.VisionsBaseType. The only state passed into its operations is the per-call state dict used by contains_op and by the decorators.

Relevant per-call state keys:
- "hasnans" (bool): Set by the series_handle_nulls decorator when contains_op is invoked. Indicates whether the original series had missing values. If present, callers and other decorated functions can read this key.

Invariants:
- Instances of Categorical are stateless beyond the VisionsBaseType inheritance.
- contains_op (after decorator processing) always receives a pandas Series that is free of NaN values (unless the decorator returned early because dropna() produced an empty Series). The decorator also ensures contains_op is only called with a non-empty series.

## Lifecycle:
Creation:
- Instantiate with no arguments: Categorical()
- Typical construction is managed by the Visions framework; no configuration arguments are required.

Usage (typical sequence):
1. get_relations() — static method that returns the TypeRelation list:
   - IdentityRelation(Unsupported)
   - InferenceRelation(Numeric, relationship=partial(numeric_is_category, k=config), transformer=to_category)
   - InferenceRelation(Text, relationship=partial(string_is_category, k=config), transformer=to_category)
   These relations allow numeric or textual series to be inferred as categorical under the specified relationship predicates, and define to_category as the transformer to perform the conversion.
2. contains_op(series, state) — static method used by the Visions engine to check whether a given pandas Series is categorical.
   - Note: contains_op is decorated by:
     - @series_not_empty: ensures empty series are rejected before evaluating.
     - @series_handle_nulls: will record state["hasnans"] and pass series.dropna() to the wrapped function; if dropna() yields an empty Series, the decorator returns False without calling the wrapped function.
     - @multimethod: registers this implementation for method-dispatch in multimethod-based overloading.
   - The actual runtime check: returns True when the series has categorical dtype and is not a boolean dtype (see Raises for edge cases).
3. No explicit destruction or cleanup is required.

Destruction:
- No cleanup, context-management, or close() responsibilities.

## Method Map:
flowchart LR
    A[get_relations()] --> B[IdentityRelation(Unsupported)]
    A --> C[InferenceRelation(Numeric)]
    C --> C1[relationship: partial(numeric_is_category, k=config)]
    C --> C2[transformer: to_category]
    A --> D[InferenceRelation(Text)]
    D --> D1[relationship: partial(string_is_category, k=config)]
    D --> D2[transformer: to_category]
    E[contains_op(series, state)]
    F[@series_handle_nulls -> records state["hasnans"], uses series.dropna()]
    G[@series_not_empty -> ensures non-empty series]
    H[@multimethod -> enables overload dispatch]
    E --> F --> G --> H

(Interpretation: contains_op is wrapped by series_handle_nulls then series_not_empty and registered as a multimethod; get_relations returns identity and inference relations using numeric/string predicates and to_category transformer.)

## Behavior (contains_op):
Signature:
- contains_op(series: pandas.Series, state: dict) -> bool

What it checks:
- After decorator preprocessing (NaN removal and non-empty guarantee), it returns True exactly when:
  - pandas.api.types.is_categorical_dtype(series) is True
  - and pandas.api.types.is_bool_dtype(series) is False

Otherwise returns False.

Decorator effects (important):
- series_handle_nulls:
  - If "hasnans" is not in state, it sets state["hasnans"] = series.hasnans.
  - If the series has NaNs, the decorator calls series.dropna(); if the resulting series is empty, the decorator returns False without invoking contains_op.
  - The wrapped contains_op therefore never observes NaNs and may assume the series has no missing values.
- series_not_empty:
  - Ensures the series passed to contains_op is not empty. If empty, it will short-circuit and the type is not considered present.

## Raises:
Potential exceptions and when they occur:
- AttributeError:
  - If the caller passes a non-pandas object (e.g., None or a plain list) that lacks the pandas-like attributes used by the decorators or the body — particularly .hasnans or .dropna() — the series_handle_nulls decorator will attempt to access series.hasnans and will raise AttributeError.
- Any pandas-related errors:
  - If pandas.api.types.is_categorical_dtype or is_bool_dtype are called with incompatible inputs, pandas may raise TypeError or other exceptions.
- No exceptions are explicitly raised by Categorical.__init__ or contains_op itself in the implementation; errors generally stem from incorrect argument types or from the behavior of the decorators and pandas API.

## Example:
1) Typical check for a pandas categorical Series (happy path)
   - Prepare a pandas Series with categorical dtype (no NaNs):
     pandas.Series(pandas.Categorical(["a", "b", "a"]))
   - Call contains_op with an empty state dict:
     state = {}
     Categorical.contains_op(series, state)  -> returns True
   - After call, state may contain "hasnans" (False in this example).

2) Series with NaNs:
   - Input series = pandas.Series(pandas.Categorical(["a", None, "b"]))
   - The series_handle_nulls decorator sets state["hasnans"] = True and passes series.dropna() to the inner function.
   - If dropna() yields a non-empty categorical Series, contains_op evaluates dtype and returns accordingly.
   - If all values were NaN and dropna() yields an empty Series, the decorator returns False and contains_op is not invoked.

3) Non-categorical Series:
   - Numeric or textual series that are not categorical will cause contains_op to return False; the Visions framework may still infer categorical via get_relations if relationship predicates (numeric_is_category/string_is_category) evaluate True and a transformer (to_category) can convert them.

Notes and cautions:
- get_relations uses functions numeric_is_category and string_is_category with an external variable config via partial(..., k=config). The behaviour of those relationship functions depends on that external config object (not defined in this class), so inference thresholds/heuristics are governed by the profiling configuration.
- Categorical treats boolean dtypes specially: a series whose dtype is boolean (or recognized as boolean by pandas) is explicitly not considered categorical by contains_op.

### `src.ydata_profiling.model.typeset.Categorical.get_relations` · *method*

## Summary:
Returns the TypeRelation descriptors that define how the Visions type system should recognize or infer the categorical type; the method does not modify object state.

## Description:
Known callers and context:
- Called by the Visions type-registration / type-inference machinery when assembling the relation graph for the Categorical type (for example during Visions' type discovery, type graph construction, or when checking whether another series can be inferred as categorical).
- The returned relations are consulted later during type inference; the relationship callables contained in the InferenceRelation entries will be invoked with a pandas Series and a state dict.

Why this is a separate method:
- Encapsulates all relation declarations for the Categorical type in one place so the Visions system can query them without instantiating objects or inlining relation construction logic.
- Keeps relation construction declarative and testable separately from containment checks and transformation logic.

## Args:
    None

## Returns:
    Sequence[TypeRelation]
    - A list with exactly three relation descriptors (in the order returned by the implementation):
        1) IdentityRelation(Unsupported)
           - Declares that Unsupported is an identity-related (fallback) type for Categorical.
        2) InferenceRelation(Numeric, relationship=..., transformer=to_category)
           - The relationship callable has the signature (series: pandas.Series, state: dict) -> bool.
           - The callable wraps numeric_is_category with k=config; when invoked it will return True if a numeric series should be considered categorical according to current configuration settings.
           - If that callable returns True, the transformer to_category(series, state) will be used to convert the series into the categorical-compatible representation (pandas "string" dtype in this codebase).
        3) InferenceRelation(Text, relationship=..., transformer=to_category)
           - The relationship callable wraps string_is_category with k=config; when invoked it will return True if a text series should be treated as categorical according to current configuration settings.
           - Uses the same to_category transformer on success.
    - Edge-case/notes:
        - The method always constructs and returns a list of three TypeRelation objects (it does not conditionally return an empty list).
        - The relationship callables are created as lambdas that close over a module-level variable named config; actual evaluation of those callables may raise errors if config is misconfigured or missing.

## Raises:
    - NameError: If the module-level symbol config is not defined (or becomes undefined) when the relationship callables are later invoked, a NameError will be raised at call time. The method itself constructs lambdas that reference config; missing config will not necessarily raise during this method call but will surface when the relationships are evaluated.
    - Any exception raised by the referenced constructor functions or classes during import-time (e.g., if IdentityRelation/InferenceRelation or the referenced type classes are not available) will surface as the normal Python errors; such import-time issues are not produced by this method's logic itself.

## State Changes:
    Attributes READ:
        - None (method is a staticmethod and does not access self.<attr>).
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The module-level symbol config should exist and be a Settings-like object expected by numeric_is_category and string_is_category (the lambdas pass k=config).
        - The referenced symbols (Unsupported, Numeric, Text, numeric_is_category, string_is_category, to_category, IdentityRelation, InferenceRelation, TypeRelation) must be available in the module namespace (they are imported at module scope in the file).
    Postconditions:
        - On successful return the caller receives a Sequence[TypeRelation] describing:
            * an identity relation for Unsupported and
            * two inference relations that indicate how Numeric and Text series can be considered categorical (including their transformer to_category).
        - No mutation of the Categorical class or other runtime state is performed by this call.

## Side Effects:
    - None intrinsic to this method (no I/O, no external service calls).
    - The method creates lambda callables that capture the module-level config variable; any side effects occur later when those callables are invoked (for example, transformer to_category will convert a pandas Series to string dtype and may allocate memory).

### `src.ydata_profiling.model.typeset.Categorical.contains_op` · *method*

## Summary:
Return True when the provided Series should be identified as a categorical variable: the Series has pandas 'category' dtype and is not a native boolean dtype. The call is a pure predicate and does not mutate object state.

## Description:
This predicate is invoked by the profiling/typeset type-detection pipeline when deciding whether a column should be classified as a Categorical type. It is typically called by the typeset dispatcher that iterates over candidate Visions types and calls each type's contains_op for a given pandas Series.

The Categorical detection is separated into its own method to centralize the dtype-level logic that distinguishes categorical series from other types (notably boolean and numeric types). The method is decorated (in the class) with helpers that guard against empty series and handle nulls before this check is applied, so the core logic remains simple and focused on dtype checks.

Known callers and context:
- The typeset/type-inference dispatcher within the profiling pipeline that tests each type's contains_op to select the best-fitting type for a DataFrame column.

Why this is a separate method:
- Keeps categorical-detection rules in one place for reuse and testing.
- Avoids repeating dtype-check patterns across the typeset.
- Allows decorators (e.g., non-empty and null-handling wrappers) to be applied consistently around this central predicate.

## Args:
    series (pd.Series):
        The pandas Series to inspect. Expected to be a pandas.Series instance containing the column values to classify.
    state (dict):
        Context dictionary passed by the profiling pipeline. This implementation does not read or depend on any keys in this dict; it exists for signature compatibility with other contains_op implementations.

## Returns:
    bool:
        True if and only if:
        - pandas.api.types.is_categorical_dtype(series) evaluates to True, AND
        - pandas.api.types.is_bool_dtype(series) evaluates to False.
        Otherwise returns False.

        Edge-case returns:
        - If the Series is categorical (dtype 'category') the method returns True even if the category values are booleans (because the dtype is 'category', not a native boolean dtype).
        - If the Series is a native boolean dtype (e.g., dtype bool), the method returns False (this avoids misclassifying native boolean columns as categorical).

## Raises:
    Exceptions raised by pandas type-checking functions (e.g., TypeError) may propagate if the `series` argument is not a valid pandas Series or contains values that cause pandas' dtype checks to error. The implementation itself does not catch these exceptions.

## State Changes:
    Attributes READ:
        None (this is a static predicate and does not read attributes on `self`; it only reads the provided `series` argument).
    Attributes WRITTEN:
        None (no mutation of `self`, `series`, or `state`).

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series instance. Passing other types may cause pandas to raise.
        - The class-level decorators applied around this method in the original implementation (e.g., series_not_empty, series_handle_nulls) imply that callers should expect empty-series and null-handling to be managed outside or by those wrappers; the core method assumes dtype checks are meaningful for the provided Series.
    Postconditions:
        - The method returns a boolean and does not modify `series` or `state`.
        - The decision strictly reflects the dtype-based rule described above.

## Side Effects:
    - No I/O, logging, or network activity.
    - No mutation of input Series or external objects.
    - Minimal CPU cost: this method performs only dtype checks, which are inexpensive; any expensive preprocessing (null handling, emptiness checks) is expected to be done by the surrounding decorators.

## Implementation notes and reimplementation hints:
    - Use pandas.api.types.is_categorical_dtype(series) to detect category dtype.
    - Use pandas.api.types.is_bool_dtype(series) to detect native boolean dtype.
    - Return the boolean result of (is_categorical_dtype(series) and not is_bool_dtype(series)).
    - Keep the method pure (no side effects). If decorators for empty-series and null-handling are available in your environment, apply them at the wrapper level rather than inside this function.

## `src.ydata_profiling.model.typeset.Boolean` · *class*

## Summary:
A Visions type representing boolean data (True/False) used by ydata_profiling's type-inference pipeline. It contains logic to detect boolean-valued pandas Series and to define how Text Series can be inferred and transformed into boolean dtype using a configurable mapping.

## Description:
Boolean centralizes two responsibilities:
- Detection: provides contains_op which the typeset/type-inference dispatcher calls to determine whether a pandas Series should be considered Boolean.
- Inference/Transformation: get_relations declares relations (including an InferenceRelation from Text) and supplies a transformer to convert textual Series to Boolean using the configured mapping (config.vars.bool.mappings).

Instantiation and callers:
- Typically instantiated/queried by the ydata_profiling typeset/type-inference dispatcher or by Visions when constructing a TypeSet. Direct instantiation via Boolean() is allowed but uncommon.
- The typeset/type-inference dispatcher iterates candidate types and calls each type's contains_op(series, state) to decide which type best describes a variable. Separately, the system queries get_relations() to learn how other types relate to Boolean (for example, to allow Text to be inferred as Boolean).

Motivation:
- Consolidates boolean detection and text→boolean inference logic in a single abstraction, relying on a configurable token-to-boolean mapping so textual boolean representations (e.g., "true"/"false", "y"/"n") can be recognized and converted consistently.

## State:
- Instance attributes: none defined in Boolean; it is effectively stateless beyond VisionsBaseType inherited behavior.
- External state dependencies:
  - config.vars.bool.mappings: expected to be a mapping-like object (Dict[str, bool]) used by get_relations to construct the relationship tester and transformer. The string-matching code lowercases series values before matching, so mapping keys should be provided in lowercase or be case-insensitively meaningful.
- Invariants:
  - Methods expect a pandas.Series for series arguments and a dict for state.
  - The mapping should map textual tokens to boolean values; string-based inference assumes mapping keys enumerate all acceptable tokens.

## Lifecycle:
Creation:
- Use Boolean() with no arguments. No special constructor parameters.

Usage (call order and responsibilities):
1. get_relations()
   - Called by the typeset/type-inference construction logic or Visions when discovering relations.
   - Returns:
     - IdentityRelation(Unsupported): declares an identity relation to the Unsupported type (i.e., relation entry referencing Unsupported).
     - InferenceRelation(Text, relationship, transformer):
       - relationship = partial(string_is_bool, k=mapping), where mapping = config.vars.bool.mappings. This callable returns True when the (NaN-free) Text Series consists only of tokens present among mapping.keys().
       - transformer = lambda s, st: to_bool(partial(string_to_bool, k=mapping)(s, st)). This maps tokens to booleans (string_to_bool) then casts to an appropriate boolean dtype (to_bool), preserving NaNs via a nullable boolean dtype when necessary.
2. contains_op(series: pd.Series, state: dict) -> bool
   - Declared as a @staticmethod. The typeset/type-inference dispatcher calls this method for candidate types when evaluating a Series.
   - Decorators present (from outer to inner in source order):
       - @staticmethod
       - @multimethod (enables Visions/multimethod infrastructure to register/dispatch overloads)
       - @series_not_empty (ensures non-empty series; if empty, contains_op returns False)
       - @series_handle_nulls (drops NaNs before invoking the function body; if dropna produces empty series, contains_op returns False)
   - Effective runtime behavior (after NaN removal and non-empty check):
       - If pandas treats the series as object dtype (pdt.is_object_dtype(series)):
           - Attempts to evaluate series.isin({True, False}).all() to confirm every entry is exactly True or False.
           - Any exception raised by this membership test (for example, due to unhashable or unexpected element types) is caught and causes the method to return False (exceptions are suppressed).
       - Otherwise, returns pdt.is_bool_dtype(series), the standard pandas dtype check for boolean dtypes.
   - Return value: True if the Series represents boolean values (after the decorators' NaN and emptiness handling); otherwise False.
3. Transformation flow (when Text is identified as convertible to Boolean):
   - relationship (string_is_bool) is evaluated first to confirm tokens match mapping keys.
   - transformer (string_to_bool then to_bool) maps lowercased tokens to booleans and casts the resulting Series to an appropriate boolean dtype, preserving NaNs such that the final Series may have a nullable boolean dtype.

Destruction:
- No cleanup or resource management required.

## Method Map:
flowchart LR
    GR[get_relations()] --> M[reads config.vars.bool.mappings]
    M --> R1[IdentityRelation(Unsupported)]
    M --> R2[InferenceRelation(Text)]
    R2 --> Rel[relationship = partial(string_is_bool, k=mapping)]
    R2 --> Trans[transformer = lambda s, st: to_bool(partial(string_to_bool,k=mapping)(s, st))]
    CO[contains_op(series, state)]
    CO --> Multi[multimethod registration]
    Multi --> NotEmpty[series_not_empty -> returns False if empty]
    NotEmpty --> DropNa[series_handle_nulls -> dropna() if hasnans; False if empty after dropna]
    DropNa --> Body[if object dtype: try series.isin({True, False}).all() except -> False; else pdt.is_bool_dtype(series)]

## Raises:
- __init__: no explicit exceptions thrown by Boolean.__init__ itself.
- get_relations:
  - Accessing config.vars.bool.mappings may raise NameError/AttributeError if the expected configuration object or structure is not available in module scope; callers must ensure the profiling configuration is initialized.
- contains_op:
  - Suppresses exceptions arising from the object-dtype membership test and returns False instead.
  - If a non-pandas.Series is passed, attribute access in decorators or dtype checks (e.g., series.hasnans, series.dropna(), pdt.is_object_dtype) may raise AttributeError or TypeError; callers are responsible for passing a pandas.Series.

## Example:
- Detecting boolean Series:
    import pandas as pd
    s = pd.Series([True, False, True])
    state = {}
    Boolean.contains_op(s, state)  # returns True

- Inferring Boolean from Text using the configured mapping:
    # Suppose config.vars.bool.mappings == {"true": True, "false": False, "y": True, "n": False}
    import pandas as pd
    s_text = pd.Series(["True", "false", "Y", None])
    # The typeset/type-inference pipeline will:
    # 1) call relationship = partial(string_is_bool, k=mapping)(s_text, state)
    #    -> string_is_bool lowercases tokens and checks membership in mapping.keys() (NaNs ignored)
    # 2) if True, call transformer -> to_bool(string_to_bool(s_text, state, k=mapping))
    #    -> string_to_bool maps tokens to booleans; to_bool casts result to bool or nullable boolean dtype
    # Result: a boolean-typed pandas Series where None/NaN values are preserved appropriately.

### `src.ydata_profiling.model.typeset.Boolean.get_relations` · *method*

## Summary:
Returns the type-relations that connect the Boolean type to other types; declares how to infer a Boolean from textual data and the identity relation to Unsupported. This does not mutate the object state.

## Description:
This static method is called during the type-inference relation construction stage of the Visions-based type system used by the profiler. Typical callers:
- The Visions relation/registry builder when gathering relations for all types prior to inference.
- Any module that builds a type graph or asks "what relations does Boolean expose?" during the profiling pipeline initialization.

Rationale for being a separate method:
- The Visions type system expects each type class to expose its relations via a dedicated get_relations function. Keeping this logic separate keeps relation declarations declarative and discoverable (no inlined mapping or transformation logic elsewhere).

Function behavior summary:
- Reads the module-level configuration for boolean string mappings.
- Returns a fixed sequence of two TypeRelation objects:
  1. IdentityRelation pointing to Unsupported.
  2. InferenceRelation from Text into Boolean with:
     - relationship callable: uses string_is_bool with the mappings to decide whether a Text series should be considered Boolean.
     - transformer callable: maps textual values to booleans via string_to_bool, then casts to an appropriate boolean dtype via to_bool.

## Args:
This method takes no arguments.

## Returns:
Sequence[TypeRelation]
- A list/sequence containing exactly two TypeRelation instances:
  - IdentityRelation(Unsupported)
  - InferenceRelation(Text, relationship=..., transformer=...)
- Edge cases:
  - If the returned mapping is empty, the relationship and transformer still get created but the relationship will normally return False for textual series (no mapping keys to match) and the transformer will map to NA for unmapped strings.

## Raises:
- NameError: if the module-level symbol used to access configuration (config) is undefined.
- AttributeError: if config exists but lacks the nested attributes (vars, vars.bool, or vars.bool.mappings).
- TypeError/ValueError (indirect): if config.vars.bool.mappings is present but is not a mapping suitable for string mapping functions (e.g., not supporting keys()/get()/mapping behavior) then downstream calls (string_is_bool/string_to_bool) may raise other exceptions when those callables are invoked. Note: this method itself does not catch these errors.

## State Changes:
Attributes READ:
- None of self.<attr> (this is a staticmethod).
- Reads module-level symbol: config (specifically config.vars.bool.mappings). This is not a self attribute.

Attributes WRITTEN:
- None. The method does not modify any self attributes or module-level state.

## Constraints:
Preconditions:
- The module-level configuration object named config must exist and expose config.vars.bool.mappings.
- config.vars.bool.mappings should be a mapping from lowercase string tokens to boolean values (e.g., {"true": True, "false": False, "yes": True}). The string-related helper functions expect that the mapping's keys are comparable to lower-cased string values from a Series.
- Text, Unsupported, string_is_bool, string_to_bool and to_bool must be available in the module scope with the documented behaviors:
  - string_is_bool(series, state, k) -> bool: tests whether a textual series matches known boolean tokens using mapping k.
  - string_to_bool(series, state, k) -> pd.Series: maps textual values to boolean values using mapping k.
  - to_bool(pd.Series) -> pd.Series: casts/returns a boolean dtype (possibly a nullable boolean dtype if NaNs present).

Postconditions:
- The returned sequence contains two TypeRelation objects configured as described above.
- No global or object state is modified by this method.

## Side Effects:
- None (no I/O, no external service calls, no mutation of objects other than returning new TypeRelation instances).
- Note: while this function only constructs and returns relation objects, those relation objects capture callables (relationship and transformer) which will, when later invoked during inference, read the same mapping and operate on pd.Series objects; such invocations may cause exceptions if the mapping is malformed.

## Implementation notes (for reimplementation):
- Read mapping once at call time as mapping = config.vars.bool.mappings.
- Create IdentityRelation pointing at the Unsupported type/marker.
- Create an InferenceRelation from Text where:
  - relationship is a callable that, when invoked with (series, state), returns partial(string_is_bool, k=mapping)(series, state). The implementation may use a lambda that wraps partial(string_is_bool, k=mapping).
  - transformer is a callable that, when invoked with (series, state), returns to_bool(partial(string_to_bool, k=mapping)(series, state)).
- Return a Sequence (list or tuple) containing the IdentityRelation and the InferenceRelation in that order.

### `src.ydata_profiling.model.typeset.Boolean.contains_op` · *method*

## Summary:
Determines whether a pandas Series should be classified as boolean: returns True when the Series is of a native boolean dtype or, for object-dtype Series, when every element is exactly the True or False literal.

## Description:
This function implements the boolean membership check used during the dataset profiling type-detection step. It is invoked by the typeset/type-inference dispatcher that iterates over candidate types and calls each type's contains_op to decide which type best describes a variable. The check is isolated because boolean detection requires two different strategies depending on the Series dtype:
- A fast dtype-level test for native boolean dtypes.
- A value-level membership test for object-dtype Series to detect Python True/False literals while guarding against runtime errors from heterogeneous object contents.

Known callers and context:
- Called during the profiling/type-inference phase by the typeset dispatcher that evaluates each typeset's contains_op for a given Series. The function is intended to be a pure predicate used in the pipeline that selects the Boolean type when it returns True.

Why separate:
- Centralizes boolean-detection policy and exception handling. Object-dtype value inspection can raise exceptions for certain content; keeping this logic separate ensures consistent handling (the function suppresses such exceptions and returns False) without scattering try/except logic throughout the pipeline.

## Args:
    series (pd.Series):
        The pandas Series to inspect. Expected to be a pandas.Series instance containing the column values to classify.
    state (dict):
        Context dictionary passed by the profiling pipeline. This function does not read or depend on any keys in this dict (it is accepted for signature compatibility with other contains_op implementations).

## Returns:
    bool:
        True if the Series should be considered boolean according to these rules:
        - If the Series has object dtype: returns True when series.isin({True, False}).all() evaluates to True (every element is exactly True or False). If the membership test raises any exception, this branch returns False.
        - Otherwise: returns True when the Series has a boolean dtype according to pandas (i.e., pandas' boolean dtype detection).
        In all other cases, returns False.

## Raises:
    None propagated.
        The function uses a broad exception handler around the object-dtype membership test; any exception raised there is caught and results in a False return value. The function does not raise exceptions itself.

## State Changes:
    Attributes READ:
        None (the function is not a method on an object that it reads; it only reads the provided `series` argument).
    Attributes WRITTEN:
        None. The function does not mutate the Series, the state dict, or any external object.

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series instance. Passing other types may cause pandas to raise; such exceptions are not propagated for the object-dtype path.
        - `state` can be any dict-like object; the function does not require any keys.
    Postconditions:
        - The Series and the `state` object remain unchanged after the call.
        - The boolean return value correctly reflects the predicate described above.

## Edge cases and notes:
    - NaN / missing values: In the object-dtype branch, NaN values are not equal to True or False, so their presence will cause the membership test .all() to be False (and thus the function will not classify the Series as boolean).
    - Empty Series: pandas' behavior for .all() on an empty boolean Series returns True; therefore, an empty object-dtype Series that produces an empty membership result may evaluate to True in that branch (consistent with pandas semantics). Callers should be aware of how empty Series are intended to be classified in their pipeline.
    - Exceptions during membership testing (e.g., due to unhashable or unusual objects) are suppressed by design and lead to a False result rather than propagating an error.

## Side Effects:
    - No I/O, logging, or network activity.
    - No external mutations; the function only performs read operations on the Series.
    - Performance: the object-dtype branch executes a vectorized membership test across the Series (series.isin({True, False})), which requires scanning all elements and may be non-trivial for very large Series.

## Example usage (illustrative):
    Given a Series of values from a DataFrame column, the profiling dispatcher calls this predicate to decide whether the column is boolean. Example scenarios:
    - A Series with dtype bool => returns True.
    - An object-dtype Series containing only True and False literals => returns True.
    - An object-dtype Series containing "True"/"False" strings or mixed values => returns False.

## `src.ydata_profiling.model.typeset.URL` · *class*

## Summary:
Represents a Visions-based type predicate for URL-like textual data; provides a relation pointing to Text and a predicate that returns True when every non-null element in a pandas Series parses as a URL with both a non-empty scheme and non-empty network location.

## Description:
This class is a Visions type used by the ydata_profiling/type-inference pipeline to identify Series that should be considered URLs. It exposes:
- get_relations(): declares that URL is identical to the Text type for relation-based inference.
- contains_op(series, state): a static predicate used by the inference engine to test whether a column's values look like URLs.

Typical instantiation and callers:
- Instantiated implicitly or explicitly when building a Visions typeset or when registering available types for inference: e.g., URL().
- The inference engine or profiling code calls URL.contains_op(series, state) (or uses multimethod dispatch) when classifying a pandas Series.
- The method is intentionally a small, testable unit that only performs the URL-detection predicate; higher-level code orchestrates state, ordering, and fallbacks.

Why this abstraction exists:
- Encapsulates URL-detection logic so the type-inference system can reuse it across datasets without duplicating parsing logic.
- Separates relation metadata (get_relations) from the predicate implementation (contains_op).

## State:
This class defines no instance attributes in the provided source and inherits any behavior from visions.VisionsBaseType. The predicate and relations are static and do not depend on instance state.

Attributes (visible to callers):
- None (no public instance attributes declared).

__init__ parameters:
- None defined in this class; default construction uses the base class constructor (no arguments required).

Shared state interaction:
- contains_op accepts a `state` dict used by the inference pipeline. The method itself does not read or write state keys directly, but the applied decorator (series_handle_nulls) will set state["hasnans"] if absent and may short-circuit based on that flag (see Lifecycle / Raises / Edge cases).

Class invariants:
- There are no per-instance invariants to maintain because the class is stateless in the provided source.
- Inference-contract invariant: get_relations always returns a sequence with a single IdentityRelation(Text).

## Lifecycle:
Creation:
- Instantiate with the default constructor: url_type = URL()
  (The class does not require initialization arguments; many inference systems call its static methods without creating an instance.)

Usage:
- get_relations():
    - Call URL.get_relations() when the typeset/registry needs to discover relations for this type.
    - Returns Sequence[TypeRelation] containing exactly IdentityRelation(Text).
- contains_op(series, state):
    - Signature (as intended by callers): (series: pandas.Series, state: dict) -> bool
    - Decorators applied (affecting invocation):
        1. @multimethod: enables multimethod dispatch (allows the same function name to have multiple overloads).
        2. @series_handle_nulls: pre-processes the passed series and populates state["hasnans"] if missing. Behavior of this decorator (important):
            - If state does not contain "hasnans", decorator sets state["hasnans"] = series.hasnans.
            - If state["hasnans"] is True, the decorator replaces series with series.dropna().
            - If series.dropna() produces an empty Series (i.e., all original values were null), the decorator returns False immediately and the inner contains_op is not invoked.
            - If state["hasnans"] is False (including the case of an originally empty series without NaNs), the decorator forwards the original series to contains_op.
    - Predicate logic (executed after decorator processing):
        - Lazily parse each element with urllib.parse.urlparse.
        - Return True only if every parsed element has both a truthy .scheme and .netloc attribute.
        - The implementation uses a generator expression and Python's all(...) so evaluation short-circuits on first failing element.
    - Typical invocation order:
        1. Registry/inference calls URL.contains_op(series, state).
        2. series_handle_nulls sets/uses state["hasnans"] and possibly returns False early for all-NaN columns.
        3. If forwarded, contains_op parses elements with urlparse and returns the all(...) result or False on AttributeError.

Destruction / cleanup:
- No cleanup or resource management is required; no files or network resources are opened. Instances have no explicit close() or context-manager behavior.

## Method Map:
graph LR
    A[Callers: Inference engine / Typeset registry] --> B[URL.get_relations()]
    A --> C[URL.contains_op(series, state)]
    C --> D[Decorator: series_handle_nulls]
    D --> E{state.get("hasnans") present?}
    E -->|No: set state["hasnans"]=series.hasnans| F{state["hasnans"]?}
    E -->|Yes| F
    F -->|True| G[series = series.dropna(); if series.empty -> return False (decorator)]
    F -->|False| H[pass series through unchanged]
    H --> I[Inner contains_op: for x in series -> urlparse(x)]
    I --> J{for all parsed x: x.scheme and x.netloc are truthy?}
    J -->|Yes| K[Return True]
    J -->|No| L[Return False]
    I --> M[AttributeError during parse/access] --> N[Return False]

## Raises:
- __init__: No explicit exceptions are raised by the class constructor in the provided source.
- get_relations(): No exceptions raised by the implementation as written.
- contains_op:
    - Catches AttributeError internally and returns False when an AttributeError occurs while iterating, parsing, or inspecting parsed objects.
    - The series_handle_nulls decorator may raise AttributeError if the provided `series` lacks expected pandas attributes (e.g., hasnans or dropna). That exception will propagate unless the caller provides a proper pandas.Series.
    - Any other exceptions raised while iterating over the series elements or by urllib.parse.urlparse (e.g., unexpected object behavior) are not caught here and will propagate to the caller.

## Edge cases and concrete behaviors:
- Columns containing only null/NaN values:
    - If state does not yet have "hasnans", the decorator sets it to True and then series.dropna() yields an empty Series. The decorator returns False (the inner predicate is not called).
    - Thus an all-null column yields False.
- Empty columns with no NaNs (e.g., an empty Series where series.hasnans is False):
    - The decorator will forward the empty series to contains_op. The predicate uses all(...) on an empty generator, which returns True — therefore empty-but-no-NaN series yields True.
- Mixed-type elements:
    - If urlparse(x) or accessing x.netloc / x.scheme raises AttributeError for some element (e.g., unexpected object lacking string-like behavior), contains_op catches AttributeError and returns False.
    - Other exceptions from element processing will propagate.
- Short-circuiting:
    - The implementation uses a generator + all(...); evaluation stops at the first element that does not satisfy both scheme and netloc.
- State mutation:
    - The decorator may insert state["hasnans"]. contains_op itself does not modify the state dict.

## Example:
1) Typical successful identification:
    from pandas import Series
    s = Series(["https://example.com/path", "http://host.local/"])
    state = {}
    result = URL.contains_op(s, state)  # Returns True
    # After call, state contains "hasnans": False

2) Column with some invalid URL-like values:
    s2 = Series(["https://good.example", "not-a-url", None])
    state2 = {}
    result2 = URL.contains_op(s2, state2)
    # series_handle_nulls sets state2["hasnans"] True -> dropna() removes None
    # contains_op sees "not-a-url" -> urlparse yields missing netloc/scheme -> returns False

3) All-NaN column:
    s3 = Series([None, None])
    state3 = {}
    result3 = URL.contains_op(s3, state3)
    # series_handle_nulls sets state3["hasnans"] True -> series.dropna() empty -> decorator returns False
    # result3 is False; inner predicate is not invoked.

4) Empty Series with no NaNs:
    s4 = Series([], dtype="object")
    state4 = {}
    result4 = URL.contains_op(s4, state4)
    # series.hasnans is False; decorator forwards empty series
    # all(...) on empty generator returns True -> result4 is True

Notes:
- Because contains_op is decorated with @multimethod, callers within a multimethod dispatch system may not call the staticmethod directly but instead rely on the dispatcher. Direct calls to URL.contains_op(series, state) are valid for testing and are shown above.
- The URL type relies on urllib.parse.urlparse to decide URL-ness; it does not perform network IO nor validate reachability.

### `src.ydata_profiling.model.typeset.URL.get_relations` · *method*

## Summary:
Returns the set of type-relations for this type: a single identity relation pointing to Text, indicating this type is considered identical to the Text type for inference purposes.

## Description:
This method provides the TypeRelation objects that declare how this type relates to other types in the visions-based type inference system. Concretely, it returns a sequence containing one IdentityRelation referencing Text.

Known callers and context:
- No direct callers are present in this file. Conceptually, this is intended to be called by the typeset/type-registration phase or the type inference engine when assembling relations for all types (e.g., when Visions or a higher-level typeset enumerates each type's relations).
- Typical lifecycle stage: invoked during initialization/registration of type relations or during inference to determine whether values of this type should be treated as Text.

Why this logic is a separate method:
- Keeps the relations for the type encapsulated and discoverable by the type system.
- Allows the type framework to query relations uniformly across different type classes without inlining relations into registration code.
- Makes it straightforward to override or extend relations in subclasses or custom types.

## Args:
This method takes no arguments.

## Returns:
Sequence[TypeRelation]
- Contents: a list/sequence containing a single IdentityRelation(Text).
- Meaning: declares that the current type is identical to the Text type for inference/relationship purposes.
- Edge cases: never returns None or an empty list; it always returns a sequence with the IdentityRelation(Text) element as shown in the implementation.

## Raises:
This method raises no exceptions.

## State Changes:
Attributes READ:
- None (the implementation does not access self or other attributes).

Attributes WRITTEN:
- None (the implementation does not modify object or module state).

## Constraints:
Preconditions:
- No preconditions: can be called at any time since it does not access external state or parameters.

Postconditions:
- Returns a sequence whose sole element is IdentityRelation(Text).
- Does not alter the object or global state.

## Side Effects:
- None. No I/O, no external service calls, no mutation of objects outside the returned sequence.

### `src.ydata_profiling.model.typeset.URL.contains_op` · *method*

## Summary:
Determines whether every element in the given pandas Series parses as a URL with both a non-empty scheme and a non-empty network location; does not modify the series or the provided state.

## Description:
Iterates over the series and applies urllib.parse.urlparse to each element, checking that the resulting parse object has both .scheme and .netloc truthy. Evaluation short-circuits on the first element that fails the check. This predicate is intended for use in type-inference or profiling pipelines that need to decide whether a column should be classified as containing URLs; keeping it as a separate function makes the URL-detection logic reusable and unit-testable.

Known callers and lifecycle/context:
- Used by type-inference or data-profiling components that evaluate predicate functions against series values (for example, when constructing TypeRelation predicates or when classifying a Series' data type). The function itself performs only the boolean test and returns the result to the caller, which integrates it into the broader inference workflow.

Why this is its own method:
- Encapsulates a single, testable predicate that may be reused by different parts of the inference pipeline.
- Keeps higher-level pipeline code focused on orchestration rather than low-level parsing checks.

## Args:
    series (pd.Series): The pandas Series to examine. The function iterates over its elements and passes each element to urllib.parse.urlparse.
    state (dict): A dict provided for API compatibility with predicate-callers; this function does not read or modify it.

## Returns:
    bool:
        - True if, for every element produced by iterating over the series, urlparse(element) yields a parsed object whose .scheme and .netloc are both truthy.
        - False if any parsed element has a falsy .scheme or .netloc.
        - False if an AttributeError is raised while attempting to parse or inspect elements (the function catches AttributeError and returns False).
        - For an empty series (no elements), returns True due to Python's all(...) behavior on empty iterables.

## Raises:
    - The function catches AttributeError and returns False in that case.
    - Any other exceptions raised during iteration or parsing (not caught by this function) will propagate to the caller.

## State Changes:
    Attributes READ:
        - None on a surrounding object; the function reads only the provided series elements.
    Attributes WRITTEN:
        - None. The function does not mutate the series, the state dict, or other external state.

## Constraints:
    Preconditions:
        - 'series' must be iterable (the function iterates over it).
        - Elements should be suitable inputs for urllib.parse.urlparse for meaningful results (typically string-like).
    Postconditions:
        - The series and the state dict remain unchanged.
        - The returned boolean reflects the per-element parse checks described above (subject to the AttributeError catch behavior).

## Side Effects:
    - None: no I/O, no network or filesystem access, and no external mutations.

## Implementation details:
    - Uses a generator expression to lazily parse elements; evaluation stops at the first failing element.
    - Relies on urllib.parse.urlparse producing objects with .scheme and .netloc attributes.
    - Because only AttributeError is caught and handled (by returning False), callers that require strict exception-safety should handle other potential exceptions themselves.

## `src.ydata_profiling.model.typeset.Path` · *class*

## Summary:
Represents a Visions type that identifies pandas Series containing filesystem paths (absolute paths). Provides type relations and a predicate to detect when a Series holds absolute filesystem paths.

## Description:
Path is a small Visions type-class used by the ydata_profiling type-inference pipeline to detect columns whose values are filesystem paths (specifically, absolute paths). It should be instantiated and used by the Visions/type-inference machinery; typical callers include the Visions engine or the ydata_profiling type-detection steps that enumerate candidate types for a pandas Series.

Motivation and responsibility boundary:
- Responsibility: supply a boolean predicate (contains_op) that returns True when every non-null element of a Series represents an absolute filesystem path according to os.path.isabs, and to announce that Path is identity-related to the Text type.
- Boundary: Path only verifies "absolute path-ness" across a Series — it does not validate file existence, determine whether entries are directories vs files, or interpret URLs. It relies on os.path.isabs semantics and any upstream pre-processing of nulls.

Known callers/factories:
- The Visions inference process (VisionsBaseType-based registry) that calls get_relations() and the multimethod-based contains_op when evaluating a Series for membership in this type.
- The ydata_profiling pipeline that queries Vision types during dataset profiling.

## State:
This class defines no instance-level attributes of its own. It inherits whatever behavior and attributes VisionsBaseType provides. The methods consume and/or mutate an external "state" dict that follows the convention used by the series_handle_nulls decorator.

For the "state" dict used by contains_op (via the series_handle_nulls decorator):
- Key: "hasnans"
  - Type: bool
  - Meaning: whether the original Series contained missing values (NaNs).
  - Behavior/invariant: If "hasnans" is not present when contains_op is invoked, the series_handle_nulls decorator sets state["hasnans"] = series.hasnans. If state["hasnans"] is True, the decorator will call series.dropna() and may short-circuit (return False) if the resulting series is empty.

Class invariants:
- The Path type declares an IdentityRelation to Text (see get_relations). This invariant expresses that values identified as Path are also considered Text by the type system.
- contains_op should always be callable with a pandas.Series and a dict-like state object. If the supplied series is not a pandas-like Series (missing hasna/dropna), decorator behavior may raise an exception (see Raises).

## Lifecycle:
Creation:
- Instantiate with no arguments: Path() (inherits VisionsBaseType constructor/signature). No Path-specific constructor arguments are required.

Usage:
1. The Visions/type-inference engine will call Path.get_relations() to learn that Path implies Text (IdentityRelation(Text)).
2. To test whether a pandas.Series s is of type Path:
   - Prepare a state dict (may be empty) and call Path.contains_op(s, state).
   - contains_op is decorated:
       - multimethod: participates in multiple-dispatch registration (used by the Visions framework).
       - series_handle_nulls: ensures missing values handling:
           * If "hasnans" is absent in state, state["hasnans"] is set to s.hasnans.
           * If state["hasnans"] is True, the decorator replaces s with s.dropna(), and if the result is empty the decorator returns False immediately.
3. contains_op then checks, element-wise, whether os.path.isabs(value) is True for every element in the (possibly dropna'd) Series. If every element is an absolute path (os.path.isabs returns True), contains_op returns True; otherwise False.

Method call ordering:
- get_relations() may be called anytime to query type relations.
- contains_op(...) must be invoked with the Series and a state dict in the profiling/type-inference pipeline. The series_handle_nulls decorator executes before the main predicate.

Destruction:
- No cleanup is required. There are no open resources or context-manager behaviors associated with Path.

## Method Map:
flowchart TD
    A[Caller/Visions engine] --> B[get_relations()] 
    A --> C[contains_op(series, state)]
    C --> D[series_handle_nulls decorator]
    D --> E[maybe set state["hasnans"]]
    E --> F{state["hasnans"] == True?}
    F -- Yes --> G[series = series.dropna()]
    G --> H{series.empty?}
    H -- Yes --> I[return False (short-circuit)]
    H -- No --> J[call contains_op body]
    F -- No --> J
    J --> K[all(os.path.isabs(p) for p in series) ?]
    K -- True --> L[return True]
    K -- False --> M[return False]

## Detailed behavior of methods

get_relations() -> Sequence[TypeRelation]
- Returns: a sequence whose single element is IdentityRelation(Text).
- Purpose: declare that Path is identity-related to Text (i.e., values classified as Path should be considered Text as well).
- No side effects.

contains_op(series: pandas.Series, state: dict) -> bool
- Input:
    - series: a pandas.Series (or pandas-compatible object) containing the column values to test. The function expects that the Series supports:
        * .hasnans attribute (boolean-like)
        * .dropna() method returning a Series
        * iteration yielding element values for element-wise checking
    - state: dict-like (mutable) object used by the series_handle_nulls decorator to record the presence of NaNs; the decorator may add or read state["hasnans"].
- Behavior:
    1. The series_handle_nulls decorator first ensures missing values are handled:
        - If "hasnans" not in state, set state["hasnans"] = series.hasnans.
        - If state["hasnans"] is True:
            * Replace series with series.dropna().
            * If series.dropna() is empty, contains_op returns False without executing its body.
    2. The method attempts to evaluate whether every remaining element in series is an absolute filesystem path:
        - It uses all(os.path.isabs(p) for p in series).
        - If all elements satisfy os.path.isabs, returns True; otherwise False.
    3. The method catches TypeError from the generator/evaluation and returns False in that case (safe failure on type errors during path-checking).
- Edge cases and constraints:
    - Empty series after dropna -> returns False (handled by decorator).
    - If series contains values that cause os.path.isabs to raise TypeError (e.g., incompatible types), contains_op catches TypeError and returns False.
    - The decorator will NOT drop NaNs if state["hasnans"] is already present and False — in that case, even if the series has NaNs, the original series will be passed through. This is a caller-visible contract: callers may pre-populate state["hasnans"] to short-circuit the decorator's check, but doing so incorrectly (for example setting False while the series actually contains NaNs) can lead to unexpected behavior.
    - The predicate uses os.path.isabs semantics:
        * It checks for absolute paths according to the running OS semantics (e.g., leading '/' on POSIX, drive-letter on Windows).
        * It does not check that the path exists or points to a file vs directory.
        * Empty strings and purely relative paths cause os.path.isabs to return False.
    - The function relies on series iteration returning the raw stored values; if the Series contains path-like objects implementing os.PathLike, os.path.isabs will accept them.

## Raises:
- AttributeError: may be raised by the series_handle_nulls decorator when accessing series.hasnans if the provided series argument is not pandas-like (e.g., None or an arbitrary iterable lacking hasnans). This occurs before the contains_op body gets control.
- Any exception raised by os.path.isabs or other unexpected runtime exceptions (other than TypeError) will propagate; however, TypeError raised during the all(...) evaluation is caught and transformed into a False return value by contains_op.
- No exceptions are raised intentionally by get_relations().

## Example:
- Typical usage within the type-inference pipeline (pseudocode):
    state = {}
    series = df["possible_path_column"]  # pandas.Series
    path_type = Path()
    # Query relations
    relations = path_type.get_relations()  # [IdentityRelation(Text)]
    # Test membership: contains_op is decorated to drop NaNs if needed
    is_path = Path.contains_op(series, state)
    # Interpret result:
    #   True  -> every non-null element is an absolute path
    #   False -> otherwise (including empty series after dropna, any non-absolute or incompatible element)
Notes:
- Because contains_op is a static method decorated with multimethod in the original class, the method is registered for Visions' multimethod dispatch. In direct usage, calling Path.contains_op(series, state) is equivalent to invoking the predicate implemented here.
- When reimplementing this class, ensure the series_handle_nulls decorator behavior (set/check state["hasnans"], dropna short-circuit) and TypeError -> False mapping are preserved to match the original semantics.

### `src.ydata_profiling.model.typeset.Path.get_relations` · *method*

## Summary:
Returns the static type relation declarations for the Path type: a sequence containing a single IdentityRelation pointing to the Text type. This does not modify the object state.

## Description:
- Context / callers:
    - There are no direct call sites for this method inside the repository snapshot. It is intended to be queried by the Visions type system (or by ydata_profiling code that integrates with Visions) during type registration and inference to discover how the Path type relates to other types.
- Purpose:
    - Encapsulates the type-relations metadata for Path so the Visions-based inference engine can build type-relation graphs without instantiating Path objects or inlining relation declarations in other code paths.
    - Keeping this as a dedicated method follows the Visions convention (each type exposes its relations) and keeps relation metadata localized to the type implementation for maintainability and testability.

## Args:
    None

## Returns:
    Sequence[TypeRelation]:
        - A sequence (concrete implementation: list) with exactly one element:
            - IdentityRelation(Text)
        - Semantics: declares that Path has an identity relation to Text (i.e., Path is related to Text according to Visions' relation semantics).
        - Edge cases: the returned sequence is always non-empty and always contains exactly one TypeRelation instance in the current implementation.

## Raises:
    None. The method constructs and returns a list literal; it does not perform I/O or operations that raise exceptions.

## State Changes:
- Attributes READ:
    - None (does not access self or any instance attributes).
- Attributes WRITTEN:
    - None (no mutation of self or external objects).

## Constraints:
- Preconditions:
    - None required. The method is a static function and does not depend on object state or arguments.
- Postconditions:
    - The caller receives a Sequence[TypeRelation] whose single element is an IdentityRelation constructed with the Text type.

## Side Effects:
    - None. The method performs no I/O, no logging, and does not mutate any objects outside the returned list.

### `src.ydata_profiling.model.typeset.Path.contains_op` · *method*

## Summary:
Determine whether every element in the provided pandas Series is an absolute filesystem path; returns a boolean and does not modify the inputs.

## Description:
This function evaluates a pandas Series of values and returns True only if every element in the Series is recognized as an absolute filesystem path by os.path.isabs. It is intended to be used as a predicate during type-detection or validation steps for Path-like columns (for example, as the 'contains' check for a Path type in a typeset). It is separated into its own function because the check is a single-purpose predicate relying on os.path behavior and error handling (TypeError -> False), making it reusable and easy to register or call from a higher-level type inference pipeline.

Known callers and typical context:
- Called by type-detection or profiling code when determining whether a pandas Series should be classified as containing filesystem paths (i.e., as part of a Path-type detection routine).
- Invoked during column-level profiling or type inference stages where candidate type-check functions are applied to a Series to decide its most appropriate type.

## Args:
    series (pd.Series):
        A pandas Series (or Series-like iterable) whose elements are expected to be path-like values (typically str or objects implementing os.PathLike).
        - Allowed values: any iterable of values. For meaningful results, elements should be strings, bytes, or os.PathLike objects.
        - Special cases: an empty Series is allowed (see Returns).

    state (dict):
        An arbitrary mapping provided by the caller (often a shared state passed through type checks). This function does not read from or modify this dict; it is accepted to match the common predicate signature used by the type-inference framework.

## Returns:
    bool:
        - True if and only if the series is iterable and every element yields True for os.path.isabs (i.e., every element is an absolute path).
        - True for an empty Series (because all(...) over an empty iterable returns True).
        - False if any element is not an absolute path or if a TypeError is raised while applying os.path.isabs to any element (e.g., non-path-like elements such as None or numeric types).
        - No other special return values.

## Raises:
    This function catches TypeError raised by os.path.isabs and returns False in that case. Other exceptions (if any) that occur during iteration or from os.path.isabs (for example, unexpected exceptions) are not explicitly caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - None on a containing object (the implementation does not access self attributes).
        - Does not read the provided state dict.

    Attributes WRITTEN:
        - None. The function does not mutate the Series or the provided state dict.

## Constraints:
    Preconditions:
        - The `series` argument must be an iterable (pandas Series is expected).
        - For meaningful (True) results, all elements of `series` should be strings/bytes/os.PathLike representing filesystem paths.
    Postconditions:
        - The input `series` and `state` are unchanged after the call.
        - The function returns a boolean summarizing whether every element is recognized as an absolute path.

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - No mutations occur to objects outside the function; it is purely observational.

## `src.ydata_profiling.model.typeset.File` · *class*

## Summary:
Represents a Visions type that recognizes pandas Series containing filesystem paths to existing files; used to detect columns whose values are file paths that exist on the local filesystem.

## Description:
This class is a Visions type intended for use in the type-inference step of data profiling. It implements:
- get_relations(): declares an identity relation to the Path type (meaning a File is a Path with the additional constraint that the referenced path exists on disk).
- contains_op(series, state): a predicate used by the Visions inference engine to determine whether a pandas Series qualifies as File-typed data.

Typical scenarios:
- Invoked during automatic dataset profiling to mark a column as containing file paths that actually exist on the profiler's host filesystem.
- Used by a Visions-based TypeSystem or a profiling pipeline that iterates candidate types and calls contains_op to accept/reject a type for a column.

Motivation / Responsibility boundary:
- File encapsulates the single responsibility of detecting whether a Series contains paths that exist on the local filesystem. It reuses the Path type (which checks for absolute path form) via an identity relation, and refines that by performing existence checks.
- It does not attempt to validate remote URLs, check readability/permissions, inspect file contents, or classify file formats; it only tests existence.

## State:
This is a class with no instance attributes. The dynamic state used by its predicate is passed via the `state` argument to contains_op:

- state (dict) — mutable mapping passed into contains_op by the type-inference engine. Interactions:
    - 'hasnans' (bool): May be set by the series_handle_nulls decorator. If present and True, the decorator will drop NaNs from the series before contains_op runs. The decorator will set this key if it was not already present.
    - No other keys are written by the File.contains_op implementation.

Notes on __init__ parameters:
- There is no explicit __init__; the class is a Visions type definition (subclass of visions.VisionsBaseType) and typically instantiated or referenced by the Visions type system. Callers usually do not instantiate File directly; they either refer to the class or rely on the Visions registry.

Class invariants:
- contains_op must only be called with a pandas.Series as the first argument and a dict as the second; the series_handle_nulls decorator assumes the Series exposes .hasnans and .dropna().

## Lifecycle:
Creation:
- No required constructor parameters. Typical usage is referencing the class object (File) within a Visions type registry or creating an instance via the Visions framework if needed.

Usage:
1. The profiling/type-inference engine may call File.get_relations() to obtain declared relations (returns [IdentityRelation(Path)]).
2. When evaluating whether a column is of type File, the engine calls File.contains_op(series, state).
   - The contains_op is decorated with series_handle_nulls: if state['hasnans'] is not set, the decorator sets it based on series.hasnans. If NaNs are present, the decorator passes series.dropna() into contains_op; if that produces an empty series, the decorator returns False immediately.
   - contains_op returns True only if os.path.exists(p) is True for every element p in the (possibly NaN-dropped) series.
3. No cleanup or destruction is required; there are no open resources to close.

Sequencing constraints:
- contains_op expects the decorator pre-processing; calling contains_op without the decorator would change behavior (i.e., it would not drop NaNs automatically). The decorated function as exposed to callers is the correct entry point.

Destruction:
- None required. No file handles are opened by this class.

## Method Map:
flowchart LR
    A[get_relations()] --> B[returns IdentityRelation(Path)]
    C[contains_op(series, state)] --> D[series_handle_nulls decorator]
    D --> E[series (NaNs dropped if any)]
    E --> F[for each element p in series: os.path.exists(p)]
    F --> G[all(...) result -> contains_op returns bool]

Notes:
- get_relations is independent; contains_op relies on the series_handle_nulls preprocessor then performs per-element os.path.exists checks.

## Raises:
The class itself does not raise exceptions at import time. contains_op (the decorated predicate) may raise exceptions under the following conditions:

- TypeError:
    - If elements of the Series are of types that os.path.exists cannot handle (for example, some non-string/unicode, non-pathlike objects), os.path.exists may raise TypeError which will propagate.
    - If the caller passes a non-pandas object lacking .hasnans or .dropna() (the decorator will access series.hasnans), an AttributeError may occur before contains_op runs; treat that as a caller error (wrong argument type).
- Any exception raised by os.path.exists will propagate to the caller.
- The series_handle_nulls decorator may set state['hasnans'] and return False early when the input series becomes empty after dropna(); that is not an exception but important control flow.

Behavioral guarantees:
- If the series (after NaN-dropping by the decorator) is empty, contains_op will not be invoked; the decorator returns False.
- If contains_op returns True, then every non-NaN element in the original series (or every element if no NaNs) existed on the local filesystem according to os.path.exists.

## Example:
- Detecting whether a DataFrame column contains existing file paths (illustrative):

    1) Prepare a pandas Series:
    series contains strings like: ['/mnt/data/report.csv', '/mnt/data/image.png', ...]

    2) Call the predicate (typical invocation by a Visions-based type system):
    state = {}
    is_file_type = File.contains_op(series, state)

    Behavior:
    - If series.hasnans is True, the decorator will drop NaNs first. If all values were NaN (dropna -> empty), the result will be False.
    - Otherwise, the function returns True iff os.path.exists(p) is True for every element p in the (NaN-free) series.

- Example edge-case:
    * If the column contains URL strings (e.g., "http://..."), os.path.exists will return False (or may raise depending on input type); remote resources are not resolved by this type.
    * If column elements are integers or objects that are not path-like, os.path.exists may raise TypeError; callers should ensure the Series contains string-like path values before relying on File.contains_op.

### `src.ydata_profiling.model.typeset.File.get_relations` · *method*

## Summary:
Returns the set of type relations that connect this type to other Visions types; specifically, it declares that this File type has an identity relation to the Path type.

## Description:
- Role and context: This static method is used by the Visions-based type system (and by ydata_profiling when assembling its typeset) during type registration and inference. The Visions engine calls get_relations() for each VisionsBaseType subclass to collect TypeRelation objects that describe how types relate to one another for conversion and inference purposes.
- Known callers: The Visions type-inference/registration routines and any codepaths in ydata_profiling that iterate over available types to build the typeset or compute possible conversions. In practice, this is invoked at typeset construction or when Visions evaluates relations during inference.
- Rationale for being a separate method: Visions expects each type to declare its relations via a dedicated static method. Keeping relation declarations in a small, isolated method makes them discoverable by the Visions framework, avoids inlining relation logic throughout the codebase, and keeps the type-class definition declarative and easy to extend.

## Args:
None.

## Returns:
Sequence[TypeRelation]
- Concrete return value: a list containing a single IdentityRelation targeting the Path type (i.e., [IdentityRelation(Path)]).
- Meaning: The IdentityRelation indicates that File and Path should be considered equivalent/identical for purposes of type relations (identity conversion). This lets the Visions engine treat values of type File as if they are Path where appropriate.
- Edge cases: Always returns a fresh list on each call. There are no conditional branches; the return value is deterministic.

## Raises:
None. The method performs no operations that may raise exceptions (it simply constructs and returns a relation object).

## State Changes:
- Attributes READ: None (method is a staticmethod; it does not access instance or class attributes).
- Attributes WRITTEN: None.

## Constraints:
- Preconditions: None. Can be called at any time without requiring prior initialization or object state.
- Postconditions:
  - The caller receives a Sequence[TypeRelation] whose sole element is IdentityRelation(Path).
  - No mutation of module-level or object-level state occurs.

## Side Effects:
None. The method performs no I/O, no network activity, and does not mutate objects outside its local return value.

### `src.ydata_profiling.model.typeset.File.contains_op` · *method*

## Summary:
Return True when every element in the provided pandas Series refers to an existing filesystem path; does not modify object state.

## Description:
This predicate is used by the profiling / typeset type-detection machinery to decide whether a column should be classified as a File type: it tests whether each value in the Series corresponds to an existing file or directory on the local filesystem. Typical callers are the type-inference dispatcher that iterates over candidate Visions types during dataset profiling; the method is invoked in the type-detection stage of the profiling pipeline.

This check is implemented as a dedicated method because it encapsulates a single, well-defined predicate (existence of paths) that is:
- Reused by the typeset dispatcher.
- Potentially expensive (per-element filesystem checks), so keeping it separate makes it easier to reason about performance and to apply decorators that handle nulls or empty-series semantics.

Note: In the class definition this method is wrapped by a decorator that handles null/missing values for the Series (series_handle_nulls). That wrapper is responsible for dealing with None/NA entries before this core predicate executes; the core implementation assumes it receives a Series appropriate for element-wise path checks.

Known callers and context:
- The typeset/type-inference dispatcher within the profiling pipeline when evaluating whether a DataFrame column should be classified as a File type.
- Any other component that needs a boolean predicate for "all entries refer to existing filesystem paths" during profiling or validation.

## Args:
    series (pd.Series):
        A pandas Series containing candidate filesystem paths. Elements should be path-like (str, bytes, or os.PathLike). The implementation iterates the Series and passes each element to os.path.exists.
    state (dict):
        Context dictionary passed by the profiling pipeline. This implementation does not read from or modify this dict; it is accepted for API compatibility with other contains_op implementations.

## Returns:
    bool:
        - True when os.path.exists(p) is True for every element p in the Series (i.e., every element refers to an existing file or directory).
        - False otherwise (if at least one element does not exist).
        Edge cases:
            - Empty Series: Python's all(...) over an empty iterator yields True (vacuous truth). Unless the surrounding pipeline or decorators filter out empty Series, an empty Series will make this predicate return True.
            - Series with non-path-like elements: if os.path.exists returns False for such values, the result will be False; if os.path.exists raises (see Raises), the exception will propagate.

## Raises:
    TypeError:
        - If one or more elements in the Series are of a type that os.path.exists (and underlying os.stat) cannot accept (for example, certain non-path-like objects), a TypeError raised by the os path routines may propagate.
    Any exception raised by iterating the Series:
        - If the provided `series` is not iterable like a pandas Series (missing expected methods), iteration may raise TypeError or AttributeError which will propagate.
    Notes:
        - The method itself does not catch exceptions; callers or decorators (e.g., series_handle_nulls) must handle problematic values if desired.

## State Changes:
    Attributes READ:
        - None on `self` (this is a static/pure predicate with respect to object attributes).
        - Reads the provided `series` argument (iterates its values).
    Attributes WRITTEN:
        - None. The method does not mutate `self`, `series`, or `state`.

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series or an iterable of path-like objects (str, bytes, os.PathLike).
        - The class-level decorator that wraps this method is expected to have handled null/missing values; if nulls remain they may cause os.path.exists to raise TypeError.
    Postconditions:
        - The method returns a boolean indicating whether every element in `series` exists on the filesystem.
        - No mutation of inputs or external state is performed by this method.

## Side Effects:
    - Filesystem reads: the method performs a per-element existence check via os.path.exists, which typically invokes system stat calls. This is I/O-bound, may be slow for large Series, and may be affected by filesystem permissions, mount points, or networked filesystems.
    - No writes or external network calls are performed by the method itself.
    - No caching is performed: each call re-checks every element in the Series.

## `src.ydata_profiling.model.typeset.Image` · *class*

## Summary:
A Visions type predicate that classifies a pandas Series as containing image file paths by checking that every (non-missing) element is recognized as an image file by the Python imghdr module.

## Description:
Image is a Visions type (subclass of visions.VisionsBaseType) intended for use during automated dataset profiling / type inference. It provides two pieces of information used by the inference engine:

- get_relations(): declares an identity relation to the File type, indicating Image is a refinement of File (Image implies File).
- contains_op(series, state): a boolean predicate that returns True when every element of the provided pandas.Series (after NaN removal by the series_handle_nulls decorator) is recognized as an image by imghdr.what.

When to instantiate / typical callers:
- The class is typically not manually instantiated by application code. Instead it is referenced by the Visions type system or profiling pipeline which queries get_relations() and calls contains_op(...) on candidate Series.
- Known caller pattern: a type-inference loop that iterates candidate Visions types and invokes static contains_op(series, state) to decide whether a Series should be assigned this type.

Motivation and responsibility boundary:
- Purpose: provide a small, focused predicate that recognizes Series of local filesystem image files (e.g., PNG, JPEG) by probing file headers using imghdr.
- Responsibility boundary: it only checks whether the elements correspond to image files according to imghdr.what. It does not:
  - Validate the File semantics beyond image recognition (this is delegated to the File relation).
  - Fetch or validate remote URLs.
  - Open or keep file handles open beyond what imghdr.what does transiently.
  - Provide content-type inference beyond imghdr's capabilities.

## State:
This class contains no instance attributes. All dynamic inputs are provided to contains_op as parameters.

- contains_op parameters:
    - series (pandas.Series): Series of values expected to be file path-like objects (commonly strings). The series may contain missing values; the series_handle_nulls decorator will handle NaNs before the predicate runs.
    - state (dict): Mutable mapping supplied by the type-inference engine. Known interactions:
        - 'hasnans' (bool): If absent the series_handle_nulls decorator sets this key to series.hasnans. If True, the decorator will pass a NaN-dropped Series into contains_op (or return False early if dropping NaNs yields an empty Series).

Type / valid values / invariants:
- series: must behave like a pandas.Series and expose .hasnans and .dropna() methods. After the decorator runs, the series passed to the inner predicate is guaranteed to have no missing values (unless the decorator short-circuits due to emptiness).
- Elements of series: expected to be strings or path-like objects referencing local files. imghdr.what will treat string values as filenames and attempt to open them. If imghdr.what returns a non-None string for an element, that element is considered an image.

Class invariants:
- contains_op should only be invoked through the decorated callable (i.e., with the series_handle_nulls wrapper applied). The wrapper ensures 'hasnans' is set in state and that series passed to the inner logic has no NaNs.
- If contains_op returns True, then imghdr.what(p) evaluated on each element p in the (NaN-free) series returned a truthy value (a non-None string).

## Lifecycle:
Creation:
- No constructor parameters. Usage is typically by referencing the class object in a Visions registry; explicit instantiation is unnecessary.

Usage pattern (typical invocation order):
1. The type-inference engine calls Image.get_relations() to retrieve declared relations (returns [IdentityRelation(File)]).
2. The engine invokes Image.contains_op(series, state) (the decorated callable). The decorator:
   - Ensures state['hasnans'] is set (from series.hasnans if absent).
   - If state['hasnans'] is True, it passes series.dropna() to the inner predicate; if dropna() yields an empty Series, the wrapper returns False immediately and the inner predicate is not called.
3. The inner predicate evaluates imghdr.what(p) for each element p in the (NaN-free) series and returns True iff all elements produced a non-None result.
4. No cleanup is required; no persistent resources are held.

Destruction:
- None required. The class introduces no long-lived resources or side effects.

Sequencing constraints:
- Always call the decorated contains_op exposed by the class (the decorator must run first). Bypassing the decorator may change behavior with NaNs and state['hasnans'].

## Method Map:
flowchart LR
    A[get_relations()] --> B[returns IdentityRelation(File)]
    C[contains_op(series, state)] --> D[series_handle_nulls decorator wraps contains_op]
    D --> E[if state['hasnans'] True -> series = series.dropna(); if series.empty -> return False]
    E --> F[for each element p in series -> imghdr.what(p)]
    F --> G[all(...) -> bool result returned by contains_op]

Notes:
- The multimethod decorator is present to support potential overloads; the implementation provides a single signature (series, state).

## Raises:
contains_op (the decorated predicate) does not intentionally raise new exceptions, but the following errors may propagate to the caller:

- AttributeError:
    - If the provided series has no .hasnans or .dropna() attributes (i.e., a non-pandas object), the series_handle_nulls wrapper will raise AttributeError when accessing these attributes.
- TypeError / ValueError / OSError (propagated):
    - If an element p is of a type that imghdr.what or the underlying open() call cannot handle (for example, certain custom objects), imghdr.what may raise TypeError or an I/O-related exception. Such exceptions are not caught by the predicate and will propagate.
- No exception for missing files:
    - If a filename string refers to a non-existent file, imghdr.what typically returns None rather than raising; this results in contains_op returning False rather than raising.
- Behavior note:
    - Passing remote URLs (e.g., "http://...") will not cause a network fetch; imghdr.what will treat the string as a filename and return None (or may raise if the string contains illegal characters for open()).

## Example:
- Typical "image path" detection scenario (described as steps):
    1) Prepare a pandas Series whose elements are local filesystem paths to image files, e.g., ['/data/a.jpg', '/data/b.png', '/data/c.gif'].
    2) Create an empty state dict: state = {}.
    3) Call the type predicate exposed by the class: call Image.contains_op(series, state) (the decorated callable).
       - If the series contains NaNs, the decorator will drop them before the inner predicate runs; if dropping NaNs yields an empty series the call returns False.
       - If all non-missing elements are recognized by imghdr.what as image files (imghdr.what returns a non-None string for each), the method returns True; otherwise False.
    4) Use the boolean result to decide whether the Series should be typed as Image (and, via the declared relation, as File).

- Edge-case examples to consider:
    * Series contains URL strings: the predicate will not fetch remote content; imghdr.what will treat them as file paths and return None, so contains_op returns False.
    * Series contains non-string objects: imghdr.what may raise TypeError; callers should ensure elements are path-like strings or handle exceptions from contains_op.
    * Series references non-existent local files: imghdr.what will usually return None; contains_op returns False (no exception).

### `src.ydata_profiling.model.typeset.Image.get_relations` · *method*

## Summary:
Declares that the Image Visions type has an identity relation to the File Visions type; returns a short immutable-like description of that relation for the type-inference engine.

## Description:
This static method is part of the Image Visions type definition and is used by the Visions-based type-inference system (and the profiling pipeline that wraps it) to discover declared relations between types during inference. Typical callers include the Visions type system or a profiling/type-inference routine that queries each candidate type for its relations while building the type hierarchy or deciding compatible/coercible types for a pandas.Series.

This logic is a separate, static method because the Visions framework expects types to expose their relations via a callable API (so callers can inspect relations without instantiating the type). Keeping relation declarations in a dedicated method keeps the type metadata isolated and easily discoverable by the inference engine.

## Args:
    None

## Returns:
    Sequence[TypeRelation]:
        - A sequence (concrete implementation: a list) containing a single IdentityRelation referencing the File type.
        - Concrete returned value in the implementation: [IdentityRelation(File)]
        - Interpretation: the returned relation object declares an identity relationship between Image and File for the Visions type system.
        - Edge cases:
            * The function always returns a new list instance containing the IdentityRelation; callers who mutate the returned list will not affect future calls to get_relations (each call constructs and returns a fresh list).
            * If the symbol File is not defined in the module's runtime environment, calling this method will raise a NameError when trying to construct the IdentityRelation (this reflects a programming/module-resolution error, not an intended behavior).

## Raises:
    - NameError: If the File identifier is missing at runtime (i.e., the File class is not available in the module namespace when get_relations is invoked).
    - No other exceptions are raised by this method itself (it performs no IO and constructs a simple object).

## State Changes:
    Attributes READ:
        - None (the method does not read any instance or class attributes).
    Attributes WRITTEN:
        - None (the method is pure with respect to object/module state; it does not modify self or any module-level variables).

## Constraints:
    Preconditions:
        - None required by the logic of the method beyond the module-level availability of the File class and visions.relations.IdentityRelation (both are present in the module as used).
        - Callers may assume the method is a static, parameterless query (no arguments).
    Postconditions:
        - The method returns a sequence containing exactly one TypeRelation instance: an IdentityRelation constructed with File as its target.
        - No state on the Image class or elsewhere is modified by calling this method.

## Side Effects:
    - None observable: the method performs no I/O, network calls, or mutations outside the returned list and the newly constructed IdentityRelation object.
    - The only potential runtime side effect is raising a NameError if File is unavailable in the module namespace at call time.

## Implementation notes for re-creation:
    - Implement as a parameterless staticmethod or classmethod that returns a Sequence[TypeRelation].
    - Return a new list holding IdentityRelation(File) so callers receive a sequence they can inspect without requiring Image instantiation.
    - Keep the method minimal and deterministic: no branching, no external calls, and no dependence on instance state.

### `src.ydata_profiling.model.typeset.Image.contains_op` · *method*

## Summary:
Return True when every element in the provided pandas Series yields a truthy result from imghdr.what, indicating each entry is recognized as an image type. The call does not mutate object state.

## Description:
This predicate is used by the typeset/type-detection machinery during dataset profiling to decide whether a column should be classified as an Image type. Typical callers are the profiling/type-inference dispatcher that iterates over candidate Visions types and invokes each type's contains_op for a given column. In the class definition this predicate is wrapped by decorators (e.g., series_handle_nulls and multimethod) which handle nulls and dispatch; the core logic here focuses solely on validating entries via imghdr.what.

This logic is implemented as a separate method because:
- It encapsulates per-element header/format inspection using a dedicated library function (imghdr.what).
- It is a focused, reusable predicate that the profiling pipeline can call consistently and test independently.
- It allows external decorators to uniformly manage nulls and empty-series semantics around this small, deterministic predicate.

## Args:
    series (pd.Series):
        A pandas Series whose elements will be passed, one-by-one, to imghdr.what. Typical elements are filenames (strings) that reference candidate image files.
    state (dict):
        Context dictionary used by the profiling pipeline. This implementation does not read or modify state; it exists for API consistency with other contains_op implementations.

## Returns:
    bool:
        - True if imghdr.what(p) evaluates to a truthy value for every element p in the Series.
        - False if at least one element yields a falsy value (e.g., imghdr.what returns None for an unrecognized header).
        Edge cases:
            - Empty Series: all(...) over an empty generator returns True (vacuous truth). If decorators or the pipeline do not filter empty Series, this method will return True for an empty Series.

## Raises:
    - Any exception raised by imghdr.what when invoked on an element, or any exception raised while iterating `series`, will propagate to the caller. The implementation does not catch exceptions. Callers or surrounding decorators should handle problematic values if required.

## State Changes:
    Attributes READ:
        - None on the containing object (`self`). The method reads only the provided `series` argument by iterating its elements.
    Attributes WRITTEN:
        - None. The method does not modify `series`, `state`, or external state.

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series (or iterable) whose elements are suitable inputs for imghdr.what (commonly filename strings).
        - The class-level decorator series_handle_nulls (present in the class) is expected to handle missing/null entries before this predicate runs; otherwise, passing None/NA values may cause imghdr.what or iteration to raise.
    Postconditions:
        - Returns a boolean indicating whether every element was recognized as an image by imghdr.what.
        - No mutation of inputs or external state occurs as a result of the call.

## Side Effects:
    - Potential filesystem I/O: when given filename inputs, imghdr.what may open and read files to inspect headers, which incurs I/O for each element.
    - No network access, no persistent writes, and no caching are performed by this method itself.
    - Each invocation independently inspects the provided elements; repeated calls re-run the checks.

## `src.ydata_profiling.model.typeset.TimeSeries` · *class*

## Summary:
Represents a Visions type that recognizes numeric pandas Series exhibiting time dependence (significant autocorrelation at configured lags). Used by the Visions inference pipeline to identify series that should be treated as time series.

## Description:
This class is a Visions type (subclass of visions.VisionsBaseType) whose purpose is to detect numeric sequences with temporal dependency. It exposes:
- get_relations: declares that TimeSeries is an identity relation of the Numeric type.
- contains_op: core detector: returns True when the provided series is numeric (excluding boolean) and shows autocorrelation above a configured threshold at any configured lag.

When to instantiate:
- No per-instance state is required; the class is typically used by the Visions type-inference/registration system or by a profiling pipeline that builds a list of detected types. Callers usually do not instantiate TimeSeries directly; instead Visions or a type registry will treat this class as a type descriptor.

Motivation and responsibility:
- Encapsulates the logic for deciding whether a pandas Series should be considered a time series based on numeric type and autocorrelation.
- Keeps the numeric/time-dependence detection logic isolated so that profiling code can query types consistently.

## State:
This class has no instance-level stored attributes (the detection logic is implemented in static methods). Relevant external state and invariants are:

- External configuration accessed:
    - config.vars.timeseries.autocorrelation: float threshold in [0.0, 1.0] used to decide whether autocorrelation at a particular lag is strong enough.
    - config.vars.timeseries.lags: Sequence[int] of lags (positive integers) to test autocorrelation against.

- Expected types and invariants:
    - The contains_op method expects:
        - series: pd.Series — a pandas Series object. Decorators applied ensure the series is non-empty and that nulls are handled according to the project’s null-handling decorator (see Lifecycle/Preconditions).
        - state: dict — a dictionary passed by the Visions/registry pipeline (unused by the implementation but required by the multimethod signature).

    - Class invariants:
        - No instance state to maintain.
        - Behavior depends on globally accessible configuration values: the autocorrelation threshold must be a numeric value and lags must be an iterable of non-negative integers for meaningful results.

## Lifecycle:
Creation:
- No constructor arguments are required. The class is a static descriptor and can be referenced directly as TimeSeries (or by the Visions registry) without instantiation.

Usage:
1. Precondition decorators:
    - series_not_empty: ensures the provided series contains at least one non-null value (so contains_op is only invoked for non-empty series).
    - series_handle_nulls: (applied as a decorator) is expected to handle or filter nulls in the series before autocorrelation checks. As a consumer of this class, ensure the pipeline provides the decorated series or that those decorators are available in the environment that registers this type.

2. Typical call sequence:
    - Visions (or a registry) calls TimeSeries.contains_op(series, state)
    - contains_op:
        a. Determines if the series is numeric and not boolean using pandas dtype checks.
        b. If numeric, checks time dependence by computing autocorrelation at each lag from config.vars.timeseries.lags.
        c. If any autocorrelation value >= config.vars.timeseries.autocorrelation, returns True. Otherwise returns False.

3. Concurrency and side effects:
    - contains_op is pure with respect to the provided series (it reads values and calls pandas.Series.autocorr). It does not mutate global state or the series.
    - It temporarily suppresses RuntimeWarning when computing autocorrelations.

Destruction:
- No cleanup or close calls are required. The class has no resources to free.

## Method Map:
flowchart LR
    A[get_relations()] --> B[IdentityRelation(Numeric)]
    C[contains_op(series, state)] --> D[is_numeric_check]
    D --> E[is_timedependent(series)]
    E --> F[for lag in config.vars.timeseries.lags]
    F --> G[series.autocorr(lag)]
    G --> H[compare >= config.vars.timeseries.autocorrelation]
    H --> I[return True if any comparison True]
    I --> J[otherwise return False]

Notes:
- get_relations() simply returns a relation object indicating this type relates to Numeric.
- contains_op uses is_numeric_check then is_timedependent helper logic to perform autocorrelation checks.

## Raises:
The class methods themselves do not explicitly raise application-specific exceptions. Potential runtime errors and their triggers:

- AttributeError / NameError:
    - If the global "config" object or its expected attributes (vars.timeseries.autocorrelation or vars.timeseries.lags) are missing or misnamed, a runtime AttributeError/NameError will be raised.
    - If pandas.Series.autocorr is unavailable for the given series object, AttributeError may be raised.

- TypeError / ValueError:
    - If config.vars.timeseries.lags is not iterable of integers, the iteration or autocorr call may raise TypeError or ValueError.
    - If autocorr returns non-comparable types, the comparison >= may raise TypeError.

- pandas-related warnings/NaN handling:
    - pandas.Series.autocorr may return NaN when there are insufficient non-null observations for a given lag. Comparisons with NaN behave as False (NaN >= threshold is False), so autocorr NaN values will not cause a True detection.

Decorators applied to contains_op (series_not_empty and series_handle_nulls) reduce the chance of some of these errors by ensuring non-empty input and by normalizing or filtering nulls; however, their exact behavior depends on the decorator implementations.

## Example:
Assume the profiling/Visions environment provides config.vars.timeseries.autocorrelation = 0.5 and config.vars.timeseries.lags = [1, 2, 3].

- Detecting a time-dependent numeric series:
    - Input: a pandas Series of numeric values with temporal autocorrelation at lag 1 >= 0.5.
    - Call: TimeSeries.contains_op(series, state={})
    - Behavior: contains_op verifies numeric dtype (not boolean), computes autocorr at lags 1, 2, 3; seeing autocorr >= 0.5 at lag 1 returns True.

- Example pseudo-usage (narrative):
    - The Visions inference loop iterates known types and calls each type's contains_op on a column series. If TimeSeries.contains_op(...) returns True, the pipeline will label the column as a TimeSeries (in addition to its Numeric relation from get_relations).

Implementation notes to reimplement this class:
- Subclass visions.VisionsBaseType.
- Implement static get_relations returning [IdentityRelation(Numeric)].
- Implement contains_op decorated with multimethod, series_not_empty, and series_handle_nulls, signature (series: pd.Series, state: dict) -> bool.
- In contains_op:
    - Implement helper is_timedependent(series) that:
        * Reads autocorrelation_threshold and lags from config.vars.timeseries.
        * Suppresses RuntimeWarning when calling pandas.Series.autocorr.
        * Iterates over lags and returns True if any series.autocorr(lag=lag) >= autocorrelation_threshold.
        * Returns False if none meet threshold.
    - Determine numeric-ness via pandas dtype checks: pdt.is_numeric_dtype(series) and not pdt.is_bool_dtype(series).
    - Return True only when both numeric-ness and is_timedependent(series) are True.

### `src.ydata_profiling.model.typeset.TimeSeries.get_relations` · *method*

## Summary:
Returns the type relations for the TimeSeries Visions type — specifically a sequence containing an IdentityRelation to the Numeric type. This does not modify object state.

## Description:
Known callers and lifecycle stage:
- Called by the Visions-based type-inference and profiling machinery when building the type-relation graph or when querying what relations a type supports.
- Typical call locations:
  - During registration of types with the inference engine.
  - When the inference engine enumerates possible conversions/relations for a column type.
- This method is executed at the stage where the system constructs the set of TypeRelation objects that define how this type relates to others (e.g., identity, inference paths).

Why this logic is a separate method:
- The Visions framework requires each type to expose its relations via a canonical method so the inference engine can discover and traverse relations programmatically. Encapsulating relation declarations in get_relations keeps relation metadata colocated with the type and avoids inlining relation construction where the engine consumes them.

## Args:
- None.
- Note: This is a static method; call as TimeSeries.get_relations() (no self/cls argument).

## Returns:
- Type: Sequence[TypeRelation] (concrete implementation: a list)
- Normal return value: a sequence containing exactly one element: IdentityRelation(Numeric)
  - Semantics: the returned IdentityRelation indicates TimeSeries is considered identical/compatible with the Numeric Visions type for the purposes of type relation traversal.
- Edge cases:
  - The function always returns a fresh list object on each call (so callers may mutate the returned list without affecting future calls).
  - Any Sequence implementation that contains the same IdentityRelation(Numeric) would be equivalent in intent.

## Raises:
- NameError:
  - Condition: If the name Numeric is not bound in the module namespace at call time, constructing or evaluating the IdentityRelation argument may raise NameError.
  - Practical note: In normal module initialization this is not an issue when Numeric is defined in the same module and module-level names are available; however, calling this function before the Numeric symbol is defined will trigger this error.
- No other exceptions are raised by this function itself (it constructs and returns objects only). Exceptions raised while using the returned relations (e.g., if a relation's predicate references other missing names) are outside this method's direct behavior.

## State Changes:
- Attributes READ: none (does not read any self or module-level mutable state beyond the Numeric name binding).
- Attributes WRITTEN: none (no mutation of object/module state).

## Constraints:
- Preconditions:
  - No runtime preconditions on input parameters (there are none).
  - The module-level symbol Numeric should be defined/bound prior to calling to avoid NameError.
- Postconditions:
  - After the call, the caller receives a Sequence[TypeRelation] whose sole element is IdentityRelation(Numeric).
  - The module or class state remains unchanged.

## Side Effects:
- None: the method performs no I/O, no logging, and mutates no external objects.
- The only observable effect is creation and return of new Python objects (the list and the IdentityRelation instance).

Implementation notes for re-implementation:
- Implement as a parameterless static method that returns a new list containing IdentityRelation(Numeric).
- Ensure Numeric is imported or defined in the same module or otherwise available in the call scope.
- Do not attempt to perform inference or evaluation here — only declare relations. The inference engine will consume these relation objects later.

### `src.ydata_profiling.model.typeset.TimeSeries.contains_op` · *method*

## Summary:
Return True when a numeric pandas Series exhibits time-dependence (autocorrelation at or above a configured threshold for at least one configured lag). The call is a pure predicate and does not modify object state.

## Description:
Known callers and context:
- Invoked by the typeset/type-inference dispatcher in the profiling pipeline during the column type-detection/inference stage. The dispatcher tests each candidate Visions type by calling its contains_op for a DataFrame column; this predicate helps decide whether a column should be classified as a TimeSeries type.
- In the class definition this function is normally wrapped by decorators (e.g., multimethod, series_not_empty, series_handle_nulls) that provide multimethod dispatch, empty-series guards, and null handling before this core predicate executes.

Why this logic is its own method:
- Encapsulates the domain-specific rule that a TimeSeries must be numeric and show sufficient autocorrelation across one or more lags.
- Keeps the autocorrelation logic isolated and testable (thresholds and lag set are read from configuration).
- Allows consistent reuse by the profiling dispatcher and separation of concerns: decorator-managed null/emptiness behavior is kept separate from the numeric + autocorrelation predicate.

## Args:
    series (pd.Series):
        A pandas Series representing a column to test. Expected to support pandas dtype inspection and Series.autocorr. Typical input is a numeric Series (the function checks this).
    state (dict):
        A context dictionary supplied by the profiling pipeline. This implementation does not read from or modify `state` — it is present for API compatibility with other contains_op implementations.

## Returns:
    bool:
        - True when both of the following hold:
            * The Series has a numeric dtype and is not a native boolean dtype.
            * For at least one lag in the configured lag list, series.autocorr(lag=lag) is greater than or equal to the configured autocorrelation threshold.
        - False otherwise.
        Edge cases:
            - If the configured lags iterable is empty, the time-dependence check yields False (no lag produced autocorrelation >= threshold).
            - If series.autocorr returns NaN for a lag (for example, due to insufficient non-missing data), that lag is treated as not meeting the threshold (NaN comparisons are False), and other lags are evaluated.
            - An empty Series or an all-NA Series typically leads to False here; the class-level decorators are expected to handle emptiness/null semantics before this predicate is invoked.

## Raises:
    - No explicit exceptions are raised by this implementation.
    - Exceptions raised by pandas operations (e.g., if `series` is not a pandas.Series or lacks the expected attributes) will propagate (AttributeError, TypeError, etc.).
    - If the module-level configuration object (accessed as config.vars.timeseries.autocorrelation and config.vars.timeseries.lags) is not present or does not expose these attributes, a NameError or AttributeError may occur; callers should ensure configuration is available.

## State Changes:
    Attributes READ:
        - None on an enclosing object (this is a static/pure predicate). It reads only the provided `series` argument and global configuration.
    Attributes WRITTEN:
        - None. The function does not mutate `series`, `state`, or any external object.

## Constraints:
    Preconditions:
        - `series` should be a pandas.Series (or Series-like) where dtype inspection (pandas.api.types.is_numeric_dtype and is_bool_dtype) and Series.autocorr are meaningful.
        - A configuration object must be accessible with:
            * config.vars.timeseries.autocorrelation: numeric threshold used in comparisons (typical autocorrelation values lie in [-1, 1]).
            * config.vars.timeseries.lags: an iterable of integer lags to evaluate (e.g., [1,2,3]).
        - In normal usage the method is executed after decorators that ensure the Series is non-empty and that nulls are handled; without those decorators callers may need to handle emptiness/nulls themselves.
    Postconditions:
        - Returns a boolean that indicates whether the Series is numeric (non-boolean dtype) and shows autocorrelation >= configured threshold for at least one configured lag.
        - No inputs, state dict, or external state are mutated by this call.

## Side Effects:
    - Uses warnings.catch_warnings to suppress runtime warnings raised by pandas during autocorrelation computation; this suppression is local to the function.
    - Performs in-memory numeric computations (autocorrelation) which can have non-trivial CPU cost for very long Series, but performs no I/O or network access.
    - No persistent side effects (no writes, no external service calls).

## `src.ydata_profiling.model.typeset.ProfilingTypeSet` · *class*

## Summary:
Represents a profiling-specific Visions typeset configured by runtime Settings and an optional explicit mapping from dataset column names to Visions type names. It centralizes the Visions types available to the profiler and resolves string type names to actual Visions type classes.

## Description:
ProfilingTypeSet is a thin subclass of visions.VisionsTypeset used by the profiling system to:
- Construct the set of Visions types (type classes) that the profiler will consider for inference and casting, using configuration.
- Store an optional per-column type schema where each value is a string type name that gets resolved to the corresponding Visions type class.

Typical scenarios:
- Instantiate once per profiling run (or per configuration) to provide a consistent typeset to the rest of the profiler.
- Created by higher-level profiler factory code with a Settings instance; callers pass an optional type_schema dict to force certain columns to given types.

Motivation and responsibility boundary:
- The class isolates the profiler's type selection and name-resolution logic from the rest of the codebase. It does not implement type inference rules itself; it relies on Visions types and a helper function (typeset_types) to produce the concrete types list based on Settings.

## State:
- config (Settings)
  - Type: ydata_profiling.config.Settings
  - Description: The profiler configuration. Required in constructor.
  - Constraints: Must be a valid Settings instance used by typeset_types to derive the concrete Visions types list.

- types (Sequence[visions.VisionsBaseType])
  - Type: Sequence of Visions type classes (subclasses of visions.VisionsBaseType)
  - Description: The typeset passed to the VisionsTypeset base class. Populated during initialization by calling typeset_types(config) and then calling the parent constructor.
  - Invariant: Each element is a Visions type class (i.e., a subclass or instance appropriate for VisionsTypeset). The VisionsTypeset base is expected to expose this list as self.types after super().__init__(...).

- type_schema (dict[str, visions.VisionsBaseType])
  - Type: Mapping from dataset column name (string) to resolved Visions type class
  - Description: Stores the resolved types for columns provided by the caller. Internally created by _init_type_schema which maps provided string type names to concrete Visions types using _get_type.
  - Default: {} if constructor argument type_schema is None.
  - Invariant: For every key/value pair, the value is a Visions type class that exists in self.types.

Notes on external dependency:
- typeset_types(config) is an external helper (not part of this class). Contract required by this class:
  - Accepts a Settings instance.
  - Returns an iterable/sequence of Visions type classes acceptable by visions.VisionsTypeset.
  - If typeset_types returns an incorrect structure, VisionsTypeset initialization may fail.

## Lifecycle:
Creation:
- Call signature:
    ProfilingTypeSet(config: Settings, type_schema: dict | None = None)
- Required arguments:
    - config: Settings instance (no default)
- Optional:
    - type_schema: dict mapping column names (str) to string type names (str). If omitted or None, an empty schema is used.
- Behavior during creation:
    1. Store config on self.config.
    2. Call typeset_types(config) to obtain the desired Visions types list.
    3. Initialize the parent visions.VisionsTypeset with the returned types. Warnings of category UserWarning are temporarily suppressed during the parent initialization.
    4. Resolve the optional type_schema mapping (if any) by converting each string type name to the corresponding Visions type class via _get_type, and store the resolved mapping on self.type_schema.

Usage:
- After instantiation, callers can read:
    - instance.types to enumerate available Visions types.
    - instance.type_schema to retrieve per-column enforced type classes.
- Typical sequence:
    1. Instantiate ProfilingTypeSet.
    2. Query or pass the instance to components that perform inference, relation checks, or casting using the provided Visions typeset.
    - No particular method-call ordering is required beyond initialization.

Destruction / Cleanup:
- No special cleanup is required. The class does not open external resources, hold file handles, or implement context manager semantics.

## Method Map:
- _init_type_schema(type_schema: dict) -> dict
  - Purpose: Resolve a mapping of column_name -> type_name (str) into column_name -> VisionsTypeClass.

- _get_type(type_name: str) -> visions.VisionsBaseType
  - Purpose: Find a Visions type class in self.types whose class name matches type_name (case-insensitive). Raises ValueError if not found.

Mermaid diagram (method call dependencies and typical invocation order):

flowchart TD
    Init[__init__(config, type_schema)]
    TypesetTypes[typeset_types(config)]
    SuppressWS[Suppress UserWarning]
    SuperInit[super().__init__(types)]
    InitSchema[_init_type_schema(type_schema)]
    GetType[_get_type(type_name)]
    Init --> TypesetTypes
    Init --> SuppressWS --> SuperInit
    Init --> InitSchema
    InitSchema --> GetType

## Raises:
- __init__ indirectly raises:
  - ValueError: If the provided type_schema contains a type name that cannot be resolved to any type in the produced types list. This occurs when _get_type fails to find a case-insensitive match and raises ValueError("Type [name] not found.").

- _get_type explicitly raises:
  - ValueError: When no type in self.types has a __name__ that case-insensitively equals the provided type_name.

Notes:
- Because parent initialization is wrapped in a warnings.catch_warnings context that filters UserWarning, warnings of this category will not surface during initialization. Other exceptions raised by VisionsTypeset (e.g., due to incorrect typeset structure) will propagate normally.

## Example:
- Basic usage:
    1. Prepare a Settings instance (example assumed to be provided by the profiling application).
    2. Optionally prepare a type schema mapping column names to type names (strings), e.g. {"age": "Numeric", "signup_date": "DateTime"}.
    3. Instantiate:
        profiler_typeset = ProfilingTypeSet(config=my_settings, type_schema={"age": "Numeric"})
    4. Inspect available types and resolved schema:
        available = profiler_typeset.types
        enforced = profiler_typeset.type_schema
    5. If type_schema contained an unknown type name, construction raises ValueError and should be handled by the caller.

Implementation hints for re-creation:
- Ensure visions is available and that the returned sequence from typeset_types contains types compatible with visions.VisionsTypeset.
- When resolving names, use case-insensitive comparison against t.__name__ for each t in self.types.
- Suppress UserWarning around the call to the VisionsTypeset initializer to mirror original behavior.

### `src.ydata_profiling.model.typeset.ProfilingTypeSet.__init__` · *method*

## Summary:
Initialize the ProfilingTypeSet instance by storing the provided Settings, constructing the Visions types list from configuration, initializing the VisionsTypeset parent with that list (suppressing UserWarning), and resolving an optional per-column type schema into concrete Visions type classes stored on the instance.

## Description:
Known callers and context:
- Called when creating a profiling typeset for a profiling run or pipeline stage that needs a consistent set of Visions types and an optional per-column enforced schema.
- Typical callers: profiler factory code or profiling run setup code that supplies a Settings instance and optionally a user-provided type schema mapping.
- Lifecycle stage: invoked during object construction (initialization) prior to any type inference, casting, or relation checks that depend on this typeset.

Why this logic is a dedicated constructor (and why work is delegated):
- Object initialization must perform multiple coordinated actions (store configuration, derive the list of Visions types, call the parent initializer, and normalize a user type schema). Keeping this logic in __init__ centralizes those responsibilities and delegates specialized parts (type-list construction and schema normalization) to helper functions (typeset_types and _init_type_schema) so each piece is testable and reusable.

## Args:
    config (Settings): Required. The profiler configuration used to derive the concrete Visions types list via typeset_types(config). Must be a valid Settings instance understood by typeset_types.
    type_schema (dict | None): Optional. Mapping from column identifiers (commonly str column names) to textual type names (str). If None, treated as an empty mapping. Keys must be hashable (strings are typical). Values are expected to be strings naming a Visions type class (case-insensitive match against the classes produced by typeset_types). Default: None.

## Returns:
    None

## Raises:
    ValueError:
        - Raised if the provided type_schema contains a type name that cannot be resolved to any type in the constructed types list. This comes from the helper _get_type invoked by _init_type_schema and has the message pattern "Type [<type_name>] not found."
    AttributeError:
        - May be raised if type_schema does not implement .items() (i.e., is not mapping-like) or if a value in type_schema lacks string-like behavior (for example, missing .lower()) during resolution.
    Any exception raised by visions.VisionsTypeset.__init__ or by typeset_types(config):
        - If typeset_types returns an invalid structure or the parent initializer detects invalid types, exceptions from those calls (such as TypeError or ValueError) will propagate. Note: UserWarning produced by the parent initializer is suppressed; other exception types are not.

## State Changes:
    Attributes READ:
        - self.types (read indirectly by _init_type_schema/_get_type during type name resolution after the parent initializer has set it)
    Attributes WRITTEN:
        - self.config: set to the provided Settings instance.
        - self.types: initialized by visions.VisionsTypeset.__init__ when called via super().__init__(types). (This happens during this constructor's execution.)
        - self.type_schema: set to the dict returned by self._init_type_schema(type_schema or {}), i.e., a mapping from keys to concrete Visions type class objects.

## Constraints:
    Preconditions:
        - config must be a valid Settings instance acceptable to typeset_types.
        - If provided, type_schema must be a mapping-like object (implement .items()) whose values are strings (or at least behave like strings, implementing .lower()) representing Visions type class names.
    Postconditions:
        - self.config references the provided Settings object.
        - self.types is populated by the parent VisionsTypeset using the sequence returned by typeset_types(config).
        - self.type_schema is a dict mapping the original keys to resolved Visions type class objects; if no type_schema was provided, it is an empty dict.

## Side Effects:
    - Suppresses warnings of category UserWarning only during the call to the VisionsTypeset parent initializer; other warnings and exceptions are unaffected.
    - May raise exceptions described above which propagate to the caller; no other I/O or external service calls are performed.
    - No mutation of input type_schema is performed; a new dict (from _init_type_schema) is assigned to self.type_schema.

### `src.ydata_profiling.model.typeset.ProfilingTypeSet._init_type_schema` · *method*

## Summary:
Converts a mapping of names to textual type identifiers into a mapping of the same names to Visions type classes, updating nothing on the object but returning the normalized schema.

## Description:
This helper is called during ProfilingTypeSet initialization to normalize a user-provided or configuration-provided type schema into the internal representation the typeset expects. Known callers:
- ProfilingTypeSet.__init__: invoked as part of object construction to set self.type_schema from the optionally provided type_schema argument.

Why this is a separate method:
- Centralizes the logic that converts textual type identifiers into Visions type classes so the conversion is consistent and testable in one place rather than duplicated inline in __init__ or other callers.

## Args:
    type_schema (dict): A mapping from arbitrary keys (typically column names or feature identifiers) to textual type names.
        - Key type: hashable objects (commonly str); keys are preserved in the returned dict.
        - Value type: str expected — the class name of a Visions type (case-insensitive). Example value: "Numeric" or "numeric".
        - Required: the argument must be a mapping-like object that supports .items().
        - Typical usage: the dict provided by user configuration that specifies a desired type for each column.

## Returns:
    dict: A new dictionary with the same keys as type_schema and with values replaced by the corresponding Visions type class objects (visions.VisionsBaseType subclasses) returned by self._get_type.
    - If type_schema is empty, returns an empty dict.
    - The returned dict preserves the same iteration order as the input mapping (dict insertion order for normal dicts).

## Raises:
    ValueError: If any provided textual type name is not found in this ProfilingTypeSet. This is raised by self._get_type with message "Type [<type_name>] not found."
    AttributeError: If a provided value in type_schema does not implement .lower() (e.g., a non-string value) and thus cannot be resolved by self._get_type, or if type_schema does not support .items() (i.e., it is not a mapping).
    Note: These exceptions are not caught by this method and propagate to the caller.

## State Changes:
    Attributes READ:
        - self._get_type (method) is called for each value in type_schema.
        - indirectly reads self.types (inside self._get_type) while resolving textual names to classes.
    Attributes WRITTEN:
        - None. This method does not modify self or any external object; it returns a new dict.

## Constraints:
    Preconditions:
        - type_schema must be a mapping-like object (supporting .items()).
        - Values in type_schema must be strings (or at least implement .lower()) corresponding to the __name__ of a Visions type present in this typeset.
    Postconditions:
        - On successful return, every input key is present in the returned dict and every corresponding value is a Visions type class object resolved by self._get_type.
        - If any value cannot be resolved, an exception is raised and no partial state is written to self.

## Side Effects:
    - No I/O, no logging, and no external service calls.
    - Possible side-effect-like behavior is raising exceptions that propagate to the caller (see Raises).
    - Does not mutate the input mapping; returns a new dict mapping keys to type classes.

### `src.ydata_profiling.model.typeset.ProfilingTypeSet._get_type` · *method*

## Summary:
Returns the Visions type object from this typeset whose class name matches the provided name (case-insensitive). If found, this does not modify object state; otherwise it raises an error.

## Description:
This helper resolves a textual type name to a VisionsBaseType class contained in the ProfilingTypeSet instance.
Typical callers are other type-resolution routines in the profiling pipeline that accept a type name (string) and need the corresponding Visions type class to apply relations or inferences. It is factored out so name-to-type resolution is centralized (single place to enforce case-insensitive matching and error handling) rather than duplicated inline wherever a string-to-type lookup is required.

## Args:
    type_name (str): The name of the type to look up. Matching is case-insensitive; e.g., "Numeric" and "numeric" are treated as equal.
        - Required: must be a string or an object implementing .lower() that returns a comparable string.
        - Typical values: the __name__ of types stored in self.types (for example, class names of Visions types).

## Returns:
    visions.VisionsBaseType: The class object from self.types whose __name__ matches type_name (case-insensitively). Returns the first matching element in iteration order.
    - Edge cases:
        - If multiple types in self.types share the same name ignoring case, the first encountered is returned.
        - If self.types is empty or contains no matching name, nothing is returned (a ValueError is raised instead).

## Raises:
    ValueError: If no type in self.types has a __name__ that matches type_name (case-insensitive). The exact message is "Type [<type_name>] not found."
    AttributeError: If the provided type_name does not provide a .lower() method (this is an implicit error coming from calling type_name.lower()).
    Note: The function signature types type_name as str; callers should pass strings to avoid the implicit AttributeError.

## State Changes:
    Attributes READ:
        - self.types: iterated to find a matching type by comparing each t.__name__.lower() to type_name.lower()
    Attributes WRITTEN:
        - None. This method does not modify self or external state.

## Constraints:
    Preconditions:
        - self.types must be an iterable of type/class objects where each element has a readable __name__ attribute (as is typical for Python classes).
        - type_name should be a string (or at least have a .lower() method that returns a string).
    Postconditions:
        - On success: returns a reference to an element t from self.types such that t.__name__.lower() == type_name.lower().
        - On failure: raises ValueError and leaves self unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutations to objects outside self.
    - Only possible side-effect-like behaviour is the implicit exception raised if type_name lacks .lower().

