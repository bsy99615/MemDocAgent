# `default_magic_parameters.py`

## `datasette.default_magic_parameters.header` · *function*

## Summary:
Return a specific HTTP header's value as a UTF-8 string from an ASGI-style request.scope["headers"], normalizing underscores to hyphens and returning an empty string when the header is not present.

## Description:
This helper reads a header from an ASGI-compatible request object: it normalizes the requested header name (underscores → hyphens), encodes the name to UTF-8 bytes (ASGI header names are bytes), builds a mapping from request.scope["headers"], and returns the decoded header value.

Known callers within the provided snapshot:
    - None discovered in the provided snapshot.

Typical callers when integrated into an ASGI application:
    - Magic-parameter resolvers, view helpers, middleware, or any code that needs to read request headers within Datasette/Starlette/FastAPI-style request handlers.

Why this function exists separately:
    - Encapsulates repeated tasks: header-name normalization, encoding for ASGI lookup, safe retrieval with a default, and decoding to text. Centralizing this behavior prevents duplicated logic and ensures a consistent fallback (empty string) and decoding policy.

## Args:
    key (str)
        - Header name to retrieve. Underscores in this name are replaced with hyphens before lookup.
        - Must be a text string. The function encodes it with UTF-8 to produce the byte key used for lookup.
        - Note: matching is performed on the raw encoded bytes. This means header-name matching is effectively byte-wise and therefore sensitive to case and exact byte content. Many ASGI servers and frameworks normalize header names to lower-case bytes (e.g., b'host', b'content-type'), but this function does not change case — callers should provide the expected casing or normalize themselves if necessary.

    request (object)
        - An ASGI-style request-like object that exposes a .scope mapping with a "headers" key.
        - Expected shape: request.scope["headers"] is an iterable (commonly a list or tuple) of (name_bytes, value_bytes) pairs. Example: [(b'x-forwarded-for', b'1.2.3.4'), (b'authorization', b'Bearer ...')].
        - If headers are not in this byte-pair format, the function may raise TypeError or ValueError.

Interdependencies:
    - Correct operation depends on request.scope["headers"] containing (bytes, bytes) pairs and on using UTF-8 for key encoding and value decoding.

## Returns:
    str
        - The header value decoded from UTF-8.
        - If the header is not present, returns an empty string "" (the function looks up the byte key with default b"" and decodes that).
        - If multiple headers with the same name exist, converting the headers iterable to dict causes the last occurrence to win (i.e., the last header with that name in the iterable is returned).
        - If the header value bytes are not valid UTF-8, a UnicodeDecodeError will be raised.

## Raises:
    UnicodeDecodeError
        - Raised when the retrieved header value bytes cannot be decoded as UTF-8.

    AttributeError
        - Raised if the provided request does not have a .scope attribute (accessing request.scope will raise this).

    KeyError
        - Raised if request.scope exists but does not contain the "headers" key (request.scope["headers"]).

    TypeError
        - Raised if request.scope["headers"] is not an iterable suitable for dict() conversion (for example, None or a non-iterable), or if items are of inappropriate types for dict().

    ValueError
        - Raised if an element of request.scope["headers"] is not a two-item sequence (dict() will raise ValueError like "dictionary update sequence element #0 has length 1" in that case).

## Constraints:
Preconditions:
    - key must be a str.
    - request.scope["headers"] must be an iterable of (bytes, bytes) pairs.

Postconditions:
    - Returns a str (possibly empty) and does not modify the request or its scope.
    - No global state or external resources are modified.

## Side Effects:
    - None. The function reads from the request object only; there is no I/O, network access, or mutation of external state.

## Control Flow:
flowchart TD
    A[Start] --> B[Receive key (str) and request object]
    B --> C[Normalize key: replace "_" with "-" and encode UTF-8 -> key_bytes]
    C --> D[Access request.scope["headers"]]
    D --> E[Convert iterable headers to dict(headers) -> headers_dict]
    E --> F[Lookup headers_dict.get(key_bytes, b"") -> value_bytes]
    F --> G[Decode value_bytes using UTF-8 -> value_str]
    G --> H[Return value_str]
    D -->|no .scope| I[AttributeError]
    D -->|no "headers" key| J[KeyError]
    E -->|invalid iterable| K[TypeError or ValueError]
    G -->|invalid UTF-8| L[UnicodeDecodeError]
    note right of C: Matching is byte-wise; case matters unless the ASGI server normalized names

