# `inspector.py`

## `flower.inspector.Inspector` · *class*

## Summary:
An asynchronous inspector that collects and maintains metadata about Celery workers through periodic inspection commands.

## Description:
The Inspector class provides a mechanism to asynchronously gather information from Celery workers by executing various inspection methods. It maintains a cache of worker information and updates it periodically through background inspection operations. This class is designed to work with an event loop (io_loop) to handle concurrent inspection requests without blocking the main thread.

## State:
- io_loop: Event loop instance used for running inspection tasks concurrently
- capp: Celery application instance used to access inspection capabilities
- timeout: Timeout duration for inspection commands  
- workers: collections.defaultdict(dict) storing worker information with timestamps

## Lifecycle:
Creation: Instantiate with io_loop, capp, and timeout parameters
Usage: Call inspect() method to initiate inspection operations, which returns a list of futures that must be awaited for completion
Destruction: No explicit cleanup required; relies on event loop management

## Method Map:
```mermaid
graph TD
    A[inspect] --> B[_inspect]
    B --> C[control.inspect()]
    C --> D[getattr(method)]
    D --> E[_on_update]
    E --> F[workers update]
```

## Raises:
- No explicit exceptions are raised by __init__
- Exceptions from underlying inspection operations may propagate through the async execution

## Example:
```python
# Create inspector instance
inspector = Inspector(io_loop, celery_app, timeout=1.0)

# Start inspection for all workers
futures = inspector.inspect()
# Wait for results: await asyncio.gather(*futures)

# Start inspection for specific worker
futures = inspector.inspect(workername='worker1@hostname')
# Wait for results: await asyncio.gather(*futures)
```

### `flower.inspector.Inspector.__init__` · *method*

## Summary:
Initializes an Inspector instance with event loop, application context, timeout settings, and worker tracking structure.

## Description:
Configures the Inspector object with core dependencies and initializes the worker tracking mechanism. This constructor establishes the fundamental state required for the inspector to monitor and manage worker processes.

## Args:
    io_loop: Event loop instance for asynchronous operations
    capp: Application context or configuration object
    timeout: Timeout duration for operations in seconds

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.io_loop, self.capp, self.timeout, self.workers

## Constraints:
    Preconditions: All arguments must be provided and valid for their respective types
    Postconditions: Inspector instance is initialized with proper attribute values and worker tracking structure

## Side Effects:
    None

### `flower.inspector.Inspector.inspect` · *method*

## Summary:
Initiates asynchronous inspection of worker statistics across registered workers.

## Description:
This method triggers concurrent inspection operations for all registered inspection methods (stats, active_queues, registered, scheduled, active, reserved, revoked, conf) on the specified worker(s). It leverages the I/O loop executor to run these operations concurrently, improving performance when inspecting multiple workers simultaneously.

The inspect method is designed as a separate method because it orchestrates the parallel execution of multiple inspection tasks, which would be less efficient if inlined. It provides a clean interface for initiating bulk inspection operations while maintaining proper async execution patterns.

## Args:
    workername (str, optional): Specific worker name to inspect. If None, inspects all registered workers. Defaults to None.

## Returns:
    list: A list of concurrent futures representing the ongoing inspection operations for each method.

## Raises:
    None explicitly raised, though underlying I/O operations may raise exceptions.

## State Changes:
    Attributes READ: self.methods, self.io_loop, self.capp, self.timeout
    Attributes WRITTEN: self.workers (via _on_update callback)

## Constraints:
    Preconditions: 
    - Inspector instance must be properly initialized with io_loop, capp, and timeout
    - self.methods must contain valid inspection method names
    - Worker names in workername parameter must exist if specified
    
    Postconditions:
    - Returns immediately with a list of futures without blocking
    - Inspection results will be processed asynchronously via callbacks
    - self.workers dictionary will be updated with inspection results over time

## Side Effects:
    - Initiates I/O operations through the I/O loop executor
    - Makes remote procedure calls to worker processes via capp.control.inspect
    - Updates internal self.workers dictionary asynchronously through callbacks
    - Logs debug and warning messages during execution

### `flower.inspector.Inspector._on_update` · *method*

## Summary:
Updates worker information with inspection results and timestamps the update.

## Description:
This method is called asynchronously when worker inspection responses are received. It stores the response from a specific inspection method for a worker and records the timestamp of when the update occurred. The method is part of the Inspector class's worker state management system.

Known callers:
- Called from `_inspect` method via `self.io_loop.add_callback(partial(self._on_update, worker, method, response))` during the worker inspection process
- Invoked during the async inspection pipeline when responses from Celery workers are processed

This method exists as a separate handler to decouple the response processing logic from the inspection execution logic, allowing for clean asynchronous handling of worker responses.

## Args:
    workername (str): Name identifier for the worker being updated
    method (str): Name of the inspection method that produced the response
    response (any): The response data from the worker inspection

## Returns:
    None: This method does not return a value

## Raises:
    KeyError: If workername does not exist in self.workers (though defaultdict handles this gracefully by creating an empty dict)

## State Changes:
    Attributes READ: self.workers
    Attributes WRITTEN: self.workers[workername][method], self.workers[workername]['timestamp']

## Constraints:
    Preconditions: 
    - workername must be a valid string identifier
    - method must be a valid inspection method name (from Inspector.methods tuple)
    - response can be any serializable data type
    - self.workers must be initialized as a collections.defaultdict(dict)

    Postconditions:
    - Worker information dictionary for workername contains the response under the method key
    - Worker information dictionary for workername has timestamp updated to current time

## Side Effects:
    None: This method performs only in-memory updates to the workers data structure

### `flower.inspector.Inspector._inspect` · *method*

*No documentation generated.*

