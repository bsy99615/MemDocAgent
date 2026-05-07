# `app.py`

## `flower.app.rewrite_handler` · *function*

## Summary:
Prepends a URL prefix to a single Tornado route entry, returning a new tornado.web.url (URLSpec) when given a url instance or a (pattern, handler) tuple when given a simple sequence.

## Description:
This helper centralizes the small but error-prone task of applying a common mount prefix (namespace, API version, mount point) to individual route entries before they are registered with a Tornado application.

Known callers and context:
- Intended to be used during application initialization when constructing the handlers list passed to tornado.web.Application(...). In this file, the function is used in the same context as the imported handlers (from urls import handlers) — i.e., when iterating over a collection of route specifications and applying a shared prefix.
- The function itself is a low-level utility; callers typically map it over an iterable of routes and then pass the transformed list to Tornado's Application or add the transformed routes to a sub-application.

Why this is a separate function:
- Ensures consistent prefixing for both tornado.web.url-based route specifications and plain (pattern, handler) tuples.
- Avoids duplicating string-manipulation logic across application setup code and makes the behavior easy to test.

## Args:
    handler (tornado.web.url | tuple | list)
        - If a tornado.web.url instance (the url symbol imported from tornado.web), the function expects that object to expose:
            * regex.pattern (str) — the original route regex/pattern string
            * handler_class — the handler class or callable
            * kwargs (dict) — keyword arguments to pass to the handler
            * name (str|None) — optional route name
        - Otherwise, handler must be a sequence (tuple or list) with at least two elements:
            * handler[0] (str): the route pattern (may start with or without a leading "/")
            * handler[1]: handler class or callable
        - Other shapes will lead to AttributeError or IndexError as described in Raises.
    url_prefix (str)
        - The prefix to prepend. Leading/trailing slashes are trimmed via url_prefix.strip("/") before concatenation.
        - Must be string-like (implement .strip). Passing None or non-string-like objects will raise an AttributeError.

## Returns:
    tornado.web.url | tuple
        - For a tornado.web.url input: returns a new url(...) constructed with:
            * pattern = "/" + url_prefix.strip("/") + handler.regex.pattern
            * handler_class = handler.handler_class
            * kwargs = handler.kwargs
            * name = handler.name
        - For a (pattern, handler) sequence: returns a tuple:
            ("/" + url_prefix.strip("/") + handler[0], handler[1])
        - Important notes on returned pattern:
            * The function always prefixes the result with a single leading "/" produced by the format string.
            * If handler.regex.pattern or handler[0] already begins with "/", the final pattern will include that slash immediately after the prefix (resulting in "/prefix/…").
            * If handler[0] does not begin with "/", the final pattern will be concatenated directly (resulting in "/prefixpattern"); callers should normalize patterns if a separator is required.

## Raises:
    AttributeError
        - If url_prefix has no .strip method (e.g., url_prefix is None or not string-like).
        - If handler is treated as a url instance but lacks expected attributes like regex or handler_class.
    IndexError
        - If handler is a sequence with fewer than 2 elements so handler[0] or handler[1] cannot be accessed.
    TypeError
        - If handler[0] is not a string-like object and string concatenation with the prefix fails (this typically surfaces as a TypeError during format/concatenation).

## Constraints:
Preconditions:
    - url_prefix should be a string (or implement .strip) and not None.
    - handler must be either:
        * a url instance from tornado.web with the expected attributes; or
        * a sequence (tuple/list) of at least two elements where the first element is the pattern string.
Postconditions:
    - Returns either a tornado.web.url (URLSpec) or a (pattern, handler) tuple with the prefix applied.
    - The input handler is not mutated; a new object/tuple is returned.

## Side Effects:
    - No external I/O, logging, or global state mutation.
    - Purely constructs and returns a new route spec; registration remains the caller's responsibility.

## Control Flow:
flowchart TD
    A[Start: rewrite_handler(handler, url_prefix)] --> B{isinstance(handler, url)?}
    B -- Yes --> C[pattern = "/" + url_prefix.strip("/") + handler.regex.pattern]
    C --> D[Return url(pattern, handler.handler_class, handler.kwargs, handler.name)]
    B -- No --> E[pattern = "/" + url_prefix.strip("/") + handler[0]]
    E --> F[Return (pattern, handler[1])]
    D --> G[End]
    F --> G[End]

