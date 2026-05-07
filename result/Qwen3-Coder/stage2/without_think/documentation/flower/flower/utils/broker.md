# `broker.py`

## `flower.utils.broker.BrokerBase` · *class*

## Summary:
Abstract base class for broker implementations that handles URL parsing and provides a common interface for queue operations.

## Description:
BrokerBase serves as the foundation for concrete broker implementations in a distributed messaging system. It parses broker connection URLs to extract connection parameters and defines the interface for queue-related operations. This class should not be instantiated directly but rather extended by specific broker implementations such as RedisBroker or RabbitMQBroker.

The class is designed to work in asynchronous environments and provides a standardized way to handle broker connection details while leaving the specific queue operation implementations to derived classes.

## State:
- host (str): Hostname extracted from the broker URL; can be None if not specified in URL
- port (int): Port number extracted from the broker URL; can be None if not specified in URL  
- vhost (str): Virtual host path extracted from the URL path component (without leading slash)
- username (str): Username from URL, URL-decoded if present; can be None
- password (str): Password from URL, URL-decoded if present; can be None

All attributes are initialized during construction and remain immutable throughout the object's lifetime.

## Lifecycle:
- Creation: Instantiate by providing a broker URL string to the constructor
- Usage: Subclasses should implement the `queues` method and use the parsed connection parameters
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[BrokerBase.__init__] --> B[BrokerBase.queues]
    B --> C[Subclass Implementation]
```

## Raises:
- No explicit exceptions raised by __init__ method itself
- The `queues` method raises NotImplementedError when called directly

## Example:
```python
# This would be used as a base class
class RedisBroker(BrokerBase):
    async def queues(self, names):
        # Implementation specific to Redis
        pass

# Usage:
broker = RedisBroker("redis://user:pass@localhost:6379/0")
# The broker now has host="localhost", port=6379, vhost="0"
# username="user", password="pass" 
```

### `flower.utils.broker.BrokerBase.__init__` · *method*

## Summary:
Initializes a broker connection by parsing the broker URL and extracting connection parameters.

## Description:
This method serves as the constructor for the BrokerBase class, responsible for parsing a broker connection URL and extracting essential connection parameters including hostname, port, virtual host, username, and password. The method handles URL decoding for credentials to ensure proper authentication.

## Args:
    broker_url (str): The broker connection URL containing protocol, hostname, port, virtual host, username, and password information.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None explicitly raised: The method does not raise any exceptions directly, though malformed URLs could cause urlparse to behave unexpectedly.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.host: Extracted from URL hostname component
    - self.port: Extracted from URL port component  
    - self.vhost: Extracted from URL path component (without leading slash)
    - self.username: Extracted from URL username component, URL-decoded if present
    - self.password: Extracted from URL password component, URL-decoded if present

## Constraints:
    Preconditions:
    - broker_url must be a valid string representing a URL
    - The URL should follow standard format with optional username/password components
    
    Postconditions:
    - All connection parameters are properly extracted and stored as instance attributes
    - Username and password are URL-decoded if present, otherwise remain as-is

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only processes the input URL and stores parsed values as instance attributes.

### `flower.utils.broker.BrokerBase.queues` · *method*

## Summary:
Asynchronously retrieves detailed information about specified queues from the broker system.

## Description:
This abstract method defines the interface for fetching queue metadata and properties from a message broker. It serves as a contract that concrete broker implementations (RedisBroker, RabbitMQBroker, etc.) must fulfill to provide queue inspection capabilities. The method enables clients to query information about multiple queues simultaneously, returning structured data about each requested queue's properties.

## Args:
    names (list[str]): A list of queue names for which to retrieve information.

## Returns:
    dict: A dictionary mapping each queue name to its corresponding queue information structure. Typical implementations return queue metadata including message counts, consumer counts, and queue status information.

## Raises:
    NotImplementedError: This abstract method must be implemented by concrete broker subclasses to provide broker-specific queue retrieval functionality.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The method must be called on a properly initialized BrokerBase subclass instance
    - The names parameter must be a list of valid queue name strings
    - The broker connection must be established and functional
    
    Postconditions:
    - The base class implementation raises NotImplementedError
    - Subclasses must return a dictionary mapping queue names to their information structures

## Side Effects:
    None: This base implementation performs no I/O operations or external service calls. Subclasses may perform network I/O or broker-specific operations to retrieve queue information.

## `flower.utils.broker.RabbitMQ` · *class*

## Summary:
RabbitMQ class implements broker functionality for RabbitMQ message brokers using the management HTTP API.

## Description:
The RabbitMQ class provides an asynchronous interface for interacting with RabbitMQ brokers through their HTTP management API. It extends BrokerBase to inherit URL parsing capabilities and implements queue retrieval functionality specific to RabbitMQ. This class is designed to be used in asynchronous environments and handles authentication, URL validation, and API communication with RabbitMQ's management interface.

## State:
- host (str): Hostname for the RabbitMQ management API; defaults to 'localhost' if not specified in broker URL
- port (int): Port number for the RabbitMQ management API; defaults to 15672 if not specified in broker URL  
- vhost (str): Virtual host path for RabbitMQ; URL-encoded and defaults to '/' if not specified in broker URL
- username (str): Username for API authentication; defaults to 'guest' if not specified in broker URL
- password (str): Password for API authentication; defaults to 'guest' if not specified in broker URL
- http_api (str): Full HTTP API endpoint URL for RabbitMQ management interface
- io_loop (tornado.ioloop.IOLoop): Event loop instance for asynchronous operations

## Lifecycle:
- Creation: Instantiate with broker_url and optional http_api and io_loop parameters
- Usage: Call the async queues() method to retrieve queue information from RabbitMQ management API
- Destruction: Automatically cleaned up by Python's garbage collector; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[RabbitMQ.__init__] --> B[RabbitMQ.queues]
    B --> C[AsyncHTTPClient.fetch]
    C --> D[JSON parsing]
    D --> E[Filter by queue names]
```

