# `compat.py`

## `src.ydata_profiling.utils.compat.pandas_version_info` · *function*

## Summary:
Returns the pandas version as a tuple of integers for easy comparison and compatibility checking.

## Description:
This function extracts the major, minor, and patch version numbers from pandas' version string and returns them as a tuple of integers. It enables version-based conditional logic in the codebase without requiring string comparisons or manual parsing.

The function is typically called during module initialization or when making version-specific decisions in compatibility layers. It's used internally by the profiling library to ensure proper behavior across different pandas versions.

This logic is extracted into its own function to centralize version parsing and avoid duplication throughout the codebase, enforcing a clear boundary between version detection and version-dependent logic.

## Args:
    None

## Returns:
    Tuple[int, ...]: A tuple containing the version components as integers. For example, pandas version "1.4.3" would return (1, 4, 3), and "2.0.0" would return (2, 0, 0). The tuple length depends on the version string format (typically 3 components for standard semantic versioning).

## Raises:
    ValueError: If any component of the version string cannot be converted to an integer (rare edge case with malformed version strings).

## Constraints:
    Preconditions:
        - The pandas library must be installed and importable
        - The pandas.__version__ attribute must be a string in the format "x.y.z" where x, y, z are integers
    
    Postconditions:
        - Always returns a tuple of integers
        - The returned tuple length corresponds to the number of version components in the pandas version string

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B[Get pd.__version__ string]
    B --> C[Split by "." character]
    C --> D[Convert each component to integer]
    D --> E[Return tuple of integers]
```

## Examples:
```python
# Typical usage for version comparison
version = pandas_version_info()
if version >= (1, 5, 0):
    # Use newer pandas features
    pass
else:
    # Fall back to older implementations
    pass

# Returns (1, 4, 3) for pandas version 1.4.3
result = pandas_version_info()
print(result)  # Output: (1, 4, 3)

# Returns (2, 0, 0) for pandas version 2.0.0  
result = pandas_version_info()
print(result)  # Output: (2, 0, 0)
```