## Examples:
Example 1 — url instance with leading slash in pattern:
    - Inputs:
        * handler is a url-like object whose regex.pattern == "/login"
        * handler.handler_class == LoginHandler
        * handler.kwargs == {}
        * handler.name == "login"
        * url_prefix == "api/v1"
    - Behavior:
        * url_prefix.strip("/") -> "api/v1"
        * pattern produced -> "/api/v1/login"
    - Return:
        * a new url object with pattern "/api/v1/login", same handler_class/kwargs/name.

Example 2 — tuple input where pattern has a leading slash:
    - Inputs:
        * handler == ("/health", HealthHandler)
        * url_prefix == "status"
    - Behavior & Return:
        * pattern produced -> "/status/health"
        * returned tuple -> ("/status/health", HealthHandler)

Example 3 — tuple input where pattern lacks a leading slash:
    - Inputs:
        * handler == ("health", HealthHandler)
        * url_prefix == "status"
    - Behavior & Return:
        * pattern produced -> "/statushealth" (no separator inserted)
        * returned tuple -> ("/statushealth", HealthHandler)
    - Recommendation:
        * Normalize handler patterns (add leading "/") when constructing routes if you expect separators between prefix and pattern.

Example 4 — empty prefix:
    - Inputs:
        * handler == ("/metrics", MetricsHandler)
        * url_prefix == ""
    - Behavior & Return:
        * url_prefix.strip("/") -> ""
        * pattern produced -> "//metrics" (leading "/" from format + handler pattern)
        * returned tuple -> ("//metrics", MetricsHandler)
    - Recommendation:
        * For predictable results, ensure url_prefix is either None (handled elsewhere) or a normalized string; callers can guard against empty prefix if "//" is undesirable.

## `flower.app.Flower` · *class*

*No documentation generated.*

### `flower.app.Flower.__init__` · *method*

## Summary:
Initializes the Flower application instance: configures route handlers, stores options, sets up the Tornado I/O loop and default SSL options, instantiates or attaches a Celery app, creates and registers a thread/executor pool, and constructs Inspector and Events helper objects; leaves the instance in a ready-but-not-started state (self.started == False).

## Description:
This constructor is invoked when a Flower application object is created (i.e., when code calls Flower(...)). It runs during application initialization to prepare all runtime components needed before the application is started or the HTTP server is bound.

Known callers and context:
- Any code that instantiates the Flower class (application entrypoints, test harnesses, or scripts that create and run the web UI/backend).
- Typical lifecycle stage: application construction/bootstrapping — before calling methods that start the HTTP server or event loop.

Why this is a separate method:
- As the class constructor, __init__ centralizes initialization logic that must run exactly once per instance: preparing route handlers, dependency injection (Celery app and Events/Inspector), and configuring the runtime executor and I/O loop. Keeping this logic in __init__ avoids duplication and ensures all required attributes exist before the application is used.

## Args:
    options (object | None)
        - Optional configuration object. If provided, it is stored to self.options.
        - Expected attributes accessed in this method: url_prefix, inspect_timeout, db, persistent, state_save_interval, enable_events, max_workers, max_tasks.
        - If None, the imported default_options is used.
    capp (celery.Celery | None)
        - Optional Celery application instance. If None, a new celery.Celery() instance is created and assigned to self.capp.
    events (Events | None)
        - Optional pre-constructed Events instance. If None, an Events(...) instance is constructed using self.capp and fields from self.options.
    io_loop (tornado.ioloop.IOLoop | None)
        - Optional Tornado I/O loop to use. If None, ioloop.IOLoop.instance() is used.
    **kwargs
        - Additional keyword arguments forwarded to the superclass __init__ via super().__init__(**kwargs).
        - This method will update kwargs with handlers=handlers before calling super().__init__.
        - Recognized optional key used here: 'ssl_options' (read from kwargs to set self.ssl_options).

