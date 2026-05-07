# `broker.py`

## `flower.utils.broker.BrokerBase` · *class*

## Summary:
Abstract base class for message broker implementations that handles URL parsing and provides a common interface for queue operations.

## Description:
BrokerBase serves as the foundation for various message broker implementations (such as Redis, RabbitMQ, etc.) by providing standardized URL parsing and defining the interface for queue-related operations. It encapsulates connection details extracted from a broker URL and establishes a contract for asynchronous queue management operations.

This class exists to enforce a consistent abstraction layer across different messaging systems while allowing concrete implementations to handle the specifics of each broker type.

## State:
- host (str): The hostname portion extracted from the broker URL; may be None if not specified
- port (int or None): The port number extracted from the broker URL; defaults to None if not specified  
- vhost (str): The virtual host path extracted from the broker URL (with leading slash stripped)
- username (str or None): The decoded username from the broker URL; None if not provided
- password (str or None): The decoded password from the broker URL; None if not provided

All attributes are initialized during object construction and remain immutable throughout the instance's lifetime.

## Lifecycle:
- Creation: Instantiate with a valid broker URL string containing protocol, hostname, port, username, password, and virtual host components
- Usage: Call the `queues()` method asynchronously to retrieve queue information for specified queue names
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[BrokerBase.__init__] --> B[BrokerBase.queues]
    B --> C[NotImplementedError]
```

## Raises:
- TypeError: If broker_url is not a string type
- ValueError: If broker_url contains invalid URL format that cannot be parsed

## Example:
```python
# Create a broker instance
broker = BrokerBase("redis://user:pass@localhost:6379/0")

# Access parsed connection details
print(broker.host)   # localhost
print(broker.port)   # 6379
print(broker.vhost)  # 0

# Note: queues() raises NotImplementedError in base class
# Concrete implementations would override this method
```

### `flower.utils.broker.BrokerBase.__init__` · *method*

## Summary:
Initializes a BrokerBase instance by parsing the broker URL and extracting connection parameters.

## Description:
This method parses the provided broker URL to extract host, port, virtual host, username, and password components. It handles URL decoding for credentials and sets these values as instance attributes. This separation allows for clean configuration management and ensures proper handling of special characters in credentials.

## Args:
    broker_url (str): The URL string containing broker connection information in the format scheme://user:pass@host:port/virtual_host

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    AttributeError: If the broker_url cannot be parsed by urlparse, or if the parsed result lacks expected attributes.
    ValueError: If the broker_url is malformed or contains invalid characters.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.host, self.port, self.vhost, self.username, self.password

## Constraints:
    Preconditions: The broker_url parameter must be a valid string that can be parsed by urlparse.
    Postconditions: Instance attributes host, port, vhost, username, and password are set based on the parsed URL components.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `flower.utils.broker.BrokerBase.queues` · *method*

## Summary:
Retrieves detailed information about specified message queues from a broker system.

## Description:
This asynchronous abstract method provides a standardized interface for fetching queue metadata from various message broker implementations. It is designed to be overridden by concrete subclasses to implement broker-specific retrieval logic for different broker types (e.g., Redis, RabbitMQ). The method accepts a list of queue names and should return structured information about each queue's properties.

## Args:
    names (list[str]): A list of queue names to retrieve information for.

## Returns:
    This abstract method must be implemented by subclasses to return queue information. The return type and structure depends on the specific broker implementation but typically includes queue properties such as message counts, consumer counts, and configuration settings.

## Raises:
    NotImplementedError: This abstract method must be implemented by subclasses. Calling this base implementation directly will raise this exception.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method is designed to be called with valid queue names that exist in the broker system.
    Postconditions: Subclasses must ensure the returned data structure is consistent with the expected interface.

## Side Effects:
    None

## `flower.utils.broker.RabbitMQ` · *class*

## Summary:
RabbitMQ class provides an asynchronous interface for retrieving queue information from RabbitMQ's HTTP management API.

## Description:
The RabbitMQ class offers a concrete implementation for interacting with RabbitMQ's HTTP management API to fetch queue details. It leverages the URL parsing capabilities inherited from BrokerBase to extract connection parameters from a broker URL, and constructs appropriate HTTP requests to query queue information. This implementation is specifically designed for scenarios requiring programmatic access to RabbitMQ queue status through its management API.

The class builds upon the abstract foundation established by BrokerBase, which provides standardized URL parsing and defines the interface contract for queue operations, while RabbitMQ adds the specific HTTP-based implementation details.

## State:
- io_loop (tornado.ioloop.IOLoop): Event loop instance used for asynchronous operations; defaults to the global IOLoop instance if not provided
- host (str): Hostname for the RabbitMQ management API; defaults to 'localhost' if not specified in broker_url
- port (int): Port number for the RabbitMQ management API; defaults to 15672 if not specified in broker_url  
- vhost (str): Virtual host path for RabbitMQ; defaults to '/' if not specified in broker_url
- username (str): Username for HTTP authentication with RabbitMQ management API; defaults to 'guest'
- password (str): Password for HTTP authentication with RabbitMQ management API; defaults to 'guest'
- http_api (str): Fully constructed HTTP API endpoint URL for accessing RabbitMQ management API

All attributes are initialized during object construction and remain immutable throughout the instance's lifetime. The class inherits URL parsing capabilities from BrokerBase.

## Lifecycle:
- Creation: Instantiate with a broker_url string and optional http_api URL; if http_api is omitted, it's auto-generated using connection details from broker_url
- Usage: Call the `queues()` method asynchronously to retrieve queue information for specified queue names
- Destruction: No explicit cleanup required; relies on Python's garbage collection and proper closing of HTTP clients

## Method Map:
```mermaid
graph TD
    A[RabbitMQ.__init__] --> B[RabbitMQ.queues]
    B --> C[httpclient.AsyncHTTPClient.fetch]
