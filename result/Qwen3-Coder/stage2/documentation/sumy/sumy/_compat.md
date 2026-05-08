# `_compat.py`

## `sumy._compat.unicode_compatible` · *function*

## Summary:
A class decorator that provides consistent Unicode string representation behavior across Python 2 and Python 3 environments.

## Description:
This decorator modifies a class to ensure consistent Unicode handling between Python 2 and Python 3 by adjusting string representation methods (__str__ and __bytes__). It is designed to bridge compatibility differences in how Python versions handle Unicode strings. The decorator expects the decorated class to have a __unicode__ method defined.

## Args:
    cls (type): The class to be made Unicode compatible. The class must define a __unicode__ method.

## Returns:
    type: The same class object with adjusted __str__ and __bytes__ methods for cross-version Unicode compatibility.

## Raises:
    None explicitly raised, but the decorator assumes the input class has a __unicode__ method.

## Constraints:
    Preconditions:
    - The input class must define a __unicode__ method
    - The module must define a PY3 variable to determine Python version (typically set from sys.version_info)
    
    Postconditions:
    - In Python 3: The class will have __str__ pointing to __unicode__ and __bytes__ method that encodes the string representation to UTF-8
    - In Python 2: The class will have __str__ method that encodes __unicode__ to UTF-8

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[unicode_compatible called with class] --> B{PY3 is True?}
    B -- Yes --> C[Set __str__ = __unicode__]
    B -- No --> D[Set __str__ = encode(__unicode__) to UTF-8]
    C --> E[Set __bytes__ = encode(__str__) to UTF-8]
    D --> E
    E --> F[Return modified class]
```

## Examples:
```python
@unicode_compatible
class MyStringClass:
    def __unicode__(self):
        return "Hello, World!"
    
    def __repr__(self):
        return self.__unicode__()

# Usage:
# In Python 3:
# str(instance) calls __unicode__
# bytes(instance) calls __str__() and encodes to UTF-8

# In Python 2:
# str(instance) calls __unicode__() and encodes to UTF-8
```

## `sumy._compat.to_string` · *function*

## Summary:
Routes object conversion to appropriate string representation function based on Python version for cross-version compatibility.

## Description:
A compatibility utility that provides version-appropriate string conversion by directing input to either Unicode conversion or bytes conversion functions based on the Python runtime environment. This function serves as a conditional dispatcher that ensures proper string representation regardless of whether the code is running on Python 2 or Python 3.

Known callers within the codebase:
- Text processing components that require normalized string representations
- Serialization routines that need consistent input formats
- Any internal code that needs to handle string conversion in a Python-version-agnostic manner

This logic is extracted into its own function rather than being inlined because it encapsulates the Python version detection and routing logic, providing a clean abstraction that allows downstream code to focus on business logic rather than compatibility concerns.

## Args:
    object (Any): Any Python object that needs to be converted to a string representation appropriate for the current Python version.

## Returns:
    str or bytes: Returns a Unicode string in Python 3 environments or bytes in Python 2 environments, as determined by the underlying conversion functions.

## Raises:
    Exceptions raised by the underlying conversion functions (`to_unicode` or `to_bytes`) depending on the Python version and input type.

## Constraints:
    Preconditions:
    - The global `PY3` constant must be properly defined to indicate the Python version
    - The `to_unicode` function must be available for Python 3 environments
    - The `to_bytes` function must be available for Python 2 environments
    - Input object must be a valid Python object that can be processed by the underlying conversion functions
    
    Postconditions:
    - Always returns a string-like object appropriate for the current Python version
    - Input object is not modified
    - Conversion follows Python 2/3 compatibility patterns

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start to_string] --> B{PY3?}
    B -->|True| C[to_unicode(object)]
    B -->|False| D[to_bytes(object)]
```

