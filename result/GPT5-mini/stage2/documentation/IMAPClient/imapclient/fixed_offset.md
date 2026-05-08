# `fixed_offset.py`

## `imapclient.fixed_offset.FixedOffset` · *class*

## Summary:
Represents a fixed-offset timezone (subclass of datetime.tzinfo) whose UTC offset is a constant number of minutes and which never observes daylight saving time.

## Description:
FixedOffset is a minimal tzinfo implementation for use when you need a timezone that is a fixed number of minutes east or west of UTC. Instantiate it with a minute offset (can be integer or float) to obtain a timezone object whose utcoffset() returns that fixed timedelta, whose tzname() returns a precomputed "+HHMM"/"-HHMM" string, and whose dst() always returns the module ZERO sentinel (no DST). Typical scenarios:
- Creating timezone-aware datetimes for protocols, logs, or I/O where the offset is known and does not observe DST.
- Converting naive datetimes to a fixed local offset.
- Obtaining the current system local offset via FixedOffset.for_system().

Known factories / callers:
- FixedOffset.for_system() — classmethod that inspects the host system time settings and returns a FixedOffset representing the current local timezone offset.
- Any application code or library that attaches a tzinfo to a datetime (e.g., datetime.replace(tzinfo=FixedOffset(...))) or that queries tzinfo.utcoffset/tzname/dst.

Responsibility boundary:
- Provides only a fixed offset tzinfo; it does not compute DST or follow historical timezone rules. For full IANA timezone support, use a zoneinfo / pytz-like implementation instead.

## State:
Attributes (instance-level)
- __offset (datetime.timedelta)
  - Type: datetime.timedelta
  - Meaning: the fixed offset from UTC represented as a timedelta of the minutes argument passed to __init__.
  - Valid range/values: any timedelta that can be constructed from the provided minutes value; extremes may raise an exception (see Raises).
  - Invariant: utcoffset(dt) returns this exact timedelta for any dt.

- __name (str)
  - Type: str
  - Meaning: a precomputed timezone name formatted as a sign followed by two zero-padded digits for hours and two zero-padded digits for minutes, e.g. "+0200", "-0530".
  - Valid values: string matching the pattern /^[+-]\d{4}$/ produced from the absolute minute count given to __init__.
  - Invariant: tzname(dt) returns this exact string for any dt.

Notes about name-mangling:
- These attributes are defined with double-underscore names; under the hood they are name-mangled (e.g., _FixedOffset__offset). Treat them as private implementation details.

Class-level constants referenced:
- ZERO (module-level): a datetime.timedelta instance representing zero offset used as the DST sentinel. (The dst() implementation always returns this module sentinel.)

Class invariants:
- __offset and __name must be set during initialization and remain immutable for the lifetime of the instance.
- utcoffset(), tzname(), and dst() do not mutate instance state.

## Lifecycle:
Creation:
- Constructor: FixedOffset(minutes)
  - Required argument: minutes (float or int) — number of minutes east (positive) or west (negative) of UTC. Example: -300 for UTC-5.
  - Alternate factory: FixedOffset.for_system() constructs a FixedOffset reflecting the current system local offset in whole minutes.

Usage:
- Typical call sequence:
  1. Instantiate FixedOffset (directly or via for_system()).
  2. Attach to a datetime or use directly where a tzinfo is required.
  3. Consumers call utcoffset(dt) to get the timedelta, tzname(dt) to get the name string, and dst(dt) to check DST (always ZERO).
- Ordering / sequencing:
  - There is no required ordering between utcoffset, tzname, and dst calls; they are independent and read-only.
  - No initialization step beyond construction is required.

Destruction / cleanup:
- No cleanup required. Instances hold only simple Python objects (timedelta and str). They do not open resources, do network I/O, or implement context management.

## Method Map:
- High-level call graph (Mermaid flowchart):

graph LR
    A[User or code] -->|FixedOffset(minutes)| B[FixedOffset.__init__]
    C[User or code] -->|FixedOffset.for_system()| D[FixedOffset.for_system]
    D -->|calls| B
    B --> E[sets __offset, __name]
    E --> F[utcoffset(dt)]
    E --> G[tzname(dt)]
    E --> H[dst(dt)]
    F -->|returns| I[datetime.timedelta (__offset)]
    G -->|returns| J[str (__name)]
    H -->|returns| K[ZERO (timedelta(0))]

