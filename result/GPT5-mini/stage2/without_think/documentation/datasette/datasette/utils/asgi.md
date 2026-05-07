# `asgi.py`

## `datasette.utils.asgi.Base400` · *class*

## Summary:
A lightweight Exception subclass representing an HTTP 400 (Bad Request) error; carries a constant `status` attribute (400) and otherwise uses standard Exception semantics.

## Description:
Base400 is a minimal exception type intended to signal a client-side (400 Bad Request) error from ASGI-related utility code. It exists so higher-level request/response handling code can raise or catch a distinct exception type when input or request parsing fails and then map that to an HTTP response with status 400.

Typical scenarios:
- Raised when request parsing, validation, or parameter handling detects a malformed request.
- Caught by an ASGI request handler or middleware that translates exceptions into HTTP responses.

Notes:
- The class defines no custom behaviour beyond the `status` attribute and inherits all initialization and storage behavior from Python's built-in Exception.
- No direct callers were discovered in the available snapshot of the repository; treat the above scenarios as the intended usage pattern for this exception type.

## State:
Attributes (public):
- status (int)
  - Value: 400
  - Invariant: This is a class-level constant intended to represent the HTTP status code for bad requests. It should not be modified by consumers.
- args (tuple)
  - Source: inherited from Exception
  - Meaning: positional arguments passed at instantiation (commonly a human-readable message). May be empty.

Notes on __init__ parameters:
- Base400 does not define its own __init__; it uses Exception.__init__.
- Callers may pass zero or more positional arguments (commonly a single string message). These are stored in the instance `.args` tuple.
- There are no keyword parameters defined by Base400 itself.

Class invariants:
- instance.status == 400 (inherited via class attribute)
- instance.args is a tuple (per Exception semantics)

## Lifecycle:
Creation:
- Instantiate by calling Base400(...) with zero or more positional arguments (typically a message string). Example: Base400("invalid query parameter").

Usage:
- Common pattern: raise Base400("reason") when validation fails.
- Consumer flow: raise -> propagate up call stack -> caught by a central ASGI request handler/middleware -> converted to an HTTP 400 response using the `status` value.
- No internal methods or state mutations—instances are immutable aside from standard Exception attributes.

Destruction / Cleanup:
- No special cleanup required. Instances are regular Python objects and are reclaimed by garbage collection; no context manager or close/cleanup API is provided or necessary.

## Method Map:
graph LR
    RAISE["raise Base400(...)"]
    PROPAGATE["propagate exception"]
    CATCH["ASGI handler / middleware catches Base400"]
    RESP["build HTTP response using .status (400)"]
    RAISE --> PROPAGATE --> CATCH --> RESP

(Explanation: Base400 has no methods. Typical flow is to raise an instance, let it propagate to a central handler, catch it there, and build an HTTP 400 response using the `status` attribute.)

## Raises:
- Base400 does not define any custom exceptions raised by its constructor.
- Instantiation follows Exception semantics; no additional validations are performed. Under normal use, creating Base400(...) will not raise.

## Example:
Raise and inspect a Base400 instance, and how a handler might inspect `status`:

- Raise:
    raise Base400("missing required parameter 'id'")

- Catch and inspect:
    try:
        # code that may raise Base400
        ...
    except Base400 as e:
        # e.status == 400
        # e.args contains any message(s) passed at instantiation
        message = e.args[0] if e.args else None
        # handler would use e.status (400) when building the HTTP response

This example demonstrates the intended usage: raise a distinct exception type for bad requests, then let a centralized error-to-response layer map it to a 400 response using the `status` attribute.

## `datasette.utils.asgi.NotFound` · *class*

## Summary:
A lightweight Exception subclass representing an HTTP 404 (Not Found) error; it exists so ASGI request handlers can raise a distinct exception that will be mapped to an HTTP 404 response.

## Description:
NotFound is a minimal exception type used to signal that a requested resource or route does not exist. It subclasses Base400 (a generic "client error" exception) and only overrides the class-level `status` attribute to 404. It provides no additional behavior beyond standard Exception semantics.

Scenarios where to instantiate:
- When a requested record, file, or route cannot be located during request handling.
- When request parsing or validation determines a target resource does not exist.
- Raised by lower-level utilities or view code and caught by a central ASGI error-to-response layer that converts it into an HTTP response.

Known callers / factories:
- No specific callers were discovered in the available snapshot. Typical callers are ASGI endpoint functions, route handlers, or utility functions performing lookups.

Motivation and responsibility boundary:
- Provides a clear, typed signal (NotFound) for code that wants to indicate "resource not found" without mixing messaging or HTTP details into business logic.
- Responsibility: carry the 404 status code and an optional message (via Exception args) so a central handler can build the correct HTTP response. It does not perform response construction itself.

## State:
Attributes (public):
- status (int)
  - Value: 404 (class-level)
  - Valid values: integer 404 specifically for this class
  - Invariant: instance.status == 404
  - Note: this is a class attribute intended to be constant; consumers should not mutate it.

- args (tuple)
  - Source: inherited from Exception
  - Meaning: positional arguments passed at instantiation (commonly a human-readable message). May be empty.

For __init__ parameters:
- NotFound does not define its own __init__; it inherits Exception.__init__ via Base400.
- Callers may pass zero or more positional arguments (commonly a single string message). There are no keyword-only parameters introduced by NotFound.

Class invariants:
- Any NotFound instance must have .status == 404.
- .args is a tuple (per Exception semantics).

## Lifecycle:
Creation:
- Instantiate by calling NotFound(...) with zero or more positional arguments (typically a string message). Example: NotFound("row id=123 not found").

Usage:
- Typical flow:
  1. Code performing a lookup raises NotFound("...") when the target is missing.
  2. The exception propagates up the call stack.
  3. A central ASGI handler or middleware catches NotFound and constructs an HTTP response using e.status (404) and optionally e.args for a message/body.
- There is no required call ordering beyond "raise -> propagate -> catch".

Destruction / cleanup:
- No special cleanup required. Instances are regular Python exception objects and are garbage-collected normally. NotFound does not implement context manager or close/cleanup APIs.

## Method Map:
graph LR
    RAISE["raise NotFound(...)"]
    PROPAGATE["propagate exception"]
    CATCH["ASGI handler / middleware catches NotFound"]
    RESP["build HTTP response using .status (404)"]
    RAISE --> PROPAGATE --> CATCH --> RESP

(Explanation: NotFound defines no methods. Typical invocation order is to raise an instance, let it propagate, have a centralized handler catch it, and then build an HTTP 404 response using the `status` attribute.)

## Raises:
- NotFound itself does not raise exceptions during instantiation beyond those possible from Exception.__init__ (which in normal use does not raise). No other exceptions are introduced by this class.

## Example:
- Creation and raising:
    raise NotFound("dataset 'public' not found")

- Catching and using in an ASGI handler:
    try:
        # code that may raise NotFound
        ...
    except NotFound as e:
        # build response with status 404
        status_code = e.status  # 404
        message = e.args[0] if e.args else None
        # the ASGI handler would turn this into an HTTP 404 response body and headers

This demonstrates the typical usage: raise NotFound where a resource is absent and let a centralized error-to-response layer map it to an HTTP 404 response.

## `datasette.utils.asgi.Forbidden` · *class*

## Summary:
Represents an HTTP 403 (Forbidden) error as a lightweight Exception subclass; used to signal that a client is authenticated but not authorized to access a resource.

## Description:
Forbidden is a tiny semantic exception type used by ASGI-related utility code to indicate client requests that must be rejected with HTTP status 403. It exists so higher-level request/response handling code can raise or catch a distinct exception type when authorization fails, and then map that to an HTTP 403 response.

Scenarios where to instantiate:
- When request authentication succeeded but the authenticated principal lacks permission for the requested operation or resource.
- Within route handlers, middleware, or utilities that perform authorization checks and want to short-circuit request processing.

Known callers / factories:
- There are no specific callers required by Forbidden; it is raised directly by application code or authorization layers. Typical callers are request handlers and middleware that perform permission checks.

Motivation and responsibility boundary:
- Forbidden is a declarative way to distinguish authorization failures from other client errors (e.g., bad request). It does not implement response-building logic; its responsibility is only to carry the semantic type and an optional message. Translation into an HTTP response (status, body) is the responsibility of the ASGI handler/middleware that catches the exception.

## State:
Attributes (public):
- status (int)
  - Value: 403
  - Location: class attribute on Forbidden
  - Invariant: Intended as a constant representing the HTTP status code for "Forbidden". Consumers should treat it as read-only.
- args (tuple)
  - Source: inherited from Exception
  - Meaning: positional arguments passed at instantiation (commonly a human-readable message). May be empty.

Notes on __init__ parameters:
- Forbidden does not define its own __init__; it inherits Exception.__init__ through Base400 and thus accepts zero or more positional arguments (commonly a single string message). There are no keyword parameters added by Forbidden.

Class invariants:
- instance.status == 403
- instance.args is a tuple (per Exception semantics)

## Lifecycle:
Creation:
- Instantiate by calling Forbidden(...) with zero or more positional arguments (typically a message string). Example form: Forbidden("not allowed to edit resource").
- No factory methods; direct construction is the intended usage.

Usage:
- Typical sequence: raise Forbidden("reason") when an authorization check fails.
- The exception propagates up the call stack until caught by an ASGI request handler or middleware that maps exceptions to HTTP responses.
- The handler uses the instance.status (403) to determine the HTTP status code to return to the client and may use e.args[0] (if present) as a response message or log entry.

Destruction / Cleanup:
- No special cleanup required. Instances are ordinary Python exceptions and will be garbage-collected when out of scope.

## Method Map:
graph LR
    RAISE["raise Forbidden(message?)"]
    PROPAGATE["propagate exception"]
    CATCH["ASGI handler / middleware catches Forbidden"]
    RESP["build HTTP response using .status (403)"]
    RAISE --> PROPAGATE --> CATCH --> RESP

(Explanation: Forbidden defines no methods; the flow shows the intended runtime lifecycle from raising to mapping to an HTTP 403 response.)

## Raises:
- Forbidden.__init__ does not perform validation and will not raise custom exceptions; instantiation follows Exception semantics (no additional errors are introduced by this subclass).
- Any exception raised while constructing the message object argument (if the caller supplies a complex expression) would come from the caller's expression, not from Forbidden itself.

## Example:
- Creation / raise:
    raise Forbidden("user lacks 'edit' permission for resource 123")

- Catching and mapping in a handler:
    try:
        # code that performs authorization checks and may raise Forbidden
        ...
    except Forbidden as e:
        # e.status == 403
        # message = e.args[0] if e.args else None
        # handler should return an HTTP response with status e.status (403),
        # optionally including or logging the message for diagnostics.

This demonstrates the intended usage: raise Forbidden to mark an authorization failure, then let a centralized error-to-response layer convert it into a 403 HTTP response.

## `datasette.utils.asgi.BadRequest` · *class*

## Summary:
A concrete Exception subclass used to signal an HTTP 400 (Bad Request) error in ASGI-related utilities; its primary purpose is to be raised by request-parsing or validation code so higher-level handlers can convert it into a 400 HTTP response.

## Description:
BadRequest is a minimal, semantic subclass of Base400 that carries a class-level status code of 400. It is intended to be raised when an incoming request is malformed, missing required parameters, or otherwise fails input validation. Typical callers include request parsing utilities, form/JSON body validators, and any ASGI helper functions that need to abort request processing with a client error.

Motivation:
- Provides a clear, descriptive type to raise in code that performs input validation or request parsing.
- Allows central error-handling middleware or request handlers to catch a specific exception type and map it to an HTTP 400 response using the status attribute.

Relationship to Base400:
- Inherits behavior and initialization semantics from Base400 (which itself inherits Exception semantics and documents the status constant). BadRequest explicitly sets status = 400 for clarity and direct use.

## State:
- status (int, class attribute)
  - Value: 400
  - Purpose: HTTP status code that indicates this exception represents a "Bad Request".
  - Invariant: Always equals 400 for this class and its instances (unless intentionally modified by attacker code; consumers should treat it as constant).
- args (tuple, instance attribute, inherited from Exception)
  - Value: tuple of positional arguments passed during instantiation (commonly a single human-readable message).
  - Constraint: May be empty; consumers should guard when accessing e.args[0].

Notes on __init__ parameters:
- BadRequest does not define its own __init__; it uses Base400/Exception.__init__.
- Accepts zero or more positional arguments (typically a single string message). No keyword-only parameters are defined by this class.

Class invariants:
- For any instance e of BadRequest: type(e).status == 400 and isinstance(e.args, tuple).

## Lifecycle:
Creation:
- Instantiate by calling BadRequest(...) with zero or more positional arguments. Example semantic argument: a short message describing the validation error. No special factory methods are required.

Usage:
1. Raise a BadRequest instance when validation or parsing fails.
2. Let the exception propagate to a top-level ASGI handler or middleware that catches BadRequest (or Base400) and constructs an HTTP response.
3. The handler should read the status attribute (400) and may read e.args to include a human-readable message in the response body or logs.

Destruction / Cleanup:
- No special cleanup required. Instances are regular Python exceptions reclaimed by garbage collection. There is no context manager protocol or close() required.

Sequencing:
- There is no required call order for methods because BadRequest defines no instance methods beyond those inherited from Exception. Typical sequence is: instantiate -> raise -> propagate -> catch -> convert to HTTP response.

## Method Map:
graph LR
    RAISE["Application code raises BadRequest(...)"]
    PROP["Exception propagates up the call stack"]
    CATCH["Top-level ASGI handler/middleware catches BadRequest"]
    RESP["Handler builds HTTP response using e.status (400) and optional message from e.args"]
    RAISE --> PROP --> CATCH --> RESP

(Explanation: BadRequest provides no methods of its own. The flow shows the typical lifecycle from raise to HTTP response creation.)

## Raises:
- Instantiation of BadRequest itself does not raise new exceptions beyond what Exception.__init__ might raise (which in normal use does not raise). There are no additional validation steps or side effects in the constructor.
- Accessing e.args[0] without checking that args is non-empty may raise IndexError in consumer code — consumers should check that args is non-empty before indexing.

## Example:
- Creation: construct a BadRequest with an explanatory message (passed as a positional argument). The message is stored in e.args.
- Typical usage pattern:
  - Raise BadRequest when an input check fails (for example, a required query parameter is missing).
  - Allow the error to propagate to a centralized ASGI error handler.
  - In the handler, use the exception's status attribute (400) as the HTTP response status code and optionally include e.args[0] as the response body or in structured error details.

This class is intentionally minimal: it exists as a clear semantic signal (BadRequest) and as a carrier of the HTTP status code (400) for response-building code.

## `datasette.utils.asgi.Request` · *class*

## Summary:
Represents an ASGI HTTP request, providing convenient access to method, URL components, headers, cookies, query and POST data, and the ASGI receive callable used to read request bodies.

## Description:
This class is a thin, ASGI-oriented request abstraction built around the ASGI "scope" mapping and the ASGI "receive" callable. It is intended to be instantiated inside ASGI applications or tests where the full ASGI scope and receive interface are available. Known factory: the classmethod fake(...) can be used to create a request-like instance for tests or internal code paths where no live ASGI receive callable is needed.

Responsibility boundary:
- Encapsulates read-only access to request metadata found in scope (method, path, scheme, headers, query string, url route kwargs, actor).
- Provides helpers to obtain parsed query parameters (args), cookies, and to read the request body asynchronously via the receive callable (post_body, post_vars).
- Does not perform routing, body streaming beyond reading all body fragments, nor form/multipart parsing beyond simple URL-decoded POST variables.

Typical callers:
- ASGI application code that receives (scope, receive) from the server and wants convenient property access.
- Unit tests that need a request-like object and can use Request.fake to construct one.

## State:
Attributes (public):
- scope (dict): Required. The ASGI scope for an HTTP request. Expected keys used by Request:
    - "method" (str): HTTP method. Accessing the method property will raise KeyError if absent.
    - "path" (str or bytes): Path portion of the request (may be str or bytes).
    - "raw_path" (bytes) optional: Raw path bytes; when present Request.path decodes it and strips any query string.
    - "query_string" (bytes) optional: The raw query string bytes (decoded using latin-1 by this class).
    - "headers" (list of (bytes, bytes)) optional: Lower-level header list as provided by ASGI. When absent, headers() returns an empty dict.
    - "url_route" (dict) optional: If present, .url_vars returns url_route.get("kwargs").
    - "scheme" (str) optional: Used by .scheme; defaults to "http" if missing or falsy.
    - "actor" (any) optional: Arbitrary value stored on the scope and returned by .actor.
    - Other ASGI keys are allowed but not read by this class.
- receive (async callable or None): Required for reading the request body. Should be an async callable that, when awaited, returns ASGI message dicts (e.g., {"type": "http.request", "body": b"...", "more_body": bool}). For instances created by fake(...), receive is None (so methods that await receive must not be used).

Derived properties (computed on access):
- method (str): From scope["method"]. KeyError if the key is missing.
- url (str): Full URL constructed via urlunparse((scheme, host, path, None, query_string, None)).
- url_vars (dict): Route keyword arguments; returns {} if not present.
- scheme (str): From scope.get("scheme") or "http".
- headers (dict[str, str]): Decodes ASGI header (bytes, bytes) list into a dict mapping lowercased header names to header values, decoding bytes using latin-1.
- host (str): headers.get("host") or "localhost".
- cookies (dict[str, str]): Parses the "cookie" header using http.cookies.SimpleCookie and returns {name: value}.
- path (str): Uses scope["raw_path"] if present (decoded latin-1 and split at '?') otherwise scope["path"] (returned as-is if str, else decoded utf-8).
- query_string (str): Decoded from scope.get("query_string") (latin-1).
- full_path (str): path + ("?" + query_string) if query_string exists else path.
- args (MultiParams): Parsed query parameters using parse_qs(..., keep_blank_values=True) then wrapped into MultiParams.
- actor (any): scope.get("actor", None).

Methods:
- post_body() -> bytes (async): Reads and returns the entire request body by repeatedly awaiting receive().
- post_vars() -> dict[str, str] (async): Reads the body via post_body and returns a dict of URL-decoded key/value pairs parsed by parse_qsl(..., keep_blank_values=True).
- fake(path_with_query_string, method="GET", scheme="http", url_vars=None) -> Request (classmethod): Returns a Request instance with a constructed scope and receive set to None. raw_path and query_string are encoded using latin-1 for consistency with normal ASGI.

Encoding and parsing decisions (invariants / constraints):
- Headers are decoded using latin-1 to preserve byte-to-string mapping without data loss.
- scope["raw_path"] is decoded using latin-1; scope["path"] is expected to be either a str or bytes; bytes are decoded using utf-8.
- query_string is decoded using latin-1.
- POST body is accumulated as bytes; post_vars decodes body using utf-8 before parsing with parse_qsl.
- args uses parse_qs with keep_blank_values=True so parameters with empty values are preserved.

Class invariants:
- self.scope is always a mapping that at minimum should contain "method" and "path" for most properties to work without KeyError.
- If receive is not an awaitable callable (e.g., None as created by fake), the async body-reading methods must not be called.

## Lifecycle:
Creation:
- Direct: Request(scope, receive)
    - scope (dict): ASGI HTTP scope (required).
    - receive (async callable or None): ASGI receive callable that yields message dicts when awaited. If receive is None, body-reading methods will fail.
- Test helper: Request.fake(path_with_query_string, method="GET", scheme="http", url_vars=None)
    - Builds a minimal scope appropriate for property access and testing; receive is set to None.

Usage (typical sequence):
1. Instantiate Request with scope and receive from an ASGI server, or use Request.fake in tests.
2. Access metadata properties: request.method, request.url, request.path, request.query_string, request.args, request.headers, request.cookies, request.url_vars, request.actor.
3. To read the request body:
    - Await request.post_body() to obtain raw bytes of the whole body.
    - Or await request.post_vars() to obtain body parsed as URL-encoded form key/value pairs.
4. There is no explicit cleanup or close method; when receive is provided by ASGI the server controls lifecycle. If custom receive requires cleanup, caller must manage it.

Destruction:
- No context manager or close method provided. No internal background resources are held by the Request instance itself.

## Method Map:
flowchart TD
    A[Create Request(scope, receive) or fake(...)] --> B{Read-only properties}
    B --> C[method]
    B --> D[url, scheme, host, path, query_string, full_path]
    B --> E[headers -> cookies]
    B --> F[args (query parsing)]
    B --> G[url_vars]
    B --> H[actor]
    A --> I[post_body() (async)]
    I --> J[await receive() loop -> assert message["type"] == "http.request"]
    I --> K[accumulate body bytes -> return bytes]
    K --> L[post_vars() (async) -> decode utf-8 -> parse_qsl -> return dict]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style I fill:#bbf,stroke:#333,stroke-width:1px

(The diagram shows typical invocation order: construct -> inspect properties -> optionally call asynchronous body readers that rely on receive.)

## Raises:
- KeyError:
    - Accessing .method will raise KeyError if "method" is not present in the provided scope.
    - Accessing .path may raise KeyError if "raw_path" is not present and "path" key is absent from scope.
- AssertionError:
    - post_body asserts that each message yielded by receive() has message["type"] == "http.request". If receive() yields a different type, an AssertionError is raised (the assertion message includes the message dict).
- TypeError / TypeError-like errors:
    - If headers in scope are not an iterable of (bytes, bytes) pairs, headers decoding will raise (TypeError or AttributeError).
    - If receive is None (e.g., when using Request.fake) and post_body or post_vars is awaited, attempting to await None will raise a TypeError.
- UnicodeDecodeError:
    - post_vars decodes the accumulated body bytes using utf-8 before parsing. If the body is not valid utf-8, a UnicodeDecodeError may be raised.

Notes on exceptions:
- The class performs minimal validation and propagates many errors from incorrect scope shape or a malformed ASGI receive stream to the caller to make failures visible early.

## Example (usage described step-by-step):
1. In an ASGI HTTP handler you receive (scope, receive):
   - Create a Request instance with these two values to wrap the ASGI request state.
2. Read request metadata:
   - Use request.method for HTTP method.
   - Use request.url or request.path and request.query_string for URL components.
   - Use request.args to access query parameters in a MultiParams wrapper.
   - Use request.headers and request.cookies to inspect headers and cookies.
3. To consume the request body:
   - Await request.post_body() to get the raw body as bytes (useful for JSON, binary payloads).
   - Or await request.post_vars() to get URL-encoded form body as a dict (suitable for "application/x-www-form-urlencoded").
