# `handle_exception.py`

## `datasette.handle_exception.handle_exception` · *function*

## Summary:
Produces an async error-response handler for a caught exception: returns an awaitable that will render either a JSON error response (for .json requests) or an HTML error page, while performing debugging and logging side effects.

## Description:
This factory function is called when the Datasette request pipeline catches an exception and needs to convert it into an HTTP Response. It returns an async callable (no-argument coroutine function) that, when awaited, performs the following:
- Optionally drops into the Python debugger if debugging is enabled on the Datasette instance.
- Prints a rich-formatted stack trace to the console (if the rich library is available).
- Classifies the exception into one of three branches (Base400, DatasetteError, or generic server error) and prepares response metadata.
- Adds CORS headers if the Datasette instance has CORS enabled.
- Returns either a JSON Response (when request path ends with .json) or an HTML Response rendered via Jinja2 templates.

Known/typical callers and trigger context:
- Invoked by the Datasette request/error handling layer immediately after an exception is caught while processing an incoming HTTP/ASGI request. Typical usage: call handle_exception(datasette, request, exception) to obtain an awaitable handler, then await that handler to produce the Response to return to the client.

Why this logic is a separate function:
- Responsibility separation: isolates the mapping of arbitrary exceptions to HTTP responses and associated side effects (debugging, logging, CORS) from the main request handling logic.
- Reusability and testability: returns an awaitable so the same conversion can be used in different catch points or middlewares without duplicating rendering/debug behavior.
- Ensures a single canonical pathway for error responses (consistent status codes, JSON vs HTML behavior, and header handling).

## Args:
    datasette (object): The application-level Datasette instance. Required attributes/behavior used:
        - pdb (bool-like): if truthy, pdb.post_mortem will be called with exception.__traceback__.
        - cors (bool): if truthy, add_cors_headers(headers) will be called to populate CORS headers.
        - jinja_env: a Jinja2 Environment exposing select_template(templates) and template.render_async(context).
        - urls: mapping/object passed into templates as "urls".
        - app_css_hash(): callable returning string used by templates as app_css_hash.
    request (object): The incoming request-like object. Only the .path attribute is accessed (a string). The code splits on "?" and checks whether the path ends with ".json".
    exception (BaseException): The exception instance that triggered the error handler. The function branches behavior based on:
        - isinstance(exception, Base400): uses exception.status and exception.args[0]
        - isinstance(exception, DatasetteError): uses exception.status, exception.error_dict, exception.message, exception.message_is_html, exception.title
        - otherwise: treated as an internal server error (500)

Notes on argument interdependencies:
- datasette.jinja_env and datasette.app_css_hash must be present for HTML rendering.
- request.path must be a string; if it's missing or not string-like the ".split" and ".endswith" checks will raise.

## Returns:
    function: A zero-argument async function (coroutine) named inner. When awaited, inner returns a datasette.Response instance:
        - Response.json(info, status=status, headers=headers) when the request path (before querystring) ends with ".json".
        - Response.html(rendered_html, status=status, headers=headers) otherwise.
    The info object included in JSON or passed into the template contains keys:
        - ok (bool): always False for error responses
        - error: the error message (string or Markup if message_is_html)
        - status: numeric HTTP status code
        - title: optional human-readable title (may be None)

Possible return status codes and associated behavior:
- For Base400-derived exceptions: status is taken from exception.status; message is exception.args[0].
- For DatasetteError: status is exception.status; info starts from exception.error_dict and message from exception.message (wrapped in markupsafe.Markup when message_is_html is truthy); title from exception.title.
- For any other exception: status == 500; message is str(exception); a traceback is printed to stderr via traceback.print_exc().

## Raises:
The handle_exception function itself simply returns an async callable and does not raise. The returned inner coroutine may raise the following (these are not explicitly raised by this code but can propagate from operations it performs):
    - IndexError: if exception is a Base400 instance but exception.args is empty (code accesses exception.args[0] without guard).
    - TemplateNotFound (jinja2.exceptions.TemplateNotFound) or similar: if datasette.jinja_env.select_template(...) fails to find any of the provided templates.
    - Any exception raised by template.render_async (e.g., during context evaluation) will propagate.
    - Any exception raised by pdb.post_mortem, rich.get_console(), add_cors_headers, datasette.app_css_hash(), or Response constructors can propagate.
