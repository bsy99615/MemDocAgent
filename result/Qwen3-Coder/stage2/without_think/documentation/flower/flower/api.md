# `flower.api`

## Tree:
```
api/
├── __init__.py
├── control.py
├── tasks.py
└── workers.py
```

## Role:
Provides a RESTful web API interface for monitoring and controlling Celery distributed task queues through the Flower monitoring system.

## Description:
The flower/api module implements a comprehensive web API layer that enables monitoring and control of Celery workers and tasks. It serves as the primary interface for the Flower web application, exposing endpoints for task management, worker control, and system monitoring. This module is organized into logical groupings of related functionality: control operations for worker management, task operations for task lifecycle management, and worker listing for system overview.

The module is designed to integrate seamlessly with Tornado web framework and Celery task queue systems, providing both authenticated and unauthenticated access patterns depending on configuration. It follows a consistent pattern of inheritance from base API handlers that enforce authentication and provide common utility methods.

## Components:
*   `BaseApiHandler` - Base class for all API endpoints with authentication enforcement and error handling
*   `ControlHandler` - Utility base class for control-related API operations with worker validation
*   `TaskRateLimit` - API endpoint for setting rate limits on Celery tasks
*   `TaskRevoke` - API endpoint for revoking running Celery tasks
*   `TaskTimout` - API endpoint for configuring timeout settings for Celery tasks
*   `WorkerPoolAutoscale` - API endpoint for dynamically adjusting worker pool sizes
*   `WorkerPoolGrow` - API endpoint for increasing worker pool size
*   `WorkerPoolRestart` - API endpoint for restarting worker pools
*   `WorkerPoolShrink` - API endpoint for decreasing worker pool size
*   `WorkerQueueAddConsumer` - API endpoint for adding queue consumers to workers
*   `WorkerQueueCancelConsumer` - API endpoint for removing queue consumers from workers
*   `WorkerShutDown` - API endpoint for gracefully shutting down workers
*   `BaseTaskHandler` - Base class for task-related API operations with argument parsing and result handling
*   `GetQueueLengths` - API endpoint for retrieving queue length information from the broker
*   `ListTaskTypes` - API endpoint for listing all task types in the system
*   `ListTasks` - API endpoint for listing and filtering tasks from the event stream
*   `TaskAbort` - API endpoint for aborting running tasks
*   `TaskApply` - API endpoint for synchronously applying tasks
*   `TaskAsyncApply` - API endpoint for asynchronously applying tasks
*   `TaskInfo` - API endpoint for retrieving detailed task information
*   `TaskResult` - API endpoint for retrieving task results
*   `TaskSend` - API endpoint for sending tasks to Celery
*   `ListWorkers` - API endpoint for listing and managing worker information

## Public API:
*   `GET /api/task/types` - Lists all task types in the system
*   `GET /api/tasks` - Lists and filters tasks from the event stream
*   `GET /api/task/info/<task_id>` - Retrieves detailed information about a specific task
*   `GET /api/task/result/<task_id>` - Retrieves the result of a specific task
*   `POST /api/task/abort/<task_id>` - Aborts a running task
*   `POST /api/task/apply/<task_name>` - Synchronously applies a task
*   `POST /api/task/async-apply/<task_name>` - Asynchronously applies a task
*   `POST /api/task/send/<task_name>` - Sends a task to Celery
*   `POST /api/task/rate-limit/<task_name>` - Sets rate limits for a task
*   `POST /api/task/revoke/<task_id>` - Revokes a running task
*   `POST /api/task/timeout/<task_name>` - Sets timeout limits for a task
*   `POST /api/worker/autoscale/<worker_name>` - Configures autoscaling for a worker
*   `POST /api/worker/pool/grow/<worker_name>` - Increases worker pool size
*   `POST /api/worker/pool/restart/<worker_name>` - Restarts worker pool
*   `POST /api/worker/pool/shrink/<worker_name>` - Decreases worker pool size
*   `POST /api/worker/queue/add/<worker_name>` - Adds a queue consumer to a worker
*   `POST /api/worker/queue/cancel/<worker_name>` - Cancels a queue consumer from a worker
*   `POST /api/shutdown/<worker_name>` - Shuts down a worker
*   `GET /api/workers` - Lists all workers or specific worker information

## Dependencies:
*   Internal: `flower.app` - Provides application context and worker management
*   Internal: `flower.utils` - Contains utility functions for task and worker operations
*   External: `tornado.web` - Web framework for HTTP request handling
*   External: `celery` - Core Celery task queue functionality
*   External: `json` - Standard library for JSON serialization/deserialization
*   External: `logging` - Standard library for application logging

## Constraints:
*   All API endpoints require proper authentication unless `FLOWER_UNAUTHENTICATED_API` environment variable is set
*   Worker operations require valid worker names that exist in the application's worker registry
*   Task operations require valid task names that exist in the Celery application's task registry
*   All methods must be called within a Tornado web request context
*   Thread-safe: The API handlers are designed to be thread-safe as they don't maintain state between requests
*   Initialization: Requires proper Celery application configuration and worker registration

---

## Files

- [`__init__.py`](api/__init__.md)
- [`control.py`](api/control.md)
- [`tasks.py`](api/tasks.md)
- [`workers.py`](api/workers.md)

