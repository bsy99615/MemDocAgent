# `versions.py`

## `src.ydata_profiling.utils.versions.pandas_version` · *function*

## Summary:
Returns the pandas version as a list of integers for easy comparison and processing.

## Description:
Extracts the pandas package version and converts it into a list of integer components. This utility function provides a standardized way to access pandas version information for compatibility checks and feature detection. The function is commonly used to determine if specific pandas features or APIs are available.

## Args:
    None

## Returns:
    list[int]: A list containing the major, minor, and patch version numbers as integers. For example, pandas version "1.3.5" would return [1, 3, 5]. The list will contain at least one integer, typically 3 integers for standard semantic versioning.

## Raises:
    Exception: May raise exceptions from importlib.metadata.version() if pandas is not installed or cannot be accessed. This typically includes ModuleNotFoundError when pandas is not installed.

## Constraints:
    Preconditions: The pandas package must be installed in the environment.
    Postconditions: The returned list contains exactly the version components as integers, with no string conversion remaining.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_version()] --> B[Get pandas version string from importlib.metadata.version("pandas")]
    B --> C[Split version string by "."]
    C --> D[Convert each component to int]
    D --> E[Return list of integers]
```

## Examples:
```python
# Typical usage for version checking
version = pandas_version()
if version >= [1, 3, 0]:
    # Use features available in pandas 1.3.0+
    pass

# Version comparison example
current_version = pandas_version()
required_version = [1, 2, 0]
if current_version >= required_version:
    print("Pandas version is compatible")
else:
    print("Pandas version is too old")
```

## `src.ydata_profiling.utils.versions.pandas_major_version` · *function*

## Summary:
Returns the major version number of the installed pandas package.

## Description:
Extracts and returns the major version component from the installed pandas package version. This function provides a convenient way to determine the major version of pandas without having to parse version strings manually.

## Args:
    None

## Returns:
    int: The major version number of the installed pandas package (e.g., for pandas version "1.3.5", returns 1).

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - The pandas package must be installed in the environment
        - The pandas package version string must follow semantic versioning format (e.g., "1.3.5")
    
    Postconditions:
        - Returns an integer representing the major version component
        - The returned value is always a positive integer for valid pandas installations

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_major_version()] --> B[Call pandas_version()]
    B --> C[Get pandas version string]
    C --> D[Split version by "."]
    D --> E[Convert to integers]
    E --> F[Return first element]
```

## Examples:
    >>> pandas_major_version()
    1

## `src.ydata_profiling.utils.versions.is_pandas_1` · *function*

## Summary:
Determines whether the installed pandas version is major version 1.

## Description:
This function checks if the currently installed pandas library is at major version 1.x.x. It serves as a version compatibility utility to enable conditional logic based on pandas version in the codebase.

## Args:
    None

## Returns:
    bool: True if the installed pandas version is major version 1, False otherwise.

## Raises:
    None

## Constraints:
    Preconditions:
    - The pandas library must be installed in the environment
    - The version string returned by importlib.metadata.version("pandas") must be in standard semantic versioning format (e.g., "1.3.5")

    Postconditions:
    - Returns a boolean value indicating major version 1 status
    - Does not modify any external state

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[is_pandas_1()] --> B[pandas_major_version()]
    B --> C[pandas_version()]
    C --> D[version("pandas")]
    D --> E[Split version string by "."]
    E --> F[Convert to integers]
    F --> G[Return first element]
    G --> H[Compare with 1]
    H --> I[Return boolean result]
```

## Examples:
```python
# Check if pandas version is 1.x.x
if is_pandas_1():
    print("Using pandas major version 1")
else:
    print("Using different pandas major version")
```

