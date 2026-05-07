# `flower.utils`

## Tree:
    - utils/
      - __init__.py
      - broker.py
      - search.py
      - tasks.py
      - template.py

## Role:
    - Centralized collection of utility functions and classes for common operations across the Flower application

## Description:
The utils module serves as a repository for reusable components that support various aspects of the Flower monitoring application. It provides utilities for broker connectivity, task management, search functionality, and template rendering. This module acts as a shared foundation that reduces code duplication and promotes consistency across different parts of the application.

The module is organized around functional areas:
- Broker utilities for connecting to different message brokers (RabbitMQ, Redis, etc.)
- Task-related utilities for processing and filtering task data
- Search functionality for filtering tasks based on various criteria
- Template utilities for formatting data for display

## Components:
    - abs_path (function): Converts a given path to an absolute path by expanding user references and joining with current working directory when necessary.
    - bugreport (function): Generates a formatted bug report string containing version information for Flower, Tornado, Humanize, and Celery dependencies.
    - gen_cookie_secret (function): Generates a cryptographically secure random cookie secret using UUID4 values encoded in base64 format.
    - prepend_url (function): Combines a URL path with a prefixed path segment, ensuring proper URL formatting with leading and trailing slash handling.
    - strtobool (function): Converts string representations of truth values to integer boolean equivalents (1 for true, 0 for false).
    - Broker (class): Abstract base class that serves as a factory for creating specific broker implementations based on URL scheme.
    - BrokerBase (class): Abstract base class for broker implementations that handles URL parsing and provides queue operation interface.
    - RabbitMQ (class): RabbitMQ broker implementation that interacts with RabbitMQ's management HTTP API to fetch queue information.
    - Redis (class): Redis is a concrete implementation of RedisBase that provides Redis broker functionality for queue management and statistics.
    - RedisBase (class): RedisBase is an abstract base class that provides Redis-specific broker functionality for queue management and statistics, inheriting from BrokerBase.
    - RedisSentinel (class): RedisSentinel is a Redis broker implementation that connects to Redis Sentinel for high availability and failover capabilities.
    - RedisSocket (class): RedisSocket is a Redis broker implementation that connects to Redis using Unix domain sockets instead of TCP connections.
    - RedisSsl (class): RedisSsl is a specialized Redis broker implementation that enables secure SSL/TLS connections to Redis servers.
    - parse_search_terms (function): Parses a raw search string into structured components based on prefixed keywords and quoted string handling.
    - preprocess_search_value (function): Strips quotation marks and whitespace from the beginning and end of a search value string.
    - satisfies_search_terms (function): Determines whether a task matches specified search criteria across multiple dimensions including state, result, arguments, and keyword arguments.
    - stringified_dict_contains_value (function): Checks if a stringified dictionary contains a specific key-value pair by parsing the string representation.
    - task_args_contains_search_args (function): Determines whether all specified search arguments are present in the task arguments collection.
    - as_dict (function): Converts a task object into a dictionary representation.
    - get_task_by_id (function): Retrieves a task object from the events state by its unique identifier.
    - iter_tasks (function): Generates filtered and sorted task records from event data, supporting pagination and multiple filter criteria.
    - sort_tasks (function): Generates tasks in sorted order based on a specified attribute, supporting both ascending and descending sort orders.
    - format_time (function): Formats a Unix timestamp with timezone information into a human-readable datetime string.
    - humanize (function): Transforms raw data objects into human-readable string representations with optional type-specific formatting and truncation.