## Examples:
    # In Python 3 environment
    result = to_string("hello")  # Returns "hello" (Unicode string)
    result = to_string(b"hello") # Returns "hello" (decoded Unicode string)
    
    # In Python 2 environment  
    result = to_string(u"hello") # Returns "hello" (encoded bytes)
    result = to_string("hello")  # Returns "hello" (encoded bytes)

## `sumy._compat.to_bytes` · *function*

## Summary:
Converts an object to bytes representation with Python 2/3 compatibility handling.

## Description:
This function normalizes object-to-bytes conversion across Python versions, handling different types of input objects appropriately. It serves as a compatibility wrapper that ensures consistent byte conversion behavior between Python 2 and Python 3 environments.

## Args:
    object: Any Python object that needs to be converted to bytes representation

## Returns:
    bytes: The bytes representation of the input object. Returns the object unchanged if it's already bytes, encodes unicode strings to UTF-8, and delegates other types to instance_to_bytes for further processing.

## Raises:
    UnicodeEncodeError: When attempting to encode a unicode string fails
    TypeError: When the object cannot be converted to bytes through any available method (propagated from instance_to_bytes)

## Constraints:
    Preconditions:
        - The input object must be a valid Python object
        - The environment must support the standard isinstance checks
    Postconditions:
        - Always returns a bytes object
        - Input bytes objects are returned unchanged
        - Unicode strings are properly UTF-8 encoded

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start to_bytes] --> B{isinstance(object, bytes)?}
    B -- Yes --> C[return object]
    B -- No --> D{isinstance(object, unicode)?}
    D -- Yes --> E[object.encode("utf-8")]
    D -- No --> F[instance_to_bytes(object)]
```

## Examples:
    # Converting bytes (no change)
    result = to_bytes(b"hello")
    # Returns b"hello"
    
    # Converting unicode string (UTF-8 encoding)
    result = to_bytes(u"hello")
    # Returns b"hello"
    
    # Converting other objects (delegates to instance_to_bytes)
    result = to_bytes("hello")
    # Returns bytes representation via instance_to_bytes

## `sumy._compat.to_unicode` · *function*

## Summary:
Converts various object types to Unicode string representations with Python 2/3 compatibility.

## Description:
A compatibility utility that standardizes object-to-Unicode conversion across Python versions. This function serves as the primary entry point for converting different data types to Unicode strings, handling the most common cases directly while delegating complex conversions to `instance_to_unicode`.

The function is designed to work seamlessly across Python 2 and Python 3 environments by properly handling the differences in string types between these versions. It provides a clean abstraction layer for Unicode conversion that simplifies downstream code.

Known callers within the codebase:
- Various internal components that require Unicode string normalization
- Text processing pipelines that need consistent string representation
- Data serialization routines that expect Unicode inputs

This logic is extracted into its own function rather than being inlined because it encapsulates the complexity of Python version compatibility and provides a reusable interface for Unicode conversion throughout the codebase.

## Args:
    object (Any): Any Python object that needs to be converted to a Unicode string. This can be a unicode string, bytes object, or any other object type.

## Returns:
    str: Unicode string representation of the input object. Returns the object unchanged if it's already a unicode string, decodes bytes as UTF-8 if it's a bytes object, or delegates to `instance_to_unicode` for other types.

## Raises:
    UnicodeDecodeError: When attempting to decode bytes that are not valid UTF-8 encoded data.

## Constraints:
    Preconditions:
    - Input object must be a valid Python object
    - The global `instance_to_unicode` function must be available for delegation
    - The Python environment must support UTF-8 decoding for bytes objects
    
    Postconditions:
    - Always returns a Unicode string (str type in Python 3, unicode type in Python 2)
    - Input object is not modified
    - Conversion follows Python 2/3 compatibility patterns

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start to_unicode] --> B{isinstance(object, unicode)?}
    B -->|Yes| C[Return object]
    B -->|No| D{isinstance(object, bytes)?}
    D -->|Yes| E[object.decode("utf-8")]
    D -->|No| F[instance_to_unicode(object)]
```

