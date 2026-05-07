# `broker.py`

## `flower.utils.broker.BrokerBase` · *class*

## Summary:
Abstract base class for broker implementations that handles URL parsing and provides a framework for queue operations.

## Description:
BrokerBase serves as a foundation for concrete broker implementations by parsing broker connection URLs and providing a standardized interface for queue operations. It extracts connection parameters such as host, port, virtual host, username, and password from a broker URL, making it easier to configure different broker backends consistently.

This class is designed to be subclassed by specific broker implementations (such as RedisBroker, RabbitMQBroker, etc.) that provide concrete implementations of the queues() method.

## State:
- host (str): Hostname extracted from the broker URL; may be None if not specified
- port (int): Port number extracted from the broker URL; may be None if not specified  
- vhost (str): Virtual host path extracted from the broker URL path component
- username (str): Decoded username from URL credentials; may be None if not specified
- password (str): Decoded password from URL credentials; may be None if not specified

The class maintains these parsed URL components as instance attributes for use by subclasses.

## Lifecycle:
- Creation: Instantiate with a broker URL string containing connection parameters
- Usage: Subclasses should implement the queues() method to provide specific queue functionality
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[BrokerBase.__init__] --> B[BrokerBase.queues]
    B --> C[Subclass Implementation]
```

## Raises:
- None explicitly raised in __init__
- queues() method raises NotImplementedError when called directly

## Example:
```python
# Basic instantiation
broker = BrokerBase("redis://user:pass@localhost:6379/0")

# Subclass implementation example
class RedisBroker(BrokerBase):
    async def queues(self, names):
        # Implementation for Redis-specific queue operations
        pass
```

### `flower.utils.broker.BrokerBase.__init__` · *method*

## Summary:
Initializes a broker connection by parsing the broker URL and extracting connection parameters.

## Description:
This method serves as the constructor for BrokerBase, responsible for parsing the provided broker URL to extract essential connection parameters including hostname, port, virtual host, username, and password. The method handles URL decoding for credentials to ensure proper authentication.

## Args:
    broker_url (str): The URL string containing broker connection information in the format protocol://username:password@host:port/virtual_host

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None explicitly raised by this method, though parsing errors could occur from urlparse if the URL format is invalid.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.host: Extracted from the URL's hostname component
        - self.port: Extracted from the URL's port component  
        - self.vhost: Extracted from the URL's path component (without leading slash)
        - self.username: Extracted from the URL's username component, URL-decoded if present
        - self.password: Extracted from the URL's password component, URL-decoded if present

## Constraints:
    Preconditions:
        - broker_url must be a valid string URL format
        - The URL should follow standard broker URL conventions (protocol://username:password@host:port/virtual_host)
    Postconditions:
        - All connection parameters are properly extracted and stored as instance attributes
        - Username and password are URL-decoded if they were encoded in the original URL

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only processes the input URL and stores parsed values as instance attributes.

### `flower.utils.broker.BrokerBase.queues` · *method*

## Summary:
Retrieves detailed information about specified message queues from a broker system.

## Description:
This asynchronous method fetches metadata and statistics for a list of queue names from a message broker (such as RabbitMQ or Redis). It serves as an abstract interface that must be implemented by concrete broker subclasses to provide broker-specific queue information retrieval.

## Args:
    names (list[str]): A list of queue names to retrieve information for.

## Returns:
    list[dict]: A list of queue information dictionaries containing details such as queue names and message counts. The exact structure depends on the broker implementation:
    - For RabbitMQ: Full queue details including queue properties, message counts, and configuration
    - For Redis: Simplified statistics including queue name and total message count across priority levels
    
    Returns an empty list if no queues are found or if an error occurs during retrieval.

## Raises:
    NotImplementedError: When called on the abstract base class without a concrete implementation.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The method should only be called on initialized broker instances
    - Queue names in the `names` parameter should be valid identifiers for the broker system
    - The broker connection should be established before calling this method
    
    Postconditions:
    - The method returns a list of queue information dictionaries
    - Error conditions are handled gracefully by returning empty lists

## Side Effects:
    - Makes asynchronous HTTP requests to broker management APIs (for RabbitMQ)
    - Performs Redis operations to query queue lengths (for Redis-based brokers)
    - May log error messages when broker communication fails

## `flower.utils.broker.RabbitMQ` · *class*

## Summary:
RabbitMQ broker client that communicates with the RabbitMQ management HTTP API to retrieve queue information.

## Description:
This class implements a broker client for RabbitMQ systems, specifically designed to interact with the RabbitMQ management API to fetch queue information. It inherits from BrokerBase and extends it with RabbitMQ-specific functionality for parsing broker URLs and making asynchronous HTTP requests to the management API endpoints.

The class is intended to be instantiated by broker managers or monitoring systems that need to query RabbitMQ queue statistics and status information. It provides an async interface for retrieving specific queue details from the RabbitMQ management API.

## State:
- io_loop: tornado.ioloop.IOLoop instance for handling asynchronous operations
- host: str, RabbitMQ server hostname (defaults to 'localhost')
- port: int, RabbitMQ management API port (defaults to 15672)
- vhost: str, virtual host identifier (URL-encoded, defaults to '/')
- username: str, authentication username (defaults to 'guest')
- password: str, authentication password (defaults to 'guest')
- http_api: str, full URL to the RabbitMQ management API endpoint

## Lifecycle:
- Creation: Instantiate with broker_url and optional http_api parameter; io_loop is automatically initialized if not provided
- Usage: Call the async queues() method with a list of queue names to retrieve information
- Destruction: Automatically closes HTTP client connections when the async operation completes

## Method Map:
```mermaid
graph TD
    A[RabbitMQ.__init__] --> B[RabbitMQ.queues]
    B --> C[httpclient.AsyncHTTPClient.fetch]
    C --> D[json.loads]
    D --> E[Return filtered queue info]
