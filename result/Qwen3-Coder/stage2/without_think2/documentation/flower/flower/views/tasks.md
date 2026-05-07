# `tasks.py`

## `flower.views.tasks.TaskView` · *class*

## Summary:
TaskView is a Tornado web handler responsible for rendering detailed information about a specific Celery task in an HTML template.

## Description:
TaskView handles GET requests to display the details of a particular task identified by its unique task ID. It retrieves the task from the application's event store, applies custom formatting if configured, and renders the information using the task.html template. This handler serves as part of the Flower web interface for monitoring Celery tasks.

The class inherits from BaseHandler, which provides authentication, error handling, and utility methods for working with Celery tasks. It leverages the @web.authenticated decorator to ensure only authenticated users can access task details.

## State:
- Inherits all state from BaseHandler including application reference and request/response objects
- No additional instance attributes beyond those inherited

## Lifecycle:
- Creation: Automatically instantiated by Tornado's routing mechanism when handling HTTP requests
- Usage: The get method is invoked during the HTTP request lifecycle when a user accesses a task detail page
- Destruction: Managed automatically by Tornado's request handling cycle

## Method Map:
```mermaid
graph TD
    A[GET request] --> B[TaskView.get]
    B --> C[get_task_by_id]
    C --> D[events.state.tasks lookup]
    D --> E{Task found?}
    E -- No --> F[HTTPError(404)]
    E -- Yes --> G[format_task]
    G --> H[render task.html]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the requested task ID does not correspond to any existing task in the events store
- tornado.web.HTTPError(401): Inherited from BaseHandler's @web.authenticated decorator when authentication fails

## Example:
```python
# Accessing task details via URL: /task/<task_id>
# User navigates to: http://flower.example.com/task/abc123-def456

# Handler flow:
# 1. Tornado routes request to TaskView.get
# 2. get_task_by_id retrieves task from events state
# 3. If task exists, format_task applies custom formatting
# 4. render() displays task.html with task data context
# 5. If task doesn't exist, raises HTTPError(404)
```

### `flower.views.tasks.TaskView.get` · *method*

## Summary:
Retrieves and renders detailed information for a specific task by its unique identifier.

## Description:
This method handles HTTP GET requests to fetch and display information about a particular task. It retrieves the task from the application's event store using the provided task ID, applies custom formatting if configured, and renders the task details in an HTML template. The method serves as the primary endpoint for accessing individual task information in the Flower web interface.

The logic is encapsulated in its own method to separate the HTTP request handling from the core task retrieval and rendering logic, promoting reusability and testability. This approach allows the task viewing functionality to be easily extended or modified without affecting other parts of the application.

## Args:
    task_id (str or int): Unique identifier of the task to retrieve and display

## Returns:
    None: This method does not return a value directly, but renders an HTML response

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when the specified task ID does not correspond to any existing task

## State Changes:
    Attributes READ: self.application.events, self.application.options.format_task
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The task_id parameter must be a valid identifier that can be used to look up tasks in the events store
        - The application must have an events store available via self.application.events
        - The application must be properly initialized with the necessary task data

    Postconditions:
        - If successful, the method renders an HTML page displaying the task details
        - If the task is not found, an HTTP 404 error is raised

## Side Effects:
    - Makes a database or storage lookup to retrieve task data
    - Renders an HTML template with task information
    - May invoke external custom formatting functions if configured via self.application.options.format_task
    - Calls the parent render method which performs HTTP response rendering

## `flower.views.tasks.Comparable` · *class*

## Summary:
A wrapper class that enables safe comparison operations between objects with potentially incompatible types.

## Description:
The Comparable class wraps an arbitrary value and provides equality (`__eq__`) and less-than (`__lt__`) comparison operations. It handles type mismatches gracefully by catching TypeError exceptions in the less-than operation and falling back to comparing with None. This class is designed to facilitate sorting and ordering operations where heterogeneous data types might be compared.

## State:
- value: The wrapped object being compared. Type can be any object that supports equality comparison with itself and potentially with None.
- Invariant: The value attribute maintains the exact object passed during initialization without modification.

## Lifecycle:
- Creation: Instantiate with any object. The constructor accepts any value.
- Usage: Call comparison operators (__eq__, __lt__) on instances. The __eq__ method compares values directly, while __lt__ attempts comparison and falls back to None checking on TypeError.
- Destruction: No special cleanup required; standard Python garbage collection applies.

## Method Map:
```mermaid
graph TD
    A[Comparable.__init__(value)] --> B[Comparable.__eq__(other)]
    A --> C[Comparable.__lt__(other)]
    B --> D[Return bool]
    C --> D
