# `tls.py`

## `imapclient.tls.wrap_socket` · *function*

## Summary:
Wraps a plain socket in TLS using the provided SSLContext (or a secure default) and returns the TLS-wrapped socket ready for encrypted I/O.

## Description:
This function centralizes two related actions: obtaining a client-side SSLContext when one is not supplied, and delegating to that context to wrap the given socket with TLS while supplying the server hostname for SNI/hostname verification.

Known callers within the provided code snapshot:
    - No direct callers were present in the supplied file excerpt. In an IMAP client library, typical call sites include:
        - Connection-establishment paths that open a fresh TLS connection to an IMAP server.
        - STARTTLS or upgrade code paths that take an already-connected TCP socket and upgrade it to use TLS.

Why the logic is extracted:
    - Ensures a consistent and secure default SSLContext is created when callers pass None, avoiding duplication of default-context creation.
    - Guarantees the server_hostname argument is passed to the TLS layer so SNI and certificate hostname verification can function consistently across the codebase.
    - Delegates TLS-specific configuration and handshake semantics to ssl.SSLContext, keeping socket-management code independent of SSL policy.

## Args:
    sock (socket.socket):
        A Python socket.socket instance. The socket should be suitable for use by the SSL routines (typically created via socket.socket()) and usually connected to the remote peer if a TLS handshake is expected immediately.
    ssl_context (Optional[ssl.SSLContext]):
        An ssl.SSLContext instance to use for wrapping. If None, the function calls ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH) to create a secure client-side default context.
        - Allowed values: ssl.SSLContext or None.
        - Interdependency: behavior of the returned wrapped socket (verification, ciphers, handshake timing) is entirely governed by the provided SSLContext.
    host (str):
        The server name passed as server_hostname to SSLContext.wrap_socket. Used for SNI and for hostname verification performed by the SSLContext.
        - Recommendation: pass the DNS hostname expected in the server certificate. Passing an IP address may cause hostname verification failures unless the certificate explicitly covers the IP.

## Returns:
    socket.socket:
        The object returned by ssl_context.wrap_socket(sock, server_hostname=host). Typically an instance of ssl.SSLSocket (a socket-like object) that provides encrypted I/O. The function returns this object directly and does not further modify or wrap it.

## Raises:
    The function does not raise exceptions itself; it directly calls ssl.create_default_context (when ssl_context is None) and ssl.SSLContext.wrap_socket. Any exceptions from those calls propagate to the caller unchanged. Common exceptions you should be prepared to handle include:
        - ssl.SSLError (and its subclasses, e.g., ssl.SSLWantReadError, ssl.SSLWantWriteError): TLS-level errors, handshake failures, or non-blocking handshake indicators.
        - OSError (socket-level errors): underlying socket errors such as connection reset, broken pipe, or network I/O errors during handshake.
        - ValueError or TypeError: raised if invalid argument types/values are passed to the underlying SSL APIs.

## Constraints:
    Preconditions:
        - sock must be a valid socket.socket instance.
        - host should represent the server name you intend to verify against the server certificate; this is a caller responsibility if hostname verification is desired.
        - If sock is non-blocking, callers must handle non-blocking TLS handshake behavior as signaled by ssl.SSLWantReadError / ssl.SSLWantWriteError from the underlying SSL APIs.
    Postconditions:
        - The returned object is the direct result of ssl_context.wrap_socket(sock, server_hostname=host) (with ssl_context created by create_default_context when the input context was None).
        - The returned socket is configured according to the SSLContext passed in (verification rules, ciphers, and handshake behavior come from that SSLContext).

## Side Effects:
    - Potential network I/O: SSLContext.wrap_socket may perform a TLS handshake that performs reads/writes on the underlying socket.
    - No module-level/global state is modified by this function.
    - No file or persistent external state is written by this function.

## Control Flow:
flowchart TD
    A[Call wrap_socket(sock, ssl_context, host)]
    A --> B{ssl_context is None?}
    B -- yes --> C[Call ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)]
    B -- no --> D[Use provided ssl_context]
    C --> E[Call ssl_context.wrap_socket(sock, server_hostname=host)]
    D --> E
    E --> F{wrap_socket succeeds?}
    F -- yes --> G[Return wrapped SSL socket]
    F -- no --> H[Underlying exception propagates to caller]

