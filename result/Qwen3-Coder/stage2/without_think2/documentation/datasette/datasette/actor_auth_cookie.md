# `actor_auth_cookie.py`

## `datasette.actor_auth_cookie.actor_from_request` · *function*

## Summary:
Extracts and validates an authenticated actor identifier from an HTTP request cookie.

## Description:
This function retrieves the signed "ds_actor" cookie from an HTTP request, verifies its signature using Datasette's signing mechanism, and returns the associated actor identifier if valid and unexpired. It serves as a core authentication utility for Datasette's cookie-based session management system.

## Args:
    datasette (Datasette instance): The Datasette application instance providing the unsigning capability.
    request (Request object): The HTTP request containing cookies to inspect.

## Returns:
    str or None: The actor identifier if the cookie is valid and unexpired, otherwise None.

## Raises:
    None explicitly raised; handles BadSignature exception internally.

## Constraints:
    Preconditions:
        - The request object must have a cookies attribute.
        - The datasette instance must support the unsign method.
    Postconditions:
        - Returns None if no ds_actor cookie is present.
        - Returns None if the cookie signature is invalid (BadSignature exception caught).
        - Returns None if the decoded data is not a dictionary or lacks the 'a' key.
        - Returns None if the token has expired.

## Side Effects:
    None observable side effects; purely functional extraction and validation.

## Control Flow:
```mermaid
flowchart TD
    A[Start actor_from_request] --> B{ds_actor cookie present?}
    B -- No --> C[Return None]
    B -- Yes --> D[Attempt to unsign cookie]
    D --> E{Unsign successful?}
    E -- No --> F[Return None]
    E -- Yes --> G{Decoded data is dict AND has 'a' key?}
    G -- No --> H[Return None]
    G -- Yes --> I[Get expires_at field]
    I --> J{expires_at present?}
    J -- No --> K[Return decoded["a"]]
    J -- Yes --> L[Decode base62 timestamp]
    L --> M[Compare current time with timestamp]
    M --> N{Current time > timestamp?}
    N -- Yes --> O[Return None]
    N -- No --> P[Return decoded["a"]]
```

## Examples:
```python
# Valid actor cookie
actor = actor_from_request(datasette_instance, request_with_valid_cookie)
assert actor == "some_user_id"

# Missing actor cookie
actor = actor_from_request(datasette_instance, request_without_cookie)
assert actor is None

# Expired actor cookie
actor = actor_from_request(datasette_instance, request_with_expired_cookie)
assert actor is None
```

