# `control.py`

## `flower.api.control.ControlHandler` · *class*

## Summary:
ControlHandler is an API endpoint handler that provides utility methods for worker validation and error reason extraction in the Flower monitoring interface.

## Description:
This class extends BaseApiHandler to provide specialized functionality for controlling and monitoring Celery workers within the Flower application. It offers methods to validate worker names against the application's registered workers and to extract meaningful error messages from API responses. The class is designed to be used as part of the Flower web API for managing worker-related operations.

The ControlHandler is typically instantiated automatically by the Tornado web framework when processing API requests, similar to other API handlers in the system.

## State:
- Inherits all state from BaseApiHandler including request context and application reference
- `self.application.workers`: A collection (likely a dictionary or set) containing registered worker names that the application tracks
- No additional instance attributes beyond those inherited from BaseHandler

## Lifecycle:
- Creation: Instantiated automatically by Tornado web framework when matching control API routes
- Usage: Framework calls appropriate HTTP method handlers (get, post, etc.) which may invoke is_worker() and error_reason() methods
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[is_worker] --> B[Check workername truthiness]
    B --> C{workername in workers?}
    C -->|Yes| D[Return True]
    C -->|No| E[Return False]
    
    F[error_reason] --> G[Iterate response items]
    G --> H{res[workername] exists?}
    H -->|Yes| I[Return error field or 'Unknown reason']
    H -->|No| J[Continue iteration]
    J --> K{All iterations complete?}
    K -->|Yes| L[Log error and return 'Unknown reason']
```

## Raises:
- No explicit exceptions raised by the ControlHandler constructor
- The error_reason method may log errors via logger.error() but doesn't raise exceptions itself

## Example:
```python
# Typical usage within a Flower API endpoint
class WorkerControlHandler(ControlHandler):
    def get(self, workername):
        if self.is_worker(workername):
            # Proceed with worker-specific operations
            pass
        else:
            self.set_status(404)
            self.write({"error": "Worker not found"})
            
    def post(self, workername):
        response = self.get_json_body()
        error_msg = self.error_reason(workername, response)
        self.write({"worker": workername, "error": error_msg})
```

### `flower.api.control.ControlHandler.is_worker` · *method*

## Summary:
Checks whether a given worker name exists in the application's registered workers collection.

## Description:
This method performs a validation check to determine if a specified worker name is currently registered with the application. It serves as a utility for verifying worker identity before performing operations that require valid worker references.

The method is designed to be used in API request handlers where worker validation is required. It provides a clean abstraction for worker existence checks while maintaining consistency with the application's worker management system.

## Args:
    self: Instance of ControlHandler class
    workername (str): The name of the worker to validate. May be None, empty string, or a valid worker identifier.

## Returns:
    bool: True if workername is not None/empty and exists in self.application.workers, False otherwise.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: 
    - self.application.workers: Collection containing registered worker names
    - self.application: Application instance reference

## Constraints:
    Preconditions:
    - self.application must be initialized and have a workers attribute
    - self.application.workers must support the 'in' operator for membership testing
    
    Postconditions:
    - Returns boolean value indicating worker registration status
    - Does not modify any object state

## Side Effects:
    None: This method performs only local computations and does not cause any I/O operations or external service calls.

### `flower.api.control.ControlHandler.error_reason` · *method*

## Summary:
Extracts error reason from response data for a specific worker, returning a default value when not found.

## Description:
Processes a list of response dictionaries to find error information associated with a specific worker. This method is used to retrieve detailed error messages from distributed worker responses in a Flower monitoring system. The method attempts to navigate nested dictionary structures to locate error information, falling back to a default 'Unknown reason' when the expected data structure is not found.

## Args:
    workername (str): Name identifier of the worker whose error information is being extracted
    response (list): List of response dictionaries containing worker status information

## Returns:
    str: Error reason string if found, otherwise 'Unknown reason'

## Raises:
    None explicitly raised - handles KeyError internally

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - workername parameter must be a string
        - response parameter must be iterable (list-like)
        - Each item in response should be a dictionary that can be indexed by workername
    Postconditions:
        - Always returns a string value
        - Returns 'Unknown reason' when no error information is found

## Side Effects:
    I/O: Writes error log message to logger when unable to extract error reason

## `flower.api.control.WorkerShutDown` · *class*

## Summary:
WorkerShutDown is an API endpoint handler that manages the shutdown process for specific Celery workers in the Flower monitoring system.

## Description:
This class implements a POST endpoint for shutting down Celery workers by broadcasting shutdown commands to targeted worker instances. It extends ControlHandler to inherit worker validation capabilities and integrates with the Flower web API framework. The handler is typically invoked through HTTP POST requests to worker control endpoints, allowing administrators to terminate specific worker processes remotely.

The class exists as a distinct abstraction to encapsulate the shutdown workflow, providing a clean interface for worker termination while maintaining consistency with other control operations in the Flower monitoring system. It ensures proper authentication through the @web.authenticated decorator and validates worker existence before attempting shutdown operations.

## State:
- Inherits all state from ControlHandler including application context and worker validation utilities
- `self.capp`: Reference to the Celery application instance used for broadcasting control commands  
- `logger`: Logging instance for recording shutdown operations (typically configured at module or application level)
- Inherits `self.application.workers` from ControlHandler for worker validation

## Lifecycle:
- Creation: Automatically instantiated by Tornado web framework when matching control API routes
- Usage: Framework invokes post() method when receiving HTTP POST requests to worker shutdown endpoints
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Validate workername with is_worker()]
    B --> C{Worker exists?}
    C -->|No| D[Raise HTTPError 404]
    C -->|Yes| E[Log shutdown operation]
    E --> F[Broadcast shutdown command]
    F --> G[Write response message]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the specified workername is not found in the application's registered workers collection

## Example:
```python
# In Flower web UI or API client:
# POST /api/shutdown/my_worker_name
# Response: {"message": "Shutting down!"}

