# `broker.py`

## `flower.utils.broker.BrokerBase` · *class*

## Summary:
A minimal abstract base for broker adapters that parses a broker URL into connection attributes (host, port, vhost, username, password) and defines an async abstract API entry point `queues`.

## Description:
BrokerBase centralizes URL parsing and credential extraction for broker implementations. It should be subclassed by concrete broker adapters that implement the async `queues(names)` method to provide broker-specific queue information. This class performs no network I/O, manages no connections, and imposes no return-type contract for `queues` (subclasses define that contract).

Typical scenarios:
- A broker-specific adapter class inherits from BrokerBase, calls super().__init__(broker_url, ...) to populate connection attributes, and implements `queues`.
- Code that requires broker-agnostic parsing can instantiate a subclass that implements `queues`.

Motivation and responsibility boundary:
- Responsibility: parse broker_url and expose standard connection attributes in a consistent way for subclasses and downstream code.
- Boundary: BrokerBase does not attempt to validate reachability, open connections, or interpret queue details; those responsibilities belong to subclasses.

## State:
Attributes created during __init__ (public instance attributes):

- host (str | None)
  - Source: parsed broker URL hostname.
  - Valid values: hostname string or None when URL lacks a hostname.
  - Invariant: set once during initialization; not modified by BrokerBase.

- port (int | None)
  - Source: parsed broker URL port.
  - Valid values: integer port number or None when URL lacks an explicit port.
  - Invariant: numeric port or None; BrokerBase performs no normalization beyond urlparse.

- vhost (str)
  - Source: parsed broker URL path with leading slash removed (purl.path[1:]).
  - Valid values: empty string when path is '/' or path is empty; otherwise the path substring after the first '/'.
  - Invariant: string type after initialization.

- username (str | None)
  - Source: parsed broker URL username; URL-decoded using urllib.parse.unquote only when the parsed username is truthy.
  - Valid values: decoded username string, empty string, or None.
  - Note: If username is falsy (for example None or empty string), the attribute is left unchanged (i.e., empty string remains empty string; None remains None).

- password (str | None)
  - Source: parsed broker URL password; URL-decoded using urllib.parse.unquote only when the parsed password is truthy.
  - Valid values: decoded password string, empty string, or None.
  - Same handling notes as username.

Constructor parameter note:
- broker_url (required): passed to urllib.parse.urlparse. It should be a string-like URL; otherwise urlparse may raise a TypeError.

Class invariants:
- After __init__, the five attributes above are always defined on the instance.
- BrokerBase does not open or close network resources; no side effects beyond attribute assignment.

## Lifecycle:
Creation:
- Call the constructor with a broker URL string: BrokerBase(broker_url, *_, **__) or, in practice, a subclass should call super().__init__(broker_url, ...).
- Extra positional and keyword arguments passed to __init__ are ignored by BrokerBase (the signature accepts *_, **__).

Usage:
- Typical pattern: subclass implements `async def queues(self, names)` and user code awaits that method on an instance of the subclass.
- There is no required ordering between attribute access and calling `queues`; attributes are available immediately after construction.

Destruction / cleanup:
- BrokerBase manages no resources and therefore defines no close/cleanup methods.
- If a subclass allocates resources (network clients, sockets, connections), that subclass is responsible for providing appropriate cleanup (context manager, close method, or async finalizer).

## Method Map:
A minimal flow of creation and method responsibilities:

flowchart LR
    A[Instantiate subclass: subclass.__init__(broker_url,...)] --> B[BrokerBase.__init__ parses URL]
    B --> C[attributes: host, port, vhost, username, password]
    C --> D[Call subclass.queues(names) (async) — subclass must implement]
    D --> E[subclass may perform network I/O and return queue info]

(Note: BrokerBase.queues raises NotImplementedError and therefore must be overridden by subclasses.)

## Raises:
- __init__ does not explicitly raise exceptions in its body.
- Underlying library calls may raise exceptions that propagate:
  - Passing a non-string/non-bytes broker_url may raise TypeError from urllib.parse.urlparse.
  - Other exceptions may propagate from URL parsing utilities if inputs are malformed.
- queues (as implemented on BrokerBase) always raises NotImplementedError; subclasses must override it.

## Example:
Creation and use pattern (described in prose, no source code definitions):

1. Implement a concrete subclass that overrides the async `queues(names)` method to retrieve queue information from the specific broker.
2. Instantiate the concrete subclass with a broker URL string (for example a URL containing hostname, optional port, optional path as vhost, and optional credentials).
3. Read parsed attributes (host, port, vhost, username, password) directly on the instance if needed to configure a client.
4. Await the subclass's `queues(names)` coroutine to obtain queue information. Because BrokerBase itself raises NotImplementedError for `queues`, instantiation of BrokerBase without overriding `queues` will not provide queue functionality.
5. If the subclass opens resources (network clients, sockets), ensure the subclass provides a cleanup mechanism and that callers invoke it when finished.

Summary note:
BrokerBase is intentionally minimal: it provides predictable URL parsing and a single abstract async API entrypoint that concrete broker adapters implement.

### `flower.utils.broker.BrokerBase.__init__` · *method*

## Summary:
Parse the provided broker URL and initialize the instance connection attributes (host, port, vhost, username, password) on the object.

## Description:
This initializer converts a single broker URL string into discrete connection properties stored on the instance for later use by Broker implementations.
- Known callers: subclass constructors that call super().__init__(broker_url, *args, **kwargs), factory functions or configuration loaders that instantiate a Broker subclass, and any startup or reconfiguration code that creates a BrokerBase-derived instance.
- Lifecycle stage: invoked at object construction time to prepare normalized connection attributes before any network connection or authentication occurs.
- Rationale: centralizes URL parsing and percent-decoding so subclasses and connection code can rely on a consistent interpretation of host, port, virtual host, username, and password. It accepts additional positional and keyword arguments (ignored) to remain compatible with subclass constructors or factory call signatures.

## Args:
    broker_url (str | bytes):
        A broker URL acceptable to urllib.parse.urlparse. Typical forms include:
          - scheme://user:pass@host:port/vhost
          - host (host only)
          - host:port
        The username and password in the URL may be percent-encoded; they will be decoded when assigned.
    *_, **__ (additional positional and keyword arguments):
        Ignored. Present to maintain a permissive signature for subclasses or callers that pass extra parameters.

## Returns:
    None

## Raises:
    TypeError:
        If broker_url is not a str or bytes object, urllib.parse.urlparse is likely to raise a TypeError. This method does not explicitly raise other exceptions.

## Behavior and Edge Cases:
    - host:
        self.host is assigned purl.hostname (a str) or None if the URL contains no hostname.
    - port:
        self.port is assigned purl.port (an int) or None if no port is specified.
    - vhost:
        self.vhost is assigned purl.path[1:] — the URL path with the leading slash removed.
        * If path is empty ('') or '/', vhost becomes an empty string ''.
        * Deeper paths retain their slashes except for the leading one (e.g. "/a/b" -> "a/b").
    - username and password:
        username = purl.username; password = purl.password
        * If username or password is truthy (not None and not empty), it is passed through urllib.parse.unquote to percent-decode before assignment.
        * If username or password is falsy (None or empty string), the value is assigned as-is (None or '') without decoding.
        * Result types for self.username and self.password are either None or str.
    - No connection attempts, credential validation, logging, or I/O occur here — only parsing and normalization.

## State Changes:
    Attributes READ:
        - None of the object's existing self.<attr> fields are read. The method only reads the broker_url argument.
    Attributes WRITTEN:
        - self.host : str | None
        - self.port : int | None
        - self.vhost : str
        - self.username : str | None
        - self.password : str | None

## Constraints:
    Preconditions:
        - broker_url should be a parseable URL string or bytes. Passing invalid types (e.g., None, int) will raise TypeError from urlparse.
    Postconditions:
        - After execution, the instance has host, port, vhost, username, and password attributes set.
        - host and port may be None when absent from the URL.
        - vhost is always a str (possibly empty).
        - username and password are either None or str (percent-decoded if originally present and truthy).

## Side Effects:
    - No network I/O, file I/O, or external service calls.
    - Only mutates the instance by setting attributes listed above; no other global or external state is modified.
    - Uses urllib.parse.urlparse and urllib.parse.unquote which are pure library calls with no side effects.

### `flower.utils.broker.BrokerBase.queues` · *method*

## Summary:
An abstract asynchronous operation that, when implemented in a concrete broker subclass, enumerates broker queues filtered by the provided names and returns a sequence of queue descriptors. Calling the base implementation raises NotImplementedError.

## Description:
This method is the extension point for broker-specific logic that lists queues managed by the broker backend. The base class provides the async signature and enforces that subclasses implement the actual retrieval.

Known callers and lifecycle:
- No direct callers exist in the base class itself. Concrete broker implementations (subclasses) should implement this method and it will be called by higher-level components that need broker queue information such as monitoring/inspection routines, the web UI or CLI components that display broker queues, and any management/diagnostic tasks that enumerate queues.
- Typical invocation occurs during runtime when the system performs broker discovery, refreshes queue listings in a UI, or collects runtime metrics about queues.

Why this is its own method:
- Listing queues is broker-backend specific (AMQP, Redis, etc.). Keeping it as an abstract async method isolates backend differences, lets each subclass use its own protocol/clients, and allows asynchronous I/O patterns to be handled uniformly by callers.

## Args:
    names (iterable[str] or None):
        - A sequence (e.g., list, tuple) of queue names to filter by, or None to indicate "all queues".
        - The argument is required by the signature (no default provided in the base class).
        - Implementations should accept either a single iterable of strings or a None value. Implementations may also accept a single string as shorthand (optional, but if supported it must be documented by the subclass).

## Returns:
    Awaitable that resolves to a sequence representing the queues:
        - The base class does not mandate a concrete descriptor schema; the exact return structure is implementation-defined.
        - Recommended/common conventions for implementers:
            - Return an empty sequence (e.g., []) when no queues match the filter.
            - Prefer a sequence of simple values (list[str]) when only names are required, or a sequence of mapping/dict objects (list[dict]) when additional metadata (e.g., message count, consumers) is useful. If using dicts, include at least a "name" key.
        - Callers should accept an awaitable resolving to a sequence; they must be written to handle empty sequences.

## Raises:
    NotImplementedError:
        - Raised unconditionally by the base-class implementation to indicate that subclasses must override this method.
    Subclass-specific exceptions:
        - Concrete implementations may raise network, protocol, or client library exceptions (e.g., connection errors). These must be documented by each subclass; the base class does not raise them.

## State Changes:
    Attributes READ:
        - None in the base class implementation.
        - Implementations commonly read connection/configuration attributes initialized on the instance, for example:
            - self.host
            - self.port
            - self.vhost
            - self.username
            - self.password
        - These are only conventions; the base method itself does not access them.

    Attributes WRITTEN:
        - None in the base class implementation.
        - Implementations should avoid mutating BrokerBase fields as a side effect of a read/list operation unless explicitly documented.

## Constraints:
    Preconditions:
        - The BrokerBase instance must have been initialized (its __init__ completed) so that any connection/config attributes are set before subclass implementations attempt to use them.
        - For concrete implementations that open network connections, any required dependencies (client libraries) must be available and configured.

    Postconditions:
        - The returned awaitable resolves to a sequence (possibly empty) of queue descriptors.
        - The base-class method does not change instance state.

## Side Effects:
    - The base implementation has no side effects beyond raising NotImplementedError.
    - Concrete implementations will typically perform I/O (network calls) to the broker, so they may:
        - Open or reuse network connections to the broker backend.
        - Engage third-party client libraries and potentially raise their specific exceptions.
        - Perform short-lived authentication/handshake operations against the broker.
    - Implementers should document any additional side effects (caching, connection pooling, modifying instance attributes) in the subclass documentation.

## `flower.utils.broker.RabbitMQ` · *class*

*No documentation generated.*

### `flower.utils.broker.RabbitMQ.__init__` · *method*

## Summary:
Initializes RabbitMQ broker instance state from parsed broker_url and optional http_api; establishes the I/O loop and normalizes default connection fields (host, port, vhost, username, password, http_api) on the instance.

## Description:
This initializer is invoked when a RabbitMQ broker object is instantiated to prepare connection-related attributes and the tornado I/O loop before the broker is used for HTTP API calls or AMQP operations. Typical callers are any code that constructs a RabbitMQ broker object as part of broker configuration or startup; it runs during object construction (the class __init__ lifecycle step).

This logic is implemented as a separate initializer because it:
- depends on base-class initialization (super().__init__(broker_url)) to parse and populate raw broker URL fields,
- performs normalization and defaulting of multiple related attributes (host, port, vhost, username, password, http_api),
- must obtain/assign the process-wide I/O loop (ioloop.IOLoop.instance()) which is a distinct initialization concern,
- invokes validation on the computed http_api and logs failures without aborting construction.

Keeping these steps together in __init__ isolates startup and normalization responsibilities from later runtime methods.

## Args:
    broker_url (str):
        The broker URL passed through to the base initializer. The base initializer is expected to parse broker_url and populate instance fields used below (self.host, self.port, self.vhost, self.username, self.password).
    http_api (str or falsy):
        Optional explicit HTTP API base URL. If falsy (None, empty string, or other false-like value), a default HTTP API URL is constructed from username, password, host, port and vhost: "http://{username}:{password}@{host}:{port}/api/{vhost}".
    io_loop (tornado.ioloop.IOLoop or None, optional):
        Optional I/O loop instance to use. If None, the method sets self.io_loop to tornado.ioloop.IOLoop.instance().
    **__ (dict):
        Catch-all for additional keyword arguments; ignored by this initializer.

## Returns:
    None

## Raises:
    Any exception raised by the base initializer (super().__init__(broker_url)) will propagate.
    Any exception raised by tornado.ioloop.IOLoop.instance() will propagate.
    Any exception raised by urllib.parse.quote (e.g., TypeError if self.vhost is not a str-like object) will propagate.
    validate_http_api may raise ValueError, but ValueError from validate_http_api is caught and only logged; it is not re-raised by this initializer. Any other exception type raised by validate_http_api will propagate.

## State Changes:
Attributes READ:
    self.host
    self.port
    self.vhost
    self.username
    self.password

Attributes WRITTEN:
    self.io_loop        - set to provided io_loop or ioloop.IOLoop.instance()
    self.host           - left unchanged if truthy, otherwise set to 'localhost'
    self.port           - left unchanged if truthy, otherwise set to 15672
    self.vhost          - normalized via urllib.parse.quote or set to '/' as fallback
    self.username       - left unchanged if truthy, otherwise set to 'guest'
    self.password       - left unchanged if truthy, otherwise set to 'guest'
    self.http_api       - set to the validated or constructed http_api string

## Constraints:
Preconditions:
    - The base initializer (super().__init__(broker_url)) must have run and set the attributes read above (self.host, self.port, self.vhost, self.username, self.password). These attributes are expected to be string-like (for quote) or numeric where appropriate.
    - If self.vhost is to be quoted, it must be a type acceptable to urllib.parse.quote (typically str). Passing None for vhost may raise TypeError.
    - http_api, if provided, must be a string-like URL accepted by validate_http_api to be considered valid; if invalid, a ValueError will be caught and logged and the value will still be assigned.

Postconditions:
    - self.io_loop is set (either to the passed io_loop or to the global tornado ioloop instance).
    - self.host, self.port, self.vhost, self.username and self.password are guaranteed to be non-falsy defaults where falsy values were present:
        * host defaults to 'localhost'
        * port defaults to 15672
        * username defaults to 'guest'
        * password defaults to 'guest'
        * vhost is set to the quoted vhost value if non-empty or '/' if quoting yields empty and original vhost != '/' (and original '/' is preserved)
    - self.http_api is set to the provided http_api if truthy, otherwise to "http://{username}:{password}@{host}:{port}/api/{vhost}" (string interpolation with the normalized fields).
    - If validate_http_api(http_api) raises ValueError, the error is logged and self.http_api still receives the (possibly invalid) http_api string.