## Returns:
    None
    - As a Python constructor, __init__ does not return a value. The method's purpose is to initialize instance state.

## Raises:
    NameError
        - If the module-global default_handlers name is not defined when this function references it.
    AttributeError
        - If options is provided but lacks an expected attribute used here (e.g., options.url_prefix, options.inspect_timeout, options.db, etc.).
        - If kwargs is not a mapping supporting .get (very unlikely in normal use).
    TypeError
        - If self.pool_executor_cls is not callable (so calling self.pool_executor_cls(max_workers=...) fails).
        - If self.max_workers is not a valid integer accepted by the pool executor implementation.
    Any exception raised by:
        - celery.Celery() constructor,
        - self.capp.loader.import_default_modules(),
        - Inspector(...) or Events(...) constructors,
        - ioloop.IOLoop.instance() or io_loop.set_default_executor(...)
      These will propagate out of __init__ as-is.

## State Changes:
Attributes READ:
    - self.pool_executor_cls (class attribute or previously set attribute) — used to construct the executor.
    - self.max_workers (class attribute or previously set attribute) — passed as max_workers to the executor.
    - self.options (the attribute is assigned early in this method and then read later for inspect_timeout, db, persistent, state_save_interval, enable_events, max_workers, max_tasks).
    - kwargs (local mapping) — read to get 'ssl_options' and later forwarded to super().__init__.
    - module globals referenced: default_handlers and rewrite_handler (these are read to prepare the handlers list).
Attributes WRITTEN:
    - self.options: set to the provided options or default_options.
    - self.io_loop: set to the provided io_loop or ioloop.IOLoop.instance().
    - self.ssl_options: set from kwargs.get('ssl_options', None).
    - self.capp: set to provided capp or a newly constructed celery.Celery() instance.
    - self.executor: set to the result of calling self.pool_executor_cls(max_workers=self.max_workers).
    - self.inspector: set to an Inspector instance constructed with (self.io_loop, self.capp, inspect_timeout_seconds).
    - self.events: set to the provided events or a new Events(...) instance configured from self.options and self.io_loop.
    - self.started: set to False.

## Constraints:
Preconditions:
    - The module-level name default_handlers must exist and be an iterable of route specs at the time __init__ is executed. If options is provided and options.url_prefix is truthy, rewrite_handler must be available and callable.
    - The instance (or class) must expose pool_executor_cls and max_workers before __init__ calls them (these are read in this method). Typically these are class-level defaults or set by subclassing.
    - options (if provided) must provide the attributes referenced above (url_prefix, inspect_timeout, db, persistent, state_save_interval, enable_events, max_workers, max_tasks) to avoid AttributeError.
Postconditions:
    - The Flower instance has:
        * self.options set (never None after __init__, because default_options is used when options is None),
        * self.io_loop set and its default executor set to self.executor,
        * self.capp set and its default modules imported via loader.import_default_modules(),
        * self.executor allocated via pool_executor_cls,
        * self.inspector and self.events initialized,
        * self.started == False ready to be switched to True by the startup logic elsewhere.

## Side Effects:
    - If capp is not provided, a new celery.Celery() is constructed and assigned to self.capp; calling loader.import_default_modules() on that app will import Celery task modules and thereby may execute module-level code in those modules.
    - Allocating the executor (self.pool_executor_cls(...)) may allocate threads or thread pools depending on the executor implementation.
    - Calling self.io_loop.set_default_executor(self.executor) mutates the provided/global I/O loop's default executor state.
    - Constructing Inspector(...) and Events(...) will execute their constructors; these constructors may schedule timers, background callbacks, or I/O depending on their implementations (those behaviors are defined by Inspector and Events).
    - No direct file or network I/O is performed by this __init__ implementation itself beyond what invoked constructors do (e.g., what celery.Celery(), Inspector, or Events may perform).

### `flower.app.Flower.start` · *method*

## Summary:
Starts the Flower application runtime: initializes event processing, opens network listeners (TCP port or UNIX socket), marks the app as started, refreshes worker state, and begins the I/O loop.