4. For unit tests or simple code paths without an ASGI server:
   - Use Request.fake(path_with_query_string, method="GET", scheme="http", url_vars=...) to construct an instance that supports metadata properties (but not body reading since receive is None).

This documentation provides the information needed to reimplement Request: required scope keys, decoding decisions, semantics of each property and async method, error cases, and the behavior of the fake test helper.

### `datasette.utils.asgi.Request.__init__` · *method*

## Summary:
Initializes a Request instance by storing the ASGI scope mapping and the ASGI receive callable on the object, establishing the minimal state required for all Request properties and asynchronous body-reading helpers.

## Description:
This constructor is called when an ASGI application or test creates a Request wrapper around the raw ASGI inputs. Typical callers and contexts:
- ASGI application entry point that receives (scope, receive) from the server and calls Request(scope, receive) during request handling.
- Request.fake(...) classmethod used in tests and internal code to construct a request-like object with receive set to None.

Why this is its own method:
- Centralizes the minimal initialization (storing inputs) so all property accessors and async helpers have a consistent and documented place to obtain the ASGI scope and receive callable.
- Keeps object construction simple and explicit; any future validation or additional derived attributes can be added here without changing callers.

## Args:
    scope (Mapping[str, any]):
        The ASGI HTTP scope mapping for the request. Expected to contain (at minimum) keys like:
            - "method" (str)
            - "path" (str) or "raw_path" (bytes)
            - optionally "query_string" (bytes), "headers" (list[(bytes, bytes)]), "scheme", "url_route", "actor"
        The constructor does not validate presence or types of specific keys; those are consumed by Request properties later.
    receive (Callable[[], Awaitable[dict]] or None):
        The ASGI receive callable, an async callable that yields ASGI message dicts when awaited (e.g., {"type": "http.request", "body": b"...", "more_body": bool}).
        Allowed values:
            - An awaitable callable matching the ASGI receive interface for live request bodies.
            - None, used by Request.fake(...) and tests — in this case, asynchronous body-reading helpers must not be awaited.

## Returns:
    None

## Raises:
    None raised directly by this method.
    (Note: Passing values of incorrect shape or type will not raise here but will cause errors later when properties/methods access the underlying scope or attempt to await receive. For example, attempting to await a None receive will raise a TypeError at call time; missing scope keys will produce KeyError when accessed by properties.)

## State Changes:
Attributes READ:
    - None (the method does not read any existing attributes of self)
Attributes WRITTEN:
    - self.scope: set to the provided scope argument
    - self.receive: set to the provided receive argument

## Constraints:
Preconditions:
    - The caller should provide a mapping-like object for scope that behaves like the ASGI HTTP scope; at minimum the application should expect "method" and "path" (or "raw_path") keys to be present for most property accessors to work without raising KeyError.
    - If body-reading methods (post_body, post_vars) will be used, receive must be an async callable conforming to the ASGI receive message protocol. If receive is None, do not call those async methods.
Postconditions:
    - After return, the instance holds references to the provided scope and receive on self.scope and self.receive respectively; no other attributes are created or mutated by this method.
    - The Request instance is immediately usable for read-only property accessors that only consult the stored scope mapping.

## Side Effects:
    - No I/O or external service calls are made.
    - Only effect is in-memory: storing references to the provided scope and receive on the new Request object.

### `datasette.utils.asgi.Request.__repr__` · *method*

## Summary:
Return a short, human-readable string identifying this ASGI request by its HTTP method and full URL.

## Description:
This method produces a one-line diagnostic representation used when the object is inspected, logged, or otherwise converted to a string via repr(). It is invoked whenever Python's repr() is called on the Request instance, when the object is shown in a debugger or REPL, or when a logging statement includes the Request object. This logic is implemented as __repr__ (the standard Python special method) so object inspection and debugging code automatically obtain a concise, consistent description without inlining formatting at every call site.

Known callers / invocation contexts:
- repr(request) or any debugging/inspection tooling that requests the object's representation.
- Printing or logging frameworks that include the object in formatted messages (implicitly via repr()).
- Developers during interactive debugging and unit tests that assert on the textual representation.

Why this is a separate method:
- __repr__ is the Python protocol for an object's canonical textual representation; implementing it as a dedicated method ensures consistent output across the system and integrates with built-in inspection/logging behavior rather than duplicating formatting logic at call sites.

## Args:
None.

## Returns:
str: A string of the form '<asgi.Request method="{}" url="{}">' where the first placeholder is replaced with the value returned by self.method and the second with the value returned by self.url.
- Possible values: any string produced by formatting those two values; not guaranteed to be valid Python code to recreate the object.
- Edge cases: the embedded METHOD and URL values are inserted verbatim (no escaping). If they contain special characters (quotes, non-ASCII characters), they appear as-is in the resulting string.

## Raises:
- KeyError: propagated if self.method attempts to access self.scope["method"] and that key is missing (see Request.method).
- Any exception raised by computing self.url (for example, TypeError or AttributeError) will propagate. These originate from the properties used to build the URL (scheme, host, path, query_string) if self.scope is malformed or contains values of unexpected types.

## State Changes:
Attributes READ:
- self.method (property) — directly read.
- self.url (property) — directly read; this in turn reads self.scheme, self.host, self.path, and self.query_string.
Attributes WRITTEN:
- None. This method does not modify the Request instance.

## Constraints:
Preconditions:
- self.scope must be present and conform sufficiently to the ASGI request scope shape so that self.method (which accesses scope["method"]) and self.url (which assembles parts from the scope) can be computed. At minimum, a mapping-like self.scope with a "method" key is expected for the typical successful case.

Postconditions:
- No mutation to the Request object or external state.
- The method returns a str as described above.

## Side Effects:
- None. This method performs no I/O and does not mutate any objects outside of returning the formatted string.

### `datasette.utils.asgi.Request.method` · *method*

## Summary:
Read-only property that returns the HTTP method string recorded in the request scope (e.g., "GET", "POST"); it does not modify the request object.

## Description:
- Known callers and contexts:
    - Request.__repr__ uses this property to include the method in the debug representation of the Request.
    - Request.fake populates the scope with a default method ("GET") when constructing test/fake Request instances.
    - Used wherever application logic inspects the incoming request's HTTP verb during routing, middleware processing, or handler dispatch (this property provides a single canonical accessor for that value).
- Rationale for separate property:
    - Encapsulates direct access to the ASGI scope's "method" key behind a stable, discoverable attribute.
    - Keeps call sites simple and readable (request.method) and centralizes any future normalization or validation logic in one place rather than inlining scope access across the codebase.

## Args:
    None

## Returns:
    str: The value stored in self.scope["method"]. In current code this is typically an ASCII string such as "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", or "HEAD" (Request.fake sets "GET"). The method returns the exact object found in the scope without modification.

## Raises:
    KeyError: If self.scope does not contain the "method" key (because the property accesses the key via subscription).
    TypeError: If self.scope is not a subscriptable mapping (for example, None), the indexing operation will raise a TypeError (e.g., "'NoneType' object is not subscriptable").

## State Changes:
- Attributes READ:
    - self.scope
- Attributes WRITTEN:
    - None (this property does not modify the Request object or its scope)

## Constraints:
- Preconditions:
    - self.scope must be a mapping-like object supporting subscription (self.scope["method"]) and should contain the "method" key whose value is the HTTP verb (typically a str).
- Postconditions:
    - After calling, the Request object is unchanged.
    - The returned value is exactly the value stored at scope["method"].

## Side Effects:
    None. This property performs no I/O, does not call external services, and does not mutate objects outside of self.

### `datasette.utils.asgi.Request.url` · *method*

## Summary:
Assembles and returns the full request URL (scheme, network location, path and query) as a single string without mutating the request object.

## Description:
This property reads the ASGI scope-derived attributes of the Request and builds a canonical URL using urllib.parse.urlunparse. Known caller in this class: __repr__ (produces a human-readable representation of the Request). It is typically accessed during request handling when handlers, loggers, or middleware need the full request URL (for logging, redirects, debugging, or generating links).

This logic is encapsulated as a property to centralize URL assembly and decoding rules in one place rather than duplicating url construction wherever the URL is needed. That ensures consistent defaults (scheme "http", host "localhost") and consistent decoding/handling of raw_path and query_string.

## Args:
    None

## Returns:
    str: The assembled absolute URL composed of:
        - scheme (self.scheme) as the URL scheme (e.g., "http", "https")
        - netloc (self.host) as the network location (host header, optionally including port)
        - path (self.path) as the request path (raw_path decoded and with any query part removed)
        - query (self.query_string) as the raw query string (decoded using latin-1)
    Edge cases:
        - If the ASGI scope does not include a scheme, "http" is used.
        - If the request headers omit a Host, "localhost" is used as the netloc.
        - If the query string is empty, the returned URL contains no "?" suffix.
        - Percent-encoding present in the path or query is preserved (the method does not perform re-encoding).

## Raises:
    None: The property does not explicitly raise exceptions. It relies on other Request properties (scheme, host, path, query_string) which perform safe decoding and provide defaults; therefore typical scope shapes will not cause errors here.

## State Changes:
    Attributes READ:
        - self.scheme
        - self.host
        - self.path
        - self.query_string
    Attributes WRITTEN:
        - None (the Request instance is not modified)

## Constraints:
    Preconditions:
        - self.scope must be the ASGI scope dictionary supplied when the Request was constructed (this is guaranteed by Request.__init__).
        - The Request properties accessed (scheme, host, path, query_string) expect scope entries in the normal ASGI forms used by this class (headers as bytes pairs, raw_path/query_string as bytes or strings). The Request implementation handles decoding and defaults.
    Postconditions:
        - The returned value is a str representing the full URL assembled via urllib.parse.urlunparse with params and fragment omitted.
        - No attributes of self or external state are modified.

## Side Effects:
    - None: no I/O, no network calls, no file access, and no mutations of objects outside self.

### `datasette.utils.asgi.Request.url_vars` · *method*

## Summary:
Return the ASGI route keyword-arguments (URL path variables) extracted from the request scope, or an empty dictionary if none are present.

## Description:
This accessor retrieves the route-level "kwargs" that ASGI routing middleware/frameworks place into the request's scope under the "url_route" key. Typical callers are request handlers, view functions, middleware, or any code executing during the HTTP request handling pipeline that needs to read path parameters (for example, a handler that expects an "id" captured from the route). This method is a small, centralized convenience accessor so callers do not need to know the exact nested structure used within the scope; it isolates the lookup logic and the fallback-to-empty-dict behavior in a single place rather than inlining the lookup throughout the codebase.

## Args:
    None (accesses self only)

## Returns:
    dict: The mapping of URL variable names to their values as provided by the underlying ASGI route handling (commonly str->str). Possible return values:
        - A dict-like object representing the route variables (returned as-is, not a copy).
        - An empty dict if self.scope has no "url_route" entry, or if that entry provides no "kwargs".
    Notes:
        - The returned object is whatever was stored at self.scope["url_route"]["kwargs"]. The method does not coerce types or deep-copy the mapping.
        - If the stored "kwargs" is an empty mapping or otherwise falsey, the method will return a fresh empty dict (the fallback).

## Raises:
    AttributeError: If self has no attribute "scope" or if self.scope does not support dict-like get(access) (e.g., scope is None), an AttributeError will be raised by the attribute access or by calling .get.
    (No other exceptions are raised by this accessor itself.)

