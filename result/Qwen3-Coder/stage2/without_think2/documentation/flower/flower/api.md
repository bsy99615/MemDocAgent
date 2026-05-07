# `flower.api`

## Tree:
    api/
    ├── __init__.py
    ├── control.py
    ├── tasks.py
    └── workers.py

## Role:
    Provides a RESTful API interface for monitoring and controlling Celery-based distributed task processing systems through the Flower web application.

## Description:
The api module serves as the core web API layer for the Flower monitoring application, exposing endpoints for task management, worker control, and system monitoring. It provides both authenticated and unauthenticated access points for various operations including task execution, worker management, and queue inspection.

This module is organized around three primary categories:
1. Control endpoints for managing Celery workers and tasks (control.py)
2. Task-related operations including execution, querying, and monitoring (tasks.py)  
3. Worker information retrieval and management (workers.py)

The module leverages Tornado's web framework for request handling and integrates with Celery's control interface to provide real-time management capabilities for distributed task queues.

## Components:
    - BaseApiHandler: Abstract base class for API request handlers with authentication and error handling
    - ControlHandler: Base class for control-related API endpoints with worker validation utilities
    - TaskRateLimit: Configure rate limits for Celery tasks
    - TaskRevoke: Revoke running Celery tasks
    - TaskTimout: Set timeout limits for Celery tasks
    - WorkerPoolAutoscale: Configure worker pool autoscaling parameters
    - WorkerPoolGrow: Increase worker pool size
    - WorkerPoolRestart: Restart worker task pools
    - WorkerPoolShrink: Decrease worker pool size
    - WorkerQueueAddConsumer: Add queue consumers to workers
    - WorkerQueueCancelConsumer: Remove queue consumers from workers
    - WorkerShutDown: Shutdown specific worker processes
    - BaseTaskHandler: Base class for task-related API handlers with argument parsing and result formatting
    - GetQueueLengths: Retrieve current message queue lengths from broker
    - ListTaskTypes: Get list of task types observed by event system
    - ListTasks: List and filter Celery tasks from event stream
    - TaskAbort: Abort running tasks that support abortion
    - TaskApply: Execute tasks synchronously and return results
    - TaskAsyncApply: Execute tasks asynchronously and return task ID
    - TaskInfo: Get detailed information about specific tasks
    - TaskResult: Get current state and result of tasks
    - TaskSend: Send tasks for asynchronous execution
    - ListWorkers: Retrieve information about registered workers

## Public API:
    - POST /api/task/rate-limit/:taskname: Configure rate limits for a specific task
    - POST /api/task/revoke/:taskid: Revoke a running task
    - POST /api/task/timeout/:taskname: Set timeout limits for a specific task
    - POST /api/worker/autoscale/:workername: Configure worker pool autoscaling parameters
    - POST /api/worker/pool/grow/:workername: Increase worker pool size
    - POST /api/worker/pool/restart/:workername: Restart worker task pools
    - POST /api/worker/pool/shrink/:workername: Decrease worker pool size
    - POST /api/worker/queue/add/:workername: Add queue consumer to worker
    - POST /api/worker/queue/cancel/:workername: Remove queue consumer from worker
    - POST /api/shutdown/:workername: Shutdown a specific worker process
    - GET /api/queues/lengths: Retrieve current message queue lengths from broker
    - GET /api/task/types: Get list of task types observed by event system
    - GET /api/tasks: List and filter Celery tasks from event stream
    - POST /api/task/abort/:taskid: Abort a running task
    - POST /api/task/apply/:taskname: Execute a task synchronously and return results
    - POST /api/task/async-apply/:taskname: Execute a task asynchronously and return task ID
    - GET /api/task/info/:taskid: Get detailed information about a specific task
    - GET /api/task/result/:taskid: Get current state and result of a task
    - POST /api/task/send/:taskname: Send a task for asynchronous execution
    - GET /workers: Retrieve information about registered workers

## Dependencies:
    - Internal: flower.app, flower.utils
    - External: tornado.web, celery, logging

## Constraints:
    - All API endpoints require proper authentication unless FLOWER_UNAUTHENTICATED_API is set
    - Worker operations require valid worker names present in self.application.workers
    - Task operations require valid task names present in self.capp.tasks
    - Time-based parameters must be in valid formats (datetime strings or numeric values)
    - All external service calls to Celery workers must be handled with appropriate error recovery

---

## Files

- [`__init__.py`](api/__init__.md)
- [`control.py`](api/control.md)
- [`tasks.py`](api/tasks.md)
- [`workers.py`](api/workers.md)

