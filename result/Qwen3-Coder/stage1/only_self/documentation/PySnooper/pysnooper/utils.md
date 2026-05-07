# `utils.py`

## `pysnooper.utils._check_methods` · *function*

## Summary:
Checks whether a class implements all specified methods by examining its Method Resolution Order (MRO).

## Description:
This utility function validates that a given class implements all required methods by traversing its Method Resolution Order (MRO) to check for method existence. It's commonly used in abstract base class implementations and protocol checking to ensure classes conform to expected interfaces.

The function is typically used in ABC metaclass implementations or protocol validation systems where it's necessary to verify that a class provides a complete interface. It returns True if all methods are implemented and not None, NotImplemented if any method is missing or explicitly set to None, and raises TypeError for invalid inputs (when the first argument is not a class).

## Args:
    C (type): The class to check for method implementations
    *methods (str): Variable-length argument list of method names to check for existence

## Returns:
    bool or NotImplemented: Returns True if all methods are implemented and not None, NotImplemented if any method is missing or explicitly set to None

## Raises:
    TypeError: When the first argument is not a class/type object (during __mro__ access)

## Constraints:
    Preconditions:
    - The first argument must be a valid class/type object
    - All method names must be strings
    
    Postconditions:
    - Returns either True, NotImplemented, or raises TypeError
    - Does not modify the input class or methods

## Side Effects:
    None: This function performs only read operations on class metadata and does not mutate any state.

## Control Flow:
```mermaid
flowchart TD
    A[Start _check_methods] --> B{C is class?}
    B -- No --> C[Raise TypeError]
    B -- Yes --> D[Get MRO of C]
    D --> E[For each method in methods]
    E --> F{Method in B.__dict__?}
    F -- No --> G[Return NotImplemented]
    F -- Yes --> H{B.__dict__[method] is None?}
    H -- Yes --> I[Return NotImplemented]
    H -- No --> J[Continue to next method]
    G --> K[Exit loop]
    I --> K
    J --> K
    K --> L[All methods checked]
    L --> M[Return True]
```

## Examples:
```python
# Basic usage to check if a class implements required methods
class MyProtocol:
    def required_method(self): pass

class Implementation:
    def required_method(self): return "implemented"

# Check if Implementation satisfies MyProtocol
result = _check_methods(Implementation, 'required_method')
# Returns True

# Check with missing method
class Incomplete:
    pass

result = _check_methods(Incomplete, 'required_method')
# Returns NotImplemented

# Check with explicitly None method (common in ABC patterns)
class WithNoneMethod:
    required_method = None

result = _check_methods(WithNoneMethod, 'required_method')
# Returns NotImplemented

# Typical usage in ABC-like protocol checking
class Drawable:
    @classmethod
    def __subclasshook__(cls, subclass):
        return _check_methods(subclass, '__draw__', 'get_area')

class Shape:
    def __draw__(self): pass
    def get_area(self): return 0

# This would return True because Shape implements both methods
result = Drawable.__subclasshook__(Shape)
```

## `pysnooper.utils.WritableStream` · *class*

## Summary:
An abstract base class defining a writable stream interface that requires implementing a write method.

## Description:
The WritableStream class serves as an abstract base class that establishes a contract for writable stream objects. It defines the minimal interface required for writing data, specifically requiring any subclass to implement a `write` method. This abstraction allows for polymorphic handling of different writable streams while ensuring type safety through the abstract base class mechanism.

The class leverages Python's abstract base class infrastructure and uses a custom `__subclasshook__` method to enable duck typing checks. This means that classes don't necessarily need to explicitly inherit from WritableStream to be considered compatible - they simply need to implement the required interface methods.

## State:
- No instance attributes: This is an abstract base class with no instance state
- No constructor parameters: The class doesn't accept initialization arguments
- Class invariant: All concrete subclasses must implement the write method

## Lifecycle:
- Creation: Instantiate by inheriting from this class or by implementing the required interface methods
- Usage: Subclasses must implement the abstract write method to be instantiable
- Destruction: No special cleanup required; follows normal Python object lifecycle

