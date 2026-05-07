# `async_utils.py`

## `src.jinja2.async_utils.async_variant` · *function*

## Summary:
Creates a decorator that enables a function to work with both synchronous and asynchronous variants by automatically selecting the appropriate implementation based on execution context.

## Description:
The `async_variant` decorator factory generates a decorator that allows a synchronous function to be paired with an asynchronous version. It intelligently routes calls to either implementation based on whether the execution environment is asynchronous. This pattern is essential in template engines like Jinja2 to support both synchronous and asynchronous rendering while maintaining clean, unified APIs.

The decorator uses introspection to detect the execution context through the `_PassArg` mechanism and automatically handles argument passing differences between synchronous and asynchronous contexts. When the decorated function is invoked, it examines the first argument to determine if the environment is asynchronous and routes accordingly.

## Args:
    normal_func (callable): The synchronous version of the function to be decorated. This function is called when the execution context is synchronous.

## Returns:
    callable: A decorator function that accepts an asynchronous function and returns a wrapper that intelligently routes calls to either the synchronous or asynchronous implementation.

## Raises:
    None explicitly raised by this function. Exceptions would propagate from the underlying functions being called.

## Constraints:
    Preconditions:
    - The `normal_func` parameter must be a callable that can be wrapped
    - The async function passed to the returned decorator must be compatible with the normal function signature
    - The function objects must have proper metadata for the wrapper assignment to work correctly
    
    Postconditions:
    - The returned wrapper function will have the same interface as the original functions
    - The wrapper function will properly route calls to either the synchronous or asynchronous implementation
    - The wrapper function will have a `jinja_async_variant` attribute set to True
    - The wrapper function will preserve the metadata of both the synchronous and asynchronous functions

## Side Effects:
    None directly caused by the decorator itself. However, the resulting wrapper function may cause side effects depending on which of the underlying functions it executes.

## Control Flow:
```mermaid
flowchart TD
    A[async_variant called with normal_func] --> B[Returns decorator function]
    B --> C[decorator called with async_func]
    C --> D[Detect pass_arg via _PassArg.from_obj(normal_func)]
    D --> E{pass_arg is None?}
    E -- Yes --> F[need_eval_context = True]
    E -- No --> G[need_eval_context = False]
    F --> H[Create is_async detection function]
    G --> H
    H --> I[Create wrapper function with proper metadata]
    I --> J[wrapper called with args/kwargs]
    J --> K{need_eval_context?}
    K -- Yes --> L[Skip first argument from args]
    K -- No --> M[Use all arguments]
    L --> N[Check if async via is_async(args)]
    M --> N
    N --> O{is_async(args)?}
    O -- Yes --> P[Call async_func(*args, **kwargs)]
    O -- No --> Q[Call normal_func(*args, **kwargs)]
    P --> R[Return async result]
    Q --> R
    R --> S[Set jinja_async_variant = True]
    S --> T[Return result]
```

## Examples:
```python
# Define synchronous function
@async_variant
def render_template(template_name, context):
    # Synchronous implementation
    return f"Rendered {template_name} synchronously"

# Define asynchronous version
async def render_template_async(template_name, context):
    # Asynchronous implementation  
    return f"Rendered {template_name} asynchronously"

# Apply the decorator to pair the functions
render_template = render_template(render_template_async)

# Usage - automatically selects sync or async based on context
# If environment.is_async is True, calls render_template_async
# Otherwise, calls render_template
result = render_template("index.html", {"title": "Home"})
```

## `src.jinja2.async_utils.auto_await` · *function*

## Summary:
Automatically awaits async values while preserving synchronous values, handling both awaitable objects and primitive types transparently.

## Description:
This utility function provides transparent handling of both synchronous and asynchronous values by checking if a value needs to be awaited before returning it. It's designed to work seamlessly with Jinja2's async rendering pipeline where values might be either regular objects or awaitable objects that need to be resolved.

The function serves as a bridge between synchronous and asynchronous code paths, ensuring that async values are properly awaited while avoiding unnecessary operations on already-resolved values. It specifically checks for common primitive types that don't need to be awaited and handles awaitable objects appropriately.

## Args:
    value (Union[Awaitable[V], V]): A value that may be either an awaitable object or a regular value of type V. The type V represents the expected return type.

## Returns:
    V: The resolved value, either directly returned if it's not awaitable, or awaited and returned if it is awaitable. The return type matches the input type.

## Raises:
    None explicitly raised - the function delegates to Python's await mechanism which may raise exceptions during the await operation

