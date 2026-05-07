# `flower.views`

## Tree:
    - views/
      - __init__.py
      - auth.py
      - broker.py
      - error.py
      - monitor.py
      - tasks.py
      - workers.py

## Role:
    - Provides web interface handlers for Flower's monitoring dashboard, including authentication, task management, worker monitoring, and broker inspection

## Description:
    - The views module implements the web interface layer for the Flower monitoring application, handling HTTP requests and rendering templates for monitoring Celery tasks, workers, and brokers.
    - Primary consumers include the Tornado web framework through URL routing, and end-users accessing the Flower dashboard via web browsers.
    - Components are grouped by functionality: authentication handlers, task monitoring, worker status, broker inspection, and error handling, reflecting a clear separation of concerns in the web interface.

## Components:
    - BaseHandler: Core web request handler with authentication, CORS, and utility methods
    - GitLabLoginHandler: OAuth2 authentication with GitLab
    - GithubLoginHandler: OAuth2 authentication with GitHub
    - GoogleAuth2LoginHandler: OAuth2 authentication with Google
    - LoginHandler: Dynamic authentication provider factory
    - OktaLoginHandler: OAuth2 authentication with Okta
    - authenticate: Email pattern validation utility
    - validate_auth_option: Authentication pattern validation utility
    - BrokerView: Displays broker queue information
    - NotFoundErrorHandler: Returns 404 errors for undefined routes
    - Healthcheck: Simple health check endpoint
    - Metrics: Exposes Prometheus metrics for monitoring
    - Comparable: Wrapper for safe comparison of heterogeneous objects
    - TaskView: Renders detailed task information
    - TasksDataTable: Server-side DataTables API for task listings
    - TasksView: Renders the main tasks dashboard
    - WorkerView: Displays detailed worker information
    - WorkersView: Shows list of workers with status information

## Public API:
    - BaseHandler: Core web handler with authentication and utility methods
    - GitLabLoginHandler: OAuth2 login with GitLab
    - GithubLoginHandler: OAuth2 login with GitHub
    - GoogleAuth2LoginHandler: OAuth2 login with Google
    - LoginHandler: Dynamic authentication provider factory
    - OktaLoginHandler: OAuth2 login with Okta
    - authenticate: Validates email against authentication patterns
    - validate_auth_option: Validates authentication pattern syntax
    - BrokerView: Displays broker queue information
    - NotFoundErrorHandler: 404 error handler
    - Healthcheck: Health check endpoint
    - Metrics: Prometheus metrics endpoint
    - Comparable: Safe comparison wrapper
    - TaskView: Task detail view
    - TasksDataTable: DataTables API for tasks
    - TasksView: Tasks dashboard view
    - WorkerView: Worker detail view
    - WorkersView: Workers list view

## Dependencies:
    - Internal: celery.utils.imports, tornado.auth, tornado.web, flower.views.error
    - External: tornado, prometheus_client

## Constraints:
    - All handlers inherit from BaseHandler for consistent behavior
    - Authentication decorators must be respected for protected endpoints
    - Handlers must properly manage HTTP response headers and status codes
    - Thread safety: Handlers are stateless and designed for concurrent access

---

## Files

- [`__init__.py`](views/__init__.md)
- [`auth.py`](views/auth.md)
- [`broker.py`](views/broker.md)
- [`error.py`](views/error.md)
- [`monitor.py`](views/monitor.md)
- [`tasks.py`](views/tasks.md)
- [`workers.py`](views/workers.md)