```

## Raises:
- ValueError: When the provided http_api URL has an invalid scheme (not 'http' or 'https') or when the broker_url cannot be parsed
- socket.error: When HTTP connection fails due to network issues
- httpclient.HTTPError: When HTTP request fails with non-200 status codes

## Example:
```python
# Create RabbitMQ broker instance
broker = RabbitMQ("amqp://user:pass@localhost:5672/vhost", 
                  "http://user:pass@localhost:15672/api/vhost")

# Retrieve queue information asynchronously
queues = await broker.queues(['queue1', 'queue2'])

# Alternative: let the class auto-generate the API URL
broker2 = RabbitMQ("amqp://user:pass@localhost:5672/vhost")
# http_api will be auto-generated as http://user:pass@localhost:15672/api/vhost
```

### `flower.utils.broker.RabbitMQ.__init__` · *method*

## Summary:
Initializes a RabbitMQ broker instance by setting up connection parameters and HTTP API configuration.

## Description:
Configures the RabbitMQ broker with connection details derived from the broker URL and optional HTTP API settings. This method handles default value assignment for host, port, vhost, username, and password, and constructs or validates the HTTP API endpoint for management operations. It also ensures proper I/O loop setup for asynchronous operations.

## Args:
    broker_url (str): The URL for connecting to the RabbitMQ broker
    http_api (str): The HTTP API endpoint for RabbitMQ management interface
    io_loop (tornado.ioloop.IOLoop, optional): The I/O loop instance to use. Defaults to None.
    **kwargs (dict): Additional keyword arguments (ignored)

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    ValueError: When the http_api URL has an invalid scheme (not http or https)

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password, self.broker_url
    Attributes WRITTEN: self.io_loop, self.http_api

## Constraints:
    Preconditions: 
    - broker_url must be a valid string
    - http_api must be a valid URL string or None
    - self.host, self.port, self.vhost, self.username, self.password should be accessible attributes
    
    Postconditions:
    - self.io_loop is set to either the provided io_loop or a default IOLoop instance
    - self.http_api is set to either the provided http_api or a constructed default URL
    - All connection parameters have appropriate default values assigned

## Side Effects:
    - May log an error message if http_api validation fails
    - Creates a default IOLoop instance if none is provided

### `flower.utils.broker.RabbitMQ.queues` · *method*

## Summary:
Retrieves filtered queue information from the RabbitMQ management API for specified queue names.

## Description:
This asynchronous method fetches queue details from RabbitMQ's management HTTP API and filters the results to only include queues whose names match the provided list. It handles authentication parsing from the API URL and manages HTTP connection errors gracefully by returning an empty list. The method is part of the RabbitMQ broker integration in Flower monitoring tool, used to retrieve specific queue information for monitoring purposes.

## Args:
    names (list[str]): A list of queue names to filter the results by

## Returns:
    list[dict]: A list of queue information dictionaries containing details about matching queues, or an empty list if the API call fails

## Raises:
    httpclient.HTTPError: When the HTTP request succeeds but returns an error status code (other than 200)

## State Changes:
    Attributes READ: self.http_api, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.http_api must be a valid URL string pointing to RabbitMQ management API
    - self.vhost must be a valid virtual host identifier
    - names must be a list of strings
    Postconditions:
    - Returns a list of queue dictionaries matching the provided names
    - On HTTP failure, returns empty list without raising exception

## Side Effects:
    - Makes an asynchronous HTTP GET request to the RabbitMQ management API
    - Logs error messages to the logger when HTTP requests fail

### `flower.utils.broker.RabbitMQ.validate_http_api` · *method*

## Summary:
Validates that an HTTP API endpoint uses a supported protocol scheme (http or https).

## Description:
This class method validates whether the provided HTTP API endpoint string uses either 'http' or 'https' as its URL scheme. It is called during RabbitMQ broker initialization to ensure the HTTP API endpoint is properly formatted with a supported protocol. This validation prevents the use of insecure or unsupported schemes that could cause connection failures or security issues.

## Args:
    cls: The RabbitMQ class (required for class method decorator)
    http_api (str): A string representing the HTTP API endpoint URL to validate

## Returns:
    None: This method does not return any value

## Raises:
    ValueError: Raised when the URL scheme is not 'http' or 'https', with descriptive error message

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The http_api parameter must be a string
    - The string must be a valid URL format that can be parsed by urlparse
    
    Postconditions:
    - If validation passes, the http_api string contains a valid 'http' or 'https' scheme
    - If validation fails, a ValueError is raised with descriptive message

## Side Effects:
    None: This method performs no I/O operations or external service calls

## `flower.utils.broker.RedisBase` · *class*

## Summary:
Abstract base class for Redis-based message broker implementations that provides queue management capabilities with priority support.

## Description:
RedisBase extends BrokerBase to provide a foundation for Redis-backed message brokers. It handles Redis-specific configuration such as priority steps, separators, and key prefixes, while maintaining a standardized interface for queue operations. This class is designed to be subclassed by concrete Redis implementations that handle the actual Redis connection and command execution.

The motivation for this abstraction is to separate Redis-specific configuration and utility methods from the core broker interface, enabling consistent handling of priority-based queues while allowing different Redis connection strategies.

## State:
- redis (redis.Redis or None): Redis client instance; initialized to None and expected to be set by subclasses
- priority_steps (list[int]): Priority levels supported for queue operations; defaults to [0, 3, 6, 9]
- sep (str): Separator character used to construct priority-based queue keys; defaults to '\x06\x16'  
- broker_prefix (str): Global prefix applied to all Redis keys; defaults to empty string

## Lifecycle:
- Creation: Instantiate with a broker URL string and optional broker_options dictionary containing priority_steps, sep, and global_keyprefix
- Usage: Typically used as part of a larger broker implementation where redis connection is established by subclasses, then queues() method is called asynchronously
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[RedisBase.__init__] --> B[RedisBase._q_for_pri]
    B --> C[RedisBase.queues]
```

