# `mt_exceptions.py`

## `mingus.core.mt_exceptions.Error` · *class*

*No documentation generated.*

## `mingus.core.mt_exceptions.FormatError` · *class*

## Summary:
FormatError is a distinct exception class used to signal formatting-related errors; it is a direct subclass of Error and introduces no new behavior or state.

## Description:
FormatError exists solely as a marker type (an identity-only exception) to allow callers to raise and catch formatting-specific problems separately from other error types.

- What it is: a bare subclass of Error (class FormatError(Error): pass).
- What it is not: it does not implement its own initializer, attributes, methods, or helpers — all runtime behavior is inherited from Error.
- When to use: raise or let FormatError propagate when code detects that input/data does not conform to expected format rules (parsing failures, malformed records, schema mismatches, etc.), and you want to handle those cases distinctly.
- Known callers: No usages were discovered in the supplied repository context; any module that needs to signal formatting errors may raise this exception.

Motivation and responsibility:
- Provides a specific exception type so higher-level code can handle formatting faults without inspecting messages or error codes.
- Responsibility is limited to classification; it carries no formatting logic or metadata by itself.

## State:
- New attributes introduced by this class: none.
- All instance state and construction behavior come from the base class Error (not defined here). This class adds no invariants of its own.
- Public surface: the class object FormatError (usable in isinstance/except checks). No public instance attributes or methods are defined in this file.

## Lifecycle:
- Creation:
  - Instances are created via the constructor provided by Error. Because FormatError does not define __init__, callers should consult Error to learn what constructor arguments (if any) are required or permitted.
  - Typical usage is to raise the exception at the point of detection.
- Usage:
  - Raised to indicate formatting problems.
  - Caught via except FormatError: to isolate handling for format-specific failures.
  - No instance methods are expected to be invoked on FormatError beyond normal exception handling operations (inspect, traceback, etc.).
- Destruction:
  - No special cleanup; behaves like a normal exception object under Python's memory management.

## Method Map:
- Inheritance relationship (no additional methods):

graph LR
    FormatError --> Error

(Interpretation: FormatError is a subclass of Error and defines no methods or attributes itself.)

## Raises:
- The class body contains no code that raises exceptions.
- Any exceptions raised during instantiation or use originate from the Error base class or from the code that raises FormatError. Consult Error's documentation/implementation for constructor-specific failure modes.

