# `exceptions.py`

## `jwt.exceptions.PyJWTError` · *class*

## Summary:
PyJWTError is the base exception type used by the PyJWT library to represent library-specific errors; it is a direct, empty subclass of Python's built-in Exception and exists solely as a distinct marker type.

## Description:
PyJWTError does not add behavior or state beyond Python's built-in Exception. It is intended to be raised by the PyJWT library (or by client code interoperating with PyJWT) to signal error conditions specific to JWT processing. Typical uses:
- Raised directly for simple error signaling where no additional context is needed.
- Used as the common base class for more specific PyJWT exception types so callers can catch all library errors with a single except PyJWTError: clause.

Motivation and responsibilities:
- Provide a single, library-scoped exception type so consumers can differentiate PyJWT-raised errors from other exceptions.
- Serve as a stable type for public exception handling APIs (catching, re-raising, and documentation) without exposing implementation details.

Known callers / factories:
- Any code within the PyJWT codebase that needs to raise or re-raise a JWT-related error may instantiate or subclass PyJWTError.
- Client code will commonly use it in except clauses to handle library errors.

## State:
This class defines no new attributes. All state and behavior are inherited from Python's built-in Exception (BaseException) machinery.

Inherited attributes available on instances:
- args (tuple): positional arguments passed to the exception constructor; often contains the error message as the first element.
- __cause__ (optional): chained exception cause (set by raise ... from ... or manually).
- __context__ (optional): the exception context when another exception was active.
- __traceback__ (optional): traceback object populated when the exception is raised.

Constructor parameters and constraints:
- Because PyJWTError does not override __init__, it accepts the same parameters as Exception:
  - Typical usage: PyJWTError() or PyJWTError("message") or PyJWTError(arg1, arg2, ...)
- There are no additional constraints enforced by PyJWTError itself (no validation, no required parameters).

Class invariants:
- Instances remain small marker exceptions with their args tuple representing constructor arguments.
- No PyJWT-specific attributes or state are present or expected to be present by callers.

## Lifecycle:
Creation:
- Instantiate directly: PyJWTError() or PyJWTError("message") or with any arguments accepted by Exception.
- Alternatively, create subclasses that inherit from PyJWTError for more specific error types.

Usage:
- Raise: raise PyJWTError("reason")
- Catch: use except PyJWTError: to handle all PyJWT library exceptions.
- Re-raise or chain exceptions using standard Python exception chaining (raise ... from ...).

Destruction / cleanup:
- No explicit cleanup is required. PyJWTError does not implement context manager protocols nor resource management methods. Normal Python garbage collection and exception lifecycle apply.

## Method Map:
graph LR
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: PyJWTError is a direct subclass of Exception and inherits its methods and properties from Exception / BaseException.)

## Raises:
- PyJWTError.__init__ (inherited from Exception) does not raise library-specific exceptions. There are no additional exceptions raised by PyJWTError itself. Any exceptions raised during instantiation would originate from the Python runtime (for example, if non-standard __init__ behavior is introduced by monkeypatching Exception, which is outside normal usage).

## Example:
- Create and raise:
    raise PyJWTError("Invalid token format")

- Catching library errors:
    try:
        do_jwt_operation()
    except PyJWTError as e:
        # Handle all PyJWT-related errors here
        log_error(str(e))
        raise

- Subclassing for a more specific error:
    class MySpecificError(PyJWTError):
        pass

Notes:
- Because PyJWTError does not provide additional attributes, prefer passing context via the message or by raising from another exception (raise PyJWTError("msg") from original_exc).

## `jwt.exceptions.InvalidTokenError` · *class*

## Summary:
InvalidTokenError is a specific marker exception indicating that a JWT (JSON Web Token) is invalid; it is a direct subclass of PyJWTError and carries no additional state or behavior.

## Description:
InvalidTokenError is used to signal token-related validation failures (for example: malformed token, invalid signature, unsupported claims, or other token integrity/validation problems). It exists so callers can catch a precise, semantically meaningful exception when JWT validation fails while still allowing broader handling via the PyJWTError base class.

Scenarios where this class should be instantiated:
- Raised by JWT validation routines when a token is syntactically or semantically invalid.
- Raised by higher-level helper utilities that detect token problems and want to classify the failure as an "invalid token" case.
- Client code may instantiate or raise this exception to normalize error handling across components that integrate with PyJWT.

Known caller pattern:
- Any JWT-processing function in the library or application that determines a token is invalid may raise InvalidTokenError("reason") or raise InvalidTokenError from another exception to preserve context.
- Callers that want to handle only invalid-token conditions can use except InvalidTokenError:; callers wishing to handle all library exceptions can use except PyJWTError:.

Motivation and responsibility boundary:
- Provide a distinct, catchable type that represents token-invalid conditions separate from other JWT error categories.
- Do not attempt to encapsulate additional context (timestamp, token payload, validation metadata) — those should be conveyed via the exception message or by raising from an underlying exception.

## State:
- This class defines no new attributes; it inherits all instance state from Python's built-in Exception via PyJWTError.
- Inherited attributes available on instances:
  - args (tuple): positional arguments passed to the constructor (commonly a single message string).
  - __cause__, __context__, __traceback__ as provided by Python's exception model.
- __init__ parameters:
  - Inherits Exception.__init__; callers may pass zero or more positional arguments (typical usage: a single message string).
  - No defaults or additional constraints are imposed by InvalidTokenError itself.
- Class invariants:
  - Instances are simple marker exceptions: no additional attributes are created by InvalidTokenError.
  - The args tuple accurately reflects constructor arguments and is used as the primary carrier of human-readable context.

## Lifecycle:
- Creation:
  - Instantiate directly with zero or more positional arguments: e.g., InvalidTokenError("token expired")
  - Can be raised directly at the point of detection: raise InvalidTokenError("reason")
  - Can be raised while preserving underlying exception context: raise InvalidTokenError("reason") from original_exc
- Usage:
  - Typical usage is immediate raising and catching; there are no lifecycle methods to call on instances.
  - Catching patterns:
    - Specific handling: except InvalidTokenError as e:
    - Broad handling: except PyJWTError as e:  (catches InvalidTokenError as it is a subclass)
- Destruction / cleanup:
  - No cleanup required. Instances are ordinary exception objects managed by Python's exception and garbage-collection mechanisms.
  - InvalidTokenError does not implement context manager protocols or resource cleanup methods.

## Method Map:
graph LR
    InvalidTokenError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: InvalidTokenError is a direct subclass of PyJWTError and inherits behavior from Python's Exception/BaseException hierarchy.)

## Raises:
- InvalidTokenError.__init__ (inherited from Exception) does not introduce new, library-specific raises.
- Instantiation or raising may raise runtime exceptions only if Python's Exception machinery is altered (not typical). Normal creation and raising do not raise additional exceptions.

## Example:
- Raising when a token validation fails:
    raise InvalidTokenError("signature verification failed")

- Raising while preserving an underlying error:
    try:
        decode_token(raw)
    except SomeLowerLevelError as exc:
        raise InvalidTokenError("token decode failed") from exc

- Catching the specific invalid-token condition:
    try:
        validate_token(token)
    except InvalidTokenError as e:
        handle_invalid_token(e)

- Catching all PyJWT library errors (including invalid-token cases):
    try:
        process_jwt(token)
    except PyJWTError as e:
        handle_library_error(e)

## `jwt.exceptions.DecodeError` · *class*

## Summary:
jwt.exceptions.DecodeError — a thin, marker exception subclass used to indicate a JWT decoding/parsing failure; it inherits all behavior and state from InvalidTokenError and carries no additional state.

## Description:
DecodeError is a semantic subtype of InvalidTokenError intended for use (by convention) when code encounters a failure during the decoding or parsing phase of JWT handling (for example: malformed token structure or bytes that cannot be parsed). The class itself introduces no new behavior or stored state beyond what is provided by InvalidTokenError and Python's Exception.