## Examples:
    # Convert unicode string (no change)
    result = to_unicode(u"hello")
    
    # Convert bytes to unicode (UTF-8 decoding)
    result = to_unicode(b"hello")
    
    # Convert other objects via delegation
    result = to_unicode(42)
```

## `sumy._compat.instance_to_bytes` · *function*

## Summary:
Converts an instance to bytes representation with Python 2/3 compatibility handling.

## Description:
This function converts Python objects to their bytes representation, handling differences between Python 2 and Python 3 string/byte handling. It attempts to use appropriate conversion methods based on the Python version and available methods on the object. The function is designed to be part of a Python 2/3 compatibility layer where PY3 is expected to be defined at module level.

## Args:
    instance: Any Python object that can potentially be converted to bytes

## Returns:
    bytes: The bytes representation of the input instance

## Raises:
    UnicodeEncodeError: When encoding fails during string to bytes conversion
    TypeError: When the object cannot be converted to bytes through any available method

## Constraints:
    Preconditions:
        - The input instance must be a valid Python object
        - The environment must define the PY3 constant for version detection
    Postconditions:
        - Always returns a bytes object
        - Falls back to repr-based conversion when direct methods fail

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start instance_to_bytes] --> B{PY3?}
    B -- Yes --> C{Has __bytes__?}
    C -- Yes --> D[return bytes(instance)]
    C -- No --> E{Has __str__?}
    E -- Yes --> F[return unicode(instance).encode("utf-8")]
    E -- No --> G[return to_bytes(repr(instance))]
    B -- No --> H{Has __str__?}
    H -- Yes --> I[return bytes(instance)]
    H -- No --> J{Has __unicode__?}
    J -- Yes --> K[return unicode(instance).encode("utf-8")]
    J -- No --> G
```

## Examples:
    # Converting a string to bytes in Python 3
    result = instance_to_bytes("hello world")
    # Returns b"hello world" if __bytes__ exists, or utf-8 encoded string otherwise
    
    # Converting an integer to bytes  
    result = instance_to_bytes(42)
    # Returns b"42" via repr conversion when no direct conversion methods exist

## `sumy._compat.instance_to_unicode` · *function*

## Summary:
Provides Python 2/3 compatible conversion of objects to Unicode string representations.

## Description:
A compatibility utility function that converts Python objects to Unicode strings using version-appropriate methods. The function implements different conversion strategies based on the Python version (determined by the global `PY3` variable) and available magic methods on the input object.

## Args:
    instance (Any): Any Python object to be converted to Unicode string representation.

## Returns:
    str: Unicode string representation of the input instance.

## Raises:
    None explicitly raised in the documented code.

## Constraints:
    Preconditions:
    - The global variable `PY3` must be defined to indicate Python version (True for Python 3, False for Python 2)
    - The global function `to_unicode` must be defined for fallback conversion
    - The input instance should be a valid Python object
    
    Postconditions:
    - Always returns a Unicode string representation
    - Uses appropriate conversion strategy based on Python version and object methods

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start instance_to_unicode] --> B{PY3?}
    B -->|True| C{Has __str__?}
    C -->|Yes| D[return unicode(instance)]
    C -->|No| E{Has __bytes__?}
    E -->|Yes| F[return bytes(instance).decode("utf-8")]
    E -->|No| G[return to_unicode(repr(instance))]
    B -->|False| H{Has __unicode__?}
    H -->|Yes| I[return unicode(instance)]
    H -->|No| J{Has __str__?}
    J -->|Yes| K[return bytes(instance).decode("utf-8")]
    J -->|No| G
```

## Examples:
    # Basic usage with string object
    result = instance_to_unicode("hello")
    
    # Usage with integer (falls back to repr-based conversion)
    result = instance_to_unicode(42)
    
    # Usage with custom object implementing __str__
    class CustomObj:
        def __str__(self):
            return "custom_string"
    
    obj = CustomObj()
    result = instance_to_unicode(obj)
```

