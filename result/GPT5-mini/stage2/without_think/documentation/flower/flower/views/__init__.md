# `__init__.py`

## `flower.views.__init__.BaseHandler` · *class*

*No documentation generated.*

### `flower.views.__init__.BaseHandler.set_default_headers` · *method*

## Summary:
When the application's authentication options are not enabled, write three CORS-related HTTP response headers into the handler's response state, affecting the outgoing headers for the current request.

## Description:
This method inspects application-level options and, if both basic_auth and auth are falsy, sets three Access-Control response headers by calling self.set_header. The logic is concentrated here so all handlers that use this BaseHandler implementation can rely on a single place for default CORS headers.

Known callers / invocation context:
- There are no explicit callers shown in the local source. The method is implemented in a style consistent with Tornado's RequestHandler hook named set_default_headers and is therefore intended to be used as that hook when BaseHandler is used as a Tornado request handler. When used as such, the framework will invoke this method as part of the request handling flow.
- Developers may also call it explicitly on handler instances, but the method body does not depend on any call-site context beyond self and self.application.options.

Why this logic is its own method:
- Centralizes default HTTP header configuration in a single overridable location.
- Matches the common Tornado extension point for setting per-request default headers, allowing derived handlers to inherit or override CORS behavior without duplicating header logic.

## Args:
None (only self is used).

## Returns:
None.

## Raises:
- AttributeError: If self.application or self.application.options does not exist, or if options lacks attributes basic_auth or auth, attribute access will raise AttributeError.
- No exceptions are explicitly caught within the method.

## State Changes:
Attributes READ:
- self.application
- self.application.options
- self.application.options.basic_auth
- self.application.options.auth

Attributes WRITTEN:
- No direct assignments to self.<attr> are performed.
- Indirectly mutates the handler's response headers via calls to:
    - self.set_header("Access-Control-Allow-Origin", "*")
    - self.set_header("Access-Control-Allow-Headers", "x-requested-with,access-control-allow-origin,authorization,content-type")
    - self.set_header('Access-Control-Allow-Methods', ' PUT, DELETE, OPTIONS, POST, GET, PATCH')
  (These calls update the response header collection managed by the handler.)

## Constraints:
Preconditions:
- self must provide a set_header(name, value) method.
- self.application must exist and have an options attribute.
- self.application.options must expose attributes named basic_auth and auth whose truthiness can be tested.

Postconditions:
- If both basic_auth and auth are falsy, the three headers listed under State Changes will be present in the response header collection with the exact string values shown (note the leading space before "PUT" in the Access-Control-Allow-Methods value).
- If either basic_auth or auth is truthy, this method makes no changes to the response headers.

## Side Effects:
- Mutates the handler's outgoing HTTP response headers via self.set_header; this affects what is ultimately sent to the client.
- No network I/O, filesystem I/O, logging, or calls to external services occur within this method.

### `flower.views.__init__.BaseHandler.options` · *method*

## Summary:
Responds to HTTP OPTIONS requests with a 204 No Content status and terminates the request/response cycle, producing no response body.

## Description:
This method is the explicit handler for HTTP OPTIONS requests on the BaseHandler (a subclass of tornado.web.RequestHandler). It is invoked by the Tornado request-dispatching machinery when an incoming request uses the OPTIONS method (typically for CORS preflight requests). Placing this logic in its own method provides a clear, overrideable hook for subclasses that need to customize OPTIONS handling (for example to add different headers or to return a different status/body) without modifying the request-dispatching flow or other HTTP method handlers.

Known callers and context:
- The Tornado framework calls this method during the request handling lifecycle when an OPTIONS HTTP request is routed to this handler class.
- Typical usage context: handling CORS preflight checks or clients probing allowed methods for a resource prior to sending a cross-origin request.

Why separate:
- Keeps CORS / OPTIONS behavior isolated and easy to override.
- Ensures a consistent minimal response (204 + finished) for preflight requests without duplicating logic in multiple endpoints.

## Args:
    *_, **__ : variadic positional and keyword arguments
        - Type: arbitrary positional and keyword arguments passed through by the dispatcher.
        - Behavior: ignored by the implementation; accepted to match the signature Tornado may call with, but not used.