## Raises:
- ValueError: Raised during initialization when http_api URL has invalid scheme (not http/https)
- socket.error: Raised during API calls when connection fails
- httpclient.HTTPError: Raised during API calls when HTTP request fails
- Exception: Propagated from underlying HTTP client operations

## Example:
```python
import asyncio
from flower.utils.broker import RabbitMQ

async def example():
    # Create RabbitMQ broker instance
    broker = RabbitMQ(
        broker_url="amqp://user:pass@localhost:5672/vhost",
        http_api="http://user:pass@localhost:15672/api/vhost"
    )
    
    # Retrieve specific queues
    queues = await broker.queues(['queue1', 'queue2'])
    print(queues)
```

### `flower.utils.broker.RabbitMQ.__init__` · *method*

## Summary:
Initializes a RabbitMQ broker connection by parsing the broker URL, setting default connection parameters, and configuring the HTTP API endpoint for management operations.

## Description:
Configures the RabbitMQ instance by inheriting connection parameters from the broker URL, applying sensible defaults for missing values, and constructing a validated HTTP API endpoint for interacting with the RabbitMQ management interface. This method serves as the primary initialization point for RabbitMQ broker connections, establishing all necessary connection parameters and validation for subsequent management operations.

The method follows a specific initialization sequence:
1. Calls the parent BrokerBase constructor to parse the broker URL
2. Sets up the I/O loop for asynchronous operations
3. Applies default values for connection parameters when not provided
4. Constructs the HTTP API URL if not explicitly provided
5. Validates the constructed HTTP API URL
6. Stores the validated HTTP API endpoint for future use

## Args:
    broker_url (str): The broker connection URL containing protocol, hostname, port, virtual host, username, and password information.
    http_api (str, optional): The HTTP API endpoint URL for RabbitMQ management interface. If not provided, it's constructed from connection parameters.
    io_loop (tornado.ioloop.IOLoop, optional): The I/O loop instance for asynchronous operations. Defaults to the current IOLoop instance if not provided.
    **__: Accepts additional keyword arguments (ignored).

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: Raised by validate_http_api when the HTTP API URL has an invalid scheme (not http or https).

## State Changes:
    Attributes READ:
    - self.host (from parent BrokerBase)
    - self.port (from parent BrokerBase)
    - self.vhost (from parent BrokerBase)
    - self.username (from parent BrokerBase)
    - self.password (from parent BrokerBase)
    
    Attributes WRITTEN:
    - self.io_loop: Set to provided io_loop or default IOLoop instance
    - self.host: Set to parsed value or 'localhost' if not provided
    - self.port: Set to parsed value or 15672 if not provided
    - self.vhost: Set to parsed value, properly encoded, or '/' if not provided
    - self.username: Set to parsed value or 'guest' if not provided
    - self.password: Set to parsed value or 'guest' if not provided
    - self.http_api: Set to validated HTTP API URL

## Constraints:
    Preconditions:
    - broker_url must be a valid string representing a URL
    - The URL should follow standard format with optional username/password components
    - If http_api is provided, it must have a valid http or https scheme
    
    Postconditions:
    - All connection parameters are properly initialized with either parsed values or sensible defaults
    - The http_api attribute contains a valid HTTP API URL that can be used for management operations
    - The instance is ready for subsequent management API calls

## Side Effects:
    - May log an error message if the HTTP API URL validation fails
    - Creates a default IOLoop instance if none is provided
    - Performs URL parsing and encoding operations

### `flower.utils.broker.RabbitMQ.queues` · *method*

## Summary:
Fetches and filters queue information from RabbitMQ management API for specified queue names.

## Description:
Retrieves all queue information from RabbitMQ's management API for the configured virtual host, then filters the results to return only queues whose names match the provided list. This method is used to obtain specific queue details for monitoring or management purposes.

The method constructs the appropriate API endpoint URL using the instance's HTTP API endpoint and virtual host configuration, performs authentication using either URL credentials or instance credentials, and makes an asynchronous HTTP request to the RabbitMQ management API.

This method is part of the RabbitMQ class and is designed to be called asynchronously as it uses async/await patterns.

## Args:
    names (list[str]): A list of queue names to filter the results by

## Returns:
    list[dict]: A list of queue information dictionaries containing details about queues that match the provided names. Each dictionary contains standard RabbitMQ queue metadata. Returns an empty list if the API call fails or no matching queues are found.

## Raises:
    None explicitly raised - HTTP errors are caught and logged, returning empty list

## State Changes:
    Attributes READ: self.http_api, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Instance must have valid http_api, vhost, username, and password attributes set
    - Names parameter must be a list-like object
    - RabbitMQ management API must be accessible at the configured endpoint
    
    Postconditions:
    - Returns a list of queue dictionaries matching the provided names
    - Returns empty list on API failure or no matches

## Side Effects:
    - Makes synchronous HTTP request to RabbitMQ management API endpoint
    - Logs error messages to logger when API calls fail
    - Creates and closes AsyncHTTPClient instance during execution

### `flower.utils.broker.RabbitMQ.validate_http_api` · *method*

## Summary:
Validates that an HTTP API URL uses either 'http' or 'https' scheme.

## Description:
This class method ensures that the provided HTTP API endpoint uses a valid scheme ('http' or 'https'). It is called during RabbitMQ broker initialization to validate the HTTP management API URL before establishing connections.

## Args:
    http_api (str): The HTTP API URL to validate, containing scheme, host, port, and path components.

## Returns:
    None: This method does not return any value.

## Raises:
    ValueError: Raised when the URL scheme is not 'http' or 'https', with descriptive error message indicating the invalid scheme.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `http_api` argument must be a valid URL string that can be parsed by `urllib.parse.urlparse()`.
    Postconditions: If successful, the URL scheme is confirmed to be either 'http' or 'https'.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only parses the URL and raises an exception if validation fails.

## `flower.utils.broker.RedisBase` · *class*

## Summary:
RedisBase is an abstract base class that provides Redis-specific broker functionality for handling message queues with priority support.

