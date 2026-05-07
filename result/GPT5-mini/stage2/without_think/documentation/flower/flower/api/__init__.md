# `__init__.py`

## `flower.api.__init__.BaseApiHandler` · *class*

## Summary:
A Tornado request handler base class for programmatic API endpoints that enforces the application's authentication policy on every request and produces concise, machine-friendly error responses instead of HTML pages.

## Description:
BaseApiHandler subclasses views.BaseHandler and is intended for API routes consumed by programmatic clients (HTTP APIs). It enforces an application-level authentication requirement during the request preparation step and simplifies error responses so they contain only a short message (when available) rather than rendered HTML error pages.

Primary responsibilities:
- Enforce that API endpoints are not accessible without authentication unless explicitly enabled via an environment variable.
- Provide a compact error-response behavior appropriate for API clients by overriding BaseHandler.write_error.

When to instantiate:
- Register BaseApiHandler (or a subclass) with the Tornado application route table. Tornado creates a handler instance per incoming request; there are no other factories in this module.

Why this abstraction exists:
- BaseHandler is geared toward browser-facing routes (renders HTML pages and debug traces). BaseApiHandler separates API-oriented behavior (auth enforcement and minimal error messages) from UI-oriented behavior, making API handlers consistent and predictable for clients.

## State:
This class adds no persistent attributes; it relies on inherited RequestHandler state. Relevant externally-managed state and invariants:

- application (inherited)
  - application.options must exist and expose:
    - options.basic_auth: truthy/falsy or iterable; presence denotes that Basic Auth is configured for the application.
    - options.auth: truthy/falsy (e.g., regex or other auth indicator); presence denotes that authenticated sessions (OAuth2/secure cookie) are expected.
  - These options are part of the application's configuration and are read-only from the handler's perspective.

- Environment variable FLOWER_UNAUTHENTICATED_API:
  - Read using os.environ.get('FLOWER_UNAUTHENTICATED_API') or the literal string "false" when not present.
  - Parsed using utils.strtobool which accepts the following case-insensitive values:
    - Truthy: 'y', 'yes', 't', 'true', 'on', '1' — strtobool returns integer 1 for these.
    - Falsey: 'n', 'no', 'f', 'false', 'off', '0' — strtobool returns integer 0 for these.
  - If the environment variable is missing, the code supplies the string "false" so strtobool receives "false" and returns 0 (falsey).
  - If the value is present but not one of the accepted strings, strtobool raises ValueError which is not caught inside prepare and therefore will propagate out of the handler.

Method-specific invariants:
- prepare must either complete successfully (allowing dispatch to HTTP method handlers) or raise a tornado.web.HTTPError(401) when unauthenticated API access is not permitted.
- write_error must set the response status and finish the request on every call; if a log_message exists in the provided exc_info it will be written to the response body first.

## Lifecycle:
Creation:
- Instances are created by Tornado when a matched route references this handler class. No custom constructor arguments are required beyond the standard Tornado RequestHandler initialization.

Typical per-request sequence:
1. Tornado constructs a new handler instance for the request and calls prepare().
2. prepare():
   - Reads FLOWER_UNAUTHENTICATED_API from the environment (defaulting to "false" when absent).
   - Converts the string value to boolean-like integer via strtobool.
   - Checks application.options.basic_auth and application.options.auth.
   - If neither basic_auth nor auth is truthy and FLOWER_UNAUTHENTICATED_API is not truthy, raises tornado.web.HTTPError(401) with a specific message.
3. If prepare returns normally, Tornado dispatches to the handler's HTTP method (get/post/put/...).
4. If an exception occurs during dispatch, Tornado calls write_error(status_code, **kwargs) on the handler:
   - write_error expects (but does not enforce) that kwargs contains exc_info in the conventional (exc_type, exc_value, traceback) tuple format.
   - If exc_info is present and exc_info[1].log_message is truthy, write_error writes that message into the response body.
   - Then it sets the HTTP status to status_code and finishes the response.

Destruction:
- No special cleanup; handler instances are discarded after the request finishes. There are no resources opened by BaseApiHandler that require manual release.

Sequencing constraints:
- prepare must run before HTTP method handlers; bypassing prepare would skip the auth enforcement for API routes.
- write_error assumes an exc_info tuple for extracting a log_message; if exc_info is missing or malformed, attribute/sequence access errors may occur.

## Method Map:
graph LR
    A[Tornado constructs handler instance] --> B[prepare()]
    B -->|passes| C[HTTP method (get/post/put/...)]
    B -->|raises HTTPError(401)| D[Tornado error handling -> write_error(401, exc_info=...)]
    C -->|raises| D
    D --> E[write exc_info[1].log_message if present]
    D --> F[set_status(status_code) & finish()]
    C --> G[normal response via write/set_status/finish]