## Example:
- Catching a formatting error produced by some parser function (safe example that does not assume Error's constructor signature):

    try:
        parse_some_input(data)  # parse_some_input may raise FormatError
    except FormatError:
        handle_formatting_issue()

- Raising a FormatError:
  - Because FormatError does not declare its own constructor, check the project's Error base-class implementation to determine valid constructor arguments before instantiating or raising with a message or payload.

Notes:
- To fully understand what arguments (if any) can be passed when creating a FormatError instance and what additional attributes may exist at runtime, consult the implementation and documentation of the base Error class in mingus.core.mt_exceptions.

## `mingus.core.mt_exceptions.NoteFormatError` · *class*

## Summary:
A dedicated exception type representing errors due to an invalid or malformed musical note format. It exists solely to provide a distinct, catchable exception class for note-format problems.

## Description:
NoteFormatError is a simple subclass of Error and adds no behavior or state of its own. It is intended to be used by parsing, validation, or conversion code that needs to signal that an input representing a musical note does not conform to the expected format. Creating this distinct type enables callers to catch note-format-specific problems separately from other error kinds.

Known callers/factories:
- The source code for this class contains no callers. Typical callers are functions or methods that parse or validate note strings; they should raise NoteFormatError to indicate an invalid note format.

Motivation:
- Providing a dedicated exception class makes error handling clearer and allows calling code to catch note-format issues explicitly (for example, to provide user feedback or attempt alternate parsing strategies) without catching unrelated errors.

## State:
- Attributes: None defined on NoteFormatError itself.
- Type: This class is a subclass of Error; any attributes or behavior are inherited from that base class.
- Invariants:
  - Instances of NoteFormatError carry no additional invariant beyond those guaranteed by Error.
  - The class defines no additional state; equality, string representation, or other behaviors are those of Error (or its base classes).

For __init__ parameters:
- NoteFormatError does not define its own __init__; it inherits Error.__init__. Callers should construct it using the same parameters that Error accepts. If Error accepts a message string, a user may pass a descriptive message when raising NoteFormatError.

## Lifecycle:
- Creation:
  - Instantiate by raising it: raise NoteFormatError(<optional message or args accepted by Error>)
  - No factory methods are defined in this class.
- Usage:
  - Typical usage is a single-step creation via raise in error conditions within parsers/validators.
  - Catching: callers can catch NoteFormatError explicitly to handle note-format errors:
      try:
          parse_note(s)
      except NoteFormatError:
          handle_invalid_note()
- Destruction:
  - Typical Python exception lifecycle applies. There is no special cleanup, context-manager protocol, or close() required.

## Method Map:
- The class declares no methods of its own. It only inherits from Error.
- Mermaid diagram (method/flow overview):

graph TD
    A[NoteFormatError] --> B[inherits Error]
    B --> C[base Exception behavior: initialization, str(), repr(), traceback propagation]

## Raises:
- __init__ (inherited): This class defines no additional raises in its own code. Any exceptions potentially raised by constructing or raising NoteFormatError come from the inherited Error.__init__ (if that implementation raises for invalid arguments) or from normal Python exception machinery.
- When to raise NoteFormatError: raise it directly when a note string or note representation is syntactically or semantically invalid for the parser/validator in use.

## Example:
- Raising a NoteFormatError with a message (typical usage):

    # inside a note parser/validator
    if not valid_note_string(s):
        raise NoteFormatError("invalid note format: expected 'C#4', got '{}'".format(s))

- Catching a NoteFormatError to handle invalid input separately:

    try:
        note = parse_note(user_input)
    except NoteFormatError as e:
        print("Please enter a valid note:", e)

## `mingus.core.mt_exceptions.KeyError` · *class*

## Summary:
A marker exception type indicating an error related to "key" operations; it is a direct subclass of Error and adds no new behavior.

## Description:
This class exists solely to provide a distinct exception type for signaling and catching errors that are specific to key-related operations within the package. It does not implement additional logic beyond what is provided by its base class, Error. Use cases include raising this exception when a function or method detects an invalid, unsupported, or otherwise problematic key-related condition, and catching it when callers need to handle key-specific failures differently from other Error subclasses.

Known callers/factories:
- Any module or function in the codebase that performs operations on "keys" (naming or semantics determined by the wider project) may raise or catch this exception. No specific callers are embedded in this class.

Motivation and responsibility boundary:
- Responsibility: serve as a typed marker to differentiate key-related failures from other errors.
- Boundary: do not contain business logic, state, or helper methods — those remain in the caller or in Error.

## State:
- Attributes: This class defines no new attributes. All instance state (if any) is inherited from the base class, Error.
- __init__ parameters: KeyError does not override __init__; it uses Error.__init__ unchanged. The exact constructor signature, default values, and parameter constraints are those of Error; consult the Error documentation for concrete parameter names, types, and behavior.
- Valid values / invariants:
  - No additional invariants beyond those enforced by Error.
  - Instances of KeyError should be treated as immutable marker exceptions unless Error documents mutable state.

## Lifecycle:
- Creation:
  - Instantiate the class by calling its constructor (the same signature as Error) or by raising it directly in code. Example forms are described below.
  - Required arguments: whatever Error.__init__ requires — see Error docs.
- Usage:
  - Typical pattern: raise KeyError(...) at the point an error condition related to keys is discovered.
  - Catching: callers may catch this specific class (except KeyError as e) to handle key-specific errors, or catch the base Error to handle it more generally.
  - There is no enforced ordering of method calls on this object—it's used as a plain exception instance.
- Destruction:
  - No cleanup is required by this class. It follows normal exception object lifecycle and is garbage-collected when no longer referenced.
  - Not a context manager; no close/cleanup API.

## Method Map:
- Relationship and typical flow (mermaid diagram):

graph TD
  A[Caller code detecting key problem] --> B[raise KeyError(instance)]
  B --> C[Exception propagation]
  C --> D[except KeyError -> handle key-specific]
  C --> E[except Error -> handle general error]
  KeyError ---|inherits| F[Error]

## Raises:
- The KeyError class itself does not raise exceptions during definition.
- During instantiation, any exceptions that Error.__init__ may raise can propagate; consult Error documentation for specific constructor-side exceptions (e.g., TypeError for wrong argument types) since KeyError inherits Error.__init__ unchanged.
- When used in code, KeyError instances are typically raised to signal error conditions; raising it does not itself raise additional exceptions beyond the normal exception-handling flow.

## Example:
- Creation: instantiate or raise an instance using the same constructor as Error. For example, to signal a key-related error create a KeyError instance with the same initialization parameters that Error accepts, and raise it at the point of failure.
- Catching: callers who need to react to key-specific failures should catch KeyError explicitly; callers that only need general error handling can catch Error (the base class).
- Cleanup: no explicit cleanup is required — treat KeyError like any other exception object.

## `mingus.core.mt_exceptions.RangeError` · *class*

## Summary:
A semantic exception class indicating a range-related error condition; a lightweight subclass of Error used solely to distinguish range errors from other error types.

## Description:
RangeError is an exception type defined as a direct subclass of Error. It does not add fields, methods, or behavior beyond what it inherits from its superclass; its purpose is to provide a distinct type that callers and exception handlers can catch when an out-of-range or range-related condition occurs.

Typical scenarios:
- Raised by validation or parsing code when a numeric, index, or boundary value lies outside an allowed range.
- Used by libraries or application code that want to signal "range" failures separately from other error classes.

Known callers/factories:
- Any code that validates bounds (index checks, numeric limits, interval assertions) may instantiate and raise RangeError. This class itself does not implement factory methods.

Motivation:
- Provides a clear, type-safe way to identify and handle range-related failures without inspecting error messages.
- Keeps range semantics separate from other Error subclasses for clearer exception handling policies.

## State:
- Instance attributes: None defined on RangeError itself.
  - Because RangeError does not declare an __init__ method, it inherits any instance attributes and initialization behavior from its superclass Error. Do not rely on any attributes being present unless documented on Error.
- __init__ parameters:
  - RangeError does not define its own __init__; callers should instantiate it using the same signature as Error (if known) or with no arguments. If Error requires arguments, the caller must follow that contract.
- Valid values/invariants:
  - There are no RangeError-specific invariants. Any invariants are those enforced by the superclass Error.

Class invariants:
- A RangeError instance must be an instance of Error (is-a relationship).
- No additional invariants are introduced by RangeError itself.

## Lifecycle:
- Creation:
  - Instantiate by calling RangeError(...) using the same constructor signature as Error (or with no arguments if Error supports that). Example: raise RangeError("index out of range")
- Usage:
  - Typically raised at the point of detecting an out-of-range condition.
  - Handlers catch RangeError explicitly when they need to handle range-specific failures, or catch Error/Exception to handle multiple error types.
  - No methods are expected to be invoked on RangeError instances beyond those provided by Error and base Exception (e.g., str()).
- Destruction:
  - Standard Python exception lifetime rules apply. No explicit cleanup, context manager, or close() is required.

## Method Map:
graph LR
    RangeError --> Error[Error (superclass)]
    RangeError -.-> |no additional methods| InstanceMethods[None]

Explanation:
- RangeError inherits all callable behavior from Error. It defines no new methods or call flows of its own.

## Raises:
- RangeError.__init__ does not declare or implement new raises in this subclass.
- Any exceptions thrown during instantiation or initialization are inherited from Error.__init__ (unknown here). Therefore:
  - Do not assume RangeError instantiation is free of exceptions; follow the Error contract if available.
  - Raising RangeError is performed with the standard Python raise statement; creation itself will only raise if the superclass initializer raises an exception.

## Example:
- Basic instantiation and raising:

    # Create and raise with a message (follows superclass constructor contract)
    raise RangeError("value 42 is outside allowed range 0..10")

- Catching specifically:

    try:
        # code that may raise RangeError
        maybe_raise_range_error()
    except RangeError as re:
        # handle range-specific failure
        handle_range_failure(re)
    except Error:
        # handle other Error types
        handle_general_error()

## `mingus.core.mt_exceptions.FingerError` · *class*

## Summary:
FingerError is a dedicated exception class that represents errors specific to "finger" operations. It is a direct, empty subclass of the module's Error base class and adds no new behavior or state.

## Description:
FingerError is provided so callers and handlers can distinguish finger-related failures from other errors in the same error hierarchy. Because the class body contains only "pass", all semantics (constructor signature, attributes, formatting, and any metadata) are inherited from Error. This documentation therefore restricts itself to the responsibilities that FingerError adds as a distinct type rather than implementation details of construction or attributes.

Scenarios for instantiation:
- Raise FingerError where code encounters an error condition specifically tied to finger functionality so that upstream code can catch this case separately.
- Re-raise or wrap underlying exceptions as FingerError when converting lower-level errors into the module's domain-specific error types.

Known callers/factories:
- Concrete callers inside the codebase are not available in this documentation snapshot. In general, any function, method, or module performing finger-related logic should raise FingerError to signal a semantic error of that category.

Motivation and responsibility boundary:
- Purpose: make finger-specific failures easily identifiable in logs and except handlers.
- Boundary: FingerError must not attempt to encapsulate other unrelated error semantics; it exists solely as a named classifier in the exception type hierarchy. All payload, message formatting, and contextual fields come from Error.

## State:
- New attributes introduced by FingerError: none.
- Inherited attributes: any instance attributes defined by Error (unknown in this snapshot). Do not assume specific attribute names, types, or defaults — consult Error to learn available message/context fields.
- Valid values and invariants: FingerError does not impose additional invariants beyond those of Python exceptions and whatever constraints Error enforces. There are no FingerError-specific value ranges or mutually exclusive attributes.

For callers:
- There are no FingerError-specific constructor parameters. Use the same parameters accepted by Error.__init__.
- If you require finger-specific metadata in exception instances, add it via Error (the base class) or extend FingerError in a new subclass that adds fields.

## Lifecycle:
- Creation:
  - Instantiate as you would any exception class. Because FingerError does not override __init__, pass only arguments that Error.__init__ accepts.
  - Example instantiation patterns (whether these variants are valid depends on Error.__init__):
    - No-argument: FingerError()
    - With message/context: FingerError("explanatory text")  (only valid if Error accepts such an argument)
    - Exception chaining: raise FingerError(...) from original_exception
- Usage:
  - Raise: used at the point of error detection to signal a finger-specific problem.
  - Catch: callers should prefer catching FingerError when they need to handle this category specifically; otherwise catch Error or Exception for broader handling.
  - Typical order in handlers:
    1. except FingerError: handle the finger-specific recovery or fallback
    2. except Error: handle other errors in the same hierarchy
    3. except Exception: fallback catch-all
- Destruction / cleanup:
  - No explicit cleanup or context manager behavior is defined. FingerError instances follow normal Python object lifecycle and garbage collection.

## Method Map:
flowchart LR
    A[Detect finger-related failure] --> B[Instantiate FingerError (via Error.__init__)]
    B --> C[raise FingerError]
    C --> D{Handler?}
    D -->|Yes: specific| E[except FingerError -> handle]
    D -->|Yes: generic| F[except Error -> handle]
    D -->|No| G[Propagate to caller / crash]

(Note: FingerError defines no methods; this map shows the typical flow where the exception is raised and then handled.)

## Raises:
- FingerError.__init__ itself defines no new raise conditions beyond those of Error.__init__. Possible raised exceptions during instantiation include:
  - TypeError or ValueError if the caller passes invalid arguments to Error.__init__ (exact behavior depends on Error).
  - MemoryError or SystemError in extreme allocation/VM failure scenarios (general Python behavior).
- Accessing attributes or calling methods on a FingerError instance will only raise exceptions if those operations are invalid per the inherited Error implementation.

## Example:
- Raising simply to classify an error (validity of parameters depends on Error.__init__):
try:
    # inside a finger-related operation
    raise FingerError()  # valid if Error supports no-arg construction
except FingerError as fe:
    # handle the finger-specific condition
    handle_finger_error(fe)

- Raising with chaining to preserve original exception context:
try:
    perform_low_level_operation()
except SomeOtherError as orig:
    # convert lower-level exception into a finger-domain exception while preserving context
    raise FingerError("conversion to finger domain error") from orig

- Catching patterns:
try:
    do_some_work()
except FingerError:
    # fine-grained handling for finger-related problems
    recover_finger_case()
except Error:
    # handle other errors in the same module hierarchy
    log_and_abort()
except Exception:
    # last-resort fallback
    fallback()

