# `handle_exception.py`

## `datasette.handle_exception.handle_exception` · *function*

## Summary
Creates an asynchronous exception handler for Datasette applications that generates appropriate HTTP responses with error information formatted as either JSON or HTML.

## Description
This function returns an async callable that processes exceptions occurring within a Datasette application. It categorizes exceptions into three types (Base400, DatasetteError, and general exceptions) and responds with appropriate HTTP status codes, error messages, and response formats. The handler automatically selects between JSON and HTML responses based on the request path (.json suffix) and applies CORS headers when enabled.

The function serves as a centralized error handling mechanism that ensures consistent error presentation throughout the Datasette application.

## Args
- datasette: The Datasette application instance containing configuration like pdb debugging flag, cors settings, and template environment
- request: The incoming HTTP request object with path information to determine response format  
- exception: The exception object that occurred and needs to be handled

## Returns
- An async function that when awaited processes the exception and returns a Response object (either Response.json or Response.html) with appropriate status code and error information

## Raises
- No explicit raises in the function itself, but the returned async function may raise exceptions during template rendering or response creation

## Constraints
- Preconditions:
  - datasette must be a valid Datasette application instance with required attributes
  - request must have a path attribute that can be processed
  - exception must be a valid Python exception object
- Postconditions:
  - The returned async function will always return a Response object
  - Error information is properly formatted in either JSON or HTML based on request path
  - The response contains proper status codes and error details according to exception type

## Side Effects
- May invoke pdb.post_mortem() if datasette.pdb is True (debugging mode)
- May print exception tracebacks to console if rich is not available (for enhanced debugging)
- May print exception tracebacks to console using traceback.print_exc() for general error logging
- May modify headers dictionary if CORS is enabled (adds Access-Control-Allow-* headers)
- May perform template rendering operations via Jinja2 environment

## Control Flow
```mermaid
flowchart TD
    A[handle_exception called] --> B{datasette.pdb?}
    B -- Yes --> C[Invoke pdb.post_mortem with exception.__traceback__]
    B -- No --> D[Continue]
    D --> E{rich available?}
    E -- Yes --> F[Print exception with rich.get_console().print_exception()]
    E -- No --> G[Continue]
    G --> H{exception type}
    H -->|Base400| I[Set status=400, info={}, message=exception.args[0]]
    H -->|DatasetteError| J[Set status, info=error_dict, message=message, title=title]
    H -->|Other| K[Set status=500, info={}, message=str(exception)]
    I --> L[Print traceback if needed]
    J --> L
    K --> L
    L --> M[Prepare templates list: [f"{status}.html", "error.html"]]
    M --> N[Update info dict with ok=False, error, status, title]
    N --> O{datasette.cors?}
    O -- Yes --> P[Add CORS headers using add_cors_headers()]
    O -- No --> Q[Continue]
    Q --> R{Request path ends with .json?}
    R -- Yes --> S[Return Response.json with info, status, headers]
    R -- No --> T[Select template and render HTML response]
    S --> U[Return Response.json]
    T --> U
```

## Examples
```python
# Typical usage in Datasette application middleware/error handling
async def handle_exception(datasette, request, exception):
    # Returns async function that handles the exception
    return inner

# When an exception occurs:
# - For a Base400 exception: returns JSON with {"ok": False, "error": "message", "status": 400}
# - For a DatasetteError: returns HTML with error details rendered by template engine
# - For other exceptions: returns JSON with {"ok": False, "error": "message", "status": 500}
```

