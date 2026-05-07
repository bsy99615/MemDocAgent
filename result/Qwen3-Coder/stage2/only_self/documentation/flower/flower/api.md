# `flower.api`

## Tree:
    - api/
      - __init__.py
      - control.py
      - tasks.py
      - workers.py

## Role:
    - Single-responsibility description: Provides RESTful API endpoints for monitoring and controlling Celery workers and tasks within the Flower application

## Description:
    - Describe where and when this module is used within the repo: This module serves as the core API layer for the Flower monitoring interface, providing HTTP endpoints for managing Celery workers and tasks. It is consumed by the Tornado web framework to handle API requests and by the Flower web UI for real-time monitoring and control operations.

    - Explain why these components are grouped into a separate module: The components are grouped together because they all serve the common purpose of exposing Flower's monitoring and control capabilities through a standardized RESTful API. They share common authentication requirements, error handling patterns, and integration with Celery's control interfaces, making them logically cohesive under a single API module.

## Components:
    - BaseApiHandler: Abstract base class providing authentication enforcement and error handling for API endpoints
    - ControlHandler: Base class for control operations that validates worker existence and extracts error information
    - TaskRateLimit: Handles setting rate limits for Celery tasks
    - TaskRevoke: Manages revocation of running Celery tasks
    - TaskTimout: Configures timeout settings for Celery tasks
    - WorkerPoolAutoscale: Adjusts worker pool size scaling parameters
    - WorkerPoolGrow: Increases the number of worker processes in a pool
    - WorkerPoolRestart: Restarts a worker's task processing pool
    - WorkerPoolShrink: Decreases the number of worker processes in a pool
    - WorkerQueueAddConsumer: Adds queue consumers to specific workers
    - WorkerQueueCancelConsumer: Removes queue consumers from specific workers
    - WorkerShutDown: Terminates specific Celery worker processes
    - BaseTaskHandler: Abstract base class for task-related API endpoints with common utilities
    - GetQueueLengths: Retrieves current queue length information from the message broker
    - ListTaskTypes: Returns a list of all task types observed by the monitoring system
    - ListTasks: Lists tasks with optional filtering and sorting capabilities
    - TaskAbort: Aborts running Celery tasks that support abortion
    - TaskApply: Invokes Celery tasks asynchronously and returns results
    - TaskAsyncApply: Submits Celery tasks asynchronously and returns task IDs
    - TaskInfo: Retrieves detailed information about specific Celery tasks
    - TaskResult: Fetches current state and result data for specific Celery tasks
    - TaskSend: Sends Celery tasks to the broker for asynchronous execution
    - ListWorkers: Retrieves information about registered Celery workers

## Public API:
    - BaseApiHandler: Abstract base class for API endpoints with authentication enforcement
    - ControlHandler: Base class for control operations with worker validation
    - TaskRateLimit: POST /api/task/rate-limit/{taskname} - Set rate limits for tasks
    - TaskRevoke: POST /api/task/revoke/{taskid} - Revoke running tasks
    - TaskTimout: POST /api/task-timeout/{taskname} - Configure timeout settings for tasks
    - WorkerPoolAutoscale: POST /api/worker/autoscale/{workername} - Adjust worker pool autoscaling
    - WorkerPoolGrow: POST /api/worker/pool/grow/{workername} - Increase worker pool size
    - WorkerPoolRestart: POST /api/worker/pool/restart/{workername} - Restart worker pool
    - WorkerPoolShrink: POST /api/worker/pool/shrink/{workername} - Decrease worker pool size
    - WorkerQueueAddConsumer: POST /api/worker/queue/add/{workername} - Add queue consumer to worker
    - WorkerQueueCancelConsumer: POST /api/worker/queue/cancel/{workername} - Remove queue consumer from worker
    - WorkerShutDown: POST /api/shutdown/{workername} - Shut down specific worker
    - GetQueueLengths: GET /api/queues/lengths - Retrieve queue length information
    - ListTaskTypes: GET /api/task/types - List all observed task types
    - ListTasks: GET /api/tasks - List tasks with filtering and sorting
    - TaskAbort: POST /api/task/abort/{taskid} - Abort running tasks
    - TaskApply: POST /api/task/apply/{taskname} - Apply tasks synchronously
    - TaskAsyncApply: POST /api/task/async-apply/{taskname} - Apply tasks asynchronously
    - TaskInfo: GET /api/task/info/{taskid} - Get detailed task information
    - TaskResult: GET /api/task/result/{taskid} - Get task result and state
    - TaskSend: POST /api/task/send/{taskname} - Send tasks to broker
    - ListWorkers: GET /api/workers - List registered workers

## Dependencies:
    - Internal imports: 
        - flower.app: For accessing Celery application instance and worker information
        - flower.utils: For utility functions and logging
        - tornado.web: For web handler base classes and decorators
        - celery.states: For task state constants
    - External imports:
        - tornado.web: For Tornado web framework components and decorators
        - celery: For Celery task management and control interfaces
        - json: For JSON serialization/deserialization
        - logging: For application logging

## Constraints:
    - All API endpoints require proper authentication unless FLOWER_UNAUTHENTICATED_API is enabled
    - Worker names must be validated against registered workers before control operations
    - Task names must exist in the Celery application's task registry
    - Backend configuration must be properly set up for result retrieval operations
    - Thread-safety: All handlers are designed to be thread-safe as they operate on immutable request data
    - Ordering requirements: Control operations should be performed in logical sequence (validate, then execute)
    - Initialization prerequisites: Application must be properly configured with Celery and event tracking enabled

---

## Files

- [`__init__.py`](api/__init__.md)
- [`control.py`](api/control.md)
- [`tasks.py`](api/tasks.md)
- [`workers.py`](api/workers.md)

