# `exceptions.py`

## `csvkit.exceptions.CustomException` · *class*

*No documentation generated.*

### `csvkit.exceptions.CustomException.__init__` · *method*

## Summary:
Assigns the provided value to the instance attribute msg, initializing the exception's stored message.

## Description:
This initializer sets up the object's message state by assigning the passed-in msg value to self.msg so the exception instance retains that payload for later inspection or display. Known callers: not available in the provided context; in normal use this method is invoked when code constructs or raises the exception (for example, when creating CustomException instances to signal an error). The logic is implemented here to centralize instance state initialization according to standard object construction practices.

## Args:
    msg (any): The value to store as the instance message. The implementation imposes no type restrictions; callers commonly pass a str but any object may be stored.

## Returns:
    None: As an initializer, it does not return a value. The effect is the mutation of the instance state.

## Raises:
    None: The method body is a direct attribute assignment and contains no explicit raise statements.

## State Changes:
    Attributes READ:
        - None: the implementation does not read any existing instance attributes.
    Attributes WRITTEN:
        - self.msg: set to the exact object passed as msg.

## Constraints:
    Preconditions:
        - None enforced by this implementation; callers may pass any value for msg.
    Postconditions:
        - After execution, self.msg references the same object provided as msg (object identity is preserved for mutable objects).

## Side Effects:
    - None: no I/O, external service calls, or modifications to objects outside the instance are performed by this method.

### `csvkit.exceptions.CustomException.__unicode__` · *method*

## Summary:
Return the value previously stored on the instance under msg; does not modify the instance.

## Description:
This method returns the instance attribute msg that is assigned in the class constructor. Within the same class, __init__(self, msg) sets this attribute and __str__ returns the same value. There are no internal callers of this method in the provided class definition.

This method exists to expose the stored msg value directly; it does not perform formatting or type conversion.

## Args:
    None

## Returns:
    Any: The exact value of self.msg as currently stored on the object. The implementation returns the object unchanged.

## Raises:
    AttributeError: If the instance was not properly initialized and self.msg does not exist, attribute access will raise AttributeError. The method contains no explicit raise statements.

## State Changes:
    Attributes READ:
        - self.msg

    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The instance should have been initialized so that self.msg exists (as assigned by __init__).

    Postconditions:
        - The instance state is unchanged.
        - The return value equals the current value of self.msg.

## Side Effects:
    - None: the method performs no I/O, external calls, or mutations of objects outside self.

### `csvkit.exceptions.CustomException.__str__` · *method*

## Summary:
Returns the stored message value as the object's textual representation, exposing the exception's msg attribute for conversion to a string.

## Description:
This method is the object's string-conversion hook and is called whenever the exception instance is converted to text (for example via the built-in str() call, implicit conversion in print(), or when an exception is formatted by logging or error-reporting code). It centralizes the representation logic so that both text and unicode conversion methods can remain consistent (see the class' __unicode__ which returns the same attribute).

Known callers / contexts:
- str(exception_instance) — explicit conversion to text.
- print(exception_instance) — uses the str() conversion implicitly.
- Logging/formatter code and any code that interpolates or concatenates the exception into strings.
- Any third-party libraries or framework code that call obj.__str__ when presenting exceptions.

Why this is a separate method:
- Keeps the textual representation logic isolated so subclasses can override representation behavior without changing other exception mechanics.
- Ensures consistent output across different textification code paths (str and print) by delegating to a single attribute.

## Args:
None.

## Returns:
object
- The method returns the exact value stored in self.msg (no transformation).
- There is no type enforcement within this method: callers should treat the returned value as whatever type was assigned to msg by the code that raised/constructed the exception.
- By convention, msg should be a text string when the exception is intended to provide human-readable text; this method does not coerce or validate that.

## Raises:
None explicitly.
- The implementation itself performs no checks or raises. Any runtime errors arising from using the returned value in other contexts (for example, code that assumes a string) are the responsibility of callers or the code that constructs the exception.

## State Changes:
Attributes READ:
- self.msg

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- The instance must have a msg attribute. The class initializer assigns this attribute (i.e., CustomException.__init__(self, msg) sets self.msg).