```

## Raises:
- ValueError: Raised during initialization when http_api URL validation fails due to invalid scheme (not http/https)
- socket.error: Raised during HTTP requests when connection fails
- httpclient.HTTPError: Raised during HTTP requests when server returns error status code

## Example:
```python
# Create RabbitMQ broker instance
broker = RabbitMQ(
    broker_url="amqp://user:pass@localhost:5672/vhost",
    http_api="http://user:pass@localhost:15672/api/vhost"
)

# Fetch queue information asynchronously
queue_info = await broker.queues(['queue1', 'queue2'])
```

### `flower.utils.broker.RabbitMQ.__init__` · *method*

## Summary:
Initializes a RabbitMQ broker connection with default values and validates the HTTP API endpoint.

## Description:
Configures the RabbitMQ broker connection by setting default values for host, port, vhost, username, and password when not provided in the broker URL. Constructs and validates the HTTP API endpoint URL for management operations. This method serves as the primary initialization point for RabbitMQ broker instances.

## Args:
    broker_url (str): The broker connection URL containing host, port, vhost, username, and password information
    http_api (str): The HTTP API endpoint URL for RabbitMQ management interface
    io_loop (tornado.ioloop.IOLoop, optional): The I/O loop instance to use. Defaults to the current IOLoop instance if not provided
    **__ (dict): Additional keyword arguments that are ignored

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    ValueError: When the http_api URL has an invalid scheme (not http or https)

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: self.io_loop, self.http_api

## Constraints:
    Preconditions: 
    - broker_url must be a valid URL format that can be parsed by urlparse
    - http_api must be a valid URL string if provided
    
    Postconditions:
    - All connection parameters (host, port, vhost, username, password) are properly initialized from broker_url
    - self.io_loop is set to either the provided io_loop or the current IOLoop instance
    - self.http_api contains a valid HTTP API URL or the constructed default URL

## Side Effects:
    - May log an error message to the logger if http_api validation fails
    - Sets up internal state for HTTP API communication with RabbitMQ management interface

### `flower.utils.broker.RabbitMQ.queues` · *method*

## Summary:
Fetches and filters queue information from RabbitMQ management API by specified queue names.

## Description:
Retrieves all queue information from RabbitMQ's management API for the configured virtual host, then filters the results to only include queues whose names match the provided list. This method serves as an implementation of the abstract queues() method defined in BrokerBase, specifically tailored for RabbitMQ brokers.

## Args:
    names (list[str]): A list of queue names to filter the retrieved queue information by.

## Returns:
    list[dict]: A list of queue information dictionaries containing details about queues that match the provided names. Returns an empty list if the API call fails or no matching queues are found.

## Raises:
    None explicitly raised - HTTP errors are caught and logged, returning empty list instead.

## State Changes:
    Attributes READ: self.http_api, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.http_api must be a valid URL pointing to RabbitMQ management API
    - self.vhost must be properly encoded for use in API requests
    - The RabbitMQ management plugin must be enabled and accessible
    Postconditions:
    - Returns a list of queue information dictionaries matching the provided names
    - If API call fails, returns empty list instead of raising exception

## Side Effects:
    - Makes asynchronous HTTP request to RabbitMQ management API
    - Logs error messages to logger when HTTP requests fail
    - Creates and closes AsyncHTTPClient instance during execution

### `flower.utils.broker.RabbitMQ.validate_http_api` · *method*

## Summary:
Validates that an HTTP API URL uses a supported scheme (http or https).

## Description:
This class method performs validation on HTTP API URLs to ensure they use either the 'http' or 'https' protocol scheme. It is called during RabbitMQ broker initialization to validate the provided HTTP API endpoint before storing it for later use in API requests.

## Args:
    http_api (str): The HTTP API URL to validate, containing a scheme (http/https) and other URL components.

## Returns:
    None: This method does not return any value.

## Raises:
    ValueError: Raised when the URL scheme is not 'http' or 'https', with a descriptive error message indicating the invalid scheme.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The http_api parameter must be a string containing a valid URL with a scheme component.
    Postconditions: If successful, the method guarantees the URL scheme is either 'http' or 'https'.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only parses the URL and checks the scheme.

## `flower.utils.broker.RedisBase` · *class*

## Summary:
RedisBase is a Redis-based broker implementation that extends BrokerBase to provide queue management and statistics functionality for Redis-backed message brokers.

## Description:
This class implements Redis-specific broker operations for managing message queues with priority support. It inherits from BrokerBase and provides concrete implementations for queue statistics retrieval. RedisBase is designed to work with Redis servers and handles queue naming conventions with priority levels.

The class is typically instantiated by framework components that need Redis broker functionality, such as Celery workers or monitoring tools. It expects a Redis connection to be established externally before queue operations are performed.

## State:
- redis: Redis client instance, initially None, must be set before queue operations
- priority_steps: List of supported priority levels, defaults to [0, 3, 6, 9]
- sep: Separator string for queue naming, defaults to '\x06\x16' 
- broker_prefix: Global prefix for Redis keys, defaults to empty string

## Lifecycle:
- Creation: Instantiated with broker_url and optional broker_options containing priority_steps, sep, and global_keyprefix
- Usage: Requires redis client to be connected before calling queues() method
- Destruction: No explicit cleanup required, relies on parent class and Redis client lifecycle

## Method Map:
```mermaid
graph TD
    A[RedisBase.__init__] --> B[BrokerBase.__init__]
    A --> C[Set priority_steps]
    A --> D[Set sep]
    A --> E[Set broker_prefix]
    F[RedisBase.queues] --> G[RedisBase._q_for_pri]
    F --> H[RedisBase.redis.llen]
