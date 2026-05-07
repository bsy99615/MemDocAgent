# `broker.py`

## `flower.utils.broker.BrokerBase` · *class*

## Summary:
Abstract base class for broker implementations that handles URL parsing and provides queue operation interface.

## Description:
BrokerBase serves as the foundation for concrete broker implementations, providing standardized URL parsing for broker connections and defining the interface for queue operations. It is designed to be subclassed by specific broker implementations like Redis, RabbitMQ, or HTTP-based brokers.

The class extracts connection parameters from a broker URL, making it easy to configure different broker backends through a unified URL format. Subclasses must implement the async queues() method to provide specific queue functionality.

## State:
- host (str): Hostname extracted from broker URL; None if not specified
- port (int): Port number extracted from broker URL; None if not specified  
- vhost (str): Virtual host path extracted from broker URL (without leading slash)
- username (str): Username from broker URL, URL-decoded if present; None if not specified
- password (str): Password from broker URL, URL-decoded if present; None if not specified

All parsed URL components are stored as instance attributes and remain immutable after initialization.

## Lifecycle:
- Creation: Instantiate with a broker URL string containing hostname, port, virtual host, username, and password components
- Usage: Subclasses should implement the async queues() method to provide queue functionality
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[BrokerBase.__init__] --> B[BrokerBase.queues]
    B --> C[Subclass Implementation]
```

## Raises:
- None explicitly raised by __init__ method
- NotImplementedError raised by queues() method when called directly

## Example:
```python
# Typical usage pattern for subclassing
class RedisBroker(BrokerBase):
    async def queues(self, names):
        # Implementation for Redis-specific queue operations
        pass

# Creating an instance
broker = RedisBroker("redis://user:pass@localhost:6379/vhost")
```

### `flower.utils.broker.BrokerBase.__init__` · *method*

## Summary:
Initializes a broker connection by parsing the broker URL and extracting connection parameters.

## Description:
This constructor method processes a broker connection URL to extract essential connection parameters including hostname, port, virtual host, username, and password. It handles URL decoding for credentials and stores them as instance attributes for subsequent broker operations. This method is typically called during object instantiation when setting up a broker connection.

## Args:
    broker_url (str): The broker connection URL containing host, port, virtual host, username, and password information in standard URL format.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though malformed URLs could cause urlparse to behave unexpectedly.

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
        - broker_url must be a valid string in URL format
        - The URL should contain at least a hostname component
    Postconditions:
        - All connection parameters are properly extracted and stored as instance attributes
        - Username and password are URL-decoded if present, otherwise remain None

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only manipulates instance attributes.

### `flower.utils.broker.BrokerBase.queues` · *method*

## Summary:
Retrieves detailed information about specified message queues from a broker system.

## Description:
This asynchronous abstract method serves as an interface for fetching queue metadata from a message broker. It is designed to be implemented by concrete broker subclasses to provide specific broker integration capabilities. The method accepts a list of queue names and returns corresponding queue information.

## Args:
    names (list[str]): A list of queue names to retrieve information for

## Returns:
    dict: A dictionary mapping queue names to their respective metadata information. The exact structure of the metadata depends on the broker implementation.

## Raises:
    NotImplementedError: Always raised by the base class implementation, requiring subclasses to provide concrete implementation

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The method must be called on a properly initialized BrokerBase subclass instance
    - The names parameter should be a list of valid queue identifiers
    Postconditions: 
    - The base class implementation raises NotImplementedError
    - Subclasses must return queue information in a standardized format

## Side Effects:
    None

## `flower.utils.broker.RabbitMQ` · *class*

## Summary:
RabbitMQ broker implementation that interacts with RabbitMQ's management HTTP API to fetch queue information.

## Description:
The RabbitMQ class provides an asynchronous interface for retrieving queue information from a RabbitMQ broker's management API. It extends BrokerBase to handle RabbitMQ-specific URL parsing and implements the async queues() method to fetch queue data via HTTP requests. This class is designed to integrate with systems that monitor or manage RabbitMQ queues programmatically.

This class is typically instantiated by dependency injection or factory methods that provide the broker URL and HTTP API endpoint configuration. It's commonly used in monitoring systems, queue management tools, or distributed application frameworks that need to query RabbitMQ queue states.

## State:
- io_loop (tornado.ioloop.IOLoop): Event loop instance for asynchronous operations; defaults to the current IOLoop instance
- host (str): RabbitMQ server hostname; defaults to 'localhost' if not specified in URL
- port (int): Management API port; defaults to 15672 if not specified in URL  
- vhost (str): Virtual host path; defaults to '/' if not specified in URL
- username (str): Authentication username; defaults to 'guest' if not specified in URL
- password (str): Authentication password; defaults to 'guest' if not specified in URL
- http_api (str): Full management API endpoint URL constructed from connection parameters

## Lifecycle:
- Creation: Instantiate with broker_url string and optional http_api parameter; validates URL format and constructs API endpoint
- Usage: Call async queues(names) method to fetch queue information for specified queue names
- Destruction: Automatically cleaned up by Python garbage collector; HTTP client is closed in finally block of queues() method

## Method Map:
```mermaid
graph TD
    A[RabbitMQ.__init__] --> B[RabbitMQ.queues]
    B --> C[AsyncHTTPClient.fetch]
    C --> D[HTTP Response Processing]
    D --> E[RabbitMQ.queues return]
```

## Raises:
- ValueError: Raised during initialization when http_api parameter contains invalid scheme (not http/https)
- socket.error: Raised during HTTP requests when connection fails
- httpclient.HTTPError: Raised during HTTP requests when server returns error status
- json.JSONDecodeError: Implicitly raised when response body cannot be decoded as JSON (handled internally)

## Example:
```python
# Create RabbitMQ broker instance
broker = RabbitMQ(
    broker_url="amqp://user:pass@rabbitmq-server:5672/vhost",
    http_api="http://user:pass@rabbitmq-server:15672/api/vhost"
)

