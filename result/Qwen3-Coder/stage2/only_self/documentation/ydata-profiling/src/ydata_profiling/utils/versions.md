# `versions.py`

## `src.ydata_profiling.utils.versions.pandas_version` · *function*

## Summary:
Returns the pandas library version as a list of integer components for easy comparison and processing.

## Description:
Extracts the pandas version from the installed package and converts it into a list of integers representing major, minor, and patch version numbers. This allows for programmatic version comparisons and validation.

## Args:
    None

## Returns:
    list[int]: A list containing the major, minor, and patch version numbers as integers. For example, pandas version "1.3.5" would return [1, 3, 5].

## Raises:
    Exception: May raise exceptions from importlib.metadata.version when the pandas package is not installed or cannot be accessed.

## Constraints:
    Preconditions: The pandas package must be installed in the Python environment.
    Postconditions: The returned list contains exactly three integer values representing the version components.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_version()] --> B[Get pandas version string]
    B --> C[Split version string by "."]
    C --> D[Convert each component to int]
    D --> E[Return list of integers]
```

## Examples:
```python
# Typical usage
version_list = pandas_version()
print(version_list)  # Output: [1, 3, 5] for pandas 1.3.5

# Usage for version comparison
current_version = pandas_version()
if current_version >= [1, 3, 0]:
    # Perform operations available in pandas 1.3.0+
    pass
```

## `src.ydata_profiling.utils.versions.pandas_major_version` · *function*

## Summary:
Returns the major version number of the installed pandas library.

## Description:
Extracts and returns only the major version component from the installed pandas library version. This function provides a convenient way to access just the major version number without dealing with the full version tuple.

## Args:
    None

## Returns:
    int: The major version number of the installed pandas library. For example, if pandas version is "1.3.5", this function returns 1.

## Raises:
    Exception: May raise exceptions from importlib.metadata.version when the pandas package is not installed or cannot be accessed, which can be propagated from the pandas_version() function.

## Constraints:
    Preconditions: The pandas package must be installed in the Python environment.
    Postconditions: The returned integer represents the major version component of the pandas library.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_major_version()] --> B[Call pandas_version()]
    B --> C[Get version list [major, minor, patch]]
    C --> D[Return first element (major version)]
```

## Examples:
```python
# Typical usage
major_version = pandas_major_version()
print(major_version)  # Output: 1 for pandas 1.3.5

# Usage for version checking
if pandas_major_version() >= 1:
    # Perform operations compatible with pandas 1.x
    pass
```

## `src.ydata_profiling.utils.versions.is_pandas_1` · *function*

## Summary:
Determines whether the installed pandas library is version 1.x.

## Description:
Checks if the major version of the installed pandas library is exactly 1. This utility function is commonly used to ensure compatibility with pandas 1.x features and APIs, particularly when maintaining backward compatibility with different pandas versions.

## Args:
    None

## Returns:
    bool: True if the installed pandas version is 1.x (major version equals 1), False otherwise.

## Raises:
    Exception: May raise exceptions from underlying version checking functions when pandas is not installed or cannot be accessed.

## Constraints:
    Preconditions: The pandas package must be installed in the Python environment.
    Postconditions: Returns a boolean indicating whether pandas major version is 1.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call is_pandas_1()] --> B[Call pandas_major_version()]
    B --> C{pandas_major_version() == 1?}
    C -->|True| D[Return True]
    C -->|False| E[Return False]
```

## Examples:
```python
# Check if running with pandas 1.x
if is_pandas_1():
    print("Using pandas 1.x")
else:
    print("Using different pandas version")

# Used in conditional logic for version-specific code paths
if is_pandas_1():
    # Execute pandas 1.x specific operations
    pass
else:
    # Execute alternative operations for other pandas versions
    pass
```