```

## Raises:
- ImportError: When the redis library is not available
- ValueError: When a priority value is not in the configured priority_steps

## Example:
```python
# Create RedisBase instance
broker = RedisBase('redis://localhost:6379/0', broker_options={
    'priority_steps': [0, 1, 2, 3],
    'sep': '|',
    'global_keyprefix': 'myapp:'
})

# Set up Redis connection (external to this class)
# broker.redis = redis_client

# Get queue statistics
stats = await broker.queues(['task_queue'])
```

### `flower.utils.broker.RedisBase.__init__` · *method*

## Summary:
Initializes a RedisBase instance with broker configuration and sets up priority handling parameters.

## Description:
This constructor initializes the RedisBase object by setting up broker connection parameters and configuring priority-based queue handling. It validates the redis library dependency and processes broker options to configure queue prioritization settings.

## Args:
    broker_url (str): URL string for connecting to the message broker
    *_: Additional positional arguments (ignored)
    **kwargs: Keyword arguments containing broker configuration options
        broker_options (dict): Dictionary of broker-specific configuration parameters

## Returns:
    None: This method initializes instance attributes but does not return a value

## Raises:
    ImportError: When the redis library is not available or importable

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.redis: Set to None initially (connection will be established later)
        - self.priority_steps: Configured from broker_options or defaults to [0, 3, 6, 9]
        - self.sep: Configured from broker_options or defaults to '\x06\x16'
        - self.broker_prefix: Configured from broker_options or defaults to empty string

## Constraints:
    Preconditions:
        - The redis library must be importable in the environment
        - broker_url must be a valid URL string for the message broker
    Postconditions:
        - self.redis is initialized to None
        - All configuration parameters are properly set with defaults applied
        - Instance is ready for subsequent broker operations

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal state.

### `flower.utils.broker.RedisBase._q_for_pri` · *method*

## Summary:
Formats a queue name with priority using a configured separator.

## Description:
Constructs a queue identifier by combining the base queue name with a priority level using the instance's configured separator. This method ensures that only valid priority levels are used and properly handles the case when no priority is specified.

## Args:
    queue (str): The base queue name to format
    pri (int, optional): Priority level to append to the queue name. Must be one of the values in self.priority_steps. Defaults to None.

## Returns:
    str: Formatted queue name with priority appended, or just the queue name if priority is None/empty.

## Raises:
    ValueError: When the specified priority level is not in self.priority_steps.

## State Changes:
    Attributes READ: self.priority_steps, self.sep
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The priority level must be one of the values defined in self.priority_steps
    - The queue name must be a valid string
    
    Postconditions:
    - Returns a properly formatted string combining queue name, separator, and priority
    - If pri is falsy, returns just the queue name without separator or priority

## Side Effects:
    None

### `flower.utils.broker.RedisBase.queues` · *method*

## Summary:
Retrieves message count statistics for multiple Redis queues, accounting for priority-based queue naming conventions.

## Description:
This asynchronous method fetches the total message count across all priority levels for each specified queue name. It overrides the abstract `BrokerBase.queues()` method and is designed for Redis-based brokers in Flower monitoring. The method constructs priority-specific queue names using the broker prefix and priority steps, then sums the lengths of all priority queues for each queue name to provide a complete message count.

## Args:
    names (list[str]): A list of queue names to retrieve statistics for

## Returns:
    list[dict]: A list of dictionaries containing queue statistics, where each dictionary has:
        - 'name' (str): The original queue name
        - 'messages' (int): Total message count across all priority levels for that queue

## Raises:
    ValueError: When a priority value is not in the configured priority_steps (via _q_for_pri helper)
    AttributeError: When self.redis is not initialized (though this would likely occur earlier in the connection process)

## State Changes:
    Attributes READ: 
        - self.broker_prefix (str): Prefix used for queue key construction
        - self.priority_steps (list[int]): Priority levels supported by this broker
        - self.redis (redis.Redis): Redis client instance for querying queue lengths
        - self._q_for_pri (method): Helper method for constructing priority queue names

## Constraints:
    Preconditions:
        - self.redis must be properly initialized and connected to Redis
        - self.priority_steps must be a valid list of integers
        - names must be a list of strings
    Postconditions:
        - Returns a list of dictionaries with consistent structure
        - Each returned dictionary contains 'name' and 'messages' keys
        - Message counts represent the total across all priority levels for each queue

## Side Effects:
    - Performs multiple Redis operations (llen) for each queue
    - Makes synchronous Redis network calls (via redis-py)
    - May cause temporary Redis connection load due to multiple operations

## `flower.utils.broker.Redis` · *class*

## Summary:
Redis broker client that manages connections to Redis servers using broker URLs.

## Description:
The Redis class provides a broker interface for Redis message queues by parsing broker URLs and creating Redis client connections. It handles virtual host (database) preparation and connection management for Redis-based task queues.

## State:
- host (str): Redis server hostname, defaults to 'localhost' if not specified in broker URL
- port (int): Redis server port number, defaults to 6379 if not specified in broker URL  
- vhost (int): Redis database number (virtual host), converted from URL path component
- redis (redis.Redis): Redis client instance configured with parsed connection parameters
- username (str): Redis authentication username from broker URL
- password (str): Redis authentication password from broker URL

## Lifecycle:
Creation: Instantiate with a broker URL string containing Redis connection information (host, port, vhost, username, password)
Usage: The redis attribute provides access to the underlying Redis client for queue operations
Destruction: Managed by Python garbage collection; Redis client doesn't require explicit cleanup

## Method Map:
```mermaid
graph TD
    A[Redis.__init__] --> B[RedisBase.__init__]
    A --> C[Redis._prepare_virtual_host]
    A --> D[Redis._get_redis_client]
    C --> E[Redis._get_redis_client_args]
    D --> E