## Method Map:
```mermaid
flowchart TD
    A[WritableStream] --> B[write(s)]
    B --> C[Concrete Implementation]
    A --> D[__subclasshook__(C)]
    D --> E{_check_methods(C, 'write')}
```

## Raises:
- TypeError: When attempting to instantiate a subclass that has unimplemented abstract methods
- AttributeError: When trying to use abstract methods without proper implementation in subclasses

## Example:
```python
from pysnooper.utils import WritableStream

class FileStream(WritableStream):
    def __init__(self, filename):
        self.filename = filename
    
    def write(self, s):
        with open(self.filename, 'w') as f:
            f.write(s)

# This works because FileStream implements the required write method
stream = FileStream("output.txt")
stream.write("Hello, world!")

# This would raise TypeError because no write method is implemented
class IncompleteStream(WritableStream):
    pass

# incomplete = IncompleteStream()  # TypeError: Can't instantiate abstract class
```

### `pysnooper.utils.WritableStream.write` · *method*

*No documentation generated.*

### `pysnooper.utils.WritableStream.__subclasshook__` · *method*

## Summary:
Determines if a class is considered a subclass of WritableStream by checking for implementation of the 'write' method.

## Description:
This special method is part of Python's Abstract Base Class (ABC) mechanism and is invoked when checking if a class is a subclass of WritableStream. It implements protocol-based subclass checking by verifying that the candidate class implements the required 'write' method. This allows classes that don't inherit directly from WritableStream but implement the required interface to be treated as subclasses.

The method is called during isinstance() and issubclass() checks involving WritableStream. It leverages the _check_methods utility to validate method implementation in the class's Method Resolution Order (MRO).

## Args:
    cls (type): The WritableStream class itself (always passed as the first argument)
    C (type): The candidate class being checked for subclass relationship

## Returns:
    bool or NotImplemented: Returns True if class C implements the 'write' method, NotImplemented otherwise

## Raises:
    None: This method doesn't raise exceptions directly, though _check_methods may raise TypeError

## State Changes:
    Attributes READ: None - this method only reads class metadata
    Attributes WRITTEN: None - this method doesn't modify any instance or class attributes

## Constraints:
    Preconditions:
    - cls must be the WritableStream class itself
    - C must be a valid class/type object
    - The 'write' method name must be a string
    
    Postconditions:
    - Returns either True, False, or NotImplemented based on method implementation
    - Does not modify the state of either class

## Side Effects:
    None: This method performs only read operations on class metadata and does not mutate any state or perform I/O operations.

## `pysnooper.utils.shitcode` · *function*

## Summary:
Filters out non-printable or non-ASCII characters from a string, replacing them with question marks.

## Description:
This utility function sanitizes input strings by retaining only characters with ordinal values in the range (0, 256), effectively filtering out extended ASCII and Unicode characters. Characters outside this range are replaced with '?' to prevent encoding issues or display problems.

## Args:
    s (str): Input string to sanitize, potentially containing non-ASCII or non-printable characters

## Returns:
    str: A sanitized string where characters with ordinal values outside the range (0, 256) have been replaced with '?'

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Input must be a string type
    - Function assumes string is iterable
    
    Postconditions:
    - Output string contains only characters with ordinals in range (0, 256)
    - Length of output string is equal to or less than input string length

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input string s] --> B{Character ordinal in range (0,256)?}
    B -- Yes --> C[Keep character]
    B -- No --> D[Replace with '?']
    C --> E[Join characters]
    D --> E
    E --> F[Return sanitized string]
```

## Examples:
    >>> shitcode("Hello, World!")
    'Hello, World!'
    
    >>> shitcode("café")
    'caf?'
    
    >>> shitcode("test\x00\x01\x02")
    'test???'
```

## `pysnooper.utils.get_repr_function` · *function*

## Summary:
Selects an appropriate representation function for an object based on custom conditions and fallback to standard repr.

## Description:
This function evaluates a list of condition-action pairs to determine the most suitable representation function for an object. It's designed to enable customized object representation in debugging or logging contexts, falling back to the standard repr() function when no custom conditions match.

