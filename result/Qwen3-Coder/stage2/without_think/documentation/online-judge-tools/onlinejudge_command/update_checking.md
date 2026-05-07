# `update_checking.py`

## `onlinejudge_command.update_checking.describe_status_code` · *function*

## Summary:
Formats an HTTP status code with its standard descriptive message.

## Description:
Converts an HTTP status code integer into a human-readable string format combining the numeric code and its standard textual description from the HTTP protocol. This utility function is commonly used for displaying HTTP response status information in a user-friendly format.

## Args:
    status_code (int): The HTTP status code to describe, typically in the range 100-599 representing standard HTTP status codes.

## Returns:
    str: A formatted string containing the status code followed by its standard HTTP message (e.g., "200 OK").

## Raises:
    KeyError: When the status_code is not present in http.client.responses dictionary, which occurs for invalid or non-standard HTTP status codes.

## Constraints:
    Preconditions: The status_code must be a valid integer that exists in http.client.responses dictionary (typically 100-599 for standard HTTP status codes).
    Postconditions: The returned string will always contain the status code and its corresponding HTTP message separated by a space.

## Side Effects:
    None: This function has no side effects and is purely a formatting utility.

## Control Flow:
```mermaid
flowchart TD
    A[Input status_code] --> B{Valid status_code?}
    B -->|Yes| C[Lookup http.client.responses[status_code]]
    C --> D[Format "{} {}".format(status_code, message)]
    D --> E[Return formatted string]
    B -->|No| F[KeyError raised]
    F --> G[Exception propagation]
```

## Examples:
    >>> describe_status_code(200)
    '200 OK'
    
    >>> describe_status_code(404)
    '404 Not Found'
    
    >>> describe_status_code(500)
    '500 Internal Server Error'

## `onlinejudge_command.update_checking.request` · *function*

## Summary:
Sends an HTTP request with standardized logging and optional status checking.

## Description:
A wrapper around requests.Session.request() that provides consistent logging of HTTP operations and optional automatic status code validation. This function centralizes HTTP request handling with standardized logging practices and follows the principle of separation of concerns by isolating HTTP communication logic from business logic.

## Args:
    method (str): The HTTP method to use ('GET' or 'POST')
    url (str): The target URL for the HTTP request
    session (requests.Session): The requests session object to use for making the request
    raise_for_status (bool): Whether to automatically raise an exception for HTTP error status codes (default: True)
    **kwargs: Additional arguments to pass to the underlying requests.Session.request() method

## Returns:
    requests.Response: The HTTP response object from the completed request

## Raises:
    requests.exceptions.RequestException: When raise_for_status is True and the HTTP response status indicates an error (4xx or 5xx codes)

## Constraints:
    Preconditions: 
    - method must be either 'GET' or 'POST'
    - session must be a valid requests.Session instance
    - url must be a valid string URL
    - All kwargs must be valid arguments for requests.Session.request()

    Postconditions:
    - The returned Response object contains the complete HTTP response information
    - All HTTP request logging has been performed
    - If raise_for_status is True, the response status code has been validated

## Side Effects:
    - Writes log messages to the module's logger at INFO and DEBUG levels
    - Makes an actual HTTP network request via the provided session
    - May redirect to a different URL if the server responds with a redirect status code

## Control Flow:
```mermaid
flowchart TD
    A[Start request] --> B{Method valid?}
    B -->|No| C[AssertionError]
    B -->|Yes| D[Set default allow_redirects=True]
    D --> E[Log method and URL]
    E --> F{Data in kwargs?}
    F -->|Yes| G[Log data (DEBUG)]
    G --> H[Make HTTP request]
    H --> I{Response redirected?}
    I -->|Yes| J[Log redirect URL (INFO)]
    J --> K[Log status code description (INFO)]
    K --> L{raise_for_status=True?}
    L -->|Yes| M[Check status code (raises if error)]
    M --> N[Return response]
    L -->|No| N
```

## Examples:
    # Basic GET request with logging
    session = requests.Session()
    response = request('GET', 'https://api.example.com/data', session)
    
    # POST request with custom headers
    response = request('POST', 'https://api.example.com/submit', session, 
                      data={'key': 'value'}, 
                      headers={'Content-Type': 'application/json'})
    
    # Request without automatic status checking
    response = request('GET', 'https://httpbin.org/status/404', session, 
                      raise_for_status=False)

## `onlinejudge_command.update_checking.get_latest_version_from_pypi` · *function*

## Summary:
Retrieves the latest version of a specified package from PyPI with local caching to minimize network requests.

## Description:
Fetches the most recent version number of a given package from the Python Package Index (PyPI) while implementing a local cache to reduce redundant network calls. This function is used for checking if updates are available for the online judge command-line tools.

## Args:
    package_name (str): The name of the PyPI package to check for updates. Must be a valid package identifier.

## Returns:
    str: The latest version string of the specified package. Returns '0.0.0' if the version cannot be determined due to network issues or other failures.

## Raises:
    None explicitly raised, though underlying network operations may raise exceptions that are caught and logged.

## Constraints:
    Preconditions:
    - package_name must be a valid string identifying a PyPI package
    - Network connectivity should be available for fetching latest versions
    
    Postconditions:
    - A local cache file is created/updated with the fetched version information
    - The returned version string follows semantic versioning format