## Description:
RedisBase extends BrokerBase to implement Redis-based broker operations, specifically providing queue management capabilities with priority support. It serves as a foundation for concrete Redis broker implementations in distributed messaging systems. This class handles Redis connection parameters extraction from broker URLs and provides utility methods for managing prioritized queues.

The class is designed to work in asynchronous environments and is intended to be subclassed by specific Redis broker implementations. It supports configurable priority levels and queue naming conventions for efficient message routing and processing.

## State:
- redis (redis.Redis or None): Redis client instance, initialized to None and set during connection setup
- priority_steps (list[int]): Priority levels supported for queue operations, defaults to [0, 3, 6, 9]
- sep (str): Separator character used in constructing prioritized queue names, defaults to '\x06\x16' 
- broker_prefix (str): Global prefix applied to all queue names for namespace isolation

The __init__ method accepts broker_url and optional broker_options dictionary containing:
- priority_steps: Custom priority levels (default: [0, 3, 6, 9])
- sep: Queue name separator (default: '\x06\x16')
- global_keyprefix: Prefix for all queue keys (default: '')

## Lifecycle:
- Creation: Instantiate with broker_url string and optional broker_options dict
- Usage: Subclasses must implement connection establishment and call queues() method asynchronously
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[RedisBase.__init__] --> B[RedisBase._q_for_pri]
    B --> C[RedisBase.queues]
    C --> D[RedisBase.redis.llen]
```

## Raises:
- ImportError: When the redis library is not available
- ValueError: When attempting to use a priority level not in priority_steps

## Example:
```python
# Basic instantiation
broker = RedisBase("redis://localhost:6379/0")

# With custom options
broker = RedisBase(
    "redis://user:pass@localhost:6379/0",
    broker_options={
        'priority_steps': [0, 1, 2, 3],
        'sep': '|',
        'global_keyprefix': 'myapp:'
    }
)

# Usage pattern (requires async context)
async def get_queue_stats():
    stats = await broker.queues(['queue1', 'queue2'])
    return stats
```

### `flower.utils.broker.RedisBase.__init__` · *method*

## Summary:
Initializes a RedisBase instance with broker configuration and default settings.

## Description:
Configures the RedisBase instance by setting up broker connection parameters and default priority handling settings. This method establishes the foundational configuration for Redis-based message brokering operations.

## Args:
    broker_url (str): URL for connecting to the Redis broker
    *_: Additional positional arguments (ignored)
    **kwargs: Keyword arguments containing broker configuration options
        broker_options (dict): Dictionary of broker-specific configuration parameters

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    ImportError: When the redis library is not available or importable

## State Changes:
    Attributes READ: 
        - self.DEFAULT_PRIORITY_STEPS (assumed to be defined in parent class)
        - self.DEFAULT_SEP (assumed to be defined in parent class)
    Attributes WRITTEN:
        - self.redis: Set to None initially
        - self.priority_steps: Set from broker_options or defaults
        - self.sep: Set from broker_options or defaults  
        - self.broker_prefix: Set from broker_options or defaults

## Constraints:
    Preconditions:
        - The redis library must be importable
        - broker_url must be a valid string URL
    Postconditions:
        - self.redis is initialized to None
        - Configuration parameters are set from broker_options or defaults

## Side Effects:
    - Raises ImportError if redis library is unavailable
    - Sets instance attributes for broker configuration

### `flower.utils.broker.RedisBase._q_for_pri` · *method*

## Summary:
Formats a queue name with an optional priority level using a configured separator.

## Description:
Constructs a priority-aware queue identifier by combining the base queue name with a priority level using a predefined separator. This method ensures that only valid priority levels are used and properly formats the resulting queue name for use in Redis operations.

The method is called internally by the `queues` method to generate queue identifiers for each priority level in the configured priority steps.

## Args:
    queue (str): The base queue name to format
    pri (int or None): Priority level to append to the queue name. Must be one of the values in `self.priority_steps`. If None or falsy, only the queue name is returned.

## Returns:
    str: Formatted queue name with priority suffix when priority is provided, otherwise just the queue name.

## Raises:
    ValueError: When the provided priority level is not in `self.priority_steps`.

## State Changes:
    Attributes READ: 
        - self.priority_steps: Used to validate priority level
        - self.sep: Used as separator between queue name and priority
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The priority level must be one of the values in `self.priority_steps`
        - The queue name must be a valid string
    Postconditions:
        - Returns a properly formatted string combining queue name, separator, and priority when priority is provided
        - Returns just the queue name when priority is None or falsy

## Side Effects:
    None

### `flower.utils.broker.RedisBase.queues` · *method*

## Summary:
Retrieves message count statistics for multiple Redis queues across all priority levels.

## Description:
Fetches the total message count for each specified queue by aggregating message counts from all priority-specific queue variants. This method is essential for monitoring queue health and workload distribution in priority-based message systems.

The method constructs priority-aware queue identifiers using the configured broker prefix and priority separator, then queries Redis for the length of each priority variant to compute the total message count for each queue.

## Args:
    names (list[str]): List of queue names to retrieve statistics for

## Returns:
    list[dict]: List of queue statistics dictionaries, each containing:
        - 'name' (str): The queue name
        - 'messages' (int): Total message count across all priority levels for that queue

## Raises:
    AttributeError: If self.redis is not properly initialized or accessible
    redis.exceptions.ConnectionError: If Redis connection fails during llen operations
    TypeError: If names is not a list or contains non-string elements

## State Changes:
    Attributes READ: 
        - self.broker_prefix: Used to prefix queue names
        - self.priority_steps: Defines available priority levels
        - self.redis: Used for Redis operations
        - self._q_for_pri: Method used to format queue names with priorities
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - self.redis must be initialized and connected to Redis server
        - self.priority_steps must contain valid priority values
        - names must be a list of valid queue name strings
    Postconditions:
        - Returns a list of statistics dictionaries with accurate message counts
        - Each queue's message count represents the sum across all priority levels

## Side Effects:
    - Performs multiple Redis network operations (llen calls)
    - May trigger Redis connection establishment if not already connected
    - Reads from Redis database to retrieve queue lengths

## `flower.utils.broker.Redis` · *class*

## Summary:
Redis is a concrete implementation of Redis-based broker functionality that handles connection setup and client creation for Redis message queues.

## Description:
The Redis class provides Redis-specific broker implementation by extending RedisBase. It processes broker URLs to extract connection parameters and creates a Redis client instance for queue operations. This class is designed to work in asynchronous environments and integrates with the broader broker infrastructure for distributed messaging systems.

This class serves as a bridge between the abstract broker interface and concrete Redis implementation, handling connection configuration, virtual host preparation, and client instantiation.

## State:
- host (str): Redis server hostname, defaults to 'localhost' if not specified in broker URL
- port (int): Redis server port number, defaults to 6379 if not specified in broker URL  
- vhost (int): Redis database number (virtual host), converted from URL path or defaulting to 0
- redis (redis.Redis): Redis client instance created during initialization

The __init__ method accepts broker_url and optional arguments, extracting connection parameters from the URL and preparing them for Redis client creation.

## Lifecycle:
- Creation: Instantiate with broker_url string; connection parameters are parsed from URL
- Usage: The redis client instance is ready for queue operations after initialization
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Redis.__init__] --> B[Redis._prepare_virtual_host]
    B --> C[Redis._get_redis_client_args]
    C --> D[Redis._get_redis_client]
    D --> E[redis.Redis()]
```

