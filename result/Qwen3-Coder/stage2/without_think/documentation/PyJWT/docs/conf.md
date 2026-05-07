# `conf.py`

## `docs.conf.read` · *function*

## Summary:
Reads and returns the content of a file located relative to the configuration file's directory.

## Description:
This utility function provides a consistent way to read file contents relative to the documentation configuration file. It constructs a file path by joining the provided path components with the directory of the current configuration file, then reads and returns the entire file content as a string.

## Args:
    *parts (str): Variable-length argument list representing path components to join with the configuration file's directory.

## Returns:
    str: The complete content of the specified file as a string.

## Raises:
    FileNotFoundError: When the specified file path does not exist.
    PermissionError: When there are insufficient permissions to read the file.
    UnicodeDecodeError: When the file cannot be decoded using UTF-8 encoding.

## Constraints:
    Preconditions:
        - The configuration file (`docs/conf.py`) must exist and be readable
        - All path components in `*parts` must form a valid relative path from the configuration file's directory
    Postconditions:
        - The returned string contains the complete file content with all newlines preserved
        - The file is closed after reading

## Side Effects:
    - Reads from the filesystem
    - May raise file system related exceptions if the file doesn't exist or isn't readable

## Control Flow:
```mermaid
flowchart TD
    A[Call read(*parts)] --> B{Construct path}
    B --> C{Open file with UTF-8 encoding}
    C --> D{Read entire file content}
    D --> E[Return file content as string]
```

## Examples:
```python
# Read the README file in the same directory as conf.py
content = read("README.rst")

# Read a file in a subdirectory
content = read("source", "index.rst")

# Read a file in a parent directory
content = read("..", "LICENSE")
```

## `docs.conf.find_version` · *function*

## Summary:
Extracts the version string from a Python package's version file by parsing the `__version__` assignment.

## Description:
This function reads a file containing Python package version information and extracts the version string using regular expression pattern matching. It's commonly used in documentation configuration files to automatically retrieve the package version for inclusion in documentation metadata.

The function expects the version file to contain a line in the format `__version__ = "x.y.z"` or `__version__ = 'x.y.z'` at the beginning of the file. It's extracted as a separate utility function to encapsulate version parsing logic and avoid duplication across different configuration files or build processes.

## Args:
    *file_paths (str): Variable-length argument list of path components that are joined to form the file path to read. These paths are relative to the documentation configuration file's directory.

## Returns:
    str: The extracted version string from the file's `__version__` assignment.

## Raises:
    RuntimeError: When the version string cannot be found in the specified file, typically when the file doesn't contain a properly formatted `__version__ = "version"` line.

## Constraints:
    Preconditions:
        - The file specified by `file_paths` must exist and be readable
        - The file must contain a line matching the pattern `^__version__ = ['"]([^'"]*)['"]` at the beginning of the file
        - The file must be encoded in UTF-8
    Postconditions:
        - The function will either return a valid version string or raise RuntimeError
        - No modifications are made to the file or system state

## Side Effects:
    - Reads from the filesystem (the file specified by file_paths)
    - May raise file system related exceptions if the file doesn't exist or isn't readable

## Control Flow:
```mermaid
flowchart TD
    A[Call find_version(*file_paths)] --> B[Read file content using read()]
    B --> C[Apply regex pattern to find __version__ assignment]
    C --> D{Match found?}
    D -->|Yes| E[Return captured version string]
    D -->|No| F[Raise RuntimeError]
```

## Examples:
```python
# Extract version from setup.py
version = find_version("setup.py")

# Extract version from package/__init__.py  
version = find_version("package", "__init__.py")

# This would raise RuntimeError if no version line is found
try:
    version = find_version("nonexistent.py")
except RuntimeError as e:
    print(f"Version not found: {e}")
```