## Examples:
Example — expected request.shape and happy path:
    Given request.scope["headers"] == [(b'x-forwarded-for', b'1.2.3.4')]
    Call: header("x_forwarded_for", request)
    Returns: "1.2.3.4"

Example — header absent:
    Given request.scope["headers"] contains no matching name
    Call: header("X-Unknown-Header", request)
    Returns: ""

Example — handling malformed request or non-UTF-8 header values:
    Use defensive wrappers when request shape or encodings are uncertain:
        try:
            user_agent = header("user_agent", request)
        except (AttributeError, KeyError, TypeError, ValueError):
            # malformed request, treat as missing header
            user_agent = ""
        except UnicodeDecodeError:
            # header value isn't valid UTF-8; choose fallback policy
            user_agent = "<non-utf8>"

Implementation notes to preserve:
    - Replace underscores with hyphens before encoding.
    - Encode the lookup key using UTF-8 and decode header values using UTF-8.
    - Converting headers iterable to a dict makes the last header with the same name take precedence.
    - Return an empty string for missing headers (convenient for templates and string concatenation).

## `datasette.default_magic_parameters.actor` · *function*

## Summary:
Return the item for key from the request's actor mapping-like object; enforce that an actor exists and raise KeyError (without message) when no actor is present.

## Description:
This small helper centralizes the common operation of retrieving a named value from the actor information attached to a request. It first ensures that the request carries an actor (not None) and then performs an indexing lookup on that actor object.

Known callers within the codebase:
    - No explicit call sites are present in the provided fragment. This function is intended for use by code that resolves "magic parameter" values from the current request context (for example, template rendering, query expansion, or permission checks) elsewhere in the Datasette codebase.

Why this is a separate function:
    - Encapsulates the guard "request must have an actor" and the lookup logic in one place so callers do not repeat the None-check and so that the exception semantics (KeyError when there is no actor) are consistent across callers.

## Args:
    key (hashable): The key to look up on request.actor. Typically a string; any object acceptable to the actor object's __getitem__ is allowed.
    request (object): An object representing the current request context. It is expected to expose an attribute named actor. That attribute may be:
        - None: in which case this function raises KeyError (explicitly);
        - A mapping-like or mapping-compatible object that supports __getitem__;
        - Any object that implements __getitem__ (exceptions from that call may propagate).

Notes on interdependencies:
    - The function assumes the request object has an attribute named actor. It does not validate the full actor interface beyond relying on __getitem__ when actor is not None.

## Returns:
    Any: The result of request.actor[key], i.e., whatever the actor object's __getitem__ returns for the provided key.

Possible outcomes:
    - Returns the value associated with key when request.actor is present and subscriptable and the key exists.
    - Raises exceptions described below in the Raises section when preconditions are violated or the lookup fails.

## Raises:
    AttributeError: If the provided request object does not have an attribute named actor. Accessing request.actor will raise this before any explicit check.
    KeyError: Raised explicitly by this function when request.actor is present but is None (the code executes "raise KeyError" with no arguments).
    KeyError (propagated): If request.actor is present and subscriptable but does not contain the requested key, the actor object's __getitem__ will raise KeyError; this function does not catch it.
    TypeError (propagated): If request.actor exists but is not subscriptable (does not implement __getitem__), attempting request.actor[key] may raise TypeError (or another implementation-specific exception); such exceptions propagate.

Exact triggering conditions:
    - AttributeError: triggered by attribute access if request lacks attribute 'actor'.
    - Explicit KeyError: triggered when request.actor is present but is None (checked with "if request.actor is None: raise KeyError").
    - Propagated KeyError/TypeError: triggered by the actor object's __getitem__ implementation.

