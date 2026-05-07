# `help.py`

## `jwt.help.info` · *function*

## Summary:
Returns detailed system and runtime environment information including platform details, Python implementation data, and library versions.

## Description:
This function collects comprehensive diagnostic information about the current execution environment, including operating system details, Python implementation specifics, and version numbers for cryptographic and JWT libraries. It serves as a utility for debugging, logging, and environment reporting purposes.

The function handles various Python implementations (CPython, PyPy) and gracefully manages potential errors when retrieving platform information. It's designed to provide consistent output regardless of the underlying system or Python distribution being used.

## Args:
    None

## Returns:
    Dict[str, Dict[str, str]]: A nested dictionary containing:
        - "platform": Dictionary with "system" and "release" keys describing the OS
        - "implementation": Dictionary with "name" and "version" keys for Python implementation
        - "cryptography": Dictionary with "version" key for cryptography library version
        - "pyjwt": Dictionary with "version" key for PyJWT library version

## Raises:
    None explicitly raised - though the platform.system() and platform.release() calls may raise OSError in rare cases, which are caught and handled gracefully by setting platform information to "Unknown".

## Constraints:
    Preconditions:
        - The cryptography and pyjwt modules must be importable and have version attributes defined at module level
        - The function should be callable in any Python environment
        
    Postconditions:
        - Always returns a dictionary with the exact structure described
        - Platform information defaults to "Unknown" if system calls fail
        - Implementation version is properly formatted for CPython and PyPy
        - Version information for cryptography and pyjwt is obtained from module-level version attributes

## Side Effects:
    None - This function performs no I/O operations or state modifications.

## Control Flow:
```mermaid
flowchart TD
    A[Start info()] --> B{platform.system() succeeds?}
    B -- Yes --> C{platform.release() succeeds?}
    C -- Yes --> D[Set platform_info]
    C -- No --> D[Set platform_info to Unknown]
    B -- No --> D[Set platform_info to Unknown]
    D --> E[Get python_implementation()]
    E --> F{Implementation is CPython?}
    F -- Yes --> G[Get python_version()]
    F -- No --> H{Implementation is PyPy?}
    H -- Yes --> I[Extract PyPy version info from sys.pypy_version_info]
    H -- No --> J[Set version to "Unknown"]
    G --> K[Build return dict]
    I --> K
    J --> K
    K --> L[Return result]
```

## Examples:
```python
# Basic usage
env_info = jwt.help.info()
print(env_info["platform"]["system"])  # e.g., "Linux"
print(env_info["implementation"]["name"])  # e.g., "CPython"
print(env_info["cryptography"]["version"])  # e.g., "39.0.1"

# Accessing all information
all_info = jwt.help.info()
print(f"OS: {all_info['platform']['system']} {all_info['platform']['release']}")
print(f"Python: {all_info['implementation']['name']} {all_info['implementation']['version']}")
print(f"Cryptography: {all_info['cryptography']['version']}")
print(f"PyJWT: {all_info['pyjwt']['version']}")
```

## `jwt.help.main` · *function*

## Summary:
Prints system and runtime environment information in JSON format for debugging and diagnostics.

## Description:
This function serves as a command-line interface entry point that displays comprehensive diagnostic information about the current execution environment. It collects system details, Python implementation data, and library versions using the `info()` helper function, then outputs the structured data as formatted JSON to standard output.

The function is typically invoked as part of a command-line tool or debugging utility to provide quick access to environment information for troubleshooting or logging purposes.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised - though the underlying `info()` function may raise exceptions if platform information retrieval fails, these are handled gracefully by the `info()` function itself.

## Constraints:
    Preconditions:
        - The `info()` function must be available in the module scope
        - All required libraries (cryptography, pyjwt) must be importable with version attributes
        - Standard output must be writable
        
    Postconditions:
        - JSON-formatted environment information is printed to stdout
        - Function completes without returning any value

## Side Effects:
    - Prints formatted JSON string to standard output (stdout)
    - No external state mutations or I/O operations beyond stdout printing

## Control Flow:
```mermaid
flowchart TD
    A[Start main()] --> B[Call info()]
    B --> C[Format result as JSON]
    C --> D[Print JSON to stdout]
    D --> E[Exit]
```

## Examples:
```python
# Typical usage in command-line context
$ python -m jwt.help
{
  "cryptography": {
    "version": "39.0.1"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.10.8"
  },
  "platform": {
    "release": "5.15.0-7625-generic",
    "system": "Linux"
  },
  "pyjwt": {
    "version": "2.6.0"
  }
}

# In programmatic context
import jwt.help
jwt.help.main()  # Prints environment info to console
```