# This endpoint allows administrators to:
# 1. Validate worker existence before shutdown
# 2. Log the shutdown operation for audit purposes
# 3. Broadcast shutdown command to the specific worker
# 4. Return confirmation to the requester

# The handler ensures:
# - Only authenticated users can access this endpoint
# - Worker name is validated against registered workers
# - Shutdown command is properly broadcast via Celery control interface
```

### `flower.api.control.WorkerShutDown.post` · *method*

## Summary:
Shuts down a specified worker by broadcasting a shutdown command to the worker instance.

## Description:
This method handles POST requests to shut down a specific worker identified by its name. It validates the worker exists, logs the shutdown operation, broadcasts a shutdown command to the worker, and returns a confirmation message. This method is part of the worker control API endpoints in the Flower monitoring interface.

The method is called during the HTTP POST phase of a worker shutdown request, typically initiated by users through the Flower web UI or API clients. It serves as a dedicated endpoint for worker termination operations.

## Args:
    self: Instance of WorkerShutDown class
    workername (str): The unique identifier/name of the worker to shut down

## Returns:
    None: This method does not return a value directly, but writes a JSON response via self.write()

## Raises:
    tornado.web.HTTPError(404): Raised when the specified workername is not found in the application's registered workers collection

## State Changes:
    Attributes READ:
    - self.application.workers: Used to validate worker existence via is_worker() method
    - self.capp: Used to access the Celery application control interface
    - self: Access to the request handler's built-in methods and properties
    
    Attributes WRITTEN:
    - Response body written via self.write() method

## Constraints:
    Preconditions:
    - The workername parameter must be a non-empty string
    - The worker identified by workername must be registered with the application
    - The application must have a valid Celery app instance available as self.capp
    
    Postconditions:
    - A shutdown command is broadcast to the specified worker
    - An informational log entry is created
    - A JSON response confirming shutdown is sent to the client

## Side Effects:
    - Writes an informational log message to the application logger
    - Broadcasts a shutdown command to the specified worker via Celery control interface
    - Sends an HTTP response back to the client with shutdown confirmation

## `flower.api.control.WorkerPoolRestart` · *class*

## Summary:
WorkerPoolRestart is a Tornado web handler that manages POST requests to restart a specific worker's task pool in a Celery-based distributed system.

## Description:
This class implements an API endpoint for restarting worker pools within the Flower monitoring interface. It serves as a control mechanism that allows administrators to gracefully restart a worker's processing pool without stopping the entire worker process. The handler validates worker existence, sends a broadcast command to the specified worker using Celery's control interface, and provides appropriate response feedback based on the operation's success or failure.

The class is designed to be used as part of the Flower web API and inherits authentication and validation capabilities from its parent ControlHandler class. It specifically targets Celery workers within a distributed task queue system, leveraging Celery's broadcast functionality to issue pool restart commands.

## State:
- Inherits all state from ControlHandler including request context and application reference
- `self.capp`: Celery application instance (typically configured in the parent class) used to send broadcast commands to workers
- `logger`: Python logging instance for tracking restart operations and errors
- All attributes inherited from BaseApiHandler including request/response handling capabilities

## Lifecycle:
- Creation: Automatically instantiated by Tornado web framework when matching control API routes
- Usage: Framework invokes post() method when receiving POST requests to restart worker pools
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Validate worker exists]
    B --> C{is_worker(workername)?}
    C -->|No| D[Raise 404 HTTPError]
    C -->|Yes| E[Log restart attempt]
    E --> F[Send broadcast pool_restart command]
    F --> G{Response received?}
    G -->|No| H[Set 403 status, write error]
    G -->|Yes| I[Check for 'ok' in response]
    I -->|No| J[Set 403 status, write error]
    I -->|Yes| K[Write success message]
```

## Raises:
- web.HTTPError(404): Raised when the specified workername is not found in registered workers
- Various exceptions may be raised by underlying broadcast mechanisms (not explicitly handled)

## Example:
```python
# Typical usage via HTTP POST request
# POST /api/workers/pool/restart/my-worker-name

# Successful response:
# {"message": "Restarting 'my-worker-name' worker's pool"}

# Failed response (when worker doesn't exist):
# HTTP 404 Not Found

# Failed response (when restart fails):
# HTTP 403 Forbidden with error message
```

### `flower.api.control.WorkerPoolRestart.post` · *method*

## Summary:
Restarts the task pool of a specified worker process and returns status information about the operation.

## Description:
This method handles POST requests to restart a Celery worker's task pool. It validates that the specified worker exists, sends a broadcast command to restart the worker's pool, and provides appropriate HTTP responses based on the outcome. This method is typically called during cluster management operations when administrators need to refresh worker processes.

## Args:
    workername (str): The name/id of the worker whose task pool should be restarted