## Args:
    item (Any): The object to be represented
    custom_repr (list[tuple]): A list of (condition, action) pairs where:
        - condition: Either a type (for isinstance checks) or callable that accepts the item
        - action: A callable that produces the representation for matching items

## Returns:
    callable: A representation function that can be applied to the item. Either:
        - The matching action function from custom_repr if a condition matches
        - The built-in repr function if no conditions match

## Raises:
    None explicitly raised

## Constraints:
    - Precondition: custom_repr must be iterable containing (condition, action) tuples
    - Precondition: condition in custom_repr can be either a type or callable
    - Precondition: action in custom_repr must be callable
    - Postcondition: Returned function can be called with the item argument

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_repr_function] --> B{custom_repr empty?}
    B -- Yes --> C[Return repr]
    B -- No --> D[Iterate custom_repr]
    D --> E{condition is type?}
    E -- Yes --> F[Convert to isinstance lambda]
    E -- No --> G[Use condition as-is]
    G --> H{condition(item)?}
    H -- Yes --> I[Return action]
    H -- No --> J[Continue iteration]
    J --> K{End of custom_repr?}
    K -- Yes --> L[Return repr]
    K -- No --> D
```

## Examples:
    # Basic usage with type-based conditions
    custom_repr = [
        (str, lambda x: f"'{x}'"),
        (int, lambda x: f"INT({x})")
    ]
    repr_func = get_repr_function("hello", custom_repr)
    result = repr_func("hello")  # Returns "'hello'"
    
    # Fallback to repr when no conditions match
    custom_repr = [(str, lambda x: f"'{x}'")]
    repr_func = get_repr_function(42, custom_repr)
    result = repr_func(42)  # Returns repr(42) which is '42'

## `pysnooper.utils.normalize_repr` · *function*

## Summary:
Applies a predefined regex pattern to clean representation strings.

## Description:
Removes patterns from string representations using the DEFAULT_REPR_RE regular expression. This function serves as a utility for normalizing object representation strings in debugging contexts.

## Args:
    item_repr (str): String representation to be processed.

## Returns:
    str: String with patterns matching DEFAULT_REPR_RE removed.

## Raises:
    None explicitly documented.

## Constraints:
    Preconditions:
    - item_repr must be a string
    - DEFAULT_REPR_RE must be a valid compiled regex pattern
    
    Postconditions:
    - Returns a string of the same length or shorter
    - All matches of DEFAULT_REPR_RE are removed from input

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Input item_repr] --> B[DEFAULT_REPR_RE.sub('', item_repr)]
    B --> C[Return cleaned string]
```

## Examples:
    # Usage example (behavior depends on DEFAULT_REPR_RE definition):
    # normalize_repr("SomeObject(123)") -> "SomeObject(123)" (if no matches)
    # normalize_repr("<SomeObject object at 0x12345678>") -> "<SomeObject object>" (example behavior)
```

## `pysnooper.utils.get_shortish_repr` · *function*

## Summary:
Creates a cleaned and optionally truncated string representation of an object for debugging or logging purposes.

## Description:
Generates a formatted string representation of an object by applying several transformations. This function is primarily used in debugging contexts to produce readable, compact representations of objects while handling potential representation failures gracefully.

## Args:
    item (Any): The object to be represented
    custom_repr (tuple, optional): A tuple of (condition, action) pairs for custom representation logic. Defaults to empty tuple.
    max_length (int, optional): Maximum allowed length for the output string. If None, no truncation occurs. Defaults to None.
    normalize (bool): Whether to apply normalization to remove certain patterns from the representation. Defaults to False.

## Returns:
    str: A string representation of the item that has been cleaned of newlines, optionally normalized, and truncated if requested. Returns 'REPR FAILED' if representation generation raises an exception.

## Raises:
    None explicitly raised

## Constraints:
    - Precondition: If max_length is provided, it must be a non-negative integer
    - Precondition: custom_repr must be iterable containing (condition, action) tuples
    - Postcondition: Returned string will have newlines removed
    - Postcondition: Returned string will be at most max_length characters when max_length is specified
    - Postcondition: Returned string will be normalized if normalize=True

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_shortish_repr] --> B[Get repr_function via get_repr_function]
    B --> C[Try repr_function(item)]
    C --> D{Exception raised?}
    D -- Yes --> E[Set r = 'REPR FAILED']
    D -- No --> F[Set r = repr_function(item)]
    F --> G[r.replace('\r', '').replace('\n', '')]
    G --> H{normalize?}
    H -- Yes --> I[Apply normalize_repr(r)]
    H -- No --> J[Skip normalization]
    J --> K{max_length specified?}
    K -- Yes --> L[Apply truncate(r, max_length)]
    K -- No --> M[Skip truncation]
    L --> N[Return result]
    M --> N
```