## Raises:
- tornado.web.HTTPError(401)
  - Raised by prepare when:
    - application.options.basic_auth is falsy/absent AND application.options.auth is falsy/absent AND FLOWER_UNAUTHENTICATED_API is not set to a strtobool-recognized truthy value.
  - The HTTPError message text is exactly:
    "FLOWER_UNAUTHENTICATED_API environment variable is required to enable API without authentication"

- ValueError
  - Propagates from utils.strtobool when FLOWER_UNAUTHENTICATED_API is present but has an unrecognized value. This is not caught in prepare and therefore will result in an uncaught exception unless the application intercepts it.

- TypeError / AttributeError (possible)
  - write_error uses kwargs.get('exc_info') and then accesses exc_info[1].log_message without checking for None or structure. If exc_info is None or not a tuple/list with index 1, or exc_info[1] lacks log_message, attribute or sequence access errors may occur.

## Example (usage outline without source-level definitions):
1. Configure your Tornado application so that application.options exposes basic_auth and/or auth when you want authenticated API access.
2. If you want to permit unauthenticated API access, set the environment variable FLOWER_UNAUTHENTICATED_API to a recognized truthy string (for example "true" or "1"). If the variable is absent, the handler treats it as "false".
3. Register a subclass of BaseApiHandler for API routes in the Tornado routing table so Tornado will instantiate it per request.
4. Per request:
   - prepare enforces auth policy and will raise HTTPError(401) with the precise message above if unauthenticated access is disallowed.
   - If an exception is raised and Tornado calls write_error, clients receive the short log_message text (if provided) and the proper HTTP status code; no HTML error page is rendered.

Practical advice:
- Avoid setting FLOWER_UNAUTHENTICATED_API to non-standard values; an unrecognized string will raise ValueError and likely result in a 500-level error.
- If you rely on write_error's log_message behavior, ensure exceptions raised by your handlers set the log_message attribute (tornado.web.HTTPError supports this) or provide exc_info in the conventional form.
- For browser-facing routes that require HTML error pages, continue to use BaseHandler (not BaseApiHandler).

### `flower.api.__init__.BaseApiHandler.prepare` · *method*

## Summary:
Checks whether API access is allowed for the incoming request by verifying either configured authentication on the application or an environment flag; raises an HTTP 401 error to block requests when neither is present. This may stop request processing (prevents handler methods from running) but does not modify handler state.

## Description:
This method is invoked as part of the request handling lifecycle (it is an override of the Tornado RequestHandler prepare hook used by BaseApiHandler). It runs at the start of handling each request, before the request handler's HTTP method (get/post/etc.) is executed, to enforce that API endpoints are only accessible when authentication is configured or when explicitly enabled via an environment variable.

Known callers and lifecycle stage:
- Tornado's request dispatch pipeline calls prepare() on a request handler instance immediately before the handler's HTTP method (e.g., get, post). Thus prepare() is executed once per incoming HTTP request handled by BaseApiHandler.

Why this is a separate method:
- Authentication gating is a cross-cutting concern that must run uniformly before any request-specific logic. Placing it in prepare() centralizes access control for all API handler methods, keeps per-method handlers free of repetitive checks, and leverages Tornado's lifecycle to short-circuit request processing when unauthorized.

## Args:
- None.

## Returns:
- None (implicitly returns None). If the method completes without raising, request processing continues to the handler's HTTP method.

## Raises:
- tornado.web.HTTPError(401, message):
    - Raised when BOTH of the following are true:
        1. Neither self.application.options.basic_auth nor self.application.options.auth are truthy (i.e., the application has no configured basic-auth or other auth option enabled).
        2. The environment variable 'FLOWER_UNAUTHENTICATED_API' is not set to an enabled/truthy value after conversion by utils.strtobool (the code fetches the value via os.environ.get('FLOWER_UNAUTHENTICATED_API') or "false" and passes it through strtobool).
    - The error uses HTTP status 401 and the message:
      "FLOWER_UNAUTHENTICATED_API environment variable is required to enable API without authentication"

## State Changes:
- Attributes READ:
    - self.application.options.basic_auth
    - self.application.options.auth
    - os.environ['FLOWER_UNAUTHENTICATED_API'] (read via os.environ.get)
- Attributes WRITTEN:
    - None — the method does not modify any self.<attr> fields.

