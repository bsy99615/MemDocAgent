# `warnings.py`

## `jwt.warnings.RemovedInPyjwt3Warning` · *class*

## Summary:
A custom deprecation warning class indicating features that will be removed in PyJWT version 3.

## Description:
This class serves as a specialized warning type that indicates deprecated functionality which will be completely removed in the upcoming PyJWT 3.0 release. It inherits from Python's built-in `DeprecationWarning` class, making it compatible with Python's warning system while providing a distinct category for tracking deprecated features specifically targeted for removal in the next major version.

The class is used internally by the PyJWT library to signal to developers that certain APIs or behaviors are deprecated and should be migrated to newer alternatives before the PyJWT 3.0 release.

## State:
- Inherits all attributes from `DeprecationWarning`
- No additional instance attributes
- No special initialization parameters beyond those inherited from `Warning`

## Lifecycle:
- Creation: Instantiated like any other warning class using `warnings.warn(message, RemovedInPyjwt3Warning)`
- Usage: Typically used in conjunction with Python's warnings module to alert users of deprecated functionality
- Destruction: No special cleanup required; follows standard Python warning object lifecycle

## Method Map:
```mermaid
graph TD
    A[warn()] --> B[RemovedInPyjwt3Warning]
    B --> C[DeprecationWarning]
    C --> D[Warning]
```

## Raises:
- No exceptions raised during instantiation as it's a simple class inheritance
- May raise `warnings.WarningMessage` when used with `warnings.warn()` if warning filters are configured to treat it as an error

## Example:
```python
import warnings
from jwt.warnings import RemovedInPyjwt3Warning

# Emitting the warning
warnings.warn(
    "The 'old_algorithm' parameter is deprecated and will be removed in PyJWT 3.0",
    RemovedInPyjwt3Warning
)
```