## Raises:
- ImportError: When the redis library is not available in the environment
- ValueError: When attempting to construct a queue name with a priority not in configured priority_steps

## Example:
```python
# Initialize RedisBase with broker options
broker = RedisBase(
    "redis://localhost:6379/0",
    broker_options={
        'priority_steps': [0, 5, 9],
        'sep': '|',
        'global_keyprefix': 'myapp:'
    }
)

# The _q_for_pri method constructs priority-based queue names
queue_name = broker._q_for_pri('tasks', 3)  # Returns 'tasks|3'

# The queues method retrieves message counts for multiple queues
# (requires redis connection to be established by subclass implementation)
```

### `flower.utils.broker.RedisBase.__init__` · *method*

## Summary:
Initializes a RedisBase instance by setting up connection parameters and configuration options from broker settings.

## Description:
This method configures the Redis broker connection by extracting settings from the broker URL and optional broker_options dictionary. It initializes the Redis client to None and sets various configuration parameters like priority steps, separator, and key prefix based on the provided options. This method is part of the Redis broker base class that provides common functionality for Redis-based message queuing systems.

The parent BrokerBase class handles basic URL parsing to extract host, port, and virtual host information from the broker URL. This initialization method extends that by adding Redis-specific configuration options.

## Args:
    broker_url (str): The URL of the Redis broker to connect to.
    *_: Accepts additional positional arguments but ignores them.
    **kwargs: Keyword arguments that may contain broker_options dictionary.

## Returns:
    None: This method does not return a value.

## Raises:
    ImportError: When the redis library is not available or importable.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.redis: Set to None initially (Redis connection is not established here)
        - self.priority_steps: Set from broker_options or defaults (class constant DEFAULT_PRIORITY_STEPS)
        - self.sep: Set from broker_options or defaults (class constant DEFAULT_SEP)
        - self.broker_prefix: Set from broker_options or defaults

## Constraints:
    Preconditions:
        - The redis library must be importable
        - broker_url must be a valid string
    Postconditions:
        - self.redis is initialized to None (connection not yet established)
        - Configuration parameters are set based on broker_options or defaults
        - The parent BrokerBase class is properly initialized with broker_url, setting host, port, and vhost attributes

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `flower.utils.broker.RedisBase._q_for_pri` · *method*

## Summary:
Constructs a prioritized queue name by combining a base queue name with a priority suffix.

## Description:
This method formats a queue name with an optional priority suffix, ensuring the priority is valid according to the instance's configured priority steps. It's used internally by the Redis broker to manage queue names for different priority levels.

## Args:
    queue (str): The base queue name to be formatted.
    pri (int or None): The priority level to append to the queue name. Must be one of the values in self.priority_steps. If None, no priority suffix is added.

## Returns:
    str: A formatted queue name with priority suffix if pri is provided, otherwise returns the base queue name unchanged.

## Raises:
    ValueError: When the provided priority value is not found in self.priority_steps.

## State Changes:
    Attributes READ: self.priority_steps, self.sep
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The pri argument must be either None or a value present in self.priority_steps
    - self.priority_steps must be initialized and contain valid priority values
    - self.sep must be initialized and represent a string separator
    Postconditions:
    - Returns a properly formatted queue name string
    - The returned string follows the pattern: queue + sep + pri when pri is not None
    - The returned string equals queue when pri is None

## Side Effects:
    None

### `flower.utils.broker.RedisBase.queues` · *method*

## Summary:
Retrieves message counts for multiple Redis queues across different priority levels.

## Description:
This asynchronous method calculates the total number of messages in each specified queue by aggregating message counts from all priority-specific queue variants. It's used to provide queue statistics for monitoring and management purposes.

## Args:
    names (list[str]): A list of queue names for which to retrieve message counts.

## Returns:
    list[dict]: A list of dictionaries containing queue statistics, where each dictionary has:
        - 'name' (str): The queue name
        - 'messages' (int): Total message count across all priority levels for that queue. Returns 0 for non-existent queues.

## Raises:
    ValueError: When a priority value in self.priority_steps is not valid (though this would be caught earlier in _q_for_pri)
    redis.exceptions.ConnectionError: When Redis connection fails during llen operations
    redis.exceptions.TimeoutError: When Redis operations timeout during llen operations

## State Changes:
    Attributes READ: self.broker_prefix, self.priority_steps, self.redis
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.priority_steps must be initialized with valid priority values
    - self.redis must be connected and accessible
    - Each name in names must be a valid string
    Postconditions:
    - Returns a list of statistics dictionaries matching the input names order
    - Each message count represents the sum across all priority levels for that queue
    - Non-existent queues return 0 messages

## Side Effects:
    - Performs multiple Redis operations (llen) to fetch message counts
    - May cause network I/O delays depending on Redis server response times

## `flower.utils.broker.Redis` · *class*

## Summary:
Redis class implements a Redis-based message broker that manages connections to Redis servers for queue operations.

## Description:
The Redis class extends RedisBase to provide a concrete implementation of a Redis-backed message broker. It handles Redis-specific configuration such as host, port, and virtual host (database) selection, and creates Redis client instances for communication with Redis servers. This class is designed to be used as part of a larger broker infrastructure where message queuing operations are performed against Redis.

The motivation for this abstraction is to encapsulate Redis connection management and configuration within a dedicated class, separating it from the core broker interface defined in RedisBase. This allows for consistent handling of Redis-specific parameters while maintaining a standardized interface for queue operations.

