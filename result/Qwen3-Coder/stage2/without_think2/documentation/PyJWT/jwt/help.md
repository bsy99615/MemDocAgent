# `help.py`

## `jwt.help.info` · *function*

## Summary:
Returns detailed system and runtime environment information including platform details, Python implementation specifics, and library versions.

## Description:
This function collects and organizes comprehensive information about the execution environment, particularly useful for debugging, compatibility checking, and system diagnostics. It gathers platform-specific data, Python implementation details, and version information for cryptographic and JWT libraries.

The function is designed to be robust against potential errors in platform detection while providing meaningful fallbacks. It specifically handles different Python implementations (CPython, PyPy) with appropriate version resolution strategies.

## Args:
    None

## Returns:
    Dict[str, object]: A nested dictionary containing:
        - "platform": Dictionary with "system" and "release" keys (both strings)
        - "implementation": Dictionary with "name" and "version" keys (both strings) for the Python implementation
        - "cryptography": Dictionary with "version" key (string) for the cryptography library version
        - "pyjwt": Dictionary with "version" key (string) for the PyJWT library version

## Raises:
    None explicitly raised, though platform.system() and platform.release() may raise OSError in rare cases (handled with fallbacks)

## Constraints:
    Preconditions:
        - The cryptography and pyjwt modules must be importable and have version attributes defined
        - Python environment must support platform module operations
    
    Postconditions:
        - Always returns a dictionary with the exact structure described
        - Fallback values are used when platform information cannot be determined

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start info()] --> B{platform.system() succeeds?}
    B -- Yes --> C{platform.release() succeeds?}
    C -- Yes --> D[Set platform_info with system and release]
    C -- No --> E[Set platform_info with Unknown values]
    B -- No --> F[Set platform_info with Unknown values]
    G[Get python implementation] --> H{Implementation is CPython?}
    H -- Yes --> I[Get version via platform.python_version()]
    H -- No --> J{Implementation is PyPy?}
    J -- Yes --> K[Extract PyPy version from sys.pypy_version_info]
    J -- No --> L[Set implementation_version to "Unknown"]
    M[Return structured dict] --> N[End]
```

## Examples:
```python
# Basic usage
env_info = info()
print(env_info["platform"]["system"])  # e.g., "Linux"
print(env_info["implementation"]["name"])  # e.g., "CPython"
print(env_info["cryptography"]["version"])  # e.g., "39.0.1"
```

## `jwt.help.main` · *function*

## Summary:
Prints detailed system and runtime environment information in JSON format.

## Description:
This function serves as the entry point for displaying comprehensive environment details including platform information, Python implementation specifics, and library versions. It calls the `info()` function to gather environment data and prints it as a formatted JSON string to standard output.

The function is designed to be a standalone command-line utility that provides diagnostic information about the current execution environment. It's extracted into its own function to separate the concern of data collection from data presentation, enabling reuse of the `info()` function in other contexts.

## Args:
    None

## Returns:
    None

## Raises:
    None

## Constraints:
    Preconditions:
        - The `info()` function must be callable and return a valid dictionary structure
        - Standard output must be writable
    
    Postconditions:
        - Prints a formatted JSON string to stdout
        - Function completes without raising exceptions from the core logic

## Side Effects:
    - Writes formatted JSON output to standard output (stdout)
    - Calls the `info()` function which may involve platform introspection

## Control Flow:
```mermaid
flowchart TD
    A[Start main()] --> B[Call info()]
    B --> C[Print JSON formatted result]
    C --> D[End]
```

## Examples:
```python
# Typical usage in command-line context
main()  # Prints environment info as JSON to stdout
```

