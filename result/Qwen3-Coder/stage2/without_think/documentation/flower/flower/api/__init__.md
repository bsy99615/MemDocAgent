# `__init__.py`

## `flower.api.__init__.BaseApiHandler` · *class*

## Summary:
BaseApiHandler is an API endpoint handler that enforces authentication requirements and manages error responses for Flower's web API.

## Description:
This class extends BaseHandler to provide API-specific functionality with mandatory authentication enforcement. It ensures that API endpoints can only be accessed when proper authentication is configured or when the FLOWER_UNAUTHENTICATED_API environment variable is explicitly set to enable unauthenticated access. The class serves as a base class for implementing various API endpoints in the Flower monitoring interface, providing consistent authentication behavior and error handling.

## State:
- Inherits all state from BaseHandler including request handling capabilities
- No additional instance attributes beyond those inherited from the parent class
- Authentication state is determined by application options and environment variables:
  - `self.application.options.basic_auth` - Basic authentication configuration
  - `self.application.options.auth` - Authentication configuration
  - Environment variable `FLOWER_UNAUTHENTICATED_API` - Enables unauthenticated API access

## Lifecycle:
- Creation: Instantiated automatically by Tornado framework when handling API requests
- Usage: Called by Tornado framework during request processing lifecycle
  - prepare() method is called first to validate authentication requirements
  - Request handlers are called after successful preparation
  - write_error() method is invoked when exceptions occur during request processing
- Destruction: Managed automatically by Tornado framework's request lifecycle

## Method Map:
```mermaid
graph TD
    A[Request Received] --> B[prepare()]
    B --> C{Authentication Required?}
    C -->|Yes| D{FLOWER_UNAUTHENTICATED_API Enabled?}
    D -->|No| E[raise HTTPError(401)]
    D -->|Yes| F[Process Request]
    C -->|No| F
    F --> G[Request Handler]
    G --> H{Exception Occurred?}
    H -->|Yes| I[write_error()]
    I --> J[Return Error Response]
    H -->|No| K[Return Success Response]
```

## Raises:
- tornado.web.HTTPError(401): Raised in prepare() method when authentication is required (neither basic_auth nor auth options are configured) and FLOWER_UNAUTHENTICATED_API environment variable is not enabled

## Example:
```python
# To enable unauthenticated API access:
os.environ['FLOWER_UNAUTHENTICATED_API'] = 'true'

# The handler will be automatically used by Tornado framework
# when processing requests to API endpoints inheriting from BaseApiHandler
```

### `flower.api.__init__.BaseApiHandler.prepare` · *method*

## Summary:
Validates API authentication requirements before processing requests.

## Description:
Checks if API access is permitted based on authentication configuration and environment variables. This method is called by the Tornado web framework during the request preparation phase, before any HTTP method handlers execute. It ensures that unauthenticated API access is only allowed when explicitly enabled via the FLOWER_UNAUTHENTICATED_API environment variable.

## Args:
    None

## Returns:
    None

## Raises:
    tornado.web.HTTPError: Raised with status code 401 when authentication is required but the FLOWER_UNAUTHENTICATED_API environment variable is not set to enable unauthenticated access.

## State Changes:
    Attributes READ: 
    - self.application.options.basic_auth
    - self.application.options.auth
    
    Attributes WRITTEN: 
    None

## Constraints:
    Preconditions:
    - The method assumes self.application.options contains basic_auth and auth attributes
    - The FLOWER_UNAUTHENTICATED_API environment variable should be a string that strtobool can parse
    
    Postconditions:
    - If authentication is required and not enabled via environment variable, an HTTP 401 error is raised
    - If authentication is properly configured or unauthenticated access is enabled, the method completes normally

## Side Effects:
    None

### `flower.api.__init__.BaseApiHandler.write_error` · *method*

## Summary:
Writes an error response containing a log message and HTTP status code to the client.

## Description:
Handles HTTP error responses by extracting error information from exception details and sending an appropriate response back to the client. This method is automatically invoked by Tornado when an HTTP error occurs during request processing. It writes the exception's log_message to the response body if available and non-empty, sets the HTTP status code, and completes the response.

## Args:
    status_code (int): The HTTP status code to send in the response.
    **kwargs: Additional keyword arguments, including 'exc_info' containing exception details.

## Returns:
    None: This method does not return a value.

## Raises:
    AttributeError: If exc_info is provided but does not contain the expected structure (exc_info[1] does not have log_message attribute).
    KeyError: If exc_info is provided but is malformed.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The method must be called within a Tornado web request context
    - When exc_info is provided, it should be a tuple of (exception_type, exception_instance, traceback)
    - The exception instance in exc_info[1] must have a log_message attribute
    
    Postconditions:
    - The HTTP response status is set to the provided status_code
    - The response body contains the log_message if available and truthy
    - The response is completed and sent to the client

## Side Effects:
    - Writes data to the HTTP response body via self.write() when log_message is truthy
    - Sets HTTP status code via self.set_status()
    - Finalizes the HTTP response via self.finish()

