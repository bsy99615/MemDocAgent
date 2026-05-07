# `__init__.py`

## `flower.utils.__init__.gen_cookie_secret` · *function*

## Summary:
Generates a cryptographically secure cookie secret using randomly generated UUID4 identifiers.

## Description:
Creates a base64-encoded string suitable for use as a cookie secret by concatenating two randomly generated UUID4 byte sequences and encoding them. This function is designed to produce unpredictable, secure secrets for web application sessions and authentication cookies.

## Args:
    None

## Returns:
    bytes: A base64-encoded byte string of 48 characters (representing 32 bytes of random data) that serves as a secure cookie secret for web applications.

## Raises:
    None

## Constraints:
    Preconditions:
    - The system must have access to the `uuid` and `base64` modules
    - The system must support the `uuid.uuid4()` function for generating random UUIDs
    
    Postconditions:
    - The returned value is always 48 characters long (base64 encoded representation of 32 random bytes)
    - The returned value contains only valid base64 characters (A-Z, a-z, 0-9, +, /, = padding)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start gen_cookie_secret()] --> B[Generate first UUID4 bytes]
    B --> C[Generate second UUID4 bytes]
    C --> D[Concatenate UUID4 bytes]
    D --> E[Base64 encode concatenated bytes]
    E --> F[Return base64-encoded secret]
```

## Examples:
```python
# Basic usage
secret = gen_cookie_secret()
print(len(secret))  # Output: 48
print(type(secret))  # Output: <class 'bytes'>

# Typical usage in web application configuration
COOKIE_SECRET = gen_cookie_secret()
```

## `flower.utils.__init__.bugreport` · *function*

## Summary:
Generates a formatted bug report string containing version information for Flower and its dependencies.

## Description:
This function collects version information from Flower, Tornado, Humanize, and the Celery application to create a standardized bug report string. It's designed to help diagnose compatibility issues by providing detailed version information for troubleshooting purposes.

The function is extracted into its own utility to centralize version reporting logic and make it reusable across different parts of the application. This promotes consistency in bug reporting and reduces code duplication.

## Args:
    app (celery.Celery, optional): A Celery application instance. If not provided, a new Celery instance is created automatically.

## Returns:
    str: A formatted bug report string in the format "flower   -> flower:{version} tornado:{tornado_version} humanize:{humanize_version}{app_bugreport}". When dependencies cannot be imported or accessed, returns an error message indicating dependency issues.

## Raises:
    ImportError: When required modules (celery, humanize, tornado) cannot be imported.
    AttributeError: When required version attributes are missing from imported modules.

## Constraints:
    Preconditions:
    - The function assumes that the required modules (celery, humanize, tornado) are available in the Python environment
    - The Celery app instance (either provided or created) must have a bugreport() method
    
    Postconditions:
    - Returns a properly formatted string with version information or an error message
    - Does not modify any global state or external resources

## Side Effects:
    - No I/O operations (files, network, stdout)
    - No external state mutations
    - No external service calls

## Control Flow:
```mermaid
flowchart TD
    A[Start bugreport()] --> B{app is None?}
    B -- Yes --> C[Create Celery app with celery.Celery()]
    B -- No --> C[Use provided app]
    C --> D[Import modules (celery, humanize, tornado)]
    D --> E{Import successful?}
    E -- No --> F[Return error message]
    E -- Yes --> G[Get flower version (__version__)]
    G --> H[Get tornado version (tornado.version)]
    H --> I[Get humanize version (getattr(humanize, '__version__', None) or getattr(humanize, 'VERSION'))]
    I --> J[Call app.bugreport()]
    J --> K[Format and return bug report string]