```

## Raises:
- ValueError: When virtual host cannot be converted to an integer database number
- ImportError: When the redis library is not available

## Example:
```python
# Create Redis broker instance
broker = Redis('redis://user:pass@localhost:6379/0')

# Access the Redis client for operations
client = broker.redis
client.lpush('queue_name', 'message_content')
```

### `flower.utils.broker.Redis.__init__` · *method*

## Summary:
Initializes a Redis broker connection with configured host, port, virtual host, and Redis client instance.

## Description:
Configures Redis connection parameters from the broker URL and establishes a Redis client connection. This method prepares the broker configuration by setting default values for host and port when not specified, processes the virtual host, and creates a Redis client instance for communication.

## Args:
    broker_url (str): The Redis broker URL containing connection information including host, port, and virtual host.
    *args: Additional positional arguments passed to the parent class initializer.
    **kwargs: Additional keyword arguments passed to the parent class initializer.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None explicitly documented: The method doesn't declare specific exceptions but may raise exceptions from parent class initialization or Redis client creation.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost
    Attributes WRITTEN: self.host, self.port, self.vhost, self.redis

## Constraints:
    Preconditions: The broker_url parameter must be a valid string containing Redis connection information.
    Postconditions: Instance attributes host, port, vhost, and redis are initialized with appropriate values.

## Side Effects:
    I/O: Establishes network connection to Redis server.
    External service calls: Creates Redis client instance which may connect to Redis server.

### `flower.utils.broker.Redis._prepare_virtual_host` · *method*

## Summary:
Normalizes virtual host (database) values to integer indices for Redis connections.

## Description:
Prepares and validates virtual host values for Redis database selection. Converts string representations of database indices to integers, handling special cases like empty values and URL-style paths. This method ensures consistent database indexing across different input formats while maintaining validation constraints.

## Args:
    vhost (str|int): Virtual host identifier which can be an integer, empty string, '/', or a string starting with '/'

## Returns:
    int: Normalized database index between 0 and limit-1

## Raises:
    ValueError: When vhost cannot be converted to an integer representing a valid database index

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Input vhost must be convertible to a valid integer database index
    Postconditions: Returned value is always an integer in the range [0, limit-1]

## Side Effects:
    None

### `flower.utils.broker.Redis._get_redis_client_args` · *method*

*No documentation generated.*

### `flower.utils.broker.Redis._get_redis_client` · *method*

## Summary:
Creates and returns a Redis client instance configured with connection parameters.

## Description:
This method encapsulates the creation of a redis.Redis client instance by gathering connection parameters from various instance attributes and passing them to the Redis constructor. It serves as a factory method for Redis clients within the broker system.

The method is called during the initialization of the Redis class to establish the primary Redis connection stored in `self.redis`.

## Args:
    None

## Returns:
    redis.Redis: A configured Redis client instance ready for database operations.

## Raises:
    None explicitly raised, but may raise exceptions from redis.Redis constructor if invalid parameters are provided.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.username, self.password
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Instance must have host, port, vhost, username, and password attributes defined
    - The redis library must be available/importable
    - Connection parameters must be valid for Redis server configuration
    
    Postconditions:
    - Returns a valid redis.Redis client instance
    - Client is configured with the instance's connection parameters

## Side Effects:
    None directly, but the returned Redis client may perform network I/O when used for database operations.

## `flower.utils.broker.RedisSentinel` · *class*

## Summary:
RedisSentinel provides a broker interface for Redis Sentinel, enabling connection to Redis master instances through a Sentinel discovery service.

## Description:
This class implements a Redis broker that connects to Redis masters via Redis Sentinel for high availability setups. It inherits from RedisBase which provides the core Redis functionality and adds Sentinel-specific connection logic for master discovery. The class is typically instantiated by the broker management system when a Redis Sentinel URL is detected.

## State:
- host (str): Redis Sentinel host address, defaults to 'localhost' if not specified in broker_url
- port (int): Redis Sentinel port number, defaults to 26379 if not specified in broker_url  
- vhost (int): Database index for Redis connection, parsed from broker_url path
- master_name (str): Required name identifying the Redis master instance in Sentinel configuration
- redis: Redis client instance connected to the master via Sentinel

## Lifecycle:
Creation: Instantiate with a Redis Sentinel broker URL containing sentinel host/port and broker_options with master_name
Usage: Typically used for queue operations through inherited methods from RedisBase
Destruction: Cleanup handled by Redis client lifecycle management

## Method Map:
```mermaid
graph TD
    A[RedisSentinel.__init__] --> B[RedisBase.__init__]
    A --> C[_prepare_virtual_host]
    A --> D[_prepare_master_name]
    A --> E[_get_redis_client]
    C --> F[vhost preparation]
    D --> G[master_name validation]
    E --> H[Redis Sentinel connection]