```

## Raises:
- No exceptions are explicitly raised by __init__.
- TypeError may occur internally during __lt__ comparison but is caught and handled gracefully.

## Example:
```python
# Create comparable wrappers
a = Comparable(5)
b = Comparable("hello")
c = Comparable(None)

# Equality comparisons
print(a == Comparable(5))  # True
print(b == Comparable("world"))  # False

# Less than comparisons
print(a < Comparable(10))  # True
print(c < a)  # True (None is considered less than any other value)
print(a < Comparable("string"))  # True (TypeError caught, falls back to None check)
```

### `flower.views.tasks.Comparable.__init__` · *method*

## Summary:
Initializes a Comparable object with a value for comparison operations.

## Description:
The `__init__` method sets up a Comparable instance by storing the provided value in the object's `value` attribute. This method is part of the Comparable class that enables ordered comparisons between instances using standard comparison operators.

## Args:
    value: The value to be stored and used for comparison operations. Can be of any type that supports equality and less-than comparisons.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.value

## Constraints:
    Preconditions: The value argument can be any object that supports the comparison operations defined in the class methods.
    Postconditions: After execution, the instance will have its `value` attribute set to the provided value.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `flower.views.tasks.Comparable.__eq__` · *method*

## Summary:
Compares two Comparable objects for equality based on their value attributes.

## Description:
This method implements the equality comparison operator (==) for Comparable objects. It is part of the total_ordering decorator's requirements and enables proper sorting and comparison behavior. The method is called during equality checks between Comparable instances, such as when using '==' or in sorting operations.

This method is essential for the Comparable class to work correctly with the @total_ordering decorator, which automatically generates the remaining comparison methods (__lt__, __le__, __gt__, __ge__) based on just __eq__ and one other comparison method (__lt__ in this case).

## Args:
    other (Comparable): Another Comparable instance to compare with this object. Must have a value attribute that supports equality comparison with self.value.

## Returns:
    bool: True if both objects have equal value attributes, False otherwise. Returns False if other does not have a value attribute.

## Raises:
    AttributeError: If the other parameter does not have a value attribute, which can occur when comparing with incompatible types.

## State Changes:
    Attributes READ: self.value, other.value
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - other must be an instance with a value attribute
    - Both self.value and other.value must be comparable using == operator
    - The comparison should be symmetric (if a == b, then b == a)
    
    Postconditions:
    - Returns boolean result of comparing self.value with other.value
    - Does not modify either object's state
    - The comparison is reflexive (a == a) and transitive (if a == b and b == c, then a == c)

## Side Effects:
    None

### `flower.views.tasks.Comparable.__lt__` · *method*

## Summary:
Compares two Comparable objects for less-than ordering, implementing fallback behavior for type mismatches in ordered collections.

## Description:
This method implements the less-than comparison operation for Comparable objects that are part of a class decorated with Python's `@total_ordering` decorator. It enables sorting and ordering operations on objects containing potentially incomparable values.

The method attempts to directly compare the `value` attributes of two Comparable instances. When a TypeError occurs due to incompatible types (e.g., comparing strings with integers), it returns `True` only if `self.value` is `None`, providing a consistent fallback ordering strategy that ensures predictable sorting behavior.

This method exists as a separate implementation because Python's `@total_ordering` decorator requires at least one rich comparison method (`__lt__`, `__le__`, `__gt__`, or `__ge__`) to be defined, and this implementation provides the core ordering logic while gracefully handling heterogeneous data types that would otherwise cause comparison failures.

## Args:
    other (Comparable): Another Comparable instance to compare against

## Returns:
    bool: True if self.value is less than other.value, or if self.value is None and other.value cannot be compared

## Raises:
    TypeError: When comparing values that cannot be compared and self.value is not None

## State Changes:
    Attributes READ: self.value, other.value
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Both self and other must be Comparable instances with comparable value attributes where possible
    Postconditions: Returns a boolean indicating the ordering relationship between the two objects

## Side Effects:
    None

## `flower.views.tasks.TasksDataTable` · *class*

## Summary:
TasksDataTable is a Tornado web handler that provides server-side processing for DataTables JavaScript library to display paginated, searchable, and sortable task lists from Celery workers.

## Description:
This class implements the backend API endpoint that DataTables uses to fetch and display task data. It handles HTTP GET requests with parameters for pagination, sorting, and filtering, then returns JSON-formatted data that DataTables can render in the browser. The class integrates with Celery's event system to retrieve real-time task information and provides a RESTful interface for frontend task listing components.

The handler processes DataTables-specific parameters including draw counter, pagination offsets, sorting column indices, and search terms. It leverages the existing Flower infrastructure for task iteration, filtering, and formatting while providing the exact JSON structure expected by DataTables for client-side rendering. The class also includes logic to normalize data types for proper sorting operations.

## State:
- `application`: Reference to the Tornado application instance containing Celery events and configuration
- `request`: Inherited from RequestHandler, contains HTTP request data including query arguments
- `response`: Inherited from RequestHandler, contains HTTP response data

## Lifecycle:
- Creation: Automatically instantiated by Tornado framework when handling HTTP requests to the associated route
- Usage: Called via HTTP GET requests with DataTables parameters; typically accessed through browser-based task listing UI
- Destruction: Managed automatically by Tornado's request lifecycle

## Method Map:
```mermaid
graph TD
    A[TasksDataTable.get()] --> B[Extract DataTables parameters]
    A --> C[Normalize sort keys for sorting]
    A --> D[Iterate and filter tasks]
    A --> E[Sort tasks by specified column]
    A --> F[Apply pagination]
    A --> G[Format task data]
    A --> H[Return JSON response]
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
```

## Raises:
- `tornado.web.HTTPError(401)`: Raised when authentication fails (via @web.authenticated decorator)
- `TypeError`: May occur during type conversion of DataTables parameters if invalid values are provided
- `KeyError`: Could occur if DataTables sends unexpected parameter names

## Example:
```python
# Typical usage through HTTP request:
# GET /tasks/data?draw=1&start=0&length=10&search[value]=error&order[0][column]=2&order[0][dir]=desc