Note: the code intentionally prints the traceback for unexpected exceptions but does not catch or swallow exceptions thrown while generating the error page itself.

## Constraints:
Preconditions:
    - datasette must implement the attributes and callables listed under Args (pdb, cors, jinja_env, urls, app_css_hash).
    - request must expose a .path string attribute.
    - exception must be an Exception-derived instance (has __traceback__ etc).

Postconditions:
    - Awaiting the returned inner coroutine yields a Response object appropriate to the request path (.json → JSON, otherwise → HTML).
    - The response headers dict may include CORS headers if datasette.cors is true.
    - Side-effecting debug/log output (pdb.post_mortem call and printed stack traces) will have been emitted if applicable.

## Side Effects:
    - Debugging:
        - If datasette.pdb is truthy, pdb.post_mortem(exception.__traceback__) is called (enters post-mortem debugger).
        - If rich is available (rich import is not None), a rich-formatted exception with local variables is printed to the console.
    - Logging:
        - For generic (non-Base400, non-DatasetteError) exceptions, traceback.print_exc() is called, printing the traceback to stderr.
    - Headers:
        - If datasette.cors is truthy, add_cors_headers(headers) is called to mutate and populate headers returned in the Response.
    - Template rendering:
        - The returned HTML response is produced by selecting and rendering Jinja2 templates (may execute template code).
    - No filesystem or network I/O is performed directly by this function beyond what template rendering or user-provided hooks inside those callables may do.

## Control Flow:
flowchart TD
    A[handle_exception called with datasette, request, exception] --> B[async inner() returned]
    B --> C{datasette.pdb truthy?}
    C -->|yes| C1[pdb.post_mortem(exception.__traceback__)]
    C -->|no| D[continue]
    D --> E{rich available?}
    E -->|yes| E1[rich.get_console().print_exception(show_locals=True)]
    E -->|no| F[continue]
    F --> G{exception is Base400?}
    G -->|yes| H[status=exception.status; message=exception.args[0]; info={}]
    G -->|no| I{exception is DatasetteError?}
    I -->|yes| J[status=exception.status; info=exception.error_dict; message=exception.message; title=exception.title; wrap Markup if message_is_html]
    I -->|no| K[status=500; info={}; message=str(exception); traceback.print_exc()]
    H & J & K --> L[templates = [f"{status}.html","error.html"]; info.update(...)]
    L --> M[headers = {}]
    M --> N{datasette.cors truthy?}
    N -->|yes| N1[add_cors_headers(headers)]
    N -->|no| O[continue]
    O --> P{request.path before query endswith .json?}
    P -->|yes| Q[return Response.json(info, status, headers)]
    P -->|no| R[template = select_template(templates); render_async(context); return Response.html(rendered, status, headers)]

## Examples:
- Typical runtime flow (JSON client):
    1. Request handler catches an exception and calls handle_exception(datasette, request, exc) producing an awaitable handler.
    2. The caller awaits the returned coroutine; because request.path ends with ".json", the handler returns Response.json(info, status, headers).
    3. The client receives JSON with keys {ok: False, error, status, title} and any CORS headers if enabled.

- Typical runtime flow (web browser requesting HTML):
    1. Request handler obtains the awaitable from handle_exception and awaits it.
    2. The handler selects the status-specific template (e.g., "404.html") falling back to "error.html", renders it with context (info, urls, app_css_hash, menu_links), and returns a Response.html payload with the proper status and headers.

- Debugging scenario:
    - If datasette.pdb is enabled and an unexpected exception occurs, the inner coroutine will call pdb.post_mortem with the exception traceback, allowing an interactive post-mortem inspection before the response is returned.

Notes:
- Do not call exception.args[0] unless the Base400 implementation guarantees an argument; otherwise IndexError may occur.
- The function purposely centralizes conversion of exceptions to HTTP responses; any change to response shape (info keys, headers) should be made here to apply site-wide.

