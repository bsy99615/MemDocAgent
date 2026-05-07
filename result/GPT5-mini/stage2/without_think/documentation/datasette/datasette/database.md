# `database.py`

## `datasette.database.Database` · *class*

*No documentation generated.*

### `datasette.database.Database.__init__` · *method*

## Summary:
Initializes a Database object by storing the provided Datasette parent and configuration flags and preparing all instance state fields used later when the database is opened or used.

## Description:
This constructor sets up the Database instance's identity and runtime fields but does not open or allocate any SQLite connections or start background threads. It is invoked when a new Database object is created (typically during application startup or when a plugin/extension registers a new database) as the first step in the Database object's lifecycle. The resulting object is ready to be further initialized by other methods (for example, methods that open connections, populate cached metadata, or start write threads).

This logic exists as its own method because it establishes the canonical, minimal in-memory representation of a Database (its configuration and placeholder attributes) separate from heavier initialization (I/O, connection setup, metadata collection). Separating this setup makes object creation lightweight and clarifies responsibilities: __init__ defines state; other methods perform side-effectful initialization.

Known callers and context:
- No exact callers are available in the provided source snippet. In the application this belongs to, Database instances are typically instantiated by the top-level application loader or a Datasette manager when discovering or registering databases. The call happens during construction/registration time — before opening database connections or starting background write threads.

## Args:
    ds (object): The parent Datasette instance (keeps a reference to the owning application). Required.
    path (str | None): Filesystem path to the SQLite database file, or None for no file backing (for example for in-memory databases). Defaults to None.
    is_mutable (bool): Whether the database should be considered writable by default. Defaults to True.
    is_memory (bool): Whether the database is an in-memory database. Defaults to False. This flag may be overridden by memory_name.
    memory_name (str | None): If provided, a logical name for an in-memory database. When not None, the constructor forces is_memory to True. Defaults to None.

## Returns:
    None

## Raises:
    This constructor does not raise exceptions. It performs only attribute assignments and simple boolean logic.

## State Changes:
Attributes READ:
    self.memory_name (read to determine whether to force is_memory True)

Attributes WRITTEN:
    self.name = None
    self.route = None
    self.ds = ds
    self.path = path
    self.is_mutable = is_mutable
    self.is_memory = is_memory (may be set True if memory_name is not None)
    self.memory_name = memory_name
    self.cached_hash = None
    self.cached_size = None
    self._cached_table_counts = None
    self._write_thread = None
    self._write_queue = None
    self._read_connection = None
    self._write_connection = None
    self._all_file_connections = []  (a new empty list instance per Database)

## Constraints:
Preconditions:
    - Caller should provide a valid parent Datasette object for the ds parameter (no runtime checks are performed).
    - No other attributes on the instance are assumed initialized prior to this call.

Postconditions:
    - The instance has all documented attributes present (listed above) and initialized to either the supplied values or sensible defaults (mostly None).
    - If memory_name was provided (not None), self.is_memory is guaranteed to be True regardless of the is_memory argument.
    - _all_file_connections is an empty list unique to this instance.

## Side Effects:
    - No I/O is performed.
    - No database connections are opened and no threads are started here.
    - The ds reference is stored (a reference to an external object is held), but no mutation of ds occurs.

### `datasette.database.Database.cached_table_counts` · *method*

## Summary:
Returns a cached mapping of table names to row counts for this database, lazily populated from the Datasette instance's inspect_data and stored on the Database object.

## Description:
This property provides a lazy, read-only view of pre-computed table counts when available from the Datasette instance metadata. Known callers:
- Database.table_counts: checks this property to return cached counts for non-mutable databases without executing COUNT(*) queries.
- External code that needs quick access to table counts for display or metadata without triggering database queries.

Typical lifecycle/context:
- Used during metadata rendering or endpoints where Datasette has pre-computed inspection data (inspect_data) for databases.
- Invoked when a caller needs cached counts (e.g., to avoid expensive live COUNT(*) queries on large, immutable databases).

Why a separate property:
- Encapsulates lazy-loading and caching logic in one place so callers can access counts uniformly without duplicating checks for inspect_data, the database name, or the cache attribute.
- Keeps table_counts implementation focused on live querying and caching policy, while this property is a simple accessor for precomputed counts.

## Args:
None.

## Returns:
dict[str, int] | None
- When available, returns a dictionary mapping table name (str) -> row count (int) as derived from self.ds.inspect_data[self.name]["tables"] where each value's "count" field is used.
- Returns None if:
  - self._cached_table_counts is None and no entry exists in self.ds.inspect_data for this database name, or
  - self.ds.inspect_data is falsy.
- Note: values are taken directly from the inspect_data payload; they are typically integers but may be None if the inspect_data stored a null/unknown count.

## Raises:
- KeyError: if self.ds.inspect_data contains an entry for this database but one of the table entries lacks the "count" key, a KeyError will be raised while building the mapping.
- Any exceptions raised by attribute access on self.ds (e.g., if self.ds is None or has unexpected structure) will propagate.

## State Changes:
Attributes READ:
- self._cached_table_counts
- self.ds.inspect_data
- self.name

Attributes WRITTEN:
- self._cached_table_counts (set to the constructed dict when inspect_data for this database is present and _cached_table_counts was previously None)

## Constraints:
Preconditions:
- The Database instance should have been initialized (self.ds set, self.name typically set to the database identifier).
- The Datasette instance's inspect_data, if present, is expected to be a mapping where inspect_data[self.name]["tables"] is iterable of (table_name, info_dict) pairs and each info_dict contains a "count" key.

Postconditions:
- If inspect_data contained table counts and self._cached_table_counts was None, then after the call self._cached_table_counts will be a dict mapping table -> count.
- If inspect_data was missing for this database, self._cached_table_counts remains unchanged (still None) and the method returns None.

## Side Effects:
- Mutates the Database object's internal cache by setting self._cached_table_counts when precomputed data is available.
- Does not perform I/O, database queries, or call external services.

### `datasette.database.Database.suggest_name` · *method*

## Summary:
Return a simple, display-friendly name for the database derived from its file path or memory name; does not modify object state.

## Description:
This method centralizes the logic for choosing a human-friendly name for a Database instance. It prefers a filesystem-derived stem when the database has a path, falls back to an explicitly-provided memory name for in-memory databases, and otherwise returns the literal "db".

Known callers and lifecycle:
- No direct callers are defined inside this Database class file. Higher-level code (e.g., the application or Datasette instance) is expected to call this method when assigning or suggesting a name for display, routing, or metadata purposes during database registration or initialization.
- Typical invocation point: shortly after a Database instance is created and before its name is published in UI/routes or stored in server metadata.

Why this is its own method:
- Encapsulates the name-selection policy in one place so callers do not duplicate logic.
- Keeps initialization and registration code simpler and makes it easy to change naming rules in the future.

## Args:
This method accepts no arguments.

## Returns:
str: The suggested database name. Possible return values:
- If self.path is truthy: Path(self.path).stem (the filename with no directory or suffix).
- Else if self.memory_name is truthy: the value of self.memory_name.
- Otherwise: the literal string "db".

Edge cases:
- If self.path is a path-like object, Path(self.path).stem returns the expected filename stem.
- If self.path is provided but cannot be converted to a pathlib.Path (e.g., an unsupported type), Path(...) may raise TypeError.

## Raises:
- TypeError: Not raised by this method explicitly, but Path(self.path) will raise TypeError if self.path is not a valid path-like object.
- Any exception coming from pathlib.Path when called with an invalid value.

## State Changes:
Attributes READ:
- self.path
- self.memory_name

Attributes WRITTEN:
- None (this method does not mutate the Database instance)

## Constraints:
Preconditions:
- None strictly required by the method. For predictable behavior, callers should ensure:
  - If using filesystem-derived naming, self.path should be a string or path-like referencing the database file.
  - If using an in-memory name, self.memory_name should be a str.

Postconditions:
- Returns a non-empty string (filename stem, memory_name, or "db").
- The Database instance remains unchanged.

## Side Effects:
- None. The method performs no I/O, network calls, or mutations outside the Database object.

### `datasette.database.Database.connect` · *method*

## Summary:
Create and return a new sqlite3.Connection appropriate to this Database instance's configuration (named shared memory, ephemeral memory, file-backed read-only/immutable, or writable), and record file-backed connections on the instance when applicable.

## Description:
This method centralizes connection-creation logic for a Database instance so all call sites get a connection that respects the instance's memory/file and mutability flags. It encapsulates:
- Selecting the correct SQLite URI and mode based on self.memory_name, self.is_memory, and self.is_mutable.
- Applying a query-only PRAGMA for named shared in-memory connections when write=False.
- Tracking file-backed connections via self._all_file_connections for later cleanup or management.

Known callers and lifecycle context:
- Used anywhere the application needs a new sqlite3.Connection for this Database: serving a request, executing a query in a worker thread, performing background tasks, or when initiating a write transaction (write=True).
- It is the canonical factory for connections for this Database instance; keeping this logic in one method ensures consistent PRAGMA usage, URI construction, thread-safety flags, and connection tracking across the codebase.

Why this is a separate method:
- URI construction and side effects (PRAGMA execution and updating _all_file_connections) are reused and conditional on several instance attributes; extracting this into a method avoids duplicated logic and inconsistent connection setup.

## Args:
    write (bool): Optional; defaults to False.
        - False: create a connection suitable for read/query-only use where the method will attempt to set query-only or use read-only/immutable URIs when applicable.
        - True: request a writable connection. Allowed only if self.is_mutable is True; otherwise the method asserts and raises AssertionError.

## Returns:
    sqlite3.Connection
    - Named shared in-memory (self.memory_name truthy):
        - Connected to URI "file:{memory_name}?mode=memory&cache=shared" with uri=True and check_same_thread=False.
        - If write is False, executes "PRAGMA query_only=1" on the returned connection before returning.
    - Ephemeral in-memory (self.is_memory truthy and no memory_name):
        - Connected to ":memory:" with uri=True. The call does not override sqlite3.connect's default check_same_thread parameter.
    - File-backed databases (fallback when not memory_name and not is_memory):
        - If self.is_mutable is True and write is False: uses URI query string "?mode=ro" (and appends "&nolock=1" if self.ds.nolock is truthy).
        - If self.is_mutable is False and write is False: uses URI query string "?immutable=1".
        - If write is True (allowed only when self.is_mutable is True): uses no query string (qs="") to open a writable connection.
        - File-backed connections are created with uri=True and check_same_thread=False.
        - The connection object for file-backed databases is appended to self._all_file_connections before returning.

Edge-case returns:
- The method always returns a sqlite3.Connection on the successful path; early returns occur for named memory and ephemeral memory branches.

## Raises:
    AssertionError:
        - If write is True while self.is_mutable is False (assert not (write and not self.is_mutable)).
    sqlite3.Error (or subclass):
        - Any exception raised by sqlite3.connect or by executing the PRAGMA (for named shared in-memory branch) will propagate; this method does not catch sqlite3 exceptions.

## State Changes:
Attributes READ:
    - self.memory_name: determines named shared in-memory branch.
    - self.is_memory: determines ephemeral in-memory branch.
    - self.is_mutable: determines read-only vs immutable file behavior and whether write is permitted.
    - self.ds and self.ds.nolock: read when self.is_mutable is True to decide whether to append "&nolock=1".
    - self.path: used to construct the file-backed URI for non-memory databases.

Attributes WRITTEN:
    - self._all_file_connections: appended with the newly-created connection for file-backed database connections (only in the file-backed branch; not appended for memory branches).

## Constraints:
Preconditions:
    - The Database instance must have the attributes referenced above (memory_name, is_memory, is_mutable, ds, path, and _all_file_connections).
    - If write is requested (write=True), the instance must be mutable (self.is_mutable is True); otherwise AssertionError is raised.

Postconditions:
    - A sqlite3.Connection is returned and is configured according to the branch taken.
    - For named shared in-memory with write=False, the returned connection has executed "PRAGMA query_only=1".
    - For file-backed connections, the instance's self._all_file_connections contains the newly-created connection.

## Side Effects:
    - Opens a new sqlite3 connection (sqlite3.connect) which allocates OS resources and must be closed by the caller when no longer needed.
    - For named shared in-memory connections with write=False, executes "PRAGMA query_only=1" on the connection, altering that connection's permissions/state at the SQLite level.
    - Mutates self._all_file_connections by appending file-backed connections.
    - For named shared memory and file-backed branches, sets check_same_thread=False on the connection creation call; for the ephemeral in-memory branch the method does not supply check_same_thread and thus the sqlite3.connect default for that parameter is used.

### `datasette.database.Database.close` · *method*

## Summary:
Closes every SQLite connection previously created for this database by iterating the internal connection list, releasing their underlying file handles and making those connection objects unusable.

## Description:
This method performs a synchronous cleanup of connection objects that were stored in the instance attribute holding file-backed connections. It is a focused resource-release routine intended to be invoked by higher-level lifecycle code (for example: server shutdown, database unload, or test teardown). It is implemented as a separate method so callers can centrally ensure all file-backed connections are closed without duplicating cleanup logic throughout the codebase.

Known callers and context:
- There are no calls to this method from other methods inside the Database class; it is intended to be called by external lifecycle or teardown code that manages Datasette or individual database lifetimes.

Why this logic is a separate method:
- Centralizes cleanup of all file-backed connections in a single place.
- Avoids duplicating close logic wherever databases are unloaded or the server is stopped.
- Keeps connection-management code (connect/execute methods) and cleanup code separate for clarity and single-responsibility.

## Args:
    None

## Returns:
    None

## Raises:
    Any exception raised by an individual connection's close() method will propagate immediately.
    - Condition: If connection.close() raises (for example due to an underlying I/O error), that exception is not caught inside this method and will bubble up to the caller.
    - Effect: If an exception is raised part-way through the loop, subsequent connections in the list will not be closed.

## State Changes:
Attributes READ:
    - self._all_file_connections: iterated to obtain connection objects to close

Attributes WRITTEN:
    - None on the Database instance itself (the list and other attributes are not modified)

Note: connection.close() mutates the external connection objects (they become closed). However, this method does not remove or replace entries in self._all_file_connections nor set self._read_connection / self._write_connection to None, so those attributes (if set elsewhere) may still reference closed connection objects after this call.

## Constraints:
Preconditions:
    - self._all_file_connections should be an iterable of objects exposing a close() method (e.g., sqlite3.Connection).
    - Preferably call this method when no other threads/tasks are actively using the connections (no concurrent reads/writes), because it is not internally synchronized.

Postconditions:
    - Each connection in self._all_file_connections that was successfully processed will have had its close() method invoked.
    - The Database instance still retains its _all_file_connections list and any _read_connection/_write_connection attributes; these may now refer to closed connections.

## Side Effects:
    - Synchronous I/O: closes file descriptors/handles held by the sqlite3 connection objects.
    - Mutates external connection objects by calling their close() method.
    - May affect other threads/tasks that try to use previously-open connections (they may receive errors after they have been closed).

### `datasette.database.Database.execute_write` · *method*

## Summary:
Executes a single modifying SQL statement inside a transaction and returns the underlying sqlite3 cursor (or a task id when enqueued non-blocking), delegating actual write execution to the database's write execution pathway.

## Description:
This asynchronous helper wraps a write SQL statement in a transaction (using the connection context manager) and delegates execution to Database.execute_write_fn while adding tracing metadata (database name, SQL, params). It is the common low-level entry point used whenever callers need to run a single write statement (INSERT/UPDATE/DELETE or DDL) and want the sqlite cursor/result returned.

Known callers and invocation context:
- No direct internal callers are present in this class for single-statement writes (other helper methods in this class call execute_write_fn directly). This method is intended to be invoked by higher-level codepaths that perform a single write SQL statement as part of request handling or internal mutations (for example: request handlers, migration helpers, or other service-layer code that needs a transactional write).
- Lifecycle: called at request-processing time (or during any code that needs to perform a write) to ensure the statement executes inside a transaction and is traced.

Why this logic is factored out:
- Centralizes the transaction pattern (with conn:) and tracing so callers do not have to duplicate transaction handling.
- Keeps the decision of whether to run writes synchronously or enqueue them to the write thread separate (that decision is implemented by execute_write_fn).
- Provides a uniform async API that hides whether writes run immediately or are executed in a background writer thread.

## Args:
    sql (str): The SQL statement to execute. Must be a non-empty SQL string that performs a write/DDL operation.
    params (Optional[Sequence|Mapping]): Optional bound parameters for the statement. Accepts a sequence/tuple/list for positional parameters or a mapping (dict) for named parameters. If None, an empty list is used for execution (positional), which is appropriate for parameterless statements.
    block (bool): When the Datasette instance is configured with an executor (background writer), block controls whether the call waits for the write task to complete (True, default) or returns immediately with a task identifier (False).

## Returns:
    sqlite3.Cursor or any value returned by the provided sqlite execute call:
        - When block is True and writes are executed immediately: returns the sqlite3.Cursor produced by conn.execute(sql, params).
        - When block is True and writes are executed via the write queue: returns whatever the write task's fn returns (normally a sqlite3.Cursor-like object).
        - When block is False and a background writer is used: returns a uuid.UUID task identifier that can be used to correlate/enumerate tasks (note: execute_write_fn produces a uuid.UUID task id in this non-blocking case).
    Edge cases:
        - If the underlying write operation returns a different type (some custom connection implementations), that type is returned unchanged.
        - If an exception occurs, an exception is raised (see Raises).

## Raises:
    sqlite3.OperationalError, sqlite3.DatabaseError (or other sqlite3 exceptions):
        - Raised if sqlite3 rejects the SQL or encounters a database-level error during execution.
    Exception (propagated from write execution):
        - If execute_write_fn enqueues the task and the background task returns an Exception, execute_write_fn will raise that Exception when block=True.
        - Any other exceptions raised by the connection or the write execution pathway are propagated to the caller.

## State Changes:
    Attributes READ:
        - self.name: used to annotate the trace with the database name.
        - self.execute_write_fn: looked up and invoked to perform the actual write.
    Attributes WRITTEN:
        - None directly by this method. (Note: execute_write_fn may create or modify Database internal state such as _write_connection, _write_queue, or _write_thread; those mutations occur inside execute_write_fn/_execute_writes, not in this wrapper.)