## Side Effects:
    - Calls tornado.ioloop.IOLoop.instance() when io_loop is not provided; this may initialize or fetch the global Tornado I/O loop singleton.
    - Calls urllib.parse.quote to URL-encode the vhost component.
    - Calls self.validate_http_api(http_api) to check the computed or provided http_api; a ValueError from that call is caught and logged via logger.error("Invalid broker api url: %s", http_api).
    - Emits a log entry (logger.error) if http_api validation fails.
    - No network I/O is performed directly in this initializer, but it prepares and validates a URL used later to make HTTP calls.

### `flower.utils.broker.RabbitMQ.queues` · *method*

## Summary:
Performs an asynchronous HTTP query to the RabbitMQ management API for queues in the broker vhost and returns the subset whose "name" matches any entry in the provided names collection; does not modify object state.

## Description:
This coroutine calls the RabbitMQ management HTTP API endpoint for queues in the configured vhost and filters the returned queue metadata to only those with names present in the supplied names iterable.

Known callers and context:
- Typically invoked from broker-management or monitoring code that needs to resolve or refresh metadata for a specific set of queues (e.g., when determining queue sizes, consumers, or to validate queue existence).
- Expected to be used during runtime status collection or administrative operations that run asynchronously (within an asyncio or Tornado ioloop context).

Why this is a separate method:
- Encapsulates the HTTP interaction, authentication extraction, error handling, and JSON parsing for the queues endpoint in one reusable asynchronous operation.
- Keeps network I/O and API-specific details out of higher-level logic so callers can request queue metadata with a simple async call and consistent error handling.

## Args:
    names (collections.abc.Iterable[str]): An iterable of queue name strings to filter for (membership-tested using "in"). Must be an iterable that supports membership checks (set/list/tuple). The function does not mutate this argument.

## Returns:
    list[dict]: A list of queue info dictionaries returned by the RabbitMQ management API whose 'name' field appears in the provided names iterable.
    - On success (HTTP 200): returns a list (possibly empty) of dict objects drawn from the API response.
    - On transient network/connection failure (socket.error or tornado.httpclient.HTTPError raised during fetch): returns an empty list as a safe fallback.
    - On non-200 HTTP responses: the underlying HTTP error is rethrown (see Raises).
    - Edge cases:
        * If the HTTP 200 response body is not valid JSON, json.JSONDecodeError is propagated.
        * If the JSON structure does not contain dicts with a 'name' key, a KeyError may be raised while filtering.

## Raises:
    tornado.httpclient.HTTPError: Re-raised by response.rethrow() when the HTTP response is not successful (response.code != 200). This happens when the request completed but the server returned an error status (4xx/5xx).
    json.JSONDecodeError: If the body of a successful (200) response cannot be parsed as JSON.
    KeyError: If the response JSON items do not include a 'name' key while filtering.
    socket.error: Could be raised by low-level socket operations (note: socket.error raised during fetch is caught and results in an empty list; socket errors outside the fetch call could still propagate).

## State Changes:
    Attributes READ:
        self.http_api - used to construct the management API URL and to extract credentials if present in the URL.
        self.vhost - appended to the API path to target the vhost's queues endpoint.
        self.username - used as fallback username when http_api URL does not contain credentials.
        self.password - used as fallback password when http_api URL does not contain credentials.

    Attributes WRITTEN:
        None - this method does not modify any self.<attr> attributes.

## Constraints:
    Preconditions:
        - self.http_api must be a valid URL string understood by urllib.parse.urlparse and urljoin.
        - self.vhost should be a string suitable to append to the 'queues/' path (expected to match RabbitMQ vhost formatting).
        - names must be an iterable of strings suitable for membership testing against queue 'name' values.
        - The caller must run this coroutine in an asyncio-compatible context (Tornado AsyncHTTPClient is used and the method is async).

    Postconditions:
        - On successful completion with HTTP 200, returns a list of dicts whose 'name' fields are in names.
        - No side-effect changes to self; http client is always closed before return/raise.

## Side Effects:
    - Network I/O: performs an HTTP GET to the RabbitMQ management API URL constructed from self.http_api and self.vhost.
    - Authentication: extracts credentials from the self.http_api URL (if present) and falls back to self.username/self.password for HTTP Basic auth.
    - Logging: on socket or HTTP fetch errors, logs an error message via the module logger (logger.error).
    - Resource management: constructs and closes a tornado.httpclient.AsyncHTTPClient instance (http_client.close()) in a finally block.

### `flower.utils.broker.RabbitMQ.validate_http_api` · *method*

## Summary:
Validate that the supplied HTTP API URL uses an allowed scheme ('http' or 'https'); on success the method returns None, on failure it raises ValueError. The method is a classmethod and does not modify object state.

## Description:
Known callers:
- RabbitMQ.__init__: invoked during RabbitMQ instance construction to validate a provided or constructed http_api before assignment to self.http_api.

Lifecycle/context:
- Runs during broker initialization to enforce that the RabbitMQ management API endpoint uses an HTTP(S) scheme.

Why this is a separate method:
- Encapsulates a single validation rule (allowed URL schemes) so it can be reused, tested, or overridden by subclasses.
- Implemented as a classmethod so callers can validate URLs without an instance and before full initialization completes.

Method type:
- classmethod (signature: cls, http_api)

## Args:
    cls (type): The class object (present because this is a classmethod). Not inspected by this implementation.
    http_api (str | bytes | os.PathLike): The URL to validate. Must be parseable by urllib.parse.urlparse (commonly a str).

Allowed values:
- The URL's scheme component, as returned by urllib.parse.urlparse(http_api).scheme, must be exactly 'http' or 'https'.

## Returns:
    None

Behavior notes:
- The method does not return any value on success (implicit None).

## Raises:
    ValueError:
        - Condition: The parsed URL's scheme is not 'http' or 'https'.
        - Raised with message: "Invalid http api schema: {scheme}" where {scheme} is the value of urlparse(http_api).scheme.
    TypeError (propagated):
        - Condition: If http_api is of a type that urllib.parse.urlparse does not accept (for example None), urlparse may raise TypeError; this method does not catch it.

## State Changes:
Attributes READ:
    - None (the implementation does not access instance or class attributes)

Attributes WRITTEN:
    - None (no mutations to self, cls, or external state)

## Constraints:
Preconditions:
    - http_api must be a value accepted by urllib.parse.urlparse (typically a str).
    - Callers expecting no exception must ensure http_api includes a scheme and that it is 'http' or 'https'.

Postconditions:
    - If the method returns normally, urlparse(http_api).scheme is either 'http' or 'https'.
    - No state on the class or instance is modified.

## Side Effects:
    - None. The method only calls urllib.parse.urlparse and performs an in-memory check; it performs no I/O, logging, or network access.

## `flower.utils.broker.RedisBase` · *class*

## Summary:
Represents a Redis-backed broker adapter base that standardizes priority-aware Redis queue naming and provides an async method to inspect queue message counts. It holds configuration (priority steps, separator, key prefix) and a placeholder for a Redis client instance.

## Description:
RedisBase is a concrete adapter base built on top of BrokerBase's URL parsing responsibilities. It does not open Redis connections itself; instead, it expects callers (or subclasses/factories) to assign an initialized Redis client to the instance's redis attribute before performing Redis I/O. Use cases include implementing monitoring/inspection endpoints or lightweight broker adapters that need to compute prioritized Redis queue keys and obtain message counts across priority sub-queues.

Typical instantiation scenarios:
- A monitoring tool creates a RedisBase, assigns a redis client (for example redis.StrictRedis or redis.Redis), then awaits queues(names) to collect per-queue message counts.
- A subclass may extend RedisBase to add connection management (connect/close) and reuse _q_for_pri and queues implementations.

Motivation and responsibility boundary:
- Purpose: centralize naming convention for priority-specific Redis queue keys and provide a simple, async method to return per-logical-queue message counts aggregated across all configured priority queues.
- Boundary: RedisBase does not manage or open network resources; it only holds configuration and performs read-only Redis calls when self.redis is set. Connection lifecycle (creation, authentication, retries, cleanup) is the caller's or subclass's responsibility.

## State:
Instance attributes (created/used by RedisBase)

- redis (Any | None)
  - Type: expected to be a Redis client object exposing an llen(key) method (callable).
  - Initial value: None (set in __init__).
  - Constraint: Must be set to a functional Redis client before invoking methods that perform I/O (e.g., queues). If left as None, calls to queues will raise AttributeError.

- priority_steps (list)
  - Type: iterable (typically list) of priority identifiers (commonly ints).
  - Default: DEFAULT_PRIORITY_STEPS, i.e., [0, 3, 6, 9].
  - Source: broker_options.get('priority_steps', DEFAULT_PRIORITY_STEPS) from __init__ kwargs.
  - Invariant: membership testing (pri in self.priority_steps) must be valid; callers rely on this for _q_for_pri validation.

- sep (str)
  - Type: str
  - Default: DEFAULT_SEP which is the two-byte string '\x06\x16'.
  - Source: broker_options.get('sep', DEFAULT_SEP).
  - Use: inserted between base queue name and priority when composing prioritized queue key names.

- broker_prefix (str)
  - Type: str
  - Default: '' (empty string)
  - Source: broker_options.get('global_keyprefix', '').
  - Use: prepended to the generated Redis key for each queue.

Class-level constants:
- DEFAULT_SEP (str): default separator between queue and priority ('\x06\x16').
- DEFAULT_PRIORITY_STEPS (list): default priority steps [0, 3, 6, 9].

Inherited state:
- RedisBase inherits BrokerBase attributes (host, port, vhost, username, password) populated by BrokerBase.__init__ and available immediately after construction.

Class invariants:
- After __init__, redis attribute exists (initialized to None), priority_steps is defined, sep is defined, and broker_prefix is defined.
- _q_for_pri must only be called with priorities that are members of priority_steps; otherwise it raises ValueError.

## Lifecycle:
Creation:
- Required argument: broker_url (string). Call signature: RedisBase(broker_url, *_, **kwargs).
- Optional configuration: pass broker_options as a key in kwargs. Example options:
  - 'priority_steps': iterable of priorities (overrides DEFAULT_PRIORITY_STEPS)
  - 'sep': separator string (overrides DEFAULT_SEP)
  - 'global_keyprefix': string to prefix all generated Redis keys
- After construction, the instance's redis attribute is None; callers must assign a Redis client before calling queues.

Usage sequence:
1. Instantiate: r = RedisBase('redis://host:port/db', broker_options={...})
   - BrokerBase.__init__ (super) parses broker_url and sets host/port/vhost/username/password.
   - RedisBase.__init__ sets redis=None and applies broker_options.
2. Initialize Redis client separately (example: client = redis.Redis(host=..., port=..., db=...)) and assign: r.redis = client
3. Use r._q_for_pri(queue, pri) to compute a priority-specific queue key when needed (validation occurs).
4. Await r.queues(names) to retrieve per-logical-queue statistics; this performs len(self.priority_steps) calls to self.redis.llen per queue name.

Destruction / cleanup:
- RedisBase itself performs no cleanup. If a Redis client was created and assigned by the caller, the caller is responsible for closing it (client.close() or similar) if the client API supports that. Subclasses that create and assign their own clients should implement and expose cleanup/close methods or context manager protocols.

## Method Map:
flowchart LR
    A[__init__(broker_url, broker_options)] --> B[sets: redis=None, priority_steps, sep, broker_prefix]
    B --> C[_q_for_pri(queue, pri) : validate priority -> compose key]
    B --> D[queues(names) : for each name -> for each pri in priority_steps -> call _q_for_pri -> call self.redis.llen(key) -> sum -> return list of dicts]

Notes:
- queues depends on _q_for_pri and on a correctly-initialized self.redis exposing llen.
- _q_for_pri performs membership validation against priority_steps before composing the queue name.

## Raises:
Exceptions explicitly possible from RedisBase methods and __init__:

- ImportError
  - Trigger: Raised in __init__ when the module-level symbol redis is falsy. This indicates that the redis library was not available at module-import time and RedisBase cannot operate.

- ValueError (from _q_for_pri)
  - Trigger: When pri is not a member of self.priority_steps.
  - Note: _q_for_pri checks membership first; a falsy pri (e.g., 0, None, '') that is present in priority_steps will pass membership test but, if falsy, will not be appended to the queue name (see edge case below).

- AttributeError
  - Trigger: If queues is called when self.redis is None or when self.redis does not expose an llen attribute; accessing self.redis.llen will raise AttributeError.

- TypeError
  - Trigger: If queues is called with a non-iterable names argument; iteration will raise TypeError.

- redis.exceptions.RedisError (or other client-specific exceptions)
  - Trigger: Any network/IO error raised by the underlying redis client when calling llen(key). These are propagated to the caller.

Edge conditions:
- Using numeric priority 0: because Python treats 0 as falsy, _q_for_pri will return the base queue name without separator even if 0 exists in priority_steps. This behavior is deliberate in the implementation and callers should account for it. If callers expect the textual '0' suffix to be appended, they must avoid relying on falsy semantics or choose different priority identifiers.

## Example:
(Async usage pattern — assume an appropriate redis client class is available and assigned)

1) Create and configure RedisBase
   r = RedisBase('redis://localhost:6379/0', broker_options={
       'priority_steps': [0, 3, 6, 9],
       'sep': '\x06\x16',
       'global_keyprefix': 'myapp:'
   })

2) Assign an initialized Redis client to the instance
   r.redis = redis.Redis(host='localhost', port=6379, db=0)

3) Inspect queues (example executed inside an async function or event loop)
   stats = await r.queues(['default', 'emails'])
   # stats -> [{'name': 'default', 'messages': 42}, {'name': 'emails', 'messages': 7}]

4) Cleanup
   # If the client supports close or connection cleanup, perform it here:
   # r.redis.close()  (caller/subclass responsibility)

### `flower.utils.broker.RedisBase.__init__` · *method*

## Summary:
Initializes a Redis-backed broker instance: delegates URL parsing to the BrokerBase initializer, verifies the redis dependency is available, and configures Redis-specific options (priority_steps, separator, and global key prefix) while preparing the instance for later connection setup by initializing self.redis to None.

## Description:
This constructor runs when a RedisBase object is created (typically during application startup or when a broker factory constructs a Redis broker). It performs three focused responsibilities:
- Delegation: calls BrokerBase.__init__(broker_url) to parse and set common broker attributes (host, port, vhost, username, password).
- Dependency check: ensures the module-level name `redis` is truthy and raises ImportError otherwise.
- Configuration: reads Redis-specific settings from kwargs['broker_options'] and assigns instance defaults for priority handling and queue key formatting.

Known callers / lifecycle context:
- No explicit instantiation sites were discovered in the local scan. In normal operation, this initializer is invoked once per Redis broker instance at bootstrap time (for example, when an application or broker factory chooses the Redis backend and constructs RedisBase or a subclass).
- After construction, other methods on the instance (for example, methods that create or use a redis client) will typically replace self.redis with an actual redis client/connection.

Why this logic is separated:
- Keeps URL parsing and generic broker initialization in BrokerBase while isolating Redis-specific dependency checks and configuration here. This separation allows other broker backends to reuse BrokerBase without Redis-specific concerns.

