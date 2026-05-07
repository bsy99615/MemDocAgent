# `_compat.py`

## `sumy._compat.unicode_compatible` · *function*

## Summary:
A class decorator that ensures consistent string representation methods across Python 2 and Python 3 by properly mapping `__str__` and `__bytes__` methods.

## Description:
This decorator provides backward compatibility for Unicode string handling between Python 2 and Python 3 environments. It modifies a class to have appropriate `__str__` and `__bytes__` methods based on the Python version being used.

In Python 3, the decorator makes `__str__` point to the existing `__unicode__` method and adds a `__bytes__` method that encodes the string representation. In Python 2, it makes `__str__` encode the unicode representation to bytes.

The decorator should be applied to classes that define a `__unicode__` method to ensure consistent string representation behavior across Python versions.

## Args:
    cls (type): The class to be decorated and made Unicode compatible

## Returns:
    type: The same class with updated `__str__` and `__bytes__` methods for cross-version compatibility

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The input class must have a `__unicode__` method defined
    - The global variable `PY3` must be defined and evaluate to a boolean
    - The Python environment must support the `__bytes__` method (Python 2.6+ or Python 3+)
    
    Postconditions:
    - The returned class will have both `__str__` and `__bytes__` methods defined
    - The `__str__` method will return a string representation
    - The `__bytes__` method will return UTF-8 encoded bytes

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[unicode_compatible called with cls] --> B{PY3?}
    B -->|Yes| C[Set cls.__str__ = cls.__unicode__]
    B -->|No| D[Set cls.__str__ = lambda self: self.__unicode__().encode("utf-8")]
    C --> E[Set cls.__bytes__ = lambda self: self.__str__().encode("utf-8")]
    D --> E
    E --> F[Return cls]
```

## Examples:
```python
# Example usage in Python 2/3 compatible code:
@unicode_compatible
class MyStringClass(object):
    def __unicode__(self):
        return u"Hello World"
        
# Usage:
obj = MyStringClass()

# In Python 3:
# str(obj) returns "Hello World" 
# bytes(obj) returns b"Hello World"

# In Python 2:
# str(obj) returns "Hello World".encode("utf-8")
```

## `sumy._compat.to_string` · *function*

## Summary:
Provides cross-version string conversion by selecting the appropriate conversion method based on the Python version.

## Description:
This compatibility function serves as a version-aware string converter that automatically selects between `to_unicode` and `to_bytes` based on the Python version detected via the `PY3` flag. In Python 3, it uses `to_unicode` to ensure Unicode string output, while in Python 2, it uses `to_bytes` to ensure byte string output. This abstraction enables consistent text processing behavior across Python 2 and Python 3 environments.

The function is typically called when normalizing text data to the appropriate string type for the current Python version, particularly in text processing pipelines requiring cross-compatibility.

## Args:
    object: Any object that can be processed by the underlying conversion functions, including strings, bytes, and other object types.

## Returns:
    str: A string representation appropriate for the current Python version - Unicode strings in Python 3, byte strings in Python 2.

## Raises:
    Exceptions that may be raised by the underlying `to_unicode` or `to_bytes` functions depending on the input type and Python version.

## Constraints:
    Preconditions:
    - The `PY3` constant must be properly defined in the module scope (typically `sys.version_info[0] >= 3`)
    - The underlying `to_unicode` and `to_bytes` functions must be available in the module scope
    
    Postconditions:
    - Returns a string-like object appropriate for the current Python version
    - The returned object maintains semantic equivalence to the input for text processing purposes

## Side Effects:
    None - This function is pure and doesn't cause any I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Call to_string(object)] --> B{PY3?}
    B -->|True| C[to_unicode(object)]
    B -->|False| D[to_bytes(object)]
    C --> E[Return Unicode string]
    D --> E
```

## Examples:
```python
# Basic usage with string input
result = to_string("hello world")  # Returns Unicode string in Python 3, bytes in Python 2

# Usage with bytes input
result = to_string(b"hello world")  # Returns bytes unchanged in Python 2, decoded to Unicode in Python 3

# Usage with Unicode input in Python 3
result = to_string("héllo wörld")  # Returns Unicode string

# Usage with other object types
result = to_string(123)  # Delegates to helper functions for complex conversions
```

