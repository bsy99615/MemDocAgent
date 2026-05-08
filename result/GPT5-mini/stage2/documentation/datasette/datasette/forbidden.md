# `forbidden.py`

## `datasette.forbidden.forbidden` · *function*

## Summary:
Creates and returns an asynchronous zero-argument handler which, when invoked and awaited, renders the "error.html" template with a "Forbidden" title and the provided message, and returns an HTML Response with HTTP status 403.

## Description:
This function is a small factory that centralizes the construction of a standard 403 (Forbidden) HTML response. It builds an async inner function that:

- Awaits datasette.render_template("error.html", context, request=request) to produce HTML,
- Wraps the rendered HTML in Response.html(..., status=403),
- Returns that Response object.

Typical callers and trigger conditions:
- Request handlers, middleware, or authorization checks that detect an access-control denial (permission missing, resource access forbidden) will use this factory to produce a consistent 403 response.
- In the provided snapshot there are no explicit call sites available. Expect it to be used wherever the application needs to return a user-facing "Forbidden" page.

Why extracted:
- Centralizes the HTML template name ("error.html"), context keys ("title" and "error"), and the 403 status code so all forbidden responses look and behave consistently.
- Returns a ready-to-run async handler compatible with async request handling pipelines without forcing callers to inline rendering and Response construction.

## Args:
    datasette (object)
        - Required.
        - Expected to provide an awaitable method with signature similar to:
          async def render_template(template_name: str, context: dict, request=None) -> str
        - The function will call: await datasette.render_template("error.html", context, request=request).
    request (object)
        - Required.
        - A request-like object forwarded into render_template as the request context (commonly an ASGI/Starlette Request or framework-equivalent).
    message (str)
        - Required.
        - Human-readable message inserted into the template context under the key "error".
        - Any value acceptable to the template renderer is permitted, but typically a string.

Parameter interdependencies:
- datasette.render_template must accept the request keyword argument for the forwarded request to be used by the renderer.
- message is passed verbatim into the template context; the function does not sanitize or modify it.

## Returns:
    callable
        - Type: async function (callable that, when called, returns a coroutine). Precise type: Callable[[], Coroutine[Any, Any, Response]]
        - Behavior:
            * The returned value is the inner async function object (not yet executed).
            * To obtain the Response you must call the returned function to get a coroutine, then await that coroutine.
            * When awaited successfully, the coroutine yields a datasette.Response whose body is the rendered HTML and whose HTTP status is 403.
        - Example outcomes:
            * Normal: awaiting the coroutine returns a Response (status=403) containing the rendered "error.html".
            * Error: if template rendering or Response construction raises, those exceptions propagate to the caller.

## Raises:
    - The factory function itself does not raise explicit exceptions.
    - Propagated exceptions (examples):
        * Any exception raised by datasette.render_template (template not found, template syntax/runtime errors, I/O errors reading templates).
        * Any exception raised by Response.html (if Response construction fails).
    - Callers should handle or allow these exceptions to propagate according to their error-handling semantics.

## Constraints:
Preconditions:
    - Caller must execute in an async-capable context to call and await the returned handler:
        1) handler_fn = forbidden(datasette, request, message)  # handler_fn is async function
        2) coroutine = handler_fn()                              # coroutine object
        3) response = await coroutine                            # yields Response
    - datasette must implement an awaitable render_template method as described above.

Postconditions:
    - When the returned coroutine completes successfully, it returns a Response where:
        * response.status == 403
        * response.body (HTML) == datasette.render_template("error.html", {"title":"Forbidden","error": message}, request=request)

## Side Effects:
    - Invokes datasette.render_template which may perform I/O (reading template files), access configuration, or execute template code that reads application state.
    - Does not mutate any global state itself.
    - No direct network calls or database writes are performed by this function, but the template rendering process could indirectly cause such effects depending on template logic.

## Control Flow:
flowchart TD
    A[Call forbidden(datasette, request, message)] --> B[Define async inner()]
    B --> C[Return inner (async function)]
    C --> D[Caller calls inner() -> coroutine]
    D --> E[Caller awaits coroutine]
    E --> F[Await datasette.render_template("error.html", {"title":"Forbidden","error":message}, request=request)]
    F --> G[render_template returns rendered_html]
    G --> H[Response.html(rendered_html, status=403)]
    H --> I[Return Response(status=403, body=rendered_html)]

## Examples (async context, illustrative):
- Invocation and awaiting (two-step form):
    1) handler_fn = forbidden(datasette, request, "You do not have permission")
    2) coro = handler_fn()
    3) response = await coro
    After step 3, `response` is a datasette.Response with status 403 and the rendered HTML body.

- Inline awaiting inside an async request handler:
    - response = await forbidden(datasette, request, "Access denied")()
    - The expression forbidden(... )() builds the coroutine and awaits it, returning the Response.

- Returning from an async handler (framework-dependent):
    - Some async frameworks accept an awaitable as a return value. In an async request handler you might:
        return await forbidden(datasette, request, "Not allowed")()
    - Or, if the framework will await returned coroutines for you, you could return the coroutine object:
        return forbidden(datasette, request, "Not allowed")()
    - Verify your framework's expected handler return semantics before returning the coroutine directly.

Notes:
- The template context keys are fixed: {"title": "Forbidden", "error": message}. To change the title or template, callers must use a different factory or modify the template system.
- The module imports include Response and render-related hooks; this function relies only on Response.html and datasette.render_template and does not itself use the os.stat import.