## Constraints:
    Preconditions:
        - self must be a properly-initialized Database instance (self.ds, name, and connection-preparation logic must be usable by execute_write_fn).
        - sql must be a valid SQL string that is suitable for conn.execute when combined with params.
        - If block is False, the caller must be prepared to receive a task identifier rather than an immediate cursor/result.
    Postconditions:
        - On successful completion (block=True), the SQL statement has been executed within a transaction (committed by the connection context manager) and the returned cursor reflects the result of that execution.
        - When executed via the background writer and block=False, a task id is returned and the actual write will be performed asynchronously by the writer thread.

## Side Effects:
    - Opens/uses a write sqlite connection (via execute_write_fn) which may create the connection and prepare it (creating self._write_connection, starting the write thread, or enqueuing a task).
    - Commits the transaction for the provided SQL statement (because execution is wrapped with the connection context manager `with conn:`).
    - Performs I/O (disk writes) as a result of committing the transaction.
    - Records tracing information through the trace("sql", ...) context manager (may log or emit telemetry).
    - Propagates any exceptions encountered during execution to the caller.

### `datasette.database.Database.execute_write_script` · *method*

## Summary:
Run a multi-statement SQL script on the database inside a single transactional scope and return the script execution result (usually None) — or enqueue the script for asynchronous execution when the Datasette instance is configured for background writes.

## Description:
This asynchronous method executes the provided SQL script (one string containing one or more SQL statements) on a writable connection. The call is traced and delegated to the Database's centralized write-dispatch logic (execute_write_fn) so that connection management, queuing, and write-thread behavior are handled consistently with other write helpers.

Known callers and lifecycle context:
- Called by code paths that must apply multiple SQL statements atomically (e.g., admin actions, migrations, maintenance scripts, CLI operations, or plugins that alter schema/data).
- Invoked at the time a write must occur: during request handling or maintenance/initialization tasks.
- This logic is a distinct method because multi-statement script execution requires use of sqlite3.Connection.executescript and must enter the same write dispatch (synchronous write-connection or queued write-thread) as other write operations. Centralization avoids duplicating connection preparation, tracing, and error/queue handling.

## Args:
    sql (str): SQL script to execute. Must be a single string; may contain multiple statements separated by semicolons. Note: sqlite3.executescript does not accept parameter bindings — pass values by composing the SQL string safely (avoid untrusted interpolation).
    block (bool, optional): If True (default), wait for the execution to complete and return its result (or raise the exception encountered). If False, and the Datasette instance has an executor configured (ds.executor is not None), the method will enqueue the work and return a task identifier immediately. If ds.executor is None, block is ignored and the script is executed synchronously.

## Returns:
    If the method runs synchronously (ds.executor is None, or ds.executor present but block=True):
        The value returned by sqlite3.Connection.executescript for the executed script. In the CPython sqlite3 implementation this is typically None.
    If ds.executor is present and block is False:
        uuid.UUID — a task identifier returned immediately after the task is enqueued (note: the identifier is produced by the write-dispatch logic).
    Edge cases:
        - If an exception occurs during synchronous execution, that exception is raised to the caller.
        - If execution is enqueued (non-blocking), the caller receives a task id and no execution result; a subsequent await/inspection mechanism (if any) would be necessary to observe success/failure.

## Raises:
    sqlite3.OperationalError, sqlite3.DatabaseError:
        Any SQLite error raised while executing the script (syntax errors, constraint violations, I/O issues) will propagate to the caller when executing synchronously (block=True or ds.executor is None). In the queued path, such exceptions are captured and delivered back through the reply queue to blocking waiters; the write thread also writes the exception to stderr.
    Exception:
        Errors creating or preparing the write connection, or starting the write thread/queue, can raise generic Exceptions. When block=True these are propagated; when block=False they may be raised synchronously or surface later in the write thread.
    AssertionError:
        The Database.connect(write=True) path contains an assertion that will fail if a write is attempted against a database configured as immutable (is_mutable is False). Callers should not attempt writes on immutable databases.

## State Changes:
    Attributes READ:
        self.name — read to annotate trace metadata.
        self.execute_write_fn — invoked to perform write dispatch (may read self.ds via execute_write_fn).
        self.ds (indirectly) — used by execute_write_fn to decide synchronous vs queued write behavior (ds.executor and other ds.* used there).
    Attributes WRITTEN (directly by this method):
        None.
    Attributes WRITTEN (indirectly via execute_write_fn / write-thread):
        self._write_connection — may be created and cached when writes are handled synchronously (ds.executor is None).
        self._write_queue — may be created when ds.executor is present and queuing is used.
        self._write_thread — may be created and started when ds.executor is present.
    Notes:
        The method delegates all connection/queue/thread mutations to execute_write_fn/_execute_writes — this method itself only creates the small inner function and delegates.

## Constraints:
    Preconditions:
        - sql must be a str containing valid SQLite statements. Passing non-string types will result in an exception from sqlite3.
        - The target Database must be writable (is_mutable is True). Attempting to write to an immutable database is invalid.
        - Do not pass parameter bindings — executescript does not support parameterized placeholders.
    Postconditions:
        - When executed synchronously and the method returns normally, all statements in the script have been executed inside a transactional "with conn:" context: either all changes are committed, or the transaction is rolled back if an exception occurred.
        - When executed non-blocking (ds.executor present and block=False), the script has been enqueued; no guarantees about completion are made on return.

## Side Effects:
    - Mutates the underlying database: schema or data changes from the script are persisted to disk for file-backed databases.
    - May create or reuse a write connection (self._write_connection) or start a write thread and place a task on self._write_queue (self._write_thread / self._write_queue).
    - Emits tracing/telemetry via tracer.trace with keys: "sql", database=self.name, sql=sql.strip(), executescript=True.
    - In the queued write-thread path, exceptions during execution are written to stderr by the write thread and then propagated back to waiting callers via the reply queue.
    - No network I/O is performed by this method itself; I/O is limited to SQLite filesystem access performed by the connection.

### `datasette.database.Database.execute_write_many` · *method*

## Summary:
Performs a bulk write by running executemany inside a transaction, counting how many parameter sets were consumed, routing the work through the database's write executor, and returning the executemany result.

## Description:
This coroutine constructs a small inner callable that (1) iterates the provided params_seq while counting items, and (2) calls connection.executemany(sql, <counting-iterator>) inside a transaction (with conn:) so the write is committed or rolled back atomically. The inner callable and its execution are delegated to execute_write_fn so that write requests follow the Database instance's write-execution policy (immediate execution vs. queued background writer).

Known callers and lifecycle context:
- This method is a public API on Database and may be invoked by request handlers, application code, or plugins when many parameterized writes must be applied efficiently.
- Within this class, execute_write_fn is the central mechanism that actually runs or schedules the provided callable. Other write convenience methods (execute_write, execute_write_script) follow the same execution policy; those methods and external code typically call execute_write_many when they need bulk writes.

Why this is a separate method:
- Encapsulates the pattern of counting consumed parameter sets while passing a lazy iterator to executemany.
- Ensures the bulk-write operation participates in the same write scheduling/serialization logic (execute_write_fn) as single-statement writes.
- Centralizes tracing of the number of parameter sets processed.

## Args:
    sql (str):
        - The SQL statement to execute via executemany (e.g., "INSERT INTO t(col) VALUES (?)").
        - The string is only stripped for tracing; SQL validity is not checked here.
    params_seq (iterable):
        - An iterable (sequence or generator) of parameter sets to be passed to executemany.
        - Each yielded item must be acceptable to sqlite3.executemany (typically a tuple/list of values or a mapping).
        - This iterable is consumed once (the function uses a generator wrapper to iterate it lazily). If params_seq is a generator, it will be exhausted after the call.
    block (bool, optional):
        - Defaults to True.
        - If self.ds.executor is None (no background executor), this argument has no effect and the write is executed synchronously on a write connection.
        - If self.ds.executor is not None and block=True, this coroutine awaits the background writer and returns the executemany result (or raises the exception produced by the writer thread).
        - If self.ds.executor is not None and block=False, execute_write_fn returns a task identifier (uuid.UUID). Because this method expects execute_write_fn to return a (result, count) tuple, passing block=False with a background writer will cause a TypeError when the code attempts to unpack the returned task id — avoid block=False in that configuration.

## Returns:
- The value produced by the underlying connection.executemany call (i.e., the first element of the tuple returned by the inner callable).
  - Typically this will be whatever the sqlite3 library returns for executemany (often a cursor-like object or None depending on the SQLite API bindings).
- The integer count of processed parameter sets is NOT returned to the caller; it is injected into the tracer context for observability only.
- Edge-cases:
  - If the write path uses a background writer and block=False, execute_write_fn returns a uuid.UUID and this method will raise TypeError due to attempting to unpack that UUID into (results, count).

## Raises:
- Re-raises any exception raised by connection.executemany or by execute_write_fn:
    - If executed synchronously (no executor configured), the exception is raised directly.
    - If executed via the background writer (executor present) and block=True, the exception instance produced by the writer thread is forwarded over the janus reply queue and re-raised here.
- TypeError when ds.executor is not None and block=False because the returned task id cannot be unpacked into (results, count).

## State Changes:
Attributes READ:
    - self.name: read to populate trace metadata.
    - self.execute_write_fn: invoked to perform or schedule the inner write callable.
Attributes WRITTEN:
    - This method does not itself assign to persistent self.<attr> fields.
    - Indirectly, executing execute_write_fn may initialize or modify the following (see execute_write_fn docs):
        - self._write_connection (created and cached when no executor is configured and a write is performed)
        - self._write_queue and self._write_thread (created when a background writer is used)
Other ephemeral state:
    - A local counter (count) and the lazy counting generator wrapper over params_seq are created and used during execution.

## Constraints:
Preconditions:
    - self.ds must exist and be properly configured; execute_write_fn uses self.ds to determine execution mode.
    - params_seq must be an iterable of parameter sets; it will be iterated once.
    - If execution requires a writable connection, the Database must permit writes (self.is_mutable) — connection creation for writes asserts this.

Postconditions:
    - On success, the SQL statement(s) have been executed and committed as part of a transaction.
    - The tracer context associated with this call will include kwargs["count"] set to the number of parameter sets consumed.
    - No persistent Database attributes are modified by this method itself; persistent write-related attributes may be created by execute_write_fn as a side effect.

## Side Effects:
- Executes database I/O (writes) via the passed SQL and parameter sets.
- The executemany call runs inside a connection context manager (with conn:) so it commits on success and rolls back on exception.
- Delegates execution to execute_write_fn which may:
    - Run the callable synchronously on a cached write connection (creating and preparing self._write_connection), or
    - Enqueue the callable to a background writer thread (creating self._write_queue and self._write_thread) and use a janus.Queue reply queue for result delivery.
- The parameters iterable is consumed lazily (via a generator wrapper), minimizing memory overhead for large sequences.
- The count of parameter sets processed is recorded only in the tracer context (kwargs["count"]) and is not part of the method's return value.

### `datasette.database.Database.execute_write_fn` · *method*

## Summary:
Schedules or executes a database write callable using either a per-database synchronous write connection (when no executor is configured) or a single background writer thread and queue (when an executor exists). Returns the callable's result (or raises its exception) when blocking, otherwise returns a task identifier.

## Description:
This method centralizes how write operations are performed for this Database instance. Known callers in this module:
- execute_write: schedules or runs a single SQL execute within a transaction.
- execute_write_script: schedules or runs executescript within a transaction.
- execute_write_many: schedules or runs executemany within a transaction and returns a tuple (result, count).

Lifecycle / invocation context:
- Called whenever the Datasette runtime needs to perform a write against the underlying SQLite file for this Database. It is invoked during request handling or other runtime tasks that modify DB state.
- Runs either immediately on the calling coroutine's event loop (if no executor is configured on the parent Datasette instance), or enqueues the work for a background writer thread to serialize all writes through one connection (if an executor is configured).

Why this is a separate method:
- Ensures a single place implements the write-execution policy (immediate vs queued writer thread).
- Provides lazy initialization of write-related resources (write connection, write queue, writer thread).
- Encapsulates reply/exception handling and the janus sync/async reply queue usage.

## Args:
    fn (callable): A callable that will be invoked with one argument: a DB connection object.
        - Expected signature: result = fn(conn)
        - The callable should perform required write operations (e.g., executing SQL within a transaction)
        - May return any Python object; may raise exceptions on failure.
    block (bool, optional): Defaults to True.
        - If True, the coroutine waits for the callable to complete and either returns its result or raises the exception the callable produced.
        - If False and a background writer is used, this method returns a task identifier immediately and does not wait for completion.

## Returns:
- If ds.executor is None (no background executor):
    - Returns whatever fn(conn) returns (synchronous execution on the coroutine path).
- If ds.executor is not None and block is True:
    - Returns whatever fn(conn) returned when executed by the background writer thread.
- If ds.executor is not None and block is False:
    - Returns a uuid.UUID task identifier that identifies the scheduled write task.
Notes:
- The actual return type is therefore dependent on the provided fn (or uuid.UUID when non-blocking scheduled).
- When blocking and the writer thread encountered an exception while executing fn, this method raises that exception (see Raises).

## Raises:
- Any exception raised by fn will be propagated:
    - If executed synchronously (ds.executor is None), the exception is raised directly from this call.
    - If executed via the background writer thread (executor present) and block=True, the exception instance produced by the writer thread is received over the reply queue and re-raised by this coroutine.
- If underlying queue/queueing or janus usage fails unexpectedly, those exceptions may propagate (e.g., RuntimeError from janus operations). The method itself does not raise new, specialized exceptions.

## State Changes:
Attributes READ:
    - self.ds.executor: read to decide synchronous vs queued behavior
    - self._write_queue: read to check whether it exists
    - self._write_thread: read to check whether it exists
    - self._write_connection: read (and possibly written) when no executor is configured
    - self.ds._prepare_connection: invoked (reads attribute from ds)
Attributes WRITTEN:
    - self._write_connection:
        - When ds.executor is None and no existing write connection exists, a new write connection is created via self.connect(write=True) and stored here.
    - self._write_queue:
        - When ds.executor is not None and the queue is None, a new queue.Queue() is created and stored here.
    - self._write_thread:
        - When ds.executor is not None and the thread is None, a new daemon threading.Thread is created targeting self._execute_writes and started; the thread object is stored here.
Other ephemeral state:
    - A local janus.Queue() (reply_queue) is created per call when enqueuing to the background writer.

## Constraints:
Preconditions:
    - self.ds must exist and expose an executor attribute (None or an executor object).
    - fn must be callable and accept a single connection argument; callers must agree on the connection type and semantics (e.g., sqlite3.Connection).
    - If write=True is required for immediate execution, the underlying database must be mutable (self.is_mutable); self.connect(write=True) asserts write allowed.

Postconditions:
    - If ds.executor is None: fn has been executed on the calling path before this coroutine returns (or raised).
    - If ds.executor is not None and block is True: fn has been executed by the background writer before return (or its exception raised).
    - If ds.executor is not None and block is False: the write task is enqueued for later execution by the background writer thread; the returned task_id identifies that queued task.

## Side Effects:
- May create and initialize a persistent write connection (self._write_connection) and call self.ds._prepare_connection(conn, self.name) to apply connection configuration. That write connection is reused for subsequent synchronous writes.
- When an executor exists, may create:
    - a queue.Queue stored in self._write_queue used to hand WriteTask values to the background writer thread
    - a daemon threading.Thread stored in self._write_thread that runs self._execute_writes which loops forever consuming tasks
    - a janus.Queue reply_queue per task that bridges the synchronous writer thread and async caller
- The background writer thread executes fn(conn) and therefore performs I/O to the database. Exceptions from that execution are captured and forwarded back via the task's reply_queue as the Exception instance; this method will re-raise the instance for blocking callers.
- Writes are serialized by the background writer thread (one thread, one connection) when the executor is enabled; non-blocking calls do not block the caller but still mutate DB state once processed by the writer thread.

## Implementation notes (for reimplementation):
- Use uuid.uuid5(uuid.NAMESPACE_DNS, "datasette.io") to produce a deterministic task id for non-blocking scheduled tasks (the code uses this constant generation; callers expect a uuid.UUID).
- Use janus.Queue to create a reply_queue that exposes both .async_q (an asyncio-compatible Queue) and .sync_q (a synchronous queue) so the writer can put results with reply_queue.sync_q.put(...) and this coroutine can await reply_queue.async_q.get().
- Enqueue a WriteTask(fn, task_id, reply_queue) on the self._write_queue for the background writer to consume.
- The writer thread function (_execute_writes) should:
    - Create its own write connection (conn = self.connect(write=True)) and call self.ds._prepare_connection(conn, self.name)
    - Loop reading tasks from the queue; for each task call task.fn(conn) and put the result (or exception instance) onto task.reply_queue.sync_q
    - If a connection error occurs during initialization, store it and return that exception for every queued task
- When ds.executor is None, run fn synchronously on a per-database write connection (create lazily and store as self._write_connection) and return its result directly.

### `datasette.database.Database._execute_writes` · *method*

## Summary:
Runs in a dedicated background thread to serially execute write callables against a single write SQLite connection and deliver each result (or exception) back to the caller via the task's reply queue. It does not return and keeps processing tasks from the write queue until the process exits.

## Description:
- Known callers and context:
    - Started by Database.execute_write_fn when a write thread has not yet been created. That function creates a queue.Queue for self._write_queue, starts a daemon Thread whose target is this method, and enqueues WriteTask instances into the queue.
    - Higher-level async helpers that ultimately enqueue tasks include: Database.execute_write, Database.execute_write_script, and Database.execute_write_many (each calls execute_write_fn).
    - Lifecycle stage: runs as a long-lived background worker thread handling the serialized write phase of the database I/O pipeline. It is active once a writer thread is started and until the process terminates.

- Why this is a separate method:
    - SQLite connections used for writes must be used in a controlled, single-threaded manner to avoid concurrency issues. Centralizing write execution in one thread ensures all write operations share one connection and are run serially.
    - Running writes in a dedicated thread decouples blocking database I/O from asyncio event loop threads and from the rest of the application, allowing async callers to await results via the janus reply queue without blocking the main loop.
    - Keeping the thread-run loop and connection setup logic separate simplifies lifecycle management and error handling (e.g., capturing a connection-creation exception that should be propagated to queued tasks).