## Args:
    broker_url (str):
        Connection URL accepted by urllib.parse.urlparse. Example: redis://user:pass@host:port/vhost.
        BrokerBase.__init__ will parse this and populate self.host, self.port, self.vhost, self.username, and self.password.
    *_, **kwargs:
        Additional positional/keyword arguments. Only broker_options is interpreted:
        broker_options (dict, optional): Redis-specific configuration dictionary. Recognized keys:
            - 'priority_steps' (list[int] or list[numbers.Number], optional):
                Sequence of priority values used to derive priority queue names. If the key is absent, DEFAULT_PRIORITY_STEPS is used. Note: if the key exists but its value is None, None will be assigned (no fallback occurs).
            - 'sep' (str, optional):
                Separator string used to join queue name and priority when building priority queue keys. If the key is absent, DEFAULT_SEP is used. If provided but None, None will be assigned.
            - 'global_keyprefix' (str, optional):
                String to prefix all generated queue keys. If absent, defaults to the empty string ''. If provided but None, None will be assigned.

## Returns:
    None

## Raises:
    ImportError:
        Raised if the module-level name `redis` evaluates to falsy at runtime (code path: `if not redis: raise ImportError('redis library is required')`). Note: in normal circumstances an unsuccessful import of the redis package would already have raised ImportError at module import time; this check guards against the unlikely case that `redis` is present but falsy (or has been tampered with).

## State Changes:
Attributes READ:
    - module-level name `redis`: checked for truthiness.
    - kwargs and the dictionary broker_options: read to obtain configuration values.
    - class attributes self.DEFAULT_PRIORITY_STEPS and self.DEFAULT_SEP: read as fallback defaults when broker_options lacks the corresponding keys.

Attributes WRITTEN:
    - self.redis: assigned None (placeholder for a future redis client/connection).
    - self.priority_steps: assigned to broker_options.get('priority_steps', DEFAULT_PRIORITY_STEPS) — may be a list of numbers, or any value supplied (including None).
    - self.sep: assigned to broker_options.get('sep', DEFAULT_SEP) — may be a string or any provided value.
    - self.broker_prefix: assigned to broker_options.get('global_keyprefix', '') — defaults to '' if key missing.
    - plus attributes initialized by BrokerBase.__init__ (via super().__init__):
        - self.host (str or None)
        - self.port (int or None)
        - self.vhost (str; BrokerBase uses the URL path with the leading '/' removed)
        - self.username (str or None)
        - self.password (str or None)

## Constraints:
Preconditions:
    - The broker_url should be a string acceptable to urllib.parse.urlparse so that BrokerBase.__init__ can extract host/port/path/username/password. If broker_url is malformed, the parsed attributes may be None or empty strings.
    - The redis Python package should be importable at module import time. The runtime check here only tests truthiness of the module-level name `redis` and will raise ImportError if it is falsy.

Postconditions:
    - After successful construction:
        - self.redis is set to None.
        - self.priority_steps is set to the value returned by broker_options.get('priority_steps', DEFAULT_PRIORITY_STEPS). This value is not validated here — it may be a list of numbers (the expected shape) or any other value if provided.
        - self.sep is set to broker_options.get('sep', DEFAULT_SEP).
        - self.broker_prefix is set to broker_options.get('global_keyprefix', '').
        - BrokerBase-provided attributes (host, port, vhost, username, password) reflect the parsed broker_url.

## Side Effects:
    - Calls BrokerBase.__init__(broker_url), which uses urllib.parse.urlparse to parse broker_url and assigns parsed values to self; this is CPU-only parsing (no network I/O).
    - Does not establish any network connections or open files itself.
    - Raises ImportError early if the redis dependency check fails, preventing instance creation.

