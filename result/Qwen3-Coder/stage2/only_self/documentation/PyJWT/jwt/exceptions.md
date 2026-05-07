# `exceptions.py`

## `jwt.exceptions.PyJWTError` · *class*

## Summary:
Base exception class for the PyJWT library that provides a common parent for all JWT-related exceptions.

## Description:
PyJWTError serves as the root exception class for all exceptions raised by the PyJWT library. It is designed to allow users to catch all JWT-related errors with a single except clause. This class inherits from Python's built-in Exception class and provides a consistent error handling interface for JWT operations.

This abstraction exists to create a clear boundary between JWT-specific errors and general Python exceptions, making error handling more predictable and organized for developers using the PyJWT library.

## State:
The class has no instance attributes beyond those inherited from Exception. It maintains no internal state.

## Lifecycle:
Creation: Instances are created by inheriting from this class or by raising it directly. No special initialization is required.
Usage: Typically used as a base class for more specific JWT exceptions like ExpiredSignatureError, InvalidTokenError, etc.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[PyJWTError] --> B[Exception]
    B --> C[Base Exception Handling]
```

## Raises:
This class itself does not raise any exceptions. It is meant to be raised or inherited by other exception classes in the JWT library.

## Example:
```python
try:
    # Some JWT operation that fails
    token = jwt.decode('invalid_token', 'secret', algorithms=['HS256'])
except jwt.PyJWTError:
    # Handle all JWT-related errors
    print("A JWT error occurred")
```

## `jwt.exceptions.InvalidTokenError` · *class*

## Summary:
Represents an error that occurs when a JWT token is invalid or cannot be processed due to structural or format issues.

## Description:
InvalidTokenError is a specific exception type in the PyJWT library that indicates a JWT token is malformed, improperly formatted, or otherwise invalid in a way that prevents successful decoding or processing. This exception inherits from PyJWTError, making it part of the unified JWT error handling system.

This class exists as a distinct abstraction to allow developers to specifically catch and handle cases where tokens are fundamentally invalid, separate from other JWT-related errors like expired signatures or incorrect algorithms. It provides a clear signal that the token itself is problematic rather than a validation issue.

The exception is typically raised during JWT decoding operations when the token structure doesn't conform to the expected JWT format (header.payload.signature), when the token components are not properly base64url encoded, or when the token contains invalid characters or structures.

## State:
The class has no instance attributes beyond those inherited from Exception and PyJWTError. It maintains no internal state.

## Lifecycle:
Creation: Instances are created automatically when JWT operations encounter invalid tokens, or can be raised manually by developers when they detect invalid token conditions. No special initialization parameters are required.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific error handling for invalid token scenarios. It can be used to distinguish invalid token errors from other JWT-related errors such as ExpiredSignatureError or InvalidAlgorithmError.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[InvalidTokenError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised when JWT operations encounter tokens that fail validation checks or are structurally unsound, particularly during decoding operations.

## Example:
```python
import jwt

# Example 1: Catching InvalidTokenError specifically
try:
    decoded = jwt.decode('invalid.token.format', 'secret', algorithms=['HS256'])
except jwt.InvalidTokenError:
    print("Received an invalid JWT token")

# Example 2: Catching all JWT errors including InvalidTokenError
try:
    decoded = jwt.decode('another.invalid.token', 'secret', algorithms=['HS256'])
except jwt.PyJWTError:
    print("A JWT error occurred (could be invalid token, expired signature, etc.)")
