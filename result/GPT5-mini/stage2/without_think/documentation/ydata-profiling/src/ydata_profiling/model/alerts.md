# `alerts.py`

## `src.ydata_profiling.model.alerts.fmt_percent` · *function*

## Summary:
Formats a numeric fraction (0..1 expected) into a one-decimal-place percentage string, with optional small/near-1 edge-case shorthand ("< 0.1%" or "> 99.9%") for values extremely close to 0 or 1.

## Description:
This helper converts a numeric fractional value into a human-readable percentage string suitable for inclusion in alerts or reports. It is purposely small and focused: responsibility is purely presentation (string formatting), not validation or normalization of the input.

Known callers in the provided context:
    - No direct call sites are present in the provided snippet. In practice this function is intended for use by alert/summary formatting code that needs to show percentages to users (for example, when reporting sample percentages, correlation p-values expressed as fractions, or other fraction-based metrics).

Why this is extracted into its own function:
    - Centralizes presentation logic for percentages (consistent rounding and special-casing tiny and near-1 values).
    - Keeps alert/report generation code concise and consistent across the codebase.
    - Encapsulates the particular string formatting (one decimal, minimum field width, special text for edge cases) so it can be updated in one place.

## Args:
    value (float):
        - The numeric fractional value to format. Typical expected range is 0.0 to 1.0 (representing 0% to 100%), but the function accepts any float-like numeric value.
        - The function does not coerce/string-parse inputs; callers should pass numeric types (float, int, numpy scalar).
    edge_cases (bool, default True):
        - If True, apply two special-cased textual outputs:
            * If value is positive but rounds to 0 at 3 decimal places, return "< 0.1%".
            * If value is less than 1 but rounds to 1 at 3 decimal places, return "> 99.9%".
        - If False, those two special cases are skipped and the numeric formatting is always used.

Interdependencies:
    - edge_cases only affects the two small/near-1 checks; it does not alter the numeric formatting when those checks do not trigger.

## Returns:
    str: A human-readable percentage string.

    Possible return shapes:
    - "< 0.1%": when edge_cases is True, round(value, 3) == 0, and value > 0 (tiny positive values).
    - "> 99.9%": when edge_cases is True, round(value, 3) == 1, and value < 1 (values extremely close to but less than 1).
    - "{X.Y}%": otherwise, the numeric value multiplied by 100, formatted with one decimal place using Python's format specifier 2.1f (for example, a value of 0.1234 -> "12.3%"; 1.234 -> "123.4%").

    Notes:
    - The numeric formatting uses one decimal place and a minimum field width of 2 (format specifier "2.1f").
    - For values outside 0..1, the function will still multiply by 100 and format (e.g., value=1.234 -> "123.4%").

## Raises:
    - The function itself does not explicitly raise custom exceptions.
    - Standard Python exceptions may arise if the input does not support the required numeric operations:
        * TypeError: if value cannot be compared to numbers or cannot be rounded/multiplied (e.g., passing a non-numeric object).
        * ValueError: unlikely from the function directly, but could occur if value originates from a conversion step performed by the caller.
    - There is no special handling of NaN/inf; behavior will follow Python's numeric semantics (formatting NaN likely yields "nan%" when using the f format).

## Constraints:
Preconditions:
    - Prefer passing numeric values (float, int, numpy/pandas numeric scalars).
    - To convey percentages in the expected human sense, pass values in fractional form (0.0 meaning 0%, 1.0 meaning 100%). The function will not validate this, so callers are responsible for normalization.

Postconditions:
    - The returned value is always a str.
    - If edge_cases True and the input meets one of the two edge conditions, the returned string is one of the two textual shorthands; otherwise it is a numeric percentage string with one decimal.

## Side Effects:
    - None. The function is pure: it performs no I/O, does not mutate external state, and does not call external services.

## Control Flow:
flowchart TD
    A[Start: receive value, edge_cases] --> B{edge_cases == True?}
    B -->|No| F[Compute numeric percent -> format "{value*100:2.1f}%" -> Return]
    B -->|Yes| C[round(value,3) == 0? and value > 0]
    C -->|Yes| D[Return "< 0.1%"]
    C -->|No| E[round(value,3) == 1? and value < 1]
    E -->|Yes| G[Return "> 99.9%"]
    E -->|No| F

## Examples:
- Typical usage:
    - fmt_percent(0.1234)
        - Returns: "12.3%"
    - fmt_percent(0.0004)
        - Returns: "< 0.1%" (tiny positive value; edge_cases default True)
    - fmt_percent(0.9997)
        - Returns: "> 99.9%" (very close to 1 but less than 1; edge_cases default True)
    - fmt_percent(1.0)
        - Returns: "100.0%"
    - fmt_percent(1.234)
        - Returns: "123.4%" (works for values > 1 if caller intentionally supplies them)

- Handling potential non-numeric input:
    - Example:
        try:
            s = fmt_percent(user_value)
        except TypeError:
            # Handle or log invalid input; the fmt_percent function expects numeric input.
            s = "n/a"

- Disabling edge-case shorthands:
    - fmt_percent(0.0004, edge_cases=False) -> "0.0%" (numeric formatting used instead of "< 0.1%")

## `src.ydata_profiling.model.alerts.AlertType` · *class*

## Summary:
An enumeration of alert categories used by the profiling system to classify issues discovered in a dataset (e.g., CONSTANT, MISSING, HIGH_CORRELATION). Each member represents a distinct, named alert type.

## Description:
AlertType is a lightweight Enum that lists all possible alert categories produced by the profiling engine. It should be referenced anywhere the code needs to label or check the category of an alert produced for a variable or dataset. Typical callers are components that build, emit, filter, or render alerts in the profiling pipeline (for example: alert constructors, report renderers, or threshold-checking utilities). This class exists to provide a single canonical set of labels so that alert producers and consumers use consistent names rather than ad-hoc strings.

Responsibility boundary:
- Provide canonical, typed labels for alert categories.
- Do not perform any logic or checks itself — it is a value object used by other components.

## State:
- Members (each is an AlertType enum member; the underlying value is an integer assigned by auto()):
    - CONSTANT: Represents variables with a single repeated value (no variation).
    - ZEROS: Represents variables that contain an excessive number or proportion of zero values.
    - HIGH_CORRELATION: Represents variables that are highly correlated with other variables.
    - HIGH_CARDINALITY: Represents variables with many distinct values relative to the sample size.
    - UNSUPPORTED: Represents variables with unsupported/unknown types for profiling operations.
    - DUPLICATES: Represents variables or rows that are duplicates.
    - SKEWED: Represents variables whose value distribution is strongly skewed.
    - IMBALANCE: Represents categorical variables with highly imbalanced class distributions.
    - MISSING: Represents variables that contain missing (NaN/None) values excessively.
    - INFINITE: Represents variables containing infinite values.
    - TYPE_DATE: Represents variables inferred as dates or date-like types.
    - UNIQUE: Represents variables where most or all values are unique (high uniqueness).
    - CONSTANT_LENGTH: Represents string variables where all entries share the same length.
    - REJECTED: Represents variables explicitly rejected from profiling (e.g., by configuration).
    - UNIFORM: Represents variables with nearly-uniform distributions (no meaningful variation).
    - NON_STATIONARY: Represents time-series variables whose distribution changes over time.
    - SEASONAL: Represents time-series variables that exhibit seasonality.
    - EMPTY: Represents variables or series that are empty (no observed data).
- Types:
    - Each member type: AlertType (Enum member)
    - Underlying .value: int (automatically assigned starting from 1 via auto()).
- Invariants:
    - Member names are stable and should not be renamed without coordinating across the codebase and persisted output (reports).
    - Members are immutable at runtime (Enum semantics).
    - The set of members is fixed at class definition time.

## Lifecycle:
- Creation:
    - Do not instantiate AlertType directly via constructor. Use existing members:
        - Access by attribute: AlertType.CONSTANT
        - Lookup by name: AlertType['CONSTANT'] (may raise KeyError for invalid names)
        - Lookup by value: AlertType(1) — if 1 corresponds to a member’s value; invalid values raise ValueError
- Usage:
    - Typical usage patterns:
        - Compare a produced alert's category: if alert.type is AlertType.MISSING: ...
        - Store the enum member on alert objects to maintain typed categories.
        - Serialize using .name for human-readable output, or .value for compact numeric encoding.
    - Method ordering / sequencing:
        - There is no required invocation sequence for AlertType itself. It is consulted and compared as needed by higher-level components.
- Destruction:
    - No cleanup required. Enum members are singletons and are managed by Python's runtime.

## Method Map:
A small dependency map showing typical interactions between a caller and AlertType:

graph TD
    A[Alert producer] -->|assign category| B[AlertType.CONSTANT]
    B -->|.name/.value| C[Serializer/Renderer]
    C -->|serialize| D[Report/Output]
    A -->|compare| E[Alert consumer]
    E -->|filter by| B

(Above diagram shows conceptual flows: an alert producer assigns an AlertType, serializer reads .name/.value, consumers compare against members.)

## Raises:
- KeyError:
    - Trigger condition: Attempting to access a member by invalid name using bracket syntax, e.g., AlertType['INVALID_NAME'].
- ValueError:
    - Trigger condition: Attempting to construct by value with an invalid scalar value, e.g., AlertType(999) when 999 does not match any member.value.
- No exceptions are raised by simple attribute access of defined members (e.g., AlertType.MISSING).

## Example:
1) Access a member and check an alert's category (illustrative plain-Python usage):
    alert_type = AlertType.MISSING
    if alert_type is AlertType.MISSING:
        # handle missing-value alert

2) Lookup by name (raises KeyError if the name is unknown):
    alert_type = AlertType['HIGH_CORRELATION']

3) Lookup by value (raises ValueError if the value is invalid):
    alert_type = AlertType(3)  # if 3 corresponds to a defined member

4) Serialization choices:
    - Human-readable label: alert_type.name  -> "MISSING"
    - Compact numeric label: alert_type.value ->  (int assigned by auto())

## `src.ydata_profiling.model.alerts.Alert` · *class*

## Summary:
Represents a single profiling alert for a dataset column or variable, encapsulating the alert category, related metadata (fields, values, column name), and small presentation helpers (formatted name and anchor id).

## Description:
The Alert class is instantiated by the profiling pipeline when a check identifies an issue or noteworthy condition for a column (for example: missing values, constant column, or high correlation). Typical callers are the rule/check implementations and alert aggregators in the profiling engine that detect conditions and create Alert objects to be collected, filtered, and rendered in reports.

This class exists to:
- Provide a typed container that pairs an AlertType (the canonical category) with structured metadata (values, related fields, column name).
- Offer small, presentation-oriented helpers used by renderers: a human-friendly alert_type_name, an anchor_id for linking within reports, a formatted label with contextual details for HIGH_CORRELATION, and a textual description for repr().

Responsibility boundary:
- It stores alert data and provides tiny convenience methods for display.
- It does not perform detection logic (checks) or I/O (rendering/serialization) — those are the responsibilities of other modules.

## State:
Instance attributes (created/initialized in __init__):
- alert_type (AlertType) — Required.
  - Description: The categorical enum member describing the alert category (e.g., AlertType.MISSING, AlertType.HIGH_CORRELATION).
  - Constraints: Should be a member of AlertType; the class does not enforce runtime type checks but callers must pass a valid AlertType.
- values (Dict) — Default: {} when None provided.
  - Description: Arbitrary mapping used to store alert-specific details. For HIGH_CORRELATION the code expects keys:
      - "fields": iterable of related field/column names (list or set of str)
      - "corr": numeric correlation value or textual representation
  - Constraints: The class treats values as a dict; if keys expected by fmt() are missing or of wrong type, methods may raise KeyError or TypeError.
- column_name (Optional[str]) — Default: None.
  - Description: The name of the column/variable the alert targets. May be None for dataset-level alerts.
  - Constraints: If a non-hashable object is supplied, anchor_id property may raise TypeError when hashing.
- fields (Set[str]) — Default: empty set when None provided.
  - Description: A set of related field names (used by some alerts to point to related columns).
  - Constraints: Converted via fields or set() in __init__; callers should pass an iterable of strings.
- _is_empty (bool) — Default: False.
  - Description: Internal boolean flag which can be used by creators to mark empty/placeholder alerts. The class stores it but does not otherwise act on it.
- _anchor_id (Optional[str]) — Default: class-level None, cached per-instance on first external access.
  - Description: Cached string identifier derived from hashing column_name. Computed lazily when the anchor_id property is accessed by external callers.
  - Invariant: After first anchor_id access, _anchor_id is a string and remains stable for the lifetime of the instance.

Class-level invariants:
- fields is always a set on the instance (never None after init).
- values is always a dict on the instance (never None after init).
- alert_type is intended to be a valid AlertType member.
- anchor_id, once computed, remains constant (cached).

## Lifecycle:
Creation:
- Constructor signature:
    Alert(alert_type: AlertType, values: Optional[Dict] = None, column_name: Optional[str] = None, fields: Optional[Set] = None, is_empty: bool = False)
- Required arguments:
    - alert_type: an AlertType enum member. Other parameters are optional.
- Typical creation pattern:
    - Checks/detectors create one Alert per detected condition:
        alert = Alert(alert_type=AlertType.MISSING, values={"count": 10}, column_name="age", fields={"age"})
Usage:
- Accessors and typical usage:
    - alert.alert_type_name -> str
        - Returns prettified title-cased label derived from alert_type.name (underscores replaced by spaces).
    - alert.anchor_id -> str
        - Lazily computes and returns a stable string based on hash(column_name) when accessed by external callers. No internal Alert methods call anchor_id automatically; it is intended for use by renderers or consumers that need a stable identifier for linking or keys.
    - alert.fmt() -> str
        - Returns a display string for the alert type. Special-case behavior: when the alert type corresponds to HIGH_CORRELATION it returns an HTML <abbr> tag containing the correlation value and comma-separated related fields extracted from values["fields"] and values["corr"].
    - repr(alert) -> str
        - Calls _get_description() which returns a bracketed alert_type.name and the column_name, e.g., "[MISSING] alert on column age".
- Sequencing:
    - No special ordering required. anchor_id and fmt may be called in any order; anchor_id caches its computed value upon first external access.
Destruction:
- No explicit cleanup or close required. The object participates in normal Python garbage collection.

## Method Map:
graph TD
    A[Constructor: __init__] --> B[alert.alert_type_name]
    A --> C[alert.anchor_id]
    A --> D[alert.fmt()]
    A --> E[repr(alert) -> _get_description()]
    D -->|reads| F[values["fields"], values["corr"]]
    C -->|computes (on external access)| G[hash(column_name)]

(Note: The fmt() method has a special conditional path when the humanized alert name equals "HIGH CORRELATION" — it reads structured keys from values and returns an annotated HTML fragment. No Alert class-internal method invokes anchor_id; external consumers are expected to access it.)

## Raises:
- __init__: No explicit exceptions raised by the constructor in normal use. Possible runtime issues originate from caller-supplied arguments (not validated by the class):
    - TypeError:
        - Trigger condition: Supplying an unhashable column_name (e.g., a list) and then accessing anchor_id triggers TypeError when hashing.
        - Trigger condition: Supplying non-iterable or otherwise incompatible types for fields may cause TypeError when code assumes a set/iterable.
    - KeyError:
        - Trigger condition: Calling fmt() when values is missing expected keys for HIGH_CORRELATION (values does not contain "fields" or "corr").
    - TypeError or ValueError:
        - Trigger condition: If values["fields"] contains non-string entries, join() in fmt() may raise TypeError; if values["corr"] is not displayable as intended, behavior will vary.
- _get_description / __repr__: No exceptions raised other than possibly TypeError if column_name’s stringification raises (rare).

Documented defensive advice:
- Callers should ensure values contains the expected keys for alerts that require structured metadata (notably HIGH_CORRELATION).
- Prefer passing simple strings for column_name.

## Example:
1) Basic creation and inspection:
    from ydata_profiling.model.alerts import Alert
    from ydata_profiling.model.alerts import AlertType

    alert = Alert(
        alert_type=AlertType.MISSING,
        values={"count": 42, "share": 0.21},
        column_name="age",
        fields={"age"}
    )

    print(alert.alert_type_name)   # "Missing"
    print(alert.anchor_id)         # stable hashed string derived from "age"
    print(alert.fmt())             # "MISSING"
    print(repr(alert))             # "[MISSING] alert on column age"

2) HIGH_CORRELATION example (fmt produces annotated HTML):
    alert = Alert(
        alert_type=AlertType.HIGH_CORRELATION,
        values={"fields": ["height", "weight"], "corr": 0.95},
        column_name="bmi",
    )
    print(alert.fmt())
    # -> '<abbr title="This variable has a high 0.95 correlation with 2 fields: height, weight">HIGH CORRELATION</abbr>'

3) Defensive usage:
    # Ensure keys expected by fmt() exist for high-correlation alerts
    if alert.alert_type is AlertType.HIGH_CORRELATION:
        required = {"fields", "corr"}
        if not required.issubset(set(alert.values.keys())):
            # populate or skip formatting
            pass

### `src.ydata_profiling.model.alerts.Alert.__init__` · *method*

## Summary:
Initialize an Alert instance by storing its type, optional payload, optional column name, a collection of related fields, and an emptiness flag — applying simple normalization rules so downstream code can rely on common default values.

## Description:
Known callers and context:
- Constructed by profiling/alert-generation code when an analysis check decides an alert should be created (for example, during correlation detection, missing-value checks, or other validation steps).
- Created during the profiler's result assembly phase, immediately after a condition is detected and before formatting/serializing results.

Why this is a dedicated initializer:
- Centralizes attribute assignment and normalization (notably converting falsy fields/values into new empty containers), ensuring other Alert methods can expect sensible defaults without duplicating normalization logic across the codebase.
- Keeps creation semantics localized and testable separate from data-check logic.

## Args:
    alert_type (AlertType):
        Required. Enum member classifying the alert. If omitted, Python raises TypeError for the missing required positional argument.
    values (Optional[Dict], optional):
        Optional payload providing alert-specific details (e.g., correlation coefficients, lists of fields).
        - Default: None
        - Behavior: If values is falsy (None, empty dict {}, or any object whose bool() is False), self.values is set to a new empty dict {}. If values is truthy, the reference is stored as-is (no type coercion or validation).
    column_name (Optional[str], optional):
        Name of the column the alert pertains to, or None for dataset-level alerts.
        - Default: None
        - Stored verbatim.
    fields (Optional[Set], optional):
        Related field/column names referenced by the alert (e.g., correlated fields).
        - Default: None
        - Behavior: If fields is falsy (None, empty set(), or any object with bool() == False), self.fields is set to a new empty set(). If fields is truthy, the reference is stored as-is (no type coercion or validation).
    is_empty (bool, optional):
        Flag indicating whether the underlying condition is considered empty.
        - Default: False
        - Stored verbatim.

## Returns:
    None
    - This initializer returns nothing; its purpose is to set instance attributes.

## Raises:
    TypeError:
        - If alert_type is omitted when calling __init__, Python will raise TypeError for the missing required positional argument.
    - The method performs no additional runtime type validation and does not raise other exceptions itself.

## State Changes:
Attributes READ:
    - None. The initializer does not read existing instance attributes.

Attributes WRITTEN:
    - self.fields:
        * If the fields argument is truthy, assigned to that exact object reference.
        * If the fields argument is falsy, assigned to a newly created empty set() instance.
    - self.alert_type:
        * Assigned to the provided alert_type value.
    - self.values:
        * If the values argument is truthy, assigned to that exact object reference.
        * If the values argument is falsy, assigned to a newly created empty dict {}.
    - self.column_name:
        * Assigned to the provided column_name (may be None).
    - self._is_empty:
        * Assigned to the provided is_empty boolean.

## Constraints:
Preconditions:
    - The caller must provide alert_type (an AlertType enum member is expected for correct downstream behavior).
    - The initializer does not enforce that values is a dict or fields is a set; passing other types is allowed but may cause errors in other methods that assume specific types.

Postconditions:
    - After return:
        * If fields was falsy on input, self.fields is a new empty set() (identity differs from the passed-in object).
        * If fields was truthy on input, self.fields is the same object as was passed in (which may or may not be a set).
        * Analogously for values: falsy input -> self.values is a new empty dict {}; truthy input -> stored by reference.
        * self.alert_type equals the provided alert_type.
        * self.column_name equals the provided column_name (or None).
        * self._is_empty equals the provided is_empty boolean.

## Side Effects:
    - No I/O, logging, or external service interactions occur.
    - Reference semantics:
        * If truthy mutable containers are provided for fields or values, those same objects are referenced by the Alert instance (external mutations will be observable through the Alert).
        * If empty containers (which are falsy) are provided, they are not preserved; the initializer replaces them with new empty containers, so object identity is not preserved for empty inputs.

### `src.ydata_profiling.model.alerts.Alert.alert_type_name` · *method*

## Summary:
Return a human-friendly, title-cased string derived from the alert type enum for display or reporting.

## Description:
This method reads the Alert object's alert_type enum member and formats its name into a presentation-friendly label by replacing underscores with spaces, lowercasing, and then title-casing the result.

Known callers and context:
- Presentation/reporting code that needs a readable label for an alert (e.g., rendering alert headings in HTML reports, logging, or serializing alerts for UIs).
- Any conversion/serialization step that transforms an Alert object into human-readable output.

Example transformation (textual):
- An alert_type with name "MISSING_VALUES" becomes "Missing Values".
- An alert_type with name "high_variance" becomes "High Variance".

Rationale for being a separate method:
- Centralizes alert-type formatting so all presentation layers use a single consistent transformation.
- Keeps presentation logic out of higher-level rendering or serialization code and makes future formatting changes easy.

## Args:
This method takes no arguments.

## Returns:
str: A title-cased, human-readable representation of self.alert_type.name.
- Produced by: self.alert_type.name.replace("_", " ").lower().title()
- Typical values: strings like "Missing Values", "High Variance", etc.
- Edge cases:
  - If alert_type.name is an empty string, the method returns an empty string.
  - Non-letter characters (digits, punctuation) are preserved; only underscores are converted to spaces before title-casing.

## Raises:
- AttributeError: If self.alert_type is None or does not have a .name attribute, or if .name is not a string (for example, attempting to call .replace on a non-string will raise AttributeError). These are runtime errors caused by invalid object state; the method does not explicitly raise custom exceptions.

## State Changes:
Attributes READ:
- self.alert_type

Attributes WRITTEN:
- None — the method does not modify the Alert object or other state.

## Constraints:
Preconditions:
- self.alert_type must be an object exposing a .name attribute (typically an Enum member).
- The .name attribute should be a string for correct formatting.

Postconditions:
- No mutation to self; the method returns a formatted string derived from self.alert_type.name.
- The returned string is guaranteed to have underscores replaced with spaces and to be title-cased.

## Side Effects:
- None. The method performs pure string manipulation and has no I/O, network calls, or mutations of external objects.

### `src.ydata_profiling.model.alerts.Alert.anchor_id` · *method*

## Summary:
Return and memoize a string identifier for this Alert instance; on first access it computes the identifier from the column name and stores it on the instance.

## Description:
- Known callers:
    - No callers are defined inside this Alert class. The property is intended for external consumers (for example, report renderers or link generators) that need a per-alert identifier to reference or anchor alerts. There are no internal references to this property within this module.
- Invocation context:
    - Typically accessed during report generation, serialization, or any stage where a stable per-instance identifier is required for linking or HTML anchors.
- Rationale for being a separate method/property:
    - Centralizes and documents the anchor-generation logic.
    - Provides memoization (cache on first access) so the identifier is computed once and then reused, avoiding repeated hashing and ensuring a stable identifier for the lifetime of the object instance.

## Args:
    None

## Returns:
    Optional[str]:
    - If self._anchor_id is already set (non-None), returns that value.
    - Otherwise, computes str(hash(self.column_name)), stores it in self._anchor_id, and returns it.
    - In normal use (with a hashable column_name) the returned value is a str representation of an integer hash (e.g., "-123456789").
    - The method can return None only if self._anchor_id remains None (for example, if hashing was not performed due to an exception or if another piece of code explicitly sets self._anchor_id to None after access).

## Raises:
    TypeError:
    - Raised if self.column_name is an unhashable object (e.g., a list). The code calls hash(self.column_name); if that call raises a TypeError, the exception will propagate.

## State Changes:
- Attributes READ:
    - self._anchor_id
    - self.column_name
- Attributes WRITTEN:
    - self._anchor_id (set to str(hash(self.column_name)) when it was previously None)

## Constraints:
- Preconditions:
    - The Alert instance must be initialized. The column_name is expected to be a hashable object (typically a str or None). If column_name is None, hashing None is permitted and will produce an identifier.
- Postconditions:
    - After a successful call when self._anchor_id was previously None, self._anchor_id is a str equal to str(hash(self.column_name)).
    - Subsequent calls will return the same str value without recomputing the hash.
    - If column_name is later mutated or replaced after the anchor was computed, the stored anchor_id will not update automatically; callers that require anchor to reflect new column_name must clear or reset self._anchor_id.

## Side Effects:
- Mutates only the Alert instance by setting self._anchor_id on first computation.
- No I/O, no network calls, and no interactions with external services.
- Note on stability: Python's built-in hash() for strings is randomized per interpreter process (hash randomization); therefore the produced identifier is not guaranteed stable across separate Python processes or interpreter restarts — it only remains stable for the lifetime of the process and the Alert instance.

### `src.ydata_profiling.model.alerts.Alert.fmt` · *method*

## Summary:
Return a presentation-ready label for this alert. For most alerts this is the alert-type name with underscores replaced by spaces; for a HIGH CORRELATION alert the method returns an HTML <abbr> element that embeds correlation details. The method does not modify the Alert instance.

## Description:
This method formats the alert type for display. Implementation details:
- It reads self.alert_type.name and converts underscores to spaces.
- If the resulting name equals the exact string "HIGH CORRELATION" and self.values is not None, it expects self.values to contain correlation details and builds an HTML abbreviation (<abbr>) containing the correlation coefficient, the number of correlated fields, and a comma-separated list of those fields.

Callers / lifecycle:
- There are no callers within the Alert class itself. The method is a presentation helper intended to be called by external code that renders or displays Alert instances (for example, report generators or templates). No specific call sites are referenced in this file.

Why this is a separate method:
- It isolates presentation/formatting logic (including an HTML special-case) from alert construction and business logic so rendering behavior can be reused or changed without altering alert creation.

## Args:
- None besides self.

## Returns:
str
- General case: the alert type name with underscores replaced by spaces (e.g., "MISSING_VALUES" -> "MISSING VALUES").
- HIGH CORRELATION case (only when name == "HIGH CORRELATION" and self.values is not None): an HTML string exactly of the form:
  '<abbr title="This variable has a high {corr} correlation with {num} fields: {title}">HIGH CORRELATION</abbr>'
  where:
  - {corr} is the value of self.values["corr"] converted to its string representation,
  - {num} is the integer length of self.values["fields"],
  - {title} is the result of ", ".join(self.values["fields"]).
- Edge-case behavior:
  - If name == "HIGH CORRELATION" but self.values is None, the method returns "HIGH CORRELATION" (the general case).
  - If name == "HIGH CORRELATION" and self.values is not None but lacks required keys or contains values of unexpected types, an exception (see Raises) will propagate instead of a graceful fallback.

## Raises:
- KeyError: If execution enters the HIGH CORRELATION branch (name == "HIGH CORRELATION" and self.values is not None) and required keys "fields" or "corr" are absent from self.values.
- TypeError: If self.values["fields"] is not an iterable of string-convertible items (len/join may raise TypeError), or if join is called on a non-iterable.
- Any exceptions raised while accessing self.alert_type.name (very unlikely if alert_type is a valid Enum) will propagate.

## State Changes:
Attributes READ:
- self.alert_type (reads self.alert_type.name)
- self.values (reads self.values)
- self.values["fields"] and self.values["corr"] (when entering the HIGH CORRELATION branch)

Attributes WRITTEN:
- None — the method does not modify any attributes on self.

## Constraints:
Preconditions:
- self.alert_type must be an object exposing a .name string attribute (typically an Enum member).
- If the alert represents high correlation and self.values is not None, then self.values must be a mapping containing:
  - "fields": an iterable of items convertible to strings,
  - "corr": a value representing the correlation (string or number).

Postconditions:
- The returned string matches the formatting rules described above.
- The Alert instance remains unchanged.

## Side Effects:
- None: this method performs no I/O, network access, or mutations of objects outside self.

### `src.ydata_profiling.model.alerts.Alert._get_description` · *method*

## Summary:
Return a one-line, human-readable description constructed from the alert's type name and the target column. The method is read-only and does not modify object state.

## Description:
Constructs a concise description string using the values available on the Alert instance:
- It obtains the alert type by accessing self.alert_type.name.
- It obtains the target column by accessing self.column_name.
This method centralizes the formatting of the description so callers can obtain a consistent textual representation. The source code does not expose which call sites invoke this method.

## Args:
    None

## Returns:
    str: A formatted string exactly in this pattern:
        "[{alert_type_name}] alert on column {column_name}"
    Where:
        - alert_type_name is the value of self.alert_type.name (usually an Enum member name).
        - column_name is the value of self.column_name (commonly a string).
    Examples:
        "[MISSING_VALUES] alert on column age"
        "[TYPE_MISMATCH] alert on column salary"
    Edge cases:
        - If self.column_name is None, "None" will appear as the column_name substring.
        - No additional sanitization or transformation is applied to either component.

## Raises:
    AttributeError:
        - If self.alert_type is None or missing, or if it lacks a .name attribute, accessing self.alert_type.name will raise AttributeError.
        - If self.column_name is missing as an attribute on the instance, accessing it will raise AttributeError.
    Note: The method does not explicitly catch exceptions; any exception raised while accessing attributes will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.alert_type
        - self.column_name
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The Alert instance must have an attribute alert_type which exposes a .name attribute (commonly an Enum).
        - The Alert instance must have an attribute column_name (ideally a string).
    Postconditions:
        - The Alert instance is unchanged.
        - The method deterministically returns a string derived from the two attributes above.

## Side Effects:
    - None. The method performs no I/O, external calls, or mutations outside the Alert instance.

### `src.ydata_profiling.model.alerts.Alert.__repr__` · *method*

## Summary:
Returns a one-line, human-readable description of the alert for use as the object's representation; it does not modify object state.

## Description:
This dunder method delegates to the Alert._get_description() helper and is invoked whenever a textual representation of the Alert instance is required by Python or the application. Known callers and contexts include:
- The built-in repr() call (repr(alert_instance)) and format specifiers that request the representation (f"{alert_instance!r}").
- Implicit representation when the object appears in containers that are printed (lists, dicts, sets) or in interactive REPL sessions.
- Logging and debugging code that records alert objects.
- Any report-generation or rendering code that uses object representations when serializing or displaying alerts.

This logic is implemented as a separate method (delegating to _get_description) to centralize and encapsulate the textual-format construction in one place. That makes the representation stable, reusable by other components, and easy to test or change without modifying dunder plumbing.

## Args:
    None

## Returns:
    str: A one-line description of the alert in the format:
         "[{ALERT_TYPE}] alert on column {COLUMN_NAME}"
         - ALERT_TYPE is taken from self.alert_type.name (the Enum name).
         - COLUMN_NAME is taken from self.column_name and converted to its string form.
         Edge cases:
         - If column_name is None the string "None" will appear in the returned text.
         - If self.alert_type is None or does not provide a .name attribute, an AttributeError may occur (see Raises).

## Raises:
    AttributeError: If self.alert_type is None or does not have a .name attribute (this is a consequence of reading self.alert_type.name in _get_description).
    (No exceptions are explicitly raised by this method; the above is a possible runtime error from malformed object state.)

## State Changes:
    Attributes READ:
        - self.alert_type (specifically reads its .name via _get_description)
        - self.column_name
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The Alert instance should have been initialized with a valid alert_type that exposes a .name attribute (typically an Enum value) and an optional column_name.
        - The object should be in a valid, initialized state (constructed via Alert.__init__ or by setting compatible attributes).
    Postconditions:
        - No modification to the Alert instance occurs.
        - A string description is returned and can be used for logging, display, or debugging.

## Side Effects:
    - None: this method performs no I/O, network calls, or mutations of external objects; it only computes and returns a string.

## `src.ydata_profiling.model.alerts.ConstantLengthAlert` · *class*

## Summary:
Represents an alert indicating that all observed non-missing entries in a column share the same string length.

## Description:
ConstantLengthAlert is instantiated by profiling checks that detect string-like variables whose observed values all have identical length (for example, every entry has length 10). It exists to carry the canonical alert category (AlertType.CONSTANT_LENGTH) together with minimal metadata useful for rendering and downstream filters. Typical callers are the profiling rule/check implementations that examine a variable's composition and emit an Alert when the min and max observed lengths are equal.

This class is a thin specialization of the generic Alert container:
- It sets the alert_type to AlertType.CONSTANT_LENGTH when constructing the base Alert.
- It sets the alert.fields set to {"composition_min_length", "composition_max_length"} to indicate which metadata keys are relevant for this alert.

Responsibility boundary:
- Store the alert category and associated metadata for a constant-length condition.
- Provide a textual description via _get_description for use by repr()/renderers.
- It does not perform the detection logic itself (that is done by the profiling checks), nor does it perform I/O.

## State:
(Inherits the public state from the base Alert; the subclass does not introduce new attributes beyond what Alert provides.)

- alert_type (AlertType)
  - Value for instances of this class: AlertType.CONSTANT_LENGTH (set by the constructor).
  - Invariant: alert_type remains the enum member representing the constant-length alert for the lifetime of the instance.

- values (Dict)
  - Type: dict
  - Caller-visible keys expected for this alert (convention):
      - "composition_min_length" (int or numeric-like): the minimum observed string length in the column sample
      - "composition_max_length" (int or numeric-like): the maximum observed string length in the column sample
  - Default behavior: when None is passed to __init__, the base Alert converts it to an empty dict (callers should populate the two composition_* keys if they want them displayed).

- column_name (Optional[str])
  - The name of the column this alert targets. May be None for dataset-level alerts; when None the description string will include "None" in the bracketed position.

- fields (Set[str])
  - Fixed by this class to the set {"composition_min_length", "composition_max_length"}.
  - Invariant: fields == {"composition_min_length", "composition_max_length"} for every instance.

- _is_empty (bool)
  - Mirrors the is_empty parameter passed at construction. Used by the profiling pipeline to mark placeholder/empty alerts; the class stores this flag but does not act on it internally.

- anchor_id, alert_type_name, fmt(), etc.
  - Provided by the Alert base class and available for consumers (renderers, report generators). anchor_id is computed lazily by Alert if/when accessed.

Class invariants:
- alert_type has been set to AlertType.CONSTANT_LENGTH by the constructor.
- fields contains exactly the two composition_* keys listed above.
- values is a dict (never None after base-class initialization); keys for composition lengths should be integers or numeric-like when present.

## Lifecycle:
Creation:
- Constructor signature:
    ConstantLengthAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments: none; all parameters are optional.
- Typical instantiation (semantic intent):
    - A check detects that min_length == max_length for a column and creates:
      - values = {"composition_min_length": min_length, "composition_max_length": max_length}
      - alert = ConstantLengthAlert(values=values, column_name=col_name)

Usage:
- Typical method/attribute usage after creation:
    - alert._get_description() -> str
      - Returns a short human-readable description that includes the column name.
      - Usually consumed by repr(alert) or renderers.
    - alert.fmt() (inherited) -> str
      - General formatting for display; may rely on values keys if renderers expect to show the composition lengths.
    - alert.anchor_id (inherited) -> str
      - Lazily computed stable identifier derived from column_name (useful for HTML anchors/links).
- Sequencing:
    - No required method ordering — you can call fmt(), anchor_id, or _get_description() in any order.
    - It is common for a reporting pipeline to create the alert, then call fmt() and access _get_description()/repr() when assembling the report.

Destruction:
- No special cleanup or close required. Normal garbage collection applies.

## Method Map:
graph TD
    A[Constructor: ConstantLengthAlert.__init__] --> B[sets alert_type = AlertType.CONSTANT_LENGTH]
    A --> C[sets fields = {"composition_min_length","composition_max_length"}]
    A --> D[stores values (dict), column_name (Optional[str]), _is_empty (bool)]
    D --> E[base.Alert.fmt()] 
    D --> F[base.Alert.anchor_id (lazy)]
    D --> G[_get_description() -> used by repr()/renderers]

## Raises:
- __init__:
  - The constructor itself does not explicitly raise exceptions for normal inputs.
  - Possible runtime errors originate from improper caller-supplied arguments or later use of inherited helpers:
      - TypeError:
          - Trigger: Passing a non-hashable object as column_name and later accessing anchor_id (hashing column_name may raise).
          - Trigger: Supplying values with unexpected types such that base.Alert.fmt() or string joins in renderers raise TypeError.
      - KeyError:
          - Trigger: Relying on values["composition_min_length"] or values["composition_max_length"] without ensuring those keys exist.
      - ValueError:
          - Trigger: Rare, depends on downstream logic expecting numeric-like lengths but receiving incompatible types.
- Defensive guidance:
  - Callers should pass an explicit dict with the two composition_* keys when they expect these to be displayed.
  - Prefer passing a simple string for column_name to avoid hashing/stringification issues.

## Example:
- Creation and basic use:
    alert = ConstantLengthAlert(values={"composition_min_length": 5, "composition_max_length": 5}, column_name="id")
    # Description used by repr()/renderers:
    description = alert._get_description()   # returns "[id] has a constant length"
    # Access base-class helpers:
    formatted = alert.fmt()                 # general formatted label (behavior from Alert.fmt)
    anchor = alert.anchor_id                # lazily computed stable anchor id for "id"

- Typical profile-check flow (conceptual):
    # After a check determines min_len == max_len for column 'code':
    meta = {"composition_min_length": min_len, "composition_max_length": max_len}
    alert = ConstantLengthAlert(values=meta, column_name="code")
    # Pipeline collects the alert and later renders description and metadata in the report

### `src.ydata_profiling.model.alerts.ConstantLengthAlert.__init__` · *method*

## Summary:
Initializes an alert instance for the "constant length" category by assigning the AlertType.CONSTANT_LENGTH enum member and storing provided metadata (values, column_name, expected fields, and empty-state) on the instance.

## Description:
- Known callers and context:
    - Invoked by profiling code when a higher-level analyzer constructs an alert for a column that has been determined to meet a "constant length" condition. The exact caller is a component in the profiling pipeline responsible for generating alerts; this constructor only sets up the alert object itself.
- Why this logic is its own method:
    - Centralizes the specific initialization values for this alert category (the AlertType enum member and the canonical set of fields associated with this alert). This avoids duplicating the same alert metadata across different parts of the codebase and keeps alert construction consistent.

## Args:
    values (Optional[Dict]): Optional dictionary with details for the alert. Typical keys (expected by downstream renderers) are 'composition_min_length' and 'composition_max_length', but this constructor does not enforce those keys. Default: None.
    column_name (Optional[str]): Name of the column the alert pertains to. May be None. Default: None.
    is_empty (bool): Whether the column/series contained no observed data. Default: False.

## Returns:
    None

## Raises:
    None — the initializer itself does not raise. Any exceptions would originate from callers or other parts of the system.

## State Changes:
- Attributes READ:
    - None (the initializer does not inspect existing instance attributes).

- Attributes WRITTEN:
    - self.fields: set to {"composition_min_length", "composition_max_length"} (as passed to the base Alert initializer).
    - self.alert_type: set to AlertType.CONSTANT_LENGTH (the enum member is stored, not interpreted here).
    - self.values: set to the provided values dict, or to an empty dict if values is None (handled by the base class).
    - self.column_name: assigned from the column_name argument.
    - self._is_empty: assigned from the is_empty argument.

## Constraints:
- Preconditions:
    - No runtime checks are performed here; callers should pass arguments with expected types:
        - values should be a mapping/dict-like if provided.
        - column_name should be a string or None.
        - is_empty should be a boolean.
- Postconditions:
    - After construction, the instance contains:
        - alert_type equal to AlertType.CONSTANT_LENGTH,
        - fields containing 'composition_min_length' and 'composition_max_length',
        - values normalized to a dict (empty if None),
        - column_name and _is_empty set as provided.

## Side Effects:
    - No I/O, no network calls, and no mutations to objects outside of the instance fields listed above.

### `src.ydata_profiling.model.alerts.ConstantLengthAlert._get_description` · *method*

## Summary:
Returns a human-readable description stating that the associated column has a constant length. This is a pure accessor-style method and does not modify the object's state.

## Description:
This method produces the textual message used to describe the constant-length alert for the column represented by this Alert instance.

Known callers and lifecycle context:
- No direct callers are present in the local class body. In the typical lifecycle of alerts, this method is intended to be invoked by alert-rendering, serialization, or reporting code that collects alert descriptions for inclusion in a report or UI. It is the per-alert description provider used when converting an Alert into a human-readable message.

Rationale for being a separate method:
- Extracting the description generation into its own method enables easy overriding by subclasses, localization, unit testing of the message text, and consistent formatting across different alert consumers. Keeping the logic here avoids duplicating the formatting logic in callers.

## Args:
This method takes no explicit arguments beyond self.
- self (ConstantLengthAlert): Instance whose column_name attribute is used to build the message.

## Returns:
- str: A single-line message following the exact format:
    "[{column_name}] has a constant length"
  where {column_name} is the string representation of self.column_name.
  - Examples:
    - If self.column_name == "age": returns "[age] has a constant length"
    - If self.column_name is None: returns "[None] has a constant length"
    - If self.column_name is a non-string (e.g., an integer), it is converted to its string representation inside the formatted output.

## Raises:
- This method does not raise any exceptions itself. Formatting uses Python's f-string conversion; any unusual behavior would stem from unusual __str__ implementations on the column_name object, not from this method.

## State Changes:
- Attributes READ:
    - self.column_name
- Attributes WRITTEN:
    - None (the method does not modify any attributes)

## Constraints:
- Preconditions:
    - The instance (self) must be a valid ConstantLengthAlert object constructed with the column_name attribute set (the constructor in the class sets column_name from the caller). The method will still function if column_name is None or non-string since Python will stringify the value.
- Postconditions:
    - The object's state remains unchanged.
    - The method returns a deterministic string derived from the current value of self.column_name.

## Side Effects:
- None. The method performs no I/O, network access, or mutations of objects outside self.

## `src.ydata_profiling.model.alerts.ConstantAlert` · *class*

## Summary:
Represents an alert indicating that a specific dataset column holds a single constant value (no variation). It is a thin subclass of Alert that sets the canonical alert category to AlertType.CONSTANT and inherits presentation helpers from the Alert base class.

## Description:
ConstantAlert is created by the profiling pipeline when a check detects that a column has only one distinct value across the observed sample. Typical callers are the individual rule/check implementations in the profiling engine (the detector that computes the number of distinct values for a column) and any alert aggregator/factory that collects alerts for later filtering and rendering.

Motivation and responsibility:
- Encapsulates the semantic category "constant column" as an Alert with canonical metadata so renderers, filters, and reports can treat constant-column cases consistently.
- Provides only minimal behavior specific to constant alerts: it fixes alert_type to AlertType.CONSTANT and the set of meaningful fields to {"n_distinct"}; presentation and other convenience methods are inherited from the Alert base class.
- It does not perform detection logic (the check that determines if a column is constant) nor any I/O.

When to instantiate:
- Instantiate when a check finds that a column's number of distinct values equals 1 (or meets the configured threshold for "constant").
- Example caller: a function that inspects a pandas Series and, if series.nunique(dropna=...) <= 1, constructs ConstantAlert(values={"n_distinct": 1}, column_name=col).

## State:
(This class does not introduce new instance attributes beyond those defined on Alert; it simply sets specific initial values.)

- alert_type (AlertType)
    - Type: AlertType enum
    - Value for ConstantAlert: always AlertType.CONSTANT (set by the constructor).
    - Invariant: alert_type on this instance is AlertType.CONSTANT for the lifetime of the object.

- values (Dict)
    - Type: dict
    - Default: If None passed to __init__, the base Alert converts it to an empty dict ({}).
    - Expected keys for consumers of ConstantAlert:
        - "n_distinct" (int or numeric-like): the number of distinct values observed for the column (typical value: 1).
    - Invariant: values is always a dict on the instance (never None after construction).

- column_name (Optional[str])
    - Type: Optional[str]
    - Meaning: The name of the column that the alert is about. May be None for dataset-level alerts, but for ConstantAlert callers typically provide the column name.
    - Constraint: Prefer simple string names; if an unhashable or complex object is supplied, other inherited helpers (e.g., anchor_id) may raise at access time.

- fields (Set[str])
    - Type: set[str]
    - Value for ConstantAlert: {"n_distinct"} (set by the constructor).
    - Meaning: A small set of field keys that are relevant for the alert — used by renderers or formatters to know which values to show.
    - Invariant: fields contains at least "n_distinct" and is a set on the instance.

- _is_empty / is_empty (bool)
    - Type: bool
    - Purpose: Internal flag for placeholder/empty alerts. Set from the is_empty parameter passed to __init__.
    - Default: False.

- _anchor_id (Optional[str]) — inherited lazily from Alert
    - Type: Optional[str]
    - Behavior: Computed lazily when anchor_id property is accessed; cached thereafter. If column_name is not hashable, computing anchor_id may raise TypeError.

Class invariants:
- alert_type == AlertType.CONSTANT.
- fields is a set and includes "n_distinct".
- values is a dict (possibly empty) and, if present, may include numeric "n_distinct".
- _anchor_id, once computed, remains stable for the instance.

## Lifecycle:
Creation:
- Constructor signature:
    ConstantAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments: None required — all parameters are optional. Typical usage provides values and column_name.
- Example instantiation:
    ConstantAlert(values={"n_distinct": 1}, column_name="age")

Usage:
- Read-only usage pattern: Consumers typically inspect alert.alert_type (will be AlertType.CONSTANT), alert.values.get("n_distinct"), alert.column_name, and alert.fields to present or filter alerts.
- Presentation helpers inherited from Alert:
    - repr(alert) / str(repr(alert)): will call the inherited _get_description() on this class which returns a human-readable description.
    - alert.anchor_id: lazily computed identifier for linking in reports (may raise TypeError if column_name unhashable).
    - alert.fmt(): formatting helper inherited from Alert; ConstantAlert does not override fmt(), so default formatting behavior applies.
- Note about AlertType usage: AlertType is an Enum; callers typically compare against members (e.g., alert.alert_type is AlertType.CONSTANT) or serialize using .name/.value. Lookups by invalid names or values (operations on AlertType itself) will raise KeyError or ValueError respectively, per AlertType's documented enum semantics; ConstantAlert does not perform such lookups internally.

Destruction:
- No special cleanup or resources: the object is an ordinary Python object subject to garbage collection. No context manager or close() behavior required.

## Method Map:
graph TD
    A[ConstantAlert.__init__] --> B[Alert.__init__ (sets alert_type, values, column_name, fields, is_empty)]
    B --> C[Instance: alert_type == AlertType.CONSTANT]
    B --> D[Instance: fields == {"n_distinct"}]
    E[alert._get_description()] --> F[returns f"[{column_name}] has a constant value"]
    G[repr(alert)] --> E
    H[renderers/consumers] -->|read| C
    H -->|read| D
    H -->|read| values["n_distinct"]
    H -->|access| anchor_id

(Explanation: __init__ calls the Alert base constructor to set standard attributes; _get_description provides the textual description used by repr and other presenters. Consumers read alert attributes for rendering or filtering.)

## Raises:
- __init__
    - No explicit exceptions are raised by ConstantAlert itself during construction.
    - Possible runtime issues inherited from Alert or caused by caller-supplied arguments:
        - TypeError: If column_name is unhashable and later code attempts to compute anchor_id (hash(column_name)), a TypeError will be raised at that later access.
        - TypeError/KeyError: If downstream consumers (e.g., formatters, renderers) assume values contains "n_distinct" and it is missing or of an unexpected type, they may raise KeyError or TypeError. ConstantAlert does not validate the presence or type of "n_distinct"; callers should supply it when appropriate.
    - Note: AlertType lookup operations (e.g., AlertType['NAME'] or AlertType(value)) are documented on the AlertType enum and may raise KeyError or ValueError for invalid inputs; such operations are not performed by ConstantAlert internally but callers should be aware of those enum semantics.

## Example:
1) Basic creation and inspection:
    # Construct when a check determines a column has a single distinct value
    alert = ConstantAlert(values={"n_distinct": 1}, column_name="country")

    # Inspect typed category
    assert alert.alert_type is AlertType.CONSTANT

    # Read the primary metric for this alert
    n = alert.values.get("n_distinct")   # expected: 1

    # Human-readable description
    description = alert._get_description()   # "[country] has a constant value"
    print(description)

    # Consumers (renderers) may call:
    # - repr(alert)  -> uses _get_description()
    # - alert.anchor_id  -> stable identifier for linking (computed lazily; may raise if column_name unhashable)

2) Defensive usage advice:
    # Prefer supplying the expected metric so formatters/serializers have consistent data
    if "n_distinct" not in (alert.values or {}):
        # populate or skip rendering this metric
        pass

### `src.ydata_profiling.model.alerts.ConstantAlert.__init__` · *method*

## Summary:
Initializes a ConstantAlert instance by delegating to the Alert base class with the CONSTANT category and the canonical field set {"n_distinct"}, updating the alert's stored values, column name, and empty-state flag on the object.

## Description:
- Known callers and context:
    - Instantiated by components that detect a variable/column with a single repeated value (typically when n_distinct == 1) during the dataset profiling stage. Typical callers are alert-producing utilities in the profiling pipeline, e.g., the variable-level checks that compute distinct counts and emit alerts.
    - Also used wherever a typed, ready-to-render alert object for a "constant" variable is required (report renderers, serializers, or alert aggregators).

- Why this is a dedicated method:
    - Encapsulates the canonical configuration for a "constant value" alert (the specific AlertType and the set of fields the alert concerns). Keeping this logic in a subclass constructor prevents callers from having to set the correct alert_type and fields manually each time and centralizes the semantic mapping (CONSTANT -> {"n_distinct"}).

## Args:
    values (Optional[Dict]): Optional dictionary with additional context for the alert (e.g., counts or sample values). Defaults to None; if None, the base class normalizes this to an empty dict.
    column_name (Optional[str]): The name of the column/variable the alert refers to. Defaults to None (alert may be non-column-scoped).
    is_empty (bool): Whether the underlying series/column was empty. Defaults to False.

## Returns:
    None: This constructor returns None and only mutates the instance state via the Alert base class.

## Raises:
    None explicitly: The method does not raise exceptions itself. It delegates to Alert.__init__, which does simple assignment and also does not raise. Passing unexpected types (e.g., non-AlertType-like objects) is not performed here because alert_type is fixed internally.

## State Changes:
- Attributes READ:
    - None of self's attributes are read by this constructor. (It reads only its own arguments.)
- Attributes WRITTEN:
    - self.fields: set to {"n_distinct"} (via Alert.__init__ when fields parameter is provided)
    - self.alert_type: set to AlertType.CONSTANT
    - self.values: set to the provided values dict or to {} if values is None
    - self.column_name: set to the provided column_name (may be None)
    - self._is_empty: set to the provided is_empty boolean
    - Note: self._anchor_id is not set here; it is lazily computed by Alert.anchor_id when accessed.

## Constraints:
- Preconditions:
    - No preconditions on self; method may be called on a newly created ConstantAlert instance during standard instantiation.
    - Arguments should generally have the declared types: values should be a mapping or None, column_name should be a string or None, is_empty should be a bool. The constructor does not enforce runtime type checks.
- Postconditions:
    - After execution:
        - self.alert_type is AlertType.CONSTANT
        - self.fields contains exactly the single element "n_distinct"
        - self.values is a dict (empty dict if None was passed)
        - self.column_name equals the provided column_name (possibly None)
        - self._is_empty equals the provided is_empty boolean

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - Only in-memory mutation: the instance attributes listed under WRITTEN are assigned. There are no mutations to objects outside of self (unless the caller passed a mutable dict as values, which is stored directly on the instance).

### `src.ydata_profiling.model.alerts.ConstantAlert._get_description` · *method*

## Summary:
Returns a human-readable one-line message describing that the target column contains a constant (single repeated) value. The call does not mutate the object.

## Description:
Known callers and contexts:
- repr(alert): The Alert.__repr__ path uses this method to produce the textual representation shown in logs, debugging output, and reports.
- Profiling rule/check implementations: Detection code that finds a variable with a single distinct value (for example, n_distinct == 1) will construct a ConstantAlert and consumers (report generators, logging, or UIs) will call this description to present the finding.
- Renderers or external consumers that need a compact textual summary of the alert.

Lifecycle stage:
- Invoked during report generation, alert formatting, or debugging after an alert instance has been created by the profiling checks. The ConstantAlert instance is typically created at detection time (when a check reports the column has no variation), and this method is called later when a human-readable representation is required.

Why this logic is its own method:
- Centralizes the presentation rule for constant-value alerts so every consumer (repr, renderers, logs) displays a consistent message.
- Keeps small presentation glue separate from detection logic, allowing easy overrides in subclasses or refinements to formatting without touching detection code.

## Args:
- None (method is an instance helper that uses self.column_name)

## Returns:
- str: A formatted message in the exact form "[{column_name}] has a constant value"
    - The column_name is stringified via standard Python string interpolation (i.e., str(self.column_name)).
    - Examples:
        - If column_name == "age" -> "[age] has a constant value"
        - If column_name is None -> "[None] has a constant value"
        - If column_name is a non-string object, its __str__() result is used.
    - Edge cases:
        - If column_name is None, the literal "None" appears inside brackets.
        - Non-string column_name values are coerced to their string representation.

## Raises:
- No explicit exceptions are raised by the implementation itself.
- Possible indirect exceptions:
    - TypeError or other exceptions if converting self.column_name to string triggers an error (e.g., a pathological __str__ implementation on a user-supplied object). This is not produced by the method logic but can propagate from Python's string formatting.

## State Changes:
- Attributes READ:
    - self.column_name
- Attributes WRITTEN:
    - None (the method does not modify any attributes or global state)

## Constraints:
- Preconditions:
    - The instance must be a valid ConstantAlert (constructed via ConstantAlert/__init__). There is no requirement that column_name is non-None, but callers typically supply a string column name.
- Postconditions:
    - The method returns a stable str describing the alert.
    - The ConstantAlert instance remains unmodified (no side-effect on self).

## Side Effects:
- None. The method performs no I/O, does not call external services, and does not mutate objects outside self.

## `src.ydata_profiling.model.alerts.DuplicatesAlert` · *class*

## Summary:
A concrete Alert subtype representing detection of duplicate rows in a dataset. It carries duplicate-count metrics and produces a concise human-readable description used by renderers and repr().

## Description:
DuplicatesAlert is constructed by the profiling pipeline's duplicate-detection check when duplicate rows (or duplicate-related metrics) are found at the dataset level. Its responsibilities are limited to:
- Tagging the condition with AlertType.DUPLICATES (set by the subclass during initialization).
- Holding duplicate-specific metrics in the values mapping for downstream consumers.
- Producing a short description string summarizing the number and share of duplicates.

Typical callers:
- A dataset-level duplicate check implementation in the profiling rules/checks.
- Alert aggregators, filters, and report renderers that collect and present dataset-level alerts.

Responsibility boundary:
- This class only represents and formats metadata for duplicate alerts. It does not perform detection, aggregation logic, or I/O.

## State:
(Inherited attributes from Alert are documented with subclass-specific expectations)

- alert_type
  - Type: AlertType
  - Value: Set to AlertType.DUPLICATES by this subclass via the call to super().
  - Invariant: Instances of this subclass should carry the DUPLICATES enum member.

- values
  - Type: Dict
  - Constructor param: Optional[Dict] = None
  - Expected keys for description formatting:
      - "n_duplicates" (int): absolute number of duplicate rows.
      - "p_duplicates" (float): fractional share of duplicates (expected 0.0..1.0).
  - Default/normalization:
      - The parent Alert class commonly normalizes a None input to an empty dict ({}). Important implications:
          * The source implementation checks "if self.values is not None" — if values is exactly None at runtime, the method returns the fallback string "Dataset has duplicated values".
          * If the parent normalizes None -> {} (so values becomes {}), the condition is True and _get_description() will attempt to access the expected keys and will raise KeyError when they are missing.
  - Valid ranges:
      - n_duplicates: integer >= 0
      - p_duplicates: numeric; typically 0.0 <= p_duplicates <= 1.0 (fmt_percent will format any numeric).

- column_name
  - Type: Optional[str]
  - Default: None
  - Purpose: Optional column target. For dataset-level duplicate alerts this is usually None.
  - Note: Passing non-string or non-hashable objects can cause downstream issues in inherited behaviors (e.g., anchor id generation).

- fields
  - Type: Set[str]
  - Value: Initialized by this subclass as {"n_duplicates"} via the call to super().
  - Purpose: Identifies the metric/field related to the alert.

- _is_empty
  - Type: bool
  - Purpose: Inherited flag that creators may set to mark placeholder or "empty" alerts. This class does not consume this flag beyond storage.

Class invariants:
- alert_type == AlertType.DUPLICATES (as set at construction).
- fields contains "n_duplicates".
- values is a dict-like object on the instance (but may be None prior to any parent normalization); callers should not assume presence of keys without checking.

## Lifecycle:
Creation:
- Constructor:
    DuplicatesAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required args: None mandatory. Typical usage supplies a values dict with "n_duplicates" and "p_duplicates".

Usage:
- Typical flow:
    1. The duplicate detection check computes metrics and constructs DuplicatesAlert with values={"n_duplicates": int, "p_duplicates": float}.
    2. Aggregators and renderers read the alert; renderers/repr() call the instance's description (which uses values).
- Methods ordering:
    - __init__ -> instance exists
    - _get_description() (called by repr or renderers) -> returns a textual description or raises if keys are missing
- No explicit destruction/cleanup.

## Method Map:
graph TD
    A[__init__] --> B[inherit Alert state: alert_type=DUPLICATES, values, column_name, fields={"n_duplicates"}]
    B --> C[_get_description()]
    C -->|if values is not None| D[reads values["n_duplicates"], values["p_duplicates"]]
    D --> E[fmt_percent(p_duplicates)]
    E --> F[return "Dataset has {n} ({pct}) duplicate rows"]
    C -->|if values is None| G[return "Dataset has duplicated values"]
    H[repr(alert) or renderer] --> C

## Raises:
- __init__:
  - The subclass constructor does not raise explicit errors itself. Runtime exceptions may originate from the parent Alert constructor if passed invalid argument types (e.g., passing an unhashable column_name and later triggering anchor generation).
- _get_description():
  - KeyError:
      - Trigger: The instance's values attribute is present (not None) but missing "n_duplicates" or "p_duplicates". This is the likely outcome when the parent normalizes None -> {} and callers attempt to render the description without populating metrics.
  - TypeError:
      - Trigger: p_duplicates is not numeric (e.g., None or a non-numeric object), causing fmt_percent to fail.
  - Other numeric/formatting errors follow fmt_percent semantics (e.g., formatting NaN/inf yields platform-specific strings).

Guidance:
- If you intend the alert to include a user-facing description, prefer providing:
    values = {"n_duplicates": <int> (>=0), "p_duplicates": <float>}
  This is a recommendation (not an absolute requirement) intended to avoid KeyError during formatting.
- If you want to create a placeholder/empty alert, use the is_empty flag or ensure callers handle the possibility of missing metric keys before calling _get_description().

## Example:
1) Typical (recommended) usage — descriptive alert
    alert = DuplicatesAlert(values={"n_duplicates": 42, "p_duplicates": 0.012})
    print(alert._get_description())
    # Expected: "Dataset has 42 (1.2%) duplicate rows"

2) Explicit fallback when values is exactly None
    alert = DuplicatesAlert(values=None)
    # If values remains None on the instance, calling _get_description() yields:
    print(alert._get_description())
    # Output: "Dataset has duplicated values"

3) Caution: parent normalization to {} leading to KeyError
    # If parent Alert normalizes None -> {} during initialization:
    alert = DuplicatesAlert(values=None)
    # values becomes {} on the instance; the following may raise KeyError
    try:
        print(alert._get_description())
    except KeyError:
        # Populate metrics or skip description rendering
        pass

### `src.ydata_profiling.model.alerts.DuplicatesAlert.__init__` · *method*

## Summary:
Initialize the DuplicatesAlert object by delegating to the Alert base initializer with AlertType.DUPLICATES, register the alert field "n_duplicates", and store the provided values, column name, and empty-flag on the instance.

## Description:
Known callers and context:
- Constructed by the profiling pipeline's duplicate-detection step when an alert about duplicated rows or duplicated values must be produced.
- Typical lifecycle stage: invoked during the "checks" or "alerts" phase of profile generation after duplicate-counting logic has run (for a dataset-level or column-level duplicate check).

Why this is a separate method:
- Encapsulates the specific configuration required for a duplicates alert (the alert type and the canonical field name "n_duplicates"), keeping callers simple and ensuring consistent alert metadata across the profiling codebase.

## Args:
    values (Optional[Dict]): Optional mapping with metrics for this alert. Default: None.
        - Recommended/expected keys (not validated here):
            - "n_duplicates" (int): absolute number of duplicate rows/entries.
            - "p_duplicates" (float): proportion of duplicates in [0.0, 1.0] used for human-readable descriptions.
    column_name (Optional[str]): Name of the column this alert refers to, or None for dataset-level alerts. Default: None.
    is_empty (bool): Whether the source series/dataset was empty when the alert was produced. Default: False.

## Returns:
    None

## Raises:
    None explicitly. This constructor does not perform input validation or I/O; it simply forwards parameters to Alert.__init__. Any exceptions would only arise from errors external to this method (for example, if the calling code passes non-hashable objects where hashed values are later required).

## State Changes:
Attributes READ:
    - None (this __init__ does not read existing instance attributes)

Attributes WRITTEN:
    - self.fields: set to {'n_duplicates'} (via the base Alert initializer)
    - self.alert_type: set to AlertType.DUPLICATES
    - self.values: set to the provided dict or to an empty dict if None
    - self.column_name: set to the provided column_name (or None)
    - self._is_empty: set to the provided is_empty boolean

## Constraints:
Preconditions:
    - No hard preconditions enforced by this method; callers may pass None for values and column_name.
    - If a human-readable description is desired (e.g., via _get_description), callers should provide values with keys "n_duplicates" (int) and "p_duplicates" (float between 0 and 1). These keys are used by instance methods but are not validated here.

Postconditions:
    - After construction:
        - instance.alert_type is AlertType.DUPLICATES
        - 'n_duplicates' is present in instance.fields
        - instance.values is a dict (the provided dict or an empty dict)
        - instance.column_name reflects the provided column_name (or None)
        - instance._is_empty equals the provided is_empty flag

## Side Effects:
    - No I/O, logging, or external service calls.
    - No mutation of objects outside self (only instance attributes are set).

### `src.ydata_profiling.model.alerts.DuplicatesAlert._get_description` · *method*

## Summary:
Return a human-readable description of duplicate rows for this alert; does not modify the object's state.

## Description:
This method builds a single-line textual description for a duplicates alert. When detailed values are available on the alert (self.values is a dict containing counts/ratios) it inserts the raw duplicate count and a formatted percentage; otherwise it falls back to a generic message.

Known callers and lifecycle context:
- No direct callers are present in the provided snippet. In typical usage within the profiling/reporting pipeline, this method is invoked by alert rendering or report-generation code that collects Alert objects and needs a human-facing description (for example, when building HTML/JSON/text representations of alerts in the profile report).
- It is intended to be called during the report assembly stage (after analysis has populated Alert.values), not during the low-level data-processing step that computes duplicates.

Why this is a separate method:
- Encapsulates the presentation logic for duplicates alerts (message templating and percentage formatting) so that rendering code can uniformly request a description without duplicating formatting details.
- Keeps the Alert subclass focused: analysis populates values and this method formats them for presentation.

## Args:
- None.

## Returns:
- str: A single-line human-readable description.
  - If self.values is not None and contains expected keys:
    - "Dataset has {n_duplicates} ({formatted_percent}) duplicate rows"
      - {n_duplicates}: string representation of the value stored at self.values['n_duplicates'] (typically an int >= 0).
      - {formatted_percent}: produced by fmt_percent(self.values['p_duplicates']) (typically a percentage string like "12.3%", "< 0.1%", or "> 99.9%").
  - If self.values is None:
    - "Dataset has duplicated values"
  - Edge-case returns:
    - If values exist but fields are malformed/missing, a runtime exception (see Raises) may occur instead of a returned string.

## Raises:
- KeyError: If self.values is not None but the keys 'n_duplicates' or 'p_duplicates' are absent; attempting to index self.values['n_duplicates'] or self.values['p_duplicates'] triggers this.
- TypeError: If self.values is not None but is not subscriptable (e.g., not a dict-like object), or if fmt_percent receives a non-numeric p_duplicates such that numeric operations inside fmt_percent fail.
- Any exceptions raised by fmt_percent for invalid numeric inputs (e.g., TypeError when the value cannot be rounded or multiplied) will propagate.

## State Changes:
- Attributes READ:
  - self.values
- Attributes WRITTEN:
  - None (the method is read-only; it does not mutate self or any external state)

## Constraints:
- Preconditions:
  - The object should be an initialized DuplicatesAlert instance.
  - If a detailed description is desired, self.values must be either None (to force generic message) or a mapping containing at least the keys:
    - 'n_duplicates' (expected: integer-like count of duplicate rows)
    - 'p_duplicates' (expected: numeric fraction, typically in 0.0..1.0, representing the share of duplicate rows)
  - fmt_percent expects p_duplicates to be a numeric type (float/int/numpy scalar); passing non-numeric values will likely raise TypeError.
- Postconditions:
  - The method returns a str formatted as described under Returns.
  - The object's attributes are unchanged.

## Side Effects:
- None: the method performs no I/O, does not call external services, and does not mutate external objects. It only reads self.values and calls the pure helper fmt_percent for presentation.

## `src.ydata_profiling.model.alerts.EmptyAlert` · *class*

## Summary:
A minimal Alert subclass that denotes an empty dataset or empty series. It encapsulates the canonical AlertType for emptiness and provides a concise description for display.

## Description:
EmptyAlert is constructed by profiling code that wants to record an "empty" condition (no observed rows or no observed entries for a column). It is a lightweight container: it does not perform detection or rendering itself — it simply stores metadata and returns a short description.

Key points:
- AlertType is an enumeration (AlertType) defined elsewhere; EmptyAlert uses the enum member AlertType.EMPTY to label the alert category.
- By convention EmptyAlert initializes its fields set to {"n"}, where "n" is the conventional key for an observation count.

Typical callers:
- Detector functions or rule implementations in the profiling pipeline that have determined a dataset or column is empty and need to emit a typed alert object.
- Aggregators and renderers that consume Alert objects to build reports or summaries.

## State:
(Inherits attributes and normalization behavior from Alert; the following notes highlight EmptyAlert-specific choices.)

- alert_type (AlertType)
  - Type: AlertType enum member
  - Value for EmptyAlert instances: AlertType.EMPTY (set during construction)
  - Invariant: Instances of EmptyAlert have alert_type equal to AlertType.EMPTY.

- values (Dict)
  - Type: dict
  - Default: {} when None is provided (normalized by the base class)
  - Typical content: may include the integer count under key "n" (commonly 0 for emptiness)

- column_name (Optional[str])
  - Type: Optional[str]
  - Default: None
  - Description: Name of the affected column for column-scoped alerts; None is typical for dataset-level emptiness alerts

- fields (Set[str])
  - Type: set[str]
  - Value set by constructor: {"n"}
  - Semantics: Follows the convention that "n" denotes the observation count; ensures consistent downstream handling when consumers expect this key

- _is_empty (bool)
  - Type: bool
  - Default: False unless explicitly set by the caller
  - Semantics: Passed through to the base class and available to consumers; not interpreted by EmptyAlert itself

Class invariants:
- alert_type is the enum member AlertType.EMPTY
- fields is a set containing the string "n"
- values is a dict (never None after initialization, per the base-class behavior)

## Lifecycle:
Creation:
- Constructor parameters:
    - values: Optional[Dict] = None
    - column_name: Optional[str] = None
    - is_empty: bool = False
- Instantiation:
    - Call EmptyAlert(values=..., column_name=..., is_empty=...)
    - The constructor calls the Alert base-class constructor with alert_type set to AlertType.EMPTY and fields set to {"n"}, forwarding values, column_name, and is_empty.

Usage:
- After construction, consumers may:
    - Inspect alert.alert_type to detect that the category is AlertType.EMPTY.
    - Read alert.values to obtain recorded metrics (e.g., {"n": 0}).
    - Call inherited helpers (fmt(), anchor_id, repr()) provided by Alert for display or linking.
- There is no required ordering of method calls; description and metadata are immediately available.

Destruction:
- No special cleanup; normal GC applies.

## Method Map:
graph TD
    A[EmptyAlert.__init__] --> B[Alert.__init__]
    B --> C[alert_type set to AlertType.EMPTY]
    B --> D[fields set to {"n"}]
    B --> E[values normalized to dict]
    A --> F[_get_description() -> "Dataset is empty"]
    F --> G[repr() uses _get_description()]

(Note: fmt() and anchor_id are inherited from Alert and can be called by external consumers.)

## Raises:
- __init__:
  - EmptyAlert.__init__ does not explicitly raise exceptions.
  - Potential runtime errors stem from improper caller-supplied arguments or later consumers:
    - TypeError may occur later if an unhashable column_name is used by Alert.anchor_id (hashing).
    - TypeError or KeyError may occur in downstream code that assumes particular keys or types in values; EmptyAlert itself does not validate values beyond passing it to the base class.

## Example:
1) Dataset-level empty alert:
   - Create:
     alert = EmptyAlert(values={"n": 0}, column_name=None, is_empty=True)
   - Inspect:
     - alert.alert_type is AlertType.EMPTY
     - alert.values == {"n": 0}
     - repr(alert) includes the description returned by _get_description(), which is "Dataset is empty"

2) Column-level empty alert:
   - Create:
     alert = EmptyAlert(values={"n": 0}, column_name="age")
   - Consumers can call alert.anchor_id (inherited) to obtain a stable identifier; anchor_id computation is implemented by Alert.

Implementation note for reimplementers:
- To reimplement EmptyAlert:
  - Subclass the Alert container type.
  - In __init__, call the base constructor with alert_type set to AlertType.EMPTY and fields set to {"n"}, and pass through values, column_name, and is_empty.
  - Override _get_description() to return the literal string "Dataset is empty".

### `src.ydata_profiling.model.alerts.EmptyAlert.__init__` · *method*

## Summary:
Constructs an Alert object representing an EMPTY variable and initializes the alert's metadata (alert type, relevant fields, provided values, column name and empty flag) so the instance is ready for rendering and downstream checks.

## Description:
This initializer is called when the profiling pipeline detects that a variable/series contains no observed data and an EMPTY alert should be created. Typical callers are alert-builder code or variable-analysis routines during the "column analysis" phase of profiling that accumulate alerts for each column. The logic is kept in a dedicated EmptyAlert constructor to centralize the canonical initialization for EMPTY alerts (pre-setting the alert type and the set of relevant fields like "n") rather than repeating those values at each call-site; this ensures consistent alert metadata and simplifies rendering/serialization code that expects these attributes.

## Args:
    values (Optional[Dict]): Optional dictionary of additional alert metadata. If None is passed, the parent Alert initializer will normalize this to an empty dict. Common/expected keys include:
        - "n" (int): the number of observations (typically 0 for an empty series). This key is declared as part of the alert's fields (see below).
    column_name (Optional[str]): The name of the column/variable the alert refers to. May be None for dataset-level or unnamed series alerts, but providing a name is recommended for readable descriptions and anchors.
    is_empty (bool): Boolean flag indicating whether the variable was observed as empty. Defaults to False (but callers constructing an EmptyAlert will typically pass True).

## Returns:
    None: This is an initializer; it returns None. After return the instance is fully initialized with normalized attributes (see Postconditions).

## Raises:
    None: The constructor does not raise exceptions directly. (The parent Alert.__init__ performs simple assignments and also does not raise.)

## State Changes:
    Attributes READ:
        - None (this initializer does not read existing instance attributes prior to assignment).
    Attributes WRITTEN:
        - self.fields: set to {"n"} (the set of field keys relevant to EMPTY alerts)
        - self.alert_type: set to AlertType.EMPTY
        - self.values: set to the provided values dict, or normalized to {} by the parent initializer if values is None
        - self.column_name: set to the provided column_name (may be None)
        - self._is_empty: set to the provided is_empty boolean

## Constraints:
    Preconditions:
        - No strict preconditions enforced by the constructor. Caller should pass a boolean for is_empty and, if meaningful metadata is available, a mapping for values (e.g., containing an integer "n").
        - For best results, provide a non-None column_name when the alert is about a specific dataset column.
    Postconditions:
        - self.alert_type is AlertType.EMPTY
        - self.fields is a set containing the single string "n"
        - self.values is guaranteed to be a mapping (dict) after initialization (empty dict if None was supplied)
        - self.column_name equals the supplied column_name
        - self._is_empty equals the supplied is_empty value

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self (only assigns attributes on self).
    - No global state is modified.

### `src.ydata_profiling.model.alerts.EmptyAlert._get_description` · *method*

*No documentation generated.*

## `src.ydata_profiling.model.alerts.HighCardinalityAlert` · *class*

## Summary:
A typed Alert subclass representing a "high cardinality" condition for a dataset column; when provided with metadata it returns a concise human-readable description that includes the distinct count and a formatted percentage of distinct values.

## Description:
HighCardinalityAlert is created by profiling checks that detect many distinct values in a column (for example identifiers or free-text fields). It is a thin wrapper around the generic Alert container that sets the canonical alert_type to AlertType.HIGH_CARDINALITY and provides a specialized description routine.

Typical callers:
- Column-level cardinality/uniqueness checks in the profiling pipeline.
- Alert aggregators and report renderers that format and display alerts.

Responsibility boundary:
- Store metadata relevant to a high-cardinality condition and provide a short textual description via a non-public presentation method.
- Do not perform the detection logic or rendering I/O.

## State:
Constructor parameters (types and defaults)
- values: Optional[Dict] = None
  - Meaning: Optional mapping carrying alert-specific metadata.
  - Expected keys for detailed formatting (when values is provided):
      - "n_distinct" (int-like): number of distinct values observed.
      - "p_distinct" (float-like): fraction (0..1) of distinct values; formatted using fmt_percent.
  - Behavior note: _get_description checks whether self.values is not None. If values is provided but lacks the expected keys, attempting to format the detailed message will raise KeyError. Callers should ensure values contains the expected keys before invoking presentation helpers.
- column_name: Optional[str] = None
  - Meaning: The name of the column targeted by the alert. Used in the description string.
  - Constraint: Prefer passing simple strings; unusual types may produce unexpected text when coerced to str.
- is_empty: bool = False
  - Meaning: A marker forwarded to the base Alert indicating a placeholder/empty alert; this subclass does not change behavior based on it.
- fields: Set[str] — Set by this subclass to {"n_distinct"} via the super() call to indicate the metadata field relevant to this alert.
- alert_type: AlertType — This subclass sets alert_type to AlertType.HIGH_CARDINALITY via the base-class constructor call.

Class invariants:
- alert_type == AlertType.HIGH_CARDINALITY.
- fields contains "n_distinct".
- values may be None or a Dict depending on how the Alert/creator constructs the object; if present, expected keys are as listed above.

## Lifecycle:
Creation:
- Signature:
    HighCardinalityAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments: none. Typical creation supplies column_name and a values dict with the expected keys.
- Implementation detail: the constructor calls the base Alert constructor with alert_type=AlertType.HIGH_CARDINALITY and fields={"n_distinct"}.

Usage:
- _get_description is the subclass method that returns a short description string (return type: str). It is non-public and intended to be used by base-class presentation helpers (for example, repr() or formatters in renderers).
- Behavior of _get_description:
    - If self.values is not None:
        - It attempts to read values["n_distinct"] and values["p_distinct"].
        - It calls fmt_percent(values["p_distinct"]) to produce a human-friendly percentage string.
        - It returns: "[{column_name}] has {n_distinct} ({fmt_percent}) distinct values"
    - If self.values is None:
        - It returns the generic string: "[{column_name}] has a high cardinality"
- Defensive sequencing advice:
    - Because callers may construct Alert objects with values omitted or incomplete, always validate that values contains "n_distinct" and "p_distinct" before invoking presentation helpers if you want to avoid exceptions.

Destruction:
- No cleanup required; normal garbage collection applies.

## Method Map:
graph TD
    A[__init__(values, column_name, is_empty)]
    A --> B[call super(... alert_type=AlertType.HIGH_CARDINALITY, fields={"n_distinct"})]
    B --> C[_get_description()]
    C -->|if self.values is not None| D[read values["n_distinct"], values["p_distinct"]]
    D --> E[call fmt_percent(values["p_distinct"])]
    E --> F[return detailed string: "[{column_name}] has {n} ({percent}) distinct values"]
    C -->|else (self.values is None)| G[return generic string: "[{column_name}] has a high cardinality"]

## Raises:
- __init__: No explicit exceptions raised by this constructor itself.
- _get_description (presentation path) may raise:
    - KeyError:
        - Trigger: self.values is not None but missing required keys "n_distinct" or "p_distinct".
    - TypeError:
        - Trigger: values["p_distinct"] is not numeric-like and fmt_percent performs numeric operations (round/multiplication).
    - Any exceptions during str() coercion of column_name (rare).
- Defensive recommendation: ensure values contains {"n_distinct", "p_distinct"} before calling presentation helpers if you need the detailed string.

## Example:
1) Correct usage — detailed description:
    alert = HighCardinalityAlert(
        values={"n_distinct": 123, "p_distinct": 0.85},
        column_name="user_id",
    )
    # Presentation helpers (e.g., repr() in base Alert) call _get_description()
    print(repr(alert))
    # -> "[user_id] has 123 (85.0%) distinct values"   # fmt_percent(0.85) -> "85.0%"

2) Generic fallback when values is None:
    alert = HighCardinalityAlert(column_name="session_token")
    print(repr(alert))
    # -> "[session_token] has a high cardinality"

3) Defensive usage to avoid KeyError:
    alert = HighCardinalityAlert(column_name="x", values={})
    if alert.values and {"n_distinct", "p_distinct"}.issubset(alert.values):
        print(repr(alert))
    else:
        print(f"[{alert.column_name}] has a high cardinality")

### `src.ydata_profiling.model.alerts.HighCardinalityAlert.__init__` · *method*

## Summary:
Initialize the alert object as a HIGH_CARDINALITY alert and set the alert's stored fields and metadata accordingly, affecting the instance state used when rendering or serializing alerts.

## Description:
This constructor is invoked when creating an alert that indicates a column has high cardinality. Typical callers are alert-producing code in the profiling pipeline that detects cardinality issues for a specific column (for example, a cardinality-checking function or rule that constructs alerts for columns during dataset profiling). It is separated into its own constructor so that all HIGH_CARDINALITY alerts consistently:
- carry the canonical AlertType (HIGH_CARDINALITY),
- declare which value fields are relevant for this alert (here, "n_distinct"),
- and reuse shared initialization behavior implemented by the Alert base class.

Separating this logic prevents duplication of the alert_type and fields wiring in multiple places and centralizes the identity of which fields a HIGH_CARDINALITY alert uses.

## Args:
    values (Optional[Dict], optional): A dictionary with numeric/statistical values associated with the alert.
        - Default: None
        - Typical keys (convention, not enforced here): 'n_distinct' (int) and 'p_distinct' (float between 0.0 and 1.0) are used by HighCardinalityAlert._get_description when creating a human description.
    column_name (Optional[str], optional): The name of the column for which the alert is generated.
        - Default: None
    is_empty (bool, optional): Whether the column/series is empty.
        - Default: False

## Returns:
    None

## Raises:
    This constructor does not explicitly raise exceptions. Errors may occur later when other code assumes specific types or keys in values (for example, accessing values['n_distinct'] in the description will raise KeyError if that key is missing). No validation is performed here.

## State Changes:
Attributes READ:
    - None in this method itself (it only forwards parameters to the base class).

Attributes WRITTEN (through base Alert.__init__ called by super().__init__):
    - self.fields: set to the provided fields argument or set() fallback. For this class it is set to {"n_distinct"}.
    - self.alert_type: set to AlertType.HIGH_CARDINALITY.
    - self.values: set to the provided values dict, or to {} if values is None.
    - self.column_name: set to the provided column_name value (may be None).
    - self._is_empty: set to the provided is_empty boolean.

## Constraints:
Preconditions:
    - No strict runtime preconditions enforced by this constructor.
    - For meaningful descriptions and downstream usage, callers should provide:
        - column_name: a non-empty string, so human-facing messages can reference the column.
        - values: a dict containing at least 'n_distinct' (and optionally 'p_distinct') if the human description is expected to include counts/percentages.

Postconditions:
    - After returning, the instance has:
        - self.alert_type is AlertType.HIGH_CARDINALITY
        - self.fields contains the single member "n_distinct"
        - self.values is a dict (empty dict if None was passed)
        - self.column_name equals the passed column_name (possibly None)
        - self._is_empty equals the passed is_empty boolean

## Side Effects:
    - No I/O, no logging, and no external service calls.
    - The only observable side effects are the mutations to the instance attributes listed above (no global state is modified).

### `src.ydata_profiling.model.alerts.HighCardinalityAlert._get_description` · *method*

## Summary:
Return a concise, human-readable description for a high-cardinality column, using available cardinality values when present; does not modify object state.

## Description:
This method builds the textual message shown to users or logs for an alert about a column's cardinality. If numeric summary values are provided on the alert (self.values), it produces a detailed message including the number of distinct values and the fraction expressed as a percentage (formatted via fmt_percent). If no summary values are available, it falls back to a generic high-cardinality message.

Known callers and lifecycle context:
- No direct call sites are present in the provided snippet. In typical usage, this method is invoked by the alert/rendering pipeline that composes or displays alerts (for example, code in the Alert base class or an alert manager that collects and formats alerts for reporting). It is part of the report/alert generation stage after column statistics have been computed.

Why this is a separate method:
- Encapsulates presentation-specific logic for the HighCardinality alert message.
- Keeps caller code concise and centralizes message formatting for easier maintenance and consistent wording.
- Isolated so tests or localization changes can target message generation without affecting alert computation logic.

## Args:
- None (method uses object state: self.values and self.column_name).

## Returns:
- str: A human-readable message.
  - If self.values is not None and contains the expected keys:
      "[{column_name}] has {n_distinct} ({formatted_percent}) distinct values"
      - n_distinct is inserted verbatim from self.values['n_distinct'].
      - formatted_percent is produced by fmt_percent(self.values['p_distinct']) and is a string like "12.3%", "< 0.1%", or "> 99.9%".
  - If self.values is None:
      "[{column_name}] has a high cardinality"
  - Edge-case return shapes:
      - If column_name is None, the f-string will include "None" between brackets (e.g., "[None] has ..."); callers should ensure column_name is set for meaningful output.
      - If values contain non-numeric types for p_distinct, fmt_percent may produce unexpected strings or raise TypeError.

## Raises:
- KeyError: If self.values is not None but does not contain the keys 'n_distinct' or 'p_distinct', accessing self.values['n_distinct'] or self.values['p_distinct'] will raise KeyError.
- TypeError (propagated): If self.values['p_distinct'] is not numeric or otherwise incompatible with fmt_percent's numeric operations, fmt_percent may raise a TypeError which will propagate out of this method.
- Other standard exceptions from fmt_percent (e.g., formatting-related errors) may propagate.

## State Changes:
- Attributes READ:
    - self.values: inspected to decide whether to produce a detailed message.
    - self.column_name: used in the generated string.
- Attributes WRITTEN:
    - None. The method is pure with respect to object state (no assignment to self.* attributes).

## Constraints:
- Preconditions:
    - For the detailed message path (when self.values is not None):
        * self.values must be a mapping (dict-like) containing:
            - 'n_distinct': an integer-like value (number of distinct values).
            - 'p_distinct': a numeric fractional value (expected 0.0..1.0 representing the fraction of distinct values).
        * fmt_percent expects a numeric input; callers must provide numeric p_distinct.
    - For meaningful output:
        * self.column_name should be a non-empty string; otherwise the message will include "None" or an empty label.
- Postconditions:
    - The method returns a str and leaves the object's attributes unchanged.
    - No guarantees are made about numeric normalization of p_distinct; the method relies on callers to supply correctly scaled fractions.

## Side Effects:
- None. The method performs no I/O, does not modify global or external state, and only composes and returns a string. It calls the pure helper fmt_percent (which itself has no side effects).

## `src.ydata_profiling.model.alerts.HighCorrelationAlert` · *class*

## Summary:
Represents a HIGH_CORRELATION alert for a single column — a small container that labels a column as highly correlated with one or more other columns and provides a human-readable description derived from provided metadata.

## Description:
HighCorrelationAlert is instantiated by correlation-checking logic in the profiling pipeline when a column is detected to have a high correlation with other column(s). It is a thin subclass of Alert that fixes the alert_type to AlertType.HIGH_CORRELATION and relies on the Alert base class to store metadata (values, column_name, fields, is_empty).

Typical callers / creation sites:
- Correlation check functions or rules in the profiling engine that detect strong linear/non-linear relationships between features and construct Alert objects.
- Alert aggregators/collectors that receive findings from checks and persist or render them in a report.

Motivation and responsibility boundary:
- Purpose: provide a typed alert instance that explicitly represents the "high correlation" condition and encapsulates the small presentation logic for describing the condition.
- Boundary: It does not perform correlation detection itself; it only holds metadata produced by such checks and formats a short description. Detection is performed elsewhere (e.g., perform_check_correlation and related utilities).

## State:
(Attributes are inherited from Alert unless stated; types shown explicitly)

- alert_type (AlertType)
  - Type: AlertType
  - Value for this subclass: AlertType.HIGH_CORRELATION (set by the constructor)
  - Invariant: must be the HIGH_CORRELATION enum member for instances of this class.

- values (Dict)
  - Type: Optional[Dict] provided at construction; if None the Alert base class normalizes to an empty dict in typical Alert implementations.
  - Expected keys (for correct description formatting):
      - "fields": sequence (list/tuple/set) of related field/column names (expected strings). The _get_description implementation reads the 0th element and the length.
      - "corr": numeric or string representation of the correlation value (used verbatim in the description).
  - Constraints:
      - If values is None, _get_description uses a fallback message (see Methods / Raises).
      - If values omits "fields" or "corr" or if "fields" is empty, calling _get_description may raise KeyError or IndexError.

- column_name (Optional[str])
  - Type: Optional[str]
  - Used for embedding the column name in the generated description string.
  - Constraint: If None, the string representation "None" will appear inside square brackets in the description (no explicit check performed).

- _is_empty (bool)
  - Type: bool
  - Default: False (passed through from the constructor)
  - Purpose: an internal marker used by callers to indicate placeholder/empty alerts (no behavior in this class depends on it).

Class invariants:
- The instance's alert_type is HIGH_CORRELATION.
- values is treated as a dict-like mapping by _get_description (presence of expected keys is assumed when values is not None).
- The description returned by _get_description is deterministic given values and column_name; it performs no external I/O.

## Lifecycle:
Creation:
- Constructor signature:
    HighCorrelationAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- How to instantiate:
    - Provide the metadata produced by a correlation check in values, e.g.:
      values = {"fields": ["other_col", ...], "corr": 0.98}
      alert = HighCorrelationAlert(values=values, column_name="my_col")
    - column_name may be omitted (None) for dataset-level or non-column alerts, but the description will include "None" if omitted.

Usage:
- There is no required call order for instance methods.
- Typical usage patterns:
    1. Create instance after a correlation rule detects high correlation.
    2. Store or append the alert to a collection for later rendering.
    3. Renderers or repr() consumers call the instance's description helper. The Alert base class typically calls _get_description() for the textual representation (repr).
- Methods:
    - _get_description() -> str: Called by renderers or repr to obtain a short, human-readable description of the high-correlation condition. See "Methods" for precise behavior.

Destruction:
- No explicit cleanup is required. Instances are normal Python objects and are garbage-collected when no longer referenced.

## Method Map:
graph TD
    A[Constructor: __init__] --> B[Inherited attributes set on Alert]
    B --> C[_get_description()]
    C -->|reads| D[values["corr"]]
    C -->|reads| E[values["fields"][0]]
    C -->|reads| F[len(values["fields"]) > 1]
    C -->|reads| G[column_name]
    style A fill:#f9f,stroke:#333,stroke-width:1px

## Methods (behavioral summary):
- __init__(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
  - Behavior: Calls the Alert base class constructor with alert_type=AlertType.HIGH_CORRELATION and passes values, column_name, and is_empty through unchanged.
  - Side effects: None beyond storing parameters on the instance via the base class.

- _get_description() -> str
  - If self.values is not None:
      - Constructs and returns a string of the form:
        "[{column_name}] is highly {corr} correlated with [{first_field}]"
        If there are additional fields beyond the first, appends:
        " and {n} other fields"
      - Where:
          - {column_name} is the instance's column_name (string conversion applied).
          - {corr} is the verbatim value of self.values["corr"] formatted via f-string (numeric values are converted to their string representation).
          - {first_field} is the first element of self.values["fields"] (index 0).
          - {n} is len(self.values["fields"]) - 1
  - If self.values is None:
      - Returns the fallback string exactly as implemented:
        "[{column_name}] has a high correlation with one or more colums"
      - Note: the fallback string in the source contains the literal substring "colums" (misspelling). This documentation preserves that exact behavior.
  - Edge behaviors and important details:
      - If values is present but does not contain the expected keys:
          - Missing "corr" raises KeyError when accessed.
          - Missing "fields" raises KeyError.
          - An empty "fields" sequence raises IndexError when attempting to access index 0.
      - If values["fields"] contains non-string entries, the formatted description will include their string conversions; if values["fields"] is not indexable (e.g., a set with undefined ordering), the meaning of "first" element depends on iteration order — callers should pass an ordered sequence if deterministic output is required.
      - If column_name is None, the string "[None]" will appear in the returned description.
      - No attempt is made to normalize or round numeric correlation values; formatting is verbatim via f-string.

## Raises:
- __init__:
  - No explicit exceptions are raised by the constructor itself in typical use; it delegates to Alert.__init__ which also does not raise for normal argument types.
  - Potential immediate exceptions:
      - TypeError: If a caller passes arguments of types that prevent standard attribute assignment in the base class (rare).
- _get_description:
  - KeyError:
      - Trigger: values is a dict missing "fields" or "corr".
  - IndexError:
      - Trigger: values["fields"] exists but is empty (access to [0]).
  - TypeError:
      - Trigger: values["fields"] is not indexable and indexing is attempted, or values["fields"] contains elements that cannot be stringified by the f-string expression in some exotic user-defined types.
  - These exceptions are not raised by the constructor but by callers that invoke _get_description when the metadata is malformed.

## Example:
1) Typical creation and description:
    values = {"fields": ["weight", "height"], "corr": 0.95}
    alert = HighCorrelationAlert(values=values, column_name="bmi")
    # Calling the description helper:
    desc = alert._get_description()
    # desc -> "[bmi] is highly 0.95 correlated with [weight] and 1 other fields"

2) Fallback when values is None:
    alert = HighCorrelationAlert(values=None, column_name="age")
    desc = alert._get_description()
    # desc -> "[age] has a high correlation with one or more colums"  (note: literal spelling from source)

3) Defensive usage to avoid exceptions:
    if (alert.values is not None) and ("fields" in alert.values) and ("corr" in alert.values) and len(alert.values["fields"]) >= 1:
        safe_desc = alert._get_description()
    else:
        # handle missing metadata (skip formatting, log, or construct fallback message)
        safe_desc = f"[{alert.column_name}] high correlation detected (metadata incomplete)"

### `src.ydata_profiling.model.alerts.HighCorrelationAlert.__init__` · *method*

## Summary:
Initializes the alert instance for a variable flagged as having a high correlation; sets the alert category and stores the provided metadata (values, column name, and empty-state flag) on the object.

## Description:
This constructor delegates initialization to the Alert base class while fixing the alert_type to the HIGH_CORRELATION category. It is invoked when an alert object representing a detected strong correlation for a column needs to be created — typically by correlation-detection or alert-construction code that runs after correlation checks in the profiling pipeline.

This logic is a dedicated method to ensure every HighCorrelationAlert instance is consistently labeled with AlertType.HIGH_CORRELATION and to centralize any future, alert-specific defaulting or validation separate from generic Alert construction.

Known callers / lifecycle stage:
- Constructed during the alert-generation stage after correlation analysis identifies strong correlations for a column (i.e., by correlation-checking or alert factory code that emits alerts for profiling results).

## Args:
    values (Optional[Dict]): Optional metadata about the correlation. Typical expected keys used elsewhere in this class:
        - 'corr' (float or str): The correlation coefficient or a textual representation.
        - 'fields' (List[str]): List of other field names this column is correlated with.
        Allowed values: any dict or None. Default: None.
    column_name (Optional[str]): The name of the column/variable this alert concerns. May be None. Default: None.
    is_empty (bool): Whether the source series/variable was considered empty. Default: False.

## Returns:
    None: As a constructor, it returns None. The effect is observed via side effects on the instance attributes documented below.

## Raises:
    None: This __init__ does not raise exceptions directly. (Note: downstream code that reads values['corr'] or values['fields'] assumes those keys exist when values is provided; missing keys will raise KeyError when those accessors are used elsewhere, not here.)

## State Changes:
Attributes READ:
    - None (the constructor does not read any pre-existing instance attributes).

Attributes WRITTEN:
    - self.fields: set to fields passed to base constructor (not provided here; defaults to an empty set).
    - self.alert_type: set to AlertType.HIGH_CORRELATION.
    - self.values: set to the passed values dict or an empty dict (Alert.__init__ applies values or {}).
    - self.column_name: set to the passed column_name.
    - self._is_empty: set to the passed is_empty flag.
    - self._anchor_id: left unchanged (initialized lazily by Alert.anchor_id property).

## Constraints:
Preconditions:
    - None required by this constructor: callers may pass None for values or column_name.
    - If callers intend later to use description/formatting helpers, values should be a dict containing 'corr' and 'fields' to avoid KeyError elsewhere.

Postconditions:
    - self.alert_type is AlertType.HIGH_CORRELATION.
    - self.values is a dict (empty dict if None was passed).
    - self.fields is a set (empty set by default).
    - self.column_name and self._is_empty reflect the provided arguments.

## Side Effects:
    - No I/O, no network calls, and no mutations of objects outside the instance.
    - All effects are limited to setting instance attributes via the base Alert initializer.

### `src.ydata_profiling.model.alerts.HighCorrelationAlert._get_description` · *method*

## Summary:
Produce a human-readable description string that states which other column(s) the alerting column is highly correlated with, based on the instance's stored `values`. The method is read-only and does not modify object state.

## Description:
Formats a short sentence describing a high-correlation alert. Behavior:
- If self.values is not None and has the expected structure, returns a sentence containing:
  - the alerting column name (self.column_name),
  - the reported correlation value (self.values['corr']),
  - the first correlated field (self.values['fields'][0]),
  - and, when more correlated fields exist, an appended phrase indicating how many additional fields are correlated.
- If self.values is None, returns a generic fallback sentence.

Context / invocation:
- Called whenever a textual description of the HighCorrelationAlert is required (for example, during report generation or UI rendering).
- The method is separated from detection/storage logic so formatting can be tested, maintained, or overridden independently.

## Args:
None.

However, the method depends on the following attributes initialized by HighCorrelationAlert.__init__:
- self.values: Optional[Dict]. Expected shape when not None:
    - 'corr': any value renderable via f-string (commonly float or str) representing the correlation magnitude or label.
    - 'fields': a sequence (e.g., list or tuple) of field/column names with length >= 1.
- self.column_name: Optional[str]. The name of the column that triggered the alert.

## Returns:
str: The formatted description.

Examples:
- Given self.column_name = "A", self.values = {'corr': 0.95, 'fields': ['B']}:
    "[A] is highly 0.95 correlated with [B]"
- Given self.column_name = "A", self.values = {'corr': 'positive', 'fields': ['B', 'C', 'D']}:
    "[A] is highly positive correlated with [B] and 2 other fields"
- Given self.column_name = "A", self.values = None:
    "[A] has a high correlation with one or more colums"
  (the fallback string matches the exact spelling used in the implementation)

Edge cases:
- If self.column_name is None the formatted output will include "None" in place of the column name.
- If self.values['corr'] is a complex object, its __str__ will be used in the output.

## Raises:
No exceptions are explicitly raised by the method, but it will propagate exceptions if self.values is present but malformed:
- KeyError: if self.values is a mapping missing the 'corr' or 'fields' keys.
- IndexError: if self.values['fields'] exists but is an empty sequence (access to [0]).
- TypeError: if self.values is not subscriptable (e.g., not a dict) or if self.values['fields'] is not indexable/sized.

## State Changes:
Attributes READ:
- self.values (and its sub-entries self.values['corr'] and self.values['fields'])
- self.column_name
Attributes WRITTEN:
- None. The method does not modify self or any external state.

## Constraints:
Preconditions:
- Preferably, self.values is either None or a dict-like object with keys 'corr' and 'fields' where 'fields' is a non-empty sequence.
- Preferably, self.column_name is a string for readable output.

Postconditions:
- A deterministic string describing the alert is returned.
- No mutation to the instance or external objects occurs.

## Side Effects:
- None: no I/O, logging, or external calls are performed.

## `src.ydata_profiling.model.alerts.ImbalanceAlert` · *class*

## Summary:
Represents an alert that a categorical variable (column) is highly imbalanced. Encapsulates the alert category (AlertType.IMBALANCE), optional metadata about the imbalance, and a presentation-friendly description.

## Description:
ImbalanceAlert is instantiated by profiling checks that detect highly imbalanced class distributions in a column (for example, a categorical column where one class dominates). Typical callers are the dataset profiling rules/checks that compute class frequencies, imbalance metrics (e.g., ratio between most frequent and other classes, or share of the top class), and then emit an alert for the offending column.

This class exists as a narrow specialization of the generic Alert container:
- It fixes the alert_type to AlertType.IMBALANCE so alert consumers can identify it by enum rather than string.
- It reserves a specific fields set ({"imbalance"}) and expects the optional values dict to contain the key "imbalance" with a human-readable or numeric measure.
- It provides a concise human-readable description via _get_description() that summarizes the column and, if available, the imbalance metric.

Responsibility boundary:
- Store typed alert metadata for imbalanced class distributions.
- Provide a description used by renderers and repr(); it does not compute imbalance metrics itself nor perform any I/O.

## State:
Inherited from Alert (see Alert documentation) and specialized as follows:

Instance attributes (set/ensured during construction):
- alert_type (AlertType)
  - Type: AlertType
  - Value: Always AlertType.IMBALANCE for this class (set in constructor).
  - Invariant: Should remain AlertType.IMBALANCE for the lifetime of the instance.

- values (Dict)
  - Type: dict
  - Default (constructor): None accepted; the Alert base typically normalizes to {} — callers should consult Alert behavior. For ImbalanceAlert semantics, when provided the values dict is expected to include:
      - "imbalance": str | float | int — a human-readable or numeric metric describing the imbalance (e.g., "0.95", 0.95, "95% / 5%")
  - Valid values: Any mapping type with a string key "imbalance". If values is None, descriptions omit the metric.
  - Invariant: Treated as a dict by methods; if provided but missing the "imbalance" key, methods that reference it may raise a KeyError.

- column_name (Optional[str])
  - Type: Optional[str]
  - Default: None
  - Purpose: Name of the column the alert refers to. If None, description will include the string "None" inside brackets (caller should ideally provide a column name).
  - Constraint: Prefer simple string values; non-hashable values may cause base-class anchor/ID helpers to raise TypeError.

- fields (Set[str])
  - Type: set[str]
  - Value for ImbalanceAlert: The constructor passes {"imbalance"} to the Alert base initializer; thus the instance's fields should include the single element 'imbalance' unless mutated later.
  - Invariant: fields contains at least the element "imbalance" immediately after construction.

- _is_empty (bool)
  - Type: bool
  - Default: False (passed through constructor)
  - Purpose: Marker used by the profiling pipeline to indicate placeholder or suppressed alerts.

Class invariants:
- alert_type is AlertType.IMBALANCE.
- fields contains "imbalance" immediately after initialization.
- values is treated as a dict when present; methods that access values["imbalance"] assume that key exists.

## Lifecycle:
Creation:
- Constructor signature:
    ImbalanceAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required args: none — all parameters are optional, but callers should provide column_name and values["imbalance"] for meaningful alerts.
- Behavior on creation:
    - The constructor delegates to Alert.__init__ with alert_type=AlertType.IMBALANCE and fields={"imbalance"}, preserving values, column_name, and is_empty.

Usage:
- Typical sequence:
    1. A profiling check computes class counts and an "imbalance" metric.
    2. The check constructs ImbalanceAlert(values={"imbalance": <metric>}, column_name="my_col").
    3. Consumers (renderers, report generators) read alert.alert_type / alert.fields and call repr(alert) or alert._get_description() to display a human-friendly message.
- Method ordering / sequencing:
    - No strict ordering required. _get_description() may be called anytime after construction. Other inherited helpers (e.g., anchor_id, fmt()) can be called in any order.
- Destruction:
    - No explicit cleanup required. Normal garbage collection applies. The class does not manage external resources.

## Method Map:
graph TD
    A[Constructor: ImbalanceAlert.__init__] --> B[Inherited: Alert.__init__ stores fields, values, column_name, alert_type]
    B --> C[Consumer: call _get_description() or repr()]
    C --> D[_get_description() reads column_name and optionally values['imbalance']]
    D --> E[Renderer/Report displays the returned text]
    B --> F[Inherited helpers: anchor_id, fmt(), alert_type_name] 

Notes:
- _get_description() is the primary ImbalanceAlert-specific method. It is typically invoked indirectly by repr().

## Raises:
- __init__:
  - No explicit exceptions are raised by ImbalanceAlert.__init__ itself under normal usage because it simply delegates to Alert.__init__.
  - Potential inherited/runtime exceptions:
      - TypeError: If column_name is an unhashable object and later code accesses anchor_id (inherited behavior) that attempts to hash column_name.
      - TypeError/ValueError: If callers pass incorrectly-typed fields/values to Alert, later operations may fail (inherited concerns).

- _get_description():
  - KeyError:
      - Trigger: If values is not None but does not contain the "imbalance" key, the expression self.values['imbalance'] raises KeyError.
  - No other explicit exceptions are raised; formatting uses Python str() semantics for inserted values. If column_name is an object with a problematic __str__, that could raise unexpected exceptions.

Defensive advice:
- Prefer providing column_name as a simple string.
- If including values, include the "imbalance" key with a string or numeric value to avoid KeyError in description rendering.

## Example:
1) Create an ImbalanceAlert with a numeric metric and display its description:
    alert = ImbalanceAlert(values={"imbalance": 0.92}, column_name="country")
    print(alert._get_description())
    # -> "[country] is highly imbalanced (0.92)"

2) Create without values (no metric available):
    alert = ImbalanceAlert(column_name="status")
    print(alert._get_description())
    # -> "[status] is highly imbalanced"

3) Defensive creation to avoid KeyError when downstream code formats values:
    metric = compute_imbalance(series)  # returns None or numeric
    values = {"imbalance": metric} if metric is not None else None
    alert = ImbalanceAlert(values=values, column_name="label")

### `src.ydata_profiling.model.alerts.ImbalanceAlert.__init__` · *method*

## Summary:
Initializes an ImbalanceAlert instance by delegating to the Alert base initializer with the IMBALANCE alert type and a fields set containing "imbalance"; this configures the instance's alert metadata (type, target column, values, fields, and empty flag).

## Description:
This constructor configures an ImbalanceAlert with the specific parameters required for an imbalance-type alert and delegates shared attribute initialization to the Alert base class.

Known callers and context:
- The file does not show explicit instantiation sites. Within the profiling system, ImbalanceAlert instances are expected to be created by the alert-generation logic that detects highly imbalanced columns (the imbalance-check stage of the profiling pipeline).
- Lifecycle: invoked at object construction time before any other Alert methods (for example, fmt() or _get_description()) are called.

Why this logic is its own method:
- Encapsulates the ImbalanceAlert-specific configuration (fixed alert type and fields) so call sites only provide contextual data (values, column_name, is_empty), avoiding repeated argument lists and keeping shared initialization centralized in Alert.__init__.

## Args:
    values (Optional[Dict]): Optional dictionary of values describing the alert (for example a metric keyed by "imbalance"). If None, Alert.__init__ will substitute an empty dict.
    column_name (Optional[str]): Name of the column this alert refers to. May be None if no column context is available.
    is_empty (bool): Flag indicating whether the column was considered empty at the time of alert generation. Defaults to False.

## Returns:
    None: As an initializer, it does not return a value. The method's effect is to set instance attributes.

## Raises:
    No exceptions are explicitly raised by this initializer. Any exception raised during construction would originate from the Alert base-class initializer.

## State Changes:
Attributes READ:
    - None (the constructor does not read existing self attributes; it consumes constructor parameters)

Attributes WRITTEN:
    - self.fields: set to {"imbalance"} (via Alert.__init__)
    - self.alert_type: set to AlertType.IMBALANCE (via Alert.__init__)
    - self.values: set to the provided dict or an empty dict if None was provided (Alert.__init__ uses values or {})
    - self.column_name: set to the provided column_name (via Alert.__init__)
    - self._is_empty: set to the provided is_empty boolean (via Alert.__init__)

## Constraints:
Preconditions:
    - No specific precondition on argument types beyond the type hints: values may be None or a Dict, column_name may be None or a str, is_empty is a bool.
    - The AlertType enumeration must include the IMBALANCE member (AlertType.IMBALANCE) used to classify this alert; Alert is expected to accept these parameters in its constructor.

Postconditions:
    - After initialization, the instance has:
        * alert_type equal to AlertType.IMBALANCE
        * fields equal to a set containing the single string "imbalance"
        * values equal to the provided dict or an empty dict if None was provided
        * column_name equal to the provided column_name (possibly None)
        * _is_empty equal to the provided is_empty boolean
    - The object is ready for use with Alert methods such as fmt() and _get_description().

## Side Effects:
    - No external I/O or network calls are performed.
    - No global state is modified.
    - Only the instance state (self.*) is mutated through the base-class initializer.

### `src.ydata_profiling.model.alerts.ImbalanceAlert._get_description` · *method*

## Summary:
Returns a human-readable one-line description stating that the alerted column is highly imbalanced, optionally appending the numeric/summarized imbalance value when available.

## Description:
Known callers and context:
- repr(alert): The Alert base class's __repr__ uses _get_description() to produce the textual representation shown in logs and reports.
- Profiling rule/check implementations: When an imbalance condition is detected, the profiling pipeline constructs an ImbalanceAlert instance; renderers, report generators, or debug output may call repr() or otherwise request the description.
Lifecycle stage:
- This method is a presentation helper invoked during reporting/representation of an ImbalanceAlert after detection; it is not part of the detection logic itself.

Why this logic is its own method:
- Keeps representation logic isolated from Alert construction and detection code so the textual format can be changed without altering alert-creation logic.
- Enables reuse by any consumer that needs a consistent textual description (repr, logging, UI hints) and centralizes presentation-related edge-case handling.

## Args:
- None.

## Returns:
- str: A single-line description. Two cases:
    - If self.values is not None and contains an "imbalance" entry, returns: "[{column_name}] is highly imbalanced ({self.values['imbalance']})"
    - Otherwise, returns: "[{column_name}] is highly imbalanced"
  Notes:
    - column_name is formatted via Python f-string interpolation; if column_name is None it will appear as "None" in the brackets.
    - The inserted imbalance value is converted to a string using the normal formatting rules; any custom object stored under "imbalance" will be formatted via its __str__/__format__.

## Raises:
- KeyError:
    - Trigger condition: self.values is not None but does not contain the key "imbalance" and callers expect the parent code to access that key elsewhere. (In this method, accessing self.values["imbalance"] will raise KeyError if missing.)
- TypeError (rare):
    - Trigger condition: Stringification/formatting of column_name or values["imbalance"] raises TypeError (highly uncommon; depends on objects provided by callers).

## State Changes:
- Attributes READ:
    - self.column_name
    - self.values
- Attributes WRITTEN:
    - None (the method does not mutate self or external objects).

## Constraints:
- Preconditions:
    - The instance must be an ImbalanceAlert (i.e., self has attributes column_name and values).
    - For the augmented description to include a numeric or textual imbalance, self.values should be a mapping that contains a key "imbalance".
    - For readable output, prefer supplying a str (or str-convertible object) for column_name.
- Postconditions:
    - No mutation occurs on the alert instance.
    - The method always returns a str describing the imbalance; it never returns None.

## Side Effects:
- None: The method performs no I/O, external service calls, or mutations outside of reading self attributes. It only constructs and returns a string.

## `src.ydata_profiling.model.alerts.InfiniteAlert` · *class*

## Summary:
Represents an "infinite values" profiling alert for a specific column — a lightweight container that records how many infinite values were observed (and their share) and provides a human-readable description for reports.

## Description:
InfiniteAlert is instantiated by dataset/column checks that detect infinite numeric values (positive or negative infinity) in a column. Typical callers are the profiling checks or rules that examine a Series and then create an InfiniteAlert when any infinite values are present. This class is a specialized Alert subclass that sets the canonical alert type (AlertType.INFINITE) and advertises the specific fields it populates.

Motivation and responsibility boundary:
- Purpose: provide a typed, presentation-friendly record for the condition "this column contains infinite values", including both a count and a proportion when available.
- Responsibility: store the alert type, structured metadata (values), column name, and a small description generator; it does not perform the detection logic or any I/O.
- Distinct abstraction: encapsulates the exact set of values/fields the infinite-value check produces, centralizing the wording of the alert description.

Known callers/factories:
- The profiling pipeline's rule/check that inspects a pandas Series and counts infinite entries should create an InfiniteAlert (for example, an "infinite values" detector function).
- Alert aggregators or report builders will read this object and call its description/format helpers for rendering.

## State:
Instance attributes (as established by Alert and this subclass):
- alert_type (AlertType)
    - Type: AlertType
    - Value for this class: AlertType.INFINITE (set by the constructor)
    - Invariant: remains the INFINITE member for the lifetime of this instance.
- values (Dict)
    - Type: dict
    - Typical expected keys (when populated by a detector):
        - 'n_infinite' -> int: the absolute count of infinite values found
        - 'p_infinite' -> float: the proportion (fraction 0.0..1.0) of infinite values
    - Default/behavior: If None is passed to the constructor, the Alert base class will normalize to an empty dict (Alert guarantees values is a dict after initialization).
    - Constraints: When present and consumers expect detailed text, the mapping must contain the keys 'n_infinite' and 'p_infinite' with appropriate numeric types. Missing or incorrectly-typed keys will cause _get_description to raise (KeyError/TypeError).
- column_name (Optional[str])
    - Type: Optional[str]
    - Meaning: the name of the column that this alert targets; may be None for dataset-level or unknown-name alerts.
    - Constraint: Consumers should pass a simple string; non-hashable types may cause errors when other Alert helpers (e.g., anchor_id) are used.
- fields (Set[str])
    - Type: set[str]
    - Value set by constructor: {"p_infinite", "n_infinite"} (declares which entries in values this alert occupies)
    - Invariant: always a set on the instance (per Alert class contract).
- _is_empty (bool)
    - Type: bool
    - Set via constructor parameter is_empty (default False). Markers for placeholder alerts; no internal logic depends on it beyond storage.
- _anchor_id (Optional[str])
    - Type: Optional[str]
    - Behavior: managed by Alert lazily; not modified by InfiniteAlert.

Class invariants:
- alert_type == AlertType.INFINITE.
- fields is the set {"p_infinite", "n_infinite"}.
- values is a dict (empty if no details were provided).
- _get_description does not mutate object state.

## Lifecycle:
Creation:
- Constructor signature:
    InfiniteAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required args: none beyond optional parameters; the alert_type is fixed by the class and applied by the call to the Alert superclass.
- Typical instantiation (conceptual):
    - Detector computes n_infinite and p_infinite, then:
        alert = InfiniteAlert(values={"n_infinite": 5, "p_infinite": 0.123}, column_name="my_col")
Usage:
- Typical call sequence:
    1. Create instance via constructor.
    2. Report/render code may query attributes (alert.values, alert.column_name) and call alert.fmt() or repr(alert) which triggers _get_description internally.
    3. _get_description is called to produce the human-friendly message; it reads values and uses fmt_percent to format the proportion.
- Required sequencing: none. _get_description may be invoked any time after construction. No methods must be called before others.
Destruction / cleanup:
- No explicit cleanup is required. Instances are plain Python objects subject to GC. There is no context manager support or close() method.

## Method Map:
graph TD
    A[InfiniteAlert.__init__] --> B[Alert.__init__ (sets alert_type, values, fields, column_name, _is_empty)]
    C[_get_description] -->|reads| D[self.values]
    C[_get_description] -->|reads| E[self.column_name]
    C[_get_description] -->|calls| F[fmt_percent(self.values['p_infinite'])]
    B --> C

(Interpretation: Construction delegates to Alert.__init__. When a description is requested, _get_description reads the instance state and calls fmt_percent to format the percentage.)

## Raises:
Exceptions that may originate from normal use of this class:

- __init__
    - No explicit exceptions raised by InfiniteAlert.__init__ in normal usage. Exceptions may propagate from the Alert superclass if callers provide invalid types (rare).
- _get_description
    - KeyError:
        - Trigger: self.values is not None (or was normalized to dict) but lacks 'n_infinite' or 'p_infinite' keys and the code attempts to access them.
    - TypeError:
        - Trigger: self.values is not a mapping that supports string-key lookup (e.g., a list) or values['p_infinite'] is not numeric and fmt_percent cannot process it.
    - Exceptions from fmt_percent:
        - fmt_percent may raise TypeError if the supplied p_infinite is not numeric; that will propagate up.
Notes:
- The class deliberately does not validate the contents of values at construction time; detectors should supply correctly-typed data to avoid runtime exceptions when formatting.

## Example:
1) Typical creation with details:
    - Detector detects 5 infinite values which are 12.3% of the sample:
      values = {"n_infinite": 5, "p_infinite": 0.123}
      alert = InfiniteAlert(values=values, column_name="my_column")
      # When rendering:
      description = alert._get_description()
      # Example returned string:
      # "[my_column] has 5 (12.3%) infinite values"

2) Creation without detailed counts (fallback message):
    - If a detector only flags the condition without providing counts:
      alert = InfiniteAlert(values=None, column_name="my_column")
      description = alert._get_description()
      # Example returned string:
      # "[my_column] has infinite values"

3) Defensive usage (avoid KeyError when values might be incomplete):
    - if alert.values and {"n_infinite", "p_infinite"}.issubset(alert.values.keys()):
          print(alert._get_description())
      else:
          # Provide an alternate message or skip formatting
          print(f"[{alert.column_name}] has infinite values (details unavailable)")

### `src.ydata_profiling.model.alerts.InfiniteAlert.__init__` · *method*

## Summary:
Configures a new alert instance to represent the presence of infinite values by assigning the INFINITE alert type and registering the canonical metric fields ("p_infinite", "n_infinite"); it sets core attributes (values, column_name, and empty flag) on the object.

## Description:
Called when the profiling pipeline needs to create a typed alert indicating infinite values were observed (or are being reported) for a column/series. Typical callers:
- The per-column analysis stage that counts infinite values and computes their proportion, which then instantiates this alert with those metrics.
- Alert-aggregation or alert-factory utilities that produce specific alert subclass instances as part of a dataset scan.

Why this is its own method:
- Encapsulates the per-alert-type configuration (selecting the AlertType enum member and the canonical fields set) while delegating common attribute assignment to the Alert base class. This preserves a uniform construction pattern across different alert subclasses.

## Args:
    values (Optional[Dict]): Optional mapping of metrics for this alert. Expected keys when provided:
        - "p_infinite": proportion (numeric) of infinite values.
        - "n_infinite": absolute count (int) of infinite values.
      Default: None. The Alert base initializer will replace None with an empty dict.
    column_name (Optional[str]): The name of the column/variable this alert is about. May be None. Default: None.
    is_empty (bool): Boolean flag indicating whether the underlying series/column was empty (no observed rows). Default: False.

## Returns:
    None — this is a constructor and initializes the instance in-place.

## Raises:
    - The constructor does not raise for the documented argument shapes.
    - Passing non-mapping values may cause downstream code that expects dict-like access to raise (TypeError/KeyError), but this initializer does not validate or raise for that.

## State Changes:
Attributes READ:
    - None; the constructor forwards arguments and does not read existing instance fields.

Attributes WRITTEN (via Alert.__init__):
    - self.alert_type: set to the AlertType.INFINITE enum member. Note: this is independent of the is_empty boolean — setting is_empty=True does NOT change alert_type to AlertType.EMPTY; AlertType.EMPTY is a separate enum member used elsewhere when an alert's category should explicitly be EMPTY.
    - self.fields: set to the set {"p_infinite", "n_infinite"}.
    - self.values: set to the provided values dict (by reference) if not None, otherwise to an empty dict (per Alert.__init__ behavior).
    - self.column_name: set to the provided column_name.
    - self._is_empty: set to the provided is_empty boolean.

Important: alert.alert_type is an AlertType enum member; consumers may call .name or .value on it per the AlertType contract.

## Constraints:
Preconditions:
    - The method performs no runtime type checks. Callers should:
        - Provide values as a dict-like mapping when metrics are available.
        - Provide column_name as a string when the alert is column-specific.
Postconditions:
    - The alert instance will have alert_type == AlertType.INFINITE, fields == {"p_infinite","n_infinite"}, and other attributes reflecting the supplied arguments. The object is ready for formatting and serialization that relies on AlertType enum semantics.

## Side Effects:
    - No I/O, logging, or external service interaction.
    - Mutates only the new instance attributes listed above.
    - The supplied values dict is stored by reference; subsequent external mutations to that dict will be visible via alert.values.

## Implementation Notes for Reimplementation:
    - Recreate by calling the Alert base initializer with:
        - alert_type=AlertType.INFINITE
        - values passed through as-is
        - column_name passed through as-is
        - fields={"p_infinite", "n_infinite"}
        - is_empty passed through as-is
    - Do not attempt to map is_empty=True to AlertType.EMPTY here; is_empty is an orthogonal flag.
    - Avoid numeric validation in this constructor; validation belongs to the code that computes "p_infinite"/"n_infinite".

### `src.ydata_profiling.model.alerts.InfiniteAlert._get_description` · *method*

## Summary:
Returns a human-readable description string for an infinite-value alert for the associated column, formatting counts and percentages when detailed values are available. Does not modify object state.

## Description:
Known callers and lifecycle:
    - No direct call sites are present in the provided snippet.
    - Typically invoked by alert/report generation code during the profiling/report assembly stage when textual alert messages are gathered for presentation (for example, when rendering column-level alerts into a report or summary).

Why this is a separate method:
    - Encapsulates the presentation logic for the alert description so formatting and wording are centralized and can be overridden by subclasses if needed.
    - Keeps the rest of the alert machinery focused on detection/state while this small method is responsible solely for human-facing text generation.

## Args:
    (implicit) self:
        - Instance of InfiniteAlert.
        - No additional parameters.

## Returns:
    str:
        - If self.values is not None:
            - A formatted string containing:
                * The column name enclosed in square brackets.
                * The count of infinite values (self.values['n_infinite'] rendered via str()).
                * The percentage of infinite values formatted via fmt_percent(self.values['p_infinite']).
              Example: "[my_column] has 5 (12.3%) infinite values"
        - If self.values is None:
            - A fallback string containing only the column name and a generic message:
              Example: "[my_column] has infinite values"
        - In all cases the method returns a str. The exact formatting of the percentage is delegated to fmt_percent and follows its rules (one decimal place, with special-case strings like "< 0.1%" or "> 99.9%" for very small/near-1 fractions when applicable).

## Raises:
    - KeyError:
        - If self.values is not None but does not contain the expected keys 'n_infinite' or 'p_infinite', accessing self.values['n_infinite'] or self.values['p_infinite'] will raise KeyError.
    - TypeError:
        - If self.values is not None but is not a mapping type that supports __getitem__ with string keys (for example, a list), attempting self.values['n_infinite'] will raise TypeError.
        - If self.values['p_infinite'] is not a numeric type acceptable by fmt_percent, fmt_percent may raise TypeError when performing numeric operations.
    - Other exceptions from fmt_percent:
        - fmt_percent may raise standard numeric-related exceptions (e.g., TypeError) if supplied a non-numeric p_infinite. Those propagate out of this method.
    - Note: The method itself does not perform explicit validation or catch these errors; callers should ensure values is a mapping with the required keys and types if they expect the detailed message.

## State Changes:
    Attributes READ:
        - self.values
        - self.column_name
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - No strict preconditions are enforced by the method, but to produce the detailed message without errors:
            * If a detailed message is desired, self.values must be a mapping containing:
                - 'n_infinite': an integer-like count of infinite values.
                - 'p_infinite': a numeric fraction (typically 0.0..1.0) representing the proportion of infinite values.
            * self.column_name should be set to a meaningful column identifier. If column_name is None, the string "None" will appear in the output inside the square brackets.
    Postconditions:
        - The method returns a str describing the alert.
        - It guarantees it will not change self or other objects; no attributes are added/modified.

## Side Effects:
    - None beyond calling the pure helper fmt_percent (which performs no I/O or state mutation). The method does not perform I/O, logging, or external service calls.

## `src.ydata_profiling.model.alerts.MissingAlert` · *class*

## Summary:
Represents a "missing values" alert for a single dataset column. Encapsulates the alert category (AlertType.MISSING), minimal structured metadata about missingness (count and fraction), and a short human-readable description generator.

## Description:
MissingAlert is created by profiling checks that detect missing values in a specific column. Typical callers are column-level checks or alert aggregators in the profiling pipeline that package detection results into Alert objects for later filtering and rendering.

This class exists to:
- Provide a typed alert object dedicated to missing-value conditions.
- Declare the expected metadata keys for downstream renderers via fields = {"p_missing", "n_missing"}.
- Produce a concise textual description for reporting.

Responsibility boundary:
- Store and expose metadata for missing values on a per-column basis.
- Generate a small human-readable description string.
- It does not perform detection logic, formatting beyond calling fmt_percent for percentage display, or any I/O. Detection and rendering are performed by other components.

## State:
Instance attributes (inherited from Alert and finalized here):
- alert_type (AlertType)
    - Type: AlertType (enum)
    - Value: AlertType.MISSING (set by the constructor via the Alert base)
    - Invariant: For all MissingAlert instances, alert_type == AlertType.MISSING.
- values (dict)
    - Type: dict (or possibly None if the Alert base does not normalize it)
    - Expected keys (when populated for reporting):
        - "n_missing": integer-like count of missing entries for the column.
        - "p_missing": numeric fraction (0.0..1.0 expected) representing the share of missing entries.
    - Notes:
        - MissingAlert's _get_description accesses values['n_missing'] and values['p_missing'] when values is not None.
        - The Alert base class in this codebase often normalizes a None argument into an empty dict ({}). If that normalization occurs, values will be {} (not None) and the _get_description method will enter the branch that expects the two keys — which will raise KeyError if they are absent. See "Raises" for details.
- column_name (Optional[str])
    - Type: Optional[str]
    - Meaning: The column this alert refers to. Prefer simple string values; non-hashable objects may later cause errors when consumers compute anchor ids.
- fields (Set[str])
    - Type: set of str
    - Value: {"p_missing", "n_missing"} (set by the constructor)
    - Meaning: Declares which keys consumers can expect in values for reporting.
- _is_empty (bool)
    - Type: bool
    - Meaning: Passed through to Alert; used by callers to mark placeholder/empty alerts.
- _anchor_id (Optional[str])
    - Type: Optional[str]
    - Meaning: Lazily-computed cached identifier provided by the Alert base (not set by MissingAlert).

Class invariants:
- alert_type is AlertType.MISSING.
- fields contains "p_missing" and "n_missing".
- _get_description will either produce a formatted description using values["n_missing"] and values["p_missing"], or (only) when values is exactly None return a generic fallback string. Because the Alert base commonly normalizes None to {}, the fallback branch will rarely be taken and callers should prefer to supply the expected keys.

## Lifecycle:
Creation:
- Constructor signature:
    MissingAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Usage notes at creation:
    - To produce a safe, descriptive alert, provide values with both expected keys:
        values = {"n_missing": <int>, "p_missing": <float>}
        MissingAlert(values=values, column_name="age")
    - Passing values=None may be normalized by the Alert base to {}, in which case the descriptive branch will attempt to read keys and may raise KeyError later.

Usage:
- Primary behavior:
    - _get_description() -> str
        - If self.values is not None:
            Returns: "[{column_name}] {n_missing} ({fmt_percent(p_missing)}) missing values"
            - It calls fmt_percent(values['p_missing']) to format the fraction as a percentage string (e.g., "4.0%").
            - It directly indexes values['n_missing'] and values['p_missing']; these keys must be present and of appropriate types for successful execution.
        - Else (self.values is None):
            Returns: "[{column_name}] has missing values"
    - Typical caller patterns:
        - Report renderers or stringification utilities may call _get_description to obtain a concise message for UI or logs. (This class provides the description method; it does not itself manage when or where rendering happens.)
- Ordering:
    - No special sequencing is required beyond constructing the object with appropriate values before invoking description/rendering methods.
- Destruction:
    - No cleanup responsibility; garbage collection applies.

## Method Map:
graph TD
    A[MissingAlert.__init__] --> B[set alert_type to AlertType.MISSING]
    A --> C[assign fields = {"p_missing","n_missing"}]
    A --> D[store values (as passed) and column_name]
    E[Renderer/consumer] --> F[call _get_description()]
    F -->|if values is not None| G[read values['n_missing'], values['p_missing']]
    G --> H[call fmt_percent(values['p_missing'])]
    F -->|if values is None| I[return generic fallback string]

## Raises:
- __init__:
    - The constructor itself does not explicitly raise custom exceptions.
    - However, invalid input can lead to runtime errors later (see below).
- _get_description and typical runtime errors:
    - KeyError:
        - Trigger: self.values is present (not None) but missing "n_missing" or "p_missing". Because MissingAlert checks only for values is not None, an empty dict ({}) will cause KeyError when these keys are accessed.
    - TypeError:
        - Trigger: values["p_missing"] is not numeric and cannot be consumed by fmt_percent (which expects a numeric-like value). Also, values["n_missing"] may be non-stringable in extreme cases.
        - Trigger: Non-string column_name values may cause issues downstream when consumers compute anchor ids (hashing) or convert column_name to str.
    - ValueError:
        - Unlikely from MissingAlert itself, but possible if fmt_percent raises for unexpected numeric inputs.
- Defensive guidance:
    - Provide the two expected keys in values to avoid KeyError.
    - Ensure p_missing is numeric (0.0..1.0 intended) so fmt_percent produces a meaningful string.

## Example:
1) Recommended (complete) usage:
    values = {"n_missing": 12, "p_missing": 0.04}
    alert = MissingAlert(values=values, column_name="age")
    desc = alert._get_description()
    # desc -> "[age] 12 (4.0%) missing values"  (fmt_percent formats 0.04 -> "4.0%")

2) Minimal usage (less descriptive; may raise later if base normalizes None to {}):
    alert = MissingAlert(values=None, column_name="id")
    # If values is exactly None, _get_description() -> "[id] has missing values"
    # If the Alert base normalized None to {}, calling _get_description() will attempt to read keys and raise KeyError.

Usage recommendations:
- When creating MissingAlert for reporting, always provide values with both "n_missing" (int) and "p_missing" (float) to guarantee safe description generation.
- Prefer simple string column_name values to avoid downstream hashing or formatting issues.

### `src.ydata_profiling.model.alerts.MissingAlert.__init__` · *method*

## Summary:
Initializes a MissingAlert instance by delegating to the Alert base constructor while fixing the alert category to "MISSING" and declaring the specific fields this alert will expose (percentage and number of missing values). Effect: sets the alert type, values container, target column name, fields set, and empty-state flag on the object.

## Description:
This constructor is invoked when the profiling engine needs to create an alert about missing values for a variable/column. Typical callers and contexts:
- Alert builder / rule-checking code that inspects a variable's summary and decides a missing-value alert is warranted (e.g., during the variable checks stage of the profiling pipeline).
- Any factory or analyzer that constructs a list of Alert objects for later rendering in reports or filtering.

Why this is a dedicated constructor:
- It centralizes the Missing-specific configuration (AlertType.MISSING and the canonical fields {"p_missing","n_missing"}) so callers do not need to repeat these constants.
- Keeps callers simple: they provide only values, column name, and empty flag; all MissingAlert-specific wiring is handled here rather than inlined at each call site.

## Args:
    values (Optional[Dict]): Optional mapping with missing-value metrics. Expected keys (by convention):
        - "p_missing": proportion/percentage of missing values (typically a float between 0.0 and 1.0 or formatted percent string elsewhere).
        - "n_missing": count of missing values (int).
        If None (default), the base Alert constructor will initialize self.values to an empty dict.
    column_name (Optional[str]): Name of the column/variable this alert refers to. May be None, but providing a string gives better descriptions and hashing for anchor_id.
    is_empty (bool): Flag indicating the source column is empty. Defaults to False.

## Returns:
    None — standard constructor. After return, the instance attributes documented in State Changes are set.

## Raises:
    This constructor does not explicitly raise exceptions. However:
    - If callers pass unexpected types in values (e.g., non-mapping objects), no explicit type-check is performed here; this may lead to downstream code expecting dictionary semantics to fail.
    - No exceptions are raised by this method itself under normal usage.

## State Changes:
Attributes READ:
    - None on self. (This constructor only calls the parent constructor and does not read prior instance state.)
Attributes WRITTEN (via Alert.__init__ call):
    - self.fields: set to {"p_missing", "n_missing"}.
    - self.alert_type: set to AlertType.MISSING.
    - self.values: set to values if truthy, otherwise to an empty dict (Alert.__init__ uses `values or {}`).
    - self.column_name: set to the provided column_name (may be None).
    - self._is_empty: set to the provided is_empty boolean.

## Constraints:
Preconditions:
    - None strictly enforced by the code. Recommended: callers should pass a mapping/dict for values with the conventional keys ("p_missing" and "n_missing") to avoid downstream errors.
    - column_name may be None, but a string is recommended for human-readable descriptions and stable hashing of anchor_id.

Postconditions (guaranteed after the call):
    - self.alert_type is AlertType.MISSING.
    - self.fields contains exactly "p_missing" and "n_missing".
    - self.values is a mapping-like object (the constructor sets it to the provided values if truthy; otherwise an empty dict).
    - self.column_name equals the provided column_name argument (possibly None).
    - self._is_empty equals the provided is_empty boolean.

## Side Effects:
    - Mutates the instance (self) by setting the attributes listed in State Changes.
    - No I/O, no network calls, and no modifications to objects outside this instance.
    - Uses the Alert base constructor; any side effects performed there (currently only attribute assignments) are inherited.

### `src.ydata_profiling.model.alerts.MissingAlert._get_description` · *method*

## Summary:
Return a human-readable, single-line description of the missing-value alert for this column, including both the absolute count and a formatted percentage when available.

## Description:
- Known callers and context:
    - No direct callers are present in the provided snippet. There is no explicit reference to where this method is invoked in the available code.
    - Intended usage: called by alert presentation/serialization code (for example, report builders, loggers, or UI renderers) that need a concise, human-readable description of a MissingAlert instance during profiling/report generation.

- Why this logic is a separate method:
    - Centralizes the textual formatting of MissingAlert descriptions so all consumers (reporting, logging, UI) receive the same wording and numeric formatting.
    - Keeps the higher-level alert aggregation and rendering code concise and avoids repeating the same string construction in multiple places.
    - Encapsulates the dependency on the fmt_percent helper so formatting rules can change without altering alert consumers.

## Args:
- None (method uses only self).

## Returns:
- type: str
- Possible return values:
    - If self.values is a mapping that contains the keys 'n_missing' and 'p_missing':
        - "[<column_name>] <n_missing> (<formatted percentage>) missing values"
          Example: "[age] 5 (2.3%) missing values" (the percentage is produced by fmt_percent).
    - If self.values is None:
        - "[<column_name>] has missing values"
          Example: "[age] has missing values"
- Edge-case returns:
    - If fmt_percent produces edge-case shorthand (e.g., "< 0.1%" or "> 99.9%"), that shorthand appears inside the parenthesis.
    - If column_name is None, the returned string will include the literal "None" in place of the column name (e.g., "[None] ..."); callers should ensure column_name is set if that is undesirable.

## Raises:
- KeyError:
    - Triggered when self.values is not None but does not contain the keys 'n_missing' or 'p_missing' and the code attempts to access them via self.values['n_missing'] / self.values['p_missing'].
- TypeError:
    - May arise if self.values is present but is not a mapping supporting __getitem__ with the expected keys (e.g., if self.values is an object that does not support indexing), or if fmt_percent receives a non-numeric value that cannot be multiplied/rounded.
- Note: The method does not explicitly catch or convert these errors; they propagate to the caller.

## State Changes:
- Attributes READ:
    - self.values (Optional[Dict]) — checked for None and, when present, indexed for 'n_missing' and 'p_missing'
    - self.column_name (Optional[str]) — read to include the column identifier in the returned string
- Attributes WRITTEN:
    - None — this method does not modify any attributes on self or external state.

## Constraints:
- Preconditions:
    - The caller should ensure that if self.values is not None then:
        * self.values is a mapping supporting index access with string keys 'n_missing' and 'p_missing'.
        * self.values['n_missing'] is a value representing the number of missing entries (commonly int).
        * self.values['p_missing'] is a numeric fraction (commonly float in 0..1) suitable for fmt_percent.
    - self.column_name is optional; if meaningful display is required, set it to a non-empty string before calling.
- Postconditions:
    - The method returns a str describing the missing-value status for the column.
    - No mutation of self or other objects occurs.

## Side Effects:
- None: the method performs no I/O and calls only the pure formatting helper fmt_percent; it does not modify global state or external resources.

## `src.ydata_profiling.model.alerts.NonStationaryAlert` · *class*

## Summary:
Represents a typed profiling alert indicating a non-stationary variable (time-series whose distribution changes over time). It is a thin subclass of Alert that tags the alert with AlertType.NON_STATIONARY and provides a short textual description.

## Description:
NonStationaryAlert is instantiated by the profiling pipeline when a time-series check or rule detects that a column's statistical properties change over time (non-stationarity). Typical callers are time-series checks or detectors inside the profiling engine that analyze temporal patterns and create alert objects for reporting. This class exists purely to:
- Canonically label the finding with AlertType.NON_STATIONARY.
- Provide a human-readable description via _get_description used by repr()/renderers.

Responsibility boundary:
- It does not perform detection or analysis itself — those are performed by check implementations. It only packages the result (metadata) into an Alert with the appropriate AlertType and a description override.

## State:
This class introduces no new attributes beyond those inherited from Alert. The following attributes are supplied via Alert and remain applicable:

- alert_type (AlertType)
  - Type: AlertType
  - Value for this class: AlertType.NON_STATIONARY (set by constructor)
  - Invariant: must be the NON_STATIONARY enum member for instances of this class.

- values (Dict)
  - Type: dict
  - Initialization: If None is passed to __init__, Alert converts it to an empty dict ({}).
  - Purpose: container for alert-specific metadata if the detector needs to attach details (e.g., test statistics). No specific keys are required by NonStationaryAlert.

- column_name (Optional[str])
  - Type: Optional[str]
  - Default: None
  - Purpose: name of the column/variable under test. If None, description will include the literal "None" because the implementation uses f"[{self.column_name}] ..." without further guarding.

- fields (Set[str])
  - Type: set of strings (inherited and normalized by Alert)
  - Default: empty set when not provided
  - Purpose: used by other alert types; not required for NonStationaryAlert.

- _is_empty (bool)
  - Type: bool
  - Default: False
  - Purpose: marker for placeholder/empty alerts (inherited).

- _anchor_id (Optional[str])
  - Type: Optional[str]
  - Computed lazily by Alert (on first access) from column_name; unchanged thereafter.

Class invariants:
- fields is always a set (never None) after initialization.
- values is always a dict (never None) after initialization.
- alert_type is the NON_STATIONARY enum member for instances of this class.

## Lifecycle:
Creation:
- Constructor signature for reimplementation:
    NonStationaryAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments:
    - None required; all parameters are optional. However, callers typically provide column_name and optionally values with detector details.
- Implementation notes for creation:
    - The constructor must call the Alert base class constructor with alert_type set to AlertType.NON_STATIONARY and forward values, column_name, and is_empty.
    - Do not perform additional validation on values or column_name; preserve Alert's permissive behavior so downstream renderers/formatters handle presentation concerns.

Usage:
- Typical usage order:
    1) A detector identifies non-stationarity for "col" and constructs:
       NonStationaryAlert(values={"stat": test_value}, column_name="col")
    2) The alert is collected into an alerts list and later consumed by formatters/serializers.
    3) Consumers may call methods inherited from Alert, e.g., fmt(), alert_type_name, anchor_id, and repr() which calls _get_description().
- Method sequencing:
    - No required call order. _get_description is used only when a textual description is needed (repr()/renderers).

Destruction:
- No explicit cleanup. Instances are normal Python objects collected by garbage collection. There is no context-manager or close() requirement.

## Method Map:
graph TD
    A[__init__(values, column_name, is_empty)] --> B[Alert.__init__(alert_type=AlertType.NON_STATIONARY,...)]
    B --> C[Inherited properties: values, fields, anchor_id, fmt(), alert_type_name]
    C --> D[_get_description() override in NonStationaryAlert]
    D --> E[repr() / renderers use description]

## Behavior / Methods (implementation details you must reproduce)
- __init__(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
  - Effect: Call Alert.__init__(alert_type=AlertType.NON_STATIONARY, values=values, column_name=column_name, is_empty=is_empty)
  - Side-effects: sets instance.alert_type to AlertType.NON_STATIONARY and initializes inherited state via Alert.
  - Validation: none (do not raise on None values or missing column_name).

- _get_description(self) -> str
  - Returns: a short string used by repr()/renderers. Must return exactly:
        f"[{self.column_name}] is non stationary"
    (note: the implementation intentionally uses the literal string "non stationary" without a hyphen).
  - Edge cases:
    - If column_name is None, the returned string will be "[None] is non stationary".
    - If column_name's __str__ raises, that exception will propagate.

## Raises:
NonStationaryAlert does not explicitly raise exceptions in its own code. However, inherited usage and typical runtime interactions may raise:
- TypeError:
  - Trigger: callers later accessing Alert.anchor_id when column_name is unhashable (e.g., a list).
- KeyError:
  - Trigger: calling Alert.fmt() when values lacks keys expected by formatting logic (not specific to this subclass).
- Any exception raised by str(column_name) will surface from _get_description if column_name's stringification fails.

When reproducing the class, do not add validation that would change these behaviors unless intentionally improving the design; keep behavior consistent with the rest of the alerts.

## Example:
- Create a simple non-stationary alert instance (typical detector usage):
    alert = NonStationaryAlert(values={"test_stat": 12.3}, column_name="sales", is_empty=False)
    # Consumers can call:
    print(repr(alert))                 # -> calls _get_description(), e.g., "[sales] is non stationary"
    print(alert.alert_type)            # -> AlertType.NON_STATIONARY
    print(alert.values.get("test_stat"))# -> 12.3

- Edge-case example when column_name is omitted:
    alert = NonStationaryAlert()
    print(repr(alert))  # -> "[None] is non stationary"

Implementation hint (how to reimplement):
- Define a class that subclasses Alert.
- Its __init__ must pass AlertType.NON_STATIONARY to the Alert base constructor along with values, column_name, and is_empty.
- Implement _get_description() returning the exact formatted string shown above.

### `src.ydata_profiling.model.alerts.NonStationaryAlert.__init__` · *method*

## Summary:
Initializes a NonStationaryAlert instance by delegating to the Alert base-class initializer and setting the alert category to NON_STATIONARY; as a result, the instance's alert_type, values, column_name and empty-flag state are established.

## Description:
- Known/typical callers and context:
    - Constructed by components that detect non-stationarity in a variable or time series during profiling checks. Typical callers are the stage of the profiling pipeline that performs time-series diagnostics and emits alerts when distributional properties change over time (i.e., when a NON_STATIONARY condition is detected).
    - Also used by any report-rendering or aggregation code that needs a typed alert object representing a non-stationary variable.

- Lifecycle stage:
    - Invoked at alert-creation time when a non-stationarity condition is discovered; it prepares the alert object for later formatting, filtering, and rendering.

- Rationale for being a distinct method:
    - Encapsulates the act of creating a typed alert (NON_STATIONARY) so that downstream code can rely on a specific subclass for customized descriptions and any future specialized behavior (e.g., custom formatting, additional metadata). The subclass exists to override descriptive behavior (_get_description) and to keep alert-type assignment centralized rather than inlining the alert_type literal across the codebase.

## Args:
    values (Optional[Dict], default=None): Optional dictionary with additional metadata for the alert (for example, diagnostic values). If None is passed, the base Alert initializer will store an empty dict.
    column_name (Optional[str], default=None): The name of the column/variable this alert refers to. May be None for alerts not bound to a specific column.
    is_empty (bool, default=False): Flag indicating whether the source variable/series was empty; stored on the instance as an internal empty indicator.

## Returns:
    None
    - As a constructor, it returns None; its observable effect is the initialized object state described in State Changes.

## Raises:
    - None raised directly by this initializer.
    - Note: No validation is performed here; invalid types passed in (e.g., non-dict for values) are accepted and stored as-is by the underlying Alert initializer.

## State Changes:
- Attributes READ:
    - (none of self's attributes are read by this method prior to initialization)

- Attributes WRITTEN (set on self as a result of this call; implemented in the Alert base-class initializer invoked here):
    - self.fields: set to the provided fields argument if supplied to Alert (not supplied here) or to an empty set (default).
    - self.alert_type: set to AlertType.NON_STATIONARY.
    - self.values: set to the provided values dict, or to an empty dict if values is None.
    - self.column_name: set to the provided column_name value (may be None).
    - self._is_empty: set to the provided is_empty boolean.

## Constraints:
- Preconditions:
    - No explicit preconditions enforced by this __init__. Callers should provide:
        - values either as a mapping/dict-like object or None.
        - column_name either as a string or None.
        - is_empty as a boolean.
    - If callers rely on downstream consumers computing an anchor_id (which uses column_name), passing a meaningful column_name is advised.

- Postconditions:
    - self.alert_type is guaranteed to be AlertType.NON_STATIONARY.
    - self.values is guaranteed to be a value equal to the passed values argument, or an empty dict if None was passed (assignment performed by Alert.__init__).
    - self.column_name equals the passed column_name value.
    - self._is_empty equals the passed is_empty flag.
    - self.fields is initialized to an empty set unless other code supplies fields via alternate constructor paths.

## Side Effects:
    - No I/O, no network or external service calls.
    - No mutation of objects outside of self, besides storing references to the provided values and column_name in the instance.
    - Lazy-computed properties on the object (for example, Alert.anchor_id) may later derive values from column_name; this initializer influences those later computations by setting column_name.

### `src.ydata_profiling.model.alerts.NonStationaryAlert._get_description` · *method*

## Summary:
Return a concise, human-readable description for the alert by embedding the alert's column name in a fixed sentence; does not modify the object's state.

## Description:
Produces the textual description for a NonStationaryAlert instance in a single, consistent format so reporters and renderers can display the same message wherever alerts are shown.

Known callers and context:
- This method has no callers defined in this file. In typical usage it is invoked by alert-rendering or reporting code (for example, when building the textual output for a report, logging alerts, or serializing alerts for UI consumption).
- It is called at the moment an alert's message string is required (presentation/formatting stage), not during the statistical detection stage.

Why this is a separate method:
- Keeps presentation logic isolated from detection logic and object construction.
- Makes the exact wording easy to override in subclasses or modify for localization/testing without changing alert-generation code.

## Args:
- None.

Note about instance state used:
- self.column_name: Expected type Optional[str] (per the class initializer). Default if not provided is None.

## Returns:
- str: The description in the exact format:
  "[{column_name}] is non stationary"
  Examples:
    - If self.column_name == "age" --> "[age] is non stationary"
    - If self.column_name is None --> "[None] is non stationary"
    - If self.column_name == 123 --> "[123] is non stationary"

Edge-case return values:
- Non-string column names are converted using their string representation.
- Characters in column_name (including '[' or ']') are included verbatim; no escaping is performed.

## Raises:
- None explicitly. The method itself does not raise exceptions under normal circumstances.
- If evaluating str(self.column_name) raises an exception (very unlikely), that exception will propagate to the caller.

## State Changes:
- Attributes READ:
  - self.column_name
- Attributes WRITTEN:
  - None (no modifications to self or other objects)

## Constraints:
- Preconditions:
  - The instance should be initialized. self.column_name may be None, but for meaningful output it should be set to a descriptive column identifier (usually a string).
- Postconditions:
  - The object state is unchanged.
  - The returned string is deterministic for the same self.column_name value.

## Side Effects:
- None. This method performs no I/O, network calls, or mutations of objects outside self.

## Example usage:
- If a NonStationaryAlert instance has column_name set to "temperature", calling this method returns the string:
  "[temperature] is non stationary"

## `src.ydata_profiling.model.alerts.SeasonalAlert` · *class*

## Summary:
Represents a profiling alert that marks a column/variable as seasonally patterned. It is a thin, typed Alert subclass that fixes the alert category to the AlertType enum member named SEASONAL and provides a short textual description.

## Description:
SeasonalAlert is instantiated when a time-series or date-like variable is detected to exhibit seasonality by the profiling checks. Typical callers are the profiling rule/check implementations and alert aggregators in the profiling pipeline that detect seasonal patterns and create alert instances for collection and rendering.

This class exists to:
- Provide a concrete Alert subtype whose alert_type is fixed to the canonical AlertType member SEASONAL (the AlertType member documented to "represent time-series variables that exhibit seasonality") so downstream consumers can reliably identify seasonal alerts.
- Supply a concise, human-readable description via _get_description(), specialized for seasonality.

Responsibility boundary:
- Stores metadata about a detected seasonal condition (delegates general alert behavior and storage to the Alert base class).
- Does not perform seasonality detection itself — that is the responsibility of the check that constructs this object.
- Does not perform I/O or rendering beyond returning description strings used by renderers.

## State:
Inherited attributes (from Alert) and their effective values for SeasonalAlert instances:
- alert_type (AlertType)
  - Type: AlertType
  - Value: the enum member AlertType.SEASONAL (this class enforces this value by passing alert_type=AlertType.SEASONAL to the Alert base constructor)
  - Purpose: Canonical category for seasonality alerts; AlertType.SEASONAL is defined in the AlertType enum as representing time-series variables that exhibit seasonality.
  - Invariant: For any instance of SeasonalAlert, alert_type is expected to be AlertType.SEASONAL.
- values (Dict)
  - Type: dict
  - Default: {} when None is supplied to the constructor (Alert.__init__ normalizes it)
  - Purpose: Arbitrary mapping for alert-specific details (e.g., period, strength). SeasonalAlert does not require any particular keys but checks may populate diagnostics here.
- column_name (Optional[str])
  - Type: Optional[str]
  - Default: None
  - Purpose: The name of the column/variable the alert targets. May remain None for dataset-level alerts.
  - Constraint: Prefer simple string names; if a non-hashable object is provided and anchor_id is later computed, a TypeError may be raised.
- fields (Set[str])
  - Type: set[str]
  - Default: empty set when not provided via Alert constructor
  - Purpose: Related field names; usually empty for a purely seasonal flag unless the creator populates related fields.
- _is_empty (bool)
  - Type: bool
  - Default: False (unless caller sets True)
  - Purpose: Internal flag for creators to mark placeholder/empty alerts.
- _anchor_id (Optional[str])
  - Type: Optional[str]
  - Default: computed lazily by Alert when anchor_id is accessed
  - Invariant: Once computed, it is stable for the lifetime of the instance.

Class invariants:
- values is always a dict (never None after initialization).
- fields is always a set (never None after initialization).
- alert_type equals the AlertType enum member SEASONAL for all SeasonalAlert instances.

## Lifecycle:
Creation:
- Constructor signature:
    SeasonalAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments:
    - None mandatory; all parameters are optional.
- Construction behavior:
    - SeasonalAlert does not accept an alert_type argument; it delegates to Alert.__init__ with alert_type=AlertType.SEASONAL and the supplied values, column_name, and is_empty flag. This enforces the alert category for the instance.
    - Alert.__init__ is responsible for normalizing values to a dict and fields to a set.

Usage:
- Typical sequence:
    1. A seasonality-detection check instantiates SeasonalAlert with optional metadata in values (e.g., period, strength) and column_name set to the inspected column.
    2. Profiling aggregator collects the alert; renderers call attributes and helpers on the Alert base class (for example, alert.alert_type_name, alert.anchor_id, alert.fmt()).
    3. repr(alert) (or Alert._get_description invoked by repr) yields the specialized description from SeasonalAlert._get_description().
- Methods of interest:
    - _get_description(): returns a short textual description (see Method Map).
    - No additional public methods are defined on SeasonalAlert beyond those inherited from Alert.

Destruction:
- No explicit cleanup required. The object follows normal Python garbage collection semantics.

## Method Map:
graph TD
    A[Instantiate SeasonalAlert.__init__] --> B[Alert.__init__ (normalize values/fields, set alert_type=AlertType.SEASONAL)]
    B --> C[Consumers call alert.alert_type_name | alert.fmt() | alert.anchor_id]
    C --> D[repr(alert) -> calls Alert._get_description() which uses SeasonalAlert._get_description()]
    D --> E[SeasonalAlert._get_description() returns "[{column_name}] is seasonal"]

(typical invocation order: create -> consumers read properties/formatting -> repr/description invoked as needed)

## Raises:
- __init__: The constructor itself does not explicitly raise exceptions under normal use.
- Potential runtime issues inherited from Alert (not introduced by SeasonalAlert):
    - TypeError:
        - Trigger condition: Supplying a non-hashable column_name (e.g., a list) and then accessing anchor_id triggers TypeError when hashing.
    - KeyError / TypeError:
        - Trigger condition: Calling Alert.fmt() for other alert types that expect specific keys in values; SeasonalAlert does not expect or require specific keys, but values may be consumed elsewhere.
    - No SeasonalAlert-specific exceptions are raised by _get_description(); if column_name is None, the description will contain the string "None" when formatted.

## Example:
- Create a SeasonalAlert with metadata and inspect the description and type:
    alert = SeasonalAlert(values={'period': 'monthly', 'strength': 0.8}, column_name='invoice_date')
    # alert.alert_type is AlertType.SEASONAL
    # str(alert) / repr(alert) will include the description produced by _get_description:
    # -> "[invoice_date] is seasonal"
    # Typical renderer usage:
    # - read alert.alert_type_name to label the alert
    # - read alert.values for diagnostics (period, strength)
    # - use alert.anchor_id for stable linking in reports

### `src.ydata_profiling.model.alerts.SeasonalAlert.__init__` · *method*

## Summary:
Initializes a SeasonalAlert instance by configuring it as a SEASONAL alert and delegating common initialization to the Alert base class; sets up the alert's type, metadata values, target column name, and empty-state flag on the instance.

## Description:
This constructor is invoked when the profiling pipeline or a detection routine determines that a column/series exhibits seasonality and an alert object must be created to represent that finding. Typical callers are alert-producing code in the time-series or temporal checks stage of the profiler (for example, a seasonal-detection routine that scans columns and creates alerts for those exhibiting periodic patterns).

The logic is implemented as a small constructor method rather than being inlined where alerts are produced to centralize how Seasonal alerts are created and to reuse common initialization implemented by the Alert base class. This ensures all alerts share the same attribute setup (fields, values, column_name, internal empty flag) and that the alert_type is consistently set to AlertType.SEASONAL.

## Args:
    values (Optional[Dict]): Optional mapping of alert-specific metadata. If None, the base Alert constructor will normalize this to an empty dict. Typical contents are informational keys describing the detected seasonality (implementation-specific). Default: None.
    column_name (Optional[str]): Name of the column or variable the alert relates to. May be None for alerts that are not column-specific. Default: None.
    is_empty (bool): Flag indicating whether the underlying data series was observed to be empty. Stored on the instance as an internal empty indicator. Default: False.

## Returns:
    None: This is an initializer; it does not return a value. After construction, the instance is usable as an Alert object and its __repr__/_get_description methods reflect the set state.

## Raises:
    No exceptions are raised directly by this constructor. Any exception would originate from the Alert base-class initializer or from invalid input types used by callers (for example, if callers pass objects that cause unexpected behavior when used elsewhere). The constructor itself performs no validation and therefore does not raise on bad types.

## State Changes:
    Attributes READ:
        - None (the constructor does not read any pre-existing instance attributes)

    Attributes WRITTEN (via Alert.__init__ called by super()):
        - self.fields: set to the provided fields argument or to an empty set (fields argument is not provided by SeasonalAlert.__init__; therefore it becomes an empty set).
        - self.alert_type: set to AlertType.SEASONAL.
        - self.values: set to the provided values or to an empty dict if values is None.
        - self.column_name: set to the provided column_name (may be None).
        - self._is_empty: set to the boolean is_empty argument.

## Constraints:
    Preconditions:
        - No invariants are enforced by this constructor; callers should ensure:
            * values is a mapping-like object or None (mismatched types are accepted but may cause errors elsewhere).
            * column_name is a string or None.
            * is_empty is a boolean.

    Postconditions:
        - self.alert_type is guaranteed to be AlertType.SEASONAL.
        - self.values is a dict-like value (the base constructor normalizes None to an empty dict).
        - self.fields is a set (empty set when not supplied).
        - self.column_name equals the provided column_name argument.
        - self._is_empty equals the provided is_empty argument.

## Side Effects:
    - No I/O is performed.
    - No external services or global state are modified.
    - The constructor mutates the instance (self) by setting the attributes listed above.
    - No lazy properties (such as anchor_id) are computed or modified during initialization; they remain in their default state until accessed elsewhere.

### `src.ydata_profiling.model.alerts.SeasonalAlert._get_description` · *method*

## Summary:
Returns a concise, human-readable description stating that the alerted column is seasonal.

## Description:
This helper constructs the textual description used when presenting a SeasonalAlert to users or in reports. It is intended to be called during alert rendering or when creating human-readable summaries of alerts; no additional computation or external resources are used.

Known callers and context:
- No explicit callers are present in the provided method snippet. In typical usage, this method is called by the alert formatting or reporting code that aggregates and renders alerts for a dataset (for example, an alert-to-string / alert-to-report step of an alert generation pipeline).
- It exists as a separate method to centralize and standardize the textual representation for this alert type so that different renderers (HTML, JSON, CLI) can reuse a single, consistent description.

Why this logic is its own method:
- Keeps presentation concern separated from detection logic (the code that determines seasonality).
- Allows override in subclasses or customization without modifying detection code.
- Ensures a single place to change wording/formatting for all outputs.

## Args:
This method takes no arguments.

However, it depends on this instance attribute:
- self.column_name (Any): The column identifier/name used inside the formatted message. It is expected to be representable as a string (None or non-string values will be stringified by the format operation).

## Returns:
str
- The returned string is exactly the column-aware message produced by formatting: "[{self.column_name}] is seasonal"
- Example returns:
    - If self.column_name == "date": "[date] is seasonal"
    - If self.column_name is None: "[None] is seasonal"
- Edge cases:
    - If column_name is not present on self, an AttributeError is raised when accessing self.column_name (see Raises).
    - Non-string column_name values are converted to strings via Python's f-string formatting.

## Raises:
- AttributeError: If the instance does not have the attribute column_name when this method is called.
- No other exceptions are raised explicitly by this method. Any exception raised during attribute access or during Python's formatting will propagate to the caller.

## State Changes:
Attributes READ:
- self.column_name

Attributes WRITTEN:
- None — this method does not modify any attributes on self.

## Constraints:
Preconditions:
- The caller should ensure the object has a meaningful self.column_name attribute prior to calling this method (recommended: a string or an object with a useful __str__ implementation).

Postconditions:
- No mutation of self occurs.
- A non-empty string is returned in normal conditions (the exact content depends on the stringification of self.column_name).

## Side Effects:
- None: the method performs no I/O, no logging, and does not call external services. It only reads an attribute and returns a formatted string.

## `src.ydata_profiling.model.alerts.SkewedAlert` · *class*

## Summary:
A typed Alert subclass that marks a variable as having a highly skewed distribution by setting alert_type to the AlertType.SKEWED value and carrying an optional skewness statistic.

## Description:
SkewedAlert is instantiated by profiling checks that detect strong skew in a column's value distribution. Typical callers are rule/check implementations inside the profiling engine which construct an alert when computed skewness passes a configured threshold.

This class exists to:
- Provide a specific alert object for skewness warnings so renderers and downstream consumers can identify and present skew-related findings consistently.
- Carry a small, structured payload (values) and metadata (column_name and fields) useful for formatting messages and report-friendly identifiers.

Note: AlertType is an enumeration defined elsewhere; this subclass assigns the Alert.alert_type attribute to AlertType.SKEWED to classify this alert.

Responsibility boundary:
- SkewedAlert does not compute skewness itself — it only stores the results supplied by a detector and provides a compact human-facing description via _get_description().
- It relies on its caller to populate values with an appropriate "skewness" entry when a numeric skewness value is available.

## State:
Instance attributes (inherited from Alert and set by this class on initialization):
- alert_type (AlertType)
  - Type: AlertType
  - Value for this subclass: AlertType.SKEWED
  - Invariant: Must remain AlertType.SKEWED for the lifetime of the instance.
- values (Dict)
  - Type: dict (or None as passed in)
  - Valid contents: ideally includes the key "skewness" mapping to a numeric value (e.g., float). Caller may pass None or a dict.
  - Note: the parent Alert class may normalize None to an empty dict; depending on that behavior, _get_description may attempt to read values["skewness"] and raise KeyError when the key is absent. Callers should therefore provide a dict containing "skewness" when intending to include the numeric value in descriptions.
- column_name (Optional[str])
  - Type: str or None
  - Purpose: human-identifying name of the column the alert targets; used in the description and by renderers for labeling.
- fields (Set[str])
  - Type: set of str
  - Value set by this subclass: {"skewness"}
  - Invariant: fields contains the string "skewness".
- _is_empty / is_empty flag (bool)
  - Type: bool
  - Purpose: forwarded to parent; may be used to mark placeholder/empty alerts (no internal logic in this class depends on it).

Class invariants:
- alert_type is AlertType.SKEWED.
- fields is a set containing "skewness".
- values should contain "skewness" when the caller expects the description to include the numeric skewness; otherwise, the description will omit the numeric suffix or may raise KeyError depending on parent-normalization of None.

## Lifecycle:
Creation:
- Constructor signature:
    SkewedAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required args: none mandatory; typical usage provides column_name and a values dict containing "skewness".
- Example creation patterns:
    - SkewedAlert(values={"skewness": 2.13}, column_name="income")
    - SkewedAlert(column_name="age")  # no numeric skewness provided

Usage:
- Typical flow:
    1. A skew-detection check computes skewness and decides an alert is warranted.
    2. The check creates SkewedAlert(values={"skewness": <float>}, column_name=<str>).
    3. Renderers or logging code call repr(alert) / str(alert) or otherwise invoke the Alert's presentation helpers (Alert.fmt(), Alert.anchor_id) which may call this class's _get_description().
- Method sequencing:
    - No strict sequencing required. _get_description() is safe to call at any time after instantiation provided values contains the expected key when present.
- Cleanup:
    - No explicit cleanup or close method; instances are garbage-collected like normal Python objects.

## Method Map:
graph TD
    A[Constructor: SkewedAlert.__init__] --> B[_get_description()]
    A --> C[inherited: alert_type (AlertType.SKEWED)]
    A --> D[inherited: fields = {"skewness"}]
    B -->|reads| E[values["skewness"]]
    B -->|reads| F[column_name]
    Note[Usage note] --> B
    Note --> D

(Above: _get_description() is the only method defined by this subclass; renderers or repr() may call it to produce a one-line textual description. The method reads column_name and, if values is present, values["skewness"].)

## Raises:
- KeyError
  - Trigger: _get_description attempts to access values["skewness"] but the values dict does not contain the "skewness" key.
  - Occurs when: caller provided a values dict missing the expected key, or when the parent Alert normalizes a None into an empty dict and this class's check for None is insufficient to avoid accessing the key.
- TypeError / ValueError (possible)
  - Trigger: formatting the skewness value may raise TypeError if values["skewness"] is a non-displayable object, or other type/format issues occur during string interpolation.
- No explicit exceptions are raised by __init__ itself under normal use; the above exceptions originate from _get_description when it is called.

## Example:
1) Typical creation and description with numeric skewness:
    alert = SkewedAlert(values={"skewness": 2.13}, column_name="income")
    # Human-facing description (via repr() or Alert presentation helpers) will be:
    # "[income] is highly skewed(γ1 = 2.13)"

2) Creation without skewness value (description will omit numeric value — but see Raises):
    alert = SkewedAlert(column_name="age")
    # If the parent normalizes values to {}, calling str(repr(alert)) may trigger KeyError
    # when _get_description tries to read values["skewness"]. To avoid this, prefer:
    alert = SkewedAlert(values=None, column_name="age")
    # and ensure the parent/renderer handles missing skewness keys gracefully.

3) Defensive pattern used by a check:
    skew = compute_skew(series)
    if abs(skew) > threshold:
        alert = SkewedAlert(values={"skewness": skew}, column_name=series.name)
        alerts_list.append(alert)

### `src.ydata_profiling.model.alerts.SkewedAlert.__init__` · *method*

## Summary:
Initialize a SkewedAlert instance by delegating to the base Alert constructor with the SKEWED category and the "skewness" field, setting initial values, column name, and emptiness flag on the object.

## Description:
This constructor creates a specialized Alert configured to represent a skewed-distribution issue for a column. It is called during the profiling pipeline when a skewness check determines that a variable's distribution is highly skewed and an alert object needs to be emitted for reporting or further processing. Typical callers are components that evaluate distributional statistics (e.g., a skewness-check routine in the variable analysis step) and construct alert objects to collect metadata for the final report.

This logic is encapsulated in its own constructor rather than inlined to:
- Provide a single, clear place to set the alert_type to SKEWED and the fields set to {"skewness"}.
- Keep alert creation uniform across different alert categories by leveraging the shared Alert initialization.
- Make it convenient to instantiate a ready-to-render alert with minimal repetition.

## Args:
    values (Optional[Dict]): Optional dictionary of alert-specific metadata. Expected keys (by convention) include:
        - "skewness": numeric value (float) describing the skewness statistic for the column.
        If omitted or None, the base Alert will assign an empty dict; see Constraints for the important implication.
        Default: None.
    column_name (Optional[str]): Name of the column/variable the alert refers to. May be None if not yet assigned.
        Default: None.
    is_empty (bool): Flag indicating whether the referenced series/variable was empty (no observed data).
        Default: False.

## Returns:
    None: This is an initializer; it returns None and mutates the instance state.

## Raises:
    None directly: The constructor itself performs no explicit checks and does not raise exceptions. However, note that downstream methods (for example, SkewedAlert._get_description) access values["skewness"] if values is not None; if values is missing the expected key this may raise a KeyError when those methods run.

## State Changes:
    Attributes READ:
        - None directly in this method implementation (it does not inspect existing instance attributes).
    Attributes WRITTEN (via base Alert.__init__):
        - self.fields: set to {"skewness"} (Set[str])
        - self.alert_type: set to AlertType.SKEWED
        - self.values: set to values if truthy, otherwise {} (dict)
        - self.column_name: set to column_name (Optional[str])
        - self._is_empty: set to is_empty (bool)

## Constraints:
    Preconditions:
        - No internal preconditions enforced by this constructor; callers should provide a values dict containing a "skewness" numeric entry if they expect descriptive methods to include the skewness value without errors.
        - column_name may be None, but many renderers and descriptions expect a non-empty column name for readable output.
    Postconditions:
        - After return, the instance will be a fully-initialized Alert with:
            * alert_type == AlertType.SKEWED
            * fields == {"skewness"}
            * values is a dict (empty {} if the caller passed None or a falsy dict)
            * column_name set to the provided argument (possibly None)
            * _is_empty set to the provided boolean
        - Because values becomes {} when falsy, code that later checks "if self.values is not None" will evaluate True (for {}) and may attempt to read values["skewness"]; therefore callers should either pass a dict containing "skewness" or downstream code should guard against missing keys.

## Side Effects:
    - No I/O or external service calls.
    - Mutates only the instance (self) by initializing the attributes listed above via the base class constructor.
    - No global state is modified.

### `src.ydata_profiling.model.alerts.SkewedAlert._get_description` · *method*

## Summary:
Return a deterministic, human-readable description for this alert that names the affected column and — if available — appends the measured skewness; the method performs no state modification.

## Description:
This private helper builds the textual message representing a "highly skewed" alert for use in alert rendering, serialization, or reporting. The message is constructed exactly as:
    "[{column_name}] is highly skewed"
and, when skewness information is present in self.values, the method appends the measurement with no extra space before the parenthesis, using the Unicode sequence \u03b31 to label the value, e.g.:
    "[age] is highly skewed(γ1 = 0.23)"

Known callers and invocation context:
    - Not shown in the provided snippet; conceptually this method is called by higher-level alert presentation logic (for example when converting the alert to a string, a dictionary field used in a report, or when rendering alerts in HTML/text output).
    - It is invoked during the alert/report generation stage of the profiling pipeline, when a user-facing description is required.

Why this is a separate method:
    - Centralizes message formatting so all presentation code obtains a consistent description.
    - Keeps presentation concerns separated from detection logic, simplifying testing and future localization/formatting changes.

## Args:
    None

## Returns:
    str: The constructed description.
        - If self.values is None:
            returns the exact string "[{column_name}] is highly skewed"
        - If self.values is not None:
            attempts to return "[{column_name}] is highly skewed(γ1 = {skewness})"
            where {skewness} is the value obtained by evaluating self.values['skewness'] and formatted using Python's default f-string conversion (i.e., str(value) or value.__format__('')).
        - Exact spacing and punctuation follow the implementation: there is no space between the end of the base sentence and the opening parenthesis.
        - Edge-case representations:
            * If skewness is None, the substring "(γ1 = None)" will appear.
            * If skewness is numpy.nan, it will appear as "nan".
            * If skewness is a non-scalar (e.g., an array-like), its string representation will be inserted.

## Raises:
    KeyError:
        - If self.values is not None but does not contain the key 'skewness', the subscription self.values['skewness'] will raise KeyError.
    TypeError:
        - If self.values is not None but is not subscriptable with a string key (for example, a numeric or object that does not implement __getitem__), attempting self.values['skewness'] may raise TypeError.
    AttributeError:
        - If the instance lacks self.column_name or self.values attributes, attribute access will raise AttributeError.
    Any exception raised during conversion/formatting of the skewness value (for example, if a custom object's __str__ raises) will propagate.

## State Changes:
    Attributes READ:
        - self.column_name
        - self.values
    Attributes WRITTEN:
        - None (the method does not modify the object's attributes or external state)

## Constraints:
    Preconditions:
        - self.column_name must be present and readable (commonly a str or convertible to str).
        - self.values must be either None or a mapping-like object expected to provide a 'skewness' entry when skewness is available.
    Postconditions:
        - The object state is unchanged.
        - A string describing the alert is returned deterministically based on the current values of self.column_name and self.values.

## Side Effects:
    - None. The method performs no I/O, network calls, logging, or external mutations; it only reads attributes and returns a formatted string.

## `src.ydata_profiling.model.alerts.TypeDateAlert` · *class*

## Summary:
Represents an alert that flags a column inferred as datetime/date-like values while being treated as categorical. Its purpose is to notify downstream consumers (renderers, reports) that the column likely should be converted with pandas.to_datetime before further type-dependent analyses.

## Description:
TypeDateAlert is a thin Alert subclass created whenever a profiling check determines that all observed values in a column are date/time-like but the column has been treated as categorical (string/object). Typical callers are the type-detection or rule-checking components in the profiling pipeline that examine a column's sample and emit alerts when a mismatch between inferred semantic type and declared/observed categorical type is detected.

Motivation and responsibility boundary:
- Encapsulates the specific alert category AlertType.TYPE_DATE together with optional metadata (values dict) and the target column name.
- Provides a single place to format a human-readable description for this situation; it does not perform detection logic itself nor does it perform any I/O.

Known callers/factories:
- Type-detection or rule checks in the profiling pipeline that inspect column samples and construct Alert instances for discovered conditions.
- Renderers or report generators that read alerts and present them in an HTML/text report.

## State:
This class inherits state from Alert and does not add new instance attributes beyond those managed by the superclass. Relevant attributes a caller can rely on:

- alert_type (AlertType)
  - Type: AlertType (Enum)
  - Value for this class: always AlertType.TYPE_DATE (set by the constructor).
  - Invariant: must be a member of AlertType.

- values (Dict[str, Any])
  - Type: dict
  - Default: {} when None is passed to the constructor.
  - Purpose: optional structured metadata about the alert. No keys are required by TypeDateAlert itself; downstream formatters may ignore or use entries if present.

- column_name (Optional[str])
  - Type: Optional[str]
  - Default: None
  - Purpose: the column/variable name this alert targets.
  - Notes/edge cases: If None, the description produced by _get_description will include "None" inside the brackets because the method formats the column_name via f-string without additional guarding. If column_name is not a str (e.g., an object with a custom __str__), its string representation will be used.

- fields (Set[str])
  - Type: set
  - Default: empty set if not provided by the Alert superclass initialization.
  - Purpose: general-purpose related-fields set (not used by this alert type but present on the superclass).

- _is_empty (bool)
  - Type: bool
  - Default: False
  - Purpose: marker used by producers to indicate an empty/placeholder alert (handled elsewhere).

- _anchor_id (Optional[str])
  - Type: Optional[str]
  - Computation: lazily computed by Alert.anchor_id when first accessed (derived from hash(column_name)).
  - Invariant: once computed it remains constant for the instance.

Class invariants (applying to every TypeDateAlert instance):
- alert_type equals AlertType.TYPE_DATE.
- values is a dict (never None after initialization).
- fields is a set (never None after initialization).
- anchor_id, once requested, is cached and stable.

## Lifecycle:
Creation:
- Constructor signature (semantic):
    TypeDateAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments: none (all parameters have defaults). Typical instantiation passes column_name and optionally values.
- Behavior: Calls the Alert superclass constructor with alert_type set to AlertType.TYPE_DATE and forwards values, column_name and is_empty.

Usage:
- Primary read/member accessors:
    - Use repr(alert) or str-like presentation helpers inherited from Alert which call alert._get_description() to produce a short human-readable description.
    - Consumers (renderers) may read alert.values for additional context and alert.column_name for display or linking.
    - Access alert.anchor_id to obtain a stable identifier for linking in reports (note: accessing anchor_id may attempt to hash column_name and could raise TypeError for unhashable column_name values).

- Typical sequence:
    1. A detector constructs TypeDateAlert(...) with the offending column_name.
    2. The alert is collected into a list/set of alerts for the report.
    3. A renderer calls repr(alert) or alert._get_description() to obtain the human-facing message.
    4. Optionally, anchor_id or formatted label (via inherited fmt() for some alert types) are accessed by renderers.

Destruction:
- No explicit cleanup required. The object is managed by Python GC. No context-manager or close semantics.

## Method Map:
graph TD
    A[Constructor: TypeDateAlert.__init__] --> B[Inherited properties: alert_type, values, column_name, fields]
    B --> C[Renderer / repr() calls _get_description()]
    C --> D[Return descriptive string: "[{column_name}] only contains datetime values, but is categorical. Consider applying `pd.to_datetime()`"]
    B --> E[anchor_id accessed (Alert.anchor_id) -> may hash(column_name)]
    E --> F[possible TypeError if column_name unhashable]

## Methods (behavioral summary):
- __init__(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
  - Effect: constructs an Alert with alert_type fixed to AlertType.TYPE_DATE and stores forwarded parameters on the Alert base class.
  - Side effects: none.

- _get_description() -> str
  - Returns a short human-readable description string in the exact format:
    "[{column_name}] only contains datetime values, but is categorical. Consider applying `pd.to_datetime()`"
  - Notes:
    - This method is used by Alert.__repr__ / presentation code to display the alert.
    - If column_name is None the string "[None] ..." will be produced.
    - There is no localization or translation applied here — the literal English sentence is returned.

## Raises:
TypeDateAlert.__init__:
- The constructor does not explicitly raise exceptions itself. However, errors may arise due to misuse or via inherited behaviors:
  - TypeError:
    - Trigger conditions:
      - Passing an unhashable object for column_name is safe at construction time but will raise TypeError if a caller later accesses alert.anchor_id (the anchor computation hashes column_name).
      - Supplying non-dict mutable types where a dict is expected may cause later methods that assume dict operations to fail.
  - No KeyError/ValueError is raised by TypeDateAlert.__init__ itself.

_get_description:
- No explicit exceptions raised. Potential exceptions are limited to those raised while converting column_name to string (rare, only if __str__ raises).

Defensive guidance:
- Prefer passing a simple str for column_name.
- If using values, adhere to dict semantics; this class does not depend on any particular keys in values.

## Example:
- Create a simple TypeDateAlert for a column named "start_date" and obtain its description and stable anchor id:
    alert = TypeDateAlert(column_name="start_date")
    description = alert._get_description()
    # description -> "[start_date] only contains datetime values, but is categorical. Consider applying `pd.to_datetime()`"
    # Access anchor id if needed (may raise TypeError if column_name is unhashable):
    anchor = alert.anchor_id

- Typical usage in a detector:
    1. Detector discovers that all values in column "signup" parse as dates.
    2. Detector constructs TypeDateAlert(column_name="signup").
    3. Detector appends the alert to the collection consumed by report generators.
    4. Report generator calls repr(alert) or alert._get_description() to include the message in the output.

### `src.ydata_profiling.model.alerts.TypeDateAlert.__init__` · *method*

## Summary:
Initializes a TypeDateAlert instance by setting the alert category to TYPE_DATE and delegating storage of provided metadata (values, column_name, is_empty) to the base Alert initializer, thereby updating the alert object's state.

## Description:
This constructor is called when creating an alert that marks a variable as "date-like" (i.e., values are date/datetime) while being treated as categorical. Typical callers are parts of the profiling pipeline that detect variable types or inconsistencies during column analysis (for example, a variable type detection or variable-level checks that decide an alert should be emitted for a column). It is invoked at the time an alert object is created — during alert generation in the profiling lifecycle.

This logic is a small, focused initializer rather than being inlined because:
- It fixes the alert_type to AlertType.TYPE_DATE for this specific alert subclass.
- It leverages the shared base-class initialization for common alert fields (fields, values, column_name, is_empty), avoiding code duplication across multiple specific alert types.
- It keeps subclass responsibility minimal: subclass declares its category and may override descriptive behavior (e.g., _get_description).

## Args:
    values (Optional[Dict]): Optional dictionary with additional metadata for the alert. Default: None. If None, it will be normalized to an empty dict by the base class initializer.
    column_name (Optional[str]): Optional name of the column the alert pertains to. Default: None.
    is_empty (bool): Whether the column is considered empty. Default: False.

## Returns:
    None: Constructors do not return a value. After return, the instance has been initialized (see Postconditions).

## Raises:
    None: This __init__ implementation does not raise any exceptions. (It only forwards arguments to the base Alert.__init__, which also does not raise for the given inputs.)

## State Changes:
Attributes READ:
    - None (the constructor itself does not read any existing self.<attr> fields).

Attributes WRITTEN (via base class initializer):
    - self.fields: set to the provided fields argument or an empty set (fields is not accepted on this subclass, so it becomes an empty set).
    - self.alert_type: set to AlertType.TYPE_DATE.
    - self.values: set to the provided values or an empty dict if values is None.
    - self.column_name: set to the provided column_name (may be None).
    - self._is_empty: set to the provided is_empty boolean.

## Constraints:
Preconditions:
    - values, if provided, should be a mapping (dict-like). No further validation is performed here.
    - column_name, if provided, should be a string identifying a column.
    - Callers should not assume that column_name is non-None; many alert consumers tolerate None.

Postconditions:
    - self.alert_type is guaranteed to be AlertType.TYPE_DATE.
    - self.values is guaranteed to be a dict (empty dict if caller passed None).
    - self.fields is guaranteed to be a set (empty set when no fields argument supplied).
    - self.column_name equals the provided column_name (or None).
    - self._is_empty equals the provided is_empty boolean.

## Side Effects:
    - Mutates the instance (self) by setting the attributes listed above.
    - No I/O is performed.
    - No external services are invoked.
    - No global state is modified.

## Implementation Notes for Reimplementation:
    - The constructor simply delegates to the base Alert.__init__ with alert_type fixed to AlertType.TYPE_DATE and forwards values, column_name, and is_empty.
    - Ensure the base Alert initializer normalizes values to {} when None and fields to set() when not provided to match expected postconditions.

### `src.ydata_profiling.model.alerts.TypeDateAlert._get_description` · *method*

## Summary:
Returns a human-readable description string stating that the target column contains only datetime values but was treated as categorical, and suggests converting it using pandas to_datetime. Does not modify the object's state.

## Description:
- Known callers and context:
    - Called by Alert.__repr__ (repr(alert)) to produce a textual representation of the alert for logging or simple textual output.
    - Invoked by reporting/rendering code paths or interactive debugging that need a short explanation of this alert type.
    - This method is used at the reporting stage of the profiling pipeline after a detection rule created a TypeDateAlert for a column that appears to contain datetime values but was classified as categorical.
- Rationale for separate method:
    - The message is a per-alert-type textual description that is small and presentation-focused. Keeping it as a dedicated method allows each Alert subclass to provide a tailored human-facing message (and makes it easy to override, test, or internationalize), instead of inlining messages in repr or the detection logic.

## Args:
    None.

## Returns:
    str: A single-line formatted message describing the issue for the alert's column. The exact format produced by the implementation is:
        "[{column_name}] only contains datetime values, but is categorical. Consider applying `pd.to_datetime()`"
    - Possible return values / edge cases:
        - If self.column_name is None, the returned string will include "None" in the bracket (i.e., "[None] ...").
        - If column_name is any object, its string representation (via standard formatting) is embedded in the brackets.

## Raises:
    - The method does not explicitly raise any exceptions.
    - A runtime exception may propagate only if converting the column_name to a string/format (its __format__/__str__) raises (for example, if column_name is an object whose formatting raises TypeError). Such exceptions are not raised by this method itself but will propagate from Python's string formatting machinery.

## State Changes:
    Attributes READ:
        - self.column_name
    Attributes WRITTEN:
        - None (no attributes on self are modified)

## Constraints:
    Preconditions:
        - None required by the method; self.column_name may be None or any object with a string representation.
    Postconditions:
        - The method returns a str describing the alert and leaves the object's attributes unchanged.

## Side Effects:
    - None. This method performs no I/O, no mutation of external objects, and no calls to external services. It purely formats and returns a string.

## `src.ydata_profiling.model.alerts.UniformAlert` · *class*

## Summary:
Represents an alert indicating that a specific column/variable is uniformly distributed. It is a lightweight, typed container that marks the alert category as AlertType.UNIFORM and provides a concise textual description for presentation.

## Description:
UniformAlert is instantiated by the profiling checks/rules when a detector determines a column's values appear uniformly distributed (for example, near-equal counts across distinct values or a flat numeric distribution). Typical callers are the profile rule implementations and alert aggregators in the profiling pipeline which create Alert objects for conditions they detect.

This class exists as a distinct abstraction because:
- It encodes the canonical alert category (AlertType.UNIFORM) so downstream renderers and consumers can filter, group, or style uniformity alerts consistently.
- It provides a focused textual description tailored to the uniformity condition via _get_description(), delegating all storage and presentation helpers to the shared Alert base class.

Responsibility boundary:
- Stores the metadata (values, column_name, is_empty) and offers a descriptive string for reporting.
- Delegates presentation helpers (alert_type_name, anchor_id, fmt()) and other utilities to the Alert base class.
- It does not perform statistical detection nor perform any I/O.

## State:
(All attributes are inherited from Alert unless noted; UniformAlert does not introduce new persistent attributes.)

- alert_type (AlertType)
  - Value for instances of this class: AlertType.UNIFORM (set by the constructor).
  - Invariant: Must remain AlertType.UNIFORM for the lifetime of the instance.

- values (Dict)
  - Type: dict
  - Meaning: Arbitrary mapping for alert-specific metadata. Commonly empty or may contain diagnostic fields (e.g., sample statistics).
  - Default: If None is passed to the constructor, the Alert base class normalizes this to an empty dict.
  - Constraints: Callers should avoid relying on specific keys unless they are documented by the detector that created the alert.

- column_name (Optional[str])
  - Type: str or None
  - Meaning: The name of the column the alert pertains to. May be None for dataset-level alerts.
  - Default: None (if not provided).
  - Constraint: Prefer passing simple string names to avoid hashing/stringification issues in anchor generation.

- fields (Set[str]) [inherited behavior]
  - Type: set of strings
  - Meaning: Related column names (if applicable). For UniformAlert this is normally empty unless provided by the detector.
  - Default: normalized to an empty set by the Alert base class.

- _is_empty (bool)
  - Type: bool
  - Meaning: Internal flag indicating an empty/placeholder alert. Passed through from constructor is_empty parameter.

- _anchor_id (Optional[str])
  - Type: Optional[str]
  - Meaning: Lazily computed stable identifier (derived from hashing column_name) used by renderers.
  - Invariant: Once computed, remains constant.

Class invariants:
- values is always a dict (never None after construction).
- fields is always a set (never None after construction).
- alert_type is the fixed enum member AlertType.UNIFORM for this class.

## Lifecycle:
Creation:
- Constructor signature (relevant parameters):
    UniformAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments: none (all parameters are optional). The constructor sets the alert_type automatically to AlertType.UNIFORM.
- Typical instantiation:
    uniform_alert = UniformAlert(column_name="zipcode")

Usage:
- Typical sequence:
    1. Detector/Check creates the UniformAlert instance, optionally populating values with diagnostic info (counts, sample, statistic).
    2. The profiling pipeline collects the instance in an alerts list.
    3. Renderers or consumers call:
        - uniform_alert.alert_type_name  (inherited) to get a human-friendly label
        - uniform_alert.fmt()           (inherited) for formatted presentation
        - uniform_alert.anchor_id       (inherited) for stable linking keys
        - repr(uniform_alert) which delegates to _get_description()
- There is no required invocation order for these accessors. anchor_id will be computed on first access and cached.

Destruction:
- No explicit resource cleanup required. Instances participate in normal Python GC. There is no context manager behavior or close() method.

## Method Map:
graph TD
    A[UniformAlert.__init__] --> B[Alert.__init__]
    B --> C[alert.values (dict)]
    B --> D[alert.fields (set)]
    B --> E[alert._is_empty (bool)]
    A --> F[_get_description()]
    F --> G[repr(instance)]
    C -->|read by| H[fmt() inherited]
    D -->|may be read by| H
    E -->|flag used externally| I[renderers/filters]
    J[anchor_id (lazy)] -->|computed on access| K[hash(column_name)]

(UniformAlert._get_description is a simple override used by repr() / description helpers. Inherited methods such as fmt() and anchor_id are provided by Alert and are not overridden here.)

## Raises:
- __init__: UniformAlert's constructor does not raise explicit exceptions; it simply forwards parameters to Alert.__init__ with alert_type set to AlertType.UNIFORM.
- Potential runtime issues (inherited from Alert and caused by caller-supplied inputs):
    - TypeError:
        - Triggered if column_name is unhashable and then anchor_id is accessed (hashing fails).
        - Triggered if values or fields are of unexpected types and later code assumes different types.
    - KeyError:
        - Triggered if external callers call fmt() (or other presentation helpers) that expect specific keys in values but those keys are absent.
    - Any exceptions raised are not specific to UniformAlert but originate from the Alert base class methods acting on the provided inputs.

## Example:
- Create a UniformAlert for a column and use common inherited helpers:

    # Creation
    ua = UniformAlert(column_name="category")
    # Presentation helpers (inherited)
    print(ua.alert_type_name)   # e.g., "Uniform" (derived from AlertType.UNIFORM)
    print(ua.fmt())             # formatted label; behavior per Alert.fmt()
    print(ua.anchor_id)         # lazily computed stable id
    # Description (uses UniformAlert._get_description)
    print(repr(ua))             # -> "[category] is uniformly distributed"

- With diagnostic values populated by a detector:
    ua2 = UniformAlert(values={"sample_counts": {"A": 10, "B": 9}}, column_name="choice")
    # values can be used by renderers or display helpers if desired
    print(ua2.values["sample_counts"])

### `src.ydata_profiling.model.alerts.UniformAlert.__init__` · *method*

## Summary:
Initializes a UniformAlert instance by configuring the base Alert state for a "uniform distribution" condition — sets the alert category, stores provided contextual values, the target column name, and emptiness flag on the object.

## Description:
This constructor delegates initialization to the Alert base class while enforcing the alert_type to AlertType.UNIFORM. It is invoked when the profiling logic detects that a variable's observed values show a nearly-uniform distribution and an alert object should be created for reporting or downstream filtering.

Known callers / typical context:
- Alert-producing checks in the profiling pipeline that detect uniform distributions for a variable (e.g., a rule or detector that inspects value counts or distribution metrics and decides to emit a Uniform alert).
- Any alert factory or summarizer that constructs alert instances for inclusion in the final profiling report.

Why this is a separate method:
- The constructor exists to encapsulate the specialization of the generic Alert base class for the specific UNIFORM category. Keeping this small constructor means callers only need to supply the context (values, column_name, is_empty) and the subclass guarantees the correct typed category is applied. This prevents callers from having to set the alert_type manually and centralizes the uniform-alert semantics.

## Args:
    values (Optional[Dict]): Contextual key/value information related to the alert.
        - Typical contents: diagnostic details such as example values, counts, or metric summaries.
        - If None, the Alert base class normalizes this to an empty dict.
        - Default: None
    column_name (Optional[str]): The name of the column/variable the alert is associated with.
        - May be None if the alert is not column-specific.
        - Default: None
    is_empty (bool): Flag indicating whether the underlying series/column is empty.
        - Stored on the instance as a boolean sentinel (Alert stores it on _is_empty).
        - Default: False

## Returns:
    None
    - As a constructor, it does not return a value. The effect is observed via mutations to the instance attributes documented below.

## Raises:
    None explicitly.
    - This constructor does not raise exceptions itself. Any exceptions raised by callers or by the Alert base class initializer (not present in the local implementation) would propagate, but the provided Alert.__init__ does not raise.

## State Changes:
Attributes READ:
    - None (the constructor does not read instance attributes before delegation).

Attributes WRITTEN:
    - self.fields: set to the provided fields argument (in this constructor fields is not passed, so base class initializes to an empty set).
    - self.alert_type: set to AlertType.UNIFORM.
    - self.values: set to the provided values argument, or to an empty dict if values is None.
    - self.column_name: set to the provided column_name argument.
    - self._is_empty: set to the provided is_empty boolean.

Other observable state:
    - self._anchor_id remains unchanged (initialized lazily in base class property; this constructor does not set it).

## Constraints:
Preconditions:
    - None strict: values may be None or a dict-like mapping; column_name may be None or a string; is_empty must be a boolean (callers should pass a bool).
    - The AlertType enum must contain the UNIFORM member (present in the codebase).

Postconditions:
    - After execution, instance.alert_type is AlertType.UNIFORM.
    - instance.values is a dict (empty dict if caller passed None).
    - instance.column_name equals the provided column_name (possibly None).
    - instance._is_empty equals the provided is_empty boolean.
    - instance.fields is a set (will be an empty set when not provided).

## Side Effects:
    - No I/O, network, or filesystem side effects.
    - Only mutates the new instance's attributes (see Attributes WRITTEN). No global state is modified.

### `src.ydata_profiling.model.alerts.UniformAlert._get_description` · *method*

## Summary:
Return a concise, human-readable description string asserting that the alert's associated column is uniformly distributed; does not modify object state.

## Description:
Known callers and lifecycle:
- Alert.__repr__: The base-class representation calls this method to generate the text shown when an alert is printed or rendered in logs and reports.
- Profiling checks / rule implementations: When a detector discovers that a column's values appear uniformly distributed, it will create a UniformAlert instance and consumers (renderers, loggers, tests) may call this method to obtain a human-friendly description.
- Typical invocation occurs during the alert creation/formatting stage of the profiling pipeline (after detection and when preparing output for a report or debugging).

Why this logic is a separate method:
- Encapsulates presentation logic for the Uniform alert type so that repr(), renderers, and any other consumers can reuse a single canonical description.
- Allows subclasses to override the description behavior without altering detection logic or the Alert base class.

## Args:
- None.

## Returns:
- str: A single-line description in the exact format:
    "[{column_name}] is uniformly distributed"
  - If column_name is a string "age", the method returns "[age] is uniformly distributed".
  - If column_name is None, the method returns "[None] is uniformly distributed" (string conversion of None is used).
  - If column_name is another object, its formatted string (via __format__/__str__) is used inside the brackets.
  - No localization, pluralization, or additional metadata (e.g., p-values or sample sizes) is included.

## Raises:
- Any exception raised by formatting self.column_name:
    - Typical source: column_name.__format__ or column_name.__str__ raising an exception (for example, if column_name is a custom object whose __str__ raises).
    - Effect: the exception will propagate; this method performs no defensive try/except.
- This method itself does not raise ValueError, KeyError, or other domain-specific exceptions.

## State Changes:
- Attributes READ:
    - self.column_name
- Attributes WRITTEN:
    - None (no mutation; method is pure w.r.t. the Alert instance)

## Constraints:
- Preconditions:
    - The instance must have a column_name attribute (the Alert base class guarantees this attribute exists after normal construction). Prefer column_name to be a str or a value safely convertible to str.
- Postconditions:
    - The returned string reflects the value of self.column_name at call time.
    - The Alert object remains unchanged (no attributes added, removed, or mutated).

## Side Effects:
- None external: the method performs no I/O, network calls, or global state changes.
- The only observable effect beyond returning a string is the invocation of the column_name object's formatting/str machinery; any side effects caused by column_name.__str__/__format__ are not introduced by this method.

## Examples (illustrative, not executable code):
- For a UniformAlert created with column_name = "age", repr(alert) -> "[age] is uniformly distributed"
- For a UniformAlert with column_name = None, alert._get_description() -> "[None] is uniformly distributed"
- Consumers typically do not call _get_description() directly; they call repr(alert) or alert formatting helpers which in turn invoke this method.

## `src.ydata_profiling.model.alerts.UniqueAlert` · *class*

## Summary:
A specialized Alert subclass that represents the condition "column has (mostly) unique values". It tags the alert with AlertType.UNIQUE and standardizes the metric keys that uniqueness checks populate.

## Description:
UniqueAlert is created by uniqueness-checking logic in the profiling pipeline when a variable/column exhibits very high uniqueness (for example: nearly all observed values are distinct). Typical callers are the rule/check implementations that compute distinct-count statistics and instantiate this alert to be collected and rendered in reports.

Responsibility:
- Set the canonical alert_type to AlertType.UNIQUE.
- Declare the standardized metric keys (fields) that uniqueness checks should populate: "n_distinct", "p_distinct", "n_unique", "p_unique".
- Provide a concise description string used by Alert.__repr__ via _get_description.

Boundary:
- UniqueAlert only stores metadata and a description; it does not perform metric computation, formatting beyond the description, or any I/O. Metric computation and rendering are handled by other modules.

## State:
(All instance attributes are created/initialized by calling the Alert base class constructor; UniqueAlert does not add new attributes beyond those in Alert. Types and defaults reflect UniqueAlert's constructor and inherited behavior.)

- values: Dict
  - Constructor parameter: values: Optional[Dict] = None
  - Effective value: The Alert base class converts None to an empty dict ({}) — UniqueAlert relies on that behavior.
  - Purpose: Hold numeric metrics about uniqueness.
  - Conventional/expected keys (by profiling checks and renderers):
    - "n_distinct" (int): number of distinct observed values.
    - "p_distinct" (float): proportion of distinct values (0.0 - 1.0).
    - "n_unique" (int): count of values that occur exactly once.
    - "p_unique" (float): proportion of unique-only values (0.0 - 1.0).
  - Constraints: UniqueAlert does not enforce presence or types for these keys; consumers should validate before use.

- column_name: Optional[str]
  - Constructor parameter: column_name: Optional[str] = None
  - Purpose: Name of the column this alert targets.
  - Notes: If column_name is None, the textual description will include the string "None" (see _get_description). Prefer passing a simple string; non-hashable objects may cause later errors when computing anchor_id in the base class.

- fields: Set[str]
  - Set by UniqueAlert via its super() call to the literal set {"n_distinct", "p_distinct", "n_unique", "p_unique"}.
  - Purpose: Document which keys in values are relevant for this alert. The Alert base class ensures fields is stored as a set on the instance.

- alert_type: AlertType
  - Value: AlertType.UNIQUE (set in the super() call).
  - Invariant: Instances of UniqueAlert always carry AlertType.UNIQUE.

- _is_empty: bool
  - Constructor parameter: is_empty: bool = False
  - Purpose: Internal flag passed to the Alert base class and stored as-is.

- _anchor_id (inherited, optional)
  - Computed lazily by Alert.anchor_id property when external consumers access it; unchanged thereafter.

Class invariants:
- alert_type == AlertType.UNIQUE.
- fields is a set containing exactly "n_distinct", "p_distinct", "n_unique", "p_unique".
- values is a dict (empty dict if None was passed at construction as per Alert behavior).
- anchor_id, once computed by the base class, remains stable.

## Lifecycle:
Creation:
- Constructor signature (exact):
    UniqueAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- How it constructs:
    - Calls the Alert base class constructor with:
        alert_type=AlertType.UNIQUE,
        values=values,
        column_name=column_name,
        fields={"n_distinct", "p_distinct", "n_unique", "p_unique"},
        is_empty=is_empty
- Required arguments: none; all parameters are optional. Typical instantiation pattern from a uniqueness check:
    UniqueAlert(values={"n_distinct": 120, "p_distinct": 0.98, "n_unique": 118, "p_unique": 0.96}, column_name="id")

Usage:
- No UniqueAlert-specific public methods beyond inherited Alert functionality.
- Typical operations by consumers:
    - repr(alert) -> uses Alert.__repr__ which calls UniqueAlert._get_description to produce a short text description.
    - alert.values -> inspect metric keys and values (validate keys before arithmetic).
    - alert.fields -> indicates which metric keys are relevant for this alert type.
    - alert.alert_type -> equals AlertType.UNIQUE (used for filtering/dispatch).
    - alert.anchor_id -> inherited lazy identifier (may raise TypeError if column_name is not hashable).
    - alert.fmt() -> inherited formatting helpers; UniqueAlert does not override fmt behavior.

Order / sequencing:
- No required order. Consumers may inspect values, call repr(), or access anchor_id in any sequence; anchor_id is computed lazily on first access.

Destruction:
- No cleanup required. Instances are ordinary Python objects subject to garbage collection.

## Method Map:
graph TD
    Init[UniqueAlert.__init__(values, column_name, is_empty)]
    Init -->|calls| Super[Alert.__init__(alert_type=AlertType.UNIQUE, values, column_name, fields={...}, is_empty)]
    Super --> Instance[Instance created with attributes: alert_type, values(dict), column_name, fields(set), _is_empty]
    Instance -->|repr() calls| Desc[UniqueAlert._get_description() -> string]
    Instance -->|consumer may call| Anchor[Alert.anchor_id (lazy; hashes column_name)]
    Instance -->|consumer may call| Fmt[Alert.fmt() (inherited)]

(Here fields={...} denotes the literal set {"n_distinct","p_distinct","n_unique","p_unique"} passed by UniqueAlert.)

## Raises:
UniqueAlert.__init__:
- Direct: None. The constructor itself does not raise exceptions under normal usage.

Inherited / indirect exceptions to be aware of (visible to callers):
- TypeError
  - When: Accessing alert.anchor_id if column_name is non-hashable (e.g., list); hashing in the base class will raise TypeError.
  - When: Consumer code operates on values keys with unexpected types (for example, joining non-string iterable elements) — these originate in consumers, not UniqueAlert itself.
- KeyError
  - When: Consumer code expects metric keys (e.g., alert.values["n_distinct"]) but those keys were not provided by the check that created the alert.
- ValueError or TypeError
  - When: Numeric operations on values entries fail because the values are of an incompatible type.

Notes:
- These are not thrown by UniqueAlert.__init__; they are runtime issues that can arise later due to malformed constructor arguments or consumer expectations. UniqueAlert deliberately defers strict validation and relies on callers to provide correctly-typed metric data.

## _get_description (behavior):
- Implementation returns the exact string produced by:
    f"[{self.column_name}] has unique values"
- Examples:
    - column_name = "age"  -> "[age] has unique values"
    - column_name = None   -> "[None] has unique values"
    - column_name = ""     -> "[] has unique values"
    - column_name = obj    -> uses str(obj) inside brackets (if obj.__str__ raises, that exception propagates)

## Example:
1) Typical creation and use:
    alert = UniqueAlert(
        values={"n_distinct": 1000, "p_distinct": 0.999, "n_unique": 995, "p_unique": 0.995},
        column_name="user_id"
    )
    print(alert.alert_type is AlertType.UNIQUE)  # True
    print(repr(alert))                            # "[user_id] has unique values"
    print(alert.values["p_distinct"])             # 0.999

2) Example when column_name is None:
    alert = UniqueAlert(values={"n_distinct": 10}, column_name=None)
    print(repr(alert))  # -> "[None] has unique values"

3) Defensive consumer pattern:
    # Verify expected keys before using them
    expected = {"n_distinct", "p_distinct", "n_unique", "p_unique"}
    if expected.issubset(set(alert.values.keys())):
        nd = int(alert.values["n_distinct"])
        pd = float(alert.values["p_distinct"])
        # proceed with safe usage

### `src.ydata_profiling.model.alerts.UniqueAlert.__init__` · *method*

## Summary:
Configure a UniqueAlert instance as an Alert with the UNIQUE category and the canonical set of uniqueness metric fields; this sets the alert type and stores the provided metadata on the instance.

## Description:
Purpose of this constructor:
- Encapsulates the fixed initialization for alerts that represent high uniqueness in a column. It delegates common initialization to the Alert base class while supplying the specific AlertType (UNIQUE) and the canonical metric field names for uniqueness checks.
- Keeping this as a subclass constructor centralizes the identity and expected fields for UNIQUE alerts so callers need only provide column-specific metadata.

Why this is a separate constructor:
- The base Alert class implements generic storage for alert metadata; the UniqueAlert constructor supplies the specific alert category and the set of fields relevant to uniqueness, avoiding repetition at call sites.

## Args:
    values (Optional[Dict]): Optional dictionary holding uniqueness-related metric values. If None, the base class will store an empty dict. Typical keys (by convention): "n_distinct", "p_distinct", "n_unique", "p_unique".
    column_name (Optional[str]): The name of the column that the alert refers to. May be None.
    is_empty (bool): Flag indicating whether the column is considered empty. Default False.

## Returns:
    None

## Raises:
    None. The constructor does not raise exceptions. (Any type errors from passing inappropriate types would arise from caller code or later usage, not from this constructor itself.)

## State Changes:
    Attributes READ:
        - None (the constructor does not read pre-existing instance attributes)
    Attributes WRITTEN:
        - self.fields: set to {"n_distinct", "p_distinct", "n_unique", "p_unique"} (the set provided to the base class)
        - self.alert_type: set to the AlertType enum member named "UNIQUE"
        - self.values: set to the provided values dict, or to {} when values is None (per base-class behavior: values or {})
        - self.column_name: set to the provided column_name
        - self._is_empty: set to the provided is_empty boolean

Notes:
- The provided values dict is stored by reference (no defensive copy). Mutating that dict after construction will affect self.values.

## Constraints:
    Preconditions:
        - No strict runtime checks; callers should pass values that conform to their expected types: values: Optional[Dict], column_name: Optional[str], is_empty: bool.
    Postconditions:
        - The instance represents a UNIQUE alert:
            * self.alert_type.name == "UNIQUE"
            * self.fields contains the four uniqueness metric names {"n_distinct", "p_distinct", "n_unique", "p_unique"}
            * self.values is a dict (empty if None was passed)
            * self.column_name equals the provided column_name (may be None)
            * self._is_empty equals the provided is_empty flag

## Side Effects:
    - No I/O or external service calls.
    - Mutates only the newly constructed instance and stores a reference to the passed values dict (no copies performed).

### `src.ydata_profiling.model.alerts.UniqueAlert._get_description` · *method*

## Summary:
Return a short, human-readable description stating that the alert's target column contains unique values.

## Description:
This method produces the textual description for a UniqueAlert instance. It is invoked by the Alert representation machinery: repr(alert) calls this method (Alert.__repr__ delegates to the subclass _get_description). The method exists as an override point so each Alert subclass can provide a concise, alert-specific message used when the alert is rendered, logged, or inspected.

Known callers and lifecycle context:
- Alert.__repr__ -> _get_description(): called when an alert instance is converted to its string representation (for example, via repr(alert) or when formatting alerts for display).

Why this is a separate method:
- Allows UniqueAlert to provide a customized description without changing Alert's generic behavior.
- Keeps representation logic localized to subclasses so renderers/consumers can call a uniform entry point (repr or the method) to obtain a message.

## Args:
This is an instance method and takes no explicit parameters beyond self.

- self: UniqueAlert
    - Expected attribute: self.column_name (Optional[str] or any object with a string representation)

## Returns:
- str: Message in the exact format "[<column_name>] has unique values".
    - Examples:
        - If column_name == "age": "[age] has unique values"
        - If column_name is None: "[None] has unique values"
        - If column_name == "": "[] has unique values"
        - If column_name is an object with a custom __str__, that string is used inside the brackets.

## Raises:
- The method does not explicitly raise exceptions.
- Indirect exceptions:
    - Any exception raised by converting self.column_name to a string (e.g., if column_name.__str__ raises) will propagate.

## State Changes:
- Attributes READ:
    - self.column_name

- Attributes WRITTEN:
    - None. The method does not modify the UniqueAlert instance.

## Constraints:
- Preconditions:
    - The instance must be an initialized UniqueAlert (in particular, column_name may be None or any object).
    - No other preconditions; the method does not require values or fields to be set.

- Postconditions:
    - Returns the description string as specified.
    - The UniqueAlert instance remains unchanged.

## Side Effects:
- None. No I/O, no external service calls, and no mutation of objects outside self.

## `src.ydata_profiling.model.alerts.UnsupportedAlert` · *class*

## Summary:
A small Alert subclass used to indicate a column has an unsupported data type for profiling. Its constructor supplies the UNSUPPORTED enum member (AlertType.UNSUPPORTED) to the parent Alert and it exposes a short human-readable description for reporting.

## Description:
UnsupportedAlert is instantiated by detector functions or the profiling pipeline when a column or variable cannot be profiled because its dtype or stored values are not supported (for example, custom Python objects in a Series). AlertType is an enumeration of alert categories used across the profiler; UnsupportedAlert uses the UNSUPPORTED member of that enum when constructing the underlying Alert.

Typical callers:
- dtype/validation checks that detect unsupported types
- alert aggregators that collect Alert objects for report rendering

This class exists to:
- Record the UNSUPPORTED alert category on an Alert instance.
- Carry optional context in values and the target column_name for renderers.
- Provide a concise description via _get_description() consumed by repr() and report templates.

Responsibility boundary:
- Store metadata and present a description. It does not perform detection, conversion, or report serialization.

## State:
Inherited attributes from Alert (how UnsupportedAlert initializes/uses them):
- alert_type (AlertType)
  - Type: AlertType enum member
  - How set: The constructor passes AlertType.UNSUPPORTED to the parent Alert, so the stored alert_type will be that member.
- values (Dict)
  - Type: Dict
  - Default normalization: parent Alert converts None to an empty dict.
  - Purpose: Free-form context (e.g., {"detected_dtype": "object"}). UnsupportedAlert does not require any specific keys.
- column_name (Optional[str])
  - Type: Optional[str]
  - Default: None
  - Purpose: Target column name; used by _get_description(). If None, the string "None" will appear in the description unless callers supply a value.
- _is_empty (bool)
  - Type: bool
  - Default: False (from is_empty parameter)
  - Purpose: Marker flag; UnsupportedAlert itself does not change behavior based on it.
- fields (Set[str])
  - Type: Set[str]
  - Default: normalized to an empty set by parent when None provided.
  - Purpose: Present for compatibility; not specifically used by UnsupportedAlert.
- _anchor_id (Optional[str])
  - Type: Optional[str]
  - Behavior: Computed lazily by the parent Alert when anchor_id is accessed; depends on column_name and may raise TypeError if column_name is unhashable.
  - Invariant: Once computed it remains stable for that instance.

## Lifecycle:
Creation:
- Signature:
    UnsupportedAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required: None — the class supplies the alert category to the parent internally.
- Typical instantiation:
    alert = UnsupportedAlert(values={"detected_dtype": "custom.ObjectType"}, column_name="payload")

Usage:
- Read alert attributes:
    - alert.alert_type -> the AlertType member set by the constructor (AlertType.UNSUPPORTED)
    - alert.values -> context dict
    - alert.column_name -> target column name
    - alert.anchor_id -> lazily computed stable identifier (may raise TypeError if column_name unhashable)
    - repr(alert) or alert._get_description() -> human-readable description string
    - alert.fmt() -> formatting helper inherited from Alert (not specific to UnsupportedAlert)
- Ordering: No required call order. Consumers may call anchor_id, fmt(), or repr() whenever needed.

Destruction:
- No explicit cleanup required. Instances are standard Python objects and are garbage-collected normally.

## Method Map:
graph TD
    init[__init__(values=None, column_name=None, is_empty=False)] --> super_call[super().__init__(alert_type=AlertType.UNSUPPORTED, ...)]
    init --> state_set[values, column_name, fields, _is_empty initialized]
    repr[repr(alert)] --> _get_description[_get_description() -> str]
    renderer[Renderer/Consumer] -->|calls| anchor_id[alert.anchor_id (lazy)]
    renderer -->|calls| fmt[alert.fmt() (inherited)]
    _get_description -->|reads| column_name

Notes: UnsupportedAlert defines __init__ (delegates to parent) and _get_description(); other functionality (values normalization, anchor_id, fmt) is implemented on the parent Alert class.

## Raises:
- __init__:
  - UnsupportedAlert does not explicitly raise exceptions during construction.
  - Possible runtime issues originate from arguments or later consumer access:
    - TypeError: Supplying an unhashable column_name and then accessing anchor_id will raise TypeError when hashing.
    - Consumer-side exceptions: If downstream formatters expect specific keys in values, missing keys may lead to KeyError or TypeError during formatting. UnsupportedAlert itself does not enforce any keys.
- _get_description:
  - No explicit exceptions. If column_name's stringification raises an exception, that will propagate.

## Example:
1) Create an unsupported alert and inspect:
    alert = UnsupportedAlert(values={"detected_dtype": "custom.ObjectType"}, column_name="payload")
    print(alert.alert_type)             # AlertType.UNSUPPORTED
    print(alert.values)                 # {"detected_dtype": "custom.ObjectType"}
    print(repr(alert))                  # "[payload] is an unsupported type, check if it needs cleaning or further analysis"

2) Create without a column name:
    alert = UnsupportedAlert()
    print(repr(alert))
    # -> "[None] is an unsupported type, check if it needs cleaning or further analysis"

3) Typical integration:
    if detector.identifies_unsupported_dtype(series):
        alerts.append(
            UnsupportedAlert(
                values={"detected_dtype": str(series.dtype)},
                column_name=series.name
            )
        )

### `src.ydata_profiling.model.alerts.UnsupportedAlert.__init__` · *method*

## Summary:
Initializes an UnsupportedAlert instance by setting its category to the UNSUPPORTED alert type and initializing the payload, target column, and emptiness flag — delegating container normalization to the base Alert initializer so the instance has the expected default state.

## Description:
Known callers and context:
- Constructed by profiling logic when a column/variable is detected to have an unsupported or unknown data type for the profiler's checks (for example during variable-type inference or early validation checks).
- Typically invoked during the profiling pipeline's analysis phase when building per-column alerts or during result assembly after a check identifies an unsupported type.
- Also used by components that assemble or emit alert objects for rendering or serialization (report generation, alert filtering).

Why this is a dedicated initializer:
- Provides a concise, intention-revealing constructor for the specific UNSUPPORTED alert category so callers do not need to repeat the alert_type argument.
- Keeps alert-type assignment and instance initialization centralized in a small subclass while delegating normalization and defaulting behavior to Alert.__init__. This avoids duplication and ensures consistent attribute defaults across alert subclasses.

## Args:
    values (Optional[Dict], optional):
        Optional payload with alert-specific details (e.g., context about the unsupported values).
        - Default: None
        - Behavior: Passed through to the base Alert initializer. If falsy (None or otherwise falsey), the base initializer will replace it with a new empty dict {}.
    column_name (Optional[str], optional):
        Name of the column the alert pertains to, or None for dataset-level alerts.
        - Default: None
        - Behavior: Stored verbatim on the instance (may be None).
    is_empty (bool, optional):
        Boolean flag indicating whether the condition should be considered empty.
        - Default: False
        - Behavior: Stored verbatim on the instance.

## Returns:
    None
    - This initializer does not return a value; it sets instance attributes via Alert.__init__.

## Raises:
    None explicitly.
    - Because this constructor always supplies the required alert_type to the base initializer, no TypeError for missing required arguments will be raised here.
    - The method performs no runtime type validation; any exceptions would originate from callers or from unrelated operations performed elsewhere.

## State Changes:
Attributes READ:
    - None. The constructor does not read pre-existing instance attributes.

Attributes WRITTEN (via Alert.__init__):
    - self.fields:
        * Since fields is not provided here, the base initializer will set self.fields to a new empty set().
    - self.alert_type:
        * Set to AlertType.UNSUPPORTED.
    - self.values:
        * If the values argument is truthy, assigned by reference to that object.
        * If values is falsy (e.g., None), the base initializer sets self.values to a new empty dict {}.
    - self.column_name:
        * Assigned to the provided column_name (may be None).
    - self._is_empty:
        * Assigned to the provided is_empty boolean.

## Constraints:
Preconditions:
    - No special preconditions required from callers; arguments are optional and may be None (values and column_name) or omitted.
    - Callers should pass a mapping for values if they expect Alert methods to rely on mapping operations; the constructor itself does not validate the type.

Postconditions:
    - After construction:
        * self.alert_type is AlertType.UNSUPPORTED.
        * self.fields is an empty set() (since fields was not passed through this subclass constructor).
        * self.values is a dict: the provided truthy mapping if passed, otherwise a new empty dict {}.
        * self.column_name equals the provided column_name (or None).
        * self._is_empty equals the provided is_empty boolean.
    - The object is ready for use with Alert methods (fmt, _get_description, __repr__) which assume the above normalized attributes.

## Side Effects:
    - No I/O, logging, or external service calls occur.
    - Reference semantics:
        * If a truthy mutable mapping is passed as values, the Alert instance will reference the same object (external mutations to that mapping will be reflected in the alert).
        * No external objects are mutated by this constructor beyond storing references on the new instance.

### `src.ydata_profiling.model.alerts.UnsupportedAlert._get_description` · *method*

## Summary:
Return a concise human-readable description stating that the column on this alert has an unsupported data type; does not modify the object's state.

## Description:
Constructs and exactly-formatted message text that identifies the affected column (by name) and advises checking for cleaning or further analysis.

Known callers / usage context:
    - No direct callers are visible in the provided source snippet.
    - Intended consumer: code that collects or renders alert descriptions (e.g., alert serialization, report assembly, or UI rendering) will call this method to obtain the message shown to users. This is an intended usage pattern, not a claim about where the method is referenced in the available files.

Why this is a separate method:
    - Isolates presentation text for this alert type so that message formatting is centralized and can be overridden, tested, or changed without touching alert orchestration logic.

## Args:
    - None (instance method).
Implicit requirements:
    - self.column_name: expected to exist on the instance. Best as a str representing the column identifier.

## Returns:
    - str: A single-line description with the column name embedded. Exact format:
        "[<column_name>] is an unsupported type, check if it needs cleaning or further analysis"
    - Behavior on edge inputs:
        * If self.column_name is not a str, Python's f-string formatting coerces it to its string representation (equivalent to str(self.column_name)).
        * If self.column_name is an empty string, the message will contain empty brackets "[]".
        * If self.column_name is missing, an AttributeError will occur (see Raises).

Example:
    - If self.column_name == "age", the method returns:
        "[age] is an unsupported type, check if it needs cleaning or further analysis"

## Raises:
    - AttributeError: If the instance does not have the attribute column_name (attribute access fails).
    - Any exception raised by the attribute access (e.g., if column_name is a property whose getter raises); such exceptions are not introduced by this method itself.

## State Changes:
Attributes READ:
    - self.column_name

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - The instance must have an attribute named column_name. Preferably this attribute is a non-empty string.
Postconditions:
    - The method returns the formatted description string and leaves the object state unchanged.

## Side Effects:
    - None. The method performs pure string formatting only; it does not perform I/O, logging, network calls, or modify external objects.

## `src.ydata_profiling.model.alerts.ZerosAlert` · *class*

## Summary:
Represents an alert indicating a column/variable contains an excessive number or proportion of zero values. It carries the zero count/share metadata and formats a concise human-readable description for reports.

## Description:
ZerosAlert is created by the profiling pipeline's zeros-detection rule when a variable exhibits many zeros (by absolute count or relative share). Typical creators are the detector/check functions; consumers are report renderers and alert aggregators that format and display detected issues.

Design responsibility and boundary:
- ZerosAlert is a small, typed container whose alert_type is the zeros category and whose fields enumerate the metric keys relevant to this alert.
- It provides a presentation helper (_get_description) that returns a one-line message using the supplied values and column name and delegates percentage formatting to fmt_percent.
- It does not perform detection or I/O; it only holds metadata and presentation bits.

Important implementation note (observed behavior):
- The ZerosAlert constructor calls the Alert base class via super().__init__ with alert_type=AlertType.ZEROS and fields={"n_zeros", "p_zeros"}. The Alert base class may normalize a None values parameter to an empty dict ({}), which affects whether the description fallback branch is reachable.

## State:
Inherited and instance attributes (as available after construction):
- alert_type (AlertType)
  - Type: AlertType enum
  - Value for ZerosAlert instances: AlertType.ZEROS (provided to the base class by the constructor).
  - Invariant: remains the ZEROS enum member.
- values (Optional[Dict])
  - Type: dict or None as passed in, but commonly an empty dict if the base Alert normalizes None.
  - Expected keys when populated:
      - 'n_zeros' (int-like): number of zeros (>= 0).
      - 'p_zeros' (float-like): fractional share (typically 0.0..1.0).
  - Notes: _get_description assumes these keys exist when values is not None; if they are missing, KeyError will be raised.
- column_name (Optional[str])
  - Type: str or None
  - Used for human-readable identification in messages; stringified in the description.
- fields (Set[str])
  - Type: set of str
  - Value: includes the metric names {"n_zeros", "p_zeros"} (provided to the base class by the constructor).
- _is_empty (bool)
  - Type: bool
  - Purpose: passthrough flag for placeholder/empty alerts (stored by the base class).
- Class invariants:
  - alert_type equals AlertType.ZEROS.
  - fields contains {"n_zeros", "p_zeros"}.
  - _get_description does not mutate instance state.

## Lifecycle:
Creation:
- Constructor signature (as implemented):
    ZerosAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Constructor behavior (observed):
    - Calls super().__init__(alert_type=AlertType.ZEROS, values=values, column_name=column_name, fields={"n_zeros", "p_zeros"}, is_empty=is_empty)
    - Note: The Alert base class documentation indicates it commonly normalizes a None values argument to {}. Therefore, callers should be mindful that passing None may result in an empty dict being stored, which will cause _get_description to attempt to read keys and raise KeyError unless values are populated.
Usage:
- Typical usage sequence:
    1) Detector creates the ZerosAlert instance with values containing 'n_zeros' and 'p_zeros' and a column_name.
    2) Renderer or consumer calls repr(alert) or alert._get_description() to obtain the textual description for reports.
    3) Other Alert base helpers (e.g., anchor_id, fmt()) may be invoked by renderers as needed.
- Ordering constraints:
    - No special ordering beyond instantiation before description/formats.
Destruction:
- No explicit cleanup required; normal garbage collection is sufficient.

## Method Map:
graph TD
    A[__init__(values, column_name, is_empty)] --> B[Alert.__init__(alert_type=AlertType.ZEROS, fields={'n_zeros','p_zeros'})]
    B --> C[Instance available to consumers]
    C --> D[_get_description()]
    D --> E{self.values is not None?}
    E -->|True| F[Read self.values['n_zeros'], self.values['p_zeros']]
    F --> G[Call fmt_percent(self.values['p_zeros'])]
    G --> H[Return "[{column_name}] has {n} ({formatted}) zeros"]
    E -->|False| I[Return "[{column_name}] has predominantly zeros"]

(Note: fmt_percent is an external helper used for percentage formatting; repr(alert) in the base Alert calls this _get_description for human-readable output.)

## Raises:
- __init__:
  - The ZerosAlert constructor itself does not explicitly raise exceptions.
  - Indirect errors may arise later from consumer access (e.g., unhashable column_name when computing anchor_id in the base class).
- _get_description:
  - KeyError:
      - Trigger: self.values is not None (or normalized to an empty dict) but lacks 'n_zeros' or 'p_zeros'.
      - Practical effect: attempting to access self.values['n_zeros'] / self.values['p_zeros'] will raise KeyError.
  - TypeError:
      - Trigger: self.values['p_zeros'] is not numeric and fmt_percent raises TypeError, or column_name cannot be stringified.
  - Notes:
      - The method propagates underlying exceptions; it does not attempt to catch missing keys or wrong types.

## Example:
1) Typical (detector-provided values):
    values = {"n_zeros": 12, "p_zeros": 0.03}
    alert = ZerosAlert(values=values, column_name="age")
    # Consumer:
    print(repr(alert))            # repr delegates to _get_description; expects "[age] has 12 (3.0%) zeros"
    print(alert._get_description())  # -> "[age] has 12 (3.0%) zeros"

2) Fallback when values is explicitly None:
    alert = ZerosAlert(values=None, column_name="age")
    # If the base Alert preserves None (rare), the fallback branch is used:
    alert._get_description()  # -> "[age] has predominantly zeros"
    # If the base Alert normalized None -> {}, calling _get_description() will raise KeyError
    # because 'n_zeros'/'p_zeros' are missing. Callers should populate values or handle KeyError.

Implementation notes for re-creation:
- When recreating this class, ensure the constructor invokes the Alert base constructor with alert_type=AlertType.ZEROS and fields={"n_zeros", "p_zeros"} to mirror observed behavior.
- The description behavior is:
    - If self.values is not None:
        - Read n = self.values['n_zeros']
        - Read p = self.values['p_zeros']
        - formatted = fmt_percent(p)
        - Return f"[{self.column_name}] has {n} ({formatted}) zeros"
    - Else:
        - Return f"[{self.column_name}] has predominantly zeros"
- Be explicit about validating values before calling _get_description in consumer code if you wish to avoid KeyError. Alternatively, populate values with the expected keys when constructing the alert.

### `src.ydata_profiling.model.alerts.ZerosAlert.__init__` · *method*

## Summary:
Initializes the alert object for columns that contain an excessive number or proportion of zero values by configuring the alert category, the set of tracked fields, and storing the provided values, column name, and empty-flag on the instance.

## Description:
This constructor creates a ZEROS-type Alert by delegating initialization to the Alert base class with the appropriate alert_type and tracked fields. It is invoked when the profiling pipeline (or alert-building logic) needs to represent a detected "too many zeros" condition for a single column or series — typically immediately after computing the number and/or proportion of zeros for that variable.

Known callers and context:
- There are no direct callers shown in this file. Typical callers are the profiling checks or alert factory functions within the data profiling pipeline that detect large counts or proportions of zeros for a column and then instantiate a ZerosAlert to record that finding.
- Lifecycle stage: construction occurs during the alert generation phase of profiling, after statistics (n_zeros, p_zeros) for a column have been computed.

Why this is a separate constructor:
- ZerosAlert exists as a small subclass to give a clear, typed alert (AlertType.ZEROS) and to centralize the set of fields relevant to zero-count alerts ("n_zeros", "p_zeros"). This avoids repeating the same configuration at multiple call sites and ensures consistent formatting and behavior for zero-related alerts.

## Args:
    values (Optional[Dict]): Optional mapping with diagnostic values for the alert. Expected keys (by convention) include:
        - "n_zeros": integer count of zero values
        - "p_zeros": proportion/percentage expressed as a float (0.0-1.0) used for display
      Default: None. If None, the alert is created without numeric details and the description falls back to a generic message.
    column_name (Optional[str]): Name of the column/series this alert refers to. Default: None.
    is_empty (bool): Flag indicating whether the referenced series is empty. Default: False.

## Returns:
    None

## Raises:
    None raised directly by this constructor.
    Note: If a caller supplies a non-None values mapping that does not include the expected "n_zeros" and "p_zeros" keys, downstream uses (for example ZerosAlert._get_description) will raise a KeyError when trying to access these keys. The constructor itself does not validate the contents of the values dict.

## State Changes:
Attributes READ:
    - None on self (the constructor delegates to the base class and does not read existing instance attributes).

Attributes WRITTEN (set on self by delegating to Alert.__init__):
    - self.fields: set to {"n_zeros", "p_zeros"} (the tracked fields for this alert type)
    - self.alert_type: set to AlertType.ZEROS
    - self.values: set to the provided values mapping or {} if values is None
    - self.column_name: set to the provided column_name (may be None)
    - self._is_empty: set to the provided is_empty boolean

## Constraints:
Preconditions:
    - Callers should pass values as either None or a mapping-like object. When providing values, callers are expected (by convention) to include integer "n_zeros" and float "p_zeros" entries if they want the descriptive message to include exact counts/proportions.
    - column_name should be a string or None.

Postconditions:
    - After construction, self.alert_type is AlertType.ZEROS and self.fields contains exactly "n_zeros" and "p_zeros".
    - self.values is a dict-like object (empty dict if None was passed).
    - self.column_name equals the passed column_name.
    - self._is_empty equals the passed is_empty.

## Side Effects:
    - No I/O, network access, or calls to external services.
    - Mutates only the instance attributes listed under "Attributes WRITTEN".
    - Does not register the alert or mutate external collections; those actions (if any) are the responsibility of the caller.

### `src.ydata_profiling.model.alerts.ZerosAlert._get_description` · *method*

## Summary:
Return a single-line human-readable description of the zeros condition for this alert, using the alert's column_name and values; does not mutate the instance.

## Description:
Known callers and invocation context:
- repr(alert): The Alert.__repr__ implementation calls this method to produce the textual description shown when an alert is stringified.
- Report renderers and presentation helpers: used when embedding alert text in profiling reports, logs, or diagnostic output after a "zeros" check has constructed a ZerosAlert.

Lifecycle stage:
- Called after a detection routine has created a ZerosAlert (typically when many zero values are detected) and later when the alert is rendered, inspected, or logged.

Why this is a separate method:
- Centralizes the presentation logic for ZerosAlert messages so repr() and renderers reuse a consistent format.
- Keeps formatting logic isolated per-alert-type so changes to wording or percentage formatting are localized.

## Args:
- None (reads instance attributes; no parameters).

## Returns:
- str: A formatted one-line message.
    - Typical (when values contains expected keys):
      "[{column_name}] has {n_zeros} ({formatted_p_zeros}) zeros"
        - {n_zeros}: value from self.values['n_zeros'] (expected integer-like, >= 0).
        - {formatted_p_zeros}: result of fmt_percent(self.values['p_zeros']) (e.g., "12.3%", "< 0.1%", "> 99.9%").
    - Fallback (when values is None):
      "[{column_name}] has predominantly zeros"
    - Edge cases:
      - If column_name is None, the bracket will show "None" (e.g., "[None] has ...").
      - If p_zeros is NaN or non-numeric, fmt_percent behavior applies (may produce "nan%" or raise TypeError).
      - If values is an empty dict (Alert's typical default), accessing self.values['n_zeros'] will raise KeyError (see Raises).

## Raises:
- KeyError:
    - Trigger: self.values is not None but does not contain 'n_zeros' or 'p_zeros' (e.g., values == {} as is the Alert default). Accessing self.values['n_zeros'] / self.values['p_zeros'] will raise KeyError.
- TypeError:
    - Trigger: self.values['p_zeros'] is not numeric and fmt_percent raises TypeError, or column_name has a representation that raises TypeError when formatted.
- Notes:
    - This method does not catch or convert exceptions; it propagates underlying errors to the caller. Callers should ensure values contains expected keys and types or handle exceptions.

## State Changes:
- Attributes READ:
    - self.values
    - self.column_name
- Attributes WRITTEN:
    - None (method does not modify the instance).

## Constraints:
Preconditions:
- Per the Alert class, instances normally have values set to a dict (Alert.__init__ normalizes None -> {}); therefore:
    - Typical callers should populate values with keys:
        - 'n_zeros' (int-like)
        - 'p_zeros' (float-like, fractional share 0.0..1.0)
    - If values remains the default empty dict, callers must expect KeyError when calling this method.
- column_name should be a value with a sensible string representation (typically a str).

Postconditions:
- The method returns a str and leaves the instance state unchanged.
- If successful, the returned string describes the zero count and formatted percentage.

## Side Effects:
- None: no I/O, no external service calls, no mutation of objects outside self. Exceptions are propagated.

## Implementation notes (for reimplementation):
- Exact behavior:
    - If self.values is not None:
        - Read n = self.values['n_zeros']
        - Read p = self.values['p_zeros']
        - formatted = fmt_percent(p)
        - Return f"[{self.column_name}] has {n} ({formatted}) zeros"
    - Else:
        - Return f"[{self.column_name}] has predominantly zeros"
- Dependency:
    - Delegates percentage formatting to fmt_percent — replicate its formatting (one decimal place with "< 0.1%" / "> 99.9%" shorthands) or call the same helper to ensure consistent presentation.
- Defensive implementation suggestion:
    - Before formatting, verify keys exist and types are compatible:
        - if not isinstance(self.values, dict) or 'n_zeros' not in self.values or 'p_zeros' not in self.values:
            - Either return the fallback message or raise a clear error (depending on desired behavior).
    - Prefer not to rely on the else branch in normal operation because Alert typically normalizes values to a dict.

## Examples:
1) Typical (values provided by a zeros-check):
    - Given: self.column_name == "age", self.values == {"n_zeros": 12, "p_zeros": 0.03}
    - Returns: "[age] has 12 (3.0%) zeros"  (fmt_percent(0.03) -> "3.0%")

2) Fallback (explicit None values; uncommon because Alert normally uses {}):
    - Given: self.column_name == "age", self.values is None
    - Returns: "[age] has predominantly zeros"

3) Malformed values (caller must handle):
    - Given: self.column_name == "age", self.values == {}
    - Behavior: KeyError when trying to read 'n_zeros' or 'p_zeros' (caller should ensure values populated).

## `src.ydata_profiling.model.alerts.RejectedAlert` · *class*

## Summary:
Represents an Alert that marks a column/variable as rejected. It is a thin, typed specialization of Alert that fixes the alert_type to AlertType.REJECTED and provides a concise human-readable description.

## Description:
Instantiate this class when the profiling pipeline or a check determines that a particular column/variable should be rejected (for example, unsuitable data type, unsupported format, or otherwise excluded from further analysis). Typical callers are rule/check implementations and alert aggregators in the profiling engine that detect a "rejected" condition and create an alert to record that decision.

This class exists as a distinct abstraction to:
- Semantically identify rejection conditions (alert_type is set to AlertType.REJECTED).
- Reuse Alert presentation helpers and metadata container semantics while providing a specialized description for rejected columns.

Responsibility boundary:
- Stores metadata about a rejection and provides a textual description used by renderers and logs.
- Does not perform detection, fixation, or any I/O. Detection logic that decides to reject a column lives elsewhere.

## State:
Inherited from Alert (always present on instances)
- alert_type (AlertType)
    - Value: fixed to AlertType.REJECTED for all RejectedAlert instances.
    - Invariant: should always equal AlertType.REJECTED for this class.
- values (Dict)
    - Type: dict
    - Default behavior: when None is passed to __init__, the Alert base class normalizes it to an empty dict ({}).
    - Usage: free-form metadata for the rejection (reason codes, counts, example values). No required keys.
- column_name (Optional[str])
    - Type: Optional[str]
    - Default: None when not supplied.
    - Usage: the name of the column/variable being rejected. Used in the textual description and by consumers that need to map alerts back to columns.
- fields (Set[str])
    - Type: set of str (Alert ensures this is a set; default empty set if not provided)
    - Usage: related field names when applicable.
- _is_empty (bool)
    - Type: bool
    - Default: False unless specified.
    - Usage: internal flag callers may use to mark placeholder/empty alerts.
- _anchor_id (Optional[str])
    - Type: Optional[str]
    - Lazy-cached string computed by Alert.anchor_id on first access (not computed by RejectedAlert directly).
    - Invariant: once computed, remains constant for the instance.

Class invariants:
- The instance's alert_type is AlertType.REJECTED.
- values is always a dict and fields is always a set after initialization (inherited invariants).
- _anchor_id, once computed via the base class property, remains stable.

## Lifecycle:
Creation:
- Constructor signature:
    RejectedAlert(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
- Required arguments:
    - None required; all parameters are optional.
- Typical instantiation:
    - Created by a detector when a column is deemed rejected:
        alert = RejectedAlert(column_name="age", values={"reason": "unsupported_dtype"}, is_empty=False)

Usage:
- Typical call sequence:
    1. Create instance as above.
    2. Consumers access attributes such as alert.values, alert.column_name, or call presentation helpers inherited from Alert (e.g., alert.fmt(), alert.alert_type_name).
    3. repr(alert) or str-like renderers call Alert._get_description (via repr) — RejectedAlert overrides _get_description to provide a rejection-specific message.
- Required sequencing:
    - There is no strict method-order requirement. _get_description is safe to call at any time after creation.
    - Accessing anchor_id (inherited) may compute and cache a value; no interaction with RejectedAlert methods is required.

Destruction:
- No explicit cleanup required. Instances are regular Python objects collected by garbage collection.

## Method Map:
graph TD
    A[Create RejectedAlert: __init__] --> B[Inherited: values, column_name, fields, _is_empty]
    A --> C[Call repr() or renderers]
    C --> D[Alert.__repr__ -> calls _get_description()]
    D --> E[RejectedAlert._get_description() -> returns "[{column_name}] was rejected"]
    B --> F[Optional: access anchor_id (inherited) -> computes _anchor_id lazily]

## Detailed behavior of methods (how to implement)
- __init__(values: Optional[Dict] = None, column_name: Optional[str] = None, is_empty: bool = False)
    - Purpose: Initialize a RejectedAlert instance by forwarding parameters to the Alert base class while fixing alert_type to AlertType.REJECTED.
    - Implementation notes:
        - Call the Alert base class constructor with alert_type=AlertType.REJECTED, and pass values, column_name, and is_empty through unchanged.
        - Do not mutate values in RejectedAlert; base class responsibility handles normalization (e.g., converting None to {}).
        - No additional attributes are added by RejectedAlert.
    - Edge cases:
        - If values is None, the base class will set values to {} (per Alert behavior).
        - If column_name is omitted (None), textual descriptions will reflect that (e.g., "[None] was rejected"); callers are encouraged to provide a meaningful string.
        - No validation of values or column_name is performed here; that remains the caller's responsibility.

- _get_description(self) -> str
    - Purpose: Provide a simple textual description used by repr() and renderers.
    - Behavior:
        - Returns a 1-line string: f"[{self.column_name}] was rejected"
        - If column_name is None, the string includes "None" inside brackets (i.e., "[None] was rejected").
        - This method does not raise under normal stringification of column_name. If column_name's __str__ raises, that exception will propagate.
    - Implementation notes:
        - Implement exactly as a formatted string containing the column_name between square brackets, followed by " was rejected".
        - Avoid side effects; pure formatting only.

## Raises:
- __init__: No explicit exceptions raised by RejectedAlert itself.
    - Potential runtime exceptions are inherited or indirect:
        - If the Alert base class performs normalization and that normalization raises because of malformed inputs, those exceptions propagate.
        - Accessing anchor_id later may raise TypeError if column_name is unhashable (this is an inherited caveat from Alert).
- _get_description:
    - No explicit exceptions; however, if column_name's string conversion raises, that error will propagate (rare in typical use).

## Example:
1) Basic creation and description
    from ydata_profiling.model.alerts import RejectedAlert

    alert = RejectedAlert(column_name="age", values={"reason": "unsupported_dtype"})
    print(alert.values)            # {'reason': 'unsupported_dtype'}
    print(alert.column_name)       # "age"
    print(repr(alert))             # Delegates to Alert.__repr__ which calls _get_description -> "[age] was rejected"
    print(alert._get_description())# "[age] was rejected"

2) Creation without column_name
    alert = RejectedAlert(values={"reason": "invalid"})
    print(alert._get_description())  # "[None] was rejected" (recommend providing column_name for clarity)

3) Notes for consumers
    - Prefer passing a succinct string for column_name so that the description and any anchor_id (if used) are meaningful.
    - Use the values dict to supply any structured metadata needed by renderers or downstream consumers (e.g., {"reason": "...", "code": 123}).

### `src.ydata_profiling.model.alerts.RejectedAlert.__init__` · *method*

## Summary:
Initializes a RejectedAlert instance by delegating to the base Alert initializer while fixing the alert type to the REJECTED category, leaving the object's alert-related attributes normalized and ready for use.

## Description:
Known callers and context:
- Constructed by profiling and alert-generation code when a variable/column is explicitly rejected from profiling (for example due to user configuration, unsupported data type, or pre-filtering logic).
- Typically invoked during the profiler's check/analysis phase immediately after the condition that marks a variable as rejected is detected and before alerts are collected, formatted, or serialized for reporting.

Why this is a dedicated initializer:
- Encapsulates the specialization of a generic Alert by setting a canonical alert_type (AlertType.REJECTED) so callers do not need to repeat that constant.
- Reuses the Alert.__init__ normalization logic for values, fields, column_name, and emptiness flag, avoiding duplication and ensuring consistent default handling across alert subclasses.
- Keeps subclass responsibilities minimal: supply the specialized AlertType and allow the shared initializer to perform attribute normalization.

## Args:
    values (Optional[Dict], optional):
        Payload dictionary with alert-specific details. Typical keys may include contextual information relevant to the rejection.
        - Default: None
        - Behavior: Passed through to Alert.__init__. If falsy (None, {} or other falsy object), the base initializer will replace it with a new empty dict {}.
    column_name (Optional[str], optional):
        The name of the column or variable this alert pertains to. May be None for dataset-level rejections.
        - Default: None
        - Behavior: Stored verbatim on the instance (no validation).
    is_empty (bool, optional):
        A boolean flag indicating whether the underlying condition is considered empty.
        - Default: False
        - Behavior: Stored verbatim on the instance as self._is_empty.

## Returns:
    None
    - This initializer does not return a value; it sets instance state via attributes.

## Raises:
    None explicitly by this method.
    - The call delegates to Alert.__init__ which requires an alert_type; because this initializer supplies AlertType.REJECTED, no TypeError for a missing alert_type occurs here.
    - No additional runtime type validation occurs; if callers pass incompatible types for values or column_name, other code that assumes specific types may raise exceptions later.

## State Changes:
Attributes READ:
    - None. The initializer does not read existing instance attributes.

Attributes WRITTEN (set on self by the delegated Alert.__init__ call):
    - self.fields:
        * Since RejectedAlert.__init__ does not accept a fields argument, the base initializer will assign a default empty set() (i.e., self.fields becomes a new empty set()).
    - self.alert_type:
        * Assigned to AlertType.REJECTED (fixed by this subclass).
    - self.values:
        * If the values argument is truthy, the same object reference is stored; if falsy, self.values is set to a new empty dict {} by the base initializer.
    - self.column_name:
        * Assigned to the given column_name value (may be None).
    - self._is_empty:
        * Assigned to the provided is_empty boolean.

## Constraints:
Preconditions:
    - No runtime validation is enforced here; callers should pass sensible arguments:
        * Prefer a dict-like object for values (though any object is accepted and stored by reference if truthy).
        * column_name should be a string or None.
    - The initializer assumes Alert.__init__ semantics are unchanged (that it performs the normalization described above).

Postconditions:
    - After construction:
        * self.alert_type is AlertType.REJECTED.
        * self.fields is an empty set() (since fields are not provided by this subclass).
        * self.values is either the truthy object passed in or a fresh empty dict {} if a falsy value was provided.
        * self.column_name equals the column_name argument (or None).
        * self._is_empty equals the is_empty argument.
        * The object is ready to be used anywhere a generic Alert is used, but it will always report its type as REJECTED.

## Side Effects:
    - No I/O, logging, or external service calls are performed.
    - Reference semantics:
        * If a mutable, truthy container is passed as values, that same object is referenced by the alert (external mutations will be visible through the alert).
        * Because fields are not accepted as an argument here, an empty set() is created for self.fields and no outside object identity is preserved for fields.

### `src.ydata_profiling.model.alerts.RejectedAlert._get_description` · *method*

## Summary:
Return a single-line human-readable message indicating that the alert's associated column was rejected.

## Description:
Produces the exact text used to describe a RejectedAlert when converting the alert to a displayable string. The implementation is a single f-string that interpolates the instance's column_name into the message template.

Callers / context:
- No callers are visible in this source file. The method is intended to be invoked by report generation, alert-serialization, or presentation code that needs a one-line description for this alert type (this intended usage is inferred from the method's purpose and class name, not enumerated in this module).

Why this is a separate method:
- It isolates the per-alert textual representation so subclasses can override formatting independently of alert evaluation logic. The method is compact and focused solely on producing the formatted description.

## Args:
None.

Note on related attribute:
- self.column_name: Optional[str] — provided by RejectedAlert.__init__(column_name: Optional[str] = None). The method uses this attribute when composing the string.

## Returns:
str
- The returned string always follows the exact format: "[{column_name}] was rejected"
- Examples:
    - If self.column_name == "age" -> "[age] was rejected"
    - If self.column_name is None -> "[None] was rejected"
- The method never returns None.

## Raises:
None.
- The implementation contains no operations that raise exceptions; it only formats an f-string.

## State Changes:
Attributes READ:
    - self.column_name

Attributes WRITTEN:
    - None. The method does not modify any attribute on self.

## Constraints:
Preconditions:
    - No runtime checks are performed. For a meaningful description, callers should ensure self.column_name is set to the desired string (the constructor accepts Optional[str], so None is allowed).

Postconditions:
    - self is unchanged.
    - The method returns a str formatted as described.

## Side Effects:
    - None. No I/O, no external calls, and no mutations of objects outside self occur.

## `src.ydata_profiling.model.alerts.check_table_alerts` · *function*

## Summary:
Scan a dataset-level summary mapping for table-level conditions and return zero or more Alert objects (currently: duplicates and emptiness) describing noteworthy dataset conditions.

## Description:
check_table_alerts is a small detector that examines a dictionary of dataset-level summary metrics (the "table" mapping) and emits typed Alert objects describing dataset-wide conditions:
- Appends a DuplicatesAlert when the table's duplicate-count metric is considered noteworthy (determined by the shared scalar predicate alert_value).
- Appends an EmptyAlert when the observation count ("n") is exactly zero.

Known callers within the codebase:
- No direct call sites were discovered in the collected memory during this scan. Typical callers are dataset-level profiling orchestrators or alert-aggregation stages of the profiling pipeline that evaluate summary statistics for the whole dataset after metrics are computed.

Why this logic is extracted into its own function:
- Responsibility separation: centralizes dataset-level alerting logic (which metrics trigger which dataset alerts) in a single, testable place rather than duplicating the same checks where metrics are produced or rendered.
- Reuse and testability: keeps simple, deterministic rules (duplicates thresholding via alert_value and emptiness via "n") decoupled from metric computation and report rendering.

## Args:
    table (dict):
        - A mapping representing dataset-level summary metrics. Expected usage in code:
            * table.get("n_duplicates", np.nan) is passed to alert_value to determine if duplicates are noteworthy.
            * table["n"] is read (direct access) to determine emptiness.
        - Expected keys and meanings:
            * "n" (int-like): total number of observations/rows. Required — code accesses it directly.
            * "n_duplicates" (numeric, optional): absolute number of duplicate rows or a metric that indicates duplicate share; if missing, a numeric NaN sentinel is supplied to alert_value.
        - Allowed values:
            * "n": an integer-like value (0 or positive). Equality to 0 is tested.
            * "n_duplicates": scalar numeric or missing. If present it should be scalar and comparable to numeric threshold logic used by alert_value.
        - Interdependencies:
            * The presence and type of "n_duplicates" affects whether a DuplicatesAlert is produced. The "n" key must exist; otherwise a KeyError is raised.

## Returns:
    List[Alert]:
        - A list of zero or more Alert instances describing dataset-level issues.
        - Possible return contents:
            * [] — no dataset-level alerts triggered.
            * [DuplicatesAlert(...)] — duplicates detected as noteworthy (alert_value returned True).
            * [EmptyAlert(...)] — dataset is empty (table["n"] == 0).
            * [DuplicatesAlert(...), EmptyAlert(...)] — both conditions can be reported if both predicates hold.
        - The DuplicatesAlert is constructed with values=table (the entire mapping), so downstream renderers expect table to contain keys used by DuplicatesAlert (e.g., "n_duplicates", "p_duplicates") for human-readable descriptions.
        - The EmptyAlert is constructed with values=table as well; renderers may read table["n"] (commonly 0).

## Raises:
    KeyError:
        - Condition: If the provided table mapping does not contain the "n" key, the direct access table["n"] raises KeyError.
    TypeError / ValueError:
        - Condition: If table is not a mapping (e.g., None or a list) calling table.get(...) may raise AttributeError/TypeError.
        - Condition: If table.get("n_duplicates", np.nan) returns an array-like (e.g., numpy.ndarray or pandas.Series) rather than a scalar, alert_value may raise ValueError or TypeError because it calls pd.isna(...) and performs a scalar comparison.
    Other exceptions:
        - The DuplicatesAlert and EmptyAlert constructors and later rendering may raise errors if they expect specific keys or types in values; these are downstream concerns outside this function's direct control.

## Constraints:
Preconditions:
    - The caller must pass a mapping-like object with a defined "n" key (int-like).
    - If "n_duplicates" is provided, it should be a scalar numeric value (or omitted) to work reliably with alert_value.

Postconditions:
    - The function returns a list of Alert instances; it does not modify the input table mapping.
    - If table["n"] == 0 then an EmptyAlert is present in the returned list.
    - If alert_value(table.get("n_duplicates", np.nan)) is True then a DuplicatesAlert (with values=table) is present in the returned list.

## Side Effects:
    - No I/O (no file, network, or stdout interactions).
    - No mutation of external state or the input mapping (the function only reads table and constructs new Alert objects).
    - Creates Alert objects (DuplicatesAlert, EmptyAlert) which may be retained by callers.

## Control Flow:
flowchart TD
    Start --> ValidateTable{is table mapping?}
    ValidateTable -- No --> RaiseTypeError[Raises TypeError/AttributeError]
    ValidateTable -- Yes --> GetDuplicates[n_dup := table.get("n_duplicates", np.nan)]
    GetDuplicates --> CheckDup[alert_value(n_dup)?]
    CheckDup -- True --> AppendDup[append DuplicatesAlert(values=table)]
    CheckDup -- False --> SkipDup
    AppendDup --> CheckEmpty
    SkipDup --> CheckEmpty
    CheckEmpty{table["n"] == 0?}
    CheckEmpty -- True --> AppendEmpty[append EmptyAlert(values=table)]
    CheckEmpty -- False --> SkipEmpty
    AppendEmpty --> ReturnAlerts[return alerts]
    SkipEmpty --> ReturnAlerts

Notes:
    - If table lacks "n", the CheckEmpty step raises KeyError and the function does not return a list.
    - If n_duplicates is missing, the function passes a NaN sentinel to alert_value, which will normally evaluate as "not an alert" (alert_value returns False for NaN).

## Examples:
1) Typical: non-empty dataset with notable duplicates
    - Input:
        table = {"n": 1000, "n_duplicates": 50, "p_duplicates": 0.05}
    - Behavior:
        - alert_value(50) -> True (if 50 is considered > threshold by alert_value/pd.isna semantics)
        - Returns: a list containing a DuplicatesAlert constructed with values=table

2) Typical: empty dataset
    - Input:
        table = {"n": 0}
    - Behavior:
        - The duplicates check uses table.get("n_duplicates", np.nan) -> np.nan -> alert_value(np.nan) -> False
        - table["n"] == 0 is True -> an EmptyAlert(values=table) is appended
        - Returns: a list containing a single EmptyAlert

3) Both alerts
    - Input:
        table = {"n": 0, "n_duplicates": 1, "p_duplicates": 1.0}
    - Behavior:
        - If alert_value(1) is True, DuplicatesAlert appended
        - table["n"] == 0 True -> EmptyAlert appended
        - Returns: [DuplicatesAlert(values=table), EmptyAlert(values=table)]

4) Error case: missing "n"
    - Input:
        table = {"n_duplicates": 10}
    - Behavior:
        - First check: alert_value(10) may append a DuplicatesAlert
        - Next: table["n"] raises KeyError -> function raises KeyError and does not return alerts

Implementation notes for reimplementers:
    - Preserve the decision order: duplicates check first (using table.get with a NaN fallback), then emptiness check via direct access to "n".
    - Use the same construction semantics: DuplicatesAlert(values=table) and EmptyAlert(values=table) so downstream renderers receive the complete metric mapping.
    - Keep the function side-effect free: do not mutate the provided table mapping.

## `src.ydata_profiling.model.alerts.numeric_alerts` · *function*

## Summary:
Generate column-level numeric alerts from a variable summary and configuration: returns a list of Alert objects (Skewed, Infinite, Zeros, Uniform) for the numeric checks that trigger.

## Description:
This function evaluates a numeric-variable summary dictionary against configured thresholds and produces zero-or-more Alert instances describing noteworthy conditions.

Known callers / typical usage:
- Called by the profiling pipeline's per-variable alert-generation stage when the pipeline is processing a numeric column's computed summary metrics.
- Typical trigger: after metrics for one numeric column are computed (skewness, counts/proportions of zeros/infinite values, and optionally a chi-squared test result), the pipeline calls numeric_alerts(config, summary) to obtain a list of Alerts to attach to the variable's report.

Why this logic is extracted:
- Consolidates numeric-specific alerting rules in a single function so detection code remains consistent and easy to maintain.
- Separates the decision logic (which alerts should be created) from metric computation and from presentation of alerts.
- Keeps threshold-based checks tied to the configured thresholds in Settings rather than scattered across the codebase.

## Args:
    config (Settings):
        The profiling configuration object. Expected to expose numeric alert thresholds at:
            config.vars.num.skewness_threshold
            config.vars.num.chi_squared_threshold
        Type: Settings (from ydata_profiling.config). The function does not validate the presence of the attributes beyond reading them; missing attributes will raise AttributeError at runtime.

    summary (dict):
        A mapping of precomputed numeric metrics for a single variable. Expected keys used by this function:
            - "skewness": numeric (float-like) skewness statistic
            - "p_infinite": numeric proportion (float) of infinite values (or None)
            - "p_zeros": numeric proportion (float) of zero values (or None)
            - "chi_squared": optional mapping with key "pvalue" (only consulted if "chi_squared" key exists)
        Notes:
            - The function reads summary["skewness"], summary["p_infinite"], and summary["p_zeros"] without guarding for their existence — providing a summary missing any of these keys will raise KeyError.
            - If "chi_squared" is not present, the chi-squared uniformity check is skipped.
            - The function passes the entire summary dict into alert constructors as the alert's values payload (e.g., SkewedAlert(summary)).

## Returns:
    List[Alert]:
        A list of zero or more Alert instances created by the function. Possible elements (constructed when a corresponding check passes):
            - SkewedAlert(summary) — appended when skewness_alert(summary["skewness"], config.vars.num.skewness_threshold) returns True.
            - InfiniteAlert(summary) — appended when alert_value(summary["p_infinite"]) returns True.
            - ZerosAlert(summary) — appended when alert_value(summary["p_zeros"]) returns True.
            - UniformAlert() — appended when "chi_squared" in summary and summary["chi_squared"]["pvalue"] > config.vars.num.chi_squared_threshold.
        Edge-case returns:
            - Returns an empty list if none of the checks trigger.
            - Returns a list containing multiple alerts (e.g., both InfiniteAlert and ZerosAlert) if multiple checks are true.

## Raises:
    KeyError:
        - If summary is missing any of the keys accessed without guard:
            * summary["skewness"]
            * summary["p_infinite"]
            * summary["p_zeros"]
        - If "chi_squared" is present but is not a mapping with key "pvalue", accessing summary["chi_squared"]["pvalue"] will raise KeyError.

    AttributeError:
        - If config.vars.num.skewness_threshold or config.vars.num.chi_squared_threshold do not exist (config object lacking expected structure), attribute access will raise.

    TypeError / ValueError (propagated from helper predicates):
        - skewness_alert and alert_value internally call pandas.isna and compare numeric values. If a supplied summary field is array-like (e.g., ndarray or Series) or otherwise non-scalar, these helper predicates may raise ValueError/TypeError. Those errors propagate out of numeric_alerts.

    Notes:
        - The function itself contains no explicit raise statements; the listed exceptions arise from dictionary access and helper functions it invokes.

## Constraints:
Preconditions:
    - config must be a Settings object with the numeric threshold attributes referenced above.
    - summary must be a dict-like mapping with keys as described in Args. At minimum, the summary must contain the keys "skewness", "p_infinite", and "p_zeros" to avoid KeyError.
    - Values for the summary keys should be scalar (float-like) or missing (None/NaN). Passing array-like objects for these values can cause helper predicates to raise.

Postconditions:
    - The function returns a list of Alert objects (possibly empty).
    - It does not mutate the provided config or summary arguments.
    - Each alert's values payload will be the original summary dict (the function forwards summary as the "values" parameter to alert constructors).

## Side Effects:
    - No I/O (no file, network, or stdout operations).
    - No global state mutation.
    - The only side effect is the creation of Alert instances (in-memory objects) which capture references to the summary dict (potentially increasing memory usage if summary is large).

## Control Flow:
flowchart TD
    Start([Start]) --> ReadSkew[Read summary["skewness"]]
    ReadSkew --> CheckSkew{skewness_alert(skewness, skew_thresh) ?}
    CheckSkew -- Yes --> AddSkewed[Append SkewedAlert(summary)]
    CheckSkew -- No --> SkipSkew[skip]

    SkipSkew --> ReadInf[Read summary["p_infinite"]]
    AddSkewed --> ReadInf

    ReadInf --> CheckInf{alert_value(p_infinite) ?}
    CheckInf -- Yes --> AddInf[Append InfiniteAlert(summary)]
    CheckInf -- No --> SkipInf[skip]

    SkipInf --> ReadZeros[Read summary["p_zeros"]]
    AddInf --> ReadZeros

    ReadZeros --> CheckZeros{alert_value(p_zeros) ?}
    CheckZeros -- Yes --> AddZeros[Append ZerosAlert(summary)]
    CheckZeros -- No --> SkipZeros[skip]

    SkipZeros --> ChiPresent{ "chi_squared" in summary? }
    AddZeros --> ChiPresent

    ChiPresent -- Yes --> ReadP[Read summary["chi_squared"]["pvalue"]]
    ChiPresent -- No --> Finalize[Return alerts]

    ReadP --> CheckChi{pvalue > chi_squared_thresh?}
    CheckChi -- Yes --> AddUniform[Append UniformAlert()]
    CheckChi -- No --> SkipUniform[skip]

    AddUniform --> Finalize
    SkipUniform --> Finalize

    Finalize --> End([Return alerts])

## Examples:
1) Typical conceptual flow:
    - Given:
        * config.vars.num.skewness_threshold = 3
        * config.vars.num.chi_squared_threshold = 0.01
        * summary contains numeric keys "skewness", "p_infinite", "p_zeros", and optionally "chi_squared": {"pvalue": ...}
    - Behavior:
        * If |summary["skewness"]| > 3 (and not missing), a SkewedAlert(summary) is created.
        * If summary["p_infinite"] > 0.01 (and not missing), an InfiniteAlert(summary) is created.
        * If summary["p_zeros"] > 0.01 (and not missing), a ZerosAlert(summary) is created.
        * If "chi_squared" exists in summary and its pvalue exceeds the configured chi-squared threshold, a UniformAlert() is created.
    - The returned list collects all alerts that triggered for that variable.

2) Defensive caller notes:
    - To avoid KeyError, ensure the summary dict contains "skewness", "p_infinite", and "p_zeros" before calling numeric_alerts. If chi-squared details may be missing, that's fine — the function will simply skip the uniformity check.
    - If summary values may be array-like or Series objects, convert them to scalars (e.g., take the appropriate element) prior to calling numeric_alerts to avoid ValueError/TypeError from the helper predicates.

## `src.ydata_profiling.model.alerts.timeseries_alerts` · *function*

## Summary:
Compose time-series specific alerts for a single variable by delegating numeric checks to the numeric_alerts routine and then adding non-stationary and seasonal alerts when indicated by the summary.

## Description:
This function is called during the per-variable alert-generation stage of the profiling pipeline after summary metrics for a variable have been computed. Typical callers are the profiling engine’s per-column processing code that collects metrics (skewness, proportions of zeros/infinite values, stationarity/seasonality flags, optional chi-squared results) and then asks this function to convert those metrics into a list of Alert objects for reporting.

Responsibility boundary and rationale:
- Responsibility: combine generic numeric alerts (via numeric_alerts(config, summary)) with simple time-series flags (non-stationary, seasonal) into a single list of Alert instances for the variable.
- Why extracted: keeps time-series-specific alert decisions separate from numeric check logic and from presentation. This separation centralizes the logic that composes the final list of alerts for a time-series variable and ensures consistent creation of the small typed Alert subclasses (NonStationaryAlert, SeasonalAlert).

Known callers (typical, within profiling pipeline):
- Per-variable alert aggregator invoked after metric computation for a column (time-series branch of the profiling engine).
- Any code that needs a consolidated list of alerts for a time-series variable given its summary metrics and configuration.

## Args:
    config (Settings):
        - Type: Settings (ydata_profiling.config.Settings)
        - Role: Provides configuration thresholds used indirectly by numeric_alerts (e.g., numeric skewness and chi-squared thresholds).
        - Constraints: Must expose the attributes expected by numeric_alerts (e.g., config.vars.num.skewness_threshold, config.vars.num.chi_squared_threshold). Missing attributes will raise AttributeError when numeric_alerts reads them.

    summary (dict):
        - Type: dict
        - Required keys (directly or indirectly required):
            * Directly read by this function:
                - "stationary": bool-like (this function reads summary["stationary"] without guard)
                - "seasonal": bool-like (this function reads summary["seasonal"] without guard)
            * Required by numeric_alerts (the function delegates to it):
                - "skewness" (used by numeric_alerts)
                - "p_infinite" (used by numeric_alerts)
                - "p_zeros" (used by numeric_alerts)
                - optional: "chi_squared" mapping with key "pvalue" (used by numeric_alerts if present)
        - Notes:
            - The function does not validate types beyond dict key access; callers must provide appropriately-typed, scalar summary values. Missing or malformed keys will produce exceptions propagated from keyed access or numeric_alerts.
            - Interdependency: summary must satisfy both the time-series flags ("stationary", "seasonal") and the numeric metric keys required by numeric_alerts.

## Returns:
    List[Alert]:
        - Type: list of Alert objects (where Alert is the base alert class used throughout the profiling code).
        - A list of zero or more Alert instances representing issues or noteworthy conditions for the variable.
        - Possible contents:
            * Any Alert objects returned by numeric_alerts(config, summary) (e.g., SkewedAlert, InfiniteAlert, ZerosAlert, UniformAlert).
            * NonStationaryAlert appended if summary["stationary"] is falsy (i.e., not stationary).
            * SeasonalAlert appended if summary["seasonal"] is truthy.
        - Implementation detail (function-specific): in this function NonStationaryAlert and SeasonalAlert are instantiated with no arguments (i.e., called as NonStationaryAlert() and SeasonalAlert()). As a result, for the instances appended here:
            - values will be the Alert default (an empty dict), and
            - column_name will be None.
          Note: the NonStationaryAlert and SeasonalAlert classes themselves accept optional values and column_name when created elsewhere; detectors in other parts of the codebase may construct them with metadata (e.g., column_name or diagnostic values). This paragraph only documents how they are created inside timeseries_alerts.
        - Edge-case returns:
            - Empty list if numeric_alerts returns no alerts and both summary["stationary"] is truthy and summary["seasonal"] is falsy.
            - A list containing multiple alerts if multiple numeric checks and/or both time-series flags trigger.

## Raises:
    - KeyError:
        - Triggered when summary is missing keys directly accessed by this function:
            * summary["stationary"]
            * summary["seasonal"]
        - Also propagated from numeric_alerts when it accesses keys like "skewness", "p_infinite", "p_zeros" or summary["chi_squared"]["pvalue"] if present but malformed.
    - AttributeError:
        - Propagated from numeric_alerts or when config is missing expected attributes (e.g., config.vars.num.*).
    - TypeError / ValueError:
        - Propagated from numeric_alerts when numeric predicates are passed non-scalar or invalid types.
    - No exceptions are raised explicitly by this function; all above arise from delegated calls or dictionary/attribute access.

## Constraints:
Preconditions:
    - config must be a Settings object with numeric threshold attributes used by numeric_alerts.
    - summary must be a dict containing at least:
        * "stationary" (bool-like)
        * "seasonal" (bool-like)
        * and the numeric metric keys required by numeric_alerts ("skewness", "p_infinite", "p_zeros"); otherwise callers should handle or construct a safe summary to avoid KeyError.
    - Summary values expected to be scalar (float-like) for numeric checks; array-like values may cause helper predicates to raise.

Postconditions:
    - The function returns a list of Alert objects (possibly empty).
    - It does not mutate config or summary.
    - Alerts created by numeric_alerts will carry the original summary dict as their values payload (numeric_alerts forwards summary as values).
    - NonStationaryAlert and SeasonalAlert appended by this function will have default values (empty dict) and no column_name (None) because they are constructed without arguments here; detectors elsewhere in the codebase may construct these alert types with metadata if needed.

## Side Effects:
    - No I/O (no files, network, or stdout).
    - No mutation of global state.
    - The only side-effect is allocating Alert instances (in-memory objects) which may hold references to the provided summary dict (via numeric_alerts’ alerts). This can increase memory retention if summary is large.

## Control Flow:
flowchart TD
    Start([Start]) --> CallNumeric[numeric_alerts(config, summary)]
    CallNumeric --> alerts_result[alerts := numeric_alerts(...)]

    alerts_result --> CheckStationary{Is summary["stationary"] truthy?}
    CheckStationary -- No (not stationary) --> AppendNonStationary[alerts.append(NonStationaryAlert())]
    CheckStationary -- Yes (stationary) --> SkipNonStationary[skip]

    AppendNonStationary --> CheckSeasonal
    SkipNonStationary --> CheckSeasonal

    CheckSeasonal{Is summary["seasonal"] truthy?} -- Yes --> AppendSeasonal[alerts.append(SeasonalAlert())]
    CheckSeasonal -- No --> SkipSeasonal[skip]

    AppendSeasonal --> ReturnAlerts
    SkipSeasonal --> ReturnAlerts

    ReturnAlerts --> End([return alerts])

    %% Error branches (propagated)
    CallNumeric -->|KeyError/AttributeError/TypeError| ErrorHandler[exceptions propagate to caller]
    CheckStationary -->|KeyError if "stationary" missing| ErrorHandler
    CheckSeasonal -->|KeyError if "seasonal" missing| ErrorHandler

## Examples:
1) Typical successful usage (conceptual):
    - Given a profile summary for a time-series column with keys:
        {
            "skewness": 4.2,
            "p_infinite": 0.0,
            "p_zeros": 0.01,
            "chi_squared": {"pvalue": 0.05},   # optional
            "stationary": False,
            "seasonal": True
        }
    - Call:
        alerts = timeseries_alerts(config, summary)
    - Result:
        - alerts contains any numeric alerts produced by numeric_alerts plus an instance of NonStationaryAlert and an instance of SeasonalAlert appended at the end.

2) Defensive calling pattern to avoid KeyError:
    - Before calling timeseries_alerts, a caller can guard or normalize summary:
        * Ensure "stationary" and "seasonal" exist (e.g., set to False by default if unknown).
        * Ensure numeric keys ("skewness", "p_infinite", "p_zeros") are present as scalars or set to None/NaN if not applicable.
    - Example (prose):
        - If a summary may omit "stationary", do:
            summary.setdefault("stationary", True)
            summary.setdefault("seasonal", False)
            # ensure numeric keys exist or are set to safe sentinel values for numeric_alerts

3) Error propagation example:
    - If summary is missing "stationary" or "seasonal", calling timeseries_alerts will raise KeyError. Wrap in try/except if upstream cannot guarantee presence of these keys:
        try:
            alerts = timeseries_alerts(config, summary)
        except KeyError as err:
            # handle missing-summary-key case: log, supply defaults, or skip alerting
            pass

Implementation note for reimplementation:
- The function behavior is intentionally simple:
    1) call numeric_alerts(config, summary) and collect returned alerts,
    2) append NonStationaryAlert() if summary["stationary"] is falsy,
    3) append SeasonalAlert() if summary["seasonal"] is truthy,
    4) return the list.
- Preserve the exact decision order (numeric alerts first, then non-stationary, then seasonal) to remain compatible with consumers that may rely on alert ordering.

## `src.ydata_profiling.model.alerts.categorical_alerts` · *function*

## Summary:
Produces a list of zero-or-more Alert objects for a single categorical variable by applying a sequence of categorical checks (high-cardinality, uniformity, date-like values, constant length, and imbalance) against the supplied summary and configuration thresholds.

## Description:
This function is called by the profiling pipeline's categorical-variable check stage (the column-level rule/check orchestrator that aggregates alerts for a single variable during profile generation). Typical callers are the column-analysis routine that builds a per-variable summary and then converts those summary metrics into typed Alert objects to be collected and rendered in the final report.

Why this logic is extracted:
- Encapsulates the mapping from raw summary metrics -> typed Alert instances for categorical variables, keeping detection/measurement code separate from alert-construction and rendering logic.
- Improves reuse and testability: the same set of categorical alert rules can be invoked consistently from different pipeline places (unit tests, report generation, or alternative pipelines) without duplicating if/then logic.

## Args:
    config (Settings):
        A Settings object from ydata_profiling.config. The function reads only the categorical-related thresholds:
        - config.vars.cat.cardinality_threshold: numeric threshold used for the n_distinct check.
        - config.vars.cat.chi_squared_threshold: numeric threshold used to determine uniformity from a chi-squared p-value.
        - config.vars.cat.imbalance_threshold: numeric threshold used to flag imbalanced categorical distributions.
        The thresholds must be numeric (float/int). If any are missing or not numeric the comparisons in this function may raise TypeError.

    summary (dict):
        Per-column summary dictionary produced earlier in the profiling pipeline. Known and expected keys (optional, presence controls checks):
        - "n_distinct" (int or numeric-like): number of distinct values observed.
            * If absent, the function uses NaN as default so the cardinality check will not fire.
        - "chi_squared" (dict-like): expected to contain "pvalue" (numeric) if present.
            * The function only runs the uniformity check when "chi_squared" is a key in summary; it then accesses summary["chi_squared"]["pvalue"].
        - "date_warning" (truthy flag): if present and truthy, the TypeDateAlert is raised.
        - "composition" (any truthy marker): used as a gating condition for constant-length detection; if present and summary contains min_length and max_length, they are compared.
        - "min_length" (int-like) and "max_length" (int-like): used to detect constant-length strings when equal.
        - "imbalance" (numeric-like): used to detect imbalanced categorical distributions.
        The function does not mutate the summary argument.

## Returns:
    List[Alert]:
        - A list containing zero or more Alert subclass instances in the following possible forms (order preserved as checks are evaluated):
            1. HighCardinalityAlert(summary) — appended when n_distinct > config.vars.cat.cardinality_threshold.
            2. UniformAlert() — appended when "chi_squared" in summary and summary["chi_squared"]["pvalue"] > config.vars.cat.chi_squared_threshold.
            3. TypeDateAlert() — appended when summary.get("date_warning") is truthy.
            4. ConstantLengthAlert() — appended when "composition" is present and summary["min_length"] == summary["max_length"].
            5. ImbalanceAlert(summary) — appended when "imbalance" in summary and summary["imbalance"] > config.vars.cat.imbalance_threshold.
        - If no checks trigger, returns an empty list [].
        - The return list contains Alert instances (or subclasses) only; each alert may hold the original summary as its values payload when the corresponding Alert constructor is called with summary.

## Raises:
    - The function itself contains no explicit raise statements; however it may propagate exceptions from unsafe summary access or invalid types:
        * KeyError:
            - If "chi_squared" is present but summary["chi_squared"] is not a mapping or lacks the "pvalue" key, accessing summary["chi_squared"]["pvalue"] raises KeyError.
            - If code elsewhere expects min_length/max_length but they are missing when "composition" exists, subsequent code that accesses those keys may raise KeyError (the current implementation directly accesses summary["min_length"] and summary["max_length"]).
        * TypeError:
            - If any compared values are not orderable with the thresholds (e.g., strings instead of numbers), comparisons like n_distinct > threshold may raise TypeError.
            - If summary["chi_squared"] is present but not indexable like a dict (e.g., None), then summary["chi_squared"]["pvalue"] may raise TypeError.
        * Any exception raised by Alert subclass constructors (e.g., unexpected types inside summary passed to HighCardinalityAlert or ImbalanceAlert) will propagate.

## Constraints:
    Preconditions:
    - config must be a valid Settings object providing numeric thresholds at config.vars.cat.cardinality_threshold, config.vars.cat.chi_squared_threshold, and config.vars.cat.imbalance_threshold.
    - summary must be a dict-like mapping. Keys referenced by checks must be present and of appropriate types for the checks to run without runtime errors.
    - The code relies on NaN comparison semantics: when "n_distinct" is missing, the default NaN causes the > comparison to evaluate False (no high-cardinality alert).

    Postconditions:
    - Returns a list of Alert instances consistent with the checks described above.
    - Does not mutate the provided summary or config objects.
    - All returned items are instances of Alert or its subclasses (HighCardinalityAlert, UniformAlert, TypeDateAlert, ConstantLengthAlert, ImbalanceAlert).

## Side Effects:
    - None visible in I/O terms: the function does not perform file, network, or stdout/stderr I/O.
    - No mutation of external state: it does not modify the summary or config objects; it only constructs and returns Alert objects.
    - It may call Alert subclass constructors which store references to objects passed (e.g., summary) inside the Alert instance values; that is internal to the created Alert objects but not a mutation performed by this function on the caller-provided summary.

## Control Flow:
flowchart TD
    Start[Start] --> Init[Create empty alerts list]
    Init --> CardCheck{n_distinct > cardinality_threshold?}
    CardCheck -- True --> AddHC[Append HighCardinalityAlert(summary)]
    CardCheck -- False --> AfterCard
    AddHC --> AfterCard[Continue]
    AfterCard --> ChiCheck{"chi_squared" in summary AND chi_squared.pvalue > chi_squared_threshold?}
    ChiCheck -- True --> AddUniform[Append UniformAlert()]
    ChiCheck -- False --> AfterChi
    AddUniform --> AfterChi[Continue]
    AfterChi --> DateCheck{summary.get("date_warning") truthy?}
    DateCheck -- True --> AddDate[Append TypeDateAlert()]
    DateCheck -- False --> AfterDate
    AddDate --> AfterDate[Continue]
    AfterDate --> CompCheck{"composition" in summary AND min_length == max_length?}
    CompCheck -- True --> AddConst[Append ConstantLengthAlert()]
    CompCheck -- False --> AfterComp
    AddConst --> AfterComp[Continue]
    AfterComp --> ImbCheck{"imbalance" in summary AND imbalance > imbalance_threshold?}
    ImbCheck -- True --> AddImb[Append ImbalanceAlert(summary)]
    ImbCheck -- False --> Final
    AddImb --> Final[Return alerts list]
    Final --> End[End]

## Examples:
1) Typical (multiple alerts fired):
    - Given thresholds:
        config.vars.cat.cardinality_threshold = 50
        config.vars.cat.chi_squared_threshold = 0.8
        config.vars.cat.imbalance_threshold = 0.7
    - Given summary:
        {
            "n_distinct": 120,
            "chi_squared": {"pvalue": 0.95},
            "date_warning": True,
            "composition": True,
            "min_length": 10,
            "max_length": 10,
            "imbalance": 0.9
        }
    - Outcome: categorical_alerts(config, summary) returns a list with five alerts:
        [HighCardinalityAlert(summary), UniformAlert(), TypeDateAlert(), ConstantLengthAlert(), ImbalanceAlert(summary)]

2) Guarding against missing nested keys:
    - If a caller cannot guarantee that summary["chi_squared"] is a dict with "pvalue", wrap the summary or validate before calling:
        * Ensure that when "chi_squared" in summary then isinstance(summary["chi_squared"], dict) and "pvalue" in summary["chi_squared"] to avoid KeyError propagation.
    - Similarly, when "composition" is present, ensure "min_length" and "max_length" exist and are comparable.

3) No alerts:
    - If none of the comparisons evaluate to True (or required keys are missing such that checks evaluate False), the function returns an empty list, indicating no categorical alerts for that variable.

Notes:
- The function relies on the Alert subclasses' constructors to format and carry metadata; returned Alert instances may use the passed summary dict as their values payload (e.g., HighCardinalityAlert(summary)).
- Keep the summary structure and types stable across the pipeline to avoid runtime exceptions when this function reads nested keys.

## `src.ydata_profiling.model.alerts.boolean_alerts` · *function*

## Summary:
Inspects a boolean-variable summary for an "imbalance" metric and returns a list with an ImbalanceAlert when that metric exceeds the configured threshold; otherwise returns an empty list.

## Description:
This function implements one small check: it looks up summary["imbalance"] and compares it to the configured threshold at config.vars.bool.imbalance_threshold. If the metric is present and strictly greater than the threshold, it appends an ImbalanceAlert instance to the result list.

Expected usage context:
- Intended to be called by the profiling pipeline or rule engine that converts per-variable summary statistics into Alert objects; this file does not itself contain pipeline orchestration or explicit callers.
- The function focuses narrowly on mapping the "imbalance" summary key to an Alert when the value exceeds a configurable threshold.

Why a separate function:
- Keeps the single check for boolean/categorical imbalance isolated and testable.
- Centralizes the threshold comparison so the threshold source (Settings) is the single place to change behavior.

## Args:
    config (Settings)
        - The global profiling Settings object.
        - The function accesses config.vars.bool.imbalance_threshold.
        - Precondition: the attribute path config.vars.bool.imbalance_threshold must exist and be a value comparable with summary["imbalance"] (typically numeric).
    summary (dict)
        - A mapping containing computed summary statistics for the variable.
        - The function checks for the key "imbalance" (membership test) and, if present, uses summary["imbalance"] in the comparison.
        - Precondition: summary must support the "in" membership test (i.e., be a mapping or iterable of keys).

Interdependencies:
- The comparison summary["imbalance"] > config.vars.bool.imbalance_threshold requires that both operands be comparable (e.g., both numeric). If they are not, a TypeError will be raised.

## Returns:
    List[Alert]
        - Always returns a list (possibly empty).
        - If "imbalance" is not in summary, returns [].
        - If "imbalance" is present and summary["imbalance"] > config.vars.bool.imbalance_threshold, returns a list containing a single ImbalanceAlert instance.
        - The ImbalanceAlert is constructed without arguments in this implementation (ImbalanceAlert()), so its values and column_name are not populated by this function; downstream code that renders alerts may expect these fields to be filled elsewhere.

## Raises:
    - AttributeError
        - Condition: If config, config.vars, or config.vars.bool is missing such that accessing .vars.bool.imbalance_threshold raises AttributeError.
    - TypeError
        - Condition: If summary does not support membership testing ("imbalance" in summary raises TypeError), or if summary["imbalance"] and the configured threshold are not comparable (the '>' operation raises TypeError).
    - Any exception propagated from ImbalanceAlert() constructor
        - Condition: Although ImbalanceAlert() normally accepts no arguments, if its constructor or the Alert base class raised for some unexpected reason, that exception will propagate.

## Constraints:
    Preconditions:
        - config.vars.bool.imbalance_threshold exists and is comparable to summary["imbalance"] when present.
        - summary supports membership testing and indexing by key.
    Postconditions:
        - The function does not mutate config or summary.
        - The returned list contains only Alert-derived instances (or is empty).
        - No external state is modified.

## Side Effects:
    - None beyond allocating in-memory Alert objects.
    - No I/O (files, network, stdout) is performed.
    - No mutation of the provided summary or global state occurs in this function.

## Control Flow:
flowchart TD
    Start[Start: call boolean_alerts(config, summary)]
    Start --> HasKey{"Is 'imbalance' in summary?"}
    HasKey -- No --> ReturnEmpty[Return []]
    HasKey -- Yes --> Compare{"summary['imbalance'] > config.vars.bool.imbalance_threshold?"}
    Compare -- No --> ReturnEmpty
    Compare -- Yes --> CreateAlert[Create ImbalanceAlert() and append to alerts]
    CreateAlert --> ReturnAlerts[Return [ImbalanceAlert]]
    ReturnEmpty --> End[End]
    ReturnAlerts --> End

## Examples:
- Imbalance above threshold:
    Given config.vars.bool.imbalance_threshold == 0.6 and summary == {"imbalance": 0.75}
    Calling boolean_alerts(config, summary) returns [ImbalanceAlert()].

- No imbalance key:
    Given summary == {}
    Calling boolean_alerts(config, summary) returns [].

- Imbalance present but not greater than threshold:
    Given config.vars.bool.imbalance_threshold == 0.8 and summary == {"imbalance": 0.75}
    Returns [].

- Type mismatch error:
    Given config.vars.bool.imbalance_threshold == 0.6 and summary == {"imbalance": "high"}
    The comparison "high" > 0.6 raises TypeError; the function does not catch it.

Note:
- The created ImbalanceAlert instance here is produced with no values or column_name. According to the ImbalanceAlert/Alert design, meaningful descriptions or formatting that rely on values["imbalance"] or column_name must be provided elsewhere in the pipeline before rendering.

## `src.ydata_profiling.model.alerts.generic_alerts` · *function*

## Summary:
Return a list of column-level Alert objects for generic conditions detected from a numeric summary; currently only emits a MissingAlert when the missing-share metric is considered notable.

## Description:
This function examines a per-column summary dictionary and produces a short list of Alert objects for generic, metric-driven conditions. It is intended to be called by profiling/aggregation code after column statistics (a "summary" dict) have been computed for a variable. Typical callers are column-level alert aggregators or report builders in the profiling pipeline that convert raw summary metrics into Alert objects to be collected and rendered.

Why this is a separate function:
- Encapsulates the simple rule-set that maps numeric summary metrics into alert objects so callers don't need to inline the threshold logic.
- Keeps detection responsibilities separate from rendering or higher-level orchestration: this function only decides which generic alerts apply and returns corresponding Alert instances.

Known/typical context:
- Called during per-column analysis once the column summary (including "p_missing") is available.
- The function relies on the alert_value predicate to decide whether a numeric metric is "noteworthy" and on MissingAlert as the concrete Alert type created for missing-value conditions.

## Args:
    summary (dict):
        - A dictionary of pre-computed summary statistics for a single column/variable (the module's profiling summary).
        - Required keys: "p_missing" — the proportion (share) of missing values for the column (expected scalar float-like).
        - The function does not accept None in place of a dict; callers should pass a mapping.

## Returns:
    List[Alert]:
        - A list of Alert instances representing generic alerts determined from the summary.
        - Possible return values:
            - []: No generic alerts apply (most common when p_missing is missing/insignificant or <= 0.01).
            - [MissingAlert(...)]: A list with a single MissingAlert instance when summary["p_missing"] passes alert_value (i.e., present and > 0.01).
        - Note: MissingAlert is constructed with no metadata (MissingAlert()) in this implementation; the returned alert may therefore contain minimal or no values metadata. Downstream renderers that expect MissingAlert.values to contain "n_missing" and "p_missing" should handle this case or the generator should be changed to provide that metadata.

## Raises:
    KeyError:
        - If "p_missing" is not present in the provided summary dict, the expression summary["p_missing"] raises KeyError.
    Propagated exceptions from alert_value:
        - NameError: If the module-level predicate alert_value internally references a missing symbol (e.g., pd) in this module's namespace.
        - ValueError: If summary["p_missing"] is array-like (numpy.ndarray or pandas.Series), alert_value may raise a ValueError due to ambiguous truth-value operations.
        - TypeError: If summary["p_missing"] is of a type that cannot be compared to a float in alert_value's comparison.
    Note: The function itself does not explicitly raise other exceptions; the listed exceptions originate from indexing the summary dict and from alert_value's behavior.

## Constraints:
Preconditions:
    - summary must be a mapping containing the key "p_missing".
    - summary["p_missing"] should be a scalar numeric (float or int) representing the fraction of missing values (typical valid range 0.0..1.0).
Postconditions:
    - Returns a list of zero or more Alert objects (no mutation of input).
    - No global state is modified and no I/O occurs.

## Side Effects:
    - None. The function is pure: it does not perform I/O, mutate global variables, or call external services.
    - It constructs Alert objects (MissingAlert) but does not register, persist, or render them.

## Control Flow:
flowchart TD
    Start --> ReadSummary["Read summary['p_missing']"]
    ReadSummary --> CallPredicate["Call alert_value(p_missing)"]
    CallPredicate --> PredicateTrue{alert_value returned True?}
    PredicateTrue -- Yes --> AppendMissing["Create MissingAlert() and append to list"]
    PredicateTrue -- No --> SkipAppend["Do not append any alert"]
    AppendMissing --> Return["Return alerts list"]
    SkipAppend --> Return

## Examples:
1) Typical usage, no alert
    summary = {"p_missing": 0.0, "n": 100}
    alerts = generic_alerts(summary)
    # alerts == []  (p_missing is not > 0.01 per alert_value)

2) Typical usage, emit MissingAlert
    summary = {"p_missing": 0.05, "n": 100}
    alerts = generic_alerts(summary)
    # alerts contains one MissingAlert instance: [MissingAlert()]
    # Note: The MissingAlert instance is constructed without values metadata; renderers expecting values["p_missing"] and values["n_missing"] should either populate them before rendering or guard against missing keys.

3) Defensive caller that handles missing "p_missing"
    try:
        alerts = generic_alerts(summary)
    except KeyError:
        # summary did not contain "p_missing"; handle gracefully (e.g., skip alerts)
        alerts = []

4) Invalid input caution (array-like)
    summary = {"p_missing": numpy.array([0.05])}
    # Calling generic_alerts(summary) may raise ValueError or TypeError because alert_value expects a scalar.
    # To avoid this, ensure p_missing is scalar before calling.

Implementation notes for integrators:
- If you want the returned MissingAlert to include the numeric metadata (n_missing, p_missing), change the creation call to MissingAlert(values={"p_missing": summary["p_missing"], "n_missing": summary.get("n", None)}, column_name=<name>) at the call site that knows the column name and count.
- Ensure the module-level symbol references required by alert_value (e.g., pandas or pd) exist in the same module namespace to avoid NameError inside alert_value.

## `src.ydata_profiling.model.alerts.supported_alerts` · *function*

## Summary:
Return Alert instances that correspond to simple distinct-value conditions detected in a per-column summary: uniqueness (distinct count equals sample size) and constant-value (exactly one distinct value).

## Description:
Given a per-variable summary mapping (a dict of precomputed metrics), this function maps specific metric conditions into typed Alert objects used by the profiling pipeline. It is intended to be invoked during the per-column alert aggregation stage after numeric summary metrics have been computed.

Known callers and typical context:
- The profiling engine's per-variable alert aggregation step (the code that collects summary metrics for each column and produces alerts for reporting).
- Uniqueness/constant checks that produce a summary dict for a column and then call this helper to obtain standardized Alert objects.
Callers usually compute metrics such as:
    - "n": the number of observations used for the column summary (required by this function)
    - "n_distinct": the number of distinct observed values (optional; treated as missing if absent)
This helper centralizes the translation from numeric summaries to Alert subclasses so alert creation remains consistent.

Why this is a separate function:
- Encapsulates the simple decision logic that converts summary metrics into Alert objects so the logic is easy to test and maintain.
- Keeps callers focused on metric computation; this function focuses only on canonical Alert creation.

## Args:
    summary (dict): Mapping of precomputed metrics for a single variable/column.
        - Expected keys:
            - "n" (numeric): sample size / count of observations. This key is required by the function; it is accessed directly.
            - "n_distinct" (int or numeric-like): number of distinct values. If absent, the function treats it as NaN via a sentinel and no alerts are created from comparisons to "n" or 1.
        - Types: summary must be dict-like and support item access by string keys. Values compared with equality should be numeric-like or otherwise comparable.
        - Interdependencies:
            - "n_distinct" is compared to summary["n"] and to 1; therefore both keys influence outcomes when present.

## Returns:
    List[Alert]: A list of zero or more Alert instances. Possible return variants (constructed exactly as below):
        - []: No matching conditions.
        - [UniqueAlert()]: Created when n_distinct == n.
            - Note: In this function UniqueAlert is instantiated with no arguments; consequently its .values dict will be empty unless callers later populate metrics.
        - [ConstantAlert(summary)]: Created when n_distinct == 1. ConstantAlert is constructed with the full summary dict passed as its values argument.
        - [UniqueAlert(), ConstantAlert(summary)]: Both conditions true (e.g., when n == 1 and n_distinct == 1). The function appends UniqueAlert first, then ConstantAlert.
    Guarantees:
        - The return value is always a Python list (never None).
        - The function does not mutate the input summary.

## Raises:
    KeyError:
        - Trigger: summary does not contain the required "n" key. The function accesses summary["n"] directly which raises KeyError if absent.
    TypeError / ValueError:
        - Trigger: If summary contains values that cannot be compared for equality with the provided "n" value (e.g., incompatible custom types), the equality checks may raise TypeError or produce unexpected results.
    NameError (module-level caution):
        - Trigger: The function uses a NaN sentinel referenced as np.nan. If the module does not define the name np (for example, if numpy is imported without the np alias), a NameError would occur. Ensure the module imports numpy as the name expected by this file.

## Constraints:
    Preconditions:
        - summary is a dict-like object and must include the "n" key with a numeric-like value suitable for equality comparison.
    Postconditions:
        - Returns a list whose elements are Alert instances representing the detected conditions. Input summary is not modified.

## Side Effects:
    - No I/O, no external state mutations, and no network or filesystem calls.
    - Only effect is allocation of Alert objects returned to the caller.

## Control Flow:
flowchart TD
    Start[Start: receive summary dict]
    A{Does summary contain "n"?}
    Start --> A
    A -- No --> Error[Accessing summary["n"] raises KeyError]
    A -- Yes --> B[nd = summary.get("n_distinct", np.nan)]
    B --> C{nd == summary["n"]}
    C -- True --> D[append UniqueAlert() (no args)]
    C -- False --> E[do nothing]
    D --> F{nd == 1}
    E --> F
    F -- True --> G[append ConstantAlert(summary)]
    F -- False --> H[do nothing]
    G --> I[Return list of alerts (order preserved)]
    H --> I

## Examples:
1) Unique values:
    Input: {"n": 100, "n_distinct": 100}
    Output: [UniqueAlert()]  # UniqueAlert instantiated without values/column_name.

2) Constant column:
    Input: {"n": 50, "n_distinct": 1}
    Output: [ConstantAlert(summary)]  # ConstantAlert receives the full summary as its values.

3) Both conditions (single-row sample):
    Input: {"n": 1, "n_distinct": 1}
    Output: [UniqueAlert(), ConstantAlert(summary)]

4) Missing n_distinct:
    Input: {"n": 10}
    Behavior: summary.get("n_distinct", np.nan) is NaN and comparisons to "n" and 1 are False; function returns [].

5) Defensive caller pattern:
    # Ensure "n" is present to avoid KeyError
    if "n" in summary:
        alerts = supported_alerts(summary)
    else:
        # handle missing sample-size information before invoking helper
        alerts = []

## `src.ydata_profiling.model.alerts.unsupported_alerts` · *function*

## Summary:
Returns a fixed list of two alert instances used to represent "unsupported" and "rejected" conditions.

## Description:
This function constructs and returns two Alert objects: an UnsupportedAlert instance and a RejectedAlert instance, created with their default constructor arguments (i.e., no values, no column_name, is_empty defaults). The provided summary argument is accepted for API compatibility but is not read or mutated by this function.

Known callers within the provided codebase:
- No direct callers were discovered in the supplied context. Typical usage in the profiling pipeline is to call this function when assembling a set of dataset-level or initialization alerts (for example, when preparing the list of alert types to consider or when seeding an aggregator that will later attach column-specific metadata).

Why this logic is a separate function:
- Centralizes the creation of the canonical Unsupported and Rejected alerts so callers can obtain a consistent, minimal set of these alert objects without needing to know concrete Alert subclasses.
- Keeps higher-level code concise and testable by isolating the construction of these specific Alert instances.

## Args:
    summary (Dict[str, Any]):
        - A dictionary representing the profiling summary for a variable or dataset.
        - Allowed values: any mapping-like object compatible with Dict[str, Any].
        - Default / behavior: no default; parameter is required by signature but currently unused inside the function.
        - Note: There are no interdependencies between summary and other parameters because this function does not use summary.

## Returns:
    List[Alert]:
        - A list of exactly two Alert instances in this order:
            1. UnsupportedAlert() — an Alert whose alert_type is AlertType.UNSUPPORTED; constructed with default args (values: {}, column_name: None, is_empty: False).
            2. RejectedAlert() — an Alert whose alert_type is AlertType.REJECTED; constructed with default args (values: {}, column_name: None, is_empty: False).
        - Edge cases:
            - If either UnsupportedAlert() or RejectedAlert() constructors raise an exception (e.g., due to unexpected behavior in their base class), that exception will propagate and no list will be returned.
        - The returned Alert instances are independent objects and may be mutated by the caller (e.g., attaching values or column_name) after return.

## Raises:
    - This function does not explicitly raise any exceptions.
    - Indirect / propagated exceptions:
        - Any exception raised by UnsupportedAlert.__init__ or RejectedAlert.__init__ (such as a TypeError raised by underlying Alert initialization when later accessed) will propagate out of unsupported_alerts.

## Constraints:
    Preconditions:
        - Caller should pass a mapping (Dict[str, Any]) as summary to match the function signature. The function does not require any particular keys and does not read summary.
    Postconditions:
        - On successful return, the function yields a list of length 2 containing the two Alert instances described in Returns.
        - No mutation of the input summary occurs.

## Side Effects:
    - None performed by this function directly: there is no I/O, no network access, no global state mutation, and no caching.
    - Side effects may occur later if the returned Alert objects are mutated by the caller (e.g., assigning column_name, setting values, or accessing anchor_id which may lazily compute and cache an anchor).

## Control Flow:
flowchart TD
    Start[Start: unsupported_alerts(summary)]
    Start --> CreateUnsupported[Create UnsupportedAlert()]
    CreateUnsupported --> CreateRejected[Create RejectedAlert()]
    CreateRejected --> ReturnList[Return [UnsupportedAlert, RejectedAlert]]
    ReturnList --> End[End]

## Examples:
1) Basic usage — obtain the two canonical alerts:
    summary = {}  # any dict; function does not read it
    alerts = unsupported_alerts(summary)
    # alerts is a list of two Alert instances
    unsupported, rejected = alerts
    assert unsupported.alert_type_name.upper().replace(" ", "_") == "UNSUPPORTED"
    assert rejected.alert_type_name.upper().replace(" ", "_") == "REJECTED"

2) Attach column-specific metadata after creation:
    summary = {"column": "payload"}
    alerts = unsupported_alerts(summary)
    unsupported, rejected = alerts
    # set contextual metadata for later rendering
    unsupported.values["detected_dtype"] = "object"
    unsupported.column_name = "payload"
    rejected.values["reason"] = "unsupported_dtype"
    rejected.column_name = "payload"

3) Defensive error handling for unexpected constructor issues:
    try:
        alerts = unsupported_alerts({})
    except Exception as exc:
        # constructors for Alert subclasses may raise in rare conditions;
        # handle or log the error in the caller context
        logger.error("Failed to create default unsupported/rejected alerts: %s", exc)
        alerts = []

## `src.ydata_profiling.model.alerts.check_variable_alerts` · *function*

## Summary:
Orchestrates per-column alert construction: runs generic checks, delegates to unsupported/supported and type-specific alert generators, attaches the column name and the original description to every produced Alert, and returns the combined list.

## Description:
- Known callers and typical context:
    - The profiling pipeline's per-column alert aggregation stage (the routine that, after computing a column/variable summary/description, collects Alert objects for reporting).
    - Report builders or any higher-level code that needs an ordered list of Alert objects for a given column/variable summary.
    - Typical trigger: invoked once per variable after computing the variable's "description" (a dict of metrics and metadata) and with the global Settings object available.

- Responsibility boundary and rationale for extraction:
    - This function centralizes the orchestration of multiple small alert-producing helpers (generic_alerts, unsupported_alerts, supported_alerts, categorical_alerts, numeric_alerts, timeseries_alerts, boolean_alerts). It keeps the per-column alert assembly logic in one place instead of duplicating the calling order and metadata-attachment code throughout the codebase.
    - It enforces consistent finalization behavior by attaching the column_name and the original description dict to every returned Alert object, so downstream renderers receive uniform Alert instances.

## Args:
    config (Settings):
        - Must be an instance of ydata_profiling.config.Settings (or a compatible object) providing the configuration thresholds referenced by delegated helpers.
        - Required per-type expectations (delegated helpers rely on these attributes):
            * For categorical variables (when description["type"] == "Categorical"):
                - config.vars.cat.cardinality_threshold: numeric (int or float)
                - config.vars.cat.chi_squared_threshold: numeric (int or float)
                - config.vars.cat.imbalance_threshold: numeric (int or float)
            * For numeric/time-series variables:
                - config.vars.num.skewness_threshold: numeric (int or float)
                - config.vars.num.chi_squared_threshold: numeric (int or float)
            * For boolean variables:
                - config.vars.bool.imbalance_threshold: numeric (int or float)
        - Precondition: the numeric threshold attributes must exist and be comparable to the corresponding summary metrics; if missing or non-numeric, the delegated helper functions will raise AttributeError/TypeError.

    col (str):
        - The name of the column/variable being analyzed.
        - This string will be assigned to the column_name attribute of each produced Alert before returning.

    description (dict):
        - A per-variable summary/description mapping produced earlier in the profiling pipeline.
        - Required keys/expected values:
            * "type" (str): identifies the variable type and controls which type-specific functions run. Known expected values include:
                - "Unsupported"
                - "Categorical"
                - "Numeric"
                - "TimeSeries"
                - "Boolean"
            * Other keys depend on the helpers (e.g., "p_missing", "n", "n_distinct", "chi_squared", "stationary", "seasonal", etc.) and are consumed by the delegated alert-generator functions.
        - The function accesses description["type"] directly; leaving out "type" will raise KeyError.

    Notes on interdependencies:
        - config is only required by helpers that reference config thresholds; description is passed into helpers and later attached to every Alert as its .values attribute (overwriting any values set by helper constructors).

## Returns:
    List[Alert]:
        - A list containing zero or more Alert instances produced by the delegated helpers in the following sequence:
            1. Alerts returned by generic_alerts(description).
            2. If description["type"] == "Unsupported": alerts returned by unsupported_alerts(description).
               Else:
                a. Alerts returned by supported_alerts(description).
                b. If description["type"] == "Categorical": append categorical_alerts(config, description). Note: categorical_alerts requires the numeric threshold attributes listed above to be present and numeric.
                c. If description["type"] == "Numeric": append numeric_alerts(config, description). numeric_alerts requires config.vars.num.* thresholds.
                d. If description["type"] == "TimeSeries": append timeseries_alerts(config, description). timeseries_alerts in turn delegates to numeric_alerts and thus relies on numeric thresholds, and also expects "stationary" and "seasonal" keys in description.
                e. If description["type"] == "Boolean": append boolean_alerts(config, description). boolean_alerts requires config.vars.bool.imbalance_threshold.
        - Post-processing guarantee: for every Alert in the returned list:
            * alert.column_name == col
            * alert.values == description
        - Notes/edge cases:
            - If no helper returns any alerts, an empty list [] is returned.
            - Alerts returned by helpers that previously included their own .values content will have that content replaced by the original description dict because this function assigns alert.values = description for every alert before returning.

## Raises:
    - KeyError:
        - If description lacks the "type" key, description["type"] will raise KeyError.
        - Also possible if delegated helpers access required keys in description (e.g., supported_alerts may access description["n"]): such KeyError will propagate.
    - AttributeError:
        - If config is missing expected attributes accessed by delegated helpers (e.g., config.vars.cat.* or config.vars.num.*), AttributeError will propagate from those helpers.
    - TypeError / ValueError:
        - Delegated helpers may raise TypeError or ValueError when encountering unexpected types (for example, array-like values where scalars are expected). These exceptions propagate unchanged.
    - Any exception raised by helper functions or by Alert constructors will propagate to the caller.

## Constraints:
- Preconditions:
    - col must be a string (or at least an object acceptable to assign to Alert.column_name).
    - description must be a mapping containing the key "type" (string). The "type" value determines which type-specific checks run.
    - config must satisfy the expectations of the delegated helpers:
        * For "Categorical" variables: config.vars.cat.cardinality_threshold, config.vars.cat.chi_squared_threshold, and config.vars.cat.imbalance_threshold must exist and be numeric.
        * For "Numeric" or "TimeSeries" variables: config.vars.num.skewness_threshold and config.vars.num.chi_squared_threshold must exist and be numeric.
        * For "Boolean" variables: config.vars.bool.imbalance_threshold must exist and be numeric.
    - If these attributes are not present or not numeric, the delegated helper functions may raise AttributeError or TypeError.

- Postconditions:
    - The function returns a list of Alert objects (possibly empty).
    - Every returned Alert has its .column_name set to col and .values set to the original description dict (reference assigned; not a deep copy).
    - The function does not mutate config or description; it mutates the returned Alert objects (their attributes).

## Side Effects:
- Mutations:
    - The function mutates the Alert objects produced by helper functions by setting two attributes:
        - alert.column_name is set to col (may overwrite a prior column_name).
        - alert.values is set to description (this overwrites any values previously attached by helpers).
- I/O:
    - None. The function does not perform file, network, or stdout/stderr I/O.
- External state:
    - No global state, caches, or external services are modified.
    - Allocation of in-memory Alert objects occurs (created by helper functions).

## Control Flow:
flowchart TD
    Start([Start]) --> Init[alerts := []]
    Init --> Gen["alerts += generic_alerts(description)"]
    Gen --> TypeCheck{"description['type'] == 'Unsupported'?"}
    TypeCheck -- Yes --> Unsupported["alerts += unsupported_alerts(description)"]
    Unsupported --> FinalizeHelpers
    TypeCheck -- No --> Supported["alerts += supported_alerts(description)"]
    Supported --> BranchType

    BranchType --> CatCheck{"type == 'Categorical'?"}
    CatCheck -- Yes --> Cat["alerts += categorical_alerts(config, description)  \n(note: requires config.vars.cat.* numeric thresholds)"]
    CatCheck -- No --> AfterCat

    Cat --> AfterCat
    AfterCat --> NumCheck{"type == 'Numeric'?"}
    NumCheck -- Yes --> Num["alerts += numeric_alerts(config, description)  \n(note: requires config.vars.num.* numeric thresholds)"]
    NumCheck -- No --> AfterNum

    Num --> AfterNum
    AfterNum --> TsCheck{"type == 'TimeSeries'?"}
    TsCheck -- Yes --> Ts["alerts += timeseries_alerts(config, description)  \n(note: expects 'stationary' and 'seasonal' keys; delegates to numeric_alerts)"]
    TsCheck -- No --> AfterTs

    Ts --> AfterTs
    AfterTs --> BoolCheck{"type == 'Boolean'?"}
    BoolCheck -- Yes --> Bool["alerts += boolean_alerts(config, description)  \n(note: requires config.vars.bool.imbalance_threshold numeric)"]
    BoolCheck -- No --> AfterBool

    Bool --> AfterBool
    AfterBool --> FinalizeHelpers[Proceed to attach metadata to each alert]
    FinalizeHelpers --> LoopSet["for alert in alerts: alert.column_name = col; alert.values = description"]
    LoopSet --> Return["return alerts"]
    Return --> End([End])

    %% Error propagation branches (implicit)
    Gen -->|helper raises| Error[exceptions propagate]
    Unsupported -->|helper raises| Error
    Supported -->|helper raises| Error
    Cat -->|helper raises| Error
    Num -->|helper raises| Error
    Ts -->|helper raises| Error
    Bool -->|helper raises| Error

## Examples:
1) Typical (numeric column):
    - Given:
        * col = "age"
        * description = {"type": "Numeric", "skewness": 4.2, "p_infinite": 0.0, "p_zeros": 0.01}
        * config provides numeric thresholds used by numeric_alerts (config.vars.num.skewness_threshold etc.)
    - Behavior:
        * Start with alerts from generic_alerts(description) (e.g., maybe []).
        * Because type != "Unsupported", supported_alerts(description) runs (may append Unique/Constant alerts).
        * numeric_alerts(config, description) runs and may append SkewedAlert, ZerosAlert, etc.
        * Every produced Alert has .column_name set to "age" and .values set to the description dict.
        * Return the ordered list of Alert objects.

2) Categorical with missing thresholds (error case):
    - If description = {"type": "Categorical", ...} but config.vars.cat.cardinality_threshold is missing or not numeric:
        * categorical_alerts(config, description) may raise AttributeError or TypeError.
        * The exception propagates; callers should validate config before invoking this orchestration function.

3) Unsupported type:
    - Given description = {"type": "Unsupported", ...}
    - Behavior:
        * generic_alerts(description) runs.
        * unsupported_alerts(description) runs (returns canonical UnsupportedAlert and RejectedAlert).
        * Type-specific helpers are not invoked.
        * Returned alerts have column_name set to col and values set to the original description.

4) Important note about values overwriting:
    - Some helper functions construct Alerts with their own values payload (for example, numeric_alerts typically constructs SkewedAlert(summary) where summary is passed into the alert). check_variable_alerts will overwrite any helper-provided .values with description. If a helper expected its per-alert values to remain intact, callers should either:
        * mutate the Alert after this function returns to reattach richer metadata, or
        * change the helper to store metadata elsewhere (or change this orchestration to avoid overwriting).
    - The assignment alert.values = description assigns the same dict object provided as description (no copy).

5) Defensive usage (avoid KeyError):
    - Ensure description contains a "type" key before calling:
        * if "type" not in description: either supply a default or skip calling this function to avoid KeyError.

## `src.ydata_profiling.model.alerts.check_correlation_alerts` · *function*

## Summary:
Converts per-method correlation matrices into a list of HighCorrelationAlert objects for columns that exceed configured correlation thresholds — returning an alert per column that is highly correlated with one or more other columns.

## Description:
Known callers:
- No direct callers were present in the provided memory snapshot. Typical callers are the profiling pipeline's alert-aggregation stage or the correlation-checking step that collects results from correlation computations and turns them into reportable alerts. This function is expected to be invoked after one or more correlation matrices have been computed for a dataset (for example, Pearson, Spearman, or mutual-information correlation matrices).

When it runs:
- The function is executed during alert generation after correlation matrices are available and Settings contains per-correlation-type configuration (warn flag and threshold). It is responsible for mapping raw correlation detection output into typed alert objects that the rest of the reporting pipeline can consume.

Why this is a separate function:
- Responsibility separation: it isolates the logic that (1) consults Settings to decide which correlation checks are active, (2) applies a single detection function to each matrix (perform_check_correlation), (3) consolidates the results across correlation types, and (4) constructs HighCorrelationAlert instances. Keeping these steps in a dedicated function makes the pipeline easier to test and keeps detection (perform_check_correlation) and alert construction separate.

## Args:
    config (Settings):
        - Expected shape/contract: config must expose an attribute .correlations that is indexable by the keys present in the correlations dict passed to this function.
        - For each correlation key (e.g., "pearson", "spearman") config.correlations[corr] must provide:
            - warn_high_correlations (bool): when True, this correlation matrix will be checked and results converted to alerts.
            - threshold (float): numeric threshold passed to perform_check_correlation to decide what constitutes "high correlation".
        - Interdependencies: Every key in the correlations mapping that should be processed must have a corresponding config.correlations[...] entry; otherwise an indexing error occurs (see Raises).

    correlations (dict):
        - Type: dict[str, pandas.DataFrame]
        - Semantic: mapping from correlation-method-name to the correlation matrix for that method.
        - Required properties of each matrix:
            - Must behave like a pandas.DataFrame with .columns and .values attributes of a square correlation matrix.
            - perform_check_correlation will be called with this matrix and the configured threshold.

## Returns:
    List[Alert]
    - Each element is a HighCorrelationAlert instance (a subclass of Alert) representing a column found to be highly correlated with one or more other columns.
    - For each returned alert:
        - alert.column_name is the column (string) that has correlated other columns.
        - alert.values is a dict with exactly two keys in this implementation:
            - "corr": the string "overall" (the function uses the literal string "overall" for the corr value).
            - "fields": a list of column names (list[str]) returned by perform_check_correlation for the given column.
    - Possible return outcomes:
        - Empty list: no correlation matrices were processed (empty correlations dict), no warn_high_correlations flags were True, or perform_check_correlation returned no correlated pairs.
        - Non-empty list: one alert per distinct column appearing in the consolidated mapping. If a column appears in multiple correlation-method mappings, the last processed mapping for that column wins (see "Implementation notes / quirks").

## Raises:
    KeyError:
        - Condition: config.correlations[corr] fails because corr (a key from the correlations dict) is missing from config.correlations.
        - Condition: If perform_check_correlation raises a KeyError internally (rare — depends on its implementation and the matrix shape), it will propagate.

    AttributeError or TypeError:
        - Condition: If elements of correlations are not pandas.DataFrame-like (missing .values or .columns), performing correlation checks or boolean indexing in perform_check_correlation may raise AttributeError or TypeError; these propagate unchanged.

    Any exception raised by perform_check_correlation:
        - Condition: perform_check_correlation assumes a valid square correlation DataFrame and a numeric threshold; if these preconditions are violated, perform_check_correlation's exceptions (e.g., ValueError, IndexError) can propagate.

## Constraints:
Preconditions:
    - The correlations dict keys must correspond to entries available under config.correlations for those correlation methods that should be checked.
    - Each correlations[corr] must be a pandas.DataFrame-like square correlation matrix.
    - config.correlations[corr].threshold must be a numeric value and warn_high_correlations a bool.

Postconditions:
    - The returned list contains a HighCorrelationAlert instance for each column that perform_check_correlation reported as correlated for at least one enabled correlation method.
    - Each alert.values["fields"] is exactly the list returned by perform_check_correlation for that column from the last processed correlation method that produced an entry for that column (no de-duplication or set-union of fields across methods is performed by this implementation — see Implementation notes).

Implementation notes / quirks (important and intentional to document):
    - The code attempts to merge mutual correlations using a set update call, but written as set(fields).update(...). That expression creates and mutates a temporary set and does not mutate the original fields list or assign the merged set back. As a result, the effective stored fields are exactly the value returned by perform_check_correlation for that column (typically a list). If a column appears across multiple correlation-method mappings, the mapping assigned last in the iteration overwrites earlier entries for the same column.
    - The function always sets values["corr"] to the literal string "overall" (it does not record the original correlation method name or numeric value).

## Side Effects:
    - No I/O (no file, network, or stdout/stderr side effects).
    - No mutation of global state in this module.
    - Calls perform_check_correlation (purely computational function) for each enabled correlation matrix; side effects from that call depend only on perform_check_correlation (which is pure in the provided implementation).
    - The function returns newly constructed HighCorrelationAlert objects; it does not persist them.

## Control Flow:
flowchart TD
    Start --> IterateCorrelations
    IterateCorrelations -->|for each (corr, matrix)| CheckWarnFlag
    CheckWarnFlag -->|warn_high_correlations True| CallPerformCheck
    CheckWarnFlag -->|False| NextCorr
    CallPerformCheck --> CorrelatedMapping{perform_check_correlation -> mapping}
    CorrelatedMapping -->|for each (col, fields)| TrySetUpdate
    TrySetUpdate -->|creates temp set and updates| AssignToConsolidated
    AssignToConsolidated --> NextCol
    NextCol --> NextCorr
    NextCorr --> EndIter
    EndIter -->|if consolidated not empty| CreateAlerts
    CreateAlerts --> ReturnAlerts
    EndIter -->|if consolidated empty| ReturnEmpty
    ReturnAlerts --> End
    ReturnEmpty --> End

## Examples:
1) Typical (happy path):
    - Preconditions are met: config has per-method settings and correlations contains DataFrame matrices.
    - Example usage summary:
        - Prepare computed correlation matrices: correlations = {"pearson": pearson_corr_df, "spearman": spearman_corr_df}
        - Ensure config.correlations["pearson"].warn_high_correlations is True and threshold is set.
        - Call: alerts = check_correlation_alerts(config, correlations)
        - Result: alerts is a list of HighCorrelationAlert instances; for each alert, alert.values["fields"] is the list of correlated columns detected for that alert.column_name.

2) Defensive usage with error handling:
    - If correlation method entries in config may be missing, guard the call:
        - Wrap call in try/except KeyError to detect missing configuration for any correlations keys.
        - If any input matrix might be malformed, guard with a broad except (TypeError, AttributeError, ValueError) and log an informative error describing which correlation method failed.

3) Example of returned alert content (conceptual, not raw code):
    - Suppose perform_check_correlation for "pearson" returned {"A": ["B", "C"], "D": ["E"]}
    - The function produces two alerts:
        - HighCorrelationAlert(column_name="A", values={"corr": "overall", "fields": ["B", "C"]})
        - HighCorrelationAlert(column_name="D", values={"corr": "overall", "fields": ["E"]})
    - Note: "corr" is the literal string "overall" and does not contain numeric correlation values or the original method name.

## `src.ydata_profiling.model.alerts.get_alerts` · *function*

## Summary:
Aggregate dataset-, variable-, and correlation-level checks into a single ordered list of Alert objects representing all detected issues for a profiling run.

## Description:
- Known callers and typical context:
    - Called by the profiling pipeline's alert aggregation or report-building stage after table-level metrics, per-variable descriptions, and correlation matrices have been computed.
    - Typical trigger: invoked once after computing all statistics for a dataset to produce the final list of alerts that will be displayed in reports or used for downstream checks.

- Why this function is separate:
    - Serves as the orchestration point that composes the three kinds of alert producers (table-level, variable-level, correlation-level) into a single, consistently ordered list.
    - Keeps high-level assembly logic out of lower-level detectors (which focus on single rules), improving reuse and testability.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings (or compatible object).
        - Role: configuration and thresholds used by delegated per-variable and correlation checks (passed through to check_variable_alerts and check_correlation_alerts).
        - Preconditions: must provide any configuration attributes required by delegated functions (e.g., config.vars.* thresholds, config.correlations entries for enabled correlation checks).

    table_stats (dict):
        - Type: mapping-like object (dict) describing dataset-level summary metrics (the "table" metrics).
        - Expected keys/values:
            * "n" (int-like): total number of rows; check_table_alerts reads it directly and will raise KeyError if missing.
            * Optional keys used by table-level checks (e.g., "n_duplicates", "p_duplicates").
        - Notes: If table_stats is malformed (missing "n" or not a mapping), check_table_alerts may raise KeyError or TypeError.

    series_description (dict):
        - Type: mapping from column name (str) to per-variable description (dict).
        - Each description dict is expected to include a "type" key (str) that determines type-specific checks (e.g., "Numeric", "Categorical", "TimeSeries", "Boolean", "Unsupported").
        - Notes: check_variable_alerts will raise KeyError if a description lacks "type", and delegated helpers may raise other exceptions for missing keys.

    correlations (dict):
        - Type: mapping from correlation-method name (str) to a pandas.DataFrame-like correlation matrix.
        - Each key present here that should be processed must have a corresponding entry under config.correlations with a warn flag and threshold.
        - Notes: malformed matrices or missing config entries can cause exceptions in check_correlation_alerts or perform_check_correlation.

## Returns:
    List[Alert]:
        - A list containing all Alert objects produced by the three detectors, combined and sorted by their alert_type string representation.
        - Composition:
            1. Alerts from check_table_alerts(table_stats) (dataset-level alerts).
            2. For each (col, description) in series_description.items(): alerts returned by check_variable_alerts(config, col, description). Each returned Alert will have its .column_name set to col and .values set to the description dict (this mutation occurs inside check_variable_alerts).
            3. Alerts from check_correlation_alerts(config, correlations) (high-correlation alerts).
        - Sorting:
            - The final list is sorted in-place with key=lambda alert: str(alert.alert_type) before returning.
        - Edge cases:
            - If no checks produce alerts the function returns an empty list [].
            - Returned Alert objects may be mutated (their .column_name and .values are set by helper functions); the function itself does not deep-copy inputs.

## Raises:
    - Propagated exceptions from delegated functions:
        - KeyError:
            * Possible conditions:
                - table_stats missing "n" (check_table_alerts uses table["n"] directly).
                - A variable description missing "type" (check_variable_alerts accesses description["type"]).
                - A correlation method key present in correlations but missing from config.correlations (check_correlation_alerts accesses config.correlations[corr]).
        - AttributeError / TypeError / ValueError:
            * Possible conditions from malformed inputs (non-mapping table_stats, non-dict descriptions, non-DataFrame correlation matrices) or missing numeric config thresholds used by delegated helpers.
        - Any other exception raised by check_table_alerts, check_variable_alerts, check_correlation_alerts, or perform_check_correlation will propagate unchanged.
    - The function performs no additional error handling — callers should wrap this call if they need to handle specific errors.

## Constraints:
- Preconditions (caller responsibilities):
    - config must expose the attributes required by delegated helpers (vars.* thresholds and config.correlations entries for active correlation methods).
    - table_stats must be a mapping that includes "n".
    - series_description must be a mapping of column_name -> description dict and each description must include "type".
    - correlations must map method names to pandas.DataFrame-like square correlation matrices when correlation checks are enabled.

- Postconditions (what the function guarantees):
    - Returns a list of Alert objects representing dataset-, variable-, and correlation-level findings.
    - The returned list is sorted by the stringified alert_type.
    - The function does not modify input mappings (table_stats, series_description, correlations) themselves, but Alert objects created by helper functions may have .values and .column_name attributes assigned (this mutation is part of the helper behavior).

## Side Effects:
    - No external I/O (no files, network, or stdout/stderr writes).
    - In-memory effects:
        - Allocation of Alert objects produced by helper functions; check_variable_alerts mutates those Alert objects by setting .column_name and .values.
    - No global state mutations are performed by get_alerts itself. Any side effects are those performed by the delegated helper functions (see their docs).

## Control Flow:
flowchart TD
    Start([Start]) --> TableAlerts[alerts := check_table_alerts(table_stats)]
    TableAlerts --> IterateCols
    IterateCols -->|for each col,description| VarAlerts["alerts += check_variable_alerts(config, col, description)"]
    VarAlerts --> LoopEnd{more columns?}
    LoopEnd -- Yes --> IterateCols
    LoopEnd -- No --> CorrAlerts[alerts += check_correlation_alerts(config, correlations)]
    CorrAlerts --> SortAlerts[alerts.sort(key=lambda alert: str(alert.alert_type))]
    SortAlerts --> ReturnAlerts[return alerts]
    ReturnAlerts --> End([End])

## Examples:
1) Typical usage (happy path):
    - Preconditions:
        * config: valid Settings with vars.* thresholds and config.correlations entries for methods in correlations.
        * table_stats: {"n": 1000, "n_duplicates": 3, "p_duplicates": 0.003}
        * series_description: {
            "age": {"type": "Numeric", "n": 1000, "p_missing": 0.0, ...},
            "country": {"type": "Categorical", "n_distinct": 20, ...}
          }
        * correlations: {"pearson": pearson_df}
    - Invocation:
        alerts = get_alerts(config, table_stats, series_description, correlations)
    - Result:
        - alerts is a list of Alert objects produced by table-level checks, per-column checks (each with .column_name set and .values set to that column's description), and correlation checks; the list is sorted by alert_type string.

2) Defensive usage with error handling:
    - If a caller cannot guarantee inputs, wrap and handle exceptions:
        try:
            alerts = get_alerts(config, table_stats, series_description, correlations)
        except KeyError as e:
            # Handle missing required keys (e.g., table_stats["n"] or description["type"])
            log_error("Missing required metric", key=e.args[0])
            alerts = []
        except (TypeError, AttributeError, ValueError) as e:
            # Handle malformed inputs (e.g., non-mapping table_stats or bad correlation matrix)
            log_error("Malformed profiling inputs", detail=str(e))
            raise

3) Minimal example (no alerts produced):
    - If table_stats, series_description, and correlations produce no alerts:
        - The function returns [].

Notes for implementers/readers:
    - This function does minimal work itself — it orchestrates existing detectors. To reason about specific alert production, consult the documentation for:
        - check_table_alerts (table-level detectors)
        - check_variable_alerts (per-variable detectors; note it mutates produced Alert objects)
        - check_correlation_alerts (correlation detectors; relies on perform_check_correlation)
    - Sorting at the end is deterministic only to the extent that str(alert.alert_type) yields stable string representations for AlertType members.

## `src.ydata_profiling.model.alerts.alert_value` · *function*

## Summary:
Return True when a scalar float is not missing and strictly greater than 0.01; otherwise return False.

## Description:
This small predicate enforces a scalar alert rule by combining a missing-value check with a numeric threshold test. It evaluates, in order:
1. pd.isna(value) — to determine whether the input is missing/NA.
2. If not missing, the numeric comparison value > 0.01.

Known callers within the codebase:
    - None discovered during this documentation scan. The function is intended for use by higher-level alerting or metric-evaluation code that needs a consistent scalar predicate for "notable" numeric values.

Responsibility boundary:
    - Encapsulates the specific decision rule (missing-value exclusion and threshold 0.01) so callers do not duplicate the logic. It is intentionally a scalar predicate and not a vectorized/array-aware routine.

Important dependency:
    - The implementation calls pd.isna(value). The module namespace must provide the symbol pd (usually pandas imported as pd). If pd is not defined in the module, invoking this function will raise NameError.

## Args:
    value (float):
        - The scalar numeric value to evaluate.
        - Matches the function signature annotation exactly: the function expects a float.
        - Required positional argument (no default).
        - Callers should pass a scalar float; passing array-like or incompatible types may lead to exceptions as described below.

## Returns:
    bool:
        - True when pd.isna(value) is False (value is present) AND value > 0.01.
        - False when pd.isna(value) is True (value is missing) OR value <= 0.01.
        - Always returns a Python bool for scalar inputs.

## Raises:
    - NameError: If the module does not define pd (the function calls pd.isna).
    - ValueError: If value is array-like (e.g., numpy.ndarray or pandas.Series), pd.isna(value) typically returns array/Series booleans and Python's logical operators with array-like booleans can raise an ambiguous truth-value ValueError.
    - TypeError: If value is not comparable with a float using > and the comparison is reached (i.e., pd.isna(value) returned False).
    - Note: The function does not explicitly raise exceptions; the listed errors arise from underlying operations and input types.

## Constraints:
Preconditions:
    - The module must expose pd.
    - The caller should pass a scalar float value.

Postconditions:
    - The function returns a Python bool.
    - No external state is modified.

## Side Effects:
    - None. The function performs pure computation only; no I/O or external side effects.

## Control Flow:
flowchart TD
    Start --> IsMissing{pd.isna(value) == True?}
    IsMissing -- Yes --> ReturnFalse[Return False]
    IsMissing -- No --> IsGreater{value > 0.01?}
    IsGreater -- Yes --> ReturnTrue[Return True]
    IsGreater -- No --> ReturnFalse

## Examples:
Illustrative scalar inputs and outcomes:
    - value = 0.02  -> True
    - value = 0.01  -> False
    - value = 0.0   -> False
    - value = float('inf') -> True
    - value = float('nan') -> False (pd.isna returns True; comparison is skipped)

Invalid usage notes:
    - Passing numpy.array([0.02]) or pandas.Series([0.02]) to value may raise an exception due to ambiguous truth-value handling; for array/Series inputs use vectorized checks instead (for example, (~series.isna()) & (series > 0.01)).

## `src.ydata_profiling.model.alerts.skewness_alert` · *function*

## Summary:
Returns whether a numeric skewness value is outside the allowed symmetric threshold (i.e., sufficiently large positive or negative skew) and is not missing.

## Description:
This small predicate is intended to be used when checking whether a computed skewness statistic for a variable should trigger an alert because it is unusually large in magnitude. It returns True only when the skewness value is present (not missing) and its magnitude exceeds the provided threshold.

Known callers within the provided code context:
    - No direct callers were discovered in the provided file fragment. In typical usage across profiling pipelines, this function is called after computing a skewness metric for a variable (for example, within an alerts-generation step that inspects variable-level statistics), to decide whether to mark that variable with a "high skewness" alert.

Why this logic is extracted into its own function:
    - Encapsulates the simple, repeatable decision rule (present AND magnitude > threshold) so the check can be reused consistently wherever skewness-based alerts are needed without repeating the same boolean expression in multiple places. It keeps alert decision logic separated from metric computation and reporting code.

## Args:
    v (float):
        The skewness value to evaluate. The function expects a numeric value (Python float, numpy.float64, or similar). The function first checks for missingness with pandas.isna; if v is missing (NaN/None) the function returns False.
    threshold (int):
        The symmetric, numeric threshold for triggering the alert. A non-negative integer is expected: the alert fires when v < -threshold or v > threshold. The function does not coerce or validate threshold; passing a negative threshold will change semantics (see Constraints).

Notes on interdependency:
    - The decision uses the sign-aware comparison v < (-1 * threshold) or v > threshold, which effectively triggers on absolute magnitude greater than threshold but preserves symmetric bounds. The code relies on pandas' isna check for detecting missing values (pd.isna).

## Returns:
    bool:
        True if and only if:
            - v is not missing (pandas.isna(v) is False), and
            - v is strictly less than -threshold OR strictly greater than threshold.
        Otherwise False.

Possible return outcomes and examples:
    - Returns False for missing values (NaN, None) because missingness suppresses alerts.
    - Returns True for v = 3.5 with threshold = 3 (3.5 > 3).
    - Returns True for v = -4 with threshold = 3 (-4 < -3).
    - Returns False for v = 2 with threshold = 3 (|2| <= 3).

## Raises:
    - The function itself contains no explicit raise statements.
    - It may raise a NameError if the pandas isna function is not available under the name used inside the module (the implementation calls pd.isna). In a correctly imported module this will not occur (pandas.isna should be available, typically via import pandas as pd).

## Constraints:
Preconditions:
    - The caller should provide a numeric-like value for v (float, numpy number) or a missing value placeholder that pandas.isna recognizes (None, numpy.nan).
    - The caller should supply a threshold that reflects the intended symmetric bound; threshold is expected to be non-negative for the intended semantics.

Postconditions:
    - The function returns a boolean and does not mutate its inputs or any external state.
    - No I/O or side effects are performed.

## Side Effects:
    - None. The function performs only pure evaluation and returns a boolean.
    - No file, network, stdout operations, or external state mutations are performed.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckMissing{pd.isna(v) == True?}
    CheckMissing -- Yes --> ReturnFalseMissing([Return False])
    CheckMissing -- No --> CompareLower{v < (-1 * threshold)?}
    CompareLower -- Yes --> ReturnTrueLower([Return True])
    CompareLower -- No --> CompareUpper{v > threshold?}
    CompareUpper -- Yes --> ReturnTrueUpper([Return True])
    CompareUpper -- No --> ReturnFalse([Return False])

## Examples:
    - Typical usage in a profiling/alerting pipeline:
        * compute skewness for a variable (skew_val)
        * call skewness_alert(skew_val, threshold=3)
        * if True, attach a "high skewness" alert to the variable's report.

    Example scenarios (conceptual):
        - skewness_alert(4.2, 3)  -> True   (present and > threshold)
        - skewness_alert(-3.5, 3) -> True   (present and < -threshold)
        - skewness_alert(2.0, 3)  -> False  (present but magnitude <= threshold)
        - skewness_alert(None, 3) -> False  (missing value suppressed)

Notes:
    - Because the function uses a pandas isna check, it accepts any value that pandas.isna recognizes as missing. To avoid unexpected behavior, ensure pandas is imported appropriately in the module scope (the implementation uses pd.isna).

## `src.ydata_profiling.model.alerts.type_date_alert` · *function*

## Summary:
Determines whether applying dateutil.parser.parse to every element of a pandas Series completes without raising a ParserError; returns True if so, otherwise returns False.

## Description:
Applies dateutil.parser.parse to each element in the provided pandas.Series using pandas.Series.apply. If any application raises dateutil.parser.ParserError, the function catches that exception and returns False. If parse completes for all elements without raising ParserError, the function returns True.

Known callers:
    - No direct callers were discovered in the provided repository snapshot.
    - Typical use case: used in data-profiling or alert-generation logic to validate whether a column is entirely date-like before assigning a date/time type or raising a date-type related alert.

Why this is extracted:
    - Encapsulates the single responsibility "can all elements be interpreted as dates" and centralizes exception handling for ParserError so callers can rely on a simple boolean result rather than duplicating parsing-and-exception-handling logic.

## Args:
    series (pandas.Series): Sequence of values to test for date-parseability.
        - Expected element values: strings or objects that dateutil.parser.parse can accept.
        - The function accepts any pandas.Series; other types may raise attribute errors before parsing.

## Returns:
    bool:
        - True: dateutil.parser.parse was applied to every element and no dateutil.parser.ParserError was raised (including the case of an empty Series).
        - False: a dateutil.parser.ParserError was raised while parsing one or more elements (the function catches this and returns False).
    Notes:
        - The function makes no attempt to report which elements failed — it only returns a boolean summary.
        - If an exception other than ParserError is raised during apply/parse, it is not caught by this function and will propagate to the caller.

## Raises:
    - This function does not raise ParserError (it is caught and converted to False).
    - Any other exception raised by pandas.Series.apply or by dateutil.parser.parse (for example, attribute errors if a non-Series is passed) will propagate unchanged to the caller.

## Constraints:
    Preconditions:
        - The argument must be a pandas.Series (or behave like one with an apply method taking a unary function).
        - Callers who require deterministic handling of missing values (None, numpy.nan) should pre-clean the Series (for example, dropna() or cast elements to str) because such values may cause parse to raise exceptions depending on the value and the dateutil version.

    Postconditions:
        - The input Series is not modified in-place.
        - On normal completion (no non-ParserError exception), the function returns a boolean value (True or False).

## Side Effects:
    - No file, network, or stdout I/O.
    - No global state mutation.
    - No external service calls.
    - Performance: linear scan over the Series (O(n) calls to parse). For large Series this can be CPU- and memory-intensive.

## Control Flow:
flowchart TD
    Start --> ApplyParse[series.apply(dateutil.parser.parse)]
    ApplyParse --> |ParserError raised during apply| ReturnFalse[Return False]
    ApplyParse --> |No ParserError raised for any element| ReturnTrue[Return True]
    ReturnFalse --> End[End]
    ReturnTrue --> End

## Examples:
    Example — all parseable values:
        Input: a Series containing "2020-01-01", "2021-12-31"
        Outcome: parse succeeds for every element -> function returns True

    Example — an unparseable value:
        Input: a Series containing "2020-01-01", "not-a-date"
        Outcome: parse("not-a-date") raises ParserError -> function catches it and returns False

    Example — empty Series:
        Input: an empty Series (no elements)
        Outcome: apply runs no element calls and no ParserError is raised -> function returns True

    Example — defensive callers:
        If callers want to avoid any non-ParserError exceptions caused by missing values or unexpected types, they can pre-clean:
            - series_clean = series.dropna().astype(str)
            - result = type_date_alert(series_clean)
        This ensures the function's boolean return is reached rather than letting other exceptions propagate.