## Edge cases and implementation notes:
    - If broker_options explicitly contains keys with value None (for example, 'priority_steps': None), those None values are assigned to the corresponding instance attributes; there is no further validation or fallback. Downstream code that expects a list for priority_steps may fail; consider validating and normalizing broker_options before assignment if stricter behavior is required.
    - DEFAULT_PRIORITY_STEPS (class attribute) is expected to be an iterable of priority values (see class-level constants). DEFAULT_SEP is expected to be a string. These defaults are used only when broker_options omits the corresponding keys.
    - The initializer intentionally sets self.redis to None so that client/connection creation can be deferred or handled by other methods; do not assume a live connection exists immediately after construction.
    - For robust implementations, add explicit type checks for priority_steps (ensure it's an iterable of numbers) and for sep and broker_prefix (ensure str), and raise TypeError or ValueError with clear messages when invalid values are provided.

### `flower.utils.broker.RedisBase._q_for_pri` · *method*

## Summary:
Returns the queue name string used for prioritized queues by appending the priority suffix when a truthy priority is requested; does not modify object state.

## Description:
This method centralizes the naming convention for prioritized queue identifiers. It validates that the requested priority exists in the broker's configured priority steps and then composes the queue name either as the base queue alone (when the priority value is falsy) or as base + separator + priority.

Known callers and invocation context:
- No direct callers are visible in the provided snippet. Conceptually, this method is intended to be called by broker implementation methods that construct queue names for enqueueing, dequeueing, inspection, or monitoring operations when priority-specific queues are used.
- Typical lifecycle stage: called whenever a queue name must be computed from a logical queue identifier and a priority level (e.g., just before pushing a task to Redis or when forming the Redis key to read from).

Rationale for being a separate method:
- Naming logic and the membership validation for priorities are centralized so all broker operations use a single consistent naming scheme and guardrail (the membership check), avoiding duplication across enqueue/dequeue codepaths.

## Args:
    queue (str): Base queue identifier (expected to be a string used as the queue/key name).
    pri (hashable): A priority value that must be a member of self.priority_steps. Allowed values are the elements of self.priority_steps (their concrete types are defined elsewhere in the broker); common types include strings or integers. The method treats falsy values (e.g., None, '', 0) specially: membership is checked first, but a falsy pri will not be appended to the queue name (see edge case).

## Returns:
    str: The composed queue name. Possible forms:
        - If pri is falsy (e.g., None, '', 0): returns exactly queue (no separator or priority appended).
        - If pri is truthy and is a member of self.priority_steps: returns queue + self.sep + str(pri).
    Edge cases:
        - If pri is 0 and 0 is present in self.priority_steps, membership check passes but 0 is falsy; the method will return the base queue without appending the separator or "0". The caller should be aware of this semantics if numeric priority values like 0 are used.

## Raises:
    ValueError: Raised when pri is not found in self.priority_steps (checked with the membership operator `pri not in self.priority_steps`). The exception is raised unconditionally before any string composition.

## State Changes:
    Attributes READ:
        - self.priority_steps: read to validate that pri is a supported priority.
        - self.sep: read to determine the string inserted between queue and pri when pri is appended.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.priority_steps must be an iterable supporting membership testing (e.g., list, tuple, set).
        - self.sep must be defined (string-like) on the instance.
        - queue should be an appropriate string or object suitable for formatting into the final queue name; it will be coerced to a string by str.format.
    Postconditions:
        - If the method returns normally, the returned value is a string representing the queue name. No instance attributes are changed.
        - If pri is not a member of self.priority_steps, a ValueError is raised and no value is returned.

## Side Effects:
    - No I/O operations or external service calls are performed.
    - No mutations of objects outside self are made.
    - Uses Python string formatting and membership testing only.

### `flower.utils.broker.RedisBase.queues` · *method*

## Summary:
Return per-queue statistics (name and total number of messages across all priority sub-queues) without mutating the object.

## Description:
This asynchronous method iterates the provided queue names and, for each queue, constructs the set of priority-specific Redis keys (by combining broker_prefix and the queue name transformed by the priority naming scheme). It queries Redis for the length of each corresponding list key and sums those lengths to produce a total message count for that queue. The method returns a list of dictionaries describing each queue and its total message count.

Known callers and context:
- Intended to be called by components that collect broker/queue statistics for monitoring, APIs, or UI endpoints (for example, web handlers or CLI status commands that present queue sizes).
- Typically invoked during monitoring/inspection phases (not in the hot path of task production/consumption) to obtain snapshot counts for display or diagnostics.

Why this logic is a separate method:
- Centralizes the mapping from a logical queue name to its priority-specific Redis keys and the aggregation logic for message counts.
- Keeps code that requests queue metrics concise and avoids duplicating Redis key naming and aggregation logic across the codebase.
- Encapsulates Redis read behavior and related error conditions in one place.

## Args:
    names (iterable[str]): An iterable of logical queue names (strings). Each name will be used to build priority-specific Redis keys. The method expects that iterating `names` yields hashable, str-like values suitable for formatting into Redis keys.

## Returns:
    list[dict]: A list where each item is a dictionary with two keys:
        - 'name' (str): the original logical queue name as provided in `names`.
        - 'messages' (int): total number of messages across all priority-specific Redis list keys for that queue (sum of redis.llen for each prioritized key). For an empty `names`, returns an empty list. The integer is non-negative (>= 0).

## Raises:
    TypeError: If `names` is not iterable (raised by Python when attempting to iterate).
    AttributeError: If self.redis is None or does not provide an `llen` attribute (occurs when the Redis client has not been initialized or is the wrong type).
    redis.exceptions.RedisError (or other exceptions raised by the redis client): If any call to self.redis.llen(...) fails (e.g., network/connection error, server-side error).
    ValueError: If the implementation of _q_for_pri raises ValueError due to an invalid priority value. (This is unlikely here since priorities are taken from self.priority_steps.)

## State Changes:
Attributes READ:
    - self.broker_prefix (str): used as a prefix to each generated Redis key.
    - self.priority_steps (list[int] or sequence): iterated to generate priority-specific keys.
    - self.sep (str): indirectly read by _q_for_pri when composing priority keys.
    - self.redis (redis client): used to call llen on keys.

Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.redis must be an initialized Redis client/object exposing a callable `llen(key)` method that returns an integer count of list elements.
    - self.priority_steps must be an iterable of priority identifiers (typically integers) expected by _q_for_pri.
    - Each item yielded by `names` must be a string-like queue identifier acceptable to _q_for_pri and safe to format into a Redis key.

Postconditions:
    - The returned list has exactly one entry per item iterated from `names`, preserving the order of iteration.
    - For each returned entry, 'name' equals the corresponding input name, and 'messages' is an integer >= 0 reflecting the sum of lengths from Redis for all priorities in self.priority_steps.
    - No attributes on self are changed.

## Side Effects:
    - Performs network I/O: executes one redis.llen call per priority step per queue name (i.e., len(self.priority_steps) calls per queue).
    - May raise or propagate exceptions from the Redis client (connection errors, timeouts, server errors).
    - No other external mutations are performed (no writes to Redis, no file or stdout I/O).

## `flower.utils.broker.Redis` · *class*

## Summary:
Represents a concrete Redis-backed broker adapter that parses broker URL settings (host, port, virtual DB, credentials) and constructs a redis.Redis client instance attached to the instance as the `redis` attribute.

## Description:
This class is a thin subclass of RedisBase that completes connection-configuration duties: it ensures sensible defaults for host and port, normalizes the virtual-host (database) identifier into an integer, and instantiates a redis.Redis client using those resolved settings.

When to instantiate:
- When you need a Redis-backed broker adapter that automatically constructs and stores a redis.Redis client with connection parameters derived from a broker URL.
- Typical callers: factories or higher-level broker adapters that parse a broker URL and then require a ready-to-use redis client bound to the broker adapter instance.

Responsibility boundary:
- This class is responsible only for resolving connection parameters and creating a redis.Redis instance (assigning it to self.redis).
- It delegates naming, priority handling, and queue inspection behavior to RedisBase (inherited).
- It does not implement advanced connection lifecycle management (retries, pooling, explicit close). Any additional lifecycle actions should be implemented by callers or subclasses.

## State:
Instance attributes (after __init__ completes):

- host (str)
  - Type: str
  - Derived from: value set by RedisBase (inherited) or defaulted here
  - Default if falsy after super().__init__: 'localhost'
  - Invariant: non-empty string suitable for redis.Redis host parameter

- port (int)
  - Type: int (or value acceptable to redis.Redis as port)
  - Derived from: value set by RedisBase or defaulted here
  - Default if falsy after super().__init__: 6379
  - Invariant: numeric port value passed to redis.Redis

- vhost (int)
  - Type: int
  - Derived from: self._prepare_virtual_host(self.vhost) — see _prepare_virtual_host behavior
  - Valid values: integer >= 0 within the Redis server's database range (implementation only ensures integer conversion; server limits are not enforced here)
  - Invariant: always an int after __init__ returns

- username (str | None)
  - Type: optional str
  - Derived from: inherited BrokerBase attribute (left unchanged by this class)
  - Use: passed to redis.Redis as username

- password (str | None)
  - Type: optional str
  - Derived from: inherited BrokerBase attribute
  - Use: passed to redis.Redis as password

- redis (redis.Redis)
  - Type: instance of redis.Redis (from the redis package)
  - Set during __init__ by calling self._get_redis_client()
  - Invariant: after __init__, self.redis is assigned the object returned by redis.Redis(**args)
  - Note: the underlying redis.Redis client behavior (lazy connection vs immediate network I/O) depends on redis-py; this class only constructs the client.

## Lifecycle:
Creation:
- Constructor signature: Redis(broker_url, *args, **kwargs)
- Required argument:
  - broker_url (str): passed to RedisBase.__init__ which parses host/port/vhost/credentials.
- Optional passthroughs:
  - Additional args/kwargs accepted by RedisBase.__init__ and consumed there (e.g., broker_options).
- Steps performed during construction:
  1. Calls super().__init__(broker_url, *args, **kwargs) to let BrokerBase/RedisBase parse and populate host, port, vhost, username, password, and RedisBase configuration fields.
  2. Ensures host has a usable default: self.host = self.host or 'localhost'.
  3. Ensures port has a usable default: self.port = self.port or 6379.
  4. Normalizes vhost to an integer via self._prepare_virtual_host(self.vhost).
  5. Builds connection arguments via self._get_redis_client_args() and creates a redis.Redis client via self._get_redis_client(), assigning it to self.redis.

Usage:
- Typical sequence:
  1. Instantiate: r = Redis('redis://host:port/db', ...)
  2. Use inherited methods (from RedisBase) such as queue name helpers and queues inspection which call self.redis.llen(...) as needed.
- There is no requirement to reassign self.redis after __init__; it is created automatically. However callers may replace it with a different client instance if desired.

Destruction / cleanup:
- This class does not provide explicit cleanup or close() semantics.
- If the created redis.Redis client requires explicit closure or resource cleanup, the caller or a subclass must perform that (e.g., call client.close() or similar if supported).
- Subclasses should override or extend to provide deterministic cleanup if needed.

## Methods and behavior details:

_prepare_virtual_host(vhost)
- Purpose: normalize the broker-supplied virtual-host (database) identifier into an integer suitable for redis.Redis `db` argument.
- Accepted input forms:
  - integers (instances of numbers.Integral) — returned unchanged.
  - falsy values: None, '' (empty string), '/' — treated as database 0.
  - strings with a leading slash: '/N' where N is a decimal integer (e.g., '/0', '/2') — leading '/' stripped then converted.
  - decimal numeric strings: 'N' (e.g., '0', '3') — converted to int.
- Behavior:
  - If input is an Integral, it is returned unchanged.
  - If input is falsy or equal to '/', it becomes 0.
  - If input is a string starting with '/', the leading '/' is removed before conversion.
  - Attempts int(vhost) conversion for non-Integral inputs.
- Errors:
  - If conversion to int fails (for example, non-numeric strings like 'db1'), _prepare_virtual_host raises ValueError with the message "Database is int between 0 and limit - 1, not {vhost}" and chains the original exception.
- Return: integer vhost

_get_redis_client_args()
- Purpose: compose a mapping of keyword arguments to pass to redis.Redis.
- Returns dict with keys: 'host', 'port', 'db', 'username', 'password'
  - 'host': self.host
  - 'port': self.port
  - 'db': self.vhost
  - 'username': self.username
  - 'password': self.password

_get_redis_client()
- Purpose: instantiate the redis.Redis client using the args returned by _get_redis_client_args.
- Behavior: returns redis.Redis(**self._get_redis_client_args())
- Side effects: none inside this class except the object allocation and any behavior performed by redis.Redis constructor (which may raise exceptions on invalid parameters).

## Method Map:
flowchart LR
    A[__init__(broker_url,...)] --> B[super().__init__ -> set inherited host/port/vhost/username/password]
    B --> C[self.host = self.host or 'localhost']
    C --> D[self.port = self.port or 6379]
    D --> E[self.vhost = _prepare_virtual_host(self.vhost)]
    E --> F[_get_redis_client_args() -> dict(host,port,db,username,password)]
    F --> G[_get_redis_client() -> redis.Redis(**args)]
    G --> H[self.redis = redis.Redis instance]

## Raises:
- ValueError
  - Trigger: _prepare_virtual_host raises ValueError when a provided vhost string cannot be converted to int (e.g., non-numeric strings); the message is: "Database is int between 0 and limit - 1, not {vhost}" with the original exception chained.
- Any exception raised by redis.Redis constructor
  - Trigger: invalid argument types or errors raised by redis-py when calling redis.Redis(**args). Common examples depend on the redis library (TypeError, redis.exceptions.RedisError); these are not swallowed and propagate to the caller.
- Note on import errors:
  - This class depends on the `redis` package being importable (module-level import). If the redis module is not available, the module import would fail earlier; instantiation assumes `redis` is present.

## Example:
- Create an instance using a broker URL with an integer database:
  - r = Redis('redis://example.com:6379/2')
  - After construction:
    - r.host -> resolved hostname or 'localhost' if missing
    - r.port -> resolved port or 6379 if missing
    - r.vhost -> 2 (int)
    - r.redis -> instance of redis.Redis constructed with host, port, db=2

- Handling common vhost forms:
  - Input vhost None, '', or '/' -> r.vhost == 0
  - Input vhost '/0' or '0' -> r.vhost == 0
  - Input vhost '3' -> r.vhost == 3
  - Invalid input 'db1' -> ValueError during initialization

- Typical usage pattern:
  1. r = Redis('redis://localhost:6379/0')
  2. Use inherited queue inspection methods (which will call r.redis.llen(key))
  3. If the redis client requires explicit close, caller should perform cleanup when finished.

### `flower.utils.broker.Redis.__init__` · *method*

## Summary:
Initializes the Redis broker instance by delegating broker_url parsing to the superclass, applying sensible defaults for host and port, normalizing the virtual host to an integer, and creating a redis.Redis client stored on the instance.

## Description:
This constructor is invoked when a Redis broker object is instantiated (i.e., as part of creating the broker backend during application startup or when a broker is created dynamically). It forwards broker_url (and any extra args/kwargs) to the superclass initializer which is responsible for parsing the broker_url and populating initial connection attributes. After that, this method:

- Ensures self.host and self.port have usable defaults ('localhost' and 6379) if they are falsy after the superclass initializer.
- Normalizes the virtual host (self.vhost) into an integer via self._prepare_virtual_host(...).
- Constructs a redis.Redis client using the resolved connection parameters via self._get_redis_client() and assigns it to self.redis.

This logic is kept in __init__ (rather than inlined elsewhere) because it performs instance-level initialization that depends on values populated by the superclass initializer and because creating the redis client is an explicit initialization step for the Redis broker backend.

Known callers / lifecycle stage:
- Any code that instantiates flower.utils.broker.Redis (i.e., Redis(broker_url, ...)). Typical usage is during broker backend setup when the application or library builds a broker object from a broker URL.

## Args:
    broker_url (Any): The broker connection URL or identifier passed through to the superclass initializer. The exact accepted format and parsing behavior are handled by the superclass __init__ and are not revalidated here.
    *args: Additional positional arguments forwarded to super().__init__.
    **kwargs: Additional keyword arguments forwarded to super().__init__.

## Returns:
    None: As an initializer, this method does not return a value. It constructs and stores state on self.

## Raises:
    ValueError: Propagated if self._prepare_virtual_host(self.vhost) fails to convert the virtual host into an integer. The helper raises:
        ValueError(f'Database is int between 0 and limit - 1, not {vhost}')
    (No other exceptions are explicitly raised by this code path; exceptions from redis.Redis(...) constructor would propagate if they occur, but construction of the client object itself typically does not perform network I/O.)

## State Changes:
Attributes READ:
    self.host
    self.port
    self.vhost
    self.username  (read indirectly by _get_redis_client/_get_redis_client_args)
    self.password  (read indirectly by _get_redis_client/_get_redis_client_args)

Attributes WRITTEN:
    self.host       - set to previous value or 'localhost' when falsy
    self.port       - set to previous value or 6379 when falsy
    self.vhost      - replaced by the integer-normalized result of _prepare_virtual_host(...)
    self.redis      - assigned the redis.Redis client instance returned by _get_redis_client()

## Constraints:
Preconditions:
    - superclass __init__ must accept (broker_url, *args, **kwargs) and is expected to initialize or leave in-place attributes referenced here (at least: host, port, vhost, username, password). This __init__ forwards broker_url to the superclass and depends on that parsing.
    - caller should provide a broker_url acceptable to the superclass initializer.

Postconditions:
    - After completion, self.host is truthy (original value or 'localhost'), self.port is truthy (original value or 6379).
    - self.vhost is an integer (result of _prepare_virtual_host).
    - self.redis is a redis.Redis instance configured with connection arguments returned by _get_redis_client_args().

## Side Effects:
    - Calls self._prepare_virtual_host(self.vhost) which may raise ValueError if vhost cannot be coerced to int.
    - Calls self._get_redis_client(), which instantiates and returns a redis.Redis client (creating an object from the redis package). Instantiating the redis.Redis client configures a client object but does not perform network calls at construction time.

### `flower.utils.broker.Redis._prepare_virtual_host` · *method*

## Summary:
Normalize and validate a Redis "virtual host" representation into a canonical integer database index and return that integer; does not modify object state.

## Description:
Converts common virtual-host inputs into an integer database index used for Redis connections. It accepts integers (returned unchanged) and several string forms (empty, "/", "/N", "N") which are converted to an int. The method centralizes parsing logic so connection/initialization code obtains a consistent numeric database index.

Known callers and lifecycle:
    - Intended to be used by Redis broker or connection setup routines during client/config parsing before establishing a connection to Redis. It is invoked in the initialization or connection-configuration stage when a virtual host (database) identifier supplied by configuration or URL needs normalization.

Why this is a separate method:
    - Parsing rules (treating empty or "/" as database 0, stripping a leading slash, validating numeric conversion) are encapsulated to avoid duplicating behavior across callers and to provide a single place to control error messaging.

## Args:
    self (Redis): Instance of the Redis broker/class (not accessed by this method).
    vhost (int | str | any): Virtual-host identifier to normalize.
        - If an instance of numbers.Integral (including bool), it is returned unchanged.
        - Common accepted string forms:
            - '' or None or '/' -> treated as database 0 (only when vhost is not an Integral)
            - '/N' or 'N' where N is an ASCII base-10 integer -> parsed to int(N)
        - Other values: the method attempts to treat vhost like a string by calling startswith('/') and then int() on the result; behavior follows Python's built-in int() rules.

## Returns:
    int | numbers.Integral-subclass: The normalized database index.
        - If vhost is already an Integral, that exact value is returned (note: bool is an Integral subclass, so True/False are returned unchanged).
        - If a convertible string is provided, returns int(parsed_value).
        - If a non-Integral falsy value (e.g., None or '') or literal '/' is provided, returns 0.

## Raises:
    ValueError:
        - Raised when vhost is not an Integral and cannot be converted to int after optional leading '/' removal.
        - The raised ValueError message is exactly: "Database is int between 0 and limit - 1, not {vhost}" where {vhost} is the original value passed (stringified by the f-string).
    AttributeError:
        - May be raised if vhost is a truthy, non-Integral object that does not implement startswith (for example, a list or custom object without startswith), since the method calls vhost.startswith('/').
    TypeError:
        - May be raised when vhost is a bytes or bytearray object: calling vhost.startswith('/') will raise TypeError because the code passes a str argument ('/') to startswith on a bytes-like object. Other TypeErrors may propagate from int() when passed incompatible types.

## State Changes:
    Attributes READ:
        - None. The method does not access any attributes on self.
    Attributes WRITTEN:
        - None. The method does not mutate self or any external state.

## Constraints:
    Preconditions:
        - No strict preconditions enforced by this method. Callers should preferably pass an integer or a string-like vhost.
        - Be aware that bool is treated as an Integral and will be returned unchanged (so passing False returns False, not necessarily the int 0).

    Postconditions:
        - On successful return, the result is an int (or an Integral-subclass value returned unchanged).
        - No side effects on the object or external systems.

## Side Effects:
    - None. The function performs in-memory computation only; it does not perform I/O or external service calls.

## Examples:
    - vhost = 3          -> returns 3
    - vhost = "3"        -> returns 3
    - vhost = "/3"       -> returns 3
    - vhost = ""         -> returns 0
    - vhost = "/"        -> returns 0
    - vhost = None       -> returns 0
    - vhost = False      -> returned unchanged (False) because bool is an Integral subclass

Notes:
    - Because the method relies on startswith('/') and int(), behavior for non-string types follows Python built-ins and may raise AttributeError/TypeError/ValueError as described above.

### `flower.utils.broker.Redis._get_redis_client_args` · *method*

## Summary:
Returns a dict of keyword arguments that should be passed to redis.Redis to create a client, reflecting the current connection-related attributes of the Redis instance.

## Description:
Known callers and lifecycle stage:
- Called by Redis._get_redis_client() to assemble the constructor arguments immediately before instantiating a redis.Redis client.
- In this repository, _get_redis_client() is invoked from Redis.__init__ during object initialization to create and assign self.redis.

Why this is a separate method:
- Centralizes the mapping from the Redis instance's attributes to the third-party redis.Redis constructor signature.
- Improves testability and extensibility: subclasses can override or patch this single method to change client construction without duplicating logic.
- Keeps client-instantiation logic concise and separates argument assembly from the act of creating the client.

## Args:
This method takes no arguments.

## Returns:
dict
- A dictionary with the following keys and values extracted from the instance at call time:
    - 'host': value of self.host (commonly a str, e.g., 'localhost')
    - 'port': value of self.port (commonly an int, e.g., 6379)
    - 'db': value of self.vhost (an int; Redis.__init__ calls _prepare_virtual_host so this will be an integer when used in the normal initialization path)
    - 'username': value of self.username (str or None)
    - 'password': value of self.password (str or None)
- Edge cases:
    - username and/or password may be None if not provided.
    - Values are returned verbatim from the corresponding attributes; no conversion or validation is performed here.

## Raises:
- AttributeError: If any of the expected attributes (self.host, self.port, self.vhost, self.username, self.password) do not exist on the instance, attribute access will raise an AttributeError.
- Note: This method does not itself validate value types or ranges (e.g., that port is within 0–65535). Such validation, if present, is performed elsewhere (for example, _prepare_virtual_host enforces that vhost becomes an int).

## State Changes:
Attributes READ:
- self.host
- self.port
- self.vhost
- self.username
- self.password

Attributes WRITTEN:
- None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
- The instance must have the attributes host, port, vhost, username, and password defined prior to calling this method.
- When used in the normal initialization flow, Redis.__init__ ensures defaults for host and port and calls _prepare_virtual_host so vhost is an integer.

Postconditions:
- Returns a plain dictionary mapping the five keys ('host', 'port', 'db', 'username', 'password') to the current attribute values.
- No attributes of self are modified.

## Side Effects:
- None. This method performs no I/O and does not call external services. It only reads instance attributes and returns a dict.

## Implementation notes for reimplementation:
- Implementation is a one-line mapping returning the five keys shown above; do not perform additional validation or mutation here.
- Keep the key names aligned with redis.Redis's constructor argument names (db is used for the Redis database index).

### `flower.utils.broker.Redis._get_redis_client` · *method*

## Summary:
Creates and returns a redis.Redis client instance configured from this object's connection parameters; does not modify object state.

## Description:
This method centralizes construction of the redis.Redis client using the connection arguments produced by this object's _get_redis_client_args() helper.

Known callers:
- Redis.__init__: invoked during object initialization to populate self.redis (i.e., self.redis = self._get_redis_client()).

Lifecycle/context:
- Called at construction time to produce the Redis client that the Redis instance will use for subsequent broker operations.

Why this is its own method:
- Encapsulates client construction so subclasses can customize the client arguments by overriding _get_redis_client_args() (for example, RedisSsl augments the args to enable SSL) without duplicating the instantiation logic.
- Improves testability and separation of concerns: argument preparation is separate from client creation.

## Args:
This method takes no arguments.

## Returns:
redis.Redis
    - A new redis.Redis client instance created with the keyword arguments returned by self._get_redis_client_args().
    - On success, an object from the redis Python client library ready for use by higher-level broker methods.
    - Edge cases: if the redis client library raises an exception when given the provided arguments, no object is returned and the exception propagates.

## Raises:
- Any exception raised by self._get_redis_client_args()
    - For example, ValueError from argument preparation (see _prepare_virtual_host) may propagate if the configured vhost is invalid.
- Any exception raised by the redis.Redis constructor
    - For example, TypeError if invalid keyword arguments are supplied, or other exceptions raised by the redis client library during client instantiation.
- This method does not catch or transform exceptions; callers should handle exceptions as appropriate.

## State Changes:
Attributes READ:
- self.host
- self.port
- self.vhost
- self.username
- self.password
  (These attributes are accessed indirectly via self._get_redis_client_args().)

Attributes WRITTEN:
- None. This method does not modify attributes on self.

## Constraints:
Preconditions:
- The Redis object should have its connection-related attributes (host, port, vhost, username, password) initialized before calling this method (as done in Redis.__init__).
- _get_redis_client_args() must return a dict of keyword arguments acceptable to redis.Redis.

Postconditions:
- Returns a redis.Redis instance configured with the keyword arguments returned by _get_redis_client_args().
- No attributes on self are changed by this call.

## Side Effects:
- Allocates and returns a redis.Redis client object. This may allocate internal client structures (e.g., connection pool objects) depending on the redis client library implementation.
- The method itself does not perform network I/O to the Redis server as part of construction; any network activity typically occurs when the returned client issues commands. Any library-specific initialization side effects raised by redis.Redis(...) may still occur and will be propagated.

## `flower.utils.broker.RedisSentinel` · *class*

## Summary:
Represents a Redis Sentinel-backed broker adapter that resolves the current Redis master by master_name and exposes a redis client configured to talk to that master.

## Description:
RedisSentinel is an adapter subclass of RedisBase whose sole responsibility is to create a redis client that targets the master node discovered by a Redis Sentinel deployment. Use this class when you need a Redis client that automatically follows master changes managed by Sentinel—typical use cases include monitoring queue lengths or performing broker operations that must hit the active master.

Callers/factories:
- Any component that previously used RedisBase but requires automatic master discovery via Sentinel.
- Monitoring tools or broker factories that supply broker_url and broker_options and expect an instance whose self.redis is a usable redis client.

Motivation and responsibility boundary:
- RedisSentinel centralizes master discovery and client construction using redis.sentinel.Sentinel.master_for(master_name).
- It delegates URL parsing and basic broker attributes (host, port, vhost, password) to RedisBase (superclass).
- It does not implement connection lifecycle APIs (no close/context-manager). Resource cleanup for the created redis client must be performed by the caller or higher-level code.

## State:
Instance attributes (established during __init__ or inherited)

- host (str)
  - Type: string
  - Defaulting behavior: if BrokerBase left host falsy, RedisSentinel sets host to 'localhost' in __init__.
  - Constraint: expected to be a reachable Sentinel hostname or IP.

- port (int)
  - Type: integer
  - Defaulting behavior: if BrokerBase left port falsy, RedisSentinel sets port to 26379 (Sentinel default).
  - Constraint: valid TCP port (no explicit validation beyond truthiness).

- vhost (int)
  - Type: integer database index
  - Source and conversion rules (via _prepare_virtual_host(vhost)):
    - If vhost is already an instance of numbers.Integral, it is returned unchanged (e.g., 2 remains 2).
    - If vhost is falsy (None, '', or '/'), it becomes 0.
    - If vhost is a string starting with '/', the leading slash is removed and the remainder is converted to int.
    - If conversion to int fails, _prepare_virtual_host raises ValueError with the literal message: 'Database is int between 0 and limit - 1, not {vhost}'.
  - Invariant: after __init__, vhost is an integer.

- master_name (any)
  - Type: obtained from broker_options['master_name'] (no extra validation of emptiness).
  - Requirement: the broker_options dict must contain the key 'master_name'; otherwise _prepare_master_name raises ValueError('master_name is required for Sentinel broker').
  - Use: passed verbatim to sentinel.master_for(master_name).

- redis (object)
  - Type: redis client-like object returned by sentinel.master_for(master_name).
  - Value: assigned during __init__ by _get_redis_client. Expected to behave like a redis-py client and to implement methods used by RedisBase (for example, llen).
  - Constraint: failures during creation (network/auth issues, invalid sentinel_kwargs) will propagate exceptions from the redis library.

Inherited attributes referenced:
- password: used to authenticate to Sentinel when creating the sentinel object. Set by BrokerBase.__init__ if present in broker_url.

Class invariants:
- After successful construction: host, port, vhost (int), master_name (present), and redis (client object) are defined on the instance.

## Lifecycle:
Creation:
- Signature: RedisSentinel(broker_url, *args, **kwargs)
  - Note: __init__ forwards *args and **kwargs to RedisBase.__init__ (so BrokerBase parsing happens before RedisSentinel's own initialization).
- broker_options (passed in kwargs) supports:
  - 'master_name' (REQUIRED): name of the master service that Sentinel manages.
  - 'sentinel_kwargs' (optional): any value passed through the connection_kwargs dictionary to redis.sentinel.Sentinel via the 'sentinel_kwargs' key.
- Typical construction:
  - Provide broker_url so BrokerBase parses host/port/vhost/password.
  - Provide broker_options including 'master_name' (string or other value acceptable to sentinel.master_for).

Usage:
1. Construct the instance:
   - RedisBase.__init__ runs first (parsing URL and setting initial attributes); RedisSentinel.__init__ then:
     - ensures default host/port for Sentinel when missing,
     - normalizes vhost to an integer via _prepare_virtual_host,
     - extracts master_name via _prepare_master_name,
     - creates a redis client using _get_redis_client and assigns it to self.redis.
2. Use RedisBase methods (for example the async queues(...) method) which will call self.redis.llen and other redis client methods.
3. Clean up: RedisSentinel does not expose a close method. If the created redis client requires cleanup (e.g., closing a connection pool), the caller must call the appropriate method on self.redis.

Destruction / cleanup:
- No explicit cleanup provided. Caller or higher-level factory must manage lifecycle/cleanup of the redis client if required.

## Component methods (private helpers)
- _prepare_virtual_host(vhost)
  - Signature: _prepare_virtual_host(self, vhost) -> int
  - Purpose: normalize vhost to an integer database index.
  - Behavior:
    - If vhost is an instance of numbers.Integral, return it unchanged.
    - If falsy or equal to '/', treat as 0.
    - If a string beginning with '/', strip leading '/' then parse int.
    - If int(vhost) fails, raise ValueError with message: 'Database is int between 0 and limit - 1, not {vhost}'.
  - Exceptions: ValueError on non-convertible vhost.

- _prepare_master_name(broker_options)
  - Signature: _prepare_master_name(self, broker_options: dict) -> Any
  - Purpose: extract and return broker_options['master_name'].
  - Behavior:
    - Attempts to return broker_options['master_name'].
    - If the key is missing, raises ValueError('master_name is required for Sentinel broker').
  - Note: No validation is performed on the returned value beyond presence of the key.

- _get_redis_client(broker_options)
  - Signature: _get_redis_client(self, broker_options: dict) -> object
  - Purpose: construct a redis client that connects to the current master via Sentinel.
  - Behavior:
    - Builds connection_kwargs = {'password': self.password, 'sentinel_kwargs': broker_options.get('sentinel_kwargs')}.
    - Calls redis.sentinel.Sentinel([(self.host, self.port)], **connection_kwargs) to create a Sentinel object.
    - Calls sentinel.master_for(self.master_name) to obtain a client that talks to the master and returns it.
  - Side effects: does not store the Sentinel instance on self (only returns the master client).
  - Exceptions: any exception raised by the redis library during Sentinel construction or master_for (e.g., redis.exceptions.RedisError, socket errors) is propagated.

## Method Map:
flowchart LR
    A[RedisSentinel.__init__(broker_url, *args, **kwargs)]
    A --> B[RedisBase.__init__(broker_url, *args, **kwargs) (parses host/port/vhost/password)]
    A --> C[_prepare_virtual_host(vhost) -> int vhost]
    A --> D[_prepare_master_name(broker_options) -> master_name or raise ValueError]
    A --> E[_get_redis_client(broker_options) -> redis_client]
    E --> F[redis.sentinel.Sentinel([(host, port)], password=self.password, sentinel_kwargs=...)]
    F --> G[sentinel.master_for(master_name) -> redis_client assigned to self.redis]
    B --> H[instance ready: host, port, vhost(int), master_name, redis(client)]

Typical invocation order: __init__ -> _prepare_virtual_host -> _prepare_master_name -> _get_redis_client -> (redis client available)

## Raises:
- ValueError
  - Condition: broker_options does not contain 'master_name'.
    - Message raised: 'master_name is required for Sentinel broker'
  - Condition: vhost cannot be converted to int in _prepare_virtual_host.
    - Message raised: 'Database is int between 0 and limit - 1, not {vhost}' (literal message string as used in code).

- redis (library) exceptions (for example redis.exceptions.RedisError)
  - Condition: Any error raised by redis.sentinel.Sentinel(...) or sentinel.master_for(...), such as connection/authentication failures or misconfiguration. These exceptions propagate.

- Other runtime exceptions (TypeError, AttributeError, socket.error)
  - Condition: Unexpected types from BrokerBase or environmental errors during sentinel/client creation; not explicitly raised by this class but possible.

## Example:
- Construction and typical use pattern (descriptive; not executable code in this doc):
  1. Call constructor while forwarding broker_url and broker_options:
     - broker_options must include 'master_name'.
     - Additional optional key 'sentinel_kwargs' may be supplied to influence Sentinel construction.
  2. After construction, self.redis is assigned to a redis client that targets the current master.
  3. Use RedisBase methods such as the async queues(...) which will use self.redis.llen to inspect queue lengths.
  4. To clean up resources, call the appropriate cleanup on self.redis (if supported) because RedisSentinel does not provide a close method.

Notes and implementation hints:
- This class forwards *args and **kwargs to RedisBase.__init__; BrokerBase parsing runs before Sentinel-specific initialization.
- If you need to retain the Sentinel object for sentinel-level operations (e.g., discover_master or sentinel.sentinels), modify _get_redis_client to store the Sentinel instance on self or return both objects.
- Because master_name is only checked for presence, callers should ensure the provided value is valid for the Sentinel deployment; an invalid value will result in an exception from the redis library at client creation or later when operations are attempted.

### `flower.utils.broker.RedisSentinel.__init__` · *method*

## Summary:
Initializes a Redis Sentinel-backed broker client by normalizing broker attributes, extracting sentinel-specific options, determining the Redis master name, and creating a redis client stored on the instance.

## Description:
This constructor is invoked when a RedisSentinel instance is created (i.e., when the application selects the Sentinel broker backend and instantiates the RedisSentinel class to manage broker connections). It performs object setup after delegating generic parsing/assignment to the RedisBase constructor.

The method is separated from lower-level helpers so that virtual-host parsing, master-name validation, and redis client creation are encapsulated and testable individually (_prepare_virtual_host, _prepare_master_name, _get_redis_client). This keeps __init__ concise and makes error reporting for misconfiguration clearer.

Known callers / invocation context:
- Called automatically when a RedisSentinel object is instantiated by code that configures or constructs broker backends (e.g., broker factory code or tests that create RedisSentinel instances).
- Lifecycle stage: object construction / initialization.

## Args:
    broker_url (str): Broker URL passed to the RedisBase initializer; format and parsing are handled by the parent class.
    *args: Additional positional arguments forwarded to the parent class.
    **kwargs: Keyword arguments forwarded to the parent class. Recognized keys used here:
        broker_options (dict, optional): Dictionary of broker-specific options. Expected keys:
            - 'master_name' (str): REQUIRED. The name of the Redis master monitored by Sentinel.
            - 'sentinel_kwargs' (dict, optional): Additional keyword args forwarded to redis.sentinel.Sentinel.

## Returns:
    None

## Raises:
    ValueError: If broker_options does not contain 'master_name'. This is raised by _prepare_master_name when the key is missing.
    ValueError: If self.vhost cannot be normalized to an integer (e.g., non-numeric string). This is raised by _prepare_virtual_host when int() conversion fails.
    Any exception raised by the redis.sentinel.Sentinel constructor or sentinel.master_for may propagate out of this method (e.g., connection/parameter errors from the redis client library).

## State Changes:
Attributes READ:
    self.host - read to determine whether to use existing value or default to 'localhost'
    self.port - read to determine whether to use existing value or default to 26379
    self.vhost - read and passed to _prepare_virtual_host for normalization
    self.password - read (indirectly) by _get_redis_client to include in connection kwargs

Attributes WRITTEN:
    self.host - set to existing value or default 'localhost'
    self.port - set to existing value or default 26379
    self.vhost - replaced with the integer-normalized database index returned by _prepare_virtual_host
    self.master_name - set to the 'master_name' value extracted from broker_options
    self.redis - set to a redis client instance obtained from the Sentinel master_for call

## Constraints:
Preconditions:
    - The parent class __init__ (RedisBase) must have executed successfully and established any base attributes used here (notably self.host, self.port, self.vhost, and self.password).
    - broker_options must be a dict if provided; otherwise an empty dict is used.
    - broker_options must include the 'master_name' key (string) or the method will raise ValueError.

Postconditions:
    - After return, self.host and self.port are guaranteed to be truthy values (either pre-existing values or defaults).
    - self.vhost is guaranteed to be an integer (database index).
    - self.master_name is set to a non-empty value extracted from broker_options.
    - self.redis references a redis client object configured to talk to the Sentinel-selected master.

## Side Effects:
    - Instantiates a redis.sentinel.Sentinel object and calls sentinel.master_for(self.master_name) to obtain a client. Depending on the redis library implementation this may perform host/port resolution and can trigger network activity when creating the sentinel object or when the returned client first issues commands.
    - No file I/O or logging is performed directly in this method.

### `flower.utils.broker.RedisSentinel._prepare_virtual_host` · *method*

## Summary:
Normalize and validate a Redis database identifier (virtual host) and return it as an integral value suitable for use as a Redis database index; treats empty or "/" as database 0 and normalizes string forms by stripping a leading '/'.

## Description:
Known callers and context:
- Invoked from RedisSentinel.__init__ during object initialization to normalize the broker's configured vhost before the instance stores or uses it for creating Redis connections. It runs once per RedisSentinel instantiation.

Why this logic is a separate method:
- Parsing and validating the vhost is a single, well-defined responsibility required at initialization. Separating it improves readability, makes unit testing straightforward, and centralizes normalization logic for reuse.

Usage examples (plain text):
- Typical initialization flow: self.vhost = self._prepare_virtual_host(self.vhost)
- Example inputs and outcomes:
    * None, "", or "/"  -> returns 0
    * "3" or "/3"      -> returns int(3)
    * 2                -> returns 2 (unchanged)
    * True             -> returns True (booleans are instances of numbers.Integral)

## Args:
    vhost (numbers.Integral | str | None):
        - The virtual host / Redis database identifier to normalize.
        - Acceptable forms:
            * An integral already (e.g., int or any numbers.Integral) — returned unchanged.
            * A string representing an integer, optionally prefixed with '/' (e.g., "4" or "/4") — leading '/' is removed then converted to int.
            * A falsey value or single "/" (None, "", "/") — treated as database 0.
        - Note: Booleans are instances of numbers.Integral in Python; True/False will be treated as integrals.

## Returns:
    numbers.Integral:
        - If vhost was an instance of numbers.Integral, the same object is returned as-is (may be a bool).
        - For string-like inputs that are successfully parsed, returns an int of the parsed numeric value.
        - On successful return, the value is a numeric index appropriate for Redis database selection.

## Raises:
    ValueError:
        - Raised when vhost is not an Integral and cannot be converted to int.
        - Trigger condition: int(vhost) raises ValueError (for example vhost == "abc").
        - Exact message text produced by this method: 'Database is int between 0 and limit - 1, not {vhost}' (the literal "{vhost}" appears in the message; the code does not perform formatting).
        - The original ValueError from int(...) is chained (raised from exc) to preserve context.

    AttributeError (possible):
        - If vhost is non-integral and does not implement startswith('/'), calling vhost.startswith('/') will raise AttributeError. This method does not catch that error.

    TypeError (possible):
        - If int(vhost) raises TypeError for the provided type, that exception will propagate; the method only converts ValueError into the custom ValueError.

## State Changes:
    Attributes READ:
        - None. The method does not read any self.<attr> attributes.

    Attributes WRITTEN:
        - None. The method returns a normalized value; any assignment to self.vhost occurs in the caller (e.g., __init__).

## Constraints:
    Preconditions:
        - If vhost is not an instance of numbers.Integral, it should be a string-like object that:
            * supports startswith('/') if a leading slash may be present, and
            * can be converted by int(...) after optional removal of a leading '/'.
        - Callers should be prepared to handle ValueError, AttributeError, or TypeError for malformed inputs.

    Postconditions:
        - On success, the return value is a numeric database index (numbers.Integral) normalized from the provided input.
        - Common textual forms are normalized: empty or "/" -> 0; "/N" -> N; "N" -> N.

## Side Effects:
    - None. The method performs only local computation and raises exceptions for invalid inputs; it does not perform I/O, network calls, logging, or mutate objects outside the method scope.

### `flower.utils.broker.RedisSentinel._prepare_master_name` · *method*

## Summary:
Extracts and returns the sentinel master name from the provided broker options mapping; used during object initialization to obtain the master identifier without mutating object state.

## Description:
Known callers and context:
    - RedisSentinel.__init__: called during RedisSentinel object construction to obtain the master name before creating the Sentinel client. The returned value is assigned to self.master_name by the caller.

Why this is a separate method:
    - Isolates the extraction and validation of the required 'master_name' option from the constructor, keeping initialization logic concise and making the behavior reusable and testable.
    - Centralizes the error message for the missing key so callers get a consistent, clear failure mode.

## Args:
    broker_options (Mapping-like): A mapping (typically dict) expected to contain the key 'master_name'.
        - Allowed values: any value stored under 'master_name' in the mapping (no coercion or validation is performed by this method).
        - Default: none (the caller is expected to supply broker_options; if omitted or not mapping, errors may propagate as described below).

## Returns:
    Any: The raw value taken from broker_options['master_name'] returned as-is. The code makes no type conversions; in normal usage this is the sentinel master name (commonly a string), but any object stored under that key will be returned.

## Raises:
    ValueError: Raised when broker_options does not contain the 'master_name' key. The ValueError wraps the original KeyError and carries the message 'master_name is required for Sentinel broker'.
    TypeError (propagated): If broker_options is None or not subscriptable (does not implement __getitem__), a TypeError (or other exception from attempting broker_options['master_name']) will propagate; this method only catches KeyError.

## State Changes:
    Attributes READ:
        - None: the method does not read or depend on any self.<attr> attributes.
    Attributes WRITTEN:
        - None: the method does not modify any self.<attr> attributes. (Note: callers commonly assign its return value to self.master_name, but that assignment occurs outside this method.)

## Constraints:
    Preconditions:
        - broker_options must be a mapping-like object that supports key access via broker_options['master_name'] and should contain that key.
    Postconditions:
        - If the method returns normally, the exact broker_options['master_name'] value is returned unchanged.
        - If the key is missing, the method raises ValueError and does not modify object state.

## Side Effects:
    - None: no I/O, no network calls, and no mutation of external objects are performed by this method. Any assignment to self.master_name is performed by the caller (e.g., within RedisSentinel.__init__).

### `flower.utils.broker.RedisSentinel._get_redis_client` · *method*

## Summary:
Construct and return a redis-py client bound to the Sentinel master for this instance, leaving the object's attributes unchanged.

## Description:
This helper builds a redis.sentinel.Sentinel using the instance host/port/password and any sentinel-specific options supplied via broker_options, then returns the client proxy for the configured master name.

Known callers and lifecycle:
- Called from RedisSentinel.__init__ to initialize self.redis during object construction (RedisSentinel.__init__ sets broker_options = kwargs.get('broker_options', {}) and then assigns self.redis = self._get_redis_client(broker_options)).
- Intended to be called during setup/initialization; callers expect a ready-to-use redis client object that will route commands to the current Sentinel master.

Why this is a separate method:
- Isolates the sentinel client creation logic for clarity and easier testing/overriding.
- Keeps RedisSentinel.__init__ concise and enables subclasses to override client creation without changing initialization flow.

## Args:
    broker_options (dict):
        Mapping of broker-specific options. Expected/recognized keys:
        - 'sentinel_kwargs' (optional): value forwarded as the sentinel_kwargs keyword argument to redis.sentinel.Sentinel. If omitted, None is forwarded.
      Notes:
        - RedisSentinel.__init__ passes a dict by default ({}), so callers typically do not pass None.
        - If a non-mapping (e.g., None) is passed, an AttributeError will be raised when the method attempts to call broker_options.get(...).

## Returns:
    redis client object (object provided by redis-py):
        The value returned by redis.sentinel.Sentinel(...).master_for(self.master_name).
        - This is the redis-py client/proxy that the application uses to execute Redis commands against the master.
        - The concrete runtime type depends on the installed redis-py version (commonly an instance that exposes Redis command methods).
        - The returned client may establish network connections lazily when commands are executed; creating it does not necessarily perform immediate network I/O.

## Raises:
    - AttributeError: If broker_options is None or otherwise lacks a .get method.
    - Any exception propagated from the redis library:
        - Exceptions raised during instantiation of redis.sentinel.Sentinel with the provided arguments (e.g., TypeError for invalid argument types).
        - Exceptions raised by sentinel.master_for(self.master_name) (e.g., if master_name is invalid according to the redis client).
    - Notes: RedisSentinel._prepare_master_name already raises ValueError during initialization if master_name is missing; by the time this method is called (from __init__), self.master_name is expected to be valid.

## State Changes:
    Attributes READ:
        - self.password (used as 'password' in Sentinel kwargs)
        - self.host (used to build the sentinels list)
        - self.port (used to build the sentinels list)
        - self.master_name (passed to master_for)
    Attributes WRITTEN:
        - None. The method does not mutate any self.<attr> fields.

## Constraints:
    Preconditions:
        - self.host must be set (string hostname or IP) and self.port must be set (integer port) prior to calling.
        - self.master_name must be set to a non-empty string identifying the Sentinel master.
        - broker_options must be a mapping-like object (typically a dict); it must implement .get.
    Postconditions:
        - A redis client proxy configured to talk to the Sentinel-resolved master (self.master_name) is returned.
        - No attributes on self have been modified by this method.

## Side Effects:
    - Allocates a redis.sentinel.Sentinel object and obtains a master client proxy; objects from redis-py are created.
    - May result in network activity when the returned client is later used (connection establishment and command execution are handled by the redis client).
    - No filesystem I/O and no mutation of external objects are performed directly by this method.
    - Repeated calls create new Sentinel/client objects (idempotent w.r.t. self state but increases resource usage if called multiple times).

## `flower.utils.broker.RedisSocket` · *class*

## Summary:
RedisSocket is a small Redis-backed broker adapter that instantiates a redis.Redis client which connects via a Unix domain socket built from the broker vhost and applies the parsed broker password for authentication.

## Description:
RedisSocket exists to provide a convenience subclass of RedisBase that manages creation of a Redis client using a Unix socket path derived from the broker URL's vhost. Instead of leaving the redis attribute unset (as RedisBase does), RedisSocket constructs and assigns a redis.Redis instance during initialization so the instance is immediately usable for Redis I/O (llen, lrange, etc.), subject to the redis client API.

Typical callers / scenarios:
- A component that needs a ready-to-use Redis-backed broker adapter and that expresses the Redis endpoint as a broker URL whose vhost encodes a local Unix socket path.
- Monitoring or inspection utilities that prefer the adapter to create and own the Redis client rather than assigning one externally.

Motivation and responsibility:
- Responsibility: parse broker URL (delegated to BrokerBase/RedisBase), then create a redis.Redis client connected over a Unix domain socket using the parsed vhost and password.
- Boundary: RedisSocket creates and assigns the client but does not add connection pooling management methods (e.g., close, context-manager) itself. Callers who need deterministic connection cleanup must operate on the created client (self.redis) or extend RedisSocket.

## State:
Instance attributes (explicitly set by RedisSocket or inherited and used here)

- redis (redis.Redis)
  - Type: instance of redis.Redis (redis-py client).
  - Value after __init__: a new redis.Redis created with:
      unix_socket_path = '/' + self.vhost
      password = self.password
  - Invariant: present and non-None after initialization. It is intended to be a ready-to-use Redis client exposing the redis-py API (e.g., llen).
  - Note: The exact client API depends on the installed redis library version; callers should program against methods they expect (e.g., llen, close/connection_pool).

Inherited / used attributes (from BrokerBase / RedisBase)
- vhost (str)
  - Source: set by BrokerBase during super().__init__(broker_url, ...).
  - Use: concatenated to a leading '/' to build unix_socket_path.
- password (str | None)
  - Source: set by BrokerBase during URL parsing.
  - Use: passed into redis.Redis to authenticate the client.

Constructor parameters (signature)
- broker_url (str)
  - Required. Passed to parent class for parsing to obtain vhost, password, and other connection fields.
- *args, **kwargs
  - Forwarded to the superclass constructor (BrokerBase/RedisBase). Any broker_options expected by RedisBase can be provided here.

Class invariants:
- After __init__ completes, self.redis is an instance of redis.Redis (constructed with unix_socket_path and password), and inherited attributes (vhost, password, priority_steps, sep, broker_prefix) remain available.

## Lifecycle:
Creation:
- Instantiate with RedisSocket(broker_url, *args, **kwargs).
  - The constructor calls super().__init__(broker_url, *args, **kwargs) to parse the broker URL and set inherited fields (vhost, password, etc.).
  - Then it creates self.redis = redis.Redis(unix_socket_path='/' + self.vhost, password=self.password).

Usage:
- After construction the instance is ready to perform Redis I/O through self.redis (e.g., call methods that RedisBase expects such as llen when using RedisBase.queues).
- Typical call sequence:
  1. r = RedisSocket('redis+socket:///var/run/redis/redis.sock', broker_options={...})
  2. r.queues([...]) or other RedisBase-provided inspection/utility methods which use r.redis.
- No additional connection method calls are required to make the client usable; the redis.Redis client is created synchronously in __init__.

Destruction / cleanup:
- RedisSocket does not implement explicit cleanup methods. Because it creates the redis client, callers who need to free resources should call the client-specific cleanup APIs (for example, redis_client.close() if available in the installed redis library, or redis_client.connection_pool.disconnect()).
- If you extend RedisSocket in a subclass that owns its client, implement and expose a close() or context-manager protocol to manage lifetime deterministically.

## Method Map:
flowchart LR
    A[RedisSocket.__init__(broker_url, *args, **kwargs)] --> B[super().__init__ -> parse broker_url -> set vhost, password, etc.]
    B --> C[create redis.Redis(unix_socket_path='/' + vhost, password=password) and assign self.redis]
    C --> D[instance ready for RedisBase methods that perform I/O (e.g., queues -> self.redis.llen(...))]

## Raises:
- Exceptions raised by the superclass constructor (super().__init__):
  - Any exceptions that BrokerBase or RedisBase raise during broker_url parsing or option handling (for example, ValueError for malformed URLs). These are propagated unchanged.
- Exceptions raised by the redis client constructor:
  - The call to redis.Redis(unix_socket_path='/' + self.vhost, password=self.password) may raise exceptions coming from the redis library (e.g., TypeError for invalid parameter types, redis.exceptions.RedisError for library-specific failures). These are not caught by RedisSocket and will propagate to the caller.
- Import-time error conditions:
  - If the redis module was not available at module import time (missing dependency), attempts to construct the client will fail earlier; ensure the redis library is installed.

Practical trigger conditions:
- Missing or malformed broker_url that prevents super().__init__ from populating vhost/password.
- An unexpected type for vhost (e.g., None) may lead to constructing an invalid unix_socket_path (resulting in errors from the redis client).

## Example:
Assume a broker URL whose vhost encodes a Unix socket path (the exact scheme used by your BrokerBase parser may differ; adapt accordingly).

1) Create a RedisSocket instance:
    r = RedisSocket('redis+socket:///var/run/redis/redis.sock')

2) Use inherited RedisBase methods immediately:
    stats = await r.queues(['default'])   # queues will call r.redis.llen on prioritized keys