## Constraints:
Preconditions:
    - The caller should pass a request-like object that exposes an attribute named actor. If callers cannot guarantee this, they should handle AttributeError.
    - If callers depend on a particular actor API (e.g., dict-like semantics), they must ensure request.actor implements that API.

Postconditions:
    - On successful return, the returned value equals request.actor[key].
    - The function does not modify request or actor objects.

## Side Effects:
    - None. No I/O, network, logging, or mutation of global state occurs. The function only reads request.actor and performs an indexing operation.

## Control Flow:
flowchart TD
    A[Start] --> B[Access request.actor]
    B --> C{AttributeError?}
    C -- Yes --> D[AttributeError raised (propagated)]
    C -- No --> E{request.actor is None?}
    E -- Yes --> F[raise KeyError  (explicit, no message)]
    E -- No --> G[Attempt value = request.actor[key]]
    G --> H{Lookup success?}
    H -- Yes --> I[return value]
    H -- No --> J[underlying __getitem__ raises KeyError/TypeError -> propagated]

## Examples:
Example 1 — tolerant lookup handling both missing actor attribute and missing key:

    try:
        value = actor("id", request)
    except AttributeError:
        # request does not expose an 'actor' attribute at all
        handle_missing_actor_attribute()
    except KeyError:
        # either request.actor was None (explicit raise) or actor mapping lacks "id"
        handle_missing_actor_or_key()

Example 2 — distinguish absent actor vs missing key:

    if not hasattr(request, "actor"):
        # explicit handling if the request object is not shaped as expected
        handle_missing_actor_attribute()
    elif request.actor is None:
        # explicit handling for a request that has no authenticated actor
        handle_no_authenticated_actor()
    else:
        # safe to attempt lookup; handle missing key separately
        try:
            role = actor("role", request)
        except KeyError:
            handle_missing_role_key()

## `datasette.default_magic_parameters.cookie` · *function*

## Summary:
Return the value of a named cookie from the provided request's cookie mapping.

## Description:
- Known callers: No direct callers were discovered in the provided source snippet. This function is a small utility intended to be called anywhere the application needs to fetch a single cookie value from a request object.
- Typical context: called during request handling or template/magic-parameter evaluation where an HTTP request object is available and contains a cookies mapping.
- Responsibility boundary: encapsulates the single responsibility of retrieving a cookie value by key from a request-like object. Keeping this logic in a function centralizes the place where cookie lookups happen so callers need not access request.cookies directly and so behavior (and error handling policy) can be documented and updated in one place.

## Args:
    key (str): The cookie name to retrieve. Must be a hashable value appropriate for indexing into the request.cookies mapping (typically a string).
    request (object): An object representing the HTTP request that exposes a cookies attribute. The attribute must be a mapping-like object that supports subscription (cookies[key]) — e.g., a dict-like interface or an object implementing __getitem__.

Interdependencies:
    - The function does not coerce or validate types beyond using the values for a subscription; key and request must be compatible with the cookies mapping implementation.

## Returns:
    Any: The value stored under the given cookie name in request.cookies. The concrete type depends on the underlying cookie store (commonly a string).
    - If the cookie exists, its stored value is returned unchanged.
    - There is no normalization, decoding, or defaulting performed by this function.

## Raises:
    KeyError: If request.cookies is a mapping and the provided key is not present.
    AttributeError: If the request object does not have a cookies attribute.
    TypeError: If request.cookies exists but is not subscriptable (does not implement __getitem__), or if the key type is incompatible with the cookies mapping's indexing semantics.

## Constraints:
Preconditions:
    - The caller must provide a request object that exposes a cookies attribute.
    - request.cookies must be a mapping-like object that supports indexing with the provided key.

Postconditions:
    - No mutation of the request or its cookies mapping occurs.
    - If no exception is raised, the returned value is exactly the value stored in the cookies mapping at the requested key.

## Side Effects:
    - None. This function performs no I/O and does not mutate external state.

