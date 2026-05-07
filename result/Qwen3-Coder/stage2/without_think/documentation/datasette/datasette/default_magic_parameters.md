# `default_magic_parameters.py`

## `datasette.default_magic_parameters.header` · *function*

## Summary:
Extracts and returns the value of a specified HTTP header from a request object.

## Description:
This function retrieves the value of an HTTP header from a request's headers dictionary. It normalizes the header key by replacing underscores with hyphens and ensures proper encoding/decoding of header values. This utility function is designed to simplify access to HTTP headers in Datasette's magic parameters system.

## Args:
    key (str): The header name to retrieve, using underscore notation (e.g., "content_type")
    request (object): A request object containing a scope dictionary with headers key

## Returns:
    str: The decoded header value if found, or an empty string if the header is not present

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - The request object must have a scope attribute containing a headers dictionary
        - The headers dictionary must be iterable and contain byte-encoded keys
    
    Postconditions:
        - Returns a properly decoded string representation of the header value
        - Always returns a string, even when header is not found

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[header(key, request)] --> B{key.replace("_", "-")}
    B --> C[key.encode("utf-8")]
    C --> D[headers_dict = dict(request.scope["headers"])]
    D --> E{headers_dict.get(key, b"")}
    E --> F{value != b""}
    F -->|True| G[value.decode("utf-8")]
    F -->|False| H[return ""]
    G --> I[return value]
    H --> I
```

## Examples:
    # Get Content-Type header
    content_type = header("content_type", request)
    
    # Get User-Agent header  
    user_agent = header("user_agent", request)
    
    # Non-existent header returns empty string
    nonexistent = header("x_nonexistent", request)  # Returns ""
```

## `datasette.default_magic_parameters.actor` · *function*

## Summary:
Retrieves a specific attribute from the request's actor data using a key lookup.

## Description:
This function serves as a magic parameter handler in Datasette that provides template access to actor information stored in the request. It's designed to be used within Datasette's plugin system to make actor data available to templates and other components that need to access user authentication or authorization context.

The function acts as a bridge between the ASGI request scope and template rendering, allowing access to actor metadata through key-based lookups. It's particularly useful in Datasette's template system where magic parameters are used to inject contextual data.

## Args:
    key (str): The attribute name to retrieve from the actor data dictionary
    request: The Datasette request object containing actor information in its scope

## Returns:
    The value associated with the specified key in the actor data dictionary

## Raises:
    KeyError: When the request does not contain actor information (request.actor is None)

## Constraints:
    Preconditions:
    - The request object must have an actor attribute that is either a dictionary-like object or None
    - The key parameter must be a valid key that exists in the actor data if the actor exists
    
    Postconditions:
    - If actor data exists, returns the value for the requested key
    - If actor data is None, raises KeyError

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call actor(key, request)] --> B{request.actor is None?}
    B -- Yes --> C[Raise KeyError]
    B -- No --> D[Return request.actor[key]]
```

## Examples:
```python
# Basic usage in a template context
# Assuming request.actor = {"id": "user123", "role": "admin"}
value = actor("id", request)  # Returns "user123"
value = actor("role", request)  # Returns "admin"

# Error case
try:
    value = actor("id", request_with_no_actor)
except KeyError:
    # Handle missing actor data
    pass
```

## `datasette.default_magic_parameters.cookie` · *function*

## Summary:
Retrieves a cookie value from the request object by key.

## Description:
Extracts a specific cookie value from the HTTP request's cookies dictionary using the provided key. This function serves as a magic parameter resolver that allows templates and plugins to access client-side cookies during request processing.

## Args:
    key (str): The name of the cookie to retrieve
    request: The HTTP request object containing cookies in request.cookies dictionary

## Returns:
    str: The value of the requested cookie, or raises KeyError if cookie doesn't exist

## Raises:
    KeyError: When the specified cookie key is not present in request.cookies

## Constraints:
    Preconditions:
        - The request object must have a cookies attribute that behaves like a dictionary
        - The key parameter must be a string that can be used as a dictionary key
    Postconditions:
        - Returns the exact cookie value stored under the given key in request.cookies
        - Does not modify any state in the application

## Side Effects:
    None: This function performs no I/O operations or external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[cookie(key, request)] --> B{key in request.cookies?}
    B -- Yes --> C[return request.cookies[key]]
    B -- No --> D[raise KeyError]
```

## Examples:
```python
# Basic usage in a template or plugin
cookie_value = cookie('session_id', request)
# Returns the value of the 'session_id' cookie from the request

# Error handling example
try:
    user_preference = cookie('theme', request)
except KeyError:
    # Handle case when cookie is not present
    user_preference = 'default'
```

