# `broker.py`

## `flower.views.broker.BrokerView` · *class*

## Summary:
BrokerView is a web handler that displays broker queue information for the Flower monitoring dashboard, providing a web interface to view active queues and their statistics.

## Description:
This class implements a GET endpoint that retrieves and displays queue information from the configured message broker. It serves as part of the Flower monitoring interface, allowing users to inspect the state of message queues in their Celery setup. The view handles different broker types (AMQP/RabbitMQ, Redis, etc.) through the Broker factory pattern and provides authentication protection.

The view specifically targets AMQP brokers for HTTP API integration, and gracefully handles cases where the broker type is unsupported or queue retrieval fails. It renders a template with broker connection details and queue statistics for display in the browser.

## State:
- `application`: Reference to the Tornado application instance containing configuration and shared resources
- `capp`: Property inherited from BaseHandler that provides access to the Celery application instance
- `request`: Inherited from RequestHandler, contains the HTTP request information
- `response`: Inherited from RequestHandler, contains the HTTP response information

## Lifecycle:
Creation: Instances are automatically created by Tornado's routing mechanism when HTTP GET requests are made to the broker view endpoint. The constructor is inherited from RequestHandler and doesn't require special instantiation.

Usage: When a GET request is received:
1. Authentication is verified via the @web.authenticated decorator
2. Application transport and broker API configuration is checked
3. A Broker instance is created based on the configured broker URL
4. Queue information is fetched asynchronously from the broker
5. Template is rendered with broker URL and queue data

Destruction: Cleanup is handled automatically by Tornado's request lifecycle management.

## Method Map:
```mermaid
graph TD
    A[GET request] --> B[@web.authenticated]
    B --> C[app = self.application]
    C --> D[http_api = None]
    D --> E[if app.transport == 'amqp' and app.options.broker_api]
    E --> F[broker = Broker(...)]
    F --> G[try broker.queues()]
    G --> H[except Exception]
    H --> I[logger.error("Unable to get queues")]
    I --> J[self.render("broker.html", ...)]
```

## Raises:
- tornado.web.HTTPError(404): Raised when the configured broker transport type is not supported (NotImplementedError from Broker constructor)
- Exception: Caught and logged when queue retrieval fails, but not re-raised (graceful degradation)

## Example:
```python
# Accessing the broker view endpoint
# GET /broker

# This would render the broker.html template with:
# - broker_url: Connection URL to the broker
# - queues: Queue statistics from the broker
```

### `flower.views.broker.BrokerView.get` · *method*

## Summary:
Retrieves and displays broker queue information for the web dashboard, supporting AMQP and various Redis-based brokers.

## Description:
This asynchronous method handles GET requests to the broker view endpoint, fetching queue statistics from the configured message broker and rendering them in a web template. It dynamically selects the appropriate broker implementation based on the application's transport configuration and handles both AMQP (RabbitMQ) and Redis-based brokers.

The method orchestrates the creation of a broker client, retrieves active queue information, and renders a template displaying broker connection details and queue statistics. It specifically supports AMQP brokers with HTTP API integration and gracefully handles unsupported broker types by returning a 404 error.

## Args:
    None

## Returns:
    None

## Raises:
    tornado.web.HTTPError: Raised with status code 404 when the configured broker transport is not supported (e.g., unsupported scheme in broker URL)

## State Changes:
    Attributes READ: 
    - self.application: Used to access transport configuration and options
    - self.capp: Used to access Celery application configuration and connection details
    - self.capp.conf: Used to access broker transport options and SSL settings
    - self.application.workers: Implicitly accessed through get_active_queue_names() method

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.application.transport must be a string indicating the broker type (e.g., 'amqp', 'redis')
    - self.application.options.broker_api must be accessible if transport is 'amqp'
    - self.capp must be properly initialized with a valid Celery application instance
    - self.capp.conf.broker_transport_options must be accessible
    - self.capp.conf.broker_use_ssl must be accessible
    - self.get_active_queue_names() must return a list of queue names

    Postconditions:
    - The method completes successfully when a supported broker is configured
    - The rendered template receives valid broker_url and queues data
    - If broker.queues() fails, the error is logged but execution continues
    - The HTTP response contains rendered HTML template

## Side Effects:
    - Makes network connections to the configured message broker
    - Calls external broker APIs (when AMQP with broker_api is configured)
    - Logs error messages to the application logger when queue retrieval fails
    - Renders HTML template with broker information

