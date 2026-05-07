# `exceptions.py`

## `jwt.exceptions.PyJWTError` · *class*

## Summary:
Base exception class for PyJWT library exceptions.

## Description:
PyJWTError serves as the root exception class for all custom exceptions raised by the PyJWT library. It provides a common base type that allows applications to catch all JWT-related exceptions using a single except clause. Other more specific JWT exceptions should inherit from this class to maintain a coherent exception hierarchy.

## State:
- No instance attributes or state variables
- Inherits all characteristics from Python's built-in Exception class
- Acts as a marker class for the JWT exception namespace

## Lifecycle:
- Creation: Instantiated like any other Exception subclass (direct instantiation or via inheritance)
- Usage: Used in try/except blocks to handle JWT-related errors
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[PyJWTError] --> B[Exception]
    B --> C[BaseException]
    C --> D[object]
```

## Raises:
- Can be raised directly when JWT operations fail
- Typically raised by other JWT-specific exceptions that inherit from it

## Example:
```python
try:
    # Some JWT operation
    token = jwt.decode(encoded_token, key, algorithms=['HS256'])
except jwt.PyJWTError:
    # Handle any JWT-related error
    print("JWT operation failed")
```

## `jwt.exceptions.InvalidTokenError` · *class*

## Summary:
Represents an error that occurs when a JWT token is invalid or cannot be processed due to validation failures.

## Description:
InvalidTokenError is a specialized exception that indicates a JWT token is malformed, expired, or otherwise invalid according to the JWT specification or application requirements. This exception is raised when JWT decoding or validation operations detect issues with the token structure or security properties. It inherits from PyJWTError, making it part of the unified JWT exception hierarchy that allows applications to catch all JWT-related errors with a single exception handler.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the PyJWTError inheritance chain

## Lifecycle:
- Creation: Instantiated when JWT validation fails (typically by the jwt.decode() function or similar validation methods)
- Usage: Caught by applications using try/except blocks to handle JWT validation failures
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[InvalidTokenError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[BaseException]
    D --> E[object]
```

## Raises:
- Raised by JWT decoding/validation functions when token validation fails
- Triggered when tokens are malformed, expired, have incorrect signatures, or violate security policies

## Example:
```python
import jwt

try:
    payload = jwt.decode('invalid.token.here', 'secret', algorithms=['HS256'])
except jwt.InvalidTokenError:
    print("Token is invalid or malformed")
```

## `jwt.exceptions.DecodeError` · *class*

## Summary:
Represents an error that occurs when a JWT token cannot be decoded due to format or structural issues.

## Description:
DecodeError is a specialized exception that indicates a JWT token failed during the decoding process due to structural problems or format violations. This exception is raised when the JWT library encounters a token that cannot be parsed or decoded properly, such as when the token is malformed, has incorrect encoding, or violates the JWT specification in ways that prevent successful decoding. It inherits from InvalidTokenError, making it part of the unified JWT exception hierarchy.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the InvalidTokenError inheritance chain

## Lifecycle:
- Creation: Instantiated automatically by JWT decoding functions when token parsing fails
- Usage: Caught by applications using try/except blocks to handle JWT decoding failures specifically
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[DecodeError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWT decoding/validation functions when token decoding fails due to structural or format issues
- Triggered when tokens are malformed, improperly encoded, or violate JWT specification requirements

## Example:
```python
import jwt

try:
    payload = jwt.decode('invalid.token.here', 'secret', algorithms=['HS256'])
except jwt.DecodeError:
    print("Token could not be decoded due to formatting issues")
except jwt.InvalidTokenError:
    print("Token is invalid for other reasons")
```

## `jwt.exceptions.InvalidSignatureError` · *class*

## Summary:
Represents an error that occurs when a JWT token's signature is invalid or cannot be verified.

## Description:
InvalidSignatureError is a specialized exception that indicates a JWT token failed signature verification during the decoding process. This exception is raised when the JWT library detects that the token's signature does not match the expected value, typically because the token was tampered with, the signing key is incorrect, or the token was signed with a different algorithm than expected. It inherits from DecodeError, making it part of the JWT decoding exception hierarchy.

This exception allows applications to distinguish signature verification failures from other decoding issues like malformed tokens or incorrect encoding. It provides specific error handling for security-related concerns in JWT authentication flows.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the DecodeError inheritance chain

## Lifecycle:
- Creation: Instantiated automatically by JWT decoding functions when signature verification fails
- Usage: Caught by applications using try/except blocks to handle JWT signature verification failures specifically
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[InvalidSignatureError] --> B[DecodeError]
    B --> C[InvalidTokenError]
    C --> D[PyJWTError]
    D --> E[Exception]
    E --> F[BaseException]
    F --> G[object]
```

## Raises:
- Raised by JWT decoding/validation functions when token signature verification fails
- Triggered when the token's signature doesn't match the expected value during verification

## Example:
```python
import jwt

try:
    payload = jwt.decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'wrong_secret', algorithms=['HS256'])