## State Changes:
    Attributes READ:
        - self.scope (the request's ASGI scope)
    Attributes WRITTEN:
        - None (this method does not modify the Request object or the scope)

## Constraints:
    Preconditions:
        - self.scope should be a mapping-like object (typically a dict) exposing .get(key) to perform lookups.
        - If the caller expects particular types for values (e.g., strings), those assumptions depend on the routing layer that populated scope["url_route"]["kwargs"].
    Postconditions:
        - The method returns a dict-like mapping of URL variables (or an empty dict). It guarantees not to return None.
        - It does not modify self.scope or the underlying kwargs mapping; however, because it returns the original mapping when present, external code that mutates the returned mapping will affect the original object.

## Side Effects:
    - None: this method performs no I/O and does not call external services.
    - Note: because the returned mapping may be the same object stored in self.scope, mutation of the returned mapping by the caller will affect objects outside the method (shared mutable state).

### `datasette.utils.asgi.Request.scheme` · *method*

## Summary:
Returns the request's URL scheme (e.g. "http" or "https"), using the ASGI scope value if present; does not modify the Request object.

## Description:
This read-only property retrieves the "scheme" entry from the Request's ASGI scope and falls back to the literal "http" when that entry is missing or falsy.

Known callers and contexts:
- Request.url: used when composing the absolute URL via urlunparse; invoked during URL generation for request handling and any code that needs an absolute URL.
- Request.fake: the test helper sets scope["scheme"], demonstrating the expected use at Request construction time.
- Typical lifecycle: invoked after a Request instance has been constructed from an ASGI scope (during request handling or in tests); used when building absolute links or for protocol checks.

Why this is a separate property:
- Centralizes the defaulting logic (fallback to "http") so callers can request the scheme without duplicating the fallback behavior.
- Keeps Request.url and other consumers simple and ensures a single place to change the default behavior if needed.

## Args:
None (this is accessed as a read-only property on an instance)

## Returns:
str
- The value of self.scope.get("scheme") if that value is truthy.
- Otherwise, returns the string "http".
- Typical values: "http", "https". The method does not coerce types — if a non-str (e.g. bytes) is stored in scope["scheme"], that value will be returned as-is (which may cause downstream callers that expect str to fail).

## Raises:
None directly.
- If self.scope is missing or does not implement .get, attribute access will raise an AttributeError (this occurs before any code in this property runs).
- Downstream callers (for example, urlunparse used by Request.url) may raise TypeError if the returned value is not a str.

## State Changes:
Attributes READ:
- self.scope

Attributes WRITTEN:
- None (this property does not mutate the Request instance)

## Constraints:
Preconditions:
- self.scope must be present and implement the mapping .get(key, default) interface (e.g., a dict-like ASGI scope).
- It is expected that scope["scheme"] (if present) is a str; providing non-str values may break callers that require strings.

Postconditions:
- No mutation of self or the ASGI scope occurs.
- The call returns a string (typical) or the raw value stored under "scheme" if it is non-str; callers can rely on a fallback of "http" when the scope value is absent or falsy.

## Side Effects:
- None: no I/O, no network calls, no mutation of objects outside self.

### `datasette.utils.asgi.Request.headers` · *method*

## Summary:
Return a plain dict of request headers with header names normalized to lowercase strings and values decoded to text, without mutating the Request.

## Description:
This method extracts the raw ASGI "headers" list from the request scope, decodes byte strings using the Latin-1 encoding, and normalizes header names to lowercase so callers can perform case-insensitive lookups using standard Python dict semantics.

Known callers and context:
- Invoked by request handlers, middleware, and utilities during the ASGI request handling pipeline when code needs a text-based mapping of header names to values (e.g., content negotiation, authentication, caching, logging).
- Typically used during the lifecycle stage where the incoming ASGI scope has been received and the application is preparing to handle the request.

Why this is its own method:
- Centralizes the decoding (bytes -> str) and normalization (lowercasing names) logic so all consumers get consistent header names and types.
- Keeps header parsing out of route handlers and middleware, avoiding duplicated decoding/normalization code and potential inconsistencies.

## Args:
None.

## Returns:
dict[str, str]
- A dictionary mapping header names (str) to header values (str).
- Header names are decoded from bytes with the Latin-1 encoding and converted to lowercase.
- Header values are decoded from bytes with the Latin-1 encoding.
- If the ASGI scope contains no "headers" entry or it is None, an empty dict is returned.
- If multiple header entries with the same name exist in the scope, the returned dict will contain the last value seen for that header name (earlier occurrences are overwritten).

## Raises:
- No exceptions are raised by this method in normal operation because Latin-1 decoding accepts any byte sequence.
- Possible exceptions not caused by this method but that may surface if preconditions are violated:
    - AttributeError or TypeError if self.scope is missing or is not a mapping with a .get method (this indicates an incorrectly constructed Request object).

## State Changes:
Attributes READ:
- self.scope (reads self.scope.get("headers"))

Attributes WRITTEN:
- None — this method does not modify any attributes on self.

## Constraints:
Preconditions:
- self.scope must be a mapping-like object that implements .get(key) (the Request constructor or ASGI adapter is expected to provide this).
- The ASGI "headers" value, if present, should be an iterable of (name_bytes, value_bytes) pairs where each element is bytes-like.

Postconditions:
- self is unchanged.
- A dictionary of decoded, lowercase header names to decoded header values is returned.
- The return value will always be a dict with str keys and str values (possibly empty).

## Side Effects:
- None. No I/O, no external service calls, and no mutations to objects outside self.

### `datasette.utils.asgi.Request.host` · *method*

## Summary:
Returns the request Host header value (hostname optionally plus port) as a string, falling back to "localhost" when no host header is present or when it is empty — does not modify object state.

## Description:
This property centralizes how the application obtains the Host for a request. It is used anywhere the code needs a canonical host for the current request; the most explicit known caller within this class is the url property, which builds a full URL using the scheme, host, path, and query string. Typical invocation happens during request handling when constructing absolute URLs for redirects, links, or logging.

This logic is a small, self-contained property so that:
- Host lookup and defaulting are implemented in one place (avoiding repeated "get or default" logic).
- Consumers can rely on a stable, documented return (always a non-empty string).
- It remains trivial to change defaulting or normalization later without updating every call site.

## Args:
None (accessed as a read-only property).

## Returns:
str — The Host header value as provided by the client (for example "example.com" or "example.com:8000"). If the request contains no Host header or the header value is empty or falsy, the property returns the string "localhost". The returned string is not validated or normalized beyond the decoding performed by the headers property.

Edge cases and notes:
- If the original Host header contains a port (e.g., "example.com:8000") that port is preserved in the returned string.
- IPv6 addresses may be returned in whatever format they were provided (e.g., "[::1]" or "[::1]:8000") — no additional parsing is performed here.
- Because headers are read via the headers property (which lowercases header names), the lookup is case-insensitive with respect to header name.

## Raises:
None. The implementation performs safe dictionary access and returns a default; it does not raise exceptions itself. (Underlying headers property assumes self.scope exists and contains a well-formed "headers" sequence; if that invariant is broken, errors would originate from headers, not from this property.)

## State Changes:
Attributes READ:
- self.headers

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- self.scope should be a mapping (as set on Request construction) and the headers property must be callable and return a dictionary-like mapping of header-name → header-value strings. In the normal object lifecycle (when Request is constructed with a valid ASGI scope), this holds true.

Postconditions:
- No attributes of the Request object are modified.
- The call returns a non-empty string: either the Host header value or "localhost".

## Side Effects:
- None. This property performs no I/O, does not call external services, and does not mutate objects outside of reading self.headers.

### `datasette.utils.asgi.Request.cookies` · *method*

## Summary:
Parses the HTTP "Cookie" header from the request scope and returns a dictionary mapping cookie names to their values without modifying the request object.

## Description:
This property reads the decoded request headers (self.headers), parses the value of the "cookie" header using Python's http.cookies.SimpleCookie, and returns a plain dict of cookie-name -> cookie-value pairs. Typical callers are request handlers, middleware, authentication or session code, and any view-layer logic that needs access to cookies during the request handling lifecycle. It is invoked during request processing (synchronously) after the Request instance has been created from the ASGI scope and before any response is produced.

This logic is implemented as a separate property to encapsulate cookie parsing in one place (so callers get a ready-to-use dict rather than repeating parsing logic), to keep header-decoding concerns centralized (headers are normalized in the headers property), and to avoid duplicating parsing semantics across handlers.

## Args:
    None

## Returns:
    dict[str, str]
        A dictionary mapping cookie names (strings) to cookie values (strings).
        - If the "cookie" header is absent or empty, returns an empty dict.
        - Cookie names are the keys exactly as parsed by SimpleCookie.
        - Values are Morsel.value strings (i.e., unquoted/unescaped values as parsed by http.cookies).
        - If multiple cookies with the same name are present in the header, the parsing semantics of SimpleCookie apply (the last assignment wins as exposed in the returned dict).

## Raises:
    None explicitly raised by this property.
        - Under normal use, no exceptions are raised because self.headers returns a string (or an empty string) for the "cookie" header.
        - Any exceptions originating from the underlying http.cookies module (very rare) would propagate; however, with the headers produced by this Request implementation (decoded to latin-1 strings), no exception is expected.

## State Changes:
    Attributes READ:
        - self.headers: reads the normalized headers mapping produced by the Request.headers property.

    Attributes WRITTEN:
        - None. This property does not modify any attributes of self.

## Constraints:
    Preconditions:
        - The Request instance must have been constructed with a valid ASGI scope such that Request.headers returns a dict-like mapping of header-name -> header-value where both are strings (the Request.headers property already performs this decoding).
        - Callers should not rely on this property to perform side effects or asynchronous work; it is a synchronous property.

    Postconditions:
        - The Request object remains unchanged.
        - The returned dict is a fresh native dictionary (mutating it does not affect the Request instance).
        - All cookie names present in the header will appear as keys in the returned dict (subject to SimpleCookie parsing rules).

## Side Effects:
    - None. This property performs in-memory parsing only and does not perform I/O or call external services.
    - No mutation of objects outside of the returned dict and the Request instance.

## Implementation notes and edge cases:
    - The header value parsed is the value returned by self.headers.get("cookie", ""), which comes from the ASGI scope and is decoded using latin-1 in Request.headers; therefore cookie bytes are treated as latin-1-decoded characters before parsing.
    - Empty or missing cookie header yields an empty dict.
    - Cookie attributes (e.g., Path, Domain) are ignored; only name -> value pairs are returned.
    - Quoted cookie values and common cookie syntaxes are handled by http.cookies.SimpleCookie according to the stdlib behavior.

### `datasette.utils.asgi.Request.path` · *method*

## Summary:
Return the request path as a Unicode string, decoding from the ASGI scope and removing any query string when the raw byte path is present.

## Description:
This method extracts the request path from the ASGI connection scope stored on the Request instance. It first prefers the scope's raw_path (a bytes value, if present) and decodes it with latin-1, stripping an embedded query string (anything from the first "?" onward). If raw_path is not present, it falls back to scope["path"], which may already be a str or bytes; bytes are decoded with UTF-8.

Known callers and lifecycle stage:
- Any code that needs the URL path during ASGI request handling — for example, routing/matching, logging, URL-building, or middleware that inspects the request location. This method is intended to be called during request processing after the ASGI scope has been populated.
- It is typically invoked early in the request lifecycle when a handler or middleware needs a canonical path string.

Why this is a separate method:
- Centralizes the logic for selecting between raw_path and path and for applying the correct decoding/normalization rules. This prevents duplication and ensures consistent behavior across all places that need the request path.

## Args:
This is an instance method and takes only self. There are no additional arguments.

## Returns:
str: The decoded path string.
- If scope["raw_path"] is present: the method decodes raw_path using latin-1 and returns the portion before the first "?" (query string removed).
- If scope["raw_path"] is absent: returns scope["path"] directly if it is already a str; if it is bytes, returns path.decode("utf-8").
- Possible return values include the empty string (e.g., when the path is "/".replace? — empty only if scope contains an empty path) or any valid Unicode string representing the path component of the request URL.

## Raises:
- KeyError: If neither "raw_path" nor "path" exist in self.scope and the code attempts to access scope["path"], a KeyError will be raised.
- UnicodeDecodeError: If scope["path"] is bytes and contains sequences invalid for UTF-8, decoding with path.decode("utf-8") may raise UnicodeDecodeError. (Note: decoding raw_path uses latin-1 which will not raise decoding errors because latin-1 maps every byte.)

## State Changes:
Attributes READ:
- self.scope (reads the mapping and the keys "raw_path" and/or "path")

Attributes WRITTEN:
- None (this method does not modify self or external objects)

## Constraints:
Preconditions:
- self.scope must be a mapping (dict-like) that contains either "raw_path" (preferable) or "path".
- If "path" is provided as bytes, those bytes are expected to be valid UTF-8 unless callers are prepared to handle UnicodeDecodeError.

Postconditions:
- The method returns a str representation of the path. It does not modify self.scope.
- If raw_path was used, the returned string will not include any query string (anything after the first "?").

## Side Effects:
- None. This method performs no I/O and does not mutate objects outside of reading from self.scope.

### `datasette.utils.asgi.Request.query_string` · *method*

## Summary:
Return the raw HTTP query string from the ASGI scope decoded to a Python str using latin-1; leaves the Request object unchanged.

## Description:
This method retrieves the "query_string" entry from the instance's ASGI scope, defaults to an empty bytes sequence when absent, and decodes it using the latin-1 encoding to produce a Python string.

Known callers and context:
- Not identified within this single-method excerpt. Conceptually, callers are other request-handling code paths that need the raw query string (for example: canonical URL construction, logging, or manual query parsing) and therefore request this normalized string during the request-handling lifecycle.

Why this is a separate method:
- Centralizes the small but important detail of handling a missing query_string and consistently decoding bytes to str with latin-1, avoiding repeated inline decode logic across the Request implementation.

## Args:
This method takes no explicit arguments.

## Returns:
str — The decoded query string.
- If the ASGI scope contains a bytes value under "query_string", that bytes sequence is decoded with latin-1 and returned.
- If "query_string" is absent or None in the scope, an empty string ("") is returned (because the code uses a default of b"").

## Raises:
- AttributeError: If scope["query_string"] exists but is not a bytes-like object (for example, a str), calling .decode on it will raise AttributeError. The ASGI specification expects bytes for this field; this method does not coerce non-bytes types.
- (No UnicodeDecodeError is expected for bytes values because latin-1 can decode any byte sequence.)

## State Changes:
Attributes READ:
- self.scope (reads self.scope.get("query_string"))

Attributes WRITTEN:
- None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
- self.scope must be a mapping object that supports .get and may contain a "query_string" key.
- If present, the value of scope["query_string"] should be bytes (per ASGI). Supplying a non-bytes value is a misuse and may raise AttributeError.

Postconditions:
- The Request instance is unchanged.
- The return value is always a str (possibly empty).

## Side Effects:
- None. This method performs no I/O, network calls, or mutation of external objects.

### `datasette.utils.asgi.Request.full_path` · *method*

## Summary:
Return the HTTP request path combined with its query string (if present), producing a single string representation of the requested resource.

## Description:
Known callers and context:
- No explicit callers are declared in this file. This accessor is intended to be used anywhere a complete request-target string is required (for example: logging, generating redirect/Location headers, constructing links, or routing/debug output) after a Request object has been created from ASGI scope data.
- Lifecycle stage: used at request-handling time after the Request object has been instantiated and its path and query_string attributes populated.

Why this is a dedicated method:
- Centralizes the logic for producing a single path + query-string representation so callers do not duplicate the conditional logic of whether to include a leading '?'.
- Keeps code that consumes Request instances simpler and more readable by exposing a single accessor for the commonly needed "full path" form.

## Args:
- None.

## Returns:
- str: A string equal to self.path concatenated with the query string (prefixed by '?' when present).
  - If self.query_string is falsy (empty string, None, or other falsy value), returns exactly self.path.
  - If self.query_string is truthy, returns self.path + "?" + self.query_string.

Edge-case return values:
- If self.query_string is an empty string or None, the returned value is identical to self.path.
- If self.query_string already contains a leading '?', this method will nonetheless prefix another '?' (resulting in two '?' characters) because it unconditionally inserts '?' when query_string is truthy.

## Raises:
- This method itself does not explicitly raise exceptions. However, a TypeError can occur if self.query_string is truthy but is not compatible with string concatenation (for example, if it is bytes); the expression "?" + self.query_string would then raise TypeError. Therefore callers should ensure query_string is a str when truthy.

## State Changes:
Attributes READ:
- self.path
- self.query_string

Attributes WRITTEN:
- None (this method does not modify the Request instance)

## Constraints:
Preconditions:
- The Request instance must have attributes path and query_string available.
- For safe operation without exceptions, if query_string is truthy it should be a str (or otherwise support concatenation with a str).

Postconditions:
- The method returns a str combining path and query string as described; it leaves the Request instance unmodified.

## Side Effects:
- None. The method performs no I/O, network calls, or mutations to objects other than reading self.path and self.query_string.

### `datasette.utils.asgi.Request.args` · *method*

## Summary:
Return a MultiParams wrapper containing the parsed query-string parameters for this request, preserving blank values and multiple values per key.

## Description:
This property is evaluated during request handling when code needs convenient access to URL query parameters (for example, inside view handlers, middleware, or route-processing logic). It exists as a property so callers can read parsed query parameters as a ready-to-use object without needing to reparse the raw query string everywhere.

Implementation note: it constructs and returns a datasette.utils.MultiParams instance by calling urllib.parse.parse_qs on the request's decoded query_string with keep_blank_values=True. parse_qs produces a dict mapping parameter names to lists of string values; that mapping is passed directly to MultiParams.

Known callers / contexts:
- Any request handler, view, or middleware that needs to read query parameters from a Request instance (i.e., during the HTTP request handling lifecycle, after the Request has been created and populated with its ASGI scope).
- Typically used during the request-processing phase before a response is generated.

Why this is a separate property:
- Centralizes parsing logic and encoding/blank-value policy (keep_blank_values=True) in one place.
- Avoids duplicated parse_qs calls across the codebase and provides a consistent MultiParams wrapper to callers.

## Args:
None — this is a zero-argument read-only property.

## Returns:
datasette.utils.MultiParams
- The returned object wraps the mapping produced by urllib.parse.parse_qs(qs=self.query_string, keep_blank_values=True).
- The underlying mapping maps each parameter name (str) to a list of values (list[str]).
- If the request has no query string, parse_qs returns an empty mapping, and the property returns an empty MultiParams instance.

Edge cases:
- Parameters with no value (e.g., ?a=&b) are preserved as empty strings because keep_blank_values=True.
- Multiple occurrences of the same parameter (e.g., ?a=1&a=2) are preserved as lists containing all provided values.

## Raises:
- The property itself does not explicitly raise exceptions.
- It will propagate any exceptions raised by MultiParams' constructor or by urllib.parse.parse_qs if called with an unexpected type (e.g., if self.query_string is not a str). Under normal operation (Request constructed from a standard ASGI scope), self.query_string is always a str and no exceptions are expected.

## State Changes:
Attributes READ:
- self.query_string (reads the decoded query-string derived from self.scope["query_string"]) 

Attributes WRITTEN:
- None — this property does not modify the Request object or its scope.

## Constraints:
Preconditions:
- The Request instance must be initialized with a valid ASGI scope (self.scope) such that the query_string property returns a str (the Request class ensures this by decoding scope["query_string"] with latin-1).

Postconditions:
- Returns a fresh MultiParams instance representing the parsed query parameters. The Request object remains unchanged.

## Side Effects:
- None — no I/O, no network calls, no mutation of external objects. The operation is purely in-memory parsing and object construction.

### `datasette.utils.asgi.Request.actor` · *method*

## Summary:
Return the request's "actor" value from the ASGI scope (or None if unset). This exposes the authenticated/identified actor attached to the underlying ASGI scope without mutating request state.

## Description:
This is a read-only property that fetches the "actor" entry from the ASGI scope backing this Request instance. The ASGI scope is provided when the Request is constructed and typically originates from the server/framework or authentication middleware that attaches an "actor" (for example a user identifier, user object, or other authentication principal).

Known callers and lifecycle stage:
- There are no callers inside this file; callers are application code, route handlers, middleware, or plugins that run during request handling and need to inspect the authenticated actor.
- It is invoked during the request handling pipeline (request lifecycle) whenever code handling the request needs to know who/what is acting for this request.

Why this logic is a separate property:
- Centralizes access to the "actor" value and its defaulting behavior (returning None when absent).
- Provides a stable, discoverable accessor for consumer code rather than having callers directly inspect the scope dictionary.
- Keeps the Request API consistent with other simple accessors (method, url, headers, cookies, etc.).

## Args:
None.

## Returns:
- type: Any | None
- Description: The value stored under the "actor" key in self.scope, or None if that key is not present.
- Possible values: any Python object that the application or middleware placed into scope["actor"] (commonly None, a string id, a dict, or an application-specific user object).

## Raises:
- AttributeError: If self.scope does not support the get(key, default) method (i.e., if scope is not a mapping-like object). This will propagate from the attribute access self.scope.get(...).
- (No other exceptions are raised directly by this property.)

## State Changes:
- Attributes READ: self.scope
- Attributes WRITTEN: None (this property does not modify any Request attributes or the scope)

## Constraints:
- Preconditions:
    - self.scope must be set (Request.__init__ assigns scope) and ideally be a mapping-like object implementing get(key, default) (the ASGI spec provides a dict-like scope).
- Postconditions:
    - No mutation of self or self.scope.
    - The returned value equals the result of self.scope.get("actor", None) at the time of the call.

## Side Effects:
- None. The property performs no I/O, network calls, or mutations of objects outside self.

### `datasette.utils.asgi.Request.post_body` · *method*

## Summary:
Asynchronously read and concatenate the entire HTTP request body from the ASGI receive channel, returning the full body as bytes and consuming the receive stream.

## Description:
Known callers:
- datasette.utils.asgi.Request.post_vars — calls this method to obtain the raw POST body before parsing form-encoded parameters.

Context and lifecycle:
- Invoked during request handling when a handler needs the complete request payload (typically for POST/PUT/PATCH requests).
- Runs in the ASGI request-processing stage and must be awaited by the consumer because it performs asynchronous receives.

Why this is a separate method:
- Encapsulates the ASGI receive-loop so callers do not need to duplicate low-level message-handling logic.
- Provides a single place to handle ASGI message semantics (concatenating 'body' fragments, honoring 'more_body') and to centralize edge-case handling for body collection.

## Args:
- None

## Returns:
- bytes: The concatenation of all 'body' fragments received from the ASGI receive callable.
  - Returns b"" when no body bytes are present.
  - The returned value is the raw request payload (not decoded). Callers are responsible for decoding (e.g., .decode('utf-8')) or parsing according to Content-Type.

## Raises:
- AssertionError: If a received message contains a 'type' key but its value is not the string "http.request". Trigger: the assertion message["type"] == "http.request" fails.
- KeyError: If a received message has no 'type' key (accessing message["type"] raises KeyError).
- TypeError: 
  - If self.receive is None or not an awaitable callable, awaiting it will raise a TypeError.
  - If a received message contains a 'body' key whose value is None, attempting to add it to the bytes accumulator (body += None) will raise a TypeError.
- Any exception propagated from awaiting self.receive (these are not caught) — for example, runtime errors raised by the ASGI receive implementation.

## State Changes:
Attributes READ:
- self.receive — the ASGI receive callable is awaited repeatedly and read until the message stream is exhausted.

Attributes WRITTEN:
- None — this method does not assign to any self.<attr> fields.

## Constraints:
Preconditions:
- self.receive must be an ASGI-style awaitable callable that yields dict messages with at least the ASGI HTTP request structure (expected keys: 'type', optional 'body' of type bytes, optional 'more_body' boolean).
- The caller must await this coroutine (await request.post_body()).

Postconditions:
- After successful completion, the ASGI receive stream has been consumed for this request (messages read by this method will not be available to other consumers).
- The method returns the full request body as bytes. self is not otherwise modified.

## Side Effects:
- Awaits the provided ASGI receive callable repeatedly; these awaits may perform I/O or drive other asynchronous operations in the ASGI server.
- Consumes (drains) the ASGI receive message stream for this request. Because messages are consumed, subsequent attempts to receive the same body must not be expected to succeed.
- No external writes are performed by this method itself; it only reads and concatenates incoming message bodies.

### `datasette.utils.asgi.Request.post_vars` · *method*

## Summary:
Parse the request body as application/x-www-form-urlencoded and return a mapping of form field names to their (single) string values; this consumes the request body stream.

## Description:
- Known callers and context:
    - Invoked by HTTP request handlers or middleware that need to read form-encoded POST data (application/x-www-form-urlencoded) during request processing.
    - Typical lifecycle: called during the request handling phase after routing and header parsing, when the application needs parsed POST form variables.
    - In tests, code may construct Request.fake(...) for GET/URL testing, but post_vars should not be called on a fake Request whose receive is None.

- Why this logic is its own method:
    - Reading the request body is an async IO operation (it awaits self.post_body()). Separating parsing from reading keeps IO handling centralized (post_body) and allows callers to obtain raw body or parsed form fields independently.
    - Encapsulates URL-encoded form parsing behavior (decode as UTF-8, treat blank values as present) in one place to avoid duplication across handlers.

## Args:
    None

## Returns:
    dict[str, str]
    - A dictionary mapping form field names to their last-seen string value.
    - Values and keys are Python str objects.
    - If the body is empty, returns an empty dict.
    - If the same field name appears multiple times in the form body, only the last occurrence is retained (because the implementation wraps parse_qsl(...) with dict()).
    - Fields with no value are returned with the empty string '' as their value (keep_blank_values=True).

## Raises:
    - Any exception raised by awaiting self.post_body()
        - AssertionError: propagated if post_body receives a message whose "type" is not "http.request" (post_body asserts this).
        - TypeError: if self.receive is None or not awaitable, awaiting self.post_body() may raise TypeError (e.g., when using Request.fake(...) with receive=None).
        - Any other exception raised by the receive callable will propagate.
    - UnicodeDecodeError: raised if the raw request body bytes cannot be decoded using UTF-8 (body.decode("utf-8")).
    - Any exception that parse_qsl might raise will propagate (e.g., if parse_qsl receives an invalid input in the Python standard library; the implementation does not catch parse errors).

## State Changes:
- Attributes READ:
    - self.post_body (method is invoked)
    - indirectly, self.receive is read/awaited by post_body to obtain the raw body bytes
- Attributes WRITTEN:
    - None — this method does not modify attributes on self.

## Constraints:
- Preconditions:
    - self.post_body must be an async callable on the instance (the Request class provides this).
    - The request body must be available via the ASGI receive callable bound to this Request (self.receive); otherwise awaiting post_body may fail or block.
    - The method assumes the body is UTF-8 encoded form data; callers should only use post_vars for application/x-www-form-urlencoded payloads.
- Postconditions:
    - After the call, the request body stream will have been consumed by post_body (the underlying receive will have been read). Subsequent attempts to read the body may fail or return no data depending on the ASGI receive implementation.
    - The return value is a dict[str, str] as described above; no mutation to the Request instance occurs.

## Side Effects:
    - Consumes the request body stream by awaiting messages from the ASGI receive callable (via self.post_body). This is an I/O operation that drains the body.
    - No external network or file I/O is performed beyond reading the ASGI input provided by self.receive.

### `datasette.utils.asgi.Request.fake` · *method*

*No documentation generated.*

## `datasette.utils.asgi.AsgiLifespan` · *class*

## Summary:
AsgiLifespan is an ASGI middleware/wrapper that handles the ASGI "lifespan" scope by running provided startup and shutdown handlers, and forwards all non-lifespan requests to an inner ASGI application.

## Description:
AsgiLifespan should be instantiated when an ASGI application needs centralized startup and shutdown hooks executed according to the ASGI lifespan protocol. Typical use is to wrap an existing ASGI app (the inner app) before handing the wrapped object to an ASGI server. The class listens for lifespan messages (lifespan.startup and lifespan.shutdown) and, when received, invokes the configured handlers in order.

Common callers/factories:
- An ASGI server/framework that accepts a top-level ASGI application callable and expects it to respond to lifespan messages.
- Application bootstrap code that wants to attach lifecycle hooks to an ASGI app.

Motivation and responsibility boundary:
- Responsibility: run zero-or-more async startup handlers when a "lifespan.startup" message arrives, and zero-or-more async shutdown handlers when "lifespan.shutdown" arrives; then send the corresponding ".complete" messages to the server.
- Boundary: It does not implement retries, error swallowing, or synchronous-to-async conversion. It also does not manage long-lived resources aside from invoking the handlers. Error handling and recovery are the caller's responsibility.

## State:
- app: (callable) The inner ASGI application callable. Expected signature: async callable app(scope: dict, receive: callable, send: callable) -> None (or follow ASGI semantics). Must be provided at construction time. Invariant: not None.
- on_startup: list[callable] A list of startup handler callables. Each element is expected to be callable with no arguments and return an awaitable when called (i.e., an async function or callable that returns a coroutine). Default: [] if on_startup parameter is None. Invariant: always a list after __init__.
- on_shutdown: list[callable] A list of shutdown handler callables. Same expectations and defaulting behavior as on_startup. Invariant: always a list after __init__.

Notes about handler elements:
- Each handler will be called with no arguments and awaited: await handler()
- If an element is not awaitable when called (e.g., a synchronous function), awaiting it will raise a TypeError at runtime.
- If a handler raises an exception, that exception will propagate out of AsgiLifespan.__call__ (the class does not catch exceptions), which will likely abort lifespan handling unless the ASGI server/framework catches it.

Class invariants:
- on_startup and on_shutdown are lists (possibly empty).
- app is preserved unchanged and used for non-lifespan scopes.

## Lifecycle:
Creation:
- Instantiate with AsgiLifespan(app, on_startup=None, on_shutdown=None)
  - app: required ASGI app callable (scope, receive, send)
  - on_startup: optional single callable or list of callables; if None defaults to []
  - on_shutdown: optional single callable or list of callables; if None defaults to []

Usage sequencing (typical ASGI server-driven lifecycle):
1. ASGI server calls the AsgiLifespan instance as an ASGI application: await asgi_lifespan(scope, receive, send)
2. If scope["type"] != "lifespan":
   - The wrapper forwards the call to the inner app: await app(scope, receive, send).
   - The wrapper plays no further role for this request.
3. If scope["type"] == "lifespan":
   - The wrapper enters a loop waiting for lifecycle messages by repeatedly awaiting receive().
   - On receiving a message where message["type"] == "lifespan.startup":
     - For each handler in on_startup, call it and await its result (await handler()) in list order.
     - After all handlers complete successfully, send {"type": "lifespan.startup.complete"} via send().
   - On receiving a message where message["type"] == "lifespan.shutdown":
     - For each handler in on_shutdown, call it and await its result (await handler()) in list order.
     - After all handlers complete successfully, send {"type": "lifespan.shutdown.complete"} via send() and return from __call__ (ending lifespan handling).
   - Any other message types are ignored by this loop; it continues awaiting the next message.

Destruction / cleanup responsibilities:
- There is no explicit close() or context manager support. Proper cleanup should be implemented by registering appropriate async shutdown handlers in on_shutdown.
- After handling a "lifespan.shutdown" message and sending the ".complete" message, __call__ returns; any further resource cleanup must be performed by the shutdown handlers.

## Method Map:
Diagram (Mermaid flowchart) showing the invocation flow and method interactions:

graph TD
    A[ASGI Server calls AsgiLifespan(scope, receive, send)]
    A --> B{scope["type"] == "lifespan" ?}
    B -- No --> C[await inner app(scope, receive, send)]
    B -- Yes --> D[enter receive loop]
    D --> E[await message = receive()]
    E --> F{message["type"]}
    F -- lifespan.startup --> G[for fn in on_startup: await fn()]
    G --> H[send {"type":"lifespan.startup.complete"}]
    H --> E
    F -- lifespan.shutdown --> I[for fn in on_shutdown: await fn()]
    I --> J[send {"type":"lifespan.shutdown.complete"}]
    J --> K[return (exit __call__)]
    F -- other --> E

(Note: the above mermaid uses node labels to illustrate ordering and dependencies; on_startup/on_shutdown handlers are invoked sequentially in the order stored.)

## Raises:
- __init__:
  - Does not explicitly raise exceptions. However, passing a non-callable as app will cause runtime failures when AsgiLifespan is invoked.
- __call__:
  - KeyError if the provided scope dict lacks the "type" key.
  - TypeError if a handler in on_startup/on_shutdown is not awaitable when awaited (e.g., a synchronous function) or if receive/send are not awaitable callables.
  - Any exception raised by a handler will propagate out of __call__ (this class does not catch or suppress handler exceptions).
  - Exceptions thrown by the inner app when forwarding non-lifespan scopes will propagate to the caller.

## Example:
- Instantiate:
  - Provide an ASGI app callable named "app" (signature: async callable taking scope, receive, send).
  - Provide one or more async startup and shutdown callables (each callable takes no arguments and returns an awaitable).
  - Example instantiation pattern: create AsgiLifespan(app, on_startup=startup_handler, on_shutdown=[shutdown_handler1, shutdown_handler2]).

- Typical runtime sequence:
  1. ASGI server calls the wrapper with a lifespan scope.
  2. When the server sends a "lifespan.startup" message, each startup handler is awaited in order, then the wrapper sends a "lifespan.startup.complete" message.
  3. Later, when the server sends "lifespan.shutdown", each shutdown handler is awaited in order, then the wrapper sends "lifespan.shutdown.complete" and returns.
  4. For normal HTTP/WebSocket/etc. scopes, the wrapper forwards requests to the inner app unchanged.

Implementation notes for re-creation:
- Ensure __init__ normalizes single callables into lists and sets empty lists for None inputs.
- __call__ must be async and adhere to the ASGI pattern: inspect scope["type"], await receive() in a loop for the lifespan scope, and call send() with the appropriate dictionaries.
- Do not swallow exceptions from handlers unless intentionally adding error handling logic — the original behavior lets exceptions propagate.

### `datasette.utils.asgi.AsgiLifespan.__init__` · *method*

## Summary:
Initializes the AsgiLifespan wrapper by storing the inner ASGI application and normalizing startup/shutdown handlers into lists on the instance.

## Description:
This constructor is called during application bootstrap when wrapping an existing ASGI application with AsgiLifespan so that lifecycle hooks (startup/shutdown) can be executed later when the ASGI server sends lifespan messages. Typical callers:
- Application bootstrap code that wants lifecycle hooks attached before handing the app to an ASGI server.
- Any factory that wraps an ASGI app to add lifespan behavior.

This logic is a separate method (constructor) because it establishes the object's invariants: storing the inner app and ensuring the on_startup and on_shutdown attributes are always lists. Keeping normalization here avoids repeating that normalization elsewhere and guarantees consistent behavior for later lifecycle handling code.

## Args:
    app (callable): Required. The inner ASGI application callable. Expected to follow ASGI calling convention: async callable taking (scope: dict, receive: callable, send: callable) -> None. No runtime checks are performed here; passing a non-callable will only fail later when the app is invoked.
    on_startup (callable | list[callable] | None): Optional. One handler or a list of handlers to run on "lifespan.startup". Each handler must be callable with no arguments and return an awaitable when called (i.e., be an async function or a callable that returns a coroutine). If None, defaults to an empty list. If a non-list value is provided, it is wrapped into a single-element list.
    on_shutdown (callable | list[callable] | None): Optional. Same semantics as on_startup but for "lifespan.shutdown" handlers.

## Returns:
    None. The constructor initializes instance attributes and does not return a value.

## Raises:
    None explicitly. The constructor does not raise exceptions itself. However:
    - Passing an invalid object for app (e.g., None or a non-callable) will not raise here but will likely raise at runtime when the wrapper forwards non-lifespan scopes to the inner app.
    - No validation is performed on handler callability here; problems (e.g., handlers that are not awaitable when called) will surface later when handlers are invoked.

## State Changes:
Attributes READ:
    - None (the constructor does not read any pre-existing self.<attr> attributes).

Attributes WRITTEN:
    - self.app: set to the provided app argument.
    - self.on_startup: set to a list (possibly empty) derived from the on_startup parameter.
    - self.on_shutdown: set to a list (possibly empty) derived from the on_shutdown parameter.

## Constraints:
Preconditions:
    - There is no enforced precondition in code; however, callers should provide:
        * app: a valid ASGI application callable.
        * handlers: callables that return awaitables when invoked (async functions or callables producing coroutines).

Postconditions:
    - self.app is set to the provided app object.
    - self.on_startup is guaranteed to be a list (empty if input was None).
    - self.on_shutdown is guaranteed to be a list (empty if input was None).
    - If a handler argument was provided as a non-list (including tuples or other iterables), it will be wrapped as a single element in a list — only instances of the list type are left unwrapped.

## Side Effects:
    - Mutates the instance by assigning self.app, self.on_startup, and self.on_shutdown.
    - No I/O, no external service calls, and no global state mutation occurs in this method.

### `datasette.utils.asgi.AsgiLifespan.__call__` · *method*

## Summary:
Handles ASGI calls for lifespan and non-lifespan scopes: on lifespan scopes it listens for startup/shutdown messages, runs configured lifecycle callables, sends the corresponding ".complete" messages, and returns on shutdown; for other scopes it delegates to the wrapped ASGI application. This method therefore coordinates the object's startup/shutdown actions without mutating AsgiLifespan's own attributes.

## Description:
This coroutine is the ASGI application entrypoint provided by the AsgiLifespan wrapper. It is invoked by an ASGI server/framework (e.g., uvicorn, hypercorn) or any ASGI dispatcher when an incoming connection or lifecycle event is routed to this application object.

Known callers and invocation context:
- An ASGI server calls the application object with a scope, receive, and send following the ASGI spec. When the server is negotiating application lifespan events it will call this object with a scope whose "type" is "lifespan".
- For normal HTTP/WebSocket/etc. requests (scope["type"] != "lifespan"), the server calls this same application object and this method simply forwards the call to the wrapped ASGI app.

Why this logic is a separate method:
- ASGI requires the application to be an awaitable callable. Implementing lifecycle handling here keeps lifespan protocol handling localized and cleanly separates lifecycle event processing (startup/shutdown sequences) from request handling implemented by the wrapped app. It allows injection of startup/shutdown callables without changing the wrapped application's behavior.

## Args:
    scope (dict): ASGI scope mapping. Must include a "type" key (e.g., "lifespan", "http", "websocket").
    receive (Callable[[], Awaitable[dict]]): awaitable callable that yields ASGI event messages (dicts). Messages expected for lifespan handling include {"type": "lifespan.startup"} and {"type": "lifespan.shutdown"}.
    send (Callable[[dict], Awaitable[None]]): awaitable callable used to send ASGI event messages back to the server. This method will send {"type": "lifespan.startup.complete"} and {"type": "lifespan.shutdown.complete"} in response to lifecycle events.

## Returns:
    None
    - For lifespan shutdown: the coroutine returns (exits) after sending the shutdown complete message.
    - For non-lifespan scopes: returns whatever the delegated wrapped ASGI app returns (typically None for ASGI apps).

## Raises:
    - Any exception raised by the awaited lifecycle callables in self.on_startup or self.on_shutdown will propagate out of this method and prevent the corresponding ".complete" message from being sent.
    - Any exception raised by receive or send (e.g., connection errors or invalid messages) will propagate.
    - Any exception raised by awaiting self.app(scope, receive, send) for non-lifespan scopes will propagate.
    - If on_startup/on_shutdown contain non-awaitable objects (e.g., normal functions that do not return an awaitable), awaiting them will raise a TypeError/RuntimeError which will propagate.

## State Changes:
Attributes READ:
    - self.on_startup: iterated to call startup handlers
    - self.on_shutdown: iterated to call shutdown handlers
    - self.app: delegated to for non-lifespan scopes

Attributes WRITTEN:
    - None (this method does not assign to any self.<attr> fields)

## Constraints:
Preconditions:
    - scope must be a mapping containing a "type" key.
    - receive must be an awaitable callable compatible with ASGI semantics (returns dict messages).
    - send must be an awaitable callable compatible with ASGI semantics (accepts dict messages).
    - self.on_startup and self.on_shutdown should be iterables (lists) of callables that return awaitables when called (i.e., async functions or callables returning awaitables). The class initializer ensures they are lists but does not enforce callable/awaitable types.

Postconditions:
    - If handling a "lifespan.startup" message and all startup handlers complete successfully, the method will have awaited every function in self.on_startup and will have called send with {"type": "lifespan.startup.complete"}.
    - If handling a "lifespan.shutdown" message and all shutdown handlers complete successfully, the method will have awaited every function in self.on_shutdown, will have called send with {"type": "lifespan.shutdown.complete"}, and will have returned (terminating lifespan handling).
    - For non-lifespan scopes, the wrapped application will have been awaited; control returns after that await completes.

## Side Effects:
    - I/O via the ASGI protocol: calls to receive() to get lifecycle messages and calls to send({...}) to emit lifecycle complete messages.
    - Execution of user-provided startup/shutdown callables which may perform arbitrary side effects (database connections, file I/O, logging, etc.). Any such external effects originate from those callables.
    - Delegation to self.app(scope, receive, send) for non-lifespan scopes which may perform network I/O, database access, and mutate external resources.
    - Early termination behavior: after processing a "lifespan.shutdown" message the method returns, which signals the ASGI server that the lifespan handler has finished.

## `datasette.utils.asgi.AsgiStream` · *class*

## Summary:
Represents an ASGI-streaming response wrapper: encapsulates an async streaming function and provides an asgi_send(send) method that emits the initial http.response.start event, invokes the provided streaming coroutine with an AsgiWriter, and finalizes the response.

## Description:
AsgiStream is used when an HTTP ASGI handler needs to stream a response body produced by an async coroutine. The caller constructs an AsgiStream with a stream function (typically an async def that accepts a writer) and optional response metadata (status, headers, content_type). The ASGI application should call await AsgiStream.asgi_send(send) inside an HTTP request scope, passing the ASGI send callable.

Typical callers/factories:
- An async ASGI HTTP request handler that wants to stream generated content (for example, CSV rows, server-sent events, or chunked text output).
- Higher-level helpers that produce streaming responses and hand an AsgiStream instance to ASGI middleware or frameworks.

Responsibility boundary and motivation:
- AsgiStream centralizes the logic of sending the initial http.response.start event (status and headers) and of coordinating the streaming coroutine with a small writer abstraction (AsgiWriter).
- It is not responsible for producing chunks itself (the stream_fn does that), nor for handling final error recovery: exceptions raised by the stream coroutine or the send callable propagate to the caller.

## State:
Attributes set by __init__ (public):
- stream_fn: Callable[[writer], Awaitable[None]]
    - The coroutine function that is called to perform streaming. Expected signature: async def stream_fn(writer): ...
    - Constraint: when called as await stream_fn(writer) it must return/complete without returning a non-awaitable value. The function is responsible for writing chunks using the supplied writer.
    - Invariant: remains callable and produces an awaitable when invoked with one argument.
- status: int
    - HTTP status code to send in the initial http.response.start event.
    - Typical valid range: 100–599 (not enforced by the class).
- headers: dict[str, str]
    - Mapping of header name -> header value. If None is provided to __init__, an empty dict is used.
    - Header names and values should be str; they will be UTF-8 encoded when sent. Any header whose name lowercased is "content-type" will be dropped here and replaced by content_type attribute.
- content_type: str
    - Value used for the Content-Type response header. Defaults to "text/plain".
    - Always used to set the outgoing "content-type" header regardless of whether headers contained their own content-type.

Class invariants:
- After initialization and before asgi_send is called, attributes do not change unless mutated by the caller.
- asgi_send always sends the content-type header derived from content_type attribute; any "content-type" in headers is ignored.
- asgi_send expects to be executed in an ASGI HTTP request scope where the provided send callable is valid and awaitable.

## Lifecycle:
Creation:
- Instantiate with required argument stream_fn and optional status, headers, content_type:
    - AsgiStream(stream_fn, status=200, headers=None, content_type="text/plain")
- stream_fn must be a callable that accepts one positional argument (writer) and returns an awaitable when called.

Usage:
- Typical sequence inside an ASGI HTTP handler:
    1. Create the AsgiStream instance with the streaming coroutine.
    2. Call and await await asgi_stream.asgi_send(send) where send is the ASGI-provided send callable.
    3. asgi_send will:
        - Prepare headers by copying self.headers and removing any header whose lowercased name equals "content-type".
        - Insert the "content-type" header with the value of self.content_type.
        - Send an ASGI "http.response.start" event with the status and headers (each header name and value encoded to UTF-8 bytes).
        - Instantiate an AsgiWriter(send) and await the stream function via await self.stream_fn(writer). The stream function should repeatedly await writer.write(chunk) to emit body frames (AsgiWriter sends frames with more_body=True).
        - After the streaming function completes, asgi_send sends a final http.response.body event with body set to b"" (no explicit more_body flag, which implies the final frame / more_body=False).
- Required sequencing:
    - asgi_send must be awaited in an async context and should only be invoked once per instance (typical).
    - The stream_fn must not itself attempt to send the initial http.response.start event; that is already done by asgi_send. If the stream_fn attempts to send start, ASGI servers may raise errors or behavior is undefined.

Destruction / cleanup:
- No explicit cleanup or close method. The finalization of the HTTP response is performed by asgi_send when it sends the final empty body message after the stream coroutine returns.
- Any resources produced by the stream_fn (files, sockets) must be closed by stream_fn or its callers.

## Method Map:
flowchart TD
    A[Call asgi_stream.asgi_send(send)] --> B[Build headers, set content-type from content_type]
    B --> C[await send({"type":"http.response.start","status":status,"headers":[[name, value]]})]
    C --> D[Create AsgiWriter(send)]
    D --> E[await stream_fn(writer)] 
    E --> F[AsgiWriter.write(...) called repeatedly by stream_fn -> sends http.response.body frames with more_body=True]
    E --> G[When stream_fn completes] --> H[send({"type":"http.response.body","body": b""}) finalizes response]

## Raises:
- __init__:
    - Does not raise any explicit exceptions. No validation is performed on types or ranges.
- asgi_send(send):
    - TypeError / AttributeError: if header names/values are not str, encoding to UTF-8 will raise when building the bytes list.
    - TypeError: if the passed send is not an awaitable-capable callable, awaiting send(...) will raise when asgi_send attempts to call it.
    - Any exception raised by stream_fn will propagate out of asgi_send (e.g., runtime errors inside the stream function).
    - Any exception raised by the send callable (network/ASGI server errors) propagates unchanged.
    - Note: Because the initial http.response.start is sent before invoking stream_fn, exceptions during streaming leave a partially-started response; callers should consider try/except around asgi_send in the request handler to perform logging or cleanup, but cannot unsend a started response.

## Example:
- Streaming an async sequence of text lines:
    1. Define the stream coroutine:
        async def my_stream(writer):
            for line in ["row1\n", "row2\n", "row3\n"]:
                await writer.write(line)
    2. Create and send in an ASGI HTTP handler:
        asgi_stream = AsgiStream(my_stream, status=200, headers={"X-Name": "value"}, content_type="text/plain; charset=utf-8")
        await asgi_stream.asgi_send(send)
    3. Behavior:
        - asgi_send sends http.response.start with status and headers (Content-Type set from content_type).
        - my_stream is awaited and uses the supplied AsgiWriter to send body frames (each with more_body=True).
        - When my_stream returns, asgi_send sends a final http.response.body with an empty body to indicate completion.

Notes and constraints:
- stream_fn must be an async callable (coroutine function) that accepts a single parameter (writer). If a non-async function is supplied, asgi_send will attempt to await its return and will raise.
- Header names and values must be str and will be UTF-8 encoded. Any header whose name lowercased equals "content-type" is ignored in favor of content_type.
- The final body frame sent by asgi_send does not include an explicit more_body key; per ASGI semantics this signals the end of the response.

### `datasette.utils.asgi.AsgiStream.__init__` · *method*

## Summary:
Initialize the AsgiStream instance by storing the provided streaming coroutine and response metadata (status, headers, content_type) on the object so subsequent asgi_send can use them to start and stream an HTTP response.

## Description:
- Known callers / call sites:
  - ASGI HTTP request handlers or helper factories that want to return a streaming response to the ASGI server.
  - Higher-level utilities that build an AsgiStream to hand off to ASGI middleware or application code.
- Lifecycle stage:
  - Called at creation time when preparing a streaming response object; the returned instance is later used by asgi_send to send the initial response headers and invoke the stream function to emit body frames.
- Why this is a separate initializer:
  - Centralizes and documents the required response metadata and streaming coroutine reference in one place.
  - Keeps the storage of state (stream function and response metadata) separated from the streaming/send logic implemented in asgi_send, enabling callers to construct the object before entering the ASGI send lifecycle or to mutate metadata if needed prior to sending.

## Args:
    stream_fn (callable): Required. An async callable that accepts a single argument (a writer) and returns an awaitable. Expected signature: async def stream_fn(writer): ...
        - Usage constraint: when invoked as await stream_fn(writer) it must perform streaming by calling writer.write(...) and then complete. Supplying a non-async function will cause awaiting it later to raise.
    status (int, optional): HTTP status code to send in the initial response. Defaults to 200.
        - Typical valid values: 100–599 (not validated here).
    headers (dict[str, str] | None, optional): Mapping of header name to header value. Defaults to None, which becomes an empty dict at initialization.
        - Expected types: str keys and str values. No validation is performed; non-str values will cause errors later when encoding headers for ASGI.
    content_type (str, optional): Value used for the Content-Type response header. Defaults to "text/plain".
        - This value will be relied upon by asgi_send to set the outgoing Content-Type header (it overrides any content-type present in headers at send time).

## Returns:
    None

## Raises:
    - None explicitly from __init__. (No type or value validation is performed here.)
    - Note: problems from incorrect argument types (e.g., non-callable stream_fn or non-dict headers) are not raised during initialization but will surface later when asgi_send attempts to call or encode them.

## State Changes:
- Attributes READ:
    - None on self (constructor reads only the provided arguments).
- Attributes WRITTEN:
    - self.stream_fn: set to the provided stream_fn argument.
    - self.status: set to the provided status argument.
    - self.headers: set to the provided headers argument or an empty dict if headers is None.
    - self.content_type: set to the provided content_type argument.

## Constraints:
- Preconditions:
    - Caller should supply a stream_fn that is an async callable accepting one argument (writer) and returning an awaitable.
    - If provided, headers should be a mapping of strings to strings (header names and values).
    - status should be an integer representing an HTTP status code.
- Postconditions:
    - The instance has stream_fn, status, headers, and content_type attributes populated.
    - headers is never None after initialization (it will be {} if caller passed None).
    - No normalization of header names or validation of values is performed here; that responsibility occurs at send time.

## Side Effects:
- No I/O or external calls are performed.
- No mutation of objects outside self except for storing references to the passed-in objects (the passed headers dict is not copied; callers who mutate that dict after initialization will affect the stored headers reference).

### `datasette.utils.asgi.AsgiStream.asgi_send` · *method*

## Summary:
Starts an ASGI HTTP response using the object's status and headers, streams the response body by invoking the stored stream function with an AsgiWriter wrapper, and then sends the final empty body frame to complete the response. This mutates no AsgiStream attributes but produces ASGI messages via the provided send callable.

## Description:
This coroutine is the runtime step that converts an AsgiStream instance into actual ASGI protocol messages delivered to the server/framework via the provided send callable.

- Known callers / invocation context:
    - Typically invoked by an ASGI HTTP handler or framework once an AsgiStream has been created (for example, by code that wants to return a streaming response). The handler passes the ASGI send callable it received from the server into this method.
    - Lifecycle stage: called when the application is ready to start sending the HTTP response (headers) and stream the body. It performs the "response start" step, runs the streaming producer, and then finalizes the response.

- Why this is a separate method:
    - Encapsulates three logically distinct responsibilities that belong together at send-time: emit the initial http.response.start event (status + headers), adapt the ASGI send callable into a simple writer and run the user-supplied streaming coroutine, and send the terminal http.response.body frame.
    - Keeps header handling and ASGI framing centralized (so stream_fn can focus on producing chunks via the AsgiWriter abstraction).

## Args:
    send (Callable[[dict], Awaitable[None]]):
        The ASGI "send" callable supplied by the ASGI server/framework. It must be awaitable and accept a single dict representing an ASGI event. Example shape:
            await send({"type": "http.response.start", "status": ..., "headers": [...]})
        Preconditions on send:
            - Awaiting send(event) should deliver the event to the ASGI server.
            - The method relies on send to accept the event dictionaries used below.

## Returns:
    None
    - This is an async coroutine that returns None when complete. Completion indicates the method has sent the response start event, invoked the stream function to produce body chunks, and sent the final empty body frame.

## Raises:
    - Any exception raised by the provided send callable is propagated unchanged.
    - Any exception raised by self.stream_fn (including TypeError, RuntimeError, etc.) is propagated unchanged.
    - If header keys or values in self.headers are not text-like objects supporting .encode("utf-8"), calling .encode will raise AttributeError/TypeError; such exceptions propagate out of this method.
    - If send is not awaitable or not callable, awaiting send(...) will raise TypeError when the method attempts to await it.

## State Changes:
- Attributes READ:
    - self.headers (dict-like): read to construct the headers list; content-type entries are filtered out.
    - self.content_type (str): read and inserted as the "content-type" header (overrides any existing content-type).
    - self.status (int): read and used as the HTTP status code in the http.response.start event.
    - self.stream_fn (Callable[[AsgiWriter], Awaitable[None]]): read and awaited to perform streaming writes. Expected to accept a writer (AsgiWriter) and be an awaitable coroutine.

- Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
- Preconditions:
    - self.headers must be an iterable of (key, value) pairs (e.g., a dict) where keys and values are text-like objects (commonly strings). The code filters headers by comparing key.lower() to "content-type" and then calls .encode("utf-8") on both key and value.
    - self.content_type must be a text-like value to be used as the "content-type" header value.
    - self.status must be an integer HTTP status code (e.g., 200, 404).
    - self.stream_fn must be an async callable that accepts a single argument (the AsgiWriter instance) and performs awaited writes on it.
    - send must be an awaitable-capable callable provided by the ASGI server.

- Postconditions (guarantees after successful return):
    - An ASGI http.response.start event has been sent with:
        - "status": self.status
        - "headers": a list of [key_bytes, value_bytes] pairs derived from self.headers with any existing content-type removed and a "content-type" header set to self.content_type. Keys and values are encoded using UTF-8 before being sent.
    - The user-supplied stream function (self.stream_fn) has been awaited with an AsgiWriter wrapping the provided send callable; any body chunks produced by stream_fn via the writer will have been sent (as sent by AsgiWriter).
    - A final ASGI http.response.body event with an empty body ({"type":"http.response.body","body": b""}) has been sent to indicate response completion (no more_body field is included).

## Side Effects:
- I/O / external interactions:
    - Calls await send(...) multiple times to deliver ASGI events. These are the primary external effects:
        1. http.response.start with encoded headers and status.
        2. Zero or more http.response.body events sent indirectly via AsgiWriter when self.stream_fn writes chunks.
        3. A final http.response.body event with body b"" to finalize the response.
    - The actual network transmission is performed by the ASGI server implementing the send callable; this method merely constructs and forwards the protocol messages.

- Mutations outside self:
    - None directly performed on external Python objects by this method itself (it does create an AsgiWriter instance and calls into self.stream_fn which may mutate external state or perform I/O).
    - Any side effects produced by self.stream_fn (database access, file I/O, further sends, logging, etc.) occur as part of the awaited stream_fn call and will propagate out as usual.

## Implementation notes / behavior details:
- Header handling:
    - Existing headers from self.headers are preserved except any header whose name lowercased equals "content-type" is removed.
    - The content-type header is set to the value of self.content_type (string) and included in the headers list.
    - When sending, header names and values are encoded to UTF-8 bytes and packaged as a list of two-element byte lists as required by ASGI.
- Streaming:
    - This method delegates chunk-level framing to AsgiWriter: it constructs AsgiWriter(send) and passes it into self.stream_fn(w). The stream function is expected to call w.write(chunk) (and await it) for each textual chunk.
    - After stream_fn completes, this method sends a final http.response.body message with body b"" to indicate completion.
- Errors in stream_fn or send will abort the method and propagate to the caller; callers should handle errors and ensure appropriate cleanup if required.

## `datasette.utils.asgi.AsgiWriter` · *class*

## Summary:
An ultra-lightweight helper that adapts an ASGI send callable into a simple writer interface exposing an async write(chunk: str) method which sends http.response.body ASGI messages with UTF-8 encoding and streaming semantics.

## Description:
AsgiWriter wraps the ASGI "send" callable provided to HTTP ASGI applications so other parts of the code can write streamed response chunks without constructing ASGI message dictionaries each time. Instantiate AsgiWriter inside an ASGI scope (for example inside an HTTP request handler) using the send callable that the ASGI server/framework passes to your application. Its responsibility is deliberately narrow: encode text chunks as UTF-8 and send them as http.response.body frames with more_body set to True to indicate streaming continues.

Typical scenarios:
- You have an async HTTP handler that receives (scope, receive, send) and you want a simple writer abstraction to stream textual response chunks.
- Libraries or utilities in the request handling path want to output partial text responses without dealing with ASGI message formatting.

Known caller/factory:
- Any ASGI HTTP handler which has access to the ASGI send callable can instantiate AsgiWriter(send).
- There are no hidden factories in this module; callers create AsgiWriter directly with the send callable.

Motivation / responsibility boundary:
- Provides a concise abstraction for sending text response chunks over ASGI.
- It is not responsible for setting headers, sending the initial http.response.start message, managing finalization of the response (closing frame with more_body=False), or converting non-text payloads. Those responsibilities remain with the caller.

## State:
Attributes (public):
- send: Callable[[dict], Awaitable[None]]
    - The ASGI send callable provided by the server/framework.
    - Expected to be an async callable that accepts a single mapping representing an ASGI event (a dict).
    - Invariant: self.send must remain a callable that can be awaited with a single dict argument. The class relies on this when write() is awaited.

No additional internal attributes or buffers are maintained by AsgiWriter.

__init__ parameters:
- send (required): An awaitable-capable callable that accepts one dict argument representing an ASGI event. No default. The caller must provide it.

Class invariants:
- After initialization, self.send is assumed to be usable with await self.send(message). Methods will fail if that invariant is violated (e.g., if send is not awaitable or not callable).

## Lifecycle:
Creation:
- Instantiate by passing the ASGI send callable:
  - Required argument: send.
  - No other initialization steps are performed.

Usage:
- Primary operation is the async write(chunk) method.
- write(chunk) must be awaited by the caller in an async context.
- Expected sequence in a streaming HTTP response:
    1. Caller (or framework) sends an initial http.response.start event (not handled by this class).
    2. Create AsgiWriter with the ASGI send callable.
    3. Repeatedly call and await writer.write(chunk) for each textual chunk to stream. Each call sends one http.response.body message with more_body=True.
    4. When streaming is complete, caller must send a final http.response.body message with more_body=False itself (AsgiWriter does not provide this).
- There is no close() or context manager on AsgiWriter. It does not manage lifecycle completion of the ASGI response.

Destruction / cleanup:
- No internal resources to release. The caller is responsible for sending the terminal ASGI body frame (more_body=False) and for any other cleanup.

## Method Map:
flowchart TD
    A[Instantiate AsgiWriter(send)] --> B[await write(chunk) ... repeated]
    B --> C[ASGI send called with {'type':'http.response.body','body':chunk_bytes,'more_body':True}]
    C --> B
    Note[Caller must send final http.response.body with more_body=False when complete]

(This diagram shows the primary control flow: create writer, call write repeatedly — each call awaits send sending a streaming body frame — and finalization is external.)

## Methods (behavioral details)
- __init__(self, send)
    - Inputs:
        - send: an awaitable-capable callable accepting a single dict representing an ASGI event.
    - Behavior:
        - Stores the provided send callable on self.send. No other work is performed.
    - Side effects: none.
    - Constraints for caller: send must be usable with await send(message) where message is a dict.

- async write(self, chunk)
    - Inputs:
        - chunk (str): A text string to be sent as one ASGI http.response.body frame.
    - Behavior:
        - Encodes chunk to UTF-8 bytes using chunk.encode("utf-8").
        - Awaits self.send(...) with a dictionary:
            {
                "type": "http.response.body",
                "body": <encoded bytes>,
                "more_body": True
            }
        - This indicates to the ASGI server that the response body continues (streaming).
    - Output: None (returns None). The method must be awaited.
    - Edge cases and constraints:
        - chunk must be a str. If a non-str (e.g., bytes) is passed, chunk.encode will either be absent or behave unexpectedly and will raise an AttributeError or TypeError; callers should ensure they pass str.
        - If self.send is not an awaitable callable, awaiting it will raise a Python TypeError at runtime.
        - This method does not send the final frame (more_body=False) — caller must do that explicitly when stream completes.
    - Side effects:
        - Causes an ASGI event to be sent via the underlying send callable.

## Raises:
- __init__: The constructor itself does not explicitly raise exceptions. However, if a non-callable is passed for send, attempts to await it later in write will raise TypeError when write is used.
- write:
    - AttributeError or TypeError if chunk is not a str and does not support encode("utf-8").
    - TypeError if self.send is not an awaitable callable (raised when awaiting self.send).
    - Any exceptions raised by the provided send callable propagate to the caller unchanged.

## Example (prose):
1. In an async HTTP request handler you receive a send callable from the ASGI server.
2. Instantiate AsgiWriter by passing that send callable.
3. Ensure you have already sent an http.response.start event (headers and status).
4. To stream response text, repeatedly call and await writer.write(...) with string chunks; each call will send a body frame marked more_body=True.
5. When all chunks have been sent, the handler should send one final http.response.body event with an empty (or final) body and more_body set to False to indicate the response is complete.

This pattern allows other utilities to focus on producing textual chunks and delegate the ASGI framing to AsgiWriter.

### `datasette.utils.asgi.AsgiWriter.__init__` · *method*

## Summary:
Assign the provided ASGI send callable to the instance so other AsgiWriter methods can use it to send ASGI events.

## Description:
Called when constructing an AsgiWriter instance (typically inside an ASGI HTTP handler that receives a send callable from the ASGI server). This method's sole responsibility is to record the provided callable on the instance; it intentionally does not perform validation or other setup. Keeping this logic in its own method separates simple state initialization from the streaming behavior implemented by other methods (for example, write).

Known callers / context:
- Created by HTTP ASGI handlers or utilities that receive the ASGI send callable and want a lightweight writer abstraction.
- Invocation happens during the request handling setup phase when the handler constructs helper objects.

## Args:
    send (Callable[[dict], Awaitable[None]]):
        The ASGI send callable provided by the ASGI server/framework. Expected usage: awaiting it with a single dict argument representing an ASGI event (e.g., await send(message)).
        - Required; no default.
        - The constructor does not validate the callable or its signature.

## Returns:
    None
    - Standard constructor behavior; no return value.

## Raises:
    None explicitly.
    - The constructor does not raise. If a non-callable is provided, or the provided callable is not awaitable, errors will occur only later when other methods attempt to await self.send.

## State Changes:
    Attributes READ:
        - None.
    Attributes WRITTEN:
        - self.send: set to the value of the send argument (stored as-is).

## Constraints:
    Preconditions:
        - Caller must supply the send argument. For correct operation of other AsgiWriter methods, that object should be an awaitable-capable callable accepting one dict argument, but this constructor does not enforce that.
    Postconditions:
        - After __init__ returns, self.send references the provided object exactly as passed in.

## Side Effects:
    - Mutates the instance by assigning to self.send.
    - No I/O, no network calls, no validation, and no allocation of external resources.

### `datasette.utils.asgi.AsgiWriter.write` · *method*

## Summary:
Awaits the stored ASGI send callable to transmit the given text chunk as a UTF-8 encoded bytes payload in an "http.response.body" message, leaving the response open (more_body=True).

## Description:
This async method encapsulates sending one piece of a streaming HTTP response over ASGI. It formats the ASGI message and awaits the send callable that was stored on the AsgiWriter instance at construction time.

Known callers and lifecycle:
- Called by streaming HTTP response code during the response-writing stage, after any "http.response.start" message has been sent and while additional body chunks are expected.
- Typical usage: a handler/streamer obtains an AsgiWriter and repeatedly awaits write(chunk) for each generated text chunk. After all chunks have been sent, the caller must send a final ASGI message with "more_body": False (this method does not do that).

Why this is a separate method:
- Centralizes ASGI message construction (message type, encoding, and more_body flag) and the required awaiting of the send callable, keeping streaming callers simple and consistent.

## Args:
    chunk (str): The text to send. Must be a str instance; the method calls chunk.encode("utf-8") to produce bytes. Passing non-str values (including None or bytes) that lack a compatible encode method will raise an exception.

## Returns:
    None: This coroutine returns None after the underlying send coroutine completes.

## Raises:
    AttributeError: If chunk does not have an encode method (e.g., None or many non-string objects), the attempt to call chunk.encode("utf-8") will raise AttributeError.
    UnicodeEncodeError: If UTF-8 encoding of the given string fails (rare for valid Python str), the exception is propagated.
    Any exception raised by the underlying ASGI send callable: errors from awaiting self.send(...) (such as connection closed errors, framework-specific exceptions, or cancellation) are propagated to the caller.

## State Changes:
    Attributes READ:
        self.send - the async callable provided to AsgiWriter.__init__ that is invoked to transmit ASGI messages.
    Attributes WRITTEN:
        None - this method does not modify attributes on self.

## Constraints:
    Preconditions:
        - The AsgiWriter instance must have a callable attribute send that is awaitable and accepts a single ASGI message dict.
        - chunk must be a str so that chunk.encode("utf-8") yields bytes.
    Postconditions:
        - The ASGI send callable has been awaited with a mapping exactly:
            {"type": "http.response.body", "body": <bytes>, "more_body": True}
          where <bytes> == chunk.encode("utf-8").
        - The response remains open from the ASGI perspective (more_body=True). The caller is responsible for sending the final message with "more_body": False when the stream is complete.

## Side Effects:
    - Performs I/O via awaiting the ASGI send callable; this causes the ASGI server/framework to transmit the provided bytes to the client.
    - No other external state or object mutations are performed by this method.

## `datasette.utils.asgi.asgi_send_json` · *function*

## Summary:
Send a JSON-serializable Python object as an HTTP JSON response over an ASGI connection, encoding it as UTF-8 and setting the response Content-Type to "application/json; charset=utf-8".

## Description:
This coroutine takes a JSON-serializable Python object, serializes it to a JSON string, and delegates the protocol-level sending to the underlying asgi_send helper which emits the ASGI http.response.start and http.response.body events.

Known callers within the codebase:
- No concrete callers were discovered in the provided repository snapshot for this specific function. Typical invocation sites in an ASGI application are:
    - ASGI request handlers or view functions that want to return API responses and therefore need a simple way to send JSON back to the client.
    - Higher-level response helpers that produce a JSON payload after assembling data from the application/database.

Typical invocation context:
- Called when the full response body is available (non-streaming) and the application wishes to return JSON. The caller provides the ASGI send callable (supplied by the ASGI server) and the Python object to serialize and send.

Why this logic is a dedicated function:
- Encapsulates JSON serialization and the correct JSON Content-Type header in one small, reusable helper.
- Keeps callers free from manually calling json.dumps and remembering the correct content-type header value.
- Delegates ASGI framing and byte-encoding to asgi_send so this function focuses on the JSON-specific contract.

## Args:
    send (Callable[[dict], Awaitable[None]]):
        The ASGI send callable supplied by the ASGI server/framework. It must be awaitable and accept a single dict describing an ASGI event. No default; required.
    info (Any):
        Any JSON-serializable Python object (e.g., dict, list, str, number, bool, None) which will be passed to json.dumps(). Must be serializable by the standard json library.
    status (int, optional):
        HTTP status code to send with the response. Defaults to 200. The function does not validate the integer; invalid values may cause downstream errors when the ASGI server processes the event.
    headers (Optional[Mapping[str, str] or Iterable[tuple[str,str]]], optional):
        Optional headers to include in the response. If None, an empty mapping is used. Values are forwarded to asgi_send which will incorporate them into the ASGI http.response.start event. Keys and values should be strings; non-text values may cause encoding errors later.

Notes on parameter interdependencies:
- info must be JSON-serializable by json.dumps; otherwise serialization will fail before asgi_send is invoked.
- headers should be in a form acceptable to asgi_send (string keys/values or iterable of (name, value) pairs).

## Returns:
    None
    - The coroutine returns None after awaiting the underlying asgi_send coroutine.
    - There are no alternate return values.

## Raises:
    TypeError:
        - Raised by json.dumps(info) if info contains objects not serializable by the standard json encoder (this is the most common failure mode).
        - Or raised if send is not awaitable/callable when awaiting asgi_send triggers the send call.
    Any exception propagated from asgi_send or from the ASGI send callable:
        - asgi_send may raise AttributeError/TypeError if provided headers or the content cannot be encoded to bytes as expected.
        - Any exceptions raised by the underlying ASGI transport (network/IO errors) will propagate unchanged.
    ValueError / other exceptions:
        - Possible if downstream code (asgi_start/asgi_send) performs checks that fail; such exceptions are not explicitly raised here but will propagate.

## Constraints:
Preconditions:
    - send must be the ASGI send callable (awaitable callable accepting a single dict).
    - info must be serializable by json.dumps using the standard library encoder (no custom encoder is used here).
    - status should be an integer HTTP status code (the function does not validate it).
    - headers (if provided) should contain string names and values suitable for header encoding.

Postconditions:
    - The underlying asgi_send coroutine will have been awaited with:
        - content equal to json.dumps(info) (a str),
        - status equal to the provided status,
        - headers forwarded as provided (or an empty mapping),
        - content_type set to "application/json; charset=utf-8".
    - After successful return, the ASGI events corresponding to the response start and the single-chunk response body have been emitted (via the send callable) and no further action is required to complete the response.

## Side Effects:
    - Network/transport I/O: awaiting asgi_send(send, ...) ultimately calls the provided send callable which leads to ASGI events being delivered to the server and network I/O performed by the server implementation.
    - CPU / memory: json.dumps(info) serializes the entire info object into a string in memory (not streaming); this may be significant for large payloads.
    - No file system or global state is modified by this function itself. Side effects from asgi_send or the ASGI server (logging, metrics, network writes) may occur.

## Control Flow:
flowchart TD
    Start --> NormalizeHeaders
    NormalizeHeaders --> JSONSerialize
    JSONSerialize --> json_ok{json.dumps succeeded?}
    json_ok -- No --> Propagate_json_error
    json_ok -- Yes --> Call_asgi_send
    Call_asgi_send --> asgi_send_ok{asgi_send awaited successfully?}
    asgi_send_ok -- No --> Propagate_asgi_error
    asgi_send_ok -- Yes --> Return
    Propagate_json_error --> End
    Propagate_asgi_error --> End

- NormalizeHeaders: headers = headers or {} (ensures a mapping is forwarded).
- JSONSerialize: content = json.dumps(info).
- Call_asgi_send: await asgi_send(send, content, status=status, headers=headers, content_type="application/json; charset=utf-8").

## Examples:
Example — simple JSON response from an ASGI app handler:

    async def app(scope, receive, send):
        # ... build some data to return ...
        data = {"success": True, "items": [1, 2, 3]}
        await asgi_send_json(send, data, status=200)

Example — include custom headers and handle serialization errors:

    async def handler(scope, receive, send):
        payload = {"time": datetime.now()}  # datetime is not JSON-serializable by default
        try:
            await asgi_send_json(send, payload, status=200, headers={"x-source": "example"})
        except TypeError:
            # Serialization failure: fall back to a safe representation
            safe_payload = {"error": "non-serializable payload"}
            await asgi_send_json(send, safe_payload, status=500)

Example — defensive handling of ASGI/send failures:

    try:
        await asgi_send_json(send, {"ok": True})
    except Exception as e:
        # Could be network/transport error during send or encoding error.
        logger.exception("Failed to send JSON response: %s", e)

## `datasette.utils.asgi.asgi_send_html` · *function*

## Summary:
Send a complete HTML response over ASGI: ensure headers are set and transmit the HTML body encoded as UTF-8 with the HTML content-type.

## Description:
Sends an HTTP response whose body is the provided HTML text. This coroutine normalizes the optional headers argument, then delegates the low-level ASGI framing and body emission to the generic asgi_send helper, forcing the response content type to "text/html; charset=utf-8".

Known callers within the codebase and typical invocation context:
- No single concrete callers were discovered in the provided snapshot. Typical callers are ASGI application handlers or higher-level response helpers that have rendered an HTML template and need to return it to the client (for example, a view or route handler that returns a rendered page). Invocation typically happens at the end of a request handler when the full HTML payload is available and streaming is unnecessary.

Why this logic is extracted into a separate function:
- Encapsulates the common pattern of sending small/complete HTML responses so callers do not need to repeat content-type setting and asgi_send invocation.
- Provides a concise, intention-revealing API for sending HTML (type safety: enforces the HTML content type), keeping content-encoding and ASGI framing details inside asgi_send.

## Args:
    send (Callable[[dict], Awaitable[None]]):
        The ASGI send callable provided by the server/framework. Must be awaitable and accept a single dict representing an ASGI event (the function will await asgi_send which will await send).
    html (str):
        The HTML payload as a Python str. It will be encoded to UTF-8 by the underlying asgi_send call. Passing a non-str will result in an AttributeError when encoding is attempted.
    status (int, optional):
        HTTP status code to send (e.g., 200, 404). Defaults to 200.
    headers (optional, mapping or iterable of (name, value) pairs):
        Additional headers to include in the response. If None, an empty mapping is used. Any "content-type" header provided here will be effectively overridden by the function's enforced content type ("text/html; charset=utf-8") because the underlying asgi_start/asgi_send logic ensures the content-type is set to the content_type argument.

Notes on parameter interdependencies:
- html must be a str because asgi_send will call .encode("utf-8") on it.
- headers may be any structure accepted by the asgi_send/asgi_start helper (commonly a dict or iterable of (name, value) pairs where names and values are text-like).

## Returns:
    None
    - The coroutine returns None after the underlying asgi_send has awaited the ASGI "http.response.start" and "http.response.body" events and the bytes body has been sent.
    - There are no alternate return values.

## Raises:
    AttributeError:
        - If html is not a str (for example, bytes or an object without .encode) the attempt to encode will raise an AttributeError; this will propagate from the underlying asgi_send.
    TypeError (or related awaitable/callable errors):
        - If send is not callable/awaitable according to the ASGI contract, awaiting send(...) (performed inside asgi_send) will raise a TypeError or similar; such exceptions propagate.
    Any exception raised by the underlying asgi_send or the ASGI send callable:
        - Any exceptions thrown by asgi_send, asgi_start, or the send callable (e.g., transport errors, header-encoding errors) will propagate unchanged.

## Constraints:
Preconditions:
    - send must be a valid ASGI send callable (awaitable, accepts a single event dict).
    - html must be a Python str containing the HTML text to transmit.
    - status should be an integer HTTP status code.
    - headers (if provided) must be acceptable to the underlying asgi_start/asgi_send helpers (text-like keys and values).

Postconditions:
    - The underlying asgi_start/asgi_send will have been awaited and the client will have received:
        1) an ASGI http.response.start event with the supplied status and headers (with content-type set to "text/html; charset=utf-8"), and
        2) a single ASGI http.response.body event whose body is html encoded to UTF-8 bytes.
    - The provided headers argument is not mutated by this function (a new or default {} is passed through).