## Description:
This method performs the ordered startup sequence required to run the Flower web application and its background event processing. It is responsible for:
- Starting the Events subsystem attached to the Celery app.
- Creating a network listener for incoming HTTP requests either by calling the Tornado Application.listen (TCP/IP) or by creating an HTTPServer and attaching a bound UNIX socket (when options.unix_socket is set).
- Marking the Flower instance as started.
- Triggering a workers-state refresh by calling update_workers().
- Starting the Tornado I/O loop to begin handling requests and background tasks.

Known callers and lifecycle stage:
- Repository search found no explicit internal callers of Flower.start. In typical deployments this method is called once during application bootstrap (for example, from a main function, CLI entrypoint, or a process manager) to transition the Flower instance from configured->running state.
- Invocation context: startup/bootstrap stage of the Flower process, before the process begins servicing HTTP requests or scheduling background inspections.

Why this is a separate method:
- The method centralizes the startup sequence and side-effectful operations (starting events, binding sockets, starting the event loop). Keeping these together prevents duplication and makes it easy to call/override the application start behavior from different entrypoints or tests.

## Args:
None

## Returns:
None

## Raises:
- The method itself does not explicitly raise exceptions. However, underlying calls it invokes may raise exceptions from their respective libraries. Examples visible from the code:
    - Errors propagated from self.events.start() (Events implementation).
    - Errors propagated by self.listen(...) (Tornado Application.listen) when attempting to bind a TCP socket.
    - OSError or related exceptions from bind_unix_socket(self.options.unix_socket, mode=0o777) if the UNIX socket path cannot be created or permission/FS errors occur.
    - Errors propagated from self.io_loop.start() (Tornado IOLoop.start).
Note: The code does not catch these exceptions; they will propagate to the caller.

## State Changes:
Attributes READ:
- self.events (used to call start())
- self.options (accessed for unix_socket, port, address, xheaders)
- self.ssl_options (read and forwarded into listen call)
- self.io_loop (read to call start())
- self.update_workers (method called; reads within that method are not listed here)

Attributes WRITTEN:
- self.started (set to True)

Other observable interactions with object state:
- self.listen(...) is invoked (inherited from tornado.web.Application) and may register listening sockets within the application/server state.
- When options.unix_socket is truthy, an HTTPServer is instantiated and server.add_socket(socket) is called (attaching the bound UNIX socket to the server).

## Constraints:
Preconditions:
- self.events, self.options, and self.io_loop must be initialized (this is satisfied by Flower.__init__, which sets these attributes).
- options.port/options.address (for TCP) or options.unix_socket (for UNIX socket) must be correctly configured according to the intended listen mode.
- If using UNIX socket mode, the process must have permissions to create/bind the specified unix socket path (filesystem permissions and parent directories must be present).

Postconditions:
- After successful return (i.e., if no exception was raised):
    - self.started is True.
    - The application is listening for HTTP requests on either the configured TCP port/address (via self.listen) or on the bound UNIX socket (via HTTPServer.add_socket).
    - The Events subsystem has been started.
    - update_workers() has been invoked, initiating a workers inspection/refresh.
    - The Tornado I/O loop (self.io_loop) is running and will process I/O and scheduled callbacks.

## Side Effects:
- I/O / OS interactions:
    - Binds a TCP socket via Tornado's listen(...) when options.unix_socket is falsy.
    - If options.unix_socket is truthy:
        - Binds a UNIX domain socket at options.unix_socket with file mode 0o777 (explicitly set in the call).
        - Creates a tornado.httpserver.HTTPServer and attaches the bound socket via add_socket(...).
    - Starts background event processing by calling self.events.start().
    - Starts the Tornado I/O loop by calling self.io_loop.start(), which blocks the current thread until the loop is stopped.
- External service calls:
    - Delegates to underlying frameworks (Tornado, Events subsystem). Any networking, file-system, or event-loop errors originate from those layers.
- Mutations outside self:
    - The code may create OS-level socket resources (file descriptors); when using UNIX sockets, a socket file may be created on the filesystem.
    - The HTTPServer instance is instantiated locally and attached to the event loop / process; it is not stored on self in this method.