## `sumy._compat.to_bytes` · *function*

## Summary
Converts an object to bytes representation, handling Python 2/3 compatibility for string and byte conversions.

## Description
This function serves as a compatibility utility for converting various object types to bytes format, ensuring consistent behavior across Python 2 and Python 3 environments. It handles three main cases: direct bytes objects (returned unchanged), unicode strings (encoded to UTF-8 bytes), and other objects (converted via instance_to_bytes helper function).

The function is part of a broader compatibility layer that manages string/bytes conversion differences between Python versions. It's designed to be called internally by other functions in the same module and is typically used when working with text processing that needs to maintain compatibility across Python versions.

## Args
    object: Any object that needs to be converted to bytes format. Can be bytes, unicode string, or other object types.

## Returns
    bytes: The object converted to bytes format. For bytes objects, returns the object unchanged. For unicode strings, returns UTF-8 encoded bytes. For other objects, delegates to instance_to_bytes for conversion.

## Raises
    UnicodeEncodeError: When attempting to encode a unicode string that contains characters not representable in UTF-8 encoding.
    AttributeError: When instance_to_bytes encounters an object without appropriate conversion methods.
    TypeError: When the object cannot be converted to bytes through any available method.

## Constraints
    Preconditions:
    - Input object must be of a type that can be meaningfully converted to bytes
    - The module must have proper Python version detection (PY3 variable) available
    
    Postconditions:
    - Returned value is always of type bytes
    - Unicode strings are properly UTF-8 encoded
    - Bytes objects are returned unchanged

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Start to_bytes] --> B{isinstance(object, bytes)?}
    B -- Yes --> C[Return object]
    B -- No --> D{isinstance(object, unicode)?}
    D -- Yes --> E[object.encode("utf-8")]
    D -- No --> F[instance_to_bytes(object)]
    F --> G[Return result]
    E --> G
    C --> G
```

## Examples
    # Convert unicode string to bytes
    result = to_bytes("hello world")
    # Returns: b"hello world"
    
    # Pass bytes object unchanged
    result = to_bytes(b"hello world")
    # Returns: b"hello world"
    
    # Convert other objects via instance_to_bytes
    result = to_bytes(123)
    # Returns: bytes representation of repr(123)
```

## `sumy._compat.to_unicode` · *function*

## Summary:
Converts an object to a Unicode string representation, handling cross-version compatibility between Python 2 and 3.

## Description:
This function serves as a compatibility utility that normalizes various object types to Unicode strings. It handles the differences between Python 2 (where `unicode` and `str` are distinct types) and Python 3 (where they are unified). The function first checks if the object is already a Unicode string, then attempts to decode bytes objects, and finally delegates to a helper function for more complex object conversions.

## Args:
    object: Any Python object that needs to be converted to a Unicode string representation

## Returns:
    unicode: A Unicode string representation of the input object

## Raises:
    UnicodeDecodeError: When attempting to decode bytes that are not valid UTF-8

## Constraints:
    Preconditions:
    - Input object must be of a type that can be meaningfully converted to Unicode
    - The `instance_to_unicode` helper function must be available in scope
    
    Postconditions:
    - Returns a Unicode string object (unicode type in Python 2, str type in Python 3)
    - The returned string represents the original object in a standardized Unicode form

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start to_unicode] --> B{isinstance(object, unicode)?}
    B -- Yes --> C[Return object]
    B -- No --> D{isinstance(object, bytes)?}
    D -- Yes --> E[object.decode("utf-8")]
    D -- No --> F[instance_to_unicode(object)]
    F --> G[Return result]
    E --> G