## Args:
- None. This is an instance method that consumes tasks from self._write_queue; tasks are objects placed there by execute_write_fn. Each task is expected to have at least:
    - fn: callable(conn) -> Any | raises Exception
    - reply_queue: a janus.Queue instance with async_q and sync_q attributes

## Returns:
- None. The method loops forever (reads tasks and puts results) and does not return to its caller.

## Raises:
- The method does not propagate exceptions out to its caller. Instead:
    - Exceptions raised while creating the write connection or preparing it are captured and stored (conn_exception). Subsequent tasks receive this exception object as their result.
    - Exceptions raised by task.fn(conn) are caught; the textual representation is written to sys.stderr and the Exception instance is sent back to the caller via the task.reply_queue.
- Implicit exceptions:
    - If self._write_queue.get() raises (e.g., due to queue being closed or interpreter shutdown), that exception may propagate and terminate the thread. The implementation assumes a normally functioning queue and runtime.

## State Changes:
- Attributes READ:
    - self.ds: used to call self.ds._prepare_connection(conn, self.name)
    - self.name: used when preparing the connection
    - self._write_queue: consumed by calling self._write_queue.get()
    - indirectly reads configuration/state used inside connect (e.g., self.is_mutable, self.memory_name) via self.connect(write=True)
- Attributes WRITTEN (modified):
    - self._all_file_connections: connect(write=True) may append the new connection to this list (connect appends file connections). This method therefore causes self._all_file_connections to gain the write connection.
    - It does not mutate other Database attributes directly.

## Constraints:
- Preconditions:
    - self._write_queue must be a thread-safe queue.Queue (execute_write_fn creates and sets one before starting the thread).
    - task objects placed on self._write_queue must conform to the expected structure: have a callable attribute fn and a reply_queue attribute that is a janus.Queue with sync_q and async_q.
    - self.ds must implement _prepare_connection(conn, database_name).
    - The caller should ensure execute_write_fn started this method as a daemon thread; it is not intended to be invoked directly on the main thread.
- Postconditions / Guarantees:
    - For each task consumed:
        - The task's reply_queue.sync_q will receive exactly one item: either the successful return value of task.fn(conn) or an Exception object.
        - If the write connection could not be created or prepared, every consumed task will receive the same connection-creation Exception as its result (no automatic reconnection).
    - The method runs indefinitely until the process/thread is terminated (no built-in shutdown path).

## Side Effects:
- I/O and external interactions:
    - Opens a write SQLite connection via self.connect(write=True). This allocates a DB connection resource and (via connect) appends it to self._all_file_connections.
    - Calls self.ds._prepare_connection(conn, self.name) which may perform PRAGMAs or other connection initialization with external side effects.
    - Executes arbitrary task.fn(conn) callables. Those callables may perform any side effects (database writes, file I/O, network calls, etc.). The method makes no assumptions about what fn does.
    - On exceptions thrown by task.fn, writes the exception text to sys.stderr and flushes it.
- Inter-thread communication:
    - Receives WriteTask instances via self._write_queue.get(), which blocks until tasks are available.
    - Sends results back to the originator by placing the result (value or Exception instance) into task.reply_queue.sync_q (synchronous side of a janus.Queue). The original async caller awaits the same result via reply_queue.async_q.get().

## Implementation notes and edge cases a reimplementer should preserve:
- The write connection is created once at thread start; an exception during connection creation stops further attempts and the exception is propagated to pending/future tasks by returning it through their reply queues.
- Each task is executed in the writer thread and should be called with the same connection instance (conn).
- Exceptions from task.fn should not kill the writer thread; they should be converted to results sent back to the caller and the loop should continue processing subsequent tasks.
- The method intentionally never returns; lifecycle cleanup (closing connections) is managed elsewhere (e.g., Database.close). If graceful shutdown is required, implementers should add termination handling (not present in the original).

### `datasette.database.Database.execute_fn` · *method*

## Summary:
Run a synchronous callable that accepts a sqlite3.Connection and return its result, ensuring an appropriate sqlite3 connection is created, prepared, and cached — either on the current object for single-threaded use or on a module-level per-database store when running in an executor.

## Description:
This async helper centralizes the pattern of obtaining a sqlite3 connection and invoking a synchronous function with it. It chooses one of two execution strategies based on whether the Datasette instance has an executor configured:
- Synchronous-on-event-loop path (ds.executor is None): ensure a shared read connection is available on self._read_connection, call fn(conn) directly on the current thread, and return its result.
- Executor path (ds.executor is not None): schedule fn to run in the configured executor using asyncio.get_event_loop().run_in_executor(self.ds.executor, in_thread). The in_thread helper obtains or creates a connection cached on a module-level object named connections (an attribute keyed by this Database.name), prepares it, then calls fn(conn) on the executor thread.

Known callers / contexts:
- execute (for read SQL queries), table_columns, table_column_details, primary_keys, fts_table, label_column_for_table, foreign_keys_for_table, get_all_foreign_keys, and other read-only helper methods in Database.
- These callers are typically invoked during request handling or internal inspection/metadata operations.

Why this logic is a separate method:
- Consolidates connection creation, ds._prepare_connection invocation, and caching semantics.
- Encapsulates the decision of whether to block the event loop or offload blocking DB operations to an executor.
- Prevents duplication of threading and connection-management boilerplate across many Database reader helpers.

## Args:
    fn (Callable[[sqlite3.Connection], Any]):
        - A synchronous callable that accepts a single sqlite3.Connection and returns a value.
        - Must not be an async coroutine function; if a coroutine function is passed, execute_fn will pass a coroutine object through as the return value rather than awaiting it.
        - Should be safe to run on an executor thread when ds.executor is set (avoid accessing asyncio event-loop-only state inside fn).

## Returns:
    Any
        - The direct return value of fn(conn).
        - When ds.executor is None: the method returns fn(self._read_connection) immediately (the async function still must be awaited by the caller to obtain the value).
        - When ds.executor is set: returns the value produced by fn(conn) after it completes in the executor (via asyncio.get_event_loop().run_in_executor).
        - If fn raises, that exception propagates to the awaiting caller.

## Raises:
    - Any exception raised by self.connect(): e.g., sqlite3.OperationalError, OSError when opening the file/URI.
    - Any exception raised by self.ds._prepare_connection(conn, self.name): propagation of errors from connection preparation.
    - Any exception raised by fn(conn): e.g., sqlite3.OperationalError, sqlite3.DatabaseError, or user-defined exceptions.
    - NameError (or UnboundLocalError) if the module-level name connections is not defined when the executor path is taken — this will occur when in_thread executes and references connections.
    - asyncio.CancelledError or other asyncio errors if the awaiting task is cancelled while waiting for the executor result.

## State Changes:
Attributes READ:
    - self.ds.executor: decision point for execution strategy.
    - self._read_connection: checked for existence in the non-executor path.
    - self.name: used as the cache key when storing/retrieving connections from the module-level connections object.
    - self.ds: used to call _prepare_connection.

Attributes WRITTEN:
    - self._read_connection: set to a new connection object when ds.executor is None and a cached read connection did not exist.
    - module-level connections (via setattr(connections, self.name, conn)): when ds.executor is set, a connection object is stored as an attribute on the module-level connections object under the database name (this caches a connection per database on the executor side).
    - Indirectly, self._all_file_connections may be appended to when connect() creates a file-backed connection (connect() appends such connections to _all_file_connections).

## Constraints:
Preconditions:
    - fn must be a synchronous callable accepting one sqlite3.Connection argument.
    - Callers must await execute_fn(...) to receive the result.
    - If ds.executor is not None, fn must be safe to execute from a worker thread (avoid manipulating asyncio-only state).

Postconditions:
    - If ds.executor is None: after the call, self._read_connection will be a connected and prepared sqlite3.Connection (unless connect() or _prepare_connection raised), and fn has been executed with that connection.
    - If ds.executor is set: a connection attribute on the module-level connections object keyed by self.name will exist after in_thread runs (unless connection creation/preparation failed), and fn(conn) has executed on an executor thread and its result returned to the awaiter.

## Side Effects:
    - Opens sqlite3 connections (calls self.connect()), which can perform file I/O and consume OS resources.
    - Calls self.ds._prepare_connection(conn, self.name) which typically modifies connection PRAGMAs; these are side effects on the sqlite3.Connection.
    - Mutates module-level state by setting an attribute on the connections object when using the executor path (shared state visible to other threads).
    - When run without an executor, fn executes on the event loop thread and can block the loop if fn is long-running.

### `datasette.database.Database.execute` · *method*

## Summary:
Runs the provided SQL on this Database's connection (safely in the configured executor or thread), applying the configured time limit and optional truncation, and returns a Results object containing the retrieved rows, a truncation flag, and the cursor description.

## Description:
This asynchronous helper centralizes how SQL is executed against a Database instance. It:
- Runs the blocking DB interaction (cursor creation, execute, and fetching) inside the database's configured execution path via self.execute_fn (either inline on a cached connection or in the configured executor/thread).
- Enforces a per-query time limit using sqlite_timelimit (with optional custom_time_limit override).
- Optionally truncates returned rows to a maximum and marks results as truncated.
- Converts low-level SQLite "interrupted" errors into QueryInterrupted to preserve SQL and params context, and logs SQL errors when requested.

Known callers and typical invocation contexts (non-exhaustive):
- Database.table_counts — invoked while counting rows for each table.
- Database.attached_databases — invoked to run PRAGMA database_list.
- Database.table_exists / Database.table_names / Database.view_names — used when discovering schema.
- Any other higher-level code in the repository that needs to run arbitrary SQL against a Database instance.
These callers typically call execute during normal request handling or during background inspection tasks; the method is used whenever code needs a consistent, safe SQL execution path rather than inlining raw connection usage.

Why this is a separate method:
- It encapsulates common behaviors required for every SQL run (executor handling, timeouts, truncation behavior, error translation and logging, and tracing). Centralizing this avoids duplicated logic and ensures uniform behavior across the codebase.

## Args:
    sql (str): SQL statement to execute. Required.
    params (tuple | list | dict | None): Parameters to bind to the SQL. Defaults to None.
        - If None, the method passes an empty mapping ({}) to cursor.execute; callers should supply positional (tuple/list) or named (dict) parameters if the SQL contains placeholders. Supplying incorrect param shape for the SQL will raise the underlying sqlite3 error.
    truncate (bool): If True, the returned Results will be constrained to at most the configured max_returned_rows and marked as truncated when more rows existed. Defaults to False.
    custom_time_limit (int | None): Optional time limit in milliseconds for this specific query. If provided and lower than the database's configured sql_time_limit_ms, it overrides the default for this call. Defaults to None.
    page_size (int | None): Page size used for the caller's paging logic. If omitted, the database's ds.page_size is used. Used only to adjust truncation behaviour when ds.max_returned_rows equals page_size.
    log_sql_errors (bool): When True (default), write formatted error messages to stderr if sqlite3.OperationalError or sqlite3.DatabaseError is raised before re-raising them.

## Returns:
    Results: An object (constructed with Results(rows, truncated_flag, cursor.description)) with:
        - rows (list[sqlite3.Row | tuple]): The fetched rows. When truncate=True and a max_returned_rows limit is in effect, length(rows) <= max_returned_rows.
        - truncated (bool): True if rows were trimmed because more rows existed than the allowed maximum; False otherwise.
        - cursor.description: The DB cursor description tuple giving column metadata (may be None for statements without result sets).
    Edge cases:
        - If ds.max_returned_rows is falsy (0 or None), the method uses cursor.fetchall() and truncated is False.
        - If truncate=True and the code detects more rows than the allowed maximum, truncated is True and rows is sliced to the allowed maximum.

## Raises:
    QueryInterrupted: Raised when a sqlite3.OperationalError or sqlite3.DatabaseError is caught and its args are exactly ("interrupted",). The QueryInterrupted wraps the original error along with the sql and params.
    sqlite3.OperationalError or sqlite3.DatabaseError: Re-raised for other database-level failures encountered during execution (after optional logging). The original exception is not wrapped in these cases.
    Any exception raised by self.execute_fn or the nested execution function (including exceptions from sqlite_timelimit, tracing, or executor management) will propagate to the caller.

## State Changes:
Attributes READ:
    - self.ds (and sub-attributes consulted):
        - self.ds.page_size (default for page_size when argument not provided)
        - self.ds.sql_time_limit_ms (default time-limit unless custom_time_limit is lower)
        - self.ds.max_returned_rows (used to decide whether/where to truncate)
        - self.ds.executor (indirectly used by execute_fn)
    - self.execute_fn: referenced to schedule the blocking SQL operation
    - self.name: used for trace metadata and for connections prepared by execute_fn
Attributes WRITTEN:
    - None. This method does not modify any self.<attr> fields.

## Constraints:
Preconditions:
    - sql must be a string containing a valid SQL statement for the underlying sqlite3 connection.
    - If the SQL uses positional placeholders (?) the caller must provide params as a sequence (tuple/list). If the SQL uses named placeholders (:name), a mapping (dict) is required. Passing the wrong param shape will cause sqlite3 to raise an error.
    - custom_time_limit, if provided, must be a numeric value representing milliseconds (int). It is compared numerically to ds.sql_time_limit_ms.
    - page_size, if provided, should be a non-negative integer.

Postconditions:
    - The returned Results will include cursor.description corresponding to the executed statement.
    - If truncate=True and ds.max_returned_rows is truthy, rows will contain at most the configured max_returned_rows and truncated will correctly reflect whether more rows were available.
    - The method completes only after execute_fn returns (which may execute in the calling thread or in an executor). Any exceptions raised during execution will be propagated or wrapped as documented.

## Side Effects:
    - Executes the SQL statement on a database connection: any side effects of that SQL (INSERT/UPDATE/DELETE/DDL) will occur.
    - Uses sqlite_timelimit which may interrupt the running query if it exceeds the time limit.
    - May log a formatted error line to sys.stderr when a sqlite3.OperationalError or sqlite3.DatabaseError occurs and log_sql_errors is True.
    - Emits a trace/context via trace("sql", database=self.name, sql=sql.strip(), params=params) for external tracing/monitoring.
    - When ds.executor is set, execution occurs in the configured executor (thread pool or similar), otherwise it may reuse this Database's cached read connection and execute inline.

### `datasette.database.Database.hash` · *method*

## Summary:
Return a stable hash string for a file-backed, immutable database and cache it on the instance; for mutable or in-memory databases return None.

## Description:
This property computes and returns a hash that identifies the contents of the underlying database file, caching the result on the Database instance so subsequent accesses are cheap.

Known callers and contexts:
- Database.__repr__: used when building a textual representation of the Database for logging or debugging.
- Any external code that needs a stable identifier for a file-backed database (for example, to detect changes, to use in cache keys, or to display a fingerprint).
Lifecycle stage:
- Typically called during read-only inspection or diagnostics of a database. It is safe to call multiple times; the result is memoized on the instance.

Why this is its own property:
- Encapsulates the logic of (a) returning a previously computed value, (b) honoring in-memory/mutable database semantics (which do not have a file hash), (c) preferring precomputed values obtained from the DataSource's inspect_data, and (d) computing the hash from disk when necessary. Centralizing this avoids duplicating caching and fallback logic across the codebase.

## Args:
    None

## Returns:
    str or None:
        - str: a hash-like string (obtained either from ds.inspect_data[self.name]["hash"] or computed by calling inspect_hash(Path(self.path))). When a string is returned, self.cached_hash is set to that string.
        - None: returned when the database is flagged mutable (is_mutable True) or in-memory (is_memory True); in this case self.cached_hash remains unchanged (commonly None).

## Raises:
    Any exception raised by Path(self.path) or by inspect_hash(Path(self.path)):
        - If the code path reaches the on-disk computation (i.e., not cached, not mutable/memory, and no inspect_data entry), Path(self.path) or inspect_hash may raise errors such as FileNotFoundError, PermissionError, OSError, or any exception propagate from inspect_hash. These are not caught here.

## State Changes:
    Attributes READ:
        - self.cached_hash
        - self.is_mutable
        - self.is_memory
        - self.ds
        - self.name
        - self.path

    Attributes WRITTEN:
        - self.cached_hash (set when a hash string is obtained from ds.inspect_data or inspect_hash)

## Constraints:
    Preconditions:
        - The Database instance should have is_mutable and is_memory set correctly to reflect whether the database is file-backed and immutable.
        - For the on-disk computation branch, self.path must refer to the database file location (not None) and be accessible by the process.
        - If relying on ds.inspect_data, that structure should be a mapping where ds.inspect_data[self.name]["hash"] is a string when present.

    Postconditions:
        - If the method returns a str, then self.cached_hash holds that same str after the call.
        - If the method returns None (because the database is mutable or memory), self.cached_hash remains unmodified by this call.
        - Once self.cached_hash is set to a string, subsequent accesses return that cached value without recomputing or re-reading ds.inspect_data.

## Side Effects:
    - Mutates self.cached_hash when a hash value is obtained.
    - May perform filesystem I/O when computing the hash via inspect_hash(Path(self.path)); this can be slow and may read file contents or metadata.
    - No network calls or external services are invoked directly by this property.

### `datasette.database.Database.size` · *method*

## Summary:
Return the database file size in bytes, using cached or precomputed inspect data when available; for in-memory databases this returns 0. This accessor may update Database.cached_size for non-mutable databases.

## Description:
Known callers and context:
    - Database.__repr__: explicitly reads this property to include size information in the object's textual representation.
    - Other call sites in the codebase may read this property when presenting database metadata; those are not shown in this class but will call this property the same way as any attribute access.

Lifecycle / pipeline stage:
    - Accessed at runtime whenever a caller needs the current size of the database file (for logging, metadata display, or diagnostics). It is a read-only property that encapsulates logic for choosing the most appropriate size source and for caching results when appropriate.

Why this logic is its own property:
    - Determining size requires checking multiple sources (in-memory, mutable filesystem stat, precomputed inspect_data, cached value) and managing caching behavior. Centralizing the logic avoids duplication of filesystem I/O and ensures consistent caching semantics across the codebase.

