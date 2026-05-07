# `tasks.py`

## `examples.tasks.add` · *function*

## Summary:
Adds two numeric values and returns their sum.

## Description:
This function performs addition of two numeric operands. It is designed to be used as a simple arithmetic operation that can be executed synchronously or asynchronously within a task processing system.

## Args:
    x (int or float): The first operand to be added.
    y (int or float): The second operand to be added.

## Returns:
    int or float: The sum of x and y. The return type matches the numeric type of the inputs.

## Raises:
    TypeError: If either x or y is not a numeric type (int or float) that supports the + operator.

## Constraints:
    Preconditions:
        - Both x and y must be numeric types (int, float) that support the + operator
        - No additional validation is performed on the input values
    
    Postconditions:
        - The result will be the mathematical sum of the two input values
        - The return type will be compatible with the input types

## Side Effects:
    None: This function has no side effects and is a pure mathematical operation.

## Control Flow:
```mermaid
flowchart TD
    A[Start add(x,y)] --> B{Inputs Valid?}
    B -->|Yes| C[Return x + y]
    B -->|No| D[Raise TypeError]
    C --> E[End]
    D --> E
```

## Examples:
    # Basic usage
    result = add(2, 3)
    # Returns: 5
    
    # With floats
    result = add(2.5, 1.7)
    # Returns: 4.2
    
    # Error case
    try:
        add("hello", "world")
    except TypeError as e:
        print(e)
    # Raises: TypeError
```

## `examples.tasks.sleep` · *function*

## Summary:
Pauses execution for a specified number of seconds.

## Description:
This function provides a simple interface to pause program execution for a given duration. It wraps Python's built-in `time.sleep()` function to provide a clean abstraction for timing operations in task processing workflows.

## Args:
    seconds (int or float): Number of seconds to pause execution. Must be non-negative.

## Returns:
    None: This function does not return any value.

## Raises:
    None: This function does not explicitly raise exceptions, though `time.sleep()` may raise exceptions under certain conditions (e.g., negative values).

## Constraints:
    Preconditions: The `seconds` parameter must be a non-negative number.
    Postconditions: Execution is paused for exactly the specified duration (approximately).

## Side Effects:
    I/O: Causes the current thread to sleep, effectively blocking execution.
    Timing: Affects the timing and scheduling of subsequent operations in the program.

## Control Flow:
```mermaid
flowchart TD
    A[Call sleep(seconds)] --> B{seconds >= 0?}
    B -- Yes --> C[time.sleep(seconds)]
    B -- No --> D[Raise ValueError]
    C --> E[Execution paused]
    D --> F[Exception raised]
```

## Examples:
    # Basic usage
    sleep(2)  # Pauses execution for 2 seconds
    
    # With fractional seconds
    sleep(0.5)  # Pauses execution for half a second
``

## `examples.tasks.echo` · *function*

## Summary:
Formats and optionally timestamps a message string for logging or display purposes.

## Description:
This utility function prepares messages for output by optionally prepending the current timestamp. It serves as a standardized way to add temporal context to log entries or user-facing messages while maintaining flexibility in formatting.

## Args:
    msg (str): The message string to be formatted or returned as-is.
    timestamp (bool): Flag indicating whether to prepend the current timestamp. Defaults to False.

## Returns:
    str: The formatted message with optional timestamp prefix, or the original message if timestamp is False.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions:
        - The `msg` parameter must be a string type.
        - The `timestamp` parameter must be a boolean type.
    
    Postconditions:
        - The returned value is always a string.
        - If timestamp=True, the returned string begins with a timestamp in ISO format followed by ": ".
        - If timestamp=False, the returned string equals the input `msg`.

## Side Effects:
    None: This function has no side effects and is pure.

## Control Flow:
```mermaid
flowchart TD
    A[Start echo()] --> B{timestamp == True?}
    B -->|Yes| C[Format timestamp + msg]
    B -->|No| D[Return msg]
    C --> E[Return formatted string]
    D --> E
```

## Examples:
    # Basic usage without timestamp
    result = echo("Hello World")
    # Returns: "Hello World"
    
    # Usage with timestamp
    result = echo("Task completed", timestamp=True)
    # Returns: "2023-06-15 14:30:45.123456: Task completed"

## `examples.tasks.error` · *function*

## Summary:
Raises an exception with the specified error message.

## Description:
This function serves as a utility for explicitly raising exceptions in the task processing system. It is designed to be a centralized point for error propagation throughout the application's workflow.

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
    A[Call error(msg)] --> B[Raise Exception(msg)]
    B --> C[Exception Propagated]
```

## Examples:
```python
# Basic usage
error("Something went wrong")

# In a task context
def process_task():
    if not validate_input(data):
        error("Invalid input data provided")
```

