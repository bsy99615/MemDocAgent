# `__main__.py`

## `zxcvbn.__main__.JSONEncoder` · *class*

## Summary:
A custom JSON encoder that handles serialization of non-standard Python objects by falling back to string representation.

## Description:
This class extends the standard `json.JSONEncoder` to provide enhanced serialization capabilities. When the standard JSON encoder cannot serialize an object, it catches the `TypeError` and converts the object to its string representation instead. This allows for graceful handling of objects that would normally cause serialization errors.

## State:
- No instance attributes beyond those inherited from `json.JSONEncoder`
- Inherits all initialization parameters and behavior from the parent class

## Lifecycle:
- Creation: Instantiated automatically by the JSON serialization process when needed
- Usage: Called internally by `json.dumps()` when encountering unserializable objects
- Destruction: Managed automatically by Python's garbage collector

## Method Map:
```mermaid
graph TD
    A[json.dumps()] --> B[JSONEncoder.default()]
    B --> C{Can serialize?}
    C -->|Yes| D[Return serialized]
    C -->|No| E[TypeError raised]
    E --> F[catch TypeError]
    F --> G[Convert to str]
    G --> H[Return string repr]
```

## Raises:
- TypeError: Raised by the parent `json.JSONEncoder.default()` when an object cannot be serialized, caught internally and handled by returning string representation

## Example:
```python
import json
from zxcvbn.__main__ import JSONEncoder

# Custom object that can't be serialized by default
class CustomObject:
    def __init__(self, value):
        self.value = value

obj = CustomObject("test")
# Without custom encoder, this would fail
result = json.dumps(obj, cls=JSONEncoder)
print(result)  # Output: "\"<__main__.CustomObject object at 0x...>\""
```

### `zxcvbn.__main__.JSONEncoder.default` · *method*

## Summary:
Handles serialization of non-standard Python objects to JSON by falling back to string conversion when native JSON serialization fails.

## Description:
This method overrides the default serialization behavior of json.JSONEncoder to gracefully handle objects that are not natively serializable to JSON. When the parent class's default serialization fails due to a TypeError (indicating the object type is not supported by JSON), it converts the object to its string representation instead. This ensures that all objects can be serialized to JSON format, even if they are not naturally JSON-serializable.

## Args:
    o (Any): The Python object to serialize to JSON format

## Returns:
    str: String representation of the object when native JSON serialization fails, or the result of parent class serialization when successful

## Raises:
    TypeError: When the object cannot be serialized to JSON and cannot be converted to a string

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object being serialized must be compatible with either JSON serialization or string conversion
    Postconditions: The returned value is always a string that represents the object in a serializable format

## Side Effects:
    None

## `zxcvbn.__main__.cli` · *function*

## Summary:
Command-line interface function that reads a password from stdin or user input, analyzes its strength using the zxcvbn algorithm, and outputs the results as formatted JSON.

## Description:
This function serves as the entry point for the zxcvbn command-line tool. It provides a user-friendly interface for analyzing password strength by accepting passwords either through standard input or interactive prompts. The function orchestrates the entire password analysis workflow, from input handling to result serialization.

The function is designed to be robust in different execution environments - when input is piped to the program via stdin, it reads directly from the pipe; otherwise, it securely prompts the user for input using the `getpass` module to hide the password entry.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## Constraints:
    Precondition: The `parser` global variable must be initialized with appropriate argument definitions
    Precondition: The `zxcvbn` function must be available in the module scope
    Precondition: The `JSONEncoder` class must be available in the module scope

## Side Effects:
    - Reads from stdin if available (via select.select)
    - Prompts user for password input via terminal if stdin is not available
    - Writes JSON-formatted analysis results to stdout
    - May write to stderr if getpass fails (though this is not explicitly handled)

## Control Flow:
```mermaid
flowchart TD
    A[Start cli()] --> B{stdin available?}
    B -->|Yes| C[Read from stdin]
    B -->|No| D[Get password via getpass]
    C --> E[Strip trailing newline]
    D --> E
    E --> F[Call zxcvbn(password, user_inputs=args.user_input)]
    F --> G[Serialize result with JSONEncoder]
    G --> H[Write JSON to stdout]
    H --> I[Write newline]
```

## Examples:
```bash
# Interactive mode
$ python -m zxcvbn
Password: ********
{
  "password": "secret123",
  "score": 2,
  "guesses": 1000000,
  ...
}

# Piped input
$ echo "mypassword" | python -m zxcvbn
{
  "password": "mypassword",
  "score": 1,
  "guesses": 10000,
  ...
}

# With user inputs
$ python -m zxcvbn --user-input "john" --user-input "doe"
{
  "password": "secret123",
  "score": 3,
  "guesses": 10000000,
  ...
}
```