Postconditions:
- The method does not modify the instance. After the call, self.msg remains unchanged.
- The returned value is identical to the pre-call value of self.msg.

## Side Effects:
- None. The method performs no I/O, network access, logging, or mutation of objects outside self.

## `csvkit.exceptions.ColumnIdentifierError` · *class*

## Summary:
Represents an error condition specific to identifying or resolving a CSV column; a semantic marker exception that subclasses CustomException and carries no additional state or behavior.

## Description:
This exception exists to signal problems related to column identification (for example: ambiguous column names, missing column references, or invalid column specifiers) in the CSV processing tooling. It is a semantic/marker subclass: code paths that need to differentiate column-identification failures from other errors should raise or catch this type.

Because the class body is empty, all construction, message formatting, attributes, and behavior are inherited from CustomException. Callers that want to signal a column-identification error should raise ColumnIdentifierError; catch blocks that need to handle column-related failures may catch this class specifically (or catch the broader CustomException if desired).

## State:
- No additional instance attributes introduced by ColumnIdentifierError.
- Invariants:
  - Any instance is also an instance of CustomException.
  - Since there is no added mutable state here, there are no additional invariants beyond those enforced by CustomException.

## Lifecycle:
- Creation:
  - Instantiate exactly as you would the base class CustomException. This class does not define its own __init__, so the available constructor signature and accepted arguments are those provided by CustomException.
  - Example invocation pattern: raise ColumnIdentifierError(<message_or_kwargs_accepted_by_CustomException>)
- Usage:
  - Typical usage is a single-step raise at the point a column identifier cannot be resolved or validated.
  - Typical consumers will catch either ColumnIdentifierError to handle column-specific recovery or CustomException to handle a broader group of related errors.
- Destruction:
  - No special cleanup is required. There is no context-manager protocol or close() method defined by this subclass.

## Method Map:
graph LR
    A[CustomException] --> B[ColumnIdentifierError]
    B --> |inherits| A

(Interpretation: ColumnIdentifierError has no methods or attributes of its own; it inherits behavior and initialization from CustomException.)

## Raises:
- ColumnIdentifierError.__init__ does not declare or implement any new raise conditions; any exceptions that can be raised during construction or usage are those that CustomException may raise (e.g., errors from argument validation inside CustomException). This subclass does not add new runtime exception types.

