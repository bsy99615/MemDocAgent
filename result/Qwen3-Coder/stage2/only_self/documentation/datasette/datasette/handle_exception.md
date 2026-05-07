# `handle_exception.py`

## `datasette.handle_exception.handle_exception` · *function*

## Summary:
Handles exceptions in Datasette applications by returning appropriate JSON or HTML error responses based on request format and exception type.

## Description:
This function acts as a factory that creates an async exception handler for Datasette applications. It processes different types of exceptions (Base400, DatasetteError, and general exceptions) and generates appropriate HTTP responses with either JSON or HTML content depending on whether the request ends with '.json'. The handler also supports debugging features like pdb post-mortem and rich console exception display.

This logic is extracted into its own function to centralize error handling logic and provide consistent error responses across the Datasette application. It separates the concern of exception processing from business logic, making error handling reusable and maintainable.

## Args:
    datasette: Datasette instance containing configuration options like pdb flag and CORS settings
    request: Request object containing path information to determine response format
    exception: The exception instance to be handled

## Returns:
    An async function that when awaited returns a Response object containing either:
    - JSON error data when request path ends with '.json'
    - HTML error page when request path does not end with '.json'

## Raises:
    None: The handle_exception function itself doesn't raise exceptions, but the returned async function may raise exceptions during template rendering or response creation.

## Constraints:
    Preconditions:
    - datasette must be a valid Datasette instance with required attributes
    - request must be a valid request object with path attribute
    - exception must be an instance of Exception or subclass
    
    Postconditions:
    - The returned async function will always return a Response object
    - Response will be either JSON or HTML formatted based on request path ending

## Side Effects:
    - May invoke pdb.post_mortem() if datasette.pdb is True
    - May print exception tracebacks to console via rich or traceback
    - May modify headers dictionary when CORS is enabled
    - May perform template rendering operations

## Control Flow:
```mermaid
flowchart TD
    A[handle_exception called] --> B{datasette.pdb True?}
    B -->|Yes| C[pdb.post_mortem]
    B -->|No| D{rich available?}
    D -->|Yes| E[rich.print_exception]
    D -->|No| F{exception type}
    F -->|Base400| G[Set status from exception]
    F -->|DatasetteError| H[Set status, info, message from exception]
    F -->|Other| I[Set status=500, message=str(exception)]
    G --> J[Prepare info dict]
    H --> J
    I --> J
    J --> K[Update info with ok=False, error, status, title]
    K --> L{datasette.cors enabled?}
    L -->|Yes| M[add_cors_headers]
    L -->|No| N
    N --> O{request ends with .json?}
    O -->|Yes| P[Response.json]
    O -->|No| Q[Select template]
    Q --> R[Render template]
    R --> S[Response.html]
```

## Examples:
```python
# In Datasette's error handling middleware
async def error_middleware(app):
    async def middleware(request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            # Centralized error handling using handle_exception
            handler = handle_exception(datasette, request, e)
            return await handler()
    
    return middleware

# Direct usage in view functions
async def my_view(request):
    try:
        # Some operation that might fail
        result = await risky_operation()
        return Response.json(result)
    except Exception as e:
        # Return appropriate error response
        handler = handle_exception(datasette, request, e)
        return await handler()
```