## Implementation notes / edge cases visible in code:
- The branch for UNIX sockets explicitly sets the socket file mode to 0o777; callers should be aware of this permission semantics.
- The method does not perform any exception handling: any exception from underlying operations will propagate to the caller and prevent self.started from being set (unless the exception occurs after the assignment).
- The I/O loop is started last; because io_loop.start() typically blocks, code after this call will not execute until the loop stops.

### `flower.app.Flower.stop` · *method*

## Summary:
Stops the running Flower application: halts event processing, shuts down the thread executor, stops the Tornado I/O loop, and marks the application as not started.

## Description:
- Known callers and lifecycle context:
    - No direct callers of this method are present in the provided source snippet. It is intended to be invoked during application shutdown — for example by a signal handler, a test harness, or an external process supervisor — to perform an orderly shutdown of resources started by Flower.start().
    - This method complements start(), which sets up resources (events, executor, I/O loop) and sets self.started = True; stop() centralizes the teardown logic performed when the application stops running.

- Why this is a separate method:
    - Encapsulates and centralizes shutdown logic so teardown is consistent and reusable across different shutdown triggers (signals, tests, graceful restarts).
    - Keeps start/stop lifecycle responsibilities separate and readable (start initializes and begins services; stop cleanly shuts them down).

## Args:
    None

## Returns:
    None
    - The method performs actions and returns no value. If self.started is False the method is a no-op and returns None immediately.

## Raises:
    None explicitly raised by this method.
    - The method does not raise exceptions itself; however, exceptions raised by delegated calls (self.events.stop(), self.executor.shutdown(...), self.io_loop.stop()) will propagate to the caller if they occur.

## State Changes:
- Attributes READ:
    - self.started (bool) — used to determine whether shutdown actions should run.
    - self.events (Events) — the Events instance whose stop() method is invoked.
    - self.executor (concurrent.futures.ThreadPoolExecutor) — the executor which is shut down.
    - self.io_loop (tornado.ioloop.IOLoop) — the I/O loop which is stopped.
- Attributes WRITTEN:
    - self.started (bool) — set to False when a shutdown occurs.

## Constraints:
- Preconditions:
    - The Flower instance must be initialized (its __init__ must have run) so that self.events, self.executor, self.io_loop, and self.started exist and have the expected types.
    - The method performs actions only when self.started is truthy. If self.started is False, the method does nothing.
- Postconditions:
    - If the method performed shutdown (i.e., self.started was True on entry):
        - self.events.stop() has been invoked.
        - self.executor.shutdown(wait=False) has been invoked (executor shutdown initiated; threads may still be terminating in background).
        - self.io_loop.stop() has been invoked (Tornado I/O loop is requested to stop).
        - self.started is set to False.
    - If self.started was False on entry, no attributes are modified.

## Side Effects:
- Calls external/owned components' lifecycle methods:
    - Invokes self.events.stop() — stops the Events subsystem (implementation-specific side effects such as stopping background polling, persisting state, or closing DB connections are delegated to Events).
    - Calls self.executor.shutdown(wait=False) — initiates shutdown of the ThreadPoolExecutor, preventing new tasks from being scheduled; existing worker threads may continue until they exit.
    - Calls self.io_loop.stop() — requests the Tornado I/O loop to stop processing; this affects all scheduled callbacks and I/O handled by that loop.
- Logging:
    - Emits debug logs via the logging module indicating the start of shutdown steps ("Stopping executors...", "Stopping event loop...").
- No direct file, network, or database operations are implemented in this method itself; such operations may occur indirectly via the invoked components' stop/shutdown methods.

### `flower.app.Flower.transport` · *method*

## Summary:
Return the broker transport driver type used by the Flower instance's Celery app, or None when the driver type is not available; does not modify the object's state.

## Description:
Known callers:
    - No direct callers were found in the provided Flower class memory snapshot. This property is typically queried by UI components, logging, or diagnostic routines to adjust behavior or display broker information in the application lifecycle after the Flower instance has been initialized.

Context / lifecycle stage:
    - Invoked at runtime after Flower has been constructed and its self.capp (Celery application) has been initialized. Useful during server startup, inspection, or when rendering status pages that need to display or branch on the underlying broker/transport type.