## Constraints:
- Preconditions:
    - self.application and self.application.options must exist and be accessible on the handler instance; options must expose the attributes basic_auth and auth. If these are missing or accessing them raises an AttributeError, the prepare call will propagate that exception (the method itself does not guard these accesses).
    - utils.strtobool must be available and callable as imported; it is used to coerce the environment value to a boolean-like value.
- Postconditions:
    - If the method returns normally (no exception), then at least one of the following is true:
        - self.application.options.basic_auth is truthy, or
        - self.application.options.auth is truthy, or
        - The environment variable FLOWER_UNAUTHENTICATED_API is set to a value that strtobool interprets as enabling the unauthenticated API.
    - If the method raises tornado.web.HTTPError(401,...), request processing is halted and Tornado will send the corresponding HTTP error response to the client.

## Side Effects:
- I/O / External interactions:
    - Reads the process environment via os.environ.get('FLOWER_UNAUTHENTICATED_API').
- External service calls:
    - Calls utils.strtobool to interpret the environment variable.
- Observable behavior to the outside world:
    - May raise tornado.web.HTTPError(401), which results in a 401 HTTP response being sent to the client and prevents further handler processing.
- No persistent state is modified and no external network calls are made by this method itself.

### `flower.api.__init__.BaseApiHandler.write_error` · *method*

## Summary:
Sets the HTTP status, optionally writes an error message extracted from exc_info into the response body, and finalizes the response so no further writes are allowed.

## Description:
This method is intended to be invoked during an HTTP request error handling path (for example, by a web framework or by application-level error handling code when an error needs to be returned to the client). It extracts an error message from the exception information supplied in kwargs and, if present, writes that message into the response body before setting the response status and finishing the response.

Known callers and context:
- Typically called by an HTTP request handler's error handling path (e.g., the framework's error dispatch when an exception occurs inside request handling).
- Called at the end of error handling to ensure the client receives a status and optional text and that the response stream is finalized.

Why this is a separate method:
- Centralizes the logic for producing an HTTP error response (extracting a short message from exception info, writing it, setting status, and finishing).
- Keeps error-finalization behavior consistent across handlers and avoids duplicating the finalization steps in multiple places.

## Args:
    status_code (int):
        - The HTTP status code to set on the response (e.g., 400, 404, 500).
        - The method does not validate the numeric range; the value is forwarded to self.set_status(status_code).
    **kwargs:
        - Optional keyword arguments; the method inspects 'exc_info' if provided.
        - exc_info should be a tuple-like exception info object (as returned by sys.exc_info()) or another container where index 1 is an exception instance that exposes a log_message attribute.

## Returns:
    None
    - The method does not return a value. Its effect is to mutate the response (write data, set status) and finalize it.
    - After this method returns the response is finished; further writes are generally not accepted by the handler.

## Raises:
    TypeError:
        - If kwargs does not contain 'exc_info' or if exc_info is None such that attempting exc_info[1] raises a TypeError (for example, if exc_info is None).
    IndexError:
        - If exc_info is a sequence with no index 1.
    AttributeError:
        - If exc_info[1] exists but the object at that position does not have a log_message attribute.
    Any exception raised by:
        - self.write(...), self.set_status(...), or self.finish() — these underlying calls may raise framework-specific exceptions depending on their implementations and the handler state.

## State Changes:
Attributes READ:
    - None of the handler's explicit data attributes are read by name in the implementation. The method does call instance methods (self.write, self.set_status, self.finish), but it does not access self.<attr> fields directly.

Attributes WRITTEN:
    - None of the handler's explicit data attributes are directly assigned. Instead, the method mutates the handler's response state via method calls:
        - response body buffer (via self.write(log_message))
        - HTTP status (via self.set_status(status_code))
        - finalization flag / connection state (via self.finish())

## Constraints:
Preconditions:
    - The caller should supply status_code as an integer acceptable to the underlying set_status implementation.
    - If an error message is expected to be written, kwargs should include an 'exc_info' whose index 1 is an exception-like object with a log_message attribute.

Postconditions:
    - The handler's HTTP status has been set to status_code.
    - If exc_info was provided and exc_info[1].log_message is truthy, that message has been written to the response body.
    - The response has been finalized (self.finish() called), so no further writes should be performed.

## Side Effects:
    - I/O: Writes to the HTTP response body (via self.write); modifies the outgoing HTTP status line (via self.set_status); finalizes the response/connection (via self.finish).
    - No external services are called directly by this method, but the side effects interact with the web server / framework I/O machinery.
    - Because the method calls self.finish(), it signals the end of the response lifecycle; subsequent operations that assume the response is still open may fail.