## State:
- host (str): Redis server hostname or IP address; defaults to 'localhost' if not specified in broker URL
- port (int): Redis server port number; defaults to 6379 if not specified in broker URL  
- vhost (int): Redis database index (0-15 by default); processed through _prepare_virtual_host method
- redis (redis.Redis): Configured Redis client instance for database operations; created during initialization

## Lifecycle:
- Creation: Instantiate with a broker URL string; host, port, and vhost are parsed from the URL, with defaults applied if missing
- Usage: The redis attribute provides access to a configured Redis client for performing database operations
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Redis.__init__] --> B[Redis._prepare_virtual_host]
    A --> C[Redis._get_redis_client]
    B --> D[Redis._get_redis_client_args]
    C --> D
```

## Raises:
- ValueError: When vhost cannot be converted to a valid integer database index (e.g., non-numeric string)
- redis.exceptions.ConnectionError: When Redis server is unreachable or connection fails
- redis.exceptions.AuthenticationError: When authentication credentials are invalid
- redis.exceptions.TimeoutError: When connection or command execution times out

## Example:
```python
# Create Redis broker instance
broker = Redis("redis://localhost:6379/0")

# Access the configured Redis client
redis_client = broker.redis

# Perform Redis operations using the client
redis_client.set("key", "value")
result = redis_client.get("key")
```

### `flower.utils.broker.Redis.__init__` · *method*

## Summary:
Initializes a Redis broker instance by configuring connection parameters, setting defaults, and establishing a Redis client connection.

## Description:
This method initializes the Redis broker by calling the parent class constructor to parse the broker URL, setting default host ('localhost') and port (6379) values when not specified, preparing the virtual host identifier for database selection, and creating a Redis client instance for communication with the Redis server. It is part of the broker initialization lifecycle in the Flower monitoring system.

## Args:
    broker_url (str): The URL specifying the Redis connection details including host, port, and virtual host.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Additional keyword arguments passed to the parent class constructor.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: Raised when the virtual host parameter cannot be converted to an integer and is not a valid database identifier.
    ImportError: Raised when the redis library is not available.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: self.host, self.port, self.vhost, self.redis

## Constraints:
    Preconditions: The broker_url must be a valid string that can be parsed by the parent class, and the redis library must be installed.
    Postconditions: The instance will have properly initialized self.host, self.port, self.vhost, and self.redis attributes with appropriate default values.

## Side Effects:
    I/O: Establishes a network connection to the Redis server via the redis-py client.
    External service calls: Connects to the Redis server using the provided connection parameters.

### `flower.utils.broker.Redis._prepare_virtual_host` · *method*

## Summary:
Converts a virtual host identifier to an integer database index for Redis connections, handling various input formats and default cases.

## Description:
This method processes the virtual host parameter and normalizes it to an integer database index suitable for Redis connections. It handles string representations of database indices, default values, and validates that the result is within acceptable bounds for Redis database selection.

The method is called during Redis connection initialization to ensure that virtual host identifiers are properly converted regardless of their input format (string, numeric, or special cases like '/' or None). This approach centralizes the conversion logic and ensures consistency across different Redis implementations.

Known callers:
- Redis.__init__: Called during Redis instance initialization to process the vhost parameter before creating the Redis client

## Args:
    vhost (Union[int, str, None]): Virtual host identifier which can be an integer, string representation of an integer, or special values like '/', None, or empty string.

## Returns:
    int: Integer database index for Redis connection, typically between 0 and the maximum database limit minus 1.

## Raises:
    ValueError: When vhost cannot be converted to a valid integer database index, specifically when it's a non-numeric string that doesn't represent a valid database number.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - Input vhost must be either an integer, string, or None/empty value
        - If vhost is a string, it must either be convertible to an integer or represent a special case ('/' or empty)
    Postconditions:
        - Returned value is always an integer
        - Returned value represents a valid Redis database index (0 to limit-1)

## Side Effects:
    None

### `flower.utils.broker.Redis._get_redis_client_args` · *method*

## Summary:
Returns a dictionary of Redis client connection arguments constructed from instance attributes.

## Description:
This method extracts connection configuration from the Redis broker instance and packages it into a dictionary suitable for initializing a Redis client. It is called during Redis client instantiation to provide connection parameters.

## Args:
    None

## Returns:
    dict: A dictionary containing Redis connection parameters with keys 'host', 'port', 'db', 'username', and 'password'.

## Raises:
    None

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password

## Constraints:
    Preconditions: All instance attributes (host, port, vhost, username, password) must be properly initialized before calling this method.
    Postconditions: The returned dictionary contains exactly the five connection parameters needed for Redis client initialization.

## Side Effects:
    None

### `flower.utils.broker.Redis._get_redis_client` · *method*

## Summary:
Creates and returns a Redis client instance configured with connection parameters derived from the broker configuration.

## Description:
This method serves as a factory for Redis client instances, encapsulating the logic for constructing a redis.Redis object using parameters obtained from the `_get_redis_client_args` method. It is designed to be called during object initialization and whenever a fresh Redis client instance is required. The method leverages the parent class's broker configuration to establish a connection to the Redis server.

## Args:
    None

## Returns:
    redis.Redis: A configured Redis client instance ready for database operations.

## Raises:
    redis.exceptions.ConnectionError: If the Redis server is unreachable or connection fails.
    redis.exceptions.AuthenticationError: If authentication credentials are invalid.
    redis.exceptions.TimeoutError: If the connection or command execution times out.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Redis connection parameters (host, port, vhost, username, password) must be properly initialized on the object. The redis library must be available.
    Postconditions: A valid redis.Redis client instance is returned, configured with the current broker settings.

## Side Effects:
    I/O: Establishes a network connection to the Redis server upon client instantiation.
    External service calls: Connects to the Redis database server.

## `flower.utils.broker.RedisSentinel` · *class*

## Summary:
RedisSentinel is a Redis broker implementation that connects to Redis master nodes through Redis Sentinel for high availability and failover support.

## Description:
RedisSentinel provides a concrete implementation of a Redis-based message broker that leverages Redis Sentinel for automatic failover detection and master node discovery. It extends RedisBase to inherit Redis-specific configuration and utility methods while implementing Redis Sentinel-specific connection logic. This class is intended to be used in distributed systems requiring resilient Redis connectivity where master nodes can fail over to slave nodes transparently.

The motivation for this abstraction is to provide a robust Redis broker implementation that automatically handles Redis master failovers through the Sentinel protocol, ensuring continuous operation even when the primary Redis instance becomes unavailable.

## State:
- host (str): Redis Sentinel host address; defaults to 'localhost' if not specified in broker_url
- port (int): Redis Sentinel port number; defaults to 26379 if not specified in broker_url  
- vhost (int): Redis database index; converted from string or integer virtual host identifier
- master_name (str): Name of the Redis master node to connect to via Sentinel
- redis (redis.Redis): Redis client instance connected to the master node through Sentinel

## Lifecycle:
- Creation: Instantiate with a broker URL string and optional broker_options dictionary containing master_name and sentinel_kwargs
- Usage: Typically used as part of a larger broker implementation where the Redis connection is established during initialization, then queue operations are performed through inherited methods from RedisBase
- Destruction: No explicit cleanup required; relies on Python's garbage collection

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
- ValueError: When master_name is not provided in broker_options or when vhost cannot be converted to a valid database index
- redis.exceptions.ConnectionError: When unable to connect to the Redis Sentinel server
- redis.exceptions.AuthenticationError: When authentication fails with the Redis Sentinel server
- redis.exceptions.TimeoutError: When the connection to the Redis Sentinel server times out
- redis.exceptions.MasterNotFoundError: When the specified master name is not found in the Sentinel configuration

## Example:
```python
# Initialize RedisSentinel with broker URL and options
broker = RedisSentinel(
    "redis://:password@sentinel-host:26379/0",
    broker_options={
        'master_name': 'mymaster',
        'sentinel_kwargs': {'socket_timeout': 0.1}
    }
)