## Side Effects:
    - Makes a network request to https://pypi.org/pypi/{package_name}/json
    - Reads from and writes to a local cache file at user cache directory
    - Logs debug and warning messages to the module's logger
    - Creates parent directories for the cache file if they don't exist

## Control Flow:
```mermaid
flowchart TD
    A[Start get_latest_version_from_pypi] --> B{Cache file exists?}
    B -->|No| C[Fetch from PyPI]
    B -->|Yes| D[Load cache data]
    D --> E{Cache expired (>8h)?}
    E -->|No| F[Return cached version]
    E -->|Yes| G[Fetch from PyPI]
    G --> H[Update cache with new version]
    H --> I[Return version]
    C --> H
```

## Examples:
    # Check latest version of the main onlinejudge package
    latest_version = get_latest_version_from_pypi('onlinejudge')
    
    # Check latest version of the command-line tool
    latest_version = get_latest_version_from_pypi('onlinejudge-command')
```

## `onlinejudge_command.update_checking.is_update_available_on_pypi` · *function*

## Summary:
Determines whether a newer version of a specified package is available on PyPI compared to the currently installed version.

## Description:
Checks if an update is available for a given package by comparing the current version with the latest version retrieved from PyPI. This function is used to notify users when newer versions of the onlinejudge command-line tools are available.

## Args:
    package_name (str): The name of the PyPI package to check for updates. Must be a valid package identifier.
    current_version (str): The currently installed version of the package in semantic version format (e.g., "1.2.3").

## Returns:
    bool: True if a newer version is available on PyPI, False otherwise. Returns False if version comparison fails, if the current version equals the latest version, or if the current version is greater than the latest version.

## Raises:
    None explicitly raised by this function, though underlying operations in get_latest_version_from_pypi may raise exceptions that are handled internally.

## Constraints:
    Preconditions:
    - package_name must be a valid string identifying a PyPI package
    - current_version must be a valid semantic version string
    - Network connectivity should be available for fetching latest versions (though caching is implemented)
    
    Postconditions:
    - No side effects beyond potential network requests and cache operations performed by get_latest_version_from_pypi

## Side Effects:
    - Makes a network request to PyPI to fetch the latest version information (via get_latest_version_from_pypi)
    - May read from and write to a local cache file (via get_latest_version_from_pypi)
    - Logs debug and warning messages to the module's logger (via get_latest_version_from_pypi)

## Control Flow:
```mermaid
flowchart TD
    A[Start is_update_available_on_pypi] --> B[Parse current_version with StrictVersion]
    B --> C[Get latest version from PyPI via get_latest_version_from_pypi]
    C --> D[Parse latest version with StrictVersion]
    D --> E[Compare versions: current < latest?]
    E -->|True| F[Return True (update available)]
    E -->|False| G[Return False (no update)]
```

## Examples:
    # Check if the main onlinejudge package has updates
    update_available = is_update_available_on_pypi('onlinejudge', '1.2.3')
    
    # Check if the command-line tool has updates
    update_available = is_update_available_on_pypi('onlinejudge-command', '0.1.0')
```

## `onlinejudge_command.update_checking.run_for_package` · *function*

## Summary:
Checks if a package is up-to-date by comparing its current version with the latest version available on PyPI, and logs update notifications when applicable.

## Description:
This function determines whether an update is available for a specified package by comparing the current version with the latest version from PyPI. When an update is detected, it logs a warning message with version details and an informational message with installation instructions. It's designed to be called periodically to notify users about available updates for the onlinejudge command-line tools.

## Args:
    package_name (str): The name of the PyPI package to check for updates. Must be a valid package identifier.
    current_version (str): The currently installed version of the package in semantic version format (e.g., "1.2.3").

## Returns:
    bool: Returns True if the package is up-to-date (no newer version available) or if update checking fails. Returns False if a newer version is available on PyPI.

## Raises:
    None explicitly raised by this function, though underlying operations in helper functions may raise exceptions that are handled internally.

## Constraints:
    Preconditions:
    - package_name must be a valid string identifying a PyPI package
    - current_version must be a valid semantic version string
    - Network connectivity should be available for fetching latest versions (though caching is implemented)
    
    Postconditions:
    - No side effects beyond potential network requests and cache operations performed by helper functions
    - Logger messages are emitted when updates are available

## Side Effects:
    - Makes network requests to PyPI to fetch version information (via helper functions)
    - May read from and write to a local cache file (via helper functions)
    - Emits log messages at WARNING level when updates are available
    - Emits log messages at INFO level when updates are available (with installation command)

## Control Flow:
```mermaid
flowchart TD
    A[Start run_for_package] --> B[Check if update available via is_update_available_on_pypi]
    B --> C{Is update available?}
    C -->|No| D[Set is_updated = True]
    C -->|Yes| E[Set is_updated = False]
    D --> F[Return True (up-to-date)]
    E --> G[Log WARNING with version info]
    G --> H[Log INFO with pip install command]
    H --> F
```

## Examples:
    # Check if the main onlinejudge package is up-to-date
    is_current = run_for_package(package_name='onlinejudge', current_version='1.2.3')
    
    # Check if the command-line tool is up-to-date
    is_current = run_for_package(package_name='onlinejudge-command', current_version='0.1.0')
```

