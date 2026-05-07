# `pycompat.py`

## `pysnooper.pycompat.ABC` · *class*

## Summary:
A minimal abstract-base-class compatibility placeholder: a plain object subclass whose metaclass is set to abc.ABCMeta and which declares no instance attributes (__slots__ = ()).

## Description:
This class serves as a very small compatibility / marker class that establishes an ABCMeta metaclass for subclasses and prevents instance dictionaries by declaring empty __slots__. Typical usage is as a base class for other classes in this codebase that intend to participate in Python's abstract base class mechanism; it does not itself declare any abstract methods or behaviors.

Scenarios / callers:
- Used where a canonical base is desired that applies abc.ABCMeta to derived classes.
- Intended to be inherited (subclassed) by other classes in the project that need the ABCMeta behavior.
- There are no factory functions or helper constructors in this file; subclasses or external callers create instances directly.

Motivation:
- Provide a minimal, single-place declaration that applies abc.ABCMeta to a base type and enforces no per-instance attribute dictionary (via __slots__ = ()), keeping the implementation minimal and explicit.

## State:
Class-level attributes (visible in source):
- __metaclass__ : module 'abc'.ABCMeta
  - Type: metaclass object (abc.ABCMeta)
  - Purpose: Causes classes defined with this base to use ABCMeta as their metaclass (as specified in the class body).
  - Notes: The source sets this attribute at class definition time.

- __slots__ : tuple (empty)
  - Value: ()
  - Type: tuple
  - Effect: Declares that instances of this class (and instances of subclasses that do not define their own __slots__) will have no instance __dict__ and therefore cannot have arbitrary attributes added at runtime.
  - Invariant: Instances have no __dict__ unless a subclass explicitly defines a __dict__-containing slot or omits __slots__.

Instance state:
- No per-instance attributes are introduced by this class. Any state must be introduced by subclasses.

Class invariants:
- The class itself has no instance attributes and defines no methods.
- __metaclass__ remains bound to abc.ABCMeta as defined in the class body.
- __slots__ remains an empty tuple.

## Lifecycle:
Creation:
- Instantiate with no arguments: instance = ABC()
- No constructor arguments are required or supported by this class (it inherits object.__init__).

Usage:
- Typical usage is to subclass ABC to create a concrete or abstract class with ABCMeta semantics:
  - Define class MyBase(ABC): ...
  - Subclasses may declare abstract methods using @abc.abstractmethod (not declared in this class).
- Because __slots__ is empty, attempts to set new attributes on instances of ABC (or subclasses that do not add writable slots) will raise AttributeError.

Destruction / cleanup:
- No special cleanup; no context-manager protocol or close pattern is implemented by this class. Normal GC/finalization applies.

Sequence constraints:
- There is no required call order for methods (no methods beyond object.__init__), and no explicit lifecycle hooks.

## Method Map:
flowchart TD
    A[ABC: no methods] --> B[object.__init__]
    B --> C[no additional calls]
(Note: ABC declares no methods; instances use inherited object methods. Diagram shows that there are no custom method interactions.)

## Raises:
- Instantiation: This class itself declares no custom __init__ and therefore raises no exceptions on construction beyond standard Python errors (e.g., MemoryError) under extreme conditions.
- Attribute assignment: Assigning arbitrary attributes to an instance (for example instance.some_attr = value) will raise AttributeError because __slots__ is an empty tuple and instances lack a __dict__ unless a subclass defines slots or otherwise enables attribute storage.

## Example:
Create a plain instance:
    instance = ABC()

Attempting to add an attribute (will raise AttributeError):
    instance.some_attr = 1  # AttributeError: 'ABC' object has no attribute 'some_attr'

Subclassing to apply ABC semantics:
    class MyBase(ABC):
        pass

Notes:
- This class itself does not declare abstract methods. Subclasses may declare abstract methods using the abc module decorators to benefit from ABCMeta semantics.

## `pysnooper.pycompat.PathLike` · *class*

## Summary:
An abstract "path-like" interface: requires implementations to provide a __fspath__ method and provides a duck-typing subclass hook that treats classes with a __fspath__ method (or classes with an open attribute and "path" in their class name) as path-like.

## Description:
PathLike defines a minimal protocol for objects that can be converted to a filesystem path representation. It exists so libraries can accept or detect "path-like" objects in a uniform way without requiring a concrete common base class.

