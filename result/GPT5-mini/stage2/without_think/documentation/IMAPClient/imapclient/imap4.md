# `imap4.py`

## `imapclient.imap4.IMAP4WithTimeout` · *class*

## Summary:
A small subclass of imaplib.IMAP4 that stores an instance-level default network timeout and uses it when creating the underlying socket connection unless an explicit timeout is provided to open().

## Description:
IMAP4WithTimeout exists to let callers provide a default timeout value (seconds, float) that will be used for TCP connection attempts performed by this IMAP client. It preserves all higher-level IMAP behavior in imaplib.IMAP4 and only changes how the socket for the connection is created.

When to instantiate:
- When you need an imaplib.IMAP4-compatible client but want a reusable default timeout for connection attempts.
- Instantiate directly via IMAP4WithTimeout(address, port, timeout).

Design/motivation:
- Responsibility: maintain self._timeout and apply it to socket.create_connection calls invoked by this class.
- Boundary: it does not reimplement IMAP protocol operations; authentication and command methods are those of the imaplib.IMAP4 base class.

## State:
Attributes (names, types, when created, and invariants):

- _timeout: Optional[float]
  - Type: float or None
  - Set in __init__ to the value passed by the caller.
  - Meaning: default timeout in seconds for socket.create_connection when open() is called without an explicit timeout.
  - Valid values: None or any float accepted by socket.create_connection. The class does not validate numeric range.

- host: str
  - Type: str
  - Set by open(host, port, timeout). May not exist before open() has been called.

- port: int
  - Type: int
  - Set by open(host, port, timeout). May not exist before open() has been called.

- sock: socket.socket
  - Type: socket.socket
  - Created by open() via _create_socket(...). May not exist before open() has been called.
  - Invariant (if present): should represent the active connection socket returned by socket.create_connection.

- file: file-like binary object
  - Type: file-like object
  - Created by open() as sock.makefile("rb"). May not exist before open() has been called.
  - Invariant: if sock exists and is connected, file is expected to be the buffered reader produced from sock.

Class invariants:
- _timeout remains whatever was assigned in __init__ unless the caller mutates it directly.
- host, port, sock, file only become defined when open() executes successfully.

## Lifecycle:
Creation
- Call IMAP4WithTimeout(address: str, port: int, timeout: Optional[float]).
  - address: required hostname or IP (str).
  - port: required TCP port (int).
  - timeout: required positional argument in the signature (may be None); pass None to indicate no instance default.

What __init__ does (observable):
- Stores the provided timeout on self._timeout.
- Calls imaplib.IMAP4.__init__(self, address, port) and lets any exceptions from the parent propagate.

Usage / typical sequence
1. Instantiate: client = IMAP4WithTimeout("imap.example.com", 143, timeout=10.0)
2. If a connection is needed (or to re-open), call:
   - client.open(host="imap.example.com", port=143, timeout=None)
   - Behavior: open sets self.host and self.port, calls _create_socket(timeout) to obtain a socket, then sets self.file = sock.makefile("rb").
   - Timeout selection: the explicit timeout argument to open() is used if it is not None; otherwise self._timeout is used.
3. Use imaplib.IMAP4 methods (login, select, fetch, etc.) as usual.
4. Cleanup: close the connection via the base-class mechanisms (e.g., logout()) or by explicitly closing client.file and client.sock if present.

Destruction / cleanup responsibilities
- This subclass does not implement its own close/cleanup helpers. Callers should ensure that file and sock are closed via imaplib.IMAP4.logout() or manual close to free resources.

## Method Map:
flowchart LR
    Init[__init__(address, port, timeout)] --> SetTimeout[set self._timeout]
    SetTimeout --> ParentInit[imaplib.IMAP4.__init__(address, port)]
    Open[open(host, port, timeout=None)] --> SetHostPort[set self.host,self.port]
    Open --> CreateSocket[_create_socket(timeout)]
    CreateSocket --> SocketCall[socket.create_connection((self.host,self.port), timeout_to_use)]
    SocketCall --> Sock[socket.socket returned]
    Open --> MakeFile[self.file = self.sock.makefile("rb")]

Notes:
- timeout_to_use = timeout if timeout is not None else self._timeout
- The parent constructor is invoked from __init__; whether it opens a connection depends on imaplib.IMAP4 implementation and is not asserted here.

## Raises:
Exceptions that may propagate from this class (all originate from called library functions and are not caught here):

- From imaplib.IMAP4.__init__(...) (propagated):
  - Any exceptions raised by the parent constructor. The specific exceptions depend on imaplib implementation and environment.

- From open(...) / _create_socket(...):
  - socket.gaierror: name resolution failure for host.
  - socket.timeout: if a timeout occurs during connection (raised by socket.create_connection or underlying socket operations).
  - OSError / ConnectionRefusedError / other socket-related errors: if the connection is refused, network is unreachable, etc.
  - TypeError / ValueError: if arguments passed to socket.create_connection are of incorrect types.

Notes:
- This class intentionally propagates socket and imaplib exceptions to the caller; it does not intercept or wrap them.

