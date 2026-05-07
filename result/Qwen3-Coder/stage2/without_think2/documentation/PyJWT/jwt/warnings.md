# `warnings.py`

## `jwt.warnings.RemovedInPyjwt3Warning` · *class*

## Summary:
A custom deprecation warning subclass indicating features that will be removed in PyJWT version 3.0.

## Description:
This class is a specialized warning category that extends Python's built-in `DeprecationWarning`. It is used by the PyJWT library to alert developers when they are using functionality that will be completely removed in version 3.0. This provides a clear migration path for users to update their code before the breaking changes occur.

## State:
- Inherits from `DeprecationWarning` - no additional instance attributes
- No constructor parameters required as it inherits all behavior from `DeprecationWarning`
- No class invariants as it's a simple marker class

## Lifecycle:
- Creation: Instantiated automatically by PyJWT library when deprecated features are detected
- Usage: Typically used with Python's `warnings.warn()` function to notify users of deprecated functionality
- Destruction: Follows standard Python warning object lifecycle with no special cleanup required

## Method Map:
```mermaid
graph TD
    A[PyJWT Library] --> B[warn()]
    B --> C[RemovedInPyjwt3Warning]
    C --> D[DeprecationWarning]
```

## Raises:
- None - this is a warning class, not a function that raises exceptions

## Example:
```python
import warnings
from jwt.warnings import RemovedInPyjwt3Warning

# Typical usage within PyJWT library
warnings.warn(
    "The 'verify' parameter will be removed in PyJWT 3.0",
    RemovedInPyjwt3Warning,
    stacklevel=2
)
```

