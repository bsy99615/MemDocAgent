# `versions.py`

## `src.ydata_profiling.utils.versions.pandas_version` · *function*

## Summary:
Returns the pandas library version as a list of integers representing the major, minor, and patch components.

## Description:
Extracts the pandas version string from the package metadata and converts it into a list of integer components. This function serves as a standardized way to obtain version information for pandas, enabling version-dependent logic throughout the profiling library. It specifically uses importlib.metadata.version to retrieve the version information, which follows semantic versioning format (MAJOR.MINOR.PATCH).

## Args:
    None

## Returns:
    list[int]: A list containing three integers representing the major, minor, and patch version numbers of pandas. For example, pandas 1.3.5 would return [1, 3, 5]. The function assumes a standard semantic versioning format (MAJOR.MINOR.PATCH) and will always return exactly three components.

## Raises:
    Exception: May raise exceptions from importlib.metadata.version when the pandas package is not installed or cannot be accessed. This includes ImportError if pandas is not installed, or other exceptions if version parsing fails.

## Constraints:
    Preconditions: The pandas package must be installed in the Python environment.
    Postconditions: The returned list always contains exactly three integer values representing semantic versioning components.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_version()] --> B[Get pandas version string via importlib.metadata.version]
    B --> C[Split version string by "."]
    C --> D[Convert each component to int]
    D --> E[Return list of integers]
```

## Examples:
    >>> pandas_version()
    [1, 3, 5]
    >>> pandas_version()
    [2, 0, 1]
```

## `src.ydata_profiling.utils.versions.pandas_major_version` · *function*

## Summary:
Returns the major version number of the pandas library currently installed in the environment.

## Description:
Extracts the major version component from the full pandas version tuple. This function provides a convenient way to access only the major version number, which is often sufficient for version-dependent conditional logic in the profiling library. The function relies on the `pandas_version()` helper function to retrieve the complete version information.

## Args:
    None

## Returns:
    int: The major version number of pandas as an integer. For example, if pandas version is 1.3.5, this function returns 1.

## Raises:
    Exception: May raise exceptions from the underlying `pandas_version()` function, such as ImportError if pandas is not installed, or other exceptions if version parsing fails.

## Constraints:
    Preconditions: The pandas package must be installed in the Python environment.
    Postconditions: The returned value is always a single integer representing the major version component.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_major_version()] --> B[Call pandas_version()]
    B --> C[Access first element of version list]
    C --> D[Return major version integer]
```

## Examples:
    >>> pandas_major_version()
    1
    >>> pandas_major_version()
    2
```

## `src.ydata_profiling.utils.versions.is_pandas_1` · *function*

## Summary:
Determines whether the installed pandas library is version 1.x.

## Description:
Checks if the major version of the pandas library is equal to 1. This utility function is used to enable version-specific behavior in the profiling library, particularly for compatibility with pandas 1.x features and APIs. The function delegates to `pandas_major_version()` to retrieve the current pandas version and compares it against the value 1.

## Args:
    None

## Returns:
    bool: True if the installed pandas version is 1.x, False otherwise.

## Raises:
    Exception: May raise exceptions from the underlying `pandas_major_version()` function, such as ImportError if pandas is not installed, or other exceptions if version parsing fails.

## Constraints:
    Preconditions: The pandas package must be installed in the Python environment.
    Postconditions: The returned value is always a boolean indicating pandas version 1.x compatibility.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call is_pandas_1()] --> B[Call pandas_major_version()]
    B --> C[Compare result with 1]
    C --> D{Equal to 1?}
    D -->|Yes| E[Return True]
    D -->|No| F[Return False]
```

## Examples:
    >>> is_pandas_1()
    True
    >>> is_pandas_1()
    False
```

