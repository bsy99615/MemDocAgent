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
    - Provides web interface components for monitoring and managing Celery task queues and workers

## Description:
The flower/views module implements the web interface layer for the Flower monitoring tool, offering a comprehensive set of HTTP endpoints for monitoring Celery task queues, workers, and task execution. This module serves as the primary user-facing interface for interacting with the distributed task processing system.

The module is organized around distinct functional areas:
- Authentication handlers for various OAuth providers (GitHub, GitLab, Google, Okta)
- Broker monitoring for message queue connections
- Task management and inspection capabilities
- Worker status monitoring and management
- System monitoring and health checks
- Error handling for invalid routes

This separation allows for modular development and clear boundaries between different aspects of the monitoring interface while maintaining cohesive integration through the BaseHandler base class that provides common functionality like authentication, argument parsing, and template rendering.

## Components:
    - BaseHandler: Core web request handler with authentication, argument parsing, and template rendering
    - LoginHandler: Factory that delegates to configurable authentication providers
    - Auth handlers (GithubLoginHandler, GitLabLoginHandler, GoogleAuth2LoginHandler, OktaLoginHandler): OAuth2 authentication implementations for various identity providers
    - BrokerView: Displays broker connection and queue information
    - NotFoundErrorHandler: Handles requests to non-existent routes with 404 responses
    - Healthcheck: Simple monitoring endpoint returning "OK"
    - Metrics: Exposes Prometheus metrics for monitoring
    - TaskView: Displays detailed information for a specific task
    - TasksDataTable: Provides task data in DataTables-compatible JSON format
    - TasksView: Main tasks dashboard page
    - WorkerView: Displays detailed information for a specific worker
    - WorkersView: Shows list of all workers with status information

## Public API:
    - BaseHandler: Base class for all web views, providing common functionality
    - LoginHandler: Factory for authentication handlers
    - GithubLoginHandler: GitHub OAuth2 authentication endpoint
    - GitLabLoginHandler: GitLab OAuth2 authentication endpoint
    - GoogleAuth2LoginHandler: Google OAuth2 authentication endpoint
    - OktaLoginHandler: Okta OAuth2 authentication endpoint
    - BrokerView: Broker connection and queue monitoring
    - NotFoundErrorHandler: 404 error handler for invalid routes
    - Healthcheck: Health monitoring endpoint
    - Metrics: Prometheus metrics endpoint
    - TaskView: Individual task detail view
    - TasksDataTable: DataTables-compatible task data API
    - TasksView: Main tasks dashboard
    - WorkerView: Individual worker detail view
    - WorkersView: Worker list and status view

## Dependencies:
    - Internal: celery.utils.imports (for dynamic authentication provider instantiation)
    - Internal: tornado.web, tornado.auth (for web request handling and OAuth mixins)
    - Internal: tornado.escape (for XSS protection)
    - External: prometheus_client (for metrics endpoint)
    - External: tornado (for web framework components)

## Constraints:
    - All views must inherit from BaseHandler for consistent authentication and functionality
    - Most views require authentication, except for healthcheck and metrics endpoints
    - Views must properly handle CORS headers when authentication is disabled
    - All authentication handlers must follow OAuth2 flow standards
    - Task and worker views require valid identifiers to avoid 404 errors
    - Metrics endpoint requires prometheus_client to be properly configured

---

## Files

- [`__init__.py`](views/__init__.md)
- [`auth.py`](views/auth.md)
- [`broker.py`](views/broker.md)
- [`error.py`](views/error.md)
- [`monitor.py`](views/monitor.md)
- [`tasks.py`](views/tasks.md)
- [`workers.py`](views/workers.md)