except jwt.InvalidSignatureError:
    print("Token signature is invalid - possible tampering or wrong secret")
except jwt.DecodeError:
    print("Token could not be decoded due to formatting issues")
```

## `jwt.exceptions.ExpiredSignatureError` · *class*

## Summary:
Represents an error that occurs when a JWT token has expired and cannot be processed.

## Description:
ExpiredSignatureError is a specialized exception that indicates a JWT token has exceeded its validity period and is no longer considered valid for authentication or authorization purposes. This exception is raised during JWT decoding operations when the token's expiration timestamp (exp claim) has passed the current time. It inherits from InvalidTokenError, making it part of the unified JWT exception hierarchy that allows applications to catch all JWT-related errors with a single exception handler.

This specific exception type enables applications to distinguish between different kinds of token validation failures, particularly when dealing with time-sensitive tokens. Applications can catch ExpiredSignatureError specifically to implement appropriate handling such as prompting users for re-authentication or refreshing tokens.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the InvalidTokenError inheritance chain

## Lifecycle:
- Creation: Instantiated automatically by JWT decoding/validation functions when a token's expiration timestamp has passed
- Usage: Caught by applications using try/except blocks to handle expired token scenarios specifically
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[ExpiredSignatureError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWT decoding/validation functions when token validation detects expiration
- Triggered when the 'exp' claim in a JWT token contains a timestamp that precedes the current time

## Example:
```python
import jwt

try:
    payload = jwt.decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'secret', algorithms=['HS256'])
except jwt.ExpiredSignatureError:
    print("Token has expired and is no longer valid")
except jwt.InvalidTokenError:
    print("Token is invalid for other reasons")
```

## `jwt.exceptions.InvalidAudienceError` · *class*

## Summary:
Represents an error that occurs when a JWT token contains an invalid audience claim during validation.

## Description:
InvalidAudienceError is a specialized exception that indicates a JWT token's audience (aud) claim does not match the expected value during token validation. This exception is raised when the JWT decoder encounters a token where the audience claim either doesn't match the allowed audiences or is missing when required. It inherits from InvalidTokenError, making it part of the unified JWT exception hierarchy that allows applications to catch all JWT-related validation errors with targeted exception handling.

This exception specifically addresses audience validation failures, which is a common security requirement in JWT implementations where tokens must be validated against specific intended recipients.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the InvalidTokenError inheritance chain

## Lifecycle:
- Creation: Instantiated automatically by JWT validation functions when audience validation fails (typically by the jwt.decode() function when audience parameter is provided)
- Usage: Caught by applications using try/except blocks to handle JWT audience validation failures
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[InvalidAudienceError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWT decoding/validation functions when audience validation fails
- Triggered when tokens have an audience claim that doesn't match expected values
- Typically raised when validating tokens with audience restrictions using the audience parameter in jwt.decode()

## Example:
```python
import jwt

try:
    payload = jwt.decode(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJleGFtcGxlLmNvbSJ9.sflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        'secret',
        algorithms=['HS256'],
        audience='expected-audience'
    )
except jwt.InvalidAudienceError:
    print("Token audience is invalid or missing")
