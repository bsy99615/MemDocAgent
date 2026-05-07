# `sqlite.py`

## `datasette.utils.sqlite.sqlite_version` · *function*

## Summary:
Returns and caches the parsed SQLite library version as a tuple of integers so callers can perform simple lexical/version comparisons without repeating the query/parsing logic.

## Description:
This function provides a cached accessor for the SQLite version tuple produced by the helper that actually queries SQLite. On first call it obtains the version by delegating to the internal helper that queries an in-memory SQLite database and parses sqlite_version() into a tuple of ints; on subsequent calls it returns the cached tuple directly.

Known callers within the provided context:
    - No direct callers were visible in the provided snippet. Typical callers in applications include:
        - Startup checks that gate features by SQLite version.
        - Code paths that log or assert SQLite capabilities in tests.
        - Any place that needs to compare the running SQLite library version (feature enablement, compatibility checks).

Why this logic is a separate function:
    - Encapsulates caching of a relatively expensive operation (open in-memory database + SQL query + parsing).
    - Centralizes where the version tuple is stored so callers do not need to duplicate query/parsing logic and can rely on identity/stability of the returned value for the process lifetime.
    - Keeps error propagation behavior consistent across callers.

## Args:
    None

## Returns:
    tuple[int, ...]
        - A non-empty tuple of integers representing the numeric components of sqlite_version(), e.g. (3, 34, 1).
        - The returned tuple is cached in a module-level global (_cached_sqlite_version) and the same tuple object is returned for subsequent calls (until process exit or the module-level variable is mutated elsewhere).

## Raises:
    - Any exception raised by the underlying helper _sqlite_version:
        - sqlite3.Error: if opening an in-memory connection or executing the SELECT fails.
        - TypeError: if the query returns None or a non-indexable fetchone result and code tries to index into it.
        - IndexError: if the fetchone result is an empty sequence and index access fails.
        - ValueError: if any dot-separated segment cannot be converted to int.
    - NameError:
        - If the module-level variable _cached_sqlite_version is not defined in the module namespace before calling this function, evaluating the cache variable will raise NameError. (Precondition: the module should initialize _cached_sqlite_version, typically to None.)

Notes:
    - sqlite_version does not catch or translate these exceptions; they propagate to the caller unchanged.

## Constraints:
Preconditions:
    - The module must define the global variable _cached_sqlite_version (commonly initialized to None).
    - The environment must allow creating an in-memory SQLite connection (sqlite3 available and usable).
Postconditions:
    - On success, the module-level _cached_sqlite_version will hold the version tuple returned by _sqlite_version and the function returns that tuple.
    - Subsequent calls return the cached tuple without re-querying SQLite.

## Side Effects:
    - Writes the retrieved version tuple into the module-level global _cached_sqlite_version.
    - No filesystem or network I/O is performed by this function itself; the heavy work is performed by _sqlite_version, which opens an in-memory sqlite3.Connection. sqlite_version itself does not open or close connections.
    - No explicit resource cleanup is performed here beyond assigning the cached value.
    - Not thread-safe: concurrent callers racing on the first invocation may call _sqlite_version multiple times; the last assignment wins but no additional synchronization is performed.

## Control Flow:
flowchart TD
    A[Start] --> B{Is _cached_sqlite_version defined?\n(if not, NameError at lookup)}
    B --> C{Is _cached_sqlite_version is None?}
    C -->|Yes| D[Call _sqlite_version()]
    D -->|_sqlite_version raises| E[Exception propagated to caller]
    D -->|returns tuple| F[Assign tuple to _cached_sqlite_version]
    F --> G[Return _cached_sqlite_version]
    C -->|No (cached present)| G
    E --> H[Caller receives exception]

## Examples:
Happy-path usage (illustrative):
    # First call: will call _sqlite_version(), cache, and return tuple
    v1 = sqlite_version()   # e.g. (3, 34, 1)

    # Subsequent call: returns cached tuple immediately
    v2 = sqlite_version()
    assert v1 is v2        # same cached tuple object in module

