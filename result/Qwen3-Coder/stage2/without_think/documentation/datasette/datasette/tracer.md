# `tracer.py`

## `datasette.tracer.get_task_id` · *function*

## Summary:
Retrieves the current task identifier for tracing purposes, either from context storage or by generating a unique ID from the current asyncio task.

## Description:
This function provides a consistent way to obtain a task identifier that can be used for tracing and logging across async operations. It first checks if a task ID is already stored in the context variable `trace_task_id`. If found, it returns that ID. Otherwise, it attempts to derive the task ID from the current asyncio task. This approach allows for manual task identification override while falling back to automatic detection when needed.

## Args:
    None

## Returns:
    int or None: The task identifier if available, or None if no event loop is running or no task context is established.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The function should be called within an async context or when an event loop is available
    - The `trace_task_id` ContextVar must be properly initialized in the module
    
    Postconditions:
    - Returns either a valid integer task ID or None
    - Does not modify global state except through context variable access

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_task_id()] --> B{trace_task_id.get(None) != None?}
    B -- Yes --> C[Return current task ID]
    B -- No --> D[Try asyncio.get_event_loop()]
    D --> E{RuntimeError?}
    E -- Yes --> F[Return None]
    E -- No --> G[Get asyncio.current_task(loop)]
    G --> H[Return id(current_task)]
```

## Examples:
```python
# Basic usage in async context
task_id = get_task_id()  # Returns integer task ID or None

# In a traced operation
async def traced_operation():
    task_id = get_task_id()  # Gets task ID for logging
    # ... operation logic ...
```

## `datasette.tracer.trace_child_tasks` · *function*

## Summary:
A context manager that establishes a tracing task identifier for child operations within an async execution context.

## Description:
This function implements a context manager pattern that sets a task identifier in a context variable for the duration of a code block. It's designed to track asynchronous child tasks during execution, allowing for proper tracing and debugging of concurrent operations. The function uses the `trace_task_id` ContextVar to store the current task identifier obtained via `get_task_id()`.

The function is typically used in async contexts where child tasks are spawned or executed, ensuring that tracing information flows properly through the call stack. It follows the standard context manager protocol with setup and teardown phases.

Known callers within the codebase:
- This function is likely called by async functions that need to establish tracing context for child operations
- It would typically be used in async contexts where child tasks are created or executed

The logic is extracted into its own function rather than inlined because:
- It encapsulates the context management pattern for task tracing
- It ensures proper cleanup of context variables even if exceptions occur
- It provides a reusable mechanism for establishing tracing context across different async operations
- It separates concerns between task identification and context management

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Must be called within an async context where context variables are supported
    - The `trace_task_id` ContextVar must be properly initialized in the module
    - The `get_task_id()` function should be available and callable
    
    Postconditions:
    - The `trace_task_id` ContextVar will be set with a task identifier during execution
    - The ContextVar will be properly reset after the context manager exits

## Side Effects:
    - Modifies the context variable `trace_task_id` by setting and resetting its value
    - No external I/O operations or state mutations beyond context variable manipulation

## Control Flow:
```mermaid
flowchart TD
    A[trace_child_tasks() called] --> B[Get task ID from get_task_id()]
    B --> C[Set trace_task_id ContextVar with task ID]
    C --> D[Yield control to caller]
    D --> E[Reset trace_task_id ContextVar]
    E --> F[Exit context manager]
```

## Examples:
```python
# Usage in async context
async def example_operation():
    async with trace_child_tasks():
        # All child operations within this block will inherit the tracing context
        await some_async_function()
        # Context automatically cleaned up after this block

# Alternative usage with explicit context management
with trace_child_tasks():
    # Context is established and will be cleaned up
    await some_async_function()