## Returns:
    None: This method writes directly to the HTTP response rather than returning a value

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when the specified worker does not exist
    tornado.web.HTTPError: Raised with status code 403 when the pool restart operation fails

## State Changes:
    Attributes READ: 
        - self.is_worker (method to validate worker existence)
        - self.capp (Celery app instance containing control interface)
        - self.error_reason (method to determine error cause)
    Attributes WRITTEN:
        - self.write (method to send HTTP response)
        - self.set_status (method to set HTTP status code)

## Constraints:
    Preconditions:
        - The worker identified by workername must exist in the cluster
        - The capp attribute must be properly initialized with a valid Celery app instance
        - The method must be called within a Tornado web request context
    Postconditions:
        - On successful restart: HTTP 200 status with success message
        - On failed restart: HTTP 403 status with error details

## Side Effects:
    - Makes a broadcast call to the Celery worker cluster via self.capp.control.broadcast()
    - Logs informational messages at INFO level when initiating restart
    - Logs error messages at ERROR level when restart fails
    - Communicates with external Celery worker processes to execute pool restart

## `flower.api.control.WorkerPoolGrow` · *class*

## Summary:
WorkerPoolGrow is an API endpoint handler that allows growing a Celery worker's process pool by a specified number of processes.

## Description:
This class implements a POST endpoint for the Flower monitoring interface that enables administrators to dynamically increase the number of worker processes for a specific Celery worker. It extends ControlHandler to inherit worker validation and error handling capabilities. The endpoint accepts a worker name and an optional parameter 'n' (defaulting to 1) specifying how many additional processes to add to the worker's pool.

The handler performs authentication via the @web.authenticated decorator, validates the worker exists, and then delegates to Celery's control interface to execute the pool growth operation. It provides appropriate HTTP responses indicating success or failure of the operation.

## State:
- Inherits all state from ControlHandler including worker validation capabilities
- `self.capp`: Reference to the Celery application instance containing the control interface
- `logger`: Module-level logger instance for tracking operations and errors
- No additional instance attributes beyond those inherited from BaseApiHandler

## Lifecycle:
- Creation: Automatically instantiated by Tornado web framework when matching the control API route
- Usage: Framework invokes post() method when a POST request is made to the endpoint with a worker name
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Authenticate via @web.authenticated]
    B --> C[Validate worker exists using is_worker()]
    C --> D{Worker valid?}
    D -->|No| E[Raise 404 HTTPError]
    D -->|Yes| F[Get 'n' argument with default 1]
    F --> G[Log info about pool growth operation]
    G --> H[Call capp.control.pool_grow()]
    H --> I{Response received?}
    I -->|No| J[Set 403 status, log error, write failure message]
    I -->|Yes| K{Success indicator in response?}
    K -->|No| J
    K -->|Yes| L[Write success message]
```

## Raises:
- web.HTTPError(404): Raised when the specified worker name is not found in the registered workers
- web.HTTPError(403): Raised when the pool growth operation fails, with detailed error information in the response

## Example:
```python
# Example API call to grow worker pool
# POST /api/worker/pool/grow/my-worker?n=2
# Response on success:
# {"message": "Growing 'my-worker' worker's pool by 2"}

# Response on failure:
# Status 403 with body: "Failed to grow 'my-worker' worker's pool: <reason>"
```

### `flower.api.control.WorkerPoolGrow.post` · *method*

## Summary:
Increases the worker pool size for a specified worker by a given number of processes.

## Description:
This method handles POST requests to grow the process pool of a specific Celery worker. It validates the worker exists, retrieves the requested growth amount (defaulting to 1), and communicates with the Celery application to expand the worker's pool size. The method provides detailed error handling and status reporting for successful and failed operations.

The method is part of the WorkerPoolGrow API endpoint and is typically invoked during runtime management of Celery workers through the Flower monitoring interface. It serves as a controlled mechanism for dynamically adjusting worker capacity.

## Args:
    self: Instance of WorkerPoolGrow class inheriting from ControlHandler
    workername (str): Identifier of the target worker whose pool size should be increased

## Returns:
    None: This method writes directly to the HTTP response rather than returning a value

## Raises:
    web.HTTPError: Raised with status code 404 when the specified workername is not found in the application's registered workers

## State Changes:
    Attributes READ:
    - self.application.workers: Used to validate worker existence via is_worker()
    - self.capp: Celery application instance for communicating with workers
    - self.request: HTTP request object for accessing arguments
    - logger: Logging instance for informational and error messages
    
    Attributes WRITTEN:
    - self.response: HTTP response object modified via write() and set_status()

## Constraints:
    Preconditions:
    - The worker identified by workername must be registered with the application
    - The capp attribute must be properly initialized with a valid Celery application instance
    - The application must have a workers collection that supports membership testing
    
    Postconditions:
    - If successful, the worker's process pool will be increased by the specified amount
    - If failed, appropriate HTTP status code (403) and error message will be returned
    - The HTTP response will contain either success confirmation or failure details

## Side Effects:
    - Makes synchronous call to Celery application's control interface via self.capp.control.pool_grow()
    - Writes to HTTP response stream via self.write() and self.set_status()
    - Logs informational messages at INFO level when processing requests
    - Logs error messages at ERROR level when operation fails

## `flower.api.control.WorkerPoolShrink` · *class*

## Summary:
WorkerPoolShrink is an API endpoint handler that reduces the size of a specified worker's process pool by a given number of processes.

## Description:
This class implements a POST endpoint for shrinking the worker pool of a Celery worker in the Flower monitoring system. It validates that the specified worker exists, retrieves the shrink count parameter, and communicates with the worker to reduce its process pool size. The handler provides appropriate HTTP responses based on the success or failure of the operation.

The class is designed to be used as part of the Flower web API for managing worker resource allocation. It leverages the ControlHandler base class for worker validation and error handling utilities.

## State:
- Inherits all state from ControlHandler including application context and worker validation capabilities
- `self.capp`: Reference to the Celery application instance that provides access to control commands
- `logger`: Logging instance for recording operational events and errors (typically configured via Python logging module)

## Lifecycle:
- Creation: Instantiated automatically by Tornado web framework when matching control API routes
- Usage: Framework calls post() method when a POST request is made to the worker pool shrink endpoint
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Validate worker exists]
    B --> C{is_worker(workername)?}
    C -->|No| D[Raise 404 HTTPError]
    C -->|Yes| E[Get 'n' argument]
    E --> F[Call pool_shrink control command]
    F --> G{Response contains 'ok'?}
    G -->|Yes| H[Write success message]
    G -->|No| I[Set 403 status]
    I --> J[Get error reason]
    J --> K[Write error message]
```