Precedence (order of checks performed):
    1. If self.cached_size is not None: return cached_size immediately (no other checks performed).
    2. If self.is_memory is True: return 0.
    3. If self.is_mutable is True: return the current on-disk file size via Path(self.path).stat().st_size (do not update cached_size).
    4. If self.ds.inspect_data is present and self.ds.inspect_data.get(self.name) is truthy: read the "size" value from that inspect data, assign it to cached_size, and return it.
    5. Otherwise (fallback): stat the file at self.path, assign its st_size to cached_size, and return it.

## Args:
    None (property with no arguments).

## Returns:
    int: Number of bytes in the database file in normal operation.
        - In-memory databases: returns 0.
        - Mutable on-disk databases: returns the current filesystem size (integer) and does not cache it.
        - For databases using precomputed inspect data: returns the integer value from ds.inspect_data[self.name]["size"] and caches it.
        - In the fallback branch the filesystem st_size (integer) is cached and returned.
    Note: If cached_size has been mutated externally to a non-integer value, this property will return that value (because the top precedence check returns cached_size as-is). Implementations should assume cached_size normally holds an integer.

## Raises:
    - TypeError: if self.path is None or of an invalid type when Path(self.path) is constructed (occurs only in branches that call Path(self.path).stat()).
    - FileNotFoundError / OSError: raised by Path(self.path).stat() if the path does not exist or is inaccessible (can happen in mutable or fallback branches).
    - KeyError: if ds.inspect_data and ds.inspect_data.get(self.name) return a mapping that does not include the "size" key (the code accesses ["size"] directly).
    - Any other exception raised by Path.stat(), attribute access on ds.inspect_data, or other underlying operations is propagated to the caller.

## State Changes:
    Attributes READ:
        - self.cached_size
        - self.is_memory
        - self.is_mutable
        - self.path
        - self.ds
        - self.name

    Attributes WRITTEN:
        - self.cached_size:
            - Written when using ds.inspect_data (assigned ds.inspect_data[self.name]["size"]).
            - Written in the fallback branch after reading Path(self.path).stat().st_size.
            - Not written when returning early from cached_size not None, when is_memory is True, or when is_mutable is True.

## Constraints:
    Preconditions:
        - The Database object must be initialized (self.ds set).
        - For branches that stat the filesystem (is_mutable True or fallback), self.path must refer to a valid filesystem path accessible to the process.
        - For the inspect_data branch, self.ds.inspect_data must be mapping-like and self.ds.inspect_data.get(self.name) must return a truthy mapping that contains a "size" key.

    Postconditions:
        - If the inspect_data branch or fallback branch is taken, self.cached_size will be set to the integer size and that integer will be returned.
        - If the mutable branch is taken, the returned value reflects the current filesystem size and self.cached_size remains unchanged.
        - If the in-memory branch is taken, 0 is returned and self.cached_size remains unchanged.
        - If cached_size was not None on entry, that exact value is returned and no further branches are evaluated.

## Side Effects:
    - Performs synchronous filesystem I/O when Path(self.path).stat() is called (mutable or fallback branches). This can be relatively expensive and may raise OS errors.
    - May mutate self.cached_size in the inspect_data and fallback branches.
    - No network I/O or external service calls are performed by this property itself.
    - Exceptions from filesystem access or malformed inspect_data are propagated to the caller; callers should handle these where appropriate.

### `datasette.database.Database.table_counts` · *method*

## Summary:
Asynchronously returns a dictionary mapping every table name in this database to its row count (int) or None when the count could not be obtained; for immutable databases the computed mapping is cached on the instance.

## Description:
This coroutine:
- Obtains the list of table names from self.table_names().
- For each table it runs a direct COUNT query ("SELECT count(*) FROM [table]") via self.execute(..., custom_time_limit=limit) and records the returned integer row count.
- If a per-table COUNT fails due to a query interruption or SQLite Operational/Database error, that table's value is set to None.

Known callers and context:
- No explicit callers were found in the provided context. Conceptually, this method is used during metadata/inspection operations (for example, building UI summaries or API endpoints that show table sizes).
- It is typically invoked during read-only inspection or reporting phases; because immutable databases do not change, their results are cached to avoid re-running multiple COUNT queries.

Why this is a separate method:
- It encapsulates the loop of per-table queries, consistent per-table timeout handling, and caching for immutable databases. Centralizing this logic avoids duplication and ensures uniform behavior for timeouts and error handling across the codebase.

## Args:
    limit (int): Per-table custom time limit applied to each COUNT query, in milliseconds. Must be a non-negative integer. Defaults to 10 (milliseconds). A smaller value will override the Datasette global SQL time limit for the individual COUNT operation.

## Returns:
    dict[str, int | None]:
        - A dictionary whose keys are table names (str) and values are either:
            * an integer row count when the SELECT COUNT(*) query completed successfully, or
            * None when the per-table COUNT was interrupted or failed with a sqlite Operational/Database error.
        - The method always returns a dict (possibly empty for a database with no tables), unless an exception propagates from self.table_names() or an unexpected exception occurs.

## Raises:
    - Any exception raised by self.table_names() will propagate (for example, connection or schema inspection errors).
    - Any exception raised by self.execute(...) other than the explicitly caught exceptions below will propagate.
    Handled (non-propagating) exceptions:
    - QueryInterrupted: caught for each table; when raised during a per-table COUNT the implementation records counts[table] = None and continues.
    - sqlite3.OperationalError and sqlite3.DatabaseError: caught for each table; when raised the implementation records counts[table] = None and continues.
    Notes:
    - The method assumes successful COUNT queries yield at least one row and that results.rows[0][0] contains an integer; if that contract is violated an IndexError or TypeError may propagate.

## State Changes:
    Attributes READ:
        - self.is_mutable
        - self.cached_table_counts (property; may read self._cached_table_counts or ds.inspect_data)
        - Implicitly reads any state used by self.table_names() and self.execute()
    Attributes WRITTEN:
        - self._cached_table_counts is set to the computed mapping when self.is_mutable is False (i.e., for immutable databases)

## Constraints:
    Preconditions:
        - The Database instance must be initialized and able to run self.table_names() and self.execute(...).
        - limit should be an integer >= 0 (negative values are not meaningful and may lead to unexpected behavior).
    Postconditions:
        - If self.is_mutable is False, self._cached_table_counts will be set to the returned mapping (even if some table values are None).
        - The returned value will be a dict mapping every table name returned by self.table_names() to either an int or None, unless an exception propagated.

## Side Effects:
    - I/O: runs "SELECT COUNT(*) FROM [table]" for each table; each query is subject to the provided custom_time_limit and the Datasette SQL time limit.
    - Caching: may assign the resulting dict to self._cached_table_counts for immutable databases.
    - No modification of database contents occurs.
    - No external network calls are made directly by this method (but underlying connection setup or hooks may have their own side effects).

### `datasette.database.Database.mtime_ns` · *method*

## Summary:
Return the on-disk database file's modification time in nanoseconds, or None for an in-memory database. This accessor does not modify the object's state.

## Description:
This method checks whether the Database instance represents an in-memory database; if so, it returns None. For a file-backed database it constructs a pathlib.Path from self.path, calls stat(), and returns the st_mtime_ns field from the resulting stat result.