## Raises:
- ValueError: When virtual host cannot be converted to an integer (invalid database specification)
- redis.exceptions.ConnectionError: When Redis client fails to connect (raised by redis.Redis constructor)
- redis.exceptions.AuthenticationError: When Redis authentication fails (raised by redis.Redis constructor)

## Example:
```python
# Basic instantiation with default localhost:6379
redis_broker = Redis("redis://localhost:6379/0")

# With credentials and custom database
redis_broker = Redis("redis://user:pass@localhost:6379/1")

# Using with async context
async def process_queues():
    # The redis client is ready for use
    queue_length = await redis_broker.redis.llen('my_queue')
    return queue_length
```

### `flower.utils.broker.Redis.__init__` · *method*

## Summary:
Initializes a Redis broker connection with parsed URL parameters and default fallbacks.

## Description:
Configures Redis connection parameters by parsing the broker URL and setting default values for host, port, and virtual host. Creates a Redis client instance for subsequent operations. This method serves as the primary initialization point for Redis broker connections in the Flower monitoring system.

## Args:
    broker_url (str): Redis broker URL containing host, port, username, password, and virtual host information
    *args: Additional positional arguments passed to parent class constructor
    **kwargs: Additional keyword arguments passed to parent class constructor

## Returns:
    None: This is an initializer method that modifies instance state

## Raises:
    ImportError: When the redis library is not available
    ValueError: When virtual host database identifier cannot be converted to integer

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: self.host, self.port, self.vhost, self.redis

## Constraints:
    Preconditions: broker_url must be a valid URL string with proper Redis format
    Postconditions: self.host defaults to 'localhost' if not specified in broker_url
    Postconditions: self.port defaults to 6379 if not specified in broker_url
    Postconditions: self.vhost is normalized to an integer database number
    Postconditions: self.redis contains a valid Redis client instance

## Side Effects:
    I/O: Establishes network connection to Redis server during _get_redis_client() call
    External service calls: Connects to Redis server when Redis client is created
    Mutations: Modifies self.host, self.port, self.vhost, and self.redis attributes

### `flower.utils.broker.Redis._prepare_virtual_host` · *method*

## Summary:
Normalizes virtual host/database specification to an integer index for Redis connections.

## Description:
Processes various input formats for Redis virtual host/database specifications and converts them to valid integer indices between 0 and limit-1. This method ensures consistent handling of database identifiers regardless of whether they are provided as strings, empty values, or numeric values.

## Args:
    vhost (str|int): Virtual host/database identifier, which can be an integer, string representation of an integer, empty string, or slash-prefixed string.

## Returns:
    int: Normalized virtual host index between 0 and limit-1.

## Raises:
    ValueError: When vhost cannot be converted to an integer between 0 and limit-1.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The vhost parameter must be convertible to an integer between 0 and limit-1.
    Postconditions: The returned value is always an integer in the valid range for Redis databases.

## Side Effects:
    None

### `flower.utils.broker.Redis._get_redis_client_args` · *method*

## Summary:
Returns a dictionary of Redis client connection parameters extracted from instance attributes.

## Description:
This method serves as a parameter extractor that aggregates Redis connection configuration from the instance's host, port, vhost, username, and password attributes. It is designed to provide a clean interface for constructing Redis client arguments while keeping the connection parameter logic centralized and reusable. The method is primarily called by `_get_redis_client()` during Redis client instantiation.

## Args:
    None

## Returns:
    dict: A dictionary containing Redis client constructor arguments with keys:
        - 'host' (str): Redis server hostname or IP address
        - 'port' (int): Redis server port number
        - 'db' (int): Database index to select
        - 'username' (str, optional): Username for authentication
        - 'password' (str, optional): Password for authentication

## Raises:
    None

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Redis instance must have been properly initialized with connection parameters
    - All instance attributes (host, port, vhost, username, password) must be accessible
    
    Postconditions:
    - Returns a dictionary with all required Redis client connection parameters
    - The returned dictionary is suitable for unpacking as keyword arguments to redis.Redis()

## Side Effects:
    None

### `flower.utils.broker.Redis._get_redis_client` · *method*

## Summary:
Creates and returns a redis.Redis client instance configured with connection parameters from the broker configuration.

## Description:
This method serves as a factory for creating redis.Redis client instances. It retrieves connection parameters from the Redis instance's attributes via the `_get_redis_client_args()` method and uses them to instantiate a new Redis client. The method is primarily used during object initialization to establish the initial Redis connection.

## Args:
    None

## Returns:
    redis.Redis: A configured redis.Redis client instance ready for use with the broker's configured connection parameters.