Scenarios where this class may be instantiated:
- Thrown by token-decoding/parsing routines when the raw token cannot be split, base64-decoded, or otherwise parsed correctly.
- Raised by higher-level helpers that want to classify an error specifically as a decoding/parsing failure while still allowing callers to catch InvalidTokenError or PyJWTError for broader handling.
- Client code may raise DecodeError("message") or raise DecodeError from another exception to preserve context; this is a convention for clearer error classification rather than enforced behavior.

Motivation and responsibility boundary:
- Provide an optional, more specific exception type to classify decoding/parsing failures of JWTs while remaining compatible with the InvalidTokenError/PyJWTError hierarchy.
- Do not expect any additional attributes or parsing metadata on DecodeError instances; any extra context should be conveyed via the exception message or exception chaining.

## State:
- DecodeError defines no new attributes; it inherits all instance state from InvalidTokenError and Exception.
- Available inherited attributes:
  - args (tuple): positional arguments passed to the constructor (typically a single message string).
  - __cause__, __context__, __traceback__ as per Python exception semantics.
- __init__ parameters:
  - Inherits Exception.__init__; callers may pass zero or more positional arguments (typical usage: a single message string). No additional parameters or defaults are defined by DecodeError.
- Class invariants:
  - Instances are marker exceptions with no extra mutable state added by this class.
  - The args tuple accurately reflects constructor arguments and is the primary carrier of human-readable context.

## Lifecycle:
- Creation:
  - Instantiate directly: DecodeError("malformed token") or DecodeError() with no arguments.
  - Can be raised directly: raise DecodeError("reason")
  - Can be chained to preserve context: raise DecodeError("reason") from original_exc
- Usage:
  - Typical usage is immediate raising and catching; there are no lifecycle or resource-management methods.
  - Catching patterns:
    - To handle decoding-specific failures: except DecodeError as e:
    - To handle any invalid-token condition: except InvalidTokenError as e: or except PyJWTError as e:
- Destruction / cleanup:
  - No cleanup required. Instances follow normal Python exception lifecycle and garbage collection. DecodeError does not implement context-manager protocols.

## Method Map:
graph LR
    jwt.exceptions.DecodeError --> jwt.exceptions.InvalidTokenError
    jwt.exceptions.InvalidTokenError --> jwt.exceptions.PyJWTError
    jwt.exceptions.PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: DecodeError is a thin subclass used for classification; behavior is inherited from its ancestors.)

## Raises:
- DecodeError.__init__ does not introduce new exceptions. Normal instantiation or raising will not raise additional exceptions beyond standard Python behavior.
- When used within decoding code, callers may chain underlying exceptions using "raise ... from ..." to preserve the original cause.

## Example:
- Raising a decoding failure:
    raise DecodeError("malformed token: unexpected segment count")

- Chaining an underlying exception:
    try:
        parse_segments(raw_token)
    except ValueError as exc:
        raise DecodeError("token parsing failed") from exc

- Catching only decoding failures:
    try:
        decode_token(token)
    except DecodeError as e:
        handle_decode_failure(e)

- Catching any invalid-token condition (including decode errors):
    try:
        process_jwt(token)
    except InvalidTokenError as e:
        handle_invalid_token(e)

## `jwt.exceptions.InvalidSignatureError` · *class*

## Summary:
An exception type that represents a JWT signature verification failure; it is a marker subclass of DecodeError used to signal that a token's signature did not validate.

## Description:
InvalidSignatureError is intended to be raised when a JWT fails cryptographic signature verification — for example, when the recomputed signature does not match the signature embedded in the token, or when the key used to verify the signature is invalid. The class itself adds no behavior or stored state; it exists purely for semantic classification so callers can catch signature-specific failures separately from other decode/validation errors.

Typical scenarios / callers:
- Signature-verification routines in the JWT validation pipeline (e.g., functions that compute and compare HMAC or RSA signatures) raise this exception when verification fails.
- Higher-level decode/verify helpers may raise InvalidSignatureError to indicate a failed signature check while still allowing broader exception handlers to catch DecodeError, InvalidTokenError, or a top-level PyJWTError.
- Client code may raise InvalidSignatureError("reason") or raise InvalidSignatureError from underlying_crypto_error to preserve cause context.

Motivation and responsibilities:
- Provide a distinct, catchable type for signature verification failures while remaining compatible with existing exception hierarchies (DecodeError and its ancestors).
- Do not assume any additional diagnostic fields are present on instances; any contextual information should be supplied in the exception message or via exception chaining.

## State:
- New attributes: none. InvalidSignatureError defines no instance attributes beyond those provided by Exception and its ancestor classes.
- Inherited attributes (available on instances):
  - args (tuple): constructor positional arguments, typically a single message string.
  - __cause__, __context__, __traceback__: standard Python exception attributes for chaining and debugging.
- __init__ parameters:
  - Inherits Exception.__init__; callers may pass zero or more positional arguments (typical use: a single message string). There are no additional parameters or defaults introduced by this class.
- Class invariants:
  - Instances are marker exceptions with no mutable state introduced by this class.
  - The args tuple accurately reflects the constructor arguments and is the primary carrier of human-readable context.

## Lifecycle:
- Creation:
  - Instantiate directly by constructing the exception with optional message(s): InvalidSignatureError("message") or with no arguments.
  - Typically created by raising: raise InvalidSignatureError("signature mismatch")
  - May be chained from another exception to preserve cause: raise InvalidSignatureError("signature verification failed") from underlying_exc
- Usage:
  - Immediately raised by verification code and (optionally) caught by application code.
  - Recommended catch patterns:
    - To handle signature-only failures: except InvalidSignatureError as exc:
    - To handle any decode/verification failures: except DecodeError as exc: or except InvalidTokenError as exc:
  - No special setup, sequencing, or lifecycle methods are required beyond normal raise/catch usage.
- Destruction / cleanup:
  - No cleanup responsibilities. Instances are ordinary Python exceptions managed by normal exception handling and garbage collection.

## Method Map:
graph LR
    jwt.exceptions.InvalidSignatureError --> jwt.exceptions.DecodeError
    jwt.exceptions.DecodeError --> jwt.exceptions.InvalidTokenError
    jwt.exceptions.InvalidTokenError --> jwt.exceptions.PyJWTError
    jwt.exceptions.PyJWTError --> Exception
    Exception --> BaseException

## Raises:
- InvalidSignatureError.__init__ does not raise new exceptions beyond those possible from Python's base Exception constructor (i.e., none in normal usage).
- When used within verification code, callers commonly "raise InvalidSignatureError" to signal a verification failure; that raise may be written with "from" to preserve an underlying exception.

## Example:
- Raising a signature verification failure:
    raise InvalidSignatureError("signature mismatch for token")

- Chaining an underlying crypto error:
    try:
        verify_signature(key, data, signature)
    except CryptoError as cause:
        raise InvalidSignatureError("signature verification failed") from cause

- Catching only signature failures:
    try:
        validate_token(token)
    except InvalidSignatureError as e:
        handle_signature_failure(e)

- Catching any decode/invalid-token error (including signature failures):
    try:
        process_jwt(token)
    except DecodeError as e:
        handle_decode_or_signature_failure(e)

## `jwt.exceptions.ExpiredSignatureError` · *class*

## Summary:
A marker exception type that denotes an expired JWT; it is a direct subclass of InvalidTokenError and carries no additional state or behavior.

## Description:
This class is a semantic specialization of InvalidTokenError intended to distinguish "expired token" failures from other invalid-token conditions. The class itself contains no logic to detect expiration — it only serves as a distinct exception type that validation or decoding code may raise by convention when an expiration condition is observed.