# Fetch specific queue information asynchronously
queue_info = await broker.queues(['queue1', 'queue2'])
```

### `flower.utils.broker.RabbitMQ.__init__` · *method*

## Summary:
Initializes a RabbitMQ broker connection with HTTP API configuration.

## Description:
Configures the RabbitMQ broker connection by parsing the broker URL, setting default connection parameters, and constructing/validating the HTTP management API endpoint. This method prepares the instance for making API calls to RabbitMQ's management interface.

## Args:
    broker_url (str): The AMQP broker URL containing connection details like host, port, vhost, username, and password.
    http_api (str): The HTTP API endpoint URL for RabbitMQ management interface. If None, constructed from connection parameters.
    io_loop (tornado.ioloop.IOLoop, optional): The I/O loop instance to use. Defaults to the current IOLoop instance if not provided.
    **__ (dict): Additional keyword arguments (ignored).

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: When the http_api URL has an invalid scheme (not http or https).

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: self.io_loop, self.http_api

## Constraints:
    Preconditions: 
    - broker_url must be a valid URL with proper AMQP scheme
    - http_api must be a valid URL if provided (or will be constructed properly)
    Postconditions:
    - All connection parameters (host, port, vhost, username, password) are properly set
    - self.http_api contains a valid HTTP API URL for RabbitMQ management interface

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only sets instance attributes.

### `flower.utils.broker.RabbitMQ.queues` · *method*

## Summary:
Fetches and filters queue information from RabbitMQ management API by specified queue names.

## Description:
Retrieves all queue information from the RabbitMQ management API for the configured virtual host, then filters the results to only include queues whose names match the provided list. This method is used to obtain specific queue details while minimizing unnecessary data transfer.

## Args:
    names (list[str]): A list of queue names to filter the results by.

## Returns:
    list[dict]: A list of queue information dictionaries containing only queues whose names are in the provided names list. Returns an empty list if the API call fails or no matching queues are found.

## Raises:
    None explicitly raised - HTTP errors are caught and logged, returning empty list.

## State Changes:
    Attributes READ: self.http_api, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.http_api must be a valid URL pointing to RabbitMQ management API
    - self.vhost must be properly encoded
    - names parameter must be iterable containing queue name strings
    
    Postconditions:
    - Returns a list of queue dictionaries matching provided names
    - Returns empty list on API failure or no matches

## Side Effects:
    - Makes asynchronous HTTP request to RabbitMQ management API
    - Logs error messages to logger when API calls fail
    - Creates and closes AsyncHTTPClient instance

### `flower.utils.broker.RabbitMQ.validate_http_api` · *method*

## Summary:
Validates that an HTTP API URL uses a supported scheme (http or https).

## Description:
This classmethod ensures that the provided HTTP API URL uses either the 'http' or 'https' scheme. It is used during RabbitMQ broker initialization to validate the management API endpoint URL before storing it for subsequent API calls. The validation prevents the use of insecure or unsupported protocols for communication with RabbitMQ's management interface.

## Args:
    cls: The class object (used for classmethod decorator)
    http_api (str): The HTTP API URL to validate for proper scheme

## Returns:
    None: This method does not return a value but raises an exception on validation failure.

## Raises:
    ValueError: Raised when the provided URL has an invalid scheme (not 'http' or 'https'). The error message includes the invalid scheme for debugging purposes.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The http_api parameter must be a string representing a valid URL
    - The URL must contain a scheme component (http:// or https://)
    
    Postconditions:
    - The method completes without raising an exception if the URL scheme is valid
    - The method raises ValueError if the URL scheme is invalid

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only parses the URL and raises an exception if validation fails.

## `flower.utils.broker.RedisBase` · *class*

## Summary:
RedisBase is an abstract base class that provides Redis-specific broker functionality for queue management and statistics, inheriting from BrokerBase.

## Description:
RedisBase serves as a foundational class for Redis-based broker implementations, handling Redis connection setup and providing standardized queue operations. It extends BrokerBase to add Redis-specific features like priority-based queue handling and message counting. This class is intended to be subclassed by concrete Redis broker implementations rather than instantiated directly.

The class manages Redis connection parameters extracted from broker URLs and provides utility methods for working with prioritized queues in Redis. It implements the basic queue statistics functionality required by the broker interface while leaving specific Redis operations to subclasses.

Priority-based queues are implemented by appending priority levels to queue names using a separator character. This allows for efficient message prioritization in Redis where messages with higher priority are processed first.

## State:
- redis (Redis client): Redis connection object initialized to None; set during connection setup
- priority_steps (list[int]): Priority levels used for queue organization; defaults to [0, 3, 6, 9]
- sep (str): Separator character used to construct priority-based queue names; defaults to '\x06\x16' 
- broker_prefix (str): Global prefix applied to all queue names; defaults to empty string

## Lifecycle:
- Creation: Instantiate with a broker URL string; requires redis library to be available
- Usage: Subclasses must implement Redis-specific connection logic; typically used for queue statistics operations
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[RedisBase.__init__] --> B[RedisBase._q_for_pri]
    B --> C[RedisBase.queues]
```

## Raises:
- ImportError: Raised during initialization if the redis library is not available
- ValueError: Raised by _q_for_pri when attempting to use a priority not in priority_steps

## Example:
```python
# Typical usage would involve subclassing RedisBase
class MyRedisBroker(RedisBase):
    def __init__(self, broker_url, *args, **kwargs):
        super().__init__(broker_url, *args, **kwargs)
        # Initialize Redis connection here
        self.redis = redis.Redis(host=self.host, port=self.port, db=0)

# Using the queues method
broker = MyRedisBroker("redis://localhost:6379/0")
queue_stats = await broker.queues(["queue1", "queue2"])
```

