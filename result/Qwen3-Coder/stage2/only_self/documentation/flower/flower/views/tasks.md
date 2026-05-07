# `tasks.py`

## `flower.views.tasks.TaskView` · *class*

## Summary:
TaskView is a web handler that retrieves and displays detailed information for a specific Celery task by its unique identifier.

## Description:
This class implements a GET endpoint for retrieving and displaying detailed information about a specific Celery task. It serves as part of the Flower monitoring web interface, allowing users to view task details through a web browser. The view handles authentication through Tornado's @web.authenticated decorator and provides appropriate error handling for missing tasks.

The class extends BaseHandler, inheriting common web request handling capabilities including authentication, template rendering, and utility methods for working with Celery tasks. It specifically focuses on task retrieval and presentation, making it a dedicated view for individual task inspection.

## State:
- `application`: Reference to the Tornado application instance containing configuration and shared resources
- `request`: Inherited from RequestHandler, contains the HTTP request information
- `response`: Inherited from RequestHandler, contains the HTTP response information

## Lifecycle:
Creation: Instances are automatically created by Tornado's routing mechanism when HTTP GET requests are received at the appropriate endpoint pattern. The constructor is inherited from RequestHandler and doesn't require special instantiation.

Usage: The typical usage involves:
1. Tornado receives a GET request to the task detail endpoint (e.g., /task/{task_id})
2. Tornado instantiates TaskView with the request parameters
3. The @web.authenticated decorator ensures the user is authenticated
4. The get() method is called with the task_id parameter
5. The task is retrieved from the events state using get_task_by_id
6. If the task exists, it's formatted using BaseHandler.format_task
7. The formatted task is rendered using the task.html template

Destruction: Cleanup is handled automatically by Tornado's request lifecycle management.

## Method Map:
```mermaid
graph TD
    A[GET request to /task/{task_id}] --> B[TaskView.get(task_id)]
    B --> C[get_task_by_id(application.events, task_id)]
    C --> D{task found?}
    D -- No --> E[raise web.HTTPError(404)]
    D -- Yes --> F[format_task(task)]
    F --> G[render("task.html", task=task)]
```

## Raises:
- tornado.web.HTTPError: Raised with status code 404 when a task with the specified ID does not exist
- tornado.web.HTTPError: Raised with status code 401 when authentication fails (handled by @web.authenticated decorator)

## Example:
```python
# When a user visits /task/abc123-def456 in the browser:
# 1. TaskView.get("abc123-def456") is invoked
# 2. get_task_by_id(self.application.events, "abc123-def456") is called
# 3. If task exists: 
#    - self.format_task(task) formats the task data for display
#    - self.render("task.html", task=formatted_task) renders the template
# 4. If task doesn't exist:
#    - web.HTTPError(404, "Unknown task 'abc123-def456'") is raised

# Typical usage in a web application context:
# URL Pattern: /task/(?P<task_id>[^/]+)
# This view handles requests like:
#   - GET /task/abc123-def456
#   - Returns HTML page with task details or 404 error
```

### `flower.views.tasks.TaskView.get` · *method*

## Summary:
Retrieves and displays detailed information for a specific task by its unique identifier.

## Description:
Handles HTTP GET requests to fetch and display information about a specific Celery task. This method serves as the entry point for viewing individual task details in the Flower web interface. It retrieves the task from the application's event store, applies custom formatting if configured, and renders the task information using the task.html template.

The method is part of the TaskView class hierarchy that extends BaseHandler, providing standardized web request handling for task-related operations. It follows the standard Tornado request lifecycle pattern where GET requests are processed through this method.

## Args:
    task_id (str): The unique identifier of the task to retrieve and display

## Returns:
    None: This method does not return a value directly, but renders an HTML response

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when no task exists with the specified task_id

## State Changes:
    Attributes READ:
        - self.application.events: Used to access the task storage
        - self.application.options.format_task: Potentially accessed during task formatting
    Attributes WRITTEN:
        - None: This method does not modify any instance attributes directly

## Constraints:
    Preconditions:
        - The task_id parameter must be a valid string identifier for an existing task
        - The application's events store must be properly initialized and contain task data
        - The application must have a valid template directory configured for rendering

    Postconditions:
        - If successful, the method triggers a template rendering operation
        - If task is not found, an HTTP 404 error is raised before any state changes