Usage conventions (by convention, not enforced by the class):
- JWT decoding/validation code typically raises this exception when it detects that a token should be considered expired.
- Client code can catch ExpiredSignatureError specifically to trigger expiry-specific behavior (e.g., refresh token flow or re-authentication).

Motivation and boundary:
- Provide a narrow, catchable exception type to represent expiry-related failures distinct from broader invalid-token errors.
- Do not expect structured expiry metadata (timestamps, claim payload) to be attached to instances — such context must be provided via the exception message or by raising from an underlying error.

## State:
- New attributes: none (class body is "pass").
- Inherited attributes:
  - From InvalidTokenError / PyJWTError / Exception:
    - args (tuple): positional arguments passed to the constructor (commonly a single message string).
    - __cause__, __context__, __traceback__ as provided by Python's exception model.
- __init__ parameters:
  - Inherits Exception.__init__; callers may pass zero or more positional arguments (typical: a single human-readable message).
  - No additional parameters, defaults, or constraints are introduced by this class.
- Class invariants:
  - Instances are marker exceptions without additional state.
  - The args tuple must reflect constructor arguments and serve as the primary carrier of human-readable context.

## Lifecycle:
- Creation:
  - Instantiate directly like any Exception:
    - ExpiredSignatureError()
    - ExpiredSignatureError("token expired")
    - ExpiredSignatureError("msg") from underlying_exc
  - Typical creation site: validation code that observes an expiry condition (this is a conventional usage pattern, not enforced by the class).
- Usage:
  - Immediately raised and caught; there are no lifecycle methods.
  - Typical catch patterns:
    - Specific handling: except ExpiredSignatureError as exc:  # handle expiry
    - Broader handling: except InvalidTokenError as exc:    # handle any invalid-token condition
- Destruction / cleanup:
  - No cleanup required. Instances are ordinary Python exceptions managed by the interpreter and garbage collector.

## Method Map:
graph LR
    ExpiredSignatureError --> InvalidTokenError
    InvalidTokenError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: ExpiredSignatureError is a direct subclass of InvalidTokenError and inherits behavior/state from its base classes.)

## Raises:
- Instantiation/raising of this exception does not introduce additional library-specific exceptions.
- Normal creation/raising will not raise; only Python runtime errors (e.g., MemoryError) could interrupt instantiation in exceptional circumstances.

## Example:
- Raising when expiry is detected (example of conventional usage):
    # inside a token validation function (pseudocode)
    if expiry_check_failed:
        raise ExpiredSignatureError("token has expired")

- Raising while preserving underlying parse error:
    try:
        parse_exp(claims)
    except ValueError as exc:
        raise ExpiredSignatureError("invalid exp claim") from exc

- Catching the specific condition:
    try:
        decode_and_validate(token)
    except ExpiredSignatureError as exc:
        handle_expiry(exc)  # e.g., redirect to login or refresh token

## `jwt.exceptions.InvalidAudienceError` · *class*

## Summary:
A marker exception indicating that a JWT's audience claim (aud) did not match the expected audience(s). It is a specific subclass used to signal audience-validation failures during token processing.

## Description:
InvalidAudienceError exists to let JWT validation code communicate a precise failure reason when the token's audience claim is invalid or does not contain the expected audience value(s). It is a semantic specialization of InvalidTokenError and is intended to be raised by JWT decoding/validation routines when they detect an audience mismatch. Client code and calling libraries can catch InvalidAudienceError to handle audience-specific recovery (e.g., reject the token, log an audit event, attempt a different verification flow) while preserving broader handling via the InvalidTokenError or PyJWTError base types.

Typical instantiation sites:
- JWT decoding/validation functions that compare the token's "aud" claim against an expected audience value or set.
- Higher-level utilities that normalize lower-level errors into a specific "audience invalid" classification.
- Tests that simulate audience mismatch failures by raising this exception directly.

Motivation and responsibility:
- Provide a distinct, catchable type representing audience-claim validation failures so callers can implement targeted error handling and clearer logging.
- Do not carry payload, timing, or validation-context state beyond the usual exception message and Python exception chaining; those details should be included in the exception message or provided by the underlying exception via "raise ... from".

## State:
- This class defines no new instance attributes; it inherits all state from its ancestors (InvalidTokenError -> PyJWTError -> Exception).
- Inherited attributes available on instances:
  - args (tuple): positional arguments passed to the constructor (commonly a single message string describing the failure).
  - __cause__, __context__, __traceback__ as provided by Python's exception model.
- __init__ parameters:
  - Inherits Exception.__init__; callers may pass zero or more positional arguments. Typical usage: InvalidAudienceError("audience did not match expected value").
  - No additional parameters, defaults, or constraints are enforced by InvalidAudienceError itself.
- Class invariants:
  - Instances are marker exceptions with no additional mutable state introduced by this class.
  - The args tuple faithfully represents constructor arguments and is the primary carrier of human-readable context.

## Lifecycle:
- Creation:
  - Instantiate directly with zero or more positional arguments: e.g., InvalidAudienceError("aud claim mismatch").
  - Often created and raised at the point of validation failure: raise InvalidAudienceError("expected 'api://default', got 'other-aud'").
  - Can be raised from another exception to preserve context: raise InvalidAudienceError("audience validation failed") from exc
- Usage:
  - Immediately raised and caught; there are no lifecycle methods or state transitions.
  - Typical catching patterns:
    - Specific handling: except InvalidAudienceError as e:
    - Handle any invalid-token condition: except InvalidTokenError as e:
    - Handle any library-level error: except PyJWTError as e:
- Destruction / cleanup:
  - No cleanup required. Instances are ordinary exception objects managed by Python's exception and garbage-collection mechanisms. The class does not implement context-manager protocols or resource cleanup methods.

## Method Map:
graph LR
    InvalidAudienceError --> InvalidTokenError
    InvalidTokenError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: InvalidAudienceError is a direct subclass of InvalidTokenError and inherits behavior from the PyJWTError/Exception hierarchy.)

## Raises:
- Instantiating InvalidAudienceError (via Exception.__init__) does not introduce library-specific raises.
- Raising or creating the exception will normally not raise other exceptions unless Python's exception machinery is modified; typical creation and raising are safe operations.

## Example:
- Raising when an audience claim does not match expected values:
    raise InvalidAudienceError("expected audience 'my-audience', got 'other'")

- Raising while preserving underlying error context:
    try:
        validate_audience(claims, expected_audience)
    except SomeLowerLevelError as exc:
        raise InvalidAudienceError("audience validation failed") from exc

- Catching the specific audience problem:
    try:
        process_jwt(token)
    except InvalidAudienceError as e:
        handle_audience_mismatch(e)

- Broad token-error handling (includes audience errors):
    try:
        process_jwt(token)
    except InvalidTokenError as e:
        handle_invalid_token(e)

## `jwt.exceptions.InvalidIssuerError` · *class*

## Summary:
Represents an "invalid issuer" JWT error — a marker exception indicating a token's issuer (the "iss" claim) did not match the expected value. It is a specific subtype of InvalidTokenError intended for callers to raise or catch when issuer validation fails.

## Description:
Use this class when issuer-checking code determines that a JWT's issuer claim is incorrect, missing, or otherwise unacceptable for the current validation context. Typical callers include JWT validation routines, claim-check helpers, or higher-level authentication/authorization code that performs issuer verification.

Motivation:
- Provide a narrow, catchable exception type that clearly communicates an issuer-related token validation failure.
- Allow callers to handle issuer failures distinctly from other invalid-token cases by catching InvalidIssuerError, while still enabling broader handling via InvalidTokenError or PyJWTError.

Known caller patterns:
- Validation code: upon detecting issuer mismatch, raise InvalidIssuerError("issuer mismatch") or raise InvalidIssuerError("expected X, got Y") from underlying parsing exceptions.
- Catchers: specific handling using except InvalidIssuerError as e: or broader handling using except InvalidTokenError as e: or except PyJWTError as e:.