```

## `jwt.exceptions.InvalidIssuerError` · *class*

## Summary:
Represents an error that occurs when a JWT token's issuer (iss claim) does not match the expected value during validation.

## Description:
InvalidIssuerError is a specialized exception that indicates a JWT token was issued by an unauthorized or unexpected issuer. This exception is raised during JWT validation when the issuer claim (iss) in the token does not match the issuer(s) that were expected by the validating application. It inherits from InvalidTokenError, making it part of the unified JWT exception hierarchy that allows applications to catch all JWT-related validation errors with a single exception handler.

This exception is typically raised by JWT validation functions when the 'issuer' parameter is provided to the decode function and the token's iss claim doesn't match any of the allowed issuers.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the InvalidTokenError inheritance chain

## Lifecycle:
- Creation: Instantiated when JWT validation detects an issuer mismatch (typically by jwt.decode() when issuer validation is enabled)
- Usage: Caught by applications using try/except blocks to handle JWT issuer validation failures
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[InvalidIssuerError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWT decoding/validation functions when issuer validation fails
- Triggered when tokens contain an issuer claim that doesn't match the expected issuer(s) provided during validation

## Example:
```python
import jwt

try:
    payload = jwt.decode(
        'token.with.wrong.issuer', 
        'secret', 
        algorithms=['HS256'],
        issuer='expected-issuer'
    )
except jwt.InvalidIssuerError:
    print("Token issuer is invalid or unauthorized")
```

## `jwt.exceptions.InvalidIssuedAtError` · *class*

## Summary:
Represents an error that occurs when a JWT token's issued-at (iat) claim is invalid or cannot be processed during validation.

## Description:
InvalidIssuedAtError is a specialized exception that indicates a JWT token contains an invalid issued-at timestamp. This exception is raised when JWT validation detects that the token's iat (issued at) claim either:
- Is set to a future timestamp (token issued after current time)
- Cannot be parsed or interpreted as a valid timestamp
- Violates application-specific validation rules for issued timestamps

This exception extends InvalidTokenError, making it part of the unified JWT exception hierarchy that allows applications to catch all JWT-related errors with a single exception handler. It specifically addresses time-based validation failures related to token issuance timing.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the InvalidTokenError inheritance chain

## Lifecycle:
- Creation: Instantiated when JWT validation encounters an invalid issued-at claim (typically by the jwt.decode() function or similar validation methods when checking time-based claims)
- Usage: Caught by applications using try/except blocks to handle JWT validation failures specifically related to issued-at timestamps
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[InvalidIssuedAtError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWT decoding/validation functions when the token's iat (issued-at) claim fails validation
- Triggered when the issued-at timestamp is in the future or cannot be parsed as a valid timestamp

## Example:
```python
import jwt
from jwt.exceptions import InvalidIssuedAtError

try:
    payload = jwt.decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE5MDAwMDAwMDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 
                        'secret', algorithms=['HS256'])
except InvalidIssuedAtError:
    print("Token was issued in the future or has invalid issued-at timestamp")
```

## `jwt.exceptions.ImmatureSignatureError` · *class*

## Summary:
Represents an error that occurs when a JWT token's signature is not yet valid due to a future 'nbf' (not before) claim.

## Description:
ImmatureSignatureError is a specialized exception that indicates a JWT token's signature is not yet valid according to its 'nbf' (not before) claim. This exception is raised during JWT decoding operations when the token's validity period has not yet begun. It inherits from InvalidTokenError, making it part of the unified JWT exception hierarchy that allows applications to catch all JWT-related errors with a single exception handler.

This specific exception type enables applications to distinguish between different kinds of token validation failures, particularly when dealing with time-sensitive tokens that have future validity periods. Applications can catch ImmatureSignatureError specifically to implement appropriate handling such as retrying the operation later or informing users that the token is not yet active.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the InvalidTokenError inheritance chain

## Lifecycle:
- Creation: Instantiated automatically by JWT decoding/validation functions when a token's 'nbf' claim contains a timestamp that exceeds the current time
- Usage: Caught by applications using try/except blocks to handle immature token scenarios specifically
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[ImmatureSignatureError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWT decoding/validation functions when token validation detects that the token is not yet valid
- Triggered when the 'nbf' (not before) claim in a JWT token contains a timestamp that exceeds the current time

## Example:
```python
import jwt

