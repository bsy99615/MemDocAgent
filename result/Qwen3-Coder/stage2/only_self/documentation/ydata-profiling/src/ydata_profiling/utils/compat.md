# `compat.py`

## `src.ydata_profiling.utils.compat.pandas_version_info` · *function*

## Summary:
Extracts and returns the major, minor, and patch version numbers of the installed pandas library as a tuple of integers.

## Description:
This utility function provides a standardized way to access pandas version information for compatibility checks and feature detection. It parses the pandas version string (e.g., "1.3.5") and converts it into a tuple of integers (e.g., (1, 3, 5)) that can be easily compared or used in conditional logic.

The function is designed to be cached for performance since version information typically doesn't change during runtime, making repeated calls efficient.

## Args:
    None

## Returns:
    Tuple[int, ...]: A tuple containing the major, minor, and patch version numbers as integers. For example, pandas version "2.0.3" would return (2, 0, 3). The tuple can contain varying number of elements depending on the version format.

## Raises:
    None

## Constraints:
    Preconditions:
    - The pandas library must be installed and importable
    - The pandas.__version__ attribute must be a string in the format "x.y.z" or similar
    
    Postconditions:
    - The returned tuple contains only integer values
    - The tuple length corresponds to the number of version components in the pandas version string

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call pandas_version_info()] --> B[Get pd.__version__]
    B --> C[Split version string by "."]
    C --> D[Convert each component to int]
    D --> E[Return tuple of integers]
```

## Examples:
```python
# Basic usage
version = pandas_version_info()
print(version)  # Output: (1, 3, 5) for pandas 1.3.5

# Version comparison
if pandas_version_info() >= (1, 3, 0):
    # Use features available in pandas 1.3.0+
    pass
```

