# `_compat.py`

## `sumy._compat.unicode_compatible` · *function*

## Summary:
Decorator that ensures consistent string representation behavior across Python 2 and Python 3 by mapping unicode methods to appropriate string methods.

## Description:
This decorator handles cross-compatibility between Python 2 and Python 3 string handling. In Python 2, objects typically define `__unicode__()` and `__str__()` methods, where `__str__()` returns bytes encoded from unicode. In Python 3, the equivalent behavior is achieved using `__str__()` and `__bytes__()` methods. This decorator automatically maps the appropriate methods to ensure consistent behavior regardless of Python version.

The decorator is typically applied to classes that need to support both Python versions, particularly those implementing custom string representations. It relies on a global `PY3` variable to detect the Python version at runtime.

## Args:
    cls (type): The class to be decorated. This is the target class whose string representation methods will be modified.

## Returns:
    type: The same class object that was passed in, but with appropriate string representation methods mapped.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The input class must have a `__unicode__` method defined
    - The global variable `PY3` must be properly defined to indicate the Python version (typically set via `sys.version_info >= (3, 0)`)
    
    Postconditions:
    - The decorated class will have consistent string representation behavior across Python 2 and 3
    - In Python 3: `__str__` will be set to `__unicode__` and `__bytes__` will be implemented to encode `__str__()` as UTF-8
    - In Python 2: `__str__` will be implemented to encode `__unicode__()` as UTF-8

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[unicode_compatible called] --> B{PY3?}
    B -->|Yes| C[__str__ = __unicode__]
    B -->|No| D[__str__ = lambda self: __unicode__().encode("utf-8")]
    C --> E[cls.__bytes__ = lambda self: self.__str__().encode("utf-8")]
    D --> E
    E --> F[Return cls]
```

## Examples:
```python
@unicode_compatible
class MyStringClass:
    def __unicode__(self):
        return u"Hello World"
    
    def __repr__(self):
        return "MyStringClass()"

# In Python 3:
# str(instance) will call __unicode__() and return a string
# bytes(instance) will call __unicode__(), encode as UTF-8, and return bytes

# In Python 2:
# str(instance) will call __unicode__(), encode as UTF-8, and return bytes
```

## `sumy._compat.to_string` · *function*

## Summary:
Converts an object to a string representation appropriate for the current Python version, using either Unicode or bytes conversion functions.

## Description:
This function serves as a compatibility wrapper that selects the appropriate string conversion method based on the Python version. In Python 3, it uses the Unicode conversion function; in Python 2, it uses the bytes conversion function. This abstraction allows the codebase to maintain consistent string handling across different Python versions without conditional logic scattered throughout the application. The selection is determined by the global PY3 flag which indicates whether the current Python environment is version 3 or later.

## Args:
    object (Any): The input object to be converted to a string representation. Can be any Python object that is compatible with either to_unicode or to_bytes functions.

## Returns:
    str or bytes: Returns a Unicode string in Python 3 environments or bytes in Python 2 environments. The exact return type depends on the Python version being used.

## Raises:
    UnicodeDecodeError: When the underlying to_unicode function attempts to decode bytes containing invalid UTF-8 sequences (only in Python 3 environments).

## Constraints:
    - Preconditions: The input object must be compatible with either to_unicode or to_bytes functions
    - Postconditions: The returned value is appropriate for the current Python version (Unicode string in Python 3, bytes in Python 2)

## Side Effects:
    - Invokes either to_unicode or to_bytes functions internally
    - No direct I/O or external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[Start to_string] --> B{PY3?}
    B -->|Yes| C[to_unicode(object)]
    B -->|No| D[to_bytes(object)]
```

## Examples:
    # Basic usage in Python 3 environment
    result = to_string("hello")  # Returns 'hello' (Unicode string)
    
    # Basic usage in Python 2 environment  
    result = to_string("hello")  # Returns 'hello' (bytes)
    
    # Usage with bytes object in Python 3
    result = to_string(b"hello")  # Returns 'hello' (decoded Unicode)
```

## `sumy._compat.to_bytes` · *function*

## Summary:
Converts an object to its bytes representation, handling different Python versions and object types appropriately.

## Description:
This function provides a cross-compatible way to convert various Python objects to bytes format, accounting for differences between Python 2 and Python 3. It serves as a compatibility layer that ensures consistent byte conversion regardless of the Python runtime environment. The function handles three main cases: direct bytes objects (returned unchanged), unicode strings (encoded to UTF-8 bytes), and other objects (converted via the instance_to_bytes helper function).

## Args:
    object (Any): The object to be converted to bytes. Can be bytes, unicode string, or any other Python object.

## Returns:
    bytes: A bytes representation of the input object. For bytes objects, the same object is returned. For unicode strings, UTF-8 encoded bytes are returned. For other objects, the result is a bytes representation handled by the instance_to_bytes helper function.

## Raises:
    None explicitly raised, though underlying conversion operations in instance_to_bytes may raise exceptions.

## Constraints:
    Preconditions:
        - The input object must be a valid Python object
        - The environment must have proper encoding support (UTF-8)
        - The global `instance_to_bytes` function must be available and properly implemented
    
    Postconditions:
        - The returned value is always of type bytes
        - The conversion respects Python version compatibility

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start to_bytes] --> B{isinstance(object, bytes)?}
    B -- Yes --> C[Return object]
    B -- No --> D{isinstance(object, unicode)?}
    D -- Yes --> E[object.encode("utf-8")]
    D -- No --> F[instance_to_bytes(object)]
```