## Examples:
    Example — upgrade a connected TCP socket to TLS with error handling (conceptual):
        1. Create and connect a TCP socket to the server (socket = socket.socket(...); socket.connect((addr, port))).
        2. Call the function: wrapped = wrap_socket(socket, None, "imap.example.com").
           - Passing None uses a secure default SSLContext configured for client/server authentication.
        3. If the call returns successfully, use 'wrapped' for subsequent encrypted protocol I/O.
        4. If an exception is raised (e.g., ssl.SSLError, OSError), treat it as a TLS handshake or network failure: close the socket, log or surface the error, and perform any retry/backoff logic as appropriate.

    Example — using a custom SSLContext:
        1. Create and configure an ssl.SSLContext (e.g., set custom CA certs, toggle hostname checking).
        2. Pass that context to the function along with the connected socket and the expected hostname to obtain the TLS-wrapped socket whose behavior matches your custom policy.

## `imapclient.tls.IMAP4_TLS` · *class*

## Summary:
A subclass of imaplib.IMAP4 that establishes and uses a TLS-wrapped socket (typically IMAPS on port 993) as the transport for IMAP protocol I/O.

## Description:
IMAP4_TLS provides a transport-layer specialization for IMAP that uses TLS from the outset by wrapping a TCP socket with an SSLContext. It reuses imaplib.IMAP4 for protocol parsing and command/response handling, while overriding connection creation and low-level I/O so the underlying transport is an ssl.SSLSocket or another socket-like object returned by an SSLContext.

When to instantiate:
- When you need an IMAP client connection that is encrypted immediately (classic IMAPS), rather than starting plain and issuing STARTTLS.
- When you want to supply a custom ssl.SSLContext (for custom CA bundles, hostname verification policies, or client certificates) to control TLS behavior.

Constructor behavior to note:
- The constructor stores ssl_context and a default timeout, then explicitly calls imaplib.IMAP4.__init__(host, port). Because the class invokes the base-class initializer with the provided host and port, callers should be prepared for any network activity or exceptions that the base-class initializer may perform or raise in the runtime's imaplib implementation.

Responsibility boundary:
- Responsibility: create/manage the TLS-wrapped socket, provide read/line/send I/O primitives expected by imaplib.IMAP4, and delegate shutdown semantics to the parent class.
- Not responsible: IMAP protocol logic (commands, authentication, mail handling) beyond transport-level I/O.

## State:
Constructor parameters (and constraints):
- host (str)
  - Required: a string hostname passed to the parent initializer and used for SNI / hostname verification when wrapping the socket.
  - Constraint: should be a DNS hostname expected in the server certificate for hostname verification to succeed; IP addresses may fail hostname verification unless cert covers them.
- port (int)
  - Required: TCP port (commonly 993 for IMAPS).
  - Constraint: valid TCP port integer (0-65535); typical callers use 993.
- ssl_context (Optional[ssl.SSLContext])
  - Default/behavior: may be None to indicate a secure default context should be used by wrap_socket; otherwise must be an ssl.SSLContext.
- timeout (Optional[float], default None)
  - Explanation: default timeout (in seconds) used by open() when no explicit timeout argument is provided.

Instance attributes (state maintained after construction/open):
- ssl_context: Optional[ssl.SSLContext]
  - Immutable from the class's perspective after __init__; used by open() to wrap sockets.
- _timeout: Optional[float]
  - Default connect timeout fallback for open().
- host: str
  - Set by open(); contains the hostname used for the connection.
- port: int
  - Set by open(); contains the port used for the connection.
- sock: socket.socket or ssl.SSLSocket (socket-like)
  - The active underlying socket returned by wrap_socket after create_connection.
  - Invariant: when a connection is open, sock supports sendall(bytes), close(), and makefile("rb").
- file: io.BufferedReader
  - The file-like buffered reader created from self.sock.makefile("rb") and used by read() and readline().