```

## Raises:
- ValueError: When master_name is not provided in broker_options
- ValueError: When vhost cannot be converted to an integer

## Example:
```python
# Create Redis Sentinel broker instance
broker_url = "redis://:password@sentinel-host:26379/0"
broker_options = {"master_name": "mymaster"}
sentinel_broker = RedisSentinel(broker_url, broker_options=broker_options)

# The broker is now ready to use for queue operations
# through inherited methods from RedisBase
```

### `flower.utils.broker.RedisSentinel.__init__` · *method*

## Summary:
Initializes a Redis Sentinel broker connection with default configurations and validates required parameters.

## Description:
Configures a Redis Sentinel connection by setting default host/port values, preparing virtual host and master name parameters, and establishing a Redis client for Sentinel-based master discovery. This method serves as the primary initialization point for Redis Sentinel broker instances, ensuring proper connection setup and validation of required configuration options.

## Args:
    broker_url (str): URL specifying the Redis Sentinel connection details including hostname, port, and virtual host.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Additional keyword arguments including broker_options dictionary containing sentinel configuration.

## Returns:
    None: This method initializes instance attributes but does not return a value.

## Raises:
    ValueError: When 'master_name' is not provided in broker_options, indicating a required configuration parameter is missing.
    ImportError: When the redis library is not available, preventing Redis operations.

## State Changes:
    Attributes READ: self.host, self.port, self.vhost, self.password
    Attributes WRITTEN: self.host, self.port, self.vhost, self.master_name, self.redis

## Constraints:
    Preconditions: 
    - broker_url must be a valid URL with hostname and port components
    - broker_options must contain 'master_name' key for Sentinel configuration
    - redis library must be importable
    
    Postconditions:
    - self.host is set to either the parsed hostname or 'localhost' default
    - self.port is set to either the parsed port or 26379 default
    - self.vhost is converted to integer database index
    - self.master_name is extracted from broker_options
    - self.redis is initialized as a Redis Sentinel client

## Side Effects:
    - Establishes network connection to Redis Sentinel server
    - May raise ImportError if redis library is unavailable
    - Creates Redis Sentinel client instance for subsequent operations

### `flower.utils.broker.RedisSentinel._prepare_virtual_host` · *method*

## Summary:
Normalizes and validates virtual host identifiers for Redis database selection.

## Description:
Processes virtual host parameters to ensure they are valid integer database numbers between 0 and limit-1. Handles various input formats including empty strings, forward slashes, and string representations of integers.

## Args:
    vhost (str|int): Virtual host identifier which can be an integer, empty string, forward slash, or string representation of a number.

## Returns:
    int: Integer database number between 0 and limit-1.

## Raises:
    ValueError: When vhost cannot be converted to an integer database number.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: vhost parameter must be convertible to an integer database number.
    Postconditions: Returned value is always an integer in the valid database range.

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._prepare_master_name` · *method*

## Summary:
Extracts and validates the master name from broker options for Redis Sentinel configuration.

## Description:
This method retrieves the 'master_name' parameter from the broker options dictionary, which is required for configuring Redis Sentinel connections. It ensures that the master name is provided and raises a descriptive error if missing.

The method is called during RedisSentinel initialization to prepare the master name needed for establishing connections to Redis Sentinel instances.