## Example:
# Create client with a 10-second default timeout
client = IMAP4WithTimeout("imap.example.com", 143, timeout=10.0)

# Optionally (re)open with an explicit per-call timeout of 5 seconds:
client.open("imap.example.com", 143, timeout=5.0)

# Perform IMAP actions using base-class methods:
# client.login(user, password)
# client.select("INBOX")

# When finished, close resources:
# Prefer base-class logout if available:
# client.logout()
# Or explicitly:
# if hasattr(client, "file") and client.file is not None:
#     client.file.close()
# if hasattr(client, "sock") and client.sock is not None:
#     client.sock.close()

### `imapclient.imap4.IMAP4WithTimeout.__init__` · *method*

## Summary:
Store the instance default network timeout and perform base-class initialization with the given address and port, leaving the object ready for subsequent connection/open operations (or propagating any errors raised by the parent constructor).

## Description:
This constructor is invoked when creating an IMAP4WithTimeout instance (typical caller: client code that needs an imaplib.IMAP4-compatible client with a reusable default connection timeout). It runs at object creation time and performs two things in sequence:
1. Saves the supplied timeout value onto the instance (self._timeout).
2. Delegates remaining initialization to imaplib.IMAP4.__init__(self, address, port).

Known callers and context:
- Direct instantiation in application code, e.g. IMAP4WithTimeout("imap.example.com", 143, timeout=10.0).
- The constructor is called during the creation/lifecycle initialization stage; after it returns successfully the instance is constructed and ready for connection/open operations (subject to whether the parent constructor opened a connection).

Why this is a separate method:
- The constructor centralizes the action of establishing the instance-level default timeout before delegating to the parent. This ordering ensures the object holds the desired default timeout (used later by open()/_create_socket) even if the parent constructor performs any initialization that may depend on instance state or trigger connection logic. Separating this concern keeps timeout management isolated and backward-compatible with the imaplib.IMAP4 API.

## Args:
    address (str):
        Hostname or IP of the IMAP server. Required positional argument. No validation is performed here; invalid values will be handled (or cause errors) by the base-class initializer or later network calls.
    port (int):
        TCP port number for the IMAP server. Required positional argument. Must be an integer acceptable to the underlying IMAP/network code.
    timeout (Optional[float]):
        Instance default network timeout in seconds. Use None to indicate no instance default (i.e., rely on per-call timeouts or system defaults). The value is stored as-is; valid values are None or any float that socket.create_connection accepts. This constructor does not enforce numeric range or type beyond the annotation.

## Returns:
    None

## Raises:
    Any exception raised by imaplib.IMAP4.__init__(self, address, port) will propagate unchanged. Possible propagated errors (originating from the parent initializer or its network operations) include, but are not limited to:
    - socket.gaierror: DNS/name-resolution failures for the provided address.
    - socket.timeout: if a connection attempt times out.
    - OSError / ConnectionRefusedError: network/OS-level connection failures.
    - TypeError / ValueError: if incorrect argument types are passed downstream.
    Note: this constructor does not catch or wrap exceptions — callers should handle these as appropriate.

## State Changes:
Attributes READ:
    - None (this constructor does not read existing instance attributes).

Attributes WRITTEN:
    - self._timeout: set to the exact value passed in the timeout argument.
    - Additionally, imaplib.IMAP4.__init__ may set or modify other instance attributes (for example: host, port, sock, file) as part of its initialization; those writes are performed by the parent initializer, not directly by this method.

## Constraints:
Preconditions:
    - Caller should pass a string for address and an int for port to match expected types. While the method does not validate types, incorrect types may cause errors in the base-class initializer or later network operations.
    - The timeout argument may be None or a float; passing other types may lead to runtime errors later when the timeout is used (e.g., by socket.create_connection).

Postconditions:
    - On successful return, self._timeout is set to the provided timeout value.
    - The base-class initializer has completed; any attributes it establishes (host, port, sock, file, etc.) will reflect its behavior.
    - If the parent initializer raised an exception, this constructor does not complete and no postconditions are guaranteed.

## Side Effects:
    - Calls imaplib.IMAP4.__init__(self, address, port). Depending on the imaplib implementation and environment, that call may perform network I/O (e.g., establishing a TCP connection), allocate sockets and file objects, and register resources that must later be closed.
    - No other I/O or external service calls are made directly by this constructor; all side effects beyond assigning self._timeout originate from the parent initializer.

### `imapclient.imap4.IMAP4WithTimeout.open` · *method*

## Summary:
Assigns the target host and port on the instance, opens a TCP connection using the configured timeout behavior, stores the connected socket on the instance, and creates a binary read file-like wrapper for that socket. The object gains an open socket (self.sock) and file object (self.file) on success.

## Description:
Known callers and context:
- imaplib.IMAP4.__init__ (via superclass initialization) or user code that explicitly calls IMAP4WithTimeout.open to establish the IMAP connection. This method is invoked during the connection/open phase of the IMAP client lifecycle when a network connection to the IMAP server must be created and prepared for protocol I/O.