Responsibility boundary:
- This class does not perform any issuer validation itself; it only serves as the canonical exception type to signal the result of such validation.
- It does not attach structured metadata about the expected/current issuer beyond what is placed in the exception message or provided via exception chaining.

## State:
Attributes (inherited; this class defines no new attributes)
- args (tuple): positional arguments passed to the constructor (commonly a single message string). No internal parsing is performed by the class.
- __cause__, __context__, __traceback__: standard Python exception attributes available when raised/chained.

__init__ parameters:
- Inherits Exception.__init__; callers may pass zero or more positional arguments (typical: a single human-readable message).
- No additional keyword parameters, defaults, or validations are introduced by this subclass.

Class invariants:
- Instances are marker exceptions with no additional state beyond standard Exception fields.
- The args tuple exactly reflects constructor arguments and should be used to carry any human-readable context.

## Lifecycle:
Creation:
- Instantiate directly with optional message(s): e.g., InvalidIssuerError("issuer claim does not match expected value").
- Common pattern: raise InvalidIssuerError("message") or raise InvalidIssuerError("message") from exc to preserve underlying context.

Usage:
- Immediate raising and catching is the intended usage. There are no lifecycle methods or state transitions to call.
- Typical handling patterns:
  - Specific recovery or logging: except InvalidIssuerError as e: ...
  - General invalid-token processing: except InvalidTokenError as e: ...  (catches InvalidIssuerError)
  - Library-wide handling: except PyJWTError as e: ...

Destruction / cleanup:
- No explicit cleanup required. Instances are ordinary exceptions subject to Python GC. This class does not implement context manager protocols or resource finalizers.

## Method Map:
graph LR
    validate_issuer[Issuer validation logic] --> |on mismatch| InvalidIssuerError
    InvalidIssuerError --> InvalidTokenError
    InvalidTokenError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException
    InvalidIssuerError --> |caught by| CatchSpecific[except InvalidIssuerError]
    InvalidTokenError --> |caught by broader handler| CatchBroader[except InvalidTokenError or PyJWTError]

(Interpretation: issuer validation logic raises InvalidIssuerError on failure; the exception flows up the inheritance chain and can be caught either specifically or by broader JWT/library exception handlers.)

## Raises:
- __init__/instantiation: no library-specific exceptions are raised by the constructor itself (behavior inherited from Exception).
- Raising an instance (raise InvalidIssuerError(...)) does not introduce additional side effects beyond standard exception propagation. Any exceptions caused by modifying Python's exception machinery are out of scope.

## Example:
- Raise when issuer check fails:
    raise InvalidIssuerError("expected issuer 'auth.example.com', got 'other.example.com'")

- Raise while preserving an underlying error:
    try:
        payload = decode_token(raw_token)
    except SomeParsingError as exc:
        raise InvalidIssuerError("issuer validation failed during decode") from exc

- Catch the specific issuer error:
    try:
        validate_issuer_claim(payload, expected="auth.example.com")
    except InvalidIssuerError as e:
        handle_issuer_mismatch(e)

- Catch broader invalid-token errors (includes InvalidIssuerError):
    try:
        validate_token(token)
    except InvalidTokenError as e:
        handle_invalid_token(e)

## `jwt.exceptions.InvalidIssuedAtError` · *class*

## Summary:
A direct, semantic marker exception subclassing InvalidTokenError used to represent problems with a JWT "iat" (Issued At) claim. The class itself carries no additional state or behavior beyond its place in the exception hierarchy.

## Description:
InvalidIssuedAtError is a named, catchable exception intended to classify errors discovered while validating or parsing the JWT "iat" claim. It is a direct subclass of InvalidTokenError; both this class and its base class are marker exceptions (see InvalidTokenError documentation). InvalidIssuedAtError does not implement validation logic or store extra context — its value is purely in providing a specific type to raise and catch when iat-related problems occur.

Scenarios where it may be raised:
- A JWT validation routine detects the iat claim is missing, malformed, clearly incorrect (for example, a timestamp in the future when not allowed), or otherwise unacceptable, and raises this exception to indicate that specific category of failure.
- Application code or helper utilities deliberately raise this type to allow callers to distinguish iat-related failures from other token errors.

Responsibility boundary:
- Acts only as a typed marker for error classification; it relies on other code to perform detection/validation and to include any contextual details (e.g., message text or underlying exception chaining).

## State:
- Defines no new attributes; it inherits all state and behavior from InvalidTokenError (and transitively from PyJWTError and Python's Exception).
- Inherited attributes:
  - args (tuple): constructor positional arguments (commonly a single message string).
  - __cause__, __context__, __traceback__ (Python exception mechanics).
- __init__ parameters:
  - Inherits Exception.__init__; accept zero or more positional arguments. Typical usage is to pass a single human-readable message.
- Class invariants:
  - Instances remain simple marker exceptions with only standard Exception state; no extra attributes are introduced by this class.

## Lifecycle:
- Creation:
  - Instantiate directly with zero or more positional arguments, for example:
        InvalidIssuedAtError("iat claim missing")
  - Typical pattern is to raise at the point of detection:
        raise InvalidIssuedAtError("iat in the future")
  - Preserve original exception context when appropriate:
        raise InvalidIssuedAtError("iat parse error") from original_exc
- Usage:
  - No lifecycle or resource-management methods; instances are raised and caught.
  - Catching patterns:
      - Specific handling: except InvalidIssuedAtError as e:
      - Broader handling: except InvalidTokenError as e:  (will also catch InvalidIssuedAtError)
- Destruction / cleanup:
  - No cleanup responsibilities; handled by Python's exception and garbage collection mechanisms.

## Method Map:
graph LR
    InvalidIssuedAtError --> InvalidTokenError
    InvalidTokenError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: InvalidIssuedAtError is a direct subclass of InvalidTokenError and inherits marker semantics from its ancestors.)

## Raises:
- Constructing or raising InvalidIssuedAtError does not introduce library-specific exceptions; under normal Python semantics, instantiation and raising succeed without raising additional exceptions.
- The occurrence of this exception signifies an iat-related validation failure as determined by the code that raises it.

## Example:
- Raise on iat validation failure:
    raise InvalidIssuedAtError("iat claim missing")

- Raise while preserving parsing error context:
    try:
        iat = parse_iat(value)
    except ValueError as exc:
        raise InvalidIssuedAtError("invalid iat format") from exc

- Catching the specific iat error:
    try:
        validate_iat(payload)
    except InvalidIssuedAtError as e:
        handle_iat_issue(e)

- Catching all token errors (including iat-related):
    try:
        process_jwt(token)
    except InvalidTokenError as e:
        handle_token_failure(e)

## `jwt.exceptions.ImmatureSignatureError` · *class*

## Summary:
ImmatureSignatureError is a marker exception indicating a JWT validation failure specifically classified as an "immature signature" condition. It is a direct subclass of InvalidTokenError and carries no additional state or behavior.

## Description:
This class exists so callers and JWT-validation code can raise and catch a semantically specific error when a token's signature is considered "immature" (i.e., the token or its signature is being used before the allowed/valid time window). As a narrow subclass of InvalidTokenError, it enables code to distinguish this case from other invalid-token conditions while still allowing broader handling via the InvalidTokenError or PyJWTError base types.

Typical scenarios where an instance is created:
- A JWT validation routine detects that the token is being used before it becomes valid (for example, based on temporal claims) and wants to report that precise condition.
- A helper utility normalizes lower-level errors into well-known library exception types and maps a "used too early" condition to ImmatureSignatureError.
- Client code or middleware may raise this exception to indicate a token was presented prior to its valid-from time.

Known caller patterns:
- Raised directly when an immature-signature condition is detected:
    raise ImmatureSignatureError("token used before valid time")