## Raises:
    redis.exceptions.ConnectionError: When the Redis server is unreachable or connection cannot be established.
    redis.exceptions.AuthenticationError: When authentication fails with the Redis server.
    TypeError: If invalid arguments are passed to the redis.Redis constructor.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The Redis instance must have been properly initialized with connection parameters
    - The `_get_redis_client_args()` method must return a valid dictionary of arguments
    - The redis library must be available and importable
    
    Postconditions:
    - Returns a valid redis.Redis client instance
    - The returned client is configured with the broker's connection settings

## Side Effects:
    - Establishes a network connection to the Redis server (when the client is first used)
    - May trigger Redis authentication if credentials are provided

## `flower.utils.broker.RedisSentinel` · *class*

## Summary:
RedisSentinel is a Redis broker implementation that connects to Redis Sentinel for high availability and failover capabilities.

## Description:
RedisSentinel provides a broker interface for Redis Sentinel deployments, enabling applications to connect to Redis masters through a Sentinel monitoring service. This class is designed for environments where Redis master-slave replication with automatic failover is required. It extracts connection parameters from broker URLs and uses Redis Sentinel to discover and connect to the current master node.

The class requires a master_name in broker_options to identify which Redis master to connect to through the Sentinel service. It's typically used in distributed systems where Redis master nodes may fail over to slave nodes automatically.

## State:
- host (str): Redis Sentinel host address, parsed from broker_url or defaults to 'localhost'
- port (int): Redis Sentinel port number, parsed from broker_url or defaults to 26379  
- vhost (int): Database index for Redis connection, processed through _prepare_virtual_host method
- master_name (str): Name of the Redis master service to connect to via Sentinel
- redis (redis.sentinel.Sentinel): Redis Sentinel client instance for master discovery and connection

The __init__ method accepts broker_url and optional broker_options dictionary. The broker_options must contain 'master_name' key for proper initialization. RedisBase parent class handles basic broker URL parsing and configuration.

## Lifecycle:
- Creation: Instantiate with broker_url string and broker_options containing 'master_name'
- Usage: Typically used in async contexts for queue operations through inherited methods from RedisBase
- Destruction: Inherits cleanup behavior from RedisBase parent class

## Method Map:
```mermaid
graph TD
    A[RedisSentinel.__init__] --> B[RedisSentinel._prepare_virtual_host]
    A --> C[RedisSentinel._prepare_master_name]
    A --> D[RedisSentinel._get_redis_client]
    D --> E[redis.sentinel.Sentinel]
    E --> F[redis.sentinel.Sentinel.master_for]
```

## Raises:
- ValueError: When master_name is not provided in broker_options, or when vhost cannot be converted to integer
- redis.exceptions.ConnectionError: When unable to connect to Redis Sentinel or master

## Example:
```python
# Create Redis Sentinel broker instance
broker = RedisSentinel(
    "sentinel://localhost:26379/0",
    broker_options={
        'master_name': 'mymaster',
        'sentinel_kwargs': {'socket_timeout': 0.1}
    }
)

# The broker can then be used for queue operations
# (usage depends on inherited methods from RedisBase)
```

### `flower.utils.broker.RedisSentinel.__init__` · *method*

## Summary:
Initializes a Redis Sentinel broker instance by parsing the broker URL and setting up connection parameters for Redis Sentinel.

## Description:
This method initializes a Redis Sentinel broker by first calling the parent class constructor to parse the broker URL and extract basic connection parameters like host, port, and virtual host. It then configures Sentinel-specific settings including the master name and establishes a Redis client connection using the Sentinel pattern.

## Args:
    broker_url (str): The URL specifying the Redis Sentinel connection details including host, port, and optional authentication.
    *args: Additional positional arguments passed to the parent constructor.
    **kwargs: Additional keyword arguments, including 'broker_options' which contains Sentinel-specific configuration.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: When 'master_name' is not provided in broker_options.
    ValueError: When virtual host path cannot be converted to an integer.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.password
    Attributes WRITTEN: self.host, self.port, self.vhost, self.master_name, self.redis

## Constraints:
    Preconditions: 
    - broker_url must be a valid URL string with proper Redis Sentinel format
    - broker_options dictionary must contain 'master_name' key for Sentinel configuration
    Postconditions:
    - self.host is set to either the parsed host from broker_url or defaults to 'localhost' (port 26379)
    - self.port is set to either the parsed port from broker_url or defaults to 26379
    - self.vhost is normalized to an integer database number through _prepare_virtual_host
    - self.master_name is extracted from broker_options through _prepare_master_name
    - self.redis is initialized as a Redis client connected via Sentinel through _get_redis_client

## Side Effects:
    - Establishes network connections to Redis Sentinel server
    - Creates a Redis client instance for subsequent operations
    - May raise exceptions during URL parsing or Redis connection establishment

### `flower.utils.broker.RedisSentinel._prepare_virtual_host` · *method*

## Summary:
Normalizes virtual host parameter to a valid Redis database integer index.

## Description:
Converts various representations of Redis database indices into a standardized integer format. This method handles string representations, special cases like root paths, and validates that the result is a valid integral database index between 0 and the database limit minus 1.

## Args:
    vhost (str or int): Virtual host identifier that can be a string representation of a number, a path-like string starting with '/', or an integer.

## Returns:
    int: Normalized Redis database index as an integer between 0 and limit-1.

## Raises:
    ValueError: When vhost cannot be converted to an integer representing a valid database index.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The vhost parameter must be either an integer or a string that can be converted to an integer.
    Postconditions: The returned value is always an integer in the valid range for Redis database indices.

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._prepare_master_name` · *method*

## Summary:
Extracts and validates the master name from broker options for Redis Sentinel configuration.

## Description:
This method retrieves the master name from the broker options dictionary, which is required for establishing connections with Redis Sentinel. It's called during Redis Sentinel broker initialization to ensure proper configuration before creating the Redis client connection.

## Args:
    broker_options (dict): Dictionary containing Redis Sentinel configuration options, including the required 'master_name' key.

## Returns:
    str: The master name string used to identify the Redis master instance in the Sentinel configuration.

## Raises:
    ValueError: When the 'master_name' key is not present in the broker_options dictionary.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The broker_options parameter must be a dictionary
    - The broker_options dictionary must contain a 'master_name' key
    Postconditions:
    - Returns the master name string if present in broker_options
    - Raises ValueError if master_name is missing

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._get_redis_client` · *method*