Feature gating example:
    try:
        version = sqlite_version()
    except sqlite3.Error:
        # SQLite unavailable or query failed — degrade or abort startup
        raise
    else:
        if version >= (3, 35, 0):
            enable_feature_x()
        else:
            disable_feature_x()

Robust error handling:
    try:
        v = sqlite_version()
    except (sqlite3.Error, TypeError, IndexError, ValueError, NameError) as e:
        # handle or surface a clearer diagnostic
        log.error("Unable to determine SQLite version: %s", e)
        # fallback or re-raise as appropriate

Implementation notes for callers:
    - Do not rely on sqlite_version() returning a freshly re-queried value; it returns a cached tuple for the process lifetime unless the module-level cache is intentionally mutated.
    - If you require updated version detection (e.g., library replaced at runtime), the module-level cache must be cleared/reset by the caller or an exposed helper.

## `datasette.utils.sqlite._sqlite_version` · *function*

## Summary:
Returns the SQLite library version as a tuple of integer components parsed from sqlite_version(), e.g. (3, 34, 1).

## Description:
This helper opens a new in-memory SQLite connection, runs the SQL function sqlite_version(), parses the resulting dot-separated version string into integer components, and returns those components as a tuple.

Known callers in the provided context:
    - No direct callers were visible in the provided snippet. Common uses in applications include startup checks, feature gating (enable/disable features depending on SQLite capabilities), logging, or tests that assert specific SQLite behavior.

Why this logic is extracted:
    - Centralizes version detection and parsing so callers can compare version tuples lexicographically without duplicating SQL/query and parsing code.
    - Isolates error/edge-case handling for SQLite version retrieval (formatting, unexpected results) in one place for easier maintenance and testing.

## Args:
    None

## Returns:
    tuple[int, ...]
        A non-empty tuple of integers corresponding to each numeric segment of the version string returned by sqlite_version().
        Examples:
            - "3.34.1" -> (3, 34, 1)
            - "3.35.0.1" -> (3, 35, 0, 1)
        Edge cases:
            - If sqlite_version() returns an unexpected format (non-numeric segments, missing value), the function will raise a conversion or indexing exception (see Raises).

## Raises:
    sqlite3.Error
        If opening the in-memory connection or executing the SELECT fails (errors raised by sqlite3.connect or Connection.execute).

    TypeError
        If fetchone() returns None (none is returned when the query yields no rows) or another non-indexable object — attempting fetchone()[0] will raise TypeError ('NoneType' object is not subscriptable or similar).

    IndexError
        If fetchone() returns an empty sequence (e.g., ()) and accessing index 0 is out of range.

    ValueError
        If any dot-separated segment cannot be converted to int (for example "3.32.1-beta" or other non-numeric segments).

Notes:
    - The function does not catch these exceptions; callers should handle them where appropriate.

## Constraints:
Preconditions:
    - The environment must provide the sqlite3 module and allow opening an in-memory SQLite connection.
    - The sqlite_version() function must be available in the connected SQLite library.

Postconditions:
    - On success, returns a tuple of ints representing each numeric part of the SQLite version string.
    - The created in-memory connection is not retained; resource cleanup depends on the connection object finalizer/garbage collection (see Side Effects).

## Side Effects:
    - Opens a new sqlite3.Connection to ":memory:" (an ephemeral in-memory database).
    - The connection is not explicitly closed in the implementation; this may leave closing to garbage collection. In long-running processes or tight loops this could increase resource usage.
    - No file system or network I/O is performed beyond the in-memory DB allocation.

## Control Flow:
flowchart TD
    A[Start] --> B[sqlite3.connect(":memory:")]
    B -->|connection fails| C[raise sqlite3.Error]
    B -->|connection ok| D[execute "select sqlite_version()"]
    D -->|execute fails| C
    D --> E[fetchone()]
    E -->|None or non-indexable| F[raise TypeError]
    E -->|sequence returned| G[try access element 0]
    G -->|index out of range| H[raise IndexError]
    G -->|got version_str| I[split by "." into segments]
    I --> J[convert each segment to int]
    J -->|conversion fails| K[raise ValueError]
    J -->|success| L[return tuple of ints]