- Raised while preserving underlying context:
    raise ImmatureSignatureError("immature signature") from original_exc
- Catching patterns:
    except ImmatureSignatureError as e:   # handle this specific condition
    except InvalidTokenError as e:       # handle all invalid-token conditions

Motivation and responsibility boundary:
- Purpose: provide a distinct, catchable type that represents the "immature signature" category of token validation failures.
- Boundary: does not encapsulate additional metadata (timestamps, token payload). Any such context must be provided via the exception message or via exception chaining (raising from an underlying exception).

## State:
- This class defines no new instance attributes; it inherits all state and behavior from InvalidTokenError (and ultimately from Python's Exception).
- Inherited attributes available on instances:
  - args (tuple): positional constructor arguments (typically a single message string).
  - __cause__, __context__, __traceback__: standard Python exception attributes for chaining and traceback.
- __init__ parameters:
  - Inherits Exception.__init__: callers may pass zero or more positional arguments (common usage is a single descriptive message).
  - No additional parameters, defaults, or constraints are imposed by this subclass.
- Class invariants:
  - Instances are simple marker exceptions; no extra attributes are added by ImmatureSignatureError.
  - The args tuple must reflect the constructor arguments and serve as the primary holder of human-readable context.

## Lifecycle:
- Creation:
  - Instantiate directly with zero or more positional arguments, e.g. ImmatureSignatureError("token used too early").
  - Typically created at the point of detection and raised immediately.
  - Can be raised with preserved context using exception chaining: raise ImmatureSignatureError("...") from exc
- Usage:
  - Common pattern is immediate raising and catching; there are no lifecycle methods to call on instances.
  - No required call order; once raised, it can be caught by handlers that specifically want to handle immature-signature errors or broader invalid-token errors.
- Destruction / cleanup:
  - No cleanup required. Instances are ordinary exception objects managed by Python's exception handling and garbage collection.
  - ImmatureSignatureError does not implement context-manager protocols or resource cleanup methods.

## Method Map:
graph LR
    ImmatureSignatureError --> InvalidTokenError
    InvalidTokenError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: ImmatureSignatureError is a direct subclass of InvalidTokenError and inherits behavior from the PyJWTError and Python Exception/BaseException hierarchy.)

## Raises:
- The class itself does not raise exceptions during normal instantiation beyond what Python's Exception machinery may raise in pathological environments.
- No library-specific exceptions are introduced by the constructor.

## Example:
- Raising the specific immature-signature condition:
    raise ImmatureSignatureError("signature used before 'nbf' / token not yet valid")

- Raising while preserving an underlying cause:
    try:
        verify_token_time_claims(payload)
    except SomeLowerLevelTimeError as exc:
        raise ImmatureSignatureError("token used too early") from exc

- Catching the specific condition:
    try:
        validate_jwt(token)
    except ImmatureSignatureError as e:
        handle_token_issued_too_early(e)

- Catching all invalid-token conditions (including immature-signature):
    try:
        process_jwt(token)
    except InvalidTokenError as e:
        handle_invalid_token(e)

## `jwt.exceptions.InvalidKeyError` · *class*

## Summary:
InvalidKeyError is a marker exception type indicating that a provided key or key material is invalid or unsuitable for use with PyJWT operations.

## Description:
This class exists as a distinct, specific error type so code can signal and handle errors related to invalid keys separately from other JWT errors. InvalidKeyError is an empty subclass of PyJWTError and adds no new behavior or state beyond being a more specific marker.

Typical scenarios where an instance should be created:
- When library code validating, parsing, or selecting a cryptographic key determines the supplied key is malformed, unsupported, missing required material, or otherwise unusable for the requested signing/verification operation.
- When higher-level operations want to raise a clearly-typed error for callers to catch when key-related validation fails.

Known callers / factories:
- Any code within the PyJWT library that performs key validation, key parsing, or selects a key for an operation may raise InvalidKeyError to indicate key-specific problems.
- Client code may raise InvalidKeyError when integrating with PyJWT to surface key validation failures in a consistent library-specific form.

Motivation and responsibility boundary:
- Provide a stable, narrowly-scoped exception type for key-related failures so callers can choose to handle invalid-key conditions distinctly from other JWT errors (catching except InvalidKeyError vs except PyJWTError).
- Responsibility is limited to signaling the error condition — it does not encapsulate key metadata, validation routines, or remediation instructions.

## State:
Attributes (inherited; InvalidKeyError defines no additional attributes):
- args (tuple): positional arguments passed to the constructor, typically contains an error message as the first element.
- __cause__ (optional): chained exception cause if raised via "raise ... from ...".
- __context__ (optional): context when another exception was active.
- __traceback__ (optional): populated when the exception is raised.

Constructor parameters and constraints:
- InvalidKeyError does not override Exception.__init__; it accepts the same parameters as built-in Exception:
  - Typical calls: InvalidKeyError(), InvalidKeyError("message"), InvalidKeyError(arg1, arg2)
- There are no additional validation rules or required parameters enforced by InvalidKeyError itself.

Class invariants:
- Instances are simple marker exceptions whose meaningful content (if any) is carried in args or by exception chaining.
- No persistent or mutable PyJWT-specific attributes are present on instances.

## Lifecycle:
Creation:
- Instantiate directly using the same call patterns as Exception:
  - InvalidKeyError() or InvalidKeyError("key is malformed") or provide multiple args if desired.
- Alternatively, raise directly at the point of detection (see Usage).

Usage:
- Raise to signal key-specific failures:
  - raise InvalidKeyError("unsupported key type")
- Catch to handle key-related issues explicitly:
  - except InvalidKeyError: handle key error
- It is common to raise InvalidKeyError from key-validation routines or to raise it from a lower-level exception to preserve cause:
  - raise InvalidKeyError("invalid key") from original_exc

Destruction / cleanup:
- No cleanup actions or context-manager protocol are implemented. Regular Python exception lifecycle and garbage collection apply.

## Method Map:
graph LR
    InvalidKeyError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: InvalidKeyError is a direct, empty subclass of PyJWTError and inherits all behavior from Exception/BaseException.)

## Raises:
- InvalidKeyError.__init__ does not raise library-specific exceptions. Any exceptions during instantiation would originate from the Python runtime (no custom validation or errors are introduced by this class).

## Example:
- Raise with a message:
    raise InvalidKeyError("Provided PEM is malformed")

- Raise while preserving an underlying error:
    try:
        parse_key(pem_bytes)
    except ValueError as e:
        raise InvalidKeyError("unable to parse key") from e

- Catch and handle:
    try:
        do_jwt_signing(key)
    except InvalidKeyError as e:
        log_error("Key invalid: " + str(e))
        # fallback, notify caller, or re-raise as appropriate

## `jwt.exceptions.InvalidAlgorithmError` · *class*

## Summary:
A lightweight marker exception class used to signal algorithm-related JWT errors; it is a direct subclass of InvalidTokenError and adds no state or behavior.

## Description:
InvalidAlgorithmError exists to provide a distinct exception type to represent problems related to the cryptographic algorithm of a JSON Web Token (JWT). From the source it is only a subclass of InvalidTokenError with no additional implementation; the class itself does not enforce or perform any algorithm checks.

Typical, conventional scenarios where code raises this exception:
- A JWT-processing routine detects that the token's declared algorithm is unsupported, disallowed, or mismatches the expected algorithm and chooses to raise a specifically-typed error.
- Policy or configuration code that enforces allowed algorithms may raise this type to classify the failure for callers.

Important distinction: these scenarios describe conventional usage by callers of the class. The class implementation imposes no semantics beyond being a distinct exception type; any algorithm checks and decision logic occur elsewhere in the codebase.