### `flower.utils.broker.RedisBase.__init__` · *method*

## Summary:
Initializes a RedisBase instance with broker connection settings and configuration options.

## Description:
This method sets up the Redis broker connection configuration by parsing the broker URL through the parent BrokerBase class and initializing Redis-specific parameters. It handles Redis library dependency checking and processes broker configuration options such as priority steps, separator, and key prefix.

## Args:
    broker_url (str): The URL of the Redis broker in standard format (e.g., redis://user:pass@host:port/vhost)
    *_: Additional positional arguments (ignored)
    **kwargs: Keyword arguments containing broker configuration options
        broker_options (dict): Dictionary of Redis broker configuration options including:
            priority_steps (list[int]): Priority levels for message queuing. Defaults to class DEFAULT_PRIORITY_STEPS [0, 3, 6, 9].
            sep (str): Separator string for priority-based queue naming. Defaults to class DEFAULT_SEP '\x06\x16'.
            global_keyprefix (str): Global prefix for all Redis keys. Defaults to empty string.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ImportError: When the redis library is not available or importable.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.redis: Set to None initially
        - self.priority_steps: Set from broker_options or defaults
        - self.sep: Set from broker_options or defaults  
        - self.broker_prefix: Set from broker_options or defaults

## Constraints:
    Preconditions:
        - The redis library must be importable
        - broker_url must be a valid URL format
    Postconditions:
        - self.redis is initialized to None
        - All configuration parameters are set with either provided values or appropriate defaults

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object state.

### `flower.utils.broker.RedisBase._q_for_pri` · *method*

## Summary:
Formats a queue name with priority information for Redis-based message queuing.

## Description:
Constructs a Redis key name by combining a queue name with a priority level using a configured separator. This method ensures that queue names are properly formatted for priority-based queuing systems, where messages are stored in separate lists based on their priority levels.

The method validates that the provided priority is within the allowed priority steps defined for this broker instance. This validation prevents invalid priority levels from being used in queue naming.

## Args:
    queue (str): The base queue name to format
    pri (int or None): Priority level to append to the queue name. Must be in self.priority_steps. If None, returns the queue name unchanged.

## Returns:
    str: Formatted queue name with priority suffix, or just the queue name if priority is None.

## Raises:
    ValueError: When the provided priority level is not in self.priority_steps.

## State Changes:
    Attributes READ: self.priority_steps, self.sep
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The priority parameter must be either None or an integer present in self.priority_steps
    - self.priority_steps must be a list of valid priority values
    - self.sep must be a string used as a separator between queue name and priority
    
    Postconditions:
    - Returns a properly formatted Redis key name
    - If pri is None, returns the original queue name unchanged
    - If pri is valid, returns queue_name + sep + priority_string

## Side Effects:
    None

### `flower.utils.broker.RedisBase.queues` · *method*

## Summary:
Retrieves message count statistics for a list of queue names from Redis by aggregating across priority levels.

## Description:
This asynchronous method calculates the total number of messages in each queue by querying all priority-specific queue names and summing their lengths. It's designed to provide comprehensive queue statistics for monitoring and management purposes. For each queue name, it generates priority-specific queue names using the broker prefix and priority steps, then sums the length of messages in all priority queues for that queue.

## Args:
    names (list[str]): A list of queue names to retrieve statistics for

## Returns:
    list[dict]: A list of dictionaries, each containing:
        - 'name' (str): The queue name
        - 'messages' (int): Total message count across all priority levels for that queue

## Raises:
    None explicitly documented

## State Changes:
    Attributes READ: self.broker_prefix, self.priority_steps, self.redis
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.broker_prefix must be defined (string)
    - self.priority_steps must be defined and iterable (typically a list of integers)
    - self.redis must be a valid Redis connection object with llen method
    - names must be iterable containing valid queue names
    
    Postconditions:
    - Returns a list of dictionaries with consistent structure
    - Each dictionary contains 'name' and 'messages' keys
    - Message counts are aggregated across all priority levels for each queue
    - Returns empty list if names is empty
    - Each priority queue name is constructed using self._q_for_pri() method

## Side Effects:
    - Makes Redis llen() operations for each priority queue (multiple Redis calls)
    - Performs string concatenation operations for building priority queue names
    - Calls self._q_for_pri() method for each queue name and priority step
    - May cause network I/O if Redis is remote

## `flower.utils.broker.Redis` · *class*

## Summary:
Redis is a concrete implementation of RedisBase that provides Redis broker functionality for queue management and statistics.

## Description:
The Redis class implements a Redis-based broker for managing task queues and retrieving queue statistics. It inherits from RedisBase and provides the concrete implementation needed to connect to a Redis server and perform queue operations. This class is designed to work with Celery-style task queues where messages are stored in Redis lists with priority-based organization.

The class handles parsing of broker URLs to extract connection parameters (host, port, database index, credentials) and creates a Redis client instance for communication with the Redis server. It supports virtual host specifications that can be either integers or paths, converting them to valid database indices.

## State:
- host (str): Redis server hostname, defaults to 'localhost' if not specified in broker URL
- port (int): Redis server port number, defaults to 6379 if not specified in broker URL  
- vhost (int): Redis database index (0-15 by default), converted from virtual host specification
- redis (redis.Redis): Configured Redis client instance for database operations

## Lifecycle:
- Creation: Instantiate with a broker URL string; requires redis library to be available
- Usage: Typically used for queue statistics operations via inherited methods from RedisBase
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[Redis.__init__] --> B[Redis._prepare_virtual_host]
    A --> C[Redis._get_redis_client]
    B --> D[Redis._get_redis_client_args]
    C --> D
```

## Raises:
- ValueError: Raised by _prepare_virtual_host when virtual host cannot be converted to integer database index
- redis.ConnectionError: May be raised by redis.Redis constructor if connection parameters are invalid
- redis.AuthenticationError: May be raised by redis.Redis constructor if authentication fails

## Example:
```python
# Create Redis broker instance
broker = Redis("redis://localhost:6379/0")

# The broker is now ready to use for queue operations
# (inherited methods from RedisBase would be used for actual operations)
```

### `flower.utils.broker.Redis.__init__` · *method*

## Summary:
Initializes a Redis broker connection by setting default host/port values, preparing virtual host configuration, and establishing a Redis client instance.

## Description:
This constructor method configures the Redis broker instance by processing the broker URL to extract connection parameters, setting default values for host and port when not specified, preparing the virtual host configuration, and creating a Redis client connection. This method serves as the primary initialization entry point for Redis broker instances in the messaging system.

## Args:
    broker_url (str): The Redis broker URL containing connection information including host, port, and virtual host
    *args: Additional positional arguments passed to the parent class constructor
    **kwargs: Additional keyword arguments passed to the parent class constructor

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    None explicitly documented: The method relies on parent class initialization and Redis client creation which may raise exceptions from underlying libraries

## State Changes:
    Attributes READ: self.host, self.port, self.vhost
    Attributes WRITTEN: self.host, self.port, self.vhost, self.redis

## Constraints:
    Preconditions: The broker_url parameter must be a valid string that can be parsed for Redis connection information
    Postconditions: Instance attributes host, port, vhost, and redis are initialized with appropriate values

## Side Effects:
    I/O: Establishes network connection to Redis server
    External service calls: Creates Redis client connection via redis-py library

### `flower.utils.broker.Redis._prepare_virtual_host` · *method*

## Summary:
Converts and validates virtual host parameters for Redis connections into integer database indices.

## Description:
Processes virtual host parameters that may be provided as strings or integers, converting them to valid integer database indices between 0 and the database limit minus 1. This method ensures consistent handling of virtual host specifications across different input formats.

## Args:
    vhost (str or int): Virtual host specification which can be an integer, string representation of an integer, or string starting with '/' indicating a database index.

## Returns:
    int: Valid integer database index between 0 and limit - 1.

## Raises:
    ValueError: When vhost cannot be converted to an integer database index.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - vhost must be convertible to an integer database index
    - Database index must be between 0 and limit - 1
    
    Postconditions:
    - Returns an integer value representing a valid database index
    - Input vhost is not modified

## Side Effects:
    None

### `flower.utils.broker.Redis._get_redis_client_args` · *method*

## Summary:
Returns a dictionary of connection arguments for configuring a Redis client instance.

## Description:
This method extracts and formats connection parameters from the Redis instance's attributes into a dictionary suitable for passing to the redis.Redis constructor. It centralizes the configuration logic for Redis client creation, making the connection setup reusable and testable.

The method is called by `_get_redis_client()` during object initialization to create the primary Redis connection (`self.redis`). This separation of concerns allows for cleaner code organization and easier testing by enabling dependency injection of connection parameters.

## Args:
    None

## Returns:
    dict: A dictionary containing Redis connection parameters with keys:
        - 'host' (str): The Redis server hostname
        - 'port' (int): The Redis server port number
        - 'db' (int): The database index to connect to
        - 'username' (str): The username for authentication (may be None)
        - 'password' (str): The password for authentication (may be None)

## Raises:
    None

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Redis instance must have been initialized with a valid broker URL
    - All connection parameters (host, port, vhost, username, password) must be properly set
    - The redis library must be available and importable
    
    Postconditions:
    - Returns a dictionary with all required Redis connection parameters
    - The returned dictionary is suitable for unpacking as keyword arguments to redis.Redis()

## Side Effects:
    None

### `flower.utils.broker.Redis._get_redis_client` · *method*

## Summary:
Creates and returns a redis.Redis client instance configured with connection parameters from the broker configuration.

## Description:
This method constructs a redis.Redis client using connection parameters derived from the broker URL configuration. It serves as a factory method for creating Redis clients and is called during object initialization to set up the primary Redis connection (`self.redis`).

The method relies on `_get_redis_client_args()` to obtain connection parameters including host, port, database index, username, and password. This separation allows for clean configuration management and makes testing easier by enabling dependency injection of connection parameters.

## Args:
    None

## Returns:
    redis.Redis: A configured Redis client instance ready for database operations

## Raises:
    None explicitly raised by this method
    - redis.ConnectionError: May be raised by redis.Redis constructor if connection parameters are invalid
    - redis.AuthenticationError: May be raised by redis.Redis constructor if authentication fails

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Redis instance must have been initialized with a valid broker URL
    - Connection parameters (host, port, vhost, username, password) must be properly set
    - The redis library must be available and importable
    
    Postconditions:
    - Returns a valid redis.Redis client instance
    - The returned client is configured with the broker's connection parameters

## Side Effects:
    - Creates a new Redis client instance
    - May establish a network connection to the Redis server upon first use
    - No modifications to the Redis instance's state

## `flower.utils.broker.RedisSentinel` · *class*

## Summary:
RedisSentinel is a Redis broker implementation that connects to Redis Sentinel for high availability and failover capabilities.

## Description:
RedisSentinel provides a broker interface for Redis Sentinel deployments, enabling connection to Redis masters through Sentinel servers for high availability. It inherits from RedisBase and implements Redis-specific connection logic tailored for Sentinel environments. This class is typically used when Redis is configured in a master-slave topology with automatic failover capabilities managed by Redis Sentinel.

The class parses broker URLs to extract connection parameters, validates required Sentinel configuration (master_name), and establishes a Redis client connected to the current master node via Sentinel discovery.

## State:
- host (str): Redis Sentinel host address; defaults to 'localhost' if not specified in broker URL
- port (int): Redis Sentinel port; defaults to 26379 if not specified in broker URL  
- vhost (int): Redis database number; converted from broker URL path or defaults to 0
- master_name (str): Name of the Redis master service in Sentinel configuration; required parameter
- redis (redis.sentinel.Sentinel): Redis Sentinel client instance connected to the master

## Lifecycle:
- Creation: Instantiate with broker_url string and optional broker_options dictionary containing 'master_name' key
- Usage: Typically used for queue statistics operations through inherited methods from RedisBase
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[RedisSentinel.__init__] --> B[RedisSentinel._prepare_virtual_host]
    A --> C[RedisSentinel._prepare_master_name]
    A --> D[RedisSentinel._get_redis_client]
    D --> E[redis.sentinel.Sentinel]
    E --> F[Sentinel.master_for]
```

## Raises:
- ValueError: Raised when master_name is not provided in broker_options or when vhost cannot be converted to integer
- redis.exceptions.ConnectionError: Raised when unable to connect to Redis Sentinel server

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

# Use inherited queue methods
queue_stats = await broker.queues(["queue1", "queue2"])
```

### `flower.utils.broker.RedisSentinel.__init__` · *method*

## Summary:
Initializes a Redis Sentinel broker instance by setting up connection parameters and establishing a Redis client for master selection.

## Description:
This constructor configures a Redis Sentinel broker by processing the broker URL, preparing virtual host settings, extracting the master name from broker options, and creating a Redis client connected to the Sentinel service. It builds upon the parent class initialization to establish the connection configuration and then sets up the Redis Sentinel client for master discovery and connection management.

## Args:
    broker_url (str): The URL specifying the Redis Sentinel connection details including host, port, and virtual host.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Additional keyword arguments, including 'broker_options' which contains Redis-specific configuration.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: When 'master_name' is not provided in broker_options.
    ValueError: When virtual host cannot be converted to an integer.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.password, self._prepare_virtual_host, self._prepare_master_name, self._get_redis_client
    Attributes WRITTEN: self.host, self.port, self.vhost, self.master_name, self.redis

## Constraints:
    Preconditions: The broker_url must be a valid URL with proper Redis Sentinel format.
    Postconditions: Instance attributes host, port, vhost, master_name, and redis are properly initialized.

## Side Effects:
    Establishes network connections to Redis Sentinel server.
    Creates Redis Sentinel client instance for master discovery and connection management.

### `flower.utils.broker.RedisSentinel._prepare_virtual_host` · *method*

## Summary:
Converts virtual host parameter to integer database index for Redis Sentinel connections.

## Description:
Prepares and validates the virtual host parameter (database index) for Redis Sentinel connections. This method normalizes various input formats (None, '/', strings starting with '/', integers) into a valid integer database index between 0 and the Redis database limit.

The method is called during RedisSentinel initialization to process the vhost parameter extracted from the broker URL. It ensures that database indices are properly formatted for Redis operations while maintaining backward compatibility with different input formats.

## Args:
    vhost (str|int|None): Virtual host parameter that can be None, empty string, '/', a string representation of a number, or an integer.

## Returns:
    int: Integer database index between 0 and limit-1, where 0 is returned for None, empty string, or '/' inputs.

## Raises:
    ValueError: When vhost is a string that cannot be converted to an integer, with message indicating database must be an integer between 0 and limit-1.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Input vhost can be None, empty string, '/', a string starting with '/', or a numeric value
    Postconditions: Returned value is always an integer between 0 and limit-1 (inclusive)

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._prepare_master_name` · *method*

## Summary:
Extracts and validates the master name required for Redis Sentinel broker configuration.

## Description:
This method retrieves the master name from broker options dictionary, which is essential for establishing connections to Redis Sentinel clusters. It ensures that the master name is provided in the broker configuration, raising a clear error message if it's missing. This validation prevents runtime errors when attempting to connect to Redis Sentinel.

The method is called during RedisSentinel initialization to prepare the master name required for connecting to the Redis master node via Sentinel discovery.

## Args:
    broker_options (dict): Dictionary containing Redis broker configuration options, including the required 'master_name' key.

## Returns:
    str: The master name string extracted from broker_options.

## Raises:
    ValueError: Raised when 'master_name' key is not present in the broker_options dictionary, with a descriptive error message indicating that master_name is required for Sentinel broker.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - broker_options must be a dictionary-like object
    - broker_options must contain the 'master_name' key
    
    Postconditions:
    - Returns the master name string as specified in broker_options
    - Does not modify the broker_options dictionary

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._get_redis_client` · *method*

## Summary:
Creates and returns a Redis client connected to the master node via Redis Sentinel.

## Description:
This method establishes a connection to a Redis master node using the Redis Sentinel protocol. It constructs connection parameters including password and sentinel-specific options, initializes a Redis Sentinel client with the configured host and port, and retrieves a master client for the specified master name. This method is designed to be called during initialization to establish the Redis connection.

## Args:
    broker_options (dict): Dictionary containing Redis broker configuration options, including optional 'sentinel_kwargs' for additional sentinel configuration.

## Returns:
    redis.client.Redis: A Redis client instance connected to the master node through Sentinel.

## Raises:
    None explicitly raised, but may raise exceptions from redis.sentinel.Sentinel or redis.client.Redis initialization.

## State Changes:
    Attributes READ: self.host, self.port, self.password, self.master_name
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.host must be a valid hostname or IP address
    - self.port must be a valid port number
    - self.master_name must be set (typically done in _prepare_master_name)
    - broker_options must be a dictionary
    Postconditions: 
    - Returns a valid Redis client instance ready for use

## Side Effects:
    I/O: Connects to Redis Sentinel server at self.host:self.port
    External service call: Communicates with Redis Sentinel to discover master node

## `flower.utils.broker.RedisSocket` · *class*

## Summary:
RedisSocket is a Redis broker implementation that connects to Redis using Unix domain sockets instead of TCP connections.

## Description:
RedisSocket provides a specialized Redis broker interface that establishes connections to Redis servers via Unix domain sockets. This approach can offer better performance and security compared to traditional TCP connections, particularly when Redis is running on the same host. The class inherits from RedisBase, which in turn inherits from BrokerBase, providing standard broker functionality while specializing in Unix socket-based Redis connections.

This implementation is typically used in environments where Redis is configured to accept Unix socket connections, such as in containerized deployments or when optimizing for local communication performance. The class specifically constructs a Unix socket path using the vhost parameter from the broker URL.

## State:
- redis (redis.Redis): Redis client instance connected via Unix socket; initialized in __init__
- vhost (str): Virtual host path extracted from broker URL (without leading slash); used to construct unix socket path
- password (str): Password from broker URL, URL-decoded if present; used for Redis authentication
- host (str): Hostname extracted from broker URL; not used in this implementation but inherited from BrokerBase
- port (int): Port number extracted from broker URL; not used in this implementation but inherited from BrokerBase

## Lifecycle:
- Creation: Instantiate with a broker_url string that contains Redis connection parameters including host, port, vhost, username, and password components
- Usage: The redis client is automatically initialized during construction and ready for use
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[RedisSocket.__init__] --> B[RedisBase.__init__]
    B --> C[BrokerBase.__init__]
    C --> D[redis.Redis.__init__]
```

## Raises:
- redis.exceptions.ConnectionError: Raised when unable to connect to the Redis Unix socket
- redis.exceptions.AuthenticationError: Raised when Redis authentication fails with provided password
- ValueError: May be raised by redis.Redis if invalid parameters are provided
- TypeError: May be raised if broker_url is not a string or if parameters are improperly formatted

## Example:
```python
# Create RedisSocket instance using broker URL with Unix socket configuration
broker = RedisSocket("redis://user:password@localhost:6379/queue_name")

# The redis client is automatically available for direct Redis operations
# Note: vhost becomes the Unix socket path (e.g., "/queue_name" for vhost="queue_name")
redis_client = broker.redis

# Perform Redis operations directly
queue_length = redis_client.llen("my_queue")
```

### `flower.utils.broker.RedisSocket.__init__` · *method*

## Summary:
Initializes a RedisSocket broker connection by setting up Redis connection parameters and establishing a Redis client instance using Unix socket communication.

## Description:
Configures a RedisSocket instance by first parsing the broker URL through the parent class hierarchy (RedisBase -> BrokerBase) to extract connection parameters, then creating a Redis client that connects via Unix socket using the virtual host path and password credentials. This method establishes the foundation for Redis-based broker communication in Flower's monitoring system.

## Args:
    broker_url (str): The Redis broker URL containing connection information including host, port, virtual host, username, and password in standard URL format.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Additional keyword arguments passed to the parent class constructor.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: 
    - self.vhost: Extracted from broker URL path component by BrokerBase.__init__
    - self.password: Extracted from broker URL password component by BrokerBase.__init__
    
    Attributes WRITTEN:
    - self.redis: Set to a redis.Redis instance connected via Unix socket

## Constraints:
    Preconditions:
    - broker_url must be a valid URL format that can be parsed by urlparse
    - The redis library must be importable and available
    - The Unix socket path specified by '/' + self.vhost must exist and be accessible
    
    Postconditions:
    - All connection parameters are properly extracted and stored from the broker URL through BrokerBase.__init__
    - RedisBase.__init__ is called to initialize Redis-specific parameters
    - A Redis client instance is created and assigned to self.redis with Unix socket connection

## Side Effects:
    I/O: Establishes Unix socket connection to Redis server
    External service calls: Creates Redis client connection via redis-py library

## `flower.utils.broker.RedisSsl` · *class*

## Summary:
RedisSsl is a specialized Redis broker implementation that enables secure SSL/TLS connections to Redis servers, extending the Redis class with SSL configuration capabilities.

## Description:
The RedisSsl class provides a concrete implementation of a Redis broker that establishes encrypted connections to Redis servers using SSL/TLS protocols. It inherits from the Redis class (which itself inherits from RedisBase) and overrides connection configuration to enable SSL encryption for all Redis communications. This class is specifically designed for use with Redis broker URLs that begin with 'rediss://' (secure Redis protocol) and requires explicit SSL configuration parameters.

The class enforces that SSL configuration is provided through the 'broker_use_ssl' parameter, ensuring that secure connections are intentionally configured rather than accidentally disabled. This makes it suitable for production environments where Redis communication security is paramount.

## State:
- broker_use_ssl (dict): Dictionary containing SSL configuration parameters for Redis client connection. Must be provided during initialization and typically includes SSL certificate and authentication settings such as 'ssl_cert_reqs', 'ssl_ca_certs', etc.
- Inherits all attributes from Redis class including host, port, vhost, and redis client instance.

## Lifecycle:
- Creation: Instantiate with a broker URL string starting with 'rediss://' and a 'broker_use_ssl' keyword argument containing SSL configuration parameters
- Usage: Used for secure Redis broker operations such as queue statistics collection, similar to the parent Redis class
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[RedisSsl.__init__] --> B[Redis.__init__]
    B --> C[Redis._prepare_virtual_host]
    B --> D[Redis._get_redis_client]
    D --> E[Redis._get_redis_client_args]
    E --> F[RedisSsl._get_redis_client_args]
    F --> G[redis.Redis()]
```

## Raises:
- ValueError: Raised during initialization when 'broker_use_ssl' is not provided in kwargs, indicating that SSL configuration is required for secure Redis connections

## Example:
```python
# Create a secure Redis broker instance for production use
broker = RedisSsl(
    "rediss://secure-redis.example.com:6380/0",
    broker_use_ssl={
        'ssl_cert_reqs': 'required',
        'ssl_ca_certs': '/etc/ssl/certs/ca-certificates.crt',
        'ssl_keyfile': '/etc/ssl/private/client.key',
        'ssl_certfile': '/etc/ssl/certs/client.crt'
    }
)

# The broker automatically configures the underlying Redis client with:
# - ssl=True (enabling SSL/TLS encryption)
# - Additional SSL parameters from broker_use_ssl dictionary
# This ensures all communication with the Redis server is encrypted
```

### `flower.utils.broker.RedisSsl.__init__` · *method*

## Summary:
Initializes a RedisSsl broker connection with SSL configuration validation.

## Description:
Configures SSL settings for Redis broker connections and validates required SSL parameters. This method ensures that secure Redis connections (using rediss:// URLs) have proper SSL configuration before establishing connections.

## Args:
    broker_url (str): The Redis broker URL, typically starting with 'rediss://' for secure connections.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Keyword arguments including 'broker_use_ssl' which must be provided for secure connections.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    ValueError: Raised when 'broker_use_ssl' is not provided in kwargs, indicating that secure Redis connections require SSL configuration.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.broker_use_ssl

## Constraints:
    Preconditions: The 'broker_use_ssl' keyword argument must be provided when using secure Redis connections (rediss:// URLs).
    Postconditions: The instance will have self.broker_use_ssl properly set from the provided kwargs.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `flower.utils.broker.RedisSsl._get_redis_client_args` · *method*

## Summary:
Configures and returns Redis client connection arguments with SSL enabled for secure communication.

## Description:
This method extends the parent class's Redis client argument configuration by enabling SSL connections and incorporating custom SSL settings. It ensures that Redis connections use secure transport protocols while maintaining compatibility with existing connection parameters.

The method is called during Redis client instantiation to configure connection parameters for the redis.Redis client. It builds upon the base connection arguments provided by the parent class and adds SSL-specific configurations required for secure Redis connections.

## Args:
    None

## Returns:
    dict: A dictionary containing Redis connection parameters with SSL configuration:
        - Includes all standard Redis connection parameters from parent class (host, port, db, username, password)
        - 'ssl' (bool): Set to True to enable SSL/TLS encryption
        - Additional SSL parameters if self.broker_use_ssl is a dictionary

## Raises:
    None

## State Changes:
    Attributes READ: self.broker_use_ssl
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The RedisSsl instance must have been initialized with a valid broker URL
    - The broker_use_ssl parameter must be provided during initialization
    - The redis library must be available and importable
    
    Postconditions:
    - Returns a dictionary with all required Redis connection parameters including SSL settings
    - The returned dictionary is suitable for unpacking as keyword arguments to redis.Redis()

## Side Effects:
    None

## `flower.utils.broker.Broker` · *class*

## Summary:
Abstract base class that serves as a factory for creating specific broker implementations based on URL scheme.

## Description:
The Broker class implements a factory pattern that dynamically instantiates concrete broker implementations based on the scheme portion of a provided broker URL. This abstraction allows clients to work with different messaging systems (RabbitMQ, Redis variants) through a unified interface without needing to know the specific implementation details.

The class is designed to be instantiated with a broker URL that specifies the broker type and connection parameters. The URL scheme determines which concrete implementation is created:
- 'amqp' → RabbitMQ
- 'redis' → Redis  
- 'rediss' → RedisSsl
- 'redis+socket' → RedisSocket
- 'sentinel' → RedisSentinel

This pattern enables flexible broker configuration and supports various messaging backends in a consistent manner.

## State:
- broker_url (str): The connection URL that determines which broker implementation to create. This URL must contain a recognized scheme ('amqp', 'redis', 'rediss', 'redis+socket', or 'sentinel').

## Lifecycle:
- Creation: Instantiate with a broker_url string containing a recognized scheme. The __new__ method will delegate to the appropriate concrete broker class constructor.
- Usage: Once created, the broker instance can be used to call abstract methods like queues() that are implemented by the concrete subclass.
- Destruction: Cleanup is handled by the concrete implementation classes; no explicit cleanup is required from the Broker base class.

## Method Map:
```mermaid
graph TD
    A[Broker.__new__] --> B[RabbitMQ|Redis|RedisSsl|RedisSocket|RedisSentinel]
    B --> C[Broker.queues]
    C --> D[Concrete Implementation queues()]
```

## Raises:
- NotImplementedError: Raised when the broker URL scheme is not one of the supported schemes ('amqp', 'redis', 'rediss', 'redis+socket', 'sentinel'). This indicates that the requested broker type is not implemented or not supported.

## Example:
```python
# Create a Redis broker instance
redis_broker = Broker("redis://localhost:6379/0")

# Create a RabbitMQ broker instance  
rabbit_broker = Broker("amqp://user:pass@rabbitmq-server:5672/vhost")

# Both brokers support the same interface for queue operations
queue_stats = await redis_broker.queues(['queue1', 'queue2'])
queue_stats = await rabbit_broker.queues(['queue1', 'queue2'])
```

### `flower.utils.broker.Broker.__new__` · *method*

## Summary:
Factory method that creates and returns an instance of a specific broker implementation based on the URL scheme.

## Description:
This method serves as a factory for creating broker instances by inspecting the scheme portion of the provided broker URL and returning an appropriate concrete broker implementation. It enables polymorphic broker creation while maintaining a uniform interface for broker instantiation across different messaging systems.

The method is called during object construction when a Broker instance is created with a broker URL. It analyzes the URL scheme and delegates to the appropriate concrete broker class constructor (RabbitMQ, Redis, RedisSsl, RedisSocket, or RedisSentinel) based on the scheme prefix.

This factory pattern centralizes broker selection logic and allows users to specify broker type through URL scheme without needing to know the specific implementation details.

## Args:
    broker_url (str): Connection URL specifying the broker type and connection parameters. The URL scheme determines which concrete broker implementation is instantiated.
    *args: Additional positional arguments passed to the selected broker constructor.
    **kwargs: Additional keyword arguments passed to the selected broker constructor.

## Returns:
    BrokerBase subclass instance: Returns an instance of one of the concrete broker implementations (RabbitMQ, Redis, RedisSsl, RedisSocket, or RedisSentinel) based on the URL scheme.

## Raises:
    NotImplementedError: Raised when the broker URL scheme is not supported (i.e., not one of amqp, redis, rediss, redis+socket, or sentinel).

## State Changes:
    Attributes READ: None - this method only reads the scheme from the URL
    Attributes WRITTEN: None - this method doesn't modify any instance attributes

## Constraints:
    Preconditions: 
    - broker_url must be a valid string containing a recognized URL scheme
    - The URL scheme must be one of: 'amqp', 'redis', 'rediss', 'redis+socket', or 'sentinel'
    - All required broker-specific parameters must be present in the URL for successful instantiation
    
    Postconditions:
    - Returns an instance of a concrete broker subclass that implements the broker interface
    - The returned instance is fully initialized with connection parameters parsed from the URL

## Side Effects:
    None - This method performs no I/O operations or external service calls. It only creates objects and returns them.

### `flower.utils.broker.Broker.queues` · *method*

## Summary:
Retrieves message count statistics for a list of queue names by aggregating across priority levels.

## Description:
This asynchronous method calculates the total number of messages in each queue by querying all priority-specific queue names and summing their lengths. It's designed to provide comprehensive queue statistics for monitoring and management purposes. The method is declared as abstract in the base Broker class and must be implemented by concrete broker subclasses (such as Redis, RabbitMQ, etc.) to provide specific queue functionality.

## Args:
    names (list[str]): A list of queue names to retrieve statistics for

## Returns:
    list[dict]: A list of dictionaries, each containing:
        - 'name' (str): The queue name
        - 'messages' (int): Total message count across all priority levels for that queue

## Raises:
    NotImplementedError: Raised by the base Broker class when this method is called directly without a concrete implementation

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - This method should be implemented by concrete broker subclasses
    - Names parameter should be iterable containing valid queue names
    
    Postconditions:
    - Should return a list of dictionaries with consistent structure
    - Each dictionary contains 'name' and 'messages' keys
    - Message counts are aggregated across all priority levels for each queue
    - Returns empty list if names is empty

## Side Effects:
    None

## `flower.utils.broker.main` · *function*

## Summary:
Command-line entry point for retrieving and displaying queue statistics from a message broker.

## Description:
An asynchronous command-line utility that connects to a message broker (RabbitMQ, Redis, etc.) and retrieves queue statistics for specified queues. This function serves as the main execution point for a monitoring utility that provides insights into message queue states across different broker implementations through a unified interface.

The function expects command-line arguments in the format: [broker_url] [queue_name] [http_api] (optional). It creates a Broker instance with the provided configuration and queries queue information, printing results to stdout when queues are found.

## Args:
    None: This function reads command line arguments directly via sys.argv

## Returns:
    None: This function does not return a value. Instead, it prints queue statistics to standard output when queues are found.

## Raises:
    None: This function does not explicitly raise exceptions, though underlying broker operations may raise exceptions during connection or query execution.

## Constraints:
    Preconditions:
    - Command line arguments must be provided in the correct order: [broker_url] [queue_name] [http_api] (optional)
    - The broker URL must contain a recognized scheme ('amqp', 'redis', 'rediss', 'redis+socket', 'sentinel')
    - The queue name must be a valid identifier for the broker system
    - The HTTP API endpoint must be accessible if provided

    Postconditions:
    - If queues exist, their statistics are printed to stdout in JSON format
    - If no queues are found, nothing is printed
    - Function exits after processing regardless of success or failure
    - All network connections are managed by the underlying broker implementation

## Side Effects:
    - Prints queue statistics to standard output (stdout)
    - Makes network connections to the configured broker and HTTP API endpoints
    - May initiate connections to broker services (RabbitMQ, Redis, etc.)
    - Reads command line arguments from sys.argv

## Control Flow:
```mermaid
flowchart TD
    A[Start main()] --> B{Number of sys.argv arguments}
    B -->|≤ 1| C[Set broker_url = 'amqp://']
    B -->|> 1| D[Set broker_url = sys.argv[1]]
    C --> E{Number of sys.argv arguments}
    E -->|≤ 2| F[Set queue_name = 'celery']
    E -->|> 2| G[Set queue_name = sys.argv[2]]
    F --> H{Number of sys.argv arguments}
    H -->|≤ 3| I[Set http_api = 'http://guest:guest@localhost:15672/api/']
    H -->|> 3| J[Set http_api = sys.argv[3]]
    I --> K[Create Broker(broker_url, http_api=http_api)]
    J --> K
    K --> L[broker.queues([queue_name])]
    L --> M{queues result}
    M -->|True| N[print(queues)]
    M -->|False| O[Exit normally]
```

## Examples:
```bash
# Run with defaults (amqp:// broker, celery queue, localhost API)
python broker.py

# Connect to RabbitMQ with custom queue
python broker.py amqp://user:pass@localhost:5672/vhost my_queue

# Connect to Redis with custom queue and API endpoint
python broker.py redis://localhost:6379/0 my_queue http://admin:password@localhost:15672/api/

# Connect to Redis with default queue and API
python broker.py redis://localhost:6379/0
```

