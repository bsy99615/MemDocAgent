# `compat.py`

## `src.ydata_profiling.utils.compat.pandas_version_info` · *function*

## Summary:
Returns the pandas version as a tuple of integers for easy version comparison.

## Description:
Extracts the major, minor, and patch version numbers from the pandas version string and returns them as a tuple of integers. This allows for straightforward version comparisons in conditional logic. The function accesses the pandas version through the global `pd` variable, which must be defined as an alias for the pandas module (likely via `import pandas as pd`).

## Args:
    None

## Returns:
    Tuple[int, ...]: A tuple containing the version components as integers (e.g., (1, 3, 0) for pandas 1.3.0).

## Raises:
    ValueError: If the pandas version string cannot be parsed into integer components.

## Constraints:
    Preconditions:
        - The pandas library must be installed and importable
        - The pandas.__version__ attribute must be a string with numeric components separated by dots
        - The global variable `pd` must be defined as an alias for the pandas module
    
    Postconditions:
        - Returns a tuple of integers representing the version components
        - All elements in the returned tuple are non-negative integers

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_version_info()] --> B[Get pd.__version__]
    B --> C[Split version string by "."]
    C --> D[Convert each part to int]
    D --> E[Return tuple of integers]
```

## Examples:
```python
# Typical usage for version comparison
version = pandas_version_info()
if version >= (1, 2, 0):
    # Use pandas features available in 1.2.0+
    pass
```