Known callers and context:
- No direct callers are visible in this function's source alone. Typical callers elsewhere in the application would be cache-invalidation, reload-check, or diagnostic code that needs to detect whether the underlying database file has changed since a prior check (for example, to decide whether to reopen or refresh caches).
- This logic is factored into a dedicated method to centralize the "in-memory vs file-backed" distinction and to provide a single place to access the file modification timestamp (so callers don't have to duplicate Path(stat) handling or the is-memory check).

## Args:
    None

## Returns:
    int or None
    - If the Database is file-backed: returns the file modification time as an integer number of nanoseconds (the value of stat().st_mtime_ns).
    - If the Database is in-memory (self.is_memory is truthy): returns None.
    - Edge cases: if the file backing self.path does not exist or is inaccessible, this method will not catch the error and the corresponding OSError (e.g., FileNotFoundError, PermissionError) will propagate to the caller.

## Raises:
    OSError or subclass (e.g., FileNotFoundError, PermissionError):
    - Raised when Path(self.path).stat() fails because the path does not exist, the process lacks permission, or another OS-level error occurs while retrieving metadata.
    - Note: the method does not handle or swallow these exceptions; they propagate.

## State Changes:
    Attributes READ:
        - self.is_memory
        - self.path
    Attributes WRITTEN:
        - None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - The Database instance must have attributes is_memory and path defined.
        - If self.is_memory is falsy, self.path should be a valid filesystem path string or a Path-compatible object convertible by pathlib.Path.
    Postconditions:
        - No attributes on self are modified.
        - The return value is either an int (nanoseconds) for file-backed DBs or None for in-memory DBs; if metadata retrieval fails, an OSError is raised.

## Side Effects:
    - Performs a filesystem metadata lookup (calls Path(...).stat()), which issues an OS-level stat system call. This is a read-only operation and does not mutate files or external state.
    - No network I/O or persistent mutations occur.

### `datasette.database.Database.attached_databases` · *method*

## Summary:
Returns a list of attached database descriptors (excluding the main database) by querying PRAGMA database_list and converting each qualifying row into an AttachedDatabase container.

## Description:
This coroutine queries the SQLite connection for the database list (PRAGMA database_list;) and converts each returned row with seq > 0 into an AttachedDatabase instance. The method is intended to encapsulate the SQL needed to discover attached databases and the mapping from raw query rows into the higher-level AttachedDatabase container so caller code can work with a typed representation instead of raw rows.

Known callers and lifecycle:
    - No direct callers were discovered in the provided code fragment. Typical use cases include:
        * At runtime when code needs to inspect which databases are attached to a connection (for example, to build a UI listing or to open references).
        * Any migration, introspection, or administration code that needs the attached database filenames or logical names.
    - This method is a small, focused utility invoked at the point in the lifecycle when the application needs to inspect the current connection's attached databases. It is intentionally separated so SQL and row-to-object mapping are kept in one place and can be reused.

Why this is a separate method:
    - Keeps the SQL string and the row-to-structure conversion centralized.
    - Makes intent explicit (list attached DBs) and isolates any future changes (different column handling or filtering) to a single location.
    - Improves readability of calling code by returning semantic objects instead of raw rows.

## Args:
    None

## Returns:
    list[AttachedDatabase]
    - A list of AttachedDatabase instances, one for each attached database whose PRAGMA database_list row has "seq" > 0.
    - Typical AttachedDatabase fields (expectation for implementers): seq (int), name (str), file (str) — corresponding to the standard PRAGMA database_list columns.
    - If no attached databases are present, an empty list is returned.
    - Edge cases:
        * If the PRAGMA returns rows but none have seq > 0, the returned list will be empty.
        * If rows exist but lack the "seq" column or are not mapping-like, a runtime error will occur (see Raises).

## Raises:
    - Any exception raised by self.execute will propagate unchanged. In the current Database.execute implementation, this can include:
        * QueryInterrupted (propagated when an "interrupted" sqlite error occurs)
        * sqlite3.OperationalError, sqlite3.DatabaseError and other sqlite3 exceptions (these may be logged and re-raised by execute)
        * Other exceptions raised by execute_fn or by the underlying DB API
    - KeyError or TypeError if a returned row does not support mapping access by column name (row["seq"]) or if the "seq" key is missing.

## State Changes:
    Attributes READ:
        - None directly on self (this method calls self.execute, but does not directly read self.<attr> fields).
    Attributes WRITTEN:
        - None (this method does not modify the Database instance state).

## Constraints:
    Preconditions:
        - The Database instance must be connected/initialized so that self.execute can be invoked successfully.
        - self.execute must return a Results-like object with a .rows attribute that is an iterable of row objects.
        - Each row must:
            * support mapping access by column name (row["seq"]), and
            * be iterable/expandable so that AttachedDatabase(*row) yields the expected positional arguments (seq, name, file) in that order.
    Postconditions:
        - The returned list contains an AttachedDatabase instance for every PRAGMA database_list row where seq > 0.
        - The Database instance is unchanged by this call.

## Side Effects:
    - Executes a read-only PRAGMA SQL statement against the database connection (invokes self.execute), which will perform I/O on the database connection.
    - No external network or file mutations are performed by this method itself. Side effects are limited to whatever happens inside self.execute (logging, query time-limiting, or exceptions).
    - No mutation of objects outside self (other than potential side effects inside self.execute).

### `datasette.database.Database.table_exists` · *method*

## Summary:
Check whether a named table exists in the SQLite database by running a lightweight read-only query and returning True if the table is present, False otherwise.

## Description:
This coroutine performs a single parameterized query against sqlite_master to determine whether a table with the supplied name exists. It awaits the Database.execute(...) helper and returns a boolean derived from whether any rows were returned.

Known callers and context:
    - No direct internal callers are present within this Database class implementation (no references to this method were found in this module).
    - Typical callers are higher-level code paths that need to guard operations based on a table's existence (e.g., schema inspection, conditional data queries, migration or setup code). It is used during runtime checks where a quick existence test is required prior to further actions.

Why this is a separate method:
    - The check is a common, small primitive used throughout higher-level logic. Encapsulating the query here keeps higher-level code concise, centralizes parameterization (preventing SQL-injection), and isolates the exact sqlite_master query string in one place for maintainability and future changes.

## Args:
    table (str): Name of the table to check for existence. Must be a string suitable for use as the sqlite_master name parameter. The value is passed as a bound parameter (params=(table,)) — passing untrusted input is safe from SQL injection due to parameterization.

## Returns:
    bool: 
        - True if a table row matching the given name exists in sqlite_master.
        - False if no such table exists (no rows returned).
    Edge cases:
        - If the query returns any row at all, the method returns True (it does not inspect the row contents beyond truthiness).
        - An empty string or unusual identifier that does not match any sqlite_master entry results in False.

## Raises:
    - Any exception raised by Database.execute(...) may propagate unchanged. In particular:
        * QueryInterrupted (raised by execute when the SQLite operation was interrupted)
        * sqlite3.OperationalError or sqlite3.DatabaseError (execute re-raises these for SQL-level errors)
    - These are raised when the underlying SQLite query fails or is interrupted; table_exists itself does not catch these exceptions.

## State Changes:
    Attributes READ:
        - None directly by this method. (Indirectly, the awaited Database.execute(...) call reads attributes such as self.name and self.ds inside its execution path.)
    Attributes WRITTEN:
        - None. This method does not mutate any self.<attr> fields.

## Constraints:
    Preconditions:
        - self must be a fully-initialized Database instance whose execute(...) coroutine can be awaited (connections prepared as needed by execute).
        - table must be a string (None is allowed syntactically but will not match any table name; passing None is not meaningful).
    Postconditions:
        - No modification to database state is performed (the query is read-only).
        - The return value accurately reflects whether sqlite_master contained a matching table row at the time the query executed.

## Side Effects:
    - Executes a parameterized SQL read against the SQLite database (I/O on the database file or in-memory DB).
    - Triggers the tracing wrapper (trace) used by execute, which may record SQL and params for telemetry/logging.
    - May block awaiting database I/O; subject to the same time limits and executor behavior enforced by Database.execute (e.g., sql_time_limit_ms, use of thread executor).

### `datasette.database.Database.table_names` · *method*

## Summary:
Return a list of all table names in the database by querying sqlite_master; does not modify the Database object's state.

## Description:
Calls the Database.execute helper to run a schema discovery query against sqlite_master and extracts the first column from each returned row as a table name.

Known callers and contexts:
- Database.table_counts: enumerates tables to count rows per table during inspection or metadata reporting.
- Database.hidden_table_names: used while computing which tables are hidden or visible.
- Any higher-level code that needs to discover available tables for routing, introspection, or UI metadata (e.g., request handlers that list tables).
These callers invoke table_names during normal request handling, background inspection, or when preparing API responses that include schema information.

Why this is a separate method:
- Encapsulates the single-purpose schema query and the common result-shaping (extracting the name column) so callers do not duplicate SQL or row-parsing logic.
- Keeps higher-level logic (counts, visibility checks, metadata gathering) decoupled from the low-level SQL used to discover tables and centralizes future changes to how table discovery is performed.

## Args:
    None

## Returns:
    list[str]: A list of table name strings (one per table). If no tables exist, returns an empty list.
    Notes:
        - The implementation extracts the first column (index 0) from each row in Results.rows; Results.rows may contain sqlite3.Row or tuple-like rows, so indexing is used.
        - Caller should expect simple string values; if the database contains unusual names (e.g., binary or non-UTF-8), the underlying sqlite3 behavior applies and may raise during execution or return byte-like objects depending on connection configuration.

## Raises:
    - QueryInterrupted: If the underlying query is interrupted by the sqlite_timelimit enforcement (the wrapped execute raises this when sqlite3 reports "interrupted").
    - sqlite3.OperationalError or sqlite3.DatabaseError: Propagated for SQL or database-level failures encountered while executing the query.
    - Any other exception raised by Database.execute or the executor (e.g., errors from tracing, time-limit context managers, or executor infrastructure) will propagate to the caller.

## State Changes:
Attributes READ:
    - self.execute (invoked), which in turn may read:
        - self.ds (to determine page_size, sql_time_limit_ms, executor, max_returned_rows, etc.)
        - self.name (used in tracing and when preparing connections)
    - Indirectly may access connection caches prepared by execute/execute_fn.

Attributes WRITTEN:
    - None. This method does not modify any self.<attr> fields.

## Constraints:
Preconditions:
    - The Database instance must be properly initialized and able to execute SQL (i.e., its underlying connection(s) or executor must be functional).
    - No arguments are required.

Postconditions:
    - The returned list contains one string per row returned by the query "select name from sqlite_master where type='table'".
    - The Database object's attributes remain unchanged by this call (no cached state is modified by table_names itself).

## Side Effects:
    - Executes a read-only SQL query on the database connection via Database.execute; any side effects are those of running that SQL (the query itself is a schema select and has no intentional data modifications).
    - May trigger execute-level side effects: tracing calls, sqlite_timelimit usage, and potential logging to stderr on SQL errors.

### `datasette.database.Database.table_columns` · *method*

## Summary:
Return the list of column names for the given table by invoking the low-level table-inspection helper within this Database's connection context.

## Description:
This asynchronous method delegates to the utils.table_columns helper to obtain column names, running that helper via this Database's execute_fn so connection management and threading are handled consistently.

Known callers:
- Database.label_column_for_table — uses the returned column names to select a display label column.
- Other callers in the codebase that require only column names (UI rendering, metadata routines, or helper utilities).

When called:
- Invoked at runtime whenever schema information (column names) is required — for request handling, metadata inspection, or other runtime schema-aware logic.

Why this method exists:
- Centralizes an async, connection-aware way to fetch column names on the Database object surface.
- Keeps connection handling (including executor/threading and connection preparation) inside execute_fn rather than duplicating that logic where column names are needed.
- Delegates actual schema parsing to utils.table_columns, avoiding duplication of inspection logic.

## Args:
    table (str): Name of the table to inspect. Passed unchanged to the underlying helper; must be a string acceptable to SQLite/inspection helpers. No additional validation or quoting is performed by this method.

## Returns:
    list[str]: Ordered list of column names returned by utils.table_columns (which itself builds names from table_column_details). The exact behavior when a table is absent or when unusual schema constructs are present is determined by the underlying helper (see utils.table_columns / table_column_details).

## Raises:
    Propagates any exception raised during connection creation/preparation or by the underlying utils.table_columns helper, for example:
    - sqlite3.OperationalError or sqlite3.DatabaseError raised by SQLite operations performed by the helper.
    - Any exception raised inside self.ds._prepare_connection, the connection creation, or execute_fn.
    There are no additional exception translations performed by this method.

## State Changes:
Attributes READ:
    - self.ds: consulted by execute_fn to determine whether to run synchronously or in an executor and to prepare connections.
    - self.name: used by execute_fn/connection-preparation logic for per-database connection handling.
    - self._read_connection: inspected by execute_fn to check for an existing cached read connection.

Attributes WRITTEN:
    - self._read_connection: may be set by execute_fn if no cached read connection exists and the synchronous execute path is taken (i.e., self.ds.executor is None). In the threaded/executor path, a per-thread or per-database connection may be created and cached on an external connections object instead (outside self).

## Constraints:
Preconditions:
    - self must be a properly-initialized Database instance.
    - table must be a string naming the intended table. This method does not validate that the table exists; such checks (and their specific outcomes) are the responsibility of the underlying helper.

Postconditions:
    - Returns a list of column name strings as produced by the underlying helper.
    - If a read connection did not previously exist and the synchronous path is taken, self._read_connection will be created and prepared.

## Side Effects:
    - May open a new SQLite connection (via self.connect()) and call self.ds._prepare_connection(conn, self.name).
    - Performs read-only schema inspection operations via utils.table_columns (which consults table_column_details).
    - When the Datasette instance uses an executor, the inspection runs in a worker thread; a per-worker or per-database connection may be cached on a shared external object (outside this Database instance).

### `datasette.database.Database.table_column_details` · *method*

## Summary:
Asynchronously returns the list of detailed column metadata for a table by delegating a PRAGMA-based inspection to the Database execution helper; does not modify the Database instance.

## Description:
This coroutine wraps the synchronous helper utils.table_column_details in the Database object's execution mechanism (self.execute_fn) and returns its output. The helper inspects SQLite schema using PRAGMA table_xinfo when available, falling back to PRAGMA table_info and appending a synthetic hidden flag. The table name is escaped by the helper before being embedded in the PRAGMA statement.

Known callers and lifecycle context:
    - No direct callers are present in the supplied snapshot. In a running application this method is intended for use wherever table schema must be inspected (for example: request handlers that render schema metadata, admin/inspection endpoints, or tools that generate UI/API documentation). It is called during request handling or metadata-collection phases that run in asynchronous code and must call into synchronous DB inspection logic.

Why this is a separate method:
    - Separation of concerns: low-level PRAGMA and row normalization logic is implemented in utils.table_column_details; this method exists to convert that synchronous helper into an awaitable operation according to the Database object's execution protocol (via self.execute_fn). Keeping the async boundary here centralizes how synchronous DB callables are scheduled/executed.

## Args:
    table (str): Name of the table to inspect. The value is forwarded to utils.table_column_details, which escapes it using escape_sqlite before embedding in the PRAGMA statement. Supplying a non-string will be passed through to the helper and may cause the helper or SQLite to raise an exception.

## Returns:
    list: A list of Column namedtuple instances (one per column) as produced by utils.table_column_details.
        - When SQLite supports PRAGMA table_xinfo, each Column is constructed directly from a table_xinfo row.
        - When table_xinfo is not supported, each Column is constructed from a table_info row with a trailing hidden flag value of 0 appended (the helper builds Column(*(list(r) + [0])) to normalize shape).
        - If no rows are returned by the PRAGMA (table does not exist or has no columns), an empty list is returned (the helper builds the list via a list comprehension over fetchall()).

## Raises:
    - Propagates any exception raised by self.execute_fn or by utils.table_column_details without alteration. Typical sources of such exceptions include SQLite errors raised during PRAGMA execution or runtime errors within the helper. This method itself adds no new exception types.

## State Changes:
    Attributes READ:
        - self.execute_fn (invoked/awaited)

    Attributes WRITTEN:
        - None. The Database instance is not mutated by this call.

## Constraints:
    Preconditions:
        - The Database instance must provide an awaitable execute_fn that, when awaited with a callable like lambda conn: ..., will invoke that callable with a connection-like object and return its result.
        - The connection provided by execute_fn must be compatible with utils.table_column_details (i.e., support conn.execute and fetchall used by PRAGMA).

    Postconditions:
        - The Database object remains unchanged.
        - The coroutine completes with the list returned by utils.table_column_details or raises an exception propagated from the execution helper or the helper itself.

## Side Effects:
    - Performs a read-only PRAGMA query (table_xinfo or table_info) on the database connection supplied by self.execute_fn. No filesystem or network IO is performed by this method itself; any side effects are limited to the database engine's internal state/observation of the PRAGMA.

## Minimal usage example:
    # Awaitable call from async context; result is a list of Column namedtuples.
    columns = await database.table_column_details("my_table")
    # columns is [] if the table has no columns or does not exist.

### `datasette.database.Database.primary_keys` · *method*

## Summary:
Return the ordered list of primary key column names for a table by running schema-inspection on a database connection; may create or reuse a read connection or dispatch the work to an executor.

## Description:
This async method delegates to the shared execute_fn helper to run the detect_primary_keys schema-inspection function on a real sqlite3.Connection. The method itself is a thin async wrapper so callers can simply await the primary-key discovery without handling connection management or executor dispatch.

Known callers and context:
- Called by higher-level Datasette code that needs to know how rows are identified (HTTP views, admin/inspection endpoints, metadata helpers).
- Typically used during request-time inspection or when building links/row-identifier logic for query results.

Why this is a separate method:
- Encapsulates the common pattern of executing a read-only schema operation under Datasette's connection and executor conventions.
- Keeps callers free from connection lifecycle and executor details, and centralizes a single, testable point for primary-key lookup behavior.

## Args:
    table (str): Table name to inspect. Must be a string representing the table name as stored in the database. Non-string values will likely lead to an error in the underlying SQLite calls.

## Returns:
    list[str]: A list of primary key column names for the given table.
    - Returns an empty list when there are no declared primary key columns.
    - May also be empty if the table does not exist (behavior depends on detect_primary_keys / table_column_details).

Example (plain text):
    Awaiting this method returns the primary key columns:
    await db.primary_keys("my_table")  ->  ["id"]

## Raises:
    Exception: Any exception raised by execute_fn, the underlying sqlite3 connection, or detect_primary_keys will propagate to the caller.
    - Callers should expect and handle database-related exceptions originating from SQLite operations (they will not be swallowed here).

## State Changes:
Attributes READ:
    - self.execute_fn (method): invoked to run the detection logic.
    - self.ds and self.name: read/used indirectly by execute_fn when preparing connections.

Attributes WRITTEN:
    - self._read_connection: may be created and assigned if no read connection exists and self.ds.executor is None (execute_fn calls connect() in that branch).
    - self._all_file_connections: connect() may append a newly created sqlite3.Connection to this list when a new file-backed connection is made.
    - Note: if self.ds.executor is not None, execute_fn will instead create and cache connections in the executor/thread-local path (so self._read_connection may remain unchanged).

## Constraints:
Preconditions:
    - The Database instance must be initialized with a valid ds (Datasette) object and the database identification (self.name) as needed by higher-level callers.
    - The table argument should be a valid table name string.

Postconditions:
    - Returns a list of primary key column names (possibly empty) if successful.
    - If a read connection was required and the executor is not being used, a read connection will be created and stored on the Database instance.

## Side Effects:
    - Performs read-only SQLite schema queries (no network I/O).
    - May create a new sqlite3.Connection and register it on the Database instance (see Attributes WRITTEN).
    - May offload the work to a configured executor (self.ds.executor), in which case connection objects may be created and cached outside the Database instance.

### `datasette.database.Database.fts_table` · *method*

## Summary:
Check whether a given table has a corresponding SQLite full-text-search (FTS) table and return that FTS table name if present; this call may initialize or cache a read sqlite3.Connection on the Database object (or on a module-level connection store when using an executor).

## Description:
Known callers / typical contexts:
- Called by request handlers, metadata/inspection routines, or UI/search features that need to know whether a table is backed by an FTS table in order to enable search-related functionality.
- Usually invoked during request handling or internal metadata inspection (i.e., when code needs to decide how to present or query a table).

Why this is its own method:
- Encapsulates the common pattern of running a synchronous connection-bound helper (detect_fts) via the Database.execute_fn helper so that connection creation/caching and executor decision logic are not duplicated where FTS detection is needed.
- Keeps FTS-detection logic isolated from higher-level code that consumes the result.

## Args:
    table (str):
        - The sqlite table name to check (expected to be the plain table name, not a schema-qualified name).
        - Must be a non-empty string representing an exact sqlite_master.name value for the table.
        - Do not pass untrusted raw input without validating/normalizing first: detect_fts composes SQL using Python string formatting, so names containing quotes or SQL metacharacters can produce SQL errors.

## Returns:
    Optional[str]:
        - The name of the FTS table (commonly "{table}_fts") if an FTS table exists for the given table.
        - None if no associated FTS table is found.
        - The returned value is exactly the return value of detect_fts(conn, table) executed under execute_fn.

## Raises:
    - Any exception raised while obtaining or preparing the sqlite3.Connection:
        * sqlite3.OperationalError, sqlite3.DatabaseError, OSError, etc., as propagated by self.connect() or self.ds._prepare_connection(conn, self.name).
    - Any exception raised by detect_fts while executing its SQL: typically sqlite3.DatabaseError or sqlite3.OperationalError if the composed SQL is invalid (for example, table contains unescaped quotes).
    - If the Datasette instance is configured with an executor and module-level connection caching is misconfigured, errors from the executor path (e.g., NameError if the module-level 'connections' object is missing) may propagate.
    - Any exception raised by execute_fn is propagated to the caller.

## State Changes:
Attributes READ:
    - self.ds (inspected to decide executor behavior and used to call _prepare_connection)
    - self.name (used as the cache key for module-level connection storage when an executor is configured)

Attributes WRITTEN (may be modified by the underlying execute_fn call):
    - self._read_connection: may be created and cached when ds.executor is None.
    - module-level connections object: when ds.executor is set, a connection attribute keyed by self.name may be created on the module-level connections object.
    - Indirectly, self._all_file_connections may be appended to when new file-backed connections are created by connect().

## Constraints:
Preconditions:
    - table must be a str identifying a single sqlite table name (not a SQL expression, not schema-qualified with a dot).
    - Callers must await the coroutine to obtain the return value.
    - If ds.executor is not None, the passed fn (detect_fts) will run on a worker thread and must not rely on asyncio-only state.

Postconditions:
    - No modifications are made to database data or schema by this call.
    - If an FTS table exists, the returned string is the FTS table name; otherwise the return is None.
    - After a successful call, a read connection is likely cached either on self._read_connection (no-executor case) or on the module-level connections object (executor case), making subsequent calls cheaper.

## Side Effects:
    - Opens and prepares a sqlite3.Connection (calls self.connect() and self.ds._prepare_connection), which involves I/O and OS resources.
    - When run without an executor, the synchronous detect_fts call executes on the event-loop thread and can block the loop for the duration of the operation.
    - When run with an executor, detect_fts executes on a worker thread; module-level connection caching is mutated.
    - No changes are made to database tables or rows by detect_fts itself.

### `datasette.database.Database.label_column_for_table` · *method*

## Summary:
Return a best-effort human-readable column name for rows of the given table (or None when no reasonable label column can be determined). This inspects metadata and schema only and does not modify the Database object.

## Description:
This asynchronous helper selects a single column to use as a display/label for rows in the specified table, following these precedence rules:

1. If Datasette table metadata for this database/table contains a truthy "label_column" value, that value is returned immediately (no schema query is performed).
2. Otherwise it queries the database for the table's column names and:
   - Prefers the first column whose name (case-insensitive) is "name" or "title". The match uses a lowercased comparison but the returned string preserves the original column name as reported by the database.
   - If no "name"/"title" column is found and the table has exactly two columns, and one of the columns is exactly the literal string "id" or "pk" (checked against the column names as-is, i.e. case-sensitive membership), it returns the other column.
3. If none of the above produce a candidate, the method returns None.

Known callers and lifecycle:
- No direct callers are visible in this file snapshot. Conceptually it is used by UI rendering, API endpoints, or other presentation-layer code that needs a concise human-readable label for table rows at request time or during schema/metadata inspection.
- It runs at the time a caller needs a label and will perform metadata lookup and possibly a read-only schema query.

Why this is a separate method:
- Centralizes the label-selection heuristic and the asynchronous DB-access required to obtain column names, avoiding duplication across callers and keeping precedence rules in a single place.

## Args:
    table (str): Table name to inspect. Required. Must be a valid table identifier for this database.

## Returns:
    Optional[str]:
        - The chosen column name string when a candidate is found (preserves the database-reported case).
        - None when no suitable column is found.
    Notes:
        - When metadata provides a truthy "label_column", that exact value is returned.
        - If multiple columns match "name"/"title", the first match in the column order is returned.
        - If the table has zero columns, returns None.

## Raises:
    This method does not explicitly raise new exception types, but it will propagate exceptions raised by:
        - self.ds.table_metadata(self.name, table)
        - await self.execute_fn(lambda conn: table_columns(conn, table))
    Specific propagated exceptions may include sqlite3.OperationalError, sqlite3.DatabaseError, QueryInterrupted, or other exceptions raised by execute_fn or the table_columns utility.
    Edge-case note:
        - If the table has exactly two columns and both column names are "id" and "pk" (in some order), the selection logic will attempt to return the "other" column but that will produce an empty list and raise an IndexError. Callers should be aware this pathological case could raise IndexError unless handled upstream.

## State Changes:
    Attributes READ:
        - self.ds (used for metadata lookup and influences execute_fn behavior)
        - self.name (database name passed to ds.table_metadata)
        - self.execute_fn (invoked to run table_columns on a connection)
    Attributes WRITTEN:
        - None. The method performs no writes to the Database object.

## Constraints:
    Preconditions:
        - self.name should be set (it is used when calling ds.table_metadata).
        - table should identify an existing table; otherwise underlying DB access may raise.
    Postconditions:
        - No mutation of self.
        - The return value conforms to the documented precedence rules (string or None), or an exception from underlying calls may be propagated.

## Side Effects:
    - Performs read-only database access via self.execute_fn(...) to obtain column names; this may open or reuse a connection and may run in an executor thread depending on Datasette's configuration.
    - No writes to the database or other external side effects are performed.
    - Exceptions from underlying metadata lookup or DB access may propagate to the caller.

### `datasette.database.Database.foreign_keys_for_table` · *method*

## Summary:
Return the list of outbound foreign-key relationships declared on a table by executing a PRAGMA query against the database; the result is retrieved via the Database connection abstraction and does not modify database state.

## Description:
This async helper obtains a sqlite3.Connection via Database.execute_fn and runs the utility get_outbound_foreign_keys on that connection and the provided table name. It is typically called during metadata inspection and request handling whenever callers need to know which columns on this table reference columns on other tables (for example when building relationship information for a table page, rendering related-record links in the UI, or when computing schema metadata).

Known callers / contexts:
- Request handlers or view-rendering code that show table relationships or need foreign-key metadata.
- Internal metadata inspection pipelines or administration endpoints that list or act on foreign-key relationships.
- Other Database helper methods that require outbound foreign-key lists for a specific table.

Why this is a separate method:
- Encapsulates the common pattern of running a small, synchronous DB-bound utility (get_outbound_foreign_keys) via the database's execute_fn helper so the same executor/connection caching logic is reused.
- Keeps callers simple (they await a single async method) and centralizes error propagation and connection preparation semantics.

## Args:
    table (str):
        - The name of the table to inspect. This is used as an SQL identifier inside a PRAGMA statement (not a bound SQL parameter).
        - Must be a valid SQLite identifier or table name present in the database. Passing arbitrary user-controlled text without validation may produce an sqlite3.OperationalError if it results in invalid SQL.
        - No default value; required.

## Returns:
    list[dict]:
        - Each list item is a dict with the keys:
            - "column" (str): column name on the current table that references another table.
            - "other_table" (str): the name of the referenced table.
            - "other_column" (str): the column name in the referenced table.
        - Possible return values:
            - An empty list [] when the table declares no outbound foreign keys or when the named table does not exist or is inaccessible.
            - A list of one-entry dictionaries for each simple (non-compound) foreign-key relationship. Compound foreign keys (multi-column FKs) are filtered out by get_outbound_foreign_keys and therefore do not appear in the returned list.

## Raises:
    - Any exception propagated from Database.execute_fn or from get_outbound_foreign_keys, including but not limited to:
        - sqlite3.OperationalError or sqlite3.DatabaseError (for SQL/PRAGMA execution errors).
        - Exceptions from connection creation or preparation (e.g., OSError when opening the DB file, or errors raised by self.ds._prepare_connection).
        - Any runtime exception raised by the utility code (e.g., programming errors). Such exceptions propagate directly to the caller.
    - Note: because the PRAGMA is constructed as an SQL identifier substitution, malformed/unsafe table names may trigger sqlite errors; callers should ensure table names are valid identifiers.

## State Changes:
Attributes READ:
    - self.ds.executor: indirectly read by execute_fn to decide execution strategy.
    - self._read_connection: may be read by execute_fn to determine whether to reuse an existing read connection when no executor is configured.
    - self.name: used by execute_fn when caching per-database connections on executor threads.
    - self.ds: used by execute_fn to call self.ds._prepare_connection if a connection must be prepared.

Attributes WRITTEN:
    - self._read_connection: may be set by execute_fn if no cached read connection existed and ds.executor is None.
    - module-level connections store (attribute on the module-level connections object keyed by self.name): may be set by execute_fn when running in an executor to cache a per-database connection.
    - Note: this method itself does not modify database rows or schema.

## Constraints:
Preconditions:
    - The caller must await the returned coroutine (method is async).
    - table must be a non-empty string representing the target table name.
    - fn passed into execute_fn (the lambda wrapping get_outbound_foreign_keys) must be safe to run on a worker thread if the Datasette instance is configured with an executor.

Postconditions:
    - No modification to database content or schema is performed.
    - The return value is a list describing simple (non-compound) outbound foreign-key relationships for the named table, or an empty list if none exist.
    - If execution succeeds, a prepared sqlite3.Connection will have been created and cached either on self._read_connection (no executor) or on the module-level connections cache (executor path) as a side effect of execute_fn's behavior.

## Side Effects:
    - May open a sqlite3 connection (via self.connect) and call self.ds._prepare_connection(conn, self.name) as part of execute_fn; these operations can perform I/O and change connection PRAGMAs.
    - The work may run on the event loop thread (blocking it) or on a background executor thread depending on self.ds.executor; thus long-running or blocking calls executed by get_outbound_foreign_keys would block the event loop if no executor is configured.
    - Exceptions raised by the underlying connection operations or PRAGMA execution will propagate to the caller.

### `datasette.database.Database.hidden_table_names` · *method*

## Summary:
Returns a list of table-name strings that should be treated as hidden for this Database instance. The returned list is computed from database queries, optional Spatialite detection, and user-supplied metadata; it does not modify the Database object.

## Description:
- What it does: Gathers and returns names (or name prefixes) of tables that callers should hide from normal listings. The method:
  1. Runs a database query (via self.execute) to seed an initial list of hidden table names/prefixes from the database itself.
  2. Calls detect_spatialite via self.execute_fn to determine whether Spatialite-specific tables should be considered hidden; if Spatialite is present, appends a fixed set of Spatialite-related names and the results of a second database query (via self.execute).
  3. Reads Datasette-level metadata (self.ds.metadata(database=self.name)) and adds any tables whose metadata entry includes a truthy "hidden" flag.
  4. Expands the hidden list by appending any actual table names (from await self.table_names()) that start with any of the already-collected hidden prefixes.
- Known callers and lifecycle stage:
  - No specific callers were found in the provided code snapshot. Conceptually, this method is typically invoked when preparing responses for endpoints or UI elements that list database tables (so that internal or otherwise-hidden tables are omitted). It is also reusable by any component that needs a canonical list of hidden table name patterns.
- Why it's a separate method:
  - The logic combines database queries, Spatialite detection, and metadata lookup, and is reused in places that need a canonical hidden-table list. Separating it keeps table-listing code simpler, centralizes the rules for what is hidden, and avoids duplication of database I/O and metadata handling.

## Args:
    None

## Returns:
    list[str]: A list of table name strings or table-name prefixes to treat as hidden.
    - Values are collected in the order discovered (initial query rows, optional Spatialite names and second query rows, metadata-driven names, then expansions from actual table names).
    - The list may be empty.
    - The list may contain duplicate names (the method appends values without de-duplication).
    - The returned elements are plain strings (the method returns r[0] values from query results and explicit string literals).

## Raises:
    - Any exception raised by self.execute or self.execute_fn (propagated unchanged). In practice these can include:
        * QueryInterrupted (raised when a timed or interrupted SQL operation is detected)
        * sqlite3.OperationalError or sqlite3.DatabaseError (errors executing SQL)
      These exceptions are not caught in this method and will propagate to the caller.
    - Any exception raised by self.ds.metadata(...) will propagate unchanged.
    - Any exception raised by self.table_names() will propagate unchanged.

## State Changes:
- Attributes READ:
    - self.ds (used to call metadata and in execute/execute_fn behavior)
    - self.name (passed to ds.metadata)
    - self.execute (invoked to run SQL and obtain initial/secondary hidden-name rows)
    - self.execute_fn (invoked with detect_spatialite to detect Spatialite presence)
    - self.table_names (invoked to obtain actual table names to expand prefixes)
- Attributes WRITTEN:
    - None. The Database instance is not mutated by this method.

## Constraints:
- Preconditions:
    - The Database instance must be initialized (self.ds and self.name should be valid for the datasource). If self.ds.metadata or the database connection mechanisms are not available, the method will raise whatever exceptions those calls raise.
    - This method must be awaited (it is async).
- Postconditions:
    - Returns a list[str] representing hidden table names and prefixes.
    - The Database object remains unchanged (no attributes are modified).
    - Any database reads performed (via self.execute / self.execute_fn) have already completed or their exceptions propagated.

## Side Effects:
    - Performs read-only SQL operations via self.execute (this may create or reuse a read database connection and perform I/O).
    - Calls self.execute_fn(detect_spatialite), which may run code on a connection thread and perform SQL to detect Spatialite (see detect_spatialite: it queries sqlite_master for geometry_columns).
    - No writes to the database are performed by this method.
    - No external network calls or file system writes are performed directly by this method, but opening/creating connections (via execute/execute_fn) may allocate resources.

### `datasette.database.Database.view_names` · *method*

## Summary:
Returns a list of all view names defined in the SQLite database by querying sqlite_master; does not modify the Database object's state.

## Description:
This asynchronous convenience method issues a single read query against the database's sqlite_master table to retrieve objects of type 'view' and returns their names as a Python list.

Known callers and context:
- No direct callers were found in the provided repository snapshot. Conceptually this method is intended for use wherever the codebase needs an inventory of views (for example: administration/inspection endpoints, metadata collection, or UI listing of views).
- It is invoked during runtime when code needs to enumerate database views; being async it fits into the same execution model as other Database.* async helpers that delegate SQL work to execute/execute_fn.

Why this is a separate method:
- Encapsulates the SQL used to list views so callers don't need to repeat the sqlite_master query.
- Keeps higher-level code concise and expressive (callers receive a simple list[str] instead of dealing with result rows).
- Matches other Database helper methods that wrap common SQL or connection-level operations (table_names, table_exists, etc.).

## Args:
- None

## Returns:
- list[str]: A list of view names (strings). If the database has no views, returns an empty list.

Edge cases:
- If sqlite_master returns rows with a NULL name (highly unlikely for valid view entries), the returned list will include None at that position.
- The ordering of names is the order returned by SQLite (no explicit ORDER BY is applied).

## Raises:
- QueryInterrupted: if the underlying execute call raised this due to an "interrupted" sqlite error (propagated from execute).
- sqlite3.OperationalError or sqlite3.DatabaseError: if SQLite reports an operational/database error during the query (propagated from execute).
- Other exceptions raised by self.execute or the underlying I/O/connection code (propagated).

Exact trigger conditions:
- QueryInterrupted: raised by execute when SQLite returns an OperationalError/DatabaseError whose e.args == ("interrupted",).
- sqlite3.OperationalError / sqlite3.DatabaseError: raised by execute when the cursor.execute(...) call raises these errors and are not the special "interrupted" case.

## State Changes:
Attributes READ:
- None directly by this method. (It calls the instance method self.execute, which may read or create connection attributes internally; view_names itself does not access self.<attr>.)

Attributes WRITTEN:
- None. This method does not modify any self.<attr> fields.

## Constraints:
Preconditions:
- The Database instance should be properly constructed (connected to an existing SQLite file or memory database via its normal lifecycle). No method arguments are required.
- The underlying database must be accessible/readable by the process; otherwise execute will raise an error.

Postconditions:
- The Database object remains unchanged.
- The return value is a list of the name column values from sqlite_master where type='view'. If the query executes successfully, callers can rely on receiving a list (possibly empty) and no side-effect on Database state.

## Side Effects:
- Executes a read-only SQL query against the database connection (this will perform I/O: reading from the SQLite file or memory database).
- No writes to the database, no changes to in-memory Database attributes, and no external network calls are performed by this method itself.

### `datasette.database.Database.get_all_foreign_keys` · *method*

## Summary:
Return a mapping of every table in this database to its incoming and outgoing foreign keys, executing the underlying utils.get_all_foreign_keys on a properly prepared SQLite connection; may create and cache the database's read connection as a side effect.

## Description:
- Known callers:
    - No direct callers were discovered in the provided source snapshot. This is a public Database API intended for higher-level inspection/metadata code that needs a full foreign-key graph for the database.
- Invocation context / lifecycle:
    - Called when the application needs an overview of all foreign-key relationships for a database (for example, to build relationship graphs, serve metadata endpoints, or perform cross-table analysis). It is an async method meant to be called from async request handlers or other async inspection code.
- Why this is its own method:
    - This method is a small, focused wrapper that delegates to the shared execute_fn machinery. Keeping it separate avoids duplicating connection/Executor handling and centralizes the semantics of "run a synchronous utility function against this database's connection (possibly in a thread pool)".

## Args:
    None

## Returns:
    dict[str, dict]: Mapping keyed by table name (str). Each value is a dict with two keys:
        - "incoming" -> list[dict]: For each incoming foreign key (i.e., another table references this table), a dict with keys:
            - "other_table" (str): the table holding the referencing column
            - "column" (str): the column on this table that is referenced
            - "other_column" (str): the column on other_table that references this table's column
        - "outgoing" -> list[dict]: For each outgoing foreign key (i.e., this table references another table), a dict with keys:
            - "other_table" (str): the table being referenced
            - "column" (str): the column on this table that references the other table
            - "other_column" (str): the column on other_table that is referenced
    Possible return-edge cases:
        - If the database has no tables, an empty dict is returned.
        - If a foreign-key definition references a non-existent table, that particular reference is skipped by the utility function (it will not appear in the mapping).
        - The returned structure exactly mirrors what utils.get_all_foreign_keys produces.

## Raises:
    - Propagates exceptions raised while creating or preparing the connection:
        - Exceptions from self.connect (e.g., I/O or sqlite3 connection errors) or from self.ds._prepare_connection.
    - Propagates exceptions raised by the underlying SQLite operations performed by utils.get_all_foreign_keys:
        - Typical examples include sqlite3.OperationalError or sqlite3.DatabaseError if the database file is invalid, locked, or otherwise raises SQLite errors.
    - Any other exception raised by utils.get_all_foreign_keys or get_outbound_foreign_keys will propagate unchanged.

## State Changes:
- Attributes READ:
    - self.ds (used to check for an executor and to call self.ds._prepare_connection)
    - self.ds.executor (checked to decide sync vs threaded execution)
    - self.name (passed to ds._prepare_connection and used when storing per-database connections in threaded mode)
    - self._read_connection (checked to see if a cached read connection already exists)
- Attributes WRITTEN:
    - self._read_connection may be set (initialized and cached) if no read connection existed prior to the call.

## Constraints:
- Preconditions:
    - The Database instance must be initialized (self.ds must be present).
    - No other preconditions are required by this wrapper method, but underlying SQLite requirements apply (valid database file or memory database).
- Postconditions:
    - After a successful call, self._read_connection will be initialized and prepared (via self.ds._prepare_connection) if it was not already present.
    - The returned value is a mapping of table names to their incoming/outgoing foreign-key lists as produced by utils.get_all_foreign_keys.

## Side Effects:
    - I/O: may open a new SQLite read connection to the database file (disk I/O) if a cached read connection does not already exist.
    - Calls self.ds._prepare_connection(conn, self.name), which may perform additional connection initialization or mutate external state in the DataSource (ds).
    - Concurrency:
        - If self.ds.executor is None, the wrapped utility runs synchronously on the current event loop thread and can block the event loop while it performs database operations.
        - If self.ds.executor is set, the utility runs in the configured executor (off the event loop) and may create or reuse a per-database connection object stored on a module-level connections object (not on self).
    - No mutation of database schema is performed by this call; it only reads schema metadata.

### `datasette.database.Database.get_table_definition` · *method*

## Summary:
Return the SQL definition for a table/view and its non-null CREATE INDEX statements as a single concatenated SQL string, or None if the named object is not present.

## Description:
This coroutine queries sqlite_master to fetch the "sql" column for the named object (default type "table") and then fetches any index definitions that reference that table. It preserves the original SQL text from sqlite_master, appending a trailing semicolon to each statement and joining them with newline characters into a single string.

Known callers:
    - No call sites were visible in the provided snippet. Typical callers are schema-inspection, export, or migration code that needs the DDL for a table/view (for example when showing schema to a user, generating a dump, or recreating the table elsewhere).

Why this is a separate method:
    - Encapsulates the SQL retrieval logic and index-collection in a single place so callers get a complete DDL fragment for a table/view without duplicating the sqlite_master queries. It isolates SQL details and the index-query from higher-level logic.

## Args:
    table (str):
        Name of the table/view as stored in sqlite_master.name. Must be a string or string-like object accepted by the underlying database parameter binding.
    type_ (str, optional):
        The sqlite_master.type to filter on (default "table"). Common values include "table" and "view"; any string may be passed and will be used verbatim in the sqlite_master WHERE clause.

## Returns:
    str or None:
        - If sqlite_master contains an entry matching name=:n and type=:t, returns a single str containing:
            * The object's "sql" text from sqlite_master with a ";" appended.
            * Followed by zero or more index "sql" texts (each with ";" appended), for indexes whose tbl_name equals the table name and whose sql is not null.
            * Statements are concatenated with newline ("\n") separators, in the order: the object's sql first, then its indexes.
        - If no sqlite_master row matches the given name and type, returns None.

## Raises:
    - Any exception raised by awaiting self.execute will propagate (for example, database operational errors raised by the database driver).
    - TypeError will occur if the retrieved sqlite_master.sql value for the main object is None (the code concatenates the value with ";" without checking for None).
    - Indexing errors (e.g., if the rows returned do not contain the expected column) would propagate as the code indexes the first row/column directly.

## State Changes:
    Attributes READ:
        - None of the instance's data attributes are read directly. The method invokes the instance method self.execute (i.e., it depends on that method) but does not read self.<attr> fields.
    Attributes WRITTEN:
        - None. The method does not modify self or any self.<attr> fields.

## Constraints:
    Preconditions:
        - Must be called within an active asyncio event loop (it is an async coroutine and must be awaited).
        - The Database instance must expose an awaitable self.execute(sql, params) that returns an iterable of row tuples; rows are expected to contain the selected "sql" column at index 0.
        - The caller should pass a sensible table name; the code does not sanitize or validate beyond binding the value into the sqlite_master query.

    Postconditions:
        - If the function returns a non-None str, that string ends with semicolons after each statement and contains at least one (the object's sql).
        - If None is returned, no matching sqlite_master row existed for the provided name/type.

## Side Effects:
    - Performs database I/O by awaiting self.execute twice:
        1) To fetch the object's "sql" from sqlite_master.
        2) To fetch index "sql" rows for that table where sql is not null.
    - No filesystem, network, or external service calls are made other than the database operations performed via self.execute.