```

## `jwt.exceptions.DecodeError` · *class*

## Summary:
Represents an error that occurs when a JWT token cannot be decoded due to structural or format issues.

## Description:
DecodeError is a specific exception type in the PyJWT library that indicates a JWT token is malformed or improperly formatted in a way that prevents successful decoding. This exception inherits from InvalidTokenError, making it part of the unified JWT error handling system.

This class serves as a distinct abstraction to allow developers to specifically catch and handle cases where JWT decoding fails due to token structure problems, separate from other JWT-related errors like expired signatures or incorrect algorithms. It provides a clear signal that the token cannot be decoded at all, rather than being valid but failing validation checks.

The exception is typically raised during JWT decoding operations when the token structure doesn't conform to the expected JWT format (header.payload.signature), when the token components are not properly base64url encoded, or when the token contains invalid characters or structures that make parsing impossible.

## State:
The class has no instance attributes beyond those inherited from Exception and InvalidTokenError. It maintains no internal state. The class inherits all behavior from its parent class InvalidTokenError.

## Lifecycle:
Creation: Instances are created automatically when JWT decoding operations encounter tokens that cannot be parsed or decoded, or can be raised manually by developers when they detect decode-specific invalid token conditions. No special initialization parameters are required.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific error handling for decoding failures. It can be used to distinguish decode errors from other JWT-related errors such as ExpiredSignatureError or InvalidAlgorithmError.
Destruction: Inherits standard Python exception cleanup behavior from the Exception hierarchy.

## Method Map:
```mermaid
graph TD
    A[DecodeError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised when JWT decoding operations encounter tokens that fail to parse or decode due to structural or format issues, particularly during the initial parsing phase of JWT processing.

## Example:
```python
import jwt

# Example 1: Catching DecodeError specifically for decoding failures
try:
    decoded = jwt.decode('invalid.token.format', 'secret', algorithms=['HS256'])
except jwt.DecodeError:
    print("Failed to decode JWT token - likely malformed or improperly formatted")

# Example 2: Catching DecodeError alongside other JWT decoding errors
try:
    decoded = jwt.decode('malformed.token.here', 'secret', algorithms=['HS256'])
except jwt.DecodeError:
    print("Token could not be decoded due to structural issues")
except jwt.ExpiredSignatureError:
    print("Token signature has expired")
except jwt.InvalidAlgorithmError:
    print("Token uses an invalid algorithm")
```

## `jwt.exceptions.InvalidSignatureError` · *class*

## Summary:
Represents an error that occurs when a JWT token's signature is invalid or cannot be verified during decoding.

## Description:
InvalidSignatureError is a specific exception type in the PyJWT library that indicates a JWT token's signature validation has failed. This exception inherits from DecodeError, which means it's part of the JWT decoding error hierarchy and specifically signals that while the token structure may be valid, the cryptographic signature verification process has failed.

This class exists as a distinct abstraction to allow developers to specifically catch and handle cases where JWT signature validation fails, separate from other token decoding issues like malformed structure or invalid algorithms. It provides a clear signal that the token's integrity cannot be verified, potentially indicating tampering or use of an incorrect secret/key.

The exception is typically raised during JWT decoding operations when the token's signature (the third component of a JWT) does not match the expected signature computed using the provided secret or public key, indicating that either:
1. The token has been modified since it was issued
2. The wrong secret/key was used for verification
3. The token was issued by a different party than expected

## State:
The class has no instance attributes beyond those inherited from Exception and its parent classes. It maintains no internal state. No constructor parameters are required as it's a simple marker exception.

## Lifecycle:
Creation: Instances are created automatically by the JWT library when signature validation fails during decoding operations. No explicit instantiation is required by developers.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific handling for signature verification failures. Developers can catch this exception separately from other InvalidTokenError cases to implement appropriate signature validation logic.
Destruction: Inherits standard Python exception cleanup behavior from the Exception hierarchy.

## Method Map:
```mermaid
graph TD
    A[InvalidSignatureError] --> B[DecodeError]
    B --> C[InvalidTokenError]
    C --> D[PyJWTError]
    D --> E[Exception]
    E --> F[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised by JWT decoding operations when signature verification fails during token validation.

## Example:
```python
import jwt

# Example of catching InvalidSignatureError specifically
try:
    decoded = jwt.decode('valid.token.with.invalid.signature', 'wrong_secret', algorithms=['HS256'])
except jwt.InvalidSignatureError:
    print("Token signature could not be verified - possibly tampered with or wrong secret used")

# Example of catching InvalidSignatureError alongside other JWT decoding errors
try:
    decoded = jwt.decode('token.with.wrong.signature', 'secret', algorithms=['HS256'])
except jwt.InvalidSignatureError:
    print("Token signature verification failed")
except jwt.DecodeError:
    print("Token could not be decoded due to structural issues")
except jwt.ExpiredSignatureError:
    print("Token signature has expired")
```

## `jwt.exceptions.ExpiredSignatureError` · *class*

## Summary:
Represents an error that occurs when a JWT token has expired and cannot be processed.

## Description:
ExpiredSignatureError is a specific exception type in the PyJWT library that indicates a JWT token has exceeded its validity period and is no longer considered valid for processing. This exception inherits from InvalidTokenError, which means it's part of the broader category of invalid JWT tokens, but specifically identifies expiration as the cause.

This class exists as a distinct abstraction to allow developers to specifically catch and handle expired token scenarios separately from other invalid token conditions. It enables more granular error handling where applications can differentiate between tokens that are malformed (InvalidTokenError) versus tokens that are valid but have expired (ExpiredSignatureError).

The exception is typically raised during JWT decoding operations when the token's expiration timestamp (exp claim) has passed the current time, indicating that the token should no longer be accepted for authentication or authorization purposes.

## State:
The class has no instance attributes beyond those inherited from Exception and PyJWTError. It maintains no internal state. No constructor parameters are required as it's a simple marker exception.

## Lifecycle:
Creation: Instances are created automatically by the JWT library when token expiration is detected during decoding operations. No explicit instantiation is required by developers.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific handling for expired tokens. Developers can catch this exception separately from other InvalidTokenError cases to implement appropriate expiration handling logic.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[ExpiredSignatureError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised by JWT decoding operations when a token's expiration timestamp has passed.

## Example:
```python
import jwt

# Example of catching ExpiredSignatureError specifically
try:
    decoded = jwt.decode('expired.token.with.exp.claim', 'secret', algorithms=['HS256'])
except jwt.ExpiredSignatureError:
    print("Token has expired and is no longer valid")
    # Implement refresh token logic or redirect to login
    
# Example of catching all JWT errors including ExpiredSignatureError
try:
    decoded = jwt.decode('expired.token', 'secret', algorithms=['HS256'])
except jwt.PyJWTError:
    print("A JWT error occurred (could be expired signature, invalid token, etc.)")
```

## `jwt.exceptions.InvalidAudienceError` · *class*

## Summary:
Represents an error that occurs when a JWT token's audience claim validation fails.

## Description:
InvalidAudienceError is a specific exception type in the PyJWT library that indicates a JWT token's audience claim (aud) validation has failed during token decoding. This exception inherits from InvalidTokenError, making it part of the unified JWT error handling system.

This class exists as a distinct abstraction to allow developers to specifically catch and handle cases where tokens are valid in structure but fail audience validation requirements, separate from other JWT-related errors like expired signatures or incorrect algorithms. It provides a clear signal that the token's audience validation has failed rather than the token being fundamentally malformed.

The exception is typically raised during JWT decoding operations when the audience validation process detects that the token's aud claim does not meet the expected audience criteria set by the application during decoding.

## State:
The class has no instance attributes beyond those inherited from Exception and InvalidTokenError. It maintains no internal state. The constructor accepts the same arguments as its parent class, allowing for standard exception initialization with optional message and args parameters.

## Lifecycle:
Creation: Instances are created automatically when JWT operations encounter audience validation failures, or can be raised manually by developers when they detect audience validation issues. No special initialization parameters are required beyond those inherited from Exception.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific error handling for audience validation failures. It can be used to distinguish audience validation errors from other JWT-related errors such as InvalidTokenError or ExpiredSignatureError.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[InvalidAudienceError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised when JWT operations encounter tokens where the audience validation fails, typically during decoding operations when the aud claim in the token doesn't satisfy the audience validation requirements.

## Example:
```python
import jwt

# Example 1: Catching InvalidAudienceError specifically
try:
    decoded = jwt.decode(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJleGFtcGxlLmNvbSJ9.signed',
        'secret',
        algorithms=['HS256'],
        audience='expected.example.com'
    )
except jwt.InvalidAudienceError:
    print("Token audience does not match expected audience")

# Example 2: Catching audience validation errors along with other JWT errors
try:
    decoded = jwt.decode(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJleGFtcGxlLmNvbSJ9.signed',
        'secret',
        algorithms=['HS256'],
        audience='wrong.example.com'
    )
except jwt.InvalidAudienceError:
    print("Audience validation failed")
except jwt.InvalidTokenError:
    print("Token is invalid for another reason")
```

## `jwt.exceptions.InvalidIssuerError` · *class*

## Summary:
Represents an error that occurs when a JWT token's issuer claim does not match the expected value during validation.

## Description:
InvalidIssuerError is a specialized exception that indicates a JWT token contains an invalid issuer claim. This exception is raised when JWT decoding/validation operations detect that the token's issuer (iss) field does not match the expected issuer value configured for validation. It inherits from InvalidTokenError, making it part of the JWT validation error hierarchy.

This class serves as a distinct abstraction to allow developers to specifically catch and handle issuer validation failures separately from other token validation issues. It enables fine-grained error handling for cases where the token structure is valid but the issuer is unauthorized or unexpected.

The exception is typically raised during JWT decoding operations when using validation parameters that specify expected issuers, such as when calling jwt.decode() with an 'issuer' parameter.

## State:
The class has no instance attributes beyond those inherited from Exception and InvalidTokenError. It maintains no internal state and requires no initialization parameters.

## Lifecycle:
Creation: Instances are created automatically by JWT decoding operations when issuer validation fails, or can be raised manually by developers when they detect invalid issuer conditions. No special initialization parameters are required.
Usage: Typically caught in try-except blocks alongside other JWT validation exceptions to provide specific error handling for issuer-related validation failures.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[InvalidIssuerError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised when JWT operations encounter tokens with invalid issuer claims during validation, particularly when the 'issuer' parameter is specified in decode operations and the token's iss field doesn't match the expected value.

## Example:
```python
import jwt

# Example 1: Catching InvalidIssuerError specifically
try:
    decoded = jwt.decode(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1cm46Y29tOm5vbmV4YW1wbGU6dXJsOjEiLCJzdWIiOiJhZG1pbiIsImF1ZCI6Imh0dHA6Ly9leGFtcGxlLmNvbSIsImlzcyI6InVybjpjb206bm9uZXhhbXBsZTp1cmw6MSIsImV4cCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        'secret',
        algorithms=['HS256'],
        issuer='urn:com:nonexample:url:1'
    )
except jwt.InvalidIssuerError:
    print("Token issuer is invalid or unauthorized")

# Example 2: Catching issuer errors alongside other JWT validation errors
try:
    decoded = jwt.decode('valid.token.with.wrong.issuer', 'secret', algorithms=['HS256'], issuer='expected-issuer')
except jwt.InvalidIssuerError:
    print("Issuer validation failed")
except jwt.InvalidTokenError:
    print("Token is invalid for other reasons")
```

## `jwt.exceptions.InvalidIssuedAtError` · *class*

## Summary:
Represents an error that occurs when a JWT token's issued-at timestamp is invalid or cannot be processed during validation.

## Description:
InvalidIssuedAtError is a specific exception type in the PyJWT library that indicates a JWT token contains an invalid issued-at (iat) timestamp. This exception inherits from InvalidTokenError, making it part of the broader category of invalid JWT tokens, but specifically identifies issues with the token's issuance time as the cause.

This class exists as a distinct abstraction to allow developers to specifically catch and handle cases where tokens have invalid issued-at timestamps, separate from other token validation issues like malformed tokens, expired signatures, or unsupported algorithms. It enables more granular error handling where applications can differentiate between various types of token validation failures.

The exception is typically raised during JWT decoding operations when the token's issued-at timestamp fails validation checks, such as when the timestamp is in the future or otherwise violates expected constraints.

## State:
The class has no instance attributes beyond those inherited from Exception and its parent classes. It maintains no internal state. No constructor parameters are required as it's a simple marker exception.

## Lifecycle:
Creation: Instances are created automatically by the JWT library when token issued-at timestamp validation fails during decoding operations. No explicit instantiation is required by developers.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific handling for issued-at timestamp validation failures. Developers can catch this exception separately from other InvalidTokenError cases to implement appropriate timestamp validation logic.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[InvalidIssuedAtError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised when JWT operations encounter tokens with invalid issued-at timestamps during validation.

## Example:
```python
import jwt

# Example of catching InvalidIssuedAtError specifically
try:
    decoded = jwt.decode('token.with.invalid.iat.timestamp', 'secret', algorithms=['HS256'])
except jwt.InvalidIssuedAtError:
    print("Token has an invalid issued-at timestamp")
    # Handle invalid timestamp scenario (e.g., log, reject, or allow grace period)

# Example of catching all JWT errors including InvalidIssuedAtError
try:
    decoded = jwt.decode('token.with.invalid.iat', 'secret', algorithms=['HS256'])
except jwt.PyJWTError:
    print("A JWT error occurred (could be invalid iat, invalid token, expired signature, etc.)")
```

## `jwt.exceptions.ImmatureSignatureError` · *class*

## Summary:
Represents an error that occurs when a JWT token is not yet valid due to a future "nbf" (not before) timestamp.

## Description:
ImmatureSignatureError is a specific exception type in the PyJWT library that indicates a JWT token's "nbf" (not before) claim specifies a future timestamp, meaning the token is not yet valid for processing. This exception inherits from InvalidTokenError, making it part of the broader category of invalid JWT tokens, but specifically identifies premature validity as the cause.

This class exists as a distinct abstraction to allow developers to specifically catch and handle cases where tokens are valid in structure but not yet within their acceptable time window. It enables more granular error handling compared to general InvalidTokenError, allowing applications to differentiate between tokens that are malformed versus tokens that are valid but not yet active.

The exception is typically raised during JWT decoding operations when the token's "nbf" claim (if present) contains a timestamp that is later than the current time, indicating that the token should not be accepted until that future time arrives.

## State:
The class has no instance attributes beyond those inherited from Exception and PyJWTError. It maintains no internal state. No constructor parameters are required as it's a simple marker exception.

## Lifecycle:
Creation: Instances are created automatically by the JWT library when token immaturity is detected during decoding operations. No explicit instantiation is required by developers.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific handling for immature tokens. Developers can catch this exception separately from other InvalidTokenError cases to implement appropriate logic for handling tokens that are not yet valid.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[ImmatureSignatureError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised by JWT decoding operations when a token's "nbf" (not before) claim contains a timestamp that exceeds the current time.

## Example:
```python
import jwt
from datetime import datetime, timedelta

# Example of catching ImmatureSignatureError specifically
try:
    # Create a token with nbf set to a future time
    payload = {
        'user_id': 123,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'nbf': datetime.utcnow() + timedelta(hours=1)  # Future time
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
except jwt.ImmatureSignatureError:
    print("Token is not yet valid - check the 'nbf' claim")
    # Handle case where token isn't active yet
    
# Example of catching all JWT errors including ImmatureSignatureError
try:
    # Similar scenario with future nbf
    payload = {
        'user_id': 123,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'nbf': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
except jwt.PyJWTError:
    print("A JWT error occurred (could be immature signature, invalid token, etc.)")
```

## `jwt.exceptions.InvalidKeyError` · *class*

## Summary:
Exception raised when an invalid or unsupported key is provided for JWT signing or verification operations.

## Description:
InvalidKeyError is a specialized exception that indicates a problem with the cryptographic key used in JWT operations. This exception is raised when the key provided for signing or verifying a JWT token is invalid, unsupported, or incompatible with the specified algorithm. It inherits from PyJWTError, making it part of the unified JWT exception hierarchy.

This exception exists to provide specific error handling for key-related issues, allowing developers to distinguish key validation problems from other JWT processing errors such as signature expiration or token corruption. It is typically raised during token decoding when the provided key doesn't match the expected format or algorithm requirements.

## State:
The class has no instance attributes beyond those inherited from Exception and PyJWTError. It maintains no internal state.

## Lifecycle:
Creation: Instances are typically raised automatically by the JWT library when key validation fails during signing or verification operations, though they can also be instantiated manually using the standard Python exception construction syntax.
Usage: Caught by exception handlers that specifically need to handle key validation failures. Should be caught alongside other JWT exceptions when implementing robust error handling.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[InvalidKeyError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised by the JWT library when key validation fails during token signing or verification operations, particularly when:
- The key is None or empty
- The key format is incompatible with the specified algorithm
- The key length is insufficient for the chosen algorithm
- An unsupported key type is provided

## Example:
```python
import jwt

# Example 1: Catching InvalidKeyError
try:
    payload = jwt.decode('token', 'invalid_key', algorithms=['HS256'])
except jwt.InvalidKeyError:
    print("The provided key is invalid or unsupported")

# Example 2: Using with other JWT exceptions
try:
    payload = jwt.decode('token', 'secret', algorithms=['HS256'])
except jwt.PyJWTError as e:
    if isinstance(e, jwt.InvalidKeyError):
        print("Key validation failed")
    elif isinstance(e, jwt.ExpiredSignatureError):
        print("Token has expired")
    else:
        print(f"Other JWT error: {e}")
```

## `jwt.exceptions.InvalidAlgorithmError` · *class*

## Summary:
Represents an error that occurs when a JWT token uses an algorithm that is not allowed or supported during validation.

## Description:
InvalidAlgorithmError is a specific exception type in the PyJWT library that indicates a JWT token was signed or encrypted using an algorithm that is either not permitted, not supported, or not explicitly allowed for validation. This exception inherits from InvalidTokenError, making it part of the JWT validation error hierarchy.

This class exists as a distinct abstraction to allow developers to specifically catch and handle cases where tokens use unauthorized or unsupported cryptographic algorithms, separate from other token validation issues like malformed tokens or expired signatures. It provides a clear signal that the algorithm used for token signing/encryption is problematic rather than the token structure itself.

The exception is typically raised during JWT decoding operations when:
1. The token's header specifies an algorithm that is not included in the allowed algorithms list provided to the decode function
2. The algorithm specified in the token is not recognized by the library
3. An algorithm is explicitly blacklisted or disabled for security reasons

## State:
The class has no instance attributes beyond those inherited from Exception and its parent classes. It maintains no internal state.

## Lifecycle:
Creation: Instances are created automatically when JWT operations encounter tokens with disallowed algorithms, or can be raised manually by developers when they detect algorithm validation failures. No special initialization parameters are required.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific error handling for algorithm validation failures. It can be used to distinguish algorithm-related errors from other JWT-related errors such as InvalidTokenError or ExpiredSignatureError.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[InvalidAlgorithmError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised when JWT operations encounter tokens that use algorithms not in the allowed list, or when the algorithm is not recognized by the library during decoding operations.

## Example:
```python
import jwt

# Example 1: Catching InvalidAlgorithmError specifically
try:
    decoded = jwt.decode('valid.token.with.unsupported.algorithm', 'secret', algorithms=['HS256'])
except jwt.InvalidAlgorithmError:
    print("Token uses an algorithm that is not allowed")

# Example 2: Catching multiple JWT errors including InvalidAlgorithmError
try:
    decoded = jwt.decode('valid.token.with.unsupported.algorithm', 'secret', algorithms=['HS256'])
except (jwt.InvalidTokenError, jwt.InvalidAlgorithmError):
    print("Token is invalid or uses an unsupported algorithm")

# Example 3: Typical usage in a web application
def validate_jwt_token(token, secret):
    try:
        return jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.InvalidAlgorithmError:
        raise ValueError("Unsupported token algorithm")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token format")
```

## `jwt.exceptions.MissingRequiredClaimError` · *class*

## Summary:
Represents an error that occurs when a JWT token is missing a required claim during validation.

## Description:
MissingRequiredClaimError is a specific exception type in the PyJWT library that indicates a JWT token lacks a required claim during validation. This exception inherits from InvalidTokenError, making it part of the unified JWT error handling system for invalid tokens.

This class exists as a distinct abstraction to allow developers to specifically catch and handle cases where tokens are valid in structure but fail validation due to missing required claims. It provides a clear signal that while the token may be syntactically correct, it doesn't contain the expected data fields necessary for proper authorization or authentication.

The exception is typically raised during JWT validation operations when a token is successfully decoded but fails validation because a required claim (such as 'exp' for expiration, 'iss' for issuer, or custom claims) is missing from the payload.

## State:
- claim (str): The name of the missing required claim that caused the error. This attribute stores the string identifier of the claim that was expected but not found in the token payload.

## Lifecycle:
Creation: Instances are created automatically when JWT validation operations detect missing required claims, or can be raised manually by developers when they validate tokens and find required claims missing. Requires a single string argument specifying the missing claim name.
Usage: Typically caught in try-except blocks alongside other JWT exceptions to provide specific error handling for validation failures. It can be used to distinguish missing claim errors from other JWT-related errors such as InvalidTokenError or ExpiredSignatureError.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[MissingRequiredClaimError] --> B[InvalidTokenError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise exceptions. It is raised when JWT validation operations encounter tokens that are structurally valid but fail validation due to missing required claims.

## Example:
```python
import jwt

# Example 1: Catching MissingRequiredClaimError specifically
try:
    decoded = jwt.decode('valid.token.without.exp', 'secret', algorithms=['HS256'], options={'require': ['exp']})
except jwt.MissingRequiredClaimError as e:
    print(f"Token missing required claim: {e.claim}")

# Example 2: Catching all JWT errors including MissingRequiredClaimError
try:
    decoded = jwt.decode('valid.token.without.iss', 'secret', algorithms=['HS256'], options={'require': ['iss']})
except jwt.PyJWTError:
    print("A JWT error occurred (could be missing claim, invalid token, expired signature, etc.)")
```

### `jwt.exceptions.MissingRequiredClaimError.__init__` · *method*

## Summary:
Initializes a MissingRequiredClaimError instance with the name of the missing required claim.

## Description:
The `__init__` method sets up a MissingRequiredClaimError exception by storing the name of the required claim that was not found in the JWT token during validation. This method is called automatically when creating instances of MissingRequiredClaimError and is part of the standard exception initialization process.

This method exists as a dedicated constructor to properly initialize the exception's state with the specific claim name that caused the validation failure. It allows downstream code to access the missing claim name through the `claim` attribute of the exception instance.

## Args:
    claim (str): The name of the required claim that was missing from the JWT token. This parameter specifies which claim validation failed due to absence.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.claim - stores the claim name that was required but missing

## Constraints:
    Preconditions: The `claim` parameter must be a string representing the name of a required JWT claim.
    Postconditions: After execution, the exception instance will have its `claim` attribute set to the provided string value.

## Side Effects:
    None: This method performs no I/O operations, external service calls, or mutations to objects outside the instance being initialized.

### `jwt.exceptions.MissingRequiredClaimError.__str__` · *method*

## Summary:
Returns a human-readable string representation of the missing claim error.

## Description:
This method provides a formatted error message indicating which JWT claim is missing from the token. It is called automatically when the exception is converted to a string or printed.

## Args:
    None

## Returns:
    str: A formatted string message in the format "Token is missing the "{claim}" claim" where {claim} is the name of the missing JWT claim.

## Raises:
    None

## State Changes:
    Attributes READ: self.claim
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The instance must have a valid claim attribute set during initialization
    Postconditions: Returns a consistent string format describing the missing claim

## Side Effects:
    None

## `jwt.exceptions.PyJWKError` · *class*

## Summary:
Base exception class for JSON Web Key (JWK) related errors in the PyJWT library.

## Description:
PyJWKError serves as the root exception class for all exceptions raised during JSON Web Key operations within the PyJWT library. This exception class extends PyJWTError to provide a specific error hierarchy for JWK-related failures such as key parsing errors, invalid key formats, or cryptographic operations that fail due to JWK issues.

The class exists as a distinct abstraction to allow developers to specifically catch JWK-related errors while maintaining compatibility with the broader PyJWT error handling system. It enables more granular error handling for applications that work extensively with JSON Web Keys.

## State:
This class inherits all state from PyJWTError and maintains no additional instance attributes. It has no constructor parameters beyond those inherited from Exception.

## Lifecycle:
Creation: Instances are created automatically when JWK-related operations fail, or manually by instantiating the class directly. No special initialization is required.
Usage: Typically used as a base class for more specific JWK exceptions or caught by exception handlers that need to handle JWK-specific errors.
Destruction: Inherits standard Python exception cleanup behavior from the Exception class.

## Method Map:
```mermaid
graph TD
    A[PyJWKError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[Base Exception Handling]
```

## Raises:
This class itself does not raise any exceptions. It is meant to be raised or inherited by other exception classes in the JWT/JWK library.

## Example:
```python
try:
    # Some JWK operation that fails
    key = jwt.JWK.from_dict({'invalid': 'key'})
except jwt.PyJWKError:
    # Handle all JWK-related errors
    print("A JWK error occurred")
```

## `jwt.exceptions.PyJWKSetError` · *class*

## Summary:
Base exception class for JWK Set-related errors in the PyJWT library.

## Description:
PyJWKSetError is a specialized exception class that serves as the base for all exceptions related to JSON Web Key Set operations within the PyJWT library. It inherits from PyJWTError, providing a consistent error handling interface for JWT operations while maintaining a clear distinction for JWK set specific failures.

This exception class is intended to be inherited by more specific JWK set-related exceptions such as invalid key set formats, missing keys, or malformed JWK sets. It allows developers to catch all JWK set related errors with a single exception handler while still maintaining the ability to handle specific JWK set errors differently when needed.

## State:
The class has no instance attributes beyond those inherited from Exception and PyJWTError. It maintains no internal state and serves purely as a categorization mechanism for JWK set related exceptions.

## Lifecycle:
Creation: Instances are created by inheriting from this class or by raising it directly. No special initialization is required as it inherits all behavior from PyJWTError.
Usage: Typically used as a base class for more specific JWK set exceptions. Can be caught by code that wants to handle all JWK set related errors uniformly.
Destruction: Inherits standard Python exception cleanup behavior from the Exception hierarchy.

## Method Map:
```mermaid
graph TD
    A[PyJWKSetError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[Base Exception Handling]
```

## Raises:
This class itself does not raise any exceptions. It is meant to be raised or inherited by other exception classes in the JWT library that relate to JWK set operations.

## Example:
```python
try:
    # Some JWK set operation that fails
    jwk_set = jwt.PyJWKSet.from_dict(jwk_set_data)
except jwt.PyJWKSetError:
    # Handle all JWK set related errors
    print("A JWK set error occurred")
```

## `jwt.exceptions.PyJWKClientError` · *class*

## Summary:
Base exception class for PyJWK client-related errors in the PyJWT library.

## Description:
PyJWKClientError serves as the root exception class for all exceptions raised by the PyJWK client functionality within the PyJWT library. This exception class inherits from PyJWTError and provides a common parent for all JWK (JSON Web Key) client-related errors, allowing developers to catch all JWK client errors with a single except clause.

This abstraction exists to create a clear boundary between JWK client-specific errors and general JWT errors, making error handling more predictable and organized for developers using the PyJWT library's JWK client features. Common scenarios that raise this exception include network failures when fetching JWK sets, invalid JWK responses, or issues with key retrieval operations.

## State:
The class has no instance attributes beyond those inherited from Exception and PyJWTError. It maintains no internal state. The class inherits all standard Exception behavior including message handling and traceback generation.

## Lifecycle:
Creation: Instances are created automatically when JWK client operations fail, or can be raised directly by code using `raise PyJWKClientError(message)`. No special initialization is required.
Usage: Typically used as a base class for more specific JWK client exceptions or caught by exception handlers that want to handle all JWK client errors.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[PyJWKClientError] --> B[PyJWTError]
    B --> C[Exception]
    C --> D[Base Exception Handling]
```

## Raises:
This class itself does not raise any exceptions. It is meant to be raised or inherited by other exception classes in the JWK client portion of the JWT library.

## Example:
```python
from jwt import PyJWKClientError
import requests

try:
    # Attempt to fetch JWK set from remote server
    client = PyJWKClient('https://example.com/.well-known/jwks.json')
    key = client.get_key('some_key_id')
except PyJWKClientError as e:
    # Handle all JWK client related errors such as network issues,
    # invalid responses, or key retrieval failures
    print(f"JWK client error occurred: {e}")
except requests.RequestException as e:
    # Handle network-related issues specifically
    print(f"Network error: {e}")
```

## `jwt.exceptions.PyJWKClientConnectionError` · *class*

## Summary:
Exception class representing connection-related errors when fetching JSON Web Key sets.

## Description:
PyJWKClientConnectionError is a specialized exception that extends PyJWKClientError to specifically indicate network connection failures when the PyJWK client attempts to retrieve JWK (JSON Web Key) sets from remote endpoints. This exception is raised when the client encounters issues such as network timeouts, DNS resolution failures, SSL/TLS handshake errors, or other communication problems during JWK set retrieval operations.

This exception provides semantic clarity for connection-specific failures, allowing developers to distinguish network connectivity issues from other JWK client errors like malformed responses or key validation failures. It serves as a distinct abstraction layer that enables targeted error handling for network-related problems in JWT authentication flows.

## State:
This class has no instance attributes beyond those inherited from Exception and PyJWKClientError. It maintains no internal state. As a simple inheritance, it behaves identically to PyJWKClientError in terms of instantiation and usage.

## Lifecycle:
Creation: Instances are created automatically when connection failures occur in JWK client operations, or can be raised directly by code using `raise PyJWKClientConnectionError(message)`. No special initialization parameters are required.
Usage: Typically caught by exception handlers that want to specifically handle connection-related JWK client errors, separate from other types of JWK client failures such as invalid key formats or key lookup issues.
Destruction: Inherits standard Python exception cleanup behavior.

## Method Map:
```mermaid
graph TD
    A[PyJWKClientConnectionError] --> B[PyJWKClientError]
    B --> C[PyJWTError]
    C --> D[Exception]
    D --> E[Base Exception Handling]
```

## Raises:
This class itself does not raise any exceptions. It is meant to be raised when connection-related failures occur in JWK client operations, particularly during HTTP requests to fetch JWK sets.

## Example:
```python
from jwt import PyJWKClientConnectionError
import requests

try:
    # Attempt to fetch JWK set from remote server
    client = PyJWKClient('https://example.com/.well-known/jwks.json')
    key = client.get_key('some_key_id')
except PyJWKClientConnectionError as e:
    # Handle specific connection failures such as timeouts or network errors
    print(f"Connection error occurred: {e}")
    # Implement retry logic or fallback mechanism
    # For example, try alternative endpoints or use cached keys
except requests.RequestException as e:
    # Handle other network-related issues
    print(f"Network error: {e}")
except Exception as e:
    # Handle other potential JWK client errors
    print(f"Other JWK client error: {e}")
```