## Side Effects:
    - Makes a read-only access to the application's events storage
    - Invokes potential custom task formatting function if configured
    - Renders an HTML response to the client
    - May log errors if custom formatting fails

## `flower.views.tasks.Comparable` · *class*

## Summary:
A wrapper class that enables comparison operations on values, particularly useful for sorting and ordering task objects.

## Description:
The Comparable class serves as a utility wrapper that provides comparison functionality to arbitrary values. It is designed to work with the task management system in Flower, where objects need to be compared for sorting and ordering purposes. The class implements equality (`__eq__`) and less-than (`__lt__`) comparison operators, leveraging Python's `@total_ordering` decorator to automatically generate the remaining comparison methods.

This abstraction is particularly valuable when dealing with potentially incomparable types or when implementing custom sorting logic that needs to handle edge cases like None values gracefully.

## State:
- value: The wrapped value that supports comparison operations
  - Type: Any comparable type (int, str, datetime, etc.)
  - Valid range: Any value that supports comparison operations
  - Invariant: The value is immutable once set during initialization

## Lifecycle:
- Creation: Instantiate with any comparable value using `Comparable(value)`
- Usage: Objects can be compared using standard comparison operators (==, <, >, <=, >=)
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
flowchart TD
    A[Comparable(value)] --> B{value is comparable?}
    B -- Yes --> C[value stored internally]
    C --> D[Supports __eq__ and __lt__ operations]
    D --> E[Automatically gets other comparisons via @total_ordering]
    B -- No --> F[TypeError in comparison operations]
    
    G[__eq__(other)] --> H{other.value exists?}
    H -- Yes --> I[Compare self.value with other.value]
    H -- No --> J[Return False]
    
    K[__lt__(other)] --> L{other.value exists?}
    L -- Yes --> M[Try self.value < other.value]
    M --> N{TypeError?}
    N -- Yes --> O[self.value is None?]
    O --> P[Return True if None, False otherwise]
    N -- No --> Q[Return comparison result]
    L -- No --> R[Return False]
```

## Raises:
- TypeError: When comparing with incompatible types that cause comparison failures in `__lt__`
- AttributeError: When accessing `other.value` fails due to missing attribute

## Example:
```python
# Basic usage for sorting
tasks = [Comparable('task_c'), Comparable('task_a'), Comparable('task_b')]
sorted_tasks = sorted(tasks)
# Results in: [Comparable('task_a'), Comparable('task_b'), Comparable('task_c')]

# Handling None values
none_task = Comparable(None)
regular_task = Comparable('some_value')
print(none_task < regular_task)  # True (None considered less than any value)
print(regular_task < none_task)  # False (any value considered greater than None)