```

## `datasette.tracer.trace` · *function*

## Summary:
A context manager that traces execution time and captures stack information for performance monitoring and debugging.

## Description:
This function provides a mechanism to instrument code sections for performance measurement and debugging. It acts as a context manager that wraps code execution, measuring the duration and capturing stack traces for later analysis. The tracing information is stored in a task-specific tracer collection when available.

## Args:
    type (str): The type or category of the traced operation for categorization
    **kwargs: Additional metadata to associate with the trace record

## Returns:
    Generator: Yields the provided kwargs to allow execution within the traced context

## Raises:
    AssertionError: When any of the keyword arguments conflict with reserved internal keys

## Constraints:
    Preconditions:
    - The function must be called within an async context or when an event loop is available
    - TRACE_RESERVED_KEYS must be defined in the module scope
    - tracers must be a dictionary-like object accessible in module scope
    
    Postconditions:
    - If tracing is enabled, trace information is appended to the appropriate task's tracer
    - If tracing is disabled, the function simply yields the kwargs unchanged

## Side Effects:
    - Modifies the global tracers dictionary when tracing is enabled
    - Captures stack trace information via traceback module
    - Uses time.perf_counter() for high-resolution timing

## Control Flow:
```mermaid
flowchart TD
    A[Start trace()] --> B{task_id available?}
    B -- No --> C[Yield kwargs and return]
    B -- Yes --> D{tracer exists for task?}
    D -- No --> E[Yield kwargs and return]
    D -- Yes --> F[Record start time]
    F --> G[Yield kwargs to execute wrapped code]
    G --> H[Record end time]
    H --> I[Build trace_info dict]
    I --> J[Update with kwargs]
    J --> K[Append to tracer]
    K --> L[Return]
```

## Examples:
```python
# Basic usage in async context
async def example_operation():
    with trace("database_query", table="users", query="SELECT * FROM users"):
        # Some database operation
        await db.execute(query)
        
# Usage with nested tracing
async def complex_operation():
    with trace("outer_operation", operation="complex"):
        with trace("inner_operation", step="validation"):
            # Validation logic
            result = validate_data(data)
```

## `datasette.tracer.capture_traces` · *function*

## Summary:
A context manager that temporarily associates a tracer object with the current task ID for tracing purposes.

## Description:
This function serves as a context manager that manages the lifecycle of tracer objects in a global registry. When a valid task ID is available, it registers the provided tracer with that task ID, making it accessible during the execution of traced operations. After the context exits, the tracer is removed from the registry.

The function acts as a generator-based context manager, yielding control to the wrapped code block while maintaining the tracer association during execution. It's typically used around traced operations to ensure proper cleanup of tracer references.

## Args:
    tracer (Any): The tracer object to associate with the current task. The exact type depends on the tracing implementation being used.

## Returns:
    Generator: A generator that yields control to the wrapped code block, managing the registration and cleanup of the tracer.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Must be called within an async context or when an event loop is available
    - The `get_task_id()` function must be available and working
    - The global `tracers` dictionary must be properly initialized
    
    Postconditions:
    - If a valid task ID exists, the tracer is registered in the global `tracers` dictionary during execution
    - The tracer is unregistered from the global `tracers` dictionary upon context exit
    - If no valid task ID exists, the function operates as a no-op

## Side Effects:
    - Modifies the global `tracers` dictionary by adding/removing entries
    - Uses context variables for task identification via `get_task_id()`
    - May affect tracing behavior by making tracers available during execution

## Control Flow:
```mermaid
flowchart TD
    A[Start capture_traces()] --> B[Call get_task_id()]
    B --> C{task_id is None?}
    C -- Yes --> D[Yield (no-op)]
    C -- No --> E[Store tracer in tracers[task_id]]
    E --> F[Yield (execute wrapped code)]
    F --> G[Delete tracer from tracers[task_id]]
```

## Examples:
```python
# Usage as a context manager
with capture_traces(my_tracer):
    # Tracing operations here
    result = some_operation()

# Usage as a decorator (when adapted for decorator pattern)
@capture_traces
async def traced_function():
    # Function body with tracing
    pass