try:
    payload = jwt.decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJubmYiOjE5MDA0NDQ4MDAsImV4cCI6MjAwMDQ0NDgwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'secret', algorithms=['HS256'])
except jwt.ImmatureSignatureError:
    print("Token signature is not yet valid - check the 'nbf' claim")
except jwt.InvalidTokenError:
    print("Token is invalid for other reasons")
```

## `jwt.exceptions.InvalidKeyError` · *class*

## Summary:
Exception raised when an invalid key is provided during JWT operations.

## Description:
InvalidKeyError is a specialized exception that indicates a key provided for JWT encoding or decoding operations is invalid. This exception inherits from PyJWTError and follows the standard PyJWT exception hierarchy. It is typically raised when the key format, type, or content does not meet the requirements for the specified JWT algorithm.

## State:
- No instance attributes or state variables
- Minimal subclass with no additional implementation beyond inheritance
- Acts as a marker exception for invalid key scenarios in JWT operations

## Lifecycle:
- Creation: Instantiated when JWT operations detect an invalid key (typically during encode/decode operations)
- Usage: Caught by try/except blocks that handle JWT-related errors
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[InvalidKeyError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[BaseException]
    D --> E[object]
```

## Raises:
- Raised during JWT encode/decode operations when key validation fails
- Triggered when the provided key doesn't meet algorithm-specific requirements

## Example:
```python
import jwt

try:
    # Attempt to decode a token with an invalid key
    payload = jwt.decode(token, invalid_key, algorithms=['HS256'])
except jwt.InvalidKeyError:
    print("The provided key is invalid for JWT operations")
```

## `jwt.exceptions.InvalidAlgorithmError` · *class*

## Summary:
Represents an error that occurs when a JWT token specifies an unsupported or invalid cryptographic algorithm.

## Description:
InvalidAlgorithmError is raised when a JWT token contains an algorithm identifier that is not supported or recognized by the PyJWT library. This exception typically occurs during JWT decoding when the token's header specifies an algorithm that is either not in the allowed algorithms list or is not implemented by the library. It inherits from InvalidTokenError, making it part of the JWT validation error hierarchy.

This exception helps distinguish algorithm validation failures from other token validation issues such as malformed tokens, expired tokens, or signature verification failures.

## State:
- No instance attributes or state variables
- Inherits all standard Exception properties (args, message, etc.)
- Part of the InvalidTokenError inheritance chain

## Lifecycle:
- Creation: Instantiated when JWT decoding/validation detects an unsupported algorithm (typically by jwt.decode() or similar validation functions)
- Usage: Caught by applications using try/except blocks to handle algorithm-specific validation failures
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[InvalidAlgorithmError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWT decoding/validation functions when the token's algorithm is not in the allowed algorithms list
- Triggered when the algorithm specified in the JWT header is not supported by the PyJWT library
- Typically occurs when algorithms like 'none', 'RS384', 'ES512' are used without proper configuration or support

## Example:
```python
import jwt

# This would raise InvalidAlgorithmError if 'none' is not in allowed algorithms
try:
    payload = jwt.decode('token.with.none.algorithm', 'secret', algorithms=['HS256'])
except jwt.InvalidAlgorithmError:
    print("Token uses an unsupported or invalid algorithm")
```

## `jwt.exceptions.MissingRequiredClaimError` · *class*

## Summary:
Represents an error that occurs when a JWT token is missing a required claim during validation.

## Description:
The MissingRequiredClaimError is raised when JWT token validation fails because a specific claim that was expected to be present in the token is missing. This exception is part of the JWT validation process and helps distinguish between different types of token validation failures. It inherits from InvalidTokenError, indicating that the token is invalid due to a structural or semantic issue rather than a cryptographic problem.

This class is typically instantiated by JWT validation functions when they encounter tokens that lack mandatory claims such as 'exp' (expiration), 'iss' (issuer), or other application-specific required fields.

## State:
- claim (str): The name of the missing required claim that caused the validation to fail. This is set during initialization and is the primary identifying characteristic of the exception instance.

## Lifecycle:
- Creation: Instantiated by JWT validation logic when a required claim is not found in the decoded token payload
- Usage: Caught by applications using try/except blocks to handle missing required claims specifically
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[MissingRequiredClaimError.__init__] --> B[Object.__init__]
    A --> C[InvalidTokenError.__init__]
    B --> D[Exception.__init__]
    C --> D
    A --> E[Sets self.claim]
    F[MissingRequiredClaimError.__str__] --> G[Returns formatted error message]
```

## Raises:
- None explicitly raised by the constructor
- Inherits all exception handling characteristics from InvalidTokenError

## Example:
```python
import jwt
from jwt.exceptions import MissingRequiredClaimError

try:
    payload = jwt.decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 
                        'secret', algorithms=['HS256'])
