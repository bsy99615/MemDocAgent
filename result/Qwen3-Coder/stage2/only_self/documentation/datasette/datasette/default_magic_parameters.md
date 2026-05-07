# `default_magic_parameters.py`

## `datasette.default_magic_parameters.header` · *function*

## Summary:
Extracts an HTTP header value from a request object using a normalized key.

## Description:
Retrieves the value of a specified HTTP header from the request scope. The header key is normalized by replacing underscores with hyphens and encoded to UTF-8 before lookup. This function is part of Datasette's magic parameters system that provides convenient access to request data through special parameter names.

## Args:
    key (str): The header name to look up, with underscores converted to hyphens for normalization
    request: A request object containing scope with headers dictionary

## Returns:
    str: The decoded header value if found, or empty string if the header is not present

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The request object must have a scope attribute with a headers dictionary
    - The key parameter must be a string
    
    Postconditions:
    - Returns a string value (empty if header not found)
    - The returned string is UTF-8 decoded from the raw bytes

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start header() function] --> B[key = key.replace("_", "-")]
    B --> C[key = key.encode("utf-8")]
    C --> D[headers_dict = dict(request.scope["headers"])]
    D --> E[return headers_dict.get(key, b"").decode("utf-8")]
```

## Examples:
    # Extract User-Agent header
    user_agent = header("user_agent", request)
    
    # Extract Content-Type header  
    content_type = header("content_type", request)
```

## `datasette.default_magic_parameters.actor` · *function*

## Summary:
Retrieves a specific attribute from the actor associated with a request, raising an exception when no actor is present.

## Description:
This function serves as a safe accessor for retrieving data from the actor object attached to a request. It's designed to prevent errors when attempting to access actor attributes when no actor has been authenticated or set for the request. The function is implemented as a Datasette hook, indicating it's part of the framework's plugin architecture for handling authentication-related data.

## Args:
    key (str): The attribute name to retrieve from the actor dictionary
    request: A request object containing an actor attribute (dictionary-like)

## Returns:
    The value associated with the specified key in the request.actor dictionary

## Raises:
    KeyError: When the request.actor attribute is None, indicating no authenticated actor is available

## Constraints:
    Preconditions:
    - The request parameter must have an actor attribute
    - The actor attribute must be a dictionary-like object if not None
    - The key parameter must be a valid key for the actor dictionary
    
    Postconditions:
    - If successful, returns the value stored under the specified key in the actor dictionary
    - If actor is None, raises KeyError immediately

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start actor()] --> B{request.actor is None?}
    B -- Yes --> C[Raise KeyError]
    B -- No --> D[return request.actor[key]]
```

## Examples:
    # Typical usage in a Datasette plugin hook
    try:
        user_id = actor('id', request)
        # Use user_id for authorization checks
    except KeyError:
        # Handle unauthenticated request
        return unauthorized_response()
```

## `datasette.default_magic_parameters.cookie` · *function*

## Summary:
Retrieves a cookie value from an HTTP request object using a specified key.

## Description:
This function provides access to HTTP cookies stored in a request object, serving as a magic parameter that can be used within Datasette's query or template systems. It extracts a specific cookie value by key from the request's cookies dictionary.

## Args:
    key (str): The name of the cookie to retrieve from the request.
    request: An HTTP request object containing a cookies dictionary attribute.

## Returns:
    The value associated with the specified cookie key in the request's cookies dictionary.

## Raises:
    KeyError: When the specified cookie key does not exist in the request's cookies.

## Constraints:
    Preconditions:
    - The request parameter must have a cookies attribute that behaves like a dictionary
    - The key parameter must be a valid key for the cookies dictionary
    
    Postconditions:
    - Returns the cookie value if the key exists
    - Raises KeyError if the key doesn't exist

## Side Effects:
    None - This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[cookie(key, request)] --> B{request.cookies[key] exists?}
    B -- Yes --> C[Return request.cookies[key]]
    B -- No --> D[Raise KeyError]
```

## Examples:
    # Typical usage in Datasette context
    # Assuming a request with cookies={'session_id': 'abc123'}
    cookie_value = cookie('session_id', request)
    # Returns: 'abc123'
    
    # Error case
    try:
        cookie('nonexistent', request)
    except KeyError:
        # Handle missing cookie case
        pass
```

## `datasette.default_magic_parameters.now` · *function*

## Summary:
Returns various UTC timestamp formats based on the specified key parameter.

## Description:
This function generates different UTC timestamp representations based on the provided key. It serves as a magic parameter handler for Datasette, allowing templates to insert current timestamps in various formats. The function is designed to be called by Datasette's magic parameter system and is decorated with @hookimpl to integrate with the plugin architecture.

## Args:
    key (str): Determines the timestamp format to return. Valid values are "epoch", "date_utc", and "datetime_utc".
    request: HTTP request object (currently unused in the implementation).

## Returns:
    int or str: Returns an integer epoch timestamp when key is "epoch", a date string in ISO format when key is "date_utc", or a datetime string in ISO format with Z suffix when key is "datetime_utc".

## Raises:
    KeyError: Raised when the key parameter is not one of the supported values ("epoch", "date_utc", "datetime_utc").