## Side Effects:
    - Network/transport: awaiting the send callable results in ASGI protocol messages being forwarded to the ASGI server which typically performs network I/O (http.response.start and http.response.body events).
    - Encoding: the html str is encoded to UTF-8 bytes before transmission.
    - No filesystem, database, or global state is modified by this function itself. Side effects may come from the ASGI server or other code that runs concurrently.

## Control Flow:
flowchart TD
    Start --> Normalize_headers
    Normalize_headers --> Call_asgi_send
    Call_asgi_send --> asgi_send_ok{asgi_send awaited successfully?}
    asgi_send_ok -- Yes --> Return
    asgi_send_ok -- No --> Propagate_error
    Propagate_error --> End

## Examples:
Example — sending a rendered HTML page from an ASGI handler:
    # assume `html_content` is a str produced by a template renderer
    await asgi_send_html(send, html_content, status=200, headers={"x-frame-options": "deny"})

Example — defensive handling when html may be non-text:
    try:
        await asgi_send_html(send, maybe_bytes_or_obj, status=200)
    except AttributeError:
        # html was not a str (no .encode); convert to text and retry or return error page
        safe_html = str(maybe_bytes_or_obj)
        await asgi_send_html(send, safe_html, status=500)
    except Exception as e:
        # send/asgi_start error: log and let framework handle the failure
        logger.exception("Failed to send HTML response: %s", e)

