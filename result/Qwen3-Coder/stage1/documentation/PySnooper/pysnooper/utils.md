# `utils.py`

## `pysnooper.utils._check_methods` · *function*

## Summary:
Checks whether a class implements all specified methods, returning True if all methods are present and not abstract.

## Description:
Validates that a given class implements all required methods by traversing its Method Resolution Order (MRO) to ensure each method exists and is not marked as abstract (None). This utility function is commonly used in abstract base class implementations to verify that subclasses properly implement required interface methods.

## Args:
    C (type): The class to check for method implementations
    *methods (str): Variable-length argument list of method names to verify exist in the class

## Returns:
    bool or NotImplemented: Returns True if all methods are implemented and not abstract, NotImplemented if any method is missing or abstract (marked as None)

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - C must be a valid class/type object
    - All method names in *methods must be strings
    - The class must have a valid __mro__ attribute
    
    Postconditions:
    - Returns True only when all specified methods exist in the class hierarchy and are not abstract
    - Returns NotImplemented when any method is either missing or explicitly set to None (abstract)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _check_methods] --> B{Class C has MRO?}
    B -->|Yes| C[Get MRO of C]
    C --> D[For each method in methods]
    D --> E{Method in B.__dict__ for B in MRO?}
    E -->|No| F[Return NotImplemented]
    E -->|Yes| G{B.__dict__[method] is None?}
    G -->|Yes| H[Return NotImplemented]
    G -->|No| I[Continue to next method]
    F --> J[End]
    H --> J
    I --> K{All methods checked?}
    K -->|No| D
    K -->|Yes| L[Return True]
    L --> J
```

## Examples:
    # Check if a class implements required methods
    class MyInterface(metaclass=ABCMeta):
        @abstractmethod
        def process(self):
            pass
    
    class ConcreteClass(MyInterface):
        def process(self):
            return "processed"
    
    # This would return True
    result = _check_methods(ConcreteClass, 'process')
    
    # If a method is missing or abstract, it returns NotImplemented
    class IncompleteClass(MyInterface):
        pass
    
    # This would return NotImplemented
    result = _check_methods(IncompleteClass, 'process')

## `pysnooper.utils.WritableStream` · *class*

*No documentation generated.*

### `pysnooper.utils.WritableStream.write` · *method*

## Summary:
Abstract method defining the interface for writing string content to a stream.

## Description:
This abstract method establishes the contract for writing string content to a writable stream. As part of the WritableStream abstract base class, it defines the expected interface that all concrete implementations must provide. This method is typically invoked during debugging operations to output trace information, variable states, or execution flow details to various destinations such as files, stdout, or buffers.

## Args:
    s (str): The string content to be written to the output stream. This represents debug information that needs to be recorded or displayed.

## Returns:
    None: This method does not return any value.

## Raises:
    NotImplementedError: When called directly on the abstract base class, as this method must be overridden by concrete implementations.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The string `s` must be a valid string object
    - This method should only be called on concrete instances of WritableStream subclasses
    - The underlying output mechanism must be properly initialized
    
    Postconditions:
    - The string content is written to the appropriate output destination as defined by the concrete implementation
    - No return value is produced

## Side Effects:
    I/O operations: Writes the provided string content to an output destination (file, stdout, buffer, etc.) as defined by concrete implementations

### `pysnooper.utils.WritableStream.__subclasshook__` · *method*

## Summary:
Determines if a class implements the write method, making it compatible with the WritableStream abstract base class.

## Description:
This special method is part of Python's Abstract Base Class mechanism and is invoked when checking if a class is a subclass of WritableStream. When a class is checked against WritableStream, this method verifies whether the candidate class implements the required 'write' method. If the class implements 'write', it's considered a subclass of WritableStream without requiring explicit inheritance.

## Args:
    cls (type): The WritableStream class itself (used for comparison)
    C (type): The candidate class being checked for subclass relationship

## Returns:
    bool or NotImplemented: Returns True if class C implements the 'write' method and it's not abstract, NotImplemented otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None - this method doesn't read any instance attributes
    Attributes WRITTEN: None - this method doesn't modify any instance attributes

## Constraints:
    Preconditions:
    - cls must be the WritableStream class itself
    - C must be a valid class/type object
    - The class C must have a valid Method Resolution Order (__mro__)

    Postconditions:
    - Returns True only when class C implements 'write' method and it's not abstract
    - Returns NotImplemented when class C doesn't implement 'write' or when 'write' is abstract

## Side Effects:
    None - this method performs only class introspection and returns a boolean value

## `pysnooper.utils.shitcode` · *function*

## Summary:
Filters a string to retain only ASCII-compatible characters, replacing non-ASCII characters with question marks.

## Description:
This function processes a string and removes or replaces characters that have ordinal values outside the range 0 < ord(c) < 256. It's designed to sanitize strings for environments that require strict ASCII compatibility or byte-level string processing.

## Args:
    s (str): Input string to be filtered for ASCII compatibility

## Returns:
    str: A new string where characters with ordinal values outside the range (0, 256) are replaced with '?' characters

## Raises:
    None

## Constraints:
    Preconditions:
        - Input must be a string type
    Postconditions:
        - Output string contains only characters with ordinal values in range [1, 255]
        - All characters with ordinal values outside this range are replaced with '?'

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input string s] --> B{Character ordinal in range (0,256)?}
    B -- Yes --> C[Keep character c]
    B -- No --> D[Replace with '?']
    C --> E[Join all characters]
    D --> E
    E --> F[Return sanitized string]
```

