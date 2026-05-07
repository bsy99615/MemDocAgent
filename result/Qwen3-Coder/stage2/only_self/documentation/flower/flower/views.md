# `flower.views`

## Tree:
views/
├── __init__.py
├── auth.py
├── broker.py
├── error.py
├── monitor.py
├── tasks.py
└── workers.py

## Role:
Provides web interface components for monitoring and managing Celery task queues through a Tornado-based web application.

## Description:
The flower/views module implements the web interface layer for the Flower monitoring application. It provides HTTP endpoints and views for monitoring Celery workers, tasks, and brokers, along with authentication mechanisms and error handling. This module serves as the primary user-facing interface for interacting with the Flower monitoring system.

The module is organized around core monitoring concepts: workers (task executors), tasks (individual units of work), and brokers (message queues). It also includes authentication handlers for securing access to monitoring features and error handlers for managing invalid requests.

## Components:
- BaseHandler: Foundation class for all web request handlers with common functionality
- LoginHandler: Factory class for selecting authentication providers
- Auth handlers (GithubLoginHandler, GitLabLoginHandler, GoogleAuth2LoginHandler, OktaLoginHandler): OAuth2 authentication implementations
- BrokerView: Displays broker queue information
- NotFoundErrorHandler: Handles 404 errors for undefined routes
- Healthcheck: Provides service health monitoring endpoint
- Metrics: Exposes Prometheus metrics for monitoring
- TaskView: Displays individual task details
- TasksView: Renders task listing dashboard
- TasksDataTable: Provides JSON data for DataTables UI component
- WorkerView: Displays individual worker statistics
- WorkersView: Renders worker listing dashboard

## Public API:
- `BaseHandler`: Base class for all web views, providing common functionality like authentication, CORS handling, and task formatting
- `LoginHandler`: Factory class that dynamically instantiates authentication providers based on configuration
- `GithubLoginHandler`, `GitLabLoginHandler`, `GoogleAuth2LoginHandler`, `OktaLoginHandler`: OAuth2 authentication handlers for different identity providers
- `BrokerView`: GET endpoint for displaying broker queue information
- `NotFoundErrorHandler`: 404 error handler for undefined routes
- `Healthcheck`: GET endpoint for service health monitoring
- `Metrics`: GET endpoint for Prometheus metrics exposure
- `TaskView`: GET endpoint for individual task details
- `TasksView`: GET endpoint for task listing dashboard
- `TasksDataTable`: GET/POST endpoints for DataTables JSON data source
- `WorkerView`: GET endpoint for individual worker statistics
- `WorkersView`: GET endpoint for worker listing dashboard

## Dependencies:
- Internal: 
  - `flower.utils`: For task-related utilities and data processing
  - `flower.app`: For application configuration and Celery integration
- External:
  - `tornado.web`: For Tornado web framework components
  - `tornado.auth`: For OAuth2 authentication mixins
  - `tornado.httpclient`: For HTTP client operations
  - `prometheus_client`: For metrics exposure
  - `celery`: For Celery task and worker integration

## Constraints:
- All views must be properly authenticated when authentication is enabled
- Views that access Celery data require a properly configured Celery application instance
- Authentication handlers must be configured with appropriate OAuth settings
- The BaseHandler provides shared functionality but requires proper inheritance
- Views that depend on worker data must have access to the application's event system
- Thread-safety: Views are stateless and rely on Tornado's request-scoped state management
- Ordering requirements: Authentication must be handled before data access in most views

---

## Files

- [`__init__.py`](views/__init__.md)
- [`auth.py`](views/auth.md)
- [`broker.py`](views/broker.md)
- [`error.py`](views/error.md)
- [`monitor.py`](views/monitor.md)
- [`tasks.py`](views/tasks.md)
- [`workers.py`](views/workers.md)