## Public API:
    - abs_path(path: str) -> str: Converts a given path to an absolute path by expanding user references and joining with current working directory when necessary.
    - bugreport(app: celery.Celery, optional) -> str: Generates a formatted bug report string containing version information for Flower, Tornado, Humanize, and Celery dependencies.
    - gen_cookie_secret() -> bytes: Generates a cryptographically secure random cookie secret using UUID4 values encoded in base64 format.
    - prepend_url(url: str, prefix: str) -> str: Combines a URL path with a prefixed path segment, ensuring proper URL formatting with leading and trailing slash handling.
    - strtobool(val: str) -> int: Converts string representations of truth values to integer boolean equivalents (1 for true, 0 for false).
    - Broker(broker_url: str, *args, **kwargs) -> BrokerBase subclass instance: Factory method that creates and returns an instance of a specific broker implementation based on the URL scheme.
    - BrokerBase(broker_url: str) -> BrokerBase instance: Initializes a broker connection by parsing the broker URL and extracting connection parameters.
    - RabbitMQ(broker_url: str, http_api: str, io_loop: tornado.ioloop.IOLoop) -> RabbitMQ instance: Initializes a RabbitMQ broker connection with HTTP API configuration.
    - Redis(broker_url: str, *args, **kwargs) -> Redis instance: Initializes a Redis broker connection by setting default host/port values, preparing virtual host configuration, and establishing a Redis client instance.
    - RedisBase(broker_url: str, *args, **kwargs) -> RedisBase instance: Initializes a RedisBase instance with broker connection settings and configuration options.
    - RedisSentinel(broker_url: str, *args, **kwargs) -> RedisSentinel instance: Initializes a Redis Sentinel broker instance by setting up connection parameters and establishing a Redis client for master selection.
    - RedisSocket(broker_url: str, *args, **kwargs) -> RedisSocket instance: Initializes a RedisSocket broker connection by setting up Redis connection parameters and establishing a Redis client instance using Unix socket communication.
    - RedisSsl(broker_url: str, *args, **kwargs) -> RedisSsl instance: Initializes a RedisSsl broker connection with SSL configuration validation.
    - parse_search_terms(raw_search_value: str) -> dict: Parses a raw search string into structured components based on prefixed keywords and quoted string handling.
    - preprocess_search_value(raw_value: str) -> str: Strips quotation marks and whitespace from the beginning and end of a search value string.
    - satisfies_search_terms(task: object, search_terms: dict) -> bool: Determines whether a task matches specified search criteria across multiple dimensions including state, result, arguments, and keyword arguments.
    - stringified_dict_contains_value(key: str, value: Any, str_dict: str) -> bool: Checks if a stringified dictionary contains a specific key-value pair by parsing the string representation.
    - task_args_contains_search_args(task_args: iterable, search_args: iterable) -> bool: Determines whether all specified search arguments are present in the task arguments collection.
    - as_dict(task: object) -> dict: Converts a task object into a dictionary representation.
    - get_task_by_id(events: object, task_id: Any) -> object: Retrieves a task object from the events state by its unique identifier.
    - iter_tasks(events: object, limit: int, offset: int, type: str, worker: str, state: str, sort_by: str, received_start: str, received_end: str, started_start: str, started_end: str, search: dict) -> generator: Generates filtered and sorted task records from event data, supporting pagination and multiple filter criteria.
    - sort_tasks(tasks: iterable, sort_by: str) -> generator: Generates tasks in sorted order based on a specified attribute, supporting both ascending and descending sort orders.
    - format_time(time: float, tz: datetime.tzinfo) -> str: Formats a Unix timestamp with timezone information into a human-readable datetime string.
    - humanize(obj: Any, type: str, length: int) -> str: Transforms raw data objects into human-readable string representations with optional type-specific formatting and truncation.

## Dependencies:
    - Internal imports:
        - flower.utils.broker: Provides broker-related functionality for connecting to message brokers
        - flower.utils.search: Provides search and filtering utilities for task data
        - flower.utils.tasks: Provides task management utilities
        - flower.utils.template: Provides template formatting utilities
    - External imports:
        - os: Used for path manipulation in abs_path function
        - base64: Used for encoding cookie secrets
        - uuid: Used for generating random UUIDs in cookie secret generation
        - urllib.parse: Used for URL parsing in broker utilities
        - json: Used for JSON parsing in broker utilities
        - tornado.httpclient: Used for HTTP requests in RabbitMQ broker
        - tornado.ioloop: Used for asynchronous operations in broker utilities
        - redis: Used for Redis connection in Redis broker implementations
        - redis.sentinel: Used for Redis Sentinel connection in RedisSentinel broker
        - humanize: Used for natural time formatting in template utilities
        - celery: Used for version information in bugreport function

## Constraints:
    - All broker implementations must be instantiated through the Broker factory class to ensure proper polymorphism
    - Search terms parsing requires specific format with prefixed keywords (result:, args:, kwargs:, state:)
    - Task filtering functions expect specific data structures for search terms and task objects
    - Template formatting functions rely on consistent data types and structures for proper rendering
    - Cookie secret generation requires secure random number generation capabilities
    - Path resolution functions assume valid filesystem access and permissions
    - All utility functions should be stateless and idempotent where possible
    - Thread-safety considerations apply to broker connections which may need to be managed appropriately in concurrent environments

---

## Files

- [`__init__.py`](utils/__init__.md)
- [`broker.py`](utils/broker.md)
- [`search.py`](utils/search.md)
- [`tasks.py`](utils/tasks.md)
- [`template.py`](utils/template.md)

