# `conf.py`

## `docs.conf.read` · *function*

## Summary:
Reads the contents of a file located at a path constructed from the given parts relative to the current module's directory.

## Description:
This function provides a convenient way to read file contents from a location relative to the directory containing the current module (`docs/conf.py`). It constructs an absolute path by joining the current directory with the provided path components and opens the file in UTF-8 encoding to return its entire content as a string.

## Args:
    *parts (str): Variable-length argument list representing path components to join with the current module's directory path.

## Returns:
    str: The entire content of the file as a string.

## Raises:
    FileNotFoundError: If the file specified by the joined path does not exist.
    PermissionError: If the process does not have permission to read the file.
    UnicodeDecodeError: If the file cannot be decoded using UTF-8 encoding.

## Constraints:
    Preconditions:
        - The file path constructed from `*parts` must be valid and accessible.
        - The file must be readable.
    Postconditions:
        - The returned string contains the full content of the file.
        - No modifications are made to the file or its metadata.

## Side Effects:
    - Reads from the filesystem.
    - May raise I/O related exceptions if the file is inaccessible or unreadable.

## Control Flow:
```mermaid
flowchart TD
    A[Start read()] --> B[Get current module directory]
    B --> C[Join path components with directory]
    C --> D[Open file with UTF-8 encoding]
    D --> E{File opened successfully?}
    E -->|Yes| F[Read entire file content]
    F --> G[Return content as string]
    E -->|No| H[Raise appropriate exception]
    H --> I[End]
    G --> I
```

## Examples:
```python
# Reading a configuration file
config_content = read("conf", "config.ini")

# Reading a README file
readme_text = read("..", "README.md")
```

## `docs.conf.find_version` · *function*

## Summary:
Extracts the version string from a Python file containing a `__version__` variable assignment.

## Description:
This function reads a file that is expected to contain a `__version__` variable declaration in the format `__version__ = "x.y.z"` and extracts the version string. It is commonly used in documentation builds to dynamically retrieve the package version for display purposes.

## Args:
    *file_paths (str): Variable-length argument list of path components that are joined to form the path to the file containing the version string.

## Returns:
    str: The version string extracted from the file.

## Raises:
    RuntimeError: If the version string cannot be found in the specified file.

## Constraints:
    Preconditions:
        - The file specified by `*file_paths` must exist and be readable.
        - The file must contain a line matching the pattern `^__version__ = ['"]([^'"]*)['"]`.
    Postconditions:
        - The function returns a valid version string if found, or raises an exception if not found.

## Side Effects:
    - Reads from the filesystem via the `read()` helper function.
    - May raise I/O related exceptions if the file is inaccessible or unreadable.

## Control Flow:
```mermaid
flowchart TD
    A[Start find_version()] --> B[Read file content]
    B --> C[Search for version pattern]
    C --> D{Pattern found?}
    D -->|Yes| E[Extract and return version]
    D -->|No| F[Raise RuntimeError]
    E --> G[End]
    F --> G
```

## Examples:
```python
# Extract version from a package's __init__.py
version = find_version("mypackage", "__init__.py")

# Extract version from a version.py file
version = find_version("mypackage", "version.py")
```