## Args:
    broker_options (dict): Dictionary containing Redis Sentinel configuration options, including the required 'master_name' key.

## Returns:
    str: The master name string used to identify the Redis master instance in Sentinel configuration.

## Raises:
    ValueError: When 'master_name' key is not present in the broker_options dictionary.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - broker_options must be a dictionary-like object
    - broker_options must contain the 'master_name' key
    
    Postconditions:
    - Returns a string value representing the Redis master name
    - Raises ValueError if master_name is missing

## Side Effects:
    None

### `flower.utils.broker.RedisSentinel._get_redis_client` · *method*

## Summary:
Creates and returns a Redis client instance connected to the master Redis server via Redis Sentinel.

## Description:
This method initializes a Redis Sentinel connection and retrieves a master Redis client for database operations. It is called during RedisSentinel initialization to establish the connection to the Redis master server through the Sentinel discovery mechanism.

## Args:
    broker_options (dict): Dictionary containing Redis Sentinel configuration options, including optional 'sentinel_kwargs' for additional sentinel configuration.

## Returns:
    redis.Redis: A Redis client instance connected to the master Redis server as identified by the master_name attribute.

## Raises:
    None explicitly raised, but may raise exceptions from redis.sentinel.Sentinel() or sentinel.master_for() if connection fails or configuration is invalid.

## State Changes:
    Attributes READ: self.host, self.port, self.password, self.master_name
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.host must be a valid hostname or IP address
    - self.port must be a valid port number
    - self.master_name must be set (validated in _prepare_master_name)
    - broker_options must be a dictionary
    Postconditions: 
    - Returns a valid Redis client instance ready for database operations

## Side Effects:
    - Creates a network connection to the Redis Sentinel server
    - May perform DNS resolution for the host address
    - Uses the password and sentinel_kwargs from broker_options for authentication

## `flower.utils.broker.RedisSocket` · *class*

## Summary:
A Redis client implementation that connects to Redis via Unix domain socket for message queue operations.

## Description:
RedisSocket is a specialized Redis client that establishes connections to Redis using Unix domain sockets rather than TCP connections. It inherits from RedisBase, which provides common Redis configuration and utility methods, and ultimately from BrokerBase, which handles URL parsing for broker connection parameters. This class is designed for environments where Unix domain sockets provide better performance and security compared to traditional TCP connections.

## State:
- `redis`: redis.Redis instance - configured with unix_socket_path and password from broker configuration
- `vhost`: str - extracted from broker_url path component, used to construct unix socket path as '/{vhost}'
- `password`: str - extracted from broker_url password component, passed to Redis connection
- All inherited attributes from RedisBase and BrokerBase including priority_steps, sep, broker_prefix

## Lifecycle:
- Creation: Instantiate with broker_url string containing Redis connection information (host, port, vhost, username, password)
- Usage: Typically used for queue statistics operations through inherited methods like queues()
- Destruction: Cleanup handled by Redis library when object is garbage collected

## Method Map:
```mermaid
graph TD
    A[RedisSocket.__init__] --> B[RedisBase.__init__]
    B --> C[BrokerBase.__init__]
    C --> D[redis.Redis()]
```

## Raises:
- ImportError: When the redis library is not available
- ValueError: When priority is not in priority steps (inherited from RedisBase)

## Example:
```python
# Create RedisSocket instance
broker_url = "redis://:password@localhost/0"
redis_socket = RedisSocket(broker_url)

# Use inherited queue methods
queue_names = ["queue1", "queue2"]
stats = await redis_socket.queues(queue_names)
```

### `flower.utils.broker.RedisSocket.__init__` · *method*

## Summary:
Initializes a RedisSocket instance by setting up a Redis connection using Unix socket path and password from the broker URL.

## Description:
This method constructs a Redis client connection using a Unix domain socket path derived from the virtual host portion of the broker URL and the password extracted from the broker URL credentials. It is part of the RedisSocket class initialization process that establishes the underlying Redis connection for message queue operations.

## Args:
    broker_url (str): The broker URL containing hostname, port, path (vhost), username, and password information
    *args: Additional positional arguments passed to the parent class constructor
    **kwargs: Additional keyword arguments passed to the parent class constructor

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    ImportError: When the redis library is not available
    ValueError: When priority steps validation fails in parent class (indirectly)

## State Changes:
    Attributes READ: self.vhost, self.password
    Attributes WRITTEN: self.redis

## Constraints:
    Preconditions: 
    - broker_url must be a valid URL string with proper formatting
    - The redis library must be installed in the environment
    - vhost attribute must be properly parsed from broker_url (non-empty string)
    
    Postconditions:
    - self.redis is initialized as a redis.Redis instance
    - self.vhost and self.password are properly set from the broker_url
    - Parent class initialization is completed successfully

## Side Effects:
    - Creates a Redis connection using Unix domain socket
    - May raise ImportError if redis library is not available

## `flower.utils.broker.RedisSsl` · *class*

*No documentation generated.*

### `flower.utils.broker.RedisSsl.__init__` · *method*