# The broker is now ready to perform Redis operations
# through the connected redis client instance
```

### `flower.utils.broker.RedisSentinel.__init__` · *method*

## Summary:
Initializes a Redis Sentinel broker connection with host, port, virtual host, master name, and Redis client.

## Description:
This method sets up the Redis Sentinel connection by processing the broker URL, extracting connection parameters, and initializing the Redis client for communicating with the Redis master instance via the Sentinel discovery mechanism. It ensures proper configuration of host, port, virtual host database, and master name required for Sentinel-based Redis connections. This method is part of the RedisSentinel class initialization process and prepares the instance for subsequent Redis operations.

## Args:
    broker_url (str): The URL specifying the Redis Sentinel connection details.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Additional keyword arguments, including 'broker_options' for Sentinel-specific settings.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    ValueError: Raised when 'master_name' is not provided in broker_options, or when the virtual host cannot be converted to an integer.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.password
    Attributes WRITTEN: self.host, self.port, self.vhost, self.master_name, self.redis

## Constraints:
    Preconditions: The broker_url must be properly formatted, and broker_options must contain 'master_name' for Sentinel configuration.
    Postconditions: Instance attributes host, port, vhost, master_name, and redis are initialized with appropriate values.

## Side Effects:
    Establishes a connection to the Redis Sentinel server and retrieves a Redis client for master instance communication.

### `flower.utils.broker.RedisSentinel._prepare_virtual_host` · *method*

## Summary:
Converts virtual host identifier to integer database index for Redis connections.

## Description:
Processes virtual host parameter that can be provided as string or integer, converting it to a valid integer database index between 0 and limit-1. Handles special cases including empty strings, forward slashes, and string representations of integers. This method ensures consistent database index conversion across Redis operations.

## Args:
    vhost (str or int): Virtual host identifier which can be an integer, string representation of an integer, or path-like string starting with '/'

## Returns:
    int: Integer database index between 0 and limit-1

## Raises:
    ValueError: When vhost cannot be converted to an integer database index

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: vhost must be convertible to an integer database index
    Postconditions: Returned value is always an integer in the valid range [0, limit-1]

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._prepare_master_name` · *method*

## Summary:
Extracts and validates the Redis master name from broker configuration options for Sentinel-based broker setup.

## Description:
This method serves as a validation and extraction utility that retrieves the required 'master_name' parameter from the broker options dictionary. It is called during the initialization or configuration phase of a Redis Sentinel broker connection to ensure proper setup before establishing connections.

## Args:
    broker_options (dict): Dictionary containing broker configuration options, including the required 'master_name' key.

## Returns:
    str: The Redis master name extracted from the broker options.

