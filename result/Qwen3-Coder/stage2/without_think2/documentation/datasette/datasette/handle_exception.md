# `handle_exception.py`

## `datasette.handle_exception.handle_exception` · *function*

## Summary:
Creates an asynchronous error handler that formats and returns appropriate HTTP responses for different types of exceptions.

## Description:
This function generates an async error handler that processes various exception types (Base400, DatasetteError, and generic exceptions) and returns either JSON or HTML responses based on the request format (.json vs regular HTTP). It provides debugging capabilities via pdb and rich console output, and properly formats error information for display.

## Args:
    datasette (Datasette): The datasette instance containing configuration such as pdb flag, CORS settings, Jinja environment, and URL utilities
    request (Request): The incoming HTTP request object with path attribute for determining response format
    exception (Exception): The exception that occurred during request processing

## Returns:
    callable: An async function that when invoked processes the exception and returns either a Response.json() or Response.html() object

## Raises:
    None explicitly raised - the function handles all exceptions internally

## Constraints:
    Preconditions:
    - datasette must be a valid Datasette instance with required attributes (pdb, cors, jinja_env, urls, app_css_hash)
    - request must be a valid request object with a path attribute
    - exception must be an Exception instance
    
    Postconditions:
    - The returned async function will always return either a Response.json() or Response.html() object
    - Error information is consistently formatted in the response regardless of exception type
    - Proper HTTP status codes are returned based on exception type

## Side Effects:
    - May invoke pdb.post_mortem() if datasette.pdb is True
    - May print rich exception information to console if rich is available
    - May print traceback to stderr for unhandled exceptions
    - May modify headers dictionary if CORS is enabled
    - May render Jinja templates using datasette's template engine

## Control Flow:
```mermaid
flowchart TD
    A[handle_exception called] --> B{datasette.pdb}
    B -- True --> C[pdb.post_mortem]
    B -- False --> D{rich available}
    D -- True --> E[rich.get_console().print_exception]
    D -- False --> F[Continue]
    F --> G{exception type}
    G -- Base400 --> H[Set status, info, message]
    G -- DatasetteError --> I[Set status, info, message, title]
    G -- Other --> J[Set status=500, message=str(exception)]
    H --> K[Set templates]
    I --> K
    J --> K
    K --> L[Update info dict]
    L --> M{datasette.cors}
    M -- True --> N[add_cors_headers]
    M -- False --> O[Skip headers]
    O --> P{request path ends with .json}
    P -- True --> Q[Response.json]
    P -- False --> R[Select template]
    R --> S[Render HTML template]
    S --> T[Response.html]
```

## Examples:
    # Typical usage in a web framework context
    try:
        # Some operation that might raise an exception
        result = risky_operation()
    except Exception as e:
        # Handle the exception with proper formatting
        response_handler = handle_exception(datasette_instance, request_instance, e)
        return await response_handler()
        
    # For a 400 error specifically
    try:
        raise Base400("Invalid parameter")
    except Base400 as e:
        response_handler = handle_exception(datasette_instance, request_instance, e)
        return await response_handler()
        
    # For a DatasetteError
    try:
        raise DatasetteError("Database connection failed", status=503)
    except DatasetteError as e:
        response_handler = handle_exception(datasette_instance, request_instance, e)
        return await response_handler()