Scenarios where this class is used:
- A library needs to accept file-system path inputs from callers and wants to support both plain strings and custom objects that can present a path; it can check issubclass(SomeClass, PathLike) or isinstance(obj, PathLike) to decide whether to treat the object as path-like.
- Developers implement custom types that represent filesystem locations (for example, wrapper objects around URIs or virtual-file descriptors) and want them to interoperate with APIs expecting path-like values; they subclass PathLike and implement __fspath__.

Known callers and factories:
- No factories are provided by PathLike itself. Typical callers are code paths that:
  - call os.fspath(obj) (or an equivalent utility) to obtain a path from an object, or
  - use issubclass(SomeClass, PathLike) / isinstance(obj, PathLike) to accept duck-typed path-like classes.

Motivation and responsibility:
- PathLike only defines the contract to obtain a path representation. It does not manage parsing, normalization, validation, or any I/O. Concrete subclasses must decide what form the path takes (str vs bytes) and any normalization rules.

## State:
- The base class defines no instance attributes; it is stateless.
- Any state (attributes) is owned and documented by concrete subclasses.
- Invariants:
  - Instances of a concrete subclass that override __fspath__ should always return a value that callers can treat as a filesystem path (commonly str or bytes).
  - __subclasshook__ is purely declarative and should not mutate subclass or instance state.

## Lifecycle:
Creation:
- To create a concrete path-like type, subclass PathLike and provide a concrete implementation of __fspath__(self).
- PathLike marks __fspath__ with the abstractmethod decorator. Therefore, attempting to instantiate a subclass that does not override __fspath__ will raise a TypeError at instantiation time (the usual abc abstract-method enforcement).

Usage:
- Typical usage pattern:
    1. Implement __fspath__(self) in a subclass to return a path representation.
    2. Construct instances using the subclass's constructor (PathLike itself provides no __init__).
    3. Pass instances to consumers that call os.fspath(obj) or directly call obj.__fspath__() to obtain the path.
    4. Consumers may use isinstance(obj, PathLike) or issubclass(MyClass, PathLike) to allow both explicit subclasses and duck-typed classes.
- No enforced ordering of methods on the instance; callers may call __fspath__ whenever they need a path representation.

Destruction:
- PathLike imposes no cleanup requirements (no context-manager protocol, close, or other teardown methods).

## Public methods and signatures:
- @abc.abstractmethod
  def __fspath__(self)
    - Parameters:
        self: instance of a concrete subclass.
    - Returns:
        A filesystem path representation (typically a str or bytes). The base class does not coerce or validate the returned type.
    - Behavior:
        The base implementation raises NotImplementedError. Concrete subclasses must override this method.
    - Purpose:
        Provide a canonical way for the object to present itself as a file-system path.

- @classmethod
  def __subclasshook__(cls, subclass)
    - Parameters:
        cls: the PathLike class (or a subclass when called on a subclass).
        subclass: the candidate class to test (typically passed by issubclass()).
    - Returns:
        A boolean: True if the candidate class should be considered a PathLike according to this hook, otherwise False. (Note: this implementation returns a plain boolean; it does not return NotImplemented.)
    - Behavior (exact logic implemented):
        Returns True if either:
          - hasattr(subclass, '__fspath__') is True, OR
          - both hasattr(subclass, 'open') is True AND the substring 'path' appears in subclass.__name__.lower()
        Otherwise returns False.
    - Purpose:
        Enable duck-typed recognition of path-like classes by issubclass and isinstance checks.

## Method Map:
graph TD
    Caller[issubclass(SomeClass, PathLike) or isinstance(obj, PathLike)] --> Hook[PathLike.__subclasshook__(cls, subclass)]
    Hook --> CheckFspath{hasattr(subclass, '__fspath__')?}
    CheckFspath -- yes --> TrueReturn[Return True]
    CheckFspath -- no --> CheckOpenName{hasattr(subclass,'open') AND 'path' in subclass.__name__.lower()?}
    CheckOpenName -- yes --> TrueReturn
    CheckOpenName -- no --> FalseReturn[Return False]
    Caller2[Caller calls os.fspath(obj) or obj.__fspath__()] --> InstanceCall[obj.__fspath__()]
    InstanceCall --> ConcreteImpl[Concrete subclass implementation]
    ConcreteImpl -- not overridden --> BaseImpl[Base raises NotImplementedError]

## Raises:
- NotImplementedError:
    - Trigger: calling PathLike.__fspath__(self) on an object whose class did not override __fspath__ (i.e., invoking the abstract base implementation).