## `datasette.utils.asgi.asgi_send_redirect` · *function*

## Summary:
Send an HTTP redirect response over ASGI by emitting a response-start with a Location header and a single empty HTML body chunk (default status 302).

## Description:
This coroutine is a small convenience helper used at the point where an ASGI application or handler needs to redirect the client to another URL. It delegates the actual ASGI emission to the common asgi_send helper, supplying an empty text/html body and a Location header.

Known callers and typical invocation context:
- ASGI application handlers or framework request handlers that decide a redirect is required (for example, after login, logout, or when a resource has moved).
- Higher-level response helper code that wants a one-liner to send a redirect instead of constructing headers and body manually.
- Typical trigger: routing or business-logic that determines the client should be redirected and calls await asgi_send_redirect(send, location, status).

Why this logic is extracted:
- Encapsulates the common pattern of sending a Location header and an immediate response via asgi_send so callers don't need to build headers, choose content-type, or remember to send an empty body chunk.
- Keeps responsibility small and readable: the helper enforces consistent content_type ("text/html; charset=utf-8") and delegates protocol framing and encoding to asgi_send/asgi_start.

## Args:
    send (Callable[[dict], Awaitable[None]]):
        The ASGI send callable supplied by the ASGI server/framework. Must be awaitable and accept a single dict representing an ASGI event.
    location (str):
        The value to place in the HTTP Location header. Should be a URL or path (absolute or relative) encoded as a Python str. The value will be forwarded as the Location header and must be encodable to UTF-8.
    status (int, optional):
        HTTP status code to use for the redirect. Defaults to 302. Typical values are 301 (permanent) or 302 (temporary).

