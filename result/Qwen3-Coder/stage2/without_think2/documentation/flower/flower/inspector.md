# `inspector.py`

## `flower.inspector.Inspector` · *class*

## Summary:
Inspector is a class that manages asynchronous inspection of Celery workers to gather various status and configuration information.

## Description:
The Inspector class is responsible for collecting runtime information from Celery workers by executing inspection commands asynchronously. It provides a mechanism to fetch worker statistics, queue information, registered tasks, scheduled tasks, active tasks, reserved tasks, revoked tasks, and configuration data. The class is designed to work with an I/O loop for asynchronous execution and maintains a cache of worker information.

## State:
- io_loop: Event loop for handling asynchronous operations
- capp: Celery application instance used to access control interface  
- timeout: Timeout value for inspection requests
- workers: Dictionary mapping worker names to their inspected information, maintained as a defaultdict of dictionaries
- methods: Tuple of inspection method names that are supported

## Lifecycle:
- Creation: Instantiate with io_loop, capp, and timeout parameters
- Usage: Call inspect() method to initiate inspection process, which returns futures for async completion
- Destruction: No explicit cleanup required; relies on underlying event loop management

## Method Map:
```mermaid
graph TD
    A[inspect] --> B[_inspect]
    B --> C[control.inspect]
    C --> D[getattr(method)]
    D --> E[_on_update]
    E --> F[workers update]
```

## Raises:
- No explicit exceptions are raised by __init__
- Exceptions may occur during asynchronous execution in _inspect method when handling responses

## Example:
```python
# Create inspector instance
inspector = Inspector(io_loop, capp, timeout=1.0)

# Start inspection for all workers
futures = inspector.inspect()

# Start inspection for specific worker
futures = inspector.inspect(workername="worker1@hostname")
```

### `flower.inspector.Inspector.__init__` · *method*

## Summary:
Initializes the Inspector instance with event loop, application context, and timeout settings.

## Description:
The `__init__` method sets up the core configuration for the Inspector object by storing references to the I/O event loop, Celery application context, and timeout duration. It also initializes an empty dictionary structure for tracking worker information.

This method serves as the constructor for the Inspector class, establishing the fundamental state needed for monitoring and inspecting Celery workers. The separation into its own method allows for clean initialization and makes the object's setup process explicit and testable.

## Args:
    io_loop: The I/O event loop instance used for asynchronous operations.
    capp: The Celery application context containing broker connection and task definitions.
    timeout: The maximum time in seconds to wait for responses from workers.

## Returns:
    None

## Raises:
    No exceptions are explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.io_loop: Stores the provided I/O event loop reference
    - self.capp: Stores the provided Celery application context
    - self.timeout: Stores the provided timeout value
    - self.workers: Initializes an empty defaultdict(dict) for worker tracking

## Constraints:
    Preconditions:
    - io_loop must be a valid I/O event loop instance
    - capp must be a valid Celery application context
    - timeout must be a numeric value representing seconds

    Postconditions:
    - All instance attributes are properly initialized
    - self.workers is initialized as an empty collections.defaultdict(dict)

## Side Effects:
    None

### `flower.inspector.Inspector.inspect` · *method*

## Summary:
Initiates asynchronous inspection of registered methods across worker processes.

## Description:
This method orchestrates the parallel execution of inspection tasks for all registered methods by submitting them to an executor pool. It enables concurrent monitoring of method availability and status across distributed workers. The inspection process retrieves information such as worker statistics, queue status, and task information from registered Celery workers.

## Args:
    workername (str, optional): Specific worker identifier to target for inspection. Defaults to None, which inspects all workers.

## Returns:
    list: A list of future objects representing the asynchronous inspection tasks for each registered method. Each future will eventually contain inspection results from worker processes.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.methods, self.io_loop, self.capp
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.methods must be iterable containing method objects
    - self.io_loop must be a valid event loop instance supporting run_in_executor
    - self.capp must be a valid Celery app instance with control.inspect capability
    Postconditions: 
    - Returns a list of futures that will eventually contain inspection results
    - Inspection tasks are submitted to the executor pool for concurrent execution

## Side Effects:
    - Submits tasks to an executor pool via io_loop.run_in_executor
    - Initiates network I/O operations to communicate with Celery workers
    - May trigger logging messages during inspection process

### `flower.inspector.Inspector._on_update` · *method*

## Summary:
Updates worker method response data and timestamp for a specific worker.

## Description:
This method handles incoming updates from workers by storing method execution responses and updating the worker's last activity timestamp. It serves as a centralized handler for worker status updates in the inspector system.

## Args:
    workername (str): The unique identifier of the worker providing the update
    method (str): The method name being updated
    response: The response data returned from the method execution

## Returns:
    None

## Raises:
    KeyError: When workername does not exist in self.workers dictionary

## State Changes:
    Attributes READ: self.workers
    Attributes WRITTEN: self.workers[workername][method], self.workers[workername]['timestamp']

## Constraints:
    Preconditions: 
    - workername must exist as a key in self.workers dictionary
    - self.workers[workername] must be a mutable mapping type (dict-like)
    Postconditions:
    - The specified method entry in worker info is updated with response
    - The worker's timestamp is set to current time

## Side Effects:
    None

### `flower.inspector.Inspector._inspect` · *method*

## Summary:
Sends an inspection command to Celery workers and processes the responses asynchronously.

## Description:
This method executes a control command against Celery workers to gather runtime information. It handles the communication with the Celery control interface, manages timeouts, and dispatches results to update handlers. The method is designed to be called internally by other inspection methods and supports both regular and safe execution modes for different command types.

## Args:
    method (str): Name of the inspection method to execute (e.g., 'active', 'reserved', 'scheduled')
    workername (str, optional): Specific worker name to target. If None, targets all workers

## Returns:
    None: This method does not return a value directly

## Raises:
    None explicitly raised: The method handles errors internally through logging

## State Changes:
    Attributes READ: self.capp, self.timeout, self.io_loop, logger
    Attributes WRITTEN: None directly modified, but indirectly affects state via callbacks

## Constraints:
    Preconditions: 
    - self.capp must be initialized with a valid Celery app instance
    - self.timeout must be a valid numeric timeout value
    - self.io_loop must be a valid event loop instance
    - method must be a valid method name available on the Celery inspect interface
    
    Postconditions:
    - If successful, the method schedules asynchronous updates via self.io_loop.add_callback
    - If failed, appropriate warning logs are generated

## Side Effects:
    - Makes network calls to Celery workers via self.capp.control.inspect
    - Logs debug and warning messages using the logger
    - Schedules callback functions on the event loop (self.io_loop.add_callback)
    - May trigger additional I/O operations through the _on_update callback