## Constraints:
    Preconditions:
    - The input value must be either a regular value or an awaitable object
    - If the value is awaitable, it must be a proper awaitable that can be awaited with 'await'
    - The `_common_primitives` variable must be defined in the module scope
    
    Postconditions:
    - The returned value is always of type V (the same type as the input value)
    - If the input was awaitable, it's resolved to its final value before return

## Side Effects:
    None - This function is pure and doesn't modify any external state

## Control Flow:
```mermaid
flowchart TD
    A[Start auto_await] --> B{type(value) in _common_primitives?}
    B -- Yes --> C[Return value casted to V]
    B -- No --> D{inspect.isawaitable(value)?}
    D -- Yes --> E[Await value and return]
    D -- No --> F[Return value casted to V]
```

## Examples:
```python
# Usage with a synchronous value
result = await auto_await(42)  # Returns 42

# Usage with an awaitable value
async def async_func():
    return "hello"
result = await auto_await(async_func())  # Returns "hello" after awaiting
```

## `src.jinja2.async_utils.auto_aiter` · *function*

## Summary:
Converts a synchronous or asynchronous iterable into an asynchronous iterator.

## Description:
This function provides a unified interface for iterating over both synchronous and asynchronous iterables. It automatically detects whether the input supports asynchronous iteration by checking for the presence of the `__aiter__` method, and then yields items accordingly. This abstraction allows downstream code to work with either type of iterable without needing to distinguish between them explicitly.

## Args:
    iterable (Union[AsyncIterable[V], Iterable[V]]): An iterable object that may be either synchronous or asynchronous. The iterable must support the standard iteration protocol.

## Returns:
    AsyncIterator[V]: An asynchronous iterator that yields items from the input iterable, regardless of whether it's synchronous or asynchronous.

## Raises:
    None explicitly raised - the function delegates to the underlying iteration mechanisms which may raise their own exceptions.

## Constraints:
    Preconditions:
    - The input iterable must be a valid iterable object (either synchronous or asynchronous)
    - The iterable must support the appropriate iteration protocol (sync or async)
    
    Postconditions:
    - The returned async iterator will yield all items from the input iterable in order
    - The function handles both sync and async iteration transparently

## Side Effects:
    None - this function is a pure generator that doesn't perform any I/O operations or mutate external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start auto_aiter] --> B{hasattr(iterable, "__aiter__")}
    B -- True --> C[async for item in iterable]
    B -- False --> D[for item in iterable]
    C --> E[Yield item]
    D --> E
    E --> F[Return async iterator]
```

## Examples:
```python
# Usage with synchronous iterable
sync_list = [1, 2, 3, 4]
async for item in auto_aiter(sync_list):
    print(item)  # Prints: 1, 2, 3, 4

# Usage with asynchronous iterable
async def async_gen():
    for i in range(4):
        yield i

async for item in auto_aiter(async_gen()):
    print(item)  # Prints: 0, 1, 2, 3
```

## `src.jinja2.async_utils.auto_to_list` · *function*

## Summary:
Converts a synchronous or asynchronous iterable into a list by asynchronously consuming all elements.

## Description:
This function provides a convenient way to transform any iterable (whether synchronous or asynchronous) into a concrete list. It leverages the `auto_aiter` utility to handle both sync and async iteration patterns transparently, making it suitable for contexts where the input type is unknown or may vary.

## Args:
    value (Union[AsyncIterable[V], Iterable[V]]): An iterable object that may be either synchronous or asynchronous. The iterable must support the standard iteration protocol.

## Returns:
    List[V]: A list containing all elements from the input iterable in their original order.

## Raises:
    None explicitly raised - the function delegates to the underlying iteration mechanisms which may raise their own exceptions.

## Constraints:
    Preconditions:
    - The input value must be a valid iterable object (either synchronous or asynchronous)
    - The iterable must support the appropriate iteration protocol (sync or async)
    
    Postconditions:
    - The returned list will contain all items from the input iterable in order
    - The function handles both sync and async iteration transparently

## Side Effects:
    None - this function is a pure async generator that doesn't perform any I/O operations or mutate external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start auto_to_list] --> B[Call auto_aiter(value)]
    B --> C[Async for x in auto_aiter(value)]
    C --> D[Collect x into list]
    D --> E[Return list]
```

## Examples:
```python
# Usage with synchronous iterable
sync_list = [1, 2, 3, 4]
result = await auto_to_list(sync_list)
print(result)  # Output: [1, 2, 3, 4]

# Usage with asynchronous iterable
async def async_gen():
    for i in range(4):
        yield i

result = await auto_to_list(async_gen())
print(result)  # Output: [0, 1, 2, 3]
```