Why this is a separate property:
    - Encapsulates the logic to locate the broker driver type in one place so callers don't duplicate the chain of attribute accesses (self.capp.connection().transport.driver_type). Keeps call sites simpler and centralizes error semantics and documentation for retrieving the transport driver type.

## Args:
    - None

## Returns:
    - str | None
        - The value of the transport object's 'driver_type' attribute (commonly a string identifying the broker driver, e.g., 'amqp', 'redis', etc.).
        - Returns None if the transport object exists but does not have a 'driver_type' attribute.
        - No other return values are produced by this expression.

## Raises:
    - AttributeError
        - If self.capp is not an object exposing a callable connection() method, or if connection() returns an object missing the 'transport' attribute, the attribute access self.capp.connection().transport will raise AttributeError (this exception is not caught by the property).
    - Any exception raised by self.capp.connection()
        - If the underlying Celery app's connection() method raises (e.g., connection setup errors), that exception will propagate.

## State Changes:
    Attributes READ:
        - self.capp
        - result of self.capp.connection()
        - (implicitly) the transport object returned by connection().transport
    Attributes WRITTEN:
        - None (this property only reads state; it does not mutate the Flower instance)

## Constraints:
    Preconditions:
        - self.capp must be initialized (Flower.__init__ sets self.capp to the provided celery app or a new celery.Celery()).
        - The object returned by self.capp.connection() should expose a 'transport' attribute to avoid AttributeError.
    Postconditions:
        - No mutation to self or external objects is performed.
        - The caller receives either a string identifying the driver type or None (if transport exists but lacks 'driver_type').

## Side Effects:
    - None within Flower itself: no I/O, no network calls, and no modifications to objects outside self are performed by this property.
    - Note: calling self.capp.connection() may involve Celery internals that lazily establish connections or perform lookups; any side effects originating inside that method are not produced by this property itself but will be observed as part of invoking connection().

### `flower.app.Flower.workers` · *method*

## Summary:
Return the Inspector's in-memory mapping of workers and their most recent inspection data; this is a direct, live reference to the inspector's state.

## Description:
This accessor exposes the Inspector.workers attribute that the Flower instance creates during initialization. It does not perform inspection or modify state — it only returns the current in-memory mapping maintained by the Inspector.

Lifecycle and usage context:
- Flower.__init__ creates self.inspector = Inspector(...), and Flower.start calls self.update_workers() which invokes Inspector.inspect to initiate background inspection. Thus, inspection data is typically populated after Flower.start runs and the I/O loop processes Inspector callbacks.
- Typical consumers are code that needs to read current worker state (for example, web request handlers, UI rendering code, or monitoring endpoints). These consumers are not shown in the provided snippet; this statement is describing intended use, not a direct code reference.

Why a dedicated property:
- Provides a simple, discoverable way for other parts of the application to access the inspector's worker state without importing or interacting with the Inspector directly.

## Args:
This property takes no arguments.

## Returns:
collections.defaultdict[str, dict]
- The exact object returned is the Inspector.workers attribute, which Inspector.__init__ constructs as collections.defaultdict(dict).
- Keys: worker identifiers as produced by celery.control.inspect (typically strings, but exact type is determined by Celery).
- Values: dictionaries containing the latest inspection responses per method and a 'timestamp' key set by Inspector._on_update; method keys correspond to Inspector.methods (e.g., 'stats', 'active_queues', 'registered', 'scheduled', 'active', 'reserved', 'revoked', 'conf').
- Edge cases:
    - If no inspection results exist, the defaultdict will be empty.
    - The returned object is the same in-memory mapping held by the Inspector; it is not a copy.

## Raises:
- The accessor itself does not raise application-specific exceptions.
- An AttributeError would occur if self.inspector is not present on the Flower instance. In normal use this should not happen because Flower.__init__ assigns self.inspector.

## State Changes:
Attributes READ:
- self.inspector
- self.inspector.workers

Attributes WRITTEN:
- None. The accessor does not modify Flower or Inspector state.