```

## Examples:
    # Converting a Unicode string (Python 2)
    >>> to_unicode(u"hello")
    u'hello'
    
    # Converting bytes to Unicode
    >>> to_unicode(b"hello")
    u'hello'
    
    # Converting other objects
    >>> to_unicode(123)
    u'123'

## `sumy._compat.instance_to_bytes` · *function*

## Summary:
Converts an instance to bytes representation, handling different Python versions and object types appropriately.

## Description:
This function provides a cross-compatible way to convert objects to bytes format, adapting its approach based on the Python version (2 or 3) and the available methods on the input instance. It attempts to use native byte conversion methods first, falling back to string conversion and finally to representation-based conversion.

## Args:
    instance: Any Python object that needs to be converted to bytes format

## Returns:
    bytes: The byte representation of the input instance

## Raises:
    UnicodeEncodeError: When encoding fails during string-to-byte conversion
    TypeError: When the object cannot be converted to bytes through any available method

## Constraints:
    Preconditions:
    - The input instance must be a valid Python object
    - The environment must have proper encoding support (UTF-8)
    
    Postconditions:
    - Always returns a bytes object
    - The returned bytes represent the original instance in a serializable format

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start instance_to_bytes] --> B{PY3?}
    B -->|True| C{Has __bytes__?}
    C -->|Yes| D[return bytes(instance)]
    C -->|No| E{Has __str__?}
    E -->|Yes| F[return unicode(instance).encode("utf-8")]
    E -->|No| G[return to_bytes(repr(instance))]
    B -->|False| H{Has __str__?}
    H -->|Yes| I[return bytes(instance)]
    H -->|No| J{Has __unicode__?}
    J -->|Yes| K[return unicode(instance).encode("utf-8")]
    J -->|No| G
```

## Examples:
    # Converting a string in Python 3
    result = instance_to_bytes("hello")  # Returns b'hello'
    
    # Converting an integer in Python 3
    result = instance_to_bytes(42)  # Returns b'42'
    
    # Converting a custom object with __bytes__ method in Python 3
    class CustomBytes:
        def __bytes__(self):
            return b"custom"
    obj = CustomBytes()
    result = instance_to_bytes(obj)  # Returns b'custom'
```

## `sumy._compat.instance_to_unicode` · *function*

## Summary:
Converts a Python object instance to a Unicode string representation using Python version-appropriate methods.

## Description:
This function provides a cross-compatible approach to converting Python objects to Unicode strings, handling the differences between Python 2 and Python 3 object model behaviors. It attempts to use appropriate magic methods (__str__, __bytes__, __unicode__) based on the Python version, falling back to a representation-based approach when direct conversion methods aren't available.

## Args:
    instance (Any): Any Python object that needs to be converted to a Unicode string representation.

## Returns:
    str: A Unicode string representation of the input instance.

## Raises:
    None explicitly raised, though underlying conversion operations may raise exceptions such as UnicodeDecodeError or TypeError during conversion.

## Constraints:
    Preconditions:
    - The input instance should be a valid Python object
    - The environment should have appropriate encoding support for UTF-8
    
    Postconditions:
    - Returns a Unicode string representation of the input
    - The returned string is guaranteed to be Unicode-compatible

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start instance_to_unicode] --> B{PY3?}
    B -->|Yes| C{Has __str__?}
    C -->|Yes| D[return unicode(instance)]
    C -->|No| E{Has __bytes__?}
    E -->|Yes| F[return bytes(instance).decode("utf-8")]
    E -->|No| G[return to_unicode(repr(instance))]
    B -->|No| H{Has __unicode__?}
    H -->|Yes| I[return unicode(instance)]
    H -->|No| J{Has __str__?}
    J -->|Yes| K[return bytes(instance).decode("utf-8")]
    J -->|No| L[return to_unicode(repr(instance))]
```

## Examples:
    # Converting a regular string
    result = instance_to_unicode("hello")  # Returns Unicode string
    
    # Converting an integer
    result = instance_to_unicode(42)  # Returns Unicode representation of "42"
    
    # Converting a custom object with __str__ method
    class CustomObj:
        def __str__(self):
            return "custom_string"
    
    obj = CustomObj()
    result = instance_to_unicode(obj)  # Returns Unicode version of "custom_string"
```