## Control Flow:
flowchart TD
    Start --> CheckCookiesAttr
    CheckCookiesAttr{request has cookies attribute?}
    CheckCookiesAttr -->|No| AttrError[Raise AttributeError]
    CheckCookiesAttr -->|Yes| AccessCookies
    AccessCookies[Attempt cookies[key]] -->|Subscript succeeds| ReturnValue[Return value]
    AccessCookies -->|Key not present| KeyError[Raise KeyError]
    AccessCookies -->|Not subscriptable| TypeError[Raise TypeError]

## Examples:
- Basic retrieval:
    value = cookie("session", request)

- Handling missing cookie robustly:
    try:
        session_value = cookie("session", request)
    except KeyError:
        session_value = None  # cookie not present
    except AttributeError:
        session_value = None  # request shape unexpected

- When callers expect a string:
    raw = cookie("user_pref", request)
    # raw will be the exact stored cookie value (commonly a string); callers should decode/parse it if needed

## `datasette.default_magic_parameters.now` · *function*

## Summary:
Compute and return one of three small UTC-based time values (epoch seconds, ISO date, or ISO-like datetime string) chosen by a string key.

## Description:
A compact helper that maps a small set of string keys to time values derived from the system UTC clock. The function accepts a `key` selecting which value to produce and a `request` parameter that the function does not read or modify (present for API/hook signature compatibility).

Known callers within the codebase:
    - No call sites are present in this file. This function is suitable to be invoked by a magic-parameter resolver or other dispatching code that needs these time values, but this file does not show any decoration or registration of the function itself. (The module imports hookimpl, but the function is not decorated or otherwise registered here.)

Why this logic is extracted into its own function:
    - Keeps mapping from named magic-parameter keys to concrete time-format formatting centralized and testable.
    - Ensures callers can request a named time value via a single stable API without duplicating formatting logic.

## Args:
    key (str):
        The name of the value to compute. Supported exact string values:
        - "epoch" — return the Unix timestamp in whole seconds.
        - "date_utc" — return the current UTC date as an ISO 8601 date string YYYY-MM-DD.
        - "datetime_utc" — return the current UTC datetime as "YYYY-MM-DDTHH:MM:SSZ".
        Any other value (including different strings or non-string types) will result in a KeyError being raised by this function.
    request (object):
        Ignored by this implementation. Accepted for compatibility with hook-style call signatures; callers may pass the current request object or None.

## Returns:
    Depending on `key`:
    - int (when key == "epoch"):
        - int(time.time()), i.e., Unix epoch seconds (whole seconds).
    - str (when key == "date_utc"):
        - datetime.datetime.utcnow().date().isoformat(), e.g. "2026-04-23".
    - str (when key == "datetime_utc"):
        - datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z", e.g. "2026-04-23T15:42:10Z".
    All return values are captured at the moment of the call; precision is seconds (no fractional seconds).

## Raises:
    KeyError:
        Raised unconditionally (explicit raise KeyError) when `key` is not one of the supported strings. The KeyError is raised without an attached message in this implementation.

## Constraints:
Preconditions:
    - The caller should pass a value for `key` that is one of the supported exact strings ("epoch", "date_utc", "datetime_utc"). If `key` is not equal to one of those strings (including when `key` is a non-str value), the function will raise KeyError.
    - System time functions (time.time and datetime.datetime.utcnow) must be available and functioning.

Postconditions:
    - On success, the returned value is of the documented type and format for the chosen key.
    - No external state is modified.

## Side Effects:
    - No I/O operations (files, network, stdout/stderr) are performed.
    - Does not mutate the provided `request` object or any global state.
    - Reads system clock via time.time() and datetime.datetime.utcnow().

