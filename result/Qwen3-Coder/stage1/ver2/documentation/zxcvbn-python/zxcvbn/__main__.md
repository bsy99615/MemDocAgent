# `__main__.py`

## `zxcvbn.__main__.JSONEncoder` · *class*

## Summary:
Custom JSON encoder that gracefully handles non-serializable objects by converting them to strings.

## Description:
A subclass of json.JSONEncoder designed to serialize objects that would normally cause JSON serialization to fail. When an object cannot be serialized by the standard JSON encoder, it falls back to converting the object to its string representation rather than raising an exception.

This encoder is particularly useful when serializing complex data structures that may contain objects of custom types or other non-standard JSON-serializable types.

## State:
- No instance attributes beyond those inherited from json.JSONEncoder
- Inherits all initialization parameters and behavior from json.JSONEncoder
- No special invariants or constraints beyond those of the parent class

## Lifecycle:
- Creation: Instantiated like any other json.JSONEncoder subclass
- Usage: Used automatically by json.dumps() when passed as the cls parameter
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[JSONEncoder.default] --> B{super().default(o)}
    B --> C{TypeError raised?}
    C -->|Yes| D[str(o)]
    C -->|No| E[Return result]
    D --> E
```

## Raises:
- TypeError: May be raised by the parent class's default method for truly unserializable objects, but is caught and handled internally

## Example:
```python
import json
from zxcvbn.__main__ import JSONEncoder

# Create a custom object
class CustomObject:
    def __init__(self, value):
        self.value = value

obj = CustomObject("test")

# Serialize using the custom encoder
result = json.dumps(obj, cls=JSONEncoder)
print(result)  # Output: "\"<__main__.CustomObject object at 0x...>\""
```

### `zxcvbn.__main__.JSONEncoder.default` · *method*

## Summary:
Handles serialization of non-standard Python objects to JSON-compatible format by converting them to strings when standard serialization fails.

## Description:
Overrides the default JSON serialization behavior to gracefully handle objects that are not natively serializable by Python's JSON encoder. When the standard serialization process raises a TypeError, this method converts the object to its string representation instead of failing.

## Args:
    self: The JSONEncoder instance
    o: The object to serialize to JSON

## Returns:
    The serialized object, either through normal JSON serialization or as a string representation

## Raises:
    TypeError: Only raised when the object cannot be serialized even after falling back to string conversion

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object being serialized must be compatible with Python's str() function
    Postconditions: The returned value is always JSON serializable (either a basic type or string)

## Side Effects:
    None

## `zxcvbn.__main__.cli` · *function*

## Summary:
Command-line interface for analyzing password strength using the zxcvbn algorithm.

## Description:
The cli() function provides a terminal-based interface for evaluating password security. It accepts a password through stdin (if available) or interactive prompting, performs strength analysis using the zxcvbn library, and outputs detailed results in JSON format.

This function extracts the input handling and output formatting logic from the main program flow, enabling clean separation between user interaction, password analysis, and result presentation. It serves as the primary entry point for the command-line utility while maintaining compatibility with piped input.

## Args:
    None - This function does not accept parameters directly

## Returns:
    None - This function does not return a value

## Raises:
    None - Exceptions from underlying functions are not explicitly caught or re-raised

## Constraints:
    Preconditions:
        - The global parser variable must be initialized with appropriate arguments
        - The zxcvbn function must be importable and callable
        - The JSONEncoder class must be importable and usable for serialization
    Postconditions:
        - Results are written to stdout in JSON format
        - Function exits after processing completes

## Side Effects:
    - Reads from stdin if available (via select.select)
    - Prompts user for password input via getpass if stdin is not available
    - Writes JSON-formatted analysis results to stdout
    - May block waiting for stdin input if data is available

## Control Flow:
```mermaid
flowchart TD
    A[Start cli()] --> B[Parse command-line arguments]
    B --> C[Check if stdin has data]
    C -->|Yes| D[Read password from stdin]
    C -->|No| E[Prompt user for password via getpass]
    D --> F[Strip trailing newline if present]
    E --> F
    F --> G[Call zxcvbn(password, user_inputs=args.user_input)]
    G --> H[Serialize result with JSONEncoder]
    H --> I[Write JSON to stdout]
    I --> J[Write trailing newline]
    J --> K[Exit]
```

## Examples:
    # Interactive usage
    $ python -m zxcvbn
    Password: ********
    {
      "password": "mypassword",
      "guesses": 123456,
      "guesses_log10": 5.09,
      "sequence": [...],
      "calc_time": 12345,
      "crack_times_seconds": {...},
      "crack_times_display": {...},
      "score": 2,
      "feedback": {...}
    }

    # Piped input usage
    $ echo "secret123" | python -m zxcvbn
    {
      "password": "secret123",
      "guesses": 456789,
      "guesses_log10": 5.66,
      "sequence": [...],
      "calc_time": 23456,
      "crack_times_seconds": {...},
      "crack_times_display": {...},
      "score": 1,
      "feedback": {...}
    }