## Example:
- Raising a column-identification error at the call site (conceptual example; actual constructor arguments depend on CustomException's signature):
    raise ColumnIdentifierError("Could not find column: 'age'")

- Catching only column-identification issues:
    try:
        resolve_column(spec)
    except ColumnIdentifierError as e:
        handle_missing_or_invalid_column(e)
    except CustomException:
        handle_other_csvkit_errors()

## `csvkit.exceptions.CSVTestException` · *class*

## Summary:
Represents an exception that records a specific CSV input row and its source line when a CSV-related test or validation fails.

## Description:
CSVTestException is intended to be instantiated when a CSV validation/test detects a problem with a particular row. It provides two pieces of contextual state (the source line number and the row payload) in addition to the textual error message forwarded to the exception superclass.

Typical scenario:
- A CSV parsing or validation routine identifies a malformed or invalid row and creates this exception to surface where (which line) and what (which row) caused the failure.
- The class does not implement validation logic itself; it is a small value-bearing exception type used to carry context.

Notes about the base class:
- This class subclasses CustomException and passes the provided msg argument to the CustomException constructor. The implementation of CustomException is not shown here, so any behavior beyond the superclass receiving the message (for example, additional attributes or side effects) is not assumed.

## State:
Attributes set by __init__ (public):
- line_number
    - Description: The line number in the CSV source that corresponds to the provided row.
    - Set by: __init__(line_number, row, msg)
    - Constraints: No type assertions are enforced by this class; callers should provide a value that meaningfully identifies the line (commonly an integer).
    - Invariant: Once set in __init__, line_number is expected to remain immutable for the lifetime of the exception instance (the class does not modify it after construction).

- row
    - Description: The row payload associated with the error; typically the parsed CSV row (could be a list, tuple, mapping, or raw record depending on the CSV reader used).
    - Set by: __init__(line_number, row, msg)
    - Constraints: No constraints enforced by this class; the value is stored verbatim.
    - Invariant: The stored row value remains unchanged by this class after __init__.

Inherited state:
- The textual message passed as msg is forwarded to CustomException via super().__init__(msg). Any attributes or behavior provided by CustomException are inherited but not redefined here.

Class invariants:
- After construction, .line_number and .row must be present on the instance.
- The class does not mutate these attributes internally after construction.

## Lifecycle:
Creation:
- Instantiate with three positional arguments in this exact order:
    1. line_number — identifier for the CSV line (no default; required)
    2. row — the row data associated with the error (no default; required)
    3. msg — the human-readable error message passed to the base exception (no default; required)
- Example signature: CSVTestException(line_number, row, msg)

Usage:
- Typically raised immediately after detection of a CSV row-level error:
    - The caller constructs CSVTestException(...) and raises it to signal failure.
    - Consumers catching this exception can inspect .line_number, .row, and the base exception message to produce diagnostics or logs.
- There are no additional public methods on this class beyond those inherited from CustomException and Exception.

Destruction / cleanup:
- No special cleanup is required. This class does not implement context manager protocols or close resources.

## Method Map:
flowchart LR
    A[Construct CSVTestException(line_number, row, msg)] --> B[Call super().__init__(msg)]
    B --> C[Set self.line_number = line_number]
    C --> D[Set self.row = row]
    D --> E[Instance ready to be raised or returned]
    E --> F[Raised and optionally caught by caller]

## Raises:
- __init__ itself contains no explicit raise statements.
- Any exceptions raised by the CustomException constructor (invoked via super().__init__(msg)) will propagate; callers should be aware that behavior of CustomException is authoritative for any constructor-side errors.

## Example:
- Creation and raising (conceptual description):
    1. A CSV validator identifies a problematic row at line 12.
    2. The validator creates the exception with the offending row and a message describing the problem: CSVTestException(12, offending_row, "Bad number format in column 3").
    3. The validator raises that instance to signal failure.
    4. A higher-level caller catches CSVTestException and inspects .line_number and .row to log the failure and present a helpful error to the user.

- Consumption pattern:
    - Catch CSVTestException to retrieve precise location and content: examine exception.line_number, exception.row, and the exception message (as defined by the base CustomException).

### `csvkit.exceptions.CSVTestException.__init__` · *method*

## Summary:
Initialize the exception by delegating the message to the base class (CustomException) and storing the provided line_number and row on the instance.

## Description:
Constructs a CSVTestException instance. The constructor forwards msg to the superclass initializer and records the row-level context by assigning line_number and row as attributes on the new exception object.

This is a dedicated initializer so that any code that raises CSVTestException can rely on every instance containing the message (handled by CustomException) plus the two contextual attributes (line_number and row) for later inspection or reporting.

## Args:
    line_number (int | None): The numeric line identifier associated with the problematic CSV row. The constructor does not validate the value; callers should pass an integer or None if the line number is unknown.
    row (Any): The CSV row object related to the error. The value is stored by reference without copying or validation.
    msg (str): The error message text. It is forwarded to CustomException.__init__; the constructor expects a string-like value.

## Returns:
    None: As an initializer, it does not return a value; it initializes the exception instance.

## Raises:
    Propagated exceptions from CustomException.__init__ or from attribute assignment: the constructor itself does not explicitly raise, but any error raised by the superclass initializer or by setting attributes will propagate to the caller.

## State Changes:
    Attributes READ:
        - None (this implementation does not read any existing instance attributes).
    Attributes WRITTEN:
        - self.line_number is assigned the provided line_number.
        - self.row is assigned the provided row.
        - The base class initializer is invoked with msg, which typically sets the exception message state on the instance.

## Constraints:
    Preconditions:
        - No internal type or value checks are performed. Callers are responsible for passing appropriate types (line_number as int or None; row in the expected row representation; msg as string-like).
    Postconditions:
        - After construction, the instance has attributes line_number and row equal to the provided values, and the exception message has been initialized by CustomException.__init__.

## Side Effects:
    - No I/O, logging, or external service interactions.
    - Mutates only the new exception instance (sets attributes on self); no other objects are modified.

## `csvkit.exceptions.LengthMismatchError` · *class*

## Summary:
Represents a CSV validation error raised when a parsed CSV row contains a different number of columns than expected. It records the source line number, the offending row, a standard human-readable message, and provides a convenience property for the row length.

## Description:
LengthMismatchError is constructed when a CSV validator or parser detects that a row does not contain the expected number of columns. Typical callers include CSV parsing/validation routines that compare each parsed row's column count against an expected schema or header-derived length and want to raise a typed exception that carries both the offending row and its location (line number).

This class exists to:
- Provide a clear, standardized message describing the mismatch (e.g., "Expected 5 columns, found 3 columns").
- Carry the context required by error handlers and loggers: the numeric line identifier and the raw row payload.
- Offer a convenience .length property that returns the current number of elements in the stored row.

LengthMismatchError is a small, focused subclass of CSVTestException; it adds no new public mutation behaviors beyond the message formatting and the .length accessor.

## State:
Public attributes (inherited or set at construction):
- line_number (inherited from CSVTestException)
  - Type: typically int (no runtime enforcement)
  - Meaning: identifies the line in the source CSV that produced the row
  - Invariant: set at construction and not modified by this class

- row (inherited from CSVTestException)
  - Type: any object representing the parsed row (commonly list or tuple)
  - Meaning: the row data that failed validation
  - Invariant: stored verbatim at construction; not mutated by this class

- message (inherited via the base exception chain)
  - Type: str
  - Meaning: the human-readable error message produced during construction (see below)
  - Invariant: set by LengthMismatchError.__init__ and forwarded to the base exception constructor

Computed property:
- length (property)
  - Type: int
  - Value: result of len(self.row)
  - Constraints: requires that self.row supports the built-in len() operation; otherwise len() will raise TypeError
  - Invariant: reflects the current length of self.row at time of access (if callers mutate the stored row externally, .length will reflect that mutation)

Constructor parameters (constraints and notes):
- line_number
  - Required positional argument. No validation is performed; callers should pass an appropriate identifier (commonly an integer).
- row
  - Required positional argument. Must be a value the caller intends to inspect later; recommended to be a sequence (list/tuple) so len(row) succeeds.
- expected_length
  - Required positional argument. Intended to be an integer representing the expected number of columns. No type enforcement is performed by this class; passing a non-integer may cause the message formatting to raise a TypeError.

Class invariants:
- After initialization, the instance must have .line_number, .row, and the base exception message available.
- .length always returns len(self.row) when accessed; the class does not cache or otherwise alter that value.

## Lifecycle:
Creation:
- Instantiate with three positional arguments in this order:
    1. line_number — source line identifier (commonly int)
    2. row — the parsed CSV row (commonly list or tuple)
    3. expected_length — expected column count (commonly int)
- The constructor formats a message using the pattern: "Expected %i columns, found %i columns" % (expected_length, len(row)) and delegates to CSVTestException.__init__(line_number, row, msg).

Usage:
- Typical usage is to construct and immediately raise this exception from a CSV validator:
    - Create: err = LengthMismatchError(line_no, row, expected_len)
    - Raise: raise err
- Error handlers catching this exception can inspect:
    - err.line_number — which line caused the error
    - err.row — the offending row contents
    - str(err) or err.message — the formatted explanatory message
    - err.length — convenience numeric count of columns actually present

Destruction / cleanup:
- No special cleanup is required. The exception holds only simple data references and does not manage external resources or implement context manager protocols.

## Method Map:
flowchart LR
    Init[__init__(line_number, row, expected_length)] --> FormatMsg[format message: "Expected %i columns, found %i columns"]
    FormatMsg --> SuperInit[CSVTestException.__init__(line_number, row, msg)]
    SuperInit --> Ready[Instance with .line_number, .row, message]
    Ready --> Raise[raise instance]
    Ready --> AccessLength[access .length property -> computes len(self.row)]

## Raises:
- TypeError (or other exceptions) can be raised during construction if:
    - len(row) fails because row does not support __len__ (TypeError).
    - The string formatting with %i fails because expected_length is an incompatible type (TypeError).
    - Any exception raised by CSVTestException.__init__ (propagated).
- There are no additional explicit raises inside LengthMismatchError beyond those that may originate from len(), the string formatting, or the base class constructor.

## Example:
- Typical creation, raising, and handling (conceptual, line-oriented):
    1. Validator detects mismatch at line 42: row = ['a','b','c']; expected_len = 5
    2. Create: ex = LengthMismatchError(42, row, expected_len)
    3. Raise: raise ex
    4. Catcher:
       - except LengthMismatchError as e:
           - report = "Line %s: %s (found %d columns)" % (e.line_number, str(e), e.length)
           - log(report)
    5. The message available from the exception will read: "Expected 5 columns, found 3 columns"

### `csvkit.exceptions.LengthMismatchError.__init__` · *method*

## Summary:
Initializes an exception instance that records a CSV row and line number and sets a standardized message indicating the expected versus actual column count.

## Description:
Constructs the error message "Expected %i columns, found %i columns" by substituting expected_length and len(row), then delegates attribute initialization to the CSVTestException base class by calling its initializer with (line_number, row, msg). This initializer encapsulates only the message construction for a length-mismatch condition and relies on the base class to assign common exception attributes.

This method is intended to be instantiated at the point code detects that a row's number of columns differs from the expected count.

## Args:
    line_number (int):
        The index/identifier of the CSV line where the mismatch was detected. The method does not validate the numeric range or whether this is 0-based or 1-based.
    row (object supporting len()):
        The parsed row object whose length will be measured via len(row) to determine the actual column count.
    expected_length (int):
        The expected number of columns for the row; used only to format the message.

## Returns:
    None
    As an initializer, it does not return a value. After execution the instance is a fully-initialized exception object with its message set and base-class attributes assigned.

## Raises:
    TypeError:
        If len(row) raises TypeError (for example, row does not support __len__), that exception will propagate from this initializer.
    Any exception raised by CSVTestException.__init__ or Exception.__init__ (for example, if those initializers raise due to invalid arguments) will also propagate.

## State Changes:
Attributes READ:
    None of self.<attr> fields are read by this initializer. It computes len(row) from the provided argument but does not inspect existing attributes on self.

Attributes WRITTEN:
    self.line_number (assigned by CSVTestException.__init__ to the provided line_number)
    self.row (assigned by CSVTestException.__init__ to the provided row)
    The exception message/args are set via calling CSVTestException.__init__(..., msg) which ultimately delegates to Exception.__init__.

## Constraints:
Preconditions:
    - row must be an object for which len(row) is valid and does not raise, unless the caller intends to handle such errors.
    - expected_length and line_number should be provided (the method does not perform type enforcement).

Postconditions:
    - self.line_number equals the provided line_number.
    - self.row equals the provided row.
    - The instance message equals the string produced by Python's old-style formatting:
      "Expected %i columns, found %i columns" % (expected_length, len(row)).

## Side Effects:
    - No I/O or external service calls.
    - Only mutates the new exception instance (via the base-class initializer). No external objects are modified.

### `csvkit.exceptions.LengthMismatchError.length` · *method*

## Summary:
Read-only property that returns the number of elements in the stored row object (the result of len(self.row)). It does not modify the instance.

## Description:
This property simply returns len(self.row). It is declared as a property on LengthMismatchError to provide a clear, named accessor for the row's column count when reporting or inspecting the exception.

Context and callers:
- The source for this module shows no callers within the same file. Call sites are expected to be error-handling, logging, or reporting code that inspects a caught LengthMismatchError to include the actual column count.
- In LengthMismatchError.__init__, the constructor calls super().__init__(line_number, row, msg), passing row to the superclass. Therefore, this property depends on self.row being present on the instance (typically set by the class hierarchy during initialization).

Why this is a separate property:
- Encapsulates the common operation len(self.row) behind a descriptive name, improving readability at call sites and centralizing the semantic meaning of "length" for the exception object.

## Args:
None.

## Returns:
int
    The integer returned by built-in len(self.row). Expected to be >= 0 for sequence-like row objects.

## Raises:
TypeError
    - If self.row is None or an object that does not implement __len__, the built-in len() will raise TypeError and that exception will propagate.
Any exception raised by row.__len__ will propagate unchanged.

## State Changes:
Attributes READ:
    - self.row

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - The instance must have an attribute self.row available (the constructor forwards row to the superclass, so the attribute is typically present after initialization).
    - self.row must be an object for which len(self.row) is defined (implements __len__).

Postconditions:
    - No mutation of the object; the instance state is unchanged.
    - On success, returns an integer equal to len(self.row).

## Side Effects:
    - None. This property performs no I/O, makes no external calls, and does not mutate objects outside of self.

## `csvkit.exceptions.InvalidValueForTypeException` · *class*

## Summary:
Represents an error indicating a particular value could not be converted to a requested/expected type at a specific position (index). It encapsulates the index, the offending value, and the target type, and forwards a human-readable message to its CustomException base.

## Description:
This exception is intended to be instantiated and raised when a value cannot be coerced/converted to the expected "normal" type during parsing or validation (for example, converting a CSV field to int/float/date). Typical usage is to create and raise this exception from conversion/validation routines that track the field index (or column/position), the raw value that failed conversion, and the target type the code attempted to convert to.

The class does not perform conversion itself; it is a rich error object that records context about the failure and produces a formatted message passed to the base CustomException.

## State:
- index (int)
  - Type: int (expected)
  - Role: position or ordinal where the value occurred (e.g., column index, row index, or field index).
  - Constraints: should be an integer; used with %i formatting in the message. If a non-integer that cannot be formatted as an integer is passed, message formatting may raise TypeError.
- value (Any)
  - Type: any Python object
  - Role: the actual value that could not be converted. The value is stored verbatim and used in the formatted message via %s (string conversion).
  - Constraints: None; must be representable via str() for the message to be meaningful.
- normal_type (Any)
  - Type: typically a type object (e.g., int, float, datetime.date) or a descriptor whose str() identifies the target type
  - Role: describes the expected/target type for conversion; included in the message via %s formatting.
  - Constraints: None strictly enforced; recommended to pass a type or a human-friendly identifier.

Class invariants:
- After initialization, the instance will have attributes index, value, and normal_type set to the provided values.
- The exception message returned by str(instance) or instance.args[0] is the formatted string:
  Unable to convert "<value>" to type <normal_type> (at index <index>)

## Lifecycle:
- Creation:
  - Required arguments: index, value, normal_type
  - Example instantiation: InvalidValueForTypeException(2, "abc", int)
  - The constructor sets the three attributes and builds a message, then calls the base class constructor with that message.
- Usage:
  - Typical pattern: raise InvalidValueForTypeException(index, value, normal_type) when a conversion fails.
  - Consumers of the exception can catch it and examine instance.index, instance.value, and instance.normal_type to produce diagnostics, logs, or recovery behavior.
  - No additional methods are defined on this class; it relies on the base CustomException for standard exception behavior.
- Destruction:
  - No special cleanup required; this exception is a plain object and follows normal Python garbage collection. It is not a context manager and has no close/dispose responsibilities.

## Method Map:
graph LR
  A[Caller performing conversion] --> B[Instantiate InvalidValueForTypeException(index, value, normal_type)]
  B --> C[__init__ sets attributes: index, value, normal_type]
  C --> D[format message: 'Unable to convert "%s" to type %s (at index %i)']
  D --> E[Call CustomException.__init__(msg)]
  E --> F[Exception instance created and can be raised]

## Raises:
- TypeError:
  - Trigger: If the provided index value cannot be formatted with %i (for example, index is a string that cannot be coerced to int), the formatting operation in __init__ may raise TypeError.
  - Trigger: If CustomException.__init__ raises TypeError for the passed message, that will propagate.
- Any exception raised by CustomException.__init__ may propagate (e.g., if the base class validates or rejects the message).

Note: The constructor itself does not explicitly validate types of its arguments; it relies on the formatting operation and the base class for any further validation.

## Example:
Create and raise the exception, then catch it and inspect context:

inst = InvalidValueForTypeException(3, "abc", int)
# The exception's message will be:
#   Unable to convert "abc" to type <class 'int'> (at index 3)
# Access details:
#   inst.index        -> 3
#   inst.value        -> "abc"
#   inst.normal_type  -> int

# Typical raising pattern:
# raise InvalidValueForTypeException(field_index, raw_value, expected_type)
# Typical handling pattern:
# try:
#     ... conversion code ...
# except InvalidValueForTypeException as e:
#     logger.error("Conversion failed at index %s for value %r -> expected %s", e.index, e.value, e.normal_type)

### `csvkit.exceptions.InvalidValueForTypeException.__init__` · *method*

## Summary:
Initializes the exception instance by recording the index, offending value, and target (normal) type on the object and creating a human-readable error message which is passed to the exception base class.

## Description:
This constructor is called when a conversion/validation routine needs to create an error object describing that a particular value could not be converted to an expected type at a specific position. Known callers and contexts:
- Conversion/parsing code paths that coerce CSV fields (or similar input fields) to a target type (e.g., int, float, date) and must signal a failure for a particular field.
- Validation routines that track a field/column/row index and raise a typed exception to report conversion failure.

Typical lifecycle stage: invoked at the point where a conversion attempt fails and the code raises an exception to abort or record the error for reporting. It exists as a dedicated constructor to centralize and standardize: 1) storage of the three contextual attributes (index, value, normal_type) and 2) consistent error message formatting before delegating to the base exception initializer.