## Raises:
- web.HTTPError(404): Raised when the specified workername is not found in the application's registered workers
- web.HTTPError(403): Raised when the pool shrink operation fails, with error details provided in the response

## Example:
```python
# Typical usage would be via HTTP POST to endpoint like:
# POST /api/worker/pool/shrink/myworker?n=2

# This would shrink the 'myworker' worker's pool by 2 processes
# Success response: {"message": "Shrinking 'myworker' worker's pool by 2"}
# Failure response: {"error": "Failed to shrink 'myworker' worker's pool: [reason]"}
```

### `flower.api.control.WorkerPoolShrink.post` · *method*

## Summary:
Reduces the number of worker processes in a specified worker's pool by the requested amount.

## Description:
Handles HTTP POST requests to shrink the process pool of a Celery worker. Validates that the worker exists using `self.is_worker()`, retrieves the shrink count parameter 'n' (defaulting to 1), and communicates with the Celery control interface to reduce the worker's pool size. Provides appropriate HTTP responses based on the success or failure of the operation.

This method is part of the Flower monitoring interface for managing Celery workers. It's typically invoked during runtime operations when administrators need to dynamically adjust worker resource allocation.

## Args:
    self: Instance of WorkerPoolShrink class
    workername (str): Name identifier of the target worker whose process pool will be shrunk

## Returns:
    None: This method writes directly to the HTTP response rather than returning a value

## Raises:
    tornado.web.HTTPError: Raised with status 404 when the specified workername is not found in the application's registered workers

## State Changes:
    Attributes READ:
    - self.application.workers: Used to validate worker existence via `self.is_worker()`
    - self.capp: Celery application instance for control operations
    - self.logger: Logging instance for informational and error messages
    
    Attributes WRITTEN:
    - HTTP response state via `self.write()` and `self.set_status()`

## Constraints:
    Preconditions:
    - self.application must be initialized with a workers collection
    - self.capp must be initialized with a valid Celery control interface
    - workername must be a non-empty string
    - self.get_argument() must be available for parameter parsing
    
    Postconditions:
    - If successful, HTTP 200 status with JSON success message is returned
    - If unsuccessful, HTTP 403 status with error message is returned
    - No changes to persistent state occur

## Side Effects:
    - I/O: Writes HTTP response data via `self.write()` and `self.set_status()`
    - Logging: Writes info messages to logger when operation begins
    - Logging: Writes error messages to logger when operation fails

## `flower.api.control.WorkerPoolAutoscale` · *class*

## Summary:
WorkerPoolAutoscale is a Tornado web handler that manages autoscaling configuration for Celery workers in the Flower monitoring system.

## Description:
This class implements a POST endpoint for adjusting the minimum and maximum pool sizes of a specific Celery worker. It serves as part of the Flower web API for managing worker resources dynamically. The handler validates worker existence, processes autoscaling parameters, and communicates with the worker via Celery's broadcast mechanism to apply scaling changes.

The class is designed to be used as part of the Flower monitoring interface, where authorized users can adjust worker pool configurations in real-time. It inherits from ControlHandler, which provides worker validation and error handling utilities.

## State:
- Inherits all state from ControlHandler including application context and worker validation capabilities
- No additional instance attributes beyond those inherited from BaseHandler
- `self.capp`: Reference to the Celery application instance (available via parent class)
- `self.application`: Application context providing access to workers and configuration

## Lifecycle:
- Creation: Automatically instantiated by Tornado web framework when matching control API routes
- Usage: Framework calls post() method with workername parameter when a POST request is made to the autoscale endpoint
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Validate worker exists]
    B --> C{is_worker(workername)?}
    C -->|No| D[Raise HTTPError 404]
    C -->|Yes| E[Get min argument with type=int]
    E --> F[Get max argument with type=int]
    F --> G[Log autoscaling request]
    G --> H[broadcast autoscale command]
    H --> I{Response received?}
    I -->|No| J[Set status 403, write error]
    I -->|Yes| K[Check for 'ok' in response]
    K -->|No| J
    K -->|Yes| L[Write success message]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the specified workername is not found in the application's registered workers