## Constraints:
    Preconditions: The key parameter must be one of the supported string values.
    Postconditions: The returned value matches the expected format for the given key.

## Side Effects:
    None: This function has no side effects beyond returning computed values.

## Control Flow:
```mermaid
flowchart TD
    A[Call now(key, request)] --> B{key == "epoch"?}
    B -- Yes --> C[Return int(time.time())]
    B -- No --> D{key == "date_utc"?}
    D -- Yes --> E[Return date().isoformat()]
    D -- No --> F{key == "datetime_utc"?}
    F -- Yes --> G[Return strftime("%Y-%m-%dT%H:%M:%S") + "Z"]
    F -- No --> H[raise KeyError]
```

## Examples:
```python
# Get current epoch timestamp
timestamp = now("epoch", request)  # Returns: 1703123456

# Get current UTC date
date_str = now("date_utc", request)  # Returns: "2023-12-21"

# Get current UTC datetime
datetime_str = now("datetime_utc", request)  # Returns: "2023-12-21T14:30:45Z"

# Invalid key raises KeyError
try:
    now("invalid_key", request)
except KeyError:
    # Handle invalid key
    pass
```

## `datasette.default_magic_parameters.random` · *function*

## Summary:
Generates cryptographically secure random hexadecimal strings for magic parameters with specific naming patterns.

## Description:
This function implements a magic parameter handler that generates random hexadecimal strings when a parameter key follows the pattern "chars_{number}". It's designed to provide cryptographically secure random data for use in URLs, tokens, or identifiers. The function extracts the desired length from the key, generates the appropriate amount of random bytes, converts them to hexadecimal, and truncates to the requested length.

## Args:
    key (str): Parameter key that must start with "chars_" followed by digits to trigger random generation
    request: HTTP request object (unused in current implementation)

## Returns:
    str: A random hexadecimal string of exactly the requested length specified in the key

## Raises:
    KeyError: When the key doesn't follow the "chars_{number}" pattern

## Constraints:
    Preconditions:
    - The key parameter must start with "chars_"
    - The portion after "chars_" must be convertible to an integer
    - The integer must be positive
    
    Postconditions:
    - Returns a string of exactly the specified number of characters
    - All characters are valid hexadecimal digits (0-9, a-f)
    - The returned string is cryptographically random

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start random()] --> B{key starts with "chars_"?}
    B -- No --> C[Raise KeyError]
    B -- Yes --> D{Last part is digit?}
    D -- No --> C
    D -- Yes --> E[Parse num_chars]
    E --> F{num_chars is odd?}
    F -- Yes --> G[urandom_len = (num_chars+1)/2]
    F -- No --> H[urandom_len = num_chars/2]
    G --> I[H]
    I --> J[os.urandom(urandom_len).hex()]
    J --> K[Truncate to num_chars]
    K --> L[Return result]
```

## Examples:
    # Generate a 16-character random hex string
    random("chars_16", request)  # Returns something like "a3f7b2c9d4e1a8f2"
    
    # Generate a 8-character random hex string  
    random("chars_8", request)   # Returns something like "b7d2f9a1"
    
    # Invalid key raises KeyError
    random("invalid_key", request)  # Raises KeyError

## `datasette.default_magic_parameters.register_magic_parameters` · *function*

## Summary:
Registers and returns the collection of built-in magic parameter handlers used by Datasette.

## Description:
This function serves as a registry for Datasette's built-in magic parameters, returning a list of tuples where each tuple contains a parameter name string and its corresponding handler function. These magic parameters provide convenient access to request data, authentication information, timestamps, and random values during query processing and template rendering.

The registered parameters include:
- header: Extracts HTTP headers from requests
- actor: Retrieves authenticated actor attributes
- cookie: Accesses HTTP cookies from requests
- now: Provides current UTC timestamps in various formats
- random: Generates cryptographically secure random hexadecimal strings

This function is typically called by Datasette's plugin system to make these magic parameters available throughout the application.

## Args:
    None

## Returns:
    list[tuple[str, callable]]: A list of tuples where each tuple contains:
        - A string parameter name (e.g., "header", "actor")
        - A callable function that handles that parameter type

## Raises:
    None

## Constraints:
    Preconditions:
    - The function must be called in a Datasette context where the dependent functions are properly defined
    - All referenced functions (header, actor, cookie, now, random) must be available in the module scope
    
    Postconditions:
    - Returns a list of exactly 5 tuples
    - Each tuple contains a valid string name and callable function reference
    - The returned list maintains the order: header, actor, cookie, now, random

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[register_magic_parameters()] --> B[Return list of 5 tuples]
    B --> C[("header", header)]
    B --> D[("actor", actor)]
    B --> E[("cookie", cookie)]
    B --> F[("now", now)]
    B --> G[("random", random)]
```

## Examples:
    # Typical usage in Datasette plugin system
    magic_params = register_magic_parameters()
    # Returns: [("header", header), ("actor", actor), ("cookie", cookie), ("now", now), ("random", random)]
    
    # Accessing individual parameter handlers
    header_handler = magic_params[0][1]  # Gets the header function
    header_name = magic_params[0][0]    # Gets "header"
```