Class invariants:
- If a connection is open, both sock and file are set and usable. read(), readline(), and send() assume these attributes are present.
- ssl_context and _timeout remain as initially set and are used by subsequent open() calls.
- Methods do not implicitly reopen or close the connection; callers must manage lifecycle sequencing.

## Lifecycle:
Creation:
- Call the constructor with host (str), port (int), ssl_context (Optional[ssl.SSLContext]) and optional timeout (Optional[float]).
- The implementation assigns ssl_context and _timeout, then calls imaplib.IMAP4.__init__(host, port). Depending on the imaplib implementation in the environment, this may cause network activity; therefore callers should catch socket/SSL exceptions around construction if they need to handle connection failures gracefully.

Opening/connecting (open method):
- Signature behavior: open(host: str = "", port: int = 993, timeout: Optional[float] = None) -> None
- Effects:
  1. Set self.host and self.port to the provided values.
  2. Call socket.create_connection((host, port), timeout if timeout is not None else self._timeout).
  3. Wrap the returned TCP socket using wrap_socket(sock, self.ssl_context, host) — this returns a wrapped TLS socket (typically ssl.SSLSocket).
  4. Create a buffered reader via self.sock.makefile("rb") and assign it to self.file.
- Timeout precedence: the call-time timeout argument is used when not None; otherwise self._timeout is used; if both are None, socket.create_connection uses its default blocking behavior.

I/O methods:
- read(size: int) -> bytes
  - Delegates to self.file.read(size). Returns bytes read; may return fewer than size bytes or b'' on EOF.
  - Precondition: open() must have successfully set self.file; otherwise AttributeError will be raised.
- readline() -> bytes
  - Delegates to self.file.readline(). Returns a single line (including trailing newline bytes if present) or b'' on EOF.
  - Precondition: open() must have successfully set self.file.
- send(data: Buffer) -> None
  - Delegates to self.sock.sendall(data). Accepts buffer-protocol objects (bytes, bytearray, memoryview). Raises TypeError if data is not a buffer-compatible object.
  - Precondition: open() must have successfully set self.sock.

Shutdown / cleanup:
- shutdown() -> None
  - Delegates to imaplib.IMAP4.shutdown(self). The exact actions (e.g., sending LOGOUT, closing socket/file) depend on the parent class's implementation; callers should handle imaplib.IMAP4.error and other exceptions that the parent may raise.
- No context manager methods are provided by this implementation; callers should explicitly call shutdown() or the library's logout/close procedures to avoid resource leaks.

Reconnection behavior:
- open() will overwrite self.sock and self.file with new objects; the class does not automatically close previously-held socket/file before overwriting them. Callers should close previous resources if necessary before calling open() again.

## Method Map:
flowchart LR
    ctor[__init__(host, port, ssl_context, timeout)]
    ctor --> assign_attrs[assign ssl_context, _timeout]
    assign_attrs --> base_init[call imaplib.IMAP4.__init__(host, port)]
    base_init --> (depends_on_imaplib)[may perform additional base-class actions]
    open_call[open(host,port,timeout)] --> create_conn[socket.create_connection((host,port),timeout||self._timeout)]
    create_conn --> wrap[wrap_socket(sock, self.ssl_context, host)]
    wrap --> set_sock[self.sock = wrapped_socket]
    set_sock --> makefile[self.file = self.sock.makefile("rb")]
    makefile --> io_ops{I/O: read/readline/send}
    io_ops --> read[read(size) -> self.file.read(size)]
    io_ops --> readline[readline() -> self.file.readline()]
    io_ops --> send[send(data) -> self.sock.sendall(data)]
    shutdown[shutdown()] --> parent_shutdown[imaplib.IMAP4.shutdown(self)]

Notes:
- The flowchart shows how construction and open() lead to the creation of sock and file, which the I/O methods use. The exact behavior of base-class initialization is implementation-dependent; callers should consult their runtime's imaplib for details.

## Raises:
Exceptions that may be raised by __init__, open, and I/O methods (propagated from underlying calls):

During __init__ / open:
- socket.gaierror, OSError (including socket.timeout)
  - From socket.create_connection: DNS resolution failures, connection refused, network unreachable, or timeouts.