## Summary:
Creates and returns a Redis client instance connected to the master node via Redis Sentinel for high availability messaging.

## Description:
This method establishes a Redis Sentinel connection to discover and connect to the current master node in a Redis replication setup. It is called during RedisSentinel initialization to create the primary Redis client used for all broker operations. The method leverages Redis Sentinel's automatic failover capabilities to ensure connections remain valid even during master node changes.

## Args:
    broker_options (dict): Configuration options for the Redis broker, including sentinel_kwargs for additional Sentinel configuration

## Returns:
    redis.Redis: A Redis client instance connected to the master node, ready for queue operations

## Raises:
    redis.exceptions.ConnectionError: When unable to establish connection to the Redis Sentinel server
    redis.exceptions.AuthenticationError: When authentication fails with the Redis Sentinel server
    redis.exceptions.TimeoutError: When connection attempts to Sentinel exceed timeout limits

## State Changes:
    Attributes READ: self.password, self.host, self.port, self.master_name
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.host must be a valid hostname or IP address
    - self.port must be a valid port number (typically 26379 for Redis Sentinel)
    - self.master_name must be configured and correspond to a valid Redis master in the Sentinel setup
    - self.password may be None or a valid password string
    - broker_options must be a dictionary-like object

    Postconditions:
    - Returns a valid Redis client instance that can be used for Redis operations
    - The returned client is configured to connect to the current master node

## Side Effects:
    - Establishes network connection to Redis Sentinel server
    - May trigger network I/O operations to resolve master node
    - Makes external service calls to Redis Sentinel for master discovery

## `flower.utils.broker.RedisSocket` · *class*

## Summary:
RedisSocket is a Redis broker implementation that connects to Redis via Unix domain socket for message queue operations.

## Description:
RedisSocket provides a concrete implementation of Redis-based message queuing using Unix domain sockets for connection. It inherits from RedisBase and specializes in handling Redis connections through Unix socket paths rather than TCP connections. This implementation is suitable for environments where Unix sockets provide better performance or security compared to network-based connections.

The class extracts connection parameters from the broker URL and establishes a Redis connection using a Unix domain socket path constructed from the virtual host component of the URL.

## State:
- redis (redis.Redis): Redis client instance connected via Unix domain socket
- vhost (str): Virtual host component extracted from broker URL, used as Unix socket path prefix
- password (str or None): Password credential extracted from broker URL for Redis authentication

## Lifecycle:
- Creation: Instantiate with broker_url string; automatically initializes Redis connection using Unix socket
- Usage: The redis attribute is ready for use after initialization; typically used for queue operations
- Destruction: Redis connection is managed by the redis-py library; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[RedisSocket.__init__] --> B[RedisBase.__init__]
    B --> C[RedisSocket.redis = redis.Redis(...)]
```

## Raises:
- redis.exceptions.ConnectionError: When unable to connect to the Unix socket
- redis.exceptions.AuthenticationError: When password authentication fails
- ValueError: When broker_url format is invalid or vhost component is missing

## Example:
```python
# Create RedisSocket instance
broker = RedisSocket("redis+socket:///var/run/redis/redis.sock")

# The redis client is automatically available for queue operations
queue_length = broker.redis.llen('my_queue')
```

### `flower.utils.broker.RedisSocket.__init__` · *method*

## Summary:
Initializes a RedisSocket instance by setting up a Redis connection using Unix socket path and password from the broker URL.

## Description:
This method constructs a RedisSocket object by first calling the parent class constructor to initialize broker-related attributes from the broker URL, then creating a redis.Redis connection using a Unix socket path derived from the virtual host and the password from the authentication credentials.

## Args:
    broker_url (str): The broker URL containing hostname, port, path (vhost), username, and password information
    *args: Additional positional arguments passed to the parent constructor
    **kwargs: Additional keyword arguments passed to the parent constructor

## Returns:
    None: This method initializes instance attributes but does not return a value

## Raises:
    ImportError: When the redis library is not available
    ValueError: When priority steps validation fails in parent class (indirectly)

## State Changes:
    Attributes READ: self.vhost, self.password
    Attributes WRITTEN: self.redis

## Constraints:
    Preconditions: 
    - broker_url must be a valid URL with proper scheme and components
    - redis library must be installed
    - vhost attribute must be properly extracted from broker_url path component
    
    Postconditions:
    - self.redis is initialized as a redis.Redis connection object
    - All parent class attributes are properly initialized

## Side Effects:
    - Creates a Redis connection using Unix socket
    - May raise ImportError if redis library is not available

## `flower.utils.broker.RedisSsl` · *class*

## Summary:
RedisSsl is a Redis broker subclass that enables SSL/TLS connections for Redis servers.

## Description:
RedisSsl is a specialized subclass of Redis designed for secure Redis broker connections using SSL/TLS encryption. It is intended for use with 'rediss://' broker URLs and requires the 'broker_use_ssl' parameter to be provided during initialization.

This implementation modifies the Redis client connection parameters to enable SSL/TLS encryption by setting the 'ssl' parameter to True and incorporating additional SSL configuration from the 'broker_use_ssl' argument. It inherits all Redis broker functionality while adding SSL support.

## State:
- broker_use_ssl (dict): Configuration dictionary for SSL parameters passed through kwargs to Redis client constructor. Required during initialization; defaults to empty dict if not specified.
- Inherits all state attributes from Redis parent class including host, port, vhost, and redis client instance.

## Lifecycle:
- Creation: Instantiate with broker_url string starting with 'rediss://' and provide 'broker_use_ssl' in kwargs. The broker_url must contain valid Redis connection parameters.
- Usage: After initialization, the redis client instance is ready for queue operations with SSL/TLS enabled.
- Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[RedisSsl.__init__] --> B[Redis.__init__]
    B --> C[Redis._prepare_virtual_host]
    C --> D[Redis._get_redis_client_args]
    D --> E[Redis._get_redis_client]
    E --> F[redis.Redis(**client_args)]
```