## State:
- This class declares no new instance attributes; it inherits all state from InvalidTokenError and ultimately from Python's Exception.
- Available inherited attributes:
  - args (tuple): positional constructor arguments (commonly a single message string).
  - __cause__, __context__, __traceback__: standard Python exception attributes.
- __init__ parameters:
  - Inherits Exception.__init__; callers may supply zero or more positional arguments (typical: a single message). No extra parameters or defaults are added.
- Class invariants:
  - Instances are marker exceptions: no additional attributes will be created by this class.
  - The args tuple must reflect the constructor arguments and is the canonical place to store a human-readable message.

## Lifecycle:
- Creation:
  - Instantiate directly: InvalidAlgorithmError() or with a message: InvalidAlgorithmError("algorithm not supported").
  - Can be raised directly at the point of detection: raise InvalidAlgorithmError("reason").
  - Can preserve underlying context: raise InvalidAlgorithmError("reason") from underlying_exc.
- Usage:
  - There are no lifecycle methods; usage is limited to raising and catching.
  - Typical catching patterns:
    - Specific handling: except InvalidAlgorithmError as e:
    - Broader handling: except InvalidTokenError as e: (will catch this subclass)
- Destruction / cleanup:
  - No cleanup responsibilities. Instances are standard exception objects managed by Python's runtime and garbage collector.

## Method Map:
graph LR
    InvalidAlgorithmError --> InvalidTokenError
    InvalidTokenError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: the diagram shows the inheritance chain; InvalidAlgorithmError adds no methods.)

## Raises:
- Instantiation and raising of this exception do not introduce library-specific raises. Normal object creation and raising follow Python's standard exception behavior and should not raise additional errors under ordinary conditions.

## Example:
- Basic raise:
    raise InvalidAlgorithmError("declared algorithm not supported")

- Raising while preserving underlying context:
    try:
        validate_token_algorithm(header)
    except SomeLowerLevelError as exc:
        raise InvalidAlgorithmError("algorithm validation failed") from exc

- Catching the specific algorithm error:
    try:
        process_jwt(token)
    except InvalidAlgorithmError as e:
        handle_algorithm_issue(e)

- Catching all token-related errors (including algorithm issues):
    try:
        process_jwt(token)
    except InvalidTokenError as e:
        handle_token_issue(e)

## `jwt.exceptions.MissingRequiredClaimError` · *class*

## Summary:
Represents an error raised when a JSON Web Token (JWT) is missing a required claim; it records the missing claim name and produces a human-readable message.

## Description:
This exception class is intended to be instantiated when JWT validation discovers that a required claim (for example, "exp", "iss", or "sub") is absent from the token payload. It encapsulates the name of the missing claim and provides a descriptive string representation for logging or error reporting.

Motivation and responsibility boundary:
- Provides a focused error type that identifies which specific claim was missing.
- Keeps the missing-claim detail (the claim name) as structured data (the `claim` attribute) so callers can programmatically inspect the error.
- Does not perform validation of the claim name; it simply stores and reports it.

Typical callers:
- JWT validation/verification code paths which check for presence of required claims and raise this error when one is absent.
- Error-handling or logging code that formats or records the message produced by this exception.

## State:
- claim (str)
    - Description: The name of the required claim that was found missing in the token.
    - Type: str (no runtime validation is performed by this class)
    - Valid values: Any object convertible to a string is accepted by the implementation; however callers should pass the claim name as a plain string.
    - Invariant: After initialization, the instance has a public attribute `claim` whose value equals the argument passed to __init__.

No other instance attributes or class-level state are introduced by this class.

## Lifecycle:
- Creation
    - Instantiate by passing the missing claim name as a single argument: MissingRequiredClaimError(claim)
    - The constructor requires one positional argument; there is no default.
- Usage
    - Common usage is to raise the instance to signal a validation failure:
        - A validator raises MissingRequiredClaimError("exp") when the "exp" claim is absent.
    - Consumers may catch this specific exception type and inspect its `claim` attribute to determine which claim triggered the error.
    - The __str__ method returns a concise human-readable message suitable for logs or error responses.
- Destruction
    - No special cleanup or context-manager behavior is provided or required.

## Method Map:
graph TD
    A[Create instance: __init__(claim)] --> B[Attribute set: self.claim = claim]
    B --> C[Read message: __str__()]
    C --> D[Return str: 'Token is missing the "X" claim']

(Note: the diagram shows the typical flow: construct -> attribute stored -> __str__ called to obtain the message.)

## Methods and behavior details:
- __init__(claim: str) -> None
    - Purpose: Initialize the exception and record the missing claim name.
    - Parameters:
        - claim (str): The name of the required claim that was missing. This parameter is required; there is no default.
    - Effects:
        - Sets the public instance attribute `claim` to the provided value.
    - Validation and constraints:
        - The implementation does not validate or coerce the value; it stores whatever value is passed. Callers should provide a meaningful string.
    - Returns: None
    - Side effects: None beyond assigning to self.claim
- __str__() -> str
    - Purpose: Produce a human-readable error message describing the missing claim.
    - Behavior:
        - Returns the string: Token is missing the "<claim>" claim where <claim> is the value of the instance's `claim` attribute.
    - Example return: 'Token is missing the "exp" claim'
    - Determinism: Always returns a string derived directly from the `claim` attribute.

## Raises:
- __init__: The constructor does not explicitly raise any exceptions. Passing unusual values (e.g., objects with side-effecting __format__ or __str__) could cause exceptions when those objects are formatted later, but this class itself performs no validation or raises no errors.

## Example:
# Instantiate to represent a missing "exp" claim
err = MissingRequiredClaimError("exp")
# Inspect the missing claim programmatically
missing = err.claim  # "exp"
# Convert to human-readable text for logging
message = str(err)  # 'Token is missing the "exp" claim'
# Typical usage in a validator:
# if "exp" not in payload:
#     raise MissingRequiredClaimError("exp")

### `jwt.exceptions.MissingRequiredClaimError.__init__` · *method*

## Summary:
Initializes the exception instance by storing the name of the missing JWT claim on the object.

## Description:
This constructor is called when an instance of the MissingRequiredClaimError exception is created. Typical usage is during JWT validation/error-handling code paths when a required claim is not present in a token; the validator constructs this exception and supplies the missing claim name so the error object carries that context.

No specific internal callers are declared in this small component; instantiation is expected wherever the authentication/validation pipeline detects a missing required claim. The logic is kept in its own initializer to create a lightweight, self-contained exception object whose instances always carry the claim name as an attribute (rather than inlining attribute assignment at various call sites).

## Args:
    claim (str): The name of the required JWT claim that was missing.
        - Type: annotated as str (no runtime type enforcement performed by this method).
        - Allowed values: any object may be passed at runtime, but callers should pass a string identifying the claim (e.g., "exp", "sub", "aud").
        - Default: no default; the parameter is required.

## Returns:
    None

## Raises:
    None — this initializer performs a direct assignment and does not raise any exceptions itself. (If callers pass values that later cause attribute access errors elsewhere, those will originate outside this method.)

## State Changes:
    Attributes READ:
        - None

    Attributes WRITTEN:
        - self.claim: assigned to the value of the claim argument

## Constraints:
    Preconditions:
        - Callers should provide a value intended to be the claim name (typically a str). The method does not validate or coerce the value.
        - The instance (self) must be a freshly constructed object of the exception class (normal object construction ensures this).

    Postconditions:
        - After the call, the instance has an attribute claim whose value equals the provided argument.
        - No other attributes or external state are modified.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside self performed by this method.

### `jwt.exceptions.MissingRequiredClaimError.__str__` · *method*

## Summary:
Return a concise, human-readable error message that embeds the missing claim name into a fixed sentence.

## Description:
This method provides the string representation for a MissingRequiredClaimError. It is invoked whenever the exception instance is converted to text (for example via str(exc), when included in log messages, or when serializing an exception message into an HTTP response). Typical call sites are exception handlers and token-validation code that catch this exception and surface its message to operators or API clients.

