# `__init__.py`

## `flower.utils.__init__.gen_cookie_secret` · *function*

## Summary:
Generates a cryptographically secure random cookie secret using UUID4 values encoded in base64 format.

## Description:
This function creates a secure cookie secret by combining two randomly generated UUID4 identifiers and encoding them using base64. It's designed to produce a unique, unpredictable string suitable for use as a session cookie secret in web applications. The function is extracted into its own utility to centralize cookie secret generation logic and ensure consistency across the application.

## Args:
    None

## Returns:
    bytes: A base64-encoded byte string containing 48 characters (32 bytes of random data) that serves as a secure cookie secret.

## Raises:
    None

## Constraints:
    Preconditions:
    - The system must have access to the `uuid` and `base64` modules
    - The system must support the `uuid.uuid4()` function for generating random UUIDs
    
    Postconditions:
    - The returned value is always 48 bytes long (after base64 decoding)
    - The returned value contains cryptographically random data
    - The returned value is suitable for use as a cookie secret in web applications

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start gen_cookie_secret()] --> B[Generate first UUID4]
    B --> C[Generate second UUID4]
    C --> D[Concatenate UUID4 bytes]
    D --> E[Base64 encode concatenated bytes]
    E --> F[Return base64-encoded secret]
```

## Examples:
```python
# Basic usage
secret = gen_cookie_secret()
print(secret)  # b'...' (base64-encoded 32-byte random value)

# Usage in a web application context
cookie_secret = gen_cookie_secret()
# This would typically be set in application configuration
app_settings = {
    'cookie_secret': cookie_secret,
    'xsrf_cookies': True
}
```

## `flower.utils.__init__.bugreport` · *function*

tags. Let me rewrite it properly with the correct format.
Action: WRITE
<DOCUMENTATION>
## Summary:
Generates a formatted bug report string containing version information for Flower, Tornado, Humanize, and Celery dependencies.

## Description:
This utility function collects version information from key dependencies to aid in debugging and issue reporting. It is typically invoked when users request diagnostic information or when troubleshooting configuration problems. The function extracts version numbers from installed packages and formats them into a standardized string that helps developers quickly identify the environment setup.

The logic is extracted into its own function to centralize version collection and error handling, making it reusable across different parts of the application while providing consistent formatting for bug reports.

## Args:
    app (celery.Celery, optional): A Celery application instance. If None, a new Celery instance is created. Defaults to None.

## Returns:
    str: A formatted bug report string containing version information in the format "flower -> flower:{version} tornado:{tornado_version} humanize:{humanize_version}{celery_bugreport}", or an error message if dependencies cannot be imported or accessed.

## Raises:
    None explicitly raised, but catches ImportError and AttributeError exceptions internally.

## Constraints:
    Preconditions:
    - The function assumes that the required dependencies (celery, humanize, tornado) are available in the Python environment
    - If app is provided, it must be a valid Celery application instance
    
    Postconditions:
    - The returned string always follows the specified format pattern
    - Error handling ensures graceful degradation when dependencies are missing

## Side Effects:
    - No direct I/O operations
    - No external state mutations
    - No external service calls
    - May trigger import operations for internal modules

## Control Flow:
```mermaid
flowchart TD
    A[Start bugreport()] --> B{app is None?}
    B -- Yes --> C[Create new Celery instance]
    B -- No --> D[Use provided app]
    C --> E[Import dependencies]
    D --> E
    E --> F[Try to collect version info]
    F --> G{ImportError/AttributeError?}
    G -- Yes --> H[Return error message]
    G -- No --> I[Format and return bug report]
```

## Examples:
    # Basic usage with default app
    report = bugreport()
    # Returns: "flower   -> flower:1.0.0 tornado:6.1.0 humanize:3.12.0<Celery bugreport>"
    
    # Usage with custom app
    from celery import Celery
    app = Celery('myapp')
    report = bugreport(app)
    # Returns: "flower   -> flower:1.0.0 tornado:6.1.0 humanize:3.12.0<Celery bugreport>"
    
    # Error case (missing dependencies)
    # Returns: "Error when generating bug report: [error message]. Have you installed correct versions of Flower's dependencies?"

## `flower.utils.__init__.abs_path` · *function*

## Summary:
Converts a given path to an absolute path by expanding user references and joining with current working directory when necessary.

## Description:
This function ensures that any given path is converted to an absolute path. It first expands user home directory references (like ~) using `os.path.expanduser()`, then checks if the result is already absolute. If not, it prepends the current working directory to make it absolute.

## Args:
    path (str): A file path that may be relative or contain user home directory references (e.g., ~/documents/file.txt)

## Returns:
    str: An absolute path string guaranteed to start with '/' (on Unix-like systems) or drive letter (on Windows)

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
        - The input path must be a string
        - The current working directory must be accessible
    
    Postconditions:
        - The returned path is always absolute
        - The returned path is normalized (no '.' or '..' components)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start abs_path] --> B{os.path.expanduser(path)}
    B --> C{os.path.isabs(path)}
    C -->|True| D[Return path]
    C -->|False| E[Get cwd via PWD env or getcwd()]
    E --> F[Join cwd with path]
    F --> D
```

