# `utils.py`

## `pysnooper.utils._check_methods` · *function*

*No documentation generated.*

## `pysnooper.utils.WritableStream` · *class*

## Summary:
Abstract base class defining a writable stream interface with a write method.

## Description:
WritableStream serves as an abstract base class that establishes a contract for writable stream objects. It defines the minimum interface required for objects that can accept written data, specifically requiring a `write` method. This class leverages Python's Abstract Base Class (ABC) framework and custom subclass checking to ensure compliance with the interface specification.

The class is designed to be inherited by concrete implementations that provide actual writing capabilities, such as file streams, buffer streams, or logging destinations. It enables polymorphic behavior where different stream implementations can be treated uniformly as WritableStream objects.

## State:
- write: Abstract method that must be implemented by subclasses to handle data writing operations
- No instance attributes beyond those defined by ABC machinery

## Lifecycle:
- Creation: Cannot be instantiated directly due to abstract nature
- Usage: Subclasses must implement the write method to be instantiable
- Destruction: Managed by Python's garbage collection; no special cleanup required

## Method Map:
```mermaid
graph TD
    A[WritableStream] --> B[write(s)]
    A --> C[__subclasshook__(C)]
    B --> D[Abstract method]
    C --> E[Method validation]
```

## Raises:
- TypeError: When attempting to instantiate the abstract class directly
- NotImplementedError: When subclasses don't implement the required write method

## Example:
```python
from pysnooper.utils import WritableStream

class MyStream(WritableStream):
    def write(self, s):
        print(f"Writing: {s}")

# Usage
stream = MyStream()  # Valid instantiation of subclass
stream.write("Hello World")  # Calls the implemented write method
```

### `pysnooper.utils.WritableStream.write` · *method*

## Summary:
Abstract interface method for writing string data to a stream destination.

## Description:
This abstract method defines the required interface for writing string data to a stream-like object. As part of the WritableStream abstract base class in the pysnooper debugging library, it establishes the contract that all concrete implementations must fulfill. Concrete subclasses must override this method to provide actual writing functionality to their specific output destination.

## Args:
    s (str): The string data to be written to the stream. Must be a valid string type.

## Returns:
    None: This method does not return any value.

## Raises:
    NotImplementedError: This abstract method must be implemented by concrete subclasses to provide actual writing functionality.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The implementing subclass must properly initialize any internal state needed for writing operations.
    Postconditions: The string data is written to the appropriate output destination as defined by the subclass implementation.

## Side Effects:
    I/O operations: Writes data to the underlying stream destination (file, buffer, stdout, etc.) as determined by the concrete implementation.

### `pysnooper.utils.WritableStream.__subclasshook__` · *method*

*No documentation generated.*

## `pysnooper.utils.shitcode` · *function*

## Summary:
Sanitizes a string by replacing non-printable ASCII characters with question marks.

## Description:
Filters input string to retain only characters with ordinal values between 1 and 255 (inclusive), replacing all other characters with '?'.

## Args:
    s (str): Input string to sanitize

## Returns:
    str: Sanitized string containing only printable ASCII characters (ordinals 1-255) with non-conforming characters replaced by '?'

## Raises:
    None

## Constraints:
    Preconditions: Input must be a string
    Postconditions: Output string contains only characters with ordinals in range [1, 255]

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input string s] --> B{Character ordinal 0 < ord(c) < 256?}
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
    >>> shitcode("test\x00invalid")
    'test?invalid'
```

## `pysnooper.utils.get_repr_function` · *function*

*No documentation generated.*

## `pysnooper.utils.normalize_repr` · *function*

*No documentation generated.*

## `pysnooper.utils.get_shortish_repr` · *function*

*No documentation generated.*

## `pysnooper.utils.truncate` · *function*

*No documentation generated.*

## `pysnooper.utils.ensure_tuple` · *function*

*No documentation generated.*