- TypeError related to abstractness:
    - Trigger: attempting to instantiate a subclass that still has __fspath__ as an abstract method (abc enforcement). This is enforced by the abstractmethod decorator semantics provided by the ABC machinery.
- The __subclasshook__ implementation returns a boolean and does not raise exceptions under normal usage.

## Important behavioral notes and edge cases:
- The class uses the abstractmethod decorator (via abc.abstractmethod). That enforces that concrete subclasses must override __fspath__ before they can be instantiated.
- os.fspath integration (typical idiom): many standard library helpers call os.fspath(obj) to obtain a path; os.fspath will use obj.__fspath__() if present. Implementers of PathLike should ensure the return type is what callers expect (commonly str).
- The __subclasshook__ implementation can produce True for classes that do not implement __fspath__ if:
    - the class has an attribute named open (callability of the attribute is not checked) AND
    - the substring "path" appears in the class name (case-insensitive).
  This is a permissive heuristic: libraries using issubclass checks should be aware that such classes will be reported as path-like even if they do not implement __fspath__.
- __subclasshook__ returns a concrete boolean (True or False). It does not return NotImplemented in any branch; therefore issubclass/isinstance queries will receive an immediate boolean outcome from this hook rather than deferring to normal MRO-based subclass checks.

## Example (conceptual, not verbatim code):
- Implement a subclass that returns a string path from __fspath__.
- Instantiate the subclass using its constructor.
- A consumer may call os.fspath(obj) to obtain the string path or use isinstance(obj, PathLike) to allow both explicit and duck-typed path-like objects.
- If a class named "MyPathWrapper" defines an open attribute but does not implement __fspath__, issubclass(MyPathWrapper, PathLike) will evaluate to True because of the subclass hook heuristic; to avoid surprising behavior, either implement __fspath__ or choose a class name that does not include "path".

### `pysnooper.pycompat.PathLike.__fspath__` · *method*

## Summary:
Provides the filesystem-path representation for an object by returning a native path string or bytes; as an abstract method, it must be implemented by subclasses and does not modify object state.

## Description:
This abstract accessor is the protocol surface that allows an object to be treated as a filesystem path. Callers of this method are typically code that needs a concrete path representation (for example, os.fspath and other path-aware standard library APIs). Within this module the method is declared abstract so that concrete Path-like classes in the codebase (or external code) implement the conversion to a native filesystem path.