## Args:
    index (int): The integer position where the value occurred (e.g., column index, field index, or ordinal). Required. The constructor formats this into the message using %i, so it must be an integer-compatible value.
    value (Any): The raw value that failed conversion. Stored verbatim and formatted into the message using %s (string conversion). Required.
    normal_type (Any): Descriptor of the expected or target type (commonly a Python type object such as int or float, or another object whose str() yields a human-friendly name). Stored and formatted into the message using %s. Required.

## Returns:
    None — standard constructor behavior. After return, the instance is initialized with the provided attributes and a formatted message available via the exception's args or str(instance).

## Raises:
    TypeError:
        - If the provided index cannot be formatted with %i (for example, a value that cannot be interpreted as an integer), the string formatting expression will raise TypeError.
        - If the base class (CustomException.__init__) raises TypeError (for example, due to its own validation of the message), that exception will propagate unchanged.
    Any exception raised by CustomException.__init__ may also propagate (documented here as pass-through behavior).

## State Changes:
- Attributes READ:
    - None of self.<attr> are read prior to assignment; the constructor uses only the provided arguments.
- Attributes WRITTEN:
    - self.index is set to the provided index argument.
    - self.value is set to the provided value argument.
    - self.normal_type is set to the provided normal_type argument.
    - Additionally, by calling the base class initializer with the formatted message, the instance's exception state (for example, args or any base-class-managed message fields) will be set by the base class.