Having this formatting logic in __str__ centralizes the message format so all string conversions of the exception produce a consistent message without duplicating formatting in multiple catch blocks.

## Args:
    None. The missing claim value is read from the instance attribute self.claim, which is set by the exception's initializer (claim: str).

## Returns:
    str: The exact message returned is:
        Token is missing the "<claim>" claim
    where <claim> is formatted using Python's standard object formatting for the value stored in self.claim (the f-string uses value.__format__('') under the hood). Examples:
    - If self.claim == "exp", returns: Token is missing the "exp" claim
    - If self.claim == "", returns: Token is missing the "" claim
    - If self.claim contains double quotes, those characters appear verbatim inside the returned string (no escaping performed by this method).

## Raises:
    - AttributeError: If the instance does not have a claim attribute, accessing self.claim will raise AttributeError and that will propagate.
    - Any exception raised by formatting the claim (for example if self.claim.__format__('') raises); such exceptions propagate from this method.

## State Changes:
    Attributes READ:
        - self.claim
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The exception instance should have an attribute claim (normally set by __init__ as a str).
        - The value stored in self.claim should be safe to format; the method relies on Python's object formatting protocol for representation.
    Postconditions:
        - The method does not modify the exception instance.
        - The returned string always follows the fixed template with the claim's formatted representation inserted between double quotes.

## Side Effects:
    - None. The method performs no I/O, does not call external services, and does not mutate objects outside the instance.

## `jwt.exceptions.PyJWKError` · *class*

block, keeping claims strictly supported by the source and the known PyJWTError base-class summary; include required sections.

Action: WRITE
<DOCUMENTATION>
## Summary:
A semantic marker exception class for JSON Web Key (JWK) related errors in the PyJWT library. It is an empty subclass of PyJWTError used to distinguish JWK-specific failures by type.

## Description:
PyJWKError is defined solely as a subclass of PyJWTError with no additional behavior or state. The source code contains only an empty subclass declaration, so all behavior is inherited from PyJWTError -> Exception -> BaseException.

Intended usage (inference from name and placement)
- The class name and its presence in the exceptions module indicate it is intended to be raised to signal problems specifically related to JWK handling. This intention is semantic: the class itself enforces no additional behavior or validation.

Responsibility boundary
- Serve as an identity/typing distinction within the exception hierarchy for JWK-related error conditions. It does not add attributes, methods, validation, or resource-management responsibilities.

## State:
Attributes defined on this class
- None. PyJWKError introduces no new instance attributes.

Inherited attributes available on instances
- args (tuple): positional arguments passed to the constructor (commonly contains the error message).
- __cause__, __context__, __traceback__: standard Python exception attributes for chaining and diagnostics.

Constructor parameters and constraints
- Inherits Exception.__init__ without override. Valid constructions include:
  - PyJWKError()
  - PyJWKError("message")
  - PyJWKError(arg1, arg2, ...)
- No class-level validation or constraints are enforced by PyJWKError.

Class invariants
- Instances are ordinary Exception objects whose type signals a JWK-related error. No invariants beyond those of Exception apply.

## Lifecycle:
Creation
- Instantiate directly using the same arguments as Exception:
  - e = PyJWKError()
  - e = PyJWKError("invalid JWK")

Usage
- Raising:
  - raise PyJWKError("explanation")
  - Optional chaining: raise PyJWKError("explanation") from original_exc
- Catching:
  - To handle JWK-specific errors: except PyJWKError:
  - To handle all PyJWT library errors: except PyJWTError:

Destruction / cleanup
- No cleanup responsibilities, no context-manager protocol. Standard Python exception lifecycle and garbage collection apply.

## Method Map:
graph LR
    PyJWKError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: PyJWKError is a direct subclass of PyJWTError and inherits behavior from Exception/BaseException.)

## Raises:
- The class definition does not introduce any new exceptions. Instantiation follows Exception semantics; no library-specific exceptions are raised by PyJWKError itself.

## Example:
- Raising a JWK error:
    raise PyJWKError("JWK is missing required 'kty' field")

- Chaining from a lower-level error:
    try:
        parse_jwk(raw)
    except ValueError as exc:
        raise PyJWKError("failed to parse JWK") from exc

- Catching JWK-specific errors:
    try:
        load_key_from_jwk(jwk)
    except PyJWKError as e:
        handle_jwk_error(e)

Notes:
- This documentation describes only what the source code defines (an empty subclass). Any broader conventions about when to raise this exception are inferred from its name and intended role within the library.

## `jwt.exceptions.PyJWKSetError` · *class*

## Summary:
A lightweight marker exception type indicating an error related to JSON Web Key (JWK) Sets within the PyJWT domain. It exists solely to provide a distinct, catchable type for JWK Set–focused error conditions.

## Description:
PyJWKSetError is an empty subclass of PyJWTError and does not add behavior or state beyond what Exception provides. Its purpose is semantic: to allow code that deals with JWK Sets to raise or catch an exception specifically representing JWK Set problems while still being categorizable as a PyJWTError for broader handling.

Intended usage (guidance, not an enforced behavior):
- Raise PyJWKSetError when a JWK Set–related problem occurs in your code (for example, when JWK Set processing, lookup, or validation fails).
- Catch PyJWKSetError when you want to handle JWK Set errors distinctly from other JWT-related errors.
- Catch PyJWTError to handle all PyJWT-related exceptions, including PyJWKSetError.

## State:
- New attributes: None. PyJWKSetError defines no instance attributes of its own.
- Inherited attributes (standard Exception/BaseException attributes):
  - args (tuple): constructor positional arguments (commonly a single message string).
  - __cause__, __context__, __traceback__: standard exception context and traceback attributes managed by the Python runtime.
- Constructor signature and constraints:
  - Inherits Exception.__init__; valid constructions include:
    - PyJWKSetError()
    - PyJWKSetError("message")
    - PyJWKSetError(arg1, arg2, ...)
  - No additional validation or constraints are enforced by PyJWKSetError.

Class invariant:
- Instances remain simple marker exceptions; the only information they carry (beyond their type) is the content of args.

## Lifecycle:
Creation:
- Instantiate directly with zero or more constructor arguments:
    e = PyJWKSetError()
    e = PyJWKSetError("no matching key found")
- Typically created at the point where JWK Set–specific errors are detected and raised.

Usage:
- Raise to signal an error:
    raise PyJWKSetError("descriptive message")
- Catch specifically:
    try:
        ...
    except PyJWKSetError as e:
        handle_jwkset_error(e)
- Or catch generally via the base:
    except PyJWTError as e:
        handle_any_pyjwt_error(e)

Destruction / cleanup:
- No cleanup or resource-management responsibilities. Standard exception lifecycle and garbage collection apply.

## Method Map:
graph LR
    PyJWKSetError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: PyJWKSetError is a direct subclass of PyJWTError and inherits methods/attributes from Exception/BaseException.)

## Raises:
- The PyJWKSetError class definition itself does not raise exceptions during import or instantiation beyond what the Python runtime might raise for improper usage of Exception (which is not applicable in normal usage).
- Library code or user code may raise PyJWKSetError to indicate JWK Set–related failure conditions.

## Example:
- Raising the exception:
    raise PyJWKSetError("JWK Set does not contain a usable key")

- Catching JWK Set errors specifically:
    try:
        process_jwk_set(jwk_set)
    except PyJWKSetError as e:
        log("JWK Set error: " + str(e))

- Broadly catching all PyJWT errors (includes PyJWKSetError):
    try:
        perform_jwt_operation()
    except PyJWTError as e:
        handle_generic_pyjwt_error(e)

- Subclassing for a more specific JWK Set error (if desired):
    class MyJWKSetValidationError(PyJWKSetError):
        pass

