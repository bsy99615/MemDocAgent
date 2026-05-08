# `inspector.py`

## `flower.inspector.Inspector` · *class*

## Summary:
An asynchronous inspector that collects metadata and status information from Celery workers.

## Description:
The Inspector class provides a mechanism to asynchronously gather various types of information from Celery workers. It's designed to collect statistics, queue information, registered tasks, scheduled jobs, active tasks, reserved tasks, revoked tasks, and configuration data from one or more workers. The class is typically used in monitoring systems to gather real-time worker status information.

This class serves as a centralized abstraction for worker inspection operations, providing a clean interface for collecting distributed worker information while managing concurrency through the provided I/O loop.

## State:
- io_loop: Event loop for executing inspection operations asynchronously
- capp: Celery application instance providing access to control interfaces
- timeout: Timeout duration for inspection requests in seconds
- workers: collections.defaultdict(dict) storing inspection results keyed by worker name, with each worker's data containing inspection responses and timestamp

## Lifecycle:
- Creation: Instantiate with io_loop, capp, and timeout parameters
- Usage: Call inspect() method to initiate inspection operations, which returns futures for async completion
- Destruction: No explicit cleanup required; relies on underlying event loop management

## Method Map:
```mermaid
graph TD
    A[inspect] --> B[_inspect]
    B --> C[control.inspect]
    C --> D[getattr(method)]
    D --> E[inspect_method()]
    E --> F[_on_update]
    F --> G[workers.update]
```

## Raises:
- No explicit exceptions are raised by __init__
- Exceptions may occur during inspection operations if underlying connections fail

## Example:
```python
# Create inspector instance
inspector = Inspector(io_loop, capp, timeout=1.0)

# Inspect all workers
futures = inspector.inspect()

# Inspect specific worker
futures = inspector.inspect(workername="worker1@hostname")

# Access collected data
worker_info = inspector.workers["worker1@hostname"]
```

### `flower.inspector.Inspector.__init__` · *method*

## Summary:
Initializes an Inspector instance with event loop, application context, timeout settings, and worker tracking structure.

## Description:
Configures the Inspector object with core dependencies and initializes the worker tracking data structure. This method establishes the fundamental state needed for the inspector to monitor and manage worker processes within a Celery application environment.

## Args:
    io_loop: Event loop instance for asynchronous operations
    capp: Celery application instance providing context and configuration
    timeout: Timeout duration for inspection operations

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.io_loop, self.capp, self.timeout, self.workers

## Constraints:
    Preconditions: All arguments must be valid objects compatible with the expected types
    Postconditions: Instance will have initialized io_loop, capp, timeout, and workers attributes

## Side Effects:
    None

### `flower.inspector.Inspector.inspect` · *method*

## Summary:
Initiates concurrent inspection operations across all registered worker methods and returns futures representing the ongoing operations.

## Description:
This method orchestrates parallel inspection requests to Celery workers by executing all defined inspection methods asynchronously. It creates a separate background task for each inspection method using the I/O loop executor, allowing multiple worker status queries to run simultaneously without blocking. The method is typically called during monitoring cycles to refresh worker information.

## Args:
    workername (str, optional): Specific worker identifier to target for inspection. If None, inspects all workers. Defaults to None.

## Returns:
    list: A list of future objects representing the concurrent inspection operations. Each future corresponds to one inspection method execution.

## Raises:
    None: This method does not raise exceptions directly; errors during inspection are handled internally and logged.

## State Changes:
    Attributes READ: self.methods, self.io_loop
    Attributes WRITTEN: None directly modified

## Constraints:
    Preconditions:
    - self.io_loop must be a valid I/O event loop capable of running executor tasks
    - self.methods must contain valid inspection method names
    - All inspection methods in self.methods must be callable on the Celery control interface
    
    Postconditions:
    - Concurrent inspection tasks are scheduled and running
    - Futures are returned immediately without waiting for completion
    - Individual inspection results will be processed asynchronously via _on_update callbacks

## Side Effects:
    - Asynchronous task scheduling: Queues inspection operations in the I/O loop executor
    - Background I/O operations: Triggers network communication with Celery workers
    - Logging: Generates debug and warning messages during inspection process

### `flower.inspector.Inspector._on_update` · *method*

## Summary:
Updates worker information with inspection results and records the timestamp of the update.

## Description:
This method is responsible for storing inspection responses from Celery workers into the internal workers dictionary. It is called asynchronously whenever a worker responds to an inspection command, updating the worker's state with the latest information and recording when the update occurred. The method serves as a key component in the real-time monitoring system that tracks worker status and performance metrics.

## Args:
    workername (str): Identifier of the worker that provided the response
    method (str): Name of the inspection method that was called (e.g., 'stats', 'active', 'registered')
    response: The response data returned from the worker's inspection method

## Returns:
    None: This method does not return a value

## Raises:
    KeyError: If workername does not exist in self.workers (though defaultdict would create it automatically)

## State Changes:
    Attributes READ: self.workers
    Attributes WRITTEN: self.workers[workername][method], self.workers[workername]['timestamp']

## Constraints:
    Preconditions:
    - workername must be a valid identifier for a worker in the system
    - method must be a valid inspection method name (from Inspector.methods tuple)
    - response should be serializable data structure returned from worker inspection
    
    Postconditions:
    - Worker information dictionary is updated with the new response data
    - Timestamp is set to current time for the worker's information

## Side Effects:
    None: This method performs only in-memory data updates and does not cause any I/O operations or external service calls

### `flower.inspector.Inspector._inspect` · *method*

## Summary:
Sends an inspection command to specified Celery workers and schedules asynchronous processing of their responses.

## Description:
Executes a dynamic inspect command on Celery workers to gather runtime information. This method is part of the Inspector class that monitors worker status and activity. It sends inspect commands to workers and schedules asynchronous updates when responses are received. The method handles special cases for the 'active' command which requires a safe parameter.

## Args:
    method (str): Name of the inspect method to execute (e.g., 'active', 'registered', 'task_types')
    workername (str, optional): Specific worker name to target. If None, targets all workers

## Returns:
    None: This method does not return a value directly

## Raises:
    None explicitly raised: The method handles errors internally and logs warnings

## State Changes:
    Attributes READ: self.capp, self.timeout, self.io_loop
    Attributes WRITTEN: None directly modified, but indirectly affects monitoring state through _on_update callbacks

## Constraints:
    Preconditions: 
    - self.capp must be a valid Celery app instance with control interface
    - self.timeout must be a valid timeout value for network operations
    - method must be a valid inspect method name available on the Celery control interface
    
    Postconditions:
    - If successful, worker update callbacks are scheduled via io_loop for processing
    - If failed, warning is logged but no exception is raised

## Side Effects:
    - Network I/O: Sends inspect commands to Celery workers via the control interface
    - Logging: Writes debug and warning messages to logger
    - Asynchronous callback scheduling: Uses io_loop to schedule _on_update calls for processing worker responses

