# `_compat.py`

## `sumy._compat.unicode_compatible` · *function*

## Summary:
Decorator that ensures a class has proper Unicode string representation methods across Python 2 and Python 3 compatibility.

## Description:
This decorator modifies a class to provide consistent string representation behavior between Python 2 and Python 3. It handles the differences in how these Python versions manage Unicode strings by setting appropriate `__str__` and `__bytes__` methods based on the Python version.

The function is designed to be used as a class decorator to ensure that classes have proper Unicode handling regardless of whether they run on Python 2 or Python 3. This is particularly useful for libraries that need to support both Python versions.

## Args:
    cls (type): The class to be made Unicode compatible. This parameter represents the class being decorated.

## Returns:
    type: The same class with updated `__str__` and `__bytes__` methods for Unicode compatibility.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The input class must have a `__unicode__` method defined
    - The environment must have a `PY3` variable defined to determine Python version
    
    Postconditions:
    - The returned class will have `__str__` and `__bytes__` methods properly configured
    - The class maintains all original functionality while gaining cross-version Unicode compatibility

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[unicode_compatible called with class] --> B{PY3 is True?}
    B -->|Yes| C[Set __str__ = __unicode__]
    B -->|No| D[Set __str__ = lambda self: __unicode__().encode("utf-8")]
    C --> E[Set __bytes__ = lambda self: __str__().encode("utf-8")]
    D --> E
    E --> F[Return modified class]
```

## Examples:
```python
@unicode_compatible
class MyStringClass:
    def __unicode__(self):
        return u"Hello, World!"
        
# In Python 3:
# str(instance) calls __unicode__() and returns a string
# bytes(instance) calls __str__() and encodes to UTF-8 bytes

# In Python 2:
# str(instance) calls __unicode__().encode("utf-8") and returns bytes
```

## `sumy._compat.to_string` · *function*

## Summary:
Converts objects to string representation (Unicode in Python 3, bytes in Python 2) with cross-version compatibility.

## Description:
This compatibility function provides a unified interface for converting objects to their appropriate string representation based on the Python version. In Python 3, it converts objects to Unicode strings using `to_unicode()`, while in Python 2, it converts them to bytes using `to_bytes()`. This abstraction allows the codebase to write version-agnostic string conversion logic.

The function serves as a bridge between Python 2 and Python 3 string handling, ensuring consistent behavior regardless of the execution environment. It's particularly useful in libraries that need to support both Python versions simultaneously, allowing developers to write clean code without version-specific branching.

## Args:
    object (Any): Any Python object that can be converted to string representation

## Returns:
    str or bytes: Unicode string in Python 3, bytes in Python 2

## Raises:
    UnicodeDecodeError: When bytes objects cannot be decoded using UTF-8 encoding (in Python 3)
    Exception: Any exception that might occur during conversion in underlying functions

## Constraints:
    Preconditions:
    - Input must be a valid Python object
    - The environment must have proper Python version compatibility setup (PY3 constant must be defined)
    
    Postconditions:
    - Always returns a string-like representation (Unicode in Python 3, bytes in Python 2)
    - Maintains backward compatibility with Python 2 string handling

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
    # Basic usage - converting strings
    result = to_string("hello")  # Returns 'hello' (Unicode string) in Python 3, b'hello' in Python 2
    
    # Working with bytes - converts to appropriate string type
    result = to_string(b"hello")  # Returns 'hello' in Python 3, b'hello' in Python 2
    
    # Converting numbers - maintains consistent behavior
    result = to_string(42)  # Returns '42' in both Python 3 and Python 2
    
    # Usage in a library function that needs cross-version compatibility
    def process_text(text):
        # Normalize text regardless of Python version
        normalized_text = to_string(text)
        # Continue processing...
        return normalized_text

## `sumy._compat.to_bytes` · *function*

## Summary:
Converts Python objects to bytes format with Python 2/3 compatibility handling.

## Description:
This function provides a unified interface for converting various Python objects to bytes representation. It handles the common case of converting strings to bytes while maintaining compatibility across Python versions. The function delegates complex conversions to the `instance_to_bytes` helper function.

## Args:
    object: Any Python object that can be converted to bytes format

## Returns:
    bytes: A bytes object representing the input object

## Raises:
    None explicitly raised in this function's code

## Constraints:
    Preconditions:
    - The input object should be a valid Python object
    - The environment should support UTF-8 encoding
    
    Postconditions:
    - Always returns a bytes object
    - Handles Python 2 and Python 3 compatibility concerns

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start to_bytes] --> B{isinstance(object, bytes)?}
    B -->|Yes| C[return object]
    B -->|No| D{isinstance(object, unicode)?}
    D -->|Yes| E[object.encode("utf-8")]
    D -->|No| F[instance_to_bytes(object)]
```