## `datasette.default_magic_parameters.now` · *function*

## Summary:
Returns various UTC timestamp formats based on the specified key parameter.

## Description:
This function generates and returns different representations of the current UTC time based on the provided key. It serves as a magic parameter handler that provides time-related values for Datasette queries. The function is designed to be called through Datasette's hook system and is typically used to inject current timestamps into SQL queries or templates.

The function extracts time-related logic into a separate component to provide standardized timestamp generation that can be used consistently across Datasette's query processing system. This separation allows for clean, reusable time formatting without duplicating timestamp generation logic throughout the codebase.

## Args:
    key (str): Specifies the format of timestamp to return. Must be one of "epoch", "date_utc", or "datetime_utc".
    request: The Datasette request object containing contextual information for the query execution.

## Returns:
    int or str: Returns an integer epoch timestamp when key is "epoch", a date string in ISO format when key is "date_utc", or a datetime string in ISO format with Z suffix when key is "datetime_utc".

## Raises:
    KeyError: Raised when the key parameter is not one of the supported values ("epoch", "date_utc", or "datetime_utc").

## Constraints:
    Preconditions:
    - The key parameter must be a string with one of the supported values
    - The function assumes UTC time zone context
    
    Postconditions:
    - The returned value matches the requested timestamp format exactly
    - All returned timestamps represent the current UTC time at function invocation

## Side Effects:
    None: This function has no side effects and is purely a deterministic time formatter.

## Control Flow:
```mermaid
flowchart TD
    A[Function Entry] --> B{key == "epoch"}
    B -- Yes --> C[Return int(time.time())]
    B -- No --> D{key == "date_utc"}
    D -- Yes --> E[Return date in ISO format]
    D -- No --> F{key == "datetime_utc"}
    F -- Yes --> G[Return datetime in ISO format with Z]
    F -- No --> H[Raise KeyError]
    C --> I[Exit]
    E --> I
    G --> I
    H --> I
```

## Examples:
    # Get current epoch timestamp
    result = now("epoch", request)  # Returns: 1703123456
    
    # Get current UTC date
    result = now("date_utc", request)  # Returns: "2023-12-21"
    
    # Get current UTC datetime
    result = now("datetime_utc", request)  # Returns: "2023-12-21T14:30:45Z"
    
    # Invalid key raises KeyError
    now("invalid_key", request)  # Raises: KeyError
```

## `datasette.default_magic_parameters.random` · *function*

...

## `datasette.default_magic_parameters.register_magic_parameters` · *function*

## Summary:
Registers and returns a collection of built-in magic parameter handlers for Datasette's query processing system.

## Description:
This function serves as the primary entry point for registering Datasette's default magic parameters. It returns a list of tuples where each tuple consists of a magic parameter name (string) and its corresponding handler function. These magic parameters provide dynamic contextual data that can be used within SQL queries and templates.

The function centralizes the registration of core magic parameters, making them available to Datasette's query processing engine and template system. This approach promotes code organization and ensures consistency in how magic parameters are exposed throughout the application.

## Args:
    None

## Returns:
    list[tuple[str, callable]]: A list of 5 tuples, each containing:
        - A string name identifying the magic parameter (one of "header", "actor", "cookie", "now", "random")
        - A callable function that handles the parameter resolution for that name
    Each tuple represents a registered magic parameter that can be used in Datasette queries.

## Raises:
    None

## Constraints:
    Preconditions:
    - The function must be called during Datasette's initialization phase
    - The referenced functions must be defined in the same module
    - The returned list structure must remain consistent with Datasette's magic parameter interface
    
    Postconditions:
    - Returns exactly 5 tuples in the specified order
    - Each tuple contains a valid string name and callable function reference
    - The returned list is suitable for direct consumption by Datasette's magic parameter system

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[register_magic_parameters()] --> B[Return list of 5 tuples]
    B --> C[("header", header_function)]
    B --> D[("actor", actor_function)]
    B --> E[("cookie", cookie_function)]
    B --> F[("now", now_function)]
    B --> G[("random", random_function)]
```

## Examples:
```python
# Typical usage in Datasette plugin system
magic_params = register_magic_parameters()

# Resulting structure:
# [
#     ("header", <function header at 0x...>),
#     ("actor", <function actor at 0x...>),
#     ("cookie", <function cookie at 0x...>),
#     ("now", <function now at 0x...>),
#     ("random", <function random at 0x...>)
# ]

# These can be consumed by Datasette's magic parameter system
# to provide dynamic values during query execution
```

