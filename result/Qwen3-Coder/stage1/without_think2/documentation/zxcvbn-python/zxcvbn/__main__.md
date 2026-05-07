# `__main__.py`

## `zxcvbn.__main__.JSONEncoder` · *class*

## Summary:
A custom JSON encoder that extends the standard library's JSONEncoder to handle objects that are not natively serializable by converting them to strings.

## Description:
This class overrides the default serialization behavior of the standard json.JSONEncoder to gracefully handle objects that would normally raise a TypeError during JSON serialization. It serves as a fallback mechanism that converts unserializable objects into their string representations rather than failing the entire serialization process.

## State:
- No instance attributes beyond those inherited from json.JSONEncoder
- Inherits all initialization parameters and behavior from the parent class

## Lifecycle:
- Creation: Instantiated automatically when used with json.dump() or json.dumps() functions when specified as the cls parameter
- Usage: Called internally by the JSON serialization process when encountering unserializable objects
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[JSONEncoder.default] --> B{Try super().default(o)}
    B --> C{TypeError raised?}
    C -->|Yes| D[return str(o)]
    C -->|No| E[return super().default(o)]
```

## Raises:
- TypeError: May be raised by the parent class's default method for objects it cannot serialize, but is caught and handled by returning str(o)

## Example:
```python
import json
from zxcvbn.__main__ import JSONEncoder

# Using the custom encoder
data = {"key": object()}  # object() is not JSON serializable
json_string = json.dumps(data, cls=JSONEncoder)
print(json_string)  # Output: '{"key": "<object object at 0x...>"}'
```

### `zxcvbn.__main__.JSONEncoder.default` · *method*

## Summary:
Converts non-serializable objects to string representations during JSON serialization.

## Description:
Overrides the default JSON serialization behavior to handle objects that cannot be natively serialized by json.JSONEncoder. When an object cannot be serialized by the parent class's default method, this implementation converts it to its string representation using str().

This method is part of a custom JSONEncoder subclass designed to provide graceful fallback handling for complex objects that would otherwise cause serialization errors.

## Args:
    self: The JSONEncoder instance
    o: The object to serialize (any Python object)

## Returns:
    A JSON-serializable representation of the object, either:
    - The result from the parent's default serialization method, or
    - A string representation of the object if the parent method raises TypeError

## Raises:
    TypeError: When the object cannot be serialized by the parent class and str() conversion also fails

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be convertible to string via str() if parent serialization fails
    Postconditions: The returned value is always JSON-serializable (either by parent method or str conversion)

## Side Effects:
    None