### `datasette.database.Database.get_view_definition` · *method*

## Summary:
Returns the full SQL definition for a named view (the view's CREATE statement plus any non-null CREATE INDEX statements) by delegating to the table-definition retrieval logic. Does not modify the Database object's state.

## Description:
This coroutine is a thin convenience wrapper around the generic table-definition routine, invoking that logic with type "view". It is used wherever callers need the DDL for a view — for example schema inspection, UI schema displays, export/dump generation, or migration tools that need to recreate a view on another database.

Known callers:
    - No explicit call sites are available in the provided snippet. Typical call points include schema endpoints, administrative UI pages, export/dump code, or any code path that displays or exports a view's DDL.

Why this is its own method:
    - Encapsulates the common intent "get the DDL for a view" as a semantically clear API (avoids callers needing to know the string literal "view" or how get_table_definition is parameterized).
    - Keeps higher-level code readable and prevents duplication of the type argument across the codebase.

## Args:
    view (str):
        The name of the view as stored in sqlite_master.name. Must be a string (or string-like object accepted by the underlying DB parameter binding). No further validation or sanitization is performed by this method.

## Returns:
    str or None:
        - If a sqlite_master entry exists with name == view and type == "view", returns a single string that contains:
            * The view's original "sql" text (from sqlite_master) with a trailing ";" appended.
            * Followed by zero or more index "sql" texts (each with ";" appended) for indexes whose tbl_name equals the view name and whose sql is not null.
            * Statements are joined with newline ("\n") separators.
        - If no matching sqlite_master row exists, returns None.
        - (Behavior and exact formatting mirror Database.get_table_definition.)

## Raises:
    - Any exception propagated from Database.get_table_definition or the underlying self.execute calls (for example sqlite3.OperationalError or sqlite3.DatabaseError).
    - TypeError may occur if the underlying sqlite_master.sql value for the main object is None and code attempts to concatenate it with a string (this is inherited from get_table_definition's behavior).
    - Any other runtime errors raised by the database layer or awaitable machinery will propagate.

## State Changes:
    Attributes READ:
        - None of the Database instance's data attributes are read directly by this method.
        - Indirectly invokes self.get_table_definition which performs database reads via self.execute.
    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - Must be awaited within an active asyncio event loop (it is an async coroutine).
        - The Database instance must be properly initialized and able to execute SQL via its get_table_definition -> self.execute path.
        - The caller should supply a valid view name; the method does not sanitize or validate the name beyond passing it to the parameterized query used by get_table_definition.

    Postconditions:
        - If a non-None string is returned, it contains the view's CREATE statement and any non-null index CREATE statements, each terminated with ";" and joined by newlines.
        - The Database object's attributes remain unchanged.

## Side Effects:
    - Performs database I/O by calling Database.get_table_definition which awaits self.execute (queries sqlite_master); this may read from disk or otherwise interact with the configured SQLite connection.
    - No filesystem writes, network calls, or modifications to external objects are performed by this method itself.

### `datasette.database.Database.__repr__` · *method*

## Summary:
Return a concise, human-readable representation of the Database object including its name and optional status tags (mutable, memory, hash, size).

## Description:
This method builds and returns a one-line representation intended for debugging, logging, and interactive inspection. Typical callers include:
- Built-in repr() and str() usage (e.g., repr(database_instance)).
- Logging statements and debugging output where a short summary of the Database object is useful.
- Test assertions or error messages that include the object representation.
Lifecycle/context: invoked whenever a string representation of the Database is requested, typically during debugging, logging, or when the object is included in formatted output.

This logic is isolated in its own method because:
- __repr__ is the standard Python hook for object representation; keeping this logic in a dedicated method centralizes formatting and makes it easy to change the textual representation without affecting other code.
- It is a small, self-contained operation that reads object state and returns a pure string; inlining would duplicate formatting logic across the codebase.

## Args:
None.

## Returns:
str: A formatted string of the form "<Database: {name}>" or "<Database: {name} (tag1, tag2, ...)>". Possible tags included, in order:
- "mutable" — included if self.is_mutable is truthy.
- "memory" — included if self.is_memory is truthy.
- "hash={hash}" — included if self.hash is truthy; {hash} is interpolated from self.hash.
- "size={size}" — included if self.size is not None; {size} is interpolated from self.size.
Edge cases:
- If no tags apply, the returned value is exactly "<Database: {name}>".
- If tags apply, they are joined with ", " and placed inside parentheses after the name: "<Database: {name} (tagA, tagB)>".

## Raises:
None. The method performs only attribute reads and string formatting; it does not raise exceptions itself unless attribute access raises an unexpected AttributeError (i.e., if required attributes are missing).

## State Changes:
Attributes READ:
- self.is_mutable
- self.is_memory
- self.hash
- self.size
- self.name

Attributes WRITTEN:
- None. This method does not modify the object's state.

## Constraints:
Preconditions:
- The object must have the attributes listed under Attributes READ. In normal usage these are provided by the Database class initializer.
- self.name should be representable as a string (the implementation uses f-string conversion).

Postconditions:
- No attributes or external state are changed.
- The return value is a pure string derived from the read attributes and does not hold references that could mutate the Database.

## Side Effects:
- None. There is no I/O, no external service interaction, and no mutation of objects outside self.

## `datasette.database.WriteTask` · *class*

## Summary:
Lightweight container object that groups a callable ("fn"), a task identifier ("task_id"), and a reply queue ("reply_queue") for handoff between producers and a writer/worker.

## Description:
WriteTask is a minimal value-object whose sole purpose is to carry three related pieces of information together:
- fn: a callable representing the work to be executed (for example, a write operation).
- task_id: an identifier for this task (e.g., a string or uuid.UUID).
- reply_queue: a queue-like object where results, acknowledgements, or exceptions can be placed by the worker that executes fn.

This class does not execute fn, perform validation, or manage threading/async behavior itself — it only stores the three values. Typical callers instantiate WriteTask when scheduling work to be executed by another execution context (a dedicated writer thread, asyncio task that consumes a queue, or other worker). Those calling contexts are responsible for actually invoking fn and putting replies onto reply_queue; this class only aggregates the fields into one immutable set of attribute names (enforced via __slots__).

## State:
- __slots__: ("fn", "task_id", "reply_queue")
  - Enforces a fixed attribute set and prevents dynamic attribute creation.
- Attributes (set by __init__):
  - fn (callable)
    - Type: any callable. The implementation does not enforce signature or return type.
    - Typical values: functions, callables that accept a DB connection, or lambdas encapsulating a write operation.
    - Invariant: attribute exists and references the original object passed in; not validated for None.
  - task_id (any hashable or identifier)
    - Type: typically str or uuid.UUID but any value may be used.
    - Invariant: set to the value passed to __init__; no automatic generation or validation.
  - reply_queue (queue-like object)
    - Type: any object implementing queue semantics (e.g., queue.Queue, janus.Queue, asyncio.Queue); the class does not enforce an interface.
    - Invariant: set to the value passed to __init__; expected by convention to support put/put_nowait or async put operations by the worker.

Class invariants:
- Instances only have the three attributes named in __slots__.
- Attributes are assigned in __init__ and thereafter may be read or reassigned (no immutability guarantees beyond the restricted attribute set).
- The class makes no assumptions about callable execution, thread-safety, or queue implementation — those responsibilities lie with callers and consumers.

## Lifecycle:
- Creation:
  - Instantiate by calling WriteTask(fn, task_id, reply_queue).
  - All three parameters are required by __init__ (no defaults).
  - There is no built-in factory method; simple constructor use is expected.
- Usage:
  - Typical sequence:
    1. Producer constructs a WriteTask instance with a callable, an id, and a reply queue.
    2. Producer places the WriteTask into a scheduling queue (e.g., a thread-safe queue or async queue).
    3. A consumer (writer thread or async worker) retrieves the WriteTask, executes task.fn (in whatever context and with any required arguments that producer/consumer agreed on), and posts results or status onto task.reply_queue.
  - The class exposes no methods beyond attribute access; ordering and execution semantics are enforced by producers/consumers, not by this class.
- Destruction / cleanup:
  - No explicit cleanup API (no close() or context manager).
  - If reply_queue requires cleanup (e.g., closing an asyncio queue), that must be handled by caller/consumer.

## Method Map:
graph TD
    A[WriteTask class] --> B[__init__(fn, task_id, reply_queue)]
    B --> C[store fn -> self.fn]
    B --> D[store task_id -> self.task_id]
    B --> E[store reply_queue -> self.reply_queue]
    note right of A[WriteTask class] : No other methods

## Raises:
- __init__ does not raise any exceptions explicitly.
- Since __init__ only assigns attributes, exceptions could only arise from unusual runtime conditions (e.g., memory errors) but there is no parameter validation that would raise ValueError or TypeError.

## Example:
1. Producer prepares:
   - Choose or create a reply queue (e.g., a queue.Queue or an asyncio/Janus queue).
   - Define a callable fn that performs the desired write work (the callable's signature and behavior must be agreed between producer and consumer).
2. Create a task:
   - Instantiate WriteTask with the callable, a task identifier, and the reply queue.
3. Schedule and consume:
   - Put the WriteTask into a scheduling queue consumed by a worker.
   - Worker retrieves the WriteTask, calls task.fn(...) as appropriate, and posts result/status to task.reply_queue.
4. Cleanup:
   - Any queue-specific shutdown must be handled by the queue owner; WriteTask itself has no cleanup responsibilities.

Notes:
- This class is intentionally minimal and acts purely as a small structured record. It exists to make producer/consumer code clearer and to prevent scattering separate variables (fn, id, queue) through scheduling queues and worker code.

### `datasette.database.WriteTask.__init__` · *method*

## Summary:
Persist the provided task payload, identifier, and reply-channel onto the instance so the object reliably represents a single scheduled write operation.

## Description:
This initializer records the three constructor arguments as instance attributes and purposely performs no validation or execution. It is called when higher-level code constructs a WriteTask to represent work that will later be executed by a writer/worker. The typical point in the lifecycle is the enqueue or dispatch stage: code preparing a write will instantiate a WriteTask, then pass it to a queue or worker for execution.

Why this is a separate method:
- Separating construction from execution keeps task creation lightweight, testable, and free of side effects. It makes the minimal contract of a task explicit (callable payload, identifier, reply channel) without coupling creation to scheduling or execution logic.

Known callers and context:
- Any scheduler or producer that prepares write operations will call this initializer during the enqueue phase.
- Common reply_queue implementations used elsewhere in this codebase are janus.Queue, asyncio.Queue, or the standard library queue.Queue, but this constructor does not require any particular implementation — it only stores the object provided.

## Args:
    fn (any)
        The task payload. Intended to be a callable or object describing the work to perform, but the initializer accepts any value and stores it unchanged on self.fn.
    task_id (any)
        An opaque identifier for the task (commonly a string or uuid.UUID). The initializer does not validate or transform it; it is saved on self.task_id for later correlation of results.
    reply_queue (any)
        A queue-like object to receive the task result or notification. The initializer stores this value on self.reply_queue. Caller-provided queues commonly implement methods such as put/put_nowait; the constructor does not enforce an interface.

## Returns:
    None
    As with all Python constructors, __init__ returns None.

## Raises:
    None
    This method performs only attribute assignments and will not raise exceptions itself unless assignment fails due to an unusual metaclass/property on the instance (not applicable in normal usage).

## State Changes:
    Attributes READ:
        - None (the method does not read or depend on any pre-existing instance attributes)
    Attributes WRITTEN:
        - self.fn is set to the provided fn argument
        - self.task_id is set to the provided task_id argument
        - self.reply_queue is set to the provided reply_queue argument

## Constraints:
    Preconditions:
        - The caller must supply three positional arguments: fn, task_id, and reply_queue.
        - The constructor does not enforce types or interfaces; callers are responsible for supplying values compatible with the consumer that will execute the task.
    Postconditions:
        - After the call, the instance has public attributes fn, task_id, and reply_queue bound to the provided values.
        - No validation, scheduling, or side-effectful operations occur during initialization.

## Side Effects:
    - None: no I/O, no external service calls, and no mutations of objects outside the simple attribute assignments performed on self.

## Usage notes:
    - Treat the created WriteTask as a plain data container representing a piece of work to be executed later by a worker. For robust systems, ensure the caller provides a reply_queue implementation and a task_id suitable for tracing/correlation prior to construction.

## `datasette.database.QueryInterrupted` · *class*

## Summary:
Represents an interruption of a SQL query by wrapping the original error together with the SQL text and its parameters so callers can inspect context when handling interrupted queries.

## Description:
This exception type is intended to be raised when an in-progress SQL query is interrupted — for example by a timeout, a cancellation request, or when an underlying SQLite driver produces an interrupt/timeout error. Rather than losing the original SQL and parameter context, code creates a QueryInterrupted instance that carries:
- the original exception or error object (so handlers can inspect traceback or driver-specific details),
- the SQL string that was running,
- the parameters that were bound to that SQL.

Typical call sites: code that executes SQL and has to translate low-level driver exceptions (timeouts, interrupts) into higher-level exceptions for the application layer. When catching QueryInterrupted, handlers should inspect the .e attribute for the original exception and the .sql/.params attributes for reproducibility/logging.

This class intentionally exists as a small wrapper abstraction to centralize how query interruption information is passed through the codebase.

## State:
- e (object)
  - Type: typically Exception (or subclass) but can be any object representing the original failure.
  - Meaning: the original, lower-level exception or interrupt marker that caused the interruption.
  - Invariant: must be set to the passed value and not mutated by the QueryInterrupted instance.
- sql (str)
  - Type: str
  - Meaning: the SQL statement that was being executed when interrupted.
  - Constraint: callers should pass the SQL as a string; None is allowed if the caller does not have SQL context, but most uses will provide a string.
- params (tuple | list | dict | None)
  - Type: commonly a sequence (tuple/list) or mapping (dict) of bound parameters for the SQL.
  - Meaning: the parameter values or mapping supplied to the SQL execution.
  - Constraint: may be None if no parameters were used.

Class invariants:
- After initialization, attributes .e, .sql, and .params must exist and hold whatever values were supplied by the creator.
- The instance does not modify these attributes.

Important implementation note (observable behavior):
- The __init__ implementation does not call the base Exception.__init__ method; therefore the Exception.args tuple will remain empty and str(instance) will not include the wrapped message unless caller code sets it or Exception.__init__ is invoked. Consumers should therefore prefer inspecting .e,.sql,.params instead of relying on the string representation.

## Lifecycle:
Creation:
- Instantiate by calling QueryInterrupted(e, sql, params).
  - Required positional arguments: e, sql, params (no defaults).
  - Example values:
    - e: an Exception subclass instance such as sqlite3.OperationalError or a custom sentinel object.
    - sql: "SELECT * FROM table WHERE id = ?"
    - params: (123,) or {"id": 123} or None

Usage:
- Typically raised immediately in an except/handler that observes a low-level interruption:
  - create the QueryInterrupted instance with the original exception and SQL context and raise it (or re-raise after wrapping).
- Typical catch pattern:
  - except QueryInterrupted as qi:
      - inspect qi.e for driver-specific details and diagnostic information
      - log qi.sql and qi.params to aid reproducing the interrupted execution
      - decide whether to retry, abort, or surface the failure to callers

Destruction / cleanup:
- No special cleanup is required. The class does not hold external resources, file handles, or background threads.
- It is a plain exception object and relies on Python's GC for cleanup.

## Method Map:
graph TD
    A[Caller executing SQL] -->|Low-level interrupt/exception| B[Create QueryInterrupted]
    B --> C[Raise QueryInterrupted]
    C --> D[Caller or higher-level handler catches QueryInterrupted]
    D --> E[Inspect .e, .sql, .params & decide action]

(Only __init__ exists; no other instance methods are defined.)

## Raises:
- TypeError: if __init__ is called with the wrong number of positional arguments (Python's standard error for mismatched constructor signature).
- No other exceptions are raised by __init__ itself; it performs only attribute assignment.
- Note: downstream code that inspects .e may access attributes on that original exception which could raise attribute errors if the original exception is an unexpected type — this is a caller concern, not from QueryInterrupted itself.

## Example:
- Creation and raising (described as simple steps rather than embedding multi-line source blocks):
  1. In exception handler for a low-level DB error, create wrapper = QueryInterrupted(original_exception, sql_text, params).
  2. Raise wrapper to propagate the interruption with context.
  3. In an upper layer: catch QueryInterrupted as qi and then use qi.e for the original error details, qi.sql for the statement, and qi.params for bound parameters; log or decide on retry/abort.

Implementation hint:
- If you want str(exception) to include useful summary information, either call Exception.__init__ with a composed message inside QueryInterrupted.__init__ or implement __str__ to return a formatted string that includes sql and a short representation of params and the original exception.

### `datasette.database.QueryInterrupted.__init__` · *method*

## Summary:
Initializes a QueryInterrupted exception instance by storing the original error together with the SQL text and its parameters so handlers can inspect the interruption context.

## Description:
- Known callers and context:
    - Created where low-level database execution code detects an interruption, timeout, or driver-specific error and needs to propagate a higher-level exception that preserves context.
    - Typical call sites: code paths that execute SQL statements and catch sqlite3 or driver exceptions, then wrap them before re-raising or returning to higher layers. Example lifecycle step: catch driver error -> construct QueryInterrupted(original_error, sql_text, params) -> raise the wrapper.
- Why this is a separate method:
    - The constructor centralizes how interruption context (original exception, SQL, parameters) is attached to the wrapper exception object. Keeping this logic in __init__ (rather than inlining attribute assignment at call sites) ensures a consistent, minimal representation for all wrapped interruptions and makes later changes (for example adding normalization or validation) possible in one place.

## Args:
    e (Exception | object):
        The original, lower-level exception or interrupt marker that caused the interruption. May be any object, but callers typically pass an Exception instance (e.g., sqlite3.OperationalError).
    sql (str | None):
        The SQL statement that was being executed when interrupted. Callers should pass a string when available; None is allowed if SQL context is not present.
    params (tuple | list | dict | None):
        The bound parameters supplied to the SQL execution. Common forms are tuple/list for positional parameters or dict for named parameters. May be None if no parameters were used.

## Returns:
    None
    - As a constructor, __init__ does not return a value. After successful return, the instance will have attributes .e, .sql, and .params set to the passed values.

## Raises:
    TypeError:
        - Raised by Python automatically if __init__ is called with the wrong number of positional arguments (e.g., missing one of e, sql, params).
    (No other exceptions are raised by the body of this __init__ implementation; it performs only attribute assignment.)

## State Changes:
- Attributes READ:
    - None (the method does not read any pre-existing instance attributes)
- Attributes WRITTEN:
    - self.e: set to the provided e value
    - self.sql: set to the provided sql value
    - self.params: set to the provided params value

## Constraints:
- Preconditions:
    - Caller must supply three positional arguments (e, sql, params). There are no additional type checks or validations performed by this method.
    - If callers expect string formatting or inspection of .sql/.params later, they should ensure sql is a str and params is of an expected container type; the constructor does not enforce these types.
- Postconditions:
    - After __init__ returns, self.e, self.sql, and self.params exist on the instance and hold the exact objects passed in.
    - The base Exception.__init__ is NOT called here; therefore Exception.args is not populated and str(instance) will not include a message derived from these fields unless the class elsewhere overrides __str__ or code calls Exception.__init__.

## Side Effects:
    - No I/O, network, or external service effects.
    - No mutation of objects outside self (the method stores references to the provided arguments but does not modify them).
    - Because Exception.__init__ is not invoked, there is no change to standard Exception initialization behavior (e.g., args tuple remains empty) unless handled elsewhere in the class.

## `datasette.database.MultipleValues` · *class*

## Summary:
A minimal, named exception type used to signal that multiple values were encountered where a single value was expected.

## Description:
This class defines a distinct exception type (MultipleValues) by subclassing the built-in Exception. The source contains no additional attributes or methods; it exists solely to provide a specific, catchable exception identity.

Scenarios / callers:
- The module source does not define any callers or factories that raise MultipleValues. Call sites are not specified in this file.
- Typical intended usage (not enforced in this file): raise MultipleValues() when an operation that expects a single value finds more than one (for example, a lookup or constraint check). Callers elsewhere in the codebase may raise or catch this specific exception type to distinguish this failure mode from other errors.

Motivation:
- Using a dedicated exception class allows higher-level code to catch and handle the "multiple values" condition explicitly, without ambiguously matching other Exception types.

## State:
- This class has no instance attributes declared in this module.
- Type: subclass of built-in Exception.
- Valid values: any instance of MultipleValues is an Exception object; no additional payload or fields are defined.
- Invariants:
  - Instances behave like standard Exception instances (stringification, traceback attachment, etc.).
  - No guaranteed attributes beyond those provided by Exception (args, __traceback__, etc.).

## Lifecycle:
- Creation:
  - Instantiate with the same call signature as Exception (e.g., MultipleValues() or MultipleValues("detail message")).
  - There are no required constructor parameters.
- Usage:
  - Typical sequence: raise MultipleValues([optional message]) in the producer; catch MultipleValues in consumer code using "except MultipleValues:" to handle the specific condition.
  - There is no required method invocation order; instances are immutable from this module's perspective.
- Destruction:
  - No resources to clean up; normal Python garbage collection applies. The class does not implement context manager or close semantics.

## Method Map:
flowchart LR
    A[Producer code detects multiple values] --> B[raise MultipleValues]
    B --> C[Exception propagates]
    C --> D[Consumer code: except MultipleValues -> handle]
    C --> E[Unhandled -> normal traceback/propagation]

## Raises:
- The class definition itself raises no exceptions.
- Instantiating MultipleValues does not raise errors beyond those that standard Exception instantiation might raise (e.g., errors from unusual custom __str__ implementations passed in args), but none are defined here.

## Example:
- Raising the exception where multiple results are discovered:
    try:
        if len(results) > 1:
            raise MultipleValues("expected a single row, found multiple")
    except MultipleValues as e:
        # handle the "multiple values" condition specifically
        log("MultipleValues encountered:", e)

Note: The example shows idiomatic usage; the module itself only defines the exception type and does not include the example's raising or handling code.

## `datasette.database.Results` · *class*

## Summary:
A lightweight, immutable container representing the rows returned from a database query together with metadata; provides small convenience accessors (columns, first, single_value) and implements iteration/length.

## Description:
Results is a simple value-object created to hold the outcome of a database query execution:
- rows: a sequence (typically a list or tuple) of result rows, where each row is itself a sequence of column values (e.g., tuples returned by a DB-API cursor).
- truncated: a boolean flag indicating whether the returned rows were truncated (true when the producer limited the number of rows returned and there may be more matching rows).
- description: the cursor-like column description structure (an iterable of sequences/tuples where the first item of each entry is the column name).

When to instantiate:
- Construct Results after fetching rows and reading the cursor description from a DB-API compatible cursor. Typical callers are code paths that execute SQL and package the raw database cursor output for higher-level consumers (for example, a Database.execute wrapper or a query runner in higher-level modules).

Motivation and responsibility:
- Separates raw DB-API outputs into a purpose-specific, immutable container that higher-level code can use without depending on the live cursor.
- Encapsulates common convenience operations (getting the first row, extracting a single scalar value, iterating rows, accessing column names).

## State:
Attributes set by __init__:
- rows (sequence[sequence]): Required. The sequence of rows returned by the query. Each row is expected to be a sequence (e.g., tuple) whose length corresponds to the number of columns described by description. No automatic validation is performed; callers are responsible for providing coherent rows and description.
- truncated (bool): Required. True when the rows were intentionally truncated/limited by the producer (indicating there may be more rows that were not returned); False otherwise.
- description (sequence[sequence]): Required. An iterable of column-descriptor sequences/tuples where the 0th element of each descriptor is the column name. The property columns reads the first element of each descriptor to produce a list of column names.

Invariants and expectations (caller-enforced):
- rows is a finite sequence (len(rows) >= 0).
- truncated is a boolean value.
- Each row length is expected to match len(columns) (i.e., number of descriptors in description), although this class does not enforce or validate that invariant.
- description contains at least the 0th element for each descriptor entry (so accessing d[0] is valid).

## Lifecycle:
Creation:
- Instantiate with Results(rows, truncated, description)
  - rows: sequence of row sequences (no default)
  - truncated: boolean (no default)
  - description: sequence of descriptor sequences (no default)
- There are no provided factory methods in this class; producers should construct Results directly after executing a query.

Usage:
- Typical methods and order:
  1. Construct Results.
  2. Use results.columns to obtain a list of column names (derived from description).
  3. Iterate over rows with "for row in results" or access results[...]-style operations through the underlying rows object (this class exposes iteration and length only).
  4. Use results.first() to get the first row or None when empty.
  5. Use results.single_value() to extract a single scalar when the result set contains exactly one row with exactly one column; this raises MultipleValues otherwise.
- There is no required call sequence; methods are independent and safe to call in any order.

Destruction / cleanup:
- Results holds only plain Python objects and has no external resources. No explicit cleanup is required.

## Method Map:
flowchart LR
    A[Create Results(rows, truncated, description)] --> B[.columns property -> list of names]
    A --> C[.first() -> first row or None]
    A --> D[.single_value() -> scalar or raise MultipleValues]
    A --> E[__iter__() -> iterator over rows]
    A --> F[__len__() -> number of rows]

## Methods and behaviors (summary):
- columns (property): Returns a list constructed as [d[0] for d in self.description]. Each element is the 0th item of the corresponding descriptor in description (commonly the column name).
- first(): Returns the first row (self.rows[0]) when rows is non-empty; otherwise returns None.
- single_value(): If and only if there is exactly one row and that row has exactly one column, returns that single value. Otherwise raises MultipleValues (a module-specific exception type).
- __iter__(): Returns an iterator over self.rows (i.e., iter(self.rows)).
- __len__(): Returns len(self.rows).

## Raises:
- __init__: The constructor does not explicitly raise exceptions. It will accept whatever values are passed; downstream method calls may fail if inputs are malformed.
- single_value: Raises MultipleValues when either:
    - self.rows is empty, or
    - len(self.rows) != 1, or
    - len(self.rows[0]) != 1.
  The raised MultipleValues is the module-defined exception type used to indicate that the result set does not contain exactly one scalar value.

## Example:
- Create a Results object from fetched rows and a cursor description, then use accessors:
    rows = [(1, "Alice"), (2, "Bob")]
    description = [("id",), ("name",)]
    results = Results(rows, truncated=False, description=description)

    # get column names
    cols = results.columns  # ["id", "name"]

    # iterate rows
    for r in results:
        handle_row(r)

    # get first row
    first = results.first()  # (1, "Alice")

    # single_value usage (only valid when exactly one row and one column)
    single_rows = [(42,)]
    single_desc = [("answer",)]
    single_results = Results(single_rows, truncated=False, description=single_desc)
    value = single_results.single_value()  # 42

    # calling single_value() on results with >1 rows or >1 columns raises MultipleValues

### `datasette.database.Results.__init__` · *method*

## Summary:
Initializes a Results container by storing the fetched rows, a truncated flag, and the cursor description onto the instance so the object can be used as an immutable-style value object by higher-level code.

## Description:
This constructor is called immediately after a SQL query has been executed and raw outputs have been collected from a DB-API cursor. Known callers include code paths that execute SQL and package cursor output for consumers (for example, the Database.execute wrapper or higher-level query runners that fetch rows and cursor.description). The constructor's responsibility is minimal: capture the three pieces of data that define a query result and expose them via instance attributes and convenience methods on Results.

This logic is implemented in its own method because:
- It is the standard object-construction step (separates object assembly from later usage).
- Packaging the three related pieces of data in a single place makes the Results object a stable value object that other code can rely on without retaining the live cursor.
- Keeping initialization trivial makes the class lightweight and predictable; callers handle data validation and any transformation before constructing Results.

## Args:
    rows (sequence[sequence]):
        The sequence of rows returned by the query. Each element is expected to be a sequence (e.g., tuple) of column values. No coercion or validation is performed here; malformed rows will only surface when consumers access them.
    truncated (bool):
        Boolean flag indicating whether the returned rows were truncated (True when the producer limited the returned rows and there may be more matching rows). The constructor does not coerce truthy/falsy values.
    description (sequence[sequence]):
        Iterable of column-descriptor sequences/tuples where the 0th element of each descriptor is the column name (matching DB-API cursor.description semantics). The constructor stores this value as-is.

## Returns:
    None
    The constructor does not return a value; it initializes the instance in-place.

## Raises:
    None
    The __init__ method does not raise exceptions itself. Errors may occur later when other methods access malformed attributes (for example, if description entries do not contain a 0th element, attributes that read d[0] will raise IndexError).

## State Changes:
Attributes READ:
    (none) — the constructor does not read any pre-existing self.<attr> fields.

Attributes WRITTEN:
    self.rows: set to the provided rows argument.
    self.truncated: set to the provided truncated argument.
    self.description: set to the provided description argument.

## Constraints:
Preconditions:
    - Callers should pass a finite sequence for rows (len(rows) >= 0).
    - truncated should be a boolean value (True or False).
    - description should be an iterable of descriptor sequences where each descriptor contains at least one element (so descriptor[0] is valid).
    - If consumers expect row tuples to align with description, callers must ensure each row length matches len(description). This class does not enforce that invariant.

Postconditions:
    - After __init__, the instance will have self.rows, self.truncated, and self.description set to the provided values.
    - Consumers can immediately call Results.columns, iterate over the Results instance, call first(), or call single_value() (but those methods may raise if the provided inputs are malformed).

## Side Effects:
    - None. The constructor performs no I/O, no external service calls, and does not mutate objects other than assigning the three attributes on self. It does not copy or deep-clone the provided structures; it stores references to the passed-in objects.

### `datasette.database.Results.columns` · *method*

## Summary:
Return the ordered list of column names for these query results by extracting the first item from each entry in the stored cursor description.

## Description:
This read-only property converts the Results.description attribute (the DB cursor-style description sequence) into a simple list of column name values. It is intended for callers that need the column headings alongside row data (for example: serializers, templates, API responses, or any code that formats or inspects query results).

Known callers / usage context:
- Any code that receives a Results instance and needs a list of column names (e.g., JSON/HTML renderers or result inspection utilities).
- It is used at the lifecycle stage after a database query has been executed and a Results object has been constructed (Results.__init__ receives description at construction time).
- Kept as a separate property because extracting column names is a common, simple operation that callers expect; making it a property centralizes the logic and keeps call sites concise (results.columns) rather than repeating list-comprehension code across the codebase.

## Args:
    None

## Returns:
    list[str]: A new list containing the first element (index 0) of each entry in self.description, in the same order as self.description.
    - If self.description is an empty sequence, an empty list is returned.
    - If any description entry has a non-string or None at index 0, that raw value is included in the returned list (no coercion or filtering is performed).

## Raises:
    This property does not explicitly raise exceptions. However, callers may see the following exceptions if the description does not meet minimal indexing expectations:
    - IndexError: if an entry in self.description is not indexable or has length 0.
    - TypeError: if self.description is None or not iterable.
    (These exceptions are incidental to accessing d[0] and are not raised by explicit checks in this property.)

## State Changes:
    Attributes READ:
        - self.description
    Attributes WRITTEN:
        - None (this property does not modify any attributes)

## Constraints:
    Preconditions:
        - self.description must be an iterable of indexable objects (e.g., tuples or lists) where each entry supports indexing at 0.
        - Typical callers expect index 0 of each description entry to be the column name (commonly a string).
    Postconditions:
        - The returned value is a list whose length equals len(self.description).
        - The object's state (self.description, self.rows, self.truncated) is unchanged.

## Side Effects:
    - None: the property performs no I/O, mutation of external state, or network/database operations. It only constructs and returns a new list derived from an in-memory attribute.

### `datasette.database.Results.first` · *method*

## Summary:
Return the first element from the Results.rows collection, or None if that collection is empty. The Results instance is not modified.

## Description:
Known callers and context:
    - No direct callers were found in the provided snapshot of the codebase.
Why this logic is a separate method:
    - Provides a concise, reusable accessor for the "first-or-none" pattern so callers do not need to repeat the emptiness check and indexing expression.

## Args:
    None

## Returns:
    element | None
        - The element at index 0 of self.rows when self.rows is non-empty (truthy).
        - None when self.rows is empty (falsy).

## Raises:
    - The method itself does not explicitly raise exceptions. However, any exceptions raised by evaluating self.rows or by attempting to index self.rows[0] (for example, if self.rows is truthy but does not support indexing) will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.rows
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The Results instance must have an attribute rows.
        - For safe operation, self.rows should be a collection that supports truth-value testing and indexing at position 0 when non-empty.
    Postconditions:
        - The Results instance remains unchanged.
        - The return value is either the first element of self.rows or None.

## Side Effects:
    - None. No I/O, no external calls, and no mutation of objects outside self.

## Edge cases and notes:
    - If self.rows is an empty sequence (e.g., [] or ()), the method returns None.
    - If self.rows is truthy but not indexable, attempting to access self.rows[0] will raise an exception which will be propagated to the caller.
    - This method accesses only the rows attribute and performs no further computation.

### `datasette.database.Results.single_value` · *method*

## Summary:
Return the single scalar value from a query result when and only when the result set contains exactly one row with exactly one column; otherwise signal the unexpected shape by raising MultipleValues.

## Description:
Known callers and context:
- This method is defined on the Results container type and has no callers defined in this file. It is intended to be used by higher-level code that executes a SQL query and expects a single cell (one row, one column) as the result (for example, a "scalar" query). Typical usage is immediately after obtaining a Results instance representing the rows returned from a database query.
- Lifecycle stage: invoked during result inspection/processing after a query has completed and been wrapped in a Results object.

Why this is a separate method:
- Encapsulates the precise check for the "exactly one row and one column" shape and the specific error signaling (MultipleValues). Keeping this logic in one small method avoids repeated shape-checking at call sites and centralizes the exact semantics for what constitutes a single value result.

## Args:
- None. The method operates on the instance state (self.rows).

## Returns:
- Any: the single value contained in the sole row and sole column (i.e., self.rows[0][0]).
- Possible values: any Python object returned from the database driver for that cell (int, float, str, bytes, None, etc.).
- Edge-case return values:
    - If the single cell holds None, the method returns None (this is a valid returned value and is distinct from raising MultipleValues).

## Raises:
- MultipleValues: raised whenever the Results instance does not contain exactly one row with exactly one column. Concretely this happens when any of the following is true:
    - self.rows is falsy (e.g., empty list/sequence) — zero rows.
    - len(self.rows) != 1 — more than one row or zero rows.
    - len(self.rows[0]) != 1 — the single row does not contain exactly one column (zero or multiple columns).
- The exception is raised with no additional payload by this method (call sites may choose to include a message when raising or catching).

## State Changes:
Attributes READ:
- self.rows: inspected for truthiness and indexed (self.rows[0] and self.rows[0][0]).
Attributes WRITTEN:
- None. This method does not modify any attributes of self.

## Constraints:
Preconditions:
- The Results instance's self.rows must be a sequence (e.g., list or tuple) of row sequences where each row is itself indexable (supports len(...) and indexing).
- Callers should not rely on this method to coerce or transform data types; it only returns the stored cell as-is.

Postconditions:
- If the method returns normally, no attributes of self have been mutated and the returned value is the exact object stored at self.rows[0][0].
- If the method raises MultipleValues, no state has been changed by this method.

## Side Effects:
- None. The method performs only in-memory inspection and indexing; it performs no I/O, logging, or calls to external services, and mutates no external objects.

### `datasette.database.Results.__iter__` · *method*

## Summary:
Returns a new Python iterator over the Results object's stored rows, enabling use of the object in iteration contexts (for ... in results) without mutating the stored rows.

## Description:
This method implements the iterator protocol for the Results container by delegating to the underlying self.rows object. Typical callers are any consumer that iterates over query results, e.g. "for row in results:" or code that explicitly calls iter(results). It is invoked at the point in the query-processing lifecycle where rows have already been materialized and code needs to traverse them for rendering, serialization, or further processing.

This logic is isolated as a method to:
- Provide the standard Python iteration protocol for the Results type.
- Keep iteration semantics consistent and explicit (delegation to the underlying rows object).
- Allow callers to obtain an iterator without exposing or copying internal storage.

## Args:
    None

## Returns:
    iterator
    - An iterator object obtained by calling iter(self.rows).
    - The iterator yields the same element objects that are stored in self.rows, in the same order.
    - If self.rows is a sequence (e.g., list or tuple), a fresh list iterator is returned on each call.
    - If self.rows is an iterator or generator, iter(self.rows) will return that iterator/generator object itself (i.e., subsequent calls to __iter__ may return the same underlying iterator, which can be exhausted).

## Raises:
    TypeError: Raised when self.rows is not an iterable (for example, None or an object that does not implement __iter__). This is a direct consequence of calling iter(self.rows).

## State Changes:
    Attributes READ:
        - self.rows

    Attributes WRITTEN:
        - None (this method does not modify any attributes)

## Constraints:
    Preconditions:
        - self.rows should be set to an iterable before calling. Typical values are list, tuple, iterator, or generator.
    Postconditions:
        - The Results object remains unchanged.
        - The caller receives an iterator over the current contents of self.rows. If self.rows is a mutable sequence and is modified after obtaining the iterator, iteration reflects those mutations according to Python's iterator semantics.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self, except that consuming an iterator returned when self.rows itself is an iterator/generator will advance/consume that underlying iterator (a side-effect visible to other holders of the same iterator object).

### `datasette.database.Results.__len__` · *method*

## Summary:
Returns the number of rows contained in this Results object by delegating to the underlying rows container's length.

## Description:
This method implements the Python sequence protocol for Results so callers can use len(results) to obtain how many rows were produced by a query. It is a lightweight accessor that delegates directly to the stored rows container.

Known callers:
    - No direct call-sites were found in the provided code snapshot. The method is invoked whenever client code or library code calls len(results) on a Results instance (for example, to decide whether any rows were returned or to report a result count).

Why this is a separate method:
    - Providing __len__ allows Results to behave like a sequence/container (supporting the built-in len() call and idiomatic container checks such as if results:) without exposing or depending on the concrete type of rows. Keeping this logic here centralizes the length behavior rather than inlining len(self.rows) throughout the codebase.

## Args:
    - None

## Returns:
    int: The integer length of self.rows (0 or greater) as returned by the underlying container's __len__ implementation.

    Edge-case return values:
    - If self.rows is an empty sequence, returns 0.
    - If self.rows is a container with a defined length, returns that length.

## Raises:
    TypeError: If self.rows does not support len() (for example, if it is None or an iterator object without __len__), the call will raise whatever exception len(self.rows) would raise (typically TypeError).
    Any exception raised originates from the underlying container's __len__ implementation; this method performs no additional error handling.

## State Changes:
    Attributes READ:
        - self.rows

    Attributes WRITTEN:
        - None (this method does not modify the object's state)

## Constraints:
    Preconditions:
        - self.rows must be set (the Results instance should have been initialized).
        - self.rows must be a container or object that implements __len__ (i.e., calling len(self.rows) is valid).

    Postconditions:
        - The Results instance remains unchanged.
        - The returned integer equals the result of calling len() on the underlying rows container at the time of the call.

## Side Effects:
    - None. This method performs no I/O, external calls, nor mutations of other objects.