## Examples:
    # Converting bytes (no change)
    result = to_bytes(b"hello")  # Returns b"hello"
    
    # Converting unicode string (UTF-8 encoding)
    result = to_bytes(u"hello")  # Returns b"hello"
    
    # Converting other objects (delegates to instance_to_bytes)
    result = to_bytes("hello")  # Returns bytes representation from instance_to_bytes
```

## `sumy._compat.to_unicode` · *function*

## Summary:
Converts an object to a Unicode string representation, handling different Python versions and data types appropriately.

## Description:
This function provides cross-compatible Unicode string conversion for both Python 2 and Python 3 environments. It serves as a compatibility layer to ensure consistent Unicode handling across different Python versions by processing three distinct cases: already Unicode objects, bytes objects requiring UTF-8 decoding, and other objects that are converted through the instance_to_unicode helper function.

## Args:
    object (Any): The input object to be converted to Unicode string. Can be a Unicode string, bytes object, or any other object type.

## Returns:
    str: Unicode string representation of the input object. Returns the object unchanged if it's already a Unicode string, decodes bytes using UTF-8 if it's a bytes object, or converts other types through the instance_to_unicode helper function.

## Raises:
    UnicodeDecodeError: When attempting to decode bytes objects that contain invalid UTF-8 sequences.

## Constraints:
    - Preconditions: The input object must be a valid Python object that can be processed by isinstance checks
    - Postconditions: The returned value is always a Unicode string (str type in Python 3)

## Side Effects:
    - May invoke decode() method on bytes objects
    - Calls instance_to_unicode function for non-Unicode, non-bytes objects
    - No external I/O or state mutations

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
    result = to_unicode(u"hello")  # Returns u"hello"
    
    # Converting bytes to Unicode
    result = to_unicode(b"hello")  # Returns u"hello" (UTF-8 decoded)
    
    # Converting other objects via instance_to_unicode
    result = to_unicode(42)  # Delegates to instance_to_unicode for conversion

## `sumy._compat.instance_to_bytes` · *function*

## Summary:
Converts an instance to a bytes representation, handling different Python versions and object types appropriately.

## Description:
This function provides a cross-compatible way to convert various Python objects to bytes format, accounting for differences between Python 2 and Python 3. It attempts to use object-specific methods like `__bytes__`, `__str__`, or `__unicode__` before falling back to a generic representation via `repr()`. The function leverages a global `PY3` flag to determine the appropriate conversion strategy.

## Args:
    instance (Any): The object to be converted to bytes. Can be any Python object.

## Returns:
    bytes: A bytes representation of the input instance. The exact format depends on the object type and Python version.

## Raises:
    None explicitly raised, though underlying conversion operations may raise exceptions.

## Constraints:
    Preconditions:
        - The input instance must be a valid Python object
        - The environment must have proper encoding support (UTF-8)
        - A global `PY3` variable must be defined to indicate Python version
    
    Postconditions:
        - The returned value is always of type bytes
        - The conversion respects Python version compatibility

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start instance_to_bytes] --> B{PY3?}
    B -- Yes --> C{hasattr(__bytes__)?}
    C -- Yes --> D[return bytes(instance)]
    C -- No --> E{hasattr(__str__)?}
    E -- Yes --> F[return unicode(instance).encode("utf-8")]
    E -- No --> G[return to_bytes(repr(instance))]
    B -- No --> H{hasattr(__str__)?}
    H -- Yes --> I[return bytes(instance)]
    H -- No --> J{hasattr(__unicode__)?}
    J -- Yes --> K[return unicode(instance).encode("utf-8")]
    J -- No --> G
```

## Examples:
    # Converting a string in Python 3
    result = instance_to_bytes("hello")  # Returns b'hello'
    
    # Converting an integer in Python 3
    result = instance_to_bytes(42)  # Returns b'42'
```

## `sumy._compat.instance_to_unicode` · *function*

## Summary:
Converts an instance to a Unicode string representation, handling different Python versions and object types appropriately.

## Description:
This function provides a cross-compatible way to convert objects to Unicode strings by checking for appropriate magic methods and falling back to representation-based conversion. It handles both Python 2 and Python 3 compatibility concerns, ensuring proper string encoding regardless of the runtime environment. The function is designed to avoid infinite recursion by having `to_unicode` call `instance_to_unicode` as a fallback.

## Args:
    instance (Any): The object to be converted to Unicode string representation

## Returns:
    str: Unicode string representation of the input instance

## Raises:
    None explicitly raised, though underlying operations may raise exceptions during conversion

## Constraints:
    - Preconditions: The input instance must be a valid Python object
    - Postconditions: The returned value is always a Unicode string

## Side Effects:
    - May invoke magic methods (__str__, __unicode__, __bytes__) on the input instance
    - Calls to_unicode function which may recursively call instance_to_unicode

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
    # Converting a regular string in Python 3
    result = instance_to_unicode("hello")  # Returns Unicode string
    
    # Converting a bytes object in Python 3
    result = instance_to_unicode(b"hello")  # Returns decoded Unicode string
    
    # Converting an object without special methods
    class TestObj:
        def __repr__(self):
            return "<TestObj>"
    
    obj = TestObj()
    result = instance_to_unicode(obj)  # Returns repr-based Unicode string
```

