# `tasks.py`

## `examples.tasks.add` · *function*

## Summary:
Performs arithmetic addition of two numeric values and returns their sum.

## Description:
This function accepts two numeric arguments and computes their mathematical sum. It serves as a basic utility for performing addition operations within the task processing system.

## Args:
    x (int or float): First operand for addition
    y (int or float): Second operand for addition

## Returns:
    int or float: The arithmetic sum of x and y

## Raises:
    TypeError: If either argument does not support the + operator (e.g., incompatible types like string + integer)

## Constraints:
    Preconditions: Both arguments must be compatible numeric types (int, float, or other types supporting the + operator)
    Postconditions: The result maintains the appropriate numeric type based on input types

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start add(x,y)] --> B{Arguments Valid?}
    B -->|No| C[Throw TypeError]
    B -->|Yes| D[Return x + y]
    D --> E[End]
```

## Examples:
```python
# Basic usage
result = add(2, 3)  # Returns 5

# With floats
result = add(2.5, 1.7)  # Returns 4.2

# With negative numbers
result = add(-1, 5)  # Returns 4
```

## `examples.tasks.sleep` · *function*

## Summary:
Pauses execution for a specified number of seconds.

## Description:
Wraps Python's built-in time.sleep() function to introduce delays in execution. This function is commonly used in task processing workflows to simulate work, add retry delays, or control execution timing.

## Args:
    seconds (float): Number of seconds to pause execution. Must be non-negative. Fractional seconds are supported.

## Returns:
    None: This function does not return any value.

## Raises:
    TypeError: If seconds is not a number (int or float).
    ValueError: If seconds is negative.

## Constraints:
    Preconditions: 
    - seconds must be a numeric value (int or float)
    - seconds must be greater than or equal to zero
    
    Postconditions:
    - Execution is paused for exactly seconds seconds
    - Function returns control to caller after the delay

## Side Effects:
    - Blocks the current thread for the specified duration
    - No external state mutations or I/O operations beyond the system sleep call

## Control Flow:
```mermaid
flowchart TD
    A[Call sleep(seconds)] --> B{seconds is numeric?}
    B -- No --> C[Raise TypeError]
    B -- Yes --> D{seconds < 0?}
    D -- Yes --> E[Raise ValueError]
    D -- No --> F[time.sleep(seconds)]
    F --> G[Return]
```

## Examples:
    # Basic usage
    sleep(2.5)  # Pauses for 2.5 seconds
    
    # Usage in a task context
    def process_task():
        # Simulate work
        sleep(1)
        # Continue with processing
        return "Task completed"

## `examples.tasks.echo` · *function*

## Summary:
Returns a formatted message with optional timestamp prefix.

## Description:
Formats and returns a message string, optionally prepending the current timestamp. This utility function provides a simple way to add temporal context to messages, commonly used for logging or debugging purposes.

## Args:
    msg (str): The message to be returned or formatted with timestamp.
    timestamp (bool): Flag indicating whether to prepend timestamp. Defaults to False.

## Returns:
    str: The original message if timestamp=False, or the message prefixed with current timestamp if timestamp=True.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions: 
    - msg must be a string
    - timestamp must be a boolean value
    
    Postconditions:
    - Returns a string value
    - If timestamp=True, result starts with timestamp followed by ": "

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start echo()] --> B{timestamp == True?}
    B -->|Yes| C[Format timestamp:msg]
    B -->|No| D[Return msg]
    C --> E[Return formatted string]
    D --> E
```

## Examples:
    >>> echo("Hello World")
    'Hello World'
    
    >>> echo("Hello World", timestamp=True)
    '2023-01-01 12:00:00.123456: Hello World'

## `examples.tasks.error` · *function*

## Summary:
Raises an exception with the specified error message.

## Description:
This function serves as a utility for explicitly raising exceptions in the task processing system. It is typically called when a task encounters an unrecoverable error condition that requires immediate termination of the current operation.

## Args:
    msg (str): The error message to include in the raised exception.

## Returns:
    This function does not return normally; it always raises an exception.

## Raises:
    Exception: Always raised with the provided message string.

## Constraints:
    Preconditions: None
    Postconditions: This function never returns successfully.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[error(msg)] --> B[Raise Exception(msg)]
    B --> C[Exit with Error]
```

## Examples:
```python
# Basic usage
error("Task failed due to invalid input")

# In a task context
def process_task(data):
    if not data:
        error("No data provided for processing")
    # ... rest of processing logic
```