## Raises:
- ValueError: Raised during initialization when 'broker_use_ssl' is not provided in kwargs, indicating that SSL configuration is mandatory for rediss broker URLs.

## Example:
```python
# Create SSL-enabled Redis broker
broker = RedisSsl(
    "rediss://user:pass@secure-redis.example.com:6380/0",
    broker_use_ssl={
        'ssl_cert_reqs': 'required',
        'ssl_ca_certs': '/path/to/ca.crt'
    }
)

# The broker is now configured for secure Redis connections
# All subsequent Redis operations will use SSL/TLS encryption
```

### `flower.utils.broker.RedisSsl.__init__` · *method*

## Summary:
Initializes an SSL-enabled Redis broker connection with proper SSL configuration validation.

## Description:
Configures a Redis broker instance for SSL connections by validating the required broker_use_ssl parameter and setting up SSL client arguments. This method ensures that rediss:// broker URLs are properly configured for secure Redis connections.

## Args:
    broker_url (str): The Redis broker URL, typically starting with 'rediss://' for SSL connections
    *args: Additional positional arguments passed to the parent class constructor
    **kwargs: Additional keyword arguments including broker_use_ssl for SSL configuration

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    ValueError: When broker_use_ssl is not provided in kwargs, indicating that SSL configuration is missing for rediss broker URLs

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.broker_use_ssl: Stores the SSL configuration dictionary from kwargs

## Constraints:
    Preconditions:
        - When using rediss:// broker URLs, broker_use_ssl must be provided in kwargs
        - broker_url must be a valid Redis URL format
    Postconditions:
        - self.broker_use_ssl is set to the provided SSL configuration or empty dict
        - Parent class initialization is completed successfully

## Side Effects:
    None: This method performs no I/O operations or external service calls beyond the parent constructor

### `flower.utils.broker.RedisSsl._get_redis_client_args` · *method*

## Summary:
Returns Redis client connection arguments with SSL enabled and additional SSL configuration applied.

## Description:
Overrides the parent class method to configure Redis client arguments for SSL connections. This method ensures that all Redis client connections use SSL encryption when working with rediss:// broker URLs. It builds upon the base connection parameters by enabling SSL and incorporating additional SSL-specific configuration options.

The method is called during Redis client instantiation to prepare connection arguments for the redis.Redis constructor. It's part of the SSL-enabled Redis broker implementation that requires explicit SSL configuration through the broker_use_ssl parameter.

## Args:
    None

## Returns:
    dict: A dictionary of Redis client constructor arguments with SSL enabled and additional SSL configuration. Includes all standard Redis connection parameters plus:
        - 'ssl' (bool): Set to True to enable SSL connections
        - Additional SSL-specific parameters from self.broker_use_ssl if provided as a dictionary

## Raises:
    None

## State Changes:
    Attributes READ: self.broker_use_ssl
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The RedisSsl instance must have been properly initialized with broker_use_ssl parameter
    - self.broker_use_ssl must be either a dictionary or None/empty dict
    - The parent class must have successfully initialized connection parameters
    
    Postconditions:
    - Returns a dictionary suitable for unpacking as keyword arguments to redis.Redis()
    - The returned dictionary contains 'ssl': True to enforce SSL connections
    - If self.broker_use_ssl is a dictionary, its key-value pairs are merged into the result

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only manipulates dictionary data structures.

## `flower.utils.broker.Broker` · *class*

## Summary:
Broker is a factory class that returns specific broker implementations based on URL scheme, supporting AMQP, Redis, Redis SSL, Redis Socket, and Redis Sentinel protocols.

## Description:
The Broker class implements a factory pattern that dynamically creates and returns instances of specialized broker implementations based on the scheme specified in the broker URL. When instantiated, it examines the URL scheme and returns an appropriate concrete broker instance (RabbitMQ, Redis, RedisSsl, RedisSocket, or RedisSentinel) that handles the specific protocol requirements. This abstraction allows the system to work uniformly with different message broker technologies through a common interface.

## State:
- The Broker class itself maintains no persistent state
- The returned broker instances have their own state based on the specific implementation (e.g., host, port, vhost, redis client for Redis implementations)

## Lifecycle:
- Creation: Called with a broker_url parameter; returns an instance of a concrete broker subclass
- Usage: The returned instance is used for queue operations through the async queues() method
- Destruction: Cleaned up by Python's garbage collector; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[Broker.__new__] --> B{URL Scheme Check}
    B -->|amqp| C[RabbitMQ Instance]
    B -->|redis| D[Redis Instance]
    B -->|rediss| E[RedisSsl Instance]
    B -->|redis+socket| F[RedisSocket Instance]
    B -->|sentinel| G[RedisSentinel Instance]
    B -->|unsupported| H[NotImplementedError]
    C --> I[Broker.queues]
    D --> I
    E --> I
    F --> I
    G --> I
```

## Raises:
- NotImplementedError: Raised when the broker URL scheme is not supported (not amqp, redis, rediss, redis+socket, or sentinel)

## Example:
```python
from flower.utils.broker import Broker

# Create different broker instances based on URL scheme
rabbitmq_broker = Broker("amqp://user:pass@localhost:5672/vhost")
redis_broker = Broker("redis://localhost:6379/0")
redis_ssl_broker = Broker("rediss://user:pass@localhost:6380/0")
redis_socket_broker = Broker("redis+socket:///var/run/redis/redis.sock")
redis_sentinel_broker = Broker("sentinel://localhost:26379/0")