## Control Flow:
flowchart TD
    A[Start: call now(key, request)] --> B{key == "epoch"?}
    B -- yes --> C[Return int(time.time())]
    B -- no --> D{key == "date_utc"?}
    D -- yes --> E[Return datetime.utcnow().date().isoformat()]
    D -- no --> F{key == "datetime_utc"?}
    F -- yes --> G[Return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"]
    F -- no --> H[Raise KeyError]

## Examples:
- Successful usage (conceptual):
    - Caller passes key="epoch", receives an int like 1618821234.
    - Caller passes key="date_utc", receives a string like "2026-04-23".
    - Caller passes key="datetime_utc", receives a string like "2026-04-23T15:42:10Z".

- Error handling:
    - Caller passes key="now" -> function raises KeyError. Example handling pattern:
        * try calling now(key, request)
        * on KeyError, fall back to a default value or skip magic-parameter substitution

- Integration note:
    - When used inside a hook or dispatching layer, include the second `request` argument to match expected signatures even though this function ignores it.

## `datasette.default_magic_parameters.random` · *function*

*No documentation generated.*

## `datasette.default_magic_parameters.register_magic_parameters` · *function*

## Summary:
Return a static list of magic-parameter registrations — (name, resolver) pairs that map parameter names to the callables that resolve their values.

## Description:
Provides a single list of magic-parameter registrations. Each element is a 2-tuple: the first element is the magic-parameter name (string) and the second element is the callable responsible for producing that parameter's value at request-time.

Known callers within the provided snapshot:
    - None discovered in the provided snapshot.

Typical consumers (contextual):
    - A registration/collection phase in an application or framework integration will call this function (or import and iterate the returned list) to discover which named magic parameters are available and which callables implement them.
    - Template rendering, request-handling, or parameter-substitution logic then invokes the returned callables with the expected signature to obtain concrete values.

Why this is extracted into a standalone function:
    - Centralizes the mapping of parameter names to resolver callables so the registration list is defined in one place and can be inspected, tested, or consumed by registration/collection code without duplicating the list.
    - Makes it easy to add, remove, or reorder registered magic parameters by editing a single function.

## Args:
    This function takes no arguments.

## Returns:
    list[tuple[str, callable]]
        - A list of 2-tuples. Each tuple is (name, resolver_callable).
        - In the current implementation the function returns five registrations:
            ("header", header)
            ("actor", actor)
            ("cookie", cookie)
            ("now", now)
            ("random", random)
        - The function returns direct references to the module names as looked up when the return expression is evaluated; it does not wrap, validate, or otherwise alter those objects.

## Raises:
    NameError
        - If any of the referenced names (header, actor, cookie, now, random) are not defined in the execution environment when register_magic_parameters() is invoked, Python will raise a NameError. Note: those names may be defined in this module or imported into it from elsewhere; this function does not assume a particular origin.
    (No other exceptions are raised by the function body itself.)

## Constraints:
Preconditions:
    - There are no enforced preconditions inside this function beyond normal Python name resolution rules. Callers or package initialization should ensure the intended resolver objects are available in the module namespace if they plan to call register_magic_parameters() without handling NameError.
    - Consumers expecting particular resolver signatures must ensure the returned callables conform to those signatures (this function does not enforce callable signatures).

Postconditions:
    - The returned list is a shallow Python list of tuples; it does not mutate module state.
    - Consumers may iterate the list and call the resolver callables; this function gives no guarantees about the behavior of those callables beyond providing their current identities.

## Side Effects:
    - None performed by this function itself. It only constructs and returns a Python list referencing existing objects.
    - Evaluating the names in the returned list requires those names to be resolvable; that evaluation can raise NameError (see Raises).

## Control Flow:
flowchart TD
    A[Start] --> B[Call register_magic_parameters()]
    B --> C[Evaluate names: header, actor, cookie, now, random]
    C --> D{All names resolvable?}
    D -- Yes --> E[Construct list of tuples and return it]
    D -- No --> F[NameError raised at evaluation time]

## Examples:
- Basic usage (inspection/collection):
    regs = register_magic_parameters()
    # regs will be a list like:
    # [("header", header), ("actor", actor), ("cookie", cookie), ("now", now), ("random", random)]
    for name, resolver in regs:
        register_into_framework(name, resolver)

- Defensive call guarding against missing symbols:
    try:
        regs = register_magic_parameters()
    except NameError:
        # fall back to an empty registration list or handle missing definitions
        regs = []

