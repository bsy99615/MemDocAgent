# `help.py`

## `jwt.help.info` · *function*

## Summary:
Collects and returns detailed system and runtime environment information including platform details, Python implementation specifics, and library versions.

## Description:
This function gathers comprehensive information about the execution environment, including operating system details, Python implementation type and version, and the versions of cryptographic and JWT libraries. It handles potential errors in platform detection gracefully by falling back to "Unknown" values.

The function is extracted into its own component to centralize environment information gathering, making it reusable across different parts of the JWT library without duplicating platform detection logic.

## Returns:
A dictionary containing nested dictionaries with environment information:
- "platform": Dictionary with "system" and "release" keys
- "implementation": Dictionary with "name" and "version" keys for the Python implementation
- "cryptography": Dictionary with "version" key for the cryptography library version
- "pyjwt": Dictionary with "version" key for the PyJWT library version

## Raises:
OSError: When platform.system() or platform.release() fails during platform information collection

## Constraints:
Preconditions:
- The function assumes that `cryptography_version` and `pyjwt_version` module-level constants are defined
- The `platform` and `sys` modules are available and functional

Postconditions:
- Always returns a dictionary with the exact structure described
- Falls back gracefully to "Unknown" values when platform information cannot be determined

## Side Effects:
None

## Control Flow:
```mermaid
flowchart TD
    A[Start info()] --> B{platform.system() succeeds?}
    B -- Yes --> C[Get system and release]
    B -- No --> D[Set platform_info to Unknown]
    C --> E[Get python implementation]
    D --> E
    E --> F{Implementation is CPython?}
    F -- Yes --> G[Get python_version()]
    F -- No --> H{Implementation is PyPy?}
    G --> I[Set implementation_version]
    H -- Yes --> J[Get pypy_version_info]
    J --> K[Format PyPy version]
    H -- No --> L[Set implementation_version to Unknown]
    K --> I
    L --> I
    I --> M[Return full info dict]
```

## `jwt.help.main` · *function*

## Summary:
Outputs detailed system and runtime environment information in JSON format.

## Description:
This function serves as the command-line entry point for displaying environment information. It collects system details using the `info()` function and prints the result as a formatted JSON string to standard output. The function is designed to be called as part of a CLI utility for debugging or diagnostic purposes.

The logic is extracted into its own function to separate the concern of output formatting from the environment information collection, allowing the `info()` function to be reused in different contexts without coupling it to printing behavior.

## Args:
    None

## Returns:
    None

## Raises:
    None

## Constraints:
    Preconditions:
    - The `info()` function must be defined and accessible in the module scope
    - The `json` module must be available
    - Standard output must be writable
    
    Postconditions:
    - The function produces no return value
    - The output is printed to standard output as a formatted JSON string

## Side Effects:
    - Prints formatted JSON output to standard output (stdout)
    - May raise IOError if stdout is not writable

## Control Flow:
```mermaid
flowchart TD
    A[Start main()] --> B[Call info()]
    B --> C[Serialize result to JSON]
    C --> D[Print JSON to stdout]
    D --> E[End]
```

## Examples:
```python
# Typical usage in CLI context
$ python -m jwt.help
{
  "cryptography": {
    "version": "3.4.8"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.9.7"
  },
  "platform": {
    "release": "20.6.0",
    "system": "Darwin"
  },
  "pyjwt": {
    "version": "2.4.0"
  }
}
```