```

## `datasette.tracer.AsgiTracer` · *class*

## Summary:
ASGI middleware that adds performance tracing capabilities to HTTP requests, injecting trace information into responses when requested.

## Description:
The AsgiTracer class is an ASGI middleware designed to instrument HTTP requests with performance tracing information. When a request includes the query parameter `_trace=1`, it captures timing data for various operations and injects this information into the HTTP response. This enables developers to analyze request performance and identify bottlenecks in their ASGI applications.

The tracer captures request duration, cumulative trace durations, and trace counts, then formats this information appropriately based on the response content type (HTML or JSON) and injects it into the response body. For HTML responses containing a `</body>` tag, trace information is injected before the closing tag. For JSON responses starting with `{`, the trace information is added as a `_trace` field.

## State:
- `app`: The wrapped ASGI application instance that this tracer wraps
- `max_body_bytes`: Class attribute defining maximum response body size (256KB) for trace injection

## Lifecycle:
- Creation: Instantiate with an ASGI application (`app`) as the sole parameter
- Usage: Call the instance with standard ASGI scope, receive, and send parameters
- Destruction: No explicit cleanup required; relies on ASGI lifecycle management

## Method Map:
```mermaid
flowchart TD
    A[AsgiTracer.__call__] --> B{Query contains _trace=1?}
    B -- No --> C[Direct app call]
    B -- Yes --> D[Initialize tracing variables]
    D --> E[Create wrapped_send function]
    E --> F[Execute app with wrapped send]
    F --> G[Process response messages]
    G --> H{Message type}
    H --> I[http.response.start]
    H --> J[http.response.body]
    I --> K[Store headers and forward]
    J --> L{Body size exceeds limit?}
    L -- Yes --> M[Send partial body and mark limit exceeded]
    L -- No --> N{More body expected?}
    N -- No --> O[Collect all body, process and inject traces]
    N -- Yes --> P[Continue collecting body]
    O --> Q{Content-Type}
    Q --> R[HTML with </body>]
    Q --> S[JSON starting with {]
    Q --> T[Other]
    R --> U[Inject trace before </body>]
    S --> V[Add _trace field to JSON]
    T --> W[Send unchanged]
```

## Raises:
- No explicit exceptions are raised by the constructor
- Exceptions from the wrapped ASGI application are propagated normally

## Example:
```python
# Create the tracer middleware
tracer = AsgiTracer(my_asgi_app)

# Use in ASGI server (e.g., with uvicorn)
# When accessing: http://localhost:8000/?_trace=1
# Response will include trace information embedded in HTML or JSON
```

### `datasette.tracer.AsgiTracer.__init__` · *method*

## Summary:
Initializes the ASGI tracer middleware with the target ASGI application to be wrapped.

## Description:
This constructor creates an instance of the AsgiTracer middleware, storing the provided ASGI application that will be wrapped for performance tracing. The tracer intercepts HTTP requests and injects timing information into responses when the `_trace=1` query parameter is present.

## Args:
    app: The ASGI application instance to be wrapped by this tracer middleware

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.app: Stores the ASGI application instance for later use in request processing

## Constraints:
    Preconditions:
    - The app parameter must be a valid ASGI application instance
    - The app must conform to the ASGI specification
    
    Postconditions:
    - The instance is properly initialized with the provided ASGI application
    - The app is stored in self.app for use in the __call__ method

## Side Effects:
    None

### `datasette.tracer.AsgiTracer.__call__` · *method*

## Summary:
Intercepts and traces ASGI HTTP requests, injecting performance timing information into response bodies when the "_trace=1" query parameter is present.

## Description:
This method implements the ASGI middleware interface to wrap HTTP request processing. When the "_trace=1" query parameter is detected in the request, it enables detailed tracing of the request processing duration and any traced operations within the application. The method wraps the response sending mechanism to capture and modify the response body to include trace information for HTML and JSON responses.

## Args:
    scope (dict): ASGI scope containing request metadata including query_string
    receive (callable): ASGI receive callable for receiving messages
    send (callable): ASGI send callable for sending messages

## Returns:
    Awaitable: A coroutine that completes when the request processing finishes

## Raises:
    None explicitly raised - All exceptions are propagated from the underlying application

## State Changes:
    Attributes READ: 
    - self.app: The wrapped ASGI application
    - self.max_body_bytes: Maximum response body size limit for tracing
    
    Attributes WRITTEN: 
    - None directly modified

## Constraints:
    Preconditions:
    - Must be called within an ASGI context
    - The scope must contain valid ASGI request data
    - The receive/send functions must conform to ASGI specification
    
    Postconditions:
    - If tracing is disabled, the original application is called unchanged
    - If tracing is enabled, trace information is injected into appropriate response bodies
    - The wrapped application receives the modified send function for tracing

## Side Effects:
    - Modifies HTTP response bodies for HTML and JSON content types to include trace data
    - Calls the wrapped ASGI application with a modified send function
    - Uses global tracer registry via capture_traces context manager
    - May cause increased memory usage for large response bodies due to buffering
    - Makes trace data available globally during request processing via context manager