## Examples:
    >>> shitcode("Hello, World!")
    'Hello, World!'
    >>> shitcode("café")
    'caf?'
    >>> shitcode("smile 😀")
    'smile ?'
```

## `pysnooper.utils.get_repr_function` · *function*

## Summary:
Selects an appropriate representation function for an item based on custom type conditions.

## Description:
This function acts as a dispatcher that chooses the correct representation function for an object by evaluating custom conditions. It's designed to allow flexible representation selection, particularly useful in debugging contexts where different objects may require different formatting approaches.

## Args:
    item (Any): The object for which to select a representation function
    custom_repr (list[tuple]): A list of (condition, action) pairs where:
        - condition: Either a callable that takes an item and returns True/False, or a type
        - action: A callable that produces a string representation of the item

## Returns:
    callable: A representation function that can be applied to the item. Returns the provided action function if a condition matches, otherwise returns the built-in `repr` function.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - `custom_repr` must be iterable containing (condition, action) tuples
        - Each condition should be either a callable or a type
        - Each action should be callable
    
    Postconditions:
        - Always returns a callable function
        - If no conditions match, returns `repr` function

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_repr_function] --> B{custom_repr iterable?}
    B -- Yes --> C[Iterate through custom_repr]
    C --> D{condition is type?}
    D -- Yes --> E[Convert to isinstance lambda]
    E --> F[Apply condition to item]
    F --> G{condition(item) matches?}
    G -- Yes --> H[Return action]
    G -- No --> I[Continue loop]
    I --> J{End of loop?}
    J -- Yes --> K[Return repr]
    J -- No --> C
    D -- No --> F
    B -- No --> L[Return repr]
```

## Examples:
    # Basic usage with type-based conditions
    custom_repr = [
        (str, lambda x: f"'{x}'"),
        (int, lambda x: f"INT({x})")
    ]
    repr_func = get_repr_function("hello", custom_repr)
    result = repr_func("hello")  # Returns "'hello'"
    
    # Usage with callable conditions
    custom_repr = [
        (lambda x: isinstance(x, list) and len(x) > 0, lambda x: f"LIST({len(x)} items)")
    ]
    repr_func = get_repr_function([1,2,3], custom_repr)
    result = repr_func([1,2,3])  # Returns "LIST(3 items)"

## `pysnooper.utils.normalize_repr` · *function*

## Summary:
Applies a regex substitution to a string representation to remove matching patterns.

## Description:
This function performs a regex substitution operation on the provided string representation. It removes patterns that match the DEFAULT_REPR_RE regular expression pattern from the input string.

## Args:
    item_repr (str): The string representation to process.

## Returns:
    str: The result of applying the regex substitution DEFAULT_REPR_RE.sub('', item_repr).

## Raises:
    None explicitly documented.

## Constraints:
    Preconditions:
    - item_repr must be a string
    - DEFAULT_REPR_RE must be defined in the module scope
    
    Postconditions:
    - Returns a string processed by the regex substitution
    - The result contains the same content as input but with patterns matching DEFAULT_REPR_RE removed

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start normalize_repr] --> B[Apply DEFAULT_REPR_RE.sub('', item_repr)]
    B --> C[Return result]