## Returns:
    None
    - The method does not return a Python value. Instead it sets the HTTP response status and finalizes the response via the RequestHandler lifecycle. After calling this method the request is finished and no further response body is sent by this handler.

## Raises:
    - No exceptions are explicitly raised by this method.
    - Note: underlying tornado.web.RequestHandler methods (set_status, finish) may raise exceptions in abnormal runtime conditions; this method does not catch or translate such exceptions.

## State Changes:
    Attributes READ:
        - None of the handler's attributes are directly read by this method.
    Attributes WRITTEN:
        - No attributes on self are directly assigned.
    External response-state mutations (effects of calling methods):
        - Calls self.set_status(204) — sets the HTTP response status code to 204 (No Content).
        - Calls self.finish() — finalizes the HTTP response and ends request processing for this handler (causes Tornado to send the response to the client and run any on_finish hooks).

## Constraints:
    Preconditions:
        - Must be called on a valid RequestHandler instance during an active request lifecycle (i.e., within Tornado's request handling thread/context).
        - No assumptions are made about headers or application options; other methods (e.g., set_default_headers) may already have set response headers before this is called.
    Postconditions:
        - The HTTP response status is set to 204.
        - The response is finished: no further writes from this handler will be sent and the request-response cycle for this handler is complete.

## Side Effects:
    - Sends an HTTP response status (204) to the connected client and ends the response.
    - May trigger Tornado RequestHandler lifecycle hooks such as on_finish and any application-level logging or metrics tied to response completion.
    - No external I/O is performed by this method other than writing the HTTP response via Tornado's request machinery.

### `flower.views.__init__.BaseHandler.render` · *method*

## Summary:
Augments the template rendering context with helper functions and a url_prefix, then delegates to the parent RequestHandler.render to produce the response.

## Description:
This method is invoked during HTTP request handling whenever a handler needs to render a template to produce a response. Known callers in this codebase include:
- BaseHandler.write_error — used to render error pages (e.g., '404.html', 'error.html').
- Any subclass of BaseHandler or other code handling requests that calls self.render(...) to render templates during request processing.

It exists as its own method to centralize and guarantee a consistent template context for all templates rendered by handlers that inherit from BaseHandler. The method injects a set of helper functions (from the imported template module) and a global url_prefix into the template keyword arguments so templates can rely on these helpers without each handler having to supply them.

## Args:
    *args: tuple
        Positional arguments passed through to tornado.web.RequestHandler.render. Typically the first positional argument is the template name (str), followed by additional positional arguments supported by the underlying render implementation.
    **kwargs: dict
        Keyword arguments passed as the template context to the renderer. Before delegation, this method adds:
          - One entry per function found in the utils.template module: name (str) -> callable
          - 'url_prefix' (str) -> application.options.url_prefix
        Caller-supplied kwargs must not use any names that collide with the names of functions exported from the utils.template module (see Raises).

## Returns:
    The return value of super().render(*args, **kwargs). In Tornado, RequestHandler.render typically returns None after writing the rendered output to the response buffer, so callers should not rely on a meaningful return value.

## Raises:
    AssertionError:
        If any key in the incoming kwargs collides with a function name discovered in the utils.template module. The collision check collects the function names from inspect.getmembers(template, inspect.isfunction) and asserts the intersection with set(kwargs.keys()) is empty. Note: assert statements can be disabled when Python is run with optimization flags, so collisions might not raise in optimized runs.
    AttributeError (implicit):
        If self.application or self.application.options is missing or does not expose url_prefix, attribute access will raise; this is an implicit precondition failure rather than an explicit raise from this method.
    Any exceptions raised by super().render:
        Errors raised by the underlying template engine or Tornado rendering (e.g., template not found, template rendering errors) propagate to the caller.

## State Changes:
    Attributes READ:
        self.application
        self.application.options
    Attributes WRITTEN:
        None — this method does not assign to any self.<attr> attributes.

## Constraints:
    Preconditions:
        - self.application must be present and must have an .options attribute with a url_prefix attribute.
        - kwargs must not contain keys that match any function name in the utils.template module (to avoid name collision).
    Postconditions:
        - The provided template context passed to the renderer includes:
            * All original kwargs (except that an assertion prevents name collisions)
            * All functions discovered in the utils.template module as callable entries keyed by their function names
            * 'url_prefix' set to self.application.options.url_prefix
        - The underlying render is invoked with the augmented context; the response output buffer will have been updated per Tornado's rendering behavior.

## Side Effects:
    - Calls super().render(*args, **kwargs), which performs template rendering and writes output to the HTTP response buffer (I/O to the client when the request is finished).
    - No mutation of handler instance attributes occurs.
    - The method depends on the utils.template module (imported at module level) and inspect.getmembers to gather functions; it does not modify that module.

### `flower.views.__init__.BaseHandler.write_error` · *method*

## Summary:
Render or write an HTTP error response and set related headers/status based on the provided HTTP status code, finalizing the handler response where appropriate.

## Description:
Called by the Tornado request-handling/error pipeline when an HTTP error or exception needs to be presented to the client. Typical callers are Tornado internals (RequestHandler.write_error) during exception handling or when an error status is raised.

The method centralizes presentation logic for common error statuses so all handlers inheriting BaseHandler present errors consistently (HTML templates for user-facing pages, plain-text for programmatic clients, and authentication challenges for protected endpoints). Keeping this logic in one method avoids duplication across many handlers and lets templates and debug behavior be controlled in one place.

Behavior by status:
- 404 or 403:
  - If kwargs contains exc_info and exc_info[0] == tornado.web.HTTPError, extracts exc_info[1].log_message to include as message.
  - Calls self.render('404.html', message=message).
  - Does not explicitly call self.set_status in this branch (status remains whatever it was prior to this call unless render/super().render alters it).
- 500:
  - Expects kwargs['exc_info'] to be the (exc_type, exc_value, traceback) tuple and uses traceback.format_exception(*kwargs['exc_info']) to build a string error_trace.
  - Calls self.render('error.html', debug=self.application.options.debug, status_code=status_code, error_trace=error_trace, bugreport=bugreport()).
  - Does not explicitly call self.set_status here.
- 401:
  - Calls self.set_status(status_code).
  - Sets 'WWW-Authenticate' header to 'Basic realm="flower"'.
  - Calls self.finish('Access denied') to finalize the response body.
- Default (any other status):
  - If kwargs contains exc_info and exc_info[0] == tornado.web.HTTPError, extracts exc_info[1].log_message, sets 'Content-Type' to 'text/plain', and writes the message via self.write(str(message)).
  - Calls self.set_status(status_code) and self.finish() to finalize the response.

## Args:
    status_code (int): The HTTP status code to present (e.g., 404, 500, 401). The method branches behavior on this value.
    **kwargs: Optional, framework-provided keyword args. Recognized key:
        exc_info: Typically the (exc_type, exc_value, traceback) tuple from sys.exc_info() or similar. Used as follows:
            - For 404/403 and default branches: inspected at index 0 to check for tornado.web.HTTPError, and index 1's log_message is used when present.
            - For 500: unpacked and passed to traceback.format_exception; required for a useful error_trace.

## Returns:
    None. The method writes to the HTTP response via render/write/finish and does not return a value.

## Raises:
    KeyError: If status_code == 500 and kwargs lacks 'exc_info', accessing kwargs['exc_info'] raises KeyError.
    TypeError or IndexError: If kwargs['exc_info'] is present but is not indexable/unpackable as expected, indexing or unpacking operations may raise these.
    AttributeError: If kwargs['exc_info'][1] exists but lacks a log_message attribute and the code accesses it for 404/403 or default branches.
    Any exception raised by traceback.format_exception, bugreport(), self.render(), self.write(), self.set_status(), self.set_header(), or self.finish() may propagate; the method does not catch exceptions raised during rendering/formatting in these branches.

## State Changes:
Attributes READ:
    - self.application.options.debug (for the 500 'error.html' template).
    - self.application (to access options).
    - module-level bugreport() (called in 500 branch).
    - module-level traceback.format_exception (used in 500 branch).
    - tornado.web.HTTPError (used for comparisons with exc_info[0]).
Methods CALLED (affect response state):
    - self.render(...) (called for 404/403 and 500 to produce HTML responses).
    - self.set_status(status_code) (called for 401 and the default branch).
    - self.set_header(...) (called to set 'WWW-Authenticate' for 401, and 'Content-Type' for text responses in default branch).
    - self.write(...) (called in default branch when exc_info indicates an HTTPError to write a plain-text message).
    - self.finish(...) (called in 401 and default branches to finalize the response).

Attributes WRITTEN / Mutated (via method calls):
    - HTTP response status: explicitly set in 401 and default branches via self.set_status(status_code).
    - HTTP response headers: may be mutated by self.set_header calls (WWW-Authenticate or Content-Type).
    - HTTP response body: produced via self.render or self.write; 401 finishes with literal 'Access denied'.

## Constraints:
Preconditions:
    - status_code should be an integer representing an HTTP status.
    - For the 500 branch to work without error, kwargs must contain a valid exc_info tuple (exc_type, exc_value, traceback).
    - If exc_info is provided and used for log_message extraction, exc_info must be indexable and exc_info[1] should have a log_message attribute when it represents a tornado.web.HTTPError.

Postconditions:
    - The response will have been populated: either rendered as HTML (404/403/500 branches) or written/finished (401 or default branch).
    - For 401 and default branches the response status will be explicitly set to status_code and finish() will have been called.
    - For 404/403 and 500 branches the method calls render(...) to generate the response body; the HTTP status may remain unchanged by this method unless the rendering layer sets it.

## Side Effects:
    - Network I/O: writes to the HTTP response stream by calling render/write and may finalize with finish.
    - Header changes: may add 'WWW-Authenticate' or 'Content-Type' headers.
    - Diagnostic work: calls bugreport() (500 branch) and traceback.format_exception which may allocate memory and collect diagnostic strings.
    - Exceptions from missing/malformed kwargs['exc_info'] or from called helper functions can propagate out of this method and be handled by higher-level Tornado error handling.

### `flower.views.__init__.BaseHandler.get_current_user` · *method*

## Summary:
Determine and return the authenticated user for the current request (or True when authentication is globally disabled); enforces Basic HTTP auth when configured and validates an application cookie against an auth regex when OAuth-style auth is enabled. Does not mutate handler state.

## Description:
This method centralizes request authentication logic and is intended to be called by the Tornado request lifecycle (for example, by the tornado.web.authenticated decorator or other handler code) to determine whether the incoming request is authenticated and to obtain the current user's identifier.

Callers and invocation context:
- tornado.web.authenticated decorator and any handler code that needs the current user; invoked during request handling before protected handler methods execute.
- When basic_auth is configured on the application, this method enforces Basic HTTP authentication by validating the Authorization header.
- When application.options.auth is falsy (authentication disabled), the method returns True immediately to indicate no authentication checks are required.
- When application.options.auth is truthy, this method checks the secure cookie named 'user' and validates it using the regex in application.options.auth.

Rationale for separate method:
- Overriding get_current_user is the standard Tornado pattern for centralizing authentication and allowing other parts of the framework (e.g., @authenticated) to rely on a single point of truth for user identity.
- Consolidates Basic Auth and cookie/regex-based checks in one place so different handlers and decorators can reuse the same logic.

## Args:
This method is an instance method and takes no explicit arguments beyond self.

## Returns:
- bool | str | None
    - True: returned when application.options.auth is falsy (authentication is disabled globally). This indicates "no authentication required".
    - str: the authenticated user identifier (decoded from the secure cookie) when:
        * a secure cookie 'user' exists, and
        * after decoding (if necessary) it matches the regular expression in application.options.auth (via re.match).
      The returned str is the decoded cookie value (UTF-8).
    - None: returned when authentication is enabled (application.options.auth truthy) but there is no valid cookie or the cookie does not match the configured auth regex.

Edge-case return notes:
- The method never returns False. Absence of authentication is indicated by None.
- When Basic Auth is configured and validated successfully, the method continues into the OAuth2/cookie branch (it does not directly return a user identifier from Basic Auth). If application.options.auth is falsy, True is returned even if Basic Auth was validated.

## Raises:
- tornado.web.HTTPError(401)
    - Raised when Basic HTTP authentication is configured (application.options.basic_auth is truthy) and any of the following occur:
        * The Authorization header is missing or does not contain two whitespace-separated tokens (split() raises ValueError).
        * The first token is not the string 'Basic'.
        * The base64-decoded credentials cannot be validated against any stored credential in application.options.basic_auth (no stored_credential yields hmac.compare_digest true).
    - The ValueError from header parsing or Unicode decode errors during base64 decoding are caught and normalized to HTTPError(401) (the code explicitly catches ValueError and raises the 401). Note: some base64 decoding errors (e.g., binascii.Error for invalid base64 input) are not caught explicitly and will propagate as their native exception types.

## State Changes:
Attributes READ:
- self.application.options.basic_auth (used to decide whether to enforce Basic Auth)
- self.request.headers (reads Authorization header)
- self.application.options.auth (used to decide whether OAuth/cookie checks are required and as a regex for matching)
- self.get_secure_cookie('user') (invoked to retrieve the secure cookie; value may be bytes or str)
- Any items inside stored credentials in application.options.basic_auth (iterated for comparison)
Attributes WRITTEN:
- None (this method does not assign to any self.<attr> fields)

## Constraints:
Preconditions:
- self.application and self.application.options must exist and expose:
    * basic_auth: an iterable of credential strings (or falsy to disable Basic Auth)
    * auth: a truthy regex string or falsy to disable auth checks
- self.request.headers must be a mapping providing an 'Authorization' header when Basic Auth is used.
- If Basic Auth is configured, stored credentials in application.options.basic_auth are expected to be strings that can be compared with the decoded credentials using hmac.compare_digest.

Postconditions:
- No mutation of handler state occurs.
- If Basic Auth is configured and fails, the method raises HTTPError(401).
- If application.options.auth is falsy, the method returns True.
- If application.options.auth is truthy and a secure cookie 'user' exists and matches the regex, the method returns the decoded string value of that cookie; otherwise it returns None.

## Side Effects:
- May raise tornado.web.HTTPError(401) which will trigger Tornado's error handling path (and may result in an HTTP 401 response and any associated write_error behavior).
- No I/O, network calls, or external service calls are made directly by this method.
- No external objects are mutated; the only observable effect (aside from return value or raised exception) is that raising HTTPError(401) will cause Tornado to send an authentication challenge to the client if not otherwise handled by the application.

### `flower.views.__init__.BaseHandler.get_argument` · *method*

## Summary:
Fetches a request argument, applies XSS-safe escaping if it's a text value, and optionally coerces it to a requested type; raises a 400 HTTPError when coercion fails (except when both the retrieved value and the supplied default are None).

## Description:
This method is the BaseHandler-specific override of Tornado's RequestHandler.get_argument. It is called by request-handling code (view methods and other handler logic) when retrieving a parameter from the current HTTP request (query string, POST body form, or path arguments as supported by Tornado). It centralizes two behaviours used across handlers:
- HTML/XHTML escaping of textual values to reduce cross-site scripting risks.
- Uniform typed conversion of argument values (including a boolean special-case using the project utility strtobool).

Keeping this logic in one place avoids duplicating escaping and conversion code in every handler and ensures consistent error handling (raising HTTP 400 for invalid user-supplied values).

Typical callers:
- Handler methods in this application that extract parameters from incoming requests during the request handling lifecycle (i.e., while processing a request in an instance of BaseHandler).

## Args:
    name (str):
        The name/key of the argument to retrieve from the request. Passed directly to the parent implementation.
    default (any, optional):
        Value to return if the argument is not present. Default value in the signature is an empty list (mutable) but callers typically pass None or a simple scalar. Note: the implementation disables the pylint warning for a dangerous default value; prefer passing an explicit immutable default when calling (for example, None or '').
    strip (bool, optional):
        If True (default), whitespace is stripped from the retrieved value by the parent implementation before further processing. Passed unchanged to the parent.
    type (callable or type, optional):
        If provided, used to coerce the retrieved value:
        - If type is bool, the code calls strtobool(str(arg)) which returns 1 or 0 (integers) for recognized boolean-like strings and raises ValueError for unrecognized values.
        - For any other callable/type, the code calls type(arg) and returns that result (or raises ValueError/TypeError on failure).

## Returns:
    any:
        - If the argument exists and no type coercion is requested: the value returned by Tornado's RequestHandler.get_argument (typically a str).
        - If the argument exists and type is provided:
            * For type=bool: returns int 1 or 0 (result of strtobool(str(arg))) on success.
            * For other types: returns the result of type(arg).
        - If the argument is absent and a default was supplied to this method (the default parameter), that default value is returned (after no further processing unless a type is requested and type conversion is applied to that default as well because the code passes default into super()).
        - Edge-case: when coercion raises ValueError or TypeError and both arg is None and default is None, the method returns None instead of raising an HTTPError.

## Raises:
    tornado.web.HTTPError(400):
        Raised when type conversion (type(arg)) fails with ValueError or TypeError — the error message is:
        "Invalid argument '{arg}' of type '{type_name}'"
        where {arg} is the (stringified) problematic value and {type_name} is type.__name__.
        Exception chaining is preserved (the original ValueError/TypeError is attached via "from").
    Other exceptions propagated from Tornado's parent implementation:
        - Any exceptions raised by super().get_argument (for example, Tornado's MissingArgumentError when an argument is missing and no default was provided) are propagated unchanged.

## State Changes:
    Attributes READ:
        - self.request (indirectly, via the call to super().get_argument which inspects the request/arguments)
    Attributes WRITTEN:
        - None. This method does not mutate self attributes.

## Constraints:
    Preconditions:
        - The request handling context must be active (this method should be called while processing a request on a RequestHandler instance).
        - `name` should be a valid key that the parent RequestHandler understands.
        - If `type` is provided and is not bool, it must be a callable that accepts the raw argument and either returns a converted value or raises ValueError/TypeError on invalid input.
        - When using type=bool: the code calls str(arg) and passes that to strtobool; strtobool expects a trimmed, case-insensitive textual token matching accepted true/false tokens. Leading/trailing whitespace will cause strtobool to raise ValueError (so callers should ensure values are appropriate or handle the HTTPError).
    Postconditions:
        - The returned value is either the original request argument (possibly escaped), or the result of successful type coercion.
        - If a string was returned (no type coercion), and it was non-empty, HTML-special characters have been escaped via tornado.escape.xhtml_escape to reduce XSS risk.
        - On conversion failure (ValueError/TypeError), an HTTP 400 is raised (except the special case where both arg and default are None).

## Side Effects:
    - Calls tornado.escape.xhtml_escape on string values (pure, no I/O).
    - Calls the project utility strtobool for boolean conversion (pure, no I/O).
    - May raise tornado.web.HTTPError(400) which will alter the request handling flow and result in an HTTP 400 response to the client.
    - No external I/O or mutation of global state is performed.

### `flower.views.__init__.BaseHandler.capp` · *method*

## Summary:
Return the Celery application object stored on the handler's application attribute.

## Description:
This accessor returns the value of self.application.capp so view code can interact with the Celery application instance used by the running Flower process.

Known callers and call-context:
- Request handler methods (e.g., get/post or other view helpers) implemented on BaseHandler subclasses call this accessor during request processing when they need to submit tasks, inspect workers, or query Celery state.
- Initialization or utility methods within view classes may use this accessor during lifecycle stages where the handler services a request or performs periodic operations.
This method is an explicit accessor so that access to the Celery app is centralized (easy to mock/override in tests) and so subclasses can override it if they need a different resolution strategy.

Why this is a separate method:
- Provides a consistent, single point of access to the Celery app.
- Enables easier unit testing and subclassing (tests can override capp to supply a fake app).
- Keeps call sites concise and avoids duplicating the attribute lookup expression across many methods.

## Args:
    None

## Returns:
    object: The value of self.application.capp. In a running Flower deployment this is typically an instance of celery.Celery (or a wrapper around it), but the method makes no guarantees beyond returning the stored attribute.

    Edge cases:
    - If self.application exists but its capp attribute is None, None will be returned.
    - If self.application.capp is present but not a Celery instance, that object will be returned as-is.

## Raises:
    AttributeError: If self has no attribute application, or if self.application has no attribute capp. This occurs because the method directly performs attribute access without guards.

## State Changes:
    Attributes READ:
        - self.application
        - self.application.capp (read via attribute access)
    Attributes WRITTEN:
        - None (this accessor does not mutate the handler or application)

## Constraints:
    Preconditions:
        - The handler instance (self) should have an application attribute.
        - The application attribute is expected to provide a capp attribute/property.

    Postconditions:
        - No mutation of self or external objects is performed.
        - The returned value equals the runtime value of self.application.capp at the time of the call.

## Side Effects:
    - None intrinsic to this method: no I/O, no network calls, and no mutation of external objects.
    - However, following use of the returned object elsewhere may cause side effects (task submission, network operations, etc.); those are not performed by this accessor itself.

### `flower.views.__init__.BaseHandler.format_task` · *method*

## Summary:
Return a task object formatted by an optional user-provided formatter from application.options, protecting the original by passing a shallow copy to the formatter and returning either the formatted result or the original task if formatting fails or no formatter is configured.

## Description:
This method centralizes the application-level hook that allows a user-provided callable to transform or annotate a task before it is used by handlers or rendered to clients. Typical callers are request-handling code paths in the web UI or API endpoints that prepare tasks for display or serialization (for example, list/detail views or handlers that build task payloads). It is implemented as a separate method to:
- Keep the formatting hook in one place so all handlers apply consistent formatting policy.
- Encapsulate exception handling and logging related to custom formatters.
- Ensure the original task is guarded by passing a shallow copy to user code to reduce accidental mutation of internal state.

## Args:
    task (Any): The task object to format. There are no enforced type constraints in this method — it accepts any object and returns whatever the formatter returns. The caller typically passes a domain Task object (an object with at least the attributes the rest of the system expects, e.g., uuid).

## Returns:
    Any: If no custom formatter is configured (application.options.format_task is falsy), the original task object is returned unchanged. If a custom formatter is configured and executes successfully, the method returns the formatter's return value (which may be the modified copy, a distinct object, or even None). If the formatter raises an exception, the original task (unchanged) is returned after logging the error.

## Raises:
    This method does not propagate exceptions raised during formatting: all exceptions thrown inside the formatter (or during the shallow copy) are caught and logged, and the original task is returned. One indirect risk:
    - If the logger call inside the exception handler attempts to access task.uuid but the provided task object lacks a uuid attribute, an AttributeError can be raised during logging (this is an implementation detail of the logging call and not of the formatting call).

## State Changes:
    Attributes READ:
        self.application.options.format_task — read to determine whether a custom formatter is configured and to obtain the callable.

    Attributes WRITTEN:
        None — this method does not modify any self.<attr> on the handler.

## Constraints:
    Preconditions:
        - self.application must be set and have an options attribute exposing format_task (which may be falsy or a callable).
        - The caller should expect a possibly different object type returned if a formatter is present.

    Postconditions:
        - The method guarantees that it will return either the original task (if no formatter is configured or if the formatter raised an exception) or the exact object returned by the formatter.
        - The original task passed by the caller will not be modified by this method itself; a shallow copy is provided to the formatter to reduce accidental mutation (note: shallow copy does not prevent mutation of nested/mutable attributes).

## Side Effects:
    - Calls the user-provided formatter callable (application.options.format_task) with a shallow copy of the task; the formatter may perform arbitrary work (mutations, I/O, network calls) and may return any object.
    - Logs an exception via the module-level logger (logger.exception) if the formatter or the copy operation raises an Exception. The log message attempts to include task.uuid; if task lacks that attribute, the logging call itself may raise an AttributeError.
    - No other I/O or persistent state changes are performed by this method.

### `flower.views.__init__.BaseHandler.get_active_queue_names` · *method*

## Summary:
Collects and returns a lexicographically sorted list of unique queue names known to the application, using worker-reported active queues first and falling back to Celery configuration when no worker-reported queues exist. This operation does not modify handler or application state.

## Description:
Behavior (step-by-step):
1. Initialize an empty set to accumulate queue names.
2. Iterate over self.application.workers.items(). For each worker info object:
   - Read info.get('active_queues', []) to obtain a sequence of queue descriptors.
   - For each queue descriptor, read queue['name'] and add that value to the set.
3. If the set is empty after checking all workers:
   - Read self.capp.conf.task_default_queue and include it (as a single-element set).
   - Read self.capp.conf.task_queues (may be None) and include q.name for each q where q.name is truthy.
   - Combine these into the set of queue names.
4. Return a Python list of the set contents sorted with Python's default string ordering (sorted(queues)).

Why a separate method:
- Centralizes the logic for obtaining the "active" queue names (runtime-reported + configuration fallback) so multiple views/handlers reuse consistent behavior without duplicating worker/config merging logic.
- Encapsulates error surface and expected environment (application.workers and Celery configuration) in a single, testable function.

Known invocation context:
- Intended for view/handler code that needs to present or operate on available queue names (e.g., UI filters, queue-specific views). The source file does not list all callers; therefore exact call sites are not asserted.

## Args:
This method accepts no arguments.

## Returns:
list[str]: A lexicographically sorted list derived from the set of discovered queue names.
- Typical result: a list of strings with queue names (e.g., ["celery", "high_priority"]).
- If configuration contains None or non-string values, the returned list may contain those values (e.g., [None]) or raise a TypeError during sorting if elements are of mutually-incomparable types.
- The return value preserves uniqueness (set behavior) before sorting.

## Raises:
The method does not explicitly raise exceptions itself, but the following exceptions can propagate depending on runtime data:
- AttributeError: if self.application, self.application.workers, self.capp, or self.capp.conf is missing.
- KeyError: if a worker-reported queue descriptor does not contain the 'name' key (queue['name']).
- TypeError: if elements in the computed set are not mutually comparable when calling sorted(queues) (for example, if mixed types are present), sorting will raise TypeError.
These exceptions indicate misconfiguration or malformed worker data rather than intended control flow.

## State Changes:
Attributes READ:
- self.application.workers
- For each worker info: info.get('active_queues', [])
- self.capp.conf.task_default_queue
- self.capp.conf.task_queues (and each q.name within it)

Attributes WRITTEN:
- None. The method does not modify self or nested application/celery objects.

## Constraints:
Preconditions:
- self.application must be present and expose a mapping attribute workers (iterable via .items()) where each value supports .get('active_queues', []).
- Each element returned by info.get('active_queues', []) should be mapping-like and contain a 'name' key whose value is the queue name.
- self.capp must be present and have a conf attribute exposing task_default_queue and task_queues (task_queues may be None or an iterable of objects with a .name attribute).
- If these preconditions are not met, AttributeError or KeyError may be raised.

Postconditions:
- If preconditions hold and data types are consistent (queue names are strings), the method returns a deterministic, sorted list of unique queue name strings.
- No mutation of handler/application state occurs.

## Side Effects:
- None external: no network I/O, file I/O, logging, or mutation of global state is performed.
- Only internal temporary collections (set, list) are allocated during execution.

## Implementation notes (reimplementation checklist):
- Use a set to ensure uniqueness while collecting names from worker info and/or configuration.
- Prefer info.get('active_queues', []) to safely handle worker info objects lacking that key.
- When falling back to configuration, include the default queue and filter task_queues entries by truthiness of q.name.
- Return sorted(queues) to provide a stable, deterministic order for display or selection.
- Be prepared to surface or handle KeyError/AttributeError if worker data or configuration structures deviate from expectations.

## Example usage (conceptual):
- A view that populates a queue selection dropdown can call this method to get current queue names for rendering; no state cleanup is required after the call.

