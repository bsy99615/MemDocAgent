# `exceptions.py`

## `hypertools._shared.exceptions.HypertoolsError` · *class*

## Summary:
A minimal, package-specific exception type used to signal errors originating from the hypertools package.

## Description:
HypertoolsError is a lightweight subclass of the built-in Exception type that exists solely to provide a distinct exception class for errors raised by hypertools internals. It does not add behavior beyond Exception; its value lies in enabling callers and tests to catch all hypertools-specific errors using a single exception class (for example, except HypertoolsError:). Instantiate this class when an error occurs within hypertools that should be reported to callers as a package-defined error rather than a built-in error type.

Scenarios where this class should be instantiated:
- When an internal hypertools function detects a condition that prevents normal operation and wants to raise a package-specific error.
- When library code wants to raise a clear, catchable signal that an operation failed due to hypertools logic (rather than a TypeError, ValueError, etc.).

Motivation and responsibility boundary:
- Responsibility: act as the canonical, minimal exception type for hypertools error signaling.
- Boundary: do not implement additional payload, state, or behavior on this class; use chained exceptions or message text for contextual details.

## State:
- This class defines no additional instance attributes beyond those provided by the base Exception class.
- There are no class attributes or configuration values.
- __init__ parameters: Inherits Exception.__init__; callers may pass a single message string, no enforced parameter names or types are introduced by this subclass.
- Valid values: Any arguments accepted by Exception are acceptable (commonly, a single str message). There are no additional invariants to maintain.

Class invariants:
- Instances are plain Exception objects; there are no additional invariants beyond those of Exception.
- The identity of the class (i.e., being a distinct subclass) is the only semantic guarantee used by client code to differentiate hypertools errors.

## Lifecycle:
Creation:
- Instantiate by calling the class with optional message or arguments supported by Exception (e.g., an error message). No required positional parameters.

Usage:
- Typical sequence:
  1. Create an instance (implicitly by raising: raise HypertoolsError("reason")).
  2. The exception propagates normally through Python exception handling.
  3. Callers may catch it explicitly (except HypertoolsError:) or catch Exception to handle broadly.
- No additional methods exist; there is no required ordering beyond standard exception raise/catch flow.

Destruction:
- No cleanup responsibilities. Instances are managed by Python's normal garbage collection when no longer referenced.

## Method Map:
flowchart LR
    A[Instantiate HypertoolsError] --> B[Raise exception]
    B --> C[Propagate to caller]
    C --> D[Catch with except HypertoolsError:]
    C --> E[Unhandled -> Python error traceback]

