# `broker.py`

## `flower.views.broker.BrokerView` · *class*

## Summary:
BrokerView is a Tornado web handler that displays broker connection information and queue statistics for the Celery task queue system.

## Description:
BrokerView provides a web interface for monitoring broker connections and queue information in a Celery-based distributed task queue system. It serves as a dashboard endpoint that displays the current broker URL and lists available queues with their statistics. The view requires authentication and supports different broker types through the Broker factory class.

This class exists as a distinct abstraction to separate the presentation layer from the broker integration logic, providing a clean interface for users to inspect their message broker configuration and queue status without requiring direct command-line access or API calls.

## State:
- `application`: Tornado application instance containing Celery configuration and shared resources (inherited from BaseHandler)
- `request`: Current HTTP request being processed (inherited from BaseHandler)
- `capp`: Celery application instance accessed via application.capp (inherited from BaseHandler)
- `logger`: Logging instance for error reporting (inherited from BaseHandler)

## Lifecycle:
- Creation: Instantiated automatically by Tornado framework when handling HTTP GET requests to the broker view endpoint
- Usage: Called during normal HTTP request processing when authenticated users access the broker monitoring page
- Destruction: Managed automatically by Tornado framework

## Method Map:
```mermaid
graph TD
    A[get] --> B[application]
    B --> C[transport check]
    C --> D{AMQP + broker_api?}
    D -->|Yes| E[http_api = broker_api]
    D -->|No| F[http_api = None]
    F --> G[Broker instantiation]
    G --> H[broker.queues()]
    H --> I[render broker.html]
    E --> G
    G --> J[Exception handling]
    J --> K{NotImplementedError?}
    K -->|Yes| L[HTTPError 404]
    K -->|No| M[logger.error]
```

## Raises:
- tornado.web.HTTPError: Raised with status code 404 when the broker transport type is not supported (e.g., unsupported broker scheme)
- Exception: Caught and logged as error when broker.queues() fails for any reason

## Example:
```python
# Accessing the broker view endpoint
# User navigates to /broker in browser (authenticated)
# Response includes:
# - broker_url: Connection string for the broker
# - queues: List of queue information with statistics
```

### `flower.views.broker.BrokerView.get` · *method*

## Summary:
Retrieves and displays broker queue information for the web UI, handling different broker transports and providing fallback mechanisms.

## Description:
This asynchronous method processes GET requests to display broker queue information in the Flower web interface. It constructs a broker connection based on the application's transport configuration, fetches queue data from the broker, and renders the results in a template. The method specifically handles AMQP brokers with HTTP API support and provides appropriate error handling for unsupported broker types.

The method is part of the BrokerView class and is decorated with @web.authenticated, ensuring only authenticated users can access broker information. It integrates with the Celery application's connection management and leverages the Broker factory pattern to support multiple broker types.

## Args:
    None

## Returns:
    None (renders broker.html template with broker information)

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when the configured broker transport is not supported (NotImplementedError from Broker class)

## State Changes:
    Attributes READ:
    - self.application: Contains transport and options configuration
    - self.capp.conf: Contains broker transport options and SSL settings
    - self.application.workers: Used indirectly via get_active_queue_names() method
    - self.capp.conf.task_default_queue: Used indirectly via get_active_queue_names() method
    - self.capp.conf.task_queues: Used indirectly via get_active_queue_names() method

    Attributes WRITTEN:
    - None

## Constraints:
    Preconditions:
    - self.application must have transport and options attributes
    - self.capp must have a valid connection method and conf attribute
    - self.capp.conf must contain broker_transport_options, broker_use_ssl, task_default_queue, and task_queues attributes
    - Application must have workers with active_queues information for get_active_queue_names() to function properly

    Postconditions:
    - The method will always attempt to render the broker.html template
    - If queue fetching fails, the queues parameter passed to the template will be None or empty
    - Broker connection is created with proper timeout and SSL settings

## Side Effects:
    - Makes network connections to the message broker (AMQP, Redis, etc.)
    - Calls external services when broker_api is configured for AMQP
    - Logs error messages when queue fetching fails
    - Renders HTML template with broker information