```

## Examples:
    # Basic usage with default Celery app
    report = bugreport()
    print(report)
    # Output: "flower   -> flower:1.0.0 tornado:6.1.0 humanize:3.12.0<some_celery_bugreport>"
    
    # Usage with custom Celery app
    from celery import Celery
    app = Celery('myapp')
    report = bugreport(app)
    print(report)
    # Output: "flower   -> flower:1.0.0 tornado:6.1.0 humanize:3.12.0<custom_celery_bugreport>"
    
    # Error case (missing dependencies)
    # If modules cannot be imported, returns error message
    # "Error when generating bug report: <error_message>. Have you installed correct versions of Flower's dependencies?"

## `flower.utils.__init__.abs_path` · *function*

## Summary:
Converts a given path to an absolute path by expanding user shortcuts and resolving relative paths against the current working directory.

## Description:
This utility function ensures that any given path is converted to an absolute path. It first expands user home directory shortcuts (like ~) using `os.path.expanduser()`, then checks if the resulting path is absolute. If not, it prepends the current working directory to make it absolute.

## Args:
    path (str): A file path that may be relative, contain user home shortcuts, or be absolute.

## Returns:
    str: An absolute path string that represents the same location as the input path.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The input `path` must be a string.
    - The current working directory must be accessible if a relative path needs to be resolved.
    
    Postconditions:
    - The returned path is guaranteed to be absolute (starts with '/').
    - The path is normalized and expanded.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start abs_path(path)] --> B{os.path.expanduser(path)}
    B --> C{os.path.isabs(result)}
    C -->|True| D[Return result]
    C -->|False| E[Get cwd via PWD env or os.getcwd()]
    E --> F[Join cwd + path with os.path.join()]
    F --> D
```

## Examples:
    >>> abs_path("~/documents/file.txt")
    "/home/user/documents/file.txt"
    
    >>> abs_path("relative/path/file.txt")
    "/current/working/directory/relative/path/file.txt"
    
    >>> abs_path("/absolute/path/file.txt")
    "/absolute/path/file.txt"

## `flower.utils.__init__.prepend_url` · *function*

## Summary:
Constructs a URL path by combining a prefix with a URL path, ensuring proper path formatting.

## Description:
Combines a URL path with a prefix by prepending the prefix to the URL after normalizing the prefix (removing leading/trailing slashes) and ensuring the result begins with a forward slash. This utility function is commonly used in web applications to build complete URL paths from base prefixes and relative paths.

## Args:
    url (str): The URL path to be appended after the prefix. May start with a forward slash.
    prefix (str): The prefix to prepend to the URL. Leading and trailing slashes are automatically removed.

## Returns:
    str: A combined URL path that starts with a forward slash, formed by joining the normalized prefix and URL.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions:
        - Both `url` and `prefix` must be strings
    Postconditions:
        - The returned string always starts with a forward slash
        - The prefix portion has leading/trailing slashes stripped
        - If the url parameter starts with a slash, it will appear in the result as-is

## Side Effects:
    None: This function has no side effects.

## Control Flow:
The function performs a simple string concatenation operation:
1. Strip leading/trailing slashes from prefix using strip('/')
2. Concatenate '/' + stripped_prefix + url
3. Return the resulting string

## Examples:
    >>> prepend_url('users/123', 'api/v1')
    '/api/v1/users/123'
    
    >>> prepend_url('users/123', '/api/v1/')
    '/api/v1/users/123'
    
    >>> prepend_url('/users/123', 'api/v1')
    '/api/v1//users/123'
    
    >>> prepend_url('', 'api/v1')
    '/api/v1'

## `flower.utils.__init__.strtobool` · *function*

## Summary:
Converts a string representation of truth to a numeric boolean value (1 for true, 0 for false).

## Description:
This utility function provides a standardized way to parse string inputs that represent boolean values. It accepts common string representations of truthy and falsy values and converts them to their numeric equivalents (1 and 0 respectively). The function is commonly used for parsing configuration values, environment variables, or user input that may be expressed as strings.

The function is extracted into its own utility to provide a consistent, reusable approach to string-to-boolean conversion throughout the application, rather than inlining this logic in multiple places.

## Args:
    val (str): A string representing a boolean value. Case-insensitive.

## Returns:
    int: Returns 1 for truthy values and 0 for falsy values.

## Raises:
    ValueError: Raised when the input string does not match any recognized truth value patterns.

## Constraints:
    Preconditions:
    - Input must be a string
    - Input must not be None
    
    Postconditions:
    - Return value is always either 0 or 1
    - Function raises ValueError for any unrecognized input

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start strtobool] --> B{val.lower()}
    B --> C{val in ('y','yes','t','true','on','1')}
    C -->|True| D[Return 1]
    C -->|False| E{val in ('n','no','f','false','off','0')}
    E -->|True| F[Return 0]
    E -->|False| G[Raise ValueError]
    D --> H[End]
    F --> H
    G --> H
```

## Examples:
    >>> strtobool('yes')
    1
    >>> strtobool('NO')
    0
    >>> strtobool('true')
    1
    >>> strtobool('false')
    0
    >>> strtobool('maybe')
    ValueError: invalid truth value 'maybe'
```