3) Cleanup the created client when done (example; actual method names depend on redis library version):
    try:
        # use r...
        pass
    finally:
        # If redis-py exposes close()
        if hasattr(r.redis, 'close'):
            r.redis.close()
        # As an alternative, disconnect the connection pool:
        if hasattr(r.redis, 'connection_pool'):
            try:
                r.redis.connection_pool.disconnect()
            except Exception:
                # ignore or log pool-disconnect errors as appropriate
                pass

### `flower.utils.broker.RedisSocket.__init__` · *method*

## Summary:
Sets up the Redis-backed broker client for this instance by delegating URL parsing and common initialization to the superclass chain, then creating and storing a redis.Redis client on self.redis configured to use a UNIX domain socket path derived from the parsed vhost and the parsed password.

## Description:
This constructor performs two, ordered steps:
1. Calls the superclass constructors (RedisBase -> BrokerBase) to parse broker_url and initialize broker connection attributes such as self.vhost and self.password. BrokerBase uses urllib.parse.urlparse to extract these values from broker_url (self.vhost is derived from the URL path without the leading slash and self.password is the URL password, URL-unquoted if present).
2. Instantiates a redis.Redis client with unix_socket_path='/' + self.vhost and password=self.password and assigns it to self.redis.

Known callers / lifecycle:
- This method is invoked whenever RedisSocket(...) is instantiated. Typical application flow: when the application chooses the Redis broker implementation and constructs its broker object, this __init__ runs as part of object construction to prepare the redis client for subsequent operations.
- No other internal callers invoke __init__ directly; it is executed only by Python object construction.

