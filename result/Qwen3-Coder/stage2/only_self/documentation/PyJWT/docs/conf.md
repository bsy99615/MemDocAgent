# `conf.py`

## `docs.conf.read` · *function*

## Summary:
Reads and returns the contents of a file located relative to the current module's directory.

## Description:
This utility function provides a convenient way to read file contents in a cross-platform manner. It constructs a file path by joining the current module's directory with the provided path components and returns the entire file content as a string. This pattern is commonly used in documentation configurations to read version information, license files, or other metadata.

## Args:
    *parts (str): Variable length argument list representing path components to join with the current module's directory.

## Returns:
    str: The complete content of the file as a string, with all content read as UTF-8 encoded text.

## Raises:
    FileNotFoundError: When the specified file path does not exist.
    PermissionError: When the process does not have permission to read the specified file.
    UnicodeDecodeError: When the file cannot be decoded using UTF-8 encoding.

## Constraints:
    Preconditions:
        - The current module must be located in a valid filesystem path
        - All path components in *parts must form a valid relative path from the current module's directory
    Postconditions:
        - The returned string contains the complete file content
        - The file is properly closed after reading

## Side Effects:
    - Reads from the filesystem
    - May raise I/O related exceptions if file access fails

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
# Reading a version file
version = read("VERSION")

# Reading a README file
readme_content = read("..", "README.md")

# Reading a configuration file
config = read("conf", "settings.json")
```

## `docs.conf.find_version` · *function*

## Summary:
Extracts version string from a Python file containing a __version__ variable declaration.

## Description:
Retrieves the version identifier from a Python source file by parsing the __version__ assignment statement. This function is commonly used in Sphinx documentation configuration files to automatically fetch the package version without hardcoding it.

## Args:
    *file_paths (str): Variable-length argument list of path components that specify the location of the file containing version information. These paths are joined with the current module's directory to construct the full file path.

## Returns:
    str: The version string captured from the __version__ assignment in the target file.

## Raises:
    RuntimeError: When the version string cannot be found in the specified file, typically because the file doesn't contain a line matching the pattern "^__version__ = ['\"]([^'\"]*)['\"]".

## Constraints:
    Preconditions:
        - The file specified by file_paths must exist and be readable
        - The file must contain a line matching the pattern "^__version__ = ['\"]([^'\"]*)['\"]"
    Postconditions:
        - The function returns a non-empty string representing the version identifier
        - No modifications are made to the file or system state

## Side Effects:
    - Reads from the filesystem via the underlying read() function
    - May raise I/O related exceptions if file access fails (propagated from read())

## Control Flow:
```mermaid
flowchart TD
    A[Call find_version(*file_paths)] --> B[Read file content]
    B --> C[Search for version pattern]
    C --> D{Pattern found?}
    D -->|Yes| E[Return captured version]
    D -->|No| F[Raise RuntimeError]
```

## Examples:
```python
# Typical usage in Sphinx conf.py
version = find_version("package", "__init__.py")

# Alternative usage
version = find_version("..", "VERSION")
```

