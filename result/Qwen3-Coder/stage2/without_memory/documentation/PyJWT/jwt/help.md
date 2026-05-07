# `help.py`

## `jwt.help.info` · *function*

## Summary:
Collects and returns detailed system and runtime environment information including platform details, Python implementation specifics, and library versions.

## Description:
This function gathers comprehensive information about the current execution environment, including operating system details, Python implementation type and version, and the versions of cryptographic and JWT libraries. It handles various Python implementations (CPython, PyPy) and provides fallbacks for system information collection failures. This function is typically used for debugging, diagnostics, and environment reporting purposes.

## Args:
    None

## Returns:
    Dict[str, Dict[str, str]]: A nested dictionary containing:
        - "platform": Dictionary with "system" and "release" keys representing OS information
        - "implementation": Dictionary with "name" and "version" keys for Python implementation details
        - "cryptography": Dictionary with "version" key for the cryptography library version
        - "pyjwt": Dictionary with "version" key for the PyJWT library version

## Raises:
    None explicitly raised, though OSError may occur during platform information collection and is handled gracefully

## Constraints:
    Preconditions:
        - The cryptography and pyjwt libraries must be installed and importable
        - The platform module must be available (standard library)
        - Module-level constants cryptography_version and pyjwt_version must be defined
        
    Postconditions:
        - Always returns a dictionary with the same structure regardless of errors or missing information
        - Fallback values are provided for missing or inaccessible information

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start info()] --> B{platform.system() succeeds?}
    B -- Yes --> C[Get system and release]
    B -- No --> D[Set Unknown values]
    C --> E[Get python implementation]
    D --> E
    E --> F{Implementation is CPython?}
    F -- Yes --> G[Get python_version()]
    F -- No --> H{Implementation is PyPy?}
    G --> I[Return result]
    H -- Yes --> J[Get pypy_version_info]
    J --> K[Format PyPy version]
    K --> L[Return result]
    H -- No --> M[Set version to "Unknown"]
    M --> L
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
Prints system and library version information in JSON format for debugging and support purposes.

## Description:
Displays detailed information about the current platform, Python implementation, cryptography library version, and PyJWT library version in a structured JSON format. This function serves as a diagnostic tool to help users understand their environment configuration.

## Args:
    None

## Returns:
    None

## Raises:
    None

## Constraints:
    Preconditions:
    - Required modules (json, platform, sys, cryptography) must be importable
    - The `cryptography_version` and `pyjwt_version` variables must be defined at module level
    
    Postconditions:
    - System information is printed to standard output in JSON format
    - Output includes platform details, Python implementation info, and library versions

## Side Effects:
    - Prints formatted JSON output to standard output (stdout)
    - No external state mutations or I/O operations beyond stdout

## Control Flow:
```mermaid
flowchart TD
    A[main function entry] --> B[Call info()]
    B --> C[Process info() result]
    C --> D[Convert to JSON with sort_keys=True, indent=2]
    D --> E[Print JSON to stdout]
    E --> F[Function exits]
```

## Examples:
```python
# Typical usage in command line context
>>> main()
{
  "cryptography": {
    "version": "41.0.4"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.11.5"
  },
  "platform": {
    "release": "22.6.0",
    "system": "Darwin"
  },
  "pyjwt": {
    "version": "2.8.0"
  }
}
```

