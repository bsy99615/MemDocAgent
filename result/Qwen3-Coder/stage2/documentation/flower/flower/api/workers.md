# `workers.py`

## `flower.api.workers.ListWorkers` · *class*

## Summary:
ListWorkers is an asynchronous HTTP API endpoint handler that provides worker information and management capabilities in the Flower monitoring interface.

## Description:
The ListWorkers class implements a RESTful API endpoint for retrieving information about Celery workers in a distributed task queue system. It serves as part of the Flower web interface that monitors and manages Celery workers. The endpoint supports various query parameters to control what information is returned and how it's updated.

This class is designed to be instantiated automatically by the Tornado web framework when handling API requests to the workers endpoint. It provides a centralized way to query worker status, refresh worker data, and retrieve worker configurations through HTTP GET requests.

## State:
- Inherits all state from ControlHandler including request handling capabilities
- `self.application.workers` - Dictionary mapping worker names to worker information objects
- `self.application.events.state.workers` - Dictionary mapping worker names to worker state objects with alive status
- `logger` - Logger instance for error logging (inherited from parent class)

## Lifecycle:
- Creation: Automatically instantiated by Tornado web framework when handling API requests to the workers endpoint
- Usage: The get() method is invoked when an HTTP GET request is made to the workers endpoint with appropriate query parameters
- Destruction: Managed automatically by Tornado framework's request lifecycle

## Method Map:
```mermaid
graph TD
    A[GET Request] --> B[ListWorkers Instance Created]
    B --> C{refresh=True?}
    C -->|Yes| D[update_workers()]
    D --> E{Exception?}
    E -->|Yes| F[HTTPError 503]
    E -->|No| G[Continue]
    C -->|No| G
    G --> H{status=True?}
    H -->|Yes| I[Return worker status dict]
    H -->|No| J[Check worker existence]
    J --> K{workername specified?}
    K -->|Yes| L[Check if worker exists]
    L --> M{Worker exists?}
    M -->|No| N[HTTPError 404]
    M -->|Yes| O[Return worker info]
    K -->|No| P[Return all workers]
```

## Raises:
- web.HTTPError(503) - Raised when worker refresh operation fails due to an exception during update_workers()
- web.HTTPError(404) - Raised when a specific workername is requested but doesn't exist in the worker registry

## Example:
```python
# Typical usage scenario:
# GET /api/workers?refresh=true&workername=worker1
# Returns refreshed information for worker1

# GET /api/workers?status=true
# Returns dictionary with worker names as keys and alive status as values

# GET /api/workers?workername=worker1
# Returns information for specific worker worker1

# GET /api/workers
# Returns information for all registered workers
```

### `flower.api.workers.ListWorkers.get` · *method*

## Summary:
Retrieves and returns worker information with support for refreshing worker states and querying specific worker details.

## Description:
Handles HTTP GET requests to retrieve worker information from the Flower monitoring interface. This method supports multiple query parameters to control how worker data is retrieved and returned. It can refresh worker states from the Celery broker, return worker status information, or fetch specific worker details based on the provided parameters.

The method follows a specific execution flow:
1. Processes refresh parameter to update worker information from the broker
2. Handles status queries to return alive status of all workers
3. Returns specific worker information when workername is provided
4. Validates worker names and raises appropriate HTTP errors for invalid workers

This logic is encapsulated in its own method because it implements complex conditional logic for handling different query scenarios while maintaining proper error handling and worker validation.

## Args:
    None - Uses Tornado's built-in request handling via self.get_argument()

## Returns:
    None - Writes directly to the HTTP response via self.write()

## Raises:
    tornado.web.HTTPError: 
        - 404 when requesting a non-existent worker (workername not found in registry)
        - 503 when worker refresh operation fails due to connection issues

## State Changes:
    Attributes READ: 
        - self.application.workers - Current worker registry
        - self.application.events.state.workers - Event-based worker state information
        - self.application.update_workers - Method to refresh worker data
        - self.is_worker - Method to validate worker names
        - self.get_argument - Tornado method to parse query arguments
    
    Attributes WRITTEN: 
        - None - This method only reads from and writes to the HTTP response

## Constraints:
    Preconditions:
        - self.application must have a valid workers registry
        - self.application must have a valid events system with state tracking
        - self.application must have a valid update_workers method
        - self must inherit from ControlHandler to have is_worker method
        
    Postconditions:
        - When refresh=True, worker information is updated from the broker
        - When status=True, returns JSON mapping worker names to alive status
        - When workername is provided, returns specific worker information
        - When no parameters are provided, returns complete worker registry

## Side Effects:
    - Asynchronous I/O operations when refresh=True (calls self.application.update_workers)
    - Network calls to Celery broker when updating worker information
    - Logging of errors when refresh operations fail
    - Direct HTTP response writing via self.write()