## Raises:
    ValueError: When the 'master_name' key is missing from the broker_options dictionary.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The broker_options parameter must be a dictionary containing the 'master_name' key.
    Postconditions: The returned value is guaranteed to be a string representing the Redis master name.

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._get_redis_client` · *method*

## Summary:
Initializes a Redis Sentinel client and returns a Redis client connected to the master node for the configured master name.

## Description:
This method creates a Redis Sentinel client using the instance's host, port, password, and sentinel_kwargs configuration, then returns a Redis client instance connected to the master node identified by the instance's master_name. This enables the RedisSentinel class to establish a connection to the Redis master node through the Sentinel discovery mechanism.

## Args:
    broker_options (dict): Dictionary containing Redis broker configuration options, including sentinel_kwargs for additional sentinel connection parameters.

## Returns:
    redis.Redis: A Redis client instance connected to the master node of the Sentinel cluster.

## Raises:
    redis.exceptions.ConnectionError: If unable to connect to the Redis Sentinel server.
    redis.exceptions.AuthenticationError: If authentication fails with the Redis Sentinel server.
    redis.exceptions.TimeoutError: If the connection to the Redis Sentinel server times out.
    redis.exceptions.MasterNotFoundError: If the specified master name is not found in the Sentinel configuration.

## State Changes:
    Attributes READ: self.host, self.port, self.password, self.master_name
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.host must be a valid hostname or IP address
    - self.port must be a valid port number for the Redis Sentinel service
    - self.password must be a valid password string if authentication is required
    - self.master_name must be a valid name of a master node in the Sentinel configuration
    - broker_options must be a dictionary that may contain sentinel_kwargs

    Postconditions:
    - Returns a valid Redis client instance connected to the master node
    - The returned client can be used for Redis operations on the master node

## Side Effects:
    - Establishes a network connection to the Redis Sentinel server
    - May perform DNS resolution of the host address
    - Makes a connection to the Redis master node via Sentinel

## `flower.utils.broker.RedisSocket` · *class*

## Summary:
RedisSocket is a concrete implementation of RedisBase that establishes Redis connections using Unix domain sockets for improved performance and security.

## Description:
RedisSocket provides a Redis broker implementation that connects to Redis via Unix domain sockets instead of TCP connections. This approach offers better performance and security by eliminating network overhead and reducing attack surface. The class inherits from RedisBase and implements the Redis connection strategy using unix_socket_path configuration.

This abstraction exists to provide a specialized Redis connection mechanism that leverages Unix sockets, which is particularly beneficial in containerized environments or when Redis is running locally on the same host. It is designed to work with broker URLs that specify Unix socket paths.

## State:
- redis (redis.Redis): Redis client instance configured with unix_socket_path and password
- vhost (str): Extracted from broker_url, represents the Unix socket path prefix (available through parent class)
- password (str or None): Password extracted from broker_url for authentication (available through parent class)

## Lifecycle:
- Creation: Instantiated with a broker_url string that specifies a Unix socket path; requires proper URL format with unix socket path
- Usage: Typically used as part of a message broker system where Redis operations are performed through the inherited queue management methods
- Destruction: Relies on Python's garbage collection for cleanup

## Method Map:
```mermaid
graph TD
    A[RedisSocket.__init__] --> B[RedisBase.__init__]
    B --> C[RedisBase._q_for_pri]
    C --> D[RedisBase.queues]
```

## Raises:
- ValueError: When broker_url does not contain a valid unix socket path or when Redis connection parameters are invalid
- redis.ConnectionError: When unable to establish connection to the Redis Unix socket
- redis.AuthenticationError: When Redis authentication fails with provided password
- ImportError: When the redis library is not available in the environment

## Example:
```python
# Create RedisSocket instance with Unix socket broker URL
broker = RedisSocket("redis+socket:///var/run/redis/redis.sock?password=mypass")

# The redis client is automatically configured with:
# - unix_socket_path='/var/run/redis/redis.sock'
# - password='mypass'
```

### `flower.utils.broker.RedisSocket.__init__` · *method*

## Summary:
Initializes a RedisSocket instance by establishing a Redis connection using Unix socket path and password from the broker URL.

## Description:
This method initializes the RedisSocket object by first delegating to the parent class constructor to parse the broker URL and extract connection parameters. It then creates a Redis client instance using a Unix socket path constructed from the vhost component of the broker URL and the password extracted from the broker URL. This approach allows for efficient Unix socket-based Redis connections.

## Args:
    broker_url (str): The URL specifying the broker connection details including hostname, port, vhost, username, and password.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Additional keyword arguments passed to the parent class constructor.

## Returns:
    None: This method does not return a value.

## Raises:
    ImportError: If the redis library is not available (checked in parent class RedisBase.__init__).

## State Changes:
    Attributes READ: self.vhost, self.password
    Attributes WRITTEN: self.redis

## Constraints:
    Preconditions: 
    - The broker_url must be a valid URL containing the necessary components (hostname, path, username, password).
    - The redis library must be installed and importable.
    Postconditions:
    - self.redis is initialized as a redis.Redis instance with Unix socket connection.
    - self.vhost and self.password are properly set from the broker URL.

## Side Effects:
    - Creates a Redis connection using a Unix socket path.
    - Accesses the redis library to create a Redis client instance.

## `flower.utils.broker.RedisSsl` · *class*

## Summary:
RedisSsl class extends the Redis base class to provide SSL-enabled Redis broker functionality for secure communication.

## Description:
The RedisSsl class is a specialized subclass of Redis that adds SSL/TLS support for Redis connections. It requires the broker_use_ssl parameter to be provided during instantiation and configures the underlying Redis client to use SSL connections. This class is intended for use with Redis brokers that require secure SSL connections.

The motivation for this abstraction is to provide a clean mechanism for SSL configuration while inheriting all Redis connection management capabilities from the parent class.

## State:
- broker_use_ssl (dict): Dictionary containing SSL configuration options; must be provided during instantiation; contains SSL-related parameters like certificates, keys, and verification settings
- Inherits all attributes from Redis base class including host, port, vhost, and redis client instance

## Lifecycle:
- Creation: Must be instantiated with a broker_url and broker_use_ssl keyword argument; raises ValueError if broker_use_ssl is missing
- Usage: Functions identically to Redis base class after initialization, providing secure Redis client access via the inherited redis attribute
- Destruction: Inherits cleanup behavior from Redis base class; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[RedisSsl.__init__] --> B[Redis.__init__]
    A --> C[RedisSsl._get_redis_client_args]
    B --> D[Redis._get_redis_client_args]
    C --> D
```

## Raises:
- ValueError: Raised when broker_use_ssl keyword argument is not provided during instantiation
- redis.exceptions.ConnectionError: When connection to Redis server fails (including SSL connection failures)
- redis.exceptions.AuthenticationError: When authentication credentials are invalid (including SSL authentication failures)
- redis.exceptions.TimeoutError: When connection or command execution times out