except MissingRequiredClaimError as e:
    print(f"Missing required claim: {e.claim}")
    # Output: Missing required claim: exp
```

### `jwt.exceptions.MissingRequiredClaimError.__init__` · *method*

## Summary:
Initializes a MissingRequiredClaimError instance with the name of the missing required claim.

## Description:
This constructor creates an exception instance that represents a JWT validation failure due to a missing required claim. The method sets up the exception's state by storing the name of the missing claim, which can later be accessed via the `claim` attribute. This allows calling code to identify exactly which required claim was not present in the JWT token during validation.

## Args:
    claim (str): The name of the required claim that was missing from the JWT token. This string identifies the specific validation failure.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.claim - stores the claim name that was missing

## Constraints:
    Preconditions: The claim parameter must be a string representing the name of a required JWT claim.
    Postconditions: After execution, the instance will have its claim attribute set to the provided claim value.

## Side Effects:
    None: This method performs no I/O operations, external service calls, or mutations to objects outside the instance.

### `jwt.exceptions.MissingRequiredClaimError.__str__` · *method*

## Summary:
Returns a formatted string representation of the missing claim error.

## Description:
This method provides a human-readable string representation of the MissingRequiredClaimError exception, indicating which JWT claim is missing from the token. It is automatically called when the exception is converted to a string or printed.

## Args:
    None

## Returns:
    str: A formatted error message indicating the missing claim in the format "Token is missing the "{claim}" claim"

## Raises:
    None

## State Changes:
    Attributes READ: self.claim
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The instance must have a claim attribute set during initialization
    Postconditions: Returns a string with the claim name properly quoted in the error message

## Side Effects:
    None

## `jwt.exceptions.PyJWKError` · *class*

## Summary:
Base exception class for JSON Web Key (JWK) related errors in the PyJWT library.

## Description:
PyJWKError is a specialized exception class that extends PyJWTError and is specifically designed to handle errors related to JSON Web Keys (JWK) operations within the PyJWT library. This exception serves as a distinct category for JWK-specific failures, allowing developers to catch JWK-related errors separately from other JWT operations while maintaining compatibility with the broader PyJWT exception hierarchy.

The class is intentionally left empty (pass) as it inherits all functionality from its parent PyJWTError class, providing only the semantic distinction needed for JWK error handling.

## State:
- No instance attributes or state variables
- Inherits all characteristics from PyJWTError and Python's built-in Exception class
- Acts as a marker class for JWK-related exceptions within the JWT ecosystem

## Lifecycle:
- Creation: Instantiated like any other Exception subclass (direct instantiation or via inheritance)
- Usage: Used in try/except blocks to handle JWK-specific JWT-related errors
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[PyJWKError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[BaseException]
    D --> E[object]
```

## Raises:
- Can be raised directly when JWK operations fail
- Typically raised by other JWK-specific exceptions that inherit from it

## Example:
```python
try:
    # Some JWK operation
    key = jwt.jwk_from_dict(jwk_dict)
except jwt.PyJWKError:
    # Handle any JWK-related error
    print("JWK operation failed")
```

## `jwt.exceptions.PyJWKSetError` · *class*

## Summary:
Base exception class for JWK Set related errors in PyJWT library.

## Description:
PyJWKSetError is a specialized exception class that extends PyJWTError for handling errors specifically related to JSON Web Key Sets (JWK Sets). This exception serves as a distinct marker for JWK Set processing failures within the PyJWT library ecosystem, allowing developers to catch JWK Set specific errors while maintaining compatibility with the broader JWT exception hierarchy.