# Using in task processing contexts
task_values = [Comparable(t.name) for t in task_list]
sorted_by_name = sorted(task_values)
```

### `flower.views.tasks.Comparable.__init__` · *method*

## Summary:
Initializes a Comparable object with the specified value for comparison operations.

## Description:
Constructs a Comparable instance that wraps a value to enable ordered comparisons. This method serves as the constructor for the Comparable class, storing the provided value in an instance attribute that is used by comparison methods (__eq__, __lt__) to perform ordering operations.

## Args:
    value: Any comparable type that can be stored and compared with other instances. The value can be of any type, including None, numbers, strings, or custom objects.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.value - stores the provided value in the instance attribute

## Constraints:
    Preconditions: The value parameter can be any type, though it should be compatible with the comparison operations defined in the class.
    Postconditions: After execution, the instance will have self.value set to the provided value argument.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only assigns a value to an instance attribute.

### `flower.views.tasks.Comparable.__eq__` · *method*

## Summary:
Compares two Comparable instances for equality based on their value attributes.

## Description:
This method implements the equality comparison operator (==) for Comparable objects. It returns True if both instances have equal value attributes, False otherwise. This method is part of the total ordering protocol implemented by the Comparable class, which uses the @total_ordering decorator to automatically generate other comparison methods.

## Args:
    other (Comparable): Another Comparable instance to compare against

## Returns:
    bool: True if self.value equals other.value, False otherwise

## Raises:
    AttributeError: If other does not have a value attribute

## State Changes:
    Attributes READ: self.value, other.value
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - other must be an instance of Comparable class
    - Both self.value and other.value must be comparable using == operator
    Postconditions: 
    - Returns boolean result of comparison
    - Does not modify either object's state

## Side Effects:
    None

### `flower.views.tasks.Comparable.__lt__` · *method*

## Summary:
Implements the less-than comparison operation for Comparable objects, handling type mismatches gracefully.

## Description:
This method defines the behavior of the less-than operator (<) for Comparable instances. It attempts to compare the value attributes of two Comparable objects. When a TypeError occurs due to incompatible types, it falls back to checking if the left operand's value is None, providing a sensible default ordering for heterogeneous comparisons.

## Args:
    other (Comparable): Another Comparable instance to compare against

## Returns:
    bool: True if self.value is less than other.value, False otherwise. Returns True when self.value is None and other.value cannot be compared, False otherwise.

## Raises:
    AttributeError: If other does not have a value attribute

## State Changes:
    Attributes READ: self.value, other.value
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - other must be an instance of Comparable class
    - Both self.value and other.value must be comparable using < operator where possible
    Postconditions: 
    - Returns boolean result of comparison or fallback logic
    - Does not modify either object's state

## Side Effects:
    None

## `flower.views.tasks.TasksDataTable` · *class*

## Summary:
TasksDataTable is a web handler that provides JSON data for DataTables UI component, enabling server-side processing of task lists with sorting, filtering, and pagination capabilities.

## Description:
This class implements a Tornado web handler that serves as a data source for DataTables JavaScript component in the Flower web interface. It handles HTTP GET and POST requests to provide paginated, searchable, and sortable task data in JSON format suitable for DataTables consumption. The class integrates with Celery's event system to retrieve real-time task information and formats it according to DataTables requirements.

The handler supports server-side processing features including:
- Pagination (start/length parameters)
- Search filtering (search[value] parameter)
- Column-based sorting (order[0][column] and columns[{column}][data] parameters)
- Authentication through the @web.authenticated decorator

## State:
- Inherits all state from BaseHandler including application reference and request/response objects
- No additional instance attributes beyond those inherited from the parent class

## Lifecycle:
Creation: Instantiated automatically by Tornado's routing mechanism when HTTP requests are made to the appropriate endpoint. Requires authentication through the @web.authenticated decorator.

Usage: 
1. HTTP GET or POST request received by Tornado
2. Handler processes request parameters (pagination, sorting, filtering)
3. Retrieves tasks from Celery events system
4. Applies filtering, sorting, and pagination
5. Formats task data for DataTables consumption
6. Writes JSON response with draw, data, recordsTotal, and recordsFiltered fields

Destruction: Automatically managed by Tornado's request lifecycle.

## Method Map:
```mermaid
graph TD
    A[GET/POST request] --> B[TasksDataTable.get()]
    B --> C[Extract request parameters]
    C --> D[maybe_normalize_for_sort()]
    D --> E[iter_tasks()]
    E --> F[sorted()]
    F --> G[Process paginated results]
    G --> H[format_task()]
    H --> I[as_dict()]
    I --> J[Write JSON response]
    
    B --> K[Post method delegates to get()]
    K --> J
```

## Raises:
- tornado.web.HTTPError: Raised by BaseHandler parent class for authentication failures or invalid request parameters
- TypeError: May occur during type conversion of request parameters
- AttributeError: Could occur if task objects lack expected attributes during sorting or formatting

## Example:
```python
# Typical usage in web application
# Request URL: /tasks/data?draw=1&start=0&length=10&search%5Bvalue%5D=&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&columns%5B0%5D%5Bdata%5D=name