- tornado.web.HTTPError(400): Raised by get_argument when min or max arguments cannot be converted to integers
- tornado.web.HTTPError(403): Raised when the autoscaling operation fails (response does not contain 'ok')

## Example:
```python
# Example usage in Flower API context:
# POST /api/worker/autoscale/my-worker?min=2&max=10
# Response on success:
# {"message": "Autoscaling 'my-worker' worker (min=2, max=10)"}

# Response on failure:
# HTTP 403 Forbidden with error message about failed autoscaling
```

### `flower.api.control.WorkerPoolAutoscale.post` · *method*

## Summary:
Handles POST requests to configure autoscaling parameters for a specific worker process.

## Description:
Processes autoscaling configuration requests for a Celery worker by validating the worker exists, extracting 'min' and 'max' integer parameters from the request, broadcasting the autoscale command to the worker, and returning appropriate success or error responses. This method is typically invoked during API calls to modify worker pool sizing dynamically.

## Args:
    workername (str): The identifier of the target worker process to configure autoscaling for

## Returns:
    None: This method writes directly to the HTTP response rather than returning a value

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when the specified workername is not recognized as a valid worker

## State Changes:
    Attributes READ:
        - self.application.workers: Used to validate worker existence via self.is_worker()
        - self.capp: Used to access the Celery app for broadcasting commands
        - self.request: Used to extract URL arguments via self.get_argument()
    
    Attributes WRITTEN:
        - self.response: Modified via self.write() and self.set_status() to send HTTP responses

## Constraints:
    Preconditions:
        - The worker identified by workername must be registered with the application
        - The request must contain 'min' and 'max' integer parameters
        - The worker must be able to process the autoscale command successfully
    
    Postconditions:
        - If successful, the worker's autoscaling configuration is updated and a success message is returned
        - If failed, appropriate HTTP status code (403) and error message are returned

## Side Effects:
    - Makes a broadcast call to the Celery worker via self.capp.control.broadcast()
    - Logs informational messages at INFO level when autoscaling is initiated
    - Logs error messages at ERROR level when autoscaling fails
    - Sends HTTP response back to client with either success or failure details

## `flower.api.control.WorkerQueueAddConsumer` · *class*

## Summary:
WorkerQueueAddConsumer is a Tornado web handler that adds a queue consumer to a specified Celery worker through the Flower monitoring interface.

## Description:
This class implements a POST endpoint for adding queue consumers to Celery workers. It serves as part of the Flower web API for managing worker queue consumption. The handler authenticates requests, validates worker existence, and communicates with the Celery worker control interface to add the specified queue consumer.

The handler is designed to be used within the Flower monitoring system to provide programmatic access to worker queue management capabilities. It follows standard Tornado web handler patterns and integrates with the Celery control protocol to manage worker queue subscriptions.

## State:
- Inherits all state from ControlHandler including application context and worker validation utilities
- `self.capp`: Reference to the Celery application instance containing the control interface for worker communication
- `logger`: Logging instance for tracking operations and errors
- `self.application`: Inherited from BaseApiHandler, provides access to application configuration and registered workers

## Lifecycle:
- Creation: Automatically instantiated by Tornado web framework when matching control API routes
- Usage: Framework invokes post() method when a POST request is made to the endpoint with workername parameter
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post(workername)] --> B{is_worker(workername)?}
    B -->|No| C[raise HTTPError 404]
    B -->|Yes| D[get_argument('queue')]
    D --> E[capp.control.broadcast(add_consumer, queue, destination=[workername])]
    E --> F{response contains 'ok'?}
    F -->|Yes| G[write success message]
    F -->|No| H[set_status 403]
    H --> I[error_reason(workername, response)]
    I --> J[write error message]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the specified workername is not found in application workers
- tornado.web.HTTPError(403): Raised when the operation fails to add the consumer, with detailed error information in response

## Example:
```python
# Typical usage scenario:
# POST /api/worker/queue/add/my-worker?queue=my_queue_name

# Success response:
# HTTP 200 OK
# {"message": "Consumer added successfully"}

# Failure response:
# HTTP 403 Forbidden  
# "Failed to add 'my_queue_name' consumer to 'my-worker' worker: Unknown reason"

# Invalid worker response:
# HTTP 404 Not Found
# "Unknown worker 'nonexistent-worker'"
```

### `flower.api.control.WorkerQueueAddConsumer.post` · *method*

## Summary:
Adds a queue consumer to a specified worker process.

## Description:
This method handles HTTP POST requests to add a queue consumer to a Celery worker. It validates the worker exists, retrieves the queue argument from the request, and broadcasts an 'add_consumer' command to the specified worker. The method provides detailed error reporting if the operation fails.

## Args:
    workername (str): The name of the worker to add the queue consumer to.

## Returns:
    None: This method writes directly to the HTTP response rather than returning a value.

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when the specified worker does not exist.

## State Changes:
    Attributes READ: 
    - self.is_worker: Used to validate worker existence
    - self.get_argument: Used to retrieve the 'queue' argument from request
    - self.capp: Used to access the Celery app control interface
    - self.error_reason: Used to generate error messages
    
    Attributes WRITTEN:
    - self.write: Used to send response data back to client
    - self.set_status: Used to set HTTP status code