# Response structure:
{
    "draw": 1,
    "data": [
        {
            "uuid": "task-123",
            "name": "process_image",
            "state": "FAILURE",
            "received": 1634567890.123,
            "started": 1634567891.456,
            "runtime": 0.123,
            "worker": "worker1@host"
        }
    ],
    "recordsTotal": 100,
    "recordsFiltered": 10
}

# The handler normalizes data types for sorting by converting fields like:
# - 'name': str
# - 'state': str  
# - 'received': float
# - 'started': float
# - 'runtime': float
```

### `flower.views.tasks.TasksDataTable.get` · *method*

## Summary:
Processes DataTable AJAX requests for task listings with sorting, filtering, and pagination support.

## Description:
Handles GET requests from DataTables JavaScript library to provide paginated and searchable task data for web UI display. This method implements server-side processing for DataTables by extracting sorting and filtering parameters from the request, retrieving and processing tasks from the Celery event stream, and returning JSON-formatted data that DataTables expects for rendering.

The method is part of the TasksDataTable view class and is invoked during DataTables initialization or user interactions (sorting, filtering, pagination) to dynamically load task information. It processes request arguments to determine sorting criteria, filtering parameters, and pagination boundaries, then fetches matching tasks, formats them appropriately, and returns them in a structure compatible with DataTables client-side expectations.

Known callers:
- DataTables JavaScript library during initialization or user interactions
- Web browser making AJAX requests to the /tasks endpoint

This logic is extracted into its own method rather than inlined because:
- It encapsulates complex DataTables integration logic including parameter parsing, sorting, filtering, and pagination
- It provides a clean separation between HTTP request handling and data processing concerns
- It enables reuse of the same data processing logic for different DataTables-based UI components
- It follows the principle of single responsibility by dedicating this method solely to handling DataTables requests

## Args:
    None directly (inherits from BaseHandler)

## Returns:
    None (writes JSON response directly via self.write)

## Raises:
    tornado.web.HTTPError: May be raised by BaseHandler.get_argument when argument parsing fails

## State Changes:
    Attributes READ: self.application, self.request.arguments
    Attributes WRITTEN: None (response written via self.write)

## Constraints:
    Preconditions:
        - Request must contain valid DataTables parameters (draw, start, length, order, columns, search)
        - Application must have events state with tasks_by_timestamp() method available
        - Sorting column index must correspond to existing columns in the DataTable configuration
        - Sort_by field must be a valid attribute of task objects
    Postconditions:
        - Response written to HTTP connection in DataTables-compatible JSON format
        - Data includes draw counter, filtered task records, and total record counts

## Side Effects:
    I/O: Reads request arguments from HTTP request
    External service calls: Calls external functions (iter_tasks, as_dict, format_task) and methods (tasks_by_timestamp, get_argument)
    Mutations to objects outside self: None (only writes response data)

### `flower.views.tasks.TasksDataTable.maybe_normalize_for_sort` · *method*

## Summary:
Converts task attribute values to appropriate data types for consistent sorting operations.

## Description:
This method normalizes task attribute values to their expected data types (str or float) based on the sort key to ensure proper sorting behavior. It processes task objects in-place, converting specified attributes to their appropriate types to enable consistent sorting. This method is typically called during data table rendering when sorting tasks by different criteria.

## Args:
    cls: The class reference (used as a class method)
    tasks: An iterable of task objects, typically tuples of (task_id, task_object) where task_object has attributes to be sorted
    sort_by: A string indicating which attribute to normalize for sorting, must be one of 'name', 'state', 'received', 'started', or 'runtime'

## Returns:
    None: This method modifies task objects in-place and does not return a value

## Raises:
    None explicitly raised: The method handles TypeError exceptions internally by silently ignoring conversion failures

## State Changes:
    Attributes READ: Reads task attributes specified by sort_by parameter using getattr
    Attributes WRITTEN: Modifies task objects in-place by setting normalized attribute values using setattr

## Constraints:
    Preconditions: 
    - tasks must be iterable containing task objects with the specified sort_by attribute
    - sort_by must be one of 'name', 'state', 'received', 'started', or 'runtime'
    Postconditions:
    - Task objects will have their sort_by attribute converted to the appropriate type (str or float) if the attribute value is truthy
    - If conversion fails due to TypeError, the original value is preserved
    - If the attribute doesn't exist or is falsy, no modification occurs

## Side Effects:
    None: This method only modifies task objects in-place and doesn't perform I/O or external service calls

### `flower.views.tasks.TasksDataTable.post` · *method*

## Summary:
Handles POST requests by delegating to the GET method for consistent task data retrieval and formatting.

## Description:
This method implements the HTTP POST endpoint for the TasksDataTable view, which serves task data in a format compatible with the DataTables JavaScript library. The POST method simply delegates to the GET method, ensuring consistent behavior and data processing regardless of the HTTP method used by the client.

The method is part of the TasksDataTable class, which inherits from BaseHandler and implements authentication through the @web.authenticated decorator. This ensures that only authenticated users can access task data through both GET and POST requests.

Known callers:
- HTTP clients making POST requests to the task data table endpoint
- The Tornado web framework during request processing when a POST request matches this route

This logic is implemented as a separate method rather than being inlined because:
- It maintains symmetry between GET and POST endpoints for the same resource
- It follows REST conventions where both methods can be used for read-only operations
- It provides a clear separation of concerns while keeping the implementation consistent
- It allows for future extension of POST-specific functionality if needed

## Args:
    None explicitly defined in method signature

## Returns:
    None (inherited from BaseHandler.get())

## Raises:
    HTTPError: May raise authentication-related HTTP errors if user is not authenticated
    HTTPError: May raise other HTTP errors inherited from BaseHandler.get() implementation

## State Changes:
    Attributes READ:
        - self.application (accessed via self.capp property)
        - self.request (inherited from RequestHandler)
        - self.response (inherited from RequestHandler)
    
    Attributes WRITTEN:
        - None (method delegates to self.get())

## Constraints:
    Preconditions:
        - User must be authenticated (enforced by @web.authenticated decorator)
        - HTTP request must be a POST request to the correct endpoint
        - Application must have proper event tracking enabled
        
    Postconditions:
        - The method returns the same data as the GET method for the same request parameters
        - Authentication requirements are satisfied before execution

## Side Effects:
    - Makes calls to self.get() which processes task data and writes JSON response
    - May make external calls to authentication services (via @web.authenticated)
    - Writes HTTP response data to the client

### `flower.views.tasks.TasksDataTable.format_task` · *method*

## Summary:
Formats task arguments using a custom formatting function if available, returning the task UUID and processed arguments.

## Description:
This method processes a task tuple by extracting its UUID and arguments, then applies a custom formatting function to the arguments if one is configured in the application options. The formatted arguments are returned alongside the original UUID. This method serves as a utility for consistent task argument processing throughout the application, separating formatting logic from the main data processing flow.

## Args:
    task (tuple): A tuple containing (uuid: str, args: dict) representing a task identifier and its arguments.

## Returns:
    tuple: A tuple containing (uuid: str, args: dict) where args may be modified by the custom formatter if one was provided.

## Raises:
    None explicitly raised, though exceptions in custom formatting functions are caught and logged.

## State Changes:
    Attributes READ: self.application.options.format_task
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The task parameter must be a tuple with exactly two elements (uuid, args) where uuid is a string and args is a dictionary-like object.
    Postconditions: The returned tuple maintains the same structure (uuid, args) with potentially modified args.

## Side Effects:
    I/O: Logs exceptions using logger.exception when custom formatting fails.
    External service calls: None directly, but depends on external custom_format_task function if provided.

## `flower.views.tasks.TasksView` · *class*

## Summary:
TasksView is a Tornado web handler responsible for rendering the main tasks dashboard page in the Flower web interface.

## Description:
The TasksView class handles HTTP GET requests to display the tasks monitoring dashboard. It inherits from BaseHandler and provides the initial page load functionality for the tasks interface. The view prepares the necessary context variables including task display columns, time formatting configuration, and an empty task list for the initial render. The actual task data is typically loaded dynamically via AJAX after the initial page load.

This class serves as the entry point for the tasks monitoring UI and ensures proper authentication through the @web.authenticated decorator before rendering the tasks.html template. The get method configures time display formatting based on application options and timezone settings, then renders the tasks.html template with empty task list and configured display settings.

## State:
- `application`: Reference to the Tornado application instance containing configuration and worker data
- `capp`: Property inherited from BaseHandler returning the Celery application object from the application instance
- `request`: Inherited from RequestHandler, contains the HTTP request data
- `response`: Inherited from RequestHandler, contains the HTTP response data

## Lifecycle:
- Creation: Instantiated automatically by Tornado's routing mechanism when handling HTTP GET requests to the tasks endpoint
- Usage: Called during initial page load of the tasks dashboard, preparing context for template rendering
- Destruction: Managed automatically by Tornado's request handling cycle

## Method Map:
```mermaid
graph TD
    A[TasksView.get] --> B[application.options.natural_time]
    A --> C[application.capp.conf.timezone]
    A --> D[render(tasks.html, ...)]