Why it's a separate method:
- Initialization of the redis client depends on attributes produced by the superclass URL parsing (vhost and password). Centralizing client creation in the constructor ensures the redis client is configured immediately after the base initialization and keeps Redis-specific setup out of generic base classes.

## Args:
    broker_url (str): Broker connection URL passed to the constructor (e.g. a URL parseable by urllib.parse.urlparse). Required. BrokerBase expects a string and extracts host, port, vhost (from path), username, and password from it.
    *args: Extra positional arguments forwarded to the superclass constructors. Not used directly in this method.
    **kwargs: Extra keyword arguments forwarded to the superclass constructors. RedisBase consumes broker_options from kwargs; this constructor forwards kwargs without inspecting them.

## Returns:
    None. As a constructor, it does not return a value. Upon successful completion, self.redis references the configured redis.Redis client.

## Raises:
    ImportError:
        - Raised by RedisBase.__init__ if the redis library is not available (RedisBase contains an explicit check that raises ImportError('redis library is required') when the redis module is falsy).
    Exception types raised by urllib.parse.urlparse / BrokerBase.__init__:
        - Passing an unsupported type for broker_url (e.g., None or a non-string) can raise an exception from urlparse or subsequent string operations; such exceptions propagate.
    Exceptions raised by redis.Redis(...):
        - Any exception that the redis client constructor raises (TypeError, ValueError, redis-related errors) will propagate from this constructor. The method does not catch or wrap these exceptions.

## State Changes:
Attributes READ:
    self.vhost — read to compute unix_socket_path as '/' + self.vhost. BrokerBase.__init__ sets this value to the broker URL path with the leading slash removed (may be an empty string).
    self.password — read to pass as the redis client's password. BrokerBase.__init__ sets this to the URL password or None; URL-decoding is applied by BrokerBase.
Attributes WRITTEN:
    self.redis — assigned a redis.Redis client instance (overwrites the prior value set to None by RedisBase.__init__).

## Constraints:
Preconditions:
    - broker_url must be a URL-like string acceptable to urllib.parse.urlparse. BrokerBase.__init__ assumes broker_url is a string; passing non-string types may raise exceptions.
    - The redis library must be importable (module-level import succeeded); otherwise RedisBase.__init__ will raise ImportError before the redis client is created.
Postconditions:
    - On normal return, self.redis is a redis.Redis instance configured with unix_socket_path='/' + self.vhost and password=self.password.
    - If an exception is raised during superclass initialization or redis client creation, the instance may not be fully initialized and self.redis may be left as None or unset.

## Side Effects:
    - Instantiates a redis.Redis client object. Whether this triggers immediate network or socket I/O depends on the redis client implementation (the constructor may or may not open a connection eagerly). This constructor itself does not execute explicit network operations beyond creating the client object.
    - Propagates any exceptions from URL parsing, the superclass constructors, or redis client instantiation to the caller; it does not swallow or convert them.

## Usage note:
- Typical usage is simply instantiating the class with a broker URL:
  Create the object with RedisSocket('redis://[:password]@host:port/vhost') (or another broker_url format expected by the application). The constructor will parse the URL and prepare self.redis for the instance.

## `flower.utils.broker.RedisSsl` · *class*

## Summary:
RedisSsl is a small Redis broker adapter subclass that enforces SSL mode for Redis client connections and allows callers to pass additional SSL configuration that will be merged into the redis client arguments.

## Description:
RedisSsl exists to provide a drop-in variant of the Redis broker adapter that ensures the underlying redis client is created with SSL/TLS enabled. It is intended to be instantiated when a broker URL should connect over TLS (commonly a "rediss" style endpoint). The class itself does not construct the redis client differently from its superclass; instead it modifies the keyword arguments used to construct the client so that ssl is enabled and any caller-supplied TLS options are included.

When to instantiate:
- Use this class when the application needs a Redis-backed broker that connects over SSL/TLS.
- Typical call sites: broker factory code or configuration layers that select a Redis-backed broker implementation for secure (TLS) connections.

Motivation and responsibility boundary:
- Responsibility: ensure the redis client arguments include ssl=True and incorporate any caller-provided SSL options (certificate files, verification settings, etc.).
- Boundary: it delegates all URL parsing, host/port/vhost normalization, client instantiation, and other broker behaviors to the Redis superclass. RedisSsl only enforces and augments SSL-related client configuration.

## State:
Instance attributes introduced or relied upon by RedisSsl:

