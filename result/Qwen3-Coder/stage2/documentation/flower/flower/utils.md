# `flower.utils`

## Tree:
```
utils/
├── __init__.py
├── broker.py
├── search.py
├── tasks.py
└── template.py
```

## Role:
Provides utility functions and classes for common operations in the Flower monitoring system, including broker integration, task management, search functionality, and template rendering utilities.

## Description:
The flower/utils module serves as a centralized repository for utility functions and classes that support various aspects of the Flower monitoring system. It encapsulates common operations needed across different parts of the application, promoting code reuse and maintaining clean separation of concerns.

This module is organized around functional areas:
- Broker integration utilities for connecting to different message brokers (AMQP, Redis, etc.)
- Task management and filtering capabilities
- Search and filtering mechanisms for task queries
- Template rendering helpers for displaying data in web interfaces

The module is consumed by various parts of the Flower application including the web UI, command-line tools, and internal monitoring components.

## Components:
- **Broker**: Factory class that returns specific broker implementations based on URL scheme, supporting AMQP, Redis, Redis SSL, Redis Socket, and Redis Sentinel protocols
- **BrokerBase**: Abstract base class for broker implementations that handles URL parsing and provides a common interface for queue operations
- **RabbitMQ**: Implements broker functionality for RabbitMQ message brokers using the management HTTP API
- **Redis**: Implements Redis-based broker functionality that handles connection setup and client creation for Redis message queues
- **RedisBase**: Abstract base class that provides Redis-specific broker functionality for handling message queues with priority support
- **RedisSentinel**: Implements Redis broker functionality that connects to Redis Sentinel for high availability and failover capabilities
- **RedisSocket**: Implements Redis broker functionality that connects to Redis via Unix domain socket for message queue operations
- **RedisSsl**: Implements SSL-enabled Redis broker functionality that enables encrypted connections to Redis servers
- **parse_search_terms**: Parses search strings into structured search terms for filtering tasks
- **preprocess_search_value**: Normalizes search input values by stripping quotation marks and whitespace
- **satisfies_search_terms**: Determines if a task matches search criteria across multiple dimensions
- **stringified_dict_contains_value**: Checks if a stringified dictionary contains a specific key-value pair
- **task_args_contains_search_args**: Checks if task arguments contain specified search arguments
- **as_dict**: Converts task objects to dictionary representation for serialization or display
- **get_task_by_id**: Retrieves a specific task by ID from event data
- **iter_tasks**: Generates filtered and sorted task records with pagination support
- **sort_tasks**: Sorts tasks by specified attributes with support for ascending and descending orders
- **format_time**: Formats Unix timestamps into human-readable datetime strings with timezone information
- **humanize**: Transforms objects into human-readable strings with optional type-specific processing and length limiting

## Public API:
- **abs_path(path)**: Converts a given path to an absolute path
- **bugreport(app=None)**: Generates a formatted bug report string with version information
- **gen_cookie_secret()**: Generates a cryptographically secure cookie secret
- **prepend_url(url, prefix)**: Constructs a URL path by combining a prefix with a URL path
- **strtobool(val)**: Converts a string representation of truth to a numeric boolean value
- **Broker(broker_url, *args, **kwargs)**: Factory class that returns specific broker implementations based on URL scheme
- **parse_search_terms(raw_search_value)**: Parses search strings into structured terms
- **preprocess_search_value(raw_value)**: Normalizes search input values
- **satisfies_search_terms(task, search_terms)**: Determines if a task matches search criteria
- **stringified_dict_contains_value(key, value, str_dict)**: Checks if a stringified dict contains a key-value pair
- **task_args_contains_search_args(task_args, search_args)**: Checks if task arguments contain search arguments
- **as_dict(task)**: Converts task objects to dictionary representation
- **get_task_by_id(events, task_id)**: Retrieves a specific task by ID from event data
- **iter_tasks(events, limit=None, offset=0, type=None, worker=None, state=None, sort_by=None, received_start=None, received_end=None, started_start=None, started_end=None, search=None)**: Generates filtered and sorted task records
- **sort_tasks(tasks, sort_by)**: Sorts tasks by specified attributes
- **format_time(time, tz)**: Formats Unix timestamps into human-readable datetime strings
- **humanize(obj, type=None, length=None)**: Transforms objects into human-readable strings

## Dependencies:
- **Internal imports**:
  - `flower.utils.broker`: Provides broker-related functionality for message queue integration
  - `flower.utils.search`: Provides search and filtering utilities for task queries
  - `flower.utils.tasks`: Provides task management and iteration utilities
  - `flower.utils.template`: Provides template rendering and formatting utilities
- **External imports**:
  - `base64`: For generating secure cookie secrets
  - `os`: For path manipulation and environment variable access
  - `urllib.parse`: For URL parsing and manipulation
  - `uuid`: For generating cryptographically secure identifiers
  - `pytz`: For timezone handling in time formatting
  - `humanize`: For natural time formatting
  - `redis`: For Redis broker integration
  - `tornado`: For asynchronous I/O operations
  - `celery`: For Celery application integration

## Constraints:
- All utility functions should be stateless and not modify external state
- Broker-related functions must handle connection failures gracefully
- Search functions should be efficient and avoid unnecessary computation
- Time formatting functions must handle timezone conversions properly
- All path manipulation functions should normalize paths correctly
- Cookie secret generation must use cryptographically secure random sources
- Thread-safety: Most utilities are stateless and thus inherently thread-safe
- Initialization prerequisites: Some components require specific environment variables or external dependencies to be available

---

## Files

- [`__init__.py`](utils/__init__.md)
- [`broker.py`](utils/broker.md)
- [`search.py`](utils/search.md)
- [`tasks.py`](utils/tasks.md)
- [`template.py`](utils/template.md)

