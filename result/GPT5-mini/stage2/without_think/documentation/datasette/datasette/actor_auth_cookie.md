# `actor_auth_cookie.py`

## `datasette.actor_auth_cookie.actor_from_request` · *function*

## Summary:
Extracts and verifies a signed actor payload from the ds_actor cookie of an incoming request and returns the actor value when the cookie is present, valid, and unexpired; returns None otherwise.

## Description:
This helper inspects request.cookies for a cookie named "ds_actor", then:
- verifies and unsigns its value via datasette.unsign(value, "actor"),
- confirms the decoded payload is a dict containing the "a" key (actor),
- optionally checks an expiry token in the "e" key (base62-encoded UNIX timestamp) and rejects the payload if expired.

Known callers and typical context:
- Request authentication/authorization middleware or request handlers that need to determine the identity/principal associated with an incoming HTTP request.
- Any part of the Datasette request processing pipeline that resolves the current actor from cookie-based authentication.

Why extracted:
- Centralizes cookie parsing, signature verification, payload validation, and expiry checks into a single reusable unit so higher-level authentication code can remain focused on policy and authorization.

## Args:
    datasette (object): An application-like object that implements unsign(signed_value: str, purpose: str) -> object. The function expects that:
        - On success, unsign returns the decoded payload (commonly a dict).
        - On signature verification failure, unsign raises itsdangerous.BadSignature.
    request (object): A request-like object with a cookies mapping attribute supporting membership testing and item access (e.g., request.cookies["ds_actor"]).

Interdependencies:
    - datasette.unsign is only invoked if "ds_actor" exists in request.cookies.
    - The function assumes datasette.unsign returns a mapping-like payload when successful.

## Returns:
    - decoded["a"]: The actor value stored under the "a" key of the decoded payload. This value is returned verbatim (no coercion).
    - None: Returned in all failure cases:
        * ds_actor cookie is missing
        * Signature verification fails (BadSignature)
        * Decoded payload is not a dict or lacks the "a" key
        * An expiry ("e") exists and decodes to a past timestamp

Notes on edge cases:
    - If decoded["a"] exists but its value is None, this function returns None; callers cannot distinguish between a None actor and other failure modes that also return None.
    - If the "e" field is present but falsy (e.g., empty string, None, or other false-equivalent), the code treats it as "no expiry" because it checks truthiness (if expires_at:).
    - The function expects baseconv.base62.decode(expires_at) to return a string or value convertible to int representing a UNIX timestamp (seconds since epoch). The result is converted with int(...).

## Raises:
    - itsdangerous.BadSignature: caught internally; the function handles this by returning None.
    - Any other exceptions raised by datasette.unsign (not BadSignature) will propagate to the caller.
    - Exceptions from baseconv.base62.decode (for malformed "e" values) or int(...) (e.g., ValueError, TypeError) will propagate to the caller; they are not caught here.
    - Accessing request.cookies may raise exceptions if request is not the expected shape; such errors propagate.

## Constraints:
Preconditions:
    - request must expose a cookies mapping-like attribute.
    - datasette must expose an unsign(value, purpose) method compatible with itsdangerous-style signed payloads.
    - When present, "e" must be a base62-encoded representation of a UNIX timestamp convertible to int.

Postconditions:
    - Successful return guarantees the returned value equals decoded["a"] from a valid, unexpired payload.
    - On any validation failure, the function returns None and does not mutate external state.

## Side Effects:
    - No I/O (no file or network access) and no stdout output.
    - No mutation of global or external state within this function.
    - Calls datasette.unsign (which may perform internal checks) but this function does not itself modify datasette state.

## Control Flow:
flowchart TD
    A[Start] --> B{"ds_actor" in request.cookies?}
    B -- No --> C[Return None]
    B -- Yes --> D[Call datasette.unsign(cookie_value, "actor")]
    D --> E{BadSignature raised?}
    E -- Yes --> C
    E -- No --> F[decoded payload returned]
    F --> G{payload is dict and has key "a"?}
    G -- No --> C
    G -- Yes --> H[expires_at = decoded.get("e")]
    H --> I{expires_at truthy?}
    I -- No --> J[Return decoded["a"]]
    I -- Yes --> K[ts = int(baseconv.base62.decode(expires_at))]
    K --> L{time.time() > ts ?}
    L -- Yes --> C
    L -- No --> J

## Examples:
- Happy path:
    * Preconditions: request.cookies["ds_actor"] exists; datasette.unsign returns {"a": "user:42"}; no "e" key.
    * Outcome: returns "user:42".

- With expiry:
    * Preconditions: decoded payload is {"a": "user:42", "e": "<base62 of future timestamp>"}.
    * Outcome: returns "user:42" until the timestamp passes, after which it returns None.

- Expired or invalid:
    * If the "e" timestamp decodes to a past time, or the signature is invalid, the function returns None.

- Malformed expiry:
    * If "e" is present but not valid base62 or decodable to an int (e.g., "not-base62"), baseconv.base62.decode or int() will raise (such as ValueError) and the exception will propagate to the caller; this function intentionally does not swallow such errors.