## Constraints:
    Preconditions:
    - The worker identified by workername must exist (validated via self.is_worker)
    - The request must contain a 'queue' argument
    - The capp attribute must be properly initialized with a Celery app instance
    
    Postconditions:
    - If successful, the worker will have the specified queue added as a consumer
    - If failed, appropriate HTTP status code (403) and error message will be returned

## Side Effects:
    - Makes a broadcast call to the Celery worker via self.capp.control.broadcast
    - Writes HTTP response data to the client
    - Logs informational and error messages using the logger

## `flower.api.control.WorkerQueueCancelConsumer` · *class*

## Summary:
WorkerQueueCancelConsumer is a Tornado web handler that cancels a consumer queue from a specific Celery worker in the Flower monitoring interface.

## Description:
This class implements a POST endpoint for canceling consumer queues on individual Celery workers. It serves as part of the Flower web API for managing worker consumer operations. The handler validates worker existence, processes cancellation requests, and returns appropriate success or error responses based on the outcome of the cancellation operation.

The handler is typically invoked by the Tornado web framework when processing API requests to the control endpoint for worker queue cancellation, and requires proper authentication to be accessed.

## State:
- Inherits all state from ControlHandler including request context and application reference
- `self.capp`: Celery application instance (assumed to be available via parent class/application context)
- No additional instance attributes beyond those inherited from ControlHandler

## Lifecycle:
- Creation: Instantiated automatically by Tornado web framework when matching control API routes
- Usage: Framework calls post() method with workername parameter when a POST request is made to the endpoint
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post(workername)] --> B{is_worker(workername)?}
    B -->|No| C[raise HTTPError 404]
    B -->|Yes| D[get_argument('queue')]
    D --> E[logger.info()]
    E --> F[capp.control.broadcast('cancel_consumer')]
    F --> G{response received?}
    G -->|No| H[set_status(403)]
    H --> I[write error message]
    G -->|Yes| J{'ok' in response?}
    J -->|Yes| K[write success message]
    J -->|No| L[set_status(403)]
    L --> M[write error message]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the specified workername is not found in the application's registered workers
- tornado.web.HTTPError(403): Raised when the cancellation operation fails, typically due to permission issues or worker communication problems

## Example:
```python
# Example API usage:
# POST /api/worker/queue/cancel/my-worker?queue=my_queue_name

# Successful response:
# HTTP 200 OK
# {"message": "Consumer 'my_queue_name' canceled successfully"}

# Error response for unknown worker:
# HTTP 404 Not Found
# "Unknown worker 'my-worker'"

# Error response for failed cancellation:
# HTTP 403 Forbidden
# "Failed to cancel 'my_queue_name' consumer from 'my-worker' worker: [reason]"
```

### `flower.api.control.WorkerQueueCancelConsumer.post` · *method*

## Summary:
Cancels a consumer queue from a specified worker by broadcasting a cancellation command.

## Description:
Handles POST requests to cancel a consumer queue from a specific worker. Validates the worker exists, retrieves the queue name from request arguments, and broadcasts a cancel_consumer command to the worker. Returns appropriate success or error responses based on the command execution result.

## Args:
    workername (str): The name of the worker from which to cancel the consumer queue.

## Returns:
    None: This method writes directly to the HTTP response rather than returning a value.

## Raises:
    web.HTTPError: Raised with status code 404 when the specified worker does not exist.

## State Changes:
    Attributes READ: 
        - self.is_worker: Used to validate worker existence
        - self.get_argument: Used to retrieve queue argument from request
        - self.capp: Used to access control broadcast functionality
        - logger: Used for logging messages
        - self.error_reason: Used to generate error messages
    
    Attributes WRITTEN:
        - self.write: Used to write HTTP response content
        - self.set_status: Used to set HTTP status code

## Constraints:
    Preconditions:
        - The workername parameter must correspond to an existing worker in the system
        - The request must contain a 'queue' argument
        - The capp attribute must be properly initialized with control capabilities
    
    Postconditions:
        - If successful, the consumer queue is canceled on the specified worker
        - If failed, appropriate HTTP status code (403) and error message are returned

## Side Effects:
    - Makes a broadcast call to the specified worker to cancel a consumer
    - Writes HTTP response content to the client
    - Logs informational and error messages to the application logger
    - May trigger external service calls through the Celery control interface

## `flower.api.control.TaskRevoke` · *class*

## Summary:
TaskRevoke is a web API endpoint that handles POST requests to revoke Celery tasks by their ID.

## Description:
This class implements a RESTful API endpoint for revoking Celery tasks. It extends ControlHandler to inherit authentication and worker validation capabilities. The endpoint accepts a task ID as a URL parameter and optional query parameters to control how the task revocation is performed, specifically whether to terminate the process and what signal to send.

The TaskRevoke handler is typically invoked by the Tornado web framework when a client makes a POST request to the appropriate API endpoint, such as `/api/task/revoke/{taskid}`.

## State:
- Inherits all state from ControlHandler including request context and application reference
- `self.capp`: Reference to the Celery application instance containing the control interface
- No additional instance attributes beyond those inherited from the parent class

## Lifecycle:
- Creation: Instantiated automatically by Tornado web framework when matching API routes
- Usage: Framework calls the post() method when a POST request is made to the task revoke endpoint
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Authenticate request]
    B --> C[Extract taskid from URL]
    C --> D[Get terminate argument (default False)]
    D --> E[Get signal argument (default SIGTERM)]
    E --> F[Call self.capp.control.revoke(taskid, terminate=terminate, signal=signal)]
    F --> G[Write success response]