## Examples:
Happy path:
    try:
        v = _sqlite_version()
    except sqlite3.Error:
        # fail-safe: SQLite not available or cannot open in-memory DB
        v = (0, 0, 0)
    else:
        if v >= (3, 35, 0):
            # enable feature requiring SQLite 3.35.0+
            pass

Robust usage with diagnostics:
    try:
        version = _sqlite_version()
    except sqlite3.Error as e:
        # could log or fallback
        raise RuntimeError("Unable to query SQLite version") from e
    except (TypeError, IndexError, ValueError) as e:
        # unexpected result format from sqlite_version()
        # handle or fail-fast depending on application needs
        raise RuntimeError("Unexpected sqlite_version() format") from e

## `datasette.utils.sqlite.supports_table_xinfo` · *function*

## Summary:
Returns True when the running SQLite library is new enough to support the TABLE xinfo pragma (SQLite >= 3.26.0); otherwise returns False.

## Description:
This is a small, focused feature-check helper used to gate code paths that rely on the TABLE xinfo capability introduced in SQLite 3.26.0. It reads the numeric SQLite library version via sqlite_version() and performs a lexical tuple comparison against (3, 26, 0).

Known callers within the codebase:
    - No direct callers were discovered in the provided snippets. Typical callers in an application like Datasette include:
        - Startup or initialization logic that enables or disables features depending on SQLite capabilities.
        - Code paths that choose different PRAGMA/SQL forms when introspecting table metadata.
        - Test helpers that skip or adapt tests when TABLE xinfo is unavailable.

Why this logic is extracted:
    - Centralizes a single-source-of-truth check for the TABLE xinfo capability so callers do not repeat the numeric comparison.
    - Keeps caller code simple and readable (callers ask a boolean question rather than manipulate version tuples).
    - Captures the exact minimum required version in one place, making future updates straightforward.

## Args:
    None

## Returns:
    bool
        - True if sqlite_version() >= (3, 26, 0).
        - False if sqlite_version() exists and compares lower than (3, 26, 0).

