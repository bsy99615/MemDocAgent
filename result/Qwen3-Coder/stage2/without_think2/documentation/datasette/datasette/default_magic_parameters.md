# `default_magic_parameters.py`

## `datasette.default_magic_parameters.header` · *function*

## Summary:
Retrieves the value of an HTTP header from a request object, normalizing underscores to hyphens in the header key.

## Description:
This function extracts a specific HTTP header value from the request's headers dictionary. It normalizes the input key by replacing underscores with hyphens, which aligns with HTTP header naming conventions. The function is designed to be used as a magic parameter in Datasette's template rendering system, allowing templates to access HTTP headers easily.

## Args:
    key (str): The header name to retrieve, using underscores to represent hyphens in the actual HTTP header name.
    request: A request object containing the HTTP headers in its scope attribute.

## Returns:
    str: The value of the requested header if it exists, or an empty string if the header is not present.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - The request object must have a scope attribute containing a headers dictionary.
        - The headers dictionary must be compatible with dict() conversion.
        - The header key must be convertible to bytes using UTF-8 encoding.
    Postconditions:
        - The returned value is always a string, even when the header is missing.
        - The function handles byte-encoded headers properly by decoding them back to UTF-8 strings.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[header(key, request)] --> B[key.replace("_", "-")]
    B --> C[key.encode("utf-8")]
    C --> D[dict(request.scope["headers"])]
    D --> E[headers_dict.get(key, b"")]
    E --> F[decode("utf-8")]
    F --> G[Return result]
```

## Examples:
```python
# Example usage in a Datasette template context
# Assuming a request with header "User-Agent: Mozilla/5.0"
user_agent = header("user_agent", request)
# Returns: "Mozilla/5.0"

# When header is missing
content_type = header("content_type", request)
# Returns: ""

# When header contains special characters
accept_encoding = header("accept_encoding", request)
# Returns: "gzip, deflate, br" (or empty string if not present)
```

## `datasette.default_magic_parameters.actor` · *function*

## Summary:
Retrieves a specific attribute value from the request's actor object using a key.

## Description:
This function serves as a utility for accessing actor-specific data stored in a request object. It ensures that the actor exists before attempting to retrieve data, raising an exception if not present. The function is designed to be used within Datasette's magic parameters system to provide access to authenticated user information.

## Args:
    key (str): The attribute name to retrieve from the actor object.
    request: The HTTP request object containing the actor information.

## Returns:
    The value associated with the given key in the actor object.

## Raises:
    KeyError: When the request.actor is None, indicating no authenticated actor is available.

## Constraints:
    Preconditions:
        - The request object must have an actor attribute.
        - The actor attribute must not be None.
        - The key must be a valid attribute name that exists in the actor object.

    Postconditions:
        - If successful, returns the value of request.actor[key].
        - If actor is None, raises KeyError.

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
```python
# Assuming a request with an actor containing 'username' attribute
try:
    username = actor('username', request)
    print(f"User: {username}")
except KeyError:
    print("No authenticated user")
```

## `datasette.default_magic_parameters.cookie` · *function*

## Summary:
Retrieves a cookie value from an HTTP request object by key.

## Description:
This function provides a standardized way to access cookies stored in an HTTP request. It serves as a magic parameter resolver that allows datasette plugins and templates to easily retrieve cookie values without directly manipulating the request object's cookie storage.

## Args:
    key (str): The name of the cookie to retrieve
    request: An HTTP request object containing cookie data in a cookies attribute

## Returns:
    The value of the requested cookie if it exists, or raises a KeyError if the cookie is not found

## Raises:
    KeyError: When the specified cookie key does not exist in the request.cookies dictionary

## Constraints:
    Preconditions:
    - The request object must have a cookies attribute that behaves like a dictionary
    - The key parameter must be a string that can be used as a dictionary key
    
    Postconditions:
    - The function returns the exact value stored under the given key in request.cookies
    - No modifications are made to the request object or its cookies

## Side Effects:
    None - This function performs no I/O operations or external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[cookie(key, request)] --> B{request.cookies[key] exists?}
    B -- Yes --> C[Return request.cookies[key]]
    B -- No --> D[Raise KeyError]
```

## Examples:
```python
# Typical usage in a datasette plugin
value = cookie('session_id', request)
# Returns the value of the 'session_id' cookie if it exists

# Error handling example
try:
    user_preference = cookie('theme', request)
except KeyError:
    # Handle missing cookie case
    user_preference = 'default'
```

## `datasette.default_magic_parameters.now` · *function*

## Summary:
Returns various timestamp formats based on the specified key parameter.

## Description:
This function generates different representations of the current UTC time based on the provided key. It serves as a magic parameter handler for Datasette, allowing templates to access current timestamps in multiple formats. The function is designed to be called by the Datasette framework through its hookimpl mechanism.

## Args:
    key (str): Determines the format of the returned timestamp. Must be one of "epoch", "date_utc", or "datetime_utc".
    request: The HTTP request object (type not specified, but typically from web framework). Used for context but not directly processed.

## Returns:
    int or str: 
    - For key="epoch": Returns current Unix timestamp as integer
    - For key="date_utc": Returns current UTC date in ISO format (YYYY-MM-DD)
    - For key="datetime_utc": Returns current UTC datetime in ISO format (YYYY-MM-DDTHH:MM:SSZ)

