# `broker.py`

## `flower.views.broker.BrokerView` · *class*

## Summary:
A Tornado web handler that displays broker connection information and queue statistics for Celery workers.

## Description:
The BrokerView class handles HTTP GET requests to display information about the message broker configured for the Celery application. It authenticates users, connects to the appropriate broker based on configuration, retrieves queue information, and renders it in a web template. This view is primarily used in the Flower monitoring interface to provide visibility into broker connectivity and queue status.

## State:
- `self.application`: Tornado application instance containing broker configuration and worker information
- `self.capp`: Celery application instance accessed via property from the application
- `logger`: Logging instance for error reporting

## Lifecycle:
- Creation: Instantiated automatically by Tornado framework when handling HTTP requests
- Usage: Processes HTTP GET requests and generates HTML responses
- Destruction: Managed by Tornado framework lifecycle

## Method Map:
```mermaid
graph TD
    A[HTTP GET request] --> B[web.authenticated]
    B --> C[Get application reference]
    C --> D{Transport is AMQP?}
    D -->|Yes| E[Set http_api from options]
    D -->|No| F[http_api = None]
    F --> G[Create Broker instance]
    G --> H[Call broker.queues()]
    H --> I[Handle exceptions]
    I --> J[Render broker.html template]
```

## Raises:
- `web.HTTPError(404)`: Raised when the broker transport type is not supported (NotImplementedError from Broker constructor)
- Various exceptions from broker.queues() method that are caught and logged but not re-raised

## Example:
```python
# Typical usage in Tornado routing:
# app.add_handlers(r".*", [(r"/broker", BrokerView)])

# When accessed via browser:
# GET /broker (authenticated)
# Response: Renders broker.html with broker URL and queue information
```

### `flower.views.broker.BrokerView.get` · *method*

## Summary:
Retrieves broker queue information for display in the broker monitoring interface.

## Description:
Handles GET requests to the broker monitoring endpoint, establishing a connection to the configured broker and fetching queue information for active queues. This method serves as the backend for the broker.html template, providing real-time queue data for monitoring purposes.

This logic is separated into its own method to encapsulate the complex broker connection setup, queue retrieval, and error handling while maintaining clean separation between business logic and presentation concerns.

## Args:
    None

## Returns:
    None (renders HTTP response via self.render())

## Raises:
    tornado.web.HTTPError: Raised with status 404 when the configured broker transport is not supported (NotImplementedError from Broker constructor)

## State Changes:
    Attributes READ: 
    - self.application (transport, options.broker_api, capp)
    - self.application.capp.connection() 
    - self.application.capp.conf.broker_transport_options
    - self.application.capp.conf.broker_use_ssl
    - self.capp.conf.task_default_queue
    - self.capp.conf.task_queues
    - self.application.workers
    
    Attributes WRITTEN: 
    - None (method is read-only and does not modify instance state)

## Constraints:
    Preconditions:
    - self.application must have valid transport configuration
    - self.application.options must contain broker_api if transport is 'amqp'
    - self.application.capp must be properly initialized with a valid Celery app
    - self.application.workers must contain valid worker information
    
    Postconditions:
    - The method will render broker.html template with queue data
    - If queue retrieval fails, the queues parameter passed to render will be None or empty list
    - Broker connection will be established with appropriate timeout settings

## Side Effects:
    - Establishes network connections to broker management API (for AMQP brokers)
    - Makes HTTP requests to broker management endpoints
    - Logs errors to application logger when queue retrieval fails
    - Renders HTML template with broker information