- ssl.SSLError and related ssl exceptions
  - From wrap_socket or SSL operations during handshake: certificate verification failure, handshake failure, non-blocking indicators, etc.
- TypeError, ValueError
  - From invalid parameter types passed to socket/ssl APIs or if the provided ssl_context is of the wrong type.
- Any exceptions raised by imaplib.IMAP4.__init__ (e.g., imaplib.IMAP4.error)
  - These propagate unchanged.

During read/readline/send:
- AttributeError
  - If self.file or self.sock is not set because open() has not been called successfully.
- OSError or ssl.SSLError
  - If the underlying socket encounters I/O or TLS errors while reading/writing.
- TypeError
  - In send(), if the provided data does not support the buffer protocol.

Shutdown:
- Any exceptions raised by imaplib.IMAP4.shutdown will propagate; callers should be prepared to catch imaplib.IMAP4.error as appropriate.

## Example:
A safe usage pattern (pseudocode-level steps; exception handling is required in real code):

1. Prepare an optional SSLContext if custom TLS settings are needed; otherwise pass None to use a secure default via wrap_socket.
2. Instantiate the transport and handle connection-time exceptions:
   - Try to create IMAP4_TLS(host, port, ssl_context, timeout)
   - If construction/open fails with socket/ssl exceptions, handle (log/retry/raise) and ensure any partial sockets are closed.