## Raises:
    KeyError: When the key parameter is not one of the supported values ("epoch", "date_utc", "datetime_utc")

## Constraints:
    Preconditions:
    - The key parameter must be a string
    - The key parameter must be one of the predefined valid values
    - The function assumes UTC timezone for all timestamp generation
    
    Postconditions:
    - The function always returns either an integer or string value
    - The function raises KeyError for invalid keys

## Side Effects:
    None: This function has no side effects beyond returning computed values.

## Control Flow:
```mermaid
flowchart TD
    A[Start now()] --> B{key == "epoch"?}
    B -- Yes --> C[return int(time.time())]
    B -- No --> D{key == "date_utc"?}
    D -- Yes --> E[return date().isoformat()]
    D -- No --> F{key == "datetime_utc"?}
    F -- Yes --> G[return strftime("%Y-%m-%dT%H:%M:%S") + "Z"]
    F -- No --> H[raise KeyError]
    C --> I[End]
    E --> I
    G --> I
    H --> I
```

## Examples:
    # Example usage in Datasette template context:
    # {{ now("epoch") }} -> 1703123456 (Unix timestamp)
    # {{ now("date_utc") }} -> "2023-12-25" (ISO date format)
    # {{ now("datetime_utc") }} -> "2023-12-25T14:30:45Z" (ISO datetime format)
    # {{ now("invalid_key") }} -> KeyError raised

## `datasette.default_magic_parameters.random` · *function*

## Summary:
Generates a random hexadecimal string of specified length using cryptographically secure random bytes.

## Description:
This function handles Datasette's magic parameter "random" by generating a random hexadecimal string based on a key pattern. It extracts the desired length from keys that follow the "chars_{number}" format and produces a cryptographically secure random string of that length. The function is part of Datasette's magic parameter system, where it responds to specific key patterns to generate random identifiers or tokens.

## Args:
    key (str): A string key that must start with "chars_" followed by digits to trigger random string generation. The digits represent the desired length of the output string.
    request: The HTTP request object (currently unused in the implementation).

## Returns:
    str: A random hexadecimal string of exactly the length specified in the key. For example, if the key is "chars_10", returns a 10-character hex string containing only characters [0-9a-f].

## Raises:
    KeyError: When the key does not start with "chars_" or does not end with digits representing a valid number.

## Constraints:
    Precondition: The key must follow the format "chars_{positive_integer}" where {positive_integer} is a digit sequence.
    Postcondition: The returned string contains only hexadecimal characters [0-9a-f] and has exactly the length specified in the key.

## Side Effects:
    None: This function does not perform any I/O operations or mutate external state. It only uses os.urandom() for secure randomness.

## Control Flow:
```mermaid
flowchart TD
    A[Start random()] --> B{key starts with "chars_"?}
    B -- No --> C[Raise KeyError]
    B -- Yes --> D{key ends with digits?}
    D -- No --> C
    D -- Yes --> E[Extract num_chars]
    E --> F{num_chars is odd?}
    F -- Yes --> G[urandom_len = (num_chars + 1) / 2]
    F -- No --> H[urandom_len = num_chars / 2]
    G --> I[Generate random bytes]
    H --> I
    I --> J[Convert to hex]
    J --> K[Truncate to num_chars]
    K --> L[Return result]
```

## Examples:
    >>> random("chars_10", None)
    'a3f7b2c9d1'
    >>> random("chars_6", None)
    '4e8b2a'
    >>> random("chars_1", None)
    '7'
    >>> random("invalid_key", None)
    KeyError raised
```

## `datasette.default_magic_parameters.register_magic_parameters` · *function*

## Summary:
Registers a collection of default magic parameters for Datasette's template system, providing access to common request context data.

## Description:
This function creates and returns a list of tuples containing default magic parameter names and their corresponding resolver functions. These magic parameters allow Datasette templates to access common HTTP request context data such as headers, actor information, cookies, timestamps, and random values without requiring explicit parameter passing. The registered parameters are integrated into Datasette's hook system through the @hookimpl decorator.

## Args:
    None

## Returns:
    list[tuple[str, callable]]: A list of 2-tuples where each tuple contains:
        - A string name identifying the magic parameter (e.g., "header", "actor")
        - A callable function that resolves the parameter value given a request object

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - The function must be called during Datasette's initialization phase
        - All referenced resolver functions must be available in the module scope
        - The returned list structure must maintain the exact format expected by Datasette's hook system
        
    Postconditions:
        - The returned list contains exactly 5 tuples
        - Each tuple contains a valid parameter name string and a callable function
        - The order of parameters in the list is fixed and follows a logical grouping

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[register_magic_parameters()] --> B[Create list of 5 tuples]
    B --> C[Return list]
```

## Examples:
```python
# Typical usage within Datasette's plugin system
magic_params = register_magic_parameters()
# Returns: [("header", header), ("actor", actor), ("cookie", cookie), ("now", now), ("random", random)]

# In template context, these parameters become available:
# {{ header("user_agent") }}
# {{ actor("username") }}
# {{ cookie("session_id") }}
# {{ now("epoch") }}
# {{ random("chars_16") }}
```