```

## `pysnooper.utils.get_shortish_repr` · *function*

## Summary:
Creates a shortened, cleaned representation of an object suitable for debugging displays.

## Description:
Generates a string representation of an object with optional normalization and truncation. This function serves as a utility for creating clean, readable representations of objects in debugging contexts, particularly in the pysnooper library where it helps display variable states in a compact, informative way.

## Args:
    item (Any): The object to represent as a string
    custom_repr (tuple[tuple], optional): Custom representation rules as (condition, action) pairs. Defaults to empty tuple.
    max_length (int, optional): Maximum length of the returned string. If None, no truncation occurs. Defaults to None.
    normalize (bool): Whether to apply normalization to remove certain patterns from the representation. Defaults to False.

## Returns:
    str: A string representation of the item, cleaned of newlines/carriage returns, optionally normalized, and optionally truncated to max_length. Returns 'REPR FAILED' if representation generation raises an exception.

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
        - item can be any Python object
        - custom_repr must be iterable of (condition, action) tuples
        - max_length, when provided, must be a non-negative integer or None
        - normalize must be a boolean value

    Postconditions:
        - Always returns a string
        - Newlines and carriage returns are removed from the representation
        - If normalize=True, the result has patterns matching DEFAULT_REPR_RE removed
        - If max_length is specified, the result length will not exceed max_length

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_shortish_repr] --> B[Get repr function for item]
    B --> C{Exception in repr?}
    C -- Yes --> D[Set r = 'REPR FAILED']
    C -- No --> E[r = repr_function(item)]
    D --> F[r = r.replace('\r', '').replace('\n', '')]
    E --> F
    F --> G{normalize?}
    G -- Yes --> H[r = normalize_repr(r)]
    G -- No --> I
    H --> I
    I --> J{max_length specified?}
    J -- Yes --> K[r = truncate(r, max_length)]
    J -- No --> L
    K --> L
    L --> M[Return r]
```

## Examples:
    >>> get_shortish_repr("hello world")
    'hello world'
    
    >>> get_shortish_repr([1, 2, 3, 4, 5], max_length=10)
    '[1, 2, ...5]'
    
    >>> get_shortish_repr("hello\nworld", normalize=True)
    'hello world'
    
    >>> get_shortish_repr(object(), custom_repr=[])
    '<object object at 0x...>'
```

## `pysnooper.utils.truncate` · *function*

## Summary:
Truncates a string to a specified maximum length, preserving the beginning and end with an ellipsis in the middle.

## Description:
This function reduces the length of a string to a maximum specified length by removing characters from the middle and inserting an ellipsis ("..."). It's designed to create shortened representations of long strings while maintaining visibility of both the start and end portions. When the string length is less than or equal to the maximum length, the original string is returned unchanged.

## Args:
    string (str): The input string to be truncated.
    max_length (int or None): The maximum allowed length for the output string. If None, no truncation occurs and the original string is returned.

## Returns:
    str: The truncated string if the original exceeds max_length, otherwise the original string unchanged. The result is always a Unicode string.

## Raises:
    None

## Constraints:
    Preconditions:
    - The string parameter must be a valid string object
    - The max_length parameter must be either None or a non-negative integer
    
    Postconditions:
    - The returned string length will be at most max_length
    - If max_length is None, the original string is returned unchanged
    - If the original string length is less than or equal to max_length, the original string is returned unchanged
    - When truncation occurs, the resulting string will have exactly 3 characters for the ellipsis plus the left and right portions

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start truncate] --> B{max_length is None OR len(string) <= max_length?}
    B -- Yes --> C[Return original string]
    B -- No --> D[Calculate left portion length: (max_length - 3) // 2]
    D --> E[Calculate right portion length: max_length - 3 - left]
    E --> F[Return string[:left] + "..."+ string[-right:]]
```

## Examples:
    >>> truncate("This is a very long string", 10)
    'This ...ring'
    
    >>> truncate("Short", 10)
    'Short'
    
    >>> truncate("Very long string indeed", None)
    'Very long string indeed'
    
    >>> truncate("Hello World", 5)
    'He...d'

## `pysnooper.utils.ensure_tuple` · *function*

## Summary:
Converts an input to a tuple, preserving iterable objects while wrapping non-iterable values.

## Description:
The ensure_tuple function normalizes input values by converting iterables (except strings) to tuples, while wrapping non-iterable objects in a single-element tuple. This utility ensures consistent tuple-based processing regardless of input type.

## Args:
    x: Any object to be converted to a tuple. Can be iterable, string, or any other type.

## Returns:
    tuple: A tuple containing the elements of x if x is iterable (and not a string), otherwise a single-element tuple containing x.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input x can be any Python object
    - The function relies on collections_abc.Iterable and string_types from pycompat module
    
    Postconditions:
    - Return value is always a tuple
    - Strings are wrapped as single-element tuples rather than split into characters
    - Non-iterable objects are wrapped in a single-element tuple

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Input x] --> B{isinstance(x, Iterable)?}
    B -- Yes --> C{isinstance(x, string_types)?}
    C -- Yes --> D[return (x,)]
    C -- No --> E[return tuple(x)]
    B -- No --> D
```

## Examples:
    >>> ensure_tuple([1, 2, 3])
    (1, 2, 3)
    
    >>> ensure_tuple("hello")
    ('hello',)
    
    >>> ensure_tuple(42)
    (42,)
    
    >>> ensure_tuple((1, 2))
    (1, 2)
```