Note on interdependencies:
- The helper constructs headers={"Location": location} and relies on asgi_send/asgi_start to convert that mapping into properly encoded ASGI header bytes. Therefore location must be a text-like object acceptable to asgi_send/asgi_start.

## Returns:
    None
    - The coroutine returns None after awaiting asgi_send which sends the http.response.start and a single http.response.body event (empty body) to complete the response.

## Raises:
    Any exception raised by asgi_send or the provided send callable:
        - Transport/network errors raised while awaiting send.
        - Encoding errors if the Location value cannot be encoded to UTF-8 when asgi_send/asgi_start performs header encoding.
    Notes:
        - Because this helper passes a constant empty string as the body, it will not raise an AttributeError for body encoding itself (empty string is a valid str). Errors will generally come from header encoding or the send callable.

## Constraints:
Preconditions:
    - send must be an awaitable-capable callable following the ASGI send contract.
    - location must be a str (or other text-like object) that can be encoded to UTF-8 and is suitable for use in an HTTP Location header.
    - status must be an integer valid as an HTTP status code.

Postconditions:
    - An ASGI http.response.start event has been sent with the given status and a Location header set to the provided location (as processed by asgi_send/asgi_start).
    - A single http.response.body event with an empty body (encoded from the empty string) has been sent to indicate response completion.

## Side Effects:
    - Network/transport: awaiting send will result in ASGI protocol messages being forwarded to the ASGI server which typically performs network I/O.
    - No filesystem, database, or global state mutation occurs in this helper itself. Any side effects originate from the ASGI transport or callers.

## Control Flow:
flowchart TD
    Start --> Call_asgi_send
    Call_asgi_send --> asgi_send_ok{asgi_send awaited successfully?}
    asgi_send_ok -- Yes --> Return
    asgi_send_ok -- No --> Propagate_error
    Propagate_error --> End

Notes:
- "Call_asgi_send" represents the single await asgi_send(send, "", status=..., headers={"Location": location}, content_type="text/html; charset=utf-8").
- Any exception raised by asgi_send (including transport/send failures or header encoding errors) propagates to the caller.

## Examples:
Example — simple ASGI handler redirect:
    # inside an ASGI app(scope, receive, send) coroutine
    await asgi_send_redirect(send, "/login?next=/dashboard")

Example — permanent redirect (301):
    await asgi_send_redirect(send, "https://example.com/new-location", status=301)

Example — defensive error handling around the send:
    try:
        await asgi_send_redirect(send, target_url)
    except Exception as e:
        # log and fall back to an internal error response or re-raise
        logger.exception("Redirect failed: %s", e)
        # optionally send an error response or close the connection

## `datasette.utils.asgi.asgi_send` · *function*

## Summary:
Emit a complete non-streaming HTTP response over ASGI by invoking a response-start helper and then sending a single http.response.body event containing the UTF-8 encoded text content.

## Description:
This small coroutine performs the final protocol-level emission for simple textual responses. It calls a separate helper (asgi_start) to perform the response-start step (status and headers) and then sends the body as a single ASGI http.response.body event with the content encoded as UTF-8 bytes.

Known callers and invocation context:
- No concrete callers were discovered in the provided repository snapshot for this specific module-level function. Typical callers are:
  - ASGI application handlers or framework code that have assembled status, headers and a text payload and now need to transmit them to the ASGI server.
  - Higher-level response helpers that choose the simple non-streaming path for small/complete textual responses.
- This function is intended for the point in the request lifecycle where the full response body is available and streaming is not required.

Why this function is separate:
- Encapsulates the two-step ASGI emission (start event + single-chunk body) so callers do not need to construct ASGI event dictionaries or perform byte-encoding for the body.
- Keeps responsibilities separated: header/status framing is delegated to asgi_start; this function focuses on sending the encoded body immediately after.

## Args:
    send (Callable[[dict], Awaitable[None]]):
        The ASGI send callable provided by the server/framework. Must be awaitable and accept a single dict representing an ASGI event.
    content (str):
        Text payload to send in the response body. The function will call content.encode("utf-8"); therefore content must be a str.
    status (int):
        HTTP status code to forward to the response-start helper (e.g., 200, 404).
    headers (optional):
        Optional headers passed through to the response-start helper. Expected to be in a form accepted by that helper (commonly a mapping or iterable of (name, value) pairs with string keys and values). If None, no additional headers are supplied.
    content_type (str, optional):
        MIME type string to be provided to the response-start helper (defaults to "text/plain").

Interdependencies:
- This function delegates header and status emission to asgi_start(send, status, headers, content_type). The correctness of the overall ASGI emission depends on that helper performing the http.response.start event emission as expected.

## Returns:
    None
    - The coroutine returns None after awaiting asgi_start and then awaiting send(...) for the body event. No other return values are produced.

## Raises:
    AttributeError:
        - If content is not a str and therefore has no .encode method, calling content.encode("utf-8") will raise AttributeError which propagates.
    TypeError:
        - If send is not callable/awaitable, awaiting send(...) will raise a TypeError (or related error) which propagates.
    Any exception raised by asgi_start or by the provided send callable:
        - Exceptions raised by the response-start helper or the ASGI transport (send) are propagated unchanged to the caller.

## Constraints:
Preconditions:
    - send must be an awaitable-capable callable following the ASGI send contract (accepting a single dict event).
    - content must be a Python str.
    - status should be an integer valid as an HTTP status code.
    - headers (if provided) must be acceptable to asgi_start (string keys/values or iterable of pairs).
Postconditions:
    - The response-start helper will have been awaited with the provided status, headers and content_type (assumes that helper emits the http.response.start event).
    - A single ASGI http.response.body event will have been awaited with the "body" set to content.encode("utf-8").
    - No mutation of the provided arguments is performed by this function.

## Side Effects:
    - Network/transport: awaiting the provided send callable results in ASGI protocol messages being forwarded to the ASGI server which typically performs network I/O.
    - Encoding: the content string is converted to UTF-8 bytes.
    - No filesystem, database, or global state mutations are performed directly by this function. Side effects from asgi_start or the ASGI server may occur.

## Control Flow:
flowchart TD
    Start --> Call_asgi_start
    Call_asgi_start --> asgi_start_ok{asgi_start awaited successfully?}
    asgi_start_ok -- No --> Propagate_error
    asgi_start_ok -- Yes --> Encode_content
    Encode_content --> body_send
    body_send --> body_send_ok{await send succeeded?}
    body_send_ok -- Yes --> Return
    body_send_ok -- No --> Propagate_error
    Propagate_error --> End

Notes:
- "Propagate_error" indicates any exception raised by asgi_start, content.encode, or awaiting send will bubble up to the caller.

## Examples:
Example — sending a simple text response from an ASGI application handler:

    # inside an ASGI app(scope, receive, send) coroutine
    await asgi_send(
        send,
        content="Hello, world!",
        status=200,
        headers=[("x-frame-options", "deny")],
        content_type="text/plain; charset=utf-8"
    )

Example — handling a non-text payload defensively:

    try:
        await asgi_send(send, content, status, headers)
    except AttributeError:
        # content was not a str: convert or return an error response
        safe_text = str(content)
        await asgi_send(send, content=safe_text, status=500)
    except Exception as e:
        # transport or helper error: log and abort
        logger.exception("Failed to send response: %s", e)

## `datasette.utils.asgi.asgi_start` · *function*

*No documentation generated.*

## `datasette.utils.asgi.asgi_send_file` · *function*

## Summary:
Asynchronously streams a local file to an ASGI client by sending an HTTP start message (status 200) followed by one or more http.response.body messages containing the file bytes.

## Description:
- Known callers within the provided context:
    - No callers were found in the provided pre-loaded context. This is a low-level ASGI helper intended to be called from ASGI application code or higher-level helpers that perform routing and error handling.
- When to call:
    - Use when an ASGI application needs to return the contents of a local file (download or direct serve) and wants to stream it efficiently without loading the entire file into memory.
- Why this logic is extracted:
    - Encapsulates the asynchronous file I/O and ASGI send-message loop required to stream a file. Keeps ASGI message formatting, content-length calculation, content-type resolution, and chunking logic in one reusable function so that route handlers can remain simple and focused on higher-level concerns (authentication, routing, error handling).
- Responsibility boundary:
    - Responsible for: preparing/mutating headers (content-length, content-disposition), determining content-type (if not provided), opening the file asynchronously, and streaming bytes via the provided send callable.
    - Not responsible for: pre-validating permissions or translating file-not-found conditions into HTTP error responses; callers should catch filesystem exceptions and convert them into appropriate ASGI responses.

## Args:
    send (callable): ASGI send callable. Must be awaitable: await send(message). The function will call send with http.response.body messages and will call an external helper (asgi_start) to initiate the response.
    filepath (str | os.PathLike): Path to the file on disk to be streamed. Will be cast to str when used with aiofiles.
    filename (str | None, optional): If provided, sets a "content-disposition" header to 'attachment; filename="..."' so browsers will prompt to download with this filename. Default: None.
    content_type (str | None, optional): Explicit Content-Type header value to send. If omitted, the function will call mimetypes.guess_type(filepath)[0] and fall back to "text/plain" if guess_type returns None. Default: None.
    chunk_size (int, optional): Number of bytes to read from the file per iteration. Must be a positive integer. Default: 4096.
    headers (dict[str,str] | None, optional): Optional dict of response headers to include. If provided, this dict will be mutated in-place (the function adds or overwrites "content-length" and may add "content-disposition"). If None, a new headers dict is created. Default: None.

Notes on interdependencies:
    - If filename is provided, the function will add/overwrite the "content-disposition" header.
    - The "content-length" header is always computed from the actual file size on disk and will overwrite any existing value with the computed size.

## Returns:
    None
    - The function has no explicit return and completes by sending ASGI messages via the provided send callable. Any consumed return is not produced by this function.

## Raises:
    - FileNotFoundError: If aiofiles.os.stat or aiofiles.open fails because the file does not exist.
    - PermissionError or OSError: If filesystem access is denied or other OS-level errors occur during stat or open.
    - Any exception raised by the provided send callable (for example, an ASGI consumer that has closed), which will propagate to the caller.
    - ValueError or TypeError may be raised by aiofiles or the OS layer if filepath or chunk_size have invalid types/values.

## Constraints:
Preconditions:
    - The caller must supply a valid ASGI send callable and a valid existing filesystem path accessible to the process.
    - The event loop must be running (function is async and must be awaited).
    - chunk_size should be a positive integer greater than zero.

Postconditions:
    - After successful completion, the ASGI connection will have received an http.response.start (via asgi_start) and one or more http.response.body messages; when the final body message is sent, its more_body flag will be False.
    - The headers dict passed in (if any) will contain keys "content-length" and optionally "content-disposition" and any other headers the caller provided.

## Side Effects:
    - I/O: Performs asynchronous filesystem operations: a stat call to determine file size and reading the file contents in binary mode via aiofiles.
    - Network/ASGI: Sends ASGI messages to the client via the provided send callable (initiates response and streams body chunks).
    - Mutates the headers dict argument in-place when a headers dict is provided (adds/overwrites "content-length" and may add "content-disposition").
    - No global state, database, or external service calls are made by this function.

## Control Flow:
flowchart TD
    A[Start asgi_send_file] --> B{headers provided?}
    B -->|no| C[headers = {}]
    B -->|yes| D[use provided headers (mutated)]
    C --> E{filename provided?}
    D --> E
    E -->|yes| F[set content-disposition header]
    E -->|no| G[skip content-disposition]
    F --> H[stat(filepath) -> file_size]
    G --> H
    H --> I[set headers["content-length"] = file_size]
    I --> J[async open(filepath, "rb")]
    J --> K[call asgi_start(send, 200, headers, content_type_or_guessed)]
    K --> L[loop: read chunk_size bytes]
    L --> M{chunk length == chunk_size?}
    M -->|true| N[more_body = True; send(http.response.body with more_body=True)]
    M -->|false| O[more_body = False; send(final http.response.body with more_body=False)]
    N --> L
    O --> P[End]

## Examples:
- Typical ASGI handler usage (conceptual, asynchronous):
    1. In an ASGI request handler that has received scope and the send callable, determine the filesystem path to serve (e.g., mapping from URL to a file in a static directory).
    2. Call asgi_send_file(send, filepath, filename="suggested-name.txt", content_type="text/plain", headers={"x-custom": "value"}).
    3. Await the call; if it succeeds, the response will have been started (status 200) and the file streamed.
    4. If the file does not exist or access is denied, catch FileNotFoundError / PermissionError and send an appropriate ASGI error response (for example, send an http.response.start with status 404 or 403 and a small error body).

- Error handling sketch (conceptual):
    - try:
        await asgi_send_file(send, filepath)
      except FileNotFoundError:
        send an ASGI start message with status 404 and a short body indicating "Not Found"
      except PermissionError:
        send an ASGI start message with status 403 and a short body indicating "Forbidden"

Notes:
    - The function relies on asgi_start to issue the initial http.response.start message; errors raised by asgi_start or by the send callable will propagate to the caller and should be handled by the caller where appropriate.

## `datasette.utils.asgi.asgi_static` · *function*

## Summary:
Creates an ASGI-compatible request handler that serves files from a given filesystem root path, returning appropriate HTTP error responses for missing files, directories, or path traversal attempts.

## Description:
This factory function returns an async handler (callable) that:
- Reads the "path" route parameter from request.scope["url_route"]["kwargs"]["path"] and treats it as a relative path under the provided root_path.
- Resolves and validates the resulting filesystem path, forbids directory listing, enforces that the resolved path is inside the configured root directory, and streams the file contents to the ASGI client.

Known callers (from provided context):
- No direct callers are present in the preloaded context. Typically this function is used by code that configures routing for static assets — e.g., a router or application setup step will call this function with a filesystem root and register the returned async handler for a route that provides a "path" parameter.

Why extracted into its own function:
- Encapsulates the static-file serving policy (resolve, containment check, directory prohibition, streaming) into a single reusable factory so route configuration code can easily obtain an ASGI handler for a given root directory without duplicating path validation and error handling logic.

## Args:
    root_path (str | os.PathLike | pathlib.Path):
        Root filesystem path (directory) that files will be served from. It is converted to a pathlib.Path internally.
    chunk_size (int, optional):
        Number of bytes requested per read/send chunk when streaming the file. Defaults to 4096.
    headers (None | any, optional):
        Present in the function signature but unused in the implementation shown. Provided for API compatibility only.
    content_type (None | any, optional):
        Present in the signature but unused by the current implementation. Provided for API compatibility only.

Notes on parameter interaction:
- chunk_size is forwarded to asgi_send_file and therefore controls the file streaming chunking behavior.
- headers and content_type are accepted but ignored; passing values has no effect in the current implementation.

## Returns:
    async function(request, send) -> None
    - A coroutine function suitable as an ASGI endpoint handler.
    - Behavior of the returned handler:
        * If request.scope["url_route"]["kwargs"]["path"] is missing, a KeyError will be raised by the handler (no explicit catch in code).
        * If Path resolution raises FileNotFoundError during initial resolve, the handler calls asgi_send_html(send, "404: Directory not found", 404) and returns without further action.
        * If the resolved path is a directory, the handler calls asgi_send_html(send, "403: Directory listing is not allowed", 403) and returns.
        * If the resolved path is not inside root_path (determined by full_path.relative_to(root_path.resolve())), the handler calls asgi_send_html(send, "404: Path not inside root path", 404) and returns.
        * If asgi_send_file raises FileNotFoundError while attempting to stream the file, the handler calls asgi_send_html(send, "404: File not found", 404) and returns.
        * On success, asgi_send_file is awaited to stream the file; the handler then returns None.

All return paths complete by calling one of the helper functions (asgi_send_html or asgi_send_file) which are responsible for emitting the ASGI messages via the provided send callable.

## Raises:
    KeyError
        - If request.scope or url_route or kwargs or path is missing, direct indexing request.scope["url_route"]["kwargs"]["path"] will raise KeyError (propagates; not caught in the handler).
    Any exceptions raised by asgi_send_html or asgi_send_file other than FileNotFoundError
        - The code only catches FileNotFoundError in two places. Any other exception raised by the helper functions (or by Path operations other than the handled FileNotFoundError and ValueError) will propagate to the caller.

## Constraints:
Preconditions:
    - The returned handler expects an ASGI-style call signature: it will be invoked with (request, send) where:
        * request is an object with a scope mapping accessible as request.scope and that mapping contains url_route -> kwargs -> path.
        * send is an ASGI send callable used by asgi_send_html/asgi_send_file to emit responses.
    - root_path should be a valid filesystem path; the function converts it to pathlib.Path.

Postconditions:
    - After successful completion, the handler will have called asgi_send_file(send, full_path, chunk_size=chunk_size) to stream the file contents to the client (or will have called asgi_send_html to emit an error and returned).
    - The function guarantees that it will not serve directories or files located outside the configured root_path (it enforces containment via Path.relative_to and returns a 404 if the requested path is outside).

## Side Effects:
    - Uses helper functions asgi_send_html and asgi_send_file to write responses; these helpers use the provided ASGI send callable to emit HTTP response start/body messages.
    - No filesystem writes are performed by this function itself; it reads filesystem metadata and passes a Path to asgi_send_file, which is expected to perform file reading/streaming.
    - No global state is modified by this function.

## Control Flow:
flowchart TD
    A[Start: inner_static called with request, send] --> B{Extract path from request.scope["url_route"]["kwargs"]["path"]}
    B --> C[Compute full_path = (root_path / path).resolve().absolute()]
    C --> D{Did resolve raise FileNotFoundError?}
    D -- Yes --> E[Call asgi_send_html(send, "404: Directory not found", 404); return]
    D -- No --> F{Is full_path a directory?}
    F -- Yes --> G[Call asgi_send_html(send, "403: Directory listing is not allowed", 403); return]
    F -- No --> H{Is full_path inside root_path? (relative_to successful)}
    H -- No (ValueError) --> I[Call asgi_send_html(send, "404: Path not inside root path", 404); return]
    H -- Yes --> J[Attempt to await asgi_send_file(send, full_path, chunk_size)]
    J --> K{Did asgi_send_file raise FileNotFoundError?}
    K -- Yes --> L[Call asgi_send_html(send, "404: File not found", 404); return]
    K -- No --> M[File streamed successfully; return]

## Examples:
- Typical setup:
    1) Create a handler: call the factory with a filesystem directory (for example, "/var/www/static"). The call returns an async handler that accepts (request, send).
    2) Register the returned handler for a route that provides a "path" parameter (for example, a route pattern that captures a single path segment or the rest of the path).
    3) When a request arrives, the handler attempts to resolve and stream the file. If the file is missing, a 404 response body (asgi_send_html is invoked with either "404: Directory not found" or "404: File not found") is emitted; directory requests yield a 403 response.

- Error handling notes for integrators:
    * Ensure router populates request.scope["url_route"]["kwargs"]["path"] for the route bound to this handler, otherwise a KeyError will occur.
    * If you want custom headers or content-type behavior, you must wrap or replace asgi_send_file/asgi_send_html (headers and content_type parameters in this function are unused in the current implementation).

## `datasette.utils.asgi.Response` · *class*

*No documentation generated.*

### `datasette.utils.asgi.Response.__init__` · *method*

## Summary:
Set up a new Response instance by assigning body, status, headers (normalizing None to an empty dict), initializing an internal cookie-header list, and storing the content type.

## Description:
This is the class constructor that creates and initializes the minimal set of attributes required on a Response object. It performs direct assignments from the provided arguments and guarantees that headers and the internal cookie-header list exist on the instance after construction.

Known callers and context:
    - Not declared in the provided snippet. This method is invoked when a Response object is instantiated.

Why this logic is its own method:
    - As the __init__ implementation, it centralizes attribute creation so other instance methods can rely on these attributes existing.

## Args:
    body (Optional[Any]): Payload to store on the instance. Default: None.
    status (int): HTTP status code to store on the instance. Default: 200.
    headers (Optional[dict]): Mapping of header names to values. Default: None.
        - If None is passed, the constructor assigns an empty dict to self.headers.
    content_type (str): Content-Type value to store on the instance. Default: "text/plain".

## Returns:
    None — constructors do not return a value. The method initializes instance attributes.

## Raises:
    None — this implementation contains only assignments and does not raise exceptions for any input values.

## State Changes:
Attributes READ:
    - None. The constructor does not read pre-existing instance attributes.

Attributes WRITTEN:
    - self.body: set to the provided body argument.
    - self.status: set to the provided status argument.
    - self.headers: set to the provided headers argument, or to a newly created empty dict when headers is None.
    - self._set_cookie_headers: initialized to an empty list.
    - self.content_type: set to the provided content_type argument.

## Constraints:
Preconditions:
    - None enforced by this method. Inputs are accepted as provided.

Postconditions:
    - After construction, the instance has attributes body, status, headers, _set_cookie_headers, and content_type.
    - self.headers is guaranteed to be a dict.
    - self._set_cookie_headers is guaranteed to be an empty list.

## Side Effects:
    - Mutates only the newly created instance by setting attributes.
    - No I/O, global state changes, or external service calls are performed by this constructor.

### `datasette.utils.asgi.Response.asgi_send` · *method*

## Summary:
Sends this Response over an ASGI connection by emitting the required http.response.start and http.response.body events; does not modify the Response object.

## Description:
This coroutine serializes the Response's headers, cookies, status and body into two ASGI events and awaits the provided ASGI send callable to transmit them to the client.

Known callers and invocation context:
- An ASGI application or request handler that constructs a Response and dispatches it to the ASGI server will call this method at the point where the Response is ready to be sent (i.e., during the ASGI "send" phase). Typical usage is from an ASGI app function which receives a "send" callable from the server and calls await response.asgi_send(send).
- Within the Datasette codebase, this is the final step of the response lifecycle: after headers, cookies and body have been prepared, asgi_send performs the actual protocol-level emission to the ASGI server.