## Raises:
- The class definition itself does not raise exceptions.
- Instantiation and raising of HypertoolsError will behave like raising any Exception; any errors during construction would be those inherited from Exception (e.g., if an argument's __str__ raises when formatting), but the class does not introduce new raise points.

## Example:
- Typical usage scenario (described):
  1. A hypertools internal function detects an unrecoverable configuration issue.
  2. The function signals this by raising a HypertoolsError with a concise message describing the problem.
  3. A higher-level caller can catch HypertoolsError specifically to handle library-level failures, or allow it to propagate to the application to produce an error report.

- Example usage in words:
  - "When a required resource is missing, raise HypertoolsError with an explanatory message; callers can then catch HypertoolsError to present a user-facing error or perform recovery."

## `hypertools._shared.exceptions.HypertoolsBackendError` · *class*

## Summary:
HypertoolsBackendError is a minimal, package-specific exception class (a subclass of HypertoolsError) that carries a single message payload. By name and inheritance it is intended to represent backend-related errors within the hypertools package while remaining a simple, catchable Exception subtype.

## Description:
This class exists to provide a distinct exception type for errors that are associated with "backend" operations in hypertools while preserving the minimal behavior of the base HypertoolsError. It accepts a single message-like argument at construction, forwards that value to the base Exception initialization, and stores it on the instance as the attribute message.

Typical scenarios for instantiation:
- When a backend component or adapter encounters an error condition and the implementation wants to raise a hypertools-specific exception that is still distinguishable from plain Exception or other library errors.
- When code needs to raise an error that can be caught either specifically (except HypertoolsBackendError:) or broadly (except HypertoolsError: or except Exception:).

Motivation and responsibility boundary:
- Responsibility: act as a thin, semantic marker exception for backend-related failures while carrying a human-readable message.
- Boundary: do not implement additional behavior (no automatic logging, no state beyond the message attribute). Use exception chaining or message text for contextual details.

## State:
- Instance attributes:
    - message (any): The value provided as the single constructor argument. Commonly a str describing the error. No type is enforced by the implementation; any object accepted by Exception.__init__ is valid.
- __init__ parameters:
    - message: required positional parameter; no default. The constructor forwards this value to the base class and stores it on self.message.
- Class invariants:
    - Every instance of HypertoolsBackendError is an instance of HypertoolsError and carries a message attribute whose value equals the argument passed to __init__.
    - No other attributes or hidden state are introduced by this class.

## Lifecycle:
- Creation:
    - Instantiate by calling HypertoolsBackendError(message).
    - The constructor calls the parent HypertoolsError (and thus Exception) initializer with the same message, then sets self.message = message.
- Usage:
    - Typical sequence:
        1. Create and raise the exception: raise HypertoolsBackendError(message)
        2. Exception propagates; callers may catch it with except HypertoolsBackendError: or except HypertoolsError:.
        3. Access the payload via e.message or str(e) (the latter provided by the Exception base behavior).
    - There are no methods other than __init__; no required call ordering beyond standard raise/catch flow.
- Destruction:
    - No explicit cleanup responsibilities. Instances are collected by Python's garbage collector once no longer referenced.

## Method Map:
flowchart LR
    A[Call HypertoolsBackendError(message)] --> B[HypertoolsBackendError.__init__]
    B --> C[Call HypertoolsError.__init__(message) / Exception.__init__]
    B --> D[Set instance attribute message = message]
    C --> E[Instance ready to be raised]
    D --> E

## Raises:
- The constructor does not explicitly raise exceptions.
- Instantiation/raising behaves like any Exception subclass: if the provided message object's __str__ or other object internals raise during initialization or when formatting, that error may surface during exception construction or when the exception is converted to a string. The class itself introduces no additional raise points.

## Example:
- Creation and raise:
    1. Construct the exception with a descriptive message (commonly a str). The message is required:
       - HypertoolsBackendError("backend failed to initialize")
    2. Raise it to signal a backend failure:
       - raise HypertoolsBackendError("backend failed to initialize")
    3. Catching and inspecting:
       - except HypertoolsBackendError as e:
           - Access the payload via e.message (the exact object passed at construction)
           - Or use str(e) to obtain the message text as produced by Exception.__str__()

- Notes:
    - Because this class subclasses HypertoolsError (which itself is a minimal Exception subtype), client code may catch HypertoolsError to handle all hypertools-related errors including this one.

### `hypertools._shared.exceptions.HypertoolsBackendError.__init__` · *method*

## Summary:
Initializes a HypertoolsBackendError instance by forwarding the provided message to the parent exception initializer and storing the same message on the instance as self.message.

## Description:
This constructor runs when code constructs or raises a HypertoolsBackendError (for example, in backend adapters or other backend-related components that detect an error and create a typed hypertools exception). It executes during the exception creation stage immediately before the exception is raised or returned to caller code.

Known callers / invocation contexts:
- Backend adapters, connectors, or other "backend" components within hypertools that detect failure conditions and raise a backend-specific error to signal the problem.
- Any code that explicitly constructs this exception to be raised or passed up to higher-level handlers:
    - Typical usage: raise HypertoolsBackendError("descriptive message")
The initializer is a dedicated method to ensure two things are always performed consistently whenever the exception is created:
- The parent class initializer (HypertoolsError -> Exception) receives the message so standard exception behavior (str(e), exception chaining) works as expected.
- The original message payload is accessible via a dedicated attribute self.message on the instance without requiring callers to inspect base-class internals.

## Args:
    message (Any): Required. The payload describing the error (commonly a str). Any object accepted by Exception.__init__ is permitted, including None.

## Returns:
    None: As an initializer, it does not return a value; it only configures the new instance.

## Raises:
    None explicitly: The method does not intentionally raise. However, exceptions may propagate if:
    - The provided message object raises during operations triggered by Exception.__init__ (rare), or
    - Later formatting or inspection of the exception (e.g., converting to str(e)) triggers errors from the message object.
The class itself does not introduce additional raise conditions.

## State Changes:
Attributes READ:
    - None. The method does not read any pre-existing instance attributes.

Attributes WRITTEN:
    - self.message: set to the provided message argument.

## Constraints:
Preconditions:
    - Must be called on an instance of HypertoolsBackendError (normal Python construction semantics).
    - Caller must supply the message argument (no default).

Postconditions:
    - The parent exception initializer has been invoked with the same message (so built-in Exception behavior reflects that message).
    - The instance has an attribute self.message equal to the provided argument and is ready to be raised or inspected.

## Side Effects:
    - Calls super().__init__(message), which initializes the parent exception state.
    - Mutates the instance by assigning self.message.
    - No I/O, logging, networking, or external mutations are performed by this method.

## `hypertools._shared.exceptions.HypertoolsIOError` · *class*

## Summary:
A package-specific exception type representing I/O-related failures in hypertools; it subclasses both HypertoolsError and OSError and carries a human-readable message payload.

## Description:
HypertoolsIOError is intended to be raised when an I/O operation performed by hypertools (for example, file reading/writing, filesystem access, or other OS-level I/O interactions used by the library) fails in a way that should be reported as a hypertools-specific error while still being compatible with OSError-based handlers. It combines the semantics of the package-level HypertoolsError (so callers can catch all hypertools errors) with OSError (so callers that expect built-in I/O errors can also catch it).

Scenarios to instantiate:
- When a hypertools routine encounters an unrecoverable I/O condition (missing file, permission denied, failed read/write) and wants to raise an exception that is both identifiable as a hypertools error and as an OSError.
- Where library code intends to present a clear message to callers while preserving the ability for external code to catch OSError.

Known creation pattern:
- Constructed directly with a single message argument and typically raised immediately: raise HypertoolsIOError("explanatory message").

Motivation and responsibility boundary:
- Responsibility: carry an error message representing an I/O failure and serve as a catchable, package-specific I/O exception.
- Boundary: this class does not perform I/O itself or wrap underlying exception metadata beyond storing the provided message and inheriting standard exception behavior from OSError/Exception. It is a signaling object only.

## State:
- Attributes:
    - message (any, commonly str): value supplied by the caller to __init__. The class stores this on self.message. Although the implementation does not enforce type, callers should pass a string; any object accepted will be stored as-is.
    - args (tuple): inherited from Exception/OSError; after initialization args will contain the original message as its first element (args[0] == message).
    - standard Exception attributes (inherited): e.g., __traceback__ when raised, and any attributes provided by OSError on contexts where system-specific details are attached (this class does not add those automatically).

- Parameter constraints:
    - __init__ requires a single positional parameter message (no default). There is no internal validation of message; it is expected to be a descriptive message (string) but may be any object.

- Class invariants:
    - After construction, self.message is equal to the first element of self.args (if any).
    - The instance is simultaneously an instance of HypertoolsError and OSError, so isinstance checks for either base class must hold.

## Lifecycle:
- Creation:
    - Instantiate by calling HypertoolsIOError(message). The message parameter is required.
    - Typical idiom: raise HypertoolsIOError("failed to read file /path/to/file").
- Usage:
    - Immediately raise the instance or propagate it: raise HypertoolsIOError(message)
    - Consumers may catch it in any of these forms:
        - except HypertoolsIOError:  # package-specific handling
        - except HypertoolsError:    # catch all hypertools exceptions
        - except OSError:            # catch as a generic I/O/OS error
    - There are no additional methods to call on the instance; it behaves as a normal exception object.
- Destruction:
    - No cleanup or resource management responsibilities. Instances are garbage-collected per normal Python semantics.

## Method Map:
flowchart LR
    A[Call HypertoolsIOError(message)] --> B[HypertoolsIOError.__init__]
    B --> C[super().__init__(message)] --> D[Exception/OSError initialization (args set)]
    B --> E[self.message = message]
    F[Raise exception] --> G[Propagate]
    G --> H[Catch except HypertoolsIOError:]
    G --> I[Catch except HypertoolsError:]
    G --> J[Catch except OSError:]

## Raises:
- __init__ itself does not deliberately raise any exceptions.
- Possible runtime errors during construction:
    - If the provided message object's __str__ or related operations raise an exception during formatting or when the exception machinery inspects the message, that underlying exception will propagate (this is not unique to this class; it is a general risk when exception message objects have buggy dunder methods).
- No class-level or constructor-level validation errors are defined by this implementation.

## Example:
- Typical usage (narrative):
    1. A hypertools function fails to open a required file.
    2. The function signals the failure by raising HypertoolsIOError with an explanatory message.
    3. Upstream code may catch the error either specifically or via OSError.

- Minimal one-line example:
    raise HypertoolsIOError("unable to read configuration file '/etc/hypertools.cfg'")

- Catching examples (described):
    - To handle library-specific I/O failures:
        except HypertoolsIOError as e:
            # handle hypertools I/O error, inspect e.message or str(e)
    - To handle all hypertools errors:
        except HypertoolsError:
            # generic hypertools error handling
    - To treat it as a platform/OS error:
        except OSError:
            # generic OS-level error handling

### `hypertools._shared.exceptions.HypertoolsIOError.__init__` · *method*

## Summary:
Initializes the exception instance by recording the provided human-readable message on the instance and forwarding it to the base exception initializer so standard Exception attributes (args) are populated.

## Description:
This constructor is called during creation of a HypertoolsIOError when the library needs to signal an I/O-related failure with a package-specific exception that remains compatible with OSError handlers. Typical callers are code paths that detect unrecoverable I/O conditions (for example, failed file open/read/write, missing configuration file, or a permission error) which then raise HypertoolsIOError with an explanatory message. The usual lifecycle stage is immediately before raising the exception (e.g., raise HypertoolsIOError("explanatory text")).

This logic is implemented as a dedicated constructor rather than being inlined at raise sites to:
- Ensure the provided message is stored on the instance as a named attribute (self.message) for convenient inspection by callers and tests.
- Guarantee the base Exception/OSError initialization occurs uniformly (so self.args contains the message).
- Provide a single location for any future augmentation of error metadata (stacking, codes, or extra attributes) without changing call sites.

## Args:
    message (Any):
        - Required positional argument.
        - A human-readable description of the I/O failure. Commonly a str, but any object is accepted and stored as-is.
        - There is no validation or coercion performed by the constructor.

## Returns:
    None
    - As with all Python constructors, __init__ returns None and yields a fully-initialized exception instance observable by the caller (typically raised immediately).

## Raises:
    - No exceptions are explicitly raised by this constructor.
    - Practical note: if the supplied message object has buggy dunder methods (for example, __str__ or __repr__ that raise), those errors may surface later when the exception is stringified or inspected; such propagation is incidental and not caused by explicit validation in this constructor.

## State Changes:
    Attributes READ:
        - None (the method does not read any pre-existing instance attributes).

    Attributes WRITTEN:
        - self.message: set to the provided message object.
        - self.args: indirectly set by calling super().__init__(message); after the call, args will contain the message (typically args == (message,)).

## Constraints:
    Preconditions:
        - A single positional argument message must be provided when calling the constructor.
        - Callers should prefer passing a descriptive string; passing other types is allowed but may impact downstream formatting/inspection.

    Postconditions:
        - After return, self.message is identical to the provided message argument.
        - After super().__init__(message) completes, self.args[0] == message (i.e., the message is preserved in the standard Exception args tuple).
        - The created instance behaves as a HypertoolsIOError and, by class design, is also compatible with catching as HypertoolsError and OSError.

## Side Effects:
    - No I/O or external service calls are performed.
    - The only side effects are mutations to the newly created exception object (self.message and self.args). There are no mutations to objects outside self.