```

## Raises:
- Inherits authentication-related exceptions from @web.authenticated decorator
- May raise HTTP 404 if the task ID is not found (handled by underlying Celery implementation)
- May raise HTTP 400 if arguments are malformed (handled by Tornado's get_argument)

## Example:
```python
# Client request:
# POST /api/task/revoke/abc123?terminate=True&signal=SIGKILL

# Server response:
# {"message": "Revoked 'abc123'"}

# Usage in a web application context:
# This handler would be mapped to a route like:
# app.add_handlers(r".*", [(r"/api/task/revoke/([^/]+)", TaskRevoke)])

# The revoke operation uses Celery's control.revoke API which:
# - Cancels the task if it hasn't started yet
# - Sends a signal to the worker process if it's running
# - Has optional terminate parameter to force kill the process
# - Uses SIGTERM by default but allows custom signals
```

### `flower.api.control.TaskRevoke.post` · *method*

## Summary:
Revokes a task by sending a termination signal to the Celery worker.

## Description:
This method handles POST requests to revoke a running task identified by its task ID. It accepts optional parameters to control the revocation behavior, including whether to forcefully terminate the process and which signal to send.

## Args:
    taskid (str): The unique identifier of the task to be revoked.

## Returns:
    None: This method does not return a value directly, but writes a JSON response to the HTTP client.

## Raises:
    None explicitly raised: The method doesn't contain try/except blocks, but underlying operations may raise exceptions from the Celery control interface.

## State Changes:
    Attributes READ: 
        - self.capp: The Celery application instance containing the control interface
        - self.request: The Tornado HTTP request object (inherited from web.RequestHandler)
    Attributes WRITTEN:
        - self.write: Writes the response to the HTTP client

## Constraints:
    Preconditions:
        - The task with the specified taskid must exist in the Celery task queue
        - The Celery worker must be running and accessible
        - The caller must have permission to revoke tasks
    Postconditions:
        - The task revocation command is sent to the Celery worker
        - A success message is returned to the client

## Side Effects:
    - Makes a call to the Celery control interface to revoke a task
    - Writes a JSON response to the HTTP client
    - Logs the revocation event at INFO level

## `flower.api.control.TaskTimout` · *class*

## Summary:
TaskTimout is an API endpoint handler that sets timeout configurations for Celery tasks through the Flower monitoring interface.

## Description:
This class implements a POST endpoint that allows administrators to configure hard and soft timeout settings for specific Celery tasks. It serves as part of the Flower web interface for monitoring and controlling Celery workers. The handler validates that the specified task and worker (if provided) exist before attempting to set timeout configurations via the underlying Celery application's control interface.

The class enforces authentication through its parent BaseApiHandler and performs validation through its parent ControlHandler's utility methods. It is designed to be invoked automatically by the Tornado web framework when processing control API requests.

## State:
- Inherits all state from BaseApiHandler and ControlHandler including request context and application reference
- `self.capp`: Celery application instance providing access to control interfaces
- No additional instance attributes beyond those inherited from parent classes

## Lifecycle:
- Creation: Automatically instantiated by Tornado web framework when matching control API routes
- Usage: Framework invokes post() method with taskname parameter when a POST request is made to the endpoint
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Get workername argument]
    B --> C[Get hard timeout argument]
    C --> D[Get soft timeout argument]
    D --> E{taskname in capp.tasks?}
    E -->|No| F[Raise HTTPError 404]
    E -->|Yes| G{workername provided?}
    G -->|No| H[Set destination=None]
    G -->|Yes| I{is_worker(workername)?}
    I -->|No| J[Raise HTTPError 404]
    I -->|Yes| H
    H --> K[Call capp.control.time_limit]
    K --> L{Response contains 'ok'?}
    L -->|Yes| M[Write success message]
    L -->|No| N[Set status 403]
    N --> O[Get error reason]
    O --> P[Write failure message]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the specified taskname is not found in self.capp.tasks
- tornado.web.HTTPError(404): Raised when a workername is provided but the worker is not found via self.is_worker()
- tornado.web.HTTPError(403): Raised when the timeout setting operation fails and cannot be completed successfully

## Example:
```python
# Example API call to set timeouts for a task
# POST /api/task-timeout/my_task?workername=my_worker&hard=30.0&soft=15.0

# Successful response:
# {"message": "Timeout set for task 'my_task'"}

# Error response for unknown task:
# HTTP 404 Not Found: "Unknown task 'unknown_task'"