## Constraints:
- Preconditions:
    - Caller must supply all three positional arguments: index, value, normal_type.
    - index should be an integer (or integer-convertible for %i formatting) to avoid message-formatting TypeError.
    - value and normal_type should be representable via str() for the resulting message to be meaningful.
- Postconditions:
    - After construction, instance.index, instance.value, and instance.normal_type will contain the supplied values.
    - The instance will have a message equivalent to:
      Unable to convert "<value>" to type <normal_type> (at index <index>)
      accessible as instance.args[0] and via str(instance) (subject to base-class behavior).
    - No other attributes defined in this constructor will remain uninitialized.

## Side Effects:
- No I/O operations are performed.
- The method invokes the base class constructor (super().__init__(msg)), which mutates the exception's built-in state (for example, populating args). Any side effects implemented by the base class (CustomException) will occur.
- No external objects are mutated by this constructor beyond the newly-created exception instance itself.

## `csvkit.exceptions.RequiredHeaderError` · *class*

## Summary:
An exception class that specifically denotes a missing required header in CSV processing. It is a semantic subclass of CustomException and does not add state or behavior.

## Description:
Instantiate or raise RequiredHeaderError from CSV parsing or validation code when a required column/header name is absent from an input CSV. Typical callers include header validators, CSV readers that enforce schema, and higher-level import/ingest routines that verify column presence before row-level processing.