3. Use the resulting object via imaplib IMAP methods (which internally call read/readline/send).
4. When finished, call shutdown() (or the library's logout/close routines) to close the connection and release resources.

Implementation checklist for reimplementers:
- Assign ssl_context and _timeout before delegating to the base-class initializer so open() (if invoked by the base) has access to these values.
- Implement open() to:
  - Create a TCP connection using socket.create_connection with proper timeout handling.
  - Wrap the TCP socket using an ssl.SSLContext (via a helper like wrap_socket) providing server_hostname for SNI/verification.
  - Call makefile("rb") on the wrapped socket and store the resulting buffered reader as self.file.
- Implement read(), readline(), and send() as thin delegations to self.file and self.sock respectively.
- Delegate shutdown() to the parent class to keep protocol-level teardown consistent with imaplib.IMAP4.

### `imapclient.tls.IMAP4_TLS.__init__` · *method*

## Summary:
Stores the provided SSL context and timeout on the instance, declares a type hint for an instance attribute named file, and delegates remaining initialization work to imaplib.IMAP4 by calling its constructor.

## Description:
This initializer performs three explicit operations in order:
1. Assigns the ssl_context argument to self.ssl_context.
2. Assigns the timeout argument to self._timeout.
3. Calls imaplib.IMAP4.__init__(self, host, port) to perform base-class initialization.

Known callers and lifecycle:
- Invoked when an IMAP4_TLS object is instantiated (i.e., when code calls IMAP4_TLS(host, port, ssl_context, timeout)). It runs once during object construction.
- There are no callers recorded in this source; typical usage is direct instantiation as part of client setup.

Why this logic is a separate method:
- The constructor centralizes TLS-related configuration onto the instance (self.ssl_context and self._timeout) before handing control to the base-class initializer. This keeps TLS configuration assignment localized to object construction while reusing existing imaplib initialization behavior.

## Args:
    host (str): Hostname or IP address of the IMAP server.
    port (int): TCP port number for the IMAP server.
    ssl_context (Optional[ssl.SSLContext]): SSLContext to use, or None. The constructor stores this value; it does not validate or modify the object.
    timeout (Optional[float]): Optional timeout in seconds; defaults to None. The constructor stores this value as given.

## Returns:
    None. As an initializer, it does not return a value.

## Raises:
    Any exception raised by imaplib.IMAP4.__init__(self, host, port) is propagated. This method contains no try/except and does not raise additional exceptions itself.

## State Changes:
Attributes READ:
    - None prior to assignment in this method.

Attributes WRITTEN:
    - self.ssl_context: set to the ssl_context argument.
    - self._timeout: set to the timeout argument.
    - No other attributes are assigned in this method body.

Note on self.file:
    - The source contains the statement "self.file: io.BufferedReader". This is a local variable/attribute type annotation (a type hint) present in the function body. It does not assign a value to self.file at runtime; it only documents the intended type for tooling and static analysis. Whether self.file is actually created or assigned a value is determined elsewhere (for example, by the base-class initializer or later code), and is not performed by this line.

## Constraints:
Preconditions:
    - host must be provided as a str and port as an int; this method does not perform type enforcement at runtime beyond normal Python behavior.
    - ssl_context, if provided, should be an ssl.SSLContext instance by convention; this is a caller responsibility (no runtime check here).
    - timeout, if provided, should be a numeric value representing seconds; the method does not validate range or sign.

Postconditions:
    - self.ssl_context equals the ssl_context argument passed in.
    - self._timeout equals the timeout argument passed in.
    - The base-class constructor imaplib.IMAP4.__init__ has been invoked with (host, port); any effects of that invocation are the responsibility of the base class and are not specified here.

## Side Effects:
    - Delegates to imaplib.IMAP4.__init__, so any side effects (I/O, socket creation, network calls, exceptions) originate from that call and are not implemented or handled by this method.
    - This method itself performs no additional I/O or external calls beyond the delegation above.

### `imapclient.tls.IMAP4_TLS.open` · *method*

## Summary:
Establishes a TCP connection to the specified host and port, wraps that socket with TLS using the instance's SSL context, and stores the TLS socket and a binary read file-like wrapper on the instance.

## Description:
This method performs the low-level transport setup for IMAP4_TLS: it opens a TCP connection, upgrades the connection to TLS, and prepares a binary reader for protocol input. Concretely it executes:
1. Assigns self.host and self.port from the provided arguments.
2. Calls socket.create_connection((host, port), timeout_value) to obtain a connected TCP socket.
3. Calls wrap_socket(sock, self.ssl_context, host) to obtain a TLS-wrapped socket and assigns it to self.sock.
4. Calls self.sock.makefile("rb") and assigns the result to self.file.

Known callers and lifecycle context:
- Called by client code when establishing or re-establishing a network connection for an IMAP4_TLS instance (e.g., during initial connect or reconnect).
- The method is part of the connection-establishment stage of the IMAP client lifecycle, and should be invoked before any IMAP protocol commands are sent or read.
- This file does not assume or assert whether imaplib.IMAP4.__init__ from the stdlib calls this method; callers should explicitly invoke open when they need a network connection.

Why this is a dedicated method:
- Encapsulates network, timeout, and TLS setup in one place, keeping higher-level IMAP protocol code independent of transport initialization.
- Provides a single point for handling (and propagating) connection and TLS errors, and for creating the buffering wrapper used by read/readline methods.

## Args:
    host (str): Hostname or IP address of the IMAP server to connect to. Default: "".
        - Note: An empty string is the signature default but is not a resolvable/usable value in normal operation; callers should pass a valid hostname or IP.
    port (int): TCP port number to connect to. Default: 993 (standard IMAPS port).
        - Note: Must be a valid TCP port (0-65535). Invalid values will cause socket.create_connection to raise.
    timeout (Optional[float]): Connection timeout in seconds. Default: None.
        - Behavior: If timeout is not None, it is passed directly to socket.create_connection. If timeout is None, the instance attribute self._timeout is used. If both are None, the system default blocking behavior applies.

## Returns:
    None

## Raises:
    The method does not catch exceptions; callers receive exceptions raised by the underlying operations. Notable exceptions include:
    - socket.gaierror: if hostname resolution fails.
    - socket.timeout (subclass of OSError): if the TCP connect times out.
    - OSError (including ConnectionRefusedError and other socket errors): for general network/socket failures raised by socket.create_connection or by sock.makefile.
    - ssl.SSLError (and subclasses): if wrap_socket or the underlying ssl APIs fail during TLS wrapping/handshake.
    - Any exception raised by wrap_socket or self.sock.makefile, which will propagate unchanged.

    Important: because exceptions are propagated and the method does not close resources on error, callers should handle cleanup (closing sockets/file-like objects) when errors occur to avoid resource leaks.

## State Changes:
    Attributes READ:
        - self._timeout: consulted when timeout argument is None to determine the timeout passed to socket.create_connection.
        - self.ssl_context: passed to wrap_socket to configure TLS behavior.

    Attributes WRITTEN:
        - self.host (str): set to the host argument at the start of the method.
        - self.port (int): set to the port argument at the start of the method.
        - self.sock (socket.socket or ssl.SSLSocket-like): set to the result of wrap_socket(sock, self.ssl_context, host) on success.
        - self.file (file-like, binary read): set to the result of self.sock.makefile("rb") on success. IMAP4_TLS.__init__ annotates self.file as io.BufferedReader; typical makefile implementations return a buffered binary reader.

    Notes on partial state after failures:
        - host and port are assigned before network calls and therefore will be set even if the method fails later.
        - If socket.create_connection succeeds but wrap_socket raises, the local variable sock (the raw TCP socket) will exist but self.sock will not be set; the raw socket will not be automatically closed by this method—callers should account for this potential resource leak.
        - If wrap_socket succeeds but self.sock.makefile("rb") raises, self.sock is set but self.file will not be; callers should close self.sock in that error path.

## Constraints:
    Preconditions:
        - The instance should have self.ssl_context and self._timeout attributes initialized (IMAP4_TLS.__init__ sets these).
        - Caller must provide a resolvable/ reachable host and a valid port value to obtain a successful connection.
        - If reusing an IMAP4_TLS instance, existing self.sock and self.file should be closed by the caller before calling open again to avoid resource conflicts or leaks.

    Postconditions:
        - On successful return: self.host and self.port equal the provided arguments; self.sock is a connected TLS-wrapped socket (the return value of wrap_socket) ready for encrypted I/O; self.file is a readable binary file-like wrapper for the socket.
        - On exception: no strong guarantees about self.sock/self.file beyond what is described in "State Changes" — callers should assume the connection did not complete and perform cleanup.

## Side Effects:
    - Performs network I/O: DNS resolution and TCP connect (socket.create_connection), and possible TLS handshake/network I/O during wrap_socket.
    - Allocates socket and file-like objects attached to the instance; the method does not close them on error.
    - Does not modify module- or process-level global state.

### `imapclient.tls.IMAP4_TLS.read` · *method*

## Summary:
Reads up to the requested number of bytes from the underlying connection file object and returns them as bytes; this consumes data from the connection but does not otherwise modify the object's attributes.

## Description:
This method is a thin wrapper that delegates the read to the underlying file-like object stored on self.file (set when open() constructs the TLS-wrapped socket and calls makefile("rb")). It is invoked during the network I/O phase after open() has established and wrapped the socket; typical callers are higher-level IMAP protocol routines (inherited from imaplib.IMAP4) that need to read raw bytes from the server, for example when reading command responses or literal data. This logic is a separate method so the IMAP4_TLS subclass can provide a file-backed read implementation that cleanly replaces or adapts the base class's socket/file access without duplicating buffering or socket-wrapping code.

## Args:
    size (int): Maximum number of bytes to read. The value is passed directly to the underlying file.read(size). Allowed values and exact semantics (e.g., size == 0, size < 0 meaning “read all remaining data”) follow the behavior of the underlying file-like object returned by socket.makefile; callers should pass a non-negative integer when they require a bounded read.

## Returns:
    bytes: A bytes object containing up to size bytes read from the underlying file. The returned length may be:
        - between 1 and size bytes when data is available,
        - fewer than size if fewer bytes are immediately available,
        - b'' when end-of-file is reached.
    The method returns whatever the underlying file.read returns, unchanged.

## Raises:
    Propagates any exception raised by self.file.read(size). Examples (dependent on the underlying implementation) include:
        - OSError or socket.error: on low-level I/O or network errors.
        - ValueError: if the underlying file is closed or the call is otherwise invalid.
    The method does not catch or convert these exceptions; callers should handle them as appropriate for their context.

## State Changes:
    Attributes READ:
        - self.file
    Attributes WRITTEN:
        - (none) — this method does not assign or mutate attributes on self.

## Constraints:
    Preconditions:
        - open() must have been called successfully (or otherwise self.file must be a configured, readable file-like object).
        - self.file must implement a read(int) -> bytes interface.
        - size must be an integer (the code signature enforces this; callers in dynamically-typed contexts should ensure an int is provided).
    Postconditions:
        - The connection/file position is advanced by the number of bytes returned.
        - No attributes on self are modified by this call.

## Side Effects:
    - Performs blocking I/O on the underlying socket/file: calling this will read data from the network connection associated with self.file and may block until data is available or an error/EOF occurs.
    - No other external side effects (no writes, no attribute changes).

### `imapclient.tls.IMAP4_TLS.readline` · *method*

## Summary:
Read the next line of bytes from the underlying connection file-like object and return it; advances the connection read cursor.

## Description:
This is a thin delegating wrapper that returns the result of calling readline() on the object's binary file-like reader (self.file) which is created by open(). It is invoked during IMAP protocol reads where the client needs to obtain the next server response line (for example, by higher-level IMAP response-parsing code or any consumer of the IMAP4_TLS instance that reads protocol data). There are no callers inside this class beyond other convenience methods; the method exists separately to keep a small, testable, and mockable surface that centralizes how line-oriented reads are performed over the TLS-wrapped socket.

Why this is a separate method:
- Provides a consistent interface alongside read() and send() for interacting with the underlying connection.
- Makes testing and substitution (e.g., mocking the file object) straightforward.
- Keeps connection-specific IO encapsulated so higher-level code does not access self.file directly.

## Args:
    None

## Returns:
    bytes: The next line read from self.file, returned as a bytes object. The returned bytes include the trailing newline (b'\n' or b'\r\n') when present. If the connection reaches EOF, an empty bytes object (b'') is returned.

## Raises:
    AttributeError: If self.file has not been set on this instance (e.g., open() was not called), attribute access to self.file will raise this error.
    Any exception raised by the underlying file-like object's readline() call is propagated. Common examples (not exhaustive) include:
        - ValueError: If the underlying file is closed, the file object's methods may raise ValueError.
        - socket.timeout: If a socket-level timeout occurred while reading.
        - ssl.SSLError or OSError: For SSL or lower-level I/O errors.
    The method does not catch or wrap these exceptions; callers should handle them as appropriate.

## State Changes:
    Attributes READ:
        - self.file: The method invokes self.file.readline() and therefore reads this attribute.
    Attributes WRITTEN:
        - None: This method does not assign to any attributes on self.

## Constraints:
    Preconditions:
        - self.file must exist and be a readable binary file-like object with a readline() method. In this class, open() sets self.file via self.sock.makefile("rb").
        - The connection and underlying socket must be in a state that allows reading; otherwise underlying I/O errors may occur.
    Postconditions:
        - If a non-empty line is returned, the internal file cursor is advanced past that line.
        - If EOF is reached, an empty bytes object (b'') is returned.
        - No attributes of the IMAP4_TLS instance are modified by this call.

## Side Effects:
    - Performs blocking I/O on the underlying connection: the call may block until a newline is received, EOF is encountered, or a socket timeout occurs.
    - Advances the read position of the underlying file-like object (self.file).
    - May propagate network/SSL-related errors from the underlying socket; it does not perform network writes or alter external resources beyond reading from the connection.

### `imapclient.tls.IMAP4_TLS.send` · *method*

## Summary:
Sends the supplied bytes-like buffer over the instance's underlying socket using a blocking write; it forwards data to the socket's sendall and does not mutate the IMAP4_TLS object's attributes.

## Description:
This is a focused I/O helper that delegates raw network transmission to self.sock.sendall. It is used as the single place to perform outbound writes for an IMAP4_TLS instance so that higher-level IMAP protocol code can rely on a consistent blocking-send behavior.

Known callers and context:
- open(): initializes self.sock (and self.file) earlier in the connection lifecycle; after open() establishes the TLS socket, subsequent IMAP protocol operations will call send to transmit commands and literals.
- Higher-level IMAP command-sending logic (inherited from imaplib.IMAP4 or implemented in client code) — during the request/command phase of an IMAP session, these components prepare protocol bytes and invoke send to write them to the server.
- Complementary read methods on this class (read and readline) consume data received from the server; together they implement the low-level request/response I/O pipeline.

Rationale for separation:
Keeping this as a separate method centralizes the blocking send behavior and error propagation in one place, simplifying testing (easy to mock/override), reasoning about timeouts, and consistent handling of bytes-like buffers.

## Args:
    data (typing_extensions.Buffer): A buffer-compatible object (e.g., bytes, bytearray, memoryview) containing the exact bytes to transmit. The caller is responsible for any necessary encoding or framing required by the IMAP protocol.

## Returns:
    None: A normal return indicates the underlying sendall call completed (i.e., it returned without raising). This means the entire buffer was accepted by the socket API for transmission; it does not guarantee higher-layer acknowledgement.

## Raises:
    The method does not catch exceptions; any exception raised by self.sock.sendall is propagated to the caller. Possible classes include lower-level I/O and SSL errors coming from the socket implementation (for example OSError/socket.error, socket.timeout, ssl.SSLError), and TypeError if the provided data is not buffer-compatible. Callers must handle these exceptions as appropriate for their context.

## State Changes:
    Attributes READ:
        - self.sock: accessed to perform the send operation; must be a socket-like object with a sendall method.
    Attributes WRITTEN:
        - None: this method does not modify attributes on self.

## Constraints:
    Preconditions:
        - self.sock must be set to a connected socket-like object (typically established by open()) and must expose a sendall(buffer) method.
        - The socket must be in a writable state (not closed).
        - The provided data must be a bytes-like/buffer-compatible object; concurrent mutation of the buffer during send is unsafe.

    Postconditions:
        - If the method returns normally, sendall was invoked and completed for the full buffer; no attributes of self were changed by this method.
        - If an exception is raised, no guarantees are made about how many bytes were transmitted prior to the error.

## Side Effects:
    - Performs blocking network I/O on self.sock; the call can block until the operating system accepts the bytes or until a configured socket timeout expires.
    - May raise network-related exceptions originating from the underlying socket/SSL layer, which will propagate to the caller.
    - Does not perform any logging, buffering, or retries; those concerns must be handled by higher-level code if desired.

### `imapclient.tls.IMAP4_TLS.shutdown` · *method*

## Summary:
Delegates teardown of the IMAP connection to the base imaplib.IMAP4 implementation; the method itself performs no additional logic and returns None.

## Description:
This method is a thin wrapper that calls imaplib.IMAP4.shutdown(self). It exists to preserve the same public API surface as the parent class (imaplib.IMAP4) and to provide a single place where TLS-specific shutdown behavior could be added in the future without changing call sites.

Known callers / lifecycle stage:
- The method is intended to be called at connection teardown (after using open(), or when cleaning up a connection). There are no callers referenced in this module; callers will be external user code or higher-level cleanup routines.

Why separate:
- Keeping shutdown on the subclass as a distinct method allows the subclass to override or extend shutdown behavior later while delegating to the parent implementation for current behavior.

## Args:
    None

## Returns:
    None

## Raises:
    Any exception raised by imaplib.IMAP4.shutdown(self) is propagated. This wrapper does not catch or translate exceptions.

## State Changes:
Attributes READ:
    - The wrapper body does not read any IMAP4_TLS-specific attributes.
Attributes WRITTEN:
    - The wrapper body does not assign to any IMAP4_TLS-specific attributes.
Note: The underlying imaplib.IMAP4.shutdown implementation that is invoked may read or modify connection-related attributes (for example, socket or file-like attributes) as part of its teardown.

## Constraints:
Preconditions:
    - The instance must be a properly-initialized IMAP4_TLS object (i.e., __init__ has been run). The wrapper itself enforces no additional preconditions.
Postconditions:
    - After this method returns, the base-class shutdown logic has executed. Any guarantees about cleaned-up resources or connection state are those provided by imaplib.IMAP4.shutdown.

## Side Effects:
    - Delegates to the base implementation which may perform network I/O and close underlying socket/file descriptors. The wrapper itself does not perform direct I/O.
    - No modification to TLS-specific attributes is performed by this wrapper; any external resource changes are a consequence of the invoked base-class method.

## Implementation note:
    - Reimplement by directly calling the base-class shutdown, for example: imaplib.IMAP4.shutdown(self) (the current implementation uses this explicit call rather than super()).

