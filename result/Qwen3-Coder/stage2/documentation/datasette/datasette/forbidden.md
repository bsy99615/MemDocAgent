# `forbidden.py`

## `datasette.forbidden.forbidden` · *function*

## Summary
Creates an async handler function for returning 403 Forbidden HTTP responses with custom error messages within Datasette's plugin system.

## Description
This function serves as a factory for creating async response handlers that generate HTTP 403 Forbidden responses. It's designed to be used within Datasette's plugin system via the @hookimpl decorator. The returned async function renders an error.html template with the provided message and sets the appropriate HTTP status code. This pattern allows plugins to gracefully handle authorization failures and return meaningful error messages to clients.

## Args
- datasette: Datasette application instance providing access to rendering capabilities and template system
- request: HTTP request object containing request context information  
- message: String error message to display in the forbidden response

## Returns
- An async callable function that when invoked returns a Response object with HTTP status 403

## Raises
- None explicitly raised by this function, though underlying template rendering may raise exceptions

## Constraints
- Preconditions: All arguments must be properly initialized (datasette and request should be valid objects)
- Postconditions: The returned async function, when called, produces a Response object with status 403

## Side Effects
- Renders HTML template using datasette.render_template
- Returns a Response object that will be sent as HTTP response with status 403

## Control Flow
```mermaid
flowchart TD
    A[forbidden called] --> B[Inner async function created]
    B --> C[Inner function invoked]
    C --> D[Render error.html template]
    D --> E[Set title="Forbidden", error=message]
    E --> F[Return Response.html with status=403]
```

## Examples
```python
# Typical usage in a Datasette plugin hook
@hookimpl
def prepare_connection(conn):
    # Some authorization logic
    if not user_can_access():
        return forbidden(datasette, request, "Access denied to this resource")

# Another common usage pattern
@hookimpl
def actor_from_request(request):
    # Authorization check
    if not is_authorized(request):
        return forbidden(datasette, request, "Authentication required")
```