# Response format:
{
    "draw": 1,
    "data": [
        {
            "uuid": "task-uuid-1",
            "name": "my_task",
            "state": "SUCCESS",
            "received": 1634567890.123,
            "started": 1634567891.456,
            "runtime": 1.333,
            "worker": "worker-hostname"
        }
    ],
    "recordsTotal": 100,
    "recordsFiltered": 100
}
```

### `flower.views.tasks.TasksDataTable.get` · *method*

## Summary:
Handles DataTables AJAX requests for retrieving and filtering task data with sorting capabilities.

## Description:
Processes HTTP GET requests from DataTables client-side component to fetch paginated and filtered task information from Celery events. This method implements server-side processing for DataTables by handling search, sorting, and pagination parameters sent by the client, then returning formatted JSON data suitable for DataTables display.

The method integrates with the Flower monitoring application's event system to retrieve real-time task information, applies custom formatting to task data, and transforms worker references into hostname strings for display. It's part of the TasksDataTable class that provides a web interface for viewing Celery tasks.

Known callers:
- DataTables JavaScript component making AJAX requests to the /tasks endpoint
- Tornado web framework routing HTTP GET requests to this method

This logic is separated into its own method to encapsulate the complex data processing pipeline required for DataTables integration, providing a clean API for handling the specific parameter formats and response structures expected by the DataTables library.

## Args:
    None: All parameters are extracted from HTTP request arguments using self.get_argument()

## Returns:
    None: Response is written directly to HTTP response using self.write()

## Raises:
    None explicitly raised: HTTP responses are handled by Tornado framework

## State Changes:
    Attributes READ:
        - self.application: Application instance containing event data
        - self.request.arguments: HTTP request parameters
    Attributes WRITTEN:
        - None: Response is written directly to HTTP response

## Constraints:
    Preconditions:
        - HTTP request must include DataTables-specific parameters (draw, start, length, search[value], order[0][column], columns[{column}][data], order[0][dir])
        - Application must have events system properly initialized with task data
        - Sort column index must be valid and correspond to existing task attributes
        - Task data must be available in app.events.state.tasks_by_timestamp()
        - Request parameters must be parseable as expected types (int, str)
        
    Postconditions:
        - HTTP response contains properly formatted JSON data for DataTables consumption
        - Response includes draw counter for DataTables state synchronization
        - Response includes record counts for pagination display
        - Response data is properly paginated and filtered
        - Task objects are temporarily modified for sorting purposes via maybe_normalize_for_sort

## Side Effects:
    - Reads HTTP request arguments from self.get_argument() with specific DataTables parameter names
    - Writes JSON response to HTTP response using self.write() with specific structure:
      {
          "draw": int,
          "data": list[dict],
          "recordsTotal": int,
          "recordsFiltered": int
      }
    - Accesses application events data through app.events.state.tasks_by_timestamp()
    - Calls external utility functions (as_dict, iter_tasks) from utils.tasks module
    - May invoke custom formatting functions configured in application options
    - Performs type conversions on task attributes for proper sorting via Comparable wrapper
    - Temporarily modifies task objects for sorting purposes through maybe_normalize_for_sort

### `flower.views.tasks.TasksDataTable.maybe_normalize_for_sort` · *method*

## Summary:
Normalizes task attributes to appropriate data types for consistent sorting operations.

## Description:
This classmethod prepares task objects for sorting by converting specific attributes to their appropriate data types. It is called before sorting tasks in the TasksDataTable view to ensure that attributes like 'received', 'started', and 'runtime' are properly typed for numerical comparisons, and 'name' and 'state' are converted to strings for alphabetical sorting.

The method operates on task objects in-place, modifying their attributes to enable correct sorting behavior. It only processes attributes that are defined in the sort_keys mapping and handles potential type conversion errors gracefully.

## Args:
    cls: The class reference (used for classmethod decorator)
    tasks: An iterable of task tuples, where each tuple contains (uuid, task_object)
    sort_by: A string indicating which attribute to normalize for sorting

## Returns:
    None: This method modifies task objects in-place and does not return a value

## Raises:
    None: Type conversion errors are caught and silently ignored

## State Changes:
    Attributes READ: None (reads from task objects indirectly via getattr)
    Attributes WRITTEN: Modifies task attributes in-place (name, state, received, started, runtime)

## Constraints:
    Preconditions:
        - The tasks parameter must be iterable containing tuples of (uuid, task_object)
        - Each task_object must have the attribute specified by sort_by
        - The sort_by parameter must be one of: 'name', 'state', 'received', 'started', 'runtime'
    
    Postconditions:
        - Task objects have their specified attributes converted to appropriate types
        - If type conversion fails, the original attribute value is preserved
        - Task objects remain unchanged except for the normalized attributes

## Side Effects:
    Mutates task objects in-place by changing their attribute values

### `flower.views.tasks.TasksDataTable.post` · *method*

## Summary:
Handles HTTP POST requests by delegating to the GET handler for data table operations.

## Description:
This method implements the HTTP POST endpoint for the TasksDataTable view, which is used by DataTables jQuery plugin to fetch paginated, sorted, and filtered task data. The POST method simply delegates to the GET method, which performs all the actual data processing including pagination, sorting, filtering, and JSON serialization. This pattern is standard for server-side DataTables implementations where both GET and POST requests should return identical data.

The method is decorated with `@web.authenticated`, ensuring that only authenticated users can access the task data table functionality. This authentication requirement is inherited from the BaseHandler parent class.

## Args:
    None: This method does not accept any explicit arguments beyond the standard Tornado request handling.

## Returns:
    None: The method returns the result of `self.get()`, which is typically a JSON response containing task data and pagination information.

## Raises:
    tornado.web.HTTPError: May be raised by the underlying `get` method or inherited authentication mechanisms when:
        - Authentication fails (401 Unauthorized)
        - Invalid request parameters are provided (400 Bad Request)
        - Other HTTP-level errors occur during data processing

## State Changes:
    Attributes READ:
        - self.application: Used by the `get` method to access application state and configuration
        - self.request: Inherited from Tornado's RequestHandler, contains HTTP request information
        - self.get_argument(): Used to extract query parameters from the request
    
    Attributes WRITTEN:
        - self.response: Inherited from Tornado's RequestHandler, modified during the response writing process

## Constraints:
    Preconditions:
        - The request must be authenticated (user must be logged in)
        - The request must include valid DataTables parameters (draw, start, length, search, order, columns)
        - The application must have valid event data and task tracking enabled
    
    Postconditions:
        - The method returns a properly formatted JSON response with task data
        - The response includes pagination metadata (recordsTotal, recordsFiltered)
        - The response maintains consistency with the GET method's output

## Side Effects:
    - I/O operations: Reads from application event data store
    - External service calls: Accesses Celery task tracking data through the application's events system
    - Response generation: Writes JSON data to the HTTP response stream
    - Authentication validation: Verifies user credentials through the authentication system

### `flower.views.tasks.TasksDataTable.format_task` · *method*

## Summary:
Formats task arguments using a custom formatting function if configured, returning the task UUID and potentially modified arguments.

## Description:
Processes a task tuple by applying custom formatting to the task arguments when a formatting function is configured in the application options. This method is used to transform raw task data into a more readable or structured format before presentation in the web interface.

The method is called during the data processing pipeline in TasksDataTable.get() when preparing task information for display in the DataTable UI. It ensures that task arguments are properly formatted according to application-specific requirements while maintaining data integrity through defensive copying.

Known callers:
- TasksDataTable.get() method during HTTP GET request processing for task listing
- Part of the data transformation pipeline in the task listing view

This logic is separated into its own method to provide a clean abstraction for task argument formatting, allowing for easy extension with custom formatting functions while maintaining consistent error handling and data protection patterns.

## Args:
    task (tuple): A tuple containing (uuid, args) where uuid is the task identifier and args are the task arguments

## Returns:
    tuple: A tuple containing (uuid, args) where uuid is unchanged and args may be modified by custom formatting

## Raises:
    None explicitly raised - Exceptions during custom formatting are caught and logged

## State Changes:
    Attributes READ:
        - self.application.options.format_task: Custom formatting function configuration
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The task parameter must be a tuple with exactly two elements (uuid, args)
        - self.application must be properly initialized with options attribute
        - self.application.options must be accessible and contain format_task attribute
        
    Postconditions:
        - The returned tuple maintains the same structure as input
        - The uuid element remains unchanged
        - The args element may be modified by custom formatting function if present
        - Original args data is preserved through copy operation

## Side Effects:
    - Makes a copy of the args data using copy.copy() for defensive programming
    - May invoke external custom formatting function if configured
    - Logs exceptions during custom formatting using logger.exception()
    - Performs minimal I/O operations (logging)

## `flower.views.tasks.TasksView` · *class*

## Summary:
TasksView is a Tornado web handler that renders the tasks monitoring dashboard in the Flower web application.

## Description:
This class implements the HTTP GET request handler for the tasks monitoring interface. It provides a web-based dashboard for viewing Celery task information and is part of the Flower monitoring application's web UI. The view requires authentication and prepares display context based on application configuration settings.

The class inherits from BaseHandler, which provides common web request handling functionality including authentication, CORS support, and template rendering utilities. The TasksView specifically focuses on presenting task-related information in a user-friendly interface.

## State:
- `application`: Reference to the Tornado application instance containing configuration and shared resources
- `capp`: Property inherited from BaseHandler that provides access to the Celery application object
- `request`: Inherited from RequestHandler, contains HTTP request information
- `response`: Inherited from RequestHandler, contains HTTP response information

## Lifecycle:
Creation: Instances are automatically created by Tornado's routing mechanism when HTTP GET requests are made to the tasks endpoint. The constructor is inherited from RequestHandler.

Usage: When a user accesses the tasks monitoring page:
1. Tornado routes the GET request to TasksView.get()
2. Authentication is verified through @web.authenticated decorator
3. Application configuration is accessed to determine time formatting
4. Template rendering is performed with prepared context data

Destruction: Cleanup is handled automatically by Tornado's request lifecycle management.

## Method Map:
```mermaid
graph TD
    A[TasksView.get()] --> B[application.options.natural_time]
    A --> C[application.capp.conf.timezone]
    A --> D[render(tasks.html, ...)]
    B --> E[time formatting logic]
    C --> E
    E --> F[time parameter construction]
    F --> D