## Examples:
    # Basic usage with default behavior
    result = get_shortish_repr("hello world")
    # Returns: 'hello world'
    
    # With newline removal
    result = get_shortish_repr("line1\\nline2")
    # Returns: 'line1line2'
    
    # With truncation
    result = get_shortish_repr("very long string", max_length=10)
    # Returns: 'very ...ng'
    
    # With normalization
    result = get_shortish_repr(some_object, normalize=True)
    # Returns: normalized representation of some_object
    
    # With custom representation
    custom_repr = [(str, lambda x: f"'{x}'")]
    result = get_shortish_repr("test", custom_repr=custom_repr)
    # Returns: "'test'"

## `pysnooper.utils.truncate` · *function*

## Summary:
Truncates a string to a specified maximum length, inserting an ellipsis in the center when necessary.

## Description:
This utility function reduces the length of a string to fit within a specified limit by removing characters from the middle and inserting an ellipsis (...) to indicate truncation. It is commonly used for displaying long strings in constrained UI space or log outputs.

## Args:
    string (str): The input string to be truncated
    max_length (int or None): Maximum allowed length for the output string. If None, no truncation occurs. Must be a non-negative integer when not None.

## Returns:
    str: The original string if it's shorter than or equal to max_length, or a truncated version with ellipsis inserted in the middle if it exceeds max_length.

## Raises:
    None

## Constraints:
    Precondition: When max_length is not None, it must be a non-negative integer.
    Postcondition: The returned string will have length less than or equal to max_length, or will be identical to the input string if it was already short enough.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start truncate] --> B{max_length is None OR len(string) ≤ max_length?}
    B -- Yes --> C[Return string]
    B -- No --> D[left = (max_length - 3) // 2]
    D --> E[right = max_length - 3 - left]
    E --> F[Return string[:left] + "..."+ string[-right:]]
```

## Examples:
    >>> truncate("Hello World", 8)
    'He...ld'
    
    >>> truncate("Short", 10)
    'Short'
    
    >>> truncate("VeryLongString", None)
    'VeryLongString'
    
    >>> truncate("Testing", 5)
    'T...g'
    
    >>> truncate("A", 3)
    'A'

## `pysnooper.utils.ensure_tuple` · *function*

## Summary:
Converts an input value to a tuple, preserving string inputs as single-element tuples while converting other iterables to proper tuples.

## Description:
This utility function normalizes input values to tuple format. It treats strings specially by wrapping them as single-element tuples rather than splitting them into character tuples, while other iterable objects are converted to tuples containing their elements.

## Args:
    x: Any object that may be iterable or non-iterable

## Returns:
    tuple: A tuple containing either:
        - The elements of x if x is iterable and not a string
        - A single-element tuple containing x if x is not iterable or is a string

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - Input x can be any Python object
    Postconditions:
        - Return value is always a tuple
        - Strings are preserved as single-element tuples
        - Other iterables are converted to tuples of their elements

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input x] --> B{isinstance(x, Iterable)?}
    B -- Yes --> C{isinstance(x, string_types)?}
    C -- Yes --> D[return (x,)]
    C -- No --> E[tuple(x)]
    B -- No --> D
```

## Examples:
    >>> ensure_tuple([1, 2, 3])
    (1, 2, 3)
    
    >>> ensure_tuple((1, 2, 3))
    (1, 2, 3)
    
    >>> ensure_tuple("hello")
    ('hello',)
    
    >>> ensure_tuple(42)
    (42,)
```