```

## Raises:
- `tornado.web.HTTPError(401)`: Raised by @web.authenticated decorator when user is not authenticated
- No explicit exceptions raised by the get method itself

## Example:
```python
# Typical usage through web browser navigation to /tasks endpoint
# This would render tasks.html with:
# - Empty tasks list (tasks=[])
# - Configured display columns from app.options.tasks_columns
# - Time formatting configuration based on app.options.natural_time and capp.conf.timezone
```

### `flower.views.tasks.TasksView.get` · *method*

## Summary:
Renders the tasks dashboard page with empty task list and configured display settings.

## Description:
This method handles GET requests to the tasks view endpoint, rendering the main tasks dashboard template. It prepares the necessary context variables including display columns, time formatting configuration, and an empty task list for initial page load. The method is part of the TasksView class that inherits from BaseHandler.

The method is called during the initial page load of the tasks dashboard, providing the basic UI structure and configuration before dynamic task data is loaded via AJAX or other mechanisms. It configures the time display format based on application options and timezone settings.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ:
        - self.application: Used to access app.options for configuration
        - self.application.capp: Used to access capp.conf for timezone configuration
    
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - self.application must be a valid Tornado application instance
        - self.application.options must exist and contain tasks_columns and natural_time attributes
        - self.application.capp must exist and have a conf attribute
        - self.application.capp.conf may contain a timezone attribute
    
    Postconditions:
        - The method calls self.render() with appropriate template and context
        - No modifications are made to the application state

## Side Effects:
    - Template rendering with HTTP response generation
    - Potential I/O operations during template rendering
    - Calls to self.render() which may involve filesystem access for templates

