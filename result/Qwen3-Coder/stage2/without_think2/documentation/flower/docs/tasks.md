# `tasks.py`

## `docs.tasks.add` · *function*

## Summary:
Performs addition of two numeric values and returns their sum.

## Description:
This function takes two numeric arguments and returns their arithmetic sum. It is designed to be used as a Celery task for distributed computation, where it can be queued and executed asynchronously. The function encapsulates a simple mathematical operation that can be easily parallelized across multiple workers.

## Args:
    x (int or float): The first operand for addition.
    y (int or float): The second operand for addition.

## Returns:
    int or float: The result of adding x and y together. The return type matches the numeric type of the inputs.

## Raises:
    TypeError: If either x or y is not a numeric type (int, float) that supports the '+' operator.

## Constraints:
    Preconditions:
        - Both x and y must be instances of numeric types (int, float) that support the '+' operator.
    Postconditions:
        - The returned value will be the mathematical sum of x and y.
        - The function will not modify any external state or variables.

## Side Effects:
    None. This function performs no I/O operations, modifies no global state, and makes no external service calls.

## Control Flow:
```mermaid
flowchart TD
    A[Start add(x,y)] --> B{Are x and y numeric?}
    B -->|No| C[raise TypeError]
    B -->|Yes| D[return x + y]
    C --> E[End]
    D --> E[End]
```

## Examples:
    >>> add(2, 3)
    5
    >>> add(1.5, 2.5)
    4.0
    >>> add(-1, 1)
    0
    
    In a Celery task context:
    >>> from docs.tasks import add
    >>> result = add.delay(5, 3)  # Queues the task for background execution
    >>> result.get()  # Retrieves the result when ready
    8

## `docs.tasks.sub` · *function*

## Summary:
Performs subtraction of two numeric values with a 30-second simulated delay, suitable for asynchronous task processing.

## Description:
This function executes a subtraction operation between two numeric arguments after introducing a 30-second delay to simulate computationally intensive work. It is intended for use in asynchronous task queues like Celery, where long-running operations can be offloaded to background workers. The delay helps simulate real-world scenarios involving I/O-bound or CPU-intensive tasks.

## Args:
    x (int or float): The minuend, the number from which another number is to be subtracted.
    y (int or float): The subtrahend, the number to be subtracted from x.

## Returns:
    int or float: The mathematical difference of x minus y.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
        - Both x and y must be numeric types (int or float).
        - The caller should account for the 30-second execution time.
    Postconditions:
        - The function will return the exact mathematical difference of x and y.
        - Execution will block for approximately 30 seconds due to the sleep() call.

## Side Effects:
    - Blocks execution for 30 seconds via sleep(30).
    - No external I/O, state changes, or network calls occur.

## Control Flow:
```mermaid
flowchart TD
    A[Start sub(x,y)] --> B{Validate inputs}
    B --> C[sleep(30)]
    C --> D[Calculate x - y]
    D --> E[Return result]
```

## Examples:
    # Basic integer subtraction
    result = sub(10, 3)
    # Returns 7 after 30 seconds
    
    # Float subtraction
    result = sub(5.5, 2.2)
    # Returns 3.3 after 30 seconds
    
    # Negative result
    result = sub(2, 5)
    # Returns -3 after 30 seconds
```