Purpose and responsibility boundary:
- Purpose: Provide a distinct exception type so callers can catch the specific "required header missing" condition separately from other error types in the CustomException hierarchy.
- Boundary: This class does not implement validation logic itself — it is a signaling type only. All construction, message formatting, and additional metadata behavior come from its superclass, CustomException.

Examples of when to use:
- After comparing expected headers to the CSV's header row and detecting that "id" or "email" is absent.
- To abort processing early with a clear semantic error that can be caught and presented to users.

Note: RequiredHeaderError does not override or provide its own __init__, attributes, or methods; it inherits them verbatim from CustomException. Consult CustomException's documentation or source to determine the exact constructor signature and any metadata fields available on instances.

## State:
- Direct attributes: None declared on RequiredHeaderError.
- Inherited attributes: Any attributes, message text, or metadata are those defined by CustomException.
- Valid values / invariants:
    - There are no new invariants introduced by this subclass.
    - Any invariants about message content, metadata keys, or immutability are those enforced by CustomException.

## Lifecycle:
- Creation:
    - Instantiate using the same constructor signature as CustomException (RequiredHeaderError does not define its own __init__). Example instantiation patterns depend on CustomException:
        - If CustomException supports a no-arg construction: RequiredHeaderError()
        - If CustomException expects a message: RequiredHeaderError("Missing required header: 'id'")
      Because the exact signature is defined by CustomException, confirm required/optional parameters there before constructing.
    - Import path:
        from csvkit.exceptions import RequiredHeaderError