Why this logic is a separate method:
- Keeps the high-level connection setup (assigning host/port and wiring instance attributes) separate from the low-level socket creation logic (handled by _create_socket). This separation makes it easier to override, test, or adapt socket-creation / timeout strategies without changing the attribute wiring and file-wrapping responsibilities of open.

## Args:
    host (str): Hostname or IP address to connect to. Defaults to the empty string ("") if not provided.
    port (int): TCP port number for the IMAP service. Defaults to 143.
    timeout (Optional[float]): Per-call connection timeout in seconds. If provided (not None) this timeout is passed to the socket creation routine; if None, the instance default self._timeout is used by _create_socket. Values should be non-negative floats or None.

## Returns:
    None

## Raises:
    Propagated exceptions from socket creation and file wrapping. Notably:
    - socket.timeout: if the TCP connect attempt times out.
    - socket.gaierror: if the host address cannot be resolved.
    - OSError (and subclasses): for other connection or I/O errors (connection refused, network unreachable, errors from sock.makefile, etc).
    These exceptions are not caught or wrapped by this method; they originate from _create_socket or socket.makefile.

## State Changes:
Attributes READ:
    - self._timeout (indirectly, because open passes timeout to _create_socket which will read self._timeout when the passed timeout is None)

Attributes WRITTEN:
    - self.host: set to the provided host argument
    - self.port: set to the provided port argument
    - self.sock: set to the socket.socket instance returned by _create_socket (connected)
    - self.file: set to the file-like object returned by self.sock.makefile("rb")

## Constraints:
Preconditions:
    - The caller should supply host as a hostname/IP string and port as an integer (the method does not validate types beyond passing them to socket APIs).
    - If host is not a valid resolvable name or port is invalid, underlying socket APIs will raise exceptions.
    - If the timeout argument is None, the instance attribute self._timeout should contain the desired default timeout (or be None to let the socket API use its default behavior).

Postconditions:
    - On successful return:
        * self.host == host (the value provided)
        * self.port == port (the value provided)
        * self.sock is a connected socket.socket object connected to (self.host, self.port)
        * self.file is a binary-read file-like wrapper for self.sock (the result of self.sock.makefile("rb"))
        * The method returns None
    - On exception: none of the attributes beyond those assigned before the failing call (host and port) will be relied upon as valid connected resources; exceptions from socket creation or makefile are propagated.

## Side Effects:
    - Performs network I/O: DNS resolution and a TCP connection attempt to the configured host and port.
    - May block for up to the configured timeout (per-call or instance default).
    - Allocates OS resources: an open socket file descriptor and a separate file-like object that also holds resources. The caller (or other parts of the object lifecycle) is responsible for closing self.file and self.sock to free resources.
    - May raise networking-related exceptions to the caller; no internal retry or recovery is performed.

### `imapclient.imap4.IMAP4WithTimeout._create_socket` · *method*

## Summary:
Creates and returns a connected TCP socket to the instance's configured host and port, using the provided per-call timeout if given or the instance default otherwise; the method itself does not mutate object state.

## Description:
Known callers and context:
- IMAP4WithTimeout.open: Invoked during the connection/opening phase. In open, self.host and self.port are assigned, then this method is called to obtain a connected socket which open assigns to self.sock and wraps with self.file.

Why this is a separate method:
- Isolates the socket creation and timeout-selection logic so open remains focused on higher-level connection setup (assigning attributes and wiring self.sock/self.file). This separation makes the connection behavior easy to override or test in subclasses.

## Args:
    timeout (Optional[float]): Per-call connection timeout in seconds. If None, the instance attribute self._timeout is used. Values should be non-negative floats or None; the method does not validate numeric ranges and will pass the value to the underlying socket API.

## Returns:
    socket.socket: A socket.socket object that has been connected to (self.host, self.port) by socket.create_connection. The caller receives ownership of the socket and is responsible for closing it when no longer needed.

## Raises:
    The method propagates exceptions raised by socket.create_connection. Notable exceptions include:
    - socket.timeout: if the connect attempt times out.
    - socket.gaierror: for address resolution failures.
    - OSError (and subclasses): for other connection errors (connection refused, network unreachable, etc).
    The method does not catch, wrap, or re-raise these exceptions.

## State Changes:
    Attributes READ:
        - self.host
        - self.port
        - self._timeout
    Attributes WRITTEN:
        - None (the method does not assign or mutate self attributes)

## Constraints:
    Preconditions:
        - self.host must be set to a hostname or IP string prior to calling (open sets this before calling).
        - self.port must be set to an integer prior to calling (open sets this before calling).
        - If both the timeout argument and self._timeout are None, socket.create_connection is called with timeout=None (behavior determined by the socket library).
    Postconditions:
        - On successful return, the returned socket is connected to (self.host, self.port).
        - On exception, no attributes on self are modified by this method.

## Side Effects:
    - Performs network I/O: DNS resolution and a TCP connection attempt to the configured host and port.
    - May block for up to the configured timeout value (or according to the socket module semantics when timeout is None).
    - Does not itself store file descriptors on self; the caller is expected to assign and manage the returned socket (for example, open assigns it to self.sock).

