# `versions.py`

## `src.ydata_profiling.utils.versions.pandas_version` · *function*

## Summary:
Returns the pandas library version as a list of integer components.

## Description:
Extracts the major, minor, and patch version numbers from the installed pandas package and returns them as a list of integers. This utility function provides a standardized way to access pandas version information for compatibility checking and feature detection.

## Args:
    None

## Returns:
    list[int]: A list containing exactly 3 integer components representing the major, minor, and patch version numbers respectively. For example, pandas version 1.3.5 would return [1, 3, 5].

## Raises:
    Exception: Raised if the pandas package is not installed or if the version string cannot be parsed properly. This includes cases where version string does not contain exactly 3 numeric components separated by dots.

## Constraints:
    Preconditions:
    - The pandas package must be installed in the Python environment
    - The version string returned by importlib.metadata.version must follow semantic versioning format with exactly 3 components (e.g., "1.2.3")
    
    Postconditions:
    - The returned list will contain exactly 3 integer elements representing major.minor.patch version components
    - All elements in the returned list will be non-negative integers

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_version()] --> B[Get pandas version string from importlib.metadata.version]
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
    # Use features available in pandas 1.3.0+
    pass

# Error handling example
try:
    version_list = pandas_version()
except Exception:
    print("Could not determine pandas version")
```

## `src.ydata_profiling.utils.versions.pandas_major_version` · *function*

## Summary:
Returns the major version number of the installed pandas library.

## Description:
Extracts and returns only the major version component from the installed pandas package version. This utility function simplifies version comparisons and compatibility checks by providing direct access to the major version integer.

## Args:
    None

## Returns:
    int: The major version number of the installed pandas library. For example, for pandas version 1.3.5, this function returns 1.

## Raises:
    Exception: Raised if the pandas package is not installed or if the version string cannot be parsed properly by the underlying pandas_version() function. This includes cases where version string does not contain exactly 3 numeric components separated by dots.

## Constraints:
    Preconditions:
    - The pandas package must be installed in the Python environment
    - The version string returned by importlib.metadata.version must follow semantic versioning format with exactly 3 components (e.g., "1.2.3")
    
    Postconditions:
    - The returned integer will be a non-negative value representing the major version component

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_major_version()] --> B[Call pandas_version()]
    B --> C[Extract first element from version list]
    C --> D[Return major version integer]
```

## Examples:
```python
# Basic usage
major_version = pandas_major_version()
print(major_version)  # Output: 1 for pandas 1.3.5

# Usage for conditional logic
if pandas_major_version() >= 1:
    # Use features available in pandas 1.x
    pass

# Error handling (though typically this wouldn't fail if pandas is properly installed)
try:
    major = pandas_major_version()
except Exception:
    print("Could not determine pandas major version")
```

## `src.ydata_profiling.utils.versions.is_pandas_1` · *function*

## Summary:
Checks whether the installed pandas library is version 1.x.

## Description:
Determines if the currently installed version of pandas follows the 1.x major version line. This utility function abstracts away the complexity of version checking by leveraging the pandas_major_version() helper function.

## Args:
    None

## Returns:
    bool: True if the pandas major version is exactly 1, False otherwise.

## Raises:
    Exception: May raise an exception if pandas is not installed or if version parsing fails within pandas_major_version().

## Constraints:
    Preconditions:
    - The pandas package must be installed in the Python environment
    - The pandas version must follow semantic versioning format with exactly 3 components
    
    Postconditions:
    - Returns a boolean value indicating major version equality to 1

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call is_pandas_1()] --> B[Call pandas_major_version()]
    B --> C[Compare result to 1]
    C --> D{Is equal to 1?}
    D -->|Yes| E[Return True]
    D -->|No| F[Return False]
```

## Examples:
```python
# Check if running with pandas 1.x
if is_pandas_1():
    print("Using pandas 1.x")
else:
    print("Using pandas 2.x or later")

# Conditional logic based on pandas version
if is_pandas_1():
    # Use pandas 1.x specific features or workarounds
    pass
else:
    # Use pandas 2.x+ features
    pass
```