- Usage:
    - Typical use is to raise the exception at header-validation time:
        raise RequiredHeaderError(...)  # supply args as permitted by CustomException
    - Catching patterns:
        - Catch only this condition:
            try:
                validate_headers(headers)
            except RequiredHeaderError as e:
                handle_missing_header(e)
        - Catch all csvkit custom errors:
            try:
                process_csv(...)
            except CustomException as e:
                handle_all_csvkit_errors(e)
    - Preserving context: If wrapping another exception or re-raising, consider using "raise RequiredHeaderError(...) from original_exc" to retain chained context.
- Destruction:
    - No special cleanup. Instances are regular exceptions subject to normal garbage collection. This class is not a context manager and does not hold resources that require explicit release.

## Method Map:
graph TD
    A[CustomException class] --> B[RequiredHeaderError (subclass)]
    B --> C[raise RequiredHeaderError(...)]
    C --> D[except RequiredHeaderError as e]
    C --> E[except CustomException as e]

(RequiredHeaderError inherits all methods and attributes from CustomException and introduces no new callable methods.)

## Raises:
- __init__: RequiredHeaderError itself does not raise new exception types. Any exceptions raised during instantiation (for example, TypeError for wrong arguments) originate from CustomException's constructor and its validations. Documented callers should rely on CustomException's doc for precise constructor error behavior.

## Example:
- Importing and raising (illustrative — confirm constructor args with CustomException):
    from csvkit.exceptions import RequiredHeaderError

    # Validator detects missing header 'id'
    raise RequiredHeaderError("Missing required header: 'id'")

- Catching the specific missing-header condition:
    try:
        validate_headers(headers)
    except RequiredHeaderError as e:
        # Handle missing-header error specifically (user message, fallback behavior, etc.)
        logger.error("CSV validation failed: %s", e)

- Catching all csvkit custom exceptions:
    from csvkit.exceptions import CustomException
    try:
        process_csv(path)
    except CustomException as e:
        # Generic handler for csvkit exceptions (includes RequiredHeaderError)
        handle_csv_error(e)

For exact constructor parameters, message formatting, and available metadata on instances, refer to the CustomException documentation or source.