## Examples:
    >>> abs_path("~/documents/file.txt")
    '/home/user/documents/file.txt'
    
    >>> abs_path("relative/path/file.txt")
    '/current/working/directory/relative/path/file.txt'
    
    >>> abs_path("/absolute/path/file.txt")
    '/absolute/path/file.txt'

## `flower.utils.__init__.prepend_url` · *function*

## Summary:
Combines a URL path with a prefixed path segment, ensuring proper URL formatting with leading and trailing slash handling.

## Description:
Prepends a URL path with a prefix path segment, automatically normalizing the prefix by removing leading/trailing slashes and ensuring the result begins with a forward slash. This utility function is commonly used in web applications to construct complete URL paths from base prefixes and relative paths.

## Args:
    url (str): The URL path to append after the prefix. May be empty or start with a forward slash.
    prefix (str): The prefix path segment to prepend to the URL. Leading/trailing slashes are automatically stripped.

## Returns:
    str: A properly formatted URL path beginning with a forward slash, combining the prefix and URL segments.

## Raises:
    None: This function does not raise any exceptions under normal operation.

## Constraints:
    Preconditions:
        - Both arguments must be strings
    Postconditions:
        - The returned string always begins with a forward slash
        - The prefix portion has leading/trailing slashes removed
        - The result is a valid URL path fragment

## Side Effects:
    None: This function has no side effects and is pure.

## Control Flow:
```mermaid
flowchart TD
    A[prepend_url(url, prefix)] --> B[Strip prefix of leading/trailing slashes]
    B --> C[Concatenate '/' + stripped_prefix + url]
    C --> D[Return result]
```

## Examples:
    >>> prepend_url('users/123', 'api/v1')
    '/api/v1users/123'
    
    >>> prepend_url('/users/123', 'api/v1/')
    '/api/v1/users/123'
    
    >>> prepend_url('users/123', '/api/v1/')
    '/api/v1/users/123'
    
    >>> prepend_url('', 'api/v1/')
    '/api/v1'
    
    >>> prepend_url('users/123', '')
    '/users/123'
```

## `flower.utils.__init__.strtobool` · *function*

## Summary:
Converts string representations of truth values to integer boolean equivalents (1 for true, 0 for false).

## Description:
This utility function provides a standardized way to parse string inputs that represent boolean values. It accepts various common string representations of truth values and converts them to their integer equivalents (1 for true, 0 for false). The function is designed to handle typical user input and configuration values that might come as strings rather than native boolean types.

The function extracts this logic into a separate utility to avoid code duplication and ensure consistent interpretation of truth-like strings across the application. Rather than inlining this conversion logic in multiple places, this centralized implementation ensures uniform behavior and makes future modifications easier.

## Args:
    val (str): A string representation of a boolean value. Expected to be one of the recognized truth value strings.

## Returns:
    int: Returns 1 for true values and 0 for false values. Specifically:
        - Returns 1 for strings: 'y', 'yes', 't', 'true', 'on', '1'
        - Returns 0 for strings: 'n', 'no', 'f', 'false', 'off', '0'

## Raises:
    ValueError: Raised when the input string does not match any of the recognized truth value patterns. The error message includes the invalid input value for debugging purposes.

## Constraints:
    Preconditions:
        - Input must be a string type
        - Input must be a valid string representation of a boolean value (one of the predefined values)
    
    Postconditions:
        - Output is always either 0 or 1
        - Input string is converted to lowercase for comparison (case-insensitive)

## Side Effects:
    None: This function has no side effects. It performs only string operations and returns a computed value.

## Control Flow:
```mermaid
flowchart TD
    A[Start strtobool] --> B{Input val}
    B --> C{val.lower() in true_values?}
    C -->|Yes| D[Return 1]
    C -->|No| E{val.lower() in false_values?}
    E -->|Yes| F[Return 0]
    E -->|No| G[Raise ValueError]
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