```

## Raises:
- tornado.web.HTTPError: Raised by @web.authenticated decorator when authentication fails (401 Unauthorized)
- tornado.web.HTTPError: Raised if template rendering fails (500 Internal Server Error)
- Exception: May be raised during template rendering if the tasks.html template is not found

## Example:
```python
# User accesses /tasks URL
# Tornado automatically creates TasksView instance
# Authentication is verified through @web.authenticated
# Application configuration is read to set time formatting
# tasks.html template is rendered with:
# - Empty tasks list (tasks=[])
# - Task columns configuration from app.options.tasks_columns
# - Time formatting string based on natural_time option and timezone
# The rendered HTML displays the tasks monitoring dashboard
```

### `flower.views.tasks.TasksView.get` · *method*

## Summary:
Renders the tasks dashboard page with configured display settings and empty task list.

## Description:
Handles GET requests to display the tasks monitoring page. This method prepares the necessary context variables for rendering the tasks.html template, including time formatting configuration and column layout settings from application options. The method initializes with an empty tasks list, expecting the frontend to populate tasks dynamically.

This logic is separated into its own method to provide a clean entry point for the tasks view, allowing for consistent initialization of view-specific parameters and proper template rendering with the expected context.

## Args:
    None: This method does not accept any explicit arguments beyond the standard Tornado handler parameters.

## Returns:
    None: This method does not return a value directly, but causes the Tornado framework to render the tasks.html template.

## Raises:
    None: This method does not explicitly raise exceptions, though Tornado's render method may raise exceptions related to template rendering issues.

## State Changes:
    Attributes READ:
        - self.application: Application instance containing configuration
        - self.application.capp: Celery application instance from the application
        - self.application.options: Configuration options for the application
        - self.application.options.natural_time: Boolean flag for time formatting
        - self.application.options.tasks_columns: Column configuration for task display
        - self.application.capp.conf.timezone: Timezone configuration from Celery

    Attributes WRITTEN:
        - None: This method does not modify any instance attributes directly.

## Constraints:
    Preconditions:
        - The handler must be properly initialized as a Tornado web handler
        - The application instance must have valid options and capp attributes
        - The tasks.html template must exist in the templates directory
        - The application options must include tasks_columns configuration

    Postconditions:
        - The response will contain rendered HTML for the tasks dashboard
        - The rendered page will include configured time formatting and column layout
        - The tasks list will be initialized as empty in the template context

## Side Effects:
    - Template rendering I/O operation to generate HTML response
    - Potential external service calls through the Celery application (via capp)
    - HTTP response generation through Tornado's render method

