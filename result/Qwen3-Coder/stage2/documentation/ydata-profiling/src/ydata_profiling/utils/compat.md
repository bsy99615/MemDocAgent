# `compat.py`

## `src.ydata_profiling.utils.compat.pandas_version_info` · *function*

## Summary:
Returns the pandas version as a tuple of integers for easy comparison and compatibility checking.

## Description:
Extracts the major, minor, and patch version numbers from the pandas library version string and returns them as a tuple of integers. This enables clean version comparisons in conditional logic throughout the codebase. The function requires that pandas be imported as `pd` in the calling scope (e.g., `import pandas as pd`).

## Args:
    None

## Returns:
    Tuple[int, ...]: A tuple containing integer version components (major, minor, patch, etc.). For example, pandas version "1.5.3" would return (1, 5, 3).

## Raises:
    ValueError: If any component of the version string cannot be converted to an integer.

## Constraints:
    Preconditions: 
    - The pandas library must be installed and importable
    - The pandas.__version__ attribute must be a string with numeric components separated by periods
    - The calling scope must have pandas imported as `pd` (this is a requirement for the function to work as written)
    
    Postconditions:
    - Returns a tuple of integers representing version components
    - All elements in the returned tuple are non-negative integers

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
import pandas as pd  # Required for this function to work
version = pandas_version_info()
print(version)  # Output: (1, 5, 3) for pandas 1.5.3

# Version comparison
import pandas as pd  # Required for this function to work
if pandas_version_info() >= (1, 5, 0):
    # Use features available in pandas 1.5.0+
    pass
```

