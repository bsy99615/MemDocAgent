# `imap4.py`

## `imapclient.imap4.IMAP4WithTimeout` · *class*

## Summary:
IMAP4WithTimeout is a wrapper around imaplib.IMAP4 that adds configurable timeout support for IMAP connections.

## Description:
This class extends the standard imaplib.IMAP4 class to provide enhanced timeout control for IMAP network operations. It allows setting a default timeout that can be overridden on a per-operation basis. The class is designed to be used when reliable network operation timing is required, particularly in environments where network latency or unresponsive mail servers need to be handled gracefully.

The primary motivation for this abstraction is to provide consistent timeout behavior across IMAP operations while maintaining compatibility with the existing imaplib.IMAP4 interface. This enables applications to set reasonable timeouts for network operations without having to manage socket-level timeouts manually.

## State:
- `_timeout`: Optional[float] - The default timeout value to use for socket connections. Can be None for no timeout.
- `host`: str - The hostname of the IMAP server being connected to.
- `port`: int - The port number of the IMAP server being connected to.
- `sock`: socket.socket - The underlying socket connection to the IMAP server.
- `file`: BufferedReader - A file-like object created from the socket for reading IMAP responses.

## Lifecycle:
- Creation: Instantiate with address (str), port (int), and timeout (Optional[float])
- Usage: Call open() to establish connection, then use standard IMAP methods
- Destruction: Should be closed via close() method or context manager when done

## Method Map:
```mermaid
graph TD
    A[IMAP4WithTimeout.__init__] --> B[imaplib.IMAP4.__init__]
    A --> C[Sets _timeout]
    B --> D[Initializes IMAP connection]
    E[open()] --> F[_create_socket()]
    F --> G[socket.create_connection()]
    E --> H[Sets host, port, sock, file]
```

## Raises:
- socket.timeout: When socket operations exceed the specified timeout duration
- socket.error: When socket connection fails due to network issues
- imaplib.IMAP4.error: When IMAP protocol errors occur

## Example:
```python
# Create IMAP client with 30-second timeout
imap = IMAP4WithTimeout('imap.example.com', 993, 30.0)

# Connect to server
imap.open()

# Perform IMAP operations
imap.login('user@example.com', 'password')
imap.select('INBOX')
typ, data = imap.search(None, 'ALL')

# Close connection
imap.close()
imap.logout()
```

### `imapclient.imap4.IMAP4WithTimeout.__init__` · *method*

## Summary:
Initializes an IMAP4WithTimeout instance with connection parameters and timeout configuration.

## Description:
Configures the IMAP client with server address, port, and timeout settings. This method sets up the underlying IMAP connection parameters and establishes the default timeout behavior for subsequent network operations. The timeout value is stored for use in socket operations and can be overridden on a per-operation basis.

## Args:
    address (str): The hostname or IP address of the IMAP server to connect to.
    port (int): The port number on which the IMAP server is listening.
    timeout (Optional[float]): The default timeout in seconds for socket operations. If None, no timeout is applied.

## Returns:
    None: This method initializes the object state and does not return a value.

## Raises:
    socket.timeout: When socket operations exceed the specified timeout duration.
    socket.error: When socket connection fails due to network issues.
    imaplib.IMAP4.error: When IMAP protocol errors occur during initialization.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._timeout: Set to the provided timeout value
        - self.host: Set by parent class initialization
        - self.port: Set by parent class initialization  
        - self.sock: Set by parent class initialization
        - self.file: Set by parent class initialization

## Constraints:
    Preconditions:
        - address must be a valid hostname or IP address string
        - port must be a valid integer in the range 1-65535
        - timeout must be None or a positive float value
    Postconditions:
        - The object is initialized with connection parameters
        - self._timeout is set to the provided timeout value
        - The underlying IMAP connection infrastructure is prepared

## Side Effects:
    None: This method only initializes object state and does not perform I/O operations or external service calls.

### `imapclient.imap4.IMAP4WithTimeout.open` · *method*

## Summary:
Configures and establishes a network connection to an IMAP server with optional timeout support.

## Description:
Sets up the connection parameters and creates a socket connection to the specified IMAP server. This method prepares the instance for IMAP communication by establishing a network connection and creating a file-like object for reading responses from the server.

## Args:
    host (str): Hostname or IP address of the IMAP server. Defaults to empty string.
    port (int): Port number to connect to. Defaults to 143 (standard IMAP port).
    timeout (Optional[float]): Connection timeout in seconds. If None, uses the instance's default timeout setting.

## Returns:
    None: This method does not return a value.

## Raises:
    socket.timeout: When the connection attempt exceeds the specified timeout.
    socket.gaierror: When DNS resolution fails for the host.
    ConnectionRefusedError: When the server refuses the connection.
    OSError: For other socket-related errors such as network issues.

## State Changes:
    Attributes READ: self._timeout
    Attributes WRITTEN: self.host, self.port, self.sock, self.file

## Constraints:
    Preconditions:
    - host must be a valid hostname or IP address string
    - port must be a valid integer port number
    - timeout must be a positive float or None
    Postconditions:
    - Instance has configured host, port, socket, and file attributes ready for IMAP operations

## Side Effects:
    I/O operation: Creates a network connection to the remote IMAP server
    External service call: Makes a DNS lookup and TCP connection to the configured host and port

### `imapclient.imap4.IMAP4WithTimeout._create_socket` · *method*

## Summary:
Creates a socket connection to the configured host and port with specified timeout settings.

## Description:
Establishes a network socket connection to the IMAP server using the host and port configured on the instance. This method handles timeout configuration by prioritizing an explicitly passed timeout value over the instance's default timeout setting.

## Args:
    timeout (Optional[float]): Connection timeout in seconds. If None, uses the instance's default timeout (_timeout attribute).

## Returns:
    socket.socket: A connected socket object ready for IMAP communication.

## Raises:
    socket.timeout: When the connection attempt exceeds the specified timeout.
    socket.gaierror: When DNS resolution fails for the host.
    ConnectionRefusedError: When the server refuses the connection.
    OSError: For other socket-related errors such as network issues.

## State Changes:
    Attributes READ: self.host, self.port, self._timeout
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.host must be a valid hostname or IP address string
    - self.port must be a valid integer port number
    - self._timeout must be a positive float or None
    Postconditions:
    - Returns a connected socket object that can be used for IMAP communication

## Side Effects:
    I/O operation: Creates a network connection to the remote IMAP server
    External service call: Makes a DNS lookup and TCP connection to the configured host and port