Why this is its own method:
- Encapsulates ASGI-specific framing (event types, header byte-encoding, set-cookie handling and single-chunk body emission) so callers do not need to know ASGI event shapes.
- Keeps concerns separated: higher-level response construction and header/cookie management are done elsewhere; this method focuses solely on transforming that state into ASGI events and invoking the send callable.

## Args:
    send (Callable[[dict], Awaitable[None]]):
        The ASGI send callable provided by the ASGI server. It must be an awaitable callable that accepts a single dict describing an ASGI event. The method will await send() twice:
        - Once with {"type": "http.response.start", "status": int, "headers": list[list[bytes, bytes]]}
        - Once with {"type": "http.response.body", "body": bytes}
        No default.

## Returns:
    None
    - The coroutine returns None after both ASGI events have been awaited.
    - There are no alternate return values.

## Raises:
    TypeError / AttributeError / ValueError (propagated from underlying operations):
        - If self.body is neither bytes nor a str (so .encode is not available), calling .encode will raise AttributeError; this will propagate.
        - If header keys or values (including cookie headers) are not strings, attempting to .encode("utf-8") on them may raise AttributeError.
        - If self.status is not an int, ASGI servers may raise when validating the event; the method itself does not perform explicit validation and will propagate any exception raised by send.
        - Any exception raised by the provided send callable (e.g., transport/network errors) will propagate.

## State Changes:
    Attributes READ:
        - self.headers: dict-like mapping of header-name (str) -> header-value (str); used to build the ASGI headers.
        - self.content_type: str; written into the "content-type" header before sending.
        - self._set_cookie_headers: iterable/list of cookie header strings; each appended as an additional "set-cookie" header.
        - self.status: int; used as the HTTP response status code in the http.response.start event.
        - self.body: bytes or str; used as the payload in the http.response.body event.

    Attributes WRITTEN:
        - None. This method does not mutate any attributes on self.

## Constraints:
    Preconditions:
        - self.status must be an integer representing a valid HTTP status code.
        - self.headers must be an iterable mapping of string header names to string header values.
        - self.content_type must be a string (will be assigned to the "content-type" header).
        - self._set_cookie_headers must be an iterable of strings (each a single Set-Cookie header value).
        - self.body must be either bytes or a str. If it is a str it will be encoded to UTF-8; if it is bytes it will be sent as-is.

    Postconditions:
        - Two ASGI events will have been awaited on the provided send callable:
            1. http.response.start with the assembled headers and status.
            2. http.response.body with the full response body as bytes (single-chunk, more_body not used).
        - The Response object remains unchanged.

## Side Effects:
    - Network/transport: invoking send will ultimately cause data to be written to the network by the ASGI server; this method triggers that I/O.
    - ASGI protocol actions: emits the http.response.start event (headers and status) and a single http.response.body event (single-chunk body). It does not stream the body in multiple chunks and does not set the more_body flag.
    - Encoding: header names and values and cookie headers are encoded to UTF-8 bytes for ASGI compliance. The body is encoded to UTF-8 if it is a str.
    - Exceptions raised by send or by encoding operations will propagate to the caller.

## Implementation notes / behavior detail:
    - Headers are transformed into a list of [name_bytes, value_bytes] pairs (both UTF-8 encoded) as required by the ASGI spec.
    - The "content-type" header is explicitly set/overwritten with self.content_type prior to sending.
    - Each entry of self._set_cookie_headers is appended as a separate "set-cookie" header (lowercased to b"set-cookie" in the header list).
    - This method assumes the caller will not require streaming or chunked sends; it always sends the full body in a single http.response.body event.

### `datasette.utils.asgi.Response.set_cookie` · *method*

## Summary:
Add a Set-Cookie header for this Response by recording a cookie header string on the instance; does not send the header immediately but ensures asgi_send will include it when the response is sent.

## Description:
This method builds a cookie using Python's SimpleCookie, sets the supplied attributes when provided, and appends the resulting header string to the Response._set_cookie_headers list. The headers recorded here are consumed by Response.asgi_send which converts each entry into a "set-cookie" HTTP header when the response is emitted.

Known callers / typical usage:
- Called by request handlers, view code, or middleware that construct a Response and need to set a cookie before the response is sent.
- Lifecycle stage: invoked after creating a Response object and before calling asgi_send (or returning the Response to the ASGI handling layer). It is a pre-send mutation step on the Response object.

Why this is a separate method:
- Cookie construction and header formatting involve several attribute decisions and edge rules (only include attributes when not None, boolean flags only when True, validation of samesite). Encapsulating this logic keeps response construction code concise and centralizes cookie header formatting and queuing for ASGI output.

## Args:
    key (str):
        Cookie name. Will be used as the cookie key in the header.
    value (str, optional):
        Cookie value. Defaults to "" (empty string). Any value will be converted by SimpleCookie/str handling.
    max_age (int|str|None, optional):
        If provided (not None), added as the Max-Age attribute. Typically an integer number of seconds, but any non-None value is accepted and converted to a string in the header.
    expires (str|int|None, optional):
        If provided (not None), added as the Expires attribute. Typically a string in the HTTP-date format or a numeric timestamp, but any non-None value is accepted and converted to a string.
    path (str|None, optional):
        If provided (not None), added as the Path attribute. Defaults to "/".
    domain (str|None, optional):
        If provided (not None), added as the Domain attribute.
    secure (bool, optional):
        If True, adds the Secure attribute (no value). Defaults to False.
    httponly (bool, optional):
        If True, adds the HttpOnly attribute (no value). Defaults to False.
    samesite (str, optional):
        SameSite attribute value; defaults to "lax". The value is validated against the module-level SAMESITE_VALUES constant — an assertion will fail if the provided value is not a member of that constant.

## Returns:
    None
    - The method mutates the Response instance by appending a formatted "Set-Cookie" header string to self._set_cookie_headers and does not return any value.

## Raises:
    AssertionError:
        Raised when the provided samesite value is not contained in the module-level SAMESITE_VALUES constant. The exact assertion message is: "samesite should be one of {}".format(SAMESITE_VALUES)
    (No other exceptions are explicitly raised by this method; underlying SimpleCookie operations will be used for formatting and may raise if given invalid internal values, but the implementation does not add extra checks.)

## State Changes:
    Attributes READ:
        - (reads only module-level) SAMESITE_VALUES — used to validate the samesite arg
        - No instance attributes are read for decision logic.
    Attributes WRITTEN:
        - self._set_cookie_headers: the method appends one string (cookie.output(header="").strip()) to this list.

## Constraints:
    Preconditions:
        - The Response instance should be initialized such that self._set_cookie_headers is a list (Response.__init__ creates this).
        - key and value should be reasonable cookie name/value strings; the method does not validate cookie-name characters or perform escaping beyond SimpleCookie's behavior.
        - samesite must be a member of the module-level SAMESITE_VALUES constant (assertion enforces this).
    Postconditions:
        - After the call, one additional cookie header string is present at the end of self._set_cookie_headers.
        - Response.asgi_send will later include a "set-cookie" header for this cookie when emitting headers.

## Side Effects:
    - No I/O or network activity.
    - Mutates the Response object by appending to _set_cookie_headers.
    - Relies on SimpleCookie to format cookie attributes; the stored header is a plain string that will be encoded to bytes by asgi_send and sent as a "set-cookie" header.
    - No other global state is modified.

## Implementation notes / behavior details:
    - Attributes with value None are omitted from the cookie header (for example, if domain is None it will not appear).
    - The mapping of method parameter names to cookie attribute names:
        * max_age -> Max-Age (attribute name in header uses a hyphen)
        * expires -> Expires
        * path -> Path
        * domain -> Domain
        * samesite -> SameSite
    - Boolean flags secure and httponly are only included when True and are added with a truthy value (cookie[key]['secure'] = True results in a flag-like attribute in the header).
    - The header string appended is produced by cookie.output(header="").strip() and is ready to be inserted into an HTTP header list; Response.asgi_send will attach it to the outgoing headers as a "set-cookie" header.

### `datasette.utils.asgi.Response.html` · *method*

## Summary:
Return a newly constructed Response instance configured to deliver HTML: the provided body and status with content_type set to "text/html; charset=utf-8".

## Description:
A concise classmethod convenience constructor used during the response-construction stage (handlers, middleware, or tests) to produce an HTTP response containing HTML. Call sites typically include request handlers or middleware that want to return HTML to the client.

Why separate:
- Centralizes and standardizes the HTML content-type value so callers do not repeat the literal header string.
- Improves readability at call sites by expressing intent (HTML response) rather than repeatedly calling the full constructor.

Known callers / contexts:
- HTTP request handlers and view functions that return HTML pages.
- Middleware that needs to craft an HTML error page or redirect response body.
- Tests that need to assert on HTML responses.

## Args:
    cls (type): The Response class (bound automatically when called as a classmethod).
    body (str | bytes): The response body. Must be either:
        - str: will be encoded to UTF-8 when sending, or
        - bytes: will be sent as-is.
      Passing None or other non-str/bytes types is unsupported and will raise an error later when sending.
    status (int, optional): HTTP status code (e.g., 200, 404). Defaults to 200.
    headers (dict[str, str] | None, optional): Mapping of additional header names to values. If None, the Response constructor will normalize this to an empty dict.

## Returns:
    Response: An instance of cls with these fields set:
        - body: as provided,
        - status: as provided,
        - headers: the provided mapping (or normalized empty dict),
        - content_type: "text/html; charset=utf-8",
        - _set_cookie_headers: initialized to an empty list by the constructor.
    The returned object is ready for use with Response.asgi_send(send).

## Raises:
    None directly from this method.
    Indirect errors that may surface later:
        - AttributeError or TypeError during Response.asgi_send if body is None or a type without an encode method (because asgi_send expects str or bytes).
        - If status is not an int, downstream ASGI servers or clients may treat the response as invalid (this method does not validate status).

## State Changes:
Attributes READ:
    - None on an existing instance (this is a classmethod; it does not read instance state).

Attributes WRITTEN (on the returned instance):
    - body
    - status
    - headers (normalized to {} by __init__ when headers is None)
    - content_type
    - _set_cookie_headers (initialized to [])

## Constraints:
Preconditions:
    - cls must accept the keyword parameters body, status, headers, and content_type in its constructor (the built-in Response implementation does).
    - body must be either a str or bytes to avoid runtime errors at send time.
    - status should be an integer valid as an HTTP status code.

Postconditions:
    - The returned object is an instance of cls with content_type exactly "text/html; charset=utf-8".
    - headers will be a dict on the returned instance (empty dict if None was passed).
    - The instance is suitable for passing to its asgi_send coroutine to transmit an HTTP response.

## Side Effects:
    - Allocates and returns a new Response object. No I/O, logging, or external network calls are performed by this method itself.

## Example usage:
    - Response.html("<html><body>Hello</body></html>")  # returns a Response configured for HTML

### `datasette.utils.asgi.Response.text` · *method*

*No documentation generated.*

### `datasette.utils.asgi.Response.json` · *method*

## Summary:
Creates and returns a new response object (factory classmethod) whose body is the JSON-serialized string of the given Python object and whose Content-Type header is set to "application/json; charset=utf-8".

## Description:
- Known callers and context:
    - Used when code paths need to produce an HTTP/ASGI response containing JSON (for example, request handlers or view functions). It is typically invoked at the end of a request-handling pipeline to construct the outgoing response.
- Why this is a separate method:
    - Encapsulates JSON serialization and the canonical JSON content-type in a single, reusable factory. This prevents repetition of json.dumps and Content-Type assignment throughout the codebase and ensures consistent behavior for JSON responses.

## Args:
    cls (type):
        The response class or factory callable to instantiate. This parameter indicates the method is intended to be used as a classmethod (first argument is the class).
    body (Any):
        The Python object to serialize to JSON. Must be serializable by json.dumps or handled by the `default` callable.
    status (int, optional):
        HTTP status code for the constructed response. Defaults to 200. The method forwards this value unvalidated to the cls constructor.
    headers (optional):
        Additional headers to pass through to the response constructor unchanged. The exact accepted structure (e.g., dict, list of tuples) depends on the cls constructor and is not validated here. Defaults to None.
    default (callable, optional):
        Passed as the `default` argument to json.dumps to convert non-serializable objects. Should accept a single object and return a JSON-serializable replacement or raise TypeError.

## Returns:
    instance of cls:
        A newly constructed response object created by calling cls(...) with:
            - positional first argument: the JSON string returned by json.dumps(body, default=default)
            - keyword arguments: status (the provided status), headers (the provided headers), content_type set to "application/json; charset=utf-8"
        Notes and edge cases:
            - json.dumps returns a Python str (not bytes); that str is provided as the response body. The method does not encode the body to bytes — any encoding to bytes is the responsibility of downstream code that converts the response to ASGI messages.
            - json.dumps uses its default serializer settings except for the `default` callable when provided (for example, ensure_ascii remains True by default, meaning non-ASCII characters will be escaped in the produced string unless callers change behavior by supplying their own serializer via the `default` parameter).

## Raises:
    TypeError:
        Propagated from json.dumps when `body` contains objects that cannot be serialized and no suitable `default` callable is provided (or if the provided `default` raises TypeError).
    OverflowError:
        May be raised by json.dumps for certain unrepresentable numeric values; this method does not catch such exceptions.
    Any exceptions raised by json.dumps:
        The method does not perform exception handling for JSON serialization errors; they propagate to the caller.

## State Changes:
- Attributes READ:
    - None on the class or instance: the method does not access or depend on any class/instance attributes.
- Attributes WRITTEN:
    - None on the class or instance: the method constructs and returns a new response instance via cls(...) and does not mutate existing state.

## Constraints:
- Preconditions:
    - `body` should be JSON-serializable by the standard json module, or callers must supply a `default` callable that converts unsupported objects to serializable forms.
    - `status` should be an integer representing an HTTP status code; this method does not validate numeric ranges (100–599).
    - `headers`, if provided, must be in a form accepted by the cls constructor.
- Postconditions:
    - The returned object is guaranteed to have been constructed with the JSON string of `body` (as produced by json.dumps(body, default=default)), status set to the supplied status, headers set to the supplied headers (or None), and content_type equal to "application/json; charset=utf-8".

## Side Effects:
    - No I/O, network, or filesystem operations are performed by this method.
    - Performs CPU work to serialize `body` to a JSON string via json.dumps.
    - No external objects are mutated; only a new response instance is created and returned.

## Example (illustrative, not executable code block):
    Calling the classmethod with a simple mapping, e.g. Response.json({'ok': True}, status=201), results in a new response instance whose body equals the string produced by json.dumps({'ok': True}) and whose content_type is "application/json; charset=utf-8", with status set to 201.

### `datasette.utils.asgi.Response.redirect` · *method*

## Summary:
Construct and return a Response instance configured as an HTTP redirect: empty body, configured status code, and a Location header set to the provided path.

## Description:
- Nature and role:
    - This is a classmethod factory that creates Response objects representing HTTP redirects. It centralizes the common redirect pattern so handlers/middleware can create redirects with a single call.
- Known callers / usage context:
    - Intended to be called by request handlers, views, or middleware when the application needs to redirect the client. The returned Response is intended to be handed to ASGI send logic (e.g., Response.asgi_send) to send the actual HTTP response.
- Why separate:
    - Encapsulates the routine setup for a redirect (empty body + Location header + status) so code across the codebase does not duplicate this logic and so redirect responses are consistently constructed.

## Args:
    cls (type): The Response class (classmethod receiver). Used to construct the Response instance via cls("", status=status, headers=headers).
    path (str): Value to place into the HTTP Location header. Must be suitable as an HTTP header value and UTF-8 encodable (Response.asgi_send later encodes header strings to UTF-8).
    status (int, optional): HTTP status code to use. Signature default is 302. Typical redirect codes: 301, 302, 303, 307, 308.
    headers (MutableMapping[str, str] | None, optional): Optional mapping of additional headers. Default is None.

    Important detail about headers behavior:
    - The implementation uses "headers = headers or {}" before assigning the Location header.
    - Consequence:
        * If headers is None or any falsy value (for example None, False, 0, or an empty mapping like {}), the method will create and use a fresh dict; the caller's object will not be mutated.
        * If headers is a truthy mapping (e.g., a dict that already contains at least one key/value and therefore evaluates to True), that mapping will be used and mutated in-place by setting headers["Location"] = path.
    - Practical guidance:
        * To ensure your mapping is mutated in-place, pass a mapping that is truthy (for example, pre-populate it with at least one header).
        * If you pass a newly-created empty dict literal, that literal will be treated as falsy and will not be the dict stored on the returned Response (the method will create a different dict).

## Returns:
    Response: A newly constructed Response instance created by calling cls("", status=status, headers=headers).
    - For the concrete Response implementation in this file, the returned instance will have:
        * body == "" (empty string)
        * status equal to the provided status argument
        * headers equal to the mapping used internally (either the provided truthy mapping mutated in-place, or a fresh dict containing "Location": path)
        * content_type equal to the class's __init__ default (the Response.__init__ default is "text/plain" in this module)

## Raises:
    - The method contains no explicit raise statements.
    - Possible runtime errors (not explicitly raised here):
        * TypeError from calling cls if cls.__init__ does not accept the provided positional/keyword arguments.
        * TypeError or AttributeError when evaluating headers or assigning headers["Location"] = path if headers is not a mutable mapping supporting item assignment.
        * Encoding errors may surface later when Response.asgi_send encodes header values to UTF-8 if header keys/values are not encodable strings.

## State Changes:
- Attributes READ:
    - None of cls's attributes or any existing instance attributes are read by this method.
- Attributes WRITTEN:
    - The method does not modify attributes on cls or any existing Response instance.
    - It may mutate the caller's headers mapping in-place by setting headers["Location"] = path — but only when the mapping passed is truthy (see Args section for details).
    - The returned Response instance is initialized with new instance attributes (body, status, headers, content_type) by cls.__init__.

## Constraints:
- Preconditions:
    - path should be a str (or otherwise UTF-8 encodable) suitable for use as an HTTP Location header value.
    - headers, if provided and intended to be mutated, should be a truthy mutable mapping that supports item assignment (e.g., a dict with at least one key/value).
    - cls must accept the constructor call pattern used here: cls(body, status=status, headers=headers).
- Postconditions:
    - The Response returned will have a headers mapping that contains a "Location" key whose value equals path.
    - The Response body will be the empty string and its status attribute will equal the provided status.

## Side Effects:
    - Mutates the headers mapping supplied by the caller only when that mapping is truthy (adds or replaces the "Location" key).
    - No I/O, network calls, or global state changes are performed by this method itself.
    - When the returned Response is later sent (Response.asgi_send), header keys and values will be encoded to UTF-8 and transmitted; therefore header keys/values should be strings and UTF-8 encodable.

## Example (descriptive):
    To issue a standard temporary redirect to "/login", call this classmethod with path="/login" and the default status 302. If you supply an existing headers dict that already contains at least one header, that dict will be updated to include "Location": "/login". If you pass None or an empty dict, the method will create a new internal dict that the returned Response will carry (your original empty dict will remain unchanged).

## `datasette.utils.asgi.AsgiFileDownload` · *class*

## Summary:
A small ASGI helper object that represents a file download response and can stream a local file to an ASGI client by delegating to the asgi_send_file helper.

## Description:
AsgiFileDownload is a lightweight wrapper that packages the information needed to stream a local filesystem file over ASGI: the file path, an optional suggested filename for download, a content type, and optional response headers. It exists to keep route-handling code concise: create an AsgiFileDownload with the desired parameters and call its async asgi_send(send) method from an ASGI handler to perform the file streaming.

When to instantiate:
- In an ASGI request handler (or higher-level helper) when you need to return a local file as the HTTP response body (for download or direct serve).
- It is useful where the application wants a small, immutable descriptor object passed around (for example, returned by a view or queued for later streaming).

Known caller pattern:
- A typical ASGI handler will create AsgiFileDownload(filepath, filename=..., content_type=..., headers=...) and await instance.asgi_send(send) to start the response and stream the file.

Motivation and responsibility boundary:
- Responsibility: Hold parameters describing the file response and perform the actual stream by delegating to the lower-level asgi_send_file implementation.
- Not responsible for: mapping URLs to filesystem paths, access control checks, or converting filesystem errors into HTTP error responses. Those responsibilities belong to the caller.

## State:
Attributes (public instance attributes):
- headers (dict[str, str])
    - Description: Response header mapping that will be used/modified when streaming.
    - Initialization: Created from the headers parameter via `headers or {}` in __init__.
    - Valid values: Mapping of header-name -> header-value strings. The stored dict will be mutated by asgi_send_file (it will add/overwrite "content-length" and may add "content-disposition").
    - Important note: The __init__ uses the expression `headers or {}`. This means any falsy headers value (None, {}, empty string, 0, etc.) will result in a new empty dict being stored. If you pass a non-empty dict it will be used directly and may be mutated in-place by the streaming process.

- filepath (str | os.PathLike)
    - Description: Filesystem path of the file to stream.
    - Initialization: Passed through from the filepath parameter without conversion.
    - Constraint: Must refer to an existing file accessible to the process when asgi_send is called; asgi_send_file will perform stat/open operations and will raise filesystem-related exceptions if the file is missing or inaccessible.
    - Invariant: Treated as an immutable descriptor; AsgiFileDownload does not alter the file contents or the path string.

- filename (str | None)
    - Description: Optional suggested filename for the client (used to set a "Content-Disposition: attachment; filename=\"...\"" header).
    - Initialization: Taken directly from the filename parameter.
    - Valid values: Any string acceptable to include in an HTTP Content-Disposition header. If None, no content-disposition header is set by the wrapper (asgi_send_file may skip setting it).

- content_type (str | None)
    - Description: The value to use for the Content-Type response header.
    - Initialization: Defaults to "application/octet-stream" if not provided by the caller.
    - Behavior: The value is forwarded to asgi_send_file. If you pass None explicitly, asgi_send_file will attempt to guess the MIME type from the filepath; otherwise the provided value will be used verbatim.

Class invariants:
- headers is always a dict at runtime (never None).
- filepath, filename, content_type remain whatever the caller provided; the instance itself performs no normalization.
- asgi_send may mutate headers (adding content-length/content-disposition) but will not change filepath/filename/content_type attributes.