# All brokers expose the same async queues method
# await broker.queues(['queue1', 'queue2'])
```

### `flower.utils.broker.Broker.__new__` · *method*

## Summary:
Creates and returns an instance of a specific broker implementation based on the URL scheme.

## Description:
The `__new__` method implements a factory pattern that dynamically instantiates the appropriate broker subclass based on the scheme portion of the provided broker URL. This allows the system to transparently handle different message broker types (AMQP, Redis, Redis SSL, Redis Socket, Redis Sentinel) through a unified interface.

The method parses the broker URL using `urlparse` to extract the scheme and delegates to the corresponding concrete broker class constructor. This approach enables polymorphic behavior where the same interface can work with different underlying broker technologies.

## Args:
    broker_url (str): Connection URL specifying the broker type and connection parameters
    *args: Additional positional arguments passed to the specific broker constructor
    **kwargs: Additional keyword arguments passed to the specific broker constructor

## Returns:
    Broker instance: An instance of the appropriate concrete broker subclass (RabbitMQ, Redis, RedisSsl, RedisSocket, or RedisSentinel)

## Raises:
    NotImplementedError: When the broker URL scheme is not supported (not one of amqp, redis, rediss, redis+socket, sentinel)

## State Changes:
    Attributes READ: None - this method doesn't read any instance attributes
    Attributes WRITTEN: None - this method doesn't write any instance attributes

## Constraints:
    Preconditions: 
    - broker_url must be a valid string containing a recognized scheme
    - Supported schemes are: 'amqp', 'redis', 'rediss', 'redis+socket', 'sentinel'
    
    Postconditions:
    - Returns an instance of a concrete broker subclass matching the URL scheme
    - The returned instance is properly initialized with the broker URL and any additional arguments

## Side Effects:
    None - This method performs no I/O operations or external service calls. It only creates objects and returns them.

### `flower.utils.broker.Broker.queues` · *method*

## Summary:
Retrieves detailed statistics for specified message queues from the broker backend.

## Description:
Asynchronously fetches queue statistics and metadata for a list of message queues from the broker backend. This method is implemented by concrete broker subclasses (Redis, RabbitMQ) to provide queue-specific information such as message counts, consumer details, and other broker-specific metrics.

The method serves as a key interface for monitoring and managing message queues in distributed systems. It enables uniform access to different message queue backends (Redis, RabbitMQ, etc.) through a consistent API, allowing applications to query queue status regardless of the underlying technology.

## Args:
    names (list[str]): A list of queue names to retrieve statistics for. Each name corresponds to a specific queue in the broker system. An empty list returns an empty result.

## Returns:
    dict[str, dict]: A dictionary mapping queue names to their respective statistics. Each queue entry contains:
        - length (int): Number of messages currently in the queue
        - consumers (int, optional): Number of active consumers (RabbitMQ specific)
        - other broker-specific metrics (varies by implementation)
    Returns an empty dictionary if no queues are found or if the names list is empty.

## Raises:
    NotImplementedError: When called directly on the abstract Broker class (this base implementation)
    ConnectionError: When unable to establish connection to the broker backend
    ValueError: When queue names are invalid or unsupported by the broker

## State Changes:
    Attributes READ: None - this method doesn't modify the Broker instance's state
    Attributes WRITTEN: None - this method doesn't modify the Broker instance's state

## Constraints:
    Preconditions:
        - The broker must be properly initialized with valid connection parameters
        - The names parameter must be a list of valid queue name strings
        - The broker must be reachable and authenticated
    Postconditions:
        - Returns a dictionary with queue statistics for all requested queues
        - If a queue doesn't exist, it won't appear in the returned dictionary
        - The returned data structure follows the broker's specific format conventions

## Side Effects:
    I/O: Makes network requests to the broker backend (HTTP calls for RabbitMQ, Redis commands for Redis)
    External service calls: Communicates with the message broker's management interface or Redis server

## `flower.utils.broker.main` · *function*

## Summary:
Command-line utility for querying message broker queue statistics.

## Description:
An asynchronous entry point that reads broker connection parameters and queue names from command line arguments, instantiates a Broker object using the provided configuration, and retrieves queue statistics from the configured message broker backend.

This function provides a simple command-line interface for monitoring message queues by delegating to the Broker factory pattern to handle different broker types (AMQP, Redis, etc.) transparently.

## Args:
    None - This function reads all configuration from command line arguments:
    - sys.argv[1] (str, optional): Broker URL with scheme (e.g., 'amqp://user:pass@host:port/vhost'). Defaults to 'amqp://'.
    - sys.argv[2] (str, optional): Queue name to query. Defaults to 'celery'.
    - sys.argv[3] (str, optional): HTTP API endpoint for broker management interface. Defaults to 'http://guest:guest@localhost:15672/api/'.

## Returns:
    None - This function prints results directly to stdout and does not return a value.

## Raises:
    NotImplementedError: When the broker URL scheme is not supported by the Broker factory.
    Exception: May raise exceptions from the underlying broker implementation during connection or query operations.

## Constraints:
    Preconditions:
        - At least one command line argument must be provided (broker URL)
        - Valid broker URL scheme must be specified (amqp, redis, rediss, redis+socket, sentinel)
    Postconditions:
        - If queues are found, their statistics are printed to stdout
        - If no queues are found, nothing is printed
        - Function execution completes asynchronously

## Side Effects:
    I/O: Writes formatted queue statistics to standard output (stdout)
    Network communication: Establishes connections to broker endpoints via TCP/IP

## Control Flow:
```mermaid
flowchart TD
    A[Start main()] --> B{Command line args provided?}
    B -->|No| C[Use defaults]
    B -->|Yes| D[Parse args]
    D --> E[Create Broker instance]
    E --> F[Call broker.queues()]
    F --> G{Queues found?}
    G -->|Yes| H[Print queues]
    G -->|No| I[Exit silently]
```

## Examples:
```bash
# Query default celery queue with default broker settings
python broker.py

# Query specific queue on custom broker
python broker.py amqp://user:pass@localhost:5672/myvhost myqueue

# Query with custom HTTP API endpoint
python broker.py redis://localhost:6379/0 myqueue http://admin:secret@broker:15672/api/
```