## State:
- Inherits all state and behavior from PyJWTError (which itself inherits from Python's built-in Exception class)
- No additional instance attributes or state variables
- Maintains the standard Exception interface with message and args properties

## Lifecycle:
- Creation: Instantiated like any other Exception subclass, either directly or through inheritance
- Usage: Caught by try/except blocks when JWK Set operations fail
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[PyJWKSetError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[BaseException]
    D --> E[object]
```

## Raises:
- Raised directly when JWK Set processing operations encounter failures
- Typically raised during JWK Set parsing, validation, or key retrieval operations

## Example:
```python
try:
    # Attempt to process a JWK Set
    jwk_set = jwt.PyJWKSet.from_dict(jwk_set_dict)
except jwt.PyJWKSetError as e:
    # Handle JWK Set specific errors
    print(f"JWK Set processing failed: {e}")
```

## `jwt.exceptions.PyJWKClientError` · *class*

## Summary:
Base exception class for PyJWK client-related errors in the PyJWT library.

## Description:
PyJWKClientError is a specialized exception class that serves as the base for all exceptions thrown by the JWK (JSON Web Key) client functionality within the PyJWT library. This exception class extends PyJWTError to provide a distinct error category specifically for issues encountered when working with JSON Web Key clients, such as key retrieval failures, validation problems, or communication errors with JWK endpoints.

The purpose of having this separate exception class is to allow developers to catch JWK client-specific errors without interfering with other JWT-related exceptions, while still maintaining compatibility with the broader PyJWT exception hierarchy.

## State:
- No instance attributes or state variables
- Inherits all characteristics from PyJWTError (and ultimately Exception)
- Acts as a marker class for JWK client error handling

## Lifecycle:
- Creation: Instantiated like any other Exception subclass (direct instantiation or via inheritance)
- Usage: Used in try/except blocks to handle JWK client-related errors
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[PyJWKClientError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[BaseException]
    D --> E[object]
```

## Raises:
- Can be raised directly when JWK client operations fail
- Typically raised by other JWK client-specific exceptions that inherit from it

## Example:
```python
try:
    # Some JWK client operation
    key = jwk_client.get_key(key_id)
except jwt.PyJWKClientError:
    # Handle JWK client specific error
    print("JWK client operation failed")
```

## `jwt.exceptions.PyJWKClientConnectionError` · *class*

## Summary:
Represents connection-related errors that occur during JWK client operations.

## Description:
PyJWKClientConnectionError is a specialized exception that extends PyJWKClientError and is raised when connection-related failures occur during JSON Web Key (JWK) client operations. This exception specifically handles scenarios where network connectivity issues, timeouts, or other connection problems prevent successful communication with JWK endpoints.

This exception serves as a distinct error type within the PyJWT library's JWK client error hierarchy, allowing developers to specifically catch and handle connection failures without affecting other types of JWK client errors.

## State:
- Inherits all state from PyJWKClientError (which itself inherits from PyJWTError and Exception)
- No additional instance attributes or state variables
- Acts as a marker exception for connection-related failures in JWK client operations

## Lifecycle:
- Creation: Instantiated like any standard Exception subclass, typically by the JWK client when connection failures are detected
- Usage: Caught in try/except blocks alongside other PyJWKClientError subclasses to handle connection-specific failures
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[PyJWKClientConnectionError] --> B[PyJWKClientError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[BaseException]
    E --> F[object]
```

## Raises:
- Raised by JWK client implementations when connection establishment or maintenance fails
- Triggered during network operations such as HTTP requests to JWK endpoints
- Typically raised when encountering network timeouts, DNS resolution failures, or unreachable servers

## Example:
```python
import jwt
from jwt.exceptions import PyJWKClientConnectionError

try:
    # Attempt to fetch keys from a JWK endpoint
    key = jwk_client.get_key(key_id)
except PyJWKClientConnectionError:
    # Handle connection failure specifically
    print("Failed to establish connection to JWK endpoint")
    # Retry logic or fallback mechanism could be implemented here
```