## Example:
```python
# Create SSL-enabled Redis broker instance
broker = RedisSsl("rediss://localhost:6379/0", broker_use_ssl={
    'ssl_cert_reqs': 'required',
    'ssl_ca_certs': '/path/to/ca.crt'
})

# Access the configured secure Redis client
redis_client = broker.redis

# Perform Redis operations using the client
redis_client.set("secure_key", "secure_value")
result = redis_client.get("secure_key")
```

### `flower.utils.broker.RedisSsl.__init__` · *method*

## Summary:
Initializes a RedisSsl broker instance with SSL configuration and establishes connection parameters.

## Description:
This method sets up the SSL configuration for a Redis broker connection by requiring the 'broker_use_ssl' parameter. It ensures proper initialization of the parent Redis class with the provided broker URL and additional arguments. This method is part of the RedisSsl class lifecycle and prepares the object for secure Redis communication. The RedisSsl class extends the base Redis class to provide SSL-enabled connections, specifically designed for 'rediss' protocol brokers.

## Args:
    broker_url (str): The URL of the Redis broker including scheme and credentials. Must use 'rediss://' scheme for SSL connections.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Keyword arguments including 'broker_use_ssl' which is required for SSL connections. This parameter specifies SSL configuration options.

## Returns:
    None: This method initializes the object state but does not return a value.

## Raises:
    ValueError: Raised when 'broker_use_ssl' is not provided in kwargs, indicating that SSL is required for rediss broker connections.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.broker_use_ssl: Set to the value of 'broker_use_ssl' from kwargs or an empty dict if not provided

## Constraints:
    Preconditions:
        - The 'broker_use_ssl' keyword argument must be provided when initializing a RedisSsl instance
        - The broker_url parameter must be a valid string representing a Redis connection URL with 'rediss://' scheme
        - The Redis class parent must be properly initialized with the broker URL
    
    Postconditions:
        - The self.broker_use_ssl attribute is initialized with the provided SSL configuration
        - The parent Redis class is properly initialized with the broker_url and additional arguments
        - The RedisSsl instance is ready for SSL-enabled Redis operations

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state and delegates to the parent class initialization.

### `flower.utils.broker.RedisSsl._get_redis_client_args` · *method*

## Summary:
Configures and returns Redis client arguments with SSL enabled for secure connections.

## Description:
This method extends the parent class's Redis client argument configuration by enabling SSL connections and incorporating additional SSL-specific settings. It is called during Redis client creation to ensure secure communication with Redis servers.

The method is separated from inline logic to allow for clean extension of Redis client configuration while maintaining the base functionality. It ensures that SSL is enabled and allows custom SSL parameters to be passed through the broker_use_ssl configuration.

Known callers:
- Redis._get_redis_client: Called during Redis client instantiation to provide connection parameters for SSL-enabled Redis connections.

## Args:
    None

## Returns:
    dict: A dictionary containing Redis client connection arguments with SSL enabled and potentially custom SSL parameters.

## Raises:
    None

## State Changes:
    Attributes READ: self.broker_use_ssl
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The RedisSsl instance must have been initialized with a broker_use_ssl parameter.
    Postconditions: The returned dictionary includes 'ssl': True and may contain additional SSL configuration from broker_use_ssl.

## Side Effects:
    None

## `flower.utils.broker.Broker` · *class*

## Summary:
Broker is an abstract base class that provides a unified interface for different message broker implementations, dynamically creating instances of concrete broker subclasses based on URL schemes.

## Description:
The Broker class serves as a factory and abstract base class for message broker implementations, enabling polymorphic instantiation of different messaging systems (RabbitMQ, Redis, Redis SSL, Redis Socket, Redis Sentinel) through a single interface. It uses the URL scheme to determine which concrete implementation to instantiate, making it easy to switch between different broker technologies without changing client code.

This abstraction exists to provide a consistent interface for queue operations across different messaging backends while allowing each backend to implement its own specific connection and communication logic. The class is designed to be extended by concrete broker implementations that handle the actual messaging protocol details.

## State:
- broker_url (str): Connection URL specifying the broker type and connection parameters; used to determine the concrete implementation to instantiate
- scheme (str): Extracted from broker_url using urlparse; determines which concrete broker subclass to create
- All other attributes are defined in the concrete subclasses (RabbitMQ, Redis, RedisSsl, RedisSocket, RedisSentinel)

## Lifecycle:
- Creation: Called via `Broker(broker_url, ...)` which triggers `__new__` to select and instantiate the appropriate concrete subclass
- Usage: Once instantiated, the concrete broker instance provides queue operations through its `queues()` method
- Destruction: Cleanup handled by the concrete subclass implementations or Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Broker.__new__] --> B[RabbitMQ]
    A --> C[Redis]
    A --> D[RedisSsl]
    A --> E[RedisSocket]
    A --> F[RedisSentinel]
    B --> G[Broker.queues]
    C --> G
    D --> G
    E --> G
    F --> G
```

## Raises:
- NotImplementedError: Raised by `__new__` when the broker URL scheme is not supported (not one of amqp, redis, rediss, redis+socket, sentinel)
- NotImplementedError: Raised by `queues()` method in the base class (must be overridden by concrete implementations)

## Example:
```python
# Create a Redis broker instance
broker = Broker("redis://localhost:6379/0")

# Create a RabbitMQ broker instance
broker = Broker("amqp://user:pass@localhost:5672/vhost")