## Lifecycle:
Creation:
- Instantiate with:
    - filepath (required): str or os.PathLike pointing to the file.
    - filename (optional): str or None. Default: None.
    - content_type (optional): str or None. Default: "application/octet-stream".
    - headers (optional): dict[str,str] or other truthy mapping. Default: None (results in new dict).

Usage:
- Typical sequence:
    1. Create an instance: downloader = AsgiFileDownload(filepath, filename="report.csv", content_type="text/csv", headers={"x-meta":"v1"})
    2. Inside an async ASGI handler, call: await downloader.asgi_send(send)
       - asgi_send is an async method that delegates to asgi_send_file(send, filepath, filename=..., content_type=..., headers=...)
       - The asgi_send_file helper will:
           - stat the file to compute content-length (mutates headers["content-length"])
           - optionally set content-disposition if filename provided (mutates headers)
           - open the file asynchronously and stream it in chunks via the provided ASGI send callable
           - call asgi_start/send http.response.start before sending bodies
    3. After await completes, the ASGI response will have been started and the file streamed (or an exception propagated).

Destruction / Cleanup:
- No explicit close or context-manager API on AsgiFileDownload.
- The underlying asgi_send_file opens and closes the file within its own streaming coroutine; AsgiFileDownload has no additional cleanup responsibilities.
- Exceptions raised during streaming (e.g., FileNotFoundError, PermissionError, or send-related errors) propagate to the caller, which should decide how to handle them (for example, by sending an HTTP error response instead).

Sequencing constraints:
- asgi_send must be awaited in an async context while an ASGI connection is active and you have a valid send callable.
- Do not reuse an instance concurrently to stream the same file to multiple clients unless you understand how shared headers dict mutation will behave; prefer creating separate instances per request or pass a fresh headers dict per instance.

## Method Map:
flowchart TD
    A[caller: create instance] --> B[AsgiFileDownload]
    B --> C[asgi_send(send) - async]
    C --> D[asgi_send_file(send, filepath, filename, content_type, headers)]
    D --> E[asgi_start -> http.response.start]
    D --> F[open file (aiofiles) -> read chunks]
    F --> G[send http.response.body messages via send]
    G --> H[final body message (more_body=False)] --> I[done]

Note: asgi_send is a thin delegating method — the streaming and header mutations occur inside asgi_send_file.

## Raises:
- __init__:
    - Does not raise for normal inputs. However, passing unusual objects as headers/filename/content_type may lead to TypeError only when streaming if those values are used by asgi_send_file or the ASGI layer.

- asgi_send(send):
    - Propagates exceptions raised by asgi_send_file and underlying operations:
        - FileNotFoundError: when the file does not exist (stat/open fail).
        - PermissionError or OSError: if filesystem access is denied or other OS-level errors occur.
        - TypeError or ValueError: if invalid argument types/values are passed (e.g., invalid chunk_size if modified in underlying call).
        - Any exception raised by the ASGI send callable (for example, consumer disconnect) will propagate.
    - Callers should catch these exceptions and convert them to appropriate ASGI error responses when necessary.

## Example:
- Typical usage pattern (conceptual):
    1. Create the descriptor:
       downloader = AsgiFileDownload("/srv/app/files/report.pdf", filename="report.pdf", content_type="application/pdf")
    2. In an ASGI endpoint handler with access to the send callable:
       await downloader.asgi_send(send)
       # After this await returns the response has been started and the file streamed.
    3. Error handling sketch:
       try:
           await downloader.asgi_send(send)
       except FileNotFoundError:
           # send an ASGI 404 response instead
           pass
       except PermissionError:
           # send an ASGI 403 response instead
           pass

Notes:
- Because the stored headers dict will be mutated by the streaming helper, do not rely on the header object identity being preserved when you pass falsy values (e.g., passing an empty dict literal will be replaced internally by a new empty dict because __init__ uses `headers or {}`).
- If you want to preserve and inspect the exact headers dict mutated during streaming, pass in a non-empty dict (truthy) when constructing the AsgiFileDownload instance.

### `datasette.utils.asgi.AsgiFileDownload.__init__` · *method*

## Summary:
Initializes a lightweight ASGI file-download response object by storing the file path, optional download filename, MIME type, and any additional response headers — updating the object's attributes but performing no I/O or validation.

## Description:
Known callers and context:
- The instance method asgi_send (on the same class) calls into asgi_send_file to actually stream the file. asgi_send_file performs file I/O and reads the stored attributes when sending.
- No other direct callers were found in the provided source; typically this initializer is invoked during request handling when code constructs a response object representing a downloadable file (i.e., at response creation time, before the ASGI send phase).
Why this is a separate method:
- The initializer is intentionally minimal: it acts as a plain-data holder for the values required to stream a file later. Keeping initialization separate avoids doing I/O or filesystem checks at construction time and keeps the streaming logic (asgi_send/asgi_send_file) focused on I/O and ASGI interaction.

## Args:
    filepath (str | pathlib.Path | os.PathLike):
        Path to the file on disk. The initializer accepts any object that can be converted to a filesystem path (it is later passed to aiofiles.os.stat and aiofiles.open after string conversion). No validation is performed here.
    filename (str | None, optional):
        Suggested download filename presented in the Content-Disposition header. If None, no Content-Disposition header will be added by __init__ itself (asgi_send/asgi_send_file will add it only if a filename is present).
    content_type (str, optional):
        MIME type to set for the response. Defaults to "application/octet-stream". If None or omitted, the sender may attempt to infer the type from the filepath when streaming.
    headers (dict[str, str] | None, optional):
        Additional HTTP headers to include in the response. If falsy (None, empty, etc.), it will be normalized to an empty dict. No deep validation of header keys/values is performed here.

## Returns:
    None
    - The method initializes instance attributes and returns nothing.

## Raises:
    - This initializer does not explicitly raise exceptions.
    - Implicit exceptions may occur later when these attributes are used (for example, if filepath is not a valid path, asgi_send_file will raise I/O-related exceptions when statting/opening the file). The initializer itself will not detect or raise those errors.

## State Changes:
Attributes READ:
    - headers (the passed-in headers parameter is read to compute the default)
    - filepath (reads the passed filepath parameter)
    - filename (reads the passed filename parameter)
    - content_type (reads the passed content_type parameter)

Attributes WRITTEN:
    - self.headers: Set to headers or {} (normalizes falsy to empty dict)
    - self.filepath: Set to the provided filepath value
    - self.filename: Set to the provided filename value
    - self.content_type: Set to the provided content_type value

## Constraints:
Preconditions:
    - Caller should supply a filepath that refers to an accessible file when the object is later used to stream data. The initializer performs no existence, permission, or type checks.
    - headers should be a mapping (dict-like) of header-name: value pairs if the caller expects header merging to behave predictably; however, any value can be assigned — misuse may cause errors later when headers are consumed.

Postconditions:
    - After return, the instance will have attributes self.headers, self.filepath, self.filename, and self.content_type set to the provided values (with headers normalized to {} when falsy).
    - No file I/O side effects will have occurred.

## Side Effects:
    - None during initialization: no filesystem access, network I/O, or external service calls.
    - Mutations are limited to setting attributes on the instance (no modifications to external objects unless the caller passed a mutable headers object and later mutates it).

### `datasette.utils.asgi.AsgiFileDownload.asgi_send` · *method*

## Summary:
Delegates to the shared file-streaming helper to asynchronously send the file referenced by this object to an ASGI client; does not catch or transform errors and may result in in-place mutation of this object's headers attribute.

## Description:
- Known callers and context:
    - Intended to be called by ASGI request-handling code that has constructed an AsgiFileDownload instance and now wants to stream the referenced file to the client. Typical usage is within an ASGI application or route handler after determining that a particular file should be returned (for example, as part of a "download" endpoint).
    - No lower-level callers are required inside this module; this method is a thin instance-level wrapper used by higher-level request dispatch code to keep file-send calls consistent and concise.

- Lifecycle / pipeline stage:
    - Invoked during the response phase of an ASGI request lifecycle when the application has decided to return a file as the HTTP response body.

- Why this is its own method:
    - Provides a concise instance-level API that takes the attributes of the AsgiFileDownload object (filepath, filename, content_type, headers) and calls the centralized asgi_send_file helper. This keeps route handlers simple (they only need to call instance.asgi_send(send)) and centralizes file-streaming behavior in one reusable helper. It also makes the call easy to override in subclasses or tests.

## Args:
    send (callable): ASGI send callable. Must be an awaitable callable that accepts an ASGI message dict (i.e., await send(message)). No default.

## Returns:
    None
    - Returns whatever asgi_send_file returns; in the canonical implementation this helper completes by sending ASGI messages and does not return a meaningful value (effectively None).

## Raises:
    - FileNotFoundError: propagated if the underlying asgi_send_file attempts to stat or open a non-existent file.
    - PermissionError or OSError: propagated if filesystem access is denied or other OS-level errors occur during stat/open/read.
    - Any exception raised by the provided send callable (for example, the ASGI connection closing) will propagate unchanged.
    - ValueError or TypeError may be raised if underlying libraries validate inputs (e.g., invalid chunk_size, invalid filepath type) — these are propagated.

## State Changes:
    Attributes READ:
        - self.filepath
        - self.filename
        - self.content_type
        - self.headers
    Attributes WRITTEN:
        - self.headers (may be mutated in-place by asgi_send_file; keys such as "content-length" and possibly "content-disposition" can be added or overwritten)

## Constraints:
    Preconditions:
        - The event loop must be running and this method must be awaited.
        - self.filepath must reference a filesystem path accessible to the process.
        - send must be a valid ASGI send callable (awaitable and accepting message dicts).
        - If self.headers is provided it should be a mutable mapping (dict-like) if the caller expects it to be mutated.

    Postconditions:
        - On successful completion, the ASGI connection will have been started and the file streamed via asgi_send_file (the underlying helper sends http.response.start and one or more http.response.body messages).
        - If a headers mapping was provided via self.headers, it will contain at least a "content-length" entry (and possibly a "content-disposition" entry) after the call returns.
        - No exceptions are swallowed; any exception raised during streaming will propagate to the caller.

## Side Effects:
    - Performs asynchronous filesystem I/O (stat and reading the file) via the asgi_send_file helper.
    - Sends ASGI messages to the client by invoking the provided send callable (network/transport side effects).
    - May mutate the headers mapping referenced by self.headers in-place (adds/overwrites "content-length" and may add "content-disposition").
    - Does not modify other attributes of self.

## `datasette.utils.asgi.AsgiRunOnFirstRequest` · *class*

## Summary:
A lightweight ASGI application wrapper that runs a list of asynchronous startup hooks once (on the first incoming request) before forwarding the request to the wrapped ASGI app.

## Description:
Use this class when you need to defer running asynchronous initialization tasks (startup hooks) until the first request arrives, rather than running them at process start. Typical callers create an instance by wrapping an existing ASGI application and supplying a list of asynchronous callables (startup hooks). Each hook is awaited sequentially the first time the wrapper receives an ASGI request, and then the wrapper forwards the request to the underlying ASGI app.

Motivation: In some deployment scenarios you may prefer lazy initialization (run expensive setup only if the app actually receives traffic). This class encapsulates that pattern so startup hooks are executed exactly once per wrapper instance and before the first forwarded request.

Responsibility boundary: This class:
- Ensures the provided list of startup hooks is iterated and awaited once (per wrapper instance) when the first request is handled.
- Forwards all ASGI calls to the wrapped application unchanged after running the hooks.
It does not:
- Manage concurrency across processes or threads (behavior is per-instance and per-process).
- Retry startup hooks on failure; exceptions raised by hooks propagate to the caller.
- Validate hook signatures beyond being present in a list; each hook must be an awaitable callable that takes no arguments.

## State:
- asgi (callable): The wrapped ASGI application. Expected call signature: await asgi(scope, receive, send). No further constraints are enforced by this class.
- on_startup (list): A Python list of startup hook callables. The constructor asserts that this is a list; elements are expected to be asynchronous callables (coroutines or callables returning awaitables) that accept no parameters. Valid values: any list object; however, semantic correctness requires its elements be awaitable callables.
- _started (bool): Internal flag indicating whether the startup hooks have already been triggered for this instance. Initially False. After the first invocation that runs the hooks, it is set to True. Invariants:
  - _started is always a boolean.
  - When _started is True, the implementation guarantees that the wrapper will not iterate and await on_startup again for that instance.

Notes on invariants:
- The "run-once" guarantee is per-instance. If multiple AsgiRunOnFirstRequest instances wrap the same underlying ASGI app (e.g., in multiple processes), each instance runs hooks independently.
- The class does not enforce or verify that elements of on_startup are awaitable; responsibility for correct hook types lies with the caller.

## Lifecycle:
Creation:
- Instantiate by providing the wrapped ASGI application and a list of startup hooks.
- Signature: AsgiRunOnFirstRequest(asgi, on_startup)
  - asgi: wrapped ASGI app (callable)
  - on_startup: list (required) of asynchronous callables (no-arg functions/coroutines)

Usage (typical sequence):
1. Create the wrapper with the underlying ASGI app and a list of hooks.
2. The wrapper is used as the ASGI application (awaitable callable) by the ASGI server. The server will call the wrapper with the ASGI scope, receive, and send parameters.
3. On the first call to the wrapper:
   - The wrapper checks _started; if False, it sets _started = True and then iterates the on_startup list, awaiting each hook sequentially.
   - If all hooks complete successfully, the wrapper then forwards the original ASGI call to the wrapped asgi application and returns the wrapped app's result.
   - If any hook raises, that exception propagates; the wrapped app is not called for that request.
4. On subsequent calls, since _started is True, the wrapper directly forwards calls to the wrapped app without invoking hooks.

Destruction / Cleanup:
- The class has no explicit cleanup API (no close/stop). Any resource cleanup for hooks or the wrapped app must be handled by those objects themselves.
- Because hooks run only once (and are awaited), any long-lived resources they create must be managed by the hook implementations.

Concurrency considerations:
- In a standard asyncio single-threaded event loop, the initial check and setting of _started occur without awaits, so once a first invocation begins, it will set _started before yielding to other tasks; this prevents duplicate execution of hooks within the same event loop instance.
- This class does not provide explicit locks and does not handle multi-threaded or multi-process concurrency. If multiple threads or multiple process workers exist, each wrapper instance (per thread/process) may run hooks independently.
- If a hook raises an exception, that exception is not caught by the wrapper and will propagate to the caller; the _started flag is already set before hooks are awaited, so a failing hook leaves _started True (no automatic retry).

## Method Map:
flowchart LR
    A[ASGI server calls wrapper] --> B{_started?}
    B -- False --> C[set _started = True]
    C --> D[for each hook in on_startup: await hook()]
    D --> E[await wrapped asgi(scope, receive, send)]
    B -- True --> E
    E --> F[return wrapped app response]

(Interpretation: first call runs setup path, subsequent calls forward directly to wrapped app.)

## Raises:
- AssertionError: Raised by __init__ if on_startup is not a list (constructor asserts isinstance(on_startup, list)).
- Any exception raised by a startup hook: If a hook raises while being awaited, that exception propagates out of the wrapper and will interrupt the handling of the first request. There is no internal catch or retry logic.
- Any exception raised by the wrapped ASGI app will propagate as normal.

## Example (prose):
1. Prepare an existing ASGI application (callable with signature await app(scope, receive, send)).
2. Define several asynchronous initialization callables (startup hooks) that accept no arguments. Each hook performs whatever setup is needed (e.g., populating caches, warming connections) and returns when done.
3. Create an AsgiRunOnFirstRequest instance by passing the ASGI app and the list of hooks.
4. Provide this wrapper object to your ASGI server instead of the raw app. On receiving the first HTTP request, the server will trigger the wrapper; the wrapper will run each hook sequentially (awaiting each) and then forward the request to the wrapped app. Subsequent requests will be forwarded immediately.

Notes:
- Because the constructor demands a list, callers that build dynamic hook lists must ensure the final value passed is a list (not a tuple or other sequence).
- If you need startup hooks run at process start rather than on first request, do not use this class; instead run hooks at process boot (e.g., using server lifecycle events).

### `datasette.utils.asgi.AsgiRunOnFirstRequest.__init__` · *method*

## Summary:
Initialize the wrapper by storing the wrapped ASGI application and the list of startup hooks, asserting the hooks container is a list, and setting the internal _started flag to False.

## Description:
Known callers and invocation context:
- Called by application setup code that wraps an existing ASGI application with this helper (e.g., when constructing the server application object to hand to an ASGI server).
- Typically invoked once during process/app configuration time, before any ASGI scope is handled.
- Test harnesses or factory functions that produce an ASGI app wrapper may also instantiate this class.

Why this logic is a separate initializer:
- Encapsulates and enforces the minimal invariants for the wrapper (must receive a list for on_startup; initial _started state).
- Keeps the object construction small and explicit so the run-on-first-request behavior (executing hooks on first request) is implemented elsewhere in the class without conflating initialization logic with runtime handling.
- Enables callers to validate that they passed a concrete list container, preventing accidental use of other sequence types (e.g., tuple) when the implementation relies on list semantics.

## Args:
    asgi (callable): The wrapped ASGI application. Expected call signature: await asgi(scope, receive, send). Required; no default.
    on_startup (list): Required. A Python list object whose elements are asynchronous startup hook callables (no-argument callables that return awaitables or are coroutines). The constructor asserts that this argument is an instance of list; the contents are not validated here.

## Returns:
    None

## Raises:
    AssertionError: Raised if on_startup is not an instance of list (triggered by isinstance(on_startup, list) assertion).
    (No other exceptions are raised by this method itself; attribute assignment could raise only in exceptional object states, which is not expected in normal usage.)

## State Changes:
    Attributes READ:
        - (none) The initializer does not read any pre-existing self attributes.
    Attributes WRITTEN:
        - self.asgi: set to the provided asgi callable.
        - self.on_startup: set to the provided on_startup list.
        - self._started: initialized to False.

## Constraints:
    Preconditions:
        - The caller must supply a list object for on_startup (the constructor enforces this with an assertion).
        - asgi should be a callable that follows the ASGI call signature; this is a semantic requirement but not enforced by the constructor.
    Postconditions:
        - After return, self.asgi references the provided asgi callable.
        - After return, self.on_startup references the provided list object.
        - After return, self._started is False, indicating startup hooks have not yet been executed for this instance.

## Side Effects:
    - No I/O, blocking operations, or external service calls occur.
    - Mutates only the new instance's attributes (self.asgi, self.on_startup, self._started).
    - May raise AssertionError immediately if on_startup is not a list.

### `datasette.utils.asgi.AsgiRunOnFirstRequest.__call__` · *method*

## Summary:
Runs configured startup hooks once (on the first invocation) and then delegates the ASGI call to the wrapped application; updates the wrapper's started flag to reflect that startup has been attempted.

## Description:
This method is the asynchronous ASGI callable entrypoint for AsgiRunOnFirstRequest instances. It is invoked by an ASGI server (for example, uvicorn/hypercorn) when a new connection or request is being processed and the server dispatches to the application object.

On its first invocation it:
- Marks the wrapper as started by setting the internal _started flag to True (this happens before running hooks).
- Iterates over the list self.on_startup and awaits each hook callable in order.

After handling startup hooks (or if startup has already been attempted), it forwards the call to the wrapped ASGI application stored in self.asgi by awaiting self.asgi(scope, receive, send) and returning that result.

Why this is its own method:
- The method implements the ASGI application protocol (callable(scope, receive, send)), so it must exist as the awaitable entrypoint an ASGI server calls.
- It encapsulates the "run-on-first-request" lazy-start behavior so that startup hooks are executed automatically and exactly from the same ASGI entry point used by the server, keeping startup logic separate from the main application code.

Known callers and lifecycle stage:
- Called by ASGI servers (uvicorn, hypercorn, etc.) when dispatching a connection/request to this application object.
- Invoked each time the ASGI server hands an incoming scope to this application; startup hooks run only during the first such invocation (subject to the concurrency caveats below).

## Args:
    scope (dict): The ASGI connection scope dictionary describing the connection (type, path, headers, etc.) as defined by the ASGI spec.
    receive (Callable[[], Awaitable[dict]]): Async callable used to receive events from the server (awaitable that yields incoming events).
    send (Callable[[dict], Awaitable[None]]): Async callable used to send events back to the server (awaitable that accepts outgoing events).

## Returns:
    Any: The value returned by awaiting self.asgi(scope, receive, send). In typical ASGI applications this is None; the wrapper simply returns whatever the inner ASGI application returns.

## Raises:
    Any exception raised by a startup hook: If any await hook() raises, that exception propagates out of this method to the caller.
    Any exception raised by the wrapped ASGI application: Exceptions from self.asgi(scope, receive, send) propagate unchanged.
    TypeError (or RuntimeError) on non-awaitable hooks: If a hook is a synchronous function (not returning an awaitable) then awaiting its result will raise a TypeError (or another await-related exception) which will propagate.

## State Changes:
    Attributes READ:
        self._started
        self.on_startup
        self.asgi
    Attributes WRITTEN:
        self._started (set to True on the first code path that executes the startup logic)

## Constraints:
    Preconditions:
        - The instance must have been constructed with on_startup asserted as a list (the constructor enforces this).
        - Each element in self.on_startup should be a callable that returns an awaitable when called (i.e., an async function or callable that returns an awaitable). If hooks are not awaitable, awaiting them will raise.
        - The wrapped application assigned to self.asgi must itself be a valid ASGI application (an async callable accepting scope, receive, send).

    Postconditions:
        - After the first invocation of this method (even if one of the startup hooks raises), self._started will be True because the flag is set before awaiting hooks.
        - Startup hooks will not be invoked again on subsequent calls once _started is set to True (note exceptions during hooks do not cause retries).

## Side Effects:
    - Runs arbitrary code in the startup hooks (each hook may perform I/O, register global state, connect to services, etc.). Those effects are external to this object and may persist across requests.
    - Delegates to the wrapped ASGI application which may perform further I/O and side effects.
    - Exceptions from hooks or the wrapped app are not swallowed; they propagate to the ASGI server.

## Concurrency notes / gotchas:
    - The class uses a simple boolean flag to guard one-time startup execution. There is no internal synchronization (locks). Under concurrent first requests it is possible (depending on scheduling) for more than one invocation to interleave such that more than one coroutine begins startup behavior (though the assignment of _started occurs before awaiting hooks, so subsequent invocations that see _started True will skip running hooks). If strict, race-free single execution of startup hooks in highly concurrent environments is required, ensure startup is performed before concurrency (for example, run hooks during process startup) or add external synchronization.