## `jwt.exceptions.PyJWKClientError` · *class*

## Summary:
A marker exception type indicating errors specific to JWK-client-related operations within the PyJWT library. It is a narrow subclass of PyJWTError used to distinguish JWK client failures from other PyJWT errors.

## Description:
PyJWKClientError exists solely to provide a distinct, catchable exception type for problems that arise in JWK client code paths (for example: fetching, parsing, validating, or resolving JSON Web Keys). It does not add behavior or state beyond its parent type and is intended to be raised by JWK client components or re-raised by higher-level code when they want to signal JWK-specific failure semantics.

Motivation and responsibility boundary:
- Allow callers to catch "all PyJWT errors" (except by catching the PyJWTError base) or to handle JWK-specific failures separately by catching PyJWKClientError.
- Serve as a stable, library-scoped marker so documentation and client code can refer to a dedicated exception class for JWK client issues without exposing implementation details.

Known / typical callers:
- Code paths that implement JWK fetching, caching, parsing, resolution, or validation.
- Higher-level routines that call those JWK-related helpers and need to re-raise or wrap JWK client failures.

## State:
- This class defines no new attributes. All instance state and behavior are inherited from its base classes.
- Inherited attributes available on instances (via PyJWTError -> Exception):
  - args (tuple): positional arguments passed to the exception constructor; commonly contains the error message.
  - __cause__, __context__, __traceback__: standard Python exception attributes used for chaining and debugging.

Constructor parameters and constraints:
- PyJWKClientError does not override __init__; it accepts the same arguments as Exception (and as PyJWTError):
  - Typical usage: PyJWKClientError() or PyJWKClientError("message") or PyJWKClientError(arg1, arg2, ...)
- No additional validation or constraints are enforced by this class.

Class invariants:
- Instances are simple marker exceptions: no custom attributes are added and the args tuple fully represents constructor-provided context.
- The inheritance chain remains intact: PyJWKClientError is always a subclass of PyJWTError and therefore of Exception.

## Lifecycle:
Creation:
- Instantiate directly with any arguments accepted by Exception:
  - Example forms: PyJWKClientError(), PyJWKClientError("failed to fetch JWK"), PyJWKClientError("msg", details)
- Alternatively, components may raise it directly: raise PyJWKClientError("reason")

Usage:
- Raising: used to indicate JWK-client-specific failure conditions.
- Catching: callers who want to handle only JWK client errors can use except PyJWKClientError:; callers who want to handle all library errors can use except PyJWTError:.
- Sequencing: there are no instance methods — usage is limited to standard exception raising/catching and optional chaining (raise ... from ...).

Destruction:
- No cleanup or resource management is associated with this exception type. Normal Python exception lifecycle and garbage collection apply.

## Method Map:
graph LR
    PyJWKClientError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: inheritance only; no additional methods or call dependencies.)

## Raises:
- PyJWKClientError.__init__ (inherited from Exception) does not raise library-specific exceptions. Any exceptions during instantiation would originate from the Python runtime (e.g., unusual customizations of Exception), not from this class.

## Example:
- Creating and raising:
    raise PyJWKClientError("unable to fetch JWK set: network error")

- Catching JWK-specific errors separately from other PyJWT errors:
    try:
        fetch_and_resolve_jwk(key_id)
    except PyJWKClientError as e:
        # handle errors specific to JWK fetching or resolution
        log_jwk_error(str(e))
    except PyJWTError as e:
        # handle other PyJWT-related errors
        log_general_jwt_error(str(e))

Notes:
- Because this class adds no extra fields, prefer passing contextual information through the exception message or by chaining (raise PyJWKClientError("msg") from original_exc).

## `jwt.exceptions.PyJWKClientConnectionError` · *class*

## Summary:
A marker exception indicating a connection-related failure occurred while a JWK (JSON Web Key) client was attempting network operations (for example, fetching a JWK set). It specializes PyJWKClientError to allow callers to catch connection-specific JWK client failures separately from other JWK/client errors.

## Description:
PyJWKClientConnectionError is raised to signal problems that are specifically about connectivity or transport when a JWK client performs network operations (DNS failures, timeouts, refused connections, HTTP connection errors, etc.). It exists purely to provide a fine-grained, catchable type for connection-related JWK failures while inheriting all behavior from PyJWKClientError and upstream PyJWTError/Exception.

Typical callers / creation sites:
- JWK-fetching components which perform HTTP(S) requests to obtain JWK sets and detect network/transport errors.
- Higher-level code that wants to re-raise or wrap lower-level network exceptions as a JWK-client connection problem.
- Any code path that needs to distinguish connection failures from other JWK-related errors (parsing, validation, lookup).

Motivation / responsibility boundary:
- Provide a dedicated exception type so client code can:
  - Retry or apply backoff on connection failures.
  - Surface a different error message or remediation advice when the failure is network-related.
- It does not implement additional logic, attributes, or methods — it is a semantic marker only.

## State:
- New attributes: none. This class does not add attributes beyond what is provided by Python's Exception and its ancestor PyJWKClientError.
- Inherited attributes available on instances:
  - args (tuple): constructor positional arguments, typically a human-readable message and optionally other context tuples.
  - __cause__, __context__, __traceback__: standard Python exception chaining and debugging attributes.
- __init__ parameters:
  - No custom __init__. Accepts the same arguments as Exception:
    - Typical forms: PyJWKClientConnectionError(), PyJWKClientConnectionError("message"), PyJWKClientConnectionError("msg", details)
  - No validation or transformation is performed on provided arguments.
- Class invariants:
  - Instances are passive marker exceptions: no mutable internal state is introduced.
  - The inheritance chain remains intact: PyJWKClientConnectionError is a subclass of PyJWKClientError, PyJWTError, Exception, etc.

## Lifecycle:
- Creation:
  - Instantiate directly with any Exception-compatible arguments:
    - PyJWKClientConnectionError("connection timed out")
    - raise PyJWKClientConnectionError("failed to connect to JWK endpoint")
  - Common pattern: wrap an underlying network exception using exception chaining:
    - raise PyJWKClientConnectionError("failed to fetch JWK set") from underlying_exc
- Usage:
  - Raising: used by JWK client code when detecting connection-related failures.
  - Catching: callers can catch this type specifically to implement retry/backoff logic:
    - except PyJWKClientConnectionError: handle connection problem
    - except PyJWKClientError: catch all JWK-client-related errors (including connection issues)
  - No ordering or method-call sequencing is required; this type is used only in raise/catch flows.
- Destruction / cleanup:
  - No explicit cleanup responsibilities. Normal Python exception lifecycle and garbage collection apply.

## Method Map:
graph LR
    PyJWKClientConnectionError --> PyJWKClientError
    PyJWKClientError --> PyJWTError
    PyJWTError --> Exception
    Exception --> BaseException

(Interpretation: inheritance only — no instance methods or additional call dependencies.)

## Raises:
- The class itself does not raise exceptions during normal instantiation.
- Any exceptions during constructing an Exception instance would originate from the Python runtime, not from this class.
- When re-raising from an underlying exception, be aware that the original exception remains available via __cause__ or __context__.

## Example:
- Raising with a message:
    raise PyJWKClientConnectionError("failed to connect to JWK endpoint: timeout")

- Raising while preserving the original network exception for debugging:
    try:
        resp = http_get(jwks_url)
    except NetworkTimeoutError as net_err:
        raise PyJWKClientConnectionError("timeout fetching JWK set") from net_err

- Catching connection-specific JWK errors separately:
    try:
        resolve_jwk(kid)
    except PyJWKClientConnectionError as conn_err:
        # handle network/connectivity issues (retry, alert, fallback)
        schedule_retry()
    except PyJWKClientError as jwk_err:
        # handle other JWK client errors (parsing, lookup failure)
        report_jwk_error(str(jwk_err))