## Raises:
    Any exception raised by sqlite_version() will propagate unchanged. Notable possibilities (derived from sqlite_version's behavior):
        - sqlite3.Error: if an in-memory SQLite connection or query fails.
        - TypeError / IndexError / ValueError: if the version parsing performed by sqlite_version() fails.
        - NameError: if the module-level cache variable used by sqlite_version() is not defined.
    Notes:
        - supports_table_xinfo does not catch or translate exceptions; callers should handle these if they need to degrade gracefully.

## Constraints:
Preconditions:
    - The sqlite_version() helper must be available and callable in the same module.
    - The environment must permit determination of SQLite version (i.e., sqlite_version() can open an in-memory connection if required).
Postconditions:
    - On normal return, a boolean value is returned; no additional guarantees about external state are made by this function itself.
    - If sqlite_version() caches the version tuple (as it typically does), that cache may be updated as a side effect of calling this function.

## Side Effects:
    - Direct: None performed by supports_table_xinfo itself beyond calling sqlite_version().
    - Indirect: sqlite_version() may perform I/O-like operations (open an in-memory SQLite connection) and may cache the parsed version in a module-level variable; those side effects therefore can occur when calling this function.
    - No filesystem, network I/O, or global mutation is performed by supports_table_xinfo beyond what sqlite_version() does.
    - Thread-safety: No synchronization is performed here; concurrent first-time calls may race to initialize sqlite_version()'s cache.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSqliteVersion{Call sqlite_version()}
    CallSqliteVersion --> |raises exception| PropagateErr[Propagate exception to caller]
    CallSqliteVersion --> |returns tuple| Compare[(returned_tuple) >= (3,26,0)?]
    Compare --> |True| ReturnTrue([return True])
    Compare --> |False| ReturnFalse([return False])

## Examples:
Happy-path usage:
    try:
        if supports_table_xinfo():
            # safe to run queries that rely on TABLE xinfo behavior
            perform_xinfo_dependent_work()
        else:
            # fall back to alternative metadata queries
            perform_fallback_work()
    except sqlite3.Error as e:
        # handle inability to determine SQLite version or other DB error
        log.error("Unable to determine SQLite capabilities: %s", e)
        handle_startup_failure(e)

Simple guard in initialization:
    try:
        use_xinfo = supports_table_xinfo()
    except Exception:
        use_xinfo = False  # conservative fallback if version cannot be determined

## `datasette.utils.sqlite.supports_generated_columns` · *function*

## Summary:
Return True if the running SQLite library supports "generated columns" (SQLite >= 3.31.0); otherwise return False.

## Description:
This small helper performs a feature-gate check by comparing the parsed SQLite library version against the minimum version that introduced generated (computed) columns.

Known callers within the provided context:
    - No direct callers were visible in the provided snippet. Typical callers include:
        - Startup or migration checks that enable/disable features depending on SQLite capabilities.
        - Code paths that create or migrate database schemas and must avoid using generated columns when the runtime SQLite is too old.
        - Test setup routines that skip tests requiring generated columns on older SQLite builds.

Why this logic is extracted into its own function:
    - Encapsulates the single responsibility of expressing the version-based capability check so call sites read clearly (supports_generated_columns()) instead of repeating the numeric comparison inline.
    - Centralizes the threshold value (3, 31, 0) in one place so it is easy to update if the policy changes.
    - Keeps callers agnostic to how the SQLite version is obtained or cached (delegates that to sqlite_version()).

## Args:
    None

## Returns:
    bool
        - True if sqlite_version() >= (3, 31, 0), meaning the running SQLite library is new enough to support generated columns.
        - False otherwise.
        - If sqlite_version() raises an exception (see Raises), that exception will propagate instead of returning a boolean.

## Raises:
    - Any exception raised by sqlite_version() will propagate unchanged. In particular (but not limited to):
        - sqlite3.Error: if querying the SQLite library version fails (e.g., opening an in-memory connection).
        - TypeError, IndexError, ValueError: if the version parsing inside sqlite_version() fails.
        - NameError: if the sqlite_version-related module-level cache/variable is missing or mis-initialized.
    Note: supports_generated_columns does not catch or translate exceptions; callers should handle them if they need robust startup behavior.

## Constraints:
Preconditions:
    - The module-level function sqlite_version() must be available and callable in the same module namespace.
    - sqlite_version() should return a tuple of integers (e.g., (3, 34, 1)) to allow reliable tuple comparison.

Postconditions:
    - On successful return (True or False), no global state is mutated by this function itself.
    - If this call causes sqlite_version() to run for the first time, sqlite_version() may cache the parsed tuple as a side effect (see sqlite_version documentation), and subsequent calls to supports_generated_columns() will use the cached value.

## Side Effects:
    - Indirect: may trigger sqlite_version() which caches the SQLite version tuple in a module-level variable. That caching is performed by sqlite_version(), not by this function.
    - No I/O, filesystem, network, or direct database writes are performed by this function itself.
    - No further external state mutations are made by this function.

## Control Flow:
flowchart TD
    Start --> Call_sqlite_version[Call sqlite_version()]
    Call_sqlite_version -->|raises exception| Propagate[Propagate exception to caller]
    Call_sqlite_version -->|returns tuple v| Compare{Is v >= (3,31,0)?}
    Compare -->|Yes| ReturnTrue[Return True]
    Compare -->|No| ReturnFalse[Return False]

## Examples:
Feature gating (happy path):
    try:
        if supports_generated_columns():
            # safe to create or migrate tables with GENERATED columns
            use_generated_columns = True
        else:
            # fall back to computed values or trigger an alternate schema
            use_generated_columns = False
    except sqlite3.Error as e:
        # unable to determine SQLite version; handle startup failure or degrade gracefully
        log.error("Could not determine SQLite capabilities: %s", e)
        raise

Example showing exception propagation (illustrative):
    # If sqlite_version() fails (e.g., sqlite3.Error), this call will raise and not return True/False.
    supports_generated_columns()  # may raise sqlite3.Error, TypeError, ValueError, NameError