- broker_use_ssl (dict | any)
  - Type: typically dict (but any value is accepted and stored)
  - Valid values:
    - dict: a mapping of keyword arguments to merge into redis client kwargs (recommended)
    - any other value (e.g., True): stored but not merged; only ssl=True will be set
  - Default behavior: __init__ requires this parameter to be present in kwargs; if present but falsy, the stored value will be the provided value or {} if explicitly set that way.
  - Invariant: attribute exists after __init__ returns.

Inherited state (from Redis / RedisBase — summarized here because RedisSsl relies on them):
- host (str): resolved hostname used for client 'host'
- port (int): resolved port used for client 'port'
- vhost (int): database index used as client 'db'
- username (str | None): passed through to client
- password (str | None): passed through to client
- Any other attributes created by the superclass remain present; RedisSsl does not remove or alter them.

Class invariants:
- Calls to _get_redis_client_args() will always include the key 'ssl' set to True.
- If broker_use_ssl is a dict, its key/value pairs will be merged into the dict returned by _get_redis_client_args() (potentially overriding defaults from the superclass).

## Lifecycle:
Creation:
- Required arguments:
  - broker_url (str): same as required by the Redis superclass; passed through to super().__init__ for parsing.
  - kwargs must include a key named 'broker_use_ssl'. If this key is absent, RedisSsl.__init__ raises ValueError.
- Typical instantiation flow:
  1. Caller supplies broker_url and an explicit keyword 'broker_use_ssl' (recommended as a dict of redis-py SSL options or at least a truthy value).
  2. RedisSsl stores the provided broker_use_ssl value on the instance.
  3. RedisSsl delegates remaining initialization to the Redis superclass via super().__init__(broker_url, *args, **kwargs). The superclass will parse the URL and create or arrange for a redis client using the argument mapping that will include ssl=True (because of the override provided by RedisSsl).

Usage:
- Typical method sequence:
  1. Instantiate RedisSsl with broker_url and broker_use_ssl in kwargs.
  2. The rest of the broker lifecycle and API is provided by Redis (enqueued/dequeued operations, queue inspection methods, etc.) and will use the redis client that was instantiated using the SSL-enabled client args.
- There is no special ordering of method calls required beyond instantiation before use.

Destruction / cleanup:
- RedisSsl does not provide any explicit cleanup or close method itself.
- Any cleanup of the underlying redis client (for example, calling client.close() if applicable) must be performed by the caller or by a subclass that implements deterministic cleanup.

## Method Map:
flowchart LR
    A[__init__(broker_url, *args, **kwargs)] --> B[check 'broker_use_ssl' in kwargs]
    B -->|missing| C[raise ValueError('rediss broker requires broker_use_ssl')]
    B -->|present| D[self.broker_use_ssl = kwargs.get('broker_use_ssl', {})]
    D --> E[super().__init__(broker_url, *args, **kwargs)]
    E --> F[_get_redis_client_args() called by superclass to build client kwargs]
    F --> G[RedisSsl._get_redis_client_args() -> calls super()._get_redis_client_args()]
    G --> H[set ssl=True in returned dict]
    H --> I[if broker_use_ssl is dict -> merge broker_use_ssl items into client args]
    I --> J[client args returned to superclass which instantiates redis client]

## Methods (behavioral summary):
- __init__(broker_url, *args, **kwargs)
  - Purpose: require broker_use_ssl and initialize the adapter via the Redis superclass.
  - Notable side effect: stores broker_use_ssl on the instance and relies on the superclass to continue initialization.

- _get_redis_client_args()
  - Purpose: produce keyword arguments for constructing the redis client.
  - Behavior:
    - Calls the superclass implementation to obtain base client args (host, port, db, username, password, etc.).
    - Ensures client_args['ssl'] = True (forces TLS mode).
    - If self.broker_use_ssl is a dict, merges its key/value pairs into client_args (overrides or extends base args).
    - Returns the resulting dict for use by the superclass's client construction logic.
  - Edge cases:
    - If broker_use_ssl is not a dict (for example True or None), no merging occurs; only ssl=True is added.
    - No validation is performed on broker_use_ssl contents — invalid keys or values will be passed to redis-py and may raise errors there.

## Raises:
- ValueError (from __init__)
  - Condition: kwargs does not contain the key 'broker_use_ssl'.
  - Message: 'rediss broker requires broker_use_ssl'

- Exceptions propagated from superclass or redis client construction
  - Condition: Any exception raised by super().__init__ (e.g., URL parsing failures, invalid parameters) or by the redis client constructor invoked by the superclass (e.g., TypeError, redis.exceptions.RedisError).
  - Note: RedisSsl does not catch these exceptions; they propagate to the caller.

## Example (usage pattern, described in prose):
- To create a TLS-enabled Redis broker adapter, call the constructor with a broker URL and include the required broker_use_ssl keyword. The recommended form for broker_use_ssl is a dict containing redis-py SSL/TLS options (for example, paths to CA certs or client certs and verification settings). After construction, use the instance through the usual Redis broker API; the underlying redis client will be created with ssl=True and any merged TLS options. When finished, if the underlying redis client requires explicit cleanup, perform that cleanup externally (for example by calling the client's close method if available).

### `flower.utils.broker.RedisSsl.__init__` · *method*

## Summary:
Initializes a RedisSsl broker instance by requiring and storing SSL configuration (broker_use_ssl) and then delegating full initialization to the Redis superclass, which sets up host/port/vhost and creates the Redis client.

## Description:
This constructor is executed when a RedisSsl object is instantiated and is responsible for validating and recording SSL-related broker options before performing the standard Redis initialization. Typical call site: any code that constructs a RedisSsl broker object (e.g., broker factory or broker setup code) — it runs during object construction.

Rationale for being a distinct method:
- Ensures that an SSL-specific configuration key ('broker_use_ssl') is present and captured on the instance before the generic Redis initialization runs.
- Keeps SSL-specific validation/assignment localized so the rest of the Redis initialization (host/port/vhost resolution and client creation) can remain shared in the superclass.

Interactions:
- Reads nothing from self before assignment.
- Writes self.broker_use_ssl locally.
- Delegates to Redis.__init__(broker_url, *args, **kwargs) which (per Redis implementation) will set defaults for host/port, prepare the virtual host, and instantiate the redis client (self.redis).
- The value stored in self.broker_use_ssl is later used by RedisSsl._get_redis_client_args(): that method always sets client_args['ssl'] = True and, if self.broker_use_ssl is a dict, merges its items into client_args to pass SSL parameters to redis.Redis.

## Args:
    broker_url (str):
        - The broker URL passed through to the superclass for parsing/processing.
        - The function does not validate broker_url itself; it is forwarded to Redis.__init__.
    *args:
        - Positional arguments forwarded unchanged to the Redis superclass constructor.
    **kwargs:
        - Must include the key 'broker_use_ssl'.
        - broker_use_ssl (required):
            - Allowed types: any Python object, but commonly a dict of ssl options (e.g., {'ssl_cert_reqs': None} or other redis client SSL kwargs).
            - When a dict is provided, its items are merged into the redis client args (see _get_redis_client_args).
            - Default: There is no default — absence triggers a ValueError. The code uses kwargs.get('broker_use_ssl', {}) to read the value, but the presence of the key is required.

## Returns:
    None
    - As a constructor, it returns None implicitly. The observable result is the mutated instance (self).

## Raises:
    ValueError:
        - Raised unconditionally when the 'broker_use_ssl' key is not present in kwargs.
        - Exact message in code: 'rediss broker requires broker_use_ssl'

## State Changes:
Attributes READ:
    - None are read directly from self by this method.

Attributes WRITTEN:
    - self.broker_use_ssl: set to kwargs.get('broker_use_ssl', {}) (effectively kwargs['broker_use_ssl'] given the required-key check).
    - Additionally, as a result of calling super().__init__(...), the following attributes are set by Redis.__init__ (and are guaranteed to exist after this constructor completes):
        - self.host (defaults to 'localhost' if absent)
        - self.port (defaults to 6379 if absent)
        - self.vhost (normalized by _prepare_virtual_host)
        - self.redis (the Redis client instance returned by _get_redis_client)

## Constraints:
Preconditions:
    - The caller must provide the key 'broker_use_ssl' in kwargs (the value may be None, a dict, a boolean, etc., but the key must exist).
    - broker_url and any forwarded args/kwargs must be acceptable to Redis.__init__ (parsing/validation of broker_url occurs in the superclass).

Postconditions:
    - self.broker_use_ssl is set to the provided value from kwargs.
    - Redis.__init__ has executed, so host, port, vhost, and redis attributes are initialized on self.
    - Subsequent calls within this class (e.g., _get_redis_client_args) will unconditionally mark 'ssl' True for the redis client and may merge broker_use_ssl if it is a dict.

## Side Effects:
    - May raise ValueError (see Raises).
    - Calls Redis.__init__ which performs further initialization (virtual-host normalization and creation of the redis client object).
    - Eventually leads to creation of a redis.Redis client object (via Redis._get_redis_client calling redis.Redis(**client_args)); that constructs an external library client object (actual network connection behavior depends on the redis library and is not forced by this constructor).

### `flower.utils.broker.RedisSsl._get_redis_client_args` · *method*

## Summary:
Return a Redis client keyword-arguments dict configured for SSL: enables SSL and merges any per-broker SSL options stored on the instance.

## Description:
This helper produces the keyword-arguments dictionary used to configure a redis client with SSL enabled. It is intended to be invoked at the point where the Redis client configuration is assembled (for example, by the base Redis implementation when creating or connecting a client). The method delegates to the superclass to obtain the baseline client arguments, then enforces SSL and applies any instance-specific SSL options.

Known callers and lifecycle stage:
- Intended caller: the code that constructs or configures the redis client (commonly implemented in the Redis base class or in connection/initialization routines that create a redis client). This is typically executed during client creation/connection setup.
- Lifecycle stage: invocation occurs before establishing a connection to Redis, when client kwargs must be prepared.

Why this logic is a separate method:
- Centralizes the SSL-specific augmentation of redis client args in one place, keeping subclass customization (SSL flags and options) separate from the base client-argument construction.
- Allows subclasses to override or extend only this piece of behavior without duplicating the superclass argument-building logic.

## Args:
    None

## Returns:
    dict: A dictionary of keyword arguments for redis client construction.
    - Guaranteed key/value:
        - 'ssl': True (boolean) — explicitly set by this method.
    - Additional keys:
        - Any key/value pairs from self.broker_use_ssl when that attribute is a dict are merged into the returned dict, potentially overriding existing keys from the superclass's dict.
    - Edge cases:
        - If the superclass returns a dict, it is mutated in-place and returned.
        - If self.broker_use_ssl is not a dict, it is ignored and only 'ssl': True is added.

## Raises:
    None raised directly by this method.
    - Note: the RedisSsl.__init__ enforces that a broker_use_ssl value is provided in kwargs and will raise ValueError at construction time if the key is missing; this method itself does not raise based on that attribute.

## State Changes:
    Attributes READ:
        - self.broker_use_ssl
    Attributes WRITTEN:
        - None (this method does not assign to any self.<attr> fields)
    Mutations:
        - The dictionary returned by super()._get_redis_client_args() is modified in-place: the 'ssl' key is set to True and, if broker_use_ssl is a dict, its items are added/merged into that dict.

## Constraints:
    Preconditions:
        - The instance must have an attribute broker_use_ssl. (RedisSsl.__init__ ensures a broker_use_ssl entry is present in kwargs or raises ValueError at construction.)
        - The superclass _get_redis_client_args() must return a mutable mapping (typically a dict). If it returns a non-mutable or non-mapping value, in-place updates will fail.
    Postconditions:
        - The returned mapping contains 'ssl': True.
        - If broker_use_ssl is a dict, every key/value pair from that dict will be present in the returned mapping (overwriting any same-named keys from the superclass mapping).

## Side Effects:
    - Calls superclass method: super()._get_redis_client_args().
    - Mutates the client-arguments mapping returned by the superclass (in-place).
    - No I/O, network calls, or modifications to external objects other than the returned mapping.

## `flower.utils.broker.Broker` · *class*

## Summary:
Broker is a lightweight factory/abstract base that selects and returns a concrete broker implementation instance based on the provided broker_url scheme; it also defines the abstract coroutine signature for obtaining queues.

## Description:
Broker centralizes backend selection: calling Broker(broker_url, *args, **kwargs) inspects the URL scheme (using urllib.parse.urlparse) and returns an instance of a concrete broker implementation:

- scheme "amqp"           -> RabbitMQ(broker_url, *args, **kwargs)
- scheme "redis"          -> Redis(broker_url, *args, **kwargs)
- scheme "rediss"         -> RedisSsl(broker_url, *args, **kwargs)
- scheme "redis+socket"   -> RedisSocket(broker_url, *args, **kwargs)
- scheme "sentinel"       -> RedisSentinel(broker_url, *args, **kwargs)

If the scheme is not one of the supported values, Broker.__new__ raises NotImplementedError.

Broker also declares an abstract coroutine:
- async def queues(self, names): concrete implementations must implement this and provide backend-specific semantics for retrieving/creating queue handles.

Typical callers:
- Any code that needs a broker instance without committing to a specific backend should call Broker(broker_url, ...) and use the returned object polymorphically.
- Callers that require backend-specific behavior may instantiate concrete implementations directly.

Motivation:
- Keep backend selection centralized and uniform.
- Provide a common interface shape (queues coroutine) so higher-level code can work across backends.

## State:
- Broker base:
    - The Broker class itself does not define persistent instance attributes; its responsibility is selection and delegation to a concrete implementation.
- __new__ parameters:
    - broker_url (str): Required. Parsed via urllib.parse.urlparse; the scheme portion determines which concrete class is instantiated.
    - *args, **kwargs: Forwarded to the chosen concrete implementation. Exact meaning depends on the concrete class; some concrete implementations forward these to their superclass constructors (for example BrokerBase or RedisBase).
- Concrete-implementation invariants:
    - Some concrete implementations normalize or derive attributes inherited from shared bases. For example, Redis-oriented implementations documented elsewhere normalize certain numeric attributes to an int during __init__ (i.e., after construction an attribute is guaranteed to be an int). The Broker base does not enforce or mutate those attributes itself.
- Class invariants:
    - After construction, callers will receive an instance of a concrete broker class (one of RabbitMQ, Redis, RedisSsl, RedisSocket, RedisSentinel).
    - The returned instance is expected to provide an async queues(names) coroutine; the exact return type/semantics are defined by the concrete class.

## Lifecycle:
- Creation:
    - Instantiate by calling Broker(broker_url, *args, **kwargs). broker_url must contain a scheme recognized by Broker.__new__.
    - The factory returns a concrete instance; callers should treat it as that concrete type for further interactions.
    - Note: concrete constructors commonly accept broker_url plus additional args/kwargs, and may forward these to a shared superclass. Consult the concrete class documentation for exact constructor parameters and any normalization behavior.
- Usage:
    - Typical sequence:
        1. broker = Broker("redis://host:port/0")
        2. await broker.queues(["default", "priority"])
        3. Use backend-specific methods on the returned instance
    - The Broker base imposes no further ordering; concrete implementations may require explicit connect/open calls or other sequencing—consult those implementations.
- Destruction / Cleanup:
    - Broker does not provide cleanup methods. Concrete implementations may expose close(), disconnect(), or async cleanup coroutines; callers must call the appropriate cleanup API on the returned concrete instance when required.

## Method Map:
graph TD
    A[call Broker(broker_url, *args, **kwargs)] --> B{urlparse(broker_url).scheme}
    B -->|amqp| C[RabbitMQ(...)]
    B -->|redis| D[Redis(...)]
    B -->|rediss| E[RedisSsl(...)]
    B -->|redis+socket| F[RedisSocket(...)]
    B -->|sentinel| G[RedisSentinel(...)]
    B -->|other| H[raise NotImplementedError]
    C --> I[implements async queues(names)]
    D --> I
    E --> I
    F --> I
    G --> I

## Raises:
- NotImplementedError: If urlparse(broker_url).scheme is not one of the supported schemes listed above.
- Indirect errors:
    - If broker_url is not a suitable input for urlparse or if a selected concrete class (e.g., RabbitMQ or Redis) is not importable/available at runtime, Python will raise the corresponding errors (TypeError, NameError, ImportError, etc.). Broker does not catch these.

## Responsibilities and notes for concrete implementations:
- Constructor semantics:
    - Concrete classes typically accept (broker_url, *args, **kwargs) but may forward these values to a shared superclass (BrokerBase or RedisBase). Callers should consult each concrete class for exact constructor arguments and any forwarded semantics.
- Attribute normalization:
    - Some concrete backends establish invariants on attributes inherited from shared bases (for example normalizing numeric values to int in __init__). Those invariants are implemented by the concrete class or its superclass, not by Broker.
- Interface requirement:
    - Concrete implementations must implement async def queues(self, names): and document the return type and behavior. The Broker base only defines the coroutine signature (raising NotImplementedError) to indicate that subclasses must provide it.

## Raises:
- NotImplementedError: Raised by Broker.__new__ for unsupported schemes.

## Example:
1) Obtain a broker instance (factory selects concrete class):
    broker = Broker("redis://localhost:6379/0")