# Both instances provide the same interface for queue operations
# but use different underlying implementations
queues_info = await broker.queues(['queue1', 'queue2'])
```

### `flower.utils.broker.Broker.__new__` · *method*

## Summary:
Creates and returns an instance of a concrete broker class based on the URL scheme of the provided broker URL.

## Description:
The `__new__` method serves as a factory method that dynamically instantiates the appropriate broker subclass based on the scheme component of the provided broker URL. This enables the system to support multiple messaging backends (AMQP, Redis, Redis SSL, Redis Socket, Redis Sentinel) through a unified interface. The method parses the URL scheme and delegates to the corresponding broker constructor, passing through all additional arguments and keyword arguments.

This logic is implemented as a `__new__` method rather than being inlined because it needs to control object creation itself, returning instances of different classes based on runtime conditions. This pattern allows for polymorphic broker instantiation while maintaining a consistent interface for users of the Broker class.

Known callers include the Broker class constructor and any code that instantiates Broker subclasses directly. This method is invoked during the object creation phase of the broker lifecycle, acting as the entry point for selecting the appropriate backend implementation.

## Args:
    cls (type): The class being instantiated (Broker class)
    broker_url (str): Connection URL specifying the broker type and connection parameters
    *args: Additional positional arguments to pass to the concrete broker constructor
    **kwargs: Additional keyword arguments to pass to the concrete broker constructor

## Returns:
    Broker instance: An instance of a concrete broker subclass (RabbitMQ, Redis, RedisSsl, RedisSocket, or RedisSentinel) based on the URL scheme

## Raises:
    NotImplementedError: When the broker URL scheme is not supported (not one of amqp, redis, rediss, redis+socket, sentinel)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - broker_url must be a valid string containing a scheme component
    - The scheme must be one of: 'amqp', 'redis', 'rediss', 'redis+socket', 'sentinel'
    Postconditions:
    - Returns an instance of a concrete broker subclass matching the URL scheme
    - All additional arguments are forwarded to the concrete broker constructor

## Side Effects:
    None

### `flower.utils.broker.Broker.queues` · *method*

## Summary:
Retrieves detailed information about specified message queues from a message broker.

## Description:
The queues method is an abstract asynchronous method that serves as the primary interface for fetching queue metadata from various message broker implementations. This method is designed to be implemented by concrete broker subclasses (such as RabbitMQ, Redis, etc.) to provide specific queue inspection capabilities for each messaging system.

The method is typically invoked during monitoring or administrative operations when detailed queue information is required. It acts as a standardized entry point that enables uniform access to queue data regardless of the underlying broker technology, supporting operations like queue size monitoring, consumer counts, and queue configuration details.

## Args:
    names (list[str]): A list of queue names to retrieve information for

## Returns:
    Awaitable[list[dict]]: An asynchronous operation that resolves to a list of dictionaries containing queue information

## Raises:
    NotImplementedError: Always raised by the base implementation, indicating that concrete implementations must override this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method must be called on a properly initialized broker instance with valid broker configuration
    Postconditions: The method always raises NotImplementedError in the base class implementation

## Side Effects:
    None

## `flower.utils.broker.main` · *function*

## Summary:
Asynchronously retrieves and displays queue information from a message broker using command-line arguments for configuration.

## Description:
The main function serves as the entry point for a command-line utility that queries message broker queue information. It parses command-line arguments to determine the broker URL, queue name, and HTTP API endpoint, then creates a Broker instance and fetches queue details for the specified queue(s). The function is designed to be run from the command line with optional arguments for customization.

This logic is extracted into its own function to provide a clean entry point for the CLI utility, separating the argument parsing and orchestration concerns from the core broker interaction logic. This makes the component testable and reusable as part of larger applications.

## Args:
    None: Function reads arguments directly from sys.argv

## Returns:
    None: Function prints results to stdout and exits

## Raises:
    None: Function does not explicitly raise exceptions, though underlying broker operations may raise exceptions

## Constraints:
    Preconditions:
    - At least one command-line argument must be provided (broker URL)
    - If two arguments are provided, the second is treated as queue name
    - If three arguments are provided, the third is treated as HTTP API endpoint
    
    Postconditions:
    - Function exits after printing queue information or completing execution
    - Queue information is printed to standard output if available

## Side Effects:
    - Prints queue information to standard output
    - Makes HTTP requests to the broker's management API
    - Creates a Broker instance and potentially establishes connections to message brokers

## Control Flow:
```mermaid
flowchart TD
    A[Start main()] --> B{sys.argv length}
    B -->|< 2| C[Set broker_url = 'amqp://']
    B -->|≥ 2| D[Set broker_url = sys.argv[1]]
    D --> E{sys.argv length}
    E -->|< 3| F[Set queue_name = 'celery']
    E -->|≥ 3| G[Set queue_name = sys.argv[2]]
    G --> H{sys.argv length}
    H -->|< 4| I[Set http_api = 'http://guest:guest@localhost:15672/api/']
    H -->|≥ 4| J[Set http_api = sys.argv[3]]
    J --> K[Create Broker(broker_url, http_api=http_api)]
    K --> L[await broker.queues([queue_name])]
    L --> M{queues result}
    M -->|True| N[print(queues)]
    M -->|False| O[Exit]
```

## Examples:
    Example 1: Basic usage with default settings
    $ python broker.py
    # Uses default amqp:// broker URL and celery queue name
    # Uses default http://guest:guest@localhost:15672/api/ HTTP API endpoint
    
    Example 2: Custom broker URL and queue name
    $ python broker.py amqp://user:pass@localhost:5672/myvhost myqueue
    # Connects to RabbitMQ at user:pass@localhost:5672/myvhost
    # Queries queue named 'myqueue'
    # Uses default HTTP API endpoint
    
    Example 3: Custom broker URL, queue name, and HTTP API endpoint
    $ python broker.py redis://localhost:6379/0 myqueue http://admin:secret@remote:15672/api/
    # Connects to Redis at localhost:6379/0
    # Queries queue named 'myqueue'
    # Uses custom HTTP API endpoint