(Interpretation: for_system calls time module helpers and instantiates FixedOffset which sets internal state. utcoffset/tzname/dst are read-only accessors that return the stored values or ZERO.)

## Methods (behavior summary)
- __init__(minutes: float)
  - Constructs the instance state:
    - __offset = datetime.timedelta(minutes=minutes)
    - __name = formatted sign + two-digit hours + two-digit minutes derived from abs(minutes)
  - The minutes argument is the authoritative source; __offset and __name are deterministically derived from it.

- utcoffset(dt: Optional[datetime.datetime]) -> datetime.timedelta
  - Returns the precomputed __offset for any dt (parameter ignored). Useful for datetime arithmetic and conversions.

- tzname(dt: Optional[datetime.datetime]) -> str
  - Returns the precomputed __name for any dt (parameter ignored). Useful for display and formatting.

- dst(dt: Optional[datetime.datetime]) -> datetime.timedelta
  - Returns the module ZERO sentinel (no DST). Always constant and does not depend on dt.

- for_system() -> FixedOffset (classmethod)
  - Inspects the system time settings:
    - If time.localtime().tm_isdst and time.daylight: uses time.altzone
    - Else: uses time.timezone
  - time.timezone / time.altzone are seconds west of UTC; the method negates that value and integer-divides by 60 (//) to obtain minutes east of UTC, and constructs cls(computed_minutes).
  - Returns a new FixedOffset (or subclass) instance representing the system's current local offset in whole minutes.

## Raises:
Constructor (__init__)
- TypeError
  - If the provided minutes value is not a numeric type that datetime.timedelta accepts (e.g., passing a completely unrelated object), datetime.timedelta or subsequent operations may raise TypeError.
- OverflowError
  - If the minutes value is so large or small that datetime.timedelta cannot represent the resulting timedelta, datetime.timedelta(...) may raise OverflowError.
- Value / formatting issues
  - The tzname formatting assumes that dividing the absolute minutes into hours/minutes produces integer-like values. If a non-integer minutes value is provided, formatting behavior depends on Python's handling of numeric-to-integer formatting (callers should prefer whole-minute values).

for_system()
- Propagates errors from the time module if the platform is non-standard (missing attributes), and propagates any exceptions raised by cls(...) (constructor errors as above).

Accessors (utcoffset, tzname, dst)
- AttributeError
  - If an instance is used before successful construction (highly unusual), attempting to call utcoffset or tzname may raise AttributeError because __offset or __name are missing. Under normal usage (after __init__), these methods do not raise.

## Example (narrative):
- Create a fixed timezone for UTC-5 (Eastern Standard Time without DST):
  1. Instantiate with minutes = -300.
  2. Use the returned FixedOffset as the tzinfo for a datetime.
  3. utcoffset(dt) will return datetime.timedelta(minutes=-300).
  4. tzname(dt) will return "-0500".
  5. dst(dt) will return ZERO (no DST offset).

- Obtain system local offset:
  1. Call FixedOffset.for_system().
  2. The method inspects time.localtime().tm_isdst and time.daylight to pick time.altzone or time.timezone.
  3. It computes minutes = -offset_seconds // 60 and returns cls(minutes).
  4. Use the returned FixedOffset as above.

Usage notes and constraints:
- Prefer passing whole-minute integer values to __init__ for predictable tzname formatting.
- This class is intended for simple fixed-offset scenarios only; for full timezone rules (historical DST and region-specific changes) use a zoneinfo or pytz implementation.

### `imapclient.fixed_offset.FixedOffset.__init__` · *method*

## Summary:
Compute and store a fixed UTC offset and a preformatted timezone name based on the supplied minute offset so the instance's utcoffset and tzname accessors can return those values cheaply.

## Description:
This constructor runs during object creation (FixedOffset(minutes)) to establish the instance's immutable state: a datetime.timedelta representing the offset and a human-readable tzname string derived from that offset. It is typically called:
- Directly by application code when creating a fixed-offset tzinfo to attach to datetimes.
- Indirectly by FixedOffset.for_system(), which computes the system local offset (in whole minutes) and instantiates FixedOffset.

This logic is implemented in the constructor to ensure utcoffset(), tzname(), and dst() can be simple, read-only accessors that do not recompute formatting or arithmetic on each call.

## Args:
    minutes (float):
        Number of minutes east (positive) or west (negative) of UTC.
        - Signature type: float (the implementation accepts numeric types supported by datetime.timedelta).
        - Expected / recommended: whole-minute integer values (e.g., -300 for UTC−5) to guarantee predictable tzname formatting.

## Returns:
    None
    - The constructor returns None; its effect is side-effecting on the instance (setting attributes).

## Raises:
    TypeError
        - Raised by datetime.timedelta(minutes=minutes) if minutes is not a numeric type accepted by datetime.timedelta.
        - The implementation formats hours and remaining minutes using integer format codes ("%02d%02d"). If hours or remaining_mins are non-integers (which occurs when minutes is not a whole integer), applying the formatting expression may raise TypeError on typical Python implementations. To avoid this, pass integer minute values.
    OverflowError
        - Raised by datetime.timedelta(...) when the supplied minutes value is too large in magnitude for a timedelta to represent.

## State Changes:
Attributes READ:
    - None on self (constructor uses only the minutes argument).
Attributes WRITTEN:
    - self.__offset (datetime.timedelta) — stored as the name-mangled attribute _FixedOffset__offset:
        - Set to datetime.timedelta(minutes=minutes).
    - self.__name (str) — stored as the name-mangled attribute _FixedOffset__name:
        - Computed by:
            1. sign = "+" (set to "-" if minutes < 0)
            2. hours, remaining_mins = divmod(abs(minutes), 60)
            3. self.__name = "%s%02d%02d" % (sign, hours, remaining_mins)

Note: divmod on a float minutes produces float results for hours and remaining_mins; the code formats those values using integer format specifiers.

## Constraints:
Preconditions:
    - The caller must supply a numeric value acceptable to datetime.timedelta as the minutes parameter.
    - Prefer whole-minute integer arguments to ensure hours and remaining_mins are integers for formatting.

Postconditions:
    - After successful return:
        - _FixedOffset__offset is a datetime.timedelta equal to the provided minutes expressed as minutes.
        - _FixedOffset__name is a string composed of the sign and two zero-padded integer fields for hours and minutes as produced by the formatting expression in the implementation. There is no enforced fixed-length guarantee for the resulting string if hours exceed two digits.

## Edge cases and implementation notes:
    - Fractional minutes: If minutes is non-integer (e.g., 90.5), hours and remaining_mins will be floats; the formatting expression in the code expects integers and therefore may raise TypeError. The implementation as written does not round or coerce fractional minutes — callers should avoid them.
    - Large offsets: If the absolute hours portion exceeds two digits, the formatted tzname will be longer than 5 characters (e.g., "+10000" for very large offsets). The implementation does not clamp or limit hour width.
    - Name-mangling: Instance attributes are defined with double-underscores; the concrete attribute names at runtime are _FixedOffset__offset and _FixedOffset__name.

## Side Effects:
    - No I/O or global state changes.
    - Allocates a datetime.timedelta and a str and stores them on the instance.
    - Any exceptions (TypeError, OverflowError) are raised synchronously during construction.

### `imapclient.fixed_offset.FixedOffset.utcoffset` · *method*

## Summary:
Return the fixed timezone offset as a datetime.timedelta; this does not modify object state.

## Description:
This implements the tzinfo.utcoffset interface for FixedOffset and returns the constant offset that was established when the FixedOffset instance was constructed. It is invoked by consumers of the tzinfo protocol (for example, Python's datetime machinery and any code that queries an aware datetime's offset) during timezone-aware arithmetic, formatting, or conversions. There are no internal callers inside this module; the method exists to fulfill the tzinfo contract so FixedOffset instances can be used wherever a tzinfo object is required.

This logic is kept as its own small method because it is the required hook of the tzinfo interface. Keeping it separate (and trivial) makes the timezone object's behavior explicit, testable, and compatible with the datetime standard library expectations.

## Args:
    _ (Optional[datetime.datetime]): The datetime for which the offset is requested. This parameter is accepted to match the tzinfo.utcoffset signature but is ignored by this implementation. Callers may pass a datetime or None.

## Returns:
    datetime.timedelta: The fixed offset stored on the instance (self.__offset). The returned timedelta may be positive, zero, or negative depending on how the FixedOffset was constructed (minutes value passed to __init__). The method returns the same timedelta object held in the instance (self.__offset).

## Raises:
    AttributeError: If the instance was not properly initialized and does not have the __offset attribute. In normal usage (after __init__), this method does not raise.

## State Changes:
    Attributes READ:
        self.__offset
    Attributes WRITTEN:
        (none) — the method does not modify any attributes.

## Constraints:
    Preconditions:
        - The FixedOffset instance must have been constructed via FixedOffset.__init__, which sets self.__offset to a datetime.timedelta based on the provided minutes.
        - The caller may supply any datetime or None for the parameter; the value is ignored.
    Postconditions:
        - No mutation of self occurs.
        - The returned value is a datetime.timedelta representing the fixed offset and will remain equal to the instance's __offset until the object is discarded.

## Side Effects:
    - None. The method performs no I/O, external calls, or mutations to objects other than returning the stored timedelta.

### `imapclient.fixed_offset.FixedOffset.tzname` · *method*

## Summary:
Returns the precomputed timezone name string for this FixedOffset instance (no state change).

## Description:
This method implements the tzname(dt) part of the datetime.tzinfo interface and simply returns the string assembled when the FixedOffset object was constructed. Known callers include the Python datetime machinery (for example when formatting, converting, or displaying timezone-aware datetimes) and any library code that queries a tzinfo object's tzname. In this codebase the method is used indirectly whenever a FixedOffset instance is attached to a datetime and the datetime API requests the zone name.

The logic is a separate method because tzinfo defines tzname as part of its interface; the FixedOffset implementation returns a fixed, precomputed value rather than computing it per-call, so separating it keeps the interface implementation minimal and avoids duplicating string-formatting logic elsewhere.

## Args:
    _: Optional[datetime.datetime]
        - The datetime for which a name could be requested.
        - Allowed values: a datetime.datetime instance or None.
        - Note: this parameter is intentionally unused by FixedOffset; its presence only satisfies the tzinfo API.

## Returns:
    str
        - The timezone name string computed in __init__, formatted as a sign followed by two-digit hours and two-digit minutes (e.g. "+0200" or "-0530").
        - Always returns the same string for a given FixedOffset instance.
        - Edge cases: if the object was not constructed correctly (see Preconditions), the return value may not be a valid timezone-name string.

## Raises:
    - This method does not raise exceptions under normal operation.
    - An AttributeError will occur if the instance was not properly initialized and self.__name does not exist.

## State Changes:
    Attributes READ:
        - self.__name
    Attributes WRITTEN:
        - None (method is read-only)

## Constraints:
    Preconditions:
        - The FixedOffset instance must have been constructed so that self.__name exists and is a string. Effectively, __init__ must have been called with a minutes value that resulted in a valid __name assignment.
        - Because __name is built with integer formatting in __init__, callers should ensure FixedOffset was created with a whole-minute offset (typical usage provides an integer minute count).

    Postconditions:
        - No change to self; the method guarantees self.__name remains unchanged.
        - The returned string equals the value computed and stored in __init__.

## Side Effects:
    - None: no I/O, no external calls, and no mutations to objects outside self.

### `imapclient.fixed_offset.FixedOffset.dst` · *method*

## Summary:
Implements the tzinfo.dst interface by returning the module's ZERO timedelta sentinel, indicating this fixed-offset timezone has no daylight saving offset. The call does not modify the object's state.

## Description:
This method fulfills the datetime.tzinfo.dst contract for FixedOffset (a subclass of datetime.tzinfo). It is invoked whenever code (the Python datetime machinery or application code) queries the daylight saving time offset for a datetime expressed in this timezone — for example when converting between time zones or when inspecting a datetime object's tzinfo. The method is separated from other logic because tzinfo requires a distinct dst(...) method; for a fixed-offset timezone there is no DST behavior to compute, so the method returns the module-level ZERO sentinel unconditionally. Keeping this as its own method maintains clarity and an exact implementation of the tzinfo API.

Known callers and call context:
- The Python datetime library and any application code that calls tzinfo.dst(datetime) or requests DST information from a datetime object that carries this tzinfo.
- Any utility or library code that inspects timezone DST to compute offsets, convert datetimes, or format timezone-aware datetimes.

Why this is a separate method:
- datetime.tzinfo specifies dst(...) as a separate method; implementing it separately ensures compliance with that interface and allows datetime.datetime and related utilities to call it directly.
- For fixed-offset timezones, DST is always zero, so this method provides a simple, explicit implementation.

## Args:
    _ (Optional[datetime.datetime]): The datetime for which DST would be computed. This parameter is accepted to match the tzinfo.dst signature but is unused by this implementation. Allowed values are None or a datetime.datetime instance.

## Returns:
    datetime.timedelta: Always returns the module-level ZERO sentinel (the timezone's DST offset). The return value is unchanged regardless of the input datetime. The method's type annotation guarantees the returned object will be a datetime.timedelta.

## Raises:
    None: This method does not raise exceptions for any input; it ignores the argument and always returns the ZERO sentinel.

## State Changes:
    Attributes READ:
        - None of the object's attributes are accessed by this method (it does not read self.__offset or self.__name).

    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - The instance should be a valid FixedOffset object (constructed via its __init__). No particular state beyond a valid instance is required.
        - The argument, if provided, should be None or a datetime.datetime object (matching the expected tzinfo.dst signature).

    Postconditions:
        - No mutation occurs on self.
        - The method returns the same module-level ZERO object every call (a datetime.timedelta value as per the method annotation).

## Side Effects:
    - None. There is no I/O, no external service calls, and no mutation of objects outside self.

### `imapclient.fixed_offset.FixedOffset.for_system` · *method*

## Summary:
Return a FixedOffset tzinfo representing the host system's current local timezone offset; does not modify existing instances but constructs and returns a new FixedOffset object.

## Description:
This classmethod reads the system time settings to determine whether daylight saving time is currently in effect and selects the appropriate system offset (time.altzone when DST is active and time.daylight is non-zero, otherwise time.timezone). It converts that offset (expressed in seconds west of UTC by the time module) into whole minutes and constructs a new FixedOffset instance with that minute offset (the method negates the seconds-west-of-UTC value to produce minutes east-of-UTC).

Known callers / usage context:
- No specific callers inside this repository were found in the provided context. Typical usage is to call FixedOffset.for_system() at runtime when code needs a tzinfo that reflects the system's current local timezone (for example, when constructing timezone-aware datetimes for I/O, logging, or protocol timestamps).
- Lifecycle stage: invoked at the point where a timezone object is required and the developer wants the system-local offset rather than a hard-coded value.

Why this logic is factored out:
- Encapsulates the OS/time-module-specific logic for choosing between time.timezone and time.altzone (DST-aware) and converting seconds to minutes.
- Keeps timezone-construction semantics centralized so callers only request a correctly-initialized FixedOffset without duplicating sign/units conversion or DST checks.

## Args:
    cls (type[FixedOffset]): The class to instantiate. Expected to be FixedOffset or a compatible subclass whose constructor accepts a single numeric minutes argument.

## Returns:
    FixedOffset: A new FixedOffset instance whose internal minutes value equals -offset // 60, where offset is the selected time.altzone or time.timezone (in seconds west of UTC).
    - The returned object's utcoffset() will return a datetime.timedelta equal to the computed minutes.
    - The tzname() will reflect the sign and hours/minutes derived from that minute value (e.g., "-0500" for UTC-5).
    - If the system offset seconds are not an exact multiple of 60, seconds are discarded by integer floor-division; the returned offset is rounded toward negative infinity in minute units (due to // semantics).

## Raises:
    This method does not explicitly raise exceptions.
    - It may propagate exceptions raised by cls(...) (for example, TypeError if the constructor signature is incompatible, or other exceptions raised in FixedOffset.__init__).
    - It will also propagate any unexpected AttributeError if the time module on the platform lacks the expected attributes (time.localtime, time.timezone, time.altzone, time.daylight), though these are present on standard Python platforms.

## State Changes:
Attributes READ:
    - None of self.<attr> — this is a classmethod and does not read instance attributes.
Attributes WRITTEN:
    - None by this method itself.
    - Side effect: constructing cls(...) will run that class's __init__, which may write instance attributes (in FixedOffset.__init__ this sets the instance's __offset and __name).

## Constraints:
Preconditions:
    - The time module must expose time.localtime(), time.timezone (seconds), time.altzone (seconds), and time.daylight (truthy when DST is defined). Standard Python platforms satisfy this.
    - cls must be callable and accept a single numeric argument representing minutes.

Postconditions:
    - Returns a FixedOffset instance representing the current system local timezone offset as whole minutes.
    - The returned instance's utcoffset() and tzname() reflect that computed minute offset.
    - No modification to existing FixedOffset class-level or instance-level state occurs.

## Side Effects:
    - Reads system clock state via time.localtime(). This is a pure read of system state (no I/O or external service calls).
    - Instantiates a new FixedOffset (or subclass) object, which may allocate memory and set instance attributes inside its constructor.