2) Use the broker to fetch queues (queues is awaitable):
    queues = await broker.queues(["default", "priority"])
3) Perform backend-specific operations and cleanup if needed:
    if hasattr(broker, "close"):
        broker.close()
    if hasattr(broker, "disconnect"):
        await broker.disconnect()

### `flower.utils.broker.Broker.__new__` · *method*

## Summary:
Selects and returns a concrete broker adapter instance based on the scheme part of the provided broker URL; does not modify the Broker class instance.

## Description:
This is a factory-style allocator invoked at object-creation time when code instantiates the Broker class (i.e., when someone calls Broker(broker_url, ...) or otherwise triggers object construction). It inspects the URL scheme extracted via urllib.parse.urlparse(broker_url).scheme and immediately constructs and returns an instance of the corresponding concrete adapter class:

- 'amqp'       -> RabbitMQ(...)
- 'redis'      -> Redis(...)
- 'rediss'     -> RedisSsl(...)
- 'redis+socket' -> RedisSocket(...)
- 'sentinel'   -> RedisSentinel(...)

Known callers / invocation contexts:
- Any part of the codebase that requests a broker adapter by calling Broker(broker_url, ...) — commonly in configuration parsing, broker factory functions, or application startup code that resolves connection URLs into concrete broker adapter objects.
- It runs during the object creation lifecycle: Python calls __new__ before __init__, and this method returns a ready-to-use concrete adapter instance by delegating construction to the target class's constructor.

Rationale for being in __new__:
- The method must be able to return an instance of a different concrete class (not just initialize self). Implementing this dispatch in __new__ allows returning a fully constructed object of the appropriate adapter class directly. Doing the dispatch in __init__ is insufficient when the desired object is not an instance of the Broker class itself.

## Args:
    broker_url (str):
        A broker connection URL string that is parseable by urllib.parse.urlparse.
        Expected to include a scheme (the leading protocol identifier).
        Allowed scheme values handled by this method: 'amqp', 'redis', 'rediss', 'redis+socket', 'sentinel'.
    *args:
        Positional arguments that will be forwarded unchanged to the selected concrete class constructor.
    **kwargs:
        Keyword arguments forwarded unchanged to the selected concrete class constructor.

## Returns:
    object:
        An instance of one of the concrete broker adapter classes listed above:
        - RabbitMQ when scheme == 'amqp'
        - Redis when scheme == 'redis'
        - RedisSsl when scheme == 'rediss'
        - RedisSocket when scheme == 'redis+socket'
        - RedisSentinel when scheme == 'sentinel'

    Edge cases:
        - If a matching scheme is found, this method returns whatever the target class constructor returns (typically a fully-initialized instance). Any exceptions raised by that constructor propagate to the caller.
        - No Broker instance (of the original cls) is returned when a concrete adapter is selected — the caller receives the concrete adapter object.

## Raises:
    NotImplementedError:
        Raised when the parsed scheme is not one of the handled values (including the case of an empty or missing scheme).
    Any exception raised by the concrete class constructors:
        Any exceptions (TypeError, ValueError, redis library exceptions, network/socket errors, NameError if a class is not defined at runtime, etc.) raised during instantiation of the selected adapter are not caught here and will propagate.

## State Changes:
    Attributes READ:
        - None on the original Broker instance (self/cls attributes are not inspected or used).
        - Reads only the provided broker_url string via urlparse; no attributes on cls/self are accessed.

    Attributes WRITTEN:
        - None on the original Broker instance. This __new__ implementation does not mutate self or cls.
        - Side-effect attributes may be created/initialized on the returned concrete adapter instance (those are defined by the concrete classes, not by this method).

## Constraints:
    Preconditions:
        - broker_url must be a string or other object accepted by urllib.parse.urlparse such that urlparse(broker_url).scheme yields the intended scheme.
        - The scheme must be one of the explicitly supported values listed above; otherwise NotImplementedError will be raised.

    Postconditions:
        - On success, an instance of the corresponding adapter class is returned and any initialization performed by that concrete class has been executed (subject to that class's own behavior).
        - The original Broker class's __init__ is not run for a Broker instance because this method delegates construction to the concrete class constructor and returns that object.

## Side Effects:
    - Instantiates the selected concrete adapter class by calling its constructor. The concrete class constructor may perform side effects, such as:
        - Allocating objects (e.g., creating a redis.Redis client object),
        - Opening sockets or network connections (depending on concrete adapter behavior),
        - Performing I/O or library calls that can raise exceptions.
    - This method itself performs no I/O and does not perform network operations directly; all external interactions originate from the concrete adapter constructors invoked here.

### `flower.utils.broker.Broker.queues` · *method*

## Summary:
Abstract asynchronous entry point for broker-specific queue discovery. The base implementation raises NotImplementedError; subclasses must implement the lookup logic.

## Description:
This coroutine is intended to be overridden by concrete Broker subclasses to resolve one or more queue identifiers into broker-side queue metadata. The base method contains no logic and always raises NotImplementedError to force subclass implementations.

Why a separate method:
    - Queue discovery depends on broker protocol and administration APIs (e.g., RabbitMQ management API, Redis keyspace). Keeping this behavior in a dedicated overridable method isolates broker-specific I/O and parsing logic from callers.

Known callers:
    - Not specified in this class definition. Callers will invoke this coroutine on Broker instances to obtain queue information; repository-level call sites are not described here.

Why implement in subclasses:
    - The base class cannot provide a correct, general implementation because different broker types expose queue information via different mechanisms (HTTP endpoints, key scans, management APIs, etc.).

## Args:
    names (Iterable[str]):
        - Description: An iterable of queue identifiers to resolve.
        - Type: Any iterable whose elements are expected to be strings (list, tuple, set, generator).
        - Expected contents: queue names or broker-specific identifiers (implementation-dependent).
        - Notes: The base method does not validate types; concrete implementations should validate and raise TypeError or ValueError on malformed input if appropriate.

## Returns:
    - Base behavior: The base method does not return; it raises NotImplementedError.
    - Recommended convention for subclasses (guidance, not enforced):
        - Return type: list[dict] (or list-like sequence of mapping objects).
        - Each dict should include at minimum a 'name' key (str) identifying the broker-side queue record.
        - If no matching queues are found, return an empty list (do not return None).
    - Implementations are free to choose other return shapes but should document them clearly in their subclass.

## Raises:
    NotImplementedError:
        - Condition: Always raised by this base method.
    Implementation-specific exceptions (subclass responsibility):
        - Concrete implementations may raise I/O or client errors (e.g., redis.RedisError, HTTP client exceptions). Decide whether to propagate, wrap, or swallow such exceptions and document that decision in the subclass.

## State Changes:
    Attributes READ:
        - Base method: None.
        - Subclasses: may read broker-connection attributes (for example, a stored URL, a client instance, or a cache attribute). Any such reads should be documented in that subclass.
    Attributes WRITTEN:
        - Base method: None.
        - Subclasses: may update caches or diagnostic attributes (e.g., self._queues_cache). Such mutations must be documented by the subclass.

## Constraints:
    Preconditions:
        - The Broker object must be initialized so that any client/connection attributes used by the subclass (e.g., a Redis client or HTTP endpoint URL) are present and valid.
        - The caller should pass an iterable of strings; subclasses may validate and raise on invalid inputs.
    Postconditions:
        - The base method has no postconditions because it raises. Subclasses that implement the method should ensure the object remains usable after the call (do not leave client attributes in an invalid state on partial failure).

## Side Effects:
    - Base method: none (raises immediately).
    - Typical subclass side effects (implementation guidance):
        - Network I/O to broker management APIs or keyspace scans.
        - Logging of errors or diagnostic information.
        - Optional local caching of fetched queue metadata.
        - No broker-side mutation: this method should be read-only with respect to broker resources (it should not create/delete queues).

## Implementation guidance (for subclass authors):
    - Make the coroutine asynchronous (async def) to allow non-blocking I/O.
    - Validate 'names' early and raise TypeError/ValueError for clearly invalid inputs.
    - Prefer returning a list (possibly empty) rather than None for consistency with typical callers.
    - Document any fields included in returned dicts (e.g., 'name', 'vhost', 'messages') in the subclass docstring.
    - Decide and document error-handling policy: whether to log and return [] on transient errors versus propagating exceptions.

## `flower.utils.broker.main` · *function*

## Summary:
Asynchronously reads command-line arguments to construct a Broker, queries a single named queue, and prints any returned queue metadata to stdout.

## Description:
This coroutine implements a minimal CLI-style orchestration that:
- Reads up to three optional values from sys.argv (broker_url, queue_name, http_api).
- Constructs a Broker via the Broker factory using the broker_url and http_api.
- Awaits the Broker.queues coroutine with a single-element list containing queue_name.
- Prints the result to stdout only when the returned value is truthy.

Known callers:
- No explicit callers are defined in the repository for this coroutine. It is intended to be executed by an asyncio runner (e.g., asyncio.run(main())) or invoked programmatically in tests or small utilities.

Reason for extraction:
- Encapsulates CLI-style argument defaults and a short async orchestration flow separate from Broker implementations and test code.
- Keeps argument parsing and top-level orchestration in one place so Broker implementations remain focused on backend-specific I/O and parsing.

## Args:
This function takes no parameters and reads inputs from sys.argv. Expected positions and defaults:

- broker_url (str) — sys.argv[1] if present; otherwise default 'amqp://'
  - Meaning: URL string used by Broker to select a concrete implementation (Broker inspects the URL scheme).
  - Constraint: If the URL scheme is unsupported, Broker.__new__ raises NotImplementedError.

- queue_name (str) — sys.argv[2] if present; otherwise default 'celery'
  - Meaning: Single queue identifier; main passes [queue_name] to Broker.queues.

- http_api (str) — sys.argv[3] if present; otherwise default 'http://guest:guest@localhost:15672/api/'
  - Meaning: HTTP API base URL forwarded to Broker constructor. Concrete Broker implementations decide whether and how to use it.

Interdependencies:
- http_api has no intrinsic effect in this function; its interpretation depends entirely on the concrete Broker chosen by Broker(broker_url, http_api=...).

## Returns:
- None (implicitly). The coroutine does not return a value.
- Observable effect: prints the value returned by Broker.queues([queue_name]) to stdout if that value is truthy. If the returned value is falsy (for example an empty list), nothing is printed.

## Raises:
This function does not explicitly raise exceptions, but the following can propagate:

- NotImplementedError:
  - Trigger: Broker.__new__ raises when broker_url has an unsupported scheme.

- Errors from Broker construction:
  - Trigger: Any exception raised during constructing the Broker (ValueError, ImportError, TypeError, etc.) will propagate.

- Errors while awaiting broker.queues:
  - Trigger: Any exception thrown by the asynchronous Broker.queues implementation (network errors, client library exceptions, ValueError/TypeError from invalid inputs) will propagate.

- Note: This function guards against IndexError when reading sys.argv by checking len(sys.argv) before indexing.

## Constraints:
Preconditions:
- An asyncio event loop must be present to await this coroutine (e.g., call via asyncio.run(main()) or from within an existing loop).
- Broker and the required concrete broker implementations must be importable and functional in the runtime environment.
- sys.argv values (if provided) should be valid strings appropriate for the target Broker implementation.

Postconditions:
- If Broker.queues returns a truthy value, that value has been written to stdout via print.
- The coroutine itself does not close or clean up the Broker; any necessary cleanup must be performed by the concrete Broker implementation or by the caller (not by this function).

## Side Effects:
- stdout: prints the queues object when truthy using print(queues).
- Indirect network I/O: Broker construction and Broker.queues may perform network requests (HTTP to management APIs, Redis connections, etc.); those side effects occur inside Broker implementations, not in main.
- No file writes, no explicit global state mutation, and no explicit process exit calls are performed by this function.

## Control Flow:
flowchart TD
    Start([Start / asyncio runner calls main()]) --> ParseArgs{len(sys.argv) > 1?}
    ParseArgs -->|yes| SetBrokerURL[broker_url = sys.argv[1]]
    ParseArgs -->|no| DefaultBrokerURL[broker_url = 'amqp://']
    SetBrokerURL --> CheckQueueArg{len(sys.argv) > 2?}
    DefaultBrokerURL --> CheckQueueArg
    CheckQueueArg -->|yes| SetQueueName[queue_name = sys.argv[2]]
    CheckQueueArg -->|no| DefaultQueueName[queue_name = 'celery']
    SetQueueName --> CheckHTTPArg{len(sys.argv) > 3?}
    DefaultQueueName --> CheckHTTPArg
    CheckHTTPArg -->|yes| SetHTTPAPI[http_api = sys.argv[3]]
    CheckHTTPArg -->|no| DefaultHTTPAPI[http_api = 'http://guest:guest@localhost:15672/api/']
    SetHTTPAPI --> CreateBroker[broker = Broker(broker_url, http_api=http_api)]
    DefaultHTTPAPI --> CreateBroker
    CreateBroker --> AwaitQueues[queues = await broker.queues([queue_name])]
    AwaitQueues --> IsTruthy{queues is truthy?}
    IsTruthy -->|yes| PrintQueues[print(queues)]
    IsTruthy -->|no| End([End])

## Examples:
1) Programmatic invocation using asyncio.run with defaults:
    - Description: Run the coroutine with default broker_url, queue_name, and http_api.
    - Pattern:
      import sys, asyncio
      sys.argv = ["progname"]  # leave defaults in place
      asyncio.run(main())

2) Programmatic invocation with explicit arguments:
    - Description: Query a specific queue on a specific broker URL and HTTP API.
    - Pattern:
      import sys, asyncio
      sys.argv = ["progname", "amqp://", "myqueue", "http://guest:guest@localhost:15672/api/"]
      asyncio.run(main())

3) Handling exceptions when invoking main():
    - Description: Show how a caller might catch and handle errors propagated by Broker construction or queues.
    - Pattern:
      import sys, asyncio
      sys.argv = ["progname", "redis://localhost:6379/0", "myqueue"]
      try:
          asyncio.run(main())
      except NotImplementedError as exc:
          # Unsupported scheme or Broker factory error
          print("Unsupported broker scheme:", exc)
      except Exception as exc:
          # Network or client errors from Broker.queues
          print("Failed to fetch queues:", exc)

Notes:
- This coroutine is intentionally minimal and delegates validation, network I/O, and broker-specific error-handling to Broker and its concrete implementations. Consumers requiring structured output, retries, or cleanup should wrap this coroutine with additional logic.