This logic is its own method because it defines the PathLike protocol contract: callers rely on a single well-known method to obtain a filesystem path representation. Keeping it as an overridable method makes the contract explicit (and enables isinstance/subclass checks through the class' __subclasshook__).

## Args:
    None

## Returns:
    str or bytes
    - A native filesystem path representation.
    - The returned value must be either a text string (str) or a bytes object, consistent with how the caller expects to handle filesystem paths.
    - Edge cases: implementations may return an empty string or empty bytes to represent an empty path; callers should validate returned value if empty paths are invalid in their context.

## Raises:
    NotImplementedError
    - Always raised by this abstract base implementation.
    - Subclasses must override this method to provide a concrete return value; calling this base implementation directly will raise NotImplementedError.

## State Changes:
    Attributes READ:
        - None (the base implementation does not read any self.<attr> fields)
    Attributes WRITTEN:
        - None (the base implementation does not modify any attributes)

## Constraints:
    Preconditions:
        - The instance should be a concrete subclass that implements this method before being passed to path-consuming APIs.
        - Callers may assume the object implements this protocol only if it is a concrete subclass or otherwise advertises support (e.g., via duck-typing).
    Postconditions:
        - For a concrete implementation: calling the method returns a str or bytes value representing the filesystem path and leaves the object state unchanged.
        - For the base (abstract) implementation: calling it raises NotImplementedError.

## Side Effects:
    - None. The abstract base implementation does not perform I/O, external calls, or mutate objects outside self. Concrete implementations should document any side effects they introduce.

### `pysnooper.pycompat.PathLike.__subclasshook__` · *method*

## Summary:
Returns whether a candidate type should be considered a PathLike by duck-typing checks performed during Python's ABC subclass/instance checks. This is a pure predicate: it does not modify object or class state.

## Description:
This method is the custom subclass hook used by the PathLike abstract base class to decide, at runtime, whether another type should be treated as a virtual subclass. It is invoked by Python's ABC machinery and type-check helpers:
- Called by abc.ABCMeta.__subclasscheck__ when evaluating issubclass(candidate, PathLike).
- Indirectly used by isinstance(obj, PathLike) because ABCMeta.__instancecheck__ uses subclass checks on type(obj).
- Any other code that explicitly calls PathLike.__subclasshook__(PathLike, candidate) or that relies on ABC virtual subclass resolution will also exercise this method.

Typical lifecycle/context:
- Executed at runtime during type-checking (issubclass / isinstance) and not during construction or import-time initialization.
- Used to implement duck-typing semantics for path-like objects so that objects exposing an os.PathLike-compatible API (notably __fspath__) — or types that look like "path" classes and provide an open method — will register as PathLike without needing direct inheritance.

Why this is a standalone method:
- Centralizes duck-typing logic for PathLike so ABCMeta can consult it during subclass checks. Keeping this logic in __subclasshook__ enables standard Python mechanisms (issubclass/isinstance) to recognize non-inheriting types as PathLike without altering those types or requiring explicit registration.

## Args:
    cls (type): The PathLike class (the class on which this hook is defined). Provided by ABC machinery; not used to store or mutate state.
    subclass (type): The candidate class/type to test. Expected to be a class or other type object passed by issubclass() or the ABC internals.

## Returns:
    bool: True if the candidate should be regarded as a PathLike, False otherwise.
    - Returns True when the candidate type has a __fspath__ attribute (duck-typing directly compatible with os.PathLike).
    - Otherwise returns True when the candidate type has an open attribute and the substring 'path' (case-insensitive) appears in the candidate's __name__.
    - Returns False in all other cases.
    - This implementation always returns a boolean (does not return NotImplemented).

## Raises:
    No exceptions are intentionally raised by this method itself.
    - The method uses hasattr() for attribute checks, so common attribute-lookup issues (AttributeError during getattr invoked by hasattr) are handled and result in False from hasattr.
    - However, direct access to subclass.__name__ and calling .lower() assumes the attribute exists and behaves like a string; if a candidate type provides a __name__ descriptor that raises an exception or returns a non-string object whose .lower() call raises, that exception will propagate (e.g., AttributeError or TypeError). Such propagation is not part of the intended contract but is possible when classes provide exotic/malicious attribute implementations.

## State Changes:
    Attributes READ:
        - No attributes on cls are read.
        - Reads attributes of the candidate type via hasattr(subclass, '__fspath__') and hasattr(subclass, 'open').
        - Reads subclass.__name__ (for the name-based heuristic) when the 'open' attribute is present.
    Attributes WRITTEN:
        - None. The method performs no mutations to cls, subclass, or other objects.

## Constraints:
    Preconditions:
        - The caller should pass a type/class object as subclass (as provided by issubclass or the ABC internals). Passing non-class objects to issubclass(...) is a TypeError before this hook would normally be invoked.
    Postconditions:
        - No side effects or mutations will have occurred on cls or subclass.
        - The return value is a boolean indicating whether the candidate meets the two-path heuristic described above.

## Side Effects:
    - None: no I/O, no network calls, no registration, and no mutation of global or external state.
    - The only potential observable effect is the propagation of exceptions raised when accessing subclass.__name__ if that attribute's getter is implemented in a way that raises or returns an object that makes .lower() fail.

## `pysnooper.pycompat.timedelta_format` · *function*

## Summary:
Produce a microsecond-precision time-of-day string by adding the given duration to a module-level "zero" datetime and formatting its time component.

## Description:
This helper converts a duration (timedelta) into a time-of-day string by computing (datetime_module.datetime.min + timedelta).time() and formatting that time with timespec='microseconds' via the module-level formatter time_isoformat.

Known callers:
- No call sites were discovered in the provided snapshot. Typically this function is used when durations must be rendered for logging, debugging, or human-readable output with consistent microsecond precision.

Why this logic is extracted:
- It centralizes the conversion of durations to a stable, microsecond-precise time string and isolates compatibility concerns (different Python versions or alternative datetime-like modules). The function delegates formatting to time_isoformat and relies on an injectable datetime_module, making tests and cross-version compatibility easier.

## Args:
    timedelta (datetime.timedelta):
        - The duration to format. The parameter name in the function signature is exactly "timedelta" (which shadows the type name).
        - Expected type: datetime.timedelta or an object that supports addition with datetime_module.datetime.min.
        - Allowed values: any timedelta for which the expression (datetime_module.datetime.min + timedelta) produces a valid datetime.
        - Important note: If timedelta represents whole days or spans more than 24 hours, the returned string reflects only the time-of-day (the date/days are discarded by .time()).

## Returns:
    str:
        - A string returned from calling time_isoformat(time, timespec='microseconds') where time is the time component of (datetime_module.datetime.min + timedelta).
        - Typical format: "HH:MM:SS.ffffff" (hours:minutes:seconds.microseconds). Whole-day components are not represented — only the time-of-day is returned.
        - Edge cases:
            * For timedelta values >= 24 hours, the returned time corresponds to (min + timedelta).time(), effectively the time modulo 24 hours (for example, 25 hours → "01:00:00.000000").
            * For negative timedeltas that still keep the sum within the supported datetime range, a valid time-of-day is returned (may represent a time on an earlier date).
            * For timedeltas that cause the datetime computation to underflow/overflow the supported range, an exception is raised (see Raises).

## Raises:
    NameError:
        - If datetime_module or time_isoformat is not defined in the module namespace at call time.
    TypeError:
        - If the provided timedelta cannot be added to datetime_module.datetime.min (incompatible type) or if time_isoformat is not callable with the provided arguments.
    OverflowError:
        - If adding the timedelta to datetime_module.datetime.min produces a datetime outside the representable range (underflow/overflow).
    Any exception raised by time_isoformat:
        - Any error thrown by the formatter (for example, if the passed object is not a time object or if the formatter rejects the timespec argument) is propagated to the caller.

## Constraints:
Preconditions:
    - datetime_module exists in the module namespace and exposes a datetime class with a .min attribute that is a valid datetime.
    - time_isoformat exists in the module namespace and is callable with signature similar to time_isoformat(time_obj, timespec='microseconds').
    - The timedelta argument is compatible with addition to datetime_module.datetime.min.
Postconditions:
    - On success, the function returns a microsecond-precision time-of-day string and does not mutate global state.

## Side Effects:
    - None intrinsic to this function. It performs pure computation and delegates formatting; it does not perform I/O or mutate external state. Exceptions from module-level dependencies may surface to the caller.

## Control Flow:
flowchart TD
    Start --> AddTimedelta[Compute datetime_module.datetime.min + timedelta]
    AddTimedelta -->|success| ExtractTime[Call .time() on the datetime]
    ExtractTime --> CallFormatter[Call time_isoformat(time, timespec='microseconds')]
    CallFormatter --> ReturnResult[Return formatted string to caller]
    AddTimedelta -->|Type/Overflow error| Error_Add[Raise TypeError or OverflowError]
    ExtractTime -->|Missing .time()| Error_Attr[Raise AttributeError/TypeError]
    CallFormatter -->|Formatter error| Error_Format[Propagate formatter exception]

## Examples (realistic usage and edge cases):
Example — typical single-hour duration (described in prose):
    - If datetime_module is the standard datetime module and time_isoformat simply calls time.isoformat(timespec=...), calling this function with a timedelta of 1 hour returns "01:00:00.000000".

Example — multi-day duration (behavior to be aware of):
    - For timedelta representing 25 hours (1 day + 1 hour), the internal computation yields datetime_module.datetime.min + timedelta corresponding to the next calendar day at 01:00:00. .time() extracts 01:00:00, and the returned string will be "01:00:00.000000". Whole days are not shown in the output.

Example — negative duration and underflow:
    - A small negative timedelta that keeps the sum within the supported datetime range returns the corresponding earlier time-of-day. If the negative timedelta is large enough to move the result before the minimal representable datetime, the function raises OverflowError; callers that may pass very large negative values should catch OverflowError and handle or clamp the duration beforehand.

Testing note:
    - Because the function relies on module-level symbols datetime_module and time_isoformat, unit tests can inject deterministic fakes for those names to verify formatting behavior, error propagation, and the handling of multi-day inputs without depending on the real datetime implementation.

## `pysnooper.pycompat.timedelta_parse` · *function*

## Summary:
Parses a short duration string into a timedelta object from the module named datetime_module.

## Description:
This function converts a textual duration into a timedelta by splitting the input into four integer fields (hours, minutes, seconds, microseconds) and passing them to datetime_module.timedelta.

Known callers:
- No call sites were provided in the available context. Search the repository for references to this symbol to discover who invokes it.

Why this is a separate function:
- Responsibility boundary: isolates the string-to-timedelta parsing logic so callers can obtain a ready-to-use timedelta without each caller reimplementing parsing rules or error handling. This keeps parsing concerns centralized and testable.

## Args:
    s (str): A duration string containing four integer fields separated by colons, or with the last separator as a dot.
        - Expected formats (examples): "H:M:S.MICRO", "H:M:S:MICRO", where:
            * H = hours (integer, may be multiple digits, may be negative if intentionally provided)
            * M = minutes (integer)
            * S = seconds (integer)
            * MICRO = microseconds (integer, typically 0..999999 but integer conversion is applied as-is)
        - The implementation performs s.replace('.', ':').split(':'), so either '.' or ':' may be used between the seconds and microseconds field.
        - Preconditions: s must be an object with a replace(str, str) method that returns a string (normally a Python str). Each resulting split segment must be convertible to int.

## Returns:
    datetime_module.timedelta
    - The function returns the result of calling timedelta on the module or object referenced by the name datetime_module, with keyword arguments hours, minutes, seconds, microseconds set to the parsed integer fields.
    - The returned object is whatever datetime_module.timedelta constructs; typically a datetime.timedelta-like object representing the same duration as the parsed fields.

## Raises:
    ValueError:
        - If the input does not split into exactly four components (the sequence unpacking into four variables will raise a ValueError).
        - If any of the four components cannot be converted to int (int(...) will raise ValueError).
    AttributeError:
        - If s does not support replace (e.g., s is None or another type without replace), calling s.replace will raise AttributeError.
    NameError (or similar at runtime):
        - If the name datetime_module is not defined in the module namespace where this function runs, attempting to access datetime_module.timedelta will raise NameError (or UnboundLocalError in some contexts). This function assumes datetime_module is available and exposes a timedelta constructor.
    TypeError:
        - If datetime_module.timedelta is called with inappropriate types after parsing (unlikely because parsed values are ints), or if datetime_module.timedelta itself raises TypeError for invalid argument ranges.

## Constraints:
    Preconditions:
        - The caller must supply a string-like s formatted as four integer fields separated by ':' (or with the last separator as '.').
        - The module-level name datetime_module must exist and provide a timedelta callable that accepts the keyword arguments hours, minutes, seconds, microseconds.
    Postconditions:
        - On successful return, a timedelta-like object has been constructed and returned; no global state is modified by this function.

## Side Effects:
    - None intrinsic to this function: it performs pure computation and returns the constructed timedelta object.
    - No I/O, no network access, and no mutation of global variables is performed by the code shown. Side effects only occur if datetime_module.timedelta has side effects (which standard datetime.timedelta does not).

## Control Flow:
flowchart TD
    A[Start: receive s] --> B{s has replace method?}
    B -- No --> C[AttributeError raised]
    B -- Yes --> D[s.replace('.', ':')]
    D --> E[split by ':' -> parts list]
    E --> F{len(parts) == 4?}
    F -- No --> G[ValueError from unpacking or explicit error]
    F -- Yes --> H[map int over parts]
    H --> I{all parts convertible to int?}
    I -- No --> J[ValueError from int()]
    I -- Yes --> K[assign hours, minutes, seconds, microseconds]
    K --> L[call datetime_module.timedelta(hours=..., minutes=..., seconds=..., microseconds=...)]
    L --> M[return timedelta object]

## Examples (described; not executable code blocks):
- Typical success:
    Input string: "1:02:03.004005"
    Parsing steps:
      - replace('.') → "1:02:03:004005"
      - split(':') → ["1", "02", "03", "004005"]
      - map(int, ...) → [1, 2, 3, 4005]
    Returned value: datetime_module.timedelta(hours=1, minutes=2, seconds=3, microseconds=4005)

- Alternate accepted separator:
    Input string: "0:00:30:500000"
    Parsed to hours=0, minutes=0, seconds=30, microseconds=500000

- Error cases:
    - Input string "1:2:3" (only three fields) will result in a ValueError during unpacking.
    - Input string "1:02:xx.004" where "xx" is non-numeric will raise ValueError when converting that segment to int.
    - Passing None for s will raise AttributeError when attempting to call replace.

Notes for integrators:
- Ensure that datetime_module is defined in the module (for example, set datetime_module = datetime if using the standard library) before calling this function.
- If microsecond precision might be omitted, callers should normalize the input into the four-field format before calling this helper.