# Error response for invalid worker:
# HTTP 404 Not Found: "Unknown worker 'invalid_worker'"
```

### `flower.api.control.TaskTimout.post` · *method*

## Summary:
Sets timeout limits for a specified Celery task, optionally targeting a specific worker.

## Description:
This method handles HTTP POST requests to configure timeout settings for Celery tasks. It validates the existence of the specified task and optional worker, then communicates with the Celery control interface to set the timeout limits. The method supports both hard and soft timeout configurations.

## Args:
    taskname (str): Name of the Celery task to configure timeouts for
    workername (str, optional): Specific worker to target. If None, applies to all workers
    hard (float, optional): Hard timeout limit in seconds. If None, uses default value
    soft (float, optional): Soft timeout limit in seconds. If None, uses default value

## Returns:
    None: Response is written directly to the HTTP response via self.write()

## Raises:
    web.HTTPError: Raised with status 404 when the specified task or worker doesn't exist
    web.HTTPError: Raised with status 403 when timeout configuration fails

## State Changes:
    Attributes READ: 
        - self.capp.tasks: Used to validate task existence
        - self.capp.control: Used to call time_limit method
        - self.is_worker: Used to validate worker existence
        - self.error_reason: Used to generate error messages
        - self.get_argument: Used to extract request parameters
    Attributes WRITTEN:
        - self.write(): Writes HTTP response content
        - self.set_status(): Sets HTTP status code

## Constraints:
    Preconditions:
        - taskname must be a valid key in self.capp.tasks
        - workername (if provided) must be a valid worker as determined by self.is_worker()
        - self.capp must have a control interface supporting time_limit method
    Postconditions:
        - HTTP response is written with either success message or error details
        - HTTP status is set appropriately (200 for success, 403 for failure)

## Side Effects:
    - Makes synchronous call to Celery control interface via self.capp.control.time_limit()
    - Logs informational message about timeout setting operation using logger.info
    - Logs error message if timeout configuration fails using logger.error
    - Writes HTTP response directly to client

## `flower.api.control.TaskRateLimit` · *class*

## Summary:
TaskRateLimit is a Tornado web handler that manages rate limiting for Celery tasks by setting rate limits on specific tasks or workers through the Flower monitoring interface.

## Description:
This class implements a POST endpoint for configuring rate limits on Celery tasks. It validates that the requested task and worker (if specified) exist, then communicates with the Celery application to apply the specified rate limit. The handler requires authentication and provides appropriate HTTP responses based on success or failure of the rate limit operation.

The class is typically invoked automatically by the Tornado web framework when processing API requests to the control endpoint for task rate limiting, and is part of the Flower monitoring interface for managing Celery workers and tasks.

## State:
- Inherits all state from ControlHandler including request context, application reference, and worker validation capabilities
- `self.capp`: Property that returns the Celery application object from the Tornado application instance
- No additional instance attributes beyond those inherited from BaseHandler and ControlHandler

## Lifecycle:
- Creation: Instantiated automatically by Tornado web framework when matching control API routes
- Usage: Framework calls post() method with taskname parameter when a POST request is made to the rate limit endpoint
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[post] --> B[Get workername argument]
    B --> C[Get ratelimit argument]
    C --> D[Validate task exists in self.capp.tasks]
    D --> E{Task exists?}
    E -->|No| F[Raise HTTPError 404]
    E -->|Yes| G[Validate worker if specified]
    G --> H{Worker specified and valid?}
    H -->|No| I[Raise HTTPError 404]
    H -->|Yes| J[Set log info]
    J --> K[Call self.capp.control.rate_limit()]
    K --> L{Response received?}
    L -->|No| M[Set 403 status and write error]
    L -->|Yes| N[Check for 'ok' in response]
    N -->|No| O[Set 403 status and write error]
    N -->|Yes| P[Write success message]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the specified taskname is not found in self.capp.tasks
- tornado.web.HTTPError(404): Raised when a workername is specified but the worker is not found in the application's registered workers
- tornado.web.HTTPError(403): Raised when the rate limit operation fails and cannot be completed successfully

## Example:
```python
# Example usage via HTTP request:
# POST /api/task/rate-limit/my_task?workername=my_worker&ratelimit=10/s
# Response on success:
# {"message": "Rate limit set to 10/s for my_task"}
#
# Response on failure:
# HTTP 403 Forbidden with error message like:
# "Failed to set rate limit: 'Unknown reason'"
```

### `flower.api.control.TaskRateLimit.post` · *method*

## Summary:
Sets the rate limit for a specified Celery task, optionally targeting a specific worker.

## Description:
This method handles POST requests to configure rate limits for Celery tasks within the Flower monitoring interface. It validates that the requested task exists and, if a worker is specified, that the worker is registered with the application. The method then communicates with the Celery control plane to apply the rate limit configuration and returns appropriate success or error responses.

The method is typically invoked during API requests to modify task execution rates in real-time, allowing administrators to control workload distribution and resource utilization.

## Args:
    taskname (str): The name of the Celery task to configure rate limiting for

## Returns:
    None: This method writes directly to the HTTP response rather than returning a value

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when:
        - The specified taskname is not found in self.capp.tasks
        - The specified workername (if provided) is not recognized as a registered worker
    tornado.web.HTTPError: Raised with status code 403 when the rate limit operation fails

## State Changes:
    Attributes READ:
        - self.capp: The Celery application instance containing task definitions
        - self.application.workers: Collection of registered worker names for validation
    Attributes WRITTEN:
        - self: The HTTP response is modified via self.write() and self.set_status()

## Constraints:
    Preconditions:
        - The task identified by taskname must exist in self.capp.tasks
        - If workername is provided, it must be a registered worker in self.application.workers
        - The ratelimit argument must be a valid rate limit string acceptable to Celery
    Postconditions:
        - If successful, the rate limit is applied to the specified task (or all tasks if no worker specified)
        - If unsuccessful, appropriate HTTP status codes and error messages are returned

## Side Effects:
    - Makes a remote procedure call to the Celery control plane via self.capp.control.rate_limit()
    - Writes HTTP response data using self.write() and self.set_status()
    - Logs informational messages at INFO level when setting rate limits
    - Logs error messages at ERROR level when rate limit operations fail