## Constraints:
Preconditions:
- Flower must have been initialized such that self.inspector exists (Flower.__init__ performs this).
- To observe populated worker data, Inspector.inspect must have run and Inspector._on_update callbacks must have executed (Flower.start → update_workers initiates this process).

Postconditions:
- The Flower instance remains unchanged.
- The caller receives a live reference to the Inspector.workers mapping which may be updated concurrently by Inspector code.

## Side Effects:
- This accessor performs no I/O and makes no external service calls.
- Returning a direct reference means that if the caller mutates the returned mapping (e.g., alters entries, deletes keys), those mutations affect the Inspector's in-memory state and are visible to other consumers and Inspector logic.

### `flower.app.Flower.update_workers` · *method*

## Summary:
Requests an asynchronous (re)inspection of workers via the Inspector and returns the list of futures representing those scheduled inspection tasks; the method itself does not block and does not directly mutate Flower state.

## Description:
- Known callers and context:
    - This file does not declare explicit call sites for update_workers. It is provided as the Flower application API for other parts of the system (for example, web handlers or background tasks) to trigger a fresh inspection of worker state.
    - Typical usage: invoke when an up-to-date snapshot of Celery workers is required (e.g., before rendering a worker status page); callers are expected to handle the returned futures if they need to wait for completion.
- Why this is a standalone method:
    - The method is a deliberate delegation to the Inspector instance to keep the Flower class decoupled from inspection scheduling details. Encapsulating this delegation simplifies testing and makes it trivial to override or mock how inspections are requested.

## Args:
    workername (str | None): Optional name of a single worker to target.
        - If a string is provided, the Inspector will direct its Celery control inspect to that single worker (Inspector uses destination=[workername]).
        - If None (default), the Inspector will target all workers (destination is None).

## Returns:
    list[object]: A list whose length equals len(self.inspector.methods). Each element is the object returned by self.inspector.io_loop.run_in_executor for a scheduled inspection invocation (typically an awaitable/future returned by the event loop's run_in_executor).
    - Each future corresponds to one inspect method (Inspector.methods: ('stats', 'active_queues', 'registered', 'scheduled', 'active', 'reserved', 'revoked', 'conf')).
    - The method returns immediately with the list of futures; it does not wait for those tasks to complete.
    - Edge-case values:
        - A scheduled task may complete with no result (None) if the underlying Inspector._inspect observes an error or returned None.
        - Exceptions raised inside scheduled tasks will not be raised by this method; they will surface when the returned futures are awaited or inspected.

## Raises:
    AttributeError: If the Flower instance has no attribute inspector (accessing self.inspector will raise).
    Any synchronous exception raised by accessing self.inspector.inspect will propagate (unlikely in normal setup).
    Exceptions from the scheduled tasks do not raise here; they are delivered to the returned futures.

## State Changes:
- Attributes READ:
    - self.inspector
    - (implicitly) self.inspector.methods and self.inspector.io_loop as used by Inspector.inspect
- Attributes WRITTEN:
    - None on the Flower instance itself.
    - Indirect asynchronous writes: the scheduled Inspector tasks may call Inspector._on_update, which mutates self.inspector.workers by setting per-worker entries:
        - For each worker and method that returns data, Inspector._on_update stores response under inspector.workers[worker][method] and sets inspector.workers[worker]['timestamp'] to the current time.

## Constraints:
- Preconditions:
    - self.inspector must be present and implement an inspect(workername) method (the method is typically an instance of the Inspector class).
    - Inspector.io_loop must support run_in_executor and be operational (the event loop must be running or able to schedule tasks); otherwise the returned futures may never complete.
- Postconditions:
    - The call returns a list with one future per item in self.inspector.methods.
    - Background inspection tasks are scheduled on the Inspector's io_loop; when those tasks complete successfully, Inspector.workers will be updated asynchronously for any workers that returned data.

## Side Effects:
    - Schedules multiple background tasks via the Inspector (which uses io_loop.run_in_executor to run Inspector._inspect concurrently for each inspect method).
    - Indirectly triggers network/control-plane calls (Celery control.inspect.*) inside the scheduled tasks; these are performed inside the background tasks and not by this method directly.
    - No synchronous I/O or network calls are performed by update_workers itself.

