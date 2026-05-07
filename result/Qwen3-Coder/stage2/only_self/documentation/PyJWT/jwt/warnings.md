# `warnings.py`

## `jwt.warnings.RemovedInPyjwt3Warning` · *class*

## Summary:
A deprecation warning class indicating features that will be removed in PyJWT version 3.

## Description:
This class serves as a specialized warning type for deprecated functionality in the PyJWT library that will be completely removed in version 3.0. It inherits from Python's built-in `DeprecationWarning` class and is used to alert developers when they are using features that should be migrated to newer alternatives before the breaking change occurs.

The warning is typically raised when code uses deprecated APIs, parameters, or behaviors that are scheduled for removal in the next major version of PyJWT. This allows developers to identify and update their code proactively before upgrading to PyJWT 3.0.

## State:
- Inherits all attributes from `DeprecationWarning`
- No additional instance attributes beyond those inherited from the parent class
- No special initialization parameters required beyond standard `DeprecationWarning` initialization

## Lifecycle:
- Creation: Instantiated like any other `DeprecationWarning` subclass, typically via `warnings.warn()` with this class as the warning category
- Usage: Used by the PyJWT library internally to signal deprecated functionality to users
- Destruction: No special cleanup required; follows normal Python warning handling patterns

## Method Map:
```mermaid
graph TD
    A[warn()] --> B[RemovedInPyjwt3Warning]
    B --> C[DeprecationWarning]
    C --> D[Warning]
    D --> E[Exception]
```

## Raises:
- None: This class doesn't raise any exceptions during instantiation or usage
- It inherits the standard `DeprecationWarning` behavior for how warnings are handled by Python's warnings system

## Example:
```python
import warnings
from jwt.warnings import RemovedInPyjwt3Warning

# Usage within PyJWT library code
warnings.warn(
    "The 'old_param' parameter is deprecated and will be removed in PyJWT 3.0",
    category=RemovedInPyjwt3Warning,
    stacklevel=2
)
```