## Summary:
Initializes a RedisSsl broker connection with SSL/TLS configuration validation.

## Description:
Configures SSL/TLS settings for Redis broker connections and validates that required SSL parameters are provided. This method ensures that secure Redis connections (using rediss:// URLs) have proper SSL configuration before establishing the connection.

## Args:
    broker_url (str): The Redis broker URL, typically starting with 'rediss://' for secure connections.
    *args: Additional positional arguments passed to the parent class constructor.
    **kwargs: Additional keyword arguments, including 'broker_use_ssl' which is required for SSL connections.

## Returns:
    None: This method initializes the object state but does not return a value.

## Raises:
    ValueError: Raised when 'broker_use_ssl' is not provided in kwargs, indicating that SSL configuration is missing for a secure Redis connection.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.broker_use_ssl: Set to the value of 'broker_use_ssl' from kwargs, or an empty dict if not provided

## Constraints:
    Preconditions:
        - When using a 'rediss://' broker URL, the 'broker_use_ssl' parameter must be provided in kwargs
        - The broker_url parameter must be a valid Redis URL string
    
    Postconditions:
        - The self.broker_use_ssl attribute is initialized with SSL configuration
        - The parent class constructor is called with all provided arguments

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal state.

### `flower.utils.broker.RedisSsl._get_redis_client_args` · *method*

## Summary:
Configures and returns Redis client connection arguments with SSL enabled for secure communication.

## Description:
This method extends the base Redis client argument configuration by enabling SSL transport and allowing custom SSL options. It is called during Redis client initialization to establish secure connections to Redis servers. The method ensures that all Redis operations through this broker use encrypted connections when configured for SSL.

## Args:
    None

## Returns:
    dict: A dictionary containing Redis client connection parameters including host, port, database, username, password, and SSL configuration. The 'ssl' key is always set to True, and additional SSL-specific parameters can be provided via the broker_use_ssl attribute.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.broker_use_ssl
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The RedisSsl instance must have been initialized with a broker_use_ssl parameter
    - The parent class's _get_redis_client_args() method must return a valid dictionary
    Postconditions:
    - The returned dictionary contains 'ssl': True
    - If broker_use_ssl is a dictionary, its contents are merged into the result

## Side Effects:
    None

## `flower.utils.broker.Broker` · *class*

## Summary:
Factory class that creates specific broker implementations (RabbitMQ, Redis, etc.) based on URL scheme.

## Description:
The Broker class implements a factory pattern to instantiate appropriate broker implementations depending on the protocol specified in the broker URL. It supports multiple messaging systems including AMQP (RabbitMQ), Redis, Redis over SSL, Redis over Unix sockets, and Redis Sentinel. This abstraction allows the system to work with different message brokers through a unified interface.

## State:
- broker_url (str): Connection URL specifying the broker type and connection parameters
- The class uses the URL scheme to determine which specific broker implementation to instantiate
- No persistent state beyond the URL parsing and instantiation logic

## Lifecycle:
- Creation: Instantiated via `Broker(broker_url)` where broker_url specifies the protocol (amqp, redis, rediss, redis+socket, sentinel)
- Usage: Typically followed by calling async methods like `queues()` on the returned instance
- Destruction: Depends on the specific broker implementation's cleanup requirements

## Method Map:
```mermaid
graph TD
    A[Broker.__new__] --> B{URL Scheme}
    B -->|amqp| C[RabbitMQ]
    B -->|redis| D[Redis]
    B -->|rediss| E[RedisSsl]
    B -->|redis+socket| F[RedisSocket]
    B -->|sentinel| G[RedisSentinel]
    B -->|unknown| H[NotImplementedError]
    C --> I[BrokerBase.queues]
    D --> I
    E --> I
    F --> I
    G --> I
```

## Raises:
- NotImplementedError: When the URL scheme is not supported (not amqp, redis, rediss, redis+socket, or sentinel)

## Example:
```python
# Create a broker instance based on URL scheme
broker = Broker('redis://localhost:6379/0')
# Use the broker to get queue information
queues = await broker.queues(['queue1', 'queue2'])
```

### `flower.utils.broker.Broker.__new__` · *method*

## Summary:
Creates and returns a broker instance based on the URL scheme, implementing a factory pattern for different broker types.

## Description:
This method serves as a factory constructor that dynamically instantiates the appropriate broker subclass based on the protocol scheme specified in the broker URL. It enables the system to support multiple messaging systems (AMQP, Redis, Redis SSL, Redis Socket, Redis Sentinel) through a unified interface.

## Args:
    cls (type): The class being instantiated (Broker class)
    broker_url (str): Connection URL specifying the broker type and connection parameters
    *args: Additional positional arguments passed to the specific broker constructor
    **kwargs: Additional keyword arguments passed to the specific broker constructor

## Returns:
    BrokerBase subclass instance: An instance of the appropriate broker implementation (RabbitMQ, Redis, RedisSsl, RedisSocket, or RedisSentinel)

## Raises:
    NotImplementedError: When the broker URL scheme is not supported (not one of amqp, redis, rediss, redis+socket, or sentinel)

## State Changes:
    Attributes READ: None (this is a static factory method)
    Attributes WRITTEN: None (this is a static factory method)

## Constraints:
    Preconditions: 
    - broker_url must be a valid string containing a recognized scheme (amqp, redis, rediss, redis+socket, sentinel)
    - The broker URL must follow the standard URL format with scheme, host, port, path, username, and password components
    
    Postconditions:
    - Returns an instance of a concrete broker subclass matching the URL scheme
    - The returned instance is properly initialized with connection parameters from the URL

## Side Effects:
    None directly, but the returned broker instance may establish connections to external services upon initialization

### `flower.utils.broker.Broker.queues` · *method*

## Summary:
Retrieves detailed statistics for specified message queues from a message broker.

## Description:
Fetches metadata and message count statistics for a list of queue names from the underlying message broker. This method serves as an abstract interface that must be implemented by concrete broker subclasses (RabbitMQ, Redis, etc.). The method is designed to provide queue monitoring capabilities for Flower's web UI and analytics.

## Args:
    names (list[str]): A list of queue names to retrieve statistics for. Must be a non-empty list of strings.

## Returns:
    list[dict]: A list of dictionaries containing queue information. Each dictionary contains:
        - 'name' (str): The queue name as provided in the input
        - 'messages' (int): The total number of messages in the queue (for Redis-based brokers)
        - Additional broker-specific fields may be present depending on implementation (e.g., RabbitMQ may include 'consumers', 'state', etc.)

## Raises:
    NotImplementedError: When called on the abstract Broker base class (this method should be overridden by subclasses)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The broker must be properly initialized and connected
    - The names parameter must be a list of strings
    - The broker implementation must support queue information retrieval
    
    Postconditions:
    - Returns a list of queue information dictionaries matching the input names order
    - Each returned dictionary contains at least a 'name' field
    - Empty list is returned if no queues match the provided names or if broker communication fails
    - Method is asynchronous and must be awaited

## Side Effects:
    - Makes network requests to the message broker's API (for RabbitMQ)
    - Performs Redis operations (for Redis-based brokers)
    - May log errors if broker communication fails
    - May block execution while waiting for broker responses

## `flower.utils.broker.main` · *function*

## Summary
Command-line utility that queries broker queue information by processing arguments and invoking broker queue retrieval.

## Description
This asynchronous function serves as the command-line entry point for retrieving message broker queue information. It processes command-line arguments to configure broker connection parameters, instantiates a broker object (which handles the actual broker-specific implementation), and retrieves queue statistics from the configured broker backend.

The function provides a unified command-line interface for accessing queue information from various broker types through their respective APIs.

## Args
This function does not accept any explicit arguments but reads from command-line arguments:
- sys.argv[1] (optional): Broker URL (default: 'amqp://'). Determines the broker type via URL scheme.
- sys.argv[2] (optional): Queue name to query (default: 'celery').
- sys.argv[3] (optional): HTTP API endpoint URL (default: 'http://guest:guest@localhost:15672/api/').

## Returns
This function does not return any value. It prints queue information directly to stdout when queues are found.

## Raises
This function does not explicitly raise exceptions but may propagate exceptions from:
- Broker instantiation when an unsupported URL scheme is provided
- Broker queue retrieval operations when API calls fail
- Network connectivity issues when making HTTP requests to broker management APIs

## Constraints
Preconditions:
- The script must be run from the command line with appropriate arguments
- Valid broker URL must be provided (supported schemes: amqp, redis, rediss, redis+socket, sentinel)
- Required broker credentials must be accessible via URL or defaults

Postconditions:
- If queues are found, their information is printed to standard output
- If no queues are found or errors occur, nothing is printed (silent failure)

## Side Effects
- Prints queue information to standard output
- Makes HTTP requests to broker management APIs (when using AMQP brokers)
- May establish network connections to broker services
- Uses global sys.argv for argument parsing

## Control Flow
```mermaid
flowchart TD
    A[Start main()] --> B{argv length}
    B -->|< 2| C[Set broker_url = 'amqp://']
    B -->|≥ 2| D[Set broker_url = argv[1]]
    D --> E{argv length}
    E -->|< 3| F[Set queue_name = 'celery']
    E -->|≥ 3| G[Set queue_name = argv[2]]
    G --> H{argv length}
    H -->|< 4| I[Set http_api = 'http://guest:guest@localhost:15672/api/']
    H -->|≥ 4| J[Set http_api = argv[3]]
    J --> K[Create broker instance with broker_url and http_api]
    K --> L[Call broker queues method with queue_name]
    L --> M{queues found?}
    M -->|Yes| N[Print queues]
    M -->|No| O[Exit silently]
```

## Examples
```bash
# Query default celery queue with default AMQP broker
python broker.py

# Query specific queue with custom AMQP broker
python broker.py amqp://user:pass@rabbitmq.example.com:5672/ myqueue

# Query with custom Redis broker and API endpoint
python broker.py redis://:password@redis.example.com:6379/ myqueue http://admin:secret@redis-api.example.com:8080/
```

