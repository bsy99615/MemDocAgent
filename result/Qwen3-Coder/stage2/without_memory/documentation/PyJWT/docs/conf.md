# `conf.py`

## `docs.conf.read` · *function*

## Summary:
Reads and returns the complete content of a file located relative to the current configuration file's directory.

## Description:
A utility function that constructs a file path from the provided path components and reads the entire file content as a string. This function is designed to simplify file reading operations within Sphinx documentation configuration contexts, ensuring paths are resolved relative to the configuration file location.

## Args:
    *parts (str): Variable-length argument list representing path components to join and resolve to a file.

## Returns:
    str: The complete content of the specified file as a string.

## Raises:
    FileNotFoundError: When the specified file path does not exist.
    PermissionError: When the process lacks permission to read the specified file.
    UnicodeDecodeError: When the file cannot be decoded using UTF-8 encoding.

## Constraints:
    Preconditions:
    - The file path constructed from `*parts` must be valid and accessible
    - The file must be readable and exist at the specified location
    - The file must be encodable in UTF-8
    
    Postconditions:
    - The returned string contains the complete file content
    - No modifications are made to the file or system state

## Side Effects:
    - Reads from the filesystem
    - May raise file I/O related exceptions if the file doesn't exist or isn't readable

## Control Flow:
```mermaid
flowchart TD
    A[Call read(*parts)] --> B{Construct base path}
    B --> C{Join path components}
    C --> D{Open file with UTF-8 encoding}
    D --> E{Read entire file content}
    E --> F[Return file content as string]
```

## Examples:
```python
# Reading a README file
content = read("..", "README.md")

# Reading a configuration file
config_content = read("conf", "settings.json")
```

## `docs.conf.find_version` · *function*

## Summary:
Extracts version string from a specified file using regular expression pattern matching.

## Description:
Retrieves version information from a file by searching for a line matching the pattern "^__version__ = ['\"]([^'\"]*)['\"]". This function is commonly used in Python package documentation to dynamically fetch the package version for Sphinx configuration.

## Args:
    *file_paths: Variable length argument list of path components that are joined to form the file path to read.

## Returns:
    str: The version string extracted from the file.

## Raises:
    RuntimeError: When the version string cannot be found in the specified file.

## Constraints:
    Preconditions:
    - The file specified by file_paths must exist and be readable
    - The file must contain a line matching the pattern "^__version__ = ['\"]([^'\"]*)['\"]"
    
    Postconditions:
    - Returns a non-empty string containing the version identifier
    - Raises RuntimeError if version pattern is not found

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start find_version] --> B{Read file}
    B --> C{Regex match found?}
    C -->|Yes| D[Return version]
    C -->|No| E[Raise RuntimeError]
```

## Examples:
```python
# Typical usage in Sphinx conf.py
version = find_version("mypackage", "__init__.py")
# Returns: "1.2.3" (assuming the file contains "__version__ = '1.2.3'")
```