## Examples:
    # Converting bytes (no change)
    result = to_bytes(b"hello")  # Returns b"hello"
    
    # Converting unicode string (UTF-8 encoding)
    result = to_bytes(u"hello")  # Returns b"hello" in Python 2/3
    
    # Converting other objects (delegates to instance_to_bytes)
    result = to_bytes(42)  # Returns bytes representation via instance_to_bytes

## `sumy._compat.to_unicode` · *function*

## Summary:
Converts various object types to Unicode string representations with cross-version compatibility for Python 2 and Python 3.

## Description:
This compatibility function handles the conversion of different object types to Unicode strings, addressing differences between Python 2 and Python 3 string handling. It specifically manages three cases: existing Unicode objects (returns unchanged), bytes objects (decodes using UTF-8), and all other objects (delegates to instance_to_unicode for further processing). The function is part of a broader compatibility layer that ensures consistent string representation behavior across Python versions.

## Args:
    object (Any): Any Python object to be converted to Unicode string representation

## Returns:
    str: Unicode string representation of the input object. Returns the object unchanged if it's already a Unicode string, decodes bytes to Unicode using UTF-8, or delegates to instance_to_unicode for other types.

## Raises:
    UnicodeDecodeError: When bytes objects cannot be decoded using UTF-8 encoding
    Exception: Any exception that might occur during the conversion process in instance_to_unicode

## Constraints:
    Preconditions:
    - Input must be a valid Python object
    - The function assumes Python 2/3 compatibility environment with proper imports
    
    Postconditions:
    - Always returns a Unicode string representation for valid inputs
    - Maintains backward compatibility with Python 2 string handling

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
    # Converting a Unicode string (no change)
    result = to_unicode(u"hello")
    
    # Converting bytes to Unicode
    result = to_unicode(b"hello")
    
    # Converting other objects via delegation
    result = to_unicode(42)
```

## `sumy._compat.instance_to_bytes` · *function*

## Summary:
Converts a Python object to bytes format with Python 2/3 compatibility handling.

## Description:
This function converts Python objects to bytes representation, implementing different conversion strategies based on Python version and object capabilities. It prioritizes objects with native __bytes__ methods, falls back to string conversion for __str__ methods, and ultimately uses repr() conversion when no suitable methods exist.

## Args:
    instance: Any Python object to be converted to bytes format

## Returns:
    bytes: The byte representation of the input instance

## Raises:
    None explicitly raised in this function's code

## Constraints:
    Preconditions:
    - The input instance should be a valid Python object
    - The environment should support UTF-8 encoding
    
    Postconditions:
    - Always returns a bytes object
    - Handles Python 2 and Python 3 compatibility concerns

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
    result = instance_to_bytes("hello")  # Returns b"hello"
    
    # Converting an integer in Python 3  
    result = instance_to_bytes(42)  # Returns b"42" (via repr)
    
    # Converting a custom object with __bytes__ method
    class CustomBytes:
        def __bytes__(self):
            return b"custom_bytes"
    obj = CustomBytes()
    result = instance_to_bytes(obj)  # Returns b"custom_bytes"
```

## `sumy._compat.instance_to_unicode` · *function*

## Summary:
Converts a Python object to Unicode string representation with cross-version compatibility for Python 2 and Python 3.

## Description:
This compatibility function handles the differences in string representation between Python 2 and Python 3 by attempting to use appropriate magic methods (__str__, __bytes__, __unicode__) before falling back to a generic representation. It serves as a bridge for maintaining consistent string conversion behavior across Python versions.

## Args:
    instance (Any): Any Python object to be converted to Unicode string representation

## Returns:
    str: Unicode string representation of the input instance

## Raises:
    UnicodeDecodeError: When byte decoding fails during conversion process
    Exception: Any exception that might occur during the conversion process

## Constraints:
    Preconditions:
    - Input must be a valid Python object
    - PY3 must be defined as a boolean indicating Python version (external dependency)
    - to_unicode function must be available in scope (external dependency)
    
    Postconditions:
    - Always returns a Unicode string representation
    - Provides graceful fallback through repr() conversion when primary methods unavailable

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
    # Converting a regular string
    result = instance_to_unicode("hello world")
    
    # Converting an object with __str__ method
    class MyString:
        def __str__(self):
            return "custom string"
    obj = MyString()
    result = instance_to_unicode(obj)
```

